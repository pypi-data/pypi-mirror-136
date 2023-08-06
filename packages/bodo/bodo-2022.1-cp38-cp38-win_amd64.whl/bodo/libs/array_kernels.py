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
        ujxq__tgtku = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = ujxq__tgtku
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
            ysxje__ewf = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            ysxje__ewf[ind + 1] = ysxje__ewf[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            ysxje__ewf = bodo.libs.array_item_arr_ext.get_offsets(arr)
            ysxje__ewf[ind + 1] = ysxje__ewf[ind]
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
    yrq__btiz = arr_tup.count
    djdra__euf = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(yrq__btiz):
        djdra__euf += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    djdra__euf += '  return\n'
    vcdm__rhp = {}
    exec(djdra__euf, {'setna': setna}, vcdm__rhp)
    impl = vcdm__rhp['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        flv__nafw = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(flv__nafw.start, flv__nafw.stop, flv__nafw.step):
            setna(arr, i)
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    yzp__mmyi = array_to_info(arr)
    _median_series_computation(res, yzp__mmyi, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(yzp__mmyi)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    yzp__mmyi = array_to_info(arr)
    _autocorr_series_computation(res, yzp__mmyi, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(yzp__mmyi)


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
    yzp__mmyi = array_to_info(arr)
    _compute_series_monotonicity(res, yzp__mmyi, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(yzp__mmyi)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    cmi__hyqv = res[0] > 0.5
    return cmi__hyqv


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        apy__rhqza = '-'
        hugt__rmx = 'index_arr[0] > threshhold_date'
        mifnl__jrds = '1, n+1'
        hkzjt__trww = 'index_arr[-i] <= threshhold_date'
        vlko__uuyt = 'i - 1'
    else:
        apy__rhqza = '+'
        hugt__rmx = 'index_arr[-1] < threshhold_date'
        mifnl__jrds = 'n'
        hkzjt__trww = 'index_arr[i] >= threshhold_date'
        vlko__uuyt = 'i'
    djdra__euf = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        djdra__euf += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        djdra__euf += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            djdra__euf += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            djdra__euf += (
                '      threshhold_date = initial_date - date_offset.base + date_offset\n'
                )
            djdra__euf += '    else:\n'
            djdra__euf += (
                '      threshhold_date = initial_date + date_offset\n')
        else:
            djdra__euf += (
                f'    threshhold_date = initial_date {apy__rhqza} date_offset\n'
                )
    else:
        djdra__euf += f'  threshhold_date = initial_date {apy__rhqza} offset\n'
    djdra__euf += '  local_valid = 0\n'
    djdra__euf += f'  n = len(index_arr)\n'
    djdra__euf += f'  if n:\n'
    djdra__euf += f'    if {hugt__rmx}:\n'
    djdra__euf += '      loc_valid = n\n'
    djdra__euf += '    else:\n'
    djdra__euf += f'      for i in range({mifnl__jrds}):\n'
    djdra__euf += f'        if {hkzjt__trww}:\n'
    djdra__euf += f'          loc_valid = {vlko__uuyt}\n'
    djdra__euf += '          break\n'
    djdra__euf += '  if is_parallel:\n'
    djdra__euf += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    djdra__euf += '    return total_valid\n'
    djdra__euf += '  else:\n'
    djdra__euf += '    return loc_valid\n'
    vcdm__rhp = {}
    exec(djdra__euf, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, vcdm__rhp)
    return vcdm__rhp['impl']


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
    drry__buyzy = numba_to_c_type(sig.args[0].dtype)
    zrmcy__wgco = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), drry__buyzy))
    onuco__qljey = args[0]
    foa__zdxzz = sig.args[0]
    if isinstance(foa__zdxzz, (IntegerArrayType, BooleanArrayType)):
        onuco__qljey = cgutils.create_struct_proxy(foa__zdxzz)(context,
            builder, onuco__qljey).data
        foa__zdxzz = types.Array(foa__zdxzz.dtype, 1, 'C')
    assert foa__zdxzz.ndim == 1
    arr = make_array(foa__zdxzz)(context, builder, onuco__qljey)
    zekc__yxnix = builder.extract_value(arr.shape, 0)
    zgt__rps = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        zekc__yxnix, args[1], builder.load(zrmcy__wgco)]
    qpg__loqk = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    buiqq__mtdn = lir.FunctionType(lir.DoubleType(), qpg__loqk)
    lobx__gymtj = cgutils.get_or_insert_function(builder.module,
        buiqq__mtdn, name='quantile_sequential')
    evna__vjsl = builder.call(lobx__gymtj, zgt__rps)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return evna__vjsl


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    drry__buyzy = numba_to_c_type(sig.args[0].dtype)
    zrmcy__wgco = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), drry__buyzy))
    onuco__qljey = args[0]
    foa__zdxzz = sig.args[0]
    if isinstance(foa__zdxzz, (IntegerArrayType, BooleanArrayType)):
        onuco__qljey = cgutils.create_struct_proxy(foa__zdxzz)(context,
            builder, onuco__qljey).data
        foa__zdxzz = types.Array(foa__zdxzz.dtype, 1, 'C')
    assert foa__zdxzz.ndim == 1
    arr = make_array(foa__zdxzz)(context, builder, onuco__qljey)
    zekc__yxnix = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        otnk__raawd = args[2]
    else:
        otnk__raawd = zekc__yxnix
    zgt__rps = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        zekc__yxnix, otnk__raawd, args[1], builder.load(zrmcy__wgco)]
    qpg__loqk = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType(
        64), lir.DoubleType(), lir.IntType(32)]
    buiqq__mtdn = lir.FunctionType(lir.DoubleType(), qpg__loqk)
    lobx__gymtj = cgutils.get_or_insert_function(builder.module,
        buiqq__mtdn, name='quantile_parallel')
    evna__vjsl = builder.call(lobx__gymtj, zgt__rps)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return evna__vjsl


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    zlq__xemdg = start
    sdsx__fjg = 2 * start + 1
    fjdmc__aduyw = 2 * start + 2
    if sdsx__fjg < n and not cmp_f(arr[sdsx__fjg], arr[zlq__xemdg]):
        zlq__xemdg = sdsx__fjg
    if fjdmc__aduyw < n and not cmp_f(arr[fjdmc__aduyw], arr[zlq__xemdg]):
        zlq__xemdg = fjdmc__aduyw
    if zlq__xemdg != start:
        arr[start], arr[zlq__xemdg] = arr[zlq__xemdg], arr[start]
        ind_arr[start], ind_arr[zlq__xemdg] = ind_arr[zlq__xemdg], ind_arr[
            start]
        min_heapify(arr, ind_arr, n, zlq__xemdg, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        lmn__dnr = np.empty(k, A.dtype)
        boux__pcxl = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                lmn__dnr[ind] = A[i]
                boux__pcxl[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            lmn__dnr = lmn__dnr[:ind]
            boux__pcxl = boux__pcxl[:ind]
        return lmn__dnr, boux__pcxl, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        puu__avl = np.sort(A)
        pgwhr__ddy = index_arr[np.argsort(A)]
        tlgti__njn = pd.Series(puu__avl).notna().values
        puu__avl = puu__avl[tlgti__njn]
        pgwhr__ddy = pgwhr__ddy[tlgti__njn]
        if is_largest:
            puu__avl = puu__avl[::-1]
            pgwhr__ddy = pgwhr__ddy[::-1]
        return np.ascontiguousarray(puu__avl), np.ascontiguousarray(pgwhr__ddy)
    lmn__dnr, boux__pcxl, start = select_k_nonan(A, index_arr, m, k)
    boux__pcxl = boux__pcxl[lmn__dnr.argsort()]
    lmn__dnr.sort()
    if not is_largest:
        lmn__dnr = np.ascontiguousarray(lmn__dnr[::-1])
        boux__pcxl = np.ascontiguousarray(boux__pcxl[::-1])
    for i in range(start, m):
        if cmp_f(A[i], lmn__dnr[0]):
            lmn__dnr[0] = A[i]
            boux__pcxl[0] = index_arr[i]
            min_heapify(lmn__dnr, boux__pcxl, k, 0, cmp_f)
    boux__pcxl = boux__pcxl[lmn__dnr.argsort()]
    lmn__dnr.sort()
    if is_largest:
        lmn__dnr = lmn__dnr[::-1]
        boux__pcxl = boux__pcxl[::-1]
    return np.ascontiguousarray(lmn__dnr), np.ascontiguousarray(boux__pcxl)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    kmfvv__gjzda = bodo.libs.distributed_api.get_rank()
    eybj__zltxn, hrns__wjoww = nlargest(A, I, k, is_largest, cmp_f)
    cmasp__gla = bodo.libs.distributed_api.gatherv(eybj__zltxn)
    ntl__zvrf = bodo.libs.distributed_api.gatherv(hrns__wjoww)
    if kmfvv__gjzda == MPI_ROOT:
        res, ohx__zop = nlargest(cmasp__gla, ntl__zvrf, k, is_largest, cmp_f)
    else:
        res = np.empty(k, A.dtype)
        ohx__zop = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(ohx__zop)
    return res, ohx__zop


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    bsp__htlrx, drg__nclk = mat.shape
    ppzj__lgo = np.empty((drg__nclk, drg__nclk), dtype=np.float64)
    for imh__gkiun in range(drg__nclk):
        for rwn__qqthh in range(imh__gkiun + 1):
            oxwel__ushu = 0
            mouro__nbo = zcx__gdnn = kjbm__bovic = bej__pczl = 0.0
            for i in range(bsp__htlrx):
                if np.isfinite(mat[i, imh__gkiun]) and np.isfinite(mat[i,
                    rwn__qqthh]):
                    xrw__rohu = mat[i, imh__gkiun]
                    khij__zkj = mat[i, rwn__qqthh]
                    oxwel__ushu += 1
                    kjbm__bovic += xrw__rohu
                    bej__pczl += khij__zkj
            if parallel:
                oxwel__ushu = bodo.libs.distributed_api.dist_reduce(oxwel__ushu
                    , sum_op)
                kjbm__bovic = bodo.libs.distributed_api.dist_reduce(kjbm__bovic
                    , sum_op)
                bej__pczl = bodo.libs.distributed_api.dist_reduce(bej__pczl,
                    sum_op)
            if oxwel__ushu < minpv:
                ppzj__lgo[imh__gkiun, rwn__qqthh] = ppzj__lgo[rwn__qqthh,
                    imh__gkiun] = np.nan
            else:
                boau__mkz = kjbm__bovic / oxwel__ushu
                dsmc__xhf = bej__pczl / oxwel__ushu
                kjbm__bovic = 0.0
                for i in range(bsp__htlrx):
                    if np.isfinite(mat[i, imh__gkiun]) and np.isfinite(mat[
                        i, rwn__qqthh]):
                        xrw__rohu = mat[i, imh__gkiun] - boau__mkz
                        khij__zkj = mat[i, rwn__qqthh] - dsmc__xhf
                        kjbm__bovic += xrw__rohu * khij__zkj
                        mouro__nbo += xrw__rohu * xrw__rohu
                        zcx__gdnn += khij__zkj * khij__zkj
                if parallel:
                    kjbm__bovic = bodo.libs.distributed_api.dist_reduce(
                        kjbm__bovic, sum_op)
                    mouro__nbo = bodo.libs.distributed_api.dist_reduce(
                        mouro__nbo, sum_op)
                    zcx__gdnn = bodo.libs.distributed_api.dist_reduce(zcx__gdnn
                        , sum_op)
                fgf__ogly = oxwel__ushu - 1.0 if cov else sqrt(mouro__nbo *
                    zcx__gdnn)
                if fgf__ogly != 0.0:
                    ppzj__lgo[imh__gkiun, rwn__qqthh] = ppzj__lgo[
                        rwn__qqthh, imh__gkiun] = kjbm__bovic / fgf__ogly
                else:
                    ppzj__lgo[imh__gkiun, rwn__qqthh] = ppzj__lgo[
                        rwn__qqthh, imh__gkiun] = np.nan
    return ppzj__lgo


@numba.njit(no_cpython_wrapper=True)
def duplicated(data, ind_arr, parallel=False):
    if parallel:
        data, (ind_arr,) = bodo.ir.join.parallel_shuffle(data, (ind_arr,))
    data = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data)
    n = len(data[0])
    out = np.empty(n, np.bool_)
    urxe__qhek = dict()
    for i in range(n):
        val = getitem_arr_tup_single(data, i)
        if val in urxe__qhek:
            out[i] = True
        else:
            out[i] = False
            urxe__qhek[val] = 0
    return out, ind_arr


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    yrq__btiz = len(data)
    djdra__euf = 'def impl(data, ind_arr, n, frac, replace, parallel=False):\n'
    djdra__euf += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        yrq__btiz)))
    djdra__euf += '  table_total = arr_info_list_to_table(info_list_total)\n'
    djdra__euf += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(yrq__btiz))
    for sfzfm__swbe in range(yrq__btiz):
        djdra__euf += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(sfzfm__swbe, sfzfm__swbe, sfzfm__swbe))
    djdra__euf += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(yrq__btiz))
    djdra__euf += '  delete_table(out_table)\n'
    djdra__euf += '  delete_table(table_total)\n'
    djdra__euf += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(yrq__btiz)))
    vcdm__rhp = {}
    exec(djdra__euf, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'sample_table': sample_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, vcdm__rhp)
    impl = vcdm__rhp['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    yrq__btiz = len(data)
    djdra__euf = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    djdra__euf += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        yrq__btiz)))
    djdra__euf += '  table_total = arr_info_list_to_table(info_list_total)\n'
    djdra__euf += '  keep_i = 0\n'
    djdra__euf += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False)
