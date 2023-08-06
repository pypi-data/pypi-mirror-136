"""Nullable boolean array that stores data in Numpy format (1 byte per value)
but nulls are stored in bit arrays (1 bit per value) similar to Arrow's nulls.
Pandas converts boolean array to object when NAs are introduced.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import NativeValue, box, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.libs.str_arr_ext import string_array_type
from bodo.utils.typing import is_list_like_index_type
ll.add_symbol('is_bool_array', hstr_ext.is_bool_array)
ll.add_symbol('is_pd_boolean_array', hstr_ext.is_pd_boolean_array)
ll.add_symbol('unbox_bool_array_obj', hstr_ext.unbox_bool_array_obj)
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, is_iterable_type, is_overload_false, is_overload_true, parse_dtype, raise_bodo_error


class BooleanArrayType(types.ArrayCompatible):

    def __init__(self):
        super(BooleanArrayType, self).__init__(name='BooleanArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.bool_

    def copy(self):
        return BooleanArrayType()


boolean_array = BooleanArrayType()


@typeof_impl.register(pd.arrays.BooleanArray)
def typeof_boolean_array(val, c):
    return boolean_array


data_type = types.Array(types.bool_, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(BooleanArrayType)
class BooleanArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        blsvm__fys = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, blsvm__fys)


make_attribute_wrapper(BooleanArrayType, 'data', '_data')
make_attribute_wrapper(BooleanArrayType, 'null_bitmap', '_null_bitmap')


class BooleanDtype(types.Number):

    def __init__(self):
        self.dtype = types.bool_
        super(BooleanDtype, self).__init__('BooleanDtype')


boolean_dtype = BooleanDtype()
register_model(BooleanDtype)(models.OpaqueModel)


@box(BooleanDtype)
def box_boolean_dtype(typ, val, c):
    rzinq__toqr = c.context.insert_const_string(c.builder.module, 'pandas')
    aweq__kyar = c.pyapi.import_module_noblock(rzinq__toqr)
    ugj__dxipz = c.pyapi.call_method(aweq__kyar, 'BooleanDtype', ())
    c.pyapi.decref(aweq__kyar)
    return ugj__dxipz


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    dvjx__ccb = n + 7 >> 3
    return np.full(dvjx__ccb, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    qvtem__wdpf = c.context.typing_context.resolve_value_type(func)
    rgz__jsa = qvtem__wdpf.get_call_type(c.context.typing_context, arg_typs, {}
        )
    whbhf__psnd = c.context.get_function(qvtem__wdpf, rgz__jsa)
    sgb__qgk = c.context.call_conv.get_function_type(rgz__jsa.return_type,
        rgz__jsa.args)
    ubdx__etuse = c.builder.module
    uaiy__ktk = lir.Function(ubdx__etuse, sgb__qgk, name=ubdx__etuse.
        get_unique_name('.func_conv'))
    uaiy__ktk.linkage = 'internal'
    jua__kddxy = lir.IRBuilder(uaiy__ktk.append_basic_block())
    ftjcv__yrva = c.context.call_conv.decode_arguments(jua__kddxy, rgz__jsa
        .args, uaiy__ktk)
    eqps__iitkw = whbhf__psnd(jua__kddxy, ftjcv__yrva)
    c.context.call_conv.return_value(jua__kddxy, eqps__iitkw)
    grd__zvhpf, aswp__qai = c.context.call_conv.call_function(c.builder,
        uaiy__ktk, rgz__jsa.return_type, rgz__jsa.args, args)
    return aswp__qai


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    ief__njgt = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(ief__njgt)
    c.pyapi.decref(ief__njgt)
    sgb__qgk = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()])
    seva__delty = cgutils.get_or_insert_function(c.builder.module, sgb__qgk,
        name='is_bool_array')
    sgb__qgk = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()])
    uaiy__ktk = cgutils.get_or_insert_function(c.builder.module, sgb__qgk,
        name='is_pd_boolean_array')
    emuye__dzv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xidyd__zfq = c.builder.call(uaiy__ktk, [obj])
    nxfef__iuv = c.builder.icmp_unsigned('!=', xidyd__zfq, xidyd__zfq.type(0))
    with c.builder.if_else(nxfef__iuv) as (pd_then, pd_otherwise):
        with pd_then:
            bfql__qunu = c.pyapi.object_getattr_string(obj, '_data')
            emuye__dzv.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), bfql__qunu).value
            msmeq__mbpa = c.pyapi.object_getattr_string(obj, '_mask')
            xzkfn__nhcev = c.pyapi.to_native_value(types.Array(types.bool_,
                1, 'C'), msmeq__mbpa).value
            dvjx__ccb = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            njul__rre = c.context.make_array(types.Array(types.bool_, 1, 'C'))(
                c.context, c.builder, xzkfn__nhcev)
            oao__kuuj = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [dvjx__ccb])
            sgb__qgk = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            uaiy__ktk = cgutils.get_or_insert_function(c.builder.module,
                sgb__qgk, name='mask_arr_to_bitmap')
            c.builder.call(uaiy__ktk, [oao__kuuj.data, njul__rre.data, n])
            emuye__dzv.null_bitmap = oao__kuuj._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), xzkfn__nhcev)
            c.pyapi.decref(bfql__qunu)
            c.pyapi.decref(msmeq__mbpa)
        with pd_otherwise:
            ebh__azsr = c.builder.call(seva__delty, [obj])
            fombn__hsswv = c.builder.icmp_unsigned('!=', ebh__azsr,
                ebh__azsr.type(0))
            with c.builder.if_else(fombn__hsswv) as (then, otherwise):
                with then:
                    emuye__dzv.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    emuye__dzv.null_bitmap = call_func_in_unbox(gen_full_bitmap
                        , (n,), (types.int64,), c)
                with otherwise:
                    emuye__dzv.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    dvjx__ccb = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    emuye__dzv.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [dvjx__ccb])._getvalue()
                    gpord__cqjtv = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, emuye__dzv.data
                        ).data
                    fzis__pvjf = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, emuye__dzv.
                        null_bitmap).data
                    sgb__qgk = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    uaiy__ktk = cgutils.get_or_insert_function(c.builder.
                        module, sgb__qgk, name='unbox_bool_array_obj')
                    c.builder.call(uaiy__ktk, [obj, gpord__cqjtv,
                        fzis__pvjf, n])
    return NativeValue(emuye__dzv._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    emuye__dzv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        emuye__dzv.data, c.env_manager)
    kolb__jryoz = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, emuye__dzv.null_bitmap).data
    ief__njgt = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(ief__njgt)
    rzinq__toqr = c.context.insert_const_string(c.builder.module, 'numpy')
    jwn__jvba = c.pyapi.import_module_noblock(rzinq__toqr)
    ezen__ogkfg = c.pyapi.object_getattr_string(jwn__jvba, 'bool_')
    xzkfn__nhcev = c.pyapi.call_method(jwn__jvba, 'empty', (ief__njgt,
        ezen__ogkfg))
    rmzeg__nfp = c.pyapi.object_getattr_string(xzkfn__nhcev, 'ctypes')
    sfem__ypn = c.pyapi.object_getattr_string(rmzeg__nfp, 'data')
    blkd__nmyny = c.builder.inttoptr(c.pyapi.long_as_longlong(sfem__ypn),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as loop:
        nmj__qcy = loop.index
        pofd__iihj = c.builder.lshr(nmj__qcy, lir.Constant(lir.IntType(64), 3))
        zppjr__bzsps = c.builder.load(cgutils.gep(c.builder, kolb__jryoz,
            pofd__iihj))
        vxdp__blpu = c.builder.trunc(c.builder.and_(nmj__qcy, lir.Constant(
            lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(zppjr__bzsps, vxdp__blpu), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        jhbo__bbqq = cgutils.gep(c.builder, blkd__nmyny, nmj__qcy)
        c.builder.store(val, jhbo__bbqq)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        emuye__dzv.null_bitmap)
    rzinq__toqr = c.context.insert_const_string(c.builder.module, 'pandas')
    aweq__kyar = c.pyapi.import_module_noblock(rzinq__toqr)
    zheb__ygbrx = c.pyapi.object_getattr_string(aweq__kyar, 'arrays')
    ugj__dxipz = c.pyapi.call_method(zheb__ygbrx, 'BooleanArray', (data,
        xzkfn__nhcev))
    c.pyapi.decref(aweq__kyar)
    c.pyapi.decref(ief__njgt)
    c.pyapi.decref(jwn__jvba)
    c.pyapi.decref(ezen__ogkfg)
    c.pyapi.decref(rmzeg__nfp)
    c.pyapi.decref(sfem__ypn)
    c.pyapi.decref(zheb__ygbrx)
    c.pyapi.decref(data)
    c.pyapi.decref(xzkfn__nhcev)
    return ugj__dxipz


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    jiql__urwd = np.empty(n, np.bool_)
    wdjrp__tzydr = np.empty(n + 7 >> 3, np.uint8)
    for nmj__qcy, s in enumerate(pyval):
        zeucf__utz = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(wdjrp__tzydr, nmj__qcy, int(
            not zeucf__utz))
        if not zeucf__utz:
            jiql__urwd[nmj__qcy] = s
    uqv__dtikq = context.get_constant_generic(builder, data_type, jiql__urwd)
    mxws__eoved = context.get_constant_generic(builder, nulls_type,
        wdjrp__tzydr)
    return lir.Constant.literal_struct([uqv__dtikq, mxws__eoved])


def lower_init_bool_array(context, builder, signature, args):
    anfhz__hzpib, kbkog__bung = args
    emuye__dzv = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    emuye__dzv.data = anfhz__hzpib
    emuye__dzv.null_bitmap = kbkog__bung
    context.nrt.incref(builder, signature.args[0], anfhz__hzpib)
    context.nrt.incref(builder, signature.args[1], kbkog__bung)
    return emuye__dzv._getvalue()


@intrinsic
def init_bool_array(typingctx, data, null_bitmap=None):
    assert data == types.Array(types.bool_, 1, 'C')
    assert null_bitmap == types.Array(types.uint8, 1, 'C')
    sig = boolean_array(data, null_bitmap)
    return sig, lower_init_bool_array


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_bool_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    rpxi__okn = args[0]
    if equiv_set.has_shape(rpxi__okn):
        return ArrayAnalysis.AnalyzeResult(shape=rpxi__okn, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    rpxi__okn = args[0]
    if equiv_set.has_shape(rpxi__okn):
        return ArrayAnalysis.AnalyzeResult(shape=rpxi__okn, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_init_bool_array = (
    init_bool_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_bool_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_bool_array',
    'bodo.libs.bool_arr_ext'] = alias_ext_init_bool_array
numba.core.ir_utils.alias_func_extensions['get_bool_arr_data',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_bool_arr_bitmap',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_bool_array(n):
    jiql__urwd = np.empty(n, dtype=np.bool_)
    ituem__amw = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(jiql__urwd, ituem__amw)


def alloc_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_alloc_bool_array = (
    alloc_bool_array_equiv)


@overload(operator.getitem, no_unliteral=True)
def bool_arr_getitem(A, ind):
    if A != boolean_array:
        return
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            umo__aurw, pmrq__mrc = array_getitem_bool_index(A, ind)
            return init_bool_array(umo__aurw, pmrq__mrc)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            umo__aurw, pmrq__mrc = array_getitem_int_index(A, ind)
            return init_bool_array(umo__aurw, pmrq__mrc)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            umo__aurw, pmrq__mrc = array_getitem_slice_index(A, ind)
            return init_bool_array(umo__aurw, pmrq__mrc)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    lcd__vjqnd = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(lcd__vjqnd)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(lcd__vjqnd)
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
        f'setitem for BooleanArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_bool_arr_len(A):
    if A == boolean_array:
        return lambda A: len(A._data)


@overload_attribute(BooleanArrayType, 'shape')
def overload_bool_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(BooleanArrayType, 'dtype')
def overload_bool_arr_dtype(A):
    return lambda A: pd.BooleanDtype()


@overload_attribute(BooleanArrayType, 'ndim')
def overload_bool_arr_ndim(A):
    return lambda A: 1


@overload_attribute(BooleanArrayType, 'nbytes')
def bool_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(BooleanArrayType, 'copy', no_unliteral=True)
def overload_bool_arr_copy(A):
    return lambda A: bodo.libs.bool_arr_ext.init_bool_array(bodo.libs.
        bool_arr_ext.get_bool_arr_data(A).copy(), bodo.libs.bool_arr_ext.
        get_bool_arr_bitmap(A).copy())


@overload_method(BooleanArrayType, 'sum', no_unliteral=True, inline='always')
def overload_bool_sum(A):

    def impl(A):
        numba.parfors.parfor.init_prange()
        s = 0
        for nmj__qcy in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, nmj__qcy):
                val = A[nmj__qcy]
            s += val
        return s
    return impl


@overload_method(BooleanArrayType, 'astype', no_unliteral=True)
def overload_bool_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "BooleanArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if dtype == types.bool_:
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
    nb_dtype = parse_dtype(dtype, 'BooleanArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
            n = len(data)
            ruzvu__ckn = np.empty(n, nb_dtype)
            for nmj__qcy in numba.parfors.parfor.internal_prange(n):
                ruzvu__ckn[nmj__qcy] = data[nmj__qcy]
                if bodo.libs.array_kernels.isna(A, nmj__qcy):
                    ruzvu__ckn[nmj__qcy] = np.nan
            return ruzvu__ckn
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload(str, no_unliteral=True)
def overload_str_bool(val):
    if val == types.bool_:

        def impl(val):
            if val:
                return 'True'
            return 'False'
        return impl


ufunc_aliases = {'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    lsebg__xbl = op.__name__
    lsebg__xbl = ufunc_aliases.get(lsebg__xbl, lsebg__xbl)
    if n_inputs == 1:

        def overload_bool_arr_op_nin_1(A):
            if isinstance(A, BooleanArrayType):
                return bodo.libs.int_arr_ext.get_nullable_array_unary_impl(op,
                    A)
        return overload_bool_arr_op_nin_1
    elif n_inputs == 2:

        def overload_bool_arr_op_nin_2(lhs, rhs):
            if lhs == boolean_array or rhs == boolean_array:
                return bodo.libs.int_arr_ext.get_nullable_array_binary_impl(op,
                    lhs, rhs)
        return overload_bool_arr_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for euya__uxr in numba.np.ufunc_db.get_ufuncs():
        uys__dtyhj = create_op_overload(euya__uxr, euya__uxr.nin)
        overload(euya__uxr, no_unliteral=True)(uys__dtyhj)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        uys__dtyhj = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(uys__dtyhj)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        uys__dtyhj = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(uys__dtyhj)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        uys__dtyhj = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(uys__dtyhj)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        vxdp__blpu = []
        drlpo__onn = False
        pasti__wgc = False
        fctcj__qlz = False
        for nmj__qcy in range(len(A)):
            if bodo.libs.array_kernels.isna(A, nmj__qcy):
                if not drlpo__onn:
                    data.append(False)
                    vxdp__blpu.append(False)
                    drlpo__onn = True
                continue
            val = A[nmj__qcy]
            if val and not pasti__wgc:
                data.append(True)
                vxdp__blpu.append(True)
                pasti__wgc = True
            if not val and not fctcj__qlz:
                data.append(False)
                vxdp__blpu.append(True)
                fctcj__qlz = True
            if drlpo__onn and pasti__wgc and fctcj__qlz:
                break
        umo__aurw = np.array(data)
        n = len(umo__aurw)
        dvjx__ccb = 1
        pmrq__mrc = np.empty(dvjx__ccb, np.uint8)
        for owyri__zyv in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(pmrq__mrc, owyri__zyv,
                vxdp__blpu[owyri__zyv])
        return init_bool_array(umo__aurw, pmrq__mrc)
    return impl_bool_arr


@overload(operator.getitem, no_unliteral=True)
def bool_arr_ind_getitem(A, ind):
    if ind == boolean_array and (isinstance(A, (types.Array, bodo.libs.
        int_arr_ext.IntegerArrayType)) or isinstance(A, bodo.libs.
        struct_arr_ext.StructArrayType) or isinstance(A, bodo.libs.
        array_item_arr_ext.ArrayItemArrayType) or isinstance(A, bodo.libs.
        map_arr_ext.MapArrayType) or A in (string_array_type, bodo.hiframes
        .split_impl.string_array_split_view_type, boolean_array)):
        return lambda A, ind: A[ind._data]


@lower_cast(types.Array(types.bool_, 1, 'C'), boolean_array)
def cast_np_bool_arr_to_bool_arr(context, builder, fromty, toty, val):
    func = lambda A: bodo.libs.bool_arr_ext.init_bool_array(A, np.full(len(
        A) + 7 >> 3, 255, np.uint8))
    ugj__dxipz = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, ugj__dxipz)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    oot__pfei = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        pnp__dkp = bodo.utils.utils.is_array_typ(val1, False)
        tpye__pqghs = bodo.utils.utils.is_array_typ(val2, False)
        wqoqh__vlltr = 'val1' if pnp__dkp else 'val2'
        lfu__hca = 'def impl(val1, val2):\n'
        lfu__hca += f'  n = len({wqoqh__vlltr})\n'
        lfu__hca += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        lfu__hca += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if pnp__dkp:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            jbkvk__stx = 'val1[i]'
        else:
            null1 = 'False\n'
            jbkvk__stx = 'val1'
        if tpye__pqghs:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            enmn__lkgph = 'val2[i]'
        else:
            null2 = 'False\n'
            enmn__lkgph = 'val2'
        if oot__pfei:
            lfu__hca += f"""    result, isna_val = compute_or_body({null1}, {null2}, {jbkvk__stx}, {enmn__lkgph})
