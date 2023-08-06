"""
Implement pd.DataFrame typing and data model handling.
"""
import json
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.cpython.listobj import ListInstance
from numba.extending import infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_index_ext import HeterogeneousIndexType, NumericIndexType, RangeIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.series_indexing import SeriesIlocType
from bodo.hiframes.table import Table, TableType, get_table_data, set_table_data_codegen
from bodo.io import json_cpp
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, py_table_to_cpp_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.distributed_api import bcast_scalar
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import str_arr_from_sequence, string_array_type
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.conversion import index_to_array
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import gen_const_tup, get_const_func_output_type, get_const_tup_vals
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_index_data_arr_types, get_literal_value, get_overload_const, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_udf_error_msg, get_udf_out_arr_type, is_heterogeneous_tuple_type, is_iterable_type, is_literal_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_tuple_like_type, raise_bodo_error, to_nullable_type
from bodo.utils.utils import is_null_pointer
_json_write = types.ExternalFunction('json_write', types.void(types.voidptr,
    types.voidptr, types.int64, types.int64, types.bool_, types.bool_,
    types.voidptr))
ll.add_symbol('json_write', json_cpp.json_write)


class DataFrameType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, data=None, index=None, columns=None, dist=None,
        is_table_format=False):
        from bodo.transforms.distributed_analysis import Distribution
        self.data = data
        if index is None:
            index = RangeIndexType(types.none)
        self.index = index
        self.columns = columns
        dist = Distribution.OneD_Var if dist is None else dist
        self.dist = dist
        self.is_table_format = is_table_format
        if columns is None:
            assert is_table_format, 'Determining columns at runtime is only supported for DataFrame with table format'
            self.table_type = TableType(tuple(data[:-1]), True)
        else:
            self.table_type = TableType(data) if is_table_format else None
        super(DataFrameType, self).__init__(name=
            f'dataframe({data}, {index}, {columns}, {dist}, {is_table_format})'
            )

    def __str__(self):
        if not self.has_runtime_cols and len(self.columns) > 20:
            qicq__yaq = f'{len(self.data)} columns of types {set(self.data)}'
            jgwc__rdjy = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({qicq__yaq}, {self.index}, {jgwc__rdjy}, {self.dist}, {self.is_table_format})'
                )
        return super().__str__()

    def copy(self, data=None, index=None, columns=None, dist=None,
        is_table_format=None):
        if data is None:
            data = self.data
        if columns is None:
            columns = self.columns
        if index is None:
            index = self.index
        if dist is None:
            dist = self.dist
        if is_table_format is None:
            is_table_format = self.is_table_format
        return DataFrameType(data, index, columns, dist, is_table_format)

    @property
    def has_runtime_cols(self):
        return self.columns is None

    @property
    def runtime_colname_typ(self):
        return self.data[-1] if self.has_runtime_cols else None

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return (self.data, self.index, self.columns, self.dist, self.
            is_table_format)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    def unify(self, typingctx, other):
        from bodo.transforms.distributed_analysis import Distribution
        if (isinstance(other, DataFrameType) and len(other.data) == len(
            self.data) and other.columns == self.columns and other.
            has_runtime_cols == self.has_runtime_cols):
            meshz__miap = (self.index if self.index == other.index else
                self.index.unify(typingctx, other.index))
            data = tuple(lulu__avltc.unify(typingctx, dkfmv__ivj) if 
                lulu__avltc != dkfmv__ivj else lulu__avltc for lulu__avltc,
                dkfmv__ivj in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if meshz__miap is not None and None not in data:
                return DataFrameType(data, meshz__miap, self.columns, dist,
                    self.is_table_format)
        if isinstance(other, DataFrameType) and len(self.data
            ) == 0 and not self.has_runtime_cols:
            return other

    def can_convert_to(self, typingctx, other):
        from numba.core.typeconv import Conversion
        if (isinstance(other, DataFrameType) and self.data == other.data and
            self.index == other.index and self.columns == other.columns and
            self.dist != other.dist and self.has_runtime_cols == other.
            has_runtime_cols):
            return Conversion.safe

    def is_precise(self):
        return all(lulu__avltc.is_precise() for lulu__avltc in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        gjmv__nckn = self.columns.index(col_name)
        iva__hjc = tuple(list(self.data[:gjmv__nckn]) + [new_type] + list(
            self.data[gjmv__nckn + 1:]))
        return DataFrameType(iva__hjc, self.index, self.columns, self.dist,
            self.is_table_format)


def check_runtime_cols_unsupported(df, func_name):
    if isinstance(df, DataFrameType) and df.has_runtime_cols:
        raise BodoError(
            f'{func_name} on DataFrames with columns determined at runtime is not yet supported. Please return the DataFrame to regular Python to update typing information.'
            )


class DataFramePayloadType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        super(DataFramePayloadType, self).__init__(name=
            f'DataFramePayloadType({df_type})')

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFramePayloadType)
class DataFramePayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        data_typ = types.Tuple(fe_type.df_type.data)
        if fe_type.df_type.is_table_format:
            data_typ = types.Tuple([fe_type.df_type.table_type])
        zcu__alh = [('data', data_typ), ('index', fe_type.df_type.index), (
            'parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            zcu__alh.append(('columns', fe_type.df_type.runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, zcu__alh)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        zcu__alh = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, zcu__alh)


make_attribute_wrapper(DataFrameType, 'meminfo', '_meminfo')


@infer_getattr
class DataFrameAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameType

    @bound_function('df.head')
    def resolve_head(self, df, args, kws):
        func_name = 'DataFrame.head'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        qay__irt = 'n',
        pqrp__plmr = {'n': 5}
        purc__kyarp, knfh__smehh = bodo.utils.typing.fold_typing_args(func_name
            , args, kws, qay__irt, pqrp__plmr)
        zsh__lbi = knfh__smehh[0]
        if not is_overload_int(zsh__lbi):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        lymj__oxehb = df.copy(is_table_format=False)
        return lymj__oxehb(*knfh__smehh).replace(pysig=purc__kyarp)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        dhh__qqpcr = (df,) + args
        qay__irt = 'df', 'method', 'min_periods'
        pqrp__plmr = {'method': 'pearson', 'min_periods': 1}
        srcy__gnr = 'method',
        purc__kyarp, knfh__smehh = bodo.utils.typing.fold_typing_args(func_name
            , dhh__qqpcr, kws, qay__irt, pqrp__plmr, srcy__gnr)
        tte__xzem = knfh__smehh[2]
        if not is_overload_int(tte__xzem):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        aayr__bgoa = []
        dldqy__fexem = []
        for iebsy__zzv, btqlt__eto in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(btqlt__eto.dtype):
                aayr__bgoa.append(iebsy__zzv)
                dldqy__fexem.append(types.Array(types.float64, 1, 'A'))
        if len(aayr__bgoa) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        dldqy__fexem = tuple(dldqy__fexem)
        aayr__bgoa = tuple(aayr__bgoa)
        index_typ = bodo.utils.typing.type_col_to_index(aayr__bgoa)
        lymj__oxehb = DataFrameType(dldqy__fexem, index_typ, aayr__bgoa)
        return lymj__oxehb(*knfh__smehh).replace(pysig=purc__kyarp)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        yvd__cxyf = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        gzywz__wtjjz = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        hwltx__pjz = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        nos__vws = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        sxz__gndyl = dict(raw=gzywz__wtjjz, result_type=hwltx__pjz)
        vue__ymhpu = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', sxz__gndyl, vue__ymhpu,
            package_name='pandas', module_name='DataFrame')
        mwiv__tmll = True
        if types.unliteral(yvd__cxyf) == types.unicode_type:
            if not is_overload_constant_str(yvd__cxyf):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            mwiv__tmll = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        usnkk__qedet = get_overload_const_int(axis)
        if mwiv__tmll and usnkk__qedet != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif usnkk__qedet not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        ukwrk__oxm = []
        for arr_typ in df.data:
            uhsv__wlaj = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            ffcg__frpf = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(uhsv__wlaj), types.int64), {}
                ).return_type
            ukwrk__oxm.append(ffcg__frpf)
        xki__frs = types.none
        dylkv__vhfsq = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(iebsy__zzv) for iebsy__zzv in df.columns)),
            None)
        rjy__wqtk = types.BaseTuple.from_types(ukwrk__oxm)
        plelh__hvl = df.index.dtype
        if plelh__hvl == types.NPDatetime('ns'):
            plelh__hvl = bodo.pd_timestamp_type
        if plelh__hvl == types.NPTimedelta('ns'):
            plelh__hvl = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(rjy__wqtk):
            ercqc__vzexd = HeterogeneousSeriesType(rjy__wqtk, dylkv__vhfsq,
                plelh__hvl)
        else:
            ercqc__vzexd = SeriesType(rjy__wqtk.dtype, rjy__wqtk,
                dylkv__vhfsq, plelh__hvl)
        mmnpx__vmihj = ercqc__vzexd,
        if nos__vws is not None:
            mmnpx__vmihj += tuple(nos__vws.types)
        try:
            if not mwiv__tmll:
                edch__mlcza = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(yvd__cxyf), self.context,
                    'DataFrame.apply', axis if usnkk__qedet == 1 else None)
            else:
                edch__mlcza = get_const_func_output_type(yvd__cxyf,
                    mmnpx__vmihj, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as vhry__tqwf:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()', vhry__tqwf)
                )
        if mwiv__tmll:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(edch__mlcza, (SeriesType, HeterogeneousSeriesType)
                ) and edch__mlcza.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(edch__mlcza, HeterogeneousSeriesType):
                typg__unevk, hbnha__phnn = edch__mlcza.const_info
                btrsq__scrhx = tuple(dtype_to_array_type(qbkq__uvf) for
                    qbkq__uvf in edch__mlcza.data.types)
                bvxxd__dxerm = DataFrameType(btrsq__scrhx, df.index,
                    hbnha__phnn)
            elif isinstance(edch__mlcza, SeriesType):
                icj__nsb, hbnha__phnn = edch__mlcza.const_info
                btrsq__scrhx = tuple(dtype_to_array_type(edch__mlcza.dtype) for
                    typg__unevk in range(icj__nsb))
                bvxxd__dxerm = DataFrameType(btrsq__scrhx, df.index,
                    hbnha__phnn)
            else:
                fxs__uzpi = get_udf_out_arr_type(edch__mlcza)
                bvxxd__dxerm = SeriesType(fxs__uzpi.dtype, fxs__uzpi, df.
                    index, None)
        else:
            bvxxd__dxerm = edch__mlcza
        uggdl__lbjvy = ', '.join("{} = ''".format(lulu__avltc) for
            lulu__avltc in kws.keys())
        sejm__wpgn = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {uggdl__lbjvy}):
