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
    ptaru__xww = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(ptaru__xww.ctypes,
        arr, parallel, skipna)
    return ptaru__xww[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        ngrr__oma = len(arr)
        ulid__crchy = np.empty(ngrr__oma, np.bool_)
        for csxz__bjqdi in numba.parfors.parfor.internal_prange(ngrr__oma):
            ulid__crchy[csxz__bjqdi] = bodo.libs.array_kernels.isna(arr,
                csxz__bjqdi)
        return ulid__crchy
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        rejnp__czhb = 0
        for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(arr)):
            umexz__lop = 0
            if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi):
                umexz__lop = 1
            rejnp__czhb += umexz__lop
        ptaru__xww = rejnp__czhb
        return ptaru__xww
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    ckc__lzkit = array_op_count(arr)
    wjq__phtai = array_op_min(arr)
    rljz__tmzbs = array_op_max(arr)
    kyp__ifwuj = array_op_mean(arr)
    raegj__kds = array_op_std(arr)
    wke__lkdny = array_op_quantile(arr, 0.25)
    emr__xnzs = array_op_quantile(arr, 0.5)
    nuyjy__qkur = array_op_quantile(arr, 0.75)
    return (ckc__lzkit, kyp__ifwuj, raegj__kds, wjq__phtai, wke__lkdny,
        emr__xnzs, nuyjy__qkur, rljz__tmzbs)