"""
        else:
            lfu__hca += f"""    result, isna_val = compute_and_body({null1}, {null2}, {jbkvk__stx}, {enmn__lkgph})
"""
        lfu__hca += '    out_arr[i] = result\n'
        lfu__hca += '    if isna_val:\n'
        lfu__hca += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        lfu__hca += '      continue\n'
        lfu__hca += '  return out_arr\n'
        cdtg__zlt = {}
        exec(lfu__hca, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, cdtg__zlt)
        impl = cdtg__zlt['impl']
        return impl
    return bool_array_impl


def compute_or_body(null1, null2, val1, val2):
    pass


@overload(compute_or_body)
def overload_compute_or_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == False
        elif null2:
            return val1, val1 == False
        else:
            return val1 | val2, False
    return impl


def compute_and_body(null1, null2, val1, val2):
    pass


@overload(compute_and_body)
def overload_compute_and_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == True
        elif null2:
            return val1, val1 == True
        else:
            return val1 & val2, False
    return impl


def create_boolean_array_logical_lower_impl(op):

    def logical_lower_impl(context, builder, sig, args):
        impl = create_nullable_logical_op_overload(op)(*sig.args)
        return context.compile_internal(builder, impl, sig, args)
    return logical_lower_impl


class BooleanArrayLogicalOperatorTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        if not is_valid_boolean_array_logical_op(args[0], args[1]):
            return
        xgiwu__mgwg = boolean_array
        return xgiwu__mgwg(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    zicmq__zif = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return zicmq__zif


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        dacm__yxfzi = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(dacm__yxfzi)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(dacm__yxfzi)


_install_nullable_logical_lowering()
