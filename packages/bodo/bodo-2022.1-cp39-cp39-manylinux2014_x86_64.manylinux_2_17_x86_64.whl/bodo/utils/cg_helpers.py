"""helper functions for code generation with llvmlite
"""
import llvmlite.binding as ll
from llvmlite import ir as lir
from numba.core import cgutils, types
import bodo
from bodo.libs import array_ext, hdist
ll.add_symbol('array_getitem', array_ext.array_getitem)
ll.add_symbol('seq_getitem', array_ext.seq_getitem)
ll.add_symbol('list_check', array_ext.list_check)
ll.add_symbol('dict_keys', array_ext.dict_keys)
ll.add_symbol('dict_values', array_ext.dict_values)
ll.add_symbol('dict_merge_from_seq2', array_ext.dict_merge_from_seq2)
ll.add_symbol('is_na_value', array_ext.is_na_value)


def set_bitmap_bit(builder, null_bitmap_ptr, ind, val):
    cyzx__voep = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    uhwp__lhqzd = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    qwys__bajd = builder.gep(null_bitmap_ptr, [cyzx__voep], inbounds=True)
    blxt__rcrwc = builder.load(qwys__bajd)
    ldodq__kxjzd = lir.ArrayType(lir.IntType(8), 8)
    ddeiv__fioe = cgutils.alloca_once_value(builder, lir.Constant(
        ldodq__kxjzd, (1, 2, 4, 8, 16, 32, 64, 128)))
    islu__naqe = builder.load(builder.gep(ddeiv__fioe, [lir.Constant(lir.
        IntType(64), 0), uhwp__lhqzd], inbounds=True))
    if val:
        builder.store(builder.or_(blxt__rcrwc, islu__naqe), qwys__bajd)
    else:
        islu__naqe = builder.xor(islu__naqe, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(blxt__rcrwc, islu__naqe), qwys__bajd)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    cyzx__voep = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    uhwp__lhqzd = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    blxt__rcrwc = builder.load(builder.gep(null_bitmap_ptr, [cyzx__voep],
        inbounds=True))
    ldodq__kxjzd = lir.ArrayType(lir.IntType(8), 8)
    ddeiv__fioe = cgutils.alloca_once_value(builder, lir.Constant(
        ldodq__kxjzd, (1, 2, 4, 8, 16, 32, 64, 128)))
    islu__naqe = builder.load(builder.gep(ddeiv__fioe, [lir.Constant(lir.
        IntType(64), 0), uhwp__lhqzd], inbounds=True))
    return builder.and_(blxt__rcrwc, islu__naqe)


def pyarray_getitem(builder, context, arr_obj, ind):
    vld__wfzpt = context.get_argument_type(types.pyobject)
    ynp__wvla = context.get_value_type(types.intp)
    hqu__myrp = lir.FunctionType(lir.IntType(8).as_pointer(), [vld__wfzpt,
        ynp__wvla])
    onvxv__schot = cgutils.get_or_insert_function(builder.module, hqu__myrp,
        name='array_getptr1')
    fpesi__amb = lir.FunctionType(vld__wfzpt, [vld__wfzpt, lir.IntType(8).
        as_pointer()])
    hpg__yuf = cgutils.get_or_insert_function(builder.module, fpesi__amb,
        name='array_getitem')
    euaf__vmzd = builder.call(onvxv__schot, [arr_obj, ind])
    return builder.call(hpg__yuf, [arr_obj, euaf__vmzd])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    vld__wfzpt = context.get_argument_type(types.pyobject)
    ynp__wvla = context.get_value_type(types.intp)
    hqu__myrp = lir.FunctionType(lir.IntType(8).as_pointer(), [vld__wfzpt,
        ynp__wvla])
    onvxv__schot = cgutils.get_or_insert_function(builder.module, hqu__myrp,
        name='array_getptr1')
    hym__eiq = lir.FunctionType(lir.VoidType(), [vld__wfzpt, lir.IntType(8)
        .as_pointer(), vld__wfzpt])
    fnq__uukcg = cgutils.get_or_insert_function(builder.module, hym__eiq,
        name='array_setitem')
    euaf__vmzd = builder.call(onvxv__schot, [arr_obj, ind])
    builder.call(fnq__uukcg, [arr_obj, euaf__vmzd, val_obj])