def array_op_describe_dt_impl(arr):
    ckc__lzkit = array_op_count(arr)
    wjq__phtai = array_op_min(arr)
    rljz__tmzbs = array_op_max(arr)
    kyp__ifwuj = array_op_mean(arr)
    wke__lkdny = array_op_quantile(arr, 0.25)
    emr__xnzs = array_op_quantile(arr, 0.5)
    nuyjy__qkur = array_op_quantile(arr, 0.75)
    return (ckc__lzkit, kyp__ifwuj, wjq__phtai, wke__lkdny, emr__xnzs,
        nuyjy__qkur, rljz__tmzbs)


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
            mnta__bfk = numba.cpython.builtins.get_type_max_value(np.int64)
            rejnp__czhb = 0
            for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(arr)):
                rrdc__licy = mnta__bfk
                umexz__lop = 0
                if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi):
                    rrdc__licy = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[csxz__bjqdi]))
                    umexz__lop = 1
                mnta__bfk = min(mnta__bfk, rrdc__licy)
                rejnp__czhb += umexz__lop
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(mnta__bfk,
                rejnp__czhb)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            mnta__bfk = numba.cpython.builtins.get_type_max_value(np.int64)
            rejnp__czhb = 0
            for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(arr)):
                rrdc__licy = mnta__bfk
                umexz__lop = 0
                if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi):
                    rrdc__licy = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[csxz__bjqdi]))
                    umexz__lop = 1
                mnta__bfk = min(mnta__bfk, rrdc__licy)
                rejnp__czhb += umexz__lop
            return bodo.hiframes.pd_index_ext._dti_val_finalize(mnta__bfk,
                rejnp__czhb)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            stgtq__bgq = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            mnta__bfk = numba.cpython.builtins.get_type_max_value(np.int64)
            rejnp__czhb = 0
            for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(
                stgtq__bgq)):
                fcl__yegps = stgtq__bgq[csxz__bjqdi]
                if fcl__yegps == -1:
                    continue
                mnta__bfk = min(mnta__bfk, fcl__yegps)
                rejnp__czhb += 1
            ptaru__xww = bodo.hiframes.series_kernels._box_cat_val(mnta__bfk,
                arr.dtype, rejnp__czhb)
            return ptaru__xww
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            mnta__bfk = bodo.hiframes.series_kernels._get_date_max_value()
            rejnp__czhb = 0
            for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(arr)):
                rrdc__licy = mnta__bfk
                umexz__lop = 0
                if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi):
                    rrdc__licy = arr[csxz__bjqdi]
                    umexz__lop = 1
                mnta__bfk = min(mnta__bfk, rrdc__licy)
                rejnp__czhb += umexz__lop
            ptaru__xww = bodo.hiframes.series_kernels._sum_handle_nan(mnta__bfk
                , rejnp__czhb)
            return ptaru__xww
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        mnta__bfk = bodo.hiframes.series_kernels._get_type_max_value(arr.dtype)
        rejnp__czhb = 0
        for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(arr)):
            rrdc__licy = mnta__bfk
            umexz__lop = 0
            if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi):
                rrdc__licy = arr[csxz__bjqdi]
                umexz__lop = 1
            mnta__bfk = min(mnta__bfk, rrdc__licy)
            rejnp__czhb += umexz__lop
        ptaru__xww = bodo.hiframes.series_kernels._sum_handle_nan(mnta__bfk,
            rejnp__czhb)
        return ptaru__xww
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            mnta__bfk = numba.cpython.builtins.get_type_min_value(np.int64)
            rejnp__czhb = 0
            for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(arr)):
                rrdc__licy = mnta__bfk
                umexz__lop = 0
                if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi):
                    rrdc__licy = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[csxz__bjqdi]))
                    umexz__lop = 1
                mnta__bfk = max(mnta__bfk, rrdc__licy)
                rejnp__czhb += umexz__lop
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(mnta__bfk,
                rejnp__czhb)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            mnta__bfk = numba.cpython.builtins.get_type_min_value(np.int64)
            rejnp__czhb = 0
            for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(arr)):
                rrdc__licy = mnta__bfk
                umexz__lop = 0
                if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi):
                    rrdc__licy = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[csxz__bjqdi]))
                    umexz__lop = 1
                mnta__bfk = max(mnta__bfk, rrdc__licy)
                rejnp__czhb += umexz__lop
            return bodo.hiframes.pd_index_ext._dti_val_finalize(mnta__bfk,
                rejnp__czhb)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            stgtq__bgq = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            mnta__bfk = -1
            for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(
                stgtq__bgq)):
                mnta__bfk = max(mnta__bfk, stgtq__bgq[csxz__bjqdi])
            ptaru__xww = bodo.hiframes.series_kernels._box_cat_val(mnta__bfk,
                arr.dtype, 1)
            return ptaru__xww
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            mnta__bfk = bodo.hiframes.series_kernels._get_date_min_value()
            rejnp__czhb = 0
            for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(arr)):
                rrdc__licy = mnta__bfk
                umexz__lop = 0
                if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi):
                    rrdc__licy = arr[csxz__bjqdi]
                    umexz__lop = 1
                mnta__bfk = max(mnta__bfk, rrdc__licy)
                rejnp__czhb += umexz__lop
            ptaru__xww = bodo.hiframes.series_kernels._sum_handle_nan(mnta__bfk
                , rejnp__czhb)
            return ptaru__xww
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        mnta__bfk = bodo.hiframes.series_kernels._get_type_min_value(arr.dtype)
        rejnp__czhb = 0
        for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(arr)):
            rrdc__licy = mnta__bfk
            umexz__lop = 0
            if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi):
                rrdc__licy = arr[csxz__bjqdi]
                umexz__lop = 1
            mnta__bfk = max(mnta__bfk, rrdc__licy)
            rejnp__czhb += umexz__lop
        ptaru__xww = bodo.hiframes.series_kernels._sum_handle_nan(mnta__bfk,
            rejnp__czhb)
        return ptaru__xww
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
    fardm__fsbr = types.float64
    xqf__yok = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        fardm__fsbr = types.float32
        xqf__yok = types.float32
    pjcqn__cffkd = fardm__fsbr(0)
    qiv__ofawj = xqf__yok(0)
    wvh__vmtj = xqf__yok(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        mnta__bfk = pjcqn__cffkd
        rejnp__czhb = qiv__ofawj
        for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(arr)):
            rrdc__licy = pjcqn__cffkd
            umexz__lop = qiv__ofawj
            if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi):
                rrdc__licy = arr[csxz__bjqdi]
                umexz__lop = wvh__vmtj
            mnta__bfk += rrdc__licy
            rejnp__czhb += umexz__lop
        ptaru__xww = bodo.hiframes.series_kernels._mean_handle_nan(mnta__bfk,
            rejnp__czhb)
        return ptaru__xww
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        ell__kilad = 0.0
        izml__qbgip = 0.0
        rejnp__czhb = 0
        for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(arr)):
            rrdc__licy = 0.0
            umexz__lop = 0
            if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi
                ) or not skipna:
                rrdc__licy = arr[csxz__bjqdi]
                umexz__lop = 1
            ell__kilad += rrdc__licy
            izml__qbgip += rrdc__licy * rrdc__licy
            rejnp__czhb += umexz__lop
        mnta__bfk = izml__qbgip - ell__kilad * ell__kilad / rejnp__czhb
        ptaru__xww = bodo.hiframes.series_kernels._handle_nan_count_ddof(
            mnta__bfk, rejnp__czhb, ddof)
        return ptaru__xww
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
                ulid__crchy = np.empty(len(q), np.int64)
                for csxz__bjqdi in range(len(q)):
                    emsd__hgm = np.float64(q[csxz__bjqdi])
                    ulid__crchy[csxz__bjqdi
                        ] = bodo.libs.array_kernels.quantile(arr.view(np.
                        int64), emsd__hgm)
                return ulid__crchy.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            ulid__crchy = np.empty(len(q), np.float64)
            for csxz__bjqdi in range(len(q)):
                emsd__hgm = np.float64(q[csxz__bjqdi])
                ulid__crchy[csxz__bjqdi] = bodo.libs.array_kernels.quantile(arr
                    , emsd__hgm)
            return ulid__crchy
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
        rplfj__btdy = types.intp
    elif arr.dtype == types.bool_:
        rplfj__btdy = np.int64
    else:
        rplfj__btdy = arr.dtype
    gtfzq__yrzb = rplfj__btdy(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            mnta__bfk = gtfzq__yrzb
            ngrr__oma = len(arr)
            rejnp__czhb = 0
            for csxz__bjqdi in numba.parfors.parfor.internal_prange(ngrr__oma):
                rrdc__licy = gtfzq__yrzb
                umexz__lop = 0
                if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi
                    ) or not skipna:
                    rrdc__licy = arr[csxz__bjqdi]
                    umexz__lop = 1
                mnta__bfk += rrdc__licy
                rejnp__czhb += umexz__lop
            ptaru__xww = bodo.hiframes.series_kernels._var_handle_mincount(
                mnta__bfk, rejnp__czhb, min_count)
            return ptaru__xww
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            mnta__bfk = gtfzq__yrzb
            ngrr__oma = len(arr)
            for csxz__bjqdi in numba.parfors.parfor.internal_prange(ngrr__oma):
                rrdc__licy = gtfzq__yrzb
                if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi):
                    rrdc__licy = arr[csxz__bjqdi]
                mnta__bfk += rrdc__licy
            return mnta__bfk
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    usov__ostv = arr.dtype(1)
    if arr.dtype == types.bool_:
        usov__ostv = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            mnta__bfk = usov__ostv
            rejnp__czhb = 0
            for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(arr)):
                rrdc__licy = usov__ostv
                umexz__lop = 0
                if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi
                    ) or not skipna:
                    rrdc__licy = arr[csxz__bjqdi]
                    umexz__lop = 1
                rejnp__czhb += umexz__lop
                mnta__bfk *= rrdc__licy
            ptaru__xww = bodo.hiframes.series_kernels._var_handle_mincount(
                mnta__bfk, rejnp__czhb, min_count)
            return ptaru__xww
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            mnta__bfk = usov__ostv
            for csxz__bjqdi in numba.parfors.parfor.internal_prange(len(arr)):
                rrdc__licy = usov__ostv
                if not bodo.libs.array_kernels.isna(arr, csxz__bjqdi):
                    rrdc__licy = arr[csxz__bjqdi]
                mnta__bfk *= rrdc__licy
            return mnta__bfk
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        csxz__bjqdi = bodo.libs.array_kernels._nan_argmax(arr)
        return index[csxz__bjqdi]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        csxz__bjqdi = bodo.libs.array_kernels._nan_argmin(arr)
        return index[csxz__bjqdi]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            ajlv__tpg = {}
            for nuigy__urx in values:
                ajlv__tpg[bodo.utils.conversion.box_if_dt64(nuigy__urx)] = 0
            return ajlv__tpg
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
        ngrr__oma = len(arr)
        ulid__crchy = np.empty(ngrr__oma, np.bool_)
        for csxz__bjqdi in numba.parfors.parfor.internal_prange(ngrr__oma):
            ulid__crchy[csxz__bjqdi] = bodo.utils.conversion.box_if_dt64(arr
                [csxz__bjqdi]) in values
        return ulid__crchy
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr):
    jiah__pamjm = 'def impl(in_arr):\n'
    jiah__pamjm += '  n = len(in_arr)\n'
    jiah__pamjm += '  arr_map = {in_arr[0]: 0 for _ in range(0)}\n'
    jiah__pamjm += '  in_lst = []\n'
    jiah__pamjm += '  map_vector = np.empty(n, np.int64)\n'
    jiah__pamjm += '  is_na = 0\n'
    if in_arr == bodo.string_array_type:
        jiah__pamjm += '  total_len = 0\n'
    jiah__pamjm += '  for i in range(n):\n'
    jiah__pamjm += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
    jiah__pamjm += '      is_na = 1\n'
    jiah__pamjm += (
        '      # Always put NA in the last location. We can safely use\n')
    jiah__pamjm += '      # -1 because in_arr[-1] == in_arr[len(in_arr) - 1]\n'
    jiah__pamjm += '      set_val = -1\n'
    jiah__pamjm += '    else:\n'
    jiah__pamjm += '      data_val = in_arr[i]\n'
    jiah__pamjm += '      if data_val not in arr_map:\n'
    jiah__pamjm += '        set_val = len(arr_map)\n'
    jiah__pamjm += '        # Add the data to index info\n'
    jiah__pamjm += '        in_lst.append(data_val)\n'
    jiah__pamjm += '        arr_map[data_val] = len(arr_map)\n'
    if in_arr == bodo.string_array_type:
        jiah__pamjm += '        total_len += len(data_val)\n'
    jiah__pamjm += '      else:\n'
    jiah__pamjm += '        set_val = arr_map[data_val]\n'
    jiah__pamjm += '    map_vector[i] = set_val\n'
    jiah__pamjm += '  n_rows = len(arr_map) + is_na\n'
    if in_arr == bodo.string_array_type:
        jiah__pamjm += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
    else:
        jiah__pamjm += (
            '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n')
    jiah__pamjm += '  for j in range(len(arr_map)):\n'
    jiah__pamjm += '    out_arr[j] = in_lst[j]\n'
    jiah__pamjm += '  if is_na:\n'
    jiah__pamjm += '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n'
    jiah__pamjm += '  return out_arr, map_vector\n'
    jsu__rcf = {}
    exec(jiah__pamjm, {'bodo': bodo, 'np': np}, jsu__rcf)
    impl = jsu__rcf['impl']
    return impl
