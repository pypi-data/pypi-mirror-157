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
        txp__tebd = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({txp__tebd})\n')
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    wuto__uovi = 'def impl(df):\n'
    if df.has_runtime_cols:
        wuto__uovi += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        wei__dbndm = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        wuto__uovi += f'  return {wei__dbndm}'
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo}, ruy__giri)
    impl = ruy__giri['impl']
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
    pvpm__hzct = len(df.columns)
    advoo__txs = set(i for i in range(pvpm__hzct) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in advoo__txs else '') for i in
        range(pvpm__hzct))
    wuto__uovi = 'def f(df):\n'.format()
    wuto__uovi += '    return np.stack(({},), 1)\n'.format(data_args)
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo, 'np': np}, ruy__giri)
    bvw__oqfta = ruy__giri['f']
    return bvw__oqfta


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
    hdod__amcp = {'dtype': dtype, 'na_value': na_value}
    nayc__akvxt = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', hdod__amcp, nayc__akvxt,
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
            vary__fmn = bodo.hiframes.table.compute_num_runtime_columns(t)
            return vary__fmn * len(t)
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
            vary__fmn = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), vary__fmn
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), types.int64(ncols))


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    wuto__uovi = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    vwhjw__ydm = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    wuto__uovi += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{vwhjw__ydm}), {index}, None)
"""
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo}, ruy__giri)
    impl = ruy__giri['impl']
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
    hdod__amcp = {'copy': copy, 'errors': errors}
    nayc__akvxt = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', hdod__amcp, nayc__akvxt,
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
        hufd__bcloc = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        zyrtt__lje = _bodo_object_typeref.instance_type
        assert isinstance(zyrtt__lje, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in zyrtt__lje.column_index:
                    idx = zyrtt__lje.column_index[name]
                    arr_typ = zyrtt__lje.data[idx]
                else:
                    arr_typ = df.data[i]
                hufd__bcloc.append(arr_typ)
        else:
            extra_globals = {}
            rgekz__rlndv = {}
            for i, name in enumerate(zyrtt__lje.columns):
                arr_typ = zyrtt__lje.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    lsrk__vcs = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    lsrk__vcs = boolean_dtype
                else:
                    lsrk__vcs = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = lsrk__vcs
                rgekz__rlndv[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {rgekz__rlndv[ffcc__vbnzr]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if ffcc__vbnzr in rgekz__rlndv else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, ffcc__vbnzr in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        geqth__msdcp = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            geqth__msdcp = {name: dtype_to_array_type(parse_dtype(dtype)) for
                name, dtype in geqth__msdcp.items()}
            for i, name in enumerate(df.columns):
                if name in geqth__msdcp:
                    arr_typ = geqth__msdcp[name]
                else:
                    arr_typ = df.data[i]
                hufd__bcloc.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(geqth__msdcp[ffcc__vbnzr])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if ffcc__vbnzr in geqth__msdcp else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, ffcc__vbnzr in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        hufd__bcloc = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        olbj__wzj = bodo.TableType(tuple(hufd__bcloc))
        extra_globals['out_table_typ'] = olbj__wzj
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
        hnboc__ualc = types.none
        extra_globals = {'output_arr_typ': hnboc__ualc}
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
        easn__mcbq = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                easn__mcbq.append(arr + '.copy()')
            elif is_overload_false(deep):
                easn__mcbq.append(arr)
            else:
                easn__mcbq.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(easn__mcbq)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    hdod__amcp = {'index': index, 'level': level, 'errors': errors}
    nayc__akvxt = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', hdod__amcp, nayc__akvxt,
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
        brdlb__wwr = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        brdlb__wwr = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    ejc__puchp = tuple([brdlb__wwr.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    szdsp__iyltd = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        szdsp__iyltd = df.copy(columns=ejc__puchp)
        hnboc__ualc = types.none
        extra_globals = {'output_arr_typ': hnboc__ualc}
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
        easn__mcbq = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                easn__mcbq.append(arr + '.copy()')
            elif is_overload_false(copy):
                easn__mcbq.append(arr)
            else:
                easn__mcbq.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(easn__mcbq)
    return _gen_init_df(header, ejc__puchp, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    osaxw__wijfz = not is_overload_none(items)
    lzsus__lwx = not is_overload_none(like)
    vsplx__vhjw = not is_overload_none(regex)
    oeue__mhb = osaxw__wijfz ^ lzsus__lwx ^ vsplx__vhjw
    xzko__swhk = not (osaxw__wijfz or lzsus__lwx or vsplx__vhjw)
    if xzko__swhk:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not oeue__mhb:
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
        pzew__plvb = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        pzew__plvb = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert pzew__plvb in {0, 1}
    wuto__uovi = (
        'def impl(df, items=None, like=None, regex=None, axis=None):\n')
    if pzew__plvb == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if pzew__plvb == 1:
        ynnq__pzavc = []
        eoc__jbqlq = []
        onvv__mxiw = []
        if osaxw__wijfz:
            if is_overload_constant_list(items):
                jjx__euwp = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if lzsus__lwx:
            if is_overload_constant_str(like):
                yzla__bftul = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if vsplx__vhjw:
            if is_overload_constant_str(regex):
                pcuyd__mfkwx = get_overload_const_str(regex)
                jbt__jpxes = re.compile(pcuyd__mfkwx)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, ffcc__vbnzr in enumerate(df.columns):
            if not is_overload_none(items
                ) and ffcc__vbnzr in jjx__euwp or not is_overload_none(like
                ) and yzla__bftul in str(ffcc__vbnzr) or not is_overload_none(
                regex) and jbt__jpxes.search(str(ffcc__vbnzr)):
                eoc__jbqlq.append(ffcc__vbnzr)
                onvv__mxiw.append(i)
        for i in onvv__mxiw:
            var_name = f'data_{i}'
            ynnq__pzavc.append(var_name)
            wuto__uovi += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(ynnq__pzavc)
        return _gen_init_df(wuto__uovi, eoc__jbqlq, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    szdsp__iyltd = None
    if df.is_table_format:
        hnboc__ualc = types.Array(types.bool_, 1, 'C')
        szdsp__iyltd = DataFrameType(tuple([hnboc__ualc] * len(df.data)),
            df.index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': hnboc__ualc}
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
    dvqmq__qvkjr = is_overload_none(include)
    mpst__ifji = is_overload_none(exclude)
    pikv__rjrrl = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if dvqmq__qvkjr and mpst__ifji:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not dvqmq__qvkjr:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            nfhz__yxvol = [dtype_to_array_type(parse_dtype(elem,
                pikv__rjrrl)) for elem in include]
        elif is_legal_input(include):
            nfhz__yxvol = [dtype_to_array_type(parse_dtype(include,
                pikv__rjrrl))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        nfhz__yxvol = get_nullable_and_non_nullable_types(nfhz__yxvol)
        sgbon__pfefo = tuple(ffcc__vbnzr for i, ffcc__vbnzr in enumerate(df
            .columns) if df.data[i] in nfhz__yxvol)
    else:
        sgbon__pfefo = df.columns
    if not mpst__ifji:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            dmns__dcc = [dtype_to_array_type(parse_dtype(elem, pikv__rjrrl)
                ) for elem in exclude]
        elif is_legal_input(exclude):
            dmns__dcc = [dtype_to_array_type(parse_dtype(exclude, pikv__rjrrl))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        dmns__dcc = get_nullable_and_non_nullable_types(dmns__dcc)
        sgbon__pfefo = tuple(ffcc__vbnzr for ffcc__vbnzr in sgbon__pfefo if
            df.data[df.column_index[ffcc__vbnzr]] not in dmns__dcc)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ffcc__vbnzr]})'
         for ffcc__vbnzr in sgbon__pfefo)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, sgbon__pfefo, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    szdsp__iyltd = None
    if df.is_table_format:
        hnboc__ualc = types.Array(types.bool_, 1, 'C')
        szdsp__iyltd = DataFrameType(tuple([hnboc__ualc] * len(df.data)),
            df.index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': hnboc__ualc}
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
    aadd__osy = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in aadd__osy:
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
    aadd__osy = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in aadd__osy:
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
    wuto__uovi = 'def impl(df, values):\n'
    ulhuz__plj = {}
    cljri__zslh = False
    if isinstance(values, DataFrameType):
        cljri__zslh = True
        for i, ffcc__vbnzr in enumerate(df.columns):
            if ffcc__vbnzr in values.column_index:
                ixjme__tcwxo = 'val{}'.format(i)
                wuto__uovi += f"""  {ixjme__tcwxo} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[ffcc__vbnzr]})
