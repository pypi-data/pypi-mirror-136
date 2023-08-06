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
    phzoc__uxd = tuple(call_list)
    if phzoc__uxd in no_side_effect_call_tuples:
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
    if len(phzoc__uxd) == 1 and tuple in getattr(phzoc__uxd[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=True):
    zrup__skk = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd, 'math': math
        }
    if extra_globals is not None:
        zrup__skk.update(extra_globals)
    if not replace_globals:
        zrup__skk = func.__globals__
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, zrup__skk, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[gpxzp__acg.name] for gpxzp__acg in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, zrup__skk)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        ocrmc__ykgk = tuple(typing_info.typemap[gpxzp__acg.name] for
            gpxzp__acg in args)
        bbfjv__hbx = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, ocrmc__ykgk, {}, {}, flags)
        bbfjv__hbx.run()
    jdz__fbj = f_ir.blocks.popitem()[1]
    replace_arg_nodes(jdz__fbj, args)
    pwf__dxukl = jdz__fbj.body[:-2]
    update_locs(pwf__dxukl[len(args):], loc)
    for stmt in pwf__dxukl[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        wfgj__tjp = jdz__fbj.body[-2]
        assert is_assign(wfgj__tjp) and is_expr(wfgj__tjp.value, 'cast')
        fatf__cutlf = wfgj__tjp.value.value
        pwf__dxukl.append(ir.Assign(fatf__cutlf, ret_var, loc))
    return pwf__dxukl


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for ofnmq__egdnz in stmt.list_vars():
            ofnmq__egdnz.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        kpaer__mrf = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        bmolq__iot, zvsn__tho = kpaer__mrf(stmt)
        return zvsn__tho
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        qundl__rjncb = get_const_value_inner(func_ir, var, arg_types,
            typemap, file_info=file_info)
        if isinstance(qundl__rjncb, ir.UndefinedType):
            gfzt__tkozx = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{gfzt__tkozx}' is not defined", loc=loc)
    except GuardException as fwfsp__pgq:
        raise BodoError(err_msg, loc=loc)
    return qundl__rjncb


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    uxqm__hrkun = get_definition(func_ir, var)
    wpg__sidg = None
    if typemap is not None:
        wpg__sidg = typemap.get(var.name, None)
    if isinstance(uxqm__hrkun, ir.Arg) and arg_types is not None:
        wpg__sidg = arg_types[uxqm__hrkun.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(wpg__sidg):
        return get_literal_value(wpg__sidg)
    if isinstance(uxqm__hrkun, (ir.Const, ir.Global, ir.FreeVar)):
        qundl__rjncb = uxqm__hrkun.value
        return qundl__rjncb
    if literalize_args and isinstance(uxqm__hrkun, ir.Arg
        ) and can_literalize_type(wpg__sidg, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({uxqm__hrkun.index}, loc=
            var.loc, file_infos={uxqm__hrkun.index: file_info} if file_info
             is not None else None)
    if is_expr(uxqm__hrkun, 'binop'):
        if file_info and uxqm__hrkun.fn == operator.add:
            try:
                rsbs__ygir = get_const_value_inner(func_ir, uxqm__hrkun.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(rsbs__ygir, True)
                erve__kkm = get_const_value_inner(func_ir, uxqm__hrkun.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return uxqm__hrkun.fn(rsbs__ygir, erve__kkm)
            except (GuardException, BodoConstUpdatedError) as fwfsp__pgq:
                pass
            try:
                erve__kkm = get_const_value_inner(func_ir, uxqm__hrkun.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(erve__kkm, False)
                rsbs__ygir = get_const_value_inner(func_ir, uxqm__hrkun.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return uxqm__hrkun.fn(rsbs__ygir, erve__kkm)
            except (GuardException, BodoConstUpdatedError) as fwfsp__pgq:
                pass
        rsbs__ygir = get_const_value_inner(func_ir, uxqm__hrkun.lhs,
            arg_types, typemap, updated_containers)
        erve__kkm = get_const_value_inner(func_ir, uxqm__hrkun.rhs,
            arg_types, typemap, updated_containers)
        return uxqm__hrkun.fn(rsbs__ygir, erve__kkm)
    if is_expr(uxqm__hrkun, 'unary'):
        qundl__rjncb = get_const_value_inner(func_ir, uxqm__hrkun.value,
            arg_types, typemap, updated_containers)
        return uxqm__hrkun.fn(qundl__rjncb)
    if is_expr(uxqm__hrkun, 'getattr') and typemap:
        zxcv__ksymy = typemap.get(uxqm__hrkun.value.name, None)
        if isinstance(zxcv__ksymy, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and uxqm__hrkun.attr == 'columns':
            return pd.Index(zxcv__ksymy.columns)
        if isinstance(zxcv__ksymy, types.SliceType):
            dadn__epczf = get_definition(func_ir, uxqm__hrkun.value)
            require(is_call(dadn__epczf))
            rihjr__zjnz = find_callname(func_ir, dadn__epczf)
            wemi__pbqg = False
            if rihjr__zjnz == ('_normalize_slice', 'numba.cpython.unicode'):
                require(uxqm__hrkun.attr in ('start', 'step'))
                dadn__epczf = get_definition(func_ir, dadn__epczf.args[0])
                wemi__pbqg = True
            require(find_callname(func_ir, dadn__epczf) == ('slice',
                'builtins'))
            if len(dadn__epczf.args) == 1:
                if uxqm__hrkun.attr == 'start':
                    return 0
                if uxqm__hrkun.attr == 'step':
                    return 1
                require(uxqm__hrkun.attr == 'stop')
                return get_const_value_inner(func_ir, dadn__epczf.args[0],
                    arg_types, typemap, updated_containers)
            if uxqm__hrkun.attr == 'start':
                qundl__rjncb = get_const_value_inner(func_ir, dadn__epczf.
                    args[0], arg_types, typemap, updated_containers)
                if qundl__rjncb is None:
                    qundl__rjncb = 0
                if wemi__pbqg:
                    require(qundl__rjncb == 0)
                return qundl__rjncb
            if uxqm__hrkun.attr == 'stop':
                assert not wemi__pbqg
                return get_const_value_inner(func_ir, dadn__epczf.args[1],
                    arg_types, typemap, updated_containers)
            require(uxqm__hrkun.attr == 'step')
            if len(dadn__epczf.args) == 2:
                return 1
            else:
                qundl__rjncb = get_const_value_inner(func_ir, dadn__epczf.
                    args[2], arg_types, typemap, updated_containers)
                if qundl__rjncb is None:
                    qundl__rjncb = 1
                if wemi__pbqg:
                    require(qundl__rjncb == 1)
                return qundl__rjncb
    if is_expr(uxqm__hrkun, 'getattr'):
        return getattr(get_const_value_inner(func_ir, uxqm__hrkun.value,
            arg_types, typemap, updated_containers), uxqm__hrkun.attr)
    if is_expr(uxqm__hrkun, 'getitem'):
        value = get_const_value_inner(func_ir, uxqm__hrkun.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, uxqm__hrkun.index, arg_types,
            typemap, updated_containers)
        return value[index]
    utaf__qemx = guard(find_callname, func_ir, uxqm__hrkun, typemap)
    if utaf__qemx is not None and len(utaf__qemx) == 2 and utaf__qemx[0
        ] == 'keys' and isinstance(utaf__qemx[1], ir.Var):
        cigp__lkano = uxqm__hrkun.func
        uxqm__hrkun = get_definition(func_ir, utaf__qemx[1])
        cvnnr__dpdd = utaf__qemx[1].name
        if updated_containers and cvnnr__dpdd in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                cvnnr__dpdd, updated_containers[cvnnr__dpdd]))
        require(is_expr(uxqm__hrkun, 'build_map'))
        vals = [ofnmq__egdnz[0] for ofnmq__egdnz in uxqm__hrkun.items]
        eiyv__tus = guard(get_definition, func_ir, cigp__lkano)
        assert isinstance(eiyv__tus, ir.Expr) and eiyv__tus.attr == 'keys'
        eiyv__tus.attr = 'copy'
        return [get_const_value_inner(func_ir, ofnmq__egdnz, arg_types,
            typemap, updated_containers) for ofnmq__egdnz in vals]
    if is_expr(uxqm__hrkun, 'build_map'):
        return {get_const_value_inner(func_ir, ofnmq__egdnz[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            ofnmq__egdnz[1], arg_types, typemap, updated_containers) for
            ofnmq__egdnz in uxqm__hrkun.items}
    if is_expr(uxqm__hrkun, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, ofnmq__egdnz, arg_types,
            typemap, updated_containers) for ofnmq__egdnz in uxqm__hrkun.items)
    if is_expr(uxqm__hrkun, 'build_list'):
        return [get_const_value_inner(func_ir, ofnmq__egdnz, arg_types,
            typemap, updated_containers) for ofnmq__egdnz in uxqm__hrkun.items]
    if is_expr(uxqm__hrkun, 'build_set'):
        return {get_const_value_inner(func_ir, ofnmq__egdnz, arg_types,
            typemap, updated_containers) for ofnmq__egdnz in uxqm__hrkun.items}
    if utaf__qemx == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, uxqm__hrkun.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if utaf__qemx == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, uxqm__hrkun.args[0],
            arg_types, typemap, updated_containers))
    if utaf__qemx == ('range', 'builtins') and len(uxqm__hrkun.args) == 1:
        return range(get_const_value_inner(func_ir, uxqm__hrkun.args[0],
            arg_types, typemap, updated_containers))
    if utaf__qemx == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, ofnmq__egdnz,
            arg_types, typemap, updated_containers) for ofnmq__egdnz in
            uxqm__hrkun.args))
    if utaf__qemx == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, uxqm__hrkun.args[0],
            arg_types, typemap, updated_containers))
    if utaf__qemx == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, uxqm__hrkun.args[0],
            arg_types, typemap, updated_containers))
    if utaf__qemx == ('format', 'builtins'):
        gpxzp__acg = get_const_value_inner(func_ir, uxqm__hrkun.args[0],
            arg_types, typemap, updated_containers)
        xvg__yom = get_const_value_inner(func_ir, uxqm__hrkun.args[1],
            arg_types, typemap, updated_containers) if len(uxqm__hrkun.args
            ) > 1 else ''
        return format(gpxzp__acg, xvg__yom)
    if utaf__qemx in (('init_binary_str_index',
        'bodo.hiframes.pd_index_ext'), ('init_numeric_index',
        'bodo.hiframes.pd_index_ext'), ('init_categorical_index',
        'bodo.hiframes.pd_index_ext'), ('init_datetime_index',
        'bodo.hiframes.pd_index_ext'), ('init_timedelta_index',
        'bodo.hiframes.pd_index_ext'), ('init_heter_index',
        'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, uxqm__hrkun.args[0],
            arg_types, typemap, updated_containers))
    if utaf__qemx == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, uxqm__hrkun.args[0],
            arg_types, typemap, updated_containers))
    if utaf__qemx == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, uxqm__hrkun.
            args[0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, uxqm__hrkun.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            uxqm__hrkun.args[2], arg_types, typemap, updated_containers))
    if utaf__qemx == ('len', 'builtins') and typemap and isinstance(typemap
        .get(uxqm__hrkun.args[0].name, None), types.BaseTuple):
        return len(typemap[uxqm__hrkun.args[0].name])
    if utaf__qemx == ('len', 'builtins'):
        pveiw__praff = guard(get_definition, func_ir, uxqm__hrkun.args[0])
        if isinstance(pveiw__praff, ir.Expr) and pveiw__praff.op in (
            'build_tuple', 'build_list', 'build_set', 'build_map'):
            return len(pveiw__praff.items)
        return len(get_const_value_inner(func_ir, uxqm__hrkun.args[0],
            arg_types, typemap, updated_containers))
    if utaf__qemx == ('CategoricalDtype', 'pandas'):
        kws = dict(uxqm__hrkun.kws)
        qvt__zql = get_call_expr_arg('CategoricalDtype', uxqm__hrkun.args,
            kws, 0, 'categories', '')
        ltele__niui = get_call_expr_arg('CategoricalDtype', uxqm__hrkun.
            args, kws, 1, 'ordered', False)
        if ltele__niui is not False:
            ltele__niui = get_const_value_inner(func_ir, ltele__niui,
                arg_types, typemap, updated_containers)
        if qvt__zql == '':
            qvt__zql = None
        else:
            qvt__zql = get_const_value_inner(func_ir, qvt__zql, arg_types,
                typemap, updated_containers)
        return pd.CategoricalDtype(qvt__zql, ltele__niui)
    if utaf__qemx == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, uxqm__hrkun.args[0],
            arg_types, typemap, updated_containers))
    if utaf__qemx is not None and len(utaf__qemx) == 2 and utaf__qemx[1
        ] == 'pandas' and utaf__qemx[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, utaf__qemx[0])()
    if utaf__qemx is not None and len(utaf__qemx) == 2 and isinstance(
        utaf__qemx[1], ir.Var):
        qundl__rjncb = get_const_value_inner(func_ir, utaf__qemx[1],
            arg_types, typemap, updated_containers)
        args = [get_const_value_inner(func_ir, ofnmq__egdnz, arg_types,
            typemap, updated_containers) for ofnmq__egdnz in uxqm__hrkun.args]
        kws = {bqpcl__pwpiw[0]: get_const_value_inner(func_ir, bqpcl__pwpiw
            [1], arg_types, typemap, updated_containers) for bqpcl__pwpiw in
            uxqm__hrkun.kws}
        return getattr(qundl__rjncb, utaf__qemx[0])(*args, **kws)
    if utaf__qemx is not None and len(utaf__qemx) == 2 and utaf__qemx[1
        ] == 'bodo' and utaf__qemx[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, ofnmq__egdnz, arg_types,
            typemap, updated_containers) for ofnmq__egdnz in uxqm__hrkun.args)
        kwargs = {gfzt__tkozx: get_const_value_inner(func_ir, ofnmq__egdnz,
            arg_types, typemap, updated_containers) for gfzt__tkozx,
            ofnmq__egdnz in dict(uxqm__hrkun.kws).items()}
        return getattr(bodo, utaf__qemx[0])(*args, **kwargs)
    if is_call(uxqm__hrkun) and typemap and isinstance(typemap.get(
        uxqm__hrkun.func.name, None), types.Dispatcher):
        py_func = typemap[uxqm__hrkun.func.name].dispatcher.py_func
        require(uxqm__hrkun.vararg is None)
        args = tuple(get_const_value_inner(func_ir, ofnmq__egdnz, arg_types,
            typemap, updated_containers) for ofnmq__egdnz in uxqm__hrkun.args)
        kwargs = {gfzt__tkozx: get_const_value_inner(func_ir, ofnmq__egdnz,
            arg_types, typemap, updated_containers) for gfzt__tkozx,
            ofnmq__egdnz in dict(uxqm__hrkun.kws).items()}
        arg_types = tuple(bodo.typeof(ofnmq__egdnz) for ofnmq__egdnz in args)
        kw_types = {nrzmk__lfsc: bodo.typeof(ofnmq__egdnz) for nrzmk__lfsc,
            ofnmq__egdnz in kwargs.items()}
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
    f_ir, typemap, vrgv__twq, vrgv__twq = bodo.compiler.get_func_type_info(
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
                    fny__aafkd = guard(get_definition, f_ir, rhs.func)
                    if isinstance(fny__aafkd, ir.Const) and isinstance(
                        fny__aafkd.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    qrsz__sbs = guard(find_callname, f_ir, rhs)
                    if qrsz__sbs is None:
                        return False
                    func_name, zdaw__xohw = qrsz__sbs
                    if zdaw__xohw == 'pandas' and func_name.startswith('read_'
                        ):
                        return False
                    if qrsz__sbs in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if qrsz__sbs == ('File', 'h5py'):
                        return False
                    if isinstance(zdaw__xohw, ir.Var):
                        wpg__sidg = typemap[zdaw__xohw.name]
                        if isinstance(wpg__sidg, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(wpg__sidg, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(wpg__sidg, bodo.LoggingLoggerType):
                            return False
                        if str(wpg__sidg).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            zdaw__xohw), ir.Arg)):
                            return False
                    if zdaw__xohw in ('numpy.random', 'time', 'logging',
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
        wuxk__cqbmk = func.literal_value.code
        pal__who = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            pal__who = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(pal__who, wuxk__cqbmk)
        fix_struct_return(f_ir)
        typemap, myvhx__nzgjf, oqf__kyxvi, vrgv__twq = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, oqf__kyxvi, myvhx__nzgjf = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, oqf__kyxvi, myvhx__nzgjf = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, oqf__kyxvi, myvhx__nzgjf = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(myvhx__nzgjf, types.DictType):
        sfyu__psp = guard(get_struct_keynames, f_ir, typemap)
        if sfyu__psp is not None:
            myvhx__nzgjf = StructType((myvhx__nzgjf.value_type,) * len(
                sfyu__psp), sfyu__psp)
    if is_udf and isinstance(myvhx__nzgjf, (SeriesType,
        HeterogeneousSeriesType)):
        axspu__sobf = numba.core.registry.cpu_target.typing_context
        qnbgl__ybfp = numba.core.registry.cpu_target.target_context
        szz__mkd = bodo.transforms.series_pass.SeriesPass(f_ir, axspu__sobf,
            qnbgl__ybfp, typemap, oqf__kyxvi, {})
        szz__mkd.run()
        szz__mkd.run()
        szz__mkd.run()
        yhf__lmes = compute_cfg_from_blocks(f_ir.blocks)
        isqy__ngohq = [guard(_get_const_series_info, f_ir.blocks[
            nqzb__ctejn], f_ir, typemap) for nqzb__ctejn in yhf__lmes.
            exit_points() if isinstance(f_ir.blocks[nqzb__ctejn].body[-1],
            ir.Return)]
        if None in isqy__ngohq or len(pd.Series(isqy__ngohq).unique()) != 1:
            myvhx__nzgjf.const_info = None
        else:
            myvhx__nzgjf.const_info = isqy__ngohq[0]
    return myvhx__nzgjf


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    ioyq__erh = block.body[-1].value
    scm__lpd = get_definition(f_ir, ioyq__erh)
    require(is_expr(scm__lpd, 'cast'))
    scm__lpd = get_definition(f_ir, scm__lpd.value)
    require(is_call(scm__lpd) and find_callname(f_ir, scm__lpd) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    rkqt__ssyq = scm__lpd.args[1]
    uekr__zgi = tuple(get_const_value_inner(f_ir, rkqt__ssyq, typemap=typemap))
    if isinstance(typemap[ioyq__erh.name], HeterogeneousSeriesType):
        return len(typemap[ioyq__erh.name].data), uekr__zgi
    oyag__rifv = scm__lpd.args[0]
    vzj__gvw = get_definition(f_ir, oyag__rifv)
    func_name, qkn__bvzvk = find_callname(f_ir, vzj__gvw)
    if is_call(vzj__gvw) and bodo.utils.utils.is_alloc_callname(func_name,
        qkn__bvzvk):
        hrlae__puz = vzj__gvw.args[0]
        odfd__vylh = get_const_value_inner(f_ir, hrlae__puz, typemap=typemap)
        return odfd__vylh, uekr__zgi
    if is_call(vzj__gvw) and find_callname(f_ir, vzj__gvw) in [('asarray',
        'numpy'), ('str_arr_from_sequence', 'bodo.libs.str_arr_ext')]:
        oyag__rifv = vzj__gvw.args[0]
        vzj__gvw = get_definition(f_ir, oyag__rifv)
    require(is_expr(vzj__gvw, 'build_tuple') or is_expr(vzj__gvw, 'build_list')
        )
    return len(vzj__gvw.items), uekr__zgi


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    lazu__gvw = []
    qldrg__phl = []
    values = []
    for nrzmk__lfsc, ofnmq__egdnz in build_map.items:
        fvo__bjyu = find_const(f_ir, nrzmk__lfsc)
        require(isinstance(fvo__bjyu, str))
        qldrg__phl.append(fvo__bjyu)
        lazu__gvw.append(nrzmk__lfsc)
        values.append(ofnmq__egdnz)
    afjw__jou = ir.Var(scope, mk_unique_var('val_tup'), loc)
    rxxrf__wlkeh = ir.Assign(ir.Expr.build_tuple(values, loc), afjw__jou, loc)
    f_ir._definitions[afjw__jou.name] = [rxxrf__wlkeh.value]
    cugfm__cmu = ir.Var(scope, mk_unique_var('key_tup'), loc)
    tmac__xrlcl = ir.Assign(ir.Expr.build_tuple(lazu__gvw, loc), cugfm__cmu,
        loc)
    f_ir._definitions[cugfm__cmu.name] = [tmac__xrlcl.value]
    if typemap is not None:
        typemap[afjw__jou.name] = types.Tuple([typemap[ofnmq__egdnz.name] for
            ofnmq__egdnz in values])
        typemap[cugfm__cmu.name] = types.Tuple([typemap[ofnmq__egdnz.name] for
            ofnmq__egdnz in lazu__gvw])
    return qldrg__phl, afjw__jou, rxxrf__wlkeh, cugfm__cmu, tmac__xrlcl


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    zjnk__jft = block.body[-1].value
    xdfd__qcn = guard(get_definition, f_ir, zjnk__jft)
    require(is_expr(xdfd__qcn, 'cast'))
    scm__lpd = guard(get_definition, f_ir, xdfd__qcn.value)
    require(is_expr(scm__lpd, 'build_map'))
    require(len(scm__lpd.items) > 0)
    loc = block.loc
    scope = block.scope
    qldrg__phl, afjw__jou, rxxrf__wlkeh, cugfm__cmu, tmac__xrlcl = (
        extract_keyvals_from_struct_map(f_ir, scm__lpd, loc, scope))
    qbj__jdu = ir.Var(scope, mk_unique_var('conv_call'), loc)
    vkk__ltvm = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), qbj__jdu, loc)
    f_ir._definitions[qbj__jdu.name] = [vkk__ltvm.value]
    moli__rrvxe = ir.Var(scope, mk_unique_var('struct_val'), loc)
    uqaer__xltfj = ir.Assign(ir.Expr.call(qbj__jdu, [afjw__jou, cugfm__cmu],
        {}, loc), moli__rrvxe, loc)
    f_ir._definitions[moli__rrvxe.name] = [uqaer__xltfj.value]
    xdfd__qcn.value = moli__rrvxe
    scm__lpd.items = [(nrzmk__lfsc, nrzmk__lfsc) for nrzmk__lfsc, vrgv__twq in
        scm__lpd.items]
    block.body = block.body[:-2] + [rxxrf__wlkeh, tmac__xrlcl, vkk__ltvm,
        uqaer__xltfj] + block.body[-2:]
    return tuple(qldrg__phl)


def get_struct_keynames(f_ir, typemap):
    yhf__lmes = compute_cfg_from_blocks(f_ir.blocks)
    vdo__daw = list(yhf__lmes.exit_points())[0]
    block = f_ir.blocks[vdo__daw]
    require(isinstance(block.body[-1], ir.Return))
    zjnk__jft = block.body[-1].value
    xdfd__qcn = guard(get_definition, f_ir, zjnk__jft)
    require(is_expr(xdfd__qcn, 'cast'))
    scm__lpd = guard(get_definition, f_ir, xdfd__qcn.value)
    require(is_call(scm__lpd) and find_callname(f_ir, scm__lpd) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[scm__lpd.args[1].name])


def fix_struct_return(f_ir):
    qiz__vte = None
    yhf__lmes = compute_cfg_from_blocks(f_ir.blocks)
    for vdo__daw in yhf__lmes.exit_points():
        qiz__vte = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            vdo__daw], vdo__daw)
    return qiz__vte


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    dmp__fqmlq = ir.Block(ir.Scope(None, loc), loc)
    dmp__fqmlq.body = node_list
    build_definitions({(0): dmp__fqmlq}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(ofnmq__egdnz) for ofnmq__egdnz in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    arz__jts = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(arz__jts, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for ufa__kzvv in range(len(vals) - 1, -1, -1):
        ofnmq__egdnz = vals[ufa__kzvv]
        if isinstance(ofnmq__egdnz, str) and ofnmq__egdnz.startswith(
            NESTED_TUP_SENTINEL):
            xdef__yqj = int(ofnmq__egdnz[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:ufa__kzvv]) + (
                tuple(vals[ufa__kzvv + 1:ufa__kzvv + xdef__yqj + 1]),) +
                tuple(vals[ufa__kzvv + xdef__yqj + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    gpxzp__acg = None
    if len(args) > arg_no and arg_no >= 0:
        gpxzp__acg = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        gpxzp__acg = kws[arg_name]
    if gpxzp__acg is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return gpxzp__acg


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
    zrup__skk = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        zrup__skk.update(extra_globals)
    func.__globals__.update(zrup__skk)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            sbr__ykvd = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[sbr__ykvd.name] = types.literal(default)
            except:
                pass_info.typemap[sbr__ykvd.name] = numba.typeof(default)
            nzzt__svfqf = ir.Assign(ir.Const(default, loc), sbr__ykvd, loc)
            pre_nodes.append(nzzt__svfqf)
            return sbr__ykvd
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    ocrmc__ykgk = tuple(pass_info.typemap[ofnmq__egdnz.name] for
        ofnmq__egdnz in args)
    if const:
        mpqjv__hajde = []
        for ufa__kzvv, gpxzp__acg in enumerate(args):
            qundl__rjncb = guard(find_const, pass_info.func_ir, gpxzp__acg)
            if qundl__rjncb:
                mpqjv__hajde.append(types.literal(qundl__rjncb))
            else:
                mpqjv__hajde.append(ocrmc__ykgk[ufa__kzvv])
        ocrmc__ykgk = tuple(mpqjv__hajde)
    return ReplaceFunc(func, ocrmc__ykgk, args, zrup__skk,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(ckw__ehr) for ckw__ehr in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        awkyb__jdu = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {awkyb__jdu} = 0\n', (awkyb__jdu,)
    if isinstance(t, ArrayItemArrayType):
        uutyt__tnwbn, bzj__zzs = gen_init_varsize_alloc_sizes(t.dtype)
        awkyb__jdu = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {awkyb__jdu} = 0\n' + uutyt__tnwbn, (awkyb__jdu,) + bzj__zzs
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
        return 1 + sum(get_type_alloc_counts(ckw__ehr.dtype) for ckw__ehr in
            t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(ckw__ehr) for ckw__ehr in t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(ckw__ehr) for ckw__ehr in t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    aylvm__tbe = typing_context.resolve_getattr(obj_dtype, func_name)
    if aylvm__tbe is None:
        mdl__qez = types.misc.Module(np)
        try:
            aylvm__tbe = typing_context.resolve_getattr(mdl__qez, func_name)
        except AttributeError as fwfsp__pgq:
            aylvm__tbe = None
        if aylvm__tbe is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return aylvm__tbe


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    aylvm__tbe = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(aylvm__tbe, types.BoundFunction):
        if axis is not None:
            pkhx__iwxca = aylvm__tbe.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            pkhx__iwxca = aylvm__tbe.get_call_type(typing_context, (), {})
        return pkhx__iwxca.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(aylvm__tbe):
            pkhx__iwxca = aylvm__tbe.get_call_type(typing_context, (
                obj_dtype,), {})
            return pkhx__iwxca.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    aylvm__tbe = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(aylvm__tbe, types.BoundFunction):
        kgi__cgm = aylvm__tbe.template
        if axis is not None:
            return kgi__cgm._overload_func(obj_dtype, axis=axis)
        else:
            return kgi__cgm._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    sps__qwtg = get_definition(func_ir, dict_var)
    require(isinstance(sps__qwtg, ir.Expr))
    require(sps__qwtg.op == 'build_map')
    wovss__manqt = sps__qwtg.items
    lazu__gvw = []
    values = []
    qmxy__ikkei = False
    for ufa__kzvv in range(len(wovss__manqt)):
        hvio__nkm, value = wovss__manqt[ufa__kzvv]
        try:
            jwrkf__qpb = get_const_value_inner(func_ir, hvio__nkm,
                arg_types, typemap, updated_containers)
            lazu__gvw.append(jwrkf__qpb)
            values.append(value)
        except GuardException as fwfsp__pgq:
            require_const_map[hvio__nkm] = label
            qmxy__ikkei = True
    if qmxy__ikkei:
        raise GuardException
    return lazu__gvw, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        lazu__gvw = tuple(get_const_value_inner(func_ir, t[0], args) for t in
            build_map.items)
    except GuardException as fwfsp__pgq:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in lazu__gvw):
        raise BodoError(err_msg, loc)
    return lazu__gvw


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    lazu__gvw = _get_const_keys_from_dict(args, func_ir, build_map, err_msg,
        loc)
    luhl__gcaus = []
    yah__qervd = [bodo.transforms.typing_pass._create_const_var(nrzmk__lfsc,
        'dict_key', scope, loc, luhl__gcaus) for nrzmk__lfsc in lazu__gvw]
    lork__cmed = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        zegxu__atqvd = ir.Var(scope, mk_unique_var('sentinel'), loc)
        btfem__hgcp = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        luhl__gcaus.append(ir.Assign(ir.Const('__bodo_tup', loc),
            zegxu__atqvd, loc))
        vow__hlf = [zegxu__atqvd] + yah__qervd + lork__cmed
        luhl__gcaus.append(ir.Assign(ir.Expr.build_tuple(vow__hlf, loc),
            btfem__hgcp, loc))
        return (btfem__hgcp,), luhl__gcaus
    else:
        sltvg__aed = ir.Var(scope, mk_unique_var('values_tup'), loc)
        bav__eoxr = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        luhl__gcaus.append(ir.Assign(ir.Expr.build_tuple(lork__cmed, loc),
            sltvg__aed, loc))
        luhl__gcaus.append(ir.Assign(ir.Expr.build_tuple(yah__qervd, loc),
            bav__eoxr, loc))
        return (sltvg__aed, bav__eoxr), luhl__gcaus
