"""
Helper functions for transformations.
"""
import itertools
import math
import operator
import types as pytypes
from collections import namedtuple
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, types
from numba.core.ir_utils import GuardException, build_definitions, compile_to_numba_ir, compute_cfg_from_blocks, find_callname, find_const, get_definition, guard, is_setitem, mk_unique_var, replace_arg_nodes, require
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import fold_arguments
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoConstUpdatedError, BodoError, can_literalize_type, get_literal_value, get_overload_const_bool, get_overload_const_list, is_literal_type, is_overload_constant_bool
from bodo.utils.utils import is_array_typ, is_assign, is_call, is_expr
ReplaceFunc = namedtuple('ReplaceFunc', ['func', 'arg_types', 'args',
    'glbls', 'inline_bodo_calls', 'run_full_pipeline', 'pre_nodes'])
bodo_types_with_params = {'ArrayItemArrayType', 'CSRMatrixType',
    'CategoricalArrayType', 'CategoricalIndexType', 'DataFrameType',
    'DatetimeIndexType', 'Decimal128Type', 'DecimalArrayType',
    'IntegerArrayType', 'IntervalArrayType', 'IntervalIndexType', 'List',
    'MapArrayType', 'NumericIndexType', 'PDCategoricalDtype',
    'PeriodIndexType', 'RangeIndexType', 'SeriesType', 'StringIndexType',
    'BinaryIndexType', 'StructArrayType', 'TimedeltaIndexType',
    'TupleArrayType'}
container_update_method_names = ('clear', 'pop', 'popitem', 'update', 'add',
    'difference_update', 'discard', 'intersection_update', 'remove',
    'symmetric_difference_update', 'append', 'extend', 'insert', 'reverse',
    'sort')
