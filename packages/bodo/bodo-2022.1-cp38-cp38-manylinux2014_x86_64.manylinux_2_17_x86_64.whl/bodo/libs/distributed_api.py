import atexit
import datetime
import operator
import sys
import time
import warnings
from collections import defaultdict
from decimal import Decimal
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from mpi4py import MPI
from numba.core import cgutils, ir_utils, types
from numba.core.typing import signature
from numba.core.typing.builtins import IndexValueType
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, models, overload, register_jitable, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.libs import hdist
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType, set_bit_to_arr
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import convert_len_arr_to_offset, get_bit_bitmap, get_data_ptr, get_null_bitmap_ptr, get_offset_ptr, num_total_chars, pre_alloc_string_array, set_bit_to, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoError, BodoWarning, is_overload_false, is_overload_none, raise_bodo_error
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, empty_like_type, numba_to_c_type, tuple_to_scalar
ll.add_symbol('dist_get_time', hdist.dist_get_time)
ll.add_symbol('get_time', hdist.get_time)
ll.add_symbol('dist_reduce', hdist.dist_reduce)
ll.add_symbol('dist_arr_reduce', hdist.dist_arr_reduce)
ll.add_symbol('dist_exscan', hdist.dist_exscan)
ll.add_symbol('dist_irecv', hdist.dist_irecv)
ll.add_symbol('dist_isend', hdist.dist_isend)
ll.add_symbol('dist_wait', hdist.dist_wait)
ll.add_symbol('dist_get_item_pointer', hdist.dist_get_item_pointer)
ll.add_symbol('get_dummy_ptr', hdist.get_dummy_ptr)
ll.add_symbol('allgather', hdist.allgather)
ll.add_symbol('comm_req_alloc', hdist.comm_req_alloc)
ll.add_symbol('comm_req_dealloc', hdist.comm_req_dealloc)
ll.add_symbol('req_array_setitem', hdist.req_array_setitem)
ll.add_symbol('dist_waitall', hdist.dist_waitall)
ll.add_symbol('oneD_reshape_shuffle', hdist.oneD_reshape_shuffle)
ll.add_symbol('permutation_int', hdist.permutation_int)
ll.add_symbol('permutation_array_index', hdist.permutation_array_index)
ll.add_symbol('c_get_rank', hdist.dist_get_rank)
ll.add_symbol('c_get_size', hdist.dist_get_size)
ll.add_symbol('c_barrier', hdist.barrier)
ll.add_symbol('c_alltoall', hdist.c_alltoall)
ll.add_symbol('c_gather_scalar', hdist.c_gather_scalar)
ll.add_symbol('c_gatherv', hdist.c_gatherv)
ll.add_symbol('c_scatterv', hdist.c_scatterv)
ll.add_symbol('c_allgatherv', hdist.c_allgatherv)
ll.add_symbol('c_bcast', hdist.c_bcast)
ll.add_symbol('c_recv', hdist.dist_recv)
ll.add_symbol('c_send', hdist.dist_send)
mpi_req_numba_type = getattr(types, 'int' + str(8 * hdist.mpi_req_num_bytes))
MPI_ROOT = 0
ANY_SOURCE = np.int32(hdist.ANY_SOURCE)


class Reduce_Type(Enum):
    Sum = 0
    Prod = 1
    Min = 2
    Max = 3
    Argmin = 4
    Argmax = 5
    Or = 6
    Concat = 7
    No_Op = 8


_get_rank = types.ExternalFunction('c_get_rank', types.int32())
_get_size = types.ExternalFunction('c_get_size', types.int32())
_barrier = types.ExternalFunction('c_barrier', types.int32())


@numba.njit
def get_rank():
    return _get_rank()


@numba.njit
def get_size():
    return _get_size()


@numba.njit
def barrier():
    _barrier()


_get_time = types.ExternalFunction('get_time', types.float64())
dist_time = types.ExternalFunction('dist_get_time', types.float64())


@overload(time.time, no_unliteral=True)
def overload_time_time():
    return lambda : _get_time()


@numba.generated_jit(nopython=True)
def get_type_enum(arr):
    arr = arr.instance_type if isinstance(arr, types.TypeRef) else arr
    dtype = arr.dtype
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = bodo.hiframes.pd_categorical_ext.get_categories_int_type(dtype)
    typ_val = numba_to_c_type(dtype)
    return lambda arr: np.int32(typ_val)


INT_MAX = np.iinfo(np.int32).max
_send = types.ExternalFunction('c_send', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def send(val, rank, tag):
    send_arr = np.full(1, val)
    avmm__olzf = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, avmm__olzf, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    avmm__olzf = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, avmm__olzf, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            avmm__olzf = get_type_enum(arr)
            return _isend(arr.ctypes, size, avmm__olzf, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        avmm__olzf = np.int32(numba_to_c_type(arr.dtype))
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            qponu__ujzz = size + 7 >> 3
            osht__wcnqs = _isend(arr._data.ctypes, size, avmm__olzf, pe,
                tag, cond)
            dcc__ljdlt = _isend(arr._null_bitmap.ctypes, qponu__ujzz,
                jcjlx__exrnx, pe, tag, cond)
            return osht__wcnqs, dcc__ljdlt
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        vkn__qwm = np.int32(numba_to_c_type(offset_type))
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            cvulc__ftrej = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(cvulc__ftrej, pe, tag - 1)
            qponu__ujzz = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                vkn__qwm, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), cvulc__ftrej,
                jcjlx__exrnx, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                qponu__ujzz, jcjlx__exrnx, pe, tag)
            return None
        return impl_str_arr
    typ_enum = numba_to_c_type(types.uint8)

    def impl_voidptr(arr, size, pe, tag, cond=True):
        return _isend(arr, size, typ_enum, pe, tag, cond)
    return impl_voidptr


