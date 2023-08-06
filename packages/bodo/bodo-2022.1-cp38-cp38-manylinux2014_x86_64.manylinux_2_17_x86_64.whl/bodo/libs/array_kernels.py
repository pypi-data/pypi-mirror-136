"""
Implements array kernels such as median and quantile.
"""
import hashlib
import inspect
import math
import operator
import re
import warnings
from math import sqrt
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types, typing
from numba.core.imputils import lower_builtin
from numba.core.ir_utils import find_const, guard
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload, overload_attribute, register_jitable
from numba.np.arrayobj import make_array
from numba.np.numpy_support import as_dtype
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, init_categorical_array
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs import quantile_alg
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, drop_duplicates_table, info_from_table, info_to_array, sample_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, offset_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import str_arr_set_na, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.shuffle import getitem_arr_tup_single
from bodo.utils.typing import BodoError, check_unsupported_args, element_type, find_common_np_dtype, get_overload_const_bool, get_overload_const_list, get_overload_const_str, is_overload_none, raise_bodo_error
from bodo.utils.utils import build_set_seen_na, check_and_propagate_cpp_exception, numba_to_c_type, unliteral_all
ll.add_symbol('quantile_sequential', quantile_alg.quantile_sequential)
ll.add_symbol('quantile_parallel', quantile_alg.quantile_parallel)
MPI_ROOT = 0
sum_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value)


def isna(arr, i):
    return False


@overload(isna)
def overload_isna(arr, i):
    i = types.unliteral(i)
    if arr == string_array_type:
        return lambda arr, i: bodo.libs.str_arr_ext.str_arr_is_na(arr, i)
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type,
        datetime_timedelta_array_type, string_array_split_view_type):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
            ._null_bitmap, i)
    if isinstance(arr, ArrayItemArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, StructArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.struct_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, TupleArrayType):
        return lambda arr, i: bodo.libs.array_kernels.isna(arr._data, i)
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return lambda arr, i: arr.codes[i] == -1
    if arr == bodo.binary_array_type:
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr._data), i)
    if isinstance(arr, types.List):
        if arr.dtype == types.none:
            return lambda arr, i: True
        elif isinstance(arr.dtype, types.optional):
            return lambda arr, i: arr[i] is None
        else:
            return lambda arr, i: False
    if isinstance(arr, bodo.NullableTupleType):
        return lambda arr, i: arr._null_values[i]
    assert isinstance(arr, types.Array)
    dtype = arr.dtype
    if isinstance(dtype, types.Float):
        return lambda arr, i: np.isnan(arr[i])
    if isinstance(dtype, (types.NPDatetime, types.NPTimedelta)):
        return lambda arr, i: np.isnat(arr[i])
    return lambda arr, i: False


def setna(arr, ind, int_nan_const=0):
    arr[ind] = np.nan


@overload(setna, no_unliteral=True)
def setna_overload(arr, ind, int_nan_const=0):
    if isinstance(arr.dtype, types.Float):
        return setna
    if isinstance(arr.dtype, (types.NPDatetime, types.NPTimedelta)):
        rquqz__hnjr = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = rquqz__hnjr
        return _setnan_impl
    if arr == string_array_type:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = ''
            str_arr_set_na(arr, ind)
        return impl
    if arr == boolean_array:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = False
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)):
        return (lambda arr, ind, int_nan_const=0: bodo.libs.int_arr_ext.
            set_bit_to_arr(arr._null_bitmap, ind, 0))
    if arr == bodo.binary_array_type:

        def impl_binary_arr(arr, ind, int_nan_const=0):
            hbbj__nrvy = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            hbbj__nrvy[ind + 1] = hbbj__nrvy[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            hbbj__nrvy = bodo.libs.array_item_arr_ext.get_offsets(arr)
            hbbj__nrvy[ind + 1] = hbbj__nrvy[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr), ind, 0)
        return impl_arr_item
    if isinstance(arr, bodo.libs.struct_arr_ext.StructArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.struct_arr_ext.
                get_null_bitmap(arr), ind, 0)
            data = bodo.libs.struct_arr_ext.get_data(arr)
            setna_tup(data, ind)
        return impl
    if isinstance(arr, TupleArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._data, ind)
        return impl
    if arr.dtype == types.bool_:

        def b_set(arr, ind, int_nan_const=0):
            arr[ind] = False
        return b_set
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):

        def setna_cat(arr, ind, int_nan_const=0):
            arr.codes[ind] = -1
        return setna_cat
    if isinstance(arr.dtype, types.Integer):

        def setna_int(arr, ind, int_nan_const=0):
            arr[ind] = int_nan_const
        return setna_int
    if arr == datetime_date_array_type:

        def setna_datetime_date(arr, ind, int_nan_const=0):
            arr._data[ind] = (1970 << 32) + (1 << 16) + 1
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_date
    if arr == datetime_timedelta_array_type:

        def setna_datetime_timedelta(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._days_data, ind)
            bodo.libs.array_kernels.setna(arr._seconds_data, ind)
            bodo.libs.array_kernels.setna(arr._microseconds_data, ind)
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_timedelta
    return lambda arr, ind, int_nan_const=0: None


def setna_tup(arr_tup, ind, int_nan_const=0):
    for arr in arr_tup:
        arr[ind] = np.nan


