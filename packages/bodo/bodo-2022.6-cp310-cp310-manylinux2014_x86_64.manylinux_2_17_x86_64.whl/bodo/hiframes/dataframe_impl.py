"""
Implementation of DataFrame attributes and methods using overload.
"""
import operator
import re
import warnings
from collections import namedtuple
from typing import Tuple
import numba
import numpy as np
import pandas as pd
from numba.core import cgutils, ir, types
from numba.core.imputils import RefType, impl_ret_borrowed, impl_ret_new_ref, iternext_impl, lower_builtin
from numba.core.ir_utils import mk_unique_var, next_label
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_getattr, models, overload, overload_attribute, overload_method, register_model, type_callable
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import _no_input, datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported, handle_inplace_df_type_change
from bodo.hiframes.pd_index_ext import DatetimeIndexType, RangeIndexType, StringIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType, if_series_to_array_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array, boolean_dtype
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.dict_arr_ext import dict_str_arr_type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils.transform import bodo_types_with_params, gen_const_tup, no_side_effect_call_tuples
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, check_unsupported_args, dtype_to_array_type, ensure_constant_arg, ensure_constant_values, get_index_data_arr_types, get_index_names, get_literal_value, get_nullable_and_non_nullable_types, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_tuple, get_overload_constant_dict, get_overload_constant_series, is_common_scalar_dtype, is_literal_type, is_overload_bool, is_overload_bool_list, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_int, is_overload_constant_list, is_overload_constant_series, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, is_scalar_type, parse_dtype, raise_bodo_error, unliteral_val
from bodo.utils.utils import is_array_typ


@overload_attribute(DataFrameType, 'index', inline='always')
def overload_dataframe_index(df):
    return lambda df: bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)


def generate_col_to_index_func_text(col_names: Tuple):
    if all(isinstance(a, str) for a in col_names) or all(isinstance(a,
        bytes) for a in col_names):
        lkrfr__bbl = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({lkrfr__bbl})\n'
            )
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    ccv__mvv = 'def impl(df):\n'
    if df.has_runtime_cols:
        ccv__mvv += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        tgdu__qhtu = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        ccv__mvv += f'  return {tgdu__qhtu}'
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo}, sczhi__csetf)
    impl = sczhi__csetf['impl']
    return impl


@overload_attribute(DataFrameType, 'values')
def overload_dataframe_values(df):
    check_runtime_cols_unsupported(df, 'DataFrame.values')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.values')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.values: only supported for dataframes containing numeric values'
            )
    rcnvi__fvf = len(df.columns)
    jqp__xtsiq = set(i for i in range(rcnvi__fvf) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in jqp__xtsiq else '') for i in
        range(rcnvi__fvf))
    ccv__mvv = 'def f(df):\n'.format()
    ccv__mvv += '    return np.stack(({},), 1)\n'.format(data_args)
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo, 'np': np}, sczhi__csetf)
    pll__seyve = sczhi__csetf['f']
    return pll__seyve


@overload_method(DataFrameType, 'to_numpy', inline='always', no_unliteral=True)
def overload_dataframe_to_numpy(df, dtype=None, copy=False, na_value=_no_input
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.to_numpy()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.to_numpy()')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.to_numpy(): only supported for dataframes containing numeric values'
            )
    nitc__wbulg = {'dtype': dtype, 'na_value': na_value}
    vuvmw__ttktr = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', nitc__wbulg, vuvmw__ttktr,
        package_name='pandas', module_name='DataFrame')

    def impl(df, dtype=None, copy=False, na_value=_no_input):
        return df.values
    return impl


@overload_attribute(DataFrameType, 'ndim', inline='always')
def overload_dataframe_ndim(df):
    return lambda df: 2


@overload_attribute(DataFrameType, 'size')
def overload_dataframe_size(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            hpzhb__dqxs = bodo.hiframes.table.compute_num_runtime_columns(t)
            return hpzhb__dqxs * len(t)
        return impl
    ncols = len(df.columns)
    return lambda df: ncols * len(df)


@lower_getattr(DataFrameType, 'shape')
def lower_dataframe_shape(context, builder, typ, val):
    impl = overload_dataframe_shape(typ)
    return context.compile_internal(builder, impl, types.Tuple([types.int64,
        types.int64])(typ), (val,))


def overload_dataframe_shape(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            hpzhb__dqxs = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), hpzhb__dqxs
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), types.int64(ncols))


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    ccv__mvv = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    bpbpt__efyq = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    ccv__mvv += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{bpbpt__efyq}), {index}, None)
"""
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo}, sczhi__csetf)
    impl = sczhi__csetf['impl']
    return impl


@overload_attribute(DataFrameType, 'empty')
def overload_dataframe_empty(df):
    check_runtime_cols_unsupported(df, 'DataFrame.empty')
    if len(df.columns) == 0:
        return lambda df: True
    return lambda df: len(df) == 0


@overload_method(DataFrameType, 'assign', no_unliteral=True)
def overload_dataframe_assign(df, **kwargs):
    check_runtime_cols_unsupported(df, 'DataFrame.assign()')
    raise_bodo_error('Invalid df.assign() call')


@overload_method(DataFrameType, 'insert', no_unliteral=True)
def overload_dataframe_insert(df, loc, column, value, allow_duplicates=False):
    check_runtime_cols_unsupported(df, 'DataFrame.insert()')
    raise_bodo_error('Invalid df.insert() call')


def _get_dtype_str(dtype):
    if isinstance(dtype, types.Function):
        if dtype.key[0] == str:
            return "'str'"
        elif dtype.key[0] == float:
            return 'float'
        elif dtype.key[0] == int:
            return 'int'
        elif dtype.key[0] == bool:
            return 'bool'
        else:
            raise BodoError(f'invalid dtype: {dtype}')
    if type(dtype) in bodo.libs.int_arr_ext.pd_int_dtype_classes:
        return dtype.name
    if isinstance(dtype, types.DTypeSpec):
        dtype = dtype.dtype
    if isinstance(dtype, types.functions.NumberClass):
        return f"'{dtype.key}'"
    if isinstance(dtype, types.PyObject) or dtype in (object, 'object'):
        return "'object'"
    if dtype in (bodo.libs.str_arr_ext.string_dtype, pd.StringDtype()):
        return 'str'
    return f"'{dtype}'"


@overload_method(DataFrameType, 'astype', inline='always', no_unliteral=True)
def overload_dataframe_astype(df, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True, _bodo_object_typeref=None):
    check_runtime_cols_unsupported(df, 'DataFrame.astype()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.astype()')
    nitc__wbulg = {'copy': copy, 'errors': errors}
    vuvmw__ttktr = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', nitc__wbulg, vuvmw__ttktr,
        package_name='pandas', module_name='DataFrame')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "DataFrame.astype(): 'dtype' when passed as string must be a constant value"
            )
    extra_globals = None
    header = """def impl(df, dtype, copy=True, errors='raise', _bodo_nan_to_str=True, _bodo_object_typeref=None):
"""
    if df.is_table_format:
        extra_globals = {}
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        bhc__dwicm = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        tbniz__zqvlo = _bodo_object_typeref.instance_type
        assert isinstance(tbniz__zqvlo, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in tbniz__zqvlo.column_index:
                    idx = tbniz__zqvlo.column_index[name]
                    arr_typ = tbniz__zqvlo.data[idx]
                else:
                    arr_typ = df.data[i]
                bhc__dwicm.append(arr_typ)
        else:
            extra_globals = {}
            xtu__fgrhu = {}
            for i, name in enumerate(tbniz__zqvlo.columns):
                arr_typ = tbniz__zqvlo.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    cnqa__vqr = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    cnqa__vqr = boolean_dtype
                else:
                    cnqa__vqr = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = cnqa__vqr
                xtu__fgrhu[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {xtu__fgrhu[ueo__ags]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if ueo__ags in xtu__fgrhu else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, ueo__ags in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        bxwsw__sbcrp = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            bxwsw__sbcrp = {name: dtype_to_array_type(parse_dtype(dtype)) for
                name, dtype in bxwsw__sbcrp.items()}
            for i, name in enumerate(df.columns):
                if name in bxwsw__sbcrp:
                    arr_typ = bxwsw__sbcrp[name]
                else:
                    arr_typ = df.data[i]
                bhc__dwicm.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(bxwsw__sbcrp[ueo__ags])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if ueo__ags in bxwsw__sbcrp else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, ueo__ags in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        bhc__dwicm = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        qyh__bty = bodo.TableType(tuple(bhc__dwicm))
        extra_globals['out_table_typ'] = qyh__bty
        data_args = (
            'bodo.utils.table_utils.table_astype(table, out_table_typ, copy, _bodo_nan_to_str)'
            )
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'copy', inline='always', no_unliteral=True)
def overload_dataframe_copy(df, deep=True):
    check_runtime_cols_unsupported(df, 'DataFrame.copy()')
    header = 'def impl(df, deep=True):\n'
    extra_globals = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        umxj__tpr = types.none
        extra_globals = {'output_arr_typ': umxj__tpr}
        if is_overload_false(deep):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
        elif is_overload_true(deep):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' + 'True)')
        else:
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' +
                'True) if deep else bodo.utils.table_utils.generate_mappable_table_func('
                 + 'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
    else:
        xgs__rzkd = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                xgs__rzkd.append(arr + '.copy()')
            elif is_overload_false(deep):
                xgs__rzkd.append(arr)
            else:
                xgs__rzkd.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(xgs__rzkd)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    nitc__wbulg = {'index': index, 'level': level, 'errors': errors}
    vuvmw__ttktr = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', nitc__wbulg, vuvmw__ttktr,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.rename(): 'inplace' keyword only supports boolean constant assignment"
            )
    if not is_overload_none(mapper):
        if not is_overload_none(columns):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'mapper' and 'columns'"
                )
        if not (is_overload_constant_int(axis) and get_overload_const_int(
            axis) == 1):
            raise BodoError(
                "DataFrame.rename(): 'mapper' only supported with axis=1")
        if not is_overload_constant_dict(mapper):
            raise_bodo_error(
                "'mapper' argument to DataFrame.rename() should be a constant dictionary"
                )
        ytck__gvlh = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        ytck__gvlh = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    rjluu__fzndx = tuple([ytck__gvlh.get(df.columns[i], df.columns[i]) for
        i in range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    ukfsh__dzjvs = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        ukfsh__dzjvs = df.copy(columns=rjluu__fzndx)
        umxj__tpr = types.none
        extra_globals = {'output_arr_typ': umxj__tpr}
        if is_overload_false(copy):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
        elif is_overload_true(copy):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' + 'True)')
        else:
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' +
                'True) if copy else bodo.utils.table_utils.generate_mappable_table_func('
                 + 'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
    else:
        xgs__rzkd = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                xgs__rzkd.append(arr + '.copy()')
            elif is_overload_false(copy):
                xgs__rzkd.append(arr)
            else:
                xgs__rzkd.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(xgs__rzkd)
    return _gen_init_df(header, rjluu__fzndx, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    wbs__vzip = not is_overload_none(items)
    ewctt__jqr = not is_overload_none(like)
    qfigk__noitq = not is_overload_none(regex)
    ydg__olzn = wbs__vzip ^ ewctt__jqr ^ qfigk__noitq
    dbp__gus = not (wbs__vzip or ewctt__jqr or qfigk__noitq)
    if dbp__gus:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not ydg__olzn:
        raise BodoError(
            'DataFrame.filter(): keyword arguments `items`, `like`, and `regex` are mutually exclusive'
            )
    if is_overload_none(axis):
        axis = 'columns'
    if is_overload_constant_str(axis):
        axis = get_overload_const_str(axis)
        if axis not in {'index', 'columns'}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either "index" or "columns" if string'
                )
        mskqu__who = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        mskqu__who = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert mskqu__who in {0, 1}
    ccv__mvv = 'def impl(df, items=None, like=None, regex=None, axis=None):\n'
    if mskqu__who == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if mskqu__who == 1:
        srhkq__yxwp = []
        thvi__nvb = []
        rpyiy__tqn = []
        if wbs__vzip:
            if is_overload_constant_list(items):
                vacc__fiqr = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if ewctt__jqr:
            if is_overload_constant_str(like):
                hor__mbn = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if qfigk__noitq:
            if is_overload_constant_str(regex):
                irp__wra = get_overload_const_str(regex)
                ttxu__apysd = re.compile(irp__wra)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, ueo__ags in enumerate(df.columns):
            if not is_overload_none(items
                ) and ueo__ags in vacc__fiqr or not is_overload_none(like
                ) and hor__mbn in str(ueo__ags) or not is_overload_none(regex
                ) and ttxu__apysd.search(str(ueo__ags)):
                thvi__nvb.append(ueo__ags)
                rpyiy__tqn.append(i)
        for i in rpyiy__tqn:
            var_name = f'data_{i}'
            srhkq__yxwp.append(var_name)
            ccv__mvv += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(srhkq__yxwp)
        return _gen_init_df(ccv__mvv, thvi__nvb, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    ukfsh__dzjvs = None
    if df.is_table_format:
        umxj__tpr = types.Array(types.bool_, 1, 'C')
        ukfsh__dzjvs = DataFrameType(tuple([umxj__tpr] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': umxj__tpr}
        data_args = ('bodo.utils.table_utils.generate_mappable_table_func(' +
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), ' +
            "'bodo.libs.array_ops.array_op_isna', " + 'output_arr_typ, ' +
            'False)')
    else:
        data_args = ', '.join(
            f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'select_dtypes', inline='always',
    no_unliteral=True)
def overload_dataframe_select_dtypes(df, include=None, exclude=None):
    check_runtime_cols_unsupported(df, 'DataFrame.select_dtypes')
    mxsfm__arca = is_overload_none(include)
    qckzu__umtte = is_overload_none(exclude)
    rtl__vhtb = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if mxsfm__arca and qckzu__umtte:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not mxsfm__arca:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            fflq__gcqii = [dtype_to_array_type(parse_dtype(elem, rtl__vhtb)
                ) for elem in include]
        elif is_legal_input(include):
            fflq__gcqii = [dtype_to_array_type(parse_dtype(include, rtl__vhtb))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        fflq__gcqii = get_nullable_and_non_nullable_types(fflq__gcqii)
        sik__sblp = tuple(ueo__ags for i, ueo__ags in enumerate(df.columns) if
            df.data[i] in fflq__gcqii)
    else:
        sik__sblp = df.columns
    if not qckzu__umtte:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            sbzap__nglu = [dtype_to_array_type(parse_dtype(elem, rtl__vhtb)
                ) for elem in exclude]
        elif is_legal_input(exclude):
            sbzap__nglu = [dtype_to_array_type(parse_dtype(exclude, rtl__vhtb))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        sbzap__nglu = get_nullable_and_non_nullable_types(sbzap__nglu)
        sik__sblp = tuple(ueo__ags for ueo__ags in sik__sblp if df.data[df.
            column_index[ueo__ags]] not in sbzap__nglu)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ueo__ags]})'
         for ueo__ags in sik__sblp)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, sik__sblp, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    ukfsh__dzjvs = None
    if df.is_table_format:
        umxj__tpr = types.Array(types.bool_, 1, 'C')
        ukfsh__dzjvs = DataFrameType(tuple([umxj__tpr] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': umxj__tpr}
        data_args = ('bodo.utils.table_utils.generate_mappable_table_func(' +
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), ' +
            "'~bodo.libs.array_ops.array_op_isna', " + 'output_arr_typ, ' +
            'False)')
    else:
        data_args = ', '.join(
            f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})) == False'
             for i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


def overload_dataframe_head(df, n=5):
    if df.is_table_format:
        data_args = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[:n]')
    else:
        data_args = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:n]'
             for i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:n]'
    return _gen_init_df(header, df.columns, data_args, index)


@lower_builtin('df.head', DataFrameType, types.Integer)
@lower_builtin('df.head', DataFrameType, types.Omitted)
def dataframe_head_lower(context, builder, sig, args):
    impl = overload_dataframe_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'tail', inline='always', no_unliteral=True)
def overload_dataframe_tail(df, n=5):
    check_runtime_cols_unsupported(df, 'DataFrame.tail()')
    if not is_overload_int(n):
        raise BodoError("Dataframe.tail(): 'n' must be an Integer")
    if df.is_table_format:
        data_args = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[m:]')
    else:
        data_args = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[m:]'
             for i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    header += '  m = bodo.hiframes.series_impl.tail_slice(len(df), n)\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[m:]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'first', inline='always', no_unliteral=True)
def overload_dataframe_first(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.first()')
    hwlf__hfybl = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in hwlf__hfybl:
        raise BodoError(
            "DataFrame.first(): 'offset' must be an string or DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.first()')
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:valid_entries]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:valid_entries]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    start_date = df_index[0]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, start_date, False)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'last', inline='always', no_unliteral=True)
def overload_dataframe_last(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.last()')
    hwlf__hfybl = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in hwlf__hfybl:
        raise BodoError(
            "DataFrame.last(): 'offset' must be an string or DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.last()')
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[len(df)-valid_entries:]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[len(df)-valid_entries:]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    final_date = df_index[-1]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, final_date, True)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'to_string', no_unliteral=True)
def to_string_overload(df, buf=None, columns=None, col_space=None, header=
    True, index=True, na_rep='NaN', formatters=None, float_format=None,
    sparsify=None, index_names=True, justify=None, max_rows=None, min_rows=
    None, max_cols=None, show_dimensions=False, decimal='.', line_width=
    None, max_colwidth=None, encoding=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_string()')

    def impl(df, buf=None, columns=None, col_space=None, header=True, index
        =True, na_rep='NaN', formatters=None, float_format=None, sparsify=
        None, index_names=True, justify=None, max_rows=None, min_rows=None,
        max_cols=None, show_dimensions=False, decimal='.', line_width=None,
        max_colwidth=None, encoding=None):
        with numba.objmode(res='string'):
            res = df.to_string(buf=buf, columns=columns, col_space=
                col_space, header=header, index=index, na_rep=na_rep,
                formatters=formatters, float_format=float_format, sparsify=
                sparsify, index_names=index_names, justify=justify,
                max_rows=max_rows, min_rows=min_rows, max_cols=max_cols,
                show_dimensions=show_dimensions, decimal=decimal,
                line_width=line_width, max_colwidth=max_colwidth, encoding=
                encoding)
        return res
    return impl


@overload_method(DataFrameType, 'isin', inline='always', no_unliteral=True)
def overload_dataframe_isin(df, values):
    check_runtime_cols_unsupported(df, 'DataFrame.isin()')
    from bodo.utils.typing import is_iterable_type
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.isin()')
    ccv__mvv = 'def impl(df, values):\n'
    mhik__vbe = {}
    lri__oiwm = False
    if isinstance(values, DataFrameType):
        lri__oiwm = True
        for i, ueo__ags in enumerate(df.columns):
            if ueo__ags in values.column_index:
                zpl__jjjzm = 'val{}'.format(i)
                ccv__mvv += f"""  {zpl__jjjzm} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[ueo__ags]})
