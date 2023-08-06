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
        zix__gfbfw = [('data', fe_type.tuple_typ), ('null_values', fe_type.
            null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, zix__gfbfw)


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
        fxqrv__wkxb = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        fxqrv__wkxb.data = data_tuple
        fxqrv__wkxb.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return fxqrv__wkxb._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    cas__qgo = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    c.context.nrt.incref(c.builder, typ.tuple_typ, cas__qgo.data)
    c.context.nrt.incref(c.builder, typ.null_typ, cas__qgo.null_values)
    hlhr__rfy = c.pyapi.from_native_value(typ.tuple_typ, cas__qgo.data, c.
        env_manager)
    qiaj__mbibt = c.pyapi.from_native_value(typ.null_typ, cas__qgo.
        null_values, c.env_manager)
    ruy__xgypn = c.context.get_constant(types.int64, len(typ.tuple_typ))
    pmijm__anmyw = c.pyapi.list_new(ruy__xgypn)
    with cgutils.for_range(c.builder, ruy__xgypn) as loop:
        i = loop.index
        ock__ueis = c.pyapi.long_from_longlong(i)
        jva__coms = c.pyapi.object_getitem(qiaj__mbibt, ock__ueis)
        yir__zkd = c.pyapi.to_native_value(types.bool_, jva__coms).value
        with c.builder.if_else(yir__zkd) as (then, orelse):
            with then:
                c.pyapi.list_setitem(pmijm__anmyw, i, c.pyapi.make_none())
            with orelse:
                ufnx__fabtq = c.pyapi.object_getitem(hlhr__rfy, ock__ueis)
                c.pyapi.list_setitem(pmijm__anmyw, i, ufnx__fabtq)
        c.pyapi.decref(ock__ueis)
        c.pyapi.decref(jva__coms)
    pxk__rygqq = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    idft__sbu = c.pyapi.call_function_objargs(pxk__rygqq, (pmijm__anmyw,))
    c.pyapi.decref(hlhr__rfy)
    c.pyapi.decref(qiaj__mbibt)
    c.pyapi.decref(pxk__rygqq)
    c.pyapi.decref(pmijm__anmyw)
    c.context.nrt.decref(c.builder, typ, val)
    return idft__sbu


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
    fxqrv__wkxb = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    hvz__dwb = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return hvz__dwb(builder, (fxqrv__wkxb.data,))
