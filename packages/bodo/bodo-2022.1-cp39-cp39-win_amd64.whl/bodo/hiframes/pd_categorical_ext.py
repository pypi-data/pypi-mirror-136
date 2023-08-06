import enum
import operator
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.utils.typing import NOT_CONSTANT, BodoError, MetaType, check_unsupported_args, dtype_to_array_type, get_literal_value, get_overload_const, get_overload_const_bool, is_common_scalar_dtype, is_iterable_type, is_list_like_index_type, is_literal_type, is_overload_constant_bool, is_overload_none, is_overload_true, is_scalar_type, raise_bodo_error


class PDCategoricalDtype(types.Opaque):

    def __init__(self, categories, elem_type, ordered, data=None, int_type=None
        ):
        self.categories = categories
        self.elem_type = elem_type
        self.ordered = ordered
        self.data = _get_cat_index_type(elem_type) if data is None else data
        self.int_type = int_type
        gct__bba = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=gct__bba)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    hhvfx__opjpl = tuple(val.categories.values)
    elem_type = None if len(hhvfx__opjpl) == 0 else bodo.typeof(val.
        categories.values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(hhvfx__opjpl, elem_type, val.ordered, bodo.
        typeof(val.categories), int_type)


def _get_cat_index_type(elem_type):
    elem_type = bodo.string_type if elem_type is None else elem_type
    return bodo.utils.typing.get_index_type_from_dtype(elem_type)


@lower_constant(PDCategoricalDtype)
def lower_constant_categorical_type(context, builder, typ, pyval):
    categories = context.get_constant_generic(builder, bodo.typeof(pyval.
        categories), pyval.categories)
    ordered = context.get_constant(types.bool_, pyval.ordered)
    return lir.Constant.literal_struct([categories, ordered])


@register_model(PDCategoricalDtype)
class PDCategoricalDtypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        llcq__kzpx = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, llcq__kzpx)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    hfod__ppz = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    ase__yqvco = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, jljp__wrmc, jljp__wrmc = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    fkd__opdb = PDCategoricalDtype(ase__yqvco, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, hfod__ppz)
    return fkd__opdb(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    qbx__hxj = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, qbx__hxj).value
    c.pyapi.decref(qbx__hxj)
    ujl__oek = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, ujl__oek).value
    c.pyapi.decref(ujl__oek)
    fbzq__oglix = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=fbzq__oglix)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    qbx__hxj = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    anhnd__woz = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    rant__ehfic = c.context.insert_const_string(c.builder.module, 'pandas')
    hvm__ojuz = c.pyapi.import_module_noblock(rant__ehfic)
    ehrxv__jozj = c.pyapi.call_method(hvm__ojuz, 'CategoricalDtype', (
        anhnd__woz, qbx__hxj))
    c.pyapi.decref(qbx__hxj)
    c.pyapi.decref(anhnd__woz)
    c.pyapi.decref(hvm__ojuz)
    c.context.nrt.decref(c.builder, typ, val)
    return ehrxv__jozj


@overload_attribute(PDCategoricalDtype, 'nbytes')
def pd_categorical_nbytes_overload(A):
    return lambda A: A.categories.nbytes + bodo.io.np_io.get_dtype_size(types
        .bool_)


class CategoricalArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(CategoricalArrayType, self).__init__(name=
            'CategoricalArrayType({})'.format(dtype))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return CategoricalArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.Categorical)
def _typeof_pd_cat(val, c):
    return CategoricalArrayType(bodo.typeof(val.dtype))


