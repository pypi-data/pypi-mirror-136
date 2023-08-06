"""
Implementation of DataFrame attributes and methods using overload.
"""
import operator
import re
import warnings
from collections import namedtuple
from typing import Tuple
import llvmlite.llvmpy.core as lc
import numba
import numpy as np
import pandas as pd
from numba.core import cgutils, ir, types
from numba.core.imputils import RefType, impl_ret_borrowed, impl_ret_new_ref, iternext_impl, lower_builtin
from numba.core.ir_utils import mk_unique_var, next_label
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import models, overload, overload_attribute, overload_method, register_model, type_callable
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import _no_input, datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported, handle_inplace_df_type_change
from bodo.hiframes.pd_index_ext import StringIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType, if_series_to_array_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils.transform import bodo_types_with_params, gen_const_tup, no_side_effect_call_tuples
from bodo.utils.typing import BodoError, BodoWarning, check_unsupported_args, dtype_to_array_type, ensure_constant_arg, ensure_constant_values, get_index_data_arr_types, get_index_names, get_literal_value, get_nullable_and_non_nullable_types, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_tuple, get_overload_constant_dict, get_overload_constant_series, is_common_scalar_dtype, is_literal_type, is_overload_bool, is_overload_bool_list, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_int, is_overload_constant_list, is_overload_constant_series, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, parse_dtype, raise_bodo_error, raise_const_error, unliteral_val
from bodo.utils.utils import is_array_typ


@overload_attribute(DataFrameType, 'index', inline='always')
def overload_dataframe_index(df):
    return lambda df: bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)


def generate_col_to_index_func_text(col_names: Tuple):
    if all(isinstance(a, str) for a in col_names) or all(isinstance(a,
        bytes) for a in col_names):
        gyhv__bcvbr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({gyhv__bcvbr})\n'
            )
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    check_runtime_cols_unsupported(df, 'DataFrame.columns')
    zxfdb__tfq = 'def impl(df):\n'
    efu__ebqa = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    zxfdb__tfq += f'  return {efu__ebqa}'
    zseir__wkn = {}
    exec(zxfdb__tfq, {'bodo': bodo}, zseir__wkn)
    impl = zseir__wkn['impl']
    return impl


@overload_attribute(DataFrameType, 'values')
def overload_dataframe_values(df):
    check_runtime_cols_unsupported(df, 'DataFrame.values')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.values: only supported for dataframes containing numeric values'
            )
    izt__cyza = len(df.columns)
    byb__liayy = set(i for i in range(izt__cyza) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in byb__liayy else '') for i in
        range(izt__cyza))
    zxfdb__tfq = 'def f(df):\n'.format()
    zxfdb__tfq += '    return np.stack(({},), 1)\n'.format(data_args)
    zseir__wkn = {}
    exec(zxfdb__tfq, {'bodo': bodo, 'np': np}, zseir__wkn)
    elrik__cky = zseir__wkn['f']
    return elrik__cky


@overload_method(DataFrameType, 'to_numpy', inline='always', no_unliteral=True)
def overload_dataframe_to_numpy(df, dtype=None, copy=False, na_value=_no_input
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.to_numpy()')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.to_numpy(): only supported for dataframes containing numeric values'
            )
    hsb__hzwsd = {'dtype': dtype, 'na_value': na_value}
    kwyqc__leuzd = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', hsb__hzwsd, kwyqc__leuzd,
        package_name='pandas', module_name='DataFrame')

    def impl(df, dtype=None, copy=False, na_value=_no_input):
        return df.values
    return impl


@overload_attribute(DataFrameType, 'ndim', inline='always')
def overload_dataframe_ndim(df):
    return lambda df: 2


@overload_attribute(DataFrameType, 'size')
def overload_dataframe_size(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            fst__cvws = bodo.hiframes.table.compute_num_runtime_columns(t)
            return fst__cvws * len(t)
        return impl
    ncols = len(df.columns)
    return lambda df: ncols * len(df)


@overload_attribute(DataFrameType, 'shape')
def overload_dataframe_shape(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            fst__cvws = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), fst__cvws
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), types.int64(ncols))


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    zxfdb__tfq = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    haizl__vkeef = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    zxfdb__tfq += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{haizl__vkeef}), {index}, None)
"""
    zseir__wkn = {}
    exec(zxfdb__tfq, {'bodo': bodo}, zseir__wkn)
    impl = zseir__wkn['impl']
    return impl


@overload_attribute(DataFrameType, 'empty')
def overload_dataframe_empty(df):
    check_runtime_cols_unsupported(df, 'DataFrame.empty')
    if len(df.columns) == 0:
        return lambda df: True
    return lambda df: len(df) == 0


@overload_method(DataFrameType, 'assign', no_unliteral=True)
def overload_dataframe_assign(df, **kwargs):
    check_runtime_cols_unsupported(df, 'DataFrame.assign()')
    raise_bodo_error('Invalid df.assign() call')


@overload_method(DataFrameType, 'insert', no_unliteral=True)
def overload_dataframe_insert(df, loc, column, value, allow_duplicates=False):
    check_runtime_cols_unsupported(df, 'DataFrame.insert()')
    raise_bodo_error('Invalid df.insert() call')


def _get_dtype_str(dtype):
    if isinstance(dtype, types.Function):
        if dtype.key[0] == str:
            return "'str'"
        elif dtype.key[0] == float:
            return 'float'
        elif dtype.key[0] == int:
            return 'int'
        elif dtype.key[0] == bool:
            return 'bool'
        else:
            raise BodoError(f'invalid dtype: {dtype}')
    if isinstance(dtype, types.DTypeSpec):
        dtype = dtype.dtype
    if isinstance(dtype, types.functions.NumberClass):
        return f"'{dtype.key}'"
    if dtype in (bodo.libs.str_arr_ext.string_dtype, pd.StringDtype()):
        return 'str'
    return f"'{dtype}'"


@overload_method(DataFrameType, 'astype', inline='always', no_unliteral=True)
def overload_dataframe_astype(df, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True):
    check_runtime_cols_unsupported(df, 'DataFrame.astype()')
    hsb__hzwsd = {'copy': copy, 'errors': errors}
    kwyqc__leuzd = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', hsb__hzwsd, kwyqc__leuzd,
        package_name='pandas', module_name='DataFrame')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "DataFrame.astype(): 'dtype' when passed as string must be a constant value"
            )
    if is_overload_constant_dict(dtype) or is_overload_constant_series(dtype):
        ohi__plhf = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(ohi__plhf[aavn__hcyl])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             if aavn__hcyl in ohi__plhf else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})' for
            i, aavn__hcyl in enumerate(df.columns))
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    header = (
        "def impl(df, dtype, copy=True, errors='raise', _bodo_nan_to_str=True):\n"
        )
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'copy', inline='always', no_unliteral=True)
def overload_dataframe_copy(df, deep=True):
    check_runtime_cols_unsupported(df, 'DataFrame.copy()')
    cimm__qywpa = []
    for i in range(len(df.columns)):
        arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
        if is_overload_true(deep):
            cimm__qywpa.append(arr + '.copy()')
        elif is_overload_false(deep):
            cimm__qywpa.append(arr)
        else:
            cimm__qywpa.append(f'{arr}.copy() if deep else {arr}')
    header = 'def impl(df, deep=True):\n'
    return _gen_init_df(header, df.columns, ', '.join(cimm__qywpa))


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    hsb__hzwsd = {'index': index, 'level': level, 'errors': errors}
    kwyqc__leuzd = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', hsb__hzwsd, kwyqc__leuzd,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.rename(): 'inplace' keyword only supports boolean constant assignment"
            )
    if not is_overload_none(mapper):
        if not is_overload_none(columns):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'mapper' and 'columns'"
                )
        if not (is_overload_constant_int(axis) and get_overload_const_int(
            axis) == 1):
            raise BodoError(
                "DataFrame.rename(): 'mapper' only supported with axis=1")
        if not is_overload_constant_dict(mapper):
            raise_bodo_error(
                "'mapper' argument to DataFrame.rename() should be a constant dictionary"
                )
        zbvbt__izgb = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        zbvbt__izgb = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    ael__gcuay = [zbvbt__izgb.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))]
    cimm__qywpa = []
    for i in range(len(df.columns)):
        arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
        if is_overload_true(copy):
            cimm__qywpa.append(arr + '.copy()')
        elif is_overload_false(copy):
            cimm__qywpa.append(arr)
        else:
            cimm__qywpa.append(f'{arr}.copy() if copy else {arr}')
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    return _gen_init_df(header, ael__gcuay, ', '.join(cimm__qywpa))


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    zakr__cfso = not is_overload_none(items)
    jxs__khx = not is_overload_none(like)
    qxdau__ibqa = not is_overload_none(regex)
    aqunq__biy = zakr__cfso ^ jxs__khx ^ qxdau__ibqa
    vskg__royt = not (zakr__cfso or jxs__khx or qxdau__ibqa)
    if vskg__royt:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not aqunq__biy:
        raise BodoError(
            'DataFrame.filter(): keyword arguments `items`, `like`, and `regex` are mutually exclusive'
            )
    if is_overload_none(axis):
        axis = 'columns'
    if is_overload_constant_str(axis):
        axis = get_overload_const_str(axis)
        if axis not in {'index', 'columns'}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either "index" or "columns" if string'
                )
        tjxo__zhdh = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        tjxo__zhdh = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert tjxo__zhdh in {0, 1}
    zxfdb__tfq = (
        'def impl(df, items=None, like=None, regex=None, axis=None):\n')
    if tjxo__zhdh == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if tjxo__zhdh == 1:
        iwxin__sgu = []
        pgsi__smfi = []
        cpnec__isr = []
        if zakr__cfso:
            if is_overload_constant_list(items):
                uoi__qoguk = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if jxs__khx:
            if is_overload_constant_str(like):
                tmawi__jleya = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if qxdau__ibqa:
            if is_overload_constant_str(regex):
                foc__jsjeo = get_overload_const_str(regex)
                asx__hfi = re.compile(foc__jsjeo)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, aavn__hcyl in enumerate(df.columns):
            if not is_overload_none(items
                ) and aavn__hcyl in uoi__qoguk or not is_overload_none(like
                ) and tmawi__jleya in str(aavn__hcyl) or not is_overload_none(
                regex) and asx__hfi.search(str(aavn__hcyl)):
                pgsi__smfi.append(aavn__hcyl)
                cpnec__isr.append(i)
        for i in cpnec__isr:
            vgsqy__fosoq = f'data_{i}'
            iwxin__sgu.append(vgsqy__fosoq)
            zxfdb__tfq += f"""  {vgsqy__fosoq} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(iwxin__sgu)
        return _gen_init_df(zxfdb__tfq, pgsi__smfi, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'select_dtypes', inline='always',
    no_unliteral=True)
def overload_dataframe_select_dtypes(df, include=None, exclude=None):
    check_runtime_cols_unsupported(df, 'DataFrame.select_dtypes')
    nne__alr = is_overload_none(include)
    hwrue__owb = is_overload_none(exclude)
    ohf__rigjn = 'DataFrame.select_dtypes'
    if nne__alr and hwrue__owb:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not nne__alr:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            eda__wfle = [dtype_to_array_type(parse_dtype(elem, ohf__rigjn)) for
                elem in include]
        elif is_legal_input(include):
            eda__wfle = [dtype_to_array_type(parse_dtype(include, ohf__rigjn))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        eda__wfle = get_nullable_and_non_nullable_types(eda__wfle)
        jutol__cdmfj = tuple(aavn__hcyl for i, aavn__hcyl in enumerate(df.
            columns) if df.data[i] in eda__wfle)
    else:
        jutol__cdmfj = df.columns
    if not hwrue__owb:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            ilbss__fyu = [dtype_to_array_type(parse_dtype(elem, ohf__rigjn)
                ) for elem in exclude]
        elif is_legal_input(exclude):
            ilbss__fyu = [dtype_to_array_type(parse_dtype(exclude, ohf__rigjn))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        ilbss__fyu = get_nullable_and_non_nullable_types(ilbss__fyu)
        jutol__cdmfj = tuple(aavn__hcyl for aavn__hcyl in jutol__cdmfj if 
            df.data[df.columns.index(aavn__hcyl)] not in ilbss__fyu)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(aavn__hcyl)})'
         for aavn__hcyl in jutol__cdmfj)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, jutol__cdmfj, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})) == False'
         for i in range(len(df.columns)))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_head(df, n=5):
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:n]' for
        i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:n]'
    return _gen_init_df(header, df.columns, data_args, index)


