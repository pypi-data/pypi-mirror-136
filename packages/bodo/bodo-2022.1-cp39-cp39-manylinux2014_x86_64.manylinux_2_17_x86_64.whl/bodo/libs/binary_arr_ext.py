"""Array implementation for binary (bytes) objects, which are usually immutable.
It is equivalent to string array, except that it stores a 'bytes' object for each
element instead of 'str'.
"""
import operator
import llvmlite.binding as ll
import llvmlite.llvmpy.core as lc
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import RefType, impl_ret_borrowed, iternext_impl
from numba.core.typing.templates import signature
from numba.extending import intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.utils.typing import BodoError, is_list_like_index_type
_bytes_fromhex = types.ExternalFunction('bytes_fromhex', types.int64(types.
    voidptr, types.voidptr, types.uint64))
ll.add_symbol('bytes_to_hex', hstr_ext.bytes_to_hex)
ll.add_symbol('bytes_fromhex', hstr_ext.bytes_fromhex)
bytes_type = types.Bytes(types.uint8, 1, 'C', readonly=True)


class BinaryArrayType(types.ArrayCompatible):

    def __init__(self):
        super(BinaryArrayType, self).__init__(name='BinaryArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return bytes_type

    def copy(self):
        return BinaryArrayType()


binary_array_type = BinaryArrayType()


@overload(len, no_unliteral=True)
def bin_arr_len_overload(bin_arr):
    if bin_arr == binary_array_type:
        return lambda bin_arr: len(bin_arr._data)


@overload_attribute(BinaryArrayType, 'size')
def bin_arr_size_overload(bin_arr):
    return lambda bin_arr: len(bin_arr._data)


@overload_attribute(BinaryArrayType, 'shape')
def bin_arr_shape_overload(bin_arr):
    return lambda bin_arr: (len(bin_arr._data),)


@overload_attribute(BinaryArrayType, 'nbytes')
def bin_arr_nbytes_overload(bin_arr):
    return lambda bin_arr: bin_arr._data.nbytes


@overload_attribute(BinaryArrayType, 'ndim')
def overload_bin_arr_ndim(A):
    return lambda A: 1


@overload_attribute(BinaryArrayType, 'dtype')
def overload_bool_arr_dtype(A):
    return lambda A: np.dtype('O')


@numba.njit
def pre_alloc_binary_array(n_bytestrs, n_chars):
    if n_chars is None:
        n_chars = -1
    bin_arr = init_binary_arr(bodo.libs.array_item_arr_ext.
        pre_alloc_array_item_array(np.int64(n_bytestrs), (np.int64(n_chars)
        ,), bodo.libs.str_arr_ext.char_arr_type))
    if n_chars == 0:
        bodo.libs.str_arr_ext.set_all_offsets_to_0(bin_arr)
    return bin_arr


@intrinsic
def init_binary_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, sig, args):
        qha__ull, = args
        ayfhw__rwxl = context.make_helper(builder, binary_array_type)
        ayfhw__rwxl.data = qha__ull
        context.nrt.incref(builder, data_typ, qha__ull)
        return ayfhw__rwxl._getvalue()
    return binary_array_type(data_typ), codegen


@intrinsic
def init_bytes_type(typingctx, data_typ, length_type):
    assert data_typ == types.Array(types.uint8, 1, 'C')
    assert length_type == types.int64

    def codegen(context, builder, sig, args):
        pyl__vxx = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        dby__sheuo = args[1]
        wabv__ffm = cgutils.create_struct_proxy(bytes_type)(context, builder)
        wabv__ffm.meminfo = context.nrt.meminfo_alloc(builder, dby__sheuo)
        wabv__ffm.nitems = dby__sheuo
        wabv__ffm.itemsize = lir.Constant(wabv__ffm.itemsize.type, 1)
        wabv__ffm.data = context.nrt.meminfo_data(builder, wabv__ffm.meminfo)
        wabv__ffm.parent = cgutils.get_null_value(wabv__ffm.parent.type)
        wabv__ffm.shape = cgutils.pack_array(builder, [dby__sheuo], context
            .get_value_type(types.intp))
        wabv__ffm.strides = pyl__vxx.strides
        cgutils.memcpy(builder, wabv__ffm.data, pyl__vxx.data, dby__sheuo)
        return wabv__ffm._getvalue()
    return bytes_type(data_typ, length_type), codegen


