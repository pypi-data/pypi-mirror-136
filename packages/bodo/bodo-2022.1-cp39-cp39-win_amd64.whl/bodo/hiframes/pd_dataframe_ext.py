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
            bip__xmcw = f'{len(self.data)} columns of types {set(self.data)}'
            ymna__igtt = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({bip__xmcw}, {self.index}, {ymna__igtt}, {self.dist}, {self.is_table_format})'
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
            btnpl__lih = (self.index if self.index == other.index else self
                .index.unify(typingctx, other.index))
            data = tuple(puq__ectdr.unify(typingctx, vfbhn__jzw) if 
                puq__ectdr != vfbhn__jzw else puq__ectdr for puq__ectdr,
                vfbhn__jzw in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if btnpl__lih is not None and None not in data:
                return DataFrameType(data, btnpl__lih, self.columns, dist,
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
        return all(puq__ectdr.is_precise() for puq__ectdr in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        pyuc__ypae = self.columns.index(col_name)
        rrcpk__yngjw = tuple(list(self.data[:pyuc__ypae]) + [new_type] +
            list(self.data[pyuc__ypae + 1:]))
        return DataFrameType(rrcpk__yngjw, self.index, self.columns, self.
            dist, self.is_table_format)


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
        ajw__qvip = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            ajw__qvip.append(('columns', fe_type.df_type.runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, ajw__qvip)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        ajw__qvip = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, ajw__qvip)


make_attribute_wrapper(DataFrameType, 'meminfo', '_meminfo')


@infer_getattr
class DataFrameAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameType

    @bound_function('df.head')
    def resolve_head(self, df, args, kws):
        func_name = 'DataFrame.head'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        xxhz__yze = 'n',
        yib__gqt = {'n': 5}
        nlm__oiy, exd__cik = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, xxhz__yze, yib__gqt)
        dwng__uvkw = exd__cik[0]
        if not is_overload_int(dwng__uvkw):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        esj__ngws = df.copy(is_table_format=False)
        return esj__ngws(*exd__cik).replace(pysig=nlm__oiy)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        beu__jnet = (df,) + args
        xxhz__yze = 'df', 'method', 'min_periods'
        yib__gqt = {'method': 'pearson', 'min_periods': 1}
        ljcl__dmh = 'method',
        nlm__oiy, exd__cik = bodo.utils.typing.fold_typing_args(func_name,
            beu__jnet, kws, xxhz__yze, yib__gqt, ljcl__dmh)
        drm__johf = exd__cik[2]
        if not is_overload_int(drm__johf):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        ltbl__oph = []
        lxd__bom = []
        for vujd__mxom, aeisk__caa in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(aeisk__caa.dtype):
                ltbl__oph.append(vujd__mxom)
                lxd__bom.append(types.Array(types.float64, 1, 'A'))
        if len(ltbl__oph) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        lxd__bom = tuple(lxd__bom)
        ltbl__oph = tuple(ltbl__oph)
        index_typ = bodo.utils.typing.type_col_to_index(ltbl__oph)
        esj__ngws = DataFrameType(lxd__bom, index_typ, ltbl__oph)
        return esj__ngws(*exd__cik).replace(pysig=nlm__oiy)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        zmpfa__loma = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        dzq__hmkxy = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        hoz__trpb = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        csq__ozjpb = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        wsni__ehiq = dict(raw=dzq__hmkxy, result_type=hoz__trpb)
        jnqx__nquog = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', wsni__ehiq, jnqx__nquog,
            package_name='pandas', module_name='DataFrame')
        rtql__kri = True
        if types.unliteral(zmpfa__loma) == types.unicode_type:
            if not is_overload_constant_str(zmpfa__loma):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            rtql__kri = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        iatfc__dtwtl = get_overload_const_int(axis)
        if rtql__kri and iatfc__dtwtl != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif iatfc__dtwtl not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        mzzx__dbpvk = []
        for arr_typ in df.data:
            xiza__kogu = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            hyg__hxa = self.context.resolve_function_type(operator.getitem,
                (SeriesIlocType(xiza__kogu), types.int64), {}).return_type
            mzzx__dbpvk.append(hyg__hxa)
        gus__vlww = types.none
        vjod__amhnf = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(vujd__mxom) for vujd__mxom in df.columns)),
            None)
        maewa__twdrl = types.BaseTuple.from_types(mzzx__dbpvk)
        ciqnk__cyzhu = df.index.dtype
        if ciqnk__cyzhu == types.NPDatetime('ns'):
            ciqnk__cyzhu = bodo.pd_timestamp_type
        if ciqnk__cyzhu == types.NPTimedelta('ns'):
            ciqnk__cyzhu = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(maewa__twdrl):
            uesn__mdxmb = HeterogeneousSeriesType(maewa__twdrl, vjod__amhnf,
                ciqnk__cyzhu)
        else:
            uesn__mdxmb = SeriesType(maewa__twdrl.dtype, maewa__twdrl,
                vjod__amhnf, ciqnk__cyzhu)
        zwhlm__xeh = uesn__mdxmb,
        if csq__ozjpb is not None:
            zwhlm__xeh += tuple(csq__ozjpb.types)
        try:
            if not rtql__kri:
                hxl__ttxy = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(zmpfa__loma), self.context,
                    'DataFrame.apply', axis if iatfc__dtwtl == 1 else None)
            else:
                hxl__ttxy = get_const_func_output_type(zmpfa__loma,
                    zwhlm__xeh, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as jms__tul:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()', jms__tul))
        if rtql__kri:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(hxl__ttxy, (SeriesType, HeterogeneousSeriesType)
                ) and hxl__ttxy.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(hxl__ttxy, HeterogeneousSeriesType):
                kqfl__hymrt, jehy__fifyc = hxl__ttxy.const_info
                pklsc__lynhm = tuple(dtype_to_array_type(cgu__ujx) for
                    cgu__ujx in hxl__ttxy.data.types)
                luox__fvme = DataFrameType(pklsc__lynhm, df.index, jehy__fifyc)
            elif isinstance(hxl__ttxy, SeriesType):
                fes__ocpfh, jehy__fifyc = hxl__ttxy.const_info
                pklsc__lynhm = tuple(dtype_to_array_type(hxl__ttxy.dtype) for
                    kqfl__hymrt in range(fes__ocpfh))
                luox__fvme = DataFrameType(pklsc__lynhm, df.index, jehy__fifyc)
            else:
                ljbu__mvh = get_udf_out_arr_type(hxl__ttxy)
                luox__fvme = SeriesType(ljbu__mvh.dtype, ljbu__mvh, df.
                    index, None)
        else:
            luox__fvme = hxl__ttxy
        gda__yexif = ', '.join("{} = ''".format(puq__ectdr) for puq__ectdr in
            kws.keys())
        wul__bkv = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {gda__yexif}):