"""
        sejm__wpgn += '    pass\n'
        pkqvu__xzphq = {}
        exec(sejm__wpgn, {}, pkqvu__xzphq)
        spwx__rwz = pkqvu__xzphq['apply_stub']
        purc__kyarp = numba.core.utils.pysignature(spwx__rwz)
        twl__sptk = (yvd__cxyf, axis, gzywz__wtjjz, hwltx__pjz, nos__vws
            ) + tuple(kws.values())
        return signature(bvxxd__dxerm, *twl__sptk).replace(pysig=purc__kyarp)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        qay__irt = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots', 'sharex',
            'sharey', 'layout', 'use_index', 'title', 'grid', 'legend',
            'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks', 'xlim',
            'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr', 'xerr',
            'secondary_y', 'sort_columns', 'xlabel', 'ylabel', 'position',
            'stacked', 'mark_right', 'include_bool', 'backend')
        pqrp__plmr = {'x': None, 'y': None, 'kind': 'line', 'figsize': None,
            'ax': None, 'subplots': False, 'sharex': None, 'sharey': False,
            'layout': None, 'use_index': True, 'title': None, 'grid': None,
            'legend': True, 'style': None, 'logx': False, 'logy': False,
            'loglog': False, 'xticks': None, 'yticks': None, 'xlim': None,
            'ylim': None, 'rot': None, 'fontsize': None, 'colormap': None,
            'table': False, 'yerr': None, 'xerr': None, 'secondary_y': 
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        srcy__gnr = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        purc__kyarp, knfh__smehh = bodo.utils.typing.fold_typing_args(func_name
            , args, kws, qay__irt, pqrp__plmr, srcy__gnr)
        ktyv__pja = knfh__smehh[2]
        if not is_overload_constant_str(ktyv__pja):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        lcmym__jpub = knfh__smehh[0]
        if not is_overload_none(lcmym__jpub) and not (is_overload_int(
            lcmym__jpub) or is_overload_constant_str(lcmym__jpub)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(lcmym__jpub):
            bgos__kumft = get_overload_const_str(lcmym__jpub)
            if bgos__kumft not in df.columns:
                raise BodoError(f'{func_name}: {bgos__kumft} column not found.'
                    )
        elif is_overload_int(lcmym__jpub):
            ughr__yov = get_overload_const_int(lcmym__jpub)
            if ughr__yov > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {ughr__yov} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            lcmym__jpub = df.columns[lcmym__jpub]
        bkxih__daxz = knfh__smehh[1]
        if not is_overload_none(bkxih__daxz) and not (is_overload_int(
            bkxih__daxz) or is_overload_constant_str(bkxih__daxz)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(bkxih__daxz):
            whkk__mxio = get_overload_const_str(bkxih__daxz)
            if whkk__mxio not in df.columns:
                raise BodoError(f'{func_name}: {whkk__mxio} column not found.')
        elif is_overload_int(bkxih__daxz):
            znc__nyl = get_overload_const_int(bkxih__daxz)
            if znc__nyl > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {znc__nyl} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            bkxih__daxz = df.columns[bkxih__daxz]
        ssbeg__laivw = knfh__smehh[3]
        if not is_overload_none(ssbeg__laivw) and not is_tuple_like_type(
            ssbeg__laivw):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        zgjdt__fgo = knfh__smehh[10]
        if not is_overload_none(zgjdt__fgo) and not is_overload_constant_str(
            zgjdt__fgo):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        qybwz__kbo = knfh__smehh[12]
        if not is_overload_bool(qybwz__kbo):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        udsr__pke = knfh__smehh[17]
        if not is_overload_none(udsr__pke) and not is_tuple_like_type(udsr__pke
            ):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        aojz__dbru = knfh__smehh[18]
        if not is_overload_none(aojz__dbru) and not is_tuple_like_type(
            aojz__dbru):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        zblf__ejel = knfh__smehh[22]
        if not is_overload_none(zblf__ejel) and not is_overload_int(zblf__ejel
            ):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        work__lsq = knfh__smehh[29]
        if not is_overload_none(work__lsq) and not is_overload_constant_str(
            work__lsq):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        kfdoh__vsg = knfh__smehh[30]
        if not is_overload_none(kfdoh__vsg) and not is_overload_constant_str(
            kfdoh__vsg):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        xgpn__gnks = types.List(types.mpl_line_2d_type)
        ktyv__pja = get_overload_const_str(ktyv__pja)
        if ktyv__pja == 'scatter':
            if is_overload_none(lcmym__jpub) and is_overload_none(bkxih__daxz):
                raise BodoError(
                    f'{func_name}: {ktyv__pja} requires an x and y column.')
            elif is_overload_none(lcmym__jpub):
                raise BodoError(
                    f'{func_name}: {ktyv__pja} x column is missing.')
            elif is_overload_none(bkxih__daxz):
                raise BodoError(
                    f'{func_name}: {ktyv__pja} y column is missing.')
            xgpn__gnks = types.mpl_path_collection_type
        elif ktyv__pja != 'line':
            raise BodoError(f'{func_name}: {ktyv__pja} plot is not supported.')
        return signature(xgpn__gnks, *knfh__smehh).replace(pysig=purc__kyarp)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            oawym__fakjg = df.columns.index(attr)
            arr_typ = df.data[oawym__fakjg]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            dsc__ugv = []
            iva__hjc = []
            fnvqn__drinv = False
            for i, jpksu__lup in enumerate(df.columns):
                if jpksu__lup[0] != attr:
                    continue
                fnvqn__drinv = True
                dsc__ugv.append(jpksu__lup[1] if len(jpksu__lup) == 2 else
                    jpksu__lup[1:])
                iva__hjc.append(df.data[i])
            if fnvqn__drinv:
                return DataFrameType(tuple(iva__hjc), df.index, tuple(dsc__ugv)
                    )


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        kcts__lnqf = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(kcts__lnqf)
        return lambda tup, idx: tup[val_ind]


def decref_df_data(context, builder, payload, df_type):
    if df_type.is_table_format:
        context.nrt.decref(builder, df_type.table_type, builder.
            extract_value(payload.data, 0))
        context.nrt.decref(builder, df_type.index, payload.index)
        if df_type.has_runtime_cols:
            context.nrt.decref(builder, df_type.data[-1], payload.columns)
        return
    for i in range(len(df_type.data)):
        cjfav__qide = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], cjfav__qide)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    iai__ukip = builder.module
    eben__fove = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    jwmt__kfxvi = cgutils.get_or_insert_function(iai__ukip, eben__fove,
        name='.dtor.df.{}'.format(df_type))
    if not jwmt__kfxvi.is_declaration:
        return jwmt__kfxvi
    jwmt__kfxvi.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(jwmt__kfxvi.append_basic_block())
    qbco__acr = jwmt__kfxvi.args[0]
    gjtit__vgjax = context.get_value_type(payload_type).as_pointer()
    wkqv__ruha = builder.bitcast(qbco__acr, gjtit__vgjax)
    payload = context.make_helper(builder, payload_type, ref=wkqv__ruha)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        bar__hcz = context.get_python_api(builder)
        rtc__qio = bar__hcz.gil_ensure()
        bar__hcz.decref(payload.parent)
        bar__hcz.gil_release(rtc__qio)
    builder.ret_void()
    return jwmt__kfxvi


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    uuf__rpzaj = cgutils.create_struct_proxy(payload_type)(context, builder)
    uuf__rpzaj.data = data_tup
    uuf__rpzaj.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        uuf__rpzaj.columns = colnames
    eyzw__vjraz = context.get_value_type(payload_type)
    wpen__prfe = context.get_abi_sizeof(eyzw__vjraz)
    vgk__qmox = define_df_dtor(context, builder, df_type, payload_type)
    hpxhv__fyh = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, wpen__prfe), vgk__qmox)
    mpq__warkb = context.nrt.meminfo_data(builder, hpxhv__fyh)
    nkct__ppvha = builder.bitcast(mpq__warkb, eyzw__vjraz.as_pointer())
    lqzp__fazwc = cgutils.create_struct_proxy(df_type)(context, builder)
    lqzp__fazwc.meminfo = hpxhv__fyh
    if parent is None:
        lqzp__fazwc.parent = cgutils.get_null_value(lqzp__fazwc.parent.type)
    else:
        lqzp__fazwc.parent = parent
        uuf__rpzaj.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            bar__hcz = context.get_python_api(builder)
            rtc__qio = bar__hcz.gil_ensure()
            bar__hcz.incref(parent)
            bar__hcz.gil_release(rtc__qio)
    builder.store(uuf__rpzaj._getvalue(), nkct__ppvha)
    return lqzp__fazwc._getvalue()


@intrinsic
def init_runtime_cols_dataframe(typingctx, data_typ, index_typ,
    colnames_index_typ=None):
    assert isinstance(data_typ, types.BaseTuple) and isinstance(data_typ.
        dtype, TableType
        ) and data_typ.dtype.has_runtime_cols, 'init_runtime_cols_dataframe must be called with a table that determines columns at runtime.'
    assert bodo.hiframes.pd_index_ext.is_pd_index_type(colnames_index_typ
        ) or isinstance(colnames_index_typ, bodo.hiframes.
        pd_multi_index_ext.MultiIndexType), 'Column names must be an index'
    if isinstance(data_typ.dtype.arr_types, types.UniTuple):
        eoy__xafny = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype.
            arr_types)
    else:
        eoy__xafny = [qbkq__uvf for qbkq__uvf in data_typ.dtype.arr_types]
    axeq__cdevv = DataFrameType(tuple(eoy__xafny + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        xwmx__gor = construct_dataframe(context, builder, df_type, data_tup,
            index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return xwmx__gor
    sig = signature(axeq__cdevv, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ=None):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    icj__nsb = len(data_tup_typ.types)
    if icj__nsb == 0:
        igso__psap = ()
    elif isinstance(col_names_typ, types.TypeRef):
        igso__psap = col_names_typ.instance_type.columns
    else:
        igso__psap = get_const_tup_vals(col_names_typ)
    if icj__nsb == 1 and isinstance(data_tup_typ.types[0], TableType):
        icj__nsb = len(data_tup_typ.types[0].arr_types)
    assert len(igso__psap
        ) == icj__nsb, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    tqdd__lmmjd = data_tup_typ.types
    if icj__nsb != 0 and isinstance(data_tup_typ.types[0], TableType):
        tqdd__lmmjd = data_tup_typ.types[0].arr_types
        is_table_format = True
    axeq__cdevv = DataFrameType(tqdd__lmmjd, index_typ, igso__psap,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            rgetn__atj = cgutils.create_struct_proxy(axeq__cdevv.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = rgetn__atj.parent
        xwmx__gor = construct_dataframe(context, builder, df_type, data_tup,
            index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return xwmx__gor
    sig = signature(axeq__cdevv, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        lqzp__fazwc = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, lqzp__fazwc.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        uuf__rpzaj = get_dataframe_payload(context, builder, df_typ, args[0])
        tovi__ywqr = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[tovi__ywqr]
        if df_typ.is_table_format:
            rgetn__atj = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(uuf__rpzaj.data, 0))
            yob__dcsk = df_typ.table_type.type_to_blk[arr_typ]
            guhi__kmfp = getattr(rgetn__atj, f'block_{yob__dcsk}')
            afd__ozgkb = ListInstance(context, builder, types.List(arr_typ),
                guhi__kmfp)
            ogjs__zeo = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[tovi__ywqr])
            cjfav__qide = afd__ozgkb.getitem(ogjs__zeo)
        else:
            cjfav__qide = builder.extract_value(uuf__rpzaj.data, tovi__ywqr)
        sgz__hsy = cgutils.alloca_once_value(builder, cjfav__qide)
        xow__ujllu = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, sgz__hsy, xow__ujllu)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    hpxhv__fyh = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, hpxhv__fyh)
    gjtit__vgjax = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, gjtit__vgjax)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    axeq__cdevv = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        axeq__cdevv = types.Tuple([TableType(df_typ.data)])
    sig = signature(axeq__cdevv, df_typ)

    def codegen(context, builder, signature, args):
        uuf__rpzaj = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            uuf__rpzaj.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, 'get_dataframe_index')

    def codegen(context, builder, signature, args):
        uuf__rpzaj = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, uuf__rpzaj
            .index)
    axeq__cdevv = df_typ.index
    sig = signature(axeq__cdevv, df_typ)
    return sig, codegen


def get_dataframe_data(df, i):
    return df[i]


@infer_global(get_dataframe_data)
class GetDataFrameDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        if not is_overload_constant_int(args[1]):
            raise_bodo_error(
                'Selecting a DataFrame column requires a constant column label'
                )
        df = args[0]
        check_runtime_cols_unsupported(df, 'get_dataframe_data')
        i = get_overload_const_int(args[1])
        lymj__oxehb = df.data[i]
        return lymj__oxehb(*args)


GetDataFrameDataInfer.prefer_literal = True


def get_dataframe_data_impl(df, i):
    if df.is_table_format:

        def _impl(df, i):
            if has_parent(df) and _column_needs_unboxing(df, i):
                bodo.hiframes.boxing.unbox_dataframe_column(df, i)
            return get_table_data(_get_dataframe_data(df)[0], i)
        return _impl

    def _impl(df, i):
        if has_parent(df) and _column_needs_unboxing(df, i):
            bodo.hiframes.boxing.unbox_dataframe_column(df, i)
        return _get_dataframe_data(df)[i]
    return _impl


@intrinsic
def get_dataframe_table(typingctx, df_typ=None):
    assert df_typ.is_table_format, 'get_dataframe_table() expects table format'

    def codegen(context, builder, signature, args):
        uuf__rpzaj = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(uuf__rpzaj.data, 0))
    return df_typ.table_type(df_typ), codegen


@lower_builtin(get_dataframe_data, DataFrameType, types.IntegerLiteral)
def lower_get_dataframe_data(context, builder, sig, args):
    impl = get_dataframe_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_dataframe_data',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_index',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_table',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func


def alias_ext_init_dataframe(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 3
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_dataframe',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_init_dataframe


def init_dataframe_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 3 and not kws
    data_tup = args[0]
    index = args[1]
    rjy__wqtk = self.typemap[data_tup.name]
    if any(is_tuple_like_type(qbkq__uvf) for qbkq__uvf in rjy__wqtk.types):
        return None
    if equiv_set.has_shape(data_tup):
        vport__uldu = equiv_set.get_shape(data_tup)
        if len(vport__uldu) > 1:
            equiv_set.insert_equiv(*vport__uldu)
        if len(vport__uldu) > 0:
            dylkv__vhfsq = self.typemap[index.name]
            if not isinstance(dylkv__vhfsq, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(vport__uldu[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(vport__uldu[0], len(
                vport__uldu)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    tdsiu__zwe = args[0]
    cfdz__uom = self.typemap[tdsiu__zwe.name].data
    if any(is_tuple_like_type(qbkq__uvf) for qbkq__uvf in cfdz__uom):
        return None
    if equiv_set.has_shape(tdsiu__zwe):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            tdsiu__zwe)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    tdsiu__zwe = args[0]
    dylkv__vhfsq = self.typemap[tdsiu__zwe.name].index
    if isinstance(dylkv__vhfsq, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(tdsiu__zwe):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            tdsiu__zwe)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    tdsiu__zwe = args[0]
    if equiv_set.has_shape(tdsiu__zwe):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            tdsiu__zwe), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    tovi__ywqr = get_overload_const_int(c_ind_typ)
    if df_typ.data[tovi__ywqr] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        fxse__vjim, typg__unevk, bpape__zrxu = args
        uuf__rpzaj = get_dataframe_payload(context, builder, df_typ, fxse__vjim
            )
        if df_typ.is_table_format:
            rgetn__atj = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(uuf__rpzaj.data, 0))
            yob__dcsk = df_typ.table_type.type_to_blk[arr_typ]
            guhi__kmfp = getattr(rgetn__atj, f'block_{yob__dcsk}')
            afd__ozgkb = ListInstance(context, builder, types.List(arr_typ),
                guhi__kmfp)
            ogjs__zeo = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[tovi__ywqr])
            afd__ozgkb.setitem(ogjs__zeo, bpape__zrxu, True)
        else:
            cjfav__qide = builder.extract_value(uuf__rpzaj.data, tovi__ywqr)
            context.nrt.decref(builder, df_typ.data[tovi__ywqr], cjfav__qide)
            uuf__rpzaj.data = builder.insert_value(uuf__rpzaj.data,
                bpape__zrxu, tovi__ywqr)
            context.nrt.incref(builder, arr_typ, bpape__zrxu)
        lqzp__fazwc = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=fxse__vjim)
        payload_type = DataFramePayloadType(df_typ)
        wkqv__ruha = context.nrt.meminfo_data(builder, lqzp__fazwc.meminfo)
        gjtit__vgjax = context.get_value_type(payload_type).as_pointer()
        wkqv__ruha = builder.bitcast(wkqv__ruha, gjtit__vgjax)
        builder.store(uuf__rpzaj._getvalue(), wkqv__ruha)
        return impl_ret_borrowed(context, builder, df_typ, fxse__vjim)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        hvh__ynws = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        yyga__hvc = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=hvh__ynws)
        mmy__llp = get_dataframe_payload(context, builder, df_typ, hvh__ynws)
        lqzp__fazwc = construct_dataframe(context, builder, signature.
            return_type, mmy__llp.data, index_val, yyga__hvc.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), mmy__llp.data)
        return lqzp__fazwc
    axeq__cdevv = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(axeq__cdevv, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    icj__nsb = len(df_type.columns)
    gnl__sexxr = icj__nsb
    khyyj__sycg = df_type.data
    igso__psap = df_type.columns
    index_typ = df_type.index
    shwca__xxdk = col_name not in df_type.columns
    tovi__ywqr = icj__nsb
    if shwca__xxdk:
        khyyj__sycg += arr_type,
        igso__psap += col_name,
        gnl__sexxr += 1
    else:
        tovi__ywqr = df_type.columns.index(col_name)
        khyyj__sycg = tuple(arr_type if i == tovi__ywqr else khyyj__sycg[i] for
            i in range(icj__nsb))

    def codegen(context, builder, signature, args):
        fxse__vjim, typg__unevk, bpape__zrxu = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, fxse__vjim)
        cbm__iwep = cgutils.create_struct_proxy(df_type)(context, builder,
            value=fxse__vjim)
        if df_type.is_table_format:
            rwbya__zaih = df_type.table_type
            zyc__blov = builder.extract_value(in_dataframe_payload.data, 0)
            rlkaz__fpl = TableType(khyyj__sycg)
            pawzc__ffuv = set_table_data_codegen(context, builder,
                rwbya__zaih, zyc__blov, rlkaz__fpl, arr_type, bpape__zrxu,
                tovi__ywqr, shwca__xxdk)
            data_tup = context.make_tuple(builder, types.Tuple([rlkaz__fpl]
                ), [pawzc__ffuv])
        else:
            tqdd__lmmjd = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != tovi__ywqr else bpape__zrxu) for i in range(
                icj__nsb)]
            if shwca__xxdk:
                tqdd__lmmjd.append(bpape__zrxu)
            for tdsiu__zwe, ctm__mcvw in zip(tqdd__lmmjd, khyyj__sycg):
                context.nrt.incref(builder, ctm__mcvw, tdsiu__zwe)
            data_tup = context.make_tuple(builder, types.Tuple(khyyj__sycg),
                tqdd__lmmjd)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        fnxes__ynhlv = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, cbm__iwep.parent, None)
        if not shwca__xxdk and arr_type == df_type.data[tovi__ywqr]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            wkqv__ruha = context.nrt.meminfo_data(builder, cbm__iwep.meminfo)
            gjtit__vgjax = context.get_value_type(payload_type).as_pointer()
            wkqv__ruha = builder.bitcast(wkqv__ruha, gjtit__vgjax)
            tkiqv__tpjxa = get_dataframe_payload(context, builder, df_type,
                fnxes__ynhlv)
            builder.store(tkiqv__tpjxa._getvalue(), wkqv__ruha)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, rlkaz__fpl, builder.
                    extract_value(data_tup, 0))
            else:
                for tdsiu__zwe, ctm__mcvw in zip(tqdd__lmmjd, khyyj__sycg):
                    context.nrt.incref(builder, ctm__mcvw, tdsiu__zwe)
        has_parent = cgutils.is_not_null(builder, cbm__iwep.parent)
        with builder.if_then(has_parent):
            bar__hcz = context.get_python_api(builder)
            rtc__qio = bar__hcz.gil_ensure()
            crfd__ukke = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, bpape__zrxu)
            iebsy__zzv = numba.core.pythonapi._BoxContext(context, builder,
                bar__hcz, crfd__ukke)
            wnyhn__zfix = iebsy__zzv.pyapi.from_native_value(arr_type,
                bpape__zrxu, iebsy__zzv.env_manager)
            if isinstance(col_name, str):
                mau__pwkhg = context.insert_const_string(builder.module,
                    col_name)
                knzj__bhbu = bar__hcz.string_from_string(mau__pwkhg)
            else:
                assert isinstance(col_name, int)
                knzj__bhbu = bar__hcz.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            bar__hcz.object_setitem(cbm__iwep.parent, knzj__bhbu, wnyhn__zfix)
            bar__hcz.decref(wnyhn__zfix)
            bar__hcz.decref(knzj__bhbu)
            bar__hcz.gil_release(rtc__qio)
        return fnxes__ynhlv
    axeq__cdevv = DataFrameType(khyyj__sycg, index_typ, igso__psap, df_type
        .dist, df_type.is_table_format)
    sig = signature(axeq__cdevv, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    icj__nsb = len(pyval.columns)
    tqdd__lmmjd = tuple(pyval.iloc[:, i].values for i in range(icj__nsb))
    if df_type.is_table_format:
        rgetn__atj = context.get_constant_generic(builder, df_type.
            table_type, Table(tqdd__lmmjd))
        data_tup = lir.Constant.literal_struct([rgetn__atj])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], jpksu__lup) for 
            i, jpksu__lup in enumerate(tqdd__lmmjd)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    vze__hnav = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, vze__hnav])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    wzwlb__znm = context.get_constant(types.int64, -1)
    cut__mbqi = context.get_constant_null(types.voidptr)
    hpxhv__fyh = lir.Constant.literal_struct([wzwlb__znm, cut__mbqi,
        cut__mbqi, payload, wzwlb__znm])
    hpxhv__fyh = cgutils.global_constant(builder, '.const.meminfo', hpxhv__fyh
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([hpxhv__fyh, vze__hnav])


@lower_cast(DataFrameType, DataFrameType)
def cast_df_to_df(context, builder, fromty, toty, val):
    if (fromty.data == toty.data and fromty.index == toty.index and fromty.
        columns == toty.columns and fromty.is_table_format == toty.
        is_table_format and fromty.dist != toty.dist and fromty.
        has_runtime_cols == toty.has_runtime_cols):
        return val
    if not fromty.has_runtime_cols and not toty.has_runtime_cols and len(fromty
        .data) == 0 and len(toty.columns):
        return _cast_empty_df(context, builder, toty)
    if (fromty.data != toty.data or fromty.has_runtime_cols != toty.
        has_runtime_cols):
        raise BodoError(f'Invalid dataframe cast from {fromty} to {toty}')
    in_dataframe_payload = get_dataframe_payload(context, builder, fromty, val)
    if isinstance(fromty.index, RangeIndexType) and isinstance(toty.index,
        NumericIndexType):
        meshz__miap = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        meshz__miap = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, meshz__miap)
    if fromty.is_table_format == toty.is_table_format:
        iva__hjc = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                iva__hjc)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), iva__hjc)
    elif toty.is_table_format:
        iva__hjc = _cast_df_data_to_table_format(context, builder, fromty,
            toty, in_dataframe_payload)
    else:
        iva__hjc = _cast_df_data_to_tuple_format(context, builder, fromty,
            toty, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, iva__hjc,
        meshz__miap, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    egcyu__xnc = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        vhbjr__irt = get_index_data_arr_types(toty.index)[0]
        ctqsl__qmcl = bodo.utils.transform.get_type_alloc_counts(vhbjr__irt
            ) - 1
        yhz__cxvju = ', '.join('0' for typg__unevk in range(ctqsl__qmcl))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(yhz__cxvju, ', ' if ctqsl__qmcl == 1 else ''))
        egcyu__xnc['index_arr_type'] = vhbjr__irt
    nmf__mfigd = []
    for i, arr_typ in enumerate(toty.data):
        ctqsl__qmcl = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        yhz__cxvju = ', '.join('0' for typg__unevk in range(ctqsl__qmcl))
        tae__exbp = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'.
            format(i, yhz__cxvju, ', ' if ctqsl__qmcl == 1 else ''))
        nmf__mfigd.append(tae__exbp)
        egcyu__xnc[f'arr_type{i}'] = arr_typ
    nmf__mfigd = ', '.join(nmf__mfigd)
    sejm__wpgn = 'def impl():\n'
    zhton__uoz = bodo.hiframes.dataframe_impl._gen_init_df(sejm__wpgn, toty
        .columns, nmf__mfigd, index, egcyu__xnc)
    df = context.compile_internal(builder, zhton__uoz, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    qmyk__aep = toty.table_type
    rgetn__atj = cgutils.create_struct_proxy(qmyk__aep)(context, builder)
    rgetn__atj.parent = in_dataframe_payload.parent
    for qbkq__uvf, yob__dcsk in qmyk__aep.type_to_blk.items():
        dlq__dnlwv = context.get_constant(types.int64, len(qmyk__aep.
            block_to_arr_ind[yob__dcsk]))
        typg__unevk, yged__xvo = ListInstance.allocate_ex(context, builder,
            types.List(qbkq__uvf), dlq__dnlwv)
        yged__xvo.size = dlq__dnlwv
        setattr(rgetn__atj, f'block_{yob__dcsk}', yged__xvo.value)
    for i, qbkq__uvf in enumerate(fromty.data):
        cjfav__qide = builder.extract_value(in_dataframe_payload.data, i)
        yob__dcsk = qmyk__aep.type_to_blk[qbkq__uvf]
        guhi__kmfp = getattr(rgetn__atj, f'block_{yob__dcsk}')
        afd__ozgkb = ListInstance(context, builder, types.List(qbkq__uvf),
            guhi__kmfp)
        ogjs__zeo = context.get_constant(types.int64, qmyk__aep.
            block_offsets[i])
        afd__ozgkb.setitem(ogjs__zeo, cjfav__qide, True)
    data_tup = context.make_tuple(builder, types.Tuple([qmyk__aep]), [
        rgetn__atj._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    qmyk__aep = fromty.table_type
    rgetn__atj = cgutils.create_struct_proxy(qmyk__aep)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    tqdd__lmmjd = []
    for i, qbkq__uvf in enumerate(toty.data):
        yob__dcsk = qmyk__aep.type_to_blk[qbkq__uvf]
        guhi__kmfp = getattr(rgetn__atj, f'block_{yob__dcsk}')
        afd__ozgkb = ListInstance(context, builder, types.List(qbkq__uvf),
            guhi__kmfp)
        ogjs__zeo = context.get_constant(types.int64, qmyk__aep.
            block_offsets[i])
        cjfav__qide = afd__ozgkb.getitem(ogjs__zeo)
        context.nrt.incref(builder, qbkq__uvf, cjfav__qide)
        tqdd__lmmjd.append(cjfav__qide)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), tqdd__lmmjd)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    mhr__tnjkq, nmf__mfigd, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    nyov__clep = gen_const_tup(mhr__tnjkq)
    sejm__wpgn = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    sejm__wpgn += (
        '  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, {})\n'
        .format(nmf__mfigd, index_arg, nyov__clep))
    pkqvu__xzphq = {}
    exec(sejm__wpgn, {'bodo': bodo, 'np': np}, pkqvu__xzphq)
    thuu__plu = pkqvu__xzphq['_init_df']
    return thuu__plu


def _get_df_args(data, index, columns, dtype, copy):
    tdhp__dknb = ''
    if not is_overload_none(dtype):
        tdhp__dknb = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        icj__nsb = (len(data.types) - 1) // 2
        tzo__mkx = [qbkq__uvf.literal_value for qbkq__uvf in data.types[1:
            icj__nsb + 1]]
        data_val_types = dict(zip(tzo__mkx, data.types[icj__nsb + 1:]))
        tqdd__lmmjd = ['data[{}]'.format(i) for i in range(icj__nsb + 1, 2 *
            icj__nsb + 1)]
        data_dict = dict(zip(tzo__mkx, tqdd__lmmjd))
        if is_overload_none(index):
            for i, qbkq__uvf in enumerate(data.types[icj__nsb + 1:]):
                if isinstance(qbkq__uvf, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(icj__nsb + 1 + i))
                    index_is_none = False
                    break
    elif is_overload_none(data):
        data_dict = {}
        data_val_types = {}
    else:
        if not (isinstance(data, types.Array) and data.ndim == 2):
            raise BodoError(
                'pd.DataFrame() only supports constant dictionary and array input'
                )
        if is_overload_none(columns):
            raise BodoError(
                "pd.DataFrame() 'columns' argument is required when an array is passed as data"
                )
        bvu__ady = '.copy()' if copy else ''
        lky__bnjf = get_overload_const_list(columns)
        icj__nsb = len(lky__bnjf)
        data_val_types = {iebsy__zzv: data.copy(ndim=1) for iebsy__zzv in
            lky__bnjf}
        tqdd__lmmjd = ['data[:,{}]{}'.format(i, bvu__ady) for i in range(
            icj__nsb)]
        data_dict = dict(zip(lky__bnjf, tqdd__lmmjd))
    if is_overload_none(columns):
        col_names = data_dict.keys()
    else:
        col_names = get_overload_const_list(columns)
    df_len = _get_df_len_from_info(data_dict, data_val_types, col_names,
        index_is_none, index_arg)
    _fill_null_arrays(data_dict, col_names, df_len, dtype)
    if index_is_none:
        if is_overload_none(data):
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_binary_str_index(bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0))'
                )
        else:
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, {}, 1, None)'
                .format(df_len))
    nmf__mfigd = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[iebsy__zzv], df_len, tdhp__dknb) for iebsy__zzv in
        col_names))
    if len(col_names) == 0:
        nmf__mfigd = '()'
    return col_names, nmf__mfigd, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for iebsy__zzv in col_names:
        if iebsy__zzv in data_dict and is_iterable_type(data_val_types[
            iebsy__zzv]):
            df_len = 'len({})'.format(data_dict[iebsy__zzv])
            break
    if df_len == '0' and not index_is_none:
        df_len = f'len({index_arg})'
    return df_len


def _fill_null_arrays(data_dict, col_names, df_len, dtype):
    if all(iebsy__zzv in data_dict for iebsy__zzv in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    fjn__gmc = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for iebsy__zzv in col_names:
        if iebsy__zzv not in data_dict:
            data_dict[iebsy__zzv] = fjn__gmc


@overload(len)
def df_len_overload(df):
    if not isinstance(df, DataFrameType):
        return
    if df.has_runtime_cols:

        def impl(df):
            qbkq__uvf = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(qbkq__uvf)
        return impl
    if len(df.columns) == 0:
        return lambda df: 0

    def impl(df):
        if is_null_pointer(df._meminfo):
            return 0
        return len(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, 0))
    return impl


@infer_global(operator.getitem)
class GetItemTuple(AbstractTemplate):
    key = operator.getitem

    def generic(self, args, kws):
        tup, idx = args
        if not isinstance(tup, types.BaseTuple) or not isinstance(idx,
            types.IntegerLiteral):
            return
        hyf__qxfu = idx.literal_value
        if isinstance(hyf__qxfu, int):
            lymj__oxehb = tup.types[hyf__qxfu]
        elif isinstance(hyf__qxfu, slice):
            lymj__oxehb = types.BaseTuple.from_types(tup.types[hyf__qxfu])
        return signature(lymj__oxehb, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    jvbv__fyqly, idx = sig.args
    idx = idx.literal_value
    tup, typg__unevk = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(jvbv__fyqly)
        if not 0 <= idx < len(jvbv__fyqly):
            raise IndexError('cannot index at %d in %s' % (idx, jvbv__fyqly))
        nyrry__ahxl = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        fpjel__kjqiu = cgutils.unpack_tuple(builder, tup)[idx]
        nyrry__ahxl = context.make_tuple(builder, sig.return_type, fpjel__kjqiu
            )
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, nyrry__ahxl)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, vkgx__lqg, suffix_x,
            suffix_y, is_join, indicator, _bodo_na_equal, idhk__zxc) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        xcu__xoary = set(left_on) & set(right_on)
        vsl__vejeh = set(left_df.columns) & set(right_df.columns)
        cxmj__lgbzw = vsl__vejeh - xcu__xoary
        onowo__oekbn = '$_bodo_index_' in left_on
        cwr__grs = '$_bodo_index_' in right_on
        how = get_overload_const_str(vkgx__lqg)
        ohb__miwm = how in {'left', 'outer'}
        nlm__mrq = how in {'right', 'outer'}
        columns = []
        data = []
        if onowo__oekbn and not cwr__grs and not is_join.literal_value:
            ntp__zebe = right_on[0]
            if ntp__zebe in left_df.columns:
                columns.append(ntp__zebe)
                data.append(right_df.data[right_df.columns.index(ntp__zebe)])
        if cwr__grs and not onowo__oekbn and not is_join.literal_value:
            jdqfw__yjqpl = left_on[0]
            if jdqfw__yjqpl in right_df.columns:
                columns.append(jdqfw__yjqpl)
                data.append(left_df.data[left_df.columns.index(jdqfw__yjqpl)])
        for qrvg__msrf, ibnhq__frrx in zip(left_df.data, left_df.columns):
            columns.append(str(ibnhq__frrx) + suffix_x.literal_value if 
                ibnhq__frrx in cxmj__lgbzw else ibnhq__frrx)
            if ibnhq__frrx in xcu__xoary:
                data.append(qrvg__msrf)
            else:
                data.append(to_nullable_type(qrvg__msrf) if nlm__mrq else
                    qrvg__msrf)
        for qrvg__msrf, ibnhq__frrx in zip(right_df.data, right_df.columns):
            if ibnhq__frrx not in xcu__xoary:
                columns.append(str(ibnhq__frrx) + suffix_y.literal_value if
                    ibnhq__frrx in cxmj__lgbzw else ibnhq__frrx)
                data.append(to_nullable_type(qrvg__msrf) if ohb__miwm else
                    qrvg__msrf)
        orqgy__gskkh = get_overload_const_bool(indicator)
        if orqgy__gskkh:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        if onowo__oekbn and cwr__grs and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        elif onowo__oekbn and not cwr__grs:
            index_typ = right_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        elif cwr__grs and not onowo__oekbn:
            index_typ = left_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        wpd__vnuva = DataFrameType(tuple(data), index_typ, tuple(columns))
        return signature(wpd__vnuva, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    lqzp__fazwc = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return lqzp__fazwc._getvalue()


@overload(pd.concat, inline='always', no_unliteral=True)
def concat_overload(objs, axis=0, join='outer', join_axes=None,
    ignore_index=False, keys=None, levels=None, names=None,
    verify_integrity=False, sort=None, copy=True):
    if not is_overload_constant_int(axis):
        raise BodoError("pd.concat(): 'axis' should be a constant integer")
    if not is_overload_constant_bool(ignore_index):
        raise BodoError(
            "pd.concat(): 'ignore_index' should be a constant boolean")
    axis = get_overload_const_int(axis)
    ignore_index = is_overload_true(ignore_index)
    sxz__gndyl = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    pqrp__plmr = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', sxz__gndyl, pqrp__plmr,
        package_name='pandas', module_name='General')
    sejm__wpgn = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        yckur__nvcfj = 0
        nmf__mfigd = []
        names = []
        for i, pqvuw__kgc in enumerate(objs.types):
            assert isinstance(pqvuw__kgc, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(pqvuw__kgc, 'pd.concat()')
            if isinstance(pqvuw__kgc, SeriesType):
                names.append(str(yckur__nvcfj))
                yckur__nvcfj += 1
                nmf__mfigd.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(pqvuw__kgc.columns)
                for lgnr__mxfp in range(len(pqvuw__kgc.data)):
                    nmf__mfigd.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, lgnr__mxfp))
        return bodo.hiframes.dataframe_impl._gen_init_df(sejm__wpgn, names,
            ', '.join(nmf__mfigd), index)
    assert axis == 0
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(qbkq__uvf, DataFrameType) for qbkq__uvf in
            objs.types)
        kly__dmaow = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pd.concat()')
            kly__dmaow.extend(df.columns)
        kly__dmaow = list(dict.fromkeys(kly__dmaow).keys())
        eoy__xafny = {}
        for yckur__nvcfj, iebsy__zzv in enumerate(kly__dmaow):
            for df in objs.types:
                if iebsy__zzv in df.columns:
                    eoy__xafny['arr_typ{}'.format(yckur__nvcfj)] = df.data[df
                        .columns.index(iebsy__zzv)]
                    break
        assert len(eoy__xafny) == len(kly__dmaow)
        hkghd__apc = []
        for yckur__nvcfj, iebsy__zzv in enumerate(kly__dmaow):
            args = []
            for i, df in enumerate(objs.types):
                if iebsy__zzv in df.columns:
                    tovi__ywqr = df.columns.index(iebsy__zzv)
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, tovi__ywqr))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, yckur__nvcfj))
            sejm__wpgn += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(yckur__nvcfj, ', '.join(args)))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(A0), 1, None)'
                )
        else:
            index = (
                """bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)) if len(objs[i].
                columns) > 0)))
        return bodo.hiframes.dataframe_impl._gen_init_df(sejm__wpgn,
            kly__dmaow, ', '.join('A{}'.format(i) for i in range(len(
            kly__dmaow))), index, eoy__xafny)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(qbkq__uvf, SeriesType) for qbkq__uvf in objs.
            types)
        sejm__wpgn += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            sejm__wpgn += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            sejm__wpgn += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        sejm__wpgn += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        pkqvu__xzphq = {}
        exec(sejm__wpgn, {'bodo': bodo, 'np': np, 'numba': numba}, pkqvu__xzphq
            )
        return pkqvu__xzphq['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pd.concat()')
        df_type = objs.dtype
        for yckur__nvcfj, iebsy__zzv in enumerate(df_type.columns):
            sejm__wpgn += '  arrs{} = []\n'.format(yckur__nvcfj)
            sejm__wpgn += '  for i in range(len(objs)):\n'
            sejm__wpgn += '    df = objs[i]\n'
            sejm__wpgn += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(yckur__nvcfj))
            sejm__wpgn += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(yckur__nvcfj))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            sejm__wpgn += '  arrs_index = []\n'
            sejm__wpgn += '  for i in range(len(objs)):\n'
            sejm__wpgn += '    df = objs[i]\n'
            sejm__wpgn += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(sejm__wpgn,
            df_type.columns, ', '.join('out_arr{}'.format(i) for i in range
            (len(df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        sejm__wpgn += '  arrs = []\n'
        sejm__wpgn += '  for i in range(len(objs)):\n'
        sejm__wpgn += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        sejm__wpgn += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            sejm__wpgn += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            sejm__wpgn += '  arrs_index = []\n'
            sejm__wpgn += '  for i in range(len(objs)):\n'
            sejm__wpgn += '    S = objs[i]\n'
            sejm__wpgn += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            sejm__wpgn += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        sejm__wpgn += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        pkqvu__xzphq = {}
        exec(sejm__wpgn, {'bodo': bodo, 'np': np, 'numba': numba}, pkqvu__xzphq
            )
        return pkqvu__xzphq['impl']
    raise BodoError('pd.concat(): input type {} not supported yet'.format(objs)
        )


def sort_values_dummy(df, by, ascending, inplace, na_position):
    return df.sort_values(by, ascending=ascending, inplace=inplace,
        na_position=na_position)


@infer_global(sort_values_dummy)
class SortDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, by, ascending, inplace, na_position = args
        index = df.index
        if isinstance(index, bodo.hiframes.pd_index_ext.RangeIndexType):
            index = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64)
        axeq__cdevv = df.copy(index=index, is_table_format=False)
        return signature(axeq__cdevv, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    jekn__ygra = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return jekn__ygra._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    sxz__gndyl = dict(index=index, name=name)
    pqrp__plmr = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', sxz__gndyl, pqrp__plmr,
        package_name='pandas', module_name='DataFrame')

    def _impl(df, index=True, name='Pandas'):
        return bodo.hiframes.pd_dataframe_ext.itertuples_dummy(df)
    return _impl


def itertuples_dummy(df):
    return df


@infer_global(itertuples_dummy)
class ItertuplesDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, = args
        assert 'Index' not in df.columns
        columns = ('Index',) + df.columns
        eoy__xafny = (types.Array(types.int64, 1, 'C'),) + df.data
        kql__aqddz = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, eoy__xafny)
        return signature(kql__aqddz, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    jekn__ygra = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return jekn__ygra._getvalue()


def query_dummy(df, expr):
    return df.eval(expr)


@infer_global(query_dummy)
class QueryDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=RangeIndexType(types
            .none)), *args)


@lower_builtin(query_dummy, types.VarArg(types.Any))
def lower_query_dummy(context, builder, sig, args):
    jekn__ygra = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return jekn__ygra._getvalue()


def val_isin_dummy(S, vals):
    return S in vals


def val_notin_dummy(S, vals):
    return S not in vals


@infer_global(val_isin_dummy)
@infer_global(val_notin_dummy)
class ValIsinTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=args[0].index), *args)


