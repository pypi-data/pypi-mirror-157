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
    aogmk__pzk = tuple(call_list)
    if aogmk__pzk in no_side_effect_call_tuples:
        return True
    if aogmk__pzk == (bodo.hiframes.pd_index_ext.init_range_index,):
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
    if len(aogmk__pzk) == 1 and tuple in getattr(aogmk__pzk[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        jur__lue = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        jur__lue = func.__globals__
    if extra_globals is not None:
        jur__lue.update(extra_globals)
    if add_default_globals:
        jur__lue.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, jur__lue, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[uel__emvr.name] for uel__emvr in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, jur__lue)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        vvzc__rjdv = tuple(typing_info.typemap[uel__emvr.name] for
            uel__emvr in args)
        nitd__hga = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, vvzc__rjdv, {}, {}, flags)
        nitd__hga.run()
    nhjzj__pca = f_ir.blocks.popitem()[1]
    replace_arg_nodes(nhjzj__pca, args)
    ahb__ccrf = nhjzj__pca.body[:-2]
    update_locs(ahb__ccrf[len(args):], loc)
    for stmt in ahb__ccrf[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        tclxf__rffj = nhjzj__pca.body[-2]
        assert is_assign(tclxf__rffj) and is_expr(tclxf__rffj.value, 'cast')
        prxs__qho = tclxf__rffj.value.value
        ahb__ccrf.append(ir.Assign(prxs__qho, ret_var, loc))
    return ahb__ccrf


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for ozdg__dlgc in stmt.list_vars():
            ozdg__dlgc.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        vyt__wpnb = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        ejtow__whifr, rzi__qjuhj = vyt__wpnb(stmt)
        return rzi__qjuhj
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        oavia__dah = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(oavia__dah, ir.UndefinedType):
            bpqhu__mhedr = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{bpqhu__mhedr}' is not defined", loc=loc)
    except GuardException as zyy__wqoa:
        raise BodoError(err_msg, loc=loc)
    return oavia__dah


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    ilyz__lkhsu = get_definition(func_ir, var)
    hbuwb__ixt = None
    if typemap is not None:
        hbuwb__ixt = typemap.get(var.name, None)
    if isinstance(ilyz__lkhsu, ir.Arg) and arg_types is not None:
        hbuwb__ixt = arg_types[ilyz__lkhsu.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(hbuwb__ixt):
        return get_literal_value(hbuwb__ixt)
    if isinstance(ilyz__lkhsu, (ir.Const, ir.Global, ir.FreeVar)):
        oavia__dah = ilyz__lkhsu.value
        return oavia__dah
    if literalize_args and isinstance(ilyz__lkhsu, ir.Arg
        ) and can_literalize_type(hbuwb__ixt, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({ilyz__lkhsu.index}, loc=
            var.loc, file_infos={ilyz__lkhsu.index: file_info} if file_info
             is not None else None)
    if is_expr(ilyz__lkhsu, 'binop'):
        if file_info and ilyz__lkhsu.fn == operator.add:
            try:
                xbws__itkue = get_const_value_inner(func_ir, ilyz__lkhsu.
                    lhs, arg_types, typemap, updated_containers,
                    literalize_args=False)
                file_info.set_concat(xbws__itkue, True)
                vpa__hrr = get_const_value_inner(func_ir, ilyz__lkhsu.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return ilyz__lkhsu.fn(xbws__itkue, vpa__hrr)
            except (GuardException, BodoConstUpdatedError) as zyy__wqoa:
                pass
            try:
                vpa__hrr = get_const_value_inner(func_ir, ilyz__lkhsu.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(vpa__hrr, False)
                xbws__itkue = get_const_value_inner(func_ir, ilyz__lkhsu.
                    lhs, arg_types, typemap, updated_containers, file_info)
                return ilyz__lkhsu.fn(xbws__itkue, vpa__hrr)
            except (GuardException, BodoConstUpdatedError) as zyy__wqoa:
                pass
        xbws__itkue = get_const_value_inner(func_ir, ilyz__lkhsu.lhs,
            arg_types, typemap, updated_containers)
        vpa__hrr = get_const_value_inner(func_ir, ilyz__lkhsu.rhs,
            arg_types, typemap, updated_containers)
        return ilyz__lkhsu.fn(xbws__itkue, vpa__hrr)
    if is_expr(ilyz__lkhsu, 'unary'):
        oavia__dah = get_const_value_inner(func_ir, ilyz__lkhsu.value,
            arg_types, typemap, updated_containers)
        return ilyz__lkhsu.fn(oavia__dah)
    if is_expr(ilyz__lkhsu, 'getattr') and typemap:
        lrc__rvv = typemap.get(ilyz__lkhsu.value.name, None)
        if isinstance(lrc__rvv, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and ilyz__lkhsu.attr == 'columns':
            return pd.Index(lrc__rvv.columns)
        if isinstance(lrc__rvv, types.SliceType):
            lifs__fqsvg = get_definition(func_ir, ilyz__lkhsu.value)
            require(is_call(lifs__fqsvg))
            oon__osga = find_callname(func_ir, lifs__fqsvg)
            ssuf__dpswo = False
            if oon__osga == ('_normalize_slice', 'numba.cpython.unicode'):
                require(ilyz__lkhsu.attr in ('start', 'step'))
                lifs__fqsvg = get_definition(func_ir, lifs__fqsvg.args[0])
                ssuf__dpswo = True
            require(find_callname(func_ir, lifs__fqsvg) == ('slice',
                'builtins'))
            if len(lifs__fqsvg.args) == 1:
                if ilyz__lkhsu.attr == 'start':
                    return 0
                if ilyz__lkhsu.attr == 'step':
                    return 1
                require(ilyz__lkhsu.attr == 'stop')
                return get_const_value_inner(func_ir, lifs__fqsvg.args[0],
                    arg_types, typemap, updated_containers)
            if ilyz__lkhsu.attr == 'start':
                oavia__dah = get_const_value_inner(func_ir, lifs__fqsvg.
                    args[0], arg_types, typemap, updated_containers)
                if oavia__dah is None:
                    oavia__dah = 0
                if ssuf__dpswo:
                    require(oavia__dah == 0)
                return oavia__dah
            if ilyz__lkhsu.attr == 'stop':
                assert not ssuf__dpswo
                return get_const_value_inner(func_ir, lifs__fqsvg.args[1],
                    arg_types, typemap, updated_containers)
            require(ilyz__lkhsu.attr == 'step')
            if len(lifs__fqsvg.args) == 2:
                return 1
            else:
                oavia__dah = get_const_value_inner(func_ir, lifs__fqsvg.
                    args[2], arg_types, typemap, updated_containers)
                if oavia__dah is None:
                    oavia__dah = 1
                if ssuf__dpswo:
                    require(oavia__dah == 1)
                return oavia__dah
    if is_expr(ilyz__lkhsu, 'getattr'):
        return getattr(get_const_value_inner(func_ir, ilyz__lkhsu.value,
            arg_types, typemap, updated_containers), ilyz__lkhsu.attr)
    if is_expr(ilyz__lkhsu, 'getitem'):
        value = get_const_value_inner(func_ir, ilyz__lkhsu.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, ilyz__lkhsu.index, arg_types,
            typemap, updated_containers)
        return value[index]
    swr__xki = guard(find_callname, func_ir, ilyz__lkhsu, typemap)
    if swr__xki is not None and len(swr__xki) == 2 and swr__xki[0
        ] == 'keys' and isinstance(swr__xki[1], ir.Var):
        typ__mvahg = ilyz__lkhsu.func
        ilyz__lkhsu = get_definition(func_ir, swr__xki[1])
        glb__ryov = swr__xki[1].name
        if updated_containers and glb__ryov in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                glb__ryov, updated_containers[glb__ryov]))
        require(is_expr(ilyz__lkhsu, 'build_map'))
        vals = [ozdg__dlgc[0] for ozdg__dlgc in ilyz__lkhsu.items]
        mtx__aated = guard(get_definition, func_ir, typ__mvahg)
        assert isinstance(mtx__aated, ir.Expr) and mtx__aated.attr == 'keys'
        mtx__aated.attr = 'copy'
        return [get_const_value_inner(func_ir, ozdg__dlgc, arg_types,
            typemap, updated_containers) for ozdg__dlgc in vals]
    if is_expr(ilyz__lkhsu, 'build_map'):
        return {get_const_value_inner(func_ir, ozdg__dlgc[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            ozdg__dlgc[1], arg_types, typemap, updated_containers) for
            ozdg__dlgc in ilyz__lkhsu.items}
    if is_expr(ilyz__lkhsu, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, ozdg__dlgc, arg_types,
            typemap, updated_containers) for ozdg__dlgc in ilyz__lkhsu.items)
    if is_expr(ilyz__lkhsu, 'build_list'):
        return [get_const_value_inner(func_ir, ozdg__dlgc, arg_types,
            typemap, updated_containers) for ozdg__dlgc in ilyz__lkhsu.items]
    if is_expr(ilyz__lkhsu, 'build_set'):
        return {get_const_value_inner(func_ir, ozdg__dlgc, arg_types,
            typemap, updated_containers) for ozdg__dlgc in ilyz__lkhsu.items}
    if swr__xki == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, ilyz__lkhsu.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if swr__xki == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, ilyz__lkhsu.args[0],
            arg_types, typemap, updated_containers))
    if swr__xki == ('range', 'builtins') and len(ilyz__lkhsu.args) == 1:
        return range(get_const_value_inner(func_ir, ilyz__lkhsu.args[0],
            arg_types, typemap, updated_containers))
    if swr__xki == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, ozdg__dlgc,
            arg_types, typemap, updated_containers) for ozdg__dlgc in
            ilyz__lkhsu.args))
    if swr__xki == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, ilyz__lkhsu.args[0],
            arg_types, typemap, updated_containers))
    if swr__xki == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, ilyz__lkhsu.args[0],
            arg_types, typemap, updated_containers))
    if swr__xki == ('format', 'builtins'):
        uel__emvr = get_const_value_inner(func_ir, ilyz__lkhsu.args[0],
            arg_types, typemap, updated_containers)
        vcq__hgon = get_const_value_inner(func_ir, ilyz__lkhsu.args[1],
            arg_types, typemap, updated_containers) if len(ilyz__lkhsu.args
            ) > 1 else ''
        return format(uel__emvr, vcq__hgon)
    if swr__xki in (('init_binary_str_index', 'bodo.hiframes.pd_index_ext'),
        ('init_numeric_index', 'bodo.hiframes.pd_index_ext'), (
        'init_categorical_index', 'bodo.hiframes.pd_index_ext'), (
        'init_datetime_index', 'bodo.hiframes.pd_index_ext'), (
        'init_timedelta_index', 'bodo.hiframes.pd_index_ext'), (
        'init_heter_index', 'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, ilyz__lkhsu.args[0],
            arg_types, typemap, updated_containers))
    if swr__xki == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, ilyz__lkhsu.args[0],
            arg_types, typemap, updated_containers))
    if swr__xki == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, ilyz__lkhsu.
            args[0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, ilyz__lkhsu.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            ilyz__lkhsu.args[2], arg_types, typemap, updated_containers))
    if swr__xki == ('len', 'builtins') and typemap and isinstance(typemap.
        get(ilyz__lkhsu.args[0].name, None), types.BaseTuple):
        return len(typemap[ilyz__lkhsu.args[0].name])
    if swr__xki == ('len', 'builtins'):
        laxrt__jzj = guard(get_definition, func_ir, ilyz__lkhsu.args[0])
        if isinstance(laxrt__jzj, ir.Expr) and laxrt__jzj.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(laxrt__jzj.items)
        return len(get_const_value_inner(func_ir, ilyz__lkhsu.args[0],
            arg_types, typemap, updated_containers))
    if swr__xki == ('CategoricalDtype', 'pandas'):
        kws = dict(ilyz__lkhsu.kws)
        vmy__ezn = get_call_expr_arg('CategoricalDtype', ilyz__lkhsu.args,
            kws, 0, 'categories', '')
        nqdy__auvi = get_call_expr_arg('CategoricalDtype', ilyz__lkhsu.args,
            kws, 1, 'ordered', False)
        if nqdy__auvi is not False:
            nqdy__auvi = get_const_value_inner(func_ir, nqdy__auvi,
                arg_types, typemap, updated_containers)
        if vmy__ezn == '':
            vmy__ezn = None
        else:
            vmy__ezn = get_const_value_inner(func_ir, vmy__ezn, arg_types,
                typemap, updated_containers)
        return pd.CategoricalDtype(vmy__ezn, nqdy__auvi)
    if swr__xki == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, ilyz__lkhsu.args[0],
            arg_types, typemap, updated_containers))
    if swr__xki is not None and len(swr__xki) == 2 and swr__xki[1
        ] == 'pandas' and swr__xki[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, swr__xki[0])()
    if swr__xki is not None and len(swr__xki) == 2 and isinstance(swr__xki[
        1], ir.Var):
        oavia__dah = get_const_value_inner(func_ir, swr__xki[1], arg_types,
            typemap, updated_containers)
        args = [get_const_value_inner(func_ir, ozdg__dlgc, arg_types,
            typemap, updated_containers) for ozdg__dlgc in ilyz__lkhsu.args]
        kws = {fyqj__kih[0]: get_const_value_inner(func_ir, fyqj__kih[1],
            arg_types, typemap, updated_containers) for fyqj__kih in
            ilyz__lkhsu.kws}
        return getattr(oavia__dah, swr__xki[0])(*args, **kws)
    if swr__xki is not None and len(swr__xki) == 2 and swr__xki[1
        ] == 'bodo' and swr__xki[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, ozdg__dlgc, arg_types,
            typemap, updated_containers) for ozdg__dlgc in ilyz__lkhsu.args)
        kwargs = {bpqhu__mhedr: get_const_value_inner(func_ir, ozdg__dlgc,
            arg_types, typemap, updated_containers) for bpqhu__mhedr,
            ozdg__dlgc in dict(ilyz__lkhsu.kws).items()}
        return getattr(bodo, swr__xki[0])(*args, **kwargs)
    if is_call(ilyz__lkhsu) and typemap and isinstance(typemap.get(
        ilyz__lkhsu.func.name, None), types.Dispatcher):
        py_func = typemap[ilyz__lkhsu.func.name].dispatcher.py_func
        require(ilyz__lkhsu.vararg is None)
        args = tuple(get_const_value_inner(func_ir, ozdg__dlgc, arg_types,
            typemap, updated_containers) for ozdg__dlgc in ilyz__lkhsu.args)
        kwargs = {bpqhu__mhedr: get_const_value_inner(func_ir, ozdg__dlgc,
            arg_types, typemap, updated_containers) for bpqhu__mhedr,
            ozdg__dlgc in dict(ilyz__lkhsu.kws).items()}
        arg_types = tuple(bodo.typeof(ozdg__dlgc) for ozdg__dlgc in args)
        kw_types = {amp__inw: bodo.typeof(ozdg__dlgc) for amp__inw,
            ozdg__dlgc in kwargs.items()}
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
    f_ir, typemap, axjnd__yqlqb, axjnd__yqlqb = (bodo.compiler.
        get_func_type_info(py_func, arg_types, kw_types))
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
                    sqx__ahk = guard(get_definition, f_ir, rhs.func)
                    if isinstance(sqx__ahk, ir.Const) and isinstance(sqx__ahk
                        .value, numba.core.dispatcher.ObjModeLiftedWith):
                        return False
                    nwa__gevlc = guard(find_callname, f_ir, rhs)
                    if nwa__gevlc is None:
                        return False
                    func_name, blg__cptk = nwa__gevlc
                    if blg__cptk == 'pandas' and func_name.startswith('read_'):
                        return False
                    if nwa__gevlc in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if nwa__gevlc == ('File', 'h5py'):
                        return False
                    if isinstance(blg__cptk, ir.Var):
                        hbuwb__ixt = typemap[blg__cptk.name]
                        if isinstance(hbuwb__ixt, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(hbuwb__ixt, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(hbuwb__ixt, bodo.LoggingLoggerType):
                            return False
                        if str(hbuwb__ixt).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            blg__cptk), ir.Arg)):
                            return False
                    if blg__cptk in ('numpy.random', 'time', 'logging',
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
        pqlsz__vvul = func.literal_value.code
        uuzd__txs = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            uuzd__txs = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(uuzd__txs, pqlsz__vvul)
        fix_struct_return(f_ir)
        typemap, wxjt__imo, pxww__hynsm, axjnd__yqlqb = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, pxww__hynsm, wxjt__imo = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, pxww__hynsm, wxjt__imo = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, pxww__hynsm, wxjt__imo = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(wxjt__imo, types.DictType):
        qxd__axro = guard(get_struct_keynames, f_ir, typemap)
        if qxd__axro is not None:
            wxjt__imo = StructType((wxjt__imo.value_type,) * len(qxd__axro),
                qxd__axro)
    if is_udf and isinstance(wxjt__imo, (SeriesType, HeterogeneousSeriesType)):
        uahp__ixt = numba.core.registry.cpu_target.typing_context
        hboyk__wrd = numba.core.registry.cpu_target.target_context
        oaq__xuj = bodo.transforms.series_pass.SeriesPass(f_ir, uahp__ixt,
            hboyk__wrd, typemap, pxww__hynsm, {})
        oaq__xuj.run()
        oaq__xuj.run()
        oaq__xuj.run()
        npql__vfaw = compute_cfg_from_blocks(f_ir.blocks)
        wbrh__kqv = [guard(_get_const_series_info, f_ir.blocks[svn__qghu],
            f_ir, typemap) for svn__qghu in npql__vfaw.exit_points() if
            isinstance(f_ir.blocks[svn__qghu].body[-1], ir.Return)]
        if None in wbrh__kqv or len(pd.Series(wbrh__kqv).unique()) != 1:
            wxjt__imo.const_info = None
        else:
            wxjt__imo.const_info = wbrh__kqv[0]
    return wxjt__imo


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    nzg__vcm = block.body[-1].value
    menj__dvkup = get_definition(f_ir, nzg__vcm)
    require(is_expr(menj__dvkup, 'cast'))
    menj__dvkup = get_definition(f_ir, menj__dvkup.value)
    require(is_call(menj__dvkup) and find_callname(f_ir, menj__dvkup) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    luwmg__pzpdw = menj__dvkup.args[1]
    wwtlk__bhzy = tuple(get_const_value_inner(f_ir, luwmg__pzpdw, typemap=
        typemap))
    if isinstance(typemap[nzg__vcm.name], HeterogeneousSeriesType):
        return len(typemap[nzg__vcm.name].data), wwtlk__bhzy
    zrh__nsmth = menj__dvkup.args[0]
    hywta__mrio = get_definition(f_ir, zrh__nsmth)
    func_name, krwpl__cxnog = find_callname(f_ir, hywta__mrio)
    if is_call(hywta__mrio) and bodo.utils.utils.is_alloc_callname(func_name,
        krwpl__cxnog):
        ilvl__opeks = hywta__mrio.args[0]
        jrfxx__ncm = get_const_value_inner(f_ir, ilvl__opeks, typemap=typemap)
        return jrfxx__ncm, wwtlk__bhzy
    if is_call(hywta__mrio) and find_callname(f_ir, hywta__mrio) in [(
        'asarray', 'numpy'), ('str_arr_from_sequence',
        'bodo.libs.str_arr_ext'), ('build_nullable_tuple',
        'bodo.libs.nullable_tuple_ext')]:
        zrh__nsmth = hywta__mrio.args[0]
        hywta__mrio = get_definition(f_ir, zrh__nsmth)
    require(is_expr(hywta__mrio, 'build_tuple') or is_expr(hywta__mrio,
        'build_list'))
    return len(hywta__mrio.items), wwtlk__bhzy


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    dkbe__qrs = []
    cck__iol = []
    values = []
    for amp__inw, ozdg__dlgc in build_map.items:
        ewe__vli = find_const(f_ir, amp__inw)
        require(isinstance(ewe__vli, str))
        cck__iol.append(ewe__vli)
        dkbe__qrs.append(amp__inw)
        values.append(ozdg__dlgc)
    xbn__cukzx = ir.Var(scope, mk_unique_var('val_tup'), loc)
    lucl__aln = ir.Assign(ir.Expr.build_tuple(values, loc), xbn__cukzx, loc)
    f_ir._definitions[xbn__cukzx.name] = [lucl__aln.value]
    slr__brw = ir.Var(scope, mk_unique_var('key_tup'), loc)
    hiyf__avgh = ir.Assign(ir.Expr.build_tuple(dkbe__qrs, loc), slr__brw, loc)
    f_ir._definitions[slr__brw.name] = [hiyf__avgh.value]
    if typemap is not None:
        typemap[xbn__cukzx.name] = types.Tuple([typemap[ozdg__dlgc.name] for
            ozdg__dlgc in values])
        typemap[slr__brw.name] = types.Tuple([typemap[ozdg__dlgc.name] for
            ozdg__dlgc in dkbe__qrs])
    return cck__iol, xbn__cukzx, lucl__aln, slr__brw, hiyf__avgh


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    gzsjg__lqez = block.body[-1].value
    qxp__vhk = guard(get_definition, f_ir, gzsjg__lqez)
    require(is_expr(qxp__vhk, 'cast'))
    menj__dvkup = guard(get_definition, f_ir, qxp__vhk.value)
    require(is_expr(menj__dvkup, 'build_map'))
    require(len(menj__dvkup.items) > 0)
    loc = block.loc
    scope = block.scope
    cck__iol, xbn__cukzx, lucl__aln, slr__brw, hiyf__avgh = (
        extract_keyvals_from_struct_map(f_ir, menj__dvkup, loc, scope))
    nnfgs__gqx = ir.Var(scope, mk_unique_var('conv_call'), loc)
    nqqab__loq = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), nnfgs__gqx, loc)
    f_ir._definitions[nnfgs__gqx.name] = [nqqab__loq.value]
    qvffz__jjrvw = ir.Var(scope, mk_unique_var('struct_val'), loc)
    qbx__txm = ir.Assign(ir.Expr.call(nnfgs__gqx, [xbn__cukzx, slr__brw], {
        }, loc), qvffz__jjrvw, loc)
    f_ir._definitions[qvffz__jjrvw.name] = [qbx__txm.value]
    qxp__vhk.value = qvffz__jjrvw
    menj__dvkup.items = [(amp__inw, amp__inw) for amp__inw, axjnd__yqlqb in
        menj__dvkup.items]
    block.body = block.body[:-2] + [lucl__aln, hiyf__avgh, nqqab__loq, qbx__txm
        ] + block.body[-2:]
    return tuple(cck__iol)


