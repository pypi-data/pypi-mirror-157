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
    oztzi__yzn = numba.core.bytecode.FunctionIdentity.from_function(func)
    wxy__gmivs = numba.core.interpreter.Interpreter(oztzi__yzn)
    hhdi__sfpin = numba.core.bytecode.ByteCode(func_id=oztzi__yzn)
    func_ir = wxy__gmivs.interpret(hhdi__sfpin)
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
        krjha__uej = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        krjha__uej.run()
    spb__nav = numba.core.postproc.PostProcessor(func_ir)
    spb__nav.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, wgrm__zgnw in visit_vars_extensions.items():
        if isinstance(stmt, t):
            wgrm__zgnw(stmt, callback, cbdata)
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
    rjddt__zqb = ['ravel', 'transpose', 'reshape']
    for fnjl__ppa in blocks.values():
        for lpl__kanag in fnjl__ppa.body:
            if type(lpl__kanag) in alias_analysis_extensions:
                wgrm__zgnw = alias_analysis_extensions[type(lpl__kanag)]
                wgrm__zgnw(lpl__kanag, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(lpl__kanag, ir.Assign):
                myoc__rhwc = lpl__kanag.value
                jnb__qug = lpl__kanag.target.name
                if is_immutable_type(jnb__qug, typemap):
                    continue
                if isinstance(myoc__rhwc, ir.Var
                    ) and jnb__qug != myoc__rhwc.name:
                    _add_alias(jnb__qug, myoc__rhwc.name, alias_map,
                        arg_aliases)
                if isinstance(myoc__rhwc, ir.Expr) and (myoc__rhwc.op ==
                    'cast' or myoc__rhwc.op in ['getitem', 'static_getitem']):
                    _add_alias(jnb__qug, myoc__rhwc.value.name, alias_map,
                        arg_aliases)
                if isinstance(myoc__rhwc, ir.Expr
                    ) and myoc__rhwc.op == 'inplace_binop':
                    _add_alias(jnb__qug, myoc__rhwc.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(myoc__rhwc, ir.Expr
                    ) and myoc__rhwc.op == 'getattr' and myoc__rhwc.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(jnb__qug, myoc__rhwc.value.name, alias_map,
                        arg_aliases)
                if isinstance(myoc__rhwc, ir.Expr
                    ) and myoc__rhwc.op == 'getattr' and myoc__rhwc.attr not in [
                    'shape'] and myoc__rhwc.value.name in arg_aliases:
                    _add_alias(jnb__qug, myoc__rhwc.value.name, alias_map,
                        arg_aliases)
                if isinstance(myoc__rhwc, ir.Expr
                    ) and myoc__rhwc.op == 'getattr' and myoc__rhwc.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(jnb__qug, myoc__rhwc.value.name, alias_map,
                        arg_aliases)
                if isinstance(myoc__rhwc, ir.Expr) and myoc__rhwc.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(jnb__qug, typemap):
                    for cyunt__cjlx in myoc__rhwc.items:
                        _add_alias(jnb__qug, cyunt__cjlx.name, alias_map,
                            arg_aliases)
                if isinstance(myoc__rhwc, ir.Expr) and myoc__rhwc.op == 'call':
                    nps__nco = guard(find_callname, func_ir, myoc__rhwc,
                        typemap)
                    if nps__nco is None:
                        continue
                    tgjzk__louzy, pzsfo__uhj = nps__nco
                    if nps__nco in alias_func_extensions:
                        sml__jaf = alias_func_extensions[nps__nco]
                        sml__jaf(jnb__qug, myoc__rhwc.args, alias_map,
                            arg_aliases)
                    if pzsfo__uhj == 'numpy' and tgjzk__louzy in rjddt__zqb:
                        _add_alias(jnb__qug, myoc__rhwc.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(pzsfo__uhj, ir.Var
                        ) and tgjzk__louzy in rjddt__zqb:
                        _add_alias(jnb__qug, pzsfo__uhj.name, alias_map,
                            arg_aliases)
    kohb__rgze = copy.deepcopy(alias_map)
    for cyunt__cjlx in kohb__rgze:
        for arwzw__lgkfw in kohb__rgze[cyunt__cjlx]:
            alias_map[cyunt__cjlx] |= alias_map[arwzw__lgkfw]
        for arwzw__lgkfw in kohb__rgze[cyunt__cjlx]:
            alias_map[arwzw__lgkfw] = alias_map[cyunt__cjlx]
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
    ett__ncdd = compute_cfg_from_blocks(func_ir.blocks)
    cdx__qjn = compute_use_defs(func_ir.blocks)
    xor__olve = compute_live_map(ett__ncdd, func_ir.blocks, cdx__qjn.usemap,
        cdx__qjn.defmap)
    ejb__jpp = True
    while ejb__jpp:
        ejb__jpp = False
        for rjcw__fphtq, block in func_ir.blocks.items():
            lives = {cyunt__cjlx.name for cyunt__cjlx in block.terminator.
                list_vars()}
            for ragl__evd, kwmhz__odkpx in ett__ncdd.successors(rjcw__fphtq):
                lives |= xor__olve[ragl__evd]
            exr__srlba = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    jnb__qug = stmt.target
                    yvpa__ktniq = stmt.value
                    if jnb__qug.name not in lives:
                        if isinstance(yvpa__ktniq, ir.Expr
                            ) and yvpa__ktniq.op == 'make_function':
                            continue
                        if isinstance(yvpa__ktniq, ir.Expr
                            ) and yvpa__ktniq.op == 'getattr':
                            continue
                        if isinstance(yvpa__ktniq, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(jnb__qug,
                            None), types.Function):
                            continue
                        if isinstance(yvpa__ktniq, ir.Expr
                            ) and yvpa__ktniq.op == 'build_map':
                            continue
                        if isinstance(yvpa__ktniq, ir.Expr
                            ) and yvpa__ktniq.op == 'build_tuple':
                            continue
                    if isinstance(yvpa__ktniq, ir.Var
                        ) and jnb__qug.name == yvpa__ktniq.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    xduff__ptkq = analysis.ir_extension_usedefs[type(stmt)]
                    mjmh__cbo, nzitf__tfawf = xduff__ptkq(stmt)
                    lives -= nzitf__tfawf
                    lives |= mjmh__cbo
                else:
                    lives |= {cyunt__cjlx.name for cyunt__cjlx in stmt.
                        list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(jnb__qug.name)
                exr__srlba.append(stmt)
            exr__srlba.reverse()
            if len(block.body) != len(exr__srlba):
                ejb__jpp = True
            block.body = exr__srlba


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    mfntk__lvk = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (mfntk__lvk,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    ccl__yvg = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), ccl__yvg)


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
            for aojd__xqgn in fnty.templates:
                self._inline_overloads.update(aojd__xqgn._inline_overloads)
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
    ccl__yvg = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), ccl__yvg)
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
    ixx__yijzd, brudg__sfrs = self._get_impl(args, kws)
    if ixx__yijzd is None:
        return
    auee__qfunr = types.Dispatcher(ixx__yijzd)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        yddca__usnsy = ixx__yijzd._compiler
        flags = compiler.Flags()
        tuqhu__vwz = yddca__usnsy.targetdescr.typing_context
        ruudw__lmdag = yddca__usnsy.targetdescr.target_context
        ygnlp__nxbn = yddca__usnsy.pipeline_class(tuqhu__vwz, ruudw__lmdag,
            None, None, None, flags, None)
        nvdyn__osg = InlineWorker(tuqhu__vwz, ruudw__lmdag, yddca__usnsy.
            locals, ygnlp__nxbn, flags, None)
        ojic__qheuv = auee__qfunr.dispatcher.get_call_template
        aojd__xqgn, eqiw__kahr, txq__nanh, kws = ojic__qheuv(brudg__sfrs, kws)
        if txq__nanh in self._inline_overloads:
            return self._inline_overloads[txq__nanh]['iinfo'].signature
        ir = nvdyn__osg.run_untyped_passes(auee__qfunr.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, ruudw__lmdag, ir, txq__nanh, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, txq__nanh, None)
        self._inline_overloads[sig.args] = {'folded_args': txq__nanh}
        gwncj__gyl = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = gwncj__gyl
        if not self._inline.is_always_inline:
            sig = auee__qfunr.get_call_type(self.context, brudg__sfrs, kws)
            self._compiled_overloads[sig.args] = auee__qfunr.get_overload(sig)
        cwlv__yooo = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': txq__nanh,
            'iinfo': cwlv__yooo}
    else:
        sig = auee__qfunr.get_call_type(self.context, brudg__sfrs, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = auee__qfunr.get_overload(sig)
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
    yfl__jqn = [True, False]
    txx__kdnkd = [False, True]
    jkg__uvvmt = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    tajoq__aceb = get_local_target(context)
    kwa__oxx = utils.order_by_target_specificity(tajoq__aceb, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for qgxfp__wbdb in kwa__oxx:
        imkr__gupb = qgxfp__wbdb(context)
        baa__umd = yfl__jqn if imkr__gupb.prefer_literal else txx__kdnkd
        baa__umd = [True] if getattr(imkr__gupb, '_no_unliteral', False
            ) else baa__umd
        for pkbp__qyy in baa__umd:
            try:
                if pkbp__qyy:
                    sig = imkr__gupb.apply(args, kws)
                else:
                    mgvc__zxhoz = tuple([_unlit_non_poison(a) for a in args])
                    ulpp__avtly = {tdnjk__ejncy: _unlit_non_poison(
                        cyunt__cjlx) for tdnjk__ejncy, cyunt__cjlx in kws.
                        items()}
                    sig = imkr__gupb.apply(mgvc__zxhoz, ulpp__avtly)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    jkg__uvvmt.add_error(imkr__gupb, False, e, pkbp__qyy)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = imkr__gupb.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    ypf__bfn = getattr(imkr__gupb, 'cases', None)
                    if ypf__bfn is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            ypf__bfn)
                    else:
                        msg = 'No match.'
                    jkg__uvvmt.add_error(imkr__gupb, True, msg, pkbp__qyy)
    jkg__uvvmt.raise_error()


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
    aojd__xqgn = self.template(context)
    rmldi__jmj = None
    fwbd__flrd = None
    ncpsq__ugdc = None
    baa__umd = [True, False] if aojd__xqgn.prefer_literal else [False, True]
    baa__umd = [True] if getattr(aojd__xqgn, '_no_unliteral', False
        ) else baa__umd
    for pkbp__qyy in baa__umd:
        if pkbp__qyy:
            try:
                ncpsq__ugdc = aojd__xqgn.apply(args, kws)
            except Exception as ubri__etie:
                if isinstance(ubri__etie, errors.ForceLiteralArg):
                    raise ubri__etie
                rmldi__jmj = ubri__etie
                ncpsq__ugdc = None
            else:
                break
        else:
            eel__kqe = tuple([_unlit_non_poison(a) for a in args])
            rabjp__ylu = {tdnjk__ejncy: _unlit_non_poison(cyunt__cjlx) for 
                tdnjk__ejncy, cyunt__cjlx in kws.items()}
            nnuui__vrsh = eel__kqe == args and kws == rabjp__ylu
            if not nnuui__vrsh and ncpsq__ugdc is None:
                try:
                    ncpsq__ugdc = aojd__xqgn.apply(eel__kqe, rabjp__ylu)
                except Exception as ubri__etie:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        ubri__etie, errors.NumbaError):
                        raise ubri__etie
                    if isinstance(ubri__etie, errors.ForceLiteralArg):
                        if aojd__xqgn.prefer_literal:
                            raise ubri__etie
                    fwbd__flrd = ubri__etie
                else:
                    break
    if ncpsq__ugdc is None and (fwbd__flrd is not None or rmldi__jmj is not
        None):
        yulun__jpjsf = '- Resolution failure for {} arguments:\n{}\n'
        fdkah__mtx = _termcolor.highlight(yulun__jpjsf)
        if numba.core.config.DEVELOPER_MODE:
            qda__wax = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    hnp__kwdnv = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    hnp__kwdnv = ['']
                qcei__ixj = '\n{}'.format(2 * qda__wax)
                kxg__nqcb = _termcolor.reset(qcei__ixj + qcei__ixj.join(
                    _bt_as_lines(hnp__kwdnv)))
                return _termcolor.reset(kxg__nqcb)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            whaa__mgbxp = str(e)
            whaa__mgbxp = whaa__mgbxp if whaa__mgbxp else str(repr(e)
                ) + add_bt(e)
            qvjl__uqvne = errors.TypingError(textwrap.dedent(whaa__mgbxp))
            return fdkah__mtx.format(literalness, str(qvjl__uqvne))
        import bodo
        if isinstance(rmldi__jmj, bodo.utils.typing.BodoError):
            raise rmldi__jmj
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', rmldi__jmj) +
                nested_msg('non-literal', fwbd__flrd))
        else:
            if 'missing a required argument' in rmldi__jmj.msg:
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
            raise errors.TypingError(msg, loc=rmldi__jmj.loc)
    return ncpsq__ugdc


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
    tgjzk__louzy = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=tgjzk__louzy)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            lbil__mmw = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), lbil__mmw)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    zieih__qdry = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            zieih__qdry.append(types.Omitted(a.value))
        else:
            zieih__qdry.append(self.typeof_pyval(a))
    epvm__udwtw = None
    try:
        error = None
        epvm__udwtw = self.compile(tuple(zieih__qdry))
    except errors.ForceLiteralArg as e:
        dwu__vnoza = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if dwu__vnoza:
            zzx__tmx = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            guy__jpn = ', '.join('Arg #{} is {}'.format(i, args[i]) for i in
                sorted(dwu__vnoza))
            raise errors.CompilerError(zzx__tmx.format(guy__jpn))
        brudg__sfrs = []
        try:
            for i, cyunt__cjlx in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        brudg__sfrs.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        brudg__sfrs.append(types.literal(args[i]))
                else:
                    brudg__sfrs.append(args[i])
            args = brudg__sfrs
        except (OSError, FileNotFoundError) as wyolj__rwyja:
            error = FileNotFoundError(str(wyolj__rwyja) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                epvm__udwtw = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        rwij__kxlu = []
        for i, kdti__mhd in enumerate(args):
            val = kdti__mhd.value if isinstance(kdti__mhd, numba.core.
                dispatcher.OmittedArg) else kdti__mhd
            try:
                lcrot__wnofl = typeof(val, Purpose.argument)
            except ValueError as mujzv__ffdm:
                rwij__kxlu.append((i, str(mujzv__ffdm)))
            else:
                if lcrot__wnofl is None:
                    rwij__kxlu.append((i,
                        f'cannot determine Numba type of value {val}'))
        if rwij__kxlu:
            lvx__fbj = '\n'.join(f'- argument {i}: {pzorn__qnccg}' for i,
                pzorn__qnccg in rwij__kxlu)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{lvx__fbj}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                nzhrf__orn = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                eznoy__egyh = False
                for mslhi__jeam in nzhrf__orn:
                    if mslhi__jeam in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        eznoy__egyh = True
                        break
                if not eznoy__egyh:
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
                lbil__mmw = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), lbil__mmw)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return epvm__udwtw


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
    for iwirk__rfqgc in cres.library._codegen._engine._defined_symbols:
        if iwirk__rfqgc.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in iwirk__rfqgc and (
            'bodo_gb_udf_update_local' in iwirk__rfqgc or 
            'bodo_gb_udf_combine' in iwirk__rfqgc or 'bodo_gb_udf_eval' in
            iwirk__rfqgc or 'bodo_gb_apply_general_udfs' in iwirk__rfqgc):
            gb_agg_cfunc_addr[iwirk__rfqgc
                ] = cres.library.get_pointer_to_function(iwirk__rfqgc)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for iwirk__rfqgc in cres.library._codegen._engine._defined_symbols:
        if iwirk__rfqgc.startswith('cfunc') and ('get_join_cond_addr' not in
            iwirk__rfqgc or 'bodo_join_gen_cond' in iwirk__rfqgc):
            join_gen_cond_cfunc_addr[iwirk__rfqgc
                ] = cres.library.get_pointer_to_function(iwirk__rfqgc)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    ixx__yijzd = self._get_dispatcher_for_current_target()
    if ixx__yijzd is not self:
        return ixx__yijzd.compile(sig)
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
            duil__ewswg = self.overloads.get(tuple(args))
            if duil__ewswg is not None:
                return duil__ewswg.entry_point
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
            bwaso__ftlgh = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=bwaso__ftlgh):
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
                xahrj__huxks = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in xahrj__huxks:
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
    lnkgr__vim = self._final_module
    ifv__soiza = []
    hlgpc__dxbtu = 0
    for fn in lnkgr__vim.functions:
        hlgpc__dxbtu += 1
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
            ifv__soiza.append(fn.name)
    if hlgpc__dxbtu == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if ifv__soiza:
        lnkgr__vim = lnkgr__vim.clone()
        for name in ifv__soiza:
            lnkgr__vim.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = lnkgr__vim
    return lnkgr__vim


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
    for ura__wtveq in self.constraints:
        loc = ura__wtveq.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                ura__wtveq(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                dymg__ixrch = numba.core.errors.TypingError(str(e), loc=
                    ura__wtveq.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(dymg__ixrch, e))
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
                    dymg__ixrch = numba.core.errors.TypingError(msg.format(
                        con=ura__wtveq, err=str(e)), loc=ura__wtveq.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(dymg__ixrch, e))
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
    for lvmnt__aunr in self._failures.values():
        for jbpp__zsge in lvmnt__aunr:
            if isinstance(jbpp__zsge.error, ForceLiteralArg):
                raise jbpp__zsge.error
            if isinstance(jbpp__zsge.error, bodo.utils.typing.BodoError):
                raise jbpp__zsge.error
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
    etj__tathn = False
    exr__srlba = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        agj__trms = set()
        lxjbj__xrzp = lives & alias_set
        for cyunt__cjlx in lxjbj__xrzp:
            agj__trms |= alias_map[cyunt__cjlx]
        lives_n_aliases = lives | agj__trms | arg_aliases
        if type(stmt) in remove_dead_extensions:
            wgrm__zgnw = remove_dead_extensions[type(stmt)]
            stmt = wgrm__zgnw(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                etj__tathn = True
                continue
        if isinstance(stmt, ir.Assign):
            jnb__qug = stmt.target
            yvpa__ktniq = stmt.value
            if jnb__qug.name not in lives:
                if has_no_side_effect(yvpa__ktniq, lives_n_aliases, call_table
                    ):
                    etj__tathn = True
                    continue
                if isinstance(yvpa__ktniq, ir.Expr
                    ) and yvpa__ktniq.op == 'call' and call_table[yvpa__ktniq
                    .func.name] == ['astype']:
                    tyxpg__ralv = guard(get_definition, func_ir,
                        yvpa__ktniq.func)
                    if (tyxpg__ralv is not None and tyxpg__ralv.op ==
                        'getattr' and isinstance(typemap[tyxpg__ralv.value.
                        name], types.Array) and tyxpg__ralv.attr == 'astype'):
                        etj__tathn = True
                        continue
            if saved_array_analysis and jnb__qug.name in lives and is_expr(
                yvpa__ktniq, 'getattr'
                ) and yvpa__ktniq.attr == 'shape' and is_array_typ(typemap[
                yvpa__ktniq.value.name]
                ) and yvpa__ktniq.value.name not in lives:
                wipq__atymk = {cyunt__cjlx: tdnjk__ejncy for tdnjk__ejncy,
                    cyunt__cjlx in func_ir.blocks.items()}
                if block in wipq__atymk:
                    rjcw__fphtq = wipq__atymk[block]
                    ewjo__sxbsl = saved_array_analysis.get_equiv_set(
                        rjcw__fphtq)
                    ryrum__agiba = ewjo__sxbsl.get_equiv_set(yvpa__ktniq.value)
                    if ryrum__agiba is not None:
                        for cyunt__cjlx in ryrum__agiba:
                            if cyunt__cjlx.endswith('#0'):
                                cyunt__cjlx = cyunt__cjlx[:-2]
                            if cyunt__cjlx in typemap and is_array_typ(typemap
                                [cyunt__cjlx]) and cyunt__cjlx in lives:
                                yvpa__ktniq.value = ir.Var(yvpa__ktniq.
                                    value.scope, cyunt__cjlx, yvpa__ktniq.
                                    value.loc)
                                etj__tathn = True
                                break
            if isinstance(yvpa__ktniq, ir.Var
                ) and jnb__qug.name == yvpa__ktniq.name:
                etj__tathn = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                etj__tathn = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            xduff__ptkq = analysis.ir_extension_usedefs[type(stmt)]
            mjmh__cbo, nzitf__tfawf = xduff__ptkq(stmt)
            lives -= nzitf__tfawf
            lives |= mjmh__cbo
        else:
            lives |= {cyunt__cjlx.name for cyunt__cjlx in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                ozugs__ouv = set()
                if isinstance(yvpa__ktniq, ir.Expr):
                    ozugs__ouv = {cyunt__cjlx.name for cyunt__cjlx in
                        yvpa__ktniq.list_vars()}
                if jnb__qug.name not in ozugs__ouv:
                    lives.remove(jnb__qug.name)
        exr__srlba.append(stmt)
    exr__srlba.reverse()
    block.body = exr__srlba
    return etj__tathn


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            chrov__khisb, = args
            if isinstance(chrov__khisb, types.IterableType):
                dtype = chrov__khisb.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), chrov__khisb)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    zdsg__reyj = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (zdsg__reyj, self.dtype)
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
        except LiteralTypingError as lcad__fbsl:
            return
    try:
        return literal(value)
    except LiteralTypingError as lcad__fbsl:
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
        raa__xnk = py_func.__qualname__
    except AttributeError as lcad__fbsl:
        raa__xnk = py_func.__name__
    boqbi__xfra = inspect.getfile(py_func)
    for cls in self._locator_classes:
        wne__sraul = cls.from_function(py_func, boqbi__xfra)
        if wne__sraul is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (raa__xnk, boqbi__xfra))
    self._locator = wne__sraul
    emjh__iqmj = inspect.getfile(py_func)
    uuri__lzyu = os.path.splitext(os.path.basename(emjh__iqmj))[0]
    if boqbi__xfra.startswith('<ipython-'):
        imqex__weav = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', uuri__lzyu, count=1)
        if imqex__weav == uuri__lzyu:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        uuri__lzyu = imqex__weav
    ateka__hfsd = '%s.%s' % (uuri__lzyu, raa__xnk)
    glf__zou = getattr(sys, 'abiflags', '')
    self._filename_base = self.get_filename_base(ateka__hfsd, glf__zou)


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    ihm__nyhwq = list(filter(lambda a: self._istuple(a.name), args))
    if len(ihm__nyhwq) == 2 and fn.__name__ == 'add':
        xmyj__iimj = self.typemap[ihm__nyhwq[0].name]
        gkj__gwm = self.typemap[ihm__nyhwq[1].name]
        if xmyj__iimj.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                ihm__nyhwq[1]))
        if gkj__gwm.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                ihm__nyhwq[0]))
        try:
            azi__nnxet = [equiv_set.get_shape(x) for x in ihm__nyhwq]
            if None in azi__nnxet:
                return None
            snhmi__ybasg = sum(azi__nnxet, ())
            return ArrayAnalysis.AnalyzeResult(shape=snhmi__ybasg)
        except GuardException as lcad__fbsl:
            return None
    agy__xin = list(filter(lambda a: self._isarray(a.name), args))
    require(len(agy__xin) > 0)
    drsn__oqpvd = [x.name for x in agy__xin]
    nhj__lev = [self.typemap[x.name].ndim for x in agy__xin]
    wgef__zivrx = max(nhj__lev)
    require(wgef__zivrx > 0)
    azi__nnxet = [equiv_set.get_shape(x) for x in agy__xin]
    if any(a is None for a in azi__nnxet):
        return ArrayAnalysis.AnalyzeResult(shape=agy__xin[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, agy__xin))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, azi__nnxet,
        drsn__oqpvd)


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
    ocsz__tmqaw = code_obj.code
    ydiq__oggxs = len(ocsz__tmqaw.co_freevars)
    foojt__ezu = ocsz__tmqaw.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        izte__wsgbw, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        foojt__ezu = [cyunt__cjlx.name for cyunt__cjlx in izte__wsgbw]
    ylen__tqeyv = caller_ir.func_id.func.__globals__
    try:
        ylen__tqeyv = getattr(code_obj, 'globals', ylen__tqeyv)
    except KeyError as lcad__fbsl:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    xhjo__kqwz = []
    for x in foojt__ezu:
        try:
            wdg__lkqgd = caller_ir.get_definition(x)
        except KeyError as lcad__fbsl:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(wdg__lkqgd, (ir.Const, ir.Global, ir.FreeVar)):
            val = wdg__lkqgd.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                mfntk__lvk = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                ylen__tqeyv[mfntk__lvk] = bodo.jit(distributed=False)(val)
                ylen__tqeyv[mfntk__lvk].is_nested_func = True
                val = mfntk__lvk
            if isinstance(val, CPUDispatcher):
                mfntk__lvk = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                ylen__tqeyv[mfntk__lvk] = val
                val = mfntk__lvk
            xhjo__kqwz.append(val)
        elif isinstance(wdg__lkqgd, ir.Expr
            ) and wdg__lkqgd.op == 'make_function':
            baesl__tzyym = convert_code_obj_to_function(wdg__lkqgd, caller_ir)
            mfntk__lvk = ir_utils.mk_unique_var('nested_func').replace('.', '_'
                )
            ylen__tqeyv[mfntk__lvk] = bodo.jit(distributed=False)(baesl__tzyym)
            ylen__tqeyv[mfntk__lvk].is_nested_func = True
            xhjo__kqwz.append(mfntk__lvk)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    iecp__omq = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate(
        xhjo__kqwz)])
    bhsjh__sax = ','.join([('c_%d' % i) for i in range(ydiq__oggxs)])
    xoxr__sdi = list(ocsz__tmqaw.co_varnames)
    ghf__iud = 0
    xhxk__rvlr = ocsz__tmqaw.co_argcount
    bgux__vjx = caller_ir.get_definition(code_obj.defaults)
    if bgux__vjx is not None:
        if isinstance(bgux__vjx, tuple):
            d = [caller_ir.get_definition(x).value for x in bgux__vjx]
            rqr__fel = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in bgux__vjx.items]
            rqr__fel = tuple(d)
        ghf__iud = len(rqr__fel)
    sul__wda = xhxk__rvlr - ghf__iud
    pmt__lgf = ','.join([('%s' % xoxr__sdi[i]) for i in range(sul__wda)])
    if ghf__iud:
        bogm__pyuw = [('%s = %s' % (xoxr__sdi[i + sul__wda], rqr__fel[i])) for
            i in range(ghf__iud)]
        pmt__lgf += ', '
        pmt__lgf += ', '.join(bogm__pyuw)
    return _create_function_from_code_obj(ocsz__tmqaw, iecp__omq, pmt__lgf,
        bhsjh__sax, ylen__tqeyv)


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
    for dpjt__donza, (lndx__nqyv, rqbl__lqzy) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % rqbl__lqzy)
            fibv__bow = _pass_registry.get(lndx__nqyv).pass_inst
            if isinstance(fibv__bow, CompilerPass):
                self._runPass(dpjt__donza, fibv__bow, state)
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
                    pipeline_name, rqbl__lqzy)
                egucp__apeh = self._patch_error(msg, e)
                raise egucp__apeh
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
    oijiz__hqy = None
    nzitf__tfawf = {}

    def lookup(var, already_seen, varonly=True):
        val = nzitf__tfawf.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    mjsvc__apiea = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        jnb__qug = stmt.target
        yvpa__ktniq = stmt.value
        nzitf__tfawf[jnb__qug.name] = yvpa__ktniq
        if isinstance(yvpa__ktniq, ir.Var
            ) and yvpa__ktniq.name in nzitf__tfawf:
            yvpa__ktniq = lookup(yvpa__ktniq, set())
        if isinstance(yvpa__ktniq, ir.Expr):
            pjqa__uxtr = set(lookup(cyunt__cjlx, set(), True).name for
                cyunt__cjlx in yvpa__ktniq.list_vars())
            if name in pjqa__uxtr:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(yvpa__ktniq)]
                fkc__yygj = [x for x, abbor__rttcl in args if abbor__rttcl.
                    name != name]
                args = [(x, abbor__rttcl) for x, abbor__rttcl in args if x !=
                    abbor__rttcl.name]
                zurz__lquwb = dict(args)
                if len(fkc__yygj) == 1:
                    zurz__lquwb[fkc__yygj[0]] = ir.Var(jnb__qug.scope, name +
                        '#init', jnb__qug.loc)
                replace_vars_inner(yvpa__ktniq, zurz__lquwb)
                oijiz__hqy = nodes[i:]
                break
    return oijiz__hqy


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
        esfto__wepnx = expand_aliases({cyunt__cjlx.name for cyunt__cjlx in
            stmt.list_vars()}, alias_map, arg_aliases)
        erd__naq = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        lhesy__otvb = expand_aliases({cyunt__cjlx.name for cyunt__cjlx in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        melbu__swx = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(erd__naq & lhesy__otvb | melbu__swx & esfto__wepnx) == 0:
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
    vxq__oln = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            vxq__oln.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                vxq__oln.update(get_parfor_writes(stmt, func_ir))
    return vxq__oln


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    vxq__oln = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        vxq__oln.add(stmt.target.name)
    if isinstance(stmt, bodo.ir.aggregate.Aggregate):
        vxq__oln = {cyunt__cjlx.name for cyunt__cjlx in stmt.df_out_vars.
            values()}
        if stmt.out_key_vars is not None:
            vxq__oln.update({cyunt__cjlx.name for cyunt__cjlx in stmt.
                out_key_vars})
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        vxq__oln = {cyunt__cjlx.name for cyunt__cjlx in stmt.out_vars}
    if isinstance(stmt, bodo.ir.join.Join):
        vxq__oln = {cyunt__cjlx.name for cyunt__cjlx in stmt.
            get_live_out_vars()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            vxq__oln.update({cyunt__cjlx.name for cyunt__cjlx in stmt.
                get_live_out_vars()})
    if is_call_assign(stmt):
        nps__nco = guard(find_callname, func_ir, stmt.value)
        if nps__nco in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'), (
            'setna', 'bodo.libs.array_kernels'), ('str_arr_item_to_numeric',
            'bodo.libs.str_arr_ext'), ('str_arr_setitem_int_to_str',
            'bodo.libs.str_arr_ext'), ('str_arr_setitem_NA_str',
            'bodo.libs.str_arr_ext'), ('str_arr_set_not_na',
            'bodo.libs.str_arr_ext'), ('get_str_arr_item_copy',
            'bodo.libs.str_arr_ext'), ('set_bit_to_arr',
            'bodo.libs.int_arr_ext')):
            vxq__oln.add(stmt.value.args[0].name)
        if nps__nco == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            vxq__oln.add(stmt.value.args[1].name)
    return vxq__oln


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
        wgrm__zgnw = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        bvv__kxi = wgrm__zgnw.format(self, msg)
        self.args = bvv__kxi,
    else:
        wgrm__zgnw = _termcolor.errmsg('{0}')
        bvv__kxi = wgrm__zgnw.format(self)
        self.args = bvv__kxi,
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
        for ucsjh__yolqo in options['distributed']:
            dist_spec[ucsjh__yolqo] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for ucsjh__yolqo in options['distributed_block']:
            dist_spec[ucsjh__yolqo] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    ojb__uqwmv = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, goeve__fix in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(goeve__fix)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    qpjvg__hcc = {}
    for thzpx__zwk in reversed(inspect.getmro(cls)):
        qpjvg__hcc.update(thzpx__zwk.__dict__)
    aof__cabj, nzedy__xhf, smy__xxz, bdow__ufez = {}, {}, {}, {}
    for tdnjk__ejncy, cyunt__cjlx in qpjvg__hcc.items():
        if isinstance(cyunt__cjlx, pytypes.FunctionType):
            aof__cabj[tdnjk__ejncy] = cyunt__cjlx
        elif isinstance(cyunt__cjlx, property):
            nzedy__xhf[tdnjk__ejncy] = cyunt__cjlx
        elif isinstance(cyunt__cjlx, staticmethod):
            smy__xxz[tdnjk__ejncy] = cyunt__cjlx
        else:
            bdow__ufez[tdnjk__ejncy] = cyunt__cjlx
    gbx__igy = (set(aof__cabj) | set(nzedy__xhf) | set(smy__xxz)) & set(spec)
    if gbx__igy:
        raise NameError('name shadowing: {0}'.format(', '.join(gbx__igy)))
    vflck__xiykf = bdow__ufez.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(bdow__ufez)
    if bdow__ufez:
        msg = 'class members are not yet supported: {0}'
        kgmi__dkkzo = ', '.join(bdow__ufez.keys())
        raise TypeError(msg.format(kgmi__dkkzo))
    for tdnjk__ejncy, cyunt__cjlx in nzedy__xhf.items():
        if cyunt__cjlx.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(
                tdnjk__ejncy))
    jit_methods = {tdnjk__ejncy: bodo.jit(returns_maybe_distributed=
        ojb__uqwmv)(cyunt__cjlx) for tdnjk__ejncy, cyunt__cjlx in aof__cabj
        .items()}
    jit_props = {}
    for tdnjk__ejncy, cyunt__cjlx in nzedy__xhf.items():
        ccl__yvg = {}
        if cyunt__cjlx.fget:
            ccl__yvg['get'] = bodo.jit(cyunt__cjlx.fget)
        if cyunt__cjlx.fset:
            ccl__yvg['set'] = bodo.jit(cyunt__cjlx.fset)
        jit_props[tdnjk__ejncy] = ccl__yvg
    jit_static_methods = {tdnjk__ejncy: bodo.jit(cyunt__cjlx.__func__) for 
        tdnjk__ejncy, cyunt__cjlx in smy__xxz.items()}
    vxr__zqrg = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    qye__ibhh = dict(class_type=vxr__zqrg, __doc__=vflck__xiykf)
    qye__ibhh.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), qye__ibhh)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, vxr__zqrg)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(vxr__zqrg, typingctx, targetctx).register()
    as_numba_type.register(cls, vxr__zqrg.instance_type)
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
    drk__vqbij = ','.join('{0}:{1}'.format(tdnjk__ejncy, cyunt__cjlx) for 
        tdnjk__ejncy, cyunt__cjlx in struct.items())
    vkebu__jrlu = ','.join('{0}:{1}'.format(tdnjk__ejncy, cyunt__cjlx) for 
        tdnjk__ejncy, cyunt__cjlx in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), drk__vqbij, vkebu__jrlu)
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
    pkx__ztit = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if pkx__ztit is None:
        return
    lhzc__lcvzs, ilnx__tamd = pkx__ztit
    for a in itertools.chain(lhzc__lcvzs, ilnx__tamd.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, lhzc__lcvzs, ilnx__tamd)
    except ForceLiteralArg as e:
        svdt__zakk = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(svdt__zakk, self.kws)
        ttj__kois = set()
        vstw__opur = set()
        tba__fxg = {}
        for dpjt__donza in e.requested_args:
            oxn__fmw = typeinfer.func_ir.get_definition(folded[dpjt__donza])
            if isinstance(oxn__fmw, ir.Arg):
                ttj__kois.add(oxn__fmw.index)
                if oxn__fmw.index in e.file_infos:
                    tba__fxg[oxn__fmw.index] = e.file_infos[oxn__fmw.index]
            else:
                vstw__opur.add(dpjt__donza)
        if vstw__opur:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif ttj__kois:
            raise ForceLiteralArg(ttj__kois, loc=self.loc, file_infos=tba__fxg)
    if sig is None:
        tgeiz__nlu = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in lhzc__lcvzs]
        args += [('%s=%s' % (tdnjk__ejncy, cyunt__cjlx)) for tdnjk__ejncy,
            cyunt__cjlx in sorted(ilnx__tamd.items())]
        xtklx__rymg = tgeiz__nlu.format(fnty, ', '.join(map(str, args)))
        chk__deotb = context.explain_function_type(fnty)
        msg = '\n'.join([xtklx__rymg, chk__deotb])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        sgdxa__vrvse = context.unify_pairs(sig.recvr, fnty.this)
        if sgdxa__vrvse is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if sgdxa__vrvse is not None and sgdxa__vrvse.is_precise():
            rwhh__qnujf = fnty.copy(this=sgdxa__vrvse)
            typeinfer.propagate_refined_type(self.func, rwhh__qnujf)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            xzhss__hjcnu = target.getone()
            if context.unify_pairs(xzhss__hjcnu, sig.return_type
                ) == xzhss__hjcnu:
                sig = sig.replace(return_type=xzhss__hjcnu)
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
        zzx__tmx = '*other* must be a {} but got a {} instead'
        raise TypeError(zzx__tmx.format(ForceLiteralArg, type(other)))
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
    ikgtf__feat = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for tdnjk__ejncy, cyunt__cjlx in kwargs.items():
        yysp__bdl = None
        try:
            ghq__whii = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var(
                'dummy'), loc)
            func_ir._definitions[ghq__whii.name] = [cyunt__cjlx]
            yysp__bdl = get_const_value_inner(func_ir, ghq__whii)
            func_ir._definitions.pop(ghq__whii.name)
            if isinstance(yysp__bdl, str):
                yysp__bdl = sigutils._parse_signature_string(yysp__bdl)
            if isinstance(yysp__bdl, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {tdnjk__ejncy} is annotated as type class {yysp__bdl}."""
                    )
            assert isinstance(yysp__bdl, types.Type)
            if isinstance(yysp__bdl, (types.List, types.Set)):
                yysp__bdl = yysp__bdl.copy(reflected=False)
            ikgtf__feat[tdnjk__ejncy] = yysp__bdl
        except BodoError as lcad__fbsl:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(yysp__bdl, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(cyunt__cjlx, ir.Global):
                    msg = f'Global {cyunt__cjlx.name!r} is not defined.'
                if isinstance(cyunt__cjlx, ir.FreeVar):
                    msg = f'Freevar {cyunt__cjlx.name!r} is not defined.'
            if isinstance(cyunt__cjlx, ir.Expr
                ) and cyunt__cjlx.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=tdnjk__ejncy, msg=msg, loc=loc)
    for name, typ in ikgtf__feat.items():
        self._legalize_arg_type(name, typ, loc)
    return ikgtf__feat


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
    mguwv__izqpv = inst.arg
    assert mguwv__izqpv > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(mguwv__izqpv)]))
    tmps = [state.make_temp() for _ in range(mguwv__izqpv - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    oxyk__wkcg = ir.Global('format', format, loc=self.loc)
    self.store(value=oxyk__wkcg, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    fmye__ngwg = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=fmye__ngwg, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    mguwv__izqpv = inst.arg
    assert mguwv__izqpv > 0, 'invalid BUILD_STRING count'
    nna__tdc = self.get(strings[0])
    for other, fkh__bjqr in zip(strings[1:], tmps):
        other = self.get(other)
        myoc__rhwc = ir.Expr.binop(operator.add, lhs=nna__tdc, rhs=other,
            loc=self.loc)
        self.store(myoc__rhwc, fkh__bjqr)
        nna__tdc = self.get(fkh__bjqr)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    bbtcx__wmbtd = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, bbtcx__wmbtd])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    hfl__aasaz = mk_unique_var(f'{var_name}')
    jzbad__mzd = hfl__aasaz.replace('<', '_').replace('>', '_')
    jzbad__mzd = jzbad__mzd.replace('.', '_').replace('$', '_v')
    return jzbad__mzd


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
                wws__axwi = get_overload_const_str(val2)
                if wws__axwi != 'ns':
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
        rkccy__ilg = states['defmap']
        if len(rkccy__ilg) == 0:
            lewo__hdrt = assign.target
            numba.core.ssa._logger.debug('first assign: %s', lewo__hdrt)
            if lewo__hdrt.name not in scope.localvars:
                lewo__hdrt = scope.define(assign.target.name, loc=assign.loc)
        else:
            lewo__hdrt = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=lewo__hdrt, value=assign.value, loc=
            assign.loc)
        rkccy__ilg[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    qnwe__kuuk = []
    for tdnjk__ejncy, cyunt__cjlx in typing.npydecl.registry.globals:
        if tdnjk__ejncy == func:
            qnwe__kuuk.append(cyunt__cjlx)
    for tdnjk__ejncy, cyunt__cjlx in typing.templates.builtin_registry.globals:
        if tdnjk__ejncy == func:
            qnwe__kuuk.append(cyunt__cjlx)
    if len(qnwe__kuuk) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return qnwe__kuuk


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    odeu__iqcl = {}
    rjp__uoael = find_topo_order(blocks)
    iytio__axtln = {}
    for rjcw__fphtq in rjp__uoael:
        block = blocks[rjcw__fphtq]
        exr__srlba = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                jnb__qug = stmt.target.name
                yvpa__ktniq = stmt.value
                if (yvpa__ktniq.op == 'getattr' and yvpa__ktniq.attr in
                    arr_math and isinstance(typemap[yvpa__ktniq.value.name],
                    types.npytypes.Array)):
                    yvpa__ktniq = stmt.value
                    rsc__dthcw = yvpa__ktniq.value
                    odeu__iqcl[jnb__qug] = rsc__dthcw
                    scope = rsc__dthcw.scope
                    loc = rsc__dthcw.loc
                    axci__qpg = ir.Var(scope, mk_unique_var('$np_g_var'), loc)
                    typemap[axci__qpg.name] = types.misc.Module(numpy)
                    not__liqx = ir.Global('np', numpy, loc)
                    yhc__ibcj = ir.Assign(not__liqx, axci__qpg, loc)
                    yvpa__ktniq.value = axci__qpg
                    exr__srlba.append(yhc__ibcj)
                    func_ir._definitions[axci__qpg.name] = [not__liqx]
                    func = getattr(numpy, yvpa__ktniq.attr)
                    dfg__lwwa = get_np_ufunc_typ_lst(func)
                    iytio__axtln[jnb__qug] = dfg__lwwa
                if (yvpa__ktniq.op == 'call' and yvpa__ktniq.func.name in
                    odeu__iqcl):
                    rsc__dthcw = odeu__iqcl[yvpa__ktniq.func.name]
                    izda__xvo = calltypes.pop(yvpa__ktniq)
                    hbcp__gdzt = izda__xvo.args[:len(yvpa__ktniq.args)]
                    ijipb__qitd = {name: typemap[cyunt__cjlx.name] for name,
                        cyunt__cjlx in yvpa__ktniq.kws}
                    phw__etgjo = iytio__axtln[yvpa__ktniq.func.name]
                    xdz__tvp = None
                    for fcz__vnrvm in phw__etgjo:
                        try:
                            xdz__tvp = fcz__vnrvm.get_call_type(typingctx, 
                                [typemap[rsc__dthcw.name]] + list(
                                hbcp__gdzt), ijipb__qitd)
                            typemap.pop(yvpa__ktniq.func.name)
                            typemap[yvpa__ktniq.func.name] = fcz__vnrvm
                            calltypes[yvpa__ktniq] = xdz__tvp
                            break
                        except Exception as lcad__fbsl:
                            pass
                    if xdz__tvp is None:
                        raise TypeError(
                            f'No valid template found for {yvpa__ktniq.func.name}'
                            )
                    yvpa__ktniq.args = [rsc__dthcw] + yvpa__ktniq.args
            exr__srlba.append(stmt)
        block.body = exr__srlba


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    bmami__avqdp = ufunc.nin
    osozy__cnn = ufunc.nout
    sul__wda = ufunc.nargs
    assert sul__wda == bmami__avqdp + osozy__cnn
    if len(args) < bmami__avqdp:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            bmami__avqdp))
    if len(args) > sul__wda:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), sul__wda))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    iksax__nrtbz = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    wnga__tlo = max(iksax__nrtbz)
    agqg__uhyne = args[bmami__avqdp:]
    if not all(d == wnga__tlo for d in iksax__nrtbz[bmami__avqdp:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(mwaa__har, types.ArrayCompatible) and not
        isinstance(mwaa__har, types.Bytes) for mwaa__har in agqg__uhyne):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(mwaa__har.mutable for mwaa__har in agqg__uhyne):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    jxhq__bhmw = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    uuj__keh = None
    if wnga__tlo > 0 and len(agqg__uhyne) < ufunc.nout:
        uuj__keh = 'C'
        lzqn__dey = [(x.layout if isinstance(x, types.ArrayCompatible) and 
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in lzqn__dey and 'F' in lzqn__dey:
            uuj__keh = 'F'
    return jxhq__bhmw, agqg__uhyne, wnga__tlo, uuj__keh


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
        iemne__uwmd = 'Dict.key_type cannot be of type {}'
        raise TypingError(iemne__uwmd.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        iemne__uwmd = 'Dict.value_type cannot be of type {}'
        raise TypingError(iemne__uwmd.format(valty))
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
    qsp__vtcl = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[qsp__vtcl]
        return impl, args
    except KeyError as lcad__fbsl:
        pass
    impl, args = self._build_impl(qsp__vtcl, args, kws)
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
        ayfrg__spn = find_topo_order(parfor.loop_body)
    btpq__lwan = ayfrg__spn[0]
    hjpj__ryag = {}
    _update_parfor_get_setitems(parfor.loop_body[btpq__lwan].body, parfor.
        index_var, alias_map, hjpj__ryag, lives_n_aliases)
    hfpsb__xcxj = set(hjpj__ryag.keys())
    for cpbr__hsbmi in ayfrg__spn:
        if cpbr__hsbmi == btpq__lwan:
            continue
        for stmt in parfor.loop_body[cpbr__hsbmi].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            opk__aduk = set(cyunt__cjlx.name for cyunt__cjlx in stmt.
                list_vars())
            rba__jof = opk__aduk & hfpsb__xcxj
            for a in rba__jof:
                hjpj__ryag.pop(a, None)
    for cpbr__hsbmi in ayfrg__spn:
        if cpbr__hsbmi == btpq__lwan:
            continue
        block = parfor.loop_body[cpbr__hsbmi]
        qiry__aotda = hjpj__ryag.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            qiry__aotda, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    glkxj__nivju = max(blocks.keys())
    zupeg__tidur, eic__njuja = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    smgvl__evam = ir.Jump(zupeg__tidur, ir.Loc('parfors_dummy', -1))
    blocks[glkxj__nivju].body.append(smgvl__evam)
    ett__ncdd = compute_cfg_from_blocks(blocks)
    cdx__qjn = compute_use_defs(blocks)
    xor__olve = compute_live_map(ett__ncdd, blocks, cdx__qjn.usemap,
        cdx__qjn.defmap)
    alias_set = set(alias_map.keys())
    for rjcw__fphtq, block in blocks.items():
        exr__srlba = []
        nvbwe__kgcd = {cyunt__cjlx.name for cyunt__cjlx in block.terminator
            .list_vars()}
        for ragl__evd, kwmhz__odkpx in ett__ncdd.successors(rjcw__fphtq):
            nvbwe__kgcd |= xor__olve[ragl__evd]
        for stmt in reversed(block.body):
            agj__trms = nvbwe__kgcd & alias_set
            for cyunt__cjlx in agj__trms:
                nvbwe__kgcd |= alias_map[cyunt__cjlx]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in nvbwe__kgcd and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                nps__nco = guard(find_callname, func_ir, stmt.value)
                if nps__nco == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in nvbwe__kgcd and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            nvbwe__kgcd |= {cyunt__cjlx.name for cyunt__cjlx in stmt.
                list_vars()}
            exr__srlba.append(stmt)
        exr__srlba.reverse()
        block.body = exr__srlba
    typemap.pop(eic__njuja.name)
    blocks[glkxj__nivju].body.pop()

    def trim_empty_parfor_branches(parfor):
        ejb__jpp = False
        blocks = parfor.loop_body.copy()
        for rjcw__fphtq, block in blocks.items():
            if len(block.body):
                aagr__gjblu = block.body[-1]
                if isinstance(aagr__gjblu, ir.Branch):
                    if len(blocks[aagr__gjblu.truebr].body) == 1 and len(blocks
                        [aagr__gjblu.falsebr].body) == 1:
                        gzo__mxonp = blocks[aagr__gjblu.truebr].body[0]
                        obooj__dpnd = blocks[aagr__gjblu.falsebr].body[0]
                        if isinstance(gzo__mxonp, ir.Jump) and isinstance(
                            obooj__dpnd, ir.Jump
                            ) and gzo__mxonp.target == obooj__dpnd.target:
                            parfor.loop_body[rjcw__fphtq].body[-1] = ir.Jump(
                                gzo__mxonp.target, aagr__gjblu.loc)
                            ejb__jpp = True
                    elif len(blocks[aagr__gjblu.truebr].body) == 1:
                        gzo__mxonp = blocks[aagr__gjblu.truebr].body[0]
                        if isinstance(gzo__mxonp, ir.Jump
                            ) and gzo__mxonp.target == aagr__gjblu.falsebr:
                            parfor.loop_body[rjcw__fphtq].body[-1] = ir.Jump(
                                gzo__mxonp.target, aagr__gjblu.loc)
                            ejb__jpp = True
                    elif len(blocks[aagr__gjblu.falsebr].body) == 1:
                        obooj__dpnd = blocks[aagr__gjblu.falsebr].body[0]
                        if isinstance(obooj__dpnd, ir.Jump
                            ) and obooj__dpnd.target == aagr__gjblu.truebr:
                            parfor.loop_body[rjcw__fphtq].body[-1] = ir.Jump(
                                obooj__dpnd.target, aagr__gjblu.loc)
                            ejb__jpp = True
        return ejb__jpp
    ejb__jpp = True
    while ejb__jpp:
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
        ejb__jpp = trim_empty_parfor_branches(parfor)
    yvky__pgru = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        yvky__pgru &= len(block.body) == 0
    if yvky__pgru:
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
    esjvv__nhwt = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                esjvv__nhwt += 1
                parfor = stmt
                pbks__vfzm = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = pbks__vfzm.scope
                loc = ir.Loc('parfors_dummy', -1)
                vbtj__iaa = ir.Var(scope, mk_unique_var('$const'), loc)
                pbks__vfzm.body.append(ir.Assign(ir.Const(0, loc),
                    vbtj__iaa, loc))
                pbks__vfzm.body.append(ir.Return(vbtj__iaa, loc))
                ett__ncdd = compute_cfg_from_blocks(parfor.loop_body)
                for nwrm__ynny in ett__ncdd.dead_nodes():
                    del parfor.loop_body[nwrm__ynny]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                pbks__vfzm = parfor.loop_body[max(parfor.loop_body.keys())]
                pbks__vfzm.body.pop()
                pbks__vfzm.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return esjvv__nhwt


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
            duil__ewswg = self.overloads.get(tuple(args))
            if duil__ewswg is not None:
                return duil__ewswg.entry_point
            self._pre_compile(args, return_type, flags)
            aju__mrxt = self.func_ir
            bwaso__ftlgh = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=bwaso__ftlgh):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=aju__mrxt, args=args,
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
        amto__gyij = copy.deepcopy(flags)
        amto__gyij.no_rewrites = True

        def compile_local(the_ir, the_flags):
            tzkg__bqig = pipeline_class(typingctx, targetctx, library, args,
                return_type, the_flags, locals)
            return tzkg__bqig.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        rnrsr__trldp = compile_local(func_ir, amto__gyij)
        bvaa__nppsu = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    bvaa__nppsu = compile_local(func_ir, flags)
                except Exception as lcad__fbsl:
                    pass
        if bvaa__nppsu is not None:
            cres = bvaa__nppsu
        else:
            cres = rnrsr__trldp
        return cres
    else:
        tzkg__bqig = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return tzkg__bqig.compile_ir(func_ir=func_ir, lifted=lifted,
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
    uvnz__bnu = self.get_data_type(typ.dtype)
    oicl__zhre = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        oicl__zhre):
        ailh__zjuse = ary.ctypes.data
        tsb__retkn = self.add_dynamic_addr(builder, ailh__zjuse, info=str(
            type(ailh__zjuse)))
        yylez__wfyrj = self.add_dynamic_addr(builder, id(ary), info=str(
            type(ary)))
        self.global_arrays.append(ary)
    else:
        qdf__ndlkp = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            qdf__ndlkp = qdf__ndlkp.view('int64')
        val = bytearray(qdf__ndlkp.data)
        wjebg__pfite = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)),
            val)
        tsb__retkn = cgutils.global_constant(builder, '.const.array.data',
            wjebg__pfite)
        tsb__retkn.align = self.get_abi_alignment(uvnz__bnu)
        yylez__wfyrj = None
    wuwv__kcxr = self.get_value_type(types.intp)
    avwvd__qomen = [self.get_constant(types.intp, rizq__qqzwg) for
        rizq__qqzwg in ary.shape]
    qym__sbvmo = lir.Constant(lir.ArrayType(wuwv__kcxr, len(avwvd__qomen)),
        avwvd__qomen)
    fqg__bnsu = [self.get_constant(types.intp, rizq__qqzwg) for rizq__qqzwg in
        ary.strides]
    foz__mcqu = lir.Constant(lir.ArrayType(wuwv__kcxr, len(fqg__bnsu)),
        fqg__bnsu)
    ndxku__cav = self.get_constant(types.intp, ary.dtype.itemsize)
    ber__fmjf = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        ber__fmjf, ndxku__cav, tsb__retkn.bitcast(self.get_value_type(types
        .CPointer(typ.dtype))), qym__sbvmo, foz__mcqu])


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
    cioa__tcuvv = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    oqs__isw = lir.Function(module, cioa__tcuvv, name='nrt_atomic_{0}'.
        format(op))
    [xoqe__ssjza] = oqs__isw.args
    fzg__mjk = oqs__isw.append_basic_block()
    builder = lir.IRBuilder(fzg__mjk)
    cnp__ablgv = lir.Constant(_word_type, 1)
    if False:
        gyoi__avfuw = builder.atomic_rmw(op, xoqe__ssjza, cnp__ablgv,
            ordering=ordering)
        res = getattr(builder, op)(gyoi__avfuw, cnp__ablgv)
        builder.ret(res)
    else:
        gyoi__avfuw = builder.load(xoqe__ssjza)
        uqp__cbwc = getattr(builder, op)(gyoi__avfuw, cnp__ablgv)
        awiqx__gkzn = builder.icmp_signed('!=', gyoi__avfuw, lir.Constant(
            gyoi__avfuw.type, -1))
        with cgutils.if_likely(builder, awiqx__gkzn):
            builder.store(uqp__cbwc, xoqe__ssjza)
        builder.ret(uqp__cbwc)
    return oqs__isw


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
        dxdwa__xrc = state.targetctx.codegen()
        state.library = dxdwa__xrc.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    wxy__gmivs = state.func_ir
    typemap = state.typemap
    vop__sfy = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    utc__sbi = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            wxy__gmivs, typemap, vop__sfy, calltypes, mangler=targetctx.
            mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            cykk__kxc = lowering.Lower(targetctx, library, fndesc,
                wxy__gmivs, metadata=metadata)
            cykk__kxc.lower()
            if not flags.no_cpython_wrapper:
                cykk__kxc.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(vop__sfy, (types.Optional, types.Generator)):
                        pass
                    else:
                        cykk__kxc.create_cfunc_wrapper()
            env = cykk__kxc.env
            beavb__fgag = cykk__kxc.call_helper
            del cykk__kxc
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, beavb__fgag, cfunc=None, env=env
                )
        else:
            jijlm__nrl = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(jijlm__nrl, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, beavb__fgag, cfunc=
                jijlm__nrl, env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        ihly__dzwnj = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = ihly__dzwnj - utc__sbi
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
        vegou__zgb = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, vegou__zgb),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            ovrgo__kqb.do_break()
        yefv__gvtl = c.builder.icmp_signed('!=', vegou__zgb, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(yefv__gvtl, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, vegou__zgb)
                c.pyapi.decref(vegou__zgb)
                ovrgo__kqb.do_break()
        c.pyapi.decref(vegou__zgb)
    cpyln__qnjs, list = listobj.ListInstance.allocate_ex(c.context, c.
        builder, typ, size)
    with c.builder.if_else(cpyln__qnjs, likely=True) as (hlaah__riogr,
        kije__tat):
        with hlaah__riogr:
            list.size = size
            cbcyc__vabe = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                cbcyc__vabe), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        cbcyc__vabe))
                    with cgutils.for_range(c.builder, size) as ovrgo__kqb:
                        itemobj = c.pyapi.list_getitem(obj, ovrgo__kqb.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        dilv__urjpw = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(dilv__urjpw.is_error, likely
                            =False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            ovrgo__kqb.do_break()
                        list.setitem(ovrgo__kqb.index, dilv__urjpw.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with kije__tat:
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
    dwcun__iyvu, kpy__sou, jylbs__wjkd, paam__dubc, tttzr__gcvc = (
        compile_time_get_string_data(literal_string))
    lnkgr__vim = builder.module
    gv = context.insert_const_bytes(lnkgr__vim, dwcun__iyvu)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        kpy__sou), context.get_constant(types.int32, jylbs__wjkd), context.
        get_constant(types.uint32, paam__dubc), context.get_constant(
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
    ldp__agxs = None
    if isinstance(shape, types.Integer):
        ldp__agxs = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(rizq__qqzwg, (types.Integer, types.IntEnumMember)
            ) for rizq__qqzwg in shape):
            ldp__agxs = len(shape)
    return ldp__agxs


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
            ldp__agxs = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if ldp__agxs == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(ldp__agxs))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            drsn__oqpvd = self._get_names(x)
            if len(drsn__oqpvd) != 0:
                return drsn__oqpvd[0]
            return drsn__oqpvd
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    drsn__oqpvd = self._get_names(obj)
    if len(drsn__oqpvd) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(drsn__oqpvd[0])


def get_equiv_set(self, obj):
    drsn__oqpvd = self._get_names(obj)
    if len(drsn__oqpvd) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(drsn__oqpvd[0])


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
    htafm__xwa = []
    for ibpvm__pvefm in func_ir.arg_names:
        if ibpvm__pvefm in typemap and isinstance(typemap[ibpvm__pvefm],
            types.containers.UniTuple) and typemap[ibpvm__pvefm].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(ibpvm__pvefm))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for sca__espn in func_ir.blocks.values():
        for stmt in sca__espn.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    qhvrk__rwv = getattr(val, 'code', None)
                    if qhvrk__rwv is not None:
                        if getattr(val, 'closure', None) is not None:
                            bxrpj__mdznq = (
                                '<creating a function from a closure>')
                            myoc__rhwc = ''
                        else:
                            bxrpj__mdznq = qhvrk__rwv.co_name
                            myoc__rhwc = '(%s) ' % bxrpj__mdznq
                    else:
                        bxrpj__mdznq = '<could not ascertain use case>'
                        myoc__rhwc = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (bxrpj__mdznq, myoc__rhwc))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                hjt__ubz = False
                if isinstance(val, pytypes.FunctionType):
                    hjt__ubz = val in {numba.gdb, numba.gdb_init}
                if not hjt__ubz:
                    hjt__ubz = getattr(val, '_name', '') == 'gdb_internal'
                if hjt__ubz:
                    htafm__xwa.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    grm__gcbh = func_ir.get_definition(var)
                    pum__vsjz = guard(find_callname, func_ir, grm__gcbh)
                    if pum__vsjz and pum__vsjz[1] == 'numpy':
                        ty = getattr(numpy, pum__vsjz[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    yyyaa__siqfv = '' if var.startswith('$'
                        ) else "'{}' ".format(var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(yyyaa__siqfv), loc=stmt.loc)
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
    if len(htafm__xwa) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        yaidy__znw = '\n'.join([x.strformat() for x in htafm__xwa])
        raise errors.UnsupportedError(msg % yaidy__znw)


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
    tdnjk__ejncy, cyunt__cjlx = next(iter(val.items()))
    mqak__uovz = typeof_impl(tdnjk__ejncy, c)
    dwpb__vrqr = typeof_impl(cyunt__cjlx, c)
    if mqak__uovz is None or dwpb__vrqr is None:
        raise ValueError(
            f'Cannot type dict element type {type(tdnjk__ejncy)}, {type(cyunt__cjlx)}'
            )
    return types.DictType(mqak__uovz, dwpb__vrqr)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    iivs__qkqir = cgutils.alloca_once_value(c.builder, val)
    dnm__vebj = c.pyapi.object_hasattr_string(val, '_opaque')
    ukyh__kyo = c.builder.icmp_unsigned('==', dnm__vebj, lir.Constant(
        dnm__vebj.type, 0))
    evpms__ruy = typ.key_type
    vcup__ljm = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(evpms__ruy, vcup__ljm)

    def copy_dict(out_dict, in_dict):
        for tdnjk__ejncy, cyunt__cjlx in in_dict.items():
            out_dict[tdnjk__ejncy] = cyunt__cjlx
    with c.builder.if_then(ukyh__kyo):
        uxmd__rdid = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        mpqf__vodz = c.pyapi.call_function_objargs(uxmd__rdid, [])
        zgdo__mxlbm = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(zgdo__mxlbm, [mpqf__vodz, val])
        c.builder.store(mpqf__vodz, iivs__qkqir)
    val = c.builder.load(iivs__qkqir)
    phhtk__bynnq = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    bfe__kmrl = c.pyapi.object_type(val)
    rhhya__yboxb = c.builder.icmp_unsigned('==', bfe__kmrl, phhtk__bynnq)
    with c.builder.if_else(rhhya__yboxb) as (dbx__iumbu, enj__vtg):
        with dbx__iumbu:
            sly__mcyp = c.pyapi.object_getattr_string(val, '_opaque')
            ofu__ojts = types.MemInfoPointer(types.voidptr)
            dilv__urjpw = c.unbox(ofu__ojts, sly__mcyp)
            mi = dilv__urjpw.value
            zieih__qdry = ofu__ojts, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *zieih__qdry)
            krn__tvm = context.get_constant_null(zieih__qdry[1])
            args = mi, krn__tvm
            xfsy__qvcq, uljn__gvvqc = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, uljn__gvvqc)
            c.pyapi.decref(sly__mcyp)
            zdc__knjgf = c.builder.basic_block
        with enj__vtg:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", bfe__kmrl, phhtk__bynnq)
            yhkqp__fweh = c.builder.basic_block
    khfju__jjqo = c.builder.phi(uljn__gvvqc.type)
    rriz__cgw = c.builder.phi(xfsy__qvcq.type)
    khfju__jjqo.add_incoming(uljn__gvvqc, zdc__knjgf)
    khfju__jjqo.add_incoming(uljn__gvvqc.type(None), yhkqp__fweh)
    rriz__cgw.add_incoming(xfsy__qvcq, zdc__knjgf)
    rriz__cgw.add_incoming(cgutils.true_bit, yhkqp__fweh)
    c.pyapi.decref(phhtk__bynnq)
    c.pyapi.decref(bfe__kmrl)
    with c.builder.if_then(ukyh__kyo):
        c.pyapi.decref(val)
    return NativeValue(khfju__jjqo, is_error=rriz__cgw)


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
    iax__akiv = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=iax__akiv, name=updatevar)
    ifnh__otb = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc)
    self.store(value=ifnh__otb, name=res)


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
        for tdnjk__ejncy, cyunt__cjlx in other.items():
            d[tdnjk__ejncy] = cyunt__cjlx
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
    myoc__rhwc = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(myoc__rhwc, res)


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
    fash__hnbq = PassManager(name)
    if state.func_ir is None:
        fash__hnbq.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            fash__hnbq.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        fash__hnbq.add_pass(FixupArgs, 'fix up args')
    fash__hnbq.add_pass(IRProcessing, 'processing IR')
    fash__hnbq.add_pass(WithLifting, 'Handle with contexts')
    fash__hnbq.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        fash__hnbq.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        fash__hnbq.add_pass(DeadBranchPrune, 'dead branch pruning')
        fash__hnbq.add_pass(GenericRewrites, 'nopython rewrites')
    fash__hnbq.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    fash__hnbq.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        fash__hnbq.add_pass(DeadBranchPrune, 'dead branch pruning')
    fash__hnbq.add_pass(FindLiterallyCalls, 'find literally calls')
    fash__hnbq.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        fash__hnbq.add_pass(ReconstructSSA, 'ssa')
    fash__hnbq.add_pass(LiteralPropagationSubPipelinePass,
        'Literal propagation')
    fash__hnbq.finalize()
    return fash__hnbq


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
    a, wnput__hme = args
    if isinstance(a, types.List) and isinstance(wnput__hme, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(wnput__hme, types.List):
        return signature(wnput__hme, types.intp, wnput__hme)


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
        vcdz__eoq, ecp__eexd = 0, 1
    else:
        vcdz__eoq, ecp__eexd = 1, 0
    yxgx__nwi = ListInstance(context, builder, sig.args[vcdz__eoq], args[
        vcdz__eoq])
    cdah__hwc = yxgx__nwi.size
    zdee__xphnx = args[ecp__eexd]
    cbcyc__vabe = lir.Constant(zdee__xphnx.type, 0)
    zdee__xphnx = builder.select(cgutils.is_neg_int(builder, zdee__xphnx),
        cbcyc__vabe, zdee__xphnx)
    ber__fmjf = builder.mul(zdee__xphnx, cdah__hwc)
    iik__ahofz = ListInstance.allocate(context, builder, sig.return_type,
        ber__fmjf)
    iik__ahofz.size = ber__fmjf
    with cgutils.for_range_slice(builder, cbcyc__vabe, ber__fmjf, cdah__hwc,
        inc=True) as (sgoz__yoh, _):
        with cgutils.for_range(builder, cdah__hwc) as ovrgo__kqb:
            value = yxgx__nwi.getitem(ovrgo__kqb.index)
            iik__ahofz.setitem(builder.add(ovrgo__kqb.index, sgoz__yoh),
                value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, iik__ahofz.value
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
    nkx__kzkol = first.unify(self, second)
    if nkx__kzkol is not None:
        return nkx__kzkol
    nkx__kzkol = second.unify(self, first)
    if nkx__kzkol is not None:
        return nkx__kzkol
    okium__yzl = self.can_convert(fromty=first, toty=second)
    if okium__yzl is not None and okium__yzl <= Conversion.safe:
        return second
    okium__yzl = self.can_convert(fromty=second, toty=first)
    if okium__yzl is not None and okium__yzl <= Conversion.safe:
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
    ber__fmjf = payload.used
    listobj = c.pyapi.list_new(ber__fmjf)
    cpyln__qnjs = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(cpyln__qnjs, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(ber__fmjf.
            type, 0))
        with payload._iterate() as ovrgo__kqb:
            i = c.builder.load(index)
            item = ovrgo__kqb.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return cpyln__qnjs, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    fserw__yodme = h.type
    lzo__ydlhe = self.mask
    dtype = self._ty.dtype
    tuqhu__vwz = context.typing_context
    fnty = tuqhu__vwz.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(tuqhu__vwz, (dtype, dtype), {})
    sxa__avpio = context.get_function(fnty, sig)
    xqzj__wjugh = ir.Constant(fserw__yodme, 1)
    rfm__zpl = ir.Constant(fserw__yodme, 5)
    arfa__cthx = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, lzo__ydlhe))
    if for_insert:
        nmk__zmy = lzo__ydlhe.type(-1)
        idtl__fzrmc = cgutils.alloca_once_value(builder, nmk__zmy)
    uksmq__cyhrv = builder.append_basic_block('lookup.body')
    qvkrt__vgxj = builder.append_basic_block('lookup.found')
    jkde__xrqr = builder.append_basic_block('lookup.not_found')
    yuu__qxx = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        vcwy__zfz = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, vcwy__zfz)):
            mzbiu__gjy = sxa__avpio(builder, (item, entry.key))
            with builder.if_then(mzbiu__gjy):
                builder.branch(qvkrt__vgxj)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, vcwy__zfz)):
            builder.branch(jkde__xrqr)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, vcwy__zfz)):
                xhzqs__ftd = builder.load(idtl__fzrmc)
                xhzqs__ftd = builder.select(builder.icmp_unsigned('==',
                    xhzqs__ftd, nmk__zmy), i, xhzqs__ftd)
                builder.store(xhzqs__ftd, idtl__fzrmc)
    with cgutils.for_range(builder, ir.Constant(fserw__yodme, numba.cpython
        .setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, xqzj__wjugh)
        i = builder.and_(i, lzo__ydlhe)
        builder.store(i, index)
    builder.branch(uksmq__cyhrv)
    with builder.goto_block(uksmq__cyhrv):
        i = builder.load(index)
        check_entry(i)
        mkej__wcgh = builder.load(arfa__cthx)
        mkej__wcgh = builder.lshr(mkej__wcgh, rfm__zpl)
        i = builder.add(xqzj__wjugh, builder.mul(i, rfm__zpl))
        i = builder.and_(lzo__ydlhe, builder.add(i, mkej__wcgh))
        builder.store(i, index)
        builder.store(mkej__wcgh, arfa__cthx)
        builder.branch(uksmq__cyhrv)
    with builder.goto_block(jkde__xrqr):
        if for_insert:
            i = builder.load(index)
            xhzqs__ftd = builder.load(idtl__fzrmc)
            i = builder.select(builder.icmp_unsigned('==', xhzqs__ftd,
                nmk__zmy), i, xhzqs__ftd)
            builder.store(i, index)
        builder.branch(yuu__qxx)
    with builder.goto_block(qvkrt__vgxj):
        builder.branch(yuu__qxx)
    builder.position_at_end(yuu__qxx)
    hjt__ubz = builder.phi(ir.IntType(1), 'found')
    hjt__ubz.add_incoming(cgutils.true_bit, qvkrt__vgxj)
    hjt__ubz.add_incoming(cgutils.false_bit, jkde__xrqr)
    return hjt__ubz, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    obyah__rstrx = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    odtcb__qkqp = payload.used
    xqzj__wjugh = ir.Constant(odtcb__qkqp.type, 1)
    odtcb__qkqp = payload.used = builder.add(odtcb__qkqp, xqzj__wjugh)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, obyah__rstrx), likely=True):
        payload.fill = builder.add(payload.fill, xqzj__wjugh)
    if do_resize:
        self.upsize(odtcb__qkqp)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    hjt__ubz, i = payload._lookup(item, h, for_insert=True)
    vtl__bxj = builder.not_(hjt__ubz)
    with builder.if_then(vtl__bxj):
        entry = payload.get_entry(i)
        obyah__rstrx = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        odtcb__qkqp = payload.used
        xqzj__wjugh = ir.Constant(odtcb__qkqp.type, 1)
        odtcb__qkqp = payload.used = builder.add(odtcb__qkqp, xqzj__wjugh)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, obyah__rstrx), likely=True):
            payload.fill = builder.add(payload.fill, xqzj__wjugh)
        if do_resize:
            self.upsize(odtcb__qkqp)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    odtcb__qkqp = payload.used
    xqzj__wjugh = ir.Constant(odtcb__qkqp.type, 1)
    odtcb__qkqp = payload.used = self._builder.sub(odtcb__qkqp, xqzj__wjugh)
    if do_resize:
        self.downsize(odtcb__qkqp)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    zsru__juxbm = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, zsru__juxbm)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    cxgh__ige = payload
    cpyln__qnjs = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(cpyln__qnjs), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with cxgh__ige._iterate() as ovrgo__kqb:
        entry = ovrgo__kqb.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(cxgh__ige.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as ovrgo__kqb:
        entry = ovrgo__kqb.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    cpyln__qnjs = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(cpyln__qnjs), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    cpyln__qnjs = cgutils.alloca_once_value(builder, cgutils.true_bit)
    fserw__yodme = context.get_value_type(types.intp)
    cbcyc__vabe = ir.Constant(fserw__yodme, 0)
    xqzj__wjugh = ir.Constant(fserw__yodme, 1)
    ovzcm__klkp = context.get_data_type(types.SetPayload(self._ty))
    gemwf__bux = context.get_abi_sizeof(ovzcm__klkp)
    chey__hib = self._entrysize
    gemwf__bux -= chey__hib
    dvu__lfol, dlicb__sqxqf = cgutils.muladd_with_overflow(builder,
        nentries, ir.Constant(fserw__yodme, chey__hib), ir.Constant(
        fserw__yodme, gemwf__bux))
    with builder.if_then(dlicb__sqxqf, likely=False):
        builder.store(cgutils.false_bit, cpyln__qnjs)
    with builder.if_then(builder.load(cpyln__qnjs), likely=True):
        if realloc:
            lmayf__ibap = self._set.meminfo
            xoqe__ssjza = context.nrt.meminfo_varsize_alloc(builder,
                lmayf__ibap, size=dvu__lfol)
            fufd__tgtj = cgutils.is_null(builder, xoqe__ssjza)
        else:
            drat__ijmt = _imp_dtor(context, builder.module, self._ty)
            lmayf__ibap = context.nrt.meminfo_new_varsize_dtor(builder,
                dvu__lfol, builder.bitcast(drat__ijmt, cgutils.voidptr_t))
            fufd__tgtj = cgutils.is_null(builder, lmayf__ibap)
        with builder.if_else(fufd__tgtj, likely=False) as (sym__ydbt,
            hlaah__riogr):
            with sym__ydbt:
                builder.store(cgutils.false_bit, cpyln__qnjs)
            with hlaah__riogr:
                if not realloc:
                    self._set.meminfo = lmayf__ibap
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, dvu__lfol, 255)
                payload.used = cbcyc__vabe
                payload.fill = cbcyc__vabe
                payload.finger = cbcyc__vabe
                dfbjt__bgdc = builder.sub(nentries, xqzj__wjugh)
                payload.mask = dfbjt__bgdc
    return builder.load(cpyln__qnjs)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    cpyln__qnjs = cgutils.alloca_once_value(builder, cgutils.true_bit)
    fserw__yodme = context.get_value_type(types.intp)
    cbcyc__vabe = ir.Constant(fserw__yodme, 0)
    xqzj__wjugh = ir.Constant(fserw__yodme, 1)
    ovzcm__klkp = context.get_data_type(types.SetPayload(self._ty))
    gemwf__bux = context.get_abi_sizeof(ovzcm__klkp)
    chey__hib = self._entrysize
    gemwf__bux -= chey__hib
    lzo__ydlhe = src_payload.mask
    nentries = builder.add(xqzj__wjugh, lzo__ydlhe)
    dvu__lfol = builder.add(ir.Constant(fserw__yodme, gemwf__bux), builder.
        mul(ir.Constant(fserw__yodme, chey__hib), nentries))
    with builder.if_then(builder.load(cpyln__qnjs), likely=True):
        drat__ijmt = _imp_dtor(context, builder.module, self._ty)
        lmayf__ibap = context.nrt.meminfo_new_varsize_dtor(builder,
            dvu__lfol, builder.bitcast(drat__ijmt, cgutils.voidptr_t))
        fufd__tgtj = cgutils.is_null(builder, lmayf__ibap)
        with builder.if_else(fufd__tgtj, likely=False) as (sym__ydbt,
            hlaah__riogr):
            with sym__ydbt:
                builder.store(cgutils.false_bit, cpyln__qnjs)
            with hlaah__riogr:
                self._set.meminfo = lmayf__ibap
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = cbcyc__vabe
                payload.mask = lzo__ydlhe
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, chey__hib)
                with src_payload._iterate() as ovrgo__kqb:
                    context.nrt.incref(builder, self._ty.dtype, ovrgo__kqb.
                        entry.key)
    return builder.load(cpyln__qnjs)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    chllq__ydv = context.get_value_type(types.voidptr)
    otpys__dbln = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [chllq__ydv, otpys__dbln, chllq__ydv]
        )
    tgjzk__louzy = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=tgjzk__louzy)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        wvnwk__ycnj = builder.bitcast(fn.args[0], cgutils.voidptr_t.
            as_pointer())
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, wvnwk__ycnj)
        with payload._iterate() as ovrgo__kqb:
            entry = ovrgo__kqb.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    xdres__qfpzr, = sig.args
    izte__wsgbw, = args
    sjoe__htlfb = numba.core.imputils.call_len(context, builder,
        xdres__qfpzr, izte__wsgbw)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, sjoe__htlfb)
    with numba.core.imputils.for_iter(context, builder, xdres__qfpzr,
        izte__wsgbw) as ovrgo__kqb:
        inst.add(ovrgo__kqb.value)
        context.nrt.decref(builder, set_type.dtype, ovrgo__kqb.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    xdres__qfpzr = sig.args[1]
    izte__wsgbw = args[1]
    sjoe__htlfb = numba.core.imputils.call_len(context, builder,
        xdres__qfpzr, izte__wsgbw)
    if sjoe__htlfb is not None:
        akxi__zvpy = builder.add(inst.payload.used, sjoe__htlfb)
        inst.upsize(akxi__zvpy)
    with numba.core.imputils.for_iter(context, builder, xdres__qfpzr,
        izte__wsgbw) as ovrgo__kqb:
        eby__esiwh = context.cast(builder, ovrgo__kqb.value, xdres__qfpzr.
            dtype, inst.dtype)
        inst.add(eby__esiwh)
        context.nrt.decref(builder, xdres__qfpzr.dtype, ovrgo__kqb.value)
    if sjoe__htlfb is not None:
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
    fydgw__omayx = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, fydgw__omayx, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    jijlm__nrl = target_context.get_executable(library, fndesc, env)
    qba__bjd = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=jijlm__nrl, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return qba__bjd


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