"""
                mhik__vbe[ueo__ags] = zpl__jjjzm
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        mhik__vbe = {ueo__ags: 'values' for ueo__ags in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        zpl__jjjzm = 'data{}'.format(i)
        ccv__mvv += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(zpl__jjjzm, i))
        data.append(zpl__jjjzm)
    vajd__fgel = ['out{}'.format(i) for i in range(len(df.columns))]
    qyq__knx = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    mamhj__dua = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    whoyy__kow = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, xmhy__fwqjk) in enumerate(zip(df.columns, data)):
        if cname in mhik__vbe:
            pszd__gkhj = mhik__vbe[cname]
            if lri__oiwm:
                ccv__mvv += qyq__knx.format(xmhy__fwqjk, pszd__gkhj,
                    vajd__fgel[i])
            else:
                ccv__mvv += mamhj__dua.format(xmhy__fwqjk, pszd__gkhj,
                    vajd__fgel[i])
        else:
            ccv__mvv += whoyy__kow.format(vajd__fgel[i])
    return _gen_init_df(ccv__mvv, df.columns, ','.join(vajd__fgel))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    rcnvi__fvf = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(rcnvi__fvf))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    rvy__ydp = [ueo__ags for ueo__ags, rzygd__crlxs in zip(df.columns, df.
        data) if bodo.utils.typing._is_pandas_numeric_dtype(rzygd__crlxs.dtype)
        ]
    assert len(rvy__ydp) != 0
    twk__vxbj = ''
    if not any(rzygd__crlxs == types.float64 for rzygd__crlxs in df.data):
        twk__vxbj = '.astype(np.float64)'
    hszsy__tnxy = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[ueo__ags], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[ueo__ags]], IntegerArrayType) or
        df.data[df.column_index[ueo__ags]] == boolean_array else '') for
        ueo__ags in rvy__ydp)
    heq__nes = 'np.stack(({},), 1){}'.format(hszsy__tnxy, twk__vxbj)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(rvy__ydp)))
    index = f'{generate_col_to_index_func_text(rvy__ydp)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(heq__nes)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, rvy__ydp, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    srkse__piqbl = dict(ddof=ddof)
    ozep__ktph = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    tct__wae = '1' if is_overload_none(min_periods) else 'min_periods'
    rvy__ydp = [ueo__ags for ueo__ags, rzygd__crlxs in zip(df.columns, df.
        data) if bodo.utils.typing._is_pandas_numeric_dtype(rzygd__crlxs.dtype)
        ]
    if len(rvy__ydp) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    twk__vxbj = ''
    if not any(rzygd__crlxs == types.float64 for rzygd__crlxs in df.data):
        twk__vxbj = '.astype(np.float64)'
    hszsy__tnxy = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[ueo__ags], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[ueo__ags]], IntegerArrayType) or
        df.data[df.column_index[ueo__ags]] == boolean_array else '') for
        ueo__ags in rvy__ydp)
    heq__nes = 'np.stack(({},), 1){}'.format(hszsy__tnxy, twk__vxbj)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(rvy__ydp)))
    index = f'pd.Index({rvy__ydp})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(heq__nes)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        tct__wae)
    return _gen_init_df(header, rvy__ydp, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    srkse__piqbl = dict(axis=axis, level=level, numeric_only=numeric_only)
    ozep__ktph = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    ccv__mvv = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    ccv__mvv += '  data = np.array([{}])\n'.format(data_args)
    tgdu__qhtu = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    ccv__mvv += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {tgdu__qhtu})\n'
        )
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo, 'np': np}, sczhi__csetf)
    impl = sczhi__csetf['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    srkse__piqbl = dict(axis=axis)
    ozep__ktph = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    ccv__mvv = 'def impl(df, axis=0, dropna=True):\n'
    ccv__mvv += '  data = np.asarray(({},))\n'.format(data_args)
    tgdu__qhtu = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    ccv__mvv += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {tgdu__qhtu})\n'
        )
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo, 'np': np}, sczhi__csetf)
    impl = sczhi__csetf['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    srkse__piqbl = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    ozep__ktph = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    srkse__piqbl = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    ozep__ktph = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    srkse__piqbl = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    ozep__ktph = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    srkse__piqbl = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    ozep__ktph = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    srkse__piqbl = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    ozep__ktph = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    srkse__piqbl = dict(skipna=skipna, level=level, ddof=ddof, numeric_only
        =numeric_only)
    ozep__ktph = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    srkse__piqbl = dict(skipna=skipna, level=level, ddof=ddof, numeric_only
        =numeric_only)
    ozep__ktph = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    srkse__piqbl = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    ozep__ktph = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    srkse__piqbl = dict(numeric_only=numeric_only, interpolation=interpolation)
    ozep__ktph = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    srkse__piqbl = dict(axis=axis, skipna=skipna)
    ozep__ktph = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for bmmjn__dam in df.data:
        if not (bodo.utils.utils.is_np_array_typ(bmmjn__dam) and (
            bmmjn__dam.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(bmmjn__dam.dtype, (types.Number, types.Boolean))) or
            isinstance(bmmjn__dam, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or bmmjn__dam in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {bmmjn__dam} not supported.'
                )
        if isinstance(bmmjn__dam, bodo.CategoricalArrayType
            ) and not bmmjn__dam.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    srkse__piqbl = dict(axis=axis, skipna=skipna)
    ozep__ktph = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for bmmjn__dam in df.data:
        if not (bodo.utils.utils.is_np_array_typ(bmmjn__dam) and (
            bmmjn__dam.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(bmmjn__dam.dtype, (types.Number, types.Boolean))) or
            isinstance(bmmjn__dam, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or bmmjn__dam in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {bmmjn__dam} not supported.'
                )
        if isinstance(bmmjn__dam, bodo.CategoricalArrayType
            ) and not bmmjn__dam.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmin(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmin', axis=axis)


@overload_method(DataFrameType, 'infer_objects', inline='always')
def overload_dataframe_infer_objects(df):
    check_runtime_cols_unsupported(df, 'DataFrame.infer_objects()')
    return lambda df: df.copy()


def _gen_reduce_impl(df, func_name, args=None, axis=None):
    args = '' if is_overload_none(args) else args
    if is_overload_none(axis):
        axis = 0
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
    else:
        raise_bodo_error(
            f'DataFrame.{func_name}: axis must be a constant Integer')
    assert axis in (0, 1), f'invalid axis argument for DataFrame.{func_name}'
    if func_name in ('idxmax', 'idxmin'):
        out_colnames = df.columns
    else:
        rvy__ydp = tuple(ueo__ags for ueo__ags, rzygd__crlxs in zip(df.
            columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype
            (rzygd__crlxs.dtype))
        out_colnames = rvy__ydp
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            suw__qtg = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[ueo__ags]].dtype) for ueo__ags in out_colnames]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(suw__qtg, []))
    except NotImplementedError as zvh__hvtdu:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    vzuh__ceo = ''
    if func_name in ('sum', 'prod'):
        vzuh__ceo = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    ccv__mvv = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, vzuh__ceo))
    if func_name == 'quantile':
        ccv__mvv = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        ccv__mvv = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        ccv__mvv += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        ccv__mvv += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        sczhi__csetf)
    impl = sczhi__csetf['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    wnpp__bbr = ''
    if func_name in ('min', 'max'):
        wnpp__bbr = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        wnpp__bbr = ', dtype=np.float32'
    xroog__fra = f'bodo.libs.array_ops.array_op_{func_name}'
    vxyti__mhk = ''
    if func_name in ['sum', 'prod']:
        vxyti__mhk = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        vxyti__mhk = 'index'
    elif func_name == 'quantile':
        vxyti__mhk = 'q'
    elif func_name in ['std', 'var']:
        vxyti__mhk = 'True, ddof'
    elif func_name == 'median':
        vxyti__mhk = 'True'
    data_args = ', '.join(
        f'{xroog__fra}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ueo__ags]}), {vxyti__mhk})'
         for ueo__ags in out_colnames)
    ccv__mvv = ''
    if func_name in ('idxmax', 'idxmin'):
        ccv__mvv += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        ccv__mvv += ('  data = bodo.utils.conversion.coerce_to_array(({},))\n'
            .format(data_args))
    else:
        ccv__mvv += '  data = np.asarray(({},){})\n'.format(data_args,
            wnpp__bbr)
    ccv__mvv += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return ccv__mvv


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    xgdfp__vyea = [df_type.column_index[ueo__ags] for ueo__ags in out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in xgdfp__vyea)
    muv__vrvrr = '\n        '.join(f'row[{i}] = arr_{xgdfp__vyea[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    icgnp__drr = f'len(arr_{xgdfp__vyea[0]})'
    bgrmx__nwtn = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in bgrmx__nwtn:
        xqu__arszs = bgrmx__nwtn[func_name]
        eyaf__zqx = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        ccv__mvv = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {icgnp__drr}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{eyaf__zqx})
    for i in numba.parfors.parfor.internal_prange(n):
        {muv__vrvrr}
        A[i] = {xqu__arszs}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return ccv__mvv
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    srkse__piqbl = dict(fill_method=fill_method, limit=limit, freq=freq)
    ozep__ktph = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.pct_change()')
    data_args = ', '.join(
        f'bodo.hiframes.rolling.pct_change(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = (
        "def impl(df, periods=1, fill_method='pad', limit=None, freq=None):\n")
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumprod', inline='always', no_unliteral=True)
def overload_dataframe_cumprod(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumprod()')
    srkse__piqbl = dict(axis=axis, skipna=skipna)
    ozep__ktph = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.cumprod()')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumprod()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumsum', inline='always', no_unliteral=True)
def overload_dataframe_cumsum(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumsum()')
    srkse__piqbl = dict(skipna=skipna)
    ozep__ktph = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.cumsum()')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumsum()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


def _is_describe_type(data):
    return isinstance(data, IntegerArrayType) or isinstance(data, types.Array
        ) and isinstance(data.dtype, types.Number
        ) or data.dtype == bodo.datetime64ns


@overload_method(DataFrameType, 'describe', inline='always', no_unliteral=True)
def overload_dataframe_describe(df, percentiles=None, include=None, exclude
    =None, datetime_is_numeric=True):
    check_runtime_cols_unsupported(df, 'DataFrame.describe()')
    srkse__piqbl = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    ozep__ktph = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    rvy__ydp = [ueo__ags for ueo__ags, rzygd__crlxs in zip(df.columns, df.
        data) if _is_describe_type(rzygd__crlxs)]
    if len(rvy__ydp) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    kvbu__huf = sum(df.data[df.column_index[ueo__ags]].dtype == bodo.
        datetime64ns for ueo__ags in rvy__ydp)

    def _get_describe(col_ind):
        ysmyj__itlnb = df.data[col_ind].dtype == bodo.datetime64ns
        if kvbu__huf and kvbu__huf != len(rvy__ydp):
            if ysmyj__itlnb:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for ueo__ags in rvy__ydp:
        col_ind = df.column_index[ueo__ags]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[ueo__ags]) for
        ueo__ags in rvy__ydp)
    zywhb__odifx = (
        "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']")
    if kvbu__huf == len(rvy__ydp):
        zywhb__odifx = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif kvbu__huf:
        zywhb__odifx = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({zywhb__odifx})'
    return _gen_init_df(header, rvy__ydp, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    srkse__piqbl = dict(axis=axis, convert=convert, is_copy=is_copy)
    ozep__ktph = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[indices_t]'
        .format(i) for i in range(len(df.columns)))
    header = 'def impl(df, indices, axis=0, convert=None, is_copy=True):\n'
    header += (
        '  indices_t = bodo.utils.conversion.coerce_to_ndarray(indices)\n')
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[indices_t]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'shift', inline='always', no_unliteral=True)
def overload_dataframe_shift(df, periods=1, freq=None, axis=0, fill_value=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.shift()')
    srkse__piqbl = dict(freq=freq, axis=axis, fill_value=fill_value)
    ozep__ktph = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for uhro__khchz in df.data:
        if not is_supported_shift_array_type(uhro__khchz):
            raise BodoError(
                f'Dataframe.shift() column input type {uhro__khchz.dtype} not supported yet.'
                )
    if not is_overload_int(periods):
        raise BodoError(
            "DataFrame.shift(): 'periods' input must be an integer.")
    data_args = ', '.join(
        f'bodo.hiframes.rolling.shift(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = 'def impl(df, periods=1, freq=None, axis=0, fill_value=None):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'diff', inline='always', no_unliteral=True)
def overload_dataframe_diff(df, periods=1, axis=0):
    check_runtime_cols_unsupported(df, 'DataFrame.diff()')
    srkse__piqbl = dict(axis=axis)
    ozep__ktph = dict(axis=0)
    check_unsupported_args('DataFrame.diff', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for uhro__khchz in df.data:
        if not (isinstance(uhro__khchz, types.Array) and (isinstance(
            uhro__khchz.dtype, types.Number) or uhro__khchz.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {uhro__khchz.dtype} not supported.'
                )
    if not is_overload_int(periods):
        raise BodoError("DataFrame.diff(): 'periods' input must be an integer."
            )
    header = 'def impl(df, periods=1, axis= 0):\n'
    for i in range(len(df.columns)):
        header += (
            f'  data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    data_args = ', '.join(
        f'bodo.hiframes.series_impl.dt64_arr_sub(data_{i}, bodo.hiframes.rolling.shift(data_{i}, periods, False))'
         if df.data[i] == types.Array(bodo.datetime64ns, 1, 'C') else
        f'data_{i} - bodo.hiframes.rolling.shift(data_{i}, periods, False)' for
        i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'explode', inline='always', no_unliteral=True)
def overload_dataframe_explode(df, column, ignore_index=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.explode()')
    uomlr__mhzm = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(uomlr__mhzm)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        goef__egt = get_overload_const_list(column)
    else:
        goef__egt = [get_literal_value(column)]
    npng__fmoho = [df.column_index[ueo__ags] for ueo__ags in goef__egt]
    for i in npng__fmoho:
        if not isinstance(df.data[i], ArrayItemArrayType) and df.data[i
            ].dtype != string_array_split_view_type:
            raise BodoError(
                f'DataFrame.explode(): columns must have array-like entries')
    n = len(df.columns)
    header = 'def impl(df, column, ignore_index=False):\n'
    header += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    header += '  index_arr = bodo.utils.conversion.index_to_array(index)\n'
    for i in range(n):
        header += (
            f'  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    header += (
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{npng__fmoho[0]})\n'
        )
    for i in range(n):
        if i in npng__fmoho:
            header += (
                f'  out_data{i} = bodo.libs.array_kernels.explode_no_index(data{i}, counts)\n'
                )
        else:
            header += (
                f'  out_data{i} = bodo.libs.array_kernels.repeat_kernel(data{i}, counts)\n'
                )
    header += (
        '  new_index = bodo.libs.array_kernels.repeat_kernel(index_arr, counts)\n'
        )
    data_args = ', '.join(f'out_data{i}' for i in range(n))
    index = 'bodo.utils.conversion.convert_to_index(new_index)'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'set_index', inline='always', no_unliteral=True
    )
def overload_dataframe_set_index(df, keys, drop=True, append=False, inplace
    =False, verify_integrity=False):
    check_runtime_cols_unsupported(df, 'DataFrame.set_index()')
    nitc__wbulg = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    vuvmw__ttktr = {'inplace': False, 'append': False, 'verify_integrity': 
        False}
    check_unsupported_args('DataFrame.set_index', nitc__wbulg, vuvmw__ttktr,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_str(keys):
        raise_bodo_error(
            "DataFrame.set_index(): 'keys' must be a constant string")
    col_name = get_overload_const_str(keys)
    col_ind = df.columns.index(col_name)
    header = """def impl(df, keys, drop=True, append=False, inplace=False, verify_integrity=False):
