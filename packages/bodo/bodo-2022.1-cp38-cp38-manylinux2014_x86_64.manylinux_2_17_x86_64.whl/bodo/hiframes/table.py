"""Table data type for storing dataframe column arrays. Supports storing many columns
(e.g. >10k) efficiently.
"""
import operator
from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, register_model, typeof_impl, unbox
from numba.np.arrayobj import _getitem_array_single_int
from numba.parfors.array_analysis import ArrayAnalysis
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.typing import BodoError, get_overload_const_int, is_list_like_index_type, is_overload_constant_int


class Table:

    def __init__(self, arrs, usecols=None, num_arrs=-1):
        if usecols is not None:
            assert num_arrs != -1, 'num_arrs must be provided if usecols is not None'
            nfn__txtz = 0
            yqscx__fsi = []
            for i in range(usecols[-1] + 1):
                if i == usecols[nfn__txtz]:
                    yqscx__fsi.append(arrs[nfn__txtz])
                    nfn__txtz += 1
                else:
                    yqscx__fsi.append(None)
            for imopr__xsdv in range(usecols[-1] + 1, num_arrs):
                yqscx__fsi.append(None)
            self.arrays = yqscx__fsi
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and other.arrays == self.arrays

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        rtosq__gnw = len(self.arrays)
        bxs__otg = dict(zip(range(rtosq__gnw), self.arrays))
        phigu__fhyk = pd.DataFrame(bxs__otg, index)
        return phigu__fhyk


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        irgss__dye = []
        mmbw__snv = []
        jhpsr__narm = {}
        kiwd__rxcbq = defaultdict(int)
        tgz__pcepd = defaultdict(list)
        if not has_runtime_cols:
            for i, uxw__jxds in enumerate(arr_types):
                if uxw__jxds not in jhpsr__narm:
                    jhpsr__narm[uxw__jxds] = len(jhpsr__narm)
                kiwti__bjoq = jhpsr__narm[uxw__jxds]
                irgss__dye.append(kiwti__bjoq)
                mmbw__snv.append(kiwd__rxcbq[kiwti__bjoq])
                kiwd__rxcbq[kiwti__bjoq] += 1
                tgz__pcepd[kiwti__bjoq].append(i)
        self.block_nums = irgss__dye
        self.block_offsets = mmbw__snv
        self.type_to_blk = jhpsr__narm
        self.block_to_arr_ind = tgz__pcepd
        super(TableType, self).__init__(name=
            f'TableType({arr_types}, {has_runtime_cols})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return self.arr_types, self.has_runtime_cols

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(Table)
def typeof_table(val, c):
    return TableType(tuple(numba.typeof(avs__bxx) for avs__bxx in val.arrays))


@register_model(TableType)
class TableTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        if fe_type.has_runtime_cols:
            bmju__gassk = [(f'block_{i}', types.List(uxw__jxds)) for i,
                uxw__jxds in enumerate(fe_type.arr_types)]
        else:
            bmju__gassk = [(f'block_{kiwti__bjoq}', types.List(uxw__jxds)) for
                uxw__jxds, kiwti__bjoq in fe_type.type_to_blk.items()]
        bmju__gassk.append(('parent', types.pyobject))
        bmju__gassk.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, bmju__gassk)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@unbox(TableType)