_irecv = types.ExternalFunction('dist_irecv', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def irecv(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            avmm__olzf = get_type_enum(arr)
            return _irecv(arr.ctypes, size, avmm__olzf, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        avmm__olzf = np.int32(numba_to_c_type(arr.dtype))
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            qponu__ujzz = size + 7 >> 3
            osht__wcnqs = _irecv(arr._data.ctypes, size, avmm__olzf, pe,
                tag, cond)
            dcc__ljdlt = _irecv(arr._null_bitmap.ctypes, qponu__ujzz,
                jcjlx__exrnx, pe, tag, cond)
            return osht__wcnqs, dcc__ljdlt
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        vkn__qwm = np.int32(numba_to_c_type(offset_type))
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            avx__gfn = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            avx__gfn = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        vqu__ybq = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {avx__gfn}(size, n_chars)
            bodo.libs.str_arr_ext.move_str_binary_arr_payload(arr, new_arr)

            n_bytes = (size + 7) >> 3
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_offset_ptr(arr),
                size + 1,
                offset_typ_enum,
                pe,
                tag,
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_data_ptr(arr), n_chars, char_typ_enum, pe, tag
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                n_bytes,
                char_typ_enum,
                pe,
                tag,
            )
            return None"""
        ygt__pqzah = dict()
        exec(vqu__ybq, {'bodo': bodo, 'np': np, 'offset_typ_enum': vkn__qwm,
            'char_typ_enum': jcjlx__exrnx}, ygt__pqzah)
        impl = ygt__pqzah['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    avmm__olzf = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), avmm__olzf)


@numba.generated_jit(nopython=True)
def gather_scalar(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    data = types.unliteral(data)
    typ_val = numba_to_c_type(data)
    dtype = data

    def gather_scalar_impl(data, allgather=False, warn_if_rep=True, root=
        MPI_ROOT):
        n_pes = bodo.libs.distributed_api.get_size()
        rank = bodo.libs.distributed_api.get_rank()
        send = np.full(1, data, dtype)
        whlta__qyyqr = n_pes if rank == root or allgather else 0
        gaod__bazm = np.empty(whlta__qyyqr, dtype)
        c_gather_scalar(send.ctypes, gaod__bazm.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return gaod__bazm
    return gather_scalar_impl


c_gather_scalar = types.ExternalFunction('c_gather_scalar', types.void(
    types.voidptr, types.voidptr, types.int32, types.bool_, types.int32))
c_gatherv = types.ExternalFunction('c_gatherv', types.void(types.voidptr,
    types.int32, types.voidptr, types.voidptr, types.voidptr, types.int32,
    types.bool_, types.int32))
c_scatterv = types.ExternalFunction('c_scatterv', types.void(types.voidptr,
    types.voidptr, types.voidptr, types.voidptr, types.int32, types.int32))


@intrinsic
def value_to_ptr(typingctx, val_tp=None):

    def codegen(context, builder, sig, args):
        ezj__pbd = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], ezj__pbd)
        return builder.bitcast(ezj__pbd, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        ezj__pbd = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(ezj__pbd)
    return val_tp(ptr_tp, val_tp), codegen


_dist_reduce = types.ExternalFunction('dist_reduce', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))
_dist_arr_reduce = types.ExternalFunction('dist_arr_reduce', types.void(
    types.voidptr, types.int64, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_reduce(value, reduce_op):
    if isinstance(value, types.Array):
        typ_enum = np.int32(numba_to_c_type(value.dtype))

        def impl_arr(value, reduce_op):
            A = np.ascontiguousarray(value)
            _dist_arr_reduce(A.ctypes, A.size, reduce_op, typ_enum)
            return A
        return impl_arr
    cifg__mvfe = types.unliteral(value)
    if isinstance(cifg__mvfe, IndexValueType):
        cifg__mvfe = cifg__mvfe.val_typ
        lgzf__bkoin = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            lgzf__bkoin.append(types.int64)
            lgzf__bkoin.append(bodo.datetime64ns)
            lgzf__bkoin.append(bodo.timedelta64ns)
            lgzf__bkoin.append(bodo.datetime_date_type)
        if cifg__mvfe not in lgzf__bkoin:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(cifg__mvfe))
    typ_enum = np.int32(numba_to_c_type(cifg__mvfe))

    def impl(value, reduce_op):
        avzt__exw = value_to_ptr(value)
        ljbh__ojm = value_to_ptr(value)
        _dist_reduce(avzt__exw, ljbh__ojm, reduce_op, typ_enum)
        return load_val_ptr(ljbh__ojm, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    cifg__mvfe = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(cifg__mvfe))
    tsjsc__cyi = cifg__mvfe(0)

    def impl(value, reduce_op):
        avzt__exw = value_to_ptr(value)
        ljbh__ojm = value_to_ptr(tsjsc__cyi)
        _dist_exscan(avzt__exw, ljbh__ojm, reduce_op, typ_enum)
        return load_val_ptr(ljbh__ojm, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    qsax__avcm = 0
    syu__kbi = 0
    for i in range(len(recv_counts)):
        xay__gpw = recv_counts[i]
        qponu__ujzz = recv_counts_nulls[i]
        xhqm__qjcd = tmp_null_bytes[qsax__avcm:qsax__avcm + qponu__ujzz]
        for lmys__ezpnp in range(xay__gpw):
            set_bit_to(null_bitmap_ptr, syu__kbi, get_bit(xhqm__qjcd,
                lmys__ezpnp))
            syu__kbi += 1
        qsax__avcm += qponu__ujzz


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            awv__qmq = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                awv__qmq, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            apy__wni = data.size
            recv_counts = gather_scalar(np.int32(apy__wni), allgather, root
                =root)
            jjcfo__zdhfa = recv_counts.sum()
            opvsb__umoj = empty_like_type(jjcfo__zdhfa, data)
            olx__xsll = np.empty(1, np.int32)
            if rank == root or allgather:
                olx__xsll = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(apy__wni), opvsb__umoj.ctypes,
                recv_counts.ctypes, olx__xsll.ctypes, np.int32(typ_val),
                allgather, np.int32(root))
            return opvsb__umoj.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if data == string_array_type:

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            opvsb__umoj = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.str_arr_ext.init_str_arr(opvsb__umoj)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            opvsb__umoj = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.binary_arr_ext.init_binary_arr(opvsb__umoj)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            apy__wni = len(data)
            qponu__ujzz = apy__wni + 7 >> 3
            recv_counts = gather_scalar(np.int32(apy__wni), allgather, root
                =root)
            jjcfo__zdhfa = recv_counts.sum()
            opvsb__umoj = empty_like_type(jjcfo__zdhfa, data)
            olx__xsll = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            ulqw__suu = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                olx__xsll = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                ulqw__suu = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(apy__wni),
                opvsb__umoj._days_data.ctypes, recv_counts.ctypes,
                olx__xsll.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._seconds_data.ctypes, np.int32(apy__wni),
                opvsb__umoj._seconds_data.ctypes, recv_counts.ctypes,
                olx__xsll.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._microseconds_data.ctypes, np.int32(apy__wni),
                opvsb__umoj._microseconds_data.ctypes, recv_counts.ctypes,
                olx__xsll.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(qponu__ujzz),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, ulqw__suu.
                ctypes, jcjlx__exrnx, allgather, np.int32(root))
            copy_gathered_null_bytes(opvsb__umoj._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return opvsb__umoj
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            apy__wni = len(data)
            qponu__ujzz = apy__wni + 7 >> 3
            recv_counts = gather_scalar(np.int32(apy__wni), allgather, root
                =root)
            jjcfo__zdhfa = recv_counts.sum()
            opvsb__umoj = empty_like_type(jjcfo__zdhfa, data)
            olx__xsll = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            ulqw__suu = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                olx__xsll = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                ulqw__suu = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(apy__wni), opvsb__umoj.
                _data.ctypes, recv_counts.ctypes, olx__xsll.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(qponu__ujzz),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, ulqw__suu.
                ctypes, jcjlx__exrnx, allgather, np.int32(root))
            copy_gathered_null_bytes(opvsb__umoj._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return opvsb__umoj
        return gatherv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            wprff__cufm = bodo.gatherv(data._left, allgather, warn_if_rep, root
                )
            kzt__gij = bodo.gatherv(data._right, allgather, warn_if_rep, root)
            return bodo.libs.interval_arr_ext.init_interval_array(wprff__cufm,
                kzt__gij)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            pjtaq__lhvhc = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            mpl__gado = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                mpl__gado, pjtaq__lhvhc)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        kao__ivwg = np.iinfo(np.int64).max
        qhwn__agkwm = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            start = data._start
            stop = data._stop
            if len(data) == 0:
                start = kao__ivwg
                stop = qhwn__agkwm
            start = bodo.libs.distributed_api.dist_reduce(start, np.int32(
                Reduce_Type.Min.value))
            stop = bodo.libs.distributed_api.dist_reduce(stop, np.int32(
                Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if start == kao__ivwg and stop == qhwn__agkwm:
                start = 0
                stop = 0
            kux__pbek = max(0, -(-(stop - start) // data._step))
            if kux__pbek < total_len:
                stop = start + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                start = 0
                stop = 0
            return bodo.hiframes.pd_index_ext.init_range_index(start, stop,
                data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            uvnl__pks = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, uvnl__pks)
        else:

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.utils.conversion.index_from_array(arr, data._name)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            opvsb__umoj = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(
                opvsb__umoj, data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        uyyiw__tsu = {'bodo': bodo, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        vqu__ybq = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        vqu__ybq += '  T = data\n'
        vqu__ybq += '  T2 = init_table(T)\n'
        for vxusv__ysy in data.type_to_blk.values():
            uyyiw__tsu[f'arr_inds_{vxusv__ysy}'] = np.array(data.
                block_to_arr_ind[vxusv__ysy], dtype=np.int64)
            vqu__ybq += (
                f'  arr_list_{vxusv__ysy} = get_table_block(T, {vxusv__ysy})\n'
                )
            vqu__ybq += (
                f'  out_arr_list_{vxusv__ysy} = alloc_list_like(arr_list_{vxusv__ysy})\n'
                )
            vqu__ybq += f'  for i in range(len(arr_list_{vxusv__ysy})):\n'
            vqu__ybq += (
                f'    arr_ind_{vxusv__ysy} = arr_inds_{vxusv__ysy}[i]\n')
            vqu__ybq += f"""    ensure_column_unboxed(T, arr_list_{vxusv__ysy}, i, arr_ind_{vxusv__ysy})
"""
            vqu__ybq += f"""    out_arr_{vxusv__ysy} = bodo.gatherv(arr_list_{vxusv__ysy}[i], allgather, warn_if_rep, root)
"""
            vqu__ybq += (
                f'    out_arr_list_{vxusv__ysy}[i] = out_arr_{vxusv__ysy}\n')
            vqu__ybq += (
                f'  T2 = set_table_block(T2, out_arr_list_{vxusv__ysy}, {vxusv__ysy})\n'
                )
        vqu__ybq += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        vqu__ybq += f'  T2 = set_table_len(T2, length)\n'
        vqu__ybq += f'  return T2\n'
        ygt__pqzah = {}
        exec(vqu__ybq, uyyiw__tsu, ygt__pqzah)
        tmp__ivjp = ygt__pqzah['impl_table']
        return tmp__ivjp
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        wzzvi__rkgyt = len(data.columns)
        if wzzvi__rkgyt == 0:
            return (lambda data, allgather=False, warn_if_rep=True, root=
                MPI_ROOT: bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data), ()))
        jra__drmi = ', '.join(f'g_data_{i}' for i in range(wzzvi__rkgyt))
        ltic__verow = bodo.utils.transform.gen_const_tup(data.columns)
        vqu__ybq = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            hwvg__dnez = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            uyyiw__tsu = {'bodo': bodo, 'df_type': hwvg__dnez}
            jra__drmi = 'T2'
            ltic__verow = 'df_type'
            vqu__ybq += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            vqu__ybq += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            uyyiw__tsu = {'bodo': bodo}
            for i in range(wzzvi__rkgyt):
                vqu__ybq += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                vqu__ybq += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        vqu__ybq += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        vqu__ybq += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        vqu__ybq += (
            '  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})\n'
            .format(jra__drmi, ltic__verow))
        ygt__pqzah = {}
        exec(vqu__ybq, uyyiw__tsu, ygt__pqzah)
        tsfmy__stpk = ygt__pqzah['impl_df']
        return tsfmy__stpk
    if isinstance(data, ArrayItemArrayType):
        jjsn__abea = np.int32(numba_to_c_type(types.int32))
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            tgvzr__uci = bodo.libs.array_item_arr_ext.get_offsets(data)
            zyr__wyf = bodo.libs.array_item_arr_ext.get_data(data)
            vlos__tzn = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            apy__wni = len(data)
            qnbzv__sjsez = np.empty(apy__wni, np.uint32)
            qponu__ujzz = apy__wni + 7 >> 3
            for i in range(apy__wni):
                qnbzv__sjsez[i] = tgvzr__uci[i + 1] - tgvzr__uci[i]
            recv_counts = gather_scalar(np.int32(apy__wni), allgather, root
                =root)
            jjcfo__zdhfa = recv_counts.sum()
            olx__xsll = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            ulqw__suu = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                olx__xsll = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for giwe__lyo in range(len(recv_counts)):
                    recv_counts_nulls[giwe__lyo] = recv_counts[giwe__lyo
                        ] + 7 >> 3
                ulqw__suu = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            fgsvw__cckd = np.empty(jjcfo__zdhfa + 1, np.uint32)
            jun__iti = bodo.gatherv(zyr__wyf, allgather, warn_if_rep, root)
            anf__afuu = np.empty(jjcfo__zdhfa + 7 >> 3, np.uint8)
            c_gatherv(qnbzv__sjsez.ctypes, np.int32(apy__wni), fgsvw__cckd.
                ctypes, recv_counts.ctypes, olx__xsll.ctypes, jjsn__abea,
                allgather, np.int32(root))
            c_gatherv(vlos__tzn.ctypes, np.int32(qponu__ujzz),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, ulqw__suu.
                ctypes, jcjlx__exrnx, allgather, np.int32(root))
            dummy_use(data)
            kti__sbx = np.empty(jjcfo__zdhfa + 1, np.uint64)
            convert_len_arr_to_offset(fgsvw__cckd.ctypes, kti__sbx.ctypes,
                jjcfo__zdhfa)
            copy_gathered_null_bytes(anf__afuu.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                jjcfo__zdhfa, jun__iti, kti__sbx, anf__afuu)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        joo__znf = data.names
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            mfe__fxzlc = bodo.libs.struct_arr_ext.get_data(data)
            lxpp__drnbw = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            ovohb__qfx = bodo.gatherv(mfe__fxzlc, allgather=allgather, root
                =root)
            rank = bodo.libs.distributed_api.get_rank()
            apy__wni = len(data)
            qponu__ujzz = apy__wni + 7 >> 3
            recv_counts = gather_scalar(np.int32(apy__wni), allgather, root
                =root)
            jjcfo__zdhfa = recv_counts.sum()
            mcokm__hyqcv = np.empty(jjcfo__zdhfa + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            ulqw__suu = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                ulqw__suu = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(lxpp__drnbw.ctypes, np.int32(qponu__ujzz),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, ulqw__suu.
                ctypes, jcjlx__exrnx, allgather, np.int32(root))
            copy_gathered_null_bytes(mcokm__hyqcv.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(ovohb__qfx,
                mcokm__hyqcv, joo__znf)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            opvsb__umoj = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.binary_arr_ext.init_binary_arr(opvsb__umoj)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            opvsb__umoj = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.tuple_arr_ext.init_tuple_arr(opvsb__umoj)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            opvsb__umoj = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.map_arr_ext.init_map_arr(opvsb__umoj)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            opvsb__umoj = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            ixf__rahcn = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            bjlg__jekz = bodo.gatherv(data.indptr, allgather, warn_if_rep, root
                )
            xyosa__jhm = gather_scalar(data.shape[0], allgather, root=root)
            fhv__fjyty = xyosa__jhm.sum()
            wzzvi__rkgyt = bodo.libs.distributed_api.dist_reduce(data.shape
                [1], np.int32(Reduce_Type.Max.value))
            nqnit__vjctk = np.empty(fhv__fjyty + 1, np.int64)
            ixf__rahcn = ixf__rahcn.astype(np.int64)
            nqnit__vjctk[0] = 0
            qeh__nxbt = 1
            cmz__uunlk = 0
            for mhb__wml in xyosa__jhm:
                for duzvk__bqo in range(mhb__wml):
                    cgz__dqnl = bjlg__jekz[cmz__uunlk + 1] - bjlg__jekz[
                        cmz__uunlk]
                    nqnit__vjctk[qeh__nxbt] = nqnit__vjctk[qeh__nxbt - 1
                        ] + cgz__dqnl
                    qeh__nxbt += 1
                    cmz__uunlk += 1
                cmz__uunlk += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(opvsb__umoj,
                ixf__rahcn, nqnit__vjctk, (fhv__fjyty, wzzvi__rkgyt))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        vqu__ybq = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        vqu__ybq += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        ygt__pqzah = {}
        exec(vqu__ybq, {'bodo': bodo}, ygt__pqzah)
        gyqwo__glndi = ygt__pqzah['impl_tuple']
        return gyqwo__glndi
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    vqu__ybq = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    vqu__ybq += '    if random:\n'
    vqu__ybq += '        if random_seed is None:\n'
    vqu__ybq += '            random = 1\n'
    vqu__ybq += '        else:\n'
    vqu__ybq += '            random = 2\n'
    vqu__ybq += '    if random_seed is None:\n'
    vqu__ybq += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        whqs__cmook = data
        wzzvi__rkgyt = len(whqs__cmook.columns)
        for i in range(wzzvi__rkgyt):
            vqu__ybq += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        vqu__ybq += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        jra__drmi = ', '.join(f'data_{i}' for i in range(wzzvi__rkgyt))
        vqu__ybq += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(cpwsr__tdyk) for
            cpwsr__tdyk in range(wzzvi__rkgyt))))
        vqu__ybq += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        vqu__ybq += '    if dests is None:\n'
        vqu__ybq += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        vqu__ybq += '    else:\n'
        vqu__ybq += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for fkte__uzova in range(wzzvi__rkgyt):
            vqu__ybq += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(fkte__uzova))
        vqu__ybq += (
            '    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
            .format(wzzvi__rkgyt))
        vqu__ybq += '    delete_table(out_table)\n'
        vqu__ybq += '    if parallel:\n'
        vqu__ybq += '        delete_table(table_total)\n'
        jra__drmi = ', '.join('out_arr_{}'.format(i) for i in range(
            wzzvi__rkgyt))
        ltic__verow = bodo.utils.transform.gen_const_tup(whqs__cmook.columns)
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        vqu__ybq += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, {})\n'
            .format(jra__drmi, index, ltic__verow))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        vqu__ybq += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        vqu__ybq += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        vqu__ybq += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        vqu__ybq += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        vqu__ybq += '    if dests is None:\n'
        vqu__ybq += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        vqu__ybq += '    else:\n'
        vqu__ybq += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        vqu__ybq += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        vqu__ybq += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        vqu__ybq += '    delete_table(out_table)\n'
        vqu__ybq += '    if parallel:\n'
        vqu__ybq += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        vqu__ybq += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        vqu__ybq += '    if not parallel:\n'
        vqu__ybq += '        return data\n'
        vqu__ybq += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        vqu__ybq += '    if dests is None:\n'
        vqu__ybq += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        vqu__ybq += '    elif bodo.get_rank() not in dests:\n'
        vqu__ybq += '        dim0_local_size = 0\n'
        vqu__ybq += '    else:\n'
        vqu__ybq += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        vqu__ybq += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        vqu__ybq += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        vqu__ybq += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        vqu__ybq += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        vqu__ybq += '    if dests is None:\n'
        vqu__ybq += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        vqu__ybq += '    else:\n'
        vqu__ybq += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        vqu__ybq += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        vqu__ybq += '    delete_table(out_table)\n'
        vqu__ybq += '    if parallel:\n'
        vqu__ybq += '        delete_table(table_total)\n'
        vqu__ybq += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    ygt__pqzah = {}
    exec(vqu__ybq, {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.
        array.array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table},
        ygt__pqzah)
    impl = ygt__pqzah['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, parallel=False):
    vqu__ybq = 'def impl(data, seed=None, dests=None, parallel=False):\n'
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        vqu__ybq += '    if seed is None:\n'
        vqu__ybq += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        vqu__ybq += '    np.random.seed(seed)\n'
        vqu__ybq += '    if not parallel:\n'
        vqu__ybq += '        data = data.copy()\n'
        vqu__ybq += '        np.random.shuffle(data)\n'
        vqu__ybq += '        return data\n'
        vqu__ybq += '    else:\n'
        vqu__ybq += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        vqu__ybq += '        permutation = np.arange(dim0_global_size)\n'
        vqu__ybq += '        np.random.shuffle(permutation)\n'
        vqu__ybq += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        vqu__ybq += """        output = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        vqu__ybq += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        vqu__ybq += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation))