@overload(setna_tup, no_unliteral=True)
def overload_setna_tup(arr_tup, ind, int_nan_const=0):
    xwa__kvii = arr_tup.count
    tsykj__jokvb = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(xwa__kvii):
        tsykj__jokvb += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    tsykj__jokvb += '  return\n'
    zysz__utu = {}
    exec(tsykj__jokvb, {'setna': setna}, zysz__utu)
    impl = zysz__utu['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        rjf__zygm = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(rjf__zygm.start, rjf__zygm.stop, rjf__zygm.step):
            setna(arr, i)
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    oft__hnp = array_to_info(arr)
    _median_series_computation(res, oft__hnp, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(oft__hnp)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    oft__hnp = array_to_info(arr)
    _autocorr_series_computation(res, oft__hnp, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(oft__hnp)


@numba.njit
def autocorr(arr, lag=1, parallel=False):
    res = np.empty(1, types.float64)
    autocorr_series_computation(res.ctypes, arr, lag, parallel)
    return res[0]


ll.add_symbol('compute_series_monotonicity', quantile_alg.
    compute_series_monotonicity)
_compute_series_monotonicity = types.ExternalFunction(
    'compute_series_monotonicity', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def series_monotonicity_call(res, arr, inc_dec, is_parallel):
    oft__hnp = array_to_info(arr)
    _compute_series_monotonicity(res, oft__hnp, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(oft__hnp)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    zmzw__ahiis = res[0] > 0.5
    return zmzw__ahiis


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        rjk__tnx = '-'
        efal__iia = 'index_arr[0] > threshhold_date'
        binvc__fiigm = '1, n+1'
        bdcez__efd = 'index_arr[-i] <= threshhold_date'
        zkthf__wdbtk = 'i - 1'
    else:
        rjk__tnx = '+'
        efal__iia = 'index_arr[-1] < threshhold_date'
        binvc__fiigm = 'n'
        bdcez__efd = 'index_arr[i] >= threshhold_date'
        zkthf__wdbtk = 'i'
    tsykj__jokvb = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        tsykj__jokvb += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        tsykj__jokvb += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            tsykj__jokvb += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            tsykj__jokvb += """      threshhold_date = initial_date - date_offset.base + date_offset
"""
            tsykj__jokvb += '    else:\n'
            tsykj__jokvb += (
                '      threshhold_date = initial_date + date_offset\n')
        else:
            tsykj__jokvb += (
                f'    threshhold_date = initial_date {rjk__tnx} date_offset\n')
    else:
        tsykj__jokvb += f'  threshhold_date = initial_date {rjk__tnx} offset\n'
    tsykj__jokvb += '  local_valid = 0\n'
    tsykj__jokvb += f'  n = len(index_arr)\n'
    tsykj__jokvb += f'  if n:\n'
    tsykj__jokvb += f'    if {efal__iia}:\n'
    tsykj__jokvb += '      loc_valid = n\n'
    tsykj__jokvb += '    else:\n'
    tsykj__jokvb += f'      for i in range({binvc__fiigm}):\n'
    tsykj__jokvb += f'        if {bdcez__efd}:\n'
    tsykj__jokvb += f'          loc_valid = {zkthf__wdbtk}\n'
    tsykj__jokvb += '          break\n'
    tsykj__jokvb += '  if is_parallel:\n'
    tsykj__jokvb += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    tsykj__jokvb += '    return total_valid\n'
    tsykj__jokvb += '  else:\n'
    tsykj__jokvb += '    return loc_valid\n'
    zysz__utu = {}
    exec(tsykj__jokvb, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, zysz__utu)
    return zysz__utu['impl']


def quantile(A, q):
    return 0


def quantile_parallel(A, q):
    return 0


@infer_global(quantile)
@infer_global(quantile_parallel)
class QuantileType(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) in [2, 3]
        return signature(types.float64, *unliteral_all(args))


@lower_builtin(quantile, types.Array, types.float64)
@lower_builtin(quantile, IntegerArrayType, types.float64)
@lower_builtin(quantile, BooleanArrayType, types.float64)
def lower_dist_quantile_seq(context, builder, sig, args):
    wplkf__gohs = numba_to_c_type(sig.args[0].dtype)
    hhngx__owa = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), wplkf__gohs))
    rgks__xumqz = args[0]
    trc__lpoi = sig.args[0]
    if isinstance(trc__lpoi, (IntegerArrayType, BooleanArrayType)):
        rgks__xumqz = cgutils.create_struct_proxy(trc__lpoi)(context,
            builder, rgks__xumqz).data
        trc__lpoi = types.Array(trc__lpoi.dtype, 1, 'C')
    assert trc__lpoi.ndim == 1
    arr = make_array(trc__lpoi)(context, builder, rgks__xumqz)
    jyzkv__jeb = builder.extract_value(arr.shape, 0)
    qlqai__jpzq = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        jyzkv__jeb, args[1], builder.load(hhngx__owa)]
    ytiau__dwdf = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    why__xsg = lir.FunctionType(lir.DoubleType(), ytiau__dwdf)
    jhpg__wrn = cgutils.get_or_insert_function(builder.module, why__xsg,
        name='quantile_sequential')
    dtv__ogmqm = builder.call(jhpg__wrn, qlqai__jpzq)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return dtv__ogmqm


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    wplkf__gohs = numba_to_c_type(sig.args[0].dtype)
    hhngx__owa = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), wplkf__gohs))
    rgks__xumqz = args[0]
    trc__lpoi = sig.args[0]
    if isinstance(trc__lpoi, (IntegerArrayType, BooleanArrayType)):
        rgks__xumqz = cgutils.create_struct_proxy(trc__lpoi)(context,
            builder, rgks__xumqz).data
        trc__lpoi = types.Array(trc__lpoi.dtype, 1, 'C')
    assert trc__lpoi.ndim == 1
    arr = make_array(trc__lpoi)(context, builder, rgks__xumqz)
    jyzkv__jeb = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        znds__hxkc = args[2]
    else:
        znds__hxkc = jyzkv__jeb
    qlqai__jpzq = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        jyzkv__jeb, znds__hxkc, args[1], builder.load(hhngx__owa)]
    ytiau__dwdf = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        IntType(64), lir.DoubleType(), lir.IntType(32)]
    why__xsg = lir.FunctionType(lir.DoubleType(), ytiau__dwdf)
    jhpg__wrn = cgutils.get_or_insert_function(builder.module, why__xsg,
        name='quantile_parallel')
    dtv__ogmqm = builder.call(jhpg__wrn, qlqai__jpzq)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return dtv__ogmqm


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    dbg__fgezu = start
    jnlw__qls = 2 * start + 1
    lncf__lkcxe = 2 * start + 2
    if jnlw__qls < n and not cmp_f(arr[jnlw__qls], arr[dbg__fgezu]):
        dbg__fgezu = jnlw__qls
    if lncf__lkcxe < n and not cmp_f(arr[lncf__lkcxe], arr[dbg__fgezu]):
        dbg__fgezu = lncf__lkcxe
    if dbg__fgezu != start:
        arr[start], arr[dbg__fgezu] = arr[dbg__fgezu], arr[start]
        ind_arr[start], ind_arr[dbg__fgezu] = ind_arr[dbg__fgezu], ind_arr[
            start]
        min_heapify(arr, ind_arr, n, dbg__fgezu, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        vuha__meb = np.empty(k, A.dtype)
        yrcmt__uvx = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                vuha__meb[ind] = A[i]
                yrcmt__uvx[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            vuha__meb = vuha__meb[:ind]
            yrcmt__uvx = yrcmt__uvx[:ind]
        return vuha__meb, yrcmt__uvx, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        upo__daqhl = np.sort(A)
        eabym__akmit = index_arr[np.argsort(A)]
        xjj__tfq = pd.Series(upo__daqhl).notna().values
        upo__daqhl = upo__daqhl[xjj__tfq]
        eabym__akmit = eabym__akmit[xjj__tfq]
        if is_largest:
            upo__daqhl = upo__daqhl[::-1]
            eabym__akmit = eabym__akmit[::-1]
        return np.ascontiguousarray(upo__daqhl), np.ascontiguousarray(
            eabym__akmit)
    vuha__meb, yrcmt__uvx, start = select_k_nonan(A, index_arr, m, k)
    yrcmt__uvx = yrcmt__uvx[vuha__meb.argsort()]
    vuha__meb.sort()
    if not is_largest:
        vuha__meb = np.ascontiguousarray(vuha__meb[::-1])
        yrcmt__uvx = np.ascontiguousarray(yrcmt__uvx[::-1])
    for i in range(start, m):
        if cmp_f(A[i], vuha__meb[0]):
            vuha__meb[0] = A[i]
            yrcmt__uvx[0] = index_arr[i]
            min_heapify(vuha__meb, yrcmt__uvx, k, 0, cmp_f)
    yrcmt__uvx = yrcmt__uvx[vuha__meb.argsort()]
    vuha__meb.sort()
    if is_largest:
        vuha__meb = vuha__meb[::-1]
        yrcmt__uvx = yrcmt__uvx[::-1]
    return np.ascontiguousarray(vuha__meb), np.ascontiguousarray(yrcmt__uvx)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    ivur__kctl = bodo.libs.distributed_api.get_rank()
    pxqyc__bjkx, vhwg__wgv = nlargest(A, I, k, is_largest, cmp_f)
    jwb__nuqy = bodo.libs.distributed_api.gatherv(pxqyc__bjkx)
    lcgo__ume = bodo.libs.distributed_api.gatherv(vhwg__wgv)
    if ivur__kctl == MPI_ROOT:
        res, wjdb__raa = nlargest(jwb__nuqy, lcgo__ume, k, is_largest, cmp_f)
    else:
        res = np.empty(k, A.dtype)
        wjdb__raa = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(wjdb__raa)
    return res, wjdb__raa


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    ski__pmy, koarm__wuhyg = mat.shape
    bfij__utvu = np.empty((koarm__wuhyg, koarm__wuhyg), dtype=np.float64)
    for lutol__ljwq in range(koarm__wuhyg):
        for awmzl__qyuci in range(lutol__ljwq + 1):
            toz__uku = 0
            keq__ydbz = ndqey__rqr = ybh__acdbv = wkpqg__ynxui = 0.0
            for i in range(ski__pmy):
                if np.isfinite(mat[i, lutol__ljwq]) and np.isfinite(mat[i,
                    awmzl__qyuci]):
                    kjyk__ugfcf = mat[i, lutol__ljwq]
                    ianm__zyw = mat[i, awmzl__qyuci]
                    toz__uku += 1
                    ybh__acdbv += kjyk__ugfcf
                    wkpqg__ynxui += ianm__zyw
            if parallel:
                toz__uku = bodo.libs.distributed_api.dist_reduce(toz__uku,
                    sum_op)
                ybh__acdbv = bodo.libs.distributed_api.dist_reduce(ybh__acdbv,
                    sum_op)
                wkpqg__ynxui = bodo.libs.distributed_api.dist_reduce(
                    wkpqg__ynxui, sum_op)
            if toz__uku < minpv:
                bfij__utvu[lutol__ljwq, awmzl__qyuci] = bfij__utvu[
                    awmzl__qyuci, lutol__ljwq] = np.nan
            else:
                dvh__ijnue = ybh__acdbv / toz__uku
                ptk__yaiw = wkpqg__ynxui / toz__uku
                ybh__acdbv = 0.0
                for i in range(ski__pmy):
                    if np.isfinite(mat[i, lutol__ljwq]) and np.isfinite(mat
                        [i, awmzl__qyuci]):
                        kjyk__ugfcf = mat[i, lutol__ljwq] - dvh__ijnue
                        ianm__zyw = mat[i, awmzl__qyuci] - ptk__yaiw
                        ybh__acdbv += kjyk__ugfcf * ianm__zyw
                        keq__ydbz += kjyk__ugfcf * kjyk__ugfcf
                        ndqey__rqr += ianm__zyw * ianm__zyw
                if parallel:
                    ybh__acdbv = bodo.libs.distributed_api.dist_reduce(
                        ybh__acdbv, sum_op)
                    keq__ydbz = bodo.libs.distributed_api.dist_reduce(keq__ydbz
                        , sum_op)
                    ndqey__rqr = bodo.libs.distributed_api.dist_reduce(
                        ndqey__rqr, sum_op)
                myubn__unw = toz__uku - 1.0 if cov else sqrt(keq__ydbz *
                    ndqey__rqr)
                if myubn__unw != 0.0:
                    bfij__utvu[lutol__ljwq, awmzl__qyuci] = bfij__utvu[
                        awmzl__qyuci, lutol__ljwq] = ybh__acdbv / myubn__unw
                else:
                    bfij__utvu[lutol__ljwq, awmzl__qyuci] = bfij__utvu[
                        awmzl__qyuci, lutol__ljwq] = np.nan
    return bfij__utvu


@numba.njit(no_cpython_wrapper=True)
def duplicated(data, ind_arr, parallel=False):
    if parallel:
        data, (ind_arr,) = bodo.ir.join.parallel_shuffle(data, (ind_arr,))
    data = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data)
    n = len(data[0])
    out = np.empty(n, np.bool_)
    ytbex__xhz = dict()
    for i in range(n):
        val = getitem_arr_tup_single(data, i)
        if val in ytbex__xhz:
            out[i] = True
        else:
            out[i] = False
            ytbex__xhz[val] = 0
    return out, ind_arr


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    xwa__kvii = len(data)
    tsykj__jokvb = (
        'def impl(data, ind_arr, n, frac, replace, parallel=False):\n')
    tsykj__jokvb += ('  info_list_total = [{}, array_to_info(ind_arr)]\n'.
        format(', '.join('array_to_info(data[{}])'.format(x) for x in range
        (xwa__kvii))))
    tsykj__jokvb += '  table_total = arr_info_list_to_table(info_list_total)\n'
    tsykj__jokvb += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(xwa__kvii))
    for lcxmg__ukk in range(xwa__kvii):
        tsykj__jokvb += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(lcxmg__ukk, lcxmg__ukk, lcxmg__ukk))
    tsykj__jokvb += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(xwa__kvii))
    tsykj__jokvb += '  delete_table(out_table)\n'
    tsykj__jokvb += '  delete_table(table_total)\n'
    tsykj__jokvb += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(xwa__kvii)))
    zysz__utu = {}
    exec(tsykj__jokvb, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'sample_table': sample_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, zysz__utu)
    impl = zysz__utu['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    xwa__kvii = len(data)
    tsykj__jokvb = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    tsykj__jokvb += ('  info_list_total = [{}, array_to_info(ind_arr)]\n'.
        format(', '.join('array_to_info(data[{}])'.format(x) for x in range
        (xwa__kvii))))
    tsykj__jokvb += '  table_total = arr_info_list_to_table(info_list_total)\n'
    tsykj__jokvb += '  keep_i = 0\n'
    tsykj__jokvb += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False)
