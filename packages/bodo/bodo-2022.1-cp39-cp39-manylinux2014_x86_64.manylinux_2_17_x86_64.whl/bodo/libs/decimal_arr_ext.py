"""Decimal array corresponding to Arrow Decimal128Array type.
It is similar to Spark's DecimalType. From Spark's docs:
'The DecimalType must have fixed precision (the maximum total number of digits) and
scale (the number of digits on the right of dot). For example, (5, 2) can support the
value from [-999.99 to 999.99].
The precision can be up to 38, the scale must be less or equal to precision.'
'When infer schema from decimal.Decimal objects, it will be DecimalType(38, 18).'
"""
import operator
from decimal import Decimal
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import decimal_ext
ll.add_symbol('box_decimal_array', decimal_ext.box_decimal_array)
ll.add_symbol('unbox_decimal', decimal_ext.unbox_decimal)
ll.add_symbol('unbox_decimal_array', decimal_ext.unbox_decimal_array)
ll.add_symbol('decimal_to_str', decimal_ext.decimal_to_str)
ll.add_symbol('str_to_decimal', decimal_ext.str_to_decimal)
ll.add_symbol('decimal_cmp_eq', decimal_ext.decimal_cmp_eq)
ll.add_symbol('decimal_cmp_ne', decimal_ext.decimal_cmp_ne)
ll.add_symbol('decimal_cmp_gt', decimal_ext.decimal_cmp_gt)
ll.add_symbol('decimal_cmp_ge', decimal_ext.decimal_cmp_ge)
ll.add_symbol('decimal_cmp_lt', decimal_ext.decimal_cmp_lt)
ll.add_symbol('decimal_cmp_le', decimal_ext.decimal_cmp_le)
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_str, is_iterable_type, is_list_like_index_type, is_overload_constant_int, is_overload_constant_str, is_overload_none
int128_type = types.Integer('int128', 128)


class Decimal128Type(types.Type):

    def __init__(self, precision, scale):
        assert isinstance(precision, int)
        assert isinstance(scale, int)
        super(Decimal128Type, self).__init__(name='Decimal128Type({}, {})'.
            format(precision, scale))
        self.precision = precision
        self.scale = scale
        self.bitwidth = 128


@typeof_impl.register(Decimal)
def typeof_decimal_value(val, c):
    return Decimal128Type(38, 18)


register_model(Decimal128Type)(models.IntegerModel)


@intrinsic
def int128_to_decimal128type(typingctx, val, precision_tp, scale_tp=None):
    assert val == int128_type
    assert is_overload_constant_int(precision_tp)
    assert is_overload_constant_int(scale_tp)

    def codegen(context, builder, signature, args):
        return args[0]
    precision = get_overload_const_int(precision_tp)
    scale = get_overload_const_int(scale_tp)
    return Decimal128Type(precision, scale)(int128_type, precision_tp, scale_tp
        ), codegen


@intrinsic
def decimal128type_to_int128(typingctx, val):
    assert isinstance(val, Decimal128Type)

    def codegen(context, builder, signature, args):
        return args[0]
    return int128_type(val), codegen


def decimal_to_str_codegen(context, builder, signature, args, scale):
    val, = args
    scale = context.get_constant(types.int32, scale)
    leu__pkza = cgutils.create_struct_proxy(types.unicode_type)(context,
        builder)
    lwwz__zbi = lir.FunctionType(lir.VoidType(), [lir.IntType(128), lir.
        IntType(8).as_pointer().as_pointer(), lir.IntType(64).as_pointer(),
        lir.IntType(32)])
    uwivx__teh = cgutils.get_or_insert_function(builder.module, lwwz__zbi,
        name='decimal_to_str')
    builder.call(uwivx__teh, [val, leu__pkza._get_ptr_by_name('meminfo'),
        leu__pkza._get_ptr_by_name('length'), scale])
    leu__pkza.kind = context.get_constant(types.int32, numba.cpython.
        unicode.PY_UNICODE_1BYTE_KIND)
    leu__pkza.is_ascii = context.get_constant(types.int32, 1)
    leu__pkza.hash = context.get_constant(numba.cpython.unicode._Py_hash_t, -1)
    leu__pkza.data = context.nrt.meminfo_data(builder, leu__pkza.meminfo)
    leu__pkza.parent = cgutils.get_null_value(leu__pkza.parent.type)
    return leu__pkza._getvalue()