"""
        vqu__ybq += '        return output\n'
    else:
        vqu__ybq += """    return bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
    ygt__pqzah = {}
    exec(vqu__ybq, {'np': np, 'bodo': bodo}, ygt__pqzah)
    impl = ygt__pqzah['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    cpzt__dpjc = np.empty(sendcounts_nulls.sum(), np.uint8)
    qsax__avcm = 0
    syu__kbi = 0
    for cthh__xvbq in range(len(sendcounts)):
        xay__gpw = sendcounts[cthh__xvbq]
        qponu__ujzz = sendcounts_nulls[cthh__xvbq]
        xhqm__qjcd = cpzt__dpjc[qsax__avcm:qsax__avcm + qponu__ujzz]
        for lmys__ezpnp in range(xay__gpw):
            set_bit_to_arr(xhqm__qjcd, lmys__ezpnp, get_bit_bitmap(
                null_bitmap_ptr, syu__kbi))
            syu__kbi += 1
        qsax__avcm += qponu__ujzz
    return cpzt__dpjc


def _bcast_dtype(data):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    vucxz__hcnv = MPI.COMM_WORLD
    data = vucxz__hcnv.bcast(data)
    return data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_scatterv_send_counts(send_counts, n_pes, n):
    if not is_overload_none(send_counts):
        return lambda send_counts, n_pes, n: send_counts

    def impl(send_counts, n_pes, n):
        send_counts = np.empty(n_pes, np.int32)
        for i in range(n_pes):
            send_counts[i] = get_node_portion(n, n_pes, i)
        return send_counts
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _scatterv_np(data, send_counts=None, warn_if_dist=True):
    typ_val = numba_to_c_type(data.dtype)
    rej__btti = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    jwr__rlsjh = (0,) * rej__btti

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        kvd__hsumg = np.ascontiguousarray(data)
        ihgb__magcg = data.ctypes
        mwizq__pezam = jwr__rlsjh
        if rank == MPI_ROOT:
            mwizq__pezam = kvd__hsumg.shape
        mwizq__pezam = bcast_tuple(mwizq__pezam)
        uokez__nmita = get_tuple_prod(mwizq__pezam[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            mwizq__pezam[0])
        send_counts *= uokez__nmita
        apy__wni = send_counts[rank]
        vnto__xdhk = np.empty(apy__wni, dtype)
        olx__xsll = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(ihgb__magcg, send_counts.ctypes, olx__xsll.ctypes,
            vnto__xdhk.ctypes, np.int32(apy__wni), np.int32(typ_val))
        return vnto__xdhk.reshape((-1,) + mwizq__pezam[1:])
    return scatterv_arr_impl


def _get_name_value_for_type(name_typ):
    assert isinstance(name_typ, (types.UnicodeType, types.StringLiteral)
        ) or name_typ == types.none
    return None if name_typ == types.none else '_' + str(ir_utils.next_label())


def get_value_for_type(dtype):
    if isinstance(dtype, types.Array):
        return np.zeros((1,) * dtype.ndim, numba.np.numpy_support.as_dtype(
            dtype.dtype))
    if dtype == string_array_type:
        return pd.array(['A'], 'string')
    if dtype == binary_array_type:
        return np.array([b'A'], dtype=object)
    if isinstance(dtype, IntegerArrayType):
        ext__gchcd = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], ext__gchcd)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        pjtaq__lhvhc = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=pjtaq__lhvhc)
        eps__qzbyj = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(eps__qzbyj)
        return pd.Index(arr, name=pjtaq__lhvhc)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        pjtaq__lhvhc = _get_name_value_for_type(dtype.name_typ)
        joo__znf = tuple(_get_name_value_for_type(t) for t in dtype.names_typ)
        bspce__uuks = tuple(get_value_for_type(t) for t in dtype.array_types)
        val = pd.MultiIndex.from_arrays(bspce__uuks, names=joo__znf)
        val.name = pjtaq__lhvhc
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        pjtaq__lhvhc = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=pjtaq__lhvhc)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        bspce__uuks = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({pjtaq__lhvhc: arr for pjtaq__lhvhc, arr in zip
            (dtype.columns, bspce__uuks)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        eps__qzbyj = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(eps__qzbyj[0],
            eps__qzbyj[0])])
    raise BodoError(f'get_value_for_type(dtype): Missing data type {dtype}')