"""
                ulhuz__plj[ffcc__vbnzr] = ixjme__tcwxo
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        ulhuz__plj = {ffcc__vbnzr: 'values' for ffcc__vbnzr in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        ixjme__tcwxo = 'data{}'.format(i)
        wuto__uovi += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(ixjme__tcwxo, i))
        data.append(ixjme__tcwxo)
    hvit__duol = ['out{}'.format(i) for i in range(len(df.columns))]
    valj__zgft = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    smtgp__uuwcg = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    nanu__crue = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, wgfma__ltkc) in enumerate(zip(df.columns, data)):
        if cname in ulhuz__plj:
            gmkeu__cojd = ulhuz__plj[cname]
            if cljri__zslh:
                wuto__uovi += valj__zgft.format(wgfma__ltkc, gmkeu__cojd,
                    hvit__duol[i])
            else:
                wuto__uovi += smtgp__uuwcg.format(wgfma__ltkc, gmkeu__cojd,
                    hvit__duol[i])
        else:
            wuto__uovi += nanu__crue.format(hvit__duol[i])
    return _gen_init_df(wuto__uovi, df.columns, ','.join(hvit__duol))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    pvpm__hzct = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(pvpm__hzct))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    jbmj__flmw = [ffcc__vbnzr for ffcc__vbnzr, kihov__pjao in zip(df.
        columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype(
        kihov__pjao.dtype)]
    assert len(jbmj__flmw) != 0
    roog__fcou = ''
    if not any(kihov__pjao == types.float64 for kihov__pjao in df.data):
        roog__fcou = '.astype(np.float64)'
    lrx__mcwrw = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[ffcc__vbnzr], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[ffcc__vbnzr]], IntegerArrayType) or
        df.data[df.column_index[ffcc__vbnzr]] == boolean_array else '') for
        ffcc__vbnzr in jbmj__flmw)
    dnrk__vvdf = 'np.stack(({},), 1){}'.format(lrx__mcwrw, roog__fcou)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(jbmj__flmw))
        )
    index = f'{generate_col_to_index_func_text(jbmj__flmw)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(dnrk__vvdf)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, jbmj__flmw, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    vzits__dlrg = dict(ddof=ddof)
    lmkj__rylwi = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    zeh__kba = '1' if is_overload_none(min_periods) else 'min_periods'
    jbmj__flmw = [ffcc__vbnzr for ffcc__vbnzr, kihov__pjao in zip(df.
        columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype(
        kihov__pjao.dtype)]
    if len(jbmj__flmw) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    roog__fcou = ''
    if not any(kihov__pjao == types.float64 for kihov__pjao in df.data):
        roog__fcou = '.astype(np.float64)'
    lrx__mcwrw = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[ffcc__vbnzr], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[ffcc__vbnzr]], IntegerArrayType) or
        df.data[df.column_index[ffcc__vbnzr]] == boolean_array else '') for
        ffcc__vbnzr in jbmj__flmw)
    dnrk__vvdf = 'np.stack(({},), 1){}'.format(lrx__mcwrw, roog__fcou)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(jbmj__flmw))
        )
    index = f'pd.Index({jbmj__flmw})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(dnrk__vvdf)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        zeh__kba)
    return _gen_init_df(header, jbmj__flmw, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    vzits__dlrg = dict(axis=axis, level=level, numeric_only=numeric_only)
    lmkj__rylwi = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    wuto__uovi = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    wuto__uovi += '  data = np.array([{}])\n'.format(data_args)
    wei__dbndm = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    wuto__uovi += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {wei__dbndm})\n'
        )
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo, 'np': np}, ruy__giri)
    impl = ruy__giri['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    vzits__dlrg = dict(axis=axis)
    lmkj__rylwi = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    wuto__uovi = 'def impl(df, axis=0, dropna=True):\n'
    wuto__uovi += '  data = np.asarray(({},))\n'.format(data_args)
    wei__dbndm = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    wuto__uovi += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {wei__dbndm})\n'
        )
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo, 'np': np}, ruy__giri)
    impl = ruy__giri['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    vzits__dlrg = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    lmkj__rylwi = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    vzits__dlrg = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    lmkj__rylwi = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    vzits__dlrg = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    lmkj__rylwi = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    vzits__dlrg = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    lmkj__rylwi = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    vzits__dlrg = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    lmkj__rylwi = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    vzits__dlrg = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    lmkj__rylwi = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    vzits__dlrg = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    lmkj__rylwi = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    vzits__dlrg = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    lmkj__rylwi = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    vzits__dlrg = dict(numeric_only=numeric_only, interpolation=interpolation)
    lmkj__rylwi = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    vzits__dlrg = dict(axis=axis, skipna=skipna)
    lmkj__rylwi = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for gon__lbz in df.data:
        if not (bodo.utils.utils.is_np_array_typ(gon__lbz) and (gon__lbz.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            gon__lbz.dtype, (types.Number, types.Boolean))) or isinstance(
            gon__lbz, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            gon__lbz in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {gon__lbz} not supported.'
                )
        if isinstance(gon__lbz, bodo.CategoricalArrayType
            ) and not gon__lbz.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    vzits__dlrg = dict(axis=axis, skipna=skipna)
    lmkj__rylwi = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for gon__lbz in df.data:
        if not (bodo.utils.utils.is_np_array_typ(gon__lbz) and (gon__lbz.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            gon__lbz.dtype, (types.Number, types.Boolean))) or isinstance(
            gon__lbz, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            gon__lbz in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {gon__lbz} not supported.'
                )
        if isinstance(gon__lbz, bodo.CategoricalArrayType
            ) and not gon__lbz.dtype.ordered:
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
        jbmj__flmw = tuple(ffcc__vbnzr for ffcc__vbnzr, kihov__pjao in zip(
            df.columns, df.data) if bodo.utils.typing.
            _is_pandas_numeric_dtype(kihov__pjao.dtype))
        out_colnames = jbmj__flmw
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            kxoo__vcj = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[ffcc__vbnzr]].dtype) for ffcc__vbnzr in
                out_colnames]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(kxoo__vcj, []))
    except NotImplementedError as gpc__zxcl:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    rslp__cak = ''
    if func_name in ('sum', 'prod'):
        rslp__cak = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    wuto__uovi = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, rslp__cak))
    if func_name == 'quantile':
        wuto__uovi = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        wuto__uovi = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        wuto__uovi += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        wuto__uovi += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        ruy__giri)
    impl = ruy__giri['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    rjfci__sujn = ''
    if func_name in ('min', 'max'):
        rjfci__sujn = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        rjfci__sujn = ', dtype=np.float32'
    jzzbv__tfdtk = f'bodo.libs.array_ops.array_op_{func_name}'
    kmw__bull = ''
    if func_name in ['sum', 'prod']:
        kmw__bull = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        kmw__bull = 'index'
    elif func_name == 'quantile':
        kmw__bull = 'q'
    elif func_name in ['std', 'var']:
        kmw__bull = 'True, ddof'
    elif func_name == 'median':
        kmw__bull = 'True'
    data_args = ', '.join(
        f'{jzzbv__tfdtk}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ffcc__vbnzr]}), {kmw__bull})'
         for ffcc__vbnzr in out_colnames)
    wuto__uovi = ''
    if func_name in ('idxmax', 'idxmin'):
        wuto__uovi += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        wuto__uovi += (
            '  data = bodo.utils.conversion.coerce_to_array(({},))\n'.
            format(data_args))
    else:
        wuto__uovi += '  data = np.asarray(({},){})\n'.format(data_args,
            rjfci__sujn)
    wuto__uovi += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return wuto__uovi


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    lis__aqfmn = [df_type.column_index[ffcc__vbnzr] for ffcc__vbnzr in
        out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in lis__aqfmn)
    zdbmu__lbtm = '\n        '.join(f'row[{i}] = arr_{lis__aqfmn[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    bjvvh__umwx = f'len(arr_{lis__aqfmn[0]})'
    cob__byzt = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum': 'np.nansum',
        'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in cob__byzt:
        fjtf__xvggq = cob__byzt[func_name]
        dme__uga = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        wuto__uovi = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {bjvvh__umwx}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{dme__uga})
    for i in numba.parfors.parfor.internal_prange(n):
        {zdbmu__lbtm}
        A[i] = {fjtf__xvggq}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return wuto__uovi
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    vzits__dlrg = dict(fill_method=fill_method, limit=limit, freq=freq)
    lmkj__rylwi = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', vzits__dlrg, lmkj__rylwi,
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
    vzits__dlrg = dict(axis=axis, skipna=skipna)
    lmkj__rylwi = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', vzits__dlrg, lmkj__rylwi,
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
    vzits__dlrg = dict(skipna=skipna)
    lmkj__rylwi = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', vzits__dlrg, lmkj__rylwi,
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
    vzits__dlrg = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    lmkj__rylwi = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    jbmj__flmw = [ffcc__vbnzr for ffcc__vbnzr, kihov__pjao in zip(df.
        columns, df.data) if _is_describe_type(kihov__pjao)]
    if len(jbmj__flmw) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    oik__ujfkc = sum(df.data[df.column_index[ffcc__vbnzr]].dtype == bodo.
        datetime64ns for ffcc__vbnzr in jbmj__flmw)

    def _get_describe(col_ind):
        ftwnd__reo = df.data[col_ind].dtype == bodo.datetime64ns
        if oik__ujfkc and oik__ujfkc != len(jbmj__flmw):
            if ftwnd__reo:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for ffcc__vbnzr in jbmj__flmw:
        col_ind = df.column_index[ffcc__vbnzr]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[ffcc__vbnzr]) for
        ffcc__vbnzr in jbmj__flmw)
    lliqe__lmtu = "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']"
    if oik__ujfkc == len(jbmj__flmw):
        lliqe__lmtu = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif oik__ujfkc:
        lliqe__lmtu = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({lliqe__lmtu})'
    return _gen_init_df(header, jbmj__flmw, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    vzits__dlrg = dict(axis=axis, convert=convert, is_copy=is_copy)
    lmkj__rylwi = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', vzits__dlrg, lmkj__rylwi,
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
    vzits__dlrg = dict(freq=freq, axis=axis, fill_value=fill_value)
    lmkj__rylwi = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for bxie__acn in df.data:
        if not is_supported_shift_array_type(bxie__acn):
            raise BodoError(
                f'Dataframe.shift() column input type {bxie__acn.dtype} not supported yet.'
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
    vzits__dlrg = dict(axis=axis)
    lmkj__rylwi = dict(axis=0)
    check_unsupported_args('DataFrame.diff', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for bxie__acn in df.data:
        if not (isinstance(bxie__acn, types.Array) and (isinstance(
            bxie__acn.dtype, types.Number) or bxie__acn.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {bxie__acn.dtype} not supported.'
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
    umsx__xqs = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(umsx__xqs)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        lrtfu__tmi = get_overload_const_list(column)
    else:
        lrtfu__tmi = [get_literal_value(column)]
    vwa__qrgu = [df.column_index[ffcc__vbnzr] for ffcc__vbnzr in lrtfu__tmi]
    for i in vwa__qrgu:
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
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{vwa__qrgu[0]})\n'
        )
    for i in range(n):
        if i in vwa__qrgu:
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
    hdod__amcp = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    nayc__akvxt = {'inplace': False, 'append': False, 'verify_integrity': False
        }
    check_unsupported_args('DataFrame.set_index', hdod__amcp, nayc__akvxt,
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
    columns = tuple(ffcc__vbnzr for ffcc__vbnzr in df.columns if 
        ffcc__vbnzr != col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    hdod__amcp = {'inplace': inplace}
    nayc__akvxt = {'inplace': False}
    check_unsupported_args('query', hdod__amcp, nayc__akvxt, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        mkgxu__sow = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[mkgxu__sow]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    hdod__amcp = {'subset': subset, 'keep': keep}
    nayc__akvxt = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', hdod__amcp, nayc__akvxt,
        package_name='pandas', module_name='DataFrame')
    pvpm__hzct = len(df.columns)
    wuto__uovi = "def impl(df, subset=None, keep='first'):\n"
    for i in range(pvpm__hzct):
        wuto__uovi += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    bhrm__fzlc = ', '.join(f'data_{i}' for i in range(pvpm__hzct))
    bhrm__fzlc += ',' if pvpm__hzct == 1 else ''
    wuto__uovi += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({bhrm__fzlc}))\n')
    wuto__uovi += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    wuto__uovi += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo}, ruy__giri)
    impl = ruy__giri['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    hdod__amcp = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    nayc__akvxt = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    wtlw__yct = []
    if is_overload_constant_list(subset):
        wtlw__yct = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        wtlw__yct = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        wtlw__yct = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    lrkas__ptg = []
    for col_name in wtlw__yct:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        lrkas__ptg.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', hdod__amcp,
        nayc__akvxt, package_name='pandas', module_name='DataFrame')
    hobc__zcl = []
    if lrkas__ptg:
        for mmwst__hmhsx in lrkas__ptg:
            if isinstance(df.data[mmwst__hmhsx], bodo.MapArrayType):
                hobc__zcl.append(df.columns[mmwst__hmhsx])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                hobc__zcl.append(col_name)
    if hobc__zcl:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {hobc__zcl} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    pvpm__hzct = len(df.columns)
    qwixw__rtp = ['data_{}'.format(i) for i in lrkas__ptg]
    bcegk__owooq = ['data_{}'.format(i) for i in range(pvpm__hzct) if i not in
        lrkas__ptg]
    if qwixw__rtp:
        dsvur__tzxt = len(qwixw__rtp)
    else:
        dsvur__tzxt = pvpm__hzct
    kkic__cbh = ', '.join(qwixw__rtp + bcegk__owooq)
    data_args = ', '.join('data_{}'.format(i) for i in range(pvpm__hzct))
    wuto__uovi = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(pvpm__hzct):
        wuto__uovi += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    wuto__uovi += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(kkic__cbh, index, dsvur__tzxt))
    wuto__uovi += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(wuto__uovi, df.columns, data_args, 'index')


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
            obja__wji = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                obja__wji = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                obja__wji = lambda i: f'other[:,{i}]'
        pvpm__hzct = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {obja__wji(i)})'
             for i in range(pvpm__hzct))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        phyj__xkhi = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(phyj__xkhi
            )


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    vzits__dlrg = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    lmkj__rylwi = dict(inplace=False, level=None, errors='raise', try_cast=
        False)
    check_unsupported_args(f'{func_name}', vzits__dlrg, lmkj__rylwi,
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
    pvpm__hzct = len(df.columns)
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
        for i in range(pvpm__hzct):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(pvpm__hzct):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(pvpm__hzct):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    eafzl__xaqo = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    wuto__uovi = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    ruy__giri = {}
    dmydb__rlp = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': eafzl__xaqo}
    dmydb__rlp.update(extra_globals)
    exec(wuto__uovi, dmydb__rlp, ruy__giri)
    impl = ruy__giri['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        lydg__qghh = pd.Index(lhs.columns)
        lxpj__ptzhg = pd.Index(rhs.columns)
        uqtfo__ouv, xjsay__fbr, rhqg__nvyw = lydg__qghh.join(lxpj__ptzhg,
            how='left' if is_inplace else 'outer', level=None,
            return_indexers=True)
        return tuple(uqtfo__ouv), xjsay__fbr, rhqg__nvyw
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        fnpcw__dqqvw = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        traw__wlzfl = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, fnpcw__dqqvw)
        check_runtime_cols_unsupported(rhs, fnpcw__dqqvw)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                uqtfo__ouv, xjsay__fbr, rhqg__nvyw = _get_binop_columns(lhs,
                    rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {wyg__hbjfx}) {fnpcw__dqqvw}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {fxcy__mweub})'
                     if wyg__hbjfx != -1 and fxcy__mweub != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for wyg__hbjfx, fxcy__mweub in zip(xjsay__fbr, rhqg__nvyw)
                    )
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, uqtfo__ouv, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            cnz__jdeqi = []
            zeu__ffmpg = []
            if op in traw__wlzfl:
                for i, oyr__dyk in enumerate(lhs.data):
                    if is_common_scalar_dtype([oyr__dyk.dtype, rhs]):
                        cnz__jdeqi.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {fnpcw__dqqvw} rhs'
                            )
                    else:
                        asn__aiu = f'arr{i}'
                        zeu__ffmpg.append(asn__aiu)
                        cnz__jdeqi.append(asn__aiu)
                data_args = ', '.join(cnz__jdeqi)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {fnpcw__dqqvw} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(zeu__ffmpg) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {asn__aiu} = np.empty(n, dtype=np.bool_)\n' for
                    asn__aiu in zeu__ffmpg)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(asn__aiu, op ==
                    operator.ne) for asn__aiu in zeu__ffmpg)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            cnz__jdeqi = []
            zeu__ffmpg = []
            if op in traw__wlzfl:
                for i, oyr__dyk in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, oyr__dyk.dtype]):
                        cnz__jdeqi.append(
                            f'lhs {fnpcw__dqqvw} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        asn__aiu = f'arr{i}'
                        zeu__ffmpg.append(asn__aiu)
                        cnz__jdeqi.append(asn__aiu)
                data_args = ', '.join(cnz__jdeqi)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, fnpcw__dqqvw) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(zeu__ffmpg) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(asn__aiu) for asn__aiu in zeu__ffmpg)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(asn__aiu, op ==
                    operator.ne) for asn__aiu in zeu__ffmpg)
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
        phyj__xkhi = create_binary_op_overload(op)
        overload(op)(phyj__xkhi)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        fnpcw__dqqvw = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, fnpcw__dqqvw)
        check_runtime_cols_unsupported(right, fnpcw__dqqvw)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                uqtfo__ouv, _, rhqg__nvyw = _get_binop_columns(left, right,
                    True)
                wuto__uovi = 'def impl(left, right):\n'
                for i, fxcy__mweub in enumerate(rhqg__nvyw):
                    if fxcy__mweub == -1:
                        wuto__uovi += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    wuto__uovi += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    wuto__uovi += f"""  df_arr{i} {fnpcw__dqqvw} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {fxcy__mweub})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    uqtfo__ouv)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(wuto__uovi, uqtfo__ouv, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            wuto__uovi = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                wuto__uovi += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                wuto__uovi += '  df_arr{0} {1} right\n'.format(i, fnpcw__dqqvw)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(wuto__uovi, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        phyj__xkhi = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(phyj__xkhi)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            fnpcw__dqqvw = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, fnpcw__dqqvw)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, fnpcw__dqqvw) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        phyj__xkhi = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(phyj__xkhi)


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
            fvck__lphhk = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                fvck__lphhk[i] = bodo.libs.array_kernels.isna(obj, i)
            return fvck__lphhk
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
            fvck__lphhk = np.empty(n, np.bool_)
            for i in range(n):
                fvck__lphhk[i] = pd.isna(obj[i])
            return fvck__lphhk
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
    hdod__amcp = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    nayc__akvxt = {'inplace': False, 'limit': None, 'regex': False,
        'method': 'pad'}
    check_unsupported_args('replace', hdod__amcp, nayc__akvxt, package_name
        ='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    exzw__cfdz = str(expr_node)
    return exzw__cfdz.startswith('left.') or exzw__cfdz.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    zfgq__jifdq = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (zfgq__jifdq,))
    ojs__zjrv = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        teoql__lptn = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        wicmv__xmpgy = {('NOT_NA', ojs__zjrv(oyr__dyk)): oyr__dyk for
            oyr__dyk in null_set}
        aaqvh__qsnhh, _, _ = _parse_query_expr(teoql__lptn, env, [], [],
            None, join_cleaned_cols=wicmv__xmpgy)
        roh__ahxee = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            zmzgu__hzgt = pd.core.computation.ops.BinOp('&', aaqvh__qsnhh,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = roh__ahxee
        return zmzgu__hzgt

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                qtmi__fsw = set()
                rmyw__dykpv = set()
                mvct__rkux = _insert_NA_cond_body(expr_node.lhs, qtmi__fsw)
                xuh__kihz = _insert_NA_cond_body(expr_node.rhs, rmyw__dykpv)
                mhqrj__kpj = qtmi__fsw.intersection(rmyw__dykpv)
                qtmi__fsw.difference_update(mhqrj__kpj)
                rmyw__dykpv.difference_update(mhqrj__kpj)
                null_set.update(mhqrj__kpj)
                expr_node.lhs = append_null_checks(mvct__rkux, qtmi__fsw)
                expr_node.rhs = append_null_checks(xuh__kihz, rmyw__dykpv)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            ztz__aryi = expr_node.name
            rofsi__hxr, col_name = ztz__aryi.split('.')
            if rofsi__hxr == 'left':
                zfsws__krchw = left_columns
                data = left_data
            else:
                zfsws__krchw = right_columns
                data = right_data
            ihmm__mtau = data[zfsws__krchw.index(col_name)]
            if bodo.utils.typing.is_nullable(ihmm__mtau):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    xzt__qdmdt = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        qvqe__qym = str(expr_node.lhs)
        gmstb__tzetx = str(expr_node.rhs)
        if qvqe__qym.startswith('left.') and gmstb__tzetx.startswith('left.'
            ) or qvqe__qym.startswith('right.') and gmstb__tzetx.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [qvqe__qym.split('.')[1]]
        right_on = [gmstb__tzetx.split('.')[1]]
        if qvqe__qym.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        eveur__jjaro, soay__qhd, lep__yhy = _extract_equal_conds(expr_node.lhs)
        wod__qgb, zguk__jgzdt, qce__mqyq = _extract_equal_conds(expr_node.rhs)
        left_on = eveur__jjaro + wod__qgb
        right_on = soay__qhd + zguk__jgzdt
        if lep__yhy is None:
            return left_on, right_on, qce__mqyq
        if qce__mqyq is None:
            return left_on, right_on, lep__yhy
        expr_node.lhs = lep__yhy
        expr_node.rhs = qce__mqyq
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    zfgq__jifdq = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (zfgq__jifdq,))
    brdlb__wwr = dict()
    ojs__zjrv = pd.core.computation.parsing.clean_column_name
    for name, qotiq__ykdk in (('left', left_columns), ('right', right_columns)
        ):
        for oyr__dyk in qotiq__ykdk:
            yjo__iwp = ojs__zjrv(oyr__dyk)
            vmj__rqqzw = name, yjo__iwp
            if vmj__rqqzw in brdlb__wwr:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{oyr__dyk}' and '{brdlb__wwr[yjo__iwp]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            brdlb__wwr[vmj__rqqzw] = oyr__dyk
    kwiai__hfk, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=brdlb__wwr)
    left_on, right_on, bnz__pnlk = _extract_equal_conds(kwiai__hfk.terms)
    return left_on, right_on, _insert_NA_cond(bnz__pnlk, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    vzits__dlrg = dict(sort=sort, copy=copy, validate=validate)
    lmkj__rylwi = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    zzvr__fuaqx = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    hubzz__ecpi = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in zzvr__fuaqx and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, plfrh__cwrdl = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if plfrh__cwrdl is None:
                    hubzz__ecpi = ''
                else:
                    hubzz__ecpi = str(plfrh__cwrdl)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = zzvr__fuaqx
        right_keys = zzvr__fuaqx
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
    kpd__qappt = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        nmjbv__msspj = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        nmjbv__msspj = list(get_overload_const_list(suffixes))
    suffix_x = nmjbv__msspj[0]
    suffix_y = nmjbv__msspj[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    wuto__uovi = "def _impl(left, right, how='inner', on=None, left_on=None,\n"
    wuto__uovi += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    wuto__uovi += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    wuto__uovi += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, kpd__qappt, hubzz__ecpi))
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo}, ruy__giri)
    _impl = ruy__giri['_impl']
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
    cpf__ccv = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    gehjl__oacc = {get_overload_const_str(kdb__fhw) for kdb__fhw in (
        left_on, right_on, on) if is_overload_constant_str(kdb__fhw)}
    for df in (left, right):
        for i, oyr__dyk in enumerate(df.data):
            if not isinstance(oyr__dyk, valid_dataframe_column_types
                ) and oyr__dyk not in cpf__ccv:
                raise BodoError(
                    f'{name_func}(): use of column with {type(oyr__dyk)} in merge unsupported'
                    )
            if df.columns[i] in gehjl__oacc and isinstance(oyr__dyk,
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
        nmjbv__msspj = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        nmjbv__msspj = list(get_overload_const_list(suffixes))
    if len(nmjbv__msspj) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    zzvr__fuaqx = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        uzmxh__eiqli = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            uzmxh__eiqli = on_str not in zzvr__fuaqx and ('left.' in on_str or
                'right.' in on_str)
        if len(zzvr__fuaqx) == 0 and not uzmxh__eiqli:
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
    vxi__uql = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            qiqfu__tdjv = left.index
            uiqe__tms = isinstance(qiqfu__tdjv, StringIndexType)
            jtgwe__nkk = right.index
            hhdga__etmyt = isinstance(jtgwe__nkk, StringIndexType)
        elif is_overload_true(left_index):
            qiqfu__tdjv = left.index
            uiqe__tms = isinstance(qiqfu__tdjv, StringIndexType)
            jtgwe__nkk = right.data[right.columns.index(right_keys[0])]
            hhdga__etmyt = jtgwe__nkk.dtype == string_type
        elif is_overload_true(right_index):
            qiqfu__tdjv = left.data[left.columns.index(left_keys[0])]
            uiqe__tms = qiqfu__tdjv.dtype == string_type
            jtgwe__nkk = right.index
            hhdga__etmyt = isinstance(jtgwe__nkk, StringIndexType)
        if uiqe__tms and hhdga__etmyt:
            return
        qiqfu__tdjv = qiqfu__tdjv.dtype
        jtgwe__nkk = jtgwe__nkk.dtype
        try:
            uqqes__syvb = vxi__uql.resolve_function_type(operator.eq, (
                qiqfu__tdjv, jtgwe__nkk), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=qiqfu__tdjv, rk_dtype=jtgwe__nkk))
    else:
        for lnn__hguk, sxa__iqy in zip(left_keys, right_keys):
            qiqfu__tdjv = left.data[left.columns.index(lnn__hguk)].dtype
            mlwgc__yrou = left.data[left.columns.index(lnn__hguk)]
            jtgwe__nkk = right.data[right.columns.index(sxa__iqy)].dtype
            djkqf__rivwa = right.data[right.columns.index(sxa__iqy)]
            if mlwgc__yrou == djkqf__rivwa:
                continue
            hlasq__uqmk = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=lnn__hguk, lk_dtype=qiqfu__tdjv, rk=sxa__iqy,
                rk_dtype=jtgwe__nkk))
            ujqri__ppkgj = qiqfu__tdjv == string_type
            mvew__qoj = jtgwe__nkk == string_type
            if ujqri__ppkgj ^ mvew__qoj:
                raise_bodo_error(hlasq__uqmk)
            try:
                uqqes__syvb = vxi__uql.resolve_function_type(operator.eq, (
                    qiqfu__tdjv, jtgwe__nkk), {})
            except:
                raise_bodo_error(hlasq__uqmk)


