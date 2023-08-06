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
    zjir__jzml = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    dbpu__jmmf = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    ztyu__zhpkf = builder.gep(null_bitmap_ptr, [zjir__jzml], inbounds=True)
    hkwpa__rtorr = builder.load(ztyu__zhpkf)
    fqb__uegv = lir.ArrayType(lir.IntType(8), 8)
    phlb__zpmb = cgutils.alloca_once_value(builder, lir.Constant(fqb__uegv,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    mwu__arc = builder.load(builder.gep(phlb__zpmb, [lir.Constant(lir.
        IntType(64), 0), dbpu__jmmf], inbounds=True))
    if val:
        builder.store(builder.or_(hkwpa__rtorr, mwu__arc), ztyu__zhpkf)
    else:
        mwu__arc = builder.xor(mwu__arc, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(hkwpa__rtorr, mwu__arc), ztyu__zhpkf)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    zjir__jzml = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    dbpu__jmmf = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    hkwpa__rtorr = builder.load(builder.gep(null_bitmap_ptr, [zjir__jzml],
        inbounds=True))
    fqb__uegv = lir.ArrayType(lir.IntType(8), 8)
    phlb__zpmb = cgutils.alloca_once_value(builder, lir.Constant(fqb__uegv,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    mwu__arc = builder.load(builder.gep(phlb__zpmb, [lir.Constant(lir.
        IntType(64), 0), dbpu__jmmf], inbounds=True))
    return builder.and_(hkwpa__rtorr, mwu__arc)


def pyarray_getitem(builder, context, arr_obj, ind):
    xcf__zvx = context.get_argument_type(types.pyobject)
    ade__ijcxr = context.get_value_type(types.intp)
    zlwoi__jwabv = lir.FunctionType(lir.IntType(8).as_pointer(), [xcf__zvx,
        ade__ijcxr])
    pmyh__azvha = cgutils.get_or_insert_function(builder.module,
        zlwoi__jwabv, name='array_getptr1')
    arwcv__dfkg = lir.FunctionType(xcf__zvx, [xcf__zvx, lir.IntType(8).
        as_pointer()])
    xrnyl__uas = cgutils.get_or_insert_function(builder.module, arwcv__dfkg,
        name='array_getitem')
    yqet__plmb = builder.call(pmyh__azvha, [arr_obj, ind])
    return builder.call(xrnyl__uas, [arr_obj, yqet__plmb])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    xcf__zvx = context.get_argument_type(types.pyobject)
    ade__ijcxr = context.get_value_type(types.intp)
    zlwoi__jwabv = lir.FunctionType(lir.IntType(8).as_pointer(), [xcf__zvx,
        ade__ijcxr])
    pmyh__azvha = cgutils.get_or_insert_function(builder.module,
        zlwoi__jwabv, name='array_getptr1')
    qvuwi__oamgq = lir.FunctionType(lir.VoidType(), [xcf__zvx, lir.IntType(
        8).as_pointer(), xcf__zvx])
    sgocf__gojv = cgutils.get_or_insert_function(builder.module,
        qvuwi__oamgq, name='array_setitem')
    yqet__plmb = builder.call(pmyh__azvha, [arr_obj, ind])
    builder.call(sgocf__gojv, [arr_obj, yqet__plmb, val_obj])


def seq_getitem(builder, context, obj, ind):
    xcf__zvx = context.get_argument_type(types.pyobject)
    ade__ijcxr = context.get_value_type(types.intp)
    rhoz__zvn = lir.FunctionType(xcf__zvx, [xcf__zvx, ade__ijcxr])
    czx__eae = cgutils.get_or_insert_function(builder.module, rhoz__zvn,
        name='seq_getitem')
    return builder.call(czx__eae, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    xcf__zvx = context.get_argument_type(types.pyobject)
    cdbmr__ziqv = lir.FunctionType(lir.IntType(32), [xcf__zvx, xcf__zvx])
    atk__ruqew = cgutils.get_or_insert_function(builder.module, cdbmr__ziqv,
        name='is_na_value')
    return builder.call(atk__ruqew, [val, C_NA])


def list_check(builder, context, obj):
    xcf__zvx = context.get_argument_type(types.pyobject)
    iro__aedn = context.get_value_type(types.int32)
    zjftg__bng = lir.FunctionType(iro__aedn, [xcf__zvx])
    jji__urpzc = cgutils.get_or_insert_function(builder.module, zjftg__bng,
        name='list_check')
    return builder.call(jji__urpzc, [obj])


def dict_keys(builder, context, obj):
    xcf__zvx = context.get_argument_type(types.pyobject)
    zjftg__bng = lir.FunctionType(xcf__zvx, [xcf__zvx])
    jji__urpzc = cgutils.get_or_insert_function(builder.module, zjftg__bng,
        name='dict_keys')
    return builder.call(jji__urpzc, [obj])


def dict_values(builder, context, obj):
    xcf__zvx = context.get_argument_type(types.pyobject)
    zjftg__bng = lir.FunctionType(xcf__zvx, [xcf__zvx])
    jji__urpzc = cgutils.get_or_insert_function(builder.module, zjftg__bng,
        name='dict_values')
    return builder.call(jji__urpzc, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    xcf__zvx = context.get_argument_type(types.pyobject)
    zjftg__bng = lir.FunctionType(lir.VoidType(), [xcf__zvx, xcf__zvx])
    jji__urpzc = cgutils.get_or_insert_function(builder.module, zjftg__bng,
        name='dict_merge_from_seq2')
    builder.call(jji__urpzc, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    eizrz__cdkfh = cgutils.alloca_once_value(builder, val)
    fcuo__kbxz = list_check(builder, context, val)
    mtdt__abjz = builder.icmp_unsigned('!=', fcuo__kbxz, lir.Constant(
        fcuo__kbxz.type, 0))
    with builder.if_then(mtdt__abjz):
        mem__tofb = context.insert_const_string(builder.module, 'numpy')
        thfta__rojd = c.pyapi.import_module_noblock(mem__tofb)
        zypzj__fmu = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            zypzj__fmu = str(typ.dtype)
        mho__kyi = c.pyapi.object_getattr_string(thfta__rojd, zypzj__fmu)
        wxk__ifwq = builder.load(eizrz__cdkfh)
        hejfk__vfr = c.pyapi.call_method(thfta__rojd, 'asarray', (wxk__ifwq,
            mho__kyi))
        builder.store(hejfk__vfr, eizrz__cdkfh)
        c.pyapi.decref(thfta__rojd)
        c.pyapi.decref(mho__kyi)
    val = builder.load(eizrz__cdkfh)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        kjx__uer = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        wfj__knlij, zmmp__mdi = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [kjx__uer])
        context.nrt.decref(builder, typ, kjx__uer)
        return cgutils.pack_array(builder, [zmmp__mdi])
    if isinstance(typ, (StructType, types.BaseTuple)):
        mem__tofb = context.insert_const_string(builder.module, 'pandas')
        hugd__fsfdm = c.pyapi.import_module_noblock(mem__tofb)
        C_NA = c.pyapi.object_getattr_string(hugd__fsfdm, 'NA')
        chcm__cufl = bodo.utils.transform.get_type_alloc_counts(typ)
        kakrt__ctn = context.make_tuple(builder, types.Tuple(chcm__cufl * [
            types.int64]), chcm__cufl * [context.get_constant(types.int64, 0)])
        jfqj__ayj = cgutils.alloca_once_value(builder, kakrt__ctn)
        lxlc__kyifj = 0
        iin__hgz = typ.data if isinstance(typ, StructType) else typ.types
        for fdce__mbxa, t in enumerate(iin__hgz):
            lrb__qqclc = bodo.utils.transform.get_type_alloc_counts(t)
            if lrb__qqclc == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    fdce__mbxa])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, fdce__mbxa)
            gsymz__takit = is_na_value(builder, context, val_obj, C_NA)
            yffj__luspc = builder.icmp_unsigned('!=', gsymz__takit, lir.
                Constant(gsymz__takit.type, 1))
            with builder.if_then(yffj__luspc):
                kakrt__ctn = builder.load(jfqj__ayj)
                xyakk__azu = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for fdce__mbxa in range(lrb__qqclc):
                    ruehy__bfe = builder.extract_value(kakrt__ctn, 
                        lxlc__kyifj + fdce__mbxa)
                    rdcrt__yjvgv = builder.extract_value(xyakk__azu, fdce__mbxa
                        )
                    kakrt__ctn = builder.insert_value(kakrt__ctn, builder.
                        add(ruehy__bfe, rdcrt__yjvgv), lxlc__kyifj + fdce__mbxa
                        )
                builder.store(kakrt__ctn, jfqj__ayj)
            lxlc__kyifj += lrb__qqclc
        c.pyapi.decref(hugd__fsfdm)
        c.pyapi.decref(C_NA)
        return builder.load(jfqj__ayj)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    mem__tofb = context.insert_const_string(builder.module, 'pandas')
    hugd__fsfdm = c.pyapi.import_module_noblock(mem__tofb)
    C_NA = c.pyapi.object_getattr_string(hugd__fsfdm, 'NA')
    chcm__cufl = bodo.utils.transform.get_type_alloc_counts(typ)
    kakrt__ctn = context.make_tuple(builder, types.Tuple(chcm__cufl * [
        types.int64]), [n] + (chcm__cufl - 1) * [context.get_constant(types
        .int64, 0)])
    jfqj__ayj = cgutils.alloca_once_value(builder, kakrt__ctn)
    with cgutils.for_range(builder, n) as loop:
        snsf__xsmq = loop.index
        zir__avf = seq_getitem(builder, context, arr_obj, snsf__xsmq)
        gsymz__takit = is_na_value(builder, context, zir__avf, C_NA)
        yffj__luspc = builder.icmp_unsigned('!=', gsymz__takit, lir.
            Constant(gsymz__takit.type, 1))
        with builder.if_then(yffj__luspc):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                kakrt__ctn = builder.load(jfqj__ayj)
                xyakk__azu = get_array_elem_counts(c, builder, context,
                    zir__avf, typ.dtype)
                for fdce__mbxa in range(chcm__cufl - 1):
                    ruehy__bfe = builder.extract_value(kakrt__ctn, 
                        fdce__mbxa + 1)
                    rdcrt__yjvgv = builder.extract_value(xyakk__azu, fdce__mbxa
                        )
                    kakrt__ctn = builder.insert_value(kakrt__ctn, builder.
                        add(ruehy__bfe, rdcrt__yjvgv), fdce__mbxa + 1)
                builder.store(kakrt__ctn, jfqj__ayj)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                lxlc__kyifj = 1
                for fdce__mbxa, t in enumerate(typ.data):
                    lrb__qqclc = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if lrb__qqclc == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(zir__avf, fdce__mbxa)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(zir__avf, typ
                            .names[fdce__mbxa])
                    gsymz__takit = is_na_value(builder, context, val_obj, C_NA)
                    yffj__luspc = builder.icmp_unsigned('!=', gsymz__takit,
                        lir.Constant(gsymz__takit.type, 1))
                    with builder.if_then(yffj__luspc):
                        kakrt__ctn = builder.load(jfqj__ayj)
                        xyakk__azu = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for fdce__mbxa in range(lrb__qqclc):
                            ruehy__bfe = builder.extract_value(kakrt__ctn, 
                                lxlc__kyifj + fdce__mbxa)
                            rdcrt__yjvgv = builder.extract_value(xyakk__azu,
                                fdce__mbxa)
                            kakrt__ctn = builder.insert_value(kakrt__ctn,
                                builder.add(ruehy__bfe, rdcrt__yjvgv), 
                                lxlc__kyifj + fdce__mbxa)
                        builder.store(kakrt__ctn, jfqj__ayj)
                    lxlc__kyifj += lrb__qqclc
            else:
                assert isinstance(typ, MapArrayType), typ
                kakrt__ctn = builder.load(jfqj__ayj)
                yjktx__wtol = dict_keys(builder, context, zir__avf)
                wuoa__edsyu = dict_values(builder, context, zir__avf)
                owno__brh = get_array_elem_counts(c, builder, context,
                    yjktx__wtol, typ.key_arr_type)
                cwrya__jqe = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for fdce__mbxa in range(1, cwrya__jqe + 1):
                    ruehy__bfe = builder.extract_value(kakrt__ctn, fdce__mbxa)
                    rdcrt__yjvgv = builder.extract_value(owno__brh, 
                        fdce__mbxa - 1)
                    kakrt__ctn = builder.insert_value(kakrt__ctn, builder.
                        add(ruehy__bfe, rdcrt__yjvgv), fdce__mbxa)
                ozngq__qfft = get_array_elem_counts(c, builder, context,
                    wuoa__edsyu, typ.value_arr_type)
                for fdce__mbxa in range(cwrya__jqe + 1, chcm__cufl):
                    ruehy__bfe = builder.extract_value(kakrt__ctn, fdce__mbxa)
                    rdcrt__yjvgv = builder.extract_value(ozngq__qfft, 
                        fdce__mbxa - cwrya__jqe)
                    kakrt__ctn = builder.insert_value(kakrt__ctn, builder.
                        add(ruehy__bfe, rdcrt__yjvgv), fdce__mbxa)
                builder.store(kakrt__ctn, jfqj__ayj)
                c.pyapi.decref(yjktx__wtol)
                c.pyapi.decref(wuoa__edsyu)
        c.pyapi.decref(zir__avf)
    c.pyapi.decref(hugd__fsfdm)
    c.pyapi.decref(C_NA)
    return builder.load(jfqj__ayj)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    roi__kkaj = n_elems.type.count
    assert roi__kkaj >= 1
    lsxam__wqkkn = builder.extract_value(n_elems, 0)
    if roi__kkaj != 1:
        ify__knhrz = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, fdce__mbxa) for fdce__mbxa in range(1, roi__kkaj)])
        azad__nolg = types.Tuple([types.int64] * (roi__kkaj - 1))
    else:
        ify__knhrz = context.get_dummy_value()
        azad__nolg = types.none
    ylt__uoxmi = types.TypeRef(arr_type)
    uoh__tehc = arr_type(types.int64, ylt__uoxmi, azad__nolg)
    args = [lsxam__wqkkn, context.get_dummy_value(), ify__knhrz]
    dfg__gbti = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        wfj__knlij, dfc__oje = c.pyapi.call_jit_code(dfg__gbti, uoh__tehc, args
            )
    else:
        dfc__oje = context.compile_internal(builder, dfg__gbti, uoh__tehc, args
            )
    return dfc__oje