@register_model(CategoricalArrayType)
class CategoricalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        eljpo__tod = get_categories_int_type(fe_type.dtype)
        llcq__kzpx = [('dtype', fe_type.dtype), ('codes', types.Array(
            eljpo__tod, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, llcq__kzpx)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    tclo__laqor = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), tclo__laqor
        ).value
    c.pyapi.decref(tclo__laqor)
    ehrxv__jozj = c.pyapi.object_getattr_string(val, 'dtype')
    dndac__ild = c.pyapi.to_native_value(typ.dtype, ehrxv__jozj).value
    c.pyapi.decref(ehrxv__jozj)
    cylxm__wchc = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    cylxm__wchc.codes = codes
    cylxm__wchc.dtype = dndac__ild
    return NativeValue(cylxm__wchc._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    zrlzb__plot = get_categories_int_type(typ.dtype)
    whh__xjjoc = context.get_constant_generic(builder, types.Array(
        zrlzb__plot, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, whh__xjjoc])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    qber__msoeu = len(cat_dtype.categories)
    if qber__msoeu < np.iinfo(np.int8).max:
        dtype = types.int8
    elif qber__msoeu < np.iinfo(np.int16).max:
        dtype = types.int16
    elif qber__msoeu < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    rant__ehfic = c.context.insert_const_string(c.builder.module, 'pandas')
    hvm__ojuz = c.pyapi.import_module_noblock(rant__ehfic)
    eljpo__tod = get_categories_int_type(dtype)
    lwx__wwqil = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    pjeof__cdv = types.Array(eljpo__tod, 1, 'C')
    c.context.nrt.incref(c.builder, pjeof__cdv, lwx__wwqil.codes)
    tclo__laqor = c.pyapi.from_native_value(pjeof__cdv, lwx__wwqil.codes, c
        .env_manager)
    c.context.nrt.incref(c.builder, dtype, lwx__wwqil.dtype)
    ehrxv__jozj = c.pyapi.from_native_value(dtype, lwx__wwqil.dtype, c.
        env_manager)
    itert__fazdf = c.pyapi.borrow_none()
    ufoxb__jvgp = c.pyapi.object_getattr_string(hvm__ojuz, 'Categorical')
    rnogx__qasjw = c.pyapi.call_method(ufoxb__jvgp, 'from_codes', (
        tclo__laqor, itert__fazdf, itert__fazdf, ehrxv__jozj))
    c.pyapi.decref(ufoxb__jvgp)
    c.pyapi.decref(tclo__laqor)
    c.pyapi.decref(ehrxv__jozj)
    c.pyapi.decref(hvm__ojuz)
    c.context.nrt.decref(c.builder, typ, val)
    return rnogx__qasjw


def _to_readonly(t):
    from bodo.hiframes.pd_index_ext import DatetimeIndexType, NumericIndexType, TimedeltaIndexType
    if isinstance(t, types.Array):
        return types.Array(t.dtype, t.ndim, 'C', True)
    if isinstance(t, NumericIndexType):
        return NumericIndexType(t.dtype, t.name_typ, _to_readonly(t.data))
    if isinstance(t, (DatetimeIndexType, TimedeltaIndexType)):
        return t.__class__(t.name_typ, _to_readonly(t.data))
    return t


@lower_cast(CategoricalArrayType, CategoricalArrayType)
def cast_cat_arr(context, builder, fromty, toty, val):
    doc__qlqto = toty.dtype
    qyun__avbxj = PDCategoricalDtype(doc__qlqto.categories, doc__qlqto.
        elem_type, doc__qlqto.ordered, _to_readonly(doc__qlqto.data),
        doc__qlqto.int_type)
    if qyun__avbxj == fromty.dtype:
        return val
    raise BodoError(f'Cannot cast from {fromty} to {toty}')


def create_cmp_op_overload(op):

    def overload_cat_arr_cmp(A, other):
        if not isinstance(A, CategoricalArrayType):
            return
        if A.dtype.categories and is_literal_type(other) and types.unliteral(
            other) == A.dtype.elem_type:
            val = get_literal_value(other)
            teqg__fbha = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                clpge__yvcp = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), teqg__fbha)
                return clpge__yvcp
            return impl_lit

        def impl(A, other):
            teqg__fbha = get_code_for_value(A.dtype, other)
            clpge__yvcp = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), teqg__fbha)
            return clpge__yvcp
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        hndrh__ayi = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(hndrh__ayi)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    lwx__wwqil = cat_dtype.categories
    n = len(lwx__wwqil)
    for jkg__wge in range(n):
        if lwx__wwqil[jkg__wge] == val:
            return jkg__wge
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    vsr__zxrk = bodo.utils.typing.parse_dtype(dtype, 'CategoricalArray.astype')
    if vsr__zxrk != A.dtype.elem_type and vsr__zxrk != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if vsr__zxrk == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            clpge__yvcp = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for jkg__wge in numba.parfors.parfor.internal_prange(n):
                iiu__vtnm = codes[jkg__wge]
                if iiu__vtnm == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(
                            clpge__yvcp, jkg__wge)
                    else:
                        bodo.libs.array_kernels.setna(clpge__yvcp, jkg__wge)
                    continue
                clpge__yvcp[jkg__wge] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[iiu__vtnm]))
            return clpge__yvcp
        return impl
    pjeof__cdv = dtype_to_array_type(vsr__zxrk)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        clpge__yvcp = bodo.utils.utils.alloc_type(n, pjeof__cdv, (-1,))
        for jkg__wge in numba.parfors.parfor.internal_prange(n):
            iiu__vtnm = codes[jkg__wge]
            if iiu__vtnm == -1:
                bodo.libs.array_kernels.setna(clpge__yvcp, jkg__wge)
                continue
            clpge__yvcp[jkg__wge] = bodo.utils.conversion.unbox_if_timestamp(
                categories[iiu__vtnm])
        return clpge__yvcp
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        smpr__bwicb, dndac__ild = args
        lwx__wwqil = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        lwx__wwqil.codes = smpr__bwicb
        lwx__wwqil.dtype = dndac__ild
        context.nrt.incref(builder, signature.args[0], smpr__bwicb)
        context.nrt.incref(builder, signature.args[1], dndac__ild)
        return lwx__wwqil._getvalue()
    rpet__dszs = CategoricalArrayType(cat_dtype)
    sig = rpet__dszs(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    qerp__wrf = args[0]
    if equiv_set.has_shape(qerp__wrf):
        return ArrayAnalysis.AnalyzeResult(shape=qerp__wrf, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    eljpo__tod = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, eljpo__tod)
        return init_categorical_array(codes, cat_dtype)
    return impl


def alloc_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_alloc_categorical_array
    ) = alloc_categorical_array_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_categorical_arr_codes(A):
    return lambda A: A.codes


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_categorical_array',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_categorical_arr_codes',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func


