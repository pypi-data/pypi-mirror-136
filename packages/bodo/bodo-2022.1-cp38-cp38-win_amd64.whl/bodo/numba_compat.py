"""
Numba monkey patches to fix issues related to Bodo. Should be imported before any
other module in bodo package.
"""
import copy
import functools
import hashlib
import inspect
import itertools
import operator
import os
import re
import sys
import textwrap
import traceback
import types as pytypes
import warnings
from collections import OrderedDict
from collections.abc import Sequence
from contextlib import ExitStack
import numba
import numba.core.boxing
import numba.core.inline_closurecall
import numba.np.linalg
from numba.core import analysis, cgutils, errors, ir, ir_utils, types
from numba.core.compiler import Compiler
from numba.core.errors import ForceLiteralArg, LiteralTypingError, TypingError
from numba.core.ir_utils import GuardException, _create_function_from_code_obj, analysis, build_definitions, find_callname, guard, has_no_side_effect, mk_unique_var, remove_dead_extensions, replace_vars_inner, require, visit_vars_extensions, visit_vars_inner
from numba.core.types import literal
from numba.core.types.functions import _bt_as_lines, _ResolutionFailures, _termcolor, _unlit_non_poison
from numba.core.typing.templates import AbstractTemplate, Signature, _EmptyImplementationEntry, _inline_info, _OverloadAttributeTemplate, infer_global, signature
from numba.core.typing.typeof import Purpose, typeof
from numba.experimental.jitclass import base as jitclass_base
from numba.experimental.jitclass import decorators as jitclass_decorators
from numba.extending import NativeValue, lower_builtin, typeof_impl
from numba.parfors.parfor import get_expr_args
from bodo.utils.typing import BodoError
_check_numba_change = False
numba.core.typing.templates._IntrinsicTemplate.prefer_literal = True


def run_frontend(func, inline_closures=False, emit_dels=False):
    evt__nzpn = numba.core.bytecode.FunctionIdentity.from_function(func)
    sma__xdl = numba.core.interpreter.Interpreter(evt__nzpn)
    snrg__wcht = numba.core.bytecode.ByteCode(func_id=evt__nzpn)
    func_ir = sma__xdl.interpret(snrg__wcht)
    if inline_closures:
        from numba.core.inline_closurecall import InlineClosureCallPass


        class DummyPipeline:

            def __init__(self, f_ir):
                self.state = numba.core.compiler.StateDict()
                self.state.typingctx = None
                self.state.targetctx = None
                self.state.args = None
                self.state.func_ir = f_ir
                self.state.typemap = None
                self.state.return_type = None
                self.state.calltypes = None
        numba.core.rewrites.rewrite_registry.apply('before-inference',
            DummyPipeline(func_ir).state)
        zrf__eql = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        zrf__eql.run()
    lgkh__msgnq = numba.core.postproc.PostProcessor(func_ir)
    lgkh__msgnq.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, qav__tpvlc in visit_vars_extensions.items():
        if isinstance(stmt, t):
            qav__tpvlc(stmt, callback, cbdata)
            return
    if isinstance(stmt, ir.Assign):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Arg):
        stmt.name = visit_vars_inner(stmt.name, callback, cbdata)
    elif isinstance(stmt, ir.Return):
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Raise):
        stmt.exception = visit_vars_inner(stmt.exception, callback, cbdata)
    elif isinstance(stmt, ir.Branch):
        stmt.cond = visit_vars_inner(stmt.cond, callback, cbdata)
    elif isinstance(stmt, ir.Jump):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
    elif isinstance(stmt, ir.Del):
        var = ir.Var(None, stmt.value, stmt.loc)
        var = visit_vars_inner(var, callback, cbdata)
        stmt.value = var.name
    elif isinstance(stmt, ir.DelAttr):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.attr = visit_vars_inner(stmt.attr, callback, cbdata)
    elif isinstance(stmt, ir.SetAttr):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.attr = visit_vars_inner(stmt.attr, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.DelItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index = visit_vars_inner(stmt.index, callback, cbdata)
    elif isinstance(stmt, ir.StaticSetItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index_var = visit_vars_inner(stmt.index_var, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.SetItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index = visit_vars_inner(stmt.index, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Print):
        stmt.args = [visit_vars_inner(x, callback, cbdata) for x in stmt.args]
        stmt.vararg = visit_vars_inner(stmt.vararg, callback, cbdata)
    else:
        pass
    return


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.visit_vars_stmt)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '52b7b645ba65c35f3cf564f936e113261db16a2dff1e80fbee2459af58844117':
        warnings.warn('numba.core.ir_utils.visit_vars_stmt has changed')
numba.core.ir_utils.visit_vars_stmt = visit_vars_stmt
old_run_pass = numba.core.typed_passes.InlineOverloads.run_pass


def InlineOverloads_run_pass(self, state):
    import bodo
    bodo.compiler.bodo_overload_inline_pass(state.func_ir, state.typingctx,
        state.targetctx, state.typemap, state.calltypes)
    return old_run_pass(self, state)


numba.core.typed_passes.InlineOverloads.run_pass = InlineOverloads_run_pass
from numba.core.ir_utils import _add_alias, alias_analysis_extensions, alias_func_extensions
_immutable_type_class = (types.Number, types.scalars._NPDatetimeBase, types
    .iterators.RangeType, types.UnicodeType)


def is_immutable_type(var, typemap):
    if typemap is None or var not in typemap:
        return False
    typ = typemap[var]
    if isinstance(typ, _immutable_type_class):
        return True
    if isinstance(typ, types.BaseTuple) and all(isinstance(t,
        _immutable_type_class) for t in typ.types):
        return True
    return False


def find_potential_aliases(blocks, args, typemap, func_ir, alias_map=None,
    arg_aliases=None):
    if alias_map is None:
        alias_map = {}
    if arg_aliases is None:
        arg_aliases = set(a for a in args if not is_immutable_type(a, typemap))
    func_ir._definitions = build_definitions(func_ir.blocks)
    bev__gee = ['ravel', 'transpose', 'reshape']
    for ycvv__orkv in blocks.values():
        for kse__pzpp in ycvv__orkv.body:
            if type(kse__pzpp) in alias_analysis_extensions:
                qav__tpvlc = alias_analysis_extensions[type(kse__pzpp)]
                qav__tpvlc(kse__pzpp, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(kse__pzpp, ir.Assign):
                ablyj__afu = kse__pzpp.value
                zwzza__sqf = kse__pzpp.target.name
                if is_immutable_type(zwzza__sqf, typemap):
                    continue
                if isinstance(ablyj__afu, ir.Var
                    ) and zwzza__sqf != ablyj__afu.name:
                    _add_alias(zwzza__sqf, ablyj__afu.name, alias_map,
                        arg_aliases)
                if isinstance(ablyj__afu, ir.Expr) and (ablyj__afu.op ==
                    'cast' or ablyj__afu.op in ['getitem', 'static_getitem']):
                    _add_alias(zwzza__sqf, ablyj__afu.value.name, alias_map,
                        arg_aliases)
                if isinstance(ablyj__afu, ir.Expr
                    ) and ablyj__afu.op == 'inplace_binop':
                    _add_alias(zwzza__sqf, ablyj__afu.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(ablyj__afu, ir.Expr
                    ) and ablyj__afu.op == 'getattr' and ablyj__afu.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(zwzza__sqf, ablyj__afu.value.name, alias_map,
                        arg_aliases)
                if isinstance(ablyj__afu, ir.Expr
                    ) and ablyj__afu.op == 'getattr' and ablyj__afu.attr not in [
                    'shape'] and ablyj__afu.value.name in arg_aliases:
                    _add_alias(zwzza__sqf, ablyj__afu.value.name, alias_map,
                        arg_aliases)
                if isinstance(ablyj__afu, ir.Expr
                    ) and ablyj__afu.op == 'getattr' and ablyj__afu.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(zwzza__sqf, ablyj__afu.value.name, alias_map,
                        arg_aliases)
                if isinstance(ablyj__afu, ir.Expr) and ablyj__afu.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(zwzza__sqf, typemap):
                    for ehma__wxyyj in ablyj__afu.items:
                        _add_alias(zwzza__sqf, ehma__wxyyj.name, alias_map,
                            arg_aliases)
                if isinstance(ablyj__afu, ir.Expr) and ablyj__afu.op == 'call':
                    lrazt__ocmdp = guard(find_callname, func_ir, ablyj__afu,
                        typemap)
                    if lrazt__ocmdp is None:
                        continue
                    dlywj__qrn, bmjbc__ekn = lrazt__ocmdp
                    if lrazt__ocmdp in alias_func_extensions:
                        hqfg__qmn = alias_func_extensions[lrazt__ocmdp]
                        hqfg__qmn(zwzza__sqf, ablyj__afu.args, alias_map,
                            arg_aliases)
                    if bmjbc__ekn == 'numpy' and dlywj__qrn in bev__gee:
                        _add_alias(zwzza__sqf, ablyj__afu.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(bmjbc__ekn, ir.Var
                        ) and dlywj__qrn in bev__gee:
                        _add_alias(zwzza__sqf, bmjbc__ekn.name, alias_map,
                            arg_aliases)
    qawya__wobq = copy.deepcopy(alias_map)
    for ehma__wxyyj in qawya__wobq:
        for uglf__zznrd in qawya__wobq[ehma__wxyyj]:
            alias_map[ehma__wxyyj] |= alias_map[uglf__zznrd]
        for uglf__zznrd in qawya__wobq[ehma__wxyyj]:
            alias_map[uglf__zznrd] = alias_map[ehma__wxyyj]
    return alias_map, arg_aliases


if _check_numba_change:
    lines = inspect.getsource(ir_utils.find_potential_aliases)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'e6cf3e0f502f903453eb98346fc6854f87dc4ea1ac62f65c2d6aef3bf690b6c5':
        warnings.warn('ir_utils.find_potential_aliases has changed')
ir_utils.find_potential_aliases = find_potential_aliases
numba.parfors.array_analysis.find_potential_aliases = find_potential_aliases
if _check_numba_change:
    lines = inspect.getsource(ir_utils.dead_code_elimination)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '40a8626300a1a17523944ec7842b093c91258bbc60844bbd72191a35a4c366bf':
        warnings.warn('ir_utils.dead_code_elimination has changed')


def mini_dce(func_ir, typemap=None, alias_map=None, arg_aliases=None):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    cwmwn__ydbt = compute_cfg_from_blocks(func_ir.blocks)
    jprw__mkmj = compute_use_defs(func_ir.blocks)
    ysaj__heg = compute_live_map(cwmwn__ydbt, func_ir.blocks, jprw__mkmj.
        usemap, jprw__mkmj.defmap)
    for wng__cmyxl, block in func_ir.blocks.items():
        lives = {ehma__wxyyj.name for ehma__wxyyj in block.terminator.
            list_vars()}
        for vnlku__jvao, rqxyq__wpx in cwmwn__ydbt.successors(wng__cmyxl):
            lives |= ysaj__heg[vnlku__jvao]
        kdh__jnswm = [block.terminator]
        for stmt in reversed(block.body[:-1]):
            if isinstance(stmt, ir.Assign):
                zwzza__sqf = stmt.target
                cjr__kmmhu = stmt.value
                if zwzza__sqf.name not in lives:
                    if isinstance(cjr__kmmhu, ir.Expr
                        ) and cjr__kmmhu.op == 'make_function':
                        continue
                    if isinstance(cjr__kmmhu, ir.Expr
                        ) and cjr__kmmhu.op == 'getattr':
                        continue
                    if isinstance(cjr__kmmhu, ir.Const):
                        continue
                    if typemap and isinstance(typemap.get(zwzza__sqf, None),
                        types.Function):
                        continue
                if isinstance(cjr__kmmhu, ir.Var
                    ) and zwzza__sqf.name == cjr__kmmhu.name:
                    continue
            if isinstance(stmt, ir.Del):
                if stmt.value not in lives:
                    continue
            if type(stmt) in analysis.ir_extension_usedefs:
                toag__cei = analysis.ir_extension_usedefs[type(stmt)]
                wuxox__yjbep, qsx__snz = toag__cei(stmt)
                lives -= qsx__snz
                lives |= wuxox__yjbep
            else:
                lives |= {ehma__wxyyj.name for ehma__wxyyj in stmt.list_vars()}
                if isinstance(stmt, ir.Assign):
                    lives.remove(zwzza__sqf.name)
            kdh__jnswm.append(stmt)
        kdh__jnswm.reverse()
        block.body = kdh__jnswm


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    feb__ptk = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (feb__ptk,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    hcilb__mrg = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), hcilb__mrg)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        make_overload_template)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '7f6974584cb10e49995b652827540cc6732e497c0b9f8231b44fd83fcc1c0a83':
        warnings.warn(
            'numba.core.typing.templates.make_overload_template has changed')
numba.core.typing.templates.make_overload_template = make_overload_template


def _resolve(self, typ, attr):
    if self._attr != attr:
        return None
    if isinstance(typ, types.TypeRef):
        assert typ == self.key
    else:
        assert isinstance(typ, self.key)


    class MethodTemplate(AbstractTemplate):
        key = self.key, attr
        _inline = self._inline
        _no_unliteral = getattr(self, '_no_unliteral', False)
        _overload_func = staticmethod(self._overload_func)
        _inline_overloads = self._inline_overloads
        prefer_literal = self.prefer_literal

        def generic(_, args, kws):
            args = (typ,) + tuple(args)
            fnty = self._get_function_type(self.context, typ)
            sig = self._get_signature(self.context, fnty, args, kws)
            sig = sig.replace(pysig=numba.core.utils.pysignature(self.
                _overload_func))
            for zglr__wan in fnty.templates:
                self._inline_overloads.update(zglr__wan._inline_overloads)
            if sig is not None:
                return sig.as_method()
    return types.BoundFunction(MethodTemplate, typ)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadMethodTemplate._resolve)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'ce8e0935dc939d0867ef969e1ed2975adb3533a58a4133fcc90ae13c4418e4d6':
        warnings.warn(
            'numba.core.typing.templates._OverloadMethodTemplate._resolve has changed'
            )
numba.core.typing.templates._OverloadMethodTemplate._resolve = _resolve


def make_overload_attribute_template(typ, attr, overload_func, inline,
    prefer_literal=False, base=_OverloadAttributeTemplate, **kwargs):
    assert isinstance(typ, types.Type) or issubclass(typ, types.Type)
    name = 'OverloadAttributeTemplate_%s_%s' % (typ, attr)
    no_unliteral = kwargs.pop('no_unliteral', False)
    hcilb__mrg = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), hcilb__mrg)
    return obj


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        make_overload_attribute_template)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f066c38c482d6cf8bf5735a529c3264118ba9b52264b24e58aad12a6b1960f5d':
        warnings.warn(
            'numba.core.typing.templates.make_overload_attribute_template has changed'
            )