@lower_builtin('df.head', DataFrameType, types.Integer)
@lower_builtin('df.head', DataFrameType, types.Omitted)
def dataframe_head_lower(context, builder, sig, args):
    impl = overload_dataframe_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'tail', inline='always', no_unliteral=True)
def overload_dataframe_tail(df, n=5):
    check_runtime_cols_unsupported(df, 'DataFrame.tail()')
    if not is_overload_int(n):
        raise BodoError("Dataframe.tail(): 'n' must be an Integer")
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[m:]' for
        i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    header += '  m = bodo.hiframes.series_impl.tail_slice(len(df), n)\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[m:]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'first', inline='always', no_unliteral=True)
def overload_dataframe_first(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.first()')
    tvyne__ymp = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in tvyne__ymp:
        raise BodoError(
            "DataFrame.first(): 'offset' must be an string or DateOffset")
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:valid_entries]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:valid_entries]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    start_date = df_index[0]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, start_date, False)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'last', inline='always', no_unliteral=True)
def overload_dataframe_last(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.last()')
    tvyne__ymp = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in tvyne__ymp:
        raise BodoError(
            "DataFrame.last(): 'offset' must be an string or DateOffset")
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[len(df)-valid_entries:]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[len(df)-valid_entries:]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    final_date = df_index[-1]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, final_date, True)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'to_string', no_unliteral=True)
def to_string_overload(df, buf=None, columns=None, col_space=None, header=
    True, index=True, na_rep='NaN', formatters=None, float_format=None,
    sparsify=None, index_names=True, justify=None, max_rows=None, min_rows=
    None, max_cols=None, show_dimensions=False, decimal='.', line_width=
    None, max_colwidth=None, encoding=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_string()')

    def impl(df, buf=None, columns=None, col_space=None, header=True, index
        =True, na_rep='NaN', formatters=None, float_format=None, sparsify=
        None, index_names=True, justify=None, max_rows=None, min_rows=None,
        max_cols=None, show_dimensions=False, decimal='.', line_width=None,
        max_colwidth=None, encoding=None):
        with numba.objmode(res='string'):
            res = df.to_string(buf=buf, columns=columns, col_space=
                col_space, header=header, index=index, na_rep=na_rep,
                formatters=formatters, float_format=float_format, sparsify=
                sparsify, index_names=index_names, justify=justify,
                max_rows=max_rows, min_rows=min_rows, max_cols=max_cols,
                show_dimensions=show_dimensions, decimal=decimal,
                line_width=line_width, max_colwidth=max_colwidth, encoding=
                encoding)
        return res
    return impl


@overload_method(DataFrameType, 'isin', inline='always', no_unliteral=True)
def overload_dataframe_isin(df, values):
    check_runtime_cols_unsupported(df, 'DataFrame.isin()')
    from bodo.utils.typing import is_iterable_type
    zxfdb__tfq = 'def impl(df, values):\n'
    aey__lwxhh = {}
    fwvyz__zjqo = False
    if isinstance(values, DataFrameType):
        fwvyz__zjqo = True
        for i, aavn__hcyl in enumerate(df.columns):
            if aavn__hcyl in values.columns:
                omh__sxw = 'val{}'.format(i)
                zxfdb__tfq += (
                    """  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {})
"""
                    .format(omh__sxw, values.columns.index(aavn__hcyl)))
                aey__lwxhh[aavn__hcyl] = omh__sxw
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        aey__lwxhh = {aavn__hcyl: 'values' for aavn__hcyl in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        omh__sxw = 'data{}'.format(i)
        zxfdb__tfq += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(omh__sxw, i))
        data.append(omh__sxw)
    xlfz__vfso = ['out{}'.format(i) for i in range(len(df.columns))]
    vsr__bmch = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    xldl__jkf = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    unxz__pey = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, rsr__todam) in enumerate(zip(df.columns, data)):
        if cname in aey__lwxhh:
            zwenl__psl = aey__lwxhh[cname]
            if fwvyz__zjqo:
                zxfdb__tfq += vsr__bmch.format(rsr__todam, zwenl__psl,
                    xlfz__vfso[i])
            else:
                zxfdb__tfq += xldl__jkf.format(rsr__todam, zwenl__psl,
                    xlfz__vfso[i])
        else:
            zxfdb__tfq += unxz__pey.format(xlfz__vfso[i])
    return _gen_init_df(zxfdb__tfq, df.columns, ','.join(xlfz__vfso))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    izt__cyza = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(izt__cyza))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    hbpl__ucc = [aavn__hcyl for aavn__hcyl, dfljv__xjj in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(dfljv__xjj.
        dtype)]
    assert len(hbpl__ucc) != 0
    qvn__hfzg = ''
    if not any(dfljv__xjj == types.float64 for dfljv__xjj in df.data):
        qvn__hfzg = '.astype(np.float64)'
    dya__aryk = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.columns.index(aavn__hcyl), '.astype(np.float64)' if 
        isinstance(df.data[df.columns.index(aavn__hcyl)], IntegerArrayType) or
        df.data[df.columns.index(aavn__hcyl)] == boolean_array else '') for
        aavn__hcyl in hbpl__ucc)
    gvvnf__muoa = 'np.stack(({},), 1){}'.format(dya__aryk, qvn__hfzg)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(hbpl__ucc)))
    index = f'{generate_col_to_index_func_text(hbpl__ucc)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(gvvnf__muoa)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, hbpl__ucc, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    wiaw__wdsoy = dict(ddof=ddof)
    kxufd__czm = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    chtu__pcgme = '1' if is_overload_none(min_periods) else 'min_periods'
    hbpl__ucc = [aavn__hcyl for aavn__hcyl, dfljv__xjj in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(dfljv__xjj.
        dtype)]
    if len(hbpl__ucc) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    qvn__hfzg = ''
    if not any(dfljv__xjj == types.float64 for dfljv__xjj in df.data):
        qvn__hfzg = '.astype(np.float64)'
    dya__aryk = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.columns.index(aavn__hcyl), '.astype(np.float64)' if 
        isinstance(df.data[df.columns.index(aavn__hcyl)], IntegerArrayType) or
        df.data[df.columns.index(aavn__hcyl)] == boolean_array else '') for
        aavn__hcyl in hbpl__ucc)
    gvvnf__muoa = 'np.stack(({},), 1){}'.format(dya__aryk, qvn__hfzg)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(hbpl__ucc)))
    index = f'pd.Index({hbpl__ucc})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(gvvnf__muoa)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        chtu__pcgme)
    return _gen_init_df(header, hbpl__ucc, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    wiaw__wdsoy = dict(axis=axis, level=level, numeric_only=numeric_only)
    kxufd__czm = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    zxfdb__tfq = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    zxfdb__tfq += '  data = np.array([{}])\n'.format(data_args)
    efu__ebqa = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    zxfdb__tfq += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {efu__ebqa})\n'
        )
    zseir__wkn = {}
    exec(zxfdb__tfq, {'bodo': bodo, 'np': np}, zseir__wkn)
    impl = zseir__wkn['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    wiaw__wdsoy = dict(axis=axis)
    kxufd__czm = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    zxfdb__tfq = 'def impl(df, axis=0, dropna=True):\n'
    zxfdb__tfq += '  data = np.asarray(({},))\n'.format(data_args)
    efu__ebqa = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    zxfdb__tfq += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {efu__ebqa})\n'
        )
    zseir__wkn = {}
    exec(zxfdb__tfq, {'bodo': bodo, 'np': np}, zseir__wkn)
    impl = zseir__wkn['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    wiaw__wdsoy = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    kxufd__czm = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    wiaw__wdsoy = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    kxufd__czm = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    wiaw__wdsoy = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    kxufd__czm = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    wiaw__wdsoy = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    kxufd__czm = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    wiaw__wdsoy = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    kxufd__czm = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    wiaw__wdsoy = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    kxufd__czm = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    wiaw__wdsoy = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    kxufd__czm = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    wiaw__wdsoy = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    kxufd__czm = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    wiaw__wdsoy = dict(numeric_only=numeric_only, interpolation=interpolation)
    kxufd__czm = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    wiaw__wdsoy = dict(axis=axis, skipna=skipna)
    kxufd__czm = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    for sepb__vjgt in df.data:
        if not (bodo.utils.utils.is_np_array_typ(sepb__vjgt) and (
            sepb__vjgt.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(sepb__vjgt.dtype, (types.Number, types.Boolean))) or
            isinstance(sepb__vjgt, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or sepb__vjgt in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {sepb__vjgt} not supported.'
                )
        if isinstance(sepb__vjgt, bodo.CategoricalArrayType
            ) and not sepb__vjgt.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    wiaw__wdsoy = dict(axis=axis, skipna=skipna)
    kxufd__czm = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    for sepb__vjgt in df.data:
        if not (bodo.utils.utils.is_np_array_typ(sepb__vjgt) and (
            sepb__vjgt.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(sepb__vjgt.dtype, (types.Number, types.Boolean))) or
            isinstance(sepb__vjgt, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or sepb__vjgt in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {sepb__vjgt} not supported.'
                )
        if isinstance(sepb__vjgt, bodo.CategoricalArrayType
            ) and not sepb__vjgt.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmin(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmin', axis=axis)


@overload_method(DataFrameType, 'infer_objects', inline='always')
def overload_dataframe_infer_objects(df):
    check_runtime_cols_unsupported(df, 'DataFrame.infer_objects()')
    return lambda df: df.copy()


def _gen_reduce_impl(df, func_name, args=None, axis=None):
    args = '' if is_overload_none(args) else args
    if is_overload_none(axis):
        axis = 0
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
    else:
        raise_bodo_error(
            f'DataFrame.{func_name}: axis must be a constant Integer')
    assert axis in (0, 1), f'invalid axis argument for DataFrame.{func_name}'
    if func_name in ('idxmax', 'idxmin'):
        out_colnames = df.columns
    else:
        hbpl__ucc = tuple(aavn__hcyl for aavn__hcyl, dfljv__xjj in zip(df.
            columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype
            (dfljv__xjj.dtype))
        out_colnames = hbpl__ucc
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            cbw__hcd = [numba.np.numpy_support.as_dtype(df.data[df.columns.
                index(aavn__hcyl)].dtype) for aavn__hcyl in out_colnames]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(cbw__hcd, []))
    except NotImplementedError as trea__zex:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    akv__oqvd = ''
    if func_name in ('sum', 'prod'):
        akv__oqvd = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    zxfdb__tfq = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, akv__oqvd))
    if func_name == 'quantile':
        zxfdb__tfq = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        zxfdb__tfq = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        zxfdb__tfq += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        zxfdb__tfq += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    zseir__wkn = {}
    exec(zxfdb__tfq, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        zseir__wkn)
    impl = zseir__wkn['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    ixgof__ihfon = ''
    if func_name in ('min', 'max'):
        ixgof__ihfon = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        ixgof__ihfon = ', dtype=np.float32'
    ncy__btq = f'bodo.libs.array_ops.array_op_{func_name}'
    zie__dkhdw = ''
    if func_name in ['sum', 'prod']:
        zie__dkhdw = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        zie__dkhdw = 'index'
    elif func_name == 'quantile':
        zie__dkhdw = 'q'
    elif func_name in ['std', 'var']:
        zie__dkhdw = 'True, ddof'
    elif func_name == 'median':
        zie__dkhdw = 'True'
    data_args = ', '.join(
        f'{ncy__btq}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(aavn__hcyl)}), {zie__dkhdw})'
         for aavn__hcyl in out_colnames)
    zxfdb__tfq = ''
    if func_name in ('idxmax', 'idxmin'):
        zxfdb__tfq += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        zxfdb__tfq += (
            '  data = bodo.utils.conversion.coerce_to_array(({},))\n'.
            format(data_args))
    else:
        zxfdb__tfq += '  data = np.asarray(({},){})\n'.format(data_args,
            ixgof__ihfon)
    zxfdb__tfq += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return zxfdb__tfq


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    emiie__lca = [df_type.columns.index(aavn__hcyl) for aavn__hcyl in
        out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in emiie__lca)
    ptvw__bnnjt = '\n        '.join(f'row[{i}] = arr_{emiie__lca[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    aut__rtv = f'len(arr_{emiie__lca[0]})'
    lxmt__ijdl = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in lxmt__ijdl:
        ahbuw__heja = lxmt__ijdl[func_name]
        alrg__ekyuk = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        zxfdb__tfq = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {aut__rtv}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{alrg__ekyuk})
    for i in numba.parfors.parfor.internal_prange(n):
        {ptvw__bnnjt}
        A[i] = {ahbuw__heja}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return zxfdb__tfq
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    wiaw__wdsoy = dict(fill_method=fill_method, limit=limit, freq=freq)
    kxufd__czm = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.hiframes.rolling.pct_change(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = (
        "def impl(df, periods=1, fill_method='pad', limit=None, freq=None):\n")
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumprod', inline='always', no_unliteral=True)
def overload_dataframe_cumprod(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumprod()')
    wiaw__wdsoy = dict(axis=axis, skipna=skipna)
    kxufd__czm = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumprod()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumsum', inline='always', no_unliteral=True)
def overload_dataframe_cumsum(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumsum()')
    wiaw__wdsoy = dict(skipna=skipna)
    kxufd__czm = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumsum()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


def _is_describe_type(data):
    return isinstance(data, IntegerArrayType) or isinstance(data, types.Array
        ) and isinstance(data.dtype, types.Number
        ) or data.dtype == bodo.datetime64ns


@overload_method(DataFrameType, 'describe', inline='always', no_unliteral=True)
def overload_dataframe_describe(df, percentiles=None, include=None, exclude
    =None, datetime_is_numeric=True):
    check_runtime_cols_unsupported(df, 'DataFrame.describe()')
    wiaw__wdsoy = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    kxufd__czm = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    hbpl__ucc = [aavn__hcyl for aavn__hcyl, dfljv__xjj in zip(df.columns,
        df.data) if _is_describe_type(dfljv__xjj)]
    if len(hbpl__ucc) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    mpv__ojmeg = sum(df.data[df.columns.index(aavn__hcyl)].dtype == bodo.
        datetime64ns for aavn__hcyl in hbpl__ucc)

    def _get_describe(col_ind):
        kajx__sagyk = df.data[col_ind].dtype == bodo.datetime64ns
        if mpv__ojmeg and mpv__ojmeg != len(hbpl__ucc):
            if kajx__sagyk:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for aavn__hcyl in hbpl__ucc:
        col_ind = df.columns.index(aavn__hcyl)
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.columns.index(aavn__hcyl)) for
        aavn__hcyl in hbpl__ucc)
    izl__nnhoq = "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']"
    if mpv__ojmeg == len(hbpl__ucc):
        izl__nnhoq = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif mpv__ojmeg:
        izl__nnhoq = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({izl__nnhoq})'
    return _gen_init_df(header, hbpl__ucc, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    wiaw__wdsoy = dict(axis=axis, convert=convert, is_copy=is_copy)
    kxufd__czm = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[indices_t]'
        .format(i) for i in range(len(df.columns)))
    header = 'def impl(df, indices, axis=0, convert=None, is_copy=True):\n'
    header += (
        '  indices_t = bodo.utils.conversion.coerce_to_ndarray(indices)\n')
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[indices_t]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'shift', inline='always', no_unliteral=True)
def overload_dataframe_shift(df, periods=1, freq=None, axis=0, fill_value=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.shift()')
    wiaw__wdsoy = dict(freq=freq, axis=axis, fill_value=fill_value)
    kxufd__czm = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    for glhlf__mfos in df.data:
        if not is_supported_shift_array_type(glhlf__mfos):
            raise BodoError(
                f'Dataframe.shift() column input type {glhlf__mfos.dtype} not supported yet.'
                )
    if not is_overload_int(periods):
        raise BodoError(
            "DataFrame.shift(): 'periods' input must be an integer.")
    data_args = ', '.join(
        f'bodo.hiframes.rolling.shift(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = 'def impl(df, periods=1, freq=None, axis=0, fill_value=None):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'diff', inline='always', no_unliteral=True)
def overload_dataframe_diff(df, periods=1, axis=0):
    check_runtime_cols_unsupported(df, 'DataFrame.diff()')
    wiaw__wdsoy = dict(axis=axis)
    kxufd__czm = dict(axis=0)
    check_unsupported_args('DataFrame.diff', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    for glhlf__mfos in df.data:
        if not (isinstance(glhlf__mfos, types.Array) and (isinstance(
            glhlf__mfos.dtype, types.Number) or glhlf__mfos.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {glhlf__mfos.dtype} not supported.'
                )
    if not is_overload_int(periods):
        raise BodoError("DataFrame.diff(): 'periods' input must be an integer."
            )
    header = 'def impl(df, periods=1, axis= 0):\n'
    for i in range(len(df.columns)):
        header += (
            f'  data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    data_args = ', '.join(
        f'bodo.hiframes.series_impl.dt64_arr_sub(data_{i}, bodo.hiframes.rolling.shift(data_{i}, periods, False))'
         if df.data[i] == types.Array(bodo.datetime64ns, 1, 'C') else
        f'data_{i} - bodo.hiframes.rolling.shift(data_{i}, periods, False)' for
        i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'set_index', inline='always', no_unliteral=True
    )
def overload_dataframe_set_index(df, keys, drop=True, append=False, inplace
    =False, verify_integrity=False):
    check_runtime_cols_unsupported(df, 'DataFrame.set_index()')
    hsb__hzwsd = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    kwyqc__leuzd = {'inplace': False, 'append': False, 'verify_integrity': 
        False}
    check_unsupported_args('DataFrame.set_index', hsb__hzwsd, kwyqc__leuzd,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_str(keys):
        raise_bodo_error(
            "DataFrame.set_index(): 'keys' must be a constant string")
    col_name = get_overload_const_str(keys)
    col_ind = df.columns.index(col_name)
    if len(df.columns) == 1:
        raise BodoError(
            'DataFrame.set_index(): Not supported on single column DataFrames.'
            )
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'.format(
        i) for i in range(len(df.columns)) if i != col_ind)
    header = """def impl(df, keys, drop=True, append=False, inplace=False, verify_integrity=False):
"""
    columns = tuple(aavn__hcyl for aavn__hcyl in df.columns if aavn__hcyl !=
        col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    hsb__hzwsd = {'inplace': inplace}
    kwyqc__leuzd = {'inplace': False}
    check_unsupported_args('query', hsb__hzwsd, kwyqc__leuzd, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        tjb__ehfg = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[tjb__ehfg]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    hsb__hzwsd = {'subset': subset, 'keep': keep}
    kwyqc__leuzd = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', hsb__hzwsd, kwyqc__leuzd,
        package_name='pandas', module_name='DataFrame')
    izt__cyza = len(df.columns)
    zxfdb__tfq = "def impl(df, subset=None, keep='first'):\n"
    for i in range(izt__cyza):
        zxfdb__tfq += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    zxfdb__tfq += (
        '  duplicated, index_arr = bodo.libs.array_kernels.duplicated(({},), {})\n'
        .format(', '.join('data_{}'.format(i) for i in range(izt__cyza)),
        index))
    zxfdb__tfq += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    zxfdb__tfq += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    zseir__wkn = {}
    exec(zxfdb__tfq, {'bodo': bodo}, zseir__wkn)
    impl = zseir__wkn['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    hsb__hzwsd = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    kwyqc__leuzd = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    zqxia__jtdym = []
    if is_overload_constant_list(subset):
        zqxia__jtdym = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        zqxia__jtdym = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        zqxia__jtdym = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    nggfd__vcwhi = []
    for col_name in zqxia__jtdym:
        if col_name not in df.columns:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        nggfd__vcwhi.append(df.columns.index(col_name))
    check_unsupported_args('DataFrame.drop_duplicates', hsb__hzwsd,
        kwyqc__leuzd, package_name='pandas', module_name='DataFrame')
    qkeb__burb = []
    if nggfd__vcwhi:
        for grss__giz in nggfd__vcwhi:
            if isinstance(df.data[grss__giz], bodo.MapArrayType):
                qkeb__burb.append(df.columns[grss__giz])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                qkeb__burb.append(col_name)
    if qkeb__burb:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {qkeb__burb} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    izt__cyza = len(df.columns)
    mbdg__ufaf = ['data_{}'.format(i) for i in nggfd__vcwhi]
    husa__iaooa = ['data_{}'.format(i) for i in range(izt__cyza) if i not in
        nggfd__vcwhi]
    if mbdg__ufaf:
        fzy__lcbhw = len(mbdg__ufaf)
    else:
        fzy__lcbhw = izt__cyza
    yymp__miy = ', '.join(mbdg__ufaf + husa__iaooa)
    data_args = ', '.join('data_{}'.format(i) for i in range(izt__cyza))
    zxfdb__tfq = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(izt__cyza):
        zxfdb__tfq += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    zxfdb__tfq += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(yymp__miy, index, fzy__lcbhw))
    zxfdb__tfq += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(zxfdb__tfq, df.columns, data_args, 'index')


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None,
    out_df_type=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    if out_df_type is not None:
        extra_globals['out_df_type'] = out_df_type
        glr__zny = 'out_df_type'
    else:
        glr__zny = gen_const_tup(columns)
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    zxfdb__tfq = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, {glr__zny})
"""
    zseir__wkn = {}
    aao__bgfgt = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba}
    aao__bgfgt.update(extra_globals)
    exec(zxfdb__tfq, aao__bgfgt, zseir__wkn)
    impl = zseir__wkn['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        kygj__xrjtx = pd.Index(lhs.columns)
        xof__bbfpf = pd.Index(rhs.columns)
        zonsw__fdxj, hpcky__pitli, sisdn__sjk = kygj__xrjtx.join(xof__bbfpf,
            how='left' if is_inplace else 'outer', level=None,
            return_indexers=True)
        return tuple(zonsw__fdxj), hpcky__pitli, sisdn__sjk
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        har__mex = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        qywwf__emxfd = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, har__mex)
        check_runtime_cols_unsupported(rhs, har__mex)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                zonsw__fdxj, hpcky__pitli, sisdn__sjk = _get_binop_columns(lhs,
                    rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {lqhxp__pnmxy}) {har__mex}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {itv__padiu})'
                     if lqhxp__pnmxy != -1 and itv__padiu != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for lqhxp__pnmxy, itv__padiu in zip(hpcky__pitli,
                    sisdn__sjk))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, zonsw__fdxj, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            lfzmv__uoon = []
            yleq__vbf = []
            if op in qywwf__emxfd:
                for i, wmtlz__eplw in enumerate(lhs.data):
                    if is_common_scalar_dtype([wmtlz__eplw.dtype, rhs]):
                        lfzmv__uoon.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {har__mex} rhs'
                            )
                    else:
                        zaoh__wpkk = f'arr{i}'
                        yleq__vbf.append(zaoh__wpkk)
                        lfzmv__uoon.append(zaoh__wpkk)
                data_args = ', '.join(lfzmv__uoon)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {har__mex} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(yleq__vbf) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {zaoh__wpkk} = np.empty(n, dtype=np.bool_)\n' for
                    zaoh__wpkk in yleq__vbf)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(zaoh__wpkk, 
                    op == operator.ne) for zaoh__wpkk in yleq__vbf)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            lfzmv__uoon = []
            yleq__vbf = []
            if op in qywwf__emxfd:
                for i, wmtlz__eplw in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, wmtlz__eplw.dtype]):
                        lfzmv__uoon.append(
                            f'lhs {har__mex} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        zaoh__wpkk = f'arr{i}'
                        yleq__vbf.append(zaoh__wpkk)
                        lfzmv__uoon.append(zaoh__wpkk)
                data_args = ', '.join(lfzmv__uoon)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, har__mex) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(yleq__vbf) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(zaoh__wpkk) for zaoh__wpkk in yleq__vbf)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(zaoh__wpkk, 
                    op == operator.ne) for zaoh__wpkk in yleq__vbf)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(rhs)'
            return _gen_init_df(header, rhs.columns, data_args, index)
    return overload_dataframe_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        nqyi__xkh = create_binary_op_overload(op)
        overload(op)(nqyi__xkh)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        har__mex = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, har__mex)
        check_runtime_cols_unsupported(right, har__mex)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                zonsw__fdxj, mpf__rua, sisdn__sjk = _get_binop_columns(left,
                    right, True)
                zxfdb__tfq = 'def impl(left, right):\n'
                for i, itv__padiu in enumerate(sisdn__sjk):
                    if itv__padiu == -1:
                        zxfdb__tfq += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    zxfdb__tfq += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    zxfdb__tfq += f"""  df_arr{i} {har__mex} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {itv__padiu})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    zonsw__fdxj)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(zxfdb__tfq, zonsw__fdxj, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            zxfdb__tfq = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                zxfdb__tfq += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                zxfdb__tfq += '  df_arr{0} {1} right\n'.format(i, har__mex)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(zxfdb__tfq, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        nqyi__xkh = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(nqyi__xkh)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            har__mex = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, har__mex)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, har__mex) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        nqyi__xkh = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(nqyi__xkh)


_install_unary_ops()


def overload_isna(obj):
    check_runtime_cols_unsupported(obj, 'pd.isna()')
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj):
        return lambda obj: obj.isna()
    if is_array_typ(obj):

        def impl(obj):
            numba.parfors.parfor.init_prange()
            n = len(obj)
            waa__fte = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                waa__fte[i] = bodo.libs.array_kernels.isna(obj, i)
            return waa__fte
        return impl


overload(pd.isna, inline='always')(overload_isna)
overload(pd.isnull, inline='always')(overload_isna)


@overload(pd.isna)
@overload(pd.isnull)
def overload_isna_scalar(obj):
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj) or is_array_typ(
        obj):
        return
    if isinstance(obj, (types.List, types.UniTuple)):

        def impl(obj):
            n = len(obj)
            waa__fte = np.empty(n, np.bool_)
            for i in range(n):
                waa__fte[i] = pd.isna(obj[i])
            return waa__fte
        return impl
    obj = types.unliteral(obj)
    if obj == bodo.string_type:
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Integer):
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Float):
        return lambda obj: np.isnan(obj)
    if isinstance(obj, (types.NPDatetime, types.NPTimedelta)):
        return lambda obj: np.isnat(obj)
    if obj == types.none:
        return lambda obj: unliteral_val(True)
    if obj == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_dt64(obj.value))
    if obj == bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type:
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_timedelta64(obj.value))
    if isinstance(obj, types.Optional):
        return lambda obj: obj is None
    return lambda obj: unliteral_val(False)