"""
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'.format(
        i) for i in range(len(df.columns)) if i != col_ind)
    columns = tuple(ueo__ags for ueo__ags in df.columns if ueo__ags != col_name
        )
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    nitc__wbulg = {'inplace': inplace}
    vuvmw__ttktr = {'inplace': False}
    check_unsupported_args('query', nitc__wbulg, vuvmw__ttktr, package_name
        ='pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        txer__yus = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[txer__yus]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    nitc__wbulg = {'subset': subset, 'keep': keep}
    vuvmw__ttktr = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', nitc__wbulg,
        vuvmw__ttktr, package_name='pandas', module_name='DataFrame')
    rcnvi__fvf = len(df.columns)
    ccv__mvv = "def impl(df, subset=None, keep='first'):\n"
    for i in range(rcnvi__fvf):
        ccv__mvv += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    nadby__tnh = ', '.join(f'data_{i}' for i in range(rcnvi__fvf))
    nadby__tnh += ',' if rcnvi__fvf == 1 else ''
    ccv__mvv += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({nadby__tnh}))\n')
    ccv__mvv += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    ccv__mvv += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo}, sczhi__csetf)
    impl = sczhi__csetf['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    nitc__wbulg = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    vuvmw__ttktr = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    rlaog__mnsv = []
    if is_overload_constant_list(subset):
        rlaog__mnsv = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        rlaog__mnsv = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        rlaog__mnsv = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    vgqp__ojcah = []
    for col_name in rlaog__mnsv:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        vgqp__ojcah.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', nitc__wbulg,
        vuvmw__ttktr, package_name='pandas', module_name='DataFrame')
    tga__brhck = []
    if vgqp__ojcah:
        for coxm__acosx in vgqp__ojcah:
            if isinstance(df.data[coxm__acosx], bodo.MapArrayType):
                tga__brhck.append(df.columns[coxm__acosx])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                tga__brhck.append(col_name)
    if tga__brhck:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {tga__brhck} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    rcnvi__fvf = len(df.columns)
    vfu__ossv = ['data_{}'.format(i) for i in vgqp__ojcah]
    siqx__bwde = ['data_{}'.format(i) for i in range(rcnvi__fvf) if i not in
        vgqp__ojcah]
    if vfu__ossv:
        mkv__zill = len(vfu__ossv)
    else:
        mkv__zill = rcnvi__fvf
    wlmz__crrn = ', '.join(vfu__ossv + siqx__bwde)
    data_args = ', '.join('data_{}'.format(i) for i in range(rcnvi__fvf))
    ccv__mvv = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(rcnvi__fvf):
        ccv__mvv += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    ccv__mvv += (
        '  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})\n'
        .format(wlmz__crrn, index, mkv__zill))
    ccv__mvv += '  index = bodo.utils.conversion.index_from_array(index_arr)\n'
    return _gen_init_df(ccv__mvv, df.columns, data_args, 'index')


def create_dataframe_mask_where_overload(func_name):

    def overload_dataframe_mask_where(df, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
            f'DataFrame.{func_name}()')
        _validate_arguments_mask_where(f'DataFrame.{func_name}', df, cond,
            other, inplace, axis, level, errors, try_cast)
        header = """def impl(df, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise', try_cast=False):
"""
        if func_name == 'mask':
            header += '  cond = ~cond\n'
        gen_all_false = [False]
        if cond.ndim == 1:
            cond_str = lambda i, _: 'cond'
        elif cond.ndim == 2:
            if isinstance(cond, DataFrameType):

                def cond_str(i, gen_all_false):
                    if df.columns[i] in cond.column_index:
                        return (
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(cond, {cond.column_index[df.columns[i]]})'
                            )
                    else:
                        gen_all_false[0] = True
                        return 'all_false'
            elif isinstance(cond, types.Array):
                cond_str = lambda i, _: f'cond[:,{i}]'
        if not hasattr(other, 'ndim') or other.ndim == 1:
            nwzt__rscbg = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                nwzt__rscbg = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                nwzt__rscbg = lambda i: f'other[:,{i}]'
        rcnvi__fvf = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {nwzt__rscbg(i)})'
             for i in range(rcnvi__fvf))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        gfhb__eav = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(gfhb__eav)


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    srkse__piqbl = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    ozep__ktph = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error(f'{func_name}(): axis argument not supported')
    if not (isinstance(cond, (SeriesType, types.Array, BooleanArrayType)) and
        (cond.ndim == 1 or cond.ndim == 2) and cond.dtype == types.bool_
        ) and not (isinstance(cond, DataFrameType) and cond.ndim == 2 and
        all(cond.data[i].dtype == types.bool_ for i in range(len(df.columns)))
        ):
        raise BodoError(
            f"{func_name}(): 'cond' argument must be a DataFrame, Series, 1- or 2-dimensional array of booleans"
            )
    rcnvi__fvf = len(df.columns)
    if hasattr(other, 'ndim') and (other.ndim != 1 or other.ndim != 2):
        if other.ndim == 2:
            if not isinstance(other, (DataFrameType, types.Array)):
                raise BodoError(
                    f"{func_name}(): 'other', if 2-dimensional, must be a DataFrame or array."
                    )
        elif other.ndim != 1:
            raise BodoError(
                f"{func_name}(): 'other' must be either 1 or 2-dimensional")
    if isinstance(other, DataFrameType):
        for i in range(rcnvi__fvf):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(rcnvi__fvf):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(rcnvi__fvf):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    jxc__ihfc = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    ccv__mvv = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    sczhi__csetf = {}
    cxg__ckcov = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': jxc__ihfc}
    cxg__ckcov.update(extra_globals)
    exec(ccv__mvv, cxg__ckcov, sczhi__csetf)
    impl = sczhi__csetf['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        viapp__fqrgk = pd.Index(lhs.columns)
        agvy__iuyif = pd.Index(rhs.columns)
        pme__ytwa, yugfe__hpcuy, rwgw__dfhk = viapp__fqrgk.join(agvy__iuyif,
            how='left' if is_inplace else 'outer', level=None,
            return_indexers=True)
        return tuple(pme__ytwa), yugfe__hpcuy, rwgw__dfhk
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        fzljw__mrxsz = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        dohpe__vze = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, fzljw__mrxsz)
        check_runtime_cols_unsupported(rhs, fzljw__mrxsz)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                pme__ytwa, yugfe__hpcuy, rwgw__dfhk = _get_binop_columns(lhs,
                    rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {mpin__uxne}) {fzljw__mrxsz}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {oxwll__gnmic})'
                     if mpin__uxne != -1 and oxwll__gnmic != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for mpin__uxne, oxwll__gnmic in zip(yugfe__hpcuy,
                    rwgw__dfhk))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, pme__ytwa, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            nlf__anyg = []
            tuoq__fflon = []
            if op in dohpe__vze:
                for i, rjk__dni in enumerate(lhs.data):
                    if is_common_scalar_dtype([rjk__dni.dtype, rhs]):
                        nlf__anyg.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {fzljw__mrxsz} rhs'
                            )
                    else:
                        qeof__subhu = f'arr{i}'
                        tuoq__fflon.append(qeof__subhu)
                        nlf__anyg.append(qeof__subhu)
                data_args = ', '.join(nlf__anyg)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {fzljw__mrxsz} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(tuoq__fflon) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {qeof__subhu} = np.empty(n, dtype=np.bool_)\n' for
                    qeof__subhu in tuoq__fflon)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(qeof__subhu, 
                    op == operator.ne) for qeof__subhu in tuoq__fflon)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            nlf__anyg = []
            tuoq__fflon = []
            if op in dohpe__vze:
                for i, rjk__dni in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, rjk__dni.dtype]):
                        nlf__anyg.append(
                            f'lhs {fzljw__mrxsz} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        qeof__subhu = f'arr{i}'
                        tuoq__fflon.append(qeof__subhu)
                        nlf__anyg.append(qeof__subhu)
                data_args = ', '.join(nlf__anyg)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, fzljw__mrxsz) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(tuoq__fflon) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(qeof__subhu) for qeof__subhu in tuoq__fflon)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(qeof__subhu, 
                    op == operator.ne) for qeof__subhu in tuoq__fflon)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(rhs)'
            return _gen_init_df(header, rhs.columns, data_args, index)
    return overload_dataframe_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        gfhb__eav = create_binary_op_overload(op)
        overload(op)(gfhb__eav)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        fzljw__mrxsz = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, fzljw__mrxsz)
        check_runtime_cols_unsupported(right, fzljw__mrxsz)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                pme__ytwa, _, rwgw__dfhk = _get_binop_columns(left, right, True
                    )
                ccv__mvv = 'def impl(left, right):\n'
                for i, oxwll__gnmic in enumerate(rwgw__dfhk):
                    if oxwll__gnmic == -1:
                        ccv__mvv += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    ccv__mvv += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    ccv__mvv += f"""  df_arr{i} {fzljw__mrxsz} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {oxwll__gnmic})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    pme__ytwa)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(ccv__mvv, pme__ytwa, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            ccv__mvv = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                ccv__mvv += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                ccv__mvv += '  df_arr{0} {1} right\n'.format(i, fzljw__mrxsz)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(ccv__mvv, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        gfhb__eav = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(gfhb__eav)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            fzljw__mrxsz = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, fzljw__mrxsz)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, fzljw__mrxsz) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        gfhb__eav = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(gfhb__eav)