def scatterv(data, send_counts=None, warn_if_dist=True):
    rank = bodo.libs.distributed_api.get_rank()
    if rank != MPI_ROOT and data is not None:
        warnings.warn(BodoWarning(
            "bodo.scatterv(): A non-None value for 'data' was found on a rank other than the root. This data won't be sent to any other ranks and will be overwritten with data from rank 0."
            ))
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return scatterv_impl(data, send_counts)


@overload(scatterv)
def scatterv_overload(data, send_counts=None, warn_if_dist=True):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.scatterv()')
    return lambda data, send_counts=None, warn_if_dist=True: scatterv_impl(data
        , send_counts)


@numba.generated_jit(nopython=True)
def scatterv_impl(data, send_counts=None, warn_if_dist=True):
    if isinstance(data, types.Array):
        return lambda data, send_counts=None, warn_if_dist=True: _scatterv_np(
            data, send_counts)
    if data in [binary_array_type, string_array_type]:
        jjsn__abea = np.int32(numba_to_c_type(types.int32))
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            avx__gfn = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            avx__gfn = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        vqu__ybq = f"""def impl(
            data, send_counts=None, warn_if_dist=True
        ):  # pragma: no cover
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            n_all = bodo.libs.distributed_api.bcast_scalar(len(data))

            # convert offsets to lengths of strings
            send_arr_lens = np.empty(
                len(data), np.uint32
            )  # XXX offset type is offset_type, lengths for comm are uint32
            for i in range(len(data)):
                send_arr_lens[i] = bodo.libs.str_arr_ext.get_str_arr_item_length(
                    data, i
                )

            # ------- calculate buffer counts -------

            send_counts = bodo.libs.distributed_api._get_scatterv_send_counts(send_counts, n_pes, n_all)

            # displacements
            displs = bodo.ir.join.calc_disp(send_counts)

            # compute send counts for characters
            send_counts_char = np.empty(n_pes, np.int32)
            if rank == 0:
                curr_str = 0
                for i in range(n_pes):
                    c = 0
                    for _ in range(send_counts[i]):
                        c += send_arr_lens[curr_str]
                        curr_str += 1
                    send_counts_char[i] = c

            bodo.libs.distributed_api.bcast(send_counts_char)

            # displacements for characters
            displs_char = bodo.ir.join.calc_disp(send_counts_char)

            # compute send counts for nulls
            send_counts_nulls = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                send_counts_nulls[i] = (send_counts[i] + 7) >> 3

            # displacements for nulls
            displs_nulls = bodo.ir.join.calc_disp(send_counts_nulls)

            # alloc output array
            n_loc = send_counts[rank]  # total number of elements on this PE
            n_loc_char = send_counts_char[rank]
            recv_arr = {avx__gfn}(n_loc, n_loc_char)

            # ----- string lengths -----------

            recv_lens = np.empty(n_loc, np.uint32)
            bodo.libs.distributed_api.c_scatterv(
                send_arr_lens.ctypes,
                send_counts.ctypes,
                displs.ctypes,
                recv_lens.ctypes,
                np.int32(n_loc),
                int32_typ_enum,
            )

            # TODO: don't hardcode offset type. Also, if offset is 32 bit we can
            # use the same buffer
            bodo.libs.str_arr_ext.convert_len_arr_to_offset(recv_lens.ctypes, bodo.libs.str_arr_ext.get_offset_ptr(recv_arr), n_loc)

            # ----- string characters -----------

            bodo.libs.distributed_api.c_scatterv(
                bodo.libs.str_arr_ext.get_data_ptr(data),
                send_counts_char.ctypes,
                displs_char.ctypes,
                bodo.libs.str_arr_ext.get_data_ptr(recv_arr),
                np.int32(n_loc_char),
                char_typ_enum,
            )

            # ----------- null bitmap -------------

            n_recv_bytes = (n_loc + 7) >> 3

            send_null_bitmap = bodo.libs.distributed_api.get_scatter_null_bytes_buff(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(data), send_counts, send_counts_nulls
            )

            bodo.libs.distributed_api.c_scatterv(
                send_null_bitmap.ctypes,
                send_counts_nulls.ctypes,
                displs_nulls.ctypes,
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(recv_arr),
                np.int32(n_recv_bytes),
                char_typ_enum,
            )

            return recv_arr"""
        ygt__pqzah = dict()
        exec(vqu__ybq, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            jjsn__abea, 'char_typ_enum': jcjlx__exrnx}, ygt__pqzah)
        impl = ygt__pqzah['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        jjsn__abea = np.int32(numba_to_c_type(types.int32))
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            bhzot__tzq = bodo.libs.array_item_arr_ext.get_offsets(data)
            zvh__kcuc = bodo.libs.array_item_arr_ext.get_data(data)
            abw__akz = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            lyx__monh = bcast_scalar(len(data))
            wyr__bll = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                wyr__bll[i] = bhzot__tzq[i + 1] - bhzot__tzq[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                lyx__monh)
            olx__xsll = bodo.ir.join.calc_disp(send_counts)
            bswjj__byfc = np.empty(n_pes, np.int32)
            if rank == 0:
                fzt__hfn = 0
                for i in range(n_pes):
                    mupw__wwlz = 0
                    for duzvk__bqo in range(send_counts[i]):
                        mupw__wwlz += wyr__bll[fzt__hfn]
                        fzt__hfn += 1
                    bswjj__byfc[i] = mupw__wwlz
            bcast(bswjj__byfc)
            ffno__qmm = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                ffno__qmm[i] = send_counts[i] + 7 >> 3
            ulqw__suu = bodo.ir.join.calc_disp(ffno__qmm)
            apy__wni = send_counts[rank]
            wnp__ucvo = np.empty(apy__wni + 1, np_offset_type)
            qzup__htr = bodo.libs.distributed_api.scatterv_impl(zvh__kcuc,
                bswjj__byfc)
            vjt__awyxb = apy__wni + 7 >> 3
            whc__gxwt = np.empty(vjt__awyxb, np.uint8)
            mhd__nmc = np.empty(apy__wni, np.uint32)
            c_scatterv(wyr__bll.ctypes, send_counts.ctypes, olx__xsll.
                ctypes, mhd__nmc.ctypes, np.int32(apy__wni), jjsn__abea)
            convert_len_arr_to_offset(mhd__nmc.ctypes, wnp__ucvo.ctypes,
                apy__wni)
            pruya__zmdck = get_scatter_null_bytes_buff(abw__akz.ctypes,
                send_counts, ffno__qmm)
            c_scatterv(pruya__zmdck.ctypes, ffno__qmm.ctypes, ulqw__suu.
                ctypes, whc__gxwt.ctypes, np.int32(vjt__awyxb), jcjlx__exrnx)
            return bodo.libs.array_item_arr_ext.init_array_item_array(apy__wni,
                qzup__htr, wnp__ucvo, whc__gxwt)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            owvp__hvk = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            owvp__hvk = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            owvp__hvk = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            owvp__hvk = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            kvd__hsumg = data._data
            lxpp__drnbw = data._null_bitmap
            imj__jsq = len(kvd__hsumg)
            ety__wxv = _scatterv_np(kvd__hsumg, send_counts)
            lyx__monh = bcast_scalar(imj__jsq)
            mhh__lmg = len(ety__wxv) + 7 >> 3
            jrpc__mop = np.empty(mhh__lmg, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                lyx__monh)
            ffno__qmm = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                ffno__qmm[i] = send_counts[i] + 7 >> 3
            ulqw__suu = bodo.ir.join.calc_disp(ffno__qmm)
            pruya__zmdck = get_scatter_null_bytes_buff(lxpp__drnbw.ctypes,
                send_counts, ffno__qmm)
            c_scatterv(pruya__zmdck.ctypes, ffno__qmm.ctypes, ulqw__suu.
                ctypes, jrpc__mop.ctypes, np.int32(mhh__lmg), jcjlx__exrnx)
            return owvp__hvk(ety__wxv, jrpc__mop)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            yrlj__jrs = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            upjmt__mdv = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(yrlj__jrs,
                upjmt__mdv)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            start = data._start
            stop = data._stop
            fflv__zgjur = data._step
            pjtaq__lhvhc = data._name
            pjtaq__lhvhc = bcast_scalar(pjtaq__lhvhc)
            start = bcast_scalar(start)
            stop = bcast_scalar(stop)
            fflv__zgjur = bcast_scalar(fflv__zgjur)
            qku__ldyb = bodo.libs.array_kernels.calc_nitems(start, stop,
                fflv__zgjur)
            chunk_start = bodo.libs.distributed_api.get_start(qku__ldyb,
                n_pes, rank)
            chunk_count = bodo.libs.distributed_api.get_node_portion(qku__ldyb,
                n_pes, rank)
            mfigx__ukos = start + fflv__zgjur * chunk_start
            mpw__ymxz = start + fflv__zgjur * (chunk_start + chunk_count)
            mpw__ymxz = min(mpw__ymxz, stop)
            return bodo.hiframes.pd_index_ext.init_range_index(mfigx__ukos,
                mpw__ymxz, fflv__zgjur, pjtaq__lhvhc)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        uvnl__pks = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            kvd__hsumg = data._data
            pjtaq__lhvhc = data._name
            pjtaq__lhvhc = bcast_scalar(pjtaq__lhvhc)
            arr = bodo.libs.distributed_api.scatterv_impl(kvd__hsumg,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                pjtaq__lhvhc, uvnl__pks)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            kvd__hsumg = data._data
            pjtaq__lhvhc = data._name
            pjtaq__lhvhc = bcast_scalar(pjtaq__lhvhc)
            arr = bodo.libs.distributed_api.scatterv_impl(kvd__hsumg,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, pjtaq__lhvhc)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            opvsb__umoj = bodo.libs.distributed_api.scatterv_impl(data.
                _data, send_counts)
            pjtaq__lhvhc = bcast_scalar(data._name)
            joo__znf = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(
                opvsb__umoj, joo__znf, pjtaq__lhvhc)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            pjtaq__lhvhc = bodo.hiframes.pd_series_ext.get_series_name(data)
            rvnis__ytwr = bcast_scalar(pjtaq__lhvhc)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            mpl__gado = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                mpl__gado, rvnis__ytwr)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        wzzvi__rkgyt = len(data.columns)
        jra__drmi = ', '.join('g_data_{}'.format(i) for i in range(
            wzzvi__rkgyt))
        ltic__verow = bodo.utils.transform.gen_const_tup(data.columns)
        vqu__ybq = 'def impl_df(data, send_counts=None, warn_if_dist=True):\n'
        for i in range(wzzvi__rkgyt):
            vqu__ybq += (
                '  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})\n'
                .format(i, i))
            vqu__ybq += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        vqu__ybq += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        vqu__ybq += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        vqu__ybq += (
            '  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})\n'
            .format(jra__drmi, ltic__verow))
        ygt__pqzah = {}
        exec(vqu__ybq, {'bodo': bodo}, ygt__pqzah)
        tsfmy__stpk = ygt__pqzah['impl_df']
        return tsfmy__stpk
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            awv__qmq = bodo.libs.distributed_api.scatterv_impl(data.codes,
                send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                awv__qmq, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        vqu__ybq = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        vqu__ybq += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        ygt__pqzah = {}
        exec(vqu__ybq, {'bodo': bodo}, ygt__pqzah)
        gyqwo__glndi = ygt__pqzah['impl_tuple']
        return gyqwo__glndi
    if data is types.none:
        return lambda data, send_counts=None, warn_if_dist=True: None
    raise BodoError('scatterv() not available for {}'.format(data))


@intrinsic
def cptr_to_voidptr(typingctx, cptr_tp=None):

    def codegen(context, builder, sig, args):
        return builder.bitcast(args[0], lir.IntType(8).as_pointer())
    return types.voidptr(cptr_tp), codegen


def bcast(data):
    return


@overload(bcast, no_unliteral=True)
def bcast_overload(data):
    if isinstance(data, types.Array):

        def bcast_impl(data):
            typ_enum = get_type_enum(data)
            count = data.size
            assert count < INT_MAX
            c_bcast(data.ctypes, np.int32(count), typ_enum, np.array([-1]).
                ctypes, 0)
            return
        return bcast_impl
    if isinstance(data, DecimalArrayType):

        def bcast_decimal_arr(data):
            count = data._data.size
            assert count < INT_MAX
            c_bcast(data._data.ctypes, np.int32(count), CTypeEnum.Int128.
                value, np.array([-1]).ctypes, 0)
            bcast(data._null_bitmap)
            return
        return bcast_decimal_arr
    if isinstance(data, IntegerArrayType) or data in (boolean_array,
        datetime_date_array_type):

        def bcast_impl_int_arr(data):
            bcast(data._data)
            bcast(data._null_bitmap)
            return
        return bcast_impl_int_arr
    if data in [binary_array_type, string_array_type]:
        vkn__qwm = np.int32(numba_to_c_type(offset_type))
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data):
            apy__wni = len(data)
            myayz__coo = num_total_chars(data)
            assert apy__wni < INT_MAX
            assert myayz__coo < INT_MAX
            xub__xxbzc = get_offset_ptr(data)
            ihgb__magcg = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            qponu__ujzz = apy__wni + 7 >> 3
            c_bcast(xub__xxbzc, np.int32(apy__wni + 1), vkn__qwm, np.array(
                [-1]).ctypes, 0)
            c_bcast(ihgb__magcg, np.int32(myayz__coo), jcjlx__exrnx, np.
                array([-1]).ctypes, 0)
            c_bcast(null_bitmap_ptr, np.int32(qponu__ujzz), jcjlx__exrnx,
                np.array([-1]).ctypes, 0)
        return bcast_str_impl