@overload(operator.setitem, no_unliteral=True)
def overload_setitem_arr_none(A, idx, val):
    if is_array_typ(A, False) and isinstance(idx, types.Integer
        ) and val == types.none:
        return lambda A, idx, val: bodo.libs.array_kernels.setna(A, idx)


def overload_notna(obj):
    check_runtime_cols_unsupported(obj, 'pd.notna()')
    if isinstance(obj, DataFrameType):
        return lambda obj: obj.notna()
    if isinstance(obj, (SeriesType, types.Array, types.List, types.UniTuple)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj
        ) or obj == bodo.string_array_type:
        return lambda obj: ~pd.isna(obj)
    return lambda obj: not pd.isna(obj)


overload(pd.notna, inline='always', no_unliteral=True)(overload_notna)
overload(pd.notnull, inline='always', no_unliteral=True)(overload_notna)


def _get_pd_dtype_str(t):
    if t.dtype == types.NPDatetime('ns'):
        return "'datetime64[ns]'"
    return bodo.ir.csv_ext._get_pd_dtype_str(t)


@overload_method(DataFrameType, 'replace', inline='always', no_unliteral=True)
def overload_dataframe_replace(df, to_replace=None, value=None, inplace=
    False, limit=None, regex=False, method='pad'):
    check_runtime_cols_unsupported(df, 'DataFrame.replace()')
    if is_overload_none(to_replace):
        raise BodoError('replace(): to_replace value of None is not supported')
    hsb__hzwsd = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    kwyqc__leuzd = {'inplace': False, 'limit': None, 'regex': False,
        'method': 'pad'}
    check_unsupported_args('replace', hsb__hzwsd, kwyqc__leuzd,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    zdy__apifd = str(expr_node)
    return zdy__apifd.startswith('left.') or zdy__apifd.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    fta__qzm = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (fta__qzm,))
    gqb__kfqmw = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        lbl__ynr = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        emnd__ffxx = {('NOT_NA', gqb__kfqmw(wmtlz__eplw)): wmtlz__eplw for
            wmtlz__eplw in null_set}
        vlyd__rue, mpf__rua, mpf__rua = _parse_query_expr(lbl__ynr, env, [],
            [], None, join_cleaned_cols=emnd__ffxx)
        rgrki__wvw = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            uywup__rarw = pd.core.computation.ops.BinOp('&', vlyd__rue,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = rgrki__wvw
        return uywup__rarw

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                npoc__eoh = set()
                fhg__cqf = set()
                vme__ltw = _insert_NA_cond_body(expr_node.lhs, npoc__eoh)
                hjveb__fjvy = _insert_NA_cond_body(expr_node.rhs, fhg__cqf)
                aklsb__xpe = npoc__eoh.intersection(fhg__cqf)
                npoc__eoh.difference_update(aklsb__xpe)
                fhg__cqf.difference_update(aklsb__xpe)
                null_set.update(aklsb__xpe)
                expr_node.lhs = append_null_checks(vme__ltw, npoc__eoh)
                expr_node.rhs = append_null_checks(hjveb__fjvy, fhg__cqf)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            gjm__hmqoi = expr_node.name
            jrzqw__cwkcq, col_name = gjm__hmqoi.split('.')
            if jrzqw__cwkcq == 'left':
                wyuq__xkaz = left_columns
                data = left_data
            else:
                wyuq__xkaz = right_columns
                data = right_data
            mzyku__lbeng = data[wyuq__xkaz.index(col_name)]
            if bodo.utils.typing.is_nullable(mzyku__lbeng):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    lmu__znd = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        ezcp__hwlzb = str(expr_node.lhs)
        ndmct__key = str(expr_node.rhs)
        if ezcp__hwlzb.startswith('left.') and ndmct__key.startswith('left.'
            ) or ezcp__hwlzb.startswith('right.') and ndmct__key.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [ezcp__hwlzb.split('.')[1]]
        right_on = [ndmct__key.split('.')[1]]
        if ezcp__hwlzb.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        ffs__xkky, dijy__poyv, foahr__ydoqa = _extract_equal_conds(expr_node
            .lhs)
        pzaio__opnn, wzm__jucm, glbua__nmtbh = _extract_equal_conds(expr_node
            .rhs)
        left_on = ffs__xkky + pzaio__opnn
        right_on = dijy__poyv + wzm__jucm
        if foahr__ydoqa is None:
            return left_on, right_on, glbua__nmtbh
        if glbua__nmtbh is None:
            return left_on, right_on, foahr__ydoqa
        expr_node.lhs = foahr__ydoqa
        expr_node.rhs = glbua__nmtbh
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    fta__qzm = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (fta__qzm,))
    zbvbt__izgb = dict()
    gqb__kfqmw = pd.core.computation.parsing.clean_column_name
    for name, rouhp__gcsuy in (('left', left_columns), ('right', right_columns)
        ):
        for wmtlz__eplw in rouhp__gcsuy:
            cbxt__qlcj = gqb__kfqmw(wmtlz__eplw)
            vusb__mmrf = name, cbxt__qlcj
            if vusb__mmrf in zbvbt__izgb:
                raise BodoException(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{wmtlz__eplw}' and '{zbvbt__izgb[cbxt__qlcj]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            zbvbt__izgb[vusb__mmrf] = wmtlz__eplw
    meag__azl, mpf__rua, mpf__rua = _parse_query_expr(on_str, env, [], [],
        None, join_cleaned_cols=zbvbt__izgb)
    left_on, right_on, kjj__nzd = _extract_equal_conds(meag__azl.terms)
    return left_on, right_on, _insert_NA_cond(kjj__nzd, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    wiaw__wdsoy = dict(sort=sort, copy=copy, validate=validate)
    kxufd__czm = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    aqd__rqwn = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    ofdv__lbsl = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in aqd__rqwn and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, dfz__ddyb = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if dfz__ddyb is None:
                    ofdv__lbsl = ''
                else:
                    ofdv__lbsl = str(dfz__ddyb)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = aqd__rqwn
        right_keys = aqd__rqwn
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    if (not left_on or not right_on) and not is_overload_none(on):
        raise BodoError(
            f"DataFrame.merge(): Merge condition '{get_overload_const_str(on)}' requires a cross join to implement, but cross join is not supported."
            )
    if not is_overload_bool(indicator):
        raise_bodo_error(
            'DataFrame.merge(): indicator must be a constant boolean')
    indicator_val = get_overload_const_bool(indicator)
    if not is_overload_bool(_bodo_na_equal):
        raise_bodo_error(
            'DataFrame.merge(): bodo extension _bodo_na_equal must be a constant boolean'
            )
    udg__iynrq = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        bca__gtj = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        bca__gtj = list(get_overload_const_list(suffixes))
    suffix_x = bca__gtj[0]
    suffix_y = bca__gtj[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    zxfdb__tfq = "def _impl(left, right, how='inner', on=None, left_on=None,\n"
    zxfdb__tfq += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    zxfdb__tfq += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    zxfdb__tfq += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, udg__iynrq, ofdv__lbsl))
    zseir__wkn = {}
    exec(zxfdb__tfq, {'bodo': bodo}, zseir__wkn)
    _impl = zseir__wkn['_impl']
    return _impl


def common_validate_merge_merge_asof_spec(name_func, left, right, on,
    left_on, right_on, left_index, right_index, suffixes):
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError(name_func + '() requires dataframe inputs')
    valid_dataframe_column_types = (ArrayItemArrayType, MapArrayType,
        StructArrayType, CategoricalArrayType, types.Array,
        IntegerArrayType, DecimalArrayType, IntervalArrayType)
    unjiw__ubs = {string_array_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    xgg__fur = {get_overload_const_str(uhk__bsbz) for uhk__bsbz in (left_on,
        right_on, on) if is_overload_constant_str(uhk__bsbz)}
    for df in (left, right):
        for i, wmtlz__eplw in enumerate(df.data):
            if not isinstance(wmtlz__eplw, valid_dataframe_column_types
                ) and wmtlz__eplw not in unjiw__ubs:
                raise BodoError(
                    f'{name_func}(): use of column with {type(wmtlz__eplw)} in merge unsupported'
                    )
            if df.columns[i] in xgg__fur and isinstance(wmtlz__eplw,
                MapArrayType):
                raise BodoError(
                    f'{name_func}(): merge on MapArrayType unsupported')
    ensure_constant_arg(name_func, 'left_index', left_index, bool)
    ensure_constant_arg(name_func, 'right_index', right_index, bool)
    if not is_overload_constant_tuple(suffixes
        ) and not is_overload_constant_list(suffixes):
        raise_const_error(name_func +
            "(): suffixes parameters should be ['_left', '_right']")
    if is_overload_constant_tuple(suffixes):
        bca__gtj = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        bca__gtj = list(get_overload_const_list(suffixes))
    if len(bca__gtj) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    aqd__rqwn = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        utu__qtjhf = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            utu__qtjhf = on_str not in aqd__rqwn and ('left.' in on_str or 
                'right.' in on_str)
        if len(aqd__rqwn) == 0 and not utu__qtjhf:
            raise_bodo_error(name_func +
                '(): No common columns to perform merge on. Merge options: left_on={lon}, right_on={ron}, left_index={lidx}, right_index={ridx}'
                .format(lon=is_overload_true(left_on), ron=is_overload_true
                (right_on), lidx=is_overload_true(left_index), ridx=
                is_overload_true(right_index)))
        if not is_overload_none(left_on) or not is_overload_none(right_on):
            raise BodoError(name_func +
                '(): Can only pass argument "on" OR "left_on" and "right_on", not a combination of both.'
                )
    if (is_overload_true(left_index) or not is_overload_none(left_on)
        ) and is_overload_none(right_on) and not is_overload_true(right_index):
        raise BodoError(name_func +
            '(): Must pass right_on or right_index=True')
    if (is_overload_true(right_index) or not is_overload_none(right_on)
        ) and is_overload_none(left_on) and not is_overload_true(left_index):
        raise BodoError(name_func + '(): Must pass left_on or left_index=True')


def validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
    right_index, sort, suffixes, copy, indicator, validate):
    common_validate_merge_merge_asof_spec('merge', left, right, on, left_on,
        right_on, left_index, right_index, suffixes)
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))


def validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
    right_index, by, left_by, right_by, suffixes, tolerance,
    allow_exact_matches, direction):
    common_validate_merge_merge_asof_spec('merge_asof', left, right, on,
        left_on, right_on, left_index, right_index, suffixes)
    if not is_overload_true(allow_exact_matches):
        raise BodoError(
            'merge_asof(): allow_exact_matches parameter only supports default value True'
            )
    if not is_overload_none(tolerance):
        raise BodoError(
            'merge_asof(): tolerance parameter only supports default value None'
            )
    if not is_overload_none(by):
        raise BodoError(
            'merge_asof(): by parameter only supports default value None')
    if not is_overload_none(left_by):
        raise BodoError(
            'merge_asof(): left_by parameter only supports default value None')
    if not is_overload_none(right_by):
        raise BodoError(
            'merge_asof(): right_by parameter only supports default value None'
            )
    if not is_overload_constant_str(direction):
        raise BodoError(
            'merge_asof(): direction parameter should be of type str')
    else:
        direction = get_overload_const_str(direction)
        if direction != 'backward':
            raise BodoError(
                "merge_asof(): direction parameter only supports default value 'backward'"
                )


def validate_merge_asof_keys_length(left_on, right_on, left_index,
    right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if not is_overload_none(left_on) and is_overload_true(right_index):
        raise BodoError(
            'merge(): right_index = True and specifying left_on is not suppported yet.'
            )
    if not is_overload_none(right_on) and is_overload_true(left_index):
        raise BodoError(
            'merge(): left_index = True and specifying right_on is not suppported yet.'
            )


def validate_keys_length(left_index, right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if is_overload_true(right_index):
        if len(left_keys) != 1:
            raise BodoError(
                'merge(): len(left_on) must equal the number of levels in the index of "right", which is 1'
                )
    if is_overload_true(left_index):
        if len(right_keys) != 1:
            raise BodoError(
                'merge(): len(right_on) must equal the number of levels in the index of "left", which is 1'
                )


def validate_keys_dtypes(left, right, left_index, right_index, left_keys,
    right_keys):
    oil__osv = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            vquk__cmbi = left.index
            elser__xtask = isinstance(vquk__cmbi, StringIndexType)
            hbac__vqo = right.index
            ydq__iavud = isinstance(hbac__vqo, StringIndexType)
        elif is_overload_true(left_index):
            vquk__cmbi = left.index
            elser__xtask = isinstance(vquk__cmbi, StringIndexType)
            hbac__vqo = right.data[right.columns.index(right_keys[0])]
            ydq__iavud = hbac__vqo.dtype == string_type
        elif is_overload_true(right_index):
            vquk__cmbi = left.data[left.columns.index(left_keys[0])]
            elser__xtask = vquk__cmbi.dtype == string_type
            hbac__vqo = right.index
            ydq__iavud = isinstance(hbac__vqo, StringIndexType)
        if elser__xtask and ydq__iavud:
            return
        vquk__cmbi = vquk__cmbi.dtype
        hbac__vqo = hbac__vqo.dtype
        try:
            rrku__kacw = oil__osv.resolve_function_type(operator.eq, (
                vquk__cmbi, hbac__vqo), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=vquk__cmbi, rk_dtype=hbac__vqo))
    else:
        for dipnq__pvewe, qnrbw__gcg in zip(left_keys, right_keys):
            vquk__cmbi = left.data[left.columns.index(dipnq__pvewe)].dtype
            glbc__deqk = left.data[left.columns.index(dipnq__pvewe)]
            hbac__vqo = right.data[right.columns.index(qnrbw__gcg)].dtype
            fccdf__eajco = right.data[right.columns.index(qnrbw__gcg)]
            if glbc__deqk == fccdf__eajco:
                continue
            kxjs__ggcc = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=dipnq__pvewe, lk_dtype=vquk__cmbi, rk=qnrbw__gcg,
                rk_dtype=hbac__vqo))
            dhg__hyxh = vquk__cmbi == string_type
            eax__hkyiw = hbac__vqo == string_type
            if dhg__hyxh ^ eax__hkyiw:
                raise_bodo_error(kxjs__ggcc)
            try:
                rrku__kacw = oil__osv.resolve_function_type(operator.eq, (
                    vquk__cmbi, hbac__vqo), {})
            except:
                raise_bodo_error(kxjs__ggcc)