no_side_effect_call_tuples = {(int,), (list,), (set,), (dict,), (min,), (
    max,), (abs,), (len,), (bool,), (str,), ('ceil', math), ('init_series',
    'pd_series_ext', 'hiframes', bodo), ('get_series_data', 'pd_series_ext',
    'hiframes', bodo), ('get_series_index', 'pd_series_ext', 'hiframes',
    bodo), ('get_series_name', 'pd_series_ext', 'hiframes', bodo), (
    'get_index_data', 'pd_index_ext', 'hiframes', bodo), ('get_index_name',
    'pd_index_ext', 'hiframes', bodo), ('init_binary_str_index',
    'pd_index_ext', 'hiframes', bodo), ('init_numeric_index',
    'pd_index_ext', 'hiframes', bodo), ('init_categorical_index',
    'pd_index_ext', 'hiframes', bodo), ('_dti_val_finalize', 'pd_index_ext',
    'hiframes', bodo), ('init_datetime_index', 'pd_index_ext', 'hiframes',
    bodo), ('init_timedelta_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_range_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_heter_index', 'pd_index_ext', 'hiframes', bodo), (
    'get_int_arr_data', 'int_arr_ext', 'libs', bodo), ('get_int_arr_bitmap',
    'int_arr_ext', 'libs', bodo), ('init_integer_array', 'int_arr_ext',
    'libs', bodo), ('alloc_int_array', 'int_arr_ext', 'libs', bodo), (
    'inplace_eq', 'str_arr_ext', 'libs', bodo), ('get_bool_arr_data',
    'bool_arr_ext', 'libs', bodo), ('get_bool_arr_bitmap', 'bool_arr_ext',
    'libs', bodo), ('init_bool_array', 'bool_arr_ext', 'libs', bodo), (
    'alloc_bool_array', 'bool_arr_ext', 'libs', bodo), (
    'datetime_date_arr_to_dt64_arr', 'pd_timestamp_ext', 'hiframes', bodo),
    (bodo.libs.bool_arr_ext.compute_or_body,), (bodo.libs.bool_arr_ext.
    compute_and_body,), ('alloc_datetime_date_array', 'datetime_date_ext',
    'hiframes', bodo), ('alloc_datetime_timedelta_array',
    'datetime_timedelta_ext', 'hiframes', bodo), ('cat_replace',
    'pd_categorical_ext', 'hiframes', bodo), ('init_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('alloc_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('get_categorical_arr_codes',
    'pd_categorical_ext', 'hiframes', bodo), ('_sum_handle_nan',
    'series_kernels', 'hiframes', bodo), ('_box_cat_val', 'series_kernels',
    'hiframes', bodo), ('_mean_handle_nan', 'series_kernels', 'hiframes',
    bodo), ('_var_handle_mincount', 'series_kernels', 'hiframes', bodo), (
    '_compute_var_nan_count_ddof', 'series_kernels', 'hiframes', bodo), (
    '_sem_handle_nan', 'series_kernels', 'hiframes', bodo), ('dist_return',
    'distributed_api', 'libs', bodo), ('rep_return', 'distributed_api',
    'libs', bodo), ('init_dataframe', 'pd_dataframe_ext', 'hiframes', bodo),
    ('get_dataframe_data', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_dataframe_table', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_dataframe_column_names', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_table_data', 'table', 'hiframes', bodo), ('get_dataframe_index',
    'pd_dataframe_ext', 'hiframes', bodo), ('init_rolling',
    'pd_rolling_ext', 'hiframes', bodo), ('init_groupby', 'pd_groupby_ext',
    'hiframes', bodo), ('calc_nitems', 'array_kernels', 'libs', bodo), (
    'concat', 'array_kernels', 'libs', bodo), ('unique', 'array_kernels',
    'libs', bodo), ('nunique', 'array_kernels', 'libs', bodo), ('quantile',
    'array_kernels', 'libs', bodo), ('explode', 'array_kernels', 'libs',
    bodo), ('explode_no_index', 'array_kernels', 'libs', bodo), (
    'get_arr_lens', 'array_kernels', 'libs', bodo), (
    'str_arr_from_sequence', 'str_arr_ext', 'libs', bodo), (
    'get_str_arr_str_length', 'str_arr_ext', 'libs', bodo), (
    'parse_datetime_str', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_dt64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'dt64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'timedelta64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_timedelta64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'npy_datetimestruct_to_datetime', 'pd_timestamp_ext', 'hiframes', bodo),
    ('isna', 'array_kernels', 'libs', bodo), ('copy',), (
    'from_iterable_impl', 'typing', 'utils', bodo), ('chain', itertools), (
    'groupby',), ('rolling',), (pd.CategoricalDtype,), (bodo.hiframes.
    pd_categorical_ext.get_code_for_value,), ('asarray', np), ('int32', np),
    ('int64', np), ('float64', np), ('float32', np), ('bool_', np), ('full',
    np), ('round', np), ('isnan', np), ('isnat', np), ('arange', np), (
    'internal_prange', 'parfor', numba), ('internal_prange', 'parfor',
    'parfors', numba), ('empty_inferred', 'ndarray', 'unsafe', numba), (
    '_slice_span', 'unicode', numba), ('_normalize_slice', 'unicode', numba
    ), ('init_session_builder', 'pyspark_ext', 'libs', bodo), (
    'init_session', 'pyspark_ext', 'libs', bodo), ('init_spark_df',
    'pyspark_ext', 'libs', bodo), ('h5size', 'h5_api', 'io', bodo), (
    'pre_alloc_struct_array', 'struct_arr_ext', 'libs', bodo), (bodo.libs.
    struct_arr_ext.pre_alloc_struct_array,), ('pre_alloc_tuple_array',
    'tuple_arr_ext', 'libs', bodo), (bodo.libs.tuple_arr_ext.
    pre_alloc_tuple_array,), ('pre_alloc_array_item_array',
    'array_item_arr_ext', 'libs', bodo), (bodo.libs.array_item_arr_ext.
    pre_alloc_array_item_array,), ('dist_reduce', 'distributed_api', 'libs',
    bodo), (bodo.libs.distributed_api.dist_reduce,), (
    'pre_alloc_string_array', 'str_arr_ext', 'libs', bodo), (bodo.libs.
    str_arr_ext.pre_alloc_string_array,), ('pre_alloc_binary_array',
    'binary_arr_ext', 'libs', bodo), (bodo.libs.binary_arr_ext.
    pre_alloc_binary_array,), ('pre_alloc_map_array', 'map_arr_ext', 'libs',
    bodo), (bodo.libs.map_arr_ext.pre_alloc_map_array,), (
    'convert_dict_arr_to_int', 'dict_arr_ext', 'libs', bodo), (
    'cat_dict_str', 'dict_arr_ext', 'libs', bodo), ('str_replace',
    'dict_arr_ext', 'libs', bodo), ('dict_arr_eq', 'dict_arr_ext', 'libs',
    bodo), ('dict_arr_ne', 'dict_arr_ext', 'libs', bodo), ('str_startswith',
    'dict_arr_ext', 'libs', bodo), ('str_endswith', 'dict_arr_ext', 'libs',
    bodo), ('str_contains_non_regex', 'dict_arr_ext', 'libs', bodo), (
    'str_series_contains_regex', 'dict_arr_ext', 'libs', bodo), (
    'str_capitalize', 'dict_arr_ext', 'libs', bodo), ('str_lower',
    'dict_arr_ext', 'libs', bodo), ('str_swapcase', 'dict_arr_ext', 'libs',
    bodo), ('str_title', 'dict_arr_ext', 'libs', bodo), ('str_upper',
    'dict_arr_ext', 'libs', bodo), ('str_center', 'dict_arr_ext', 'libs',
    bodo), ('str_get', 'dict_arr_ext', 'libs', bodo), ('str_repeat_int',
    'dict_arr_ext', 'libs', bodo), ('str_lstrip', 'dict_arr_ext', 'libs',
    bodo), ('str_rstrip', 'dict_arr_ext', 'libs', bodo), ('str_strip',
    'dict_arr_ext', 'libs', bodo), ('str_zfill', 'dict_arr_ext', 'libs',
    bodo), ('str_ljust', 'dict_arr_ext', 'libs', bodo), ('str_rjust',
    'dict_arr_ext', 'libs', bodo), ('str_find', 'dict_arr_ext', 'libs',
    bodo), ('str_rfind', 'dict_arr_ext', 'libs', bodo), ('str_slice',
    'dict_arr_ext', 'libs', bodo), ('str_extract', 'dict_arr_ext', 'libs',
    bodo), ('str_extractall', 'dict_arr_ext', 'libs', bodo), (
    'str_extractall_multi', 'dict_arr_ext', 'libs', bodo), ('str_len',
    'dict_arr_ext', 'libs', bodo), ('str_count', 'dict_arr_ext', 'libs',
    bodo), ('str_isalnum', 'dict_arr_ext', 'libs', bodo), ('str_isalpha',
    'dict_arr_ext', 'libs', bodo), ('str_isdigit', 'dict_arr_ext', 'libs',
    bodo), ('str_isspace', 'dict_arr_ext', 'libs', bodo), ('str_islower',
    'dict_arr_ext', 'libs', bodo), ('str_isupper', 'dict_arr_ext', 'libs',
    bodo), ('str_istitle', 'dict_arr_ext', 'libs', bodo), ('str_isnumeric',
    'dict_arr_ext', 'libs', bodo), ('str_isdecimal', 'dict_arr_ext', 'libs',
    bodo), ('prange', bodo), (bodo.prange,), ('objmode', bodo), (bodo.
    objmode,), ('get_label_dict_from_categories', 'pd_categorial_ext',
    'hiframes', bodo), ('get_label_dict_from_categories_no_duplicates',
    'pd_categorial_ext', 'hiframes', bodo), ('build_nullable_tuple',
    'nullable_tuple_ext', 'libs', bodo), ('generate_mappable_table_func',
    'table_utils', 'utils', bodo), ('table_astype', 'table_utils', 'utils',
    bodo), ('table_concat', 'table_utils', 'utils', bodo), ('table_filter',
    'table', 'hiframes', bodo), ('table_subset', 'table', 'hiframes', bodo)}


def remove_hiframes(rhs, lives, call_list):
    gmhn__xvfic = tuple(call_list)
    if gmhn__xvfic in no_side_effect_call_tuples:
        return True
    if gmhn__xvfic == (bodo.hiframes.pd_index_ext.init_range_index,):
        return True
    if len(call_list) == 4 and call_list[1:] == ['conversion', 'utils', bodo]:
        return True
    if isinstance(call_list[-1], pytypes.ModuleType) and call_list[-1
        ].__name__ == 'bodosql':
        return True
    if len(call_list) == 2 and call_list[0] == 'copy':
        return True
    if call_list == ['h5read', 'h5_api', 'io', bodo] and rhs.args[5
        ].name not in lives:
        return True
    if call_list == ['move_str_binary_arr_payload', 'str_arr_ext', 'libs', bodo
        ] and rhs.args[0].name not in lives:
        return True
    if call_list == ['setna', 'array_kernels', 'libs', bodo] and rhs.args[0
        ].name not in lives:
        return True
    if call_list == ['set_table_data', 'table', 'hiframes', bodo] and rhs.args[
        0].name not in lives:
        return True
    if call_list == ['set_table_data_null', 'table', 'hiframes', bodo
        ] and rhs.args[0].name not in lives:
        return True
    if call_list == ['ensure_column_unboxed', 'table', 'hiframes', bodo
        ] and rhs.args[0].name not in lives and rhs.args[1].name not in lives:
        return True
    if call_list == ['generate_table_nbytes', 'table_utils', 'utils', bodo
        ] and rhs.args[1].name not in lives:
        return True
    if len(gmhn__xvfic) == 1 and tuple in getattr(gmhn__xvfic[0], '__mro__', ()
        ):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        ybuvy__zza = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        ybuvy__zza = func.__globals__
    if extra_globals is not None:
        ybuvy__zza.update(extra_globals)
    if add_default_globals:
        ybuvy__zza.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, ybuvy__zza, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[yvfta__fyg.name] for yvfta__fyg in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, ybuvy__zza)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        tqes__xhw = tuple(typing_info.typemap[yvfta__fyg.name] for
            yvfta__fyg in args)
        ffk__ixx = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, tqes__xhw, {}, {}, flags)
        ffk__ixx.run()
    nli__uns = f_ir.blocks.popitem()[1]
    replace_arg_nodes(nli__uns, args)
    tkv__zuhb = nli__uns.body[:-2]
    update_locs(tkv__zuhb[len(args):], loc)
    for stmt in tkv__zuhb[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        veo__uky = nli__uns.body[-2]
        assert is_assign(veo__uky) and is_expr(veo__uky.value, 'cast')
        yvzcv__vrkz = veo__uky.value.value
        tkv__zuhb.append(ir.Assign(yvzcv__vrkz, ret_var, loc))
    return tkv__zuhb


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for jul__yjkud in stmt.list_vars():
            jul__yjkud.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        jvs__ufe = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        eox__venxl, xuktf__emp = jvs__ufe(stmt)
        return xuktf__emp
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        grwc__iks = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(grwc__iks, ir.UndefinedType):
            vnkql__jiqt = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{vnkql__jiqt}' is not defined", loc=loc)
    except GuardException as zwfj__qvy:
        raise BodoError(err_msg, loc=loc)
    return grwc__iks


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    msf__lnmkr = get_definition(func_ir, var)
    hgrcu__wkrbx = None
    if typemap is not None:
        hgrcu__wkrbx = typemap.get(var.name, None)
    if isinstance(msf__lnmkr, ir.Arg) and arg_types is not None:
        hgrcu__wkrbx = arg_types[msf__lnmkr.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(hgrcu__wkrbx):
        return get_literal_value(hgrcu__wkrbx)
    if isinstance(msf__lnmkr, (ir.Const, ir.Global, ir.FreeVar)):
        grwc__iks = msf__lnmkr.value
        return grwc__iks
    if literalize_args and isinstance(msf__lnmkr, ir.Arg
        ) and can_literalize_type(hgrcu__wkrbx, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({msf__lnmkr.index}, loc=var
            .loc, file_infos={msf__lnmkr.index: file_info} if file_info is not
            None else None)
    if is_expr(msf__lnmkr, 'binop'):
        if file_info and msf__lnmkr.fn == operator.add:
            try:
                eaim__xeiv = get_const_value_inner(func_ir, msf__lnmkr.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(eaim__xeiv, True)
                juz__ghte = get_const_value_inner(func_ir, msf__lnmkr.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return msf__lnmkr.fn(eaim__xeiv, juz__ghte)
            except (GuardException, BodoConstUpdatedError) as zwfj__qvy:
                pass
            try:
                juz__ghte = get_const_value_inner(func_ir, msf__lnmkr.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(juz__ghte, False)
                eaim__xeiv = get_const_value_inner(func_ir, msf__lnmkr.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return msf__lnmkr.fn(eaim__xeiv, juz__ghte)
            except (GuardException, BodoConstUpdatedError) as zwfj__qvy:
                pass
        eaim__xeiv = get_const_value_inner(func_ir, msf__lnmkr.lhs,
            arg_types, typemap, updated_containers)
        juz__ghte = get_const_value_inner(func_ir, msf__lnmkr.rhs,
            arg_types, typemap, updated_containers)
        return msf__lnmkr.fn(eaim__xeiv, juz__ghte)
    if is_expr(msf__lnmkr, 'unary'):
        grwc__iks = get_const_value_inner(func_ir, msf__lnmkr.value,
            arg_types, typemap, updated_containers)
        return msf__lnmkr.fn(grwc__iks)
    if is_expr(msf__lnmkr, 'getattr') and typemap:
        jza__gwpm = typemap.get(msf__lnmkr.value.name, None)
        if isinstance(jza__gwpm, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and msf__lnmkr.attr == 'columns':
            return pd.Index(jza__gwpm.columns)
        if isinstance(jza__gwpm, types.SliceType):
            nzn__didqd = get_definition(func_ir, msf__lnmkr.value)
            require(is_call(nzn__didqd))
            rdod__jcwxw = find_callname(func_ir, nzn__didqd)
            xapqj__xotl = False
            if rdod__jcwxw == ('_normalize_slice', 'numba.cpython.unicode'):
                require(msf__lnmkr.attr in ('start', 'step'))
                nzn__didqd = get_definition(func_ir, nzn__didqd.args[0])
                xapqj__xotl = True
            require(find_callname(func_ir, nzn__didqd) == ('slice', 'builtins')
                )
            if len(nzn__didqd.args) == 1:
                if msf__lnmkr.attr == 'start':
                    return 0
                if msf__lnmkr.attr == 'step':
                    return 1
                require(msf__lnmkr.attr == 'stop')
                return get_const_value_inner(func_ir, nzn__didqd.args[0],
                    arg_types, typemap, updated_containers)
            if msf__lnmkr.attr == 'start':
                grwc__iks = get_const_value_inner(func_ir, nzn__didqd.args[
                    0], arg_types, typemap, updated_containers)
                if grwc__iks is None:
                    grwc__iks = 0
                if xapqj__xotl:
                    require(grwc__iks == 0)
                return grwc__iks
            if msf__lnmkr.attr == 'stop':
                assert not xapqj__xotl
                return get_const_value_inner(func_ir, nzn__didqd.args[1],
                    arg_types, typemap, updated_containers)
            require(msf__lnmkr.attr == 'step')
            if len(nzn__didqd.args) == 2:
                return 1
            else:
                grwc__iks = get_const_value_inner(func_ir, nzn__didqd.args[
                    2], arg_types, typemap, updated_containers)
                if grwc__iks is None:
                    grwc__iks = 1
                if xapqj__xotl:
                    require(grwc__iks == 1)
                return grwc__iks
    if is_expr(msf__lnmkr, 'getattr'):
        return getattr(get_const_value_inner(func_ir, msf__lnmkr.value,
            arg_types, typemap, updated_containers), msf__lnmkr.attr)
    if is_expr(msf__lnmkr, 'getitem'):
        value = get_const_value_inner(func_ir, msf__lnmkr.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, msf__lnmkr.index, arg_types,
            typemap, updated_containers)
        return value[index]
    jkxd__wcng = guard(find_callname, func_ir, msf__lnmkr, typemap)
    if jkxd__wcng is not None and len(jkxd__wcng) == 2 and jkxd__wcng[0
        ] == 'keys' and isinstance(jkxd__wcng[1], ir.Var):
        xweoq__eyi = msf__lnmkr.func
        msf__lnmkr = get_definition(func_ir, jkxd__wcng[1])
        psc__insyl = jkxd__wcng[1].name
        if updated_containers and psc__insyl in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                psc__insyl, updated_containers[psc__insyl]))
        require(is_expr(msf__lnmkr, 'build_map'))
        vals = [jul__yjkud[0] for jul__yjkud in msf__lnmkr.items]
        rlyao__xci = guard(get_definition, func_ir, xweoq__eyi)
        assert isinstance(rlyao__xci, ir.Expr) and rlyao__xci.attr == 'keys'
        rlyao__xci.attr = 'copy'
        return [get_const_value_inner(func_ir, jul__yjkud, arg_types,
            typemap, updated_containers) for jul__yjkud in vals]
    if is_expr(msf__lnmkr, 'build_map'):
        return {get_const_value_inner(func_ir, jul__yjkud[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            jul__yjkud[1], arg_types, typemap, updated_containers) for
            jul__yjkud in msf__lnmkr.items}
    if is_expr(msf__lnmkr, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, jul__yjkud, arg_types,
            typemap, updated_containers) for jul__yjkud in msf__lnmkr.items)
    if is_expr(msf__lnmkr, 'build_list'):
        return [get_const_value_inner(func_ir, jul__yjkud, arg_types,
            typemap, updated_containers) for jul__yjkud in msf__lnmkr.items]
    if is_expr(msf__lnmkr, 'build_set'):
        return {get_const_value_inner(func_ir, jul__yjkud, arg_types,
            typemap, updated_containers) for jul__yjkud in msf__lnmkr.items}
    if jkxd__wcng == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, msf__lnmkr.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if jkxd__wcng == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, msf__lnmkr.args[0],
            arg_types, typemap, updated_containers))
    if jkxd__wcng == ('range', 'builtins') and len(msf__lnmkr.args) == 1:
        return range(get_const_value_inner(func_ir, msf__lnmkr.args[0],
            arg_types, typemap, updated_containers))
    if jkxd__wcng == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, jul__yjkud,
            arg_types, typemap, updated_containers) for jul__yjkud in
            msf__lnmkr.args))
    if jkxd__wcng == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, msf__lnmkr.args[0],
            arg_types, typemap, updated_containers))
    if jkxd__wcng == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, msf__lnmkr.args[0],
            arg_types, typemap, updated_containers))
    if jkxd__wcng == ('format', 'builtins'):
        yvfta__fyg = get_const_value_inner(func_ir, msf__lnmkr.args[0],
            arg_types, typemap, updated_containers)
        mib__jwa = get_const_value_inner(func_ir, msf__lnmkr.args[1],
            arg_types, typemap, updated_containers) if len(msf__lnmkr.args
            ) > 1 else ''
        return format(yvfta__fyg, mib__jwa)
    if jkxd__wcng in (('init_binary_str_index',
        'bodo.hiframes.pd_index_ext'), ('init_numeric_index',
        'bodo.hiframes.pd_index_ext'), ('init_categorical_index',
        'bodo.hiframes.pd_index_ext'), ('init_datetime_index',
        'bodo.hiframes.pd_index_ext'), ('init_timedelta_index',
        'bodo.hiframes.pd_index_ext'), ('init_heter_index',
        'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, msf__lnmkr.args[0],
            arg_types, typemap, updated_containers))
    if jkxd__wcng == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, msf__lnmkr.args[0],
            arg_types, typemap, updated_containers))
    if jkxd__wcng == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, msf__lnmkr.args
            [0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, msf__lnmkr.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            msf__lnmkr.args[2], arg_types, typemap, updated_containers))
    if jkxd__wcng == ('len', 'builtins') and typemap and isinstance(typemap
        .get(msf__lnmkr.args[0].name, None), types.BaseTuple):
        return len(typemap[msf__lnmkr.args[0].name])
    if jkxd__wcng == ('len', 'builtins'):
        gzq__mlho = guard(get_definition, func_ir, msf__lnmkr.args[0])
        if isinstance(gzq__mlho, ir.Expr) and gzq__mlho.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(gzq__mlho.items)
        return len(get_const_value_inner(func_ir, msf__lnmkr.args[0],
            arg_types, typemap, updated_containers))
    if jkxd__wcng == ('CategoricalDtype', 'pandas'):
        kws = dict(msf__lnmkr.kws)
        vqlpi__ytta = get_call_expr_arg('CategoricalDtype', msf__lnmkr.args,
            kws, 0, 'categories', '')
        arvtx__pdx = get_call_expr_arg('CategoricalDtype', msf__lnmkr.args,
            kws, 1, 'ordered', False)
        if arvtx__pdx is not False:
            arvtx__pdx = get_const_value_inner(func_ir, arvtx__pdx,
                arg_types, typemap, updated_containers)
        if vqlpi__ytta == '':
            vqlpi__ytta = None
        else:
            vqlpi__ytta = get_const_value_inner(func_ir, vqlpi__ytta,
                arg_types, typemap, updated_containers)
        return pd.CategoricalDtype(vqlpi__ytta, arvtx__pdx)
    if jkxd__wcng == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, msf__lnmkr.args[0],
            arg_types, typemap, updated_containers))
    if jkxd__wcng is not None and len(jkxd__wcng) == 2 and jkxd__wcng[1
        ] == 'pandas' and jkxd__wcng[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, jkxd__wcng[0])()
    if jkxd__wcng is not None and len(jkxd__wcng) == 2 and isinstance(
        jkxd__wcng[1], ir.Var):
        grwc__iks = get_const_value_inner(func_ir, jkxd__wcng[1], arg_types,
            typemap, updated_containers)
        args = [get_const_value_inner(func_ir, jul__yjkud, arg_types,
            typemap, updated_containers) for jul__yjkud in msf__lnmkr.args]
        kws = {iwb__jlxh[0]: get_const_value_inner(func_ir, iwb__jlxh[1],
            arg_types, typemap, updated_containers) for iwb__jlxh in
            msf__lnmkr.kws}
        return getattr(grwc__iks, jkxd__wcng[0])(*args, **kws)
    if jkxd__wcng is not None and len(jkxd__wcng) == 2 and jkxd__wcng[1
        ] == 'bodo' and jkxd__wcng[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, jul__yjkud, arg_types,
            typemap, updated_containers) for jul__yjkud in msf__lnmkr.args)
        kwargs = {vnkql__jiqt: get_const_value_inner(func_ir, jul__yjkud,
            arg_types, typemap, updated_containers) for vnkql__jiqt,
            jul__yjkud in dict(msf__lnmkr.kws).items()}
        return getattr(bodo, jkxd__wcng[0])(*args, **kwargs)
    if is_call(msf__lnmkr) and typemap and isinstance(typemap.get(
        msf__lnmkr.func.name, None), types.Dispatcher):
        py_func = typemap[msf__lnmkr.func.name].dispatcher.py_func
        require(msf__lnmkr.vararg is None)
        args = tuple(get_const_value_inner(func_ir, jul__yjkud, arg_types,
            typemap, updated_containers) for jul__yjkud in msf__lnmkr.args)
        kwargs = {vnkql__jiqt: get_const_value_inner(func_ir, jul__yjkud,
            arg_types, typemap, updated_containers) for vnkql__jiqt,
            jul__yjkud in dict(msf__lnmkr.kws).items()}
        arg_types = tuple(bodo.typeof(jul__yjkud) for jul__yjkud in args)
        kw_types = {klsv__lhapt: bodo.typeof(jul__yjkud) for klsv__lhapt,
            jul__yjkud in kwargs.items()}
        require(_func_is_pure(py_func, arg_types, kw_types))
        return py_func(*args, **kwargs)
    raise GuardException('Constant value not found')


