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
        gyo__zgxwb = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, gyo__zgxwb)


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
    dby__ppm = context.get_value_type(str_arr_split_view_payload_type)
    czc__eeld = context.get_abi_sizeof(dby__ppm)
    ffpy__tpayj = context.get_value_type(types.voidptr)
    jhlal__brsop = context.get_value_type(types.uintp)
    sjwgm__zuvyi = lir.FunctionType(lir.VoidType(), [ffpy__tpayj,
        jhlal__brsop, ffpy__tpayj])
    vqo__eboc = cgutils.get_or_insert_function(builder.module, sjwgm__zuvyi,
        name='dtor_str_arr_split_view')
    cflcq__nczk = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, czc__eeld), vqo__eboc)
    lxeyw__uzgpr = context.nrt.meminfo_data(builder, cflcq__nczk)
    poel__mxdw = builder.bitcast(lxeyw__uzgpr, dby__ppm.as_pointer())
    return cflcq__nczk, poel__mxdw


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        oir__wqksa, cdsqv__hwy = args
        cflcq__nczk, poel__mxdw = construct_str_arr_split_view(context, builder
            )
        gjoo__zlnyd = _get_str_binary_arr_payload(context, builder,
            oir__wqksa, string_array_type)
        xfm__cwk = lir.FunctionType(lir.VoidType(), [poel__mxdw.type, lir.
            IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        enmh__tide = cgutils.get_or_insert_function(builder.module,
            xfm__cwk, name='str_arr_split_view_impl')
        ljuey__ylyku = context.make_helper(builder, offset_arr_type,
            gjoo__zlnyd.offsets).data
        igcjr__vcwo = context.make_helper(builder, char_arr_type,
            gjoo__zlnyd.data).data
        hppn__pwhxu = context.make_helper(builder, null_bitmap_arr_type,
            gjoo__zlnyd.null_bitmap).data
        aqjv__gus = context.get_constant(types.int8, ord(sep_typ.literal_value)
            )
        builder.call(enmh__tide, [poel__mxdw, gjoo__zlnyd.n_arrays,
            ljuey__ylyku, igcjr__vcwo, hppn__pwhxu, aqjv__gus])
        gwrry__egl = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(poel__mxdw))
        rai__kal = context.make_helper(builder, string_array_split_view_type)
        rai__kal.num_items = gjoo__zlnyd.n_arrays
        rai__kal.index_offsets = gwrry__egl.index_offsets
        rai__kal.data_offsets = gwrry__egl.data_offsets
        rai__kal.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [oir__wqksa])
        rai__kal.null_bitmap = gwrry__egl.null_bitmap
        rai__kal.meminfo = cflcq__nczk
        zrer__tng = rai__kal._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, zrer__tng)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    njgid__xfd = context.make_helper(builder, string_array_split_view_type, val
        )
    wro__lku = context.insert_const_string(builder.module, 'numpy')
    xex__ljjb = c.pyapi.import_module_noblock(wro__lku)
    dtype = c.pyapi.object_getattr_string(xex__ljjb, 'object_')
    dvsoc__gdte = builder.sext(njgid__xfd.num_items, c.pyapi.longlong)
    wyd__cko = c.pyapi.long_from_longlong(dvsoc__gdte)
    pbsv__eadg = c.pyapi.call_method(xex__ljjb, 'ndarray', (wyd__cko, dtype))
    coyo__rxx = LLType.function(lir.IntType(8).as_pointer(), [c.pyapi.pyobj,
        c.pyapi.py_ssize_t])
    tixnd__nacym = c.pyapi._get_function(coyo__rxx, name='array_getptr1')
    gsai__quz = LLType.function(lir.VoidType(), [c.pyapi.pyobj, lir.IntType
        (8).as_pointer(), c.pyapi.pyobj])
    cwmn__qist = c.pyapi._get_function(gsai__quz, name='array_setitem')
    ehn__kbycz = c.pyapi.object_getattr_string(xex__ljjb, 'nan')
    with cgutils.for_range(builder, njgid__xfd.num_items) as loop:
        str_ind = loop.index
        oth__jkom = builder.sext(builder.load(builder.gep(njgid__xfd.
            index_offsets, [str_ind])), lir.IntType(64))
        tth__xjplu = builder.sext(builder.load(builder.gep(njgid__xfd.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        oak__nuht = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        wlav__jzyqq = builder.gep(njgid__xfd.null_bitmap, [oak__nuht])
        cxn__zntos = builder.load(wlav__jzyqq)
        pxwhg__hqvcg = builder.trunc(builder.and_(str_ind, lir.Constant(lir
            .IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(cxn__zntos, pxwhg__hqvcg), lir.
            Constant(lir.IntType(8), 1))
        zsug__zsgt = builder.sub(tth__xjplu, oth__jkom)
        zsug__zsgt = builder.sub(zsug__zsgt, zsug__zsgt.type(1))
        gej__kampw = builder.call(tixnd__nacym, [pbsv__eadg, str_ind])
        zjht__nkao = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(zjht__nkao) as (then, otherwise):
            with then:
                kjhz__ximts = c.pyapi.list_new(zsug__zsgt)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    kjhz__ximts), likely=True):
                    with cgutils.for_range(c.builder, zsug__zsgt) as loop:
                        yfz__uivoy = builder.add(oth__jkom, loop.index)
                        data_start = builder.load(builder.gep(njgid__xfd.
                            data_offsets, [yfz__uivoy]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        pqz__etqd = builder.load(builder.gep(njgid__xfd.
                            data_offsets, [builder.add(yfz__uivoy,
                            yfz__uivoy.type(1))]))
                        kleb__cpiw = builder.gep(builder.extract_value(
                            njgid__xfd.data, 0), [data_start])
                        eyq__kxfu = builder.sext(builder.sub(pqz__etqd,
                            data_start), lir.IntType(64))
                        bysfl__zonn = c.pyapi.string_from_string_and_size(
                            kleb__cpiw, eyq__kxfu)
                        c.pyapi.list_setitem(kjhz__ximts, loop.index,
                            bysfl__zonn)
                builder.call(cwmn__qist, [pbsv__eadg, gej__kampw, kjhz__ximts])
            with otherwise:
                builder.call(cwmn__qist, [pbsv__eadg, gej__kampw, ehn__kbycz])
    c.pyapi.decref(xex__ljjb)
    c.pyapi.decref(dtype)
    c.pyapi.decref(ehn__kbycz)
    return pbsv__eadg


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        hrpvk__brim, jkj__bsjla, kleb__cpiw = args
        cflcq__nczk, poel__mxdw = construct_str_arr_split_view(context, builder
            )
        xfm__cwk = lir.FunctionType(lir.VoidType(), [poel__mxdw.type, lir.
            IntType(64), lir.IntType(64)])
        enmh__tide = cgutils.get_or_insert_function(builder.module,
            xfm__cwk, name='str_arr_split_view_alloc')
        builder.call(enmh__tide, [poel__mxdw, hrpvk__brim, jkj__bsjla])
        gwrry__egl = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(poel__mxdw))
        rai__kal = context.make_helper(builder, string_array_split_view_type)
        rai__kal.num_items = hrpvk__brim
        rai__kal.index_offsets = gwrry__egl.index_offsets
        rai__kal.data_offsets = gwrry__egl.data_offsets
        rai__kal.data = kleb__cpiw
        rai__kal.null_bitmap = gwrry__egl.null_bitmap
        context.nrt.incref(builder, data_t, kleb__cpiw)
        rai__kal.meminfo = cflcq__nczk
        zrer__tng = rai__kal._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, zrer__tng)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        efti__iqpd, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            efti__iqpd = builder.extract_value(efti__iqpd, 0)
        return builder.bitcast(builder.gep(efti__iqpd, [ind]), lir.IntType(
            8).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        efti__iqpd, ind = args
        return builder.load(builder.gep(efti__iqpd, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        efti__iqpd, ind, fhfbp__ixb = args
        crgg__ckwi = builder.gep(efti__iqpd, [ind])
        builder.store(fhfbp__ixb, crgg__ckwi)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        lndi__cytvx, ind = args
        rlvl__mni = context.make_helper(builder, arr_ctypes_t, lndi__cytvx)
        btol__fhisp = context.make_helper(builder, arr_ctypes_t)
        btol__fhisp.data = builder.gep(rlvl__mni.data, [ind])
        btol__fhisp.meminfo = rlvl__mni.meminfo
        nhhbh__hye = btol__fhisp._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, nhhbh__hye)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    nmlf__wajtq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not nmlf__wajtq:
        return 0, 0, 0
    yfz__uivoy = getitem_c_arr(arr._index_offsets, item_ind)
    ohznh__vrjt = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    rmvgp__uta = ohznh__vrjt - yfz__uivoy
    if str_ind >= rmvgp__uta:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, yfz__uivoy + str_ind)
    data_start += 1
    if yfz__uivoy + str_ind == 0:
        data_start = 0
    pqz__etqd = getitem_c_arr(arr._data_offsets, yfz__uivoy + str_ind + 1)
    ymdl__movz = pqz__etqd - data_start
    return 1, data_start, ymdl__movz


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
        sgdfq__crg = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            yfz__uivoy = getitem_c_arr(A._index_offsets, ind)
            ohznh__vrjt = getitem_c_arr(A._index_offsets, ind + 1)
            cpzvo__clm = ohznh__vrjt - yfz__uivoy - 1
            oir__wqksa = bodo.libs.str_arr_ext.pre_alloc_string_array(
                cpzvo__clm, -1)
            for nyyct__tvrfy in range(cpzvo__clm):
                data_start = getitem_c_arr(A._data_offsets, yfz__uivoy +
                    nyyct__tvrfy)
                data_start += 1
                if yfz__uivoy + nyyct__tvrfy == 0:
                    data_start = 0
                pqz__etqd = getitem_c_arr(A._data_offsets, yfz__uivoy +
                    nyyct__tvrfy + 1)
                ymdl__movz = pqz__etqd - data_start
                crgg__ckwi = get_array_ctypes_ptr(A._data, data_start)
                iwip__kuwaq = bodo.libs.str_arr_ext.decode_utf8(crgg__ckwi,
                    ymdl__movz)
                oir__wqksa[nyyct__tvrfy] = iwip__kuwaq
            return oir__wqksa
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        cwxvc__hjofs = offset_type.bitwidth // 8

        def _impl(A, ind):
            cpzvo__clm = len(A)
            if cpzvo__clm != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            hrpvk__brim = 0
            jkj__bsjla = 0
            for nyyct__tvrfy in range(cpzvo__clm):
                if ind[nyyct__tvrfy]:
                    hrpvk__brim += 1
                    yfz__uivoy = getitem_c_arr(A._index_offsets, nyyct__tvrfy)
                    ohznh__vrjt = getitem_c_arr(A._index_offsets, 
                        nyyct__tvrfy + 1)
                    jkj__bsjla += ohznh__vrjt - yfz__uivoy
            pbsv__eadg = pre_alloc_str_arr_view(hrpvk__brim, jkj__bsjla, A.
                _data)
            item_ind = 0
            gqc__kqnhv = 0
            for nyyct__tvrfy in range(cpzvo__clm):
                if ind[nyyct__tvrfy]:
                    yfz__uivoy = getitem_c_arr(A._index_offsets, nyyct__tvrfy)
                    ohznh__vrjt = getitem_c_arr(A._index_offsets, 
                        nyyct__tvrfy + 1)
                    nsyzq__hekes = ohznh__vrjt - yfz__uivoy
                    setitem_c_arr(pbsv__eadg._index_offsets, item_ind,
                        gqc__kqnhv)
                    crgg__ckwi = get_c_arr_ptr(A._data_offsets, yfz__uivoy)
                    ifcsz__gdjpr = get_c_arr_ptr(pbsv__eadg._data_offsets,
                        gqc__kqnhv)
                    _memcpy(ifcsz__gdjpr, crgg__ckwi, nsyzq__hekes,
                        cwxvc__hjofs)
                    nmlf__wajtq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, nyyct__tvrfy)
                    bodo.libs.int_arr_ext.set_bit_to_arr(pbsv__eadg.
                        _null_bitmap, item_ind, nmlf__wajtq)
                    item_ind += 1
                    gqc__kqnhv += nsyzq__hekes
            setitem_c_arr(pbsv__eadg._index_offsets, item_ind, gqc__kqnhv)
            return pbsv__eadg
        return _impl