c_bcast = types.ExternalFunction('c_bcast', types.void(types.voidptr, types
    .int32, types.int32, types.voidptr, types.int32))


def bcast_scalar(val):
    return val


@overload(bcast_scalar, no_unliteral=True)
def bcast_scalar_overload(val):
    val = types.unliteral(val)
    if not (isinstance(val, (types.Integer, types.Float)) or val in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.string_type, types.none,
        types.bool_]):
        raise_bodo_error(
            f'bcast_scalar requires an argument of type Integer, Float, datetime64ns, timedelta64ns, string, None, or Bool. Found type {val}'
            )
    if val == types.none:
        return lambda val: None
    if val == bodo.string_type:
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != MPI_ROOT:
                jwg__sfb = 0
                ryso__hrvty = np.empty(0, np.uint8).ctypes
            else:
                ryso__hrvty, jwg__sfb = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            jwg__sfb = bodo.libs.distributed_api.bcast_scalar(jwg__sfb)
            if rank != MPI_ROOT:
                zxxn__wud = np.empty(jwg__sfb + 1, np.uint8)
                zxxn__wud[jwg__sfb] = 0
                ryso__hrvty = zxxn__wud.ctypes
            c_bcast(ryso__hrvty, np.int32(jwg__sfb), jcjlx__exrnx, np.array
                ([-1]).ctypes, 0)
            return bodo.libs.str_arr_ext.decode_utf8(ryso__hrvty, jwg__sfb)
        return impl_str
    typ_val = numba_to_c_type(val)
    vqu__ybq = (
        """def bcast_scalar_impl(val):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({}), np.array([-1]).ctypes, 0)
  return send[0]
"""
        .format(typ_val))
    dtype = numba.np.numpy_support.as_dtype(val)
    ygt__pqzah = {}
    exec(vqu__ybq, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, ygt__pqzah)
    yqb__lse = ygt__pqzah['bcast_scalar_impl']
    return yqb__lse


