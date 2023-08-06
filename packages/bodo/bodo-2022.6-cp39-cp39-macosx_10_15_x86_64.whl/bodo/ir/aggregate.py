"""IR node for the groupby, pivot and cross_tabulation"""
import ctypes
import operator
import types as pytypes
from collections import defaultdict, namedtuple
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, compiler, ir, ir_utils, types
from numba.core.analysis import compute_use_defs
from numba.core.ir_utils import build_definitions, compile_to_numba_ir, find_callname, find_const, find_topo_order, get_definition, get_ir_of_code, get_name_var_table, guard, is_getitem, mk_unique_var, next_label, remove_dels, replace_arg_nodes, replace_var_names, replace_vars_inner, visit_vars_inner
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, lower_builtin
from numba.parfors.parfor import Parfor, unwrap_parfor_blocks, wrap_parfor_blocks
import bodo
from bodo.hiframes.datetime_date_ext import DatetimeDateArrayType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, groupby_and_aggregate, info_from_table, info_to_array, pivot_groupby_and_aggregate
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, pre_alloc_array_item_array
from bodo.libs.binary_arr_ext import BinaryArrayType, pre_alloc_binary_array
from bodo.libs.bool_arr_ext import BooleanArrayType
from bodo.libs.decimal_arr_ext import DecimalArrayType, alloc_decimal_array
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.utils.transform import get_call_expr_arg
from bodo.utils.typing import BodoError, decode_if_dict_array, get_literal_value, get_overload_const_func, get_overload_const_list, get_overload_const_str, get_overload_constant_dict, is_overload_constant_dict, is_overload_constant_list, is_overload_constant_str, list_cumulative, to_str_arr_if_dict_array
from bodo.utils.utils import debug_prints, incref, is_assign, is_call_assign, is_expr, is_null_pointer, is_var_assign, sanitize_varname, unliteral_all
gb_agg_cfunc = {}
gb_agg_cfunc_addr = {}