@overload_method(CategoricalArrayType, 'copy', no_unliteral=True)
def cat_arr_copy_overload(arr):
    return lambda arr: init_categorical_array(arr.codes.copy(), arr.dtype)


def build_replace_dicts(to_replace, value, categories):
    return dict(), np.empty(len(categories) + 1), 0


@overload(build_replace_dicts, no_unliteral=True)
def _build_replace_dicts(to_replace, value, categories):
    if isinstance(to_replace, types.Number) or to_replace == bodo.string_type:

        def impl(to_replace, value, categories):
            return build_replace_dicts([to_replace], value, categories)
        return impl
    else:

        def impl(to_replace, value, categories):
            n = len(categories)
            kfpev__usb = {}
            whh__xjjoc = np.empty(n + 1, np.int64)
            dseqb__ctoal = {}
            pfwh__mnuq = []
            esyrx__orpl = {}
            for jkg__wge in range(n):
                esyrx__orpl[categories[jkg__wge]] = jkg__wge
            for nru__pjct in to_replace:
                if nru__pjct != value:
                    if nru__pjct in esyrx__orpl:
                        if value in esyrx__orpl:
                            kfpev__usb[nru__pjct] = nru__pjct
                            akwp__mjuwp = esyrx__orpl[nru__pjct]
                            dseqb__ctoal[akwp__mjuwp] = esyrx__orpl[value]
                            pfwh__mnuq.append(akwp__mjuwp)
                        else:
                            kfpev__usb[nru__pjct] = value
                            esyrx__orpl[value] = esyrx__orpl[nru__pjct]
            hbv__zgz = np.sort(np.array(pfwh__mnuq))
            oxc__rzq = 0
            ewpv__qsrvk = []
            for wdwjj__lgrb in range(-1, n):
                while oxc__rzq < len(hbv__zgz) and wdwjj__lgrb > hbv__zgz[
                    oxc__rzq]:
                    oxc__rzq += 1
                ewpv__qsrvk.append(oxc__rzq)
            for qjfk__djtv in range(-1, n):
                xrxs__alty = qjfk__djtv
                if qjfk__djtv in dseqb__ctoal:
                    xrxs__alty = dseqb__ctoal[qjfk__djtv]
                whh__xjjoc[qjfk__djtv + 1] = xrxs__alty - ewpv__qsrvk[
                    xrxs__alty + 1]
            return kfpev__usb, whh__xjjoc, len(hbv__zgz)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for jkg__wge in range(len(new_codes_arr)):
        new_codes_arr[jkg__wge] = codes_map_arr[old_codes_arr[jkg__wge] + 1]


@overload_method(CategoricalArrayType, 'replace', inline='always',
    no_unliteral=True)