@lower_builtin(val_isin_dummy, types.VarArg(types.Any))
@lower_builtin(val_notin_dummy, types.VarArg(types.Any))
def lower_val_isin_dummy(context, builder, sig, args):
    jekn__ygra = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return jekn__ygra._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values, index_name,
    columns_name, value_names, check_duplicates=True, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    wyca__fjzer = get_overload_const_bool(check_duplicates)
    vpxxi__puq = not is_overload_none(value_names)
    nhisq__bjiiw = isinstance(values_tup, types.UniTuple)
    if nhisq__bjiiw:
        hsp__egws = [to_nullable_type(values_tup.dtype)]
    else:
        hsp__egws = [to_nullable_type(ctm__mcvw) for ctm__mcvw in values_tup]
    sejm__wpgn = 'def impl(\n'
    sejm__wpgn += """    index_tup, columns_tup, values_tup, pivot_values, index_name, columns_name, value_names, check_duplicates=True, parallel=False
"""
    sejm__wpgn += '):\n'
    sejm__wpgn += '    if parallel:\n'
    kwzg__rty = ', '.join([f'array_to_info(index_tup[{i}])' for i in range(
        len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for i in
        range(len(columns_tup))] + [f'array_to_info(values_tup[{i}])' for i in
        range(len(values_tup))])
    sejm__wpgn += f'        info_list = [{kwzg__rty}]\n'
    sejm__wpgn += '        cpp_table = arr_info_list_to_table(info_list)\n'
    sejm__wpgn += (
        '        out_cpp_table = shuffle_table(cpp_table, 1, parallel, 0)\n')
    pltw__ysb = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
         for i in range(len(index_tup))])
    ybst__lswfo = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
         for i in range(len(columns_tup))])
    dyen__yecws = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
         for i in range(len(values_tup))])
    sejm__wpgn += f'        index_tup = ({pltw__ysb},)\n'
    sejm__wpgn += f'        columns_tup = ({ybst__lswfo},)\n'
    sejm__wpgn += f'        values_tup = ({dyen__yecws},)\n'
    sejm__wpgn += '        delete_table(cpp_table)\n'
    sejm__wpgn += '        delete_table(out_cpp_table)\n'
    sejm__wpgn += '    index_arr = index_tup[0]\n'
    sejm__wpgn += '    columns_arr = columns_tup[0]\n'
    if nhisq__bjiiw:
        sejm__wpgn += '    values_arrs = [arr for arr in values_tup]\n'
    sejm__wpgn += """    unique_index_arr, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    sejm__wpgn += '        index_arr\n'
    sejm__wpgn += '    )\n'
    sejm__wpgn += '    n_rows = len(unique_index_arr)\n'
    sejm__wpgn += '    num_values_arrays = len(values_tup)\n'
    sejm__wpgn += '    n_unique_pivots = len(pivot_values)\n'
    if nhisq__bjiiw:
        sejm__wpgn += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        sejm__wpgn += '    n_cols = n_unique_pivots\n'
    sejm__wpgn += '    col_map = {}\n'
    sejm__wpgn += '    for i in range(n_unique_pivots):\n'
    sejm__wpgn += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    sejm__wpgn += '            raise ValueError(\n'
    sejm__wpgn += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    sejm__wpgn += '            )\n'
    sejm__wpgn += '        col_map[pivot_values[i]] = i\n'
    ebhnr__cgrw = False
    for i, ckp__epwe in enumerate(hsp__egws):
        if ckp__epwe == bodo.string_array_type:
            ebhnr__cgrw = True
            sejm__wpgn += f"""    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]