_install_unary_ops()


def overload_isna(obj):
    check_runtime_cols_unsupported(obj, 'pd.isna()')
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj):
        return lambda obj: obj.isna()
    if is_array_typ(obj):

        def impl(obj):
            numba.parfors.parfor.init_prange()
            n = len(obj)
            drbq__cglo = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                drbq__cglo[i] = bodo.libs.array_kernels.isna(obj, i)
            return drbq__cglo
        return impl


overload(pd.isna, inline='always')(overload_isna)
overload(pd.isnull, inline='always')(overload_isna)


@overload(pd.isna)
@overload(pd.isnull)
def overload_isna_scalar(obj):
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj) or is_array_typ(
        obj):
        return
    if isinstance(obj, (types.List, types.UniTuple)):

        def impl(obj):
            n = len(obj)
            drbq__cglo = np.empty(n, np.bool_)
            for i in range(n):
                drbq__cglo[i] = pd.isna(obj[i])
            return drbq__cglo
        return impl
    obj = types.unliteral(obj)
    if obj == bodo.string_type:
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Integer):
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Float):
        return lambda obj: np.isnan(obj)
    if isinstance(obj, (types.NPDatetime, types.NPTimedelta)):
        return lambda obj: np.isnat(obj)
    if obj == types.none:
        return lambda obj: unliteral_val(True)
    if isinstance(obj, bodo.hiframes.pd_timestamp_ext.PandasTimestampType):
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_dt64(obj.value))
    if obj == bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type:
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_timedelta64(obj.value))
    if isinstance(obj, types.Optional):
        return lambda obj: obj is None
    return lambda obj: unliteral_val(False)


@overload(operator.setitem, no_unliteral=True)
def overload_setitem_arr_none(A, idx, val):
    if is_array_typ(A, False) and isinstance(idx, types.Integer
        ) and val == types.none:
        return lambda A, idx, val: bodo.libs.array_kernels.setna(A, idx)


def overload_notna(obj):
    check_runtime_cols_unsupported(obj, 'pd.notna()')
    if isinstance(obj, (DataFrameType, SeriesType)):
        return lambda obj: obj.notna()
    if isinstance(obj, (types.List, types.UniTuple)) or is_array_typ(obj,
        include_index_series=True):
        return lambda obj: ~pd.isna(obj)
    return lambda obj: not pd.isna(obj)


overload(pd.notna, inline='always', no_unliteral=True)(overload_notna)
overload(pd.notnull, inline='always', no_unliteral=True)(overload_notna)


def _get_pd_dtype_str(t):
    if t.dtype == types.NPDatetime('ns'):
        return "'datetime64[ns]'"
    return bodo.ir.csv_ext._get_pd_dtype_str(t)


@overload_method(DataFrameType, 'replace', inline='always', no_unliteral=True)
def overload_dataframe_replace(df, to_replace=None, value=None, inplace=
    False, limit=None, regex=False, method='pad'):
    check_runtime_cols_unsupported(df, 'DataFrame.replace()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.replace()')
    if is_overload_none(to_replace):
        raise BodoError('replace(): to_replace value of None is not supported')
    nitc__wbulg = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    vuvmw__ttktr = {'inplace': False, 'limit': None, 'regex': False,
        'method': 'pad'}
    check_unsupported_args('replace', nitc__wbulg, vuvmw__ttktr,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    bmye__amcx = str(expr_node)
    return bmye__amcx.startswith('left.') or bmye__amcx.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    lckr__kefu = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (lckr__kefu,))
    flyy__goifx = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        xysc__ada = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        cozz__hpl = {('NOT_NA', flyy__goifx(rjk__dni)): rjk__dni for
            rjk__dni in null_set}
        rlky__nazdu, _, _ = _parse_query_expr(xysc__ada, env, [], [], None,
            join_cleaned_cols=cozz__hpl)
        ihii__sgbpj = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            poe__xsj = pd.core.computation.ops.BinOp('&', rlky__nazdu,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = ihii__sgbpj
        return poe__xsj

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                lcv__dzsy = set()
                gqos__oclrp = set()
                lphzr__gkzhd = _insert_NA_cond_body(expr_node.lhs, lcv__dzsy)
                piczm__gzvlo = _insert_NA_cond_body(expr_node.rhs, gqos__oclrp)
                xnl__nzrt = lcv__dzsy.intersection(gqos__oclrp)
                lcv__dzsy.difference_update(xnl__nzrt)
                gqos__oclrp.difference_update(xnl__nzrt)
                null_set.update(xnl__nzrt)
                expr_node.lhs = append_null_checks(lphzr__gkzhd, lcv__dzsy)
                expr_node.rhs = append_null_checks(piczm__gzvlo, gqos__oclrp)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            bach__zuinm = expr_node.name
            jcr__opxu, col_name = bach__zuinm.split('.')
            if jcr__opxu == 'left':
                xicfc__xgwq = left_columns
                data = left_data
            else:
                xicfc__xgwq = right_columns
                data = right_data
            cnh__favqv = data[xicfc__xgwq.index(col_name)]
            if bodo.utils.typing.is_nullable(cnh__favqv):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    ponqq__tgu = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        vutk__ldmm = str(expr_node.lhs)
        hxbxe__nlzr = str(expr_node.rhs)
        if vutk__ldmm.startswith('left.') and hxbxe__nlzr.startswith('left.'
            ) or vutk__ldmm.startswith('right.') and hxbxe__nlzr.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [vutk__ldmm.split('.')[1]]
        right_on = [hxbxe__nlzr.split('.')[1]]
        if vutk__ldmm.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        ckft__ncgyd, ckbvd__qayw, tbm__nbsz = _extract_equal_conds(expr_node
            .lhs)
        efcz__endw, hhock__butm, aomon__wmh = _extract_equal_conds(expr_node
            .rhs)
        left_on = ckft__ncgyd + efcz__endw
        right_on = ckbvd__qayw + hhock__butm
        if tbm__nbsz is None:
            return left_on, right_on, aomon__wmh
        if aomon__wmh is None:
            return left_on, right_on, tbm__nbsz
        expr_node.lhs = tbm__nbsz
        expr_node.rhs = aomon__wmh
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    lckr__kefu = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (lckr__kefu,))
    ytck__gvlh = dict()
    flyy__goifx = pd.core.computation.parsing.clean_column_name
    for name, mqxit__poptp in (('left', left_columns), ('right', right_columns)
        ):
        for rjk__dni in mqxit__poptp:
            rnkyx__wee = flyy__goifx(rjk__dni)
            cjfty__uyg = name, rnkyx__wee
            if cjfty__uyg in ytck__gvlh:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{rjk__dni}' and '{ytck__gvlh[rnkyx__wee]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            ytck__gvlh[cjfty__uyg] = rjk__dni
    hjbru__jzom, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=ytck__gvlh)
    left_on, right_on, jmua__vsmkh = _extract_equal_conds(hjbru__jzom.terms)
    return left_on, right_on, _insert_NA_cond(jmua__vsmkh, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    srkse__piqbl = dict(sort=sort, copy=copy, validate=validate)
    ozep__ktph = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    wge__usxn = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    jcbk__nroy = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in wge__usxn and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, jmo__jtjc = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if jmo__jtjc is None:
                    jcbk__nroy = ''
                else:
                    jcbk__nroy = str(jmo__jtjc)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = wge__usxn
        right_keys = wge__usxn
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    if (not left_on or not right_on) and not is_overload_none(on):
        raise BodoError(
            f"DataFrame.merge(): Merge condition '{get_overload_const_str(on)}' requires a cross join to implement, but cross join is not supported."
            )
    if not is_overload_bool(indicator):
        raise_bodo_error(
            'DataFrame.merge(): indicator must be a constant boolean')
    indicator_val = get_overload_const_bool(indicator)
    if not is_overload_bool(_bodo_na_equal):
        raise_bodo_error(
            'DataFrame.merge(): bodo extension _bodo_na_equal must be a constant boolean'
            )
    owbcm__tqgie = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        ajxdn__apmwk = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        ajxdn__apmwk = list(get_overload_const_list(suffixes))
    suffix_x = ajxdn__apmwk[0]
    suffix_y = ajxdn__apmwk[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    ccv__mvv = "def _impl(left, right, how='inner', on=None, left_on=None,\n"
    ccv__mvv += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    ccv__mvv += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    ccv__mvv += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, owbcm__tqgie, jcbk__nroy))
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo}, sczhi__csetf)
    _impl = sczhi__csetf['_impl']
    return _impl


def common_validate_merge_merge_asof_spec(name_func, left, right, on,
    left_on, right_on, left_index, right_index, suffixes):
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError(name_func + '() requires dataframe inputs')
    valid_dataframe_column_types = (ArrayItemArrayType, MapArrayType,
        StructArrayType, CategoricalArrayType, types.Array,
        IntegerArrayType, DecimalArrayType, IntervalArrayType, bodo.
        DatetimeArrayType)
    wkwfd__rtli = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    awmi__ibrjb = {get_overload_const_str(qxh__jqns) for qxh__jqns in (
        left_on, right_on, on) if is_overload_constant_str(qxh__jqns)}
    for df in (left, right):
        for i, rjk__dni in enumerate(df.data):
            if not isinstance(rjk__dni, valid_dataframe_column_types
                ) and rjk__dni not in wkwfd__rtli:
                raise BodoError(
                    f'{name_func}(): use of column with {type(rjk__dni)} in merge unsupported'
                    )
            if df.columns[i] in awmi__ibrjb and isinstance(rjk__dni,
                MapArrayType):
                raise BodoError(
                    f'{name_func}(): merge on MapArrayType unsupported')
    ensure_constant_arg(name_func, 'left_index', left_index, bool)
    ensure_constant_arg(name_func, 'right_index', right_index, bool)
    if not is_overload_constant_tuple(suffixes
        ) and not is_overload_constant_list(suffixes):
        raise_bodo_error(name_func +
            "(): suffixes parameters should be ['_left', '_right']")
    if is_overload_constant_tuple(suffixes):
        ajxdn__apmwk = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        ajxdn__apmwk = list(get_overload_const_list(suffixes))
    if len(ajxdn__apmwk) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    wge__usxn = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        jhvwv__jaq = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            jhvwv__jaq = on_str not in wge__usxn and ('left.' in on_str or 
                'right.' in on_str)
        if len(wge__usxn) == 0 and not jhvwv__jaq:
            raise_bodo_error(name_func +
                '(): No common columns to perform merge on. Merge options: left_on={lon}, right_on={ron}, left_index={lidx}, right_index={ridx}'
                .format(lon=is_overload_true(left_on), ron=is_overload_true
                (right_on), lidx=is_overload_true(left_index), ridx=
                is_overload_true(right_index)))
        if not is_overload_none(left_on) or not is_overload_none(right_on):
            raise BodoError(name_func +
                '(): Can only pass argument "on" OR "left_on" and "right_on", not a combination of both.'
                )
    if (is_overload_true(left_index) or not is_overload_none(left_on)
        ) and is_overload_none(right_on) and not is_overload_true(right_index):
        raise BodoError(name_func +
            '(): Must pass right_on or right_index=True')
    if (is_overload_true(right_index) or not is_overload_none(right_on)
        ) and is_overload_none(left_on) and not is_overload_true(left_index):
        raise BodoError(name_func + '(): Must pass left_on or left_index=True')


def validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
    right_index, sort, suffixes, copy, indicator, validate):
    common_validate_merge_merge_asof_spec('merge', left, right, on, left_on,
        right_on, left_index, right_index, suffixes)
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))


def validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
    right_index, by, left_by, right_by, suffixes, tolerance,
    allow_exact_matches, direction):
    common_validate_merge_merge_asof_spec('merge_asof', left, right, on,
        left_on, right_on, left_index, right_index, suffixes)
    if not is_overload_true(allow_exact_matches):
        raise BodoError(
            'merge_asof(): allow_exact_matches parameter only supports default value True'
            )
    if not is_overload_none(tolerance):
        raise BodoError(
            'merge_asof(): tolerance parameter only supports default value None'
            )
    if not is_overload_none(by):
        raise BodoError(
            'merge_asof(): by parameter only supports default value None')
    if not is_overload_none(left_by):
        raise BodoError(
            'merge_asof(): left_by parameter only supports default value None')
    if not is_overload_none(right_by):
        raise BodoError(
            'merge_asof(): right_by parameter only supports default value None'
            )
    if not is_overload_constant_str(direction):
        raise BodoError(
            'merge_asof(): direction parameter should be of type str')
    else:
        direction = get_overload_const_str(direction)
        if direction != 'backward':
            raise BodoError(
                "merge_asof(): direction parameter only supports default value 'backward'"
                )


def validate_merge_asof_keys_length(left_on, right_on, left_index,
    right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if not is_overload_none(left_on) and is_overload_true(right_index):
        raise BodoError(
            'merge(): right_index = True and specifying left_on is not suppported yet.'
            )
    if not is_overload_none(right_on) and is_overload_true(left_index):
        raise BodoError(
            'merge(): left_index = True and specifying right_on is not suppported yet.'
            )


def validate_keys_length(left_index, right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if is_overload_true(right_index):
        if len(left_keys) != 1:
            raise BodoError(
                'merge(): len(left_on) must equal the number of levels in the index of "right", which is 1'
                )
    if is_overload_true(left_index):
        if len(right_keys) != 1:
            raise BodoError(
                'merge(): len(right_on) must equal the number of levels in the index of "left", which is 1'
                )


def validate_keys_dtypes(left, right, left_index, right_index, left_keys,
    right_keys):
    myvew__jbzg = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            katfk__tryw = left.index
            pigff__wyqr = isinstance(katfk__tryw, StringIndexType)
            kyjth__gnwu = right.index
            fvdtm__nby = isinstance(kyjth__gnwu, StringIndexType)
        elif is_overload_true(left_index):
            katfk__tryw = left.index
            pigff__wyqr = isinstance(katfk__tryw, StringIndexType)
            kyjth__gnwu = right.data[right.columns.index(right_keys[0])]
            fvdtm__nby = kyjth__gnwu.dtype == string_type
        elif is_overload_true(right_index):
            katfk__tryw = left.data[left.columns.index(left_keys[0])]
            pigff__wyqr = katfk__tryw.dtype == string_type
            kyjth__gnwu = right.index
            fvdtm__nby = isinstance(kyjth__gnwu, StringIndexType)
        if pigff__wyqr and fvdtm__nby:
            return
        katfk__tryw = katfk__tryw.dtype
        kyjth__gnwu = kyjth__gnwu.dtype
        try:
            ogjw__xcgv = myvew__jbzg.resolve_function_type(operator.eq, (
                katfk__tryw, kyjth__gnwu), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=katfk__tryw, rk_dtype=kyjth__gnwu))
    else:
        for pkg__bpnnj, kfx__qfgej in zip(left_keys, right_keys):
            katfk__tryw = left.data[left.columns.index(pkg__bpnnj)].dtype
            fch__cgk = left.data[left.columns.index(pkg__bpnnj)]
            kyjth__gnwu = right.data[right.columns.index(kfx__qfgej)].dtype
            ibro__ojdji = right.data[right.columns.index(kfx__qfgej)]
            if fch__cgk == ibro__ojdji:
                continue
            byrl__lgdl = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=pkg__bpnnj, lk_dtype=katfk__tryw, rk=kfx__qfgej,
                rk_dtype=kyjth__gnwu))
            qbj__qkwju = katfk__tryw == string_type
            mxvhf__qpjc = kyjth__gnwu == string_type
            if qbj__qkwju ^ mxvhf__qpjc:
                raise_bodo_error(byrl__lgdl)
            try:
                ogjw__xcgv = myvew__jbzg.resolve_function_type(operator.eq,
                    (katfk__tryw, kyjth__gnwu), {})
            except:
                raise_bodo_error(byrl__lgdl)


def validate_keys(keys, df):
    qognj__reebg = set(keys).difference(set(df.columns))
    if len(qognj__reebg) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in qognj__reebg:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {qognj__reebg} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    srkse__piqbl = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    ozep__ktph = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort)
    how = get_overload_const_str(how)
    if not is_overload_none(on):
        left_keys = get_overload_const_list(on)
    else:
        left_keys = ['$_bodo_index_']
    right_keys = ['$_bodo_index_']
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    ccv__mvv = "def _impl(left, other, on=None, how='left',\n"
    ccv__mvv += "    lsuffix='', rsuffix='', sort=False):\n"
    ccv__mvv += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo}, sczhi__csetf)
    _impl = sczhi__csetf['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        rnm__pvlq = get_overload_const_list(on)
        validate_keys(rnm__pvlq, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    wge__usxn = tuple(set(left.columns) & set(other.columns))
    if len(wge__usxn) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=wge__usxn))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    egr__znra = set(left_keys) & set(right_keys)
    ztiu__hsxx = set(left_columns) & set(right_columns)
    zwii__fxbnv = ztiu__hsxx - egr__znra
    fjm__wmg = set(left_columns) - ztiu__hsxx
    vmgrf__elt = set(right_columns) - ztiu__hsxx
    xawcr__sozei = {}

    def insertOutColumn(col_name):
        if col_name in xawcr__sozei:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        xawcr__sozei[col_name] = 0
    for vcmh__sqtib in egr__znra:
        insertOutColumn(vcmh__sqtib)
    for vcmh__sqtib in zwii__fxbnv:
        wgblr__tng = str(vcmh__sqtib) + suffix_x
        ihz__kktce = str(vcmh__sqtib) + suffix_y
        insertOutColumn(wgblr__tng)
        insertOutColumn(ihz__kktce)
    for vcmh__sqtib in fjm__wmg:
        insertOutColumn(vcmh__sqtib)
    for vcmh__sqtib in vmgrf__elt:
        insertOutColumn(vcmh__sqtib)
    if indicator_val:
        insertOutColumn('_merge')


@overload(pd.merge_asof, inline='always', no_unliteral=True)
def overload_dataframe_merge_asof(left, right, on=None, left_on=None,
    right_on=None, left_index=False, right_index=False, by=None, left_by=
    None, right_by=None, suffixes=('_x', '_y'), tolerance=None,
    allow_exact_matches=True, direction='backward'):
    raise BodoError('pandas.merge_asof() not support yet')
    validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
        right_index, by, left_by, right_by, suffixes, tolerance,
        allow_exact_matches, direction)
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError('merge_asof() requires dataframe inputs')
    wge__usxn = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = wge__usxn
        right_keys = wge__usxn
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    validate_merge_asof_keys_length(left_on, right_on, left_index,
        right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    if isinstance(suffixes, tuple):
        ajxdn__apmwk = suffixes
    if is_overload_constant_list(suffixes):
        ajxdn__apmwk = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        ajxdn__apmwk = suffixes.value
    suffix_x = ajxdn__apmwk[0]
    suffix_y = ajxdn__apmwk[1]
    ccv__mvv = 'def _impl(left, right, on=None, left_on=None, right_on=None,\n'
    ccv__mvv += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    ccv__mvv += "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n"
    ccv__mvv += "    allow_exact_matches=True, direction='backward'):\n"
    ccv__mvv += '  suffix_x = suffixes[0]\n'
    ccv__mvv += '  suffix_y = suffixes[1]\n'
    ccv__mvv += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo}, sczhi__csetf)
    _impl = sczhi__csetf['_impl']
    return _impl


@overload_method(DataFrameType, 'groupby', inline='always', no_unliteral=True)
def overload_dataframe_groupby(df, by=None, axis=0, level=None, as_index=
    True, sort=False, group_keys=True, squeeze=False, observed=True, dropna
    =True):
    check_runtime_cols_unsupported(df, 'DataFrame.groupby()')
    validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
        squeeze, observed, dropna)

    def _impl(df, by=None, axis=0, level=None, as_index=True, sort=False,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        return bodo.hiframes.pd_groupby_ext.init_groupby(df, by, as_index,
            dropna)
    return _impl


def validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
    squeeze, observed, dropna):
    if is_overload_none(by):
        raise BodoError("groupby(): 'by' must be supplied.")
    if not is_overload_zero(axis):
        raise BodoError(
            "groupby(): 'axis' parameter only supports integer value 0.")
    if not is_overload_none(level):
        raise BodoError(
            "groupby(): 'level' is not supported since MultiIndex is not supported."
            )
    if not is_literal_type(by) and not is_overload_constant_list(by):
        raise_bodo_error(
            f"groupby(): 'by' parameter only supports a constant column label or column labels, not {by}."
            )
    if len(set(get_overload_const_list(by)).difference(set(df.columns))) > 0:
        raise_bodo_error(
            "groupby(): invalid key {} for 'by' (not available in columns {})."
            .format(get_overload_const_list(by), df.columns))
    if not is_overload_constant_bool(as_index):
        raise_bodo_error(
            "groupby(): 'as_index' parameter must be a constant bool, not {}."
            .format(as_index))
    if not is_overload_constant_bool(dropna):
        raise_bodo_error(
            "groupby(): 'dropna' parameter must be a constant bool, not {}."
            .format(dropna))
    srkse__piqbl = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    thg__gxmwl = dict(sort=False, group_keys=True, squeeze=False, observed=True
        )
    check_unsupported_args('Dataframe.groupby', srkse__piqbl, thg__gxmwl,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    wuyi__evjv = func_name == 'DataFrame.pivot_table'
    if wuyi__evjv:
        if is_overload_none(index) or not is_literal_type(index):
            raise_bodo_error(
                f"DataFrame.pivot_table(): 'index' argument is required and must be constant column labels"
                )
    elif not is_overload_none(index) and not is_literal_type(index):
        raise_bodo_error(
            f"{func_name}(): if 'index' argument is provided it must be constant column labels"
            )
    if is_overload_none(columns) or not is_literal_type(columns):
        raise_bodo_error(
            f"{func_name}(): 'columns' argument is required and must be a constant column label"
            )
    if not is_overload_none(values) and not is_literal_type(values):
        raise_bodo_error(
            f"{func_name}(): if 'values' argument is provided it must be constant column labels"
            )
    aicwm__zyk = get_literal_value(columns)
    if isinstance(aicwm__zyk, (list, tuple)):
        if len(aicwm__zyk) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {aicwm__zyk}"
                )
        aicwm__zyk = aicwm__zyk[0]
    if aicwm__zyk not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {aicwm__zyk} not found in DataFrame {df}."
            )
    con__pri = df.column_index[aicwm__zyk]
    if is_overload_none(index):
        lyd__hhixm = []
        ogfyg__zhq = []
    else:
        ogfyg__zhq = get_literal_value(index)
        if not isinstance(ogfyg__zhq, (list, tuple)):
            ogfyg__zhq = [ogfyg__zhq]
        lyd__hhixm = []
        for index in ogfyg__zhq:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            lyd__hhixm.append(df.column_index[index])
    if not (all(isinstance(ueo__ags, int) for ueo__ags in ogfyg__zhq) or
        all(isinstance(ueo__ags, str) for ueo__ags in ogfyg__zhq)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        qtjt__kqddf = []
        mesa__bqkd = []
        mzyc__vwwmi = lyd__hhixm + [con__pri]
        for i, ueo__ags in enumerate(df.columns):
            if i not in mzyc__vwwmi:
                qtjt__kqddf.append(i)
                mesa__bqkd.append(ueo__ags)
    else:
        mesa__bqkd = get_literal_value(values)
        if not isinstance(mesa__bqkd, (list, tuple)):
            mesa__bqkd = [mesa__bqkd]
        qtjt__kqddf = []
        for val in mesa__bqkd:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            qtjt__kqddf.append(df.column_index[val])
    pijd__xcbbz = set(qtjt__kqddf) | set(lyd__hhixm) | {con__pri}
    if len(pijd__xcbbz) != len(qtjt__kqddf) + len(lyd__hhixm) + 1:
        raise BodoError(
            f"{func_name}(): 'index', 'columns', and 'values' must all refer to different columns"
            )

    def check_valid_index_typ(index_column):
        if isinstance(index_column, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType, bodo.
            IntervalArrayType)):
            raise BodoError(
                f"{func_name}(): 'index' DataFrame column must have scalar rows"
                )
        if isinstance(index_column, bodo.CategoricalArrayType):
            raise BodoError(
                f"{func_name}(): 'index' DataFrame column does not support categorical data"
                )
    if len(lyd__hhixm) == 0:
        index = df.index
        if isinstance(index, MultiIndexType):
            raise BodoError(
                f"{func_name}(): 'index' cannot be None with a DataFrame with a multi-index"
                )
        if not isinstance(index, RangeIndexType):
            check_valid_index_typ(index.data)
        if not is_literal_type(df.index.name_typ):
            raise BodoError(
                f"{func_name}(): If 'index' is None, the name of the DataFrame's Index must be constant at compile-time"
                )
    else:
        for kiwf__mdx in lyd__hhixm:
            index_column = df.data[kiwf__mdx]
            check_valid_index_typ(index_column)
    llf__xbkne = df.data[con__pri]
    if isinstance(llf__xbkne, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(llf__xbkne, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for yvnlf__bakn in qtjt__kqddf:
        rdebk__tmjs = df.data[yvnlf__bakn]
        if isinstance(rdebk__tmjs, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or rdebk__tmjs == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return (ogfyg__zhq, aicwm__zyk, mesa__bqkd, lyd__hhixm, con__pri,
        qtjt__kqddf)


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    ogfyg__zhq, aicwm__zyk, mesa__bqkd, kiwf__mdx, con__pri, prl__bzf = (
        pivot_error_checking(data, index, columns, values, 'DataFrame.pivot'))
    if len(ogfyg__zhq) == 0:
        if is_overload_none(data.index.name_typ):
            kjx__auc = None,
        else:
            kjx__auc = get_literal_value(data.index.name_typ),
    else:
        kjx__auc = tuple(ogfyg__zhq)
    ogfyg__zhq = ColNamesMetaType(kjx__auc)
    mesa__bqkd = ColNamesMetaType(tuple(mesa__bqkd))
    aicwm__zyk = ColNamesMetaType((aicwm__zyk,))
    ccv__mvv = 'def impl(data, index=None, columns=None, values=None):\n'
    ccv__mvv += f'    pivot_values = data.iloc[:, {con__pri}].unique()\n'
    ccv__mvv += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(kiwf__mdx) == 0:
        ccv__mvv += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        ccv__mvv += '        (\n'
        for jjh__wncit in kiwf__mdx:
            ccv__mvv += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {jjh__wncit}),
"""
        ccv__mvv += '        ),\n'
    ccv__mvv += (
        f'        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {con__pri}),),\n'
        )
    ccv__mvv += '        (\n'
    for yvnlf__bakn in prl__bzf:
        ccv__mvv += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {yvnlf__bakn}),
"""
    ccv__mvv += '        ),\n'
    ccv__mvv += '        pivot_values,\n'
    ccv__mvv += '        index_lit,\n'
    ccv__mvv += '        columns_lit,\n'
    ccv__mvv += '        values_lit,\n'
    ccv__mvv += '    )\n'
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo, 'index_lit': ogfyg__zhq, 'columns_lit':
        aicwm__zyk, 'values_lit': mesa__bqkd}, sczhi__csetf)
    impl = sczhi__csetf['impl']
    return impl