@intrinsic
def decimal_to_str(typingctx, val_t=None):
    assert isinstance(val_t, Decimal128Type)

    def codegen(context, builder, signature, args):
        return decimal_to_str_codegen(context, builder, signature, args,
            val_t.scale)
    return bodo.string_type(val_t), codegen


def str_to_decimal_codegen(context, builder, signature, args):
    val, lul__nrah, lul__nrah = args
    val = bodo.libs.str_ext.gen_unicode_to_std_str(context, builder, val)
    lwwz__zbi = lir.FunctionType(lir.IntType(128), [lir.IntType(8).
        as_pointer()])
    uwivx__teh = cgutils.get_or_insert_function(builder.module, lwwz__zbi,
        name='str_to_decimal')
    xhgq__arkno = builder.call(uwivx__teh, [val])
    return xhgq__arkno


@intrinsic
def str_to_decimal(typingctx, val, precision_tp, scale_tp=None):
    assert val == bodo.string_type or is_overload_constant_str(val)
    assert is_overload_constant_int(precision_tp)
    assert is_overload_constant_int(scale_tp)

    def codegen(context, builder, signature, args):
        return str_to_decimal_codegen(context, builder, signature, args)
    precision = get_overload_const_int(precision_tp)
    scale = get_overload_const_int(scale_tp)
    return Decimal128Type(precision, scale)(val, precision_tp, scale_tp
        ), codegen


@overload(str, no_unliteral=True)
def overload_str_decimal(val):
    if isinstance(val, Decimal128Type):

        def impl(val):
            return decimal_to_str(val)
        return impl


@intrinsic
def decimal128type_to_int64_tuple(typingctx, val):
    assert isinstance(val, Decimal128Type)

    def codegen(context, builder, signature, args):
        uuqqo__dbggi = cgutils.alloca_once(builder, lir.ArrayType(lir.
            IntType(64), 2))
        builder.store(args[0], builder.bitcast(uuqqo__dbggi, lir.IntType(
            128).as_pointer()))
        return builder.load(uuqqo__dbggi)
    return types.UniTuple(types.int64, 2)(val), codegen


@intrinsic
def decimal128type_cmp(typingctx, val1, scale1, val2, scale2, func_name):
    assert is_overload_constant_str(func_name)
    znaha__ikyh = get_overload_const_str(func_name)

    def codegen(context, builder, signature, args):
        val1, scale1, val2, scale2, lul__nrah = args
        lwwz__zbi = lir.FunctionType(lir.IntType(1), [lir.IntType(128), lir
            .IntType(64), lir.IntType(128), lir.IntType(64)])
        uwivx__teh = cgutils.get_or_insert_function(builder.module,
            lwwz__zbi, name=znaha__ikyh)
        return builder.call(uwivx__teh, (val1, scale1, val2, scale2))
    return types.boolean(val1, scale1, val2, scale2, func_name), codegen


def decimal_create_cmp_op_overload(op):

    def overload_cmp(lhs, rhs):
        if isinstance(lhs, Decimal128Type) and isinstance(rhs, Decimal128Type):
            znaha__ikyh = 'decimal_cmp_' + op.__name__
            scale1 = lhs.scale
            scale2 = rhs.scale

            def impl(lhs, rhs):
                return decimal128type_cmp(lhs, scale1, rhs, scale2, znaha__ikyh
                    )
            return impl
    return overload_cmp