def _func_is_pure(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.ir.csv_ext import CsvReader
    from bodo.ir.json_ext import JsonReader
    from bodo.ir.parquet_ext import ParquetReader
    from bodo.ir.sql_ext import SqlReader
    f_ir, typemap, zmvo__jaen, zmvo__jaen = bodo.compiler.get_func_type_info(
        py_func, arg_types, kw_types)
    for block in f_ir.blocks.values():
        for stmt in block.body:
            if isinstance(stmt, ir.Print):
                return False
            if isinstance(stmt, (CsvReader, JsonReader, ParquetReader,
                SqlReader)):
                return False
            if is_setitem(stmt) and isinstance(guard(get_definition, f_ir,
                stmt.target), ir.Arg):
                return False
            if is_assign(stmt):
                rhs = stmt.value
                if isinstance(rhs, ir.Yield):
                    return False
                if is_call(rhs):
                    nscn__fwvkd = guard(get_definition, f_ir, rhs.func)
                    if isinstance(nscn__fwvkd, ir.Const) and isinstance(
                        nscn__fwvkd.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    uil__wjhr = guard(find_callname, f_ir, rhs)
                    if uil__wjhr is None:
                        return False
                    func_name, uftu__jxx = uil__wjhr
                    if uftu__jxx == 'pandas' and func_name.startswith('read_'):
                        return False
                    if uil__wjhr in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if uil__wjhr == ('File', 'h5py'):
                        return False
                    if isinstance(uftu__jxx, ir.Var):
                        hgrcu__wkrbx = typemap[uftu__jxx.name]
                        if isinstance(hgrcu__wkrbx, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(hgrcu__wkrbx, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(hgrcu__wkrbx, bodo.LoggingLoggerType):
                            return False
                        if str(hgrcu__wkrbx).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            uftu__jxx), ir.Arg)):
                            return False
                    if uftu__jxx in ('numpy.random', 'time', 'logging',
                        'matplotlib.pyplot'):
                        return False
    return True


def fold_argument_types(pysig, args, kws):

    def normal_handler(index, param, value):
        return value

    def default_handler(index, param, default):
        return types.Omitted(default)

    def stararg_handler(index, param, values):
        return types.StarArgTuple(values)
    args = fold_arguments(pysig, args, kws, normal_handler, default_handler,
        stararg_handler)
    return args


def get_const_func_output_type(func, arg_types, kw_types, typing_context,
    target_context, is_udf=True):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
    py_func = None
    if isinstance(func, types.MakeFunctionLiteral):
        doyq__fjm = func.literal_value.code
        bnrhk__fjitg = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            bnrhk__fjitg = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(bnrhk__fjitg, doyq__fjm)
        fix_struct_return(f_ir)
        typemap, ixuw__xligl, hpw__luc, zmvo__jaen = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, hpw__luc, ixuw__xligl = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, hpw__luc, ixuw__xligl = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, hpw__luc, ixuw__xligl = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(ixuw__xligl, types.DictType):
        dgvg__duld = guard(get_struct_keynames, f_ir, typemap)
        if dgvg__duld is not None:
            ixuw__xligl = StructType((ixuw__xligl.value_type,) * len(
                dgvg__duld), dgvg__duld)
    if is_udf and isinstance(ixuw__xligl, (SeriesType, HeterogeneousSeriesType)
        ):
        wbyf__wsio = numba.core.registry.cpu_target.typing_context
        lxej__smoy = numba.core.registry.cpu_target.target_context
        fcdkv__pyw = bodo.transforms.series_pass.SeriesPass(f_ir,
            wbyf__wsio, lxej__smoy, typemap, hpw__luc, {})
        fcdkv__pyw.run()
        fcdkv__pyw.run()
        fcdkv__pyw.run()
        asy__wroyu = compute_cfg_from_blocks(f_ir.blocks)
        hqlje__nbto = [guard(_get_const_series_info, f_ir.blocks[
            lodaw__qogd], f_ir, typemap) for lodaw__qogd in asy__wroyu.
            exit_points() if isinstance(f_ir.blocks[lodaw__qogd].body[-1],
            ir.Return)]
        if None in hqlje__nbto or len(pd.Series(hqlje__nbto).unique()) != 1:
            ixuw__xligl.const_info = None
        else:
            ixuw__xligl.const_info = hqlje__nbto[0]
    return ixuw__xligl


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    alvmt__mcha = block.body[-1].value
    iia__hjrdr = get_definition(f_ir, alvmt__mcha)
    require(is_expr(iia__hjrdr, 'cast'))
    iia__hjrdr = get_definition(f_ir, iia__hjrdr.value)
    require(is_call(iia__hjrdr) and find_callname(f_ir, iia__hjrdr) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    dge__eht = iia__hjrdr.args[1]
    gxod__ykiq = tuple(get_const_value_inner(f_ir, dge__eht, typemap=typemap))
    if isinstance(typemap[alvmt__mcha.name], HeterogeneousSeriesType):
        return len(typemap[alvmt__mcha.name].data), gxod__ykiq
    vcmkg__ads = iia__hjrdr.args[0]
    hyaps__pdmt = get_definition(f_ir, vcmkg__ads)
    func_name, gwyr__ctidw = find_callname(f_ir, hyaps__pdmt)
    if is_call(hyaps__pdmt) and bodo.utils.utils.is_alloc_callname(func_name,
        gwyr__ctidw):
        axo__tnabn = hyaps__pdmt.args[0]
        huibw__kbkyo = get_const_value_inner(f_ir, axo__tnabn, typemap=typemap)
        return huibw__kbkyo, gxod__ykiq
    if is_call(hyaps__pdmt) and find_callname(f_ir, hyaps__pdmt) in [(
        'asarray', 'numpy'), ('str_arr_from_sequence',
        'bodo.libs.str_arr_ext'), ('build_nullable_tuple',
        'bodo.libs.nullable_tuple_ext')]:
        vcmkg__ads = hyaps__pdmt.args[0]
        hyaps__pdmt = get_definition(f_ir, vcmkg__ads)
    require(is_expr(hyaps__pdmt, 'build_tuple') or is_expr(hyaps__pdmt,
        'build_list'))
    return len(hyaps__pdmt.items), gxod__ykiq


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    iktbz__dgy = []
    qhqf__jljns = []
    values = []
    for klsv__lhapt, jul__yjkud in build_map.items:
        ntip__uaj = find_const(f_ir, klsv__lhapt)
        require(isinstance(ntip__uaj, str))
        qhqf__jljns.append(ntip__uaj)
        iktbz__dgy.append(klsv__lhapt)
        values.append(jul__yjkud)
    ivvkb__deiht = ir.Var(scope, mk_unique_var('val_tup'), loc)
    yipr__kkq = ir.Assign(ir.Expr.build_tuple(values, loc), ivvkb__deiht, loc)
    f_ir._definitions[ivvkb__deiht.name] = [yipr__kkq.value]
    gmawb__yxn = ir.Var(scope, mk_unique_var('key_tup'), loc)
    kruuh__jvdck = ir.Assign(ir.Expr.build_tuple(iktbz__dgy, loc),
        gmawb__yxn, loc)
    f_ir._definitions[gmawb__yxn.name] = [kruuh__jvdck.value]
    if typemap is not None:
        typemap[ivvkb__deiht.name] = types.Tuple([typemap[jul__yjkud.name] for
            jul__yjkud in values])
        typemap[gmawb__yxn.name] = types.Tuple([typemap[jul__yjkud.name] for
            jul__yjkud in iktbz__dgy])
    return qhqf__jljns, ivvkb__deiht, yipr__kkq, gmawb__yxn, kruuh__jvdck


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    dnhhf__qgurf = block.body[-1].value
    inbz__zqwg = guard(get_definition, f_ir, dnhhf__qgurf)
    require(is_expr(inbz__zqwg, 'cast'))
    iia__hjrdr = guard(get_definition, f_ir, inbz__zqwg.value)
    require(is_expr(iia__hjrdr, 'build_map'))
    require(len(iia__hjrdr.items) > 0)
    loc = block.loc
    scope = block.scope
    qhqf__jljns, ivvkb__deiht, yipr__kkq, gmawb__yxn, kruuh__jvdck = (
        extract_keyvals_from_struct_map(f_ir, iia__hjrdr, loc, scope))
    adzf__yys = ir.Var(scope, mk_unique_var('conv_call'), loc)
    mtwx__hsemh = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), adzf__yys, loc)
    f_ir._definitions[adzf__yys.name] = [mtwx__hsemh.value]
    nmd__xviyx = ir.Var(scope, mk_unique_var('struct_val'), loc)
    vizz__fiotz = ir.Assign(ir.Expr.call(adzf__yys, [ivvkb__deiht,
        gmawb__yxn], {}, loc), nmd__xviyx, loc)
    f_ir._definitions[nmd__xviyx.name] = [vizz__fiotz.value]
    inbz__zqwg.value = nmd__xviyx
    iia__hjrdr.items = [(klsv__lhapt, klsv__lhapt) for klsv__lhapt,
        zmvo__jaen in iia__hjrdr.items]
    block.body = block.body[:-2] + [yipr__kkq, kruuh__jvdck, mtwx__hsemh,
        vizz__fiotz] + block.body[-2:]
    return tuple(qhqf__jljns)


