"""
Implements array operations for usage by DataFrames and Series
such as count and max.
"""
import numba
import numpy as np
import pandas as pd
from numba import generated_jit
from numba.core import types
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.utils.typing import element_type, is_hashable_type, is_iterable_type, is_overload_true, is_overload_zero


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    yvc__jkme = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(yvc__jkme.ctypes, arr,
        parallel, skipna)
    return yvc__jkme[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        sxve__glc = len(arr)
        iggel__ykocj = np.empty(sxve__glc, np.bool_)
        for kgl__irclz in numba.parfors.parfor.internal_prange(sxve__glc):
            iggel__ykocj[kgl__irclz] = bodo.libs.array_kernels.isna(arr,
                kgl__irclz)
        return iggel__ykocj
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        iivq__ivxz = 0
        for kgl__irclz in numba.parfors.parfor.internal_prange(len(arr)):
            gcp__zvsgw = 0
            if not bodo.libs.array_kernels.isna(arr, kgl__irclz):
                gcp__zvsgw = 1
            iivq__ivxz += gcp__zvsgw
        yvc__jkme = iivq__ivxz
        return yvc__jkme
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    quaw__fgpym = array_op_count(arr)
    nyay__spjz = array_op_min(arr)
    kdmli__ulgd = array_op_max(arr)
    nsia__bma = array_op_mean(arr)
    narc__cyduq = array_op_std(arr)
    ogv__ihrvp = array_op_quantile(arr, 0.25)
    znlei__eeu = array_op_quantile(arr, 0.5)
    qrz__uevaw = array_op_quantile(arr, 0.75)
    return (quaw__fgpym, nsia__bma, narc__cyduq, nyay__spjz, ogv__ihrvp,
        znlei__eeu, qrz__uevaw, kdmli__ulgd)


def array_op_describe_dt_impl(arr):
    quaw__fgpym = array_op_count(arr)
    nyay__spjz = array_op_min(arr)
    kdmli__ulgd = array_op_max(arr)
    nsia__bma = array_op_mean(arr)
    ogv__ihrvp = array_op_quantile(arr, 0.25)
    znlei__eeu = array_op_quantile(arr, 0.5)
    qrz__uevaw = array_op_quantile(arr, 0.75)
    return (quaw__fgpym, nsia__bma, nyay__spjz, ogv__ihrvp, znlei__eeu,
        qrz__uevaw, kdmli__ulgd)


@overload(array_op_describe)
def overload_array_op_describe(arr):
    if arr.dtype == bodo.datetime64ns:
        return array_op_describe_dt_impl
    return array_op_describe_impl


def array_op_min(arr):
    pass


@overload(array_op_min)
def overload_array_op_min(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            kotl__lyctd = numba.cpython.builtins.get_type_max_value(np.int64)
            iivq__ivxz = 0
            for kgl__irclz in numba.parfors.parfor.internal_prange(len(arr)):
                sssc__ont = kotl__lyctd
                gcp__zvsgw = 0
                if not bodo.libs.array_kernels.isna(arr, kgl__irclz):
                    sssc__ont = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[kgl__irclz]))
                    gcp__zvsgw = 1
                kotl__lyctd = min(kotl__lyctd, sssc__ont)
                iivq__ivxz += gcp__zvsgw
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(kotl__lyctd,
                iivq__ivxz)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            kotl__lyctd = numba.cpython.builtins.get_type_max_value(np.int64)
            iivq__ivxz = 0
            for kgl__irclz in numba.parfors.parfor.internal_prange(len(arr)):
                sssc__ont = kotl__lyctd
                gcp__zvsgw = 0
                if not bodo.libs.array_kernels.isna(arr, kgl__irclz):
                    sssc__ont = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[kgl__irclz])
                    gcp__zvsgw = 1
                kotl__lyctd = min(kotl__lyctd, sssc__ont)
                iivq__ivxz += gcp__zvsgw
            return bodo.hiframes.pd_index_ext._dti_val_finalize(kotl__lyctd,
                iivq__ivxz)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            awgha__cac = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            kotl__lyctd = numba.cpython.builtins.get_type_max_value(np.int64)
            iivq__ivxz = 0
            for kgl__irclz in numba.parfors.parfor.internal_prange(len(
                awgha__cac)):
                opr__oau = awgha__cac[kgl__irclz]
                if opr__oau == -1:
                    continue
                kotl__lyctd = min(kotl__lyctd, opr__oau)
                iivq__ivxz += 1
            yvc__jkme = bodo.hiframes.series_kernels._box_cat_val(kotl__lyctd,
                arr.dtype, iivq__ivxz)
            return yvc__jkme
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            kotl__lyctd = bodo.hiframes.series_kernels._get_date_max_value()
            iivq__ivxz = 0
            for kgl__irclz in numba.parfors.parfor.internal_prange(len(arr)):
                sssc__ont = kotl__lyctd
                gcp__zvsgw = 0
                if not bodo.libs.array_kernels.isna(arr, kgl__irclz):
                    sssc__ont = arr[kgl__irclz]
                    gcp__zvsgw = 1
                kotl__lyctd = min(kotl__lyctd, sssc__ont)
                iivq__ivxz += gcp__zvsgw
            yvc__jkme = bodo.hiframes.series_kernels._sum_handle_nan(
                kotl__lyctd, iivq__ivxz)
            return yvc__jkme
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        kotl__lyctd = bodo.hiframes.series_kernels._get_type_max_value(arr.
            dtype)
        iivq__ivxz = 0
        for kgl__irclz in numba.parfors.parfor.internal_prange(len(arr)):
            sssc__ont = kotl__lyctd
            gcp__zvsgw = 0
            if not bodo.libs.array_kernels.isna(arr, kgl__irclz):
                sssc__ont = arr[kgl__irclz]
                gcp__zvsgw = 1
            kotl__lyctd = min(kotl__lyctd, sssc__ont)
            iivq__ivxz += gcp__zvsgw
        yvc__jkme = bodo.hiframes.series_kernels._sum_handle_nan(kotl__lyctd,
            iivq__ivxz)
        return yvc__jkme
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            kotl__lyctd = numba.cpython.builtins.get_type_min_value(np.int64)
            iivq__ivxz = 0
            for kgl__irclz in numba.parfors.parfor.internal_prange(len(arr)):
                sssc__ont = kotl__lyctd
                gcp__zvsgw = 0
                if not bodo.libs.array_kernels.isna(arr, kgl__irclz):
                    sssc__ont = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[kgl__irclz]))
                    gcp__zvsgw = 1
                kotl__lyctd = max(kotl__lyctd, sssc__ont)
                iivq__ivxz += gcp__zvsgw
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(kotl__lyctd,
                iivq__ivxz)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            kotl__lyctd = numba.cpython.builtins.get_type_min_value(np.int64)
            iivq__ivxz = 0
            for kgl__irclz in numba.parfors.parfor.internal_prange(len(arr)):
                sssc__ont = kotl__lyctd
                gcp__zvsgw = 0
                if not bodo.libs.array_kernels.isna(arr, kgl__irclz):
                    sssc__ont = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[kgl__irclz])
                    gcp__zvsgw = 1
                kotl__lyctd = max(kotl__lyctd, sssc__ont)
                iivq__ivxz += gcp__zvsgw
            return bodo.hiframes.pd_index_ext._dti_val_finalize(kotl__lyctd,
                iivq__ivxz)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            awgha__cac = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            kotl__lyctd = -1
            for kgl__irclz in numba.parfors.parfor.internal_prange(len(
                awgha__cac)):
                kotl__lyctd = max(kotl__lyctd, awgha__cac[kgl__irclz])
            yvc__jkme = bodo.hiframes.series_kernels._box_cat_val(kotl__lyctd,
                arr.dtype, 1)
            return yvc__jkme
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            kotl__lyctd = bodo.hiframes.series_kernels._get_date_min_value()
            iivq__ivxz = 0
            for kgl__irclz in numba.parfors.parfor.internal_prange(len(arr)):
                sssc__ont = kotl__lyctd
                gcp__zvsgw = 0
                if not bodo.libs.array_kernels.isna(arr, kgl__irclz):
                    sssc__ont = arr[kgl__irclz]
                    gcp__zvsgw = 1
                kotl__lyctd = max(kotl__lyctd, sssc__ont)
                iivq__ivxz += gcp__zvsgw
            yvc__jkme = bodo.hiframes.series_kernels._sum_handle_nan(
                kotl__lyctd, iivq__ivxz)
            return yvc__jkme
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        kotl__lyctd = bodo.hiframes.series_kernels._get_type_min_value(arr.
            dtype)
        iivq__ivxz = 0
        for kgl__irclz in numba.parfors.parfor.internal_prange(len(arr)):
            sssc__ont = kotl__lyctd
            gcp__zvsgw = 0
            if not bodo.libs.array_kernels.isna(arr, kgl__irclz):
                sssc__ont = arr[kgl__irclz]
                gcp__zvsgw = 1
            kotl__lyctd = max(kotl__lyctd, sssc__ont)
            iivq__ivxz += gcp__zvsgw
        yvc__jkme = bodo.hiframes.series_kernels._sum_handle_nan(kotl__lyctd,
            iivq__ivxz)
        return yvc__jkme
    return impl


