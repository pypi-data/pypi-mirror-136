"""
Indexing support for pd.DataFrame type.
"""
import operator
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.utils.transform import gen_const_tup
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_list, get_overload_const_str, is_immutable_array, is_list_like_index_type, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, raise_bodo_error


@infer_global(operator.getitem)
class DataFrameGetItemTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        check_runtime_cols_unsupported(args[0], 'DataFrame getitem (df[])')
        if isinstance(args[0], DataFrameType):
            return self.typecheck_df_getitem(args)
        elif isinstance(args[0], DataFrameLocType):
            return self.typecheck_loc_getitem(args)
        else:
            return

    def typecheck_loc_getitem(self, args):
        I = args[0]
        idx = args[1]
        df = I.df_type
        if isinstance(df.columns[0], tuple):
            raise_bodo_error(
                'DataFrame.loc[] getitem (location-based indexing) with multi-indexed columns not supported yet'
                )
        if is_list_like_index_type(idx) and idx.dtype == types.bool_:
            uqa__aho = idx
            vlafq__blofd = df.data
            jdhbc__fbymv = df.columns
            ejlnf__sst = self.replace_range_with_numeric_idx_if_needed(df,
                uqa__aho)
            glir__rrg = DataFrameType(vlafq__blofd, ejlnf__sst, jdhbc__fbymv)
            return glir__rrg(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            logb__fuwy = idx.types[0]
            wel__ajsup = idx.types[1]
            if isinstance(logb__fuwy, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(wel__ajsup):
                    ttlti__eaa = get_overload_const_str(wel__ajsup)
                    if ttlti__eaa not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, ttlti__eaa))
                    bdoyo__rish = df.columns.index(ttlti__eaa)
                    return df.data[bdoyo__rish].dtype(*args)
                if isinstance(wel__ajsup, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(logb__fuwy
                ) and logb__fuwy.dtype == types.bool_ or isinstance(logb__fuwy,
                types.SliceType):
                ejlnf__sst = self.replace_range_with_numeric_idx_if_needed(df,
                    logb__fuwy)
                if is_overload_constant_str(wel__ajsup):
                    jyi__nbfi = get_overload_const_str(wel__ajsup)
                    if jyi__nbfi not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {jyi__nbfi}'
                            )
                    bdoyo__rish = df.columns.index(jyi__nbfi)
                    liq__zzlar = df.data[bdoyo__rish]
                    ysstj__mqef = liq__zzlar.dtype
                    ebzeu__jgn = types.literal(df.columns[bdoyo__rish])
                    glir__rrg = bodo.SeriesType(ysstj__mqef, liq__zzlar,
                        ejlnf__sst, ebzeu__jgn)
                    return glir__rrg(*args)
                if isinstance(wel__ajsup, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
                        )
                elif is_overload_constant_list(wel__ajsup):
                    rbv__kpnje = get_overload_const_list(wel__ajsup)
                    kheow__lfts = types.unliteral(wel__ajsup)
                    if kheow__lfts.dtype == types.bool_:
                        if len(df.columns) != len(rbv__kpnje):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {rbv__kpnje} has {len(rbv__kpnje)} values'
                                )
                        vkd__nbhe = []
                        mhydy__ichzo = []
                        for gnx__wpn in range(len(rbv__kpnje)):
                            if rbv__kpnje[gnx__wpn]:
                                vkd__nbhe.append(df.columns[gnx__wpn])
                                mhydy__ichzo.append(df.data[gnx__wpn])
                        cgeu__mys = tuple()
                        glir__rrg = DataFrameType(tuple(mhydy__ichzo),
                            ejlnf__sst, tuple(vkd__nbhe))
                        return glir__rrg(*args)
                    elif kheow__lfts.dtype == bodo.string_type:
                        cgeu__mys, mhydy__ichzo = self.get_kept_cols_and_data(
                            df, rbv__kpnje)
                        glir__rrg = DataFrameType(mhydy__ichzo, ejlnf__sst,
                            cgeu__mys)
                        return glir__rrg(*args)
        raise_bodo_error(
            f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet. If you are trying to select a subset of the columns by passing a list of column names, that list must be a compile time constant. See https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
            )

    def typecheck_df_getitem(self, args):
        df = args[0]
        ind = args[1]
        if is_overload_constant_str(ind) or is_overload_constant_int(ind):
            ind_val = get_overload_const_str(ind) if is_overload_constant_str(
                ind) else get_overload_const_int(ind)
            if isinstance(df.columns[0], tuple):
                vkd__nbhe = []
                mhydy__ichzo = []
                for gnx__wpn, mlcpq__lvfvr in enumerate(df.columns):
                    if mlcpq__lvfvr[0] != ind_val:
                        continue
                    vkd__nbhe.append(mlcpq__lvfvr[1] if len(mlcpq__lvfvr) ==
                        2 else mlcpq__lvfvr[1:])
                    mhydy__ichzo.append(df.data[gnx__wpn])
                liq__zzlar = tuple(mhydy__ichzo)
                joctz__fboix = df.index
                isx__sadut = tuple(vkd__nbhe)
                glir__rrg = DataFrameType(liq__zzlar, joctz__fboix, isx__sadut)
                return glir__rrg(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                bdoyo__rish = df.columns.index(ind_val)
                liq__zzlar = df.data[bdoyo__rish]
                ysstj__mqef = liq__zzlar.dtype
                joctz__fboix = df.index
                ebzeu__jgn = types.literal(df.columns[bdoyo__rish])
                glir__rrg = bodo.SeriesType(ysstj__mqef, liq__zzlar,
                    joctz__fboix, ebzeu__jgn)
                return glir__rrg(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            liq__zzlar = df.data
            joctz__fboix = self.replace_range_with_numeric_idx_if_needed(df,
                ind)
            isx__sadut = df.columns
            glir__rrg = DataFrameType(liq__zzlar, joctz__fboix, isx__sadut,
                is_table_format=df.is_table_format)
            return glir__rrg(*args)
        elif is_overload_constant_list(ind):
            cqp__sroc = get_overload_const_list(ind)
            isx__sadut, liq__zzlar = self.get_kept_cols_and_data(df, cqp__sroc)
            joctz__fboix = df.index
            glir__rrg = DataFrameType(liq__zzlar, joctz__fboix, isx__sadut)
            return glir__rrg(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html'
            )

    def get_kept_cols_and_data(self, df, cols_to_keep_list):
        for euyz__cwut in cols_to_keep_list:
            if euyz__cwut not in df.columns:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(euyz__cwut, df.columns))
        isx__sadut = tuple(cols_to_keep_list)
        liq__zzlar = tuple(df.data[df.columns.index(igm__driv)] for
            igm__driv in isx__sadut)
        return isx__sadut, liq__zzlar

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        ejlnf__sst = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return ejlnf__sst


DataFrameGetItemTemplate._no_unliteral = True


@lower_builtin(operator.getitem, DataFrameType, types.Any)
def getitem_df_lower(context, builder, sig, args):
    impl = df_getitem_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def df_getitem_overload(df, ind):
    if not isinstance(df, DataFrameType):
        return
    if is_overload_constant_str(ind) or is_overload_constant_int(ind):
        ind_val = get_overload_const_str(ind) if is_overload_constant_str(ind
            ) else get_overload_const_int(ind)
        if isinstance(df.columns[0], tuple):
            vkd__nbhe = []
            mhydy__ichzo = []
            for gnx__wpn, mlcpq__lvfvr in enumerate(df.columns):
                if mlcpq__lvfvr[0] != ind_val:
                    continue
                vkd__nbhe.append(mlcpq__lvfvr[1] if len(mlcpq__lvfvr) == 2 else
                    mlcpq__lvfvr[1:])
                mhydy__ichzo.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(gnx__wpn))
            mua__zmlke = 'def impl(df, ind):\n'
            dxyq__flf = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(mua__zmlke,
                vkd__nbhe, ', '.join(mhydy__ichzo), dxyq__flf)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        cqp__sroc = get_overload_const_list(ind)
        for euyz__cwut in cqp__sroc:
            if euyz__cwut not in df.columns:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(euyz__cwut, df.columns))
        mhydy__ichzo = ', '.join(
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}).copy()'
            .format(df.columns.index(euyz__cwut)) for euyz__cwut in cqp__sroc)
        mua__zmlke = 'def impl(df, ind):\n'
        dxyq__flf = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(mua__zmlke,
            cqp__sroc, mhydy__ichzo, dxyq__flf)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        mua__zmlke = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            mua__zmlke += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        dxyq__flf = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            mhydy__ichzo = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            mhydy__ichzo = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(euyz__cwut)})[ind]'
                 for euyz__cwut in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(mua__zmlke, df.
            columns, mhydy__ichzo, dxyq__flf, out_df_type=df)
    raise_bodo_error('df[] getitem using {} not supported'.format(ind))


