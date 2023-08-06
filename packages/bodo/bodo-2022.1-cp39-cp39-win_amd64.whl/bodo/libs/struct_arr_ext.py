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
            .utils.is_array_typ(fkvk__lmq, False) for fkvk__lmq in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(fkvk__lmq,
                str) for fkvk__lmq in names) and len(names) == len(data)
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
        return StructType(tuple(ota__bqn.dtype for ota__bqn in self.data),
            self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(fkvk__lmq) for fkvk__lmq in d.keys())
        data = tuple(dtype_to_array_type(ota__bqn) for ota__bqn in d.values())
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(fkvk__lmq, False) for fkvk__lmq in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xhw__yvzz = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, xhw__yvzz)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        xhw__yvzz = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, xhw__yvzz)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    qmck__gvb = builder.module
    rdxwu__exc = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    zruws__dxq = cgutils.get_or_insert_function(qmck__gvb, rdxwu__exc, name
        ='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not zruws__dxq.is_declaration:
        return zruws__dxq
    zruws__dxq.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(zruws__dxq.append_basic_block())
    suw__zryx = zruws__dxq.args[0]
    abq__ezin = context.get_value_type(payload_type).as_pointer()
    hcacr__xsezl = builder.bitcast(suw__zryx, abq__ezin)
    fdek__aukf = context.make_helper(builder, payload_type, ref=hcacr__xsezl)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), fdek__aukf.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        fdek__aukf.null_bitmap)
    builder.ret_void()
    return zruws__dxq


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    aixd__eip = context.get_value_type(payload_type)
    tpm__hiop = context.get_abi_sizeof(aixd__eip)
    pajgn__xufnu = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    uaai__pzlq = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, tpm__hiop), pajgn__xufnu)
    ccvcz__fbq = context.nrt.meminfo_data(builder, uaai__pzlq)
    omdpn__zew = builder.bitcast(ccvcz__fbq, aixd__eip.as_pointer())
    fdek__aukf = cgutils.create_struct_proxy(payload_type)(context, builder)
    tvf__schha = []
    uyl__rug = 0
    for arr_typ in struct_arr_type.data:
        hvnhb__etgst = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype
            )
        wjhw__glmk = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(uyl__rug, uyl__rug +
            hvnhb__etgst)])
        arr = gen_allocate_array(context, builder, arr_typ, wjhw__glmk, c)
        tvf__schha.append(arr)
        uyl__rug += hvnhb__etgst
    fdek__aukf.data = cgutils.pack_array(builder, tvf__schha
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, tvf__schha)
    nnbah__wxux = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    rtt__rxln = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [nnbah__wxux])
    null_bitmap_ptr = rtt__rxln.data
    fdek__aukf.null_bitmap = rtt__rxln._getvalue()
    builder.store(fdek__aukf._getvalue(), omdpn__zew)
    return uaai__pzlq, fdek__aukf.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    obctk__vrg = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        pogba__tihif = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            pogba__tihif)
        obctk__vrg.append(arr.data)
    nxd__yguic = cgutils.pack_array(c.builder, obctk__vrg
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, obctk__vrg)
    svo__uexrv = cgutils.alloca_once_value(c.builder, nxd__yguic)
    ufn__duaj = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(fkvk__lmq.dtype)) for fkvk__lmq in data_typ]
    lwqin__ygcch = cgutils.alloca_once_value(c.builder, cgutils.pack_array(
        c.builder, ufn__duaj))
    dkedx__phv = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, fkvk__lmq) for fkvk__lmq in
        names])
    lin__rsbd = cgutils.alloca_once_value(c.builder, dkedx__phv)
    return svo__uexrv, lwqin__ygcch, lin__rsbd


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    xeqa__pymxe = all(isinstance(ota__bqn, types.Array) and ota__bqn.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        ota__bqn in typ.data)
    if xeqa__pymxe:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        dxg__rnevj = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            dxg__rnevj, i) for i in range(1, dxg__rnevj.type.count)], lir.
            IntType(64))
    uaai__pzlq, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if xeqa__pymxe:
        svo__uexrv, lwqin__ygcch, lin__rsbd = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        rdxwu__exc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        zruws__dxq = cgutils.get_or_insert_function(c.builder.module,
            rdxwu__exc, name='struct_array_from_sequence')
        c.builder.call(zruws__dxq, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(svo__uexrv, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(lwqin__ygcch,
            lir.IntType(8).as_pointer()), c.builder.bitcast(lin__rsbd, lir.
            IntType(8).as_pointer()), c.context.get_constant(types.bool_,
            is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    gnhy__vbt = c.context.make_helper(c.builder, typ)
    gnhy__vbt.meminfo = uaai__pzlq
    gqay__wokh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(gnhy__vbt._getvalue(), is_error=gqay__wokh)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    wwgaw__dpc = context.insert_const_string(builder.module, 'pandas')
    twlgy__rmq = c.pyapi.import_module_noblock(wwgaw__dpc)
    cxdz__dhsz = c.pyapi.object_getattr_string(twlgy__rmq, 'NA')
    with cgutils.for_range(builder, n_structs) as loop:
        otxps__bfn = loop.index
        ioiu__qjke = seq_getitem(builder, context, val, otxps__bfn)
        set_bitmap_bit(builder, null_bitmap_ptr, otxps__bfn, 0)
        for piatv__csvv in range(len(typ.data)):
            arr_typ = typ.data[piatv__csvv]
            data_arr = builder.extract_value(data_tup, piatv__csvv)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            ctcm__ohwxv, fwfh__wdm = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, otxps__bfn])
        uqzc__zzxd = is_na_value(builder, context, ioiu__qjke, cxdz__dhsz)
        cepjb__txk = builder.icmp_unsigned('!=', uqzc__zzxd, lir.Constant(
            uqzc__zzxd.type, 1))
        with builder.if_then(cepjb__txk):
            set_bitmap_bit(builder, null_bitmap_ptr, otxps__bfn, 1)
            for piatv__csvv in range(len(typ.data)):
                arr_typ = typ.data[piatv__csvv]
                if is_tuple_array:
                    tzria__uyobf = c.pyapi.tuple_getitem(ioiu__qjke,
                        piatv__csvv)
                else:
                    tzria__uyobf = c.pyapi.dict_getitem_string(ioiu__qjke,
                        typ.names[piatv__csvv])
                uqzc__zzxd = is_na_value(builder, context, tzria__uyobf,
                    cxdz__dhsz)
                cepjb__txk = builder.icmp_unsigned('!=', uqzc__zzxd, lir.
                    Constant(uqzc__zzxd.type, 1))
                with builder.if_then(cepjb__txk):
                    tzria__uyobf = to_arr_obj_if_list_obj(c, context,
                        builder, tzria__uyobf, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        tzria__uyobf).value
                    data_arr = builder.extract_value(data_tup, piatv__csvv)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    ctcm__ohwxv, fwfh__wdm = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, otxps__bfn, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(ioiu__qjke)
    c.pyapi.decref(twlgy__rmq)
    c.pyapi.decref(cxdz__dhsz)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    gnhy__vbt = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    ccvcz__fbq = context.nrt.meminfo_data(builder, gnhy__vbt.meminfo)
    omdpn__zew = builder.bitcast(ccvcz__fbq, context.get_value_type(
        payload_type).as_pointer())
    fdek__aukf = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(omdpn__zew))
    return fdek__aukf


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    fdek__aukf = _get_struct_arr_payload(c.context, c.builder, typ, val)
    ctcm__ohwxv, length = c.pyapi.call_jit_code(lambda A: len(A), types.
        int64(typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), fdek__aukf.null_bitmap).data
    xeqa__pymxe = all(isinstance(ota__bqn, types.Array) and ota__bqn.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        ota__bqn in typ.data)
    if xeqa__pymxe:
        svo__uexrv, lwqin__ygcch, lin__rsbd = _get_C_API_ptrs(c, fdek__aukf
            .data, typ.data, typ.names)
        rdxwu__exc = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        xcn__npe = cgutils.get_or_insert_function(c.builder.module,
            rdxwu__exc, name='np_array_from_struct_array')
        arr = c.builder.call(xcn__npe, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(svo__uexrv, lir.
            IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            lwqin__ygcch, lir.IntType(8).as_pointer()), c.builder.bitcast(
            lin__rsbd, lir.IntType(8).as_pointer()), c.context.get_constant
            (types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, fdek__aukf.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    wwgaw__dpc = context.insert_const_string(builder.module, 'numpy')
    coqk__tzkm = c.pyapi.import_module_noblock(wwgaw__dpc)
    qgota__adap = c.pyapi.object_getattr_string(coqk__tzkm, 'object_')
    trfwn__lnqjl = c.pyapi.long_from_longlong(length)
    urezo__dqnt = c.pyapi.call_method(coqk__tzkm, 'ndarray', (trfwn__lnqjl,
        qgota__adap))
    cfgpm__ntsvn = c.pyapi.object_getattr_string(coqk__tzkm, 'nan')
    with cgutils.for_range(builder, length) as loop:
        otxps__bfn = loop.index
        pyarray_setitem(builder, context, urezo__dqnt, otxps__bfn, cfgpm__ntsvn
            )
        mglfl__kel = get_bitmap_bit(builder, null_bitmap_ptr, otxps__bfn)
        jtz__czz = builder.icmp_unsigned('!=', mglfl__kel, lir.Constant(lir
            .IntType(8), 0))
        with builder.if_then(jtz__czz):
            if is_tuple_array:
                ioiu__qjke = c.pyapi.tuple_new(len(typ.data))
            else:
                ioiu__qjke = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(cfgpm__ntsvn)
                    c.pyapi.tuple_setitem(ioiu__qjke, i, cfgpm__ntsvn)
                else:
                    c.pyapi.dict_setitem_string(ioiu__qjke, typ.names[i],
                        cfgpm__ntsvn)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                ctcm__ohwxv, uph__redqd = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, otxps__bfn])
                with builder.if_then(uph__redqd):
                    ctcm__ohwxv, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, otxps__bfn])
                    ivvow__edral = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(ioiu__qjke, i, ivvow__edral)
                    else:
                        c.pyapi.dict_setitem_string(ioiu__qjke, typ.names[i
                            ], ivvow__edral)
                        c.pyapi.decref(ivvow__edral)
            pyarray_setitem(builder, context, urezo__dqnt, otxps__bfn,
                ioiu__qjke)
            c.pyapi.decref(ioiu__qjke)
    c.pyapi.decref(coqk__tzkm)
    c.pyapi.decref(qgota__adap)
    c.pyapi.decref(trfwn__lnqjl)
    c.pyapi.decref(cfgpm__ntsvn)
    return urezo__dqnt


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    mrf__mdhx = bodo.utils.transform.get_type_alloc_counts(struct_arr_type) - 1
    if mrf__mdhx == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for zid__cokto in range(mrf__mdhx)])
    elif nested_counts_type.count < mrf__mdhx:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for zid__cokto in range(
            mrf__mdhx - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(ota__bqn) for ota__bqn in
            names_typ.types)
    iidoo__adb = tuple(ota__bqn.instance_type for ota__bqn in dtypes_typ.types)
    struct_arr_type = StructArrayType(iidoo__adb, names)

    def codegen(context, builder, sig, args):
        ljqw__ujesq, nested_counts, zid__cokto, zid__cokto = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        uaai__pzlq, zid__cokto, zid__cokto = construct_struct_array(context,
            builder, struct_arr_type, ljqw__ujesq, nested_counts)
        gnhy__vbt = context.make_helper(builder, struct_arr_type)
        gnhy__vbt.meminfo = uaai__pzlq
        return gnhy__vbt._getvalue()
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
        assert isinstance(names, tuple) and all(isinstance(fkvk__lmq, str) for
            fkvk__lmq in names) and len(names) == len(data)
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
        xhw__yvzz = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, xhw__yvzz)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        xhw__yvzz = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, xhw__yvzz)


