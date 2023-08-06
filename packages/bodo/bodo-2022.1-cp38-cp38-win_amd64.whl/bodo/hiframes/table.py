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
            lhl__yfcw = 0
            byz__kqqf = []
            for i in range(usecols[-1] + 1):
                if i == usecols[lhl__yfcw]:
                    byz__kqqf.append(arrs[lhl__yfcw])
                    lhl__yfcw += 1
                else:
                    byz__kqqf.append(None)
            for dwtgo__tbljx in range(usecols[-1] + 1, num_arrs):
                byz__kqqf.append(None)
            self.arrays = byz__kqqf
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and other.arrays == self.arrays

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        vtwog__uurda = len(self.arrays)
        dios__uqh = dict(zip(range(vtwog__uurda), self.arrays))
        luhys__eoxeu = pd.DataFrame(dios__uqh, index)
        return luhys__eoxeu


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        ermad__hchsq = []
        tdio__lmyfd = []
        crlj__tboq = {}
        ddx__cpq = defaultdict(int)
        thqk__wmuvg = defaultdict(list)
        if not has_runtime_cols:
            for i, grycv__iup in enumerate(arr_types):
                if grycv__iup not in crlj__tboq:
                    crlj__tboq[grycv__iup] = len(crlj__tboq)
                plouc__qzs = crlj__tboq[grycv__iup]
                ermad__hchsq.append(plouc__qzs)
                tdio__lmyfd.append(ddx__cpq[plouc__qzs])
                ddx__cpq[plouc__qzs] += 1
                thqk__wmuvg[plouc__qzs].append(i)
        self.block_nums = ermad__hchsq
        self.block_offsets = tdio__lmyfd
        self.type_to_blk = crlj__tboq
        self.block_to_arr_ind = thqk__wmuvg
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
    return TableType(tuple(numba.typeof(badgm__milm) for badgm__milm in val
        .arrays))


@register_model(TableType)
class TableTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        if fe_type.has_runtime_cols:
            pwmb__nbahb = [(f'block_{i}', types.List(grycv__iup)) for i,
                grycv__iup in enumerate(fe_type.arr_types)]
        else:
            pwmb__nbahb = [(f'block_{plouc__qzs}', types.List(grycv__iup)) for
                grycv__iup, plouc__qzs in fe_type.type_to_blk.items()]
        pwmb__nbahb.append(('parent', types.pyobject))
        pwmb__nbahb.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, pwmb__nbahb)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@unbox(TableType)
