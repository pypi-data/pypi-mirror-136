"""
Helper functions for transformations.
"""
import itertools
import math
import operator
import types as pytypes
from collections import namedtuple
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, types
from numba.core.ir_utils import GuardException, build_definitions, compile_to_numba_ir, compute_cfg_from_blocks, find_callname, find_const, get_definition, guard, is_setitem, mk_unique_var, replace_arg_nodes, require
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import fold_arguments
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoConstUpdatedError, BodoError, can_literalize_type, get_literal_value, get_overload_const_bool, get_overload_const_list, is_literal_type, is_overload_constant_bool
from bodo.utils.utils import is_array_typ, is_assign, is_call, is_expr
ReplaceFunc = namedtuple('ReplaceFunc', ['func', 'arg_types', 'args',
    'glbls', 'inline_bodo_calls', 'run_full_pipeline', 'pre_nodes'])
bodo_types_with_params = {'ArrayItemArrayType', 'CSRMatrixType',
    'CategoricalArrayType', 'CategoricalIndexType', 'DataFrameType',
    'DatetimeIndexType', 'Decimal128Type', 'DecimalArrayType',
    'IntegerArrayType', 'IntervalArrayType', 'IntervalIndexType', 'List',
    'MapArrayType', 'NumericIndexType', 'PDCategoricalDtype',
    'PeriodIndexType', 'RangeIndexType', 'SeriesType', 'StringIndexType',
    'BinaryIndexType', 'StructArrayType', 'TimedeltaIndexType',
    'TupleArrayType'}
container_update_method_names = ('clear', 'pop', 'popitem', 'update', 'add',
    'difference_update', 'discard', 'intersection_update', 'remove',
    'symmetric_difference_update', 'append', 'extend', 'insert', 'reverse',
    'sort')
