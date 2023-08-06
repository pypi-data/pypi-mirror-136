"""IR node for the groupby, pivot and cross_tabulation"""
import ctypes
import operator
import types as pytypes
from collections import defaultdict, namedtuple
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, compiler, ir, ir_utils, types
from numba.core.analysis import compute_use_defs
from numba.core.ir_utils import build_definitions, compile_to_numba_ir, find_callname, find_const, find_topo_order, get_definition, get_ir_of_code, get_name_var_table, guard, is_getitem, mk_unique_var, next_label, remove_dels, replace_arg_nodes, replace_var_names, replace_vars_inner, visit_vars_inner
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, lower_builtin, overload
from numba.parfors.parfor import Parfor, unwrap_parfor_blocks, wrap_parfor_blocks
import bodo
from bodo.hiframes.datetime_date_ext import DatetimeDateArrayType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, compute_node_partition_by_hash, delete_info_decref_array, delete_table, delete_table_decref_arrays, groupby_and_aggregate, info_from_table, info_to_array, pivot_groupby_and_aggregate
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, pre_alloc_array_item_array
from bodo.libs.binary_arr_ext import BinaryArrayType, pre_alloc_binary_array
from bodo.libs.bool_arr_ext import BooleanArrayType
from bodo.libs.decimal_arr_ext import DecimalArrayType, alloc_decimal_array
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.utils.transform import get_call_expr_arg
from bodo.utils.typing import BodoError, get_literal_value, get_overload_const_func, get_overload_const_str, get_overload_constant_dict, is_overload_constant_dict, is_overload_constant_str, list_cumulative
from bodo.utils.utils import debug_prints, incref, is_assign, is_call_assign, is_expr, is_null_pointer, is_var_assign, sanitize_varname, unliteral_all
gb_agg_cfunc = {}
gb_agg_cfunc_addr = {}


