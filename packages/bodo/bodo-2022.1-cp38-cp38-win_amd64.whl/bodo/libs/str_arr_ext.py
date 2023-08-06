"""Array implementation for string objects, which are usually immutable.
The characters are stored in a contingous data array, and an offsets array marks the
the individual strings. For example:
value:             ['a', 'bc', '', 'abc', None, 'bb']
data:              [a, b, c, a, b, c, b, b]
offsets:           [0, 1, 3, 3, 6, 6, 8]
"""
import glob
import operator
import llvmlite.llvmpy.core as lc
import numba
import numba.core.typing.typeof
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.imputils import RefType, impl_ret_borrowed, iternext_impl, lower_constant
from numba.core.typing.templates import signature
from numba.core.unsafe.bytes import memcpy_region
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, type_callable, typeof_impl, unbox
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayPayloadType, ArrayItemArrayType, _get_array_item_arr_payload, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, pre_alloc_binary_array
from bodo.libs.str_ext import memcmp, string_type, unicode_to_utf8_and_len
from bodo.utils.typing import BodoError, is_list_like_index_type, is_overload_constant_int, is_overload_none, is_overload_true, parse_dtype, raise_bodo_error
use_pd_string_array = False
char_type = types.uint8
char_arr_type = types.Array(char_type, 1, 'C')
offset_arr_type = types.Array(offset_type, 1, 'C')
null_bitmap_arr_type = types.Array(types.uint8, 1, 'C')
data_ctypes_type = types.ArrayCTypes(char_arr_type)
offset_ctypes_type = types.ArrayCTypes(offset_arr_type)


class StringArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self):
        super(StringArrayType, self).__init__(name='StringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    @property
    def iterator_type(self):
        return StringArrayIterator()

    def copy(self):
        return StringArrayType()


string_array_type = StringArrayType()


@typeof_impl.register(pd.arrays.StringArray)
def typeof_string_array(val, c):
    return string_array_type


@register_model(BinaryArrayType)
@register_model(StringArrayType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tdfj__rlwn = ArrayItemArrayType(char_arr_type)
        emvh__hczfd = [('data', tdfj__rlwn)]
        models.StructModel.__init__(self, dmm, fe_type, emvh__hczfd)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        kyka__jxsld, = args
        jzqmn__caxsi = context.make_helper(builder, string_array_type)
        jzqmn__caxsi.data = kyka__jxsld
        context.nrt.incref(builder, data_typ, kyka__jxsld)
        return jzqmn__caxsi._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    ayb__vjh = c.context.insert_const_string(c.builder.module, 'pandas')
    rtl__xjuj = c.pyapi.import_module_noblock(ayb__vjh)
    gdxk__ltiki = c.pyapi.call_method(rtl__xjuj, 'StringDtype', ())
    c.pyapi.decref(rtl__xjuj)
    return gdxk__ltiki


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        if lhs == string_array_type and rhs == string_array_type:

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                kxo__dfo = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(kxo__dfo)
                for i in numba.parfors.parfor.internal_prange(kxo__dfo):
                    if bodo.libs.array_kernels.isna(lhs, i
                        ) or bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_both
        if lhs == string_array_type and types.unliteral(rhs) == string_type:

            def impl_left(lhs, rhs):
                numba.parfors.parfor.init_prange()
                kxo__dfo = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(kxo__dfo)
                for i in numba.parfors.parfor.internal_prange(kxo__dfo):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs)
                    out_arr[i] = val
                return out_arr
            return impl_left
        if types.unliteral(lhs) == string_type and rhs == string_array_type:

            def impl_right(lhs, rhs):
                numba.parfors.parfor.init_prange()
                kxo__dfo = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(kxo__dfo)
                for i in numba.parfors.parfor.internal_prange(kxo__dfo):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs, rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_right
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_string_array_binary_op


def overload_add_operator_string_array(lhs, rhs):
    pwfjs__drug = lhs == string_array_type or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    liinx__czcg = rhs == string_array_type or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if (lhs == string_array_type and liinx__czcg or pwfjs__drug and rhs ==
        string_array_type):

        def impl_both(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for qgha__cor in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, qgha__cor
                    ) or bodo.libs.array_kernels.isna(rhs, qgha__cor):
                    out_arr[qgha__cor] = ''
                    bodo.libs.array_kernels.setna(out_arr, qgha__cor)
                else:
                    out_arr[qgha__cor] = lhs[qgha__cor] + rhs[qgha__cor]
            return out_arr
        return impl_both
    if lhs == string_array_type and types.unliteral(rhs) == string_type:

        def impl_left(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for qgha__cor in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, qgha__cor):
                    out_arr[qgha__cor] = ''
                    bodo.libs.array_kernels.setna(out_arr, qgha__cor)
                else:
                    out_arr[qgha__cor] = lhs[qgha__cor] + rhs
            return out_arr
        return impl_left
    if types.unliteral(lhs) == string_type and rhs == string_array_type:

        def impl_right(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(rhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for qgha__cor in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(rhs, qgha__cor):
                    out_arr[qgha__cor] = ''
                    bodo.libs.array_kernels.setna(out_arr, qgha__cor)
                else:
                    out_arr[qgha__cor] = lhs + rhs[qgha__cor]
            return out_arr
        return impl_right


def overload_mul_operator_str_arr(lhs, rhs):
    if lhs == string_array_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for qgha__cor in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, qgha__cor):
                    out_arr[qgha__cor] = ''
                    bodo.libs.array_kernels.setna(out_arr, qgha__cor)
                else:
                    out_arr[qgha__cor] = lhs[qgha__cor] * rhs
            return out_arr
        return impl
    if isinstance(lhs, types.Integer) and rhs == string_array_type:

        def impl(lhs, rhs):
            return rhs * lhs
        return impl


class StringArrayIterator(types.SimpleIteratorType):

    def __init__(self):
        tbgn__nclf = 'iter(String)'
        knby__zlx = string_type
        super(StringArrayIterator, self).__init__(tbgn__nclf, knby__zlx)


@register_model(StringArrayIterator)
class StrArrayIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        emvh__hczfd = [('index', types.EphemeralPointer(types.uintp)), (
            'array', string_array_type)]
        super(StrArrayIteratorModel, self).__init__(dmm, fe_type, emvh__hczfd)


lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@lower_builtin('iternext', StringArrayIterator)
@iternext_impl(RefType.NEW)
def iternext_str_array(context, builder, sig, args, result):
    [axx__zfqsa] = sig.args
    [asw__brg] = args
    dhpw__oppv = context.make_helper(builder, axx__zfqsa, value=asw__brg)
    uga__ukoa = signature(types.intp, string_array_type)
    ttfvi__zrdv = context.compile_internal(builder, lambda a: len(a),
        uga__ukoa, [dhpw__oppv.array])
    mdxl__alnva = builder.load(dhpw__oppv.index)
    fwq__vvxzd = builder.icmp(lc.ICMP_SLT, mdxl__alnva, ttfvi__zrdv)
    result.set_valid(fwq__vvxzd)
    with builder.if_then(fwq__vvxzd):
        bpvjr__cnp = signature(string_type, string_array_type, types.intp)
        value = context.compile_internal(builder, lambda a, i: a[i],
            bpvjr__cnp, [dhpw__oppv.array, mdxl__alnva])
        result.yield_(value)
        wibi__ttwmn = cgutils.increment_index(builder, mdxl__alnva)
        builder.store(wibi__ttwmn, dhpw__oppv.index)


def _get_str_binary_arr_payload(context, builder, arr_value, arr_typ):
    assert arr_typ == string_array_type or arr_typ == binary_array_type
    ydgs__sfz = context.make_helper(builder, arr_typ, arr_value)
    tdfj__rlwn = ArrayItemArrayType(char_arr_type)
    ybd__dnyr = _get_array_item_arr_payload(context, builder, tdfj__rlwn,
        ydgs__sfz.data)
    return ybd__dnyr


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return ybd__dnyr.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        asuka__lpxhu = context.make_helper(builder, offset_arr_type,
            ybd__dnyr.offsets).data
        return _get_num_total_chars(builder, asuka__lpxhu, ybd__dnyr.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        sbj__epxpc = context.make_helper(builder, offset_arr_type,
            ybd__dnyr.offsets)
        mwtru__omewg = context.make_helper(builder, offset_ctypes_type)
        mwtru__omewg.data = builder.bitcast(sbj__epxpc.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        mwtru__omewg.meminfo = sbj__epxpc.meminfo
        gdxk__ltiki = mwtru__omewg._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            gdxk__ltiki)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        kyka__jxsld = context.make_helper(builder, char_arr_type, ybd__dnyr
            .data)
        mwtru__omewg = context.make_helper(builder, data_ctypes_type)
        mwtru__omewg.data = kyka__jxsld.data
        mwtru__omewg.meminfo = kyka__jxsld.meminfo
        gdxk__ltiki = mwtru__omewg._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            gdxk__ltiki)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        hpzb__hmkp, ind = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            hpzb__hmkp, sig.args[0])
        kyka__jxsld = context.make_helper(builder, char_arr_type, ybd__dnyr
            .data)
        mwtru__omewg = context.make_helper(builder, data_ctypes_type)
        mwtru__omewg.data = builder.gep(kyka__jxsld.data, [ind])
        mwtru__omewg.meminfo = kyka__jxsld.meminfo
        gdxk__ltiki = mwtru__omewg._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            gdxk__ltiki)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        bua__onnok, mouti__hioav, kxu__clumk, dykl__khi = args
        mmbzs__faowm = builder.bitcast(builder.gep(bua__onnok, [
            mouti__hioav]), lir.IntType(8).as_pointer())
        ruw__qzc = builder.bitcast(builder.gep(kxu__clumk, [dykl__khi]),
            lir.IntType(8).as_pointer())
        eby__ntty = builder.load(ruw__qzc)
        builder.store(eby__ntty, mmbzs__faowm)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        wgbjw__qkd = context.make_helper(builder, null_bitmap_arr_type,
            ybd__dnyr.null_bitmap)
        mwtru__omewg = context.make_helper(builder, data_ctypes_type)
        mwtru__omewg.data = wgbjw__qkd.data
        mwtru__omewg.meminfo = wgbjw__qkd.meminfo
        gdxk__ltiki = mwtru__omewg._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            gdxk__ltiki)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        asuka__lpxhu = context.make_helper(builder, offset_arr_type,
            ybd__dnyr.offsets).data
        return builder.load(builder.gep(asuka__lpxhu, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, ybd__dnyr.
            offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        nsye__bszni, ind = args
        if in_bitmap_typ == data_ctypes_type:
            mwtru__omewg = context.make_helper(builder, data_ctypes_type,
                nsye__bszni)
            nsye__bszni = mwtru__omewg.data
        return builder.load(builder.gep(nsye__bszni, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        nsye__bszni, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            mwtru__omewg = context.make_helper(builder, data_ctypes_type,
                nsye__bszni)
            nsye__bszni = mwtru__omewg.data
        builder.store(val, builder.gep(nsye__bszni, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        asxtt__xie = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ptfnh__jfxih = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        jsrsr__wsaom = context.make_helper(builder, offset_arr_type,
            asxtt__xie.offsets).data
        ucj__gciwj = context.make_helper(builder, offset_arr_type,
            ptfnh__jfxih.offsets).data
        rghc__swd = context.make_helper(builder, char_arr_type, asxtt__xie.data
            ).data
        eoq__ghkw = context.make_helper(builder, char_arr_type,
            ptfnh__jfxih.data).data
        okqsd__wdh = context.make_helper(builder, null_bitmap_arr_type,
            asxtt__xie.null_bitmap).data
        aisms__sodjf = context.make_helper(builder, null_bitmap_arr_type,
            ptfnh__jfxih.null_bitmap).data
        sihu__rhxjk = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, ucj__gciwj, jsrsr__wsaom, sihu__rhxjk)
        cgutils.memcpy(builder, eoq__ghkw, rghc__swd, builder.load(builder.
            gep(jsrsr__wsaom, [ind])))
        ffxhc__prrv = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        yhtss__tgod = builder.lshr(ffxhc__prrv, lir.Constant(lir.IntType(64
            ), 3))
        cgutils.memcpy(builder, aisms__sodjf, okqsd__wdh, yhtss__tgod)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        asxtt__xie = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ptfnh__jfxih = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        jsrsr__wsaom = context.make_helper(builder, offset_arr_type,
            asxtt__xie.offsets).data
        rghc__swd = context.make_helper(builder, char_arr_type, asxtt__xie.data
            ).data
        eoq__ghkw = context.make_helper(builder, char_arr_type,
            ptfnh__jfxih.data).data
        num_total_chars = _get_num_total_chars(builder, jsrsr__wsaom,
            asxtt__xie.n_arrays)
        cgutils.memcpy(builder, eoq__ghkw, rghc__swd, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        asxtt__xie = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ptfnh__jfxih = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        jsrsr__wsaom = context.make_helper(builder, offset_arr_type,
            asxtt__xie.offsets).data
        ucj__gciwj = context.make_helper(builder, offset_arr_type,
            ptfnh__jfxih.offsets).data
        okqsd__wdh = context.make_helper(builder, null_bitmap_arr_type,
            asxtt__xie.null_bitmap).data
        kxo__dfo = asxtt__xie.n_arrays
        sns__xils = context.get_constant(offset_type, 0)
        twqq__bxpb = cgutils.alloca_once_value(builder, sns__xils)
        with cgutils.for_range(builder, kxo__dfo) as loop:
            mvyv__kydtj = lower_is_na(context, builder, okqsd__wdh, loop.index)
            with cgutils.if_likely(builder, builder.not_(mvyv__kydtj)):
                iqex__eogwp = builder.load(builder.gep(jsrsr__wsaom, [loop.
                    index]))
                qjw__ose = builder.load(twqq__bxpb)
                builder.store(iqex__eogwp, builder.gep(ucj__gciwj, [qjw__ose]))
                builder.store(builder.add(qjw__ose, lir.Constant(context.
                    get_value_type(offset_type), 1)), twqq__bxpb)
        qjw__ose = builder.load(twqq__bxpb)
        iqex__eogwp = builder.load(builder.gep(jsrsr__wsaom, [kxo__dfo]))
        builder.store(iqex__eogwp, builder.gep(ucj__gciwj, [qjw__ose]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        tderx__odbkj, ind, str, yhj__ztrbx = args
        tderx__odbkj = context.make_array(sig.args[0])(context, builder,
            tderx__odbkj)
        ehvlp__cdl = builder.gep(tderx__odbkj.data, [ind])
        cgutils.raw_memcpy(builder, ehvlp__cdl, str, yhj__ztrbx, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        ehvlp__cdl, ind, pyc__pktza, yhj__ztrbx = args
        ehvlp__cdl = builder.gep(ehvlp__cdl, [ind])
        cgutils.raw_memcpy(builder, ehvlp__cdl, pyc__pktza, yhj__ztrbx, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_length(A, i):
    return np.int64(getitem_str_offset(A, i + 1) - getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    kxo__dfo = len(str_arr)
    brv__nptj = np.empty(kxo__dfo, np.bool_)
    for i in range(kxo__dfo):
        brv__nptj[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return brv__nptj


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if data in [string_array_type, binary_array_type]:

        def to_list_impl(data, str_null_bools=None):
            kxo__dfo = len(data)
            l = []
            for i in range(kxo__dfo):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        mskwl__htvlj = data.count
        cgh__mnw = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(mskwl__htvlj)]
        if is_overload_true(str_null_bools):
            cgh__mnw += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(mskwl__htvlj) if data.types[i] in [string_array_type,
                binary_array_type]]
        pwwlw__kaplk = 'def f(data, str_null_bools=None):\n'
        pwwlw__kaplk += '  return ({}{})\n'.format(', '.join(cgh__mnw), ',' if
            mskwl__htvlj == 1 else '')
        dmpk__dbf = {}
        exec(pwwlw__kaplk, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, dmpk__dbf)
        ttt__glo = dmpk__dbf['f']
        return ttt__glo
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                kxo__dfo = len(list_data)
                for i in range(kxo__dfo):
                    pyc__pktza = list_data[i]
                    str_arr[i] = pyc__pktza
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                kxo__dfo = len(list_data)
                for i in range(kxo__dfo):
                    pyc__pktza = list_data[i]
                    str_arr[i] = pyc__pktza
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        mskwl__htvlj = str_arr.count
        yau__ugjw = 0
        pwwlw__kaplk = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(mskwl__htvlj):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                pwwlw__kaplk += (
                    """  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])
"""
                    .format(i, i, mskwl__htvlj + yau__ugjw))
                yau__ugjw += 1
            else:
                pwwlw__kaplk += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        pwwlw__kaplk += '  return\n'
        dmpk__dbf = {}
        exec(pwwlw__kaplk, {'cp_str_list_to_array': cp_str_list_to_array},
            dmpk__dbf)
        xnatg__bxm = dmpk__dbf['f']
        return xnatg__bxm
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            kxo__dfo = len(str_list)
            str_arr = pre_alloc_string_array(kxo__dfo, -1)
            for i in range(kxo__dfo):
                pyc__pktza = str_list[i]
                str_arr[i] = pyc__pktza
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            kxo__dfo = len(A)
            onex__nszor = 0
            for i in range(kxo__dfo):
                pyc__pktza = A[i]
                onex__nszor += get_utf8_size(pyc__pktza)
            return onex__nszor
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        kxo__dfo = len(arr)
        n_chars = num_total_chars(arr)
        hfab__keibd = pre_alloc_string_array(kxo__dfo, np.int64(n_chars))
        copy_str_arr_slice(hfab__keibd, arr, kxo__dfo)
        return hfab__keibd
    return copy_impl


@overload(len, no_unliteral=True)
def str_arr_len_overload(str_arr):
    if str_arr == string_array_type:

        def str_arr_len(str_arr):
            return str_arr.size
        return str_arr_len


@overload_attribute(StringArrayType, 'size')
def str_arr_size_overload(str_arr):
    return lambda str_arr: len(str_arr._data)


@overload_attribute(StringArrayType, 'shape')
def str_arr_shape_overload(str_arr):
    return lambda str_arr: (str_arr.size,)


@overload_attribute(StringArrayType, 'nbytes')
def str_arr_nbytes_overload(str_arr):
    return lambda str_arr: str_arr._data.nbytes


@overload_method(types.Array, 'tolist', no_unliteral=True)
@overload_method(StringArrayType, 'tolist', no_unliteral=True)
def overload_to_list(arr):
    return lambda arr: list(arr)


import llvmlite.binding as ll
from llvmlite import ir as lir
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('setitem_string_array', hstr_ext.setitem_string_array)
ll.add_symbol('is_na', hstr_ext.is_na)
ll.add_symbol('string_array_from_sequence', array_ext.
    string_array_from_sequence)
ll.add_symbol('pd_array_from_string_array', hstr_ext.pd_array_from_string_array
    )
ll.add_symbol('np_array_from_string_array', hstr_ext.np_array_from_string_array
    )
ll.add_symbol('convert_len_arr_to_offset32', hstr_ext.
    convert_len_arr_to_offset32)
ll.add_symbol('convert_len_arr_to_offset', hstr_ext.convert_len_arr_to_offset)
ll.add_symbol('set_string_array_range', hstr_ext.set_string_array_range)
ll.add_symbol('str_arr_to_int64', hstr_ext.str_arr_to_int64)
ll.add_symbol('str_arr_to_float64', hstr_ext.str_arr_to_float64)
ll.add_symbol('get_utf8_size', hstr_ext.get_utf8_size)
ll.add_symbol('print_str_arr', hstr_ext.print_str_arr)
ll.add_symbol('inplace_int64_to_str', hstr_ext.inplace_int64_to_str)
inplace_int64_to_str = types.ExternalFunction('inplace_int64_to_str', types
    .void(types.voidptr, types.int64, types.int64))
convert_len_arr_to_offset32 = types.ExternalFunction(
    'convert_len_arr_to_offset32', types.void(types.voidptr, types.intp))
convert_len_arr_to_offset = types.ExternalFunction('convert_len_arr_to_offset',
    types.void(types.voidptr, types.voidptr, types.intp))
setitem_string_array = types.ExternalFunction('setitem_string_array', types
    .void(types.CPointer(offset_type), types.CPointer(char_type), types.
    uint64, types.voidptr, types.intp, offset_type, offset_type, types.intp))
_get_utf8_size = types.ExternalFunction('get_utf8_size', types.intp(types.
    voidptr, types.intp, offset_type))
_print_str_arr = types.ExternalFunction('print_str_arr', types.void(types.
    uint64, types.uint64, types.CPointer(offset_type), types.CPointer(
    char_type)))


@numba.generated_jit(nopython=True)
def empty_str_arr(in_seq):
    pwwlw__kaplk = 'def f(in_seq):\n'
    pwwlw__kaplk += '    n_strs = len(in_seq)\n'
    pwwlw__kaplk += '    A = pre_alloc_string_array(n_strs, -1)\n'
    pwwlw__kaplk += '    return A\n'
    dmpk__dbf = {}
    exec(pwwlw__kaplk, {'pre_alloc_string_array': pre_alloc_string_array},
        dmpk__dbf)
    nlki__bwssx = dmpk__dbf['f']
    return nlki__bwssx


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    if in_seq.dtype == bodo.bytes_type:
        yewgi__rewx = 'pre_alloc_binary_array'
    else:
        yewgi__rewx = 'pre_alloc_string_array'
    pwwlw__kaplk = 'def f(in_seq):\n'
    pwwlw__kaplk += '    n_strs = len(in_seq)\n'
    pwwlw__kaplk += f'    A = {yewgi__rewx}(n_strs, -1)\n'
    pwwlw__kaplk += '    for i in range(n_strs):\n'
    pwwlw__kaplk += '        A[i] = in_seq[i]\n'
    pwwlw__kaplk += '    return A\n'
    dmpk__dbf = {}
    exec(pwwlw__kaplk, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, dmpk__dbf)
    nlki__bwssx = dmpk__dbf['f']
    return nlki__bwssx


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        dtrhy__bhuqu = builder.add(ybd__dnyr.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        yii__yvsjr = builder.lshr(lir.Constant(lir.IntType(64), offset_type
            .bitwidth), lir.Constant(lir.IntType(64), 3))
        yhtss__tgod = builder.mul(dtrhy__bhuqu, yii__yvsjr)
        slj__kjc = context.make_array(offset_arr_type)(context, builder,
            ybd__dnyr.offsets).data
        cgutils.memset(builder, slj__kjc, yhtss__tgod, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        npcz__fxnn = ybd__dnyr.n_arrays
        yhtss__tgod = builder.lshr(builder.add(npcz__fxnn, lir.Constant(lir
            .IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        pvwm__zrsxg = context.make_array(null_bitmap_arr_type)(context,
            builder, ybd__dnyr.null_bitmap).data
        cgutils.memset(builder, pvwm__zrsxg, yhtss__tgod, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@numba.njit
def pre_alloc_string_array(n_strs, n_chars):
    if n_chars is None:
        n_chars = -1
    str_arr = init_str_arr(bodo.libs.array_item_arr_ext.
        pre_alloc_array_item_array(np.int64(n_strs), (np.int64(n_chars),),
        char_arr_type))
    if n_chars == 0:
        set_all_offsets_to_0(str_arr)
    return str_arr


@register_jitable
def gen_na_str_array_lens(n_strs, total_len, len_arr):
    str_arr = pre_alloc_string_array(n_strs, total_len)
    set_bitmap_all_NA(str_arr)
    offsets = bodo.libs.array_item_arr_ext.get_offsets(str_arr._data)
    rig__nyth = 0
    kaacw__qcof = len(len_arr)
    for i in range(kaacw__qcof):
        offsets[i] = rig__nyth
        rig__nyth += len_arr[i]
    offsets[kaacw__qcof] = rig__nyth
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    hgz__cfq = i // 8
    pwo__mgm = getitem_str_bitmap(bits, hgz__cfq)
    pwo__mgm ^= np.uint8(-np.uint8(bit_is_set) ^ pwo__mgm) & kBitmask[i % 8]
    setitem_str_bitmap(bits, hgz__cfq, pwo__mgm)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    mhgo__cnjc = get_null_bitmap_ptr(out_str_arr)
    cpmr__aib = get_null_bitmap_ptr(in_str_arr)
    for qgha__cor in range(len(in_str_arr)):
        hgf__itdfi = get_bit_bitmap(cpmr__aib, qgha__cor)
        set_bit_to(mhgo__cnjc, out_start + qgha__cor, hgf__itdfi)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type
    assert curr_str_typ == types.intp and curr_chars_typ == types.intp

    def codegen(context, builder, sig, args):
        out_arr, hpzb__hmkp, sbm__yzrx, nckr__uxfki = args
        asxtt__xie = _get_str_binary_arr_payload(context, builder,
            hpzb__hmkp, string_array_type)
        ptfnh__jfxih = _get_str_binary_arr_payload(context, builder,
            out_arr, string_array_type)
        jsrsr__wsaom = context.make_helper(builder, offset_arr_type,
            asxtt__xie.offsets).data
        ucj__gciwj = context.make_helper(builder, offset_arr_type,
            ptfnh__jfxih.offsets).data
        rghc__swd = context.make_helper(builder, char_arr_type, asxtt__xie.data
            ).data
        eoq__ghkw = context.make_helper(builder, char_arr_type,
            ptfnh__jfxih.data).data
        num_total_chars = _get_num_total_chars(builder, jsrsr__wsaom,
            asxtt__xie.n_arrays)
        uha__gqj = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        xgdr__fqrnv = cgutils.get_or_insert_function(builder.module,
            uha__gqj, name='set_string_array_range')
        builder.call(xgdr__fqrnv, [ucj__gciwj, eoq__ghkw, jsrsr__wsaom,
            rghc__swd, sbm__yzrx, nckr__uxfki, asxtt__xie.n_arrays,
            num_total_chars])
        pcj__xthbo = context.typing_context.resolve_value_type(copy_nulls_range
            )
        wlhda__ymy = pcj__xthbo.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        nwigh__sezf = context.get_function(pcj__xthbo, wlhda__ymy)
        nwigh__sezf(builder, (out_arr, hpzb__hmkp, sbm__yzrx))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    lkr__deinf = c.context.make_helper(c.builder, typ, val)
    tdfj__rlwn = ArrayItemArrayType(char_arr_type)
    ybd__dnyr = _get_array_item_arr_payload(c.context, c.builder,
        tdfj__rlwn, lkr__deinf.data)
    xnzp__lmui = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    jimq__rbpl = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        jimq__rbpl = 'pd_array_from_string_array'
    uha__gqj = lir.FunctionType(c.context.get_argument_type(types.pyobject),
        [lir.IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
        lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
        IntType(32)])
    igq__evfj = cgutils.get_or_insert_function(c.builder.module, uha__gqj,
        name=jimq__rbpl)
    asuka__lpxhu = c.context.make_array(offset_arr_type)(c.context, c.
        builder, ybd__dnyr.offsets).data
    kwir__wmq = c.context.make_array(char_arr_type)(c.context, c.builder,
        ybd__dnyr.data).data
    pvwm__zrsxg = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, ybd__dnyr.null_bitmap).data
    arr = c.builder.call(igq__evfj, [ybd__dnyr.n_arrays, asuka__lpxhu,
        kwir__wmq, pvwm__zrsxg, xnzp__lmui])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pvwm__zrsxg = context.make_array(null_bitmap_arr_type)(context,
            builder, ybd__dnyr.null_bitmap).data
        tqas__col = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        ybqtj__kan = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        pwo__mgm = builder.load(builder.gep(pvwm__zrsxg, [tqas__col],
            inbounds=True))
        ecu__ajzx = lir.ArrayType(lir.IntType(8), 8)
        qid__dkjm = cgutils.alloca_once_value(builder, lir.Constant(
            ecu__ajzx, (1, 2, 4, 8, 16, 32, 64, 128)))
        bdbco__wtold = builder.load(builder.gep(qid__dkjm, [lir.Constant(
            lir.IntType(64), 0), ybqtj__kan], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(pwo__mgm,
            bdbco__wtold), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        tqas__col = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        ybqtj__kan = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        pvwm__zrsxg = context.make_array(null_bitmap_arr_type)(context,
            builder, ybd__dnyr.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, ybd__dnyr.
            offsets).data
        ampz__sare = builder.gep(pvwm__zrsxg, [tqas__col], inbounds=True)
        pwo__mgm = builder.load(ampz__sare)
        ecu__ajzx = lir.ArrayType(lir.IntType(8), 8)
        qid__dkjm = cgutils.alloca_once_value(builder, lir.Constant(
            ecu__ajzx, (1, 2, 4, 8, 16, 32, 64, 128)))
        bdbco__wtold = builder.load(builder.gep(qid__dkjm, [lir.Constant(
            lir.IntType(64), 0), ybqtj__kan], inbounds=True))
        bdbco__wtold = builder.xor(bdbco__wtold, lir.Constant(lir.IntType(8
            ), -1))
        builder.store(builder.and_(pwo__mgm, bdbco__wtold), ampz__sare)
        if str_arr_typ == string_array_type:
            ocdvu__rehuq = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            upow__yxs = builder.icmp_unsigned('!=', ocdvu__rehuq, ybd__dnyr
                .n_arrays)
            with builder.if_then(upow__yxs):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [ocdvu__rehuq]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        tqas__col = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        ybqtj__kan = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        pvwm__zrsxg = context.make_array(null_bitmap_arr_type)(context,
            builder, ybd__dnyr.null_bitmap).data
        ampz__sare = builder.gep(pvwm__zrsxg, [tqas__col], inbounds=True)
        pwo__mgm = builder.load(ampz__sare)
        ecu__ajzx = lir.ArrayType(lir.IntType(8), 8)
        qid__dkjm = cgutils.alloca_once_value(builder, lir.Constant(
            ecu__ajzx, (1, 2, 4, 8, 16, 32, 64, 128)))
        bdbco__wtold = builder.load(builder.gep(qid__dkjm, [lir.Constant(
            lir.IntType(64), 0), ybqtj__kan], inbounds=True))
        builder.store(builder.or_(pwo__mgm, bdbco__wtold), ampz__sare)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        yhtss__tgod = builder.udiv(builder.add(ybd__dnyr.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        pvwm__zrsxg = context.make_array(null_bitmap_arr_type)(context,
            builder, ybd__dnyr.null_bitmap).data
        cgutils.memset(builder, pvwm__zrsxg, yhtss__tgod, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    hctuo__jdoy = context.make_helper(builder, string_array_type, str_arr)
    tdfj__rlwn = ArrayItemArrayType(char_arr_type)
    pvm__hrp = context.make_helper(builder, tdfj__rlwn, hctuo__jdoy.data)
    ewnqp__uipm = ArrayItemArrayPayloadType(tdfj__rlwn)
    xtp__rzoaq = context.nrt.meminfo_data(builder, pvm__hrp.meminfo)
    jqzo__hbdm = builder.bitcast(xtp__rzoaq, context.get_value_type(
        ewnqp__uipm).as_pointer())
    return jqzo__hbdm


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        fzdry__ybmjp, cplgm__racu = args
        bbhyd__lklj = _get_str_binary_arr_data_payload_ptr(context, builder,
            cplgm__racu)
        kuzi__leh = _get_str_binary_arr_data_payload_ptr(context, builder,
            fzdry__ybmjp)
        obao__udgsx = _get_str_binary_arr_payload(context, builder,
            cplgm__racu, sig.args[1])
        ihni__xyuhe = _get_str_binary_arr_payload(context, builder,
            fzdry__ybmjp, sig.args[0])
        context.nrt.incref(builder, char_arr_type, obao__udgsx.data)
        context.nrt.incref(builder, offset_arr_type, obao__udgsx.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, obao__udgsx.
            null_bitmap)
        context.nrt.decref(builder, char_arr_type, ihni__xyuhe.data)
        context.nrt.decref(builder, offset_arr_type, ihni__xyuhe.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, ihni__xyuhe.
            null_bitmap)
        builder.store(builder.load(bbhyd__lklj), kuzi__leh)
        return context.get_dummy_value()
    return types.none(to_arr_typ, from_arr_typ), codegen


dummy_use = numba.njit(lambda a: None)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_utf8_size(s):
    if isinstance(s, types.StringLiteral):
        l = len(s.literal_value.encode())
        return lambda s: l

    def impl(s):
        if s is None:
            return 0
        s = bodo.utils.indexing.unoptional(s)
        if s._is_ascii == 1:
            return len(s)
        kxo__dfo = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return kxo__dfo
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, ehvlp__cdl, flwi__qjv = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder, arr, sig.
            args[0])
        offsets = context.make_helper(builder, offset_arr_type, ybd__dnyr.
            offsets).data
        data = context.make_helper(builder, char_arr_type, ybd__dnyr.data).data
        uha__gqj = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        qrs__fvq = cgutils.get_or_insert_function(builder.module, uha__gqj,
            name='setitem_string_array')
        zgt__speo = context.get_constant(types.int32, -1)
        tsrwd__oqkjd = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets, ybd__dnyr.
            n_arrays)
        builder.call(qrs__fvq, [offsets, data, num_total_chars, builder.
            extract_value(ehvlp__cdl, 0), flwi__qjv, zgt__speo,
            tsrwd__oqkjd, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    uha__gqj = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer(
        ), lir.IntType(64)])
    dazcs__rdsf = cgutils.get_or_insert_function(builder.module, uha__gqj,
        name='is_na')
    return builder.call(dazcs__rdsf, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        mmbzs__faowm, ruw__qzc, mskwl__htvlj, qsc__zxmxq = args
        cgutils.raw_memcpy(builder, mmbzs__faowm, ruw__qzc, mskwl__htvlj,
            qsc__zxmxq)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.voidptr, types.intp, types.intp
        ), codegen


@numba.njit
def print_str_arr(arr):
    _print_str_arr(num_strings(arr), num_total_chars(arr), get_offset_ptr(
        arr), get_data_ptr(arr))


def inplace_eq(A, i, val):
    return A[i] == val


@overload(inplace_eq)
def inplace_eq_overload(A, ind, val):

    def impl(A, ind, val):
        fad__wii, fbos__otd = unicode_to_utf8_and_len(val)
        yvio__ezlr = getitem_str_offset(A, ind)
        eow__mgoei = getitem_str_offset(A, ind + 1)
        bkuq__ycai = eow__mgoei - yvio__ezlr
        if bkuq__ycai != fbos__otd:
            return False
        ehvlp__cdl = get_data_ptr_ind(A, yvio__ezlr)
        return memcmp(ehvlp__cdl, fad__wii, fbos__otd) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        yvio__ezlr = getitem_str_offset(A, ind)
        bkuq__ycai = bodo.libs.str_ext.int_to_str_len(val)
        jtwso__vkf = yvio__ezlr + bkuq__ycai
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            yvio__ezlr, jtwso__vkf)
        ehvlp__cdl = get_data_ptr_ind(A, yvio__ezlr)
        inplace_int64_to_str(ehvlp__cdl, bkuq__ycai, val)
        setitem_str_offset(A, ind + 1, yvio__ezlr + bkuq__ycai)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        ehvlp__cdl, = args
        xht__hvr = context.insert_const_string(builder.module, '<NA>')
        whs__wygvw = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, ehvlp__cdl, xht__hvr, whs__wygvw, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    amym__poibc = len('<NA>')

    def impl(A, ind):
        yvio__ezlr = getitem_str_offset(A, ind)
        jtwso__vkf = yvio__ezlr + amym__poibc
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            yvio__ezlr, jtwso__vkf)
        ehvlp__cdl = get_data_ptr_ind(A, yvio__ezlr)
        inplace_set_NA_str(ehvlp__cdl)
        setitem_str_offset(A, ind + 1, yvio__ezlr + amym__poibc)
        str_arr_set_not_na(A, ind)
    return impl


@overload(operator.getitem, no_unliteral=True)
def str_arr_getitem_int(A, ind):
    if A != string_array_type:
        return
    if isinstance(ind, types.Integer):

        def str_arr_getitem_impl(A, ind):
            if ind < 0:
                ind += A.size
            yvio__ezlr = getitem_str_offset(A, ind)
            eow__mgoei = getitem_str_offset(A, ind + 1)
            flwi__qjv = eow__mgoei - yvio__ezlr
            ehvlp__cdl = get_data_ptr_ind(A, yvio__ezlr)
            wkwqv__syy = decode_utf8(ehvlp__cdl, flwi__qjv)
            return wkwqv__syy
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            kxo__dfo = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(kxo__dfo):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            rfc__vytb = get_data_ptr(out_arr).data
            utyyj__wbx = get_data_ptr(A).data
            yau__ugjw = 0
            qjw__ose = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(kxo__dfo):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    zrwen__nbw = get_str_arr_item_length(A, i)
                    if zrwen__nbw == 1:
                        copy_single_char(rfc__vytb, qjw__ose, utyyj__wbx,
                            getitem_str_offset(A, i))
                    else:
                        memcpy_region(rfc__vytb, qjw__ose, utyyj__wbx,
                            getitem_str_offset(A, i), zrwen__nbw, 1)
                    qjw__ose += zrwen__nbw
                    setitem_str_offset(out_arr, yau__ugjw + 1, qjw__ose)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, yau__ugjw)
                    else:
                        str_arr_set_not_na(out_arr, yau__ugjw)
                    yau__ugjw += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            kxo__dfo = len(ind)
            out_arr = pre_alloc_string_array(kxo__dfo, -1)
            yau__ugjw = 0
            for i in range(kxo__dfo):
                pyc__pktza = A[ind[i]]
                out_arr[yau__ugjw] = pyc__pktza
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, yau__ugjw)
                yau__ugjw += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            kxo__dfo = len(A)
            vpy__pgbd = numba.cpython.unicode._normalize_slice(ind, kxo__dfo)
            iidew__poi = numba.cpython.unicode._slice_span(vpy__pgbd)
            if vpy__pgbd.step == 1:
                yvio__ezlr = getitem_str_offset(A, vpy__pgbd.start)
                eow__mgoei = getitem_str_offset(A, vpy__pgbd.stop)
                n_chars = eow__mgoei - yvio__ezlr
                hfab__keibd = pre_alloc_string_array(iidew__poi, np.int64(
                    n_chars))
                for i in range(iidew__poi):
                    hfab__keibd[i] = A[vpy__pgbd.start + i]
                    if str_arr_is_na(A, vpy__pgbd.start + i):
                        str_arr_set_na(hfab__keibd, i)
                return hfab__keibd
            else:
                hfab__keibd = pre_alloc_string_array(iidew__poi, -1)
                for i in range(iidew__poi):
                    hfab__keibd[i] = A[vpy__pgbd.start + i * vpy__pgbd.step]
                    if str_arr_is_na(A, vpy__pgbd.start + i * vpy__pgbd.step):
                        str_arr_set_na(hfab__keibd, i)
                return hfab__keibd
        return str_arr_slice_impl
    raise BodoError(
        f'getitem for StringArray with indexing type {ind} not supported.')


dummy_use = numba.njit(lambda a: None)


@overload(operator.setitem)
def str_arr_setitem(A, idx, val):
    if A != string_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    otsg__qrp = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(otsg__qrp)
        thcuv__dprj = 4

        def impl_scalar(A, idx, val):
            pwhp__ejzay = (val._length if val._is_ascii else thcuv__dprj *
                val._length)
            kyka__jxsld = A._data
            yvio__ezlr = np.int64(getitem_str_offset(A, idx))
            jtwso__vkf = yvio__ezlr + pwhp__ejzay
            bodo.libs.array_item_arr_ext.ensure_data_capacity(kyka__jxsld,
                yvio__ezlr, jtwso__vkf)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                jtwso__vkf, val._data, val._length, val._kind, val.
                _is_ascii, idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                vpy__pgbd = numba.cpython.unicode._normalize_slice(idx, len(A))
                hjhu__axoji = vpy__pgbd.start
                kyka__jxsld = A._data
                yvio__ezlr = np.int64(getitem_str_offset(A, hjhu__axoji))
                jtwso__vkf = yvio__ezlr + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(kyka__jxsld,
                    yvio__ezlr, jtwso__vkf)
                set_string_array_range(A, val, hjhu__axoji, yvio__ezlr)
                lmkjo__lihjm = 0
                for i in range(vpy__pgbd.start, vpy__pgbd.stop, vpy__pgbd.step
                    ):
                    if str_arr_is_na(val, lmkjo__lihjm):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    lmkjo__lihjm += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                dzso__pjgl = str_list_to_array(val)
                A[idx] = dzso__pjgl
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                vpy__pgbd = numba.cpython.unicode._normalize_slice(idx, len(A))
                for i in range(vpy__pgbd.start, vpy__pgbd.stop, vpy__pgbd.step
                    ):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(otsg__qrp)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                kxo__dfo = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(kxo__dfo, -1)
                for i in numba.parfors.parfor.internal_prange(kxo__dfo):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        out_arr[i] = val
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        out_arr[i] = A[i]
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_scalar
        elif val == string_array_type or isinstance(val, types.Array
            ) and isinstance(val.dtype, types.UnicodeCharSeq):

            def impl_bool_arr(A, idx, val):
                kxo__dfo = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(kxo__dfo, -1)
                vap__clfft = 0
                for i in numba.parfors.parfor.internal_prange(kxo__dfo):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, vap__clfft):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, vap__clfft)
                        else:
                            out_arr[i] = str(val[vap__clfft])
                        vap__clfft += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        out_arr[i] = A[i]
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(otsg__qrp)
    raise BodoError(otsg__qrp)


@overload_attribute(StringArrayType, 'dtype')
def overload_str_arr_dtype(A):
    return lambda A: pd.StringDtype()


@overload_attribute(StringArrayType, 'ndim')
def overload_str_arr_ndim(A):
    return lambda A: 1


@overload_method(StringArrayType, 'astype', no_unliteral=True)
def overload_str_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "StringArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.Function) and dtype.key[0] == str:
        return lambda A, dtype, copy=True: A
    xokm__bakh = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(xokm__bakh, (types.Float, types.Integer)):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(xokm__bakh, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            kxo__dfo = len(A)
            vez__gdaq = np.empty(kxo__dfo, xokm__bakh)
            for i in numba.parfors.parfor.internal_prange(kxo__dfo):
                if bodo.libs.array_kernels.isna(A, i):
                    vez__gdaq[i] = np.nan
                else:
                    vez__gdaq[i] = float(A[i])
            return vez__gdaq
        return impl_float
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            kxo__dfo = len(A)
            vez__gdaq = np.empty(kxo__dfo, xokm__bakh)
            for i in numba.parfors.parfor.internal_prange(kxo__dfo):
                vez__gdaq[i] = int(A[i])
            return vez__gdaq
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        ehvlp__cdl, flwi__qjv = args
        cpbe__frj = context.get_python_api(builder)
        qkck__vuw = cpbe__frj.string_from_string_and_size(ehvlp__cdl, flwi__qjv
            )
        vih__lwbav = cpbe__frj.to_native_value(string_type, qkck__vuw).value
        igi__szgdl = cgutils.create_struct_proxy(string_type)(context,
            builder, vih__lwbav)
        igi__szgdl.hash = igi__szgdl.hash.type(-1)
        cpbe__frj.decref(qkck__vuw)
        return igi__szgdl._getvalue()
    return string_type(types.voidptr, types.intp), codegen


def get_arr_data_ptr(arr, ind):
    return arr


@overload(get_arr_data_ptr, no_unliteral=True)
def overload_get_arr_data_ptr(arr, ind):
    assert isinstance(types.unliteral(ind), types.Integer)
    if isinstance(arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(arr, ind):
            return bodo.hiframes.split_impl.get_c_arr_ptr(arr._data.ctypes, ind
                )
        return impl_int
    assert isinstance(arr, types.Array)

    def impl_np(arr, ind):
        return bodo.hiframes.split_impl.get_c_arr_ptr(arr.ctypes, ind)
    return impl_np


def set_to_numeric_out_na_err(out_arr, out_ind, err_code):
    pass


@overload(set_to_numeric_out_na_err)
def set_to_numeric_out_na_err_overload(out_arr, out_ind, err_code):
    if isinstance(out_arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(out_arr, out_ind, err_code):
            bodo.libs.int_arr_ext.set_bit_to_arr(out_arr._null_bitmap,
                out_ind, 0 if err_code == -1 else 1)
        return impl_int
    assert isinstance(out_arr, types.Array)
    if isinstance(out_arr.dtype, types.Float):

        def impl_np(out_arr, out_ind, err_code):
            if err_code == -1:
                out_arr[out_ind] = np.nan
        return impl_np
    return lambda out_arr, out_ind, err_code: None


@numba.njit(no_cpython_wrapper=True)
def str_arr_item_to_numeric(out_arr, out_ind, str_arr, ind):
    err_code = _str_arr_item_to_numeric(get_arr_data_ptr(out_arr, out_ind),
        str_arr, ind, out_arr.dtype)
    set_to_numeric_out_na_err(out_arr, out_ind, err_code)


@intrinsic
def _str_arr_item_to_numeric(typingctx, out_ptr_t, str_arr_t, ind_t,
    out_dtype_t=None):
    assert str_arr_t == string_array_type
    assert ind_t == types.int64

    def codegen(context, builder, sig, args):
        qcta__upc, arr, ind, ryu__pwlpd = args
        ybd__dnyr = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, ybd__dnyr.
            offsets).data
        data = context.make_helper(builder, char_arr_type, ybd__dnyr.data).data
        uha__gqj = lir.FunctionType(lir.IntType(32), [qcta__upc.type, lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        jroo__vmckp = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            jroo__vmckp = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        xswj__wti = cgutils.get_or_insert_function(builder.module, uha__gqj,
            jroo__vmckp)
        return builder.call(xswj__wti, [qcta__upc, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    xnzp__lmui = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    uha__gqj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(8
        ).as_pointer(), lir.IntType(32)])
    iaceg__oeu = cgutils.get_or_insert_function(c.builder.module, uha__gqj,
        name='string_array_from_sequence')
    piozs__wyu = c.builder.call(iaceg__oeu, [val, xnzp__lmui])
    tdfj__rlwn = ArrayItemArrayType(char_arr_type)
    pvm__hrp = c.context.make_helper(c.builder, tdfj__rlwn)
    pvm__hrp.meminfo = piozs__wyu
    hctuo__jdoy = c.context.make_helper(c.builder, typ)
    kyka__jxsld = pvm__hrp._getvalue()
    hctuo__jdoy.data = kyka__jxsld
    smccp__hutc = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(hctuo__jdoy._getvalue(), is_error=smccp__hutc)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    kxo__dfo = len(pyval)
    qjw__ose = 0
    cuoj__zui = np.empty(kxo__dfo + 1, np_offset_type)
    yzft__lazdi = []
    qzupl__bztyl = np.empty(kxo__dfo + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        cuoj__zui[i] = qjw__ose
        oijpk__bpl = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(qzupl__bztyl, i, int(not
            oijpk__bpl))
        if oijpk__bpl:
            continue
        kdhh__pyorn = list(s.encode()) if isinstance(s, str) else list(s)
        yzft__lazdi.extend(kdhh__pyorn)
        qjw__ose += len(kdhh__pyorn)
    cuoj__zui[kxo__dfo] = qjw__ose
    dwp__vhda = np.array(yzft__lazdi, np.uint8)
    rrond__yfnn = context.get_constant(types.int64, kxo__dfo)
    sag__lhu = context.get_constant_generic(builder, char_arr_type, dwp__vhda)
    btddt__hckg = context.get_constant_generic(builder, offset_arr_type,
        cuoj__zui)
    lgf__nfzf = context.get_constant_generic(builder, null_bitmap_arr_type,
        qzupl__bztyl)
    ybd__dnyr = lir.Constant.literal_struct([rrond__yfnn, sag__lhu,
        btddt__hckg, lgf__nfzf])
    ybd__dnyr = cgutils.global_constant(builder, '.const.payload', ybd__dnyr
        ).bitcast(cgutils.voidptr_t)
    mhrs__hvep = context.get_constant(types.int64, -1)
    dpxbf__npj = context.get_constant_null(types.voidptr)
    zyxlq__coq = lir.Constant.literal_struct([mhrs__hvep, dpxbf__npj,
        dpxbf__npj, ybd__dnyr, mhrs__hvep])
    zyxlq__coq = cgutils.global_constant(builder, '.const.meminfo', zyxlq__coq
        ).bitcast(cgutils.voidptr_t)
    kyka__jxsld = lir.Constant.literal_struct([zyxlq__coq])
    hctuo__jdoy = lir.Constant.literal_struct([kyka__jxsld])
    return hctuo__jdoy


def pre_alloc_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


from numba.parfors.array_analysis import ArrayAnalysis
(ArrayAnalysis._analyze_op_call_bodo_libs_str_arr_ext_pre_alloc_string_array
    ) = pre_alloc_str_arr_equiv


@overload(glob.glob, no_unliteral=True)
def overload_glob_glob(pathname, recursive=False):

    def _glob_glob_impl(pathname, recursive=False):
        with numba.objmode(l='list_str_type'):
            l = glob.glob(pathname, recursive=recursive)
        return l
    return _glob_glob_impl