no_side_effect_call_tuples = {(int,), (list,), (set,), (dict,), (min,), (
    max,), (abs,), (len,), (bool,), (str,), ('ceil', math), ('init_series',
    'pd_series_ext', 'hiframes', bodo), ('get_series_data', 'pd_series_ext',
    'hiframes', bodo), ('get_series_index', 'pd_series_ext', 'hiframes',
    bodo), ('get_series_name', 'pd_series_ext', 'hiframes', bodo), (
    'get_index_data', 'pd_index_ext', 'hiframes', bodo), ('get_index_name',
    'pd_index_ext', 'hiframes', bodo), ('init_binary_str_index',
    'pd_index_ext', 'hiframes', bodo), ('init_numeric_index',
    'pd_index_ext', 'hiframes', bodo), ('init_categorical_index',
    'pd_index_ext', 'hiframes', bodo), ('_dti_val_finalize', 'pd_index_ext',
    'hiframes', bodo), ('init_datetime_index', 'pd_index_ext', 'hiframes',
    bodo), ('init_timedelta_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_range_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_heter_index', 'pd_index_ext', 'hiframes', bodo), (
    'get_int_arr_data', 'int_arr_ext', 'libs', bodo), ('get_int_arr_bitmap',
    'int_arr_ext', 'libs', bodo), ('init_integer_array', 'int_arr_ext',
    'libs', bodo), ('alloc_int_array', 'int_arr_ext', 'libs', bodo), (
    'inplace_eq', 'str_arr_ext', 'libs', bodo), ('get_bool_arr_data',
    'bool_arr_ext', 'libs', bodo), ('get_bool_arr_bitmap', 'bool_arr_ext',
    'libs', bodo), ('init_bool_array', 'bool_arr_ext', 'libs', bodo), (
    'alloc_bool_array', 'bool_arr_ext', 'libs', bodo), (bodo.libs.
    bool_arr_ext.compute_or_body,), (bodo.libs.bool_arr_ext.
    compute_and_body,), ('alloc_datetime_date_array', 'datetime_date_ext',
    'hiframes', bodo), ('alloc_datetime_timedelta_array',
    'datetime_timedelta_ext', 'hiframes', bodo), ('cat_replace',
    'pd_categorical_ext', 'hiframes', bodo), ('init_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('alloc_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('get_categorical_arr_codes',
    'pd_categorical_ext', 'hiframes', bodo), ('_sum_handle_nan',
    'series_kernels', 'hiframes', bodo), ('_box_cat_val', 'series_kernels',
    'hiframes', bodo), ('_mean_handle_nan', 'series_kernels', 'hiframes',
    bodo), ('_var_handle_mincount', 'series_kernels', 'hiframes', bodo), (
    '_handle_nan_count', 'series_kernels', 'hiframes', bodo), (
    '_handle_nan_count_ddof', 'series_kernels', 'hiframes', bodo), (
    'dist_return', 'distributed_api', 'libs', bodo), ('init_dataframe',
    'pd_dataframe_ext', 'hiframes', bodo), ('get_dataframe_data',
    'pd_dataframe_ext', 'hiframes', bodo), ('get_dataframe_table',
    'pd_dataframe_ext', 'hiframes', bodo), ('get_table_data', 'table',
    'hiframes', bodo), ('get_dataframe_index', 'pd_dataframe_ext',
    'hiframes', bodo), ('init_rolling', 'pd_rolling_ext', 'hiframes', bodo),
    ('init_groupby', 'pd_groupby_ext', 'hiframes', bodo), ('calc_nitems',
    'array_kernels', 'libs', bodo), ('concat', 'array_kernels', 'libs',
    bodo), ('unique', 'array_kernels', 'libs', bodo), ('nunique',
    'array_kernels', 'libs', bodo), ('quantile', 'array_kernels', 'libs',
    bodo), ('explode', 'array_kernels', 'libs', bodo), (
    'str_arr_from_sequence', 'str_arr_ext', 'libs', bodo), (
    'parse_datetime_str', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_dt64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'dt64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'timedelta64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_timedelta64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'npy_datetimestruct_to_datetime', 'pd_timestamp_ext', 'hiframes', bodo),
    ('isna', 'array_kernels', 'libs', bodo), ('copy',), (
    'from_iterable_impl', 'typing', 'utils', bodo), ('chain', itertools), (
    'groupby',), ('rolling',), (pd.CategoricalDtype,), (bodo.hiframes.
    pd_categorical_ext.get_code_for_value,), ('asarray', np), ('int32', np),
    ('int64', np), ('float64', np), ('float32', np), ('bool_', np), ('full',
    np), ('round', np), ('isnan', np), ('isnat', np), ('internal_prange',
    'parfor', numba), ('internal_prange', 'parfor', 'parfors', numba), (
    'empty_inferred', 'ndarray', 'unsafe', numba), ('_slice_span',
    'unicode', numba), ('_normalize_slice', 'unicode', numba), (
    'init_session_builder', 'pyspark_ext', 'libs', bodo), ('init_session',
    'pyspark_ext', 'libs', bodo), ('init_spark_df', 'pyspark_ext', 'libs',
    bodo), ('h5size', 'h5_api', 'io', bodo), ('pre_alloc_struct_array',
    'struct_arr_ext', 'libs', bodo), (bodo.libs.struct_arr_ext.
    pre_alloc_struct_array,), ('pre_alloc_tuple_array', 'tuple_arr_ext',
    'libs', bodo), (bodo.libs.tuple_arr_ext.pre_alloc_tuple_array,), (
    'pre_alloc_array_item_array', 'array_item_arr_ext', 'libs', bodo), (
    bodo.libs.array_item_arr_ext.pre_alloc_array_item_array,), (
    'dist_reduce', 'distributed_api', 'libs', bodo), (bodo.libs.
    distributed_api.dist_reduce,), ('pre_alloc_string_array', 'str_arr_ext',
    'libs', bodo), (bodo.libs.str_arr_ext.pre_alloc_string_array,), (
    'pre_alloc_binary_array', 'binary_arr_ext', 'libs', bodo), (bodo.libs.
    binary_arr_ext.pre_alloc_binary_array,), ('pre_alloc_map_array',
    'map_arr_ext', 'libs', bodo), (bodo.libs.map_arr_ext.
    pre_alloc_map_array,), ('prange', bodo), (bodo.prange,), ('objmode',
    bodo), (bodo.objmode,), ('get_label_dict_from_categories',
    'pd_categorial_ext', 'hiframes', bodo), (
    'get_label_dict_from_categories_no_duplicates', 'pd_categorial_ext',
    'hiframes', bodo), ('build_nullable_tuple', 'nullable_tuple_ext',
    'libs', bodo)}


def remove_hiframes(rhs, lives, call_list):
    vpo__unf = tuple(call_list)
    if vpo__unf in no_side_effect_call_tuples:
        return True
    if len(call_list) == 4 and call_list[1:] == ['conversion', 'utils', bodo]:
        return True
    if isinstance(call_list[-1], pytypes.ModuleType) and call_list[-1
        ].__name__ == 'bodosql':
        return True
    if len(call_list) == 2 and call_list[0] == 'copy':
        return True
    if call_list == ['h5read', 'h5_api', 'io', bodo] and rhs.args[5
        ].name not in lives:
        return True
    if call_list == ['move_str_binary_arr_payload', 'str_arr_ext', 'libs', bodo
        ] and rhs.args[0].name not in lives:
        return True
    if call_list == ['setna', 'array_kernels', 'libs', bodo] and rhs.args[0
        ].name not in lives:
        return True
    if call_list == ['set_table_data', 'table', 'hiframes', bodo] and rhs.args[
        0].name not in lives:
        return True
    if len(vpo__unf) == 1 and tuple in getattr(vpo__unf[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=True):
    qiba__nbm = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd, 'math': math
        }
    if extra_globals is not None:
        qiba__nbm.update(extra_globals)
    if not replace_globals:
        qiba__nbm = func.__globals__
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, qiba__nbm, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[csft__bfce.name] for csft__bfce in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, qiba__nbm)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        plwdj__znptp = tuple(typing_info.typemap[csft__bfce.name] for
            csft__bfce in args)
        ekcm__nemw = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, plwdj__znptp, {}, {}, flags)
        ekcm__nemw.run()
    btr__bjshb = f_ir.blocks.popitem()[1]
    replace_arg_nodes(btr__bjshb, args)
    fqfd__tzywl = btr__bjshb.body[:-2]
    update_locs(fqfd__tzywl[len(args):], loc)
    for stmt in fqfd__tzywl[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        oyap__ufxs = btr__bjshb.body[-2]
        assert is_assign(oyap__ufxs) and is_expr(oyap__ufxs.value, 'cast')
        hkski__hmvos = oyap__ufxs.value.value
        fqfd__tzywl.append(ir.Assign(hkski__hmvos, ret_var, loc))
    return fqfd__tzywl


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for dzst__pvi in stmt.list_vars():
            dzst__pvi.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        jgeqa__ccly = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        ztla__gsp, appe__nmlz = jgeqa__ccly(stmt)
        return appe__nmlz
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        houa__nwx = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(houa__nwx, ir.UndefinedType):
            bmm__hnf = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{bmm__hnf}' is not defined", loc=loc)
    except GuardException as idv__ekgag:
        raise BodoError(err_msg, loc=loc)
    return houa__nwx


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    foyvu__spsy = get_definition(func_ir, var)
    jbmar__ldiu = None
    if typemap is not None:
        jbmar__ldiu = typemap.get(var.name, None)
    if isinstance(foyvu__spsy, ir.Arg) and arg_types is not None:
        jbmar__ldiu = arg_types[foyvu__spsy.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(jbmar__ldiu):
        return get_literal_value(jbmar__ldiu)
    if isinstance(foyvu__spsy, (ir.Const, ir.Global, ir.FreeVar)):
        houa__nwx = foyvu__spsy.value
        return houa__nwx
    if literalize_args and isinstance(foyvu__spsy, ir.Arg
        ) and can_literalize_type(jbmar__ldiu, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({foyvu__spsy.index}, loc=
            var.loc, file_infos={foyvu__spsy.index: file_info} if file_info
             is not None else None)
    if is_expr(foyvu__spsy, 'binop'):
        if file_info and foyvu__spsy.fn == operator.add:
            try:
                gpmgr__cdvnl = get_const_value_inner(func_ir, foyvu__spsy.
                    lhs, arg_types, typemap, updated_containers,
                    literalize_args=False)
                file_info.set_concat(gpmgr__cdvnl, True)
                sgzp__bec = get_const_value_inner(func_ir, foyvu__spsy.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return foyvu__spsy.fn(gpmgr__cdvnl, sgzp__bec)
            except (GuardException, BodoConstUpdatedError) as idv__ekgag:
                pass
            try:
                sgzp__bec = get_const_value_inner(func_ir, foyvu__spsy.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(sgzp__bec, False)
                gpmgr__cdvnl = get_const_value_inner(func_ir, foyvu__spsy.
                    lhs, arg_types, typemap, updated_containers, file_info)
                return foyvu__spsy.fn(gpmgr__cdvnl, sgzp__bec)
            except (GuardException, BodoConstUpdatedError) as idv__ekgag:
                pass
        gpmgr__cdvnl = get_const_value_inner(func_ir, foyvu__spsy.lhs,
            arg_types, typemap, updated_containers)
        sgzp__bec = get_const_value_inner(func_ir, foyvu__spsy.rhs,
            arg_types, typemap, updated_containers)
        return foyvu__spsy.fn(gpmgr__cdvnl, sgzp__bec)
    if is_expr(foyvu__spsy, 'unary'):
        houa__nwx = get_const_value_inner(func_ir, foyvu__spsy.value,
            arg_types, typemap, updated_containers)
        return foyvu__spsy.fn(houa__nwx)
    if is_expr(foyvu__spsy, 'getattr') and typemap:
        fjx__mgg = typemap.get(foyvu__spsy.value.name, None)
        if isinstance(fjx__mgg, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and foyvu__spsy.attr == 'columns':
            return pd.Index(fjx__mgg.columns)
        if isinstance(fjx__mgg, types.SliceType):
            azy__brjm = get_definition(func_ir, foyvu__spsy.value)
            require(is_call(azy__brjm))
            hzzmt__jgrn = find_callname(func_ir, azy__brjm)
            geuon__jded = False
            if hzzmt__jgrn == ('_normalize_slice', 'numba.cpython.unicode'):
                require(foyvu__spsy.attr in ('start', 'step'))
                azy__brjm = get_definition(func_ir, azy__brjm.args[0])
                geuon__jded = True
            require(find_callname(func_ir, azy__brjm) == ('slice', 'builtins'))
            if len(azy__brjm.args) == 1:
                if foyvu__spsy.attr == 'start':
                    return 0
                if foyvu__spsy.attr == 'step':
                    return 1
                require(foyvu__spsy.attr == 'stop')
                return get_const_value_inner(func_ir, azy__brjm.args[0],
                    arg_types, typemap, updated_containers)
            if foyvu__spsy.attr == 'start':
                houa__nwx = get_const_value_inner(func_ir, azy__brjm.args[0
                    ], arg_types, typemap, updated_containers)
                if houa__nwx is None:
                    houa__nwx = 0
                if geuon__jded:
                    require(houa__nwx == 0)
                return houa__nwx
            if foyvu__spsy.attr == 'stop':
                assert not geuon__jded
                return get_const_value_inner(func_ir, azy__brjm.args[1],
                    arg_types, typemap, updated_containers)
            require(foyvu__spsy.attr == 'step')
            if len(azy__brjm.args) == 2:
                return 1
            else:
                houa__nwx = get_const_value_inner(func_ir, azy__brjm.args[2
                    ], arg_types, typemap, updated_containers)
                if houa__nwx is None:
                    houa__nwx = 1
                if geuon__jded:
                    require(houa__nwx == 1)
                return houa__nwx
    if is_expr(foyvu__spsy, 'getattr'):
        return getattr(get_const_value_inner(func_ir, foyvu__spsy.value,
            arg_types, typemap, updated_containers), foyvu__spsy.attr)
    if is_expr(foyvu__spsy, 'getitem'):
        value = get_const_value_inner(func_ir, foyvu__spsy.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, foyvu__spsy.index, arg_types,
            typemap, updated_containers)
        return value[index]
    onwih__quybd = guard(find_callname, func_ir, foyvu__spsy, typemap)
    if onwih__quybd is not None and len(onwih__quybd) == 2 and onwih__quybd[0
        ] == 'keys' and isinstance(onwih__quybd[1], ir.Var):
        itn__ckx = foyvu__spsy.func
        foyvu__spsy = get_definition(func_ir, onwih__quybd[1])
        agl__mgf = onwih__quybd[1].name
        if updated_containers and agl__mgf in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                agl__mgf, updated_containers[agl__mgf]))
        require(is_expr(foyvu__spsy, 'build_map'))
        vals = [dzst__pvi[0] for dzst__pvi in foyvu__spsy.items]
        qssv__hnvt = guard(get_definition, func_ir, itn__ckx)
        assert isinstance(qssv__hnvt, ir.Expr) and qssv__hnvt.attr == 'keys'
        qssv__hnvt.attr = 'copy'
        return [get_const_value_inner(func_ir, dzst__pvi, arg_types,
            typemap, updated_containers) for dzst__pvi in vals]
    if is_expr(foyvu__spsy, 'build_map'):
        return {get_const_value_inner(func_ir, dzst__pvi[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            dzst__pvi[1], arg_types, typemap, updated_containers) for
            dzst__pvi in foyvu__spsy.items}
    if is_expr(foyvu__spsy, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, dzst__pvi, arg_types,
            typemap, updated_containers) for dzst__pvi in foyvu__spsy.items)
    if is_expr(foyvu__spsy, 'build_list'):
        return [get_const_value_inner(func_ir, dzst__pvi, arg_types,
            typemap, updated_containers) for dzst__pvi in foyvu__spsy.items]
    if is_expr(foyvu__spsy, 'build_set'):
        return {get_const_value_inner(func_ir, dzst__pvi, arg_types,
            typemap, updated_containers) for dzst__pvi in foyvu__spsy.items}
    if onwih__quybd == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, foyvu__spsy.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if onwih__quybd == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, foyvu__spsy.args[0],
            arg_types, typemap, updated_containers))
    if onwih__quybd == ('range', 'builtins') and len(foyvu__spsy.args) == 1:
        return range(get_const_value_inner(func_ir, foyvu__spsy.args[0],
            arg_types, typemap, updated_containers))
    if onwih__quybd == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, dzst__pvi,
            arg_types, typemap, updated_containers) for dzst__pvi in
            foyvu__spsy.args))
    if onwih__quybd == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, foyvu__spsy.args[0],
            arg_types, typemap, updated_containers))
    if onwih__quybd == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, foyvu__spsy.args[0],
            arg_types, typemap, updated_containers))
    if onwih__quybd == ('format', 'builtins'):
        csft__bfce = get_const_value_inner(func_ir, foyvu__spsy.args[0],
            arg_types, typemap, updated_containers)
        jwe__gvci = get_const_value_inner(func_ir, foyvu__spsy.args[1],
            arg_types, typemap, updated_containers) if len(foyvu__spsy.args
            ) > 1 else ''
        return format(csft__bfce, jwe__gvci)
    if onwih__quybd in (('init_binary_str_index',
        'bodo.hiframes.pd_index_ext'), ('init_numeric_index',
        'bodo.hiframes.pd_index_ext'), ('init_categorical_index',
        'bodo.hiframes.pd_index_ext'), ('init_datetime_index',
        'bodo.hiframes.pd_index_ext'), ('init_timedelta_index',
        'bodo.hiframes.pd_index_ext'), ('init_heter_index',
        'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, foyvu__spsy.args[0],
            arg_types, typemap, updated_containers))
    if onwih__quybd == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, foyvu__spsy.args[0],
            arg_types, typemap, updated_containers))
    if onwih__quybd == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, foyvu__spsy.
            args[0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, foyvu__spsy.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            foyvu__spsy.args[2], arg_types, typemap, updated_containers))
    if onwih__quybd == ('len', 'builtins') and typemap and isinstance(typemap
        .get(foyvu__spsy.args[0].name, None), types.BaseTuple):
        return len(typemap[foyvu__spsy.args[0].name])
    if onwih__quybd == ('len', 'builtins'):
        jpc__yjdy = guard(get_definition, func_ir, foyvu__spsy.args[0])
        if isinstance(jpc__yjdy, ir.Expr) and jpc__yjdy.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(jpc__yjdy.items)
        return len(get_const_value_inner(func_ir, foyvu__spsy.args[0],
            arg_types, typemap, updated_containers))
    if onwih__quybd == ('CategoricalDtype', 'pandas'):
        kws = dict(foyvu__spsy.kws)
        kfs__has = get_call_expr_arg('CategoricalDtype', foyvu__spsy.args,
            kws, 0, 'categories', '')
        aafx__sfifr = get_call_expr_arg('CategoricalDtype', foyvu__spsy.
            args, kws, 1, 'ordered', False)
        if aafx__sfifr is not False:
            aafx__sfifr = get_const_value_inner(func_ir, aafx__sfifr,
                arg_types, typemap, updated_containers)
        if kfs__has == '':
            kfs__has = None
        else:
            kfs__has = get_const_value_inner(func_ir, kfs__has, arg_types,
                typemap, updated_containers)
        return pd.CategoricalDtype(kfs__has, aafx__sfifr)
    if onwih__quybd == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, foyvu__spsy.args[0],
            arg_types, typemap, updated_containers))
    if onwih__quybd is not None and len(onwih__quybd) == 2 and onwih__quybd[1
        ] == 'pandas' and onwih__quybd[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, onwih__quybd[0])()
    if onwih__quybd is not None and len(onwih__quybd) == 2 and isinstance(
        onwih__quybd[1], ir.Var):
        houa__nwx = get_const_value_inner(func_ir, onwih__quybd[1],
            arg_types, typemap, updated_containers)
        args = [get_const_value_inner(func_ir, dzst__pvi, arg_types,
            typemap, updated_containers) for dzst__pvi in foyvu__spsy.args]
        kws = {ckuul__vdcrt[0]: get_const_value_inner(func_ir, ckuul__vdcrt
            [1], arg_types, typemap, updated_containers) for ckuul__vdcrt in
            foyvu__spsy.kws}
        return getattr(houa__nwx, onwih__quybd[0])(*args, **kws)
    if onwih__quybd is not None and len(onwih__quybd) == 2 and onwih__quybd[1
        ] == 'bodo' and onwih__quybd[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, dzst__pvi, arg_types,
            typemap, updated_containers) for dzst__pvi in foyvu__spsy.args)
        kwargs = {bmm__hnf: get_const_value_inner(func_ir, dzst__pvi,
            arg_types, typemap, updated_containers) for bmm__hnf, dzst__pvi in
            dict(foyvu__spsy.kws).items()}
        return getattr(bodo, onwih__quybd[0])(*args, **kwargs)
    if is_call(foyvu__spsy) and typemap and isinstance(typemap.get(
        foyvu__spsy.func.name, None), types.Dispatcher):
        py_func = typemap[foyvu__spsy.func.name].dispatcher.py_func
        require(foyvu__spsy.vararg is None)
        args = tuple(get_const_value_inner(func_ir, dzst__pvi, arg_types,
            typemap, updated_containers) for dzst__pvi in foyvu__spsy.args)
        kwargs = {bmm__hnf: get_const_value_inner(func_ir, dzst__pvi,
            arg_types, typemap, updated_containers) for bmm__hnf, dzst__pvi in
            dict(foyvu__spsy.kws).items()}
        arg_types = tuple(bodo.typeof(dzst__pvi) for dzst__pvi in args)
        kw_types = {hxg__hkl: bodo.typeof(dzst__pvi) for hxg__hkl,
            dzst__pvi in kwargs.items()}
        require(_func_is_pure(py_func, arg_types, kw_types))
        return py_func(*args, **kwargs)
    raise GuardException('Constant value not found')