def is_ll_eq(builder, val1, val2):
    zxvyd__cspd = val1.type.pointee
    qaya__jck = val2.type.pointee
    assert zxvyd__cspd == qaya__jck, 'invalid llvm value comparison'
    if isinstance(zxvyd__cspd, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(zxvyd__cspd.elements) if isinstance(zxvyd__cspd, lir.
            BaseStructType) else zxvyd__cspd.count
        pbpd__aum = lir.Constant(lir.IntType(1), 1)
        for fdce__mbxa in range(n_elems):
            qyxc__nsf = lir.IntType(32)(0)
            ocom__qxby = lir.IntType(32)(fdce__mbxa)
            sxa__ivj = builder.gep(val1, [qyxc__nsf, ocom__qxby], inbounds=True
                )
            vgkmy__plv = builder.gep(val2, [qyxc__nsf, ocom__qxby],
                inbounds=True)
            pbpd__aum = builder.and_(pbpd__aum, is_ll_eq(builder, sxa__ivj,
                vgkmy__plv))
        return pbpd__aum
    lsbod__xti = builder.load(val1)
    dbf__iwvb = builder.load(val2)
    if lsbod__xti.type in (lir.FloatType(), lir.DoubleType()):
        bjepj__yzu = 32 if lsbod__xti.type == lir.FloatType() else 64
        lsbod__xti = builder.bitcast(lsbod__xti, lir.IntType(bjepj__yzu))
        dbf__iwvb = builder.bitcast(dbf__iwvb, lir.IntType(bjepj__yzu))
    return builder.icmp_unsigned('==', lsbod__xti, dbf__iwvb)