def unbox_table(typ, val, c):
    jhdq__krrtt = c.pyapi.object_getattr_string(val, 'arrays')
    lyl__znqx = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    lyl__znqx.parent = cgutils.get_null_value(lyl__znqx.parent.type)
    zxoum__wmz = c.pyapi.make_none()
    vzcy__dqys = c.context.get_constant(types.int64, 0)
    mekl__dkz = cgutils.alloca_once_value(c.builder, vzcy__dqys)
    for grycv__iup, plouc__qzs in typ.type_to_blk.items():
        hvfzc__wkiv = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[plouc__qzs]))
        dwtgo__tbljx, adffn__ncd = ListInstance.allocate_ex(c.context, c.
            builder, types.List(grycv__iup), hvfzc__wkiv)
        adffn__ncd.size = hvfzc__wkiv
        zgl__zkyur = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[plouc__qzs],
            dtype=np.int64))
        itt__ricz = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, zgl__zkyur)
        with cgutils.for_range(c.builder, hvfzc__wkiv) as loop:
            i = loop.index
            nlq__cmxco = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), itt__ricz, i)
            tmugl__fexr = c.pyapi.long_from_longlong(nlq__cmxco)
            tocf__pop = c.pyapi.object_getitem(jhdq__krrtt, tmugl__fexr)
            dqlw__xaldk = c.builder.icmp_unsigned('==', tocf__pop, zxoum__wmz)
            with c.builder.if_else(dqlw__xaldk) as (then, orelse):
                with then:
                    bbf__fnf = c.context.get_constant_null(grycv__iup)
                    adffn__ncd.inititem(i, bbf__fnf, incref=False)
                with orelse:
                    agjuk__tul = c.pyapi.call_method(tocf__pop, '__len__', ())
                    zbmdw__mukn = c.pyapi.long_as_longlong(agjuk__tul)
                    c.builder.store(zbmdw__mukn, mekl__dkz)
                    c.pyapi.decref(agjuk__tul)
                    badgm__milm = c.pyapi.to_native_value(grycv__iup, tocf__pop
                        ).value
                    adffn__ncd.inititem(i, badgm__milm, incref=False)
            c.pyapi.decref(tocf__pop)
            c.pyapi.decref(tmugl__fexr)
        setattr(lyl__znqx, f'block_{plouc__qzs}', adffn__ncd.value)
    lyl__znqx.len = c.builder.load(mekl__dkz)
    c.pyapi.decref(jhdq__krrtt)
    c.pyapi.decref(zxoum__wmz)
    rwfj__qlphn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(lyl__znqx._getvalue(), is_error=rwfj__qlphn)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    lyl__znqx = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        sezxq__fwlqc = c.context.get_constant(types.int64, 0)
        for i, grycv__iup in enumerate(typ.arr_types):
            byz__kqqf = getattr(lyl__znqx, f'block_{i}')
            lurb__tjvi = ListInstance(c.context, c.builder, types.List(
                grycv__iup), byz__kqqf)
            sezxq__fwlqc = c.builder.add(sezxq__fwlqc, lurb__tjvi.size)
        gdha__gqe = c.pyapi.list_new(sezxq__fwlqc)
        bvk__mmfgu = c.context.get_constant(types.int64, 0)
        for i, grycv__iup in enumerate(typ.arr_types):
            byz__kqqf = getattr(lyl__znqx, f'block_{i}')
            lurb__tjvi = ListInstance(c.context, c.builder, types.List(
                grycv__iup), byz__kqqf)
            with cgutils.for_range(c.builder, lurb__tjvi.size) as loop:
                i = loop.index
                badgm__milm = lurb__tjvi.getitem(i)
                c.context.nrt.incref(c.builder, grycv__iup, badgm__milm)
                idx = c.builder.add(bvk__mmfgu, i)
                c.pyapi.list_setitem(gdha__gqe, idx, c.pyapi.
                    from_native_value(grycv__iup, badgm__milm, c.env_manager))
            bvk__mmfgu = c.builder.add(bvk__mmfgu, lurb__tjvi.size)
        jiv__spm = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        hio__nbv = c.pyapi.call_function_objargs(jiv__spm, (gdha__gqe,))
        c.pyapi.decref(jiv__spm)
        c.pyapi.decref(gdha__gqe)
        c.context.nrt.decref(c.builder, typ, val)
        return hio__nbv
    gdha__gqe = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    yifrq__wmxc = cgutils.is_not_null(c.builder, lyl__znqx.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for grycv__iup, plouc__qzs in typ.type_to_blk.items():
        byz__kqqf = getattr(lyl__znqx, f'block_{plouc__qzs}')
        lurb__tjvi = ListInstance(c.context, c.builder, types.List(
            grycv__iup), byz__kqqf)
        zgl__zkyur = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[plouc__qzs],
            dtype=np.int64))
        itt__ricz = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, zgl__zkyur)
        with cgutils.for_range(c.builder, lurb__tjvi.size) as loop:
            i = loop.index
            nlq__cmxco = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), itt__ricz, i)
            badgm__milm = lurb__tjvi.getitem(i)
            vqa__kqc = cgutils.alloca_once_value(c.builder, badgm__milm)
            wgpqg__yekde = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(grycv__iup))
            enzm__swqm = is_ll_eq(c.builder, vqa__kqc, wgpqg__yekde)
            with c.builder.if_else(c.builder.and_(enzm__swqm, c.builder.
                not_(ensure_unboxed))) as (then, orelse):
                with then:
                    zxoum__wmz = c.pyapi.make_none()
                    c.pyapi.list_setitem(gdha__gqe, nlq__cmxco, zxoum__wmz)
                with orelse:
                    tocf__pop = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(enzm__swqm,
                        yifrq__wmxc)) as (arr_then, arr_orelse):
                        with arr_then:
                            tkc__cnnzt = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, lyl__znqx.
                                parent, nlq__cmxco, grycv__iup)
                            c.builder.store(tkc__cnnzt, tocf__pop)
                        with arr_orelse:
                            c.context.nrt.incref(c.builder, grycv__iup,
                                badgm__milm)
                            c.builder.store(c.pyapi.from_native_value(
                                grycv__iup, badgm__milm, c.env_manager),
                                tocf__pop)
                    c.pyapi.list_setitem(gdha__gqe, nlq__cmxco, c.builder.
                        load(tocf__pop))
    jiv__spm = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    hio__nbv = c.pyapi.call_function_objargs(jiv__spm, (gdha__gqe,))
    c.pyapi.decref(jiv__spm)
    c.pyapi.decref(gdha__gqe)
    c.context.nrt.decref(c.builder, typ, val)
    return hio__nbv


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
        lyl__znqx = cgutils.create_struct_proxy(table_type)(context,
            builder, table_arg)
        lgrrh__xilk = context.get_constant(types.int64, 0)
        for i, grycv__iup in enumerate(table_type.arr_types):
            byz__kqqf = getattr(lyl__znqx, f'block_{i}')
            lurb__tjvi = ListInstance(context, builder, types.List(
                grycv__iup), byz__kqqf)
            lgrrh__xilk = builder.add(lgrrh__xilk, lurb__tjvi.size)
        return lgrrh__xilk
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    lyl__znqx = cgutils.create_struct_proxy(table_type)(context, builder,
        table_arg)
    plouc__qzs = table_type.block_nums[col_ind]
    ennqm__ukfw = table_type.block_offsets[col_ind]
    byz__kqqf = getattr(lyl__znqx, f'block_{plouc__qzs}')
    lurb__tjvi = ListInstance(context, builder, types.List(arr_type), byz__kqqf
        )
    badgm__milm = lurb__tjvi.getitem(ennqm__ukfw)
    return badgm__milm