"""
    for lcxmg__ukk in range(xwa__kvii):
        tsykj__jokvb += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(lcxmg__ukk, lcxmg__ukk, lcxmg__ukk))
    tsykj__jokvb += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(xwa__kvii))
    tsykj__jokvb += '  delete_table(out_table)\n'
    tsykj__jokvb += '  delete_table(table_total)\n'
    tsykj__jokvb += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(xwa__kvii)))
    zysz__utu = {}
    exec(tsykj__jokvb, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, zysz__utu)
    impl = zysz__utu['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        epgn__zyd = [array_to_info(data_arr)]
        pwk__spnex = arr_info_list_to_table(epgn__zyd)
        hxm__xgojp = 0
        imcx__bdbn = drop_duplicates_table(pwk__spnex, parallel, 1,
            hxm__xgojp, False)
        hru__rus = info_to_array(info_from_table(imcx__bdbn, 0), data_arr)
        delete_table(imcx__bdbn)
        delete_table(pwk__spnex)
        return hru__rus
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    zwmsx__lsfwo = len(data.types)
    qwgsc__cfi = [('out' + str(i)) for i in range(zwmsx__lsfwo)]
    pghl__yht = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    gstx__ukz = ['isna(data[{}], i)'.format(i) for i in pghl__yht]
    osu__qolql = 'not ({})'.format(' or '.join(gstx__ukz))
    if not is_overload_none(thresh):
        osu__qolql = '(({}) <= ({}) - thresh)'.format(' + '.join(gstx__ukz),
            zwmsx__lsfwo - 1)
    elif how == 'all':
        osu__qolql = 'not ({})'.format(' and '.join(gstx__ukz))
    tsykj__jokvb = 'def _dropna_imp(data, how, thresh, subset):\n'
    tsykj__jokvb += '  old_len = len(data[0])\n'
    tsykj__jokvb += '  new_len = 0\n'
    tsykj__jokvb += '  for i in range(old_len):\n'
    tsykj__jokvb += '    if {}:\n'.format(osu__qolql)
    tsykj__jokvb += '      new_len += 1\n'
    for i, out in enumerate(qwgsc__cfi):
        if isinstance(data[i], bodo.CategoricalArrayType):
            tsykj__jokvb += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            tsykj__jokvb += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    tsykj__jokvb += '  curr_ind = 0\n'
    tsykj__jokvb += '  for i in range(old_len):\n'
    tsykj__jokvb += '    if {}:\n'.format(osu__qolql)
    for i in range(zwmsx__lsfwo):
        tsykj__jokvb += '      if isna(data[{}], i):\n'.format(i)
        tsykj__jokvb += '        setna({}, curr_ind)\n'.format(qwgsc__cfi[i])
        tsykj__jokvb += '      else:\n'
        tsykj__jokvb += '        {}[curr_ind] = data[{}][i]\n'.format(
            qwgsc__cfi[i], i)
    tsykj__jokvb += '      curr_ind += 1\n'
    tsykj__jokvb += '  return {}\n'.format(', '.join(qwgsc__cfi))
    zysz__utu = {}
    sstb__zpgi = {'t{}'.format(i): cenj__cjjp for i, cenj__cjjp in
        enumerate(data.types)}
    sstb__zpgi.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(tsykj__jokvb, sstb__zpgi, zysz__utu)
    bcqf__aimmb = zysz__utu['_dropna_imp']
    return bcqf__aimmb


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        trc__lpoi = arr.dtype
        ulgh__ncxy = trc__lpoi.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            heuk__rkjj = init_nested_counts(ulgh__ncxy)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                heuk__rkjj = add_nested_counts(heuk__rkjj, val[ind])
            hru__rus = bodo.utils.utils.alloc_type(n, trc__lpoi, heuk__rkjj)
            for cbdls__fzw in range(n):
                if bodo.libs.array_kernels.isna(arr, cbdls__fzw):
                    setna(hru__rus, cbdls__fzw)
                    continue
                val = arr[cbdls__fzw]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(hru__rus, cbdls__fzw)
                    continue
                hru__rus[cbdls__fzw] = val[ind]
            return hru__rus
        return get_arr_item


def concat(arr_list):
    return pd.concat(arr_list)


@overload(concat, no_unliteral=True)
def concat_overload(arr_list):
    if isinstance(arr_list, bodo.NullableTupleType):
        return lambda arr_list: bodo.libs.array_kernels.concat(arr_list._data)
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, ArrayItemArrayType):
        ohry__cwy = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            sbp__nnf = 0
            amw__ujzin = []
            for A in arr_list:
                wqkuo__ymkf = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                amw__ujzin.append(bodo.libs.array_item_arr_ext.get_data(A))
                sbp__nnf += wqkuo__ymkf
            ljno__dteu = np.empty(sbp__nnf + 1, offset_type)
            mqz__cbra = bodo.libs.array_kernels.concat(amw__ujzin)
            pdmw__vns = np.empty(sbp__nnf + 7 >> 3, np.uint8)
            zebp__ebrro = 0
            xunjq__unoi = 0
            for A in arr_list:
                iwu__bjg = bodo.libs.array_item_arr_ext.get_offsets(A)
                emn__otiq = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                wqkuo__ymkf = len(A)
                pvaja__zlo = iwu__bjg[wqkuo__ymkf]
                for i in range(wqkuo__ymkf):
                    ljno__dteu[i + zebp__ebrro] = iwu__bjg[i] + xunjq__unoi
                    xra__xpa = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        emn__otiq, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(pdmw__vns, i +
                        zebp__ebrro, xra__xpa)
                zebp__ebrro += wqkuo__ymkf
                xunjq__unoi += pvaja__zlo
            ljno__dteu[zebp__ebrro] = xunjq__unoi
            hru__rus = bodo.libs.array_item_arr_ext.init_array_item_array(
                sbp__nnf, mqz__cbra, ljno__dteu, pdmw__vns)
            return hru__rus
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        ckn__toelz = arr_list.dtype.names
        tsykj__jokvb = 'def struct_array_concat_impl(arr_list):\n'
        tsykj__jokvb += f'    n_all = 0\n'
        for i in range(len(ckn__toelz)):
            tsykj__jokvb += f'    concat_list{i} = []\n'
        tsykj__jokvb += '    for A in arr_list:\n'
        tsykj__jokvb += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(ckn__toelz)):
            tsykj__jokvb += f'        concat_list{i}.append(data_tuple[{i}])\n'
        tsykj__jokvb += '        n_all += len(A)\n'
        tsykj__jokvb += '    n_bytes = (n_all + 7) >> 3\n'
        tsykj__jokvb += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        tsykj__jokvb += '    curr_bit = 0\n'
        tsykj__jokvb += '    for A in arr_list:\n'
        tsykj__jokvb += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        tsykj__jokvb += '        for j in range(len(A)):\n'
        tsykj__jokvb += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        tsykj__jokvb += """            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)