def overload_replace(arr, to_replace, value):

    def impl(arr, to_replace, value):
        return bodo.hiframes.pd_categorical_ext.cat_replace(arr, to_replace,
            value)
    return impl


def cat_replace(arr, to_replace, value):
    return


@overload(cat_replace, no_unliteral=True)
def cat_replace_overload(arr, to_replace, value):
    qxid__kqhm = arr.dtype.ordered
    xnq__qjorr = arr.dtype.elem_type
    tdj__uvur = get_overload_const(to_replace)
    lmi__wtf = get_overload_const(value)
    if (arr.dtype.categories is not None and tdj__uvur is not NOT_CONSTANT and
        lmi__wtf is not NOT_CONSTANT):
        bzv__fuih, codes_map_arr, jljp__wrmc = python_build_replace_dicts(
            tdj__uvur, lmi__wtf, arr.dtype.categories)
        if len(bzv__fuih) == 0:
            return lambda arr, to_replace, value: arr.copy()
        ukzd__jdjj = []
        for pywrv__ibvmm in arr.dtype.categories:
            if pywrv__ibvmm in bzv__fuih:
                sris__sioyk = bzv__fuih[pywrv__ibvmm]
                if sris__sioyk != pywrv__ibvmm:
                    ukzd__jdjj.append(sris__sioyk)
            else:
                ukzd__jdjj.append(pywrv__ibvmm)
        kuh__lhgz = pd.CategoricalDtype(ukzd__jdjj, qxid__kqhm
            ).categories.values
        pasn__gsfo = MetaType(tuple(kuh__lhgz))

        def impl_dtype(arr, to_replace, value):
            esvju__slrtx = init_cat_dtype(bodo.utils.conversion.
                index_from_array(kuh__lhgz), qxid__kqhm, None, pasn__gsfo)
            lwx__wwqil = alloc_categorical_array(len(arr.codes), esvju__slrtx)
            reassign_codes(lwx__wwqil.codes, arr.codes, codes_map_arr)
            return lwx__wwqil
        return impl_dtype
    xnq__qjorr = arr.dtype.elem_type
    if xnq__qjorr == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            kfpev__usb, codes_map_arr, hjen__rvwr = build_replace_dicts(
                to_replace, value, categories.values)
            if len(kfpev__usb) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), qxid__kqhm,
                    None, None))
            n = len(categories)
            kuh__lhgz = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                hjen__rvwr, -1)
            yqnpz__cufpn = 0
            for wdwjj__lgrb in range(n):
                usqs__hwv = categories[wdwjj__lgrb]
                if usqs__hwv in kfpev__usb:
                    bsbhn__ipd = kfpev__usb[usqs__hwv]
                    if bsbhn__ipd != usqs__hwv:
                        kuh__lhgz[yqnpz__cufpn] = bsbhn__ipd
                        yqnpz__cufpn += 1
                else:
                    kuh__lhgz[yqnpz__cufpn] = usqs__hwv
                    yqnpz__cufpn += 1
            lwx__wwqil = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                kuh__lhgz), qxid__kqhm, None, None))
            reassign_codes(lwx__wwqil.codes, arr.codes, codes_map_arr)
            return lwx__wwqil
        return impl_str
    dtv__wzib = dtype_to_array_type(xnq__qjorr)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        kfpev__usb, codes_map_arr, hjen__rvwr = build_replace_dicts(to_replace,
            value, categories.values)
        if len(kfpev__usb) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), qxid__kqhm, None, None))
        n = len(categories)
        kuh__lhgz = bodo.utils.utils.alloc_type(n - hjen__rvwr, dtv__wzib, None
            )
        yqnpz__cufpn = 0
        for jkg__wge in range(n):
            usqs__hwv = categories[jkg__wge]
            if usqs__hwv in kfpev__usb:
                bsbhn__ipd = kfpev__usb[usqs__hwv]
                if bsbhn__ipd != usqs__hwv:
                    kuh__lhgz[yqnpz__cufpn] = bsbhn__ipd
                    yqnpz__cufpn += 1
            else:
                kuh__lhgz[yqnpz__cufpn] = usqs__hwv
                yqnpz__cufpn += 1
        lwx__wwqil = alloc_categorical_array(len(arr.codes), init_cat_dtype
            (bodo.utils.conversion.index_from_array(kuh__lhgz), qxid__kqhm,
            None, None))
        reassign_codes(lwx__wwqil.codes, arr.codes, codes_map_arr)
        return lwx__wwqil
    return impl