@intrinsic
def add_agg_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        sig = func.signature
        if sig == types.none(types.voidptr):
            aai__nzkac = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            jqf__zbez = cgutils.get_or_insert_function(builder.module,
                aai__nzkac, sym._literal_value)
            builder.call(jqf__zbez, [context.get_constant_null(sig.args[0])])
        elif sig == types.none(types.int64, types.voidptr, types.voidptr):
            aai__nzkac = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            jqf__zbez = cgutils.get_or_insert_function(builder.module,
                aai__nzkac, sym._literal_value)
            builder.call(jqf__zbez, [context.get_constant(types.int64, 0),
                context.get_constant_null(sig.args[1]), context.
                get_constant_null(sig.args[2])])
        else:
            aai__nzkac = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            jqf__zbez = cgutils.get_or_insert_function(builder.module,
                aai__nzkac, sym._literal_value)
            builder.call(jqf__zbez, [context.get_constant_null(sig.args[0]),
                context.get_constant_null(sig.args[1]), context.
                get_constant_null(sig.args[2])])
        context.add_linking_libs([gb_agg_cfunc[sym._literal_value]._library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_agg_udf_addr(name):
    with numba.objmode(addr='int64'):
        addr = gb_agg_cfunc_addr[name]
    return addr


class AggUDFStruct(object):

    def __init__(self, regular_udf_funcs=None, general_udf_funcs=None):
        assert regular_udf_funcs is not None or general_udf_funcs is not None
        self.regular_udfs = False
        self.general_udfs = False
        self.regular_udf_cfuncs = None
        self.general_udf_cfunc = None
        if regular_udf_funcs is not None:
            (self.var_typs, self.init_func, self.update_all_func, self.
                combine_all_func, self.eval_all_func) = regular_udf_funcs
            self.regular_udfs = True
        if general_udf_funcs is not None:
            self.general_udf_funcs = general_udf_funcs
            self.general_udfs = True

    def set_regular_cfuncs(self, update_cb, combine_cb, eval_cb):
        assert self.regular_udfs and self.regular_udf_cfuncs is None
        self.regular_udf_cfuncs = [update_cb, combine_cb, eval_cb]

    def set_general_cfunc(self, general_udf_cb):
        assert self.general_udfs and self.general_udf_cfunc is None
        self.general_udf_cfunc = general_udf_cb


AggFuncStruct = namedtuple('AggFuncStruct', ['func', 'ftype'])
supported_agg_funcs = ['no_op', 'head', 'transform', 'size', 'shift', 'sum',
    'count', 'nunique', 'median', 'cumsum', 'cumprod', 'cummin', 'cummax',
    'mean', 'min', 'max', 'prod', 'first', 'last', 'idxmin', 'idxmax',
    'var', 'std', 'udf', 'gen_udf']
supported_transform_funcs = ['no_op', 'sum', 'count', 'nunique', 'median',
    'mean', 'min', 'max', 'prod', 'first', 'last', 'var', 'std']


def get_agg_func(func_ir, func_name, rhs, series_type=None, typemap=None):
    if func_name == 'no_op':
        raise BodoError('Unknown aggregation function used in groupby.')
    if series_type is None:
        series_type = SeriesType(types.float64)
    if func_name in {'var', 'std'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 3
        func.ncols_post_shuffle = 4
        return func
    if func_name in {'first', 'last'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        return func
    if func_name in {'idxmin', 'idxmax'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 2
        func.ncols_post_shuffle = 2
        return func
    if func_name in supported_agg_funcs[:-8]:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        gpau__xeqn = True
        nnhg__qbch = 1
        kwk__xte = -1
        if isinstance(rhs, ir.Expr):
            for meh__yvdy in rhs.kws:
                if func_name in list_cumulative:
                    if meh__yvdy[0] == 'skipna':
                        gpau__xeqn = guard(find_const, func_ir, meh__yvdy[1])
                        if not isinstance(gpau__xeqn, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if meh__yvdy[0] == 'dropna':
                        gpau__xeqn = guard(find_const, func_ir, meh__yvdy[1])
                        if not isinstance(gpau__xeqn, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            nnhg__qbch = get_call_expr_arg('shift', rhs.args, dict(rhs.kws),
                0, 'periods', nnhg__qbch)
            nnhg__qbch = guard(find_const, func_ir, nnhg__qbch)
        if func_name == 'head':
            kwk__xte = get_call_expr_arg('head', rhs.args, dict(rhs.kws), 0,
                'n', 5)
            if not isinstance(kwk__xte, int):
                kwk__xte = guard(find_const, func_ir, kwk__xte)
            if kwk__xte < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = gpau__xeqn
        func.periods = nnhg__qbch
        func.head_n = kwk__xte
        if func_name == 'transform':
            kws = dict(rhs.kws)
            hjpgc__hilr = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            vjdo__tabd = typemap[hjpgc__hilr.name]
            jztm__hiwuc = None
            if isinstance(vjdo__tabd, str):
                jztm__hiwuc = vjdo__tabd
            elif is_overload_constant_str(vjdo__tabd):
                jztm__hiwuc = get_overload_const_str(vjdo__tabd)
            elif bodo.utils.typing.is_builtin_function(vjdo__tabd):
                jztm__hiwuc = bodo.utils.typing.get_builtin_function_name(
                    vjdo__tabd)
            if jztm__hiwuc not in bodo.ir.aggregate.supported_transform_funcs[:
                ]:
                raise BodoError(f'unsupported transform function {jztm__hiwuc}'
                    )
            func.transform_func = supported_agg_funcs.index(jztm__hiwuc)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    hjpgc__hilr = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if hjpgc__hilr == '':
        vjdo__tabd = types.none
    else:
        vjdo__tabd = typemap[hjpgc__hilr.name]
    if is_overload_constant_dict(vjdo__tabd):
        ipni__gqum = get_overload_constant_dict(vjdo__tabd)
        advx__lib = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in ipni__gqum.values()]
        return advx__lib
    if vjdo__tabd == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(vjdo__tabd, types.BaseTuple) or is_overload_constant_list(
        vjdo__tabd):
        advx__lib = []
        ttk__ulpt = 0
        if is_overload_constant_list(vjdo__tabd):
            czn__nhms = get_overload_const_list(vjdo__tabd)
        else:
            czn__nhms = vjdo__tabd.types
        for t in czn__nhms:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                advx__lib.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(czn__nhms) > 1:
                    func.fname = '<lambda_' + str(ttk__ulpt) + '>'
                    ttk__ulpt += 1
                advx__lib.append(func)
        return [advx__lib]
    if is_overload_constant_str(vjdo__tabd):
        func_name = get_overload_const_str(vjdo__tabd)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(vjdo__tabd):
        func_name = bodo.utils.typing.get_builtin_function_name(vjdo__tabd)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    assert typemap is not None, 'typemap is required for agg UDF handling'
    func = _get_const_agg_func(typemap[rhs.args[0].name], func_ir)
    func.ftype = 'udf'
    func.fname = _get_udf_name(func)
    return func


def get_agg_func_udf(func_ir, f_val, rhs, series_type, typemap):
    if isinstance(f_val, str):
        return get_agg_func(func_ir, f_val, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(f_val):
        func_name = bodo.utils.typing.get_builtin_function_name(f_val)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if isinstance(f_val, (tuple, list)):
        ttk__ulpt = 0
        jcfcm__aljh = []
        for xbsj__jcp in f_val:
            func = get_agg_func_udf(func_ir, xbsj__jcp, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{ttk__ulpt}>'
                ttk__ulpt += 1
            jcfcm__aljh.append(func)
        return jcfcm__aljh
    else:
        assert is_expr(f_val, 'make_function') or isinstance(f_val, (numba.
            core.registry.CPUDispatcher, types.Dispatcher))
        assert typemap is not None, 'typemap is required for agg UDF handling'
        func = _get_const_agg_func(f_val, func_ir)
        func.ftype = 'udf'
        func.fname = _get_udf_name(func)
        return func


def _get_udf_name(func):
    code = func.code if hasattr(func, 'code') else func.__code__
    jztm__hiwuc = code.co_name
    return jztm__hiwuc


def _get_const_agg_func(func_typ, func_ir):
    agg_func = get_overload_const_func(func_typ, func_ir)
    if is_expr(agg_func, 'make_function'):

        def agg_func_wrapper(A):
            return A
        agg_func_wrapper.__code__ = agg_func.code
        agg_func = agg_func_wrapper
        return agg_func
    return agg_func


@infer_global(type)
class TypeDt64(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if len(args) == 1 and isinstance(args[0], (types.NPDatetime, types.
            NPTimedelta)):
            yljrj__kmhui = types.DType(args[0])
            return signature(yljrj__kmhui, *args)


@numba.njit(no_cpython_wrapper=True)
def _var_combine(ssqdm_a, mean_a, nobs_a, ssqdm_b, mean_b, nobs_b):
    dts__icsgw = nobs_a + nobs_b
    zhf__ijard = (nobs_a * mean_a + nobs_b * mean_b) / dts__icsgw
    tuzx__pnes = mean_b - mean_a
    rcg__nfpe = (ssqdm_a + ssqdm_b + tuzx__pnes * tuzx__pnes * nobs_a *
        nobs_b / dts__icsgw)
    return rcg__nfpe, zhf__ijard, dts__icsgw


def __special_combine(*args):
    return


@infer_global(__special_combine)
class SpecialCombineTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *unliteral_all(args))


@lower_builtin(__special_combine, types.VarArg(types.Any))
def lower_special_combine(context, builder, sig, args):
    return context.get_dummy_value()


class Aggregate(ir.Stmt):

    def __init__(self, df_out, df_in, key_names, gb_info_in, gb_info_out,
        out_key_vars, df_out_vars, df_in_vars, key_arrs, input_has_index,
        same_index, return_key, loc, func_name, dropna=True, pivot_arr=None,
        pivot_values=None, is_crosstab=False):
        self.df_out = df_out
        self.df_in = df_in
        self.key_names = key_names
        self.gb_info_in = gb_info_in
        self.gb_info_out = gb_info_out
        self.out_key_vars = out_key_vars
        self.df_out_vars = df_out_vars
        self.df_in_vars = df_in_vars
        self.key_arrs = key_arrs
        self.input_has_index = input_has_index
        self.same_index = same_index
        self.return_key = return_key
        self.loc = loc
        self.func_name = func_name
        self.dropna = dropna
        self.pivot_arr = pivot_arr
        self.pivot_values = pivot_values
        self.is_crosstab = is_crosstab

    def __repr__(self):
        fwoa__wnjv = ''
        for qlmph__rkswx, jayzt__jvuq in self.df_out_vars.items():
            fwoa__wnjv += "'{}':{}, ".format(qlmph__rkswx, jayzt__jvuq.name)
        xgvb__hygdh = '{}{{{}}}'.format(self.df_out, fwoa__wnjv)
        pbr__jic = ''
        for qlmph__rkswx, jayzt__jvuq in self.df_in_vars.items():
            pbr__jic += "'{}':{}, ".format(qlmph__rkswx, jayzt__jvuq.name)
        srfp__iwgw = '{}{{{}}}'.format(self.df_in, pbr__jic)
        nctuq__yep = 'pivot {}:{}'.format(self.pivot_arr.name, self.
            pivot_values) if self.pivot_arr is not None else ''
        key_names = ','.join([str(pfdxt__ieyo) for pfdxt__ieyo in self.
            key_names])
        ykh__jrc = ','.join([jayzt__jvuq.name for jayzt__jvuq in self.key_arrs]
            )
        return 'aggregate: {} = {} [key: {}:{}] {}'.format(xgvb__hygdh,
            srfp__iwgw, key_names, ykh__jrc, nctuq__yep)

    def remove_out_col(self, out_col_name):
        self.df_out_vars.pop(out_col_name)
        hont__kiw, hebts__pjhiz = self.gb_info_out.pop(out_col_name)
        if hont__kiw is None and not self.is_crosstab:
            return
        qhm__wpg = self.gb_info_in[hont__kiw]
        if self.pivot_arr is not None:
            self.pivot_values.remove(out_col_name)
            for tps__uei, (func, fwoa__wnjv) in enumerate(qhm__wpg):
                try:
                    fwoa__wnjv.remove(out_col_name)
                    if len(fwoa__wnjv) == 0:
                        qhm__wpg.pop(tps__uei)
                        break
                except ValueError as zbe__itmgo:
                    continue
        else:
            for tps__uei, (func, vceal__que) in enumerate(qhm__wpg):
                if vceal__que == out_col_name:
                    qhm__wpg.pop(tps__uei)
                    break
        if len(qhm__wpg) == 0:
            self.gb_info_in.pop(hont__kiw)
            self.df_in_vars.pop(hont__kiw)


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({jayzt__jvuq.name for jayzt__jvuq in aggregate_node.
        key_arrs})
    use_set.update({jayzt__jvuq.name for jayzt__jvuq in aggregate_node.
        df_in_vars.values()})
    if aggregate_node.pivot_arr is not None:
        use_set.add(aggregate_node.pivot_arr.name)
    def_set.update({jayzt__jvuq.name for jayzt__jvuq in aggregate_node.
        df_out_vars.values()})
    if aggregate_node.out_key_vars is not None:
        def_set.update({jayzt__jvuq.name for jayzt__jvuq in aggregate_node.
            out_key_vars})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(aggregate_node, lives_no_aliases, lives,
    arg_aliases, alias_map, func_ir, typemap):
    poem__hjd = [yzz__syrut for yzz__syrut, lvrqz__pxtka in aggregate_node.
        df_out_vars.items() if lvrqz__pxtka.name not in lives]
    for uilh__nmwe in poem__hjd:
        aggregate_node.remove_out_col(uilh__nmwe)
    out_key_vars = aggregate_node.out_key_vars
    if out_key_vars is not None and all(jayzt__jvuq.name not in lives for
        jayzt__jvuq in out_key_vars):
        aggregate_node.out_key_vars = None
    if len(aggregate_node.df_out_vars
        ) == 0 and aggregate_node.out_key_vars is None:
        return None
    return aggregate_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    fopz__kvu = set(jayzt__jvuq.name for jayzt__jvuq in aggregate_node.
        df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        fopz__kvu.update({jayzt__jvuq.name for jayzt__jvuq in
            aggregate_node.out_key_vars})
    return set(), fopz__kvu


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for tps__uei in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[tps__uei] = replace_vars_inner(aggregate_node
            .key_arrs[tps__uei], var_dict)
    for yzz__syrut in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[yzz__syrut] = replace_vars_inner(
            aggregate_node.df_in_vars[yzz__syrut], var_dict)
    for yzz__syrut in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[yzz__syrut] = replace_vars_inner(
            aggregate_node.df_out_vars[yzz__syrut], var_dict)
    if aggregate_node.out_key_vars is not None:
        for tps__uei in range(len(aggregate_node.out_key_vars)):
            aggregate_node.out_key_vars[tps__uei] = replace_vars_inner(
                aggregate_node.out_key_vars[tps__uei], var_dict)
    if aggregate_node.pivot_arr is not None:
        aggregate_node.pivot_arr = replace_vars_inner(aggregate_node.
            pivot_arr, var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    if debug_prints():
        print('visiting aggregate vars for:', aggregate_node)
        print('cbdata: ', sorted(cbdata.items()))
    for tps__uei in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[tps__uei] = visit_vars_inner(aggregate_node
            .key_arrs[tps__uei], callback, cbdata)
    for yzz__syrut in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[yzz__syrut] = visit_vars_inner(aggregate_node
            .df_in_vars[yzz__syrut], callback, cbdata)
    for yzz__syrut in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[yzz__syrut] = visit_vars_inner(
            aggregate_node.df_out_vars[yzz__syrut], callback, cbdata)
    if aggregate_node.out_key_vars is not None:
        for tps__uei in range(len(aggregate_node.out_key_vars)):
            aggregate_node.out_key_vars[tps__uei] = visit_vars_inner(
                aggregate_node.out_key_vars[tps__uei], callback, cbdata)
    if aggregate_node.pivot_arr is not None:
        aggregate_node.pivot_arr = visit_vars_inner(aggregate_node.
            pivot_arr, callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    assert len(aggregate_node.df_out_vars
        ) > 0 or aggregate_node.out_key_vars is not None or aggregate_node.is_crosstab, 'empty aggregate in array analysis'
    ybpvj__qsd = []
    for ktnip__mevvc in aggregate_node.key_arrs:
        xfqaa__kwih = equiv_set.get_shape(ktnip__mevvc)
        if xfqaa__kwih:
            ybpvj__qsd.append(xfqaa__kwih[0])
    if aggregate_node.pivot_arr is not None:
        xfqaa__kwih = equiv_set.get_shape(aggregate_node.pivot_arr)
        if xfqaa__kwih:
            ybpvj__qsd.append(xfqaa__kwih[0])
    for lvrqz__pxtka in aggregate_node.df_in_vars.values():
        xfqaa__kwih = equiv_set.get_shape(lvrqz__pxtka)
        if xfqaa__kwih:
            ybpvj__qsd.append(xfqaa__kwih[0])
    if len(ybpvj__qsd) > 1:
        equiv_set.insert_equiv(*ybpvj__qsd)
    vxwes__bih = []
    ybpvj__qsd = []
    ubzr__frnp = list(aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        ubzr__frnp.extend(aggregate_node.out_key_vars)
    for lvrqz__pxtka in ubzr__frnp:
        sqt__jxufn = typemap[lvrqz__pxtka.name]
        rghuh__fbrul = array_analysis._gen_shape_call(equiv_set,
            lvrqz__pxtka, sqt__jxufn.ndim, None, vxwes__bih)
        equiv_set.insert_equiv(lvrqz__pxtka, rghuh__fbrul)
        ybpvj__qsd.append(rghuh__fbrul[0])
        equiv_set.define(lvrqz__pxtka, set())
    if len(ybpvj__qsd) > 1:
        equiv_set.insert_equiv(*ybpvj__qsd)
    return [], vxwes__bih


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    ciem__rxnbn = Distribution.OneD
    for lvrqz__pxtka in aggregate_node.df_in_vars.values():
        ciem__rxnbn = Distribution(min(ciem__rxnbn.value, array_dists[
            lvrqz__pxtka.name].value))
    for ktnip__mevvc in aggregate_node.key_arrs:
        ciem__rxnbn = Distribution(min(ciem__rxnbn.value, array_dists[
            ktnip__mevvc.name].value))
    if aggregate_node.pivot_arr is not None:
        ciem__rxnbn = Distribution(min(ciem__rxnbn.value, array_dists[
            aggregate_node.pivot_arr.name].value))
        array_dists[aggregate_node.pivot_arr.name] = ciem__rxnbn
    for lvrqz__pxtka in aggregate_node.df_in_vars.values():
        array_dists[lvrqz__pxtka.name] = ciem__rxnbn
    for ktnip__mevvc in aggregate_node.key_arrs:
        array_dists[ktnip__mevvc.name] = ciem__rxnbn
    svhx__gyib = Distribution.OneD_Var
    for lvrqz__pxtka in aggregate_node.df_out_vars.values():
        if lvrqz__pxtka.name in array_dists:
            svhx__gyib = Distribution(min(svhx__gyib.value, array_dists[
                lvrqz__pxtka.name].value))
    if aggregate_node.out_key_vars is not None:
        for lvrqz__pxtka in aggregate_node.out_key_vars:
            if lvrqz__pxtka.name in array_dists:
                svhx__gyib = Distribution(min(svhx__gyib.value, array_dists
                    [lvrqz__pxtka.name].value))
    svhx__gyib = Distribution(min(svhx__gyib.value, ciem__rxnbn.value))
    for lvrqz__pxtka in aggregate_node.df_out_vars.values():
        array_dists[lvrqz__pxtka.name] = svhx__gyib
    if aggregate_node.out_key_vars is not None:
        for kyg__tded in aggregate_node.out_key_vars:
            array_dists[kyg__tded.name] = svhx__gyib
    if svhx__gyib != Distribution.OneD_Var:
        for ktnip__mevvc in aggregate_node.key_arrs:
            array_dists[ktnip__mevvc.name] = svhx__gyib
        if aggregate_node.pivot_arr is not None:
            array_dists[aggregate_node.pivot_arr.name] = svhx__gyib
        for lvrqz__pxtka in aggregate_node.df_in_vars.values():
            array_dists[lvrqz__pxtka.name] = svhx__gyib


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for lvrqz__pxtka in agg_node.df_out_vars.values():
        definitions[lvrqz__pxtka.name].append(agg_node)
    if agg_node.out_key_vars is not None:
        for kyg__tded in agg_node.out_key_vars:
            definitions[kyg__tded.name].append(agg_node)
    return definitions


ir_utils.build_defs_extensions[Aggregate] = build_agg_definitions


def __update_redvars():
    pass


@infer_global(__update_redvars)
class UpdateDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __combine_redvars():
    pass


@infer_global(__combine_redvars)
class CombineDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __eval_res():
    pass


@infer_global(__eval_res)
class EvalDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(args[0].dtype, *args)


def agg_distributed_run(agg_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for jayzt__jvuq in (list(agg_node.df_in_vars.values()) + list(
            agg_node.df_out_vars.values()) + agg_node.key_arrs):
            if array_dists[jayzt__jvuq.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                jayzt__jvuq.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    sck__llqu = tuple(typemap[jayzt__jvuq.name] for jayzt__jvuq in agg_node
        .key_arrs)
    ddje__vbs = [jayzt__jvuq for yxsp__tna, jayzt__jvuq in agg_node.
        df_in_vars.items()]
    qqhwc__xktdj = [jayzt__jvuq for yxsp__tna, jayzt__jvuq in agg_node.
        df_out_vars.items()]
    in_col_typs = []
    advx__lib = []
    if agg_node.pivot_arr is not None:
        for hont__kiw, qhm__wpg in agg_node.gb_info_in.items():
            for func, hebts__pjhiz in qhm__wpg:
                if hont__kiw is not None:
                    in_col_typs.append(typemap[agg_node.df_in_vars[
                        hont__kiw].name])
                advx__lib.append(func)
    else:
        for hont__kiw, func in agg_node.gb_info_out.values():
            if hont__kiw is not None:
                in_col_typs.append(typemap[agg_node.df_in_vars[hont__kiw].name]
                    )
            advx__lib.append(func)
    out_col_typs = tuple(typemap[jayzt__jvuq.name] for jayzt__jvuq in
        qqhwc__xktdj)
    pivot_typ = types.none if agg_node.pivot_arr is None else typemap[agg_node
        .pivot_arr.name]
    arg_typs = tuple(sck__llqu + tuple(typemap[jayzt__jvuq.name] for
        jayzt__jvuq in ddje__vbs) + (pivot_typ,))
    in_col_typs = [to_str_arr_if_dict_array(t) for t in in_col_typs]
    zhnd__wsfkg = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for tps__uei, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            zhnd__wsfkg.update({f'in_cat_dtype_{tps__uei}': in_col_typ})
    for tps__uei, atpj__bzs in enumerate(out_col_typs):
        if isinstance(atpj__bzs, bodo.CategoricalArrayType):
            zhnd__wsfkg.update({f'out_cat_dtype_{tps__uei}': atpj__bzs})
    udf_func_struct = get_udf_func_struct(advx__lib, agg_node.
        input_has_index, in_col_typs, out_col_typs, typingctx, targetctx,
        pivot_typ, agg_node.pivot_values, agg_node.is_crosstab)
    nhiwu__pvlc = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, parallel, udf_func_struct)
    zhnd__wsfkg.update({'pd': pd, 'pre_alloc_string_array':
        pre_alloc_string_array, 'pre_alloc_binary_array':
        pre_alloc_binary_array, 'pre_alloc_array_item_array':
        pre_alloc_array_item_array, 'string_array_type': string_array_type,
        'alloc_decimal_array': alloc_decimal_array, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'coerce_to_array': bodo.utils.conversion.coerce_to_array,
        'groupby_and_aggregate': groupby_and_aggregate,
        'pivot_groupby_and_aggregate': pivot_groupby_and_aggregate,
        'info_from_table': info_from_table, 'info_to_array': info_to_array,
        'delete_info_decref_array': delete_info_decref_array,
        'delete_table': delete_table, 'add_agg_cfunc_sym':
        add_agg_cfunc_sym, 'get_agg_udf_addr': get_agg_udf_addr,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'decode_if_dict_array': decode_if_dict_array, 'out_typs': out_col_typs}
        )
    if udf_func_struct is not None:
        if udf_func_struct.regular_udfs:
            zhnd__wsfkg.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            zhnd__wsfkg.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    njiir__iduf = compile_to_numba_ir(nhiwu__pvlc, zhnd__wsfkg, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    fwtg__wrabq = []
    if agg_node.pivot_arr is None:
        zrih__ycbj = agg_node.key_arrs[0].scope
        loc = agg_node.loc
        itppp__nwkk = ir.Var(zrih__ycbj, mk_unique_var('dummy_none'), loc)
        typemap[itppp__nwkk.name] = types.none
        fwtg__wrabq.append(ir.Assign(ir.Const(None, loc), itppp__nwkk, loc))
        ddje__vbs.append(itppp__nwkk)
    else:
        ddje__vbs.append(agg_node.pivot_arr)
    replace_arg_nodes(njiir__iduf, agg_node.key_arrs + ddje__vbs)
    bzs__bsub = njiir__iduf.body[-3]
    assert is_assign(bzs__bsub) and isinstance(bzs__bsub.value, ir.Expr
        ) and bzs__bsub.value.op == 'build_tuple'
    fwtg__wrabq += njiir__iduf.body[:-3]
    ubzr__frnp = list(agg_node.df_out_vars.values())
    if agg_node.out_key_vars is not None:
        ubzr__frnp += agg_node.out_key_vars
    for tps__uei, jsdbb__ldxwe in enumerate(ubzr__frnp):
        juurf__zwgni = bzs__bsub.value.items[tps__uei]
        fwtg__wrabq.append(ir.Assign(juurf__zwgni, jsdbb__ldxwe,
            jsdbb__ldxwe.loc))
    return fwtg__wrabq


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def get_numba_set(dtype):
    pass


@infer_global(get_numba_set)
class GetNumbaSetTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        sqtii__legp = args[0]
        dtype = types.Tuple([t.dtype for t in sqtii__legp.types]
            ) if isinstance(sqtii__legp, types.BaseTuple
            ) else sqtii__legp.dtype
        if isinstance(sqtii__legp, types.BaseTuple) and len(sqtii__legp.types
            ) == 1:
            dtype = sqtii__legp.types[0].dtype
        return signature(types.Set(dtype), *args)


@lower_builtin(get_numba_set, types.Any)
def lower_get_numba_set(context, builder, sig, args):
    return numba.cpython.setobj.set_empty_constructor(context, builder, sig,
        args)


@infer_global(bool)
class BoolNoneTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        qnmpp__edbd = args[0]
        if qnmpp__edbd == types.none:
            return signature(types.boolean, *args)


@lower_builtin(bool, types.none)
def lower_column_mean_impl(context, builder, sig, args):
    mmydu__rsnjc = context.compile_internal(builder, lambda a: False, sig, args
        )
    return mmydu__rsnjc


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        xubi__akmpx = IntDtype(t.dtype).name
        assert xubi__akmpx.endswith('Dtype()')
        xubi__akmpx = xubi__akmpx[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{xubi__akmpx}'))"
            )
    elif isinstance(t, BooleanArrayType):
        return (
            'bodo.libs.bool_arr_ext.init_bool_array(np.empty(0, np.bool_), np.empty(0, np.uint8))'
            )
    elif isinstance(t, StringArrayType):
        return 'pre_alloc_string_array(1, 1)'
    elif isinstance(t, BinaryArrayType):
        return 'pre_alloc_binary_array(1, 1)'
    elif t == ArrayItemArrayType(string_array_type):
        return 'pre_alloc_array_item_array(1, (1, 1), string_array_type)'
    elif isinstance(t, DecimalArrayType):
        return 'alloc_decimal_array(1, {}, {})'.format(t.precision, t.scale)
    elif isinstance(t, DatetimeDateArrayType):
        return (
            'bodo.hiframes.datetime_date_ext.init_datetime_date_array(np.empty(1, np.int64), np.empty(1, np.uint8))'
            )
    elif isinstance(t, bodo.CategoricalArrayType):
        if t.dtype.categories is None:
            raise BodoError(
                'Groupby agg operations on Categorical types require constant categories'
                )
        jaafa__nfon = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {jaafa__nfon}_cat_dtype_{colnum})'
            )
    else:
        return 'np.empty(1, {})'.format(_get_np_dtype(t.dtype))


def _get_np_dtype(t):
    if t == types.bool_:
        return 'np.bool_'
    if t == types.NPDatetime('ns'):
        return 'dt64_dtype'
    if t == types.NPTimedelta('ns'):
        return 'td64_dtype'
    return 'np.{}'.format(t)


def gen_update_cb(udf_func_struct, allfuncs, n_keys, data_in_typs_,
    out_data_typs, do_combine, func_idx_to_in_col, label_suffix):
    nabzn__bpyrt = udf_func_struct.var_typs
    neh__hdbx = len(nabzn__bpyrt)
    vafb__cfz = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    vafb__cfz += '    if is_null_pointer(in_table):\n'
    vafb__cfz += '        return\n'
    vafb__cfz += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in nabzn__bpyrt]),
        ',' if len(nabzn__bpyrt) == 1 else '')
    hbewa__nvzd = n_keys
    hgirj__jnp = []
    redvar_offsets = []
    uyt__kzqhs = []
    if do_combine:
        for tps__uei, xbsj__jcp in enumerate(allfuncs):
            if xbsj__jcp.ftype != 'udf':
                hbewa__nvzd += xbsj__jcp.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(hbewa__nvzd, hbewa__nvzd +
                    xbsj__jcp.n_redvars))
                hbewa__nvzd += xbsj__jcp.n_redvars
                uyt__kzqhs.append(data_in_typs_[func_idx_to_in_col[tps__uei]])
                hgirj__jnp.append(func_idx_to_in_col[tps__uei] + n_keys)
    else:
        for tps__uei, xbsj__jcp in enumerate(allfuncs):
            if xbsj__jcp.ftype != 'udf':
                hbewa__nvzd += xbsj__jcp.ncols_post_shuffle
            else:
                redvar_offsets += list(range(hbewa__nvzd + 1, hbewa__nvzd +
                    1 + xbsj__jcp.n_redvars))
                hbewa__nvzd += xbsj__jcp.n_redvars + 1
                uyt__kzqhs.append(data_in_typs_[func_idx_to_in_col[tps__uei]])
                hgirj__jnp.append(func_idx_to_in_col[tps__uei] + n_keys)
    assert len(redvar_offsets) == neh__hdbx
    nzsd__avoz = len(uyt__kzqhs)
    xfkax__loj = []
    for tps__uei, t in enumerate(uyt__kzqhs):
        xfkax__loj.append(_gen_dummy_alloc(t, tps__uei, True))
    vafb__cfz += '    data_in_dummy = ({}{})\n'.format(','.join(xfkax__loj),
        ',' if len(uyt__kzqhs) == 1 else '')
    vafb__cfz += """
    # initialize redvar cols
"""
    vafb__cfz += '    init_vals = __init_func()\n'
    for tps__uei in range(neh__hdbx):
        vafb__cfz += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(tps__uei, redvar_offsets[tps__uei], tps__uei))
        vafb__cfz += '    incref(redvar_arr_{})\n'.format(tps__uei)
        vafb__cfz += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(tps__uei,
            tps__uei)
    vafb__cfz += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(tps__uei) for tps__uei in range(neh__hdbx)]), ',' if 
        neh__hdbx == 1 else '')
    vafb__cfz += '\n'
    for tps__uei in range(nzsd__avoz):
        vafb__cfz += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(tps__uei, hgirj__jnp[tps__uei], tps__uei))
        vafb__cfz += '    incref(data_in_{})\n'.format(tps__uei)
    vafb__cfz += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(tps__uei) for tps__uei in range(nzsd__avoz)]), ',' if 
        nzsd__avoz == 1 else '')
    vafb__cfz += '\n'
    vafb__cfz += '    for i in range(len(data_in_0)):\n'
    vafb__cfz += '        w_ind = row_to_group[i]\n'
    vafb__cfz += '        if w_ind != -1:\n'
    vafb__cfz += (
        '            __update_redvars(redvars, data_in, w_ind, i, pivot_arr=None)\n'
        )
    xqeuk__wkzbc = {}
    exec(vafb__cfz, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, xqeuk__wkzbc)
    return xqeuk__wkzbc['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, out_data_typs,
    label_suffix):
    nabzn__bpyrt = udf_func_struct.var_typs
    neh__hdbx = len(nabzn__bpyrt)
    vafb__cfz = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    vafb__cfz += '    if is_null_pointer(in_table):\n'
    vafb__cfz += '        return\n'
    vafb__cfz += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in nabzn__bpyrt]),
        ',' if len(nabzn__bpyrt) == 1 else '')
    gnyp__zoxeu = n_keys
    lpn__ybae = n_keys
    suvgf__finp = []
    xyz__akmbm = []
    for xbsj__jcp in allfuncs:
        if xbsj__jcp.ftype != 'udf':
            gnyp__zoxeu += xbsj__jcp.ncols_pre_shuffle
            lpn__ybae += xbsj__jcp.ncols_post_shuffle
        else:
            suvgf__finp += list(range(gnyp__zoxeu, gnyp__zoxeu + xbsj__jcp.
                n_redvars))
            xyz__akmbm += list(range(lpn__ybae + 1, lpn__ybae + 1 +
                xbsj__jcp.n_redvars))
            gnyp__zoxeu += xbsj__jcp.n_redvars
            lpn__ybae += 1 + xbsj__jcp.n_redvars
    assert len(suvgf__finp) == neh__hdbx
    vafb__cfz += """
    # initialize redvar cols
"""
    vafb__cfz += '    init_vals = __init_func()\n'
    for tps__uei in range(neh__hdbx):
        vafb__cfz += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(tps__uei, xyz__akmbm[tps__uei], tps__uei))
        vafb__cfz += '    incref(redvar_arr_{})\n'.format(tps__uei)
        vafb__cfz += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(tps__uei,
            tps__uei)
    vafb__cfz += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(tps__uei) for tps__uei in range(neh__hdbx)]), ',' if 
        neh__hdbx == 1 else '')
    vafb__cfz += '\n'
    for tps__uei in range(neh__hdbx):
        vafb__cfz += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(tps__uei, suvgf__finp[tps__uei], tps__uei))
        vafb__cfz += '    incref(recv_redvar_arr_{})\n'.format(tps__uei)
    vafb__cfz += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(tps__uei) for tps__uei in range(
        neh__hdbx)]), ',' if neh__hdbx == 1 else '')
    vafb__cfz += '\n'
    if neh__hdbx:
        vafb__cfz += '    for i in range(len(recv_redvar_arr_0)):\n'
        vafb__cfz += '        w_ind = row_to_group[i]\n'
        vafb__cfz += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i, pivot_arr=None)\n'
            )
    xqeuk__wkzbc = {}
    exec(vafb__cfz, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, xqeuk__wkzbc)
    return xqeuk__wkzbc['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    nabzn__bpyrt = udf_func_struct.var_typs
    neh__hdbx = len(nabzn__bpyrt)
    hbewa__nvzd = n_keys
    redvar_offsets = []
    kafw__fjir = []
    out_data_typs = []
    for tps__uei, xbsj__jcp in enumerate(allfuncs):
        if xbsj__jcp.ftype != 'udf':
            hbewa__nvzd += xbsj__jcp.ncols_post_shuffle
        else:
            kafw__fjir.append(hbewa__nvzd)
            redvar_offsets += list(range(hbewa__nvzd + 1, hbewa__nvzd + 1 +
                xbsj__jcp.n_redvars))
            hbewa__nvzd += 1 + xbsj__jcp.n_redvars
            out_data_typs.append(out_data_typs_[tps__uei])
    assert len(redvar_offsets) == neh__hdbx
    nzsd__avoz = len(out_data_typs)
    vafb__cfz = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    vafb__cfz += '    if is_null_pointer(table):\n'
    vafb__cfz += '        return\n'
    vafb__cfz += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in nabzn__bpyrt]),
        ',' if len(nabzn__bpyrt) == 1 else '')
    vafb__cfz += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        out_data_typs]), ',' if len(out_data_typs) == 1 else '')
    for tps__uei in range(neh__hdbx):
        vafb__cfz += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(tps__uei, redvar_offsets[tps__uei], tps__uei))
        vafb__cfz += '    incref(redvar_arr_{})\n'.format(tps__uei)
    vafb__cfz += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(tps__uei) for tps__uei in range(neh__hdbx)]), ',' if 
        neh__hdbx == 1 else '')
    vafb__cfz += '\n'
    for tps__uei in range(nzsd__avoz):
        vafb__cfz += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(tps__uei, kafw__fjir[tps__uei], tps__uei))
        vafb__cfz += '    incref(data_out_{})\n'.format(tps__uei)
    vafb__cfz += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(tps__uei) for tps__uei in range(nzsd__avoz)]), ',' if 
        nzsd__avoz == 1 else '')
    vafb__cfz += '\n'
    vafb__cfz += '    for i in range(len(data_out_0)):\n'
    vafb__cfz += '        __eval_res(redvars, data_out, i)\n'
    xqeuk__wkzbc = {}
    exec(vafb__cfz, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, xqeuk__wkzbc)
    return xqeuk__wkzbc['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    hbewa__nvzd = n_keys
    zas__kmqhv = []
    for tps__uei, xbsj__jcp in enumerate(allfuncs):
        if xbsj__jcp.ftype == 'gen_udf':
            zas__kmqhv.append(hbewa__nvzd)
            hbewa__nvzd += 1
        elif xbsj__jcp.ftype != 'udf':
            hbewa__nvzd += xbsj__jcp.ncols_post_shuffle
        else:
            hbewa__nvzd += xbsj__jcp.n_redvars + 1
    vafb__cfz = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    vafb__cfz += '    if num_groups == 0:\n'
    vafb__cfz += '        return\n'
    for tps__uei, func in enumerate(udf_func_struct.general_udf_funcs):
        vafb__cfz += '    # col {}\n'.format(tps__uei)
        vafb__cfz += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(zas__kmqhv[tps__uei], tps__uei))
        vafb__cfz += '    incref(out_col)\n'
        vafb__cfz += '    for j in range(num_groups):\n'
        vafb__cfz += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(tps__uei, tps__uei))
        vafb__cfz += '        incref(in_col)\n'
        vafb__cfz += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(tps__uei))
    zhnd__wsfkg = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    eyn__vqhk = 0
    for tps__uei, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[eyn__vqhk]
        zhnd__wsfkg['func_{}'.format(eyn__vqhk)] = func
        zhnd__wsfkg['in_col_{}_typ'.format(eyn__vqhk)] = in_col_typs[
            func_idx_to_in_col[tps__uei]]
        zhnd__wsfkg['out_col_{}_typ'.format(eyn__vqhk)] = out_col_typs[tps__uei
            ]
        eyn__vqhk += 1
    xqeuk__wkzbc = {}
    exec(vafb__cfz, zhnd__wsfkg, xqeuk__wkzbc)
    xbsj__jcp = xqeuk__wkzbc['bodo_gb_apply_general_udfs{}'.format(
        label_suffix)]
    cst__hyykl = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(cst__hyykl, nopython=True)(xbsj__jcp)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs, parallel,
    udf_func_struct):
    hegi__dknq = agg_node.pivot_arr is not None
    if agg_node.same_index:
        assert agg_node.input_has_index
    if agg_node.pivot_values is None:
        ywwo__eej = 1
    else:
        ywwo__eej = len(agg_node.pivot_values)
    ynxc__qqyvz = tuple('key_' + sanitize_varname(qlmph__rkswx) for
        qlmph__rkswx in agg_node.key_names)
    aksx__tyg = {qlmph__rkswx: 'in_{}'.format(sanitize_varname(qlmph__rkswx
        )) for qlmph__rkswx in agg_node.gb_info_in.keys() if qlmph__rkswx
         is not None}
    qviyq__nevcl = {qlmph__rkswx: ('out_' + sanitize_varname(qlmph__rkswx)) for
        qlmph__rkswx in agg_node.gb_info_out.keys()}
    n_keys = len(agg_node.key_names)
    thoiu__luhci = ', '.join(ynxc__qqyvz)
    ctdi__mefyw = ', '.join(aksx__tyg.values())
    if ctdi__mefyw != '':
        ctdi__mefyw = ', ' + ctdi__mefyw
    vafb__cfz = 'def agg_top({}{}{}, pivot_arr):\n'.format(thoiu__luhci,
        ctdi__mefyw, ', index_arg' if agg_node.input_has_index else '')
    for a in tuple(aksx__tyg.values()):
        vafb__cfz += f'    {a} = decode_if_dict_array({a})\n'
    if hegi__dknq:
        vafb__cfz += f'    pivot_arr = decode_if_dict_array(pivot_arr)\n'
        xtt__nusfz = []
        for hont__kiw, qhm__wpg in agg_node.gb_info_in.items():
            if hont__kiw is not None:
                for func, hebts__pjhiz in qhm__wpg:
                    xtt__nusfz.append(aksx__tyg[hont__kiw])
    else:
        xtt__nusfz = tuple(aksx__tyg[hont__kiw] for hont__kiw, hebts__pjhiz in
            agg_node.gb_info_out.values() if hont__kiw is not None)
    aqbyd__gahxu = ynxc__qqyvz + tuple(xtt__nusfz)
    vafb__cfz += '    info_list = [{}{}{}]\n'.format(', '.join(
        'array_to_info({})'.format(a) for a in aqbyd__gahxu), 
        ', array_to_info(index_arg)' if agg_node.input_has_index else '', 
        ', array_to_info(pivot_arr)' if agg_node.is_crosstab else '')
    vafb__cfz += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    adnt__ibucx = []
    func_idx_to_in_col = []
    jnkm__bhkct = []
    gpau__xeqn = False
    quszo__yulxr = 1
    kwk__xte = -1
    rsoc__djw = 0
    cwqt__fqqko = 0
    if not hegi__dknq:
        advx__lib = [func for hebts__pjhiz, func in agg_node.gb_info_out.
            values()]
    else:
        advx__lib = [func for func, hebts__pjhiz in qhm__wpg for qhm__wpg in
            agg_node.gb_info_in.values()]
    for ztudn__ajtrw, func in enumerate(advx__lib):
        adnt__ibucx.append(len(allfuncs))
        if func.ftype in {'median', 'nunique'}:
            do_combine = False
        if func.ftype in list_cumulative:
            rsoc__djw += 1
        if hasattr(func, 'skipdropna'):
            gpau__xeqn = func.skipdropna
        if func.ftype == 'shift':
            quszo__yulxr = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            cwqt__fqqko = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            kwk__xte = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(ztudn__ajtrw)
        if func.ftype == 'udf':
            jnkm__bhkct.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            jnkm__bhkct.append(0)
            do_combine = False
    adnt__ibucx.append(len(allfuncs))
    if agg_node.is_crosstab:
        assert len(agg_node.gb_info_out
            ) == ywwo__eej, 'invalid number of groupby outputs for pivot'
    else:
        assert len(agg_node.gb_info_out) == len(allfuncs
            ) * ywwo__eej, 'invalid number of groupby outputs'
    if rsoc__djw > 0:
        if rsoc__djw != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    for tps__uei, qlmph__rkswx in enumerate(agg_node.gb_info_out.keys()):
        sdvj__rwnr = qviyq__nevcl[qlmph__rkswx] + '_dummy'
        atpj__bzs = out_col_typs[tps__uei]
        hont__kiw, func = agg_node.gb_info_out[qlmph__rkswx]
        if isinstance(func, pytypes.SimpleNamespace) and func.fname in ['min',
            'max', 'shift'] and isinstance(atpj__bzs, bodo.CategoricalArrayType
            ):
            vafb__cfz += '    {} = {}\n'.format(sdvj__rwnr, aksx__tyg[
                hont__kiw])
        elif udf_func_struct is not None:
            vafb__cfz += '    {} = {}\n'.format(sdvj__rwnr,
                _gen_dummy_alloc(atpj__bzs, tps__uei, False))
    if udf_func_struct is not None:
        qmw__saztk = next_label()
        if udf_func_struct.regular_udfs:
            cst__hyykl = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            lcnk__zamu = numba.cfunc(cst__hyykl, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs,
                out_col_typs, do_combine, func_idx_to_in_col, qmw__saztk))
            uexkj__zzsw = numba.cfunc(cst__hyykl, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, out_col_typs, qmw__saztk))
            cdixs__uwabm = numba.cfunc('void(voidptr)', nopython=True)(
                gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_col_typs,
                qmw__saztk))
            udf_func_struct.set_regular_cfuncs(lcnk__zamu, uexkj__zzsw,
                cdixs__uwabm)
            for hunn__oaita in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[hunn__oaita.native_name] = hunn__oaita
                gb_agg_cfunc_addr[hunn__oaita.native_name
                    ] = hunn__oaita.address
        if udf_func_struct.general_udfs:
            fuzi__tcix = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, out_col_typs, func_idx_to_in_col,
                qmw__saztk)
            udf_func_struct.set_general_cfunc(fuzi__tcix)
        acdsk__utf = []
        lxjac__jic = 0
        tps__uei = 0
        for sdvj__rwnr, xbsj__jcp in zip(qviyq__nevcl.values(), allfuncs):
            if xbsj__jcp.ftype in ('udf', 'gen_udf'):
                acdsk__utf.append(sdvj__rwnr + '_dummy')
                for ygvb__iyoz in range(lxjac__jic, lxjac__jic +
                    jnkm__bhkct[tps__uei]):
                    acdsk__utf.append('data_redvar_dummy_' + str(ygvb__iyoz))
                lxjac__jic += jnkm__bhkct[tps__uei]
                tps__uei += 1
        if udf_func_struct.regular_udfs:
            nabzn__bpyrt = udf_func_struct.var_typs
            for tps__uei, t in enumerate(nabzn__bpyrt):
                vafb__cfz += ('    data_redvar_dummy_{} = np.empty(1, {})\n'
                    .format(tps__uei, _get_np_dtype(t)))
        vafb__cfz += '    out_info_list_dummy = [{}]\n'.format(', '.join(
            'array_to_info({})'.format(a) for a in acdsk__utf))
        vafb__cfz += (
            '    udf_table_dummy = arr_info_list_to_table(out_info_list_dummy)\n'
            )
        if udf_func_struct.regular_udfs:
            vafb__cfz += "    add_agg_cfunc_sym(cpp_cb_update, '{}')\n".format(
                lcnk__zamu.native_name)
            vafb__cfz += ("    add_agg_cfunc_sym(cpp_cb_combine, '{}')\n".
                format(uexkj__zzsw.native_name))
            vafb__cfz += "    add_agg_cfunc_sym(cpp_cb_eval, '{}')\n".format(
                cdixs__uwabm.native_name)
            vafb__cfz += ("    cpp_cb_update_addr = get_agg_udf_addr('{}')\n"
                .format(lcnk__zamu.native_name))
            vafb__cfz += ("    cpp_cb_combine_addr = get_agg_udf_addr('{}')\n"
                .format(uexkj__zzsw.native_name))
            vafb__cfz += ("    cpp_cb_eval_addr = get_agg_udf_addr('{}')\n"
                .format(cdixs__uwabm.native_name))
        else:
            vafb__cfz += '    cpp_cb_update_addr = 0\n'
            vafb__cfz += '    cpp_cb_combine_addr = 0\n'
            vafb__cfz += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            hunn__oaita = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[hunn__oaita.native_name] = hunn__oaita
            gb_agg_cfunc_addr[hunn__oaita.native_name] = hunn__oaita.address
            vafb__cfz += ("    add_agg_cfunc_sym(cpp_cb_general, '{}')\n".
                format(hunn__oaita.native_name))
            vafb__cfz += ("    cpp_cb_general_addr = get_agg_udf_addr('{}')\n"
                .format(hunn__oaita.native_name))
        else:
            vafb__cfz += '    cpp_cb_general_addr = 0\n'
    else:
        vafb__cfz += (
            '    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])\n'
            )
        vafb__cfz += '    cpp_cb_update_addr = 0\n'
        vafb__cfz += '    cpp_cb_combine_addr = 0\n'
        vafb__cfz += '    cpp_cb_eval_addr = 0\n'
        vafb__cfz += '    cpp_cb_general_addr = 0\n'
    vafb__cfz += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(', '
        .join([str(supported_agg_funcs.index(xbsj__jcp.ftype)) for
        xbsj__jcp in allfuncs] + ['0']))
    vafb__cfz += '    func_offsets = np.array({}, dtype=np.int32)\n'.format(str
        (adnt__ibucx))
    if len(jnkm__bhkct) > 0:
        vafb__cfz += '    udf_ncols = np.array({}, dtype=np.int32)\n'.format(
            str(jnkm__bhkct))
    else:
        vafb__cfz += '    udf_ncols = np.array([0], np.int32)\n'
    if hegi__dknq:
        vafb__cfz += '    arr_type = coerce_to_array({})\n'.format(agg_node
            .pivot_values)
        vafb__cfz += '    arr_info = array_to_info(arr_type)\n'
        vafb__cfz += (
            '    dispatch_table = arr_info_list_to_table([arr_info])\n')
        vafb__cfz += '    pivot_info = array_to_info(pivot_arr)\n'
        vafb__cfz += (
            '    dispatch_info = arr_info_list_to_table([pivot_info])\n')
        vafb__cfz += (
            """    out_table = pivot_groupby_and_aggregate(table, {}, dispatch_table, dispatch_info, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, agg_node.
            is_crosstab, gpau__xeqn, agg_node.return_key, agg_node.same_index))
        vafb__cfz += '    delete_info_decref_array(pivot_info)\n'
        vafb__cfz += '    delete_info_decref_array(arr_info)\n'
    else:
        vafb__cfz += (
            """    out_table = groupby_and_aggregate(table, {}, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, gpau__xeqn,
            quszo__yulxr, cwqt__fqqko, kwk__xte, agg_node.return_key,
            agg_node.same_index, agg_node.dropna))
    xni__bhiq = 0
    if agg_node.return_key:
        for tps__uei, cxf__jbbyu in enumerate(ynxc__qqyvz):
            vafb__cfz += (
                '    {} = info_to_array(info_from_table(out_table, {}), {})\n'
                .format(cxf__jbbyu, xni__bhiq, cxf__jbbyu))
            xni__bhiq += 1
    for tps__uei, sdvj__rwnr in enumerate(qviyq__nevcl.values()):
        if isinstance(func, pytypes.SimpleNamespace) and func.fname in ['min',
            'max', 'shift'] and isinstance(atpj__bzs, bodo.CategoricalArrayType
            ):
            vafb__cfz += f"""    {sdvj__rwnr} = info_to_array(info_from_table(out_table, {xni__bhiq}), {sdvj__rwnr + '_dummy'})
"""
        else:
            vafb__cfz += f"""    {sdvj__rwnr} = info_to_array(info_from_table(out_table, {xni__bhiq}), out_typs[{tps__uei}])
"""
        xni__bhiq += 1
    if agg_node.same_index:
        vafb__cfz += (
            """    out_index_arg = info_to_array(info_from_table(out_table, {}), index_arg)
"""
            .format(xni__bhiq))
        xni__bhiq += 1
    vafb__cfz += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    vafb__cfz += '    delete_table_decref_arrays(table)\n'
    vafb__cfz += '    delete_table_decref_arrays(udf_table_dummy)\n'
    vafb__cfz += '    delete_table(out_table)\n'
    vafb__cfz += f'    ev_clean.finalize()\n'
    txq__jhxsk = tuple(qviyq__nevcl.values())
    if agg_node.return_key:
        txq__jhxsk += tuple(ynxc__qqyvz)
    vafb__cfz += '    return ({},{})\n'.format(', '.join(txq__jhxsk), 
        ' out_index_arg,' if agg_node.same_index else '')
    xqeuk__wkzbc = {}
    exec(vafb__cfz, {'out_typs': out_col_typs}, xqeuk__wkzbc)
    xoas__bakli = xqeuk__wkzbc['agg_top']
    return xoas__bakli


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for gcj__nnzaj in block.body:
            if is_call_assign(gcj__nnzaj) and find_callname(f_ir,
                gcj__nnzaj.value) == ('len', 'builtins'
                ) and gcj__nnzaj.value.args[0].name == f_ir.arg_names[0]:
                lkoh__rbg = get_definition(f_ir, gcj__nnzaj.value.func)
                lkoh__rbg.name = 'dummy_agg_count'
                lkoh__rbg.value = dummy_agg_count
    bkm__hjotn = get_name_var_table(f_ir.blocks)
    wwfk__krq = {}
    for name, hebts__pjhiz in bkm__hjotn.items():
        wwfk__krq[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, wwfk__krq)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    qhcy__gmd = numba.core.compiler.Flags()
    qhcy__gmd.nrt = True
    mtf__fbzm = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, qhcy__gmd)
    mtf__fbzm.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, jfru__tcmgw, calltypes, hebts__pjhiz = (numba.core.
        typed_passes.type_inference_stage(typingctx, targetctx, f_ir,
        arg_typs, None))
    pcxat__kfdl = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    zdi__okjg = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    ltso__fsf = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    eerdh__yuvw = ltso__fsf(typemap, calltypes)
    pm = zdi__okjg(typingctx, targetctx, None, f_ir, typemap, jfru__tcmgw,
        calltypes, eerdh__yuvw, {}, qhcy__gmd, None)
    dtbnb__kege = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = zdi__okjg(typingctx, targetctx, None, f_ir, typemap, jfru__tcmgw,
        calltypes, eerdh__yuvw, {}, qhcy__gmd, dtbnb__kege)
    ykz__udd = numba.core.typed_passes.InlineOverloads()
    ykz__udd.run_pass(pm)
    jiuth__rkuxg = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    jiuth__rkuxg.run()
    for block in f_ir.blocks.values():
        for gcj__nnzaj in block.body:
            if is_assign(gcj__nnzaj) and isinstance(gcj__nnzaj.value, (ir.
                Arg, ir.Var)) and isinstance(typemap[gcj__nnzaj.target.name
                ], SeriesType):
                sqt__jxufn = typemap.pop(gcj__nnzaj.target.name)
                typemap[gcj__nnzaj.target.name] = sqt__jxufn.data
            if is_call_assign(gcj__nnzaj) and find_callname(f_ir,
                gcj__nnzaj.value) == ('get_series_data',
                'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[gcj__nnzaj.target.name].remove(gcj__nnzaj
                    .value)
                gcj__nnzaj.value = gcj__nnzaj.value.args[0]
                f_ir._definitions[gcj__nnzaj.target.name].append(gcj__nnzaj
                    .value)
            if is_call_assign(gcj__nnzaj) and find_callname(f_ir,
                gcj__nnzaj.value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[gcj__nnzaj.target.name].remove(gcj__nnzaj
                    .value)
                gcj__nnzaj.value = ir.Const(False, gcj__nnzaj.loc)
                f_ir._definitions[gcj__nnzaj.target.name].append(gcj__nnzaj
                    .value)
            if is_call_assign(gcj__nnzaj) and find_callname(f_ir,
                gcj__nnzaj.value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[gcj__nnzaj.target.name].remove(gcj__nnzaj
                    .value)
                gcj__nnzaj.value = ir.Const(False, gcj__nnzaj.loc)
                f_ir._definitions[gcj__nnzaj.target.name].append(gcj__nnzaj
                    .value)
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    iuvqb__ybw = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, pcxat__kfdl)
    iuvqb__ybw.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    hoazq__ojcms = numba.core.compiler.StateDict()
    hoazq__ojcms.func_ir = f_ir
    hoazq__ojcms.typemap = typemap
    hoazq__ojcms.calltypes = calltypes
    hoazq__ojcms.typingctx = typingctx
    hoazq__ojcms.targetctx = targetctx
    hoazq__ojcms.return_type = jfru__tcmgw
    numba.core.rewrites.rewrite_registry.apply('after-inference', hoazq__ojcms)
    awg__stg = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        jfru__tcmgw, typingctx, targetctx, pcxat__kfdl, qhcy__gmd, {})
    awg__stg.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            wik__kvg = ctypes.pythonapi.PyCell_Get
            wik__kvg.restype = ctypes.py_object
            wik__kvg.argtypes = ctypes.py_object,
            ipni__gqum = tuple(wik__kvg(nbs__gbah) for nbs__gbah in closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            ipni__gqum = closure.items
        assert len(code.co_freevars) == len(ipni__gqum)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, ipni__gqum
            )


