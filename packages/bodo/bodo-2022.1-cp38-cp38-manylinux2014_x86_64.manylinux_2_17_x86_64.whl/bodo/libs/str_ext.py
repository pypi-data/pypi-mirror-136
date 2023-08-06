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
    uyax__qjw = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        lhlgs__lngux, = args
        ktbl__hwvo = cgutils.create_struct_proxy(string_type)(context,
            builder, value=lhlgs__lngux)
        xjeus__woal = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        fkhag__pvy = cgutils.create_struct_proxy(uyax__qjw)(context, builder)
        is_ascii = builder.icmp_unsigned('==', ktbl__hwvo.is_ascii, lir.
            Constant(ktbl__hwvo.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (then, orelse):
            with then:
                context.nrt.incref(builder, string_type, lhlgs__lngux)
                xjeus__woal.data = ktbl__hwvo.data
                xjeus__woal.meminfo = ktbl__hwvo.meminfo
                fkhag__pvy.f1 = ktbl__hwvo.length
            with orelse:
                alvqn__ayopb = lir.FunctionType(lir.IntType(64), [lir.
                    IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                    lir.IntType(64), lir.IntType(32)])
                yrhsp__evvqx = cgutils.get_or_insert_function(builder.
                    module, alvqn__ayopb, name='unicode_to_utf8')
                oqdb__ymfkt = context.get_constant_null(types.voidptr)
                lto__ntnre = builder.call(yrhsp__evvqx, [oqdb__ymfkt,
                    ktbl__hwvo.data, ktbl__hwvo.length, ktbl__hwvo.kind])
                fkhag__pvy.f1 = lto__ntnre
                orgtl__dsax = builder.add(lto__ntnre, lir.Constant(lir.
                    IntType(64), 1))
                xjeus__woal.meminfo = context.nrt.meminfo_alloc_aligned(builder
                    , size=orgtl__dsax, align=32)
                xjeus__woal.data = context.nrt.meminfo_data(builder,
                    xjeus__woal.meminfo)
                builder.call(yrhsp__evvqx, [xjeus__woal.data, ktbl__hwvo.
                    data, ktbl__hwvo.length, ktbl__hwvo.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    xjeus__woal.data, [lto__ntnre]))
        fkhag__pvy.f0 = xjeus__woal._getvalue()
        return fkhag__pvy._getvalue()
    return uyax__qjw(string_type), codegen


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
        alvqn__ayopb = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        snp__upmg = cgutils.get_or_insert_function(builder.module,
            alvqn__ayopb, name='memcmp')
        return builder.call(snp__upmg, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    iaa__for = n(10)

    def impl(n):
        if n == 0:
            return 1
        odm__cgoen = 0
        if n < 0:
            n = -n
            odm__cgoen += 1
        while n > 0:
            n = n // iaa__for
            odm__cgoen += 1
        return odm__cgoen
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
        [xdbc__xlbqv] = args
        if isinstance(xdbc__xlbqv, StdStringType):
            return signature(types.float64, xdbc__xlbqv)
        if xdbc__xlbqv == string_type:
            return signature(types.float64, xdbc__xlbqv)


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
    ktbl__hwvo = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    alvqn__ayopb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    vvktr__pzs = cgutils.get_or_insert_function(builder.module,
        alvqn__ayopb, name='init_string_const')
    return builder.call(vvktr__pzs, [ktbl__hwvo.data, ktbl__hwvo.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        agnyi__iwdtd = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(agnyi__iwdtd._data, bodo.libs.str_ext
            .get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return agnyi__iwdtd
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    ktbl__hwvo = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return ktbl__hwvo.data


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
        utat__cmagm = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, utat__cmagm)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        yqk__wvps, = args
        suj__ukqi = types.List(string_type)
        dfk__ppz = numba.cpython.listobj.ListInstance.allocate(context,
            builder, suj__ukqi, yqk__wvps)
        dfk__ppz.size = yqk__wvps
        vyw__aqwd = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        vyw__aqwd.data = dfk__ppz.value
        return vyw__aqwd._getvalue()
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
            evi__rnww = 0
            crm__wbx = v
            if crm__wbx < 0:
                evi__rnww = 1
                crm__wbx = -crm__wbx
            if crm__wbx < 1:
                ato__cvbhu = 1
            else:
                ato__cvbhu = 1 + int(np.floor(np.log10(crm__wbx)))
            length = evi__rnww + ato__cvbhu + 1 + 6
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
    alvqn__ayopb = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    vvktr__pzs = cgutils.get_or_insert_function(builder.module,
        alvqn__ayopb, name='str_to_float64')
    return builder.call(vvktr__pzs, (val,))


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    alvqn__ayopb = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    vvktr__pzs = cgutils.get_or_insert_function(builder.module,
        alvqn__ayopb, name='str_to_float32')
    return builder.call(vvktr__pzs, (val,))


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
    ktbl__hwvo = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    alvqn__ayopb = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    vvktr__pzs = cgutils.get_or_insert_function(builder.module,
        alvqn__ayopb, name='str_to_int64')
    return builder.call(vvktr__pzs, (ktbl__hwvo.data, ktbl__hwvo.length))


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    ktbl__hwvo = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    alvqn__ayopb = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    vvktr__pzs = cgutils.get_or_insert_function(builder.module,
        alvqn__ayopb, name='str_to_uint64')
    return builder.call(vvktr__pzs, (ktbl__hwvo.data, ktbl__hwvo.length))


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        wtzco__ouciz = ', '.join('e{}'.format(ehmo__lrfv) for ehmo__lrfv in
            range(len(args)))
        if wtzco__ouciz:
            wtzco__ouciz += ', '
        fvz__vggkc = ', '.join("{} = ''".format(a) for a in kws.keys())
        aerdn__fvjr = (
            f'def format_stub(string, {wtzco__ouciz} {fvz__vggkc}):\n')
        aerdn__fvjr += '    pass\n'
        bqre__cosfk = {}
        exec(aerdn__fvjr, {}, bqre__cosfk)
        dcq__yyvfq = bqre__cosfk['format_stub']
        vmgt__yck = numba.core.utils.pysignature(dcq__yyvfq)
        zcig__jsns = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, zcig__jsns).replace(pysig=vmgt__yck)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    ypqst__owamg = pat is not None and len(pat) > 1
    if ypqst__owamg:
        mouaf__fqrfo = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    dfk__ppz = len(arr)
    nyxok__dhid = 0
    rzew__dkg = 0
    for ehmo__lrfv in numba.parfors.parfor.internal_prange(dfk__ppz):
        if bodo.libs.array_kernels.isna(arr, ehmo__lrfv):
            continue
        if ypqst__owamg:
            wca__miw = mouaf__fqrfo.split(arr[ehmo__lrfv], maxsplit=n)
        elif pat == '':
            wca__miw = [''] + list(arr[ehmo__lrfv]) + ['']
        else:
            wca__miw = arr[ehmo__lrfv].split(pat, n)
        nyxok__dhid += len(wca__miw)
        for s in wca__miw:
            rzew__dkg += bodo.libs.str_arr_ext.get_utf8_size(s)
    oljj__pmwjb = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        dfk__ppz, (nyxok__dhid, rzew__dkg), bodo.libs.str_arr_ext.
        string_array_type)
    ejgir__lbp = bodo.libs.array_item_arr_ext.get_offsets(oljj__pmwjb)
    twxld__vohac = bodo.libs.array_item_arr_ext.get_null_bitmap(oljj__pmwjb)
    gndk__efggo = bodo.libs.array_item_arr_ext.get_data(oljj__pmwjb)
    wwbiy__iix = 0
    for qwwm__ldrqb in numba.parfors.parfor.internal_prange(dfk__ppz):
        ejgir__lbp[qwwm__ldrqb] = wwbiy__iix
        if bodo.libs.array_kernels.isna(arr, qwwm__ldrqb):
            bodo.libs.int_arr_ext.set_bit_to_arr(twxld__vohac, qwwm__ldrqb, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(twxld__vohac, qwwm__ldrqb, 1)
        if ypqst__owamg:
            wca__miw = mouaf__fqrfo.split(arr[qwwm__ldrqb], maxsplit=n)
        elif pat == '':
            wca__miw = [''] + list(arr[qwwm__ldrqb]) + ['']
        else:
            wca__miw = arr[qwwm__ldrqb].split(pat, n)
        qihoo__iyxh = len(wca__miw)
        for peyyb__ylqr in range(qihoo__iyxh):
            s = wca__miw[peyyb__ylqr]
            gndk__efggo[wwbiy__iix] = s
            wwbiy__iix += 1
    ejgir__lbp[dfk__ppz] = wwbiy__iix
    return oljj__pmwjb


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                olit__byucr = '-0x'
                x = x * -1
            else:
                olit__byucr = '0x'
            x = np.uint64(x)
            if x == 0:
                zit__qarbp = 1
            else:
                zit__qarbp = fast_ceil_log2(x + 1)
                zit__qarbp = (zit__qarbp + 3) // 4
            length = len(olit__byucr) + zit__qarbp
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, olit__byucr._data,
                len(olit__byucr), 1)
            int_to_hex(output, zit__qarbp, len(olit__byucr), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    fojl__umi = 0 if x & x - 1 == 0 else 1
    fqt__gks = [np.uint64(18446744069414584320), np.uint64(4294901760), np.
        uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    tuxsg__szgr = 32
    for ehmo__lrfv in range(len(fqt__gks)):
        tidrq__ymocl = 0 if x & fqt__gks[ehmo__lrfv] == 0 else tuxsg__szgr
        fojl__umi = fojl__umi + tidrq__ymocl
        x = x >> tidrq__ymocl
        tuxsg__szgr = tuxsg__szgr >> 1
    return fojl__umi


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        gbu__vkpw = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        alvqn__ayopb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        mvxa__ules = cgutils.get_or_insert_function(builder.module,
            alvqn__ayopb, name='int_to_hex')
        ttjkb__gexkw = builder.inttoptr(builder.add(builder.ptrtoint(
            gbu__vkpw.data, lir.IntType(64)), header_len), lir.IntType(8).
            as_pointer())
        builder.call(mvxa__ules, (ttjkb__gexkw, out_len, int_val))
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
