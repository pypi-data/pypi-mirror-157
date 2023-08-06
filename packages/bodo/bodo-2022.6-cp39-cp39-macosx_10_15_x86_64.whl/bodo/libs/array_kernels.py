"""
Implements array kernels such as median and quantile.
"""
import hashlib
import inspect
import math
import operator
import re
import warnings
from math import sqrt
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types, typing
from numba.core.imputils import lower_builtin
from numba.core.ir_utils import find_const, guard
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload, overload_attribute, register_jitable
from numba.np.arrayobj import make_array
from numba.np.numpy_support import as_dtype
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, init_categorical_array
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs import quantile_alg
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, drop_duplicates_table, info_from_table, info_to_array, sample_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, offset_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.dict_arr_ext import DictionaryArrayType
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import str_arr_set_na, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, check_unsupported_args, decode_if_dict_array, element_type, find_common_np_dtype, get_overload_const_bool, get_overload_const_list, get_overload_const_str, is_overload_constant_bool, is_overload_constant_str, is_overload_none, is_str_arr_type, raise_bodo_error, to_str_arr_if_dict_array
from bodo.utils.utils import build_set_seen_na, check_and_propagate_cpp_exception, numba_to_c_type, unliteral_all
ll.add_symbol('quantile_sequential', quantile_alg.quantile_sequential)
ll.add_symbol('quantile_parallel', quantile_alg.quantile_parallel)
MPI_ROOT = 0
sum_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value)
max_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Max.value)
min_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Min.value)


def isna(arr, i):
    return False


@overload(isna)
def overload_isna(arr, i):
    i = types.unliteral(i)
    if arr == string_array_type:
        return lambda arr, i: bodo.libs.str_arr_ext.str_arr_is_na(arr, i)
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type,
        datetime_timedelta_array_type, string_array_split_view_type):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
            ._null_bitmap, i)
    if isinstance(arr, ArrayItemArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, StructArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.struct_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, TupleArrayType):
        return lambda arr, i: bodo.libs.array_kernels.isna(arr._data, i)
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return lambda arr, i: arr.codes[i] == -1
    if arr == bodo.binary_array_type:
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr._data), i)
    if isinstance(arr, types.List):
        if arr.dtype == types.none:
            return lambda arr, i: True
        elif isinstance(arr.dtype, types.optional):
            return lambda arr, i: arr[i] is None
        else:
            return lambda arr, i: False
    if isinstance(arr, bodo.NullableTupleType):
        return lambda arr, i: arr._null_values[i]
    if isinstance(arr, DictionaryArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
            ._indices._null_bitmap, i) or bodo.libs.array_kernels.isna(arr.
            _data, arr._indices[i])
    if isinstance(arr, DatetimeArrayType):
        return lambda arr, i: np.isnat(arr._data[i])
    assert isinstance(arr, types.Array), f'Invalid array type in isna(): {arr}'
    dtype = arr.dtype
    if isinstance(dtype, types.Float):
        return lambda arr, i: np.isnan(arr[i])
    if isinstance(dtype, (types.NPDatetime, types.NPTimedelta)):
        return lambda arr, i: np.isnat(arr[i])
    return lambda arr, i: False


def setna(arr, ind, int_nan_const=0):
    arr[ind] = np.nan


@overload(setna, no_unliteral=True)
def setna_overload(arr, ind, int_nan_const=0):
    if isinstance(arr.dtype, types.Float):
        return setna
    if isinstance(arr.dtype, (types.NPDatetime, types.NPTimedelta)):
        quxqs__vylg = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = quxqs__vylg
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        quxqs__vylg = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = quxqs__vylg
        return _setnan_impl
    if arr == string_array_type:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = ''
            str_arr_set_na(arr, ind)
        return impl
    if isinstance(arr, DictionaryArrayType):
        return lambda arr, ind, int_nan_const=0: bodo.libs.array_kernels.setna(
            arr._indices, ind)
    if arr == boolean_array:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = False
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)):
        return (lambda arr, ind, int_nan_const=0: bodo.libs.int_arr_ext.
            set_bit_to_arr(arr._null_bitmap, ind, 0))
    if arr == bodo.binary_array_type:

        def impl_binary_arr(arr, ind, int_nan_const=0):
            xlaw__lwzat = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            xlaw__lwzat[ind + 1] = xlaw__lwzat[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            xlaw__lwzat = bodo.libs.array_item_arr_ext.get_offsets(arr)
            xlaw__lwzat[ind + 1] = xlaw__lwzat[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr), ind, 0)
        return impl_arr_item
    if isinstance(arr, bodo.libs.struct_arr_ext.StructArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.struct_arr_ext.
                get_null_bitmap(arr), ind, 0)
            data = bodo.libs.struct_arr_ext.get_data(arr)
            setna_tup(data, ind)
        return impl
    if isinstance(arr, TupleArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._data, ind)
        return impl
    if arr.dtype == types.bool_:

        def b_set(arr, ind, int_nan_const=0):
            arr[ind] = False
        return b_set
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):

        def setna_cat(arr, ind, int_nan_const=0):
            arr.codes[ind] = -1
        return setna_cat
    if isinstance(arr.dtype, types.Integer):

        def setna_int(arr, ind, int_nan_const=0):
            arr[ind] = int_nan_const
        return setna_int
    if arr == datetime_date_array_type:

        def setna_datetime_date(arr, ind, int_nan_const=0):
            arr._data[ind] = (1970 << 32) + (1 << 16) + 1
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_date
    if arr == datetime_timedelta_array_type:

        def setna_datetime_timedelta(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._days_data, ind)
            bodo.libs.array_kernels.setna(arr._seconds_data, ind)
            bodo.libs.array_kernels.setna(arr._microseconds_data, ind)
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_timedelta
    return lambda arr, ind, int_nan_const=0: None


def setna_tup(arr_tup, ind, int_nan_const=0):
    for arr in arr_tup:
        arr[ind] = np.nan