def bcast_tuple(val):
    return val


@overload(bcast_tuple, no_unliteral=True)
def overload_bcast_tuple(val):
    assert isinstance(val, types.BaseTuple)
    vaok__ymv = len(val)
    vqu__ybq = 'def bcast_tuple_impl(val):\n'
    vqu__ybq += '  return ({}{})'.format(','.join('bcast_scalar(val[{}])'.
        format(i) for i in range(vaok__ymv)), ',' if vaok__ymv else '')
    ygt__pqzah = {}
    exec(vqu__ybq, {'bcast_scalar': bcast_scalar}, ygt__pqzah)
    pcde__lwj = ygt__pqzah['bcast_tuple_impl']
    return pcde__lwj


def prealloc_str_for_bcast(arr):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr):
    if arr == string_array_type:

        def prealloc_impl(arr):
            rank = bodo.libs.distributed_api.get_rank()
            apy__wni = bcast_scalar(len(arr))
            guts__joft = bcast_scalar(np.int64(num_total_chars(arr)))
            if rank != MPI_ROOT:
                arr = pre_alloc_string_array(apy__wni, guts__joft)
            return arr
        return prealloc_impl
    return lambda arr: arr


def get_local_slice(idx, arr_start, total_len):
    return idx


@overload(get_local_slice, no_unliteral=True, jit_options={'cache': True,
    'no_cpython_wrapper': True})
def get_local_slice_overload(idx, arr_start, total_len):

    def impl(idx, arr_start, total_len):
        slice_index = numba.cpython.unicode._normalize_slice(idx, total_len)
        start = slice_index.start
        fflv__zgjur = slice_index.step
        ecrpk__wai = 0 if fflv__zgjur == 1 or start > arr_start else abs(
            fflv__zgjur - arr_start % fflv__zgjur) % fflv__zgjur
        mfigx__ukos = max(arr_start, slice_index.start
            ) - arr_start + ecrpk__wai
        mpw__ymxz = max(slice_index.stop - arr_start, 0)
        return slice(mfigx__ukos, mpw__ymxz, fflv__zgjur)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        uewyo__lzkr = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[uewyo__lzkr])
    return getitem_impl


def slice_getitem_from_start(arr, slice_index):
    return arr[slice_index]


@overload(slice_getitem_from_start, no_unliteral=True)
def slice_getitem_from_start_overload(arr, slice_index):
    if arr == bodo.hiframes.datetime_date_ext.datetime_date_array_type:

        def getitem_datetime_date_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            giwe__lyo = slice_index.stop
            A = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
                giwe__lyo)
            if rank == 0:
                A = arr[:giwe__lyo]
            bodo.libs.distributed_api.bcast(A)
            return A
        return getitem_datetime_date_impl
    if (arr == bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_array_type):

        def getitem_datetime_timedelta_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            giwe__lyo = slice_index.stop
            A = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(giwe__lyo))
            if rank == 0:
                A = arr[:giwe__lyo]
            bodo.libs.distributed_api.bcast(A)
            return A
        return getitem_datetime_timedelta_impl
    if isinstance(arr.dtype, Decimal128Type):
        precision = arr.dtype.precision
        scale = arr.dtype.scale

        def getitem_decimal_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            giwe__lyo = slice_index.stop
            A = bodo.libs.decimal_arr_ext.alloc_decimal_array(giwe__lyo,
                precision, scale)
            if rank == 0:
                for i in range(giwe__lyo):
                    A._data[i] = arr._data[i]
                    dghf__rnhwn = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, i,
                        dghf__rnhwn)
            bodo.libs.distributed_api.bcast(A)
            return A
        return getitem_decimal_impl
    if arr == string_array_type:

        def getitem_str_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            giwe__lyo = slice_index.stop
            cvulc__ftrej = np.uint64(0)
            if rank == 0:
                out_arr = arr[:giwe__lyo]
                cvulc__ftrej = num_total_chars(out_arr)
            cvulc__ftrej = bcast_scalar(cvulc__ftrej)
            if rank != 0:
                out_arr = pre_alloc_string_array(giwe__lyo, cvulc__ftrej)
            bodo.libs.distributed_api.bcast(out_arr)
            return out_arr
        return getitem_str_impl
    eps__qzbyj = arr

    def getitem_impl(arr, slice_index):
        rank = bodo.libs.distributed_api.get_rank()
        giwe__lyo = slice_index.stop
        out_arr = bodo.utils.utils.alloc_type(tuple_to_scalar((giwe__lyo,) +
            arr.shape[1:]), eps__qzbyj)
        if rank == 0:
            out_arr = arr[:giwe__lyo]
        bodo.libs.distributed_api.bcast(out_arr)
        return out_arr
    return getitem_impl


dummy_use = numba.njit(lambda a: None)


def int_getitem(arr, ind, arr_start, total_len, is_1D):
    return arr[ind]


def transform_str_getitem_output(data, length):
    pass


@overload(transform_str_getitem_output)
def overload_transform_str_getitem_output(data, length):
    if data == bodo.string_type:
        return lambda data, length: bodo.libs.str_arr_ext.decode_utf8(data.
            _data, length)
    if data == types.Array(types.uint8, 1, 'C'):
        return lambda data, length: bodo.libs.binary_arr_ext.init_bytes_type(
            data, length)
    raise BodoError(
        f'Internal Error: Expected String or Uint8 Array, found {data}')


@overload(int_getitem, no_unliteral=True)
def int_getitem_overload(arr, ind, arr_start, total_len, is_1D):
    if arr in [bodo.binary_array_type, string_array_type]:
        raz__wvh = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        jcjlx__exrnx = np.int32(numba_to_c_type(types.uint8))
        aurre__jao = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            xxf__orc = np.int32(10)
            tag = np.int32(11)
            sbjw__pnv = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                zyr__wyf = arr._data
                hzwtr__erw = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    zyr__wyf, ind)
                gjjrp__bjngc = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    zyr__wyf, ind + 1)
                length = gjjrp__bjngc - hzwtr__erw
                ezj__pbd = zyr__wyf[ind]
                sbjw__pnv[0] = length
                isend(sbjw__pnv, np.int32(1), root, xxf__orc, True)
                isend(ezj__pbd, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(aurre__jao
                , raz__wvh, 0, 1)
            kux__pbek = 0
            if rank == root:
                kux__pbek = recv(np.int64, ANY_SOURCE, xxf__orc)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    aurre__jao, raz__wvh, kux__pbek, 1)
                ihgb__magcg = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(ihgb__magcg, np.int32(kux__pbek), jcjlx__exrnx,
                    ANY_SOURCE, tag)
            dummy_use(sbjw__pnv)
            kux__pbek = bcast_scalar(kux__pbek)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    aurre__jao, raz__wvh, kux__pbek, 1)
            ihgb__magcg = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(ihgb__magcg, np.int32(kux__pbek), jcjlx__exrnx, np.
                array([-1]).ctypes, 0)
            val = transform_str_getitem_output(val, kux__pbek)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        vshf__mgycn = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, vshf__mgycn)
            if arr_start <= ind < arr_start + len(arr):
                awv__qmq = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = awv__qmq[ind - arr_start]
                send_arr = np.full(1, data, vshf__mgycn)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = vshf__mgycn(-1)
            if rank == root:
                val = recv(vshf__mgycn, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            hsny__nohq = arr.dtype.categories[max(val, 0)]
            return hsny__nohq
        return cat_getitem_impl
    crhq__oob = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, crhq__oob)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, crhq__oob)[0]
        if rank == root:
            val = recv(crhq__oob, ANY_SOURCE, tag)
        dummy_use(send_arr)
        val = bcast_scalar(val)
        return val
    return getitem_impl