def validate_keys(keys, df):
    tdu__pawvo = set(keys).difference(set(df.columns))
    if len(tdu__pawvo) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in tdu__pawvo:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {tdu__pawvo} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    vzits__dlrg = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    lmkj__rylwi = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', vzits__dlrg, lmkj__rylwi,
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
    wuto__uovi = "def _impl(left, other, on=None, how='left',\n"
    wuto__uovi += "    lsuffix='', rsuffix='', sort=False):\n"
    wuto__uovi += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo}, ruy__giri)
    _impl = ruy__giri['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        cho__ctgb = get_overload_const_list(on)
        validate_keys(cho__ctgb, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    zzvr__fuaqx = tuple(set(left.columns) & set(other.columns))
    if len(zzvr__fuaqx) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=zzvr__fuaqx))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    szvu__mzpj = set(left_keys) & set(right_keys)
    wtvnn__wrhyi = set(left_columns) & set(right_columns)
    cnhx__dfedb = wtvnn__wrhyi - szvu__mzpj
    pxo__mxir = set(left_columns) - wtvnn__wrhyi
    wtngo__fdf = set(right_columns) - wtvnn__wrhyi
    bmurf__xhtx = {}

    def insertOutColumn(col_name):
        if col_name in bmurf__xhtx:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        bmurf__xhtx[col_name] = 0
    for xdz__vawvf in szvu__mzpj:
        insertOutColumn(xdz__vawvf)
    for xdz__vawvf in cnhx__dfedb:
        bltr__mpd = str(xdz__vawvf) + suffix_x
        zmlnt__emfd = str(xdz__vawvf) + suffix_y
        insertOutColumn(bltr__mpd)
        insertOutColumn(zmlnt__emfd)
    for xdz__vawvf in pxo__mxir:
        insertOutColumn(xdz__vawvf)
    for xdz__vawvf in wtngo__fdf:
        insertOutColumn(xdz__vawvf)
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
    zzvr__fuaqx = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = zzvr__fuaqx
        right_keys = zzvr__fuaqx
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
        nmjbv__msspj = suffixes
    if is_overload_constant_list(suffixes):
        nmjbv__msspj = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        nmjbv__msspj = suffixes.value
    suffix_x = nmjbv__msspj[0]
    suffix_y = nmjbv__msspj[1]
    wuto__uovi = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    wuto__uovi += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    wuto__uovi += "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n"
    wuto__uovi += "    allow_exact_matches=True, direction='backward'):\n"
    wuto__uovi += '  suffix_x = suffixes[0]\n'
    wuto__uovi += '  suffix_y = suffixes[1]\n'
    wuto__uovi += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo}, ruy__giri)
    _impl = ruy__giri['_impl']
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
    vzits__dlrg = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    vzm__wanqy = dict(sort=False, group_keys=True, squeeze=False, observed=True
        )
    check_unsupported_args('Dataframe.groupby', vzits__dlrg, vzm__wanqy,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    pkw__ofaqq = func_name == 'DataFrame.pivot_table'
    if pkw__ofaqq:
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
    cbilc__mbz = get_literal_value(columns)
    if isinstance(cbilc__mbz, (list, tuple)):
        if len(cbilc__mbz) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {cbilc__mbz}"
                )
        cbilc__mbz = cbilc__mbz[0]
    if cbilc__mbz not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {cbilc__mbz} not found in DataFrame {df}."
            )
    nqrq__vjqw = df.column_index[cbilc__mbz]
    if is_overload_none(index):
        yhgwi__xlfj = []
        whxvj__ccsi = []
    else:
        whxvj__ccsi = get_literal_value(index)
        if not isinstance(whxvj__ccsi, (list, tuple)):
            whxvj__ccsi = [whxvj__ccsi]
        yhgwi__xlfj = []
        for index in whxvj__ccsi:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            yhgwi__xlfj.append(df.column_index[index])
    if not (all(isinstance(ffcc__vbnzr, int) for ffcc__vbnzr in whxvj__ccsi
        ) or all(isinstance(ffcc__vbnzr, str) for ffcc__vbnzr in whxvj__ccsi)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        xap__fqqgq = []
        fyp__hkq = []
        umz__ebuj = yhgwi__xlfj + [nqrq__vjqw]
        for i, ffcc__vbnzr in enumerate(df.columns):
            if i not in umz__ebuj:
                xap__fqqgq.append(i)
                fyp__hkq.append(ffcc__vbnzr)
    else:
        fyp__hkq = get_literal_value(values)
        if not isinstance(fyp__hkq, (list, tuple)):
            fyp__hkq = [fyp__hkq]
        xap__fqqgq = []
        for val in fyp__hkq:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            xap__fqqgq.append(df.column_index[val])
    njh__rxp = set(xap__fqqgq) | set(yhgwi__xlfj) | {nqrq__vjqw}
    if len(njh__rxp) != len(xap__fqqgq) + len(yhgwi__xlfj) + 1:
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
    if len(yhgwi__xlfj) == 0:
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
        for oimh__rfn in yhgwi__xlfj:
            index_column = df.data[oimh__rfn]
            check_valid_index_typ(index_column)
    emz__opbfm = df.data[nqrq__vjqw]
    if isinstance(emz__opbfm, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(emz__opbfm, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for oqgkv__ezpvh in xap__fqqgq:
        bbxt__hit = df.data[oqgkv__ezpvh]
        if isinstance(bbxt__hit, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or bbxt__hit == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return (whxvj__ccsi, cbilc__mbz, fyp__hkq, yhgwi__xlfj, nqrq__vjqw,
        xap__fqqgq)


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (whxvj__ccsi, cbilc__mbz, fyp__hkq, oimh__rfn, nqrq__vjqw, wyjt__xjxb) = (
        pivot_error_checking(data, index, columns, values, 'DataFrame.pivot'))
    if len(whxvj__ccsi) == 0:
        if is_overload_none(data.index.name_typ):
            akpf__qee = None,
        else:
            akpf__qee = get_literal_value(data.index.name_typ),
    else:
        akpf__qee = tuple(whxvj__ccsi)
    whxvj__ccsi = ColNamesMetaType(akpf__qee)
    fyp__hkq = ColNamesMetaType(tuple(fyp__hkq))
    cbilc__mbz = ColNamesMetaType((cbilc__mbz,))
    wuto__uovi = 'def impl(data, index=None, columns=None, values=None):\n'
    wuto__uovi += f'    pivot_values = data.iloc[:, {nqrq__vjqw}].unique()\n'
    wuto__uovi += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(oimh__rfn) == 0:
        wuto__uovi += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        wuto__uovi += '        (\n'
        for bpx__vwlc in oimh__rfn:
            wuto__uovi += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {bpx__vwlc}),
"""
        wuto__uovi += '        ),\n'
    wuto__uovi += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {nqrq__vjqw}),),
"""
    wuto__uovi += '        (\n'
    for oqgkv__ezpvh in wyjt__xjxb:
        wuto__uovi += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {oqgkv__ezpvh}),
"""
    wuto__uovi += '        ),\n'
    wuto__uovi += '        pivot_values,\n'
    wuto__uovi += '        index_lit,\n'
    wuto__uovi += '        columns_lit,\n'
    wuto__uovi += '        values_lit,\n'
    wuto__uovi += '    )\n'
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo, 'index_lit': whxvj__ccsi, 'columns_lit':
        cbilc__mbz, 'values_lit': fyp__hkq}, ruy__giri)
    impl = ruy__giri['impl']
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
    vzits__dlrg = dict(fill_value=fill_value, margins=margins, dropna=
        dropna, margins_name=margins_name, observed=observed, sort=sort)
    lmkj__rylwi = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', vzits__dlrg,
        lmkj__rylwi, package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    (whxvj__ccsi, cbilc__mbz, fyp__hkq, oimh__rfn, nqrq__vjqw, wyjt__xjxb) = (
        pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    jikl__idnlr = whxvj__ccsi
    whxvj__ccsi = ColNamesMetaType(tuple(whxvj__ccsi))
    fyp__hkq = ColNamesMetaType(tuple(fyp__hkq))
    lzrlg__oihu = cbilc__mbz
    cbilc__mbz = ColNamesMetaType((cbilc__mbz,))
    wuto__uovi = 'def impl(\n'
    wuto__uovi += '    data,\n'
    wuto__uovi += '    values=None,\n'
    wuto__uovi += '    index=None,\n'
    wuto__uovi += '    columns=None,\n'
    wuto__uovi += '    aggfunc="mean",\n'
    wuto__uovi += '    fill_value=None,\n'
    wuto__uovi += '    margins=False,\n'
    wuto__uovi += '    dropna=True,\n'
    wuto__uovi += '    margins_name="All",\n'
    wuto__uovi += '    observed=False,\n'
    wuto__uovi += '    sort=True,\n'
    wuto__uovi += '    _pivot_values=None,\n'
    wuto__uovi += '):\n'
    nyz__vhe = oimh__rfn + [nqrq__vjqw] + wyjt__xjxb
    wuto__uovi += f'    data = data.iloc[:, {nyz__vhe}]\n'
    ktoky__bmf = jikl__idnlr + [lzrlg__oihu]
    if not is_overload_none(_pivot_values):
        lbotz__xyf = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(lbotz__xyf)
        wuto__uovi += '    pivot_values = _pivot_values_arr\n'
        wuto__uovi += (
            f'    data = data[data.iloc[:, {len(oimh__rfn)}].isin(pivot_values)]\n'
            )
        if all(isinstance(ffcc__vbnzr, str) for ffcc__vbnzr in lbotz__xyf):
            jtsq__evfg = pd.array(lbotz__xyf, 'string')
        elif all(isinstance(ffcc__vbnzr, int) for ffcc__vbnzr in lbotz__xyf):
            jtsq__evfg = np.array(lbotz__xyf, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        jtsq__evfg = None
    wuto__uovi += (
        f'    data = data.groupby({ktoky__bmf!r}, as_index=False).agg(aggfunc)\n'
        )
    if is_overload_none(_pivot_values):
        wuto__uovi += (
            f'    pivot_values = data.iloc[:, {len(oimh__rfn)}].unique()\n')
    wuto__uovi += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    wuto__uovi += '        (\n'
    for i in range(0, len(oimh__rfn)):
        wuto__uovi += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    wuto__uovi += '        ),\n'
    wuto__uovi += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(oimh__rfn)}),),
"""
    wuto__uovi += '        (\n'
    for i in range(len(oimh__rfn) + 1, len(wyjt__xjxb) + len(oimh__rfn) + 1):
        wuto__uovi += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    wuto__uovi += '        ),\n'
    wuto__uovi += '        pivot_values,\n'
    wuto__uovi += '        index_lit,\n'
    wuto__uovi += '        columns_lit,\n'
    wuto__uovi += '        values_lit,\n'
    wuto__uovi += '        check_duplicates=False,\n'
    wuto__uovi += '        _constant_pivot_values=_constant_pivot_values,\n'
    wuto__uovi += '    )\n'
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo, 'numba': numba, 'index_lit':
        whxvj__ccsi, 'columns_lit': cbilc__mbz, 'values_lit': fyp__hkq,
        '_pivot_values_arr': jtsq__evfg, '_constant_pivot_values':
        _pivot_values}, ruy__giri)
    impl = ruy__giri['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    vzits__dlrg = dict(col_level=col_level, ignore_index=ignore_index)
    lmkj__rylwi = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', vzits__dlrg, lmkj__rylwi,
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
    qlmi__ery = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(qlmi__ery, (list, tuple)):
        qlmi__ery = [qlmi__ery]
    for ffcc__vbnzr in qlmi__ery:
        if ffcc__vbnzr not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {ffcc__vbnzr} not found in {frame}."
                )
    qnx__gve = [frame.column_index[i] for i in qlmi__ery]
    if is_overload_none(value_vars):
        cfo__cgoz = []
        tdqx__jhgt = []
        for i, ffcc__vbnzr in enumerate(frame.columns):
            if i not in qnx__gve:
                cfo__cgoz.append(i)
                tdqx__jhgt.append(ffcc__vbnzr)
    else:
        tdqx__jhgt = get_literal_value(value_vars)
        if not isinstance(tdqx__jhgt, (list, tuple)):
            tdqx__jhgt = [tdqx__jhgt]
        tdqx__jhgt = [v for v in tdqx__jhgt if v not in qlmi__ery]
        if not tdqx__jhgt:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        cfo__cgoz = []
        for val in tdqx__jhgt:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            cfo__cgoz.append(frame.column_index[val])
    for ffcc__vbnzr in tdqx__jhgt:
        if ffcc__vbnzr not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {ffcc__vbnzr} not found in {frame}."
                )
    if not (all(isinstance(ffcc__vbnzr, int) for ffcc__vbnzr in tdqx__jhgt) or
        all(isinstance(ffcc__vbnzr, str) for ffcc__vbnzr in tdqx__jhgt)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    lnj__qhrsd = frame.data[cfo__cgoz[0]]
    feptf__cpuqt = [frame.data[i].dtype for i in cfo__cgoz]
    cfo__cgoz = np.array(cfo__cgoz, dtype=np.int64)
    qnx__gve = np.array(qnx__gve, dtype=np.int64)
    _, ukjxs__uzrkt = bodo.utils.typing.get_common_scalar_dtype(feptf__cpuqt)
    if not ukjxs__uzrkt:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': tdqx__jhgt, 'val_type': lnj__qhrsd}
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
    if frame.is_table_format and all(v == lnj__qhrsd.dtype for v in
        feptf__cpuqt):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            cfo__cgoz))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(tdqx__jhgt) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {cfo__cgoz[0]})