def array_op_mean(arr):
    pass


@overload(array_op_mean)
def overload_array_op_mean(arr):
    if arr.dtype == bodo.datetime64ns:

        def impl(arr):
            return pd.Timestamp(types.int64(bodo.libs.array_ops.
                array_op_mean(arr.view(np.int64))))
        return impl
    gpnx__voxs = types.float64
    fvp__fuku = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        gpnx__voxs = types.float32
        fvp__fuku = types.float32
    geji__cuyrm = gpnx__voxs(0)
    zzut__oafen = fvp__fuku(0)
    luuf__cufp = fvp__fuku(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        kotl__lyctd = geji__cuyrm
        iivq__ivxz = zzut__oafen
        for kgl__irclz in numba.parfors.parfor.internal_prange(len(arr)):
            sssc__ont = geji__cuyrm
            gcp__zvsgw = zzut__oafen
            if not bodo.libs.array_kernels.isna(arr, kgl__irclz):
                sssc__ont = arr[kgl__irclz]
                gcp__zvsgw = luuf__cufp
            kotl__lyctd += sssc__ont
            iivq__ivxz += gcp__zvsgw
        yvc__jkme = bodo.hiframes.series_kernels._mean_handle_nan(kotl__lyctd,
            iivq__ivxz)
        return yvc__jkme
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        ncxb__yjpf = 0.0
        dzrtr__nstlp = 0.0
        iivq__ivxz = 0
        for kgl__irclz in numba.parfors.parfor.internal_prange(len(arr)):
            sssc__ont = 0.0
            gcp__zvsgw = 0
            if not bodo.libs.array_kernels.isna(arr, kgl__irclz) or not skipna:
                sssc__ont = arr[kgl__irclz]
                gcp__zvsgw = 1
            ncxb__yjpf += sssc__ont
            dzrtr__nstlp += sssc__ont * sssc__ont
            iivq__ivxz += gcp__zvsgw
        kotl__lyctd = dzrtr__nstlp - ncxb__yjpf * ncxb__yjpf / iivq__ivxz
        yvc__jkme = bodo.hiframes.series_kernels._handle_nan_count_ddof(
            kotl__lyctd, iivq__ivxz, ddof)
        return yvc__jkme
    return impl


def array_op_std(arr, skipna=True, ddof=1):
    pass


@overload(array_op_std)
def overload_array_op_std(arr, skipna=True, ddof=1):
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr, skipna=True, ddof=1):
            return pd.Timedelta(types.int64(array_op_var(arr.view(np.int64),
                skipna, ddof) ** 0.5))
        return impl_dt64
    return lambda arr, skipna=True, ddof=1: array_op_var(arr, skipna, ddof
        ) ** 0.5