def seq_getitem(builder, context, obj, ind):
    vld__wfzpt = context.get_argument_type(types.pyobject)
    ynp__wvla = context.get_value_type(types.intp)
    kko__ont = lir.FunctionType(vld__wfzpt, [vld__wfzpt, ynp__wvla])
    ftuy__zfram = cgutils.get_or_insert_function(builder.module, kko__ont,
        name='seq_getitem')
    return builder.call(ftuy__zfram, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    vld__wfzpt = context.get_argument_type(types.pyobject)
    ygp__cmw = lir.FunctionType(lir.IntType(32), [vld__wfzpt, vld__wfzpt])
    nas__xmbb = cgutils.get_or_insert_function(builder.module, ygp__cmw,
        name='is_na_value')
    return builder.call(nas__xmbb, [val, C_NA])


def list_check(builder, context, obj):
    vld__wfzpt = context.get_argument_type(types.pyobject)
    uasy__iejy = context.get_value_type(types.int32)
    ikvl__vfhoa = lir.FunctionType(uasy__iejy, [vld__wfzpt])
    mdapi__dxg = cgutils.get_or_insert_function(builder.module, ikvl__vfhoa,
        name='list_check')
    return builder.call(mdapi__dxg, [obj])


def dict_keys(builder, context, obj):
    vld__wfzpt = context.get_argument_type(types.pyobject)
    ikvl__vfhoa = lir.FunctionType(vld__wfzpt, [vld__wfzpt])
    mdapi__dxg = cgutils.get_or_insert_function(builder.module, ikvl__vfhoa,
        name='dict_keys')
    return builder.call(mdapi__dxg, [obj])


def dict_values(builder, context, obj):
    vld__wfzpt = context.get_argument_type(types.pyobject)
    ikvl__vfhoa = lir.FunctionType(vld__wfzpt, [vld__wfzpt])
    mdapi__dxg = cgutils.get_or_insert_function(builder.module, ikvl__vfhoa,
        name='dict_values')
    return builder.call(mdapi__dxg, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    vld__wfzpt = context.get_argument_type(types.pyobject)
    ikvl__vfhoa = lir.FunctionType(lir.VoidType(), [vld__wfzpt, vld__wfzpt])
    mdapi__dxg = cgutils.get_or_insert_function(builder.module, ikvl__vfhoa,
        name='dict_merge_from_seq2')
    builder.call(mdapi__dxg, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    zuxa__isz = cgutils.alloca_once_value(builder, val)
    tzuyi__aczw = list_check(builder, context, val)
    akcl__hethh = builder.icmp_unsigned('!=', tzuyi__aczw, lir.Constant(
        tzuyi__aczw.type, 0))
    with builder.if_then(akcl__hethh):
        uni__smd = context.insert_const_string(builder.module, 'numpy')
        jvo__bjzvz = c.pyapi.import_module_noblock(uni__smd)
        fcqk__kzyde = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            fcqk__kzyde = str(typ.dtype)
        tlzb__mdtw = c.pyapi.object_getattr_string(jvo__bjzvz, fcqk__kzyde)
        iabhz__yuw = builder.load(zuxa__isz)
        spcfy__horiu = c.pyapi.call_method(jvo__bjzvz, 'asarray', (
            iabhz__yuw, tlzb__mdtw))
        builder.store(spcfy__horiu, zuxa__isz)
        c.pyapi.decref(jvo__bjzvz)
        c.pyapi.decref(tlzb__mdtw)
    val = builder.load(zuxa__isz)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        ysjwo__dseo = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        iat__bigo, uwdy__dawea = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [ysjwo__dseo])
        context.nrt.decref(builder, typ, ysjwo__dseo)
        return cgutils.pack_array(builder, [uwdy__dawea])
    if isinstance(typ, (StructType, types.BaseTuple)):
        uni__smd = context.insert_const_string(builder.module, 'pandas')
        gbbl__kwb = c.pyapi.import_module_noblock(uni__smd)
        C_NA = c.pyapi.object_getattr_string(gbbl__kwb, 'NA')
        bkhhc__xtdok = bodo.utils.transform.get_type_alloc_counts(typ)
        vyp__bojdc = context.make_tuple(builder, types.Tuple(bkhhc__xtdok *
            [types.int64]), bkhhc__xtdok * [context.get_constant(types.
            int64, 0)])
        hlfd__zntn = cgutils.alloca_once_value(builder, vyp__bojdc)
        yjw__sis = 0
        oirj__upl = typ.data if isinstance(typ, StructType) else typ.types
        for iunq__aiol, t in enumerate(oirj__upl):
            mmp__sysjc = bodo.utils.transform.get_type_alloc_counts(t)
            if mmp__sysjc == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    iunq__aiol])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, iunq__aiol)
            tylnv__forj = is_na_value(builder, context, val_obj, C_NA)
            gliv__xeq = builder.icmp_unsigned('!=', tylnv__forj, lir.
                Constant(tylnv__forj.type, 1))
            with builder.if_then(gliv__xeq):
                vyp__bojdc = builder.load(hlfd__zntn)
                fli__prx = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for iunq__aiol in range(mmp__sysjc):
                    qxymz__svcs = builder.extract_value(vyp__bojdc, 
                        yjw__sis + iunq__aiol)
                    cawfg__sosw = builder.extract_value(fli__prx, iunq__aiol)
                    vyp__bojdc = builder.insert_value(vyp__bojdc, builder.
                        add(qxymz__svcs, cawfg__sosw), yjw__sis + iunq__aiol)
                builder.store(vyp__bojdc, hlfd__zntn)
            yjw__sis += mmp__sysjc
        c.pyapi.decref(gbbl__kwb)
        c.pyapi.decref(C_NA)
        return builder.load(hlfd__zntn)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    uni__smd = context.insert_const_string(builder.module, 'pandas')
    gbbl__kwb = c.pyapi.import_module_noblock(uni__smd)
    C_NA = c.pyapi.object_getattr_string(gbbl__kwb, 'NA')
    bkhhc__xtdok = bodo.utils.transform.get_type_alloc_counts(typ)
    vyp__bojdc = context.make_tuple(builder, types.Tuple(bkhhc__xtdok * [
        types.int64]), [n] + (bkhhc__xtdok - 1) * [context.get_constant(
        types.int64, 0)])
    hlfd__zntn = cgutils.alloca_once_value(builder, vyp__bojdc)
    with cgutils.for_range(builder, n) as loop:
        guyx__zkm = loop.index
        ggm__nkdun = seq_getitem(builder, context, arr_obj, guyx__zkm)
        tylnv__forj = is_na_value(builder, context, ggm__nkdun, C_NA)
        gliv__xeq = builder.icmp_unsigned('!=', tylnv__forj, lir.Constant(
            tylnv__forj.type, 1))
        with builder.if_then(gliv__xeq):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                vyp__bojdc = builder.load(hlfd__zntn)
                fli__prx = get_array_elem_counts(c, builder, context,
                    ggm__nkdun, typ.dtype)
                for iunq__aiol in range(bkhhc__xtdok - 1):
                    qxymz__svcs = builder.extract_value(vyp__bojdc, 
                        iunq__aiol + 1)
                    cawfg__sosw = builder.extract_value(fli__prx, iunq__aiol)
                    vyp__bojdc = builder.insert_value(vyp__bojdc, builder.
                        add(qxymz__svcs, cawfg__sosw), iunq__aiol + 1)
                builder.store(vyp__bojdc, hlfd__zntn)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                yjw__sis = 1
                for iunq__aiol, t in enumerate(typ.data):
                    mmp__sysjc = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if mmp__sysjc == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(ggm__nkdun, iunq__aiol)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(ggm__nkdun,
                            typ.names[iunq__aiol])
                    tylnv__forj = is_na_value(builder, context, val_obj, C_NA)
                    gliv__xeq = builder.icmp_unsigned('!=', tylnv__forj,
                        lir.Constant(tylnv__forj.type, 1))
                    with builder.if_then(gliv__xeq):
                        vyp__bojdc = builder.load(hlfd__zntn)
                        fli__prx = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for iunq__aiol in range(mmp__sysjc):
                            qxymz__svcs = builder.extract_value(vyp__bojdc,
                                yjw__sis + iunq__aiol)
                            cawfg__sosw = builder.extract_value(fli__prx,
                                iunq__aiol)
                            vyp__bojdc = builder.insert_value(vyp__bojdc,
                                builder.add(qxymz__svcs, cawfg__sosw), 
                                yjw__sis + iunq__aiol)
                        builder.store(vyp__bojdc, hlfd__zntn)
                    yjw__sis += mmp__sysjc
            else:
                assert isinstance(typ, MapArrayType), typ
                vyp__bojdc = builder.load(hlfd__zntn)
                mpqtp__key = dict_keys(builder, context, ggm__nkdun)
                dpggd__clkg = dict_values(builder, context, ggm__nkdun)
                hrcb__wbl = get_array_elem_counts(c, builder, context,
                    mpqtp__key, typ.key_arr_type)
                auepf__jwzvc = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for iunq__aiol in range(1, auepf__jwzvc + 1):
                    qxymz__svcs = builder.extract_value(vyp__bojdc, iunq__aiol)
                    cawfg__sosw = builder.extract_value(hrcb__wbl, 
                        iunq__aiol - 1)
                    vyp__bojdc = builder.insert_value(vyp__bojdc, builder.
                        add(qxymz__svcs, cawfg__sosw), iunq__aiol)
                dyes__yoif = get_array_elem_counts(c, builder, context,
                    dpggd__clkg, typ.value_arr_type)
                for iunq__aiol in range(auepf__jwzvc + 1, bkhhc__xtdok):
                    qxymz__svcs = builder.extract_value(vyp__bojdc, iunq__aiol)
                    cawfg__sosw = builder.extract_value(dyes__yoif, 
                        iunq__aiol - auepf__jwzvc)
                    vyp__bojdc = builder.insert_value(vyp__bojdc, builder.
                        add(qxymz__svcs, cawfg__sosw), iunq__aiol)
                builder.store(vyp__bojdc, hlfd__zntn)
                c.pyapi.decref(mpqtp__key)
                c.pyapi.decref(dpggd__clkg)
        c.pyapi.decref(ggm__nkdun)
    c.pyapi.decref(gbbl__kwb)
    c.pyapi.decref(C_NA)
    return builder.load(hlfd__zntn)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    dddu__icki = n_elems.type.count
    assert dddu__icki >= 1
    tqyr__ixiua = builder.extract_value(n_elems, 0)
    if dddu__icki != 1:
        kri__bmti = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, iunq__aiol) for iunq__aiol in range(1, dddu__icki)])
        jwfh__bquy = types.Tuple([types.int64] * (dddu__icki - 1))
    else:
        kri__bmti = context.get_dummy_value()
        jwfh__bquy = types.none
    elm__aeho = types.TypeRef(arr_type)
    xjzd__rajzw = arr_type(types.int64, elm__aeho, jwfh__bquy)
    args = [tqyr__ixiua, context.get_dummy_value(), kri__bmti]
    cyhjv__lhj = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        iat__bigo, wpdlq__pjlxt = c.pyapi.call_jit_code(cyhjv__lhj,
            xjzd__rajzw, args)
    else:
        wpdlq__pjlxt = context.compile_internal(builder, cyhjv__lhj,
            xjzd__rajzw, args)
    return wpdlq__pjlxt