@lower_constant(Decimal128Type)
def lower_constant_decimal(context, builder, ty, pyval):
    cmqf__fthmq = numba.njit(lambda v: decimal128type_to_int64_tuple(v))(pyval)
    zhq__yyovk = [context.get_constant_generic(builder, types.int64, v) for
        v in cmqf__fthmq]
    zdjd__anoab = cgutils.pack_array(builder, zhq__yyovk)
    uuqqo__dbggi = cgutils.alloca_once(builder, lir.IntType(128))
    builder.store(zdjd__anoab, builder.bitcast(uuqqo__dbggi, lir.ArrayType(
        lir.IntType(64), 2).as_pointer()))
    return builder.load(uuqqo__dbggi)


@overload(Decimal, no_unliteral=True)
def decimal_constructor_overload(value='0', context=None):
    if not is_overload_none(context):
        raise BodoError('decimal.Decimal() context argument not supported yet')
    if isinstance(value, (types.Integer,)) or is_overload_constant_str(value
        ) or value == bodo.string_type:

        def impl(value='0', context=None):
            return str_to_decimal(str(value), 38, 18)
        return impl
    else:
        raise BodoError(
            'decimal.Decimal() value type must be an integer or string')


@overload(bool, no_unliteral=True)
def decimal_to_bool(dec):
    if not isinstance(dec, Decimal128Type):
        return

    def impl(dec):
        return bool(decimal128type_to_int128(dec))
    return impl


@unbox(Decimal128Type)
def unbox_decimal(typ, val, c):
    lwwz__zbi = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(128).as_pointer()])
    uwivx__teh = cgutils.get_or_insert_function(c.builder.module, lwwz__zbi,
        name='unbox_decimal')
    uuqqo__dbggi = cgutils.alloca_once(c.builder, c.context.get_value_type(
        int128_type))
    c.builder.call(uwivx__teh, [val, uuqqo__dbggi])
    qfe__girs = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    kle__mggnf = c.builder.load(uuqqo__dbggi)
    return NativeValue(kle__mggnf, is_error=qfe__girs)


@box(Decimal128Type)
def box_decimal(typ, val, c):
    uyva__istfv = decimal_to_str_codegen(c.context, c.builder, bodo.
        string_type(typ), (val,), typ.scale)
    oif__vbnk = c.pyapi.from_native_value(bodo.string_type, uyva__istfv, c.
        env_manager)
    boww__gmvu = c.context.insert_const_string(c.builder.module, 'decimal')
    gvs__syg = c.pyapi.import_module_noblock(boww__gmvu)
    uuqqo__dbggi = c.pyapi.call_method(gvs__syg, 'Decimal', (oif__vbnk,))
    c.pyapi.decref(oif__vbnk)
    c.pyapi.decref(gvs__syg)
    return uuqqo__dbggi


@overload_method(Decimal128Type, '__hash__', no_unliteral=True)
def decimal_hash(val):

    def impl(val):
        return hash(decimal_to_str(val))
    return impl


class DecimalArrayType(types.ArrayCompatible):

    def __init__(self, precision, scale):
        self.precision = precision
        self.scale = scale
        super(DecimalArrayType, self).__init__(name=
            'DecimalArrayType({}, {})'.format(precision, scale))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return DecimalArrayType(self.precision, self.scale)

    @property
    def dtype(self):
        return Decimal128Type(self.precision, self.scale)


data_type = types.Array(int128_type, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(DecimalArrayType)
class DecimalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pydnz__snzd = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, pydnz__snzd)


make_attribute_wrapper(DecimalArrayType, 'data', '_data')
make_attribute_wrapper(DecimalArrayType, 'null_bitmap', '_null_bitmap')