def unbox_table(typ, val, c):
    tsj__ewf = c.pyapi.object_getattr_string(val, 'arrays')
    icf__ylxmp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    icf__ylxmp.parent = cgutils.get_null_value(icf__ylxmp.parent.type)
    edjmn__atph = c.pyapi.make_none()
    rjoxy__zuolr = c.context.get_constant(types.int64, 0)
    gknyz__gchza = cgutils.alloca_once_value(c.builder, rjoxy__zuolr)
    for uxw__jxds, kiwti__bjoq in typ.type_to_blk.items():
        xwss__cjssb = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[kiwti__bjoq]))
        imopr__xsdv, izk__cnz = ListInstance.allocate_ex(c.context, c.
            builder, types.List(uxw__jxds), xwss__cjssb)
        izk__cnz.size = xwss__cjssb
        fbmyb__zftms = c.context.make_constant_array(c.builder, types.Array
            (types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[
            kiwti__bjoq], dtype=np.int64))
        ffft__mgj = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, fbmyb__zftms)
        with cgutils.for_range(c.builder, xwss__cjssb) as loop:
            i = loop.index
            ybftp__rjeuj = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), ffft__mgj, i)
            fvvb__rmx = c.pyapi.long_from_longlong(ybftp__rjeuj)
            lim__mtqlz = c.pyapi.object_getitem(tsj__ewf, fvvb__rmx)
            cwn__aygoa = c.builder.icmp_unsigned('==', lim__mtqlz, edjmn__atph)
            with c.builder.if_else(cwn__aygoa) as (then, orelse):
                with then:
                    nkwsx__pkg = c.context.get_constant_null(uxw__jxds)
                    izk__cnz.inititem(i, nkwsx__pkg, incref=False)
                with orelse:
                    ysty__zvs = c.pyapi.call_method(lim__mtqlz, '__len__', ())
                    tfiq__zkxal = c.pyapi.long_as_longlong(ysty__zvs)
                    c.builder.store(tfiq__zkxal, gknyz__gchza)
                    c.pyapi.decref(ysty__zvs)
                    avs__bxx = c.pyapi.to_native_value(uxw__jxds, lim__mtqlz
                        ).value
                    izk__cnz.inititem(i, avs__bxx, incref=False)
            c.pyapi.decref(lim__mtqlz)
            c.pyapi.decref(fvvb__rmx)
        setattr(icf__ylxmp, f'block_{kiwti__bjoq}', izk__cnz.value)
    icf__ylxmp.len = c.builder.load(gknyz__gchza)
    c.pyapi.decref(tsj__ewf)
    c.pyapi.decref(edjmn__atph)
    mbdgf__fgmq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(icf__ylxmp._getvalue(), is_error=mbdgf__fgmq)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    icf__ylxmp = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        gblws__kxcfx = c.context.get_constant(types.int64, 0)
        for i, uxw__jxds in enumerate(typ.arr_types):
            yqscx__fsi = getattr(icf__ylxmp, f'block_{i}')
            lko__legsa = ListInstance(c.context, c.builder, types.List(
                uxw__jxds), yqscx__fsi)
            gblws__kxcfx = c.builder.add(gblws__kxcfx, lko__legsa.size)
        clnq__tur = c.pyapi.list_new(gblws__kxcfx)
        snt__ytj = c.context.get_constant(types.int64, 0)
        for i, uxw__jxds in enumerate(typ.arr_types):
            yqscx__fsi = getattr(icf__ylxmp, f'block_{i}')
            lko__legsa = ListInstance(c.context, c.builder, types.List(
                uxw__jxds), yqscx__fsi)
            with cgutils.for_range(c.builder, lko__legsa.size) as loop:
                i = loop.index
                avs__bxx = lko__legsa.getitem(i)
                c.context.nrt.incref(c.builder, uxw__jxds, avs__bxx)
                idx = c.builder.add(snt__ytj, i)
                c.pyapi.list_setitem(clnq__tur, idx, c.pyapi.
                    from_native_value(uxw__jxds, avs__bxx, c.env_manager))
            snt__ytj = c.builder.add(snt__ytj, lko__legsa.size)
        tbjiu__sbo = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        iccz__hwjul = c.pyapi.call_function_objargs(tbjiu__sbo, (clnq__tur,))
        c.pyapi.decref(tbjiu__sbo)
        c.pyapi.decref(clnq__tur)
        c.context.nrt.decref(c.builder, typ, val)
        return iccz__hwjul
    clnq__tur = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    quuw__vgsjj = cgutils.is_not_null(c.builder, icf__ylxmp.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for uxw__jxds, kiwti__bjoq in typ.type_to_blk.items():
        yqscx__fsi = getattr(icf__ylxmp, f'block_{kiwti__bjoq}')
        lko__legsa = ListInstance(c.context, c.builder, types.List(
            uxw__jxds), yqscx__fsi)
        fbmyb__zftms = c.context.make_constant_array(c.builder, types.Array
            (types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[
            kiwti__bjoq], dtype=np.int64))
        ffft__mgj = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, fbmyb__zftms)
        with cgutils.for_range(c.builder, lko__legsa.size) as loop:
            i = loop.index
            ybftp__rjeuj = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), ffft__mgj, i)
            avs__bxx = lko__legsa.getitem(i)
            ihu__tez = cgutils.alloca_once_value(c.builder, avs__bxx)
            obtzk__vthzb = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(uxw__jxds))
            cdpjg__ttcgr = is_ll_eq(c.builder, ihu__tez, obtzk__vthzb)
            with c.builder.if_else(c.builder.and_(cdpjg__ttcgr, c.builder.
                not_(ensure_unboxed))) as (then, orelse):
                with then:
                    edjmn__atph = c.pyapi.make_none()
                    c.pyapi.list_setitem(clnq__tur, ybftp__rjeuj, edjmn__atph)
                with orelse:
                    lim__mtqlz = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(cdpjg__ttcgr,
                        quuw__vgsjj)) as (arr_then, arr_orelse):
                        with arr_then:
                            lnxav__kir = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, icf__ylxmp.
                                parent, ybftp__rjeuj, uxw__jxds)
                            c.builder.store(lnxav__kir, lim__mtqlz)
                        with arr_orelse:
                            c.context.nrt.incref(c.builder, uxw__jxds, avs__bxx
                                )
                            c.builder.store(c.pyapi.from_native_value(
                                uxw__jxds, avs__bxx, c.env_manager), lim__mtqlz
                                )
                    c.pyapi.list_setitem(clnq__tur, ybftp__rjeuj, c.builder
                        .load(lim__mtqlz))
    tbjiu__sbo = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    iccz__hwjul = c.pyapi.call_function_objargs(tbjiu__sbo, (clnq__tur,))
    c.pyapi.decref(tbjiu__sbo)
    c.pyapi.decref(clnq__tur)
    c.context.nrt.decref(c.builder, typ, val)
    return iccz__hwjul


