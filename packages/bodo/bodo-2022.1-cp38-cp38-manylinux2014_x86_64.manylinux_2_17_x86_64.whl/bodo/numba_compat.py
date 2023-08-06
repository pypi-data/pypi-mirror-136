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
    tgg__jvv = numba.core.bytecode.FunctionIdentity.from_function(func)
    ovx__bfauy = numba.core.interpreter.Interpreter(tgg__jvv)
    mvcg__lfx = numba.core.bytecode.ByteCode(func_id=tgg__jvv)
    func_ir = ovx__bfauy.interpret(mvcg__lfx)
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
        drpj__uzio = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        drpj__uzio.run()
    vjki__ojffw = numba.core.postproc.PostProcessor(func_ir)
    vjki__ojffw.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, vzs__bwzgi in visit_vars_extensions.items():
        if isinstance(stmt, t):
            vzs__bwzgi(stmt, callback, cbdata)
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
    rjsj__rye = ['ravel', 'transpose', 'reshape']
    for tvqh__zqc in blocks.values():
        for dsbnd__txk in tvqh__zqc.body:
            if type(dsbnd__txk) in alias_analysis_extensions:
                vzs__bwzgi = alias_analysis_extensions[type(dsbnd__txk)]
                vzs__bwzgi(dsbnd__txk, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(dsbnd__txk, ir.Assign):
                cix__amnh = dsbnd__txk.value
                ljby__qgim = dsbnd__txk.target.name
                if is_immutable_type(ljby__qgim, typemap):
                    continue
                if isinstance(cix__amnh, ir.Var
                    ) and ljby__qgim != cix__amnh.name:
                    _add_alias(ljby__qgim, cix__amnh.name, alias_map,
                        arg_aliases)
                if isinstance(cix__amnh, ir.Expr) and (cix__amnh.op ==
                    'cast' or cix__amnh.op in ['getitem', 'static_getitem']):
                    _add_alias(ljby__qgim, cix__amnh.value.name, alias_map,
                        arg_aliases)
                if isinstance(cix__amnh, ir.Expr
                    ) and cix__amnh.op == 'inplace_binop':
                    _add_alias(ljby__qgim, cix__amnh.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(cix__amnh, ir.Expr
                    ) and cix__amnh.op == 'getattr' and cix__amnh.attr in ['T',
                    'ctypes', 'flat']:
                    _add_alias(ljby__qgim, cix__amnh.value.name, alias_map,
                        arg_aliases)
                if isinstance(cix__amnh, ir.Expr
                    ) and cix__amnh.op == 'getattr' and cix__amnh.attr not in [
                    'shape'] and cix__amnh.value.name in arg_aliases:
                    _add_alias(ljby__qgim, cix__amnh.value.name, alias_map,
                        arg_aliases)
                if isinstance(cix__amnh, ir.Expr
                    ) and cix__amnh.op == 'getattr' and cix__amnh.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(ljby__qgim, cix__amnh.value.name, alias_map,
                        arg_aliases)
                if isinstance(cix__amnh, ir.Expr) and cix__amnh.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(ljby__qgim, typemap):
                    for jdoou__ygka in cix__amnh.items:
                        _add_alias(ljby__qgim, jdoou__ygka.name, alias_map,
                            arg_aliases)
                if isinstance(cix__amnh, ir.Expr) and cix__amnh.op == 'call':
                    qhue__kpp = guard(find_callname, func_ir, cix__amnh,
                        typemap)
                    if qhue__kpp is None:
                        continue
                    sso__wzlpw, ffqz__zpep = qhue__kpp
                    if qhue__kpp in alias_func_extensions:
                        fokgo__gltje = alias_func_extensions[qhue__kpp]
                        fokgo__gltje(ljby__qgim, cix__amnh.args, alias_map,
                            arg_aliases)
                    if ffqz__zpep == 'numpy' and sso__wzlpw in rjsj__rye:
                        _add_alias(ljby__qgim, cix__amnh.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(ffqz__zpep, ir.Var
                        ) and sso__wzlpw in rjsj__rye:
                        _add_alias(ljby__qgim, ffqz__zpep.name, alias_map,
                            arg_aliases)
    ppp__ajg = copy.deepcopy(alias_map)
    for jdoou__ygka in ppp__ajg:
        for amfxq__eaon in ppp__ajg[jdoou__ygka]:
            alias_map[jdoou__ygka] |= alias_map[amfxq__eaon]
        for amfxq__eaon in ppp__ajg[jdoou__ygka]:
            alias_map[amfxq__eaon] = alias_map[jdoou__ygka]
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
    hitp__gpy = compute_cfg_from_blocks(func_ir.blocks)
    tsj__ufygd = compute_use_defs(func_ir.blocks)
    esar__zkhl = compute_live_map(hitp__gpy, func_ir.blocks, tsj__ufygd.
        usemap, tsj__ufygd.defmap)
    for icg__ahc, block in func_ir.blocks.items():
        lives = {jdoou__ygka.name for jdoou__ygka in block.terminator.
            list_vars()}
        for lbeb__lqv, gsey__ydkv in hitp__gpy.successors(icg__ahc):
            lives |= esar__zkhl[lbeb__lqv]
        reue__xjcw = [block.terminator]
        for stmt in reversed(block.body[:-1]):
            if isinstance(stmt, ir.Assign):
                ljby__qgim = stmt.target
                nkey__ayg = stmt.value
                if ljby__qgim.name not in lives:
                    if isinstance(nkey__ayg, ir.Expr
                        ) and nkey__ayg.op == 'make_function':
                        continue
                    if isinstance(nkey__ayg, ir.Expr
                        ) and nkey__ayg.op == 'getattr':
                        continue
                    if isinstance(nkey__ayg, ir.Const):
                        continue
                    if typemap and isinstance(typemap.get(ljby__qgim, None),
                        types.Function):
                        continue
                if isinstance(nkey__ayg, ir.Var
                    ) and ljby__qgim.name == nkey__ayg.name:
                    continue
            if isinstance(stmt, ir.Del):
                if stmt.value not in lives:
                    continue
            if type(stmt) in analysis.ir_extension_usedefs:
                bqm__npxt = analysis.ir_extension_usedefs[type(stmt)]
                rtw__bgnhb, nsrsw__qdgt = bqm__npxt(stmt)
                lives -= nsrsw__qdgt
                lives |= rtw__bgnhb
            else:
                lives |= {jdoou__ygka.name for jdoou__ygka in stmt.list_vars()}
                if isinstance(stmt, ir.Assign):
                    lives.remove(ljby__qgim.name)
            reue__xjcw.append(stmt)
        reue__xjcw.reverse()
        block.body = reue__xjcw


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    wdpx__eiphn = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (wdpx__eiphn,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    mfc__itjt = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), mfc__itjt)


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
            for hffnf__slqc in fnty.templates:
                self._inline_overloads.update(hffnf__slqc._inline_overloads)
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
    mfc__itjt = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), mfc__itjt)
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
    nkuf__ksced, lbnof__uuvpk = self._get_impl(args, kws)
    if nkuf__ksced is None:
        return
    dcygp__wqkog = types.Dispatcher(nkuf__ksced)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        oiie__kjces = nkuf__ksced._compiler
        flags = compiler.Flags()
        iurgk__xzxp = oiie__kjces.targetdescr.typing_context
        mymi__uzpti = oiie__kjces.targetdescr.target_context
        xnlp__bxljo = oiie__kjces.pipeline_class(iurgk__xzxp, mymi__uzpti,
            None, None, None, flags, None)
        llr__utfhm = InlineWorker(iurgk__xzxp, mymi__uzpti, oiie__kjces.
            locals, xnlp__bxljo, flags, None)
        kcwuu__iwfyr = dcygp__wqkog.dispatcher.get_call_template
        hffnf__slqc, zhtc__rrla, nkqrd__qunsj, kws = kcwuu__iwfyr(lbnof__uuvpk,
            kws)
        if nkqrd__qunsj in self._inline_overloads:
            return self._inline_overloads[nkqrd__qunsj]['iinfo'].signature
        ir = llr__utfhm.run_untyped_passes(dcygp__wqkog.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, mymi__uzpti, ir, nkqrd__qunsj, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, nkqrd__qunsj, None)
        self._inline_overloads[sig.args] = {'folded_args': nkqrd__qunsj}
        sox__lojm = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = sox__lojm
        if not self._inline.is_always_inline:
            sig = dcygp__wqkog.get_call_type(self.context, lbnof__uuvpk, kws)
            self._compiled_overloads[sig.args] = dcygp__wqkog.get_overload(sig)
        adral__ftne = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': nkqrd__qunsj,
            'iinfo': adral__ftne}
    else:
        sig = dcygp__wqkog.get_call_type(self.context, lbnof__uuvpk, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = dcygp__wqkog.get_overload(sig)
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
    amsh__mtr = [True, False]
    wwdn__rzso = [False, True]
    tdf__rfrbf = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    psy__fkn = get_local_target(context)
    zukcf__xesx = utils.order_by_target_specificity(psy__fkn, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for klkys__fozj in zukcf__xesx:
        ctn__lrjst = klkys__fozj(context)
        uzht__psef = amsh__mtr if ctn__lrjst.prefer_literal else wwdn__rzso
        uzht__psef = [True] if getattr(ctn__lrjst, '_no_unliteral', False
            ) else uzht__psef
        for xbag__zive in uzht__psef:
            try:
                if xbag__zive:
                    sig = ctn__lrjst.apply(args, kws)
                else:
                    bhxtv__tlo = tuple([_unlit_non_poison(a) for a in args])
                    dbf__xrh = {ggzs__uxhx: _unlit_non_poison(jdoou__ygka) for
                        ggzs__uxhx, jdoou__ygka in kws.items()}
                    sig = ctn__lrjst.apply(bhxtv__tlo, dbf__xrh)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    tdf__rfrbf.add_error(ctn__lrjst, False, e, xbag__zive)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = ctn__lrjst.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    qphaf__ifxi = getattr(ctn__lrjst, 'cases', None)
                    if qphaf__ifxi is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            qphaf__ifxi)
                    else:
                        msg = 'No match.'
                    tdf__rfrbf.add_error(ctn__lrjst, True, msg, xbag__zive)
    tdf__rfrbf.raise_error()


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
    hffnf__slqc = self.template(context)
    sxf__rap = None
    eid__xssu = None
    tta__dfcx = None
    uzht__psef = [True, False] if hffnf__slqc.prefer_literal else [False, True]
    uzht__psef = [True] if getattr(hffnf__slqc, '_no_unliteral', False
        ) else uzht__psef
    for xbag__zive in uzht__psef:
        if xbag__zive:
            try:
                tta__dfcx = hffnf__slqc.apply(args, kws)
            except Exception as dzzgr__wuv:
                if isinstance(dzzgr__wuv, errors.ForceLiteralArg):
                    raise dzzgr__wuv
                sxf__rap = dzzgr__wuv
                tta__dfcx = None
            else:
                break
        else:
            cef__dfods = tuple([_unlit_non_poison(a) for a in args])
            ewsd__rvkn = {ggzs__uxhx: _unlit_non_poison(jdoou__ygka) for 
                ggzs__uxhx, jdoou__ygka in kws.items()}
            nzg__evxq = cef__dfods == args and kws == ewsd__rvkn
            if not nzg__evxq and tta__dfcx is None:
                try:
                    tta__dfcx = hffnf__slqc.apply(cef__dfods, ewsd__rvkn)
                except Exception as dzzgr__wuv:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        dzzgr__wuv, errors.NumbaError):
                        raise dzzgr__wuv
                    if isinstance(dzzgr__wuv, errors.ForceLiteralArg):
                        if hffnf__slqc.prefer_literal:
                            raise dzzgr__wuv
                    eid__xssu = dzzgr__wuv
                else:
                    break
    if tta__dfcx is None and (eid__xssu is not None or sxf__rap is not None):
        xbz__cmg = '- Resolution failure for {} arguments:\n{}\n'
        dqnl__wuz = _termcolor.highlight(xbz__cmg)
        if numba.core.config.DEVELOPER_MODE:
            txor__iyzzc = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    tdk__hit = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    tdk__hit = ['']
                dwi__ohfy = '\n{}'.format(2 * txor__iyzzc)
                hsuyn__bcc = _termcolor.reset(dwi__ohfy + dwi__ohfy.join(
                    _bt_as_lines(tdk__hit)))
                return _termcolor.reset(hsuyn__bcc)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            ona__txx = str(e)
            ona__txx = ona__txx if ona__txx else str(repr(e)) + add_bt(e)
            flkqd__xfb = errors.TypingError(textwrap.dedent(ona__txx))
            return dqnl__wuz.format(literalness, str(flkqd__xfb))
        import bodo
        if isinstance(sxf__rap, bodo.utils.typing.BodoError):
            raise sxf__rap
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', sxf__rap) +
                nested_msg('non-literal', eid__xssu))
        else:
            msg = 'Compilation error for '
            if isinstance(self.this, bodo.hiframes.pd_dataframe_ext.
                DataFrameType):
                msg += 'DataFrame.'
            elif isinstance(self.this, bodo.hiframes.pd_series_ext.SeriesType):
                msg += 'Series.'
            msg += f'{self.typing_key[1]}().{bodo_typing_error_info}'
            raise errors.TypingError(msg)
    return tta__dfcx


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
    sso__wzlpw = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=sso__wzlpw)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            edjtk__xmh = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), edjtk__xmh)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    wnfw__yhkc = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            wnfw__yhkc.append(types.Omitted(a.value))
        else:
            wnfw__yhkc.append(self.typeof_pyval(a))
    ypd__ijna = None
    try:
        error = None
        ypd__ijna = self.compile(tuple(wnfw__yhkc))
    except errors.ForceLiteralArg as e:
        engmh__crq = [wazte__koyyv for wazte__koyyv in e.requested_args if 
            isinstance(args[wazte__koyyv], types.Literal) and not
            isinstance(args[wazte__koyyv], types.LiteralStrKeyDict)]
        if engmh__crq:
            dynl__cnuwb = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            yjf__ynkk = ', '.join('Arg #{} is {}'.format(wazte__koyyv, args
                [wazte__koyyv]) for wazte__koyyv in sorted(engmh__crq))
            raise errors.CompilerError(dynl__cnuwb.format(yjf__ynkk))
        lbnof__uuvpk = []
        try:
            for wazte__koyyv, jdoou__ygka in enumerate(args):
                if wazte__koyyv in e.requested_args:
                    if wazte__koyyv in e.file_infos:
                        lbnof__uuvpk.append(types.FilenameType(args[
                            wazte__koyyv], e.file_infos[wazte__koyyv]))
                    else:
                        lbnof__uuvpk.append(types.literal(args[wazte__koyyv]))
                else:
                    lbnof__uuvpk.append(args[wazte__koyyv])
            args = lbnof__uuvpk
        except (OSError, FileNotFoundError) as zrpsk__rnmu:
            error = FileNotFoundError(str(zrpsk__rnmu) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                ypd__ijna = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        fmle__osnmt = []
        for wazte__koyyv, orns__srs in enumerate(args):
            val = orns__srs.value if isinstance(orns__srs, numba.core.
                dispatcher.OmittedArg) else orns__srs
            try:
                hxf__epjgb = typeof(val, Purpose.argument)
            except ValueError as gcu__jlzy:
                fmle__osnmt.append((wazte__koyyv, str(gcu__jlzy)))
            else:
                if hxf__epjgb is None:
                    fmle__osnmt.append((wazte__koyyv,
                        f'cannot determine Numba type of value {val}'))
        if fmle__osnmt:
            iln__wlnjf = '\n'.join(
                f'- argument {wazte__koyyv}: {sywx__vco}' for wazte__koyyv,
                sywx__vco in fmle__osnmt)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{iln__wlnjf}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                murco__cxs = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'numba', 'Overload',
                    'lowering']
                jyiq__uhms = False
                for nee__rxxq in murco__cxs:
                    if nee__rxxq in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        jyiq__uhms = True
                        break
                if not jyiq__uhms:
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
                edjtk__xmh = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), edjtk__xmh)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return ypd__ijna


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
    for jezjs__dyeoc in cres.library._codegen._engine._defined_symbols:
        if jezjs__dyeoc.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in jezjs__dyeoc and (
            'bodo_gb_udf_update_local' in jezjs__dyeoc or 
            'bodo_gb_udf_combine' in jezjs__dyeoc or 'bodo_gb_udf_eval' in
            jezjs__dyeoc or 'bodo_gb_apply_general_udfs' in jezjs__dyeoc):
            gb_agg_cfunc_addr[jezjs__dyeoc
                ] = cres.library.get_pointer_to_function(jezjs__dyeoc)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for jezjs__dyeoc in cres.library._codegen._engine._defined_symbols:
        if jezjs__dyeoc.startswith('cfunc') and ('get_join_cond_addr' not in
            jezjs__dyeoc or 'bodo_join_gen_cond' in jezjs__dyeoc):
            join_gen_cond_cfunc_addr[jezjs__dyeoc
                ] = cres.library.get_pointer_to_function(jezjs__dyeoc)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    nkuf__ksced = self._get_dispatcher_for_current_target()
    if nkuf__ksced is not self:
        return nkuf__ksced.compile(sig)
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
            odw__wsu = self.overloads.get(tuple(args))
            if odw__wsu is not None:
                return odw__wsu.entry_point
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
            ven__veya = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=ven__veya):
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
    hjuvn__fluc = self._final_module
    acvc__ewyfi = []
    vrext__kkhh = 0
    for fn in hjuvn__fluc.functions:
        vrext__kkhh += 1
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
            acvc__ewyfi.append(fn.name)
    if vrext__kkhh == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if acvc__ewyfi:
        hjuvn__fluc = hjuvn__fluc.clone()
        for name in acvc__ewyfi:
            hjuvn__fluc.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = hjuvn__fluc
    return hjuvn__fluc


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
    for ffx__dbfhk in self.constraints:
        loc = ffx__dbfhk.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                ffx__dbfhk(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                drh__qmc = numba.core.errors.TypingError(str(e), loc=
                    ffx__dbfhk.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(drh__qmc, e))
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
                    drh__qmc = numba.core.errors.TypingError(msg.format(con
                        =ffx__dbfhk, err=str(e)), loc=ffx__dbfhk.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(drh__qmc, e))
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
    for boxi__tjstg in self._failures.values():
        for ydwes__rshg in boxi__tjstg:
            if isinstance(ydwes__rshg.error, ForceLiteralArg):
                raise ydwes__rshg.error
            if isinstance(ydwes__rshg.error, bodo.utils.typing.BodoError):
                raise ydwes__rshg.error
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
    sbvrm__gjbqd = False
    reue__xjcw = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        gusuw__jor = set()
        uiz__onqp = lives & alias_set
        for jdoou__ygka in uiz__onqp:
            gusuw__jor |= alias_map[jdoou__ygka]
        lives_n_aliases = lives | gusuw__jor | arg_aliases
        if type(stmt) in remove_dead_extensions:
            vzs__bwzgi = remove_dead_extensions[type(stmt)]
            stmt = vzs__bwzgi(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                sbvrm__gjbqd = True
                continue
        if isinstance(stmt, ir.Assign):
            ljby__qgim = stmt.target
            nkey__ayg = stmt.value
            if ljby__qgim.name not in lives and has_no_side_effect(nkey__ayg,
                lives_n_aliases, call_table):
                sbvrm__gjbqd = True
                continue
            if saved_array_analysis and ljby__qgim.name in lives and is_expr(
                nkey__ayg, 'getattr'
                ) and nkey__ayg.attr == 'shape' and is_array_typ(typemap[
                nkey__ayg.value.name]) and nkey__ayg.value.name not in lives:
                mpuxm__tnkyj = {jdoou__ygka: ggzs__uxhx for ggzs__uxhx,
                    jdoou__ygka in func_ir.blocks.items()}
                if block in mpuxm__tnkyj:
                    icg__ahc = mpuxm__tnkyj[block]
                    wli__nvt = saved_array_analysis.get_equiv_set(icg__ahc)
                    zokee__wph = wli__nvt.get_equiv_set(nkey__ayg.value)
                    if zokee__wph is not None:
                        for jdoou__ygka in zokee__wph:
                            if jdoou__ygka.endswith('#0'):
                                jdoou__ygka = jdoou__ygka[:-2]
                            if jdoou__ygka in typemap and is_array_typ(typemap
                                [jdoou__ygka]) and jdoou__ygka in lives:
                                nkey__ayg.value = ir.Var(nkey__ayg.value.
                                    scope, jdoou__ygka, nkey__ayg.value.loc)
                                sbvrm__gjbqd = True
                                break
            if isinstance(nkey__ayg, ir.Var
                ) and ljby__qgim.name == nkey__ayg.name:
                sbvrm__gjbqd = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                sbvrm__gjbqd = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            bqm__npxt = analysis.ir_extension_usedefs[type(stmt)]
            rtw__bgnhb, nsrsw__qdgt = bqm__npxt(stmt)
            lives -= nsrsw__qdgt
            lives |= rtw__bgnhb
        else:
            lives |= {jdoou__ygka.name for jdoou__ygka in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                zsvc__fbpue = set()
                if isinstance(nkey__ayg, ir.Expr):
                    zsvc__fbpue = {jdoou__ygka.name for jdoou__ygka in
                        nkey__ayg.list_vars()}
                if ljby__qgim.name not in zsvc__fbpue:
                    lives.remove(ljby__qgim.name)
        reue__xjcw.append(stmt)
    reue__xjcw.reverse()
    block.body = reue__xjcw
    return sbvrm__gjbqd


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            mzb__olc, = args
            if isinstance(mzb__olc, types.IterableType):
                dtype = mzb__olc.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), mzb__olc)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    jip__ouqx = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (jip__ouqx, self.dtype)
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
        except LiteralTypingError as rzky__xln:
            return
    try:
        return literal(value)
    except LiteralTypingError as rzky__xln:
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
        rkh__xzz = py_func.__qualname__
    except AttributeError as rzky__xln:
        rkh__xzz = py_func.__name__
    dostv__iov = inspect.getfile(py_func)
    for cls in self._locator_classes:
        zag__flyxh = cls.from_function(py_func, dostv__iov)
        if zag__flyxh is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (rkh__xzz, dostv__iov))
    self._locator = zag__flyxh
    hidb__zckhl = inspect.getfile(py_func)
    comm__igy = os.path.splitext(os.path.basename(hidb__zckhl))[0]
    if dostv__iov.startswith('<ipython-'):
        mzvs__uankl = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', comm__igy, count=1)
        if mzvs__uankl == comm__igy:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        comm__igy = mzvs__uankl
    qequf__wgb = '%s.%s' % (comm__igy, rkh__xzz)
    spqu__wbqao = getattr(sys, 'abiflags', '')
    self._filename_base = self.get_filename_base(qequf__wgb, spqu__wbqao)


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    wvizd__kwh = list(filter(lambda a: self._istuple(a.name), args))
    if len(wvizd__kwh) == 2 and fn.__name__ == 'add':
        omu__rnyt = self.typemap[wvizd__kwh[0].name]
        tzjcx__hmh = self.typemap[wvizd__kwh[1].name]
        if omu__rnyt.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                wvizd__kwh[1]))
        if tzjcx__hmh.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                wvizd__kwh[0]))
        try:
            ncmy__hym = [equiv_set.get_shape(x) for x in wvizd__kwh]
            if None in ncmy__hym:
                return None
            oxrx__uti = sum(ncmy__hym, ())
            return ArrayAnalysis.AnalyzeResult(shape=oxrx__uti)
        except GuardException as rzky__xln:
            return None
    gmz__fppqs = list(filter(lambda a: self._isarray(a.name), args))
    require(len(gmz__fppqs) > 0)
    czhc__pmncb = [x.name for x in gmz__fppqs]
    qyp__ktxw = [self.typemap[x.name].ndim for x in gmz__fppqs]
    yujn__ulont = max(qyp__ktxw)
    require(yujn__ulont > 0)
    ncmy__hym = [equiv_set.get_shape(x) for x in gmz__fppqs]
    if any(a is None for a in ncmy__hym):
        return ArrayAnalysis.AnalyzeResult(shape=gmz__fppqs[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, gmz__fppqs))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, ncmy__hym,
        czhc__pmncb)


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
    jhz__mymf = code_obj.code
    momh__tsaap = len(jhz__mymf.co_freevars)
    deqa__kmmwu = jhz__mymf.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        tjxhd__xjfto, op = ir_utils.find_build_sequence(caller_ir, code_obj
            .closure)
        assert op == 'build_tuple'
        deqa__kmmwu = [jdoou__ygka.name for jdoou__ygka in tjxhd__xjfto]
    thwm__lbj = caller_ir.func_id.func.__globals__
    try:
        thwm__lbj = getattr(code_obj, 'globals', thwm__lbj)
    except KeyError as rzky__xln:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/udfs.html"
        )
    orm__hojpz = []
    for x in deqa__kmmwu:
        try:
            dgs__taq = caller_ir.get_definition(x)
        except KeyError as rzky__xln:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(dgs__taq, (ir.Const, ir.Global, ir.FreeVar)):
            val = dgs__taq.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                wdpx__eiphn = ir_utils.mk_unique_var('nested_func').replace('.'
                    , '_')
                thwm__lbj[wdpx__eiphn] = bodo.jit(distributed=False)(val)
                thwm__lbj[wdpx__eiphn].is_nested_func = True
                val = wdpx__eiphn
            if isinstance(val, CPUDispatcher):
                wdpx__eiphn = ir_utils.mk_unique_var('nested_func').replace('.'
                    , '_')
                thwm__lbj[wdpx__eiphn] = val
                val = wdpx__eiphn
            orm__hojpz.append(val)
        elif isinstance(dgs__taq, ir.Expr) and dgs__taq.op == 'make_function':
            jkbqu__jotn = convert_code_obj_to_function(dgs__taq, caller_ir)
            wdpx__eiphn = ir_utils.mk_unique_var('nested_func').replace('.',
                '_')
            thwm__lbj[wdpx__eiphn] = bodo.jit(distributed=False)(jkbqu__jotn)
            thwm__lbj[wdpx__eiphn].is_nested_func = True
            orm__hojpz.append(wdpx__eiphn)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    itsf__pjv = '\n'.join([('\tc_%d = %s' % (wazte__koyyv, x)) for 
        wazte__koyyv, x in enumerate(orm__hojpz)])
    dcz__aqpih = ','.join([('c_%d' % wazte__koyyv) for wazte__koyyv in
        range(momh__tsaap)])
    nmv__azxk = list(jhz__mymf.co_varnames)
    dyj__jhier = 0
    qyd__tbnwq = jhz__mymf.co_argcount
    lzmvp__eiwz = caller_ir.get_definition(code_obj.defaults)
    if lzmvp__eiwz is not None:
        if isinstance(lzmvp__eiwz, tuple):
            win__scgy = [caller_ir.get_definition(x).value for x in lzmvp__eiwz
                ]
            ugwq__gbk = tuple(win__scgy)
        else:
            win__scgy = [caller_ir.get_definition(x).value for x in
                lzmvp__eiwz.items]
            ugwq__gbk = tuple(win__scgy)
        dyj__jhier = len(ugwq__gbk)
    chkmq__wna = qyd__tbnwq - dyj__jhier
    irht__hbbk = ','.join([('%s' % nmv__azxk[wazte__koyyv]) for
        wazte__koyyv in range(chkmq__wna)])
    if dyj__jhier:
        lqjrf__qdbl = [('%s = %s' % (nmv__azxk[wazte__koyyv + chkmq__wna],
            ugwq__gbk[wazte__koyyv])) for wazte__koyyv in range(dyj__jhier)]
        irht__hbbk += ', '
        irht__hbbk += ', '.join(lqjrf__qdbl)
    return _create_function_from_code_obj(jhz__mymf, itsf__pjv, irht__hbbk,
        dcz__aqpih, thwm__lbj)


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
    for zcz__fxulq, (eikol__xdzw, gcxwf__ldp) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % gcxwf__ldp)
            jrn__cjce = _pass_registry.get(eikol__xdzw).pass_inst
            if isinstance(jrn__cjce, CompilerPass):
                self._runPass(zcz__fxulq, jrn__cjce, state)
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
                    pipeline_name, gcxwf__ldp)
                rzi__pwfre = self._patch_error(msg, e)
                raise rzi__pwfre
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
    qgts__wcy = None
    nsrsw__qdgt = {}

    def lookup(var, already_seen, varonly=True):
        val = nsrsw__qdgt.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    beia__eja = reduction_node.unversioned_name
    for wazte__koyyv, stmt in enumerate(nodes):
        ljby__qgim = stmt.target
        nkey__ayg = stmt.value
        nsrsw__qdgt[ljby__qgim.name] = nkey__ayg
        if isinstance(nkey__ayg, ir.Var) and nkey__ayg.name in nsrsw__qdgt:
            nkey__ayg = lookup(nkey__ayg, set())
        if isinstance(nkey__ayg, ir.Expr):
            gbqt__onq = set(lookup(jdoou__ygka, set(), True).name for
                jdoou__ygka in nkey__ayg.list_vars())
            if name in gbqt__onq:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(nkey__ayg)]
                peog__vns = [x for x, hfw__ibjh in args if hfw__ibjh.name !=
                    name]
                args = [(x, hfw__ibjh) for x, hfw__ibjh in args if x !=
                    hfw__ibjh.name]
                gkbue__udgm = dict(args)
                if len(peog__vns) == 1:
                    gkbue__udgm[peog__vns[0]] = ir.Var(ljby__qgim.scope, 
                        name + '#init', ljby__qgim.loc)
                replace_vars_inner(nkey__ayg, gkbue__udgm)
                qgts__wcy = nodes[wazte__koyyv:]
                break
    return qgts__wcy


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
        evat__hfsj = expand_aliases({jdoou__ygka.name for jdoou__ygka in
            stmt.list_vars()}, alias_map, arg_aliases)
        xcrbj__gdjt = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        opml__qekx = expand_aliases({jdoou__ygka.name for jdoou__ygka in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        ztzqp__ftpkv = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(xcrbj__gdjt & opml__qekx | ztzqp__ftpkv & evat__hfsj) == 0:
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
    rex__tbwqd = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            rex__tbwqd.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                rex__tbwqd.update(get_parfor_writes(stmt, func_ir))
    return rex__tbwqd


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    rex__tbwqd = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        rex__tbwqd.add(stmt.target.name)
    if isinstance(stmt, bodo.ir.aggregate.Aggregate):
        rex__tbwqd = {jdoou__ygka.name for jdoou__ygka in stmt.df_out_vars.
            values()}
        if stmt.out_key_vars is not None:
            rex__tbwqd.update({jdoou__ygka.name for jdoou__ygka in stmt.
                out_key_vars})
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        rex__tbwqd = {jdoou__ygka.name for jdoou__ygka in stmt.out_vars}
    if isinstance(stmt, bodo.ir.join.Join):
        rex__tbwqd = {jdoou__ygka.name for jdoou__ygka in stmt.
            out_data_vars.values()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            rex__tbwqd.update({jdoou__ygka.name for jdoou__ygka in stmt.
                out_key_arrs})
            rex__tbwqd.update({jdoou__ygka.name for jdoou__ygka in stmt.
                df_out_vars.values()})
    if is_call_assign(stmt):
        qhue__kpp = guard(find_callname, func_ir, stmt.value)
        if qhue__kpp in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            rex__tbwqd.add(stmt.value.args[0].name)
    return rex__tbwqd


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
        vzs__bwzgi = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        xdeal__qsl = vzs__bwzgi.format(self, msg)
        self.args = xdeal__qsl,
    else:
        vzs__bwzgi = _termcolor.errmsg('{0}')
        xdeal__qsl = vzs__bwzgi.format(self)
        self.args = xdeal__qsl,
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
        for tvqeb__mkhh in options['distributed']:
            dist_spec[tvqeb__mkhh] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for tvqeb__mkhh in options['distributed_block']:
            dist_spec[tvqeb__mkhh] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    yuhp__vien = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, xby__ocwrl in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(xby__ocwrl)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    nob__xxwu = {}
    for vaeji__nss in reversed(inspect.getmro(cls)):
        nob__xxwu.update(vaeji__nss.__dict__)
    xzuk__nhhy, eir__nepi, ylqcj__qtg, fju__bzyrj = {}, {}, {}, {}
    for ggzs__uxhx, jdoou__ygka in nob__xxwu.items():
        if isinstance(jdoou__ygka, pytypes.FunctionType):
            xzuk__nhhy[ggzs__uxhx] = jdoou__ygka
        elif isinstance(jdoou__ygka, property):
            eir__nepi[ggzs__uxhx] = jdoou__ygka
        elif isinstance(jdoou__ygka, staticmethod):
            ylqcj__qtg[ggzs__uxhx] = jdoou__ygka
        else:
            fju__bzyrj[ggzs__uxhx] = jdoou__ygka
    pkc__ikle = (set(xzuk__nhhy) | set(eir__nepi) | set(ylqcj__qtg)) & set(spec
        )
    if pkc__ikle:
        raise NameError('name shadowing: {0}'.format(', '.join(pkc__ikle)))
    gemr__cfmq = fju__bzyrj.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(fju__bzyrj)
    if fju__bzyrj:
        msg = 'class members are not yet supported: {0}'
        nfv__gbo = ', '.join(fju__bzyrj.keys())
        raise TypeError(msg.format(nfv__gbo))
    for ggzs__uxhx, jdoou__ygka in eir__nepi.items():
        if jdoou__ygka.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(ggzs__uxhx))
    jit_methods = {ggzs__uxhx: bodo.jit(returns_maybe_distributed=
        yuhp__vien)(jdoou__ygka) for ggzs__uxhx, jdoou__ygka in xzuk__nhhy.
        items()}
    jit_props = {}
    for ggzs__uxhx, jdoou__ygka in eir__nepi.items():
        mfc__itjt = {}
        if jdoou__ygka.fget:
            mfc__itjt['get'] = bodo.jit(jdoou__ygka.fget)
        if jdoou__ygka.fset:
            mfc__itjt['set'] = bodo.jit(jdoou__ygka.fset)
        jit_props[ggzs__uxhx] = mfc__itjt
    jit_static_methods = {ggzs__uxhx: bodo.jit(jdoou__ygka.__func__) for 
        ggzs__uxhx, jdoou__ygka in ylqcj__qtg.items()}
    okja__wclku = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    djg__lxd = dict(class_type=okja__wclku, __doc__=gemr__cfmq)
    djg__lxd.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), djg__lxd)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, okja__wclku)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(okja__wclku, typingctx, targetctx).register()
    as_numba_type.register(cls, okja__wclku.instance_type)
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
    mkea__wen = ','.join('{0}:{1}'.format(ggzs__uxhx, jdoou__ygka) for 
        ggzs__uxhx, jdoou__ygka in struct.items())
    yzp__hsh = ','.join('{0}:{1}'.format(ggzs__uxhx, jdoou__ygka) for 
        ggzs__uxhx, jdoou__ygka in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), mkea__wen, yzp__hsh)
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
    agu__kuq = numba.core.typeinfer.fold_arg_vars(typevars, self.args, self
        .vararg, self.kws)
    if agu__kuq is None:
        return
    kwf__ihg, qykk__pimeh = agu__kuq
    for a in itertools.chain(kwf__ihg, qykk__pimeh.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, kwf__ihg, qykk__pimeh)
    except ForceLiteralArg as e:
        zqbd__vcr = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(zqbd__vcr, self.kws)
        cike__nuuyb = set()
        xdqoy__qxuxb = set()
        neftj__biih = {}
        for zcz__fxulq in e.requested_args:
            jhjg__wszxa = typeinfer.func_ir.get_definition(folded[zcz__fxulq])
            if isinstance(jhjg__wszxa, ir.Arg):
                cike__nuuyb.add(jhjg__wszxa.index)
                if jhjg__wszxa.index in e.file_infos:
                    neftj__biih[jhjg__wszxa.index] = e.file_infos[jhjg__wszxa
                        .index]
            else:
                xdqoy__qxuxb.add(zcz__fxulq)
        if xdqoy__qxuxb:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif cike__nuuyb:
            raise ForceLiteralArg(cike__nuuyb, loc=self.loc, file_infos=
                neftj__biih)
    if sig is None:
        dazuz__cmrxl = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in kwf__ihg]
        args += [('%s=%s' % (ggzs__uxhx, jdoou__ygka)) for ggzs__uxhx,
            jdoou__ygka in sorted(qykk__pimeh.items())]
        uiniu__gpy = dazuz__cmrxl.format(fnty, ', '.join(map(str, args)))
        sao__mnf = context.explain_function_type(fnty)
        msg = '\n'.join([uiniu__gpy, sao__mnf])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        cbalx__ptwdw = context.unify_pairs(sig.recvr, fnty.this)
        if cbalx__ptwdw is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if cbalx__ptwdw is not None and cbalx__ptwdw.is_precise():
            ofl__rwzz = fnty.copy(this=cbalx__ptwdw)
            typeinfer.propagate_refined_type(self.func, ofl__rwzz)
    if not sig.return_type.is_precise():
        gvpfx__xcy = typevars[self.target]
        if gvpfx__xcy.defined:
            piuiw__wwhvi = gvpfx__xcy.getone()
            if context.unify_pairs(piuiw__wwhvi, sig.return_type
                ) == piuiw__wwhvi:
                sig = sig.replace(return_type=piuiw__wwhvi)
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
        dynl__cnuwb = '*other* must be a {} but got a {} instead'
        raise TypeError(dynl__cnuwb.format(ForceLiteralArg, type(other)))
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
    yuhg__dli = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for ggzs__uxhx, jdoou__ygka in kwargs.items():
        gigle__abbgm = None
        try:
            wktcp__rgda = ir.Var(ir.Scope(None, loc), ir_utils.
                mk_unique_var('dummy'), loc)
            func_ir._definitions[wktcp__rgda.name] = [jdoou__ygka]
            gigle__abbgm = get_const_value_inner(func_ir, wktcp__rgda)
            func_ir._definitions.pop(wktcp__rgda.name)
            if isinstance(gigle__abbgm, str):
                gigle__abbgm = sigutils._parse_signature_string(gigle__abbgm)
            if isinstance(gigle__abbgm, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {ggzs__uxhx} is annotated as type class {gigle__abbgm}."""
                    )
            assert isinstance(gigle__abbgm, types.Type)
            if isinstance(gigle__abbgm, (types.List, types.Set)):
                gigle__abbgm = gigle__abbgm.copy(reflected=False)
            yuhg__dli[ggzs__uxhx] = gigle__abbgm
        except BodoError as rzky__xln:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(gigle__abbgm, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(jdoou__ygka, ir.Global):
                    msg = f'Global {jdoou__ygka.name!r} is not defined.'
                if isinstance(jdoou__ygka, ir.FreeVar):
                    msg = f'Freevar {jdoou__ygka.name!r} is not defined.'
            if isinstance(jdoou__ygka, ir.Expr
                ) and jdoou__ygka.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=ggzs__uxhx, msg=msg, loc=loc)
    for name, typ in yuhg__dli.items():
        self._legalize_arg_type(name, typ, loc)
    return yuhg__dli


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
    eifuv__zytlt = inst.arg
    assert eifuv__zytlt > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(eifuv__zytlt)]))
    tmps = [state.make_temp() for _ in range(eifuv__zytlt - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    tef__vqzwl = ir.Global('format', format, loc=self.loc)
    self.store(value=tef__vqzwl, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    kjztu__ihxc = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=kjztu__ihxc, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    eifuv__zytlt = inst.arg
    assert eifuv__zytlt > 0, 'invalid BUILD_STRING count'
    kvj__quz = self.get(strings[0])
    for other, tffko__pyr in zip(strings[1:], tmps):
        other = self.get(other)
        cix__amnh = ir.Expr.binop(operator.add, lhs=kvj__quz, rhs=other,
            loc=self.loc)
        self.store(cix__amnh, tffko__pyr)
        kvj__quz = self.get(tffko__pyr)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite.llvmpy.core import Type
    fhi__pyn = self.context.insert_const_string(self.module, attr)
    fnty = Type.function(Type.int(), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, fhi__pyn])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    wsc__fdw = mk_unique_var(f'{var_name}')
    dwuo__tnixw = wsc__fdw.replace('<', '_').replace('>', '_')
    dwuo__tnixw = dwuo__tnixw.replace('.', '_').replace('$', '_v')
    return dwuo__tnixw


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
        dtgtj__qae = states['defmap']
        if len(dtgtj__qae) == 0:
            ldmtg__xogl = assign.target
            numba.core.ssa._logger.debug('first assign: %s', ldmtg__xogl)
            if ldmtg__xogl.name not in scope.localvars:
                ldmtg__xogl = scope.define(assign.target.name, loc=assign.loc)
        else:
            ldmtg__xogl = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=ldmtg__xogl, value=assign.value, loc=
            assign.loc)
        dtgtj__qae[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    crx__azs = []
    for ggzs__uxhx, jdoou__ygka in typing.npydecl.registry.globals:
        if ggzs__uxhx == func:
            crx__azs.append(jdoou__ygka)
    for ggzs__uxhx, jdoou__ygka in typing.templates.builtin_registry.globals:
        if ggzs__uxhx == func:
            crx__azs.append(jdoou__ygka)
    if len(crx__azs) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return crx__azs


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    jwwgn__isio = {}
    nbay__bppyq = find_topo_order(blocks)
    mxk__uudaw = {}
    for icg__ahc in nbay__bppyq:
        block = blocks[icg__ahc]
        reue__xjcw = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                ljby__qgim = stmt.target.name
                nkey__ayg = stmt.value
                if (nkey__ayg.op == 'getattr' and nkey__ayg.attr in
                    arr_math and isinstance(typemap[nkey__ayg.value.name],
                    types.npytypes.Array)):
                    nkey__ayg = stmt.value
                    qjwra__cvyry = nkey__ayg.value
                    jwwgn__isio[ljby__qgim] = qjwra__cvyry
                    scope = qjwra__cvyry.scope
                    loc = qjwra__cvyry.loc
                    vbfm__imzj = ir.Var(scope, mk_unique_var('$np_g_var'), loc)
                    typemap[vbfm__imzj.name] = types.misc.Module(numpy)
                    ennpu__mplz = ir.Global('np', numpy, loc)
                    ldt__ujvs = ir.Assign(ennpu__mplz, vbfm__imzj, loc)
                    nkey__ayg.value = vbfm__imzj
                    reue__xjcw.append(ldt__ujvs)
                    func_ir._definitions[vbfm__imzj.name] = [ennpu__mplz]
                    func = getattr(numpy, nkey__ayg.attr)
                    gertu__gak = get_np_ufunc_typ_lst(func)
                    mxk__uudaw[ljby__qgim] = gertu__gak
                if (nkey__ayg.op == 'call' and nkey__ayg.func.name in
                    jwwgn__isio):
                    qjwra__cvyry = jwwgn__isio[nkey__ayg.func.name]
                    lysii__flcfh = calltypes.pop(nkey__ayg)
                    hbu__dnm = lysii__flcfh.args[:len(nkey__ayg.args)]
                    jrqq__zgtsj = {name: typemap[jdoou__ygka.name] for name,
                        jdoou__ygka in nkey__ayg.kws}
                    veve__pypp = mxk__uudaw[nkey__ayg.func.name]
                    det__wkuz = None
                    for ijx__ysgyf in veve__pypp:
                        try:
                            det__wkuz = ijx__ysgyf.get_call_type(typingctx,
                                [typemap[qjwra__cvyry.name]] + list(
                                hbu__dnm), jrqq__zgtsj)
                            typemap.pop(nkey__ayg.func.name)
                            typemap[nkey__ayg.func.name] = ijx__ysgyf
                            calltypes[nkey__ayg] = det__wkuz
                            break
                        except Exception as rzky__xln:
                            pass
                    if det__wkuz is None:
                        raise TypeError(
                            f'No valid template found for {nkey__ayg.func.name}'
                            )
                    nkey__ayg.args = [qjwra__cvyry] + nkey__ayg.args
            reue__xjcw.append(stmt)
        block.body = reue__xjcw


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    xlccs__kyo = ufunc.nin
    sls__tuwa = ufunc.nout
    chkmq__wna = ufunc.nargs
    assert chkmq__wna == xlccs__kyo + sls__tuwa
    if len(args) < xlccs__kyo:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), xlccs__kyo)
            )
    if len(args) > chkmq__wna:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), chkmq__wna)
            )
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    aabj__hwkdd = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    vkiyf__pbt = max(aabj__hwkdd)
    rzjzw__hyvig = args[xlccs__kyo:]
    if not all(win__scgy == vkiyf__pbt for win__scgy in aabj__hwkdd[
        xlccs__kyo:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(cgeu__bns, types.ArrayCompatible) and not
        isinstance(cgeu__bns, types.Bytes) for cgeu__bns in rzjzw__hyvig):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(cgeu__bns.mutable for cgeu__bns in rzjzw__hyvig):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    hoern__sia = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    ush__qgu = None
    if vkiyf__pbt > 0 and len(rzjzw__hyvig) < ufunc.nout:
        ush__qgu = 'C'
        uqmn__gib = [(x.layout if isinstance(x, types.ArrayCompatible) and 
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in uqmn__gib and 'F' in uqmn__gib:
            ush__qgu = 'F'
    return hoern__sia, rzjzw__hyvig, vkiyf__pbt, ush__qgu


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
        cxtq__yliip = 'Dict.key_type cannot be of type {}'
        raise TypingError(cxtq__yliip.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        cxtq__yliip = 'Dict.value_type cannot be of type {}'
        raise TypingError(cxtq__yliip.format(valty))
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
    for wazte__koyyv, a in enumerate(args, start=1):
        if isinstance(a, types.Dispatcher):
            msg = (
                'Does not support function type inputs into with-context for arg {}'
                )
            raise errors.TypingError(msg.format(wazte__koyyv))


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.ObjModeLiftedWith.
        _legalize_arg_types)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4793f44ebc7da8843e8f298e08cd8a5428b4b84b89fd9d5c650273fdb8fee5ee':
        warnings.warn('ObjModeLiftedWith._legalize_arg_types has changed')
numba.core.dispatcher.ObjModeLiftedWith._legalize_arg_types = (
    _legalize_arg_types)


def _overload_template_get_impl(self, args, kws):
    bfxd__hbml = self.context, tuple(args), tuple(kws.items())
    try:
        ojzfb__htg, args = self._impl_cache[bfxd__hbml]
        return ojzfb__htg, args
    except KeyError as rzky__xln:
        pass
    ojzfb__htg, args = self._build_impl(bfxd__hbml, args, kws)
    return ojzfb__htg, args


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
        fiv__rxk = find_topo_order(parfor.loop_body)
    lfhk__oehbv = fiv__rxk[0]
    hdxo__aint = {}
    _update_parfor_get_setitems(parfor.loop_body[lfhk__oehbv].body, parfor.
        index_var, alias_map, hdxo__aint, lives_n_aliases)
    mznr__cgou = set(hdxo__aint.keys())
    for imqs__iywm in fiv__rxk:
        if imqs__iywm == lfhk__oehbv:
            continue
        for stmt in parfor.loop_body[imqs__iywm].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            rqd__lct = set(jdoou__ygka.name for jdoou__ygka in stmt.list_vars()
                )
            ngjnf__mru = rqd__lct & mznr__cgou
            for a in ngjnf__mru:
                hdxo__aint.pop(a, None)
    for imqs__iywm in fiv__rxk:
        if imqs__iywm == lfhk__oehbv:
            continue
        block = parfor.loop_body[imqs__iywm]
        xzyqg__vtggu = hdxo__aint.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            xzyqg__vtggu, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    zuubg__muk = max(blocks.keys())
    wla__ozhm, slfi__xctm = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    nhnai__tngvw = ir.Jump(wla__ozhm, ir.Loc('parfors_dummy', -1))
    blocks[zuubg__muk].body.append(nhnai__tngvw)
    hitp__gpy = compute_cfg_from_blocks(blocks)
    tsj__ufygd = compute_use_defs(blocks)
    esar__zkhl = compute_live_map(hitp__gpy, blocks, tsj__ufygd.usemap,
        tsj__ufygd.defmap)
    alias_set = set(alias_map.keys())
    for icg__ahc, block in blocks.items():
        reue__xjcw = []
        yya__hgpfo = {jdoou__ygka.name for jdoou__ygka in block.terminator.
            list_vars()}
        for lbeb__lqv, gsey__ydkv in hitp__gpy.successors(icg__ahc):
            yya__hgpfo |= esar__zkhl[lbeb__lqv]
        for stmt in reversed(block.body):
            gusuw__jor = yya__hgpfo & alias_set
            for jdoou__ygka in gusuw__jor:
                yya__hgpfo |= alias_map[jdoou__ygka]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in yya__hgpfo and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                qhue__kpp = guard(find_callname, func_ir, stmt.value)
                if qhue__kpp == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in yya__hgpfo and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            yya__hgpfo |= {jdoou__ygka.name for jdoou__ygka in stmt.list_vars()
                }
            reue__xjcw.append(stmt)
        reue__xjcw.reverse()
        block.body = reue__xjcw
    typemap.pop(slfi__xctm.name)
    blocks[zuubg__muk].body.pop()

    def trim_empty_parfor_branches(parfor):
        ooy__yxj = False
        blocks = parfor.loop_body.copy()
        for icg__ahc, block in blocks.items():
            if len(block.body):
                ftg__mlir = block.body[-1]
                if isinstance(ftg__mlir, ir.Branch):
                    if len(blocks[ftg__mlir.truebr].body) == 1 and len(blocks
                        [ftg__mlir.falsebr].body) == 1:
                        siwu__ahqo = blocks[ftg__mlir.truebr].body[0]
                        qad__qvca = blocks[ftg__mlir.falsebr].body[0]
                        if isinstance(siwu__ahqo, ir.Jump) and isinstance(
                            qad__qvca, ir.Jump
                            ) and siwu__ahqo.target == qad__qvca.target:
                            parfor.loop_body[icg__ahc].body[-1] = ir.Jump(
                                siwu__ahqo.target, ftg__mlir.loc)
                            ooy__yxj = True
                    elif len(blocks[ftg__mlir.truebr].body) == 1:
                        siwu__ahqo = blocks[ftg__mlir.truebr].body[0]
                        if isinstance(siwu__ahqo, ir.Jump
                            ) and siwu__ahqo.target == ftg__mlir.falsebr:
                            parfor.loop_body[icg__ahc].body[-1] = ir.Jump(
                                siwu__ahqo.target, ftg__mlir.loc)
                            ooy__yxj = True
                    elif len(blocks[ftg__mlir.falsebr].body) == 1:
                        qad__qvca = blocks[ftg__mlir.falsebr].body[0]
                        if isinstance(qad__qvca, ir.Jump
                            ) and qad__qvca.target == ftg__mlir.truebr:
                            parfor.loop_body[icg__ahc].body[-1] = ir.Jump(
                                qad__qvca.target, ftg__mlir.loc)
                            ooy__yxj = True
        return ooy__yxj
    ooy__yxj = True
    while ooy__yxj:
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
        ooy__yxj = trim_empty_parfor_branches(parfor)
    hpq__blf = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        hpq__blf &= len(block.body) == 0
    if hpq__blf:
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
    izuzc__kgu = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                izuzc__kgu += 1
                parfor = stmt
                ormp__imk = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = ormp__imk.scope
                loc = ir.Loc('parfors_dummy', -1)
                eir__ovuh = ir.Var(scope, mk_unique_var('$const'), loc)
                ormp__imk.body.append(ir.Assign(ir.Const(0, loc), eir__ovuh,
                    loc))
                ormp__imk.body.append(ir.Return(eir__ovuh, loc))
                hitp__gpy = compute_cfg_from_blocks(parfor.loop_body)
                for ighkn__eazr in hitp__gpy.dead_nodes():
                    del parfor.loop_body[ighkn__eazr]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                ormp__imk = parfor.loop_body[max(parfor.loop_body.keys())]
                ormp__imk.body.pop()
                ormp__imk.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return izuzc__kgu


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
            odw__wsu = self.overloads.get(tuple(args))
            if odw__wsu is not None:
                return odw__wsu.entry_point
            self._pre_compile(args, return_type, flags)
            vmrj__jvdjk = self.func_ir
            ven__veya = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=ven__veya):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=vmrj__jvdjk, args=
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
        afyj__gabws = copy.deepcopy(flags)
        afyj__gabws.no_rewrites = True

        def compile_local(the_ir, the_flags):
            jpml__bkhoa = pipeline_class(typingctx, targetctx, library,
                args, return_type, the_flags, locals)
            return jpml__bkhoa.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        lui__nyzyf = compile_local(func_ir, afyj__gabws)
        rbbf__kuojm = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    rbbf__kuojm = compile_local(func_ir, flags)
                except Exception as rzky__xln:
                    pass
        if rbbf__kuojm is not None:
            cres = rbbf__kuojm
        else:
            cres = lui__nyzyf
        return cres
    else:
        jpml__bkhoa = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return jpml__bkhoa.compile_ir(func_ir=func_ir, lifted=lifted,
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
    bhnrf__weu = self.get_data_type(typ.dtype)
    tjhh__eof = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        tjhh__eof):
        zisa__tad = ary.ctypes.data
        xoc__vaa = self.add_dynamic_addr(builder, zisa__tad, info=str(type(
            zisa__tad)))
        vbcm__swmr = self.add_dynamic_addr(builder, id(ary), info=str(type(
            ary)))
        self.global_arrays.append(ary)
    else:
        lqzm__vkq = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            lqzm__vkq = lqzm__vkq.view('int64')
        ptk__rxkn = Constant.array(Type.int(8), bytearray(lqzm__vkq.data))
        xoc__vaa = cgutils.global_constant(builder, '.const.array.data',
            ptk__rxkn)
        xoc__vaa.align = self.get_abi_alignment(bhnrf__weu)
        vbcm__swmr = None
    qtcn__knqxk = self.get_value_type(types.intp)
    qxi__utat = [self.get_constant(types.intp, tsc__ltlc) for tsc__ltlc in
        ary.shape]
    bkrva__jns = Constant.array(qtcn__knqxk, qxi__utat)
    cha__lkzz = [self.get_constant(types.intp, tsc__ltlc) for tsc__ltlc in
        ary.strides]
    suf__izfkm = Constant.array(qtcn__knqxk, cha__lkzz)
    ffe__esgxc = self.get_constant(types.intp, ary.dtype.itemsize)
    pdhhw__mkl = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        pdhhw__mkl, ffe__esgxc, xoc__vaa.bitcast(self.get_value_type(types.
        CPointer(typ.dtype))), bkrva__jns, suf__izfkm])


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
    aumf__itwzg = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    bdar__izdqb = lir.Function(module, aumf__itwzg, name='nrt_atomic_{0}'.
        format(op))
    [aitm__kvlbd] = bdar__izdqb.args
    zvpb__gwpne = bdar__izdqb.append_basic_block()
    builder = lir.IRBuilder(zvpb__gwpne)
    dyq__khhhf = lir.Constant(_word_type, 1)
    if False:
        kig__txv = builder.atomic_rmw(op, aitm__kvlbd, dyq__khhhf, ordering
            =ordering)
        res = getattr(builder, op)(kig__txv, dyq__khhhf)
        builder.ret(res)
    else:
        kig__txv = builder.load(aitm__kvlbd)
        ckn__olq = getattr(builder, op)(kig__txv, dyq__khhhf)
        ald__mwyei = builder.icmp_signed('!=', kig__txv, lir.Constant(
            kig__txv.type, -1))
        with cgutils.if_likely(builder, ald__mwyei):
            builder.store(ckn__olq, aitm__kvlbd)
        builder.ret(ckn__olq)
    return bdar__izdqb


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
        ekkw__qeki = state.targetctx.codegen()
        state.library = ekkw__qeki.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    ovx__bfauy = state.func_ir
    typemap = state.typemap
    wik__opex = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    rhs__wpvp = state.metadata
    ydf__hahio = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        htw__qeo = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            ovx__bfauy, typemap, wik__opex, calltypes, mangler=targetctx.
            mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            rjvpm__csdpo = lowering.Lower(targetctx, library, htw__qeo,
                ovx__bfauy, metadata=rhs__wpvp)
            rjvpm__csdpo.lower()
            if not flags.no_cpython_wrapper:
                rjvpm__csdpo.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(wik__opex, (types.Optional, types.Generator)
                        ):
                        pass
                    else:
                        rjvpm__csdpo.create_cfunc_wrapper()
            tca__cbb = rjvpm__csdpo.env
            uvzy__iwe = rjvpm__csdpo.call_helper
            del rjvpm__csdpo
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(htw__qeo, uvzy__iwe, cfunc=None, env
                =tca__cbb)
        else:
            dmfg__xhclp = targetctx.get_executable(library, htw__qeo, tca__cbb)
            targetctx.insert_user_function(dmfg__xhclp, htw__qeo, [library])
            state['cr'] = _LowerResult(htw__qeo, uvzy__iwe, cfunc=
                dmfg__xhclp, env=tca__cbb)
        rhs__wpvp['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        mqkm__zlrp = llvm.passmanagers.dump_refprune_stats()
        rhs__wpvp['prune_stats'] = mqkm__zlrp - ydf__hahio
        rhs__wpvp['llvm_pass_timings'] = library.recorded_timings
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
        skbih__uza = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, skbih__uza),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            loop.do_break()
        xwm__glbyb = c.builder.icmp_signed('!=', skbih__uza, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(xwm__glbyb, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, skbih__uza)
                c.pyapi.decref(skbih__uza)
                loop.do_break()
        c.pyapi.decref(skbih__uza)
    gnou__qojo, list = listobj.ListInstance.allocate_ex(c.context, c.
        builder, typ, size)
    with c.builder.if_else(gnou__qojo, likely=True) as (if_ok, if_not_ok):
        with if_ok:
            list.size = size
            zype__ikn = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                zype__ikn), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        zype__ikn))
                    with cgutils.for_range(c.builder, size) as loop:
                        itemobj = c.pyapi.list_getitem(obj, loop.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        ikg__nck = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(ikg__nck.is_error, likely=False
                            ):
                            c.builder.store(cgutils.true_bit, errorptr)
                            loop.do_break()
                        list.setitem(loop.index, ikg__nck.value, incref=False)
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
    xmg__kpjg, irvo__jyxy, bbt__wduzz, osaqv__ezof, uxv__pna = (
        compile_time_get_string_data(literal_string))
    hjuvn__fluc = builder.module
    gv = context.insert_const_bytes(hjuvn__fluc, xmg__kpjg)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        irvo__jyxy), context.get_constant(types.int32, bbt__wduzz), context
        .get_constant(types.uint32, osaqv__ezof), context.get_constant(
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
    udkj__fbur = None
    if isinstance(shape, types.Integer):
        udkj__fbur = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(tsc__ltlc, (types.Integer, types.IntEnumMember)) for
            tsc__ltlc in shape):
            udkj__fbur = len(shape)
    return udkj__fbur


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
            udkj__fbur = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if udkj__fbur == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, wazte__koyyv) for
                    wazte__koyyv in range(udkj__fbur))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            czhc__pmncb = self._get_names(x)
            if len(czhc__pmncb) != 0:
                return czhc__pmncb[0]
            return czhc__pmncb
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    czhc__pmncb = self._get_names(obj)
    if len(czhc__pmncb) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(czhc__pmncb[0])


def get_equiv_set(self, obj):
    czhc__pmncb = self._get_names(obj)
    if len(czhc__pmncb) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(czhc__pmncb[0])


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
    eoh__dvsk = []
    for eta__tars in func_ir.arg_names:
        if eta__tars in typemap and isinstance(typemap[eta__tars], types.
            containers.UniTuple) and typemap[eta__tars].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(eta__tars))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for alxai__ousg in func_ir.blocks.values():
        for stmt in alxai__ousg.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    doefy__bkoyl = getattr(val, 'code', None)
                    if doefy__bkoyl is not None:
                        if getattr(val, 'closure', None) is not None:
                            yydo__gcj = '<creating a function from a closure>'
                            cix__amnh = ''
                        else:
                            yydo__gcj = doefy__bkoyl.co_name
                            cix__amnh = '(%s) ' % yydo__gcj
                    else:
                        yydo__gcj = '<could not ascertain use case>'
                        cix__amnh = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (yydo__gcj, cix__amnh))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                clb__gvbk = False
                if isinstance(val, pytypes.FunctionType):
                    clb__gvbk = val in {numba.gdb, numba.gdb_init}
                if not clb__gvbk:
                    clb__gvbk = getattr(val, '_name', '') == 'gdb_internal'
                if clb__gvbk:
                    eoh__dvsk.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    wnxt__vazo = func_ir.get_definition(var)
                    uzfy__novcd = guard(find_callname, func_ir, wnxt__vazo)
                    if uzfy__novcd and uzfy__novcd[1] == 'numpy':
                        ty = getattr(numpy, uzfy__novcd[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    ewc__jliv = '' if var.startswith('$') else "'{}' ".format(
                        var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(ewc__jliv), loc=stmt.loc)
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
    ggzs__uxhx, jdoou__ygka = next(iter(val.items()))
    vqz__ygy = typeof_impl(ggzs__uxhx, c)
    nvoax__hgh = typeof_impl(jdoou__ygka, c)
    if vqz__ygy is None or nvoax__hgh is None:
        raise ValueError(
            f'Cannot type dict element type {type(ggzs__uxhx)}, {type(jdoou__ygka)}'
            )
    return types.DictType(vqz__ygy, nvoax__hgh)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    npfo__vovl = cgutils.alloca_once_value(c.builder, val)
    smgd__ipnd = c.pyapi.object_hasattr_string(val, '_opaque')
    fphk__gzop = c.builder.icmp_unsigned('==', smgd__ipnd, lir.Constant(
        smgd__ipnd.type, 0))
    wwkuf__qlcfl = typ.key_type
    mbgoh__uxh = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(wwkuf__qlcfl, mbgoh__uxh)

    def copy_dict(out_dict, in_dict):
        for ggzs__uxhx, jdoou__ygka in in_dict.items():
            out_dict[ggzs__uxhx] = jdoou__ygka
    with c.builder.if_then(fphk__gzop):
        afrs__spcj = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        lxjl__sak = c.pyapi.call_function_objargs(afrs__spcj, [])
        kukss__qnnwo = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(kukss__qnnwo, [lxjl__sak, val])
        c.builder.store(lxjl__sak, npfo__vovl)
    val = c.builder.load(npfo__vovl)
    xfxdc__kyfj = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    fymol__mvqy = c.pyapi.object_type(val)
    ixk__zhbwv = c.builder.icmp_unsigned('==', fymol__mvqy, xfxdc__kyfj)
    with c.builder.if_else(ixk__zhbwv) as (then, orelse):
        with then:
            xygrg__vyg = c.pyapi.object_getattr_string(val, '_opaque')
            zlsn__fhft = types.MemInfoPointer(types.voidptr)
            ikg__nck = c.unbox(zlsn__fhft, xygrg__vyg)
            mi = ikg__nck.value
            wnfw__yhkc = zlsn__fhft, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *wnfw__yhkc)
            uard__nllnz = context.get_constant_null(wnfw__yhkc[1])
            args = mi, uard__nllnz
            yrbo__sma, rjfsx__cllz = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, rjfsx__cllz)
            c.pyapi.decref(xygrg__vyg)
            qxi__smhc = c.builder.basic_block
        with orelse:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", fymol__mvqy, xfxdc__kyfj)
            ybyc__beafh = c.builder.basic_block
    gmrh__wbv = c.builder.phi(rjfsx__cllz.type)
    gsbfc__npuwh = c.builder.phi(yrbo__sma.type)
    gmrh__wbv.add_incoming(rjfsx__cllz, qxi__smhc)
    gmrh__wbv.add_incoming(rjfsx__cllz.type(None), ybyc__beafh)
    gsbfc__npuwh.add_incoming(yrbo__sma, qxi__smhc)
    gsbfc__npuwh.add_incoming(cgutils.true_bit, ybyc__beafh)
    c.pyapi.decref(xfxdc__kyfj)
    c.pyapi.decref(fymol__mvqy)
    with c.builder.if_then(fphk__gzop):
        c.pyapi.decref(val)
    return NativeValue(gmrh__wbv, is_error=gsbfc__npuwh)


import numba.typed.typeddict
if _check_numba_change:
    lines = inspect.getsource(numba.core.pythonapi._unboxers.functions[
        numba.core.types.DictType])
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5f6f183b94dc57838538c668a54c2476576c85d8553843f3219f5162c61e7816':
        warnings.warn('unbox_dicttype has changed')
numba.core.pythonapi._unboxers.functions[types.DictType] = unbox_dicttype
