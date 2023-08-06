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
    lql__ustqt = typemap[node.file_name.name]
    if types.unliteral(lql__ustqt) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {lql__ustqt}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        dst__xvjbk = typemap[node.skiprows.name]
        if isinstance(dst__xvjbk, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(dst__xvjbk, types.Integer) and not (isinstance(
            dst__xvjbk, (types.List, types.Tuple)) and isinstance(
            dst__xvjbk.dtype, types.Integer)) and not isinstance(dst__xvjbk,
            (types.LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {dst__xvjbk}."
                , loc=node.skiprows.loc)
        elif isinstance(dst__xvjbk, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        eouc__ascus = typemap[node.nrows.name]
        if not isinstance(eouc__ascus, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {eouc__ascus}."
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
        ehkp__zqefq = csv_node.out_vars[0]
        if ehkp__zqefq.name not in lives:
            return None
    else:
        rfbbv__ecq = csv_node.out_vars[0]
        jqo__uwy = csv_node.out_vars[1]
        if rfbbv__ecq.name not in lives and jqo__uwy.name not in lives:
            return None
        elif jqo__uwy.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif rfbbv__ecq.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.type_usecol_offset = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    dst__xvjbk = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        if array_dists is not None:
            nzqf__tmms = csv_node.out_vars[0].name
            parallel = array_dists[nzqf__tmms] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        gdqp__ibdwm = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        gdqp__ibdwm += (
            f'    reader = _csv_reader_init(fname, nrows, skiprows)\n')
        gdqp__ibdwm += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        ilrb__xubp = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(gdqp__ibdwm, {}, ilrb__xubp)
        dgs__zbook = ilrb__xubp['csv_iterator_impl']
        njld__prp = 'def csv_reader_init(fname, nrows, skiprows):\n'
        njld__prp += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory)
        njld__prp += '  return f_reader\n'
        exec(njld__prp, globals(), ilrb__xubp)
        yujcb__pvwu = ilrb__xubp['csv_reader_init']
        nrb__btwes = numba.njit(yujcb__pvwu)
        compiled_funcs.append(nrb__btwes)
        facsq__kzlqj = compile_to_numba_ir(dgs__zbook, {'_csv_reader_init':
            nrb__btwes, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, dst__xvjbk), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(facsq__kzlqj, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        mrrp__xlgov = facsq__kzlqj.body[:-3]
        mrrp__xlgov[-1].target = csv_node.out_vars[0]
        return mrrp__xlgov
    if array_dists is not None:
        qirkh__sadp = csv_node.out_vars[0].name
        parallel = array_dists[qirkh__sadp] in (distributed_pass.
            Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        ctrmi__ishlc = csv_node.out_vars[1].name
        assert typemap[ctrmi__ishlc
            ] == types.none or not parallel or array_dists[ctrmi__ishlc] in (
            distributed_pass.Distribution.OneD, distributed_pass.
            Distribution.OneD_Var
            ), 'pq data/index parallelization does not match'
    gdqp__ibdwm = 'def csv_impl(fname, nrows, skiprows):\n'
    gdqp__ibdwm += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    ilrb__xubp = {}
    exec(gdqp__ibdwm, {}, ilrb__xubp)
    xzulk__dlmt = ilrb__xubp['csv_impl']
    gtywo__sikel = csv_node.usecols
    if gtywo__sikel:
        gtywo__sikel = [csv_node.usecols[pym__uhcbu] for pym__uhcbu in
            csv_node.type_usecol_offset]
    xtn__htnlb = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, gtywo__sikel, csv_node.type_usecol_offset, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, idx_col_index=csv_node.
        index_column_index, idx_col_typ=csv_node.index_column_typ)
    facsq__kzlqj = compile_to_numba_ir(xzulk__dlmt, {'_csv_reader_py':
        xtn__htnlb}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, dst__xvjbk), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(facsq__kzlqj, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    mrrp__xlgov = facsq__kzlqj.body[:-3]
    mrrp__xlgov[-1].target = csv_node.out_vars[1]
    mrrp__xlgov[-2].target = csv_node.out_vars[0]
    if csv_node.index_column_index is None:
        mrrp__xlgov.pop(-1)
    elif not gtywo__sikel:
        mrrp__xlgov.pop(-2)
    return mrrp__xlgov


def csv_remove_dead_column(csv_node, column_live_map, equiv_vars, typemap):
    if csv_node.chunksize is not None:
        return False
    assert len(csv_node.out_vars) == 2, 'invalid CsvReader node'
    rmfs__ini = csv_node.out_vars[0].name
    if isinstance(typemap[rmfs__ini], TableType) and csv_node.usecols:
        dvpuq__uxly, vaqe__zefkc = get_live_column_nums_block(column_live_map,
            equiv_vars, rmfs__ini)
        dvpuq__uxly = bodo.ir.connector.trim_extra_used_columns(dvpuq__uxly,
            len(csv_node.usecols))
        if not vaqe__zefkc and not dvpuq__uxly:
            dvpuq__uxly = [0]
        if not vaqe__zefkc and len(dvpuq__uxly) != len(csv_node.
            type_usecol_offset):
            csv_node.type_usecol_offset = dvpuq__uxly
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
    ois__bgi = t.dtype
    if isinstance(ois__bgi, PDCategoricalDtype):
        jiqu__pqh = CategoricalArrayType(ois__bgi)
        kag__xamb = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, kag__xamb, jiqu__pqh)
        return kag__xamb
    if ois__bgi == types.NPDatetime('ns'):
        ois__bgi = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        ihlp__fyon = 'int_arr_{}'.format(ois__bgi)
        setattr(types, ihlp__fyon, t)
        return ihlp__fyon
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if ois__bgi == types.bool_:
        ois__bgi = 'bool_'
    if ois__bgi == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(ois__bgi, (
        StringArrayType, ArrayItemArrayType)):
        tqxva__smvg = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, tqxva__smvg, t)
        return tqxva__smvg
    return '{}[::1]'.format(ois__bgi)


def _get_pd_dtype_str(t):
    ois__bgi = t.dtype
    if isinstance(ois__bgi, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(ois__bgi.categories)
    if ois__bgi == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if ois__bgi.signed else 'U', ois__bgi.
            bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(ois__bgi, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(ois__bgi)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    nvqsm__zuae = ''
    from collections import defaultdict
    lzmt__wwq = defaultdict(list)
    for tgwii__puvue, rhxy__ubcdp in typemap.items():
        lzmt__wwq[rhxy__ubcdp].append(tgwii__puvue)
    crd__zghx = df.columns.to_list()
    zpu__yow = []
    for rhxy__ubcdp, jpmjr__eypj in lzmt__wwq.items():
        try:
            zpu__yow.append(df.loc[:, jpmjr__eypj].astype(rhxy__ubcdp, copy
                =False))
            df = df.drop(jpmjr__eypj, axis=1)
        except (ValueError, TypeError) as fyvfn__jrmjr:
            nvqsm__zuae = (
                f"Caught the runtime error '{fyvfn__jrmjr}' on columns {jpmjr__eypj}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    ctjxs__lrbyw = bool(nvqsm__zuae)
    if parallel:
        tqbkd__crrfl = MPI.COMM_WORLD
        ctjxs__lrbyw = tqbkd__crrfl.allreduce(ctjxs__lrbyw, op=MPI.LOR)
    if ctjxs__lrbyw:
        lepwj__zdaw = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if nvqsm__zuae:
            raise TypeError(f'{lepwj__zdaw}\n{nvqsm__zuae}')
        else:
            raise TypeError(
                f'{lepwj__zdaw}\nPlease refer to errors on other ranks.')
    df = pd.concat(zpu__yow + [df], axis=1)
    zkjil__seh = df.loc[:, crd__zghx]
    return zkjil__seh


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory):
    hiorr__oposz = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        gdqp__ibdwm = '  skiprows = sorted(set(skiprows))\n'
    else:
        gdqp__ibdwm = '  skiprows = [skiprows]\n'
    gdqp__ibdwm += '  skiprows_list_len = len(skiprows)\n'
    gdqp__ibdwm += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    gdqp__ibdwm += '  check_java_installation(fname)\n'
    gdqp__ibdwm += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    gdqp__ibdwm += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    gdqp__ibdwm += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), {}, {}, skiprows_list_len, {})
"""
        .format(parallel, hiorr__oposz, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    gdqp__ibdwm += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    gdqp__ibdwm += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    gdqp__ibdwm += "      raise FileNotFoundError('File does not exist')\n"
    return gdqp__ibdwm


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    type_usecol_offset, sep, call_id, glbs, parallel,
    check_parallel_runtime, idx_col_index, idx_col_typ):
    tjt__rdau = [str(jtenu__kqwsq) for pym__uhcbu, jtenu__kqwsq in
        enumerate(usecols) if col_typs[type_usecol_offset[pym__uhcbu]].
        dtype == types.NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        tjt__rdau.append(str(idx_col_index))
    uos__ymt = ', '.join(tjt__rdau)
    gdopa__qxin = _gen_parallel_flag_name(sanitized_cnames)
    xmvbe__npgsj = f"{gdopa__qxin}='bool_'" if check_parallel_runtime else ''
    gcjr__sdp = [_get_pd_dtype_str(col_typs[type_usecol_offset[pym__uhcbu]]
        ) for pym__uhcbu in range(len(usecols))]
    gri__vxcd = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    nfpr__abdxz = [jtenu__kqwsq for pym__uhcbu, jtenu__kqwsq in enumerate(
        usecols) if gcjr__sdp[pym__uhcbu] == 'str']
    if idx_col_index is not None and gri__vxcd == 'str':
        nfpr__abdxz.append(idx_col_index)
    iavno__jiw = np.array(nfpr__abdxz, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = iavno__jiw
    gdqp__ibdwm = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    zzae__iyu = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []))
    glbs[f'usecols_arr_{call_id}'] = zzae__iyu
    gdqp__ibdwm += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    mecsy__zcz = np.array(type_usecol_offset, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = mecsy__zcz
        gdqp__ibdwm += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    gcec__gahrz = defaultdict(list)
    for pym__uhcbu, jtenu__kqwsq in enumerate(usecols):
        if gcjr__sdp[pym__uhcbu] == 'str':
            continue
        gcec__gahrz[gcjr__sdp[pym__uhcbu]].append(jtenu__kqwsq)
    if idx_col_index is not None and gri__vxcd != 'str':
        gcec__gahrz[gri__vxcd].append(idx_col_index)
    for pym__uhcbu, aabpo__ielba in enumerate(gcec__gahrz.values()):
        glbs[f't_arr_{pym__uhcbu}_{call_id}'] = np.asarray(aabpo__ielba)
        gdqp__ibdwm += (
            f'  t_arr_{pym__uhcbu}_{call_id}_2 = t_arr_{pym__uhcbu}_{call_id}\n'
            )
    if idx_col_index != None:
        gdqp__ibdwm += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {xmvbe__npgsj}):
"""
    else:
        gdqp__ibdwm += (
            f'  with objmode(T=table_type_{call_id}, {xmvbe__npgsj}):\n')
    gdqp__ibdwm += f'    typemap = {{}}\n'
    for pym__uhcbu, cdira__pai in enumerate(gcec__gahrz.keys()):
        gdqp__ibdwm += f"""    typemap.update({{i:{cdira__pai} for i in t_arr_{pym__uhcbu}_{call_id}_2}})
"""
    gdqp__ibdwm += '    if f_reader.get_chunk_size() == 0:\n'
    gdqp__ibdwm += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    gdqp__ibdwm += '    else:\n'
    gdqp__ibdwm += '      df = pd.read_csv(f_reader,\n'
    gdqp__ibdwm += '        header=None,\n'
    gdqp__ibdwm += '        parse_dates=[{}],\n'.format(uos__ymt)
    gdqp__ibdwm += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    gdqp__ibdwm += (
        f'        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False)\n'
        )
    if check_parallel_runtime:
        gdqp__ibdwm += f'    {gdopa__qxin} = f_reader.is_parallel()\n'
    else:
        gdqp__ibdwm += f'    {gdopa__qxin} = {parallel}\n'
    gdqp__ibdwm += f'    df = astype(df, typemap, {gdopa__qxin})\n'
    if idx_col_index != None:
        liczb__tulhx = sorted(zzae__iyu).index(idx_col_index)
        gdqp__ibdwm += f'    idx_arr = df.iloc[:, {liczb__tulhx}].values\n'
        gdqp__ibdwm += (
            f'    df.drop(columns=df.columns[{liczb__tulhx}], inplace=True)\n')
    if len(usecols) == 0:
        gdqp__ibdwm += f'    T = None\n'
    else:
        gdqp__ibdwm += f'    arrs = []\n'
        gdqp__ibdwm += f'    for i in range(df.shape[1]):\n'
        gdqp__ibdwm += f'      arrs.append(df.iloc[:, i].values)\n'
        gdqp__ibdwm += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return gdqp__ibdwm


def _gen_parallel_flag_name(sanitized_cnames):
    gdopa__qxin = '_parallel_value'
    while gdopa__qxin in sanitized_cnames:
        gdopa__qxin = '_' + gdopa__qxin
    return gdopa__qxin


def _gen_csv_reader_py(col_names, col_typs, usecols, type_usecol_offset,
    sep, parallel, header, compression, is_skiprows_list, pd_low_memory,
    idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(vtoz__vcqxd) for vtoz__vcqxd in
        col_names]
    gdqp__ibdwm = 'def csv_reader_py(fname, nrows, skiprows):\n'
    gdqp__ibdwm += _gen_csv_file_reader_init(parallel, header, compression,
        -1, is_skiprows_list, pd_low_memory)
    call_id = ir_utils.next_label()
    memvc__dvwym = globals()
    if idx_col_typ != types.none:
        memvc__dvwym[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        memvc__dvwym[f'table_type_{call_id}'] = types.none
    else:
        memvc__dvwym[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    gdqp__ibdwm += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, type_usecol_offset, sep, call_id, memvc__dvwym,
        parallel=parallel, check_parallel_runtime=False, idx_col_index=
        idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        gdqp__ibdwm += '  return (T, idx_arr)\n'
    else:
        gdqp__ibdwm += '  return (T, None)\n'
    ilrb__xubp = {}
    exec(gdqp__ibdwm, memvc__dvwym, ilrb__xubp)
    xtn__htnlb = ilrb__xubp['csv_reader_py']
    nrb__btwes = numba.njit(xtn__htnlb)
    compiled_funcs.append(nrb__btwes)
    return nrb__btwes
