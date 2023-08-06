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
        zvysw__yrxer = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=zvysw__yrxer)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    clbk__adp = tuple(val.categories.values)
    elem_type = None if len(clbk__adp) == 0 else bodo.typeof(val.categories
        .values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(clbk__adp, elem_type, val.ordered, bodo.
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
        wldm__fxa = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, wldm__fxa)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    ebug__jfgh = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    xijb__awgy = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, iojs__xxat, iojs__xxat = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    ohd__pnsn = PDCategoricalDtype(xijb__awgy, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, ebug__jfgh)
    return ohd__pnsn(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    uwzke__lpg = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, uwzke__lpg).value
    c.pyapi.decref(uwzke__lpg)
    wjrwf__vqkk = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, wjrwf__vqkk).value
    c.pyapi.decref(wjrwf__vqkk)
    nwzy__tuj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=nwzy__tuj)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    uwzke__lpg = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    aae__gwtg = c.pyapi.from_native_value(typ.data, cat_dtype.categories, c
        .env_manager)
    rah__mzmx = c.context.insert_const_string(c.builder.module, 'pandas')
    loncc__tferv = c.pyapi.import_module_noblock(rah__mzmx)
    iil__vrxz = c.pyapi.call_method(loncc__tferv, 'CategoricalDtype', (
        aae__gwtg, uwzke__lpg))
    c.pyapi.decref(uwzke__lpg)
    c.pyapi.decref(aae__gwtg)
    c.pyapi.decref(loncc__tferv)
    c.context.nrt.decref(c.builder, typ, val)
    return iil__vrxz


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
        zwt__swkrv = get_categories_int_type(fe_type.dtype)
        wldm__fxa = [('dtype', fe_type.dtype), ('codes', types.Array(
            zwt__swkrv, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, wldm__fxa)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    olw__mgxeu = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), olw__mgxeu
        ).value
    c.pyapi.decref(olw__mgxeu)
    iil__vrxz = c.pyapi.object_getattr_string(val, 'dtype')
    ctoqh__swst = c.pyapi.to_native_value(typ.dtype, iil__vrxz).value
    c.pyapi.decref(iil__vrxz)
    qdsn__eks = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    qdsn__eks.codes = codes
    qdsn__eks.dtype = ctoqh__swst
    return NativeValue(qdsn__eks._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    bppeo__ecrm = get_categories_int_type(typ.dtype)
    pee__vey = context.get_constant_generic(builder, types.Array(
        bppeo__ecrm, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, pee__vey])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    vhq__dzgwe = len(cat_dtype.categories)
    if vhq__dzgwe < np.iinfo(np.int8).max:
        dtype = types.int8
    elif vhq__dzgwe < np.iinfo(np.int16).max:
        dtype = types.int16
    elif vhq__dzgwe < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    rah__mzmx = c.context.insert_const_string(c.builder.module, 'pandas')
    loncc__tferv = c.pyapi.import_module_noblock(rah__mzmx)
    zwt__swkrv = get_categories_int_type(dtype)
    xmnmp__ywlkh = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    sxwcb__dtpst = types.Array(zwt__swkrv, 1, 'C')
    c.context.nrt.incref(c.builder, sxwcb__dtpst, xmnmp__ywlkh.codes)
    olw__mgxeu = c.pyapi.from_native_value(sxwcb__dtpst, xmnmp__ywlkh.codes,
        c.env_manager)
    c.context.nrt.incref(c.builder, dtype, xmnmp__ywlkh.dtype)
    iil__vrxz = c.pyapi.from_native_value(dtype, xmnmp__ywlkh.dtype, c.
        env_manager)
    xlenp__ydpw = c.pyapi.borrow_none()
    ljgo__frwyp = c.pyapi.object_getattr_string(loncc__tferv, 'Categorical')
    vvv__crtyb = c.pyapi.call_method(ljgo__frwyp, 'from_codes', (olw__mgxeu,
        xlenp__ydpw, xlenp__ydpw, iil__vrxz))
    c.pyapi.decref(ljgo__frwyp)
    c.pyapi.decref(olw__mgxeu)
    c.pyapi.decref(iil__vrxz)
    c.pyapi.decref(loncc__tferv)
    c.context.nrt.decref(c.builder, typ, val)
    return vvv__crtyb


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
    cpfir__fdm = toty.dtype
    nys__vplm = PDCategoricalDtype(cpfir__fdm.categories, cpfir__fdm.
        elem_type, cpfir__fdm.ordered, _to_readonly(cpfir__fdm.data),
        cpfir__fdm.int_type)
    if nys__vplm == fromty.dtype:
        return val
    raise BodoError(f'Cannot cast from {fromty} to {toty}')


def create_cmp_op_overload(op):

    def overload_cat_arr_cmp(A, other):
        if not isinstance(A, CategoricalArrayType):
            return
        if A.dtype.categories and is_literal_type(other) and types.unliteral(
            other) == A.dtype.elem_type:
            val = get_literal_value(other)
            zdv__pom = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                sjar__pspsd = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), zdv__pom)
                return sjar__pspsd
            return impl_lit

        def impl(A, other):
            zdv__pom = get_code_for_value(A.dtype, other)
            sjar__pspsd = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), zdv__pom)
            return sjar__pspsd
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        grjuf__vxcwu = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(grjuf__vxcwu)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    xmnmp__ywlkh = cat_dtype.categories
    n = len(xmnmp__ywlkh)
    for rsr__fbr in range(n):
        if xmnmp__ywlkh[rsr__fbr] == val:
            return rsr__fbr
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    yjl__ihid = bodo.utils.typing.parse_dtype(dtype, 'CategoricalArray.astype')
    if yjl__ihid != A.dtype.elem_type and yjl__ihid != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if yjl__ihid == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            sjar__pspsd = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for rsr__fbr in numba.parfors.parfor.internal_prange(n):
                sdcza__hgc = codes[rsr__fbr]
                if sdcza__hgc == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(
                            sjar__pspsd, rsr__fbr)
                    else:
                        bodo.libs.array_kernels.setna(sjar__pspsd, rsr__fbr)
                    continue
                sjar__pspsd[rsr__fbr] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[sdcza__hgc]))
            return sjar__pspsd
        return impl
    sxwcb__dtpst = dtype_to_array_type(yjl__ihid)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        sjar__pspsd = bodo.utils.utils.alloc_type(n, sxwcb__dtpst, (-1,))
        for rsr__fbr in numba.parfors.parfor.internal_prange(n):
            sdcza__hgc = codes[rsr__fbr]
            if sdcza__hgc == -1:
                bodo.libs.array_kernels.setna(sjar__pspsd, rsr__fbr)
                continue
            sjar__pspsd[rsr__fbr] = bodo.utils.conversion.unbox_if_timestamp(
                categories[sdcza__hgc])
        return sjar__pspsd
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        tmnsb__voi, ctoqh__swst = args
        xmnmp__ywlkh = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        xmnmp__ywlkh.codes = tmnsb__voi
        xmnmp__ywlkh.dtype = ctoqh__swst
        context.nrt.incref(builder, signature.args[0], tmnsb__voi)
        context.nrt.incref(builder, signature.args[1], ctoqh__swst)
        return xmnmp__ywlkh._getvalue()
    unjt__bijnh = CategoricalArrayType(cat_dtype)
    sig = unjt__bijnh(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    lly__khmrq = args[0]
    if equiv_set.has_shape(lly__khmrq):
        return ArrayAnalysis.AnalyzeResult(shape=lly__khmrq, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    zwt__swkrv = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, zwt__swkrv)
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
            qlzfe__pdz = {}
            pee__vey = np.empty(n + 1, np.int64)
            oppru__liru = {}
            yrwyu__smb = []
            zpulu__qrxcc = {}
            for rsr__fbr in range(n):
                zpulu__qrxcc[categories[rsr__fbr]] = rsr__fbr
            for fyxbm__bkq in to_replace:
                if fyxbm__bkq != value:
                    if fyxbm__bkq in zpulu__qrxcc:
                        if value in zpulu__qrxcc:
                            qlzfe__pdz[fyxbm__bkq] = fyxbm__bkq
                            hzns__tildz = zpulu__qrxcc[fyxbm__bkq]
                            oppru__liru[hzns__tildz] = zpulu__qrxcc[value]
                            yrwyu__smb.append(hzns__tildz)
                        else:
                            qlzfe__pdz[fyxbm__bkq] = value
                            zpulu__qrxcc[value] = zpulu__qrxcc[fyxbm__bkq]
            evah__uez = np.sort(np.array(yrwyu__smb))
            tndo__rqh = 0
            aisvr__cdil = []
            for liclz__amsps in range(-1, n):
                while tndo__rqh < len(evah__uez) and liclz__amsps > evah__uez[
                    tndo__rqh]:
                    tndo__rqh += 1
                aisvr__cdil.append(tndo__rqh)
            for dgoct__woap in range(-1, n):
                tfat__baa = dgoct__woap
                if dgoct__woap in oppru__liru:
                    tfat__baa = oppru__liru[dgoct__woap]
                pee__vey[dgoct__woap + 1] = tfat__baa - aisvr__cdil[
                    tfat__baa + 1]
            return qlzfe__pdz, pee__vey, len(evah__uez)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for rsr__fbr in range(len(new_codes_arr)):
        new_codes_arr[rsr__fbr] = codes_map_arr[old_codes_arr[rsr__fbr] + 1]


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
    lgk__qtsqk = arr.dtype.ordered
    dai__zzfq = arr.dtype.elem_type
    njbd__wognu = get_overload_const(to_replace)
    ymkwq__wvat = get_overload_const(value)
    if (arr.dtype.categories is not None and njbd__wognu is not
        NOT_CONSTANT and ymkwq__wvat is not NOT_CONSTANT):
        jac__qlgot, codes_map_arr, iojs__xxat = python_build_replace_dicts(
            njbd__wognu, ymkwq__wvat, arr.dtype.categories)
        if len(jac__qlgot) == 0:
            return lambda arr, to_replace, value: arr.copy()
        pmdxp__iutwe = []
        for nvq__cltl in arr.dtype.categories:
            if nvq__cltl in jac__qlgot:
                lxpe__zpday = jac__qlgot[nvq__cltl]
                if lxpe__zpday != nvq__cltl:
                    pmdxp__iutwe.append(lxpe__zpday)
            else:
                pmdxp__iutwe.append(nvq__cltl)
        dfoyg__cjn = pd.CategoricalDtype(pmdxp__iutwe, lgk__qtsqk
            ).categories.values
        qneo__awz = MetaType(tuple(dfoyg__cjn))

        def impl_dtype(arr, to_replace, value):
            eens__qnlt = init_cat_dtype(bodo.utils.conversion.
                index_from_array(dfoyg__cjn), lgk__qtsqk, None, qneo__awz)
            xmnmp__ywlkh = alloc_categorical_array(len(arr.codes), eens__qnlt)
            reassign_codes(xmnmp__ywlkh.codes, arr.codes, codes_map_arr)
            return xmnmp__ywlkh
        return impl_dtype
    dai__zzfq = arr.dtype.elem_type
    if dai__zzfq == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            qlzfe__pdz, codes_map_arr, ercj__jwirx = build_replace_dicts(
                to_replace, value, categories.values)
            if len(qlzfe__pdz) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), lgk__qtsqk,
                    None, None))
            n = len(categories)
            dfoyg__cjn = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                ercj__jwirx, -1)
            iaqr__dsz = 0
            for liclz__amsps in range(n):
                wgbmh__jxzg = categories[liclz__amsps]
                if wgbmh__jxzg in qlzfe__pdz:
                    iqoa__iuyvb = qlzfe__pdz[wgbmh__jxzg]
                    if iqoa__iuyvb != wgbmh__jxzg:
                        dfoyg__cjn[iaqr__dsz] = iqoa__iuyvb
                        iaqr__dsz += 1
                else:
                    dfoyg__cjn[iaqr__dsz] = wgbmh__jxzg
                    iaqr__dsz += 1
            xmnmp__ywlkh = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                dfoyg__cjn), lgk__qtsqk, None, None))
            reassign_codes(xmnmp__ywlkh.codes, arr.codes, codes_map_arr)
            return xmnmp__ywlkh
        return impl_str
    nvt__wfn = dtype_to_array_type(dai__zzfq)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        qlzfe__pdz, codes_map_arr, ercj__jwirx = build_replace_dicts(to_replace
            , value, categories.values)
        if len(qlzfe__pdz) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), lgk__qtsqk, None, None))
        n = len(categories)
        dfoyg__cjn = bodo.utils.utils.alloc_type(n - ercj__jwirx, nvt__wfn,
            None)
        iaqr__dsz = 0
        for rsr__fbr in range(n):
            wgbmh__jxzg = categories[rsr__fbr]
            if wgbmh__jxzg in qlzfe__pdz:
                iqoa__iuyvb = qlzfe__pdz[wgbmh__jxzg]
                if iqoa__iuyvb != wgbmh__jxzg:
                    dfoyg__cjn[iaqr__dsz] = iqoa__iuyvb
                    iaqr__dsz += 1
            else:
                dfoyg__cjn[iaqr__dsz] = wgbmh__jxzg
                iaqr__dsz += 1
        xmnmp__ywlkh = alloc_categorical_array(len(arr.codes),
            init_cat_dtype(bodo.utils.conversion.index_from_array(
            dfoyg__cjn), lgk__qtsqk, None, None))
        reassign_codes(xmnmp__ywlkh.codes, arr.codes, codes_map_arr)
        return xmnmp__ywlkh
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
    tbs__lcj = dict()
    ychgf__inyyh = 0
    for rsr__fbr in range(len(vals)):
        val = vals[rsr__fbr]
        if val in tbs__lcj:
            continue
        tbs__lcj[val] = ychgf__inyyh
        ychgf__inyyh += 1
    return tbs__lcj


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    tbs__lcj = dict()
    for rsr__fbr in range(len(vals)):
        val = vals[rsr__fbr]
        tbs__lcj[val] = rsr__fbr
    return tbs__lcj


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    idexc__gor = dict(fastpath=fastpath)
    dski__may = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', idexc__gor, dski__may)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        hce__wuvnd = get_overload_const(categories)
        if hce__wuvnd is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                ncy__qrwg = False
            else:
                ncy__qrwg = get_overload_const_bool(ordered)
            shov__zdiw = pd.CategoricalDtype(hce__wuvnd, ncy__qrwg
                ).categories.values
            xtbo__wjca = MetaType(tuple(shov__zdiw))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                eens__qnlt = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(shov__zdiw), ncy__qrwg, None, xtbo__wjca)
                return bodo.utils.conversion.fix_arr_dtype(data, eens__qnlt)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            clbk__adp = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                clbk__adp, ordered, None, None)
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
            mmtk__iyqsl = arr.codes[ind]
            return arr.dtype.categories[max(mmtk__iyqsl, 0)]
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
    for rsr__fbr in range(len(arr1)):
        if arr1[rsr__fbr] != arr2[rsr__fbr]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    oxjhl__cduzb = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    sihrg__wtb = not isinstance(val, CategoricalArrayType
        ) and is_iterable_type(val) and is_common_scalar_dtype([val.dtype,
        arr.dtype.elem_type]) and not (isinstance(arr.dtype.elem_type,
        types.Integer) and isinstance(val.dtype, types.Float))
    baby__qcbsu = categorical_arrs_match(arr, val)
    zkyvk__bhn = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    sgni__eby = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not oxjhl__cduzb:
            raise BodoError(zkyvk__bhn)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            mmtk__iyqsl = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = mmtk__iyqsl
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (oxjhl__cduzb or sihrg__wtb or baby__qcbsu !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(zkyvk__bhn)
        if baby__qcbsu == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(sgni__eby)
        if oxjhl__cduzb:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                hdxey__uxux = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for liclz__amsps in range(n):
                    arr.codes[ind[liclz__amsps]] = hdxey__uxux
            return impl_scalar
        if baby__qcbsu == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for rsr__fbr in range(n):
                    arr.codes[ind[rsr__fbr]] = val.codes[rsr__fbr]
            return impl_arr_ind_mask
        if baby__qcbsu == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(sgni__eby)
                n = len(val.codes)
                for rsr__fbr in range(n):
                    arr.codes[ind[rsr__fbr]] = val.codes[rsr__fbr]
            return impl_arr_ind_mask
        if sihrg__wtb:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for liclz__amsps in range(n):
                    cgoze__wgh = bodo.utils.conversion.unbox_if_timestamp(val
                        [liclz__amsps])
                    if cgoze__wgh not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    mmtk__iyqsl = categories.get_loc(cgoze__wgh)
                    arr.codes[ind[liclz__amsps]] = mmtk__iyqsl
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (oxjhl__cduzb or sihrg__wtb or baby__qcbsu !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(zkyvk__bhn)
        if baby__qcbsu == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(sgni__eby)
        if oxjhl__cduzb:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                hdxey__uxux = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for liclz__amsps in range(n):
                    if ind[liclz__amsps]:
                        arr.codes[liclz__amsps] = hdxey__uxux
            return impl_scalar
        if baby__qcbsu == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                tcnlv__bkqr = 0
                for rsr__fbr in range(n):
                    if ind[rsr__fbr]:
                        arr.codes[rsr__fbr] = val.codes[tcnlv__bkqr]
                        tcnlv__bkqr += 1
            return impl_bool_ind_mask
        if baby__qcbsu == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(sgni__eby)
                n = len(ind)
                tcnlv__bkqr = 0
                for rsr__fbr in range(n):
                    if ind[rsr__fbr]:
                        arr.codes[rsr__fbr] = val.codes[tcnlv__bkqr]
                        tcnlv__bkqr += 1
            return impl_bool_ind_mask
        if sihrg__wtb:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                tcnlv__bkqr = 0
                categories = arr.dtype.categories
                for liclz__amsps in range(n):
                    if ind[liclz__amsps]:
                        cgoze__wgh = bodo.utils.conversion.unbox_if_timestamp(
                            val[tcnlv__bkqr])
                        if cgoze__wgh not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        mmtk__iyqsl = categories.get_loc(cgoze__wgh)
                        arr.codes[liclz__amsps] = mmtk__iyqsl
                        tcnlv__bkqr += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (oxjhl__cduzb or sihrg__wtb or baby__qcbsu !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(zkyvk__bhn)
        if baby__qcbsu == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(sgni__eby)
        if oxjhl__cduzb:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                hdxey__uxux = arr.dtype.categories.get_loc(val)
                wnsu__uoxq = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                for liclz__amsps in range(wnsu__uoxq.start, wnsu__uoxq.stop,
                    wnsu__uoxq.step):
                    arr.codes[liclz__amsps] = hdxey__uxux
            return impl_scalar
        if baby__qcbsu == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if baby__qcbsu == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(sgni__eby)
                arr.codes[ind] = val.codes
            return impl_arr
        if sihrg__wtb:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                wnsu__uoxq = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                tcnlv__bkqr = 0
                for liclz__amsps in range(wnsu__uoxq.start, wnsu__uoxq.stop,
                    wnsu__uoxq.step):
                    cgoze__wgh = bodo.utils.conversion.unbox_if_timestamp(val
                        [tcnlv__bkqr])
                    if cgoze__wgh not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    mmtk__iyqsl = categories.get_loc(cgoze__wgh)
                    arr.codes[liclz__amsps] = mmtk__iyqsl
                    tcnlv__bkqr += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