def array_op_quantile(arr, q):
    pass


@overload(array_op_quantile)
def overload_array_op_quantile(arr, q):
    if is_iterable_type(q):
        if arr.dtype == bodo.datetime64ns:

            def _impl_list_dt(arr, q):
                iggel__ykocj = np.empty(len(q), np.int64)
                for kgl__irclz in range(len(q)):
                    gdrj__nibak = np.float64(q[kgl__irclz])
                    iggel__ykocj[kgl__irclz
                        ] = bodo.libs.array_kernels.quantile(arr.view(np.
                        int64), gdrj__nibak)
                return iggel__ykocj.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            iggel__ykocj = np.empty(len(q), np.float64)
            for kgl__irclz in range(len(q)):
                gdrj__nibak = np.float64(q[kgl__irclz])
                iggel__ykocj[kgl__irclz] = bodo.libs.array_kernels.quantile(arr
                    , gdrj__nibak)
            return iggel__ykocj
        return impl_list
    if arr.dtype == bodo.datetime64ns:

        def _impl_dt(arr, q):
            return pd.Timestamp(bodo.libs.array_kernels.quantile(arr.view(
                np.int64), np.float64(q)))
        return _impl_dt

    def impl(arr, q):
        return bodo.libs.array_kernels.quantile(arr, np.float64(q))
    return impl


