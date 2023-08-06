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
            zlh__fxfvi = list()
            for yru__nfcr in range(len(S)):
                zlh__fxfvi.append(S.iat[yru__nfcr])
            return zlh__fxfvi
        return impl_float

    def impl(S):
        zlh__fxfvi = list()
        for yru__nfcr in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, yru__nfcr):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            zlh__fxfvi.append(S.iat[yru__nfcr])
        return zlh__fxfvi
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    drgbz__nadg = dict(dtype=dtype, copy=copy, na_value=na_value)
    geliw__dshoj = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    drgbz__nadg = dict(name=name, inplace=inplace)
    geliw__dshoj = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', drgbz__nadg, geliw__dshoj,
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
    gypg__lgbh = get_name_literal(S.index.name_typ, True, series_name)
    bnmu__zwgx = [gypg__lgbh, series_name]
    ecq__qbsyg = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    ecq__qbsyg += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    ecq__qbsyg += """    index = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S))
"""
    ecq__qbsyg += """    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)
"""
    ecq__qbsyg += '    col_var = {}\n'.format(gen_const_tup(bnmu__zwgx))
    ecq__qbsyg += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe((index, arr), df_index, col_var)
"""
    ewh__wkoo = {}
    exec(ecq__qbsyg, {'bodo': bodo}, ewh__wkoo)
    lnvyc__vkwj = ewh__wkoo['_impl']
    return lnvyc__vkwj


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wghx__qwrvz = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name
            )
    return impl


@overload_method(SeriesType, 'round', inline='always', no_unliteral=True)
def overload_series_round(S, decimals=0):

    def impl(S, decimals=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        wghx__qwrvz = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for yru__nfcr in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[yru__nfcr]):
                bodo.libs.array_kernels.setna(wghx__qwrvz, yru__nfcr)
            else:
                wghx__qwrvz[yru__nfcr] = np.round(arr[yru__nfcr], decimals)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name
            )
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    drgbz__nadg = dict(level=level, numeric_only=numeric_only)
    geliw__dshoj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', drgbz__nadg, geliw__dshoj,
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
    drgbz__nadg = dict(level=level, numeric_only=numeric_only)
    geliw__dshoj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', drgbz__nadg, geliw__dshoj,
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
    drgbz__nadg = dict(axis=axis, bool_only=bool_only, skipna=skipna, level
        =level)
    geliw__dshoj = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        kdp__fedwm = 0
        for yru__nfcr in numba.parfors.parfor.internal_prange(len(A)):
            ccgj__vqnl = 0
            if not bodo.libs.array_kernels.isna(A, yru__nfcr):
                ccgj__vqnl = int(A[yru__nfcr])
            kdp__fedwm += ccgj__vqnl
        return kdp__fedwm != 0
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
        lbzz__wbdyh = bodo.hiframes.pd_series_ext.get_series_data(S)
        bmoq__col = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        kdp__fedwm = 0
        for yru__nfcr in numba.parfors.parfor.internal_prange(len(lbzz__wbdyh)
            ):
            ccgj__vqnl = 0
            cpn__jhp = bodo.libs.array_kernels.isna(lbzz__wbdyh, yru__nfcr)
            kso__qkkxv = bodo.libs.array_kernels.isna(bmoq__col, yru__nfcr)
            if cpn__jhp and not kso__qkkxv or not cpn__jhp and kso__qkkxv:
                ccgj__vqnl = 1
            elif not cpn__jhp:
                if lbzz__wbdyh[yru__nfcr] != bmoq__col[yru__nfcr]:
                    ccgj__vqnl = 1
            kdp__fedwm += ccgj__vqnl
        return kdp__fedwm == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    drgbz__nadg = dict(axis=axis, bool_only=bool_only, skipna=skipna, level
        =level)
    geliw__dshoj = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        kdp__fedwm = 0
        for yru__nfcr in numba.parfors.parfor.internal_prange(len(A)):
            ccgj__vqnl = 0
            if not bodo.libs.array_kernels.isna(A, yru__nfcr):
                ccgj__vqnl = int(not A[yru__nfcr])
            kdp__fedwm += ccgj__vqnl
        return kdp__fedwm == 0
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    drgbz__nadg = dict(level=level)
    geliw__dshoj = dict(level=None)
    check_unsupported_args('Series.mad', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    bkfya__trmd = types.float64
    rayvp__tyykp = types.float64
    if S.dtype == types.float32:
        bkfya__trmd = types.float32
        rayvp__tyykp = types.float32
    gfxm__eaacq = bkfya__trmd(0)
    khale__xrzci = rayvp__tyykp(0)
    mgb__ztbb = rayvp__tyykp(1)

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        pkuyy__kktzw = gfxm__eaacq
        kdp__fedwm = khale__xrzci
        for yru__nfcr in numba.parfors.parfor.internal_prange(len(A)):
            ccgj__vqnl = gfxm__eaacq
            qzf__uyw = khale__xrzci
            if not bodo.libs.array_kernels.isna(A, yru__nfcr) or not skipna:
                ccgj__vqnl = A[yru__nfcr]
                qzf__uyw = mgb__ztbb
            pkuyy__kktzw += ccgj__vqnl
            kdp__fedwm += qzf__uyw
        kru__cwa = bodo.hiframes.series_kernels._mean_handle_nan(pkuyy__kktzw,
            kdp__fedwm)
        yuj__oifl = gfxm__eaacq
        for yru__nfcr in numba.parfors.parfor.internal_prange(len(A)):
            ccgj__vqnl = gfxm__eaacq
            if not bodo.libs.array_kernels.isna(A, yru__nfcr) or not skipna:
                ccgj__vqnl = abs(A[yru__nfcr] - kru__cwa)
            yuj__oifl += ccgj__vqnl
        bkwu__reldf = bodo.hiframes.series_kernels._mean_handle_nan(yuj__oifl,
            kdp__fedwm)
        return bkwu__reldf
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    drgbz__nadg = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    geliw__dshoj = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', drgbz__nadg, geliw__dshoj,
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
    drgbz__nadg = dict(level=level, numeric_only=numeric_only)
    geliw__dshoj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', drgbz__nadg, geliw__dshoj,
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
        rhl__nfmh = 0
        sie__ycl = 0
        kdp__fedwm = 0
        for yru__nfcr in numba.parfors.parfor.internal_prange(len(A)):
            ccgj__vqnl = 0
            qzf__uyw = 0
            if not bodo.libs.array_kernels.isna(A, yru__nfcr) or not skipna:
                ccgj__vqnl = A[yru__nfcr]
                qzf__uyw = 1
            rhl__nfmh += ccgj__vqnl
            sie__ycl += ccgj__vqnl * ccgj__vqnl
            kdp__fedwm += qzf__uyw
        s = sie__ycl - rhl__nfmh * rhl__nfmh / kdp__fedwm
        ydx__yvueq = bodo.hiframes.series_kernels._handle_nan_count_ddof(s,
            kdp__fedwm, ddof)
        rttjk__slrah = (ydx__yvueq / kdp__fedwm) ** 0.5
        return rttjk__slrah
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    drgbz__nadg = dict(level=level, numeric_only=numeric_only)
    geliw__dshoj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.kurtosis(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError(
            "Series.kurtosis(): 'skipna' argument must be a boolean")

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        rhl__nfmh = 0.0
        sie__ycl = 0.0
        ynq__dahvf = 0.0
        lyorw__wwyuh = 0.0
        kdp__fedwm = 0
        for yru__nfcr in numba.parfors.parfor.internal_prange(len(A)):
            ccgj__vqnl = 0.0
            qzf__uyw = 0
            if not bodo.libs.array_kernels.isna(A, yru__nfcr) or not skipna:
                ccgj__vqnl = np.float64(A[yru__nfcr])
                qzf__uyw = 1
            rhl__nfmh += ccgj__vqnl
            sie__ycl += ccgj__vqnl ** 2
            ynq__dahvf += ccgj__vqnl ** 3
            lyorw__wwyuh += ccgj__vqnl ** 4
            kdp__fedwm += qzf__uyw
        ydx__yvueq = bodo.hiframes.series_kernels.compute_kurt(rhl__nfmh,
            sie__ycl, ynq__dahvf, lyorw__wwyuh, kdp__fedwm)
        return ydx__yvueq
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    drgbz__nadg = dict(level=level, numeric_only=numeric_only)
    geliw__dshoj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.skew(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.skew(): skipna argument must be a boolean')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        rhl__nfmh = 0.0
        sie__ycl = 0.0
        ynq__dahvf = 0.0
        kdp__fedwm = 0
        for yru__nfcr in numba.parfors.parfor.internal_prange(len(A)):
            ccgj__vqnl = 0.0
            qzf__uyw = 0
            if not bodo.libs.array_kernels.isna(A, yru__nfcr) or not skipna:
                ccgj__vqnl = np.float64(A[yru__nfcr])
                qzf__uyw = 1
            rhl__nfmh += ccgj__vqnl
            sie__ycl += ccgj__vqnl ** 2
            ynq__dahvf += ccgj__vqnl ** 3
            kdp__fedwm += qzf__uyw
        ydx__yvueq = bodo.hiframes.series_kernels.compute_skew(rhl__nfmh,
            sie__ycl, ynq__dahvf, kdp__fedwm)
        return ydx__yvueq
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    drgbz__nadg = dict(level=level, numeric_only=numeric_only)
    geliw__dshoj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', drgbz__nadg, geliw__dshoj,
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
    drgbz__nadg = dict(level=level, numeric_only=numeric_only)
    geliw__dshoj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', drgbz__nadg, geliw__dshoj,
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
        lbzz__wbdyh = bodo.hiframes.pd_series_ext.get_series_data(S)
        bmoq__col = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        kwozf__qxgs = 0
        for yru__nfcr in numba.parfors.parfor.internal_prange(len(lbzz__wbdyh)
            ):
            kmaf__zud = lbzz__wbdyh[yru__nfcr]
            abv__tajy = bmoq__col[yru__nfcr]
            kwozf__qxgs += kmaf__zud * abv__tajy
        return kwozf__qxgs
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    drgbz__nadg = dict(skipna=skipna)
    geliw__dshoj = dict(skipna=True)
    check_unsupported_args('Series.cumsum', drgbz__nadg, geliw__dshoj,
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
    drgbz__nadg = dict(skipna=skipna)
    geliw__dshoj = dict(skipna=True)
    check_unsupported_args('Series.cumprod', drgbz__nadg, geliw__dshoj,
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
    drgbz__nadg = dict(skipna=skipna)
    geliw__dshoj = dict(skipna=True)
    check_unsupported_args('Series.cummin', drgbz__nadg, geliw__dshoj,
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
    drgbz__nadg = dict(skipna=skipna)
    geliw__dshoj = dict(skipna=True)
    check_unsupported_args('Series.cummax', drgbz__nadg, geliw__dshoj,
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
    drgbz__nadg = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    geliw__dshoj = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        pbo__klqqc = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, pbo__klqqc, index)
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
    drgbz__nadg = dict(level=level)
    geliw__dshoj = dict(level=None)
    check_unsupported_args('Series.count', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    drgbz__nadg = dict(method=method, min_periods=min_periods)
    geliw__dshoj = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        tswun__xvu = S.sum()
        lniw__kukft = other.sum()
        a = n * (S * other).sum() - tswun__xvu * lniw__kukft
        spm__dksc = n * (S ** 2).sum() - tswun__xvu ** 2
        svdyo__qbjs = n * (other ** 2).sum() - lniw__kukft ** 2
        return a / np.sqrt(spm__dksc * svdyo__qbjs)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    drgbz__nadg = dict(min_periods=min_periods)
    geliw__dshoj = dict(min_periods=None)
    check_unsupported_args('Series.cov', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')

    def impl(S, other, min_periods=None, ddof=1):
        tswun__xvu = S.mean()
        lniw__kukft = other.mean()
        nqru__ufwcd = ((S - tswun__xvu) * (other - lniw__kukft)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(nqru__ufwcd, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            den__htt = np.sign(sum_val)
            return np.inf * den__htt
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    drgbz__nadg = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    geliw__dshoj = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', drgbz__nadg, geliw__dshoj,
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
    drgbz__nadg = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    geliw__dshoj = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', drgbz__nadg, geliw__dshoj,
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
    drgbz__nadg = dict(axis=axis, skipna=skipna)
    geliw__dshoj = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', drgbz__nadg, geliw__dshoj,
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
    drgbz__nadg = dict(axis=axis, skipna=skipna)
    geliw__dshoj = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', drgbz__nadg, geliw__dshoj,
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
    drgbz__nadg = dict(level=level, numeric_only=numeric_only)
    geliw__dshoj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', drgbz__nadg, geliw__dshoj,
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
        rkzba__gji = arr[:n]
        smivx__acib = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(rkzba__gji,
            smivx__acib, name)
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
        pff__yeq = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        rkzba__gji = arr[pff__yeq:]
        smivx__acib = index[pff__yeq:]
        return bodo.hiframes.pd_series_ext.init_series(rkzba__gji,
            smivx__acib, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    yvd__lfre = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in yvd__lfre:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            awbv__hzgg = index[0]
            ndgif__emq = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                awbv__hzgg, False))
        else:
            ndgif__emq = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        rkzba__gji = arr[:ndgif__emq]
        smivx__acib = index[:ndgif__emq]
        return bodo.hiframes.pd_series_ext.init_series(rkzba__gji,
            smivx__acib, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    yvd__lfre = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in yvd__lfre:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            xmmw__ytf = index[-1]
            ndgif__emq = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset, xmmw__ytf,
                True))
        else:
            ndgif__emq = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        rkzba__gji = arr[len(arr) - ndgif__emq:]
        smivx__acib = index[len(arr) - ndgif__emq:]
        return bodo.hiframes.pd_series_ext.init_series(rkzba__gji,
            smivx__acib, name)
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    drgbz__nadg = dict(keep=keep)
    geliw__dshoj = dict(keep='first')
    check_unsupported_args('Series.nlargest', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        seus__expxi = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wghx__qwrvz, zmg__mywnj = bodo.libs.array_kernels.nlargest(arr,
            seus__expxi, n, True, bodo.hiframes.series_kernels.gt_f)
        doedn__dpqec = bodo.utils.conversion.convert_to_index(zmg__mywnj)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
            doedn__dpqec, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    drgbz__nadg = dict(keep=keep)
    geliw__dshoj = dict(keep='first')
    check_unsupported_args('Series.nsmallest', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        seus__expxi = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wghx__qwrvz, zmg__mywnj = bodo.libs.array_kernels.nlargest(arr,
            seus__expxi, n, False, bodo.hiframes.series_kernels.lt_f)
        doedn__dpqec = bodo.utils.conversion.convert_to_index(zmg__mywnj)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
            doedn__dpqec, name)
    return impl


@overload_method(SeriesType, 'notnull', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'notna', inline='always', no_unliteral=True)
def overload_series_notna(S):
    return lambda S: S.isna() == False


@overload_method(SeriesType, 'astype', inline='always', no_unliteral=True)
def overload_series_astype(S, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True):
    drgbz__nadg = dict(errors=errors)
    geliw__dshoj = dict(errors='raise')
    check_unsupported_args('Series.astype', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "Series.astype(): 'dtype' when passed as string must be a constant value"
            )

    def impl(S, dtype, copy=True, errors='raise', _bodo_nan_to_str=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wghx__qwrvz = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name
            )
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    drgbz__nadg = dict(axis=axis, is_copy=is_copy)
    geliw__dshoj = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        jog__tisi = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[jog__tisi],
            index[jog__tisi], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    drgbz__nadg = dict(axis=axis, kind=kind, order=order)
    geliw__dshoj = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        gnweb__tsd = S.notna().values
        if not gnweb__tsd.all():
            wghx__qwrvz = np.full(n, -1, np.int64)
            wghx__qwrvz[gnweb__tsd] = argsort(arr[gnweb__tsd])
        else:
            wghx__qwrvz = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name
            )
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    drgbz__nadg = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    geliw__dshoj = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', drgbz__nadg, geliw__dshoj,
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
        bbkv__mpp = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, ('$_bodo_col3_',))
        wbs__wdadi = bbkv__mpp.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        wghx__qwrvz = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            wbs__wdadi, 0)
        doedn__dpqec = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            wbs__wdadi)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
            doedn__dpqec, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    drgbz__nadg = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    geliw__dshoj = dict(axis=0, inplace=False, kind='quicksort',
        ignore_index=False, key=None)
    check_unsupported_args('Series.sort_values', drgbz__nadg, geliw__dshoj,
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
        bbkv__mpp = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, ('$_bodo_col_',))
        wbs__wdadi = bbkv__mpp.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        wghx__qwrvz = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            wbs__wdadi, 0)
        doedn__dpqec = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            wbs__wdadi)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
            doedn__dpqec, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    ijbx__yzgq = is_overload_true(is_nullable)
    ecq__qbsyg = (
        'def impl(bins, arr, is_nullable=True, include_lowest=True):\n')
    ecq__qbsyg += '  numba.parfors.parfor.init_prange()\n'
    ecq__qbsyg += '  n = len(arr)\n'
    if ijbx__yzgq:
        ecq__qbsyg += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        ecq__qbsyg += '  out_arr = np.empty(n, np.int64)\n'
    ecq__qbsyg += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    ecq__qbsyg += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if ijbx__yzgq:
        ecq__qbsyg += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        ecq__qbsyg += '      out_arr[i] = -1\n'
    ecq__qbsyg += '      continue\n'
    ecq__qbsyg += '    val = arr[i]\n'
    ecq__qbsyg += '    if include_lowest and val == bins[0]:\n'
    ecq__qbsyg += '      ind = 1\n'
    ecq__qbsyg += '    else:\n'
    ecq__qbsyg += '      ind = np.searchsorted(bins, val)\n'
    ecq__qbsyg += '    if ind == 0 or ind == len(bins):\n'
    if ijbx__yzgq:
        ecq__qbsyg += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        ecq__qbsyg += '      out_arr[i] = -1\n'
    ecq__qbsyg += '    else:\n'
    ecq__qbsyg += '      out_arr[i] = ind - 1\n'
    ecq__qbsyg += '  return out_arr\n'
    ewh__wkoo = {}
    exec(ecq__qbsyg, {'bodo': bodo, 'np': np, 'numba': numba}, ewh__wkoo)
    impl = ewh__wkoo['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        uirko__ewmw, qwr__ocu = np.divmod(x, 1)
        if uirko__ewmw == 0:
            cdj__fszyo = -int(np.floor(np.log10(abs(qwr__ocu)))
                ) - 1 + precision
        else:
            cdj__fszyo = precision
        return np.around(x, cdj__fszyo)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        ttgy__cwdd = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(ttgy__cwdd)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        kypkr__jll = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            gumhw__wbpv = bins.copy()
            if right and include_lowest:
                gumhw__wbpv[0] = gumhw__wbpv[0] - kypkr__jll
            bzcj__wlequ = bodo.libs.interval_arr_ext.init_interval_array(
                gumhw__wbpv[:-1], gumhw__wbpv[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(bzcj__wlequ,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        gumhw__wbpv = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            gumhw__wbpv[0] = gumhw__wbpv[0] - 10.0 ** -precision
        bzcj__wlequ = bodo.libs.interval_arr_ext.init_interval_array(
            gumhw__wbpv[:-1], gumhw__wbpv[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(bzcj__wlequ, None
            )
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        fvywz__xlug = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        mjroc__oxi = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        wghx__qwrvz = np.zeros(nbins, np.int64)
        for yru__nfcr in range(len(fvywz__xlug)):
            wghx__qwrvz[mjroc__oxi[yru__nfcr]] = fvywz__xlug[yru__nfcr]
        return wghx__qwrvz
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
            xstvq__pmt = (max_val - min_val) * 0.001
            if right:
                bins[0] -= xstvq__pmt
            else:
                bins[-1] += xstvq__pmt
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    drgbz__nadg = dict(dropna=dropna)
    geliw__dshoj = dict(dropna=True)
    check_unsupported_args('Series.value_counts', drgbz__nadg, geliw__dshoj,
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
    qyxpg__qnk = not is_overload_none(bins)
    ecq__qbsyg = 'def impl(\n'
    ecq__qbsyg += '    S,\n'
    ecq__qbsyg += '    normalize=False,\n'
    ecq__qbsyg += '    sort=True,\n'
    ecq__qbsyg += '    ascending=False,\n'
    ecq__qbsyg += '    bins=None,\n'
    ecq__qbsyg += '    dropna=True,\n'
    ecq__qbsyg += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    ecq__qbsyg += '):\n'
    ecq__qbsyg += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    ecq__qbsyg += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    ecq__qbsyg += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if qyxpg__qnk:
        ecq__qbsyg += '    right = True\n'
        ecq__qbsyg += _gen_bins_handling(bins, S.dtype)
        ecq__qbsyg += '    arr = get_bin_inds(bins, arr)\n'
    ecq__qbsyg += (
        '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
    ecq__qbsyg += "        (arr,), index, ('$_bodo_col2_',)\n"
    ecq__qbsyg += '    )\n'
    ecq__qbsyg += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if qyxpg__qnk:
        ecq__qbsyg += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        ecq__qbsyg += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        ecq__qbsyg += '    index = get_bin_labels(bins)\n'
    else:
        ecq__qbsyg += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        ecq__qbsyg += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        ecq__qbsyg += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        ecq__qbsyg += '    )\n'
        ecq__qbsyg += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    ecq__qbsyg += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        ecq__qbsyg += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        xnc__unrgu = 'len(S)' if qyxpg__qnk else 'count_arr.sum()'
        ecq__qbsyg += f'    res = res / float({xnc__unrgu})\n'
    ecq__qbsyg += '    return res\n'
    ewh__wkoo = {}
    exec(ecq__qbsyg, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, ewh__wkoo)
    impl = ewh__wkoo['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    ecq__qbsyg = ''
    if isinstance(bins, types.Integer):
        ecq__qbsyg += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        ecq__qbsyg += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            ecq__qbsyg += '    min_val = min_val.value\n'
            ecq__qbsyg += '    max_val = max_val.value\n'
        ecq__qbsyg += (
            '    bins = compute_bins(bins, min_val, max_val, right)\n')
        if dtype == bodo.datetime64ns:
            ecq__qbsyg += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        ecq__qbsyg += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return ecq__qbsyg


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    drgbz__nadg = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    geliw__dshoj = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='General')
    ecq__qbsyg = 'def impl(\n'
    ecq__qbsyg += '    x,\n'
    ecq__qbsyg += '    bins,\n'
    ecq__qbsyg += '    right=True,\n'
    ecq__qbsyg += '    labels=None,\n'
    ecq__qbsyg += '    retbins=False,\n'
    ecq__qbsyg += '    precision=3,\n'
    ecq__qbsyg += '    include_lowest=False,\n'
    ecq__qbsyg += "    duplicates='raise',\n"
    ecq__qbsyg += '    ordered=True\n'
    ecq__qbsyg += '):\n'
    if isinstance(x, SeriesType):
        ecq__qbsyg += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        ecq__qbsyg += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        ecq__qbsyg += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        ecq__qbsyg += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    ecq__qbsyg += _gen_bins_handling(bins, x.dtype)
    ecq__qbsyg += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    ecq__qbsyg += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    ecq__qbsyg += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    ecq__qbsyg += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        ecq__qbsyg += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        ecq__qbsyg += '    return res\n'
    else:
        ecq__qbsyg += '    return out_arr\n'
    ewh__wkoo = {}
    exec(ecq__qbsyg, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, ewh__wkoo)
    impl = ewh__wkoo['impl']
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
    drgbz__nadg = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    geliw__dshoj = dict(labels=None, retbins=False, precision=3, duplicates
        ='raise')
    check_unsupported_args('pandas.qcut', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        esav__trn = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, esav__trn)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    drgbz__nadg = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze
        =squeeze, observed=observed, dropna=dropna)
    geliw__dshoj = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', drgbz__nadg, geliw__dshoj,
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
            pmwe__whiu = bodo.utils.conversion.coerce_to_array(index)
            bbkv__mpp = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                pmwe__whiu, arr), index, (' ', ''))
            return bbkv__mpp.groupby(' ')['']
        return impl_index
    wovs__mgdcd = by
    if isinstance(by, SeriesType):
        wovs__mgdcd = by.data
    if isinstance(wovs__mgdcd, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        pmwe__whiu = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        bbkv__mpp = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            pmwe__whiu, arr), index, (' ', ''))
        return bbkv__mpp.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    drgbz__nadg = dict(verify_integrity=verify_integrity)
    geliw__dshoj = dict(verify_integrity=False)
    check_unsupported_args('Series.append', drgbz__nadg, geliw__dshoj,
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
            kcd__wjv = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            wghx__qwrvz = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(wghx__qwrvz, A, kcd__wjv, False)
            return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wghx__qwrvz = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name
            )
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    drgbz__nadg = dict(interpolation=interpolation)
    geliw__dshoj = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            wghx__qwrvz = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
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
        tsvc__qkch = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(tsvc__qkch, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    drgbz__nadg = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    geliw__dshoj = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', drgbz__nadg, geliw__dshoj,
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
        fecyp__kxjb = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        fecyp__kxjb = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    ecq__qbsyg = 'def impl(\n'
    ecq__qbsyg += '    S,\n'
    ecq__qbsyg += '    value=None,\n'
    ecq__qbsyg += '    method=None,\n'
    ecq__qbsyg += '    axis=None,\n'
    ecq__qbsyg += '    inplace=False,\n'
    ecq__qbsyg += '    limit=None,\n'
    ecq__qbsyg += '    downcast=None,\n'
    ecq__qbsyg += '):  # pragma: no cover\n'
    ecq__qbsyg += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    ecq__qbsyg += (
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)\n')
    ecq__qbsyg += '    n = len(in_arr)\n'
    ecq__qbsyg += f'    out_arr = {fecyp__kxjb}(n, -1)\n'
    ecq__qbsyg += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    ecq__qbsyg += '        s = in_arr[j]\n'
    ecq__qbsyg += """        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna(
"""
    ecq__qbsyg += '            fill_arr, j\n'
    ecq__qbsyg += '        ):\n'
    ecq__qbsyg += '            s = fill_arr[j]\n'
    ecq__qbsyg += '        out_arr[j] = s\n'
    ecq__qbsyg += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    ldrk__oqq = dict()
    exec(ecq__qbsyg, {'bodo': bodo, 'numba': numba}, ldrk__oqq)
    bgyc__erzv = ldrk__oqq['impl']
    return bgyc__erzv


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        fecyp__kxjb = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        fecyp__kxjb = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    ecq__qbsyg = 'def impl(S,\n'
    ecq__qbsyg += '     value=None,\n'
    ecq__qbsyg += '    method=None,\n'
    ecq__qbsyg += '    axis=None,\n'
    ecq__qbsyg += '    inplace=False,\n'
    ecq__qbsyg += '    limit=None,\n'
    ecq__qbsyg += '   downcast=None,\n'
    ecq__qbsyg += '):\n'
    ecq__qbsyg += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    ecq__qbsyg += '    n = len(in_arr)\n'
    ecq__qbsyg += f'    out_arr = {fecyp__kxjb}(n, -1)\n'
    ecq__qbsyg += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    ecq__qbsyg += '        s = in_arr[j]\n'
    ecq__qbsyg += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    ecq__qbsyg += '            s = value\n'
    ecq__qbsyg += '        out_arr[j] = s\n'
    ecq__qbsyg += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    ldrk__oqq = dict()
    exec(ecq__qbsyg, {'bodo': bodo, 'numba': numba}, ldrk__oqq)
    bgyc__erzv = ldrk__oqq['impl']
    return bgyc__erzv


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    myzs__nfvj = bodo.hiframes.pd_series_ext.get_series_data(S)
    zkif__scysb = bodo.hiframes.pd_series_ext.get_series_data(value)
    for yru__nfcr in numba.parfors.parfor.internal_prange(len(myzs__nfvj)):
        s = myzs__nfvj[yru__nfcr]
        if bodo.libs.array_kernels.isna(myzs__nfvj, yru__nfcr
            ) and not bodo.libs.array_kernels.isna(zkif__scysb, yru__nfcr):
            s = zkif__scysb[yru__nfcr]
        myzs__nfvj[yru__nfcr] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    myzs__nfvj = bodo.hiframes.pd_series_ext.get_series_data(S)
    for yru__nfcr in numba.parfors.parfor.internal_prange(len(myzs__nfvj)):
        s = myzs__nfvj[yru__nfcr]
        if bodo.libs.array_kernels.isna(myzs__nfvj, yru__nfcr):
            s = value
        myzs__nfvj[yru__nfcr] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    myzs__nfvj = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    zkif__scysb = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(myzs__nfvj)
    wghx__qwrvz = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for snkcv__vao in numba.parfors.parfor.internal_prange(n):
        s = myzs__nfvj[snkcv__vao]
        if bodo.libs.array_kernels.isna(myzs__nfvj, snkcv__vao
            ) and not bodo.libs.array_kernels.isna(zkif__scysb, snkcv__vao):
            s = zkif__scysb[snkcv__vao]
        wghx__qwrvz[snkcv__vao] = s
        if bodo.libs.array_kernels.isna(myzs__nfvj, snkcv__vao
            ) and bodo.libs.array_kernels.isna(zkif__scysb, snkcv__vao):
            bodo.libs.array_kernels.setna(wghx__qwrvz, snkcv__vao)
    return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    myzs__nfvj = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    zkif__scysb = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(myzs__nfvj)
    wghx__qwrvz = bodo.utils.utils.alloc_type(n, myzs__nfvj.dtype, (-1,))
    for yru__nfcr in numba.parfors.parfor.internal_prange(n):
        s = myzs__nfvj[yru__nfcr]
        if bodo.libs.array_kernels.isna(myzs__nfvj, yru__nfcr
            ) and not bodo.libs.array_kernels.isna(zkif__scysb, yru__nfcr):
            s = zkif__scysb[yru__nfcr]
        wghx__qwrvz[yru__nfcr] = s
    return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    drgbz__nadg = dict(limit=limit, downcast=downcast)
    geliw__dshoj = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')
    vnzaa__szf = not is_overload_none(value)
    rvll__lneh = not is_overload_none(method)
    if vnzaa__szf and rvll__lneh:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not vnzaa__szf and not rvll__lneh:
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
    if rvll__lneh:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        dgrl__ycjb = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(dgrl__ycjb)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(dgrl__ycjb)
    cbuno__bdd = element_type(S.data)
    grg__hwqr = None
    if vnzaa__szf:
        grg__hwqr = element_type(types.unliteral(value))
    if grg__hwqr and not can_replace(cbuno__bdd, grg__hwqr):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {grg__hwqr} with series type {cbuno__bdd}'
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
        fas__dxn = S.data
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                myzs__nfvj = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                zkif__scysb = bodo.hiframes.pd_series_ext.get_series_data(value
                    )
                n = len(myzs__nfvj)
                wghx__qwrvz = bodo.utils.utils.alloc_type(n, fas__dxn, (-1,))
                for yru__nfcr in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(myzs__nfvj, yru__nfcr
                        ) and bodo.libs.array_kernels.isna(zkif__scysb,
                        yru__nfcr):
                        bodo.libs.array_kernels.setna(wghx__qwrvz, yru__nfcr)
                        continue
                    if bodo.libs.array_kernels.isna(myzs__nfvj, yru__nfcr):
                        wghx__qwrvz[yru__nfcr
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            zkif__scysb[yru__nfcr])
                        continue
                    wghx__qwrvz[yru__nfcr
                        ] = bodo.utils.conversion.unbox_if_timestamp(myzs__nfvj
                        [yru__nfcr])
                return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                    index, name)
            return fillna_series_impl
        if rvll__lneh:
            ovshh__nofz = (types.unicode_type, types.bool_, bodo.
                datetime64ns, bodo.timedelta64ns)
            if not isinstance(cbuno__bdd, (types.Integer, types.Float)
                ) and cbuno__bdd not in ovshh__nofz:
                raise BodoError(
                    f"Series.fillna(): series of type {cbuno__bdd} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                myzs__nfvj = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                wghx__qwrvz = bodo.libs.array_kernels.ffill_bfill_arr(
                    myzs__nfvj, method)
                return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            myzs__nfvj = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(myzs__nfvj)
            wghx__qwrvz = bodo.utils.utils.alloc_type(n, fas__dxn, (-1,))
            for yru__nfcr in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(myzs__nfvj[
                    yru__nfcr])
                if bodo.libs.array_kernels.isna(myzs__nfvj, yru__nfcr):
                    s = value
                wghx__qwrvz[yru__nfcr] = s
            return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        evvsg__nwhpz = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        drgbz__nadg = dict(limit=limit, downcast=downcast)
        geliw__dshoj = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', drgbz__nadg,
            geliw__dshoj, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        cbuno__bdd = element_type(S.data)
        ovshh__nofz = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(cbuno__bdd, (types.Integer, types.Float)
            ) and cbuno__bdd not in ovshh__nofz:
            raise BodoError(
                f'Series.{overload_name}(): series of type {cbuno__bdd} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            myzs__nfvj = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            wghx__qwrvz = bodo.libs.array_kernels.ffill_bfill_arr(myzs__nfvj,
                evvsg__nwhpz)
            return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        yusi__cuy = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(yusi__cuy
            )


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        gthvy__mtyqp = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(gthvy__mtyqp)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        gthvy__mtyqp = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(gthvy__mtyqp)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        gthvy__mtyqp = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(gthvy__mtyqp)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    drgbz__nadg = dict(inplace=inplace, limit=limit, regex=regex, method=method
        )
    yaw__rhdc = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', drgbz__nadg, yaw__rhdc,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    cbuno__bdd = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        oxeb__fzii = element_type(to_replace.key_type)
        grg__hwqr = element_type(to_replace.value_type)
    else:
        oxeb__fzii = element_type(to_replace)
        grg__hwqr = element_type(value)
    unkxg__rnlv = None
    if cbuno__bdd != types.unliteral(oxeb__fzii):
        if bodo.utils.typing.equality_always_false(cbuno__bdd, types.
            unliteral(oxeb__fzii)
            ) or not bodo.utils.typing.types_equality_exists(cbuno__bdd,
            oxeb__fzii):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(cbuno__bdd, (types.Float, types.Integer)
            ) or cbuno__bdd == np.bool_:
            unkxg__rnlv = cbuno__bdd
    if not can_replace(cbuno__bdd, types.unliteral(grg__hwqr)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    zpb__nezuu = S.data
    if isinstance(zpb__nezuu, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            myzs__nfvj = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(myzs__nfvj.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        myzs__nfvj = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(myzs__nfvj)
        wghx__qwrvz = bodo.utils.utils.alloc_type(n, zpb__nezuu, (-1,))
        tbv__puyng = build_replace_dict(to_replace, value, unkxg__rnlv)
        for yru__nfcr in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(myzs__nfvj, yru__nfcr):
                bodo.libs.array_kernels.setna(wghx__qwrvz, yru__nfcr)
                continue
            s = myzs__nfvj[yru__nfcr]
            if s in tbv__puyng:
                s = tbv__puyng[s]
            wghx__qwrvz[yru__nfcr] = s
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name
            )
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    wzy__dogl = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    biwx__xvppp = is_iterable_type(to_replace)
    aakjw__epsk = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    yrvhn__tgcq = is_iterable_type(value)
    if wzy__dogl and aakjw__epsk:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                tbv__puyng = {}
                tbv__puyng[key_dtype_conv(to_replace)] = value
                return tbv__puyng
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            tbv__puyng = {}
            tbv__puyng[to_replace] = value
            return tbv__puyng
        return impl
    if biwx__xvppp and aakjw__epsk:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                tbv__puyng = {}
                for evyfz__ffpky in to_replace:
                    tbv__puyng[key_dtype_conv(evyfz__ffpky)] = value
                return tbv__puyng
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            tbv__puyng = {}
            for evyfz__ffpky in to_replace:
                tbv__puyng[evyfz__ffpky] = value
            return tbv__puyng
        return impl
    if biwx__xvppp and yrvhn__tgcq:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                tbv__puyng = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for yru__nfcr in range(len(to_replace)):
                    tbv__puyng[key_dtype_conv(to_replace[yru__nfcr])] = value[
                        yru__nfcr]
                return tbv__puyng
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            tbv__puyng = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for yru__nfcr in range(len(to_replace)):
                tbv__puyng[to_replace[yru__nfcr]] = value[yru__nfcr]
            return tbv__puyng
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
            wghx__qwrvz = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wghx__qwrvz = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name
            )
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    drgbz__nadg = dict(ignore_index=ignore_index)
    vtdq__kzcoy = dict(ignore_index=False)
    check_unsupported_args('Series.explode', drgbz__nadg, vtdq__kzcoy,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        seus__expxi = bodo.utils.conversion.index_to_array(index)
        wghx__qwrvz, zin__tfgtb = bodo.libs.array_kernels.explode(arr,
            seus__expxi)
        doedn__dpqec = bodo.utils.conversion.index_from_array(zin__tfgtb)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
            doedn__dpqec, name)
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
            ojekx__ywg = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for yru__nfcr in numba.parfors.parfor.internal_prange(n):
                ojekx__ywg[yru__nfcr] = np.argmax(a[yru__nfcr])
            return ojekx__ywg
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            whcov__nczy = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for yru__nfcr in numba.parfors.parfor.internal_prange(n):
                whcov__nczy[yru__nfcr] = np.argmin(a[yru__nfcr])
            return whcov__nczy
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
    drgbz__nadg = dict(axis=axis, inplace=inplace, how=how)
    gjy__rutm = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', drgbz__nadg, gjy__rutm,
        package_name='pandas', module_name='Series')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            myzs__nfvj = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            gnweb__tsd = S.notna().values
            seus__expxi = bodo.utils.conversion.extract_index_array(S)
            doedn__dpqec = bodo.utils.conversion.convert_to_index(seus__expxi
                [gnweb__tsd])
            wghx__qwrvz = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(myzs__nfvj))
            return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                doedn__dpqec, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            myzs__nfvj = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            seus__expxi = bodo.utils.conversion.extract_index_array(S)
            gnweb__tsd = S.notna().values
            doedn__dpqec = bodo.utils.conversion.convert_to_index(seus__expxi
                [gnweb__tsd])
            wghx__qwrvz = myzs__nfvj[gnweb__tsd]
            return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                doedn__dpqec, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    drgbz__nadg = dict(freq=freq, axis=axis, fill_value=fill_value)
    geliw__dshoj = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', drgbz__nadg, geliw__dshoj,
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
        wghx__qwrvz = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name
            )
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    drgbz__nadg = dict(fill_method=fill_method, limit=limit, freq=freq)
    geliw__dshoj = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', drgbz__nadg, geliw__dshoj,
        package_name='pandas', module_name='Series')
    if not is_overload_int(periods):
        raise BodoError(
            'Series.pct_change(): periods argument must be an Integer')

    def impl(S, periods=1, fill_method='pad', limit=None, freq=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wghx__qwrvz = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name
            )
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
        wghx__qwrvz = bodo.hiframes.series_impl.where_impl(cond, arr, other)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name
            )
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
        wghx__qwrvz = bodo.hiframes.series_impl.where_impl(~cond, arr, other)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name
            )
    return impl


def _validate_arguments_mask_where(func_name, S, cond, other, inplace, axis,
    level, errors, try_cast):
    drgbz__nadg = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    geliw__dshoj = dict(inplace=False, level=None, errors='raise', try_cast
        =False)
    check_unsupported_args(f'{func_name}', drgbz__nadg, geliw__dshoj,
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
    odw__tsde = is_overload_constant_nan(other)
    if not (odw__tsde or is_scalar_type(other) or isinstance(other, types.
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
        nfhmf__eybql = S.dtype.elem_type
    else:
        nfhmf__eybql = S.dtype
    if is_iterable_type(other):
        mswmy__sxo = other.dtype
    elif odw__tsde:
        mswmy__sxo = types.float64
    else:
        mswmy__sxo = types.unliteral(other)
    if not is_common_scalar_dtype([nfhmf__eybql, mswmy__sxo]):
        raise BodoError(
            f"{func_name}() series and 'other' must share a common type.")


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        drgbz__nadg = dict(level=level, axis=axis)
        geliw__dshoj = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), drgbz__nadg,
            geliw__dshoj, package_name='pandas', module_name='Series')
        ezilo__hmqwv = other == string_type or is_overload_constant_str(other)
        wyjnz__ofj = is_iterable_type(other) and other.dtype == string_type
        cfy__dttkk = S.dtype == string_type and (op == operator.add and (
            ezilo__hmqwv or wyjnz__ofj) or op == operator.mul and
            isinstance(other, types.Integer))
        semmc__ecs = S.dtype == bodo.timedelta64ns
        youf__qvus = S.dtype == bodo.datetime64ns
        txag__ysvgl = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        wfbw__suraf = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        stsbi__zbq = semmc__ecs and (txag__ysvgl or wfbw__suraf
            ) or youf__qvus and txag__ysvgl
        stsbi__zbq = stsbi__zbq and op == operator.add
        if not (isinstance(S.dtype, types.Number) or cfy__dttkk or stsbi__zbq):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        efkyc__rln = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            zpb__nezuu = efkyc__rln.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and zpb__nezuu == types.Array(types.bool_, 1, 'C'):
                zpb__nezuu = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                wghx__qwrvz = bodo.utils.utils.alloc_type(n, zpb__nezuu, (-1,))
                for yru__nfcr in numba.parfors.parfor.internal_prange(n):
                    vdhk__jedsv = bodo.libs.array_kernels.isna(arr, yru__nfcr)
                    if vdhk__jedsv:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(wghx__qwrvz,
                                yru__nfcr)
                        else:
                            wghx__qwrvz[yru__nfcr] = op(fill_value, other)
                    else:
                        wghx__qwrvz[yru__nfcr] = op(arr[yru__nfcr], other)
                return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        zpb__nezuu = efkyc__rln.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and zpb__nezuu == types.Array(
            types.bool_, 1, 'C'):
            zpb__nezuu = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            cdb__nlp = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            wghx__qwrvz = bodo.utils.utils.alloc_type(n, zpb__nezuu, (-1,))
            for yru__nfcr in numba.parfors.parfor.internal_prange(n):
                vdhk__jedsv = bodo.libs.array_kernels.isna(arr, yru__nfcr)
                xpdn__dqd = bodo.libs.array_kernels.isna(cdb__nlp, yru__nfcr)
                if vdhk__jedsv and xpdn__dqd:
                    bodo.libs.array_kernels.setna(wghx__qwrvz, yru__nfcr)
                elif vdhk__jedsv:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(wghx__qwrvz, yru__nfcr)
                    else:
                        wghx__qwrvz[yru__nfcr] = op(fill_value, cdb__nlp[
                            yru__nfcr])
                elif xpdn__dqd:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(wghx__qwrvz, yru__nfcr)
                    else:
                        wghx__qwrvz[yru__nfcr] = op(arr[yru__nfcr], fill_value)
                else:
                    wghx__qwrvz[yru__nfcr] = op(arr[yru__nfcr], cdb__nlp[
                        yru__nfcr])
            return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
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
        efkyc__rln = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            zpb__nezuu = efkyc__rln.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and zpb__nezuu == types.Array(types.bool_, 1, 'C'):
                zpb__nezuu = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                wghx__qwrvz = bodo.utils.utils.alloc_type(n, zpb__nezuu, None)
                for yru__nfcr in numba.parfors.parfor.internal_prange(n):
                    vdhk__jedsv = bodo.libs.array_kernels.isna(arr, yru__nfcr)
                    if vdhk__jedsv:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(wghx__qwrvz,
                                yru__nfcr)
                        else:
                            wghx__qwrvz[yru__nfcr] = op(other, fill_value)
                    else:
                        wghx__qwrvz[yru__nfcr] = op(other, arr[yru__nfcr])
                return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        zpb__nezuu = efkyc__rln.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and zpb__nezuu == types.Array(
            types.bool_, 1, 'C'):
            zpb__nezuu = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            cdb__nlp = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            wghx__qwrvz = bodo.utils.utils.alloc_type(n, zpb__nezuu, None)
            for yru__nfcr in numba.parfors.parfor.internal_prange(n):
                vdhk__jedsv = bodo.libs.array_kernels.isna(arr, yru__nfcr)
                xpdn__dqd = bodo.libs.array_kernels.isna(cdb__nlp, yru__nfcr)
                wghx__qwrvz[yru__nfcr] = op(cdb__nlp[yru__nfcr], arr[yru__nfcr]
                    )
                if vdhk__jedsv and xpdn__dqd:
                    bodo.libs.array_kernels.setna(wghx__qwrvz, yru__nfcr)
                elif vdhk__jedsv:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(wghx__qwrvz, yru__nfcr)
                    else:
                        wghx__qwrvz[yru__nfcr] = op(cdb__nlp[yru__nfcr],
                            fill_value)
                elif xpdn__dqd:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(wghx__qwrvz, yru__nfcr)
                    else:
                        wghx__qwrvz[yru__nfcr] = op(fill_value, arr[yru__nfcr])
                else:
                    wghx__qwrvz[yru__nfcr] = op(cdb__nlp[yru__nfcr], arr[
                        yru__nfcr])
            return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
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
    for op, apwgi__dpho in explicit_binop_funcs_two_ways.items():
        for name in apwgi__dpho:
            yusi__cuy = create_explicit_binary_op_overload(op)
            ysnj__qhftz = create_explicit_binary_reverse_op_overload(op)
            aeq__xqet = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(yusi__cuy)
            overload_method(SeriesType, aeq__xqet, no_unliteral=True)(
                ysnj__qhftz)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        yusi__cuy = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(yusi__cuy)
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
                wksx__txgh = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                wghx__qwrvz = dt64_arr_sub(arr, wksx__txgh)
                return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
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
                wghx__qwrvz = np.empty(n, np.dtype('datetime64[ns]'))
                for yru__nfcr in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, yru__nfcr):
                        bodo.libs.array_kernels.setna(wghx__qwrvz, yru__nfcr)
                        continue
                    ubmd__vyxc = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[yru__nfcr]))
                    oqd__kacmi = op(ubmd__vyxc, rhs)
                    wghx__qwrvz[yru__nfcr
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        oqd__kacmi.value)
                return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
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
                    wksx__txgh = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    wghx__qwrvz = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(wksx__txgh))
                    return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                wksx__txgh = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                wghx__qwrvz = op(arr, wksx__txgh)
                return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    vlz__rmad = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    wghx__qwrvz = op(bodo.utils.conversion.
                        unbox_if_timestamp(vlz__rmad), arr)
                    return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                vlz__rmad = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                wghx__qwrvz = op(vlz__rmad, arr)
                return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        yusi__cuy = create_binary_op_overload(op)
        overload(op)(yusi__cuy)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    vhwcb__slg = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, vhwcb__slg)
        for yru__nfcr in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, yru__nfcr
                ) or bodo.libs.array_kernels.isna(arg2, yru__nfcr):
                bodo.libs.array_kernels.setna(S, yru__nfcr)
                continue
            S[yru__nfcr
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                yru__nfcr]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[yru__nfcr]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                cdb__nlp = bodo.utils.conversion.get_array_if_series_or_index(
                    other)
                op(arr, cdb__nlp)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        yusi__cuy = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(yusi__cuy)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                wghx__qwrvz = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        yusi__cuy = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(yusi__cuy)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    wghx__qwrvz = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
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
                    cdb__nlp = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    wghx__qwrvz = ufunc(arr, cdb__nlp)
                    return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    cdb__nlp = bodo.hiframes.pd_series_ext.get_series_data(S2)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    wghx__qwrvz = ufunc(arr, cdb__nlp)
                    return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        yusi__cuy = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(yusi__cuy)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        zmy__foo = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),))
        orqwm__fhq = np.arange(n),
        bodo.libs.timsort.sort(zmy__foo, 0, n, orqwm__fhq)
        return orqwm__fhq[0]
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
        wrig__cia = get_overload_const_str(downcast)
        if wrig__cia in ('integer', 'signed'):
            out_dtype = types.int64
        elif wrig__cia == 'unsigned':
            out_dtype = types.uint64
        else:
            assert wrig__cia == 'float'
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            myzs__nfvj = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            wghx__qwrvz = pd.to_numeric(myzs__nfvj, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                index, name)
        return impl_series
    if arg_a != string_array_type:
        raise BodoError('pd.to_numeric(): invalid argument type {}'.format(
            arg_a))
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            zfd__tmm = np.empty(n, np.float64)
            for yru__nfcr in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, yru__nfcr):
                    bodo.libs.array_kernels.setna(zfd__tmm, yru__nfcr)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(zfd__tmm,
                        yru__nfcr, arg_a, yru__nfcr)
            return zfd__tmm
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            zfd__tmm = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for yru__nfcr in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, yru__nfcr):
                    bodo.libs.array_kernels.setna(zfd__tmm, yru__nfcr)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(zfd__tmm,
                        yru__nfcr, arg_a, yru__nfcr)
            return zfd__tmm
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        usbmy__biazp = if_series_to_array_type(args[0])
        if isinstance(usbmy__biazp, types.Array) and isinstance(usbmy__biazp
            .dtype, types.Integer):
            usbmy__biazp = types.Array(types.float64, 1, 'C')
        return usbmy__biazp(*args)


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
    tzf__fmdgo = bodo.utils.utils.is_array_typ(x, True)
    cmb__sxz = bodo.utils.utils.is_array_typ(y, True)
    ecq__qbsyg = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        ecq__qbsyg += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if tzf__fmdgo and not bodo.utils.utils.is_array_typ(x, False):
        ecq__qbsyg += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if cmb__sxz and not bodo.utils.utils.is_array_typ(y, False):
        ecq__qbsyg += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    ecq__qbsyg += '  n = len(condition)\n'
    dctg__hke = x.dtype if tzf__fmdgo else types.unliteral(x)
    alb__qipbp = y.dtype if cmb__sxz else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        dctg__hke = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        alb__qipbp = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    tlw__rjih = get_data(x)
    mpw__mchbb = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(orqwm__fhq) for
        orqwm__fhq in [tlw__rjih, mpw__mchbb])
    if tlw__rjih == mpw__mchbb and not is_nullable:
        out_dtype = dtype_to_array_type(dctg__hke)
    elif dctg__hke == string_type or alb__qipbp == string_type:
        out_dtype = bodo.string_array_type
    elif tlw__rjih == bytes_type or (tzf__fmdgo and dctg__hke == bytes_type
        ) and (mpw__mchbb == bytes_type or cmb__sxz and alb__qipbp ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(dctg__hke, bodo.PDCategoricalDtype):
        out_dtype = None
    elif dctg__hke in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(dctg__hke, 1, 'C')
    elif alb__qipbp in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(alb__qipbp, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(dctg__hke), numba.np.numpy_support.
            as_dtype(alb__qipbp)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(dctg__hke, bodo.PDCategoricalDtype):
        lrh__fefw = 'x'
    else:
        lrh__fefw = 'out_dtype'
    ecq__qbsyg += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {lrh__fefw}, (-1,))\n')
    if isinstance(dctg__hke, bodo.PDCategoricalDtype):
        ecq__qbsyg += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        ecq__qbsyg += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    ecq__qbsyg += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    ecq__qbsyg += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if tzf__fmdgo:
        ecq__qbsyg += '      if bodo.libs.array_kernels.isna(x, j):\n'
        ecq__qbsyg += '        setna(out_arr, j)\n'
        ecq__qbsyg += '        continue\n'
    if isinstance(dctg__hke, bodo.PDCategoricalDtype):
        ecq__qbsyg += '      out_codes[j] = x_codes[j]\n'
    else:
        ecq__qbsyg += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if tzf__fmdgo else 'x'))
    ecq__qbsyg += '    else:\n'
    if cmb__sxz:
        ecq__qbsyg += '      if bodo.libs.array_kernels.isna(y, j):\n'
        ecq__qbsyg += '        setna(out_arr, j)\n'
        ecq__qbsyg += '        continue\n'
    ecq__qbsyg += (
        '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
        .format('y[j]' if cmb__sxz else 'y'))
    ecq__qbsyg += '  return out_arr\n'
    ewh__wkoo = {}
    exec(ecq__qbsyg, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, ewh__wkoo)
    lnvyc__vkwj = ewh__wkoo['_impl']
    return lnvyc__vkwj


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
        mut__qiss = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(mut__qiss, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(mut__qiss):
            rkah__nnmwp = mut__qiss.data.dtype
        else:
            rkah__nnmwp = mut__qiss.dtype
        if isinstance(rkah__nnmwp, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        bzb__hdv = mut__qiss
    else:
        rci__viu = []
        for mut__qiss in choicelist:
            if not bodo.utils.utils.is_array_typ(mut__qiss, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(mut__qiss):
                rkah__nnmwp = mut__qiss.data.dtype
            else:
                rkah__nnmwp = mut__qiss.dtype
            if isinstance(rkah__nnmwp, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            rci__viu.append(rkah__nnmwp)
        if not is_common_scalar_dtype(rci__viu):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        bzb__hdv = choicelist[0]
    if is_series_type(bzb__hdv):
        bzb__hdv = bzb__hdv.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, bzb__hdv.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(bzb__hdv, types.Array) or isinstance(bzb__hdv,
        BooleanArrayType) or isinstance(bzb__hdv, IntegerArrayType) or bodo
        .utils.utils.is_array_typ(bzb__hdv, False) and bzb__hdv.dtype in [
        bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {bzb__hdv} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    ixyxy__tcc = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        ovaod__yimp = choicelist.dtype
    else:
        lnaw__bibpb = False
        rci__viu = []
        for mut__qiss in choicelist:
            if is_nullable_type(mut__qiss):
                lnaw__bibpb = True
            if is_series_type(mut__qiss):
                rkah__nnmwp = mut__qiss.data.dtype
            else:
                rkah__nnmwp = mut__qiss.dtype
            if isinstance(rkah__nnmwp, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            rci__viu.append(rkah__nnmwp)
        hcy__tcdw, yfsw__tuo = get_common_scalar_dtype(rci__viu)
        if not yfsw__tuo:
            raise BodoError('Internal error in overload_np_select')
        qab__cnq = dtype_to_array_type(hcy__tcdw)
        if lnaw__bibpb:
            qab__cnq = to_nullable_type(qab__cnq)
        ovaod__yimp = qab__cnq
    if isinstance(ovaod__yimp, SeriesType):
        ovaod__yimp = ovaod__yimp.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        ikzmp__utqrd = True
    else:
        ikzmp__utqrd = False
    kybqg__zxe = False
    usx__pcx = False
    if ikzmp__utqrd:
        if isinstance(ovaod__yimp.dtype, types.Number):
            pass
        elif ovaod__yimp.dtype == types.bool_:
            usx__pcx = True
        else:
            kybqg__zxe = True
            ovaod__yimp = to_nullable_type(ovaod__yimp)
    elif default == types.none or is_overload_constant_nan(default):
        kybqg__zxe = True
        ovaod__yimp = to_nullable_type(ovaod__yimp)
    ecq__qbsyg = 'def np_select_impl(condlist, choicelist, default=0):\n'
    ecq__qbsyg += '  if len(condlist) != len(choicelist):\n'
    ecq__qbsyg += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    ecq__qbsyg += '  output_len = len(choicelist[0])\n'
    ecq__qbsyg += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    ecq__qbsyg += '  for i in range(output_len):\n'
    if kybqg__zxe:
        ecq__qbsyg += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif usx__pcx:
        ecq__qbsyg += '    out[i] = False\n'
    else:
        ecq__qbsyg += '    out[i] = default\n'
    if ixyxy__tcc:
        ecq__qbsyg += '  for i in range(len(condlist) - 1, -1, -1):\n'
        ecq__qbsyg += '    cond = condlist[i]\n'
        ecq__qbsyg += '    choice = choicelist[i]\n'
        ecq__qbsyg += '    out = np.where(cond, choice, out)\n'
    else:
        for yru__nfcr in range(len(choicelist) - 1, -1, -1):
            ecq__qbsyg += f'  cond = condlist[{yru__nfcr}]\n'
            ecq__qbsyg += f'  choice = choicelist[{yru__nfcr}]\n'
            ecq__qbsyg += f'  out = np.where(cond, choice, out)\n'
    ecq__qbsyg += '  return out'
    ewh__wkoo = dict()
    exec(ecq__qbsyg, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': ovaod__yimp}, ewh__wkoo)
    impl = ewh__wkoo['np_select_impl']
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    drgbz__nadg = dict(subset=subset, keep=keep, inplace=inplace)
    geliw__dshoj = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', drgbz__nadg,
        geliw__dshoj, package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        gbe__ljjnz = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (gbe__ljjnz,), seus__expxi = bodo.libs.array_kernels.drop_duplicates((
            gbe__ljjnz,), index, 1)
        index = bodo.utils.conversion.index_from_array(seus__expxi)
        return bodo.hiframes.pd_series_ext.init_series(gbe__ljjnz, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    ttbs__rbxw = element_type(S.data)
    if not is_common_scalar_dtype([ttbs__rbxw, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([ttbs__rbxw, right]):
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
        wghx__qwrvz = np.empty(n, np.bool_)
        for yru__nfcr in numba.parfors.parfor.internal_prange(n):
            ccgj__vqnl = bodo.utils.conversion.box_if_dt64(arr[yru__nfcr])
            if inclusive == 'both':
                wghx__qwrvz[yru__nfcr
                    ] = ccgj__vqnl <= right and ccgj__vqnl >= left
            else:
                wghx__qwrvz[yru__nfcr
                    ] = ccgj__vqnl < right and ccgj__vqnl > left
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz, index, name
            )
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    drgbz__nadg = dict(axis=axis)
    geliw__dshoj = dict(axis=None)
    check_unsupported_args('Series.repeat', drgbz__nadg, geliw__dshoj,
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
            seus__expxi = bodo.utils.conversion.index_to_array(index)
            wghx__qwrvz = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            zin__tfgtb = bodo.libs.array_kernels.repeat_kernel(seus__expxi,
                repeats)
            doedn__dpqec = bodo.utils.conversion.index_from_array(zin__tfgtb)
            return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
                doedn__dpqec, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        seus__expxi = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        wghx__qwrvz = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        zin__tfgtb = bodo.libs.array_kernels.repeat_kernel(seus__expxi, repeats
            )
        doedn__dpqec = bodo.utils.conversion.index_from_array(zin__tfgtb)
        return bodo.hiframes.pd_series_ext.init_series(wghx__qwrvz,
            doedn__dpqec, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        orqwm__fhq = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(orqwm__fhq)
        hhg__uos = {}
        for yru__nfcr in range(n):
            ccgj__vqnl = bodo.utils.conversion.box_if_dt64(orqwm__fhq[
                yru__nfcr])
            hhg__uos[index[yru__nfcr]] = ccgj__vqnl
        return hhg__uos
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    dgrl__ycjb = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            uwl__ufu = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(dgrl__ycjb)
    elif is_literal_type(name):
        uwl__ufu = get_literal_value(name)
    else:
        raise_bodo_error(dgrl__ycjb)
    uwl__ufu = 0 if uwl__ufu is None else uwl__ufu

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            (uwl__ufu,))
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