def validate_keys(keys, df):
    kibcp__fjg = set(keys).difference(set(df.columns))
    if len(kibcp__fjg) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in kibcp__fjg:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {kibcp__fjg} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    wiaw__wdsoy = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    kxufd__czm = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort)
    how = get_overload_const_str(how)
    if not is_overload_none(on):
        left_keys = get_overload_const_list(on)
    else:
        left_keys = ['$_bodo_index_']
    right_keys = ['$_bodo_index_']
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    zxfdb__tfq = "def _impl(left, other, on=None, how='left',\n"
    zxfdb__tfq += "    lsuffix='', rsuffix='', sort=False):\n"
    zxfdb__tfq += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    zseir__wkn = {}
    exec(zxfdb__tfq, {'bodo': bodo}, zseir__wkn)
    _impl = zseir__wkn['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        zauo__kjzhb = get_overload_const_list(on)
        validate_keys(zauo__kjzhb, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    aqd__rqwn = tuple(set(left.columns) & set(other.columns))
    if len(aqd__rqwn) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=aqd__rqwn))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    qxipv__jzev = set(left_keys) & set(right_keys)
    wpdqd__lnrfv = set(left_columns) & set(right_columns)
    kvj__tqv = wpdqd__lnrfv - qxipv__jzev
    ioqlu__jtee = set(left_columns) - wpdqd__lnrfv
    szs__tioqs = set(right_columns) - wpdqd__lnrfv
    tcat__oim = {}

    def insertOutColumn(col_name):
        if col_name in tcat__oim:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        tcat__oim[col_name] = 0
    for vpgf__emcg in qxipv__jzev:
        insertOutColumn(vpgf__emcg)
    for vpgf__emcg in kvj__tqv:
        mblei__xsgeo = str(vpgf__emcg) + suffix_x
        nplh__besbf = str(vpgf__emcg) + suffix_y
        insertOutColumn(mblei__xsgeo)
        insertOutColumn(nplh__besbf)
    for vpgf__emcg in ioqlu__jtee:
        insertOutColumn(vpgf__emcg)
    for vpgf__emcg in szs__tioqs:
        insertOutColumn(vpgf__emcg)
    if indicator_val:
        insertOutColumn('_merge')


