"""
Defines Bodo's compiler pipeline.
"""
import os
import warnings
from collections import namedtuple
import numba
from numba.core import ir, ir_utils
from numba.core.compiler import DefaultPassBuilder
from numba.core.compiler_machinery import AnalysisPass, FunctionPass, register_pass
from numba.core.inline_closurecall import inline_closure_call
from numba.core.ir_utils import build_definitions, find_callname, get_definition, guard
from numba.core.registry import CPUDispatcher
from numba.core.typed_passes import DumpParforDiagnostics, InlineOverloads, IRLegalization, NopythonTypeInference, ParforPass, PreParforPass
from numba.core.untyped_passes import MakeFunctionToJitFunction, ReconstructSSA, WithLifting
import bodo
import bodo.libs
import bodo.libs.array_kernels
import bodo.libs.int_arr_ext
import bodo.libs.re_ext
import bodo.libs.spark_extra
import bodo.transforms
import bodo.transforms.series_pass
import bodo.transforms.untyped_pass
from bodo.transforms.series_pass import SeriesPass
from bodo.transforms.table_column_del_pass import TableColumnDelPass
from bodo.transforms.typing_pass import BodoTypeInference
from bodo.transforms.untyped_pass import UntypedPass
from bodo.utils.utils import is_assign, is_call_assign, is_expr
_is_sklearn_supported_version = False
_max_sklearn_version = 0, 24, 2
_max_sklearn_ver_str = '.'.join(str(x) for x in _max_sklearn_version)
try:
    import re
    import sklearn
    import bodo.libs.sklearn_ext
    regex = re.compile('(\\d+)\\.(\\d+)\\..*(\\d+)')
    sklearn_version = sklearn.__version__
    m = regex.match(sklearn_version)
    if m:
        ver = tuple(map(int, m.groups()))
        if ver <= _max_sklearn_version:
            _is_sklearn_supported_version = True
except ImportError as ftv__azb:
    pass
_matplotlib_installed = False
try:
    import matplotlib
    import bodo.libs.matplotlib_ext
    _matplotlib_installed = True
except ImportError as ftv__azb:
    pass
_pyspark_installed = False
try:
    import pyspark
    import pyspark.sql.functions
    import bodo.libs.pyspark_ext
    bodo.utils.transform.no_side_effect_call_tuples.update({('col', pyspark
        .sql.functions), (pyspark.sql.functions.col,), ('sum', pyspark.sql.
        functions), (pyspark.sql.functions.sum,)})
    _pyspark_installed = True
except ImportError as ftv__azb:
    pass
import bodo.hiframes.dataframe_indexing
import bodo.hiframes.datetime_datetime_ext
import bodo.hiframes.datetime_timedelta_ext
try:
    import xgboost
    import bodo.libs.xgb_ext
except ImportError as ftv__azb:
    pass
import bodo.io
import bodo.utils
import bodo.utils.typing
if bodo.utils.utils.has_supported_h5py():
    from bodo.io import h5
numba.core.config.DISABLE_PERFORMANCE_WARNINGS = 1
from numba.core.errors import NumbaExperimentalFeatureWarning, NumbaPendingDeprecationWarning
warnings.simplefilter('ignore', category=NumbaExperimentalFeatureWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
inline_all_calls = False


class BodoCompiler(numba.core.compiler.CompilerBase):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=True,
            inline_calls_pass=inline_all_calls)

    def _create_bodo_pipeline(self, distributed=True, inline_calls_pass=
        False, udf_pipeline=False):
        xnrcs__bhar = 'bodo' if distributed else 'bodo_seq'
        xnrcs__bhar = (xnrcs__bhar + '_inline' if inline_calls_pass else
            xnrcs__bhar)
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state,
            xnrcs__bhar)
        if inline_calls_pass:
            pm.add_pass_after(InlinePass, WithLifting)
        if udf_pipeline:
            pm.add_pass_after(ConvertCallsUDFPass, WithLifting)
        add_pass_before(pm, BodoUntypedPass, ReconstructSSA)
        replace_pass(pm, BodoTypeInference, NopythonTypeInference)
        remove_pass(pm, MakeFunctionToJitFunction)
        add_pass_before(pm, BodoSeriesPass, PreParforPass)
        if distributed:
            pm.add_pass_after(BodoDistributedPass, ParforPass)
        else:
            pm.add_pass_after(LowerParforSeq, ParforPass)
            pm.add_pass_after(LowerBodoIRExtSeq, LowerParforSeq)
        add_pass_before(pm, BodoTableColumnDelPass, IRLegalization)
        pm.add_pass_after(BodoDumpDistDiagnosticsPass, DumpParforDiagnostics)
        pm.finalize()
        return [pm]