"""
    else:
        dywrj__bfv = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in cfo__cgoz)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({dywrj__bfv},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in qnx__gve:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(tdqx__jhgt)})\n'
            )
    ycfqe__zix = ', '.join(f'out_id{i}' for i in qnx__gve) + (', ' if len(
        qnx__gve) > 0 else '')
    data_args = ycfqe__zix + 'var_col, val_col'
    columns = tuple(qlmi__ery + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(tdqx__jhgt)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    vzits__dlrg = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    lmkj__rylwi = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', vzits__dlrg, lmkj__rylwi,
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
    vzits__dlrg = dict(ignore_index=ignore_index, key=key)
    lmkj__rylwi = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', vzits__dlrg,
        lmkj__rylwi, package_name='pandas', module_name='DataFrame')
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
    kxhx__ivrq = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        kxhx__ivrq.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        xkka__prvpr = [get_overload_const_tuple(by)]
    else:
        xkka__prvpr = get_overload_const_list(by)
    xkka__prvpr = set((k, '') if (k, '') in kxhx__ivrq else k for k in
        xkka__prvpr)
    if len(xkka__prvpr.difference(kxhx__ivrq)) > 0:
        kuq__cqex = list(set(get_overload_const_list(by)).difference(
            kxhx__ivrq))
        raise_bodo_error(f'sort_values(): invalid keys {kuq__cqex} for by.')
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
        ucc__lrii = get_overload_const_list(na_position)
        for na_position in ucc__lrii:
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
    vzits__dlrg = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    lmkj__rylwi = dict(axis=0, level=None, kind='quicksort', sort_remaining
        =True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', vzits__dlrg, lmkj__rylwi,
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
    vzits__dlrg = dict(limit=limit, downcast=downcast)
    lmkj__rylwi = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', vzits__dlrg, lmkj__rylwi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    bhpa__rgzf = not is_overload_none(value)
    wxz__ofmbl = not is_overload_none(method)
    if bhpa__rgzf and wxz__ofmbl:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not bhpa__rgzf and not wxz__ofmbl:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if bhpa__rgzf:
        bgops__xjhq = 'value=value'
    else:
        bgops__xjhq = 'method=method'
    data_args = [(
        f"df['{ffcc__vbnzr}'].fillna({bgops__xjhq}, inplace=inplace)" if
        isinstance(ffcc__vbnzr, str) else
        f'df[{ffcc__vbnzr}].fillna({bgops__xjhq}, inplace=inplace)') for
        ffcc__vbnzr in df.columns]
    wuto__uovi = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        wuto__uovi += '  ' + '  \n'.join(data_args) + '\n'
        ruy__giri = {}
        exec(wuto__uovi, {}, ruy__giri)
        impl = ruy__giri['impl']
        return impl
    else:
        return _gen_init_df(wuto__uovi, df.columns, ', '.join(kihov__pjao +
            '.values' for kihov__pjao in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    vzits__dlrg = dict(col_level=col_level, col_fill=col_fill)
    lmkj__rylwi = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', vzits__dlrg,
        lmkj__rylwi, package_name='pandas', module_name='DataFrame')
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
    wuto__uovi = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    wuto__uovi += (
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
        dlz__xtkk = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            dlz__xtkk)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            wuto__uovi += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            amia__esymg = ['m_index[{}]'.format(i) for i in range(df.index.
                nlevels)]
            data_args = amia__esymg + data_args
        else:
            usy__aiht = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [usy__aiht] + data_args
    return _gen_init_df(wuto__uovi, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    vsjs__ramj = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and vsjs__ramj == 1 or is_overload_constant_list(level
        ) and list(get_overload_const_list(level)) == list(range(vsjs__ramj))


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
        frhu__tgpm = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        hcftr__hwtkq = get_overload_const_list(subset)
        frhu__tgpm = []
        for gxj__hiel in hcftr__hwtkq:
            if gxj__hiel not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{gxj__hiel}' not in data frame columns {df}"
                    )
            frhu__tgpm.append(df.column_index[gxj__hiel])
    pvpm__hzct = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(pvpm__hzct))
    wuto__uovi = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(pvpm__hzct):
        wuto__uovi += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    wuto__uovi += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in frhu__tgpm)))
    wuto__uovi += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(wuto__uovi, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    vzits__dlrg = dict(index=index, level=level, errors=errors)
    lmkj__rylwi = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', vzits__dlrg, lmkj__rylwi,
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
            ikk__uxcs = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            ikk__uxcs = get_overload_const_list(labels)
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
            ikk__uxcs = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            ikk__uxcs = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for ffcc__vbnzr in ikk__uxcs:
        if ffcc__vbnzr not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(ffcc__vbnzr, df.columns))
    if len(set(ikk__uxcs)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    ejc__puchp = tuple(ffcc__vbnzr for ffcc__vbnzr in df.columns if 
        ffcc__vbnzr not in ikk__uxcs)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[ffcc__vbnzr], '.copy()' if not inplace else
        '') for ffcc__vbnzr in ejc__puchp)
    wuto__uovi = (
        'def impl(df, labels=None, axis=0, index=None, columns=None,\n')
    wuto__uovi += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(wuto__uovi, ejc__puchp, data_args, index)


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
    vzits__dlrg = dict(random_state=random_state, weights=weights, axis=
        axis, ignore_index=ignore_index)
    uxfvk__lxy = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', vzits__dlrg, uxfvk__lxy,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    pvpm__hzct = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(pvpm__hzct))
    sepwa__qsij = ', '.join('rhs_data_{}'.format(i) for i in range(pvpm__hzct))
    wuto__uovi = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    wuto__uovi += '  if (frac == 1 or n == len(df)) and not replace:\n'
    wuto__uovi += (
        '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n')
    for i in range(pvpm__hzct):
        wuto__uovi += (
            """  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})