@intrinsic
def get_table_data(typingctx, table_type, ind_typ=None):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, dwtgo__tbljx = args
        badgm__milm = get_table_data_codegen(context, builder, table_arg,
            col_ind, table_type)
        return impl_ret_borrowed(context, builder, arr_type, badgm__milm)
    sig = arr_type(table_type, ind_typ)
    return sig, codegen


@intrinsic
def del_column(typingctx, table_type, ind_typ=None):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, dwtgo__tbljx = args
        lyl__znqx = cgutils.create_struct_proxy(table_type)(context,
            builder, table_arg)
        plouc__qzs = table_type.block_nums[col_ind]
        ennqm__ukfw = table_type.block_offsets[col_ind]
        byz__kqqf = getattr(lyl__znqx, f'block_{plouc__qzs}')
        lurb__tjvi = ListInstance(context, builder, types.List(arr_type),
            byz__kqqf)
        badgm__milm = lurb__tjvi.getitem(ennqm__ukfw)
        context.nrt.decref(builder, arr_type, badgm__milm)
        bbf__fnf = context.get_constant_null(arr_type)
        lurb__tjvi.inititem(ennqm__ukfw, bbf__fnf, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    vzcy__dqys = context.get_constant(types.int64, 0)
    zkfa__lsr = context.get_constant(types.int64, 1)
    ppkh__zws = arr_type not in in_table_type.type_to_blk
    for grycv__iup, plouc__qzs in out_table_type.type_to_blk.items():
        if grycv__iup in in_table_type.type_to_blk:
            iyc__iishl = in_table_type.type_to_blk[grycv__iup]
            adffn__ncd = ListInstance(context, builder, types.List(
                grycv__iup), getattr(in_table, f'block_{iyc__iishl}'))
            context.nrt.incref(builder, types.List(grycv__iup), adffn__ncd.
                value)
            setattr(out_table, f'block_{plouc__qzs}', adffn__ncd.value)
    if ppkh__zws:
        dwtgo__tbljx, adffn__ncd = ListInstance.allocate_ex(context,
            builder, types.List(arr_type), zkfa__lsr)
        adffn__ncd.size = zkfa__lsr
        adffn__ncd.inititem(vzcy__dqys, arr_arg, incref=True)
        plouc__qzs = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{plouc__qzs}', adffn__ncd.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        plouc__qzs = out_table_type.type_to_blk[arr_type]
        adffn__ncd = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{plouc__qzs}'))
        if is_new_col:
            n = adffn__ncd.size
            jypo__msyw = builder.add(n, zkfa__lsr)
            adffn__ncd.resize(jypo__msyw)
            adffn__ncd.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            dfm__kbdfr = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            adffn__ncd.setitem(dfm__kbdfr, arr_arg, True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            dfm__kbdfr = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = adffn__ncd.size
            jypo__msyw = builder.add(n, zkfa__lsr)
            adffn__ncd.resize(jypo__msyw)
            context.nrt.incref(builder, arr_type, adffn__ncd.getitem(
                dfm__kbdfr))
            adffn__ncd.move(builder.add(dfm__kbdfr, zkfa__lsr), dfm__kbdfr,
                builder.sub(n, dfm__kbdfr))
            adffn__ncd.setitem(dfm__kbdfr, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    ixjqi__zugpx = in_table_type.arr_types[col_ind]
    if ixjqi__zugpx in out_table_type.type_to_blk:
        plouc__qzs = out_table_type.type_to_blk[ixjqi__zugpx]
        pnnbh__xuq = getattr(out_table, f'block_{plouc__qzs}')
        jlem__xww = types.List(ixjqi__zugpx)
        dfm__kbdfr = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        dskt__jvkco = jlem__xww.dtype(jlem__xww, types.intp)
        lib__qhjip = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), dskt__jvkco, (pnnbh__xuq, dfm__kbdfr))
        context.nrt.decref(builder, ixjqi__zugpx, lib__qhjip)


@intrinsic
def set_table_data(typingctx, table_type, ind_type, arr_type=None):
    assert isinstance(table_type, TableType), 'invalid input to set_table_data'
    assert is_overload_constant_int(ind_type
        ), 'set_table_data expects const index'
    col_ind = get_overload_const_int(ind_type)
    is_new_col = col_ind == len(table_type.arr_types)
    nmklp__jyzej = list(table_type.arr_types)
    if is_new_col:
        nmklp__jyzej.append(arr_type)
    else:
        nmklp__jyzej[col_ind] = arr_type
    out_table_type = TableType(tuple(nmklp__jyzej))

    def codegen(context, builder, sig, args):
        table_arg, dwtgo__tbljx, rfpm__dwfz = args
        out_table = set_table_data_codegen(context, builder, table_type,
            table_arg, out_table_type, arr_type, rfpm__dwfz, col_ind,
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
    urwt__zulqn = args[0]
    if equiv_set.has_shape(urwt__zulqn):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            urwt__zulqn)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    lyl__znqx = cgutils.create_struct_proxy(table_type)(context, builder)
    lyl__znqx.parent = cgutils.get_null_value(lyl__znqx.parent.type)
    for grycv__iup, plouc__qzs in table_type.type_to_blk.items():
        uvik__ogg = len(table_type.block_to_arr_ind[plouc__qzs])
        hvfzc__wkiv = context.get_constant(types.int64, uvik__ogg)
        dwtgo__tbljx, adffn__ncd = ListInstance.allocate_ex(context,
            builder, types.List(grycv__iup), hvfzc__wkiv)
        adffn__ncd.size = hvfzc__wkiv
        for i in range(uvik__ogg):
            nlq__cmxco = table_type.block_to_arr_ind[plouc__qzs][i]
            badgm__milm = context.get_constant_generic(builder, table_type.
                arr_types[nlq__cmxco], pyval.arrays[nlq__cmxco])
            divbt__xvvo = context.get_constant(types.int64, i)
            adffn__ncd.inititem(divbt__xvvo, badgm__milm, incref=False)
        setattr(lyl__znqx, f'block_{plouc__qzs}', adffn__ncd.value)
    return lyl__znqx._getvalue()


@intrinsic
def init_table(typingctx, table_type=None):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        lyl__znqx = cgutils.create_struct_proxy(table_type)(context, builder)
        for grycv__iup, plouc__qzs in table_type.type_to_blk.items():
            kgbkz__buk = context.get_constant_null(types.List(grycv__iup))
            setattr(lyl__znqx, f'block_{plouc__qzs}', kgbkz__buk)
        return lyl__znqx._getvalue()
    sig = table_type(table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type=None):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    plouc__qzs = get_overload_const_int(blk_type)
    arr_type = None
    for grycv__iup, awio__dbhid in table_type.type_to_blk.items():
        if awio__dbhid == plouc__qzs:
            arr_type = grycv__iup
            break
    assert arr_type is not None, 'invalid table type block'
    cahdy__dmv = types.List(arr_type)

    def codegen(context, builder, sig, args):
        lyl__znqx = cgutils.create_struct_proxy(table_type)(context,
            builder, args[0])
        byz__kqqf = getattr(lyl__znqx, f'block_{plouc__qzs}')
        return impl_ret_borrowed(context, builder, cahdy__dmv, byz__kqqf)
    sig = cahdy__dmv(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_column_unboxed(typingctx, table_type, arr_list_t, ind_t,
    arr_ind_t=None):
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, arr_list_t, ind_t, arr_ind_t)
    return sig, ensure_column_unboxed_codegen


def ensure_column_unboxed_codegen(context, builder, sig, args):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table_arg, nymzd__ezkq, hzmx__qomfi, ttycq__hpzap = args
    onh__vpg = context.get_python_api(builder)
    lyl__znqx = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    yifrq__wmxc = cgutils.is_not_null(builder, lyl__znqx.parent)
    lurb__tjvi = ListInstance(context, builder, sig.args[1], nymzd__ezkq)
    cccz__irt = lurb__tjvi.getitem(hzmx__qomfi)
    vqa__kqc = cgutils.alloca_once_value(builder, cccz__irt)
    wgpqg__yekde = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    enzm__swqm = is_ll_eq(builder, vqa__kqc, wgpqg__yekde)
    with builder.if_then(enzm__swqm):
        with builder.if_else(yifrq__wmxc) as (then, orelse):
            with then:
                tocf__pop = get_df_obj_column_codegen(context, builder,
                    onh__vpg, lyl__znqx.parent, ttycq__hpzap, sig.args[1].dtype
                    )
                badgm__milm = onh__vpg.to_native_value(sig.args[1].dtype,
                    tocf__pop).value
                lurb__tjvi.inititem(hzmx__qomfi, badgm__milm, incref=False)
                onh__vpg.decref(tocf__pop)
            with orelse:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type=None):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    plouc__qzs = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, sicyt__ehmyc, dwtgo__tbljx = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{plouc__qzs}', sicyt__ehmyc)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type=None):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, ktknv__gvnjv = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = ktknv__gvnjv
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type=None):
    assert isinstance(list_type, types.List), 'list type expected'

    def codegen(context, builder, sig, args):
        lqlul__fww = ListInstance(context, builder, list_type, args[0])
        ewyjo__zxcg = lqlul__fww.size
        dwtgo__tbljx, adffn__ncd = ListInstance.allocate_ex(context,
            builder, list_type, ewyjo__zxcg)
        adffn__ncd.size = ewyjo__zxcg
        return adffn__ncd.value
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
        olfd__wrj = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(olfd__wrj)
    return impl