@overload(len)
def table_len_overload(T):
    if not isinstance(T, TableType):
        return

    def impl(T):
        return T._len
    return impl


@overload_attribute(TableType, 'shape')
def table_shape_overload(T):
    if T.has_runtime_cols:

        def impl(T):
            return T._len, compute_num_runtime_columns(T)
        return impl
    ncols = len(T.arr_types)
    return lambda T: (T._len, types.int64(ncols))


@intrinsic
def compute_num_runtime_columns(typingctx, table_type):
    assert isinstance(table_type, TableType)

    def codegen(context, builder, sig, args):
        table_arg, = args
        icf__ylxmp = cgutils.create_struct_proxy(table_type)(context,
            builder, table_arg)
        stq__dxox = context.get_constant(types.int64, 0)
        for i, uxw__jxds in enumerate(table_type.arr_types):
            yqscx__fsi = getattr(icf__ylxmp, f'block_{i}')
            lko__legsa = ListInstance(context, builder, types.List(
                uxw__jxds), yqscx__fsi)
            stq__dxox = builder.add(stq__dxox, lko__legsa.size)
        return stq__dxox
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    icf__ylxmp = cgutils.create_struct_proxy(table_type)(context, builder,
        table_arg)
    kiwti__bjoq = table_type.block_nums[col_ind]
    kdvfs__hmiro = table_type.block_offsets[col_ind]
    yqscx__fsi = getattr(icf__ylxmp, f'block_{kiwti__bjoq}')
    lko__legsa = ListInstance(context, builder, types.List(arr_type),
        yqscx__fsi)
    avs__bxx = lko__legsa.getitem(kdvfs__hmiro)
    return avs__bxx


@intrinsic
def get_table_data(typingctx, table_type, ind_typ=None):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, imopr__xsdv = args
        avs__bxx = get_table_data_codegen(context, builder, table_arg,
            col_ind, table_type)
        return impl_ret_borrowed(context, builder, arr_type, avs__bxx)
    sig = arr_type(table_type, ind_typ)
    return sig, codegen