"""
        wul__bkv += '    pass\n'
        afrpl__trtj = {}
        exec(wul__bkv, {}, afrpl__trtj)
        ucai__fzpnx = afrpl__trtj['apply_stub']
        nlm__oiy = numba.core.utils.pysignature(ucai__fzpnx)
        rhsav__rnj = (zmpfa__loma, axis, dzq__hmkxy, hoz__trpb, csq__ozjpb
            ) + tuple(kws.values())
        return signature(luox__fvme, *rhsav__rnj).replace(pysig=nlm__oiy)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        xxhz__yze = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        yib__gqt = {'x': None, 'y': None, 'kind': 'line', 'figsize': None,
            'ax': None, 'subplots': False, 'sharex': None, 'sharey': False,
            'layout': None, 'use_index': True, 'title': None, 'grid': None,
            'legend': True, 'style': None, 'logx': False, 'logy': False,
            'loglog': False, 'xticks': None, 'yticks': None, 'xlim': None,
            'ylim': None, 'rot': None, 'fontsize': None, 'colormap': None,
            'table': False, 'yerr': None, 'xerr': None, 'secondary_y': 
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        ljcl__dmh = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        nlm__oiy, exd__cik = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, xxhz__yze, yib__gqt, ljcl__dmh)
        clml__ygkwk = exd__cik[2]
        if not is_overload_constant_str(clml__ygkwk):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        nqqcb__npxzc = exd__cik[0]
        if not is_overload_none(nqqcb__npxzc) and not (is_overload_int(
            nqqcb__npxzc) or is_overload_constant_str(nqqcb__npxzc)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(nqqcb__npxzc):
            ehjdz__laqw = get_overload_const_str(nqqcb__npxzc)
            if ehjdz__laqw not in df.columns:
                raise BodoError(f'{func_name}: {ehjdz__laqw} column not found.'
                    )
        elif is_overload_int(nqqcb__npxzc):
            vssm__nscb = get_overload_const_int(nqqcb__npxzc)
            if vssm__nscb > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {vssm__nscb} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            nqqcb__npxzc = df.columns[nqqcb__npxzc]
        qio__umxzw = exd__cik[1]
        if not is_overload_none(qio__umxzw) and not (is_overload_int(
            qio__umxzw) or is_overload_constant_str(qio__umxzw)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(qio__umxzw):
            pobf__vswo = get_overload_const_str(qio__umxzw)
            if pobf__vswo not in df.columns:
                raise BodoError(f'{func_name}: {pobf__vswo} column not found.')
        elif is_overload_int(qio__umxzw):
            zmpvg__gci = get_overload_const_int(qio__umxzw)
            if zmpvg__gci > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {zmpvg__gci} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            qio__umxzw = df.columns[qio__umxzw]
        bwy__lcgw = exd__cik[3]
        if not is_overload_none(bwy__lcgw) and not is_tuple_like_type(bwy__lcgw
            ):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        qzqgu__hlbqv = exd__cik[10]
        if not is_overload_none(qzqgu__hlbqv) and not is_overload_constant_str(
            qzqgu__hlbqv):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        pgtqr__vcq = exd__cik[12]
        if not is_overload_bool(pgtqr__vcq):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        ohksl__vawj = exd__cik[17]
        if not is_overload_none(ohksl__vawj) and not is_tuple_like_type(
            ohksl__vawj):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        vgai__zkem = exd__cik[18]
        if not is_overload_none(vgai__zkem) and not is_tuple_like_type(
            vgai__zkem):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        hbiz__gngj = exd__cik[22]
        if not is_overload_none(hbiz__gngj) and not is_overload_int(hbiz__gngj
            ):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        zyr__cmai = exd__cik[29]
        if not is_overload_none(zyr__cmai) and not is_overload_constant_str(
            zyr__cmai):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        flh__umg = exd__cik[30]
        if not is_overload_none(flh__umg) and not is_overload_constant_str(
            flh__umg):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        raa__hvw = types.List(types.mpl_line_2d_type)
        clml__ygkwk = get_overload_const_str(clml__ygkwk)
        if clml__ygkwk == 'scatter':
            if is_overload_none(nqqcb__npxzc) and is_overload_none(qio__umxzw):
                raise BodoError(
                    f'{func_name}: {clml__ygkwk} requires an x and y column.')
            elif is_overload_none(nqqcb__npxzc):
                raise BodoError(
                    f'{func_name}: {clml__ygkwk} x column is missing.')
            elif is_overload_none(qio__umxzw):
                raise BodoError(
                    f'{func_name}: {clml__ygkwk} y column is missing.')
            raa__hvw = types.mpl_path_collection_type
        elif clml__ygkwk != 'line':
            raise BodoError(
                f'{func_name}: {clml__ygkwk} plot is not supported.')
        return signature(raa__hvw, *exd__cik).replace(pysig=nlm__oiy)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            bqvi__coj = df.columns.index(attr)
            arr_typ = df.data[bqvi__coj]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            ddhe__djbt = []
            rrcpk__yngjw = []
            htsva__ljlz = False
            for i, hhg__ortq in enumerate(df.columns):
                if hhg__ortq[0] != attr:
                    continue
                htsva__ljlz = True
                ddhe__djbt.append(hhg__ortq[1] if len(hhg__ortq) == 2 else
                    hhg__ortq[1:])
                rrcpk__yngjw.append(df.data[i])
            if htsva__ljlz:
                return DataFrameType(tuple(rrcpk__yngjw), df.index, tuple(
                    ddhe__djbt))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        tzvmo__dst = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(tzvmo__dst)
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
        ckjj__iau = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], ckjj__iau)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    dcczd__rnebb = builder.module
    oqs__kefhw = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    nxfnq__grj = cgutils.get_or_insert_function(dcczd__rnebb, oqs__kefhw,
        name='.dtor.df.{}'.format(df_type))
    if not nxfnq__grj.is_declaration:
        return nxfnq__grj
    nxfnq__grj.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(nxfnq__grj.append_basic_block())
    rlbn__tac = nxfnq__grj.args[0]
    qlc__miu = context.get_value_type(payload_type).as_pointer()
    sdry__udr = builder.bitcast(rlbn__tac, qlc__miu)
    payload = context.make_helper(builder, payload_type, ref=sdry__udr)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        msj__ljcl = context.get_python_api(builder)
        dynlr__dxehz = msj__ljcl.gil_ensure()
        msj__ljcl.decref(payload.parent)
        msj__ljcl.gil_release(dynlr__dxehz)
    builder.ret_void()
    return nxfnq__grj


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    istx__lhgo = cgutils.create_struct_proxy(payload_type)(context, builder)
    istx__lhgo.data = data_tup
    istx__lhgo.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        istx__lhgo.columns = colnames
    zxag__tll = context.get_value_type(payload_type)
    bfgqa__oagkh = context.get_abi_sizeof(zxag__tll)
    flc__vycbi = define_df_dtor(context, builder, df_type, payload_type)
    xdyx__oieeb = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, bfgqa__oagkh), flc__vycbi)
    jwqut__nco = context.nrt.meminfo_data(builder, xdyx__oieeb)
    aelgd__qlbo = builder.bitcast(jwqut__nco, zxag__tll.as_pointer())
    ulye__kgvj = cgutils.create_struct_proxy(df_type)(context, builder)
    ulye__kgvj.meminfo = xdyx__oieeb
    if parent is None:
        ulye__kgvj.parent = cgutils.get_null_value(ulye__kgvj.parent.type)
    else:
        ulye__kgvj.parent = parent
        istx__lhgo.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            msj__ljcl = context.get_python_api(builder)
            dynlr__dxehz = msj__ljcl.gil_ensure()
            msj__ljcl.incref(parent)
            msj__ljcl.gil_release(dynlr__dxehz)
    builder.store(istx__lhgo._getvalue(), aelgd__qlbo)
    return ulye__kgvj._getvalue()


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
        fdvv__qayt = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype.
            arr_types)
    else:
        fdvv__qayt = [cgu__ujx for cgu__ujx in data_typ.dtype.arr_types]
    yfi__vvya = DataFrameType(tuple(fdvv__qayt + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        qjc__rsr = construct_dataframe(context, builder, df_type, data_tup,
            index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return qjc__rsr
    sig = signature(yfi__vvya, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ=None):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    fes__ocpfh = len(data_tup_typ.types)
    if fes__ocpfh == 0:
        wuk__cirm = ()
    elif isinstance(col_names_typ, types.TypeRef):
        wuk__cirm = col_names_typ.instance_type.columns
    else:
        wuk__cirm = get_const_tup_vals(col_names_typ)
    if fes__ocpfh == 1 and isinstance(data_tup_typ.types[0], TableType):
        fes__ocpfh = len(data_tup_typ.types[0].arr_types)
    assert len(wuk__cirm
        ) == fes__ocpfh, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    utbs__kgih = data_tup_typ.types
    if fes__ocpfh != 0 and isinstance(data_tup_typ.types[0], TableType):
        utbs__kgih = data_tup_typ.types[0].arr_types
        is_table_format = True
    yfi__vvya = DataFrameType(utbs__kgih, index_typ, wuk__cirm,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            tbo__qfjb = cgutils.create_struct_proxy(yfi__vvya.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = tbo__qfjb.parent
        qjc__rsr = construct_dataframe(context, builder, df_type, data_tup,
            index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return qjc__rsr
    sig = signature(yfi__vvya, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        ulye__kgvj = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, ulye__kgvj.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        istx__lhgo = get_dataframe_payload(context, builder, df_typ, args[0])
        krflw__qvd = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[krflw__qvd]
        if df_typ.is_table_format:
            tbo__qfjb = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(istx__lhgo.data, 0))
            uat__ekwle = df_typ.table_type.type_to_blk[arr_typ]
            xzs__kzd = getattr(tbo__qfjb, f'block_{uat__ekwle}')
            sfdyp__qma = ListInstance(context, builder, types.List(arr_typ),
                xzs__kzd)
            ula__fxup = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[krflw__qvd])
            ckjj__iau = sfdyp__qma.getitem(ula__fxup)
        else:
            ckjj__iau = builder.extract_value(istx__lhgo.data, krflw__qvd)
        xkymt__xqo = cgutils.alloca_once_value(builder, ckjj__iau)
        sfmwo__omm = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, xkymt__xqo, sfmwo__omm)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    xdyx__oieeb = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, xdyx__oieeb)
    qlc__miu = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, qlc__miu)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    yfi__vvya = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        yfi__vvya = types.Tuple([TableType(df_typ.data)])
    sig = signature(yfi__vvya, df_typ)

    def codegen(context, builder, signature, args):
        istx__lhgo = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            istx__lhgo.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, 'get_dataframe_index')

    def codegen(context, builder, signature, args):
        istx__lhgo = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, istx__lhgo
            .index)
    yfi__vvya = df_typ.index
    sig = signature(yfi__vvya, df_typ)
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
        esj__ngws = df.data[i]
        return esj__ngws(*args)


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
        istx__lhgo = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(istx__lhgo.data, 0))
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
    maewa__twdrl = self.typemap[data_tup.name]
    if any(is_tuple_like_type(cgu__ujx) for cgu__ujx in maewa__twdrl.types):
        return None
    if equiv_set.has_shape(data_tup):
        wfyxl__wge = equiv_set.get_shape(data_tup)
        if len(wfyxl__wge) > 1:
            equiv_set.insert_equiv(*wfyxl__wge)
        if len(wfyxl__wge) > 0:
            vjod__amhnf = self.typemap[index.name]
            if not isinstance(vjod__amhnf, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(wfyxl__wge[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(wfyxl__wge[0], len(
                wfyxl__wge)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    lrnci__zymll = args[0]
    hooqn__nqr = self.typemap[lrnci__zymll.name].data
    if any(is_tuple_like_type(cgu__ujx) for cgu__ujx in hooqn__nqr):
        return None
    if equiv_set.has_shape(lrnci__zymll):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            lrnci__zymll)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    lrnci__zymll = args[0]
    vjod__amhnf = self.typemap[lrnci__zymll.name].index
    if isinstance(vjod__amhnf, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(lrnci__zymll):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            lrnci__zymll)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    lrnci__zymll = args[0]
    if equiv_set.has_shape(lrnci__zymll):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            lrnci__zymll), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    krflw__qvd = get_overload_const_int(c_ind_typ)
    if df_typ.data[krflw__qvd] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        douv__tbjp, kqfl__hymrt, vcx__dlld = args
        istx__lhgo = get_dataframe_payload(context, builder, df_typ, douv__tbjp
            )
        if df_typ.is_table_format:
            tbo__qfjb = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(istx__lhgo.data, 0))
            uat__ekwle = df_typ.table_type.type_to_blk[arr_typ]
            xzs__kzd = getattr(tbo__qfjb, f'block_{uat__ekwle}')
            sfdyp__qma = ListInstance(context, builder, types.List(arr_typ),
                xzs__kzd)
            ula__fxup = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[krflw__qvd])
            sfdyp__qma.setitem(ula__fxup, vcx__dlld, True)
        else:
            ckjj__iau = builder.extract_value(istx__lhgo.data, krflw__qvd)
            context.nrt.decref(builder, df_typ.data[krflw__qvd], ckjj__iau)
            istx__lhgo.data = builder.insert_value(istx__lhgo.data,
                vcx__dlld, krflw__qvd)
            context.nrt.incref(builder, arr_typ, vcx__dlld)
        ulye__kgvj = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=douv__tbjp)
        payload_type = DataFramePayloadType(df_typ)
        sdry__udr = context.nrt.meminfo_data(builder, ulye__kgvj.meminfo)
        qlc__miu = context.get_value_type(payload_type).as_pointer()
        sdry__udr = builder.bitcast(sdry__udr, qlc__miu)
        builder.store(istx__lhgo._getvalue(), sdry__udr)
        return impl_ret_borrowed(context, builder, df_typ, douv__tbjp)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        phcp__bxst = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        tqtjg__oyklo = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=phcp__bxst)
        mzby__uvkd = get_dataframe_payload(context, builder, df_typ, phcp__bxst
            )
        ulye__kgvj = construct_dataframe(context, builder, signature.
            return_type, mzby__uvkd.data, index_val, tqtjg__oyklo.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), mzby__uvkd.data)
        return ulye__kgvj
    yfi__vvya = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(yfi__vvya, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    fes__ocpfh = len(df_type.columns)
    bbe__toj = fes__ocpfh
    mcwdn__zvlgb = df_type.data
    wuk__cirm = df_type.columns
    index_typ = df_type.index
    amq__sgb = col_name not in df_type.columns
    krflw__qvd = fes__ocpfh
    if amq__sgb:
        mcwdn__zvlgb += arr_type,
        wuk__cirm += col_name,
        bbe__toj += 1
    else:
        krflw__qvd = df_type.columns.index(col_name)
        mcwdn__zvlgb = tuple(arr_type if i == krflw__qvd else mcwdn__zvlgb[
            i] for i in range(fes__ocpfh))

    def codegen(context, builder, signature, args):
        douv__tbjp, kqfl__hymrt, vcx__dlld = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, douv__tbjp)
        qcoqg__rat = cgutils.create_struct_proxy(df_type)(context, builder,
            value=douv__tbjp)
        if df_type.is_table_format:
            mfm__ujdca = df_type.table_type
            eyiyx__frcy = builder.extract_value(in_dataframe_payload.data, 0)
            bwtw__frtv = TableType(mcwdn__zvlgb)
            ixxep__gphsc = set_table_data_codegen(context, builder,
                mfm__ujdca, eyiyx__frcy, bwtw__frtv, arr_type, vcx__dlld,
                krflw__qvd, amq__sgb)
            data_tup = context.make_tuple(builder, types.Tuple([bwtw__frtv]
                ), [ixxep__gphsc])
        else:
            utbs__kgih = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != krflw__qvd else vcx__dlld) for i in range(
                fes__ocpfh)]
            if amq__sgb:
                utbs__kgih.append(vcx__dlld)
            for lrnci__zymll, tazid__enlam in zip(utbs__kgih, mcwdn__zvlgb):
                context.nrt.incref(builder, tazid__enlam, lrnci__zymll)
            data_tup = context.make_tuple(builder, types.Tuple(mcwdn__zvlgb
                ), utbs__kgih)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        dvq__mzwqm = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, qcoqg__rat.parent, None)
        if not amq__sgb and arr_type == df_type.data[krflw__qvd]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            sdry__udr = context.nrt.meminfo_data(builder, qcoqg__rat.meminfo)
            qlc__miu = context.get_value_type(payload_type).as_pointer()
            sdry__udr = builder.bitcast(sdry__udr, qlc__miu)
            welzi__lhr = get_dataframe_payload(context, builder, df_type,
                dvq__mzwqm)
            builder.store(welzi__lhr._getvalue(), sdry__udr)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, bwtw__frtv, builder.
                    extract_value(data_tup, 0))
            else:
                for lrnci__zymll, tazid__enlam in zip(utbs__kgih, mcwdn__zvlgb
                    ):
                    context.nrt.incref(builder, tazid__enlam, lrnci__zymll)
        has_parent = cgutils.is_not_null(builder, qcoqg__rat.parent)
        with builder.if_then(has_parent):
            msj__ljcl = context.get_python_api(builder)
            dynlr__dxehz = msj__ljcl.gil_ensure()
            xumx__wcwu = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, vcx__dlld)
            vujd__mxom = numba.core.pythonapi._BoxContext(context, builder,
                msj__ljcl, xumx__wcwu)
            cwfd__gdk = vujd__mxom.pyapi.from_native_value(arr_type,
                vcx__dlld, vujd__mxom.env_manager)
            if isinstance(col_name, str):
                xsgt__ubg = context.insert_const_string(builder.module,
                    col_name)
                vmpp__ubpp = msj__ljcl.string_from_string(xsgt__ubg)
            else:
                assert isinstance(col_name, int)
                vmpp__ubpp = msj__ljcl.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            msj__ljcl.object_setitem(qcoqg__rat.parent, vmpp__ubpp, cwfd__gdk)
            msj__ljcl.decref(cwfd__gdk)
            msj__ljcl.decref(vmpp__ubpp)
            msj__ljcl.gil_release(dynlr__dxehz)
        return dvq__mzwqm
    yfi__vvya = DataFrameType(mcwdn__zvlgb, index_typ, wuk__cirm, df_type.
        dist, df_type.is_table_format)
    sig = signature(yfi__vvya, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    fes__ocpfh = len(pyval.columns)
    utbs__kgih = tuple(pyval.iloc[:, i].values for i in range(fes__ocpfh))
    if df_type.is_table_format:
        tbo__qfjb = context.get_constant_generic(builder, df_type.
            table_type, Table(utbs__kgih))
        data_tup = lir.Constant.literal_struct([tbo__qfjb])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], hhg__ortq) for i,
            hhg__ortq in enumerate(utbs__kgih)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    vbp__nyd = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, vbp__nyd])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    wdvgg__lffu = context.get_constant(types.int64, -1)
    qxdbh__ddn = context.get_constant_null(types.voidptr)
    xdyx__oieeb = lir.Constant.literal_struct([wdvgg__lffu, qxdbh__ddn,
        qxdbh__ddn, payload, wdvgg__lffu])
    xdyx__oieeb = cgutils.global_constant(builder, '.const.meminfo',
        xdyx__oieeb).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([xdyx__oieeb, vbp__nyd])


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
        btnpl__lih = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        btnpl__lih = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, btnpl__lih)
    if fromty.is_table_format == toty.is_table_format:
        rrcpk__yngjw = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                rrcpk__yngjw)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), rrcpk__yngjw)
    elif toty.is_table_format:
        rrcpk__yngjw = _cast_df_data_to_table_format(context, builder,
            fromty, toty, in_dataframe_payload)
    else:
        rrcpk__yngjw = _cast_df_data_to_tuple_format(context, builder,
            fromty, toty, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, rrcpk__yngjw,
        btnpl__lih, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    fzszu__fho = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        slkw__ilp = get_index_data_arr_types(toty.index)[0]
        nke__tctu = bodo.utils.transform.get_type_alloc_counts(slkw__ilp) - 1
        yvx__ybo = ', '.join('0' for kqfl__hymrt in range(nke__tctu))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(yvx__ybo, ', ' if nke__tctu == 1 else ''))
        fzszu__fho['index_arr_type'] = slkw__ilp
    hersc__xqq = []
    for i, arr_typ in enumerate(toty.data):
        nke__tctu = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        yvx__ybo = ', '.join('0' for kqfl__hymrt in range(nke__tctu))
        enjhl__farzm = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'
            .format(i, yvx__ybo, ', ' if nke__tctu == 1 else ''))
        hersc__xqq.append(enjhl__farzm)
        fzszu__fho[f'arr_type{i}'] = arr_typ
    hersc__xqq = ', '.join(hersc__xqq)
    wul__bkv = 'def impl():\n'
    sfbxg__jbv = bodo.hiframes.dataframe_impl._gen_init_df(wul__bkv, toty.
        columns, hersc__xqq, index, fzszu__fho)
    df = context.compile_internal(builder, sfbxg__jbv, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    hri__cxqpm = toty.table_type
    tbo__qfjb = cgutils.create_struct_proxy(hri__cxqpm)(context, builder)
    tbo__qfjb.parent = in_dataframe_payload.parent
    for cgu__ujx, uat__ekwle in hri__cxqpm.type_to_blk.items():
        bhlq__hbouw = context.get_constant(types.int64, len(hri__cxqpm.
            block_to_arr_ind[uat__ekwle]))
        kqfl__hymrt, rasa__atjh = ListInstance.allocate_ex(context, builder,
            types.List(cgu__ujx), bhlq__hbouw)
        rasa__atjh.size = bhlq__hbouw
        setattr(tbo__qfjb, f'block_{uat__ekwle}', rasa__atjh.value)
    for i, cgu__ujx in enumerate(fromty.data):
        ckjj__iau = builder.extract_value(in_dataframe_payload.data, i)
        uat__ekwle = hri__cxqpm.type_to_blk[cgu__ujx]
        xzs__kzd = getattr(tbo__qfjb, f'block_{uat__ekwle}')
        sfdyp__qma = ListInstance(context, builder, types.List(cgu__ujx),
            xzs__kzd)
        ula__fxup = context.get_constant(types.int64, hri__cxqpm.
            block_offsets[i])
        sfdyp__qma.setitem(ula__fxup, ckjj__iau, True)
    data_tup = context.make_tuple(builder, types.Tuple([hri__cxqpm]), [
        tbo__qfjb._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    hri__cxqpm = fromty.table_type
    tbo__qfjb = cgutils.create_struct_proxy(hri__cxqpm)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    utbs__kgih = []
    for i, cgu__ujx in enumerate(toty.data):
        uat__ekwle = hri__cxqpm.type_to_blk[cgu__ujx]
        xzs__kzd = getattr(tbo__qfjb, f'block_{uat__ekwle}')
        sfdyp__qma = ListInstance(context, builder, types.List(cgu__ujx),
            xzs__kzd)
        ula__fxup = context.get_constant(types.int64, hri__cxqpm.
            block_offsets[i])
        ckjj__iau = sfdyp__qma.getitem(ula__fxup)
        context.nrt.incref(builder, cgu__ujx, ckjj__iau)
        utbs__kgih.append(ckjj__iau)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), utbs__kgih)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    uut__qvbi, hersc__xqq, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    asrk__frl = gen_const_tup(uut__qvbi)
    wul__bkv = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    wul__bkv += (
        '  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, {})\n'
        .format(hersc__xqq, index_arg, asrk__frl))
    afrpl__trtj = {}
    exec(wul__bkv, {'bodo': bodo, 'np': np}, afrpl__trtj)
    dojtf__aphs = afrpl__trtj['_init_df']
    return dojtf__aphs


def _get_df_args(data, index, columns, dtype, copy):
    mxks__ktgc = ''
    if not is_overload_none(dtype):
        mxks__ktgc = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        fes__ocpfh = (len(data.types) - 1) // 2
        spemp__osu = [cgu__ujx.literal_value for cgu__ujx in data.types[1:
            fes__ocpfh + 1]]
        data_val_types = dict(zip(spemp__osu, data.types[fes__ocpfh + 1:]))
        utbs__kgih = ['data[{}]'.format(i) for i in range(fes__ocpfh + 1, 2 *
            fes__ocpfh + 1)]
        data_dict = dict(zip(spemp__osu, utbs__kgih))
        if is_overload_none(index):
            for i, cgu__ujx in enumerate(data.types[fes__ocpfh + 1:]):
                if isinstance(cgu__ujx, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(fes__ocpfh + 1 + i))
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
        ipl__bpgrz = '.copy()' if copy else ''
        uft__ltui = get_overload_const_list(columns)
        fes__ocpfh = len(uft__ltui)
        data_val_types = {vujd__mxom: data.copy(ndim=1) for vujd__mxom in
            uft__ltui}
        utbs__kgih = ['data[:,{}]{}'.format(i, ipl__bpgrz) for i in range(
            fes__ocpfh)]
        data_dict = dict(zip(uft__ltui, utbs__kgih))
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
    hersc__xqq = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[vujd__mxom], df_len, mxks__ktgc) for vujd__mxom in
        col_names))
    if len(col_names) == 0:
        hersc__xqq = '()'
    return col_names, hersc__xqq, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for vujd__mxom in col_names:
        if vujd__mxom in data_dict and is_iterable_type(data_val_types[
            vujd__mxom]):
            df_len = 'len({})'.format(data_dict[vujd__mxom])
            break
    if df_len == '0' and not index_is_none:
        df_len = f'len({index_arg})'
    return df_len


def _fill_null_arrays(data_dict, col_names, df_len, dtype):
    if all(vujd__mxom in data_dict for vujd__mxom in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    fwmv__syg = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for vujd__mxom in col_names:
        if vujd__mxom not in data_dict:
            data_dict[vujd__mxom] = fwmv__syg


@overload(len)
def df_len_overload(df):
    if not isinstance(df, DataFrameType):
        return
    if df.has_runtime_cols:

        def impl(df):
            cgu__ujx = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(cgu__ujx)
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
        ehr__gohqa = idx.literal_value
        if isinstance(ehr__gohqa, int):
            esj__ngws = tup.types[ehr__gohqa]
        elif isinstance(ehr__gohqa, slice):
            esj__ngws = types.BaseTuple.from_types(tup.types[ehr__gohqa])
        return signature(esj__ngws, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    dnvdo__aezd, idx = sig.args
    idx = idx.literal_value
    tup, kqfl__hymrt = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(dnvdo__aezd)
        if not 0 <= idx < len(dnvdo__aezd):
            raise IndexError('cannot index at %d in %s' % (idx, dnvdo__aezd))
        ltte__hvoh = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        zeguw__ciqkl = cgutils.unpack_tuple(builder, tup)[idx]
        ltte__hvoh = context.make_tuple(builder, sig.return_type, zeguw__ciqkl)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, ltte__hvoh)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, oqce__cppz, suffix_x,
            suffix_y, is_join, indicator, _bodo_na_equal, spe__tgkt) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        oua__tcoxc = set(left_on) & set(right_on)
        tzo__kjads = set(left_df.columns) & set(right_df.columns)
        honez__pdk = tzo__kjads - oua__tcoxc
        zuhys__ezvq = '$_bodo_index_' in left_on
        eepd__wqql = '$_bodo_index_' in right_on
        how = get_overload_const_str(oqce__cppz)
        cug__xvf = how in {'left', 'outer'}
        phznh__tnjr = how in {'right', 'outer'}
        columns = []
        data = []
        if zuhys__ezvq and not eepd__wqql and not is_join.literal_value:
            zkx__kvnqd = right_on[0]
            if zkx__kvnqd in left_df.columns:
                columns.append(zkx__kvnqd)
                data.append(right_df.data[right_df.columns.index(zkx__kvnqd)])
        if eepd__wqql and not zuhys__ezvq and not is_join.literal_value:
            ylgt__fzda = left_on[0]
            if ylgt__fzda in right_df.columns:
                columns.append(ylgt__fzda)
                data.append(left_df.data[left_df.columns.index(ylgt__fzda)])
        for kze__shkh, hag__urq in zip(left_df.data, left_df.columns):
            columns.append(str(hag__urq) + suffix_x.literal_value if 
                hag__urq in honez__pdk else hag__urq)
            if hag__urq in oua__tcoxc:
                data.append(kze__shkh)
            else:
                data.append(to_nullable_type(kze__shkh) if phznh__tnjr else
                    kze__shkh)
        for kze__shkh, hag__urq in zip(right_df.data, right_df.columns):
            if hag__urq not in oua__tcoxc:
                columns.append(str(hag__urq) + suffix_y.literal_value if 
                    hag__urq in honez__pdk else hag__urq)
                data.append(to_nullable_type(kze__shkh) if cug__xvf else
                    kze__shkh)
        nvoaz__xsbiq = get_overload_const_bool(indicator)
        if nvoaz__xsbiq:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        if zuhys__ezvq and eepd__wqql and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        elif zuhys__ezvq and not eepd__wqql:
            index_typ = right_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        elif eepd__wqql and not zuhys__ezvq:
            index_typ = left_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        uscv__mpyjh = DataFrameType(tuple(data), index_typ, tuple(columns))
        return signature(uscv__mpyjh, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    ulye__kgvj = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ulye__kgvj._getvalue()


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
    wsni__ehiq = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    yib__gqt = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', wsni__ehiq, yib__gqt,
        package_name='pandas', module_name='General')
    wul__bkv = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        ftcsz__malt = 0
        hersc__xqq = []
        names = []
        for i, wizr__ejp in enumerate(objs.types):
            assert isinstance(wizr__ejp, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(wizr__ejp, 'pd.concat()')
            if isinstance(wizr__ejp, SeriesType):
                names.append(str(ftcsz__malt))
                ftcsz__malt += 1
                hersc__xqq.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(wizr__ejp.columns)
                for nny__qpp in range(len(wizr__ejp.data)):
                    hersc__xqq.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, nny__qpp))
        return bodo.hiframes.dataframe_impl._gen_init_df(wul__bkv, names,
            ', '.join(hersc__xqq), index)
    assert axis == 0
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(cgu__ujx, DataFrameType) for cgu__ujx in objs
            .types)
        zoas__rqjr = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pd.concat()')
            zoas__rqjr.extend(df.columns)
        zoas__rqjr = list(dict.fromkeys(zoas__rqjr).keys())
        fdvv__qayt = {}
        for ftcsz__malt, vujd__mxom in enumerate(zoas__rqjr):
            for df in objs.types:
                if vujd__mxom in df.columns:
                    fdvv__qayt['arr_typ{}'.format(ftcsz__malt)] = df.data[df
                        .columns.index(vujd__mxom)]
                    break
        assert len(fdvv__qayt) == len(zoas__rqjr)
        rub__ubc = []
        for ftcsz__malt, vujd__mxom in enumerate(zoas__rqjr):
            args = []
            for i, df in enumerate(objs.types):
                if vujd__mxom in df.columns:
                    krflw__qvd = df.columns.index(vujd__mxom)
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, krflw__qvd))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, ftcsz__malt))
            wul__bkv += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'.
                format(ftcsz__malt, ', '.join(args)))
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
        return bodo.hiframes.dataframe_impl._gen_init_df(wul__bkv,
            zoas__rqjr, ', '.join('A{}'.format(i) for i in range(len(
            zoas__rqjr))), index, fdvv__qayt)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(cgu__ujx, SeriesType) for cgu__ujx in objs.types)
        wul__bkv += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'.
            format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            wul__bkv += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            wul__bkv += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        wul__bkv += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        afrpl__trtj = {}
        exec(wul__bkv, {'bodo': bodo, 'np': np, 'numba': numba}, afrpl__trtj)
        return afrpl__trtj['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pd.concat()')
        df_type = objs.dtype
        for ftcsz__malt, vujd__mxom in enumerate(df_type.columns):
            wul__bkv += '  arrs{} = []\n'.format(ftcsz__malt)
            wul__bkv += '  for i in range(len(objs)):\n'
            wul__bkv += '    df = objs[i]\n'
            wul__bkv += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(ftcsz__malt))
            wul__bkv += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(ftcsz__malt))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            wul__bkv += '  arrs_index = []\n'
            wul__bkv += '  for i in range(len(objs)):\n'
            wul__bkv += '    df = objs[i]\n'
            wul__bkv += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(wul__bkv, df_type.
            columns, ', '.join('out_arr{}'.format(i) for i in range(len(
            df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        wul__bkv += '  arrs = []\n'
        wul__bkv += '  for i in range(len(objs)):\n'
        wul__bkv += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        wul__bkv += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            wul__bkv += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            wul__bkv += '  arrs_index = []\n'
            wul__bkv += '  for i in range(len(objs)):\n'
            wul__bkv += '    S = objs[i]\n'
            wul__bkv += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            wul__bkv += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        wul__bkv += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        afrpl__trtj = {}
        exec(wul__bkv, {'bodo': bodo, 'np': np, 'numba': numba}, afrpl__trtj)
        return afrpl__trtj['impl']
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
        yfi__vvya = df.copy(index=index, is_table_format=False)
        return signature(yfi__vvya, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    yxgal__vmc = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return yxgal__vmc._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    wsni__ehiq = dict(index=index, name=name)
    yib__gqt = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', wsni__ehiq, yib__gqt,
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
        fdvv__qayt = (types.Array(types.int64, 1, 'C'),) + df.data
        ceuu__kiaj = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, fdvv__qayt)
        return signature(ceuu__kiaj, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    yxgal__vmc = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return yxgal__vmc._getvalue()


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
    yxgal__vmc = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return yxgal__vmc._getvalue()


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
    yxgal__vmc = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return yxgal__vmc._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values, index_name,
    columns_name, value_names, check_duplicates=True, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    frx__soem = get_overload_const_bool(check_duplicates)
    yhwqt__threy = not is_overload_none(value_names)
    ofayv__rphk = isinstance(values_tup, types.UniTuple)
    if ofayv__rphk:
        pqxl__kwiel = [to_nullable_type(values_tup.dtype)]
    else:
        pqxl__kwiel = [to_nullable_type(tazid__enlam) for tazid__enlam in
            values_tup]
    wul__bkv = 'def impl(\n'
    wul__bkv += """    index_tup, columns_tup, values_tup, pivot_values, index_name, columns_name, value_names, check_duplicates=True, parallel=False