def define_struct_dtor(context, builder, struct_type, payload_type):
    qmck__gvb = builder.module
    rdxwu__exc = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    zruws__dxq = cgutils.get_or_insert_function(qmck__gvb, rdxwu__exc, name
        ='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not zruws__dxq.is_declaration:
        return zruws__dxq
    zruws__dxq.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(zruws__dxq.append_basic_block())
    suw__zryx = zruws__dxq.args[0]
    abq__ezin = context.get_value_type(payload_type).as_pointer()
    hcacr__xsezl = builder.bitcast(suw__zryx, abq__ezin)
    fdek__aukf = context.make_helper(builder, payload_type, ref=hcacr__xsezl)
    for i in range(len(struct_type.data)):
        bfwv__yqahc = builder.extract_value(fdek__aukf.null_bitmap, i)
        jtz__czz = builder.icmp_unsigned('==', bfwv__yqahc, lir.Constant(
            bfwv__yqahc.type, 1))
        with builder.if_then(jtz__czz):
            val = builder.extract_value(fdek__aukf.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return zruws__dxq


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    ccvcz__fbq = context.nrt.meminfo_data(builder, struct.meminfo)
    omdpn__zew = builder.bitcast(ccvcz__fbq, context.get_value_type(
        payload_type).as_pointer())
    fdek__aukf = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(omdpn__zew))
    return fdek__aukf, omdpn__zew


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    wwgaw__dpc = context.insert_const_string(builder.module, 'pandas')
    twlgy__rmq = c.pyapi.import_module_noblock(wwgaw__dpc)
    cxdz__dhsz = c.pyapi.object_getattr_string(twlgy__rmq, 'NA')
    idzah__ntn = []
    nulls = []
    for i, ota__bqn in enumerate(typ.data):
        ivvow__edral = c.pyapi.dict_getitem_string(val, typ.names[i])
        cyevx__tpclz = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        muj__djlc = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(ota__bqn)))
        uqzc__zzxd = is_na_value(builder, context, ivvow__edral, cxdz__dhsz)
        jtz__czz = builder.icmp_unsigned('!=', uqzc__zzxd, lir.Constant(
            uqzc__zzxd.type, 1))
        with builder.if_then(jtz__czz):
            builder.store(context.get_constant(types.uint8, 1), cyevx__tpclz)
            field_val = c.pyapi.to_native_value(ota__bqn, ivvow__edral).value
            builder.store(field_val, muj__djlc)
        idzah__ntn.append(builder.load(muj__djlc))
        nulls.append(builder.load(cyevx__tpclz))
    c.pyapi.decref(twlgy__rmq)
    c.pyapi.decref(cxdz__dhsz)
    uaai__pzlq = construct_struct(context, builder, typ, idzah__ntn, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = uaai__pzlq
    gqay__wokh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=gqay__wokh)