@overload(pd.merge_asof, inline='always', no_unliteral=True)
def overload_dataframe_merge_asof(left, right, on=None, left_on=None,
    right_on=None, left_index=False, right_index=False, by=None, left_by=
    None, right_by=None, suffixes=('_x', '_y'), tolerance=None,
    allow_exact_matches=True, direction='backward'):
    validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
        right_index, by, left_by, right_by, suffixes, tolerance,
        allow_exact_matches, direction)
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError('merge_asof() requires dataframe inputs')
    aqd__rqwn = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = aqd__rqwn
        right_keys = aqd__rqwn
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    validate_merge_asof_keys_length(left_on, right_on, left_index,
        right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    if isinstance(suffixes, tuple):
        bca__gtj = suffixes
    if is_overload_constant_list(suffixes):
        bca__gtj = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        bca__gtj = suffixes.value
    suffix_x = bca__gtj[0]
    suffix_y = bca__gtj[1]
    zxfdb__tfq = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    zxfdb__tfq += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    zxfdb__tfq += "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n"
    zxfdb__tfq += "    allow_exact_matches=True, direction='backward'):\n"
    zxfdb__tfq += '  suffix_x = suffixes[0]\n'
    zxfdb__tfq += '  suffix_y = suffixes[1]\n'
    zxfdb__tfq += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    zseir__wkn = {}
    exec(zxfdb__tfq, {'bodo': bodo}, zseir__wkn)
    _impl = zseir__wkn['_impl']
    return _impl


@overload_method(DataFrameType, 'groupby', inline='always', no_unliteral=True)
def overload_dataframe_groupby(df, by=None, axis=0, level=None, as_index=
    True, sort=False, group_keys=True, squeeze=False, observed=True, dropna
    =True):
    check_runtime_cols_unsupported(df, 'DataFrame.groupby()')
    validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
        squeeze, observed, dropna)

    def _impl(df, by=None, axis=0, level=None, as_index=True, sort=False,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        return bodo.hiframes.pd_groupby_ext.init_groupby(df, by, as_index,
            dropna)
    return _impl


def validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
    squeeze, observed, dropna):
    if is_overload_none(by):
        raise BodoError("groupby(): 'by' must be supplied.")
    if not is_overload_zero(axis):
        raise BodoError(
            "groupby(): 'axis' parameter only supports integer value 0.")
    if not is_overload_none(level):
        raise BodoError(
            "groupby(): 'level' is not supported since MultiIndex is not supported."
            )
    if not is_literal_type(by) and not is_overload_constant_list(by):
        raise_const_error(
            f"groupby(): 'by' parameter only supports a constant column label or column labels, not {by}."
            )
    if len(set(get_overload_const_list(by)).difference(set(df.columns))) > 0:
        raise_const_error(
            "groupby(): invalid key {} for 'by' (not available in columns {})."
            .format(get_overload_const_list(by), df.columns))
    if not is_overload_constant_bool(as_index):
        raise_const_error(
            "groupby(): 'as_index' parameter must be a constant bool, not {}."
            .format(as_index))
    if not is_overload_constant_bool(dropna):
        raise_const_error(
            "groupby(): 'dropna' parameter must be a constant bool, not {}."
            .format(dropna))
    wiaw__wdsoy = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    tsh__tehm = dict(sort=False, group_keys=True, squeeze=False, observed=True)
    check_unsupported_args('Dataframe.groupby', wiaw__wdsoy, tsh__tehm,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    if is_overload_none(index) or not is_literal_type(index):
        raise BodoError(
            f"{func_name}(): 'index' argument is required and must be a constant column label"
            )
    if is_overload_none(columns) or not is_literal_type(columns):
        raise BodoError(
            f"{func_name}(): 'columns' argument is required and must be a constant column label"
            )
    if not is_overload_none(values) and not is_literal_type(values):
        raise BodoError(
            f"{func_name}(): if 'values' argument is provided it must be a constant column label"
            )
    ecnpw__fidh = get_literal_value(index)
    if isinstance(ecnpw__fidh, (list, tuple)):
        if len(ecnpw__fidh) > 1:
            raise BodoError(
                f"{func_name}(): 'index' argument must be a constant column label not a {ecnpw__fidh}"
                )
        ecnpw__fidh = ecnpw__fidh[0]
    jxdo__qqjy = get_literal_value(columns)
    if isinstance(jxdo__qqjy, (list, tuple)):
        if len(jxdo__qqjy) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {jxdo__qqjy}"
                )
        jxdo__qqjy = jxdo__qqjy[0]
    if ecnpw__fidh not in df.columns:
        raise BodoError(
            f"{func_name}(): 'index' column {ecnpw__fidh} not found in DataFrame {df}."
            )
    if jxdo__qqjy not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {jxdo__qqjy} not found in DataFrame {df}."
            )
    gcl__sekh = {aavn__hcyl: i for i, aavn__hcyl in enumerate(df.columns)}
    two__bkto = gcl__sekh[ecnpw__fidh]
    ptem__pomnq = gcl__sekh[jxdo__qqjy]
    if is_overload_none(values):
        wuire__dmakz = []
        rvt__anqx = []
        for i, aavn__hcyl in enumerate(df.columns):
            if i not in (two__bkto, ptem__pomnq):
                wuire__dmakz.append(i)
                rvt__anqx.append(aavn__hcyl)
    else:
        rvt__anqx = get_literal_value(values)
        if not isinstance(rvt__anqx, (list, tuple)):
            rvt__anqx = [rvt__anqx]
        wuire__dmakz = []
        for val in rvt__anqx:
            if val not in gcl__sekh:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            wuire__dmakz.append(gcl__sekh[val])
    if all(isinstance(aavn__hcyl, int) for aavn__hcyl in rvt__anqx):
        rvt__anqx = np.array(rvt__anqx, 'int64')
    elif all(isinstance(aavn__hcyl, str) for aavn__hcyl in rvt__anqx):
        rvt__anqx = pd.array(rvt__anqx, 'string')
    else:
        raise BodoError(
            f"{func_name}(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    tkeyt__vmn = set(wuire__dmakz) | {two__bkto, ptem__pomnq}
    if len(tkeyt__vmn) != len(wuire__dmakz) + 2:
        raise BodoError(
            f"{func_name}(): 'index', 'columns', and 'values' must all refer to different columns"
            )
    bcft__tdsc = df.data[two__bkto]
    if isinstance(bcft__tdsc, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'index' DataFrame column must have scalar rows")
    if isinstance(bcft__tdsc, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'index' DataFrame column does not support categorical data"
            )
    hicxq__jgpb = df.data[ptem__pomnq]
    if isinstance(hicxq__jgpb, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(hicxq__jgpb, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for nbrn__lwuy in wuire__dmakz:
        pysky__bxp = df.data[nbrn__lwuy]
        if isinstance(pysky__bxp, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or pysky__bxp == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return (ecnpw__fidh, jxdo__qqjy, rvt__anqx, two__bkto, ptem__pomnq,
        wuire__dmakz)


@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(df, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pivot()')
    (ecnpw__fidh, jxdo__qqjy, rvt__anqx, two__bkto, ptem__pomnq, sij__lep) = (
        pivot_error_checking(df, index, columns, values, 'DataFrame.pivot'))
    if len(rvt__anqx) == 1:
        omd__ridy = None
    else:
        omd__ridy = rvt__anqx
    zxfdb__tfq = 'def impl(df, index=None, columns=None, values=None):\n'
    zxfdb__tfq += f'    pivot_values = df.iloc[:, {ptem__pomnq}].unique()\n'
    zxfdb__tfq += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    zxfdb__tfq += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {two__bkto}),),
"""
    zxfdb__tfq += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ptem__pomnq}),),
"""
    zxfdb__tfq += '        (\n'
    for nbrn__lwuy in sij__lep:
        zxfdb__tfq += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {nbrn__lwuy}),
"""
    zxfdb__tfq += '        ),\n'
    zxfdb__tfq += '        pivot_values,\n'
    zxfdb__tfq += '        index_lit,\n'
    zxfdb__tfq += '        columns_lit,\n'
    zxfdb__tfq += '        values_name_const,\n'
    zxfdb__tfq += '    )\n'
    zseir__wkn = {}
    exec(zxfdb__tfq, {'bodo': bodo, 'index_lit': ecnpw__fidh, 'columns_lit':
        jxdo__qqjy, 'values_name_const': omd__ridy}, zseir__wkn)
    impl = zseir__wkn['impl']
    return impl


@overload_method(DataFrameType, 'pivot_table', inline='always',
    no_unliteral=True)
def overload_dataframe_pivot_table(df, values=None, index=None, columns=
    None, aggfunc='mean', fill_value=None, margins=False, dropna=True,
    margins_name='All', observed=False, sort=True, _pivot_values=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pivot_table()')
    wiaw__wdsoy = dict(fill_value=fill_value, margins=margins, dropna=
        dropna, margins_name=margins_name, observed=observed, sort=sort)
    kxufd__czm = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    if _pivot_values is None:
        (ecnpw__fidh, jxdo__qqjy, rvt__anqx, two__bkto, ptem__pomnq, sij__lep
            ) = (pivot_error_checking(df, index, columns, values,
            'DataFrame.pivot_table'))
        if len(rvt__anqx) == 1:
            omd__ridy = None
        else:
            omd__ridy = rvt__anqx
        zxfdb__tfq = 'def impl(\n'
        zxfdb__tfq += '    df,\n'
        zxfdb__tfq += '    values=None,\n'
        zxfdb__tfq += '    index=None,\n'
        zxfdb__tfq += '    columns=None,\n'
        zxfdb__tfq += '    aggfunc="mean",\n'
        zxfdb__tfq += '    fill_value=None,\n'
        zxfdb__tfq += '    margins=False,\n'
        zxfdb__tfq += '    dropna=True,\n'
        zxfdb__tfq += '    margins_name="All",\n'
        zxfdb__tfq += '    observed=False,\n'
        zxfdb__tfq += '    sort=True,\n'
        zxfdb__tfq += '    _pivot_values=None,\n'
        zxfdb__tfq += '):\n'
        wjj__vwh = [two__bkto, ptem__pomnq] + sij__lep
        zxfdb__tfq += f'    df = df.iloc[:, {wjj__vwh}]\n'
        zxfdb__tfq += """    df = df.groupby([index_lit, columns_lit], as_index=False).agg(aggfunc)
"""
        zxfdb__tfq += '    pivot_values = df.iloc[:, 1].unique()\n'
        zxfdb__tfq += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
        zxfdb__tfq += (
            f'        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, 0),),\n'
            )
        zxfdb__tfq += (
            f'        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, 1),),\n'
            )
        zxfdb__tfq += '        (\n'
        for i in range(2, len(sij__lep) + 2):
            zxfdb__tfq += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}),
"""
        zxfdb__tfq += '        ),\n'
        zxfdb__tfq += '        pivot_values,\n'
        zxfdb__tfq += '        index_lit,\n'
        zxfdb__tfq += '        columns_lit,\n'
        zxfdb__tfq += '        values_name_const,\n'
        zxfdb__tfq += '        check_duplicates=False,\n'
        zxfdb__tfq += '    )\n'
        zseir__wkn = {}
        exec(zxfdb__tfq, {'bodo': bodo, 'index_lit': ecnpw__fidh,
            'columns_lit': jxdo__qqjy, 'values_name_const': omd__ridy},
            zseir__wkn)
        impl = zseir__wkn['impl']
        return impl
    if aggfunc == 'mean':

        def _impl(df, values=None, index=None, columns=None, aggfunc='mean',
            fill_value=None, margins=False, dropna=True, margins_name='All',
            observed=False, sort=True, _pivot_values=None):
            return bodo.hiframes.pd_groupby_ext.pivot_table_dummy(df,
                values, index, columns, 'mean', _pivot_values)
        return _impl

    def _impl(df, values=None, index=None, columns=None, aggfunc='mean',
        fill_value=None, margins=False, dropna=True, margins_name='All',
        observed=False, sort=True, _pivot_values=None):
        return bodo.hiframes.pd_groupby_ext.pivot_table_dummy(df, values,
            index, columns, aggfunc, _pivot_values)
    return _impl


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    wiaw__wdsoy = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    kxufd__czm = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(index, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'index' argument only supported for Series types, found {index}"
            )
    if not isinstance(columns, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'columns' argument only supported for Series types, found {columns}"
            )

    def _impl(index, columns, values=None, rownames=None, colnames=None,
        aggfunc=None, margins=False, margins_name='All', dropna=True,
        normalize=False, _pivot_values=None):
        return bodo.hiframes.pd_groupby_ext.crosstab_dummy(index, columns,
            _pivot_values)
    return _impl


@overload_method(DataFrameType, 'sort_values', inline='always',
    no_unliteral=True)
def overload_dataframe_sort_values(df, by, axis=0, ascending=True, inplace=
    False, kind='quicksort', na_position='last', ignore_index=False, key=
    None, _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_values()')
    wiaw__wdsoy = dict(ignore_index=ignore_index, key=key)
    kxufd__czm = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'sort_values')
    validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
        na_position)

    def _impl(df, by, axis=0, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', ignore_index=False, key=None,
        _bodo_transformed=False):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df, by,
            ascending, inplace, na_position)
    return _impl


def validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
    na_position):
    if is_overload_none(by) or not is_literal_type(by
        ) and not is_overload_constant_list(by):
        raise_const_error(
            "sort_values(): 'by' parameter only supports a constant column label or column labels. by={}"
            .format(by))
    qxrn__bklih = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        qxrn__bklih.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        yal__owiz = [get_overload_const_tuple(by)]
    else:
        yal__owiz = get_overload_const_list(by)
    yal__owiz = set((k, '') if (k, '') in qxrn__bklih else k for k in yal__owiz
        )
    if len(yal__owiz.difference(qxrn__bklih)) > 0:
        azh__bmot = list(set(get_overload_const_list(by)).difference(
            qxrn__bklih))
        raise_bodo_error(f'sort_values(): invalid keys {azh__bmot} for by.')
    if not is_overload_zero(axis):
        raise_bodo_error(
            "sort_values(): 'axis' parameter only supports integer value 0.")
    if not is_overload_bool(ascending) and not is_overload_bool_list(ascending
        ):
        raise_bodo_error(
            "sort_values(): 'ascending' parameter must be of type bool or list of bool, not {}."
            .format(ascending))
    if not is_overload_bool(inplace):
        raise_bodo_error(
            "sort_values(): 'inplace' parameter must be of type bool, not {}."
            .format(inplace))
    if kind != 'quicksort' and not isinstance(kind, types.Omitted):
        warnings.warn(BodoWarning(
            'sort_values(): specifying sorting algorithm is not supported in Bodo. Bodo uses stable sort.'
            ))
    if is_overload_constant_str(na_position):
        na_position = get_overload_const_str(na_position)
        if na_position not in ('first', 'last'):
            raise BodoError(
                "sort_values(): na_position should either be 'first' or 'last'"
                )
    elif is_overload_constant_list(na_position):
        yod__varao = get_overload_const_list(na_position)
        for na_position in yod__varao:
            if na_position not in ('first', 'last'):
                raise BodoError(
                    "sort_values(): Every value in na_position should either be 'first' or 'last'"
                    )
    else:
        raise_const_error(
            f'sort_values(): na_position parameter must be a literal constant of type str or a constant list of str with 1 entry per key column, not {na_position}'
            )
    na_position = get_overload_const_str(na_position)
    if na_position not in ['first', 'last']:
        raise BodoError(
            "sort_values(): na_position should either be 'first' or 'last'")


@overload_method(DataFrameType, 'sort_index', inline='always', no_unliteral
    =True)
