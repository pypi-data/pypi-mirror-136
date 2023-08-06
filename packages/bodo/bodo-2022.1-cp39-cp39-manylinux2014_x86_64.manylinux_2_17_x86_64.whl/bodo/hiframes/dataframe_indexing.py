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
            dflk__vdxq = idx
            sgkmq__msni = df.data
            wywb__uvnuy = df.columns
            pitt__nktc = self.replace_range_with_numeric_idx_if_needed(df,
                dflk__vdxq)
            xura__hwlnx = DataFrameType(sgkmq__msni, pitt__nktc, wywb__uvnuy)
            return xura__hwlnx(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            mrt__vndo = idx.types[0]
            mez__euqyx = idx.types[1]
            if isinstance(mrt__vndo, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(mez__euqyx):
                    twjv__ysle = get_overload_const_str(mez__euqyx)
                    if twjv__ysle not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, twjv__ysle))
                    pvzjt__tbiea = df.columns.index(twjv__ysle)
                    return df.data[pvzjt__tbiea].dtype(*args)
                if isinstance(mez__euqyx, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(mrt__vndo
                ) and mrt__vndo.dtype == types.bool_ or isinstance(mrt__vndo,
                types.SliceType):
                pitt__nktc = self.replace_range_with_numeric_idx_if_needed(df,
                    mrt__vndo)
                if is_overload_constant_str(mez__euqyx):
                    jbu__otvde = get_overload_const_str(mez__euqyx)
                    if jbu__otvde not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {jbu__otvde}'
                            )
                    pvzjt__tbiea = df.columns.index(jbu__otvde)
                    mhint__wcqoi = df.data[pvzjt__tbiea]
                    covgg__zjhzh = mhint__wcqoi.dtype
                    wjr__ggvz = types.literal(df.columns[pvzjt__tbiea])
                    xura__hwlnx = bodo.SeriesType(covgg__zjhzh,
                        mhint__wcqoi, pitt__nktc, wjr__ggvz)
                    return xura__hwlnx(*args)
                if isinstance(mez__euqyx, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
                        )
                elif is_overload_constant_list(mez__euqyx):
                    edms__fnvu = get_overload_const_list(mez__euqyx)
                    qkeg__gbje = types.unliteral(mez__euqyx)
                    if qkeg__gbje.dtype == types.bool_:
                        if len(df.columns) != len(edms__fnvu):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {edms__fnvu} has {len(edms__fnvu)} values'
                                )
                        yagrv__jsoyv = []
                        tux__mmz = []
                        for asc__avu in range(len(edms__fnvu)):
                            if edms__fnvu[asc__avu]:
                                yagrv__jsoyv.append(df.columns[asc__avu])
                                tux__mmz.append(df.data[asc__avu])
                        vxts__yrzbu = tuple()
                        xura__hwlnx = DataFrameType(tuple(tux__mmz),
                            pitt__nktc, tuple(yagrv__jsoyv))
                        return xura__hwlnx(*args)
                    elif qkeg__gbje.dtype == bodo.string_type:
                        vxts__yrzbu, tux__mmz = self.get_kept_cols_and_data(df,
                            edms__fnvu)
                        xura__hwlnx = DataFrameType(tux__mmz, pitt__nktc,
                            vxts__yrzbu)
                        return xura__hwlnx(*args)
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
                yagrv__jsoyv = []
                tux__mmz = []
                for asc__avu, cxb__zkem in enumerate(df.columns):
                    if cxb__zkem[0] != ind_val:
                        continue
                    yagrv__jsoyv.append(cxb__zkem[1] if len(cxb__zkem) == 2
                         else cxb__zkem[1:])
                    tux__mmz.append(df.data[asc__avu])
                mhint__wcqoi = tuple(tux__mmz)
                sbz__csnpr = df.index
                uriu__fxb = tuple(yagrv__jsoyv)
                xura__hwlnx = DataFrameType(mhint__wcqoi, sbz__csnpr, uriu__fxb
                    )
                return xura__hwlnx(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                pvzjt__tbiea = df.columns.index(ind_val)
                mhint__wcqoi = df.data[pvzjt__tbiea]
                covgg__zjhzh = mhint__wcqoi.dtype
                sbz__csnpr = df.index
                wjr__ggvz = types.literal(df.columns[pvzjt__tbiea])
                xura__hwlnx = bodo.SeriesType(covgg__zjhzh, mhint__wcqoi,
                    sbz__csnpr, wjr__ggvz)
                return xura__hwlnx(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            mhint__wcqoi = df.data
            sbz__csnpr = self.replace_range_with_numeric_idx_if_needed(df, ind)
            uriu__fxb = df.columns
            xura__hwlnx = DataFrameType(mhint__wcqoi, sbz__csnpr, uriu__fxb,
                is_table_format=df.is_table_format)
            return xura__hwlnx(*args)
        elif is_overload_constant_list(ind):
            wzaw__hxag = get_overload_const_list(ind)
            uriu__fxb, mhint__wcqoi = self.get_kept_cols_and_data(df,
                wzaw__hxag)
            sbz__csnpr = df.index
            xura__hwlnx = DataFrameType(mhint__wcqoi, sbz__csnpr, uriu__fxb)
            return xura__hwlnx(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html'
            )

    def get_kept_cols_and_data(self, df, cols_to_keep_list):
        for rflah__wapy in cols_to_keep_list:
            if rflah__wapy not in df.columns:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(rflah__wapy, df.columns))
        uriu__fxb = tuple(cols_to_keep_list)
        mhint__wcqoi = tuple(df.data[df.columns.index(vcggc__wcr)] for
            vcggc__wcr in uriu__fxb)
        return uriu__fxb, mhint__wcqoi

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        pitt__nktc = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return pitt__nktc


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
            yagrv__jsoyv = []
            tux__mmz = []
            for asc__avu, cxb__zkem in enumerate(df.columns):
                if cxb__zkem[0] != ind_val:
                    continue
                yagrv__jsoyv.append(cxb__zkem[1] if len(cxb__zkem) == 2 else
                    cxb__zkem[1:])
                tux__mmz.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(asc__avu))
            joyp__iyw = 'def impl(df, ind):\n'
            mrb__gpwmo = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(joyp__iyw,
                yagrv__jsoyv, ', '.join(tux__mmz), mrb__gpwmo)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        wzaw__hxag = get_overload_const_list(ind)
        for rflah__wapy in wzaw__hxag:
            if rflah__wapy not in df.columns:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(rflah__wapy, df.columns))
        tux__mmz = ', '.join(
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}).copy()'
            .format(df.columns.index(rflah__wapy)) for rflah__wapy in
            wzaw__hxag)
        joyp__iyw = 'def impl(df, ind):\n'
        mrb__gpwmo = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(joyp__iyw,
            wzaw__hxag, tux__mmz, mrb__gpwmo)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        joyp__iyw = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            joyp__iyw += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        mrb__gpwmo = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            tux__mmz = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            tux__mmz = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(rflah__wapy)})[ind]'
                 for rflah__wapy in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(joyp__iyw, df.
            columns, tux__mmz, mrb__gpwmo, out_df_type=df)
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
        vcggc__wcr = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(vcggc__wcr)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        bhi__vlb = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, bhi__vlb)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        otix__sokia, = args
        pefv__mwbxc = signature.return_type
        xosur__mhqw = cgutils.create_struct_proxy(pefv__mwbxc)(context, builder
            )
        xosur__mhqw.obj = otix__sokia
        context.nrt.incref(builder, signature.args[0], otix__sokia)
        return xosur__mhqw._getvalue()
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
        llp__jxgs = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            gbde__wiavd = get_overload_const_int(idx.types[1])
            if gbde__wiavd < 0 or gbde__wiavd >= llp__jxgs:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            fshot__fqvq = [gbde__wiavd]
        else:
            is_out_series = False
            fshot__fqvq = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= llp__jxgs for
                ind in fshot__fqvq):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[fshot__fqvq])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                gbde__wiavd = fshot__fqvq[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, gbde__wiavd
                        )[idx[0]])
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
    joyp__iyw = 'def impl(I, idx):\n'
    joyp__iyw += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        joyp__iyw += f'  idx_t = {idx}\n'
    else:
        joyp__iyw += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    mrb__gpwmo = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    tux__mmz = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(rflah__wapy)})[idx_t]'
         for rflah__wapy in col_names)
    if is_out_series:
        zby__foh = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        joyp__iyw += f"""  return bodo.hiframes.pd_series_ext.init_series({tux__mmz}, {mrb__gpwmo}, {zby__foh})
"""
        gmfp__gjv = {}
        exec(joyp__iyw, {'bodo': bodo}, gmfp__gjv)
        return gmfp__gjv['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(joyp__iyw, col_names,
        tux__mmz, mrb__gpwmo)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    joyp__iyw = 'def impl(I, idx):\n'
    joyp__iyw += '  df = I._obj\n'
    tws__sirwc = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(rflah__wapy)})[{idx}]'
         for rflah__wapy in col_names)
    joyp__iyw += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    joyp__iyw += f"""  return bodo.hiframes.pd_series_ext.init_series(({tws__sirwc},), row_idx, None)
"""
    gmfp__gjv = {}
    exec(joyp__iyw, {'bodo': bodo}, gmfp__gjv)
    impl = gmfp__gjv['impl']
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
        vcggc__wcr = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(vcggc__wcr)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        bhi__vlb = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, bhi__vlb)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        otix__sokia, = args
        uifsr__enx = signature.return_type
        mzmsx__wegq = cgutils.create_struct_proxy(uifsr__enx)(context, builder)
        mzmsx__wegq.obj = otix__sokia
        context.nrt.incref(builder, signature.args[0], otix__sokia)
        return mzmsx__wegq._getvalue()
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
        joyp__iyw = 'def impl(I, idx):\n'
        joyp__iyw += '  df = I._obj\n'
        joyp__iyw += '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n'
        mrb__gpwmo = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        tux__mmz = ', '.join(
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[idx_t]'
            .format(df.columns.index(rflah__wapy)) for rflah__wapy in df.
            columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(joyp__iyw, df.
            columns, tux__mmz, mrb__gpwmo)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        frwa__sgmb = idx.types[1]
        if is_overload_constant_str(frwa__sgmb):
            zzbc__keev = get_overload_const_str(frwa__sgmb)
            gbde__wiavd = df.columns.index(zzbc__keev)

            def impl_col_name(I, idx):
                df = I._obj
                mrb__gpwmo = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                kohk__pato = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
                    df, gbde__wiavd)
                return bodo.hiframes.pd_series_ext.init_series(kohk__pato,
                    mrb__gpwmo, zzbc__keev).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(frwa__sgmb):
            col_idx_list = get_overload_const_list(frwa__sgmb)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(rflah__wapy in df.columns for
                rflah__wapy in col_idx_list):
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
    tux__mmz = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[idx[0]]'
        .format(df.columns.index(rflah__wapy)) for rflah__wapy in col_idx_list)
    mrb__gpwmo = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    joyp__iyw = 'def impl(I, idx):\n'
    joyp__iyw += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(joyp__iyw,
        col_idx_list, tux__mmz, mrb__gpwmo)


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
        vcggc__wcr = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(vcggc__wcr)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        bhi__vlb = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, bhi__vlb)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        otix__sokia, = args
        pfr__djmxq = signature.return_type
        uvic__xrzgq = cgutils.create_struct_proxy(pfr__djmxq)(context, builder)
        uvic__xrzgq.obj = otix__sokia
        context.nrt.incref(builder, signature.args[0], otix__sokia)
        return uvic__xrzgq._getvalue()
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
        gbde__wiavd = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            kohk__pato = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                gbde__wiavd)
            return kohk__pato[idx[0]]
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
        gbde__wiavd = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[gbde__wiavd]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            kohk__pato = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                gbde__wiavd)
            kohk__pato[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    uvic__xrzgq = cgutils.create_struct_proxy(fromty)(context, builder, val)
    luvn__lrpm = context.cast(builder, uvic__xrzgq.obj, fromty.df_type,
        toty.df_type)
    vorzd__jot = cgutils.create_struct_proxy(toty)(context, builder)
    vorzd__jot.obj = luvn__lrpm
    return vorzd__jot._getvalue()