@box(StructType)
def box_struct(typ, val, c):
    lkmbo__asftf = c.pyapi.dict_new(len(typ.data))
    fdek__aukf, zid__cokto = _get_struct_payload(c.context, c.builder, typ, val
        )
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(lkmbo__asftf, typ.names[i], c.pyapi.
            borrow_none())
        bfwv__yqahc = c.builder.extract_value(fdek__aukf.null_bitmap, i)
        jtz__czz = c.builder.icmp_unsigned('==', bfwv__yqahc, lir.Constant(
            bfwv__yqahc.type, 1))
        with c.builder.if_then(jtz__czz):
            qenla__mga = c.builder.extract_value(fdek__aukf.data, i)
            c.context.nrt.incref(c.builder, val_typ, qenla__mga)
            tzria__uyobf = c.pyapi.from_native_value(val_typ, qenla__mga, c
                .env_manager)
            c.pyapi.dict_setitem_string(lkmbo__asftf, typ.names[i],
                tzria__uyobf)
            c.pyapi.decref(tzria__uyobf)
    c.context.nrt.decref(c.builder, typ, val)
    return lkmbo__asftf


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(ota__bqn) for ota__bqn in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, uda__jsies = args
        payload_type = StructPayloadType(struct_type.data)
        aixd__eip = context.get_value_type(payload_type)
        tpm__hiop = context.get_abi_sizeof(aixd__eip)
        pajgn__xufnu = define_struct_dtor(context, builder, struct_type,
            payload_type)
        uaai__pzlq = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, tpm__hiop), pajgn__xufnu)
        ccvcz__fbq = context.nrt.meminfo_data(builder, uaai__pzlq)
        omdpn__zew = builder.bitcast(ccvcz__fbq, aixd__eip.as_pointer())
        fdek__aukf = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        fdek__aukf.data = data
        fdek__aukf.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for zid__cokto in range(len(
            data_typ.types))])
        builder.store(fdek__aukf._getvalue(), omdpn__zew)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = uaai__pzlq
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        fdek__aukf, zid__cokto = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            fdek__aukf.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        fdek__aukf, zid__cokto = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            fdek__aukf.null_bitmap)
    usock__uul = types.UniTuple(types.int8, len(struct_typ.data))
    return usock__uul(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, zid__cokto, val = args
        fdek__aukf, omdpn__zew = _get_struct_payload(context, builder,
            struct_typ, struct)
        focu__rms = fdek__aukf.data
        sdlp__hru = builder.insert_value(focu__rms, val, field_ind)
        wra__lnks = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, wra__lnks, focu__rms)
        context.nrt.incref(builder, wra__lnks, sdlp__hru)
        fdek__aukf.data = sdlp__hru
        builder.store(fdek__aukf._getvalue(), omdpn__zew)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    wxmli__xlht = get_overload_const_str(ind)
    if wxmli__xlht not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            wxmli__xlht, struct))
    return struct.names.index(wxmli__xlht)


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
    aixd__eip = context.get_value_type(payload_type)
    tpm__hiop = context.get_abi_sizeof(aixd__eip)
    pajgn__xufnu = define_struct_dtor(context, builder, struct_type,
        payload_type)
    uaai__pzlq = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, tpm__hiop), pajgn__xufnu)
    ccvcz__fbq = context.nrt.meminfo_data(builder, uaai__pzlq)
    omdpn__zew = builder.bitcast(ccvcz__fbq, aixd__eip.as_pointer())
    fdek__aukf = cgutils.create_struct_proxy(payload_type)(context, builder)
    fdek__aukf.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    fdek__aukf.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(fdek__aukf._getvalue(), omdpn__zew)
    return uaai__pzlq


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    nuhcj__onxdx = tuple(d.dtype for d in struct_arr_typ.data)
    drh__ccp = StructType(nuhcj__onxdx, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        pdg__pxm, ind = args
        fdek__aukf = _get_struct_arr_payload(context, builder,
            struct_arr_typ, pdg__pxm)
        idzah__ntn = []
        mgyn__dpuei = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            pogba__tihif = builder.extract_value(fdek__aukf.data, i)
            aozhj__gmrhb = context.compile_internal(builder, lambda arr,
                ind: np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [
                pogba__tihif, ind])
            mgyn__dpuei.append(aozhj__gmrhb)
            xwzf__rtm = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            jtz__czz = builder.icmp_unsigned('==', aozhj__gmrhb, lir.
                Constant(aozhj__gmrhb.type, 1))
            with builder.if_then(jtz__czz):
                ojn__cpa = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    pogba__tihif, ind])
                builder.store(ojn__cpa, xwzf__rtm)
            idzah__ntn.append(builder.load(xwzf__rtm))
        if isinstance(drh__ccp, types.DictType):
            nvtb__yjyzj = [context.insert_const_string(builder.module,
                wfjs__vph) for wfjs__vph in struct_arr_typ.names]
            wehdz__rrbbp = cgutils.pack_array(builder, idzah__ntn)
            rqstr__etrp = cgutils.pack_array(builder, nvtb__yjyzj)

            def impl(names, vals):
                d = {}
                for i, wfjs__vph in enumerate(names):
                    d[wfjs__vph] = vals[i]
                return d
            edbt__izmzq = context.compile_internal(builder, impl, drh__ccp(
                types.Tuple(tuple(types.StringLiteral(wfjs__vph) for
                wfjs__vph in struct_arr_typ.names)), types.Tuple(
                nuhcj__onxdx)), [rqstr__etrp, wehdz__rrbbp])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                nuhcj__onxdx), wehdz__rrbbp)
            return edbt__izmzq
        uaai__pzlq = construct_struct(context, builder, drh__ccp,
            idzah__ntn, mgyn__dpuei)
        struct = context.make_helper(builder, drh__ccp)
        struct.meminfo = uaai__pzlq
        return struct._getvalue()
    return drh__ccp(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        fdek__aukf = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            fdek__aukf.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        fdek__aukf = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            fdek__aukf.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(ota__bqn) for ota__bqn in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, rtt__rxln, uda__jsies = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        aixd__eip = context.get_value_type(payload_type)
        tpm__hiop = context.get_abi_sizeof(aixd__eip)
        pajgn__xufnu = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        uaai__pzlq = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, tpm__hiop), pajgn__xufnu)
        ccvcz__fbq = context.nrt.meminfo_data(builder, uaai__pzlq)
        omdpn__zew = builder.bitcast(ccvcz__fbq, aixd__eip.as_pointer())
        fdek__aukf = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        fdek__aukf.data = data
        fdek__aukf.null_bitmap = rtt__rxln
        builder.store(fdek__aukf._getvalue(), omdpn__zew)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, rtt__rxln)
        gnhy__vbt = context.make_helper(builder, struct_arr_type)
        gnhy__vbt.meminfo = uaai__pzlq
        return gnhy__vbt._getvalue()
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
    ddzx__tykxd = len(arr.data)
    yprve__yisk = 'def impl(arr, ind):\n'
    yprve__yisk += '  data = get_data(arr)\n'
    yprve__yisk += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        yprve__yisk += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        yprve__yisk += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        yprve__yisk += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    yprve__yisk += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(ddzx__tykxd)), ', '.join("'{}'".format(wfjs__vph) for
        wfjs__vph in arr.names)))
    okuy__qjtvy = {}
    exec(yprve__yisk, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, okuy__qjtvy)
    impl = okuy__qjtvy['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        ddzx__tykxd = len(arr.data)
        yprve__yisk = 'def impl(arr, ind, val):\n'
        yprve__yisk += '  data = get_data(arr)\n'
        yprve__yisk += '  null_bitmap = get_null_bitmap(arr)\n'
        yprve__yisk += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(ddzx__tykxd):
            if isinstance(val, StructType):
                yprve__yisk += "  if is_field_value_null(val, '{}'):\n".format(
                    arr.names[i])
                yprve__yisk += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                yprve__yisk += '  else:\n'
                yprve__yisk += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                yprve__yisk += "  data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
        okuy__qjtvy = {}
        exec(yprve__yisk, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, okuy__qjtvy)
        impl = okuy__qjtvy['impl']
        return impl
    if isinstance(ind, types.SliceType):
        ddzx__tykxd = len(arr.data)
        yprve__yisk = 'def impl(arr, ind, val):\n'
        yprve__yisk += '  data = get_data(arr)\n'
        yprve__yisk += '  null_bitmap = get_null_bitmap(arr)\n'
        yprve__yisk += '  val_data = get_data(val)\n'
        yprve__yisk += '  val_null_bitmap = get_null_bitmap(val)\n'
        yprve__yisk += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(ddzx__tykxd):
            yprve__yisk += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        okuy__qjtvy = {}
        exec(yprve__yisk, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, okuy__qjtvy)
        impl = okuy__qjtvy['impl']
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
    yprve__yisk = 'def impl(A):\n'
    yprve__yisk += '  total_nbytes = 0\n'
    yprve__yisk += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        yprve__yisk += f'  total_nbytes += data[{i}].nbytes\n'
    yprve__yisk += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    yprve__yisk += '  return total_nbytes\n'
    okuy__qjtvy = {}
    exec(yprve__yisk, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, okuy__qjtvy)
    impl = okuy__qjtvy['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        rtt__rxln = get_null_bitmap(A)
        vrk__njx = bodo.ir.join.copy_arr_tup(data)
        lbgbg__hcx = rtt__rxln.copy()
        return init_struct_arr(vrk__njx, lbgbg__hcx, names)
    return copy_impl