numba.core.typing.templates.make_overload_attribute_template = (
    make_overload_attribute_template)


def generic(self, args, kws):
    from numba.core.typed_passes import PreLowerStripPhis
    mpcr__euig, sgkwl__oqe = self._get_impl(args, kws)
    if mpcr__euig is None:
        return
    exs__pvay = types.Dispatcher(mpcr__euig)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        giq__gwxq = mpcr__euig._compiler
        flags = compiler.Flags()
        emh__pul = giq__gwxq.targetdescr.typing_context
        vyuw__vkwd = giq__gwxq.targetdescr.target_context
        ragz__cvojb = giq__gwxq.pipeline_class(emh__pul, vyuw__vkwd, None,
            None, None, flags, None)
        mtit__dxv = InlineWorker(emh__pul, vyuw__vkwd, giq__gwxq.locals,
            ragz__cvojb, flags, None)
        dsiz__mmdm = exs__pvay.dispatcher.get_call_template
        zglr__wan, fur__lyqmc, irj__fjsou, kws = dsiz__mmdm(sgkwl__oqe, kws)
        if irj__fjsou in self._inline_overloads:
            return self._inline_overloads[irj__fjsou]['iinfo'].signature
        ir = mtit__dxv.run_untyped_passes(exs__pvay.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, vyuw__vkwd, ir, irj__fjsou, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, irj__fjsou, None)
        self._inline_overloads[sig.args] = {'folded_args': irj__fjsou}
        bvg__zmw = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = bvg__zmw
        if not self._inline.is_always_inline:
            sig = exs__pvay.get_call_type(self.context, sgkwl__oqe, kws)
            self._compiled_overloads[sig.args] = exs__pvay.get_overload(sig)
        jvua__eatm = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': irj__fjsou,
            'iinfo': jvua__eatm}
    else:
        sig = exs__pvay.get_call_type(self.context, sgkwl__oqe, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = exs__pvay.get_overload(sig)
    return sig


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadFunctionTemplate.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5d453a6d0215ebf0bab1279ff59eb0040b34938623be99142ce20acc09cdeb64':
        warnings.warn(
            'numba.core.typing.templates._OverloadFunctionTemplate.generic has changed'
            )
numba.core.typing.templates._OverloadFunctionTemplate.generic = generic


def bound_function(template_key, no_unliteral=False):

    def wrapper(method_resolver):

        @functools.wraps(method_resolver)
        def attribute_resolver(self, ty):


            class MethodTemplate(AbstractTemplate):
                key = template_key

                def generic(_, args, kws):
                    sig = method_resolver(self, ty, args, kws)
                    if sig is not None and sig.recvr is None:
                        sig = sig.replace(recvr=ty)
                    return sig
            MethodTemplate._no_unliteral = no_unliteral
            return types.BoundFunction(MethodTemplate, ty)
        return attribute_resolver
    return wrapper


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.bound_function)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a2feefe64eae6a15c56affc47bf0c1d04461f9566913442d539452b397103322':
        warnings.warn('numba.core.typing.templates.bound_function has changed')
numba.core.typing.templates.bound_function = bound_function


def get_call_type(self, context, args, kws):
    from numba.core import utils
    hnlh__esh = [True, False]
    mrkp__mavhp = [False, True]
    kicys__frxa = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    ciz__ren = get_local_target(context)
    vzjmn__kini = utils.order_by_target_specificity(ciz__ren, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for tdq__air in vzjmn__kini:
        bujky__qlrsa = tdq__air(context)
        xfpw__kabd = hnlh__esh if bujky__qlrsa.prefer_literal else mrkp__mavhp
        xfpw__kabd = [True] if getattr(bujky__qlrsa, '_no_unliteral', False
            ) else xfpw__kabd
        for ndsop__oithz in xfpw__kabd:
            try:
                if ndsop__oithz:
                    sig = bujky__qlrsa.apply(args, kws)
                else:
                    ibbw__cccfv = tuple([_unlit_non_poison(a) for a in args])
                    ivdge__gcav = {qxb__lygvj: _unlit_non_poison(
                        ehma__wxyyj) for qxb__lygvj, ehma__wxyyj in kws.items()
                        }
                    sig = bujky__qlrsa.apply(ibbw__cccfv, ivdge__gcav)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    kicys__frxa.add_error(bujky__qlrsa, False, e, ndsop__oithz)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = bujky__qlrsa.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    brff__rzzx = getattr(bujky__qlrsa, 'cases', None)
                    if brff__rzzx is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            brff__rzzx)
                    else:
                        msg = 'No match.'
                    kicys__frxa.add_error(bujky__qlrsa, True, msg, ndsop__oithz
                        )
    kicys__frxa.raise_error()


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.BaseFunction.
        get_call_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '25f038a7216f8e6f40068ea81e11fd9af8ad25d19888f7304a549941b01b7015':
        warnings.warn(
            'numba.core.types.functions.BaseFunction.get_call_type has changed'
            )
numba.core.types.functions.BaseFunction.get_call_type = get_call_type
bodo_typing_error_info = """
This is often caused by the use of unsupported features or typing issues.
See https://docs.bodo.ai/
"""


def get_call_type2(self, context, args, kws):
    zglr__wan = self.template(context)
    opyhr__yffa = None
    isvn__azcr = None
    kps__omn = None
    xfpw__kabd = [True, False] if zglr__wan.prefer_literal else [False, True]
    xfpw__kabd = [True] if getattr(zglr__wan, '_no_unliteral', False
        ) else xfpw__kabd
    for ndsop__oithz in xfpw__kabd:
        if ndsop__oithz:
            try:
                kps__omn = zglr__wan.apply(args, kws)
            except Exception as tmnl__vkeb:
                if isinstance(tmnl__vkeb, errors.ForceLiteralArg):
                    raise tmnl__vkeb
                opyhr__yffa = tmnl__vkeb
                kps__omn = None
            else:
                break
        else:
            xntcf__jxp = tuple([_unlit_non_poison(a) for a in args])
            oar__brn = {qxb__lygvj: _unlit_non_poison(ehma__wxyyj) for 
                qxb__lygvj, ehma__wxyyj in kws.items()}
            vivvw__bvn = xntcf__jxp == args and kws == oar__brn
            if not vivvw__bvn and kps__omn is None:
                try:
                    kps__omn = zglr__wan.apply(xntcf__jxp, oar__brn)
                except Exception as tmnl__vkeb:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        tmnl__vkeb, errors.NumbaError):
                        raise tmnl__vkeb
                    if isinstance(tmnl__vkeb, errors.ForceLiteralArg):
                        if zglr__wan.prefer_literal:
                            raise tmnl__vkeb
                    isvn__azcr = tmnl__vkeb
                else:
                    break
    if kps__omn is None and (isvn__azcr is not None or opyhr__yffa is not None
        ):
        agkro__svq = '- Resolution failure for {} arguments:\n{}\n'
        qja__tzma = _termcolor.highlight(agkro__svq)
        if numba.core.config.DEVELOPER_MODE:
            iyfo__tjraj = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    aedo__ypa = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    aedo__ypa = ['']
                rul__wylog = '\n{}'.format(2 * iyfo__tjraj)
                hciei__zvfhd = _termcolor.reset(rul__wylog + rul__wylog.
                    join(_bt_as_lines(aedo__ypa)))
                return _termcolor.reset(hciei__zvfhd)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            bai__eyc = str(e)
            bai__eyc = bai__eyc if bai__eyc else str(repr(e)) + add_bt(e)
            uhyb__ptw = errors.TypingError(textwrap.dedent(bai__eyc))
            return qja__tzma.format(literalness, str(uhyb__ptw))
        import bodo
        if isinstance(opyhr__yffa, bodo.utils.typing.BodoError):
            raise opyhr__yffa
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', opyhr__yffa) +
                nested_msg('non-literal', isvn__azcr))
        else:
            msg = 'Compilation error for '
            if isinstance(self.this, bodo.hiframes.pd_dataframe_ext.
                DataFrameType):
                msg += 'DataFrame.'
            elif isinstance(self.this, bodo.hiframes.pd_series_ext.SeriesType):
                msg += 'Series.'
            msg += f'{self.typing_key[1]}().{bodo_typing_error_info}'
            raise errors.TypingError(msg)
    return kps__omn


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.BoundFunction.
        get_call_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '502cd77c0084452e903a45a0f1f8107550bfbde7179363b57dabd617ce135f4a':
        warnings.warn(
            'numba.core.types.functions.BoundFunction.get_call_type has changed'
            )
numba.core.types.functions.BoundFunction.get_call_type = get_call_type2


def string_from_string_and_size(self, string, size):
    from llvmlite.llvmpy.core import Type
    fnty = Type.function(self.pyobj, [self.cstring, self.py_ssize_t])
    dlywj__qrn = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=dlywj__qrn)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            bxdn__bqx = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), bxdn__bqx)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    qyt__nkj = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            qyt__nkj.append(types.Omitted(a.value))
        else:
            qyt__nkj.append(self.typeof_pyval(a))
    cchlb__dwdur = None
    try:
        error = None
        cchlb__dwdur = self.compile(tuple(qyt__nkj))
    except errors.ForceLiteralArg as e:
        ayiq__cohun = [gfxjm__emmfw for gfxjm__emmfw in e.requested_args if
            isinstance(args[gfxjm__emmfw], types.Literal) and not
            isinstance(args[gfxjm__emmfw], types.LiteralStrKeyDict)]
        if ayiq__cohun:
            snb__rrrnv = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            cffe__mdx = ', '.join('Arg #{} is {}'.format(gfxjm__emmfw, args
                [gfxjm__emmfw]) for gfxjm__emmfw in sorted(ayiq__cohun))
            raise errors.CompilerError(snb__rrrnv.format(cffe__mdx))
        sgkwl__oqe = []
        try:
            for gfxjm__emmfw, ehma__wxyyj in enumerate(args):
                if gfxjm__emmfw in e.requested_args:
                    if gfxjm__emmfw in e.file_infos:
                        sgkwl__oqe.append(types.FilenameType(args[
                            gfxjm__emmfw], e.file_infos[gfxjm__emmfw]))
                    else:
                        sgkwl__oqe.append(types.literal(args[gfxjm__emmfw]))
                else:
                    sgkwl__oqe.append(args[gfxjm__emmfw])
            args = sgkwl__oqe
        except (OSError, FileNotFoundError) as rtin__buhzz:
            error = FileNotFoundError(str(rtin__buhzz) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                cchlb__dwdur = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        vxl__edkg = []
        for gfxjm__emmfw, lyv__ugph in enumerate(args):
            val = lyv__ugph.value if isinstance(lyv__ugph, numba.core.
                dispatcher.OmittedArg) else lyv__ugph
            try:
                snj__ljfd = typeof(val, Purpose.argument)
            except ValueError as sjps__rhe:
                vxl__edkg.append((gfxjm__emmfw, str(sjps__rhe)))
            else:
                if snj__ljfd is None:
                    vxl__edkg.append((gfxjm__emmfw,
                        f'cannot determine Numba type of value {val}'))
        if vxl__edkg:
            fiyha__fxnc = '\n'.join(
                f'- argument {gfxjm__emmfw}: {ffvt__ymdp}' for gfxjm__emmfw,
                ffvt__ymdp in vxl__edkg)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{fiyha__fxnc}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                hgb__nusm = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'numba', 'Overload',
                    'lowering']
                cqf__cov = False
                for jgfq__qjk in hgb__nusm:
                    if jgfq__qjk in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        cqf__cov = True
                        break
                if not cqf__cov:
                    msg = f'{str(e)}'
                msg += '\n' + e.loc.strformat() + '\n'
                e.patch_message(msg)
        error_rewrite(e, 'typing')
    except errors.UnsupportedError as e:
        error_rewrite(e, 'unsupported_error')
    except (errors.NotDefinedError, errors.RedefinedError, errors.
        VerificationError) as e:
        error_rewrite(e, 'interpreter')
    except errors.ConstantInferenceError as e:
        error_rewrite(e, 'constant_inference')
    except bodo.utils.typing.BodoError as e:
        error = bodo.utils.typing.BodoError(str(e))
    except Exception as e:
        if numba.core.config.SHOW_HELP:
            if hasattr(e, 'patch_message'):
                bxdn__bqx = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), bxdn__bqx)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return cchlb__dwdur


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher._DispatcherBase.
        _compile_for_args)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5cdfbf0b13a528abf9f0408e70f67207a03e81d610c26b1acab5b2dc1f79bf06':
        warnings.warn(
            'numba.core.dispatcher._DispatcherBase._compile_for_args has changed'
            )