@overload(operator.setitem, no_unliteral=True)
def df_setitem_overload(df, idx, val):
    check_runtime_cols_unsupported(df, 'DataFrame setitem (df[])')
    if not isinstance(df, DataFrameType):
        return
    raise_bodo_error('DataFrame setitem: transform necessary')


class DataFrameILocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        igm__driv = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(igm__driv)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tdzuv__suau = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, tdzuv__suau)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        wrd__uhp, = args
        vru__hxh = signature.return_type
        qrb__bpfsq = cgutils.create_struct_proxy(vru__hxh)(context, builder)
        qrb__bpfsq.obj = wrd__uhp
        context.nrt.incref(builder, signature.args[0], wrd__uhp)
        return qrb__bpfsq._getvalue()
    return DataFrameILocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iloc')
def overload_dataframe_iloc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iloc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iloc(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iloc_getitem(I, idx):
    if not isinstance(I, DataFrameILocType):
        return
    df = I.df_type
    if isinstance(idx, types.Integer):
        return _gen_iloc_getitem_row_impl(df, df.columns, 'idx')
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and not isinstance(
        idx[1], types.SliceType):
        if not (is_overload_constant_list(idx.types[1]) or
            is_overload_constant_int(idx.types[1])):
            raise_bodo_error(
                'idx2 in df.iloc[idx1, idx2] should be a constant integer or constant list of integers. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
                )
        amjv__bso = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            nitd__ivc = get_overload_const_int(idx.types[1])
            if nitd__ivc < 0 or nitd__ivc >= amjv__bso:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            yrigj__tmebt = [nitd__ivc]
        else:
            is_out_series = False
            yrigj__tmebt = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= amjv__bso for
                ind in yrigj__tmebt):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[yrigj__tmebt])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                nitd__ivc = yrigj__tmebt[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, nitd__ivc)[
                        idx[0]])
                return impl
            return _gen_iloc_getitem_row_impl(df, col_names, 'idx[0]')
        if is_list_like_index_type(idx.types[0]) and isinstance(idx.types[0
            ].dtype, (types.Integer, types.Boolean)) or isinstance(idx.
            types[0], types.SliceType):
            return _gen_iloc_getitem_bool_slice_impl(df, col_names, idx.
                types[0], 'idx[0]', is_out_series)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, (types.
        Integer, types.Boolean)) or isinstance(idx, types.SliceType):
        return _gen_iloc_getitem_bool_slice_impl(df, df.columns, idx, 'idx',
            False)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):
        raise_bodo_error(
            'slice2 in df.iloc[slice1,slice2] should be constant. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
            )
    raise_bodo_error(f'df.iloc[] getitem using {idx} not supported')