c_alltoallv = types.ExternalFunction('c_alltoallv', types.void(types.
    voidptr, types.voidptr, types.voidptr, types.voidptr, types.voidptr,
    types.voidptr, types.int32))


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def alltoallv(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    typ_enum = get_type_enum(send_data)
    veok__flcet = get_type_enum(out_data)
    assert typ_enum == veok__flcet
    if isinstance(send_data, (IntegerArrayType, DecimalArrayType)
        ) or send_data in (boolean_array, datetime_date_array_type):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data._data.ctypes,
            out_data._data.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    if isinstance(send_data, bodo.CategoricalArrayType):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data.codes.ctypes,
            out_data.codes.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    return (lambda send_data, out_data, send_counts, recv_counts, send_disp,
        recv_disp: c_alltoallv(send_data.ctypes, out_data.ctypes,
        send_counts.ctypes, recv_counts.ctypes, send_disp.ctypes, recv_disp
        .ctypes, typ_enum))


def alltoallv_tup(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    return


@overload(alltoallv_tup, no_unliteral=True)
def alltoallv_tup_overload(send_data, out_data, send_counts, recv_counts,
    send_disp, recv_disp):
    count = send_data.count
    assert out_data.count == count
    vqu__ybq = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        vqu__ybq += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    vqu__ybq += '  return\n'
    ygt__pqzah = {}
    exec(vqu__ybq, {'alltoallv': alltoallv}, ygt__pqzah)
    fhuxl__omvwf = ygt__pqzah['f']
    return fhuxl__omvwf


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    start = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return start, count


@numba.njit
def get_start(total_size, pes, rank):
    gaod__bazm = total_size % pes
    zicb__dbx = (total_size - gaod__bazm) // pes
    return rank * zicb__dbx + min(rank, gaod__bazm)


@numba.njit
def get_end(total_size, pes, rank):
    gaod__bazm = total_size % pes
    zicb__dbx = (total_size - gaod__bazm) // pes
    return (rank + 1) * zicb__dbx + min(rank + 1, gaod__bazm)


@numba.njit
def get_node_portion(total_size, pes, rank):
    gaod__bazm = total_size % pes
    zicb__dbx = (total_size - gaod__bazm) // pes
    if rank < gaod__bazm:
        return zicb__dbx + 1
    else:
        return zicb__dbx


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    tsjsc__cyi = in_arr.dtype(0)
    qperl__obe = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        mupw__wwlz = tsjsc__cyi
        for abntm__xpmr in np.nditer(in_arr):
            mupw__wwlz += abntm__xpmr.item()
        qwfc__ycwqk = dist_exscan(mupw__wwlz, qperl__obe)
        for i in range(in_arr.size):
            qwfc__ycwqk += in_arr[i]
            out_arr[i] = qwfc__ycwqk
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    xdxg__hioi = in_arr.dtype(1)
    qperl__obe = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        mupw__wwlz = xdxg__hioi
        for abntm__xpmr in np.nditer(in_arr):
            mupw__wwlz *= abntm__xpmr.item()
        qwfc__ycwqk = dist_exscan(mupw__wwlz, qperl__obe)
        if get_rank() == 0:
            qwfc__ycwqk = xdxg__hioi
        for i in range(in_arr.size):
            qwfc__ycwqk *= in_arr[i]
            out_arr[i] = qwfc__ycwqk
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        xdxg__hioi = np.finfo(in_arr.dtype(1).dtype).max
    else:
        xdxg__hioi = np.iinfo(in_arr.dtype(1).dtype).max
    qperl__obe = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        mupw__wwlz = xdxg__hioi
        for abntm__xpmr in np.nditer(in_arr):
            mupw__wwlz = min(mupw__wwlz, abntm__xpmr.item())
        qwfc__ycwqk = dist_exscan(mupw__wwlz, qperl__obe)
        if get_rank() == 0:
            qwfc__ycwqk = xdxg__hioi
        for i in range(in_arr.size):
            qwfc__ycwqk = min(qwfc__ycwqk, in_arr[i])
            out_arr[i] = qwfc__ycwqk
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        xdxg__hioi = np.finfo(in_arr.dtype(1).dtype).min
    else:
        xdxg__hioi = np.iinfo(in_arr.dtype(1).dtype).min
    xdxg__hioi = in_arr.dtype(1)
    qperl__obe = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        mupw__wwlz = xdxg__hioi
        for abntm__xpmr in np.nditer(in_arr):
            mupw__wwlz = max(mupw__wwlz, abntm__xpmr.item())
        qwfc__ycwqk = dist_exscan(mupw__wwlz, qperl__obe)
        if get_rank() == 0:
            qwfc__ycwqk = xdxg__hioi
        for i in range(in_arr.size):
            qwfc__ycwqk = max(qwfc__ycwqk, in_arr[i])
            out_arr[i] = qwfc__ycwqk
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    avmm__olzf = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), avmm__olzf)


def dist_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    eww__wzbp = args[0]
    if equiv_set.has_shape(eww__wzbp):
        return ArrayAnalysis.AnalyzeResult(shape=eww__wzbp, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_distributed_api_dist_return = (
    dist_return_equiv)


def threaded_return(A):
    return A


@numba.njit
def set_arr_local(arr, ind, val):
    arr[ind] = val


@numba.njit
def local_alloc_size(n, in_arr):
    return n


@infer_global(threaded_return)
@infer_global(dist_return)
class ThreadedRetTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        return signature(args[0], *args)


@numba.njit
def parallel_print(*args):
    print(*args)


@numba.njit
def single_print(*args):
    if bodo.libs.distributed_api.get_rank() == 0:
        print(*args)


@numba.njit(no_cpython_wrapper=True)
def print_if_not_empty(arg):
    if len(arg) != 0 or bodo.get_rank() == 0:
        print(arg)


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        qdnhv__byk = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        vqu__ybq = 'def f(req, cond=True):\n'
        vqu__ybq += f'  return {qdnhv__byk}\n'
        ygt__pqzah = {}
        exec(vqu__ybq, {'_wait': _wait}, ygt__pqzah)
        impl = ygt__pqzah['f']
        return impl
    if is_overload_none(req):
        return lambda req, cond=True: None
    return lambda req, cond=True: _wait(req, cond)


class ReqArrayType(types.Type):

    def __init__(self):
        super(ReqArrayType, self).__init__(name='ReqArrayType()')


req_array_type = ReqArrayType()
register_model(ReqArrayType)(models.OpaqueModel)
waitall = types.ExternalFunction('dist_waitall', types.void(types.int32,
    req_array_type))
comm_req_alloc = types.ExternalFunction('comm_req_alloc', req_array_type(
    types.int32))
comm_req_dealloc = types.ExternalFunction('comm_req_dealloc', types.void(
    req_array_type))
req_array_setitem = types.ExternalFunction('req_array_setitem', types.void(
    req_array_type, types.int64, mpi_req_numba_type))


@overload(operator.setitem, no_unliteral=True)
def overload_req_arr_setitem(A, idx, val):
    if A == req_array_type:
        assert val == mpi_req_numba_type
        return lambda A, idx, val: req_array_setitem(A, idx, val)


@numba.njit
def _get_local_range(start, stop, chunk_start, chunk_count):
    assert start >= 0 and stop > 0
    mfigx__ukos = max(start, chunk_start)
    mpw__ymxz = min(stop, chunk_start + chunk_count)
    nehm__lqf = mfigx__ukos - chunk_start
    plo__kqknu = mpw__ymxz - chunk_start
    if nehm__lqf < 0 or plo__kqknu < 0:
        nehm__lqf = 1
        plo__kqknu = 0
    return nehm__lqf, plo__kqknu


@register_jitable
def _set_if_in_range(A, val, index, chunk_start):
    if index >= chunk_start and index < chunk_start + len(A):
        A[index - chunk_start] = val


@register_jitable
def _root_rank_select(old_val, new_val):
    if get_rank() == 0:
        return old_val
    return new_val


def get_tuple_prod(t):
    return np.prod(t)


@overload(get_tuple_prod, no_unliteral=True)
def get_tuple_prod_overload(t):
    if t == numba.core.types.containers.Tuple(()):
        return lambda t: 1

    def get_tuple_prod_impl(t):
        gaod__bazm = 1
        for a in t:
            gaod__bazm *= a
        return gaod__bazm
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    psmuq__tye = np.ascontiguousarray(in_arr)
    ocr__hkn = get_tuple_prod(psmuq__tye.shape[1:])
    ljox__vnszk = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        wrm__ihbap = np.array(dest_ranks, dtype=np.int32)
    else:
        wrm__ihbap = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, psmuq__tye.ctypes, new_dim0_global_len,
        len(in_arr), dtype_size * ljox__vnszk, dtype_size * ocr__hkn, len(
        wrm__ihbap), wrm__ihbap.ctypes)
    check_and_propagate_cpp_exception()


