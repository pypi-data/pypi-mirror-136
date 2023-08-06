"""
Implementation of Series attributes and methods using overload.
"""
import operator
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_builtin, overload, overload_attribute, overload_method, register_jitable
import bodo
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.datetime_timedelta_ext import PDTimeDeltaType, datetime_timedelta_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.pd_offsets_ext import is_offsets_type
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType, if_series_to_array_type, is_series_type
from bodo.hiframes.pd_timestamp_ext import PandasTimestampType, pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.transform import gen_const_tup, is_var_size_item_array_type
from bodo.utils.typing import BodoError, can_replace, check_unsupported_args, dtype_to_array_type, element_type, get_common_scalar_dtype, get_literal_value, get_overload_const_bytes, get_overload_const_int, get_overload_const_str, is_common_scalar_dtype, is_iterable_type, is_literal_type, is_nullable_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_bytes, is_overload_constant_int, is_overload_constant_nan, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, is_scalar_type, raise_bodo_error, to_nullable_type


@overload_attribute(HeterogeneousSeriesType, 'index', inline='always')
@overload_attribute(SeriesType, 'index', inline='always')
def overload_series_index(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_index(s)


@overload_attribute(HeterogeneousSeriesType, 'values', inline='always')
@overload_attribute(SeriesType, 'values', inline='always')
def overload_series_values(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s)


@overload_attribute(SeriesType, 'dtype', inline='always')
def overload_series_dtype(s):
    if s.dtype == bodo.string_type:
        raise BodoError('Series.dtype not supported for string Series yet')
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s).dtype


@overload_attribute(HeterogeneousSeriesType, 'shape')
@overload_attribute(SeriesType, 'shape')
def overload_series_shape(s):
    return lambda s: (len(bodo.hiframes.pd_series_ext.get_series_data(s)),)


@overload_attribute(HeterogeneousSeriesType, 'ndim', inline='always')
@overload_attribute(SeriesType, 'ndim', inline='always')
def overload_series_ndim(s):
    return lambda s: 1


@overload_attribute(HeterogeneousSeriesType, 'size')
@overload_attribute(SeriesType, 'size')
def overload_series_size(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s))


@overload_attribute(HeterogeneousSeriesType, 'T', inline='always')
@overload_attribute(SeriesType, 'T', inline='always')
def overload_series_T(s):
    return lambda s: s


@overload_attribute(SeriesType, 'hasnans', inline='always')
def overload_series_hasnans(s):
    return lambda s: s.isna().sum() != 0


@overload_attribute(HeterogeneousSeriesType, 'empty')
@overload_attribute(SeriesType, 'empty')
def overload_series_empty(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s)) == 0


@overload_attribute(SeriesType, 'dtypes', inline='always')
def overload_series_dtypes(s):
    return lambda s: s.dtype