"""
    wul__bkv += '):\n'
    wul__bkv += '    if parallel:\n'
    vvot__ymqw = ', '.join([f'array_to_info(index_tup[{i}])' for i in range
        (len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for i in
        range(len(columns_tup))] + [f'array_to_info(values_tup[{i}])' for i in
        range(len(values_tup))])
    wul__bkv += f'        info_list = [{vvot__ymqw}]\n'
    wul__bkv += '        cpp_table = arr_info_list_to_table(info_list)\n'
    wul__bkv += (
        '        out_cpp_table = shuffle_table(cpp_table, 1, parallel, 0)\n')
    iex__cchwo = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
         for i in range(len(index_tup))])
    gxmut__kljto = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
         for i in range(len(columns_tup))])
    gymrc__xyqkm = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
         for i in range(len(values_tup))])
    wul__bkv += f'        index_tup = ({iex__cchwo},)\n'
    wul__bkv += f'        columns_tup = ({gxmut__kljto},)\n'
    wul__bkv += f'        values_tup = ({gymrc__xyqkm},)\n'
    wul__bkv += '        delete_table(cpp_table)\n'
    wul__bkv += '        delete_table(out_cpp_table)\n'
    wul__bkv += '    index_arr = index_tup[0]\n'
    wul__bkv += '    columns_arr = columns_tup[0]\n'
    if ofayv__rphk:
        wul__bkv += '    values_arrs = [arr for arr in values_tup]\n'
    wul__bkv += (
        '    unique_index_arr, row_vector = bodo.libs.array_ops.array_unique_vector_map(\n'
        )
    wul__bkv += '        index_arr\n'
    wul__bkv += '    )\n'
    wul__bkv += '    n_rows = len(unique_index_arr)\n'
    wul__bkv += '    num_values_arrays = len(values_tup)\n'
    wul__bkv += '    n_unique_pivots = len(pivot_values)\n'
    if ofayv__rphk:
        wul__bkv += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        wul__bkv += '    n_cols = n_unique_pivots\n'
    wul__bkv += '    col_map = {}\n'
    wul__bkv += '    for i in range(n_unique_pivots):\n'
    wul__bkv += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    wul__bkv += '            raise ValueError(\n'
    wul__bkv += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    wul__bkv += '            )\n'
    wul__bkv += '        col_map[pivot_values[i]] = i\n'
    wye__rgq = False
    for i, kiu__bbip in enumerate(pqxl__kwiel):
        if kiu__bbip == bodo.string_array_type:
            wye__rgq = True
            wul__bkv += (
                f'    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]\n'
                )
            wul__bkv += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if wye__rgq:
        if frx__soem:
            wul__bkv += '    nbytes = (n_rows + 7) >> 3\n'
            wul__bkv += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        wul__bkv += '    for i in range(len(columns_arr)):\n'
        wul__bkv += '        col_name = columns_arr[i]\n'
        wul__bkv += '        pivot_idx = col_map[col_name]\n'
        wul__bkv += '        row_idx = row_vector[i]\n'
        if frx__soem:
            wul__bkv += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            wul__bkv += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            wul__bkv += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            wul__bkv += '        else:\n'
            wul__bkv += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if ofayv__rphk:
            wul__bkv += '        for j in range(num_values_arrays):\n'
            wul__bkv += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            wul__bkv += '            len_arr = len_arrs_0[col_idx]\n'
            wul__bkv += '            values_arr = values_arrs[j]\n'
            wul__bkv += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            wul__bkv += (
                '                len_arr[row_idx] = len(values_arr[i])\n')
            wul__bkv += (
                '                total_lens_0[col_idx] += len(values_arr[i])\n'
                )
        else:
            for i, kiu__bbip in enumerate(pqxl__kwiel):
                if kiu__bbip == bodo.string_array_type:
                    wul__bkv += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    wul__bkv += f"""            len_arrs_{i}[pivot_idx][row_idx] = len(values_tup[{i}][i])
