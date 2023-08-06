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
            jnpie__sbaq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            omhxe__erg = cgutils.get_or_insert_function(builder.module,
                jnpie__sbaq, sym._literal_value)
            builder.call(omhxe__erg, [context.get_constant_null(sig.args[0])])
        elif sig == types.none(types.int64, types.voidptr, types.voidptr):
            jnpie__sbaq = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            omhxe__erg = cgutils.get_or_insert_function(builder.module,
                jnpie__sbaq, sym._literal_value)
            builder.call(omhxe__erg, [context.get_constant(types.int64, 0),
                context.get_constant_null(sig.args[1]), context.
                get_constant_null(sig.args[2])])
        else:
            jnpie__sbaq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            omhxe__erg = cgutils.get_or_insert_function(builder.module,
                jnpie__sbaq, sym._literal_value)
            builder.call(omhxe__erg, [context.get_constant_null(sig.args[0]
                ), context.get_constant_null(sig.args[1]), context.
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
        tjs__koch = True
        zzh__bmyh = 1
        ezmdw__gnnvv = -1
        if isinstance(rhs, ir.Expr):
            for hcelu__ejx in rhs.kws:
                if func_name in list_cumulative:
                    if hcelu__ejx[0] == 'skipna':
                        tjs__koch = guard(find_const, func_ir, hcelu__ejx[1])
                        if not isinstance(tjs__koch, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if hcelu__ejx[0] == 'dropna':
                        tjs__koch = guard(find_const, func_ir, hcelu__ejx[1])
                        if not isinstance(tjs__koch, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            zzh__bmyh = get_call_expr_arg('shift', rhs.args, dict(rhs.kws),
                0, 'periods', zzh__bmyh)
            zzh__bmyh = guard(find_const, func_ir, zzh__bmyh)
        if func_name == 'head':
            ezmdw__gnnvv = get_call_expr_arg('head', rhs.args, dict(rhs.kws
                ), 0, 'n', 5)
            if not isinstance(ezmdw__gnnvv, int):
                ezmdw__gnnvv = guard(find_const, func_ir, ezmdw__gnnvv)
            if ezmdw__gnnvv < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = tjs__koch
        func.periods = zzh__bmyh
        func.head_n = ezmdw__gnnvv
        if func_name == 'transform':
            kws = dict(rhs.kws)
            xhpqw__vjmbw = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            upsst__nzvvi = typemap[xhpqw__vjmbw.name]
            rwxx__cpcmc = None
            if isinstance(upsst__nzvvi, str):
                rwxx__cpcmc = upsst__nzvvi
            elif is_overload_constant_str(upsst__nzvvi):
                rwxx__cpcmc = get_overload_const_str(upsst__nzvvi)
            elif bodo.utils.typing.is_builtin_function(upsst__nzvvi):
                rwxx__cpcmc = bodo.utils.typing.get_builtin_function_name(
                    upsst__nzvvi)
            if rwxx__cpcmc not in bodo.ir.aggregate.supported_transform_funcs[:
                ]:
                raise BodoError(f'unsupported transform function {rwxx__cpcmc}'
                    )
            func.transform_func = supported_agg_funcs.index(rwxx__cpcmc)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    xhpqw__vjmbw = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if xhpqw__vjmbw == '':
        upsst__nzvvi = types.none
    else:
        upsst__nzvvi = typemap[xhpqw__vjmbw.name]
    if is_overload_constant_dict(upsst__nzvvi):
        aqc__qezio = get_overload_constant_dict(upsst__nzvvi)
        uerb__jdt = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in aqc__qezio.values()]
        return uerb__jdt
    if upsst__nzvvi == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(upsst__nzvvi, types.BaseTuple) or is_overload_constant_list(
        upsst__nzvvi):
        uerb__jdt = []
        ofoh__jcw = 0
        if is_overload_constant_list(upsst__nzvvi):
            wud__obx = get_overload_const_list(upsst__nzvvi)
        else:
            wud__obx = upsst__nzvvi.types
        for t in wud__obx:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                uerb__jdt.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(wud__obx) > 1:
                    func.fname = '<lambda_' + str(ofoh__jcw) + '>'
                    ofoh__jcw += 1
                uerb__jdt.append(func)
        return [uerb__jdt]
    if is_overload_constant_str(upsst__nzvvi):
        func_name = get_overload_const_str(upsst__nzvvi)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(upsst__nzvvi):
        func_name = bodo.utils.typing.get_builtin_function_name(upsst__nzvvi)
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
        ofoh__jcw = 0
        olcef__pizh = []
        for pvrqm__mry in f_val:
            func = get_agg_func_udf(func_ir, pvrqm__mry, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{ofoh__jcw}>'
                ofoh__jcw += 1
            olcef__pizh.append(func)
        return olcef__pizh
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
    rwxx__cpcmc = code.co_name
    return rwxx__cpcmc


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
            cns__kok = types.DType(args[0])
            return signature(cns__kok, *args)


@numba.njit(no_cpython_wrapper=True)
def _var_combine(ssqdm_a, mean_a, nobs_a, ssqdm_b, mean_b, nobs_b):
    rnttx__dhtup = nobs_a + nobs_b
    ulpb__fqcyi = (nobs_a * mean_a + nobs_b * mean_b) / rnttx__dhtup
    ody__mrae = mean_b - mean_a
    pnxw__bucrh = (ssqdm_a + ssqdm_b + ody__mrae * ody__mrae * nobs_a *
        nobs_b / rnttx__dhtup)
    return pnxw__bucrh, ulpb__fqcyi, rnttx__dhtup


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
        fvwhu__cwjjk = ''
        for hvfs__jwcs, iajhg__cjy in self.df_out_vars.items():
            fvwhu__cwjjk += "'{}':{}, ".format(hvfs__jwcs, iajhg__cjy.name)
        hef__xex = '{}{{{}}}'.format(self.df_out, fvwhu__cwjjk)
        chd__tuu = ''
        for hvfs__jwcs, iajhg__cjy in self.df_in_vars.items():
            chd__tuu += "'{}':{}, ".format(hvfs__jwcs, iajhg__cjy.name)
        wzobn__pqen = '{}{{{}}}'.format(self.df_in, chd__tuu)
        ygq__vogab = 'pivot {}:{}'.format(self.pivot_arr.name, self.
            pivot_values) if self.pivot_arr is not None else ''
        key_names = ','.join([str(tqh__hywcf) for tqh__hywcf in self.key_names]
            )
        enqg__uqs = ','.join([iajhg__cjy.name for iajhg__cjy in self.key_arrs])
        return 'aggregate: {} = {} [key: {}:{}] {}'.format(hef__xex,
            wzobn__pqen, key_names, enqg__uqs, ygq__vogab)

    def remove_out_col(self, out_col_name):
        self.df_out_vars.pop(out_col_name)
        sngav__bxbe, uxu__senz = self.gb_info_out.pop(out_col_name)
        if sngav__bxbe is None and not self.is_crosstab:
            return
        giyxs__vxcv = self.gb_info_in[sngav__bxbe]
        if self.pivot_arr is not None:
            self.pivot_values.remove(out_col_name)
            for sai__lccl, (func, fvwhu__cwjjk) in enumerate(giyxs__vxcv):
                try:
                    fvwhu__cwjjk.remove(out_col_name)
                    if len(fvwhu__cwjjk) == 0:
                        giyxs__vxcv.pop(sai__lccl)
                        break
                except ValueError as mco__zhla:
                    continue
        else:
            for sai__lccl, (func, aus__kyro) in enumerate(giyxs__vxcv):
                if aus__kyro == out_col_name:
                    giyxs__vxcv.pop(sai__lccl)
                    break
        if len(giyxs__vxcv) == 0:
            self.gb_info_in.pop(sngav__bxbe)
            self.df_in_vars.pop(sngav__bxbe)


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({iajhg__cjy.name for iajhg__cjy in aggregate_node.key_arrs})
    use_set.update({iajhg__cjy.name for iajhg__cjy in aggregate_node.
        df_in_vars.values()})
    if aggregate_node.pivot_arr is not None:
        use_set.add(aggregate_node.pivot_arr.name)
    def_set.update({iajhg__cjy.name for iajhg__cjy in aggregate_node.
        df_out_vars.values()})
    if aggregate_node.out_key_vars is not None:
        def_set.update({iajhg__cjy.name for iajhg__cjy in aggregate_node.
            out_key_vars})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(aggregate_node, lives_no_aliases, lives,
    arg_aliases, alias_map, func_ir, typemap):
    poyq__qaz = [jyo__oyc for jyo__oyc, mvdaf__enmr in aggregate_node.
        df_out_vars.items() if mvdaf__enmr.name not in lives]
    for plm__wptch in poyq__qaz:
        aggregate_node.remove_out_col(plm__wptch)
    out_key_vars = aggregate_node.out_key_vars
    if out_key_vars is not None and all(iajhg__cjy.name not in lives for
        iajhg__cjy in out_key_vars):
        aggregate_node.out_key_vars = None
    if len(aggregate_node.df_out_vars
        ) == 0 and aggregate_node.out_key_vars is None:
        return None
    return aggregate_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    xgiz__aqo = set(iajhg__cjy.name for iajhg__cjy in aggregate_node.
        df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        xgiz__aqo.update({iajhg__cjy.name for iajhg__cjy in aggregate_node.
            out_key_vars})
    return set(), xgiz__aqo


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for sai__lccl in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[sai__lccl] = replace_vars_inner(aggregate_node
            .key_arrs[sai__lccl], var_dict)
    for jyo__oyc in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[jyo__oyc] = replace_vars_inner(aggregate_node
            .df_in_vars[jyo__oyc], var_dict)
    for jyo__oyc in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[jyo__oyc] = replace_vars_inner(
            aggregate_node.df_out_vars[jyo__oyc], var_dict)
    if aggregate_node.out_key_vars is not None:
        for sai__lccl in range(len(aggregate_node.out_key_vars)):
            aggregate_node.out_key_vars[sai__lccl] = replace_vars_inner(
                aggregate_node.out_key_vars[sai__lccl], var_dict)
    if aggregate_node.pivot_arr is not None:
        aggregate_node.pivot_arr = replace_vars_inner(aggregate_node.
            pivot_arr, var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    if debug_prints():
        print('visiting aggregate vars for:', aggregate_node)
        print('cbdata: ', sorted(cbdata.items()))
    for sai__lccl in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[sai__lccl] = visit_vars_inner(aggregate_node
            .key_arrs[sai__lccl], callback, cbdata)
    for jyo__oyc in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[jyo__oyc] = visit_vars_inner(aggregate_node
            .df_in_vars[jyo__oyc], callback, cbdata)
    for jyo__oyc in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[jyo__oyc] = visit_vars_inner(aggregate_node
            .df_out_vars[jyo__oyc], callback, cbdata)
    if aggregate_node.out_key_vars is not None:
        for sai__lccl in range(len(aggregate_node.out_key_vars)):
            aggregate_node.out_key_vars[sai__lccl] = visit_vars_inner(
                aggregate_node.out_key_vars[sai__lccl], callback, cbdata)
    if aggregate_node.pivot_arr is not None:
        aggregate_node.pivot_arr = visit_vars_inner(aggregate_node.
            pivot_arr, callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    assert len(aggregate_node.df_out_vars
        ) > 0 or aggregate_node.out_key_vars is not None or aggregate_node.is_crosstab, 'empty aggregate in array analysis'
    blmdo__ldgz = []
    for wvo__zac in aggregate_node.key_arrs:
        lfmi__hdbyl = equiv_set.get_shape(wvo__zac)
        if lfmi__hdbyl:
            blmdo__ldgz.append(lfmi__hdbyl[0])
    if aggregate_node.pivot_arr is not None:
        lfmi__hdbyl = equiv_set.get_shape(aggregate_node.pivot_arr)
        if lfmi__hdbyl:
            blmdo__ldgz.append(lfmi__hdbyl[0])
    for mvdaf__enmr in aggregate_node.df_in_vars.values():
        lfmi__hdbyl = equiv_set.get_shape(mvdaf__enmr)
        if lfmi__hdbyl:
            blmdo__ldgz.append(lfmi__hdbyl[0])
    if len(blmdo__ldgz) > 1:
        equiv_set.insert_equiv(*blmdo__ldgz)
    wvkpv__boqq = []
    blmdo__ldgz = []
    tzxbj__tpquu = list(aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        tzxbj__tpquu.extend(aggregate_node.out_key_vars)
    for mvdaf__enmr in tzxbj__tpquu:
        thtfo__pans = typemap[mvdaf__enmr.name]
        pzzh__tgfp = array_analysis._gen_shape_call(equiv_set, mvdaf__enmr,
            thtfo__pans.ndim, None, wvkpv__boqq)
        equiv_set.insert_equiv(mvdaf__enmr, pzzh__tgfp)
        blmdo__ldgz.append(pzzh__tgfp[0])
        equiv_set.define(mvdaf__enmr, set())
    if len(blmdo__ldgz) > 1:
        equiv_set.insert_equiv(*blmdo__ldgz)
    return [], wvkpv__boqq


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    moegy__ilsof = Distribution.OneD
    for mvdaf__enmr in aggregate_node.df_in_vars.values():
        moegy__ilsof = Distribution(min(moegy__ilsof.value, array_dists[
            mvdaf__enmr.name].value))
    for wvo__zac in aggregate_node.key_arrs:
        moegy__ilsof = Distribution(min(moegy__ilsof.value, array_dists[
            wvo__zac.name].value))
    if aggregate_node.pivot_arr is not None:
        moegy__ilsof = Distribution(min(moegy__ilsof.value, array_dists[
            aggregate_node.pivot_arr.name].value))
        array_dists[aggregate_node.pivot_arr.name] = moegy__ilsof
    for mvdaf__enmr in aggregate_node.df_in_vars.values():
        array_dists[mvdaf__enmr.name] = moegy__ilsof
    for wvo__zac in aggregate_node.key_arrs:
        array_dists[wvo__zac.name] = moegy__ilsof
    olcas__gcdiz = Distribution.OneD_Var
    for mvdaf__enmr in aggregate_node.df_out_vars.values():
        if mvdaf__enmr.name in array_dists:
            olcas__gcdiz = Distribution(min(olcas__gcdiz.value, array_dists
                [mvdaf__enmr.name].value))
    if aggregate_node.out_key_vars is not None:
        for mvdaf__enmr in aggregate_node.out_key_vars:
            if mvdaf__enmr.name in array_dists:
                olcas__gcdiz = Distribution(min(olcas__gcdiz.value,
                    array_dists[mvdaf__enmr.name].value))
    olcas__gcdiz = Distribution(min(olcas__gcdiz.value, moegy__ilsof.value))
    for mvdaf__enmr in aggregate_node.df_out_vars.values():
        array_dists[mvdaf__enmr.name] = olcas__gcdiz
    if aggregate_node.out_key_vars is not None:
        for mtxyv__edpq in aggregate_node.out_key_vars:
            array_dists[mtxyv__edpq.name] = olcas__gcdiz
    if olcas__gcdiz != Distribution.OneD_Var:
        for wvo__zac in aggregate_node.key_arrs:
            array_dists[wvo__zac.name] = olcas__gcdiz
        if aggregate_node.pivot_arr is not None:
            array_dists[aggregate_node.pivot_arr.name] = olcas__gcdiz
        for mvdaf__enmr in aggregate_node.df_in_vars.values():
            array_dists[mvdaf__enmr.name] = olcas__gcdiz


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for mvdaf__enmr in agg_node.df_out_vars.values():
        definitions[mvdaf__enmr.name].append(agg_node)
    if agg_node.out_key_vars is not None:
        for mtxyv__edpq in agg_node.out_key_vars:
            definitions[mtxyv__edpq.name].append(agg_node)
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
        for iajhg__cjy in (list(agg_node.df_in_vars.values()) + list(
            agg_node.df_out_vars.values()) + agg_node.key_arrs):
            if array_dists[iajhg__cjy.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                iajhg__cjy.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    dqo__cjx = tuple(typemap[iajhg__cjy.name] for iajhg__cjy in agg_node.
        key_arrs)
    bll__hglw = [iajhg__cjy for yvx__qzkn, iajhg__cjy in agg_node.
        df_in_vars.items()]
    blfy__ennlg = [iajhg__cjy for yvx__qzkn, iajhg__cjy in agg_node.
        df_out_vars.items()]
    in_col_typs = []
    uerb__jdt = []
    if agg_node.pivot_arr is not None:
        for sngav__bxbe, giyxs__vxcv in agg_node.gb_info_in.items():
            for func, uxu__senz in giyxs__vxcv:
                if sngav__bxbe is not None:
                    in_col_typs.append(typemap[agg_node.df_in_vars[
                        sngav__bxbe].name])
                uerb__jdt.append(func)
    else:
        for sngav__bxbe, func in agg_node.gb_info_out.values():
            if sngav__bxbe is not None:
                in_col_typs.append(typemap[agg_node.df_in_vars[sngav__bxbe]
                    .name])
            uerb__jdt.append(func)
    out_col_typs = tuple(typemap[iajhg__cjy.name] for iajhg__cjy in blfy__ennlg
        )
    pivot_typ = types.none if agg_node.pivot_arr is None else typemap[agg_node
        .pivot_arr.name]
    arg_typs = tuple(dqo__cjx + tuple(typemap[iajhg__cjy.name] for
        iajhg__cjy in bll__hglw) + (pivot_typ,))
    in_col_typs = [to_str_arr_if_dict_array(t) for t in in_col_typs]
    rnn__dbdo = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for sai__lccl, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            rnn__dbdo.update({f'in_cat_dtype_{sai__lccl}': in_col_typ})
    for sai__lccl, ixu__ckwu in enumerate(out_col_typs):
        if isinstance(ixu__ckwu, bodo.CategoricalArrayType):
            rnn__dbdo.update({f'out_cat_dtype_{sai__lccl}': ixu__ckwu})
    udf_func_struct = get_udf_func_struct(uerb__jdt, agg_node.
        input_has_index, in_col_typs, out_col_typs, typingctx, targetctx,
        pivot_typ, agg_node.pivot_values, agg_node.is_crosstab)
    qur__let = gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
        parallel, udf_func_struct)
    rnn__dbdo.update({'pd': pd, 'pre_alloc_string_array':
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
            rnn__dbdo.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            rnn__dbdo.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    obfyi__wgyk = compile_to_numba_ir(qur__let, rnn__dbdo, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    bixsq__xkoup = []
    if agg_node.pivot_arr is None:
        vydx__rzuet = agg_node.key_arrs[0].scope
        loc = agg_node.loc
        fadn__ijj = ir.Var(vydx__rzuet, mk_unique_var('dummy_none'), loc)
        typemap[fadn__ijj.name] = types.none
        bixsq__xkoup.append(ir.Assign(ir.Const(None, loc), fadn__ijj, loc))
        bll__hglw.append(fadn__ijj)
    else:
        bll__hglw.append(agg_node.pivot_arr)
    replace_arg_nodes(obfyi__wgyk, agg_node.key_arrs + bll__hglw)
    vrsh__fbic = obfyi__wgyk.body[-3]
    assert is_assign(vrsh__fbic) and isinstance(vrsh__fbic.value, ir.Expr
        ) and vrsh__fbic.value.op == 'build_tuple'
    bixsq__xkoup += obfyi__wgyk.body[:-3]
    tzxbj__tpquu = list(agg_node.df_out_vars.values())
    if agg_node.out_key_vars is not None:
        tzxbj__tpquu += agg_node.out_key_vars
    for sai__lccl, ovh__wtnde in enumerate(tzxbj__tpquu):
        ugk__qfsu = vrsh__fbic.value.items[sai__lccl]
        bixsq__xkoup.append(ir.Assign(ugk__qfsu, ovh__wtnde, ovh__wtnde.loc))
    return bixsq__xkoup


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def get_numba_set(dtype):
    pass


@infer_global(get_numba_set)
class GetNumbaSetTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        yqjzs__gzx = args[0]
        dtype = types.Tuple([t.dtype for t in yqjzs__gzx.types]) if isinstance(
            yqjzs__gzx, types.BaseTuple) else yqjzs__gzx.dtype
        if isinstance(yqjzs__gzx, types.BaseTuple) and len(yqjzs__gzx.types
            ) == 1:
            dtype = yqjzs__gzx.types[0].dtype
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
        wlj__ihun = args[0]
        if wlj__ihun == types.none:
            return signature(types.boolean, *args)


@lower_builtin(bool, types.none)
def lower_column_mean_impl(context, builder, sig, args):
    lsw__rxkm = context.compile_internal(builder, lambda a: False, sig, args)
    return lsw__rxkm


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        fkha__iqgp = IntDtype(t.dtype).name
        assert fkha__iqgp.endswith('Dtype()')
        fkha__iqgp = fkha__iqgp[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{fkha__iqgp}'))"
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
        roioy__ppq = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {roioy__ppq}_cat_dtype_{colnum})')
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
    uuiqi__mekx = udf_func_struct.var_typs
    cuqcm__akfof = len(uuiqi__mekx)
    cews__fsgk = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    cews__fsgk += '    if is_null_pointer(in_table):\n'
    cews__fsgk += '        return\n'
    cews__fsgk += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in uuiqi__mekx]), 
        ',' if len(uuiqi__mekx) == 1 else '')
    iamuq__jicb = n_keys
    rmll__zgyp = []
    redvar_offsets = []
    bzjz__ija = []
    if do_combine:
        for sai__lccl, pvrqm__mry in enumerate(allfuncs):
            if pvrqm__mry.ftype != 'udf':
                iamuq__jicb += pvrqm__mry.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(iamuq__jicb, iamuq__jicb +
                    pvrqm__mry.n_redvars))
                iamuq__jicb += pvrqm__mry.n_redvars
                bzjz__ija.append(data_in_typs_[func_idx_to_in_col[sai__lccl]])
                rmll__zgyp.append(func_idx_to_in_col[sai__lccl] + n_keys)
    else:
        for sai__lccl, pvrqm__mry in enumerate(allfuncs):
            if pvrqm__mry.ftype != 'udf':
                iamuq__jicb += pvrqm__mry.ncols_post_shuffle
            else:
                redvar_offsets += list(range(iamuq__jicb + 1, iamuq__jicb +
                    1 + pvrqm__mry.n_redvars))
                iamuq__jicb += pvrqm__mry.n_redvars + 1
                bzjz__ija.append(data_in_typs_[func_idx_to_in_col[sai__lccl]])
                rmll__zgyp.append(func_idx_to_in_col[sai__lccl] + n_keys)
    assert len(redvar_offsets) == cuqcm__akfof
    cex__jxn = len(bzjz__ija)
    uvdu__lnc = []
    for sai__lccl, t in enumerate(bzjz__ija):
        uvdu__lnc.append(_gen_dummy_alloc(t, sai__lccl, True))
    cews__fsgk += '    data_in_dummy = ({}{})\n'.format(','.join(uvdu__lnc),
        ',' if len(bzjz__ija) == 1 else '')
    cews__fsgk += """
    # initialize redvar cols
"""
    cews__fsgk += '    init_vals = __init_func()\n'
    for sai__lccl in range(cuqcm__akfof):
        cews__fsgk += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(sai__lccl, redvar_offsets[sai__lccl], sai__lccl))
        cews__fsgk += '    incref(redvar_arr_{})\n'.format(sai__lccl)
        cews__fsgk += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            sai__lccl, sai__lccl)
    cews__fsgk += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(sai__lccl) for sai__lccl in range(cuqcm__akfof)]), ',' if 
        cuqcm__akfof == 1 else '')
    cews__fsgk += '\n'
    for sai__lccl in range(cex__jxn):
        cews__fsgk += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(sai__lccl, rmll__zgyp[sai__lccl], sai__lccl))
        cews__fsgk += '    incref(data_in_{})\n'.format(sai__lccl)
    cews__fsgk += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(sai__lccl) for sai__lccl in range(cex__jxn)]), ',' if 
        cex__jxn == 1 else '')
    cews__fsgk += '\n'
    cews__fsgk += '    for i in range(len(data_in_0)):\n'
    cews__fsgk += '        w_ind = row_to_group[i]\n'
    cews__fsgk += '        if w_ind != -1:\n'
    cews__fsgk += (
        '            __update_redvars(redvars, data_in, w_ind, i, pivot_arr=None)\n'
        )
    nwl__leamz = {}
    exec(cews__fsgk, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, nwl__leamz)
    return nwl__leamz['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, out_data_typs,
    label_suffix):
    uuiqi__mekx = udf_func_struct.var_typs
    cuqcm__akfof = len(uuiqi__mekx)
    cews__fsgk = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    cews__fsgk += '    if is_null_pointer(in_table):\n'
    cews__fsgk += '        return\n'
    cews__fsgk += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in uuiqi__mekx]), 
        ',' if len(uuiqi__mekx) == 1 else '')
    ntcs__bisr = n_keys
    rejht__gbec = n_keys
    mqx__eeg = []
    oynu__vbply = []
    for pvrqm__mry in allfuncs:
        if pvrqm__mry.ftype != 'udf':
            ntcs__bisr += pvrqm__mry.ncols_pre_shuffle
            rejht__gbec += pvrqm__mry.ncols_post_shuffle
        else:
            mqx__eeg += list(range(ntcs__bisr, ntcs__bisr + pvrqm__mry.
                n_redvars))
            oynu__vbply += list(range(rejht__gbec + 1, rejht__gbec + 1 +
                pvrqm__mry.n_redvars))
            ntcs__bisr += pvrqm__mry.n_redvars
            rejht__gbec += 1 + pvrqm__mry.n_redvars
    assert len(mqx__eeg) == cuqcm__akfof
    cews__fsgk += """
    # initialize redvar cols
"""
    cews__fsgk += '    init_vals = __init_func()\n'
    for sai__lccl in range(cuqcm__akfof):
        cews__fsgk += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(sai__lccl, oynu__vbply[sai__lccl], sai__lccl))
        cews__fsgk += '    incref(redvar_arr_{})\n'.format(sai__lccl)
        cews__fsgk += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            sai__lccl, sai__lccl)
    cews__fsgk += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(sai__lccl) for sai__lccl in range(cuqcm__akfof)]), ',' if 
        cuqcm__akfof == 1 else '')
    cews__fsgk += '\n'
    for sai__lccl in range(cuqcm__akfof):
        cews__fsgk += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(sai__lccl, mqx__eeg[sai__lccl], sai__lccl))
        cews__fsgk += '    incref(recv_redvar_arr_{})\n'.format(sai__lccl)
    cews__fsgk += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(sai__lccl) for sai__lccl in range(
        cuqcm__akfof)]), ',' if cuqcm__akfof == 1 else '')
    cews__fsgk += '\n'
    if cuqcm__akfof:
        cews__fsgk += '    for i in range(len(recv_redvar_arr_0)):\n'
        cews__fsgk += '        w_ind = row_to_group[i]\n'
        cews__fsgk += """        __combine_redvars(redvars, recv_redvars, w_ind, i, pivot_arr=None)
"""
    nwl__leamz = {}
    exec(cews__fsgk, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, nwl__leamz)
    return nwl__leamz['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    uuiqi__mekx = udf_func_struct.var_typs
    cuqcm__akfof = len(uuiqi__mekx)
    iamuq__jicb = n_keys
    redvar_offsets = []
    cdwp__wmwt = []
    out_data_typs = []
    for sai__lccl, pvrqm__mry in enumerate(allfuncs):
        if pvrqm__mry.ftype != 'udf':
            iamuq__jicb += pvrqm__mry.ncols_post_shuffle
        else:
            cdwp__wmwt.append(iamuq__jicb)
            redvar_offsets += list(range(iamuq__jicb + 1, iamuq__jicb + 1 +
                pvrqm__mry.n_redvars))
            iamuq__jicb += 1 + pvrqm__mry.n_redvars
            out_data_typs.append(out_data_typs_[sai__lccl])
    assert len(redvar_offsets) == cuqcm__akfof
    cex__jxn = len(out_data_typs)
    cews__fsgk = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    cews__fsgk += '    if is_null_pointer(table):\n'
    cews__fsgk += '        return\n'
    cews__fsgk += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in uuiqi__mekx]), 
        ',' if len(uuiqi__mekx) == 1 else '')
    cews__fsgk += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        out_data_typs]), ',' if len(out_data_typs) == 1 else '')
    for sai__lccl in range(cuqcm__akfof):
        cews__fsgk += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(sai__lccl, redvar_offsets[sai__lccl], sai__lccl))
        cews__fsgk += '    incref(redvar_arr_{})\n'.format(sai__lccl)
    cews__fsgk += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(sai__lccl) for sai__lccl in range(cuqcm__akfof)]), ',' if 
        cuqcm__akfof == 1 else '')
    cews__fsgk += '\n'
    for sai__lccl in range(cex__jxn):
        cews__fsgk += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(sai__lccl, cdwp__wmwt[sai__lccl], sai__lccl))
        cews__fsgk += '    incref(data_out_{})\n'.format(sai__lccl)
    cews__fsgk += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(sai__lccl) for sai__lccl in range(cex__jxn)]), ',' if 
        cex__jxn == 1 else '')
    cews__fsgk += '\n'
    cews__fsgk += '    for i in range(len(data_out_0)):\n'
    cews__fsgk += '        __eval_res(redvars, data_out, i)\n'
    nwl__leamz = {}
    exec(cews__fsgk, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, nwl__leamz)
    return nwl__leamz['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    iamuq__jicb = n_keys
    nmf__tcjbg = []
    for sai__lccl, pvrqm__mry in enumerate(allfuncs):
        if pvrqm__mry.ftype == 'gen_udf':
            nmf__tcjbg.append(iamuq__jicb)
            iamuq__jicb += 1
        elif pvrqm__mry.ftype != 'udf':
            iamuq__jicb += pvrqm__mry.ncols_post_shuffle
        else:
            iamuq__jicb += pvrqm__mry.n_redvars + 1
    cews__fsgk = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    cews__fsgk += '    if num_groups == 0:\n'
    cews__fsgk += '        return\n'
    for sai__lccl, func in enumerate(udf_func_struct.general_udf_funcs):
        cews__fsgk += '    # col {}\n'.format(sai__lccl)
        cews__fsgk += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(nmf__tcjbg[sai__lccl], sai__lccl))
        cews__fsgk += '    incref(out_col)\n'
        cews__fsgk += '    for j in range(num_groups):\n'
        cews__fsgk += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(sai__lccl, sai__lccl))
        cews__fsgk += '        incref(in_col)\n'
        cews__fsgk += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(sai__lccl))
    rnn__dbdo = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    soyg__uzs = 0
    for sai__lccl, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[soyg__uzs]
        rnn__dbdo['func_{}'.format(soyg__uzs)] = func
        rnn__dbdo['in_col_{}_typ'.format(soyg__uzs)] = in_col_typs[
            func_idx_to_in_col[sai__lccl]]
        rnn__dbdo['out_col_{}_typ'.format(soyg__uzs)] = out_col_typs[sai__lccl]
        soyg__uzs += 1
    nwl__leamz = {}
    exec(cews__fsgk, rnn__dbdo, nwl__leamz)
    pvrqm__mry = nwl__leamz['bodo_gb_apply_general_udfs{}'.format(label_suffix)
        ]
    pbez__chfee = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(pbez__chfee, nopython=True)(pvrqm__mry)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs, parallel,
    udf_func_struct):
    fnbcs__tkoky = agg_node.pivot_arr is not None
    if agg_node.same_index:
        assert agg_node.input_has_index
    if agg_node.pivot_values is None:
        olie__otgik = 1
    else:
        olie__otgik = len(agg_node.pivot_values)
    ukqp__kcng = tuple('key_' + sanitize_varname(hvfs__jwcs) for hvfs__jwcs in
        agg_node.key_names)
    wdn__xuw = {hvfs__jwcs: 'in_{}'.format(sanitize_varname(hvfs__jwcs)) for
        hvfs__jwcs in agg_node.gb_info_in.keys() if hvfs__jwcs is not None}
    mut__lsend = {hvfs__jwcs: ('out_' + sanitize_varname(hvfs__jwcs)) for
        hvfs__jwcs in agg_node.gb_info_out.keys()}
    n_keys = len(agg_node.key_names)
    itr__oso = ', '.join(ukqp__kcng)
    ugnbu__vfld = ', '.join(wdn__xuw.values())
    if ugnbu__vfld != '':
        ugnbu__vfld = ', ' + ugnbu__vfld
    cews__fsgk = 'def agg_top({}{}{}, pivot_arr):\n'.format(itr__oso,
        ugnbu__vfld, ', index_arg' if agg_node.input_has_index else '')
    for a in tuple(wdn__xuw.values()):
        cews__fsgk += f'    {a} = decode_if_dict_array({a})\n'
    if fnbcs__tkoky:
        cews__fsgk += f'    pivot_arr = decode_if_dict_array(pivot_arr)\n'
        bxua__bnr = []
        for sngav__bxbe, giyxs__vxcv in agg_node.gb_info_in.items():
            if sngav__bxbe is not None:
                for func, uxu__senz in giyxs__vxcv:
                    bxua__bnr.append(wdn__xuw[sngav__bxbe])
    else:
        bxua__bnr = tuple(wdn__xuw[sngav__bxbe] for sngav__bxbe, uxu__senz in
            agg_node.gb_info_out.values() if sngav__bxbe is not None)
    ycer__nxlwj = ukqp__kcng + tuple(bxua__bnr)
    cews__fsgk += '    info_list = [{}{}{}]\n'.format(', '.join(
        'array_to_info({})'.format(a) for a in ycer__nxlwj), 
        ', array_to_info(index_arg)' if agg_node.input_has_index else '', 
        ', array_to_info(pivot_arr)' if agg_node.is_crosstab else '')
    cews__fsgk += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    zdj__ylfrd = []
    func_idx_to_in_col = []
    zil__bkc = []
    tjs__koch = False
    jpbk__ebvk = 1
    ezmdw__gnnvv = -1
    jqa__dhuh = 0
    nnc__vahww = 0
    if not fnbcs__tkoky:
        uerb__jdt = [func for uxu__senz, func in agg_node.gb_info_out.values()]
    else:
        uerb__jdt = [func for func, uxu__senz in giyxs__vxcv for
            giyxs__vxcv in agg_node.gb_info_in.values()]
    for urfej__qnf, func in enumerate(uerb__jdt):
        zdj__ylfrd.append(len(allfuncs))
        if func.ftype in {'median', 'nunique'}:
            do_combine = False
        if func.ftype in list_cumulative:
            jqa__dhuh += 1
        if hasattr(func, 'skipdropna'):
            tjs__koch = func.skipdropna
        if func.ftype == 'shift':
            jpbk__ebvk = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            nnc__vahww = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            ezmdw__gnnvv = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(urfej__qnf)
        if func.ftype == 'udf':
            zil__bkc.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            zil__bkc.append(0)
            do_combine = False
    zdj__ylfrd.append(len(allfuncs))
    if agg_node.is_crosstab:
        assert len(agg_node.gb_info_out
            ) == olie__otgik, 'invalid number of groupby outputs for pivot'
    else:
        assert len(agg_node.gb_info_out) == len(allfuncs
            ) * olie__otgik, 'invalid number of groupby outputs'
    if jqa__dhuh > 0:
        if jqa__dhuh != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    for sai__lccl, hvfs__jwcs in enumerate(agg_node.gb_info_out.keys()):
        ovdxb__ujzaa = mut__lsend[hvfs__jwcs] + '_dummy'
        ixu__ckwu = out_col_typs[sai__lccl]
        sngav__bxbe, func = agg_node.gb_info_out[hvfs__jwcs]
        if isinstance(func, pytypes.SimpleNamespace) and func.fname in ['min',
            'max', 'shift'] and isinstance(ixu__ckwu, bodo.CategoricalArrayType
            ):
            cews__fsgk += '    {} = {}\n'.format(ovdxb__ujzaa, wdn__xuw[
                sngav__bxbe])
        elif udf_func_struct is not None:
            cews__fsgk += '    {} = {}\n'.format(ovdxb__ujzaa,
                _gen_dummy_alloc(ixu__ckwu, sai__lccl, False))
    if udf_func_struct is not None:
        wkgm__wyyug = next_label()
        if udf_func_struct.regular_udfs:
            pbez__chfee = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            wzrm__lfspa = numba.cfunc(pbez__chfee, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs,
                out_col_typs, do_combine, func_idx_to_in_col, wkgm__wyyug))
            tjze__yfpg = numba.cfunc(pbez__chfee, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, out_col_typs, wkgm__wyyug))
            jluu__kwe = numba.cfunc('void(voidptr)', nopython=True)(gen_eval_cb
                (udf_func_struct, allfuncs, n_keys, out_col_typs, wkgm__wyyug))
            udf_func_struct.set_regular_cfuncs(wzrm__lfspa, tjze__yfpg,
                jluu__kwe)
            for kbwb__gsv in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[kbwb__gsv.native_name] = kbwb__gsv
                gb_agg_cfunc_addr[kbwb__gsv.native_name] = kbwb__gsv.address
        if udf_func_struct.general_udfs:
            mxj__ubn = gen_general_udf_cb(udf_func_struct, allfuncs, n_keys,
                in_col_typs, out_col_typs, func_idx_to_in_col, wkgm__wyyug)
            udf_func_struct.set_general_cfunc(mxj__ubn)
        xel__tfy = []
        fvec__fixe = 0
        sai__lccl = 0
        for ovdxb__ujzaa, pvrqm__mry in zip(mut__lsend.values(), allfuncs):
            if pvrqm__mry.ftype in ('udf', 'gen_udf'):
                xel__tfy.append(ovdxb__ujzaa + '_dummy')
                for nwbb__wbz in range(fvec__fixe, fvec__fixe + zil__bkc[
                    sai__lccl]):
                    xel__tfy.append('data_redvar_dummy_' + str(nwbb__wbz))
                fvec__fixe += zil__bkc[sai__lccl]
                sai__lccl += 1
        if udf_func_struct.regular_udfs:
            uuiqi__mekx = udf_func_struct.var_typs
            for sai__lccl, t in enumerate(uuiqi__mekx):
                cews__fsgk += ('    data_redvar_dummy_{} = np.empty(1, {})\n'
                    .format(sai__lccl, _get_np_dtype(t)))
        cews__fsgk += '    out_info_list_dummy = [{}]\n'.format(', '.join(
            'array_to_info({})'.format(a) for a in xel__tfy))
        cews__fsgk += (
            '    udf_table_dummy = arr_info_list_to_table(out_info_list_dummy)\n'
            )
        if udf_func_struct.regular_udfs:
            cews__fsgk += ("    add_agg_cfunc_sym(cpp_cb_update, '{}')\n".
                format(wzrm__lfspa.native_name))
            cews__fsgk += ("    add_agg_cfunc_sym(cpp_cb_combine, '{}')\n".
                format(tjze__yfpg.native_name))
            cews__fsgk += "    add_agg_cfunc_sym(cpp_cb_eval, '{}')\n".format(
                jluu__kwe.native_name)
            cews__fsgk += ("    cpp_cb_update_addr = get_agg_udf_addr('{}')\n"
                .format(wzrm__lfspa.native_name))
            cews__fsgk += ("    cpp_cb_combine_addr = get_agg_udf_addr('{}')\n"
                .format(tjze__yfpg.native_name))
            cews__fsgk += ("    cpp_cb_eval_addr = get_agg_udf_addr('{}')\n"
                .format(jluu__kwe.native_name))
        else:
            cews__fsgk += '    cpp_cb_update_addr = 0\n'
            cews__fsgk += '    cpp_cb_combine_addr = 0\n'
            cews__fsgk += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            kbwb__gsv = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[kbwb__gsv.native_name] = kbwb__gsv
            gb_agg_cfunc_addr[kbwb__gsv.native_name] = kbwb__gsv.address
            cews__fsgk += ("    add_agg_cfunc_sym(cpp_cb_general, '{}')\n".
                format(kbwb__gsv.native_name))
            cews__fsgk += ("    cpp_cb_general_addr = get_agg_udf_addr('{}')\n"
                .format(kbwb__gsv.native_name))
        else:
            cews__fsgk += '    cpp_cb_general_addr = 0\n'
    else:
        cews__fsgk += """    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])
"""
        cews__fsgk += '    cpp_cb_update_addr = 0\n'
        cews__fsgk += '    cpp_cb_combine_addr = 0\n'
        cews__fsgk += '    cpp_cb_eval_addr = 0\n'
        cews__fsgk += '    cpp_cb_general_addr = 0\n'
    cews__fsgk += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(
        ', '.join([str(supported_agg_funcs.index(pvrqm__mry.ftype)) for
        pvrqm__mry in allfuncs] + ['0']))
    cews__fsgk += '    func_offsets = np.array({}, dtype=np.int32)\n'.format(
        str(zdj__ylfrd))
    if len(zil__bkc) > 0:
        cews__fsgk += '    udf_ncols = np.array({}, dtype=np.int32)\n'.format(
            str(zil__bkc))
    else:
        cews__fsgk += '    udf_ncols = np.array([0], np.int32)\n'
    if fnbcs__tkoky:
        cews__fsgk += '    arr_type = coerce_to_array({})\n'.format(agg_node
            .pivot_values)
        cews__fsgk += '    arr_info = array_to_info(arr_type)\n'
        cews__fsgk += (
            '    dispatch_table = arr_info_list_to_table([arr_info])\n')
        cews__fsgk += '    pivot_info = array_to_info(pivot_arr)\n'
        cews__fsgk += (
            '    dispatch_info = arr_info_list_to_table([pivot_info])\n')
        cews__fsgk += (
            """    out_table = pivot_groupby_and_aggregate(table, {}, dispatch_table, dispatch_info, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, agg_node.
            is_crosstab, tjs__koch, agg_node.return_key, agg_node.same_index))
        cews__fsgk += '    delete_info_decref_array(pivot_info)\n'
        cews__fsgk += '    delete_info_decref_array(arr_info)\n'
    else:
        cews__fsgk += (
            """    out_table = groupby_and_aggregate(table, {}, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, tjs__koch,
            jpbk__ebvk, nnc__vahww, ezmdw__gnnvv, agg_node.return_key,
            agg_node.same_index, agg_node.dropna))
    hwzpi__lyedb = 0
    if agg_node.return_key:
        for sai__lccl, mjyri__whh in enumerate(ukqp__kcng):
            cews__fsgk += (
                '    {} = info_to_array(info_from_table(out_table, {}), {})\n'
                .format(mjyri__whh, hwzpi__lyedb, mjyri__whh))
            hwzpi__lyedb += 1
    for sai__lccl, ovdxb__ujzaa in enumerate(mut__lsend.values()):
        if isinstance(func, pytypes.SimpleNamespace) and func.fname in ['min',
            'max', 'shift'] and isinstance(ixu__ckwu, bodo.CategoricalArrayType
            ):
            cews__fsgk += f"""    {ovdxb__ujzaa} = info_to_array(info_from_table(out_table, {hwzpi__lyedb}), {ovdxb__ujzaa + '_dummy'})
"""
        else:
            cews__fsgk += f"""    {ovdxb__ujzaa} = info_to_array(info_from_table(out_table, {hwzpi__lyedb}), out_typs[{sai__lccl}])
"""
        hwzpi__lyedb += 1
    if agg_node.same_index:
        cews__fsgk += (
            """    out_index_arg = info_to_array(info_from_table(out_table, {}), index_arg)
"""
            .format(hwzpi__lyedb))
        hwzpi__lyedb += 1
    cews__fsgk += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    cews__fsgk += '    delete_table_decref_arrays(table)\n'
    cews__fsgk += '    delete_table_decref_arrays(udf_table_dummy)\n'
    cews__fsgk += '    delete_table(out_table)\n'
    cews__fsgk += f'    ev_clean.finalize()\n'
    pxu__wxilh = tuple(mut__lsend.values())
    if agg_node.return_key:
        pxu__wxilh += tuple(ukqp__kcng)
    cews__fsgk += '    return ({},{})\n'.format(', '.join(pxu__wxilh), 
        ' out_index_arg,' if agg_node.same_index else '')
    nwl__leamz = {}
    exec(cews__fsgk, {'out_typs': out_col_typs}, nwl__leamz)
    usuz__udsa = nwl__leamz['agg_top']
    return usuz__udsa


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for lglw__qmdx in block.body:
            if is_call_assign(lglw__qmdx) and find_callname(f_ir,
                lglw__qmdx.value) == ('len', 'builtins'
                ) and lglw__qmdx.value.args[0].name == f_ir.arg_names[0]:
                colxi__ezldg = get_definition(f_ir, lglw__qmdx.value.func)
                colxi__ezldg.name = 'dummy_agg_count'
                colxi__ezldg.value = dummy_agg_count
    ntxrq__lqwzv = get_name_var_table(f_ir.blocks)
    ivkeu__fzf = {}
    for name, uxu__senz in ntxrq__lqwzv.items():
        ivkeu__fzf[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, ivkeu__fzf)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    bvfvt__wpm = numba.core.compiler.Flags()
    bvfvt__wpm.nrt = True
    qnao__wsm = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, bvfvt__wpm)
    qnao__wsm.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, hvltq__wyxbl, calltypes, uxu__senz = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    neym__hdmj = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    dywt__vpf = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    rkdvt__ovyh = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    uqor__ujjr = rkdvt__ovyh(typemap, calltypes)
    pm = dywt__vpf(typingctx, targetctx, None, f_ir, typemap, hvltq__wyxbl,
        calltypes, uqor__ujjr, {}, bvfvt__wpm, None)
    wcyxw__yvqd = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = dywt__vpf(typingctx, targetctx, None, f_ir, typemap, hvltq__wyxbl,
        calltypes, uqor__ujjr, {}, bvfvt__wpm, wcyxw__yvqd)
    zhnpb__wuxdv = numba.core.typed_passes.InlineOverloads()
    zhnpb__wuxdv.run_pass(pm)
    chqta__zlk = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    chqta__zlk.run()
    for block in f_ir.blocks.values():
        for lglw__qmdx in block.body:
            if is_assign(lglw__qmdx) and isinstance(lglw__qmdx.value, (ir.
                Arg, ir.Var)) and isinstance(typemap[lglw__qmdx.target.name
                ], SeriesType):
                thtfo__pans = typemap.pop(lglw__qmdx.target.name)
                typemap[lglw__qmdx.target.name] = thtfo__pans.data
            if is_call_assign(lglw__qmdx) and find_callname(f_ir,
                lglw__qmdx.value) == ('get_series_data',
                'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[lglw__qmdx.target.name].remove(lglw__qmdx
                    .value)
                lglw__qmdx.value = lglw__qmdx.value.args[0]
                f_ir._definitions[lglw__qmdx.target.name].append(lglw__qmdx
                    .value)
            if is_call_assign(lglw__qmdx) and find_callname(f_ir,
                lglw__qmdx.value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[lglw__qmdx.target.name].remove(lglw__qmdx
                    .value)
                lglw__qmdx.value = ir.Const(False, lglw__qmdx.loc)
                f_ir._definitions[lglw__qmdx.target.name].append(lglw__qmdx
                    .value)
            if is_call_assign(lglw__qmdx) and find_callname(f_ir,
                lglw__qmdx.value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[lglw__qmdx.target.name].remove(lglw__qmdx
                    .value)
                lglw__qmdx.value = ir.Const(False, lglw__qmdx.loc)
                f_ir._definitions[lglw__qmdx.target.name].append(lglw__qmdx
                    .value)
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    yyr__gjv = numba.parfors.parfor.PreParforPass(f_ir, typemap, calltypes,
        typingctx, targetctx, neym__hdmj)
    yyr__gjv.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    lew__ilhrq = numba.core.compiler.StateDict()
    lew__ilhrq.func_ir = f_ir
    lew__ilhrq.typemap = typemap
    lew__ilhrq.calltypes = calltypes
    lew__ilhrq.typingctx = typingctx
    lew__ilhrq.targetctx = targetctx
    lew__ilhrq.return_type = hvltq__wyxbl
    numba.core.rewrites.rewrite_registry.apply('after-inference', lew__ilhrq)
    ezx__oxyj = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        hvltq__wyxbl, typingctx, targetctx, neym__hdmj, bvfvt__wpm, {})
    ezx__oxyj.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            ybqa__spn = ctypes.pythonapi.PyCell_Get
            ybqa__spn.restype = ctypes.py_object
            ybqa__spn.argtypes = ctypes.py_object,
            aqc__qezio = tuple(ybqa__spn(tfvfi__pfan) for tfvfi__pfan in
                closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            aqc__qezio = closure.items
        assert len(code.co_freevars) == len(aqc__qezio)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, aqc__qezio
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
        ble__ocypx = SeriesType(in_col_typ.dtype, in_col_typ, None, string_type
            )
        f_ir, pm = compile_to_optimized_ir(func, (ble__ocypx,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        jiqqs__kis, arr_var = _rm_arg_agg_block(block, pm.typemap)
        ocm__cdj = -1
        for sai__lccl, lglw__qmdx in enumerate(jiqqs__kis):
            if isinstance(lglw__qmdx, numba.parfors.parfor.Parfor):
                assert ocm__cdj == -1, 'only one parfor for aggregation function'
                ocm__cdj = sai__lccl
        parfor = None
        if ocm__cdj != -1:
            parfor = jiqqs__kis[ocm__cdj]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = jiqqs__kis[:ocm__cdj] + parfor.init_block.body
        eval_nodes = jiqqs__kis[ocm__cdj + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for lglw__qmdx in init_nodes:
            if is_assign(lglw__qmdx) and lglw__qmdx.target.name in redvars:
                ind = redvars.index(lglw__qmdx.target.name)
                reduce_vars[ind] = lglw__qmdx.target
        var_types = [pm.typemap[iajhg__cjy] for iajhg__cjy in redvars]
        uhng__dxgs = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        yoq__mtuf = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        pgd__xll = gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types,
            pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(pgd__xll)
        self.all_update_funcs.append(yoq__mtuf)
        self.all_combine_funcs.append(uhng__dxgs)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        self.all_vartypes = self.all_vartypes * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_vartypes
        self.all_reduce_vars = self.all_reduce_vars * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_reduce_vars
        nfsi__ziv = gen_init_func(self.all_init_nodes, self.all_reduce_vars,
            self.all_vartypes, self.typingctx, self.targetctx)
        eopwk__zmgw = gen_all_update_func(self.all_update_funcs, self.
            all_vartypes, self.in_col_types, self.redvar_offsets, self.
            typingctx, self.targetctx, self.pivot_typ, self.pivot_values,
            self.is_crosstab)
        wman__tpk = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.
            targetctx, self.pivot_typ, self.pivot_values)
        nheuy__tfhm = gen_all_eval_func(self.all_eval_funcs, self.
            all_vartypes, self.redvar_offsets, self.out_col_types, self.
            typingctx, self.targetctx, self.pivot_values)
        return (self.all_vartypes, nfsi__ziv, eopwk__zmgw, wman__tpk,
            nheuy__tfhm)


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
    vfci__awm = []
    for t, pvrqm__mry in zip(in_col_types, agg_func):
        vfci__awm.append((t, pvrqm__mry))
    siez__myhk = RegularUDFGenerator(in_col_types, out_col_types, pivot_typ,
        pivot_values, is_crosstab, typingctx, targetctx)
    blbn__rkhgj = GeneralUDFGenerator()
    for in_col_typ, func in vfci__awm:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            siez__myhk.add_udf(in_col_typ, func)
        except:
            blbn__rkhgj.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = siez__myhk.gen_all_func()
    general_udf_funcs = blbn__rkhgj.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    xydy__wgb = compute_use_defs(parfor.loop_body)
    asx__xmxet = set()
    for sff__pjvz in xydy__wgb.usemap.values():
        asx__xmxet |= sff__pjvz
    rvaq__wcwmc = set()
    for sff__pjvz in xydy__wgb.defmap.values():
        rvaq__wcwmc |= sff__pjvz
    lbsc__mvrh = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    lbsc__mvrh.body = eval_nodes
    lwom__qvtkj = compute_use_defs({(0): lbsc__mvrh})
    zhea__cbxhg = lwom__qvtkj.usemap[0]
    web__ffwx = set()
    tefg__dckoa = []
    srqzc__jeb = []
    for lglw__qmdx in reversed(init_nodes):
        dpk__rkie = {iajhg__cjy.name for iajhg__cjy in lglw__qmdx.list_vars()}
        if is_assign(lglw__qmdx):
            iajhg__cjy = lglw__qmdx.target.name
            dpk__rkie.remove(iajhg__cjy)
            if (iajhg__cjy in asx__xmxet and iajhg__cjy not in web__ffwx and
                iajhg__cjy not in zhea__cbxhg and iajhg__cjy not in rvaq__wcwmc
                ):
                srqzc__jeb.append(lglw__qmdx)
                asx__xmxet |= dpk__rkie
                rvaq__wcwmc.add(iajhg__cjy)
                continue
        web__ffwx |= dpk__rkie
        tefg__dckoa.append(lglw__qmdx)
    srqzc__jeb.reverse()
    tefg__dckoa.reverse()
    vkhr__ohl = min(parfor.loop_body.keys())
    aovoj__rwcxv = parfor.loop_body[vkhr__ohl]
    aovoj__rwcxv.body = srqzc__jeb + aovoj__rwcxv.body
    return tefg__dckoa


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    wlbv__dup = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    aeux__xka = set()
    rgjom__crxky = []
    for lglw__qmdx in init_nodes:
        if is_assign(lglw__qmdx) and isinstance(lglw__qmdx.value, ir.Global
            ) and isinstance(lglw__qmdx.value.value, pytypes.FunctionType
            ) and lglw__qmdx.value.value in wlbv__dup:
            aeux__xka.add(lglw__qmdx.target.name)
        elif is_call_assign(lglw__qmdx
            ) and lglw__qmdx.value.func.name in aeux__xka:
            pass
        else:
            rgjom__crxky.append(lglw__qmdx)
    init_nodes = rgjom__crxky
    azjtr__ndeij = types.Tuple(var_types)
    ynd__usq = lambda : None
    f_ir = compile_to_numba_ir(ynd__usq, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    iotgv__xmsy = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    opv__nkhby = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc),
        iotgv__xmsy, loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [opv__nkhby] + block.body
    block.body[-2].value.value = iotgv__xmsy
    zjtla__shw = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        azjtr__ndeij, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rqmfm__lga = numba.core.target_extension.dispatcher_registry[cpu_target](
        ynd__usq)
    rqmfm__lga.add_overload(zjtla__shw)
    return rqmfm__lga


def gen_all_update_func(update_funcs, reduce_var_types, in_col_types,
    redvar_offsets, typingctx, targetctx, pivot_typ, pivot_values, is_crosstab
    ):
    rhqlw__yefi = len(update_funcs)
    nbws__cnew = len(in_col_types)
    if pivot_values is not None:
        assert nbws__cnew == 1
    cews__fsgk = (
        'def update_all_f(redvar_arrs, data_in, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        ctgd__xqyp = redvar_offsets[nbws__cnew]
        cews__fsgk += '  pv = pivot_arr[i]\n'
        for nwbb__wbz, udmd__afu in enumerate(pivot_values):
            vdtm__kinhi = 'el' if nwbb__wbz != 0 else ''
            cews__fsgk += "  {}if pv == '{}':\n".format(vdtm__kinhi, udmd__afu)
            hbewz__tmi = ctgd__xqyp * nwbb__wbz
            vmala__abo = ', '.join(['redvar_arrs[{}][w_ind]'.format(
                sai__lccl) for sai__lccl in range(hbewz__tmi +
                redvar_offsets[0], hbewz__tmi + redvar_offsets[1])])
            yjzhd__kdgm = 'data_in[0][i]'
            if is_crosstab:
                yjzhd__kdgm = '0'
            cews__fsgk += '    {} = update_vars_0({}, {})\n'.format(vmala__abo,
                vmala__abo, yjzhd__kdgm)
    else:
        for nwbb__wbz in range(rhqlw__yefi):
            vmala__abo = ', '.join(['redvar_arrs[{}][w_ind]'.format(
                sai__lccl) for sai__lccl in range(redvar_offsets[nwbb__wbz],
                redvar_offsets[nwbb__wbz + 1])])
            if vmala__abo:
                cews__fsgk += ('  {} = update_vars_{}({},  data_in[{}][i])\n'
                    .format(vmala__abo, nwbb__wbz, vmala__abo, 0 if 
                    nbws__cnew == 1 else nwbb__wbz))
    cews__fsgk += '  return\n'
    rnn__dbdo = {}
    for sai__lccl, pvrqm__mry in enumerate(update_funcs):
        rnn__dbdo['update_vars_{}'.format(sai__lccl)] = pvrqm__mry
    nwl__leamz = {}
    exec(cews__fsgk, rnn__dbdo, nwl__leamz)
    akkl__ugfur = nwl__leamz['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(akkl__ugfur)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx, pivot_typ, pivot_values):
    pulkm__thh = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types]
        )
    arg_typs = pulkm__thh, pulkm__thh, types.intp, types.intp, pivot_typ
    tlzu__cpwyl = len(redvar_offsets) - 1
    ctgd__xqyp = redvar_offsets[tlzu__cpwyl]
    cews__fsgk = (
        'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        assert tlzu__cpwyl == 1
        for tqh__hywcf in range(len(pivot_values)):
            hbewz__tmi = ctgd__xqyp * tqh__hywcf
            vmala__abo = ', '.join(['redvar_arrs[{}][w_ind]'.format(
                sai__lccl) for sai__lccl in range(hbewz__tmi +
                redvar_offsets[0], hbewz__tmi + redvar_offsets[1])])
            znxg__fzj = ', '.join(['recv_arrs[{}][i]'.format(sai__lccl) for
                sai__lccl in range(hbewz__tmi + redvar_offsets[0], 
                hbewz__tmi + redvar_offsets[1])])
            cews__fsgk += '  {} = combine_vars_0({}, {})\n'.format(vmala__abo,
                vmala__abo, znxg__fzj)
    else:
        for nwbb__wbz in range(tlzu__cpwyl):
            vmala__abo = ', '.join(['redvar_arrs[{}][w_ind]'.format(
                sai__lccl) for sai__lccl in range(redvar_offsets[nwbb__wbz],
                redvar_offsets[nwbb__wbz + 1])])
            znxg__fzj = ', '.join(['recv_arrs[{}][i]'.format(sai__lccl) for
                sai__lccl in range(redvar_offsets[nwbb__wbz],
                redvar_offsets[nwbb__wbz + 1])])
            if znxg__fzj:
                cews__fsgk += '  {} = combine_vars_{}({}, {})\n'.format(
                    vmala__abo, nwbb__wbz, vmala__abo, znxg__fzj)
    cews__fsgk += '  return\n'
    rnn__dbdo = {}
    for sai__lccl, pvrqm__mry in enumerate(combine_funcs):
        rnn__dbdo['combine_vars_{}'.format(sai__lccl)] = pvrqm__mry
    nwl__leamz = {}
    exec(cews__fsgk, rnn__dbdo, nwl__leamz)
    eyxpz__omkb = nwl__leamz['combine_all_f']
    f_ir = compile_to_numba_ir(eyxpz__omkb, rnn__dbdo)
    wman__tpk = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rqmfm__lga = numba.core.target_extension.dispatcher_registry[cpu_target](
        eyxpz__omkb)
    rqmfm__lga.add_overload(wman__tpk)
    return rqmfm__lga


def gen_all_eval_func(eval_funcs, reduce_var_types, redvar_offsets,
    out_col_typs, typingctx, targetctx, pivot_values):
    pulkm__thh = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types]
        )
    out_col_typs = types.Tuple(out_col_typs)
    tlzu__cpwyl = len(redvar_offsets) - 1
    ctgd__xqyp = redvar_offsets[tlzu__cpwyl]
    cews__fsgk = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    if pivot_values is not None:
        assert tlzu__cpwyl == 1
        for nwbb__wbz in range(len(pivot_values)):
            hbewz__tmi = ctgd__xqyp * nwbb__wbz
            vmala__abo = ', '.join(['redvar_arrs[{}][j]'.format(sai__lccl) for
                sai__lccl in range(hbewz__tmi + redvar_offsets[0], 
                hbewz__tmi + redvar_offsets[1])])
            cews__fsgk += '  out_arrs[{}][j] = eval_vars_0({})\n'.format(
                nwbb__wbz, vmala__abo)
    else:
        for nwbb__wbz in range(tlzu__cpwyl):
            vmala__abo = ', '.join(['redvar_arrs[{}][j]'.format(sai__lccl) for
                sai__lccl in range(redvar_offsets[nwbb__wbz],
                redvar_offsets[nwbb__wbz + 1])])
            cews__fsgk += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
                nwbb__wbz, nwbb__wbz, vmala__abo)
    cews__fsgk += '  return\n'
    rnn__dbdo = {}
    for sai__lccl, pvrqm__mry in enumerate(eval_funcs):
        rnn__dbdo['eval_vars_{}'.format(sai__lccl)] = pvrqm__mry
    nwl__leamz = {}
    exec(cews__fsgk, rnn__dbdo, nwl__leamz)
    smaw__tpgq = nwl__leamz['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(smaw__tpgq)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    wgaii__dtf = len(var_types)
    lpit__txmpb = [f'in{sai__lccl}' for sai__lccl in range(wgaii__dtf)]
    azjtr__ndeij = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    xkr__vzknu = azjtr__ndeij(0)
    cews__fsgk = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        lpit__txmpb))
    nwl__leamz = {}
    exec(cews__fsgk, {'_zero': xkr__vzknu}, nwl__leamz)
    jfsnx__luqyw = nwl__leamz['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(jfsnx__luqyw, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': xkr__vzknu}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    dbndk__zduna = []
    for sai__lccl, iajhg__cjy in enumerate(reduce_vars):
        dbndk__zduna.append(ir.Assign(block.body[sai__lccl].target,
            iajhg__cjy, iajhg__cjy.loc))
        for mdusv__ncbf in iajhg__cjy.versioned_names:
            dbndk__zduna.append(ir.Assign(iajhg__cjy, ir.Var(iajhg__cjy.
                scope, mdusv__ncbf, iajhg__cjy.loc), iajhg__cjy.loc))
    block.body = block.body[:wgaii__dtf] + dbndk__zduna + eval_nodes
    pgd__xll = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        azjtr__ndeij, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rqmfm__lga = numba.core.target_extension.dispatcher_registry[cpu_target](
        jfsnx__luqyw)
    rqmfm__lga.add_overload(pgd__xll)
    return rqmfm__lga


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    wgaii__dtf = len(redvars)
    tgu__zws = [f'v{sai__lccl}' for sai__lccl in range(wgaii__dtf)]
    lpit__txmpb = [f'in{sai__lccl}' for sai__lccl in range(wgaii__dtf)]
    cews__fsgk = 'def agg_combine({}):\n'.format(', '.join(tgu__zws +
        lpit__txmpb))
    owhhy__cfdh = wrap_parfor_blocks(parfor)
    tqd__vqnzg = find_topo_order(owhhy__cfdh)
    tqd__vqnzg = tqd__vqnzg[1:]
    unwrap_parfor_blocks(parfor)
    xam__atiac = {}
    apbxf__ski = []
    for hnjb__uum in tqd__vqnzg:
        xye__igfa = parfor.loop_body[hnjb__uum]
        for lglw__qmdx in xye__igfa.body:
            if is_call_assign(lglw__qmdx) and guard(find_callname, f_ir,
                lglw__qmdx.value) == ('__special_combine', 'bodo.ir.aggregate'
                ):
                args = lglw__qmdx.value.args
                vookp__jnns = []
                rugdf__rjop = []
                for iajhg__cjy in args[:-1]:
                    ind = redvars.index(iajhg__cjy.name)
                    apbxf__ski.append(ind)
                    vookp__jnns.append('v{}'.format(ind))
                    rugdf__rjop.append('in{}'.format(ind))
                agp__ncae = '__special_combine__{}'.format(len(xam__atiac))
                cews__fsgk += '    ({},) = {}({})\n'.format(', '.join(
                    vookp__jnns), agp__ncae, ', '.join(vookp__jnns +
                    rugdf__rjop))
                oac__vgo = ir.Expr.call(args[-1], [], (), xye__igfa.loc)
                rfi__pak = guard(find_callname, f_ir, oac__vgo)
                assert rfi__pak == ('_var_combine', 'bodo.ir.aggregate')
                rfi__pak = bodo.ir.aggregate._var_combine
                xam__atiac[agp__ncae] = rfi__pak
            if is_assign(lglw__qmdx) and lglw__qmdx.target.name in redvars:
                apytq__rgg = lglw__qmdx.target.name
                ind = redvars.index(apytq__rgg)
                if ind in apbxf__ski:
                    continue
                if len(f_ir._definitions[apytq__rgg]) == 2:
                    var_def = f_ir._definitions[apytq__rgg][0]
                    cews__fsgk += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[apytq__rgg][1]
                    cews__fsgk += _match_reduce_def(var_def, f_ir, ind)
    cews__fsgk += '    return {}'.format(', '.join(['v{}'.format(sai__lccl) for
        sai__lccl in range(wgaii__dtf)]))
    nwl__leamz = {}
    exec(cews__fsgk, {}, nwl__leamz)
    ejv__vwdmf = nwl__leamz['agg_combine']
    arg_typs = tuple(2 * var_types)
    rnn__dbdo = {'numba': numba, 'bodo': bodo, 'np': np}
    rnn__dbdo.update(xam__atiac)
    f_ir = compile_to_numba_ir(ejv__vwdmf, rnn__dbdo, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    azjtr__ndeij = pm.typemap[block.body[-1].value.name]
    uhng__dxgs = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        azjtr__ndeij, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rqmfm__lga = numba.core.target_extension.dispatcher_registry[cpu_target](
        ejv__vwdmf)
    rqmfm__lga.add_overload(uhng__dxgs)
    return rqmfm__lga


def _match_reduce_def(var_def, f_ir, ind):
    cews__fsgk = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        cews__fsgk = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        bqch__wvqz = guard(find_callname, f_ir, var_def)
        if bqch__wvqz == ('min', 'builtins'):
            cews__fsgk = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if bqch__wvqz == ('max', 'builtins'):
            cews__fsgk = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return cews__fsgk


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    wgaii__dtf = len(redvars)
    yrp__wamuy = 1
    vbdhc__oywaz = []
    for sai__lccl in range(yrp__wamuy):
        zon__evqzy = ir.Var(arr_var.scope, f'$input{sai__lccl}', arr_var.loc)
        vbdhc__oywaz.append(zon__evqzy)
    vcbuz__arkru = parfor.loop_nests[0].index_variable
    hhk__xcoeq = [0] * wgaii__dtf
    for xye__igfa in parfor.loop_body.values():
        ksnvf__pyly = []
        for lglw__qmdx in xye__igfa.body:
            if is_var_assign(lglw__qmdx
                ) and lglw__qmdx.value.name == vcbuz__arkru.name:
                continue
            if is_getitem(lglw__qmdx
                ) and lglw__qmdx.value.value.name == arr_var.name:
                lglw__qmdx.value = vbdhc__oywaz[0]
            if is_call_assign(lglw__qmdx) and guard(find_callname, pm.
                func_ir, lglw__qmdx.value) == ('isna',
                'bodo.libs.array_kernels') and lglw__qmdx.value.args[0
                ].name == arr_var.name:
                lglw__qmdx.value = ir.Const(False, lglw__qmdx.target.loc)
            if is_assign(lglw__qmdx) and lglw__qmdx.target.name in redvars:
                ind = redvars.index(lglw__qmdx.target.name)
                hhk__xcoeq[ind] = lglw__qmdx.target
            ksnvf__pyly.append(lglw__qmdx)
        xye__igfa.body = ksnvf__pyly
    tgu__zws = ['v{}'.format(sai__lccl) for sai__lccl in range(wgaii__dtf)]
    lpit__txmpb = ['in{}'.format(sai__lccl) for sai__lccl in range(yrp__wamuy)]
    cews__fsgk = 'def agg_update({}):\n'.format(', '.join(tgu__zws +
        lpit__txmpb))
    cews__fsgk += '    __update_redvars()\n'
    cews__fsgk += '    return {}'.format(', '.join(['v{}'.format(sai__lccl) for
        sai__lccl in range(wgaii__dtf)]))
    nwl__leamz = {}
    exec(cews__fsgk, {}, nwl__leamz)
    wfgi__swf = nwl__leamz['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * yrp__wamuy)
    f_ir = compile_to_numba_ir(wfgi__swf, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    ugrf__iipb = f_ir.blocks.popitem()[1].body
    azjtr__ndeij = pm.typemap[ugrf__iipb[-1].value.name]
    owhhy__cfdh = wrap_parfor_blocks(parfor)
    tqd__vqnzg = find_topo_order(owhhy__cfdh)
    tqd__vqnzg = tqd__vqnzg[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    aovoj__rwcxv = f_ir.blocks[tqd__vqnzg[0]]
    rtuo__evpj = f_ir.blocks[tqd__vqnzg[-1]]
    frez__hncph = ugrf__iipb[:wgaii__dtf + yrp__wamuy]
    if wgaii__dtf > 1:
        wcaf__sedly = ugrf__iipb[-3:]
        assert is_assign(wcaf__sedly[0]) and isinstance(wcaf__sedly[0].
            value, ir.Expr) and wcaf__sedly[0].value.op == 'build_tuple'
    else:
        wcaf__sedly = ugrf__iipb[-2:]
    for sai__lccl in range(wgaii__dtf):
        dqfa__cdkh = ugrf__iipb[sai__lccl].target
        kdpz__qyy = ir.Assign(dqfa__cdkh, hhk__xcoeq[sai__lccl], dqfa__cdkh.loc
            )
        frez__hncph.append(kdpz__qyy)
    for sai__lccl in range(wgaii__dtf, wgaii__dtf + yrp__wamuy):
        dqfa__cdkh = ugrf__iipb[sai__lccl].target
        kdpz__qyy = ir.Assign(dqfa__cdkh, vbdhc__oywaz[sai__lccl -
            wgaii__dtf], dqfa__cdkh.loc)
        frez__hncph.append(kdpz__qyy)
    aovoj__rwcxv.body = frez__hncph + aovoj__rwcxv.body
    ekurz__qycu = []
    for sai__lccl in range(wgaii__dtf):
        dqfa__cdkh = ugrf__iipb[sai__lccl].target
        kdpz__qyy = ir.Assign(hhk__xcoeq[sai__lccl], dqfa__cdkh, dqfa__cdkh.loc
            )
        ekurz__qycu.append(kdpz__qyy)
    rtuo__evpj.body += ekurz__qycu + wcaf__sedly
    vqbfh__zxlts = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        azjtr__ndeij, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rqmfm__lga = numba.core.target_extension.dispatcher_registry[cpu_target](
        wfgi__swf)
    rqmfm__lga.add_overload(vqbfh__zxlts)
    return rqmfm__lga


def _rm_arg_agg_block(block, typemap):
    jiqqs__kis = []
    arr_var = None
    for sai__lccl, lglw__qmdx in enumerate(block.body):
        if is_assign(lglw__qmdx) and isinstance(lglw__qmdx.value, ir.Arg):
            arr_var = lglw__qmdx.target
            bzmda__wspv = typemap[arr_var.name]
            if not isinstance(bzmda__wspv, types.ArrayCompatible):
                jiqqs__kis += block.body[sai__lccl + 1:]
                break
            mrmlz__muug = block.body[sai__lccl + 1]
            assert is_assign(mrmlz__muug) and isinstance(mrmlz__muug.value,
                ir.Expr
                ) and mrmlz__muug.value.op == 'getattr' and mrmlz__muug.value.attr == 'shape' and mrmlz__muug.value.value.name == arr_var.name
            rdx__cfbd = mrmlz__muug.target
            oao__fjmqx = block.body[sai__lccl + 2]
            assert is_assign(oao__fjmqx) and isinstance(oao__fjmqx.value,
                ir.Expr
                ) and oao__fjmqx.value.op == 'static_getitem' and oao__fjmqx.value.value.name == rdx__cfbd.name
            jiqqs__kis += block.body[sai__lccl + 3:]
            break
        jiqqs__kis.append(lglw__qmdx)
    return jiqqs__kis, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    owhhy__cfdh = wrap_parfor_blocks(parfor)
    tqd__vqnzg = find_topo_order(owhhy__cfdh)
    tqd__vqnzg = tqd__vqnzg[1:]
    unwrap_parfor_blocks(parfor)
    for hnjb__uum in reversed(tqd__vqnzg):
        for lglw__qmdx in reversed(parfor.loop_body[hnjb__uum].body):
            if isinstance(lglw__qmdx, ir.Assign) and (lglw__qmdx.target.
                name in parfor_params or lglw__qmdx.target.name in var_to_param
                ):
                hmoe__vnwg = lglw__qmdx.target.name
                rhs = lglw__qmdx.value
                uhl__nmbw = (hmoe__vnwg if hmoe__vnwg in parfor_params else
                    var_to_param[hmoe__vnwg])
                horsq__opv = []
                if isinstance(rhs, ir.Var):
                    horsq__opv = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    horsq__opv = [iajhg__cjy.name for iajhg__cjy in
                        lglw__qmdx.value.list_vars()]
                param_uses[uhl__nmbw].extend(horsq__opv)
                for iajhg__cjy in horsq__opv:
                    var_to_param[iajhg__cjy] = uhl__nmbw
            if isinstance(lglw__qmdx, Parfor):
                get_parfor_reductions(lglw__qmdx, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for ugatw__nica, horsq__opv in param_uses.items():
        if ugatw__nica in horsq__opv and ugatw__nica not in reduce_varnames:
            reduce_varnames.append(ugatw__nica)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
