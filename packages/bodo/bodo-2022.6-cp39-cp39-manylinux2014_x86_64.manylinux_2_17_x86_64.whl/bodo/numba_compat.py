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
import numba.core.typing.listdecl
import numba.np.linalg
from numba.core import analysis, cgutils, errors, ir, ir_utils, types
from numba.core.compiler import Compiler
from numba.core.errors import ForceLiteralArg, LiteralTypingError, TypingError
from numba.core.ir_utils import GuardException, _create_function_from_code_obj, analysis, build_definitions, find_callname, get_definition, guard, has_no_side_effect, mk_unique_var, remove_dead_extensions, replace_vars_inner, require, visit_vars_extensions, visit_vars_inner
from numba.core.types import literal
from numba.core.types.functions import _bt_as_lines, _ResolutionFailures, _termcolor, _unlit_non_poison
from numba.core.typing.templates import AbstractTemplate, Signature, _EmptyImplementationEntry, _inline_info, _OverloadAttributeTemplate, infer_global, signature
from numba.core.typing.typeof import Purpose, typeof
from numba.experimental.jitclass import base as jitclass_base
from numba.experimental.jitclass import decorators as jitclass_decorators
from numba.extending import NativeValue, lower_builtin, typeof_impl
from numba.parfors.parfor import get_expr_args
from bodo.utils.python_310_bytecode_pass import Bodo310ByteCodePass, peep_hole_call_function_ex_to_call_function_kw, peep_hole_fuse_dict_add_updates
from bodo.utils.typing import BodoError, get_overload_const_str, is_overload_constant_str, raise_bodo_error
_check_numba_change = False
numba.core.typing.templates._IntrinsicTemplate.prefer_literal = True


