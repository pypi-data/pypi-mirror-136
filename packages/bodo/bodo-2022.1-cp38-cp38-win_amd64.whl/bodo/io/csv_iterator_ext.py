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
        xsaai__poh = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name})'
            )
        super(types.SimpleIteratorType, self).__init__(xsaai__poh)
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
        tklxk__acof = [('csv_reader', bodo.ir.connector.stream_reader_type),
            ('index', types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, tklxk__acof)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    lxu__jwz = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    eoxv__ymic = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer()]
        )
    sivpo__mmpxb = cgutils.get_or_insert_function(builder.module,
        eoxv__ymic, name='initialize_csv_reader')
    builder.call(sivpo__mmpxb, [lxu__jwz.csv_reader])
    builder.store(context.get_constant(types.uint64, 0), lxu__jwz.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [fxk__inwe] = sig.args
    [echi__volt] = args
    lxu__jwz = cgutils.create_struct_proxy(fxk__inwe)(context, builder,
        value=echi__volt)
    eoxv__ymic = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer()]
        )
    sivpo__mmpxb = cgutils.get_or_insert_function(builder.module,
        eoxv__ymic, name='update_csv_reader')
    yqil__bjcik = builder.call(sivpo__mmpxb, [lxu__jwz.csv_reader])
    result.set_valid(yqil__bjcik)
    with builder.if_then(yqil__bjcik):
        rinl__tzk = builder.load(lxu__jwz.index)
        irs__zdtoq = types.Tuple([sig.return_type.first_type, types.int64])
        ipqa__buwlc = gen_read_csv_objmode(sig.args[0])
        nin__rnznr = signature(irs__zdtoq, bodo.ir.connector.
            stream_reader_type, types.int64)
        adba__jxr = context.compile_internal(builder, ipqa__buwlc,
            nin__rnznr, [lxu__jwz.csv_reader, rinl__tzk])
        nlg__lfqb, qzfe__xvuw = cgutils.unpack_tuple(builder, adba__jxr)
        xuofy__sbeni = builder.add(rinl__tzk, qzfe__xvuw, flags=['nsw'])
        builder.store(xuofy__sbeni, lxu__jwz.index)
        result.yield_(nlg__lfqb)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        omq__pyn = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        omq__pyn.csv_reader = args[0]
        axnx__lkt = context.get_constant(types.uintp, 0)
        omq__pyn.index = cgutils.alloca_once_value(builder, axnx__lkt)
        return omq__pyn._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    tjx__zza = csv_iterator_typeref.instance_type
    sig = signature(tjx__zza, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    ncpm__reqxx = 'def read_csv_objmode(f_reader):\n'
    qpyf__dik = [sanitize_varname(zyda__cgia) for zyda__cgia in
        csv_iterator_type._out_colnames]
    xcqdm__wnt = ir_utils.next_label()
    cuqk__wwtjj = globals()
    out_types = csv_iterator_type._out_types
    cuqk__wwtjj[f'table_type_{xcqdm__wnt}'] = TableType(tuple(out_types))
    cuqk__wwtjj[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    mxev__tav = list(range(len(csv_iterator_type._usecols)))
    ncpm__reqxx += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        qpyf__dik, out_types, csv_iterator_type._usecols, mxev__tav,
        csv_iterator_type._sep, xcqdm__wnt, cuqk__wwtjj, parallel=False,
        check_parallel_runtime=True, idx_col_index=csv_iterator_type.
        _index_ind, idx_col_typ=csv_iterator_type._index_arr_typ)
    kqa__sera = bodo.ir.csv_ext._gen_parallel_flag_name(qpyf__dik)
    njh__nmtc = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [kqa__sera]
    ncpm__reqxx += f"  return {', '.join(njh__nmtc)}"
    cuqk__wwtjj = globals()
    xxqh__scha = {}
    exec(ncpm__reqxx, cuqk__wwtjj, xxqh__scha)
    caw__wnjiy = xxqh__scha['read_csv_objmode']
    uaq__sdpf = numba.njit(caw__wnjiy)
    bodo.ir.csv_ext.compiled_funcs.append(uaq__sdpf)
    gwj__sjj = 'def read_func(reader, local_start):\n'
    gwj__sjj += f"  {', '.join(njh__nmtc)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        gwj__sjj += f'  local_len = len(T)\n'
        gwj__sjj += '  total_size = local_len\n'
        gwj__sjj += f'  if ({kqa__sera}):\n'
        gwj__sjj += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        gwj__sjj += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        vlf__kpzjh = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        gwj__sjj += '  total_size = 0\n'
        vlf__kpzjh = (
            f'bodo.utils.conversion.convert_to_index({njh__nmtc[1]}, {csv_iterator_type._index_name!r})'
            )
    gwj__sjj += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({njh__nmtc[0]},), {vlf__kpzjh}, out_df_typ), total_size)
"""
    exec(gwj__sjj, {'bodo': bodo, 'objmode_func': uaq__sdpf, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        'out_df_typ': csv_iterator_type.yield_type}, xxqh__scha)
    return xxqh__scha['read_func']
