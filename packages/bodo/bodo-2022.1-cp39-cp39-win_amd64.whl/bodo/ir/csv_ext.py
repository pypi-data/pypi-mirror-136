from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from mpi4py import MPI
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import Table, TableType
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.table_column_del_pass import get_live_column_nums_block, ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import sanitize_varname


class CsvReader(ir.Stmt):

    def __init__(self, file_name, df_out, sep, df_colnames, out_vars,
        out_types, usecols, loc, header, compression, nrows, skiprows,
        chunksize, is_skiprows_list, low_memory, index_column_index=None,
        index_column_typ=types.none):
        self.connector_typ = 'csv'
        self.file_name = file_name
        self.df_out = df_out
        self.sep = sep
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.usecols = usecols
        self.loc = loc
        self.skiprows = skiprows
        self.nrows = nrows
        self.header = header
        self.compression = compression
        self.chunksize = chunksize
        self.is_skiprows_list = is_skiprows_list
        self.pd_low_memory = low_memory
        self.index_column_index = index_column_index
        self.index_column_typ = index_column_typ
        self.type_usecol_offset = list(range(len(usecols)))

    def __repr__(self):
        return (
            '{} = ReadCsv(file={}, col_names={}, types={}, vars={}, nrows={}, skiprows={}, chunksize={}, is_skiprows_list={}, pd_low_memory={}, index_column_index={}, index_colum_typ = {}, type_usecol_offsets={})'
            .format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars, self.nrows, self.skiprows, self.
            chunksize, self.is_skiprows_list, self.pd_low_memory, self.
            index_column_index, self.index_column_typ, self.type_usecol_offset)
            )