numba.core.dispatcher._DispatcherBase._compile_for_args = _compile_for_args


def resolve_gb_agg_funcs(cres):
    from bodo.ir.aggregate import gb_agg_cfunc_addr
    for ixk__xfsgr in cres.library._codegen._engine._defined_symbols:
        if ixk__xfsgr.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in ixk__xfsgr and (
            'bodo_gb_udf_update_local' in ixk__xfsgr or 
            'bodo_gb_udf_combine' in ixk__xfsgr or 'bodo_gb_udf_eval' in
            ixk__xfsgr or 'bodo_gb_apply_general_udfs' in ixk__xfsgr):
            gb_agg_cfunc_addr[ixk__xfsgr
                ] = cres.library.get_pointer_to_function(ixk__xfsgr)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for ixk__xfsgr in cres.library._codegen._engine._defined_symbols:
        if ixk__xfsgr.startswith('cfunc') and ('get_join_cond_addr' not in
            ixk__xfsgr or 'bodo_join_gen_cond' in ixk__xfsgr):
            join_gen_cond_cfunc_addr[ixk__xfsgr
                ] = cres.library.get_pointer_to_function(ixk__xfsgr)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    mpcr__euig = self._get_dispatcher_for_current_target()
    if mpcr__euig is not self:
        return mpcr__euig.compile(sig)
    with ExitStack() as scope:
        cres = None

        def cb_compiler(dur):
            if cres is not None:
                self._callback_add_compiler_timer(dur, cres)

        def cb_llvm(dur):
            if cres is not None:
                self._callback_add_llvm_timer(dur, cres)
        scope.enter_context(ev.install_timer('numba:compiler_lock',
            cb_compiler))
        scope.enter_context(ev.install_timer('numba:llvm_lock', cb_llvm))
        scope.enter_context(global_compiler_lock)
        if not self._can_compile:
            raise RuntimeError('compilation disabled')
        with self._compiling_counter:
            args, return_type = sigutils.normalize_signature(sig)
            gbh__jvqo = self.overloads.get(tuple(args))
            if gbh__jvqo is not None:
                return gbh__jvqo.entry_point
            cres = self._cache.load_overload(sig, self.targetctx)
            if cres is not None:
                resolve_gb_agg_funcs(cres)
                resolve_join_general_cond_funcs(cres)
                self._cache_hits[sig] += 1
                if not cres.objectmode:
                    self.targetctx.insert_user_function(cres.entry_point,
                        cres.fndesc, [cres.library])
                self.add_overload(cres)
                return cres.entry_point
            self._cache_misses[sig] += 1
            kmcrs__coby = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=kmcrs__coby):
                try:
                    cres = self._compiler.compile(args, return_type)
                except errors.ForceLiteralArg as e:

                    def folded(args, kws):
                        return self._compiler.fold_argument_types(args, kws)[1]
                    raise e.bind_fold_arguments(folded)
                self.add_overload(cres)
            self._cache.save_overload(sig, cres)
            return cres.entry_point


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.Dispatcher.compile)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '934ec993577ea3b1c7dd2181ac02728abf8559fd42c17062cc821541b092ff8f':
        warnings.warn('numba.core.dispatcher.Dispatcher.compile has changed')
numba.core.dispatcher.Dispatcher.compile = compile


def _get_module_for_linking(self):
    import llvmlite.binding as ll
    self._ensure_finalized()
    if self._shared_module is not None:
        return self._shared_module
    dne__jotg = self._final_module
    gbcee__lyh = []
    bzs__vwyeq = 0
    for fn in dne__jotg.functions:
        bzs__vwyeq += 1
        if not fn.is_declaration and fn.linkage == ll.Linkage.external:
            if 'get_agg_udf_addr' not in fn.name:
                if 'bodo_gb_udf_update_local' in fn.name:
                    continue
                if 'bodo_gb_udf_combine' in fn.name:
                    continue
                if 'bodo_gb_udf_eval' in fn.name:
                    continue
                if 'bodo_gb_apply_general_udfs' in fn.name:
                    continue
            if 'get_join_cond_addr' not in fn.name:
                if 'bodo_join_gen_cond' in fn.name:
                    continue
            gbcee__lyh.append(fn.name)
    if bzs__vwyeq == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if gbcee__lyh:
        dne__jotg = dne__jotg.clone()
        for name in gbcee__lyh:
            dne__jotg.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = dne__jotg
    return dne__jotg


if _check_numba_change:
    lines = inspect.getsource(numba.core.codegen.CPUCodeLibrary.
        _get_module_for_linking)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '56dde0e0555b5ec85b93b97c81821bce60784515a1fbf99e4542e92d02ff0a73':
        warnings.warn(
            'numba.core.codegen.CPUCodeLibrary._get_module_for_linking has changed'
            )
numba.core.codegen.CPUCodeLibrary._get_module_for_linking = (
    _get_module_for_linking)


def propagate(self, typeinfer):
    import bodo
    errors = []
    for nxic__hfvvk in self.constraints:
        loc = nxic__hfvvk.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                nxic__hfvvk(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                err__zfvdp = numba.core.errors.TypingError(str(e), loc=
                    nxic__hfvvk.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(err__zfvdp, e))
            except bodo.utils.typing.BodoError as e:
                if loc not in e.locs_in_msg:
                    errors.append(bodo.utils.typing.BodoError(str(e.msg) +
                        '\n' + loc.strformat() + '\n', locs_in_msg=e.
                        locs_in_msg + [loc]))
                else:
                    errors.append(bodo.utils.typing.BodoError(e.msg,
                        locs_in_msg=e.locs_in_msg))
            except Exception as e:
                from numba.core import utils
                if utils.use_old_style_errors():
                    numba.core.typeinfer._logger.debug('captured error',
                        exc_info=e)
                    msg = """Internal error at {con}.
{err}
Enable logging at debug level for details."""
                    err__zfvdp = numba.core.errors.TypingError(msg.format(
                        con=nxic__hfvvk, err=str(e)), loc=nxic__hfvvk.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(err__zfvdp, e))
                elif utils.use_new_style_errors():
                    raise e
                else:
                    msg = (
                        f"Unknown CAPTURED_ERRORS style: '{numba.core.config.CAPTURED_ERRORS}'."
                        )
                    assert 0, msg
    return errors


if _check_numba_change:
    lines = inspect.getsource(numba.core.typeinfer.ConstraintNetwork.propagate)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1e73635eeba9ba43cb3372f395b747ae214ce73b729fb0adba0a55237a1cb063':
        warnings.warn(
            'numba.core.typeinfer.ConstraintNetwork.propagate has changed')
numba.core.typeinfer.ConstraintNetwork.propagate = propagate


def raise_error(self):
    import bodo
    for wkll__lyyg in self._failures.values():
        for zuwm__aobt in wkll__lyyg:
            if isinstance(zuwm__aobt.error, ForceLiteralArg):
                raise zuwm__aobt.error
            if isinstance(zuwm__aobt.error, bodo.utils.typing.BodoError):
                raise zuwm__aobt.error
    raise TypingError(self.format())


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.
        _ResolutionFailures.raise_error)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '84b89430f5c8b46cfc684804e6037f00a0f170005cd128ad245551787b2568ea':
        warnings.warn(
            'numba.core.types.functions._ResolutionFailures.raise_error has changed'
            )
numba.core.types.functions._ResolutionFailures.raise_error = raise_error


def bodo_remove_dead_block(block, lives, call_table, arg_aliases, alias_map,
    alias_set, func_ir, typemap):
    from bodo.transforms.distributed_pass import saved_array_analysis
    from bodo.utils.utils import is_array_typ, is_expr
    nhcnw__uffx = False
    kdh__jnswm = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        vgj__xlls = set()
        hixjh__hvdqx = lives & alias_set
        for ehma__wxyyj in hixjh__hvdqx:
            vgj__xlls |= alias_map[ehma__wxyyj]
        lives_n_aliases = lives | vgj__xlls | arg_aliases
        if type(stmt) in remove_dead_extensions:
            qav__tpvlc = remove_dead_extensions[type(stmt)]
            stmt = qav__tpvlc(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                nhcnw__uffx = True
                continue
        if isinstance(stmt, ir.Assign):
            zwzza__sqf = stmt.target
            cjr__kmmhu = stmt.value
            if zwzza__sqf.name not in lives and has_no_side_effect(cjr__kmmhu,
                lives_n_aliases, call_table):
                nhcnw__uffx = True
                continue
            if saved_array_analysis and zwzza__sqf.name in lives and is_expr(
                cjr__kmmhu, 'getattr'
                ) and cjr__kmmhu.attr == 'shape' and is_array_typ(typemap[
                cjr__kmmhu.value.name]) and cjr__kmmhu.value.name not in lives:
                kvity__fmr = {ehma__wxyyj: qxb__lygvj for qxb__lygvj,
                    ehma__wxyyj in func_ir.blocks.items()}
                if block in kvity__fmr:
                    wng__cmyxl = kvity__fmr[block]
                    zovbl__jwkcf = saved_array_analysis.get_equiv_set(
                        wng__cmyxl)
                    uoz__xvvdt = zovbl__jwkcf.get_equiv_set(cjr__kmmhu.value)
                    if uoz__xvvdt is not None:
                        for ehma__wxyyj in uoz__xvvdt:
                            if ehma__wxyyj.endswith('#0'):
                                ehma__wxyyj = ehma__wxyyj[:-2]
                            if ehma__wxyyj in typemap and is_array_typ(typemap
                                [ehma__wxyyj]) and ehma__wxyyj in lives:
                                cjr__kmmhu.value = ir.Var(cjr__kmmhu.value.
                                    scope, ehma__wxyyj, cjr__kmmhu.value.loc)
                                nhcnw__uffx = True
                                break
            if isinstance(cjr__kmmhu, ir.Var
                ) and zwzza__sqf.name == cjr__kmmhu.name:
                nhcnw__uffx = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                nhcnw__uffx = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            toag__cei = analysis.ir_extension_usedefs[type(stmt)]
            wuxox__yjbep, qsx__snz = toag__cei(stmt)
            lives -= qsx__snz
            lives |= wuxox__yjbep
        else:
            lives |= {ehma__wxyyj.name for ehma__wxyyj in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                wbz__vuf = set()
                if isinstance(cjr__kmmhu, ir.Expr):
                    wbz__vuf = {ehma__wxyyj.name for ehma__wxyyj in
                        cjr__kmmhu.list_vars()}
                if zwzza__sqf.name not in wbz__vuf:
                    lives.remove(zwzza__sqf.name)
        kdh__jnswm.append(stmt)
    kdh__jnswm.reverse()
    block.body = kdh__jnswm
    return nhcnw__uffx


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            czu__qdmg, = args
            if isinstance(czu__qdmg, types.IterableType):
                dtype = czu__qdmg.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), czu__qdmg)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    yyo__sye = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (yyo__sye, self.dtype)
    super(types.Set, self).__init__(name=name)


types.Set.__init__ = Set__init__


@lower_builtin(operator.eq, types.UnicodeType, types.UnicodeType)
def eq_str(context, builder, sig, args):
    func = numba.cpython.unicode.unicode_eq(*sig.args)
    return context.compile_internal(builder, func, sig, args)


numba.parfors.parfor.push_call_vars = (lambda blocks, saved_globals,
    saved_getattrs, typemap, nested=False: None)


def maybe_literal(value):
    if isinstance(value, (list, dict, pytypes.FunctionType)):
        return
    if isinstance(value, tuple):
        try:
            return types.Tuple([literal(x) for x in value])
        except LiteralTypingError as rihfs__hjvbc:
            return
    try:
        return literal(value)
    except LiteralTypingError as rihfs__hjvbc:
        return


if _check_numba_change:
    lines = inspect.getsource(types.maybe_literal)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8fb2fd93acf214b28e33e37d19dc2f7290a42792ec59b650553ac278854b5081':
        warnings.warn('types.maybe_literal has changed')
types.maybe_literal = maybe_literal
types.misc.maybe_literal = maybe_literal