"""
            sejm__wpgn += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if ebhnr__cgrw:
        if wyca__fjzer:
            sejm__wpgn += '    nbytes = (n_rows + 7) >> 3\n'
            sejm__wpgn += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        sejm__wpgn += '    for i in range(len(columns_arr)):\n'
        sejm__wpgn += '        col_name = columns_arr[i]\n'
        sejm__wpgn += '        pivot_idx = col_map[col_name]\n'
        sejm__wpgn += '        row_idx = row_vector[i]\n'
        if wyca__fjzer:
            sejm__wpgn += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            sejm__wpgn += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            sejm__wpgn += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            sejm__wpgn += '        else:\n'
            sejm__wpgn += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if nhisq__bjiiw:
            sejm__wpgn += '        for j in range(num_values_arrays):\n'
            sejm__wpgn += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            sejm__wpgn += '            len_arr = len_arrs_0[col_idx]\n'
            sejm__wpgn += '            values_arr = values_arrs[j]\n'
            sejm__wpgn += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            sejm__wpgn += (
                '                len_arr[row_idx] = len(values_arr[i])\n')
            sejm__wpgn += (
                '                total_lens_0[col_idx] += len(values_arr[i])\n'
                )
        else:
            for i, ckp__epwe in enumerate(hsp__egws):
                if ckp__epwe == bodo.string_array_type:
                    sejm__wpgn += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    sejm__wpgn += f"""            len_arrs_{i}[pivot_idx][row_idx] = len(values_tup[{i}][i])