def get_struct_keynames(f_ir, typemap):
    asy__wroyu = compute_cfg_from_blocks(f_ir.blocks)
    agnf__dwto = list(asy__wroyu.exit_points())[0]
    block = f_ir.blocks[agnf__dwto]
    require(isinstance(block.body[-1], ir.Return))
    dnhhf__qgurf = block.body[-1].value
    inbz__zqwg = guard(get_definition, f_ir, dnhhf__qgurf)
    require(is_expr(inbz__zqwg, 'cast'))
    iia__hjrdr = guard(get_definition, f_ir, inbz__zqwg.value)
    require(is_call(iia__hjrdr) and find_callname(f_ir, iia__hjrdr) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[iia__hjrdr.args[1].name])


def fix_struct_return(f_ir):
    jrag__paey = None
    asy__wroyu = compute_cfg_from_blocks(f_ir.blocks)
    for agnf__dwto in asy__wroyu.exit_points():
        jrag__paey = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            agnf__dwto], agnf__dwto)
    return jrag__paey


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    yxcin__dofy = ir.Block(ir.Scope(None, loc), loc)
    yxcin__dofy.body = node_list
    build_definitions({(0): yxcin__dofy}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(jul__yjkud) for jul__yjkud in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    jtm__bcok = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(jtm__bcok, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for tyzj__mbgrx in range(len(vals) - 1, -1, -1):
        jul__yjkud = vals[tyzj__mbgrx]
        if isinstance(jul__yjkud, str) and jul__yjkud.startswith(
            NESTED_TUP_SENTINEL):
            fck__gcnb = int(jul__yjkud[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:tyzj__mbgrx]) + (
                tuple(vals[tyzj__mbgrx + 1:tyzj__mbgrx + fck__gcnb + 1]),) +
                tuple(vals[tyzj__mbgrx + fck__gcnb + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    yvfta__fyg = None
    if len(args) > arg_no and arg_no >= 0:
        yvfta__fyg = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        yvfta__fyg = kws[arg_name]
    if yvfta__fyg is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return yvfta__fyg


def set_call_expr_arg(var, args, kws, arg_no, arg_name, add_if_missing=False):
    if len(args) > arg_no:
        args[arg_no] = var
    elif add_if_missing or arg_name in kws:
        kws[arg_name] = var
    else:
        raise BodoError('cannot set call argument since does not exist')


def avoid_udf_inline(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    f_ir = numba.core.compiler.run_frontend(py_func, inline_closures=True)
    if '_bodo_inline' in kw_types and is_overload_constant_bool(kw_types[
        '_bodo_inline']):
        return not get_overload_const_bool(kw_types['_bodo_inline'])
    if any(isinstance(t, DataFrameType) for t in arg_types + tuple(kw_types
        .values())):
        return True
    for block in f_ir.blocks.values():
        if isinstance(block.body[-1], (ir.Raise, ir.StaticRaise)):
            return True
        for stmt in block.body:
            if isinstance(stmt, ir.EnterWith):
                return True
    return False


def replace_func(pass_info, func, args, const=False, pre_nodes=None,
    extra_globals=None, pysig=None, kws=None, inline_bodo_calls=False,
    run_full_pipeline=False):
    ybuvy__zza = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        ybuvy__zza.update(extra_globals)
    func.__globals__.update(ybuvy__zza)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            aik__kyb = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[aik__kyb.name] = types.literal(default)
            except:
                pass_info.typemap[aik__kyb.name] = numba.typeof(default)
            zilwq__pjpfe = ir.Assign(ir.Const(default, loc), aik__kyb, loc)
            pre_nodes.append(zilwq__pjpfe)
            return aik__kyb
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    tqes__xhw = tuple(pass_info.typemap[jul__yjkud.name] for jul__yjkud in args
        )
    if const:
        tgcn__vewcw = []
        for tyzj__mbgrx, yvfta__fyg in enumerate(args):
            grwc__iks = guard(find_const, pass_info.func_ir, yvfta__fyg)
            if grwc__iks:
                tgcn__vewcw.append(types.literal(grwc__iks))
            else:
                tgcn__vewcw.append(tqes__xhw[tyzj__mbgrx])
        tqes__xhw = tuple(tgcn__vewcw)
    return ReplaceFunc(func, tqes__xhw, args, ybuvy__zza, inline_bodo_calls,
        run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(pgsk__pwda) for pgsk__pwda in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        rnl__ukqb = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {rnl__ukqb} = 0\n', (rnl__ukqb,)
    if isinstance(t, ArrayItemArrayType):
        lcs__fzf, gfiu__zjy = gen_init_varsize_alloc_sizes(t.dtype)
        rnl__ukqb = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {rnl__ukqb} = 0\n' + lcs__fzf, (rnl__ukqb,) + gfiu__zjy
    return '', ()


def gen_varsize_item_sizes(t, item, var_names):
    if t == string_array_type:
        return '    {} += bodo.libs.str_arr_ext.get_utf8_size({})\n'.format(
            var_names[0], item)
    if isinstance(t, ArrayItemArrayType):
        return '    {} += len({})\n'.format(var_names[0], item
            ) + gen_varsize_array_counts(t.dtype, item, var_names[1:])
    return ''


def gen_varsize_array_counts(t, item, var_names):
    if t == string_array_type:
        return ('    {} += bodo.libs.str_arr_ext.get_num_total_chars({})\n'
            .format(var_names[0], item))
    return ''


def get_type_alloc_counts(t):
    if isinstance(t, (StructArrayType, TupleArrayType)):
        return 1 + sum(get_type_alloc_counts(pgsk__pwda.dtype) for
            pgsk__pwda in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(pgsk__pwda) for pgsk__pwda in t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(pgsk__pwda) for pgsk__pwda in t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    bsvzw__gcq = typing_context.resolve_getattr(obj_dtype, func_name)
    if bsvzw__gcq is None:
        ixmtb__avals = types.misc.Module(np)
        try:
            bsvzw__gcq = typing_context.resolve_getattr(ixmtb__avals, func_name
                )
        except AttributeError as zwfj__qvy:
            bsvzw__gcq = None
        if bsvzw__gcq is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return bsvzw__gcq


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    bsvzw__gcq = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(bsvzw__gcq, types.BoundFunction):
        if axis is not None:
            bwp__eir = bsvzw__gcq.get_call_type(typing_context, (), {'axis':
                axis})
        else:
            bwp__eir = bsvzw__gcq.get_call_type(typing_context, (), {})
        return bwp__eir.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(bsvzw__gcq):
            bwp__eir = bsvzw__gcq.get_call_type(typing_context, (obj_dtype,
                ), {})
            return bwp__eir.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    bsvzw__gcq = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(bsvzw__gcq, types.BoundFunction):
        vssq__bvxy = bsvzw__gcq.template
        if axis is not None:
            return vssq__bvxy._overload_func(obj_dtype, axis=axis)
        else:
            return vssq__bvxy._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    dlxv__fbxa = get_definition(func_ir, dict_var)
    require(isinstance(dlxv__fbxa, ir.Expr))
    require(dlxv__fbxa.op == 'build_map')
    liu__reks = dlxv__fbxa.items
    iktbz__dgy = []
    values = []
    hbhtw__vmygc = False
    for tyzj__mbgrx in range(len(liu__reks)):
        wwp__wxqy, value = liu__reks[tyzj__mbgrx]
        try:
            mlu__ogdrv = get_const_value_inner(func_ir, wwp__wxqy,
                arg_types, typemap, updated_containers)
            iktbz__dgy.append(mlu__ogdrv)
            values.append(value)
        except GuardException as zwfj__qvy:
            require_const_map[wwp__wxqy] = label
            hbhtw__vmygc = True
    if hbhtw__vmygc:
        raise GuardException
    return iktbz__dgy, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        iktbz__dgy = tuple(get_const_value_inner(func_ir, t[0], args) for t in
            build_map.items)
    except GuardException as zwfj__qvy:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in iktbz__dgy):
        raise BodoError(err_msg, loc)
    return iktbz__dgy


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    iktbz__dgy = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    vksd__nwdo = []
    axs__cos = [bodo.transforms.typing_pass._create_const_var(klsv__lhapt,
        'dict_key', scope, loc, vksd__nwdo) for klsv__lhapt in iktbz__dgy]
    pnfoc__tum = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        lmobt__gbsb = ir.Var(scope, mk_unique_var('sentinel'), loc)
        mfhxb__lxj = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        vksd__nwdo.append(ir.Assign(ir.Const('__bodo_tup', loc),
            lmobt__gbsb, loc))
        uyt__ftcn = [lmobt__gbsb] + axs__cos + pnfoc__tum
        vksd__nwdo.append(ir.Assign(ir.Expr.build_tuple(uyt__ftcn, loc),
            mfhxb__lxj, loc))
        return (mfhxb__lxj,), vksd__nwdo
    else:
        hts__dot = ir.Var(scope, mk_unique_var('values_tup'), loc)
        zqg__nhld = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        vksd__nwdo.append(ir.Assign(ir.Expr.build_tuple(pnfoc__tum, loc),
            hts__dot, loc))
        vksd__nwdo.append(ir.Assign(ir.Expr.build_tuple(axs__cos, loc),
            zqg__nhld, loc))
        return (hts__dot, zqg__nhld), vksd__nwdo