"""
                    wul__bkv += f"""            total_lens_{i}[pivot_idx] += len(values_tup[{i}][i])
"""
    for i, kiu__bbip in enumerate(pqxl__kwiel):
        if kiu__bbip == bodo.string_array_type:
            wul__bkv += f'    data_arrs_{i} = [\n'
            wul__bkv += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            wul__bkv += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            wul__bkv += '        )\n'
            wul__bkv += '        for i in range(n_cols)\n'
            wul__bkv += '    ]\n'
        else:
            wul__bkv += f'    data_arrs_{i} = [\n'
            wul__bkv += (
                f'        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})\n'
                )
            wul__bkv += '        for _ in range(n_cols)\n'
            wul__bkv += '    ]\n'
    if not wye__rgq and frx__soem:
        wul__bkv += '    nbytes = (n_rows + 7) >> 3\n'
        wul__bkv += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    wul__bkv += '    for i in range(len(columns_arr)):\n'
    wul__bkv += '        col_name = columns_arr[i]\n'
    wul__bkv += '        pivot_idx = col_map[col_name]\n'
    wul__bkv += '        row_idx = row_vector[i]\n'
    if not wye__rgq and frx__soem:
        wul__bkv += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        wul__bkv += (
            '        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):\n'
            )
        wul__bkv += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        wul__bkv += '        else:\n'
        wul__bkv += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if ofayv__rphk:
        wul__bkv += '        for j in range(num_values_arrays):\n'
        wul__bkv += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        wul__bkv += '            col_arr = data_arrs_0[col_idx]\n'
        wul__bkv += '            values_arr = values_arrs[j]\n'
        wul__bkv += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        wul__bkv += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        wul__bkv += '            else:\n'
        wul__bkv += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, kiu__bbip in enumerate(pqxl__kwiel):
            wul__bkv += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            wul__bkv += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            wul__bkv += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            wul__bkv += f'        else:\n'
            wul__bkv += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    wul__bkv += """    index = bodo.utils.conversion.index_from_array(unique_index_arr, index_name)