@overload(setna_tup, no_unliteral=True)
def overload_setna_tup(arr_tup, ind, int_nan_const=0):
    dou__dawf = arr_tup.count
    pfyi__lannh = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(dou__dawf):
        pfyi__lannh += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    pfyi__lannh += '  return\n'
    dqml__okjl = {}
    exec(pfyi__lannh, {'setna': setna}, dqml__okjl)
    impl = dqml__okjl['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        djg__qxqq = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(djg__qxqq.start, djg__qxqq.stop, djg__qxqq.step):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        pegk__drupi = 'n'
        yhdem__vztj = 'n_pes'
        wtmb__lcy = 'min_op'
    else:
        pegk__drupi = 'n-1, -1, -1'
        yhdem__vztj = '-1'
        wtmb__lcy = 'max_op'
    pfyi__lannh = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {yhdem__vztj}
    for i in range({pegk__drupi}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {wtmb__lcy}))
        if possible_valid_rank != {yhdem__vztj}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    dqml__okjl = {}
    exec(pfyi__lannh, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op':
        max_op, 'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.
        box_if_dt64}, dqml__okjl)
    impl = dqml__okjl['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    pba__gjshl = array_to_info(arr)
    _median_series_computation(res, pba__gjshl, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(pba__gjshl)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    pba__gjshl = array_to_info(arr)
    _autocorr_series_computation(res, pba__gjshl, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(pba__gjshl)


@numba.njit
def autocorr(arr, lag=1, parallel=False):
    res = np.empty(1, types.float64)
    autocorr_series_computation(res.ctypes, arr, lag, parallel)
    return res[0]


ll.add_symbol('compute_series_monotonicity', quantile_alg.
    compute_series_monotonicity)
_compute_series_monotonicity = types.ExternalFunction(
    'compute_series_monotonicity', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def series_monotonicity_call(res, arr, inc_dec, is_parallel):
    pba__gjshl = array_to_info(arr)
    _compute_series_monotonicity(res, pba__gjshl, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(pba__gjshl)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    goiv__epun = res[0] > 0.5
    return goiv__epun


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        cxg__ggn = '-'
        dmuc__fjm = 'index_arr[0] > threshhold_date'
        pegk__drupi = '1, n+1'
        ozhic__veos = 'index_arr[-i] <= threshhold_date'
        qnlug__tgkv = 'i - 1'
    else:
        cxg__ggn = '+'
        dmuc__fjm = 'index_arr[-1] < threshhold_date'
        pegk__drupi = 'n'
        ozhic__veos = 'index_arr[i] >= threshhold_date'
        qnlug__tgkv = 'i'
    pfyi__lannh = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        pfyi__lannh += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        pfyi__lannh += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            pfyi__lannh += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            pfyi__lannh += """      threshhold_date = initial_date - date_offset.base + date_offset
"""
            pfyi__lannh += '    else:\n'
            pfyi__lannh += (
                '      threshhold_date = initial_date + date_offset\n')
        else:
            pfyi__lannh += (
                f'    threshhold_date = initial_date {cxg__ggn} date_offset\n')
    else:
        pfyi__lannh += f'  threshhold_date = initial_date {cxg__ggn} offset\n'
    pfyi__lannh += '  local_valid = 0\n'
    pfyi__lannh += f'  n = len(index_arr)\n'
    pfyi__lannh += f'  if n:\n'
    pfyi__lannh += f'    if {dmuc__fjm}:\n'
    pfyi__lannh += '      loc_valid = n\n'
    pfyi__lannh += '    else:\n'
    pfyi__lannh += f'      for i in range({pegk__drupi}):\n'
    pfyi__lannh += f'        if {ozhic__veos}:\n'
    pfyi__lannh += f'          loc_valid = {qnlug__tgkv}\n'
    pfyi__lannh += '          break\n'
    pfyi__lannh += '  if is_parallel:\n'
    pfyi__lannh += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    pfyi__lannh += '    return total_valid\n'
    pfyi__lannh += '  else:\n'
    pfyi__lannh += '    return loc_valid\n'
    dqml__okjl = {}
    exec(pfyi__lannh, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, dqml__okjl)
    return dqml__okjl['impl']


def quantile(A, q):
    return 0


def quantile_parallel(A, q):
    return 0


@infer_global(quantile)
@infer_global(quantile_parallel)
class QuantileType(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) in [2, 3]
        return signature(types.float64, *unliteral_all(args))


@lower_builtin(quantile, types.Array, types.float64)
@lower_builtin(quantile, IntegerArrayType, types.float64)
@lower_builtin(quantile, BooleanArrayType, types.float64)
def lower_dist_quantile_seq(context, builder, sig, args):
    djvzm__wqssm = numba_to_c_type(sig.args[0].dtype)
    kmjxd__chj = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), djvzm__wqssm))
    fjmvk__thi = args[0]
    hdn__pkh = sig.args[0]
    if isinstance(hdn__pkh, (IntegerArrayType, BooleanArrayType)):
        fjmvk__thi = cgutils.create_struct_proxy(hdn__pkh)(context, builder,
            fjmvk__thi).data
        hdn__pkh = types.Array(hdn__pkh.dtype, 1, 'C')
    assert hdn__pkh.ndim == 1
    arr = make_array(hdn__pkh)(context, builder, fjmvk__thi)
    rlj__syok = builder.extract_value(arr.shape, 0)
    cwc__aebf = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        rlj__syok, args[1], builder.load(kmjxd__chj)]
    xcnn__mwg = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    dcv__gegq = lir.FunctionType(lir.DoubleType(), xcnn__mwg)
    bjp__xpk = cgutils.get_or_insert_function(builder.module, dcv__gegq,
        name='quantile_sequential')
    bbcyn__uhpat = builder.call(bjp__xpk, cwc__aebf)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return bbcyn__uhpat


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    djvzm__wqssm = numba_to_c_type(sig.args[0].dtype)
    kmjxd__chj = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), djvzm__wqssm))
    fjmvk__thi = args[0]
    hdn__pkh = sig.args[0]
    if isinstance(hdn__pkh, (IntegerArrayType, BooleanArrayType)):
        fjmvk__thi = cgutils.create_struct_proxy(hdn__pkh)(context, builder,
            fjmvk__thi).data
        hdn__pkh = types.Array(hdn__pkh.dtype, 1, 'C')
    assert hdn__pkh.ndim == 1
    arr = make_array(hdn__pkh)(context, builder, fjmvk__thi)
    rlj__syok = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        syxjo__czc = args[2]
    else:
        syxjo__czc = rlj__syok
    cwc__aebf = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        rlj__syok, syxjo__czc, args[1], builder.load(kmjxd__chj)]
    xcnn__mwg = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType(
        64), lir.DoubleType(), lir.IntType(32)]
    dcv__gegq = lir.FunctionType(lir.DoubleType(), xcnn__mwg)
    bjp__xpk = cgutils.get_or_insert_function(builder.module, dcv__gegq,
        name='quantile_parallel')
    bbcyn__uhpat = builder.call(bjp__xpk, cwc__aebf)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return bbcyn__uhpat


def rank(arr, method='average', na_option='keep', ascending=True, pct=False):
    return arr


