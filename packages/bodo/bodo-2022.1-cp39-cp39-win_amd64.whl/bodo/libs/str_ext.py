import operator
import re
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, bound_function, infer_getattr, infer_global, signature
from numba.extending import intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_jitable, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.utils.typing import get_overload_const_int, get_overload_const_str, is_overload_constant_int, is_overload_constant_str


def unliteral_all(args):
    return tuple(types.unliteral(a) for a in args)


ll.add_symbol('del_str', hstr_ext.del_str)
ll.add_symbol('unicode_to_utf8', hstr_ext.unicode_to_utf8)
ll.add_symbol('memcmp', hstr_ext.memcmp)
ll.add_symbol('int_to_hex', hstr_ext.int_to_hex)
string_type = types.unicode_type


@numba.njit
def contains_regex(e, in_str):
    with numba.objmode(res='bool_'):
        res = bool(e.search(in_str))
    return res


@numba.generated_jit
def str_findall_count(regex, in_str):

    def _str_findall_count_impl(regex, in_str):
        with numba.objmode(res='int64'):
            res = len(regex.findall(in_str))
        return res
    return _str_findall_count_impl


utf8_str_type = types.ArrayCTypes(types.Array(types.uint8, 1, 'C'))


@intrinsic
def unicode_to_utf8_and_len(typingctx, str_typ=None):
    assert str_typ in (string_type, types.Optional(string_type)) or isinstance(
        str_typ, types.StringLiteral)
    fauyy__idtlj = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        verci__mad, = args
        ewbej__cnorf = cgutils.create_struct_proxy(string_type)(context,
            builder, value=verci__mad)
        pkoz__uozi = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        zyubm__isrj = cgutils.create_struct_proxy(fauyy__idtlj)(context,
            builder)
        is_ascii = builder.icmp_unsigned('==', ewbej__cnorf.is_ascii, lir.
            Constant(ewbej__cnorf.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (then, orelse):
            with then:
                context.nrt.incref(builder, string_type, verci__mad)
                pkoz__uozi.data = ewbej__cnorf.data
                pkoz__uozi.meminfo = ewbej__cnorf.meminfo
                zyubm__isrj.f1 = ewbej__cnorf.length
            with orelse:
                ngjz__jzor = lir.FunctionType(lir.IntType(64), [lir.IntType
                    (8).as_pointer(), lir.IntType(8).as_pointer(), lir.
                    IntType(64), lir.IntType(32)])
                dgh__wwr = cgutils.get_or_insert_function(builder.module,
                    ngjz__jzor, name='unicode_to_utf8')
                rdml__tqfc = context.get_constant_null(types.voidptr)
                dgsh__xdc = builder.call(dgh__wwr, [rdml__tqfc,
                    ewbej__cnorf.data, ewbej__cnorf.length, ewbej__cnorf.kind])
                zyubm__isrj.f1 = dgsh__xdc
                svbd__gmhxa = builder.add(dgsh__xdc, lir.Constant(lir.
                    IntType(64), 1))
                pkoz__uozi.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=svbd__gmhxa, align=32)
                pkoz__uozi.data = context.nrt.meminfo_data(builder,
                    pkoz__uozi.meminfo)
                builder.call(dgh__wwr, [pkoz__uozi.data, ewbej__cnorf.data,
                    ewbej__cnorf.length, ewbej__cnorf.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    pkoz__uozi.data, [dgsh__xdc]))
        zyubm__isrj.f0 = pkoz__uozi._getvalue()
        return zyubm__isrj._getvalue()
    return fauyy__idtlj(string_type), codegen


def unicode_to_utf8(s):
    return s


@overload(unicode_to_utf8)
def overload_unicode_to_utf8(s):
    return lambda s: unicode_to_utf8_and_len(s)[0]


@overload(max)
def overload_builtin_max(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs > rhs else rhs
        return impl


@overload(min)
def overload_builtin_min(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs < rhs else rhs
        return impl


@intrinsic
def memcmp(typingctx, dest_t, src_t, count_t=None):

    def codegen(context, builder, sig, args):
        ngjz__jzor = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        gwux__ipy = cgutils.get_or_insert_function(builder.module,
            ngjz__jzor, name='memcmp')
        return builder.call(gwux__ipy, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    fvsyh__erta = n(10)

    def impl(n):
        if n == 0:
            return 1
        gyjl__vmp = 0
        if n < 0:
            n = -n
            gyjl__vmp += 1
        while n > 0:
            n = n // fvsyh__erta
            gyjl__vmp += 1
        return gyjl__vmp
    return impl


class StdStringType(types.Opaque):

    def __init__(self):
        super(StdStringType, self).__init__(name='StdStringType')


std_str_type = StdStringType()
register_model(StdStringType)(models.OpaqueModel)
del_str = types.ExternalFunction('del_str', types.void(std_str_type))
get_c_str = types.ExternalFunction('get_c_str', types.voidptr(std_str_type))
dummy_use = numba.njit(lambda a: None)


@overload(int)
def int_str_overload(in_str, base=10):
    if in_str == string_type:
        if is_overload_constant_int(base) and get_overload_const_int(base
            ) == 10:

            def _str_to_int_impl(in_str, base=10):
                val = _str_to_int64(in_str._data, in_str._length)
                dummy_use(in_str)
                return val
            return _str_to_int_impl

        def _str_to_int_base_impl(in_str, base=10):
            val = _str_to_int64_base(in_str._data, in_str._length, base)
            dummy_use(in_str)
            return val
        return _str_to_int_base_impl


@infer_global(float)
class StrToFloat(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        [fyp__ikvp] = args
        if isinstance(fyp__ikvp, StdStringType):
            return signature(types.float64, fyp__ikvp)
        if fyp__ikvp == string_type:
            return signature(types.float64, fyp__ikvp)


ll.add_symbol('init_string_const', hstr_ext.init_string_const)
ll.add_symbol('get_c_str', hstr_ext.get_c_str)
ll.add_symbol('str_to_int64', hstr_ext.str_to_int64)
ll.add_symbol('str_to_uint64', hstr_ext.str_to_uint64)
ll.add_symbol('str_to_int64_base', hstr_ext.str_to_int64_base)
ll.add_symbol('str_to_float64', hstr_ext.str_to_float64)
ll.add_symbol('str_to_float32', hstr_ext.str_to_float32)
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('str_from_float32', hstr_ext.str_from_float32)
ll.add_symbol('str_from_float64', hstr_ext.str_from_float64)
get_std_str_len = types.ExternalFunction('get_str_len', signature(types.
    intp, std_str_type))
init_string_from_chars = types.ExternalFunction('init_string_const',
    std_str_type(types.voidptr, types.intp))
_str_to_int64 = types.ExternalFunction('str_to_int64', signature(types.
    int64, types.voidptr, types.int64))
_str_to_uint64 = types.ExternalFunction('str_to_uint64', signature(types.
    uint64, types.voidptr, types.int64))
_str_to_int64_base = types.ExternalFunction('str_to_int64_base', signature(
    types.int64, types.voidptr, types.int64, types.int64))


def gen_unicode_to_std_str(context, builder, unicode_val):
    ewbej__cnorf = cgutils.create_struct_proxy(string_type)(context,
        builder, value=unicode_val)
    ngjz__jzor = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer(), lir.IntType(64)])
    gkus__mrp = cgutils.get_or_insert_function(builder.module, ngjz__jzor,
        name='init_string_const')
    return builder.call(gkus__mrp, [ewbej__cnorf.data, ewbej__cnorf.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        yrmi__tcyo = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(yrmi__tcyo._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return yrmi__tcyo
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    ewbej__cnorf = cgutils.create_struct_proxy(string_type)(context,
        builder, value=unicode_val)
    return ewbej__cnorf.data


@intrinsic
def unicode_to_std_str(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_unicode_to_std_str(context, builder, args[0])
    return std_str_type(string_type), codegen


@intrinsic
def std_str_to_unicode(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_std_str_to_unicode(context, builder, args[0], True)
    return string_type(std_str_type), codegen


class RandomAccessStringArrayType(types.ArrayCompatible):

    def __init__(self):
        super(RandomAccessStringArrayType, self).__init__(name=
            'RandomAccessStringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    def copy(self):
        RandomAccessStringArrayType()


random_access_string_array = RandomAccessStringArrayType()


@register_model(RandomAccessStringArrayType)
class RandomAccessStringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        auiqd__ppm = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, auiqd__ppm)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        riino__upego, = args
        vnxkp__jga = types.List(string_type)
        uzom__xzj = numba.cpython.listobj.ListInstance.allocate(context,
            builder, vnxkp__jga, riino__upego)
        uzom__xzj.size = riino__upego
        mskgf__dqchq = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        mskgf__dqchq.data = uzom__xzj.value
        return mskgf__dqchq._getvalue()
    return random_access_string_array(types.intp), codegen


@overload(operator.getitem, no_unliteral=True)
def random_access_str_arr_getitem(A, ind):
    if A != random_access_string_array:
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]


@overload(operator.setitem)
def random_access_str_arr_setitem(A, idx, val):
    if A != random_access_string_array:
        return
    if isinstance(idx, types.Integer):
        assert val == string_type

        def impl_scalar(A, idx, val):
            A._data[idx] = val
        return impl_scalar


@overload(len, no_unliteral=True)
def overload_str_arr_len(A):
    if A == random_access_string_array:
        return lambda A: len(A._data)


@overload_attribute(RandomAccessStringArrayType, 'shape')
def overload_str_arr_shape(A):
    return lambda A: (len(A._data),)


def alloc_random_access_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_str_ext_alloc_random_access_string_array
    ) = alloc_random_access_str_arr_equiv
str_from_float32 = types.ExternalFunction('str_from_float32', types.void(
    types.voidptr, types.float32))
str_from_float64 = types.ExternalFunction('str_from_float64', types.void(
    types.voidptr, types.float64))


def float_to_str(s, v):
    pass


@overload(float_to_str)
def float_to_str_overload(s, v):
    assert isinstance(v, types.Float)
    if v == types.float32:
        return lambda s, v: str_from_float32(s._data, v)
    return lambda s, v: str_from_float64(s._data, v)


@overload(str)
def float_str_overload(v):
    if isinstance(v, types.Float):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(v):
            if v == 0:
                return '0.0'
            inqvc__ljqpb = 0
            haqbr__sra = v
            if haqbr__sra < 0:
                inqvc__ljqpb = 1
                haqbr__sra = -haqbr__sra
            if haqbr__sra < 1:
                lsvz__ceg = 1
            else:
                lsvz__ceg = 1 + int(np.floor(np.log10(haqbr__sra)))
            length = inqvc__ljqpb + lsvz__ceg + 1 + 6
            s = numba.cpython.unicode._malloc_string(kind, 1, length, True)
            float_to_str(s, v)
            return s
        return impl


@overload(format, no_unliteral=True)
def overload_format(value, format_spec=''):
    if is_overload_constant_str(format_spec) and get_overload_const_str(
        format_spec) == '':

        def impl_fast(value, format_spec=''):
            return str(value)
        return impl_fast

    def impl(value, format_spec=''):
        with numba.objmode(res='string'):
            res = format(value, format_spec)
        return res
    return impl


@lower_cast(StdStringType, types.float64)
def cast_str_to_float64(context, builder, fromty, toty, val):
    ngjz__jzor = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    gkus__mrp = cgutils.get_or_insert_function(builder.module, ngjz__jzor,
        name='str_to_float64')
    return builder.call(gkus__mrp, (val,))


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    ngjz__jzor = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    gkus__mrp = cgutils.get_or_insert_function(builder.module, ngjz__jzor,
        name='str_to_float32')
    return builder.call(gkus__mrp, (val,))


@lower_cast(string_type, types.float64)
def cast_unicode_str_to_float64(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float64(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.float32)
def cast_unicode_str_to_float32(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float32(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.int64)
@lower_cast(string_type, types.int32)
@lower_cast(string_type, types.int16)
@lower_cast(string_type, types.int8)
def cast_unicode_str_to_int64(context, builder, fromty, toty, val):
    ewbej__cnorf = cgutils.create_struct_proxy(string_type)(context,
        builder, value=val)
    ngjz__jzor = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    gkus__mrp = cgutils.get_or_insert_function(builder.module, ngjz__jzor,
        name='str_to_int64')
    return builder.call(gkus__mrp, (ewbej__cnorf.data, ewbej__cnorf.length))


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    ewbej__cnorf = cgutils.create_struct_proxy(string_type)(context,
        builder, value=val)
    ngjz__jzor = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    gkus__mrp = cgutils.get_or_insert_function(builder.module, ngjz__jzor,
        name='str_to_uint64')
    return builder.call(gkus__mrp, (ewbej__cnorf.data, ewbej__cnorf.length))


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        lsyk__jwkj = ', '.join('e{}'.format(kbys__mmd) for kbys__mmd in
            range(len(args)))
        if lsyk__jwkj:
            lsyk__jwkj += ', '
        ygms__zxw = ', '.join("{} = ''".format(a) for a in kws.keys())
        vaf__npb = f'def format_stub(string, {lsyk__jwkj} {ygms__zxw}):\n'
        vaf__npb += '    pass\n'
        ondr__nkge = {}
        exec(vaf__npb, {}, ondr__nkge)
        ssy__jcn = ondr__nkge['format_stub']
        lyphz__nxvu = numba.core.utils.pysignature(ssy__jcn)
        vdqyu__gzukl = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, vdqyu__gzukl).replace(pysig=lyphz__nxvu)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    vog__jjkyf = pat is not None and len(pat) > 1
    if vog__jjkyf:
        sbom__qcig = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    uzom__xzj = len(arr)
    lbla__cyiq = 0
    umgb__vvct = 0
    for kbys__mmd in numba.parfors.parfor.internal_prange(uzom__xzj):
        if bodo.libs.array_kernels.isna(arr, kbys__mmd):
            continue
        if vog__jjkyf:
            fofws__npapl = sbom__qcig.split(arr[kbys__mmd], maxsplit=n)
        elif pat == '':
            fofws__npapl = [''] + list(arr[kbys__mmd]) + ['']
        else:
            fofws__npapl = arr[kbys__mmd].split(pat, n)
        lbla__cyiq += len(fofws__npapl)
        for s in fofws__npapl:
            umgb__vvct += bodo.libs.str_arr_ext.get_utf8_size(s)
    iuxq__tupjq = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        uzom__xzj, (lbla__cyiq, umgb__vvct), bodo.libs.str_arr_ext.
        string_array_type)
    ccd__poyq = bodo.libs.array_item_arr_ext.get_offsets(iuxq__tupjq)
    uqg__cvpfz = bodo.libs.array_item_arr_ext.get_null_bitmap(iuxq__tupjq)
    ajz__qabdk = bodo.libs.array_item_arr_ext.get_data(iuxq__tupjq)
    whwq__hang = 0
    for exmhc__zxug in numba.parfors.parfor.internal_prange(uzom__xzj):
        ccd__poyq[exmhc__zxug] = whwq__hang
        if bodo.libs.array_kernels.isna(arr, exmhc__zxug):
            bodo.libs.int_arr_ext.set_bit_to_arr(uqg__cvpfz, exmhc__zxug, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(uqg__cvpfz, exmhc__zxug, 1)
        if vog__jjkyf:
            fofws__npapl = sbom__qcig.split(arr[exmhc__zxug], maxsplit=n)
        elif pat == '':
            fofws__npapl = [''] + list(arr[exmhc__zxug]) + ['']
        else:
            fofws__npapl = arr[exmhc__zxug].split(pat, n)
        rut__cwyw = len(fofws__npapl)
        for brok__bkx in range(rut__cwyw):
            s = fofws__npapl[brok__bkx]
            ajz__qabdk[whwq__hang] = s
            whwq__hang += 1
    ccd__poyq[uzom__xzj] = whwq__hang
    return iuxq__tupjq


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                oah__rwcf = '-0x'
                x = x * -1
            else:
                oah__rwcf = '0x'
            x = np.uint64(x)
            if x == 0:
                fro__hdpk = 1
            else:
                fro__hdpk = fast_ceil_log2(x + 1)
                fro__hdpk = (fro__hdpk + 3) // 4
            length = len(oah__rwcf) + fro__hdpk
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, oah__rwcf._data,
                len(oah__rwcf), 1)
            int_to_hex(output, fro__hdpk, len(oah__rwcf), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    cbs__viwq = 0 if x & x - 1 == 0 else 1
    qjpr__kuw = [np.uint64(18446744069414584320), np.uint64(4294901760), np
        .uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    fihiw__yys = 32
    for kbys__mmd in range(len(qjpr__kuw)):
        qyb__qxngo = 0 if x & qjpr__kuw[kbys__mmd] == 0 else fihiw__yys
        cbs__viwq = cbs__viwq + qyb__qxngo
        x = x >> qyb__qxngo
        fihiw__yys = fihiw__yys >> 1
    return cbs__viwq


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        rxub__nfe = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        ngjz__jzor = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        kpmv__nzyzh = cgutils.get_or_insert_function(builder.module,
            ngjz__jzor, name='int_to_hex')
        cnmix__ypw = builder.inttoptr(builder.add(builder.ptrtoint(
            rxub__nfe.data, lir.IntType(64)), header_len), lir.IntType(8).
            as_pointer())
        builder.call(kpmv__nzyzh, (cnmix__ypw, out_len, int_val))
    return types.void(output, out_len, header_len, int_val), codegen


def alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    pass


@overload(alloc_empty_bytes_or_string_data)
def overload_alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    typ = typ.instance_type if isinstance(typ, types.TypeRef) else typ
    if typ == bodo.bytes_type:
        return lambda typ, kind, length, is_ascii=0: np.empty(length, np.uint8)
    if typ == string_type:
        return (lambda typ, kind, length, is_ascii=0: numba.cpython.unicode
            ._empty_string(kind, length, is_ascii))
    raise BodoError(
        f'Internal Error: Expected Bytes or String type, found {typ}')


def get_unicode_or_numpy_data(val):
    pass


@overload(get_unicode_or_numpy_data)
def overload_get_unicode_or_numpy_data(val):
    if val == string_type:
        return lambda val: val._data
    if isinstance(val, types.Array):
        return lambda val: val.ctypes
    raise BodoError(
        f'Internal Error: Expected String or Numpy Array, found {val}')