def CacheImpl__init__(self, py_func):
    self._lineno = py_func.__code__.co_firstlineno
    try:
        yhg__wcx = py_func.__qualname__
    except AttributeError as rihfs__hjvbc:
        yhg__wcx = py_func.__name__
    dwre__yzyls = inspect.getfile(py_func)
    for cls in self._locator_classes:
        dujfl__xvviw = cls.from_function(py_func, dwre__yzyls)
        if dujfl__xvviw is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (yhg__wcx, dwre__yzyls))
    self._locator = dujfl__xvviw
    slph__mex = inspect.getfile(py_func)
    qzkbx__rpfxj = os.path.splitext(os.path.basename(slph__mex))[0]
    if dwre__yzyls.startswith('<ipython-'):
        qgn__qibte = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', qzkbx__rpfxj, count=1)
        if qgn__qibte == qzkbx__rpfxj:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        qzkbx__rpfxj = qgn__qibte
    bgpzu__syzl = '%s.%s' % (qzkbx__rpfxj, yhg__wcx)
    pybw__wisan = getattr(sys, 'abiflags', '')
    self._filename_base = self.get_filename_base(bgpzu__syzl, pybw__wisan)


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    ggqr__sumc = list(filter(lambda a: self._istuple(a.name), args))
    if len(ggqr__sumc) == 2 and fn.__name__ == 'add':
        tmjv__sgsh = self.typemap[ggqr__sumc[0].name]
        ihft__lux = self.typemap[ggqr__sumc[1].name]
        if tmjv__sgsh.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                ggqr__sumc[1]))
        if ihft__lux.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                ggqr__sumc[0]))
        try:
            cdodv__wtgj = [equiv_set.get_shape(x) for x in ggqr__sumc]
            if None in cdodv__wtgj:
                return None
            rdr__waxpf = sum(cdodv__wtgj, ())
            return ArrayAnalysis.AnalyzeResult(shape=rdr__waxpf)
        except GuardException as rihfs__hjvbc:
            return None
    qfz__qabqf = list(filter(lambda a: self._isarray(a.name), args))
    require(len(qfz__qabqf) > 0)
    dcam__egge = [x.name for x in qfz__qabqf]
    haeq__kndso = [self.typemap[x.name].ndim for x in qfz__qabqf]
    coae__fvt = max(haeq__kndso)
    require(coae__fvt > 0)
    cdodv__wtgj = [equiv_set.get_shape(x) for x in qfz__qabqf]
    if any(a is None for a in cdodv__wtgj):
        return ArrayAnalysis.AnalyzeResult(shape=qfz__qabqf[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, qfz__qabqf))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, cdodv__wtgj,
        dcam__egge)


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.array_analysis.ArrayAnalysis.
        _analyze_broadcast)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '6c91fec038f56111338ea2b08f5f0e7f61ebdab1c81fb811fe26658cc354e40f':
        warnings.warn(
            'numba.parfors.array_analysis.ArrayAnalysis._analyze_broadcast has changed'
            )
numba.parfors.array_analysis.ArrayAnalysis._analyze_broadcast = (
    _analyze_broadcast)


def convert_code_obj_to_function(code_obj, caller_ir):
    import bodo
    ymqjj__sxuzx = code_obj.code
    oivb__wyp = len(ymqjj__sxuzx.co_freevars)
    bwqk__kim = ymqjj__sxuzx.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        mhjz__xpuvm, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        bwqk__kim = [ehma__wxyyj.name for ehma__wxyyj in mhjz__xpuvm]
    kofr__ngbb = caller_ir.func_id.func.__globals__
    try:
        kofr__ngbb = getattr(code_obj, 'globals', kofr__ngbb)
    except KeyError as rihfs__hjvbc:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/udfs.html"
        )
    ygnn__ndf = []
    for x in bwqk__kim:
        try:
            kuk__gypc = caller_ir.get_definition(x)
        except KeyError as rihfs__hjvbc:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(kuk__gypc, (ir.Const, ir.Global, ir.FreeVar)):
            val = kuk__gypc.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                feb__ptk = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                kofr__ngbb[feb__ptk] = bodo.jit(distributed=False)(val)
                kofr__ngbb[feb__ptk].is_nested_func = True
                val = feb__ptk
            if isinstance(val, CPUDispatcher):
                feb__ptk = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                kofr__ngbb[feb__ptk] = val
                val = feb__ptk
            ygnn__ndf.append(val)
        elif isinstance(kuk__gypc, ir.Expr
            ) and kuk__gypc.op == 'make_function':
            erslt__lahu = convert_code_obj_to_function(kuk__gypc, caller_ir)
            feb__ptk = ir_utils.mk_unique_var('nested_func').replace('.', '_')
            kofr__ngbb[feb__ptk] = bodo.jit(distributed=False)(erslt__lahu)
            kofr__ngbb[feb__ptk].is_nested_func = True
            ygnn__ndf.append(feb__ptk)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    rhv__uehbj = '\n'.join([('\tc_%d = %s' % (gfxjm__emmfw, x)) for 
        gfxjm__emmfw, x in enumerate(ygnn__ndf)])
    rye__fucc = ','.join([('c_%d' % gfxjm__emmfw) for gfxjm__emmfw in range
        (oivb__wyp)])
    xdlcs__iudga = list(ymqjj__sxuzx.co_varnames)
    brhax__yxhq = 0
    xtciz__hrk = ymqjj__sxuzx.co_argcount
    dnqt__tmul = caller_ir.get_definition(code_obj.defaults)
    if dnqt__tmul is not None:
        if isinstance(dnqt__tmul, tuple):
            twmw__ckny = [caller_ir.get_definition(x).value for x in dnqt__tmul
                ]
            fxs__msbr = tuple(twmw__ckny)
        else:
            twmw__ckny = [caller_ir.get_definition(x).value for x in
                dnqt__tmul.items]
            fxs__msbr = tuple(twmw__ckny)
        brhax__yxhq = len(fxs__msbr)
    jnp__pegjh = xtciz__hrk - brhax__yxhq
    vbltq__qeupg = ','.join([('%s' % xdlcs__iudga[gfxjm__emmfw]) for
        gfxjm__emmfw in range(jnp__pegjh)])
    if brhax__yxhq:
        dxas__mzllr = [('%s = %s' % (xdlcs__iudga[gfxjm__emmfw + jnp__pegjh
            ], fxs__msbr[gfxjm__emmfw])) for gfxjm__emmfw in range(brhax__yxhq)
            ]
        vbltq__qeupg += ', '
        vbltq__qeupg += ', '.join(dxas__mzllr)
    return _create_function_from_code_obj(ymqjj__sxuzx, rhv__uehbj,
        vbltq__qeupg, rye__fucc, kofr__ngbb)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.convert_code_obj_to_function)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b840769812418d589460e924a15477e83e7919aac8a3dcb0188ff447344aa8ac':
        warnings.warn(
            'numba.core.ir_utils.convert_code_obj_to_function has changed')
numba.core.ir_utils.convert_code_obj_to_function = convert_code_obj_to_function
numba.core.untyped_passes.convert_code_obj_to_function = (
    convert_code_obj_to_function)


def passmanager_run(self, state):
    from numba.core.compiler import _EarlyPipelineCompletion
    if not self.finalized:
        raise RuntimeError('Cannot run non-finalised pipeline')
    from numba.core.compiler_machinery import CompilerPass, _pass_registry
    import bodo
    for wba__zqhu, (bqoe__nkma, vjlb__hek) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % vjlb__hek)
            eowm__mkb = _pass_registry.get(bqoe__nkma).pass_inst
            if isinstance(eowm__mkb, CompilerPass):
                self._runPass(wba__zqhu, eowm__mkb, state)
            else:
                raise BaseException('Legacy pass in use')
        except _EarlyPipelineCompletion as e:
            raise e
        except bodo.utils.typing.BodoError as e:
            raise
        except Exception as e:
            if numba.core.config.DEVELOPER_MODE:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                msg = 'Failed in %s mode pipeline (step: %s)' % (self.
                    pipeline_name, vjlb__hek)
                qpi__jrzcl = self._patch_error(msg, e)
                raise qpi__jrzcl
            else:
                raise e


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler_machinery.PassManager.run)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '43505782e15e690fd2d7e53ea716543bec37aa0633502956864edf649e790cdb':
        warnings.warn(
            'numba.core.compiler_machinery.PassManager.run has changed')
numba.core.compiler_machinery.PassManager.run = passmanager_run
if _check_numba_change:
    lines = inspect.getsource(numba.np.ufunc.parallel._launch_threads)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a57ef28c4168fdd436a5513bba4351ebc6d9fba76c5819f44046431a79b9030f':
        warnings.warn('numba.np.ufunc.parallel._launch_threads has changed')
numba.np.ufunc.parallel._launch_threads = lambda : None


def get_reduce_nodes(reduction_node, nodes, func_ir):
    bgg__gosn = None
    qsx__snz = {}

    def lookup(var, already_seen, varonly=True):
        val = qsx__snz.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    dgrm__ere = reduction_node.unversioned_name
    for gfxjm__emmfw, stmt in enumerate(nodes):
        zwzza__sqf = stmt.target
        cjr__kmmhu = stmt.value
        qsx__snz[zwzza__sqf.name] = cjr__kmmhu
        if isinstance(cjr__kmmhu, ir.Var) and cjr__kmmhu.name in qsx__snz:
            cjr__kmmhu = lookup(cjr__kmmhu, set())
        if isinstance(cjr__kmmhu, ir.Expr):
            gxaz__henk = set(lookup(ehma__wxyyj, set(), True).name for
                ehma__wxyyj in cjr__kmmhu.list_vars())
            if name in gxaz__henk:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(cjr__kmmhu)]
                lqzgt__bahx = [x for x, zzf__uzs in args if zzf__uzs.name !=
                    name]
                args = [(x, zzf__uzs) for x, zzf__uzs in args if x !=
                    zzf__uzs.name]
                jddbt__zhalm = dict(args)
                if len(lqzgt__bahx) == 1:
                    jddbt__zhalm[lqzgt__bahx[0]] = ir.Var(zwzza__sqf.scope,
                        name + '#init', zwzza__sqf.loc)
                replace_vars_inner(cjr__kmmhu, jddbt__zhalm)
                bgg__gosn = nodes[gfxjm__emmfw:]
                break
    return bgg__gosn


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_reduce_nodes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a05b52aff9cb02e595a510cd34e973857303a71097fc5530567cb70ca183ef3b':
        warnings.warn('numba.parfors.parfor.get_reduce_nodes has changed')
numba.parfors.parfor.get_reduce_nodes = get_reduce_nodes


def _can_reorder_stmts(stmt, next_stmt, func_ir, call_table, alias_map,
    arg_aliases):
    from numba.parfors.parfor import Parfor, expand_aliases, is_assert_equiv
    if isinstance(stmt, Parfor) and not isinstance(next_stmt, Parfor
        ) and not isinstance(next_stmt, ir.Print) and (not isinstance(
        next_stmt, ir.Assign) or has_no_side_effect(next_stmt.value, set(),
        call_table) or guard(is_assert_equiv, func_ir, next_stmt.value)):
        aigl__xyfx = expand_aliases({ehma__wxyyj.name for ehma__wxyyj in
            stmt.list_vars()}, alias_map, arg_aliases)
        nymrj__akki = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        hsd__fbu = expand_aliases({ehma__wxyyj.name for ehma__wxyyj in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        crjxs__fyx = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(nymrj__akki & hsd__fbu | crjxs__fyx & aigl__xyfx) == 0:
            return True
    return False


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor._can_reorder_stmts)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '18caa9a01b21ab92b4f79f164cfdbc8574f15ea29deedf7bafdf9b0e755d777c':
        warnings.warn('numba.parfors.parfor._can_reorder_stmts has changed')
numba.parfors.parfor._can_reorder_stmts = _can_reorder_stmts


def get_parfor_writes(parfor, func_ir):
    from numba.parfors.parfor import Parfor
    assert isinstance(parfor, Parfor)
    waak__avv = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            waak__avv.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                waak__avv.update(get_parfor_writes(stmt, func_ir))
    return waak__avv


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    waak__avv = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        waak__avv.add(stmt.target.name)
    if isinstance(stmt, bodo.ir.aggregate.Aggregate):
        waak__avv = {ehma__wxyyj.name for ehma__wxyyj in stmt.df_out_vars.
            values()}
        if stmt.out_key_vars is not None:
            waak__avv.update({ehma__wxyyj.name for ehma__wxyyj in stmt.
                out_key_vars})
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        waak__avv = {ehma__wxyyj.name for ehma__wxyyj in stmt.out_vars}
    if isinstance(stmt, bodo.ir.join.Join):
        waak__avv = {ehma__wxyyj.name for ehma__wxyyj in stmt.out_data_vars
            .values()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            waak__avv.update({ehma__wxyyj.name for ehma__wxyyj in stmt.
                out_key_arrs})
            waak__avv.update({ehma__wxyyj.name for ehma__wxyyj in stmt.
                df_out_vars.values()})
    if is_call_assign(stmt):
        lrazt__ocmdp = guard(find_callname, func_ir, stmt.value)
        if lrazt__ocmdp in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'
            ), ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            waak__avv.add(stmt.value.args[0].name)
    return waak__avv


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.get_stmt_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1a7a80b64c9a0eb27e99dc8eaae187bde379d4da0b74c84fbf87296d87939974':
        warnings.warn('numba.core.ir_utils.get_stmt_writes has changed')


def patch_message(self, new_message):
    self.msg = new_message
    self.args = (new_message,) + self.args[1:]


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.NumbaError.patch_message)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'ed189a428a7305837e76573596d767b6e840e99f75c05af6941192e0214fa899':
        warnings.warn('numba.core.errors.NumbaError.patch_message has changed')
numba.core.errors.NumbaError.patch_message = patch_message


def add_context(self, msg):
    if numba.core.config.DEVELOPER_MODE:
        self.contexts.append(msg)
        qav__tpvlc = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        flkco__fpvwx = qav__tpvlc.format(self, msg)
        self.args = flkco__fpvwx,
    else:
        qav__tpvlc = _termcolor.errmsg('{0}')
        flkco__fpvwx = qav__tpvlc.format(self)
        self.args = flkco__fpvwx,
    return self


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.NumbaError.add_context)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '6a388d87788f8432c2152ac55ca9acaa94dbc3b55be973b2cf22dd4ee7179ab8':
        warnings.warn('numba.core.errors.NumbaError.add_context has changed')
numba.core.errors.NumbaError.add_context = add_context