@intrinsic
def add_agg_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        sig = func.signature
        if sig == types.none(types.voidptr):
            modp__xfzz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            fdn__icubg = cgutils.get_or_insert_function(builder.module,
                modp__xfzz, sym._literal_value)
            builder.call(fdn__icubg, [context.get_constant_null(sig.args[0])])
        elif sig == types.none(types.int64, types.voidptr, types.voidptr):
            modp__xfzz = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            fdn__icubg = cgutils.get_or_insert_function(builder.module,
                modp__xfzz, sym._literal_value)
            builder.call(fdn__icubg, [context.get_constant(types.int64, 0),
                context.get_constant_null(sig.args[1]), context.
                get_constant_null(sig.args[2])])
        else:
            modp__xfzz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            fdn__icubg = cgutils.get_or_insert_function(builder.module,
                modp__xfzz, sym._literal_value)
            builder.call(fdn__icubg, [context.get_constant_null(sig.args[0]
                ), context.get_constant_null(sig.args[1]), context.
                get_constant_null(sig.args[2])])
        context.add_linking_libs([gb_agg_cfunc[sym._literal_value]._library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_agg_udf_addr(name):
    with numba.objmode(addr='int64'):
        addr = gb_agg_cfunc_addr[name]
    return addr


class AggUDFStruct(object):

    def __init__(self, regular_udf_funcs=None, general_udf_funcs=None):
        assert regular_udf_funcs is not None or general_udf_funcs is not None
        self.regular_udfs = False
        self.general_udfs = False
        self.regular_udf_cfuncs = None
        self.general_udf_cfunc = None
        if regular_udf_funcs is not None:
            (self.var_typs, self.init_func, self.update_all_func, self.
                combine_all_func, self.eval_all_func) = regular_udf_funcs
            self.regular_udfs = True
        if general_udf_funcs is not None:
            self.general_udf_funcs = general_udf_funcs
            self.general_udfs = True

    def set_regular_cfuncs(self, update_cb, combine_cb, eval_cb):
        assert self.regular_udfs and self.regular_udf_cfuncs is None
        self.regular_udf_cfuncs = [update_cb, combine_cb, eval_cb]

    def set_general_cfunc(self, general_udf_cb):
        assert self.general_udfs and self.general_udf_cfunc is None
        self.general_udf_cfunc = general_udf_cb


AggFuncStruct = namedtuple('AggFuncStruct', ['func', 'ftype'])
supported_agg_funcs = ['no_op', 'head', 'transform', 'size', 'shift', 'sum',
    'count', 'nunique', 'median', 'cumsum', 'cumprod', 'cummin', 'cummax',
    'mean', 'min', 'max', 'prod', 'first', 'last', 'idxmin', 'idxmax',
    'var', 'std', 'udf', 'gen_udf']
supported_transform_funcs = ['no_op', 'sum', 'count', 'nunique', 'median',
    'mean', 'min', 'max', 'prod', 'first', 'last', 'var', 'std']


def get_agg_func(func_ir, func_name, rhs, series_type=None, typemap=None):
    if func_name == 'no_op':
        raise BodoError('Unknown aggregation function used in groupby.')
    if series_type is None:
        series_type = SeriesType(types.float64)
    if func_name in {'var', 'std'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 3
        func.ncols_post_shuffle = 4
        return func
    if func_name in {'first', 'last'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        return func
    if func_name in {'idxmin', 'idxmax'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 2
        func.ncols_post_shuffle = 2
        return func
    if func_name in supported_agg_funcs[:-8]:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        nnovo__tuul = True
        oit__mbggu = 1
        hvjmg__vgu = -1
        if isinstance(rhs, ir.Expr):
            for stp__pbb in rhs.kws:
                if func_name in list_cumulative:
                    if stp__pbb[0] == 'skipna':
                        nnovo__tuul = guard(find_const, func_ir, stp__pbb[1])
                        if not isinstance(nnovo__tuul, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if stp__pbb[0] == 'dropna':
                        nnovo__tuul = guard(find_const, func_ir, stp__pbb[1])
                        if not isinstance(nnovo__tuul, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            oit__mbggu = get_call_expr_arg('shift', rhs.args, dict(rhs.kws),
                0, 'periods', oit__mbggu)
            oit__mbggu = guard(find_const, func_ir, oit__mbggu)
        if func_name == 'head':
            hvjmg__vgu = get_call_expr_arg('head', rhs.args, dict(rhs.kws),
                0, 'n', 5)
            if not isinstance(hvjmg__vgu, int):
                hvjmg__vgu = guard(find_const, func_ir, hvjmg__vgu)
            if hvjmg__vgu < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = nnovo__tuul
        func.periods = oit__mbggu
        func.head_n = hvjmg__vgu
        if func_name == 'transform':
            kws = dict(rhs.kws)
            bunpk__bzug = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            doopr__sjjua = typemap[bunpk__bzug.name]
            gbgu__uduh = None
            if isinstance(doopr__sjjua, str):
                gbgu__uduh = doopr__sjjua
            elif is_overload_constant_str(doopr__sjjua):
                gbgu__uduh = get_overload_const_str(doopr__sjjua)
            elif bodo.utils.typing.is_builtin_function(doopr__sjjua):
                gbgu__uduh = bodo.utils.typing.get_builtin_function_name(
                    doopr__sjjua)
            if gbgu__uduh not in bodo.ir.aggregate.supported_transform_funcs[:
                ]:
                raise BodoError(f'unsupported transform function {gbgu__uduh}')
            func.transform_func = supported_agg_funcs.index(gbgu__uduh)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    bunpk__bzug = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if bunpk__bzug == '':
        doopr__sjjua = types.none
    else:
        doopr__sjjua = typemap[bunpk__bzug.name]
    if is_overload_constant_dict(doopr__sjjua):
        rrr__uemxe = get_overload_constant_dict(doopr__sjjua)
        kgveu__qwcvd = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in rrr__uemxe.values()]
        return kgveu__qwcvd
    if doopr__sjjua == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(doopr__sjjua, types.BaseTuple):
        kgveu__qwcvd = []
        ucdu__thwt = 0
        for t in doopr__sjjua.types:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                kgveu__qwcvd.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>':
                    func.fname = '<lambda_' + str(ucdu__thwt) + '>'
                    ucdu__thwt += 1
                kgveu__qwcvd.append(func)
        return [kgveu__qwcvd]
    if is_overload_constant_str(doopr__sjjua):
        func_name = get_overload_const_str(doopr__sjjua)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(doopr__sjjua):
        func_name = bodo.utils.typing.get_builtin_function_name(doopr__sjjua)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    assert typemap is not None, 'typemap is required for agg UDF handling'
    func = _get_const_agg_func(typemap[rhs.args[0].name], func_ir)
    func.ftype = 'udf'
    func.fname = _get_udf_name(func)
    return func


def get_agg_func_udf(func_ir, f_val, rhs, series_type, typemap):
    if isinstance(f_val, str):
        return get_agg_func(func_ir, f_val, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(f_val):
        func_name = bodo.utils.typing.get_builtin_function_name(f_val)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if isinstance(f_val, (tuple, list)):
        ucdu__thwt = 0
        cjax__upi = []
        for yxnp__rntmv in f_val:
            func = get_agg_func_udf(func_ir, yxnp__rntmv, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{ucdu__thwt}>'
                ucdu__thwt += 1
            cjax__upi.append(func)
        return cjax__upi
    else:
        assert is_expr(f_val, 'make_function') or isinstance(f_val, (numba.
            core.registry.CPUDispatcher, types.Dispatcher))
        assert typemap is not None, 'typemap is required for agg UDF handling'
        func = _get_const_agg_func(f_val, func_ir)
        func.ftype = 'udf'
        func.fname = _get_udf_name(func)
        return func


def _get_udf_name(func):
    code = func.code if hasattr(func, 'code') else func.__code__
    gbgu__uduh = code.co_name
    return gbgu__uduh


def _get_const_agg_func(func_typ, func_ir):
    agg_func = get_overload_const_func(func_typ, func_ir)
    if is_expr(agg_func, 'make_function'):

        def agg_func_wrapper(A):
            return A
        agg_func_wrapper.__code__ = agg_func.code
        agg_func = agg_func_wrapper
        return agg_func
    return agg_func


@infer_global(type)
class TypeDt64(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if len(args) == 1 and isinstance(args[0], (types.NPDatetime, types.
            NPTimedelta)):
            xhmvf__hch = types.DType(args[0])
            return signature(xhmvf__hch, *args)


@numba.njit(no_cpython_wrapper=True)
def _var_combine(ssqdm_a, mean_a, nobs_a, ssqdm_b, mean_b, nobs_b):
    ebt__qcv = nobs_a + nobs_b
    uuwo__gvdd = (nobs_a * mean_a + nobs_b * mean_b) / ebt__qcv
    turc__oywr = mean_b - mean_a
    uctq__bbv = (ssqdm_a + ssqdm_b + turc__oywr * turc__oywr * nobs_a *
        nobs_b / ebt__qcv)
    return uctq__bbv, uuwo__gvdd, ebt__qcv


def __special_combine(*args):
    return


@infer_global(__special_combine)
class SpecialCombineTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *unliteral_all(args))


@lower_builtin(__special_combine, types.VarArg(types.Any))
def lower_special_combine(context, builder, sig, args):
    return context.get_dummy_value()


class Aggregate(ir.Stmt):

    def __init__(self, df_out, df_in, key_names, gb_info_in, gb_info_out,
        out_key_vars, df_out_vars, df_in_vars, key_arrs, input_has_index,
        same_index, return_key, loc, func_name, dropna=True, pivot_arr=None,
        pivot_values=None, is_crosstab=False):
        self.df_out = df_out
        self.df_in = df_in
        self.key_names = key_names
        self.gb_info_in = gb_info_in
        self.gb_info_out = gb_info_out
        self.out_key_vars = out_key_vars
        self.df_out_vars = df_out_vars
        self.df_in_vars = df_in_vars
        self.key_arrs = key_arrs
        self.input_has_index = input_has_index
        self.same_index = same_index
        self.return_key = return_key
        self.loc = loc
        self.func_name = func_name
        self.dropna = dropna
        self.pivot_arr = pivot_arr
        self.pivot_values = pivot_values
        self.is_crosstab = is_crosstab

    def __repr__(self):
        jegd__rdx = ''
        for jqzg__sklz, v in self.df_out_vars.items():
            jegd__rdx += "'{}':{}, ".format(jqzg__sklz, v.name)
        irgt__cwd = '{}{{{}}}'.format(self.df_out, jegd__rdx)
        vgy__mle = ''
        for jqzg__sklz, v in self.df_in_vars.items():
            vgy__mle += "'{}':{}, ".format(jqzg__sklz, v.name)
        fiiu__vvqgc = '{}{{{}}}'.format(self.df_in, vgy__mle)
        cljc__ibl = 'pivot {}:{}'.format(self.pivot_arr.name, self.pivot_values
            ) if self.pivot_arr is not None else ''
        key_names = ','.join(self.key_names)
        nfu__yamz = ','.join([v.name for v in self.key_arrs])
        return 'aggregate: {} = {} [key: {}:{}] {}'.format(irgt__cwd,
            fiiu__vvqgc, key_names, nfu__yamz, cljc__ibl)

    def remove_out_col(self, out_col_name):
        self.df_out_vars.pop(out_col_name)
        egj__buy, jzjcx__dlyw = self.gb_info_out.pop(out_col_name)
        if egj__buy is None and not self.is_crosstab:
            return
        zxkh__tmrm = self.gb_info_in[egj__buy]
        if self.pivot_arr is not None:
            self.pivot_values.remove(out_col_name)
            for i, (func, jegd__rdx) in enumerate(zxkh__tmrm):
                try:
                    jegd__rdx.remove(out_col_name)
                    if len(jegd__rdx) == 0:
                        zxkh__tmrm.pop(i)
                        break
                except ValueError as pfi__jpjjn:
                    continue
        else:
            for i, (func, eken__rmdsx) in enumerate(zxkh__tmrm):
                if eken__rmdsx == out_col_name:
                    zxkh__tmrm.pop(i)
                    break
        if len(zxkh__tmrm) == 0:
            self.gb_info_in.pop(egj__buy)
            self.df_in_vars.pop(egj__buy)


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({v.name for v in aggregate_node.key_arrs})
    use_set.update({v.name for v in aggregate_node.df_in_vars.values()})
    if aggregate_node.pivot_arr is not None:
        use_set.add(aggregate_node.pivot_arr.name)
    def_set.update({v.name for v in aggregate_node.df_out_vars.values()})
    if aggregate_node.out_key_vars is not None:
        def_set.update({v.name for v in aggregate_node.out_key_vars})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(aggregate_node, lives_no_aliases, lives,
    arg_aliases, alias_map, func_ir, typemap):
    qok__gaol = [jnxaq__wvyly for jnxaq__wvyly, tdt__idrtj in
        aggregate_node.df_out_vars.items() if tdt__idrtj.name not in lives]
    for nmlqr__vzpb in qok__gaol:
        aggregate_node.remove_out_col(nmlqr__vzpb)
    out_key_vars = aggregate_node.out_key_vars
    if out_key_vars is not None and all(v.name not in lives for v in
        out_key_vars):
        aggregate_node.out_key_vars = None
    if len(aggregate_node.df_out_vars
        ) == 0 and aggregate_node.out_key_vars is None:
        return None
    return aggregate_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    abyx__owmzl = set(v.name for v in aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        abyx__owmzl.update({v.name for v in aggregate_node.out_key_vars})
    return set(), abyx__owmzl


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for i in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[i] = replace_vars_inner(aggregate_node.
            key_arrs[i], var_dict)
    for jnxaq__wvyly in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[jnxaq__wvyly] = replace_vars_inner(
            aggregate_node.df_in_vars[jnxaq__wvyly], var_dict)
    for jnxaq__wvyly in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[jnxaq__wvyly] = replace_vars_inner(
            aggregate_node.df_out_vars[jnxaq__wvyly], var_dict)
    if aggregate_node.out_key_vars is not None:
        for i in range(len(aggregate_node.out_key_vars)):
            aggregate_node.out_key_vars[i] = replace_vars_inner(aggregate_node
                .out_key_vars[i], var_dict)
    if aggregate_node.pivot_arr is not None:
        aggregate_node.pivot_arr = replace_vars_inner(aggregate_node.
            pivot_arr, var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    if debug_prints():
        print('visiting aggregate vars for:', aggregate_node)
        print('cbdata: ', sorted(cbdata.items()))
    for i in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[i] = visit_vars_inner(aggregate_node.
            key_arrs[i], callback, cbdata)
    for jnxaq__wvyly in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[jnxaq__wvyly] = visit_vars_inner(
            aggregate_node.df_in_vars[jnxaq__wvyly], callback, cbdata)
    for jnxaq__wvyly in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[jnxaq__wvyly] = visit_vars_inner(
            aggregate_node.df_out_vars[jnxaq__wvyly], callback, cbdata)
    if aggregate_node.out_key_vars is not None:
        for i in range(len(aggregate_node.out_key_vars)):
            aggregate_node.out_key_vars[i] = visit_vars_inner(aggregate_node
                .out_key_vars[i], callback, cbdata)
    if aggregate_node.pivot_arr is not None:
        aggregate_node.pivot_arr = visit_vars_inner(aggregate_node.
            pivot_arr, callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    assert len(aggregate_node.df_out_vars
        ) > 0 or aggregate_node.out_key_vars is not None or aggregate_node.is_crosstab, 'empty aggregate in array analysis'
    crkco__kqta = []
    for yyqa__ass in aggregate_node.key_arrs:
        cog__apog = equiv_set.get_shape(yyqa__ass)
        if cog__apog:
            crkco__kqta.append(cog__apog[0])
    if aggregate_node.pivot_arr is not None:
        cog__apog = equiv_set.get_shape(aggregate_node.pivot_arr)
        if cog__apog:
            crkco__kqta.append(cog__apog[0])
    for tdt__idrtj in aggregate_node.df_in_vars.values():
        cog__apog = equiv_set.get_shape(tdt__idrtj)
        if cog__apog:
            crkco__kqta.append(cog__apog[0])
    if len(crkco__kqta) > 1:
        equiv_set.insert_equiv(*crkco__kqta)
    gykp__eklum = []
    crkco__kqta = []
    ukp__zdiv = list(aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        ukp__zdiv.extend(aggregate_node.out_key_vars)
    for tdt__idrtj in ukp__zdiv:
        svbd__uci = typemap[tdt__idrtj.name]
        ujy__rhg = array_analysis._gen_shape_call(equiv_set, tdt__idrtj,
            svbd__uci.ndim, None, gykp__eklum)
        equiv_set.insert_equiv(tdt__idrtj, ujy__rhg)
        crkco__kqta.append(ujy__rhg[0])
        equiv_set.define(tdt__idrtj, set())
    if len(crkco__kqta) > 1:
        equiv_set.insert_equiv(*crkco__kqta)
    return [], gykp__eklum


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    aqwyd__tzp = Distribution.OneD
    for tdt__idrtj in aggregate_node.df_in_vars.values():
        aqwyd__tzp = Distribution(min(aqwyd__tzp.value, array_dists[
            tdt__idrtj.name].value))
    for yyqa__ass in aggregate_node.key_arrs:
        aqwyd__tzp = Distribution(min(aqwyd__tzp.value, array_dists[
            yyqa__ass.name].value))
    if aggregate_node.pivot_arr is not None:
        aqwyd__tzp = Distribution(min(aqwyd__tzp.value, array_dists[
            aggregate_node.pivot_arr.name].value))
        array_dists[aggregate_node.pivot_arr.name] = aqwyd__tzp
    for tdt__idrtj in aggregate_node.df_in_vars.values():
        array_dists[tdt__idrtj.name] = aqwyd__tzp
    for yyqa__ass in aggregate_node.key_arrs:
        array_dists[yyqa__ass.name] = aqwyd__tzp
    kwz__rsz = Distribution.OneD_Var
    for tdt__idrtj in aggregate_node.df_out_vars.values():
        if tdt__idrtj.name in array_dists:
            kwz__rsz = Distribution(min(kwz__rsz.value, array_dists[
                tdt__idrtj.name].value))
    if aggregate_node.out_key_vars is not None:
        for tdt__idrtj in aggregate_node.out_key_vars:
            if tdt__idrtj.name in array_dists:
                kwz__rsz = Distribution(min(kwz__rsz.value, array_dists[
                    tdt__idrtj.name].value))
    kwz__rsz = Distribution(min(kwz__rsz.value, aqwyd__tzp.value))
    for tdt__idrtj in aggregate_node.df_out_vars.values():
        array_dists[tdt__idrtj.name] = kwz__rsz
    if aggregate_node.out_key_vars is not None:
        for zle__uemiy in aggregate_node.out_key_vars:
            array_dists[zle__uemiy.name] = kwz__rsz
    if kwz__rsz != Distribution.OneD_Var:
        for yyqa__ass in aggregate_node.key_arrs:
            array_dists[yyqa__ass.name] = kwz__rsz
        if aggregate_node.pivot_arr is not None:
            array_dists[aggregate_node.pivot_arr.name] = kwz__rsz
        for tdt__idrtj in aggregate_node.df_in_vars.values():
            array_dists[tdt__idrtj.name] = kwz__rsz


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for tdt__idrtj in agg_node.df_out_vars.values():
        definitions[tdt__idrtj.name].append(agg_node)
    if agg_node.out_key_vars is not None:
        for zle__uemiy in agg_node.out_key_vars:
            definitions[zle__uemiy.name].append(agg_node)
    return definitions


ir_utils.build_defs_extensions[Aggregate] = build_agg_definitions


def __update_redvars():
    pass


@infer_global(__update_redvars)
class UpdateDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __combine_redvars():
    pass


@infer_global(__combine_redvars)
class CombineDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __eval_res():
    pass


@infer_global(__eval_res)
class EvalDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(args[0].dtype, *args)


def agg_distributed_run(agg_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for v in (list(agg_node.df_in_vars.values()) + list(agg_node.
            df_out_vars.values()) + agg_node.key_arrs):
            if array_dists[v.name
                ] != distributed_pass.Distribution.OneD and array_dists[v.name
                ] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    sst__xjbu = tuple(typemap[v.name] for v in agg_node.key_arrs)
    zsq__ojtq = [v for ijn__fego, v in agg_node.df_in_vars.items()]
    gnc__sncwm = [v for ijn__fego, v in agg_node.df_out_vars.items()]
    in_col_typs = []
    kgveu__qwcvd = []
    if agg_node.pivot_arr is not None:
        for egj__buy, zxkh__tmrm in agg_node.gb_info_in.items():
            for func, jzjcx__dlyw in zxkh__tmrm:
                if egj__buy is not None:
                    in_col_typs.append(typemap[agg_node.df_in_vars[egj__buy
                        ].name])
                kgveu__qwcvd.append(func)
    else:
        for egj__buy, func in agg_node.gb_info_out.values():
            if egj__buy is not None:
                in_col_typs.append(typemap[agg_node.df_in_vars[egj__buy].name])
            kgveu__qwcvd.append(func)
    out_col_typs = tuple(typemap[v.name] for v in gnc__sncwm)
    pivot_typ = types.none if agg_node.pivot_arr is None else typemap[agg_node
        .pivot_arr.name]
    arg_typs = tuple(sst__xjbu + tuple(typemap[v.name] for v in zsq__ojtq) +
        (pivot_typ,))
    jnm__gkbz = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for i, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            jnm__gkbz.update({f'in_cat_dtype_{i}': in_col_typ})
    for i, sey__yztzx in enumerate(out_col_typs):
        if isinstance(sey__yztzx, bodo.CategoricalArrayType):
            jnm__gkbz.update({f'out_cat_dtype_{i}': sey__yztzx})
    udf_func_struct = get_udf_func_struct(kgveu__qwcvd, agg_node.
        input_has_index, in_col_typs, out_col_typs, typingctx, targetctx,
        pivot_typ, agg_node.pivot_values, agg_node.is_crosstab)
    vlw__yghk = gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
        parallel, udf_func_struct)
    jnm__gkbz.update({'pd': pd, 'pre_alloc_string_array':
        pre_alloc_string_array, 'pre_alloc_binary_array':
        pre_alloc_binary_array, 'pre_alloc_array_item_array':
        pre_alloc_array_item_array, 'string_array_type': string_array_type,
        'alloc_decimal_array': alloc_decimal_array, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'coerce_to_array': bodo.utils.conversion.coerce_to_array,
        'groupby_and_aggregate': groupby_and_aggregate,
        'pivot_groupby_and_aggregate': pivot_groupby_and_aggregate,
        'compute_node_partition_by_hash': compute_node_partition_by_hash,
        'info_from_table': info_from_table, 'info_to_array': info_to_array,
        'delete_info_decref_array': delete_info_decref_array,
        'delete_table': delete_table, 'add_agg_cfunc_sym':
        add_agg_cfunc_sym, 'get_agg_udf_addr': get_agg_udf_addr,
        'delete_table_decref_arrays': delete_table_decref_arrays})
    if udf_func_struct is not None:
        if udf_func_struct.regular_udfs:
            jnm__gkbz.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            jnm__gkbz.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    cer__nwk = compile_to_numba_ir(vlw__yghk, jnm__gkbz, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    gdi__pviz = []
    if agg_node.pivot_arr is None:
        bwbw__vnik = agg_node.key_arrs[0].scope
        loc = agg_node.loc
        lgvu__fcrzt = ir.Var(bwbw__vnik, mk_unique_var('dummy_none'), loc)
        typemap[lgvu__fcrzt.name] = types.none
        gdi__pviz.append(ir.Assign(ir.Const(None, loc), lgvu__fcrzt, loc))
        zsq__ojtq.append(lgvu__fcrzt)
    else:
        zsq__ojtq.append(agg_node.pivot_arr)
    replace_arg_nodes(cer__nwk, agg_node.key_arrs + zsq__ojtq)
    djc__tat = cer__nwk.body[-3]
    assert is_assign(djc__tat) and isinstance(djc__tat.value, ir.Expr
        ) and djc__tat.value.op == 'build_tuple'
    gdi__pviz += cer__nwk.body[:-3]
    ukp__zdiv = list(agg_node.df_out_vars.values())
    if agg_node.out_key_vars is not None:
        ukp__zdiv += agg_node.out_key_vars
    for i, ccgqm__csjb in enumerate(ukp__zdiv):
        zyxya__wiv = djc__tat.value.items[i]
        gdi__pviz.append(ir.Assign(zyxya__wiv, ccgqm__csjb, ccgqm__csjb.loc))
    return gdi__pviz


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def get_numba_set(dtype):
    pass


@infer_global(get_numba_set)
class GetNumbaSetTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        arr = args[0]
        dtype = types.Tuple([t.dtype for t in arr.types]) if isinstance(arr,
            types.BaseTuple) else arr.dtype
        if isinstance(arr, types.BaseTuple) and len(arr.types) == 1:
            dtype = arr.types[0].dtype
        return signature(types.Set(dtype), *args)


@lower_builtin(get_numba_set, types.Any)
def lower_get_numba_set(context, builder, sig, args):
    return numba.cpython.setobj.set_empty_constructor(context, builder, sig,
        args)


@infer_global(bool)
class BoolNoneTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        llpo__pibjn = args[0]
        if llpo__pibjn == types.none:
            return signature(types.boolean, *args)


@lower_builtin(bool, types.none)
def lower_column_mean_impl(context, builder, sig, args):
    sykw__npeq = context.compile_internal(builder, lambda a: False, sig, args)
    return sykw__npeq


def setitem_array_with_str(arr, i, v):
    return


@overload(setitem_array_with_str)
def setitem_array_with_str_overload(arr, i, val):
    if arr == string_array_type:

        def setitem_str_arr(arr, i, val):
            arr[i] = val
        return setitem_str_arr
    if val == string_type:
        return lambda arr, i, val: None

    def setitem_impl(arr, i, val):
        arr[i] = val
    return setitem_impl


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        ajzo__fbai = IntDtype(t.dtype).name
        assert ajzo__fbai.endswith('Dtype()')
        ajzo__fbai = ajzo__fbai[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{ajzo__fbai}'))"
            )
    elif isinstance(t, BooleanArrayType):
        return (
            'bodo.libs.bool_arr_ext.init_bool_array(np.empty(0, np.bool_), np.empty(0, np.uint8))'
            )
    elif isinstance(t, StringArrayType):
        return 'pre_alloc_string_array(1, 1)'
    elif isinstance(t, BinaryArrayType):
        return 'pre_alloc_binary_array(1, 1)'
    elif t == ArrayItemArrayType(string_array_type):
        return 'pre_alloc_array_item_array(1, (1, 1), string_array_type)'
    elif isinstance(t, DecimalArrayType):
        return 'alloc_decimal_array(1, {}, {})'.format(t.precision, t.scale)
    elif isinstance(t, DatetimeDateArrayType):
        return (
            'bodo.hiframes.datetime_date_ext.init_datetime_date_array(np.empty(1, np.int64), np.empty(1, np.uint8))'
            )
    elif isinstance(t, bodo.CategoricalArrayType):
        if t.dtype.categories is None:
            raise BodoError(
                'Groupby agg operations on Categorical types require constant categories'
                )
        std__nvsvi = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {std__nvsvi}_cat_dtype_{colnum})')
    else:
        return 'np.empty(1, {})'.format(_get_np_dtype(t.dtype))


def _get_np_dtype(t):
    if t == types.bool_:
        return 'np.bool_'
    if t == types.NPDatetime('ns'):
        return 'dt64_dtype'
    if t == types.NPTimedelta('ns'):
        return 'td64_dtype'
    return 'np.{}'.format(t)


def gen_update_cb(udf_func_struct, allfuncs, n_keys, data_in_typs_,
    out_data_typs, do_combine, func_idx_to_in_col, label_suffix):
    rvorx__oryo = udf_func_struct.var_typs
    sjsx__tceev = len(rvorx__oryo)
    bnt__oak = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    bnt__oak += '    if is_null_pointer(in_table):\n'
    bnt__oak += '        return\n'
    bnt__oak += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in rvorx__oryo]), 
        ',' if len(rvorx__oryo) == 1 else '')
    avj__iqn = n_keys
    mxd__dnd = []
    redvar_offsets = []
    ugpua__rral = []
    if do_combine:
        for i, yxnp__rntmv in enumerate(allfuncs):
            if yxnp__rntmv.ftype != 'udf':
                avj__iqn += yxnp__rntmv.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(avj__iqn, avj__iqn +
                    yxnp__rntmv.n_redvars))
                avj__iqn += yxnp__rntmv.n_redvars
                ugpua__rral.append(data_in_typs_[func_idx_to_in_col[i]])
                mxd__dnd.append(func_idx_to_in_col[i] + n_keys)
    else:
        for i, yxnp__rntmv in enumerate(allfuncs):
            if yxnp__rntmv.ftype != 'udf':
                avj__iqn += yxnp__rntmv.ncols_post_shuffle
            else:
                redvar_offsets += list(range(avj__iqn + 1, avj__iqn + 1 +
                    yxnp__rntmv.n_redvars))
                avj__iqn += yxnp__rntmv.n_redvars + 1
                ugpua__rral.append(data_in_typs_[func_idx_to_in_col[i]])
                mxd__dnd.append(func_idx_to_in_col[i] + n_keys)
    assert len(redvar_offsets) == sjsx__tceev
    ire__zug = len(ugpua__rral)
    uesux__snvv = []
    for i, t in enumerate(ugpua__rral):
        uesux__snvv.append(_gen_dummy_alloc(t, i, True))
    bnt__oak += '    data_in_dummy = ({}{})\n'.format(','.join(uesux__snvv),
        ',' if len(ugpua__rral) == 1 else '')
    bnt__oak += """
    # initialize redvar cols
"""
    bnt__oak += '    init_vals = __init_func()\n'
    for i in range(sjsx__tceev):
        bnt__oak += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(i, redvar_offsets[i], i))
        bnt__oak += '    incref(redvar_arr_{})\n'.format(i)
        bnt__oak += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(i, i)
    bnt__oak += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(i) for i in range(sjsx__tceev)]), ',' if sjsx__tceev == 1 else
        '')
    bnt__oak += '\n'
    for i in range(ire__zug):
        bnt__oak += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(i, mxd__dnd[i], i))
        bnt__oak += '    incref(data_in_{})\n'.format(i)
    bnt__oak += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(i) for i in range(ire__zug)]), ',' if ire__zug == 1 else '')
    bnt__oak += '\n'
    bnt__oak += '    for i in range(len(data_in_0)):\n'
    bnt__oak += '        w_ind = row_to_group[i]\n'
    bnt__oak += '        if w_ind != -1:\n'
    bnt__oak += (
        '            __update_redvars(redvars, data_in, w_ind, i, pivot_arr=None)\n'
        )
    nayu__zzxdv = {}
    exec(bnt__oak, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, nayu__zzxdv)
    return nayu__zzxdv['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, out_data_typs,
    label_suffix):
    rvorx__oryo = udf_func_struct.var_typs
    sjsx__tceev = len(rvorx__oryo)
    bnt__oak = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    bnt__oak += '    if is_null_pointer(in_table):\n'
    bnt__oak += '        return\n'
    bnt__oak += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in rvorx__oryo]), 
        ',' if len(rvorx__oryo) == 1 else '')
    zigcx__djtii = n_keys
    juq__sty = n_keys
    ucfcz__gpah = []
    qrzjm__oufsz = []
    for yxnp__rntmv in allfuncs:
        if yxnp__rntmv.ftype != 'udf':
            zigcx__djtii += yxnp__rntmv.ncols_pre_shuffle
            juq__sty += yxnp__rntmv.ncols_post_shuffle
        else:
            ucfcz__gpah += list(range(zigcx__djtii, zigcx__djtii +
                yxnp__rntmv.n_redvars))
            qrzjm__oufsz += list(range(juq__sty + 1, juq__sty + 1 +
                yxnp__rntmv.n_redvars))
            zigcx__djtii += yxnp__rntmv.n_redvars
            juq__sty += 1 + yxnp__rntmv.n_redvars
    assert len(ucfcz__gpah) == sjsx__tceev
    bnt__oak += """
    # initialize redvar cols
"""
    bnt__oak += '    init_vals = __init_func()\n'
    for i in range(sjsx__tceev):
        bnt__oak += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(i, qrzjm__oufsz[i], i))
        bnt__oak += '    incref(redvar_arr_{})\n'.format(i)
        bnt__oak += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(i, i)
    bnt__oak += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(i) for i in range(sjsx__tceev)]), ',' if sjsx__tceev == 1 else
        '')
    bnt__oak += '\n'
    for i in range(sjsx__tceev):
        bnt__oak += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(i, ucfcz__gpah[i], i))
        bnt__oak += '    incref(recv_redvar_arr_{})\n'.format(i)
    bnt__oak += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(i) for i in range(sjsx__tceev)]), ',' if
        sjsx__tceev == 1 else '')
    bnt__oak += '\n'
    if sjsx__tceev:
        bnt__oak += '    for i in range(len(recv_redvar_arr_0)):\n'
        bnt__oak += '        w_ind = row_to_group[i]\n'
        bnt__oak += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i, pivot_arr=None)\n'
            )
    nayu__zzxdv = {}
    exec(bnt__oak, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, nayu__zzxdv)
    return nayu__zzxdv['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    rvorx__oryo = udf_func_struct.var_typs
    sjsx__tceev = len(rvorx__oryo)
    avj__iqn = n_keys
    redvar_offsets = []
    omgls__icxol = []
    out_data_typs = []
    for i, yxnp__rntmv in enumerate(allfuncs):
        if yxnp__rntmv.ftype != 'udf':
            avj__iqn += yxnp__rntmv.ncols_post_shuffle
        else:
            omgls__icxol.append(avj__iqn)
            redvar_offsets += list(range(avj__iqn + 1, avj__iqn + 1 +
                yxnp__rntmv.n_redvars))
            avj__iqn += 1 + yxnp__rntmv.n_redvars
            out_data_typs.append(out_data_typs_[i])
    assert len(redvar_offsets) == sjsx__tceev
    ire__zug = len(out_data_typs)
    bnt__oak = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    bnt__oak += '    if is_null_pointer(table):\n'
    bnt__oak += '        return\n'
    bnt__oak += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in rvorx__oryo]), 
        ',' if len(rvorx__oryo) == 1 else '')
    bnt__oak += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        out_data_typs]), ',' if len(out_data_typs) == 1 else '')
    for i in range(sjsx__tceev):
        bnt__oak += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(i, redvar_offsets[i], i))
        bnt__oak += '    incref(redvar_arr_{})\n'.format(i)
    bnt__oak += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(i) for i in range(sjsx__tceev)]), ',' if sjsx__tceev == 1 else
        '')
    bnt__oak += '\n'
    for i in range(ire__zug):
        bnt__oak += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(i, omgls__icxol[i], i))
        bnt__oak += '    incref(data_out_{})\n'.format(i)
    bnt__oak += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(i) for i in range(ire__zug)]), ',' if ire__zug == 1 else '')
    bnt__oak += '\n'
    bnt__oak += '    for i in range(len(data_out_0)):\n'
    bnt__oak += '        __eval_res(redvars, data_out, i)\n'
    nayu__zzxdv = {}
    exec(bnt__oak, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, nayu__zzxdv)
    return nayu__zzxdv['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    avj__iqn = n_keys
    wghc__isl = []
    for i, yxnp__rntmv in enumerate(allfuncs):
        if yxnp__rntmv.ftype == 'gen_udf':
            wghc__isl.append(avj__iqn)
            avj__iqn += 1
        elif yxnp__rntmv.ftype != 'udf':
            avj__iqn += yxnp__rntmv.ncols_post_shuffle
        else:
            avj__iqn += yxnp__rntmv.n_redvars + 1
    bnt__oak = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    bnt__oak += '    if num_groups == 0:\n'
    bnt__oak += '        return\n'
    for i, func in enumerate(udf_func_struct.general_udf_funcs):
        bnt__oak += '    # col {}\n'.format(i)
        bnt__oak += (
            '    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)\n'
            .format(wghc__isl[i], i))
        bnt__oak += '    incref(out_col)\n'
        bnt__oak += '    for j in range(num_groups):\n'
        bnt__oak += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(i, i))
        bnt__oak += '        incref(in_col)\n'
        bnt__oak += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(i))
    jnm__gkbz = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    eft__rwzk = 0
    for i, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[eft__rwzk]
        jnm__gkbz['func_{}'.format(eft__rwzk)] = func
        jnm__gkbz['in_col_{}_typ'.format(eft__rwzk)] = in_col_typs[
            func_idx_to_in_col[i]]
        jnm__gkbz['out_col_{}_typ'.format(eft__rwzk)] = out_col_typs[i]
        eft__rwzk += 1
    nayu__zzxdv = {}
    exec(bnt__oak, jnm__gkbz, nayu__zzxdv)
    yxnp__rntmv = nayu__zzxdv['bodo_gb_apply_general_udfs{}'.format(
        label_suffix)]
    vgxlq__ffpzv = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(vgxlq__ffpzv, nopython=True)(yxnp__rntmv)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs, parallel,
    udf_func_struct):
    gtx__ttm = agg_node.pivot_arr is not None
    if agg_node.same_index:
        assert agg_node.input_has_index
    if agg_node.pivot_values is None:
        tpv__enrpk = 1
    else:
        tpv__enrpk = len(agg_node.pivot_values)
    rhia__fdi = tuple('key_' + sanitize_varname(jqzg__sklz) for jqzg__sklz in
        agg_node.key_names)
    hpwfa__feqp = {jqzg__sklz: 'in_{}'.format(sanitize_varname(jqzg__sklz)) for
        jqzg__sklz in agg_node.gb_info_in.keys() if jqzg__sklz is not None}
    vrc__eag = {jqzg__sklz: ('out_' + sanitize_varname(jqzg__sklz)) for
        jqzg__sklz in agg_node.gb_info_out.keys()}
    n_keys = len(agg_node.key_names)
    pebv__cbz = ', '.join(rhia__fdi)
    eimut__qfaaz = ', '.join(hpwfa__feqp.values())
    if eimut__qfaaz != '':
        eimut__qfaaz = ', ' + eimut__qfaaz
    bnt__oak = 'def agg_top({}{}{}, pivot_arr):\n'.format(pebv__cbz,
        eimut__qfaaz, ', index_arg' if agg_node.input_has_index else '')
    if gtx__ttm:
        coset__watuv = []
        for egj__buy, zxkh__tmrm in agg_node.gb_info_in.items():
            if egj__buy is not None:
                for func, jzjcx__dlyw in zxkh__tmrm:
                    coset__watuv.append(hpwfa__feqp[egj__buy])
    else:
        coset__watuv = tuple(hpwfa__feqp[egj__buy] for egj__buy,
            jzjcx__dlyw in agg_node.gb_info_out.values() if egj__buy is not
            None)
    cqjz__aij = rhia__fdi + tuple(coset__watuv)
    bnt__oak += '    info_list = [{}{}{}]\n'.format(', '.join(
        'array_to_info({})'.format(a) for a in cqjz__aij), 
        ', array_to_info(index_arg)' if agg_node.input_has_index else '', 
        ', array_to_info(pivot_arr)' if agg_node.is_crosstab else '')
    bnt__oak += '    table = arr_info_list_to_table(info_list)\n'
    for i, jqzg__sklz in enumerate(agg_node.gb_info_out.keys()):
        kdd__couh = vrc__eag[jqzg__sklz] + '_dummy'
        sey__yztzx = out_col_typs[i]
        egj__buy, func = agg_node.gb_info_out[jqzg__sklz]
        if isinstance(func, pytypes.SimpleNamespace) and func.fname in ['min',
            'max', 'shift'] and isinstance(sey__yztzx, bodo.
            CategoricalArrayType):
            bnt__oak += '    {} = {}\n'.format(kdd__couh, hpwfa__feqp[egj__buy]
                )
        else:
            bnt__oak += '    {} = {}\n'.format(kdd__couh, _gen_dummy_alloc(
                sey__yztzx, i, False))
    do_combine = parallel
    allfuncs = []
    imbb__gtku = []
    func_idx_to_in_col = []
    ltkdj__bqmrf = []
    nnovo__tuul = False
    hziz__mimb = 1
    hvjmg__vgu = -1
    qxv__lvjh = 0
    jmow__ssqe = 0
    if not gtx__ttm:
        kgveu__qwcvd = [func for jzjcx__dlyw, func in agg_node.gb_info_out.
            values()]
    else:
        kgveu__qwcvd = [func for func, jzjcx__dlyw in zxkh__tmrm for
            zxkh__tmrm in agg_node.gb_info_in.values()]
    for lgkq__nlng, func in enumerate(kgveu__qwcvd):
        imbb__gtku.append(len(allfuncs))
        if func.ftype in {'median', 'nunique'}:
            do_combine = False
        if func.ftype in list_cumulative:
            qxv__lvjh += 1
        if hasattr(func, 'skipdropna'):
            nnovo__tuul = func.skipdropna
        if func.ftype == 'shift':
            hziz__mimb = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            jmow__ssqe = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            hvjmg__vgu = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(lgkq__nlng)
        if func.ftype == 'udf':
            ltkdj__bqmrf.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            ltkdj__bqmrf.append(0)
            do_combine = False
    imbb__gtku.append(len(allfuncs))
    if agg_node.is_crosstab:
        assert len(agg_node.gb_info_out
            ) == tpv__enrpk, 'invalid number of groupby outputs for pivot'
    else:
        assert len(agg_node.gb_info_out) == len(allfuncs
            ) * tpv__enrpk, 'invalid number of groupby outputs'
    if qxv__lvjh > 0:
        if qxv__lvjh != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    if udf_func_struct is not None:
        tss__rjwht = next_label()
        if udf_func_struct.regular_udfs:
            vgxlq__ffpzv = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            nxppn__bxw = numba.cfunc(vgxlq__ffpzv, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs,
                out_col_typs, do_combine, func_idx_to_in_col, tss__rjwht))
            ujcp__bygi = numba.cfunc(vgxlq__ffpzv, nopython=True)(
                gen_combine_cb(udf_func_struct, allfuncs, n_keys,
                out_col_typs, tss__rjwht))
            deg__rrq = numba.cfunc('void(voidptr)', nopython=True)(gen_eval_cb
                (udf_func_struct, allfuncs, n_keys, out_col_typs, tss__rjwht))
            udf_func_struct.set_regular_cfuncs(nxppn__bxw, ujcp__bygi, deg__rrq
                )
            for awp__xwpn in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[awp__xwpn.native_name] = awp__xwpn
                gb_agg_cfunc_addr[awp__xwpn.native_name] = awp__xwpn.address
        if udf_func_struct.general_udfs:
            yplp__llp = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, out_col_typs, func_idx_to_in_col,
                tss__rjwht)
            udf_func_struct.set_general_cfunc(yplp__llp)
        easb__zztv = []
        ohdru__rbz = 0
        i = 0
        for kdd__couh, yxnp__rntmv in zip(vrc__eag.values(), allfuncs):
            if yxnp__rntmv.ftype in ('udf', 'gen_udf'):
                easb__zztv.append(kdd__couh + '_dummy')
                for xov__kwj in range(ohdru__rbz, ohdru__rbz + ltkdj__bqmrf[i]
                    ):
                    easb__zztv.append('data_redvar_dummy_' + str(xov__kwj))
                ohdru__rbz += ltkdj__bqmrf[i]
                i += 1
        if udf_func_struct.regular_udfs:
            rvorx__oryo = udf_func_struct.var_typs
            for i, t in enumerate(rvorx__oryo):
                bnt__oak += ('    data_redvar_dummy_{} = np.empty(1, {})\n'
                    .format(i, _get_np_dtype(t)))
        bnt__oak += '    out_info_list_dummy = [{}]\n'.format(', '.join(
            'array_to_info({})'.format(a) for a in easb__zztv))
        bnt__oak += (
            '    udf_table_dummy = arr_info_list_to_table(out_info_list_dummy)\n'
            )
        if udf_func_struct.regular_udfs:
            bnt__oak += "    add_agg_cfunc_sym(cpp_cb_update, '{}')\n".format(
                nxppn__bxw.native_name)
            bnt__oak += "    add_agg_cfunc_sym(cpp_cb_combine, '{}')\n".format(
                ujcp__bygi.native_name)
            bnt__oak += "    add_agg_cfunc_sym(cpp_cb_eval, '{}')\n".format(
                deg__rrq.native_name)
            bnt__oak += ("    cpp_cb_update_addr = get_agg_udf_addr('{}')\n"
                .format(nxppn__bxw.native_name))
            bnt__oak += ("    cpp_cb_combine_addr = get_agg_udf_addr('{}')\n"
                .format(ujcp__bygi.native_name))
            bnt__oak += ("    cpp_cb_eval_addr = get_agg_udf_addr('{}')\n".
                format(deg__rrq.native_name))
        else:
            bnt__oak += '    cpp_cb_update_addr = 0\n'
            bnt__oak += '    cpp_cb_combine_addr = 0\n'
            bnt__oak += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            awp__xwpn = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[awp__xwpn.native_name] = awp__xwpn
            gb_agg_cfunc_addr[awp__xwpn.native_name] = awp__xwpn.address
            bnt__oak += "    add_agg_cfunc_sym(cpp_cb_general, '{}')\n".format(
                awp__xwpn.native_name)
            bnt__oak += ("    cpp_cb_general_addr = get_agg_udf_addr('{}')\n"
                .format(awp__xwpn.native_name))
        else:
            bnt__oak += '    cpp_cb_general_addr = 0\n'
    else:
        bnt__oak += (
            '    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])\n'
            )
        bnt__oak += '    cpp_cb_update_addr = 0\n'
        bnt__oak += '    cpp_cb_combine_addr = 0\n'
        bnt__oak += '    cpp_cb_eval_addr = 0\n'
        bnt__oak += '    cpp_cb_general_addr = 0\n'
    bnt__oak += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(', '
        .join([str(supported_agg_funcs.index(yxnp__rntmv.ftype)) for
        yxnp__rntmv in allfuncs] + ['0']))
    bnt__oak += '    func_offsets = np.array({}, dtype=np.int32)\n'.format(str
        (imbb__gtku))
    if len(ltkdj__bqmrf) > 0:
        bnt__oak += '    udf_ncols = np.array({}, dtype=np.int32)\n'.format(str
            (ltkdj__bqmrf))
    else:
        bnt__oak += '    udf_ncols = np.array([0], np.int32)\n'
    if gtx__ttm:
        bnt__oak += '    arr_type = coerce_to_array({})\n'.format(agg_node.
            pivot_values)
        bnt__oak += '    arr_info = array_to_info(arr_type)\n'
        bnt__oak += '    dispatch_table = arr_info_list_to_table([arr_info])\n'
        bnt__oak += '    pivot_info = array_to_info(pivot_arr)\n'
        bnt__oak += (
            '    dispatch_info = arr_info_list_to_table([pivot_info])\n')
        bnt__oak += (
            """    out_table = pivot_groupby_and_aggregate(table, {}, dispatch_table, dispatch_info, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, agg_node.
            is_crosstab, nnovo__tuul, agg_node.return_key, agg_node.same_index)
            )
        bnt__oak += '    delete_info_decref_array(pivot_info)\n'
        bnt__oak += '    delete_info_decref_array(arr_info)\n'
    else:
        bnt__oak += (
            """    out_table = groupby_and_aggregate(table, {}, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, nnovo__tuul,
            hziz__mimb, jmow__ssqe, hvjmg__vgu, agg_node.return_key,
            agg_node.same_index, agg_node.dropna))
    yek__khpj = 0
    if agg_node.return_key:
        for i, ulrgw__httje in enumerate(rhia__fdi):
            bnt__oak += (
                '    {} = info_to_array(info_from_table(out_table, {}), {})\n'
                .format(ulrgw__httje, yek__khpj, ulrgw__httje))
            yek__khpj += 1
    for kdd__couh in vrc__eag.values():
        bnt__oak += (
            '    {} = info_to_array(info_from_table(out_table, {}), {})\n'.
            format(kdd__couh, yek__khpj, kdd__couh + '_dummy'))
        yek__khpj += 1
    if agg_node.same_index:
        bnt__oak += (
            """    out_index_arg = info_to_array(info_from_table(out_table, {}), index_arg)
"""
            .format(yek__khpj))
        yek__khpj += 1
    bnt__oak += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    bnt__oak += '    delete_table_decref_arrays(table)\n'
    bnt__oak += '    delete_table_decref_arrays(udf_table_dummy)\n'
    bnt__oak += '    delete_table(out_table)\n'
    bnt__oak += f'    ev_clean.finalize()\n'
    qxxci__udkjf = tuple(vrc__eag.values())
    if agg_node.return_key:
        qxxci__udkjf += tuple(rhia__fdi)
    bnt__oak += '    return ({},{})\n'.format(', '.join(qxxci__udkjf), 
        ' out_index_arg,' if agg_node.same_index else '')
    nayu__zzxdv = {}
    exec(bnt__oak, {}, nayu__zzxdv)
    lcyrf__edvsr = nayu__zzxdv['agg_top']
    return lcyrf__edvsr


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for adjxf__lddt in block.body:
            if is_call_assign(adjxf__lddt) and find_callname(f_ir,
                adjxf__lddt.value) == ('len', 'builtins'
                ) and adjxf__lddt.value.args[0].name == f_ir.arg_names[0]:
                zej__mgzct = get_definition(f_ir, adjxf__lddt.value.func)
                zej__mgzct.name = 'dummy_agg_count'
                zej__mgzct.value = dummy_agg_count
    zdn__asdtr = get_name_var_table(f_ir.blocks)
    fmasg__fnasy = {}
    for name, jzjcx__dlyw in zdn__asdtr.items():
        fmasg__fnasy[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, fmasg__fnasy)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    hhrga__ftdm = numba.core.compiler.Flags()
    hhrga__ftdm.nrt = True
    aro__pbd = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, hhrga__ftdm)
    aro__pbd.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, ltob__qsu, calltypes, jzjcx__dlyw = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    ndjq__kfp = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    wot__svkz = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    yetb__bszpr = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    bzf__nqoar = yetb__bszpr(typemap, calltypes)
    pm = wot__svkz(typingctx, targetctx, None, f_ir, typemap, ltob__qsu,
        calltypes, bzf__nqoar, {}, hhrga__ftdm, None)
    xzkxp__whh = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = wot__svkz(typingctx, targetctx, None, f_ir, typemap, ltob__qsu,
        calltypes, bzf__nqoar, {}, hhrga__ftdm, xzkxp__whh)
    wjk__ewmo = numba.core.typed_passes.InlineOverloads()
    wjk__ewmo.run_pass(pm)
    vwmf__segdr = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    vwmf__segdr.run()
    for block in f_ir.blocks.values():
        for adjxf__lddt in block.body:
            if is_assign(adjxf__lddt) and isinstance(adjxf__lddt.value, (ir
                .Arg, ir.Var)) and isinstance(typemap[adjxf__lddt.target.
                name], SeriesType):
                svbd__uci = typemap.pop(adjxf__lddt.target.name)
                typemap[adjxf__lddt.target.name] = svbd__uci.data
            if is_call_assign(adjxf__lddt) and find_callname(f_ir,
                adjxf__lddt.value) == ('get_series_data',
                'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[adjxf__lddt.target.name].remove(adjxf__lddt
                    .value)
                adjxf__lddt.value = adjxf__lddt.value.args[0]
                f_ir._definitions[adjxf__lddt.target.name].append(adjxf__lddt
                    .value)
            if is_call_assign(adjxf__lddt) and find_callname(f_ir,
                adjxf__lddt.value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[adjxf__lddt.target.name].remove(adjxf__lddt
                    .value)
                adjxf__lddt.value = ir.Const(False, adjxf__lddt.loc)
                f_ir._definitions[adjxf__lddt.target.name].append(adjxf__lddt
                    .value)
            if is_call_assign(adjxf__lddt) and find_callname(f_ir,
                adjxf__lddt.value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[adjxf__lddt.target.name].remove(adjxf__lddt
                    .value)
                adjxf__lddt.value = ir.Const(False, adjxf__lddt.loc)
                f_ir._definitions[adjxf__lddt.target.name].append(adjxf__lddt
                    .value)
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    tflo__lgt = numba.parfors.parfor.PreParforPass(f_ir, typemap, calltypes,
        typingctx, targetctx, ndjq__kfp)
    tflo__lgt.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    rnztj__kchf = numba.core.compiler.StateDict()
    rnztj__kchf.func_ir = f_ir
    rnztj__kchf.typemap = typemap
    rnztj__kchf.calltypes = calltypes
    rnztj__kchf.typingctx = typingctx
    rnztj__kchf.targetctx = targetctx
    rnztj__kchf.return_type = ltob__qsu
    numba.core.rewrites.rewrite_registry.apply('after-inference', rnztj__kchf)
    wysu__gjx = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        ltob__qsu, typingctx, targetctx, ndjq__kfp, hhrga__ftdm, {})
    wysu__gjx.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            bgd__udws = ctypes.pythonapi.PyCell_Get
            bgd__udws.restype = ctypes.py_object
            bgd__udws.argtypes = ctypes.py_object,
            rrr__uemxe = tuple(bgd__udws(uwgja__snw) for uwgja__snw in closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            rrr__uemxe = closure.items
        assert len(code.co_freevars) == len(rrr__uemxe)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, rrr__uemxe
            )


class RegularUDFGenerator(object):

    def __init__(self, in_col_types, out_col_types, pivot_typ, pivot_values,
        is_crosstab, typingctx, targetctx):
        self.in_col_types = in_col_types
        self.out_col_types = out_col_types
        self.pivot_typ = pivot_typ
        self.pivot_values = pivot_values
        self.is_crosstab = is_crosstab
        self.typingctx = typingctx
        self.targetctx = targetctx
        self.all_reduce_vars = []
        self.all_vartypes = []
        self.all_init_nodes = []
        self.all_eval_funcs = []
        self.all_update_funcs = []
        self.all_combine_funcs = []
        self.curr_offset = 0
        self.redvar_offsets = [0]

    def add_udf(self, in_col_typ, func):
        livdd__tsxc = SeriesType(in_col_typ.dtype, in_col_typ, None,
            string_type)
        f_ir, pm = compile_to_optimized_ir(func, (livdd__tsxc,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        uhlie__kunt, arr_var = _rm_arg_agg_block(block, pm.typemap)
        okg__txre = -1
        for i, adjxf__lddt in enumerate(uhlie__kunt):
            if isinstance(adjxf__lddt, numba.parfors.parfor.Parfor):
                assert okg__txre == -1, 'only one parfor for aggregation function'
                okg__txre = i
        parfor = None
        if okg__txre != -1:
            parfor = uhlie__kunt[okg__txre]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = uhlie__kunt[:okg__txre] + parfor.init_block.body
        eval_nodes = uhlie__kunt[okg__txre + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for adjxf__lddt in init_nodes:
            if is_assign(adjxf__lddt) and adjxf__lddt.target.name in redvars:
                ind = redvars.index(adjxf__lddt.target.name)
                reduce_vars[ind] = adjxf__lddt.target
        var_types = [pm.typemap[v] for v in redvars]
        fyct__orzsh = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        ytps__keh = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        oqra__nvxvn = gen_eval_func(f_ir, eval_nodes, reduce_vars,
            var_types, pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(oqra__nvxvn)
        self.all_update_funcs.append(ytps__keh)
        self.all_combine_funcs.append(fyct__orzsh)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        self.all_vartypes = self.all_vartypes * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_vartypes
        self.all_reduce_vars = self.all_reduce_vars * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_reduce_vars
        qjdyn__enwh = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        xrhr__iqh = gen_all_update_func(self.all_update_funcs, self.
            all_vartypes, self.in_col_types, self.redvar_offsets, self.
            typingctx, self.targetctx, self.pivot_typ, self.pivot_values,
            self.is_crosstab)
        nzjyf__yoigw = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.
            targetctx, self.pivot_typ, self.pivot_values)
        kkqs__lcgun = gen_all_eval_func(self.all_eval_funcs, self.
            all_vartypes, self.redvar_offsets, self.out_col_types, self.
            typingctx, self.targetctx, self.pivot_values)
        return (self.all_vartypes, qjdyn__enwh, xrhr__iqh, nzjyf__yoigw,
            kkqs__lcgun)


class GeneralUDFGenerator(object):

    def __init__(self):
        self.funcs = []

    def add_udf(self, func):
        self.funcs.append(bodo.jit(distributed=False)(func))
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        func.n_redvars = 0

    def gen_all_func(self):
        if len(self.funcs) > 0:
            return self.funcs
        else:
            return None


def get_udf_func_struct(agg_func, input_has_index, in_col_types,
    out_col_types, typingctx, targetctx, pivot_typ, pivot_values, is_crosstab):
    if is_crosstab and len(in_col_types) == 0:
        in_col_types = [types.Array(types.intp, 1, 'C')]
    gehl__pahd = []
    for t, yxnp__rntmv in zip(in_col_types, agg_func):
        gehl__pahd.append((t, yxnp__rntmv))
    yhyb__xjkoa = RegularUDFGenerator(in_col_types, out_col_types,
        pivot_typ, pivot_values, is_crosstab, typingctx, targetctx)
    smuig__gpin = GeneralUDFGenerator()
    for in_col_typ, func in gehl__pahd:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            yhyb__xjkoa.add_udf(in_col_typ, func)
        except:
            smuig__gpin.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = yhyb__xjkoa.gen_all_func()
    general_udf_funcs = smuig__gpin.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    xul__dhn = compute_use_defs(parfor.loop_body)
    iyzo__vdu = set()
    for mdsj__pxrdr in xul__dhn.usemap.values():
        iyzo__vdu |= mdsj__pxrdr
    tal__bfdq = set()
    for mdsj__pxrdr in xul__dhn.defmap.values():
        tal__bfdq |= mdsj__pxrdr
    hxu__vfg = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    hxu__vfg.body = eval_nodes
    dews__elr = compute_use_defs({(0): hxu__vfg})
    psgqi__ajbtp = dews__elr.usemap[0]
    drvii__lmb = set()
    mfn__tglt = []
    hepfz__qdj = []
    for adjxf__lddt in reversed(init_nodes):
        xno__ioulf = {v.name for v in adjxf__lddt.list_vars()}
        if is_assign(adjxf__lddt):
            v = adjxf__lddt.target.name
            xno__ioulf.remove(v)
            if (v in iyzo__vdu and v not in drvii__lmb and v not in
                psgqi__ajbtp and v not in tal__bfdq):
                hepfz__qdj.append(adjxf__lddt)
                iyzo__vdu |= xno__ioulf
                tal__bfdq.add(v)
                continue
        drvii__lmb |= xno__ioulf
        mfn__tglt.append(adjxf__lddt)
    hepfz__qdj.reverse()
    mfn__tglt.reverse()
    brwrf__iwun = min(parfor.loop_body.keys())
    kszsn__ymi = parfor.loop_body[brwrf__iwun]
    kszsn__ymi.body = hepfz__qdj + kszsn__ymi.body
    return mfn__tglt


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    svnb__lwqr = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    xdbc__wcrvc = set()
    kciwb__aelmw = []
    for adjxf__lddt in init_nodes:
        if is_assign(adjxf__lddt) and isinstance(adjxf__lddt.value, ir.Global
            ) and isinstance(adjxf__lddt.value.value, pytypes.FunctionType
            ) and adjxf__lddt.value.value in svnb__lwqr:
            xdbc__wcrvc.add(adjxf__lddt.target.name)
        elif is_call_assign(adjxf__lddt
            ) and adjxf__lddt.value.func.name in xdbc__wcrvc:
            pass
        else:
            kciwb__aelmw.append(adjxf__lddt)
    init_nodes = kciwb__aelmw
    lygi__mufc = types.Tuple(var_types)
    pfb__hwcgj = lambda : None
    f_ir = compile_to_numba_ir(pfb__hwcgj, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    kdso__ramzq = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    jjjby__rdm = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc),
        kdso__ramzq, loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [jjjby__rdm] + block.body
    block.body[-2].value.value = kdso__ramzq
    lqxrn__qrlqd = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        lygi__mufc, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sbi__dfjld = numba.core.target_extension.dispatcher_registry[cpu_target](
        pfb__hwcgj)
    sbi__dfjld.add_overload(lqxrn__qrlqd)
    return sbi__dfjld


def gen_all_update_func(update_funcs, reduce_var_types, in_col_types,
    redvar_offsets, typingctx, targetctx, pivot_typ, pivot_values, is_crosstab
    ):
    pfpu__sqng = len(update_funcs)
    wwdt__dum = len(in_col_types)
    if pivot_values is not None:
        assert wwdt__dum == 1
    bnt__oak = 'def update_all_f(redvar_arrs, data_in, w_ind, i, pivot_arr):\n'
    if pivot_values is not None:
        ljbk__addp = redvar_offsets[wwdt__dum]
        bnt__oak += '  pv = pivot_arr[i]\n'
        for xov__kwj, mikav__gjws in enumerate(pivot_values):
            brczu__qihlt = 'el' if xov__kwj != 0 else ''
            bnt__oak += "  {}if pv == '{}':\n".format(brczu__qihlt, mikav__gjws
                )
            hawc__texj = ljbk__addp * xov__kwj
            eul__wsvo = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for i in
                range(hawc__texj + redvar_offsets[0], hawc__texj +
                redvar_offsets[1])])
            dtbtn__izh = 'data_in[0][i]'
            if is_crosstab:
                dtbtn__izh = '0'
            bnt__oak += '    {} = update_vars_0({}, {})\n'.format(eul__wsvo,
                eul__wsvo, dtbtn__izh)
    else:
        for xov__kwj in range(pfpu__sqng):
            eul__wsvo = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for i in
                range(redvar_offsets[xov__kwj], redvar_offsets[xov__kwj + 1])])
            if eul__wsvo:
                bnt__oak += ('  {} = update_vars_{}({},  data_in[{}][i])\n'
                    .format(eul__wsvo, xov__kwj, eul__wsvo, 0 if wwdt__dum ==
                    1 else xov__kwj))
    bnt__oak += '  return\n'
    jnm__gkbz = {}
    for i, yxnp__rntmv in enumerate(update_funcs):
        jnm__gkbz['update_vars_{}'.format(i)] = yxnp__rntmv
    nayu__zzxdv = {}
    exec(bnt__oak, jnm__gkbz, nayu__zzxdv)
    rwau__xskca = nayu__zzxdv['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(rwau__xskca)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx, pivot_typ, pivot_values):
    exr__xmw = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types])
    arg_typs = exr__xmw, exr__xmw, types.intp, types.intp, pivot_typ
    uoww__iyuu = len(redvar_offsets) - 1
    ljbk__addp = redvar_offsets[uoww__iyuu]
    bnt__oak = (
        'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        assert uoww__iyuu == 1
        for evif__ugwxj in range(len(pivot_values)):
            hawc__texj = ljbk__addp * evif__ugwxj
            eul__wsvo = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for i in
                range(hawc__texj + redvar_offsets[0], hawc__texj +
                redvar_offsets[1])])
            exb__alkz = ', '.join(['recv_arrs[{}][i]'.format(i) for i in
                range(hawc__texj + redvar_offsets[0], hawc__texj +
                redvar_offsets[1])])
            bnt__oak += '  {} = combine_vars_0({}, {})\n'.format(eul__wsvo,
                eul__wsvo, exb__alkz)
    else:
        for xov__kwj in range(uoww__iyuu):
            eul__wsvo = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for i in
                range(redvar_offsets[xov__kwj], redvar_offsets[xov__kwj + 1])])
            exb__alkz = ', '.join(['recv_arrs[{}][i]'.format(i) for i in
                range(redvar_offsets[xov__kwj], redvar_offsets[xov__kwj + 1])])
            if exb__alkz:
                bnt__oak += '  {} = combine_vars_{}({}, {})\n'.format(eul__wsvo
                    , xov__kwj, eul__wsvo, exb__alkz)
    bnt__oak += '  return\n'
    jnm__gkbz = {}
    for i, yxnp__rntmv in enumerate(combine_funcs):
        jnm__gkbz['combine_vars_{}'.format(i)] = yxnp__rntmv
    nayu__zzxdv = {}
    exec(bnt__oak, jnm__gkbz, nayu__zzxdv)
    ymdyg__pkctk = nayu__zzxdv['combine_all_f']
    f_ir = compile_to_numba_ir(ymdyg__pkctk, jnm__gkbz)
    nzjyf__yoigw = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sbi__dfjld = numba.core.target_extension.dispatcher_registry[cpu_target](
        ymdyg__pkctk)
    sbi__dfjld.add_overload(nzjyf__yoigw)
    return sbi__dfjld