@overload(rank, no_unliteral=True, inline='always')
def overload_rank(arr, method='average', na_option='keep', ascending=True,
    pct=False):
    if not is_overload_constant_str(method):
        raise_bodo_error(
            "Series.rank(): 'method' argument must be a constant string")
    method = get_overload_const_str(method)
    if not is_overload_constant_str(na_option):
        raise_bodo_error(
            "Series.rank(): 'na_option' argument must be a constant string")
    na_option = get_overload_const_str(na_option)
    if not is_overload_constant_bool(ascending):
        raise_bodo_error(
            "Series.rank(): 'ascending' argument must be a constant boolean")
    ascending = get_overload_const_bool(ascending)
    if not is_overload_constant_bool(pct):
        raise_bodo_error(
            "Series.rank(): 'pct' argument must be a constant boolean")
    pct = get_overload_const_bool(pct)
    if method == 'first' and not ascending:
        raise BodoError(
            "Series.rank(): method='first' with ascending=False is currently unsupported."
            )
    pfyi__lannh = (
        "def impl(arr, method='average', na_option='keep', ascending=True, pct=False):\n"
        )
    pfyi__lannh += '  na_idxs = pd.isna(arr)\n'
    pfyi__lannh += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    pfyi__lannh += '  nas = sum(na_idxs)\n'
    if not ascending:
        pfyi__lannh += '  if nas and nas < (sorter.size - 1):\n'
        pfyi__lannh += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        pfyi__lannh += '  else:\n'
        pfyi__lannh += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        pfyi__lannh += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    pfyi__lannh += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    pfyi__lannh += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        pfyi__lannh += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        pfyi__lannh += '    inv,\n'
        pfyi__lannh += '    new_dtype=np.float64,\n'
        pfyi__lannh += '    copy=True,\n'
        pfyi__lannh += '    nan_to_str=False,\n'
        pfyi__lannh += '    from_series=True,\n'
        pfyi__lannh += '    ) + 1\n'
    else:
        pfyi__lannh += '  arr = arr[sorter]\n'
        pfyi__lannh += '  sorted_nas = np.nonzero(pd.isna(arr))[0]\n'
        pfyi__lannh += '  eq_arr_na = arr[1:] != arr[:-1]\n'
        pfyi__lannh += '  eq_arr_na[pd.isna(eq_arr_na)] = False\n'
        pfyi__lannh += '  eq_arr = eq_arr_na.astype(np.bool_)\n'
        pfyi__lannh += '  obs = np.concatenate((np.array([True]), eq_arr))\n'
        pfyi__lannh += '  if sorted_nas.size:\n'
        pfyi__lannh += (
            '    first_na, rep_nas = sorted_nas[0], sorted_nas[1:]\n')
        pfyi__lannh += '    obs[first_na] = True\n'
        pfyi__lannh += '    obs[rep_nas] = False\n'
        pfyi__lannh += (
            '    if rep_nas.size and (rep_nas[-1] + 1) < obs.size:\n')
        pfyi__lannh += '      obs[rep_nas[-1] + 1] = True\n'
        pfyi__lannh += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            pfyi__lannh += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            pfyi__lannh += '    dense,\n'
            pfyi__lannh += '    new_dtype=np.float64,\n'
            pfyi__lannh += '    copy=True,\n'
            pfyi__lannh += '    nan_to_str=False,\n'
            pfyi__lannh += '    from_series=True,\n'
            pfyi__lannh += '  )\n'
        else:
            pfyi__lannh += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            pfyi__lannh += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                pfyi__lannh += '  ret = count_float[dense]\n'
            elif method == 'min':
                pfyi__lannh += '  ret = count_float[dense - 1] + 1\n'
            else:
                pfyi__lannh += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                pfyi__lannh += '  ret[na_idxs] = -1\n'
            pfyi__lannh += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            pfyi__lannh += '  div_val = arr.size - nas\n'
        else:
            pfyi__lannh += '  div_val = arr.size\n'
        pfyi__lannh += '  for i in range(len(ret)):\n'
        pfyi__lannh += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        pfyi__lannh += '  ret[na_idxs] = np.nan\n'
    pfyi__lannh += '  return ret\n'
    dqml__okjl = {}
    exec(pfyi__lannh, {'np': np, 'pd': pd, 'bodo': bodo}, dqml__okjl)
    return dqml__okjl['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    win__kvi = start
    jyw__tfs = 2 * start + 1
    puzf__ylzzx = 2 * start + 2
    if jyw__tfs < n and not cmp_f(arr[jyw__tfs], arr[win__kvi]):
        win__kvi = jyw__tfs
    if puzf__ylzzx < n and not cmp_f(arr[puzf__ylzzx], arr[win__kvi]):
        win__kvi = puzf__ylzzx
    if win__kvi != start:
        arr[start], arr[win__kvi] = arr[win__kvi], arr[start]
        ind_arr[start], ind_arr[win__kvi] = ind_arr[win__kvi], ind_arr[start]
        min_heapify(arr, ind_arr, n, win__kvi, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        mnlm__wqap = np.empty(k, A.dtype)
        rrr__vbxv = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                mnlm__wqap[ind] = A[i]
                rrr__vbxv[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            mnlm__wqap = mnlm__wqap[:ind]
            rrr__vbxv = rrr__vbxv[:ind]
        return mnlm__wqap, rrr__vbxv, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        gvp__mjgi = np.sort(A)
        pbr__zecu = index_arr[np.argsort(A)]
        anm__fqm = pd.Series(gvp__mjgi).notna().values
        gvp__mjgi = gvp__mjgi[anm__fqm]
        pbr__zecu = pbr__zecu[anm__fqm]
        if is_largest:
            gvp__mjgi = gvp__mjgi[::-1]
            pbr__zecu = pbr__zecu[::-1]
        return np.ascontiguousarray(gvp__mjgi), np.ascontiguousarray(pbr__zecu)
    mnlm__wqap, rrr__vbxv, start = select_k_nonan(A, index_arr, m, k)
    rrr__vbxv = rrr__vbxv[mnlm__wqap.argsort()]
    mnlm__wqap.sort()
    if not is_largest:
        mnlm__wqap = np.ascontiguousarray(mnlm__wqap[::-1])
        rrr__vbxv = np.ascontiguousarray(rrr__vbxv[::-1])
    for i in range(start, m):
        if cmp_f(A[i], mnlm__wqap[0]):
            mnlm__wqap[0] = A[i]
            rrr__vbxv[0] = index_arr[i]
            min_heapify(mnlm__wqap, rrr__vbxv, k, 0, cmp_f)
    rrr__vbxv = rrr__vbxv[mnlm__wqap.argsort()]
    mnlm__wqap.sort()
    if is_largest:
        mnlm__wqap = mnlm__wqap[::-1]
        rrr__vbxv = rrr__vbxv[::-1]
    return np.ascontiguousarray(mnlm__wqap), np.ascontiguousarray(rrr__vbxv)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    ehle__stdbn = bodo.libs.distributed_api.get_rank()
    urk__mibby, odg__mrre = nlargest(A, I, k, is_largest, cmp_f)
    ovuk__wepzk = bodo.libs.distributed_api.gatherv(urk__mibby)
    pcd__fiw = bodo.libs.distributed_api.gatherv(odg__mrre)
    if ehle__stdbn == MPI_ROOT:
        res, itinn__tbx = nlargest(ovuk__wepzk, pcd__fiw, k, is_largest, cmp_f)
    else:
        res = np.empty(k, A.dtype)
        itinn__tbx = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(itinn__tbx)
    return res, itinn__tbx


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    fqft__txb, mlark__vzvt = mat.shape
    yxos__tigbf = np.empty((mlark__vzvt, mlark__vzvt), dtype=np.float64)
    for vkew__vmm in range(mlark__vzvt):
        for xoomm__uzmga in range(vkew__vmm + 1):
            dfo__sxj = 0
            bmwah__msvv = xmgc__svws = cdet__pihr = jdbu__qnwpi = 0.0
            for i in range(fqft__txb):
                if np.isfinite(mat[i, vkew__vmm]) and np.isfinite(mat[i,
                    xoomm__uzmga]):
                    gov__rpw = mat[i, vkew__vmm]
                    oiivl__hak = mat[i, xoomm__uzmga]
                    dfo__sxj += 1
                    cdet__pihr += gov__rpw
                    jdbu__qnwpi += oiivl__hak
            if parallel:
                dfo__sxj = bodo.libs.distributed_api.dist_reduce(dfo__sxj,
                    sum_op)
                cdet__pihr = bodo.libs.distributed_api.dist_reduce(cdet__pihr,
                    sum_op)
                jdbu__qnwpi = bodo.libs.distributed_api.dist_reduce(jdbu__qnwpi
                    , sum_op)
            if dfo__sxj < minpv:
                yxos__tigbf[vkew__vmm, xoomm__uzmga] = yxos__tigbf[
                    xoomm__uzmga, vkew__vmm] = np.nan
            else:
                tky__boa = cdet__pihr / dfo__sxj
                uqruj__jwy = jdbu__qnwpi / dfo__sxj
                cdet__pihr = 0.0
                for i in range(fqft__txb):
                    if np.isfinite(mat[i, vkew__vmm]) and np.isfinite(mat[i,
                        xoomm__uzmga]):
                        gov__rpw = mat[i, vkew__vmm] - tky__boa
                        oiivl__hak = mat[i, xoomm__uzmga] - uqruj__jwy
                        cdet__pihr += gov__rpw * oiivl__hak
                        bmwah__msvv += gov__rpw * gov__rpw
                        xmgc__svws += oiivl__hak * oiivl__hak
                if parallel:
                    cdet__pihr = bodo.libs.distributed_api.dist_reduce(
                        cdet__pihr, sum_op)
                    bmwah__msvv = bodo.libs.distributed_api.dist_reduce(
                        bmwah__msvv, sum_op)
                    xmgc__svws = bodo.libs.distributed_api.dist_reduce(
                        xmgc__svws, sum_op)
                gchcj__jxni = dfo__sxj - 1.0 if cov else sqrt(bmwah__msvv *
                    xmgc__svws)
                if gchcj__jxni != 0.0:
                    yxos__tigbf[vkew__vmm, xoomm__uzmga] = yxos__tigbf[
                        xoomm__uzmga, vkew__vmm] = cdet__pihr / gchcj__jxni
                else:
                    yxos__tigbf[vkew__vmm, xoomm__uzmga] = yxos__tigbf[
                        xoomm__uzmga, vkew__vmm] = np.nan
    return yxos__tigbf


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    qosnp__neqvc = n != 1
    pfyi__lannh = 'def impl(data, parallel=False):\n'
    pfyi__lannh += '  if parallel:\n'
    yta__jfz = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    pfyi__lannh += f'    cpp_table = arr_info_list_to_table([{yta__jfz}])\n'
    pfyi__lannh += f"""    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)
"""
    dbf__jnj = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    pfyi__lannh += f'    data = ({dbf__jnj},)\n'
    pfyi__lannh += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    pfyi__lannh += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    pfyi__lannh += '    bodo.libs.array.delete_table(cpp_table)\n'
    pfyi__lannh += '  n = len(data[0])\n'
    pfyi__lannh += '  out = np.empty(n, np.bool_)\n'
    pfyi__lannh += '  uniqs = dict()\n'
    if qosnp__neqvc:
        pfyi__lannh += '  for i in range(n):\n'
        zmsjt__ecfhg = ', '.join(f'data[{i}][i]' for i in range(n))
        nausj__ubbq = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        pfyi__lannh += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({zmsjt__ecfhg},), ({nausj__ubbq},))
"""
        pfyi__lannh += '    if val in uniqs:\n'
        pfyi__lannh += '      out[i] = True\n'
        pfyi__lannh += '    else:\n'
        pfyi__lannh += '      out[i] = False\n'
        pfyi__lannh += '      uniqs[val] = 0\n'
    else:
        pfyi__lannh += '  data = data[0]\n'
        pfyi__lannh += '  hasna = False\n'
        pfyi__lannh += '  for i in range(n):\n'
        pfyi__lannh += '    if bodo.libs.array_kernels.isna(data, i):\n'
        pfyi__lannh += '      out[i] = hasna\n'
        pfyi__lannh += '      hasna = True\n'
        pfyi__lannh += '    else:\n'
        pfyi__lannh += '      val = data[i]\n'
        pfyi__lannh += '      if val in uniqs:\n'
        pfyi__lannh += '        out[i] = True\n'
        pfyi__lannh += '      else:\n'
        pfyi__lannh += '        out[i] = False\n'
        pfyi__lannh += '        uniqs[val] = 0\n'
    pfyi__lannh += '  if parallel:\n'
    pfyi__lannh += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    pfyi__lannh += '  return out\n'
    dqml__okjl = {}
    exec(pfyi__lannh, {'bodo': bodo, 'np': np, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'info_to_array': info_to_array, 'info_from_table': info_from_table},
        dqml__okjl)
    impl = dqml__okjl['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    dou__dawf = len(data)
    pfyi__lannh = (
        'def impl(data, ind_arr, n, frac, replace, parallel=False):\n')
    pfyi__lannh += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        dou__dawf)))
    pfyi__lannh += '  table_total = arr_info_list_to_table(info_list_total)\n'
    pfyi__lannh += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(dou__dawf))
    for vevxa__gyw in range(dou__dawf):
        pfyi__lannh += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(vevxa__gyw, vevxa__gyw, vevxa__gyw))
    pfyi__lannh += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(dou__dawf))
    pfyi__lannh += '  delete_table(out_table)\n'
    pfyi__lannh += '  delete_table(table_total)\n'
    pfyi__lannh += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(dou__dawf)))
    dqml__okjl = {}
    exec(pfyi__lannh, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'sample_table': sample_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, dqml__okjl)
    impl = dqml__okjl['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    dou__dawf = len(data)
    pfyi__lannh = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    pfyi__lannh += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        dou__dawf)))
    pfyi__lannh += '  table_total = arr_info_list_to_table(info_list_total)\n'
    pfyi__lannh += '  keep_i = 0\n'
    pfyi__lannh += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for vevxa__gyw in range(dou__dawf):
        pfyi__lannh += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(vevxa__gyw, vevxa__gyw, vevxa__gyw))
    pfyi__lannh += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(dou__dawf))
    pfyi__lannh += '  delete_table(out_table)\n'
    pfyi__lannh += '  delete_table(table_total)\n'
    pfyi__lannh += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(dou__dawf)))
    dqml__okjl = {}
    exec(pfyi__lannh, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, dqml__okjl)
    impl = dqml__okjl['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        xvco__epgr = [array_to_info(data_arr)]
        frjy__egie = arr_info_list_to_table(xvco__epgr)
        unz__fxlpn = 0
        nygp__egb = drop_duplicates_table(frjy__egie, parallel, 1,
            unz__fxlpn, False, True)
        rgvsb__kfme = info_to_array(info_from_table(nygp__egb, 0), data_arr)
        delete_table(nygp__egb)
        delete_table(frjy__egie)
        return rgvsb__kfme
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    obsz__fhnly = len(data.types)
    fphl__uaam = [('out' + str(i)) for i in range(obsz__fhnly)]
    skxz__gwsj = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    qmsu__jmlt = ['isna(data[{}], i)'.format(i) for i in skxz__gwsj]
    vjrfe__yji = 'not ({})'.format(' or '.join(qmsu__jmlt))
    if not is_overload_none(thresh):
        vjrfe__yji = '(({}) <= ({}) - thresh)'.format(' + '.join(qmsu__jmlt
            ), obsz__fhnly - 1)
    elif how == 'all':
        vjrfe__yji = 'not ({})'.format(' and '.join(qmsu__jmlt))
    pfyi__lannh = 'def _dropna_imp(data, how, thresh, subset):\n'
    pfyi__lannh += '  old_len = len(data[0])\n'
    pfyi__lannh += '  new_len = 0\n'
    pfyi__lannh += '  for i in range(old_len):\n'
    pfyi__lannh += '    if {}:\n'.format(vjrfe__yji)
    pfyi__lannh += '      new_len += 1\n'
    for i, out in enumerate(fphl__uaam):
        if isinstance(data[i], bodo.CategoricalArrayType):
            pfyi__lannh += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            pfyi__lannh += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    pfyi__lannh += '  curr_ind = 0\n'
    pfyi__lannh += '  for i in range(old_len):\n'
    pfyi__lannh += '    if {}:\n'.format(vjrfe__yji)
    for i in range(obsz__fhnly):
        pfyi__lannh += '      if isna(data[{}], i):\n'.format(i)
        pfyi__lannh += '        setna({}, curr_ind)\n'.format(fphl__uaam[i])
        pfyi__lannh += '      else:\n'
        pfyi__lannh += '        {}[curr_ind] = data[{}][i]\n'.format(fphl__uaam
            [i], i)
    pfyi__lannh += '      curr_ind += 1\n'
    pfyi__lannh += '  return {}\n'.format(', '.join(fphl__uaam))
    dqml__okjl = {}
    oueav__crid = {'t{}'.format(i): den__jpa for i, den__jpa in enumerate(
        data.types)}
    oueav__crid.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(pfyi__lannh, oueav__crid, dqml__okjl)
    srq__yqlcb = dqml__okjl['_dropna_imp']
    return srq__yqlcb


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        hdn__pkh = arr.dtype
        xko__wls = hdn__pkh.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            voih__ufaj = init_nested_counts(xko__wls)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                voih__ufaj = add_nested_counts(voih__ufaj, val[ind])
            rgvsb__kfme = bodo.utils.utils.alloc_type(n, hdn__pkh, voih__ufaj)
            for vfdqa__tfalk in range(n):
                if bodo.libs.array_kernels.isna(arr, vfdqa__tfalk):
                    setna(rgvsb__kfme, vfdqa__tfalk)
                    continue
                val = arr[vfdqa__tfalk]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(rgvsb__kfme, vfdqa__tfalk)
                    continue
                rgvsb__kfme[vfdqa__tfalk] = val[ind]
            return rgvsb__kfme
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    wkzr__ttt = _to_readonly(arr_types.types[0])
    return all(isinstance(den__jpa, CategoricalArrayType) and _to_readonly(
        den__jpa) == wkzr__ttt for den__jpa in arr_types.types)


def concat(arr_list):
    return pd.concat(arr_list)


@overload(concat, no_unliteral=True)
def concat_overload(arr_list):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arr_list.
        dtype, 'bodo.concat()')
    if isinstance(arr_list, bodo.NullableTupleType):
        return lambda arr_list: bodo.libs.array_kernels.concat(arr_list._data)
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, ArrayItemArrayType):
        ubp__psuwl = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            xjx__agg = 0
            pdtt__xjjl = []
            for A in arr_list:
                keyv__axfa = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                pdtt__xjjl.append(bodo.libs.array_item_arr_ext.get_data(A))
                xjx__agg += keyv__axfa
            iai__xfbba = np.empty(xjx__agg + 1, offset_type)
            ugvz__zfv = bodo.libs.array_kernels.concat(pdtt__xjjl)
            oju__xtm = np.empty(xjx__agg + 7 >> 3, np.uint8)
            zzu__fyyk = 0
            uikel__yyt = 0
            for A in arr_list:
                anky__tbft = bodo.libs.array_item_arr_ext.get_offsets(A)
                fty__ipxo = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                keyv__axfa = len(A)
                txqf__yhgr = anky__tbft[keyv__axfa]
                for i in range(keyv__axfa):
                    iai__xfbba[i + zzu__fyyk] = anky__tbft[i] + uikel__yyt
                    vlf__lte = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        fty__ipxo, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(oju__xtm, i +
                        zzu__fyyk, vlf__lte)
                zzu__fyyk += keyv__axfa
                uikel__yyt += txqf__yhgr
            iai__xfbba[zzu__fyyk] = uikel__yyt
            rgvsb__kfme = bodo.libs.array_item_arr_ext.init_array_item_array(
                xjx__agg, ugvz__zfv, iai__xfbba, oju__xtm)
            return rgvsb__kfme
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        lvk__ntjbp = arr_list.dtype.names
        pfyi__lannh = 'def struct_array_concat_impl(arr_list):\n'
        pfyi__lannh += f'    n_all = 0\n'
        for i in range(len(lvk__ntjbp)):
            pfyi__lannh += f'    concat_list{i} = []\n'
        pfyi__lannh += '    for A in arr_list:\n'
        pfyi__lannh += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(lvk__ntjbp)):
            pfyi__lannh += f'        concat_list{i}.append(data_tuple[{i}])\n'
        pfyi__lannh += '        n_all += len(A)\n'
        pfyi__lannh += '    n_bytes = (n_all + 7) >> 3\n'
        pfyi__lannh += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        pfyi__lannh += '    curr_bit = 0\n'
        pfyi__lannh += '    for A in arr_list:\n'
        pfyi__lannh += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        pfyi__lannh += '        for j in range(len(A)):\n'
        pfyi__lannh += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        pfyi__lannh += """            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)
"""
        pfyi__lannh += '            curr_bit += 1\n'
        pfyi__lannh += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        gds__dpyrd = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(lvk__ntjbp))])
        pfyi__lannh += f'        ({gds__dpyrd},),\n'
        pfyi__lannh += '        new_mask,\n'
        pfyi__lannh += f'        {lvk__ntjbp},\n'
        pfyi__lannh += '    )\n'
        dqml__okjl = {}
        exec(pfyi__lannh, {'bodo': bodo, 'np': np}, dqml__okjl)
        return dqml__okjl['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            ncqny__dzqc = 0
            for A in arr_list:
                ncqny__dzqc += len(A)
            wkf__qhxqi = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(ncqny__dzqc))
            csl__efl = 0
            for A in arr_list:
                for i in range(len(A)):
                    wkf__qhxqi._data[i + csl__efl] = A._data[i]
                    vlf__lte = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(wkf__qhxqi.
                        _null_bitmap, i + csl__efl, vlf__lte)
                csl__efl += len(A)
            return wkf__qhxqi
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            ncqny__dzqc = 0
            for A in arr_list:
                ncqny__dzqc += len(A)
            wkf__qhxqi = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(ncqny__dzqc))
            csl__efl = 0
            for A in arr_list:
                for i in range(len(A)):
                    wkf__qhxqi._days_data[i + csl__efl] = A._days_data[i]
                    wkf__qhxqi._seconds_data[i + csl__efl] = A._seconds_data[i]
                    wkf__qhxqi._microseconds_data[i + csl__efl
                        ] = A._microseconds_data[i]
                    vlf__lte = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(wkf__qhxqi.
                        _null_bitmap, i + csl__efl, vlf__lte)
                csl__efl += len(A)
            return wkf__qhxqi
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        hya__phy = arr_list.dtype.precision
        ika__crz = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            ncqny__dzqc = 0
            for A in arr_list:
                ncqny__dzqc += len(A)
            wkf__qhxqi = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                ncqny__dzqc, hya__phy, ika__crz)
            csl__efl = 0
            for A in arr_list:
                for i in range(len(A)):
                    wkf__qhxqi._data[i + csl__efl] = A._data[i]
                    vlf__lte = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(wkf__qhxqi.
                        _null_bitmap, i + csl__efl, vlf__lte)
                csl__efl += len(A)
            return wkf__qhxqi
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        den__jpa) for den__jpa in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            mal__plw = arr_list.types[0]
        else:
            mal__plw = arr_list.dtype
        mal__plw = to_str_arr_if_dict_array(mal__plw)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            eguy__fmzwe = 0
            ythwn__ljfru = 0
            for A in arr_list:
                arr = A
                eguy__fmzwe += len(arr)
                ythwn__ljfru += bodo.libs.str_arr_ext.num_total_chars(arr)
            rgvsb__kfme = bodo.utils.utils.alloc_type(eguy__fmzwe, mal__plw,
                (ythwn__ljfru,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(rgvsb__kfme, -1)
            vax__dcp = 0
            gkuuf__dar = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(rgvsb__kfme,
                    arr, vax__dcp, gkuuf__dar)
                vax__dcp += len(arr)
                gkuuf__dar += bodo.libs.str_arr_ext.num_total_chars(arr)
            return rgvsb__kfme
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(den__jpa.dtype, types.Integer) for
        den__jpa in arr_list.types) and any(isinstance(den__jpa,
        IntegerArrayType) for den__jpa in arr_list.types):

        def impl_int_arr_list(arr_list):
            duw__hpr = convert_to_nullable_tup(arr_list)
            kicve__mbv = []
            rlrfh__trbnh = 0
            for A in duw__hpr:
                kicve__mbv.append(A._data)
                rlrfh__trbnh += len(A)
            ugvz__zfv = bodo.libs.array_kernels.concat(kicve__mbv)
            hkl__tbt = rlrfh__trbnh + 7 >> 3
            vti__atiux = np.empty(hkl__tbt, np.uint8)
            zrt__sre = 0
            for A in duw__hpr:
                tir__frk = A._null_bitmap
                for vfdqa__tfalk in range(len(A)):
                    vlf__lte = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        tir__frk, vfdqa__tfalk)
                    bodo.libs.int_arr_ext.set_bit_to_arr(vti__atiux,
                        zrt__sre, vlf__lte)
                    zrt__sre += 1
            return bodo.libs.int_arr_ext.init_integer_array(ugvz__zfv,
                vti__atiux)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(den__jpa.dtype == types.bool_ for den__jpa in
        arr_list.types) and any(den__jpa == boolean_array for den__jpa in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            duw__hpr = convert_to_nullable_tup(arr_list)
            kicve__mbv = []
            rlrfh__trbnh = 0
            for A in duw__hpr:
                kicve__mbv.append(A._data)
                rlrfh__trbnh += len(A)
            ugvz__zfv = bodo.libs.array_kernels.concat(kicve__mbv)
            hkl__tbt = rlrfh__trbnh + 7 >> 3
            vti__atiux = np.empty(hkl__tbt, np.uint8)
            zrt__sre = 0
            for A in duw__hpr:
                tir__frk = A._null_bitmap
                for vfdqa__tfalk in range(len(A)):
                    vlf__lte = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        tir__frk, vfdqa__tfalk)
                    bodo.libs.int_arr_ext.set_bit_to_arr(vti__atiux,
                        zrt__sre, vlf__lte)
                    zrt__sre += 1
            return bodo.libs.bool_arr_ext.init_bool_array(ugvz__zfv, vti__atiux
                )
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            epby__qlv = []
            for A in arr_list:
                epby__qlv.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                epby__qlv), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        zdq__qqlso = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        pfyi__lannh = 'def impl(arr_list):\n'
        pfyi__lannh += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({zdq__qqlso},)), arr_list[0].dtype)
"""
        oyj__xaw = {}
        exec(pfyi__lannh, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, oyj__xaw)
        return oyj__xaw['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            rlrfh__trbnh = 0
            for A in arr_list:
                rlrfh__trbnh += len(A)
            rgvsb__kfme = np.empty(rlrfh__trbnh, dtype)
            xmdkw__zsh = 0
            for A in arr_list:
                n = len(A)
                rgvsb__kfme[xmdkw__zsh:xmdkw__zsh + n] = A
                xmdkw__zsh += n
            return rgvsb__kfme
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(den__jpa, (
        types.Array, IntegerArrayType)) and isinstance(den__jpa.dtype,
        types.Integer) for den__jpa in arr_list.types) and any(isinstance(
        den__jpa, types.Array) and isinstance(den__jpa.dtype, types.Float) for
        den__jpa in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            irw__qyar = []
            for A in arr_list:
                irw__qyar.append(A._data)
            lfjki__ywdd = bodo.libs.array_kernels.concat(irw__qyar)
            yxos__tigbf = bodo.libs.map_arr_ext.init_map_arr(lfjki__ywdd)
            return yxos__tigbf
        return impl_map_arr_list
    for xhr__ekf in arr_list:
        if not isinstance(xhr__ekf, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(den__jpa.astype(np.float64) for den__jpa in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    dou__dawf = len(arr_tup.types)
    pfyi__lannh = 'def f(arr_tup):\n'
    pfyi__lannh += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(dou__dawf
        )), ',' if dou__dawf == 1 else '')
    dqml__okjl = {}
    exec(pfyi__lannh, {'np': np}, dqml__okjl)
    svl__xsu = dqml__okjl['f']
    return svl__xsu


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    dou__dawf = len(arr_tup.types)
    mvtm__bvf = find_common_np_dtype(arr_tup.types)
    xko__wls = None
    pkgwk__dat = ''
    if isinstance(mvtm__bvf, types.Integer):
        xko__wls = bodo.libs.int_arr_ext.IntDtype(mvtm__bvf)
        pkgwk__dat = '.astype(out_dtype, False)'
    pfyi__lannh = 'def f(arr_tup):\n'
    pfyi__lannh += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, pkgwk__dat) for i in range(dou__dawf)), ',' if dou__dawf ==
        1 else '')
    dqml__okjl = {}
    exec(pfyi__lannh, {'bodo': bodo, 'out_dtype': xko__wls}, dqml__okjl)
    nnvbr__ilpuf = dqml__okjl['f']
    return nnvbr__ilpuf


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, qrogx__oyh = build_set_seen_na(A)
        return len(s) + int(not dropna and qrogx__oyh)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        jeool__tqhy = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        aay__enauw = len(jeool__tqhy)
        return bodo.libs.distributed_api.dist_reduce(aay__enauw, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([xisk__yauho for xisk__yauho in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        vmh__mcdoz = np.finfo(A.dtype(1).dtype).max
    else:
        vmh__mcdoz = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        rgvsb__kfme = np.empty(n, A.dtype)
        rvfp__skp = vmh__mcdoz
        for i in range(n):
            rvfp__skp = min(rvfp__skp, A[i])
            rgvsb__kfme[i] = rvfp__skp
        return rgvsb__kfme
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        vmh__mcdoz = np.finfo(A.dtype(1).dtype).min
    else:
        vmh__mcdoz = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        rgvsb__kfme = np.empty(n, A.dtype)
        rvfp__skp = vmh__mcdoz
        for i in range(n):
            rvfp__skp = max(rvfp__skp, A[i])
            rgvsb__kfme[i] = rvfp__skp
        return rgvsb__kfme
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        cap__ilbx = arr_info_list_to_table([array_to_info(A)])
        sha__jiktp = 1
        unz__fxlpn = 0
        nygp__egb = drop_duplicates_table(cap__ilbx, parallel, sha__jiktp,
            unz__fxlpn, dropna, True)
        rgvsb__kfme = info_to_array(info_from_table(nygp__egb, 0), A)
        delete_table(cap__ilbx)
        delete_table(nygp__egb)
        return rgvsb__kfme
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    ubp__psuwl = bodo.utils.typing.to_nullable_type(arr.dtype)
    qrixs__cbai = index_arr
    eaov__xpowy = qrixs__cbai.dtype

    def impl(arr, index_arr):
        n = len(arr)
        voih__ufaj = init_nested_counts(ubp__psuwl)
        uetzh__shm = init_nested_counts(eaov__xpowy)
        for i in range(n):
            pzw__aivq = index_arr[i]
            if isna(arr, i):
                voih__ufaj = (voih__ufaj[0] + 1,) + voih__ufaj[1:]
                uetzh__shm = add_nested_counts(uetzh__shm, pzw__aivq)
                continue
            hrqrz__kdy = arr[i]
            if len(hrqrz__kdy) == 0:
                voih__ufaj = (voih__ufaj[0] + 1,) + voih__ufaj[1:]
                uetzh__shm = add_nested_counts(uetzh__shm, pzw__aivq)
                continue
            voih__ufaj = add_nested_counts(voih__ufaj, hrqrz__kdy)
            for honoj__phuh in range(len(hrqrz__kdy)):
                uetzh__shm = add_nested_counts(uetzh__shm, pzw__aivq)
        rgvsb__kfme = bodo.utils.utils.alloc_type(voih__ufaj[0], ubp__psuwl,
            voih__ufaj[1:])
        jdb__eul = bodo.utils.utils.alloc_type(voih__ufaj[0], qrixs__cbai,
            uetzh__shm)
        uikel__yyt = 0
        for i in range(n):
            if isna(arr, i):
                setna(rgvsb__kfme, uikel__yyt)
                jdb__eul[uikel__yyt] = index_arr[i]
                uikel__yyt += 1
                continue
            hrqrz__kdy = arr[i]
            txqf__yhgr = len(hrqrz__kdy)
            if txqf__yhgr == 0:
                setna(rgvsb__kfme, uikel__yyt)
                jdb__eul[uikel__yyt] = index_arr[i]
                uikel__yyt += 1
                continue
            rgvsb__kfme[uikel__yyt:uikel__yyt + txqf__yhgr] = hrqrz__kdy
            jdb__eul[uikel__yyt:uikel__yyt + txqf__yhgr] = index_arr[i]
            uikel__yyt += txqf__yhgr
        return rgvsb__kfme, jdb__eul
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    ubp__psuwl = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        voih__ufaj = init_nested_counts(ubp__psuwl)
        for i in range(n):
            if isna(arr, i):
                voih__ufaj = (voih__ufaj[0] + 1,) + voih__ufaj[1:]
                gduy__ertlr = 1
            else:
                hrqrz__kdy = arr[i]
                fgw__kam = len(hrqrz__kdy)
                if fgw__kam == 0:
                    voih__ufaj = (voih__ufaj[0] + 1,) + voih__ufaj[1:]
                    gduy__ertlr = 1
                    continue
                else:
                    voih__ufaj = add_nested_counts(voih__ufaj, hrqrz__kdy)
                    gduy__ertlr = fgw__kam
            if counts[i] != gduy__ertlr:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        rgvsb__kfme = bodo.utils.utils.alloc_type(voih__ufaj[0], ubp__psuwl,
            voih__ufaj[1:])
        uikel__yyt = 0
        for i in range(n):
            if isna(arr, i):
                setna(rgvsb__kfme, uikel__yyt)
                uikel__yyt += 1
                continue
            hrqrz__kdy = arr[i]
            txqf__yhgr = len(hrqrz__kdy)
            if txqf__yhgr == 0:
                setna(rgvsb__kfme, uikel__yyt)
                uikel__yyt += 1
                continue
            rgvsb__kfme[uikel__yyt:uikel__yyt + txqf__yhgr] = hrqrz__kdy
            uikel__yyt += txqf__yhgr
        return rgvsb__kfme
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(loj__dwlb) for loj__dwlb in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        msms__ufuiz = 'np.empty(n, np.int64)'
        gfcex__gnnu = 'out_arr[i] = 1'
        agzip__inc = 'max(len(arr[i]), 1)'
    else:
        msms__ufuiz = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        gfcex__gnnu = 'bodo.libs.array_kernels.setna(out_arr, i)'
        agzip__inc = 'len(arr[i])'
    pfyi__lannh = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {msms__ufuiz}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {gfcex__gnnu}
        else:
            out_arr[i] = {agzip__inc}
    return out_arr
    """
    dqml__okjl = {}
    exec(pfyi__lannh, {'bodo': bodo, 'numba': numba, 'np': np}, dqml__okjl)
    impl = dqml__okjl['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    qrixs__cbai = index_arr
    eaov__xpowy = qrixs__cbai.dtype

    def impl(arr, pat, n, index_arr):
        yprll__mmck = pat is not None and len(pat) > 1
        if yprll__mmck:
            qkuhd__nrmd = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        zinp__bmpot = len(arr)
        eguy__fmzwe = 0
        ythwn__ljfru = 0
        uetzh__shm = init_nested_counts(eaov__xpowy)
        for i in range(zinp__bmpot):
            pzw__aivq = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                eguy__fmzwe += 1
                uetzh__shm = add_nested_counts(uetzh__shm, pzw__aivq)
                continue
            if yprll__mmck:
                qfucc__aunby = qkuhd__nrmd.split(arr[i], maxsplit=n)
            else:
                qfucc__aunby = arr[i].split(pat, n)
            eguy__fmzwe += len(qfucc__aunby)
            for s in qfucc__aunby:
                uetzh__shm = add_nested_counts(uetzh__shm, pzw__aivq)
                ythwn__ljfru += bodo.libs.str_arr_ext.get_utf8_size(s)
        rgvsb__kfme = bodo.libs.str_arr_ext.pre_alloc_string_array(eguy__fmzwe,
            ythwn__ljfru)
        jdb__eul = bodo.utils.utils.alloc_type(eguy__fmzwe, qrixs__cbai,
            uetzh__shm)
        ttzse__pwv = 0
        for vfdqa__tfalk in range(zinp__bmpot):
            if isna(arr, vfdqa__tfalk):
                rgvsb__kfme[ttzse__pwv] = ''
                bodo.libs.array_kernels.setna(rgvsb__kfme, ttzse__pwv)
                jdb__eul[ttzse__pwv] = index_arr[vfdqa__tfalk]
                ttzse__pwv += 1
                continue
            if yprll__mmck:
                qfucc__aunby = qkuhd__nrmd.split(arr[vfdqa__tfalk], maxsplit=n)
            else:
                qfucc__aunby = arr[vfdqa__tfalk].split(pat, n)
            ueqpf__gkbs = len(qfucc__aunby)
            rgvsb__kfme[ttzse__pwv:ttzse__pwv + ueqpf__gkbs] = qfucc__aunby
            jdb__eul[ttzse__pwv:ttzse__pwv + ueqpf__gkbs] = index_arr[
                vfdqa__tfalk]
            ttzse__pwv += ueqpf__gkbs
        return rgvsb__kfme, jdb__eul
    return impl


def gen_na_array(n, arr):
    return np.full(n, np.nan)


@overload(gen_na_array, no_unliteral=True)
def overload_gen_na_array(n, arr):
    if isinstance(arr, types.TypeRef):
        arr = arr.instance_type
    dtype = arr.dtype
    if not isinstance(arr, IntegerArrayType) and isinstance(dtype, (types.
        Integer, types.Float)):
        dtype = dtype if isinstance(dtype, types.Float) else types.float64

        def impl_float(n, arr):
            numba.parfors.parfor.init_prange()
            rgvsb__kfme = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                rgvsb__kfme[i] = np.nan
            return rgvsb__kfme
        return impl_float
    qcnk__olzu = to_str_arr_if_dict_array(arr)

    def impl(n, arr):
        numba.parfors.parfor.init_prange()
        rgvsb__kfme = bodo.utils.utils.alloc_type(n, qcnk__olzu, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(rgvsb__kfme, i)
        return rgvsb__kfme
    return impl


def gen_na_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_gen_na_array = (
    gen_na_array_equiv)


def resize_and_copy(A, new_len):
    return A


@overload(resize_and_copy, no_unliteral=True)
def overload_resize_and_copy(A, old_size, new_len):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.resize_and_copy()')
    qtktw__ihqv = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            rgvsb__kfme = bodo.utils.utils.alloc_type(new_len, qtktw__ihqv)
            bodo.libs.str_arr_ext.str_copy_ptr(rgvsb__kfme.ctypes, 0, A.
                ctypes, old_size)
            return rgvsb__kfme
        return impl_char

    def impl(A, old_size, new_len):
        rgvsb__kfme = bodo.utils.utils.alloc_type(new_len, qtktw__ihqv, (-1,))
        rgvsb__kfme[:old_size] = A[:old_size]
        return rgvsb__kfme
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    ird__vox = math.ceil((stop - start) / step)
    return int(max(ird__vox, 0))


def calc_nitems_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    if guard(find_const, self.func_ir, args[0]) == 0 and guard(find_const,
        self.func_ir, args[2]) == 1:
        return ArrayAnalysis.AnalyzeResult(shape=args[1], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_calc_nitems = (
    calc_nitems_equiv)


def arange_parallel_impl(return_type, *args):
    dtype = as_dtype(return_type.dtype)

    def arange_1(stop):
        return np.arange(0, stop, 1, dtype)

    def arange_2(start, stop):
        return np.arange(start, stop, 1, dtype)

    def arange_3(start, stop, step):
        return np.arange(start, stop, step, dtype)
    if any(isinstance(xisk__yauho, types.Complex) for xisk__yauho in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            cjv__ombf = (stop - start) / step
            ird__vox = math.ceil(cjv__ombf.real)
            gxt__vnmo = math.ceil(cjv__ombf.imag)
            qxjtu__pbsk = int(max(min(gxt__vnmo, ird__vox), 0))
            arr = np.empty(qxjtu__pbsk, dtype)
            for i in numba.parfors.parfor.internal_prange(qxjtu__pbsk):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            qxjtu__pbsk = bodo.libs.array_kernels.calc_nitems(start, stop, step
                )
            arr = np.empty(qxjtu__pbsk, dtype)
            for i in numba.parfors.parfor.internal_prange(qxjtu__pbsk):
                arr[i] = start + i * step
            return arr
    if len(args) == 1:
        return arange_1
    elif len(args) == 2:
        return arange_2
    elif len(args) == 3:
        return arange_3
    elif len(args) == 4:
        return arange_4
    else:
        raise BodoError('parallel arange with types {}'.format(args))


if bodo.numba_compat._check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.arange_parallel_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c72b0390b4f3e52dcc5426bd42c6b55ff96bae5a425381900985d36e7527a4bd':
        warnings.warn('numba.parfors.parfor.arange_parallel_impl has changed')
numba.parfors.parfor.swap_functions_map['arange', 'numpy'
    ] = arange_parallel_impl


def sort(arr, ascending, inplace):
    return np.sort(arr)


@overload(sort, no_unliteral=True)
def overload_sort(arr, ascending, inplace):

    def impl(arr, ascending, inplace):
        n = len(arr)
        data = np.arange(n),
        faskl__rcjr = arr,
        if not inplace:
            faskl__rcjr = arr.copy(),
        ynafa__mgnmj = bodo.libs.str_arr_ext.to_list_if_immutable_arr(
            faskl__rcjr)
        ker__lwi = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(ynafa__mgnmj, 0, n, ker__lwi)
        if not ascending:
            bodo.libs.timsort.reverseRange(ynafa__mgnmj, 0, n, ker__lwi)
        bodo.libs.str_arr_ext.cp_str_list_to_array(faskl__rcjr, ynafa__mgnmj)
        return faskl__rcjr[0]
    return impl


def overload_array_max(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).max()
        return impl


overload(np.max, inline='always', no_unliteral=True)(overload_array_max)
overload(max, inline='always', no_unliteral=True)(overload_array_max)


def overload_array_min(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).min()
        return impl


overload(np.min, inline='always', no_unliteral=True)(overload_array_min)
overload(min, inline='always', no_unliteral=True)(overload_array_min)


def overload_array_sum(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).sum()
    return impl


overload(np.sum, inline='always', no_unliteral=True)(overload_array_sum)
overload(sum, inline='always', no_unliteral=True)(overload_array_sum)


@overload(np.prod, inline='always', no_unliteral=True)
def overload_array_prod(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).prod()
    return impl


def nonzero(arr):
    return arr,


@overload(nonzero, no_unliteral=True)
def nonzero_overload(A, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.nonzero()')
    if not bodo.utils.utils.is_array_typ(A, False):
        return

    def impl(A, parallel=False):
        n = len(A)
        if parallel:
            offset = bodo.libs.distributed_api.dist_exscan(n, Reduce_Type.
                Sum.value)
        else:
            offset = 0
        yxos__tigbf = []
        for i in range(n):
            if A[i]:
                yxos__tigbf.append(i + offset)
        return np.array(yxos__tigbf, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    qtktw__ihqv = element_type(A)
    if qtktw__ihqv == types.unicode_type:
        null_value = '""'
    elif qtktw__ihqv == types.bool_:
        null_value = 'False'
    elif qtktw__ihqv == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif qtktw__ihqv == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    ttzse__pwv = 'i'
    ygcsa__qiy = False
    fkltz__pyh = get_overload_const_str(method)
    if fkltz__pyh in ('ffill', 'pad'):
        lig__hiqm = 'n'
        send_right = True
    elif fkltz__pyh in ('backfill', 'bfill'):
        lig__hiqm = 'n-1, -1, -1'
        send_right = False
        if qtktw__ihqv == types.unicode_type:
            ttzse__pwv = '(n - 1) - i'
            ygcsa__qiy = True
    pfyi__lannh = 'def impl(A, method, parallel=False):\n'
    pfyi__lannh += '  A = decode_if_dict_array(A)\n'
    pfyi__lannh += '  has_last_value = False\n'
    pfyi__lannh += f'  last_value = {null_value}\n'
    pfyi__lannh += '  if parallel:\n'
    pfyi__lannh += '    rank = bodo.libs.distributed_api.get_rank()\n'
    pfyi__lannh += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    pfyi__lannh += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    pfyi__lannh += '  n = len(A)\n'
    pfyi__lannh += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    pfyi__lannh += f'  for i in range({lig__hiqm}):\n'
    pfyi__lannh += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    pfyi__lannh += (
        f'      bodo.libs.array_kernels.setna(out_arr, {ttzse__pwv})\n')
    pfyi__lannh += '      continue\n'
    pfyi__lannh += '    s = A[i]\n'
    pfyi__lannh += '    if bodo.libs.array_kernels.isna(A, i):\n'
    pfyi__lannh += '      s = last_value\n'
    pfyi__lannh += f'    out_arr[{ttzse__pwv}] = s\n'
    pfyi__lannh += '    last_value = s\n'
    pfyi__lannh += '    has_last_value = True\n'
    if ygcsa__qiy:
        pfyi__lannh += '  return out_arr[::-1]\n'
    else:
        pfyi__lannh += '  return out_arr\n'
    dnsxm__soyj = {}
    exec(pfyi__lannh, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, dnsxm__soyj)
    impl = dnsxm__soyj['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        ump__kbft = 0
        tzzij__kasc = n_pes - 1
        cci__egwwd = np.int32(rank + 1)
        gfv__srozw = np.int32(rank - 1)
        vjyal__ciw = len(in_arr) - 1
        zmje__riw = -1
        xfiu__tlihr = -1
    else:
        ump__kbft = n_pes - 1
        tzzij__kasc = 0
        cci__egwwd = np.int32(rank - 1)
        gfv__srozw = np.int32(rank + 1)
        vjyal__ciw = 0
        zmje__riw = len(in_arr)
        xfiu__tlihr = 1
    lxbr__zmww = np.int32(bodo.hiframes.rolling.comm_border_tag)
    tlno__wyusb = np.empty(1, dtype=np.bool_)
    oqxgs__diw = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    ncpc__xrje = np.empty(1, dtype=np.bool_)
    idp__prgr = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    dozac__mfbcc = False
    tctpi__ghabv = null_value
    for i in range(vjyal__ciw, zmje__riw, xfiu__tlihr):
        if not isna(in_arr, i):
            dozac__mfbcc = True
            tctpi__ghabv = in_arr[i]
            break
    if rank != ump__kbft:
        iish__epczl = bodo.libs.distributed_api.irecv(tlno__wyusb, 1,
            gfv__srozw, lxbr__zmww, True)
        bodo.libs.distributed_api.wait(iish__epczl, True)
        csqc__nhop = bodo.libs.distributed_api.irecv(oqxgs__diw, 1,
            gfv__srozw, lxbr__zmww, True)
        bodo.libs.distributed_api.wait(csqc__nhop, True)
        brfkd__ybzo = tlno__wyusb[0]
        wwit__vppx = oqxgs__diw[0]
    else:
        brfkd__ybzo = False
        wwit__vppx = null_value
    if dozac__mfbcc:
        ncpc__xrje[0] = dozac__mfbcc
        idp__prgr[0] = tctpi__ghabv
    else:
        ncpc__xrje[0] = brfkd__ybzo
        idp__prgr[0] = wwit__vppx
    if rank != tzzij__kasc:
        ngx__ktcbv = bodo.libs.distributed_api.isend(ncpc__xrje, 1,
            cci__egwwd, lxbr__zmww, True)
        cuhcn__voq = bodo.libs.distributed_api.isend(idp__prgr, 1,
            cci__egwwd, lxbr__zmww, True)
    return brfkd__ybzo, wwit__vppx


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    ron__powrn = {'axis': axis, 'kind': kind, 'order': order}
    ervf__rtqe = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', ron__powrn, ervf__rtqe, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    qtktw__ihqv = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            A = decode_if_dict_array(A)
            zinp__bmpot = len(A)
            rgvsb__kfme = bodo.utils.utils.alloc_type(zinp__bmpot * repeats,
                qtktw__ihqv, (-1,))
            for i in range(zinp__bmpot):
                ttzse__pwv = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for vfdqa__tfalk in range(repeats):
                        bodo.libs.array_kernels.setna(rgvsb__kfme, 
                            ttzse__pwv + vfdqa__tfalk)
                else:
                    rgvsb__kfme[ttzse__pwv:ttzse__pwv + repeats] = A[i]
            return rgvsb__kfme
        return impl_int

    def impl_arr(A, repeats):
        A = decode_if_dict_array(A)
        zinp__bmpot = len(A)
        rgvsb__kfme = bodo.utils.utils.alloc_type(repeats.sum(),
            qtktw__ihqv, (-1,))
        ttzse__pwv = 0
        for i in range(zinp__bmpot):
            colst__gmm = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for vfdqa__tfalk in range(colst__gmm):
                    bodo.libs.array_kernels.setna(rgvsb__kfme, ttzse__pwv +
                        vfdqa__tfalk)
            else:
                rgvsb__kfme[ttzse__pwv:ttzse__pwv + colst__gmm] = A[i]
            ttzse__pwv += colst__gmm
        return rgvsb__kfme
    return impl_arr


@overload(np.repeat, inline='always', no_unliteral=True)
def np_repeat(A, repeats):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    if not isinstance(repeats, types.Integer):
        raise BodoError(
            'Only integer type supported for repeats in np.repeat()')

    def impl(A, repeats):
        return bodo.libs.array_kernels.repeat_kernel(A, repeats)
    return impl


@numba.generated_jit
def repeat_like(A, dist_like_arr):
    if not bodo.utils.utils.is_array_typ(A, False
        ) or not bodo.utils.utils.is_array_typ(dist_like_arr, False):
        raise BodoError('Both A and dist_like_arr must be array-like.')

    def impl(A, dist_like_arr):
        return bodo.libs.array_kernels.repeat_kernel(A, len(dist_like_arr))
    return impl


@overload(np.unique, inline='always', no_unliteral=True)
def np_unique(A):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return

    def impl(A):
        fapa__wnfnw = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(fapa__wnfnw, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        grnoy__ste = bodo.libs.array_kernels.concat([A1, A2])
        krs__jdnkg = bodo.libs.array_kernels.unique(grnoy__ste)
        return pd.Series(krs__jdnkg).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    ron__powrn = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    ervf__rtqe = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', ron__powrn, ervf__rtqe, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        yhp__vbj = bodo.libs.array_kernels.unique(A1)
        thcny__cuor = bodo.libs.array_kernels.unique(A2)
        grnoy__ste = bodo.libs.array_kernels.concat([yhp__vbj, thcny__cuor])
        zll__jsvhh = pd.Series(grnoy__ste).sort_values().values
        return slice_array_intersect1d(zll__jsvhh)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    anm__fqm = arr[1:] == arr[:-1]
    return arr[:-1][anm__fqm]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    lxbr__zmww = np.int32(bodo.hiframes.rolling.comm_border_tag)
    zez__akqfp = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        qma__bvpuf = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), lxbr__zmww, True)
        bodo.libs.distributed_api.wait(qma__bvpuf, True)
    if rank == n_pes - 1:
        return None
    else:
        tdqt__ozzdz = bodo.libs.distributed_api.irecv(zez__akqfp, 1, np.
            int32(rank + 1), lxbr__zmww, True)
        bodo.libs.distributed_api.wait(tdqt__ozzdz, True)
        return zez__akqfp[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    anm__fqm = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            anm__fqm[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        twi__rlb = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == twi__rlb:
            anm__fqm[n - 1] = True
    return anm__fqm


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    ron__powrn = {'assume_unique': assume_unique}
    ervf__rtqe = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', ron__powrn, ervf__rtqe, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        yhp__vbj = bodo.libs.array_kernels.unique(A1)
        thcny__cuor = bodo.libs.array_kernels.unique(A2)
        anm__fqm = calculate_mask_setdiff1d(yhp__vbj, thcny__cuor)
        return pd.Series(yhp__vbj[anm__fqm]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    anm__fqm = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        anm__fqm &= A1 != A2[i]
    return anm__fqm


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    ron__powrn = {'retstep': retstep, 'axis': axis}
    ervf__rtqe = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', ron__powrn, ervf__rtqe, 'numpy')
    kmhcp__jjby = False
    if is_overload_none(dtype):
        qtktw__ihqv = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            kmhcp__jjby = True
        qtktw__ihqv = numba.np.numpy_support.as_dtype(dtype).type
    if kmhcp__jjby:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            zkvs__veof = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            rgvsb__kfme = np.empty(num, qtktw__ihqv)
            for i in numba.parfors.parfor.internal_prange(num):
                rgvsb__kfme[i] = qtktw__ihqv(np.floor(start + i * zkvs__veof))
            return rgvsb__kfme
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            zkvs__veof = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            rgvsb__kfme = np.empty(num, qtktw__ihqv)
            for i in numba.parfors.parfor.internal_prange(num):
                rgvsb__kfme[i] = qtktw__ihqv(start + i * zkvs__veof)
            return rgvsb__kfme
        return impl


def np_linspace_get_stepsize(start, stop, num, endpoint):
    return 0


@overload(np_linspace_get_stepsize, no_unliteral=True)
def overload_np_linspace_get_stepsize(start, stop, num, endpoint):

    def impl(start, stop, num, endpoint):
        if num < 0:
            raise ValueError('np.linspace() Num must be >= 0')
        if endpoint:
            num -= 1
        if num > 1:
            return (stop - start) / num
        return 0
    return impl


@overload(operator.contains, no_unliteral=True)
def arr_contains(A, val):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'np.contains()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.dtype == types.
        unliteral(val)):
        return

    def impl(A, val):
        numba.parfors.parfor.init_prange()
        dou__dawf = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                dou__dawf += A[i] == val
        return dou__dawf > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    ron__powrn = {'axis': axis, 'out': out, 'keepdims': keepdims}
    ervf__rtqe = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', ron__powrn, ervf__rtqe, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        dou__dawf = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                dou__dawf += int(bool(A[i]))
        return dou__dawf > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    ron__powrn = {'axis': axis, 'out': out, 'keepdims': keepdims}
    ervf__rtqe = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', ron__powrn, ervf__rtqe, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        dou__dawf = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                dou__dawf += int(bool(A[i]))
        return dou__dawf == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    ron__powrn = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    ervf__rtqe = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', ron__powrn, ervf__rtqe, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        rmsi__iddb = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            rgvsb__kfme = np.empty(n, rmsi__iddb)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(rgvsb__kfme, i)
                    continue
                rgvsb__kfme[i] = np_cbrt_scalar(A[i], rmsi__iddb)
            return rgvsb__kfme
        return impl_arr
    rmsi__iddb = np.promote_types(numba.np.numpy_support.as_dtype(A), numba
        .np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, rmsi__iddb)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    alzdc__fdq = x < 0
    if alzdc__fdq:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if alzdc__fdq:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    umcj__imsl = isinstance(tup, (types.BaseTuple, types.List))
    axk__ongg = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for xhr__ekf in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(xhr__ekf,
                'numpy.hstack()')
            umcj__imsl = umcj__imsl and bodo.utils.utils.is_array_typ(xhr__ekf,
                False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        umcj__imsl = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif axk__ongg:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        xny__qaz = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for xhr__ekf in xny__qaz.types:
            axk__ongg = axk__ongg and bodo.utils.utils.is_array_typ(xhr__ekf,
                False)
    if not (umcj__imsl or axk__ongg):
        return
    if axk__ongg:

        def impl_series(tup):
            arr_tup = bodo.hiframes.pd_series_ext.get_series_data(tup)
            return bodo.libs.array_kernels.concat(arr_tup)
        return impl_series

    def impl(tup):
        return bodo.libs.array_kernels.concat(tup)
    return impl


@overload(np.random.multivariate_normal, inline='always', no_unliteral=True)
def np_random_multivariate_normal(mean, cov, size=None, check_valid='warn',
    tol=1e-08):
    ron__powrn = {'check_valid': check_valid, 'tol': tol}
    ervf__rtqe = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', ron__powrn,
        ervf__rtqe, 'numpy')
    if not isinstance(size, types.Integer):
        raise BodoError(
            'np.random.multivariate_normal() size argument is required and must be an integer'
            )
    if not (bodo.utils.utils.is_array_typ(mean, False) and mean.ndim == 1):
        raise BodoError(
            'np.random.multivariate_normal() mean must be a 1 dimensional numpy array'
            )
    if not (bodo.utils.utils.is_array_typ(cov, False) and cov.ndim == 2):
        raise BodoError(
            'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
            )

    def impl(mean, cov, size=None, check_valid='warn', tol=1e-08):
        _validate_multivar_norm(cov)
        fqft__txb = mean.shape[0]
        aqth__zfe = size, fqft__txb
        sdt__whwmi = np.random.standard_normal(aqth__zfe)
        cov = cov.astype(np.float64)
        xef__qrpr, s, hdsec__gvaxq = np.linalg.svd(cov)
        res = np.dot(sdt__whwmi, np.sqrt(s).reshape(fqft__txb, 1) *
            hdsec__gvaxq)
        yaqfk__jdwt = res + mean
        return yaqfk__jdwt
    return impl


def _validate_multivar_norm(cov):
    return


@overload(_validate_multivar_norm, no_unliteral=True)
def _overload_validate_multivar_norm(cov):

    def impl(cov):
        if cov.shape[0] != cov.shape[1]:
            raise ValueError(
                'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
                )
    return impl


def _nan_argmin(arr):
    return


@overload(_nan_argmin, no_unliteral=True)
def _overload_nan_argmin(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            numba.parfors.parfor.init_prange()
            yhdem__vztj = bodo.hiframes.series_kernels._get_type_max_value(arr)
            hrfja__bfi = typing.builtins.IndexValue(-1, yhdem__vztj)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                pcrdr__vqhyy = typing.builtins.IndexValue(i, arr[i])
                hrfja__bfi = min(hrfja__bfi, pcrdr__vqhyy)
            return hrfja__bfi.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        nos__iyg = bodo.hiframes.pd_categorical_ext.get_categories_int_type(arr
            .dtype)

        def impl_cat_arr(arr):
            nbtlh__hcjq = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            yhdem__vztj = nos__iyg(len(arr.dtype.categories) + 1)
            hrfja__bfi = typing.builtins.IndexValue(-1, yhdem__vztj)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                pcrdr__vqhyy = typing.builtins.IndexValue(i, nbtlh__hcjq[i])
                hrfja__bfi = min(hrfja__bfi, pcrdr__vqhyy)
            return hrfja__bfi.index
        return impl_cat_arr
    return lambda arr: arr.argmin()


def _nan_argmax(arr):
    return


@overload(_nan_argmax, no_unliteral=True)
def _overload_nan_argmax(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            n = len(arr)
            numba.parfors.parfor.init_prange()
            yhdem__vztj = bodo.hiframes.series_kernels._get_type_min_value(arr)
            hrfja__bfi = typing.builtins.IndexValue(-1, yhdem__vztj)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                pcrdr__vqhyy = typing.builtins.IndexValue(i, arr[i])
                hrfja__bfi = max(hrfja__bfi, pcrdr__vqhyy)
            return hrfja__bfi.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        nos__iyg = bodo.hiframes.pd_categorical_ext.get_categories_int_type(arr
            .dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            nbtlh__hcjq = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            yhdem__vztj = nos__iyg(-1)
            hrfja__bfi = typing.builtins.IndexValue(-1, yhdem__vztj)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                pcrdr__vqhyy = typing.builtins.IndexValue(i, nbtlh__hcjq[i])
                hrfja__bfi = max(hrfja__bfi, pcrdr__vqhyy)
            return hrfja__bfi.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