@overload(pd.pivot_table, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot_table', inline='always',
    no_unliteral=True)
def overload_dataframe_pivot_table(data, values=None, index=None, columns=
    None, aggfunc='mean', fill_value=None, margins=False, dropna=True,
    margins_name='All', observed=False, sort=True, _pivot_values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot_table()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot_table()')
    srkse__piqbl = dict(fill_value=fill_value, margins=margins, dropna=
        dropna, margins_name=margins_name, observed=observed, sort=sort)
    ozep__ktph = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', srkse__piqbl,
        ozep__ktph, package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    ogfyg__zhq, aicwm__zyk, mesa__bqkd, kiwf__mdx, con__pri, prl__bzf = (
        pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    spqv__jqd = ogfyg__zhq
    ogfyg__zhq = ColNamesMetaType(tuple(ogfyg__zhq))
    mesa__bqkd = ColNamesMetaType(tuple(mesa__bqkd))
    kfqpf__ntumc = aicwm__zyk
    aicwm__zyk = ColNamesMetaType((aicwm__zyk,))
    ccv__mvv = 'def impl(\n'
    ccv__mvv += '    data,\n'
    ccv__mvv += '    values=None,\n'
    ccv__mvv += '    index=None,\n'
    ccv__mvv += '    columns=None,\n'
    ccv__mvv += '    aggfunc="mean",\n'
    ccv__mvv += '    fill_value=None,\n'
    ccv__mvv += '    margins=False,\n'
    ccv__mvv += '    dropna=True,\n'
    ccv__mvv += '    margins_name="All",\n'
    ccv__mvv += '    observed=False,\n'
    ccv__mvv += '    sort=True,\n'
    ccv__mvv += '    _pivot_values=None,\n'
    ccv__mvv += '):\n'
    kdo__rwkgt = kiwf__mdx + [con__pri] + prl__bzf
    ccv__mvv += f'    data = data.iloc[:, {kdo__rwkgt}]\n'
    fnhkn__yypqb = spqv__jqd + [kfqpf__ntumc]
    if not is_overload_none(_pivot_values):
        wik__oklke = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(wik__oklke)
        ccv__mvv += '    pivot_values = _pivot_values_arr\n'
        ccv__mvv += (
            f'    data = data[data.iloc[:, {len(kiwf__mdx)}].isin(pivot_values)]\n'
            )
        if all(isinstance(ueo__ags, str) for ueo__ags in wik__oklke):
            lpejg__veqd = pd.array(wik__oklke, 'string')
        elif all(isinstance(ueo__ags, int) for ueo__ags in wik__oklke):
            lpejg__veqd = np.array(wik__oklke, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        lpejg__veqd = None
    ccv__mvv += (
        f'    data = data.groupby({fnhkn__yypqb!r}, as_index=False).agg(aggfunc)\n'
        )
    if is_overload_none(_pivot_values):
        ccv__mvv += (
            f'    pivot_values = data.iloc[:, {len(kiwf__mdx)}].unique()\n')
    ccv__mvv += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    ccv__mvv += '        (\n'
    for i in range(0, len(kiwf__mdx)):
        ccv__mvv += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    ccv__mvv += '        ),\n'
    ccv__mvv += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(kiwf__mdx)}),),
"""
    ccv__mvv += '        (\n'
    for i in range(len(kiwf__mdx) + 1, len(prl__bzf) + len(kiwf__mdx) + 1):
        ccv__mvv += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    ccv__mvv += '        ),\n'
    ccv__mvv += '        pivot_values,\n'
    ccv__mvv += '        index_lit,\n'
    ccv__mvv += '        columns_lit,\n'
    ccv__mvv += '        values_lit,\n'
    ccv__mvv += '        check_duplicates=False,\n'
    ccv__mvv += '        _constant_pivot_values=_constant_pivot_values,\n'
    ccv__mvv += '    )\n'
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo, 'numba': numba, 'index_lit': ogfyg__zhq,
        'columns_lit': aicwm__zyk, 'values_lit': mesa__bqkd,
        '_pivot_values_arr': lpejg__veqd, '_constant_pivot_values':
        _pivot_values}, sczhi__csetf)
    impl = sczhi__csetf['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    srkse__piqbl = dict(col_level=col_level, ignore_index=ignore_index)
    ozep__ktph = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(frame, DataFrameType):
        raise BodoError("pandas.melt(): 'frame' argument must be a DataFrame.")
    if not is_overload_none(id_vars) and not is_literal_type(id_vars):
        raise_bodo_error(
            "DataFrame.melt(): 'id_vars', if specified, must be a literal.")
    if not is_overload_none(value_vars) and not is_literal_type(value_vars):
        raise_bodo_error(
            "DataFrame.melt(): 'value_vars', if specified, must be a literal.")
    if not is_overload_none(var_name) and not (is_literal_type(var_name) and
        (is_scalar_type(var_name) or isinstance(value_name, types.Omitted))):
        raise_bodo_error(
            "DataFrame.melt(): 'var_name', if specified, must be a literal.")
    if value_name != 'value' and not (is_literal_type(value_name) and (
        is_scalar_type(value_name) or isinstance(value_name, types.Omitted))):
        raise_bodo_error(
            "DataFrame.melt(): 'value_name', if specified, must be a literal.")
    var_name = get_literal_value(var_name) if not is_overload_none(var_name
        ) else 'variable'
    value_name = get_literal_value(value_name
        ) if value_name != 'value' else 'value'
    ypl__ruyp = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(ypl__ruyp, (list, tuple)):
        ypl__ruyp = [ypl__ruyp]
    for ueo__ags in ypl__ruyp:
        if ueo__ags not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {ueo__ags} not found in {frame}."
                )
    trgss__ajc = [frame.column_index[i] for i in ypl__ruyp]
    if is_overload_none(value_vars):
        wkhgm__grhez = []
        apwcz__ngrm = []
        for i, ueo__ags in enumerate(frame.columns):
            if i not in trgss__ajc:
                wkhgm__grhez.append(i)
                apwcz__ngrm.append(ueo__ags)
    else:
        apwcz__ngrm = get_literal_value(value_vars)
        if not isinstance(apwcz__ngrm, (list, tuple)):
            apwcz__ngrm = [apwcz__ngrm]
        apwcz__ngrm = [v for v in apwcz__ngrm if v not in ypl__ruyp]
        if not apwcz__ngrm:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        wkhgm__grhez = []
        for val in apwcz__ngrm:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            wkhgm__grhez.append(frame.column_index[val])
    for ueo__ags in apwcz__ngrm:
        if ueo__ags not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {ueo__ags} not found in {frame}."
                )
    if not (all(isinstance(ueo__ags, int) for ueo__ags in apwcz__ngrm) or
        all(isinstance(ueo__ags, str) for ueo__ags in apwcz__ngrm)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    ybs__xooqi = frame.data[wkhgm__grhez[0]]
    iez__ivk = [frame.data[i].dtype for i in wkhgm__grhez]
    wkhgm__grhez = np.array(wkhgm__grhez, dtype=np.int64)
    trgss__ajc = np.array(trgss__ajc, dtype=np.int64)
    _, odm__jyh = bodo.utils.typing.get_common_scalar_dtype(iez__ivk)
    if not odm__jyh:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': apwcz__ngrm, 'val_type': ybs__xooqi
        }
    header = 'def impl(\n'
    header += '  frame,\n'
    header += '  id_vars=None,\n'
    header += '  value_vars=None,\n'
    header += '  var_name=None,\n'
    header += "  value_name='value',\n"
    header += '  col_level=None,\n'
    header += '  ignore_index=True,\n'
    header += '):\n'
    header += (
        '  dummy_id = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, 0)\n'
        )
    if frame.is_table_format and all(v == ybs__xooqi.dtype for v in iez__ivk):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            wkhgm__grhez))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(apwcz__ngrm) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {wkhgm__grhez[0]})
"""
    else:
        akxzp__kzw = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in wkhgm__grhez)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({akxzp__kzw},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in trgss__ajc:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(apwcz__ngrm)})\n'
            )
    vaq__kncz = ', '.join(f'out_id{i}' for i in trgss__ajc) + (', ' if len(
        trgss__ajc) > 0 else '')
    data_args = vaq__kncz + 'var_col, val_col'
    columns = tuple(ypl__ruyp + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(apwcz__ngrm)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    srkse__piqbl = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    ozep__ktph = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(index,
        'pandas.crosstab()')
    if not isinstance(index, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'index' argument only supported for Series types, found {index}"
            )
    if not isinstance(columns, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'columns' argument only supported for Series types, found {columns}"
            )

    def _impl(index, columns, values=None, rownames=None, colnames=None,
        aggfunc=None, margins=False, margins_name='All', dropna=True,
        normalize=False, _pivot_values=None):
        return bodo.hiframes.pd_groupby_ext.crosstab_dummy(index, columns,
            _pivot_values)
    return _impl


@overload_method(DataFrameType, 'sort_values', inline='always',
    no_unliteral=True)
def overload_dataframe_sort_values(df, by, axis=0, ascending=True, inplace=
    False, kind='quicksort', na_position='last', ignore_index=False, key=
    None, _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_values()')
    srkse__piqbl = dict(ignore_index=ignore_index, key=key)
    ozep__ktph = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', srkse__piqbl,
        ozep__ktph, package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'sort_values')
    validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
        na_position)

    def _impl(df, by, axis=0, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', ignore_index=False, key=None,
        _bodo_transformed=False):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df, by,
            ascending, inplace, na_position)
    return _impl


def validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
    na_position):
    if is_overload_none(by) or not is_literal_type(by
        ) and not is_overload_constant_list(by):
        raise_bodo_error(
            "sort_values(): 'by' parameter only supports a constant column label or column labels. by={}"
            .format(by))
    byorp__qxdl = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        byorp__qxdl.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        zsu__xbg = [get_overload_const_tuple(by)]
    else:
        zsu__xbg = get_overload_const_list(by)
    zsu__xbg = set((k, '') if (k, '') in byorp__qxdl else k for k in zsu__xbg)
    if len(zsu__xbg.difference(byorp__qxdl)) > 0:
        par__pvjp = list(set(get_overload_const_list(by)).difference(
            byorp__qxdl))
        raise_bodo_error(f'sort_values(): invalid keys {par__pvjp} for by.')
    if not is_overload_zero(axis):
        raise_bodo_error(
            "sort_values(): 'axis' parameter only supports integer value 0.")
    if not is_overload_bool(ascending) and not is_overload_bool_list(ascending
        ):
        raise_bodo_error(
            "sort_values(): 'ascending' parameter must be of type bool or list of bool, not {}."
            .format(ascending))
    if not is_overload_bool(inplace):
        raise_bodo_error(
            "sort_values(): 'inplace' parameter must be of type bool, not {}."
            .format(inplace))
    if kind != 'quicksort' and not isinstance(kind, types.Omitted):
        warnings.warn(BodoWarning(
            'sort_values(): specifying sorting algorithm is not supported in Bodo. Bodo uses stable sort.'
            ))
    if is_overload_constant_str(na_position):
        na_position = get_overload_const_str(na_position)
        if na_position not in ('first', 'last'):
            raise BodoError(
                "sort_values(): na_position should either be 'first' or 'last'"
                )
    elif is_overload_constant_list(na_position):
        lgqe__olegq = get_overload_const_list(na_position)
        for na_position in lgqe__olegq:
            if na_position not in ('first', 'last'):
                raise BodoError(
                    "sort_values(): Every value in na_position should either be 'first' or 'last'"
                    )
    else:
        raise_bodo_error(
            f'sort_values(): na_position parameter must be a literal constant of type str or a constant list of str with 1 entry per key column, not {na_position}'
            )
    na_position = get_overload_const_str(na_position)
    if na_position not in ['first', 'last']:
        raise BodoError(
            "sort_values(): na_position should either be 'first' or 'last'")