def gen_all_eval_func(eval_funcs, reduce_var_types, redvar_offsets,
    out_col_typs, typingctx, targetctx, pivot_values):
    exr__xmw = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types])
    out_col_typs = types.Tuple(out_col_typs)
    uoww__iyuu = len(redvar_offsets) - 1
    ljbk__addp = redvar_offsets[uoww__iyuu]
    bnt__oak = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    if pivot_values is not None:
        assert uoww__iyuu == 1
        for xov__kwj in range(len(pivot_values)):
            hawc__texj = ljbk__addp * xov__kwj
            eul__wsvo = ', '.join(['redvar_arrs[{}][j]'.format(i) for i in
                range(hawc__texj + redvar_offsets[0], hawc__texj +
                redvar_offsets[1])])
            bnt__oak += '  out_arrs[{}][j] = eval_vars_0({})\n'.format(xov__kwj
                , eul__wsvo)
    else:
        for xov__kwj in range(uoww__iyuu):
            eul__wsvo = ', '.join(['redvar_arrs[{}][j]'.format(i) for i in
                range(redvar_offsets[xov__kwj], redvar_offsets[xov__kwj + 1])])
            bnt__oak += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
                xov__kwj, xov__kwj, eul__wsvo)
    bnt__oak += '  return\n'
    jnm__gkbz = {}
    for i, yxnp__rntmv in enumerate(eval_funcs):
        jnm__gkbz['eval_vars_{}'.format(i)] = yxnp__rntmv
    nayu__zzxdv = {}
    exec(bnt__oak, jnm__gkbz, nayu__zzxdv)
    bsgcg__tpiba = nayu__zzxdv['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(bsgcg__tpiba)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    hth__qik = len(var_types)
    ykzir__bxucc = [f'in{i}' for i in range(hth__qik)]
    lygi__mufc = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    hmfh__oig = lygi__mufc(0)
    bnt__oak = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        ykzir__bxucc))
    nayu__zzxdv = {}
    exec(bnt__oak, {'_zero': hmfh__oig}, nayu__zzxdv)
    jgxmp__svk = nayu__zzxdv['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(jgxmp__svk, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': hmfh__oig}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    snh__mkshu = []
    for i, v in enumerate(reduce_vars):
        snh__mkshu.append(ir.Assign(block.body[i].target, v, v.loc))
        for npa__gvww in v.versioned_names:
            snh__mkshu.append(ir.Assign(v, ir.Var(v.scope, npa__gvww, v.loc
                ), v.loc))
    block.body = block.body[:hth__qik] + snh__mkshu + eval_nodes
    oqra__nvxvn = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        lygi__mufc, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sbi__dfjld = numba.core.target_extension.dispatcher_registry[cpu_target](
        jgxmp__svk)
    sbi__dfjld.add_overload(oqra__nvxvn)
    return sbi__dfjld


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    hth__qik = len(redvars)
    lsyss__uxoim = [f'v{i}' for i in range(hth__qik)]
    ykzir__bxucc = [f'in{i}' for i in range(hth__qik)]
    bnt__oak = 'def agg_combine({}):\n'.format(', '.join(lsyss__uxoim +
        ykzir__bxucc))
    jwv__ekssk = wrap_parfor_blocks(parfor)
    anfi__dlte = find_topo_order(jwv__ekssk)
    anfi__dlte = anfi__dlte[1:]
    unwrap_parfor_blocks(parfor)
    jxmqe__xwuyu = {}
    wwsk__gyww = []
    for wwq__cigi in anfi__dlte:
        ufz__elrof = parfor.loop_body[wwq__cigi]
        for adjxf__lddt in ufz__elrof.body:
            if is_call_assign(adjxf__lddt) and guard(find_callname, f_ir,
                adjxf__lddt.value) == ('__special_combine', 'bodo.ir.aggregate'
                ):
                args = adjxf__lddt.value.args
                gcbib__dvyf = []
                akyy__dau = []
                for v in args[:-1]:
                    ind = redvars.index(v.name)
                    wwsk__gyww.append(ind)
                    gcbib__dvyf.append('v{}'.format(ind))
                    akyy__dau.append('in{}'.format(ind))
                feodk__ebi = '__special_combine__{}'.format(len(jxmqe__xwuyu))
                bnt__oak += '    ({},) = {}({})\n'.format(', '.join(
                    gcbib__dvyf), feodk__ebi, ', '.join(gcbib__dvyf +
                    akyy__dau))
                gnt__oqqbw = ir.Expr.call(args[-1], [], (), ufz__elrof.loc)
                zve__bpl = guard(find_callname, f_ir, gnt__oqqbw)
                assert zve__bpl == ('_var_combine', 'bodo.ir.aggregate')
                zve__bpl = bodo.ir.aggregate._var_combine
                jxmqe__xwuyu[feodk__ebi] = zve__bpl
            if is_assign(adjxf__lddt) and adjxf__lddt.target.name in redvars:
                wdgcp__uhm = adjxf__lddt.target.name
                ind = redvars.index(wdgcp__uhm)
                if ind in wwsk__gyww:
                    continue
                if len(f_ir._definitions[wdgcp__uhm]) == 2:
                    var_def = f_ir._definitions[wdgcp__uhm][0]
                    bnt__oak += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[wdgcp__uhm][1]
                    bnt__oak += _match_reduce_def(var_def, f_ir, ind)
    bnt__oak += '    return {}'.format(', '.join(['v{}'.format(i) for i in
        range(hth__qik)]))
    nayu__zzxdv = {}
    exec(bnt__oak, {}, nayu__zzxdv)
    cpom__qbr = nayu__zzxdv['agg_combine']
    arg_typs = tuple(2 * var_types)
    jnm__gkbz = {'numba': numba, 'bodo': bodo, 'np': np}
    jnm__gkbz.update(jxmqe__xwuyu)
    f_ir = compile_to_numba_ir(cpom__qbr, jnm__gkbz, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    lygi__mufc = pm.typemap[block.body[-1].value.name]
    fyct__orzsh = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        lygi__mufc, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sbi__dfjld = numba.core.target_extension.dispatcher_registry[cpu_target](
        cpom__qbr)
    sbi__dfjld.add_overload(fyct__orzsh)
    return sbi__dfjld


def _match_reduce_def(var_def, f_ir, ind):
    bnt__oak = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        bnt__oak = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        uqda__ootnd = guard(find_callname, f_ir, var_def)
        if uqda__ootnd == ('min', 'builtins'):
            bnt__oak = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if uqda__ootnd == ('max', 'builtins'):
            bnt__oak = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return bnt__oak


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    hth__qik = len(redvars)
    mwo__abw = 1
    unyfs__djw = []
    for i in range(mwo__abw):
        nsqcn__oxh = ir.Var(arr_var.scope, f'$input{i}', arr_var.loc)
        unyfs__djw.append(nsqcn__oxh)
    ayjb__crroe = parfor.loop_nests[0].index_variable
    vfri__gxgdz = [0] * hth__qik
    for ufz__elrof in parfor.loop_body.values():
        yugzt__foy = []
        for adjxf__lddt in ufz__elrof.body:
            if is_var_assign(adjxf__lddt
                ) and adjxf__lddt.value.name == ayjb__crroe.name:
                continue
            if is_getitem(adjxf__lddt
                ) and adjxf__lddt.value.value.name == arr_var.name:
                adjxf__lddt.value = unyfs__djw[0]
            if is_call_assign(adjxf__lddt) and guard(find_callname, pm.
                func_ir, adjxf__lddt.value) == ('isna',
                'bodo.libs.array_kernels') and adjxf__lddt.value.args[0
                ].name == arr_var.name:
                adjxf__lddt.value = ir.Const(False, adjxf__lddt.target.loc)
            if is_assign(adjxf__lddt) and adjxf__lddt.target.name in redvars:
                ind = redvars.index(adjxf__lddt.target.name)
                vfri__gxgdz[ind] = adjxf__lddt.target
            yugzt__foy.append(adjxf__lddt)
        ufz__elrof.body = yugzt__foy
    lsyss__uxoim = ['v{}'.format(i) for i in range(hth__qik)]
    ykzir__bxucc = ['in{}'.format(i) for i in range(mwo__abw)]
    bnt__oak = 'def agg_update({}):\n'.format(', '.join(lsyss__uxoim +
        ykzir__bxucc))
    bnt__oak += '    __update_redvars()\n'
    bnt__oak += '    return {}'.format(', '.join(['v{}'.format(i) for i in
        range(hth__qik)]))
    nayu__zzxdv = {}
    exec(bnt__oak, {}, nayu__zzxdv)
    qloaj__xse = nayu__zzxdv['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * mwo__abw)
    f_ir = compile_to_numba_ir(qloaj__xse, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    fpprc__ydjfz = f_ir.blocks.popitem()[1].body
    lygi__mufc = pm.typemap[fpprc__ydjfz[-1].value.name]
    jwv__ekssk = wrap_parfor_blocks(parfor)
    anfi__dlte = find_topo_order(jwv__ekssk)
    anfi__dlte = anfi__dlte[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    kszsn__ymi = f_ir.blocks[anfi__dlte[0]]
    bluvv__qzv = f_ir.blocks[anfi__dlte[-1]]
    doi__iqb = fpprc__ydjfz[:hth__qik + mwo__abw]
    if hth__qik > 1:
        txf__ulmoo = fpprc__ydjfz[-3:]
        assert is_assign(txf__ulmoo[0]) and isinstance(txf__ulmoo[0].value,
            ir.Expr) and txf__ulmoo[0].value.op == 'build_tuple'
    else:
        txf__ulmoo = fpprc__ydjfz[-2:]
    for i in range(hth__qik):
        qky__grmk = fpprc__ydjfz[i].target
        edf__erend = ir.Assign(qky__grmk, vfri__gxgdz[i], qky__grmk.loc)
        doi__iqb.append(edf__erend)
    for i in range(hth__qik, hth__qik + mwo__abw):
        qky__grmk = fpprc__ydjfz[i].target
        edf__erend = ir.Assign(qky__grmk, unyfs__djw[i - hth__qik],
            qky__grmk.loc)
        doi__iqb.append(edf__erend)
    kszsn__ymi.body = doi__iqb + kszsn__ymi.body
    wzf__vjng = []
    for i in range(hth__qik):
        qky__grmk = fpprc__ydjfz[i].target
        edf__erend = ir.Assign(vfri__gxgdz[i], qky__grmk, qky__grmk.loc)
        wzf__vjng.append(edf__erend)
    bluvv__qzv.body += wzf__vjng + txf__ulmoo
    ddn__gbzn = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        lygi__mufc, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sbi__dfjld = numba.core.target_extension.dispatcher_registry[cpu_target](
        qloaj__xse)
    sbi__dfjld.add_overload(ddn__gbzn)
    return sbi__dfjld


def _rm_arg_agg_block(block, typemap):
    uhlie__kunt = []
    arr_var = None
    for i, adjxf__lddt in enumerate(block.body):
        if is_assign(adjxf__lddt) and isinstance(adjxf__lddt.value, ir.Arg):
            arr_var = adjxf__lddt.target
            vkf__inkhz = typemap[arr_var.name]
            if not isinstance(vkf__inkhz, types.ArrayCompatible):
                uhlie__kunt += block.body[i + 1:]
                break
            gpfrp__glyx = block.body[i + 1]
            assert is_assign(gpfrp__glyx) and isinstance(gpfrp__glyx.value,
                ir.Expr
                ) and gpfrp__glyx.value.op == 'getattr' and gpfrp__glyx.value.attr == 'shape' and gpfrp__glyx.value.value.name == arr_var.name
            cmlk__pmah = gpfrp__glyx.target
            jtvf__gnosh = block.body[i + 2]
            assert is_assign(jtvf__gnosh) and isinstance(jtvf__gnosh.value,
                ir.Expr
                ) and jtvf__gnosh.value.op == 'static_getitem' and jtvf__gnosh.value.value.name == cmlk__pmah.name
            uhlie__kunt += block.body[i + 3:]
            break
        uhlie__kunt.append(adjxf__lddt)
    return uhlie__kunt, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    jwv__ekssk = wrap_parfor_blocks(parfor)
    anfi__dlte = find_topo_order(jwv__ekssk)
    anfi__dlte = anfi__dlte[1:]
    unwrap_parfor_blocks(parfor)
    for wwq__cigi in reversed(anfi__dlte):
        for adjxf__lddt in reversed(parfor.loop_body[wwq__cigi].body):
            if isinstance(adjxf__lddt, ir.Assign) and (adjxf__lddt.target.
                name in parfor_params or adjxf__lddt.target.name in
                var_to_param):
                vvnb__hhj = adjxf__lddt.target.name
                rhs = adjxf__lddt.value
                echlq__uec = (vvnb__hhj if vvnb__hhj in parfor_params else
                    var_to_param[vvnb__hhj])
                ffn__itc = []
                if isinstance(rhs, ir.Var):
                    ffn__itc = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    ffn__itc = [v.name for v in adjxf__lddt.value.list_vars()]
                param_uses[echlq__uec].extend(ffn__itc)
                for v in ffn__itc:
                    var_to_param[v] = echlq__uec
            if isinstance(adjxf__lddt, Parfor):
                get_parfor_reductions(adjxf__lddt, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for orwtv__zeyro, ffn__itc in param_uses.items():
        if orwtv__zeyro in ffn__itc and orwtv__zeyro not in reduce_varnames:
            reduce_varnames.append(orwtv__zeyro)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
