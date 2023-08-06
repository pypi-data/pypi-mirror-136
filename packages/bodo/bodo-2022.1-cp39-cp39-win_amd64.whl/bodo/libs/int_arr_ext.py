"""Nullable integer array corresponding to Pandas IntegerArray.
However, nulls are stored in bit arrays similar to Arrow's arrays.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs.str_arr_ext import kBitmask
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('mask_arr_to_bitmap', hstr_ext.mask_arr_to_bitmap)
ll.add_symbol('is_pd_int_array', array_ext.is_pd_int_array)
ll.add_symbol('int_array_from_sequence', array_ext.int_array_from_sequence)
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, check_unsupported_args, is_iterable_type, is_list_like_index_type, is_overload_false, is_overload_none, is_overload_true, parse_dtype, raise_bodo_error, to_nullable_type


class IntegerArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(IntegerArrayType, self).__init__(name='IntegerArrayType({})'.
            format(dtype))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntegerArrayType(self.dtype)


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        kwchr__kpask = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, kwchr__kpask)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    kxajc__lamt = 8 * val.dtype.itemsize
    nfov__scbcw = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(nfov__scbcw, kxajc__lamt))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        wget__wabxu = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(wget__wabxu)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    oiae__ldhn = c.context.insert_const_string(c.builder.module, 'pandas')
    jnnll__lku = c.pyapi.import_module_noblock(oiae__ldhn)
    njkg__tye = c.pyapi.call_method(jnnll__lku, str(typ)[:-2], ())
    c.pyapi.decref(jnnll__lku)
    return njkg__tye


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    kxajc__lamt = 8 * val.itemsize
    nfov__scbcw = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(nfov__scbcw, kxajc__lamt))
    return IntDtype(dtype)


def _register_int_dtype(t):
    typeof_impl.register(t)(typeof_pd_int_dtype)
    int_dtype = typeof_pd_int_dtype(t(), None)
    type_callable(t)(lambda c: lambda : int_dtype)
    lower_builtin(t)(lambda c, b, s, a: c.get_dummy_value())


pd_int_dtype_classes = (pd.Int8Dtype, pd.Int16Dtype, pd.Int32Dtype, pd.
    Int64Dtype, pd.UInt8Dtype, pd.UInt16Dtype, pd.UInt32Dtype, pd.UInt64Dtype)
for t in pd_int_dtype_classes:
    _register_int_dtype(t)


@numba.extending.register_jitable
def mask_arr_to_bitmap(mask_arr):
    n = len(mask_arr)
    ysfog__uena = n + 7 >> 3
    nmjnd__apal = np.empty(ysfog__uena, np.uint8)
    for i in range(n):
        aueco__bjyi = i // 8
        nmjnd__apal[aueco__bjyi] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            nmjnd__apal[aueco__bjyi]) & kBitmask[i % 8]
    return nmjnd__apal


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    rvvl__mka = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(rvvl__mka)
    c.pyapi.decref(rvvl__mka)
    cytm__fpcqk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ysfog__uena = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    oxctu__dcf = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [ysfog__uena])
    kfhld__vbmu = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    sco__ucib = cgutils.get_or_insert_function(c.builder.module,
        kfhld__vbmu, name='is_pd_int_array')
    iits__invp = c.builder.call(sco__ucib, [obj])
    lhhhv__zopdp = c.builder.icmp_unsigned('!=', iits__invp, iits__invp.type(0)
        )
    with c.builder.if_else(lhhhv__zopdp) as (pd_then, pd_otherwise):
        with pd_then:
            cyiwu__qew = c.pyapi.object_getattr_string(obj, '_data')
            cytm__fpcqk.data = c.pyapi.to_native_value(types.Array(typ.
                dtype, 1, 'C'), cyiwu__qew).value
            sniqd__dcequ = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), sniqd__dcequ).value
            c.pyapi.decref(cyiwu__qew)
            c.pyapi.decref(sniqd__dcequ)
            kdmu__qhkoq = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, mask_arr)
            kfhld__vbmu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            sco__ucib = cgutils.get_or_insert_function(c.builder.module,
                kfhld__vbmu, name='mask_arr_to_bitmap')
            c.builder.call(sco__ucib, [oxctu__dcf.data, kdmu__qhkoq.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with pd_otherwise:
            ckf__iabh = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            kfhld__vbmu = lir.FunctionType(lir.IntType(32), [lir.IntType(8)
                .as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            ime__bvvze = cgutils.get_or_insert_function(c.builder.module,
                kfhld__vbmu, name='int_array_from_sequence')
            c.builder.call(ime__bvvze, [obj, c.builder.bitcast(ckf__iabh.
                data, lir.IntType(8).as_pointer()), oxctu__dcf.data])
            cytm__fpcqk.data = ckf__iabh._getvalue()
    cytm__fpcqk.null_bitmap = oxctu__dcf._getvalue()
    yac__bwwzr = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cytm__fpcqk._getvalue(), is_error=yac__bwwzr)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    cytm__fpcqk = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        cytm__fpcqk.data, c.env_manager)
    fbwj__rric = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, cytm__fpcqk.null_bitmap).data
    rvvl__mka = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(rvvl__mka)
    oiae__ldhn = c.context.insert_const_string(c.builder.module, 'numpy')
    qzzs__ali = c.pyapi.import_module_noblock(oiae__ldhn)
    tsd__hjmww = c.pyapi.object_getattr_string(qzzs__ali, 'bool_')
    mask_arr = c.pyapi.call_method(qzzs__ali, 'empty', (rvvl__mka, tsd__hjmww))
    fpya__yvjkx = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    tzgvk__fygz = c.pyapi.object_getattr_string(fpya__yvjkx, 'data')
    qhy__bmrmg = c.builder.inttoptr(c.pyapi.long_as_longlong(tzgvk__fygz),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as loop:
        i = loop.index
        nunp__rif = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        pziey__svgw = c.builder.load(cgutils.gep(c.builder, fbwj__rric,
            nunp__rif))
        pgmj__qkota = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(pziey__svgw, pgmj__qkota), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        awwq__vcv = cgutils.gep(c.builder, qhy__bmrmg, i)
        c.builder.store(val, awwq__vcv)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        cytm__fpcqk.null_bitmap)
    oiae__ldhn = c.context.insert_const_string(c.builder.module, 'pandas')
    jnnll__lku = c.pyapi.import_module_noblock(oiae__ldhn)
    wani__mvhog = c.pyapi.object_getattr_string(jnnll__lku, 'arrays')
    njkg__tye = c.pyapi.call_method(wani__mvhog, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(jnnll__lku)
    c.pyapi.decref(rvvl__mka)
    c.pyapi.decref(qzzs__ali)
    c.pyapi.decref(tsd__hjmww)
    c.pyapi.decref(fpya__yvjkx)
    c.pyapi.decref(tzgvk__fygz)
    c.pyapi.decref(wani__mvhog)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return njkg__tye


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        ring__spj, gtt__djezr = args
        cytm__fpcqk = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        cytm__fpcqk.data = ring__spj
        cytm__fpcqk.null_bitmap = gtt__djezr
        context.nrt.incref(builder, signature.args[0], ring__spj)
        context.nrt.incref(builder, signature.args[1], gtt__djezr)
        return cytm__fpcqk._getvalue()
    lbwj__dqayh = IntegerArrayType(data.dtype)
    hper__mdio = lbwj__dqayh(data, null_bitmap)
    return hper__mdio, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    pysgk__tsetx = np.empty(n, pyval.dtype.type)
    yaoy__uuli = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        mpo__yzact = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(yaoy__uuli, i, int(not mpo__yzact)
            )
        if not mpo__yzact:
            pysgk__tsetx[i] = s
    bmju__vkxwi = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), pysgk__tsetx)
    qcf__lthy = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), yaoy__uuli)
    return lir.Constant.literal_struct([bmju__vkxwi, qcf__lthy])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    vfqh__qei = args[0]
    if equiv_set.has_shape(vfqh__qei):
        return ArrayAnalysis.AnalyzeResult(shape=vfqh__qei, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    vfqh__qei = args[0]
    if equiv_set.has_shape(vfqh__qei):
        return ArrayAnalysis.AnalyzeResult(shape=vfqh__qei, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_init_integer_array = (
    init_integer_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_integer_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_integer_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_integer_array
numba.core.ir_utils.alias_func_extensions['get_int_arr_data',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_int_arr_bitmap',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_int_array(n, dtype):
    pysgk__tsetx = np.empty(n, dtype)
    hmym__rax = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(pysgk__tsetx, hmym__rax)


def alloc_int_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_alloc_int_array = (
    alloc_int_array_equiv)


@numba.extending.register_jitable
def set_bit_to_arr(bits, i, bit_is_set):
    bits[i // 8] ^= np.uint8(-np.uint8(bit_is_set) ^ bits[i // 8]) & kBitmask[
        i % 8]


@numba.extending.register_jitable
def get_bit_bitmap_arr(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@overload(operator.getitem, no_unliteral=True)
def int_arr_getitem(A, ind):
    if not isinstance(A, IntegerArrayType):
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            wdqtj__btgc, sxer__nyj = array_getitem_bool_index(A, ind)
            return init_integer_array(wdqtj__btgc, sxer__nyj)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            wdqtj__btgc, sxer__nyj = array_getitem_int_index(A, ind)
            return init_integer_array(wdqtj__btgc, sxer__nyj)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            wdqtj__btgc, sxer__nyj = array_getitem_slice_index(A, ind)
            return init_integer_array(wdqtj__btgc, sxer__nyj)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    eptza__jmyzl = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    exy__dgi = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if exy__dgi:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(eptza__jmyzl)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or exy__dgi):
        raise BodoError(eptza__jmyzl)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):

        def impl_arr_ind_mask(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind_mask
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for IntegerArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_int_arr_len(A):
    if isinstance(A, IntegerArrayType):
        return lambda A: len(A._data)


@overload_attribute(IntegerArrayType, 'shape')
def overload_int_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(IntegerArrayType, 'dtype')
def overload_int_arr_dtype(A):
    dtype_class = getattr(pd, '{}Int{}Dtype'.format('' if A.dtype.signed else
        'U', A.dtype.bitwidth))
    return lambda A: dtype_class()


@overload_attribute(IntegerArrayType, 'ndim')
def overload_int_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntegerArrayType, 'nbytes')
def int_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(IntegerArrayType, 'copy', no_unliteral=True)
def overload_int_arr_copy(A, dtype=None):
    if not is_overload_none(dtype):
        return lambda A, dtype=None: A.astype(dtype, copy=True)
    else:
        return lambda A, dtype=None: bodo.libs.int_arr_ext.init_integer_array(
            bodo.libs.int_arr_ext.get_int_arr_data(A).copy(), bodo.libs.
            int_arr_ext.get_int_arr_bitmap(A).copy())


@overload_method(IntegerArrayType, 'astype', no_unliteral=True)
def overload_int_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "IntegerArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.NumberClass):
        dtype = dtype.dtype
    if isinstance(dtype, IntDtype) and A.dtype == dtype.dtype:
        if is_overload_false(copy):
            return lambda A, dtype, copy=True: A
        elif is_overload_true(copy):
            return lambda A, dtype, copy=True: A.copy()
        else:

            def impl(A, dtype, copy=True):
                if copy:
                    return A.copy()
                else:
                    return A
            return impl
    if isinstance(dtype, IntDtype):
        np_dtype = dtype.dtype
        return (lambda A, dtype, copy=True: bodo.libs.int_arr_ext.
            init_integer_array(bodo.libs.int_arr_ext.get_int_arr_data(A).
            astype(np_dtype), bodo.libs.int_arr_ext.get_int_arr_bitmap(A).
            copy()))
    nb_dtype = parse_dtype(dtype, 'IntegerArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.int_arr_ext.get_int_arr_data(A)
            n = len(data)
            whjf__ojbd = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                whjf__ojbd[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    whjf__ojbd[i] = np.nan
            return whjf__ojbd
        return impl_float
    return lambda A, dtype, copy=True: bodo.libs.int_arr_ext.get_int_arr_data(A
        ).astype(nb_dtype)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def apply_null_mask(arr, bitmap, mask_fill, inplace):
    assert isinstance(arr, types.Array)
    if isinstance(arr.dtype, types.Integer):
        if is_overload_none(inplace):
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap.copy()))
        else:
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap))
    if isinstance(arr.dtype, types.Float):

        def impl(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = np.nan
            return arr
        return impl
    if arr.dtype == types.bool_:

        def impl_bool(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = mask_fill
            return arr
        return impl_bool
    return lambda arr, bitmap, mask_fill, inplace: arr


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def merge_bitmaps(B1, B2, n, inplace):
    assert B1 == types.Array(types.uint8, 1, 'C')
    assert B2 == types.Array(types.uint8, 1, 'C')
    if not is_overload_none(inplace):

        def impl_inplace(B1, B2, n, inplace):
            for i in numba.parfors.parfor.internal_prange(n):
                nzsi__ioqv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                yax__sznu = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                wwqrg__oej = nzsi__ioqv & yax__sznu
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, wwqrg__oej)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        ysfog__uena = n + 7 >> 3
        whjf__ojbd = np.empty(ysfog__uena, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            nzsi__ioqv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            yax__sznu = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            wwqrg__oej = nzsi__ioqv & yax__sznu
            bodo.libs.int_arr_ext.set_bit_to_arr(whjf__ojbd, i, wwqrg__oej)
        return whjf__ojbd
    return impl


ufunc_aliases = {'subtract': 'sub', 'multiply': 'mul', 'floor_divide':
    'floordiv', 'true_divide': 'truediv', 'power': 'pow', 'remainder':
    'mod', 'divide': 'div', 'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    if n_inputs == 1:

        def overload_int_arr_op_nin_1(A):
            if isinstance(A, IntegerArrayType):
                return get_nullable_array_unary_impl(op, A)
        return overload_int_arr_op_nin_1
    elif n_inputs == 2:

        def overload_series_op_nin_2(lhs, rhs):
            if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
                IntegerArrayType):
                return get_nullable_array_binary_impl(op, lhs, rhs)
        return overload_series_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ial__nvpik in numba.np.ufunc_db.get_ufuncs():
        xudcl__ptr = create_op_overload(ial__nvpik, ial__nvpik.nin)
        overload(ial__nvpik, no_unliteral=True)(xudcl__ptr)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        xudcl__ptr = create_op_overload(op, 2)
        overload(op)(xudcl__ptr)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        xudcl__ptr = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(xudcl__ptr)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        xudcl__ptr = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(xudcl__ptr)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    lgrou__uiyo = len(arrs.types)
    qxp__kwz = 'def f(arrs):\n'
    njkg__tye = ', '.join('arrs[{}]._data'.format(i) for i in range(
        lgrou__uiyo))
    qxp__kwz += '  return ({}{})\n'.format(njkg__tye, ',' if lgrou__uiyo ==
        1 else '')
    qgmw__kvvvz = {}
    exec(qxp__kwz, {}, qgmw__kvvvz)
    impl = qgmw__kvvvz['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    lgrou__uiyo = len(arrs.types)
    jig__gzv = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        lgrou__uiyo))
    qxp__kwz = 'def f(arrs):\n'
    qxp__kwz += '  n = {}\n'.format(jig__gzv)
    qxp__kwz += '  n_bytes = (n + 7) >> 3\n'
    qxp__kwz += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    qxp__kwz += '  curr_bit = 0\n'
    for i in range(lgrou__uiyo):
        qxp__kwz += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        qxp__kwz += '  for j in range(len(arrs[{}])):\n'.format(i)
        qxp__kwz += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        qxp__kwz += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        qxp__kwz += '    curr_bit += 1\n'
    qxp__kwz += '  return new_mask\n'
    qgmw__kvvvz = {}
    exec(qxp__kwz, {'np': np, 'bodo': bodo}, qgmw__kvvvz)
    impl = qgmw__kvvvz['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    goxvw__xtj = dict(skipna=skipna, min_count=min_count)
    llos__kxzj = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', goxvw__xtj, llos__kxzj)

    def impl(A, skipna=True, min_count=0):
        numba.parfors.parfor.init_prange()
        s = 0
        for i in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, i):
                val = A[i]
            s += val
        return s
    return impl


@overload_method(IntegerArrayType, 'unique', no_unliteral=True)
def overload_unique(A):
    dtype = A.dtype

    def impl_int_arr(A):
        data = []
        pgmj__qkota = []
        dyr__nxbre = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not dyr__nxbre:
                    data.append(dtype(1))
                    pgmj__qkota.append(False)
                    dyr__nxbre = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                pgmj__qkota.append(True)
        wdqtj__btgc = np.array(data)
        n = len(wdqtj__btgc)
        ysfog__uena = n + 7 >> 3
        sxer__nyj = np.empty(ysfog__uena, np.uint8)
        for mhurz__tiqmf in range(n):
            set_bit_to_arr(sxer__nyj, mhurz__tiqmf, pgmj__qkota[mhurz__tiqmf])
        return init_integer_array(wdqtj__btgc, sxer__nyj)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    wnz__mhap = numba.core.registry.cpu_target.typing_context
    rqihi__mwgjr = wnz__mhap.resolve_function_type(op, (types.Array(A.dtype,
        1, 'C'),), {}).return_type
    rqihi__mwgjr = to_nullable_type(rqihi__mwgjr)

    def impl(A):
        n = len(A)
        zntcb__ypu = bodo.utils.utils.alloc_type(n, rqihi__mwgjr, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(zntcb__ypu, i)
                continue
            zntcb__ypu[i] = op(A[i])
        return zntcb__ypu
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    msun__hbnu = isinstance(lhs, (types.Number, types.Boolean))
    anyx__orms = isinstance(rhs, (types.Number, types.Boolean))
    itwii__xrc = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    wul__outev = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    wnz__mhap = numba.core.registry.cpu_target.typing_context
    rqihi__mwgjr = wnz__mhap.resolve_function_type(op, (itwii__xrc,
        wul__outev), {}).return_type
    rqihi__mwgjr = to_nullable_type(rqihi__mwgjr)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    dtgso__dqod = 'lhs' if msun__hbnu else 'lhs[i]'
    smi__rbdg = 'rhs' if anyx__orms else 'rhs[i]'
    oxtiw__psr = ('False' if msun__hbnu else
        'bodo.libs.array_kernels.isna(lhs, i)')
    dezk__adcyk = ('False' if anyx__orms else
        'bodo.libs.array_kernels.isna(rhs, i)')
    qxp__kwz = 'def impl(lhs, rhs):\n'
    qxp__kwz += '  n = len({})\n'.format('lhs' if not msun__hbnu else 'rhs')
    if inplace:
        qxp__kwz += '  out_arr = {}\n'.format('lhs' if not msun__hbnu else
            'rhs')
    else:
        qxp__kwz += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    qxp__kwz += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    qxp__kwz += '    if ({}\n'.format(oxtiw__psr)
    qxp__kwz += '        or {}):\n'.format(dezk__adcyk)
    qxp__kwz += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    qxp__kwz += '      continue\n'
    qxp__kwz += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(dtgso__dqod, smi__rbdg))
    qxp__kwz += '  return out_arr\n'
    qgmw__kvvvz = {}
    exec(qxp__kwz, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        rqihi__mwgjr, 'op': op}, qgmw__kvvvz)
    impl = qgmw__kvvvz['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        msun__hbnu = lhs in [pd_timedelta_type]
        anyx__orms = rhs in [pd_timedelta_type]
        if msun__hbnu:

            def impl(lhs, rhs):
                n = len(rhs)
                zntcb__ypu = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(zntcb__ypu, i)
                        continue
                    zntcb__ypu[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs, rhs[i]))
                return zntcb__ypu
            return impl
        elif anyx__orms:

            def impl(lhs, rhs):
                n = len(lhs)
                zntcb__ypu = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(zntcb__ypu, i)
                        continue
                    zntcb__ypu[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs[i], rhs))
                return zntcb__ypu
            return impl
    return impl