"""
        tsykj__jokvb += '            curr_bit += 1\n'
        tsykj__jokvb += (
            '    return bodo.libs.struct_arr_ext.init_struct_arr(\n')
        frcvm__qfpz = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(ckn__toelz))])
        tsykj__jokvb += f'        ({frcvm__qfpz},),\n'
        tsykj__jokvb += '        new_mask,\n'
        tsykj__jokvb += f'        {ckn__toelz},\n'
        tsykj__jokvb += '    )\n'
        zysz__utu = {}
        exec(tsykj__jokvb, {'bodo': bodo, 'np': np}, zysz__utu)
        return zysz__utu['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            jmtxa__egvlf = 0
            for A in arr_list:
                jmtxa__egvlf += len(A)
            wero__shf = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(jmtxa__egvlf))
            yoti__fljsh = 0
            for A in arr_list:
                for i in range(len(A)):
                    wero__shf._data[i + yoti__fljsh] = A._data[i]
                    xra__xpa = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(wero__shf.
                        _null_bitmap, i + yoti__fljsh, xra__xpa)
                yoti__fljsh += len(A)
            return wero__shf
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            jmtxa__egvlf = 0
            for A in arr_list:
                jmtxa__egvlf += len(A)
            wero__shf = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(jmtxa__egvlf))
            yoti__fljsh = 0
            for A in arr_list:
                for i in range(len(A)):
                    wero__shf._days_data[i + yoti__fljsh] = A._days_data[i]
                    wero__shf._seconds_data[i + yoti__fljsh] = A._seconds_data[
                        i]
                    wero__shf._microseconds_data[i + yoti__fljsh
                        ] = A._microseconds_data[i]
                    xra__xpa = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(wero__shf.
                        _null_bitmap, i + yoti__fljsh, xra__xpa)
                yoti__fljsh += len(A)
            return wero__shf
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        jrd__yipk = arr_list.dtype.precision
        wey__wryg = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            jmtxa__egvlf = 0
            for A in arr_list:
                jmtxa__egvlf += len(A)
            wero__shf = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                jmtxa__egvlf, jrd__yipk, wey__wryg)
            yoti__fljsh = 0
            for A in arr_list:
                for i in range(len(A)):
                    wero__shf._data[i + yoti__fljsh] = A._data[i]
                    xra__xpa = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(wero__shf.
                        _null_bitmap, i + yoti__fljsh, xra__xpa)
                yoti__fljsh += len(A)
            return wero__shf
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype in [string_array_type, bodo.binary_array_type]:
        if arr_list.dtype == bodo.binary_array_type:
            uboxd__elvh = 'bodo.libs.str_arr_ext.pre_alloc_binary_array'
        elif arr_list.dtype == string_array_type:
            uboxd__elvh = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        tsykj__jokvb = 'def impl(arr_list):  # pragma: no cover\n'
        tsykj__jokvb += '    # preallocate the output\n'
        tsykj__jokvb += '    num_strs = 0\n'
        tsykj__jokvb += '    num_chars = 0\n'
        tsykj__jokvb += '    for A in arr_list:\n'
        tsykj__jokvb += '        arr = A\n'
        tsykj__jokvb += '        num_strs += len(arr)\n'
        tsykj__jokvb += (
            '        # this should work for both binary and string\n')
        tsykj__jokvb += (
            '        num_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n'
            )
        tsykj__jokvb += f'    out_arr = {uboxd__elvh}(\n'
        tsykj__jokvb += '        num_strs, num_chars\n'
        tsykj__jokvb += '    )\n'
        tsykj__jokvb += (
            '    bodo.libs.str_arr_ext.set_null_bits_to_value(out_arr, -1)\n')
        tsykj__jokvb += '    # copy data to output\n'
        tsykj__jokvb += '    curr_str_ind = 0\n'
        tsykj__jokvb += '    curr_chars_ind = 0\n'
        tsykj__jokvb += '    for A in arr_list:\n'
        tsykj__jokvb += '        arr = A\n'
        tsykj__jokvb += '        # This will probably need to be extended\n'
        tsykj__jokvb += (
            '        bodo.libs.str_arr_ext.set_string_array_range(\n')
        tsykj__jokvb += (
            '            out_arr, arr, curr_str_ind, curr_chars_ind\n')
        tsykj__jokvb += '        )\n'
        tsykj__jokvb += '        curr_str_ind += len(arr)\n'
        tsykj__jokvb += (
            '        # this should work for both binary and string\n')
        tsykj__jokvb += (
            '        curr_chars_ind += bodo.libs.str_arr_ext.num_total_chars(arr)\n'
            )
        tsykj__jokvb += '    return out_arr\n'
        unsag__axj = dict()
        exec(tsykj__jokvb, {'bodo': bodo}, unsag__axj)
        rxza__ceij = unsag__axj['impl']
        return rxza__ceij
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(cenj__cjjp.dtype, types.Integer) for
        cenj__cjjp in arr_list.types) and any(isinstance(cenj__cjjp,
        IntegerArrayType) for cenj__cjjp in arr_list.types):

        def impl_int_arr_list(arr_list):
            hxgrf__ifa = convert_to_nullable_tup(arr_list)
            yazc__ddbxz = []
            duqjv__fegjt = 0
            for A in hxgrf__ifa:
                yazc__ddbxz.append(A._data)
                duqjv__fegjt += len(A)
            mqz__cbra = bodo.libs.array_kernels.concat(yazc__ddbxz)
            qgs__hsf = duqjv__fegjt + 7 >> 3
            zxrq__viwqt = np.empty(qgs__hsf, np.uint8)
            vvbtd__vocwy = 0
            for A in hxgrf__ifa:
                dsj__oywv = A._null_bitmap
                for cbdls__fzw in range(len(A)):
                    xra__xpa = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        dsj__oywv, cbdls__fzw)
                    bodo.libs.int_arr_ext.set_bit_to_arr(zxrq__viwqt,
                        vvbtd__vocwy, xra__xpa)
                    vvbtd__vocwy += 1
            return bodo.libs.int_arr_ext.init_integer_array(mqz__cbra,
                zxrq__viwqt)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(cenj__cjjp.dtype == types.bool_ for cenj__cjjp in
        arr_list.types) and any(cenj__cjjp == boolean_array for cenj__cjjp in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            hxgrf__ifa = convert_to_nullable_tup(arr_list)
            yazc__ddbxz = []
            duqjv__fegjt = 0
            for A in hxgrf__ifa:
                yazc__ddbxz.append(A._data)
                duqjv__fegjt += len(A)
            mqz__cbra = bodo.libs.array_kernels.concat(yazc__ddbxz)
            qgs__hsf = duqjv__fegjt + 7 >> 3
            zxrq__viwqt = np.empty(qgs__hsf, np.uint8)
            vvbtd__vocwy = 0
            for A in hxgrf__ifa:
                dsj__oywv = A._null_bitmap
                for cbdls__fzw in range(len(A)):
                    xra__xpa = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        dsj__oywv, cbdls__fzw)
                    bodo.libs.int_arr_ext.set_bit_to_arr(zxrq__viwqt,
                        vvbtd__vocwy, xra__xpa)
                    vvbtd__vocwy += 1
            return bodo.libs.bool_arr_ext.init_bool_array(mqz__cbra,
                zxrq__viwqt)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            cmx__ueuh = []
            for A in arr_list:
                cmx__ueuh.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                cmx__ueuh), arr_list[0].dtype)
        return cat_array_concat_impl
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            duqjv__fegjt = 0
            for A in arr_list:
                duqjv__fegjt += len(A)
            hru__rus = np.empty(duqjv__fegjt, dtype)
            uwzsp__umqc = 0
            for A in arr_list:
                n = len(A)
                hru__rus[uwzsp__umqc:uwzsp__umqc + n] = A
                uwzsp__umqc += n
            return hru__rus
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(cenj__cjjp,
        (types.Array, IntegerArrayType)) and isinstance(cenj__cjjp.dtype,
        types.Integer) for cenj__cjjp in arr_list.types) and any(isinstance
        (cenj__cjjp, types.Array) and isinstance(cenj__cjjp.dtype, types.
        Float) for cenj__cjjp in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            zfxbi__vfz = []
            for A in arr_list:
                zfxbi__vfz.append(A._data)
            fza__vhul = bodo.libs.array_kernels.concat(zfxbi__vfz)
            bfij__utvu = bodo.libs.map_arr_ext.init_map_arr(fza__vhul)
            return bfij__utvu
        return impl_map_arr_list
    for bwimf__medj in arr_list:
        if not isinstance(bwimf__medj, types.Array):
            raise_bodo_error('concat of array types {} not supported'.
                format(arr_list))
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(cenj__cjjp.astype(np.float64) for cenj__cjjp in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    xwa__kvii = len(arr_tup.types)
    tsykj__jokvb = 'def f(arr_tup):\n'
    tsykj__jokvb += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(xwa__kvii
        )), ',' if xwa__kvii == 1 else '')
    zysz__utu = {}
    exec(tsykj__jokvb, {'np': np}, zysz__utu)
    mmx__otizl = zysz__utu['f']
    return mmx__otizl


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    xwa__kvii = len(arr_tup.types)
    afny__ahj = find_common_np_dtype(arr_tup.types)
    ulgh__ncxy = None
    gwfr__qugx = ''
    if isinstance(afny__ahj, types.Integer):
        ulgh__ncxy = bodo.libs.int_arr_ext.IntDtype(afny__ahj)
        gwfr__qugx = '.astype(out_dtype, False)'
    tsykj__jokvb = 'def f(arr_tup):\n'
    tsykj__jokvb += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, gwfr__qugx) for i in range(xwa__kvii)), ',' if xwa__kvii ==
        1 else '')
    zysz__utu = {}
    exec(tsykj__jokvb, {'bodo': bodo, 'out_dtype': ulgh__ncxy}, zysz__utu)
    etqvc__hzov = zysz__utu['f']
    return etqvc__hzov


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, kmbqj__twvml = build_set_seen_na(A)
        return len(s) + int(not dropna and kmbqj__twvml)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        kck__uljqa = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        xmmun__nfv = len(kck__uljqa)
        return bodo.libs.distributed_api.dist_reduce(xmmun__nfv, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([rwxsg__iekis for rwxsg__iekis in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        hqg__hlmy = np.finfo(A.dtype(1).dtype).max
    else:
        hqg__hlmy = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        hru__rus = np.empty(n, A.dtype)
        vafx__ndm = hqg__hlmy
        for i in range(n):
            vafx__ndm = min(vafx__ndm, A[i])
            hru__rus[i] = vafx__ndm
        return hru__rus
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        hqg__hlmy = np.finfo(A.dtype(1).dtype).min
    else:
        hqg__hlmy = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        hru__rus = np.empty(n, A.dtype)
        vafx__ndm = hqg__hlmy
        for i in range(n):
            vafx__ndm = max(vafx__ndm, A[i])
            hru__rus[i] = vafx__ndm
        return hru__rus
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        xrps__gsv = arr_info_list_to_table([array_to_info(A)])
        jadvu__glklb = 1
        hxm__xgojp = 0
        imcx__bdbn = drop_duplicates_table(xrps__gsv, parallel,
            jadvu__glklb, hxm__xgojp, dropna)
        hru__rus = info_to_array(info_from_table(imcx__bdbn, 0), A)
        delete_table(xrps__gsv)
        delete_table(imcx__bdbn)
        return hru__rus
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    ohry__cwy = bodo.utils.typing.to_nullable_type(arr.dtype)
    cah__ompg = index_arr
    hwr__lydcz = cah__ompg.dtype

    def impl(arr, index_arr):
        n = len(arr)
        heuk__rkjj = init_nested_counts(ohry__cwy)
        afjxq__npfrm = init_nested_counts(hwr__lydcz)
        for i in range(n):
            gliyn__ccz = index_arr[i]
            if isna(arr, i):
                heuk__rkjj = (heuk__rkjj[0] + 1,) + heuk__rkjj[1:]
                afjxq__npfrm = add_nested_counts(afjxq__npfrm, gliyn__ccz)
                continue
            dtme__ieni = arr[i]
            if len(dtme__ieni) == 0:
                heuk__rkjj = (heuk__rkjj[0] + 1,) + heuk__rkjj[1:]
                afjxq__npfrm = add_nested_counts(afjxq__npfrm, gliyn__ccz)
                continue
            heuk__rkjj = add_nested_counts(heuk__rkjj, dtme__ieni)
            for ykrlj__vmtbe in range(len(dtme__ieni)):
                afjxq__npfrm = add_nested_counts(afjxq__npfrm, gliyn__ccz)
        hru__rus = bodo.utils.utils.alloc_type(heuk__rkjj[0], ohry__cwy,
            heuk__rkjj[1:])
        kiu__yrt = bodo.utils.utils.alloc_type(heuk__rkjj[0], cah__ompg,
            afjxq__npfrm)
        xunjq__unoi = 0
        for i in range(n):
            if isna(arr, i):
                setna(hru__rus, xunjq__unoi)
                kiu__yrt[xunjq__unoi] = index_arr[i]
                xunjq__unoi += 1
                continue
            dtme__ieni = arr[i]
            pvaja__zlo = len(dtme__ieni)
            if pvaja__zlo == 0:
                setna(hru__rus, xunjq__unoi)
                kiu__yrt[xunjq__unoi] = index_arr[i]
                xunjq__unoi += 1
                continue
            hru__rus[xunjq__unoi:xunjq__unoi + pvaja__zlo] = dtme__ieni
            kiu__yrt[xunjq__unoi:xunjq__unoi + pvaja__zlo] = index_arr[i]
            xunjq__unoi += pvaja__zlo
        return hru__rus, kiu__yrt
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert arr == string_array_type
    cah__ompg = index_arr
    hwr__lydcz = cah__ompg.dtype

    def impl(arr, pat, n, index_arr):
        ker__annr = pat is not None and len(pat) > 1
        if ker__annr:
            xrtv__ylmls = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        tjc__djs = len(arr)
        wcxn__rgqp = 0
        oef__hch = 0
        afjxq__npfrm = init_nested_counts(hwr__lydcz)
        for i in range(tjc__djs):
            gliyn__ccz = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                wcxn__rgqp += 1
                afjxq__npfrm = add_nested_counts(afjxq__npfrm, gliyn__ccz)
                continue
            if ker__annr:
                thr__uoavv = xrtv__ylmls.split(arr[i], maxsplit=n)
            else:
                thr__uoavv = arr[i].split(pat, n)
            wcxn__rgqp += len(thr__uoavv)
            for s in thr__uoavv:
                afjxq__npfrm = add_nested_counts(afjxq__npfrm, gliyn__ccz)
                oef__hch += bodo.libs.str_arr_ext.get_utf8_size(s)
        hru__rus = bodo.libs.str_arr_ext.pre_alloc_string_array(wcxn__rgqp,
            oef__hch)
        kiu__yrt = bodo.utils.utils.alloc_type(wcxn__rgqp, cah__ompg,
            afjxq__npfrm)
        kqv__ddpy = 0
        for cbdls__fzw in range(tjc__djs):
            if isna(arr, cbdls__fzw):
                hru__rus[kqv__ddpy] = ''
                bodo.libs.array_kernels.setna(hru__rus, kqv__ddpy)
                kiu__yrt[kqv__ddpy] = index_arr[cbdls__fzw]
                kqv__ddpy += 1
                continue
            if ker__annr:
                thr__uoavv = xrtv__ylmls.split(arr[cbdls__fzw], maxsplit=n)
            else:
                thr__uoavv = arr[cbdls__fzw].split(pat, n)
            xnih__sfsw = len(thr__uoavv)
            hru__rus[kqv__ddpy:kqv__ddpy + xnih__sfsw] = thr__uoavv
            kiu__yrt[kqv__ddpy:kqv__ddpy + xnih__sfsw] = index_arr[cbdls__fzw]
            kqv__ddpy += xnih__sfsw
        return hru__rus, kiu__yrt
    return impl


def gen_na_array(n, arr):
    return np.full(n, np.nan)


@overload(gen_na_array, no_unliteral=True)
def overload_gen_na_array(n, arr):
    if isinstance(arr, types.TypeRef):
        arr = arr.instance_type
    dtype = arr.dtype
    if isinstance(dtype, (types.Integer, types.Float)):
        dtype = dtype if isinstance(dtype, types.Float) else types.float64

        def impl_float(n, arr):
            numba.parfors.parfor.init_prange()
            hru__rus = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                hru__rus[i] = np.nan
            return hru__rus
        return impl_float

    def impl(n, arr):
        numba.parfors.parfor.init_prange()
        hru__rus = bodo.utils.utils.alloc_type(n, arr, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(hru__rus, i)
        return hru__rus
    return impl


def gen_na_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_gen_na_array = (
    gen_na_array_equiv)


def resize_and_copy(A, new_len):
    return A


@overload(resize_and_copy, no_unliteral=True)
def overload_resize_and_copy(A, old_size, new_len):
    jful__uwn = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            hru__rus = bodo.utils.utils.alloc_type(new_len, jful__uwn)
            bodo.libs.str_arr_ext.str_copy_ptr(hru__rus.ctypes, 0, A.ctypes,
                old_size)
            return hru__rus
        return impl_char

    def impl(A, old_size, new_len):
        hru__rus = bodo.utils.utils.alloc_type(new_len, jful__uwn, (-1,))
        hru__rus[:old_size] = A[:old_size]
        return hru__rus
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    fpcrp__oxub = math.ceil((stop - start) / step)
    return int(max(fpcrp__oxub, 0))


def calc_nitems_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    if guard(find_const, self.func_ir, args[0]) == 0 and guard(find_const,
        self.func_ir, args[2]) == 1:
        return ArrayAnalysis.AnalyzeResult(shape=args[1], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_calc_nitems = (
    calc_nitems_equiv)


def arange_parallel_impl(return_type, *args):
    dtype = as_dtype(return_type.dtype)

    def arange_1(stop):
        return np.arange(0, stop, 1, dtype)

    def arange_2(start, stop):
        return np.arange(start, stop, 1, dtype)

    def arange_3(start, stop, step):
        return np.arange(start, stop, step, dtype)
    if any(isinstance(rwxsg__iekis, types.Complex) for rwxsg__iekis in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            piao__inoh = (stop - start) / step
            fpcrp__oxub = math.ceil(piao__inoh.real)
            kjld__jsfa = math.ceil(piao__inoh.imag)
            tim__jujm = int(max(min(kjld__jsfa, fpcrp__oxub), 0))
            arr = np.empty(tim__jujm, dtype)
            for i in numba.parfors.parfor.internal_prange(tim__jujm):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            tim__jujm = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(tim__jujm, dtype)
            for i in numba.parfors.parfor.internal_prange(tim__jujm):
                arr[i] = start + i * step
            return arr
    if len(args) == 1:
        return arange_1
    elif len(args) == 2:
        return arange_2
    elif len(args) == 3:
        return arange_3
    elif len(args) == 4:
        return arange_4
    else:
        raise BodoError('parallel arange with types {}'.format(args))


if bodo.numba_compat._check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.arange_parallel_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c72b0390b4f3e52dcc5426bd42c6b55ff96bae5a425381900985d36e7527a4bd':
        warnings.warn('numba.parfors.parfor.arange_parallel_impl has changed')
numba.parfors.parfor.swap_functions_map['arange', 'numpy'
    ] = arange_parallel_impl


def sort(arr, ascending, inplace):
    return np.sort(arr)


@overload(sort, no_unliteral=True)
def overload_sort(arr, ascending, inplace):

    def impl(arr, ascending, inplace):
        n = len(arr)
        data = np.arange(n),
        yprj__gbos = arr,
        if not inplace:
            yprj__gbos = arr.copy(),
        uaalb__knfdz = bodo.libs.str_arr_ext.to_list_if_immutable_arr(
            yprj__gbos)
        iau__mzpw = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(uaalb__knfdz, 0, n, iau__mzpw)
        if not ascending:
            bodo.libs.timsort.reverseRange(uaalb__knfdz, 0, n, iau__mzpw)
        bodo.libs.str_arr_ext.cp_str_list_to_array(yprj__gbos, uaalb__knfdz)
        return yprj__gbos[0]
    return impl


def overload_array_max(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).max()
        return impl


overload(np.max, inline='always', no_unliteral=True)(overload_array_max)
overload(max, inline='always', no_unliteral=True)(overload_array_max)


def overload_array_min(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).min()
        return impl


overload(np.min, inline='always', no_unliteral=True)(overload_array_min)
overload(min, inline='always', no_unliteral=True)(overload_array_min)


def overload_array_sum(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).sum()
    return impl


overload(np.sum, inline='always', no_unliteral=True)(overload_array_sum)
overload(sum, inline='always', no_unliteral=True)(overload_array_sum)


@overload(np.prod, inline='always', no_unliteral=True)
def overload_array_prod(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).prod()
    return impl


def nonzero(arr):
    return arr,


@overload(nonzero, no_unliteral=True)
def nonzero_overload(A, parallel=False):
    if not bodo.utils.utils.is_array_typ(A, False):
        return

    def impl(A, parallel=False):
        n = len(A)
        if parallel:
            offset = bodo.libs.distributed_api.dist_exscan(n, Reduce_Type.
                Sum.value)
        else:
            offset = 0
        bfij__utvu = []
        for i in range(n):
            if A[i]:
                bfij__utvu.append(i + offset)
        return np.array(bfij__utvu, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    jful__uwn = element_type(A)
    if jful__uwn == types.unicode_type:
        null_value = '""'
    elif jful__uwn == types.bool_:
        null_value = 'False'
    elif jful__uwn == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif jful__uwn == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    kqv__ddpy = 'i'
    kjr__ookfk = False
    oklyg__ivnn = get_overload_const_str(method)
    if oklyg__ivnn in ('ffill', 'pad'):
        nfcca__rcgjg = 'n'
        send_right = True
    elif oklyg__ivnn in ('backfill', 'bfill'):
        nfcca__rcgjg = 'n-1, -1, -1'
        send_right = False
        if jful__uwn == types.unicode_type:
            kqv__ddpy = '(n - 1) - i'
            kjr__ookfk = True
    tsykj__jokvb = 'def impl(A, method, parallel=False):\n'
    tsykj__jokvb += '  has_last_value = False\n'
    tsykj__jokvb += f'  last_value = {null_value}\n'
    tsykj__jokvb += '  if parallel:\n'
    tsykj__jokvb += '    rank = bodo.libs.distributed_api.get_rank()\n'
    tsykj__jokvb += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    tsykj__jokvb += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    tsykj__jokvb += '  n = len(A)\n'
    tsykj__jokvb += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    tsykj__jokvb += f'  for i in range({nfcca__rcgjg}):\n'
    tsykj__jokvb += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    tsykj__jokvb += (
        f'      bodo.libs.array_kernels.setna(out_arr, {kqv__ddpy})\n')
    tsykj__jokvb += '      continue\n'
    tsykj__jokvb += '    s = A[i]\n'
    tsykj__jokvb += '    if bodo.libs.array_kernels.isna(A, i):\n'
    tsykj__jokvb += '      s = last_value\n'
    tsykj__jokvb += f'    out_arr[{kqv__ddpy}] = s\n'
    tsykj__jokvb += '    last_value = s\n'
    tsykj__jokvb += '    has_last_value = True\n'
    if kjr__ookfk:
        tsykj__jokvb += '  return out_arr[::-1]\n'
    else:
        tsykj__jokvb += '  return out_arr\n'
    ceoj__gbziq = {}
    exec(tsykj__jokvb, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm}, ceoj__gbziq)
    impl = ceoj__gbziq['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        hbffz__neke = 0
        cwlq__krcz = n_pes - 1
        ezf__vvfm = np.int32(rank + 1)
        cmm__kwka = np.int32(rank - 1)
        xbye__putzp = len(in_arr) - 1
        flmzt__wadb = -1
        qql__wgq = -1
    else:
        hbffz__neke = n_pes - 1
        cwlq__krcz = 0
        ezf__vvfm = np.int32(rank - 1)
        cmm__kwka = np.int32(rank + 1)
        xbye__putzp = 0
        flmzt__wadb = len(in_arr)
        qql__wgq = 1
    xel__cowp = np.int32(bodo.hiframes.rolling.comm_border_tag)
    wrrmo__wuzcr = np.empty(1, dtype=np.bool_)
    jixw__fskq = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    dmtoo__uyu = np.empty(1, dtype=np.bool_)
    bfbb__wdkei = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    crjh__sjb = False
    kbgxj__gwdip = null_value
    for i in range(xbye__putzp, flmzt__wadb, qql__wgq):
        if not isna(in_arr, i):
            crjh__sjb = True
            kbgxj__gwdip = in_arr[i]
            break
    if rank != hbffz__neke:
        tkmhx__wbnm = bodo.libs.distributed_api.irecv(wrrmo__wuzcr, 1,
            cmm__kwka, xel__cowp, True)
        bodo.libs.distributed_api.wait(tkmhx__wbnm, True)
        laktq__xdix = bodo.libs.distributed_api.irecv(jixw__fskq, 1,
            cmm__kwka, xel__cowp, True)
        bodo.libs.distributed_api.wait(laktq__xdix, True)
        ner__gorao = wrrmo__wuzcr[0]
        ggs__hvhzq = jixw__fskq[0]
    else:
        ner__gorao = False
        ggs__hvhzq = null_value
    if crjh__sjb:
        dmtoo__uyu[0] = crjh__sjb
        bfbb__wdkei[0] = kbgxj__gwdip
    else:
        dmtoo__uyu[0] = ner__gorao
        bfbb__wdkei[0] = ggs__hvhzq
    if rank != cwlq__krcz:
        qtdbe__anlk = bodo.libs.distributed_api.isend(dmtoo__uyu, 1,
            ezf__vvfm, xel__cowp, True)
        pagyd__zehz = bodo.libs.distributed_api.isend(bfbb__wdkei, 1,
            ezf__vvfm, xel__cowp, True)
    return ner__gorao, ggs__hvhzq


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    fias__kki = {'axis': axis, 'kind': kind, 'order': order}
    xxj__fyw = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', fias__kki, xxj__fyw, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    jful__uwn = A
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            tjc__djs = len(A)
            hru__rus = bodo.utils.utils.alloc_type(tjc__djs * repeats,
                jful__uwn, (-1,))
            for i in range(tjc__djs):
                kqv__ddpy = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for cbdls__fzw in range(repeats):
                        bodo.libs.array_kernels.setna(hru__rus, kqv__ddpy +
                            cbdls__fzw)
                else:
                    hru__rus[kqv__ddpy:kqv__ddpy + repeats] = A[i]
            return hru__rus
        return impl_int

    def impl_arr(A, repeats):
        tjc__djs = len(A)
        hru__rus = bodo.utils.utils.alloc_type(repeats.sum(), jful__uwn, (-1,))
        kqv__ddpy = 0
        for i in range(tjc__djs):
            ubs__djmkf = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for cbdls__fzw in range(ubs__djmkf):
                    bodo.libs.array_kernels.setna(hru__rus, kqv__ddpy +
                        cbdls__fzw)
            else:
                hru__rus[kqv__ddpy:kqv__ddpy + ubs__djmkf] = A[i]
            kqv__ddpy += ubs__djmkf
        return hru__rus
    return impl_arr


@overload(np.repeat, inline='always', no_unliteral=True)
def np_repeat(A, repeats):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    if not isinstance(repeats, types.Integer):
        raise BodoError(
            'Only integer type supported for repeats in np.repeat()')

    def impl(A, repeats):
        return bodo.libs.array_kernels.repeat_kernel(A, repeats)
    return impl


@overload(np.unique, inline='always', no_unliteral=True)
def np_unique(A):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return

    def impl(A):
        cif__inyq = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(cif__inyq, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        fot__ncn = bodo.libs.array_kernels.concat([A1, A2])
        sqyb__qehi = bodo.libs.array_kernels.unique(fot__ncn)
        return pd.Series(sqyb__qehi).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    fias__kki = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    xxj__fyw = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', fias__kki, xxj__fyw, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        glpkt__rett = bodo.libs.array_kernels.unique(A1)
        osmze__pld = bodo.libs.array_kernels.unique(A2)
        fot__ncn = bodo.libs.array_kernels.concat([glpkt__rett, osmze__pld])
        mnj__mwcpq = pd.Series(fot__ncn).sort_values().values
        return slice_array_intersect1d(mnj__mwcpq)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    xjj__tfq = arr[1:] == arr[:-1]
    return arr[:-1][xjj__tfq]


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    fias__kki = {'assume_unique': assume_unique}
    xxj__fyw = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', fias__kki, xxj__fyw, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        glpkt__rett = bodo.libs.array_kernels.unique(A1)
        osmze__pld = bodo.libs.array_kernels.unique(A2)
        xjj__tfq = calculate_mask_setdiff1d(glpkt__rett, osmze__pld)
        return pd.Series(glpkt__rett[xjj__tfq]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    xjj__tfq = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        xjj__tfq &= A1 != A2[i]
    return xjj__tfq


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    fias__kki = {'retstep': retstep, 'axis': axis}
    xxj__fyw = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', fias__kki, xxj__fyw, 'numpy')
    tjvj__kmt = False
    if is_overload_none(dtype):
        jful__uwn = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            tjvj__kmt = True
        jful__uwn = numba.np.numpy_support.as_dtype(dtype).type
    if tjvj__kmt:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            nyxo__wkepr = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            hru__rus = np.empty(num, jful__uwn)
            for i in numba.parfors.parfor.internal_prange(num):
                hru__rus[i] = jful__uwn(np.floor(start + i * nyxo__wkepr))
            return hru__rus
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            nyxo__wkepr = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            hru__rus = np.empty(num, jful__uwn)
            for i in numba.parfors.parfor.internal_prange(num):
                hru__rus[i] = jful__uwn(start + i * nyxo__wkepr)
            return hru__rus
        return impl


def np_linspace_get_stepsize(start, stop, num, endpoint):
    return 0


@overload(np_linspace_get_stepsize, no_unliteral=True)
def overload_np_linspace_get_stepsize(start, stop, num, endpoint):

    def impl(start, stop, num, endpoint):
        if num < 0:
            raise ValueError('np.linspace() Num must be >= 0')
        if endpoint:
            num -= 1
        if num > 1:
            return (stop - start) / num
        return 0
    return impl


@overload(operator.contains, no_unliteral=True)
def arr_contains(A, val):
    if not (bodo.utils.utils.is_array_typ(A, False) and A.dtype == types.
        unliteral(val)):
        return

    def impl(A, val):
        numba.parfors.parfor.init_prange()
        xwa__kvii = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                xwa__kvii += A[i] == val
        return xwa__kvii > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    fias__kki = {'axis': axis, 'out': out, 'keepdims': keepdims}
    xxj__fyw = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', fias__kki, xxj__fyw, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        xwa__kvii = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                xwa__kvii += int(bool(A[i]))
        return xwa__kvii > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    fias__kki = {'axis': axis, 'out': out, 'keepdims': keepdims}
    xxj__fyw = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', fias__kki, xxj__fyw, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        xwa__kvii = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                xwa__kvii += int(bool(A[i]))
        return xwa__kvii == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    fias__kki = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    xxj__fyw = {'out': None, 'where': True, 'casting': 'same_kind', 'order':
        'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', fias__kki, xxj__fyw, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        cmy__htnw = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            hru__rus = np.empty(n, cmy__htnw)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(hru__rus, i)
                    continue
                hru__rus[i] = np_cbrt_scalar(A[i], cmy__htnw)
            return hru__rus
        return impl_arr
    cmy__htnw = np.promote_types(numba.np.numpy_support.as_dtype(A), numba.
        np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, cmy__htnw)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    dtae__fubbk = x < 0
    if dtae__fubbk:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if dtae__fubbk:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    melx__tkyd = isinstance(tup, (types.BaseTuple, types.List))
    gipt__mxwba = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for bwimf__medj in tup.types:
            melx__tkyd = melx__tkyd and bodo.utils.utils.is_array_typ(
                bwimf__medj, False)
    elif isinstance(tup, types.List):
        melx__tkyd = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif gipt__mxwba:
        vwweq__prpts = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for bwimf__medj in vwweq__prpts.types:
            gipt__mxwba = gipt__mxwba and bodo.utils.utils.is_array_typ(
                bwimf__medj, False)
    if not (melx__tkyd or gipt__mxwba):
        return
    if gipt__mxwba:

        def impl_series(tup):
            arr_tup = bodo.hiframes.pd_series_ext.get_series_data(tup)
            return bodo.libs.array_kernels.concat(arr_tup)
        return impl_series

    def impl(tup):
        return bodo.libs.array_kernels.concat(tup)
    return impl


@overload(np.random.multivariate_normal, inline='always', no_unliteral=True)
def np_random_multivariate_normal(mean, cov, size=None, check_valid='warn',
    tol=1e-08):
    fias__kki = {'check_valid': check_valid, 'tol': tol}
    xxj__fyw = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', fias__kki,
        xxj__fyw, 'numpy')
    if not isinstance(size, types.Integer):
        raise BodoError(
            'np.random.multivariate_normal() size argument is required and must be an integer'
            )
    if not (bodo.utils.utils.is_array_typ(mean, False) and mean.ndim == 1):
        raise BodoError(
            'np.random.multivariate_normal() mean must be a 1 dimensional numpy array'
            )
    if not (bodo.utils.utils.is_array_typ(cov, False) and cov.ndim == 2):
        raise BodoError(
            'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
            )

    def impl(mean, cov, size=None, check_valid='warn', tol=1e-08):
        _validate_multivar_norm(cov)
        ski__pmy = mean.shape[0]
        cnpu__ypd = size, ski__pmy
        nnkl__vqfp = np.random.standard_normal(cnpu__ypd)
        cov = cov.astype(np.float64)
        kfso__jhpr, s, aol__ehrkx = np.linalg.svd(cov)
        res = np.dot(nnkl__vqfp, np.sqrt(s).reshape(ski__pmy, 1) * aol__ehrkx)
        civ__wlt = res + mean
        return civ__wlt
    return impl


def _validate_multivar_norm(cov):
    return


@overload(_validate_multivar_norm, no_unliteral=True)
def _overload_validate_multivar_norm(cov):

    def impl(cov):
        if cov.shape[0] != cov.shape[1]:
            raise ValueError(
                'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
                )
    return impl


def _nan_argmin(arr):
    return


@overload(_nan_argmin, no_unliteral=True)
def _overload_nan_argmin(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            numba.parfors.parfor.init_prange()
            ymhlp__krtq = bodo.hiframes.series_kernels._get_type_max_value(arr)
            ygdz__oaw = typing.builtins.IndexValue(-1, ymhlp__krtq)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                ogy__wvr = typing.builtins.IndexValue(i, arr[i])
                ygdz__oaw = min(ygdz__oaw, ogy__wvr)
            return ygdz__oaw.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        irahi__yrbwj = (bodo.hiframes.pd_categorical_ext.
            get_categories_int_type(arr.dtype))

        def impl_cat_arr(arr):
            hglak__gjh = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            ymhlp__krtq = irahi__yrbwj(len(arr.dtype.categories) + 1)
            ygdz__oaw = typing.builtins.IndexValue(-1, ymhlp__krtq)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                ogy__wvr = typing.builtins.IndexValue(i, hglak__gjh[i])
                ygdz__oaw = min(ygdz__oaw, ogy__wvr)
            return ygdz__oaw.index
        return impl_cat_arr
    return lambda arr: arr.argmin()


def _nan_argmax(arr):
    return


@overload(_nan_argmax, no_unliteral=True)
def _overload_nan_argmax(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            n = len(arr)
            numba.parfors.parfor.init_prange()
            ymhlp__krtq = bodo.hiframes.series_kernels._get_type_min_value(arr)
            ygdz__oaw = typing.builtins.IndexValue(-1, ymhlp__krtq)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                ogy__wvr = typing.builtins.IndexValue(i, arr[i])
                ygdz__oaw = max(ygdz__oaw, ogy__wvr)
            return ygdz__oaw.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        irahi__yrbwj = (bodo.hiframes.pd_categorical_ext.
            get_categories_int_type(arr.dtype))

        def impl_cat_arr(arr):
            n = len(arr)
            hglak__gjh = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            ymhlp__krtq = irahi__yrbwj(-1)
            ygdz__oaw = typing.builtins.IndexValue(-1, ymhlp__krtq)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                ogy__wvr = typing.builtins.IndexValue(i, hglak__gjh[i])
                ygdz__oaw = max(ygdz__oaw, ogy__wvr)
            return ygdz__oaw.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
