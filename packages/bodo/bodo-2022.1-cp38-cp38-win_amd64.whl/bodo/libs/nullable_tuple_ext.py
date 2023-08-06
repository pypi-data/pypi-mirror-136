"""
Wrapper class for Tuples that supports tracking null entries.
This is primarily used for maintaining null information for
Series values used in df.apply
"""
import operator
from numba.core import cgutils, types
from numba.extending import box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, register_model


class NullableTupleType(types.IterableType):

    def __init__(self, tuple_typ, null_typ):
        self._tuple_typ = tuple_typ
        self._null_typ = null_typ
        super(NullableTupleType, self).__init__(name=
            f'NullableTupleType({tuple_typ}, {null_typ})')

    @property
    def tuple_typ(self):
        return self._tuple_typ

    @property
    def null_typ(self):
        return self._null_typ

    def __getitem__(self, i):
        return self._tuple_typ[i]

    @property
    def key(self):
        return self._tuple_typ

    @property
    def dtype(self):
        return self.tuple_typ.dtype

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def iterator_type(self):
        return self.tuple_typ.iterator_type


@register_model(NullableTupleType)
class NullableTupleModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qyz__ckq = [('data', fe_type.tuple_typ), ('null_values', fe_type.
            null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, qyz__ckq)


make_attribute_wrapper(NullableTupleType, 'data', '_data')
make_attribute_wrapper(NullableTupleType, 'null_values', '_null_values')


@intrinsic
def build_nullable_tuple(typingctx, data_tuple, null_values):
    assert isinstance(data_tuple, types.BaseTuple
        ), "build_nullable_tuple 'data_tuple' argument must be a tuple"
    assert isinstance(null_values, types.BaseTuple
        ), "build_nullable_tuple 'null_values' argument must be a tuple"

    def codegen(context, builder, signature, args):
        data_tuple, null_values = args
        banu__jnrye = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        banu__jnrye.data = data_tuple
        banu__jnrye.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return banu__jnrye._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    eyiq__cwxa = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    c.context.nrt.incref(c.builder, typ.tuple_typ, eyiq__cwxa.data)
    c.context.nrt.incref(c.builder, typ.null_typ, eyiq__cwxa.null_values)
    mpyi__gnxzq = c.pyapi.from_native_value(typ.tuple_typ, eyiq__cwxa.data,
        c.env_manager)
    ost__eco = c.pyapi.from_native_value(typ.null_typ, eyiq__cwxa.
        null_values, c.env_manager)
    pkkao__awrxc = c.context.get_constant(types.int64, len(typ.tuple_typ))
    lvzly__zffma = c.pyapi.list_new(pkkao__awrxc)
    with cgutils.for_range(c.builder, pkkao__awrxc) as loop:
        i = loop.index
        fwjs__gow = c.pyapi.long_from_longlong(i)
        ukqme__ehd = c.pyapi.object_getitem(ost__eco, fwjs__gow)
        uwlq__xghk = c.pyapi.to_native_value(types.bool_, ukqme__ehd).value
        with c.builder.if_else(uwlq__xghk) as (then, orelse):
            with then:
                c.pyapi.list_setitem(lvzly__zffma, i, c.pyapi.make_none())
            with orelse:
                unvq__prxv = c.pyapi.object_getitem(mpyi__gnxzq, fwjs__gow)
                c.pyapi.list_setitem(lvzly__zffma, i, unvq__prxv)
        c.pyapi.decref(fwjs__gow)
        c.pyapi.decref(ukqme__ehd)
    rei__jqdg = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    lhxlq__rsotj = c.pyapi.call_function_objargs(rei__jqdg, (lvzly__zffma,))
    c.pyapi.decref(mpyi__gnxzq)
    c.pyapi.decref(ost__eco)
    c.pyapi.decref(rei__jqdg)
    c.pyapi.decref(lvzly__zffma)
    c.context.nrt.decref(c.builder, typ, val)
    return lhxlq__rsotj


@overload(operator.getitem)
def overload_getitem(A, idx):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A, idx: A._data[idx]


@overload(len)
def overload_len(A):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A: len(A._data)


@lower_builtin('getiter', NullableTupleType)
def nullable_tuple_getiter(context, builder, sig, args):
    banu__jnrye = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    nyuf__hdi = context.get_function('getiter', sig.return_type(sig.args[0]
        .tuple_typ))
    return nyuf__hdi(builder, (banu__jnrye.data,))