"""
                    sejm__wpgn += f"""            total_lens_{i}[pivot_idx] += len(values_tup[{i}][i])
"""
    for i, ckp__epwe in enumerate(hsp__egws):
        if ckp__epwe == bodo.string_array_type:
            sejm__wpgn += f'    data_arrs_{i} = [\n'
            sejm__wpgn += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            sejm__wpgn += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            sejm__wpgn += '        )\n'
            sejm__wpgn += '        for i in range(n_cols)\n'
            sejm__wpgn += '    ]\n'
        else:
            sejm__wpgn += f'    data_arrs_{i} = [\n'
            sejm__wpgn += f"""        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})
"""
            sejm__wpgn += '        for _ in range(n_cols)\n'
            sejm__wpgn += '    ]\n'
    if not ebhnr__cgrw and wyca__fjzer:
        sejm__wpgn += '    nbytes = (n_rows + 7) >> 3\n'
        sejm__wpgn += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    sejm__wpgn += '    for i in range(len(columns_arr)):\n'
    sejm__wpgn += '        col_name = columns_arr[i]\n'
    sejm__wpgn += '        pivot_idx = col_map[col_name]\n'
    sejm__wpgn += '        row_idx = row_vector[i]\n'
    if not ebhnr__cgrw and wyca__fjzer:
        sejm__wpgn += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        sejm__wpgn += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
        sejm__wpgn += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        sejm__wpgn += '        else:\n'
        sejm__wpgn += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if nhisq__bjiiw:
        sejm__wpgn += '        for j in range(num_values_arrays):\n'
        sejm__wpgn += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        sejm__wpgn += '            col_arr = data_arrs_0[col_idx]\n'
        sejm__wpgn += '            values_arr = values_arrs[j]\n'
        sejm__wpgn += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        sejm__wpgn += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        sejm__wpgn += '            else:\n'
        sejm__wpgn += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, ckp__epwe in enumerate(hsp__egws):
            sejm__wpgn += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            sejm__wpgn += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            sejm__wpgn += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            sejm__wpgn += f'        else:\n'
            sejm__wpgn += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    sejm__wpgn += """    index = bodo.utils.conversion.index_from_array(unique_index_arr, index_name)