def _func_is_pure(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.ir.csv_ext import CsvReader
    from bodo.ir.json_ext import JsonReader
    from bodo.ir.parquet_ext import ParquetReader
    from bodo.ir.sql_ext import SqlReader
    f_ir, typemap, ekz__jfn, ekz__jfn = bodo.compiler.get_func_type_info(
        py_func, arg_types, kw_types)
    for block in f_ir.blocks.values():
        for stmt in block.body:
            if isinstance(stmt, ir.Print):
                return False
            if isinstance(stmt, (CsvReader, JsonReader, ParquetReader,
                SqlReader)):
                return False
            if is_setitem(stmt) and isinstance(guard(get_definition, f_ir,
                stmt.target), ir.Arg):
                return False
            if is_assign(stmt):
                rhs = stmt.value
                if isinstance(rhs, ir.Yield):
                    return False
                if is_call(rhs):
                    gtlz__lkyr = guard(get_definition, f_ir, rhs.func)
                    if isinstance(gtlz__lkyr, ir.Const) and isinstance(
                        gtlz__lkyr.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    mdfor__bfz = guard(find_callname, f_ir, rhs)
                    if mdfor__bfz is None:
                        return False
                    func_name, blvw__axji = mdfor__bfz
                    if blvw__axji == 'pandas' and func_name.startswith('read_'
                        ):
                        return False
                    if mdfor__bfz in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if mdfor__bfz == ('File', 'h5py'):
                        return False
                    if isinstance(blvw__axji, ir.Var):
                        jbmar__ldiu = typemap[blvw__axji.name]
                        if isinstance(jbmar__ldiu, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(jbmar__ldiu, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(jbmar__ldiu, bodo.LoggingLoggerType):
                            return False
                        if str(jbmar__ldiu).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            blvw__axji), ir.Arg)):
                            return False
                    if blvw__axji in ('numpy.random', 'time', 'logging',
                        'matplotlib.pyplot'):
                        return False
    return True


def fold_argument_types(pysig, args, kws):

    def normal_handler(index, param, value):
        return value

    def default_handler(index, param, default):
        return types.Omitted(default)

    def stararg_handler(index, param, values):
        return types.StarArgTuple(values)
    args = fold_arguments(pysig, args, kws, normal_handler, default_handler,
        stararg_handler)
    return args


def get_const_func_output_type(func, arg_types, kw_types, typing_context,
    target_context, is_udf=True):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
    py_func = None
    if isinstance(func, types.MakeFunctionLiteral):
        wponf__ayrm = func.literal_value.code
        zeojr__aim = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            zeojr__aim = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(zeojr__aim, wponf__ayrm)
        fix_struct_return(f_ir)
        typemap, agq__gsgj, coct__uza, ekz__jfn = (numba.core.typed_passes.
            type_inference_stage(typing_context, target_context, f_ir,
            arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, coct__uza, agq__gsgj = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, coct__uza, agq__gsgj = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, coct__uza, agq__gsgj = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    if is_udf and isinstance(agq__gsgj, types.DictType):
        taaox__ehy = guard(get_struct_keynames, f_ir, typemap)
        if taaox__ehy is not None:
            agq__gsgj = StructType((agq__gsgj.value_type,) * len(taaox__ehy
                ), taaox__ehy)
    if is_udf and isinstance(agq__gsgj, (SeriesType, HeterogeneousSeriesType)):
        gwmck__vmh = numba.core.registry.cpu_target.typing_context
        bjk__ngj = numba.core.registry.cpu_target.target_context
        fzlg__kjox = bodo.transforms.series_pass.SeriesPass(f_ir,
            gwmck__vmh, bjk__ngj, typemap, coct__uza, {})
        fzlg__kjox.run()
        fzlg__kjox.run()
        fzlg__kjox.run()
        wlqcz__hlcvx = compute_cfg_from_blocks(f_ir.blocks)
        fbgp__gilq = [guard(_get_const_series_info, f_ir.blocks[grrfn__qce],
            f_ir, typemap) for grrfn__qce in wlqcz__hlcvx.exit_points() if
            isinstance(f_ir.blocks[grrfn__qce].body[-1], ir.Return)]
        if None in fbgp__gilq or len(pd.Series(fbgp__gilq).unique()) != 1:
            agq__gsgj.const_info = None
        else:
            agq__gsgj.const_info = fbgp__gilq[0]
    return agq__gsgj


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    oxhv__kjjk = block.body[-1].value
    kmiqb__fehc = get_definition(f_ir, oxhv__kjjk)
    require(is_expr(kmiqb__fehc, 'cast'))
    kmiqb__fehc = get_definition(f_ir, kmiqb__fehc.value)
    require(is_call(kmiqb__fehc) and find_callname(f_ir, kmiqb__fehc) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    lztd__mjlnx = kmiqb__fehc.args[1]
    atbn__sgg = tuple(get_const_value_inner(f_ir, lztd__mjlnx, typemap=typemap)
        )
    if isinstance(typemap[oxhv__kjjk.name], HeterogeneousSeriesType):
        return len(typemap[oxhv__kjjk.name].data), atbn__sgg
    hjeiz__xssas = kmiqb__fehc.args[0]
    kwfc__kgr = get_definition(f_ir, hjeiz__xssas)
    func_name, smuxv__pezbo = find_callname(f_ir, kwfc__kgr)
    if is_call(kwfc__kgr) and bodo.utils.utils.is_alloc_callname(func_name,
        smuxv__pezbo):
        fedth__ant = kwfc__kgr.args[0]
        slb__nddkj = get_const_value_inner(f_ir, fedth__ant, typemap=typemap)
        return slb__nddkj, atbn__sgg
    if is_call(kwfc__kgr) and find_callname(f_ir, kwfc__kgr) in [('asarray',
        'numpy'), ('str_arr_from_sequence', 'bodo.libs.str_arr_ext')]:
        hjeiz__xssas = kwfc__kgr.args[0]
        kwfc__kgr = get_definition(f_ir, hjeiz__xssas)
    require(is_expr(kwfc__kgr, 'build_tuple') or is_expr(kwfc__kgr,
        'build_list'))
    return len(kwfc__kgr.items), atbn__sgg


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    qyhmt__ghmxw = []
    zljjg__sml = []
    values = []
    for hxg__hkl, dzst__pvi in build_map.items:
        iqu__zljh = find_const(f_ir, hxg__hkl)
        require(isinstance(iqu__zljh, str))
        zljjg__sml.append(iqu__zljh)
        qyhmt__ghmxw.append(hxg__hkl)
        values.append(dzst__pvi)
    dhk__uhxn = ir.Var(scope, mk_unique_var('val_tup'), loc)
    krai__hbhm = ir.Assign(ir.Expr.build_tuple(values, loc), dhk__uhxn, loc)
    f_ir._definitions[dhk__uhxn.name] = [krai__hbhm.value]
    deysb__gatuv = ir.Var(scope, mk_unique_var('key_tup'), loc)
    dkx__kuwad = ir.Assign(ir.Expr.build_tuple(qyhmt__ghmxw, loc),
        deysb__gatuv, loc)
    f_ir._definitions[deysb__gatuv.name] = [dkx__kuwad.value]
    if typemap is not None:
        typemap[dhk__uhxn.name] = types.Tuple([typemap[dzst__pvi.name] for
            dzst__pvi in values])
        typemap[deysb__gatuv.name] = types.Tuple([typemap[dzst__pvi.name] for
            dzst__pvi in qyhmt__ghmxw])
    return zljjg__sml, dhk__uhxn, krai__hbhm, deysb__gatuv, dkx__kuwad


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    dgt__xqdao = block.body[-1].value
    iuig__rxha = guard(get_definition, f_ir, dgt__xqdao)
    require(is_expr(iuig__rxha, 'cast'))
    kmiqb__fehc = guard(get_definition, f_ir, iuig__rxha.value)
    require(is_expr(kmiqb__fehc, 'build_map'))
    require(len(kmiqb__fehc.items) > 0)
    loc = block.loc
    scope = block.scope
    zljjg__sml, dhk__uhxn, krai__hbhm, deysb__gatuv, dkx__kuwad = (
        extract_keyvals_from_struct_map(f_ir, kmiqb__fehc, loc, scope))
    yvjex__eeyf = ir.Var(scope, mk_unique_var('conv_call'), loc)
    tjql__eglrs = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), yvjex__eeyf, loc)
    f_ir._definitions[yvjex__eeyf.name] = [tjql__eglrs.value]
    soyxs__acnv = ir.Var(scope, mk_unique_var('struct_val'), loc)
    calr__ltv = ir.Assign(ir.Expr.call(yvjex__eeyf, [dhk__uhxn,
        deysb__gatuv], {}, loc), soyxs__acnv, loc)
    f_ir._definitions[soyxs__acnv.name] = [calr__ltv.value]
    iuig__rxha.value = soyxs__acnv
    kmiqb__fehc.items = [(hxg__hkl, hxg__hkl) for hxg__hkl, ekz__jfn in
        kmiqb__fehc.items]
    block.body = block.body[:-2] + [krai__hbhm, dkx__kuwad, tjql__eglrs,
        calr__ltv] + block.body[-2:]
    return tuple(zljjg__sml)


def get_struct_keynames(f_ir, typemap):
    wlqcz__hlcvx = compute_cfg_from_blocks(f_ir.blocks)
    zdum__dnd = list(wlqcz__hlcvx.exit_points())[0]
    block = f_ir.blocks[zdum__dnd]
    require(isinstance(block.body[-1], ir.Return))
    dgt__xqdao = block.body[-1].value
    iuig__rxha = guard(get_definition, f_ir, dgt__xqdao)
    require(is_expr(iuig__rxha, 'cast'))
    kmiqb__fehc = guard(get_definition, f_ir, iuig__rxha.value)
    require(is_call(kmiqb__fehc) and find_callname(f_ir, kmiqb__fehc) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[kmiqb__fehc.args[1].name])


def fix_struct_return(f_ir):
    adj__rfynx = None
    wlqcz__hlcvx = compute_cfg_from_blocks(f_ir.blocks)
    for zdum__dnd in wlqcz__hlcvx.exit_points():
        adj__rfynx = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            zdum__dnd], zdum__dnd)
    return adj__rfynx


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    jpob__wnb = ir.Block(ir.Scope(None, loc), loc)
    jpob__wnb.body = node_list
    build_definitions({(0): jpob__wnb}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(dzst__pvi) for dzst__pvi in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    bfhb__szc = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(bfhb__szc, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for luxr__vkujt in range(len(vals) - 1, -1, -1):
        dzst__pvi = vals[luxr__vkujt]
        if isinstance(dzst__pvi, str) and dzst__pvi.startswith(
            NESTED_TUP_SENTINEL):
            xosfb__mqy = int(dzst__pvi[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:luxr__vkujt]) + (
                tuple(vals[luxr__vkujt + 1:luxr__vkujt + xosfb__mqy + 1]),) +
                tuple(vals[luxr__vkujt + xosfb__mqy + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    csft__bfce = None
    if len(args) > arg_no and arg_no >= 0:
        csft__bfce = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        csft__bfce = kws[arg_name]
    if csft__bfce is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return csft__bfce


def set_call_expr_arg(var, args, kws, arg_no, arg_name):
    if len(args) > arg_no:
        args[arg_no] = var
    elif arg_name in kws:
        kws[arg_name] = var
    else:
        raise BodoError('cannot set call argument since does not exist')


def avoid_udf_inline(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    f_ir = numba.core.compiler.run_frontend(py_func, inline_closures=True)
    if '_bodo_inline' in kw_types and is_overload_constant_bool(kw_types[
        '_bodo_inline']):
        return not get_overload_const_bool(kw_types['_bodo_inline'])
    if any(isinstance(t, DataFrameType) for t in arg_types + tuple(kw_types
        .values())):
        return True
    for block in f_ir.blocks.values():
        if isinstance(block.body[-1], (ir.Raise, ir.StaticRaise)):
            return True
        for stmt in block.body:
            if isinstance(stmt, ir.EnterWith):
                return True
    return False


def replace_func(pass_info, func, args, const=False, pre_nodes=None,
    extra_globals=None, pysig=None, kws=None, inline_bodo_calls=False,
    run_full_pipeline=False):
    qiba__nbm = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        qiba__nbm.update(extra_globals)
    func.__globals__.update(qiba__nbm)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            kcyqr__ast = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[kcyqr__ast.name] = types.literal(default)
            except:
                pass_info.typemap[kcyqr__ast.name] = numba.typeof(default)
            qljab__ihsw = ir.Assign(ir.Const(default, loc), kcyqr__ast, loc)
            pre_nodes.append(qljab__ihsw)
            return kcyqr__ast
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    plwdj__znptp = tuple(pass_info.typemap[dzst__pvi.name] for dzst__pvi in
        args)
    if const:
        dufpa__neqg = []
        for luxr__vkujt, csft__bfce in enumerate(args):
            houa__nwx = guard(find_const, pass_info.func_ir, csft__bfce)
            if houa__nwx:
                dufpa__neqg.append(types.literal(houa__nwx))
            else:
                dufpa__neqg.append(plwdj__znptp[luxr__vkujt])
        plwdj__znptp = tuple(dufpa__neqg)
    return ReplaceFunc(func, plwdj__znptp, args, qiba__nbm,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(nzzbz__sjfp) for nzzbz__sjfp in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        bmub__mbrrx = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {bmub__mbrrx} = 0\n', (bmub__mbrrx,)
    if isinstance(t, ArrayItemArrayType):
        jzfg__tgi, crtvl__whwji = gen_init_varsize_alloc_sizes(t.dtype)
        bmub__mbrrx = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {bmub__mbrrx} = 0\n' + jzfg__tgi, (bmub__mbrrx,
            ) + crtvl__whwji
    return '', ()


def gen_varsize_item_sizes(t, item, var_names):
    if t == string_array_type:
        return '    {} += bodo.libs.str_arr_ext.get_utf8_size({})\n'.format(
            var_names[0], item)
    if isinstance(t, ArrayItemArrayType):
        return '    {} += len({})\n'.format(var_names[0], item
            ) + gen_varsize_array_counts(t.dtype, item, var_names[1:])
    return ''


def gen_varsize_array_counts(t, item, var_names):
    if t == string_array_type:
        return ('    {} += bodo.libs.str_arr_ext.get_num_total_chars({})\n'
            .format(var_names[0], item))
    return ''


def get_type_alloc_counts(t):
    if isinstance(t, (StructArrayType, TupleArrayType)):
        return 1 + sum(get_type_alloc_counts(nzzbz__sjfp.dtype) for
            nzzbz__sjfp in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(nzzbz__sjfp) for nzzbz__sjfp in t.data
            )
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(nzzbz__sjfp) for nzzbz__sjfp in t.
            types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    jae__nwmdh = typing_context.resolve_getattr(obj_dtype, func_name)
    if jae__nwmdh is None:
        oow__zjfu = types.misc.Module(np)
        try:
            jae__nwmdh = typing_context.resolve_getattr(oow__zjfu, func_name)
        except AttributeError as idv__ekgag:
            jae__nwmdh = None
        if jae__nwmdh is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return jae__nwmdh


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    jae__nwmdh = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(jae__nwmdh, types.BoundFunction):
        if axis is not None:
            fwb__tesv = jae__nwmdh.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            fwb__tesv = jae__nwmdh.get_call_type(typing_context, (), {})
        return fwb__tesv.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(jae__nwmdh):
            fwb__tesv = jae__nwmdh.get_call_type(typing_context, (obj_dtype
                ,), {})
            return fwb__tesv.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    jae__nwmdh = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(jae__nwmdh, types.BoundFunction):
        frol__hxsms = jae__nwmdh.template
        if axis is not None:
            return frol__hxsms._overload_func(obj_dtype, axis=axis)
        else:
            return frol__hxsms._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    byvsq__nxcg = get_definition(func_ir, dict_var)
    require(isinstance(byvsq__nxcg, ir.Expr))
    require(byvsq__nxcg.op == 'build_map')
    efkie__acv = byvsq__nxcg.items
    qyhmt__ghmxw = []
    values = []
    yph__ldaw = False
    for luxr__vkujt in range(len(efkie__acv)):
        qnco__ydccf, value = efkie__acv[luxr__vkujt]
        try:
            fbs__throm = get_const_value_inner(func_ir, qnco__ydccf,
                arg_types, typemap, updated_containers)
            qyhmt__ghmxw.append(fbs__throm)
            values.append(value)
        except GuardException as idv__ekgag:
            require_const_map[qnco__ydccf] = label
            yph__ldaw = True
    if yph__ldaw:
        raise GuardException
    return qyhmt__ghmxw, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        qyhmt__ghmxw = tuple(get_const_value_inner(func_ir, t[0], args) for
            t in build_map.items)
    except GuardException as idv__ekgag:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in qyhmt__ghmxw):
        raise BodoError(err_msg, loc)
    return qyhmt__ghmxw


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    qyhmt__ghmxw = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    agqpv__cyc = []
    bfh__kzie = [bodo.transforms.typing_pass._create_const_var(hxg__hkl,
        'dict_key', scope, loc, agqpv__cyc) for hxg__hkl in qyhmt__ghmxw]
    vfk__qvu = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        rpsdv__epkqu = ir.Var(scope, mk_unique_var('sentinel'), loc)
        jzzmo__nfze = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        agqpv__cyc.append(ir.Assign(ir.Const('__bodo_tup', loc),
            rpsdv__epkqu, loc))
        deq__gftv = [rpsdv__epkqu] + bfh__kzie + vfk__qvu
        agqpv__cyc.append(ir.Assign(ir.Expr.build_tuple(deq__gftv, loc),
            jzzmo__nfze, loc))
        return (jzzmo__nfze,), agqpv__cyc
    else:
        myqkg__llwn = ir.Var(scope, mk_unique_var('values_tup'), loc)
        nzry__csfhj = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        agqpv__cyc.append(ir.Assign(ir.Expr.build_tuple(vfk__qvu, loc),
            myqkg__llwn, loc))
        agqpv__cyc.append(ir.Assign(ir.Expr.build_tuple(bfh__kzie, loc),
            nzry__csfhj, loc))
        return (myqkg__llwn, nzry__csfhj), agqpv__cyc