def gen_table_filter(T, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    eyxq__sqx = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if used_cols is not None:
        eyxq__sqx['used_cols'] = np.array(used_cols, dtype=np.int64)
    nsutc__sft = 'def impl(T, idx):\n'
    nsutc__sft += f'  T2 = init_table(T)\n'
    nsutc__sft += f'  l = 0\n'
    if used_cols is not None and len(used_cols) == 0:
        nsutc__sft += f'  l = _get_idx_length(idx, len(T))\n'
        nsutc__sft += f'  T2 = set_table_len(T2, l)\n'
        nsutc__sft += f'  return T2\n'
        haok__syycx = {}
        exec(nsutc__sft, eyxq__sqx, haok__syycx)
        return haok__syycx['impl']
    if used_cols is not None:
        nsutc__sft += f'  used_set = set(used_cols)\n'
    for plouc__qzs in T.type_to_blk.values():
        eyxq__sqx[f'arr_inds_{plouc__qzs}'] = np.array(T.block_to_arr_ind[
            plouc__qzs], dtype=np.int64)
        nsutc__sft += (
            f'  arr_list_{plouc__qzs} = get_table_block(T, {plouc__qzs})\n')
        nsutc__sft += (
            f'  out_arr_list_{plouc__qzs} = alloc_list_like(arr_list_{plouc__qzs})\n'
            )
        nsutc__sft += f'  for i in range(len(arr_list_{plouc__qzs})):\n'
        nsutc__sft += f'    arr_ind_{plouc__qzs} = arr_inds_{plouc__qzs}[i]\n'
        if used_cols is not None:
            nsutc__sft += (
                f'    if arr_ind_{plouc__qzs} not in used_set: continue\n')
        nsutc__sft += f"""    ensure_column_unboxed(T, arr_list_{plouc__qzs}, i, arr_ind_{plouc__qzs})
"""
        nsutc__sft += f"""    out_arr_{plouc__qzs} = ensure_contig_if_np(arr_list_{plouc__qzs}[i][idx])
"""
        nsutc__sft += f'    l = len(out_arr_{plouc__qzs})\n'
        nsutc__sft += (
            f'    out_arr_list_{plouc__qzs}[i] = out_arr_{plouc__qzs}\n')
        nsutc__sft += (
            f'  T2 = set_table_block(T2, out_arr_list_{plouc__qzs}, {plouc__qzs})\n'
            )
    nsutc__sft += f'  T2 = set_table_len(T2, l)\n'
    nsutc__sft += f'  return T2\n'
    haok__syycx = {}
    exec(nsutc__sft, eyxq__sqx, haok__syycx)
    return haok__syycx['impl']


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
        msfh__nkhdn = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        msfh__nkhdn = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            msfh__nkhdn.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        nvzxg__cxn, dbrr__gaj = args
        lyl__znqx = cgutils.create_struct_proxy(table_type)(context, builder)
        lyl__znqx.len = dbrr__gaj
        bcg__metdu = cgutils.unpack_tuple(builder, nvzxg__cxn)
        for i, byz__kqqf in enumerate(bcg__metdu):
            setattr(lyl__znqx, f'block_{i}', byz__kqqf)
            context.nrt.incref(builder, types.List(msfh__nkhdn[i]), byz__kqqf)
        return lyl__znqx._getvalue()
    table_type = TableType(tuple(msfh__nkhdn), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen
