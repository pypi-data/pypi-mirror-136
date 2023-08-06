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
except ImportError as lvw__hhyu:
    pass
_matplotlib_installed = False
try:
    import matplotlib
    import bodo.libs.matplotlib_ext
    _matplotlib_installed = True
except ImportError as lvw__hhyu:
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
except ImportError as lvw__hhyu:
    pass
import bodo.hiframes.dataframe_indexing
import bodo.hiframes.datetime_datetime_ext
import bodo.hiframes.datetime_timedelta_ext
try:
    import xgboost
    import bodo.libs.xgb_ext
except ImportError as lvw__hhyu:
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
        zva__hhh = 'bodo' if distributed else 'bodo_seq'
        zva__hhh = zva__hhh + '_inline' if inline_calls_pass else zva__hhh
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, zva__hhh)
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
    for bakt__uwqu, (x, mfy__yvdkm) in enumerate(pm.passes):
        if x == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(bakt__uwqu, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for bakt__uwqu, (x, mfy__yvdkm) in enumerate(pm.passes):
        if x == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[bakt__uwqu] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for bakt__uwqu, (x, mfy__yvdkm) in enumerate(pm.passes):
        if x == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(bakt__uwqu)
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
    cbms__uxmam = guard(get_definition, func_ir, rhs.func)
    if isinstance(cbms__uxmam, (ir.Global, ir.FreeVar, ir.Const)):
        qqit__zvnce = cbms__uxmam.value
    else:
        tzq__yucyu = guard(find_callname, func_ir, rhs)
        if not (tzq__yucyu and isinstance(tzq__yucyu[0], str) and
            isinstance(tzq__yucyu[1], str)):
            return
        func_name, func_mod = tzq__yucyu
        try:
            import importlib
            svh__ngcje = importlib.import_module(func_mod)
            qqit__zvnce = getattr(svh__ngcje, func_name)
        except:
            return
    if isinstance(qqit__zvnce, CPUDispatcher) and issubclass(qqit__zvnce.
        _compiler.pipeline_class, BodoCompiler
        ) and qqit__zvnce._compiler.pipeline_class != BodoCompilerUDF:
        qqit__zvnce._compiler.pipeline_class = BodoCompilerUDF


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for rwzv__lilf in block.body:
                if is_call_assign(rwzv__lilf):
                    _convert_bodo_dispatcher_to_udf(rwzv__lilf.value, state
                        .func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        hxgmy__nnshl = UntypedPass(state.func_ir, state.typingctx, state.
            args, state.locals, state.metadata, state.flags)
        hxgmy__nnshl.run()
        return True


def _update_definitions(func_ir, node_list):
    ufj__zofck = ir.Loc('', 0)
    ummhw__fln = ir.Block(ir.Scope(None, ufj__zofck), ufj__zofck)
    ummhw__fln.body = node_list
    build_definitions({(0): ummhw__fln}, func_ir._definitions)


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
        miii__wlfnz = 'overload_series_' + rhs.attr
        meq__wlp = getattr(bodo.hiframes.series_impl, miii__wlfnz)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        miii__wlfnz = 'overload_dataframe_' + rhs.attr
        meq__wlp = getattr(bodo.hiframes.dataframe_impl, miii__wlfnz)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    gem__wpi = meq__wlp(rhs_type)
    wgi__itsb = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    znzw__ikei = compile_func_single_block(gem__wpi, (rhs.value,), stmt.
        target, wgi__itsb)
    _update_definitions(func_ir, znzw__ikei)
    new_body += znzw__ikei
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
        ofo__pmhq = tuple(typemap[itgx__vfh.name] for itgx__vfh in rhs.args)
        cpwia__gdat = {zva__hhh: typemap[itgx__vfh.name] for zva__hhh,
            itgx__vfh in dict(rhs.kws).items()}
        gem__wpi = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*ofo__pmhq, **cpwia__gdat)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        ofo__pmhq = tuple(typemap[itgx__vfh.name] for itgx__vfh in rhs.args)
        cpwia__gdat = {zva__hhh: typemap[itgx__vfh.name] for zva__hhh,
            itgx__vfh in dict(rhs.kws).items()}
        gem__wpi = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*ofo__pmhq, **cpwia__gdat)
    else:
        return False
    xnefl__boek = replace_func(pass_info, gem__wpi, rhs.args, pysig=numba.
        core.utils.pysignature(gem__wpi), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    yph__cgmo, mfy__yvdkm = inline_closure_call(func_ir, xnefl__boek.glbls,
        block, len(new_body), xnefl__boek.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=xnefl__boek.arg_types, typemap=
        typemap, calltypes=calltypes, work_list=work_list)
    for zls__lfpzv in yph__cgmo.values():
        zls__lfpzv.loc = rhs.loc
        update_locs(zls__lfpzv.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    xul__ikagf = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = xul__ikagf(func_ir, typemap)
    jgaiu__mdd = func_ir.blocks
    work_list = list((hrfe__lhtrl, jgaiu__mdd[hrfe__lhtrl]) for hrfe__lhtrl in
        reversed(jgaiu__mdd.keys()))
    while work_list:
        lgjcd__kbjyq, block = work_list.pop()
        new_body = []
        kkuli__dod = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                tzq__yucyu = guard(find_callname, func_ir, rhs, typemap)
                if tzq__yucyu is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = tzq__yucyu
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    kkuli__dod = True
                    break
            new_body.append(stmt)
        if not kkuli__dod:
            jgaiu__mdd[lgjcd__kbjyq].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        coso__uoc = DistributedPass(state.func_ir, state.typingctx, state.
            targetctx, state.type_annotation.typemap, state.type_annotation
            .calltypes, state.return_type, state.metadata, state.flags)
        state.return_type = coso__uoc.run()
        state.type_annotation.blocks = state.func_ir.blocks
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        gbz__mknh = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.type_annotation.typemap, state.type_annotation
            .calltypes, state.locals)
        gbz__mknh.run()
        gbz__mknh.run()
        gbz__mknh.run()
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        ookg__shmqk = 0
        gpjp__rrm = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            ookg__shmqk = int(os.environ[gpjp__rrm])
        except:
            pass
        if ookg__shmqk > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(ookg__shmqk,
                state.metadata)
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
        wgi__itsb = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, wgi__itsb)
        for block in state.func_ir.blocks.values():
            new_body = []
            for rwzv__lilf in block.body:
                if type(rwzv__lilf) in distributed_run_extensions:
                    lmopt__kva = distributed_run_extensions[type(rwzv__lilf)]
                    nnh__vtbdo = lmopt__kva(rwzv__lilf, None, state.typemap,
                        state.calltypes, state.typingctx, state.targetctx)
                    new_body += nnh__vtbdo
                elif is_call_assign(rwzv__lilf):
                    rhs = rwzv__lilf.value
                    tzq__yucyu = guard(find_callname, state.func_ir, rhs)
                    if tzq__yucyu == ('gatherv', 'bodo') or tzq__yucyu == (
                        'allgatherv', 'bodo'):
                        rwzv__lilf.value = rhs.args[0]
                    new_body.append(rwzv__lilf)
                else:
                    new_body.append(rwzv__lilf)
            block.body = new_body
        state.type_annotation.blocks = state.func_ir.blocks
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        pjn__jnfp = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.type_annotation.typemap, state.
            type_annotation.calltypes)
        return pjn__jnfp.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    ajq__uqx = set()
    while work_list:
        lgjcd__kbjyq, block = work_list.pop()
        ajq__uqx.add(lgjcd__kbjyq)
        for i, eev__tzv in enumerate(block.body):
            if isinstance(eev__tzv, ir.Assign):
                bzmlx__svag = eev__tzv.value
                if isinstance(bzmlx__svag, ir.Expr
                    ) and bzmlx__svag.op == 'call':
                    cbms__uxmam = guard(get_definition, func_ir,
                        bzmlx__svag.func)
                    if isinstance(cbms__uxmam, (ir.Global, ir.FreeVar)
                        ) and isinstance(cbms__uxmam.value, CPUDispatcher
                        ) and issubclass(cbms__uxmam.value._compiler.
                        pipeline_class, BodoCompiler):
                        olxg__oib = cbms__uxmam.value.py_func
                        arg_types = None
                        if typingctx:
                            rvvyi__ecegm = dict(bzmlx__svag.kws)
                            fsds__uij = tuple(typemap[itgx__vfh.name] for
                                itgx__vfh in bzmlx__svag.args)
                            llfzv__ndt = {zfphi__ngrar: typemap[itgx__vfh.
                                name] for zfphi__ngrar, itgx__vfh in
                                rvvyi__ecegm.items()}
                            mfy__yvdkm, arg_types = (cbms__uxmam.value.
                                fold_argument_types(fsds__uij, llfzv__ndt))
                        mfy__yvdkm, nayeb__qqhdp = inline_closure_call(func_ir,
                            olxg__oib.__globals__, block, i, olxg__oib,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((nayeb__qqhdp[zfphi__ngrar].name,
                            itgx__vfh) for zfphi__ngrar, itgx__vfh in
                            cbms__uxmam.value.locals.items() if 
                            zfphi__ngrar in nayeb__qqhdp)
                        break
    return ajq__uqx


def udf_jit(signature_or_function=None, **options):
    jjjf__ilfc = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=jjjf__ilfc,
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
    for bakt__uwqu, (x, mfy__yvdkm) in enumerate(pm.passes):
        if x == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:bakt__uwqu + 1]
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
    bqoxx__gtl = None
    lmai__goyph = None
    _locals = {}
    ozh__jldk = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(ozh__jldk, arg_types,
        kw_types)
    kmj__itzrv = numba.core.compiler.Flags()
    katq__bgpa = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    tbswl__taie = {'nopython': True, 'boundscheck': False, 'parallel':
        katq__bgpa}
    numba.core.registry.cpu_target.options.parse_as_flags(kmj__itzrv,
        tbswl__taie)
    ffqdk__vvh = TyperCompiler(typingctx, targetctx, bqoxx__gtl, args,
        lmai__goyph, kmj__itzrv, _locals)
    return ffqdk__vvh.compile_extra(func)