def overload_dataframe_sort_index(df, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_index()')
    wiaw__wdsoy = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    kxufd__czm = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_bool(ascending):
        raise BodoError(
            "DataFrame.sort_index(): 'ascending' parameter must be of type bool"
            )
    if not is_overload_bool(inplace):
        raise BodoError(
            "DataFrame.sort_index(): 'inplace' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "DataFrame.sort_index(): 'na_position' should either be 'first' or 'last'"
            )

    def _impl(df, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df,
            '$_bodo_index_', ascending, inplace, na_position)
    return _impl


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    wiaw__wdsoy = dict(limit=limit, downcast=downcast)
    kxufd__czm = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    dog__toqsv = not is_overload_none(value)
    lrcg__xcm = not is_overload_none(method)
    if dog__toqsv and lrcg__xcm:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not dog__toqsv and not lrcg__xcm:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if dog__toqsv:
        kykf__emq = 'value=value'
    else:
        kykf__emq = 'method=method'
    data_args = [(
        f"df['{aavn__hcyl}'].fillna({kykf__emq}, inplace=inplace)" if
        isinstance(aavn__hcyl, str) else
        f'df[{aavn__hcyl}].fillna({kykf__emq}, inplace=inplace)') for
        aavn__hcyl in df.columns]
    zxfdb__tfq = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        zxfdb__tfq += '  ' + '  \n'.join(data_args) + '\n'
        zseir__wkn = {}
        exec(zxfdb__tfq, {}, zseir__wkn)
        impl = zseir__wkn['impl']
        return impl
    else:
        return _gen_init_df(zxfdb__tfq, df.columns, ', '.join(dfljv__xjj +
            '.values' for dfljv__xjj in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    wiaw__wdsoy = dict(col_level=col_level, col_fill=col_fill)
    kxufd__czm = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'reset_index')
    if not _is_all_levels(df, level):
        raise_bodo_error(
            'DataFrame.reset_index(): only dropping all index levels supported'
            )
    if not is_overload_constant_bool(drop):
        raise BodoError(
            "DataFrame.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.reset_index(): 'inplace' parameter should be a constant boolean value"
            )
    zxfdb__tfq = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    zxfdb__tfq += (
        '  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(df), 1, None)\n'
        )
    drop = is_overload_true(drop)
    inplace = is_overload_true(inplace)
    columns = df.columns
    data_args = [
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}\n'.
        format(i, '' if inplace else '.copy()') for i in range(len(df.columns))
        ]
    if not drop:
        sck__pgdr = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            sck__pgdr)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            zxfdb__tfq += (
                '  m_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
                )
            ayrv__vevs = ['m_index._data[{}]'.format(i) for i in range(df.
                index.nlevels)]
            data_args = ayrv__vevs + data_args
        else:
            bho__lgu = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [bho__lgu] + data_args
    return _gen_init_df(zxfdb__tfq, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    bad__qywru = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and bad__qywru == 1 or is_overload_constant_list(level
        ) and list(get_overload_const_list(level)) == list(range(bad__qywru))


@overload_method(DataFrameType, 'dropna', inline='always', no_unliteral=True)
def overload_dataframe_dropna(df, axis=0, how='any', thresh=None, subset=
    None, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.dropna()')
    if not is_overload_constant_bool(inplace) or is_overload_true(inplace):
        raise BodoError('DataFrame.dropna(): inplace=True is not supported')
    if not is_overload_zero(axis):
        raise_bodo_error(f'df.dropna(): only axis=0 supported')
    ensure_constant_values('dropna', 'how', how, ('any', 'all'))
    if is_overload_none(subset):
        wjcn__nnzp = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        lyru__zgrpp = get_overload_const_list(subset)
        wjcn__nnzp = []
        for aru__zapp in lyru__zgrpp:
            if aru__zapp not in df.columns:
                raise_bodo_error(
                    f"df.dropna(): column '{aru__zapp}' not in data frame columns {df}"
                    )
            wjcn__nnzp.append(df.columns.index(aru__zapp))
    izt__cyza = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(izt__cyza))
    zxfdb__tfq = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(izt__cyza):
        zxfdb__tfq += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    zxfdb__tfq += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in wjcn__nnzp)))
    zxfdb__tfq += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(zxfdb__tfq, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    wiaw__wdsoy = dict(index=index, level=level, errors=errors)
    kxufd__czm = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', wiaw__wdsoy, kxufd__czm,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'drop')
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "DataFrame.drop(): 'inplace' parameter should be a constant bool")
    if not is_overload_none(labels):
        if not is_overload_none(columns):
            raise BodoError(
                "Dataframe.drop(): Cannot specify both 'labels' and 'columns'")
        if not is_overload_constant_int(axis) or get_overload_const_int(axis
            ) != 1:
            raise_bodo_error('DataFrame.drop(): only axis=1 supported')
        if is_overload_constant_str(labels):
            zricx__gdfe = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            zricx__gdfe = get_overload_const_list(labels)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    else:
        if is_overload_none(columns):
            raise BodoError(
                "DataFrame.drop(): Need to specify at least one of 'labels' or 'columns'"
                )
        if is_overload_constant_str(columns):
            zricx__gdfe = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            zricx__gdfe = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for aavn__hcyl in zricx__gdfe:
        if aavn__hcyl not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(aavn__hcyl, df.columns))
    if len(set(zricx__gdfe)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    ael__gcuay = tuple(aavn__hcyl for aavn__hcyl in df.columns if 
        aavn__hcyl not in zricx__gdfe)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.columns.index(aavn__hcyl), '.copy()' if not inplace else
        '') for aavn__hcyl in ael__gcuay)
    zxfdb__tfq = (
        'def impl(df, labels=None, axis=0, index=None, columns=None,\n')
    zxfdb__tfq += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(zxfdb__tfq, ael__gcuay, data_args, index)


@overload_method(DataFrameType, 'append', inline='always', no_unliteral=True)
def overload_dataframe_append(df, other, ignore_index=False,
    verify_integrity=False, sort=None):
    check_runtime_cols_unsupported(df, 'DataFrame.append()')
    check_runtime_cols_unsupported(other, 'DataFrame.append()')
    if isinstance(other, DataFrameType):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df, other), ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.BaseTuple):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df,) + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.List) and isinstance(other.dtype, DataFrameType
        ):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat([df] + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    raise BodoError(
        'invalid df.append() input. Only dataframe and list/tuple of dataframes supported'
        )


@overload_method(DataFrameType, 'sample', inline='always', no_unliteral=True)
def overload_dataframe_sample(df, n=None, frac=None, replace=False, weights
    =None, random_state=None, axis=None, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sample()')
    wiaw__wdsoy = dict(random_state=random_state, weights=weights, axis=
        axis, ignore_index=ignore_index)
    tfjm__bhf = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', wiaw__wdsoy, tfjm__bhf,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    izt__cyza = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(izt__cyza))
    zxfdb__tfq = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    for i in range(izt__cyza):
        zxfdb__tfq += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    zxfdb__tfq += '  if frac is None:\n'
    zxfdb__tfq += '    frac_d = -1.0\n'
    zxfdb__tfq += '  else:\n'
    zxfdb__tfq += '    frac_d = frac\n'
    zxfdb__tfq += '  if n is None:\n'
    zxfdb__tfq += '    n_i = 0\n'
    zxfdb__tfq += '  else:\n'
    zxfdb__tfq += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    zxfdb__tfq += (
        """  ({0},), index_arr = bodo.libs.array_kernels.sample_table_operation(({0},), {1}, n_i, frac_d, replace)
"""
        .format(data_args, index))
    zxfdb__tfq += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(zxfdb__tfq, df.columns,
        data_args, 'index')


@numba.njit
def _sizeof_fmt(num, size_qualifier=''):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f'{num:3.1f}{size_qualifier} {x}'
        num /= 1024.0
    return f'{num:3.1f}{size_qualifier} PB'


@overload_method(DataFrameType, 'info', no_unliteral=True)
def overload_dataframe_info(df, verbose=None, buf=None, max_cols=None,
    memory_usage=None, show_counts=None, null_counts=None):
    check_runtime_cols_unsupported(df, 'DataFrame.info()')
    hsb__hzwsd = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    kwyqc__leuzd = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', hsb__hzwsd, kwyqc__leuzd,
        package_name='pandas', module_name='DataFrame')
    bwywd__bjuoy = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            wjvil__ugtxf = bwywd__bjuoy + '\n'
            wjvil__ugtxf += 'Index: 0 entries\n'
            wjvil__ugtxf += 'Empty DataFrame'
            print(wjvil__ugtxf)
        return _info_impl
    else:
        zxfdb__tfq = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        zxfdb__tfq += '    ncols = df.shape[1]\n'
        zxfdb__tfq += f'    lines = "{bwywd__bjuoy}\\n"\n'
        zxfdb__tfq += f'    lines += "{df.index}: "\n'
        zxfdb__tfq += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            zxfdb__tfq += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            zxfdb__tfq += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            zxfdb__tfq += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        zxfdb__tfq += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        zxfdb__tfq += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        zxfdb__tfq += '    column_width = max(space, 7)\n'
        zxfdb__tfq += '    column= "Column"\n'
        zxfdb__tfq += '    underl= "------"\n'
        zxfdb__tfq += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        zxfdb__tfq += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        zxfdb__tfq += '    mem_size = 0\n'
        zxfdb__tfq += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        zxfdb__tfq += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        zxfdb__tfq += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        rbei__djn = dict()
        for i in range(len(df.columns)):
            zxfdb__tfq += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            ugs__bctf = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                ugs__bctf = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                vwtw__hmxu = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                ugs__bctf = f'{vwtw__hmxu[:-7]}'
            zxfdb__tfq += f'    col_dtype[{i}] = "{ugs__bctf}"\n'
            if ugs__bctf in rbei__djn:
                rbei__djn[ugs__bctf] += 1
            else:
                rbei__djn[ugs__bctf] = 1
            zxfdb__tfq += f'    col_name[{i}] = "{df.columns[i]}"\n'
            zxfdb__tfq += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        zxfdb__tfq += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        zxfdb__tfq += '    for i in column_info:\n'
        zxfdb__tfq += "        lines += f'{i}\\n'\n"
        rpig__bce = ', '.join(f'{k}({rbei__djn[k]})' for k in sorted(rbei__djn)
            )
        zxfdb__tfq += f"    lines += 'dtypes: {rpig__bce}\\n'\n"
        zxfdb__tfq += '    mem_size += df.index.nbytes\n'
        zxfdb__tfq += '    total_size = _sizeof_fmt(mem_size)\n'
        zxfdb__tfq += "    lines += f'memory usage: {total_size}'\n"
        zxfdb__tfq += '    print(lines)\n'
        zseir__wkn = {}
        exec(zxfdb__tfq, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo':
            bodo, 'np': np}, zseir__wkn)
        _info_impl = zseir__wkn['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    zxfdb__tfq = 'def impl(df, index=True, deep=False):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes'
         for i in range(len(df.columns)))
    if is_overload_true(index):
        zakbv__xtj = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes\n,')
        mjf__rvj = ','.join(f"'{aavn__hcyl}'" for aavn__hcyl in df.columns)
        arr = f"bodo.utils.conversion.coerce_to_array(('Index',{mjf__rvj}))"
        index = f'bodo.hiframes.pd_index_ext.init_binary_str_index({arr})'
        zxfdb__tfq += f"""  return bodo.hiframes.pd_series_ext.init_series(({zakbv__xtj}{data}), {index}, None)
"""
    else:
        haizl__vkeef = ',' if len(df.columns) == 1 else ''
        glr__zny = gen_const_tup(df.columns)
        zxfdb__tfq += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{haizl__vkeef}), pd.Index({glr__zny}), None)
"""
    zseir__wkn = {}
    exec(zxfdb__tfq, {'bodo': bodo, 'pd': pd}, zseir__wkn)
    impl = zseir__wkn['impl']
    return impl


@overload(pd.read_excel, no_unliteral=True)
def overload_read_excel(io, sheet_name=0, header=0, names=None, index_col=
    None, usecols=None, squeeze=False, dtype=None, engine=None, converters=
    None, true_values=None, false_values=None, skiprows=None, nrows=None,
    na_values=None, keep_default_na=True, na_filter=True, verbose=False,
    parse_dates=False, date_parser=None, thousands=None, comment=None,
    skipfooter=0, convert_float=True, mangle_dupe_cols=True, _bodo_df_type=None
    ):
    df_type = _bodo_df_type.instance_type
    iyrd__axsw = 'read_excel_df{}'.format(next_label())
    setattr(types, iyrd__axsw, df_type)
    iqyh__zoc = False
    if is_overload_constant_list(parse_dates):
        iqyh__zoc = get_overload_const_list(parse_dates)
    bdedu__els = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    zxfdb__tfq = (
        """