@overload(len, no_unliteral=True)
def overload_cat_arr_len(A):
    if isinstance(A, CategoricalArrayType):
        return lambda A: len(A.codes)


@overload_attribute(CategoricalArrayType, 'shape')
def overload_cat_arr_shape(A):
    return lambda A: (len(A.codes),)


@overload_attribute(CategoricalArrayType, 'ndim')
def overload_cat_arr_ndim(A):
    return lambda A: 1


@overload_attribute(CategoricalArrayType, 'nbytes')
def cat_arr_nbytes_overload(A):
    return lambda A: A.codes.nbytes + A.dtype.nbytes


@register_jitable
def get_label_dict_from_categories(vals):
    ihjc__jsm = dict()
    vkmfi__bjam = 0
    for jkg__wge in range(len(vals)):
        val = vals[jkg__wge]
        if val in ihjc__jsm:
            continue
        ihjc__jsm[val] = vkmfi__bjam
        vkmfi__bjam += 1
    return ihjc__jsm


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    ihjc__jsm = dict()
    for jkg__wge in range(len(vals)):
        val = vals[jkg__wge]
        ihjc__jsm[val] = jkg__wge
    return ihjc__jsm


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    ebe__liw = dict(fastpath=fastpath)
    eknz__bvsol = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', ebe__liw, eknz__bvsol)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        ram__tqrr = get_overload_const(categories)
        if ram__tqrr is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                exmf__jonvg = False
            else:
                exmf__jonvg = get_overload_const_bool(ordered)
            xjddl__ohrc = pd.CategoricalDtype(ram__tqrr, exmf__jonvg
                ).categories.values
            zzkm__cckgg = MetaType(tuple(xjddl__ohrc))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                esvju__slrtx = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(xjddl__ohrc), exmf__jonvg, None,
                    zzkm__cckgg)
                return bodo.utils.conversion.fix_arr_dtype(data, esvju__slrtx)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            hhvfx__opjpl = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                hhvfx__opjpl, ordered, None, None)
            return bodo.utils.conversion.fix_arr_dtype(data, cat_dtype)
        return impl_cats
    elif is_overload_none(ordered):

        def impl_auto(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, 'category')
        return impl_auto
    raise BodoError(
        f'pd.Categorical(): argument combination not supported yet: {values}, {categories}, {ordered}, {dtype}'
        )


@overload(operator.getitem, no_unliteral=True)
def categorical_array_getitem(arr, ind):
    if not isinstance(arr, CategoricalArrayType):
        return
    if isinstance(ind, types.Integer):

        def categorical_getitem_impl(arr, ind):
            cnvyr__adx = arr.codes[ind]
            return arr.dtype.categories[max(cnvyr__adx, 0)]
        return categorical_getitem_impl
    if is_list_like_index_type(ind) or isinstance(ind, types.SliceType):

        def impl_bool(arr, ind):
            return init_categorical_array(arr.codes[ind], arr.dtype)
        return impl_bool
    raise BodoError(
        f'getitem for CategoricalArrayType with indexing type {ind} not supported.'
        )


class CategoricalMatchingValues(enum.Enum):
    DIFFERENT_TYPES = -1
    DONT_MATCH = 0
    MAY_MATCH = 1
    DO_MATCH = 2


def categorical_arrs_match(arr1, arr2):
    if not (isinstance(arr1, CategoricalArrayType) and isinstance(arr2,
        CategoricalArrayType)):
        return CategoricalMatchingValues.DIFFERENT_TYPES
    if arr1.dtype.categories is None or arr2.dtype.categories is None:
        return CategoricalMatchingValues.MAY_MATCH
    return (CategoricalMatchingValues.DO_MATCH if arr1.dtype.categories ==
        arr2.dtype.categories and arr1.dtype.ordered == arr2.dtype.ordered else
        CategoricalMatchingValues.DONT_MATCH)


