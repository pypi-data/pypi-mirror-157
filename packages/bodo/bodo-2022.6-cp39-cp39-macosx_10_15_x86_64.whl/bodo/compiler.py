"""
Defines Bodo's compiler pipeline.
"""
import os
import warnings
from collections import namedtuple
import numba
from numba.core import ir, ir_utils, types
from numba.core.compiler import DefaultPassBuilder
from numba.core.compiler_machinery import AnalysisPass, FunctionPass, register_pass
from numba.core.inline_closurecall import inline_closure_call
from numba.core.ir_utils import build_definitions, find_callname, get_definition, guard
from numba.core.registry import CPUDispatcher
from numba.core.typed_passes import DumpParforDiagnostics, InlineOverloads, IRLegalization, NopythonTypeInference, ParforPass, PreParforPass
from numba.core.untyped_passes import MakeFunctionToJitFunction, ReconstructSSA, WithLifting
import bodo
import bodo.hiframes.dataframe_indexing
import bodo.hiframes.datetime_datetime_ext
import bodo.hiframes.datetime_timedelta_ext
import bodo.io
import bodo.libs
import bodo.libs.array_kernels
import bodo.libs.int_arr_ext
import bodo.libs.re_ext
import bodo.libs.spark_extra
import bodo.transforms
import bodo.transforms.series_pass
import bodo.transforms.untyped_pass
import bodo.utils
import bodo.utils.table_utils
import bodo.utils.typing
from bodo.transforms.series_pass import SeriesPass
from bodo.transforms.table_column_del_pass import TableColumnDelPass
from bodo.transforms.typing_pass import BodoTypeInference
from bodo.transforms.untyped_pass import UntypedPass
from bodo.utils.utils import is_assign, is_call_assign, is_expr
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
        baq__uuioi = 'bodo' if distributed else 'bodo_seq'
        baq__uuioi = (baq__uuioi + '_inline' if inline_calls_pass else
            baq__uuioi)
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, baq__uuioi
            )
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
    for knzl__pdq, (onlm__inyz, nss__jxnb) in enumerate(pm.passes):
        if onlm__inyz == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(knzl__pdq, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for knzl__pdq, (onlm__inyz, nss__jxnb) in enumerate(pm.passes):
        if onlm__inyz == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[knzl__pdq] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for knzl__pdq, (onlm__inyz, nss__jxnb) in enumerate(pm.passes):
        if onlm__inyz == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(knzl__pdq)
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
    irkk__pdnpy = guard(get_definition, func_ir, rhs.func)
    if isinstance(irkk__pdnpy, (ir.Global, ir.FreeVar, ir.Const)):
        gkp__wrbe = irkk__pdnpy.value
    else:
        ksrre__xkx = guard(find_callname, func_ir, rhs)
        if not (ksrre__xkx and isinstance(ksrre__xkx[0], str) and
            isinstance(ksrre__xkx[1], str)):
            return
        func_name, func_mod = ksrre__xkx
        try:
            import importlib
            fgl__ttpel = importlib.import_module(func_mod)
            gkp__wrbe = getattr(fgl__ttpel, func_name)
        except:
            return
    if isinstance(gkp__wrbe, CPUDispatcher) and issubclass(gkp__wrbe.
        _compiler.pipeline_class, BodoCompiler
        ) and gkp__wrbe._compiler.pipeline_class != BodoCompilerUDF:
        gkp__wrbe._compiler.pipeline_class = BodoCompilerUDF
        gkp__wrbe.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for rfau__fwlq in block.body:
                if is_call_assign(rfau__fwlq):
                    _convert_bodo_dispatcher_to_udf(rfau__fwlq.value, state
                        .func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        gvks__taml = UntypedPass(state.func_ir, state.typingctx, state.args,
            state.locals, state.metadata, state.flags)
        gvks__taml.run()
        return True


def _update_definitions(func_ir, node_list):
    aijbi__rhp = ir.Loc('', 0)
    zdmgu__kcmel = ir.Block(ir.Scope(None, aijbi__rhp), aijbi__rhp)
    zdmgu__kcmel.body = node_list
    build_definitions({(0): zdmgu__kcmel}, func_ir._definitions)


_series_inline_attrs = {'values', 'shape', 'size', 'empty', 'name', 'index',
    'dtype'}
_series_no_inline_methods = {'to_list', 'tolist', 'rolling', 'to_csv',
    'count', 'fillna', 'to_dict', 'map', 'apply', 'pipe', 'combine',
    'bfill', 'ffill', 'pad', 'backfill', 'mask', 'where'}
_series_method_alias = {'isnull': 'isna', 'product': 'prod', 'kurtosis':
    'kurt', 'is_monotonic': 'is_monotonic_increasing', 'notnull': 'notna'}
_dataframe_no_inline_methods = {'apply', 'itertuples', 'pipe', 'to_parquet',
    'to_sql', 'to_csv', 'to_json', 'assign', 'to_string', 'query',
    'rolling', 'mask', 'where'}
TypingInfo = namedtuple('TypingInfo', ['typingctx', 'targetctx', 'typemap',
    'calltypes', 'curr_loc'])


def _inline_bodo_getattr(stmt, rhs, rhs_type, new_body, func_ir, typingctx,
    targetctx, typemap, calltypes):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.utils.transform import compile_func_single_block
    if isinstance(rhs_type, SeriesType) and rhs.attr in _series_inline_attrs:
        bivjs__wkld = 'overload_series_' + rhs.attr
        stuho__kuyi = getattr(bodo.hiframes.series_impl, bivjs__wkld)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        bivjs__wkld = 'overload_dataframe_' + rhs.attr
        stuho__kuyi = getattr(bodo.hiframes.dataframe_impl, bivjs__wkld)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    uxstj__zqh = stuho__kuyi(rhs_type)
    yaiy__iet = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    ynjf__rtxy = compile_func_single_block(uxstj__zqh, (rhs.value,), stmt.
        target, yaiy__iet)
    _update_definitions(func_ir, ynjf__rtxy)
    new_body += ynjf__rtxy
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
        ekbbi__nzw = tuple(typemap[oehny__gjt.name] for oehny__gjt in rhs.args)
        zmzx__ryqe = {baq__uuioi: typemap[oehny__gjt.name] for baq__uuioi,
            oehny__gjt in dict(rhs.kws).items()}
        uxstj__zqh = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*ekbbi__nzw, **zmzx__ryqe)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        ekbbi__nzw = tuple(typemap[oehny__gjt.name] for oehny__gjt in rhs.args)
        zmzx__ryqe = {baq__uuioi: typemap[oehny__gjt.name] for baq__uuioi,
            oehny__gjt in dict(rhs.kws).items()}
        uxstj__zqh = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*ekbbi__nzw, **zmzx__ryqe)
    else:
        return False
    wosa__aoaju = replace_func(pass_info, uxstj__zqh, rhs.args, pysig=numba
        .core.utils.pysignature(uxstj__zqh), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    lpbv__rrho, nss__jxnb = inline_closure_call(func_ir, wosa__aoaju.glbls,
        block, len(new_body), wosa__aoaju.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=wosa__aoaju.arg_types, typemap=
        typemap, calltypes=calltypes, work_list=work_list)
    for zvsv__snbzb in lpbv__rrho.values():
        zvsv__snbzb.loc = rhs.loc
        update_locs(zvsv__snbzb.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    rsvg__dao = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = rsvg__dao(func_ir, typemap)
    cuwl__gzq = func_ir.blocks
    work_list = list((noncp__kdgg, cuwl__gzq[noncp__kdgg]) for noncp__kdgg in
        reversed(cuwl__gzq.keys()))
    while work_list:
        vsylc__dqeq, block = work_list.pop()
        new_body = []
        cdzr__ebhsn = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                ksrre__xkx = guard(find_callname, func_ir, rhs, typemap)
                if ksrre__xkx is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = ksrre__xkx
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    cdzr__ebhsn = True
                    break
            new_body.append(stmt)
        if not cdzr__ebhsn:
            cuwl__gzq[vsylc__dqeq].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        rbajp__eflaf = DistributedPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes, state.
            return_type, state.metadata, state.flags)
        state.return_type = rbajp__eflaf.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        cisdz__okcs = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        oig__ciot = cisdz__okcs.run()
        wxwf__shkm = oig__ciot
        if wxwf__shkm:
            wxwf__shkm = cisdz__okcs.run()
        if wxwf__shkm:
            cisdz__okcs.run()
        return oig__ciot


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        ufp__ljgdj = 0
        dpe__maq = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            ufp__ljgdj = int(os.environ[dpe__maq])
        except:
            pass
        if ufp__ljgdj > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(ufp__ljgdj,
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
        from bodo.utils.transform import compile_func_single_block
        from bodo.utils.typing import decode_if_dict_array, to_str_arr_if_dict_array
        state.func_ir._definitions = build_definitions(state.func_ir.blocks)
        yaiy__iet = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, yaiy__iet)
        for block in state.func_ir.blocks.values():
            new_body = []
            for rfau__fwlq in block.body:
                if type(rfau__fwlq) in distributed_run_extensions:
                    gju__kloh = distributed_run_extensions[type(rfau__fwlq)]
                    fezkh__ctz = gju__kloh(rfau__fwlq, None, state.typemap,
                        state.calltypes, state.typingctx, state.targetctx)
                    new_body += fezkh__ctz
                elif is_call_assign(rfau__fwlq):
                    rhs = rfau__fwlq.value
                    ksrre__xkx = guard(find_callname, state.func_ir, rhs)
                    if ksrre__xkx == ('gatherv', 'bodo') or ksrre__xkx == (
                        'allgatherv', 'bodo'):
                        bin__haiat = state.typemap[rfau__fwlq.target.name]
                        hfiww__tdq = state.typemap[rhs.args[0].name]
                        if isinstance(hfiww__tdq, types.Array) and isinstance(
                            bin__haiat, types.Array):
                            uvi__vkoc = hfiww__tdq.copy(readonly=False)
                            qlanr__rgtpr = bin__haiat.copy(readonly=False)
                            if uvi__vkoc == qlanr__rgtpr:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), rfau__fwlq.target, yaiy__iet)
                                continue
                        if (bin__haiat != hfiww__tdq and 
                            to_str_arr_if_dict_array(bin__haiat) ==
                            to_str_arr_if_dict_array(hfiww__tdq)):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), rfau__fwlq.target,
                                yaiy__iet, extra_globals={
                                'decode_if_dict_array': decode_if_dict_array})
                            continue
                        else:
                            rfau__fwlq.value = rhs.args[0]
                    new_body.append(rfau__fwlq)
                else:
                    new_body.append(rfau__fwlq)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        xusua__sfg = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes)
        return xusua__sfg.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    exgd__fuzo = set()
    while work_list:
        vsylc__dqeq, block = work_list.pop()
        exgd__fuzo.add(vsylc__dqeq)
        for i, hffyc__cwza in enumerate(block.body):
            if isinstance(hffyc__cwza, ir.Assign):
                mbbl__xhzbn = hffyc__cwza.value
                if isinstance(mbbl__xhzbn, ir.Expr
                    ) and mbbl__xhzbn.op == 'call':
                    irkk__pdnpy = guard(get_definition, func_ir,
                        mbbl__xhzbn.func)
                    if isinstance(irkk__pdnpy, (ir.Global, ir.FreeVar)
                        ) and isinstance(irkk__pdnpy.value, CPUDispatcher
                        ) and issubclass(irkk__pdnpy.value._compiler.
                        pipeline_class, BodoCompiler):
                        eda__vnld = irkk__pdnpy.value.py_func
                        arg_types = None
                        if typingctx:
                            xhykw__mxv = dict(mbbl__xhzbn.kws)
                            izie__lkp = tuple(typemap[oehny__gjt.name] for
                                oehny__gjt in mbbl__xhzbn.args)
                            ejh__tmkt = {xaave__taqdk: typemap[oehny__gjt.
                                name] for xaave__taqdk, oehny__gjt in
                                xhykw__mxv.items()}
                            nss__jxnb, arg_types = (irkk__pdnpy.value.
                                fold_argument_types(izie__lkp, ejh__tmkt))
                        nss__jxnb, aapi__hwk = inline_closure_call(func_ir,
                            eda__vnld.__globals__, block, i, eda__vnld,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((aapi__hwk[xaave__taqdk].name,
                            oehny__gjt) for xaave__taqdk, oehny__gjt in
                            irkk__pdnpy.value.locals.items() if 
                            xaave__taqdk in aapi__hwk)
                        break
    return exgd__fuzo


def udf_jit(signature_or_function=None, **options):
    jfb__gbnni = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=jfb__gbnni,
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
    for knzl__pdq, (onlm__inyz, nss__jxnb) in enumerate(pm.passes):
        if onlm__inyz == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:knzl__pdq + 1]
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
    obmhn__xzz = None
    cpz__kulzc = None
    _locals = {}
    hnh__tcas = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(hnh__tcas, arg_types,
        kw_types)
    big__bfhmg = numba.core.compiler.Flags()
    qquio__kmxnt = {'comprehension': True, 'setitem': False,
        'inplace_binop': False, 'reduction': True, 'numpy': True, 'stencil':
        False, 'fusion': True}
    uilfs__wxm = {'nopython': True, 'boundscheck': False, 'parallel':
        qquio__kmxnt}
    numba.core.registry.cpu_target.options.parse_as_flags(big__bfhmg,
        uilfs__wxm)
    dulhq__bodd = TyperCompiler(typingctx, targetctx, obmhn__xzz, args,
        cpz__kulzc, big__bfhmg, _locals)
    return dulhq__bodd.compile_extra(func)