def is_ll_eq(builder, val1, val2):
    nhlyz__cysy = val1.type.pointee
    elwq__ercew = val2.type.pointee
    assert nhlyz__cysy == elwq__ercew, 'invalid llvm value comparison'
    if isinstance(nhlyz__cysy, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(nhlyz__cysy.elements) if isinstance(nhlyz__cysy, lir.
            BaseStructType) else nhlyz__cysy.count
        fdrun__nef = lir.Constant(lir.IntType(1), 1)
        for iunq__aiol in range(n_elems):
            mfbb__qrkxc = lir.IntType(32)(0)
            bapar__kim = lir.IntType(32)(iunq__aiol)
            sxgs__htu = builder.gep(val1, [mfbb__qrkxc, bapar__kim],
                inbounds=True)
            jhgw__rlza = builder.gep(val2, [mfbb__qrkxc, bapar__kim],
                inbounds=True)
            fdrun__nef = builder.and_(fdrun__nef, is_ll_eq(builder,
                sxgs__htu, jhgw__rlza))
        return fdrun__nef
    lhes__rnl = builder.load(val1)
    fcpg__ssjqo = builder.load(val2)
    if lhes__rnl.type in (lir.FloatType(), lir.DoubleType()):
        tjzn__vwvi = 32 if lhes__rnl.type == lir.FloatType() else 64
        lhes__rnl = builder.bitcast(lhes__rnl, lir.IntType(tjzn__vwvi))
        fcpg__ssjqo = builder.bitcast(fcpg__ssjqo, lir.IntType(tjzn__vwvi))
    return builder.icmp_unsigned('==', lhes__rnl, fcpg__ssjqo)
