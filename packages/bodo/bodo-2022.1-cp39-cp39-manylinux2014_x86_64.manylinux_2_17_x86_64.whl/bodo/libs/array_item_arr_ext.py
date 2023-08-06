"""Array implementation for variable-size array items.
Corresponds to Spark's ArrayType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Variable-size List: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in a contingous data array, while an offsets array marks the
individual arrays. For example:
value:             [[1, 2], [3], None, [5, 4, 6], []]
data:              [1, 2, 3, 5, 4, 6]
offsets:           [0, 2, 3, 3, 6, 6]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, is_iterable_type, is_list_like_index_type
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('array_item_array_from_sequence', array_ext.
    array_item_array_from_sequence)
ll.add_symbol('np_array_from_array_item_array', array_ext.
    np_array_from_array_item_array)
offset_type = types.uint64
np_offset_type = numba.np.numpy_support.as_dtype(offset_type)


class ArrayItemArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        assert bodo.utils.utils.is_array_typ(dtype, False)
        self.dtype = dtype
        super(ArrayItemArrayType, self).__init__(name=
            'ArrayItemArrayType({})'.format(dtype))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return ArrayItemArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class ArrayItemArrayPayloadType(types.Type):

    def __init__(self, array_type):
        self.array_type = array_type
        super(ArrayItemArrayPayloadType, self).__init__(name=
            'ArrayItemArrayPayloadType({})'.format(array_type))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(ArrayItemArrayPayloadType)
class ArrayItemArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qqp__xste = [('n_arrays', types.int64), ('data', fe_type.array_type
            .dtype), ('offsets', types.Array(offset_type, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, qqp__xste)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        qqp__xste = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, qqp__xste)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    eown__xju = builder.module
    nij__tkgq = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    kjk__xace = cgutils.get_or_insert_function(eown__xju, nij__tkgq, name=
        '.dtor.array_item.{}'.format(array_item_type.dtype))
    if not kjk__xace.is_declaration:
        return kjk__xace
    kjk__xace.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(kjk__xace.append_basic_block())
    tuir__intv = kjk__xace.args[0]
    svdh__abx = context.get_value_type(payload_type).as_pointer()
    vfqx__kkzw = builder.bitcast(tuir__intv, svdh__abx)
    qqhtv__iimbp = context.make_helper(builder, payload_type, ref=vfqx__kkzw)
    context.nrt.decref(builder, array_item_type.dtype, qqhtv__iimbp.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'),
        qqhtv__iimbp.offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        qqhtv__iimbp.null_bitmap)
    builder.ret_void()
    return kjk__xace


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    gzfld__dypmg = context.get_value_type(payload_type)
    ppkz__qdqj = context.get_abi_sizeof(gzfld__dypmg)
    yys__izihi = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    nhwld__cdsy = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, ppkz__qdqj), yys__izihi)
    bqbv__ttq = context.nrt.meminfo_data(builder, nhwld__cdsy)
    ivef__aay = builder.bitcast(bqbv__ttq, gzfld__dypmg.as_pointer())
    qqhtv__iimbp = cgutils.create_struct_proxy(payload_type)(context, builder)
    qqhtv__iimbp.n_arrays = n_arrays
    epwnl__pluzr = n_elems.type.count
    imr__dlpca = builder.extract_value(n_elems, 0)
    wwt__vfpli = cgutils.alloca_once_value(builder, imr__dlpca)
    rft__ajvc = builder.icmp_signed('==', imr__dlpca, lir.Constant(
        imr__dlpca.type, -1))
    with builder.if_then(rft__ajvc):
        builder.store(n_arrays, wwt__vfpli)
    n_elems = cgutils.pack_array(builder, [builder.load(wwt__vfpli)] + [
        builder.extract_value(n_elems, vzi__defu) for vzi__defu in range(1,
        epwnl__pluzr)])
    qqhtv__iimbp.data = gen_allocate_array(context, builder,
        array_item_type.dtype, n_elems, c)
    rmvx__kbkc = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    chj__wlwj = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [rmvx__kbkc])
    offsets_ptr = chj__wlwj.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    qqhtv__iimbp.offsets = chj__wlwj._getvalue()
    jiq__zuvzy = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    luzuw__soxts = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [jiq__zuvzy])
    null_bitmap_ptr = luzuw__soxts.data
    qqhtv__iimbp.null_bitmap = luzuw__soxts._getvalue()
    builder.store(qqhtv__iimbp._getvalue(), ivef__aay)
    return nhwld__cdsy, qqhtv__iimbp.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    dmi__zbz, cdlpv__wdadj = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    shwfq__mfw = context.insert_const_string(builder.module, 'pandas')
    trqt__tqejd = c.pyapi.import_module_noblock(shwfq__mfw)
    uzj__yzldu = c.pyapi.object_getattr_string(trqt__tqejd, 'NA')
    uemft__zdt = c.context.get_constant(offset_type, 0)
    builder.store(uemft__zdt, offsets_ptr)
    sdwkn__trnq = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as loop:
        ludz__pgdm = loop.index
        item_ind = builder.load(sdwkn__trnq)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [ludz__pgdm]))
        arr_obj = seq_getitem(builder, context, val, ludz__pgdm)
        set_bitmap_bit(builder, null_bitmap_ptr, ludz__pgdm, 0)
        lcx__mvqtk = is_na_value(builder, context, arr_obj, uzj__yzldu)
        isvxd__kzed = builder.icmp_unsigned('!=', lcx__mvqtk, lir.Constant(
            lcx__mvqtk.type, 1))
        with builder.if_then(isvxd__kzed):
            set_bitmap_bit(builder, null_bitmap_ptr, ludz__pgdm, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), sdwkn__trnq)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(sdwkn__trnq), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(trqt__tqejd)
    c.pyapi.decref(uzj__yzldu)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    kvccy__yhcu = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if kvccy__yhcu:
        nij__tkgq = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        cota__rpeo = cgutils.get_or_insert_function(c.builder.module,
            nij__tkgq, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(cota__rpeo,
            [val])])
    else:
        vhazx__vnu = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            vhazx__vnu, vzi__defu) for vzi__defu in range(1, vhazx__vnu.
            type.count)])
    nhwld__cdsy, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if kvccy__yhcu:
        joewy__ork = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        rwj__jshfh = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        nij__tkgq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        kjk__xace = cgutils.get_or_insert_function(c.builder.module,
            nij__tkgq, name='array_item_array_from_sequence')
        c.builder.call(kjk__xace, [val, c.builder.bitcast(rwj__jshfh, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), joewy__ork)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    qid__toxl = c.context.make_helper(c.builder, typ)
    qid__toxl.meminfo = nhwld__cdsy
    vvsh__cfrjp = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(qid__toxl._getvalue(), is_error=vvsh__cfrjp)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    qid__toxl = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    bqbv__ttq = context.nrt.meminfo_data(builder, qid__toxl.meminfo)
    ivef__aay = builder.bitcast(bqbv__ttq, context.get_value_type(
        payload_type).as_pointer())
    qqhtv__iimbp = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(ivef__aay))
    return qqhtv__iimbp


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    shwfq__mfw = context.insert_const_string(builder.module, 'numpy')
    bcjd__zzscd = c.pyapi.import_module_noblock(shwfq__mfw)
    offto__njnb = c.pyapi.object_getattr_string(bcjd__zzscd, 'object_')
    hsw__qwhwp = c.pyapi.long_from_longlong(n_arrays)
    ref__hkpsz = c.pyapi.call_method(bcjd__zzscd, 'ndarray', (hsw__qwhwp,
        offto__njnb))
    hwrvm__bwu = c.pyapi.object_getattr_string(bcjd__zzscd, 'nan')
    sdwkn__trnq = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_arrays) as loop:
        ludz__pgdm = loop.index
        pyarray_setitem(builder, context, ref__hkpsz, ludz__pgdm, hwrvm__bwu)
        bqz__cnpgo = get_bitmap_bit(builder, null_bitmap_ptr, ludz__pgdm)
        zyfla__oqr = builder.icmp_unsigned('!=', bqz__cnpgo, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(zyfla__oqr):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(ludz__pgdm, lir.Constant(
                ludz__pgdm.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [ludz__pgdm]))), lir.IntType(64))
            item_ind = builder.load(sdwkn__trnq)
            dmi__zbz, xeo__ojlf = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), sdwkn__trnq)
            arr_obj = c.pyapi.from_native_value(typ.dtype, xeo__ojlf, c.
                env_manager)
            pyarray_setitem(builder, context, ref__hkpsz, ludz__pgdm, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(bcjd__zzscd)
    c.pyapi.decref(offto__njnb)
    c.pyapi.decref(hsw__qwhwp)
    c.pyapi.decref(hwrvm__bwu)
    return ref__hkpsz


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    qqhtv__iimbp = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = qqhtv__iimbp.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), qqhtv__iimbp.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), qqhtv__iimbp.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        joewy__ork = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        rwj__jshfh = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        nij__tkgq = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        mwecv__vgqen = cgutils.get_or_insert_function(c.builder.module,
            nij__tkgq, name='np_array_from_array_item_array')
        arr = c.builder.call(mwecv__vgqen, [qqhtv__iimbp.n_arrays, c.
            builder.bitcast(rwj__jshfh, lir.IntType(8).as_pointer()),
            offsets_ptr, null_bitmap_ptr, lir.Constant(lir.IntType(32),
            joewy__ork)])
    else:
        arr = _box_array_item_array_generic(typ, c, qqhtv__iimbp.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    befy__nlwy, fsz__dnjz, pjt__ecxm = args
    fjg__xlcx = bodo.utils.transform.get_type_alloc_counts(array_item_type.
        dtype)
    qnd__mpp = sig.args[1]
    if not isinstance(qnd__mpp, types.UniTuple):
        fsz__dnjz = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), -1) for pjt__ecxm in range(fjg__xlcx)])
    elif qnd__mpp.count < fjg__xlcx:
        fsz__dnjz = cgutils.pack_array(builder, [builder.extract_value(
            fsz__dnjz, vzi__defu) for vzi__defu in range(qnd__mpp.count)] +
            [lir.Constant(lir.IntType(64), -1) for pjt__ecxm in range(
            fjg__xlcx - qnd__mpp.count)])
    nhwld__cdsy, pjt__ecxm, pjt__ecxm, pjt__ecxm = construct_array_item_array(
        context, builder, array_item_type, befy__nlwy, fsz__dnjz)
    qid__toxl = context.make_helper(builder, array_item_type)
    qid__toxl.meminfo = nhwld__cdsy
    return qid__toxl._getvalue()


@intrinsic
def pre_alloc_array_item_array(typingctx, num_arrs_typ, num_values_typ,
    dtype_typ=None):
    assert isinstance(num_arrs_typ, types.Integer)
    array_item_type = ArrayItemArrayType(dtype_typ.instance_type)
    num_values_typ = types.unliteral(num_values_typ)
    return array_item_type(types.int64, num_values_typ, dtype_typ
        ), lower_pre_alloc_array_item_array


def pre_alloc_array_item_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_array_item_arr_ext_pre_alloc_array_item_array
    ) = pre_alloc_array_item_array_equiv


def init_array_item_array_codegen(context, builder, signature, args):
    n_arrays, ctzh__aiv, chj__wlwj, luzuw__soxts = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    gzfld__dypmg = context.get_value_type(payload_type)
    ppkz__qdqj = context.get_abi_sizeof(gzfld__dypmg)
    yys__izihi = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    nhwld__cdsy = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, ppkz__qdqj), yys__izihi)
    bqbv__ttq = context.nrt.meminfo_data(builder, nhwld__cdsy)
    ivef__aay = builder.bitcast(bqbv__ttq, gzfld__dypmg.as_pointer())
    qqhtv__iimbp = cgutils.create_struct_proxy(payload_type)(context, builder)
    qqhtv__iimbp.n_arrays = n_arrays
    qqhtv__iimbp.data = ctzh__aiv
    qqhtv__iimbp.offsets = chj__wlwj
    qqhtv__iimbp.null_bitmap = luzuw__soxts
    builder.store(qqhtv__iimbp._getvalue(), ivef__aay)
    context.nrt.incref(builder, signature.args[1], ctzh__aiv)
    context.nrt.incref(builder, signature.args[2], chj__wlwj)
    context.nrt.incref(builder, signature.args[3], luzuw__soxts)
    qid__toxl = context.make_helper(builder, array_item_type)
    qid__toxl.meminfo = nhwld__cdsy
    return qid__toxl._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    tarrh__yytc = ArrayItemArrayType(data_type)
    sig = tarrh__yytc(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        qqhtv__iimbp = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            qqhtv__iimbp.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        qqhtv__iimbp = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        rwj__jshfh = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, qqhtv__iimbp.offsets).data
        chj__wlwj = builder.bitcast(rwj__jshfh, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(chj__wlwj, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        qqhtv__iimbp = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            qqhtv__iimbp.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        qqhtv__iimbp = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            qqhtv__iimbp.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


def alias_ext_single_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_offsets',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_data',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_null_bitmap',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array


@intrinsic
def get_n_arrays(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        qqhtv__iimbp = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        return qqhtv__iimbp.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, azoo__dihn = args
        qid__toxl = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        bqbv__ttq = context.nrt.meminfo_data(builder, qid__toxl.meminfo)
        ivef__aay = builder.bitcast(bqbv__ttq, context.get_value_type(
            payload_type).as_pointer())
        qqhtv__iimbp = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(ivef__aay))
        context.nrt.decref(builder, data_typ, qqhtv__iimbp.data)
        qqhtv__iimbp.data = azoo__dihn
        context.nrt.incref(builder, data_typ, azoo__dihn)
        builder.store(qqhtv__iimbp._getvalue(), ivef__aay)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    ctzh__aiv = get_data(arr)
    lqonk__vvdkf = len(ctzh__aiv)
    if lqonk__vvdkf < new_size:
        cmtw__fzjkr = max(2 * lqonk__vvdkf, new_size)
        azoo__dihn = bodo.libs.array_kernels.resize_and_copy(ctzh__aiv,
            old_size, cmtw__fzjkr)
        replace_data_arr(arr, azoo__dihn)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    ctzh__aiv = get_data(arr)
    chj__wlwj = get_offsets(arr)
    vujus__kbfom = len(ctzh__aiv)
    fdr__wkoyf = chj__wlwj[-1]
    if vujus__kbfom != fdr__wkoyf:
        azoo__dihn = bodo.libs.array_kernels.resize_and_copy(ctzh__aiv,
            fdr__wkoyf, fdr__wkoyf)
        replace_data_arr(arr, azoo__dihn)


@overload(len, no_unliteral=True)
def overload_array_item_arr_len(A):
    if isinstance(A, ArrayItemArrayType):
        return lambda A: get_n_arrays(A)


@overload_attribute(ArrayItemArrayType, 'shape')
def overload_array_item_arr_shape(A):
    return lambda A: (get_n_arrays(A),)


@overload_attribute(ArrayItemArrayType, 'dtype')
def overload_array_item_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(ArrayItemArrayType, 'ndim')
def overload_array_item_arr_ndim(A):
    return lambda A: 1


@overload_attribute(ArrayItemArrayType, 'nbytes')
def overload_array_item_arr_nbytes(A):
    return lambda A: get_data(A).nbytes + get_offsets(A
        ).nbytes + get_null_bitmap(A).nbytes


@overload(operator.getitem, no_unliteral=True)
def array_item_arr_getitem_array(arr, ind):
    if not isinstance(arr, ArrayItemArrayType):
        return
    if isinstance(ind, types.Integer):

        def array_item_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            chj__wlwj = get_offsets(arr)
            ctzh__aiv = get_data(arr)
            cato__bwr = chj__wlwj[ind]
            pzzwv__pqau = chj__wlwj[ind + 1]
            return ctzh__aiv[cato__bwr:pzzwv__pqau]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        ryx__pne = arr.dtype

        def impl_bool(arr, ind):
            szz__kldc = len(arr)
            if szz__kldc != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            luzuw__soxts = get_null_bitmap(arr)
            n_arrays = 0
            ylh__ilib = init_nested_counts(ryx__pne)
            for vzi__defu in range(szz__kldc):
                if ind[vzi__defu]:
                    n_arrays += 1
                    cwp__kguzw = arr[vzi__defu]
                    ylh__ilib = add_nested_counts(ylh__ilib, cwp__kguzw)
            ref__hkpsz = pre_alloc_array_item_array(n_arrays, ylh__ilib,
                ryx__pne)
            kizp__tts = get_null_bitmap(ref__hkpsz)
            ntjd__lcs = 0
            for llqgs__qey in range(szz__kldc):
                if ind[llqgs__qey]:
                    ref__hkpsz[ntjd__lcs] = arr[llqgs__qey]
                    diif__sndzd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        luzuw__soxts, llqgs__qey)
                    bodo.libs.int_arr_ext.set_bit_to_arr(kizp__tts,
                        ntjd__lcs, diif__sndzd)
                    ntjd__lcs += 1
            return ref__hkpsz
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        ryx__pne = arr.dtype

        def impl_int(arr, ind):
            luzuw__soxts = get_null_bitmap(arr)
            szz__kldc = len(ind)
            n_arrays = szz__kldc
            ylh__ilib = init_nested_counts(ryx__pne)
            for pqfb__qkxa in range(szz__kldc):
                vzi__defu = ind[pqfb__qkxa]
                cwp__kguzw = arr[vzi__defu]
                ylh__ilib = add_nested_counts(ylh__ilib, cwp__kguzw)
            ref__hkpsz = pre_alloc_array_item_array(n_arrays, ylh__ilib,
                ryx__pne)
            kizp__tts = get_null_bitmap(ref__hkpsz)
            for oycy__jbnu in range(szz__kldc):
                llqgs__qey = ind[oycy__jbnu]
                ref__hkpsz[oycy__jbnu] = arr[llqgs__qey]
                diif__sndzd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    luzuw__soxts, llqgs__qey)
                bodo.libs.int_arr_ext.set_bit_to_arr(kizp__tts, oycy__jbnu,
                    diif__sndzd)
            return ref__hkpsz
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            szz__kldc = len(arr)
            xhgsd__kpuv = numba.cpython.unicode._normalize_slice(ind, szz__kldc
                )
            idrce__xgja = np.arange(xhgsd__kpuv.start, xhgsd__kpuv.stop,
                xhgsd__kpuv.step)
            return arr[idrce__xgja]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            chj__wlwj = get_offsets(A)
            luzuw__soxts = get_null_bitmap(A)
            if idx == 0:
                chj__wlwj[0] = 0
            n_items = len(val)
            dams__wzbp = chj__wlwj[idx] + n_items
            ensure_data_capacity(A, chj__wlwj[idx], dams__wzbp)
            ctzh__aiv = get_data(A)
            chj__wlwj[idx + 1] = chj__wlwj[idx] + n_items
            ctzh__aiv[chj__wlwj[idx]:chj__wlwj[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(luzuw__soxts, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            xhgsd__kpuv = numba.cpython.unicode._normalize_slice(idx, len(A))
            for vzi__defu in range(xhgsd__kpuv.start, xhgsd__kpuv.stop,
                xhgsd__kpuv.step):
                A[vzi__defu] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            chj__wlwj = get_offsets(A)
            luzuw__soxts = get_null_bitmap(A)
            dxqpy__selql = get_offsets(val)
            dbml__axrvn = get_data(val)
            arbwm__kkpa = get_null_bitmap(val)
            szz__kldc = len(A)
            xhgsd__kpuv = numba.cpython.unicode._normalize_slice(idx, szz__kldc
                )
            drw__ptqkk, yibl__vqiqq = xhgsd__kpuv.start, xhgsd__kpuv.stop
            assert xhgsd__kpuv.step == 1
            if drw__ptqkk == 0:
                chj__wlwj[drw__ptqkk] = 0
            vlezk__kxv = chj__wlwj[drw__ptqkk]
            dams__wzbp = vlezk__kxv + len(dbml__axrvn)
            ensure_data_capacity(A, vlezk__kxv, dams__wzbp)
            ctzh__aiv = get_data(A)
            ctzh__aiv[vlezk__kxv:vlezk__kxv + len(dbml__axrvn)] = dbml__axrvn
            chj__wlwj[drw__ptqkk:yibl__vqiqq + 1] = dxqpy__selql + vlezk__kxv
            snldm__uxpl = 0
            for vzi__defu in range(drw__ptqkk, yibl__vqiqq):
                diif__sndzd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    arbwm__kkpa, snldm__uxpl)
                bodo.libs.int_arr_ext.set_bit_to_arr(luzuw__soxts,
                    vzi__defu, diif__sndzd)
                snldm__uxpl += 1
        return impl_slice
    raise BodoError(
        'only setitem with scalar index is currently supported for list arrays'
        )


@overload_method(ArrayItemArrayType, 'copy', no_unliteral=True)
def overload_array_item_arr_copy(A):

    def copy_impl(A):
        return init_array_item_array(len(A), get_data(A).copy(),
            get_offsets(A).copy(), get_null_bitmap(A).copy())
    return copy_impl
