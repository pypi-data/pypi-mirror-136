import operator
import llvmlite.binding as ll
import numba
import numba.core.typing.typeof
import numpy as np
from llvmlite import ir as lir
from llvmlite.llvmpy.core import Type as LLType
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, impl_ret_new_ref
from numba.extending import box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import offset_type
from bodo.libs.str_arr_ext import _get_str_binary_arr_payload, _memcpy, char_arr_type, get_data_ptr, null_bitmap_arr_type, offset_arr_type, string_array_type
ll.add_symbol('array_setitem', hstr_ext.array_setitem)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
ll.add_symbol('dtor_str_arr_split_view', hstr_ext.dtor_str_arr_split_view)
ll.add_symbol('str_arr_split_view_impl', hstr_ext.str_arr_split_view_impl)
ll.add_symbol('str_arr_split_view_alloc', hstr_ext.str_arr_split_view_alloc)
char_typ = types.uint8
data_ctypes_type = types.ArrayCTypes(types.Array(char_typ, 1, 'C'))
offset_ctypes_type = types.ArrayCTypes(types.Array(offset_type, 1, 'C'))


class StringArraySplitViewType(types.ArrayCompatible):

    def __init__(self):
        super(StringArraySplitViewType, self).__init__(name=
            'StringArraySplitViewType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_array_type

    def copy(self):
        return StringArraySplitViewType()


string_array_split_view_type = StringArraySplitViewType()


class StringArraySplitViewPayloadType(types.Type):

    def __init__(self):
        super(StringArraySplitViewPayloadType, self).__init__(name=
            'StringArraySplitViewPayloadType()')


str_arr_split_view_payload_type = StringArraySplitViewPayloadType()


@register_model(StringArraySplitViewPayloadType)
class StringArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        iic__ftfg = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, iic__ftfg)


str_arr_model_members = [('num_items', types.uint64), ('index_offsets',
    types.CPointer(offset_type)), ('data_offsets', types.CPointer(
    offset_type)), ('data', data_ctypes_type), ('null_bitmap', types.
    CPointer(char_typ)), ('meminfo', types.MemInfoPointer(
    str_arr_split_view_payload_type))]