@overload_attribute(HeterogeneousSeriesType, 'name', inline='always')
@overload_attribute(SeriesType, 'name', inline='always')
def overload_series_name(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_name(s)


@overload(len, no_unliteral=True)
def overload_series_len(S):
    if isinstance(S, (SeriesType, HeterogeneousSeriesType)):
        return lambda S: len(bodo.hiframes.pd_series_ext.get_series_data(S))


@overload_method(SeriesType, 'copy', inline='always', no_unliteral=True)
def overload_series_copy(S, deep=True):
    if is_overload_true(deep):

        def impl1(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr.copy(),
                index, name)
        return impl1
    if is_overload_false(deep):

        def impl2(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl2

    def impl(S, deep=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        if deep:
            arr = arr.copy()
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
    return impl


@overload_method(SeriesType, 'to_list', no_unliteral=True)
@overload_method(SeriesType, 'tolist', no_unliteral=True)
def overload_series_to_list(S):
    if isinstance(S.dtype, types.Float):

        def impl_float(S):
            zfnj__mix = list()
            for kaf__dsmqb in range(len(S)):
                zfnj__mix.append(S.iat[kaf__dsmqb])
            return zfnj__mix
        return impl_float

    def impl(S):
        zfnj__mix = list()
        for kaf__dsmqb in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, kaf__dsmqb):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            zfnj__mix.append(S.iat[kaf__dsmqb])
        return zfnj__mix
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    kgl__bmhk = dict(dtype=dtype, copy=copy, na_value=na_value)
    bxdi__nnpd = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    kgl__bmhk = dict(name=name, inplace=inplace)
    bxdi__nnpd = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not bodo.hiframes.dataframe_impl._is_all_levels(S, level):
        raise_bodo_error(
            'Series.reset_index(): only dropping all index levels supported')
    if not is_overload_constant_bool(drop):
        raise_bodo_error(
            "Series.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if is_overload_true(drop):

        def impl_drop(S, level=None, drop=False, name=None, inplace=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_index_ext.init_range_index(0, len(arr),
                1, None)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl_drop

    def get_name_literal(name_typ, is_index=False, series_name=None):
        if is_overload_none(name_typ):
            if is_index:
                return 'index' if series_name != 'index' else 'level_0'
            return 0
        if is_literal_type(name_typ):
            return get_literal_value(name_typ)
        else:
            raise BodoError(
                'Series.reset_index() not supported for non-literal series names'
                )
    series_name = get_name_literal(S.name_typ)
    xlpoy__eumbl = get_name_literal(S.index.name_typ, True, series_name)
    gkdoy__fyymi = [xlpoy__eumbl, series_name]
    lrq__tqrvf = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    lrq__tqrvf += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    lrq__tqrvf += """    index = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S))
"""
    lrq__tqrvf += """    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)
"""
    lrq__tqrvf += '    col_var = {}\n'.format(gen_const_tup(gkdoy__fyymi))
    lrq__tqrvf += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe((index, arr), df_index, col_var)
"""
    qvx__ahvui = {}
    exec(lrq__tqrvf, {'bodo': bodo}, qvx__ahvui)
    ztx__yfw = qvx__ahvui['_impl']
    return ztx__yfw


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zwfsp__ipp = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)
    return impl


@overload_method(SeriesType, 'round', inline='always', no_unliteral=True)
def overload_series_round(S, decimals=0):

    def impl(S, decimals=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        zwfsp__ipp = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[kaf__dsmqb]):
                bodo.libs.array_kernels.setna(zwfsp__ipp, kaf__dsmqb)
            else:
                zwfsp__ipp[kaf__dsmqb] = np.round(arr[kaf__dsmqb], decimals)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    kgl__bmhk = dict(level=level, numeric_only=numeric_only)
    bxdi__nnpd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sum(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sum(): skipna argument must be a boolean')
    if not is_overload_int(min_count):
        raise BodoError('Series.sum(): min_count argument must be an integer')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_sum(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'prod', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'product', inline='always', no_unliteral=True)
def overload_series_prod(S, axis=None, skipna=True, level=None,
    numeric_only=None, min_count=0):
    kgl__bmhk = dict(level=level, numeric_only=numeric_only)
    bxdi__nnpd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.product(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.product(): skipna argument must be a boolean')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_prod(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'any', inline='always', no_unliteral=True)
def overload_series_any(S, axis=0, bool_only=None, skipna=True, level=None):
    kgl__bmhk = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=level
        )
    bxdi__nnpd = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        gcu__fdjha = 0
        for kaf__dsmqb in numba.parfors.parfor.internal_prange(len(A)):
            kmbey__twl = 0
            if not bodo.libs.array_kernels.isna(A, kaf__dsmqb):
                kmbey__twl = int(A[kaf__dsmqb])
            gcu__fdjha += kmbey__twl
        return gcu__fdjha != 0
    return impl


@overload_method(SeriesType, 'equals', inline='always', no_unliteral=True)
def overload_series_equals(S, other):
    if not isinstance(other, SeriesType):
        raise BodoError("Series.equals() 'other' must be a Series")
    if isinstance(S.data, bodo.ArrayItemArrayType):
        raise BodoError(
            'Series.equals() not supported for Series where each element is an array or list'
            )
    if S.data != other.data:
        return lambda S, other: False

    def impl(S, other):
        sip__axat = bodo.hiframes.pd_series_ext.get_series_data(S)
        zqhni__mkyey = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        gcu__fdjha = 0
        for kaf__dsmqb in numba.parfors.parfor.internal_prange(len(sip__axat)):
            kmbey__twl = 0
            dvyw__owy = bodo.libs.array_kernels.isna(sip__axat, kaf__dsmqb)
            oygjc__lcm = bodo.libs.array_kernels.isna(zqhni__mkyey, kaf__dsmqb)
            if dvyw__owy and not oygjc__lcm or not dvyw__owy and oygjc__lcm:
                kmbey__twl = 1
            elif not dvyw__owy:
                if sip__axat[kaf__dsmqb] != zqhni__mkyey[kaf__dsmqb]:
                    kmbey__twl = 1
            gcu__fdjha += kmbey__twl
        return gcu__fdjha == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    kgl__bmhk = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=level
        )
    bxdi__nnpd = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        gcu__fdjha = 0
        for kaf__dsmqb in numba.parfors.parfor.internal_prange(len(A)):
            kmbey__twl = 0
            if not bodo.libs.array_kernels.isna(A, kaf__dsmqb):
                kmbey__twl = int(not A[kaf__dsmqb])
            gcu__fdjha += kmbey__twl
        return gcu__fdjha == 0
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    kgl__bmhk = dict(level=level)
    bxdi__nnpd = dict(level=None)
    check_unsupported_args('Series.mad', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    kztw__fkrnt = types.float64
    uokr__afusd = types.float64
    if S.dtype == types.float32:
        kztw__fkrnt = types.float32
        uokr__afusd = types.float32
    kqjhg__fxtjg = kztw__fkrnt(0)
    ccdgh__nylfa = uokr__afusd(0)
    sbdz__kploj = uokr__afusd(1)

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        skgw__dphs = kqjhg__fxtjg
        gcu__fdjha = ccdgh__nylfa
        for kaf__dsmqb in numba.parfors.parfor.internal_prange(len(A)):
            kmbey__twl = kqjhg__fxtjg
            zyc__kqf = ccdgh__nylfa
            if not bodo.libs.array_kernels.isna(A, kaf__dsmqb) or not skipna:
                kmbey__twl = A[kaf__dsmqb]
                zyc__kqf = sbdz__kploj
            skgw__dphs += kmbey__twl
            gcu__fdjha += zyc__kqf
        ichv__alg = bodo.hiframes.series_kernels._mean_handle_nan(skgw__dphs,
            gcu__fdjha)
        ndgbm__pshj = kqjhg__fxtjg
        for kaf__dsmqb in numba.parfors.parfor.internal_prange(len(A)):
            kmbey__twl = kqjhg__fxtjg
            if not bodo.libs.array_kernels.isna(A, kaf__dsmqb) or not skipna:
                kmbey__twl = abs(A[kaf__dsmqb] - ichv__alg)
            ndgbm__pshj += kmbey__twl
        hkuz__rob = bodo.hiframes.series_kernels._mean_handle_nan(ndgbm__pshj,
            gcu__fdjha)
        return hkuz__rob
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    kgl__bmhk = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    bxdi__nnpd = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mean(): axis argument not supported')

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_mean(arr)
    return impl


@overload_method(SeriesType, 'sem', inline='always', no_unliteral=True)
def overload_series_sem(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    kgl__bmhk = dict(level=level, numeric_only=numeric_only)
    bxdi__nnpd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sem(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sem(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.sem(): ddof argument must be an integer')

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        malw__ejz = 0
        srzg__bzilf = 0
        gcu__fdjha = 0
        for kaf__dsmqb in numba.parfors.parfor.internal_prange(len(A)):
            kmbey__twl = 0
            zyc__kqf = 0
            if not bodo.libs.array_kernels.isna(A, kaf__dsmqb) or not skipna:
                kmbey__twl = A[kaf__dsmqb]
                zyc__kqf = 1
            malw__ejz += kmbey__twl
            srzg__bzilf += kmbey__twl * kmbey__twl
            gcu__fdjha += zyc__kqf
        s = srzg__bzilf - malw__ejz * malw__ejz / gcu__fdjha
        dop__xeur = bodo.hiframes.series_kernels._handle_nan_count_ddof(s,
            gcu__fdjha, ddof)
        vwpq__yld = (dop__xeur / gcu__fdjha) ** 0.5
        return vwpq__yld
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    kgl__bmhk = dict(level=level, numeric_only=numeric_only)
    bxdi__nnpd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.kurtosis(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError(
            "Series.kurtosis(): 'skipna' argument must be a boolean")

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        malw__ejz = 0.0
        srzg__bzilf = 0.0
        pszdy__vklvh = 0.0
        emzts__hxlzr = 0.0
        gcu__fdjha = 0
        for kaf__dsmqb in numba.parfors.parfor.internal_prange(len(A)):
            kmbey__twl = 0.0
            zyc__kqf = 0
            if not bodo.libs.array_kernels.isna(A, kaf__dsmqb) or not skipna:
                kmbey__twl = np.float64(A[kaf__dsmqb])
                zyc__kqf = 1
            malw__ejz += kmbey__twl
            srzg__bzilf += kmbey__twl ** 2
            pszdy__vklvh += kmbey__twl ** 3
            emzts__hxlzr += kmbey__twl ** 4
            gcu__fdjha += zyc__kqf
        dop__xeur = bodo.hiframes.series_kernels.compute_kurt(malw__ejz,
            srzg__bzilf, pszdy__vklvh, emzts__hxlzr, gcu__fdjha)
        return dop__xeur
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    kgl__bmhk = dict(level=level, numeric_only=numeric_only)
    bxdi__nnpd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.skew(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.skew(): skipna argument must be a boolean')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        malw__ejz = 0.0
        srzg__bzilf = 0.0
        pszdy__vklvh = 0.0
        gcu__fdjha = 0
        for kaf__dsmqb in numba.parfors.parfor.internal_prange(len(A)):
            kmbey__twl = 0.0
            zyc__kqf = 0
            if not bodo.libs.array_kernels.isna(A, kaf__dsmqb) or not skipna:
                kmbey__twl = np.float64(A[kaf__dsmqb])
                zyc__kqf = 1
            malw__ejz += kmbey__twl
            srzg__bzilf += kmbey__twl ** 2
            pszdy__vklvh += kmbey__twl ** 3
            gcu__fdjha += zyc__kqf
        dop__xeur = bodo.hiframes.series_kernels.compute_skew(malw__ejz,
            srzg__bzilf, pszdy__vklvh, gcu__fdjha)
        return dop__xeur
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    kgl__bmhk = dict(level=level, numeric_only=numeric_only)
    bxdi__nnpd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.var(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.var(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.var(): ddof argument must be an integer')

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_var(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'std', inline='always', no_unliteral=True)
def overload_series_std(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    kgl__bmhk = dict(level=level, numeric_only=numeric_only)
    bxdi__nnpd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.std(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.std(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.std(): ddof argument must be an integer')

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_std(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'dot', inline='always', no_unliteral=True)
def overload_series_dot(S, other):

    def impl(S, other):
        sip__axat = bodo.hiframes.pd_series_ext.get_series_data(S)
        zqhni__mkyey = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        qyp__xqg = 0
        for kaf__dsmqb in numba.parfors.parfor.internal_prange(len(sip__axat)):
            cbzkp__beycp = sip__axat[kaf__dsmqb]
            hfsf__bvabs = zqhni__mkyey[kaf__dsmqb]
            qyp__xqg += cbzkp__beycp * hfsf__bvabs
        return qyp__xqg
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    kgl__bmhk = dict(skipna=skipna)
    bxdi__nnpd = dict(skipna=True)
    check_unsupported_args('Series.cumsum', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumsum(): axis argument not supported')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumsum(), index, name)
    return impl


@overload_method(SeriesType, 'cumprod', inline='always', no_unliteral=True)
def overload_series_cumprod(S, axis=None, skipna=True):
    kgl__bmhk = dict(skipna=skipna)
    bxdi__nnpd = dict(skipna=True)
    check_unsupported_args('Series.cumprod', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumprod(): axis argument not supported')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumprod(), index, name
            )
    return impl


@overload_method(SeriesType, 'cummin', inline='always', no_unliteral=True)
def overload_series_cummin(S, axis=None, skipna=True):
    kgl__bmhk = dict(skipna=skipna)
    bxdi__nnpd = dict(skipna=True)
    check_unsupported_args('Series.cummin', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummin(): axis argument not supported')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummin(arr), index, name)
    return impl


@overload_method(SeriesType, 'cummax', inline='always', no_unliteral=True)
def overload_series_cummax(S, axis=None, skipna=True):
    kgl__bmhk = dict(skipna=skipna)
    bxdi__nnpd = dict(skipna=True)
    check_unsupported_args('Series.cummax', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummax(): axis argument not supported')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummax(arr), index, name)
    return impl


@overload_method(SeriesType, 'rename', inline='always', no_unliteral=True)
def overload_series_rename(S, index=None, axis=None, copy=True, inplace=
    False, level=None, errors='ignore'):
    if not (index == bodo.string_type or isinstance(index, types.StringLiteral)
        ):
        raise BodoError("Series.rename() 'index' can only be a string")
    kgl__bmhk = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    bxdi__nnpd = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        hsvmb__jahxl = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, hsvmb__jahxl, index)
    return impl


@overload_method(SeriesType, 'abs', inline='always', no_unliteral=True)
def overload_series_abs(S):

    def impl(S):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(np.abs(A), index, name)
    return impl


@overload_method(SeriesType, 'count', no_unliteral=True)
def overload_series_count(S, level=None):
    kgl__bmhk = dict(level=level)
    bxdi__nnpd = dict(level=None)
    check_unsupported_args('Series.count', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    kgl__bmhk = dict(method=method, min_periods=min_periods)
    bxdi__nnpd = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        llb__rvex = S.sum()
        mez__xqcq = other.sum()
        a = n * (S * other).sum() - llb__rvex * mez__xqcq
        wvuw__cwdp = n * (S ** 2).sum() - llb__rvex ** 2
        mcxki__lkasf = n * (other ** 2).sum() - mez__xqcq ** 2
        return a / np.sqrt(wvuw__cwdp * mcxki__lkasf)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    kgl__bmhk = dict(min_periods=min_periods)
    bxdi__nnpd = dict(min_periods=None)
    check_unsupported_args('Series.cov', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')

    def impl(S, other, min_periods=None, ddof=1):
        llb__rvex = S.mean()
        mez__xqcq = other.mean()
        erjbx__qeaxr = ((S - llb__rvex) * (other - mez__xqcq)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(erjbx__qeaxr, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            safrv__tbyf = np.sign(sum_val)
            return np.inf * safrv__tbyf
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    kgl__bmhk = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    bxdi__nnpd = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.min(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.min(): only ordered categoricals are possible')

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_min(arr)
    return impl


@overload(max, no_unliteral=True)
def overload_series_builtins_max(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.max()
        return impl


@overload(min, no_unliteral=True)
def overload_series_builtins_min(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.min()
        return impl


@overload(sum, no_unliteral=True)
def overload_series_builtins_sum(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.sum()
        return impl


@overload(np.prod, inline='always', no_unliteral=True)
def overload_series_np_prod(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.prod()
        return impl


@overload_method(SeriesType, 'max', inline='always', no_unliteral=True)
def overload_series_max(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    kgl__bmhk = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    bxdi__nnpd = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.max(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.max(): only ordered categoricals are possible')

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_max(arr)
    return impl


@overload_method(SeriesType, 'idxmin', inline='always', no_unliteral=True)
def overload_series_idxmin(S, axis=0, skipna=True):
    kgl__bmhk = dict(axis=axis, skipna=skipna)
    bxdi__nnpd = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmin() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmin(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmin(arr, index)
    return impl


@overload_method(SeriesType, 'idxmax', inline='always', no_unliteral=True)
def overload_series_idxmax(S, axis=0, skipna=True):
    kgl__bmhk = dict(axis=axis, skipna=skipna)
    bxdi__nnpd = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmax() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmax(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmax(arr, index)
    return impl


@overload_method(SeriesType, 'infer_objects', inline='always')
def overload_series_infer_objects(S):
    return lambda S: S.copy()


@overload_attribute(SeriesType, 'is_monotonic', inline='always')
@overload_attribute(SeriesType, 'is_monotonic_increasing', inline='always')
def overload_series_is_monotonic_increasing(S):
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 1)


@overload_attribute(SeriesType, 'is_monotonic_decreasing', inline='always')
def overload_series_is_monotonic_decreasing(S):
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 2)


@overload_attribute(SeriesType, 'nbytes', inline='always')
def overload_series_nbytes(S):
    return lambda S: bodo.hiframes.pd_series_ext.get_series_data(S).nbytes


@overload_method(SeriesType, 'autocorr', inline='always', no_unliteral=True)
def overload_series_autocorr(S, lag=1):
    return lambda S, lag=1: bodo.libs.array_kernels.autocorr(bodo.hiframes.
        pd_series_ext.get_series_data(S), lag)


@overload_method(SeriesType, 'median', inline='always', no_unliteral=True)
def overload_series_median(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    kgl__bmhk = dict(level=level, numeric_only=numeric_only)
    bxdi__nnpd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.median(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.median(): skipna argument must be a boolean')
    return (lambda S, axis=None, skipna=True, level=None, numeric_only=None:
        bodo.libs.array_ops.array_op_median(bodo.hiframes.pd_series_ext.
        get_series_data(S), skipna))


def overload_series_head(S, n=5):

    def impl(S, n=5):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        gyb__nkn = arr[:n]
        zhzek__see = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(gyb__nkn, zhzek__see,
            name)
    return impl


@lower_builtin('series.head', SeriesType, types.Integer)
@lower_builtin('series.head', SeriesType, types.Omitted)
def series_head_lower(context, builder, sig, args):
    impl = overload_series_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@numba.extending.register_jitable
def tail_slice(k, n):
    if n == 0:
        return k
    return -n


@overload_method(SeriesType, 'tail', inline='always', no_unliteral=True)
def overload_series_tail(S, n=5):
    if not is_overload_int(n):
        raise BodoError("Series.tail(): 'n' must be an Integer")

    def impl(S, n=5):
        phqqo__lff = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        gyb__nkn = arr[phqqo__lff:]
        zhzek__see = index[phqqo__lff:]
        return bodo.hiframes.pd_series_ext.init_series(gyb__nkn, zhzek__see,
            name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    hhodx__uga = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in hhodx__uga:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            sil__kzovp = index[0]
            ybues__pqmo = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                sil__kzovp, False))
        else:
            ybues__pqmo = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        gyb__nkn = arr[:ybues__pqmo]
        zhzek__see = index[:ybues__pqmo]
        return bodo.hiframes.pd_series_ext.init_series(gyb__nkn, zhzek__see,
            name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    hhodx__uga = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in hhodx__uga:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            lqf__scntc = index[-1]
            ybues__pqmo = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                lqf__scntc, True))
        else:
            ybues__pqmo = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        gyb__nkn = arr[len(arr) - ybues__pqmo:]
        zhzek__see = index[len(arr) - ybues__pqmo:]
        return bodo.hiframes.pd_series_ext.init_series(gyb__nkn, zhzek__see,
            name)
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    kgl__bmhk = dict(keep=keep)
    bxdi__nnpd = dict(keep='first')
    check_unsupported_args('Series.nlargest', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        xrr__spwt = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zwfsp__ipp, hpc__fyvwg = bodo.libs.array_kernels.nlargest(arr,
            xrr__spwt, n, True, bodo.hiframes.series_kernels.gt_f)
        qmra__vdwl = bodo.utils.conversion.convert_to_index(hpc__fyvwg)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
            qmra__vdwl, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    kgl__bmhk = dict(keep=keep)
    bxdi__nnpd = dict(keep='first')
    check_unsupported_args('Series.nsmallest', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        xrr__spwt = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zwfsp__ipp, hpc__fyvwg = bodo.libs.array_kernels.nlargest(arr,
            xrr__spwt, n, False, bodo.hiframes.series_kernels.lt_f)
        qmra__vdwl = bodo.utils.conversion.convert_to_index(hpc__fyvwg)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
            qmra__vdwl, name)
    return impl


@overload_method(SeriesType, 'notnull', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'notna', inline='always', no_unliteral=True)
def overload_series_notna(S):
    return lambda S: S.isna() == False


@overload_method(SeriesType, 'astype', inline='always', no_unliteral=True)
def overload_series_astype(S, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True):
    kgl__bmhk = dict(errors=errors)
    bxdi__nnpd = dict(errors='raise')
    check_unsupported_args('Series.astype', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "Series.astype(): 'dtype' when passed as string must be a constant value"
            )

    def impl(S, dtype, copy=True, errors='raise', _bodo_nan_to_str=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zwfsp__ipp = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    kgl__bmhk = dict(axis=axis, is_copy=is_copy)
    bxdi__nnpd = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        zow__wytez = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[zow__wytez],
            index[zow__wytez], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    kgl__bmhk = dict(axis=axis, kind=kind, order=order)
    bxdi__nnpd = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ydz__kbh = S.notna().values
        if not ydz__kbh.all():
            zwfsp__ipp = np.full(n, -1, np.int64)
            zwfsp__ipp[ydz__kbh] = argsort(arr[ydz__kbh])
        else:
            zwfsp__ipp = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    kgl__bmhk = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    bxdi__nnpd = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        cnfs__wgpln = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, ('$_bodo_col3_',))
        cled__dorws = cnfs__wgpln.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        zwfsp__ipp = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            cled__dorws, 0)
        qmra__vdwl = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            cled__dorws)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
            qmra__vdwl, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    kgl__bmhk = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    bxdi__nnpd = dict(axis=0, inplace=False, kind='quicksort', ignore_index
        =False, key=None)
    check_unsupported_args('Series.sort_values', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        cnfs__wgpln = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, ('$_bodo_col_',))
        cled__dorws = cnfs__wgpln.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        zwfsp__ipp = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            cled__dorws, 0)
        qmra__vdwl = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            cled__dorws)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
            qmra__vdwl, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    lcoy__fsx = is_overload_true(is_nullable)
    lrq__tqrvf = (
        'def impl(bins, arr, is_nullable=True, include_lowest=True):\n')
    lrq__tqrvf += '  numba.parfors.parfor.init_prange()\n'
    lrq__tqrvf += '  n = len(arr)\n'
    if lcoy__fsx:
        lrq__tqrvf += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        lrq__tqrvf += '  out_arr = np.empty(n, np.int64)\n'
    lrq__tqrvf += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    lrq__tqrvf += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if lcoy__fsx:
        lrq__tqrvf += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        lrq__tqrvf += '      out_arr[i] = -1\n'
    lrq__tqrvf += '      continue\n'
    lrq__tqrvf += '    val = arr[i]\n'
    lrq__tqrvf += '    if include_lowest and val == bins[0]:\n'
    lrq__tqrvf += '      ind = 1\n'
    lrq__tqrvf += '    else:\n'
    lrq__tqrvf += '      ind = np.searchsorted(bins, val)\n'
    lrq__tqrvf += '    if ind == 0 or ind == len(bins):\n'
    if lcoy__fsx:
        lrq__tqrvf += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        lrq__tqrvf += '      out_arr[i] = -1\n'
    lrq__tqrvf += '    else:\n'
    lrq__tqrvf += '      out_arr[i] = ind - 1\n'
    lrq__tqrvf += '  return out_arr\n'
    qvx__ahvui = {}
    exec(lrq__tqrvf, {'bodo': bodo, 'np': np, 'numba': numba}, qvx__ahvui)
    impl = qvx__ahvui['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        kncol__smb, mxj__uwao = np.divmod(x, 1)
        if kncol__smb == 0:
            feku__tgz = -int(np.floor(np.log10(abs(mxj__uwao)))
                ) - 1 + precision
        else:
            feku__tgz = precision
        return np.around(x, feku__tgz)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        iuagd__xgx = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(iuagd__xgx)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        lffy__rwk = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            mtves__lvdby = bins.copy()
            if right and include_lowest:
                mtves__lvdby[0] = mtves__lvdby[0] - lffy__rwk
            avql__mdleh = bodo.libs.interval_arr_ext.init_interval_array(
                mtves__lvdby[:-1], mtves__lvdby[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(avql__mdleh,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        mtves__lvdby = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            mtves__lvdby[0] = mtves__lvdby[0] - 10.0 ** -precision
        avql__mdleh = bodo.libs.interval_arr_ext.init_interval_array(
            mtves__lvdby[:-1], mtves__lvdby[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(avql__mdleh, None
            )
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        irhe__upow = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        ovwe__kps = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        zwfsp__ipp = np.zeros(nbins, np.int64)
        for kaf__dsmqb in range(len(irhe__upow)):
            zwfsp__ipp[ovwe__kps[kaf__dsmqb]] = irhe__upow[kaf__dsmqb]
        return zwfsp__ipp
    return impl


def compute_bins(nbins, min_val, max_val):
    pass


@overload(compute_bins, no_unliteral=True)
def overload_compute_bins(nbins, min_val, max_val, right=True):

    def impl(nbins, min_val, max_val, right=True):
        if nbins < 1:
            raise ValueError('`bins` should be a positive integer.')
        min_val = min_val + 0.0
        max_val = max_val + 0.0
        if np.isinf(min_val) or np.isinf(max_val):
            raise ValueError(
                'cannot specify integer `bins` when input data contains infinity'
                )
        elif min_val == max_val:
            min_val -= 0.001 * abs(min_val) if min_val != 0 else 0.001
            max_val += 0.001 * abs(max_val) if max_val != 0 else 0.001
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
        else:
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
            ahr__cxhp = (max_val - min_val) * 0.001
            if right:
                bins[0] -= ahr__cxhp
            else:
                bins[-1] += ahr__cxhp
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    kgl__bmhk = dict(dropna=dropna)
    bxdi__nnpd = dict(dropna=True)
    check_unsupported_args('Series.value_counts', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not is_overload_constant_bool(normalize):
        raise_bodo_error(
            'Series.value_counts(): normalize argument must be a constant boolean'
            )
    if not is_overload_constant_bool(sort):
        raise_bodo_error(
            'Series.value_counts(): sort argument must be a constant boolean')
    if not is_overload_bool(ascending):
        raise_bodo_error(
            'Series.value_counts(): ascending argument must be a constant boolean'
            )
    rwejg__rbb = not is_overload_none(bins)
    lrq__tqrvf = 'def impl(\n'
    lrq__tqrvf += '    S,\n'
    lrq__tqrvf += '    normalize=False,\n'
    lrq__tqrvf += '    sort=True,\n'
    lrq__tqrvf += '    ascending=False,\n'
    lrq__tqrvf += '    bins=None,\n'
    lrq__tqrvf += '    dropna=True,\n'
    lrq__tqrvf += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    lrq__tqrvf += '):\n'
    lrq__tqrvf += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    lrq__tqrvf += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    lrq__tqrvf += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if rwejg__rbb:
        lrq__tqrvf += '    right = True\n'
        lrq__tqrvf += _gen_bins_handling(bins, S.dtype)
        lrq__tqrvf += '    arr = get_bin_inds(bins, arr)\n'
    lrq__tqrvf += (
        '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
    lrq__tqrvf += "        (arr,), index, ('$_bodo_col2_',)\n"
    lrq__tqrvf += '    )\n'
    lrq__tqrvf += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if rwejg__rbb:
        lrq__tqrvf += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        lrq__tqrvf += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        lrq__tqrvf += '    index = get_bin_labels(bins)\n'
    else:
        lrq__tqrvf += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        lrq__tqrvf += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        lrq__tqrvf += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        lrq__tqrvf += '    )\n'
        lrq__tqrvf += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    lrq__tqrvf += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        lrq__tqrvf += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        yeqpn__aair = 'len(S)' if rwejg__rbb else 'count_arr.sum()'
        lrq__tqrvf += f'    res = res / float({yeqpn__aair})\n'
    lrq__tqrvf += '    return res\n'
    qvx__ahvui = {}
    exec(lrq__tqrvf, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, qvx__ahvui)
    impl = qvx__ahvui['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    lrq__tqrvf = ''
    if isinstance(bins, types.Integer):
        lrq__tqrvf += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        lrq__tqrvf += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            lrq__tqrvf += '    min_val = min_val.value\n'
            lrq__tqrvf += '    max_val = max_val.value\n'
        lrq__tqrvf += (
            '    bins = compute_bins(bins, min_val, max_val, right)\n')
        if dtype == bodo.datetime64ns:
            lrq__tqrvf += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        lrq__tqrvf += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return lrq__tqrvf


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    kgl__bmhk = dict(right=right, labels=labels, retbins=retbins, precision
        =precision, duplicates=duplicates, ordered=ordered)
    bxdi__nnpd = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='General')
    lrq__tqrvf = 'def impl(\n'
    lrq__tqrvf += '    x,\n'
    lrq__tqrvf += '    bins,\n'
    lrq__tqrvf += '    right=True,\n'
    lrq__tqrvf += '    labels=None,\n'
    lrq__tqrvf += '    retbins=False,\n'
    lrq__tqrvf += '    precision=3,\n'
    lrq__tqrvf += '    include_lowest=False,\n'
    lrq__tqrvf += "    duplicates='raise',\n"
    lrq__tqrvf += '    ordered=True\n'
    lrq__tqrvf += '):\n'
    if isinstance(x, SeriesType):
        lrq__tqrvf += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        lrq__tqrvf += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        lrq__tqrvf += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        lrq__tqrvf += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    lrq__tqrvf += _gen_bins_handling(bins, x.dtype)
    lrq__tqrvf += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    lrq__tqrvf += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    lrq__tqrvf += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    lrq__tqrvf += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        lrq__tqrvf += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        lrq__tqrvf += '    return res\n'
    else:
        lrq__tqrvf += '    return out_arr\n'
    qvx__ahvui = {}
    exec(lrq__tqrvf, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, qvx__ahvui)
    impl = qvx__ahvui['impl']
    return impl


def _get_q_list(q):
    return q


@overload(_get_q_list, no_unliteral=True)
def get_q_list_overload(q):
    if is_overload_int(q):
        return lambda q: np.linspace(0, 1, q + 1)
    return lambda q: q


@overload(pd.qcut, inline='always', no_unliteral=True)
def overload_qcut(x, q, labels=None, retbins=False, precision=3, duplicates
    ='raise'):
    kgl__bmhk = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    bxdi__nnpd = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        vdm__hok = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, vdm__hok)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    kgl__bmhk = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze=
        squeeze, observed=observed, dropna=dropna)
    bxdi__nnpd = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='GroupBy')
    if not is_overload_true(as_index):
        raise BodoError('as_index=False only valid with DataFrame')
    if is_overload_none(by) and is_overload_none(level):
        raise BodoError("You have to supply one of 'by' and 'level'")
    if not is_overload_none(by) and not is_overload_none(level):
        raise BodoError(
            "Series.groupby(): 'level' argument should be None if 'by' is not None"
            )
    if not is_overload_none(level):
        if not (is_overload_constant_int(level) and get_overload_const_int(
            level) == 0) or isinstance(S.index, bodo.hiframes.
            pd_multi_index_ext.MultiIndexType):
            raise BodoError(
                "Series.groupby(): MultiIndex case or 'level' other than 0 not supported yet"
                )

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            kbrf__fmo = bodo.utils.conversion.coerce_to_array(index)
            cnfs__wgpln = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                kbrf__fmo, arr), index, (' ', ''))
            return cnfs__wgpln.groupby(' ')['']
        return impl_index
    cpzap__pjcku = by
    if isinstance(by, SeriesType):
        cpzap__pjcku = by.data
    if isinstance(cpzap__pjcku, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        kbrf__fmo = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        cnfs__wgpln = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            kbrf__fmo, arr), index, (' ', ''))
        return cnfs__wgpln.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    kgl__bmhk = dict(verify_integrity=verify_integrity)
    bxdi__nnpd = dict(verify_integrity=False)
    check_unsupported_args('Series.append', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if isinstance(to_append, SeriesType):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S, to_append), ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    if isinstance(to_append, types.BaseTuple):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S,) + to_append, ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    return (lambda S, to_append, ignore_index=False, verify_integrity=False:
        pd.concat([S] + to_append, ignore_index=ignore_index,
        verify_integrity=verify_integrity))


@overload_method(SeriesType, 'isin', inline='always', no_unliteral=True)
def overload_series_isin(S, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(S, values):
            cwl__epdv = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            zwfsp__ipp = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(zwfsp__ipp, A, cwl__epdv, False)
            return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zwfsp__ipp = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    kgl__bmhk = dict(interpolation=interpolation)
    bxdi__nnpd = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            zwfsp__ipp = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                index, name)
        return impl_list
    elif isinstance(q, (float, types.Number)) or is_overload_constant_int(q):

        def impl(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return bodo.libs.array_ops.array_op_quantile(arr, q)
        return impl
    else:
        raise BodoError(
            f'Series.quantile() q type must be float or iterable of floats only.'
            )


@overload_method(SeriesType, 'nunique', inline='always', no_unliteral=True)
def overload_series_nunique(S, dropna=True):
    if not is_overload_bool(dropna):
        raise BodoError('Series.nunique: dropna must be a boolean value')

    def impl(S, dropna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_kernels.nunique(arr, dropna)
    return impl


@overload_method(SeriesType, 'unique', inline='always', no_unliteral=True)
def overload_series_unique(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        rgwle__xnzm = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(rgwle__xnzm, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    kgl__bmhk = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    bxdi__nnpd = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)
        ) and not isinstance(S.data, IntegerArrayType):
        raise BodoError(f'describe() column input type {S.data} not supported.'
            )
    if S.data.dtype == bodo.datetime64ns:

        def impl_dt(S, percentiles=None, include=None, exclude=None,
            datetime_is_numeric=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
                array_ops.array_op_describe(arr), bodo.utils.conversion.
                convert_to_index(['count', 'mean', 'min', '25%', '50%',
                '75%', 'max']), name)
        return impl_dt

    def impl(S, percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.array_ops.
            array_op_describe(arr), bodo.utils.conversion.convert_to_index(
            ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']), name)
    return impl


@overload_method(SeriesType, 'memory_usage', inline='always', no_unliteral=True
    )
def overload_series_memory_usage(S, index=True, deep=False):
    if is_overload_true(index):

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            return arr.nbytes + index.nbytes
        return impl
    else:

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return arr.nbytes
        return impl


def binary_str_fillna_inplace_series_impl(is_binary=False):
    if is_binary:
        ytbr__fboml = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        ytbr__fboml = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    lrq__tqrvf = 'def impl(\n'
    lrq__tqrvf += '    S,\n'
    lrq__tqrvf += '    value=None,\n'
    lrq__tqrvf += '    method=None,\n'
    lrq__tqrvf += '    axis=None,\n'
    lrq__tqrvf += '    inplace=False,\n'
    lrq__tqrvf += '    limit=None,\n'
    lrq__tqrvf += '    downcast=None,\n'
    lrq__tqrvf += '):  # pragma: no cover\n'
    lrq__tqrvf += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    lrq__tqrvf += (
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)\n')
    lrq__tqrvf += '    n = len(in_arr)\n'
    lrq__tqrvf += f'    out_arr = {ytbr__fboml}(n, -1)\n'
    lrq__tqrvf += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    lrq__tqrvf += '        s = in_arr[j]\n'
    lrq__tqrvf += """        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna(
"""
    lrq__tqrvf += '            fill_arr, j\n'
    lrq__tqrvf += '        ):\n'
    lrq__tqrvf += '            s = fill_arr[j]\n'
    lrq__tqrvf += '        out_arr[j] = s\n'
    lrq__tqrvf += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    xtf__ascc = dict()
    exec(lrq__tqrvf, {'bodo': bodo, 'numba': numba}, xtf__ascc)
    eulfo__rbxx = xtf__ascc['impl']
    return eulfo__rbxx


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        ytbr__fboml = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        ytbr__fboml = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    lrq__tqrvf = 'def impl(S,\n'
    lrq__tqrvf += '     value=None,\n'
    lrq__tqrvf += '    method=None,\n'
    lrq__tqrvf += '    axis=None,\n'
    lrq__tqrvf += '    inplace=False,\n'
    lrq__tqrvf += '    limit=None,\n'
    lrq__tqrvf += '   downcast=None,\n'
    lrq__tqrvf += '):\n'
    lrq__tqrvf += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    lrq__tqrvf += '    n = len(in_arr)\n'
    lrq__tqrvf += f'    out_arr = {ytbr__fboml}(n, -1)\n'
    lrq__tqrvf += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    lrq__tqrvf += '        s = in_arr[j]\n'
    lrq__tqrvf += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    lrq__tqrvf += '            s = value\n'
    lrq__tqrvf += '        out_arr[j] = s\n'
    lrq__tqrvf += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    xtf__ascc = dict()
    exec(lrq__tqrvf, {'bodo': bodo, 'numba': numba}, xtf__ascc)
    eulfo__rbxx = xtf__ascc['impl']
    return eulfo__rbxx


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    hbn__jwpo = bodo.hiframes.pd_series_ext.get_series_data(S)
    cql__emm = bodo.hiframes.pd_series_ext.get_series_data(value)
    for kaf__dsmqb in numba.parfors.parfor.internal_prange(len(hbn__jwpo)):
        s = hbn__jwpo[kaf__dsmqb]
        if bodo.libs.array_kernels.isna(hbn__jwpo, kaf__dsmqb
            ) and not bodo.libs.array_kernels.isna(cql__emm, kaf__dsmqb):
            s = cql__emm[kaf__dsmqb]
        hbn__jwpo[kaf__dsmqb] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    hbn__jwpo = bodo.hiframes.pd_series_ext.get_series_data(S)
    for kaf__dsmqb in numba.parfors.parfor.internal_prange(len(hbn__jwpo)):
        s = hbn__jwpo[kaf__dsmqb]
        if bodo.libs.array_kernels.isna(hbn__jwpo, kaf__dsmqb):
            s = value
        hbn__jwpo[kaf__dsmqb] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    hbn__jwpo = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    cql__emm = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(hbn__jwpo)
    zwfsp__ipp = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for ljmj__ezoo in numba.parfors.parfor.internal_prange(n):
        s = hbn__jwpo[ljmj__ezoo]
        if bodo.libs.array_kernels.isna(hbn__jwpo, ljmj__ezoo
            ) and not bodo.libs.array_kernels.isna(cql__emm, ljmj__ezoo):
            s = cql__emm[ljmj__ezoo]
        zwfsp__ipp[ljmj__ezoo] = s
        if bodo.libs.array_kernels.isna(hbn__jwpo, ljmj__ezoo
            ) and bodo.libs.array_kernels.isna(cql__emm, ljmj__ezoo):
            bodo.libs.array_kernels.setna(zwfsp__ipp, ljmj__ezoo)
    return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    hbn__jwpo = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    cql__emm = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(hbn__jwpo)
    zwfsp__ipp = bodo.utils.utils.alloc_type(n, hbn__jwpo.dtype, (-1,))
    for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
        s = hbn__jwpo[kaf__dsmqb]
        if bodo.libs.array_kernels.isna(hbn__jwpo, kaf__dsmqb
            ) and not bodo.libs.array_kernels.isna(cql__emm, kaf__dsmqb):
            s = cql__emm[kaf__dsmqb]
        zwfsp__ipp[kaf__dsmqb] = s
    return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    kgl__bmhk = dict(limit=limit, downcast=downcast)
    bxdi__nnpd = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    edzn__racw = not is_overload_none(value)
    zgc__hdmog = not is_overload_none(method)
    if edzn__racw and zgc__hdmog:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not edzn__racw and not zgc__hdmog:
        raise BodoError(
            "Series.fillna(): Must specify one of 'value' and 'method'.")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.fillna(): axis argument not supported')
    elif is_iterable_type(value) and not isinstance(value, SeriesType):
        raise BodoError('Series.fillna(): "value" parameter cannot be a list')
    elif is_var_size_item_array_type(S.data
        ) and not S.dtype == bodo.string_type:
        raise BodoError(
            f'Series.fillna() with inplace=True not supported for {S.dtype} values yet.'
            )
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "Series.fillna(): 'inplace' argument must be a constant boolean")
    if zgc__hdmog:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        svzit__xhjr = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(svzit__xhjr)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(svzit__xhjr)
    yaym__xss = element_type(S.data)
    zxy__ywjig = None
    if edzn__racw:
        zxy__ywjig = element_type(types.unliteral(value))
    if zxy__ywjig and not can_replace(yaym__xss, zxy__ywjig):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {zxy__ywjig} with series type {yaym__xss}'
            )
    if is_overload_true(inplace):
        if S.dtype == bodo.string_type:
            if is_overload_constant_str(value) and get_overload_const_str(value
                ) == '':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=False)
            return binary_str_fillna_inplace_impl(is_binary=False)
        if S.dtype == bodo.bytes_type:
            if is_overload_constant_bytes(value) and get_overload_const_bytes(
                value) == b'':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=True)
            return binary_str_fillna_inplace_impl(is_binary=True)
        else:
            if isinstance(value, SeriesType):
                return fillna_inplace_series_impl
            return fillna_inplace_impl
    else:
        lff__oyv = S.data
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                hbn__jwpo = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                cql__emm = bodo.hiframes.pd_series_ext.get_series_data(value)
                n = len(hbn__jwpo)
                zwfsp__ipp = bodo.utils.utils.alloc_type(n, lff__oyv, (-1,))
                for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(hbn__jwpo, kaf__dsmqb
                        ) and bodo.libs.array_kernels.isna(cql__emm, kaf__dsmqb
                        ):
                        bodo.libs.array_kernels.setna(zwfsp__ipp, kaf__dsmqb)
                        continue
                    if bodo.libs.array_kernels.isna(hbn__jwpo, kaf__dsmqb):
                        zwfsp__ipp[kaf__dsmqb
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            cql__emm[kaf__dsmqb])
                        continue
                    zwfsp__ipp[kaf__dsmqb
                        ] = bodo.utils.conversion.unbox_if_timestamp(hbn__jwpo
                        [kaf__dsmqb])
                return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                    index, name)
            return fillna_series_impl
        if zgc__hdmog:
            vtvk__xil = (types.unicode_type, types.bool_, bodo.datetime64ns,
                bodo.timedelta64ns)
            if not isinstance(yaym__xss, (types.Integer, types.Float)
                ) and yaym__xss not in vtvk__xil:
                raise BodoError(
                    f"Series.fillna(): series of type {yaym__xss} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                hbn__jwpo = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                zwfsp__ipp = bodo.libs.array_kernels.ffill_bfill_arr(hbn__jwpo,
                    method)
                return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            hbn__jwpo = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(hbn__jwpo)
            zwfsp__ipp = bodo.utils.utils.alloc_type(n, lff__oyv, (-1,))
            for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(hbn__jwpo[
                    kaf__dsmqb])
                if bodo.libs.array_kernels.isna(hbn__jwpo, kaf__dsmqb):
                    s = value
                zwfsp__ipp[kaf__dsmqb] = s
            return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        pdp__rkvio = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        kgl__bmhk = dict(limit=limit, downcast=downcast)
        bxdi__nnpd = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', kgl__bmhk,
            bxdi__nnpd, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        yaym__xss = element_type(S.data)
        vtvk__xil = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(yaym__xss, (types.Integer, types.Float)
            ) and yaym__xss not in vtvk__xil:
            raise BodoError(
                f'Series.{overload_name}(): series of type {yaym__xss} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            hbn__jwpo = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            zwfsp__ipp = bodo.libs.array_kernels.ffill_bfill_arr(hbn__jwpo,
                pdp__rkvio)
            return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        udx__nyh = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(udx__nyh)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        dih__gsro = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(dih__gsro)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        dih__gsro = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(dih__gsro)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        dih__gsro = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(dih__gsro)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    kgl__bmhk = dict(inplace=inplace, limit=limit, regex=regex, method=method)
    gsi__imsvb = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', kgl__bmhk, gsi__imsvb,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    yaym__xss = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        pqszu__qmjm = element_type(to_replace.key_type)
        zxy__ywjig = element_type(to_replace.value_type)
    else:
        pqszu__qmjm = element_type(to_replace)
        zxy__ywjig = element_type(value)
    ztxi__ilyyq = None
    if yaym__xss != types.unliteral(pqszu__qmjm):
        if bodo.utils.typing.equality_always_false(yaym__xss, types.
            unliteral(pqszu__qmjm)
            ) or not bodo.utils.typing.types_equality_exists(yaym__xss,
            pqszu__qmjm):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(yaym__xss, (types.Float, types.Integer)
            ) or yaym__xss == np.bool_:
            ztxi__ilyyq = yaym__xss
    if not can_replace(yaym__xss, types.unliteral(zxy__ywjig)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    opiod__dcjyz = S.data
    if isinstance(opiod__dcjyz, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            hbn__jwpo = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(hbn__jwpo.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        hbn__jwpo = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(hbn__jwpo)
        zwfsp__ipp = bodo.utils.utils.alloc_type(n, opiod__dcjyz, (-1,))
        sdt__pgzjp = build_replace_dict(to_replace, value, ztxi__ilyyq)
        for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(hbn__jwpo, kaf__dsmqb):
                bodo.libs.array_kernels.setna(zwfsp__ipp, kaf__dsmqb)
                continue
            s = hbn__jwpo[kaf__dsmqb]
            if s in sdt__pgzjp:
                s = sdt__pgzjp[s]
            zwfsp__ipp[kaf__dsmqb] = s
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    dagc__kdols = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    elzjz__ynkob = is_iterable_type(to_replace)
    qpixb__dho = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    rdy__lgt = is_iterable_type(value)
    if dagc__kdols and qpixb__dho:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                sdt__pgzjp = {}
                sdt__pgzjp[key_dtype_conv(to_replace)] = value
                return sdt__pgzjp
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            sdt__pgzjp = {}
            sdt__pgzjp[to_replace] = value
            return sdt__pgzjp
        return impl
    if elzjz__ynkob and qpixb__dho:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                sdt__pgzjp = {}
                for inbj__loyqq in to_replace:
                    sdt__pgzjp[key_dtype_conv(inbj__loyqq)] = value
                return sdt__pgzjp
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            sdt__pgzjp = {}
            for inbj__loyqq in to_replace:
                sdt__pgzjp[inbj__loyqq] = value
            return sdt__pgzjp
        return impl
    if elzjz__ynkob and rdy__lgt:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                sdt__pgzjp = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for kaf__dsmqb in range(len(to_replace)):
                    sdt__pgzjp[key_dtype_conv(to_replace[kaf__dsmqb])] = value[
                        kaf__dsmqb]
                return sdt__pgzjp
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            sdt__pgzjp = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for kaf__dsmqb in range(len(to_replace)):
                sdt__pgzjp[to_replace[kaf__dsmqb]] = value[kaf__dsmqb]
            return sdt__pgzjp
        return impl
    if isinstance(to_replace, numba.types.DictType) and is_overload_none(value
        ):
        return lambda to_replace, value, key_dtype_conv: to_replace
    raise BodoError(
        'Series.replace(): Not supported for types to_replace={} and value={}'
        .format(to_replace, value))


@overload_method(SeriesType, 'diff', inline='always', no_unliteral=True)
def overload_series_diff(S, periods=1):
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)):
        raise BodoError(
            f'Series.diff() column input type {S.data} not supported.')
    if not is_overload_int(periods):
        raise BodoError("Series.diff(): 'periods' input must be an integer.")
    if S.data == types.Array(bodo.datetime64ns, 1, 'C'):

        def impl_datetime(S, periods=1):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            zwfsp__ipp = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zwfsp__ipp = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    kgl__bmhk = dict(ignore_index=ignore_index)
    ulork__rdop = dict(ignore_index=False)
    check_unsupported_args('Series.explode', kgl__bmhk, ulork__rdop,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        xrr__spwt = bodo.utils.conversion.index_to_array(index)
        zwfsp__ipp, cmh__hofmg = bodo.libs.array_kernels.explode(arr, xrr__spwt
            )
        qmra__vdwl = bodo.utils.conversion.index_from_array(cmh__hofmg)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
            qmra__vdwl, name)
    return impl


@overload(np.digitize, inline='always', no_unliteral=True)
def overload_series_np_digitize(x, bins, right=False):
    if isinstance(x, SeriesType):

        def impl(x, bins, right=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(x)
            return np.digitize(arr, bins, right)
        return impl


@overload(np.argmax, inline='always', no_unliteral=True)
def argmax_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            pnv__ocgfk = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
                pnv__ocgfk[kaf__dsmqb] = np.argmax(a[kaf__dsmqb])
            return pnv__ocgfk
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            gam__urc = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
                gam__urc[kaf__dsmqb] = np.argmin(a[kaf__dsmqb])
            return gam__urc
        return impl


def overload_series_np_dot(a, b, out=None):
    if (isinstance(a, SeriesType) or isinstance(b, SeriesType)
        ) and not is_overload_none(out):
        raise BodoError("np.dot(): 'out' parameter not supported yet")
    if isinstance(a, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(a)
            return np.dot(arr, b)
        return impl
    if isinstance(b, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(b)
            return np.dot(a, arr)
        return impl


overload(np.dot, inline='always', no_unliteral=True)(overload_series_np_dot)
overload(operator.matmul, inline='always', no_unliteral=True)(
    overload_series_np_dot)


@overload_method(SeriesType, 'dropna', inline='always', no_unliteral=True)
def overload_series_dropna(S, axis=0, inplace=False, how=None):
    kgl__bmhk = dict(axis=axis, inplace=inplace, how=how)
    eocnj__tltmk = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', kgl__bmhk, eocnj__tltmk,
        package_name='pandas', module_name='Series')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            hbn__jwpo = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            ydz__kbh = S.notna().values
            xrr__spwt = bodo.utils.conversion.extract_index_array(S)
            qmra__vdwl = bodo.utils.conversion.convert_to_index(xrr__spwt[
                ydz__kbh])
            zwfsp__ipp = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(hbn__jwpo))
            return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                qmra__vdwl, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            hbn__jwpo = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            xrr__spwt = bodo.utils.conversion.extract_index_array(S)
            ydz__kbh = S.notna().values
            qmra__vdwl = bodo.utils.conversion.convert_to_index(xrr__spwt[
                ydz__kbh])
            zwfsp__ipp = hbn__jwpo[ydz__kbh]
            return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                qmra__vdwl, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    kgl__bmhk = dict(freq=freq, axis=axis, fill_value=fill_value)
    bxdi__nnpd = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not is_supported_shift_array_type(S.data):
        raise BodoError(
            f"Series.shift(): Series input type '{S.data.dtype}' not supported yet."
            )
    if not is_overload_int(periods):
        raise BodoError("Series.shift(): 'periods' input must be an integer.")

    def impl(S, periods=1, freq=None, axis=0, fill_value=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zwfsp__ipp = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    kgl__bmhk = dict(fill_method=fill_method, limit=limit, freq=freq)
    bxdi__nnpd = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not is_overload_int(periods):
        raise BodoError(
            'Series.pct_change(): periods argument must be an Integer')

    def impl(S, periods=1, fill_method='pad', limit=None, freq=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zwfsp__ipp = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)
    return impl


@overload_method(SeriesType, 'where', inline='always', no_unliteral=True)
def overload_series_where(S, cond, other=np.nan, inplace=False, axis=None,
    level=None, errors='raise', try_cast=False):
    _validate_arguments_mask_where('Series.where', S, cond, other, inplace,
        axis, level, errors, try_cast)

    def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None,
        errors='raise', try_cast=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zwfsp__ipp = bodo.hiframes.series_impl.where_impl(cond, arr, other)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)
    return impl


@overload_method(SeriesType, 'mask', inline='always', no_unliteral=True)
def overload_series_mask(S, cond, other=np.nan, inplace=False, axis=None,
    level=None, errors='raise', try_cast=False):
    _validate_arguments_mask_where('Series.mask', S, cond, other, inplace,
        axis, level, errors, try_cast)

    def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None,
        errors='raise', try_cast=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zwfsp__ipp = bodo.hiframes.series_impl.where_impl(~cond, arr, other)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)
    return impl


def _validate_arguments_mask_where(func_name, S, cond, other, inplace, axis,
    level, errors, try_cast):
    kgl__bmhk = dict(inplace=inplace, level=level, errors=errors, try_cast=
        try_cast)
    bxdi__nnpd = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error(f'{func_name}(): axis argument not supported')
    if not (isinstance(S.data, types.Array) or isinstance(S.data,
        BooleanArrayType) or isinstance(S.data, IntegerArrayType) or bodo.
        utils.utils.is_array_typ(S.data, False) and S.dtype in [bodo.
        string_type, bodo.bytes_type] or isinstance(S.data, bodo.
        CategoricalArrayType) and S.dtype.elem_type not in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.pd_timestamp_type, bodo.
        pd_timedelta_type]):
        raise BodoError(
            f'{func_name}() Series data with type {S.data} not yet supported')
    if not (isinstance(cond, (SeriesType, types.Array, BooleanArrayType)) and
        cond.ndim == 1 and cond.dtype == types.bool_):
        raise BodoError(
            f"{func_name}() 'cond' argument must be a Series or 1-dim array of booleans"
            )
    coa__jep = is_overload_constant_nan(other)
    if not (coa__jep or is_scalar_type(other) or isinstance(other, types.
        Array) and other.ndim == 1 or isinstance(other, SeriesType) and (
        isinstance(S.data, types.Array) or S.dtype in [bodo.string_type,
        bodo.bytes_type]) or isinstance(other, StringArrayType) and (S.
        dtype == bodo.string_type or isinstance(S.data, bodo.
        CategoricalArrayType) and S.dtype.elem_type == bodo.string_type) or
        isinstance(other, BinaryArrayType) and (S.dtype == bodo.bytes_type or
        isinstance(S.data, bodo.CategoricalArrayType) and S.dtype.elem_type ==
        bodo.bytes_type) or (not isinstance(other, (StringArrayType,
        BinaryArrayType)) and (isinstance(S.data.dtype, types.Integer) and
        (bodo.utils.utils.is_array_typ(other) and isinstance(other.dtype,
        types.Integer) or is_series_type(other) and isinstance(other.data.
        dtype, types.Integer))) or (bodo.utils.utils.is_array_typ(other) and
        S.data.dtype == other.dtype or is_series_type(other) and S.data.
        dtype == other.data.dtype)) and (isinstance(S.data,
        BooleanArrayType) or isinstance(S.data, IntegerArrayType))):
        raise BodoError(
            f"{func_name}() 'other' must be a scalar, non-categorical series, 1-dim numpy array or StringArray with a matching type for Series."
            )
    if isinstance(S.dtype, bodo.PDCategoricalDtype):
        qxlhw__ywif = S.dtype.elem_type
    else:
        qxlhw__ywif = S.dtype
    if is_iterable_type(other):
        kald__jtqk = other.dtype
    elif coa__jep:
        kald__jtqk = types.float64
    else:
        kald__jtqk = types.unliteral(other)
    if not is_common_scalar_dtype([qxlhw__ywif, kald__jtqk]):
        raise BodoError(
            f"{func_name}() series and 'other' must share a common type.")


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        kgl__bmhk = dict(level=level, axis=axis)
        bxdi__nnpd = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), kgl__bmhk,
            bxdi__nnpd, package_name='pandas', module_name='Series')
        iosne__keihl = other == string_type or is_overload_constant_str(other)
        tql__hdly = is_iterable_type(other) and other.dtype == string_type
        jbzv__ous = S.dtype == string_type and (op == operator.add and (
            iosne__keihl or tql__hdly) or op == operator.mul and isinstance
            (other, types.Integer))
        qlv__xkwdv = S.dtype == bodo.timedelta64ns
        pcpg__zbogl = S.dtype == bodo.datetime64ns
        lyx__nnvdb = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        rizy__pfzwy = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        nic__tovs = qlv__xkwdv and (lyx__nnvdb or rizy__pfzwy
            ) or pcpg__zbogl and lyx__nnvdb
        nic__tovs = nic__tovs and op == operator.add
        if not (isinstance(S.dtype, types.Number) or jbzv__ous or nic__tovs):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        idkq__jxkc = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            opiod__dcjyz = idkq__jxkc.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and opiod__dcjyz == types.Array(types.bool_, 1, 'C'):
                opiod__dcjyz = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                zwfsp__ipp = bodo.utils.utils.alloc_type(n, opiod__dcjyz, (-1,)
                    )
                for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
                    hdifo__vilnh = bodo.libs.array_kernels.isna(arr, kaf__dsmqb
                        )
                    if hdifo__vilnh:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(zwfsp__ipp,
                                kaf__dsmqb)
                        else:
                            zwfsp__ipp[kaf__dsmqb] = op(fill_value, other)
                    else:
                        zwfsp__ipp[kaf__dsmqb] = op(arr[kaf__dsmqb], other)
                return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        opiod__dcjyz = idkq__jxkc.resolve_function_type(op, args, {}
            ).return_type
        if isinstance(S.data, IntegerArrayType
            ) and opiod__dcjyz == types.Array(types.bool_, 1, 'C'):
            opiod__dcjyz = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            ebhrn__kauwx = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            zwfsp__ipp = bodo.utils.utils.alloc_type(n, opiod__dcjyz, (-1,))
            for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
                hdifo__vilnh = bodo.libs.array_kernels.isna(arr, kaf__dsmqb)
                qcdi__kdt = bodo.libs.array_kernels.isna(ebhrn__kauwx,
                    kaf__dsmqb)
                if hdifo__vilnh and qcdi__kdt:
                    bodo.libs.array_kernels.setna(zwfsp__ipp, kaf__dsmqb)
                elif hdifo__vilnh:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(zwfsp__ipp, kaf__dsmqb)
                    else:
                        zwfsp__ipp[kaf__dsmqb] = op(fill_value,
                            ebhrn__kauwx[kaf__dsmqb])
                elif qcdi__kdt:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(zwfsp__ipp, kaf__dsmqb)
                    else:
                        zwfsp__ipp[kaf__dsmqb] = op(arr[kaf__dsmqb], fill_value
                            )
                else:
                    zwfsp__ipp[kaf__dsmqb] = op(arr[kaf__dsmqb],
                        ebhrn__kauwx[kaf__dsmqb])
            return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                index, name)
        return impl
    return overload_series_explicit_binary_op


def create_explicit_binary_reverse_op_overload(op):

    def overload_series_explicit_binary_reverse_op(S, other, level=None,
        fill_value=None, axis=0):
        if not is_overload_none(level):
            raise BodoError('level argument not supported')
        if not is_overload_zero(axis):
            raise BodoError('axis argument not supported')
        if not isinstance(S.dtype, types.Number):
            raise BodoError('only numeric values supported')
        idkq__jxkc = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            opiod__dcjyz = idkq__jxkc.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and opiod__dcjyz == types.Array(types.bool_, 1, 'C'):
                opiod__dcjyz = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                zwfsp__ipp = bodo.utils.utils.alloc_type(n, opiod__dcjyz, None)
                for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
                    hdifo__vilnh = bodo.libs.array_kernels.isna(arr, kaf__dsmqb
                        )
                    if hdifo__vilnh:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(zwfsp__ipp,
                                kaf__dsmqb)
                        else:
                            zwfsp__ipp[kaf__dsmqb] = op(other, fill_value)
                    else:
                        zwfsp__ipp[kaf__dsmqb] = op(other, arr[kaf__dsmqb])
                return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        opiod__dcjyz = idkq__jxkc.resolve_function_type(op, args, {}
            ).return_type
        if isinstance(S.data, IntegerArrayType
            ) and opiod__dcjyz == types.Array(types.bool_, 1, 'C'):
            opiod__dcjyz = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            ebhrn__kauwx = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            zwfsp__ipp = bodo.utils.utils.alloc_type(n, opiod__dcjyz, None)
            for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
                hdifo__vilnh = bodo.libs.array_kernels.isna(arr, kaf__dsmqb)
                qcdi__kdt = bodo.libs.array_kernels.isna(ebhrn__kauwx,
                    kaf__dsmqb)
                zwfsp__ipp[kaf__dsmqb] = op(ebhrn__kauwx[kaf__dsmqb], arr[
                    kaf__dsmqb])
                if hdifo__vilnh and qcdi__kdt:
                    bodo.libs.array_kernels.setna(zwfsp__ipp, kaf__dsmqb)
                elif hdifo__vilnh:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(zwfsp__ipp, kaf__dsmqb)
                    else:
                        zwfsp__ipp[kaf__dsmqb] = op(ebhrn__kauwx[kaf__dsmqb
                            ], fill_value)
                elif qcdi__kdt:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(zwfsp__ipp, kaf__dsmqb)
                    else:
                        zwfsp__ipp[kaf__dsmqb] = op(fill_value, arr[kaf__dsmqb]
                            )
                else:
                    zwfsp__ipp[kaf__dsmqb] = op(ebhrn__kauwx[kaf__dsmqb],
                        arr[kaf__dsmqb])
            return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                index, name)
        return impl
    return overload_series_explicit_binary_reverse_op


explicit_binop_funcs_two_ways = {operator.add: {'add'}, operator.sub: {
    'sub'}, operator.mul: {'mul'}, operator.truediv: {'div', 'truediv'},
    operator.floordiv: {'floordiv'}, operator.mod: {'mod'}, operator.pow: {
    'pow'}}
explicit_binop_funcs_single = {operator.lt: 'lt', operator.gt: 'gt',
    operator.le: 'le', operator.ge: 'ge', operator.ne: 'ne', operator.eq: 'eq'}
explicit_binop_funcs = set()
split_logical_binops_funcs = [operator.or_, operator.and_]


def _install_explicit_binary_ops():
    for op, veae__ftdoe in explicit_binop_funcs_two_ways.items():
        for name in veae__ftdoe:
            udx__nyh = create_explicit_binary_op_overload(op)
            ezn__tes = create_explicit_binary_reverse_op_overload(op)
            htp__ahpc = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(udx__nyh)
            overload_method(SeriesType, htp__ahpc, no_unliteral=True)(ezn__tes)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        udx__nyh = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(udx__nyh)
        explicit_binop_funcs.add(name)


_install_explicit_binary_ops()


def create_binary_op_overload(op):

    def overload_series_binary_op(lhs, rhs):
        if (isinstance(lhs, SeriesType) and isinstance(rhs, SeriesType) and
            lhs.dtype == bodo.datetime64ns and rhs.dtype == bodo.
            datetime64ns and op == operator.sub):

            def impl_dt64(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ylqu__ohc = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                zwfsp__ipp = dt64_arr_sub(arr, ylqu__ohc)
                return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                    index, name)
            return impl_dt64
        if op in [operator.add, operator.sub] and isinstance(lhs, SeriesType
            ) and lhs.dtype == bodo.datetime64ns and is_offsets_type(rhs):

            def impl_offsets(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                zwfsp__ipp = np.empty(n, np.dtype('datetime64[ns]'))
                for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, kaf__dsmqb):
                        bodo.libs.array_kernels.setna(zwfsp__ipp, kaf__dsmqb)
                        continue
                    dmys__tatnn = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[kaf__dsmqb]))
                    zswwy__ntavx = op(dmys__tatnn, rhs)
                    zwfsp__ipp[kaf__dsmqb
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        zswwy__ntavx.value)
                return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                    index, name)
            return impl_offsets
        if op == operator.add and is_offsets_type(lhs) and isinstance(rhs,
            SeriesType) and rhs.dtype == bodo.datetime64ns:

            def impl(lhs, rhs):
                return op(rhs, lhs)
            return impl
        if isinstance(lhs, SeriesType):
            if lhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                    ylqu__ohc = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    zwfsp__ipp = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(ylqu__ohc))
                    return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ylqu__ohc = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                zwfsp__ipp = op(arr, ylqu__ohc)
                return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    zjg__drwl = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    zwfsp__ipp = op(bodo.utils.conversion.
                        unbox_if_timestamp(zjg__drwl), arr)
                    return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                zjg__drwl = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                zwfsp__ipp = op(zjg__drwl, arr)
                return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        udx__nyh = create_binary_op_overload(op)
        overload(op)(udx__nyh)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    furqj__dieu = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, furqj__dieu)
        for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, kaf__dsmqb
                ) or bodo.libs.array_kernels.isna(arg2, kaf__dsmqb):
                bodo.libs.array_kernels.setna(S, kaf__dsmqb)
                continue
            S[kaf__dsmqb
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                kaf__dsmqb]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[kaf__dsmqb]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                ebhrn__kauwx = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, ebhrn__kauwx)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        udx__nyh = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(udx__nyh)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                zwfsp__ipp = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        udx__nyh = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(udx__nyh)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    zwfsp__ipp = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                        index, name)
                return impl
        return overload_series_ufunc_nin_1
    elif ufunc.nin == 2:

        def overload_series_ufunc_nin_2(S1, S2):
            if isinstance(S1, SeriesType):

                def impl(S1, S2):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S1)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S1)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S1)
                    ebhrn__kauwx = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    zwfsp__ipp = ufunc(arr, ebhrn__kauwx)
                    return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    ebhrn__kauwx = bodo.hiframes.pd_series_ext.get_series_data(
                        S2)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    zwfsp__ipp = ufunc(arr, ebhrn__kauwx)
                    return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        udx__nyh = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(udx__nyh)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        hqwq__nmtu = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),)
            )
        iisa__vibim = np.arange(n),
        bodo.libs.timsort.sort(hqwq__nmtu, 0, n, iisa__vibim)
        return iisa__vibim[0]
    return impl


@overload(pd.to_numeric, inline='always', no_unliteral=True)
def overload_to_numeric(arg_a, errors='raise', downcast=None):
    if not is_overload_none(downcast) and not (is_overload_constant_str(
        downcast) and get_overload_const_str(downcast) in ('integer',
        'signed', 'unsigned', 'float')):
        raise BodoError(
            'pd.to_numeric(): invalid downcasting method provided {}'.
            format(downcast))
    out_dtype = types.float64
    if not is_overload_none(downcast):
        jbj__lma = get_overload_const_str(downcast)
        if jbj__lma in ('integer', 'signed'):
            out_dtype = types.int64
        elif jbj__lma == 'unsigned':
            out_dtype = types.uint64
        else:
            assert jbj__lma == 'float'
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            hbn__jwpo = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            zwfsp__ipp = pd.to_numeric(hbn__jwpo, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                index, name)
        return impl_series
    if arg_a != string_array_type:
        raise BodoError('pd.to_numeric(): invalid argument type {}'.format(
            arg_a))
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            ssjh__tsmy = np.empty(n, np.float64)
            for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, kaf__dsmqb):
                    bodo.libs.array_kernels.setna(ssjh__tsmy, kaf__dsmqb)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(ssjh__tsmy,
                        kaf__dsmqb, arg_a, kaf__dsmqb)
            return ssjh__tsmy
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            ssjh__tsmy = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, kaf__dsmqb):
                    bodo.libs.array_kernels.setna(ssjh__tsmy, kaf__dsmqb)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(ssjh__tsmy,
                        kaf__dsmqb, arg_a, kaf__dsmqb)
            return ssjh__tsmy
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        oyzau__cpll = if_series_to_array_type(args[0])
        if isinstance(oyzau__cpll, types.Array) and isinstance(oyzau__cpll.
            dtype, types.Integer):
            oyzau__cpll = types.Array(types.float64, 1, 'C')
        return oyzau__cpll(*args)


def where_impl_one_arg(c):
    return np.where(c)


@overload(where_impl_one_arg, no_unliteral=True)
def overload_where_unsupported_one_arg(condition):
    if isinstance(condition, SeriesType) or bodo.utils.utils.is_array_typ(
        condition, False):
        return lambda condition: np.where(condition)


def overload_np_where_one_arg(condition):
    if isinstance(condition, SeriesType):

        def impl_series(condition):
            condition = bodo.hiframes.pd_series_ext.get_series_data(condition)
            return bodo.libs.array_kernels.nonzero(condition)
        return impl_series
    elif bodo.utils.utils.is_array_typ(condition, False):

        def impl(condition):
            return bodo.libs.array_kernels.nonzero(condition)
        return impl


overload(np.where, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)
overload(where_impl_one_arg, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)


def where_impl(c, x, y):
    return np.where(c, x, y)


@overload(where_impl, no_unliteral=True)
def overload_where_unsupported(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return lambda condition, x, y: np.where(condition, x, y)


@overload(where_impl, no_unliteral=True)
@overload(np.where, no_unliteral=True)
def overload_np_where(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return
    assert condition.dtype == types.bool_, 'invalid condition dtype'
    qsgpd__wrud = bodo.utils.utils.is_array_typ(x, True)
    brwon__mugu = bodo.utils.utils.is_array_typ(y, True)
    lrq__tqrvf = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        lrq__tqrvf += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if qsgpd__wrud and not bodo.utils.utils.is_array_typ(x, False):
        lrq__tqrvf += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if brwon__mugu and not bodo.utils.utils.is_array_typ(y, False):
        lrq__tqrvf += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    lrq__tqrvf += '  n = len(condition)\n'
    ywpp__sllbl = x.dtype if qsgpd__wrud else types.unliteral(x)
    ewckz__rswi = y.dtype if brwon__mugu else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        ywpp__sllbl = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        ewckz__rswi = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    neu__gaycf = get_data(x)
    gow__hrmlo = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(iisa__vibim) for
        iisa__vibim in [neu__gaycf, gow__hrmlo])
    if neu__gaycf == gow__hrmlo and not is_nullable:
        out_dtype = dtype_to_array_type(ywpp__sllbl)
    elif ywpp__sllbl == string_type or ewckz__rswi == string_type:
        out_dtype = bodo.string_array_type
    elif neu__gaycf == bytes_type or (qsgpd__wrud and ywpp__sllbl == bytes_type
        ) and (gow__hrmlo == bytes_type or brwon__mugu and ewckz__rswi ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(ywpp__sllbl, bodo.PDCategoricalDtype):
        out_dtype = None
    elif ywpp__sllbl in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(ywpp__sllbl, 1, 'C')
    elif ewckz__rswi in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(ewckz__rswi, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(ywpp__sllbl), numba.np.numpy_support.
            as_dtype(ewckz__rswi)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(ywpp__sllbl, bodo.PDCategoricalDtype):
        vbdyw__phth = 'x'
    else:
        vbdyw__phth = 'out_dtype'
    lrq__tqrvf += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {vbdyw__phth}, (-1,))\n')
    if isinstance(ywpp__sllbl, bodo.PDCategoricalDtype):
        lrq__tqrvf += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        lrq__tqrvf += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    lrq__tqrvf += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    lrq__tqrvf += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if qsgpd__wrud:
        lrq__tqrvf += '      if bodo.libs.array_kernels.isna(x, j):\n'
        lrq__tqrvf += '        setna(out_arr, j)\n'
        lrq__tqrvf += '        continue\n'
    if isinstance(ywpp__sllbl, bodo.PDCategoricalDtype):
        lrq__tqrvf += '      out_codes[j] = x_codes[j]\n'
    else:
        lrq__tqrvf += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if qsgpd__wrud else 'x'))
    lrq__tqrvf += '    else:\n'
    if brwon__mugu:
        lrq__tqrvf += '      if bodo.libs.array_kernels.isna(y, j):\n'
        lrq__tqrvf += '        setna(out_arr, j)\n'
        lrq__tqrvf += '        continue\n'
    lrq__tqrvf += (
        '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
        .format('y[j]' if brwon__mugu else 'y'))
    lrq__tqrvf += '  return out_arr\n'
    qvx__ahvui = {}
    exec(lrq__tqrvf, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, qvx__ahvui)
    ztx__yfw = qvx__ahvui['_impl']
    return ztx__yfw


def _verify_np_select_arg_typs(condlist, choicelist, default):
    if isinstance(condlist, (types.List, types.UniTuple)):
        if not (bodo.utils.utils.is_np_array_typ(condlist.dtype) and 
            condlist.dtype.dtype == types.bool_):
            raise BodoError(
                "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
                )
    else:
        raise BodoError(
            "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
            )
    if not isinstance(choicelist, (types.List, types.UniTuple, types.BaseTuple)
        ):
        raise BodoError(
            "np.select(): 'choicelist' argument must be list or tuple type")
    if isinstance(choicelist, (types.List, types.UniTuple)):
        ctg__harh = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(ctg__harh, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(ctg__harh):
            esbw__mdrb = ctg__harh.data.dtype
        else:
            esbw__mdrb = ctg__harh.dtype
        if isinstance(esbw__mdrb, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        its__hzo = ctg__harh
    else:
        mej__aalui = []
        for ctg__harh in choicelist:
            if not bodo.utils.utils.is_array_typ(ctg__harh, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(ctg__harh):
                esbw__mdrb = ctg__harh.data.dtype
            else:
                esbw__mdrb = ctg__harh.dtype
            if isinstance(esbw__mdrb, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            mej__aalui.append(esbw__mdrb)
        if not is_common_scalar_dtype(mej__aalui):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        its__hzo = choicelist[0]
    if is_series_type(its__hzo):
        its__hzo = its__hzo.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, its__hzo.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(its__hzo, types.Array) or isinstance(its__hzo,
        BooleanArrayType) or isinstance(its__hzo, IntegerArrayType) or bodo
        .utils.utils.is_array_typ(its__hzo, False) and its__hzo.dtype in [
        bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {its__hzo} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    nsk__ppaz = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        julep__zrm = choicelist.dtype
    else:
        gyno__sjzkq = False
        mej__aalui = []
        for ctg__harh in choicelist:
            if is_nullable_type(ctg__harh):
                gyno__sjzkq = True
            if is_series_type(ctg__harh):
                esbw__mdrb = ctg__harh.data.dtype
            else:
                esbw__mdrb = ctg__harh.dtype
            if isinstance(esbw__mdrb, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            mej__aalui.append(esbw__mdrb)
        vrhzo__aosnc, cru__fsxe = get_common_scalar_dtype(mej__aalui)
        if not cru__fsxe:
            raise BodoError('Internal error in overload_np_select')
        udouu__grxet = dtype_to_array_type(vrhzo__aosnc)
        if gyno__sjzkq:
            udouu__grxet = to_nullable_type(udouu__grxet)
        julep__zrm = udouu__grxet
    if isinstance(julep__zrm, SeriesType):
        julep__zrm = julep__zrm.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        rmbau__hze = True
    else:
        rmbau__hze = False
    ltb__ppom = False
    acoo__owhv = False
    if rmbau__hze:
        if isinstance(julep__zrm.dtype, types.Number):
            pass
        elif julep__zrm.dtype == types.bool_:
            acoo__owhv = True
        else:
            ltb__ppom = True
            julep__zrm = to_nullable_type(julep__zrm)
    elif default == types.none or is_overload_constant_nan(default):
        ltb__ppom = True
        julep__zrm = to_nullable_type(julep__zrm)
    lrq__tqrvf = 'def np_select_impl(condlist, choicelist, default=0):\n'
    lrq__tqrvf += '  if len(condlist) != len(choicelist):\n'
    lrq__tqrvf += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    lrq__tqrvf += '  output_len = len(choicelist[0])\n'
    lrq__tqrvf += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    lrq__tqrvf += '  for i in range(output_len):\n'
    if ltb__ppom:
        lrq__tqrvf += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif acoo__owhv:
        lrq__tqrvf += '    out[i] = False\n'
    else:
        lrq__tqrvf += '    out[i] = default\n'
    if nsk__ppaz:
        lrq__tqrvf += '  for i in range(len(condlist) - 1, -1, -1):\n'
        lrq__tqrvf += '    cond = condlist[i]\n'
        lrq__tqrvf += '    choice = choicelist[i]\n'
        lrq__tqrvf += '    out = np.where(cond, choice, out)\n'
    else:
        for kaf__dsmqb in range(len(choicelist) - 1, -1, -1):
            lrq__tqrvf += f'  cond = condlist[{kaf__dsmqb}]\n'
            lrq__tqrvf += f'  choice = choicelist[{kaf__dsmqb}]\n'
            lrq__tqrvf += f'  out = np.where(cond, choice, out)\n'
    lrq__tqrvf += '  return out'
    qvx__ahvui = dict()
    exec(lrq__tqrvf, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': julep__zrm}, qvx__ahvui)
    impl = qvx__ahvui['np_select_impl']
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    kgl__bmhk = dict(subset=subset, keep=keep, inplace=inplace)
    bxdi__nnpd = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        cfo__gsz = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (cfo__gsz,), xrr__spwt = bodo.libs.array_kernels.drop_duplicates((
            cfo__gsz,), index, 1)
        index = bodo.utils.conversion.index_from_array(xrr__spwt)
        return bodo.hiframes.pd_series_ext.init_series(cfo__gsz, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    wxd__bul = element_type(S.data)
    if not is_common_scalar_dtype([wxd__bul, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([wxd__bul, right]):
        raise_bodo_error(
            "Series.between(): 'right' must be compariable with the Series data"
            )
    if not is_overload_constant_str(inclusive) or get_overload_const_str(
        inclusive) not in ('both', 'neither'):
        raise_bodo_error(
            "Series.between(): 'inclusive' must be a constant string and one of ('both', 'neither')"
            )

    def impl(S, left, right, inclusive='both'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        zwfsp__ipp = np.empty(n, np.bool_)
        for kaf__dsmqb in numba.parfors.parfor.internal_prange(n):
            kmbey__twl = bodo.utils.conversion.box_if_dt64(arr[kaf__dsmqb])
            if inclusive == 'both':
                zwfsp__ipp[kaf__dsmqb
                    ] = kmbey__twl <= right and kmbey__twl >= left
            else:
                zwfsp__ipp[kaf__dsmqb
                    ] = kmbey__twl < right and kmbey__twl > left
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    kgl__bmhk = dict(axis=axis)
    bxdi__nnpd = dict(axis=None)
    check_unsupported_args('Series.repeat', kgl__bmhk, bxdi__nnpd,
        package_name='pandas', module_name='Series')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Series.repeat(): 'repeats' should be an integer or array of integers"
            )
    if isinstance(repeats, types.Integer):

        def impl_int(S, repeats, axis=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            xrr__spwt = bodo.utils.conversion.index_to_array(index)
            zwfsp__ipp = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            cmh__hofmg = bodo.libs.array_kernels.repeat_kernel(xrr__spwt,
                repeats)
            qmra__vdwl = bodo.utils.conversion.index_from_array(cmh__hofmg)
            return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
                qmra__vdwl, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        xrr__spwt = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        zwfsp__ipp = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        cmh__hofmg = bodo.libs.array_kernels.repeat_kernel(xrr__spwt, repeats)
        qmra__vdwl = bodo.utils.conversion.index_from_array(cmh__hofmg)
        return bodo.hiframes.pd_series_ext.init_series(zwfsp__ipp,
            qmra__vdwl, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        iisa__vibim = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(iisa__vibim)
        sobx__byb = {}
        for kaf__dsmqb in range(n):
            kmbey__twl = bodo.utils.conversion.box_if_dt64(iisa__vibim[
                kaf__dsmqb])
            sobx__byb[index[kaf__dsmqb]] = kmbey__twl
        return sobx__byb
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    svzit__xhjr = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            wisd__dwbza = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(svzit__xhjr)
    elif is_literal_type(name):
        wisd__dwbza = get_literal_value(name)
    else:
        raise_bodo_error(svzit__xhjr)
    wisd__dwbza = 0 if wisd__dwbza is None else wisd__dwbza

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            (wisd__dwbza,))
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