@intrinsic
def del_column(typingctx, table_type, ind_typ=None):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, imopr__xsdv = args
        icf__ylxmp = cgutils.create_struct_proxy(table_type)(context,
            builder, table_arg)
        kiwti__bjoq = table_type.block_nums[col_ind]
        kdvfs__hmiro = table_type.block_offsets[col_ind]
        yqscx__fsi = getattr(icf__ylxmp, f'block_{kiwti__bjoq}')
        lko__legsa = ListInstance(context, builder, types.List(arr_type),
            yqscx__fsi)
        avs__bxx = lko__legsa.getitem(kdvfs__hmiro)
        context.nrt.decref(builder, arr_type, avs__bxx)
        nkwsx__pkg = context.get_constant_null(arr_type)
        lko__legsa.inititem(kdvfs__hmiro, nkwsx__pkg, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    rjoxy__zuolr = context.get_constant(types.int64, 0)
    swa__jqou = context.get_constant(types.int64, 1)
    lmj__vii = arr_type not in in_table_type.type_to_blk
    for uxw__jxds, kiwti__bjoq in out_table_type.type_to_blk.items():
        if uxw__jxds in in_table_type.type_to_blk:
            rnmk__wqoc = in_table_type.type_to_blk[uxw__jxds]
            izk__cnz = ListInstance(context, builder, types.List(uxw__jxds),
                getattr(in_table, f'block_{rnmk__wqoc}'))
            context.nrt.incref(builder, types.List(uxw__jxds), izk__cnz.value)
            setattr(out_table, f'block_{kiwti__bjoq}', izk__cnz.value)
    if lmj__vii:
        imopr__xsdv, izk__cnz = ListInstance.allocate_ex(context, builder,
            types.List(arr_type), swa__jqou)
        izk__cnz.size = swa__jqou
        izk__cnz.inititem(rjoxy__zuolr, arr_arg, incref=True)
        kiwti__bjoq = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{kiwti__bjoq}', izk__cnz.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        kiwti__bjoq = out_table_type.type_to_blk[arr_type]
        izk__cnz = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{kiwti__bjoq}'))
        if is_new_col:
            n = izk__cnz.size
            xpx__ruyos = builder.add(n, swa__jqou)
            izk__cnz.resize(xpx__ruyos)
            izk__cnz.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            fxhgp__khx = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            izk__cnz.setitem(fxhgp__khx, arr_arg, True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            fxhgp__khx = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = izk__cnz.size
            xpx__ruyos = builder.add(n, swa__jqou)
            izk__cnz.resize(xpx__ruyos)
            context.nrt.incref(builder, arr_type, izk__cnz.getitem(fxhgp__khx))
            izk__cnz.move(builder.add(fxhgp__khx, swa__jqou), fxhgp__khx,
                builder.sub(n, fxhgp__khx))
            izk__cnz.setitem(fxhgp__khx, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    tnbr__kjx = in_table_type.arr_types[col_ind]
    if tnbr__kjx in out_table_type.type_to_blk:
        kiwti__bjoq = out_table_type.type_to_blk[tnbr__kjx]
        von__wnk = getattr(out_table, f'block_{kiwti__bjoq}')
        tunpm__lkl = types.List(tnbr__kjx)
        fxhgp__khx = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        dew__ifi = tunpm__lkl.dtype(tunpm__lkl, types.intp)
        oxg__vsan = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), dew__ifi, (von__wnk, fxhgp__khx))
        context.nrt.decref(builder, tnbr__kjx, oxg__vsan)


@intrinsic
def set_table_data(typingctx, table_type, ind_type, arr_type=None):
    assert isinstance(table_type, TableType), 'invalid input to set_table_data'
    assert is_overload_constant_int(ind_type
        ), 'set_table_data expects const index'
    col_ind = get_overload_const_int(ind_type)
    is_new_col = col_ind == len(table_type.arr_types)
    qvo__xuuf = list(table_type.arr_types)
    if is_new_col:
        qvo__xuuf.append(arr_type)
    else:
        qvo__xuuf[col_ind] = arr_type
    out_table_type = TableType(tuple(qvo__xuuf))

    def codegen(context, builder, sig, args):
        table_arg, imopr__xsdv, gvvd__aqjka = args
        out_table = set_table_data_codegen(context, builder, table_type,
            table_arg, out_table_type, arr_type, gvvd__aqjka, col_ind,
            is_new_col)
        return out_table
    return out_table_type(table_type, ind_type, arr_type), codegen


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    tzh__ujytm = args[0]
    if equiv_set.has_shape(tzh__ujytm):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            tzh__ujytm)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    icf__ylxmp = cgutils.create_struct_proxy(table_type)(context, builder)
    icf__ylxmp.parent = cgutils.get_null_value(icf__ylxmp.parent.type)
    for uxw__jxds, kiwti__bjoq in table_type.type_to_blk.items():
        elzsf__hife = len(table_type.block_to_arr_ind[kiwti__bjoq])
        xwss__cjssb = context.get_constant(types.int64, elzsf__hife)
        imopr__xsdv, izk__cnz = ListInstance.allocate_ex(context, builder,
            types.List(uxw__jxds), xwss__cjssb)
        izk__cnz.size = xwss__cjssb
        for i in range(elzsf__hife):
            ybftp__rjeuj = table_type.block_to_arr_ind[kiwti__bjoq][i]
            avs__bxx = context.get_constant_generic(builder, table_type.
                arr_types[ybftp__rjeuj], pyval.arrays[ybftp__rjeuj])
            szr__brljf = context.get_constant(types.int64, i)
            izk__cnz.inititem(szr__brljf, avs__bxx, incref=False)
        setattr(icf__ylxmp, f'block_{kiwti__bjoq}', izk__cnz.value)
    return icf__ylxmp._getvalue()