def add_pass_before(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for oottw__lupu, (x, oird__yba) in enumerate(pm.passes):
        if x == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(oottw__lupu, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for oottw__lupu, (x, oird__yba) in enumerate(pm.passes):
        if x == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[oottw__lupu] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for oottw__lupu, (x, oird__yba) in enumerate(pm.passes):
        if x == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(oottw__lupu)
    pm._finalized = False


@register_pass(mutates_CFG=True, analysis_only=False)
class InlinePass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        inline_calls(state.func_ir, state.locals)
        state.func_ir.blocks = ir_utils.simplify_CFG(state.func_ir.blocks)
        return True


def _convert_bodo_dispatcher_to_udf(rhs, func_ir):
    pjtg__ugq = guard(get_definition, func_ir, rhs.func)
    if isinstance(pjtg__ugq, (ir.Global, ir.FreeVar, ir.Const)):
        qhx__vzo = pjtg__ugq.value
    else:
        qxhve__bhpon = guard(find_callname, func_ir, rhs)
        if not (qxhve__bhpon and isinstance(qxhve__bhpon[0], str) and
            isinstance(qxhve__bhpon[1], str)):
            return
        func_name, func_mod = qxhve__bhpon
        try:
            import importlib
            bimk__fcue = importlib.import_module(func_mod)
            qhx__vzo = getattr(bimk__fcue, func_name)
        except:
            return
    if isinstance(qhx__vzo, CPUDispatcher) and issubclass(qhx__vzo.
        _compiler.pipeline_class, BodoCompiler
        ) and qhx__vzo._compiler.pipeline_class != BodoCompilerUDF:
        qhx__vzo._compiler.pipeline_class = BodoCompilerUDF


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for clig__irqz in block.body:
                if is_call_assign(clig__irqz):
                    _convert_bodo_dispatcher_to_udf(clig__irqz.value, state
                        .func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        tzwx__ziumc = UntypedPass(state.func_ir, state.typingctx, state.
            args, state.locals, state.metadata, state.flags)
        tzwx__ziumc.run()
        return True


def _update_definitions(func_ir, node_list):
    vsojd__dvm = ir.Loc('', 0)
    rhhqw__plc = ir.Block(ir.Scope(None, vsojd__dvm), vsojd__dvm)
    rhhqw__plc.body = node_list
    build_definitions({(0): rhhqw__plc}, func_ir._definitions)


_series_inline_attrs = {'values', 'shape', 'size', 'empty', 'name', 'index',
    'dtype'}
_series_no_inline_methods = {'to_list', 'tolist', 'rolling', 'to_csv',
    'count', 'fillna', 'to_dict', 'map', 'apply', 'pipe', 'combine',
    'bfill', 'ffill', 'pad', 'backfill'}
_series_method_alias = {'isnull': 'isna', 'product': 'prod', 'kurtosis':
    'kurt', 'is_monotonic': 'is_monotonic_increasing', 'notnull': 'notna'}
_dataframe_no_inline_methods = {'apply', 'itertuples', 'pipe', 'to_parquet',
    'to_sql', 'to_csv', 'to_json', 'assign', 'to_string', 'query', 'rolling'}
TypingInfo = namedtuple('TypingInfo', ['typingctx', 'targetctx', 'typemap',
    'calltypes', 'curr_loc'])


def _inline_bodo_getattr(stmt, rhs, rhs_type, new_body, func_ir, typingctx,
    targetctx, typemap, calltypes):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.utils.transform import compile_func_single_block
    if isinstance(rhs_type, SeriesType) and rhs.attr in _series_inline_attrs:
        wnm__xjkoo = 'overload_series_' + rhs.attr
        fcc__edbt = getattr(bodo.hiframes.series_impl, wnm__xjkoo)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        wnm__xjkoo = 'overload_dataframe_' + rhs.attr
        fcc__edbt = getattr(bodo.hiframes.dataframe_impl, wnm__xjkoo)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    eava__qumzc = fcc__edbt(rhs_type)
    wwy__mdcyt = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    fmugt__sgi = compile_func_single_block(eava__qumzc, (rhs.value,), stmt.
        target, wwy__mdcyt)
    _update_definitions(func_ir, fmugt__sgi)
    new_body += fmugt__sgi
    return True


def _inline_bodo_call(rhs, i, func_mod, func_name, pass_info, new_body,
    block, typingctx, targetctx, calltypes, work_list):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.utils.transform import replace_func, update_locs
    func_ir = pass_info.func_ir
    typemap = pass_info.typemap
    if isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        SeriesType) and func_name not in _series_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        if (func_name in bodo.hiframes.series_impl.explicit_binop_funcs or 
            func_name.startswith('r') and func_name[1:] in bodo.hiframes.
            series_impl.explicit_binop_funcs):
            return False
        rhs.args.insert(0, func_mod)
        wkjx__krzz = tuple(typemap[rzml__mbt.name] for rzml__mbt in rhs.args)
        cij__hqfgd = {xnrcs__bhar: typemap[rzml__mbt.name] for xnrcs__bhar,
            rzml__mbt in dict(rhs.kws).items()}
        eava__qumzc = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*wkjx__krzz, **cij__hqfgd)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        wkjx__krzz = tuple(typemap[rzml__mbt.name] for rzml__mbt in rhs.args)
        cij__hqfgd = {xnrcs__bhar: typemap[rzml__mbt.name] for xnrcs__bhar,
            rzml__mbt in dict(rhs.kws).items()}
        eava__qumzc = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*wkjx__krzz, **cij__hqfgd)
    else:
        return False
    npjy__rzsl = replace_func(pass_info, eava__qumzc, rhs.args, pysig=numba
        .core.utils.pysignature(eava__qumzc), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    icme__lrr, oird__yba = inline_closure_call(func_ir, npjy__rzsl.glbls,
        block, len(new_body), npjy__rzsl.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=npjy__rzsl.arg_types, typemap=typemap,
        calltypes=calltypes, work_list=work_list)
    for hhzl__onqss in icme__lrr.values():
        hhzl__onqss.loc = rhs.loc
        update_locs(hhzl__onqss.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    fjlrp__atqx = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = fjlrp__atqx(func_ir, typemap)
    kaxi__ykjku = func_ir.blocks
    work_list = list((xmbs__lnplg, kaxi__ykjku[xmbs__lnplg]) for
        xmbs__lnplg in reversed(kaxi__ykjku.keys()))
    while work_list:
        rapk__eicj, block = work_list.pop()
        new_body = []
        muimv__iftf = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                qxhve__bhpon = guard(find_callname, func_ir, rhs, typemap)
                if qxhve__bhpon is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = qxhve__bhpon
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    muimv__iftf = True
                    break
            new_body.append(stmt)
        if not muimv__iftf:
            kaxi__ykjku[rapk__eicj].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        tgwoj__sul = DistributedPass(state.func_ir, state.typingctx, state.
            targetctx, state.type_annotation.typemap, state.type_annotation
            .calltypes, state.return_type, state.metadata, state.flags)
        state.return_type = tgwoj__sul.run()
        state.type_annotation.blocks = state.func_ir.blocks
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        pxti__nauqw = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.type_annotation.typemap, state.type_annotation
            .calltypes, state.locals)
        pxti__nauqw.run()
        pxti__nauqw.run()
        pxti__nauqw.run()
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        mau__uxrp = 0
        rtg__vtayn = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            mau__uxrp = int(os.environ[rtg__vtayn])
        except:
            pass
        if mau__uxrp > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(mau__uxrp, state
                .metadata)
        return True


class BodoCompilerSeq(BodoCompiler):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=False,
            inline_calls_pass=inline_all_calls)