@overload_method(DataFrameType, 'sort_index', inline='always', no_unliteral
    =True)
def overload_dataframe_sort_index(df, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_index()')
    srkse__piqbl = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    ozep__ktph = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_bool(ascending):
        raise BodoError(
            "DataFrame.sort_index(): 'ascending' parameter must be of type bool"
            )
    if not is_overload_bool(inplace):
        raise BodoError(
            "DataFrame.sort_index(): 'inplace' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "DataFrame.sort_index(): 'na_position' should either be 'first' or 'last'"
            )

    def _impl(df, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df,
            '$_bodo_index_', ascending, inplace, na_position)
    return _impl


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    srkse__piqbl = dict(limit=limit, downcast=downcast)
    ozep__ktph = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    kbnvu__qfvs = not is_overload_none(value)
    oedzj__kkxy = not is_overload_none(method)
    if kbnvu__qfvs and oedzj__kkxy:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not kbnvu__qfvs and not oedzj__kkxy:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if kbnvu__qfvs:
        rsysa__djxm = 'value=value'
    else:
        rsysa__djxm = 'method=method'
    data_args = [(
        f"df['{ueo__ags}'].fillna({rsysa__djxm}, inplace=inplace)" if
        isinstance(ueo__ags, str) else
        f'df[{ueo__ags}].fillna({rsysa__djxm}, inplace=inplace)') for
        ueo__ags in df.columns]
    ccv__mvv = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        ccv__mvv += '  ' + '  \n'.join(data_args) + '\n'
        sczhi__csetf = {}
        exec(ccv__mvv, {}, sczhi__csetf)
        impl = sczhi__csetf['impl']
        return impl
    else:
        return _gen_init_df(ccv__mvv, df.columns, ', '.join(rzygd__crlxs +
            '.values' for rzygd__crlxs in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    srkse__piqbl = dict(col_level=col_level, col_fill=col_fill)
    ozep__ktph = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', srkse__piqbl,
        ozep__ktph, package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'reset_index')
    if not _is_all_levels(df, level):
        raise_bodo_error(
            'DataFrame.reset_index(): only dropping all index levels supported'
            )
    if not is_overload_constant_bool(drop):
        raise BodoError(
            "DataFrame.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.reset_index(): 'inplace' parameter should be a constant boolean value"
            )
    ccv__mvv = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    ccv__mvv += (
        '  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(df), 1, None)\n'
        )
    drop = is_overload_true(drop)
    inplace = is_overload_true(inplace)
    columns = df.columns
    data_args = [
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}\n'.
        format(i, '' if inplace else '.copy()') for i in range(len(df.columns))
        ]
    if not drop:
        rfkt__xtrm = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            rfkt__xtrm)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            ccv__mvv += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            loury__jrftm = ['m_index[{}]'.format(i) for i in range(df.index
                .nlevels)]
            data_args = loury__jrftm + data_args
        else:
            pvip__jqu = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [pvip__jqu] + data_args
    return _gen_init_df(ccv__mvv, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    wlumx__mtmab = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and wlumx__mtmab == 1 or is_overload_constant_list(level
        ) and list(get_overload_const_list(level)) == list(range(wlumx__mtmab))


@overload_method(DataFrameType, 'dropna', inline='always', no_unliteral=True)
def overload_dataframe_dropna(df, axis=0, how='any', thresh=None, subset=
    None, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.dropna()')
    if not is_overload_constant_bool(inplace) or is_overload_true(inplace):
        raise BodoError('DataFrame.dropna(): inplace=True is not supported')
    if not is_overload_zero(axis):
        raise_bodo_error(f'df.dropna(): only axis=0 supported')
    ensure_constant_values('dropna', 'how', how, ('any', 'all'))
    if is_overload_none(subset):
        pxcpt__rlque = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        ottds__qbh = get_overload_const_list(subset)
        pxcpt__rlque = []
        for mhe__yfpa in ottds__qbh:
            if mhe__yfpa not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{mhe__yfpa}' not in data frame columns {df}"
                    )
            pxcpt__rlque.append(df.column_index[mhe__yfpa])
    rcnvi__fvf = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(rcnvi__fvf))
    ccv__mvv = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(rcnvi__fvf):
        ccv__mvv += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    ccv__mvv += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in pxcpt__rlque)))
    ccv__mvv += '  index = bodo.utils.conversion.index_from_array(index_arr)\n'
    return _gen_init_df(ccv__mvv, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    srkse__piqbl = dict(index=index, level=level, errors=errors)
    ozep__ktph = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', srkse__piqbl, ozep__ktph,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'drop')
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "DataFrame.drop(): 'inplace' parameter should be a constant bool")
    if not is_overload_none(labels):
        if not is_overload_none(columns):
            raise BodoError(
                "Dataframe.drop(): Cannot specify both 'labels' and 'columns'")
        if not is_overload_constant_int(axis) or get_overload_const_int(axis
            ) != 1:
            raise_bodo_error('DataFrame.drop(): only axis=1 supported')
        if is_overload_constant_str(labels):
            xdr__kix = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            xdr__kix = get_overload_const_list(labels)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    else:
        if is_overload_none(columns):
            raise BodoError(
                "DataFrame.drop(): Need to specify at least one of 'labels' or 'columns'"
                )
        if is_overload_constant_str(columns):
            xdr__kix = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            xdr__kix = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for ueo__ags in xdr__kix:
        if ueo__ags not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(ueo__ags, df.columns))
    if len(set(xdr__kix)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    rjluu__fzndx = tuple(ueo__ags for ueo__ags in df.columns if ueo__ags not in
        xdr__kix)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[ueo__ags], '.copy()' if not inplace else '') for
        ueo__ags in rjluu__fzndx)
    ccv__mvv = 'def impl(df, labels=None, axis=0, index=None, columns=None,\n'
    ccv__mvv += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(ccv__mvv, rjluu__fzndx, data_args, index)


@overload_method(DataFrameType, 'append', inline='always', no_unliteral=True)
def overload_dataframe_append(df, other, ignore_index=False,
    verify_integrity=False, sort=None):
    check_runtime_cols_unsupported(df, 'DataFrame.append()')
    check_runtime_cols_unsupported(other, 'DataFrame.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'DataFrame.append()')
    if isinstance(other, DataFrameType):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df, other), ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.BaseTuple):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df,) + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.List) and isinstance(other.dtype, DataFrameType
        ):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat([df] + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    raise BodoError(
        'invalid df.append() input. Only dataframe and list/tuple of dataframes supported'
        )


@overload_method(DataFrameType, 'sample', inline='always', no_unliteral=True)
def overload_dataframe_sample(df, n=None, frac=None, replace=False, weights
    =None, random_state=None, axis=None, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sample()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sample()')
    srkse__piqbl = dict(random_state=random_state, weights=weights, axis=
        axis, ignore_index=ignore_index)
    xrun__eziyr = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', srkse__piqbl, xrun__eziyr,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    rcnvi__fvf = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(rcnvi__fvf))
    dxnl__hrr = ', '.join('rhs_data_{}'.format(i) for i in range(rcnvi__fvf))
    ccv__mvv = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    ccv__mvv += '  if (frac == 1 or n == len(df)) and not replace:\n'
    ccv__mvv += '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n'
    for i in range(rcnvi__fvf):
        ccv__mvv += (
            '  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    ccv__mvv += '  if frac is None:\n'
    ccv__mvv += '    frac_d = -1.0\n'
    ccv__mvv += '  else:\n'
    ccv__mvv += '    frac_d = frac\n'
    ccv__mvv += '  if n is None:\n'
    ccv__mvv += '    n_i = 0\n'
    ccv__mvv += '  else:\n'
    ccv__mvv += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    ccv__mvv += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({dxnl__hrr},), {index}, n_i, frac_d, replace)
"""
    ccv__mvv += '  index = bodo.utils.conversion.index_from_array(index_arr)\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(ccv__mvv, df.columns,
        data_args, 'index')


@numba.njit
def _sizeof_fmt(num, size_qualifier=''):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f'{num:3.1f}{size_qualifier} {x}'
        num /= 1024.0
    return f'{num:3.1f}{size_qualifier} PB'


@overload_method(DataFrameType, 'info', no_unliteral=True)
def overload_dataframe_info(df, verbose=None, buf=None, max_cols=None,
    memory_usage=None, show_counts=None, null_counts=None):
    check_runtime_cols_unsupported(df, 'DataFrame.info()')
    nitc__wbulg = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    vuvmw__ttktr = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', nitc__wbulg, vuvmw__ttktr,
        package_name='pandas', module_name='DataFrame')
    ieps__ggwt = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            hin__rflu = ieps__ggwt + '\n'
            hin__rflu += 'Index: 0 entries\n'
            hin__rflu += 'Empty DataFrame'
            print(hin__rflu)
        return _info_impl
    else:
        ccv__mvv = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        ccv__mvv += '    ncols = df.shape[1]\n'
        ccv__mvv += f'    lines = "{ieps__ggwt}\\n"\n'
        ccv__mvv += f'    lines += "{df.index}: "\n'
        ccv__mvv += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            ccv__mvv += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            ccv__mvv += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            ccv__mvv += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        ccv__mvv += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        ccv__mvv += f'    space = {max(len(str(k)) for k in df.columns) + 1}\n'
        ccv__mvv += '    column_width = max(space, 7)\n'
        ccv__mvv += '    column= "Column"\n'
        ccv__mvv += '    underl= "------"\n'
        ccv__mvv += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        ccv__mvv += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        ccv__mvv += '    mem_size = 0\n'
        ccv__mvv += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        ccv__mvv += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        ccv__mvv += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        lgji__qqk = dict()
        for i in range(len(df.columns)):
            ccv__mvv += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            hxp__mrkj = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                hxp__mrkj = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                wrlzf__tqpm = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                hxp__mrkj = f'{wrlzf__tqpm[:-7]}'
            ccv__mvv += f'    col_dtype[{i}] = "{hxp__mrkj}"\n'
            if hxp__mrkj in lgji__qqk:
                lgji__qqk[hxp__mrkj] += 1
            else:
                lgji__qqk[hxp__mrkj] = 1
            ccv__mvv += f'    col_name[{i}] = "{df.columns[i]}"\n'
            ccv__mvv += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        ccv__mvv += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        ccv__mvv += '    for i in column_info:\n'
        ccv__mvv += "        lines += f'{i}\\n'\n"
        dlb__jny = ', '.join(f'{k}({lgji__qqk[k]})' for k in sorted(lgji__qqk))
        ccv__mvv += f"    lines += 'dtypes: {dlb__jny}\\n'\n"
        ccv__mvv += '    mem_size += df.index.nbytes\n'
        ccv__mvv += '    total_size = _sizeof_fmt(mem_size)\n'
        ccv__mvv += "    lines += f'memory usage: {total_size}'\n"
        ccv__mvv += '    print(lines)\n'
        sczhi__csetf = {}
        exec(ccv__mvv, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo': bodo,
            'np': np}, sczhi__csetf)
        _info_impl = sczhi__csetf['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    ccv__mvv = 'def impl(df, index=True, deep=False):\n'
    skxib__xvq = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes')
    zfs__ima = is_overload_true(index)
    columns = df.columns
    if zfs__ima:
        columns = ('Index',) + columns
    if len(columns) == 0:
        jnwgl__vrv = ()
    elif all(isinstance(ueo__ags, int) for ueo__ags in columns):
        jnwgl__vrv = np.array(columns, 'int64')
    elif all(isinstance(ueo__ags, str) for ueo__ags in columns):
        jnwgl__vrv = pd.array(columns, 'string')
    else:
        jnwgl__vrv = columns
    if df.is_table_format and len(df.columns) > 0:
        jopo__btjzu = int(zfs__ima)
        hpzhb__dqxs = len(columns)
        ccv__mvv += f'  nbytes_arr = np.empty({hpzhb__dqxs}, np.int64)\n'
        ccv__mvv += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        ccv__mvv += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {jopo__btjzu})
"""
        if zfs__ima:
            ccv__mvv += f'  nbytes_arr[0] = {skxib__xvq}\n'
        ccv__mvv += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if zfs__ima:
            data = f'{skxib__xvq},{data}'
        else:
            bpbpt__efyq = ',' if len(columns) == 1 else ''
            data = f'{data}{bpbpt__efyq}'
        ccv__mvv += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        jnwgl__vrv}, sczhi__csetf)
    impl = sczhi__csetf['impl']
    return impl