@intrinsic
def init_decimal_array(typingctx, data, null_bitmap, precision_tp, scale_tp
    =None):
    assert data == types.Array(int128_type, 1, 'C')
    assert null_bitmap == types.Array(types.uint8, 1, 'C')
    assert is_overload_constant_int(precision_tp)
    assert is_overload_constant_int(scale_tp)

    def codegen(context, builder, signature, args):
        czik__ytim, qeexq__yhn, lul__nrah, lul__nrah = args
        aym__jzdu = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        aym__jzdu.data = czik__ytim
        aym__jzdu.null_bitmap = qeexq__yhn
        context.nrt.incref(builder, signature.args[0], czik__ytim)
        context.nrt.incref(builder, signature.args[1], qeexq__yhn)
        return aym__jzdu._getvalue()
    precision = get_overload_const_int(precision_tp)
    scale = get_overload_const_int(scale_tp)
    tsfkt__cppw = DecimalArrayType(precision, scale)
    vpeye__ahsv = tsfkt__cppw(data, null_bitmap, precision_tp, scale_tp)
    return vpeye__ahsv, codegen


@lower_constant(DecimalArrayType)
def lower_constant_decimal_arr(context, builder, typ, pyval):
    n = len(pyval)
    gicp__mqeu = context.get_constant(types.int64, n)
    vob__zmbhi = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(int128_type, 1, 'C'), [gicp__mqeu])
    loz__spy = np.empty(n + 7 >> 3, np.uint8)

    def f(arr, idx, val):
        arr[idx] = decimal128type_to_int128(val)
    for acm__kmo, rymvu__qdph in enumerate(pyval):
        ipgv__uvvg = pd.isna(rymvu__qdph)
        bodo.libs.int_arr_ext.set_bit_to_arr(loz__spy, acm__kmo, int(not
            ipgv__uvvg))
        if not ipgv__uvvg:
            context.compile_internal(builder, f, types.void(types.Array(
                int128_type, 1, 'C'), types.int64, Decimal128Type(typ.
                precision, typ.scale)), [vob__zmbhi._getvalue(), context.
                get_constant(types.int64, acm__kmo), context.
                get_constant_generic(builder, Decimal128Type(typ.precision,
                typ.scale), rymvu__qdph)])
    nqxg__idh = context.get_constant_generic(builder, nulls_type, loz__spy)
    aym__jzdu = context.make_helper(builder, typ)
    aym__jzdu.data = vob__zmbhi._getvalue()
    aym__jzdu.null_bitmap = nqxg__idh
    return aym__jzdu._getvalue()


@numba.njit(no_cpython_wrapper=True)
def alloc_decimal_array(n, precision, scale):
    itx__nvnc = np.empty(n, dtype=int128_type)
    isw__xkho = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_decimal_array(itx__nvnc, isw__xkho, precision, scale)


def alloc_decimal_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_decimal_arr_ext_alloc_decimal_array
    ) = alloc_decimal_array_equiv


@box(DecimalArrayType)
def box_decimal_arr(typ, val, c):
    blcr__smj = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    itx__nvnc = c.context.make_array(types.Array(int128_type, 1, 'C'))(c.
        context, c.builder, blcr__smj.data)
    pviaq__fjajm = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, blcr__smj.null_bitmap).data
    n = c.builder.extract_value(itx__nvnc.shape, 0)
    scale = c.context.get_constant(types.int32, typ.scale)
    lwwz__zbi = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(128).as_pointer(), lir.IntType(8).as_pointer(), lir.IntType
        (32)])
    xttrw__saqq = cgutils.get_or_insert_function(c.builder.module,
        lwwz__zbi, name='box_decimal_array')
    caloq__tkwl = c.builder.call(xttrw__saqq, [n, itx__nvnc.data,
        pviaq__fjajm, scale])
    c.context.nrt.decref(c.builder, typ, val)
    return caloq__tkwl