@register_model(StringArraySplitViewType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        models.StructModel.__init__(self, dmm, fe_type, str_arr_model_members)


make_attribute_wrapper(StringArraySplitViewType, 'num_items', '_num_items')
make_attribute_wrapper(StringArraySplitViewType, 'index_offsets',
    '_index_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data_offsets',
    '_data_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data', '_data')
make_attribute_wrapper(StringArraySplitViewType, 'null_bitmap', '_null_bitmap')


def construct_str_arr_split_view(context, builder):
    apfxg__qaj = context.get_value_type(str_arr_split_view_payload_type)
    knult__egm = context.get_abi_sizeof(apfxg__qaj)
    vddbb__yrb = context.get_value_type(types.voidptr)
    mdq__dxm = context.get_value_type(types.uintp)
    pvty__aikd = lir.FunctionType(lir.VoidType(), [vddbb__yrb, mdq__dxm,
        vddbb__yrb])
    nzn__ahmp = cgutils.get_or_insert_function(builder.module, pvty__aikd,
        name='dtor_str_arr_split_view')
    mgt__drfw = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, knult__egm), nzn__ahmp)
    lhhf__jzkpm = context.nrt.meminfo_data(builder, mgt__drfw)
    upu__fjgsu = builder.bitcast(lhhf__jzkpm, apfxg__qaj.as_pointer())
    return mgt__drfw, upu__fjgsu


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        ovr__bitvn, yogu__mzdw = args
        mgt__drfw, upu__fjgsu = construct_str_arr_split_view(context, builder)
        bcjwk__xvku = _get_str_binary_arr_payload(context, builder,
            ovr__bitvn, string_array_type)
        plpth__mpl = lir.FunctionType(lir.VoidType(), [upu__fjgsu.type, lir
            .IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        tmf__jbb = cgutils.get_or_insert_function(builder.module,
            plpth__mpl, name='str_arr_split_view_impl')
        xjw__glrx = context.make_helper(builder, offset_arr_type,
            bcjwk__xvku.offsets).data
        ccey__vgcsk = context.make_helper(builder, char_arr_type,
            bcjwk__xvku.data).data
        lqf__cjx = context.make_helper(builder, null_bitmap_arr_type,
            bcjwk__xvku.null_bitmap).data
        erfot__mqwbb = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(tmf__jbb, [upu__fjgsu, bcjwk__xvku.n_arrays, xjw__glrx,
            ccey__vgcsk, lqf__cjx, erfot__mqwbb])
        luug__pdkjj = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(upu__fjgsu))
        ysbk__jivrv = context.make_helper(builder, string_array_split_view_type
            )
        ysbk__jivrv.num_items = bcjwk__xvku.n_arrays
        ysbk__jivrv.index_offsets = luug__pdkjj.index_offsets
        ysbk__jivrv.data_offsets = luug__pdkjj.data_offsets
        ysbk__jivrv.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [ovr__bitvn])
        ysbk__jivrv.null_bitmap = luug__pdkjj.null_bitmap
        ysbk__jivrv.meminfo = mgt__drfw
        ejz__sbc = ysbk__jivrv._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, ejz__sbc)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    ehtt__txogx = context.make_helper(builder, string_array_split_view_type,
        val)
    ipgt__avrf = context.insert_const_string(builder.module, 'numpy')
    cjj__low = c.pyapi.import_module_noblock(ipgt__avrf)
    dtype = c.pyapi.object_getattr_string(cjj__low, 'object_')
    flaml__lsi = builder.sext(ehtt__txogx.num_items, c.pyapi.longlong)
    rnrzu__rkl = c.pyapi.long_from_longlong(flaml__lsi)
    yscbk__gcpca = c.pyapi.call_method(cjj__low, 'ndarray', (rnrzu__rkl, dtype)
        )
    ilgxm__oic = LLType.function(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    uhltt__hhb = c.pyapi._get_function(ilgxm__oic, name='array_getptr1')
    fcean__rcyu = LLType.function(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    umvqa__adl = c.pyapi._get_function(fcean__rcyu, name='array_setitem')
    vxzlq__mmka = c.pyapi.object_getattr_string(cjj__low, 'nan')
    with cgutils.for_range(builder, ehtt__txogx.num_items) as loop:
        str_ind = loop.index
        rtzx__bsw = builder.sext(builder.load(builder.gep(ehtt__txogx.
            index_offsets, [str_ind])), lir.IntType(64))
        lndo__dxwdk = builder.sext(builder.load(builder.gep(ehtt__txogx.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        grxf__sxz = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        vobf__ncfr = builder.gep(ehtt__txogx.null_bitmap, [grxf__sxz])
        hcoq__zwf = builder.load(vobf__ncfr)
        lrwks__zhk = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(hcoq__zwf, lrwks__zhk), lir.
            Constant(lir.IntType(8), 1))
        scrbo__ijh = builder.sub(lndo__dxwdk, rtzx__bsw)
        scrbo__ijh = builder.sub(scrbo__ijh, scrbo__ijh.type(1))
        asmr__zlt = builder.call(uhltt__hhb, [yscbk__gcpca, str_ind])
        wqnuz__ukw = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(wqnuz__ukw) as (then, otherwise):
            with then:
                ovs__fqwq = c.pyapi.list_new(scrbo__ijh)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    ovs__fqwq), likely=True):
                    with cgutils.for_range(c.builder, scrbo__ijh) as loop:
                        tdv__szx = builder.add(rtzx__bsw, loop.index)
                        data_start = builder.load(builder.gep(ehtt__txogx.
                            data_offsets, [tdv__szx]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        gltgg__lxpce = builder.load(builder.gep(ehtt__txogx
                            .data_offsets, [builder.add(tdv__szx, tdv__szx.
                            type(1))]))
                        cjig__sdar = builder.gep(builder.extract_value(
                            ehtt__txogx.data, 0), [data_start])
                        dvvm__ozdgh = builder.sext(builder.sub(gltgg__lxpce,
                            data_start), lir.IntType(64))
                        cqy__yvbop = c.pyapi.string_from_string_and_size(
                            cjig__sdar, dvvm__ozdgh)
                        c.pyapi.list_setitem(ovs__fqwq, loop.index, cqy__yvbop)
                builder.call(umvqa__adl, [yscbk__gcpca, asmr__zlt, ovs__fqwq])
            with otherwise:
                builder.call(umvqa__adl, [yscbk__gcpca, asmr__zlt, vxzlq__mmka]
                    )
    c.pyapi.decref(cjj__low)
    c.pyapi.decref(dtype)
    c.pyapi.decref(vxzlq__mmka)
    return yscbk__gcpca


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        ihys__dhnpe, uvmxe__vbde, cjig__sdar = args
        mgt__drfw, upu__fjgsu = construct_str_arr_split_view(context, builder)
        plpth__mpl = lir.FunctionType(lir.VoidType(), [upu__fjgsu.type, lir
            .IntType(64), lir.IntType(64)])
        tmf__jbb = cgutils.get_or_insert_function(builder.module,
            plpth__mpl, name='str_arr_split_view_alloc')
        builder.call(tmf__jbb, [upu__fjgsu, ihys__dhnpe, uvmxe__vbde])
        luug__pdkjj = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(upu__fjgsu))
        ysbk__jivrv = context.make_helper(builder, string_array_split_view_type
            )
        ysbk__jivrv.num_items = ihys__dhnpe
        ysbk__jivrv.index_offsets = luug__pdkjj.index_offsets
        ysbk__jivrv.data_offsets = luug__pdkjj.data_offsets
        ysbk__jivrv.data = cjig__sdar
        ysbk__jivrv.null_bitmap = luug__pdkjj.null_bitmap
        context.nrt.incref(builder, data_t, cjig__sdar)
        ysbk__jivrv.meminfo = mgt__drfw
        ejz__sbc = ysbk__jivrv._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, ejz__sbc)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        ofy__hdlgi, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            ofy__hdlgi = builder.extract_value(ofy__hdlgi, 0)
        return builder.bitcast(builder.gep(ofy__hdlgi, [ind]), lir.IntType(
            8).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        ofy__hdlgi, ind = args
        return builder.load(builder.gep(ofy__hdlgi, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        ofy__hdlgi, ind, ygyra__ubczc = args
        glv__ijxlq = builder.gep(ofy__hdlgi, [ind])
        builder.store(ygyra__ubczc, glv__ijxlq)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        wfby__mww, ind = args
        vsai__myarf = context.make_helper(builder, arr_ctypes_t, wfby__mww)
        kjvhx__kxfm = context.make_helper(builder, arr_ctypes_t)
        kjvhx__kxfm.data = builder.gep(vsai__myarf.data, [ind])
        kjvhx__kxfm.meminfo = vsai__myarf.meminfo
        dgo__jmp = kjvhx__kxfm._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, dgo__jmp)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    wdeu__ceqm = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not wdeu__ceqm:
        return 0, 0, 0
    tdv__szx = getitem_c_arr(arr._index_offsets, item_ind)
    tnzx__bsuex = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    xpfv__xvka = tnzx__bsuex - tdv__szx
    if str_ind >= xpfv__xvka:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, tdv__szx + str_ind)
    data_start += 1
    if tdv__szx + str_ind == 0:
        data_start = 0
    gltgg__lxpce = getitem_c_arr(arr._data_offsets, tdv__szx + str_ind + 1)
    iwcal__zxgnk = gltgg__lxpce - data_start
    return 1, data_start, iwcal__zxgnk


@numba.njit(no_cpython_wrapper=True)
def get_split_view_data_ptr(arr, data_start):
    return get_array_ctypes_ptr(arr._data, data_start)


@overload(len, no_unliteral=True)
def str_arr_split_view_len_overload(arr):
    if arr == string_array_split_view_type:
        return lambda arr: np.int64(arr._num_items)


@overload_attribute(StringArraySplitViewType, 'shape')
def overload_split_view_arr_shape(A):
    return lambda A: (np.int64(A._num_items),)


@overload(operator.getitem, no_unliteral=True)
def str_arr_split_view_getitem_overload(A, ind):
    if A != string_array_split_view_type:
        return
    if A == string_array_split_view_type and isinstance(ind, types.Integer):
        vkt__dyjj = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            tdv__szx = getitem_c_arr(A._index_offsets, ind)
            tnzx__bsuex = getitem_c_arr(A._index_offsets, ind + 1)
            yugb__qjg = tnzx__bsuex - tdv__szx - 1
            ovr__bitvn = bodo.libs.str_arr_ext.pre_alloc_string_array(yugb__qjg
                , -1)
            for kfusl__jspm in range(yugb__qjg):
                data_start = getitem_c_arr(A._data_offsets, tdv__szx +
                    kfusl__jspm)
                data_start += 1
                if tdv__szx + kfusl__jspm == 0:
                    data_start = 0
                gltgg__lxpce = getitem_c_arr(A._data_offsets, tdv__szx +
                    kfusl__jspm + 1)
                iwcal__zxgnk = gltgg__lxpce - data_start
                glv__ijxlq = get_array_ctypes_ptr(A._data, data_start)
                wdwym__wvna = bodo.libs.str_arr_ext.decode_utf8(glv__ijxlq,
                    iwcal__zxgnk)
                ovr__bitvn[kfusl__jspm] = wdwym__wvna
            return ovr__bitvn
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        wslse__grue = offset_type.bitwidth // 8

        def _impl(A, ind):
            yugb__qjg = len(A)
            if yugb__qjg != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            ihys__dhnpe = 0
            uvmxe__vbde = 0
            for kfusl__jspm in range(yugb__qjg):
                if ind[kfusl__jspm]:
                    ihys__dhnpe += 1
                    tdv__szx = getitem_c_arr(A._index_offsets, kfusl__jspm)
                    tnzx__bsuex = getitem_c_arr(A._index_offsets, 
                        kfusl__jspm + 1)
                    uvmxe__vbde += tnzx__bsuex - tdv__szx
            yscbk__gcpca = pre_alloc_str_arr_view(ihys__dhnpe, uvmxe__vbde,
                A._data)
            item_ind = 0
            xug__gmxky = 0
            for kfusl__jspm in range(yugb__qjg):
                if ind[kfusl__jspm]:
                    tdv__szx = getitem_c_arr(A._index_offsets, kfusl__jspm)
                    tnzx__bsuex = getitem_c_arr(A._index_offsets, 
                        kfusl__jspm + 1)
                    qrx__sgugb = tnzx__bsuex - tdv__szx
                    setitem_c_arr(yscbk__gcpca._index_offsets, item_ind,
                        xug__gmxky)
                    glv__ijxlq = get_c_arr_ptr(A._data_offsets, tdv__szx)
                    qaep__vztm = get_c_arr_ptr(yscbk__gcpca._data_offsets,
                        xug__gmxky)
                    _memcpy(qaep__vztm, glv__ijxlq, qrx__sgugb, wslse__grue)
                    wdeu__ceqm = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, kfusl__jspm)
                    bodo.libs.int_arr_ext.set_bit_to_arr(yscbk__gcpca.
                        _null_bitmap, item_ind, wdeu__ceqm)
                    item_ind += 1
                    xug__gmxky += qrx__sgugb
            setitem_c_arr(yscbk__gcpca._index_offsets, item_ind, xug__gmxky)
            return yscbk__gcpca
        return _impl