@overload(pd.read_excel, no_unliteral=True)
def overload_read_excel(io, sheet_name=0, header=0, names=None, index_col=
    None, usecols=None, squeeze=False, dtype=None, engine=None, converters=
    None, true_values=None, false_values=None, skiprows=None, nrows=None,
    na_values=None, keep_default_na=True, na_filter=True, verbose=False,
    parse_dates=False, date_parser=None, thousands=None, comment=None,
    skipfooter=0, convert_float=True, mangle_dupe_cols=True, _bodo_df_type=None
    ):
    df_type = _bodo_df_type.instance_type
    ija__ubipf = 'read_excel_df{}'.format(next_label())
    setattr(types, ija__ubipf, df_type)
    dluqx__ivh = False
    if is_overload_constant_list(parse_dates):
        dluqx__ivh = get_overload_const_list(parse_dates)
    rcr__hebh = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    ccv__mvv = f"""
def impl(
    io,
    sheet_name=0,
    header=0,
    names=None,
    index_col=None,
    usecols=None,
    squeeze=False,
    dtype=None,
    engine=None,
    converters=None,
    true_values=None,
    false_values=None,
    skiprows=None,
    nrows=None,
    na_values=None,
    keep_default_na=True,
    na_filter=True,
    verbose=False,
    parse_dates=False,
    date_parser=None,
    thousands=None,
    comment=None,
    skipfooter=0,
    convert_float=True,
    mangle_dupe_cols=True,
    _bodo_df_type=None,
):
    with numba.objmode(df="{ija__ubipf}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{rcr__hebh}}},
            engine=engine,
            converters=converters,
            true_values=true_values,
            false_values=false_values,
            skiprows=skiprows,
            nrows=nrows,
            na_values=na_values,
            keep_default_na=keep_default_na,
            na_filter=na_filter,
            verbose=verbose,
            parse_dates={dluqx__ivh},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    sczhi__csetf = {}
    exec(ccv__mvv, globals(), sczhi__csetf)
    impl = sczhi__csetf['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as zvh__hvtdu:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    ccv__mvv = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    ccv__mvv += '    ylabel=None, title=None, legend=True, fontsize=None, \n'
    ccv__mvv += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        ccv__mvv += '   fig, ax = plt.subplots()\n'
    else:
        ccv__mvv += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        ccv__mvv += '   fig.set_figwidth(figsize[0])\n'
        ccv__mvv += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        ccv__mvv += '   xlabel = x\n'
    ccv__mvv += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        ccv__mvv += '   ylabel = y\n'
    else:
        ccv__mvv += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        ccv__mvv += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        ccv__mvv += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    ccv__mvv += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            ccv__mvv += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            rmn__xoc = get_overload_const_str(x)
            mqj__zlb = df.columns.index(rmn__xoc)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if mqj__zlb != i:
                        ccv__mvv += (
                            f'   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])\n'
                            )
        else:
            ccv__mvv += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        ccv__mvv += '   ax.scatter(df[x], df[y], s=20)\n'
        ccv__mvv += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        ccv__mvv += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        ccv__mvv += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        ccv__mvv += '   ax.legend()\n'
    ccv__mvv += '   return ax\n'
    sczhi__csetf = {}
    exec(ccv__mvv, {'bodo': bodo, 'plt': plt}, sczhi__csetf)
    impl = sczhi__csetf['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for blcoz__thxw in df_typ.data:
        if not (isinstance(blcoz__thxw, IntegerArrayType) or isinstance(
            blcoz__thxw.dtype, types.Number) or blcoz__thxw.dtype in (bodo.
            datetime64ns, bodo.timedelta64ns)):
            return False
    return True


def typeref_to_type(v):
    if isinstance(v, types.BaseTuple):
        return types.BaseTuple.from_types(tuple(typeref_to_type(a) for a in v))
    return v.instance_type if isinstance(v, (types.TypeRef, types.NumberClass)
        ) else v


def _install_typer_for_type(type_name, typ):

    @type_callable(typ)
    def type_call_type(context):

        def typer(*args, **kws):
            args = tuple(typeref_to_type(v) for v in args)
            kws = {name: typeref_to_type(v) for name, v in kws.items()}
            return types.TypeRef(typ(*args, **kws))
        return typer
    no_side_effect_call_tuples.add((type_name, bodo))
    no_side_effect_call_tuples.add((typ,))


def _install_type_call_typers():
    for type_name in bodo_types_with_params:
        typ = getattr(bodo, type_name)
        _install_typer_for_type(type_name, typ)


_install_type_call_typers()


def set_df_col(df, cname, arr, inplace):
    df[cname] = arr


@infer_global(set_df_col)
class SetDfColInfer(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        assert not kws
        assert len(args) == 4
        assert isinstance(args[1], types.Literal)
        oon__ivfdh = args[0]
        fyti__diof = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        ghah__oct = oon__ivfdh
        check_runtime_cols_unsupported(oon__ivfdh, 'set_df_col()')
        if isinstance(oon__ivfdh, DataFrameType):
            index = oon__ivfdh.index
            if len(oon__ivfdh.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(oon__ivfdh.columns) == 0:
                    index = val.index
                val = val.data
            if is_pd_index_type(val):
                val = bodo.utils.typing.get_index_data_arr_types(val)[0]
            if isinstance(val, types.List):
                val = dtype_to_array_type(val.dtype)
            if not is_array_typ(val):
                val = dtype_to_array_type(val)
            if fyti__diof in oon__ivfdh.columns:
                rjluu__fzndx = oon__ivfdh.columns
                lehcm__hiqth = oon__ivfdh.columns.index(fyti__diof)
                doeq__tgtsh = list(oon__ivfdh.data)
                doeq__tgtsh[lehcm__hiqth] = val
                doeq__tgtsh = tuple(doeq__tgtsh)
            else:
                rjluu__fzndx = oon__ivfdh.columns + (fyti__diof,)
                doeq__tgtsh = oon__ivfdh.data + (val,)
            ghah__oct = DataFrameType(doeq__tgtsh, index, rjluu__fzndx,
                oon__ivfdh.dist, oon__ivfdh.is_table_format)
        return ghah__oct(*args)


SetDfColInfer.prefer_literal = True


def __bodosql_replace_columns_dummy(df, col_names_to_replace,
    cols_to_replace_with):
    for i in range(len(col_names_to_replace)):
        df[col_names_to_replace[i]] = cols_to_replace_with[i]


@infer_global(__bodosql_replace_columns_dummy)
class BodoSQLReplaceColsInfer(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        assert not kws
        assert len(args) == 3
        assert is_overload_constant_tuple(args[1])
        assert isinstance(args[2], types.BaseTuple)
        hhkr__rklk = args[0]
        assert isinstance(hhkr__rklk, DataFrameType) and len(hhkr__rklk.columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        ugn__btxc = args[2]
        assert len(col_names_to_replace) == len(ugn__btxc
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(hhkr__rklk.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in hhkr__rklk.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(hhkr__rklk,
            '__bodosql_replace_columns_dummy()')
        index = hhkr__rklk.index
        rjluu__fzndx = hhkr__rklk.columns
        doeq__tgtsh = list(hhkr__rklk.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            xdgx__nxf = ugn__btxc[i]
            assert isinstance(xdgx__nxf, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(xdgx__nxf, SeriesType):
                xdgx__nxf = xdgx__nxf.data
            coxm__acosx = hhkr__rklk.column_index[col_name]
            doeq__tgtsh[coxm__acosx] = xdgx__nxf
        doeq__tgtsh = tuple(doeq__tgtsh)
        ghah__oct = DataFrameType(doeq__tgtsh, index, rjluu__fzndx,
            hhkr__rklk.dist, hhkr__rklk.is_table_format)
        return ghah__oct(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    wgyzd__zwwv = {}

    def _rewrite_membership_op(self, node, left, right):
        yat__dbf = node.op
        op = self.visit(yat__dbf)
        return op, yat__dbf, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    ioxek__wdkuo = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in ioxek__wdkuo:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in ioxek__wdkuo:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        afp__inl = node.attr
        value = node.value
        kxjn__douua = pd.core.computation.ops.LOCAL_TAG
        if afp__inl in ('str', 'dt'):
            try:
                ydu__qburh = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as kyxu__esqr:
                col_name = kyxu__esqr.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            ydu__qburh = str(self.visit(value))
        cjfty__uyg = ydu__qburh, afp__inl
        if cjfty__uyg in join_cleaned_cols:
            afp__inl = join_cleaned_cols[cjfty__uyg]
        name = ydu__qburh + '.' + afp__inl
        if name.startswith(kxjn__douua):
            name = name[len(kxjn__douua):]
        if afp__inl in ('str', 'dt'):
            ptu__uiduz = columns[cleaned_columns.index(ydu__qburh)]
            wgyzd__zwwv[ptu__uiduz] = ydu__qburh
            self.env.scope[name] = 0
            return self.term_type(kxjn__douua + name, self.env)
        ioxek__wdkuo.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in ioxek__wdkuo:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        coki__emn = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        fyti__diof = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(coki__emn), fyti__diof))

    def op__str__(self):
        pfyo__izsx = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            kkq__vvoep)) for kkq__vvoep in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(pfyo__izsx)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(pfyo__izsx)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(pfyo__izsx))
    aywmm__etmmn = (pd.core.computation.expr.BaseExprVisitor.
        _rewrite_membership_op)
    bfr__xslp = pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop
    djwy__brmm = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    zcwis__tpr = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    dgohl__giu = pd.core.computation.ops.Term.__str__
    xavs__sbsqp = pd.core.computation.ops.MathCall.__str__
    uhm__sgp = pd.core.computation.ops.Op.__str__
    ihii__sgbpj = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
    try:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            _rewrite_membership_op)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            _maybe_evaluate_binop)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = (
            visit_Attribute)
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = lambda self, left, right: (left, right)
        pd.core.computation.ops.Term.__str__ = __str__
        pd.core.computation.ops.MathCall.__str__ = math__str__
        pd.core.computation.ops.Op.__str__ = op__str__
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        hjbru__jzom = pd.core.computation.expr.Expr(expr, env=env)
        uviyr__cxfp = str(hjbru__jzom)
    except pd.core.computation.ops.UndefinedVariableError as kyxu__esqr:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == kyxu__esqr.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {kyxu__esqr}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            aywmm__etmmn)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            bfr__xslp)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = djwy__brmm
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = zcwis__tpr
        pd.core.computation.ops.Term.__str__ = dgohl__giu
        pd.core.computation.ops.MathCall.__str__ = xavs__sbsqp
        pd.core.computation.ops.Op.__str__ = uhm__sgp
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            ihii__sgbpj)
    kqmmf__qlv = pd.core.computation.parsing.clean_column_name
    wgyzd__zwwv.update({ueo__ags: kqmmf__qlv(ueo__ags) for ueo__ags in
        columns if kqmmf__qlv(ueo__ags) in hjbru__jzom.names})
    return hjbru__jzom, uviyr__cxfp, wgyzd__zwwv


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        yvfoz__htwct = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(yvfoz__htwct))
        pbbt__ieyvi = namedtuple('Pandas', col_names)
        mvy__hwyf = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], pbbt__ieyvi)
        super(DataFrameTupleIterator, self).__init__(name, mvy__hwyf)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_series_dtype(arr_typ):
    if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
        return pd_timestamp_type
    return arr_typ.dtype


def get_itertuples():
    pass


@infer_global(get_itertuples)
class TypeIterTuples(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) % 2 == 0, 'name and column pairs expected'
        col_names = [a.literal_value for a in args[:len(args) // 2]]
        aqwwj__mimy = [if_series_to_array_type(a) for a in args[len(args) //
            2:]]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        aqwwj__mimy = [types.Array(types.int64, 1, 'C')] + aqwwj__mimy
        fqav__uyu = DataFrameTupleIterator(col_names, aqwwj__mimy)
        return fqav__uyu(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        kidrz__ssm = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            kidrz__ssm)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    znaup__ljvof = args[len(args) // 2:]
    smmqg__yesyb = sig.args[len(sig.args) // 2:]
    dgz__hhmc = context.make_helper(builder, sig.return_type)
    ckhgl__faw = context.get_constant(types.intp, 0)
    hobp__xqjx = cgutils.alloca_once_value(builder, ckhgl__faw)
    dgz__hhmc.index = hobp__xqjx
    for i, arr in enumerate(znaup__ljvof):
        setattr(dgz__hhmc, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(znaup__ljvof, smmqg__yesyb):
        context.nrt.incref(builder, arr_typ, arr)
    res = dgz__hhmc._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    kpwwp__ypoti, = sig.args
    epwrn__cnwpw, = args
    dgz__hhmc = context.make_helper(builder, kpwwp__ypoti, value=epwrn__cnwpw)
    fwv__dwjts = signature(types.intp, kpwwp__ypoti.array_types[1])
    xytb__uzk = context.compile_internal(builder, lambda a: len(a),
        fwv__dwjts, [dgz__hhmc.array0])
    index = builder.load(dgz__hhmc.index)
    npysu__aid = builder.icmp_signed('<', index, xytb__uzk)
    result.set_valid(npysu__aid)
    with builder.if_then(npysu__aid):
        values = [index]
        for i, arr_typ in enumerate(kpwwp__ypoti.array_types[1:]):
            yqwb__vdd = getattr(dgz__hhmc, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                vfupj__jsu = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    vfupj__jsu, [yqwb__vdd, index])
            else:
                vfupj__jsu = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    vfupj__jsu, [yqwb__vdd, index])
            values.append(val)
        value = context.make_tuple(builder, kpwwp__ypoti.yield_type, values)
        result.yield_(value)
        yhega__pwpv = cgutils.increment_index(builder, index)
        builder.store(yhega__pwpv, dgz__hhmc.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    wdndw__wubd = ir.Assign(rhs, lhs, expr.loc)
    ncqey__ijk = lhs
    kizw__ptrs = []
    mdl__odl = []
    ftprk__xqc = typ.count
    for i in range(ftprk__xqc):
        vgze__vvm = ir.Var(ncqey__ijk.scope, mk_unique_var('{}_size{}'.
            format(ncqey__ijk.name, i)), ncqey__ijk.loc)
        lbyp__ximp = ir.Expr.static_getitem(lhs, i, None, ncqey__ijk.loc)
        self.calltypes[lbyp__ximp] = None
        kizw__ptrs.append(ir.Assign(lbyp__ximp, vgze__vvm, ncqey__ijk.loc))
        self._define(equiv_set, vgze__vvm, types.intp, lbyp__ximp)
        mdl__odl.append(vgze__vvm)
    qbou__hgo = tuple(mdl__odl)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        qbou__hgo, pre=[wdndw__wubd] + kizw__ptrs)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