"""
    if vpxxi__puq:
        sejm__wpgn += '    num_rows = len(value_names) * len(pivot_values)\n'
        if value_names == bodo.string_array_type:
            sejm__wpgn += '    total_chars = 0\n'
            sejm__wpgn += '    for i in range(len(value_names)):\n'
            sejm__wpgn += '        total_chars += len(value_names[i])\n'
            sejm__wpgn += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
        else:
            sejm__wpgn += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names, (-1,))
"""
        if pivot_values == bodo.string_array_type:
            sejm__wpgn += '    total_chars = 0\n'
            sejm__wpgn += '    for i in range(len(pivot_values)):\n'
            sejm__wpgn += '        total_chars += len(pivot_values[i])\n'
            sejm__wpgn += """    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(value_names))
"""
        else:
            sejm__wpgn += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
        sejm__wpgn += '    for i in range(len(value_names)):\n'
        sejm__wpgn += '        for j in range(len(pivot_values)):\n'
        sejm__wpgn += (
            '            new_value_names[(i * len(pivot_values)) + j] = value_names[i]\n'
            )
        sejm__wpgn += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
        sejm__wpgn += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name), None)
"""
    else:
        sejm__wpgn += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name)
"""
    gii__wpv = ', '.join(f'data_arrs_{i}' for i in range(len(hsp__egws)))
    sejm__wpgn += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({gii__wpv},), n_rows)