permutation_int = types.ExternalFunction('permutation_int', types.void(
    types.voidptr, types.intp))


@numba.njit
def dist_permutation_int(lhs, n):
    permutation_int(lhs.ctypes, n)


permutation_array_index = types.ExternalFunction('permutation_array_index',
    types.void(types.voidptr, types.intp, types.intp, types.voidptr, types.
    int64, types.voidptr, types.intp))


@numba.njit
def dist_permutation_array_index(lhs, lhs_len, dtype_size, rhs, p, p_len):
    oxnb__hmgfh = np.ascontiguousarray(rhs)
    jviog__siu = get_tuple_prod(oxnb__hmgfh.shape[1:])
    zsog__wxz = dtype_size * jviog__siu
    permutation_array_index(lhs.ctypes, lhs_len, zsog__wxz, oxnb__hmgfh.
        ctypes, oxnb__hmgfh.shape[0], p.ctypes, p_len)
    check_and_propagate_cpp_exception()


from bodo.io import fsspec_reader, hdfs_reader, s3_reader
ll.add_symbol('finalize', hdist.finalize)
finalize = types.ExternalFunction('finalize', types.int32())
ll.add_symbol('finalize_s3', s3_reader.finalize_s3)
finalize_s3 = types.ExternalFunction('finalize_s3', types.int32())
ll.add_symbol('finalize_fsspec', fsspec_reader.finalize_fsspec)
finalize_fsspec = types.ExternalFunction('finalize_fsspec', types.int32())
ll.add_symbol('disconnect_hdfs', hdfs_reader.disconnect_hdfs)
disconnect_hdfs = types.ExternalFunction('disconnect_hdfs', types.int32())


def _check_for_cpp_errors():
    pass


@overload(_check_for_cpp_errors)
def overload_check_for_cpp_errors():
    return lambda : check_and_propagate_cpp_exception()


@numba.njit
def call_finalize():
    finalize()
    finalize_s3()
    finalize_fsspec()
    _check_for_cpp_errors()
    disconnect_hdfs()


def flush_stdout():
    if not sys.stdout.closed:
        sys.stdout.flush()


atexit.register(call_finalize)
atexit.register(flush_stdout)


def bcast_comm(data, comm_ranks, nranks):
    rank = bodo.libs.distributed_api.get_rank()
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return bcast_comm_impl(data, comm_ranks, nranks)


@overload(bcast_comm)
def bcast_comm_overload(data, comm_ranks, nranks):
    return lambda data, comm_ranks, nranks: bcast_comm_impl(data,
        comm_ranks, nranks)


@numba.generated_jit(nopython=True)
def bcast_comm_impl(data, comm_ranks, nranks):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.bcast_comm()')
    if isinstance(data, (types.Integer, types.Float)):
        typ_val = numba_to_c_type(data)
        vqu__ybq = (
            """def bcast_scalar_impl(data, comm_ranks, nranks):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({}), comm_ranks,ctypes, np.int32({}))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        ygt__pqzah = {}
        exec(vqu__ybq, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
            dtype}, ygt__pqzah)
        yqb__lse = ygt__pqzah['bcast_scalar_impl']
        return yqb__lse
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks: _bcast_np(data, comm_ranks,
            nranks)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        wzzvi__rkgyt = len(data.columns)
        jra__drmi = ', '.join('g_data_{}'.format(i) for i in range(
            wzzvi__rkgyt))
        ltic__verow = bodo.utils.transform.gen_const_tup(data.columns)
        vqu__ybq = 'def impl_df(data, comm_ranks, nranks):\n'
        for i in range(wzzvi__rkgyt):
            vqu__ybq += (
                '  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})\n'
                .format(i, i))
            vqu__ybq += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks)
"""
                .format(i, i))
        vqu__ybq += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        vqu__ybq += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks)
"""
        vqu__ybq += (
            '  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})\n'
            .format(jra__drmi, ltic__verow))
        ygt__pqzah = {}
        exec(vqu__ybq, {'bodo': bodo}, ygt__pqzah)
        tsfmy__stpk = ygt__pqzah['impl_df']
        return tsfmy__stpk
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            start = data._start
            stop = data._stop
            fflv__zgjur = data._step
            pjtaq__lhvhc = data._name
            pjtaq__lhvhc = bcast_scalar(pjtaq__lhvhc)
            start = bcast_scalar(start)
            stop = bcast_scalar(stop)
            fflv__zgjur = bcast_scalar(fflv__zgjur)
            qku__ldyb = bodo.libs.array_kernels.calc_nitems(start, stop,
                fflv__zgjur)
            chunk_start = bodo.libs.distributed_api.get_start(qku__ldyb,
                n_pes, rank)
            chunk_count = bodo.libs.distributed_api.get_node_portion(qku__ldyb,
                n_pes, rank)
            mfigx__ukos = start + fflv__zgjur * chunk_start
            mpw__ymxz = start + fflv__zgjur * (chunk_start + chunk_count)
            mpw__ymxz = min(mpw__ymxz, stop)
            return bodo.hiframes.pd_index_ext.init_range_index(mfigx__ukos,
                mpw__ymxz, fflv__zgjur, pjtaq__lhvhc)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks):
            kvd__hsumg = data._data
            pjtaq__lhvhc = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(kvd__hsumg,
                comm_ranks, nranks)
            return bodo.utils.conversion.index_from_array(arr, pjtaq__lhvhc)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            pjtaq__lhvhc = bodo.hiframes.pd_series_ext.get_series_name(data)
            rvnis__ytwr = bodo.libs.distributed_api.bcast_comm_impl(
                pjtaq__lhvhc, comm_ranks, nranks)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks)
            mpl__gado = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                mpl__gado, rvnis__ytwr)
        return impl_series
    if isinstance(data, types.BaseTuple):
        vqu__ybq = 'def impl_tuple(data, comm_ranks, nranks):\n'
        vqu__ybq += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks)'.format(i) for i in
            range(len(data))), ',' if len(data) > 0 else '')
        ygt__pqzah = {}
        exec(vqu__ybq, {'bcast_comm_impl': bcast_comm_impl}, ygt__pqzah)
        gyqwo__glndi = ygt__pqzah['impl_tuple']
        return gyqwo__glndi
    if data is types.none:
        return lambda data, comm_ranks, nranks: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks):
    typ_val = numba_to_c_type(data.dtype)
    rej__btti = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    jwr__rlsjh = (0,) * rej__btti

    def bcast_arr_impl(data, comm_ranks, nranks):
        rank = bodo.libs.distributed_api.get_rank()
        kvd__hsumg = np.ascontiguousarray(data)
        ihgb__magcg = data.ctypes
        mwizq__pezam = jwr__rlsjh
        if rank == MPI_ROOT:
            mwizq__pezam = kvd__hsumg.shape
        mwizq__pezam = bcast_tuple(mwizq__pezam)
        uokez__nmita = get_tuple_prod(mwizq__pezam[1:])
        send_counts = mwizq__pezam[0] * uokez__nmita
        vnto__xdhk = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(ihgb__magcg, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks))
            return data
        else:
            c_bcast(vnto__xdhk.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks))
            return vnto__xdhk.reshape((-1,) + mwizq__pezam[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        vucxz__hcnv = MPI.COMM_WORLD
        auyb__tbhu = MPI.Get_processor_name()
        gpic__dooo = vucxz__hcnv.allgather(auyb__tbhu)
        node_ranks = defaultdict(list)
        for i, zrk__dnf in enumerate(gpic__dooo):
            node_ranks[zrk__dnf].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    vucxz__hcnv = MPI.COMM_WORLD
    eiz__jmihr = vucxz__hcnv.Get_group()
    zch__ypk = eiz__jmihr.Incl(comm_ranks)
    wmak__plei = vucxz__hcnv.Create_group(zch__ypk)
    return wmak__plei


def get_nodes_first_ranks():
    qpd__hwbbt = get_host_ranks()
    return np.array([kbvw__vffw[0] for kbvw__vffw in qpd__hwbbt.values()],
        dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
