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
    aonyg__wucb = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(aonyg__wucb)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ede__pah = _get_map_arr_data_type(fe_type)
        kyf__rcsor = [('data', ede__pah)]
        models.StructModel.__init__(self, dmm, fe_type, kyf__rcsor)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    ivz__bjtdw = all(isinstance(zbxxl__wwz, types.Array) and zbxxl__wwz.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for zbxxl__wwz in (typ.key_arr_type, typ.
        value_arr_type))
    if ivz__bjtdw:
        vzblp__fsx = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        qlgi__pzwx = cgutils.get_or_insert_function(c.builder.module,
            vzblp__fsx, name='count_total_elems_list_array')
        bhl__tsys = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            qlgi__pzwx, [val])])
    else:
        bhl__tsys = get_array_elem_counts(c, c.builder, c.context, val, typ)
    ede__pah = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, ede__pah, bhl__tsys, c)
    aexa__hakz = _get_array_item_arr_payload(c.context, c.builder, ede__pah,
        data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, aexa__hakz.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, aexa__hakz.offsets).data
    mhtm__ykm = _get_struct_arr_payload(c.context, c.builder, ede__pah.
        dtype, aexa__hakz.data)
    key_arr = c.builder.extract_value(mhtm__ykm.data, 0)
    value_arr = c.builder.extract_value(mhtm__ykm.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    yad__uqd, hgzmx__abvtk = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [mhtm__ykm.null_bitmap])
    if ivz__bjtdw:
        xnm__wio = c.context.make_array(ede__pah.dtype.data[0])(c.context,
            c.builder, key_arr).data
        uydem__vnsyk = c.context.make_array(ede__pah.dtype.data[1])(c.
            context, c.builder, value_arr).data
        vzblp__fsx = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        yfakq__zkyqh = cgutils.get_or_insert_function(c.builder.module,
            vzblp__fsx, name='map_array_from_sequence')
        ayvop__zomyh = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        nkff__wmktc = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype
            )
        c.builder.call(yfakq__zkyqh, [val, c.builder.bitcast(xnm__wio, lir.
            IntType(8).as_pointer()), c.builder.bitcast(uydem__vnsyk, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), ayvop__zomyh), lir.Constant(lir.
            IntType(32), nkff__wmktc)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    vns__drvqh = c.context.make_helper(c.builder, typ)
    vns__drvqh.data = data_arr
    upwhh__plos = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(vns__drvqh._getvalue(), is_error=upwhh__plos)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    nbkt__jscx = context.insert_const_string(builder.module, 'pandas')
    jijq__eifwj = c.pyapi.import_module_noblock(nbkt__jscx)
    rfato__mvhi = c.pyapi.object_getattr_string(jijq__eifwj, 'NA')
    lqb__mjfs = c.context.get_constant(offset_type, 0)
    builder.store(lqb__mjfs, offsets_ptr)
    cfiki__hxbpk = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as loop:
        funh__unnw = loop.index
        item_ind = builder.load(cfiki__hxbpk)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [funh__unnw]))
        mrzay__qeg = seq_getitem(builder, context, val, funh__unnw)
        set_bitmap_bit(builder, null_bitmap_ptr, funh__unnw, 0)
        hylot__popfv = is_na_value(builder, context, mrzay__qeg, rfato__mvhi)
        xbn__kjx = builder.icmp_unsigned('!=', hylot__popfv, lir.Constant(
            hylot__popfv.type, 1))
        with builder.if_then(xbn__kjx):
            set_bitmap_bit(builder, null_bitmap_ptr, funh__unnw, 1)
            krr__toqg = dict_keys(builder, context, mrzay__qeg)
            bzux__hanjx = dict_values(builder, context, mrzay__qeg)
            n_items = bodo.utils.utils.object_length(c, krr__toqg)
            _unbox_array_item_array_copy_data(typ.key_arr_type, krr__toqg,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                bzux__hanjx, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), cfiki__hxbpk)
            c.pyapi.decref(krr__toqg)
            c.pyapi.decref(bzux__hanjx)
        c.pyapi.decref(mrzay__qeg)
    builder.store(builder.trunc(builder.load(cfiki__hxbpk), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(jijq__eifwj)
    c.pyapi.decref(rfato__mvhi)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    vns__drvqh = c.context.make_helper(c.builder, typ, val)
    data_arr = vns__drvqh.data
    ede__pah = _get_map_arr_data_type(typ)
    aexa__hakz = _get_array_item_arr_payload(c.context, c.builder, ede__pah,
        data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, aexa__hakz.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, aexa__hakz.offsets).data
    mhtm__ykm = _get_struct_arr_payload(c.context, c.builder, ede__pah.
        dtype, aexa__hakz.data)
    key_arr = c.builder.extract_value(mhtm__ykm.data, 0)
    value_arr = c.builder.extract_value(mhtm__ykm.data, 1)
    if all(isinstance(zbxxl__wwz, types.Array) and zbxxl__wwz.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type) for
        zbxxl__wwz in (typ.key_arr_type, typ.value_arr_type)):
        xnm__wio = c.context.make_array(ede__pah.dtype.data[0])(c.context,
            c.builder, key_arr).data
        uydem__vnsyk = c.context.make_array(ede__pah.dtype.data[1])(c.
            context, c.builder, value_arr).data
        vzblp__fsx = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        iii__frlyd = cgutils.get_or_insert_function(c.builder.module,
            vzblp__fsx, name='np_array_from_map_array')
        ayvop__zomyh = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        nkff__wmktc = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype
            )
        arr = c.builder.call(iii__frlyd, [aexa__hakz.n_arrays, c.builder.
            bitcast(xnm__wio, lir.IntType(8).as_pointer()), c.builder.
            bitcast(uydem__vnsyk, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), ayvop__zomyh),
            lir.Constant(lir.IntType(32), nkff__wmktc)])
    else:
        arr = _box_map_array_generic(typ, c, aexa__hakz.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    nbkt__jscx = context.insert_const_string(builder.module, 'numpy')
    fnz__thdj = c.pyapi.import_module_noblock(nbkt__jscx)
    cao__iwxa = c.pyapi.object_getattr_string(fnz__thdj, 'object_')
    dggla__gket = c.pyapi.long_from_longlong(n_maps)
    aih__epi = c.pyapi.call_method(fnz__thdj, 'ndarray', (dggla__gket,
        cao__iwxa))
    neamt__uijd = c.pyapi.object_getattr_string(fnz__thdj, 'nan')
    rmru__uqde = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    cfiki__hxbpk = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_maps) as loop:
        dxxq__cvvp = loop.index
        pyarray_setitem(builder, context, aih__epi, dxxq__cvvp, neamt__uijd)
        dfa__tjsx = get_bitmap_bit(builder, null_bitmap_ptr, dxxq__cvvp)
        cpqas__agnb = builder.icmp_unsigned('!=', dfa__tjsx, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(cpqas__agnb):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(dxxq__cvvp, lir.Constant(
                dxxq__cvvp.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [dxxq__cvvp]))), lir.IntType(64))
            item_ind = builder.load(cfiki__hxbpk)
            mrzay__qeg = c.pyapi.dict_new()
            cnoah__hlgi = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            yad__uqd, dzgk__qnolw = c.pyapi.call_jit_code(cnoah__hlgi, typ.
                key_arr_type(typ.key_arr_type, types.int64, types.int64), [
                key_arr, item_ind, n_items])
            yad__uqd, ydh__psmmz = c.pyapi.call_jit_code(cnoah__hlgi, typ.
                value_arr_type(typ.value_arr_type, types.int64, types.int64
                ), [value_arr, item_ind, n_items])
            gmd__nmit = c.pyapi.from_native_value(typ.key_arr_type,
                dzgk__qnolw, c.env_manager)
            ylsrh__jvk = c.pyapi.from_native_value(typ.value_arr_type,
                ydh__psmmz, c.env_manager)
            sal__nqxn = c.pyapi.call_function_objargs(rmru__uqde, (
                gmd__nmit, ylsrh__jvk))
            dict_merge_from_seq2(builder, context, mrzay__qeg, sal__nqxn)
            builder.store(builder.add(item_ind, n_items), cfiki__hxbpk)
            pyarray_setitem(builder, context, aih__epi, dxxq__cvvp, mrzay__qeg)
            c.pyapi.decref(sal__nqxn)
            c.pyapi.decref(gmd__nmit)
            c.pyapi.decref(ylsrh__jvk)
            c.pyapi.decref(mrzay__qeg)
    c.pyapi.decref(rmru__uqde)
    c.pyapi.decref(fnz__thdj)
    c.pyapi.decref(cao__iwxa)
    c.pyapi.decref(dggla__gket)
    c.pyapi.decref(neamt__uijd)
    return aih__epi


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    vns__drvqh = context.make_helper(builder, sig.return_type)
    vns__drvqh.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return vns__drvqh._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    zojol__rtyn = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return zojol__rtyn(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    dfokx__tuk = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(dfokx__tuk)


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
    ubv__fji = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            ygu__vcnyr = val.keys()
            uxxe__npu = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), ubv__fji, ('key', 'value'))
            for smy__nng, kpz__qvesu in enumerate(ygu__vcnyr):
                uxxe__npu[smy__nng] = bodo.libs.struct_arr_ext.init_struct((
                    kpz__qvesu, val[kpz__qvesu]), ('key', 'value'))
            arr._data[ind] = uxxe__npu
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
            tkf__ahnbz = dict()
            lfhd__wpzzn = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            uxxe__npu = bodo.libs.array_item_arr_ext.get_data(arr._data)
            nvspd__cds, rug__hghhq = bodo.libs.struct_arr_ext.get_data(
                uxxe__npu)
            ygl__hculy = lfhd__wpzzn[ind]
            lypi__ogv = lfhd__wpzzn[ind + 1]
            for smy__nng in range(ygl__hculy, lypi__ogv):
                tkf__ahnbz[nvspd__cds[smy__nng]] = rug__hghhq[smy__nng]
            return tkf__ahnbz
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
