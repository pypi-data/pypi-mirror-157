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
        oaljr__dsnbe = 'bodo' if distributed else 'bodo_seq'
        oaljr__dsnbe = (oaljr__dsnbe + '_inline' if inline_calls_pass else
            oaljr__dsnbe)
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state,
            oaljr__dsnbe)
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
    for gjkzo__wmycn, (txqus__jjp, vsy__qsrpr) in enumerate(pm.passes):
        if txqus__jjp == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(gjkzo__wmycn, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for gjkzo__wmycn, (txqus__jjp, vsy__qsrpr) in enumerate(pm.passes):
        if txqus__jjp == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[gjkzo__wmycn] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for gjkzo__wmycn, (txqus__jjp, vsy__qsrpr) in enumerate(pm.passes):
        if txqus__jjp == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(gjkzo__wmycn)
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
    ipw__qzp = guard(get_definition, func_ir, rhs.func)
    if isinstance(ipw__qzp, (ir.Global, ir.FreeVar, ir.Const)):
        uxqmd__yqwb = ipw__qzp.value
    else:
        jaw__vtk = guard(find_callname, func_ir, rhs)
        if not (jaw__vtk and isinstance(jaw__vtk[0], str) and isinstance(
            jaw__vtk[1], str)):
            return
        func_name, func_mod = jaw__vtk
        try:
            import importlib
            isuh__lej = importlib.import_module(func_mod)
            uxqmd__yqwb = getattr(isuh__lej, func_name)
        except:
            return
    if isinstance(uxqmd__yqwb, CPUDispatcher) and issubclass(uxqmd__yqwb.
        _compiler.pipeline_class, BodoCompiler
        ) and uxqmd__yqwb._compiler.pipeline_class != BodoCompilerUDF:
        uxqmd__yqwb._compiler.pipeline_class = BodoCompilerUDF
        uxqmd__yqwb.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for bsg__pbei in block.body:
                if is_call_assign(bsg__pbei):
                    _convert_bodo_dispatcher_to_udf(bsg__pbei.value, state.
                        func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        gesbm__ggtr = UntypedPass(state.func_ir, state.typingctx, state.
            args, state.locals, state.metadata, state.flags)
        gesbm__ggtr.run()
        return True


def _update_definitions(func_ir, node_list):
    gbjm__myzzx = ir.Loc('', 0)
    sjbb__oip = ir.Block(ir.Scope(None, gbjm__myzzx), gbjm__myzzx)
    sjbb__oip.body = node_list
    build_definitions({(0): sjbb__oip}, func_ir._definitions)


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
        han__wzqbn = 'overload_series_' + rhs.attr
        qzsc__sjzie = getattr(bodo.hiframes.series_impl, han__wzqbn)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        han__wzqbn = 'overload_dataframe_' + rhs.attr
        qzsc__sjzie = getattr(bodo.hiframes.dataframe_impl, han__wzqbn)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    rjd__vtby = qzsc__sjzie(rhs_type)
    bwe__hcn = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    gsbf__msqli = compile_func_single_block(rjd__vtby, (rhs.value,), stmt.
        target, bwe__hcn)
    _update_definitions(func_ir, gsbf__msqli)
    new_body += gsbf__msqli
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
        kgto__hyg = tuple(typemap[tfxga__gfprj.name] for tfxga__gfprj in
            rhs.args)
        ujoym__myifx = {oaljr__dsnbe: typemap[tfxga__gfprj.name] for 
            oaljr__dsnbe, tfxga__gfprj in dict(rhs.kws).items()}
        rjd__vtby = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*kgto__hyg, **ujoym__myifx)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        kgto__hyg = tuple(typemap[tfxga__gfprj.name] for tfxga__gfprj in
            rhs.args)
        ujoym__myifx = {oaljr__dsnbe: typemap[tfxga__gfprj.name] for 
            oaljr__dsnbe, tfxga__gfprj in dict(rhs.kws).items()}
        rjd__vtby = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*kgto__hyg, **ujoym__myifx)
    else:
        return False
    tgswr__xls = replace_func(pass_info, rjd__vtby, rhs.args, pysig=numba.
        core.utils.pysignature(rjd__vtby), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    topx__kmhi, vsy__qsrpr = inline_closure_call(func_ir, tgswr__xls.glbls,
        block, len(new_body), tgswr__xls.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=tgswr__xls.arg_types, typemap=typemap,
        calltypes=calltypes, work_list=work_list)
    for lotv__yhbn in topx__kmhi.values():
        lotv__yhbn.loc = rhs.loc
        update_locs(lotv__yhbn.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    lhak__rixtv = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = lhak__rixtv(func_ir, typemap)
    pfar__sxgj = func_ir.blocks
    work_list = list((tddnq__gxhac, pfar__sxgj[tddnq__gxhac]) for
        tddnq__gxhac in reversed(pfar__sxgj.keys()))
    while work_list:
        qei__ccafn, block = work_list.pop()
        new_body = []
        bcce__rcuk = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                jaw__vtk = guard(find_callname, func_ir, rhs, typemap)
                if jaw__vtk is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = jaw__vtk
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    bcce__rcuk = True
                    break
            new_body.append(stmt)
        if not bcce__rcuk:
            pfar__sxgj[qei__ccafn].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        ctckg__tcq = DistributedPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = ctckg__tcq.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        fpstx__ffyc = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        vdqs__rgm = fpstx__ffyc.run()
        wmaj__utlm = vdqs__rgm
        if wmaj__utlm:
            wmaj__utlm = fpstx__ffyc.run()
        if wmaj__utlm:
            fpstx__ffyc.run()
        return vdqs__rgm


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        jbtr__xcjru = 0
        jveu__fecxe = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            jbtr__xcjru = int(os.environ[jveu__fecxe])
        except:
            pass
        if jbtr__xcjru > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(jbtr__xcjru,
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
        bwe__hcn = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, bwe__hcn)
        for block in state.func_ir.blocks.values():
            new_body = []
            for bsg__pbei in block.body:
                if type(bsg__pbei) in distributed_run_extensions:
                    mylv__vusy = distributed_run_extensions[type(bsg__pbei)]
                    rckox__dgtyb = mylv__vusy(bsg__pbei, None, state.
                        typemap, state.calltypes, state.typingctx, state.
                        targetctx)
                    new_body += rckox__dgtyb
                elif is_call_assign(bsg__pbei):
                    rhs = bsg__pbei.value
                    jaw__vtk = guard(find_callname, state.func_ir, rhs)
                    if jaw__vtk == ('gatherv', 'bodo') or jaw__vtk == (
                        'allgatherv', 'bodo'):
                        ugiar__lrmyi = state.typemap[bsg__pbei.target.name]
                        wmua__tza = state.typemap[rhs.args[0].name]
                        if isinstance(wmua__tza, types.Array) and isinstance(
                            ugiar__lrmyi, types.Array):
                            qnr__iexte = wmua__tza.copy(readonly=False)
                            iaz__ukah = ugiar__lrmyi.copy(readonly=False)
                            if qnr__iexte == iaz__ukah:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), bsg__pbei.target, bwe__hcn)
                                continue
                        if (ugiar__lrmyi != wmua__tza and 
                            to_str_arr_if_dict_array(ugiar__lrmyi) ==
                            to_str_arr_if_dict_array(wmua__tza)):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), bsg__pbei.target, bwe__hcn,
                                extra_globals={'decode_if_dict_array':
                                decode_if_dict_array})
                            continue
                        else:
                            bsg__pbei.value = rhs.args[0]
                    new_body.append(bsg__pbei)
                else:
                    new_body.append(bsg__pbei)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        vjd__rnek = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes)
        return vjd__rnek.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    mipg__srv = set()
    while work_list:
        qei__ccafn, block = work_list.pop()
        mipg__srv.add(qei__ccafn)
        for i, qaw__vpy in enumerate(block.body):
            if isinstance(qaw__vpy, ir.Assign):
                yxxez__wnpg = qaw__vpy.value
                if isinstance(yxxez__wnpg, ir.Expr
                    ) and yxxez__wnpg.op == 'call':
                    ipw__qzp = guard(get_definition, func_ir, yxxez__wnpg.func)
                    if isinstance(ipw__qzp, (ir.Global, ir.FreeVar)
                        ) and isinstance(ipw__qzp.value, CPUDispatcher
                        ) and issubclass(ipw__qzp.value._compiler.
                        pipeline_class, BodoCompiler):
                        efq__bfm = ipw__qzp.value.py_func
                        arg_types = None
                        if typingctx:
                            mjav__pmke = dict(yxxez__wnpg.kws)
                            djs__mug = tuple(typemap[tfxga__gfprj.name] for
                                tfxga__gfprj in yxxez__wnpg.args)
                            vbb__npimt = {eegz__voq: typemap[tfxga__gfprj.
                                name] for eegz__voq, tfxga__gfprj in
                                mjav__pmke.items()}
                            vsy__qsrpr, arg_types = (ipw__qzp.value.
                                fold_argument_types(djs__mug, vbb__npimt))
                        vsy__qsrpr, ziw__rsqu = inline_closure_call(func_ir,
                            efq__bfm.__globals__, block, i, efq__bfm,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((ziw__rsqu[eegz__voq].name,
                            tfxga__gfprj) for eegz__voq, tfxga__gfprj in
                            ipw__qzp.value.locals.items() if eegz__voq in
                            ziw__rsqu)
                        break
    return mipg__srv


def udf_jit(signature_or_function=None, **options):
    otjc__duswp = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=otjc__duswp,
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
    for gjkzo__wmycn, (txqus__jjp, vsy__qsrpr) in enumerate(pm.passes):
        if txqus__jjp == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:gjkzo__wmycn + 1]
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
    pctne__bmdha = None
    kos__tvdo = None
    _locals = {}
    geupl__xknpy = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(geupl__xknpy, arg_types,
        kw_types)
    szbb__rtgry = numba.core.compiler.Flags()
    ibexp__tll = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    igux__spjmr = {'nopython': True, 'boundscheck': False, 'parallel':
        ibexp__tll}
    numba.core.registry.cpu_target.options.parse_as_flags(szbb__rtgry,
        igux__spjmr)
    igwk__zit = TyperCompiler(typingctx, targetctx, pctne__bmdha, args,
        kos__tvdo, szbb__rtgry, _locals)
    return igwk__zit.compile_extra(func)
