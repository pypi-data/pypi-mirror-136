"""
Array of intervals corresponding to IntervalArray of Pandas.
Used for IntervalIndex, which is necessary for Series.value_counts() with 'bins'
argument.
"""
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo


class IntervalType(types.Type):

    def __init__(self):
        super(IntervalType, self).__init__('IntervalType()')


class IntervalArrayType(types.ArrayCompatible):

    def __init__(self, arr_type):
        self.arr_type = arr_type
        self.dtype = IntervalType()
        super(IntervalArrayType, self).__init__(name=
            f'IntervalArrayType({arr_type})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntervalArrayType(self.arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(IntervalArrayType)
class IntervalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        mjv__gfeyz = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, mjv__gfeyz)


make_attribute_wrapper(IntervalArrayType, 'left', '_left')
make_attribute_wrapper(IntervalArrayType, 'right', '_right')


@typeof_impl.register(pd.arrays.IntervalArray)
def typeof_interval_array(val, c):
    arr_type = bodo.typeof(val._left)
    return IntervalArrayType(arr_type)


@intrinsic
def init_interval_array(typingctx, left, right=None):
    assert left == right, 'Interval left/right array types should be the same'

    def codegen(context, builder, signature, args):
        etw__eean, bkgxo__wfxf = args
        jviho__itf = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        jviho__itf.left = etw__eean
        jviho__itf.right = bkgxo__wfxf
        context.nrt.incref(builder, signature.args[0], etw__eean)
        context.nrt.incref(builder, signature.args[1], bkgxo__wfxf)
        return jviho__itf._getvalue()
    xfqf__hkf = IntervalArrayType(left)
    nvsn__nfabj = xfqf__hkf(left, right)
    return nvsn__nfabj, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    shb__cul = []
    for qbli__vqwd in args:
        swdlq__gxn = equiv_set.get_shape(qbli__vqwd)
        if swdlq__gxn is not None:
            shb__cul.append(swdlq__gxn[0])
    if len(shb__cul) > 1:
        equiv_set.insert_equiv(*shb__cul)
    left = args[0]
    if equiv_set.has_shape(left):
        return ArrayAnalysis.AnalyzeResult(shape=left, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_libs_interval_arr_ext_init_interval_array
    ) = init_interval_array_equiv


def alias_ext_init_interval_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_interval_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_interval_array


@box(IntervalArrayType)
def box_interval_arr(typ, val, c):
    jviho__itf = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, jviho__itf.left)
    gsplq__cgjh = c.pyapi.from_native_value(typ.arr_type, jviho__itf.left,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, jviho__itf.right)
    jzbfk__xpk = c.pyapi.from_native_value(typ.arr_type, jviho__itf.right,
        c.env_manager)
    kst__eydmb = c.context.insert_const_string(c.builder.module, 'pandas')
    vipxw__jxwa = c.pyapi.import_module_noblock(kst__eydmb)
    urqo__bkaoc = c.pyapi.object_getattr_string(vipxw__jxwa, 'arrays')
    vuvr__jbv = c.pyapi.object_getattr_string(urqo__bkaoc, 'IntervalArray')
    juu__ucwet = c.pyapi.call_method(vuvr__jbv, 'from_arrays', (gsplq__cgjh,
        jzbfk__xpk))
    c.pyapi.decref(gsplq__cgjh)
    c.pyapi.decref(jzbfk__xpk)
    c.pyapi.decref(vipxw__jxwa)
    c.pyapi.decref(urqo__bkaoc)
    c.pyapi.decref(vuvr__jbv)
    c.context.nrt.decref(c.builder, typ, val)
    return juu__ucwet


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    gsplq__cgjh = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, gsplq__cgjh).value
    c.pyapi.decref(gsplq__cgjh)
    jzbfk__xpk = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, jzbfk__xpk).value
    c.pyapi.decref(jzbfk__xpk)
    jviho__itf = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jviho__itf.left = left
    jviho__itf.right = right
    jqhd__xbs = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jviho__itf._getvalue(), is_error=jqhd__xbs)


@overload(len, no_unliteral=True)
def overload_interval_arr_len(A):
    if isinstance(A, IntervalArrayType):
        return lambda A: len(A._left)


@overload_attribute(IntervalArrayType, 'shape')
def overload_interval_arr_shape(A):
    return lambda A: (len(A._left),)


@overload_attribute(IntervalArrayType, 'ndim')
def overload_interval_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntervalArrayType, 'nbytes')
def overload_interval_arr_nbytes(A):
    return lambda A: A._left.nbytes + A._right.nbytes


@overload_method(IntervalArrayType, 'copy', no_unliteral=True)
def overload_interval_arr_copy(A):
    return lambda A: bodo.libs.interval_arr_ext.init_interval_array(A._left
        .copy(), A._right.copy())
