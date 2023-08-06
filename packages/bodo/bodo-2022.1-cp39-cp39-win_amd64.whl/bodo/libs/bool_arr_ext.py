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
        uzhog__yjkdw = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, uzhog__yjkdw)


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
    bxw__tqdg = c.context.insert_const_string(c.builder.module, 'pandas')
    lumlh__otij = c.pyapi.import_module_noblock(bxw__tqdg)
    gfdpl__yuh = c.pyapi.call_method(lumlh__otij, 'BooleanDtype', ())
    c.pyapi.decref(lumlh__otij)
    return gfdpl__yuh


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    eayqp__qnmoj = n + 7 >> 3
    return np.full(eayqp__qnmoj, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    aig__cbq = c.context.typing_context.resolve_value_type(func)
    jlfpt__cjyjc = aig__cbq.get_call_type(c.context.typing_context,
        arg_typs, {})
    voj__jxx = c.context.get_function(aig__cbq, jlfpt__cjyjc)
    fuol__cvj = c.context.call_conv.get_function_type(jlfpt__cjyjc.
        return_type, jlfpt__cjyjc.args)
    jgw__tft = c.builder.module
    ovqff__mhng = lir.Function(jgw__tft, fuol__cvj, name=jgw__tft.
        get_unique_name('.func_conv'))
    ovqff__mhng.linkage = 'internal'
    smb__wye = lir.IRBuilder(ovqff__mhng.append_basic_block())
    hqlc__eim = c.context.call_conv.decode_arguments(smb__wye, jlfpt__cjyjc
        .args, ovqff__mhng)
    yfycd__cgi = voj__jxx(smb__wye, hqlc__eim)
    c.context.call_conv.return_value(smb__wye, yfycd__cgi)
    awk__weuox, fzicc__kcmh = c.context.call_conv.call_function(c.builder,
        ovqff__mhng, jlfpt__cjyjc.return_type, jlfpt__cjyjc.args, args)
    return fzicc__kcmh


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    uhc__dczb = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(uhc__dczb)
    c.pyapi.decref(uhc__dczb)
    fuol__cvj = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    zwvhh__lazxk = cgutils.get_or_insert_function(c.builder.module,
        fuol__cvj, name='is_bool_array')
    fuol__cvj = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    ovqff__mhng = cgutils.get_or_insert_function(c.builder.module,
        fuol__cvj, name='is_pd_boolean_array')
    jyq__wiff = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rktp__ygw = c.builder.call(ovqff__mhng, [obj])
    bvxi__wblu = c.builder.icmp_unsigned('!=', rktp__ygw, rktp__ygw.type(0))
    with c.builder.if_else(bvxi__wblu) as (pd_then, pd_otherwise):
        with pd_then:
            cheow__lxg = c.pyapi.object_getattr_string(obj, '_data')
            jyq__wiff.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), cheow__lxg).value
            quhjm__nvc = c.pyapi.object_getattr_string(obj, '_mask')
            uxu__yzik = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), quhjm__nvc).value
            eayqp__qnmoj = c.builder.udiv(c.builder.add(n, lir.Constant(lir
                .IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            cwvo__mjke = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, uxu__yzik)
            nlari__yhl = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [eayqp__qnmoj])
            fuol__cvj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            ovqff__mhng = cgutils.get_or_insert_function(c.builder.module,
                fuol__cvj, name='mask_arr_to_bitmap')
            c.builder.call(ovqff__mhng, [nlari__yhl.data, cwvo__mjke.data, n])
            jyq__wiff.null_bitmap = nlari__yhl._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), uxu__yzik)
            c.pyapi.decref(cheow__lxg)
            c.pyapi.decref(quhjm__nvc)
        with pd_otherwise:
            ruqln__cej = c.builder.call(zwvhh__lazxk, [obj])
            qkihg__qvlb = c.builder.icmp_unsigned('!=', ruqln__cej,
                ruqln__cej.type(0))
            with c.builder.if_else(qkihg__qvlb) as (then, otherwise):
                with then:
                    jyq__wiff.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    jyq__wiff.null_bitmap = call_func_in_unbox(gen_full_bitmap,
                        (n,), (types.int64,), c)
                with otherwise:
                    jyq__wiff.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    eayqp__qnmoj = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    jyq__wiff.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [eayqp__qnmoj])._getvalue()
                    sriy__geeah = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, jyq__wiff.data
                        ).data
                    sjf__goxze = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, jyq__wiff.
                        null_bitmap).data
                    fuol__cvj = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    ovqff__mhng = cgutils.get_or_insert_function(c.builder.
                        module, fuol__cvj, name='unbox_bool_array_obj')
                    c.builder.call(ovqff__mhng, [obj, sriy__geeah,
                        sjf__goxze, n])
    return NativeValue(jyq__wiff._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    jyq__wiff = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        jyq__wiff.data, c.env_manager)
    rzro__cygm = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, jyq__wiff.null_bitmap).data
    uhc__dczb = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(uhc__dczb)
    bxw__tqdg = c.context.insert_const_string(c.builder.module, 'numpy')
    qpdg__pie = c.pyapi.import_module_noblock(bxw__tqdg)
    wzdua__fepj = c.pyapi.object_getattr_string(qpdg__pie, 'bool_')
    uxu__yzik = c.pyapi.call_method(qpdg__pie, 'empty', (uhc__dczb,
        wzdua__fepj))
    zqkx__romii = c.pyapi.object_getattr_string(uxu__yzik, 'ctypes')
    fevf__epp = c.pyapi.object_getattr_string(zqkx__romii, 'data')
    bch__wpn = c.builder.inttoptr(c.pyapi.long_as_longlong(fevf__epp), lir.
        IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as loop:
        czvk__pkl = loop.index
        jnzw__ziic = c.builder.lshr(czvk__pkl, lir.Constant(lir.IntType(64), 3)
            )
        ikql__bgpbp = c.builder.load(cgutils.gep(c.builder, rzro__cygm,
            jnzw__ziic))
        kwvwr__usom = c.builder.trunc(c.builder.and_(czvk__pkl, lir.
            Constant(lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(ikql__bgpbp, kwvwr__usom), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        muwhd__nsh = cgutils.gep(c.builder, bch__wpn, czvk__pkl)
        c.builder.store(val, muwhd__nsh)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        jyq__wiff.null_bitmap)
    bxw__tqdg = c.context.insert_const_string(c.builder.module, 'pandas')
    lumlh__otij = c.pyapi.import_module_noblock(bxw__tqdg)
    xwrgq__kaqiq = c.pyapi.object_getattr_string(lumlh__otij, 'arrays')
    gfdpl__yuh = c.pyapi.call_method(xwrgq__kaqiq, 'BooleanArray', (data,
        uxu__yzik))
    c.pyapi.decref(lumlh__otij)
    c.pyapi.decref(uhc__dczb)
    c.pyapi.decref(qpdg__pie)
    c.pyapi.decref(wzdua__fepj)
    c.pyapi.decref(zqkx__romii)
    c.pyapi.decref(fevf__epp)
    c.pyapi.decref(xwrgq__kaqiq)
    c.pyapi.decref(data)
    c.pyapi.decref(uxu__yzik)
    return gfdpl__yuh


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    ifwji__ajea = np.empty(n, np.bool_)
    nnrl__fbt = np.empty(n + 7 >> 3, np.uint8)
    for czvk__pkl, s in enumerate(pyval):
        oca__vfe = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(nnrl__fbt, czvk__pkl, int(not
            oca__vfe))
        if not oca__vfe:
            ifwji__ajea[czvk__pkl] = s
    cfe__cxpa = context.get_constant_generic(builder, data_type, ifwji__ajea)
    oxhu__qggl = context.get_constant_generic(builder, nulls_type, nnrl__fbt)
    return lir.Constant.literal_struct([cfe__cxpa, oxhu__qggl])


def lower_init_bool_array(context, builder, signature, args):
    qxbv__nszm, pgmux__wwma = args
    jyq__wiff = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    jyq__wiff.data = qxbv__nszm
    jyq__wiff.null_bitmap = pgmux__wwma
    context.nrt.incref(builder, signature.args[0], qxbv__nszm)
    context.nrt.incref(builder, signature.args[1], pgmux__wwma)
    return jyq__wiff._getvalue()


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
    vna__zwp = args[0]
    if equiv_set.has_shape(vna__zwp):
        return ArrayAnalysis.AnalyzeResult(shape=vna__zwp, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    vna__zwp = args[0]
    if equiv_set.has_shape(vna__zwp):
        return ArrayAnalysis.AnalyzeResult(shape=vna__zwp, pre=[])
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
    ifwji__ajea = np.empty(n, dtype=np.bool_)
    rzqmn__qxpqj = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(ifwji__ajea, rzqmn__qxpqj)


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
            jwq__mwckm, zlhr__vlq = array_getitem_bool_index(A, ind)
            return init_bool_array(jwq__mwckm, zlhr__vlq)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            jwq__mwckm, zlhr__vlq = array_getitem_int_index(A, ind)
            return init_bool_array(jwq__mwckm, zlhr__vlq)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            jwq__mwckm, zlhr__vlq = array_getitem_slice_index(A, ind)
            return init_bool_array(jwq__mwckm, zlhr__vlq)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    ekgoz__dsbts = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(ekgoz__dsbts)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(ekgoz__dsbts)
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
        for czvk__pkl in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, czvk__pkl):
                val = A[czvk__pkl]
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
            ratfj__eyo = np.empty(n, nb_dtype)
            for czvk__pkl in numba.parfors.parfor.internal_prange(n):
                ratfj__eyo[czvk__pkl] = data[czvk__pkl]
                if bodo.libs.array_kernels.isna(A, czvk__pkl):
                    ratfj__eyo[czvk__pkl] = np.nan
            return ratfj__eyo
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
    vegq__iqi = op.__name__
    vegq__iqi = ufunc_aliases.get(vegq__iqi, vegq__iqi)
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
    for tszbd__ekm in numba.np.ufunc_db.get_ufuncs():
        vzb__oppv = create_op_overload(tszbd__ekm, tszbd__ekm.nin)
        overload(tszbd__ekm, no_unliteral=True)(vzb__oppv)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        vzb__oppv = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(vzb__oppv)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        vzb__oppv = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(vzb__oppv)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        vzb__oppv = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(vzb__oppv)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        kwvwr__usom = []
        xumm__fsrx = False
        wbmo__purn = False
        svjlw__ygc = False
        for czvk__pkl in range(len(A)):
            if bodo.libs.array_kernels.isna(A, czvk__pkl):
                if not xumm__fsrx:
                    data.append(False)
                    kwvwr__usom.append(False)
                    xumm__fsrx = True
                continue
            val = A[czvk__pkl]
            if val and not wbmo__purn:
                data.append(True)
                kwvwr__usom.append(True)
                wbmo__purn = True
            if not val and not svjlw__ygc:
                data.append(False)
                kwvwr__usom.append(True)
                svjlw__ygc = True
            if xumm__fsrx and wbmo__purn and svjlw__ygc:
                break
        jwq__mwckm = np.array(data)
        n = len(jwq__mwckm)
        eayqp__qnmoj = 1
        zlhr__vlq = np.empty(eayqp__qnmoj, np.uint8)
        for ieebj__bca in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(zlhr__vlq, ieebj__bca,
                kwvwr__usom[ieebj__bca])
        return init_bool_array(jwq__mwckm, zlhr__vlq)
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
    gfdpl__yuh = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, gfdpl__yuh)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    nvqc__cqltn = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        uyvw__bvv = bodo.utils.utils.is_array_typ(val1, False)
        xtl__lql = bodo.utils.utils.is_array_typ(val2, False)
        qvlg__klej = 'val1' if uyvw__bvv else 'val2'
        gzdmy__ixwzq = 'def impl(val1, val2):\n'
        gzdmy__ixwzq += f'  n = len({qvlg__klej})\n'
        gzdmy__ixwzq += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        gzdmy__ixwzq += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if uyvw__bvv:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            cdr__tnd = 'val1[i]'
        else:
            null1 = 'False\n'
            cdr__tnd = 'val1'
        if xtl__lql:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            fix__ous = 'val2[i]'
        else:
            null2 = 'False\n'
            fix__ous = 'val2'
        if nvqc__cqltn:
            gzdmy__ixwzq += f"""    result, isna_val = compute_or_body({null1}, {null2}, {cdr__tnd}, {fix__ous})
"""
        else:
            gzdmy__ixwzq += f"""    result, isna_val = compute_and_body({null1}, {null2}, {cdr__tnd}, {fix__ous})
"""
        gzdmy__ixwzq += '    out_arr[i] = result\n'
        gzdmy__ixwzq += '    if isna_val:\n'
        gzdmy__ixwzq += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        gzdmy__ixwzq += '      continue\n'
        gzdmy__ixwzq += '  return out_arr\n'
        wse__zuz = {}
        exec(gzdmy__ixwzq, {'bodo': bodo, 'numba': numba,
            'compute_and_body': compute_and_body, 'compute_or_body':
            compute_or_body}, wse__zuz)
        impl = wse__zuz['impl']
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
        wyw__diiaz = boolean_array
        return wyw__diiaz(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    tfkx__zte = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return tfkx__zte


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        gwae__cuefq = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(gwae__cuefq)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(gwae__cuefq)


_install_nullable_logical_lowering()