def _get_dist_spec_from_options(spec, **options):
    from bodo.transforms.distributed_analysis import Distribution
    dist_spec = {}
    if 'distributed' in options:
        for bhtiv__jafc in options['distributed']:
            dist_spec[bhtiv__jafc] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for bhtiv__jafc in options['distributed_block']:
            dist_spec[bhtiv__jafc] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    ebx__rozb = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, lassa__uusfa in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(lassa__uusfa)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    shgmh__oize = {}
    for flup__jcdil in reversed(inspect.getmro(cls)):
        shgmh__oize.update(flup__jcdil.__dict__)
    pjuj__lkt, fdgui__yprp, afgci__nuf, lqbm__xto = {}, {}, {}, {}
    for qxb__lygvj, ehma__wxyyj in shgmh__oize.items():
        if isinstance(ehma__wxyyj, pytypes.FunctionType):
            pjuj__lkt[qxb__lygvj] = ehma__wxyyj
        elif isinstance(ehma__wxyyj, property):
            fdgui__yprp[qxb__lygvj] = ehma__wxyyj
        elif isinstance(ehma__wxyyj, staticmethod):
            afgci__nuf[qxb__lygvj] = ehma__wxyyj
        else:
            lqbm__xto[qxb__lygvj] = ehma__wxyyj
    kyvh__tjmgq = (set(pjuj__lkt) | set(fdgui__yprp) | set(afgci__nuf)) & set(
        spec)
    if kyvh__tjmgq:
        raise NameError('name shadowing: {0}'.format(', '.join(kyvh__tjmgq)))
    yzj__nzsoz = lqbm__xto.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(lqbm__xto)
    if lqbm__xto:
        msg = 'class members are not yet supported: {0}'
        wmlp__ytw = ', '.join(lqbm__xto.keys())
        raise TypeError(msg.format(wmlp__ytw))
    for qxb__lygvj, ehma__wxyyj in fdgui__yprp.items():
        if ehma__wxyyj.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(qxb__lygvj))
    jit_methods = {qxb__lygvj: bodo.jit(returns_maybe_distributed=ebx__rozb
        )(ehma__wxyyj) for qxb__lygvj, ehma__wxyyj in pjuj__lkt.items()}
    jit_props = {}
    for qxb__lygvj, ehma__wxyyj in fdgui__yprp.items():
        hcilb__mrg = {}
        if ehma__wxyyj.fget:
            hcilb__mrg['get'] = bodo.jit(ehma__wxyyj.fget)
        if ehma__wxyyj.fset:
            hcilb__mrg['set'] = bodo.jit(ehma__wxyyj.fset)
        jit_props[qxb__lygvj] = hcilb__mrg
    jit_static_methods = {qxb__lygvj: bodo.jit(ehma__wxyyj.__func__) for 
        qxb__lygvj, ehma__wxyyj in afgci__nuf.items()}
    dctgc__msum = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    mle__ceo = dict(class_type=dctgc__msum, __doc__=yzj__nzsoz)
    mle__ceo.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), mle__ceo)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, dctgc__msum)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(dctgc__msum, typingctx, targetctx).register()
    as_numba_type.register(cls, dctgc__msum.instance_type)
    return cls


if _check_numba_change:
    lines = inspect.getsource(jitclass_base.register_class_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '005e6e2e89a47f77a19ba86305565050d4dbc2412fc4717395adf2da348671a9':
        warnings.warn('jitclass_base.register_class_type has changed')
jitclass_base.register_class_type = register_class_type


def ClassType__init__(self, class_def, ctor_template_cls, struct,
    jit_methods, jit_props, jit_static_methods, dist_spec=None):
    if dist_spec is None:
        dist_spec = {}
    self.class_name = class_def.__name__
    self.class_doc = class_def.__doc__
    self._ctor_template_class = ctor_template_cls
    self.jit_methods = jit_methods
    self.jit_props = jit_props
    self.jit_static_methods = jit_static_methods
    self.struct = struct
    self.dist_spec = dist_spec
    eoiyx__zrds = ','.join('{0}:{1}'.format(qxb__lygvj, ehma__wxyyj) for 
        qxb__lygvj, ehma__wxyyj in struct.items())
    qvf__aud = ','.join('{0}:{1}'.format(qxb__lygvj, ehma__wxyyj) for 
        qxb__lygvj, ehma__wxyyj in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), eoiyx__zrds, qvf__aud)
    super(types.misc.ClassType, self).__init__(name)


if _check_numba_change:
    lines = inspect.getsource(types.misc.ClassType.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '2b848ea82946c88f540e81f93ba95dfa7cd66045d944152a337fe2fc43451c30':
        warnings.warn('types.misc.ClassType.__init__ has changed')
types.misc.ClassType.__init__ = ClassType__init__


def jitclass(cls_or_spec=None, spec=None, **options):
    if cls_or_spec is not None and spec is None and not isinstance(cls_or_spec,
        type):
        spec = cls_or_spec
        cls_or_spec = None

    def wrap(cls):
        if numba.core.config.DISABLE_JIT:
            return cls
        else:
            from numba.experimental.jitclass.base import ClassBuilder
            return register_class_type(cls, spec, types.ClassType,
                ClassBuilder, **options)
    if cls_or_spec is None:
        return wrap
    else:
        return wrap(cls_or_spec)


if _check_numba_change:
    lines = inspect.getsource(jitclass_decorators.jitclass)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '265f1953ee5881d1a5d90238d3c932cd300732e41495657e65bf51e59f7f4af5':
        warnings.warn('jitclass_decorators.jitclass has changed')


def CallConstraint_resolve(self, typeinfer, typevars, fnty):
    assert fnty
    context = typeinfer.context
    qctnq__gggdn = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if qctnq__gggdn is None:
        return
    rkcx__ljgrl, uowp__iqxzk = qctnq__gggdn
    for a in itertools.chain(rkcx__ljgrl, uowp__iqxzk.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, rkcx__ljgrl, uowp__iqxzk)
    except ForceLiteralArg as e:
        xobfz__vfge = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(xobfz__vfge, self.kws)
        ozygr__guiw = set()
        niwc__nwogs = set()
        lbbo__duei = {}
        for wba__zqhu in e.requested_args:
            qkiqf__zeyy = typeinfer.func_ir.get_definition(folded[wba__zqhu])
            if isinstance(qkiqf__zeyy, ir.Arg):
                ozygr__guiw.add(qkiqf__zeyy.index)
                if qkiqf__zeyy.index in e.file_infos:
                    lbbo__duei[qkiqf__zeyy.index] = e.file_infos[qkiqf__zeyy
                        .index]
            else:
                niwc__nwogs.add(wba__zqhu)
        if niwc__nwogs:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif ozygr__guiw:
            raise ForceLiteralArg(ozygr__guiw, loc=self.loc, file_infos=
                lbbo__duei)
    if sig is None:
        yzfq__khv = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in rkcx__ljgrl]
        args += [('%s=%s' % (qxb__lygvj, ehma__wxyyj)) for qxb__lygvj,
            ehma__wxyyj in sorted(uowp__iqxzk.items())]
        mcr__cfiwm = yzfq__khv.format(fnty, ', '.join(map(str, args)))
        zjjml__pmtyo = context.explain_function_type(fnty)
        msg = '\n'.join([mcr__cfiwm, zjjml__pmtyo])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        zuqn__zwtz = context.unify_pairs(sig.recvr, fnty.this)
        if zuqn__zwtz is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if zuqn__zwtz is not None and zuqn__zwtz.is_precise():
            ajw__yqa = fnty.copy(this=zuqn__zwtz)
            typeinfer.propagate_refined_type(self.func, ajw__yqa)
    if not sig.return_type.is_precise():
        rdjq__jfvff = typevars[self.target]
        if rdjq__jfvff.defined:
            rlaio__sbqnx = rdjq__jfvff.getone()
            if context.unify_pairs(rlaio__sbqnx, sig.return_type
                ) == rlaio__sbqnx:
                sig = sig.replace(return_type=rlaio__sbqnx)
    self.signature = sig
    self._add_refine_map(typeinfer, typevars, sig)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typeinfer.CallConstraint.resolve)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c78cd8ffc64b836a6a2ddf0362d481b52b9d380c5249920a87ff4da052ce081f':
        warnings.warn('numba.core.typeinfer.CallConstraint.resolve has changed'
            )
numba.core.typeinfer.CallConstraint.resolve = CallConstraint_resolve


def ForceLiteralArg__init__(self, arg_indices, fold_arguments=None, loc=
    None, file_infos=None):
    super(ForceLiteralArg, self).__init__(
        'Pseudo-exception to force literal arguments in the dispatcher',
        loc=loc)
    self.requested_args = frozenset(arg_indices)
    self.fold_arguments = fold_arguments
    if file_infos is None:
        self.file_infos = {}
    else:
        self.file_infos = file_infos


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b241d5e36a4cf7f4c73a7ad3238693612926606c7a278cad1978070b82fb55ef':
        warnings.warn('numba.core.errors.ForceLiteralArg.__init__ has changed')
numba.core.errors.ForceLiteralArg.__init__ = ForceLiteralArg__init__


def ForceLiteralArg_bind_fold_arguments(self, fold_arguments):
    e = ForceLiteralArg(self.requested_args, fold_arguments, loc=self.loc,
        file_infos=self.file_infos)
    return numba.core.utils.chain_exception(e, self)


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.
        bind_fold_arguments)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1e93cca558f7c604a47214a8f2ec33ee994104cb3e5051166f16d7cc9315141d':
        warnings.warn(
            'numba.core.errors.ForceLiteralArg.bind_fold_arguments has changed'
            )
numba.core.errors.ForceLiteralArg.bind_fold_arguments = (
    ForceLiteralArg_bind_fold_arguments)


def ForceLiteralArg_combine(self, other):
    if not isinstance(other, ForceLiteralArg):
        snb__rrrnv = '*other* must be a {} but got a {} instead'
        raise TypeError(snb__rrrnv.format(ForceLiteralArg, type(other)))
    return ForceLiteralArg(self.requested_args | other.requested_args, {**
        self.file_infos, **other.file_infos})


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.combine)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '49bf06612776f5d755c1c7d1c5eb91831a57665a8fed88b5651935f3bf33e899':
        warnings.warn('numba.core.errors.ForceLiteralArg.combine has changed')
numba.core.errors.ForceLiteralArg.combine = ForceLiteralArg_combine


def _get_global_type(self, gv):
    from bodo.utils.typing import FunctionLiteral
    ty = self._lookup_global(gv)
    if ty is not None:
        return ty
    if isinstance(gv, pytypes.ModuleType):
        return types.Module(gv)
    if isinstance(gv, pytypes.FunctionType):
        return FunctionLiteral(gv)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.context.BaseContext.
        _get_global_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8ffe6b81175d1eecd62a37639b5005514b4477d88f35f5b5395041ac8c945a4a':
        warnings.warn(
            'numba.core.typing.context.BaseContext._get_global_type has changed'
            )
numba.core.typing.context.BaseContext._get_global_type = _get_global_type


def _legalize_args(self, func_ir, args, kwargs, loc, func_globals,
    func_closures):
    from numba.core import sigutils
    from bodo.utils.transform import get_const_value_inner
    if args:
        raise errors.CompilerError(
            "objectmode context doesn't take any positional arguments")
    kkwf__oic = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for qxb__lygvj, ehma__wxyyj in kwargs.items():
        pfst__hdk = None
        try:
            bfw__gcp = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var(
                'dummy'), loc)
            func_ir._definitions[bfw__gcp.name] = [ehma__wxyyj]
            pfst__hdk = get_const_value_inner(func_ir, bfw__gcp)
            func_ir._definitions.pop(bfw__gcp.name)
            if isinstance(pfst__hdk, str):
                pfst__hdk = sigutils._parse_signature_string(pfst__hdk)
            if isinstance(pfst__hdk, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {qxb__lygvj} is annotated as type class {pfst__hdk}."""
                    )
            assert isinstance(pfst__hdk, types.Type)
            if isinstance(pfst__hdk, (types.List, types.Set)):
                pfst__hdk = pfst__hdk.copy(reflected=False)
            kkwf__oic[qxb__lygvj] = pfst__hdk
        except BodoError as rihfs__hjvbc:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(pfst__hdk, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(ehma__wxyyj, ir.Global):
                    msg = f'Global {ehma__wxyyj.name!r} is not defined.'
                if isinstance(ehma__wxyyj, ir.FreeVar):
                    msg = f'Freevar {ehma__wxyyj.name!r} is not defined.'
            if isinstance(ehma__wxyyj, ir.Expr
                ) and ehma__wxyyj.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=qxb__lygvj, msg=msg, loc=loc)
    for name, typ in kkwf__oic.items():
        self._legalize_arg_type(name, typ, loc)
    return kkwf__oic


if _check_numba_change:
    lines = inspect.getsource(numba.core.withcontexts._ObjModeContextType.
        _legalize_args)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '867c9ba7f1bcf438be56c38e26906bb551f59a99f853a9f68b71208b107c880e':
        warnings.warn(
            'numba.core.withcontexts._ObjModeContextType._legalize_args has changed'
            )
numba.core.withcontexts._ObjModeContextType._legalize_args = _legalize_args


def op_FORMAT_VALUE_byteflow(self, state, inst):
    flags = inst.arg
    if flags & 3 != 0:
        msg = 'str/repr/ascii conversion in f-strings not supported yet'
        raise errors.UnsupportedError(msg, loc=self.get_debug_loc(inst.lineno))
    format_spec = None
    if flags & 4 == 4:
        format_spec = state.pop()
    value = state.pop()
    fmtvar = state.make_temp()
    res = state.make_temp()
    state.append(inst, value=value, res=res, fmtvar=fmtvar, format_spec=
        format_spec)
    state.push(res)


def op_BUILD_STRING_byteflow(self, state, inst):
    oelq__zxtl = inst.arg
    assert oelq__zxtl > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(oelq__zxtl)]))
    tmps = [state.make_temp() for _ in range(oelq__zxtl - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    kua__merf = ir.Global('format', format, loc=self.loc)
    self.store(value=kua__merf, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    rzps__wqkab = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=rzps__wqkab, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    oelq__zxtl = inst.arg
    assert oelq__zxtl > 0, 'invalid BUILD_STRING count'
    bemih__gnbh = self.get(strings[0])
    for other, eslso__xhq in zip(strings[1:], tmps):
        other = self.get(other)
        ablyj__afu = ir.Expr.binop(operator.add, lhs=bemih__gnbh, rhs=other,
            loc=self.loc)
        self.store(ablyj__afu, eslso__xhq)
        bemih__gnbh = self.get(eslso__xhq)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite.llvmpy.core import Type
    khdke__bmmj = self.context.insert_const_string(self.module, attr)
    fnty = Type.function(Type.int(), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, khdke__bmmj])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    fnn__ikuf = mk_unique_var(f'{var_name}')
    rgp__sioel = fnn__ikuf.replace('<', '_').replace('>', '_')
    rgp__sioel = rgp__sioel.replace('.', '_').replace('$', '_v')
    return rgp__sioel


if _check_numba_change:
    lines = inspect.getsource(numba.core.inline_closurecall.
        _created_inlined_var_name)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '0d91aac55cd0243e58809afe9d252562f9ae2899cde1112cc01a46804e01821e':
        warnings.warn(
            'numba.core.inline_closurecall._created_inlined_var_name has changed'
            )
numba.core.inline_closurecall._created_inlined_var_name = (
    _created_inlined_var_name)


def resolve_number___call__(self, classty):
    import numpy as np
    from numba.core.typing.templates import make_callable_template
    ty = classty.instance_type

    def typer(val):
        if isinstance(val, (types.BaseTuple, types.Sequence)):
            fnty = self.context.resolve_value_type(np.array)
            sig = fnty.get_call_type(self.context, (val, types.DType(ty)), {})
            return sig.return_type
        elif isinstance(val, (types.Number, types.Boolean, types.IntEnumMember)
            ):
            return ty
        elif val == types.unicode_type:
            return ty
        elif isinstance(val, (types.NPDatetime, types.NPTimedelta)):
            if ty.bitwidth == 64:
                return ty
            else:
                msg = f'Cannot cast {val} to {ty} as {ty} is not 64 bits wide.'
                raise errors.TypingError(msg)
        elif isinstance(val, types.Array
            ) and val.ndim == 0 and val.dtype == ty:
            return ty
        else:
            msg = f'Casting {val} to {ty} directly is unsupported.'
            if isinstance(val, types.Array):
                msg += f" Try doing '<array>.astype(np.{ty})' instead"
            raise errors.TypingError(msg)
    return types.Function(make_callable_template(key=ty, typer=typer))


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.builtins.
        NumberClassAttribute.resolve___call__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fdaf0c7d0820130481bb2bd922985257b9281b670f0bafffe10e51cabf0d5081':
        warnings.warn(
            'numba.core.typing.builtins.NumberClassAttribute.resolve___call__ has changed'
            )
numba.core.typing.builtins.NumberClassAttribute.resolve___call__ = (
    resolve_number___call__)


def on_assign(self, states, assign):
    if assign.target.name == states['varname']:
        scope = states['scope']
        oaqz__uevkl = states['defmap']
        if len(oaqz__uevkl) == 0:
            drxdt__pxbmn = assign.target
            numba.core.ssa._logger.debug('first assign: %s', drxdt__pxbmn)
            if drxdt__pxbmn.name not in scope.localvars:
                drxdt__pxbmn = scope.define(assign.target.name, loc=assign.loc)
        else:
            drxdt__pxbmn = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=drxdt__pxbmn, value=assign.value, loc=
            assign.loc)
        oaqz__uevkl[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    zocs__hoyv = []
    for qxb__lygvj, ehma__wxyyj in typing.npydecl.registry.globals:
        if qxb__lygvj == func:
            zocs__hoyv.append(ehma__wxyyj)
    for qxb__lygvj, ehma__wxyyj in typing.templates.builtin_registry.globals:
        if qxb__lygvj == func:
            zocs__hoyv.append(ehma__wxyyj)
    if len(zocs__hoyv) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return zocs__hoyv


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    mvdv__gikyf = {}
    cimn__zdblx = find_topo_order(blocks)
    zsts__bwvn = {}
    for wng__cmyxl in cimn__zdblx:
        block = blocks[wng__cmyxl]
        kdh__jnswm = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                zwzza__sqf = stmt.target.name
                cjr__kmmhu = stmt.value
                if (cjr__kmmhu.op == 'getattr' and cjr__kmmhu.attr in
                    arr_math and isinstance(typemap[cjr__kmmhu.value.name],
                    types.npytypes.Array)):
                    cjr__kmmhu = stmt.value
                    ytyc__pjd = cjr__kmmhu.value
                    mvdv__gikyf[zwzza__sqf] = ytyc__pjd
                    scope = ytyc__pjd.scope
                    loc = ytyc__pjd.loc
                    ytisw__xbz = ir.Var(scope, mk_unique_var('$np_g_var'), loc)
                    typemap[ytisw__xbz.name] = types.misc.Module(numpy)
                    cli__uum = ir.Global('np', numpy, loc)
                    kwyv__tfgyw = ir.Assign(cli__uum, ytisw__xbz, loc)
                    cjr__kmmhu.value = ytisw__xbz
                    kdh__jnswm.append(kwyv__tfgyw)
                    func_ir._definitions[ytisw__xbz.name] = [cli__uum]
                    func = getattr(numpy, cjr__kmmhu.attr)
                    fggbi__atbrf = get_np_ufunc_typ_lst(func)
                    zsts__bwvn[zwzza__sqf] = fggbi__atbrf
                if (cjr__kmmhu.op == 'call' and cjr__kmmhu.func.name in
                    mvdv__gikyf):
                    ytyc__pjd = mvdv__gikyf[cjr__kmmhu.func.name]
                    qjqh__dxcoa = calltypes.pop(cjr__kmmhu)
                    uoi__wsbj = qjqh__dxcoa.args[:len(cjr__kmmhu.args)]
                    oxqs__xqfmf = {name: typemap[ehma__wxyyj.name] for name,
                        ehma__wxyyj in cjr__kmmhu.kws}
                    yhw__dgtek = zsts__bwvn[cjr__kmmhu.func.name]
                    ykikx__rrlwd = None
                    for vag__aqy in yhw__dgtek:
                        try:
                            ykikx__rrlwd = vag__aqy.get_call_type(typingctx,
                                [typemap[ytyc__pjd.name]] + list(uoi__wsbj),
                                oxqs__xqfmf)
                            typemap.pop(cjr__kmmhu.func.name)
                            typemap[cjr__kmmhu.func.name] = vag__aqy
                            calltypes[cjr__kmmhu] = ykikx__rrlwd
                            break
                        except Exception as rihfs__hjvbc:
                            pass
                    if ykikx__rrlwd is None:
                        raise TypeError(
                            f'No valid template found for {cjr__kmmhu.func.name}'
                            )
                    cjr__kmmhu.args = [ytyc__pjd] + cjr__kmmhu.args
            kdh__jnswm.append(stmt)
        block.body = kdh__jnswm


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    ojqrs__vwtj = ufunc.nin
    ekn__vzvkk = ufunc.nout
    jnp__pegjh = ufunc.nargs
    assert jnp__pegjh == ojqrs__vwtj + ekn__vzvkk
    if len(args) < ojqrs__vwtj:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            ojqrs__vwtj))
    if len(args) > jnp__pegjh:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), jnp__pegjh)
            )
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    crsot__tqavt = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    mjnmq__qfl = max(crsot__tqavt)
    vhsbw__vxo = args[ojqrs__vwtj:]
    if not all(twmw__ckny == mjnmq__qfl for twmw__ckny in crsot__tqavt[
        ojqrs__vwtj:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(nwy__xvqtm, types.ArrayCompatible) and not
        isinstance(nwy__xvqtm, types.Bytes) for nwy__xvqtm in vhsbw__vxo):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(nwy__xvqtm.mutable for nwy__xvqtm in vhsbw__vxo):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    yoe__mvlc = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    nvht__dsvac = None
    if mjnmq__qfl > 0 and len(vhsbw__vxo) < ufunc.nout:
        nvht__dsvac = 'C'
        tlxnb__ubyh = [(x.layout if isinstance(x, types.ArrayCompatible) and
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in tlxnb__ubyh and 'F' in tlxnb__ubyh:
            nvht__dsvac = 'F'
    return yoe__mvlc, vhsbw__vxo, mjnmq__qfl, nvht__dsvac


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.npydecl.Numpy_rules_ufunc.
        _handle_inputs)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4b97c64ad9c3d50e082538795054f35cf6d2fe962c3ca40e8377a4601b344d5c':
        warnings.warn('Numpy_rules_ufunc._handle_inputs has changed')
numba.core.typing.npydecl.Numpy_rules_ufunc._handle_inputs = (
    _Numpy_Rules_ufunc_handle_inputs)
numba.np.ufunc.dufunc.npydecl.Numpy_rules_ufunc._handle_inputs = (
    _Numpy_Rules_ufunc_handle_inputs)


def DictType__init__(self, keyty, valty, initial_value=None):
    from numba.types import DictType, InitialValue, NoneType, Optional, Tuple, TypeRef, unliteral
    assert not isinstance(keyty, TypeRef)
    assert not isinstance(valty, TypeRef)
    keyty = unliteral(keyty)
    valty = unliteral(valty)
    if isinstance(keyty, (Optional, NoneType)):
        utjl__tbbe = 'Dict.key_type cannot be of type {}'
        raise TypingError(utjl__tbbe.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        utjl__tbbe = 'Dict.value_type cannot be of type {}'
        raise TypingError(utjl__tbbe.format(valty))
    self.key_type = keyty
    self.value_type = valty
    self.keyvalue_type = Tuple([keyty, valty])
    name = '{}[{},{}]<iv={}>'.format(self.__class__.__name__, keyty, valty,
        initial_value)
    super(DictType, self).__init__(name)
    InitialValue.__init__(self, initial_value)


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.containers.DictType.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '475acd71224bd51526750343246e064ff071320c0d10c17b8b8ac81d5070d094':
        warnings.warn('DictType.__init__ has changed')
numba.core.types.containers.DictType.__init__ = DictType__init__


def _legalize_arg_types(self, args):
    for gfxjm__emmfw, a in enumerate(args, start=1):
        if isinstance(a, types.Dispatcher):
            msg = (
                'Does not support function type inputs into with-context for arg {}'
                )
            raise errors.TypingError(msg.format(gfxjm__emmfw))


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.ObjModeLiftedWith.
        _legalize_arg_types)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4793f44ebc7da8843e8f298e08cd8a5428b4b84b89fd9d5c650273fdb8fee5ee':
        warnings.warn('ObjModeLiftedWith._legalize_arg_types has changed')
numba.core.dispatcher.ObjModeLiftedWith._legalize_arg_types = (
    _legalize_arg_types)


def _overload_template_get_impl(self, args, kws):
    urk__uhide = self.context, tuple(args), tuple(kws.items())
    try:
        vrbpr__qnt, args = self._impl_cache[urk__uhide]
        return vrbpr__qnt, args
    except KeyError as rihfs__hjvbc:
        pass
    vrbpr__qnt, args = self._build_impl(urk__uhide, args, kws)
    return vrbpr__qnt, args


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadFunctionTemplate._get_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4e27d07b214ca16d6e8ed88f70d886b6b095e160d8f77f8df369dd4ed2eb3fae':
        warnings.warn(
            'numba.core.typing.templates._OverloadFunctionTemplate._get_impl has changed'
            )
numba.core.typing.templates._OverloadFunctionTemplate._get_impl = (
    _overload_template_get_impl)


def remove_dead_parfor(parfor, lives, lives_n_aliases, arg_aliases,
    alias_map, func_ir, typemap):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    from numba.core.ir_utils import find_topo_order
    from numba.parfors.parfor import _add_liveness_return_block, _update_parfor_get_setitems, dummy_return_in_loop_body, get_index_var, remove_dead_parfor_recursive, simplify_parfor_body_CFG
    with dummy_return_in_loop_body(parfor.loop_body):
        pwnv__tdmzm = find_topo_order(parfor.loop_body)
    keekw__hhlkm = pwnv__tdmzm[0]
    zkaj__bonak = {}
    _update_parfor_get_setitems(parfor.loop_body[keekw__hhlkm].body, parfor
        .index_var, alias_map, zkaj__bonak, lives_n_aliases)
    jprsw__ssxxy = set(zkaj__bonak.keys())
    for fzdwu__mykz in pwnv__tdmzm:
        if fzdwu__mykz == keekw__hhlkm:
            continue
        for stmt in parfor.loop_body[fzdwu__mykz].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            ebao__gij = set(ehma__wxyyj.name for ehma__wxyyj in stmt.
                list_vars())
            djnnq__qwqw = ebao__gij & jprsw__ssxxy
            for a in djnnq__qwqw:
                zkaj__bonak.pop(a, None)
    for fzdwu__mykz in pwnv__tdmzm:
        if fzdwu__mykz == keekw__hhlkm:
            continue
        block = parfor.loop_body[fzdwu__mykz]
        lvx__sdse = zkaj__bonak.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            lvx__sdse, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    rvw__sfyh = max(blocks.keys())
    ajmb__nzyl, epr__vhyr = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    vwucw__bmc = ir.Jump(ajmb__nzyl, ir.Loc('parfors_dummy', -1))
    blocks[rvw__sfyh].body.append(vwucw__bmc)
    cwmwn__ydbt = compute_cfg_from_blocks(blocks)
    jprw__mkmj = compute_use_defs(blocks)
    ysaj__heg = compute_live_map(cwmwn__ydbt, blocks, jprw__mkmj.usemap,
        jprw__mkmj.defmap)
    alias_set = set(alias_map.keys())
    for wng__cmyxl, block in blocks.items():
        kdh__jnswm = []
        gehq__fjfe = {ehma__wxyyj.name for ehma__wxyyj in block.terminator.
            list_vars()}
        for vnlku__jvao, rqxyq__wpx in cwmwn__ydbt.successors(wng__cmyxl):
            gehq__fjfe |= ysaj__heg[vnlku__jvao]
        for stmt in reversed(block.body):
            vgj__xlls = gehq__fjfe & alias_set
            for ehma__wxyyj in vgj__xlls:
                gehq__fjfe |= alias_map[ehma__wxyyj]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in gehq__fjfe and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                lrazt__ocmdp = guard(find_callname, func_ir, stmt.value)
                if lrazt__ocmdp == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in gehq__fjfe and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            gehq__fjfe |= {ehma__wxyyj.name for ehma__wxyyj in stmt.list_vars()
                }
            kdh__jnswm.append(stmt)
        kdh__jnswm.reverse()
        block.body = kdh__jnswm
    typemap.pop(epr__vhyr.name)
    blocks[rvw__sfyh].body.pop()

    def trim_empty_parfor_branches(parfor):
        xtiwf__udv = False
        blocks = parfor.loop_body.copy()
        for wng__cmyxl, block in blocks.items():
            if len(block.body):
                jzn__jqhbr = block.body[-1]
                if isinstance(jzn__jqhbr, ir.Branch):
                    if len(blocks[jzn__jqhbr.truebr].body) == 1 and len(blocks
                        [jzn__jqhbr.falsebr].body) == 1:
                        iocd__xgqlv = blocks[jzn__jqhbr.truebr].body[0]
                        qyn__kzu = blocks[jzn__jqhbr.falsebr].body[0]
                        if isinstance(iocd__xgqlv, ir.Jump) and isinstance(
                            qyn__kzu, ir.Jump
                            ) and iocd__xgqlv.target == qyn__kzu.target:
                            parfor.loop_body[wng__cmyxl].body[-1] = ir.Jump(
                                iocd__xgqlv.target, jzn__jqhbr.loc)
                            xtiwf__udv = True
                    elif len(blocks[jzn__jqhbr.truebr].body) == 1:
                        iocd__xgqlv = blocks[jzn__jqhbr.truebr].body[0]
                        if isinstance(iocd__xgqlv, ir.Jump
                            ) and iocd__xgqlv.target == jzn__jqhbr.falsebr:
                            parfor.loop_body[wng__cmyxl].body[-1] = ir.Jump(
                                iocd__xgqlv.target, jzn__jqhbr.loc)
                            xtiwf__udv = True
                    elif len(blocks[jzn__jqhbr.falsebr].body) == 1:
                        qyn__kzu = blocks[jzn__jqhbr.falsebr].body[0]
                        if isinstance(qyn__kzu, ir.Jump
                            ) and qyn__kzu.target == jzn__jqhbr.truebr:
                            parfor.loop_body[wng__cmyxl].body[-1] = ir.Jump(
                                qyn__kzu.target, jzn__jqhbr.loc)
                            xtiwf__udv = True
        return xtiwf__udv
    xtiwf__udv = True
    while xtiwf__udv:
        """
        Process parfor body recursively.
        Note that this is the only place in this function that uses the
        argument lives instead of lives_n_aliases.  The former does not
        include the aliases of live variables but only the live variable
        names themselves.  See a comment in this function for how that
        is used.
        """
        remove_dead_parfor_recursive(parfor, lives, arg_aliases, alias_map,
            func_ir, typemap)
        simplify_parfor_body_CFG(func_ir.blocks)
        xtiwf__udv = trim_empty_parfor_branches(parfor)
    phb__vmpza = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        phb__vmpza &= len(block.body) == 0
    if phb__vmpza:
        return None
    return parfor


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.remove_dead_parfor)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1c9b008a7ead13e988e1efe67618d8f87f0b9f3d092cc2cd6bfcd806b1fdb859':
        warnings.warn('remove_dead_parfor has changed')
numba.parfors.parfor.remove_dead_parfor = remove_dead_parfor
numba.core.ir_utils.remove_dead_extensions[numba.parfors.parfor.Parfor
    ] = remove_dead_parfor


def simplify_parfor_body_CFG(blocks):
    from numba.core.analysis import compute_cfg_from_blocks
    from numba.core.ir_utils import simplify_CFG
    from numba.parfors.parfor import Parfor
    yql__bpduu = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                yql__bpduu += 1
                parfor = stmt
                kffe__qhm = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = kffe__qhm.scope
                loc = ir.Loc('parfors_dummy', -1)
                ziop__bivp = ir.Var(scope, mk_unique_var('$const'), loc)
                kffe__qhm.body.append(ir.Assign(ir.Const(0, loc),
                    ziop__bivp, loc))
                kffe__qhm.body.append(ir.Return(ziop__bivp, loc))
                cwmwn__ydbt = compute_cfg_from_blocks(parfor.loop_body)
                for fis__ffixi in cwmwn__ydbt.dead_nodes():
                    del parfor.loop_body[fis__ffixi]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                kffe__qhm = parfor.loop_body[max(parfor.loop_body.keys())]
                kffe__qhm.body.pop()
                kffe__qhm.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return yql__bpduu


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.simplify_parfor_body_CFG)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '437ae96a5e8ec64a2b69a4f23ba8402a1d170262a5400aa0aa7bfe59e03bf726':
        warnings.warn('simplify_parfor_body_CFG has changed')
numba.parfors.parfor.simplify_parfor_body_CFG = simplify_parfor_body_CFG


def _lifted_compile(self, sig):
    import numba.core.event as ev
    from numba.core import compiler, sigutils
    from numba.core.compiler_lock import global_compiler_lock
    from numba.core.ir_utils import remove_dels
    with ExitStack() as scope:
        cres = None

        def cb_compiler(dur):
            if cres is not None:
                self._callback_add_compiler_timer(dur, cres)

        def cb_llvm(dur):
            if cres is not None:
                self._callback_add_llvm_timer(dur, cres)
        scope.enter_context(ev.install_timer('numba:compiler_lock',
            cb_compiler))
        scope.enter_context(ev.install_timer('numba:llvm_lock', cb_llvm))
        scope.enter_context(global_compiler_lock)
        with self._compiling_counter:
            flags = self.flags
            args, return_type = sigutils.normalize_signature(sig)
            gbh__jvqo = self.overloads.get(tuple(args))
            if gbh__jvqo is not None:
                return gbh__jvqo.entry_point
            self._pre_compile(args, return_type, flags)
            xuly__avjei = self.func_ir
            kmcrs__coby = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=kmcrs__coby):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=xuly__avjei, args=
                    args, return_type=return_type, flags=flags, locals=self
                    .locals, lifted=(), lifted_from=self.lifted_from,
                    is_lifted_loop=True)
                if cres.typing_error is not None and not flags.enable_pyobject:
                    raise cres.typing_error
                self.add_overload(cres)
            remove_dels(self.func_ir.blocks)
            return cres.entry_point


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.LiftedCode.compile)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1351ebc5d8812dc8da167b30dad30eafb2ca9bf191b49aaed6241c21e03afff1':
        warnings.warn('numba.core.dispatcher.LiftedCode.compile has changed')
numba.core.dispatcher.LiftedCode.compile = _lifted_compile


def compile_ir(typingctx, targetctx, func_ir, args, return_type, flags,
    locals, lifted=(), lifted_from=None, is_lifted_loop=False, library=None,
    pipeline_class=Compiler):
    if is_lifted_loop:
        oqjj__zcfb = copy.deepcopy(flags)
        oqjj__zcfb.no_rewrites = True

        def compile_local(the_ir, the_flags):
            qiy__tjgo = pipeline_class(typingctx, targetctx, library, args,
                return_type, the_flags, locals)
            return qiy__tjgo.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        vbsw__rowx = compile_local(func_ir, oqjj__zcfb)
        lfx__ylc = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    lfx__ylc = compile_local(func_ir, flags)
                except Exception as rihfs__hjvbc:
                    pass
        if lfx__ylc is not None:
            cres = lfx__ylc
        else:
            cres = vbsw__rowx
        return cres
    else:
        qiy__tjgo = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return qiy__tjgo.compile_ir(func_ir=func_ir, lifted=lifted,
            lifted_from=lifted_from)


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.compile_ir)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c48ce5493f4c43326e8cbdd46f3ea038b2b9045352d9d25894244798388e5e5b':
        warnings.warn('numba.core.compiler.compile_ir has changed')
numba.core.compiler.compile_ir = compile_ir


def make_constant_array(self, builder, typ, ary):
    import math
    from llvmlite import ir as lir
    from llvmlite.llvmpy.core import Constant, Type
    jdw__ofdr = self.get_data_type(typ.dtype)
    mnln__fnwpf = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        mnln__fnwpf):
        uak__ujm = ary.ctypes.data
        xkz__sxf = self.add_dynamic_addr(builder, uak__ujm, info=str(type(
            uak__ujm)))
        zaqzu__oeq = self.add_dynamic_addr(builder, id(ary), info=str(type(
            ary)))
        self.global_arrays.append(ary)
    else:
        jlfc__edf = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            jlfc__edf = jlfc__edf.view('int64')
        ayajg__fgmd = Constant.array(Type.int(8), bytearray(jlfc__edf.data))
        xkz__sxf = cgutils.global_constant(builder, '.const.array.data',
            ayajg__fgmd)
        xkz__sxf.align = self.get_abi_alignment(jdw__ofdr)
        zaqzu__oeq = None
    bhky__zfvr = self.get_value_type(types.intp)
    btbe__kwjkg = [self.get_constant(types.intp, aujtk__cdtx) for
        aujtk__cdtx in ary.shape]
    hpwty__ays = Constant.array(bhky__zfvr, btbe__kwjkg)
    hzy__dup = [self.get_constant(types.intp, aujtk__cdtx) for aujtk__cdtx in
        ary.strides]
    aej__mslt = Constant.array(bhky__zfvr, hzy__dup)
    nyxvn__ngk = self.get_constant(types.intp, ary.dtype.itemsize)
    zll__uohqv = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        zll__uohqv, nyxvn__ngk, xkz__sxf.bitcast(self.get_value_type(types.
        CPointer(typ.dtype))), hpwty__ays, aej__mslt])


if _check_numba_change:
    lines = inspect.getsource(numba.core.base.BaseContext.make_constant_array)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5721b5360b51f782f79bd794f7bf4d48657911ecdc05c30db22fd55f15dad821':
        warnings.warn(
            'numba.core.base.BaseContext.make_constant_array has changed')
numba.core.base.BaseContext.make_constant_array = make_constant_array


def _define_atomic_inc_dec(module, op, ordering):
    from llvmlite import ir as lir
    from numba.core.runtime.nrtdynmod import _word_type
    klwcr__tnw = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    laz__egebs = lir.Function(module, klwcr__tnw, name='nrt_atomic_{0}'.
        format(op))
    [rnwx__qslbe] = laz__egebs.args
    jwl__zys = laz__egebs.append_basic_block()
    builder = lir.IRBuilder(jwl__zys)
    mzo__aib = lir.Constant(_word_type, 1)
    if False:
        vun__tfyr = builder.atomic_rmw(op, rnwx__qslbe, mzo__aib, ordering=
            ordering)
        res = getattr(builder, op)(vun__tfyr, mzo__aib)
        builder.ret(res)
    else:
        vun__tfyr = builder.load(rnwx__qslbe)
        rdqdq__wgp = getattr(builder, op)(vun__tfyr, mzo__aib)
        smtk__psqf = builder.icmp_signed('!=', vun__tfyr, lir.Constant(
            vun__tfyr.type, -1))
        with cgutils.if_likely(builder, smtk__psqf):
            builder.store(rdqdq__wgp, rnwx__qslbe)
        builder.ret(rdqdq__wgp)
    return laz__egebs


if _check_numba_change:
    lines = inspect.getsource(numba.core.runtime.nrtdynmod.
        _define_atomic_inc_dec)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '9cc02c532b2980b6537b702f5608ea603a1ff93c6d3c785ae2cf48bace273f48':
        warnings.warn(
            'numba.core.runtime.nrtdynmod._define_atomic_inc_dec has changed')
numba.core.runtime.nrtdynmod._define_atomic_inc_dec = _define_atomic_inc_dec


def NativeLowering_run_pass(self, state):
    from llvmlite import binding as llvm
    from numba.core import funcdesc, lowering
    from numba.core.typed_passes import fallback_context
    if state.library is None:
        gaga__posls = state.targetctx.codegen()
        state.library = gaga__posls.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    sma__xdl = state.func_ir
    typemap = state.typemap
    fdb__jvj = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    hifx__fnnp = state.metadata
    zpf__iwlv = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        xxun__yqz = (funcdesc.PythonFunctionDescriptor.
            from_specialized_function(sma__xdl, typemap, fdb__jvj,
            calltypes, mangler=targetctx.mangler, inline=flags.forceinline,
            noalias=flags.noalias, abi_tags=[flags.get_mangle_string()]))
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            lth__pzke = lowering.Lower(targetctx, library, xxun__yqz,
                sma__xdl, metadata=hifx__fnnp)
            lth__pzke.lower()
            if not flags.no_cpython_wrapper:
                lth__pzke.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(fdb__jvj, (types.Optional, types.Generator)):
                        pass
                    else:
                        lth__pzke.create_cfunc_wrapper()
            kwvh__xbqjd = lth__pzke.env
            zdgyq__wbb = lth__pzke.call_helper
            del lth__pzke
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(xxun__yqz, zdgyq__wbb, cfunc=None,
                env=kwvh__xbqjd)
        else:
            nhs__xscw = targetctx.get_executable(library, xxun__yqz,
                kwvh__xbqjd)
            targetctx.insert_user_function(nhs__xscw, xxun__yqz, [library])
            state['cr'] = _LowerResult(xxun__yqz, zdgyq__wbb, cfunc=
                nhs__xscw, env=kwvh__xbqjd)
        hifx__fnnp['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        hqdc__uco = llvm.passmanagers.dump_refprune_stats()
        hifx__fnnp['prune_stats'] = hqdc__uco - zpf__iwlv
        hifx__fnnp['llvm_pass_timings'] = library.recorded_timings
    return True


if _check_numba_change:
    lines = inspect.getsource(numba.core.typed_passes.NativeLowering.run_pass)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a777ce6ce1bb2b1cbaa3ac6c2c0e2adab69a9c23888dff5f1cbb67bfb176b5de':
        warnings.warn(
            'numba.core.typed_passes.NativeLowering.run_pass has changed')
numba.core.typed_passes.NativeLowering.run_pass = NativeLowering_run_pass


def _python_list_to_native(typ, obj, c, size, listptr, errorptr):
    from llvmlite import ir as lir
    from numba.core.boxing import _NumbaTypeHelper
    from numba.cpython import listobj

    def check_element_type(nth, itemobj, expected_typobj):
        tcr__cwfw = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, tcr__cwfw),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            loop.do_break()
        ppp__qicso = c.builder.icmp_signed('!=', tcr__cwfw, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(ppp__qicso, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, tcr__cwfw)
                c.pyapi.decref(tcr__cwfw)
                loop.do_break()
        c.pyapi.decref(tcr__cwfw)
    gyfj__fvdio, list = listobj.ListInstance.allocate_ex(c.context, c.
        builder, typ, size)
    with c.builder.if_else(gyfj__fvdio, likely=True) as (if_ok, if_not_ok):
        with if_ok:
            list.size = size
            owbqw__qlbxq = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                owbqw__qlbxq), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        owbqw__qlbxq))
                    with cgutils.for_range(c.builder, size) as loop:
                        itemobj = c.pyapi.list_getitem(obj, loop.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        szrbk__fqpy = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(szrbk__fqpy.is_error, likely
                            =False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            loop.do_break()
                        list.setitem(loop.index, szrbk__fqpy.value, incref=
                            False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with if_not_ok:
            c.builder.store(cgutils.true_bit, errorptr)
    with c.builder.if_then(c.builder.load(errorptr)):
        c.context.nrt.decref(c.builder, typ, list.value)


if _check_numba_change:
    lines = inspect.getsource(numba.core.boxing._python_list_to_native)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f8e546df8b07adfe74a16b6aafb1d4fddbae7d3516d7944b3247cc7c9b7ea88a':
        warnings.warn('numba.core.boxing._python_list_to_native has changed')
numba.core.boxing._python_list_to_native = _python_list_to_native


def make_string_from_constant(context, builder, typ, literal_string):
    from llvmlite import ir as lir
    from numba.cpython.hashing import _Py_hash_t
    from numba.cpython.unicode import compile_time_get_string_data
    lpv__wum, wxn__alr, mooty__uhmm, qsbqi__cihpg, hgal__sxns = (
        compile_time_get_string_data(literal_string))
    dne__jotg = builder.module
    gv = context.insert_const_bytes(dne__jotg, lpv__wum)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        wxn__alr), context.get_constant(types.int32, mooty__uhmm), context.
        get_constant(types.uint32, qsbqi__cihpg), context.get_constant(
        _Py_hash_t, -1), context.get_constant_null(types.MemInfoPointer(
        types.voidptr)), context.get_constant_null(types.pyobject)])


if _check_numba_change:
    lines = inspect.getsource(numba.cpython.unicode.make_string_from_constant)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '525bd507383e06152763e2f046dae246cd60aba027184f50ef0fc9a80d4cd7fa':
        warnings.warn(
            'numba.cpython.unicode.make_string_from_constant has changed')
numba.cpython.unicode.make_string_from_constant = make_string_from_constant


def parse_shape(shape):
    esm__yztly = None
    if isinstance(shape, types.Integer):
        esm__yztly = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(aujtk__cdtx, (types.Integer, types.IntEnumMember)
            ) for aujtk__cdtx in shape):
            esm__yztly = len(shape)
    return esm__yztly


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.npydecl.parse_shape)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'e62e3ff09d36df5ac9374055947d6a8be27160ce32960d3ef6cb67f89bd16429':
        warnings.warn('numba.core.typing.npydecl.parse_shape has changed')
numba.core.typing.npydecl.parse_shape = parse_shape


def _get_names(self, obj):
    if isinstance(obj, ir.Var) or isinstance(obj, str):
        name = obj if isinstance(obj, str) else obj.name
        if name not in self.typemap:
            return name,
        typ = self.typemap[name]
        if isinstance(typ, (types.BaseTuple, types.ArrayCompatible)):
            esm__yztly = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if esm__yztly == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, gfxjm__emmfw) for
                    gfxjm__emmfw in range(esm__yztly))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            dcam__egge = self._get_names(x)
            if len(dcam__egge) != 0:
                return dcam__egge[0]
            return dcam__egge
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    dcam__egge = self._get_names(obj)
    if len(dcam__egge) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(dcam__egge[0])


def get_equiv_set(self, obj):
    dcam__egge = self._get_names(obj)
    if len(dcam__egge) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(dcam__egge[0])


if _check_numba_change:
    for name, orig, new, hash in ((
        'numba.parfors.array_analysis.ShapeEquivSet._get_names', numba.
        parfors.array_analysis.ShapeEquivSet._get_names, _get_names,
        '8c9bf136109028d5445fd0a82387b6abeb70c23b20b41e2b50c34ba5359516ee'),
        ('numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const',
        numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const,
        get_equiv_const,
        'bef410ca31a9e29df9ee74a4a27d339cc332564e4a237828b8a4decf625ce44e'),
        ('numba.parfors.array_analysis.ShapeEquivSet.get_equiv_set', numba.
        parfors.array_analysis.ShapeEquivSet.get_equiv_set, get_equiv_set,
        'ec936d340c488461122eb74f28a28b88227cb1f1bca2b9ba3c19258cfe1eb40a')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
numba.parfors.array_analysis.ShapeEquivSet._get_names = _get_names
numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const = get_equiv_const
numba.parfors.array_analysis.ShapeEquivSet.get_equiv_set = get_equiv_set


def raise_on_unsupported_feature(func_ir, typemap):
    import numpy
    zfnks__dfati = []
    for hxrpj__eclb in func_ir.arg_names:
        if hxrpj__eclb in typemap and isinstance(typemap[hxrpj__eclb],
            types.containers.UniTuple) and typemap[hxrpj__eclb].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(hxrpj__eclb))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for ats__jsea in func_ir.blocks.values():
        for stmt in ats__jsea.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    hfj__hdgr = getattr(val, 'code', None)
                    if hfj__hdgr is not None:
                        if getattr(val, 'closure', None) is not None:
                            csayc__dlll = (
                                '<creating a function from a closure>')
                            ablyj__afu = ''
                        else:
                            csayc__dlll = hfj__hdgr.co_name
                            ablyj__afu = '(%s) ' % csayc__dlll
                    else:
                        csayc__dlll = '<could not ascertain use case>'
                        ablyj__afu = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (csayc__dlll, ablyj__afu))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                xza__gipf = False
                if isinstance(val, pytypes.FunctionType):
                    xza__gipf = val in {numba.gdb, numba.gdb_init}
                if not xza__gipf:
                    xza__gipf = getattr(val, '_name', '') == 'gdb_internal'
                if xza__gipf:
                    zfnks__dfati.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    vmoh__sto = func_ir.get_definition(var)
                    yzmqt__jcr = guard(find_callname, func_ir, vmoh__sto)
                    if yzmqt__jcr and yzmqt__jcr[1] == 'numpy':
                        ty = getattr(numpy, yzmqt__jcr[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    uawe__bfi = '' if var.startswith('$') else "'{}' ".format(
                        var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(uawe__bfi), loc=stmt.loc)
            if isinstance(stmt.value, ir.Global):
                ty = typemap[stmt.target.name]
                msg = (
                    "The use of a %s type, assigned to variable '%s' in globals, is not supported as globals are considered compile-time constants and there is no known way to compile a %s type as a constant."
                    )
                if getattr(ty, 'reflected', False) or isinstance(ty, types.
                    ListType):
                    raise TypingError(msg % (ty, stmt.value.name, ty), loc=
                        stmt.loc)
            if isinstance(stmt.value, ir.Yield) and not func_ir.is_generator:
                msg = 'The use of generator expressions is unsupported.'
                raise errors.UnsupportedError(msg, loc=stmt.loc)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.raise_on_unsupported_feature)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'eca43ce27128a243039d2b20d5da0cb8823403911814135b9b74f2b6549daf3d':
        warnings.warn(
            'numba.core.ir_utils.raise_on_unsupported_feature has changed')
numba.core.ir_utils.raise_on_unsupported_feature = raise_on_unsupported_feature
numba.core.typed_passes.raise_on_unsupported_feature = (
    raise_on_unsupported_feature)


@typeof_impl.register(dict)
def _typeof_dict(val, c):
    if len(val) == 0:
        raise ValueError('Cannot type empty dict')
    qxb__lygvj, ehma__wxyyj = next(iter(val.items()))
    nxkbi__hjp = typeof_impl(qxb__lygvj, c)
    aqjfo__bkjnl = typeof_impl(ehma__wxyyj, c)
    if nxkbi__hjp is None or aqjfo__bkjnl is None:
        raise ValueError(
            f'Cannot type dict element type {type(qxb__lygvj)}, {type(ehma__wxyyj)}'
            )
    return types.DictType(nxkbi__hjp, aqjfo__bkjnl)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    qwi__dpu = cgutils.alloca_once_value(c.builder, val)
    tvt__qfxf = c.pyapi.object_hasattr_string(val, '_opaque')
    vgd__deuo = c.builder.icmp_unsigned('==', tvt__qfxf, lir.Constant(
        tvt__qfxf.type, 0))
    jbs__fuur = typ.key_type
    onauv__tdomd = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(jbs__fuur, onauv__tdomd)

    def copy_dict(out_dict, in_dict):
        for qxb__lygvj, ehma__wxyyj in in_dict.items():
            out_dict[qxb__lygvj] = ehma__wxyyj
    with c.builder.if_then(vgd__deuo):
        eqhos__cqenz = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        izjzr__pnzu = c.pyapi.call_function_objargs(eqhos__cqenz, [])
        jbnf__qtf = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(jbnf__qtf, [izjzr__pnzu, val])
        c.builder.store(izjzr__pnzu, qwi__dpu)
    val = c.builder.load(qwi__dpu)
    iquac__qvk = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    fiorj__eac = c.pyapi.object_type(val)
    wxhud__pwa = c.builder.icmp_unsigned('==', fiorj__eac, iquac__qvk)
    with c.builder.if_else(wxhud__pwa) as (then, orelse):
        with then:
            clypf__rtku = c.pyapi.object_getattr_string(val, '_opaque')
            ozoe__xgi = types.MemInfoPointer(types.voidptr)
            szrbk__fqpy = c.unbox(ozoe__xgi, clypf__rtku)
            mi = szrbk__fqpy.value
            qyt__nkj = ozoe__xgi, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *qyt__nkj)
            spn__hke = context.get_constant_null(qyt__nkj[1])
            args = mi, spn__hke
            clao__psra, urntf__qly = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, urntf__qly)
            c.pyapi.decref(clypf__rtku)
            cad__agix = c.builder.basic_block
        with orelse:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", fiorj__eac, iquac__qvk)
            pmdw__obpon = c.builder.basic_block
    deep__rtt = c.builder.phi(urntf__qly.type)
    biwxw__gdadb = c.builder.phi(clao__psra.type)
    deep__rtt.add_incoming(urntf__qly, cad__agix)
    deep__rtt.add_incoming(urntf__qly.type(None), pmdw__obpon)
    biwxw__gdadb.add_incoming(clao__psra, cad__agix)
    biwxw__gdadb.add_incoming(cgutils.true_bit, pmdw__obpon)
    c.pyapi.decref(iquac__qvk)
    c.pyapi.decref(fiorj__eac)
    with c.builder.if_then(vgd__deuo):
        c.pyapi.decref(val)
    return NativeValue(deep__rtt, is_error=biwxw__gdadb)


import numba.typed.typeddict
if _check_numba_change:
    lines = inspect.getsource(numba.core.pythonapi._unboxers.functions[
        numba.core.types.DictType])
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5f6f183b94dc57838538c668a54c2476576c85d8553843f3219f5162c61e7816':
        warnings.warn('unbox_dicttype has changed')
numba.core.pythonapi._unboxers.functions[types.DictType] = unbox_dicttype