@register_jitable
def cat_dtype_equal(dtype1, dtype2):
    if dtype1.ordered != dtype2.ordered or len(dtype1.categories) != len(dtype2
        .categories):
        return False
    arr1 = dtype1.categories.values
    arr2 = dtype2.categories.values
    for jkg__wge in range(len(arr1)):
        if arr1[jkg__wge] != arr2[jkg__wge]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    bmgps__xtgco = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    lrvbz__iak = not isinstance(val, CategoricalArrayType
        ) and is_iterable_type(val) and is_common_scalar_dtype([val.dtype,
        arr.dtype.elem_type]) and not (isinstance(arr.dtype.elem_type,
        types.Integer) and isinstance(val.dtype, types.Float))
    dpn__mrl = categorical_arrs_match(arr, val)
    ftdls__hkf = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    czofe__fpcxg = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not bmgps__xtgco:
            raise BodoError(ftdls__hkf)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            cnvyr__adx = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = cnvyr__adx
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (bmgps__xtgco or lrvbz__iak or dpn__mrl !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(ftdls__hkf)
        if dpn__mrl == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(czofe__fpcxg)
        if bmgps__xtgco:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                odx__gnt = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for wdwjj__lgrb in range(n):
                    arr.codes[ind[wdwjj__lgrb]] = odx__gnt
            return impl_scalar
        if dpn__mrl == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for jkg__wge in range(n):
                    arr.codes[ind[jkg__wge]] = val.codes[jkg__wge]
            return impl_arr_ind_mask
        if dpn__mrl == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(czofe__fpcxg)
                n = len(val.codes)
                for jkg__wge in range(n):
                    arr.codes[ind[jkg__wge]] = val.codes[jkg__wge]
            return impl_arr_ind_mask
        if lrvbz__iak:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for wdwjj__lgrb in range(n):
                    izti__vdwsf = bodo.utils.conversion.unbox_if_timestamp(val
                        [wdwjj__lgrb])
                    if izti__vdwsf not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    cnvyr__adx = categories.get_loc(izti__vdwsf)
                    arr.codes[ind[wdwjj__lgrb]] = cnvyr__adx
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (bmgps__xtgco or lrvbz__iak or dpn__mrl !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(ftdls__hkf)
        if dpn__mrl == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(czofe__fpcxg)
        if bmgps__xtgco:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                odx__gnt = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for wdwjj__lgrb in range(n):
                    if ind[wdwjj__lgrb]:
                        arr.codes[wdwjj__lgrb] = odx__gnt
            return impl_scalar
        if dpn__mrl == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                tth__dblx = 0
                for jkg__wge in range(n):
                    if ind[jkg__wge]:
                        arr.codes[jkg__wge] = val.codes[tth__dblx]
                        tth__dblx += 1
            return impl_bool_ind_mask
        if dpn__mrl == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(czofe__fpcxg)
                n = len(ind)
                tth__dblx = 0
                for jkg__wge in range(n):
                    if ind[jkg__wge]:
                        arr.codes[jkg__wge] = val.codes[tth__dblx]
                        tth__dblx += 1
            return impl_bool_ind_mask
        if lrvbz__iak:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                tth__dblx = 0
                categories = arr.dtype.categories
                for wdwjj__lgrb in range(n):
                    if ind[wdwjj__lgrb]:
                        izti__vdwsf = bodo.utils.conversion.unbox_if_timestamp(
                            val[tth__dblx])
                        if izti__vdwsf not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        cnvyr__adx = categories.get_loc(izti__vdwsf)
                        arr.codes[wdwjj__lgrb] = cnvyr__adx
                        tth__dblx += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (bmgps__xtgco or lrvbz__iak or dpn__mrl !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(ftdls__hkf)
        if dpn__mrl == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(czofe__fpcxg)
        if bmgps__xtgco:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                odx__gnt = arr.dtype.categories.get_loc(val)
                xymo__cqk = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                for wdwjj__lgrb in range(xymo__cqk.start, xymo__cqk.stop,
                    xymo__cqk.step):
                    arr.codes[wdwjj__lgrb] = odx__gnt
            return impl_scalar
        if dpn__mrl == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if dpn__mrl == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(czofe__fpcxg)
                arr.codes[ind] = val.codes
            return impl_arr
        if lrvbz__iak:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                xymo__cqk = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                tth__dblx = 0
                for wdwjj__lgrb in range(xymo__cqk.start, xymo__cqk.stop,
                    xymo__cqk.step):
                    izti__vdwsf = bodo.utils.conversion.unbox_if_timestamp(val
                        [tth__dblx])
                    if izti__vdwsf not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    cnvyr__adx = categories.get_loc(izti__vdwsf)
                    arr.codes[wdwjj__lgrb] = cnvyr__adx
                    tth__dblx += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
