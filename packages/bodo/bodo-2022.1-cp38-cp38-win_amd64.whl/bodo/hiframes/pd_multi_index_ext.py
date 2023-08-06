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
        khtvg__nbkl = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, khtvg__nbkl)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[wot__pdbo].values) for
        wot__pdbo in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (rasr__vadml) for rasr__vadml in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    pvx__eyt = c.context.insert_const_string(c.builder.module, 'pandas')
    gzj__fuc = c.pyapi.import_module_noblock(pvx__eyt)
    wxq__ojx = c.pyapi.object_getattr_string(gzj__fuc, 'MultiIndex')
    sbdjz__nfw = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types),
        sbdjz__nfw.data)
    data = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        sbdjz__nfw.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), sbdjz__nfw.
        names)
    names = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        sbdjz__nfw.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, sbdjz__nfw.name)
    name = c.pyapi.from_native_value(typ.name_typ, sbdjz__nfw.name, c.
        env_manager)
    sortorder = c.pyapi.make_none()
    rttw__vkjz = c.pyapi.call_method(wxq__ojx, 'from_arrays', (data,
        sortorder, names))
    c.pyapi.object_setattr_string(rttw__vkjz, 'name', name)
    c.pyapi.decref(gzj__fuc)
    c.pyapi.decref(wxq__ojx)
    c.context.nrt.decref(c.builder, typ, val)
    return rttw__vkjz


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    eigb__ctyuy = []
    qtn__qnj = []
    for wot__pdbo in range(typ.nlevels):
        avm__nyq = c.pyapi.unserialize(c.pyapi.serialize_object(wot__pdbo))
        lixpg__sjsdr = c.pyapi.call_method(val, 'get_level_values', (avm__nyq,)
            )
        fair__xzlhx = c.pyapi.object_getattr_string(lixpg__sjsdr, 'values')
        c.pyapi.decref(lixpg__sjsdr)
        c.pyapi.decref(avm__nyq)
        cdz__oyo = c.pyapi.to_native_value(typ.array_types[wot__pdbo],
            fair__xzlhx).value
        eigb__ctyuy.append(cdz__oyo)
        qtn__qnj.append(fair__xzlhx)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, eigb__ctyuy)
    else:
        data = cgutils.pack_struct(c.builder, eigb__ctyuy)
    zak__zmf = c.pyapi.object_getattr_string(val, 'names')
    aru__ehgc = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    kuyl__ctd = c.pyapi.call_function_objargs(aru__ehgc, (zak__zmf,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), kuyl__ctd
        ).value
    djfia__trp = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, djfia__trp).value
    sbdjz__nfw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    sbdjz__nfw.data = data
    sbdjz__nfw.names = names
    sbdjz__nfw.name = name
    for fair__xzlhx in qtn__qnj:
        c.pyapi.decref(fair__xzlhx)
    c.pyapi.decref(zak__zmf)
    c.pyapi.decref(aru__ehgc)
    c.pyapi.decref(kuyl__ctd)
    c.pyapi.decref(djfia__trp)
    return NativeValue(sbdjz__nfw._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    xebio__tdcdp = 'pandas.MultiIndex.from_product'
    hfkzc__gasdq = dict(sortorder=sortorder)
    hld__hmura = dict(sortorder=None)
    check_unsupported_args(xebio__tdcdp, hfkzc__gasdq, hld__hmura,
        package_name='pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{xebio__tdcdp}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{xebio__tdcdp}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{xebio__tdcdp}: iterables and names must be of the same length.')


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
    nng__qhuzz = MultiIndexType(array_types, names_typ)
    riei__mmc = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, riei__mmc, nng__qhuzz)
    icz__iuoxt = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{riei__mmc}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    buqr__xgmyu = {}
    exec(icz__iuoxt, globals(), buqr__xgmyu)
    jfx__nkocr = buqr__xgmyu['impl']
    return jfx__nkocr


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        jfse__gzb, huz__zfrnn, kxi__anfwv = args
        cqdfl__jhmp = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        cqdfl__jhmp.data = jfse__gzb
        cqdfl__jhmp.names = huz__zfrnn
        cqdfl__jhmp.name = kxi__anfwv
        context.nrt.incref(builder, signature.args[0], jfse__gzb)
        context.nrt.incref(builder, signature.args[1], huz__zfrnn)
        context.nrt.incref(builder, signature.args[2], kxi__anfwv)
        return cqdfl__jhmp._getvalue()
    jxiz__xegdr = MultiIndexType(data.types, names.types, name)
    return jxiz__xegdr(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        tami__jgh = len(I.array_types)
        icz__iuoxt = 'def impl(I, ind):\n'
        icz__iuoxt += '  data = I._data\n'
        icz__iuoxt += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(f'data[{wot__pdbo}][ind]' for wot__pdbo in
            range(tami__jgh))))
        buqr__xgmyu = {}
        exec(icz__iuoxt, {'init_multi_index': init_multi_index}, buqr__xgmyu)
        jfx__nkocr = buqr__xgmyu['impl']
        return jfx__nkocr


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    pxp__zdo, wdap__hbu = sig.args
    if pxp__zdo != wdap__hbu:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