"""
    if yhwqt__threy:
        wul__bkv += '    num_rows = len(value_names) * len(pivot_values)\n'
        if value_names == bodo.string_array_type:
            wul__bkv += '    total_chars = 0\n'
            wul__bkv += '    for i in range(len(value_names)):\n'
            wul__bkv += '        total_chars += len(value_names[i])\n'
            wul__bkv += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
        else:
            wul__bkv += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names, (-1,))
"""
        if pivot_values == bodo.string_array_type:
            wul__bkv += '    total_chars = 0\n'
            wul__bkv += '    for i in range(len(pivot_values)):\n'
            wul__bkv += '        total_chars += len(pivot_values[i])\n'
            wul__bkv += """    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(value_names))
"""
        else:
            wul__bkv += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
        wul__bkv += '    for i in range(len(value_names)):\n'
        wul__bkv += '        for j in range(len(pivot_values)):\n'
        wul__bkv += (
            '            new_value_names[(i * len(pivot_values)) + j] = value_names[i]\n'
            )
        wul__bkv += (
            '            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]\n'
            )
        wul__bkv += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name), None)
"""
    else:
        wul__bkv += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name)
"""
    uky__yrt = ', '.join(f'data_arrs_{i}' for i in range(len(pqxl__kwiel)))
    wul__bkv += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({uky__yrt},), n_rows)