class BodoCompilerUDF(BodoCompiler):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=False, udf_pipeline=True)


@register_pass(mutates_CFG=False, analysis_only=True)
class LowerParforSeq(FunctionPass):
    _name = 'bodo_lower_parfor_seq_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        bodo.transforms.distributed_pass.lower_parfor_sequential(state.
            typingctx, state.func_ir, state.typemap, state.calltypes, state
            .metadata)
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class LowerBodoIRExtSeq(FunctionPass):
    _name = 'bodo_lower_ir_ext_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        from bodo.transforms.distributed_pass import distributed_run_extensions
        from bodo.transforms.table_column_del_pass import remove_dead_table_columns
        state.func_ir._definitions = build_definitions(state.func_ir.blocks)
        wwy__mdcyt = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, wwy__mdcyt)
        for block in state.func_ir.blocks.values():
            new_body = []
            for clig__irqz in block.body:
                if type(clig__irqz) in distributed_run_extensions:
                    omzsb__adre = distributed_run_extensions[type(clig__irqz)]
                    usgw__ola = omzsb__adre(clig__irqz, None, state.typemap,
                        state.calltypes, state.typingctx, state.targetctx)
                    new_body += usgw__ola
                elif is_call_assign(clig__irqz):
                    rhs = clig__irqz.value
                    qxhve__bhpon = guard(find_callname, state.func_ir, rhs)
                    if qxhve__bhpon == ('gatherv', 'bodo') or qxhve__bhpon == (
                        'allgatherv', 'bodo'):
                        clig__irqz.value = rhs.args[0]
                    new_body.append(clig__irqz)
                else:
                    new_body.append(clig__irqz)
            block.body = new_body
        state.type_annotation.blocks = state.func_ir.blocks
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        glhs__bgc = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.type_annotation.typemap, state.
            type_annotation.calltypes)
        return glhs__bgc.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    dxwaf__lyca = set()
    while work_list:
        rapk__eicj, block = work_list.pop()
        dxwaf__lyca.add(rapk__eicj)
        for i, perji__npje in enumerate(block.body):
            if isinstance(perji__npje, ir.Assign):
                gwyw__pqx = perji__npje.value
                if isinstance(gwyw__pqx, ir.Expr) and gwyw__pqx.op == 'call':
                    pjtg__ugq = guard(get_definition, func_ir, gwyw__pqx.func)
                    if isinstance(pjtg__ugq, (ir.Global, ir.FreeVar)
                        ) and isinstance(pjtg__ugq.value, CPUDispatcher
                        ) and issubclass(pjtg__ugq.value._compiler.
                        pipeline_class, BodoCompiler):
                        qvkh__vjh = pjtg__ugq.value.py_func
                        arg_types = None
                        if typingctx:
                            gugho__fdp = dict(gwyw__pqx.kws)
                            owra__toy = tuple(typemap[rzml__mbt.name] for
                                rzml__mbt in gwyw__pqx.args)
                            dzx__nsy = {iypcv__xnb: typemap[rzml__mbt.name] for
                                iypcv__xnb, rzml__mbt in gugho__fdp.items()}
                            oird__yba, arg_types = (pjtg__ugq.value.
                                fold_argument_types(owra__toy, dzx__nsy))
                        oird__yba, fpogk__jlp = inline_closure_call(func_ir,
                            qvkh__vjh.__globals__, block, i, qvkh__vjh,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((fpogk__jlp[iypcv__xnb].name,
                            rzml__mbt) for iypcv__xnb, rzml__mbt in
                            pjtg__ugq.value.locals.items() if iypcv__xnb in
                            fpogk__jlp)
                        break
    return dxwaf__lyca


def udf_jit(signature_or_function=None, **options):
    bxmp__mpwvk = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=bxmp__mpwvk,
        pipeline_class=bodo.compiler.BodoCompilerUDF, **options)