def run_frontend(func, inline_closures=False, emit_dels=False):
    from numba.core.utils import PYVERSION
    ebwy__prft = numba.core.bytecode.FunctionIdentity.from_function(func)
    ticzp__idta = numba.core.interpreter.Interpreter(ebwy__prft)
    bgh__jse = numba.core.bytecode.ByteCode(func_id=ebwy__prft)
    func_ir = ticzp__idta.interpret(bgh__jse)
    if PYVERSION == (3, 10):
        func_ir = peep_hole_call_function_ex_to_call_function_kw(func_ir)
        func_ir = peep_hole_fuse_dict_add_updates(func_ir)
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
        qqvtz__eqnc = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        qqvtz__eqnc.run()
    weehg__jgj = numba.core.postproc.PostProcessor(func_ir)
    weehg__jgj.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, jtlm__ceoyh in visit_vars_extensions.items():
        if isinstance(stmt, t):
            jtlm__ceoyh(stmt, callback, cbdata)
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
    gtww__dgq = ['ravel', 'transpose', 'reshape']
    for lhpxp__skif in blocks.values():
        for kga__rmnov in lhpxp__skif.body:
            if type(kga__rmnov) in alias_analysis_extensions:
                jtlm__ceoyh = alias_analysis_extensions[type(kga__rmnov)]
                jtlm__ceoyh(kga__rmnov, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(kga__rmnov, ir.Assign):
                dph__ozn = kga__rmnov.value
                ikgb__wlyzr = kga__rmnov.target.name
                if is_immutable_type(ikgb__wlyzr, typemap):
                    continue
                if isinstance(dph__ozn, ir.Var
                    ) and ikgb__wlyzr != dph__ozn.name:
                    _add_alias(ikgb__wlyzr, dph__ozn.name, alias_map,
                        arg_aliases)
                if isinstance(dph__ozn, ir.Expr) and (dph__ozn.op == 'cast' or
                    dph__ozn.op in ['getitem', 'static_getitem']):
                    _add_alias(ikgb__wlyzr, dph__ozn.value.name, alias_map,
                        arg_aliases)
                if isinstance(dph__ozn, ir.Expr
                    ) and dph__ozn.op == 'inplace_binop':
                    _add_alias(ikgb__wlyzr, dph__ozn.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(dph__ozn, ir.Expr
                    ) and dph__ozn.op == 'getattr' and dph__ozn.attr in ['T',
                    'ctypes', 'flat']:
                    _add_alias(ikgb__wlyzr, dph__ozn.value.name, alias_map,
                        arg_aliases)
                if isinstance(dph__ozn, ir.Expr
                    ) and dph__ozn.op == 'getattr' and dph__ozn.attr not in [
                    'shape'] and dph__ozn.value.name in arg_aliases:
                    _add_alias(ikgb__wlyzr, dph__ozn.value.name, alias_map,
                        arg_aliases)
                if isinstance(dph__ozn, ir.Expr
                    ) and dph__ozn.op == 'getattr' and dph__ozn.attr in ('loc',
                    'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(ikgb__wlyzr, dph__ozn.value.name, alias_map,
                        arg_aliases)
                if isinstance(dph__ozn, ir.Expr) and dph__ozn.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(ikgb__wlyzr, typemap):
                    for fjv__wca in dph__ozn.items:
                        _add_alias(ikgb__wlyzr, fjv__wca.name, alias_map,
                            arg_aliases)
                if isinstance(dph__ozn, ir.Expr) and dph__ozn.op == 'call':
                    qzq__liiwi = guard(find_callname, func_ir, dph__ozn,
                        typemap)
                    if qzq__liiwi is None:
                        continue
                    fun__bhpb, bba__lqdfv = qzq__liiwi
                    if qzq__liiwi in alias_func_extensions:
                        gjs__dygf = alias_func_extensions[qzq__liiwi]
                        gjs__dygf(ikgb__wlyzr, dph__ozn.args, alias_map,
                            arg_aliases)
                    if bba__lqdfv == 'numpy' and fun__bhpb in gtww__dgq:
                        _add_alias(ikgb__wlyzr, dph__ozn.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(bba__lqdfv, ir.Var
                        ) and fun__bhpb in gtww__dgq:
                        _add_alias(ikgb__wlyzr, bba__lqdfv.name, alias_map,
                            arg_aliases)
    vigo__sbk = copy.deepcopy(alias_map)
    for fjv__wca in vigo__sbk:
        for yjc__jrxha in vigo__sbk[fjv__wca]:
            alias_map[fjv__wca] |= alias_map[yjc__jrxha]
        for yjc__jrxha in vigo__sbk[fjv__wca]:
            alias_map[yjc__jrxha] = alias_map[fjv__wca]
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
    tgybf__aqizp = compute_cfg_from_blocks(func_ir.blocks)
    bxef__nmia = compute_use_defs(func_ir.blocks)
    yidhs__fiby = compute_live_map(tgybf__aqizp, func_ir.blocks, bxef__nmia
        .usemap, bxef__nmia.defmap)
    lljuz__xuo = True
    while lljuz__xuo:
        lljuz__xuo = False
        for kls__qvxdo, block in func_ir.blocks.items():
            lives = {fjv__wca.name for fjv__wca in block.terminator.list_vars()
                }
            for giz__elg, rkyxq__futoy in tgybf__aqizp.successors(kls__qvxdo):
                lives |= yidhs__fiby[giz__elg]
            rnif__rgko = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    ikgb__wlyzr = stmt.target
                    gykud__ekw = stmt.value
                    if ikgb__wlyzr.name not in lives:
                        if isinstance(gykud__ekw, ir.Expr
                            ) and gykud__ekw.op == 'make_function':
                            continue
                        if isinstance(gykud__ekw, ir.Expr
                            ) and gykud__ekw.op == 'getattr':
                            continue
                        if isinstance(gykud__ekw, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(ikgb__wlyzr,
                            None), types.Function):
                            continue
                        if isinstance(gykud__ekw, ir.Expr
                            ) and gykud__ekw.op == 'build_map':
                            continue
                        if isinstance(gykud__ekw, ir.Expr
                            ) and gykud__ekw.op == 'build_tuple':
                            continue
                    if isinstance(gykud__ekw, ir.Var
                        ) and ikgb__wlyzr.name == gykud__ekw.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    fmsv__uan = analysis.ir_extension_usedefs[type(stmt)]
                    cun__ggo, djce__inuw = fmsv__uan(stmt)
                    lives -= djce__inuw
                    lives |= cun__ggo
                else:
                    lives |= {fjv__wca.name for fjv__wca in stmt.list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(ikgb__wlyzr.name)
                rnif__rgko.append(stmt)
            rnif__rgko.reverse()
            if len(block.body) != len(rnif__rgko):
                lljuz__xuo = True
            block.body = rnif__rgko


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    yceea__paxps = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (yceea__paxps,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    rhh__maw = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), rhh__maw)


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
            for fls__pssr in fnty.templates:
                self._inline_overloads.update(fls__pssr._inline_overloads)
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
    rhh__maw = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), rhh__maw)
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
    doju__chgz, xhfk__cchvh = self._get_impl(args, kws)
    if doju__chgz is None:
        return
    hyhzh__takt = types.Dispatcher(doju__chgz)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        vqi__pzf = doju__chgz._compiler
        flags = compiler.Flags()
        ifpl__fgn = vqi__pzf.targetdescr.typing_context
        nov__idk = vqi__pzf.targetdescr.target_context
        hdofx__kwe = vqi__pzf.pipeline_class(ifpl__fgn, nov__idk, None,
            None, None, flags, None)
        boh__chcd = InlineWorker(ifpl__fgn, nov__idk, vqi__pzf.locals,
            hdofx__kwe, flags, None)
        ubuo__wmnk = hyhzh__takt.dispatcher.get_call_template
        fls__pssr, vkt__omdb, nrlea__evjyd, kws = ubuo__wmnk(xhfk__cchvh, kws)
        if nrlea__evjyd in self._inline_overloads:
            return self._inline_overloads[nrlea__evjyd]['iinfo'].signature
        ir = boh__chcd.run_untyped_passes(hyhzh__takt.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, nov__idk, ir, nrlea__evjyd, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, nrlea__evjyd, None)
        self._inline_overloads[sig.args] = {'folded_args': nrlea__evjyd}
        pvkvg__svbck = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = pvkvg__svbck
        if not self._inline.is_always_inline:
            sig = hyhzh__takt.get_call_type(self.context, xhfk__cchvh, kws)
            self._compiled_overloads[sig.args] = hyhzh__takt.get_overload(sig)
        yrvd__qfdve = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': nrlea__evjyd,
            'iinfo': yrvd__qfdve}
    else:
        sig = hyhzh__takt.get_call_type(self.context, xhfk__cchvh, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = hyhzh__takt.get_overload(sig)
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
    gce__lgy = [True, False]
    ppq__wzq = [False, True]
    uksyg__lwtr = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    gnvdf__fshzb = get_local_target(context)
    wow__bwzgv = utils.order_by_target_specificity(gnvdf__fshzb, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for fxid__hzr in wow__bwzgv:
        lsg__niik = fxid__hzr(context)
        frve__aztk = gce__lgy if lsg__niik.prefer_literal else ppq__wzq
        frve__aztk = [True] if getattr(lsg__niik, '_no_unliteral', False
            ) else frve__aztk
        for mqrlz__jkp in frve__aztk:
            try:
                if mqrlz__jkp:
                    sig = lsg__niik.apply(args, kws)
                else:
                    dxm__rmdv = tuple([_unlit_non_poison(a) for a in args])
                    ksw__gmwi = {nealf__llt: _unlit_non_poison(fjv__wca) for
                        nealf__llt, fjv__wca in kws.items()}
                    sig = lsg__niik.apply(dxm__rmdv, ksw__gmwi)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    uksyg__lwtr.add_error(lsg__niik, False, e, mqrlz__jkp)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = lsg__niik.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    jap__twsc = getattr(lsg__niik, 'cases', None)
                    if jap__twsc is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            jap__twsc)
                    else:
                        msg = 'No match.'
                    uksyg__lwtr.add_error(lsg__niik, True, msg, mqrlz__jkp)
    uksyg__lwtr.raise_error()


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
    fls__pssr = self.template(context)
    ludy__gev = None
    ssip__hgpc = None
    wdhg__mjywe = None
    frve__aztk = [True, False] if fls__pssr.prefer_literal else [False, True]
    frve__aztk = [True] if getattr(fls__pssr, '_no_unliteral', False
        ) else frve__aztk
    for mqrlz__jkp in frve__aztk:
        if mqrlz__jkp:
            try:
                wdhg__mjywe = fls__pssr.apply(args, kws)
            except Exception as kys__jdef:
                if isinstance(kys__jdef, errors.ForceLiteralArg):
                    raise kys__jdef
                ludy__gev = kys__jdef
                wdhg__mjywe = None
            else:
                break
        else:
            obsa__qpn = tuple([_unlit_non_poison(a) for a in args])
            xrex__zim = {nealf__llt: _unlit_non_poison(fjv__wca) for 
                nealf__llt, fjv__wca in kws.items()}
            kdtln__jio = obsa__qpn == args and kws == xrex__zim
            if not kdtln__jio and wdhg__mjywe is None:
                try:
                    wdhg__mjywe = fls__pssr.apply(obsa__qpn, xrex__zim)
                except Exception as kys__jdef:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        kys__jdef, errors.NumbaError):
                        raise kys__jdef
                    if isinstance(kys__jdef, errors.ForceLiteralArg):
                        if fls__pssr.prefer_literal:
                            raise kys__jdef
                    ssip__hgpc = kys__jdef
                else:
                    break
    if wdhg__mjywe is None and (ssip__hgpc is not None or ludy__gev is not None
        ):
        prujt__kisrz = '- Resolution failure for {} arguments:\n{}\n'
        mfm__ajxd = _termcolor.highlight(prujt__kisrz)
        if numba.core.config.DEVELOPER_MODE:
            fmt__mqwq = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    reo__yshe = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    reo__yshe = ['']
                zad__mrt = '\n{}'.format(2 * fmt__mqwq)
                svj__xhix = _termcolor.reset(zad__mrt + zad__mrt.join(
                    _bt_as_lines(reo__yshe)))
                return _termcolor.reset(svj__xhix)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            sczue__johv = str(e)
            sczue__johv = sczue__johv if sczue__johv else str(repr(e)
                ) + add_bt(e)
            qshcz__jhpd = errors.TypingError(textwrap.dedent(sczue__johv))
            return mfm__ajxd.format(literalness, str(qshcz__jhpd))
        import bodo
        if isinstance(ludy__gev, bodo.utils.typing.BodoError):
            raise ludy__gev
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', ludy__gev) +
                nested_msg('non-literal', ssip__hgpc))
        else:
            if 'missing a required argument' in ludy__gev.msg:
                msg = 'missing a required argument'
            else:
                msg = 'Compilation error for '
                if isinstance(self.this, bodo.hiframes.pd_dataframe_ext.
                    DataFrameType):
                    msg += 'DataFrame.'
                elif isinstance(self.this, bodo.hiframes.pd_series_ext.
                    SeriesType):
                    msg += 'Series.'
                msg += f'{self.typing_key[1]}().{bodo_typing_error_info}'
            raise errors.TypingError(msg, loc=ludy__gev.loc)
    return wdhg__mjywe


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
    from llvmlite import ir as lir
    fnty = lir.FunctionType(self.pyobj, [self.cstring, self.py_ssize_t])
    fun__bhpb = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=fun__bhpb)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            dhwx__ggb = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), dhwx__ggb)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    jdevi__xlvu = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            jdevi__xlvu.append(types.Omitted(a.value))
        else:
            jdevi__xlvu.append(self.typeof_pyval(a))
    wmtod__sjqd = None
    try:
        error = None
        wmtod__sjqd = self.compile(tuple(jdevi__xlvu))
    except errors.ForceLiteralArg as e:
        dtz__zodfg = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if dtz__zodfg:
            rzg__pmh = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            zvay__prls = ', '.join('Arg #{} is {}'.format(i, args[i]) for i in
                sorted(dtz__zodfg))
            raise errors.CompilerError(rzg__pmh.format(zvay__prls))
        xhfk__cchvh = []
        try:
            for i, fjv__wca in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        xhfk__cchvh.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        xhfk__cchvh.append(types.literal(args[i]))
                else:
                    xhfk__cchvh.append(args[i])
            args = xhfk__cchvh
        except (OSError, FileNotFoundError) as pfd__oqeu:
            error = FileNotFoundError(str(pfd__oqeu) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                wmtod__sjqd = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        ripom__ouj = []
        for i, nchio__uvqa in enumerate(args):
            val = nchio__uvqa.value if isinstance(nchio__uvqa, numba.core.
                dispatcher.OmittedArg) else nchio__uvqa
            try:
                tjqi__iciss = typeof(val, Purpose.argument)
            except ValueError as udah__bcn:
                ripom__ouj.append((i, str(udah__bcn)))
            else:
                if tjqi__iciss is None:
                    ripom__ouj.append((i,
                        f'cannot determine Numba type of value {val}'))
        if ripom__ouj:
            kmqq__vmadc = '\n'.join(f'- argument {i}: {bjwfk__jdwha}' for i,
                bjwfk__jdwha in ripom__ouj)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{kmqq__vmadc}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                cizy__tpjlp = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                yurz__tffy = False
                for wpxsa__vrxiw in cizy__tpjlp:
                    if wpxsa__vrxiw in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        yurz__tffy = True
                        break
                if not yurz__tffy:
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
                dhwx__ggb = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), dhwx__ggb)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return wmtod__sjqd


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
    for qmkx__twt in cres.library._codegen._engine._defined_symbols:
        if qmkx__twt.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in qmkx__twt and (
            'bodo_gb_udf_update_local' in qmkx__twt or 
            'bodo_gb_udf_combine' in qmkx__twt or 'bodo_gb_udf_eval' in
            qmkx__twt or 'bodo_gb_apply_general_udfs' in qmkx__twt):
            gb_agg_cfunc_addr[qmkx__twt
                ] = cres.library.get_pointer_to_function(qmkx__twt)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for qmkx__twt in cres.library._codegen._engine._defined_symbols:
        if qmkx__twt.startswith('cfunc') and ('get_join_cond_addr' not in
            qmkx__twt or 'bodo_join_gen_cond' in qmkx__twt):
            join_gen_cond_cfunc_addr[qmkx__twt
                ] = cres.library.get_pointer_to_function(qmkx__twt)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    doju__chgz = self._get_dispatcher_for_current_target()
    if doju__chgz is not self:
        return doju__chgz.compile(sig)
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
            jnwf__snbjz = self.overloads.get(tuple(args))
            if jnwf__snbjz is not None:
                return jnwf__snbjz.entry_point
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
            byv__dab = dict(dispatcher=self, args=args, return_type=return_type
                )
            with ev.trigger_event('numba:compile', data=byv__dab):
                try:
                    cres = self._compiler.compile(args, return_type)
                except errors.ForceLiteralArg as e:

                    def folded(args, kws):
                        return self._compiler.fold_argument_types(args, kws)[1]
                    raise e.bind_fold_arguments(folded)
                self.add_overload(cres)
            if os.environ.get('BODO_PLATFORM_CACHE_LOCATION') is not None:
                if bodo.get_rank() == 0:
                    self._cache.save_overload(sig, cres)
            else:
                xnyw__mibgv = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in xnyw__mibgv:
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
    atew__bjx = self._final_module
    eac__rowew = []
    tnbxt__vedcf = 0
    for fn in atew__bjx.functions:
        tnbxt__vedcf += 1
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
            eac__rowew.append(fn.name)
    if tnbxt__vedcf == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if eac__rowew:
        atew__bjx = atew__bjx.clone()
        for name in eac__rowew:
            atew__bjx.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = atew__bjx
    return atew__bjx


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
    for bnmup__wixg in self.constraints:
        loc = bnmup__wixg.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                bnmup__wixg(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                xkhzz__egdo = numba.core.errors.TypingError(str(e), loc=
                    bnmup__wixg.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(xkhzz__egdo, e))
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
                    xkhzz__egdo = numba.core.errors.TypingError(msg.format(
                        con=bnmup__wixg, err=str(e)), loc=bnmup__wixg.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(xkhzz__egdo, e))
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
    for wfwa__bqpt in self._failures.values():
        for vjbt__wewr in wfwa__bqpt:
            if isinstance(vjbt__wewr.error, ForceLiteralArg):
                raise vjbt__wewr.error
            if isinstance(vjbt__wewr.error, bodo.utils.typing.BodoError):
                raise vjbt__wewr.error
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
    jydcz__ewrgz = False
    rnif__rgko = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        lyye__rhi = set()
        syosp__cxdd = lives & alias_set
        for fjv__wca in syosp__cxdd:
            lyye__rhi |= alias_map[fjv__wca]
        lives_n_aliases = lives | lyye__rhi | arg_aliases
        if type(stmt) in remove_dead_extensions:
            jtlm__ceoyh = remove_dead_extensions[type(stmt)]
            stmt = jtlm__ceoyh(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                jydcz__ewrgz = True
                continue
        if isinstance(stmt, ir.Assign):
            ikgb__wlyzr = stmt.target
            gykud__ekw = stmt.value
            if ikgb__wlyzr.name not in lives:
                if has_no_side_effect(gykud__ekw, lives_n_aliases, call_table):
                    jydcz__ewrgz = True
                    continue
                if isinstance(gykud__ekw, ir.Expr
                    ) and gykud__ekw.op == 'call' and call_table[gykud__ekw
                    .func.name] == ['astype']:
                    mwtl__fmajw = guard(get_definition, func_ir, gykud__ekw
                        .func)
                    if (mwtl__fmajw is not None and mwtl__fmajw.op ==
                        'getattr' and isinstance(typemap[mwtl__fmajw.value.
                        name], types.Array) and mwtl__fmajw.attr == 'astype'):
                        jydcz__ewrgz = True
                        continue
            if saved_array_analysis and ikgb__wlyzr.name in lives and is_expr(
                gykud__ekw, 'getattr'
                ) and gykud__ekw.attr == 'shape' and is_array_typ(typemap[
                gykud__ekw.value.name]) and gykud__ekw.value.name not in lives:
                eyfqs__vhn = {fjv__wca: nealf__llt for nealf__llt, fjv__wca in
                    func_ir.blocks.items()}
                if block in eyfqs__vhn:
                    kls__qvxdo = eyfqs__vhn[block]
                    sqw__ainlh = saved_array_analysis.get_equiv_set(kls__qvxdo)
                    mrtcp__troe = sqw__ainlh.get_equiv_set(gykud__ekw.value)
                    if mrtcp__troe is not None:
                        for fjv__wca in mrtcp__troe:
                            if fjv__wca.endswith('#0'):
                                fjv__wca = fjv__wca[:-2]
                            if fjv__wca in typemap and is_array_typ(typemap
                                [fjv__wca]) and fjv__wca in lives:
                                gykud__ekw.value = ir.Var(gykud__ekw.value.
                                    scope, fjv__wca, gykud__ekw.value.loc)
                                jydcz__ewrgz = True
                                break
            if isinstance(gykud__ekw, ir.Var
                ) and ikgb__wlyzr.name == gykud__ekw.name:
                jydcz__ewrgz = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                jydcz__ewrgz = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            fmsv__uan = analysis.ir_extension_usedefs[type(stmt)]
            cun__ggo, djce__inuw = fmsv__uan(stmt)
            lives -= djce__inuw
            lives |= cun__ggo
        else:
            lives |= {fjv__wca.name for fjv__wca in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                nlayt__rvtd = set()
                if isinstance(gykud__ekw, ir.Expr):
                    nlayt__rvtd = {fjv__wca.name for fjv__wca in gykud__ekw
                        .list_vars()}
                if ikgb__wlyzr.name not in nlayt__rvtd:
                    lives.remove(ikgb__wlyzr.name)
        rnif__rgko.append(stmt)
    rnif__rgko.reverse()
    block.body = rnif__rgko
    return jydcz__ewrgz


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            gsjim__fqg, = args
            if isinstance(gsjim__fqg, types.IterableType):
                dtype = gsjim__fqg.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), gsjim__fqg)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    roy__eyw = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (roy__eyw, self.dtype)
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
        except LiteralTypingError as gsee__qhq:
            return
    try:
        return literal(value)
    except LiteralTypingError as gsee__qhq:
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
        lco__xkvew = py_func.__qualname__
    except AttributeError as gsee__qhq:
        lco__xkvew = py_func.__name__
    noequ__apvn = inspect.getfile(py_func)
    for cls in self._locator_classes:
        csnca__mfv = cls.from_function(py_func, noequ__apvn)
        if csnca__mfv is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (lco__xkvew, noequ__apvn))
    self._locator = csnca__mfv
    cqsvr__cybwj = inspect.getfile(py_func)
    qzto__lludi = os.path.splitext(os.path.basename(cqsvr__cybwj))[0]
    if noequ__apvn.startswith('<ipython-'):
        usm__fbhqw = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', qzto__lludi, count=1)
        if usm__fbhqw == qzto__lludi:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        qzto__lludi = usm__fbhqw
    eaf__hypz = '%s.%s' % (qzto__lludi, lco__xkvew)
    jvyww__nfe = getattr(sys, 'abiflags', '')
    self._filename_base = self.get_filename_base(eaf__hypz, jvyww__nfe)


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    ets__vlz = list(filter(lambda a: self._istuple(a.name), args))
    if len(ets__vlz) == 2 and fn.__name__ == 'add':
        xjyi__adt = self.typemap[ets__vlz[0].name]
        qel__hdhvl = self.typemap[ets__vlz[1].name]
        if xjyi__adt.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                ets__vlz[1]))
        if qel__hdhvl.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                ets__vlz[0]))
        try:
            oocce__pxjv = [equiv_set.get_shape(x) for x in ets__vlz]
            if None in oocce__pxjv:
                return None
            cktvg__hwxki = sum(oocce__pxjv, ())
            return ArrayAnalysis.AnalyzeResult(shape=cktvg__hwxki)
        except GuardException as gsee__qhq:
            return None
    hwwr__nntlq = list(filter(lambda a: self._isarray(a.name), args))
    require(len(hwwr__nntlq) > 0)
    jhzs__mku = [x.name for x in hwwr__nntlq]
    phmp__vcgdt = [self.typemap[x.name].ndim for x in hwwr__nntlq]
    rsflj__ludtn = max(phmp__vcgdt)
    require(rsflj__ludtn > 0)
    oocce__pxjv = [equiv_set.get_shape(x) for x in hwwr__nntlq]
    if any(a is None for a in oocce__pxjv):
        return ArrayAnalysis.AnalyzeResult(shape=hwwr__nntlq[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, hwwr__nntlq))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, oocce__pxjv,
        jhzs__mku)


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