@intrinsic
def cast_bytes_uint8array(typingctx, data_typ):
    assert data_typ == bytes_type

    def codegen(context, builder, sig, args):
        return impl_ret_borrowed(context, builder, sig.return_type, args[0])
    return types.Array(types.uint8, 1, 'C')(data_typ), codegen


@overload_method(BinaryArrayType, 'copy', no_unliteral=True)
def binary_arr_copy_overload(arr):

    def copy_impl(arr):
        return init_binary_arr(arr._data.copy())
    return copy_impl


@overload_method(types.Bytes, 'hex')
def binary_arr_hex(arr):
    wefoz__cgn = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def impl(arr):
        dby__sheuo = len(arr) * 2
        output = numba.cpython.unicode._empty_string(wefoz__cgn, dby__sheuo, 1)
        bytes_to_hex(output, arr)
        return output
    return impl


@lower_cast(types.CPointer(types.uint8), types.voidptr)
def cast_uint8_array_to_voidptr(context, builder, fromty, toty, val):
    return val


make_attribute_wrapper(types.Bytes, 'data', '_data')


@overload_method(types.Bytes, '__hash__')
def bytes_hash(arr):

    def impl(arr):
        return numba.cpython.hashing._Py_HashBytes(arr._data, len(arr))
    return impl


@intrinsic
def bytes_to_hex(typingctx, output, arr):

    def codegen(context, builder, sig, args):
        jaugl__wpevk = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        blowg__jpzoe = cgutils.create_struct_proxy(sig.args[1])(context,
            builder, value=args[1])
        xps__ohc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(64)])
        dku__selz = cgutils.get_or_insert_function(builder.module, xps__ohc,
            name='bytes_to_hex')
        builder.call(dku__selz, (jaugl__wpevk.data, blowg__jpzoe.data,
            blowg__jpzoe.nitems))
    return types.void(output, arr), codegen


@overload(operator.getitem, no_unliteral=True)
def binary_arr_getitem(arr, ind):
    if arr != binary_array_type:
        return
    if isinstance(ind, types.Integer):

        def impl(arr, ind):
            eyayp__qkmk = arr._data[ind]
            return init_bytes_type(eyayp__qkmk, len(eyayp__qkmk))
        return impl
    if is_list_like_index_type(ind) and (ind.dtype == types.bool_ or
        isinstance(ind.dtype, types.Integer)) or isinstance(ind, types.
        SliceType):
        return lambda arr, ind: init_binary_arr(arr._data[ind])
    raise BodoError(
        f'getitem for Binary Array with indexing type {ind} not supported.')


def bytes_fromhex(hex_str):
    pass


