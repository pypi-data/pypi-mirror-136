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
        except OSError as aoey__ckbn:
            if 'non-file path' in str(aoey__ckbn):
                raise FileNotFoundError(str(aoey__ckbn))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=None):
        qme__wqxkq = lhs.scope
        jrwd__iywu = lhs.loc
        qwwmk__qxm = None
        if lhs.name in self.locals:
            qwwmk__qxm = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        fjyox__grhe = {}
        if lhs.name + ':convert' in self.locals:
            fjyox__grhe = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if qwwmk__qxm is None:
            ztpc__oqi = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/source/programming_with_bodo/file_io.html#non-constant-filepaths'
                )
            iet__puix = get_const_value(file_name, self.func_ir, ztpc__oqi,
                arg_types=self.args, file_info=ParquetFileInfo(columns,
                storage_options=storage_options))
            pgsvw__jqgtm = False
            jck__ocwlb = guard(get_definition, self.func_ir, file_name)
            if isinstance(jck__ocwlb, ir.Arg):
                typ = self.args[jck__ocwlb.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, vsnj__dmjh, ootcg__znune, col_indices,
                        partition_names) = typ.schema
                    pgsvw__jqgtm = True
            if not pgsvw__jqgtm:
                (col_names, vsnj__dmjh, ootcg__znune, col_indices,
                    partition_names) = (parquet_file_schema(iet__puix,
                    columns, storage_options=storage_options))
        else:
            fdz__cyezx = list(qwwmk__qxm.keys())
            dje__xxe = [npwq__oqrjl for npwq__oqrjl in qwwmk__qxm.values()]
            ootcg__znune = 'index' if 'index' in fdz__cyezx else None
            if columns is None:
                selected_columns = fdz__cyezx
            else:
                selected_columns = columns
            col_indices = [fdz__cyezx.index(c) for c in selected_columns]
            vsnj__dmjh = [dje__xxe[fdz__cyezx.index(c)] for c in
                selected_columns]
            col_names = selected_columns
            ootcg__znune = ootcg__znune if ootcg__znune in col_names else None
            partition_names = []
        ufop__wsvuc = None if isinstance(ootcg__znune, dict
            ) or ootcg__znune is None else ootcg__znune
        index_column_index = None
        index_column_type = types.none
        if ufop__wsvuc:
            ayx__jlnxv = col_names.index(ufop__wsvuc)
            col_indices = col_indices.copy()
            vsnj__dmjh = vsnj__dmjh.copy()
            index_column_index = col_indices.pop(ayx__jlnxv)
            index_column_type = vsnj__dmjh.pop(ayx__jlnxv)
        for oxm__webm, c in enumerate(col_names):
            if c in fjyox__grhe:
                vsnj__dmjh[oxm__webm] = fjyox__grhe[c]
        oakb__hqrj = [ir.Var(qme__wqxkq, mk_unique_var('pq_table'),
            jrwd__iywu), ir.Var(qme__wqxkq, mk_unique_var('pq_index'),
            jrwd__iywu)]
        ohzdw__wmbws = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.
            name, col_names, col_indices, vsnj__dmjh, oakb__hqrj,
            jrwd__iywu, partition_names, storage_options,
            index_column_index, index_column_type)]
        return (col_names, oakb__hqrj, ootcg__znune, ohzdw__wmbws,
            vsnj__dmjh, index_column_type)