@intrinsic
def init_table(typingctx, table_type=None):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        icf__ylxmp = cgutils.create_struct_proxy(table_type)(context, builder)
        for uxw__jxds, kiwti__bjoq in table_type.type_to_blk.items():
            gcl__fznx = context.get_constant_null(types.List(uxw__jxds))
            setattr(icf__ylxmp, f'block_{kiwti__bjoq}', gcl__fznx)
        return icf__ylxmp._getvalue()
    sig = table_type(table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type=None):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    kiwti__bjoq = get_overload_const_int(blk_type)
    arr_type = None
    for uxw__jxds, nhz__kzlxl in table_type.type_to_blk.items():
        if nhz__kzlxl == kiwti__bjoq:
            arr_type = uxw__jxds
            break
    assert arr_type is not None, 'invalid table type block'
    udmw__tbgzk = types.List(arr_type)

    def codegen(context, builder, sig, args):
        icf__ylxmp = cgutils.create_struct_proxy(table_type)(context,
            builder, args[0])
        yqscx__fsi = getattr(icf__ylxmp, f'block_{kiwti__bjoq}')
        return impl_ret_borrowed(context, builder, udmw__tbgzk, yqscx__fsi)
    sig = udmw__tbgzk(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_column_unboxed(typingctx, table_type, arr_list_t, ind_t,
    arr_ind_t=None):
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, arr_list_t, ind_t, arr_ind_t)
    return sig, ensure_column_unboxed_codegen


def ensure_column_unboxed_codegen(context, builder, sig, args):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table_arg, xuxz__iaoo, owh__ljrit, nuhvw__rumr = args
    xcll__gwe = context.get_python_api(builder)
    icf__ylxmp = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    quuw__vgsjj = cgutils.is_not_null(builder, icf__ylxmp.parent)
    lko__legsa = ListInstance(context, builder, sig.args[1], xuxz__iaoo)
    zch__ijko = lko__legsa.getitem(owh__ljrit)
    ihu__tez = cgutils.alloca_once_value(builder, zch__ijko)
    obtzk__vthzb = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    cdpjg__ttcgr = is_ll_eq(builder, ihu__tez, obtzk__vthzb)
    with builder.if_then(cdpjg__ttcgr):
        with builder.if_else(quuw__vgsjj) as (then, orelse):
            with then:
                lim__mtqlz = get_df_obj_column_codegen(context, builder,
                    xcll__gwe, icf__ylxmp.parent, nuhvw__rumr, sig.args[1].
                    dtype)
                avs__bxx = xcll__gwe.to_native_value(sig.args[1].dtype,
                    lim__mtqlz).value
                lko__legsa.inititem(owh__ljrit, avs__bxx, incref=False)
                xcll__gwe.decref(lim__mtqlz)
            with orelse:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type=None):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    kiwti__bjoq = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, woo__uxkve, imopr__xsdv = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{kiwti__bjoq}', woo__uxkve)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type=None):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, mtiuv__dys = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = mtiuv__dys
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type=None):
    assert isinstance(list_type, types.List), 'list type expected'

    def codegen(context, builder, sig, args):
        cty__gxm = ListInstance(context, builder, list_type, args[0])
        onjt__cslzl = cty__gxm.size
        imopr__xsdv, izk__cnz = ListInstance.allocate_ex(context, builder,
            list_type, onjt__cslzl)
        izk__cnz.size = onjt__cslzl
        return izk__cnz.value
    sig = list_type(list_type)
    return sig, codegen


def _get_idx_length(idx):
    pass