def impl(
    io,
    sheet_name=0,
    header=0,
    names=None,
    index_col=None,
    usecols=None,
    squeeze=False,
    dtype=None,
    engine=None,
    converters=None,
    true_values=None,
    false_values=None,
    skiprows=None,
    nrows=None,
    na_values=None,
    keep_default_na=True,
    na_filter=True,
    verbose=False,
    parse_dates=False,
    date_parser=None,
    thousands=None,
    comment=None,
    skipfooter=0,
    convert_float=True,
    mangle_dupe_cols=True,
    _bodo_df_type=None,
):
    with numba.objmode(df="{}"):
        df = pd.read_excel(
            io,
            sheet_name,
            header,
            {},
            index_col,
            usecols,
            squeeze,
            {{{}}},
            engine,
            converters,
            true_values,
            false_values,
            skiprows,
            nrows,
            na_values,
            keep_default_na,
            na_filter,
            verbose,
            {},
            date_parser,
            thousands,
            comment,
            skipfooter,
            convert_float,
            mangle_dupe_cols,
        )
    return df
    """
        .format(iyrd__axsw, list(df_type.columns), bdedu__els, iqyh__zoc))
    zseir__wkn = {}
    exec(zxfdb__tfq, globals(), zseir__wkn)
    impl = zseir__wkn['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    if bodo.compiler._matplotlib_installed:
        import matplotlib.pyplot as plt
    else:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    zxfdb__tfq = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    zxfdb__tfq += '    ylabel=None, title=None, legend=True, fontsize=None, \n'
    zxfdb__tfq += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        zxfdb__tfq += '   fig, ax = plt.subplots()\n'
    else:
        zxfdb__tfq += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        zxfdb__tfq += '   fig.set_figwidth(figsize[0])\n'
        zxfdb__tfq += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        zxfdb__tfq += '   xlabel = x\n'
    zxfdb__tfq += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        zxfdb__tfq += '   ylabel = y\n'
    else:
        zxfdb__tfq += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        zxfdb__tfq += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        zxfdb__tfq += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    zxfdb__tfq += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            zxfdb__tfq += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            ypwvs__nji = get_overload_const_str(x)
            gsxfq__wocr = df.columns.index(ypwvs__nji)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if gsxfq__wocr != i:
                        zxfdb__tfq += (
                            f'   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])\n'
                            )
        else:
            zxfdb__tfq += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        zxfdb__tfq += '   ax.scatter(df[x], df[y], s=20)\n'
        zxfdb__tfq += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        zxfdb__tfq += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        zxfdb__tfq += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        zxfdb__tfq += '   ax.legend()\n'
    zxfdb__tfq += '   return ax\n'
    zseir__wkn = {}
    exec(zxfdb__tfq, {'bodo': bodo, 'plt': plt}, zseir__wkn)
    impl = zseir__wkn['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for vge__dddmg in df_typ.data:
        if not (isinstance(vge__dddmg, IntegerArrayType) or isinstance(
            vge__dddmg.dtype, types.Number) or vge__dddmg.dtype in (bodo.
            datetime64ns, bodo.timedelta64ns)):
            return False
    return True


def typeref_to_type(v):
    if isinstance(v, types.BaseTuple):
        return types.BaseTuple.from_types(tuple(typeref_to_type(a) for a in v))
    return v.instance_type if isinstance(v, (types.TypeRef, types.NumberClass)
        ) else v


def _install_typer_for_type(type_name, typ):

    @type_callable(typ)
    def type_call_type(context):

        def typer(*args, **kws):
            args = tuple(typeref_to_type(v) for v in args)
            kws = {name: typeref_to_type(v) for name, v in kws.items()}
            return types.TypeRef(typ(*args, **kws))
        return typer
    no_side_effect_call_tuples.add((type_name, bodo))
    no_side_effect_call_tuples.add((typ,))


def _install_type_call_typers():
    for type_name in bodo_types_with_params:
        typ = getattr(bodo, type_name)
        _install_typer_for_type(type_name, typ)


_install_type_call_typers()


def set_df_col(df, cname, arr, inplace):
    df[cname] = arr


@infer_global(set_df_col)
class SetDfColInfer(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        assert not kws
        assert len(args) == 4
        assert isinstance(args[1], types.Literal)
        gkqok__ign = args[0]
        pwxqk__ezdx = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        gol__kqvki = gkqok__ign
        check_runtime_cols_unsupported(gkqok__ign, 'set_df_col()')
        if isinstance(gkqok__ign, DataFrameType):
            index = gkqok__ign.index
            if len(gkqok__ign.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(gkqok__ign.columns) == 0:
                    index = val.index
                val = val.data
            if is_pd_index_type(val):
                val = bodo.utils.typing.get_index_data_arr_types(val)[0]
            if isinstance(val, types.List):
                val = dtype_to_array_type(val.dtype)
            if not is_array_typ(val):
                val = dtype_to_array_type(val)
            if pwxqk__ezdx in gkqok__ign.columns:
                ael__gcuay = gkqok__ign.columns
                epjhw__damv = gkqok__ign.columns.index(pwxqk__ezdx)
                tkft__jkto = list(gkqok__ign.data)
                tkft__jkto[epjhw__damv] = val
                tkft__jkto = tuple(tkft__jkto)
            else:
                ael__gcuay = gkqok__ign.columns + (pwxqk__ezdx,)
                tkft__jkto = gkqok__ign.data + (val,)
            gol__kqvki = DataFrameType(tkft__jkto, index, ael__gcuay,
                gkqok__ign.dist, gkqok__ign.is_table_format)
        return gol__kqvki(*args)


SetDfColInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    bubyq__oytbf = {}

    def _rewrite_membership_op(self, node, left, right):
        yrqx__yjz = node.op
        op = self.visit(yrqx__yjz)
        return op, yrqx__yjz, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    kfh__weooq = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in kfh__weooq:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in kfh__weooq:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        inrcx__nol = node.attr
        value = node.value
        riy__sqj = pd.core.computation.ops.LOCAL_TAG
        if inrcx__nol in ('str', 'dt'):
            try:
                qvs__nuzx = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as jmtaw__efag:
                col_name = jmtaw__efag.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            qvs__nuzx = str(self.visit(value))
        vusb__mmrf = qvs__nuzx, inrcx__nol
        if vusb__mmrf in join_cleaned_cols:
            inrcx__nol = join_cleaned_cols[vusb__mmrf]
        name = qvs__nuzx + '.' + inrcx__nol
        if name.startswith(riy__sqj):
            name = name[len(riy__sqj):]
        if inrcx__nol in ('str', 'dt'):
            tkbiq__lkvjo = columns[cleaned_columns.index(qvs__nuzx)]
            bubyq__oytbf[tkbiq__lkvjo] = qvs__nuzx
            self.env.scope[name] = 0
            return self.term_type(riy__sqj + name, self.env)
        kfh__weooq.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in kfh__weooq:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        okh__cpqba = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        pwxqk__ezdx = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(okh__cpqba), pwxqk__ezdx))

    def op__str__(self):
        bntaz__oyitm = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            muq__xfgdk)) for muq__xfgdk in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(bntaz__oyitm)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(bntaz__oyitm)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(bntaz__oyitm))
    kkd__wmtq = pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op
    ehbxn__qogqg = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_evaluate_binop)
    oizcb__gjzde = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    tfau__ogy = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    ndwbr__zpy = pd.core.computation.ops.Term.__str__
    rzu__yke = pd.core.computation.ops.MathCall.__str__
    drhf__umno = pd.core.computation.ops.Op.__str__
    rgrki__wvw = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
    try:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            _rewrite_membership_op)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            _maybe_evaluate_binop)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = (
            visit_Attribute)
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = lambda self, left, right: (left, right)
        pd.core.computation.ops.Term.__str__ = __str__
        pd.core.computation.ops.MathCall.__str__ = math__str__
        pd.core.computation.ops.Op.__str__ = op__str__
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        meag__azl = pd.core.computation.expr.Expr(expr, env=env)
        yrwp__xam = str(meag__azl)
    except pd.core.computation.ops.UndefinedVariableError as jmtaw__efag:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == jmtaw__efag.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {jmtaw__efag}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            kkd__wmtq)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            ehbxn__qogqg)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = oizcb__gjzde
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = tfau__ogy
        pd.core.computation.ops.Term.__str__ = ndwbr__zpy
        pd.core.computation.ops.MathCall.__str__ = rzu__yke
        pd.core.computation.ops.Op.__str__ = drhf__umno
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            rgrki__wvw)
    kxuc__wmud = pd.core.computation.parsing.clean_column_name
    bubyq__oytbf.update({aavn__hcyl: kxuc__wmud(aavn__hcyl) for aavn__hcyl in
        columns if kxuc__wmud(aavn__hcyl) in meag__azl.names})
    return meag__azl, yrwp__xam, bubyq__oytbf


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        nmxqm__fwlih = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(nmxqm__fwlih))
        qzpvc__rtorf = namedtuple('Pandas', col_names)
        pffuu__sei = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], qzpvc__rtorf)
        super(DataFrameTupleIterator, self).__init__(name, pffuu__sei)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_series_dtype(arr_typ):
    if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
        return pd_timestamp_type
    return arr_typ.dtype


def get_itertuples():
    pass


@infer_global(get_itertuples)
class TypeIterTuples(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) % 2 == 0, 'name and column pairs expected'
        col_names = [a.literal_value for a in args[:len(args) // 2]]
        llsc__oejy = [if_series_to_array_type(a) for a in args[len(args) // 2:]
            ]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        llsc__oejy = [types.Array(types.int64, 1, 'C')] + llsc__oejy
        mzz__mzk = DataFrameTupleIterator(col_names, llsc__oejy)
        return mzz__mzk(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        iqeeo__pdz = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            iqeeo__pdz)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    ped__sxu = args[len(args) // 2:]
    nrga__cyoh = sig.args[len(sig.args) // 2:]
    nklu__dvjtx = context.make_helper(builder, sig.return_type)
    abbrb__obxvy = context.get_constant(types.intp, 0)
    kybjz__grw = cgutils.alloca_once_value(builder, abbrb__obxvy)
    nklu__dvjtx.index = kybjz__grw
    for i, arr in enumerate(ped__sxu):
        setattr(nklu__dvjtx, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(ped__sxu, nrga__cyoh):
        context.nrt.incref(builder, arr_typ, arr)
    res = nklu__dvjtx._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    imlew__jji, = sig.args
    mjz__womw, = args
    nklu__dvjtx = context.make_helper(builder, imlew__jji, value=mjz__womw)
    ndk__uas = signature(types.intp, imlew__jji.array_types[1])
    bkm__tpdui = context.compile_internal(builder, lambda a: len(a),
        ndk__uas, [nklu__dvjtx.array0])
    index = builder.load(nklu__dvjtx.index)
    lcz__oft = builder.icmp(lc.ICMP_SLT, index, bkm__tpdui)
    result.set_valid(lcz__oft)
    with builder.if_then(lcz__oft):
        values = [index]
        for i, arr_typ in enumerate(imlew__jji.array_types[1:]):
            lnuks__euju = getattr(nklu__dvjtx, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                oazif__rwyov = signature(pd_timestamp_type, arr_typ, types.intp
                    )
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    oazif__rwyov, [lnuks__euju, index])
            else:
                oazif__rwyov = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    oazif__rwyov, [lnuks__euju, index])
            values.append(val)
        value = context.make_tuple(builder, imlew__jji.yield_type, values)
        result.yield_(value)
        kyjde__nqfpl = cgutils.increment_index(builder, index)
        builder.store(kyjde__nqfpl, nklu__dvjtx.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    ehedg__evwpk = ir.Assign(rhs, lhs, expr.loc)
    kmde__dsb = lhs
    lcjf__edid = []
    jirmd__czn = []
    ree__bwemv = typ.count
    for i in range(ree__bwemv):
        cgwn__wvitp = ir.Var(kmde__dsb.scope, mk_unique_var('{}_size{}'.
            format(kmde__dsb.name, i)), kmde__dsb.loc)
        jiza__gvi = ir.Expr.static_getitem(lhs, i, None, kmde__dsb.loc)
        self.calltypes[jiza__gvi] = None
        lcjf__edid.append(ir.Assign(jiza__gvi, cgwn__wvitp, kmde__dsb.loc))
        self._define(equiv_set, cgwn__wvitp, types.intp, jiza__gvi)
        jirmd__czn.append(cgwn__wvitp)
    gtg__iqc = tuple(jirmd__czn)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        gtg__iqc, pre=[ehedg__evwpk] + lcjf__edid)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