"""
    for sfzfm__swbe in range(yrq__btiz):
        djdra__euf += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(sfzfm__swbe, sfzfm__swbe, sfzfm__swbe))
    djdra__euf += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(yrq__btiz))
    djdra__euf += '  delete_table(out_table)\n'
    djdra__euf += '  delete_table(table_total)\n'
    djdra__euf += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(yrq__btiz)))
    vcdm__rhp = {}
    exec(djdra__euf, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, vcdm__rhp)
    impl = vcdm__rhp['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        bnno__cmkke = [array_to_info(data_arr)]
        ryxky__eavw = arr_info_list_to_table(bnno__cmkke)
        hmque__amn = 0
        ehfig__rhau = drop_duplicates_table(ryxky__eavw, parallel, 1,
            hmque__amn, False)
        fln__rwvbj = info_to_array(info_from_table(ehfig__rhau, 0), data_arr)
        delete_table(ehfig__rhau)
        delete_table(ryxky__eavw)
        return fln__rwvbj
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    kgle__bkz = len(data.types)
    vnbc__zbowz = [('out' + str(i)) for i in range(kgle__bkz)]
    gjym__nmfyn = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    hmb__dlowu = ['isna(data[{}], i)'.format(i) for i in gjym__nmfyn]
    cqaf__seiva = 'not ({})'.format(' or '.join(hmb__dlowu))
    if not is_overload_none(thresh):
        cqaf__seiva = '(({}) <= ({}) - thresh)'.format(' + '.join(
            hmb__dlowu), kgle__bkz - 1)
    elif how == 'all':
        cqaf__seiva = 'not ({})'.format(' and '.join(hmb__dlowu))
    djdra__euf = 'def _dropna_imp(data, how, thresh, subset):\n'
    djdra__euf += '  old_len = len(data[0])\n'
    djdra__euf += '  new_len = 0\n'
    djdra__euf += '  for i in range(old_len):\n'
    djdra__euf += '    if {}:\n'.format(cqaf__seiva)
    djdra__euf += '      new_len += 1\n'
    for i, out in enumerate(vnbc__zbowz):
        if isinstance(data[i], bodo.CategoricalArrayType):
            djdra__euf += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            djdra__euf += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    djdra__euf += '  curr_ind = 0\n'
    djdra__euf += '  for i in range(old_len):\n'
    djdra__euf += '    if {}:\n'.format(cqaf__seiva)
    for i in range(kgle__bkz):
        djdra__euf += '      if isna(data[{}], i):\n'.format(i)
        djdra__euf += '        setna({}, curr_ind)\n'.format(vnbc__zbowz[i])
        djdra__euf += '      else:\n'
        djdra__euf += '        {}[curr_ind] = data[{}][i]\n'.format(vnbc__zbowz
            [i], i)
    djdra__euf += '      curr_ind += 1\n'
    djdra__euf += '  return {}\n'.format(', '.join(vnbc__zbowz))
    vcdm__rhp = {}
    kbkpi__wcjo = {'t{}'.format(i): fbmqj__zjc for i, fbmqj__zjc in
        enumerate(data.types)}
    kbkpi__wcjo.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(djdra__euf, kbkpi__wcjo, vcdm__rhp)
    dnrru__vcaw = vcdm__rhp['_dropna_imp']
    return dnrru__vcaw


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        foa__zdxzz = arr.dtype
        osgo__sayl = foa__zdxzz.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            nutet__izz = init_nested_counts(osgo__sayl)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                nutet__izz = add_nested_counts(nutet__izz, val[ind])
            fln__rwvbj = bodo.utils.utils.alloc_type(n, foa__zdxzz, nutet__izz)
            for bxweo__pkyw in range(n):
                if bodo.libs.array_kernels.isna(arr, bxweo__pkyw):
                    setna(fln__rwvbj, bxweo__pkyw)
                    continue
                val = arr[bxweo__pkyw]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(fln__rwvbj, bxweo__pkyw)
                    continue
                fln__rwvbj[bxweo__pkyw] = val[ind]
            return fln__rwvbj
        return get_arr_item


def concat(arr_list):
    return pd.concat(arr_list)


@overload(concat, no_unliteral=True)
def concat_overload(arr_list):
    if isinstance(arr_list, bodo.NullableTupleType):
        return lambda arr_list: bodo.libs.array_kernels.concat(arr_list._data)
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, ArrayItemArrayType):
        unclp__cfa = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            nxk__smzrl = 0
            ueng__rzosm = []
            for A in arr_list:
                srlip__dyw = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                ueng__rzosm.append(bodo.libs.array_item_arr_ext.get_data(A))
                nxk__smzrl += srlip__dyw
            kin__yingb = np.empty(nxk__smzrl + 1, offset_type)
            cwgtk__mxj = bodo.libs.array_kernels.concat(ueng__rzosm)
            jqq__jrn = np.empty(nxk__smzrl + 7 >> 3, np.uint8)
            ixp__alw = 0
            dkj__xeya = 0
            for A in arr_list:
                qesw__irxy = bodo.libs.array_item_arr_ext.get_offsets(A)
                gmxzo__suj = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                srlip__dyw = len(A)
                sdhyh__ybxbp = qesw__irxy[srlip__dyw]
                for i in range(srlip__dyw):
                    kin__yingb[i + ixp__alw] = qesw__irxy[i] + dkj__xeya
                    vpqgh__pmw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        gmxzo__suj, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(jqq__jrn, i +
                        ixp__alw, vpqgh__pmw)
                ixp__alw += srlip__dyw
                dkj__xeya += sdhyh__ybxbp
            kin__yingb[ixp__alw] = dkj__xeya
            fln__rwvbj = bodo.libs.array_item_arr_ext.init_array_item_array(
                nxk__smzrl, cwgtk__mxj, kin__yingb, jqq__jrn)
            return fln__rwvbj
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        lyeoy__gpyj = arr_list.dtype.names
        djdra__euf = 'def struct_array_concat_impl(arr_list):\n'
        djdra__euf += f'    n_all = 0\n'
        for i in range(len(lyeoy__gpyj)):
            djdra__euf += f'    concat_list{i} = []\n'
        djdra__euf += '    for A in arr_list:\n'
        djdra__euf += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(lyeoy__gpyj)):
            djdra__euf += f'        concat_list{i}.append(data_tuple[{i}])\n'
        djdra__euf += '        n_all += len(A)\n'
        djdra__euf += '    n_bytes = (n_all + 7) >> 3\n'
        djdra__euf += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        djdra__euf += '    curr_bit = 0\n'
        djdra__euf += '    for A in arr_list:\n'
        djdra__euf += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        djdra__euf += '        for j in range(len(A)):\n'
        djdra__euf += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        djdra__euf += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        djdra__euf += '            curr_bit += 1\n'
        djdra__euf += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        ospg__glt = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(lyeoy__gpyj))])
        djdra__euf += f'        ({ospg__glt},),\n'
        djdra__euf += '        new_mask,\n'
        djdra__euf += f'        {lyeoy__gpyj},\n'
        djdra__euf += '    )\n'
        vcdm__rhp = {}
        exec(djdra__euf, {'bodo': bodo, 'np': np}, vcdm__rhp)
        return vcdm__rhp['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            veaa__amw = 0
            for A in arr_list:
                veaa__amw += len(A)
            bjtb__akqxh = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(veaa__amw))
            fxp__oht = 0
            for A in arr_list:
                for i in range(len(A)):
                    bjtb__akqxh._data[i + fxp__oht] = A._data[i]
                    vpqgh__pmw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(bjtb__akqxh.
                        _null_bitmap, i + fxp__oht, vpqgh__pmw)
                fxp__oht += len(A)
            return bjtb__akqxh
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            veaa__amw = 0
            for A in arr_list:
                veaa__amw += len(A)
            bjtb__akqxh = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(veaa__amw))
            fxp__oht = 0
            for A in arr_list:
                for i in range(len(A)):
                    bjtb__akqxh._days_data[i + fxp__oht] = A._days_data[i]
                    bjtb__akqxh._seconds_data[i + fxp__oht] = A._seconds_data[i
                        ]
                    bjtb__akqxh._microseconds_data[i + fxp__oht
                        ] = A._microseconds_data[i]
                    vpqgh__pmw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(bjtb__akqxh.
                        _null_bitmap, i + fxp__oht, vpqgh__pmw)
                fxp__oht += len(A)
            return bjtb__akqxh
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        sjwv__mri = arr_list.dtype.precision
        gwh__rhtmc = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            veaa__amw = 0
            for A in arr_list:
                veaa__amw += len(A)
            bjtb__akqxh = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                veaa__amw, sjwv__mri, gwh__rhtmc)
            fxp__oht = 0
            for A in arr_list:
                for i in range(len(A)):
                    bjtb__akqxh._data[i + fxp__oht] = A._data[i]
                    vpqgh__pmw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(bjtb__akqxh.
                        _null_bitmap, i + fxp__oht, vpqgh__pmw)
                fxp__oht += len(A)
            return bjtb__akqxh
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype in [string_array_type, bodo.binary_array_type]:
        if arr_list.dtype == bodo.binary_array_type:
            egudr__evtq = 'bodo.libs.str_arr_ext.pre_alloc_binary_array'
        elif arr_list.dtype == string_array_type:
            egudr__evtq = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        djdra__euf = 'def impl(arr_list):  # pragma: no cover\n'
        djdra__euf += '    # preallocate the output\n'
        djdra__euf += '    num_strs = 0\n'
        djdra__euf += '    num_chars = 0\n'
        djdra__euf += '    for A in arr_list:\n'
        djdra__euf += '        arr = A\n'
        djdra__euf += '        num_strs += len(arr)\n'
        djdra__euf += '        # this should work for both binary and string\n'
        djdra__euf += (
            '        num_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n'
            )
        djdra__euf += f'    out_arr = {egudr__evtq}(\n'
        djdra__euf += '        num_strs, num_chars\n'
        djdra__euf += '    )\n'
        djdra__euf += (
            '    bodo.libs.str_arr_ext.set_null_bits_to_value(out_arr, -1)\n')
        djdra__euf += '    # copy data to output\n'
        djdra__euf += '    curr_str_ind = 0\n'
        djdra__euf += '    curr_chars_ind = 0\n'
        djdra__euf += '    for A in arr_list:\n'
        djdra__euf += '        arr = A\n'
        djdra__euf += '        # This will probably need to be extended\n'
        djdra__euf += '        bodo.libs.str_arr_ext.set_string_array_range(\n'
        djdra__euf += (
            '            out_arr, arr, curr_str_ind, curr_chars_ind\n')
        djdra__euf += '        )\n'
        djdra__euf += '        curr_str_ind += len(arr)\n'
        djdra__euf += '        # this should work for both binary and string\n'
        djdra__euf += (
            '        curr_chars_ind += bodo.libs.str_arr_ext.num_total_chars(arr)\n'
            )
        djdra__euf += '    return out_arr\n'
        ownsu__tzxr = dict()
        exec(djdra__euf, {'bodo': bodo}, ownsu__tzxr)
        uqxn__vyzhk = ownsu__tzxr['impl']
        return uqxn__vyzhk
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(fbmqj__zjc.dtype, types.Integer) for
        fbmqj__zjc in arr_list.types) and any(isinstance(fbmqj__zjc,
        IntegerArrayType) for fbmqj__zjc in arr_list.types):

        def impl_int_arr_list(arr_list):
            nrpe__xlrn = convert_to_nullable_tup(arr_list)
            vhtz__mfttf = []
            ibwh__vwfri = 0
            for A in nrpe__xlrn:
                vhtz__mfttf.append(A._data)
                ibwh__vwfri += len(A)
            cwgtk__mxj = bodo.libs.array_kernels.concat(vhtz__mfttf)
            wjxrp__jaj = ibwh__vwfri + 7 >> 3
            ggj__ist = np.empty(wjxrp__jaj, np.uint8)
            mrd__ozws = 0
            for A in nrpe__xlrn:
                qtmy__vjl = A._null_bitmap
                for bxweo__pkyw in range(len(A)):
                    vpqgh__pmw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        qtmy__vjl, bxweo__pkyw)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ggj__ist,
                        mrd__ozws, vpqgh__pmw)
                    mrd__ozws += 1
            return bodo.libs.int_arr_ext.init_integer_array(cwgtk__mxj,
                ggj__ist)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(fbmqj__zjc.dtype == types.bool_ for fbmqj__zjc in
        arr_list.types) and any(fbmqj__zjc == boolean_array for fbmqj__zjc in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            nrpe__xlrn = convert_to_nullable_tup(arr_list)
            vhtz__mfttf = []
            ibwh__vwfri = 0
            for A in nrpe__xlrn:
                vhtz__mfttf.append(A._data)
                ibwh__vwfri += len(A)
            cwgtk__mxj = bodo.libs.array_kernels.concat(vhtz__mfttf)
            wjxrp__jaj = ibwh__vwfri + 7 >> 3
            ggj__ist = np.empty(wjxrp__jaj, np.uint8)
            mrd__ozws = 0
            for A in nrpe__xlrn:
                qtmy__vjl = A._null_bitmap
                for bxweo__pkyw in range(len(A)):
                    vpqgh__pmw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        qtmy__vjl, bxweo__pkyw)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ggj__ist,
                        mrd__ozws, vpqgh__pmw)
                    mrd__ozws += 1
            return bodo.libs.bool_arr_ext.init_bool_array(cwgtk__mxj, ggj__ist)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            fepyx__uch = []
            for A in arr_list:
                fepyx__uch.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                fepyx__uch), arr_list[0].dtype)
        return cat_array_concat_impl
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            ibwh__vwfri = 0
            for A in arr_list:
                ibwh__vwfri += len(A)
            fln__rwvbj = np.empty(ibwh__vwfri, dtype)
            tdc__pie = 0
            for A in arr_list:
                n = len(A)
                fln__rwvbj[tdc__pie:tdc__pie + n] = A
                tdc__pie += n
            return fln__rwvbj
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(fbmqj__zjc,
        (types.Array, IntegerArrayType)) and isinstance(fbmqj__zjc.dtype,
        types.Integer) for fbmqj__zjc in arr_list.types) and any(isinstance
        (fbmqj__zjc, types.Array) and isinstance(fbmqj__zjc.dtype, types.
        Float) for fbmqj__zjc in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            dkzv__rgkwh = []
            for A in arr_list:
                dkzv__rgkwh.append(A._data)
            rgvwx__sye = bodo.libs.array_kernels.concat(dkzv__rgkwh)
            ppzj__lgo = bodo.libs.map_arr_ext.init_map_arr(rgvwx__sye)
            return ppzj__lgo
        return impl_map_arr_list
    for hefjt__ibhet in arr_list:
        if not isinstance(hefjt__ibhet, types.Array):
            raise_bodo_error('concat of array types {} not supported'.
                format(arr_list))
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(fbmqj__zjc.astype(np.float64) for fbmqj__zjc in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    yrq__btiz = len(arr_tup.types)
    djdra__euf = 'def f(arr_tup):\n'
    djdra__euf += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(yrq__btiz
        )), ',' if yrq__btiz == 1 else '')
    vcdm__rhp = {}
    exec(djdra__euf, {'np': np}, vcdm__rhp)
    mlfvo__ava = vcdm__rhp['f']
    return mlfvo__ava


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    yrq__btiz = len(arr_tup.types)
    tvem__lehva = find_common_np_dtype(arr_tup.types)
    osgo__sayl = None
    bkge__lcce = ''
    if isinstance(tvem__lehva, types.Integer):
        osgo__sayl = bodo.libs.int_arr_ext.IntDtype(tvem__lehva)
        bkge__lcce = '.astype(out_dtype, False)'
    djdra__euf = 'def f(arr_tup):\n'
    djdra__euf += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, bkge__lcce) for i in range(yrq__btiz)), ',' if yrq__btiz ==
        1 else '')
    vcdm__rhp = {}
    exec(djdra__euf, {'bodo': bodo, 'out_dtype': osgo__sayl}, vcdm__rhp)
    muj__arx = vcdm__rhp['f']
    return muj__arx


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, kwis__khm = build_set_seen_na(A)
        return len(s) + int(not dropna and kwis__khm)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        qrzze__shtbo = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        yzgr__ikj = len(qrzze__shtbo)
        return bodo.libs.distributed_api.dist_reduce(yzgr__ikj, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([vwela__pas for vwela__pas in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        tul__psbz = np.finfo(A.dtype(1).dtype).max
    else:
        tul__psbz = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        fln__rwvbj = np.empty(n, A.dtype)
        oxw__xsia = tul__psbz
        for i in range(n):
            oxw__xsia = min(oxw__xsia, A[i])
            fln__rwvbj[i] = oxw__xsia
        return fln__rwvbj
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        tul__psbz = np.finfo(A.dtype(1).dtype).min
    else:
        tul__psbz = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        fln__rwvbj = np.empty(n, A.dtype)
        oxw__xsia = tul__psbz
        for i in range(n):
            oxw__xsia = max(oxw__xsia, A[i])
            fln__rwvbj[i] = oxw__xsia
        return fln__rwvbj
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        kdr__cohex = arr_info_list_to_table([array_to_info(A)])
        vzvq__uvyz = 1
        hmque__amn = 0
        ehfig__rhau = drop_duplicates_table(kdr__cohex, parallel,
            vzvq__uvyz, hmque__amn, dropna)
        fln__rwvbj = info_to_array(info_from_table(ehfig__rhau, 0), A)
        delete_table(kdr__cohex)
        delete_table(ehfig__rhau)
        return fln__rwvbj
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    unclp__cfa = bodo.utils.typing.to_nullable_type(arr.dtype)
    gcif__gtcwe = index_arr
    aizl__apeo = gcif__gtcwe.dtype

    def impl(arr, index_arr):
        n = len(arr)
        nutet__izz = init_nested_counts(unclp__cfa)
        lssr__pmp = init_nested_counts(aizl__apeo)
        for i in range(n):
            tzqjy__msz = index_arr[i]
            if isna(arr, i):
                nutet__izz = (nutet__izz[0] + 1,) + nutet__izz[1:]
                lssr__pmp = add_nested_counts(lssr__pmp, tzqjy__msz)
                continue
            bin__gsay = arr[i]
            if len(bin__gsay) == 0:
                nutet__izz = (nutet__izz[0] + 1,) + nutet__izz[1:]
                lssr__pmp = add_nested_counts(lssr__pmp, tzqjy__msz)
                continue
            nutet__izz = add_nested_counts(nutet__izz, bin__gsay)
            for gpja__aniac in range(len(bin__gsay)):
                lssr__pmp = add_nested_counts(lssr__pmp, tzqjy__msz)
        fln__rwvbj = bodo.utils.utils.alloc_type(nutet__izz[0], unclp__cfa,
            nutet__izz[1:])
        hmeum__bsw = bodo.utils.utils.alloc_type(nutet__izz[0], gcif__gtcwe,
            lssr__pmp)
        dkj__xeya = 0
        for i in range(n):
            if isna(arr, i):
                setna(fln__rwvbj, dkj__xeya)
                hmeum__bsw[dkj__xeya] = index_arr[i]
                dkj__xeya += 1
                continue
            bin__gsay = arr[i]
            sdhyh__ybxbp = len(bin__gsay)
            if sdhyh__ybxbp == 0:
                setna(fln__rwvbj, dkj__xeya)
                hmeum__bsw[dkj__xeya] = index_arr[i]
                dkj__xeya += 1
                continue
            fln__rwvbj[dkj__xeya:dkj__xeya + sdhyh__ybxbp] = bin__gsay
            hmeum__bsw[dkj__xeya:dkj__xeya + sdhyh__ybxbp] = index_arr[i]
            dkj__xeya += sdhyh__ybxbp
        return fln__rwvbj, hmeum__bsw
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert arr == string_array_type
    gcif__gtcwe = index_arr
    aizl__apeo = gcif__gtcwe.dtype

    def impl(arr, pat, n, index_arr):
        pxnkf__gus = pat is not None and len(pat) > 1
        if pxnkf__gus:
            eprfu__qxjls = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        ttj__irt = len(arr)
        eoquc__onkaf = 0
        rzka__oboqk = 0
        lssr__pmp = init_nested_counts(aizl__apeo)
        for i in range(ttj__irt):
            tzqjy__msz = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                eoquc__onkaf += 1
                lssr__pmp = add_nested_counts(lssr__pmp, tzqjy__msz)
                continue
            if pxnkf__gus:
                jyn__drc = eprfu__qxjls.split(arr[i], maxsplit=n)
            else:
                jyn__drc = arr[i].split(pat, n)
            eoquc__onkaf += len(jyn__drc)
            for s in jyn__drc:
                lssr__pmp = add_nested_counts(lssr__pmp, tzqjy__msz)
                rzka__oboqk += bodo.libs.str_arr_ext.get_utf8_size(s)
        fln__rwvbj = bodo.libs.str_arr_ext.pre_alloc_string_array(eoquc__onkaf,
            rzka__oboqk)
        hmeum__bsw = bodo.utils.utils.alloc_type(eoquc__onkaf, gcif__gtcwe,
            lssr__pmp)
        ditib__rotbc = 0
        for bxweo__pkyw in range(ttj__irt):
            if isna(arr, bxweo__pkyw):
                fln__rwvbj[ditib__rotbc] = ''
                bodo.libs.array_kernels.setna(fln__rwvbj, ditib__rotbc)
                hmeum__bsw[ditib__rotbc] = index_arr[bxweo__pkyw]
                ditib__rotbc += 1
                continue
            if pxnkf__gus:
                jyn__drc = eprfu__qxjls.split(arr[bxweo__pkyw], maxsplit=n)
            else:
                jyn__drc = arr[bxweo__pkyw].split(pat, n)
            vhpp__vckt = len(jyn__drc)
            fln__rwvbj[ditib__rotbc:ditib__rotbc + vhpp__vckt] = jyn__drc
            hmeum__bsw[ditib__rotbc:ditib__rotbc + vhpp__vckt] = index_arr[
                bxweo__pkyw]
            ditib__rotbc += vhpp__vckt
        return fln__rwvbj, hmeum__bsw
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
            fln__rwvbj = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                fln__rwvbj[i] = np.nan
            return fln__rwvbj
        return impl_float

    def impl(n, arr):
        numba.parfors.parfor.init_prange()
        fln__rwvbj = bodo.utils.utils.alloc_type(n, arr, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(fln__rwvbj, i)
        return fln__rwvbj
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
    zlj__mel = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            fln__rwvbj = bodo.utils.utils.alloc_type(new_len, zlj__mel)
            bodo.libs.str_arr_ext.str_copy_ptr(fln__rwvbj.ctypes, 0, A.
                ctypes, old_size)
            return fln__rwvbj
        return impl_char

    def impl(A, old_size, new_len):
        fln__rwvbj = bodo.utils.utils.alloc_type(new_len, zlj__mel, (-1,))
        fln__rwvbj[:old_size] = A[:old_size]
        return fln__rwvbj
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    cyuuj__gzwhx = math.ceil((stop - start) / step)
    return int(max(cyuuj__gzwhx, 0))


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
    if any(isinstance(vwela__pas, types.Complex) for vwela__pas in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            fyo__rww = (stop - start) / step
            cyuuj__gzwhx = math.ceil(fyo__rww.real)
            vlj__muir = math.ceil(fyo__rww.imag)
            tjp__lovhn = int(max(min(vlj__muir, cyuuj__gzwhx), 0))
            arr = np.empty(tjp__lovhn, dtype)
            for i in numba.parfors.parfor.internal_prange(tjp__lovhn):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            tjp__lovhn = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(tjp__lovhn, dtype)
            for i in numba.parfors.parfor.internal_prange(tjp__lovhn):
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
        xlb__qwyxn = arr,
        if not inplace:
            xlb__qwyxn = arr.copy(),
        zkwsu__opy = bodo.libs.str_arr_ext.to_list_if_immutable_arr(xlb__qwyxn)
        ukm__wmrjn = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(zkwsu__opy, 0, n, ukm__wmrjn)
        if not ascending:
            bodo.libs.timsort.reverseRange(zkwsu__opy, 0, n, ukm__wmrjn)
        bodo.libs.str_arr_ext.cp_str_list_to_array(xlb__qwyxn, zkwsu__opy)
        return xlb__qwyxn[0]
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
        ppzj__lgo = []
        for i in range(n):
            if A[i]:
                ppzj__lgo.append(i + offset)
        return np.array(ppzj__lgo, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    zlj__mel = element_type(A)
    if zlj__mel == types.unicode_type:
        null_value = '""'
    elif zlj__mel == types.bool_:
        null_value = 'False'
    elif zlj__mel == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif zlj__mel == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    ditib__rotbc = 'i'
    zqcm__mutf = False
    zxhv__vmy = get_overload_const_str(method)
    if zxhv__vmy in ('ffill', 'pad'):
        sjgw__ogozk = 'n'
        send_right = True
    elif zxhv__vmy in ('backfill', 'bfill'):
        sjgw__ogozk = 'n-1, -1, -1'
        send_right = False
        if zlj__mel == types.unicode_type:
            ditib__rotbc = '(n - 1) - i'
            zqcm__mutf = True
    djdra__euf = 'def impl(A, method, parallel=False):\n'
    djdra__euf += '  has_last_value = False\n'
    djdra__euf += f'  last_value = {null_value}\n'
    djdra__euf += '  if parallel:\n'
    djdra__euf += '    rank = bodo.libs.distributed_api.get_rank()\n'
    djdra__euf += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    djdra__euf += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    djdra__euf += '  n = len(A)\n'
    djdra__euf += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    djdra__euf += f'  for i in range({sjgw__ogozk}):\n'
    djdra__euf += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    djdra__euf += (
        f'      bodo.libs.array_kernels.setna(out_arr, {ditib__rotbc})\n')
    djdra__euf += '      continue\n'
    djdra__euf += '    s = A[i]\n'
    djdra__euf += '    if bodo.libs.array_kernels.isna(A, i):\n'
    djdra__euf += '      s = last_value\n'
    djdra__euf += f'    out_arr[{ditib__rotbc}] = s\n'
    djdra__euf += '    last_value = s\n'
    djdra__euf += '    has_last_value = True\n'
    if zqcm__mutf:
        djdra__euf += '  return out_arr[::-1]\n'
    else:
        djdra__euf += '  return out_arr\n'
    znkc__uapr = {}
    exec(djdra__euf, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm}, znkc__uapr)
    impl = znkc__uapr['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        eog__ydn = 0
        fmxol__qgkp = n_pes - 1
        usy__ugu = np.int32(rank + 1)
        yvfdq__nkdkm = np.int32(rank - 1)
        pesf__ryuab = len(in_arr) - 1
        ira__pbco = -1
        phm__atlt = -1
    else:
        eog__ydn = n_pes - 1
        fmxol__qgkp = 0
        usy__ugu = np.int32(rank - 1)
        yvfdq__nkdkm = np.int32(rank + 1)
        pesf__ryuab = 0
        ira__pbco = len(in_arr)
        phm__atlt = 1
    smfhd__trlx = np.int32(bodo.hiframes.rolling.comm_border_tag)
    kguje__zzjhe = np.empty(1, dtype=np.bool_)
    lhtk__xtrx = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    idis__rmdv = np.empty(1, dtype=np.bool_)
    wox__wdbt = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    xsvi__gbvia = False
    thtx__bizll = null_value
    for i in range(pesf__ryuab, ira__pbco, phm__atlt):
        if not isna(in_arr, i):
            xsvi__gbvia = True
            thtx__bizll = in_arr[i]
            break
    if rank != eog__ydn:
        czusc__tsbmk = bodo.libs.distributed_api.irecv(kguje__zzjhe, 1,
            yvfdq__nkdkm, smfhd__trlx, True)
        bodo.libs.distributed_api.wait(czusc__tsbmk, True)
        imksc__eiy = bodo.libs.distributed_api.irecv(lhtk__xtrx, 1,
            yvfdq__nkdkm, smfhd__trlx, True)
        bodo.libs.distributed_api.wait(imksc__eiy, True)
        xeo__ihcgt = kguje__zzjhe[0]
        vkth__roc = lhtk__xtrx[0]
    else:
        xeo__ihcgt = False
        vkth__roc = null_value
    if xsvi__gbvia:
        idis__rmdv[0] = xsvi__gbvia
        wox__wdbt[0] = thtx__bizll
    else:
        idis__rmdv[0] = xeo__ihcgt
        wox__wdbt[0] = vkth__roc
    if rank != fmxol__qgkp:
        ain__qibh = bodo.libs.distributed_api.isend(idis__rmdv, 1, usy__ugu,
            smfhd__trlx, True)
        jhgut__ovvt = bodo.libs.distributed_api.isend(wox__wdbt, 1,
            usy__ugu, smfhd__trlx, True)
    return xeo__ihcgt, vkth__roc


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    foxyj__gtcm = {'axis': axis, 'kind': kind, 'order': order}
    jdfn__hztjb = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', foxyj__gtcm, jdfn__hztjb, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    zlj__mel = A
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            ttj__irt = len(A)
            fln__rwvbj = bodo.utils.utils.alloc_type(ttj__irt * repeats,
                zlj__mel, (-1,))
            for i in range(ttj__irt):
                ditib__rotbc = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for bxweo__pkyw in range(repeats):
                        bodo.libs.array_kernels.setna(fln__rwvbj, 
                            ditib__rotbc + bxweo__pkyw)
                else:
                    fln__rwvbj[ditib__rotbc:ditib__rotbc + repeats] = A[i]
            return fln__rwvbj
        return impl_int

    def impl_arr(A, repeats):
        ttj__irt = len(A)
        fln__rwvbj = bodo.utils.utils.alloc_type(repeats.sum(), zlj__mel, (-1,)
            )
        ditib__rotbc = 0
        for i in range(ttj__irt):
            amp__bvla = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for bxweo__pkyw in range(amp__bvla):
                    bodo.libs.array_kernels.setna(fln__rwvbj, ditib__rotbc +
                        bxweo__pkyw)
            else:
                fln__rwvbj[ditib__rotbc:ditib__rotbc + amp__bvla] = A[i]
            ditib__rotbc += amp__bvla
        return fln__rwvbj
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
        tivfo__lswy = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(tivfo__lswy, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        kzv__xgems = bodo.libs.array_kernels.concat([A1, A2])
        zupy__mzre = bodo.libs.array_kernels.unique(kzv__xgems)
        return pd.Series(zupy__mzre).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    foxyj__gtcm = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    jdfn__hztjb = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', foxyj__gtcm, jdfn__hztjb, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        ari__ujk = bodo.libs.array_kernels.unique(A1)
        fwo__oabec = bodo.libs.array_kernels.unique(A2)
        kzv__xgems = bodo.libs.array_kernels.concat([ari__ujk, fwo__oabec])
        sezs__mpdu = pd.Series(kzv__xgems).sort_values().values
        return slice_array_intersect1d(sezs__mpdu)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    tlgti__njn = arr[1:] == arr[:-1]
    return arr[:-1][tlgti__njn]


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    foxyj__gtcm = {'assume_unique': assume_unique}
    jdfn__hztjb = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', foxyj__gtcm, jdfn__hztjb, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        ari__ujk = bodo.libs.array_kernels.unique(A1)
        fwo__oabec = bodo.libs.array_kernels.unique(A2)
        tlgti__njn = calculate_mask_setdiff1d(ari__ujk, fwo__oabec)
        return pd.Series(ari__ujk[tlgti__njn]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    tlgti__njn = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        tlgti__njn &= A1 != A2[i]
    return tlgti__njn


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    foxyj__gtcm = {'retstep': retstep, 'axis': axis}
    jdfn__hztjb = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', foxyj__gtcm, jdfn__hztjb, 'numpy')
    tiyq__tmz = False
    if is_overload_none(dtype):
        zlj__mel = np.promote_types(np.promote_types(numba.np.numpy_support
            .as_dtype(start), numba.np.numpy_support.as_dtype(stop)), numba
            .np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            tiyq__tmz = True
        zlj__mel = numba.np.numpy_support.as_dtype(dtype).type
    if tiyq__tmz:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            crttx__yui = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            fln__rwvbj = np.empty(num, zlj__mel)
            for i in numba.parfors.parfor.internal_prange(num):
                fln__rwvbj[i] = zlj__mel(np.floor(start + i * crttx__yui))
            return fln__rwvbj
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            crttx__yui = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            fln__rwvbj = np.empty(num, zlj__mel)
            for i in numba.parfors.parfor.internal_prange(num):
                fln__rwvbj[i] = zlj__mel(start + i * crttx__yui)
            return fln__rwvbj
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
        yrq__btiz = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                yrq__btiz += A[i] == val
        return yrq__btiz > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    foxyj__gtcm = {'axis': axis, 'out': out, 'keepdims': keepdims}
    jdfn__hztjb = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', foxyj__gtcm, jdfn__hztjb, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        yrq__btiz = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                yrq__btiz += int(bool(A[i]))
        return yrq__btiz > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    foxyj__gtcm = {'axis': axis, 'out': out, 'keepdims': keepdims}
    jdfn__hztjb = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', foxyj__gtcm, jdfn__hztjb, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        yrq__btiz = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                yrq__btiz += int(bool(A[i]))
        return yrq__btiz == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    foxyj__gtcm = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    jdfn__hztjb = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', foxyj__gtcm, jdfn__hztjb, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        zbhv__bvcz = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            fln__rwvbj = np.empty(n, zbhv__bvcz)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(fln__rwvbj, i)
                    continue
                fln__rwvbj[i] = np_cbrt_scalar(A[i], zbhv__bvcz)
            return fln__rwvbj
        return impl_arr
    zbhv__bvcz = np.promote_types(numba.np.numpy_support.as_dtype(A), numba
        .np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, zbhv__bvcz)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    ejxr__wjt = x < 0
    if ejxr__wjt:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if ejxr__wjt:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    xhb__rrbkm = isinstance(tup, (types.BaseTuple, types.List))
    ardrc__dkhad = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for hefjt__ibhet in tup.types:
            xhb__rrbkm = xhb__rrbkm and bodo.utils.utils.is_array_typ(
                hefjt__ibhet, False)
    elif isinstance(tup, types.List):
        xhb__rrbkm = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif ardrc__dkhad:
        oaaq__yvzn = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for hefjt__ibhet in oaaq__yvzn.types:
            ardrc__dkhad = ardrc__dkhad and bodo.utils.utils.is_array_typ(
                hefjt__ibhet, False)
    if not (xhb__rrbkm or ardrc__dkhad):
        return
    if ardrc__dkhad:

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
    foxyj__gtcm = {'check_valid': check_valid, 'tol': tol}
    jdfn__hztjb = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', foxyj__gtcm,
        jdfn__hztjb, 'numpy')
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
        bsp__htlrx = mean.shape[0]
        czmck__bwrr = size, bsp__htlrx
        mkyin__frt = np.random.standard_normal(czmck__bwrr)
        cov = cov.astype(np.float64)
        ogb__uja, s, yca__guas = np.linalg.svd(cov)
        res = np.dot(mkyin__frt, np.sqrt(s).reshape(bsp__htlrx, 1) * yca__guas)
        ncg__ikmrv = res + mean
        return ncg__ikmrv
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
            mdhxm__xzqq = bodo.hiframes.series_kernels._get_type_max_value(arr)
            rztuw__dere = typing.builtins.IndexValue(-1, mdhxm__xzqq)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                qmml__fcfn = typing.builtins.IndexValue(i, arr[i])
                rztuw__dere = min(rztuw__dere, qmml__fcfn)
            return rztuw__dere.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        dxy__gcs = bodo.hiframes.pd_categorical_ext.get_categories_int_type(arr
            .dtype)

        def impl_cat_arr(arr):
            prkm__xoxcg = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            mdhxm__xzqq = dxy__gcs(len(arr.dtype.categories) + 1)
            rztuw__dere = typing.builtins.IndexValue(-1, mdhxm__xzqq)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                qmml__fcfn = typing.builtins.IndexValue(i, prkm__xoxcg[i])
                rztuw__dere = min(rztuw__dere, qmml__fcfn)
            return rztuw__dere.index
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
            mdhxm__xzqq = bodo.hiframes.series_kernels._get_type_min_value(arr)
            rztuw__dere = typing.builtins.IndexValue(-1, mdhxm__xzqq)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                qmml__fcfn = typing.builtins.IndexValue(i, arr[i])
                rztuw__dere = max(rztuw__dere, qmml__fcfn)
            return rztuw__dere.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        dxy__gcs = bodo.hiframes.pd_categorical_ext.get_categories_int_type(arr
            .dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            prkm__xoxcg = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            mdhxm__xzqq = dxy__gcs(-1)
            rztuw__dere = typing.builtins.IndexValue(-1, mdhxm__xzqq)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                qmml__fcfn = typing.builtins.IndexValue(i, prkm__xoxcg[i])
                rztuw__dere = max(rztuw__dere, qmml__fcfn)
            return rztuw__dere.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