"""
            .format(i))
    wuto__uovi += '  if frac is None:\n'
    wuto__uovi += '    frac_d = -1.0\n'
    wuto__uovi += '  else:\n'
    wuto__uovi += '    frac_d = frac\n'
    wuto__uovi += '  if n is None:\n'
    wuto__uovi += '    n_i = 0\n'
    wuto__uovi += '  else:\n'
    wuto__uovi += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    wuto__uovi += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({sepwa__qsij},), {index}, n_i, frac_d, replace)
"""
    wuto__uovi += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(wuto__uovi, df.columns,
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
    hdod__amcp = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    nayc__akvxt = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', hdod__amcp, nayc__akvxt,
        package_name='pandas', module_name='DataFrame')
    ddle__aki = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            uuiaq__dxanj = ddle__aki + '\n'
            uuiaq__dxanj += 'Index: 0 entries\n'
            uuiaq__dxanj += 'Empty DataFrame'
            print(uuiaq__dxanj)
        return _info_impl
    else:
        wuto__uovi = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        wuto__uovi += '    ncols = df.shape[1]\n'
        wuto__uovi += f'    lines = "{ddle__aki}\\n"\n'
        wuto__uovi += f'    lines += "{df.index}: "\n'
        wuto__uovi += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            wuto__uovi += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            wuto__uovi += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            wuto__uovi += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        wuto__uovi += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        wuto__uovi += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        wuto__uovi += '    column_width = max(space, 7)\n'
        wuto__uovi += '    column= "Column"\n'
        wuto__uovi += '    underl= "------"\n'
        wuto__uovi += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        wuto__uovi += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        wuto__uovi += '    mem_size = 0\n'
        wuto__uovi += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        wuto__uovi += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        wuto__uovi += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        kfgw__gsgh = dict()
        for i in range(len(df.columns)):
            wuto__uovi += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            emkwt__hhqwg = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                emkwt__hhqwg = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                aldy__zgtsb = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                emkwt__hhqwg = f'{aldy__zgtsb[:-7]}'
            wuto__uovi += f'    col_dtype[{i}] = "{emkwt__hhqwg}"\n'
            if emkwt__hhqwg in kfgw__gsgh:
                kfgw__gsgh[emkwt__hhqwg] += 1
            else:
                kfgw__gsgh[emkwt__hhqwg] = 1
            wuto__uovi += f'    col_name[{i}] = "{df.columns[i]}"\n'
            wuto__uovi += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        wuto__uovi += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        wuto__uovi += '    for i in column_info:\n'
        wuto__uovi += "        lines += f'{i}\\n'\n"
        tcijh__qrk = ', '.join(f'{k}({kfgw__gsgh[k]})' for k in sorted(
            kfgw__gsgh))
        wuto__uovi += f"    lines += 'dtypes: {tcijh__qrk}\\n'\n"
        wuto__uovi += '    mem_size += df.index.nbytes\n'
        wuto__uovi += '    total_size = _sizeof_fmt(mem_size)\n'
        wuto__uovi += "    lines += f'memory usage: {total_size}'\n"
        wuto__uovi += '    print(lines)\n'
        ruy__giri = {}
        exec(wuto__uovi, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo':
            bodo, 'np': np}, ruy__giri)
        _info_impl = ruy__giri['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    wuto__uovi = 'def impl(df, index=True, deep=False):\n'
    kwdvg__zfkb = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes')
    jzini__elq = is_overload_true(index)
    columns = df.columns
    if jzini__elq:
        columns = ('Index',) + columns
    if len(columns) == 0:
        uuba__zyjkj = ()
    elif all(isinstance(ffcc__vbnzr, int) for ffcc__vbnzr in columns):
        uuba__zyjkj = np.array(columns, 'int64')
    elif all(isinstance(ffcc__vbnzr, str) for ffcc__vbnzr in columns):
        uuba__zyjkj = pd.array(columns, 'string')
    else:
        uuba__zyjkj = columns
    if df.is_table_format and len(df.columns) > 0:
        rjdu__pjeg = int(jzini__elq)
        vary__fmn = len(columns)
        wuto__uovi += f'  nbytes_arr = np.empty({vary__fmn}, np.int64)\n'
        wuto__uovi += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        wuto__uovi += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {rjdu__pjeg})
