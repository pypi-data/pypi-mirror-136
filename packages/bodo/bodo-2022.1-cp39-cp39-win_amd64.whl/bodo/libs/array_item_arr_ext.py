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
        ktepw__enib = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, ktepw__enib)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        ktepw__enib = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, ktepw__enib)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    ziqjn__kvfge = builder.module
    fzcns__pne = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    nhf__zbn = cgutils.get_or_insert_function(ziqjn__kvfge, fzcns__pne,
        name='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not nhf__zbn.is_declaration:
        return nhf__zbn
    nhf__zbn.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(nhf__zbn.append_basic_block())
    kmel__npid = nhf__zbn.args[0]
    pdm__teqbw = context.get_value_type(payload_type).as_pointer()
    kxw__smf = builder.bitcast(kmel__npid, pdm__teqbw)
    mnme__fxss = context.make_helper(builder, payload_type, ref=kxw__smf)
    context.nrt.decref(builder, array_item_type.dtype, mnme__fxss.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'),
        mnme__fxss.offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        mnme__fxss.null_bitmap)
    builder.ret_void()
    return nhf__zbn


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    ipuj__vhjv = context.get_value_type(payload_type)
    rce__yhrg = context.get_abi_sizeof(ipuj__vhjv)
    jdcdd__pqqy = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    zel__nggp = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, rce__yhrg), jdcdd__pqqy)
    bsqql__slq = context.nrt.meminfo_data(builder, zel__nggp)
    wld__ukvw = builder.bitcast(bsqql__slq, ipuj__vhjv.as_pointer())
    mnme__fxss = cgutils.create_struct_proxy(payload_type)(context, builder)
    mnme__fxss.n_arrays = n_arrays
    iyjy__loltc = n_elems.type.count
    mbfr__ujqa = builder.extract_value(n_elems, 0)
    aclwh__cyz = cgutils.alloca_once_value(builder, mbfr__ujqa)
    omirk__rvtm = builder.icmp_signed('==', mbfr__ujqa, lir.Constant(
        mbfr__ujqa.type, -1))
    with builder.if_then(omirk__rvtm):
        builder.store(n_arrays, aclwh__cyz)
    n_elems = cgutils.pack_array(builder, [builder.load(aclwh__cyz)] + [
        builder.extract_value(n_elems, nwu__qya) for nwu__qya in range(1,
        iyjy__loltc)])
    mnme__fxss.data = gen_allocate_array(context, builder, array_item_type.
        dtype, n_elems, c)
    mgex__pntlt = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    gyevg__scj = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [mgex__pntlt])
    offsets_ptr = gyevg__scj.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    mnme__fxss.offsets = gyevg__scj._getvalue()
    dpz__qtw = builder.udiv(builder.add(n_arrays, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    yqc__vod = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [dpz__qtw])
    null_bitmap_ptr = yqc__vod.data
    mnme__fxss.null_bitmap = yqc__vod._getvalue()
    builder.store(mnme__fxss._getvalue(), wld__ukvw)
    return zel__nggp, mnme__fxss.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    jsqlz__kbjb, ozv__hgl = c.pyapi.call_jit_code(copy_data, sig, [data_arr,
        item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    jqddk__lxb = context.insert_const_string(builder.module, 'pandas')
    erce__mso = c.pyapi.import_module_noblock(jqddk__lxb)
    xoftc__aemf = c.pyapi.object_getattr_string(erce__mso, 'NA')
    frbw__yrz = c.context.get_constant(offset_type, 0)
    builder.store(frbw__yrz, offsets_ptr)
    teoxk__xrho = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as loop:
        ggj__abh = loop.index
        item_ind = builder.load(teoxk__xrho)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [ggj__abh]))
        arr_obj = seq_getitem(builder, context, val, ggj__abh)
        set_bitmap_bit(builder, null_bitmap_ptr, ggj__abh, 0)
        cdh__nvtp = is_na_value(builder, context, arr_obj, xoftc__aemf)
        sxzo__onw = builder.icmp_unsigned('!=', cdh__nvtp, lir.Constant(
            cdh__nvtp.type, 1))
        with builder.if_then(sxzo__onw):
            set_bitmap_bit(builder, null_bitmap_ptr, ggj__abh, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), teoxk__xrho)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(teoxk__xrho), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(erce__mso)
    c.pyapi.decref(xoftc__aemf)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    vgb__nhzac = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if vgb__nhzac:
        fzcns__pne = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        gznyp__fnwds = cgutils.get_or_insert_function(c.builder.module,
            fzcns__pne, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(
            gznyp__fnwds, [val])])
    else:
        vjapt__twe = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            vjapt__twe, nwu__qya) for nwu__qya in range(1, vjapt__twe.type.
            count)])
    zel__nggp, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if vgb__nhzac:
        tlc__njxe = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        nla__xpsgz = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        fzcns__pne = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        nhf__zbn = cgutils.get_or_insert_function(c.builder.module,
            fzcns__pne, name='array_item_array_from_sequence')
        c.builder.call(nhf__zbn, [val, c.builder.bitcast(nla__xpsgz, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), tlc__njxe)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    jksk__uwhq = c.context.make_helper(c.builder, typ)
    jksk__uwhq.meminfo = zel__nggp
    tyaqx__henmu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jksk__uwhq._getvalue(), is_error=tyaqx__henmu)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    jksk__uwhq = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    bsqql__slq = context.nrt.meminfo_data(builder, jksk__uwhq.meminfo)
    wld__ukvw = builder.bitcast(bsqql__slq, context.get_value_type(
        payload_type).as_pointer())
    mnme__fxss = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(wld__ukvw))
    return mnme__fxss


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    jqddk__lxb = context.insert_const_string(builder.module, 'numpy')
    eqymy__zdp = c.pyapi.import_module_noblock(jqddk__lxb)
    dcrp__lmlub = c.pyapi.object_getattr_string(eqymy__zdp, 'object_')
    ugd__yueai = c.pyapi.long_from_longlong(n_arrays)
    uqnfm__cdu = c.pyapi.call_method(eqymy__zdp, 'ndarray', (ugd__yueai,
        dcrp__lmlub))
    lnc__wyh = c.pyapi.object_getattr_string(eqymy__zdp, 'nan')
    teoxk__xrho = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_arrays) as loop:
        ggj__abh = loop.index
        pyarray_setitem(builder, context, uqnfm__cdu, ggj__abh, lnc__wyh)
        fst__kyhez = get_bitmap_bit(builder, null_bitmap_ptr, ggj__abh)
        ytp__jgaxi = builder.icmp_unsigned('!=', fst__kyhez, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(ytp__jgaxi):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(ggj__abh, lir.Constant(ggj__abh.
                type, 1))])), builder.load(builder.gep(offsets_ptr, [
                ggj__abh]))), lir.IntType(64))
            item_ind = builder.load(teoxk__xrho)
            jsqlz__kbjb, xbyi__vzy = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), teoxk__xrho)
            arr_obj = c.pyapi.from_native_value(typ.dtype, xbyi__vzy, c.
                env_manager)
            pyarray_setitem(builder, context, uqnfm__cdu, ggj__abh, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(eqymy__zdp)
    c.pyapi.decref(dcrp__lmlub)
    c.pyapi.decref(ugd__yueai)
    c.pyapi.decref(lnc__wyh)
    return uqnfm__cdu


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    mnme__fxss = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = mnme__fxss.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), mnme__fxss.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), mnme__fxss.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        tlc__njxe = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        nla__xpsgz = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        fzcns__pne = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        gwgr__nmcj = cgutils.get_or_insert_function(c.builder.module,
            fzcns__pne, name='np_array_from_array_item_array')
        arr = c.builder.call(gwgr__nmcj, [mnme__fxss.n_arrays, c.builder.
            bitcast(nla__xpsgz, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), tlc__njxe)])
    else:
        arr = _box_array_item_array_generic(typ, c, mnme__fxss.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    hnau__zyi, grco__gelo, wbcoz__obh = args
    lcem__gzkre = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    ynblx__fbnk = sig.args[1]
    if not isinstance(ynblx__fbnk, types.UniTuple):
        grco__gelo = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), -1) for wbcoz__obh in range(lcem__gzkre)])
    elif ynblx__fbnk.count < lcem__gzkre:
        grco__gelo = cgutils.pack_array(builder, [builder.extract_value(
            grco__gelo, nwu__qya) for nwu__qya in range(ynblx__fbnk.count)] +
            [lir.Constant(lir.IntType(64), -1) for wbcoz__obh in range(
            lcem__gzkre - ynblx__fbnk.count)])
    zel__nggp, wbcoz__obh, wbcoz__obh, wbcoz__obh = construct_array_item_array(
        context, builder, array_item_type, hnau__zyi, grco__gelo)
    jksk__uwhq = context.make_helper(builder, array_item_type)
    jksk__uwhq.meminfo = zel__nggp
    return jksk__uwhq._getvalue()


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
    n_arrays, nhqs__sxnf, gyevg__scj, yqc__vod = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    ipuj__vhjv = context.get_value_type(payload_type)
    rce__yhrg = context.get_abi_sizeof(ipuj__vhjv)
    jdcdd__pqqy = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    zel__nggp = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, rce__yhrg), jdcdd__pqqy)
    bsqql__slq = context.nrt.meminfo_data(builder, zel__nggp)
    wld__ukvw = builder.bitcast(bsqql__slq, ipuj__vhjv.as_pointer())
    mnme__fxss = cgutils.create_struct_proxy(payload_type)(context, builder)
    mnme__fxss.n_arrays = n_arrays
    mnme__fxss.data = nhqs__sxnf
    mnme__fxss.offsets = gyevg__scj
    mnme__fxss.null_bitmap = yqc__vod
    builder.store(mnme__fxss._getvalue(), wld__ukvw)
    context.nrt.incref(builder, signature.args[1], nhqs__sxnf)
    context.nrt.incref(builder, signature.args[2], gyevg__scj)
    context.nrt.incref(builder, signature.args[3], yqc__vod)
    jksk__uwhq = context.make_helper(builder, array_item_type)
    jksk__uwhq.meminfo = zel__nggp
    return jksk__uwhq._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    ciul__worly = ArrayItemArrayType(data_type)
    sig = ciul__worly(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        mnme__fxss = _get_array_item_arr_payload(context, builder, arr_typ, arr
            )
        return impl_ret_borrowed(context, builder, sig.return_type,
            mnme__fxss.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        mnme__fxss = _get_array_item_arr_payload(context, builder, arr_typ, arr
            )
        nla__xpsgz = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, mnme__fxss.offsets).data
        gyevg__scj = builder.bitcast(nla__xpsgz, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(gyevg__scj, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        mnme__fxss = _get_array_item_arr_payload(context, builder, arr_typ, arr
            )
        return impl_ret_borrowed(context, builder, sig.return_type,
            mnme__fxss.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        mnme__fxss = _get_array_item_arr_payload(context, builder, arr_typ, arr
            )
        return impl_ret_borrowed(context, builder, sig.return_type,
            mnme__fxss.null_bitmap)
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
        mnme__fxss = _get_array_item_arr_payload(context, builder, arr_typ, arr
            )
        return mnme__fxss.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, bipgp__ogo = args
        jksk__uwhq = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        bsqql__slq = context.nrt.meminfo_data(builder, jksk__uwhq.meminfo)
        wld__ukvw = builder.bitcast(bsqql__slq, context.get_value_type(
            payload_type).as_pointer())
        mnme__fxss = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(wld__ukvw))
        context.nrt.decref(builder, data_typ, mnme__fxss.data)
        mnme__fxss.data = bipgp__ogo
        context.nrt.incref(builder, data_typ, bipgp__ogo)
        builder.store(mnme__fxss._getvalue(), wld__ukvw)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    nhqs__sxnf = get_data(arr)
    vxss__xexin = len(nhqs__sxnf)
    if vxss__xexin < new_size:
        dlbjb__bgj = max(2 * vxss__xexin, new_size)
        bipgp__ogo = bodo.libs.array_kernels.resize_and_copy(nhqs__sxnf,
            old_size, dlbjb__bgj)
        replace_data_arr(arr, bipgp__ogo)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    nhqs__sxnf = get_data(arr)
    gyevg__scj = get_offsets(arr)
    uuoh__kdh = len(nhqs__sxnf)
    leb__iemos = gyevg__scj[-1]
    if uuoh__kdh != leb__iemos:
        bipgp__ogo = bodo.libs.array_kernels.resize_and_copy(nhqs__sxnf,
            leb__iemos, leb__iemos)
        replace_data_arr(arr, bipgp__ogo)


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
            gyevg__scj = get_offsets(arr)
            nhqs__sxnf = get_data(arr)
            fipwx__jhg = gyevg__scj[ind]
            rkeko__hnmns = gyevg__scj[ind + 1]
            return nhqs__sxnf[fipwx__jhg:rkeko__hnmns]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        sevi__xhhdc = arr.dtype

        def impl_bool(arr, ind):
            mozb__koorl = len(arr)
            if mozb__koorl != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            yqc__vod = get_null_bitmap(arr)
            n_arrays = 0
            rhv__irb = init_nested_counts(sevi__xhhdc)
            for nwu__qya in range(mozb__koorl):
                if ind[nwu__qya]:
                    n_arrays += 1
                    uqtd__kxt = arr[nwu__qya]
                    rhv__irb = add_nested_counts(rhv__irb, uqtd__kxt)
            uqnfm__cdu = pre_alloc_array_item_array(n_arrays, rhv__irb,
                sevi__xhhdc)
            iwo__lrv = get_null_bitmap(uqnfm__cdu)
            piqbu__jlgd = 0
            for vnu__hqkt in range(mozb__koorl):
                if ind[vnu__hqkt]:
                    uqnfm__cdu[piqbu__jlgd] = arr[vnu__hqkt]
                    syk__yjhz = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        yqc__vod, vnu__hqkt)
                    bodo.libs.int_arr_ext.set_bit_to_arr(iwo__lrv,
                        piqbu__jlgd, syk__yjhz)
                    piqbu__jlgd += 1
            return uqnfm__cdu
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        sevi__xhhdc = arr.dtype

        def impl_int(arr, ind):
            yqc__vod = get_null_bitmap(arr)
            mozb__koorl = len(ind)
            n_arrays = mozb__koorl
            rhv__irb = init_nested_counts(sevi__xhhdc)
            for ylbn__tnpzn in range(mozb__koorl):
                nwu__qya = ind[ylbn__tnpzn]
                uqtd__kxt = arr[nwu__qya]
                rhv__irb = add_nested_counts(rhv__irb, uqtd__kxt)
            uqnfm__cdu = pre_alloc_array_item_array(n_arrays, rhv__irb,
                sevi__xhhdc)
            iwo__lrv = get_null_bitmap(uqnfm__cdu)
            for yvo__bmvj in range(mozb__koorl):
                vnu__hqkt = ind[yvo__bmvj]
                uqnfm__cdu[yvo__bmvj] = arr[vnu__hqkt]
                syk__yjhz = bodo.libs.int_arr_ext.get_bit_bitmap_arr(yqc__vod,
                    vnu__hqkt)
                bodo.libs.int_arr_ext.set_bit_to_arr(iwo__lrv, yvo__bmvj,
                    syk__yjhz)
            return uqnfm__cdu
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            mozb__koorl = len(arr)
            fdkcm__ozu = numba.cpython.unicode._normalize_slice(ind,
                mozb__koorl)
            lgazx__syu = np.arange(fdkcm__ozu.start, fdkcm__ozu.stop,
                fdkcm__ozu.step)
            return arr[lgazx__syu]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            gyevg__scj = get_offsets(A)
            yqc__vod = get_null_bitmap(A)
            if idx == 0:
                gyevg__scj[0] = 0
            n_items = len(val)
            zalf__sigeg = gyevg__scj[idx] + n_items
            ensure_data_capacity(A, gyevg__scj[idx], zalf__sigeg)
            nhqs__sxnf = get_data(A)
            gyevg__scj[idx + 1] = gyevg__scj[idx] + n_items
            nhqs__sxnf[gyevg__scj[idx]:gyevg__scj[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(yqc__vod, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            fdkcm__ozu = numba.cpython.unicode._normalize_slice(idx, len(A))
            for nwu__qya in range(fdkcm__ozu.start, fdkcm__ozu.stop,
                fdkcm__ozu.step):
                A[nwu__qya] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            gyevg__scj = get_offsets(A)
            yqc__vod = get_null_bitmap(A)
            fdddd__plsjw = get_offsets(val)
            jlur__qhd = get_data(val)
            qnpyc__uluv = get_null_bitmap(val)
            mozb__koorl = len(A)
            fdkcm__ozu = numba.cpython.unicode._normalize_slice(idx,
                mozb__koorl)
            jxyva__yzzlu, gvmcv__fvn = fdkcm__ozu.start, fdkcm__ozu.stop
            assert fdkcm__ozu.step == 1
            if jxyva__yzzlu == 0:
                gyevg__scj[jxyva__yzzlu] = 0
            txuok__ldbak = gyevg__scj[jxyva__yzzlu]
            zalf__sigeg = txuok__ldbak + len(jlur__qhd)
            ensure_data_capacity(A, txuok__ldbak, zalf__sigeg)
            nhqs__sxnf = get_data(A)
            nhqs__sxnf[txuok__ldbak:txuok__ldbak + len(jlur__qhd)] = jlur__qhd
            gyevg__scj[jxyva__yzzlu:gvmcv__fvn + 1
                ] = fdddd__plsjw + txuok__ldbak
            yhg__hijvp = 0
            for nwu__qya in range(jxyva__yzzlu, gvmcv__fvn):
                syk__yjhz = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    qnpyc__uluv, yhg__hijvp)
                bodo.libs.int_arr_ext.set_bit_to_arr(yqc__vod, nwu__qya,
                    syk__yjhz)
                yhg__hijvp += 1
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