"""
    wul__bkv += (
        '    return bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
        )
    wul__bkv += '        (table,), index, column_index\n'
    wul__bkv += '    )\n'
    afrpl__trtj = {}
    vecaw__ckdli = {f'data_arr_typ_{i}': kiu__bbip for i, kiu__bbip in
        enumerate(pqxl__kwiel)}
    wlkxe__zkpo = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, **vecaw__ckdli}
    exec(wul__bkv, wlkxe__zkpo, afrpl__trtj)
    impl = afrpl__trtj['impl']
    return impl


def gen_pandas_parquet_metadata(df, write_non_range_index_to_metadata,
    write_rangeindex_to_metadata, partition_cols=None):
    uozpe__wrub = {}
    uozpe__wrub['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, kxpy__ytpst in zip(df.columns, df.data):
        if col_name in partition_cols:
            continue
        if isinstance(kxpy__ytpst, types.Array
            ) or kxpy__ytpst == boolean_array:
            yoipm__gof = nsf__cka = kxpy__ytpst.dtype.name
            if nsf__cka.startswith('datetime'):
                yoipm__gof = 'datetime'
        elif kxpy__ytpst == string_array_type:
            yoipm__gof = 'unicode'
            nsf__cka = 'object'
        elif kxpy__ytpst == binary_array_type:
            yoipm__gof = 'bytes'
            nsf__cka = 'object'
        elif isinstance(kxpy__ytpst, DecimalArrayType):
            yoipm__gof = nsf__cka = 'object'
        elif isinstance(kxpy__ytpst, IntegerArrayType):
            yofdv__tmgwu = kxpy__ytpst.dtype.name
            if yofdv__tmgwu.startswith('int'):
                yoipm__gof = 'Int' + yofdv__tmgwu[3:]
            elif yofdv__tmgwu.startswith('uint'):
                yoipm__gof = 'UInt' + yofdv__tmgwu[4:]
            else:
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, kxpy__ytpst))
            nsf__cka = kxpy__ytpst.dtype.name
        elif kxpy__ytpst == datetime_date_array_type:
            yoipm__gof = 'datetime'
            nsf__cka = 'object'
        elif isinstance(kxpy__ytpst, (StructArrayType, ArrayItemArrayType)):
            yoipm__gof = 'object'
            nsf__cka = 'object'
        else:
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, kxpy__ytpst))
        hlscy__iwvjo = {'name': col_name, 'field_name': col_name,
            'pandas_type': yoipm__gof, 'numpy_type': nsf__cka, 'metadata': None
            }
        uozpe__wrub['columns'].append(hlscy__iwvjo)
    if write_non_range_index_to_metadata:
        if isinstance(df.index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in df.index.name:
            ndnzw__nhlu = '__index_level_0__'
            tsrh__xne = None
        else:
            ndnzw__nhlu = '%s'
            tsrh__xne = '%s'
        uozpe__wrub['index_columns'] = [ndnzw__nhlu]
        uozpe__wrub['columns'].append({'name': tsrh__xne, 'field_name':
            ndnzw__nhlu, 'pandas_type': df.index.pandas_type_name,
            'numpy_type': df.index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        uozpe__wrub['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        uozpe__wrub['index_columns'] = []
    uozpe__wrub['pandas_version'] = pd.__version__
    return uozpe__wrub


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
        bnv__rueqa = []
        for utxxu__ilgre in partition_cols:
            try:
                idx = df.columns.index(utxxu__ilgre)
            except ValueError as peyo__ucvx:
                raise BodoError(
                    f'Partition column {utxxu__ilgre} is not in dataframe')
            bnv__rueqa.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    yhec__myxs = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType
        )
    txkav__xfqlw = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not yhec__myxs)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not yhec__myxs or
        is_overload_true(_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and yhec__myxs and not is_overload_true(_is_parallel)
    hlt__tzck = json.dumps(gen_pandas_parquet_metadata(df,
        write_non_range_index_to_metadata, write_rangeindex_to_metadata,
        partition_cols=partition_cols))
    if not is_overload_true(_is_parallel) and yhec__myxs:
        hlt__tzck = hlt__tzck.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            hlt__tzck = hlt__tzck.replace('"%s"', '%s')
    hersc__xqq = ', '.join(
        'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(len(df.columns)))
    wul__bkv = """def df_to_parquet(df, fname, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, _is_parallel=False):