class RegularUDFGenerator(object):

    def __init__(self, in_col_types, out_col_types, pivot_typ, pivot_values,
        is_crosstab, typingctx, targetctx):
        self.in_col_types = in_col_types
        self.out_col_types = out_col_types
        self.pivot_typ = pivot_typ
        self.pivot_values = pivot_values
        self.is_crosstab = is_crosstab
        self.typingctx = typingctx
        self.targetctx = targetctx
        self.all_reduce_vars = []
        self.all_vartypes = []
        self.all_init_nodes = []
        self.all_eval_funcs = []
        self.all_update_funcs = []
        self.all_combine_funcs = []
        self.curr_offset = 0
        self.redvar_offsets = [0]

    def add_udf(self, in_col_typ, func):
        ibb__zxmva = SeriesType(in_col_typ.dtype, in_col_typ, None, string_type
            )
        f_ir, pm = compile_to_optimized_ir(func, (ibb__zxmva,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        gntk__plo, arr_var = _rm_arg_agg_block(block, pm.typemap)
        phdt__thz = -1
        for tps__uei, gcj__nnzaj in enumerate(gntk__plo):
            if isinstance(gcj__nnzaj, numba.parfors.parfor.Parfor):
                assert phdt__thz == -1, 'only one parfor for aggregation function'
                phdt__thz = tps__uei
        parfor = None
        if phdt__thz != -1:
            parfor = gntk__plo[phdt__thz]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = gntk__plo[:phdt__thz] + parfor.init_block.body
        eval_nodes = gntk__plo[phdt__thz + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for gcj__nnzaj in init_nodes:
            if is_assign(gcj__nnzaj) and gcj__nnzaj.target.name in redvars:
                ind = redvars.index(gcj__nnzaj.target.name)
                reduce_vars[ind] = gcj__nnzaj.target
        var_types = [pm.typemap[jayzt__jvuq] for jayzt__jvuq in redvars]
        lxyw__yytlg = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        mye__otmtu = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        shvsb__ipoyp = gen_eval_func(f_ir, eval_nodes, reduce_vars,
            var_types, pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(shvsb__ipoyp)
        self.all_update_funcs.append(mye__otmtu)
        self.all_combine_funcs.append(lxyw__yytlg)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        self.all_vartypes = self.all_vartypes * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_vartypes
        self.all_reduce_vars = self.all_reduce_vars * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_reduce_vars
        viuxz__btpg = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        xmqq__djcrq = gen_all_update_func(self.all_update_funcs, self.
            all_vartypes, self.in_col_types, self.redvar_offsets, self.
            typingctx, self.targetctx, self.pivot_typ, self.pivot_values,
            self.is_crosstab)
        wxw__utm = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.
            targetctx, self.pivot_typ, self.pivot_values)
        ynh__eivy = gen_all_eval_func(self.all_eval_funcs, self.
            all_vartypes, self.redvar_offsets, self.out_col_types, self.
            typingctx, self.targetctx, self.pivot_values)
        return self.all_vartypes, viuxz__btpg, xmqq__djcrq, wxw__utm, ynh__eivy


class GeneralUDFGenerator(object):

    def __init__(self):
        self.funcs = []

    def add_udf(self, func):
        self.funcs.append(bodo.jit(distributed=False)(func))
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        func.n_redvars = 0

    def gen_all_func(self):
        if len(self.funcs) > 0:
            return self.funcs
        else:
            return None


def get_udf_func_struct(agg_func, input_has_index, in_col_types,
    out_col_types, typingctx, targetctx, pivot_typ, pivot_values, is_crosstab):
    if is_crosstab and len(in_col_types) == 0:
        in_col_types = [types.Array(types.intp, 1, 'C')]
    nakn__vup = []
    for t, xbsj__jcp in zip(in_col_types, agg_func):
        nakn__vup.append((t, xbsj__jcp))
    tlars__dwjm = RegularUDFGenerator(in_col_types, out_col_types,
        pivot_typ, pivot_values, is_crosstab, typingctx, targetctx)
    eodze__zporv = GeneralUDFGenerator()
    for in_col_typ, func in nakn__vup:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            tlars__dwjm.add_udf(in_col_typ, func)
        except:
            eodze__zporv.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = tlars__dwjm.gen_all_func()
    general_udf_funcs = eodze__zporv.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    rkra__nme = compute_use_defs(parfor.loop_body)
    vgqgp__hjvm = set()
    for hyf__evv in rkra__nme.usemap.values():
        vgqgp__hjvm |= hyf__evv
    eomeu__kpz = set()
    for hyf__evv in rkra__nme.defmap.values():
        eomeu__kpz |= hyf__evv
    jft__fko = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    jft__fko.body = eval_nodes
    dkczq__jpjvx = compute_use_defs({(0): jft__fko})
    auh__jqfj = dkczq__jpjvx.usemap[0]
    vmad__jfq = set()
    dewns__ypr = []
    jtrw__zvydw = []
    for gcj__nnzaj in reversed(init_nodes):
        xqaee__vbh = {jayzt__jvuq.name for jayzt__jvuq in gcj__nnzaj.
            list_vars()}
        if is_assign(gcj__nnzaj):
            jayzt__jvuq = gcj__nnzaj.target.name
            xqaee__vbh.remove(jayzt__jvuq)
            if (jayzt__jvuq in vgqgp__hjvm and jayzt__jvuq not in vmad__jfq and
                jayzt__jvuq not in auh__jqfj and jayzt__jvuq not in eomeu__kpz
                ):
                jtrw__zvydw.append(gcj__nnzaj)
                vgqgp__hjvm |= xqaee__vbh
                eomeu__kpz.add(jayzt__jvuq)
                continue
        vmad__jfq |= xqaee__vbh
        dewns__ypr.append(gcj__nnzaj)
    jtrw__zvydw.reverse()
    dewns__ypr.reverse()
    guec__wsp = min(parfor.loop_body.keys())
    cwsjk__uules = parfor.loop_body[guec__wsp]
    cwsjk__uules.body = jtrw__zvydw + cwsjk__uules.body
    return dewns__ypr


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    heglk__rvv = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    qea__aput = set()
    gks__jmt = []
    for gcj__nnzaj in init_nodes:
        if is_assign(gcj__nnzaj) and isinstance(gcj__nnzaj.value, ir.Global
            ) and isinstance(gcj__nnzaj.value.value, pytypes.FunctionType
            ) and gcj__nnzaj.value.value in heglk__rvv:
            qea__aput.add(gcj__nnzaj.target.name)
        elif is_call_assign(gcj__nnzaj
            ) and gcj__nnzaj.value.func.name in qea__aput:
            pass
        else:
            gks__jmt.append(gcj__nnzaj)
    init_nodes = gks__jmt
    jciqg__oprc = types.Tuple(var_types)
    yglkj__deoal = lambda : None
    f_ir = compile_to_numba_ir(yglkj__deoal, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    usef__tbl = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    fqnmi__suw = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc), usef__tbl,
        loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [fqnmi__suw] + block.body
    block.body[-2].value.value = usef__tbl
    gmi__ora = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        jciqg__oprc, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    vqp__gmlh = numba.core.target_extension.dispatcher_registry[cpu_target](
        yglkj__deoal)
    vqp__gmlh.add_overload(gmi__ora)
    return vqp__gmlh


def gen_all_update_func(update_funcs, reduce_var_types, in_col_types,
    redvar_offsets, typingctx, targetctx, pivot_typ, pivot_values, is_crosstab
    ):
    kjp__iyjp = len(update_funcs)
    uido__cezr = len(in_col_types)
    if pivot_values is not None:
        assert uido__cezr == 1
    vafb__cfz = (
        'def update_all_f(redvar_arrs, data_in, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        iwfd__emq = redvar_offsets[uido__cezr]
        vafb__cfz += '  pv = pivot_arr[i]\n'
        for ygvb__iyoz, dlme__avye in enumerate(pivot_values):
            oed__dzf = 'el' if ygvb__iyoz != 0 else ''
            vafb__cfz += "  {}if pv == '{}':\n".format(oed__dzf, dlme__avye)
            eiv__bkfo = iwfd__emq * ygvb__iyoz
            wsw__krq = ', '.join(['redvar_arrs[{}][w_ind]'.format(tps__uei) for
                tps__uei in range(eiv__bkfo + redvar_offsets[0], eiv__bkfo +
                redvar_offsets[1])])
            niim__pgjd = 'data_in[0][i]'
            if is_crosstab:
                niim__pgjd = '0'
            vafb__cfz += '    {} = update_vars_0({}, {})\n'.format(wsw__krq,
                wsw__krq, niim__pgjd)
    else:
        for ygvb__iyoz in range(kjp__iyjp):
            wsw__krq = ', '.join(['redvar_arrs[{}][w_ind]'.format(tps__uei) for
                tps__uei in range(redvar_offsets[ygvb__iyoz],
                redvar_offsets[ygvb__iyoz + 1])])
            if wsw__krq:
                vafb__cfz += ('  {} = update_vars_{}({},  data_in[{}][i])\n'
                    .format(wsw__krq, ygvb__iyoz, wsw__krq, 0 if uido__cezr ==
                    1 else ygvb__iyoz))
    vafb__cfz += '  return\n'
    zhnd__wsfkg = {}
    for tps__uei, xbsj__jcp in enumerate(update_funcs):
        zhnd__wsfkg['update_vars_{}'.format(tps__uei)] = xbsj__jcp
    xqeuk__wkzbc = {}
    exec(vafb__cfz, zhnd__wsfkg, xqeuk__wkzbc)
    loslg__pml = xqeuk__wkzbc['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(loslg__pml)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx, pivot_typ, pivot_values):
    xrkz__glexo = types.Tuple([types.Array(t, 1, 'C') for t in
        reduce_var_types])
    arg_typs = xrkz__glexo, xrkz__glexo, types.intp, types.intp, pivot_typ
    soo__xlom = len(redvar_offsets) - 1
    iwfd__emq = redvar_offsets[soo__xlom]
    vafb__cfz = (
        'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        assert soo__xlom == 1
        for pfdxt__ieyo in range(len(pivot_values)):
            eiv__bkfo = iwfd__emq * pfdxt__ieyo
            wsw__krq = ', '.join(['redvar_arrs[{}][w_ind]'.format(tps__uei) for
                tps__uei in range(eiv__bkfo + redvar_offsets[0], eiv__bkfo +
                redvar_offsets[1])])
            tnxef__mvo = ', '.join(['recv_arrs[{}][i]'.format(tps__uei) for
                tps__uei in range(eiv__bkfo + redvar_offsets[0], eiv__bkfo +
                redvar_offsets[1])])
            vafb__cfz += '  {} = combine_vars_0({}, {})\n'.format(wsw__krq,
                wsw__krq, tnxef__mvo)
    else:
        for ygvb__iyoz in range(soo__xlom):
            wsw__krq = ', '.join(['redvar_arrs[{}][w_ind]'.format(tps__uei) for
                tps__uei in range(redvar_offsets[ygvb__iyoz],
                redvar_offsets[ygvb__iyoz + 1])])
            tnxef__mvo = ', '.join(['recv_arrs[{}][i]'.format(tps__uei) for
                tps__uei in range(redvar_offsets[ygvb__iyoz],
                redvar_offsets[ygvb__iyoz + 1])])
            if tnxef__mvo:
                vafb__cfz += '  {} = combine_vars_{}({}, {})\n'.format(wsw__krq
                    , ygvb__iyoz, wsw__krq, tnxef__mvo)
    vafb__cfz += '  return\n'
    zhnd__wsfkg = {}
    for tps__uei, xbsj__jcp in enumerate(combine_funcs):
        zhnd__wsfkg['combine_vars_{}'.format(tps__uei)] = xbsj__jcp
    xqeuk__wkzbc = {}
    exec(vafb__cfz, zhnd__wsfkg, xqeuk__wkzbc)
    cik__hckah = xqeuk__wkzbc['combine_all_f']
    f_ir = compile_to_numba_ir(cik__hckah, zhnd__wsfkg)
    wxw__utm = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    vqp__gmlh = numba.core.target_extension.dispatcher_registry[cpu_target](
        cik__hckah)
    vqp__gmlh.add_overload(wxw__utm)
    return vqp__gmlh


def gen_all_eval_func(eval_funcs, reduce_var_types, redvar_offsets,
    out_col_typs, typingctx, targetctx, pivot_values):
    xrkz__glexo = types.Tuple([types.Array(t, 1, 'C') for t in
        reduce_var_types])
    out_col_typs = types.Tuple(out_col_typs)
    soo__xlom = len(redvar_offsets) - 1
    iwfd__emq = redvar_offsets[soo__xlom]
    vafb__cfz = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    if pivot_values is not None:
        assert soo__xlom == 1
        for ygvb__iyoz in range(len(pivot_values)):
            eiv__bkfo = iwfd__emq * ygvb__iyoz
            wsw__krq = ', '.join(['redvar_arrs[{}][j]'.format(tps__uei) for
                tps__uei in range(eiv__bkfo + redvar_offsets[0], eiv__bkfo +
                redvar_offsets[1])])
            vafb__cfz += '  out_arrs[{}][j] = eval_vars_0({})\n'.format(
                ygvb__iyoz, wsw__krq)
    else:
        for ygvb__iyoz in range(soo__xlom):
            wsw__krq = ', '.join(['redvar_arrs[{}][j]'.format(tps__uei) for
                tps__uei in range(redvar_offsets[ygvb__iyoz],
                redvar_offsets[ygvb__iyoz + 1])])
            vafb__cfz += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
                ygvb__iyoz, ygvb__iyoz, wsw__krq)
    vafb__cfz += '  return\n'
    zhnd__wsfkg = {}
    for tps__uei, xbsj__jcp in enumerate(eval_funcs):
        zhnd__wsfkg['eval_vars_{}'.format(tps__uei)] = xbsj__jcp
    xqeuk__wkzbc = {}
    exec(vafb__cfz, zhnd__wsfkg, xqeuk__wkzbc)
    jbz__aqiin = xqeuk__wkzbc['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(jbz__aqiin)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    wwt__yuynt = len(var_types)
    ncov__jrlj = [f'in{tps__uei}' for tps__uei in range(wwt__yuynt)]
    jciqg__oprc = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    rlc__evpp = jciqg__oprc(0)
    vafb__cfz = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        ncov__jrlj))
    xqeuk__wkzbc = {}
    exec(vafb__cfz, {'_zero': rlc__evpp}, xqeuk__wkzbc)
    ztul__pdkc = xqeuk__wkzbc['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(ztul__pdkc, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': rlc__evpp}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    jdyij__dzi = []
    for tps__uei, jayzt__jvuq in enumerate(reduce_vars):
        jdyij__dzi.append(ir.Assign(block.body[tps__uei].target,
            jayzt__jvuq, jayzt__jvuq.loc))
        for llihh__zfmg in jayzt__jvuq.versioned_names:
            jdyij__dzi.append(ir.Assign(jayzt__jvuq, ir.Var(jayzt__jvuq.
                scope, llihh__zfmg, jayzt__jvuq.loc), jayzt__jvuq.loc))
    block.body = block.body[:wwt__yuynt] + jdyij__dzi + eval_nodes
    shvsb__ipoyp = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        jciqg__oprc, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    vqp__gmlh = numba.core.target_extension.dispatcher_registry[cpu_target](
        ztul__pdkc)
    vqp__gmlh.add_overload(shvsb__ipoyp)
    return vqp__gmlh


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    wwt__yuynt = len(redvars)
    xdsfg__unu = [f'v{tps__uei}' for tps__uei in range(wwt__yuynt)]
    ncov__jrlj = [f'in{tps__uei}' for tps__uei in range(wwt__yuynt)]
    vafb__cfz = 'def agg_combine({}):\n'.format(', '.join(xdsfg__unu +
        ncov__jrlj))
    ublf__rym = wrap_parfor_blocks(parfor)
    ehsje__hww = find_topo_order(ublf__rym)
    ehsje__hww = ehsje__hww[1:]
    unwrap_parfor_blocks(parfor)
    tkj__qdor = {}
    aovcu__rawuh = []
    for rysk__fdxds in ehsje__hww:
        zywzf__omer = parfor.loop_body[rysk__fdxds]
        for gcj__nnzaj in zywzf__omer.body:
            if is_call_assign(gcj__nnzaj) and guard(find_callname, f_ir,
                gcj__nnzaj.value) == ('__special_combine', 'bodo.ir.aggregate'
                ):
                args = gcj__nnzaj.value.args
                fut__cpdq = []
                ovs__eqh = []
                for jayzt__jvuq in args[:-1]:
                    ind = redvars.index(jayzt__jvuq.name)
                    aovcu__rawuh.append(ind)
                    fut__cpdq.append('v{}'.format(ind))
                    ovs__eqh.append('in{}'.format(ind))
                pehw__hxli = '__special_combine__{}'.format(len(tkj__qdor))
                vafb__cfz += '    ({},) = {}({})\n'.format(', '.join(
                    fut__cpdq), pehw__hxli, ', '.join(fut__cpdq + ovs__eqh))
                kbdei__pbhkv = ir.Expr.call(args[-1], [], (), zywzf__omer.loc)
                heor__xnkg = guard(find_callname, f_ir, kbdei__pbhkv)
                assert heor__xnkg == ('_var_combine', 'bodo.ir.aggregate')
                heor__xnkg = bodo.ir.aggregate._var_combine
                tkj__qdor[pehw__hxli] = heor__xnkg
            if is_assign(gcj__nnzaj) and gcj__nnzaj.target.name in redvars:
                nofe__iuz = gcj__nnzaj.target.name
                ind = redvars.index(nofe__iuz)
                if ind in aovcu__rawuh:
                    continue
                if len(f_ir._definitions[nofe__iuz]) == 2:
                    var_def = f_ir._definitions[nofe__iuz][0]
                    vafb__cfz += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[nofe__iuz][1]
                    vafb__cfz += _match_reduce_def(var_def, f_ir, ind)
    vafb__cfz += '    return {}'.format(', '.join(['v{}'.format(tps__uei) for
        tps__uei in range(wwt__yuynt)]))
    xqeuk__wkzbc = {}
    exec(vafb__cfz, {}, xqeuk__wkzbc)
    lidd__nnndx = xqeuk__wkzbc['agg_combine']
    arg_typs = tuple(2 * var_types)
    zhnd__wsfkg = {'numba': numba, 'bodo': bodo, 'np': np}
    zhnd__wsfkg.update(tkj__qdor)
    f_ir = compile_to_numba_ir(lidd__nnndx, zhnd__wsfkg, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=pm.
        typemap, calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    jciqg__oprc = pm.typemap[block.body[-1].value.name]
    lxyw__yytlg = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        jciqg__oprc, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    vqp__gmlh = numba.core.target_extension.dispatcher_registry[cpu_target](
        lidd__nnndx)
    vqp__gmlh.add_overload(lxyw__yytlg)
    return vqp__gmlh


def _match_reduce_def(var_def, f_ir, ind):
    vafb__cfz = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        vafb__cfz = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        xkxa__ixqye = guard(find_callname, f_ir, var_def)
        if xkxa__ixqye == ('min', 'builtins'):
            vafb__cfz = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if xkxa__ixqye == ('max', 'builtins'):
            vafb__cfz = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return vafb__cfz


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    wwt__yuynt = len(redvars)
    duj__wpld = 1
    ofa__kzap = []
    for tps__uei in range(duj__wpld):
        vpbp__wdwdu = ir.Var(arr_var.scope, f'$input{tps__uei}', arr_var.loc)
        ofa__kzap.append(vpbp__wdwdu)
    aqnrm__hqm = parfor.loop_nests[0].index_variable
    lokk__xwuz = [0] * wwt__yuynt
    for zywzf__omer in parfor.loop_body.values():
        naf__gkx = []
        for gcj__nnzaj in zywzf__omer.body:
            if is_var_assign(gcj__nnzaj
                ) and gcj__nnzaj.value.name == aqnrm__hqm.name:
                continue
            if is_getitem(gcj__nnzaj
                ) and gcj__nnzaj.value.value.name == arr_var.name:
                gcj__nnzaj.value = ofa__kzap[0]
            if is_call_assign(gcj__nnzaj) and guard(find_callname, pm.
                func_ir, gcj__nnzaj.value) == ('isna',
                'bodo.libs.array_kernels') and gcj__nnzaj.value.args[0
                ].name == arr_var.name:
                gcj__nnzaj.value = ir.Const(False, gcj__nnzaj.target.loc)
            if is_assign(gcj__nnzaj) and gcj__nnzaj.target.name in redvars:
                ind = redvars.index(gcj__nnzaj.target.name)
                lokk__xwuz[ind] = gcj__nnzaj.target
            naf__gkx.append(gcj__nnzaj)
        zywzf__omer.body = naf__gkx
    xdsfg__unu = ['v{}'.format(tps__uei) for tps__uei in range(wwt__yuynt)]
    ncov__jrlj = ['in{}'.format(tps__uei) for tps__uei in range(duj__wpld)]
    vafb__cfz = 'def agg_update({}):\n'.format(', '.join(xdsfg__unu +
        ncov__jrlj))
    vafb__cfz += '    __update_redvars()\n'
    vafb__cfz += '    return {}'.format(', '.join(['v{}'.format(tps__uei) for
        tps__uei in range(wwt__yuynt)]))
    xqeuk__wkzbc = {}
    exec(vafb__cfz, {}, xqeuk__wkzbc)
    vqkbo__qsbjr = xqeuk__wkzbc['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * duj__wpld)
    f_ir = compile_to_numba_ir(vqkbo__qsbjr, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    mcuip__cxwho = f_ir.blocks.popitem()[1].body
    jciqg__oprc = pm.typemap[mcuip__cxwho[-1].value.name]
    ublf__rym = wrap_parfor_blocks(parfor)
    ehsje__hww = find_topo_order(ublf__rym)
    ehsje__hww = ehsje__hww[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    cwsjk__uules = f_ir.blocks[ehsje__hww[0]]
    uay__krnt = f_ir.blocks[ehsje__hww[-1]]
    hlemo__dpmqw = mcuip__cxwho[:wwt__yuynt + duj__wpld]
    if wwt__yuynt > 1:
        ews__ekqck = mcuip__cxwho[-3:]
        assert is_assign(ews__ekqck[0]) and isinstance(ews__ekqck[0].value,
            ir.Expr) and ews__ekqck[0].value.op == 'build_tuple'
    else:
        ews__ekqck = mcuip__cxwho[-2:]
    for tps__uei in range(wwt__yuynt):
        nxi__zitpw = mcuip__cxwho[tps__uei].target
        wbpey__mkwy = ir.Assign(nxi__zitpw, lokk__xwuz[tps__uei],
            nxi__zitpw.loc)
        hlemo__dpmqw.append(wbpey__mkwy)
    for tps__uei in range(wwt__yuynt, wwt__yuynt + duj__wpld):
        nxi__zitpw = mcuip__cxwho[tps__uei].target
        wbpey__mkwy = ir.Assign(nxi__zitpw, ofa__kzap[tps__uei - wwt__yuynt
            ], nxi__zitpw.loc)
        hlemo__dpmqw.append(wbpey__mkwy)
    cwsjk__uules.body = hlemo__dpmqw + cwsjk__uules.body
    opjyi__ellx = []
    for tps__uei in range(wwt__yuynt):
        nxi__zitpw = mcuip__cxwho[tps__uei].target
        wbpey__mkwy = ir.Assign(lokk__xwuz[tps__uei], nxi__zitpw,
            nxi__zitpw.loc)
        opjyi__ellx.append(wbpey__mkwy)
    uay__krnt.body += opjyi__ellx + ews__ekqck
    ovzso__aoilh = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        jciqg__oprc, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    vqp__gmlh = numba.core.target_extension.dispatcher_registry[cpu_target](
        vqkbo__qsbjr)
    vqp__gmlh.add_overload(ovzso__aoilh)
    return vqp__gmlh


def _rm_arg_agg_block(block, typemap):
    gntk__plo = []
    arr_var = None
    for tps__uei, gcj__nnzaj in enumerate(block.body):
        if is_assign(gcj__nnzaj) and isinstance(gcj__nnzaj.value, ir.Arg):
            arr_var = gcj__nnzaj.target
            ktiqc__aews = typemap[arr_var.name]
            if not isinstance(ktiqc__aews, types.ArrayCompatible):
                gntk__plo += block.body[tps__uei + 1:]
                break
            kead__ewgti = block.body[tps__uei + 1]
            assert is_assign(kead__ewgti) and isinstance(kead__ewgti.value,
                ir.Expr
                ) and kead__ewgti.value.op == 'getattr' and kead__ewgti.value.attr == 'shape' and kead__ewgti.value.value.name == arr_var.name
            yspy__vkjmr = kead__ewgti.target
            syi__awzwb = block.body[tps__uei + 2]
            assert is_assign(syi__awzwb) and isinstance(syi__awzwb.value,
                ir.Expr
                ) and syi__awzwb.value.op == 'static_getitem' and syi__awzwb.value.value.name == yspy__vkjmr.name
            gntk__plo += block.body[tps__uei + 3:]
            break
        gntk__plo.append(gcj__nnzaj)
    return gntk__plo, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    ublf__rym = wrap_parfor_blocks(parfor)
    ehsje__hww = find_topo_order(ublf__rym)
    ehsje__hww = ehsje__hww[1:]
    unwrap_parfor_blocks(parfor)
    for rysk__fdxds in reversed(ehsje__hww):
        for gcj__nnzaj in reversed(parfor.loop_body[rysk__fdxds].body):
            if isinstance(gcj__nnzaj, ir.Assign) and (gcj__nnzaj.target.
                name in parfor_params or gcj__nnzaj.target.name in var_to_param
                ):
                ycirh__wyi = gcj__nnzaj.target.name
                rhs = gcj__nnzaj.value
                evw__vveko = (ycirh__wyi if ycirh__wyi in parfor_params else
                    var_to_param[ycirh__wyi])
                ypmf__kozl = []
                if isinstance(rhs, ir.Var):
                    ypmf__kozl = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    ypmf__kozl = [jayzt__jvuq.name for jayzt__jvuq in
                        gcj__nnzaj.value.list_vars()]
                param_uses[evw__vveko].extend(ypmf__kozl)
                for jayzt__jvuq in ypmf__kozl:
                    var_to_param[jayzt__jvuq] = evw__vveko
            if isinstance(gcj__nnzaj, Parfor):
                get_parfor_reductions(gcj__nnzaj, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for ebz__hpz, ypmf__kozl in param_uses.items():
        if ebz__hpz in ypmf__kozl and ebz__hpz not in reduce_varnames:
            reduce_varnames.append(ebz__hpz)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
