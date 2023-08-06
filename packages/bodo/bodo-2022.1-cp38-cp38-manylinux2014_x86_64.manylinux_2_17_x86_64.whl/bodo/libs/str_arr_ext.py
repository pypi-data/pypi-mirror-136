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
        pgeo__lmoax = ArrayItemArrayType(char_arr_type)
        hhe__jlge = [('data', pgeo__lmoax)]
        models.StructModel.__init__(self, dmm, fe_type, hhe__jlge)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        wuus__xnyl, = args
        ecjz__utlvk = context.make_helper(builder, string_array_type)
        ecjz__utlvk.data = wuus__xnyl
        context.nrt.incref(builder, data_typ, wuus__xnyl)
        return ecjz__utlvk._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    wfoih__dgjl = c.context.insert_const_string(c.builder.module, 'pandas')
    hbbk__dyl = c.pyapi.import_module_noblock(wfoih__dgjl)
    smcdu__djka = c.pyapi.call_method(hbbk__dyl, 'StringDtype', ())
    c.pyapi.decref(hbbk__dyl)
    return smcdu__djka


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
                ebk__dpao = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ebk__dpao)
                for i in numba.parfors.parfor.internal_prange(ebk__dpao):
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
                ebk__dpao = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ebk__dpao)
                for i in numba.parfors.parfor.internal_prange(ebk__dpao):
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
                ebk__dpao = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ebk__dpao)
                for i in numba.parfors.parfor.internal_prange(ebk__dpao):
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
    recx__vwt = lhs == string_array_type or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    kpryl__znuu = rhs == string_array_type or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if (lhs == string_array_type and kpryl__znuu or recx__vwt and rhs ==
        string_array_type):

        def impl_both(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for dsg__vqtjq in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, dsg__vqtjq
                    ) or bodo.libs.array_kernels.isna(rhs, dsg__vqtjq):
                    out_arr[dsg__vqtjq] = ''
                    bodo.libs.array_kernels.setna(out_arr, dsg__vqtjq)
                else:
                    out_arr[dsg__vqtjq] = lhs[dsg__vqtjq] + rhs[dsg__vqtjq]
            return out_arr
        return impl_both
    if lhs == string_array_type and types.unliteral(rhs) == string_type:

        def impl_left(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for dsg__vqtjq in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, dsg__vqtjq):
                    out_arr[dsg__vqtjq] = ''
                    bodo.libs.array_kernels.setna(out_arr, dsg__vqtjq)
                else:
                    out_arr[dsg__vqtjq] = lhs[dsg__vqtjq] + rhs
            return out_arr
        return impl_left
    if types.unliteral(lhs) == string_type and rhs == string_array_type:

        def impl_right(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(rhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for dsg__vqtjq in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(rhs, dsg__vqtjq):
                    out_arr[dsg__vqtjq] = ''
                    bodo.libs.array_kernels.setna(out_arr, dsg__vqtjq)
                else:
                    out_arr[dsg__vqtjq] = lhs + rhs[dsg__vqtjq]
            return out_arr
        return impl_right


def overload_mul_operator_str_arr(lhs, rhs):
    if lhs == string_array_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for dsg__vqtjq in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, dsg__vqtjq):
                    out_arr[dsg__vqtjq] = ''
                    bodo.libs.array_kernels.setna(out_arr, dsg__vqtjq)
                else:
                    out_arr[dsg__vqtjq] = lhs[dsg__vqtjq] * rhs
            return out_arr
        return impl
    if isinstance(lhs, types.Integer) and rhs == string_array_type:

        def impl(lhs, rhs):
            return rhs * lhs
        return impl


class StringArrayIterator(types.SimpleIteratorType):

    def __init__(self):
        qupfw__eibdg = 'iter(String)'
        cjny__jub = string_type
        super(StringArrayIterator, self).__init__(qupfw__eibdg, cjny__jub)


@register_model(StringArrayIterator)
class StrArrayIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hhe__jlge = [('index', types.EphemeralPointer(types.uintp)), (
            'array', string_array_type)]
        super(StrArrayIteratorModel, self).__init__(dmm, fe_type, hhe__jlge)


lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@lower_builtin('iternext', StringArrayIterator)
@iternext_impl(RefType.NEW)
def iternext_str_array(context, builder, sig, args, result):
    [pkdi__ewm] = sig.args
    [tynz__hrsys] = args
    tzzw__wxemg = context.make_helper(builder, pkdi__ewm, value=tynz__hrsys)
    nlqr__bvgii = signature(types.intp, string_array_type)
    ecu__rtvxv = context.compile_internal(builder, lambda a: len(a),
        nlqr__bvgii, [tzzw__wxemg.array])
    mqpw__dbo = builder.load(tzzw__wxemg.index)
    iobqo__rore = builder.icmp(lc.ICMP_SLT, mqpw__dbo, ecu__rtvxv)
    result.set_valid(iobqo__rore)
    with builder.if_then(iobqo__rore):
        bhhy__rqp = signature(string_type, string_array_type, types.intp)
        value = context.compile_internal(builder, lambda a, i: a[i],
            bhhy__rqp, [tzzw__wxemg.array, mqpw__dbo])
        result.yield_(value)
        vie__efze = cgutils.increment_index(builder, mqpw__dbo)
        builder.store(vie__efze, tzzw__wxemg.index)


def _get_str_binary_arr_payload(context, builder, arr_value, arr_typ):
    assert arr_typ == string_array_type or arr_typ == binary_array_type
    iynv__idpf = context.make_helper(builder, arr_typ, arr_value)
    pgeo__lmoax = ArrayItemArrayType(char_arr_type)
    whcem__fgxqf = _get_array_item_arr_payload(context, builder,
        pgeo__lmoax, iynv__idpf.data)
    return whcem__fgxqf


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return whcem__fgxqf.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        ncj__ueo = context.make_helper(builder, offset_arr_type,
            whcem__fgxqf.offsets).data
        return _get_num_total_chars(builder, ncj__ueo, whcem__fgxqf.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        chj__ydxqj = context.make_helper(builder, offset_arr_type,
            whcem__fgxqf.offsets)
        twblq__aqt = context.make_helper(builder, offset_ctypes_type)
        twblq__aqt.data = builder.bitcast(chj__ydxqj.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        twblq__aqt.meminfo = chj__ydxqj.meminfo
        smcdu__djka = twblq__aqt._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            smcdu__djka)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        wuus__xnyl = context.make_helper(builder, char_arr_type,
            whcem__fgxqf.data)
        twblq__aqt = context.make_helper(builder, data_ctypes_type)
        twblq__aqt.data = wuus__xnyl.data
        twblq__aqt.meminfo = wuus__xnyl.meminfo
        smcdu__djka = twblq__aqt._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            smcdu__djka)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        vbadv__wzj, ind = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            vbadv__wzj, sig.args[0])
        wuus__xnyl = context.make_helper(builder, char_arr_type,
            whcem__fgxqf.data)
        twblq__aqt = context.make_helper(builder, data_ctypes_type)
        twblq__aqt.data = builder.gep(wuus__xnyl.data, [ind])
        twblq__aqt.meminfo = wuus__xnyl.meminfo
        smcdu__djka = twblq__aqt._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            smcdu__djka)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        rmjr__ohl, igo__tdbcg, xmxby__pqj, ejnw__vnw = args
        xaixt__vjp = builder.bitcast(builder.gep(rmjr__ohl, [igo__tdbcg]),
            lir.IntType(8).as_pointer())
        oup__bvpp = builder.bitcast(builder.gep(xmxby__pqj, [ejnw__vnw]),
            lir.IntType(8).as_pointer())
        yrmj__fuzuy = builder.load(oup__bvpp)
        builder.store(yrmj__fuzuy, xaixt__vjp)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        aau__fdz = context.make_helper(builder, null_bitmap_arr_type,
            whcem__fgxqf.null_bitmap)
        twblq__aqt = context.make_helper(builder, data_ctypes_type)
        twblq__aqt.data = aau__fdz.data
        twblq__aqt.meminfo = aau__fdz.meminfo
        smcdu__djka = twblq__aqt._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            smcdu__djka)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        ncj__ueo = context.make_helper(builder, offset_arr_type,
            whcem__fgxqf.offsets).data
        return builder.load(builder.gep(ncj__ueo, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type,
            whcem__fgxqf.offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        gszw__hwzx, ind = args
        if in_bitmap_typ == data_ctypes_type:
            twblq__aqt = context.make_helper(builder, data_ctypes_type,
                gszw__hwzx)
            gszw__hwzx = twblq__aqt.data
        return builder.load(builder.gep(gszw__hwzx, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        gszw__hwzx, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            twblq__aqt = context.make_helper(builder, data_ctypes_type,
                gszw__hwzx)
            gszw__hwzx = twblq__aqt.data
        builder.store(val, builder.gep(gszw__hwzx, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        vbcwp__ksl = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pmnbl__rbyh = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        wvyk__gbcb = context.make_helper(builder, offset_arr_type,
            vbcwp__ksl.offsets).data
        eyx__awoti = context.make_helper(builder, offset_arr_type,
            pmnbl__rbyh.offsets).data
        jzcg__pijmu = context.make_helper(builder, char_arr_type,
            vbcwp__ksl.data).data
        dupr__gbsfl = context.make_helper(builder, char_arr_type,
            pmnbl__rbyh.data).data
        ulsz__wlyk = context.make_helper(builder, null_bitmap_arr_type,
            vbcwp__ksl.null_bitmap).data
        vjext__wekea = context.make_helper(builder, null_bitmap_arr_type,
            pmnbl__rbyh.null_bitmap).data
        xszvo__kcfy = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, eyx__awoti, wvyk__gbcb, xszvo__kcfy)
        cgutils.memcpy(builder, dupr__gbsfl, jzcg__pijmu, builder.load(
            builder.gep(wvyk__gbcb, [ind])))
        jaqq__scq = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        upard__lios = builder.lshr(jaqq__scq, lir.Constant(lir.IntType(64), 3))
        cgutils.memcpy(builder, vjext__wekea, ulsz__wlyk, upard__lios)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        vbcwp__ksl = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pmnbl__rbyh = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        wvyk__gbcb = context.make_helper(builder, offset_arr_type,
            vbcwp__ksl.offsets).data
        jzcg__pijmu = context.make_helper(builder, char_arr_type,
            vbcwp__ksl.data).data
        dupr__gbsfl = context.make_helper(builder, char_arr_type,
            pmnbl__rbyh.data).data
        num_total_chars = _get_num_total_chars(builder, wvyk__gbcb,
            vbcwp__ksl.n_arrays)
        cgutils.memcpy(builder, dupr__gbsfl, jzcg__pijmu, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        vbcwp__ksl = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pmnbl__rbyh = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        wvyk__gbcb = context.make_helper(builder, offset_arr_type,
            vbcwp__ksl.offsets).data
        eyx__awoti = context.make_helper(builder, offset_arr_type,
            pmnbl__rbyh.offsets).data
        ulsz__wlyk = context.make_helper(builder, null_bitmap_arr_type,
            vbcwp__ksl.null_bitmap).data
        ebk__dpao = vbcwp__ksl.n_arrays
        itakp__okql = context.get_constant(offset_type, 0)
        lilwk__bds = cgutils.alloca_once_value(builder, itakp__okql)
        with cgutils.for_range(builder, ebk__dpao) as loop:
            uallk__svp = lower_is_na(context, builder, ulsz__wlyk, loop.index)
            with cgutils.if_likely(builder, builder.not_(uallk__svp)):
                nanj__pgmp = builder.load(builder.gep(wvyk__gbcb, [loop.index])
                    )
                uupl__gnius = builder.load(lilwk__bds)
                builder.store(nanj__pgmp, builder.gep(eyx__awoti, [
                    uupl__gnius]))
                builder.store(builder.add(uupl__gnius, lir.Constant(context
                    .get_value_type(offset_type), 1)), lilwk__bds)
        uupl__gnius = builder.load(lilwk__bds)
        nanj__pgmp = builder.load(builder.gep(wvyk__gbcb, [ebk__dpao]))
        builder.store(nanj__pgmp, builder.gep(eyx__awoti, [uupl__gnius]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        bjmd__scg, ind, str, kvn__zwwnk = args
        bjmd__scg = context.make_array(sig.args[0])(context, builder, bjmd__scg
            )
        ill__hnas = builder.gep(bjmd__scg.data, [ind])
        cgutils.raw_memcpy(builder, ill__hnas, str, kvn__zwwnk, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        ill__hnas, ind, xxv__suvdw, kvn__zwwnk = args
        ill__hnas = builder.gep(ill__hnas, [ind])
        cgutils.raw_memcpy(builder, ill__hnas, xxv__suvdw, kvn__zwwnk, 1)
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
    ebk__dpao = len(str_arr)
    ggvf__weume = np.empty(ebk__dpao, np.bool_)
    for i in range(ebk__dpao):
        ggvf__weume[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return ggvf__weume


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if data in [string_array_type, binary_array_type]:

        def to_list_impl(data, str_null_bools=None):
            ebk__dpao = len(data)
            l = []
            for i in range(ebk__dpao):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        wdfc__spdp = data.count
        xqacu__npib = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(wdfc__spdp)]
        if is_overload_true(str_null_bools):
            xqacu__npib += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(wdfc__spdp) if data.types[i] in [string_array_type,
                binary_array_type]]
        hqo__huuw = 'def f(data, str_null_bools=None):\n'
        hqo__huuw += '  return ({}{})\n'.format(', '.join(xqacu__npib), ',' if
            wdfc__spdp == 1 else '')
        kgja__hsde = {}
        exec(hqo__huuw, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, kgja__hsde)
        isa__uxfwr = kgja__hsde['f']
        return isa__uxfwr
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                ebk__dpao = len(list_data)
                for i in range(ebk__dpao):
                    xxv__suvdw = list_data[i]
                    str_arr[i] = xxv__suvdw
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                ebk__dpao = len(list_data)
                for i in range(ebk__dpao):
                    xxv__suvdw = list_data[i]
                    str_arr[i] = xxv__suvdw
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        wdfc__spdp = str_arr.count
        ngih__dpr = 0
        hqo__huuw = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(wdfc__spdp):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                hqo__huuw += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, wdfc__spdp + ngih__dpr))
                ngih__dpr += 1
            else:
                hqo__huuw += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        hqo__huuw += '  return\n'
        kgja__hsde = {}
        exec(hqo__huuw, {'cp_str_list_to_array': cp_str_list_to_array},
            kgja__hsde)
        xyc__usnys = kgja__hsde['f']
        return xyc__usnys
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            ebk__dpao = len(str_list)
            str_arr = pre_alloc_string_array(ebk__dpao, -1)
            for i in range(ebk__dpao):
                xxv__suvdw = str_list[i]
                str_arr[i] = xxv__suvdw
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            ebk__dpao = len(A)
            zbc__rvkpw = 0
            for i in range(ebk__dpao):
                xxv__suvdw = A[i]
                zbc__rvkpw += get_utf8_size(xxv__suvdw)
            return zbc__rvkpw
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        ebk__dpao = len(arr)
        n_chars = num_total_chars(arr)
        laerj__lwa = pre_alloc_string_array(ebk__dpao, np.int64(n_chars))
        copy_str_arr_slice(laerj__lwa, arr, ebk__dpao)
        return laerj__lwa
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
    hqo__huuw = 'def f(in_seq):\n'
    hqo__huuw += '    n_strs = len(in_seq)\n'
    hqo__huuw += '    A = pre_alloc_string_array(n_strs, -1)\n'
    hqo__huuw += '    return A\n'
    kgja__hsde = {}
    exec(hqo__huuw, {'pre_alloc_string_array': pre_alloc_string_array},
        kgja__hsde)
    bdsc__mxls = kgja__hsde['f']
    return bdsc__mxls


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    if in_seq.dtype == bodo.bytes_type:
        evlzg__gnkat = 'pre_alloc_binary_array'
    else:
        evlzg__gnkat = 'pre_alloc_string_array'
    hqo__huuw = 'def f(in_seq):\n'
    hqo__huuw += '    n_strs = len(in_seq)\n'
    hqo__huuw += f'    A = {evlzg__gnkat}(n_strs, -1)\n'
    hqo__huuw += '    for i in range(n_strs):\n'
    hqo__huuw += '        A[i] = in_seq[i]\n'
    hqo__huuw += '    return A\n'
    kgja__hsde = {}
    exec(hqo__huuw, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, kgja__hsde)
    bdsc__mxls = kgja__hsde['f']
    return bdsc__mxls


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        wxu__xmy = builder.add(whcem__fgxqf.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        axjav__iig = builder.lshr(lir.Constant(lir.IntType(64), offset_type
            .bitwidth), lir.Constant(lir.IntType(64), 3))
        upard__lios = builder.mul(wxu__xmy, axjav__iig)
        qfc__dod = context.make_array(offset_arr_type)(context, builder,
            whcem__fgxqf.offsets).data
        cgutils.memset(builder, qfc__dod, upard__lios, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        ahh__xaxcf = whcem__fgxqf.n_arrays
        upard__lios = builder.lshr(builder.add(ahh__xaxcf, lir.Constant(lir
            .IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        miakj__qjdt = context.make_array(null_bitmap_arr_type)(context,
            builder, whcem__fgxqf.null_bitmap).data
        cgutils.memset(builder, miakj__qjdt, upard__lios, 0)
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
    jcsdg__zojcj = 0
    spo__olwk = len(len_arr)
    for i in range(spo__olwk):
        offsets[i] = jcsdg__zojcj
        jcsdg__zojcj += len_arr[i]
    offsets[spo__olwk] = jcsdg__zojcj
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    zox__uyqr = i // 8
    iwjh__wtibl = getitem_str_bitmap(bits, zox__uyqr)
    iwjh__wtibl ^= np.uint8(-np.uint8(bit_is_set) ^ iwjh__wtibl) & kBitmask[
        i % 8]
    setitem_str_bitmap(bits, zox__uyqr, iwjh__wtibl)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    euszf__anb = get_null_bitmap_ptr(out_str_arr)
    ylgo__wkzi = get_null_bitmap_ptr(in_str_arr)
    for dsg__vqtjq in range(len(in_str_arr)):
        blbz__rzjmi = get_bit_bitmap(ylgo__wkzi, dsg__vqtjq)
        set_bit_to(euszf__anb, out_start + dsg__vqtjq, blbz__rzjmi)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type
    assert curr_str_typ == types.intp and curr_chars_typ == types.intp

    def codegen(context, builder, sig, args):
        out_arr, vbadv__wzj, hzdpg__duubg, cra__jzcb = args
        vbcwp__ksl = _get_str_binary_arr_payload(context, builder,
            vbadv__wzj, string_array_type)
        pmnbl__rbyh = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        wvyk__gbcb = context.make_helper(builder, offset_arr_type,
            vbcwp__ksl.offsets).data
        eyx__awoti = context.make_helper(builder, offset_arr_type,
            pmnbl__rbyh.offsets).data
        jzcg__pijmu = context.make_helper(builder, char_arr_type,
            vbcwp__ksl.data).data
        dupr__gbsfl = context.make_helper(builder, char_arr_type,
            pmnbl__rbyh.data).data
        num_total_chars = _get_num_total_chars(builder, wvyk__gbcb,
            vbcwp__ksl.n_arrays)
        vkh__grzz = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        rnz__ogrih = cgutils.get_or_insert_function(builder.module,
            vkh__grzz, name='set_string_array_range')
        builder.call(rnz__ogrih, [eyx__awoti, dupr__gbsfl, wvyk__gbcb,
            jzcg__pijmu, hzdpg__duubg, cra__jzcb, vbcwp__ksl.n_arrays,
            num_total_chars])
        jedk__dpzy = context.typing_context.resolve_value_type(copy_nulls_range
            )
        jcahx__jga = jedk__dpzy.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        nyoyq__jhadw = context.get_function(jedk__dpzy, jcahx__jga)
        nyoyq__jhadw(builder, (out_arr, vbadv__wzj, hzdpg__duubg))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    mqc__wmkd = c.context.make_helper(c.builder, typ, val)
    pgeo__lmoax = ArrayItemArrayType(char_arr_type)
    whcem__fgxqf = _get_array_item_arr_payload(c.context, c.builder,
        pgeo__lmoax, mqc__wmkd.data)
    tjxuy__ovr = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    bdk__knn = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        bdk__knn = 'pd_array_from_string_array'
    vkh__grzz = lir.FunctionType(c.context.get_argument_type(types.pyobject
        ), [lir.IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
        lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
        IntType(32)])
    behbf__clac = cgutils.get_or_insert_function(c.builder.module,
        vkh__grzz, name=bdk__knn)
    ncj__ueo = c.context.make_array(offset_arr_type)(c.context, c.builder,
        whcem__fgxqf.offsets).data
    ieh__uhx = c.context.make_array(char_arr_type)(c.context, c.builder,
        whcem__fgxqf.data).data
    miakj__qjdt = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, whcem__fgxqf.null_bitmap).data
    arr = c.builder.call(behbf__clac, [whcem__fgxqf.n_arrays, ncj__ueo,
        ieh__uhx, miakj__qjdt, tjxuy__ovr])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        miakj__qjdt = context.make_array(null_bitmap_arr_type)(context,
            builder, whcem__fgxqf.null_bitmap).data
        szi__nik = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        cllbt__uyuop = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        iwjh__wtibl = builder.load(builder.gep(miakj__qjdt, [szi__nik],
            inbounds=True))
        osnk__gkfpy = lir.ArrayType(lir.IntType(8), 8)
        fffwz__jxrfr = cgutils.alloca_once_value(builder, lir.Constant(
            osnk__gkfpy, (1, 2, 4, 8, 16, 32, 64, 128)))
        ayrw__jemhd = builder.load(builder.gep(fffwz__jxrfr, [lir.Constant(
            lir.IntType(64), 0), cllbt__uyuop], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(iwjh__wtibl,
            ayrw__jemhd), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        szi__nik = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        cllbt__uyuop = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        miakj__qjdt = context.make_array(null_bitmap_arr_type)(context,
            builder, whcem__fgxqf.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type,
            whcem__fgxqf.offsets).data
        ujvef__mvwib = builder.gep(miakj__qjdt, [szi__nik], inbounds=True)
        iwjh__wtibl = builder.load(ujvef__mvwib)
        osnk__gkfpy = lir.ArrayType(lir.IntType(8), 8)
        fffwz__jxrfr = cgutils.alloca_once_value(builder, lir.Constant(
            osnk__gkfpy, (1, 2, 4, 8, 16, 32, 64, 128)))
        ayrw__jemhd = builder.load(builder.gep(fffwz__jxrfr, [lir.Constant(
            lir.IntType(64), 0), cllbt__uyuop], inbounds=True))
        ayrw__jemhd = builder.xor(ayrw__jemhd, lir.Constant(lir.IntType(8), -1)
            )
        builder.store(builder.and_(iwjh__wtibl, ayrw__jemhd), ujvef__mvwib)
        if str_arr_typ == string_array_type:
            drh__qtna = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            krknd__prb = builder.icmp_unsigned('!=', drh__qtna,
                whcem__fgxqf.n_arrays)
            with builder.if_then(krknd__prb):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [drh__qtna]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        szi__nik = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        cllbt__uyuop = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        miakj__qjdt = context.make_array(null_bitmap_arr_type)(context,
            builder, whcem__fgxqf.null_bitmap).data
        ujvef__mvwib = builder.gep(miakj__qjdt, [szi__nik], inbounds=True)
        iwjh__wtibl = builder.load(ujvef__mvwib)
        osnk__gkfpy = lir.ArrayType(lir.IntType(8), 8)
        fffwz__jxrfr = cgutils.alloca_once_value(builder, lir.Constant(
            osnk__gkfpy, (1, 2, 4, 8, 16, 32, 64, 128)))
        ayrw__jemhd = builder.load(builder.gep(fffwz__jxrfr, [lir.Constant(
            lir.IntType(64), 0), cllbt__uyuop], inbounds=True))
        builder.store(builder.or_(iwjh__wtibl, ayrw__jemhd), ujvef__mvwib)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        upard__lios = builder.udiv(builder.add(whcem__fgxqf.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        miakj__qjdt = context.make_array(null_bitmap_arr_type)(context,
            builder, whcem__fgxqf.null_bitmap).data
        cgutils.memset(builder, miakj__qjdt, upard__lios, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    fhs__mlo = context.make_helper(builder, string_array_type, str_arr)
    pgeo__lmoax = ArrayItemArrayType(char_arr_type)
    dvb__rrap = context.make_helper(builder, pgeo__lmoax, fhs__mlo.data)
    qre__sno = ArrayItemArrayPayloadType(pgeo__lmoax)
    abwry__xhu = context.nrt.meminfo_data(builder, dvb__rrap.meminfo)
    ozkgk__utgmx = builder.bitcast(abwry__xhu, context.get_value_type(
        qre__sno).as_pointer())
    return ozkgk__utgmx


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        jyg__azo, jcssb__ejsw = args
        txx__cbyqk = _get_str_binary_arr_data_payload_ptr(context, builder,
            jcssb__ejsw)
        lqgfl__kqr = _get_str_binary_arr_data_payload_ptr(context, builder,
            jyg__azo)
        pqevr__qmku = _get_str_binary_arr_payload(context, builder,
            jcssb__ejsw, sig.args[1])
        rciqn__nlwln = _get_str_binary_arr_payload(context, builder,
            jyg__azo, sig.args[0])
        context.nrt.incref(builder, char_arr_type, pqevr__qmku.data)
        context.nrt.incref(builder, offset_arr_type, pqevr__qmku.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, pqevr__qmku.
            null_bitmap)
        context.nrt.decref(builder, char_arr_type, rciqn__nlwln.data)
        context.nrt.decref(builder, offset_arr_type, rciqn__nlwln.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, rciqn__nlwln.
            null_bitmap)
        builder.store(builder.load(txx__cbyqk), lqgfl__kqr)
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
        ebk__dpao = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return ebk__dpao
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, ill__hnas, tlzd__ixsds = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder, arr,
            sig.args[0])
        offsets = context.make_helper(builder, offset_arr_type,
            whcem__fgxqf.offsets).data
        data = context.make_helper(builder, char_arr_type, whcem__fgxqf.data
            ).data
        vkh__grzz = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        gifn__cgi = cgutils.get_or_insert_function(builder.module,
            vkh__grzz, name='setitem_string_array')
        oujsg__aqjro = context.get_constant(types.int32, -1)
        anjy__clj = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets,
            whcem__fgxqf.n_arrays)
        builder.call(gifn__cgi, [offsets, data, num_total_chars, builder.
            extract_value(ill__hnas, 0), tlzd__ixsds, oujsg__aqjro,
            anjy__clj, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    vkh__grzz = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer
        (), lir.IntType(64)])
    rbmvb__czz = cgutils.get_or_insert_function(builder.module, vkh__grzz,
        name='is_na')
    return builder.call(rbmvb__czz, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        xaixt__vjp, oup__bvpp, wdfc__spdp, qcx__squx = args
        cgutils.raw_memcpy(builder, xaixt__vjp, oup__bvpp, wdfc__spdp,
            qcx__squx)
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
        vgp__eoj, dnow__lybhq = unicode_to_utf8_and_len(val)
        jiwnp__qswm = getitem_str_offset(A, ind)
        fwoh__jsn = getitem_str_offset(A, ind + 1)
        ozm__dniz = fwoh__jsn - jiwnp__qswm
        if ozm__dniz != dnow__lybhq:
            return False
        ill__hnas = get_data_ptr_ind(A, jiwnp__qswm)
        return memcmp(ill__hnas, vgp__eoj, dnow__lybhq) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        jiwnp__qswm = getitem_str_offset(A, ind)
        ozm__dniz = bodo.libs.str_ext.int_to_str_len(val)
        jeixl__geucm = jiwnp__qswm + ozm__dniz
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            jiwnp__qswm, jeixl__geucm)
        ill__hnas = get_data_ptr_ind(A, jiwnp__qswm)
        inplace_int64_to_str(ill__hnas, ozm__dniz, val)
        setitem_str_offset(A, ind + 1, jiwnp__qswm + ozm__dniz)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        ill__hnas, = args
        bsrwf__rqp = context.insert_const_string(builder.module, '<NA>')
        ezf__cckc = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, ill__hnas, bsrwf__rqp, ezf__cckc, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    hvf__arsx = len('<NA>')

    def impl(A, ind):
        jiwnp__qswm = getitem_str_offset(A, ind)
        jeixl__geucm = jiwnp__qswm + hvf__arsx
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            jiwnp__qswm, jeixl__geucm)
        ill__hnas = get_data_ptr_ind(A, jiwnp__qswm)
        inplace_set_NA_str(ill__hnas)
        setitem_str_offset(A, ind + 1, jiwnp__qswm + hvf__arsx)
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
            jiwnp__qswm = getitem_str_offset(A, ind)
            fwoh__jsn = getitem_str_offset(A, ind + 1)
            tlzd__ixsds = fwoh__jsn - jiwnp__qswm
            ill__hnas = get_data_ptr_ind(A, jiwnp__qswm)
            tdp__lafb = decode_utf8(ill__hnas, tlzd__ixsds)
            return tdp__lafb
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            ebk__dpao = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(ebk__dpao):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            sgo__tsn = get_data_ptr(out_arr).data
            vvxy__limwt = get_data_ptr(A).data
            ngih__dpr = 0
            uupl__gnius = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(ebk__dpao):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    wsh__vzzd = get_str_arr_item_length(A, i)
                    if wsh__vzzd == 1:
                        copy_single_char(sgo__tsn, uupl__gnius, vvxy__limwt,
                            getitem_str_offset(A, i))
                    else:
                        memcpy_region(sgo__tsn, uupl__gnius, vvxy__limwt,
                            getitem_str_offset(A, i), wsh__vzzd, 1)
                    uupl__gnius += wsh__vzzd
                    setitem_str_offset(out_arr, ngih__dpr + 1, uupl__gnius)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, ngih__dpr)
                    else:
                        str_arr_set_not_na(out_arr, ngih__dpr)
                    ngih__dpr += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            ebk__dpao = len(ind)
            out_arr = pre_alloc_string_array(ebk__dpao, -1)
            ngih__dpr = 0
            for i in range(ebk__dpao):
                xxv__suvdw = A[ind[i]]
                out_arr[ngih__dpr] = xxv__suvdw
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, ngih__dpr)
                ngih__dpr += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            ebk__dpao = len(A)
            ikm__urgch = numba.cpython.unicode._normalize_slice(ind, ebk__dpao)
            bii__vqhxn = numba.cpython.unicode._slice_span(ikm__urgch)
            if ikm__urgch.step == 1:
                jiwnp__qswm = getitem_str_offset(A, ikm__urgch.start)
                fwoh__jsn = getitem_str_offset(A, ikm__urgch.stop)
                n_chars = fwoh__jsn - jiwnp__qswm
                laerj__lwa = pre_alloc_string_array(bii__vqhxn, np.int64(
                    n_chars))
                for i in range(bii__vqhxn):
                    laerj__lwa[i] = A[ikm__urgch.start + i]
                    if str_arr_is_na(A, ikm__urgch.start + i):
                        str_arr_set_na(laerj__lwa, i)
                return laerj__lwa
            else:
                laerj__lwa = pre_alloc_string_array(bii__vqhxn, -1)
                for i in range(bii__vqhxn):
                    laerj__lwa[i] = A[ikm__urgch.start + i * ikm__urgch.step]
                    if str_arr_is_na(A, ikm__urgch.start + i * ikm__urgch.step
                        ):
                        str_arr_set_na(laerj__lwa, i)
                return laerj__lwa
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
    bkt__mfro = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(bkt__mfro)
        szw__mrdls = 4

        def impl_scalar(A, idx, val):
            uitlk__jjbm = (val._length if val._is_ascii else szw__mrdls *
                val._length)
            wuus__xnyl = A._data
            jiwnp__qswm = np.int64(getitem_str_offset(A, idx))
            jeixl__geucm = jiwnp__qswm + uitlk__jjbm
            bodo.libs.array_item_arr_ext.ensure_data_capacity(wuus__xnyl,
                jiwnp__qswm, jeixl__geucm)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                jeixl__geucm, val._data, val._length, val._kind, val.
                _is_ascii, idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                ikm__urgch = numba.cpython.unicode._normalize_slice(idx, len(A)
                    )
                zzn__aiaxd = ikm__urgch.start
                wuus__xnyl = A._data
                jiwnp__qswm = np.int64(getitem_str_offset(A, zzn__aiaxd))
                jeixl__geucm = jiwnp__qswm + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(wuus__xnyl,
                    jiwnp__qswm, jeixl__geucm)
                set_string_array_range(A, val, zzn__aiaxd, jiwnp__qswm)
                oyi__rhlio = 0
                for i in range(ikm__urgch.start, ikm__urgch.stop,
                    ikm__urgch.step):
                    if str_arr_is_na(val, oyi__rhlio):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    oyi__rhlio += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                zwiyk__cmwl = str_list_to_array(val)
                A[idx] = zwiyk__cmwl
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                ikm__urgch = numba.cpython.unicode._normalize_slice(idx, len(A)
                    )
                for i in range(ikm__urgch.start, ikm__urgch.stop,
                    ikm__urgch.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(bkt__mfro)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                ebk__dpao = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(ebk__dpao, -1)
                for i in numba.parfors.parfor.internal_prange(ebk__dpao):
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
                ebk__dpao = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(ebk__dpao, -1)
                slljw__wemc = 0
                for i in numba.parfors.parfor.internal_prange(ebk__dpao):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, slljw__wemc):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, slljw__wemc)
                        else:
                            out_arr[i] = str(val[slljw__wemc])
                        slljw__wemc += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        out_arr[i] = A[i]
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(bkt__mfro)
    raise BodoError(bkt__mfro)


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
    lbunp__cism = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(lbunp__cism, (types.Float, types.Integer)):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(lbunp__cism, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ebk__dpao = len(A)
            kdyc__msco = np.empty(ebk__dpao, lbunp__cism)
            for i in numba.parfors.parfor.internal_prange(ebk__dpao):
                if bodo.libs.array_kernels.isna(A, i):
                    kdyc__msco[i] = np.nan
                else:
                    kdyc__msco[i] = float(A[i])
            return kdyc__msco
        return impl_float
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ebk__dpao = len(A)
            kdyc__msco = np.empty(ebk__dpao, lbunp__cism)
            for i in numba.parfors.parfor.internal_prange(ebk__dpao):
                kdyc__msco[i] = int(A[i])
            return kdyc__msco
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        ill__hnas, tlzd__ixsds = args
        hwfh__ubqij = context.get_python_api(builder)
        uxc__vhtj = hwfh__ubqij.string_from_string_and_size(ill__hnas,
            tlzd__ixsds)
        qhbs__nnrdl = hwfh__ubqij.to_native_value(string_type, uxc__vhtj).value
        uzj__bgmcd = cgutils.create_struct_proxy(string_type)(context,
            builder, qhbs__nnrdl)
        uzj__bgmcd.hash = uzj__bgmcd.hash.type(-1)
        hwfh__ubqij.decref(uxc__vhtj)
        return uzj__bgmcd._getvalue()
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
        mbh__vovro, arr, ind, ietm__cxg = args
        whcem__fgxqf = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type,
            whcem__fgxqf.offsets).data
        data = context.make_helper(builder, char_arr_type, whcem__fgxqf.data
            ).data
        vkh__grzz = lir.FunctionType(lir.IntType(32), [mbh__vovro.type, lir
            .IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        jsrg__kau = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            jsrg__kau = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        vknd__rkegy = cgutils.get_or_insert_function(builder.module,
            vkh__grzz, jsrg__kau)
        return builder.call(vknd__rkegy, [mbh__vovro, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    tjxuy__ovr = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    vkh__grzz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(
        8).as_pointer(), lir.IntType(32)])
    clyhd__kszg = cgutils.get_or_insert_function(c.builder.module,
        vkh__grzz, name='string_array_from_sequence')
    pll__ppf = c.builder.call(clyhd__kszg, [val, tjxuy__ovr])
    pgeo__lmoax = ArrayItemArrayType(char_arr_type)
    dvb__rrap = c.context.make_helper(c.builder, pgeo__lmoax)
    dvb__rrap.meminfo = pll__ppf
    fhs__mlo = c.context.make_helper(c.builder, typ)
    wuus__xnyl = dvb__rrap._getvalue()
    fhs__mlo.data = wuus__xnyl
    vfij__ifutq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(fhs__mlo._getvalue(), is_error=vfij__ifutq)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    ebk__dpao = len(pyval)
    uupl__gnius = 0
    hjr__vrye = np.empty(ebk__dpao + 1, np_offset_type)
    ptq__klf = []
    rupg__zkp = np.empty(ebk__dpao + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        hjr__vrye[i] = uupl__gnius
        taan__gvvk = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(rupg__zkp, i, int(not taan__gvvk))
        if taan__gvvk:
            continue
        tvzkp__gza = list(s.encode()) if isinstance(s, str) else list(s)
        ptq__klf.extend(tvzkp__gza)
        uupl__gnius += len(tvzkp__gza)
    hjr__vrye[ebk__dpao] = uupl__gnius
    sqy__wbui = np.array(ptq__klf, np.uint8)
    bvv__irc = context.get_constant(types.int64, ebk__dpao)
    ibg__uaokv = context.get_constant_generic(builder, char_arr_type, sqy__wbui
        )
    ooiqi__eddl = context.get_constant_generic(builder, offset_arr_type,
        hjr__vrye)
    jxck__mmdej = context.get_constant_generic(builder,
        null_bitmap_arr_type, rupg__zkp)
    whcem__fgxqf = lir.Constant.literal_struct([bvv__irc, ibg__uaokv,
        ooiqi__eddl, jxck__mmdej])
    whcem__fgxqf = cgutils.global_constant(builder, '.const.payload',
        whcem__fgxqf).bitcast(cgutils.voidptr_t)
    ydg__ivn = context.get_constant(types.int64, -1)
    zirs__dfki = context.get_constant_null(types.voidptr)
    pymhh__ypg = lir.Constant.literal_struct([ydg__ivn, zirs__dfki,
        zirs__dfki, whcem__fgxqf, ydg__ivn])
    pymhh__ypg = cgutils.global_constant(builder, '.const.meminfo', pymhh__ypg
        ).bitcast(cgutils.voidptr_t)
    wuus__xnyl = lir.Constant.literal_struct([pymhh__ypg])
    fhs__mlo = lir.Constant.literal_struct([wuus__xnyl])
    return fhs__mlo


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
