import os
import warnings
from collections import defaultdict
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow
import pyarrow.dataset as ds
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, get_definition, guard, mk_unique_var, next_label, replace_arg_nodes
from numba.extending import NativeValue, intrinsic, models, overload, register_model, unbox
from pyarrow import null
import bodo
import bodo.ir.parquet_ext
import bodo.utils.tracing as tracing
from bodo.hiframes.datetime_date_ext import datetime_date_array_type, datetime_date_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import TableType
from bodo.io.fs_io import get_hdfs_fs, get_s3_fs_from_path, get_s3_subtree_fs
from bodo.libs.array import cpp_table_to_py_table, delete_table, info_from_table, info_to_array, table_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.distributed_api import get_end, get_start
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.transforms import distributed_pass
from bodo.utils.transform import get_const_value
from bodo.utils.typing import BodoError, BodoWarning, FileInfo, get_overload_const_str, get_overload_constant_dict
from bodo.utils.utils import check_and_propagate_cpp_exception, numba_to_c_type, sanitize_varname
use_nullable_int_arr = True
from urllib.parse import urlparse
import bodo.io.pa_parquet


class ParquetPredicateType(types.Type):

    def __init__(self):
        super(ParquetPredicateType, self).__init__(name=
            'ParquetPredicateType()')


parquet_predicate_type = ParquetPredicateType()
types.parquet_predicate_type = parquet_predicate_type
register_model(ParquetPredicateType)(models.OpaqueModel)


@unbox(ParquetPredicateType)
def unbox_parquet_predicate_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


class ReadParquetFilepathType(types.Opaque):

    def __init__(self):
        super(ReadParquetFilepathType, self).__init__(name=
            'ReadParquetFilepathType')


read_parquet_fpath_type = ReadParquetFilepathType()
types.read_parquet_fpath_type = read_parquet_fpath_type
register_model(ReadParquetFilepathType)(models.OpaqueModel)


@unbox(ReadParquetFilepathType)
def unbox_read_parquet_fpath_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


class StorageOptionsDictType(types.Opaque):

    def __init__(self):
        super(StorageOptionsDictType, self).__init__(name=
            'StorageOptionsDictType')


storage_options_dict_type = StorageOptionsDictType()
types.storage_options_dict_type = storage_options_dict_type
register_model(StorageOptionsDictType)(models.OpaqueModel)


@unbox(StorageOptionsDictType)
def unbox_storage_options_dict_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


class ParquetFileInfo(FileInfo):

    def __init__(self, columns, storage_options=None):
        self.columns = columns
        self.storage_options = storage_options
        super().__init__()

    def _get_schema(self, fname):
        try:
            return parquet_file_schema(fname, selected_columns=self.columns,
                storage_options=self.storage_options)
        except OSError as wugx__ajl:
            if 'non-file path' in str(wugx__ajl):
                raise FileNotFoundError(str(wugx__ajl))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=None):
        hedm__frtyl = lhs.scope
        vww__bchv = lhs.loc
        jrden__vgpi = None
        if lhs.name in self.locals:
            jrden__vgpi = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        bosmv__rbmmc = {}
        if lhs.name + ':convert' in self.locals:
            bosmv__rbmmc = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if jrden__vgpi is None:
            octw__ycz = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/source/programming_with_bodo/file_io.html#non-constant-filepaths'
                )
            orb__yphd = get_const_value(file_name, self.func_ir, octw__ycz,
                arg_types=self.args, file_info=ParquetFileInfo(columns,
                storage_options=storage_options))
            mkzt__zzyo = False
            wmhb__oub = guard(get_definition, self.func_ir, file_name)
            if isinstance(wmhb__oub, ir.Arg):
                typ = self.args[wmhb__oub.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, zwkye__akep, dpvi__jbeju, col_indices,
                        partition_names) = typ.schema
                    mkzt__zzyo = True
            if not mkzt__zzyo:
                (col_names, zwkye__akep, dpvi__jbeju, col_indices,
                    partition_names) = (parquet_file_schema(orb__yphd,
                    columns, storage_options=storage_options))
        else:
            ojw__txmb = list(jrden__vgpi.keys())
            qjrul__gpb = [sgsc__ncf for sgsc__ncf in jrden__vgpi.values()]
            dpvi__jbeju = 'index' if 'index' in ojw__txmb else None
            if columns is None:
                selected_columns = ojw__txmb
            else:
                selected_columns = columns
            col_indices = [ojw__txmb.index(c) for c in selected_columns]
            zwkye__akep = [qjrul__gpb[ojw__txmb.index(c)] for c in
                selected_columns]
            col_names = selected_columns
            dpvi__jbeju = dpvi__jbeju if dpvi__jbeju in col_names else None
            partition_names = []
        ixh__xuw = None if isinstance(dpvi__jbeju, dict
            ) or dpvi__jbeju is None else dpvi__jbeju
        index_column_index = None
        index_column_type = types.none
        if ixh__xuw:
            cyve__ebhn = col_names.index(ixh__xuw)
            col_indices = col_indices.copy()
            zwkye__akep = zwkye__akep.copy()
            index_column_index = col_indices.pop(cyve__ebhn)
            index_column_type = zwkye__akep.pop(cyve__ebhn)
        for bkh__jbi, c in enumerate(col_names):
            if c in bosmv__rbmmc:
                zwkye__akep[bkh__jbi] = bosmv__rbmmc[c]
        zfye__mdehw = [ir.Var(hedm__frtyl, mk_unique_var('pq_table'),
            vww__bchv), ir.Var(hedm__frtyl, mk_unique_var('pq_index'),
            vww__bchv)]
        jaoop__pxy = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.name,
            col_names, col_indices, zwkye__akep, zfye__mdehw, vww__bchv,
            partition_names, storage_options, index_column_index,
            index_column_type)]
        return (col_names, zfye__mdehw, dpvi__jbeju, jaoop__pxy,
            zwkye__akep, index_column_type)


def determine_filter_cast(pq_node, typemap, filter_val):
    ugq__ydgg = filter_val[0]
    gtnx__fzym = pq_node.original_out_types[pq_node.original_df_colnames.
        index(ugq__ydgg)]
    vqa__pnlyp = bodo.utils.typing.element_type(gtnx__fzym)
    if ugq__ydgg in pq_node.partition_names:
        if vqa__pnlyp == types.unicode_type:
            pzzys__wwopw = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(vqa__pnlyp, types.Integer):
            pzzys__wwopw = f'.cast(pyarrow.{vqa__pnlyp.name}(), safe=False)'
        else:
            pzzys__wwopw = ''
    else:
        pzzys__wwopw = ''
    szut__lsgj = typemap[filter_val[2].name]
    if not bodo.utils.typing.is_common_scalar_dtype([vqa__pnlyp, szut__lsgj]):
        if not bodo.utils.typing.is_safe_arrow_cast(vqa__pnlyp, szut__lsgj):
            raise BodoError(
                f'Unsupport Arrow cast from {vqa__pnlyp} to {szut__lsgj} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if vqa__pnlyp == types.unicode_type:
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif vqa__pnlyp in (bodo.datetime64ns, bodo.pd_timestamp_type):
            return pzzys__wwopw, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return pzzys__wwopw, ''


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    pnicy__jlj = len(pq_node.out_vars)
    extra_args = ''
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    jagv__qjyb, fty__jixya = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    if jagv__qjyb:
        qfaty__lwk = []
        qyypu__iis = []
        abrxe__dplky = False
        ymk__gug = None
        for zxta__pkcnj in pq_node.filters:
            fkzcf__mtub = []
            jifmg__fhb = []
            mdv__dvxwm = set()
            for cqt__uswae in zxta__pkcnj:
                if isinstance(cqt__uswae[2], ir.Var):
                    aifdf__kldcy, lbix__csli = determine_filter_cast(pq_node,
                        typemap, cqt__uswae)
                    jifmg__fhb.append(
                        f"(ds.field('{cqt__uswae[0]}'){aifdf__kldcy} {cqt__uswae[1]} ds.scalar({jagv__qjyb[cqt__uswae[2].name]}){lbix__csli})"
                        )
                else:
                    assert cqt__uswae[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if cqt__uswae[1] == 'is not':
                        wtvqx__qol = '~'
                    else:
                        wtvqx__qol = ''
                    jifmg__fhb.append(
                        f"({wtvqx__qol}ds.field('{cqt__uswae[0]}').is_null())")
                if cqt__uswae[0] in pq_node.partition_names and isinstance(
                    cqt__uswae[2], ir.Var):
                    mmra__ouer = (
                        f"('{cqt__uswae[0]}', '{cqt__uswae[1]}', {jagv__qjyb[cqt__uswae[2].name]})"
                        )
                    fkzcf__mtub.append(mmra__ouer)
                    mdv__dvxwm.add(mmra__ouer)
                else:
                    abrxe__dplky = True
            if ymk__gug is None:
                ymk__gug = mdv__dvxwm
            else:
                ymk__gug.intersection_update(mdv__dvxwm)
            xus__eutlg = ', '.join(fkzcf__mtub)
            zpe__tezw = ' & '.join(jifmg__fhb)
            if xus__eutlg:
                qfaty__lwk.append(f'[{xus__eutlg}]')
            qyypu__iis.append(f'({zpe__tezw})')
        llp__gqcg = ', '.join(qfaty__lwk)
        abmpd__ibp = ' | '.join(qyypu__iis)
        if abrxe__dplky:
            if ymk__gug:
                aus__hotk = sorted(ymk__gug)
                dnf_filter_str = f"[[{', '.join(aus__hotk)}]]"
        elif llp__gqcg:
            dnf_filter_str = f'[{llp__gqcg}]'
        expr_filter_str = f'({abmpd__ibp})'
        extra_args = ', '.join(jagv__qjyb.values())
    hkjh__msjom = ', '.join(f'out{bkh__jbi}' for bkh__jbi in range(pnicy__jlj))
    pcaf__gygy = f'def pq_impl(fname, {extra_args}):\n'
    pcaf__gygy += (
        f'    (total_rows, {hkjh__msjom},) = _pq_reader_py(fname, {extra_args})\n'
        )
    oplhb__gjrn = {}
    exec(pcaf__gygy, {}, oplhb__gjrn)
    isgz__fabe = oplhb__gjrn['pq_impl']
    parallel = False
    if array_dists is not None:
        djhyg__zto = pq_node.out_vars[0].name
        parallel = array_dists[djhyg__zto] in (distributed_pass.
            Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        tvb__myq = pq_node.out_vars[1].name
        assert typemap[tvb__myq] == types.none or not parallel or array_dists[
            tvb__myq] in (distributed_pass.Distribution.OneD,
            distributed_pass.Distribution.OneD_Var
            ), 'pq data/index parallelization does not match'
    uju__ovv = _gen_pq_reader_py(pq_node.df_colnames, pq_node.col_indices,
        pq_node.type_usecol_offset, pq_node.out_types, pq_node.
        storage_options, pq_node.partition_names, dnf_filter_str,
        expr_filter_str, extra_args, parallel, meta_head_only_info, pq_node
        .index_column_index, pq_node.index_column_type)
    ectb__cnqhd = typemap[pq_node.file_name.name]
    uyji__kgugw = (ectb__cnqhd,) + tuple(typemap[cqt__uswae.name] for
        cqt__uswae in fty__jixya)
    utn__fegag = compile_to_numba_ir(isgz__fabe, {'_pq_reader_py': uju__ovv
        }, typingctx=typingctx, targetctx=targetctx, arg_typs=uyji__kgugw,
        typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(utn__fegag, [pq_node.file_name] + fty__jixya)
    jaoop__pxy = utn__fegag.body[:-3]
    if meta_head_only_info:
        jaoop__pxy[-1 - pnicy__jlj].target = meta_head_only_info[1]
    jaoop__pxy[-2].target = pq_node.out_vars[0]
    jaoop__pxy[-1].target = pq_node.out_vars[1]
    return jaoop__pxy


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    opsb__mcw = get_overload_const_str(dnf_filter_str)
    fwljm__yoszv = get_overload_const_str(expr_filter_str)
    nla__cfmaq = ', '.join(f'f{bkh__jbi}' for bkh__jbi in range(len(var_tup)))
    pcaf__gygy = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        pcaf__gygy += f'  {nla__cfmaq}, = var_tup\n'
    pcaf__gygy += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    pcaf__gygy += f'    dnf_filters_py = {opsb__mcw}\n'
    pcaf__gygy += f'    expr_filters_py = {fwljm__yoszv}\n'
    pcaf__gygy += '  return (dnf_filters_py, expr_filters_py)\n'
    oplhb__gjrn = {}
    exec(pcaf__gygy, globals(), oplhb__gjrn)
    return oplhb__gjrn['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def get_storage_options_pyobject(storage_options):
    pass


@overload(get_storage_options_pyobject, no_unliteral=True)
def overload_get_storage_options_pyobject(storage_options):
    iicyb__btxuf = get_overload_constant_dict(storage_options)
    pcaf__gygy = 'def impl(storage_options):\n'
    pcaf__gygy += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    pcaf__gygy += f'    storage_options_py = {str(iicyb__btxuf)}\n'
    pcaf__gygy += '  return storage_options_py\n'
    oplhb__gjrn = {}
    exec(pcaf__gygy, globals(), oplhb__gjrn)
    return oplhb__gjrn['impl']


def _gen_pq_reader_py(col_names, col_indices, type_usecol_offset, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type):
    lqqqo__rictv = next_label()
    vsf__hxocd = ',' if extra_args else ''
    pcaf__gygy = f'def pq_reader_py(fname,{extra_args}):\n'
    pcaf__gygy += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    pcaf__gygy += "    ev.add_attribute('fname', fname)\n"
    pcaf__gygy += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={is_parallel})
"""
    pcaf__gygy += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{vsf__hxocd}))
"""
    pcaf__gygy += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    pcaf__gygy += (
        f'    storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    ujz__hqwmu = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        ujz__hqwmu = meta_head_only_info[0]
    msr__drd = not type_usecol_offset
    gtv__ovk = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    nrtf__kzm = []
    mbr__fxbhs = set()
    for bkh__jbi in type_usecol_offset:
        if gtv__ovk[bkh__jbi] not in partition_names:
            nrtf__kzm.append(col_indices[bkh__jbi])
        else:
            mbr__fxbhs.add(col_indices[bkh__jbi])
    if index_column_index is not None:
        nrtf__kzm.append(index_column_index)
    nrtf__kzm = sorted(nrtf__kzm)

    def is_nullable(typ):
        return bodo.utils.utils.is_array_typ(typ, False) and not isinstance(typ
            , types.Array)
    zohqv__bhx = [(int(is_nullable(out_types[col_indices.index(onumd__ewcd)
        ])) if onumd__ewcd != index_column_index else int(is_nullable(
        index_column_type))) for onumd__ewcd in nrtf__kzm]
    akwi__qtik = []
    wtzuu__ucekx = []
    acupp__kvhzr = []
    for bkh__jbi, mjv__jvh in enumerate(partition_names):
        try:
            tue__aengt = gtv__ovk.index(mjv__jvh)
            if col_indices[tue__aengt] not in mbr__fxbhs:
                continue
        except ValueError as wxxog__ekpww:
            continue
        akwi__qtik.append(mjv__jvh)
        wtzuu__ucekx.append(bkh__jbi)
        knga__jmc = out_types[tue__aengt].dtype
        hitqd__gefi = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            knga__jmc)
        acupp__kvhzr.append(numba_to_c_type(hitqd__gefi))
    pcaf__gygy += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    if len(wtzuu__ucekx) > 0:
        pcaf__gygy += f"""    out_table = pq_read(fname_py, {is_parallel}, unicode_to_utf8(bucket_region), dnf_filters, expr_filters, storage_options_py, {ujz__hqwmu}, selected_cols_arr_{lqqqo__rictv}.ctypes, {len(nrtf__kzm)}, nullable_cols_arr_{lqqqo__rictv}.ctypes, np.array({wtzuu__ucekx}, dtype=np.int32).ctypes, np.array({acupp__kvhzr}, dtype=np.int32).ctypes, {len(wtzuu__ucekx)}, total_rows_np.ctypes)
"""
    else:
        pcaf__gygy += f"""    out_table = pq_read(fname_py, {is_parallel}, unicode_to_utf8(bucket_region), dnf_filters, expr_filters, storage_options_py, {ujz__hqwmu}, selected_cols_arr_{lqqqo__rictv}.ctypes, {len(nrtf__kzm)}, nullable_cols_arr_{lqqqo__rictv}.ctypes, 0, 0, 0, total_rows_np.ctypes)
"""
    pcaf__gygy += '    check_and_propagate_cpp_exception()\n'
    ryfp__iyrnt = 'None'
    qnfn__atwsy = index_column_type
    omsnz__zfzmn = TableType(tuple(out_types))
    if msr__drd:
        omsnz__zfzmn = types.none
    if index_column_index is not None:
        xjpv__exdcj = nrtf__kzm.index(index_column_index)
        ryfp__iyrnt = (
            f'info_to_array(info_from_table(out_table, {xjpv__exdcj}), index_arr_type)'
            )
    pcaf__gygy += f'    index_arr = {ryfp__iyrnt}\n'
    if msr__drd:
        zhl__fem = None
    else:
        zhl__fem = []
        fxvkm__bcqpd = 0
        for bkh__jbi, kzvg__iulhc in enumerate(col_indices):
            if fxvkm__bcqpd < len(type_usecol_offset
                ) and bkh__jbi == type_usecol_offset[fxvkm__bcqpd]:
                cykc__rwyf = col_indices[bkh__jbi]
                if cykc__rwyf in mbr__fxbhs:
                    oduh__mgj = gtv__ovk[bkh__jbi]
                    zhl__fem.append(len(nrtf__kzm) + akwi__qtik.index(
                        oduh__mgj))
                else:
                    zhl__fem.append(nrtf__kzm.index(kzvg__iulhc))
                fxvkm__bcqpd += 1
            else:
                zhl__fem.append(-1)
        zhl__fem = np.array(zhl__fem, dtype=np.int64)
    if msr__drd:
        pcaf__gygy += '    T = None\n'
    else:
        pcaf__gygy += f"""    T = cpp_table_to_py_table(out_table, table_idx_{lqqqo__rictv}, py_table_type_{lqqqo__rictv})
"""
    pcaf__gygy += '    delete_table(out_table)\n'
    pcaf__gygy += f'    total_rows = total_rows_np[0]\n'
    pcaf__gygy += f'    ev.finalize()\n'
    pcaf__gygy += '    return (total_rows, T, index_arr)\n'
    oplhb__gjrn = {}
    noaq__woox = {f'py_table_type_{lqqqo__rictv}': omsnz__zfzmn,
        f'table_idx_{lqqqo__rictv}': zhl__fem,
        f'selected_cols_arr_{lqqqo__rictv}': np.array(nrtf__kzm, np.int32),
        f'nullable_cols_arr_{lqqqo__rictv}': np.array(zohqv__bhx, np.int32),
        'index_arr_type': qnfn__atwsy, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(pcaf__gygy, noaq__woox, oplhb__gjrn)
    uju__ovv = oplhb__gjrn['pq_reader_py']
    salu__iiu = numba.njit(uju__ovv, no_cpython_wrapper=True)
    return salu__iiu


def _get_numba_typ_from_pa_typ(pa_typ, is_index, nullable_from_metadata,
    category_info):
    import pyarrow as pa
    if isinstance(pa_typ.type, pa.ListType):
        return ArrayItemArrayType(_get_numba_typ_from_pa_typ(pa_typ.type.
            value_field, is_index, nullable_from_metadata, category_info))
    if isinstance(pa_typ.type, pa.StructType):
        pqacv__clwm = []
        oxvyc__zxpa = []
        for djeb__cxv in pa_typ.flatten():
            oxvyc__zxpa.append(djeb__cxv.name.split('.')[-1])
            pqacv__clwm.append(_get_numba_typ_from_pa_typ(djeb__cxv,
                is_index, nullable_from_metadata, category_info))
        return StructArrayType(tuple(pqacv__clwm), tuple(oxvyc__zxpa))
    if isinstance(pa_typ.type, pa.Decimal128Type):
        return DecimalArrayType(pa_typ.type.precision, pa_typ.type.scale)
    vqdz__mjca = {pa.bool_(): types.bool_, pa.int8(): types.int8, pa.int16(
        ): types.int16, pa.int32(): types.int32, pa.int64(): types.int64,
        pa.uint8(): types.uint8, pa.uint16(): types.uint16, pa.uint32():
        types.uint32, pa.uint64(): types.uint64, pa.float32(): types.
        float32, pa.float64(): types.float64, pa.string(): string_type, pa.
        binary(): bytes_type, pa.date32(): datetime_date_type, pa.date64():
        types.NPDatetime('ns'), pa.timestamp('ns'): types.NPDatetime('ns'),
        pa.timestamp('us'): types.NPDatetime('ns'), pa.timestamp('ms'):
        types.NPDatetime('ns'), pa.timestamp('s'): types.NPDatetime('ns'),
        null(): string_type}
    if isinstance(pa_typ.type, pa.DictionaryType):
        if pa_typ.type.value_type != pa.string():
            raise BodoError(
                f'Parquet Categorical data type should be string, not {pa_typ.type.value_type}'
                )
        rzfio__vmf = vqdz__mjca[pa_typ.type.index_type]
        yapg__ckh = PDCategoricalDtype(category_info[pa_typ.name], bodo.
            string_type, pa_typ.type.ordered, int_type=rzfio__vmf)
        return CategoricalArrayType(yapg__ckh)
    if pa_typ.type not in vqdz__mjca:
        raise BodoError('Arrow data type {} not supported yet'.format(
            pa_typ.type))
    lerbe__cgc = vqdz__mjca[pa_typ.type]
    if lerbe__cgc == datetime_date_type:
        return datetime_date_array_type
    if lerbe__cgc == bytes_type:
        return binary_array_type
    qfj__oec = string_array_type if lerbe__cgc == string_type else types.Array(
        lerbe__cgc, 1, 'C')
    if lerbe__cgc == types.bool_:
        qfj__oec = boolean_array
    if nullable_from_metadata is not None:
        ntou__exy = nullable_from_metadata
    else:
        ntou__exy = use_nullable_int_arr
    if ntou__exy and not is_index and isinstance(lerbe__cgc, types.Integer
        ) and pa_typ.nullable:
        qfj__oec = IntegerArrayType(lerbe__cgc)
    return qfj__oec


def is_filter_pushdown_disabled_fpath(fpath):
    return fpath.startswith('gs://') or fpath.startswith('gcs://'
        ) or fpath.startswith('hdfs://') or fpath.startswith('abfs://'
        ) or fpath.startswith('abfss://')


def get_parquet_dataset(fpath, get_row_counts=True, dnf_filters=None,
    expr_filters=None, storage_options=None, read_categories=False,
    is_parallel=False):
    if get_row_counts:
        iauu__fbwyp = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    tsea__myrze = MPI.COMM_WORLD
    if isinstance(fpath, list):
        jqrhj__nlkku = urlparse(fpath[0])
        mmfn__qmc = jqrhj__nlkku.scheme
        hjxc__otk = jqrhj__nlkku.netloc
        for bkh__jbi in range(len(fpath)):
            ducy__znogs = fpath[bkh__jbi]
            rkuvk__kkb = urlparse(ducy__znogs)
            if rkuvk__kkb.scheme != mmfn__qmc:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if rkuvk__kkb.netloc != hjxc__otk:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[bkh__jbi] = ducy__znogs.rstrip('/')
    else:
        jqrhj__nlkku = urlparse(fpath)
        mmfn__qmc = jqrhj__nlkku.scheme
        fpath = fpath.rstrip('/')
    if mmfn__qmc in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as wxxog__ekpww:
            fmli__egxh = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(fmli__egxh)
    if mmfn__qmc == 'http':
        try:
            import fsspec
        except ImportError as wxxog__ekpww:
            fmli__egxh = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
"""
    dqt__rhda = []

    def getfs(parallel=False):
        if len(dqt__rhda) == 1:
            return dqt__rhda[0]
        if mmfn__qmc == 's3':
            dqt__rhda.append(get_s3_fs_from_path(fpath, parallel=parallel,
                storage_options=storage_options) if not isinstance(fpath,
                list) else get_s3_fs_from_path(fpath[0], parallel=parallel,
                storage_options=storage_options))
        elif mmfn__qmc in {'gcs', 'gs'}:
            ualuq__jlkj = gcsfs.GCSFileSystem(token=None)
            dqt__rhda.append(ualuq__jlkj)
        elif mmfn__qmc == 'http':
            dqt__rhda.append(fsspec.filesystem('http'))
        elif mmfn__qmc in {'hdfs', 'abfs', 'abfss'}:
            dqt__rhda.append(get_hdfs_fs(fpath) if not isinstance(fpath,
                list) else get_hdfs_fs(fpath[0]))
        else:
            dqt__rhda.append(None)
        return dqt__rhda[0]
    xtoae__cov = False
    if get_row_counts:
        tgss__hfnk = getfs(parallel=True)
        xtoae__cov = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        qxmwj__akdbs = 1
        mzjf__igaxx = os.cpu_count()
        if mzjf__igaxx is not None and mzjf__igaxx > 1:
            qxmwj__akdbs = mzjf__igaxx // 2
        try:
            if get_row_counts:
                qaq__tra = tracing.Event('pq.ParquetDataset', is_parallel=False
                    )
                if tracing.is_tracing():
                    qaq__tra.add_attribute('dnf_filter', str(dnf_filters))
            kax__hqvy = pa.io_thread_count()
            pa.set_io_thread_count(qxmwj__akdbs)
            uxq__svvkp = pq.ParquetDataset(fpath, filesystem=getfs(),
                filters=None, use_legacy_dataset=True, validate_schema=
                False, metadata_nthreads=qxmwj__akdbs)
            pa.set_io_thread_count(kax__hqvy)
            azog__owuhs = bodo.io.pa_parquet.get_dataset_schema(uxq__svvkp)
            if dnf_filters:
                if get_row_counts:
                    qaq__tra.add_attribute('num_pieces_before_filter', len(
                        uxq__svvkp.pieces))
                ckic__gply = time.time()
                uxq__svvkp._filter(dnf_filters)
                if get_row_counts:
                    qaq__tra.add_attribute('dnf_filter_time', time.time() -
                        ckic__gply)
                    qaq__tra.add_attribute('num_pieces_after_filter', len(
                        uxq__svvkp.pieces))
            if get_row_counts:
                qaq__tra.finalize()
            uxq__svvkp._metadata.fs = None
        except Exception as wugx__ajl:
            tsea__myrze.bcast(wugx__ajl)
            raise BodoError(
                f'error from pyarrow: {type(wugx__ajl).__name__}: {str(wugx__ajl)}\n'
                )
        if get_row_counts:
            rfbox__whtk = tracing.Event('bcast dataset')
        tsea__myrze.bcast(uxq__svvkp)
        tsea__myrze.bcast(azog__owuhs)
    else:
        if get_row_counts:
            rfbox__whtk = tracing.Event('bcast dataset')
        uxq__svvkp = tsea__myrze.bcast(None)
        if isinstance(uxq__svvkp, Exception):
            xkh__jhuwn = uxq__svvkp
            raise BodoError(
                f'error from pyarrow: {type(xkh__jhuwn).__name__}: {str(xkh__jhuwn)}\n'
                )
        azog__owuhs = tsea__myrze.bcast(None)
    if get_row_counts:
        rfbox__whtk.finalize()
    uxq__svvkp._bodo_total_rows = 0
    if get_row_counts or xtoae__cov:
        if get_row_counts and tracing.is_tracing():
            onc__jarl = tracing.Event('get_row_counts')
            onc__jarl.add_attribute('g_num_pieces', len(uxq__svvkp.pieces))
            onc__jarl.add_attribute('g_expr_filters', str(expr_filters))
        yvftv__pkgfo = 0.0
        num_pieces = len(uxq__svvkp.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        eavh__nwb = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        fmrhy__urhn = 0
        wxku__qzuic = 0
        ogcw__uhh = True
        uxq__svvkp._metadata.fs = getfs()
        if expr_filters is not None:
            import random
            random.seed(37)
            pcxx__xwn = random.sample(uxq__svvkp.pieces, k=len(uxq__svvkp.
                pieces))
        else:
            pcxx__xwn = uxq__svvkp.pieces
        for rpoea__gfxw in pcxx__xwn:
            rpoea__gfxw._bodo_num_rows = 0
        if mmfn__qmc in {'gcs', 'gs', 'hdfs', 'abfs', 'abfss'}:
            for rpoea__gfxw in pcxx__xwn[start:eavh__nwb]:
                nhvd__pwejc = rpoea__gfxw.get_metadata()
                if get_row_counts:
                    if expr_filters is not None:
                        pa.set_io_thread_count(2)
                        pa.set_cpu_count(2)
                        ckic__gply = time.time()
                        rclgz__uspl = ds.dataset(rpoea__gfxw.path,
                            partitioning=ds.partitioning(flavor='hive')
                            ).scanner(filter=expr_filters, use_threads=True,
                            use_async=True).count_rows()
                        yvftv__pkgfo += time.time() - ckic__gply
                    else:
                        rclgz__uspl = nhvd__pwejc.num_rows
                    rpoea__gfxw._bodo_num_rows = rclgz__uspl
                    fmrhy__urhn += rclgz__uspl
                    wxku__qzuic += nhvd__pwejc.num_row_groups
                if xtoae__cov:
                    axihy__zmi = nhvd__pwejc.schema.to_arrow_schema()
                    if azog__owuhs != axihy__zmi:
                        print(
                            'Schema in {!s} was different. \n{!s}\n\nvs\n\n{!s}'
                            .format(rpoea__gfxw, axihy__zmi, azog__owuhs))
                        ogcw__uhh = False
                        break
        else:
            fpaths = [rpoea__gfxw.path for rpoea__gfxw in pcxx__xwn[start:
                eavh__nwb]]
            if mmfn__qmc == 's3':
                hjxc__otk = jqrhj__nlkku.netloc
                wtvqx__qol = 's3://' + hjxc__otk + '/'
                fpaths = [ducy__znogs[len(wtvqx__qol):] for ducy__znogs in
                    fpaths]
                yyarx__mlci = get_s3_subtree_fs(hjxc__otk, region=getfs().
                    region, storage_options=storage_options)
            else:
                yyarx__mlci = None
            pa.set_io_thread_count(4)
            pa.set_cpu_count(4)
            clnb__djz = ds.dataset(fpaths, filesystem=yyarx__mlci,
                partitioning=ds.partitioning(flavor='hive'))
            for qwkj__cioe, pgxsk__usiob in zip(pcxx__xwn[start:eavh__nwb],
                clnb__djz.get_fragments()):
                ckic__gply = time.time()
                rclgz__uspl = pgxsk__usiob.scanner(schema=clnb__djz.schema,
                    filter=expr_filters, use_threads=True, use_async=True
                    ).count_rows()
                yvftv__pkgfo += time.time() - ckic__gply
                qwkj__cioe._bodo_num_rows = rclgz__uspl
                fmrhy__urhn += rclgz__uspl
                wxku__qzuic += pgxsk__usiob.num_row_groups
                if xtoae__cov:
                    axihy__zmi = pgxsk__usiob.metadata.schema.to_arrow_schema()
                    if azog__owuhs != axihy__zmi:
                        print(
                            'Schema in {!s} was different. \n{!s}\n\nvs\n\n{!s}'
                            .format(qwkj__cioe, axihy__zmi, azog__owuhs))
                        ogcw__uhh = False
                        break
        if xtoae__cov:
            ogcw__uhh = tsea__myrze.allreduce(ogcw__uhh, op=MPI.LAND)
            if not ogcw__uhh:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            uxq__svvkp._bodo_total_rows = tsea__myrze.allreduce(fmrhy__urhn,
                op=MPI.SUM)
            rieql__gezgo = tsea__myrze.allreduce(wxku__qzuic, op=MPI.SUM)
            xfrfw__fzzx = np.array([rpoea__gfxw._bodo_num_rows for
                rpoea__gfxw in uxq__svvkp.pieces])
            xfrfw__fzzx = tsea__myrze.allreduce(xfrfw__fzzx, op=MPI.SUM)
            for rpoea__gfxw, tnxp__qzg in zip(uxq__svvkp.pieces, xfrfw__fzzx):
                rpoea__gfxw._bodo_num_rows = tnxp__qzg
            if is_parallel and bodo.get_rank(
                ) == 0 and rieql__gezgo < bodo.get_size():
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({rieql__gezgo}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()})
"""
                    ))
            if tracing.is_tracing():
                onc__jarl.add_attribute('g_total_num_row_groups', rieql__gezgo)
                if expr_filters is not None:
                    onc__jarl.add_attribute('total_scan_time', yvftv__pkgfo)
                ilepk__tji = np.array([rpoea__gfxw._bodo_num_rows for
                    rpoea__gfxw in uxq__svvkp.pieces])
                gqa__lfuv = np.percentile(ilepk__tji, [25, 50, 75])
                onc__jarl.add_attribute('g_row_counts_min', ilepk__tji.min())
                onc__jarl.add_attribute('g_row_counts_Q1', gqa__lfuv[0])
                onc__jarl.add_attribute('g_row_counts_median', gqa__lfuv[1])
                onc__jarl.add_attribute('g_row_counts_Q3', gqa__lfuv[2])
                onc__jarl.add_attribute('g_row_counts_max', ilepk__tji.max())
                onc__jarl.add_attribute('g_row_counts_mean', ilepk__tji.mean())
                onc__jarl.add_attribute('g_row_counts_std', ilepk__tji.std())
                onc__jarl.add_attribute('g_row_counts_sum', ilepk__tji.sum())
                onc__jarl.finalize()
    uxq__svvkp._prefix = ''
    if mmfn__qmc == 'hdfs':
        wtvqx__qol = f'{mmfn__qmc}://{jqrhj__nlkku.netloc}'
        if len(uxq__svvkp.pieces) > 0:
            qwkj__cioe = uxq__svvkp.pieces[0]
            if not qwkj__cioe.path.startswith(wtvqx__qol):
                uxq__svvkp._prefix = wtvqx__qol
    if read_categories:
        _add_categories_to_pq_dataset(uxq__svvkp)
    if get_row_counts:
        iauu__fbwyp.finalize()
    return uxq__svvkp


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, storage_options, region):
    import pyarrow as pa
    mzjf__igaxx = os.cpu_count()
    if mzjf__igaxx is None or mzjf__igaxx == 0:
        mzjf__igaxx = 2
    hdiji__rkjy = min(4, mzjf__igaxx)
    bvsg__pqb = min(16, mzjf__igaxx)
    if is_parallel and len(fpaths) > bvsg__pqb and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(bvsg__pqb)
        pa.set_cpu_count(bvsg__pqb)
    else:
        pa.set_io_thread_count(hdiji__rkjy)
        pa.set_cpu_count(hdiji__rkjy)
    if fpaths[0].startswith('s3://'):
        hjxc__otk = urlparse(fpaths[0]).netloc
        wtvqx__qol = 's3://' + hjxc__otk + '/'
        fpaths = [ducy__znogs[len(wtvqx__qol):] for ducy__znogs in fpaths]
        yyarx__mlci = get_s3_subtree_fs(hjxc__otk, region=region,
            storage_options=storage_options)
    else:
        yyarx__mlci = None
    uxq__svvkp = ds.dataset(fpaths, filesystem=yyarx__mlci, partitioning=ds
        .partitioning(flavor='hive'))
    col_names = uxq__svvkp.schema.names
    qqwry__xngs = [col_names[tbsn__cpjl] for tbsn__cpjl in selected_fields]
    return uxq__svvkp.scanner(columns=qqwry__xngs, filter=expr_filters,
        use_threads=True, use_async=True).to_reader()


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    lvbqr__dokcu = pq_dataset.schema.to_arrow_schema()
    cckbf__vyg = [c for c in lvbqr__dokcu.names if isinstance(lvbqr__dokcu.
        field(c).type, pa.DictionaryType)]
    if len(cckbf__vyg) == 0:
        pq_dataset._category_info = {}
        return
    tsea__myrze = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            yqgft__zywq = pq_dataset.pieces[0].open()
            kiuo__tavgq = yqgft__zywq.read_row_group(0, cckbf__vyg)
            category_info = {c: tuple(kiuo__tavgq.column(c).chunk(0).
                dictionary.to_pylist()) for c in cckbf__vyg}
            del yqgft__zywq, kiuo__tavgq
        except Exception as wugx__ajl:
            tsea__myrze.bcast(wugx__ajl)
            raise wugx__ajl
        tsea__myrze.bcast(category_info)
    else:
        category_info = tsea__myrze.bcast(None)
        if isinstance(category_info, Exception):
            xkh__jhuwn = category_info
            raise xkh__jhuwn
    pq_dataset._category_info = category_info


def get_pandas_metadata(schema, num_pieces):
    dpvi__jbeju = None
    nullable_from_metadata = defaultdict(lambda : None)
    ida__jbo = b'pandas'
    if schema.metadata is not None and ida__jbo in schema.metadata:
        import json
        vkohh__byndp = json.loads(schema.metadata[ida__jbo].decode('utf8'))
        xcu__nmfk = len(vkohh__byndp['index_columns'])
        if xcu__nmfk > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        dpvi__jbeju = vkohh__byndp['index_columns'][0] if xcu__nmfk else None
        if not isinstance(dpvi__jbeju, str) and (not isinstance(dpvi__jbeju,
            dict) or num_pieces != 1):
            dpvi__jbeju = None
        for wnda__xnkl in vkohh__byndp['columns']:
            pkc__fcf = wnda__xnkl['name']
            if wnda__xnkl['pandas_type'].startswith('int'
                ) and pkc__fcf is not None:
                if wnda__xnkl['numpy_type'].startswith('Int'):
                    nullable_from_metadata[pkc__fcf] = True
                else:
                    nullable_from_metadata[pkc__fcf] = False
    return dpvi__jbeju, nullable_from_metadata


def parquet_file_schema(file_name, selected_columns, storage_options=None):
    col_names = []
    zwkye__akep = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = [] if pq_dataset.partitions is None else [pq_dataset.
        partitions.levels[bkh__jbi].name for bkh__jbi in range(len(
        pq_dataset.partitions.partition_names))]
    lvbqr__dokcu = pq_dataset.schema.to_arrow_schema()
    num_pieces = len(pq_dataset.pieces)
    col_names = lvbqr__dokcu.names
    dpvi__jbeju, nullable_from_metadata = get_pandas_metadata(lvbqr__dokcu,
        num_pieces)
    qjrul__gpb = [_get_numba_typ_from_pa_typ(lvbqr__dokcu.field(c), c ==
        dpvi__jbeju, nullable_from_metadata[c], pq_dataset._category_info) for
        c in col_names]
    if partition_names:
        col_names += partition_names
        qjrul__gpb += [_get_partition_cat_dtype(pq_dataset.partitions.
            levels[bkh__jbi]) for bkh__jbi in range(len(partition_names))]
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in col_names:
            raise BodoError('Selected column {} not in Parquet file schema'
                .format(c))
    if dpvi__jbeju and not isinstance(dpvi__jbeju, dict
        ) and dpvi__jbeju not in selected_columns:
        selected_columns.append(dpvi__jbeju)
    col_indices = [col_names.index(c) for c in selected_columns]
    zwkye__akep = [qjrul__gpb[col_names.index(c)] for c in selected_columns]
    col_names = selected_columns
    return col_names, zwkye__akep, dpvi__jbeju, col_indices, partition_names


def _get_partition_cat_dtype(part_set):
    dye__lhquk = part_set.dictionary.to_pandas()
    mmdzz__umup = bodo.typeof(dye__lhquk).dtype
    yapg__ckh = PDCategoricalDtype(tuple(dye__lhquk), mmdzz__umup, False)
    return CategoricalArrayType(yapg__ckh)


_pq_read = types.ExternalFunction('pq_read', table_type(
    read_parquet_fpath_type, types.boolean, types.voidptr,
    parquet_predicate_type, parquet_predicate_type,
    storage_options_dict_type, types.int64, types.voidptr, types.int32,
    types.voidptr, types.voidptr, types.voidptr, types.int32, types.voidptr))
from llvmlite import ir as lir
from numba.core import cgutils
if bodo.utils.utils.has_pyarrow():
    from bodo.io import arrow_cpp
    ll.add_symbol('pq_read', arrow_cpp.pq_read)
    ll.add_symbol('pq_write', arrow_cpp.pq_write)
    ll.add_symbol('pq_write_partitioned', arrow_cpp.pq_write_partitioned)


@intrinsic
def parquet_write_table_cpp(typingctx, filename_t, table_t, col_names_t,
    index_t, write_index, metadata_t, compression_t, is_parallel_t,
    write_range_index, start, stop, step, name, bucket_region):

    def codegen(context, builder, sig, args):
        bdfbn__rfl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer()])
        atzj__ocwj = cgutils.get_or_insert_function(builder.module,
            bdfbn__rfl, name='pq_write')
        builder.call(atzj__ocwj, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, table_t, col_names_t, index_t, types.
        boolean, types.voidptr, types.voidptr, types.boolean, types.boolean,
        types.int32, types.int32, types.int32, types.voidptr, types.voidptr
        ), codegen


@intrinsic
def parquet_write_table_partitioned_cpp(typingctx, filename_t, data_table_t,
    col_names_t, col_names_no_partitions_t, cat_table_t, part_col_idxs_t,
    num_part_col_t, compression_t, is_parallel_t, bucket_region):

    def codegen(context, builder, sig, args):
        bdfbn__rfl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer()])
        atzj__ocwj = cgutils.get_or_insert_function(builder.module,
            bdfbn__rfl, name='pq_write_partitioned')
        builder.call(atzj__ocwj, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr), codegen