def _gen_iloc_getitem_bool_slice_impl(df, col_names, idx_typ, idx,
    is_out_series):
    mua__zmlke = 'def impl(I, idx):\n'
    mua__zmlke += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        mua__zmlke += f'  idx_t = {idx}\n'
    else:
        mua__zmlke += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    dxyq__flf = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]'
    mhydy__ichzo = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(euyz__cwut)})[idx_t]'
         for euyz__cwut in col_names)
    if is_out_series:
        ciiam__xbkf = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        mua__zmlke += f"""  return bodo.hiframes.pd_series_ext.init_series({mhydy__ichzo}, {dxyq__flf}, {ciiam__xbkf})
"""
        ths__ehpar = {}
        exec(mua__zmlke, {'bodo': bodo}, ths__ehpar)
        return ths__ehpar['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(mua__zmlke, col_names,
        mhydy__ichzo, dxyq__flf)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    mua__zmlke = 'def impl(I, idx):\n'
    mua__zmlke += '  df = I._obj\n'
    zwp__npu = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(euyz__cwut)})[{idx}]'
         for euyz__cwut in col_names)
    mua__zmlke += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    mua__zmlke += f"""  return bodo.hiframes.pd_series_ext.init_series(({zwp__npu},), row_idx, None)
"""
    ths__ehpar = {}
    exec(mua__zmlke, {'bodo': bodo}, ths__ehpar)
    impl = ths__ehpar['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def df_iloc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameILocType):
        return
    raise_bodo_error(
        f'DataFrame.iloc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameLocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        igm__driv = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(igm__driv)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tdzuv__suau = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, tdzuv__suau)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        wrd__uhp, = args
        tgc__jsb = signature.return_type
        ktka__gllu = cgutils.create_struct_proxy(tgc__jsb)(context, builder)
        ktka__gllu.obj = wrd__uhp
        context.nrt.incref(builder, signature.args[0], wrd__uhp)
        return ktka__gllu._getvalue()
    return DataFrameLocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'loc')
def overload_dataframe_loc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.loc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_loc(df)


@lower_builtin(operator.getitem, DataFrameLocType, types.Any)
def loc_getitem_lower(context, builder, sig, args):
    impl = overload_loc_getitem(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def overload_loc_getitem(I, idx):
    if not isinstance(I, DataFrameLocType):
        return
    df = I.df_type
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        mua__zmlke = 'def impl(I, idx):\n'
        mua__zmlke += '  df = I._obj\n'
        mua__zmlke += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        dxyq__flf = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        mhydy__ichzo = ', '.join(
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[idx_t]'
            .format(df.columns.index(euyz__cwut)) for euyz__cwut in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(mua__zmlke, df.
            columns, mhydy__ichzo, dxyq__flf)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        sckb__wfrqu = idx.types[1]
        if is_overload_constant_str(sckb__wfrqu):
            cmp__hkl = get_overload_const_str(sckb__wfrqu)
            nitd__ivc = df.columns.index(cmp__hkl)

            def impl_col_name(I, idx):
                df = I._obj
                dxyq__flf = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
                    df)
                mnc__uhlzq = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
                    df, nitd__ivc)
                return bodo.hiframes.pd_series_ext.init_series(mnc__uhlzq,
                    dxyq__flf, cmp__hkl).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(sckb__wfrqu):
            col_idx_list = get_overload_const_list(sckb__wfrqu)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(euyz__cwut in df.columns for
                euyz__cwut in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        col_idx_list = list(pd.Series(df.columns, dtype=object)[col_idx_list])
    mhydy__ichzo = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[idx[0]]'
        .format(df.columns.index(euyz__cwut)) for euyz__cwut in col_idx_list)
    dxyq__flf = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    mua__zmlke = 'def impl(I, idx):\n'
    mua__zmlke += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(mua__zmlke,
        col_idx_list, mhydy__ichzo, dxyq__flf)


@overload(operator.setitem, no_unliteral=True)
def df_loc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameLocType):
        return
    raise_bodo_error(
        f'DataFrame.loc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameIatType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        igm__driv = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(igm__driv)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tdzuv__suau = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, tdzuv__suau)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        wrd__uhp, = args
        itv__qaevl = signature.return_type
        osjj__urr = cgutils.create_struct_proxy(itv__qaevl)(context, builder)
        osjj__urr.obj = wrd__uhp
        context.nrt.incref(builder, signature.args[0], wrd__uhp)
        return osjj__urr._getvalue()
    return DataFrameIatType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iat')
def overload_dataframe_iat(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iat')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iat(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iat_getitem(I, idx):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat getitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
                )
        nitd__ivc = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            mnc__uhlzq = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                nitd__ivc)
            return mnc__uhlzq[idx[0]]
        return impl_col_ind
    raise BodoError('df.iat[] getitem using {} not supported'.format(idx))


@overload(operator.setitem, no_unliteral=True)
def overload_iat_setitem(I, idx, val):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat setitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html'
                )
        nitd__ivc = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[nitd__ivc]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            mnc__uhlzq = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                nitd__ivc)
            mnc__uhlzq[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    osjj__urr = cgutils.create_struct_proxy(fromty)(context, builder, val)
    oid__jgknp = context.cast(builder, osjj__urr.obj, fromty.df_type, toty.
        df_type)
    epzwr__rpgxy = cgutils.create_struct_proxy(toty)(context, builder)
    epzwr__rpgxy.obj = oid__jgknp
    return epzwr__rpgxy._getvalue()