def determine_filter_cast(pq_node, typemap, filter_val):
    wetu__lghv = filter_val[0]
    bqvx__szx = pq_node.original_out_types[pq_node.original_df_colnames.
        index(wetu__lghv)]
    daihy__bcu = bodo.utils.typing.element_type(bqvx__szx)
    if wetu__lghv in pq_node.partition_names:
        if daihy__bcu == types.unicode_type:
            yqx__iflq = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(daihy__bcu, types.Integer):
            yqx__iflq = f'.cast(pyarrow.{daihy__bcu.name}(), safe=False)'
        else:
            yqx__iflq = ''
    else:
        yqx__iflq = ''
    rhsc__apj = typemap[filter_val[2].name]
    if not bodo.utils.typing.is_common_scalar_dtype([daihy__bcu, rhsc__apj]):
        if not bodo.utils.typing.is_safe_arrow_cast(daihy__bcu, rhsc__apj):
            raise BodoError(
                f'Unsupport Arrow cast from {daihy__bcu} to {rhsc__apj} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if daihy__bcu == types.unicode_type:
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif daihy__bcu in (bodo.datetime64ns, bodo.pd_timestamp_type):
            return yqx__iflq, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return yqx__iflq, ''


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    ocrc__kgji = len(pq_node.out_vars)
    extra_args = ''
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    mmyzp__pouit, anf__wom = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    if mmyzp__pouit:
        uizom__yis = []
        jjq__pxqz = []
        wykzt__ajwm = False
        zuiq__uly = None
        for fnhv__uawtq in pq_node.filters:
            jzcxi__fcwo = []
            hdn__zcg = []
            rfv__ufe = set()
            for njm__ywx in fnhv__uawtq:
                if isinstance(njm__ywx[2], ir.Var):
                    pci__mtjt, mhsi__rhvsg = determine_filter_cast(pq_node,
                        typemap, njm__ywx)
                    hdn__zcg.append(
                        f"(ds.field('{njm__ywx[0]}'){pci__mtjt} {njm__ywx[1]} ds.scalar({mmyzp__pouit[njm__ywx[2].name]}){mhsi__rhvsg})"
                        )
                else:
                    assert njm__ywx[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if njm__ywx[1] == 'is not':
                        fercx__inc = '~'
                    else:
                        fercx__inc = ''
                    hdn__zcg.append(
                        f"({fercx__inc}ds.field('{njm__ywx[0]}').is_null())")
                if njm__ywx[0] in pq_node.partition_names and isinstance(
                    njm__ywx[2], ir.Var):
                    ldcw__wnwuq = (
                        f"('{njm__ywx[0]}', '{njm__ywx[1]}', {mmyzp__pouit[njm__ywx[2].name]})"
                        )
                    jzcxi__fcwo.append(ldcw__wnwuq)
                    rfv__ufe.add(ldcw__wnwuq)
                else:
                    wykzt__ajwm = True
            if zuiq__uly is None:
                zuiq__uly = rfv__ufe
            else:
                zuiq__uly.intersection_update(rfv__ufe)
            jkmr__clhwg = ', '.join(jzcxi__fcwo)
            wilu__vsh = ' & '.join(hdn__zcg)
            if jkmr__clhwg:
                uizom__yis.append(f'[{jkmr__clhwg}]')
            jjq__pxqz.append(f'({wilu__vsh})')
        exiro__wjer = ', '.join(uizom__yis)
        rac__gczoz = ' | '.join(jjq__pxqz)
        if wykzt__ajwm:
            if zuiq__uly:
                kknk__tyj = sorted(zuiq__uly)
                dnf_filter_str = f"[[{', '.join(kknk__tyj)}]]"
        elif exiro__wjer:
            dnf_filter_str = f'[{exiro__wjer}]'
        expr_filter_str = f'({rac__gczoz})'
        extra_args = ', '.join(mmyzp__pouit.values())
    fuf__qhe = ', '.join(f'out{oxm__webm}' for oxm__webm in range(ocrc__kgji))
    tbzsd__dvcp = f'def pq_impl(fname, {extra_args}):\n'
    tbzsd__dvcp += (
        f'    (total_rows, {fuf__qhe},) = _pq_reader_py(fname, {extra_args})\n'
        )
    hpq__zaut = {}
    exec(tbzsd__dvcp, {}, hpq__zaut)
    mme__jnttv = hpq__zaut['pq_impl']
    parallel = False
    if array_dists is not None:
        ppqb__taae = pq_node.out_vars[0].name
        parallel = array_dists[ppqb__taae] in (distributed_pass.
            Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        apkqs__dzmd = pq_node.out_vars[1].name
        assert typemap[apkqs__dzmd
            ] == types.none or not parallel or array_dists[apkqs__dzmd] in (
            distributed_pass.Distribution.OneD, distributed_pass.
            Distribution.OneD_Var
            ), 'pq data/index parallelization does not match'
    ftd__dijht = _gen_pq_reader_py(pq_node.df_colnames, pq_node.col_indices,
        pq_node.type_usecol_offset, pq_node.out_types, pq_node.
        storage_options, pq_node.partition_names, dnf_filter_str,
        expr_filter_str, extra_args, parallel, meta_head_only_info, pq_node
        .index_column_index, pq_node.index_column_type)
    bie__gupsw = typemap[pq_node.file_name.name]
    bwfe__nfqzl = (bie__gupsw,) + tuple(typemap[njm__ywx.name] for njm__ywx in
        anf__wom)
    jlv__snwac = compile_to_numba_ir(mme__jnttv, {'_pq_reader_py':
        ftd__dijht}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        bwfe__nfqzl, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(jlv__snwac, [pq_node.file_name] + anf__wom)
    ohzdw__wmbws = jlv__snwac.body[:-3]
    if meta_head_only_info:
        ohzdw__wmbws[-1 - ocrc__kgji].target = meta_head_only_info[1]
    ohzdw__wmbws[-2].target = pq_node.out_vars[0]
    ohzdw__wmbws[-1].target = pq_node.out_vars[1]
    return ohzdw__wmbws


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    qtrzc__gffk = get_overload_const_str(dnf_filter_str)
    jmjc__mrcuz = get_overload_const_str(expr_filter_str)
    qpj__woo = ', '.join(f'f{oxm__webm}' for oxm__webm in range(len(var_tup)))
    tbzsd__dvcp = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        tbzsd__dvcp += f'  {qpj__woo}, = var_tup\n'
    tbzsd__dvcp += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    tbzsd__dvcp += f'    dnf_filters_py = {qtrzc__gffk}\n'
    tbzsd__dvcp += f'    expr_filters_py = {jmjc__mrcuz}\n'
    tbzsd__dvcp += '  return (dnf_filters_py, expr_filters_py)\n'
    hpq__zaut = {}
    exec(tbzsd__dvcp, globals(), hpq__zaut)
    return hpq__zaut['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def get_storage_options_pyobject(storage_options):
    pass


@overload(get_storage_options_pyobject, no_unliteral=True)
def overload_get_storage_options_pyobject(storage_options):
    aoj__xyyt = get_overload_constant_dict(storage_options)
    tbzsd__dvcp = 'def impl(storage_options):\n'
    tbzsd__dvcp += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    tbzsd__dvcp += f'    storage_options_py = {str(aoj__xyyt)}\n'
    tbzsd__dvcp += '  return storage_options_py\n'
    hpq__zaut = {}
    exec(tbzsd__dvcp, globals(), hpq__zaut)
    return hpq__zaut['impl']


def _gen_pq_reader_py(col_names, col_indices, type_usecol_offset, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type):
    zywos__djtlv = next_label()
    ovuri__vuw = ',' if extra_args else ''
    tbzsd__dvcp = f'def pq_reader_py(fname,{extra_args}):\n'
    tbzsd__dvcp += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    tbzsd__dvcp += "    ev.add_attribute('fname', fname)\n"
    tbzsd__dvcp += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={is_parallel})
"""
    tbzsd__dvcp += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{ovuri__vuw}))
"""
    tbzsd__dvcp += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    tbzsd__dvcp += f"""    storage_options_py = get_storage_options_pyobject({str(storage_options)})
"""
    cqa__zvglc = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        cqa__zvglc = meta_head_only_info[0]
    aplwx__rqe = not type_usecol_offset
    urpm__pzgvt = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    mos__lgty = []
    hff__vej = set()
    for oxm__webm in type_usecol_offset:
        if urpm__pzgvt[oxm__webm] not in partition_names:
            mos__lgty.append(col_indices[oxm__webm])
        else:
            hff__vej.add(col_indices[oxm__webm])
    if index_column_index is not None:
        mos__lgty.append(index_column_index)
    mos__lgty = sorted(mos__lgty)

    def is_nullable(typ):
        return bodo.utils.utils.is_array_typ(typ, False) and not isinstance(typ
            , types.Array)
    uxrod__jsa = [(int(is_nullable(out_types[col_indices.index(zsy__cdglf)]
        )) if zsy__cdglf != index_column_index else int(is_nullable(
        index_column_type))) for zsy__cdglf in mos__lgty]
    rmdb__bhanw = []
    quyi__lht = []
    vpby__eezu = []
    for oxm__webm, fheig__yiwl in enumerate(partition_names):
        try:
            lonpw__rtp = urpm__pzgvt.index(fheig__yiwl)
            if col_indices[lonpw__rtp] not in hff__vej:
                continue
        except ValueError as rkhl__lpmum:
            continue
        rmdb__bhanw.append(fheig__yiwl)
        quyi__lht.append(oxm__webm)
        euf__htb = out_types[lonpw__rtp].dtype
        ysb__kgijs = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            euf__htb)
        vpby__eezu.append(numba_to_c_type(ysb__kgijs))
    tbzsd__dvcp += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    if len(quyi__lht) > 0:
        tbzsd__dvcp += f"""    out_table = pq_read(fname_py, {is_parallel}, unicode_to_utf8(bucket_region), dnf_filters, expr_filters, storage_options_py, {cqa__zvglc}, selected_cols_arr_{zywos__djtlv}.ctypes, {len(mos__lgty)}, nullable_cols_arr_{zywos__djtlv}.ctypes, np.array({quyi__lht}, dtype=np.int32).ctypes, np.array({vpby__eezu}, dtype=np.int32).ctypes, {len(quyi__lht)}, total_rows_np.ctypes)
"""
    else:
        tbzsd__dvcp += f"""    out_table = pq_read(fname_py, {is_parallel}, unicode_to_utf8(bucket_region), dnf_filters, expr_filters, storage_options_py, {cqa__zvglc}, selected_cols_arr_{zywos__djtlv}.ctypes, {len(mos__lgty)}, nullable_cols_arr_{zywos__djtlv}.ctypes, 0, 0, 0, total_rows_np.ctypes)
"""
    tbzsd__dvcp += '    check_and_propagate_cpp_exception()\n'
    gad__vtu = 'None'
    nxxhb__olgg = index_column_type
    arc__ulfpw = TableType(tuple(out_types))
    if aplwx__rqe:
        arc__ulfpw = types.none
    if index_column_index is not None:
        enqm__zvvmo = mos__lgty.index(index_column_index)
        gad__vtu = (
            f'info_to_array(info_from_table(out_table, {enqm__zvvmo}), index_arr_type)'
            )
    tbzsd__dvcp += f'    index_arr = {gad__vtu}\n'
    if aplwx__rqe:
        zlv__piqdi = None
    else:
        zlv__piqdi = []
        fzch__mtfwo = 0
        for oxm__webm, een__rlr in enumerate(col_indices):
            if fzch__mtfwo < len(type_usecol_offset
                ) and oxm__webm == type_usecol_offset[fzch__mtfwo]:
                vrmf__xkpk = col_indices[oxm__webm]
                if vrmf__xkpk in hff__vej:
                    gvi__luk = urpm__pzgvt[oxm__webm]
                    zlv__piqdi.append(len(mos__lgty) + rmdb__bhanw.index(
                        gvi__luk))
                else:
                    zlv__piqdi.append(mos__lgty.index(een__rlr))
                fzch__mtfwo += 1
            else:
                zlv__piqdi.append(-1)
        zlv__piqdi = np.array(zlv__piqdi, dtype=np.int64)
    if aplwx__rqe:
        tbzsd__dvcp += '    T = None\n'
    else:
        tbzsd__dvcp += f"""    T = cpp_table_to_py_table(out_table, table_idx_{zywos__djtlv}, py_table_type_{zywos__djtlv})
"""
    tbzsd__dvcp += '    delete_table(out_table)\n'
    tbzsd__dvcp += f'    total_rows = total_rows_np[0]\n'
    tbzsd__dvcp += f'    ev.finalize()\n'
    tbzsd__dvcp += '    return (total_rows, T, index_arr)\n'
    hpq__zaut = {}
    ooxbt__iuxfx = {f'py_table_type_{zywos__djtlv}': arc__ulfpw,
        f'table_idx_{zywos__djtlv}': zlv__piqdi,
        f'selected_cols_arr_{zywos__djtlv}': np.array(mos__lgty, np.int32),
        f'nullable_cols_arr_{zywos__djtlv}': np.array(uxrod__jsa, np.int32),
        'index_arr_type': nxxhb__olgg, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(tbzsd__dvcp, ooxbt__iuxfx, hpq__zaut)
    ftd__dijht = hpq__zaut['pq_reader_py']
    rcr__ulhlo = numba.njit(ftd__dijht, no_cpython_wrapper=True)
    return rcr__ulhlo


def _get_numba_typ_from_pa_typ(pa_typ, is_index, nullable_from_metadata,
    category_info):
    import pyarrow as pa
    if isinstance(pa_typ.type, pa.ListType):
        return ArrayItemArrayType(_get_numba_typ_from_pa_typ(pa_typ.type.
            value_field, is_index, nullable_from_metadata, category_info))
    if isinstance(pa_typ.type, pa.StructType):
        eaavp__whv = []
        hnpum__zlyij = []
        for fit__kjnyq in pa_typ.flatten():
            hnpum__zlyij.append(fit__kjnyq.name.split('.')[-1])
            eaavp__whv.append(_get_numba_typ_from_pa_typ(fit__kjnyq,
                is_index, nullable_from_metadata, category_info))
        return StructArrayType(tuple(eaavp__whv), tuple(hnpum__zlyij))
    if isinstance(pa_typ.type, pa.Decimal128Type):
        return DecimalArrayType(pa_typ.type.precision, pa_typ.type.scale)
    gekwt__duaho = {pa.bool_(): types.bool_, pa.int8(): types.int8, pa.
        int16(): types.int16, pa.int32(): types.int32, pa.int64(): types.
        int64, pa.uint8(): types.uint8, pa.uint16(): types.uint16, pa.
        uint32(): types.uint32, pa.uint64(): types.uint64, pa.float32():
        types.float32, pa.float64(): types.float64, pa.string():
        string_type, pa.binary(): bytes_type, pa.date32():
        datetime_date_type, pa.date64(): types.NPDatetime('ns'), pa.
        timestamp('ns'): types.NPDatetime('ns'), pa.timestamp('us'): types.
        NPDatetime('ns'), pa.timestamp('ms'): types.NPDatetime('ns'), pa.
        timestamp('s'): types.NPDatetime('ns'), null(): string_type}
    if isinstance(pa_typ.type, pa.DictionaryType):
        if pa_typ.type.value_type != pa.string():
            raise BodoError(
                f'Parquet Categorical data type should be string, not {pa_typ.type.value_type}'
                )
        iymyr__njhug = gekwt__duaho[pa_typ.type.index_type]
        wvfcr__rei = PDCategoricalDtype(category_info[pa_typ.name], bodo.
            string_type, pa_typ.type.ordered, int_type=iymyr__njhug)
        return CategoricalArrayType(wvfcr__rei)
    if pa_typ.type not in gekwt__duaho:
        raise BodoError('Arrow data type {} not supported yet'.format(
            pa_typ.type))
    fyb__edja = gekwt__duaho[pa_typ.type]
    if fyb__edja == datetime_date_type:
        return datetime_date_array_type
    if fyb__edja == bytes_type:
        return binary_array_type
    xvvwq__keae = (string_array_type if fyb__edja == string_type else types
        .Array(fyb__edja, 1, 'C'))
    if fyb__edja == types.bool_:
        xvvwq__keae = boolean_array
    if nullable_from_metadata is not None:
        qksb__unym = nullable_from_metadata
    else:
        qksb__unym = use_nullable_int_arr
    if qksb__unym and not is_index and isinstance(fyb__edja, types.Integer
        ) and pa_typ.nullable:
        xvvwq__keae = IntegerArrayType(fyb__edja)
    return xvvwq__keae


def is_filter_pushdown_disabled_fpath(fpath):
    return fpath.startswith('gs://') or fpath.startswith('gcs://'
        ) or fpath.startswith('hdfs://') or fpath.startswith('abfs://'
        ) or fpath.startswith('abfss://')


def get_parquet_dataset(fpath, get_row_counts=True, dnf_filters=None,
    expr_filters=None, storage_options=None, read_categories=False,
    is_parallel=False):
    if get_row_counts:
        ypx__ixvdf = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    jriq__omnkh = MPI.COMM_WORLD
    if isinstance(fpath, list):
        oib__rtsxt = urlparse(fpath[0])
        izev__fksvg = oib__rtsxt.scheme
        ktwx__bof = oib__rtsxt.netloc
        for oxm__webm in range(len(fpath)):
            xdv__owz = fpath[oxm__webm]
            bftea__kume = urlparse(xdv__owz)
            if bftea__kume.scheme != izev__fksvg:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if bftea__kume.netloc != ktwx__bof:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[oxm__webm] = xdv__owz.rstrip('/')
    else:
        oib__rtsxt = urlparse(fpath)
        izev__fksvg = oib__rtsxt.scheme
        fpath = fpath.rstrip('/')
    if izev__fksvg in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as rkhl__lpmum:
            xakji__jcah = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(xakji__jcah)
    if izev__fksvg == 'http':
        try:
            import fsspec
        except ImportError as rkhl__lpmum:
            xakji__jcah = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
"""
    zxjf__azfon = []

    def getfs(parallel=False):
        if len(zxjf__azfon) == 1:
            return zxjf__azfon[0]
        if izev__fksvg == 's3':
            zxjf__azfon.append(get_s3_fs_from_path(fpath, parallel=parallel,
                storage_options=storage_options) if not isinstance(fpath,
                list) else get_s3_fs_from_path(fpath[0], parallel=parallel,
                storage_options=storage_options))
        elif izev__fksvg in {'gcs', 'gs'}:
            eit__fdcc = gcsfs.GCSFileSystem(token=None)
            zxjf__azfon.append(eit__fdcc)
        elif izev__fksvg == 'http':
            zxjf__azfon.append(fsspec.filesystem('http'))
        elif izev__fksvg in {'hdfs', 'abfs', 'abfss'}:
            zxjf__azfon.append(get_hdfs_fs(fpath) if not isinstance(fpath,
                list) else get_hdfs_fs(fpath[0]))
        else:
            zxjf__azfon.append(None)
        return zxjf__azfon[0]
    abd__kjxs = False
    if get_row_counts:
        kreo__ymb = getfs(parallel=True)
        abd__kjxs = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        yzw__oqp = 1
        eut__vzrkq = os.cpu_count()
        if eut__vzrkq is not None and eut__vzrkq > 1:
            yzw__oqp = eut__vzrkq // 2
        try:
            if get_row_counts:
                cxj__mbhua = tracing.Event('pq.ParquetDataset', is_parallel
                    =False)
                if tracing.is_tracing():
                    cxj__mbhua.add_attribute('dnf_filter', str(dnf_filters))
            eqsg__osmzf = pa.io_thread_count()
            pa.set_io_thread_count(yzw__oqp)
            rmo__oultd = pq.ParquetDataset(fpath, filesystem=getfs(),
                filters=None, use_legacy_dataset=True, validate_schema=
                False, metadata_nthreads=yzw__oqp)
            pa.set_io_thread_count(eqsg__osmzf)
            bcs__phtym = bodo.io.pa_parquet.get_dataset_schema(rmo__oultd)
            if dnf_filters:
                if get_row_counts:
                    cxj__mbhua.add_attribute('num_pieces_before_filter',
                        len(rmo__oultd.pieces))
                yfo__xqd = time.time()
                rmo__oultd._filter(dnf_filters)
                if get_row_counts:
                    cxj__mbhua.add_attribute('dnf_filter_time', time.time() -
                        yfo__xqd)
                    cxj__mbhua.add_attribute('num_pieces_after_filter', len
                        (rmo__oultd.pieces))
            if get_row_counts:
                cxj__mbhua.finalize()
            rmo__oultd._metadata.fs = None
        except Exception as aoey__ckbn:
            jriq__omnkh.bcast(aoey__ckbn)
            raise BodoError(
                f'error from pyarrow: {type(aoey__ckbn).__name__}: {str(aoey__ckbn)}\n'
                )
        if get_row_counts:
            liwa__fbezx = tracing.Event('bcast dataset')
        jriq__omnkh.bcast(rmo__oultd)
        jriq__omnkh.bcast(bcs__phtym)
    else:
        if get_row_counts:
            liwa__fbezx = tracing.Event('bcast dataset')
        rmo__oultd = jriq__omnkh.bcast(None)
        if isinstance(rmo__oultd, Exception):
            jrn__qzns = rmo__oultd
            raise BodoError(
                f'error from pyarrow: {type(jrn__qzns).__name__}: {str(jrn__qzns)}\n'
                )
        bcs__phtym = jriq__omnkh.bcast(None)
    if get_row_counts:
        liwa__fbezx.finalize()
    rmo__oultd._bodo_total_rows = 0
    if get_row_counts or abd__kjxs:
        if get_row_counts and tracing.is_tracing():
            juhi__joy = tracing.Event('get_row_counts')
            juhi__joy.add_attribute('g_num_pieces', len(rmo__oultd.pieces))
            juhi__joy.add_attribute('g_expr_filters', str(expr_filters))
        expl__dkcxm = 0.0
        num_pieces = len(rmo__oultd.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        jaopt__bcs = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        gwvee__ozs = 0
        lzjje__xatz = 0
        axmsx__yxqh = True
        rmo__oultd._metadata.fs = getfs()
        if expr_filters is not None:
            import random
            random.seed(37)
            yllr__sauw = random.sample(rmo__oultd.pieces, k=len(rmo__oultd.
                pieces))
        else:
            yllr__sauw = rmo__oultd.pieces
        for tfy__hyl in yllr__sauw:
            tfy__hyl._bodo_num_rows = 0
        if izev__fksvg in {'gcs', 'gs', 'hdfs', 'abfs', 'abfss'}:
            for tfy__hyl in yllr__sauw[start:jaopt__bcs]:
                iwc__uanyz = tfy__hyl.get_metadata()
                if get_row_counts:
                    if expr_filters is not None:
                        pa.set_io_thread_count(2)
                        pa.set_cpu_count(2)
                        yfo__xqd = time.time()
                        bzy__pwxz = ds.dataset(tfy__hyl.path, partitioning=
                            ds.partitioning(flavor='hive')).scanner(filter=
                            expr_filters, use_threads=True, use_async=True
                            ).count_rows()
                        expl__dkcxm += time.time() - yfo__xqd
                    else:
                        bzy__pwxz = iwc__uanyz.num_rows
                    tfy__hyl._bodo_num_rows = bzy__pwxz
                    gwvee__ozs += bzy__pwxz
                    lzjje__xatz += iwc__uanyz.num_row_groups
                if abd__kjxs:
                    gbcgb__imke = iwc__uanyz.schema.to_arrow_schema()
                    if bcs__phtym != gbcgb__imke:
                        print(
                            'Schema in {!s} was different. \n{!s}\n\nvs\n\n{!s}'
                            .format(tfy__hyl, gbcgb__imke, bcs__phtym))
                        axmsx__yxqh = False
                        break
        else:
            fpaths = [tfy__hyl.path for tfy__hyl in yllr__sauw[start:
                jaopt__bcs]]
            if izev__fksvg == 's3':
                ktwx__bof = oib__rtsxt.netloc
                fercx__inc = 's3://' + ktwx__bof + '/'
                fpaths = [xdv__owz[len(fercx__inc):] for xdv__owz in fpaths]
                taa__zrjpg = get_s3_subtree_fs(ktwx__bof, region=getfs().
                    region, storage_options=storage_options)
            else:
                taa__zrjpg = None
            pa.set_io_thread_count(4)
            pa.set_cpu_count(4)
            jff__blcdl = ds.dataset(fpaths, filesystem=taa__zrjpg,
                partitioning=ds.partitioning(flavor='hive'))
            for luv__pjauy, srs__frio in zip(yllr__sauw[start:jaopt__bcs],
                jff__blcdl.get_fragments()):
                yfo__xqd = time.time()
                bzy__pwxz = srs__frio.scanner(schema=jff__blcdl.schema,
                    filter=expr_filters, use_threads=True, use_async=True
                    ).count_rows()
                expl__dkcxm += time.time() - yfo__xqd
                luv__pjauy._bodo_num_rows = bzy__pwxz
                gwvee__ozs += bzy__pwxz
                lzjje__xatz += srs__frio.num_row_groups
                if abd__kjxs:
                    gbcgb__imke = srs__frio.metadata.schema.to_arrow_schema()
                    if bcs__phtym != gbcgb__imke:
                        print(
                            'Schema in {!s} was different. \n{!s}\n\nvs\n\n{!s}'
                            .format(luv__pjauy, gbcgb__imke, bcs__phtym))
                        axmsx__yxqh = False
                        break
        if abd__kjxs:
            axmsx__yxqh = jriq__omnkh.allreduce(axmsx__yxqh, op=MPI.LAND)
            if not axmsx__yxqh:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            rmo__oultd._bodo_total_rows = jriq__omnkh.allreduce(gwvee__ozs,
                op=MPI.SUM)
            tvcua__vsptz = jriq__omnkh.allreduce(lzjje__xatz, op=MPI.SUM)
            znwra__hdbp = np.array([tfy__hyl._bodo_num_rows for tfy__hyl in
                rmo__oultd.pieces])
            znwra__hdbp = jriq__omnkh.allreduce(znwra__hdbp, op=MPI.SUM)
            for tfy__hyl, ozefi__ecc in zip(rmo__oultd.pieces, znwra__hdbp):
                tfy__hyl._bodo_num_rows = ozefi__ecc
            if is_parallel and bodo.get_rank(
                ) == 0 and tvcua__vsptz < bodo.get_size():
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({tvcua__vsptz}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()})
"""
                    ))
            if tracing.is_tracing():
                juhi__joy.add_attribute('g_total_num_row_groups', tvcua__vsptz)
                if expr_filters is not None:
                    juhi__joy.add_attribute('total_scan_time', expl__dkcxm)
                sqwi__pjud = np.array([tfy__hyl._bodo_num_rows for tfy__hyl in
                    rmo__oultd.pieces])
                bminj__iqlmg = np.percentile(sqwi__pjud, [25, 50, 75])
                juhi__joy.add_attribute('g_row_counts_min', sqwi__pjud.min())
                juhi__joy.add_attribute('g_row_counts_Q1', bminj__iqlmg[0])
                juhi__joy.add_attribute('g_row_counts_median', bminj__iqlmg[1])
                juhi__joy.add_attribute('g_row_counts_Q3', bminj__iqlmg[2])
                juhi__joy.add_attribute('g_row_counts_max', sqwi__pjud.max())
                juhi__joy.add_attribute('g_row_counts_mean', sqwi__pjud.mean())
                juhi__joy.add_attribute('g_row_counts_std', sqwi__pjud.std())
                juhi__joy.add_attribute('g_row_counts_sum', sqwi__pjud.sum())
                juhi__joy.finalize()
    rmo__oultd._prefix = ''
    if izev__fksvg == 'hdfs':
        fercx__inc = f'{izev__fksvg}://{oib__rtsxt.netloc}'
        if len(rmo__oultd.pieces) > 0:
            luv__pjauy = rmo__oultd.pieces[0]
            if not luv__pjauy.path.startswith(fercx__inc):
                rmo__oultd._prefix = fercx__inc
    if read_categories:
        _add_categories_to_pq_dataset(rmo__oultd)
    if get_row_counts:
        ypx__ixvdf.finalize()
    return rmo__oultd


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, storage_options, region):
    import pyarrow as pa
    eut__vzrkq = os.cpu_count()
    if eut__vzrkq is None or eut__vzrkq == 0:
        eut__vzrkq = 2
    vlrf__vifhc = min(4, eut__vzrkq)
    whyuc__ureb = min(16, eut__vzrkq)
    if is_parallel and len(fpaths) > whyuc__ureb and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(whyuc__ureb)
        pa.set_cpu_count(whyuc__ureb)
    else:
        pa.set_io_thread_count(vlrf__vifhc)
        pa.set_cpu_count(vlrf__vifhc)
    if fpaths[0].startswith('s3://'):
        ktwx__bof = urlparse(fpaths[0]).netloc
        fercx__inc = 's3://' + ktwx__bof + '/'
        fpaths = [xdv__owz[len(fercx__inc):] for xdv__owz in fpaths]
        taa__zrjpg = get_s3_subtree_fs(ktwx__bof, region=region,
            storage_options=storage_options)
    else:
        taa__zrjpg = None
    rmo__oultd = ds.dataset(fpaths, filesystem=taa__zrjpg, partitioning=ds.
        partitioning(flavor='hive'))
    col_names = rmo__oultd.schema.names
    lmwhx__dulvp = [col_names[pickr__onfsj] for pickr__onfsj in selected_fields
        ]
    return rmo__oultd.scanner(columns=lmwhx__dulvp, filter=expr_filters,
        use_threads=True, use_async=True).to_reader()


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    nntfs__pyw = pq_dataset.schema.to_arrow_schema()
    gvp__tsb = [c for c in nntfs__pyw.names if isinstance(nntfs__pyw.field(
        c).type, pa.DictionaryType)]
    if len(gvp__tsb) == 0:
        pq_dataset._category_info = {}
        return
    jriq__omnkh = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            fpyv__vjhq = pq_dataset.pieces[0].open()
            adnd__hhog = fpyv__vjhq.read_row_group(0, gvp__tsb)
            category_info = {c: tuple(adnd__hhog.column(c).chunk(0).
                dictionary.to_pylist()) for c in gvp__tsb}
            del fpyv__vjhq, adnd__hhog
        except Exception as aoey__ckbn:
            jriq__omnkh.bcast(aoey__ckbn)
            raise aoey__ckbn
        jriq__omnkh.bcast(category_info)
    else:
        category_info = jriq__omnkh.bcast(None)
        if isinstance(category_info, Exception):
            jrn__qzns = category_info
            raise jrn__qzns
    pq_dataset._category_info = category_info


def get_pandas_metadata(schema, num_pieces):
    ootcg__znune = None
    nullable_from_metadata = defaultdict(lambda : None)
    bigb__mfkg = b'pandas'
    if schema.metadata is not None and bigb__mfkg in schema.metadata:
        import json
        fqbvs__ucf = json.loads(schema.metadata[bigb__mfkg].decode('utf8'))
        zau__bffwp = len(fqbvs__ucf['index_columns'])
        if zau__bffwp > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        ootcg__znune = fqbvs__ucf['index_columns'][0] if zau__bffwp else None
        if not isinstance(ootcg__znune, str) and (not isinstance(
            ootcg__znune, dict) or num_pieces != 1):
            ootcg__znune = None
        for wgbmg__ftwk in fqbvs__ucf['columns']:
            qjt__qwcdl = wgbmg__ftwk['name']
            if wgbmg__ftwk['pandas_type'].startswith('int'
                ) and qjt__qwcdl is not None:
                if wgbmg__ftwk['numpy_type'].startswith('Int'):
                    nullable_from_metadata[qjt__qwcdl] = True
                else:
                    nullable_from_metadata[qjt__qwcdl] = False
    return ootcg__znune, nullable_from_metadata


def parquet_file_schema(file_name, selected_columns, storage_options=None):
    col_names = []
    vsnj__dmjh = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = [] if pq_dataset.partitions is None else [pq_dataset.
        partitions.levels[oxm__webm].name for oxm__webm in range(len(
        pq_dataset.partitions.partition_names))]
    nntfs__pyw = pq_dataset.schema.to_arrow_schema()
    num_pieces = len(pq_dataset.pieces)
    col_names = nntfs__pyw.names
    ootcg__znune, nullable_from_metadata = get_pandas_metadata(nntfs__pyw,
        num_pieces)
    dje__xxe = [_get_numba_typ_from_pa_typ(nntfs__pyw.field(c), c ==
        ootcg__znune, nullable_from_metadata[c], pq_dataset._category_info) for
        c in col_names]
    if partition_names:
        col_names += partition_names
        dje__xxe += [_get_partition_cat_dtype(pq_dataset.partitions.levels[
            oxm__webm]) for oxm__webm in range(len(partition_names))]
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in col_names:
            raise BodoError('Selected column {} not in Parquet file schema'
                .format(c))
    if ootcg__znune and not isinstance(ootcg__znune, dict
        ) and ootcg__znune not in selected_columns:
        selected_columns.append(ootcg__znune)
    col_indices = [col_names.index(c) for c in selected_columns]
    vsnj__dmjh = [dje__xxe[col_names.index(c)] for c in selected_columns]
    col_names = selected_columns
    return col_names, vsnj__dmjh, ootcg__znune, col_indices, partition_names


def _get_partition_cat_dtype(part_set):
    tres__wjua = part_set.dictionary.to_pandas()
    clo__osjj = bodo.typeof(tres__wjua).dtype
    wvfcr__rei = PDCategoricalDtype(tuple(tres__wjua), clo__osjj, False)
    return CategoricalArrayType(wvfcr__rei)


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
        eis__ltgd = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer()])
        slzy__bpz = cgutils.get_or_insert_function(builder.module,
            eis__ltgd, name='pq_write')
        builder.call(slzy__bpz, args)
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
        eis__ltgd = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer()])
        slzy__bpz = cgutils.get_or_insert_function(builder.module,
            eis__ltgd, name='pq_write_partitioned')
        builder.call(slzy__bpz, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr), codegen
