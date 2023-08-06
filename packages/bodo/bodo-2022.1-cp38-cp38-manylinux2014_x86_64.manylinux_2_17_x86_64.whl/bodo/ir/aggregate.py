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
            wdiu__jbcb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            vacz__ktdzk = cgutils.get_or_insert_function(builder.module,
                wdiu__jbcb, sym._literal_value)
            builder.call(vacz__ktdzk, [context.get_constant_null(sig.args[0])])
        elif sig == types.none(types.int64, types.voidptr, types.voidptr):
            wdiu__jbcb = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            vacz__ktdzk = cgutils.get_or_insert_function(builder.module,
                wdiu__jbcb, sym._literal_value)
            builder.call(vacz__ktdzk, [context.get_constant(types.int64, 0),
                context.get_constant_null(sig.args[1]), context.
                get_constant_null(sig.args[2])])
        else:
            wdiu__jbcb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            vacz__ktdzk = cgutils.get_or_insert_function(builder.module,
                wdiu__jbcb, sym._literal_value)
            builder.call(vacz__ktdzk, [context.get_constant_null(sig.args[0
                ]), context.get_constant_null(sig.args[1]), context.
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
        ovgdq__khh = True
        cdljq__oqrm = 1
        zqqa__kftp = -1
        if isinstance(rhs, ir.Expr):
            for izfz__yssw in rhs.kws:
                if func_name in list_cumulative:
                    if izfz__yssw[0] == 'skipna':
                        ovgdq__khh = guard(find_const, func_ir, izfz__yssw[1])
                        if not isinstance(ovgdq__khh, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if izfz__yssw[0] == 'dropna':
                        ovgdq__khh = guard(find_const, func_ir, izfz__yssw[1])
                        if not isinstance(ovgdq__khh, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            cdljq__oqrm = get_call_expr_arg('shift', rhs.args, dict(rhs.kws
                ), 0, 'periods', cdljq__oqrm)
            cdljq__oqrm = guard(find_const, func_ir, cdljq__oqrm)
        if func_name == 'head':
            zqqa__kftp = get_call_expr_arg('head', rhs.args, dict(rhs.kws),
                0, 'n', 5)
            if not isinstance(zqqa__kftp, int):
                zqqa__kftp = guard(find_const, func_ir, zqqa__kftp)
            if zqqa__kftp < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = ovgdq__khh
        func.periods = cdljq__oqrm
        func.head_n = zqqa__kftp
        if func_name == 'transform':
            kws = dict(rhs.kws)
            iopyr__ntgey = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            gdsr__ctpl = typemap[iopyr__ntgey.name]
            aef__qefr = None
            if isinstance(gdsr__ctpl, str):
                aef__qefr = gdsr__ctpl
            elif is_overload_constant_str(gdsr__ctpl):
                aef__qefr = get_overload_const_str(gdsr__ctpl)
            elif bodo.utils.typing.is_builtin_function(gdsr__ctpl):
                aef__qefr = bodo.utils.typing.get_builtin_function_name(
                    gdsr__ctpl)
            if aef__qefr not in bodo.ir.aggregate.supported_transform_funcs[:]:
                raise BodoError(f'unsupported transform function {aef__qefr}')
            func.transform_func = supported_agg_funcs.index(aef__qefr)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    iopyr__ntgey = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if iopyr__ntgey == '':
        gdsr__ctpl = types.none
    else:
        gdsr__ctpl = typemap[iopyr__ntgey.name]
    if is_overload_constant_dict(gdsr__ctpl):
        ouqqw__sami = get_overload_constant_dict(gdsr__ctpl)
        ufoql__lcp = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in ouqqw__sami.values()]
        return ufoql__lcp
    if gdsr__ctpl == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(gdsr__ctpl, types.BaseTuple):
        ufoql__lcp = []
        nwp__ccbj = 0
        for t in gdsr__ctpl.types:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                ufoql__lcp.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>':
                    func.fname = '<lambda_' + str(nwp__ccbj) + '>'
                    nwp__ccbj += 1
                ufoql__lcp.append(func)
        return [ufoql__lcp]
    if is_overload_constant_str(gdsr__ctpl):
        func_name = get_overload_const_str(gdsr__ctpl)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(gdsr__ctpl):
        func_name = bodo.utils.typing.get_builtin_function_name(gdsr__ctpl)
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
        nwp__ccbj = 0
        haufr__xvhi = []
        for ypcd__wov in f_val:
            func = get_agg_func_udf(func_ir, ypcd__wov, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{nwp__ccbj}>'
                nwp__ccbj += 1
            haufr__xvhi.append(func)
        return haufr__xvhi
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
    aef__qefr = code.co_name
    return aef__qefr


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
            flhe__qijb = types.DType(args[0])
            return signature(flhe__qijb, *args)


@numba.njit(no_cpython_wrapper=True)
def _var_combine(ssqdm_a, mean_a, nobs_a, ssqdm_b, mean_b, nobs_b):
    vlj__hxyz = nobs_a + nobs_b
    izt__lwj = (nobs_a * mean_a + nobs_b * mean_b) / vlj__hxyz
    permk__wnxz = mean_b - mean_a
    xmv__hwt = (ssqdm_a + ssqdm_b + permk__wnxz * permk__wnxz * nobs_a *
        nobs_b / vlj__hxyz)
    return xmv__hwt, izt__lwj, vlj__hxyz


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
        ozz__wvj = ''
        for kam__igp, v in self.df_out_vars.items():
            ozz__wvj += "'{}':{}, ".format(kam__igp, v.name)
        fzti__lls = '{}{{{}}}'.format(self.df_out, ozz__wvj)
        xixx__fhq = ''
        for kam__igp, v in self.df_in_vars.items():
            xixx__fhq += "'{}':{}, ".format(kam__igp, v.name)
        jhc__ymwv = '{}{{{}}}'.format(self.df_in, xixx__fhq)
        slh__ouf = 'pivot {}:{}'.format(self.pivot_arr.name, self.pivot_values
            ) if self.pivot_arr is not None else ''
        key_names = ','.join(self.key_names)
        ixm__anvix = ','.join([v.name for v in self.key_arrs])
        return 'aggregate: {} = {} [key: {}:{}] {}'.format(fzti__lls,
            jhc__ymwv, key_names, ixm__anvix, slh__ouf)

    def remove_out_col(self, out_col_name):
        self.df_out_vars.pop(out_col_name)
        fwit__umjc, ota__krfur = self.gb_info_out.pop(out_col_name)
        if fwit__umjc is None and not self.is_crosstab:
            return
        tdvdv__jcf = self.gb_info_in[fwit__umjc]
        if self.pivot_arr is not None:
            self.pivot_values.remove(out_col_name)
            for i, (func, ozz__wvj) in enumerate(tdvdv__jcf):
                try:
                    ozz__wvj.remove(out_col_name)
                    if len(ozz__wvj) == 0:
                        tdvdv__jcf.pop(i)
                        break
                except ValueError as hzqkm__zhrq:
                    continue
        else:
            for i, (func, ycadl__hnx) in enumerate(tdvdv__jcf):
                if ycadl__hnx == out_col_name:
                    tdvdv__jcf.pop(i)
                    break
        if len(tdvdv__jcf) == 0:
            self.gb_info_in.pop(fwit__umjc)
            self.df_in_vars.pop(fwit__umjc)


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
    qda__uavha = [ghz__nbs for ghz__nbs, xcg__tevuy in aggregate_node.
        df_out_vars.items() if xcg__tevuy.name not in lives]
    for caymq__msbh in qda__uavha:
        aggregate_node.remove_out_col(caymq__msbh)
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
    fdc__oyfed = set(v.name for v in aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        fdc__oyfed.update({v.name for v in aggregate_node.out_key_vars})
    return set(), fdc__oyfed


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for i in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[i] = replace_vars_inner(aggregate_node.
            key_arrs[i], var_dict)
    for ghz__nbs in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[ghz__nbs] = replace_vars_inner(aggregate_node
            .df_in_vars[ghz__nbs], var_dict)
    for ghz__nbs in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[ghz__nbs] = replace_vars_inner(
            aggregate_node.df_out_vars[ghz__nbs], var_dict)
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
    for ghz__nbs in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[ghz__nbs] = visit_vars_inner(aggregate_node
            .df_in_vars[ghz__nbs], callback, cbdata)
    for ghz__nbs in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[ghz__nbs] = visit_vars_inner(aggregate_node
            .df_out_vars[ghz__nbs], callback, cbdata)
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
    fgbe__upw = []
    for qbwk__vcjbp in aggregate_node.key_arrs:
        yvjuo__bydke = equiv_set.get_shape(qbwk__vcjbp)
        if yvjuo__bydke:
            fgbe__upw.append(yvjuo__bydke[0])
    if aggregate_node.pivot_arr is not None:
        yvjuo__bydke = equiv_set.get_shape(aggregate_node.pivot_arr)
        if yvjuo__bydke:
            fgbe__upw.append(yvjuo__bydke[0])
    for xcg__tevuy in aggregate_node.df_in_vars.values():
        yvjuo__bydke = equiv_set.get_shape(xcg__tevuy)
        if yvjuo__bydke:
            fgbe__upw.append(yvjuo__bydke[0])
    if len(fgbe__upw) > 1:
        equiv_set.insert_equiv(*fgbe__upw)
    jzi__hhwzk = []
    fgbe__upw = []
    jvzw__duzsy = list(aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        jvzw__duzsy.extend(aggregate_node.out_key_vars)
    for xcg__tevuy in jvzw__duzsy:
        pbnc__cjymd = typemap[xcg__tevuy.name]
        mbgd__xrfif = array_analysis._gen_shape_call(equiv_set, xcg__tevuy,
            pbnc__cjymd.ndim, None, jzi__hhwzk)
        equiv_set.insert_equiv(xcg__tevuy, mbgd__xrfif)
        fgbe__upw.append(mbgd__xrfif[0])
        equiv_set.define(xcg__tevuy, set())
    if len(fgbe__upw) > 1:
        equiv_set.insert_equiv(*fgbe__upw)
    return [], jzi__hhwzk


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    szl__atc = Distribution.OneD
    for xcg__tevuy in aggregate_node.df_in_vars.values():
        szl__atc = Distribution(min(szl__atc.value, array_dists[xcg__tevuy.
            name].value))
    for qbwk__vcjbp in aggregate_node.key_arrs:
        szl__atc = Distribution(min(szl__atc.value, array_dists[qbwk__vcjbp
            .name].value))
    if aggregate_node.pivot_arr is not None:
        szl__atc = Distribution(min(szl__atc.value, array_dists[
            aggregate_node.pivot_arr.name].value))
        array_dists[aggregate_node.pivot_arr.name] = szl__atc
    for xcg__tevuy in aggregate_node.df_in_vars.values():
        array_dists[xcg__tevuy.name] = szl__atc
    for qbwk__vcjbp in aggregate_node.key_arrs:
        array_dists[qbwk__vcjbp.name] = szl__atc
    cxltn__pombb = Distribution.OneD_Var
    for xcg__tevuy in aggregate_node.df_out_vars.values():
        if xcg__tevuy.name in array_dists:
            cxltn__pombb = Distribution(min(cxltn__pombb.value, array_dists
                [xcg__tevuy.name].value))
    if aggregate_node.out_key_vars is not None:
        for xcg__tevuy in aggregate_node.out_key_vars:
            if xcg__tevuy.name in array_dists:
                cxltn__pombb = Distribution(min(cxltn__pombb.value,
                    array_dists[xcg__tevuy.name].value))
    cxltn__pombb = Distribution(min(cxltn__pombb.value, szl__atc.value))
    for xcg__tevuy in aggregate_node.df_out_vars.values():
        array_dists[xcg__tevuy.name] = cxltn__pombb
    if aggregate_node.out_key_vars is not None:
        for lcz__mhcm in aggregate_node.out_key_vars:
            array_dists[lcz__mhcm.name] = cxltn__pombb
    if cxltn__pombb != Distribution.OneD_Var:
        for qbwk__vcjbp in aggregate_node.key_arrs:
            array_dists[qbwk__vcjbp.name] = cxltn__pombb
        if aggregate_node.pivot_arr is not None:
            array_dists[aggregate_node.pivot_arr.name] = cxltn__pombb
        for xcg__tevuy in aggregate_node.df_in_vars.values():
            array_dists[xcg__tevuy.name] = cxltn__pombb


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for xcg__tevuy in agg_node.df_out_vars.values():
        definitions[xcg__tevuy.name].append(agg_node)
    if agg_node.out_key_vars is not None:
        for lcz__mhcm in agg_node.out_key_vars:
            definitions[lcz__mhcm.name].append(agg_node)
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
    pphx__fte = tuple(typemap[v.name] for v in agg_node.key_arrs)
    elq__fzmpr = [v for btu__fam, v in agg_node.df_in_vars.items()]
    nrfz__qnfa = [v for btu__fam, v in agg_node.df_out_vars.items()]
    in_col_typs = []
    ufoql__lcp = []
    if agg_node.pivot_arr is not None:
        for fwit__umjc, tdvdv__jcf in agg_node.gb_info_in.items():
            for func, ota__krfur in tdvdv__jcf:
                if fwit__umjc is not None:
                    in_col_typs.append(typemap[agg_node.df_in_vars[
                        fwit__umjc].name])
                ufoql__lcp.append(func)
    else:
        for fwit__umjc, func in agg_node.gb_info_out.values():
            if fwit__umjc is not None:
                in_col_typs.append(typemap[agg_node.df_in_vars[fwit__umjc].
                    name])
            ufoql__lcp.append(func)
    out_col_typs = tuple(typemap[v.name] for v in nrfz__qnfa)
    pivot_typ = types.none if agg_node.pivot_arr is None else typemap[agg_node
        .pivot_arr.name]
    arg_typs = tuple(pphx__fte + tuple(typemap[v.name] for v in elq__fzmpr) +
        (pivot_typ,))
    juz__vtcj = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for i, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            juz__vtcj.update({f'in_cat_dtype_{i}': in_col_typ})
    for i, wosn__sumg in enumerate(out_col_typs):
        if isinstance(wosn__sumg, bodo.CategoricalArrayType):
            juz__vtcj.update({f'out_cat_dtype_{i}': wosn__sumg})
    udf_func_struct = get_udf_func_struct(ufoql__lcp, agg_node.
        input_has_index, in_col_typs, out_col_typs, typingctx, targetctx,
        pivot_typ, agg_node.pivot_values, agg_node.is_crosstab)
    kskr__mio = gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
        parallel, udf_func_struct)
    juz__vtcj.update({'pd': pd, 'pre_alloc_string_array':
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
            juz__vtcj.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            juz__vtcj.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    gmowd__kbt = compile_to_numba_ir(kskr__mio, juz__vtcj, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    pafh__jhfv = []
    if agg_node.pivot_arr is None:
        vxrds__fcs = agg_node.key_arrs[0].scope
        loc = agg_node.loc
        gcqpc__ciur = ir.Var(vxrds__fcs, mk_unique_var('dummy_none'), loc)
        typemap[gcqpc__ciur.name] = types.none
        pafh__jhfv.append(ir.Assign(ir.Const(None, loc), gcqpc__ciur, loc))
        elq__fzmpr.append(gcqpc__ciur)
    else:
        elq__fzmpr.append(agg_node.pivot_arr)
    replace_arg_nodes(gmowd__kbt, agg_node.key_arrs + elq__fzmpr)
    sbyrw__eqrgv = gmowd__kbt.body[-3]
    assert is_assign(sbyrw__eqrgv) and isinstance(sbyrw__eqrgv.value, ir.Expr
        ) and sbyrw__eqrgv.value.op == 'build_tuple'
    pafh__jhfv += gmowd__kbt.body[:-3]
    jvzw__duzsy = list(agg_node.df_out_vars.values())
    if agg_node.out_key_vars is not None:
        jvzw__duzsy += agg_node.out_key_vars
    for i, egij__szisw in enumerate(jvzw__duzsy):
        oeu__fwlbr = sbyrw__eqrgv.value.items[i]
        pafh__jhfv.append(ir.Assign(oeu__fwlbr, egij__szisw, egij__szisw.loc))
    return pafh__jhfv


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
        tmzb__zza = args[0]
        if tmzb__zza == types.none:
            return signature(types.boolean, *args)


@lower_builtin(bool, types.none)
def lower_column_mean_impl(context, builder, sig, args):
    qkrg__phwt = context.compile_internal(builder, lambda a: False, sig, args)
    return qkrg__phwt


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
        fzxne__jxkwd = IntDtype(t.dtype).name
        assert fzxne__jxkwd.endswith('Dtype()')
        fzxne__jxkwd = fzxne__jxkwd[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{fzxne__jxkwd}'))"
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
        fmpp__nlnaw = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {fmpp__nlnaw}_cat_dtype_{colnum})'
            )
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
    lwuuj__yrhgc = udf_func_struct.var_typs
    xgsbi__ikmc = len(lwuuj__yrhgc)
    xdyd__fyc = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    xdyd__fyc += '    if is_null_pointer(in_table):\n'
    xdyd__fyc += '        return\n'
    xdyd__fyc += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in lwuuj__yrhgc]),
        ',' if len(lwuuj__yrhgc) == 1 else '')
    aaisp__fkx = n_keys
    qcvh__haaer = []
    redvar_offsets = []
    dbv__vbwa = []
    if do_combine:
        for i, ypcd__wov in enumerate(allfuncs):
            if ypcd__wov.ftype != 'udf':
                aaisp__fkx += ypcd__wov.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(aaisp__fkx, aaisp__fkx +
                    ypcd__wov.n_redvars))
                aaisp__fkx += ypcd__wov.n_redvars
                dbv__vbwa.append(data_in_typs_[func_idx_to_in_col[i]])
                qcvh__haaer.append(func_idx_to_in_col[i] + n_keys)
    else:
        for i, ypcd__wov in enumerate(allfuncs):
            if ypcd__wov.ftype != 'udf':
                aaisp__fkx += ypcd__wov.ncols_post_shuffle
            else:
                redvar_offsets += list(range(aaisp__fkx + 1, aaisp__fkx + 1 +
                    ypcd__wov.n_redvars))
                aaisp__fkx += ypcd__wov.n_redvars + 1
                dbv__vbwa.append(data_in_typs_[func_idx_to_in_col[i]])
                qcvh__haaer.append(func_idx_to_in_col[i] + n_keys)
    assert len(redvar_offsets) == xgsbi__ikmc
    xjwtc__oegwx = len(dbv__vbwa)
    yir__dqwuw = []
    for i, t in enumerate(dbv__vbwa):
        yir__dqwuw.append(_gen_dummy_alloc(t, i, True))
    xdyd__fyc += '    data_in_dummy = ({}{})\n'.format(','.join(yir__dqwuw),
        ',' if len(dbv__vbwa) == 1 else '')
    xdyd__fyc += """
    # initialize redvar cols
"""
    xdyd__fyc += '    init_vals = __init_func()\n'
    for i in range(xgsbi__ikmc):
        xdyd__fyc += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(i, redvar_offsets[i], i))
        xdyd__fyc += '    incref(redvar_arr_{})\n'.format(i)
        xdyd__fyc += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(i, i)
    xdyd__fyc += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(i) for i in range(xgsbi__ikmc)]), ',' if xgsbi__ikmc == 1 else
        '')
    xdyd__fyc += '\n'
    for i in range(xjwtc__oegwx):
        xdyd__fyc += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(i, qcvh__haaer[i], i))
        xdyd__fyc += '    incref(data_in_{})\n'.format(i)
    xdyd__fyc += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(i) for i in range(xjwtc__oegwx)]), ',' if xjwtc__oegwx == 1 else
        '')
    xdyd__fyc += '\n'
    xdyd__fyc += '    for i in range(len(data_in_0)):\n'
    xdyd__fyc += '        w_ind = row_to_group[i]\n'
    xdyd__fyc += '        if w_ind != -1:\n'
    xdyd__fyc += (
        '            __update_redvars(redvars, data_in, w_ind, i, pivot_arr=None)\n'
        )
    zhip__ljtl = {}
    exec(xdyd__fyc, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, zhip__ljtl)
    return zhip__ljtl['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, out_data_typs,
    label_suffix):
    lwuuj__yrhgc = udf_func_struct.var_typs
    xgsbi__ikmc = len(lwuuj__yrhgc)
    xdyd__fyc = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    xdyd__fyc += '    if is_null_pointer(in_table):\n'
    xdyd__fyc += '        return\n'
    xdyd__fyc += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in lwuuj__yrhgc]),
        ',' if len(lwuuj__yrhgc) == 1 else '')
    bgbly__sbi = n_keys
    tafy__jamlk = n_keys
    fgvhw__muoeg = []
    qcff__ytmt = []
    for ypcd__wov in allfuncs:
        if ypcd__wov.ftype != 'udf':
            bgbly__sbi += ypcd__wov.ncols_pre_shuffle
            tafy__jamlk += ypcd__wov.ncols_post_shuffle
        else:
            fgvhw__muoeg += list(range(bgbly__sbi, bgbly__sbi + ypcd__wov.
                n_redvars))
            qcff__ytmt += list(range(tafy__jamlk + 1, tafy__jamlk + 1 +
                ypcd__wov.n_redvars))
            bgbly__sbi += ypcd__wov.n_redvars
            tafy__jamlk += 1 + ypcd__wov.n_redvars
    assert len(fgvhw__muoeg) == xgsbi__ikmc
    xdyd__fyc += """
    # initialize redvar cols
"""
    xdyd__fyc += '    init_vals = __init_func()\n'
    for i in range(xgsbi__ikmc):
        xdyd__fyc += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(i, qcff__ytmt[i], i))
        xdyd__fyc += '    incref(redvar_arr_{})\n'.format(i)
        xdyd__fyc += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(i, i)
    xdyd__fyc += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(i) for i in range(xgsbi__ikmc)]), ',' if xgsbi__ikmc == 1 else
        '')
    xdyd__fyc += '\n'
    for i in range(xgsbi__ikmc):
        xdyd__fyc += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(i, fgvhw__muoeg[i], i))
        xdyd__fyc += '    incref(recv_redvar_arr_{})\n'.format(i)
    xdyd__fyc += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(i) for i in range(xgsbi__ikmc)]), ',' if
        xgsbi__ikmc == 1 else '')
    xdyd__fyc += '\n'
    if xgsbi__ikmc:
        xdyd__fyc += '    for i in range(len(recv_redvar_arr_0)):\n'
        xdyd__fyc += '        w_ind = row_to_group[i]\n'
        xdyd__fyc += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i, pivot_arr=None)\n'
            )
    zhip__ljtl = {}
    exec(xdyd__fyc, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, zhip__ljtl)
    return zhip__ljtl['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    lwuuj__yrhgc = udf_func_struct.var_typs
    xgsbi__ikmc = len(lwuuj__yrhgc)
    aaisp__fkx = n_keys
    redvar_offsets = []
    wnt__qwji = []
    out_data_typs = []
    for i, ypcd__wov in enumerate(allfuncs):
        if ypcd__wov.ftype != 'udf':
            aaisp__fkx += ypcd__wov.ncols_post_shuffle
        else:
            wnt__qwji.append(aaisp__fkx)
            redvar_offsets += list(range(aaisp__fkx + 1, aaisp__fkx + 1 +
                ypcd__wov.n_redvars))
            aaisp__fkx += 1 + ypcd__wov.n_redvars
            out_data_typs.append(out_data_typs_[i])
    assert len(redvar_offsets) == xgsbi__ikmc
    xjwtc__oegwx = len(out_data_typs)
    xdyd__fyc = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    xdyd__fyc += '    if is_null_pointer(table):\n'
    xdyd__fyc += '        return\n'
    xdyd__fyc += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in lwuuj__yrhgc]),
        ',' if len(lwuuj__yrhgc) == 1 else '')
    xdyd__fyc += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        out_data_typs]), ',' if len(out_data_typs) == 1 else '')
    for i in range(xgsbi__ikmc):
        xdyd__fyc += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(i, redvar_offsets[i], i))
        xdyd__fyc += '    incref(redvar_arr_{})\n'.format(i)
    xdyd__fyc += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(i) for i in range(xgsbi__ikmc)]), ',' if xgsbi__ikmc == 1 else
        '')
    xdyd__fyc += '\n'
    for i in range(xjwtc__oegwx):
        xdyd__fyc += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(i, wnt__qwji[i], i))
        xdyd__fyc += '    incref(data_out_{})\n'.format(i)
    xdyd__fyc += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(i) for i in range(xjwtc__oegwx)]), ',' if xjwtc__oegwx == 1 else
        '')
    xdyd__fyc += '\n'
    xdyd__fyc += '    for i in range(len(data_out_0)):\n'
    xdyd__fyc += '        __eval_res(redvars, data_out, i)\n'
    zhip__ljtl = {}
    exec(xdyd__fyc, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, zhip__ljtl)
    return zhip__ljtl['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    aaisp__fkx = n_keys
    gfuxg__twih = []
    for i, ypcd__wov in enumerate(allfuncs):
        if ypcd__wov.ftype == 'gen_udf':
            gfuxg__twih.append(aaisp__fkx)
            aaisp__fkx += 1
        elif ypcd__wov.ftype != 'udf':
            aaisp__fkx += ypcd__wov.ncols_post_shuffle
        else:
            aaisp__fkx += ypcd__wov.n_redvars + 1
    xdyd__fyc = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    xdyd__fyc += '    if num_groups == 0:\n'
    xdyd__fyc += '        return\n'
    for i, func in enumerate(udf_func_struct.general_udf_funcs):
        xdyd__fyc += '    # col {}\n'.format(i)
        xdyd__fyc += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(gfuxg__twih[i], i))
        xdyd__fyc += '    incref(out_col)\n'
        xdyd__fyc += '    for j in range(num_groups):\n'
        xdyd__fyc += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(i, i))
        xdyd__fyc += '        incref(in_col)\n'
        xdyd__fyc += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(i))
    juz__vtcj = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    jyqa__tirgu = 0
    for i, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[jyqa__tirgu]
        juz__vtcj['func_{}'.format(jyqa__tirgu)] = func
        juz__vtcj['in_col_{}_typ'.format(jyqa__tirgu)] = in_col_typs[
            func_idx_to_in_col[i]]
        juz__vtcj['out_col_{}_typ'.format(jyqa__tirgu)] = out_col_typs[i]
        jyqa__tirgu += 1
    zhip__ljtl = {}
    exec(xdyd__fyc, juz__vtcj, zhip__ljtl)
    ypcd__wov = zhip__ljtl['bodo_gb_apply_general_udfs{}'.format(label_suffix)]
    axv__pslzi = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(axv__pslzi, nopython=True)(ypcd__wov)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs, parallel,
    udf_func_struct):
    cwylc__lnbah = agg_node.pivot_arr is not None
    if agg_node.same_index:
        assert agg_node.input_has_index
    if agg_node.pivot_values is None:
        kjed__tgr = 1
    else:
        kjed__tgr = len(agg_node.pivot_values)
    zkk__qeywv = tuple('key_' + sanitize_varname(kam__igp) for kam__igp in
        agg_node.key_names)
    siasa__sva = {kam__igp: 'in_{}'.format(sanitize_varname(kam__igp)) for
        kam__igp in agg_node.gb_info_in.keys() if kam__igp is not None}
    vxiw__lsk = {kam__igp: ('out_' + sanitize_varname(kam__igp)) for
        kam__igp in agg_node.gb_info_out.keys()}
    n_keys = len(agg_node.key_names)
    cwids__yddg = ', '.join(zkk__qeywv)
    xwf__xnwin = ', '.join(siasa__sva.values())
    if xwf__xnwin != '':
        xwf__xnwin = ', ' + xwf__xnwin
    xdyd__fyc = 'def agg_top({}{}{}, pivot_arr):\n'.format(cwids__yddg,
        xwf__xnwin, ', index_arg' if agg_node.input_has_index else '')
    if cwylc__lnbah:
        sgto__pjvef = []
        for fwit__umjc, tdvdv__jcf in agg_node.gb_info_in.items():
            if fwit__umjc is not None:
                for func, ota__krfur in tdvdv__jcf:
                    sgto__pjvef.append(siasa__sva[fwit__umjc])
    else:
        sgto__pjvef = tuple(siasa__sva[fwit__umjc] for fwit__umjc,
            ota__krfur in agg_node.gb_info_out.values() if fwit__umjc is not
            None)
    jpkul__mulc = zkk__qeywv + tuple(sgto__pjvef)
    xdyd__fyc += '    info_list = [{}{}{}]\n'.format(', '.join(
        'array_to_info({})'.format(a) for a in jpkul__mulc), 
        ', array_to_info(index_arg)' if agg_node.input_has_index else '', 
        ', array_to_info(pivot_arr)' if agg_node.is_crosstab else '')
    xdyd__fyc += '    table = arr_info_list_to_table(info_list)\n'
    for i, kam__igp in enumerate(agg_node.gb_info_out.keys()):
        hyrxc__cgx = vxiw__lsk[kam__igp] + '_dummy'
        wosn__sumg = out_col_typs[i]
        fwit__umjc, func = agg_node.gb_info_out[kam__igp]
        if isinstance(func, pytypes.SimpleNamespace) and func.fname in ['min',
            'max', 'shift'] and isinstance(wosn__sumg, bodo.
            CategoricalArrayType):
            xdyd__fyc += '    {} = {}\n'.format(hyrxc__cgx, siasa__sva[
                fwit__umjc])
        else:
            xdyd__fyc += '    {} = {}\n'.format(hyrxc__cgx,
                _gen_dummy_alloc(wosn__sumg, i, False))
    do_combine = parallel
    allfuncs = []
    cezl__komd = []
    func_idx_to_in_col = []
    lus__votcz = []
    ovgdq__khh = False
    lmi__jopf = 1
    zqqa__kftp = -1
    vbi__irfw = 0
    ero__znqdn = 0
    if not cwylc__lnbah:
        ufoql__lcp = [func for ota__krfur, func in agg_node.gb_info_out.
            values()]
    else:
        ufoql__lcp = [func for func, ota__krfur in tdvdv__jcf for
            tdvdv__jcf in agg_node.gb_info_in.values()]
    for rjrbh__tjozo, func in enumerate(ufoql__lcp):
        cezl__komd.append(len(allfuncs))
        if func.ftype in {'median', 'nunique'}:
            do_combine = False
        if func.ftype in list_cumulative:
            vbi__irfw += 1
        if hasattr(func, 'skipdropna'):
            ovgdq__khh = func.skipdropna
        if func.ftype == 'shift':
            lmi__jopf = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            ero__znqdn = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            zqqa__kftp = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(rjrbh__tjozo)
        if func.ftype == 'udf':
            lus__votcz.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            lus__votcz.append(0)
            do_combine = False
    cezl__komd.append(len(allfuncs))
    if agg_node.is_crosstab:
        assert len(agg_node.gb_info_out
            ) == kjed__tgr, 'invalid number of groupby outputs for pivot'
    else:
        assert len(agg_node.gb_info_out) == len(allfuncs
            ) * kjed__tgr, 'invalid number of groupby outputs'
    if vbi__irfw > 0:
        if vbi__irfw != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    if udf_func_struct is not None:
        klgd__ukgvo = next_label()
        if udf_func_struct.regular_udfs:
            axv__pslzi = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            wrrf__itjae = numba.cfunc(axv__pslzi, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs,
                out_col_typs, do_combine, func_idx_to_in_col, klgd__ukgvo))
            ilkeo__tdd = numba.cfunc(axv__pslzi, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, out_col_typs, klgd__ukgvo))
            bqps__ffjn = numba.cfunc('void(voidptr)', nopython=True)(
                gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_col_typs,
                klgd__ukgvo))
            udf_func_struct.set_regular_cfuncs(wrrf__itjae, ilkeo__tdd,
                bqps__ffjn)
            for bxh__xga in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[bxh__xga.native_name] = bxh__xga
                gb_agg_cfunc_addr[bxh__xga.native_name] = bxh__xga.address
        if udf_func_struct.general_udfs:
            wvyev__whp = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, out_col_typs, func_idx_to_in_col,
                klgd__ukgvo)
            udf_func_struct.set_general_cfunc(wvyev__whp)
        hevbx__mvpd = []
        dspn__fdlu = 0
        i = 0
        for hyrxc__cgx, ypcd__wov in zip(vxiw__lsk.values(), allfuncs):
            if ypcd__wov.ftype in ('udf', 'gen_udf'):
                hevbx__mvpd.append(hyrxc__cgx + '_dummy')
                for uiaqp__iqldj in range(dspn__fdlu, dspn__fdlu +
                    lus__votcz[i]):
                    hevbx__mvpd.append('data_redvar_dummy_' + str(uiaqp__iqldj)
                        )
                dspn__fdlu += lus__votcz[i]
                i += 1
        if udf_func_struct.regular_udfs:
            lwuuj__yrhgc = udf_func_struct.var_typs
            for i, t in enumerate(lwuuj__yrhgc):
                xdyd__fyc += ('    data_redvar_dummy_{} = np.empty(1, {})\n'
                    .format(i, _get_np_dtype(t)))
        xdyd__fyc += '    out_info_list_dummy = [{}]\n'.format(', '.join(
            'array_to_info({})'.format(a) for a in hevbx__mvpd))
        xdyd__fyc += (
            '    udf_table_dummy = arr_info_list_to_table(out_info_list_dummy)\n'
            )
        if udf_func_struct.regular_udfs:
            xdyd__fyc += "    add_agg_cfunc_sym(cpp_cb_update, '{}')\n".format(
                wrrf__itjae.native_name)
            xdyd__fyc += ("    add_agg_cfunc_sym(cpp_cb_combine, '{}')\n".
                format(ilkeo__tdd.native_name))
            xdyd__fyc += "    add_agg_cfunc_sym(cpp_cb_eval, '{}')\n".format(
                bqps__ffjn.native_name)
            xdyd__fyc += ("    cpp_cb_update_addr = get_agg_udf_addr('{}')\n"
                .format(wrrf__itjae.native_name))
            xdyd__fyc += ("    cpp_cb_combine_addr = get_agg_udf_addr('{}')\n"
                .format(ilkeo__tdd.native_name))
            xdyd__fyc += ("    cpp_cb_eval_addr = get_agg_udf_addr('{}')\n"
                .format(bqps__ffjn.native_name))
        else:
            xdyd__fyc += '    cpp_cb_update_addr = 0\n'
            xdyd__fyc += '    cpp_cb_combine_addr = 0\n'
            xdyd__fyc += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            bxh__xga = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[bxh__xga.native_name] = bxh__xga
            gb_agg_cfunc_addr[bxh__xga.native_name] = bxh__xga.address
            xdyd__fyc += ("    add_agg_cfunc_sym(cpp_cb_general, '{}')\n".
                format(bxh__xga.native_name))
            xdyd__fyc += ("    cpp_cb_general_addr = get_agg_udf_addr('{}')\n"
                .format(bxh__xga.native_name))
        else:
            xdyd__fyc += '    cpp_cb_general_addr = 0\n'
    else:
        xdyd__fyc += (
            '    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])\n'
            )
        xdyd__fyc += '    cpp_cb_update_addr = 0\n'
        xdyd__fyc += '    cpp_cb_combine_addr = 0\n'
        xdyd__fyc += '    cpp_cb_eval_addr = 0\n'
        xdyd__fyc += '    cpp_cb_general_addr = 0\n'
    xdyd__fyc += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(', '
        .join([str(supported_agg_funcs.index(ypcd__wov.ftype)) for
        ypcd__wov in allfuncs] + ['0']))
    xdyd__fyc += '    func_offsets = np.array({}, dtype=np.int32)\n'.format(str
        (cezl__komd))
    if len(lus__votcz) > 0:
        xdyd__fyc += '    udf_ncols = np.array({}, dtype=np.int32)\n'.format(
            str(lus__votcz))
    else:
        xdyd__fyc += '    udf_ncols = np.array([0], np.int32)\n'
    if cwylc__lnbah:
        xdyd__fyc += '    arr_type = coerce_to_array({})\n'.format(agg_node
            .pivot_values)
        xdyd__fyc += '    arr_info = array_to_info(arr_type)\n'
        xdyd__fyc += (
            '    dispatch_table = arr_info_list_to_table([arr_info])\n')
        xdyd__fyc += '    pivot_info = array_to_info(pivot_arr)\n'
        xdyd__fyc += (
            '    dispatch_info = arr_info_list_to_table([pivot_info])\n')
        xdyd__fyc += (
            """    out_table = pivot_groupby_and_aggregate(table, {}, dispatch_table, dispatch_info, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, agg_node.
            is_crosstab, ovgdq__khh, agg_node.return_key, agg_node.same_index))
        xdyd__fyc += '    delete_info_decref_array(pivot_info)\n'
        xdyd__fyc += '    delete_info_decref_array(arr_info)\n'
    else:
        xdyd__fyc += (
            """    out_table = groupby_and_aggregate(table, {}, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, ovgdq__khh,
            lmi__jopf, ero__znqdn, zqqa__kftp, agg_node.return_key,
            agg_node.same_index, agg_node.dropna))
    bnbg__rbvxw = 0
    if agg_node.return_key:
        for i, jre__lgse in enumerate(zkk__qeywv):
            xdyd__fyc += (
                '    {} = info_to_array(info_from_table(out_table, {}), {})\n'
                .format(jre__lgse, bnbg__rbvxw, jre__lgse))
            bnbg__rbvxw += 1
    for hyrxc__cgx in vxiw__lsk.values():
        xdyd__fyc += (
            '    {} = info_to_array(info_from_table(out_table, {}), {})\n'.
            format(hyrxc__cgx, bnbg__rbvxw, hyrxc__cgx + '_dummy'))
        bnbg__rbvxw += 1
    if agg_node.same_index:
        xdyd__fyc += (
            """    out_index_arg = info_to_array(info_from_table(out_table, {}), index_arg)
"""
            .format(bnbg__rbvxw))
        bnbg__rbvxw += 1
    xdyd__fyc += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    xdyd__fyc += '    delete_table_decref_arrays(table)\n'
    xdyd__fyc += '    delete_table_decref_arrays(udf_table_dummy)\n'
    xdyd__fyc += '    delete_table(out_table)\n'
    xdyd__fyc += f'    ev_clean.finalize()\n'
    lhsi__ebhk = tuple(vxiw__lsk.values())
    if agg_node.return_key:
        lhsi__ebhk += tuple(zkk__qeywv)
    xdyd__fyc += '    return ({},{})\n'.format(', '.join(lhsi__ebhk), 
        ' out_index_arg,' if agg_node.same_index else '')
    zhip__ljtl = {}
    exec(xdyd__fyc, {}, zhip__ljtl)
    uofcz__swyy = zhip__ljtl['agg_top']
    return uofcz__swyy


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for hjxtv__lwkc in block.body:
            if is_call_assign(hjxtv__lwkc) and find_callname(f_ir,
                hjxtv__lwkc.value) == ('len', 'builtins'
                ) and hjxtv__lwkc.value.args[0].name == f_ir.arg_names[0]:
                gsg__fly = get_definition(f_ir, hjxtv__lwkc.value.func)
                gsg__fly.name = 'dummy_agg_count'
                gsg__fly.value = dummy_agg_count
    jrxn__paqon = get_name_var_table(f_ir.blocks)
    sffy__eqbpz = {}
    for name, ota__krfur in jrxn__paqon.items():
        sffy__eqbpz[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, sffy__eqbpz)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    yyzz__pdbox = numba.core.compiler.Flags()
    yyzz__pdbox.nrt = True
    jurxw__qndc = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, yyzz__pdbox)
    jurxw__qndc.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, wyavh__lbx, calltypes, ota__krfur = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    nuk__zys = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    jezy__jajj = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    lukfk__gjiw = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    friat__elb = lukfk__gjiw(typemap, calltypes)
    pm = jezy__jajj(typingctx, targetctx, None, f_ir, typemap, wyavh__lbx,
        calltypes, friat__elb, {}, yyzz__pdbox, None)
    lri__ouhc = numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline(
        pm)
    pm = jezy__jajj(typingctx, targetctx, None, f_ir, typemap, wyavh__lbx,
        calltypes, friat__elb, {}, yyzz__pdbox, lri__ouhc)
    gbji__sqin = numba.core.typed_passes.InlineOverloads()
    gbji__sqin.run_pass(pm)
    ptjvs__bpq = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    ptjvs__bpq.run()
    for block in f_ir.blocks.values():
        for hjxtv__lwkc in block.body:
            if is_assign(hjxtv__lwkc) and isinstance(hjxtv__lwkc.value, (ir
                .Arg, ir.Var)) and isinstance(typemap[hjxtv__lwkc.target.
                name], SeriesType):
                pbnc__cjymd = typemap.pop(hjxtv__lwkc.target.name)
                typemap[hjxtv__lwkc.target.name] = pbnc__cjymd.data
            if is_call_assign(hjxtv__lwkc) and find_callname(f_ir,
                hjxtv__lwkc.value) == ('get_series_data',
                'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[hjxtv__lwkc.target.name].remove(hjxtv__lwkc
                    .value)
                hjxtv__lwkc.value = hjxtv__lwkc.value.args[0]
                f_ir._definitions[hjxtv__lwkc.target.name].append(hjxtv__lwkc
                    .value)
            if is_call_assign(hjxtv__lwkc) and find_callname(f_ir,
                hjxtv__lwkc.value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[hjxtv__lwkc.target.name].remove(hjxtv__lwkc
                    .value)
                hjxtv__lwkc.value = ir.Const(False, hjxtv__lwkc.loc)
                f_ir._definitions[hjxtv__lwkc.target.name].append(hjxtv__lwkc
                    .value)
            if is_call_assign(hjxtv__lwkc) and find_callname(f_ir,
                hjxtv__lwkc.value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[hjxtv__lwkc.target.name].remove(hjxtv__lwkc
                    .value)
                hjxtv__lwkc.value = ir.Const(False, hjxtv__lwkc.loc)
                f_ir._definitions[hjxtv__lwkc.target.name].append(hjxtv__lwkc
                    .value)
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    gfx__nji = numba.parfors.parfor.PreParforPass(f_ir, typemap, calltypes,
        typingctx, targetctx, nuk__zys)
    gfx__nji.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    cey__qiv = numba.core.compiler.StateDict()
    cey__qiv.func_ir = f_ir
    cey__qiv.typemap = typemap
    cey__qiv.calltypes = calltypes
    cey__qiv.typingctx = typingctx
    cey__qiv.targetctx = targetctx
    cey__qiv.return_type = wyavh__lbx
    numba.core.rewrites.rewrite_registry.apply('after-inference', cey__qiv)
    spb__ead = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        wyavh__lbx, typingctx, targetctx, nuk__zys, yyzz__pdbox, {})
    spb__ead.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            tmu__gvm = ctypes.pythonapi.PyCell_Get
            tmu__gvm.restype = ctypes.py_object
            tmu__gvm.argtypes = ctypes.py_object,
            ouqqw__sami = tuple(tmu__gvm(zvtql__lzr) for zvtql__lzr in closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            ouqqw__sami = closure.items
        assert len(code.co_freevars) == len(ouqqw__sami)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks,
            ouqqw__sami)


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
        ulf__ifq = SeriesType(in_col_typ.dtype, in_col_typ, None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (ulf__ifq,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        pwuqs__tsv, arr_var = _rm_arg_agg_block(block, pm.typemap)
        mmgl__ioofu = -1
        for i, hjxtv__lwkc in enumerate(pwuqs__tsv):
            if isinstance(hjxtv__lwkc, numba.parfors.parfor.Parfor):
                assert mmgl__ioofu == -1, 'only one parfor for aggregation function'
                mmgl__ioofu = i
        parfor = None
        if mmgl__ioofu != -1:
            parfor = pwuqs__tsv[mmgl__ioofu]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = pwuqs__tsv[:mmgl__ioofu] + parfor.init_block.body
        eval_nodes = pwuqs__tsv[mmgl__ioofu + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for hjxtv__lwkc in init_nodes:
            if is_assign(hjxtv__lwkc) and hjxtv__lwkc.target.name in redvars:
                ind = redvars.index(hjxtv__lwkc.target.name)
                reduce_vars[ind] = hjxtv__lwkc.target
        var_types = [pm.typemap[v] for v in redvars]
        vlyf__mfy = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        itdh__vxnmu = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        wkchk__esdmj = gen_eval_func(f_ir, eval_nodes, reduce_vars,
            var_types, pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(wkchk__esdmj)
        self.all_update_funcs.append(itdh__vxnmu)
        self.all_combine_funcs.append(vlyf__mfy)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        self.all_vartypes = self.all_vartypes * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_vartypes
        self.all_reduce_vars = self.all_reduce_vars * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_reduce_vars
        iwcwp__huai = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        tgma__aqtx = gen_all_update_func(self.all_update_funcs, self.
            all_vartypes, self.in_col_types, self.redvar_offsets, self.
            typingctx, self.targetctx, self.pivot_typ, self.pivot_values,
            self.is_crosstab)
        qezqi__mojg = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.
            targetctx, self.pivot_typ, self.pivot_values)
        ykkl__yrwa = gen_all_eval_func(self.all_eval_funcs, self.
            all_vartypes, self.redvar_offsets, self.out_col_types, self.
            typingctx, self.targetctx, self.pivot_values)
        return (self.all_vartypes, iwcwp__huai, tgma__aqtx, qezqi__mojg,
            ykkl__yrwa)


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
    psbo__yrrw = []
    for t, ypcd__wov in zip(in_col_types, agg_func):
        psbo__yrrw.append((t, ypcd__wov))
    qosfb__vulde = RegularUDFGenerator(in_col_types, out_col_types,
        pivot_typ, pivot_values, is_crosstab, typingctx, targetctx)
    tzha__bbhnl = GeneralUDFGenerator()
    for in_col_typ, func in psbo__yrrw:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            qosfb__vulde.add_udf(in_col_typ, func)
        except:
            tzha__bbhnl.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = qosfb__vulde.gen_all_func()
    general_udf_funcs = tzha__bbhnl.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    apfn__zhkap = compute_use_defs(parfor.loop_body)
    kyydw__iwfzg = set()
    for ozg__onuxr in apfn__zhkap.usemap.values():
        kyydw__iwfzg |= ozg__onuxr
    jip__gaixc = set()
    for ozg__onuxr in apfn__zhkap.defmap.values():
        jip__gaixc |= ozg__onuxr
    ueym__lry = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    ueym__lry.body = eval_nodes
    hjvxx__txumy = compute_use_defs({(0): ueym__lry})
    ejt__sjpn = hjvxx__txumy.usemap[0]
    rnxp__xirm = set()
    ybyso__qlfl = []
    mkur__jrffg = []
    for hjxtv__lwkc in reversed(init_nodes):
        ctc__npem = {v.name for v in hjxtv__lwkc.list_vars()}
        if is_assign(hjxtv__lwkc):
            v = hjxtv__lwkc.target.name
            ctc__npem.remove(v)
            if (v in kyydw__iwfzg and v not in rnxp__xirm and v not in
                ejt__sjpn and v not in jip__gaixc):
                mkur__jrffg.append(hjxtv__lwkc)
                kyydw__iwfzg |= ctc__npem
                jip__gaixc.add(v)
                continue
        rnxp__xirm |= ctc__npem
        ybyso__qlfl.append(hjxtv__lwkc)
    mkur__jrffg.reverse()
    ybyso__qlfl.reverse()
    xcfbl__lokkv = min(parfor.loop_body.keys())
    xlsd__cnqy = parfor.loop_body[xcfbl__lokkv]
    xlsd__cnqy.body = mkur__jrffg + xlsd__cnqy.body
    return ybyso__qlfl


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    pkwey__mkolw = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    svka__jsanu = set()
    wvlp__ryxk = []
    for hjxtv__lwkc in init_nodes:
        if is_assign(hjxtv__lwkc) and isinstance(hjxtv__lwkc.value, ir.Global
            ) and isinstance(hjxtv__lwkc.value.value, pytypes.FunctionType
            ) and hjxtv__lwkc.value.value in pkwey__mkolw:
            svka__jsanu.add(hjxtv__lwkc.target.name)
        elif is_call_assign(hjxtv__lwkc
            ) and hjxtv__lwkc.value.func.name in svka__jsanu:
            pass
        else:
            wvlp__ryxk.append(hjxtv__lwkc)
    init_nodes = wvlp__ryxk
    qco__ddd = types.Tuple(var_types)
    tcn__efjm = lambda : None
    f_ir = compile_to_numba_ir(tcn__efjm, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    ohern__lsnwf = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    uslgb__dsbh = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc),
        ohern__lsnwf, loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [uslgb__dsbh] + block.body
    block.body[-2].value.value = ohern__lsnwf
    odk__hpp = compiler.compile_ir(typingctx, targetctx, f_ir, (), qco__ddd,
        compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rbhi__zkmkb = numba.core.target_extension.dispatcher_registry[cpu_target](
        tcn__efjm)
    rbhi__zkmkb.add_overload(odk__hpp)
    return rbhi__zkmkb


def gen_all_update_func(update_funcs, reduce_var_types, in_col_types,
    redvar_offsets, typingctx, targetctx, pivot_typ, pivot_values, is_crosstab
    ):
    lwkf__hul = len(update_funcs)
    qpm__nrb = len(in_col_types)
    if pivot_values is not None:
        assert qpm__nrb == 1
    xdyd__fyc = (
        'def update_all_f(redvar_arrs, data_in, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        mqod__vfhxx = redvar_offsets[qpm__nrb]
        xdyd__fyc += '  pv = pivot_arr[i]\n'
        for uiaqp__iqldj, trsg__skow in enumerate(pivot_values):
            lsybx__uxqol = 'el' if uiaqp__iqldj != 0 else ''
            xdyd__fyc += "  {}if pv == '{}':\n".format(lsybx__uxqol, trsg__skow
                )
            yqfa__mcr = mqod__vfhxx * uiaqp__iqldj
            isvy__bav = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for i in
                range(yqfa__mcr + redvar_offsets[0], yqfa__mcr +
                redvar_offsets[1])])
            xzl__kidcw = 'data_in[0][i]'
            if is_crosstab:
                xzl__kidcw = '0'
            xdyd__fyc += '    {} = update_vars_0({}, {})\n'.format(isvy__bav,
                isvy__bav, xzl__kidcw)
    else:
        for uiaqp__iqldj in range(lwkf__hul):
            isvy__bav = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for i in
                range(redvar_offsets[uiaqp__iqldj], redvar_offsets[
                uiaqp__iqldj + 1])])
            if isvy__bav:
                xdyd__fyc += ('  {} = update_vars_{}({},  data_in[{}][i])\n'
                    .format(isvy__bav, uiaqp__iqldj, isvy__bav, 0 if 
                    qpm__nrb == 1 else uiaqp__iqldj))
    xdyd__fyc += '  return\n'
    juz__vtcj = {}
    for i, ypcd__wov in enumerate(update_funcs):
        juz__vtcj['update_vars_{}'.format(i)] = ypcd__wov
    zhip__ljtl = {}
    exec(xdyd__fyc, juz__vtcj, zhip__ljtl)
    dyx__cldcj = zhip__ljtl['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(dyx__cldcj)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx, pivot_typ, pivot_values):
    lqegt__sac = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types]
        )
    arg_typs = lqegt__sac, lqegt__sac, types.intp, types.intp, pivot_typ
    oxo__ipyeu = len(redvar_offsets) - 1
    mqod__vfhxx = redvar_offsets[oxo__ipyeu]
    xdyd__fyc = (
        'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        assert oxo__ipyeu == 1
        for jwhqt__zzepm in range(len(pivot_values)):
            yqfa__mcr = mqod__vfhxx * jwhqt__zzepm
            isvy__bav = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for i in
                range(yqfa__mcr + redvar_offsets[0], yqfa__mcr +
                redvar_offsets[1])])
            trhe__dnwm = ', '.join(['recv_arrs[{}][i]'.format(i) for i in
                range(yqfa__mcr + redvar_offsets[0], yqfa__mcr +
                redvar_offsets[1])])
            xdyd__fyc += '  {} = combine_vars_0({}, {})\n'.format(isvy__bav,
                isvy__bav, trhe__dnwm)
    else:
        for uiaqp__iqldj in range(oxo__ipyeu):
            isvy__bav = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for i in
                range(redvar_offsets[uiaqp__iqldj], redvar_offsets[
                uiaqp__iqldj + 1])])
            trhe__dnwm = ', '.join(['recv_arrs[{}][i]'.format(i) for i in
                range(redvar_offsets[uiaqp__iqldj], redvar_offsets[
                uiaqp__iqldj + 1])])
            if trhe__dnwm:
                xdyd__fyc += '  {} = combine_vars_{}({}, {})\n'.format(
                    isvy__bav, uiaqp__iqldj, isvy__bav, trhe__dnwm)
    xdyd__fyc += '  return\n'
    juz__vtcj = {}
    for i, ypcd__wov in enumerate(combine_funcs):
        juz__vtcj['combine_vars_{}'.format(i)] = ypcd__wov
    zhip__ljtl = {}
    exec(xdyd__fyc, juz__vtcj, zhip__ljtl)
    gqrv__yjkym = zhip__ljtl['combine_all_f']
    f_ir = compile_to_numba_ir(gqrv__yjkym, juz__vtcj)
    qezqi__mojg = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rbhi__zkmkb = numba.core.target_extension.dispatcher_registry[cpu_target](
        gqrv__yjkym)
    rbhi__zkmkb.add_overload(qezqi__mojg)
    return rbhi__zkmkb


def gen_all_eval_func(eval_funcs, reduce_var_types, redvar_offsets,
    out_col_typs, typingctx, targetctx, pivot_values):
    lqegt__sac = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types]
        )
    out_col_typs = types.Tuple(out_col_typs)
    oxo__ipyeu = len(redvar_offsets) - 1
    mqod__vfhxx = redvar_offsets[oxo__ipyeu]
    xdyd__fyc = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    if pivot_values is not None:
        assert oxo__ipyeu == 1
        for uiaqp__iqldj in range(len(pivot_values)):
            yqfa__mcr = mqod__vfhxx * uiaqp__iqldj
            isvy__bav = ', '.join(['redvar_arrs[{}][j]'.format(i) for i in
                range(yqfa__mcr + redvar_offsets[0], yqfa__mcr +
                redvar_offsets[1])])
            xdyd__fyc += '  out_arrs[{}][j] = eval_vars_0({})\n'.format(
                uiaqp__iqldj, isvy__bav)
    else:
        for uiaqp__iqldj in range(oxo__ipyeu):
            isvy__bav = ', '.join(['redvar_arrs[{}][j]'.format(i) for i in
                range(redvar_offsets[uiaqp__iqldj], redvar_offsets[
                uiaqp__iqldj + 1])])
            xdyd__fyc += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
                uiaqp__iqldj, uiaqp__iqldj, isvy__bav)
    xdyd__fyc += '  return\n'
    juz__vtcj = {}
    for i, ypcd__wov in enumerate(eval_funcs):
        juz__vtcj['eval_vars_{}'.format(i)] = ypcd__wov
    zhip__ljtl = {}
    exec(xdyd__fyc, juz__vtcj, zhip__ljtl)
    gdm__daxw = zhip__ljtl['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(gdm__daxw)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    qxi__fvj = len(var_types)
    etb__dakb = [f'in{i}' for i in range(qxi__fvj)]
    qco__ddd = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    dztnx__ptvy = qco__ddd(0)
    xdyd__fyc = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        etb__dakb))
    zhip__ljtl = {}
    exec(xdyd__fyc, {'_zero': dztnx__ptvy}, zhip__ljtl)
    nxq__ajec = zhip__ljtl['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(nxq__ajec, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': dztnx__ptvy}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    dfum__rcpi = []
    for i, v in enumerate(reduce_vars):
        dfum__rcpi.append(ir.Assign(block.body[i].target, v, v.loc))
        for vre__hrcv in v.versioned_names:
            dfum__rcpi.append(ir.Assign(v, ir.Var(v.scope, vre__hrcv, v.loc
                ), v.loc))
    block.body = block.body[:qxi__fvj] + dfum__rcpi + eval_nodes
    wkchk__esdmj = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        qco__ddd, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rbhi__zkmkb = numba.core.target_extension.dispatcher_registry[cpu_target](
        nxq__ajec)
    rbhi__zkmkb.add_overload(wkchk__esdmj)
    return rbhi__zkmkb


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    qxi__fvj = len(redvars)
    vio__cugv = [f'v{i}' for i in range(qxi__fvj)]
    etb__dakb = [f'in{i}' for i in range(qxi__fvj)]
    xdyd__fyc = 'def agg_combine({}):\n'.format(', '.join(vio__cugv +
        etb__dakb))
    jlkfz__ncp = wrap_parfor_blocks(parfor)
    zdv__gyl = find_topo_order(jlkfz__ncp)
    zdv__gyl = zdv__gyl[1:]
    unwrap_parfor_blocks(parfor)
    qpslo__rjfan = {}
    rjsfa__xuiy = []
    for kzus__tmtcp in zdv__gyl:
        oxo__ikp = parfor.loop_body[kzus__tmtcp]
        for hjxtv__lwkc in oxo__ikp.body:
            if is_call_assign(hjxtv__lwkc) and guard(find_callname, f_ir,
                hjxtv__lwkc.value) == ('__special_combine', 'bodo.ir.aggregate'
                ):
                args = hjxtv__lwkc.value.args
                kmy__odnza = []
                tjsk__vwte = []
                for v in args[:-1]:
                    ind = redvars.index(v.name)
                    rjsfa__xuiy.append(ind)
                    kmy__odnza.append('v{}'.format(ind))
                    tjsk__vwte.append('in{}'.format(ind))
                lxz__yaixn = '__special_combine__{}'.format(len(qpslo__rjfan))
                xdyd__fyc += '    ({},) = {}({})\n'.format(', '.join(
                    kmy__odnza), lxz__yaixn, ', '.join(kmy__odnza + tjsk__vwte)
                    )
                ixc__tasfe = ir.Expr.call(args[-1], [], (), oxo__ikp.loc)
                oay__ytonq = guard(find_callname, f_ir, ixc__tasfe)
                assert oay__ytonq == ('_var_combine', 'bodo.ir.aggregate')
                oay__ytonq = bodo.ir.aggregate._var_combine
                qpslo__rjfan[lxz__yaixn] = oay__ytonq
            if is_assign(hjxtv__lwkc) and hjxtv__lwkc.target.name in redvars:
                smvdj__wnmf = hjxtv__lwkc.target.name
                ind = redvars.index(smvdj__wnmf)
                if ind in rjsfa__xuiy:
                    continue
                if len(f_ir._definitions[smvdj__wnmf]) == 2:
                    var_def = f_ir._definitions[smvdj__wnmf][0]
                    xdyd__fyc += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[smvdj__wnmf][1]
                    xdyd__fyc += _match_reduce_def(var_def, f_ir, ind)
    xdyd__fyc += '    return {}'.format(', '.join(['v{}'.format(i) for i in
        range(qxi__fvj)]))
    zhip__ljtl = {}
    exec(xdyd__fyc, {}, zhip__ljtl)
    iim__dnie = zhip__ljtl['agg_combine']
    arg_typs = tuple(2 * var_types)
    juz__vtcj = {'numba': numba, 'bodo': bodo, 'np': np}
    juz__vtcj.update(qpslo__rjfan)
    f_ir = compile_to_numba_ir(iim__dnie, juz__vtcj, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    qco__ddd = pm.typemap[block.body[-1].value.name]
    vlyf__mfy = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        qco__ddd, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rbhi__zkmkb = numba.core.target_extension.dispatcher_registry[cpu_target](
        iim__dnie)
    rbhi__zkmkb.add_overload(vlyf__mfy)
    return rbhi__zkmkb


def _match_reduce_def(var_def, f_ir, ind):
    xdyd__fyc = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        xdyd__fyc = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        zknec__ahij = guard(find_callname, f_ir, var_def)
        if zknec__ahij == ('min', 'builtins'):
            xdyd__fyc = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if zknec__ahij == ('max', 'builtins'):
            xdyd__fyc = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return xdyd__fyc


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    qxi__fvj = len(redvars)
    fqte__vqodh = 1
    uino__ypsrl = []
    for i in range(fqte__vqodh):
        aeoli__etib = ir.Var(arr_var.scope, f'$input{i}', arr_var.loc)
        uino__ypsrl.append(aeoli__etib)
    jcys__aewgj = parfor.loop_nests[0].index_variable
    soy__ogr = [0] * qxi__fvj
    for oxo__ikp in parfor.loop_body.values():
        igw__dukmv = []
        for hjxtv__lwkc in oxo__ikp.body:
            if is_var_assign(hjxtv__lwkc
                ) and hjxtv__lwkc.value.name == jcys__aewgj.name:
                continue
            if is_getitem(hjxtv__lwkc
                ) and hjxtv__lwkc.value.value.name == arr_var.name:
                hjxtv__lwkc.value = uino__ypsrl[0]
            if is_call_assign(hjxtv__lwkc) and guard(find_callname, pm.
                func_ir, hjxtv__lwkc.value) == ('isna',
                'bodo.libs.array_kernels') and hjxtv__lwkc.value.args[0
                ].name == arr_var.name:
                hjxtv__lwkc.value = ir.Const(False, hjxtv__lwkc.target.loc)
            if is_assign(hjxtv__lwkc) and hjxtv__lwkc.target.name in redvars:
                ind = redvars.index(hjxtv__lwkc.target.name)
                soy__ogr[ind] = hjxtv__lwkc.target
            igw__dukmv.append(hjxtv__lwkc)
        oxo__ikp.body = igw__dukmv
    vio__cugv = ['v{}'.format(i) for i in range(qxi__fvj)]
    etb__dakb = ['in{}'.format(i) for i in range(fqte__vqodh)]
    xdyd__fyc = 'def agg_update({}):\n'.format(', '.join(vio__cugv + etb__dakb)
        )
    xdyd__fyc += '    __update_redvars()\n'
    xdyd__fyc += '    return {}'.format(', '.join(['v{}'.format(i) for i in
        range(qxi__fvj)]))
    zhip__ljtl = {}
    exec(xdyd__fyc, {}, zhip__ljtl)
    etk__mtdf = zhip__ljtl['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * fqte__vqodh)
    f_ir = compile_to_numba_ir(etk__mtdf, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    xfd__hwgyb = f_ir.blocks.popitem()[1].body
    qco__ddd = pm.typemap[xfd__hwgyb[-1].value.name]
    jlkfz__ncp = wrap_parfor_blocks(parfor)
    zdv__gyl = find_topo_order(jlkfz__ncp)
    zdv__gyl = zdv__gyl[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    xlsd__cnqy = f_ir.blocks[zdv__gyl[0]]
    mbqzr__ijjck = f_ir.blocks[zdv__gyl[-1]]
    jyc__igqx = xfd__hwgyb[:qxi__fvj + fqte__vqodh]
    if qxi__fvj > 1:
        xmfy__vau = xfd__hwgyb[-3:]
        assert is_assign(xmfy__vau[0]) and isinstance(xmfy__vau[0].value,
            ir.Expr) and xmfy__vau[0].value.op == 'build_tuple'
    else:
        xmfy__vau = xfd__hwgyb[-2:]
    for i in range(qxi__fvj):
        umj__jkjw = xfd__hwgyb[i].target
        fvhb__ciig = ir.Assign(umj__jkjw, soy__ogr[i], umj__jkjw.loc)
        jyc__igqx.append(fvhb__ciig)
    for i in range(qxi__fvj, qxi__fvj + fqte__vqodh):
        umj__jkjw = xfd__hwgyb[i].target
        fvhb__ciig = ir.Assign(umj__jkjw, uino__ypsrl[i - qxi__fvj],
            umj__jkjw.loc)
        jyc__igqx.append(fvhb__ciig)
    xlsd__cnqy.body = jyc__igqx + xlsd__cnqy.body
    rnqbx__nfbd = []
    for i in range(qxi__fvj):
        umj__jkjw = xfd__hwgyb[i].target
        fvhb__ciig = ir.Assign(soy__ogr[i], umj__jkjw, umj__jkjw.loc)
        rnqbx__nfbd.append(fvhb__ciig)
    mbqzr__ijjck.body += rnqbx__nfbd + xmfy__vau
    hwk__mvefs = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        qco__ddd, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rbhi__zkmkb = numba.core.target_extension.dispatcher_registry[cpu_target](
        etk__mtdf)
    rbhi__zkmkb.add_overload(hwk__mvefs)
    return rbhi__zkmkb


def _rm_arg_agg_block(block, typemap):
    pwuqs__tsv = []
    arr_var = None
    for i, hjxtv__lwkc in enumerate(block.body):
        if is_assign(hjxtv__lwkc) and isinstance(hjxtv__lwkc.value, ir.Arg):
            arr_var = hjxtv__lwkc.target
            rvcyw__utm = typemap[arr_var.name]
            if not isinstance(rvcyw__utm, types.ArrayCompatible):
                pwuqs__tsv += block.body[i + 1:]
                break
            gyv__nsgi = block.body[i + 1]
            assert is_assign(gyv__nsgi) and isinstance(gyv__nsgi.value, ir.Expr
                ) and gyv__nsgi.value.op == 'getattr' and gyv__nsgi.value.attr == 'shape' and gyv__nsgi.value.value.name == arr_var.name
            oht__tfyrj = gyv__nsgi.target
            zvep__naw = block.body[i + 2]
            assert is_assign(zvep__naw) and isinstance(zvep__naw.value, ir.Expr
                ) and zvep__naw.value.op == 'static_getitem' and zvep__naw.value.value.name == oht__tfyrj.name
            pwuqs__tsv += block.body[i + 3:]
            break
        pwuqs__tsv.append(hjxtv__lwkc)
    return pwuqs__tsv, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    jlkfz__ncp = wrap_parfor_blocks(parfor)
    zdv__gyl = find_topo_order(jlkfz__ncp)
    zdv__gyl = zdv__gyl[1:]
    unwrap_parfor_blocks(parfor)
    for kzus__tmtcp in reversed(zdv__gyl):
        for hjxtv__lwkc in reversed(parfor.loop_body[kzus__tmtcp].body):
            if isinstance(hjxtv__lwkc, ir.Assign) and (hjxtv__lwkc.target.
                name in parfor_params or hjxtv__lwkc.target.name in
                var_to_param):
                clgi__yohab = hjxtv__lwkc.target.name
                rhs = hjxtv__lwkc.value
                cbj__ghzy = (clgi__yohab if clgi__yohab in parfor_params else
                    var_to_param[clgi__yohab])
                yill__jis = []
                if isinstance(rhs, ir.Var):
                    yill__jis = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    yill__jis = [v.name for v in hjxtv__lwkc.value.list_vars()]
                param_uses[cbj__ghzy].extend(yill__jis)
                for v in yill__jis:
                    var_to_param[v] = cbj__ghzy
            if isinstance(hjxtv__lwkc, Parfor):
                get_parfor_reductions(hjxtv__lwkc, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for cjfj__plj, yill__jis in param_uses.items():
        if cjfj__plj in yill__jis and cjfj__plj not in reduce_varnames:
            reduce_varnames.append(cjfj__plj)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