def is_udf_call(func_type):
    return isinstance(func_type, numba.core.types.Dispatcher
        ) and func_type.dispatcher._compiler.pipeline_class == BodoCompilerUDF


def is_user_dispatcher(func_type):
    return isinstance(func_type, numba.core.types.functions.ObjModeDispatcher
        ) or isinstance(func_type, numba.core.types.Dispatcher) and issubclass(
        func_type.dispatcher._compiler.pipeline_class, BodoCompiler)


@register_pass(mutates_CFG=False, analysis_only=True)
class DummyCR(FunctionPass):
    _name = 'bodo_dummy_cr'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        state.cr = (state.func_ir, state.typemap, state.calltypes, state.
            return_type)
        return True


def remove_passes_after(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for oottw__lupu, (x, oird__yba) in enumerate(pm.passes):
        if x == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:oottw__lupu + 1]
    pm._finalized = False


class TyperCompiler(BodoCompiler):

    def define_pipelines(self):
        [pm] = self._create_bodo_pipeline()
        remove_passes_after(pm, InlineOverloads)
        pm.add_pass_after(DummyCR, InlineOverloads)
        pm.finalize()
        return [pm]


def get_func_type_info(func, arg_types, kw_types):
    typingctx = numba.core.registry.cpu_target.typing_context
    targetctx = numba.core.registry.cpu_target.target_context
    oii__fiy = None
    iuu__acwq = None
    _locals = {}
    rqiqb__atc = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(rqiqb__atc, arg_types,
        kw_types)
    anmaq__lbge = numba.core.compiler.Flags()
    jhx__ozwfe = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    oqxaf__ghfwc = {'nopython': True, 'boundscheck': False, 'parallel':
        jhx__ozwfe}
    numba.core.registry.cpu_target.options.parse_as_flags(anmaq__lbge,
        oqxaf__ghfwc)
    dtm__bqmu = TyperCompiler(typingctx, targetctx, oii__fiy, args,
        iuu__acwq, anmaq__lbge, _locals)
    return dtm__bqmu.compile_extra(func)