@overload(bytes_fromhex)
def overload_bytes_fromhex(hex_str):
    hex_str = types.unliteral(hex_str)
    if hex_str == bodo.string_type:
        wefoz__cgn = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(hex_str):
            if not hex_str._is_ascii or hex_str._kind != wefoz__cgn:
                raise TypeError(
                    'bytes.fromhex is only supported on ascii strings')
            qha__ull = np.empty(len(hex_str) // 2, np.uint8)
            dby__sheuo = _bytes_fromhex(qha__ull.ctypes, hex_str._data, len
                (hex_str))
            result = init_bytes_type(qha__ull, dby__sheuo)
            return result
        return impl
    raise BodoError(f'bytes.fromhex not supported with argument type {hex_str}'
        )


@overload(operator.setitem)
def binary_arr_setitem(arr, ind, val):
    if arr != binary_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if val != bytes_type:
        raise BodoError(
            f'setitem for Binary Array only supported with bytes value and integer indexing'
            )
    if isinstance(ind, types.Integer):

        def impl(arr, ind, val):
            arr._data[ind] = bodo.libs.binary_arr_ext.cast_bytes_uint8array(val
                )
        return impl
    raise BodoError(
        f'setitem for Binary Array with indexing type {ind} not supported.')


def create_binary_cmp_op_overload(op):

    def overload_binary_cmp(lhs, rhs):
        pxj__dgcx = lhs == binary_array_type
        mzxp__dtei = rhs == binary_array_type
        cuw__mrt = 'lhs' if pxj__dgcx else 'rhs'
        ryr__diq = 'def impl(lhs, rhs):\n'
        ryr__diq += '  numba.parfors.parfor.init_prange()\n'
        ryr__diq += f'  n = len({cuw__mrt})\n'
        ryr__diq += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n)\n'
        ryr__diq += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        kyxl__ubye = []
        if pxj__dgcx:
            kyxl__ubye.append('bodo.libs.array_kernels.isna(lhs, i)')
        if mzxp__dtei:
            kyxl__ubye.append('bodo.libs.array_kernels.isna(rhs, i)')
        ryr__diq += f"    if {' or '.join(kyxl__ubye)}:\n"
        ryr__diq += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        ryr__diq += '      continue\n'
        weh__rxigg = 'lhs[i]' if pxj__dgcx else 'lhs'
        bfrzl__czt = 'rhs[i]' if mzxp__dtei else 'rhs'
        ryr__diq += f'    out_arr[i] = op({weh__rxigg}, {bfrzl__czt})\n'
        ryr__diq += '  return out_arr\n'
        fshn__hksg = {}
        exec(ryr__diq, {'bodo': bodo, 'numba': numba, 'op': op}, fshn__hksg)
        return fshn__hksg['impl']
    return overload_binary_cmp


class BinaryArrayIterator(types.SimpleIteratorType):

    def __init__(self):
        ldqz__tnib = 'iter(Bytes)'
        kbji__uzn = bytes_type
        super(BinaryArrayIterator, self).__init__(ldqz__tnib, kbji__uzn)


@register_model(BinaryArrayIterator)
class BinaryArrayIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fgsa__fpezl = [('index', types.EphemeralPointer(types.uintp)), (
            'array', binary_array_type)]
        super(BinaryArrayIteratorModel, self).__init__(dmm, fe_type,
            fgsa__fpezl)


lower_builtin('getiter', binary_array_type)(numba.np.arrayobj.getiter_array)


@lower_builtin('iternext', BinaryArrayIterator)
@iternext_impl(RefType.NEW)
def iternext_binary_array(context, builder, sig, args, result):
    [zpftw__meq] = sig.args
    [dcex__ayayc] = args
    hxgcu__cigk = context.make_helper(builder, zpftw__meq, value=dcex__ayayc)
    trgad__ika = signature(types.intp, binary_array_type)
    zgf__yhrh = context.compile_internal(builder, lambda a: len(a),
        trgad__ika, [hxgcu__cigk.array])
    asgq__xxpfg = builder.load(hxgcu__cigk.index)
    yfq__elxeg = builder.icmp(lc.ICMP_SLT, asgq__xxpfg, zgf__yhrh)
    result.set_valid(yfq__elxeg)
    with builder.if_then(yfq__elxeg):
        jhl__tysle = signature(bytes_type, binary_array_type, types.intp)
        pbte__ntwp = context.compile_internal(builder, lambda a, i: a[i],
            jhl__tysle, [hxgcu__cigk.array, asgq__xxpfg])
        result.yield_(pbte__ntwp)
        wxd__zijrq = cgutils.increment_index(builder, asgq__xxpfg)
        builder.store(wxd__zijrq, hxgcu__cigk.index)


def pre_alloc_binary_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


from numba.parfors.array_analysis import ArrayAnalysis
(ArrayAnalysis._analyze_op_call_bodo_libs_binary_arr_ext_pre_alloc_binary_array
    ) = pre_alloc_binary_arr_equiv
