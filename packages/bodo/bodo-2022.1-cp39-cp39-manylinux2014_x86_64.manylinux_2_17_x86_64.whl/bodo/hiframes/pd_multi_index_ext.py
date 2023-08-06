"""Support for MultiIndex type of Pandas
"""
import operator
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, register_model, typeof_impl, unbox
from bodo.utils.typing import BodoError, check_unsupported_args, dtype_to_array_type, get_val_type_maybe_str_literal, is_overload_none


class MultiIndexType(types.Type):

    def __init__(self, array_types, names_typ=None, name_typ=None):
        names_typ = (types.none,) * len(array_types
            ) if names_typ is None else names_typ
        name_typ = types.none if name_typ is None else name_typ
        self.array_types = array_types
        self.names_typ = names_typ
        self.name_typ = name_typ
        super(MultiIndexType, self).__init__(name=
            'MultiIndexType({}, {}, {})'.format(array_types, names_typ,
            name_typ))
    ndim = 1

    def copy(self):
        return MultiIndexType(self.array_types, self.names_typ, self.name_typ)

    @property
    def nlevels(self):
        return len(self.array_types)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(MultiIndexType)
class MultiIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hymb__nwo = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, hymb__nwo)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[lcjec__vhbt].values) for
        lcjec__vhbt in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (llkms__ckn) for llkms__ckn in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    wuecw__pephq = c.context.insert_const_string(c.builder.module, 'pandas')
    blc__hlwe = c.pyapi.import_module_noblock(wuecw__pephq)
    emrwg__oenub = c.pyapi.object_getattr_string(blc__hlwe, 'MultiIndex')
    tmw__kmt = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types), tmw__kmt.data
        )
    data = c.pyapi.from_native_value(types.Tuple(typ.array_types), tmw__kmt
        .data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), tmw__kmt.names)
    names = c.pyapi.from_native_value(types.Tuple(typ.names_typ), tmw__kmt.
        names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, tmw__kmt.name)
    name = c.pyapi.from_native_value(typ.name_typ, tmw__kmt.name, c.env_manager
        )
    sortorder = c.pyapi.make_none()
    xblk__bmsrw = c.pyapi.call_method(emrwg__oenub, 'from_arrays', (data,
        sortorder, names))
    c.pyapi.object_setattr_string(xblk__bmsrw, 'name', name)
    c.pyapi.decref(blc__hlwe)
    c.pyapi.decref(emrwg__oenub)
    c.context.nrt.decref(c.builder, typ, val)
    return xblk__bmsrw


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    utt__gjb = []
    rpz__dme = []
    for lcjec__vhbt in range(typ.nlevels):
        tjb__lkjqk = c.pyapi.unserialize(c.pyapi.serialize_object(lcjec__vhbt))
        naa__vlqg = c.pyapi.call_method(val, 'get_level_values', (tjb__lkjqk,))
        qmihp__ema = c.pyapi.object_getattr_string(naa__vlqg, 'values')
        c.pyapi.decref(naa__vlqg)
        c.pyapi.decref(tjb__lkjqk)
        mcq__tkrr = c.pyapi.to_native_value(typ.array_types[lcjec__vhbt],
            qmihp__ema).value
        utt__gjb.append(mcq__tkrr)
        rpz__dme.append(qmihp__ema)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, utt__gjb)
    else:
        data = cgutils.pack_struct(c.builder, utt__gjb)
    kkkrf__wnm = c.pyapi.object_getattr_string(val, 'names')
    muvqa__faf = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    zbz__rex = c.pyapi.call_function_objargs(muvqa__faf, (kkkrf__wnm,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), zbz__rex).value
    mdf__pixmr = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, mdf__pixmr).value
    tmw__kmt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tmw__kmt.data = data
    tmw__kmt.names = names
    tmw__kmt.name = name
    for qmihp__ema in rpz__dme:
        c.pyapi.decref(qmihp__ema)
    c.pyapi.decref(kkkrf__wnm)
    c.pyapi.decref(muvqa__faf)
    c.pyapi.decref(zbz__rex)
    c.pyapi.decref(mdf__pixmr)
    return NativeValue(tmw__kmt._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    abmo__urps = 'pandas.MultiIndex.from_product'
    jbe__fvd = dict(sortorder=sortorder)
    hfw__tdw = dict(sortorder=None)
    check_unsupported_args(abmo__urps, jbe__fvd, hfw__tdw, package_name=
        'pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{abmo__urps}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{abmo__urps}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{abmo__urps}: iterables and names must be of the same length.')


def from_product(iterable, sortorder=None, names=None):
    pass


@overload(from_product)
def from_product_overload(iterables, sortorder=None, names=None):
    from_product_error_checking(iterables, sortorder, names)
    array_types = tuple(dtype_to_array_type(iterable.dtype) for iterable in
        iterables)
    if is_overload_none(names):
        names_typ = tuple([types.none] * len(iterables))
    else:
        names_typ = names.types
    tymo__cdlw = MultiIndexType(array_types, names_typ)
    ghxn__pewnu = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, ghxn__pewnu, tymo__cdlw)
    qbgw__ghmg = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{ghxn__pewnu}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    siurj__fljh = {}
    exec(qbgw__ghmg, globals(), siurj__fljh)
    kvwv__mdkuo = siurj__fljh['impl']
    return kvwv__mdkuo


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        kvc__tdcbi, pahzb__rsrg, tzdz__tddp = args
        ipjuq__nzij = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        ipjuq__nzij.data = kvc__tdcbi
        ipjuq__nzij.names = pahzb__rsrg
        ipjuq__nzij.name = tzdz__tddp
        context.nrt.incref(builder, signature.args[0], kvc__tdcbi)
        context.nrt.incref(builder, signature.args[1], pahzb__rsrg)
        context.nrt.incref(builder, signature.args[2], tzdz__tddp)
        return ipjuq__nzij._getvalue()
    ixvy__bmjx = MultiIndexType(data.types, names.types, name)
    return ixvy__bmjx(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        dena__gvyz = len(I.array_types)
        qbgw__ghmg = 'def impl(I, ind):\n'
        qbgw__ghmg += '  data = I._data\n'
        qbgw__ghmg += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(f'data[{lcjec__vhbt}][ind]' for lcjec__vhbt in
            range(dena__gvyz))))
        siurj__fljh = {}
        exec(qbgw__ghmg, {'init_multi_index': init_multi_index}, siurj__fljh)
        kvwv__mdkuo = siurj__fljh['impl']
        return kvwv__mdkuo


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    gmogc__dzs, nvo__sivaj = sig.args
    if gmogc__dzs != nvo__sivaj:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
