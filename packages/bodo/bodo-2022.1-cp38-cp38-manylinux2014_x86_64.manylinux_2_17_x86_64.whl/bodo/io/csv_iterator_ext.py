"""
Class information for DataFrame iterators returned by pd.read_csv. This is used
to handle situations in which pd.read_csv is used to return chunks with separate
read calls instead of just a single read.
"""
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir_utils, types
from numba.core.imputils import RefType, impl_ret_borrowed, iternext_impl
from numba.core.typing.templates import signature
from numba.extending import intrinsic, lower_builtin, models, register_model
import bodo
import bodo.ir.connector
import bodo.ir.csv_ext
from bodo import objmode
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.table import Table, TableType
from bodo.io import csv_cpp
from bodo.ir.csv_ext import _gen_read_csv_objmode, astype
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import sanitize_varname
ll.add_symbol('update_csv_reader', csv_cpp.update_csv_reader)
ll.add_symbol('initialize_csv_reader', csv_cpp.initialize_csv_reader)


class CSVIteratorType(types.SimpleIteratorType):

    def __init__(self, df_type, out_colnames, out_types, usecols, sep,
        index_ind, index_arr_typ, index_name):
        assert isinstance(df_type, DataFrameType
            ), 'CSVIterator must return a DataFrame'
        wrwey__jhsx = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name})'
            )
        super(types.SimpleIteratorType, self).__init__(wrwey__jhsx)
        self._yield_type = df_type
        self._out_colnames = out_colnames
        self._out_types = out_types
        self._usecols = usecols
        self._sep = sep
        self._index_ind = index_ind
        self._index_arr_typ = index_arr_typ
        self._index_name = index_name

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(CSVIteratorType)
class CSVIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        lhda__rzbx = [('csv_reader', bodo.ir.connector.stream_reader_type),
            ('index', types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, lhda__rzbx)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    jia__mnai = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    retfq__exgrh = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer()])
    eoxca__cioap = cgutils.get_or_insert_function(builder.module,
        retfq__exgrh, name='initialize_csv_reader')
    builder.call(eoxca__cioap, [jia__mnai.csv_reader])
    builder.store(context.get_constant(types.uint64, 0), jia__mnai.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [ypokg__xtqzi] = sig.args
    [anm__yaafb] = args
    jia__mnai = cgutils.create_struct_proxy(ypokg__xtqzi)(context, builder,
        value=anm__yaafb)
    retfq__exgrh = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer()])
    eoxca__cioap = cgutils.get_or_insert_function(builder.module,
        retfq__exgrh, name='update_csv_reader')
    ixudv__kqa = builder.call(eoxca__cioap, [jia__mnai.csv_reader])
    result.set_valid(ixudv__kqa)
    with builder.if_then(ixudv__kqa):
        yppej__swaa = builder.load(jia__mnai.index)
        jzmw__nci = types.Tuple([sig.return_type.first_type, types.int64])
        mhszv__wcx = gen_read_csv_objmode(sig.args[0])
        hea__avxwk = signature(jzmw__nci, bodo.ir.connector.
            stream_reader_type, types.int64)
        gfbpp__rjhu = context.compile_internal(builder, mhszv__wcx,
            hea__avxwk, [jia__mnai.csv_reader, yppej__swaa])
        dgc__tbk, gtas__tdr = cgutils.unpack_tuple(builder, gfbpp__rjhu)
        jbfsf__cmv = builder.add(yppej__swaa, gtas__tdr, flags=['nsw'])
        builder.store(jbfsf__cmv, jia__mnai.index)
        result.yield_(dgc__tbk)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        ktapz__dir = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        ktapz__dir.csv_reader = args[0]
        imf__agngj = context.get_constant(types.uintp, 0)
        ktapz__dir.index = cgutils.alloca_once_value(builder, imf__agngj)
        return ktapz__dir._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    yfu__bryn = csv_iterator_typeref.instance_type
    sig = signature(yfu__bryn, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    zaqyc__dly = 'def read_csv_objmode(f_reader):\n'
    wmy__vjl = [sanitize_varname(ndn__tqlzf) for ndn__tqlzf in
        csv_iterator_type._out_colnames]
    zvc__lzf = ir_utils.next_label()
    qst__dzkoc = globals()
    out_types = csv_iterator_type._out_types
    qst__dzkoc[f'table_type_{zvc__lzf}'] = TableType(tuple(out_types))
    qst__dzkoc[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    ejxb__vdlp = list(range(len(csv_iterator_type._usecols)))
    zaqyc__dly += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        wmy__vjl, out_types, csv_iterator_type._usecols, ejxb__vdlp,
        csv_iterator_type._sep, zvc__lzf, qst__dzkoc, parallel=False,
        check_parallel_runtime=True, idx_col_index=csv_iterator_type.
        _index_ind, idx_col_typ=csv_iterator_type._index_arr_typ)
    paxn__tfj = bodo.ir.csv_ext._gen_parallel_flag_name(wmy__vjl)
    oqere__szqig = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [paxn__tfj]
    zaqyc__dly += f"  return {', '.join(oqere__szqig)}"
    qst__dzkoc = globals()
    xbb__ckl = {}
    exec(zaqyc__dly, qst__dzkoc, xbb__ckl)
    wfhb__vsv = xbb__ckl['read_csv_objmode']
    dytta__yizp = numba.njit(wfhb__vsv)
    bodo.ir.csv_ext.compiled_funcs.append(dytta__yizp)
    jspfs__tfjxd = 'def read_func(reader, local_start):\n'
    jspfs__tfjxd += f"  {', '.join(oqere__szqig)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        jspfs__tfjxd += f'  local_len = len(T)\n'
        jspfs__tfjxd += '  total_size = local_len\n'
        jspfs__tfjxd += f'  if ({paxn__tfj}):\n'
        jspfs__tfjxd += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        jspfs__tfjxd += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        dfn__nwqkw = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        jspfs__tfjxd += '  total_size = 0\n'
        dfn__nwqkw = (
            f'bodo.utils.conversion.convert_to_index({oqere__szqig[1]}, {csv_iterator_type._index_name!r})'
            )
    jspfs__tfjxd += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({oqere__szqig[0]},), {dfn__nwqkw}, out_df_typ), total_size)
"""
    exec(jspfs__tfjxd, {'bodo': bodo, 'objmode_func': dytta__yizp, '_op':
        np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        'out_df_typ': csv_iterator_type.yield_type}, xbb__ckl)
    return xbb__ckl['read_func']
