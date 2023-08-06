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
        fzer__lrszu = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, fzer__lrszu)


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
        avstd__yoelk, clnv__hqz = args
        gac__dlef = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        gac__dlef.left = avstd__yoelk
        gac__dlef.right = clnv__hqz
        context.nrt.incref(builder, signature.args[0], avstd__yoelk)
        context.nrt.incref(builder, signature.args[1], clnv__hqz)
        return gac__dlef._getvalue()
    nut__qaojq = IntervalArrayType(left)
    wcc__xnnhi = nut__qaojq(left, right)
    return wcc__xnnhi, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    mqw__svxlo = []
    for oiqxp__tue in args:
        vltg__ompm = equiv_set.get_shape(oiqxp__tue)
        if vltg__ompm is not None:
            mqw__svxlo.append(vltg__ompm[0])
    if len(mqw__svxlo) > 1:
        equiv_set.insert_equiv(*mqw__svxlo)
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
    gac__dlef = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, gac__dlef.left)
    gms__xdclq = c.pyapi.from_native_value(typ.arr_type, gac__dlef.left, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, gac__dlef.right)
    cgy__sdbzu = c.pyapi.from_native_value(typ.arr_type, gac__dlef.right, c
        .env_manager)
    htkuu__kyy = c.context.insert_const_string(c.builder.module, 'pandas')
    rgoc__elzj = c.pyapi.import_module_noblock(htkuu__kyy)
    icx__ixyd = c.pyapi.object_getattr_string(rgoc__elzj, 'arrays')
    jbc__rnyu = c.pyapi.object_getattr_string(icx__ixyd, 'IntervalArray')
    xgg__sqtuv = c.pyapi.call_method(jbc__rnyu, 'from_arrays', (gms__xdclq,
        cgy__sdbzu))
    c.pyapi.decref(gms__xdclq)
    c.pyapi.decref(cgy__sdbzu)
    c.pyapi.decref(rgoc__elzj)
    c.pyapi.decref(icx__ixyd)
    c.pyapi.decref(jbc__rnyu)
    c.context.nrt.decref(c.builder, typ, val)
    return xgg__sqtuv


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    gms__xdclq = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, gms__xdclq).value
    c.pyapi.decref(gms__xdclq)
    cgy__sdbzu = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, cgy__sdbzu).value
    c.pyapi.decref(cgy__sdbzu)
    gac__dlef = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    gac__dlef.left = left
    gac__dlef.right = right
    yerr__iiut = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(gac__dlef._getvalue(), is_error=yerr__iiut)


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