@overload(_get_idx_length)
def overload_get_idx_length(idx, n):
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        return lambda idx, n: idx.sum()
    assert isinstance(idx, types.SliceType), 'slice index expected'

    def impl(idx, n):
        tnam__nnkm = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(tnam__nnkm)
    return impl


def gen_table_filter(T, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    spi__jrm = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if used_cols is not None:
        spi__jrm['used_cols'] = np.array(used_cols, dtype=np.int64)
    pbz__mdf = 'def impl(T, idx):\n'
    pbz__mdf += f'  T2 = init_table(T)\n'
    pbz__mdf += f'  l = 0\n'
    if used_cols is not None and len(used_cols) == 0:
        pbz__mdf += f'  l = _get_idx_length(idx, len(T))\n'
        pbz__mdf += f'  T2 = set_table_len(T2, l)\n'
        pbz__mdf += f'  return T2\n'
        ehyy__iuwc = {}
        exec(pbz__mdf, spi__jrm, ehyy__iuwc)
        return ehyy__iuwc['impl']
    if used_cols is not None:
        pbz__mdf += f'  used_set = set(used_cols)\n'
    for kiwti__bjoq in T.type_to_blk.values():
        spi__jrm[f'arr_inds_{kiwti__bjoq}'] = np.array(T.block_to_arr_ind[
            kiwti__bjoq], dtype=np.int64)
        pbz__mdf += (
            f'  arr_list_{kiwti__bjoq} = get_table_block(T, {kiwti__bjoq})\n')
        pbz__mdf += (
            f'  out_arr_list_{kiwti__bjoq} = alloc_list_like(arr_list_{kiwti__bjoq})\n'
            )
        pbz__mdf += f'  for i in range(len(arr_list_{kiwti__bjoq})):\n'
        pbz__mdf += f'    arr_ind_{kiwti__bjoq} = arr_inds_{kiwti__bjoq}[i]\n'
        if used_cols is not None:
            pbz__mdf += (
                f'    if arr_ind_{kiwti__bjoq} not in used_set: continue\n')
        pbz__mdf += f"""    ensure_column_unboxed(T, arr_list_{kiwti__bjoq}, i, arr_ind_{kiwti__bjoq})
"""
        pbz__mdf += f"""    out_arr_{kiwti__bjoq} = ensure_contig_if_np(arr_list_{kiwti__bjoq}[i][idx])
"""
        pbz__mdf += f'    l = len(out_arr_{kiwti__bjoq})\n'
        pbz__mdf += (
            f'    out_arr_list_{kiwti__bjoq}[i] = out_arr_{kiwti__bjoq}\n')
        pbz__mdf += (
            f'  T2 = set_table_block(T2, out_arr_list_{kiwti__bjoq}, {kiwti__bjoq})\n'
            )
    pbz__mdf += f'  T2 = set_table_len(T2, l)\n'
    pbz__mdf += f'  return T2\n'
    ehyy__iuwc = {}
    exec(pbz__mdf, spi__jrm, ehyy__iuwc)
    return ehyy__iuwc['impl']


@overload(operator.getitem, no_unliteral=True)
def table_getitem(T, idx):
    if not isinstance(T, TableType):
        return
    return gen_table_filter(T)


@intrinsic
def init_runtime_table_from_lists(typingctx, arr_list_tup_typ, nrows_typ=None):
    assert isinstance(arr_list_tup_typ, types.BaseTuple
        ), 'init_runtime_table_from_lists requires a tuple of list of arrays'
    if isinstance(arr_list_tup_typ, types.UniTuple):
        if arr_list_tup_typ.dtype.dtype == types.undefined:
            return
        lav__rloau = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        lav__rloau = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            lav__rloau.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        axhz__cdvu, fqg__bolrv = args
        icf__ylxmp = cgutils.create_struct_proxy(table_type)(context, builder)
        icf__ylxmp.len = fqg__bolrv
        dcvdf__ilki = cgutils.unpack_tuple(builder, axhz__cdvu)
        for i, yqscx__fsi in enumerate(dcvdf__ilki):
            setattr(icf__ylxmp, f'block_{i}', yqscx__fsi)
            context.nrt.incref(builder, types.List(lav__rloau[i]), yqscx__fsi)
        return icf__ylxmp._getvalue()
    table_type = TableType(tuple(lav__rloau), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen
