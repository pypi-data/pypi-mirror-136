"""Array implementation for structs of values.
Corresponds to Spark's StructType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Struct arrays: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in contiguous data arrays; one array per field. For example:
A:             ["AA", "B", "C"]
B:             [1, 2, 4]
"""
import operator
import llvmlite.binding as ll
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
from numba.typed.typedobjectutils import _cast
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.typing import BodoError, dtype_to_array_type, get_overload_const_int, get_overload_const_str, is_list_like_index_type, is_overload_constant_int, is_overload_constant_str, is_overload_none
ll.add_symbol('struct_array_from_sequence', array_ext.
    struct_array_from_sequence)
ll.add_symbol('np_array_from_struct_array', array_ext.
    np_array_from_struct_array)


class StructArrayType(types.ArrayCompatible):

    def __init__(self, data, names=None):
        assert isinstance(data, tuple) and len(data) > 0 and all(bodo.utils
            .utils.is_array_typ(zhqhm__wfb, False) for zhqhm__wfb in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(zhqhm__wfb,
                str) for zhqhm__wfb in names) and len(names) == len(data)
        else:
            names = tuple('f{}'.format(i) for i in range(len(data)))
        self.data = data
        self.names = names
        super(StructArrayType, self).__init__(name=
            'StructArrayType({}, {})'.format(data, names))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return StructType(tuple(ilmwr__uqi.dtype for ilmwr__uqi in self.
            data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(zhqhm__wfb) for zhqhm__wfb in d.keys())
        data = tuple(dtype_to_array_type(ilmwr__uqi) for ilmwr__uqi in d.
            values())
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(zhqhm__wfb, False) for zhqhm__wfb in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        htm__qtn = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, htm__qtn)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        htm__qtn = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, htm__qtn)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    oziye__psth = builder.module
    rhi__itq = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    bgqs__uvnjw = cgutils.get_or_insert_function(oziye__psth, rhi__itq,
        name='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not bgqs__uvnjw.is_declaration:
        return bgqs__uvnjw
    bgqs__uvnjw.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(bgqs__uvnjw.append_basic_block())
    etjt__kdx = bgqs__uvnjw.args[0]
    piem__ultf = context.get_value_type(payload_type).as_pointer()
    jwr__ssbq = builder.bitcast(etjt__kdx, piem__ultf)
    hwars__rxb = context.make_helper(builder, payload_type, ref=jwr__ssbq)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), hwars__rxb.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        hwars__rxb.null_bitmap)
    builder.ret_void()
    return bgqs__uvnjw


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    phfh__rnbq = context.get_value_type(payload_type)
    emmd__xgxg = context.get_abi_sizeof(phfh__rnbq)
    jdfqs__wtond = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    udfm__sfdjb = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, emmd__xgxg), jdfqs__wtond)
    oux__nxj = context.nrt.meminfo_data(builder, udfm__sfdjb)
    ika__uxwg = builder.bitcast(oux__nxj, phfh__rnbq.as_pointer())
    hwars__rxb = cgutils.create_struct_proxy(payload_type)(context, builder)
    inds__dvm = []
    rdly__dlsk = 0
    for arr_typ in struct_arr_type.data:
        twuhx__yks = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        wmvm__awj = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(rdly__dlsk, rdly__dlsk +
            twuhx__yks)])
        arr = gen_allocate_array(context, builder, arr_typ, wmvm__awj, c)
        inds__dvm.append(arr)
        rdly__dlsk += twuhx__yks
    hwars__rxb.data = cgutils.pack_array(builder, inds__dvm
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, inds__dvm)
    oma__tiqlh = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    qtpnw__fdw = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [oma__tiqlh])
    null_bitmap_ptr = qtpnw__fdw.data
    hwars__rxb.null_bitmap = qtpnw__fdw._getvalue()
    builder.store(hwars__rxb._getvalue(), ika__uxwg)
    return udfm__sfdjb, hwars__rxb.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    wnv__dlsa = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        svhxd__psgc = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            svhxd__psgc)
        wnv__dlsa.append(arr.data)
    atez__keemi = cgutils.pack_array(c.builder, wnv__dlsa
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, wnv__dlsa)
    wsmg__wfoc = cgutils.alloca_once_value(c.builder, atez__keemi)
    syl__koje = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(zhqhm__wfb.dtype)) for zhqhm__wfb in data_typ]
    nocxs__ghtr = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c
        .builder, syl__koje))
    xik__skqm = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, zhqhm__wfb) for zhqhm__wfb in
        names])
    fyma__djrr = cgutils.alloca_once_value(c.builder, xik__skqm)
    return wsmg__wfoc, nocxs__ghtr, fyma__djrr


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    cmj__qnejw = all(isinstance(ilmwr__uqi, types.Array) and ilmwr__uqi.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for ilmwr__uqi in typ.data)
    if cmj__qnejw:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        bjgt__eyj = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            bjgt__eyj, i) for i in range(1, bjgt__eyj.type.count)], lir.
            IntType(64))
    udfm__sfdjb, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if cmj__qnejw:
        wsmg__wfoc, nocxs__ghtr, fyma__djrr = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        rhi__itq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        bgqs__uvnjw = cgutils.get_or_insert_function(c.builder.module,
            rhi__itq, name='struct_array_from_sequence')
        c.builder.call(bgqs__uvnjw, [val, c.context.get_constant(types.
            int32, len(typ.data)), c.builder.bitcast(wsmg__wfoc, lir.
            IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            nocxs__ghtr, lir.IntType(8).as_pointer()), c.builder.bitcast(
            fyma__djrr, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    rdc__xvd = c.context.make_helper(c.builder, typ)
    rdc__xvd.meminfo = udfm__sfdjb
    cqku__rwjf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(rdc__xvd._getvalue(), is_error=cqku__rwjf)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    rmq__kpohb = context.insert_const_string(builder.module, 'pandas')
    bfty__lqfmo = c.pyapi.import_module_noblock(rmq__kpohb)
    csmf__kusi = c.pyapi.object_getattr_string(bfty__lqfmo, 'NA')
    with cgutils.for_range(builder, n_structs) as loop:
        uxdf__aiiio = loop.index
        vfaim__cmep = seq_getitem(builder, context, val, uxdf__aiiio)
        set_bitmap_bit(builder, null_bitmap_ptr, uxdf__aiiio, 0)
        for mzvx__nytk in range(len(typ.data)):
            arr_typ = typ.data[mzvx__nytk]
            data_arr = builder.extract_value(data_tup, mzvx__nytk)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            gzv__wccje, aqc__iky = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, uxdf__aiiio])
        wesxf__ngl = is_na_value(builder, context, vfaim__cmep, csmf__kusi)
        miv__dbk = builder.icmp_unsigned('!=', wesxf__ngl, lir.Constant(
            wesxf__ngl.type, 1))
        with builder.if_then(miv__dbk):
            set_bitmap_bit(builder, null_bitmap_ptr, uxdf__aiiio, 1)
            for mzvx__nytk in range(len(typ.data)):
                arr_typ = typ.data[mzvx__nytk]
                if is_tuple_array:
                    fado__rxefo = c.pyapi.tuple_getitem(vfaim__cmep, mzvx__nytk
                        )
                else:
                    fado__rxefo = c.pyapi.dict_getitem_string(vfaim__cmep,
                        typ.names[mzvx__nytk])
                wesxf__ngl = is_na_value(builder, context, fado__rxefo,
                    csmf__kusi)
                miv__dbk = builder.icmp_unsigned('!=', wesxf__ngl, lir.
                    Constant(wesxf__ngl.type, 1))
                with builder.if_then(miv__dbk):
                    fado__rxefo = to_arr_obj_if_list_obj(c, context,
                        builder, fado__rxefo, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        fado__rxefo).value
                    data_arr = builder.extract_value(data_tup, mzvx__nytk)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    gzv__wccje, aqc__iky = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, uxdf__aiiio, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(vfaim__cmep)
    c.pyapi.decref(bfty__lqfmo)
    c.pyapi.decref(csmf__kusi)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    rdc__xvd = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    oux__nxj = context.nrt.meminfo_data(builder, rdc__xvd.meminfo)
    ika__uxwg = builder.bitcast(oux__nxj, context.get_value_type(
        payload_type).as_pointer())
    hwars__rxb = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(ika__uxwg))
    return hwars__rxb


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    hwars__rxb = _get_struct_arr_payload(c.context, c.builder, typ, val)
    gzv__wccje, length = c.pyapi.call_jit_code(lambda A: len(A), types.
        int64(typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), hwars__rxb.null_bitmap).data
    cmj__qnejw = all(isinstance(ilmwr__uqi, types.Array) and ilmwr__uqi.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for ilmwr__uqi in typ.data)
    if cmj__qnejw:
        wsmg__wfoc, nocxs__ghtr, fyma__djrr = _get_C_API_ptrs(c, hwars__rxb
            .data, typ.data, typ.names)
        rhi__itq = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        gjv__bpgum = cgutils.get_or_insert_function(c.builder.module,
            rhi__itq, name='np_array_from_struct_array')
        arr = c.builder.call(gjv__bpgum, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(wsmg__wfoc, lir.
            IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            nocxs__ghtr, lir.IntType(8).as_pointer()), c.builder.bitcast(
            fyma__djrr, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, hwars__rxb.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    rmq__kpohb = context.insert_const_string(builder.module, 'numpy')
    trqbq__tmq = c.pyapi.import_module_noblock(rmq__kpohb)
    gph__swjk = c.pyapi.object_getattr_string(trqbq__tmq, 'object_')
    jlt__hfmjj = c.pyapi.long_from_longlong(length)
    hps__olby = c.pyapi.call_method(trqbq__tmq, 'ndarray', (jlt__hfmjj,
        gph__swjk))
    yjrfe__apbx = c.pyapi.object_getattr_string(trqbq__tmq, 'nan')
    with cgutils.for_range(builder, length) as loop:
        uxdf__aiiio = loop.index
        pyarray_setitem(builder, context, hps__olby, uxdf__aiiio, yjrfe__apbx)
        qky__onv = get_bitmap_bit(builder, null_bitmap_ptr, uxdf__aiiio)
        bsz__ike = builder.icmp_unsigned('!=', qky__onv, lir.Constant(lir.
            IntType(8), 0))
        with builder.if_then(bsz__ike):
            if is_tuple_array:
                vfaim__cmep = c.pyapi.tuple_new(len(typ.data))
            else:
                vfaim__cmep = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(yjrfe__apbx)
                    c.pyapi.tuple_setitem(vfaim__cmep, i, yjrfe__apbx)
                else:
                    c.pyapi.dict_setitem_string(vfaim__cmep, typ.names[i],
                        yjrfe__apbx)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                gzv__wccje, pkl__trmi = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, uxdf__aiiio])
                with builder.if_then(pkl__trmi):
                    gzv__wccje, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, uxdf__aiiio])
                    jxp__sza = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(vfaim__cmep, i, jxp__sza)
                    else:
                        c.pyapi.dict_setitem_string(vfaim__cmep, typ.names[
                            i], jxp__sza)
                        c.pyapi.decref(jxp__sza)
            pyarray_setitem(builder, context, hps__olby, uxdf__aiiio,
                vfaim__cmep)
            c.pyapi.decref(vfaim__cmep)
    c.pyapi.decref(trqbq__tmq)
    c.pyapi.decref(gph__swjk)
    c.pyapi.decref(jlt__hfmjj)
    c.pyapi.decref(yjrfe__apbx)
    return hps__olby


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    csaln__wyamy = bodo.utils.transform.get_type_alloc_counts(struct_arr_type
        ) - 1
    if csaln__wyamy == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for icwc__rxtl in range(csaln__wyamy)])
    elif nested_counts_type.count < csaln__wyamy:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for icwc__rxtl in range(
            csaln__wyamy - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(ilmwr__uqi) for ilmwr__uqi in
            names_typ.types)
    kql__ihxc = tuple(ilmwr__uqi.instance_type for ilmwr__uqi in dtypes_typ
        .types)
    struct_arr_type = StructArrayType(kql__ihxc, names)

    def codegen(context, builder, sig, args):
        zsckc__dna, nested_counts, icwc__rxtl, icwc__rxtl = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        udfm__sfdjb, icwc__rxtl, icwc__rxtl = construct_struct_array(context,
            builder, struct_arr_type, zsckc__dna, nested_counts)
        rdc__xvd = context.make_helper(builder, struct_arr_type)
        rdc__xvd.meminfo = udfm__sfdjb
        return rdc__xvd._getvalue()
    return struct_arr_type(num_structs_typ, nested_counts_typ, dtypes_typ,
        names_typ), codegen


def pre_alloc_struct_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_struct_arr_ext_pre_alloc_struct_array
    ) = pre_alloc_struct_array_equiv


class StructType(types.Type):

    def __init__(self, data, names):
        assert isinstance(data, tuple) and len(data) > 0
        assert isinstance(names, tuple) and all(isinstance(zhqhm__wfb, str) for
            zhqhm__wfb in names) and len(names) == len(data)
        self.data = data
        self.names = names
        super(StructType, self).__init__(name='StructType({}, {})'.format(
            data, names))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple)
        self.data = data
        super(StructPayloadType, self).__init__(name=
            'StructPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructPayloadType)
class StructPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        htm__qtn = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, htm__qtn)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        htm__qtn = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, htm__qtn)


def define_struct_dtor(context, builder, struct_type, payload_type):
    oziye__psth = builder.module
    rhi__itq = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    bgqs__uvnjw = cgutils.get_or_insert_function(oziye__psth, rhi__itq,
        name='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not bgqs__uvnjw.is_declaration:
        return bgqs__uvnjw
    bgqs__uvnjw.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(bgqs__uvnjw.append_basic_block())
    etjt__kdx = bgqs__uvnjw.args[0]
    piem__ultf = context.get_value_type(payload_type).as_pointer()
    jwr__ssbq = builder.bitcast(etjt__kdx, piem__ultf)
    hwars__rxb = context.make_helper(builder, payload_type, ref=jwr__ssbq)
    for i in range(len(struct_type.data)):
        kfmxt__jejpa = builder.extract_value(hwars__rxb.null_bitmap, i)
        bsz__ike = builder.icmp_unsigned('==', kfmxt__jejpa, lir.Constant(
            kfmxt__jejpa.type, 1))
        with builder.if_then(bsz__ike):
            val = builder.extract_value(hwars__rxb.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return bgqs__uvnjw


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    oux__nxj = context.nrt.meminfo_data(builder, struct.meminfo)
    ika__uxwg = builder.bitcast(oux__nxj, context.get_value_type(
        payload_type).as_pointer())
    hwars__rxb = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(ika__uxwg))
    return hwars__rxb, ika__uxwg


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    rmq__kpohb = context.insert_const_string(builder.module, 'pandas')
    bfty__lqfmo = c.pyapi.import_module_noblock(rmq__kpohb)
    csmf__kusi = c.pyapi.object_getattr_string(bfty__lqfmo, 'NA')
    qorzw__avtw = []
    nulls = []
    for i, ilmwr__uqi in enumerate(typ.data):
        jxp__sza = c.pyapi.dict_getitem_string(val, typ.names[i])
        ypj__amknb = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        wenk__caf = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(ilmwr__uqi)))
        wesxf__ngl = is_na_value(builder, context, jxp__sza, csmf__kusi)
        bsz__ike = builder.icmp_unsigned('!=', wesxf__ngl, lir.Constant(
            wesxf__ngl.type, 1))
        with builder.if_then(bsz__ike):
            builder.store(context.get_constant(types.uint8, 1), ypj__amknb)
            field_val = c.pyapi.to_native_value(ilmwr__uqi, jxp__sza).value
            builder.store(field_val, wenk__caf)
        qorzw__avtw.append(builder.load(wenk__caf))
        nulls.append(builder.load(ypj__amknb))
    c.pyapi.decref(bfty__lqfmo)
    c.pyapi.decref(csmf__kusi)
    udfm__sfdjb = construct_struct(context, builder, typ, qorzw__avtw, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = udfm__sfdjb
    cqku__rwjf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=cqku__rwjf)


@box(StructType)
def box_struct(typ, val, c):
    rasyj__eun = c.pyapi.dict_new(len(typ.data))
    hwars__rxb, icwc__rxtl = _get_struct_payload(c.context, c.builder, typ, val
        )
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(rasyj__eun, typ.names[i], c.pyapi.
            borrow_none())
        kfmxt__jejpa = c.builder.extract_value(hwars__rxb.null_bitmap, i)
        bsz__ike = c.builder.icmp_unsigned('==', kfmxt__jejpa, lir.Constant
            (kfmxt__jejpa.type, 1))
        with c.builder.if_then(bsz__ike):
            sujp__mgstn = c.builder.extract_value(hwars__rxb.data, i)
            c.context.nrt.incref(c.builder, val_typ, sujp__mgstn)
            fado__rxefo = c.pyapi.from_native_value(val_typ, sujp__mgstn, c
                .env_manager)
            c.pyapi.dict_setitem_string(rasyj__eun, typ.names[i], fado__rxefo)
            c.pyapi.decref(fado__rxefo)
    c.context.nrt.decref(c.builder, typ, val)
    return rasyj__eun


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(ilmwr__uqi) for ilmwr__uqi in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, zun__hplzx = args
        payload_type = StructPayloadType(struct_type.data)
        phfh__rnbq = context.get_value_type(payload_type)
        emmd__xgxg = context.get_abi_sizeof(phfh__rnbq)
        jdfqs__wtond = define_struct_dtor(context, builder, struct_type,
            payload_type)
        udfm__sfdjb = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, emmd__xgxg), jdfqs__wtond)
        oux__nxj = context.nrt.meminfo_data(builder, udfm__sfdjb)
        ika__uxwg = builder.bitcast(oux__nxj, phfh__rnbq.as_pointer())
        hwars__rxb = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        hwars__rxb.data = data
        hwars__rxb.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for icwc__rxtl in range(len(
            data_typ.types))])
        builder.store(hwars__rxb._getvalue(), ika__uxwg)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = udfm__sfdjb
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        hwars__rxb, icwc__rxtl = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            hwars__rxb.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        hwars__rxb, icwc__rxtl = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            hwars__rxb.null_bitmap)
    bejp__auqmf = types.UniTuple(types.int8, len(struct_typ.data))
    return bejp__auqmf(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, icwc__rxtl, val = args
        hwars__rxb, ika__uxwg = _get_struct_payload(context, builder,
            struct_typ, struct)
        kgmg__tfcx = hwars__rxb.data
        dwbp__nabp = builder.insert_value(kgmg__tfcx, val, field_ind)
        njyco__izc = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, njyco__izc, kgmg__tfcx)
        context.nrt.incref(builder, njyco__izc, dwbp__nabp)
        hwars__rxb.data = dwbp__nabp
        builder.store(hwars__rxb._getvalue(), ika__uxwg)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    rhdfj__fbph = get_overload_const_str(ind)
    if rhdfj__fbph not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            rhdfj__fbph, struct))
    return struct.names.index(rhdfj__fbph)


def is_field_value_null(s, field_name):
    pass


@overload(is_field_value_null, no_unliteral=True)
def overload_is_field_value_null(s, field_name):
    field_ind = _get_struct_field_ind(s, field_name, 'element access (getitem)'
        )
    return lambda s, field_name: get_struct_null_bitmap(s)[field_ind] == 0


@overload(operator.getitem, no_unliteral=True)
def struct_getitem(struct, ind):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'element access (getitem)')
    return lambda struct, ind: get_struct_data(struct)[field_ind]


@overload(operator.setitem, no_unliteral=True)
def struct_setitem(struct, ind, val):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'item assignment (setitem)')
    field_typ = struct.data[field_ind]
    return lambda struct, ind, val: set_struct_data(struct, field_ind,
        _cast(val, field_typ))


@overload(len, no_unliteral=True)
def overload_struct_arr_len(struct):
    if isinstance(struct, StructType):
        num_fields = len(struct.data)
        return lambda struct: num_fields


def construct_struct(context, builder, struct_type, values, nulls):
    payload_type = StructPayloadType(struct_type.data)
    phfh__rnbq = context.get_value_type(payload_type)
    emmd__xgxg = context.get_abi_sizeof(phfh__rnbq)
    jdfqs__wtond = define_struct_dtor(context, builder, struct_type,
        payload_type)
    udfm__sfdjb = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, emmd__xgxg), jdfqs__wtond)
    oux__nxj = context.nrt.meminfo_data(builder, udfm__sfdjb)
    ika__uxwg = builder.bitcast(oux__nxj, phfh__rnbq.as_pointer())
    hwars__rxb = cgutils.create_struct_proxy(payload_type)(context, builder)
    hwars__rxb.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    hwars__rxb.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(hwars__rxb._getvalue(), ika__uxwg)
    return udfm__sfdjb


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    sxtt__smscw = tuple(d.dtype for d in struct_arr_typ.data)
    xvmi__osceo = StructType(sxtt__smscw, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        cpex__dbiq, ind = args
        hwars__rxb = _get_struct_arr_payload(context, builder,
            struct_arr_typ, cpex__dbiq)
        qorzw__avtw = []
        tdsk__eax = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            svhxd__psgc = builder.extract_value(hwars__rxb.data, i)
            lel__cgp = context.compile_internal(builder, lambda arr, ind: 
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [
                svhxd__psgc, ind])
            tdsk__eax.append(lel__cgp)
            svfk__xtl = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            bsz__ike = builder.icmp_unsigned('==', lel__cgp, lir.Constant(
                lel__cgp.type, 1))
            with builder.if_then(bsz__ike):
                bpdpc__sikw = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    svhxd__psgc, ind])
                builder.store(bpdpc__sikw, svfk__xtl)
            qorzw__avtw.append(builder.load(svfk__xtl))
        if isinstance(xvmi__osceo, types.DictType):
            jzl__ehwlm = [context.insert_const_string(builder.module,
                ckik__mso) for ckik__mso in struct_arr_typ.names]
            zonxl__bcxy = cgutils.pack_array(builder, qorzw__avtw)
            lxbf__gmpy = cgutils.pack_array(builder, jzl__ehwlm)

            def impl(names, vals):
                d = {}
                for i, ckik__mso in enumerate(names):
                    d[ckik__mso] = vals[i]
                return d
            koir__ngbpv = context.compile_internal(builder, impl,
                xvmi__osceo(types.Tuple(tuple(types.StringLiteral(ckik__mso
                ) for ckik__mso in struct_arr_typ.names)), types.Tuple(
                sxtt__smscw)), [lxbf__gmpy, zonxl__bcxy])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                sxtt__smscw), zonxl__bcxy)
            return koir__ngbpv
        udfm__sfdjb = construct_struct(context, builder, xvmi__osceo,
            qorzw__avtw, tdsk__eax)
        struct = context.make_helper(builder, xvmi__osceo)
        struct.meminfo = udfm__sfdjb
        return struct._getvalue()
    return xvmi__osceo(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        hwars__rxb = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            hwars__rxb.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        hwars__rxb = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            hwars__rxb.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(ilmwr__uqi) for ilmwr__uqi in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, qtpnw__fdw, zun__hplzx = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        phfh__rnbq = context.get_value_type(payload_type)
        emmd__xgxg = context.get_abi_sizeof(phfh__rnbq)
        jdfqs__wtond = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        udfm__sfdjb = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, emmd__xgxg), jdfqs__wtond)
        oux__nxj = context.nrt.meminfo_data(builder, udfm__sfdjb)
        ika__uxwg = builder.bitcast(oux__nxj, phfh__rnbq.as_pointer())
        hwars__rxb = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        hwars__rxb.data = data
        hwars__rxb.null_bitmap = qtpnw__fdw
        builder.store(hwars__rxb._getvalue(), ika__uxwg)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, qtpnw__fdw)
        rdc__xvd = context.make_helper(builder, struct_arr_type)
        rdc__xvd.meminfo = udfm__sfdjb
        return rdc__xvd._getvalue()
    return struct_arr_type(data_typ, null_bitmap_typ, names_typ), codegen


@overload(operator.getitem, no_unliteral=True)
def struct_arr_getitem(arr, ind):
    if not isinstance(arr, StructArrayType):
        return
    if isinstance(ind, types.Integer):

        def struct_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            return struct_array_get_struct(arr, ind)
        return struct_arr_getitem_impl
    wucc__fjldg = len(arr.data)
    pkj__qlj = 'def impl(arr, ind):\n'
    pkj__qlj += '  data = get_data(arr)\n'
    pkj__qlj += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        pkj__qlj += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        pkj__qlj += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        pkj__qlj += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    pkj__qlj += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(wucc__fjldg)), ', '.join("'{}'".format(ckik__mso) for
        ckik__mso in arr.names)))
    ucuxx__foy = {}
    exec(pkj__qlj, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, ucuxx__foy)
    impl = ucuxx__foy['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        wucc__fjldg = len(arr.data)
        pkj__qlj = 'def impl(arr, ind, val):\n'
        pkj__qlj += '  data = get_data(arr)\n'
        pkj__qlj += '  null_bitmap = get_null_bitmap(arr)\n'
        pkj__qlj += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(wucc__fjldg):
            if isinstance(val, StructType):
                pkj__qlj += "  if is_field_value_null(val, '{}'):\n".format(arr
                    .names[i])
                pkj__qlj += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                pkj__qlj += '  else:\n'
                pkj__qlj += "    data[{}][ind] = val['{}']\n".format(i, arr
                    .names[i])
            else:
                pkj__qlj += "  data[{}][ind] = val['{}']\n".format(i, arr.
                    names[i])
        ucuxx__foy = {}
        exec(pkj__qlj, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, ucuxx__foy)
        impl = ucuxx__foy['impl']
        return impl
    if isinstance(ind, types.SliceType):
        wucc__fjldg = len(arr.data)
        pkj__qlj = 'def impl(arr, ind, val):\n'
        pkj__qlj += '  data = get_data(arr)\n'
        pkj__qlj += '  null_bitmap = get_null_bitmap(arr)\n'
        pkj__qlj += '  val_data = get_data(val)\n'
        pkj__qlj += '  val_null_bitmap = get_null_bitmap(val)\n'
        pkj__qlj += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(wucc__fjldg):
            pkj__qlj += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        ucuxx__foy = {}
        exec(pkj__qlj, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, ucuxx__foy)
        impl = ucuxx__foy['impl']
        return impl
    raise BodoError(
        'only setitem with scalar/slice index is currently supported for struct arrays'
        )


@overload(len, no_unliteral=True)
def overload_struct_arr_len(A):
    if isinstance(A, StructArrayType):
        return lambda A: len(get_data(A)[0])


@overload_attribute(StructArrayType, 'shape')
def overload_struct_arr_shape(A):
    return lambda A: (len(get_data(A)[0]),)


@overload_attribute(StructArrayType, 'dtype')
def overload_struct_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(StructArrayType, 'ndim')
def overload_struct_arr_ndim(A):
    return lambda A: 1


@overload_attribute(StructArrayType, 'nbytes')
def overload_struct_arr_nbytes(A):
    pkj__qlj = 'def impl(A):\n'
    pkj__qlj += '  total_nbytes = 0\n'
    pkj__qlj += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        pkj__qlj += f'  total_nbytes += data[{i}].nbytes\n'
    pkj__qlj += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    pkj__qlj += '  return total_nbytes\n'
    ucuxx__foy = {}
    exec(pkj__qlj, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, ucuxx__foy)
    impl = ucuxx__foy['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        qtpnw__fdw = get_null_bitmap(A)
        dzes__hnx = bodo.ir.join.copy_arr_tup(data)
        mqhe__eryy = qtpnw__fdw.copy()
        return init_struct_arr(dzes__hnx, mqhe__eryy, names)
    return copy_impl