"""
    if df.is_table_format:
        wul__bkv += (
            '    table = py_table_to_cpp_table(get_dataframe_table(df), py_table_typ)\n'
            )
    else:
        wul__bkv += '    info_list = [{}]\n'.format(hersc__xqq)
        wul__bkv += '    table = arr_info_list_to_table(info_list)\n'
    wul__bkv += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and txkav__xfqlw:
        wul__bkv += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        ksnl__mcbkn = True
    else:
        wul__bkv += '    index_col = array_to_info(np.empty(0))\n'
        ksnl__mcbkn = False
    wul__bkv += '    metadata = """' + hlt__tzck + '"""\n'
    wul__bkv += '    if compression is None:\n'
    wul__bkv += "        compression = 'none'\n"
    wul__bkv += '    if df.index.name is not None:\n'
    wul__bkv += '        name_ptr = df.index.name\n'
    wul__bkv += '    else:\n'
    wul__bkv += "        name_ptr = 'null'\n"
    wul__bkv += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel=_is_parallel)
"""
    nzee__jbnbc = None
    if partition_cols:
        nzee__jbnbc = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        bvko__fwuq = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in bnv__rueqa)
        if bvko__fwuq:
            wul__bkv += '    cat_info_list = [{}]\n'.format(bvko__fwuq)
            wul__bkv += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            wul__bkv += '    cat_table = table\n'
        wul__bkv += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        wul__bkv += (
            f'    part_cols_idxs = np.array({bnv__rueqa}, dtype=np.int32)\n')
        wul__bkv += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(fname),\n'
            )
        wul__bkv += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        wul__bkv += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        wul__bkv += (
            '                            unicode_to_utf8(compression),\n')
        wul__bkv += '                            _is_parallel,\n'
        wul__bkv += (
            '                            unicode_to_utf8(bucket_region))\n')
        wul__bkv += '    delete_table_decref_arrays(table)\n'
        wul__bkv += '    delete_info_decref_array(index_col)\n'
        wul__bkv += '    delete_info_decref_array(col_names_no_partitions)\n'
        wul__bkv += '    delete_info_decref_array(col_names)\n'
        if bvko__fwuq:
            wul__bkv += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        wul__bkv += '    parquet_write_table_cpp(unicode_to_utf8(fname),\n'
        wul__bkv += (
            '                            table, col_names, index_col,\n')
        wul__bkv += '                            ' + str(ksnl__mcbkn) + ',\n'
        wul__bkv += '                            unicode_to_utf8(metadata),\n'
        wul__bkv += (
            '                            unicode_to_utf8(compression),\n')
        wul__bkv += (
            '                            _is_parallel, 1, df.index.start,\n')
        wul__bkv += (
            '                            df.index.stop, df.index.step,\n')
        wul__bkv += '                            unicode_to_utf8(name_ptr),\n'
        wul__bkv += (
            '                            unicode_to_utf8(bucket_region))\n')
        wul__bkv += '    delete_table_decref_arrays(table)\n'
        wul__bkv += '    delete_info_decref_array(index_col)\n'
        wul__bkv += '    delete_info_decref_array(col_names)\n'
    else:
        wul__bkv += '    parquet_write_table_cpp(unicode_to_utf8(fname),\n'
        wul__bkv += (
            '                            table, col_names, index_col,\n')
        wul__bkv += '                            ' + str(ksnl__mcbkn) + ',\n'
        wul__bkv += '                            unicode_to_utf8(metadata),\n'
        wul__bkv += (
            '                            unicode_to_utf8(compression),\n')
        wul__bkv += '                            _is_parallel, 0, 0, 0, 0,\n'
        wul__bkv += '                            unicode_to_utf8(name_ptr),\n'
        wul__bkv += (
            '                            unicode_to_utf8(bucket_region))\n')
        wul__bkv += '    delete_table_decref_arrays(table)\n'
        wul__bkv += '    delete_info_decref_array(index_col)\n'
        wul__bkv += '    delete_info_decref_array(col_names)\n'
    afrpl__trtj = {}
    exec(wul__bkv, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
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
        'col_names_no_parts_arr': nzee__jbnbc}, afrpl__trtj)
    nlee__zsqbz = afrpl__trtj['df_to_parquet']
    return nlee__zsqbz


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None):
    aclb__xdih = 'all_ok'
    try:
        df.to_sql(name, con, schema, if_exists, index, index_label,
            chunksize, dtype, method)
    except ValueError as jms__tul:
        aclb__xdih = jms__tul.args[0]
    return aclb__xdih


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
    wsni__ehiq = dict(chunksize=chunksize)
    yib__gqt = dict(chunksize=None)
    check_unsupported_args('to_sql', wsni__ehiq, yib__gqt, package_name=
        'pandas', module_name='IO')

    def _impl(df, name, con, schema=None, if_exists='fail', index=True,
        index_label=None, chunksize=None, dtype=None, method=None,
        _is_parallel=False):
        xmcsf__cqs = bodo.libs.distributed_api.get_rank()
        aclb__xdih = 'unset'
        if xmcsf__cqs != 0:
            if_exists = 'append'
            aclb__xdih = bcast_scalar(aclb__xdih)
        if xmcsf__cqs == 0 or _is_parallel and aclb__xdih == 'all_ok':
            aclb__xdih = to_sql_exception_guard_encaps(df, name, con,
                schema, if_exists, index, index_label, chunksize, dtype, method
                )
        if xmcsf__cqs == 0:
            aclb__xdih = bcast_scalar(aclb__xdih)
        if aclb__xdih != 'all_ok':
            print('err_msg=', aclb__xdih)
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
        qietd__ouend = get_overload_const_str(path_or_buf)
        if qietd__ouend.endswith(('.gz', '.bz2', '.zip', '.xz')):
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
        ubm__ouq = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(ubm__ouq))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(ubm__ouq))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    udtgi__zvn = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    pcv__ggsh = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', udtgi__zvn, pcv__ggsh,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    wul__bkv = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        tuq__sqy = data.data.dtype.categories
        wul__bkv += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        tuq__sqy = data.dtype.categories
        wul__bkv += '  data_values = data\n'
    fes__ocpfh = len(tuq__sqy)
    wul__bkv += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    wul__bkv += '  numba.parfors.parfor.init_prange()\n'
    wul__bkv += '  n = len(data_values)\n'
    for i in range(fes__ocpfh):
        wul__bkv += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    wul__bkv += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    wul__bkv += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for nny__qpp in range(fes__ocpfh):
        wul__bkv += '          data_arr_{}[i] = 0\n'.format(nny__qpp)
    wul__bkv += '      else:\n'
    for hgtv__nvvl in range(fes__ocpfh):
        wul__bkv += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            hgtv__nvvl)
    hersc__xqq = ', '.join(f'data_arr_{i}' for i in range(fes__ocpfh))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(tuq__sqy[0], np.datetime64):
        tuq__sqy = tuple(pd.Timestamp(vujd__mxom) for vujd__mxom in tuq__sqy)
    return bodo.hiframes.dataframe_impl._gen_init_df(wul__bkv, tuq__sqy,
        hersc__xqq, index)


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
    for qxena__aenr in pd_unsupported:
        fname = mod_name + '.' + qxena__aenr.__name__
        overload(qxena__aenr, no_unliteral=True)(create_unsupported_overload
            (fname))


def _install_dataframe_unsupported():
    for tjp__aawu in dataframe_unsupported_attrs:
        rsdj__wdcvw = 'DataFrame.' + tjp__aawu
        overload_attribute(DataFrameType, tjp__aawu)(
            create_unsupported_overload(rsdj__wdcvw))
    for fname in dataframe_unsupported:
        rsdj__wdcvw = 'DataFrame.' + fname + '()'
        overload_method(DataFrameType, fname)(create_unsupported_overload(
            rsdj__wdcvw))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