"""
    sejm__wpgn += (
        '    return bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
        )
    sejm__wpgn += '        (table,), index, column_index\n'
    sejm__wpgn += '    )\n'
    pkqvu__xzphq = {}
    kkgkq__aizr = {f'data_arr_typ_{i}': ckp__epwe for i, ckp__epwe in
        enumerate(hsp__egws)}
    dpyp__dojjs = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, **kkgkq__aizr}
    exec(sejm__wpgn, dpyp__dojjs, pkqvu__xzphq)
    impl = pkqvu__xzphq['impl']
    return impl


def gen_pandas_parquet_metadata(df, write_non_range_index_to_metadata,
    write_rangeindex_to_metadata, partition_cols=None):
    dprql__ymgk = {}
    dprql__ymgk['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, ollwe__cvw in zip(df.columns, df.data):
        if col_name in partition_cols:
            continue
        if isinstance(ollwe__cvw, types.Array) or ollwe__cvw == boolean_array:
            setu__imw = zyz__cbbc = ollwe__cvw.dtype.name
            if zyz__cbbc.startswith('datetime'):
                setu__imw = 'datetime'
        elif ollwe__cvw == string_array_type:
            setu__imw = 'unicode'
            zyz__cbbc = 'object'
        elif ollwe__cvw == binary_array_type:
            setu__imw = 'bytes'
            zyz__cbbc = 'object'
        elif isinstance(ollwe__cvw, DecimalArrayType):
            setu__imw = zyz__cbbc = 'object'
        elif isinstance(ollwe__cvw, IntegerArrayType):
            jqt__mmd = ollwe__cvw.dtype.name
            if jqt__mmd.startswith('int'):
                setu__imw = 'Int' + jqt__mmd[3:]
            elif jqt__mmd.startswith('uint'):
                setu__imw = 'UInt' + jqt__mmd[4:]
            else:
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, ollwe__cvw))
            zyz__cbbc = ollwe__cvw.dtype.name
        elif ollwe__cvw == datetime_date_array_type:
            setu__imw = 'datetime'
            zyz__cbbc = 'object'
        elif isinstance(ollwe__cvw, (StructArrayType, ArrayItemArrayType)):
            setu__imw = 'object'
            zyz__cbbc = 'object'
        else:
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, ollwe__cvw))
        nfwbz__xxy = {'name': col_name, 'field_name': col_name,
            'pandas_type': setu__imw, 'numpy_type': zyz__cbbc, 'metadata': None
            }
        dprql__ymgk['columns'].append(nfwbz__xxy)
    if write_non_range_index_to_metadata:
        if isinstance(df.index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in df.index.name:
            lgqvm__sijh = '__index_level_0__'
            nylu__qdmj = None
        else:
            lgqvm__sijh = '%s'
            nylu__qdmj = '%s'
        dprql__ymgk['index_columns'] = [lgqvm__sijh]
        dprql__ymgk['columns'].append({'name': nylu__qdmj, 'field_name':
            lgqvm__sijh, 'pandas_type': df.index.pandas_type_name,
            'numpy_type': df.index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        dprql__ymgk['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        dprql__ymgk['index_columns'] = []
    dprql__ymgk['pandas_version'] = pd.__version__
    return dprql__ymgk


@overload_method(DataFrameType, 'to_parquet', no_unliteral=True)
def to_parquet_overload(df, fname, engine='auto', compression='snappy',
    index=None, partition_cols=None, storage_options=None, _is_parallel=False):
    check_runtime_cols_unsupported(df, 'DataFrame.to_parquet()')
    check_unsupported_args('DataFrame.to_parquet', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if not is_overload_none(engine) and get_overload_const_str(engine) not in (
        'auto', 'pyarrow'):
        raise BodoError('DataFrame.to_parquet(): only pyarrow engine supported'
            )
    if not is_overload_none(compression) and get_overload_const_str(compression
        ) not in {'snappy', 'gzip', 'brotli'}:
        raise BodoError('to_parquet(): Unsupported compression: ' + str(
            get_overload_const_str(compression)))
    if not is_overload_none(partition_cols):
        partition_cols = get_overload_const_list(partition_cols)
        jeui__xwao = []
        for sadn__pplwf in partition_cols:
            try:
                idx = df.columns.index(sadn__pplwf)
            except ValueError as ewb__dav:
                raise BodoError(
                    f'Partition column {sadn__pplwf} is not in dataframe')
            jeui__xwao.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    jhjk__rlisb = isinstance(df.index, bodo.hiframes.pd_index_ext.
        RangeIndexType)
    seeas__mwx = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not jhjk__rlisb)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not jhjk__rlisb or
        is_overload_true(_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and jhjk__rlisb and not is_overload_true(_is_parallel)
    nus__wkm = json.dumps(gen_pandas_parquet_metadata(df,
        write_non_range_index_to_metadata, write_rangeindex_to_metadata,
        partition_cols=partition_cols))
    if not is_overload_true(_is_parallel) and jhjk__rlisb:
        nus__wkm = nus__wkm.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            nus__wkm = nus__wkm.replace('"%s"', '%s')
    nmf__mfigd = ', '.join(
        'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(len(df.columns)))
    sejm__wpgn = """def df_to_parquet(df, fname, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, _is_parallel=False):
"""
    if df.is_table_format:
        sejm__wpgn += (
            '    table = py_table_to_cpp_table(get_dataframe_table(df), py_table_typ)\n'
            )
    else:
        sejm__wpgn += '    info_list = [{}]\n'.format(nmf__mfigd)
        sejm__wpgn += '    table = arr_info_list_to_table(info_list)\n'
    sejm__wpgn += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and seeas__mwx:
        sejm__wpgn += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        yoi__aoodj = True
    else:
        sejm__wpgn += '    index_col = array_to_info(np.empty(0))\n'
        yoi__aoodj = False
    sejm__wpgn += '    metadata = """' + nus__wkm + '"""\n'
    sejm__wpgn += '    if compression is None:\n'
    sejm__wpgn += "        compression = 'none'\n"
    sejm__wpgn += '    if df.index.name is not None:\n'
    sejm__wpgn += '        name_ptr = df.index.name\n'
    sejm__wpgn += '    else:\n'
    sejm__wpgn += "        name_ptr = 'null'\n"
    sejm__wpgn += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel=_is_parallel)
"""
    vbvf__vzyxe = None
    if partition_cols:
        vbvf__vzyxe = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        yren__musw = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in jeui__xwao)
        if yren__musw:
            sejm__wpgn += '    cat_info_list = [{}]\n'.format(yren__musw)
            sejm__wpgn += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            sejm__wpgn += '    cat_table = table\n'
        sejm__wpgn += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        sejm__wpgn += (
            f'    part_cols_idxs = np.array({jeui__xwao}, dtype=np.int32)\n')
        sejm__wpgn += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(fname),\n'
            )
        sejm__wpgn += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        sejm__wpgn += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        sejm__wpgn += (
            '                            unicode_to_utf8(compression),\n')
        sejm__wpgn += '                            _is_parallel,\n'
        sejm__wpgn += (
            '                            unicode_to_utf8(bucket_region))\n')
        sejm__wpgn += '    delete_table_decref_arrays(table)\n'
        sejm__wpgn += '    delete_info_decref_array(index_col)\n'
        sejm__wpgn += '    delete_info_decref_array(col_names_no_partitions)\n'
        sejm__wpgn += '    delete_info_decref_array(col_names)\n'
        if yren__musw:
            sejm__wpgn += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        sejm__wpgn += '    parquet_write_table_cpp(unicode_to_utf8(fname),\n'
        sejm__wpgn += (
            '                            table, col_names, index_col,\n')
        sejm__wpgn += '                            ' + str(yoi__aoodj) + ',\n'
        sejm__wpgn += (
            '                            unicode_to_utf8(metadata),\n')
        sejm__wpgn += (
            '                            unicode_to_utf8(compression),\n')
        sejm__wpgn += (
            '                            _is_parallel, 1, df.index.start,\n')
        sejm__wpgn += (
            '                            df.index.stop, df.index.step,\n')
        sejm__wpgn += (
            '                            unicode_to_utf8(name_ptr),\n')
        sejm__wpgn += (
            '                            unicode_to_utf8(bucket_region))\n')
        sejm__wpgn += '    delete_table_decref_arrays(table)\n'
        sejm__wpgn += '    delete_info_decref_array(index_col)\n'
        sejm__wpgn += '    delete_info_decref_array(col_names)\n'
    else:
        sejm__wpgn += '    parquet_write_table_cpp(unicode_to_utf8(fname),\n'
        sejm__wpgn += (
            '                            table, col_names, index_col,\n')
        sejm__wpgn += '                            ' + str(yoi__aoodj) + ',\n'
        sejm__wpgn += (
            '                            unicode_to_utf8(metadata),\n')
        sejm__wpgn += (
            '                            unicode_to_utf8(compression),\n')
        sejm__wpgn += '                            _is_parallel, 0, 0, 0, 0,\n'
        sejm__wpgn += (
            '                            unicode_to_utf8(name_ptr),\n')
        sejm__wpgn += (
            '                            unicode_to_utf8(bucket_region))\n')
        sejm__wpgn += '    delete_table_decref_arrays(table)\n'
        sejm__wpgn += '    delete_info_decref_array(index_col)\n'
        sejm__wpgn += '    delete_info_decref_array(col_names)\n'
    pkqvu__xzphq = {}
    exec(sejm__wpgn, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': pd.array(df.columns),
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': vbvf__vzyxe}, pkqvu__xzphq)
    shd__mba = pkqvu__xzphq['df_to_parquet']
    return shd__mba


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None):
    henqf__lwxdx = 'all_ok'
    try:
        df.to_sql(name, con, schema, if_exists, index, index_label,
            chunksize, dtype, method)
    except ValueError as vhry__tqwf:
        henqf__lwxdx = vhry__tqwf.args[0]
    return henqf__lwxdx


@numba.njit
def to_sql_exception_guard_encaps(df, name, con, schema=None, if_exists=
    'fail', index=True, index_label=None, chunksize=None, dtype=None,
    method=None):
    with numba.objmode(out='unicode_type'):
        out = to_sql_exception_guard(df, name, con, schema, if_exists,
            index, index_label, chunksize, dtype, method)
    return out


@overload_method(DataFrameType, 'to_sql')
def to_sql_overload(df, name, con, schema=None, if_exists='fail', index=
    True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_parallel=False):
    check_runtime_cols_unsupported(df, 'DataFrame.to_sql()')
    sxz__gndyl = dict(chunksize=chunksize)
    pqrp__plmr = dict(chunksize=None)
    check_unsupported_args('to_sql', sxz__gndyl, pqrp__plmr, package_name=
        'pandas', module_name='IO')

    def _impl(df, name, con, schema=None, if_exists='fail', index=True,
        index_label=None, chunksize=None, dtype=None, method=None,
        _is_parallel=False):
        fakfo__sotq = bodo.libs.distributed_api.get_rank()
        henqf__lwxdx = 'unset'
        if fakfo__sotq != 0:
            if_exists = 'append'
            henqf__lwxdx = bcast_scalar(henqf__lwxdx)
        if fakfo__sotq == 0 or _is_parallel and henqf__lwxdx == 'all_ok':
            henqf__lwxdx = to_sql_exception_guard_encaps(df, name, con,
                schema, if_exists, index, index_label, chunksize, dtype, method
                )
        if fakfo__sotq == 0:
            henqf__lwxdx = bcast_scalar(henqf__lwxdx)
        if henqf__lwxdx != 'all_ok':
            print('err_msg=', henqf__lwxdx)
            raise ValueError('error in to_sql() operation')
    return _impl