def slice_size(self, index, dsize, equiv_set, scope, stmts):
    return None, None


numba.parfors.array_analysis.ArrayAnalysis.slice_size = slice_size


def convert_code_obj_to_function(code_obj, caller_ir):
    import bodo
    qcvc__kcpjj = code_obj.code
    lccr__aqw = len(qcvc__kcpjj.co_freevars)
    ran__jwkwd = qcvc__kcpjj.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        wowu__fljqh, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        ran__jwkwd = [fjv__wca.name for fjv__wca in wowu__fljqh]
    hbzw__qagrx = caller_ir.func_id.func.__globals__
    try:
        hbzw__qagrx = getattr(code_obj, 'globals', hbzw__qagrx)
    except KeyError as gsee__qhq:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    mzc__sastw = []
    for x in ran__jwkwd:
        try:
            qss__awwv = caller_ir.get_definition(x)
        except KeyError as gsee__qhq:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(qss__awwv, (ir.Const, ir.Global, ir.FreeVar)):
            val = qss__awwv.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                yceea__paxps = ir_utils.mk_unique_var('nested_func').replace(
                    '.', '_')
                hbzw__qagrx[yceea__paxps] = bodo.jit(distributed=False)(val)
                hbzw__qagrx[yceea__paxps].is_nested_func = True
                val = yceea__paxps
            if isinstance(val, CPUDispatcher):
                yceea__paxps = ir_utils.mk_unique_var('nested_func').replace(
                    '.', '_')
                hbzw__qagrx[yceea__paxps] = val
                val = yceea__paxps
            mzc__sastw.append(val)
        elif isinstance(qss__awwv, ir.Expr
            ) and qss__awwv.op == 'make_function':
            ohbm__twfh = convert_code_obj_to_function(qss__awwv, caller_ir)
            yceea__paxps = ir_utils.mk_unique_var('nested_func').replace('.',
                '_')
            hbzw__qagrx[yceea__paxps] = bodo.jit(distributed=False)(ohbm__twfh)
            hbzw__qagrx[yceea__paxps].is_nested_func = True
            mzc__sastw.append(yceea__paxps)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    oqaj__xvkab = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate
        (mzc__sastw)])
    nwepy__oaxsz = ','.join([('c_%d' % i) for i in range(lccr__aqw)])
    queco__itlvv = list(qcvc__kcpjj.co_varnames)
    mugc__lce = 0
    oea__gilij = qcvc__kcpjj.co_argcount
    epm__idze = caller_ir.get_definition(code_obj.defaults)
    if epm__idze is not None:
        if isinstance(epm__idze, tuple):
            d = [caller_ir.get_definition(x).value for x in epm__idze]
            qefea__agek = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in epm__idze.items]
            qefea__agek = tuple(d)
        mugc__lce = len(qefea__agek)
    fqhjg__ejo = oea__gilij - mugc__lce
    jhsb__gqzid = ','.join([('%s' % queco__itlvv[i]) for i in range(
        fqhjg__ejo)])
    if mugc__lce:
        wgwt__sonu = [('%s = %s' % (queco__itlvv[i + fqhjg__ejo],
            qefea__agek[i])) for i in range(mugc__lce)]
        jhsb__gqzid += ', '
        jhsb__gqzid += ', '.join(wgwt__sonu)
    return _create_function_from_code_obj(qcvc__kcpjj, oqaj__xvkab,
        jhsb__gqzid, nwepy__oaxsz, hbzw__qagrx)


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
    for omoc__bwz, (gfaiv__xtvyh, rncxq__bmkth) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % rncxq__bmkth)
            nuegw__eha = _pass_registry.get(gfaiv__xtvyh).pass_inst
            if isinstance(nuegw__eha, CompilerPass):
                self._runPass(omoc__bwz, nuegw__eha, state)
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
                    pipeline_name, rncxq__bmkth)
                tli__cxeq = self._patch_error(msg, e)
                raise tli__cxeq
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
    eukgp__dzigb = None
    djce__inuw = {}

    def lookup(var, already_seen, varonly=True):
        val = djce__inuw.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    yvilr__gbldg = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        ikgb__wlyzr = stmt.target
        gykud__ekw = stmt.value
        djce__inuw[ikgb__wlyzr.name] = gykud__ekw
        if isinstance(gykud__ekw, ir.Var) and gykud__ekw.name in djce__inuw:
            gykud__ekw = lookup(gykud__ekw, set())
        if isinstance(gykud__ekw, ir.Expr):
            lbs__xsxuf = set(lookup(fjv__wca, set(), True).name for
                fjv__wca in gykud__ekw.list_vars())
            if name in lbs__xsxuf:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(gykud__ekw)]
                vedky__veka = [x for x, byfzi__urc in args if byfzi__urc.
                    name != name]
                args = [(x, byfzi__urc) for x, byfzi__urc in args if x !=
                    byfzi__urc.name]
                ouewq__byx = dict(args)
                if len(vedky__veka) == 1:
                    ouewq__byx[vedky__veka[0]] = ir.Var(ikgb__wlyzr.scope, 
                        name + '#init', ikgb__wlyzr.loc)
                replace_vars_inner(gykud__ekw, ouewq__byx)
                eukgp__dzigb = nodes[i:]
                break
    return eukgp__dzigb


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
        ipw__xlnv = expand_aliases({fjv__wca.name for fjv__wca in stmt.
            list_vars()}, alias_map, arg_aliases)
        daga__kmk = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        nlab__jcsrd = expand_aliases({fjv__wca.name for fjv__wca in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        bwz__skmhk = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(daga__kmk & nlab__jcsrd | bwz__skmhk & ipw__xlnv) == 0:
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
    msikl__vqy = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            msikl__vqy.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                msikl__vqy.update(get_parfor_writes(stmt, func_ir))
    return msikl__vqy


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    msikl__vqy = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        msikl__vqy.add(stmt.target.name)
    if isinstance(stmt, bodo.ir.aggregate.Aggregate):
        msikl__vqy = {fjv__wca.name for fjv__wca in stmt.df_out_vars.values()}
        if stmt.out_key_vars is not None:
            msikl__vqy.update({fjv__wca.name for fjv__wca in stmt.out_key_vars}
                )
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        msikl__vqy = {fjv__wca.name for fjv__wca in stmt.out_vars}
    if isinstance(stmt, bodo.ir.join.Join):
        msikl__vqy = {fjv__wca.name for fjv__wca in stmt.get_live_out_vars()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            msikl__vqy.update({fjv__wca.name for fjv__wca in stmt.
                get_live_out_vars()})
    if is_call_assign(stmt):
        qzq__liiwi = guard(find_callname, func_ir, stmt.value)
        if qzq__liiwi in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            msikl__vqy.add(stmt.value.args[0].name)
        if qzq__liiwi == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            msikl__vqy.add(stmt.value.args[1].name)
    return msikl__vqy


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
        jtlm__ceoyh = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        gvhq__ktahw = jtlm__ceoyh.format(self, msg)
        self.args = gvhq__ktahw,
    else:
        jtlm__ceoyh = _termcolor.errmsg('{0}')
        gvhq__ktahw = jtlm__ceoyh.format(self)
        self.args = gvhq__ktahw,
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
        for izn__nnfv in options['distributed']:
            dist_spec[izn__nnfv] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for izn__nnfv in options['distributed_block']:
            dist_spec[izn__nnfv] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    wezcw__hms = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, rnn__rrxyz in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(rnn__rrxyz)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    biy__huhs = {}
    for djbna__hvaw in reversed(inspect.getmro(cls)):
        biy__huhs.update(djbna__hvaw.__dict__)
    vviiu__vra, jzvpu__jbemb, mqhe__vivx, undao__zfh = {}, {}, {}, {}
    for nealf__llt, fjv__wca in biy__huhs.items():
        if isinstance(fjv__wca, pytypes.FunctionType):
            vviiu__vra[nealf__llt] = fjv__wca
        elif isinstance(fjv__wca, property):
            jzvpu__jbemb[nealf__llt] = fjv__wca
        elif isinstance(fjv__wca, staticmethod):
            mqhe__vivx[nealf__llt] = fjv__wca
        else:
            undao__zfh[nealf__llt] = fjv__wca
    zqi__xfdnc = (set(vviiu__vra) | set(jzvpu__jbemb) | set(mqhe__vivx)) & set(
        spec)
    if zqi__xfdnc:
        raise NameError('name shadowing: {0}'.format(', '.join(zqi__xfdnc)))
    lgt__ymu = undao__zfh.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(undao__zfh)
    if undao__zfh:
        msg = 'class members are not yet supported: {0}'
        vjb__pnhd = ', '.join(undao__zfh.keys())
        raise TypeError(msg.format(vjb__pnhd))
    for nealf__llt, fjv__wca in jzvpu__jbemb.items():
        if fjv__wca.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(nealf__llt))
    jit_methods = {nealf__llt: bodo.jit(returns_maybe_distributed=
        wezcw__hms)(fjv__wca) for nealf__llt, fjv__wca in vviiu__vra.items()}
    jit_props = {}
    for nealf__llt, fjv__wca in jzvpu__jbemb.items():
        rhh__maw = {}
        if fjv__wca.fget:
            rhh__maw['get'] = bodo.jit(fjv__wca.fget)
        if fjv__wca.fset:
            rhh__maw['set'] = bodo.jit(fjv__wca.fset)
        jit_props[nealf__llt] = rhh__maw
    jit_static_methods = {nealf__llt: bodo.jit(fjv__wca.__func__) for 
        nealf__llt, fjv__wca in mqhe__vivx.items()}
    jwr__ibcvs = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    rcmu__nepjp = dict(class_type=jwr__ibcvs, __doc__=lgt__ymu)
    rcmu__nepjp.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), rcmu__nepjp)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, jwr__ibcvs)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(jwr__ibcvs, typingctx, targetctx).register()
    as_numba_type.register(cls, jwr__ibcvs.instance_type)
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
    jdb__dez = ','.join('{0}:{1}'.format(nealf__llt, fjv__wca) for 
        nealf__llt, fjv__wca in struct.items())
    hhoe__ssr = ','.join('{0}:{1}'.format(nealf__llt, fjv__wca) for 
        nealf__llt, fjv__wca in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), jdb__dez, hhoe__ssr)
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
    cle__jpib = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if cle__jpib is None:
        return
    lnq__fwsna, gspzs__mci = cle__jpib
    for a in itertools.chain(lnq__fwsna, gspzs__mci.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, lnq__fwsna, gspzs__mci)
    except ForceLiteralArg as e:
        axr__gyxjr = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(axr__gyxjr, self.kws)
        xec__nrhc = set()
        ezbx__svbje = set()
        lbezz__mvcm = {}
        for omoc__bwz in e.requested_args:
            xfyei__jcl = typeinfer.func_ir.get_definition(folded[omoc__bwz])
            if isinstance(xfyei__jcl, ir.Arg):
                xec__nrhc.add(xfyei__jcl.index)
                if xfyei__jcl.index in e.file_infos:
                    lbezz__mvcm[xfyei__jcl.index] = e.file_infos[xfyei__jcl
                        .index]
            else:
                ezbx__svbje.add(omoc__bwz)
        if ezbx__svbje:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif xec__nrhc:
            raise ForceLiteralArg(xec__nrhc, loc=self.loc, file_infos=
                lbezz__mvcm)
    if sig is None:
        iqmqr__psee = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in lnq__fwsna]
        args += [('%s=%s' % (nealf__llt, fjv__wca)) for nealf__llt,
            fjv__wca in sorted(gspzs__mci.items())]
        ikbh__najow = iqmqr__psee.format(fnty, ', '.join(map(str, args)))
        ecbqy__tfot = context.explain_function_type(fnty)
        msg = '\n'.join([ikbh__najow, ecbqy__tfot])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        rvb__cfwu = context.unify_pairs(sig.recvr, fnty.this)
        if rvb__cfwu is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if rvb__cfwu is not None and rvb__cfwu.is_precise():
            yjg__cjj = fnty.copy(this=rvb__cfwu)
            typeinfer.propagate_refined_type(self.func, yjg__cjj)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            hhv__kat = target.getone()
            if context.unify_pairs(hhv__kat, sig.return_type) == hhv__kat:
                sig = sig.replace(return_type=hhv__kat)
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
        rzg__pmh = '*other* must be a {} but got a {} instead'
        raise TypeError(rzg__pmh.format(ForceLiteralArg, type(other)))
    return ForceLiteralArg(self.requested_args | other.requested_args,
        file_infos={**self.file_infos, **other.file_infos})


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
    dnie__qzic = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for nealf__llt, fjv__wca in kwargs.items():
        vqsu__ttd = None
        try:
            yjndl__pnfq = ir.Var(ir.Scope(None, loc), ir_utils.
                mk_unique_var('dummy'), loc)
            func_ir._definitions[yjndl__pnfq.name] = [fjv__wca]
            vqsu__ttd = get_const_value_inner(func_ir, yjndl__pnfq)
            func_ir._definitions.pop(yjndl__pnfq.name)
            if isinstance(vqsu__ttd, str):
                vqsu__ttd = sigutils._parse_signature_string(vqsu__ttd)
            if isinstance(vqsu__ttd, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {nealf__llt} is annotated as type class {vqsu__ttd}."""
                    )
            assert isinstance(vqsu__ttd, types.Type)
            if isinstance(vqsu__ttd, (types.List, types.Set)):
                vqsu__ttd = vqsu__ttd.copy(reflected=False)
            dnie__qzic[nealf__llt] = vqsu__ttd
        except BodoError as gsee__qhq:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(vqsu__ttd, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(fjv__wca, ir.Global):
                    msg = f'Global {fjv__wca.name!r} is not defined.'
                if isinstance(fjv__wca, ir.FreeVar):
                    msg = f'Freevar {fjv__wca.name!r} is not defined.'
            if isinstance(fjv__wca, ir.Expr) and fjv__wca.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=nealf__llt, msg=msg, loc=loc)
    for name, typ in dnie__qzic.items():
        self._legalize_arg_type(name, typ, loc)
    return dnie__qzic


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
    lrs__livo = inst.arg
    assert lrs__livo > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(lrs__livo)]))
    tmps = [state.make_temp() for _ in range(lrs__livo - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    lkh__tqfr = ir.Global('format', format, loc=self.loc)
    self.store(value=lkh__tqfr, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    mee__jqbl = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=mee__jqbl, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    lrs__livo = inst.arg
    assert lrs__livo > 0, 'invalid BUILD_STRING count'
    ano__wrc = self.get(strings[0])
    for other, jymub__bplk in zip(strings[1:], tmps):
        other = self.get(other)
        dph__ozn = ir.Expr.binop(operator.add, lhs=ano__wrc, rhs=other, loc
            =self.loc)
        self.store(dph__ozn, jymub__bplk)
        ano__wrc = self.get(jymub__bplk)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    xpf__jdf = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, xpf__jdf])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    fcz__ctnzd = mk_unique_var(f'{var_name}')
    blrze__lpodk = fcz__ctnzd.replace('<', '_').replace('>', '_')
    blrze__lpodk = blrze__lpodk.replace('.', '_').replace('$', '_v')
    return blrze__lpodk


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
    import bodo
    ty = classty.instance_type
    if isinstance(ty, types.NPDatetime):

        def typer(val1, val2):
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(val1,
                'numpy.datetime64')
            if val1 == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
                if not is_overload_constant_str(val2):
                    raise_bodo_error(
                        "datetime64(): 'units' must be a 'str' specifying 'ns'"
                        )
                dug__nwxu = get_overload_const_str(val2)
                if dug__nwxu != 'ns':
                    raise BodoError("datetime64(): 'units' must be 'ns'")
                return types.NPDatetime('ns')
    else:

        def typer(val):
            if isinstance(val, (types.BaseTuple, types.Sequence)):
                fnty = self.context.resolve_value_type(np.array)
                sig = fnty.get_call_type(self.context, (val, types.DType(ty
                    )), {})
                return sig.return_type
            elif isinstance(val, (types.Number, types.Boolean, types.
                IntEnumMember)):
                return ty
            elif val == types.unicode_type:
                return ty
            elif isinstance(val, (types.NPDatetime, types.NPTimedelta)):
                if ty.bitwidth == 64:
                    return ty
                else:
                    msg = (
                        f'Cannot cast {val} to {ty} as {ty} is not 64 bits wide.'
                        )
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
        grrdw__gkm = states['defmap']
        if len(grrdw__gkm) == 0:
            vdrl__udkl = assign.target
            numba.core.ssa._logger.debug('first assign: %s', vdrl__udkl)
            if vdrl__udkl.name not in scope.localvars:
                vdrl__udkl = scope.define(assign.target.name, loc=assign.loc)
        else:
            vdrl__udkl = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=vdrl__udkl, value=assign.value, loc=
            assign.loc)
        grrdw__gkm[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    ztc__bub = []
    for nealf__llt, fjv__wca in typing.npydecl.registry.globals:
        if nealf__llt == func:
            ztc__bub.append(fjv__wca)
    for nealf__llt, fjv__wca in typing.templates.builtin_registry.globals:
        if nealf__llt == func:
            ztc__bub.append(fjv__wca)
    if len(ztc__bub) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return ztc__bub


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    win__xqbg = {}
    rfch__wfr = find_topo_order(blocks)
    ejia__kmu = {}
    for kls__qvxdo in rfch__wfr:
        block = blocks[kls__qvxdo]
        rnif__rgko = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                ikgb__wlyzr = stmt.target.name
                gykud__ekw = stmt.value
                if (gykud__ekw.op == 'getattr' and gykud__ekw.attr in
                    arr_math and isinstance(typemap[gykud__ekw.value.name],
                    types.npytypes.Array)):
                    gykud__ekw = stmt.value
                    etvg__krwmb = gykud__ekw.value
                    win__xqbg[ikgb__wlyzr] = etvg__krwmb
                    scope = etvg__krwmb.scope
                    loc = etvg__krwmb.loc
                    mpol__wqzgj = ir.Var(scope, mk_unique_var('$np_g_var'), loc
                        )
                    typemap[mpol__wqzgj.name] = types.misc.Module(numpy)
                    berk__fkld = ir.Global('np', numpy, loc)
                    xyp__xmpv = ir.Assign(berk__fkld, mpol__wqzgj, loc)
                    gykud__ekw.value = mpol__wqzgj
                    rnif__rgko.append(xyp__xmpv)
                    func_ir._definitions[mpol__wqzgj.name] = [berk__fkld]
                    func = getattr(numpy, gykud__ekw.attr)
                    clvx__troo = get_np_ufunc_typ_lst(func)
                    ejia__kmu[ikgb__wlyzr] = clvx__troo
                if (gykud__ekw.op == 'call' and gykud__ekw.func.name in
                    win__xqbg):
                    etvg__krwmb = win__xqbg[gykud__ekw.func.name]
                    cgk__eqs = calltypes.pop(gykud__ekw)
                    kct__dpeoy = cgk__eqs.args[:len(gykud__ekw.args)]
                    pxi__bxeu = {name: typemap[fjv__wca.name] for name,
                        fjv__wca in gykud__ekw.kws}
                    wjv__nyeo = ejia__kmu[gykud__ekw.func.name]
                    ckdsm__kllmq = None
                    for qmdl__ngb in wjv__nyeo:
                        try:
                            ckdsm__kllmq = qmdl__ngb.get_call_type(typingctx,
                                [typemap[etvg__krwmb.name]] + list(
                                kct__dpeoy), pxi__bxeu)
                            typemap.pop(gykud__ekw.func.name)
                            typemap[gykud__ekw.func.name] = qmdl__ngb
                            calltypes[gykud__ekw] = ckdsm__kllmq
                            break
                        except Exception as gsee__qhq:
                            pass
                    if ckdsm__kllmq is None:
                        raise TypeError(
                            f'No valid template found for {gykud__ekw.func.name}'
                            )
                    gykud__ekw.args = [etvg__krwmb] + gykud__ekw.args
            rnif__rgko.append(stmt)
        block.body = rnif__rgko


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    nthb__nsf = ufunc.nin
    kpi__anylc = ufunc.nout
    fqhjg__ejo = ufunc.nargs
    assert fqhjg__ejo == nthb__nsf + kpi__anylc
    if len(args) < nthb__nsf:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), nthb__nsf))
    if len(args) > fqhjg__ejo:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), fqhjg__ejo)
            )
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    wyl__mfmrv = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    grwfv__gnurf = max(wyl__mfmrv)
    rfy__pqna = args[nthb__nsf:]
    if not all(d == grwfv__gnurf for d in wyl__mfmrv[nthb__nsf:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(wgg__pqg, types.ArrayCompatible) and not
        isinstance(wgg__pqg, types.Bytes) for wgg__pqg in rfy__pqna):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(wgg__pqg.mutable for wgg__pqg in rfy__pqna):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    tbd__tima = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    cgj__gkrt = None
    if grwfv__gnurf > 0 and len(rfy__pqna) < ufunc.nout:
        cgj__gkrt = 'C'
        kvhh__jbi = [(x.layout if isinstance(x, types.ArrayCompatible) and 
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in kvhh__jbi and 'F' in kvhh__jbi:
            cgj__gkrt = 'F'
    return tbd__tima, rfy__pqna, grwfv__gnurf, cgj__gkrt


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
        bczo__ypwb = 'Dict.key_type cannot be of type {}'
        raise TypingError(bczo__ypwb.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        bczo__ypwb = 'Dict.value_type cannot be of type {}'
        raise TypingError(bczo__ypwb.format(valty))
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
    for i, a in enumerate(args, start=1):
        if isinstance(a, types.Dispatcher):
            msg = (
                'Does not support function type inputs into with-context for arg {}'
                )
            raise errors.TypingError(msg.format(i))


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.ObjModeLiftedWith.
        _legalize_arg_types)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4793f44ebc7da8843e8f298e08cd8a5428b4b84b89fd9d5c650273fdb8fee5ee':
        warnings.warn('ObjModeLiftedWith._legalize_arg_types has changed')
numba.core.dispatcher.ObjModeLiftedWith._legalize_arg_types = (
    _legalize_arg_types)


def _overload_template_get_impl(self, args, kws):
    saseb__vtoi = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[saseb__vtoi]
        return impl, args
    except KeyError as gsee__qhq:
        pass
    impl, args = self._build_impl(saseb__vtoi, args, kws)
    return impl, args


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
        quo__pxxc = find_topo_order(parfor.loop_body)
    lhlds__ntxhr = quo__pxxc[0]
    kjosv__ofw = {}
    _update_parfor_get_setitems(parfor.loop_body[lhlds__ntxhr].body, parfor
        .index_var, alias_map, kjosv__ofw, lives_n_aliases)
    kolr__ntx = set(kjosv__ofw.keys())
    for has__apyw in quo__pxxc:
        if has__apyw == lhlds__ntxhr:
            continue
        for stmt in parfor.loop_body[has__apyw].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            itini__vosq = set(fjv__wca.name for fjv__wca in stmt.list_vars())
            lkosv__uiky = itini__vosq & kolr__ntx
            for a in lkosv__uiky:
                kjosv__ofw.pop(a, None)
    for has__apyw in quo__pxxc:
        if has__apyw == lhlds__ntxhr:
            continue
        block = parfor.loop_body[has__apyw]
        zcv__fpqmv = kjosv__ofw.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            zcv__fpqmv, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    mgla__lxmg = max(blocks.keys())
    rqji__rgzlf, nerv__cazsn = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    htfrg__qyj = ir.Jump(rqji__rgzlf, ir.Loc('parfors_dummy', -1))
    blocks[mgla__lxmg].body.append(htfrg__qyj)
    tgybf__aqizp = compute_cfg_from_blocks(blocks)
    bxef__nmia = compute_use_defs(blocks)
    yidhs__fiby = compute_live_map(tgybf__aqizp, blocks, bxef__nmia.usemap,
        bxef__nmia.defmap)
    alias_set = set(alias_map.keys())
    for kls__qvxdo, block in blocks.items():
        rnif__rgko = []
        lxj__soox = {fjv__wca.name for fjv__wca in block.terminator.list_vars()
            }
        for giz__elg, rkyxq__futoy in tgybf__aqizp.successors(kls__qvxdo):
            lxj__soox |= yidhs__fiby[giz__elg]
        for stmt in reversed(block.body):
            lyye__rhi = lxj__soox & alias_set
            for fjv__wca in lyye__rhi:
                lxj__soox |= alias_map[fjv__wca]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in lxj__soox and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                qzq__liiwi = guard(find_callname, func_ir, stmt.value)
                if qzq__liiwi == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in lxj__soox and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            lxj__soox |= {fjv__wca.name for fjv__wca in stmt.list_vars()}
            rnif__rgko.append(stmt)
        rnif__rgko.reverse()
        block.body = rnif__rgko
    typemap.pop(nerv__cazsn.name)
    blocks[mgla__lxmg].body.pop()

    def trim_empty_parfor_branches(parfor):
        lljuz__xuo = False
        blocks = parfor.loop_body.copy()
        for kls__qvxdo, block in blocks.items():
            if len(block.body):
                gpsj__rtuio = block.body[-1]
                if isinstance(gpsj__rtuio, ir.Branch):
                    if len(blocks[gpsj__rtuio.truebr].body) == 1 and len(blocks
                        [gpsj__rtuio.falsebr].body) == 1:
                        ssh__elaxz = blocks[gpsj__rtuio.truebr].body[0]
                        zrzum__aox = blocks[gpsj__rtuio.falsebr].body[0]
                        if isinstance(ssh__elaxz, ir.Jump) and isinstance(
                            zrzum__aox, ir.Jump
                            ) and ssh__elaxz.target == zrzum__aox.target:
                            parfor.loop_body[kls__qvxdo].body[-1] = ir.Jump(
                                ssh__elaxz.target, gpsj__rtuio.loc)
                            lljuz__xuo = True
                    elif len(blocks[gpsj__rtuio.truebr].body) == 1:
                        ssh__elaxz = blocks[gpsj__rtuio.truebr].body[0]
                        if isinstance(ssh__elaxz, ir.Jump
                            ) and ssh__elaxz.target == gpsj__rtuio.falsebr:
                            parfor.loop_body[kls__qvxdo].body[-1] = ir.Jump(
                                ssh__elaxz.target, gpsj__rtuio.loc)
                            lljuz__xuo = True
                    elif len(blocks[gpsj__rtuio.falsebr].body) == 1:
                        zrzum__aox = blocks[gpsj__rtuio.falsebr].body[0]
                        if isinstance(zrzum__aox, ir.Jump
                            ) and zrzum__aox.target == gpsj__rtuio.truebr:
                            parfor.loop_body[kls__qvxdo].body[-1] = ir.Jump(
                                zrzum__aox.target, gpsj__rtuio.loc)
                            lljuz__xuo = True
        return lljuz__xuo
    lljuz__xuo = True
    while lljuz__xuo:
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
        lljuz__xuo = trim_empty_parfor_branches(parfor)
    jtdr__hkltc = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        jtdr__hkltc &= len(block.body) == 0
    if jtdr__hkltc:
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
    dqbkg__gml = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                dqbkg__gml += 1
                parfor = stmt
                fzvx__svi = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = fzvx__svi.scope
                loc = ir.Loc('parfors_dummy', -1)
                oqyz__cmlkc = ir.Var(scope, mk_unique_var('$const'), loc)
                fzvx__svi.body.append(ir.Assign(ir.Const(0, loc),
                    oqyz__cmlkc, loc))
                fzvx__svi.body.append(ir.Return(oqyz__cmlkc, loc))
                tgybf__aqizp = compute_cfg_from_blocks(parfor.loop_body)
                for jrch__jcq in tgybf__aqizp.dead_nodes():
                    del parfor.loop_body[jrch__jcq]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                fzvx__svi = parfor.loop_body[max(parfor.loop_body.keys())]
                fzvx__svi.body.pop()
                fzvx__svi.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return dqbkg__gml


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
            jnwf__snbjz = self.overloads.get(tuple(args))
            if jnwf__snbjz is not None:
                return jnwf__snbjz.entry_point
            self._pre_compile(args, return_type, flags)
            ympf__eav = self.func_ir
            byv__dab = dict(dispatcher=self, args=args, return_type=return_type
                )
            with ev.trigger_event('numba:compile', data=byv__dab):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=ympf__eav, args=args,
                    return_type=return_type, flags=flags, locals=self.
                    locals, lifted=(), lifted_from=self.lifted_from,
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
        qsgsw__baw = copy.deepcopy(flags)
        qsgsw__baw.no_rewrites = True

        def compile_local(the_ir, the_flags):
            utrlu__fedu = pipeline_class(typingctx, targetctx, library,
                args, return_type, the_flags, locals)
            return utrlu__fedu.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        xkeb__cqqk = compile_local(func_ir, qsgsw__baw)
        uqla__hoyu = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    uqla__hoyu = compile_local(func_ir, flags)
                except Exception as gsee__qhq:
                    pass
        if uqla__hoyu is not None:
            cres = uqla__hoyu
        else:
            cres = xkeb__cqqk
        return cres
    else:
        utrlu__fedu = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return utrlu__fedu.compile_ir(func_ir=func_ir, lifted=lifted,
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
    mekn__jue = self.get_data_type(typ.dtype)
    wcwfu__ttc = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        wcwfu__ttc):
        jlh__riob = ary.ctypes.data
        cwm__virs = self.add_dynamic_addr(builder, jlh__riob, info=str(type
            (jlh__riob)))
        hlz__gwye = self.add_dynamic_addr(builder, id(ary), info=str(type(ary))
            )
        self.global_arrays.append(ary)
    else:
        uka__tisda = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            uka__tisda = uka__tisda.view('int64')
        val = bytearray(uka__tisda.data)
        hsv__tldjp = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)), val)
        cwm__virs = cgutils.global_constant(builder, '.const.array.data',
            hsv__tldjp)
        cwm__virs.align = self.get_abi_alignment(mekn__jue)
        hlz__gwye = None
    nddu__itp = self.get_value_type(types.intp)
    gmhpc__berd = [self.get_constant(types.intp, dtutm__ifl) for dtutm__ifl in
        ary.shape]
    nsoz__tpbr = lir.Constant(lir.ArrayType(nddu__itp, len(gmhpc__berd)),
        gmhpc__berd)
    xym__eni = [self.get_constant(types.intp, dtutm__ifl) for dtutm__ifl in
        ary.strides]
    gok__tsp = lir.Constant(lir.ArrayType(nddu__itp, len(xym__eni)), xym__eni)
    dem__uoea = self.get_constant(types.intp, ary.dtype.itemsize)
    oegb__abm = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        oegb__abm, dem__uoea, cwm__virs.bitcast(self.get_value_type(types.
        CPointer(typ.dtype))), nsoz__tpbr, gok__tsp])


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
    jlaqg__dracv = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    pqpfp__bbct = lir.Function(module, jlaqg__dracv, name='nrt_atomic_{0}'.
        format(op))
    [fwl__hkikt] = pqpfp__bbct.args
    mfie__bdybp = pqpfp__bbct.append_basic_block()
    builder = lir.IRBuilder(mfie__bdybp)
    klgdh__pxfxg = lir.Constant(_word_type, 1)
    if False:
        dotoi__zbdw = builder.atomic_rmw(op, fwl__hkikt, klgdh__pxfxg,
            ordering=ordering)
        res = getattr(builder, op)(dotoi__zbdw, klgdh__pxfxg)
        builder.ret(res)
    else:
        dotoi__zbdw = builder.load(fwl__hkikt)
        qjie__dag = getattr(builder, op)(dotoi__zbdw, klgdh__pxfxg)
        tmqx__lfy = builder.icmp_signed('!=', dotoi__zbdw, lir.Constant(
            dotoi__zbdw.type, -1))
        with cgutils.if_likely(builder, tmqx__lfy):
            builder.store(qjie__dag, fwl__hkikt)
        builder.ret(qjie__dag)
    return pqpfp__bbct


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
        sitl__gdg = state.targetctx.codegen()
        state.library = sitl__gdg.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    ticzp__idta = state.func_ir
    typemap = state.typemap
    cuj__pact = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    cqsh__lfbxm = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            ticzp__idta, typemap, cuj__pact, calltypes, mangler=targetctx.
            mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            ubbuf__yxzxa = lowering.Lower(targetctx, library, fndesc,
                ticzp__idta, metadata=metadata)
            ubbuf__yxzxa.lower()
            if not flags.no_cpython_wrapper:
                ubbuf__yxzxa.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(cuj__pact, (types.Optional, types.Generator)
                        ):
                        pass
                    else:
                        ubbuf__yxzxa.create_cfunc_wrapper()
            env = ubbuf__yxzxa.env
            ibbrp__tetkf = ubbuf__yxzxa.call_helper
            del ubbuf__yxzxa
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, ibbrp__tetkf, cfunc=None,
                env=env)
        else:
            omy__vmlb = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(omy__vmlb, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, ibbrp__tetkf, cfunc=
                omy__vmlb, env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        jvx__ouyn = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = jvx__ouyn - cqsh__lfbxm
        metadata['llvm_pass_timings'] = library.recorded_timings
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
        ucvbe__pufw = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, ucvbe__pufw),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            igp__drnui.do_break()
        vsh__xskkk = c.builder.icmp_signed('!=', ucvbe__pufw, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(vsh__xskkk, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, ucvbe__pufw)
                c.pyapi.decref(ucvbe__pufw)
                igp__drnui.do_break()
        c.pyapi.decref(ucvbe__pufw)
    nofyw__uyx, list = listobj.ListInstance.allocate_ex(c.context, c.
        builder, typ, size)
    with c.builder.if_else(nofyw__uyx, likely=True) as (kjwe__mzv, neobs__jzqp
        ):
        with kjwe__mzv:
            list.size = size
            kyc__llqa = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                kyc__llqa), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        kyc__llqa))
                    with cgutils.for_range(c.builder, size) as igp__drnui:
                        itemobj = c.pyapi.list_getitem(obj, igp__drnui.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        bky__uhdxt = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(bky__uhdxt.is_error, likely=
                            False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            igp__drnui.do_break()
                        list.setitem(igp__drnui.index, bky__uhdxt.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with neobs__jzqp:
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
    hfsd__zdbfh, bfyx__tgbzw, dgtmk__uie, ysex__sxz, zmv__mlq = (
        compile_time_get_string_data(literal_string))
    atew__bjx = builder.module
    gv = context.insert_const_bytes(atew__bjx, hfsd__zdbfh)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        bfyx__tgbzw), context.get_constant(types.int32, dgtmk__uie),
        context.get_constant(types.uint32, ysex__sxz), context.get_constant
        (_Py_hash_t, -1), context.get_constant_null(types.MemInfoPointer(
        types.voidptr)), context.get_constant_null(types.pyobject)])


if _check_numba_change:
    lines = inspect.getsource(numba.cpython.unicode.make_string_from_constant)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '525bd507383e06152763e2f046dae246cd60aba027184f50ef0fc9a80d4cd7fa':
        warnings.warn(
            'numba.cpython.unicode.make_string_from_constant has changed')
numba.cpython.unicode.make_string_from_constant = make_string_from_constant


def parse_shape(shape):
    eyl__pcm = None
    if isinstance(shape, types.Integer):
        eyl__pcm = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(dtutm__ifl, (types.Integer, types.IntEnumMember)) for
            dtutm__ifl in shape):
            eyl__pcm = len(shape)
    return eyl__pcm


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
            eyl__pcm = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if eyl__pcm == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(eyl__pcm))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            jhzs__mku = self._get_names(x)
            if len(jhzs__mku) != 0:
                return jhzs__mku[0]
            return jhzs__mku
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    jhzs__mku = self._get_names(obj)
    if len(jhzs__mku) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(jhzs__mku[0])


def get_equiv_set(self, obj):
    jhzs__mku = self._get_names(obj)
    if len(jhzs__mku) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(jhzs__mku[0])


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
    kxzfe__obd = []
    for diptd__hfknl in func_ir.arg_names:
        if diptd__hfknl in typemap and isinstance(typemap[diptd__hfknl],
            types.containers.UniTuple) and typemap[diptd__hfknl].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(diptd__hfknl))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for tzb__pgbmv in func_ir.blocks.values():
        for stmt in tzb__pgbmv.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    gfk__yzx = getattr(val, 'code', None)
                    if gfk__yzx is not None:
                        if getattr(val, 'closure', None) is not None:
                            hzt__aqh = '<creating a function from a closure>'
                            dph__ozn = ''
                        else:
                            hzt__aqh = gfk__yzx.co_name
                            dph__ozn = '(%s) ' % hzt__aqh
                    else:
                        hzt__aqh = '<could not ascertain use case>'
                        dph__ozn = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (hzt__aqh, dph__ozn))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                bxy__hejm = False
                if isinstance(val, pytypes.FunctionType):
                    bxy__hejm = val in {numba.gdb, numba.gdb_init}
                if not bxy__hejm:
                    bxy__hejm = getattr(val, '_name', '') == 'gdb_internal'
                if bxy__hejm:
                    kxzfe__obd.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    bygar__dsr = func_ir.get_definition(var)
                    gbsw__udxbc = guard(find_callname, func_ir, bygar__dsr)
                    if gbsw__udxbc and gbsw__udxbc[1] == 'numpy':
                        ty = getattr(numpy, gbsw__udxbc[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    ldi__eqrt = '' if var.startswith('$') else "'{}' ".format(
                        var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(ldi__eqrt), loc=stmt.loc)
            if isinstance(stmt.value, ir.Global):
                ty = typemap[stmt.target.name]
                msg = (
                    "The use of a %s type, assigned to variable '%s' in globals, is not supported as globals are considered compile-time constants and there is no known way to compile a %s type as a constant."
                    )
                if isinstance(ty, types.ListType):
                    raise TypingError(msg % (ty, stmt.value.name, ty), loc=
                        stmt.loc)
            if isinstance(stmt.value, ir.Yield) and not func_ir.is_generator:
                msg = 'The use of generator expressions is unsupported.'
                raise errors.UnsupportedError(msg, loc=stmt.loc)
    if len(kxzfe__obd) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        kxuxy__kaaet = '\n'.join([x.strformat() for x in kxzfe__obd])
        raise errors.UnsupportedError(msg % kxuxy__kaaet)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.raise_on_unsupported_feature)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '237a4fe8395a40899279c718bc3754102cd2577463ef2f48daceea78d79b2d5e':
        warnings.warn(
            'numba.core.ir_utils.raise_on_unsupported_feature has changed')
numba.core.ir_utils.raise_on_unsupported_feature = raise_on_unsupported_feature
numba.core.typed_passes.raise_on_unsupported_feature = (
    raise_on_unsupported_feature)


@typeof_impl.register(dict)
def _typeof_dict(val, c):
    if len(val) == 0:
        raise ValueError('Cannot type empty dict')
    nealf__llt, fjv__wca = next(iter(val.items()))
    svy__hipux = typeof_impl(nealf__llt, c)
    ouoox__xmt = typeof_impl(fjv__wca, c)
    if svy__hipux is None or ouoox__xmt is None:
        raise ValueError(
            f'Cannot type dict element type {type(nealf__llt)}, {type(fjv__wca)}'
            )
    return types.DictType(svy__hipux, ouoox__xmt)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    tgl__kgxr = cgutils.alloca_once_value(c.builder, val)
    tsoo__aau = c.pyapi.object_hasattr_string(val, '_opaque')
    pgduv__jcs = c.builder.icmp_unsigned('==', tsoo__aau, lir.Constant(
        tsoo__aau.type, 0))
    jyi__lwli = typ.key_type
    qoi__ukww = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(jyi__lwli, qoi__ukww)

    def copy_dict(out_dict, in_dict):
        for nealf__llt, fjv__wca in in_dict.items():
            out_dict[nealf__llt] = fjv__wca
    with c.builder.if_then(pgduv__jcs):
        pua__jnpp = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        hvqgs__tue = c.pyapi.call_function_objargs(pua__jnpp, [])
        zxdg__yib = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(zxdg__yib, [hvqgs__tue, val])
        c.builder.store(hvqgs__tue, tgl__kgxr)
    val = c.builder.load(tgl__kgxr)
    jxb__jakxu = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    wpue__dkt = c.pyapi.object_type(val)
    ihg__nekq = c.builder.icmp_unsigned('==', wpue__dkt, jxb__jakxu)
    with c.builder.if_else(ihg__nekq) as (ibgs__ciwio, qewc__aam):
        with ibgs__ciwio:
            ljfz__zfbc = c.pyapi.object_getattr_string(val, '_opaque')
            lsp__otn = types.MemInfoPointer(types.voidptr)
            bky__uhdxt = c.unbox(lsp__otn, ljfz__zfbc)
            mi = bky__uhdxt.value
            jdevi__xlvu = lsp__otn, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *jdevi__xlvu)
            vwi__vfuk = context.get_constant_null(jdevi__xlvu[1])
            args = mi, vwi__vfuk
            kqlyr__woip, tftg__fnxev = c.pyapi.call_jit_code(convert, sig, args
                )
            c.context.nrt.decref(c.builder, typ, tftg__fnxev)
            c.pyapi.decref(ljfz__zfbc)
            bxwj__skso = c.builder.basic_block
        with qewc__aam:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", wpue__dkt, jxb__jakxu)
            nvh__hbc = c.builder.basic_block
    uolip__nqkel = c.builder.phi(tftg__fnxev.type)
    ywyr__ittg = c.builder.phi(kqlyr__woip.type)
    uolip__nqkel.add_incoming(tftg__fnxev, bxwj__skso)
    uolip__nqkel.add_incoming(tftg__fnxev.type(None), nvh__hbc)
    ywyr__ittg.add_incoming(kqlyr__woip, bxwj__skso)
    ywyr__ittg.add_incoming(cgutils.true_bit, nvh__hbc)
    c.pyapi.decref(jxb__jakxu)
    c.pyapi.decref(wpue__dkt)
    with c.builder.if_then(pgduv__jcs):
        c.pyapi.decref(val)
    return NativeValue(uolip__nqkel, is_error=ywyr__ittg)


import numba.typed.typeddict
if _check_numba_change:
    lines = inspect.getsource(numba.core.pythonapi._unboxers.functions[
        numba.core.types.DictType])
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5f6f183b94dc57838538c668a54c2476576c85d8553843f3219f5162c61e7816':
        warnings.warn('unbox_dicttype has changed')
numba.core.pythonapi._unboxers.functions[types.DictType] = unbox_dicttype


def op_DICT_UPDATE_byteflow(self, state, inst):
    value = state.pop()
    index = inst.arg
    target = state.peek(index)
    updatevar = state.make_temp()
    res = state.make_temp()
    state.append(inst, target=target, value=value, updatevar=updatevar, res=res
        )


if _check_numba_change:
    if hasattr(numba.core.byteflow.TraceRunner, 'op_DICT_UPDATE'):
        warnings.warn(
            'numba.core.byteflow.TraceRunner.op_DICT_UPDATE has changed')
numba.core.byteflow.TraceRunner.op_DICT_UPDATE = op_DICT_UPDATE_byteflow


def op_DICT_UPDATE_interpreter(self, inst, target, value, updatevar, res):
    from numba.core import ir
    target = self.get(target)
    value = self.get(value)
    xuxu__sdw = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=xuxu__sdw, name=updatevar)
    dbjgn__ckrrj = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc
        )
    self.store(value=dbjgn__ckrrj, name=res)


if _check_numba_change:
    if hasattr(numba.core.interpreter.Interpreter, 'op_DICT_UPDATE'):
        warnings.warn(
            'numba.core.interpreter.Interpreter.op_DICT_UPDATE has changed')
numba.core.interpreter.Interpreter.op_DICT_UPDATE = op_DICT_UPDATE_interpreter


@numba.extending.overload_method(numba.core.types.DictType, 'update')
def ol_dict_update(d, other):
    if not isinstance(d, numba.core.types.DictType):
        return
    if not isinstance(other, numba.core.types.DictType):
        return

    def impl(d, other):
        for nealf__llt, fjv__wca in other.items():
            d[nealf__llt] = fjv__wca
    return impl


if _check_numba_change:
    if hasattr(numba.core.interpreter.Interpreter, 'ol_dict_update'):
        warnings.warn('numba.typed.dictobject.ol_dict_update has changed')


def op_CALL_FUNCTION_EX_byteflow(self, state, inst):
    from numba.core.utils import PYVERSION
    if inst.arg & 1 and PYVERSION != (3, 10):
        errmsg = 'CALL_FUNCTION_EX with **kwargs not supported'
        raise errors.UnsupportedError(errmsg)
    if inst.arg & 1:
        varkwarg = state.pop()
    else:
        varkwarg = None
    vararg = state.pop()
    func = state.pop()
    res = state.make_temp()
    state.append(inst, func=func, vararg=vararg, varkwarg=varkwarg, res=res)
    state.push(res)


if _check_numba_change:
    lines = inspect.getsource(numba.core.byteflow.TraceRunner.
        op_CALL_FUNCTION_EX)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '349e7cfd27f5dab80fe15a7728c5f098f3f225ba8512d84331e39d01e863c6d4':
        warnings.warn(
            'numba.core.byteflow.TraceRunner.op_CALL_FUNCTION_EX has changed')
numba.core.byteflow.TraceRunner.op_CALL_FUNCTION_EX = (
    op_CALL_FUNCTION_EX_byteflow)


def op_CALL_FUNCTION_EX_interpreter(self, inst, func, vararg, varkwarg, res):
    func = self.get(func)
    vararg = self.get(vararg)
    if varkwarg is not None:
        varkwarg = self.get(varkwarg)
    dph__ozn = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(dph__ozn, res)


if _check_numba_change:
    lines = inspect.getsource(numba.core.interpreter.Interpreter.
        op_CALL_FUNCTION_EX)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '84846e5318ab7ccc8f9abaae6ab9e0ca879362648196f9d4b0ffb91cf2e01f5d':
        warnings.warn(
            'numba.core.interpreter.Interpreter.op_CALL_FUNCTION_EX has changed'
            )
numba.core.interpreter.Interpreter.op_CALL_FUNCTION_EX = (
    op_CALL_FUNCTION_EX_interpreter)


@classmethod
def ir_expr_call(cls, func, args, kws, loc, vararg=None, varkwarg=None,
    target=None):
    assert isinstance(func, ir.Var)
    assert isinstance(loc, ir.Loc)
    op = 'call'
    return cls(op=op, loc=loc, func=func, args=args, kws=kws, vararg=vararg,
        varkwarg=varkwarg, target=target)


if _check_numba_change:
    lines = inspect.getsource(ir.Expr.call)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '665601d0548d4f648d454492e542cb8aa241107a8df6bc68d0eec664c9ada738':
        warnings.warn('ir.Expr.call has changed')
ir.Expr.call = ir_expr_call


@staticmethod
def define_untyped_pipeline(state, name='untyped'):
    from numba.core.compiler_machinery import PassManager
    from numba.core.untyped_passes import DeadBranchPrune, FindLiterallyCalls, FixupArgs, GenericRewrites, InlineClosureLikes, InlineInlinables, IRProcessing, LiteralPropagationSubPipelinePass, LiteralUnroll, MakeFunctionToJitFunction, ReconstructSSA, RewriteSemanticConstants, TranslateByteCode, WithLifting
    from numba.core.utils import PYVERSION
    ebli__karn = PassManager(name)
    if state.func_ir is None:
        ebli__karn.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            ebli__karn.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        ebli__karn.add_pass(FixupArgs, 'fix up args')
    ebli__karn.add_pass(IRProcessing, 'processing IR')
    ebli__karn.add_pass(WithLifting, 'Handle with contexts')
    ebli__karn.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        ebli__karn.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        ebli__karn.add_pass(DeadBranchPrune, 'dead branch pruning')
        ebli__karn.add_pass(GenericRewrites, 'nopython rewrites')
    ebli__karn.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    ebli__karn.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        ebli__karn.add_pass(DeadBranchPrune, 'dead branch pruning')
    ebli__karn.add_pass(FindLiterallyCalls, 'find literally calls')
    ebli__karn.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        ebli__karn.add_pass(ReconstructSSA, 'ssa')
    ebli__karn.add_pass(LiteralPropagationSubPipelinePass,
        'Literal propagation')
    ebli__karn.finalize()
    return ebli__karn


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fc5a0665658cc30588a78aca984ac2d323d5d3a45dce538cc62688530c772896':
        warnings.warn(
            'numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline has changed'
            )
numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline = (
    define_untyped_pipeline)


def mul_list_generic(self, args, kws):
    a, uyqlx__jzip = args
    if isinstance(a, types.List) and isinstance(uyqlx__jzip, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(uyqlx__jzip, types.List):
        return signature(uyqlx__jzip, types.intp, uyqlx__jzip)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.listdecl.MulList.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '95882385a8ffa67aa576e8169b9ee6b3197e0ad3d5def4b47fa65ce8cd0f1575':
        warnings.warn('numba.core.typing.listdecl.MulList.generic has changed')
numba.core.typing.listdecl.MulList.generic = mul_list_generic


@lower_builtin(operator.mul, types.Integer, types.List)
def list_mul(context, builder, sig, args):
    from llvmlite import ir as lir
    from numba.core.imputils import impl_ret_new_ref
    from numba.cpython.listobj import ListInstance
    if isinstance(sig.args[0], types.List):
        kbje__wuzw, uch__zxvq = 0, 1
    else:
        kbje__wuzw, uch__zxvq = 1, 0
    pkmlw__nico = ListInstance(context, builder, sig.args[kbje__wuzw], args
        [kbje__wuzw])
    dzl__xnp = pkmlw__nico.size
    zhrm__bjr = args[uch__zxvq]
    kyc__llqa = lir.Constant(zhrm__bjr.type, 0)
    zhrm__bjr = builder.select(cgutils.is_neg_int(builder, zhrm__bjr),
        kyc__llqa, zhrm__bjr)
    oegb__abm = builder.mul(zhrm__bjr, dzl__xnp)
    obxoc__czk = ListInstance.allocate(context, builder, sig.return_type,
        oegb__abm)
    obxoc__czk.size = oegb__abm
    with cgutils.for_range_slice(builder, kyc__llqa, oegb__abm, dzl__xnp,
        inc=True) as (nxhnp__bqyla, _):
        with cgutils.for_range(builder, dzl__xnp) as igp__drnui:
            value = pkmlw__nico.getitem(igp__drnui.index)
            obxoc__czk.setitem(builder.add(igp__drnui.index, nxhnp__bqyla),
                value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, obxoc__czk.value
        )


def unify_pairs(self, first, second):
    from numba.core.typeconv import Conversion
    if first == second:
        return first
    if first is types.undefined:
        return second
    elif second is types.undefined:
        return first
    if first is types.unknown or second is types.unknown:
        return types.unknown
    sfph__jdo = first.unify(self, second)
    if sfph__jdo is not None:
        return sfph__jdo
    sfph__jdo = second.unify(self, first)
    if sfph__jdo is not None:
        return sfph__jdo
    hurf__bdv = self.can_convert(fromty=first, toty=second)
    if hurf__bdv is not None and hurf__bdv <= Conversion.safe:
        return second
    hurf__bdv = self.can_convert(fromty=second, toty=first)
    if hurf__bdv is not None and hurf__bdv <= Conversion.safe:
        return first
    if isinstance(first, types.Literal) or isinstance(second, types.Literal):
        first = types.unliteral(first)
        second = types.unliteral(second)
        return self.unify_pairs(first, second)
    return None


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.context.BaseContext.unify_pairs
        )
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f0eaf4cfdf1537691de26efd24d7e320f7c3f10d35e9aefe70cb946b3be0008c':
        warnings.warn(
            'numba.core.typing.context.BaseContext.unify_pairs has changed')
numba.core.typing.context.BaseContext.unify_pairs = unify_pairs


def _native_set_to_python_list(typ, payload, c):
    from llvmlite import ir
    oegb__abm = payload.used
    listobj = c.pyapi.list_new(oegb__abm)
    nofyw__uyx = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(nofyw__uyx, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(oegb__abm.
            type, 0))
        with payload._iterate() as igp__drnui:
            i = c.builder.load(index)
            item = igp__drnui.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return nofyw__uyx, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    xpar__ayl = h.type
    uaw__fuju = self.mask
    dtype = self._ty.dtype
    ifpl__fgn = context.typing_context
    fnty = ifpl__fgn.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(ifpl__fgn, (dtype, dtype), {})
    hbjcv__kpfj = context.get_function(fnty, sig)
    desg__ilyp = ir.Constant(xpar__ayl, 1)
    wzv__piouu = ir.Constant(xpar__ayl, 5)
    kgsrr__kgde = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, uaw__fuju))
    if for_insert:
        dia__mkscp = uaw__fuju.type(-1)
        nhq__dhuz = cgutils.alloca_once_value(builder, dia__mkscp)
    rvogk__buvkj = builder.append_basic_block('lookup.body')
    tfm__wmvnm = builder.append_basic_block('lookup.found')
    vjwr__pnjq = builder.append_basic_block('lookup.not_found')
    yce__suez = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        cmiwg__hti = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, cmiwg__hti)):
            hfxbz__fdei = hbjcv__kpfj(builder, (item, entry.key))
            with builder.if_then(hfxbz__fdei):
                builder.branch(tfm__wmvnm)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, cmiwg__hti)):
            builder.branch(vjwr__pnjq)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, cmiwg__hti)):
                grtpr__nae = builder.load(nhq__dhuz)
                grtpr__nae = builder.select(builder.icmp_unsigned('==',
                    grtpr__nae, dia__mkscp), i, grtpr__nae)
                builder.store(grtpr__nae, nhq__dhuz)
    with cgutils.for_range(builder, ir.Constant(xpar__ayl, numba.cpython.
        setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, desg__ilyp)
        i = builder.and_(i, uaw__fuju)
        builder.store(i, index)
    builder.branch(rvogk__buvkj)
    with builder.goto_block(rvogk__buvkj):
        i = builder.load(index)
        check_entry(i)
        kadoh__wnqpb = builder.load(kgsrr__kgde)
        kadoh__wnqpb = builder.lshr(kadoh__wnqpb, wzv__piouu)
        i = builder.add(desg__ilyp, builder.mul(i, wzv__piouu))
        i = builder.and_(uaw__fuju, builder.add(i, kadoh__wnqpb))
        builder.store(i, index)
        builder.store(kadoh__wnqpb, kgsrr__kgde)
        builder.branch(rvogk__buvkj)
    with builder.goto_block(vjwr__pnjq):
        if for_insert:
            i = builder.load(index)
            grtpr__nae = builder.load(nhq__dhuz)
            i = builder.select(builder.icmp_unsigned('==', grtpr__nae,
                dia__mkscp), i, grtpr__nae)
            builder.store(i, index)
        builder.branch(yce__suez)
    with builder.goto_block(tfm__wmvnm):
        builder.branch(yce__suez)
    builder.position_at_end(yce__suez)
    bxy__hejm = builder.phi(ir.IntType(1), 'found')
    bxy__hejm.add_incoming(cgutils.true_bit, tfm__wmvnm)
    bxy__hejm.add_incoming(cgutils.false_bit, vjwr__pnjq)
    return bxy__hejm, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    pdfnu__yzi = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    ztc__hhyg = payload.used
    desg__ilyp = ir.Constant(ztc__hhyg.type, 1)
    ztc__hhyg = payload.used = builder.add(ztc__hhyg, desg__ilyp)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, pdfnu__yzi), likely=True):
        payload.fill = builder.add(payload.fill, desg__ilyp)
    if do_resize:
        self.upsize(ztc__hhyg)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    bxy__hejm, i = payload._lookup(item, h, for_insert=True)
    prho__hfch = builder.not_(bxy__hejm)
    with builder.if_then(prho__hfch):
        entry = payload.get_entry(i)
        pdfnu__yzi = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        ztc__hhyg = payload.used
        desg__ilyp = ir.Constant(ztc__hhyg.type, 1)
        ztc__hhyg = payload.used = builder.add(ztc__hhyg, desg__ilyp)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, pdfnu__yzi), likely=True):
            payload.fill = builder.add(payload.fill, desg__ilyp)
        if do_resize:
            self.upsize(ztc__hhyg)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    ztc__hhyg = payload.used
    desg__ilyp = ir.Constant(ztc__hhyg.type, 1)
    ztc__hhyg = payload.used = self._builder.sub(ztc__hhyg, desg__ilyp)
    if do_resize:
        self.downsize(ztc__hhyg)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    hyd__pyu = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, hyd__pyu)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    yyu__xwap = payload
    nofyw__uyx = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(nofyw__uyx), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with yyu__xwap._iterate() as igp__drnui:
        entry = igp__drnui.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(yyu__xwap.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as igp__drnui:
        entry = igp__drnui.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    nofyw__uyx = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(nofyw__uyx), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    nofyw__uyx = cgutils.alloca_once_value(builder, cgutils.true_bit)
    xpar__ayl = context.get_value_type(types.intp)
    kyc__llqa = ir.Constant(xpar__ayl, 0)
    desg__ilyp = ir.Constant(xpar__ayl, 1)
    uszln__fhb = context.get_data_type(types.SetPayload(self._ty))
    lcwhi__prx = context.get_abi_sizeof(uszln__fhb)
    qjlh__dzoh = self._entrysize
    lcwhi__prx -= qjlh__dzoh
    xet__wdx, tki__yoapo = cgutils.muladd_with_overflow(builder, nentries,
        ir.Constant(xpar__ayl, qjlh__dzoh), ir.Constant(xpar__ayl, lcwhi__prx))
    with builder.if_then(tki__yoapo, likely=False):
        builder.store(cgutils.false_bit, nofyw__uyx)
    with builder.if_then(builder.load(nofyw__uyx), likely=True):
        if realloc:
            cwkxk__vinem = self._set.meminfo
            fwl__hkikt = context.nrt.meminfo_varsize_alloc(builder,
                cwkxk__vinem, size=xet__wdx)
            ctzv__lfy = cgutils.is_null(builder, fwl__hkikt)
        else:
            djly__ncnjf = _imp_dtor(context, builder.module, self._ty)
            cwkxk__vinem = context.nrt.meminfo_new_varsize_dtor(builder,
                xet__wdx, builder.bitcast(djly__ncnjf, cgutils.voidptr_t))
            ctzv__lfy = cgutils.is_null(builder, cwkxk__vinem)
        with builder.if_else(ctzv__lfy, likely=False) as (jezo__nfq, kjwe__mzv
            ):
            with jezo__nfq:
                builder.store(cgutils.false_bit, nofyw__uyx)
            with kjwe__mzv:
                if not realloc:
                    self._set.meminfo = cwkxk__vinem
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, xet__wdx, 255)
                payload.used = kyc__llqa
                payload.fill = kyc__llqa
                payload.finger = kyc__llqa
                vaat__alz = builder.sub(nentries, desg__ilyp)
                payload.mask = vaat__alz
    return builder.load(nofyw__uyx)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    nofyw__uyx = cgutils.alloca_once_value(builder, cgutils.true_bit)
    xpar__ayl = context.get_value_type(types.intp)
    kyc__llqa = ir.Constant(xpar__ayl, 0)
    desg__ilyp = ir.Constant(xpar__ayl, 1)
    uszln__fhb = context.get_data_type(types.SetPayload(self._ty))
    lcwhi__prx = context.get_abi_sizeof(uszln__fhb)
    qjlh__dzoh = self._entrysize
    lcwhi__prx -= qjlh__dzoh
    uaw__fuju = src_payload.mask
    nentries = builder.add(desg__ilyp, uaw__fuju)
    xet__wdx = builder.add(ir.Constant(xpar__ayl, lcwhi__prx), builder.mul(
        ir.Constant(xpar__ayl, qjlh__dzoh), nentries))
    with builder.if_then(builder.load(nofyw__uyx), likely=True):
        djly__ncnjf = _imp_dtor(context, builder.module, self._ty)
        cwkxk__vinem = context.nrt.meminfo_new_varsize_dtor(builder,
            xet__wdx, builder.bitcast(djly__ncnjf, cgutils.voidptr_t))
        ctzv__lfy = cgutils.is_null(builder, cwkxk__vinem)
        with builder.if_else(ctzv__lfy, likely=False) as (jezo__nfq, kjwe__mzv
            ):
            with jezo__nfq:
                builder.store(cgutils.false_bit, nofyw__uyx)
            with kjwe__mzv:
                self._set.meminfo = cwkxk__vinem
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = kyc__llqa
                payload.mask = uaw__fuju
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, qjlh__dzoh)
                with src_payload._iterate() as igp__drnui:
                    context.nrt.incref(builder, self._ty.dtype, igp__drnui.
                        entry.key)
    return builder.load(nofyw__uyx)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    ioay__jyxt = context.get_value_type(types.voidptr)
    tvyuf__vfvra = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [ioay__jyxt, tvyuf__vfvra,
        ioay__jyxt])
    fun__bhpb = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=fun__bhpb)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        yjsgu__yhwba = builder.bitcast(fn.args[0], cgutils.voidptr_t.
            as_pointer())
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, yjsgu__yhwba)
        with payload._iterate() as igp__drnui:
            entry = igp__drnui.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    rctcf__tss, = sig.args
    wowu__fljqh, = args
    jmq__dyokj = numba.core.imputils.call_len(context, builder, rctcf__tss,
        wowu__fljqh)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, jmq__dyokj)
    with numba.core.imputils.for_iter(context, builder, rctcf__tss, wowu__fljqh
        ) as igp__drnui:
        inst.add(igp__drnui.value)
        context.nrt.decref(builder, set_type.dtype, igp__drnui.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    rctcf__tss = sig.args[1]
    wowu__fljqh = args[1]
    jmq__dyokj = numba.core.imputils.call_len(context, builder, rctcf__tss,
        wowu__fljqh)
    if jmq__dyokj is not None:
        rqubv__zio = builder.add(inst.payload.used, jmq__dyokj)
        inst.upsize(rqubv__zio)
    with numba.core.imputils.for_iter(context, builder, rctcf__tss, wowu__fljqh
        ) as igp__drnui:
        woqc__bdvg = context.cast(builder, igp__drnui.value, rctcf__tss.
            dtype, inst.dtype)
        inst.add(woqc__bdvg)
        context.nrt.decref(builder, rctcf__tss.dtype, igp__drnui.value)
    if jmq__dyokj is not None:
        inst.downsize(inst.payload.used)
    return context.get_dummy_value()


if _check_numba_change:
    for name, orig, hash in ((
        'numba.core.boxing._native_set_to_python_list', numba.core.boxing.
        _native_set_to_python_list,
        'b47f3d5e582c05d80899ee73e1c009a7e5121e7a660d42cb518bb86933f3c06f'),
        ('numba.cpython.setobj._SetPayload._lookup', numba.cpython.setobj.
        _SetPayload._lookup,
        'c797b5399d7b227fe4eea3a058b3d3103f59345699388afb125ae47124bee395'),
        ('numba.cpython.setobj.SetInstance._add_entry', numba.cpython.
        setobj.SetInstance._add_entry,
        'c5ed28a5fdb453f242e41907cb792b66da2df63282c17abe0b68fc46782a7f94'),
        ('numba.cpython.setobj.SetInstance._add_key', numba.cpython.setobj.
        SetInstance._add_key,
        '324d6172638d02a361cfa0ca7f86e241e5a56a008d4ab581a305f9ae5ea4a75f'),
        ('numba.cpython.setobj.SetInstance._remove_entry', numba.cpython.
        setobj.SetInstance._remove_entry,
        '2c441b00daac61976e673c0e738e8e76982669bd2851951890dd40526fa14da1'),
        ('numba.cpython.setobj.SetInstance.pop', numba.cpython.setobj.
        SetInstance.pop,
        '1a7b7464cbe0577f2a38f3af9acfef6d4d25d049b1e216157275fbadaab41d1b'),
        ('numba.cpython.setobj.SetInstance._resize', numba.cpython.setobj.
        SetInstance._resize,
        '5ca5c2ba4f8c4bf546fde106b9c2656d4b22a16d16e163fb64c5d85ea4d88746'),
        ('numba.cpython.setobj.SetInstance._replace_payload', numba.cpython
        .setobj.SetInstance._replace_payload,
        'ada75a6c85828bff69c8469538c1979801f560a43fb726221a9c21bf208ae78d'),
        ('numba.cpython.setobj.SetInstance._allocate_payload', numba.
        cpython.setobj.SetInstance._allocate_payload,
        '2e80c419df43ebc71075b4f97fc1701c10dbc576aed248845e176b8d5829e61b'),
        ('numba.cpython.setobj.SetInstance._copy_payload', numba.cpython.
        setobj.SetInstance._copy_payload,
        '0885ac36e1eb5a0a0fc4f5d91e54b2102b69e536091fed9f2610a71d225193ec'),
        ('numba.cpython.setobj.set_constructor', numba.cpython.setobj.
        set_constructor,
        '3d521a60c3b8eaf70aa0f7267427475dfddd8f5e5053b5bfe309bb5f1891b0ce'),
        ('numba.cpython.setobj.set_update', numba.cpython.setobj.set_update,
        '965c4f7f7abcea5cbe0491b602e6d4bcb1800fa1ec39b1ffccf07e1bc56051c3')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
        orig = new
numba.core.boxing._native_set_to_python_list = _native_set_to_python_list
numba.cpython.setobj._SetPayload._lookup = _lookup
numba.cpython.setobj.SetInstance._add_entry = _add_entry
numba.cpython.setobj.SetInstance._add_key = _add_key
numba.cpython.setobj.SetInstance._remove_entry = _remove_entry
numba.cpython.setobj.SetInstance.pop = pop
numba.cpython.setobj.SetInstance._resize = _resize
numba.cpython.setobj.SetInstance._replace_payload = _replace_payload
numba.cpython.setobj.SetInstance._allocate_payload = _allocate_payload
numba.cpython.setobj.SetInstance._copy_payload = _copy_payload


def _reduce(self):
    libdata = self.library.serialize_using_object_code()
    typeann = str(self.type_annotation)
    fndesc = self.fndesc
    fndesc.typemap = fndesc.calltypes = None
    referenced_envs = self._find_referenced_environments()
    pvnqb__pmd = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, pvnqb__pmd, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    omy__vmlb = target_context.get_executable(library, fndesc, env)
    hpx__arqat = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=omy__vmlb, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return hpx__arqat


if _check_numba_change:
    for name, orig, hash in (('numba.core.compiler.CompileResult._reduce',
        numba.core.compiler.CompileResult._reduce,
        '5f86eacfa5202c202b3dc200f1a7a9b6d3f9d1ec16d43a52cb2d580c34fbfa82'),
        ('numba.core.compiler.CompileResult._rebuild', numba.core.compiler.
        CompileResult._rebuild,
        '44fa9dc2255883ab49195d18c3cca8c0ad715d0dd02033bd7e2376152edc4e84')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
        orig = new
numba.core.compiler.CompileResult._reduce = _reduce
numba.core.compiler.CompileResult._rebuild = _rebuild


def _get_cache_path(self):
    return numba.config.CACHE_DIR


if _check_numba_change:
    if os.environ.get('BODO_PLATFORM_CACHE_LOCATION') is not None:
        numba.core.caching._IPythonCacheLocator.get_cache_path = (
            _get_cache_path)