def array_op_sum(arr, skipna, min_count):
    pass


@overload(array_op_sum, no_unliteral=True)
def overload_array_op_sum(arr, skipna, min_count):
    if isinstance(arr.dtype, types.Integer):
        hpk__dlxzz = types.intp
    elif arr.dtype == types.bool_:
        hpk__dlxzz = np.int64
    else:
        hpk__dlxzz = arr.dtype
    xdnln__avbsp = hpk__dlxzz(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            kotl__lyctd = xdnln__avbsp
            sxve__glc = len(arr)
            iivq__ivxz = 0
            for kgl__irclz in numba.parfors.parfor.internal_prange(sxve__glc):
                sssc__ont = xdnln__avbsp
                gcp__zvsgw = 0
                if not bodo.libs.array_kernels.isna(arr, kgl__irclz
                    ) or not skipna:
                    sssc__ont = arr[kgl__irclz]
                    gcp__zvsgw = 1
                kotl__lyctd += sssc__ont
                iivq__ivxz += gcp__zvsgw
            yvc__jkme = bodo.hiframes.series_kernels._var_handle_mincount(
                kotl__lyctd, iivq__ivxz, min_count)
            return yvc__jkme
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            kotl__lyctd = xdnln__avbsp
            sxve__glc = len(arr)
            for kgl__irclz in numba.parfors.parfor.internal_prange(sxve__glc):
                sssc__ont = xdnln__avbsp
                if not bodo.libs.array_kernels.isna(arr, kgl__irclz):
                    sssc__ont = arr[kgl__irclz]
                kotl__lyctd += sssc__ont
            return kotl__lyctd
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    ofl__vhx = arr.dtype(1)
    if arr.dtype == types.bool_:
        ofl__vhx = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            kotl__lyctd = ofl__vhx
            iivq__ivxz = 0
            for kgl__irclz in numba.parfors.parfor.internal_prange(len(arr)):
                sssc__ont = ofl__vhx
                gcp__zvsgw = 0
                if not bodo.libs.array_kernels.isna(arr, kgl__irclz
                    ) or not skipna:
                    sssc__ont = arr[kgl__irclz]
                    gcp__zvsgw = 1
                iivq__ivxz += gcp__zvsgw
                kotl__lyctd *= sssc__ont
            yvc__jkme = bodo.hiframes.series_kernels._var_handle_mincount(
                kotl__lyctd, iivq__ivxz, min_count)
            return yvc__jkme
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            kotl__lyctd = ofl__vhx
            for kgl__irclz in numba.parfors.parfor.internal_prange(len(arr)):
                sssc__ont = ofl__vhx
                if not bodo.libs.array_kernels.isna(arr, kgl__irclz):
                    sssc__ont = arr[kgl__irclz]
                kotl__lyctd *= sssc__ont
            return kotl__lyctd
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        kgl__irclz = bodo.libs.array_kernels._nan_argmax(arr)
        return index[kgl__irclz]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        kgl__irclz = bodo.libs.array_kernels._nan_argmin(arr)
        return index[kgl__irclz]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            tulye__wqldz = {}
            for wikgy__ptc in values:
                tulye__wqldz[bodo.utils.conversion.box_if_dt64(wikgy__ptc)] = 0
            return tulye__wqldz
        return impl
    else:

        def impl(values, use_hash_impl):
            return values
        return impl


def array_op_isin(arr, values):
    pass


@overload(array_op_isin, inline='always')
def overload_array_op_isin(arr, values):
    use_hash_impl = element_type(values) == element_type(arr
        ) and is_hashable_type(element_type(values))

    def impl(arr, values):
        values = bodo.libs.array_ops._convert_isin_values(values, use_hash_impl
            )
        numba.parfors.parfor.init_prange()
        sxve__glc = len(arr)
        iggel__ykocj = np.empty(sxve__glc, np.bool_)
        for kgl__irclz in numba.parfors.parfor.internal_prange(sxve__glc):
            iggel__ykocj[kgl__irclz] = bodo.utils.conversion.box_if_dt64(arr
                [kgl__irclz]) in values
        return iggel__ykocj
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr):
    qdk__jwvgn = 'def impl(in_arr):\n'
    qdk__jwvgn += '  n = len(in_arr)\n'
    qdk__jwvgn += '  arr_map = {in_arr[0]: 0 for _ in range(0)}\n'
    qdk__jwvgn += '  in_lst = []\n'
    qdk__jwvgn += '  map_vector = np.empty(n, np.int64)\n'
    qdk__jwvgn += '  is_na = 0\n'
    if in_arr == bodo.string_array_type:
        qdk__jwvgn += '  total_len = 0\n'
    qdk__jwvgn += '  for i in range(n):\n'
    qdk__jwvgn += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
    qdk__jwvgn += '      is_na = 1\n'
    qdk__jwvgn += (
        '      # Always put NA in the last location. We can safely use\n')
    qdk__jwvgn += '      # -1 because in_arr[-1] == in_arr[len(in_arr) - 1]\n'
    qdk__jwvgn += '      set_val = -1\n'
    qdk__jwvgn += '    else:\n'
    qdk__jwvgn += '      data_val = in_arr[i]\n'
    qdk__jwvgn += '      if data_val not in arr_map:\n'
    qdk__jwvgn += '        set_val = len(arr_map)\n'
    qdk__jwvgn += '        # Add the data to index info\n'
    qdk__jwvgn += '        in_lst.append(data_val)\n'
    qdk__jwvgn += '        arr_map[data_val] = len(arr_map)\n'
    if in_arr == bodo.string_array_type:
        qdk__jwvgn += '        total_len += len(data_val)\n'
    qdk__jwvgn += '      else:\n'
    qdk__jwvgn += '        set_val = arr_map[data_val]\n'
    qdk__jwvgn += '    map_vector[i] = set_val\n'
    qdk__jwvgn += '  n_rows = len(arr_map) + is_na\n'
    if in_arr == bodo.string_array_type:
        qdk__jwvgn += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
    else:
        qdk__jwvgn += (
            '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n')
    qdk__jwvgn += '  for j in range(len(arr_map)):\n'
    qdk__jwvgn += '    out_arr[j] = in_lst[j]\n'
    qdk__jwvgn += '  if is_na:\n'
    qdk__jwvgn += '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n'
    qdk__jwvgn += '  return out_arr, map_vector\n'
    xwzle__gaqhq = {}
    exec(qdk__jwvgn, {'bodo': bodo, 'np': np}, xwzle__gaqhq)
    impl = xwzle__gaqhq['impl']
    return impl