@overload_method(DataFrameType, 'to_csv', no_unliteral=True)
def to_csv_overload(df, path_or_buf=None, sep=',', na_rep='', float_format=
    None, columns=None, header=True, index=True, index_label=None, mode='w',
    encoding=None, compression=None, quoting=None, quotechar='"',
    line_terminator=None, chunksize=None, date_format=None, doublequote=
    True, escapechar=None, decimal='.', errors='strict', storage_options=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_csv()')
    check_unsupported_args('DataFrame.to_csv', {'encoding': encoding,
        'mode': mode, 'errors': errors, 'storage_options': storage_options},
        {'encoding': None, 'mode': 'w', 'errors': 'strict',
        'storage_options': None}, package_name='pandas', module_name='IO')
    if not (is_overload_none(path_or_buf) or is_overload_constant_str(
        path_or_buf) or path_or_buf == string_type):
        raise BodoError(
            "DataFrame.to_csv(): 'path_or_buf' argument should be None or string"
            )
    if not is_overload_none(compression):
        raise BodoError(
            "DataFrame.to_csv(): 'compression' argument supports only None, which is the default in JIT code."
            )
    if is_overload_constant_str(path_or_buf):
        hmin__hmby = get_overload_const_str(path_or_buf)
        if hmin__hmby.endswith(('.gz', '.bz2', '.zip', '.xz')):
            import warnings
            from bodo.utils.typing import BodoWarning
            warnings.warn(BodoWarning(
                "DataFrame.to_csv(): 'compression' argument defaults to None in JIT code, which is the only supported value."
                ))
    if isinstance(columns, types.List):
        raise BodoError(
            "DataFrame.to_csv(): 'columns' argument must not be list type. Please convert to tuple type."
            )
    if is_overload_none(path_or_buf):

        def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=
            None, columns=None, header=True, index=True, index_label=None,
            mode='w', encoding=None, compression=None, quoting=None,
            quotechar='"', line_terminator=None, chunksize=None,
            date_format=None, doublequote=True, escapechar=None, decimal=
            '.', errors='strict', storage_options=None):
            with numba.objmode(D='unicode_type'):
                D = df.to_csv(path_or_buf, sep, na_rep, float_format,
                    columns, header, index, index_label, mode, encoding,
                    compression, quoting, quotechar, line_terminator,
                    chunksize, date_format, doublequote, escapechar,
                    decimal, errors, storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=None,
        columns=None, header=True, index=True, index_label=None, mode='w',
        encoding=None, compression=None, quoting=None, quotechar='"',
        line_terminator=None, chunksize=None, date_format=None, doublequote
        =True, escapechar=None, decimal='.', errors='strict',
        storage_options=None):
        with numba.objmode(D='unicode_type'):
            D = df.to_csv(None, sep, na_rep, float_format, columns, header,
                index, index_label, mode, encoding, compression, quoting,
                quotechar, line_terminator, chunksize, date_format,
                doublequote, escapechar, decimal, errors, storage_options)
        bodo.io.fs_io.csv_write(path_or_buf, D)
    return _impl


@overload_method(DataFrameType, 'to_json', no_unliteral=True)
def to_json_overload(df, path_or_buf=None, orient='columns', date_format=
    None, double_precision=10, force_ascii=True, date_unit='ms',
    default_handler=None, lines=False, compression='infer', index=True,
    indent=None, storage_options=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_json()')
    check_unsupported_args('DataFrame.to_json', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if path_or_buf is None or path_or_buf == types.none:

        def _impl(df, path_or_buf=None, orient='columns', date_format=None,
            double_precision=10, force_ascii=True, date_unit='ms',
            default_handler=None, lines=False, compression='infer', index=
            True, indent=None, storage_options=None):
            with numba.objmode(D='unicode_type'):
                D = df.to_json(path_or_buf, orient, date_format,
                    double_precision, force_ascii, date_unit,
                    default_handler, lines, compression, index, indent,
                    storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, orient='columns', date_format=None,
        double_precision=10, force_ascii=True, date_unit='ms',
        default_handler=None, lines=False, compression='infer', index=True,
        indent=None, storage_options=None):
        with numba.objmode(D='unicode_type'):
            D = df.to_json(None, orient, date_format, double_precision,
                force_ascii, date_unit, default_handler, lines, compression,
                index, indent, storage_options)
        qaxu__kdxrd = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(qaxu__kdxrd))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(qaxu__kdxrd))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    ztj__nky = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    jup__vubn = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', ztj__nky, jup__vubn,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    sejm__wpgn = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        xddjm__fhi = data.data.dtype.categories
        sejm__wpgn += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        xddjm__fhi = data.dtype.categories
        sejm__wpgn += '  data_values = data\n'
    icj__nsb = len(xddjm__fhi)
    sejm__wpgn += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    sejm__wpgn += '  numba.parfors.parfor.init_prange()\n'
    sejm__wpgn += '  n = len(data_values)\n'
    for i in range(icj__nsb):
        sejm__wpgn += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    sejm__wpgn += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    sejm__wpgn += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for lgnr__mxfp in range(icj__nsb):
        sejm__wpgn += '          data_arr_{}[i] = 0\n'.format(lgnr__mxfp)
    sejm__wpgn += '      else:\n'
    for dcdm__qleq in range(icj__nsb):
        sejm__wpgn += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            dcdm__qleq)
    nmf__mfigd = ', '.join(f'data_arr_{i}' for i in range(icj__nsb))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(xddjm__fhi[0], np.datetime64):
        xddjm__fhi = tuple(pd.Timestamp(iebsy__zzv) for iebsy__zzv in
            xddjm__fhi)
    return bodo.hiframes.dataframe_impl._gen_init_df(sejm__wpgn, xddjm__fhi,
        nmf__mfigd, index)


def categorical_can_construct_dataframe(val):
    if isinstance(val, CategoricalArrayType):
        return val.dtype.categories is not None
    elif isinstance(val, SeriesType) and isinstance(val.data,
        CategoricalArrayType):
        return val.data.dtype.categories is not None
    return False


def handle_inplace_df_type_change(inplace, _bodo_transformed, func_name):
    if is_overload_false(_bodo_transformed
        ) and bodo.transforms.typing_pass.in_partial_typing and (
        is_overload_true(inplace) or not is_overload_constant_bool(inplace)):
        bodo.transforms.typing_pass.typing_transform_required = True
        raise Exception('DataFrame.{}(): transform necessary for inplace'.
            format(func_name))


pd_unsupported = (pd.read_pickle, pd.read_table, pd.read_fwf, pd.
    read_clipboard, pd.ExcelFile, pd.read_html, pd.read_xml, pd.read_hdf,
    pd.read_feather, pd.read_orc, pd.read_sas, pd.read_spss, pd.
    read_sql_table, pd.read_sql_query, pd.read_gbq, pd.read_stata, pd.
    ExcelWriter, pd.json_normalize, pd.melt, pd.pivot, pd.pivot_table, pd.
    merge_ordered, pd.factorize, pd.unique, pd.wide_to_long, pd.bdate_range,
    pd.period_range, pd.infer_freq, pd.interval_range, pd.eval, pd.test, pd
    .Grouper)
pd_util_unsupported = pd.util.hash_array, pd.util.hash_pandas_object
dataframe_unsupported = ['set_flags', 'convert_dtypes', 'bool', '__iter__',
    'items', 'iteritems', 'keys', 'iterrows', 'lookup', 'pop', 'xs', 'get',
    'where', 'mask', 'add', 'sub', 'mul', 'div', 'truediv', 'floordiv',
    'mod', 'pow', 'dot', 'radd', 'rsub', 'rmul', 'rdiv', 'rtruediv',
    'rfloordiv', 'rmod', 'rpow', 'lt', 'gt', 'le', 'ge', 'ne', 'eq',
    'combine', 'combine_first', 'subtract', 'divide', 'multiply',
    'applymap', 'agg', 'aggregate', 'transform', 'expanding', 'ewm', 'all',
    'any', 'clip', 'corrwith', 'cummax', 'cummin', 'eval', 'kurt',
    'kurtosis', 'mad', 'mode', 'rank', 'round', 'sem', 'skew',
    'value_counts', 'add_prefix', 'add_suffix', 'align', 'at_time',
    'between_time', 'equals', 'reindex', 'reindex_like', 'rename_axis',
    'set_axis', 'truncate', 'backfill', 'bfill', 'ffill', 'interpolate',
    'pad', 'droplevel', 'reorder_levels', 'nlargest', 'nsmallest',
    'swaplevel', 'stack', 'unstack', 'swapaxes', 'melt', 'explode',
    'squeeze', 'to_xarray', 'T', 'transpose', 'compare', 'update', 'asfreq',
    'asof', 'slice_shift', 'tshift', 'first_valid_index',
    'last_valid_index', 'resample', 'to_period', 'to_timestamp',
    'tz_convert', 'tz_localize', 'boxplot', 'hist', 'from_dict',
    'from_records', 'to_pickle', 'to_hdf', 'to_dict', 'to_excel', 'to_html',
    'to_feather', 'to_latex', 'to_stata', 'to_gbq', 'to_records',
    'to_clipboard', 'to_markdown', 'to_xml']
dataframe_unsupported_attrs = ['at', 'attrs', 'axes', 'flags', 'style',
    'sparse']


def _install_pd_unsupported(mod_name, pd_unsupported):
    for eylea__gohik in pd_unsupported:
        fname = mod_name + '.' + eylea__gohik.__name__
        overload(eylea__gohik, no_unliteral=True)(create_unsupported_overload
            (fname))


def _install_dataframe_unsupported():
    for otbv__igeut in dataframe_unsupported_attrs:
        hxj__pjic = 'DataFrame.' + otbv__igeut
        overload_attribute(DataFrameType, otbv__igeut)(
            create_unsupported_overload(hxj__pjic))
    for fname in dataframe_unsupported:
        hxj__pjic = 'DataFrame.' + fname + '()'
        overload_method(DataFrameType, fname)(create_unsupported_overload(
            hxj__pjic))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