def check_node_typing(node, typemap):
    cft__glhw = typemap[node.file_name.name]
    if types.unliteral(cft__glhw) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {cft__glhw}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        phhsx__yfbo = typemap[node.skiprows.name]
        if isinstance(phhsx__yfbo, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(phhsx__yfbo, types.Integer) and not (isinstance
            (phhsx__yfbo, (types.List, types.Tuple)) and isinstance(
            phhsx__yfbo.dtype, types.Integer)) and not isinstance(phhsx__yfbo,
            (types.LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {phhsx__yfbo}."
                , loc=node.skiprows.loc)
        elif isinstance(phhsx__yfbo, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        cron__ouh = typemap[node.nrows.name]
        if not isinstance(cron__ouh, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {cron__ouh}."
                , loc=node.nrows.loc)


import llvmlite.binding as ll
from bodo.io import csv_cpp
ll.add_symbol('csv_file_chunk_reader', csv_cpp.csv_file_chunk_reader)
csv_file_chunk_reader = types.ExternalFunction('csv_file_chunk_reader',
    bodo.ir.connector.stream_reader_type(types.voidptr, types.bool_, types.
    voidptr, types.int64, types.bool_, types.voidptr, types.voidptr, types.
    int64, types.bool_, types.int64, types.bool_))


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        faony__fnew = csv_node.out_vars[0]
        if faony__fnew.name not in lives:
            return None
    else:
        sic__vmbpx = csv_node.out_vars[0]
        uqqs__bpc = csv_node.out_vars[1]
        if sic__vmbpx.name not in lives and uqqs__bpc.name not in lives:
            return None
        elif uqqs__bpc.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif sic__vmbpx.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.type_usecol_offset = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    phhsx__yfbo = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        if array_dists is not None:
            bznpj__hkmx = csv_node.out_vars[0].name
            parallel = array_dists[bznpj__hkmx] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        hmog__elw = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        hmog__elw += f'    reader = _csv_reader_init(fname, nrows, skiprows)\n'
        hmog__elw += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        etc__gped = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(hmog__elw, {}, etc__gped)
        uadvb__tljvu = etc__gped['csv_iterator_impl']
        jjkkg__nwj = 'def csv_reader_init(fname, nrows, skiprows):\n'
        jjkkg__nwj += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory)
        jjkkg__nwj += '  return f_reader\n'
        exec(jjkkg__nwj, globals(), etc__gped)
        mubfu__ojvi = etc__gped['csv_reader_init']
        azn__jlqdu = numba.njit(mubfu__ojvi)
        compiled_funcs.append(azn__jlqdu)
        lgll__fmkpb = compile_to_numba_ir(uadvb__tljvu, {'_csv_reader_init':
            azn__jlqdu, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, phhsx__yfbo), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(lgll__fmkpb, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        npkqn__dvl = lgll__fmkpb.body[:-3]
        npkqn__dvl[-1].target = csv_node.out_vars[0]
        return npkqn__dvl
    if array_dists is not None:
        fkzo__lfa = csv_node.out_vars[0].name
        parallel = array_dists[fkzo__lfa] in (distributed_pass.Distribution
            .OneD, distributed_pass.Distribution.OneD_Var)
        jgi__inpb = csv_node.out_vars[1].name
        assert typemap[jgi__inpb] == types.none or not parallel or array_dists[
            jgi__inpb] in (distributed_pass.Distribution.OneD,
            distributed_pass.Distribution.OneD_Var
            ), 'pq data/index parallelization does not match'
    hmog__elw = 'def csv_impl(fname, nrows, skiprows):\n'
    hmog__elw += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    etc__gped = {}
    exec(hmog__elw, {}, etc__gped)
    gmi__hsptx = etc__gped['csv_impl']
    bkss__xloy = csv_node.usecols
    if bkss__xloy:
        bkss__xloy = [csv_node.usecols[edv__khvra] for edv__khvra in
            csv_node.type_usecol_offset]
    nizmj__wmat = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, bkss__xloy, csv_node.type_usecol_offset, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, idx_col_index=csv_node.
        index_column_index, idx_col_typ=csv_node.index_column_typ)
    lgll__fmkpb = compile_to_numba_ir(gmi__hsptx, {'_csv_reader_py':
        nizmj__wmat}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, phhsx__yfbo), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(lgll__fmkpb, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    npkqn__dvl = lgll__fmkpb.body[:-3]
    npkqn__dvl[-1].target = csv_node.out_vars[1]
    npkqn__dvl[-2].target = csv_node.out_vars[0]
    if csv_node.index_column_index is None:
        npkqn__dvl.pop(-1)
    elif not bkss__xloy:
        npkqn__dvl.pop(-2)
    return npkqn__dvl


def csv_remove_dead_column(csv_node, column_live_map, equiv_vars, typemap):
    if csv_node.chunksize is not None:
        return False
    assert len(csv_node.out_vars) == 2, 'invalid CsvReader node'
    dbg__jbzj = csv_node.out_vars[0].name
    if isinstance(typemap[dbg__jbzj], TableType) and csv_node.usecols:
        khm__qrgag, kfg__gxuwk = get_live_column_nums_block(column_live_map,
            equiv_vars, dbg__jbzj)
        khm__qrgag = bodo.ir.connector.trim_extra_used_columns(khm__qrgag,
            len(csv_node.usecols))
        if not kfg__gxuwk and not khm__qrgag:
            khm__qrgag = [0]
        if not kfg__gxuwk and len(khm__qrgag) != len(csv_node.
            type_usecol_offset):
            csv_node.type_usecol_offset = khm__qrgag
            return True
    return False


def csv_table_column_use(csv_node, block_use_map, equiv_vars, typemap):
    return


numba.parfors.array_analysis.array_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[CsvReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[CsvReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[CsvReader] = remove_dead_csv
numba.core.analysis.ir_extension_usedefs[CsvReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[CsvReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[CsvReader] = csv_distributed_run
remove_dead_column_extensions[CsvReader] = csv_remove_dead_column
ir_extension_table_column_use[CsvReader] = csv_table_column_use


def _get_dtype_str(t):
    ejsz__njeb = t.dtype
    if isinstance(ejsz__njeb, PDCategoricalDtype):
        lfy__yrdts = CategoricalArrayType(ejsz__njeb)
        wek__ooihu = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, wek__ooihu, lfy__yrdts)
        return wek__ooihu
    if ejsz__njeb == types.NPDatetime('ns'):
        ejsz__njeb = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        frybl__brhvh = 'int_arr_{}'.format(ejsz__njeb)
        setattr(types, frybl__brhvh, t)
        return frybl__brhvh
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if ejsz__njeb == types.bool_:
        ejsz__njeb = 'bool_'
    if ejsz__njeb == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(ejsz__njeb, (
        StringArrayType, ArrayItemArrayType)):
        fly__unjgi = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, fly__unjgi, t)
        return fly__unjgi
    return '{}[::1]'.format(ejsz__njeb)


def _get_pd_dtype_str(t):
    ejsz__njeb = t.dtype
    if isinstance(ejsz__njeb, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(ejsz__njeb.categories)
    if ejsz__njeb == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if ejsz__njeb.signed else 'U',
            ejsz__njeb.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(ejsz__njeb, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(ejsz__njeb)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    sey__cjl = ''
    from collections import defaultdict
    zjhb__puix = defaultdict(list)
    for awj__tvze, vmpc__dtl in typemap.items():
        zjhb__puix[vmpc__dtl].append(awj__tvze)
    ifgv__wqipt = df.columns.to_list()
    zdyjs__jkw = []
    for vmpc__dtl, ynmv__ceyc in zjhb__puix.items():
        try:
            zdyjs__jkw.append(df.loc[:, ynmv__ceyc].astype(vmpc__dtl, copy=
                False))
            df = df.drop(ynmv__ceyc, axis=1)
        except (ValueError, TypeError) as ruku__uhqlw:
            sey__cjl = (
                f"Caught the runtime error '{ruku__uhqlw}' on columns {ynmv__ceyc}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    bfkym__tswdo = bool(sey__cjl)
    if parallel:
        huha__erkv = MPI.COMM_WORLD
        bfkym__tswdo = huha__erkv.allreduce(bfkym__tswdo, op=MPI.LOR)
    if bfkym__tswdo:
        aqin__mvk = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if sey__cjl:
            raise TypeError(f'{aqin__mvk}\n{sey__cjl}')
        else:
            raise TypeError(
                f'{aqin__mvk}\nPlease refer to errors on other ranks.')
    df = pd.concat(zdyjs__jkw + [df], axis=1)
    djd__avvp = df.loc[:, ifgv__wqipt]
    return djd__avvp


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory):
    huhpu__oypss = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        hmog__elw = '  skiprows = sorted(set(skiprows))\n'
    else:
        hmog__elw = '  skiprows = [skiprows]\n'
    hmog__elw += '  skiprows_list_len = len(skiprows)\n'
    hmog__elw += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    hmog__elw += '  check_java_installation(fname)\n'
    hmog__elw += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    hmog__elw += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    hmog__elw += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), {}, {}, skiprows_list_len, {})
"""
        .format(parallel, huhpu__oypss, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    hmog__elw += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    hmog__elw += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    hmog__elw += "      raise FileNotFoundError('File does not exist')\n"
    return hmog__elw


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    type_usecol_offset, sep, call_id, glbs, parallel,
    check_parallel_runtime, idx_col_index, idx_col_typ):
    jmhhu__gpyvw = [str(vwis__hhvrq) for edv__khvra, vwis__hhvrq in
        enumerate(usecols) if col_typs[type_usecol_offset[edv__khvra]].
        dtype == types.NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        jmhhu__gpyvw.append(str(idx_col_index))
    osh__gjns = ', '.join(jmhhu__gpyvw)
    ochj__nza = _gen_parallel_flag_name(sanitized_cnames)
    sevj__vjdy = f"{ochj__nza}='bool_'" if check_parallel_runtime else ''
    elyaz__lhjp = [_get_pd_dtype_str(col_typs[type_usecol_offset[edv__khvra
        ]]) for edv__khvra in range(len(usecols))]
    mmhht__awwk = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    fxyu__qld = [vwis__hhvrq for edv__khvra, vwis__hhvrq in enumerate(
        usecols) if elyaz__lhjp[edv__khvra] == 'str']
    if idx_col_index is not None and mmhht__awwk == 'str':
        fxyu__qld.append(idx_col_index)
    vicz__npoe = np.array(fxyu__qld, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = vicz__npoe
    hmog__elw = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    fzh__uar = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []))
    glbs[f'usecols_arr_{call_id}'] = fzh__uar
    hmog__elw += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    tck__fwd = np.array(type_usecol_offset, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = tck__fwd
        hmog__elw += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    ffkbu__whcr = defaultdict(list)
    for edv__khvra, vwis__hhvrq in enumerate(usecols):
        if elyaz__lhjp[edv__khvra] == 'str':
            continue
        ffkbu__whcr[elyaz__lhjp[edv__khvra]].append(vwis__hhvrq)
    if idx_col_index is not None and mmhht__awwk != 'str':
        ffkbu__whcr[mmhht__awwk].append(idx_col_index)
    for edv__khvra, oliz__cijwx in enumerate(ffkbu__whcr.values()):
        glbs[f't_arr_{edv__khvra}_{call_id}'] = np.asarray(oliz__cijwx)
        hmog__elw += (
            f'  t_arr_{edv__khvra}_{call_id}_2 = t_arr_{edv__khvra}_{call_id}\n'
            )
    if idx_col_index != None:
        hmog__elw += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {sevj__vjdy}):
"""
    else:
        hmog__elw += f'  with objmode(T=table_type_{call_id}, {sevj__vjdy}):\n'
    hmog__elw += f'    typemap = {{}}\n'
    for edv__khvra, wifvj__bjazn in enumerate(ffkbu__whcr.keys()):
        hmog__elw += f"""    typemap.update({{i:{wifvj__bjazn} for i in t_arr_{edv__khvra}_{call_id}_2}})
"""
    hmog__elw += '    if f_reader.get_chunk_size() == 0:\n'
    hmog__elw += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    hmog__elw += '    else:\n'
    hmog__elw += '      df = pd.read_csv(f_reader,\n'
    hmog__elw += '        header=None,\n'
    hmog__elw += '        parse_dates=[{}],\n'.format(osh__gjns)
    hmog__elw += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    hmog__elw += (
        f'        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False)\n'
        )
    if check_parallel_runtime:
        hmog__elw += f'    {ochj__nza} = f_reader.is_parallel()\n'
    else:
        hmog__elw += f'    {ochj__nza} = {parallel}\n'
    hmog__elw += f'    df = astype(df, typemap, {ochj__nza})\n'
    if idx_col_index != None:
        ssvuj__sdv = sorted(fzh__uar).index(idx_col_index)
        hmog__elw += f'    idx_arr = df.iloc[:, {ssvuj__sdv}].values\n'
        hmog__elw += (
            f'    df.drop(columns=df.columns[{ssvuj__sdv}], inplace=True)\n')
    if len(usecols) == 0:
        hmog__elw += f'    T = None\n'
    else:
        hmog__elw += f'    arrs = []\n'
        hmog__elw += f'    for i in range(df.shape[1]):\n'
        hmog__elw += f'      arrs.append(df.iloc[:, i].values)\n'
        hmog__elw += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return hmog__elw


def _gen_parallel_flag_name(sanitized_cnames):
    ochj__nza = '_parallel_value'
    while ochj__nza in sanitized_cnames:
        ochj__nza = '_' + ochj__nza
    return ochj__nza


def _gen_csv_reader_py(col_names, col_typs, usecols, type_usecol_offset,
    sep, parallel, header, compression, is_skiprows_list, pd_low_memory,
    idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(kugl__kvot) for kugl__kvot in
        col_names]
    hmog__elw = 'def csv_reader_py(fname, nrows, skiprows):\n'
    hmog__elw += _gen_csv_file_reader_init(parallel, header, compression, -
        1, is_skiprows_list, pd_low_memory)
    call_id = ir_utils.next_label()
    pbex__yuos = globals()
    if idx_col_typ != types.none:
        pbex__yuos[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        pbex__yuos[f'table_type_{call_id}'] = types.none
    else:
        pbex__yuos[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    hmog__elw += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, type_usecol_offset, sep, call_id, pbex__yuos,
        parallel=parallel, check_parallel_runtime=False, idx_col_index=
        idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        hmog__elw += '  return (T, idx_arr)\n'
    else:
        hmog__elw += '  return (T, None)\n'
    etc__gped = {}
    exec(hmog__elw, pbex__yuos, etc__gped)
    nizmj__wmat = etc__gped['csv_reader_py']
    azn__jlqdu = numba.njit(nizmj__wmat)
    compiled_funcs.append(azn__jlqdu)
    return azn__jlqdu