def get_struct_keynames(f_ir, typemap):
    npql__vfaw = compute_cfg_from_blocks(f_ir.blocks)
    bpfe__ggm = list(npql__vfaw.exit_points())[0]
    block = f_ir.blocks[bpfe__ggm]
    require(isinstance(block.body[-1], ir.Return))
    gzsjg__lqez = block.body[-1].value
    qxp__vhk = guard(get_definition, f_ir, gzsjg__lqez)
    require(is_expr(qxp__vhk, 'cast'))
    menj__dvkup = guard(get_definition, f_ir, qxp__vhk.value)
    require(is_call(menj__dvkup) and find_callname(f_ir, menj__dvkup) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[menj__dvkup.args[1].name])


def fix_struct_return(f_ir):
    gngsr__wpn = None
    npql__vfaw = compute_cfg_from_blocks(f_ir.blocks)
    for bpfe__ggm in npql__vfaw.exit_points():
        gngsr__wpn = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            bpfe__ggm], bpfe__ggm)
    return gngsr__wpn


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    cdtfo__dzna = ir.Block(ir.Scope(None, loc), loc)
    cdtfo__dzna.body = node_list
    build_definitions({(0): cdtfo__dzna}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(ozdg__dlgc) for ozdg__dlgc in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    jgw__bunym = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(jgw__bunym, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for yli__izefw in range(len(vals) - 1, -1, -1):
        ozdg__dlgc = vals[yli__izefw]
        if isinstance(ozdg__dlgc, str) and ozdg__dlgc.startswith(
            NESTED_TUP_SENTINEL):
            kdryb__vjdr = int(ozdg__dlgc[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:yli__izefw]) + (
                tuple(vals[yli__izefw + 1:yli__izefw + kdryb__vjdr + 1]),) +
                tuple(vals[yli__izefw + kdryb__vjdr + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    uel__emvr = None
    if len(args) > arg_no and arg_no >= 0:
        uel__emvr = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        uel__emvr = kws[arg_name]
    if uel__emvr is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return uel__emvr


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
    jur__lue = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        jur__lue.update(extra_globals)
    func.__globals__.update(jur__lue)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            jykh__xqjyy = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[jykh__xqjyy.name] = types.literal(default)
            except:
                pass_info.typemap[jykh__xqjyy.name] = numba.typeof(default)
            jyks__svn = ir.Assign(ir.Const(default, loc), jykh__xqjyy, loc)
            pre_nodes.append(jyks__svn)
            return jykh__xqjyy
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    vvzc__rjdv = tuple(pass_info.typemap[ozdg__dlgc.name] for ozdg__dlgc in
        args)
    if const:
        avgk__pdgt = []
        for yli__izefw, uel__emvr in enumerate(args):
            oavia__dah = guard(find_const, pass_info.func_ir, uel__emvr)
            if oavia__dah:
                avgk__pdgt.append(types.literal(oavia__dah))
            else:
                avgk__pdgt.append(vvzc__rjdv[yli__izefw])
        vvzc__rjdv = tuple(avgk__pdgt)
    return ReplaceFunc(func, vvzc__rjdv, args, jur__lue, inline_bodo_calls,
        run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(wyi__xwfi) for wyi__xwfi in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        yvwzu__cwr = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {yvwzu__cwr} = 0\n', (yvwzu__cwr,)
    if isinstance(t, ArrayItemArrayType):
        unfeu__sll, lwgbb__xmwwf = gen_init_varsize_alloc_sizes(t.dtype)
        yvwzu__cwr = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {yvwzu__cwr} = 0\n' + unfeu__sll, (yvwzu__cwr,
            ) + lwgbb__xmwwf
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
        return 1 + sum(get_type_alloc_counts(wyi__xwfi.dtype) for wyi__xwfi in
            t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(wyi__xwfi) for wyi__xwfi in t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(wyi__xwfi) for wyi__xwfi in t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    eay__mezm = typing_context.resolve_getattr(obj_dtype, func_name)
    if eay__mezm is None:
        ugm__ftqa = types.misc.Module(np)
        try:
            eay__mezm = typing_context.resolve_getattr(ugm__ftqa, func_name)
        except AttributeError as zyy__wqoa:
            eay__mezm = None
        if eay__mezm is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return eay__mezm


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    eay__mezm = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(eay__mezm, types.BoundFunction):
        if axis is not None:
            vtjwg__blp = eay__mezm.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            vtjwg__blp = eay__mezm.get_call_type(typing_context, (), {})
        return vtjwg__blp.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(eay__mezm):
            vtjwg__blp = eay__mezm.get_call_type(typing_context, (obj_dtype
                ,), {})
            return vtjwg__blp.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    eay__mezm = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(eay__mezm, types.BoundFunction):
        iuos__dgmyj = eay__mezm.template
        if axis is not None:
            return iuos__dgmyj._overload_func(obj_dtype, axis=axis)
        else:
            return iuos__dgmyj._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    oby__ssqp = get_definition(func_ir, dict_var)
    require(isinstance(oby__ssqp, ir.Expr))
    require(oby__ssqp.op == 'build_map')
    ytfc__pqy = oby__ssqp.items
    dkbe__qrs = []
    values = []
    qdaqm__nrny = False
    for yli__izefw in range(len(ytfc__pqy)):
        ieg__oojmz, value = ytfc__pqy[yli__izefw]
        try:
            kdmc__qewr = get_const_value_inner(func_ir, ieg__oojmz,
                arg_types, typemap, updated_containers)
            dkbe__qrs.append(kdmc__qewr)
            values.append(value)
        except GuardException as zyy__wqoa:
            require_const_map[ieg__oojmz] = label
            qdaqm__nrny = True
    if qdaqm__nrny:
        raise GuardException
    return dkbe__qrs, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        dkbe__qrs = tuple(get_const_value_inner(func_ir, t[0], args) for t in
            build_map.items)
    except GuardException as zyy__wqoa:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in dkbe__qrs):
        raise BodoError(err_msg, loc)
    return dkbe__qrs


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    dkbe__qrs = _get_const_keys_from_dict(args, func_ir, build_map, err_msg,
        loc)
    gtih__uzsxa = []
    yepcm__pwdn = [bodo.transforms.typing_pass._create_const_var(amp__inw,
        'dict_key', scope, loc, gtih__uzsxa) for amp__inw in dkbe__qrs]
    ecnj__phr = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        vhmx__ysoo = ir.Var(scope, mk_unique_var('sentinel'), loc)
        fae__rojm = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        gtih__uzsxa.append(ir.Assign(ir.Const('__bodo_tup', loc),
            vhmx__ysoo, loc))
        cyv__ypq = [vhmx__ysoo] + yepcm__pwdn + ecnj__phr
        gtih__uzsxa.append(ir.Assign(ir.Expr.build_tuple(cyv__ypq, loc),
            fae__rojm, loc))
        return (fae__rojm,), gtih__uzsxa
    else:
        lygjg__axq = ir.Var(scope, mk_unique_var('values_tup'), loc)
        bcbna__tezjj = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        gtih__uzsxa.append(ir.Assign(ir.Expr.build_tuple(ecnj__phr, loc),
            lygjg__axq, loc))
        gtih__uzsxa.append(ir.Assign(ir.Expr.build_tuple(yepcm__pwdn, loc),
            bcbna__tezjj, loc))
        return (lygjg__axq, bcbna__tezjj), gtih__uzsxa
