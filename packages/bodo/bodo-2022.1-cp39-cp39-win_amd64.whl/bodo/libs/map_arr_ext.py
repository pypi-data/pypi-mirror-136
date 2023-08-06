"""Array implementation for map values.
Corresponds to Spark's MapType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Map arrays: https://github.com/apache/arrow/blob/master/format/Schema.fbs

The implementation uses an array(struct) array underneath similar to Spark and Arrow.
For example: [{1: 2.1, 3: 1.1}, {5: -1.0}]
[[{"key": 1, "value" 2.1}, {"key": 3, "value": 1.1}], [{"key": 5, "value": -1.0}]]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, _get_array_item_arr_payload, offset_type
from bodo.libs.struct_arr_ext import StructArrayType, _get_struct_arr_payload
from bodo.utils.cg_helpers import dict_keys, dict_merge_from_seq2, dict_values, gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit
from bodo.utils.typing import BodoError
from bodo.libs import array_ext, hdist
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('map_array_from_sequence', array_ext.map_array_from_sequence)
ll.add_symbol('np_array_from_map_array', array_ext.np_array_from_map_array)


class MapArrayType(types.ArrayCompatible):

    def __init__(self, key_arr_type, value_arr_type):
        self.key_arr_type = key_arr_type
        self.value_arr_type = value_arr_type
        super(MapArrayType, self).__init__(name='MapArrayType({}, {})'.
            format(key_arr_type, value_arr_type))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.DictType(self.key_arr_type.dtype, self.value_arr_type.
            dtype)

    def copy(self):
        return MapArrayType(self.key_arr_type, self.value_arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_map_arr_data_type(map_type):
    gnxj__pow = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(gnxj__pow)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rhseo__bzgh = _get_map_arr_data_type(fe_type)
        tnzos__sutnl = [('data', rhseo__bzgh)]
        models.StructModel.__init__(self, dmm, fe_type, tnzos__sutnl)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    fezcw__iaraf = all(isinstance(ukb__xnw, types.Array) and ukb__xnw.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        ukb__xnw in (typ.key_arr_type, typ.value_arr_type))
    if fezcw__iaraf:
        tij__opz = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        wspk__fgexe = cgutils.get_or_insert_function(c.builder.module,
            tij__opz, name='count_total_elems_list_array')
        nlso__gtbz = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            wspk__fgexe, [val])])
    else:
        nlso__gtbz = get_array_elem_counts(c, c.builder, c.context, val, typ)
    rhseo__bzgh = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, rhseo__bzgh,
        nlso__gtbz, c)
    mgq__ckoqo = _get_array_item_arr_payload(c.context, c.builder,
        rhseo__bzgh, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, mgq__ckoqo.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, mgq__ckoqo.offsets).data
    zrlh__rhz = _get_struct_arr_payload(c.context, c.builder, rhseo__bzgh.
        dtype, mgq__ckoqo.data)
    key_arr = c.builder.extract_value(zrlh__rhz.data, 0)
    value_arr = c.builder.extract_value(zrlh__rhz.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    wfofw__dapz, yttqy__poh = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [zrlh__rhz.null_bitmap])
    if fezcw__iaraf:
        uxx__qfxqy = c.context.make_array(rhseo__bzgh.dtype.data[0])(c.
            context, c.builder, key_arr).data
        kvh__vvply = c.context.make_array(rhseo__bzgh.dtype.data[1])(c.
            context, c.builder, value_arr).data
        tij__opz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        sjqd__hkqkf = cgutils.get_or_insert_function(c.builder.module,
            tij__opz, name='map_array_from_sequence')
        ylc__ubuh = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        uwmn__qyuu = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        c.builder.call(sjqd__hkqkf, [val, c.builder.bitcast(uxx__qfxqy, lir
            .IntType(8).as_pointer()), c.builder.bitcast(kvh__vvply, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), ylc__ubuh), lir.Constant(lir.IntType(
            32), uwmn__qyuu)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    jhkx__kyxzb = c.context.make_helper(c.builder, typ)
    jhkx__kyxzb.data = data_arr
    htmc__sknq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jhkx__kyxzb._getvalue(), is_error=htmc__sknq)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    bkb__hlq = context.insert_const_string(builder.module, 'pandas')
    xpse__hes = c.pyapi.import_module_noblock(bkb__hlq)
    gozem__sclj = c.pyapi.object_getattr_string(xpse__hes, 'NA')
    dri__btezn = c.context.get_constant(offset_type, 0)
    builder.store(dri__btezn, offsets_ptr)
    sfi__zwxs = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as loop:
        knt__vnz = loop.index
        item_ind = builder.load(sfi__zwxs)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [knt__vnz]))
        xvv__irqh = seq_getitem(builder, context, val, knt__vnz)
        set_bitmap_bit(builder, null_bitmap_ptr, knt__vnz, 0)
        shyw__gvmo = is_na_value(builder, context, xvv__irqh, gozem__sclj)
        jqhr__cubwb = builder.icmp_unsigned('!=', shyw__gvmo, lir.Constant(
            shyw__gvmo.type, 1))
        with builder.if_then(jqhr__cubwb):
            set_bitmap_bit(builder, null_bitmap_ptr, knt__vnz, 1)
            hne__klox = dict_keys(builder, context, xvv__irqh)
            oup__nyev = dict_values(builder, context, xvv__irqh)
            n_items = bodo.utils.utils.object_length(c, hne__klox)
            _unbox_array_item_array_copy_data(typ.key_arr_type, hne__klox,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type, oup__nyev,
                c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), sfi__zwxs)
            c.pyapi.decref(hne__klox)
            c.pyapi.decref(oup__nyev)
        c.pyapi.decref(xvv__irqh)
    builder.store(builder.trunc(builder.load(sfi__zwxs), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(xpse__hes)
    c.pyapi.decref(gozem__sclj)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    jhkx__kyxzb = c.context.make_helper(c.builder, typ, val)
    data_arr = jhkx__kyxzb.data
    rhseo__bzgh = _get_map_arr_data_type(typ)
    mgq__ckoqo = _get_array_item_arr_payload(c.context, c.builder,
        rhseo__bzgh, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, mgq__ckoqo.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, mgq__ckoqo.offsets).data
    zrlh__rhz = _get_struct_arr_payload(c.context, c.builder, rhseo__bzgh.
        dtype, mgq__ckoqo.data)
    key_arr = c.builder.extract_value(zrlh__rhz.data, 0)
    value_arr = c.builder.extract_value(zrlh__rhz.data, 1)
    if all(isinstance(ukb__xnw, types.Array) and ukb__xnw.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type) for ukb__xnw in
        (typ.key_arr_type, typ.value_arr_type)):
        uxx__qfxqy = c.context.make_array(rhseo__bzgh.dtype.data[0])(c.
            context, c.builder, key_arr).data
        kvh__vvply = c.context.make_array(rhseo__bzgh.dtype.data[1])(c.
            context, c.builder, value_arr).data
        tij__opz = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        zbir__kgvcf = cgutils.get_or_insert_function(c.builder.module,
            tij__opz, name='np_array_from_map_array')
        ylc__ubuh = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        uwmn__qyuu = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        arr = c.builder.call(zbir__kgvcf, [mgq__ckoqo.n_arrays, c.builder.
            bitcast(uxx__qfxqy, lir.IntType(8).as_pointer()), c.builder.
            bitcast(kvh__vvply, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), ylc__ubuh), lir.
            Constant(lir.IntType(32), uwmn__qyuu)])
    else:
        arr = _box_map_array_generic(typ, c, mgq__ckoqo.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    bkb__hlq = context.insert_const_string(builder.module, 'numpy')
    pnrzi__rlvlf = c.pyapi.import_module_noblock(bkb__hlq)
    cij__zfn = c.pyapi.object_getattr_string(pnrzi__rlvlf, 'object_')
    paocu__rcenk = c.pyapi.long_from_longlong(n_maps)
    rdqmm__jzwu = c.pyapi.call_method(pnrzi__rlvlf, 'ndarray', (
        paocu__rcenk, cij__zfn))
    fmp__japz = c.pyapi.object_getattr_string(pnrzi__rlvlf, 'nan')
    dtpf__pzxbu = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    sfi__zwxs = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (64), 0))
    with cgutils.for_range(builder, n_maps) as loop:
        gxyl__lklz = loop.index
        pyarray_setitem(builder, context, rdqmm__jzwu, gxyl__lklz, fmp__japz)
        cdlfu__xyo = get_bitmap_bit(builder, null_bitmap_ptr, gxyl__lklz)
        hxt__cov = builder.icmp_unsigned('!=', cdlfu__xyo, lir.Constant(lir
            .IntType(8), 0))
        with builder.if_then(hxt__cov):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(gxyl__lklz, lir.Constant(
                gxyl__lklz.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [gxyl__lklz]))), lir.IntType(64))
            item_ind = builder.load(sfi__zwxs)
            xvv__irqh = c.pyapi.dict_new()
            vvd__mhkj = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            wfofw__dapz, dkjcn__yktr = c.pyapi.call_jit_code(vvd__mhkj, typ
                .key_arr_type(typ.key_arr_type, types.int64, types.int64),
                [key_arr, item_ind, n_items])
            wfofw__dapz, wqdjz__hraq = c.pyapi.call_jit_code(vvd__mhkj, typ
                .value_arr_type(typ.value_arr_type, types.int64, types.
                int64), [value_arr, item_ind, n_items])
            furjm__yfrnd = c.pyapi.from_native_value(typ.key_arr_type,
                dkjcn__yktr, c.env_manager)
            uypga__wajq = c.pyapi.from_native_value(typ.value_arr_type,
                wqdjz__hraq, c.env_manager)
            yse__khg = c.pyapi.call_function_objargs(dtpf__pzxbu, (
                furjm__yfrnd, uypga__wajq))
            dict_merge_from_seq2(builder, context, xvv__irqh, yse__khg)
            builder.store(builder.add(item_ind, n_items), sfi__zwxs)
            pyarray_setitem(builder, context, rdqmm__jzwu, gxyl__lklz,
                xvv__irqh)
            c.pyapi.decref(yse__khg)
            c.pyapi.decref(furjm__yfrnd)
            c.pyapi.decref(uypga__wajq)
            c.pyapi.decref(xvv__irqh)
    c.pyapi.decref(dtpf__pzxbu)
    c.pyapi.decref(pnrzi__rlvlf)
    c.pyapi.decref(cij__zfn)
    c.pyapi.decref(paocu__rcenk)
    c.pyapi.decref(fmp__japz)
    return rdqmm__jzwu


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    jhkx__kyxzb = context.make_helper(builder, sig.return_type)
    jhkx__kyxzb.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return jhkx__kyxzb._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    ipa__zdl = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return ipa__zdl(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    naea__squfa = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(naea__squfa)


def pre_alloc_map_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_map_arr_ext_pre_alloc_map_array
    ) = pre_alloc_map_array_equiv


@overload(len, no_unliteral=True)
def overload_map_arr_len(A):
    if isinstance(A, MapArrayType):
        return lambda A: len(A._data)


@overload_attribute(MapArrayType, 'shape')
def overload_map_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(MapArrayType, 'dtype')
def overload_map_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(MapArrayType, 'ndim')
def overload_map_arr_ndim(A):
    return lambda A: 1


@overload_attribute(MapArrayType, 'nbytes')
def overload_map_arr_nbytes(A):
    return lambda A: A._data.nbytes


@overload_method(MapArrayType, 'copy')
def overload_map_arr_copy(A):
    return lambda A: init_map_arr(A._data.copy())


@overload(operator.setitem, no_unliteral=True)
def map_arr_setitem(arr, ind, val):
    if not isinstance(arr, MapArrayType):
        return
    btkl__zvnow = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            arr__vgur = val.keys()
            uvuqc__gbqcu = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), btkl__zvnow, ('key', 'value'))
            for xvr__axu, ovi__kseeb in enumerate(arr__vgur):
                uvuqc__gbqcu[xvr__axu] = bodo.libs.struct_arr_ext.init_struct((
                    ovi__kseeb, val[ovi__kseeb]), ('key', 'value'))
            arr._data[ind] = uvuqc__gbqcu
        return map_arr_setitem_impl
    raise BodoError(
        'operator.setitem with MapArrays is only supported with an integer index.'
        )


@overload(operator.getitem, no_unliteral=True)
def map_arr_getitem(arr, ind):
    if not isinstance(arr, MapArrayType):
        return
    if isinstance(ind, types.Integer):

        def map_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            fppg__ipj = dict()
            gvma__gylrl = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            uvuqc__gbqcu = bodo.libs.array_item_arr_ext.get_data(arr._data)
            lwngh__cnh, eotqt__mwepu = bodo.libs.struct_arr_ext.get_data(
                uvuqc__gbqcu)
            jyk__pfwhw = gvma__gylrl[ind]
            qolj__pqwfq = gvma__gylrl[ind + 1]
            for xvr__axu in range(jyk__pfwhw, qolj__pqwfq):
                fppg__ipj[lwngh__cnh[xvr__axu]] = eotqt__mwepu[xvr__axu]
            return fppg__ipj
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