"""
        if jzini__elq:
            wuto__uovi += f'  nbytes_arr[0] = {kwdvg__zfkb}\n'
        wuto__uovi += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if jzini__elq:
            data = f'{kwdvg__zfkb},{data}'
        else:
            vwhjw__ydm = ',' if len(columns) == 1 else ''
            data = f'{data}{vwhjw__ydm}'
        wuto__uovi += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        uuba__zyjkj}, ruy__giri)
    impl = ruy__giri['impl']
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
    qfg__vlbmk = 'read_excel_df{}'.format(next_label())
    setattr(types, qfg__vlbmk, df_type)
    vvac__ndqf = False
    if is_overload_constant_list(parse_dates):
        vvac__ndqf = get_overload_const_list(parse_dates)
    gjbvq__och = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    wuto__uovi = f"""
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
    with numba.objmode(df="{qfg__vlbmk}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{gjbvq__och}}},
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
            parse_dates={vvac__ndqf},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    ruy__giri = {}
    exec(wuto__uovi, globals(), ruy__giri)
    impl = ruy__giri['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as gpc__zxcl:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    wuto__uovi = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    wuto__uovi += '    ylabel=None, title=None, legend=True, fontsize=None, \n'
    wuto__uovi += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        wuto__uovi += '   fig, ax = plt.subplots()\n'
    else:
        wuto__uovi += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        wuto__uovi += '   fig.set_figwidth(figsize[0])\n'
        wuto__uovi += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        wuto__uovi += '   xlabel = x\n'
    wuto__uovi += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        wuto__uovi += '   ylabel = y\n'
    else:
        wuto__uovi += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        wuto__uovi += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        wuto__uovi += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    wuto__uovi += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            wuto__uovi += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            ihn__wwxtt = get_overload_const_str(x)
            dlg__qbe = df.columns.index(ihn__wwxtt)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if dlg__qbe != i:
                        wuto__uovi += (
                            f'   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])\n'
                            )
        else:
            wuto__uovi += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        wuto__uovi += '   ax.scatter(df[x], df[y], s=20)\n'
        wuto__uovi += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        wuto__uovi += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        wuto__uovi += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        wuto__uovi += '   ax.legend()\n'
    wuto__uovi += '   return ax\n'
    ruy__giri = {}
    exec(wuto__uovi, {'bodo': bodo, 'plt': plt}, ruy__giri)
    impl = ruy__giri['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for fonb__ckvjt in df_typ.data:
        if not (isinstance(fonb__ckvjt, IntegerArrayType) or isinstance(
            fonb__ckvjt.dtype, types.Number) or fonb__ckvjt.dtype in (bodo.
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
        pdukn__cbpc = args[0]
        bhel__klg = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        dmmcn__llqrk = pdukn__cbpc
        check_runtime_cols_unsupported(pdukn__cbpc, 'set_df_col()')
        if isinstance(pdukn__cbpc, DataFrameType):
            index = pdukn__cbpc.index
            if len(pdukn__cbpc.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(pdukn__cbpc.columns) == 0:
                    index = val.index
                val = val.data
            if is_pd_index_type(val):
                val = bodo.utils.typing.get_index_data_arr_types(val)[0]
            if isinstance(val, types.List):
                val = dtype_to_array_type(val.dtype)
            if not is_array_typ(val):
                val = dtype_to_array_type(val)
            if bhel__klg in pdukn__cbpc.columns:
                ejc__puchp = pdukn__cbpc.columns
                kmr__cymi = pdukn__cbpc.columns.index(bhel__klg)
                bgpwq__cqnf = list(pdukn__cbpc.data)
                bgpwq__cqnf[kmr__cymi] = val
                bgpwq__cqnf = tuple(bgpwq__cqnf)
            else:
                ejc__puchp = pdukn__cbpc.columns + (bhel__klg,)
                bgpwq__cqnf = pdukn__cbpc.data + (val,)
            dmmcn__llqrk = DataFrameType(bgpwq__cqnf, index, ejc__puchp,
                pdukn__cbpc.dist, pdukn__cbpc.is_table_format)
        return dmmcn__llqrk(*args)


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
        rqyx__qwcet = args[0]
        assert isinstance(rqyx__qwcet, DataFrameType) and len(rqyx__qwcet.
            columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        vkukx__jxzu = args[2]
        assert len(col_names_to_replace) == len(vkukx__jxzu
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(rqyx__qwcet.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in rqyx__qwcet.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(rqyx__qwcet,
            '__bodosql_replace_columns_dummy()')
        index = rqyx__qwcet.index
        ejc__puchp = rqyx__qwcet.columns
        bgpwq__cqnf = list(rqyx__qwcet.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            usnjn__rggf = vkukx__jxzu[i]
            assert isinstance(usnjn__rggf, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(usnjn__rggf, SeriesType):
                usnjn__rggf = usnjn__rggf.data
            mmwst__hmhsx = rqyx__qwcet.column_index[col_name]
            bgpwq__cqnf[mmwst__hmhsx] = usnjn__rggf
        bgpwq__cqnf = tuple(bgpwq__cqnf)
        dmmcn__llqrk = DataFrameType(bgpwq__cqnf, index, ejc__puchp,
            rqyx__qwcet.dist, rqyx__qwcet.is_table_format)
        return dmmcn__llqrk(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    orn__cbf = {}

    def _rewrite_membership_op(self, node, left, right):
        fyu__kpy = node.op
        op = self.visit(fyu__kpy)
        return op, fyu__kpy, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    tdm__rbdrg = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in tdm__rbdrg:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in tdm__rbdrg:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        yqu__rlz = node.attr
        value = node.value
        lcqz__wdz = pd.core.computation.ops.LOCAL_TAG
        if yqu__rlz in ('str', 'dt'):
            try:
                bui__ynp = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as qkb__khbu:
                col_name = qkb__khbu.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            bui__ynp = str(self.visit(value))
        vmj__rqqzw = bui__ynp, yqu__rlz
        if vmj__rqqzw in join_cleaned_cols:
            yqu__rlz = join_cleaned_cols[vmj__rqqzw]
        name = bui__ynp + '.' + yqu__rlz
        if name.startswith(lcqz__wdz):
            name = name[len(lcqz__wdz):]
        if yqu__rlz in ('str', 'dt'):
            lbayw__wkhfw = columns[cleaned_columns.index(bui__ynp)]
            orn__cbf[lbayw__wkhfw] = bui__ynp
            self.env.scope[name] = 0
            return self.term_type(lcqz__wdz + name, self.env)
        tdm__rbdrg.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in tdm__rbdrg:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        hfz__rvsj = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        bhel__klg = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(hfz__rvsj), bhel__klg))

    def op__str__(self):
        ggmj__qpve = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            nkh__hrlgm)) for nkh__hrlgm in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(ggmj__qpve)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(ggmj__qpve)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(ggmj__qpve))
    dzwr__gitmo = (pd.core.computation.expr.BaseExprVisitor.
        _rewrite_membership_op)
    eib__ocul = pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop
    cjhib__qlcpm = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    datb__web = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    cpi__joxei = pd.core.computation.ops.Term.__str__
    oyq__emvys = pd.core.computation.ops.MathCall.__str__
    xfl__stnkp = pd.core.computation.ops.Op.__str__
    roh__ahxee = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
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
        kwiai__hfk = pd.core.computation.expr.Expr(expr, env=env)
        yxd__mak = str(kwiai__hfk)
    except pd.core.computation.ops.UndefinedVariableError as qkb__khbu:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == qkb__khbu.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {qkb__khbu}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            dzwr__gitmo)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            eib__ocul)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = cjhib__qlcpm
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = datb__web
        pd.core.computation.ops.Term.__str__ = cpi__joxei
        pd.core.computation.ops.MathCall.__str__ = oyq__emvys
        pd.core.computation.ops.Op.__str__ = xfl__stnkp
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            roh__ahxee)
    dge__hlf = pd.core.computation.parsing.clean_column_name
    orn__cbf.update({ffcc__vbnzr: dge__hlf(ffcc__vbnzr) for ffcc__vbnzr in
        columns if dge__hlf(ffcc__vbnzr) in kwiai__hfk.names})
    return kwiai__hfk, yxd__mak, orn__cbf


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        jrwi__dcxbn = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(jrwi__dcxbn))
        zox__tpsf = namedtuple('Pandas', col_names)
        wvgw__jaufx = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], zox__tpsf)
        super(DataFrameTupleIterator, self).__init__(name, wvgw__jaufx)

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
        yes__uxbtg = [if_series_to_array_type(a) for a in args[len(args) // 2:]
            ]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        yes__uxbtg = [types.Array(types.int64, 1, 'C')] + yes__uxbtg
        uwmhq__ypld = DataFrameTupleIterator(col_names, yes__uxbtg)
        return uwmhq__ypld(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rrepr__urzkc = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            rrepr__urzkc)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    dqs__wikkq = args[len(args) // 2:]
    izceu__ewl = sig.args[len(sig.args) // 2:]
    syugs__wycup = context.make_helper(builder, sig.return_type)
    meur__nhkmo = context.get_constant(types.intp, 0)
    ofwcu__npxx = cgutils.alloca_once_value(builder, meur__nhkmo)
    syugs__wycup.index = ofwcu__npxx
    for i, arr in enumerate(dqs__wikkq):
        setattr(syugs__wycup, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(dqs__wikkq, izceu__ewl):
        context.nrt.incref(builder, arr_typ, arr)
    res = syugs__wycup._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    sdgtw__aiy, = sig.args
    yvfpf__ugw, = args
    syugs__wycup = context.make_helper(builder, sdgtw__aiy, value=yvfpf__ugw)
    hoip__laalv = signature(types.intp, sdgtw__aiy.array_types[1])
    fchgw__pihsa = context.compile_internal(builder, lambda a: len(a),
        hoip__laalv, [syugs__wycup.array0])
    index = builder.load(syugs__wycup.index)
    aqj__meu = builder.icmp_signed('<', index, fchgw__pihsa)
    result.set_valid(aqj__meu)
    with builder.if_then(aqj__meu):
        values = [index]
        for i, arr_typ in enumerate(sdgtw__aiy.array_types[1:]):
            yzsvf__hkygu = getattr(syugs__wycup, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                aznak__ptppu = signature(pd_timestamp_type, arr_typ, types.intp
                    )
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    aznak__ptppu, [yzsvf__hkygu, index])
            else:
                aznak__ptppu = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    aznak__ptppu, [yzsvf__hkygu, index])
            values.append(val)
        value = context.make_tuple(builder, sdgtw__aiy.yield_type, values)
        result.yield_(value)
        fks__xjy = cgutils.increment_index(builder, index)
        builder.store(fks__xjy, syugs__wycup.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    skmrq__ipzfo = ir.Assign(rhs, lhs, expr.loc)
    tqmri__prryt = lhs
    ftdf__lyn = []
    unu__vqwf = []
    jmm__isofq = typ.count
    for i in range(jmm__isofq):
        urt__mqnuc = ir.Var(tqmri__prryt.scope, mk_unique_var('{}_size{}'.
            format(tqmri__prryt.name, i)), tqmri__prryt.loc)
        oiz__awe = ir.Expr.static_getitem(lhs, i, None, tqmri__prryt.loc)
        self.calltypes[oiz__awe] = None
        ftdf__lyn.append(ir.Assign(oiz__awe, urt__mqnuc, tqmri__prryt.loc))
        self._define(equiv_set, urt__mqnuc, types.intp, oiz__awe)
        unu__vqwf.append(urt__mqnuc)
    ffedk__chfvs = tuple(unu__vqwf)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        ffedk__chfvs, pre=[skmrq__ipzfo] + ftdf__lyn)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