@unbox(DecimalArrayType)
def unbox_decimal_arr(typ, val, c):
    aym__jzdu = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    easo__gxfa = c.pyapi.call_method(val, '__len__', ())
    n = c.pyapi.long_as_longlong(easo__gxfa)
    c.pyapi.decref(easo__gxfa)
    spw__vhvu = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64
        ), 7)), lir.Constant(lir.IntType(64), 8))
    vob__zmbhi = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(int128_type, 1, 'C'), [n])
    ruo__aolar = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [spw__vhvu])
    lwwz__zbi = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(64), lir.IntType(128).as_pointer(), lir.IntType(8).
        as_pointer()])
    uwivx__teh = cgutils.get_or_insert_function(c.builder.module, lwwz__zbi,
        name='unbox_decimal_array')
    c.builder.call(uwivx__teh, [val, n, vob__zmbhi.data, ruo__aolar.data])
    aym__jzdu.null_bitmap = ruo__aolar._getvalue()
    aym__jzdu.data = vob__zmbhi._getvalue()
    qfe__girs = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(aym__jzdu._getvalue(), is_error=qfe__girs)


@overload_method(DecimalArrayType, 'copy', no_unliteral=True)
def overload_decimal_arr_copy(A):
    precision = A.precision
    scale = A.scale
    return lambda A: bodo.libs.decimal_arr_ext.init_decimal_array(A._data.
        copy(), A._null_bitmap.copy(), precision, scale)


@overload(len, no_unliteral=True)
def overload_decimal_arr_len(A):
    if isinstance(A, DecimalArrayType):
        return lambda A: len(A._data)


@overload_attribute(DecimalArrayType, 'shape')
def overload_decimal_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(DecimalArrayType, 'dtype')
def overload_decimal_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(DecimalArrayType, 'ndim')
def overload_decimal_arr_ndim(A):
    return lambda A: 1


@overload_attribute(DecimalArrayType, 'nbytes')
def decimal_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload(operator.setitem, no_unliteral=True)
def decimal_arr_setitem(A, idx, val):
    if not isinstance(A, DecimalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    ccj__oess = (
        f"setitem for DecimalArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if isinstance(val, Decimal128Type):

            def impl_scalar(A, idx, val):
                A._data[idx] = decimal128type_to_int128(val)
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(ccj__oess)
    if not (is_iterable_type(val) and isinstance(val.dtype, bodo.
        Decimal128Type) or isinstance(val, Decimal128Type)):
        raise BodoError(ccj__oess)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):
        if isinstance(val, Decimal128Type):
            return lambda A, idx, val: array_setitem_int_index(A, idx,
                decimal128type_to_int128(val))

        def impl_arr_ind_mask(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind_mask
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if isinstance(val, Decimal128Type):
            return lambda A, idx, val: array_setitem_bool_index(A, idx,
                decimal128type_to_int128(val))

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):
        if isinstance(val, Decimal128Type):
            return lambda A, idx, val: array_setitem_slice_index(A, idx,
                decimal128type_to_int128(val))

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for DecimalArray with indexing type {idx} not supported.')


@overload(operator.getitem, no_unliteral=True)
def decimal_arr_getitem(A, ind):
    if not isinstance(A, DecimalArrayType):
        return
    if isinstance(ind, types.Integer):
        precision = A.precision
        scale = A.scale
        return lambda A, ind: int128_to_decimal128type(A._data[ind],
            precision, scale)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        precision = A.precision
        scale = A.scale

        def impl(A, ind):
            zpuuf__ljib, dcjas__uop = array_getitem_bool_index(A, ind)
            return init_decimal_array(zpuuf__ljib, dcjas__uop, precision, scale
                )
        return impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        precision = A.precision
        scale = A.scale

        def impl(A, ind):
            zpuuf__ljib, dcjas__uop = array_getitem_int_index(A, ind)
            return init_decimal_array(zpuuf__ljib, dcjas__uop, precision, scale
                )
        return impl
    if isinstance(ind, types.SliceType):
        precision = A.precision
        scale = A.scale

        def impl_slice(A, ind):
            zpuuf__ljib, dcjas__uop = array_getitem_slice_index(A, ind)
            return init_decimal_array(zpuuf__ljib, dcjas__uop, precision, scale
                )
        return impl_slice
    raise BodoError(
        f'getitem for DecimalArray with indexing type {ind} not supported.')
