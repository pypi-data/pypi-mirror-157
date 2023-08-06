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
        nob__bxtps = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = nob__bxtps
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        nob__bxtps = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = nob__bxtps
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
            lgkco__hvle = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            lgkco__hvle[ind + 1] = lgkco__hvle[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            lgkco__hvle = bodo.libs.array_item_arr_ext.get_offsets(arr)
            lgkco__hvle[ind + 1] = lgkco__hvle[ind]
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
    hkqk__bzxh = arr_tup.count
    kmd__yjn = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(hkqk__bzxh):
        kmd__yjn += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    kmd__yjn += '  return\n'
    zqaia__xfqa = {}
    exec(kmd__yjn, {'setna': setna}, zqaia__xfqa)
    impl = zqaia__xfqa['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        itqh__isv = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(itqh__isv.start, itqh__isv.stop, itqh__isv.step):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        zjc__jvlj = 'n'
        lrmzp__yhay = 'n_pes'
        bjzb__mqzya = 'min_op'
    else:
        zjc__jvlj = 'n-1, -1, -1'
        lrmzp__yhay = '-1'
        bjzb__mqzya = 'max_op'
    kmd__yjn = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {lrmzp__yhay}
    for i in range({zjc__jvlj}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {bjzb__mqzya}))
        if possible_valid_rank != {lrmzp__yhay}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    zqaia__xfqa = {}
    exec(kmd__yjn, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op': max_op,
        'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.box_if_dt64},
        zqaia__xfqa)
    impl = zqaia__xfqa['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    ltmtv__eru = array_to_info(arr)
    _median_series_computation(res, ltmtv__eru, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(ltmtv__eru)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    ltmtv__eru = array_to_info(arr)
    _autocorr_series_computation(res, ltmtv__eru, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(ltmtv__eru)


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
    ltmtv__eru = array_to_info(arr)
    _compute_series_monotonicity(res, ltmtv__eru, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(ltmtv__eru)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    akfg__bkf = res[0] > 0.5
    return akfg__bkf


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        nnr__anqsp = '-'
        yjq__acy = 'index_arr[0] > threshhold_date'
        zjc__jvlj = '1, n+1'
        ztnp__gnr = 'index_arr[-i] <= threshhold_date'
        xkmd__xgqv = 'i - 1'
    else:
        nnr__anqsp = '+'
        yjq__acy = 'index_arr[-1] < threshhold_date'
        zjc__jvlj = 'n'
        ztnp__gnr = 'index_arr[i] >= threshhold_date'
        xkmd__xgqv = 'i'
    kmd__yjn = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        kmd__yjn += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        kmd__yjn += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            kmd__yjn += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            kmd__yjn += (
                '      threshhold_date = initial_date - date_offset.base + date_offset\n'
                )
            kmd__yjn += '    else:\n'
            kmd__yjn += '      threshhold_date = initial_date + date_offset\n'
        else:
            kmd__yjn += (
                f'    threshhold_date = initial_date {nnr__anqsp} date_offset\n'
                )
    else:
        kmd__yjn += f'  threshhold_date = initial_date {nnr__anqsp} offset\n'
    kmd__yjn += '  local_valid = 0\n'
    kmd__yjn += f'  n = len(index_arr)\n'
    kmd__yjn += f'  if n:\n'
    kmd__yjn += f'    if {yjq__acy}:\n'
    kmd__yjn += '      loc_valid = n\n'
    kmd__yjn += '    else:\n'
    kmd__yjn += f'      for i in range({zjc__jvlj}):\n'
    kmd__yjn += f'        if {ztnp__gnr}:\n'
    kmd__yjn += f'          loc_valid = {xkmd__xgqv}\n'
    kmd__yjn += '          break\n'
    kmd__yjn += '  if is_parallel:\n'
    kmd__yjn += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    kmd__yjn += '    return total_valid\n'
    kmd__yjn += '  else:\n'
    kmd__yjn += '    return loc_valid\n'
    zqaia__xfqa = {}
    exec(kmd__yjn, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, zqaia__xfqa)
    return zqaia__xfqa['impl']


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
    kdzj__dyb = numba_to_c_type(sig.args[0].dtype)
    bzkgf__omoc = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), kdzj__dyb))
    smv__qipyr = args[0]
    uwv__dlh = sig.args[0]
    if isinstance(uwv__dlh, (IntegerArrayType, BooleanArrayType)):
        smv__qipyr = cgutils.create_struct_proxy(uwv__dlh)(context, builder,
            smv__qipyr).data
        uwv__dlh = types.Array(uwv__dlh.dtype, 1, 'C')
    assert uwv__dlh.ndim == 1
    arr = make_array(uwv__dlh)(context, builder, smv__qipyr)
    zccuz__vnugj = builder.extract_value(arr.shape, 0)
    bmhv__hlrh = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        zccuz__vnugj, args[1], builder.load(bzkgf__omoc)]
    tmkx__sar = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    wwbaq__but = lir.FunctionType(lir.DoubleType(), tmkx__sar)
    cirii__ecj = cgutils.get_or_insert_function(builder.module, wwbaq__but,
        name='quantile_sequential')
    zkep__zdz = builder.call(cirii__ecj, bmhv__hlrh)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return zkep__zdz


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    kdzj__dyb = numba_to_c_type(sig.args[0].dtype)
    bzkgf__omoc = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), kdzj__dyb))
    smv__qipyr = args[0]
    uwv__dlh = sig.args[0]
    if isinstance(uwv__dlh, (IntegerArrayType, BooleanArrayType)):
        smv__qipyr = cgutils.create_struct_proxy(uwv__dlh)(context, builder,
            smv__qipyr).data
        uwv__dlh = types.Array(uwv__dlh.dtype, 1, 'C')
    assert uwv__dlh.ndim == 1
    arr = make_array(uwv__dlh)(context, builder, smv__qipyr)
    zccuz__vnugj = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        gzvtc__icf = args[2]
    else:
        gzvtc__icf = zccuz__vnugj
    bmhv__hlrh = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        zccuz__vnugj, gzvtc__icf, args[1], builder.load(bzkgf__omoc)]
    tmkx__sar = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType(
        64), lir.DoubleType(), lir.IntType(32)]
    wwbaq__but = lir.FunctionType(lir.DoubleType(), tmkx__sar)
    cirii__ecj = cgutils.get_or_insert_function(builder.module, wwbaq__but,
        name='quantile_parallel')
    zkep__zdz = builder.call(cirii__ecj, bmhv__hlrh)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return zkep__zdz


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
    kmd__yjn = (
        "def impl(arr, method='average', na_option='keep', ascending=True, pct=False):\n"
        )
    kmd__yjn += '  na_idxs = pd.isna(arr)\n'
    kmd__yjn += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    kmd__yjn += '  nas = sum(na_idxs)\n'
    if not ascending:
        kmd__yjn += '  if nas and nas < (sorter.size - 1):\n'
        kmd__yjn += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        kmd__yjn += '  else:\n'
        kmd__yjn += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        kmd__yjn += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    kmd__yjn += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    kmd__yjn += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        kmd__yjn += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        kmd__yjn += '    inv,\n'
        kmd__yjn += '    new_dtype=np.float64,\n'
        kmd__yjn += '    copy=True,\n'
        kmd__yjn += '    nan_to_str=False,\n'
        kmd__yjn += '    from_series=True,\n'
        kmd__yjn += '    ) + 1\n'
    else:
        kmd__yjn += '  arr = arr[sorter]\n'
        kmd__yjn += '  sorted_nas = np.nonzero(pd.isna(arr))[0]\n'
        kmd__yjn += '  eq_arr_na = arr[1:] != arr[:-1]\n'
        kmd__yjn += '  eq_arr_na[pd.isna(eq_arr_na)] = False\n'
        kmd__yjn += '  eq_arr = eq_arr_na.astype(np.bool_)\n'
        kmd__yjn += '  obs = np.concatenate((np.array([True]), eq_arr))\n'
        kmd__yjn += '  if sorted_nas.size:\n'
        kmd__yjn += '    first_na, rep_nas = sorted_nas[0], sorted_nas[1:]\n'
        kmd__yjn += '    obs[first_na] = True\n'
        kmd__yjn += '    obs[rep_nas] = False\n'
        kmd__yjn += '    if rep_nas.size and (rep_nas[-1] + 1) < obs.size:\n'
        kmd__yjn += '      obs[rep_nas[-1] + 1] = True\n'
        kmd__yjn += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            kmd__yjn += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            kmd__yjn += '    dense,\n'
            kmd__yjn += '    new_dtype=np.float64,\n'
            kmd__yjn += '    copy=True,\n'
            kmd__yjn += '    nan_to_str=False,\n'
            kmd__yjn += '    from_series=True,\n'
            kmd__yjn += '  )\n'
        else:
            kmd__yjn += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            kmd__yjn += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                kmd__yjn += '  ret = count_float[dense]\n'
            elif method == 'min':
                kmd__yjn += '  ret = count_float[dense - 1] + 1\n'
            else:
                kmd__yjn += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                kmd__yjn += '  ret[na_idxs] = -1\n'
            kmd__yjn += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            kmd__yjn += '  div_val = arr.size - nas\n'
        else:
            kmd__yjn += '  div_val = arr.size\n'
        kmd__yjn += '  for i in range(len(ret)):\n'
        kmd__yjn += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        kmd__yjn += '  ret[na_idxs] = np.nan\n'
    kmd__yjn += '  return ret\n'
    zqaia__xfqa = {}
    exec(kmd__yjn, {'np': np, 'pd': pd, 'bodo': bodo}, zqaia__xfqa)
    return zqaia__xfqa['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    uen__rmqd = start
    jfaw__ipwqj = 2 * start + 1
    weh__xkib = 2 * start + 2
    if jfaw__ipwqj < n and not cmp_f(arr[jfaw__ipwqj], arr[uen__rmqd]):
        uen__rmqd = jfaw__ipwqj
    if weh__xkib < n and not cmp_f(arr[weh__xkib], arr[uen__rmqd]):
        uen__rmqd = weh__xkib
    if uen__rmqd != start:
        arr[start], arr[uen__rmqd] = arr[uen__rmqd], arr[start]
        ind_arr[start], ind_arr[uen__rmqd] = ind_arr[uen__rmqd], ind_arr[start]
        min_heapify(arr, ind_arr, n, uen__rmqd, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        aqzoj__qmhj = np.empty(k, A.dtype)
        gjdn__npi = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                aqzoj__qmhj[ind] = A[i]
                gjdn__npi[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            aqzoj__qmhj = aqzoj__qmhj[:ind]
            gjdn__npi = gjdn__npi[:ind]
        return aqzoj__qmhj, gjdn__npi, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        saa__gqqu = np.sort(A)
        uzwrb__aoxv = index_arr[np.argsort(A)]
        eyhgf__wnea = pd.Series(saa__gqqu).notna().values
        saa__gqqu = saa__gqqu[eyhgf__wnea]
        uzwrb__aoxv = uzwrb__aoxv[eyhgf__wnea]
        if is_largest:
            saa__gqqu = saa__gqqu[::-1]
            uzwrb__aoxv = uzwrb__aoxv[::-1]
        return np.ascontiguousarray(saa__gqqu), np.ascontiguousarray(
            uzwrb__aoxv)
    aqzoj__qmhj, gjdn__npi, start = select_k_nonan(A, index_arr, m, k)
    gjdn__npi = gjdn__npi[aqzoj__qmhj.argsort()]
    aqzoj__qmhj.sort()
    if not is_largest:
        aqzoj__qmhj = np.ascontiguousarray(aqzoj__qmhj[::-1])
        gjdn__npi = np.ascontiguousarray(gjdn__npi[::-1])
    for i in range(start, m):
        if cmp_f(A[i], aqzoj__qmhj[0]):
            aqzoj__qmhj[0] = A[i]
            gjdn__npi[0] = index_arr[i]
            min_heapify(aqzoj__qmhj, gjdn__npi, k, 0, cmp_f)
    gjdn__npi = gjdn__npi[aqzoj__qmhj.argsort()]
    aqzoj__qmhj.sort()
    if is_largest:
        aqzoj__qmhj = aqzoj__qmhj[::-1]
        gjdn__npi = gjdn__npi[::-1]
    return np.ascontiguousarray(aqzoj__qmhj), np.ascontiguousarray(gjdn__npi)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    rtpy__rdzdh = bodo.libs.distributed_api.get_rank()
    clco__xaqfe, dnmwn__swhw = nlargest(A, I, k, is_largest, cmp_f)
    plic__lbsba = bodo.libs.distributed_api.gatherv(clco__xaqfe)
    bek__ewdc = bodo.libs.distributed_api.gatherv(dnmwn__swhw)
    if rtpy__rdzdh == MPI_ROOT:
        res, uotyb__humwj = nlargest(plic__lbsba, bek__ewdc, k, is_largest,
            cmp_f)
    else:
        res = np.empty(k, A.dtype)
        uotyb__humwj = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(uotyb__humwj)
    return res, uotyb__humwj


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    ztnid__nwxv, pedv__lneyn = mat.shape
    kocew__ceft = np.empty((pedv__lneyn, pedv__lneyn), dtype=np.float64)
    for etu__ascz in range(pedv__lneyn):
        for gilqq__zwpa in range(etu__ascz + 1):
            nrksa__xljtq = 0
            ymm__mrrdz = seros__mplh = unrmw__oam = egt__jdqj = 0.0
            for i in range(ztnid__nwxv):
                if np.isfinite(mat[i, etu__ascz]) and np.isfinite(mat[i,
                    gilqq__zwpa]):
                    pkmzx__sse = mat[i, etu__ascz]
                    crju__pejv = mat[i, gilqq__zwpa]
                    nrksa__xljtq += 1
                    unrmw__oam += pkmzx__sse
                    egt__jdqj += crju__pejv
            if parallel:
                nrksa__xljtq = bodo.libs.distributed_api.dist_reduce(
                    nrksa__xljtq, sum_op)
                unrmw__oam = bodo.libs.distributed_api.dist_reduce(unrmw__oam,
                    sum_op)
                egt__jdqj = bodo.libs.distributed_api.dist_reduce(egt__jdqj,
                    sum_op)
            if nrksa__xljtq < minpv:
                kocew__ceft[etu__ascz, gilqq__zwpa] = kocew__ceft[
                    gilqq__zwpa, etu__ascz] = np.nan
            else:
                gge__ivg = unrmw__oam / nrksa__xljtq
                ttk__kufzl = egt__jdqj / nrksa__xljtq
                unrmw__oam = 0.0
                for i in range(ztnid__nwxv):
                    if np.isfinite(mat[i, etu__ascz]) and np.isfinite(mat[i,
                        gilqq__zwpa]):
                        pkmzx__sse = mat[i, etu__ascz] - gge__ivg
                        crju__pejv = mat[i, gilqq__zwpa] - ttk__kufzl
                        unrmw__oam += pkmzx__sse * crju__pejv
                        ymm__mrrdz += pkmzx__sse * pkmzx__sse
                        seros__mplh += crju__pejv * crju__pejv
                if parallel:
                    unrmw__oam = bodo.libs.distributed_api.dist_reduce(
                        unrmw__oam, sum_op)
                    ymm__mrrdz = bodo.libs.distributed_api.dist_reduce(
                        ymm__mrrdz, sum_op)
                    seros__mplh = bodo.libs.distributed_api.dist_reduce(
                        seros__mplh, sum_op)
                ysw__uwi = nrksa__xljtq - 1.0 if cov else sqrt(ymm__mrrdz *
                    seros__mplh)
                if ysw__uwi != 0.0:
                    kocew__ceft[etu__ascz, gilqq__zwpa] = kocew__ceft[
                        gilqq__zwpa, etu__ascz] = unrmw__oam / ysw__uwi
                else:
                    kocew__ceft[etu__ascz, gilqq__zwpa] = kocew__ceft[
                        gilqq__zwpa, etu__ascz] = np.nan
    return kocew__ceft


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    sth__yrxl = n != 1
    kmd__yjn = 'def impl(data, parallel=False):\n'
    kmd__yjn += '  if parallel:\n'
    atdin__sfhk = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    kmd__yjn += f'    cpp_table = arr_info_list_to_table([{atdin__sfhk}])\n'
    kmd__yjn += (
        f'    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)\n'
        )
    xde__qrlqz = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    kmd__yjn += f'    data = ({xde__qrlqz},)\n'
    kmd__yjn += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    kmd__yjn += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    kmd__yjn += '    bodo.libs.array.delete_table(cpp_table)\n'
    kmd__yjn += '  n = len(data[0])\n'
    kmd__yjn += '  out = np.empty(n, np.bool_)\n'
    kmd__yjn += '  uniqs = dict()\n'
    if sth__yrxl:
        kmd__yjn += '  for i in range(n):\n'
        ilj__prj = ', '.join(f'data[{i}][i]' for i in range(n))
        jnpsx__bfc = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        kmd__yjn += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({ilj__prj},), ({jnpsx__bfc},))
"""
        kmd__yjn += '    if val in uniqs:\n'
        kmd__yjn += '      out[i] = True\n'
        kmd__yjn += '    else:\n'
        kmd__yjn += '      out[i] = False\n'
        kmd__yjn += '      uniqs[val] = 0\n'
    else:
        kmd__yjn += '  data = data[0]\n'
        kmd__yjn += '  hasna = False\n'
        kmd__yjn += '  for i in range(n):\n'
        kmd__yjn += '    if bodo.libs.array_kernels.isna(data, i):\n'
        kmd__yjn += '      out[i] = hasna\n'
        kmd__yjn += '      hasna = True\n'
        kmd__yjn += '    else:\n'
        kmd__yjn += '      val = data[i]\n'
        kmd__yjn += '      if val in uniqs:\n'
        kmd__yjn += '        out[i] = True\n'
        kmd__yjn += '      else:\n'
        kmd__yjn += '        out[i] = False\n'
        kmd__yjn += '        uniqs[val] = 0\n'
    kmd__yjn += '  if parallel:\n'
    kmd__yjn += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    kmd__yjn += '  return out\n'
    zqaia__xfqa = {}
    exec(kmd__yjn, {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table}, zqaia__xfqa)
    impl = zqaia__xfqa['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    hkqk__bzxh = len(data)
    kmd__yjn = 'def impl(data, ind_arr, n, frac, replace, parallel=False):\n'
    kmd__yjn += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        hkqk__bzxh)))
    kmd__yjn += '  table_total = arr_info_list_to_table(info_list_total)\n'
    kmd__yjn += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(hkqk__bzxh))
    for rvhj__rqauk in range(hkqk__bzxh):
        kmd__yjn += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(rvhj__rqauk, rvhj__rqauk, rvhj__rqauk))
    kmd__yjn += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(hkqk__bzxh))
    kmd__yjn += '  delete_table(out_table)\n'
    kmd__yjn += '  delete_table(table_total)\n'
    kmd__yjn += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(hkqk__bzxh)))
    zqaia__xfqa = {}
    exec(kmd__yjn, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'sample_table': sample_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'info_from_table': info_from_table,
        'info_to_array': info_to_array, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, zqaia__xfqa)
    impl = zqaia__xfqa['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    hkqk__bzxh = len(data)
    kmd__yjn = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    kmd__yjn += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        hkqk__bzxh)))
    kmd__yjn += '  table_total = arr_info_list_to_table(info_list_total)\n'
    kmd__yjn += '  keep_i = 0\n'
    kmd__yjn += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for rvhj__rqauk in range(hkqk__bzxh):
        kmd__yjn += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(rvhj__rqauk, rvhj__rqauk, rvhj__rqauk))
    kmd__yjn += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(hkqk__bzxh))
    kmd__yjn += '  delete_table(out_table)\n'
    kmd__yjn += '  delete_table(table_total)\n'
    kmd__yjn += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(hkqk__bzxh)))
    zqaia__xfqa = {}
    exec(kmd__yjn, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, zqaia__xfqa)
    impl = zqaia__xfqa['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        tdmr__apcw = [array_to_info(data_arr)]
        edamh__upc = arr_info_list_to_table(tdmr__apcw)
        owsk__xefrh = 0
        minue__eoldi = drop_duplicates_table(edamh__upc, parallel, 1,
            owsk__xefrh, False, True)
        qutr__rnbj = info_to_array(info_from_table(minue__eoldi, 0), data_arr)
        delete_table(minue__eoldi)
        delete_table(edamh__upc)
        return qutr__rnbj
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    ltt__agsf = len(data.types)
    rgsw__miy = [('out' + str(i)) for i in range(ltt__agsf)]
    vuexq__dxepa = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    rptz__tylvd = ['isna(data[{}], i)'.format(i) for i in vuexq__dxepa]
    wdpkx__aec = 'not ({})'.format(' or '.join(rptz__tylvd))
    if not is_overload_none(thresh):
        wdpkx__aec = '(({}) <= ({}) - thresh)'.format(' + '.join(
            rptz__tylvd), ltt__agsf - 1)
    elif how == 'all':
        wdpkx__aec = 'not ({})'.format(' and '.join(rptz__tylvd))
    kmd__yjn = 'def _dropna_imp(data, how, thresh, subset):\n'
    kmd__yjn += '  old_len = len(data[0])\n'
    kmd__yjn += '  new_len = 0\n'
    kmd__yjn += '  for i in range(old_len):\n'
    kmd__yjn += '    if {}:\n'.format(wdpkx__aec)
    kmd__yjn += '      new_len += 1\n'
    for i, out in enumerate(rgsw__miy):
        if isinstance(data[i], bodo.CategoricalArrayType):
            kmd__yjn += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            kmd__yjn += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    kmd__yjn += '  curr_ind = 0\n'
    kmd__yjn += '  for i in range(old_len):\n'
    kmd__yjn += '    if {}:\n'.format(wdpkx__aec)
    for i in range(ltt__agsf):
        kmd__yjn += '      if isna(data[{}], i):\n'.format(i)
        kmd__yjn += '        setna({}, curr_ind)\n'.format(rgsw__miy[i])
        kmd__yjn += '      else:\n'
        kmd__yjn += '        {}[curr_ind] = data[{}][i]\n'.format(rgsw__miy
            [i], i)
    kmd__yjn += '      curr_ind += 1\n'
    kmd__yjn += '  return {}\n'.format(', '.join(rgsw__miy))
    zqaia__xfqa = {}
    zrzgb__pqi = {'t{}'.format(i): ikv__trisu for i, ikv__trisu in
        enumerate(data.types)}
    zrzgb__pqi.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(kmd__yjn, zrzgb__pqi, zqaia__xfqa)
    rlc__nwmdo = zqaia__xfqa['_dropna_imp']
    return rlc__nwmdo


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        uwv__dlh = arr.dtype
        ngj__zhcu = uwv__dlh.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            gevnj__jxel = init_nested_counts(ngj__zhcu)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                gevnj__jxel = add_nested_counts(gevnj__jxel, val[ind])
            qutr__rnbj = bodo.utils.utils.alloc_type(n, uwv__dlh, gevnj__jxel)
            for rdukt__iso in range(n):
                if bodo.libs.array_kernels.isna(arr, rdukt__iso):
                    setna(qutr__rnbj, rdukt__iso)
                    continue
                val = arr[rdukt__iso]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(qutr__rnbj, rdukt__iso)
                    continue
                qutr__rnbj[rdukt__iso] = val[ind]
            return qutr__rnbj
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    arg__etmvc = _to_readonly(arr_types.types[0])
    return all(isinstance(ikv__trisu, CategoricalArrayType) and 
        _to_readonly(ikv__trisu) == arg__etmvc for ikv__trisu in arr_types.
        types)


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
        wvllz__xqcxi = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            bbn__mps = 0
            ioezo__clq = []
            for A in arr_list:
                gxvy__zdcc = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                ioezo__clq.append(bodo.libs.array_item_arr_ext.get_data(A))
                bbn__mps += gxvy__zdcc
            nood__enk = np.empty(bbn__mps + 1, offset_type)
            mnwmo__efipv = bodo.libs.array_kernels.concat(ioezo__clq)
            ubld__ijkpu = np.empty(bbn__mps + 7 >> 3, np.uint8)
            honqo__vfm = 0
            ftoyf__dwv = 0
            for A in arr_list:
                fqudv__zxa = bodo.libs.array_item_arr_ext.get_offsets(A)
                yrm__ywuk = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                gxvy__zdcc = len(A)
                aqscu__yfanp = fqudv__zxa[gxvy__zdcc]
                for i in range(gxvy__zdcc):
                    nood__enk[i + honqo__vfm] = fqudv__zxa[i] + ftoyf__dwv
                    mne__vnqqp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        yrm__ywuk, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ubld__ijkpu, i +
                        honqo__vfm, mne__vnqqp)
                honqo__vfm += gxvy__zdcc
                ftoyf__dwv += aqscu__yfanp
            nood__enk[honqo__vfm] = ftoyf__dwv
            qutr__rnbj = bodo.libs.array_item_arr_ext.init_array_item_array(
                bbn__mps, mnwmo__efipv, nood__enk, ubld__ijkpu)
            return qutr__rnbj
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        kqjnt__lyyab = arr_list.dtype.names
        kmd__yjn = 'def struct_array_concat_impl(arr_list):\n'
        kmd__yjn += f'    n_all = 0\n'
        for i in range(len(kqjnt__lyyab)):
            kmd__yjn += f'    concat_list{i} = []\n'
        kmd__yjn += '    for A in arr_list:\n'
        kmd__yjn += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(kqjnt__lyyab)):
            kmd__yjn += f'        concat_list{i}.append(data_tuple[{i}])\n'
        kmd__yjn += '        n_all += len(A)\n'
        kmd__yjn += '    n_bytes = (n_all + 7) >> 3\n'
        kmd__yjn += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        kmd__yjn += '    curr_bit = 0\n'
        kmd__yjn += '    for A in arr_list:\n'
        kmd__yjn += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        kmd__yjn += '        for j in range(len(A)):\n'
        kmd__yjn += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        kmd__yjn += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        kmd__yjn += '            curr_bit += 1\n'
        kmd__yjn += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        rjfn__mxran = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(kqjnt__lyyab))])
        kmd__yjn += f'        ({rjfn__mxran},),\n'
        kmd__yjn += '        new_mask,\n'
        kmd__yjn += f'        {kqjnt__lyyab},\n'
        kmd__yjn += '    )\n'
        zqaia__xfqa = {}
        exec(kmd__yjn, {'bodo': bodo, 'np': np}, zqaia__xfqa)
        return zqaia__xfqa['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            fpzbq__vggl = 0
            for A in arr_list:
                fpzbq__vggl += len(A)
            ckwfw__mmau = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(fpzbq__vggl))
            hcnr__hrjyo = 0
            for A in arr_list:
                for i in range(len(A)):
                    ckwfw__mmau._data[i + hcnr__hrjyo] = A._data[i]
                    mne__vnqqp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ckwfw__mmau.
                        _null_bitmap, i + hcnr__hrjyo, mne__vnqqp)
                hcnr__hrjyo += len(A)
            return ckwfw__mmau
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            fpzbq__vggl = 0
            for A in arr_list:
                fpzbq__vggl += len(A)
            ckwfw__mmau = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(fpzbq__vggl))
            hcnr__hrjyo = 0
            for A in arr_list:
                for i in range(len(A)):
                    ckwfw__mmau._days_data[i + hcnr__hrjyo] = A._days_data[i]
                    ckwfw__mmau._seconds_data[i + hcnr__hrjyo
                        ] = A._seconds_data[i]
                    ckwfw__mmau._microseconds_data[i + hcnr__hrjyo
                        ] = A._microseconds_data[i]
                    mne__vnqqp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ckwfw__mmau.
                        _null_bitmap, i + hcnr__hrjyo, mne__vnqqp)
                hcnr__hrjyo += len(A)
            return ckwfw__mmau
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        ebf__tcf = arr_list.dtype.precision
        xdewi__mxop = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            fpzbq__vggl = 0
            for A in arr_list:
                fpzbq__vggl += len(A)
            ckwfw__mmau = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                fpzbq__vggl, ebf__tcf, xdewi__mxop)
            hcnr__hrjyo = 0
            for A in arr_list:
                for i in range(len(A)):
                    ckwfw__mmau._data[i + hcnr__hrjyo] = A._data[i]
                    mne__vnqqp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ckwfw__mmau.
                        _null_bitmap, i + hcnr__hrjyo, mne__vnqqp)
                hcnr__hrjyo += len(A)
            return ckwfw__mmau
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        ikv__trisu) for ikv__trisu in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            ahwf__ixeko = arr_list.types[0]
        else:
            ahwf__ixeko = arr_list.dtype
        ahwf__ixeko = to_str_arr_if_dict_array(ahwf__ixeko)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            vgu__vyrf = 0
            vadno__akjzc = 0
            for A in arr_list:
                arr = A
                vgu__vyrf += len(arr)
                vadno__akjzc += bodo.libs.str_arr_ext.num_total_chars(arr)
            qutr__rnbj = bodo.utils.utils.alloc_type(vgu__vyrf, ahwf__ixeko,
                (vadno__akjzc,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(qutr__rnbj, -1)
            msce__uau = 0
            mdkgd__ttwbz = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(qutr__rnbj,
                    arr, msce__uau, mdkgd__ttwbz)
                msce__uau += len(arr)
                mdkgd__ttwbz += bodo.libs.str_arr_ext.num_total_chars(arr)
            return qutr__rnbj
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(ikv__trisu.dtype, types.Integer) for
        ikv__trisu in arr_list.types) and any(isinstance(ikv__trisu,
        IntegerArrayType) for ikv__trisu in arr_list.types):

        def impl_int_arr_list(arr_list):
            qnqb__himvh = convert_to_nullable_tup(arr_list)
            fonv__yvrko = []
            pxljm__hwwkm = 0
            for A in qnqb__himvh:
                fonv__yvrko.append(A._data)
                pxljm__hwwkm += len(A)
            mnwmo__efipv = bodo.libs.array_kernels.concat(fonv__yvrko)
            revwo__riyk = pxljm__hwwkm + 7 >> 3
            iivxv__opuvq = np.empty(revwo__riyk, np.uint8)
            koti__lybba = 0
            for A in qnqb__himvh:
                ezlu__ffv = A._null_bitmap
                for rdukt__iso in range(len(A)):
                    mne__vnqqp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ezlu__ffv, rdukt__iso)
                    bodo.libs.int_arr_ext.set_bit_to_arr(iivxv__opuvq,
                        koti__lybba, mne__vnqqp)
                    koti__lybba += 1
            return bodo.libs.int_arr_ext.init_integer_array(mnwmo__efipv,
                iivxv__opuvq)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(ikv__trisu.dtype == types.bool_ for ikv__trisu in
        arr_list.types) and any(ikv__trisu == boolean_array for ikv__trisu in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            qnqb__himvh = convert_to_nullable_tup(arr_list)
            fonv__yvrko = []
            pxljm__hwwkm = 0
            for A in qnqb__himvh:
                fonv__yvrko.append(A._data)
                pxljm__hwwkm += len(A)
            mnwmo__efipv = bodo.libs.array_kernels.concat(fonv__yvrko)
            revwo__riyk = pxljm__hwwkm + 7 >> 3
            iivxv__opuvq = np.empty(revwo__riyk, np.uint8)
            koti__lybba = 0
            for A in qnqb__himvh:
                ezlu__ffv = A._null_bitmap
                for rdukt__iso in range(len(A)):
                    mne__vnqqp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ezlu__ffv, rdukt__iso)
                    bodo.libs.int_arr_ext.set_bit_to_arr(iivxv__opuvq,
                        koti__lybba, mne__vnqqp)
                    koti__lybba += 1
            return bodo.libs.bool_arr_ext.init_bool_array(mnwmo__efipv,
                iivxv__opuvq)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            hwouu__epwk = []
            for A in arr_list:
                hwouu__epwk.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                hwouu__epwk), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        ztgbw__fngru = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        kmd__yjn = 'def impl(arr_list):\n'
        kmd__yjn += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({ztgbw__fngru},)), arr_list[0].dtype)
"""
        otrai__tdpbp = {}
        exec(kmd__yjn, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, otrai__tdpbp)
        return otrai__tdpbp['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            pxljm__hwwkm = 0
            for A in arr_list:
                pxljm__hwwkm += len(A)
            qutr__rnbj = np.empty(pxljm__hwwkm, dtype)
            jqww__txx = 0
            for A in arr_list:
                n = len(A)
                qutr__rnbj[jqww__txx:jqww__txx + n] = A
                jqww__txx += n
            return qutr__rnbj
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(ikv__trisu,
        (types.Array, IntegerArrayType)) and isinstance(ikv__trisu.dtype,
        types.Integer) for ikv__trisu in arr_list.types) and any(isinstance
        (ikv__trisu, types.Array) and isinstance(ikv__trisu.dtype, types.
        Float) for ikv__trisu in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            aobmj__sfosb = []
            for A in arr_list:
                aobmj__sfosb.append(A._data)
            gpyux__bvj = bodo.libs.array_kernels.concat(aobmj__sfosb)
            kocew__ceft = bodo.libs.map_arr_ext.init_map_arr(gpyux__bvj)
            return kocew__ceft
        return impl_map_arr_list
    for wmu__iaqkv in arr_list:
        if not isinstance(wmu__iaqkv, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(ikv__trisu.astype(np.float64) for ikv__trisu in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    hkqk__bzxh = len(arr_tup.types)
    kmd__yjn = 'def f(arr_tup):\n'
    kmd__yjn += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(
        hkqk__bzxh)), ',' if hkqk__bzxh == 1 else '')
    zqaia__xfqa = {}
    exec(kmd__yjn, {'np': np}, zqaia__xfqa)
    oeqz__ljry = zqaia__xfqa['f']
    return oeqz__ljry


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    hkqk__bzxh = len(arr_tup.types)
    dav__tckt = find_common_np_dtype(arr_tup.types)
    ngj__zhcu = None
    yxkk__iiu = ''
    if isinstance(dav__tckt, types.Integer):
        ngj__zhcu = bodo.libs.int_arr_ext.IntDtype(dav__tckt)
        yxkk__iiu = '.astype(out_dtype, False)'
    kmd__yjn = 'def f(arr_tup):\n'
    kmd__yjn += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, yxkk__iiu) for i in range(hkqk__bzxh)), ',' if 
        hkqk__bzxh == 1 else '')
    zqaia__xfqa = {}
    exec(kmd__yjn, {'bodo': bodo, 'out_dtype': ngj__zhcu}, zqaia__xfqa)
    paax__uudxw = zqaia__xfqa['f']
    return paax__uudxw


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, afkb__iov = build_set_seen_na(A)
        return len(s) + int(not dropna and afkb__iov)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        cey__vij = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        aii__blwmm = len(cey__vij)
        return bodo.libs.distributed_api.dist_reduce(aii__blwmm, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([ussm__evr for ussm__evr in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        ufec__htec = np.finfo(A.dtype(1).dtype).max
    else:
        ufec__htec = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        qutr__rnbj = np.empty(n, A.dtype)
        bfdc__vws = ufec__htec
        for i in range(n):
            bfdc__vws = min(bfdc__vws, A[i])
            qutr__rnbj[i] = bfdc__vws
        return qutr__rnbj
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        ufec__htec = np.finfo(A.dtype(1).dtype).min
    else:
        ufec__htec = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        qutr__rnbj = np.empty(n, A.dtype)
        bfdc__vws = ufec__htec
        for i in range(n):
            bfdc__vws = max(bfdc__vws, A[i])
            qutr__rnbj[i] = bfdc__vws
        return qutr__rnbj
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        hczep__icf = arr_info_list_to_table([array_to_info(A)])
        agl__gavud = 1
        owsk__xefrh = 0
        minue__eoldi = drop_duplicates_table(hczep__icf, parallel,
            agl__gavud, owsk__xefrh, dropna, True)
        qutr__rnbj = info_to_array(info_from_table(minue__eoldi, 0), A)
        delete_table(hczep__icf)
        delete_table(minue__eoldi)
        return qutr__rnbj
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    wvllz__xqcxi = bodo.utils.typing.to_nullable_type(arr.dtype)
    masi__ivfye = index_arr
    ztz__fvxku = masi__ivfye.dtype

    def impl(arr, index_arr):
        n = len(arr)
        gevnj__jxel = init_nested_counts(wvllz__xqcxi)
        pkelz__bspi = init_nested_counts(ztz__fvxku)
        for i in range(n):
            kqll__xjaq = index_arr[i]
            if isna(arr, i):
                gevnj__jxel = (gevnj__jxel[0] + 1,) + gevnj__jxel[1:]
                pkelz__bspi = add_nested_counts(pkelz__bspi, kqll__xjaq)
                continue
            onez__rfa = arr[i]
            if len(onez__rfa) == 0:
                gevnj__jxel = (gevnj__jxel[0] + 1,) + gevnj__jxel[1:]
                pkelz__bspi = add_nested_counts(pkelz__bspi, kqll__xjaq)
                continue
            gevnj__jxel = add_nested_counts(gevnj__jxel, onez__rfa)
            for vttwa__bbub in range(len(onez__rfa)):
                pkelz__bspi = add_nested_counts(pkelz__bspi, kqll__xjaq)
        qutr__rnbj = bodo.utils.utils.alloc_type(gevnj__jxel[0],
            wvllz__xqcxi, gevnj__jxel[1:])
        qyj__rcb = bodo.utils.utils.alloc_type(gevnj__jxel[0], masi__ivfye,
            pkelz__bspi)
        ftoyf__dwv = 0
        for i in range(n):
            if isna(arr, i):
                setna(qutr__rnbj, ftoyf__dwv)
                qyj__rcb[ftoyf__dwv] = index_arr[i]
                ftoyf__dwv += 1
                continue
            onez__rfa = arr[i]
            aqscu__yfanp = len(onez__rfa)
            if aqscu__yfanp == 0:
                setna(qutr__rnbj, ftoyf__dwv)
                qyj__rcb[ftoyf__dwv] = index_arr[i]
                ftoyf__dwv += 1
                continue
            qutr__rnbj[ftoyf__dwv:ftoyf__dwv + aqscu__yfanp] = onez__rfa
            qyj__rcb[ftoyf__dwv:ftoyf__dwv + aqscu__yfanp] = index_arr[i]
            ftoyf__dwv += aqscu__yfanp
        return qutr__rnbj, qyj__rcb
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    wvllz__xqcxi = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        gevnj__jxel = init_nested_counts(wvllz__xqcxi)
        for i in range(n):
            if isna(arr, i):
                gevnj__jxel = (gevnj__jxel[0] + 1,) + gevnj__jxel[1:]
                btyrm__fkkgf = 1
            else:
                onez__rfa = arr[i]
                tfhy__xmsn = len(onez__rfa)
                if tfhy__xmsn == 0:
                    gevnj__jxel = (gevnj__jxel[0] + 1,) + gevnj__jxel[1:]
                    btyrm__fkkgf = 1
                    continue
                else:
                    gevnj__jxel = add_nested_counts(gevnj__jxel, onez__rfa)
                    btyrm__fkkgf = tfhy__xmsn
            if counts[i] != btyrm__fkkgf:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        qutr__rnbj = bodo.utils.utils.alloc_type(gevnj__jxel[0],
            wvllz__xqcxi, gevnj__jxel[1:])
        ftoyf__dwv = 0
        for i in range(n):
            if isna(arr, i):
                setna(qutr__rnbj, ftoyf__dwv)
                ftoyf__dwv += 1
                continue
            onez__rfa = arr[i]
            aqscu__yfanp = len(onez__rfa)
            if aqscu__yfanp == 0:
                setna(qutr__rnbj, ftoyf__dwv)
                ftoyf__dwv += 1
                continue
            qutr__rnbj[ftoyf__dwv:ftoyf__dwv + aqscu__yfanp] = onez__rfa
            ftoyf__dwv += aqscu__yfanp
        return qutr__rnbj
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(ogya__hmkrh) for ogya__hmkrh in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        ojwue__iupi = 'np.empty(n, np.int64)'
        yczek__yyhf = 'out_arr[i] = 1'
        smayf__avvjo = 'max(len(arr[i]), 1)'
    else:
        ojwue__iupi = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        yczek__yyhf = 'bodo.libs.array_kernels.setna(out_arr, i)'
        smayf__avvjo = 'len(arr[i])'
    kmd__yjn = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {ojwue__iupi}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {yczek__yyhf}
        else:
            out_arr[i] = {smayf__avvjo}
    return out_arr
    """
    zqaia__xfqa = {}
    exec(kmd__yjn, {'bodo': bodo, 'numba': numba, 'np': np}, zqaia__xfqa)
    impl = zqaia__xfqa['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    masi__ivfye = index_arr
    ztz__fvxku = masi__ivfye.dtype

    def impl(arr, pat, n, index_arr):
        qcf__muyr = pat is not None and len(pat) > 1
        if qcf__muyr:
            qvhde__oxer = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        dnkaf__xqmzo = len(arr)
        vgu__vyrf = 0
        vadno__akjzc = 0
        pkelz__bspi = init_nested_counts(ztz__fvxku)
        for i in range(dnkaf__xqmzo):
            kqll__xjaq = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                vgu__vyrf += 1
                pkelz__bspi = add_nested_counts(pkelz__bspi, kqll__xjaq)
                continue
            if qcf__muyr:
                lut__wkvy = qvhde__oxer.split(arr[i], maxsplit=n)
            else:
                lut__wkvy = arr[i].split(pat, n)
            vgu__vyrf += len(lut__wkvy)
            for s in lut__wkvy:
                pkelz__bspi = add_nested_counts(pkelz__bspi, kqll__xjaq)
                vadno__akjzc += bodo.libs.str_arr_ext.get_utf8_size(s)
        qutr__rnbj = bodo.libs.str_arr_ext.pre_alloc_string_array(vgu__vyrf,
            vadno__akjzc)
        qyj__rcb = bodo.utils.utils.alloc_type(vgu__vyrf, masi__ivfye,
            pkelz__bspi)
        xsyj__vrz = 0
        for rdukt__iso in range(dnkaf__xqmzo):
            if isna(arr, rdukt__iso):
                qutr__rnbj[xsyj__vrz] = ''
                bodo.libs.array_kernels.setna(qutr__rnbj, xsyj__vrz)
                qyj__rcb[xsyj__vrz] = index_arr[rdukt__iso]
                xsyj__vrz += 1
                continue
            if qcf__muyr:
                lut__wkvy = qvhde__oxer.split(arr[rdukt__iso], maxsplit=n)
            else:
                lut__wkvy = arr[rdukt__iso].split(pat, n)
            zvrp__igt = len(lut__wkvy)
            qutr__rnbj[xsyj__vrz:xsyj__vrz + zvrp__igt] = lut__wkvy
            qyj__rcb[xsyj__vrz:xsyj__vrz + zvrp__igt] = index_arr[rdukt__iso]
            xsyj__vrz += zvrp__igt
        return qutr__rnbj, qyj__rcb
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
            qutr__rnbj = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                qutr__rnbj[i] = np.nan
            return qutr__rnbj
        return impl_float
    mfg__qtyad = to_str_arr_if_dict_array(arr)

    def impl(n, arr):
        numba.parfors.parfor.init_prange()
        qutr__rnbj = bodo.utils.utils.alloc_type(n, mfg__qtyad, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(qutr__rnbj, i)
        return qutr__rnbj
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
    dlstm__kcvn = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            qutr__rnbj = bodo.utils.utils.alloc_type(new_len, dlstm__kcvn)
            bodo.libs.str_arr_ext.str_copy_ptr(qutr__rnbj.ctypes, 0, A.
                ctypes, old_size)
            return qutr__rnbj
        return impl_char

    def impl(A, old_size, new_len):
        qutr__rnbj = bodo.utils.utils.alloc_type(new_len, dlstm__kcvn, (-1,))
        qutr__rnbj[:old_size] = A[:old_size]
        return qutr__rnbj
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    uzi__qkpdw = math.ceil((stop - start) / step)
    return int(max(uzi__qkpdw, 0))


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
    if any(isinstance(ussm__evr, types.Complex) for ussm__evr in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            lkss__cggjb = (stop - start) / step
            uzi__qkpdw = math.ceil(lkss__cggjb.real)
            ltfj__ibhy = math.ceil(lkss__cggjb.imag)
            bdk__foka = int(max(min(ltfj__ibhy, uzi__qkpdw), 0))
            arr = np.empty(bdk__foka, dtype)
            for i in numba.parfors.parfor.internal_prange(bdk__foka):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            bdk__foka = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(bdk__foka, dtype)
            for i in numba.parfors.parfor.internal_prange(bdk__foka):
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
        cuao__ezmx = arr,
        if not inplace:
            cuao__ezmx = arr.copy(),
        xmoid__tru = bodo.libs.str_arr_ext.to_list_if_immutable_arr(cuao__ezmx)
        agarp__ouqjy = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data,
            True)
        bodo.libs.timsort.sort(xmoid__tru, 0, n, agarp__ouqjy)
        if not ascending:
            bodo.libs.timsort.reverseRange(xmoid__tru, 0, n, agarp__ouqjy)
        bodo.libs.str_arr_ext.cp_str_list_to_array(cuao__ezmx, xmoid__tru)
        return cuao__ezmx[0]
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
        kocew__ceft = []
        for i in range(n):
            if A[i]:
                kocew__ceft.append(i + offset)
        return np.array(kocew__ceft, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    dlstm__kcvn = element_type(A)
    if dlstm__kcvn == types.unicode_type:
        null_value = '""'
    elif dlstm__kcvn == types.bool_:
        null_value = 'False'
    elif dlstm__kcvn == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif dlstm__kcvn == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    xsyj__vrz = 'i'
    yolzk__lex = False
    pvvt__iajs = get_overload_const_str(method)
    if pvvt__iajs in ('ffill', 'pad'):
        rsvpm__doi = 'n'
        send_right = True
    elif pvvt__iajs in ('backfill', 'bfill'):
        rsvpm__doi = 'n-1, -1, -1'
        send_right = False
        if dlstm__kcvn == types.unicode_type:
            xsyj__vrz = '(n - 1) - i'
            yolzk__lex = True
    kmd__yjn = 'def impl(A, method, parallel=False):\n'
    kmd__yjn += '  A = decode_if_dict_array(A)\n'
    kmd__yjn += '  has_last_value = False\n'
    kmd__yjn += f'  last_value = {null_value}\n'
    kmd__yjn += '  if parallel:\n'
    kmd__yjn += '    rank = bodo.libs.distributed_api.get_rank()\n'
    kmd__yjn += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    kmd__yjn += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    kmd__yjn += '  n = len(A)\n'
    kmd__yjn += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    kmd__yjn += f'  for i in range({rsvpm__doi}):\n'
    kmd__yjn += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    kmd__yjn += f'      bodo.libs.array_kernels.setna(out_arr, {xsyj__vrz})\n'
    kmd__yjn += '      continue\n'
    kmd__yjn += '    s = A[i]\n'
    kmd__yjn += '    if bodo.libs.array_kernels.isna(A, i):\n'
    kmd__yjn += '      s = last_value\n'
    kmd__yjn += f'    out_arr[{xsyj__vrz}] = s\n'
    kmd__yjn += '    last_value = s\n'
    kmd__yjn += '    has_last_value = True\n'
    if yolzk__lex:
        kmd__yjn += '  return out_arr[::-1]\n'
    else:
        kmd__yjn += '  return out_arr\n'
    kif__sgzm = {}
    exec(kmd__yjn, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, kif__sgzm)
    impl = kif__sgzm['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        hhqm__hfww = 0
        cylox__uup = n_pes - 1
        zxem__dqado = np.int32(rank + 1)
        gjmn__fov = np.int32(rank - 1)
        fpij__sdxz = len(in_arr) - 1
        coel__ehb = -1
        mmai__xrie = -1
    else:
        hhqm__hfww = n_pes - 1
        cylox__uup = 0
        zxem__dqado = np.int32(rank - 1)
        gjmn__fov = np.int32(rank + 1)
        fpij__sdxz = 0
        coel__ehb = len(in_arr)
        mmai__xrie = 1
    zhcor__evulr = np.int32(bodo.hiframes.rolling.comm_border_tag)
    aag__bvxf = np.empty(1, dtype=np.bool_)
    ghwi__hgzkw = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    kzak__enr = np.empty(1, dtype=np.bool_)
    yftr__exozw = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    mvfz__ubabw = False
    ulomj__kowd = null_value
    for i in range(fpij__sdxz, coel__ehb, mmai__xrie):
        if not isna(in_arr, i):
            mvfz__ubabw = True
            ulomj__kowd = in_arr[i]
            break
    if rank != hhqm__hfww:
        gryq__heem = bodo.libs.distributed_api.irecv(aag__bvxf, 1,
            gjmn__fov, zhcor__evulr, True)
        bodo.libs.distributed_api.wait(gryq__heem, True)
        vezaf__tfxv = bodo.libs.distributed_api.irecv(ghwi__hgzkw, 1,
            gjmn__fov, zhcor__evulr, True)
        bodo.libs.distributed_api.wait(vezaf__tfxv, True)
        idv__utz = aag__bvxf[0]
        agyv__dzqon = ghwi__hgzkw[0]
    else:
        idv__utz = False
        agyv__dzqon = null_value
    if mvfz__ubabw:
        kzak__enr[0] = mvfz__ubabw
        yftr__exozw[0] = ulomj__kowd
    else:
        kzak__enr[0] = idv__utz
        yftr__exozw[0] = agyv__dzqon
    if rank != cylox__uup:
        rsp__pib = bodo.libs.distributed_api.isend(kzak__enr, 1,
            zxem__dqado, zhcor__evulr, True)
        uxz__xmvo = bodo.libs.distributed_api.isend(yftr__exozw, 1,
            zxem__dqado, zhcor__evulr, True)
    return idv__utz, agyv__dzqon


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    derd__xruw = {'axis': axis, 'kind': kind, 'order': order}
    dixv__dwonx = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', derd__xruw, dixv__dwonx, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    dlstm__kcvn = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            A = decode_if_dict_array(A)
            dnkaf__xqmzo = len(A)
            qutr__rnbj = bodo.utils.utils.alloc_type(dnkaf__xqmzo * repeats,
                dlstm__kcvn, (-1,))
            for i in range(dnkaf__xqmzo):
                xsyj__vrz = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for rdukt__iso in range(repeats):
                        bodo.libs.array_kernels.setna(qutr__rnbj, xsyj__vrz +
                            rdukt__iso)
                else:
                    qutr__rnbj[xsyj__vrz:xsyj__vrz + repeats] = A[i]
            return qutr__rnbj
        return impl_int

    def impl_arr(A, repeats):
        A = decode_if_dict_array(A)
        dnkaf__xqmzo = len(A)
        qutr__rnbj = bodo.utils.utils.alloc_type(repeats.sum(), dlstm__kcvn,
            (-1,))
        xsyj__vrz = 0
        for i in range(dnkaf__xqmzo):
            fjwqb__yhkl = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for rdukt__iso in range(fjwqb__yhkl):
                    bodo.libs.array_kernels.setna(qutr__rnbj, xsyj__vrz +
                        rdukt__iso)
            else:
                qutr__rnbj[xsyj__vrz:xsyj__vrz + fjwqb__yhkl] = A[i]
            xsyj__vrz += fjwqb__yhkl
        return qutr__rnbj
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
        cckt__cakj = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(cckt__cakj, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        oybfk__vrsaz = bodo.libs.array_kernels.concat([A1, A2])
        yergr__jjy = bodo.libs.array_kernels.unique(oybfk__vrsaz)
        return pd.Series(yergr__jjy).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    derd__xruw = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    dixv__dwonx = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', derd__xruw, dixv__dwonx, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        ebumu__rvmy = bodo.libs.array_kernels.unique(A1)
        dlr__mvj = bodo.libs.array_kernels.unique(A2)
        oybfk__vrsaz = bodo.libs.array_kernels.concat([ebumu__rvmy, dlr__mvj])
        oiut__ymn = pd.Series(oybfk__vrsaz).sort_values().values
        return slice_array_intersect1d(oiut__ymn)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    eyhgf__wnea = arr[1:] == arr[:-1]
    return arr[:-1][eyhgf__wnea]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    zhcor__evulr = np.int32(bodo.hiframes.rolling.comm_border_tag)
    juzx__eixdk = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        dlxx__kvsu = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), zhcor__evulr, True)
        bodo.libs.distributed_api.wait(dlxx__kvsu, True)
    if rank == n_pes - 1:
        return None
    else:
        ybmdm__ancn = bodo.libs.distributed_api.irecv(juzx__eixdk, 1, np.
            int32(rank + 1), zhcor__evulr, True)
        bodo.libs.distributed_api.wait(ybmdm__ancn, True)
        return juzx__eixdk[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    eyhgf__wnea = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            eyhgf__wnea[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        zoh__pzsu = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == zoh__pzsu:
            eyhgf__wnea[n - 1] = True
    return eyhgf__wnea


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    derd__xruw = {'assume_unique': assume_unique}
    dixv__dwonx = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', derd__xruw, dixv__dwonx, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        ebumu__rvmy = bodo.libs.array_kernels.unique(A1)
        dlr__mvj = bodo.libs.array_kernels.unique(A2)
        eyhgf__wnea = calculate_mask_setdiff1d(ebumu__rvmy, dlr__mvj)
        return pd.Series(ebumu__rvmy[eyhgf__wnea]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    eyhgf__wnea = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        eyhgf__wnea &= A1 != A2[i]
    return eyhgf__wnea


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    derd__xruw = {'retstep': retstep, 'axis': axis}
    dixv__dwonx = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', derd__xruw, dixv__dwonx, 'numpy')
    dssxy__rto = False
    if is_overload_none(dtype):
        dlstm__kcvn = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            dssxy__rto = True
        dlstm__kcvn = numba.np.numpy_support.as_dtype(dtype).type
    if dssxy__rto:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            qvwp__pzn = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            qutr__rnbj = np.empty(num, dlstm__kcvn)
            for i in numba.parfors.parfor.internal_prange(num):
                qutr__rnbj[i] = dlstm__kcvn(np.floor(start + i * qvwp__pzn))
            return qutr__rnbj
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            qvwp__pzn = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            qutr__rnbj = np.empty(num, dlstm__kcvn)
            for i in numba.parfors.parfor.internal_prange(num):
                qutr__rnbj[i] = dlstm__kcvn(start + i * qvwp__pzn)
            return qutr__rnbj
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
        hkqk__bzxh = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                hkqk__bzxh += A[i] == val
        return hkqk__bzxh > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    derd__xruw = {'axis': axis, 'out': out, 'keepdims': keepdims}
    dixv__dwonx = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', derd__xruw, dixv__dwonx, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        hkqk__bzxh = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                hkqk__bzxh += int(bool(A[i]))
        return hkqk__bzxh > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    derd__xruw = {'axis': axis, 'out': out, 'keepdims': keepdims}
    dixv__dwonx = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', derd__xruw, dixv__dwonx, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        hkqk__bzxh = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                hkqk__bzxh += int(bool(A[i]))
        return hkqk__bzxh == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    derd__xruw = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    dixv__dwonx = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', derd__xruw, dixv__dwonx, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        ogmio__gfng = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            qutr__rnbj = np.empty(n, ogmio__gfng)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(qutr__rnbj, i)
                    continue
                qutr__rnbj[i] = np_cbrt_scalar(A[i], ogmio__gfng)
            return qutr__rnbj
        return impl_arr
    ogmio__gfng = np.promote_types(numba.np.numpy_support.as_dtype(A),
        numba.np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, ogmio__gfng)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    khbv__apm = x < 0
    if khbv__apm:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if khbv__apm:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    max__zxju = isinstance(tup, (types.BaseTuple, types.List))
    nlgoc__gmzof = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for wmu__iaqkv in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                wmu__iaqkv, 'numpy.hstack()')
            max__zxju = max__zxju and bodo.utils.utils.is_array_typ(wmu__iaqkv,
                False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        max__zxju = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif nlgoc__gmzof:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        arq__qxcqm = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for wmu__iaqkv in arq__qxcqm.types:
            nlgoc__gmzof = nlgoc__gmzof and bodo.utils.utils.is_array_typ(
                wmu__iaqkv, False)
    if not (max__zxju or nlgoc__gmzof):
        return
    if nlgoc__gmzof:

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
    derd__xruw = {'check_valid': check_valid, 'tol': tol}
    dixv__dwonx = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', derd__xruw,
        dixv__dwonx, 'numpy')
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
        ztnid__nwxv = mean.shape[0]
        xlat__dvexj = size, ztnid__nwxv
        bvpwt__cvntz = np.random.standard_normal(xlat__dvexj)
        cov = cov.astype(np.float64)
        ftz__idgze, s, nfv__hxjru = np.linalg.svd(cov)
        res = np.dot(bvpwt__cvntz, np.sqrt(s).reshape(ztnid__nwxv, 1) *
            nfv__hxjru)
        rdphh__ilopb = res + mean
        return rdphh__ilopb
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
            lrmzp__yhay = bodo.hiframes.series_kernels._get_type_max_value(arr)
            qusj__ghk = typing.builtins.IndexValue(-1, lrmzp__yhay)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                emo__qqb = typing.builtins.IndexValue(i, arr[i])
                qusj__ghk = min(qusj__ghk, emo__qqb)
            return qusj__ghk.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        qaq__lasn = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            nne__jkij = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            lrmzp__yhay = qaq__lasn(len(arr.dtype.categories) + 1)
            qusj__ghk = typing.builtins.IndexValue(-1, lrmzp__yhay)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                emo__qqb = typing.builtins.IndexValue(i, nne__jkij[i])
                qusj__ghk = min(qusj__ghk, emo__qqb)
            return qusj__ghk.index
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
            lrmzp__yhay = bodo.hiframes.series_kernels._get_type_min_value(arr)
            qusj__ghk = typing.builtins.IndexValue(-1, lrmzp__yhay)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                emo__qqb = typing.builtins.IndexValue(i, arr[i])
                qusj__ghk = max(qusj__ghk, emo__qqb)
            return qusj__ghk.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        qaq__lasn = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            nne__jkij = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            lrmzp__yhay = qaq__lasn(-1)
            qusj__ghk = typing.builtins.IndexValue(-1, lrmzp__yhay)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                emo__qqb = typing.builtins.IndexValue(i, nne__jkij[i])
                qusj__ghk = max(qusj__ghk, emo__qqb)
            return qusj__ghk.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
