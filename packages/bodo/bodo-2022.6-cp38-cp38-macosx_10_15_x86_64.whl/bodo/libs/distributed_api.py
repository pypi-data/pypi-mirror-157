import atexit
import datetime
import sys
import time
import warnings
from collections import defaultdict
from decimal import Decimal
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from mpi4py import MPI
from numba.core import cgutils, ir_utils, types
from numba.core.typing import signature
from numba.core.typing.builtins import IndexValueType
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, overload, register_jitable
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.libs import hdist
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType, set_bit_to_arr
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import convert_len_arr_to_offset, get_bit_bitmap, get_data_ptr, get_null_bitmap_ptr, get_offset_ptr, num_total_chars, pre_alloc_string_array, set_bit_to, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, decode_if_dict_array, is_overload_false, is_overload_none, is_str_arr_type
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, empty_like_type, is_array_typ, numba_to_c_type
ll.add_symbol('dist_get_time', hdist.dist_get_time)
ll.add_symbol('get_time', hdist.get_time)
ll.add_symbol('dist_reduce', hdist.dist_reduce)
ll.add_symbol('dist_arr_reduce', hdist.dist_arr_reduce)
ll.add_symbol('dist_exscan', hdist.dist_exscan)
ll.add_symbol('dist_irecv', hdist.dist_irecv)
ll.add_symbol('dist_isend', hdist.dist_isend)
ll.add_symbol('dist_wait', hdist.dist_wait)
ll.add_symbol('dist_get_item_pointer', hdist.dist_get_item_pointer)
ll.add_symbol('get_dummy_ptr', hdist.get_dummy_ptr)
ll.add_symbol('allgather', hdist.allgather)
ll.add_symbol('oneD_reshape_shuffle', hdist.oneD_reshape_shuffle)
ll.add_symbol('permutation_int', hdist.permutation_int)
ll.add_symbol('permutation_array_index', hdist.permutation_array_index)
ll.add_symbol('c_get_rank', hdist.dist_get_rank)
ll.add_symbol('c_get_size', hdist.dist_get_size)
ll.add_symbol('c_barrier', hdist.barrier)
ll.add_symbol('c_alltoall', hdist.c_alltoall)
ll.add_symbol('c_gather_scalar', hdist.c_gather_scalar)
ll.add_symbol('c_gatherv', hdist.c_gatherv)
ll.add_symbol('c_scatterv', hdist.c_scatterv)
ll.add_symbol('c_allgatherv', hdist.c_allgatherv)
ll.add_symbol('c_bcast', hdist.c_bcast)
ll.add_symbol('c_recv', hdist.dist_recv)
ll.add_symbol('c_send', hdist.dist_send)
mpi_req_numba_type = getattr(types, 'int' + str(8 * hdist.mpi_req_num_bytes))
MPI_ROOT = 0
ANY_SOURCE = np.int32(hdist.ANY_SOURCE)


class Reduce_Type(Enum):
    Sum = 0
    Prod = 1
    Min = 2
    Max = 3
    Argmin = 4
    Argmax = 5
    Or = 6
    Concat = 7
    No_Op = 8


_get_rank = types.ExternalFunction('c_get_rank', types.int32())
_get_size = types.ExternalFunction('c_get_size', types.int32())
_barrier = types.ExternalFunction('c_barrier', types.int32())


@numba.njit
def get_rank():
    return _get_rank()


@numba.njit
def get_size():
    return _get_size()


@numba.njit
def barrier():
    _barrier()


_get_time = types.ExternalFunction('get_time', types.float64())
dist_time = types.ExternalFunction('dist_get_time', types.float64())


@overload(time.time, no_unliteral=True)
def overload_time_time():
    return lambda : _get_time()


@numba.generated_jit(nopython=True)
def get_type_enum(arr):
    arr = arr.instance_type if isinstance(arr, types.TypeRef) else arr
    dtype = arr.dtype
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = bodo.hiframes.pd_categorical_ext.get_categories_int_type(dtype)
    typ_val = numba_to_c_type(dtype)
    return lambda arr: np.int32(typ_val)


INT_MAX = np.iinfo(np.int32).max
_send = types.ExternalFunction('c_send', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def send(val, rank, tag):
    send_arr = np.full(1, val)
    kha__lnoe = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, kha__lnoe, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    kha__lnoe = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, kha__lnoe, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            kha__lnoe = get_type_enum(arr)
            return _isend(arr.ctypes, size, kha__lnoe, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        kha__lnoe = np.int32(numba_to_c_type(arr.dtype))
        ete__ypde = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            bpxdz__dhnl = size + 7 >> 3
            eqde__lgn = _isend(arr._data.ctypes, size, kha__lnoe, pe, tag, cond
                )
            une__rhnv = _isend(arr._null_bitmap.ctypes, bpxdz__dhnl,
                ete__ypde, pe, tag, cond)
            return eqde__lgn, une__rhnv
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        jdnnb__wxo = np.int32(numba_to_c_type(offset_type))
        ete__ypde = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            wtd__trbct = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(wtd__trbct, pe, tag - 1)
            bpxdz__dhnl = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                jdnnb__wxo, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), wtd__trbct,
                ete__ypde, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                bpxdz__dhnl, ete__ypde, pe, tag)
            return None
        return impl_str_arr
    typ_enum = numba_to_c_type(types.uint8)

    def impl_voidptr(arr, size, pe, tag, cond=True):
        return _isend(arr, size, typ_enum, pe, tag, cond)
    return impl_voidptr


_irecv = types.ExternalFunction('dist_irecv', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def irecv(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            kha__lnoe = get_type_enum(arr)
            return _irecv(arr.ctypes, size, kha__lnoe, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        kha__lnoe = np.int32(numba_to_c_type(arr.dtype))
        ete__ypde = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            bpxdz__dhnl = size + 7 >> 3
            eqde__lgn = _irecv(arr._data.ctypes, size, kha__lnoe, pe, tag, cond
                )
            une__rhnv = _irecv(arr._null_bitmap.ctypes, bpxdz__dhnl,
                ete__ypde, pe, tag, cond)
            return eqde__lgn, une__rhnv
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        jdnnb__wxo = np.int32(numba_to_c_type(offset_type))
        ete__ypde = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            chmg__tbwzj = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            chmg__tbwzj = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        ydolg__eqihw = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {chmg__tbwzj}(size, n_chars)
            bodo.libs.str_arr_ext.move_str_binary_arr_payload(arr, new_arr)

            n_bytes = (size + 7) >> 3
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_offset_ptr(arr),
                size + 1,
                offset_typ_enum,
                pe,
                tag,
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_data_ptr(arr), n_chars, char_typ_enum, pe, tag
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                n_bytes,
                char_typ_enum,
                pe,
                tag,
            )
            return None"""
        oxe__xjijn = dict()
        exec(ydolg__eqihw, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            jdnnb__wxo, 'char_typ_enum': ete__ypde}, oxe__xjijn)
        impl = oxe__xjijn['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    kha__lnoe = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), kha__lnoe)


@numba.generated_jit(nopython=True)
def gather_scalar(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    data = types.unliteral(data)
    typ_val = numba_to_c_type(data)
    dtype = data

    def gather_scalar_impl(data, allgather=False, warn_if_rep=True, root=
        MPI_ROOT):
        n_pes = bodo.libs.distributed_api.get_size()
        rank = bodo.libs.distributed_api.get_rank()
        send = np.full(1, data, dtype)
        pdgec__veixe = n_pes if rank == root or allgather else 0
        les__ibqs = np.empty(pdgec__veixe, dtype)
        c_gather_scalar(send.ctypes, les__ibqs.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return les__ibqs
    return gather_scalar_impl


c_gather_scalar = types.ExternalFunction('c_gather_scalar', types.void(
    types.voidptr, types.voidptr, types.int32, types.bool_, types.int32))
c_gatherv = types.ExternalFunction('c_gatherv', types.void(types.voidptr,
    types.int32, types.voidptr, types.voidptr, types.voidptr, types.int32,
    types.bool_, types.int32))
c_scatterv = types.ExternalFunction('c_scatterv', types.void(types.voidptr,
    types.voidptr, types.voidptr, types.voidptr, types.int32, types.int32))


@intrinsic
def value_to_ptr(typingctx, val_tp=None):

    def codegen(context, builder, sig, args):
        nupb__uuyc = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], nupb__uuyc)
        return builder.bitcast(nupb__uuyc, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        nupb__uuyc = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(nupb__uuyc)
    return val_tp(ptr_tp, val_tp), codegen


_dist_reduce = types.ExternalFunction('dist_reduce', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))
_dist_arr_reduce = types.ExternalFunction('dist_arr_reduce', types.void(
    types.voidptr, types.int64, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_reduce(value, reduce_op):
    if isinstance(value, types.Array):
        typ_enum = np.int32(numba_to_c_type(value.dtype))

        def impl_arr(value, reduce_op):
            A = np.ascontiguousarray(value)
            _dist_arr_reduce(A.ctypes, A.size, reduce_op, typ_enum)
            return A
        return impl_arr
    das__sprr = types.unliteral(value)
    if isinstance(das__sprr, IndexValueType):
        das__sprr = das__sprr.val_typ
        sonrm__qjca = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            sonrm__qjca.append(types.int64)
            sonrm__qjca.append(bodo.datetime64ns)
            sonrm__qjca.append(bodo.timedelta64ns)
            sonrm__qjca.append(bodo.datetime_date_type)
        if das__sprr not in sonrm__qjca:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(das__sprr))
    typ_enum = np.int32(numba_to_c_type(das__sprr))

    def impl(value, reduce_op):
        wvk__kiu = value_to_ptr(value)
        skjh__ctenh = value_to_ptr(value)
        _dist_reduce(wvk__kiu, skjh__ctenh, reduce_op, typ_enum)
        return load_val_ptr(skjh__ctenh, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    das__sprr = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(das__sprr))
    timyk__soneg = das__sprr(0)

    def impl(value, reduce_op):
        wvk__kiu = value_to_ptr(value)
        skjh__ctenh = value_to_ptr(timyk__soneg)
        _dist_exscan(wvk__kiu, skjh__ctenh, reduce_op, typ_enum)
        return load_val_ptr(skjh__ctenh, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    gqovq__zjt = 0
    yhn__wyjtb = 0
    for i in range(len(recv_counts)):
        rscz__pbvm = recv_counts[i]
        bpxdz__dhnl = recv_counts_nulls[i]
        kirxa__qsep = tmp_null_bytes[gqovq__zjt:gqovq__zjt + bpxdz__dhnl]
        for dnxu__fwy in range(rscz__pbvm):
            set_bit_to(null_bitmap_ptr, yhn__wyjtb, get_bit(kirxa__qsep,
                dnxu__fwy))
            yhn__wyjtb += 1
        gqovq__zjt += bpxdz__dhnl


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            zaj__cuc = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                zaj__cuc, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            ttag__epcvq = data.size
            recv_counts = gather_scalar(np.int32(ttag__epcvq), allgather,
                root=root)
            pqqyj__wcxlb = recv_counts.sum()
            szqz__mzaz = empty_like_type(pqqyj__wcxlb, data)
            febs__fno = np.empty(1, np.int32)
            if rank == root or allgather:
                febs__fno = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(ttag__epcvq), szqz__mzaz.ctypes,
                recv_counts.ctypes, febs__fno.ctypes, np.int32(typ_val),
                allgather, np.int32(root))
            return szqz__mzaz.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            szqz__mzaz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.str_arr_ext.init_str_arr(szqz__mzaz)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            szqz__mzaz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(szqz__mzaz)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        ete__ypde = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            ttag__epcvq = len(data)
            bpxdz__dhnl = ttag__epcvq + 7 >> 3
            recv_counts = gather_scalar(np.int32(ttag__epcvq), allgather,
                root=root)
            pqqyj__wcxlb = recv_counts.sum()
            szqz__mzaz = empty_like_type(pqqyj__wcxlb, data)
            febs__fno = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            stjlk__hqlnv = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                febs__fno = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                stjlk__hqlnv = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(ttag__epcvq),
                szqz__mzaz._days_data.ctypes, recv_counts.ctypes, febs__fno
                .ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._seconds_data.ctypes, np.int32(ttag__epcvq),
                szqz__mzaz._seconds_data.ctypes, recv_counts.ctypes,
                febs__fno.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._microseconds_data.ctypes, np.int32(ttag__epcvq),
                szqz__mzaz._microseconds_data.ctypes, recv_counts.ctypes,
                febs__fno.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(bpxdz__dhnl),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                stjlk__hqlnv.ctypes, ete__ypde, allgather, np.int32(root))
            copy_gathered_null_bytes(szqz__mzaz._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return szqz__mzaz
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        ete__ypde = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            ttag__epcvq = len(data)
            bpxdz__dhnl = ttag__epcvq + 7 >> 3
            recv_counts = gather_scalar(np.int32(ttag__epcvq), allgather,
                root=root)
            pqqyj__wcxlb = recv_counts.sum()
            szqz__mzaz = empty_like_type(pqqyj__wcxlb, data)
            febs__fno = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            stjlk__hqlnv = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                febs__fno = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                stjlk__hqlnv = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(ttag__epcvq), szqz__mzaz.
                _data.ctypes, recv_counts.ctypes, febs__fno.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(bpxdz__dhnl),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                stjlk__hqlnv.ctypes, ete__ypde, allgather, np.int32(root))
            copy_gathered_null_bytes(szqz__mzaz._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return szqz__mzaz
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        wum__yqva = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            elp__nwpsj = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                elp__nwpsj, wum__yqva)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            wxu__kzwej = bodo.gatherv(data._left, allgather, warn_if_rep, root)
            uwfd__yyknt = bodo.gatherv(data._right, allgather, warn_if_rep,
                root)
            return bodo.libs.interval_arr_ext.init_interval_array(wxu__kzwej,
                uwfd__yyknt)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            rjfsc__jcs = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            lhjdb__dyqdh = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                lhjdb__dyqdh, rjfsc__jcs)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        bysp__ybwna = np.iinfo(np.int64).max
        gbovi__fshwo = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            vwjac__vnqx = data._start
            nip__jpx = data._stop
            if len(data) == 0:
                vwjac__vnqx = bysp__ybwna
                nip__jpx = gbovi__fshwo
            vwjac__vnqx = bodo.libs.distributed_api.dist_reduce(vwjac__vnqx,
                np.int32(Reduce_Type.Min.value))
            nip__jpx = bodo.libs.distributed_api.dist_reduce(nip__jpx, np.
                int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if vwjac__vnqx == bysp__ybwna and nip__jpx == gbovi__fshwo:
                vwjac__vnqx = 0
                nip__jpx = 0
            hrfjc__vzpit = max(0, -(-(nip__jpx - vwjac__vnqx) // data._step))
            if hrfjc__vzpit < total_len:
                nip__jpx = vwjac__vnqx + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                vwjac__vnqx = 0
                nip__jpx = 0
            return bodo.hiframes.pd_index_ext.init_range_index(vwjac__vnqx,
                nip__jpx, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            rbwc__ispi = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, rbwc__ispi)
        else:

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.utils.conversion.index_from_array(arr, data._name)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            szqz__mzaz = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(szqz__mzaz
                , data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        twsl__bqehp = {'bodo': bodo, 'get_table_block': bodo.hiframes.table
            .get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        ydolg__eqihw = f"""def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):
"""
        ydolg__eqihw += '  T = data\n'
        ydolg__eqihw += '  T2 = init_table(T, True)\n'
        for ayjc__ooq in data.type_to_blk.values():
            twsl__bqehp[f'arr_inds_{ayjc__ooq}'] = np.array(data.
                block_to_arr_ind[ayjc__ooq], dtype=np.int64)
            ydolg__eqihw += (
                f'  arr_list_{ayjc__ooq} = get_table_block(T, {ayjc__ooq})\n')
            ydolg__eqihw += f"""  out_arr_list_{ayjc__ooq} = alloc_list_like(arr_list_{ayjc__ooq}, len(arr_list_{ayjc__ooq}), True)
"""
            ydolg__eqihw += f'  for i in range(len(arr_list_{ayjc__ooq})):\n'
            ydolg__eqihw += (
                f'    arr_ind_{ayjc__ooq} = arr_inds_{ayjc__ooq}[i]\n')
            ydolg__eqihw += f"""    ensure_column_unboxed(T, arr_list_{ayjc__ooq}, i, arr_ind_{ayjc__ooq})
"""
            ydolg__eqihw += f"""    out_arr_{ayjc__ooq} = bodo.gatherv(arr_list_{ayjc__ooq}[i], allgather, warn_if_rep, root)
"""
            ydolg__eqihw += (
                f'    out_arr_list_{ayjc__ooq}[i] = out_arr_{ayjc__ooq}\n')
            ydolg__eqihw += (
                f'  T2 = set_table_block(T2, out_arr_list_{ayjc__ooq}, {ayjc__ooq})\n'
                )
        ydolg__eqihw += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        ydolg__eqihw += f'  T2 = set_table_len(T2, length)\n'
        ydolg__eqihw += f'  return T2\n'
        oxe__xjijn = {}
        exec(ydolg__eqihw, twsl__bqehp, oxe__xjijn)
        ncp__bsm = oxe__xjijn['impl_table']
        return ncp__bsm
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        glqys__ulbd = len(data.columns)
        if glqys__ulbd == 0:
            jvuwm__hbda = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                xaz__rmqyx = bodo.gatherv(index, allgather, warn_if_rep, root)
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    xaz__rmqyx, jvuwm__hbda)
            return impl
        ohr__ktmeh = ', '.join(f'g_data_{i}' for i in range(glqys__ulbd))
        ydolg__eqihw = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            oktu__epr = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            ohr__ktmeh = 'T2'
            ydolg__eqihw += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            ydolg__eqihw += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(glqys__ulbd):
                ydolg__eqihw += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                ydolg__eqihw += (
                    """  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)
"""
                    .format(i, i))
        ydolg__eqihw += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        ydolg__eqihw += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        ydolg__eqihw += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(ohr__ktmeh))
        oxe__xjijn = {}
        twsl__bqehp = {'bodo': bodo,
            '__col_name_meta_value_gatherv_with_cols': ColNamesMetaType(
            data.columns)}
        exec(ydolg__eqihw, twsl__bqehp, oxe__xjijn)
        zspa__jnvj = oxe__xjijn['impl_df']
        return zspa__jnvj
    if isinstance(data, ArrayItemArrayType):
        vhs__cwr = np.int32(numba_to_c_type(types.int32))
        ete__ypde = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            tukue__gdr = bodo.libs.array_item_arr_ext.get_offsets(data)
            ifodv__yne = bodo.libs.array_item_arr_ext.get_data(data)
            ifodv__yne = ifodv__yne[:tukue__gdr[-1]]
            bnvt__awh = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            ttag__epcvq = len(data)
            vgu__ceyoa = np.empty(ttag__epcvq, np.uint32)
            bpxdz__dhnl = ttag__epcvq + 7 >> 3
            for i in range(ttag__epcvq):
                vgu__ceyoa[i] = tukue__gdr[i + 1] - tukue__gdr[i]
            recv_counts = gather_scalar(np.int32(ttag__epcvq), allgather,
                root=root)
            pqqyj__wcxlb = recv_counts.sum()
            febs__fno = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            stjlk__hqlnv = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                febs__fno = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for efy__zcag in range(len(recv_counts)):
                    recv_counts_nulls[efy__zcag] = recv_counts[efy__zcag
                        ] + 7 >> 3
                stjlk__hqlnv = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            aigwm__bzg = np.empty(pqqyj__wcxlb + 1, np.uint32)
            vkdur__mpl = bodo.gatherv(ifodv__yne, allgather, warn_if_rep, root)
            hpzbu__mwt = np.empty(pqqyj__wcxlb + 7 >> 3, np.uint8)
            c_gatherv(vgu__ceyoa.ctypes, np.int32(ttag__epcvq), aigwm__bzg.
                ctypes, recv_counts.ctypes, febs__fno.ctypes, vhs__cwr,
                allgather, np.int32(root))
            c_gatherv(bnvt__awh.ctypes, np.int32(bpxdz__dhnl),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                stjlk__hqlnv.ctypes, ete__ypde, allgather, np.int32(root))
            dummy_use(data)
            mqwh__wskd = np.empty(pqqyj__wcxlb + 1, np.uint64)
            convert_len_arr_to_offset(aigwm__bzg.ctypes, mqwh__wskd.ctypes,
                pqqyj__wcxlb)
            copy_gathered_null_bytes(hpzbu__mwt.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                pqqyj__wcxlb, vkdur__mpl, mqwh__wskd, hpzbu__mwt)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        wqkp__ces = data.names
        ete__ypde = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            zyth__wqo = bodo.libs.struct_arr_ext.get_data(data)
            ztvxf__eudcg = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            mcsy__jgkmp = bodo.gatherv(zyth__wqo, allgather=allgather, root
                =root)
            rank = bodo.libs.distributed_api.get_rank()
            ttag__epcvq = len(data)
            bpxdz__dhnl = ttag__epcvq + 7 >> 3
            recv_counts = gather_scalar(np.int32(ttag__epcvq), allgather,
                root=root)
            pqqyj__wcxlb = recv_counts.sum()
            hys__oqbrt = np.empty(pqqyj__wcxlb + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            stjlk__hqlnv = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                stjlk__hqlnv = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(ztvxf__eudcg.ctypes, np.int32(bpxdz__dhnl),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                stjlk__hqlnv.ctypes, ete__ypde, allgather, np.int32(root))
            copy_gathered_null_bytes(hys__oqbrt.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(mcsy__jgkmp,
                hys__oqbrt, wqkp__ces)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            szqz__mzaz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(szqz__mzaz)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            szqz__mzaz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(szqz__mzaz)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            szqz__mzaz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.map_arr_ext.init_map_arr(szqz__mzaz)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            szqz__mzaz = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            wzkm__pmmg = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            nxzjy__fpvac = bodo.gatherv(data.indptr, allgather, warn_if_rep,
                root)
            auikp__phm = gather_scalar(data.shape[0], allgather, root=root)
            jnxsk__dtk = auikp__phm.sum()
            glqys__ulbd = bodo.libs.distributed_api.dist_reduce(data.shape[
                1], np.int32(Reduce_Type.Max.value))
            gyrds__xof = np.empty(jnxsk__dtk + 1, np.int64)
            wzkm__pmmg = wzkm__pmmg.astype(np.int64)
            gyrds__xof[0] = 0
            gisgh__eiunf = 1
            nqab__zoi = 0
            for udjh__rvcz in auikp__phm:
                for ughz__zewf in range(udjh__rvcz):
                    vepfk__dmc = nxzjy__fpvac[nqab__zoi + 1] - nxzjy__fpvac[
                        nqab__zoi]
                    gyrds__xof[gisgh__eiunf] = gyrds__xof[gisgh__eiunf - 1
                        ] + vepfk__dmc
                    gisgh__eiunf += 1
                    nqab__zoi += 1
                nqab__zoi += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(szqz__mzaz,
                wzkm__pmmg, gyrds__xof, (jnxsk__dtk, glqys__ulbd))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        ydolg__eqihw = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        ydolg__eqihw += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        oxe__xjijn = {}
        exec(ydolg__eqihw, {'bodo': bodo}, oxe__xjijn)
        fltj__hftwu = oxe__xjijn['impl_tuple']
        return fltj__hftwu
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    ydolg__eqihw = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    ydolg__eqihw += '    if random:\n'
    ydolg__eqihw += '        if random_seed is None:\n'
    ydolg__eqihw += '            random = 1\n'
    ydolg__eqihw += '        else:\n'
    ydolg__eqihw += '            random = 2\n'
    ydolg__eqihw += '    if random_seed is None:\n'
    ydolg__eqihw += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        mcwzv__dla = data
        glqys__ulbd = len(mcwzv__dla.columns)
        for i in range(glqys__ulbd):
            ydolg__eqihw += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        ydolg__eqihw += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        ohr__ktmeh = ', '.join(f'data_{i}' for i in range(glqys__ulbd))
        ydolg__eqihw += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(ohsb__qda) for
            ohsb__qda in range(glqys__ulbd))))
        ydolg__eqihw += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        ydolg__eqihw += '    if dests is None:\n'
        ydolg__eqihw += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        ydolg__eqihw += '    else:\n'
        ydolg__eqihw += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for mha__ikmh in range(glqys__ulbd):
            ydolg__eqihw += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(mha__ikmh))
        ydolg__eqihw += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(glqys__ulbd))
        ydolg__eqihw += '    delete_table(out_table)\n'
        ydolg__eqihw += '    if parallel:\n'
        ydolg__eqihw += '        delete_table(table_total)\n'
        ohr__ktmeh = ', '.join('out_arr_{}'.format(i) for i in range(
            glqys__ulbd))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        ydolg__eqihw += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(ohr__ktmeh, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        ydolg__eqihw += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        ydolg__eqihw += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        ydolg__eqihw += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        ydolg__eqihw += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        ydolg__eqihw += '    if dests is None:\n'
        ydolg__eqihw += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        ydolg__eqihw += '    else:\n'
        ydolg__eqihw += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        ydolg__eqihw += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        ydolg__eqihw += """    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)
"""
        ydolg__eqihw += '    delete_table(out_table)\n'
        ydolg__eqihw += '    if parallel:\n'
        ydolg__eqihw += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        ydolg__eqihw += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        ydolg__eqihw += '    if not parallel:\n'
        ydolg__eqihw += '        return data\n'
        ydolg__eqihw += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        ydolg__eqihw += '    if dests is None:\n'
        ydolg__eqihw += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        ydolg__eqihw += '    elif bodo.get_rank() not in dests:\n'
        ydolg__eqihw += '        dim0_local_size = 0\n'
        ydolg__eqihw += '    else:\n'
        ydolg__eqihw += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        ydolg__eqihw += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        ydolg__eqihw += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        ydolg__eqihw += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        ydolg__eqihw += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        ydolg__eqihw += '    if dests is None:\n'
        ydolg__eqihw += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        ydolg__eqihw += '    else:\n'
        ydolg__eqihw += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        ydolg__eqihw += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        ydolg__eqihw += '    delete_table(out_table)\n'
        ydolg__eqihw += '    if parallel:\n'
        ydolg__eqihw += '        delete_table(table_total)\n'
        ydolg__eqihw += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    oxe__xjijn = {}
    twsl__bqehp = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.array
        .array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        twsl__bqehp.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(mcwzv__dla.columns)})
    exec(ydolg__eqihw, twsl__bqehp, oxe__xjijn)
    impl = oxe__xjijn['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    ydolg__eqihw = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        ydolg__eqihw += '    if seed is None:\n'
        ydolg__eqihw += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        ydolg__eqihw += '    np.random.seed(seed)\n'
        ydolg__eqihw += '    if not parallel:\n'
        ydolg__eqihw += '        data = data.copy()\n'
        ydolg__eqihw += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            ydolg__eqihw += '        data = data[:n_samples]\n'
        ydolg__eqihw += '        return data\n'
        ydolg__eqihw += '    else:\n'
        ydolg__eqihw += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        ydolg__eqihw += '        permutation = np.arange(dim0_global_size)\n'
        ydolg__eqihw += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            ydolg__eqihw += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            ydolg__eqihw += '        n_samples = dim0_global_size\n'
        ydolg__eqihw += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        ydolg__eqihw += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        ydolg__eqihw += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        ydolg__eqihw += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        ydolg__eqihw += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        ydolg__eqihw += '        return output\n'
    else:
        ydolg__eqihw += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            ydolg__eqihw += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            ydolg__eqihw += '    output = output[:local_n_samples]\n'
        ydolg__eqihw += '    return output\n'
    oxe__xjijn = {}
    exec(ydolg__eqihw, {'np': np, 'bodo': bodo}, oxe__xjijn)
    impl = oxe__xjijn['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    qxh__ylk = np.empty(sendcounts_nulls.sum(), np.uint8)
    gqovq__zjt = 0
    yhn__wyjtb = 0
    for tjh__bhib in range(len(sendcounts)):
        rscz__pbvm = sendcounts[tjh__bhib]
        bpxdz__dhnl = sendcounts_nulls[tjh__bhib]
        kirxa__qsep = qxh__ylk[gqovq__zjt:gqovq__zjt + bpxdz__dhnl]
        for dnxu__fwy in range(rscz__pbvm):
            set_bit_to_arr(kirxa__qsep, dnxu__fwy, get_bit_bitmap(
                null_bitmap_ptr, yhn__wyjtb))
            yhn__wyjtb += 1
        gqovq__zjt += bpxdz__dhnl
    return qxh__ylk


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    rync__kecal = MPI.COMM_WORLD
    data = rync__kecal.bcast(data, root)
    return data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_scatterv_send_counts(send_counts, n_pes, n):
    if not is_overload_none(send_counts):
        return lambda send_counts, n_pes, n: send_counts

    def impl(send_counts, n_pes, n):
        send_counts = np.empty(n_pes, np.int32)
        for i in range(n_pes):
            send_counts[i] = get_node_portion(n, n_pes, i)
        return send_counts
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _scatterv_np(data, send_counts=None, warn_if_dist=True):
    typ_val = numba_to_c_type(data.dtype)
    qgzbh__nlhs = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    hncg__bit = (0,) * qgzbh__nlhs

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        hfw__ixnl = np.ascontiguousarray(data)
        wmsi__onw = data.ctypes
        fgwxc__hinkf = hncg__bit
        if rank == MPI_ROOT:
            fgwxc__hinkf = hfw__ixnl.shape
        fgwxc__hinkf = bcast_tuple(fgwxc__hinkf)
        gumu__ekm = get_tuple_prod(fgwxc__hinkf[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            fgwxc__hinkf[0])
        send_counts *= gumu__ekm
        ttag__epcvq = send_counts[rank]
        dqj__pwm = np.empty(ttag__epcvq, dtype)
        febs__fno = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(wmsi__onw, send_counts.ctypes, febs__fno.ctypes,
            dqj__pwm.ctypes, np.int32(ttag__epcvq), np.int32(typ_val))
        return dqj__pwm.reshape((-1,) + fgwxc__hinkf[1:])
    return scatterv_arr_impl


def _get_name_value_for_type(name_typ):
    assert isinstance(name_typ, (types.UnicodeType, types.StringLiteral)
        ) or name_typ == types.none
    return None if name_typ == types.none else '_' + str(ir_utils.next_label())


def get_value_for_type(dtype):
    if isinstance(dtype, types.Array):
        return np.zeros((1,) * dtype.ndim, numba.np.numpy_support.as_dtype(
            dtype.dtype))
    if dtype == string_array_type:
        return pd.array(['A'], 'string')
    if dtype == bodo.dict_str_arr_type:
        import pyarrow as pa
        return pa.array(['a'], type=pa.dictionary(pa.int32(), pa.string()))
    if dtype == binary_array_type:
        return np.array([b'A'], dtype=object)
    if isinstance(dtype, IntegerArrayType):
        huod__pct = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], huod__pct)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        rjfsc__jcs = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=rjfsc__jcs)
        wryf__gwb = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(wryf__gwb)
        return pd.Index(arr, name=rjfsc__jcs)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        rjfsc__jcs = _get_name_value_for_type(dtype.name_typ)
        wqkp__ces = tuple(_get_name_value_for_type(t) for t in dtype.names_typ)
        yvpn__ilke = tuple(get_value_for_type(t) for t in dtype.array_types)
        yvpn__ilke = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in yvpn__ilke)
        val = pd.MultiIndex.from_arrays(yvpn__ilke, names=wqkp__ces)
        val.name = rjfsc__jcs
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        rjfsc__jcs = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=rjfsc__jcs)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        yvpn__ilke = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({rjfsc__jcs: arr for rjfsc__jcs, arr in zip(
            dtype.columns, yvpn__ilke)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        wryf__gwb = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(wryf__gwb[0], wryf__gwb
            [0])])
    raise BodoError(f'get_value_for_type(dtype): Missing data type {dtype}')


def scatterv(data, send_counts=None, warn_if_dist=True):
    rank = bodo.libs.distributed_api.get_rank()
    if rank != MPI_ROOT and data is not None:
        warnings.warn(BodoWarning(
            "bodo.scatterv(): A non-None value for 'data' was found on a rank other than the root. This data won't be sent to any other ranks and will be overwritten with data from rank 0."
            ))
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return scatterv_impl(data, send_counts)


@overload(scatterv)
def scatterv_overload(data, send_counts=None, warn_if_dist=True):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.scatterv()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.scatterv()')
    return lambda data, send_counts=None, warn_if_dist=True: scatterv_impl(data
        , send_counts)


@numba.generated_jit(nopython=True)
def scatterv_impl(data, send_counts=None, warn_if_dist=True):
    if isinstance(data, types.Array):
        return lambda data, send_counts=None, warn_if_dist=True: _scatterv_np(
            data, send_counts)
    if is_str_arr_type(data) or data == binary_array_type:
        vhs__cwr = np.int32(numba_to_c_type(types.int32))
        ete__ypde = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            chmg__tbwzj = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            chmg__tbwzj = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        ydolg__eqihw = f"""def impl(
            data, send_counts=None, warn_if_dist=True
        ):  # pragma: no cover
            data = decode_if_dict_array(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            n_all = bodo.libs.distributed_api.bcast_scalar(len(data))

            # convert offsets to lengths of strings
            send_arr_lens = np.empty(
                len(data), np.uint32
            )  # XXX offset type is offset_type, lengths for comm are uint32
            for i in range(len(data)):
                send_arr_lens[i] = bodo.libs.str_arr_ext.get_str_arr_item_length(
                    data, i
                )

            # ------- calculate buffer counts -------

            send_counts = bodo.libs.distributed_api._get_scatterv_send_counts(send_counts, n_pes, n_all)

            # displacements
            displs = bodo.ir.join.calc_disp(send_counts)

            # compute send counts for characters
            send_counts_char = np.empty(n_pes, np.int32)
            if rank == 0:
                curr_str = 0
                for i in range(n_pes):
                    c = 0
                    for _ in range(send_counts[i]):
                        c += send_arr_lens[curr_str]
                        curr_str += 1
                    send_counts_char[i] = c

            bodo.libs.distributed_api.bcast(send_counts_char)

            # displacements for characters
            displs_char = bodo.ir.join.calc_disp(send_counts_char)

            # compute send counts for nulls
            send_counts_nulls = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                send_counts_nulls[i] = (send_counts[i] + 7) >> 3

            # displacements for nulls
            displs_nulls = bodo.ir.join.calc_disp(send_counts_nulls)

            # alloc output array
            n_loc = send_counts[rank]  # total number of elements on this PE
            n_loc_char = send_counts_char[rank]
            recv_arr = {chmg__tbwzj}(n_loc, n_loc_char)

            # ----- string lengths -----------

            recv_lens = np.empty(n_loc, np.uint32)
            bodo.libs.distributed_api.c_scatterv(
                send_arr_lens.ctypes,
                send_counts.ctypes,
                displs.ctypes,
                recv_lens.ctypes,
                np.int32(n_loc),
                int32_typ_enum,
            )

            # TODO: don't hardcode offset type. Also, if offset is 32 bit we can
            # use the same buffer
            bodo.libs.str_arr_ext.convert_len_arr_to_offset(recv_lens.ctypes, bodo.libs.str_arr_ext.get_offset_ptr(recv_arr), n_loc)

            # ----- string characters -----------

            bodo.libs.distributed_api.c_scatterv(
                bodo.libs.str_arr_ext.get_data_ptr(data),
                send_counts_char.ctypes,
                displs_char.ctypes,
                bodo.libs.str_arr_ext.get_data_ptr(recv_arr),
                np.int32(n_loc_char),
                char_typ_enum,
            )

            # ----------- null bitmap -------------

            n_recv_bytes = (n_loc + 7) >> 3

            send_null_bitmap = bodo.libs.distributed_api.get_scatter_null_bytes_buff(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(data), send_counts, send_counts_nulls
            )

            bodo.libs.distributed_api.c_scatterv(
                send_null_bitmap.ctypes,
                send_counts_nulls.ctypes,
                displs_nulls.ctypes,
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(recv_arr),
                np.int32(n_recv_bytes),
                char_typ_enum,
            )

            return recv_arr"""
        oxe__xjijn = dict()
        exec(ydolg__eqihw, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            vhs__cwr, 'char_typ_enum': ete__ypde, 'decode_if_dict_array':
            decode_if_dict_array}, oxe__xjijn)
        impl = oxe__xjijn['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        vhs__cwr = np.int32(numba_to_c_type(types.int32))
        ete__ypde = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            maq__fmjg = bodo.libs.array_item_arr_ext.get_offsets(data)
            hatd__lmts = bodo.libs.array_item_arr_ext.get_data(data)
            hatd__lmts = hatd__lmts[:maq__fmjg[-1]]
            uvots__fnia = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            zhy__mwyh = bcast_scalar(len(data))
            hee__ccysr = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                hee__ccysr[i] = maq__fmjg[i + 1] - maq__fmjg[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                zhy__mwyh)
            febs__fno = bodo.ir.join.calc_disp(send_counts)
            dctr__tlhok = np.empty(n_pes, np.int32)
            if rank == 0:
                dgq__wnu = 0
                for i in range(n_pes):
                    bszs__jvz = 0
                    for ughz__zewf in range(send_counts[i]):
                        bszs__jvz += hee__ccysr[dgq__wnu]
                        dgq__wnu += 1
                    dctr__tlhok[i] = bszs__jvz
            bcast(dctr__tlhok)
            jdeuc__lya = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                jdeuc__lya[i] = send_counts[i] + 7 >> 3
            stjlk__hqlnv = bodo.ir.join.calc_disp(jdeuc__lya)
            ttag__epcvq = send_counts[rank]
            kxfo__mgfu = np.empty(ttag__epcvq + 1, np_offset_type)
            pit__yka = bodo.libs.distributed_api.scatterv_impl(hatd__lmts,
                dctr__tlhok)
            zxbr__sohln = ttag__epcvq + 7 >> 3
            pwqug__hrxbg = np.empty(zxbr__sohln, np.uint8)
            rmq__szzn = np.empty(ttag__epcvq, np.uint32)
            c_scatterv(hee__ccysr.ctypes, send_counts.ctypes, febs__fno.
                ctypes, rmq__szzn.ctypes, np.int32(ttag__epcvq), vhs__cwr)
            convert_len_arr_to_offset(rmq__szzn.ctypes, kxfo__mgfu.ctypes,
                ttag__epcvq)
            yqg__mop = get_scatter_null_bytes_buff(uvots__fnia.ctypes,
                send_counts, jdeuc__lya)
            c_scatterv(yqg__mop.ctypes, jdeuc__lya.ctypes, stjlk__hqlnv.
                ctypes, pwqug__hrxbg.ctypes, np.int32(zxbr__sohln), ete__ypde)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                ttag__epcvq, pit__yka, kxfo__mgfu, pwqug__hrxbg)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        ete__ypde = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            ffib__ipis = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            ffib__ipis = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            ffib__ipis = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            ffib__ipis = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            hfw__ixnl = data._data
            ztvxf__eudcg = data._null_bitmap
            xum__lkbbc = len(hfw__ixnl)
            iiui__bavh = _scatterv_np(hfw__ixnl, send_counts)
            zhy__mwyh = bcast_scalar(xum__lkbbc)
            cxho__xrjks = len(iiui__bavh) + 7 >> 3
            nba__fbjih = np.empty(cxho__xrjks, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                zhy__mwyh)
            jdeuc__lya = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                jdeuc__lya[i] = send_counts[i] + 7 >> 3
            stjlk__hqlnv = bodo.ir.join.calc_disp(jdeuc__lya)
            yqg__mop = get_scatter_null_bytes_buff(ztvxf__eudcg.ctypes,
                send_counts, jdeuc__lya)
            c_scatterv(yqg__mop.ctypes, jdeuc__lya.ctypes, stjlk__hqlnv.
                ctypes, nba__fbjih.ctypes, np.int32(cxho__xrjks), ete__ypde)
            return ffib__ipis(iiui__bavh, nba__fbjih)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            cidpg__lux = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            eqqur__hir = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(cidpg__lux,
                eqqur__hir)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            vwjac__vnqx = data._start
            nip__jpx = data._stop
            zhum__syif = data._step
            rjfsc__jcs = data._name
            rjfsc__jcs = bcast_scalar(rjfsc__jcs)
            vwjac__vnqx = bcast_scalar(vwjac__vnqx)
            nip__jpx = bcast_scalar(nip__jpx)
            zhum__syif = bcast_scalar(zhum__syif)
            qne__mpag = bodo.libs.array_kernels.calc_nitems(vwjac__vnqx,
                nip__jpx, zhum__syif)
            chunk_start = bodo.libs.distributed_api.get_start(qne__mpag,
                n_pes, rank)
            xaju__jmi = bodo.libs.distributed_api.get_node_portion(qne__mpag,
                n_pes, rank)
            umsox__dmwxx = vwjac__vnqx + zhum__syif * chunk_start
            aewms__pslu = vwjac__vnqx + zhum__syif * (chunk_start + xaju__jmi)
            aewms__pslu = min(aewms__pslu, nip__jpx)
            return bodo.hiframes.pd_index_ext.init_range_index(umsox__dmwxx,
                aewms__pslu, zhum__syif, rjfsc__jcs)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        rbwc__ispi = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            hfw__ixnl = data._data
            rjfsc__jcs = data._name
            rjfsc__jcs = bcast_scalar(rjfsc__jcs)
            arr = bodo.libs.distributed_api.scatterv_impl(hfw__ixnl,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                rjfsc__jcs, rbwc__ispi)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            hfw__ixnl = data._data
            rjfsc__jcs = data._name
            rjfsc__jcs = bcast_scalar(rjfsc__jcs)
            arr = bodo.libs.distributed_api.scatterv_impl(hfw__ixnl,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, rjfsc__jcs)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            szqz__mzaz = bodo.libs.distributed_api.scatterv_impl(data._data,
                send_counts)
            rjfsc__jcs = bcast_scalar(data._name)
            wqkp__ces = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(szqz__mzaz
                , wqkp__ces, rjfsc__jcs)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            rjfsc__jcs = bodo.hiframes.pd_series_ext.get_series_name(data)
            ice__gjbl = bcast_scalar(rjfsc__jcs)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            lhjdb__dyqdh = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                lhjdb__dyqdh, ice__gjbl)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        glqys__ulbd = len(data.columns)
        ohr__ktmeh = ', '.join('g_data_{}'.format(i) for i in range(
            glqys__ulbd))
        tsqpy__ykxiv = ColNamesMetaType(data.columns)
        ydolg__eqihw = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        for i in range(glqys__ulbd):
            ydolg__eqihw += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            ydolg__eqihw += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        ydolg__eqihw += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        ydolg__eqihw += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        ydolg__eqihw += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({ohr__ktmeh},), g_index, __col_name_meta_scaterv_impl)
"""
        oxe__xjijn = {}
        exec(ydolg__eqihw, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            tsqpy__ykxiv}, oxe__xjijn)
        zspa__jnvj = oxe__xjijn['impl_df']
        return zspa__jnvj
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            zaj__cuc = bodo.libs.distributed_api.scatterv_impl(data.codes,
                send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                zaj__cuc, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        ydolg__eqihw = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        ydolg__eqihw += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        oxe__xjijn = {}
        exec(ydolg__eqihw, {'bodo': bodo}, oxe__xjijn)
        fltj__hftwu = oxe__xjijn['impl_tuple']
        return fltj__hftwu
    if data is types.none:
        return lambda data, send_counts=None, warn_if_dist=True: None
    raise BodoError('scatterv() not available for {}'.format(data))


@intrinsic
def cptr_to_voidptr(typingctx, cptr_tp=None):

    def codegen(context, builder, sig, args):
        return builder.bitcast(args[0], lir.IntType(8).as_pointer())
    return types.voidptr(cptr_tp), codegen


def bcast(data, root=MPI_ROOT):
    return


@overload(bcast, no_unliteral=True)
def bcast_overload(data, root=MPI_ROOT):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.bcast()')
    if isinstance(data, types.Array):

        def bcast_impl(data, root=MPI_ROOT):
            typ_enum = get_type_enum(data)
            count = data.size
            assert count < INT_MAX
            c_bcast(data.ctypes, np.int32(count), typ_enum, np.array([-1]).
                ctypes, 0, np.int32(root))
            return
        return bcast_impl
    if isinstance(data, DecimalArrayType):

        def bcast_decimal_arr(data, root=MPI_ROOT):
            count = data._data.size
            assert count < INT_MAX
            c_bcast(data._data.ctypes, np.int32(count), CTypeEnum.Int128.
                value, np.array([-1]).ctypes, 0, np.int32(root))
            bcast(data._null_bitmap, root)
            return
        return bcast_decimal_arr
    if isinstance(data, IntegerArrayType) or data in (boolean_array,
        datetime_date_array_type):

        def bcast_impl_int_arr(data, root=MPI_ROOT):
            bcast(data._data, root)
            bcast(data._null_bitmap, root)
            return
        return bcast_impl_int_arr
    if is_str_arr_type(data) or data == binary_array_type:
        jdnnb__wxo = np.int32(numba_to_c_type(offset_type))
        ete__ypde = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            ttag__epcvq = len(data)
            ldyln__sxi = num_total_chars(data)
            assert ttag__epcvq < INT_MAX
            assert ldyln__sxi < INT_MAX
            zji__eztwo = get_offset_ptr(data)
            wmsi__onw = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            bpxdz__dhnl = ttag__epcvq + 7 >> 3
            c_bcast(zji__eztwo, np.int32(ttag__epcvq + 1), jdnnb__wxo, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(wmsi__onw, np.int32(ldyln__sxi), ete__ypde, np.array([-
                1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(bpxdz__dhnl), ete__ypde, np.
                array([-1]).ctypes, 0, np.int32(root))
        return bcast_str_impl


c_bcast = types.ExternalFunction('c_bcast', types.void(types.voidptr, types
    .int32, types.int32, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def bcast_scalar(val, root=MPI_ROOT):
    val = types.unliteral(val)
    if not (isinstance(val, (types.Integer, types.Float)) or val in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.string_type, types.none,
        types.bool_]):
        raise BodoError(
            f'bcast_scalar requires an argument of type Integer, Float, datetime64ns, timedelta64ns, string, None, or Bool. Found type {val}'
            )
    if val == types.none:
        return lambda val, root=MPI_ROOT: None
    if val == bodo.string_type:
        ete__ypde = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                gqgmd__oyni = 0
                oaz__tdzih = np.empty(0, np.uint8).ctypes
            else:
                oaz__tdzih, gqgmd__oyni = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            gqgmd__oyni = bodo.libs.distributed_api.bcast_scalar(gqgmd__oyni,
                root)
            if rank != root:
                ecyhc__xxgx = np.empty(gqgmd__oyni + 1, np.uint8)
                ecyhc__xxgx[gqgmd__oyni] = 0
                oaz__tdzih = ecyhc__xxgx.ctypes
            c_bcast(oaz__tdzih, np.int32(gqgmd__oyni), ete__ypde, np.array(
                [-1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(oaz__tdzih, gqgmd__oyni)
        return impl_str
    typ_val = numba_to_c_type(val)
    ydolg__eqihw = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    oxe__xjijn = {}
    exec(ydolg__eqihw, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, oxe__xjijn)
    fvda__tvq = oxe__xjijn['bcast_scalar_impl']
    return fvda__tvq


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    zfvuv__ssdd = len(val)
    ydolg__eqihw = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    ydolg__eqihw += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(zfvuv__ssdd)
        ), ',' if zfvuv__ssdd else '')
    oxe__xjijn = {}
    exec(ydolg__eqihw, {'bcast_scalar': bcast_scalar}, oxe__xjijn)
    qwjf__acwoo = oxe__xjijn['bcast_tuple_impl']
    return qwjf__acwoo


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            ttag__epcvq = bcast_scalar(len(arr), root)
            enfdp__btvh = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(ttag__epcvq, enfdp__btvh)
            return arr
        return prealloc_impl
    return lambda arr, root=MPI_ROOT: arr


def get_local_slice(idx, arr_start, total_len):
    return idx


@overload(get_local_slice, no_unliteral=True, jit_options={'cache': True,
    'no_cpython_wrapper': True})
def get_local_slice_overload(idx, arr_start, total_len):
    if not idx.has_step:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            umsox__dmwxx = max(arr_start, slice_index.start) - arr_start
            aewms__pslu = max(slice_index.stop - arr_start, 0)
            return slice(umsox__dmwxx, aewms__pslu)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            vwjac__vnqx = slice_index.start
            zhum__syif = slice_index.step
            qqbf__iwe = (0 if zhum__syif == 1 or vwjac__vnqx > arr_start else
                abs(zhum__syif - arr_start % zhum__syif) % zhum__syif)
            umsox__dmwxx = max(arr_start, slice_index.start
                ) - arr_start + qqbf__iwe
            aewms__pslu = max(slice_index.stop - arr_start, 0)
            return slice(umsox__dmwxx, aewms__pslu, zhum__syif)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        tytls__bbj = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[tytls__bbj])
    return getitem_impl


dummy_use = numba.njit(lambda a: None)


def int_getitem(arr, ind, arr_start, total_len, is_1D):
    return arr[ind]


def transform_str_getitem_output(data, length):
    pass


@overload(transform_str_getitem_output)
def overload_transform_str_getitem_output(data, length):
    if data == bodo.string_type:
        return lambda data, length: bodo.libs.str_arr_ext.decode_utf8(data.
            _data, length)
    if data == types.Array(types.uint8, 1, 'C'):
        return lambda data, length: bodo.libs.binary_arr_ext.init_bytes_type(
            data, length)
    raise BodoError(
        f'Internal Error: Expected String or Uint8 Array, found {data}')


@overload(int_getitem, no_unliteral=True)
def int_getitem_overload(arr, ind, arr_start, total_len, is_1D):
    if is_str_arr_type(arr) or arr == bodo.binary_array_type:
        nohgn__ancym = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        ete__ypde = np.int32(numba_to_c_type(types.uint8))
        uufup__mdkx = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            cxi__eccpv = np.int32(10)
            tag = np.int32(11)
            xne__ypcw = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                ifodv__yne = arr._data
                qfcsj__pdf = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    ifodv__yne, ind)
                cgw__gou = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    ifodv__yne, ind + 1)
                length = cgw__gou - qfcsj__pdf
                nupb__uuyc = ifodv__yne[ind]
                xne__ypcw[0] = length
                isend(xne__ypcw, np.int32(1), root, cxi__eccpv, True)
                isend(nupb__uuyc, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                uufup__mdkx, nohgn__ancym, 0, 1)
            hrfjc__vzpit = 0
            if rank == root:
                hrfjc__vzpit = recv(np.int64, ANY_SOURCE, cxi__eccpv)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    uufup__mdkx, nohgn__ancym, hrfjc__vzpit, 1)
                wmsi__onw = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(wmsi__onw, np.int32(hrfjc__vzpit), ete__ypde,
                    ANY_SOURCE, tag)
            dummy_use(xne__ypcw)
            hrfjc__vzpit = bcast_scalar(hrfjc__vzpit)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    uufup__mdkx, nohgn__ancym, hrfjc__vzpit, 1)
            wmsi__onw = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(wmsi__onw, np.int32(hrfjc__vzpit), ete__ypde, np.array(
                [-1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, hrfjc__vzpit)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        vga__wuq = bodo.hiframes.pd_categorical_ext.get_categories_int_type(arr
            .dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, vga__wuq)
            if arr_start <= ind < arr_start + len(arr):
                zaj__cuc = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = zaj__cuc[ind - arr_start]
                send_arr = np.full(1, data, vga__wuq)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = vga__wuq(-1)
            if rank == root:
                val = recv(vga__wuq, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            fqx__wcrkf = arr.dtype.categories[max(val, 0)]
            return fqx__wcrkf
        return cat_getitem_impl
    ohqhl__ddt = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, ohqhl__ddt)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, ohqhl__ddt)[0]
        if rank == root:
            val = recv(ohqhl__ddt, ANY_SOURCE, tag)
        dummy_use(send_arr)
        val = bcast_scalar(val)
        return val
    return getitem_impl


c_alltoallv = types.ExternalFunction('c_alltoallv', types.void(types.
    voidptr, types.voidptr, types.voidptr, types.voidptr, types.voidptr,
    types.voidptr, types.int32))


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def alltoallv(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    typ_enum = get_type_enum(send_data)
    ytrfq__duam = get_type_enum(out_data)
    assert typ_enum == ytrfq__duam
    if isinstance(send_data, (IntegerArrayType, DecimalArrayType)
        ) or send_data in (boolean_array, datetime_date_array_type):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data._data.ctypes,
            out_data._data.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    if isinstance(send_data, bodo.CategoricalArrayType):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data.codes.ctypes,
            out_data.codes.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    return (lambda send_data, out_data, send_counts, recv_counts, send_disp,
        recv_disp: c_alltoallv(send_data.ctypes, out_data.ctypes,
        send_counts.ctypes, recv_counts.ctypes, send_disp.ctypes, recv_disp
        .ctypes, typ_enum))


def alltoallv_tup(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    return


@overload(alltoallv_tup, no_unliteral=True)
def alltoallv_tup_overload(send_data, out_data, send_counts, recv_counts,
    send_disp, recv_disp):
    count = send_data.count
    assert out_data.count == count
    ydolg__eqihw = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        ydolg__eqihw += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    ydolg__eqihw += '  return\n'
    oxe__xjijn = {}
    exec(ydolg__eqihw, {'alltoallv': alltoallv}, oxe__xjijn)
    alsoc__miw = oxe__xjijn['f']
    return alsoc__miw


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    vwjac__vnqx = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return vwjac__vnqx, count


@numba.njit
def get_start(total_size, pes, rank):
    les__ibqs = total_size % pes
    ipxy__lzaue = (total_size - les__ibqs) // pes
    return rank * ipxy__lzaue + min(rank, les__ibqs)


@numba.njit
def get_end(total_size, pes, rank):
    les__ibqs = total_size % pes
    ipxy__lzaue = (total_size - les__ibqs) // pes
    return (rank + 1) * ipxy__lzaue + min(rank + 1, les__ibqs)


@numba.njit
def get_node_portion(total_size, pes, rank):
    les__ibqs = total_size % pes
    ipxy__lzaue = (total_size - les__ibqs) // pes
    if rank < les__ibqs:
        return ipxy__lzaue + 1
    else:
        return ipxy__lzaue


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    timyk__soneg = in_arr.dtype(0)
    qxuyt__tqyh = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        bszs__jvz = timyk__soneg
        for bfgy__bmx in np.nditer(in_arr):
            bszs__jvz += bfgy__bmx.item()
        rsms__xkck = dist_exscan(bszs__jvz, qxuyt__tqyh)
        for i in range(in_arr.size):
            rsms__xkck += in_arr[i]
            out_arr[i] = rsms__xkck
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    xqg__kfo = in_arr.dtype(1)
    qxuyt__tqyh = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        bszs__jvz = xqg__kfo
        for bfgy__bmx in np.nditer(in_arr):
            bszs__jvz *= bfgy__bmx.item()
        rsms__xkck = dist_exscan(bszs__jvz, qxuyt__tqyh)
        if get_rank() == 0:
            rsms__xkck = xqg__kfo
        for i in range(in_arr.size):
            rsms__xkck *= in_arr[i]
            out_arr[i] = rsms__xkck
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        xqg__kfo = np.finfo(in_arr.dtype(1).dtype).max
    else:
        xqg__kfo = np.iinfo(in_arr.dtype(1).dtype).max
    qxuyt__tqyh = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        bszs__jvz = xqg__kfo
        for bfgy__bmx in np.nditer(in_arr):
            bszs__jvz = min(bszs__jvz, bfgy__bmx.item())
        rsms__xkck = dist_exscan(bszs__jvz, qxuyt__tqyh)
        if get_rank() == 0:
            rsms__xkck = xqg__kfo
        for i in range(in_arr.size):
            rsms__xkck = min(rsms__xkck, in_arr[i])
            out_arr[i] = rsms__xkck
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        xqg__kfo = np.finfo(in_arr.dtype(1).dtype).min
    else:
        xqg__kfo = np.iinfo(in_arr.dtype(1).dtype).min
    xqg__kfo = in_arr.dtype(1)
    qxuyt__tqyh = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        bszs__jvz = xqg__kfo
        for bfgy__bmx in np.nditer(in_arr):
            bszs__jvz = max(bszs__jvz, bfgy__bmx.item())
        rsms__xkck = dist_exscan(bszs__jvz, qxuyt__tqyh)
        if get_rank() == 0:
            rsms__xkck = xqg__kfo
        for i in range(in_arr.size):
            rsms__xkck = max(rsms__xkck, in_arr[i])
            out_arr[i] = rsms__xkck
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    kha__lnoe = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), kha__lnoe)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    uot__jyf = args[0]
    if equiv_set.has_shape(uot__jyf):
        return ArrayAnalysis.AnalyzeResult(shape=uot__jyf, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_distributed_api_dist_return = (
    dist_return_equiv)
ArrayAnalysis._analyze_op_call_bodo_libs_distributed_api_rep_return = (
    dist_return_equiv)


def threaded_return(A):
    return A


@numba.njit
def set_arr_local(arr, ind, val):
    arr[ind] = val


@numba.njit
def local_alloc_size(n, in_arr):
    return n


@infer_global(threaded_return)
@infer_global(dist_return)
@infer_global(rep_return)
class ThreadedRetTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        return signature(args[0], *args)


@numba.njit
def parallel_print(*args):
    print(*args)


@numba.njit
def single_print(*args):
    if bodo.libs.distributed_api.get_rank() == 0:
        print(*args)


def print_if_not_empty(args):
    pass


@overload(print_if_not_empty)
def overload_print_if_not_empty(*args):
    qsg__lpwr = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for i,
        hlsha__wxjls in enumerate(args) if is_array_typ(hlsha__wxjls) or
        isinstance(hlsha__wxjls, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    ydolg__eqihw = f"""def impl(*args):
    if {qsg__lpwr} or bodo.get_rank() == 0:
        print(*args)"""
    oxe__xjijn = {}
    exec(ydolg__eqihw, globals(), oxe__xjijn)
    impl = oxe__xjijn['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        wys__saly = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        ydolg__eqihw = 'def f(req, cond=True):\n'
        ydolg__eqihw += f'  return {wys__saly}\n'
        oxe__xjijn = {}
        exec(ydolg__eqihw, {'_wait': _wait}, oxe__xjijn)
        impl = oxe__xjijn['f']
        return impl
    if is_overload_none(req):
        return lambda req, cond=True: None
    return lambda req, cond=True: _wait(req, cond)


@register_jitable
def _set_if_in_range(A, val, index, chunk_start):
    if index >= chunk_start and index < chunk_start + len(A):
        A[index - chunk_start] = val


@register_jitable
def _root_rank_select(old_val, new_val):
    if get_rank() == 0:
        return old_val
    return new_val


def get_tuple_prod(t):
    return np.prod(t)


@overload(get_tuple_prod, no_unliteral=True)
def get_tuple_prod_overload(t):
    if t == numba.core.types.containers.Tuple(()):
        return lambda t: 1

    def get_tuple_prod_impl(t):
        les__ibqs = 1
        for a in t:
            les__ibqs *= a
        return les__ibqs
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    rqoia__hzi = np.ascontiguousarray(in_arr)
    bwpq__akhgp = get_tuple_prod(rqoia__hzi.shape[1:])
    utfjr__xgk = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        xsi__gkpfb = np.array(dest_ranks, dtype=np.int32)
    else:
        xsi__gkpfb = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, rqoia__hzi.ctypes, new_dim0_global_len,
        len(in_arr), dtype_size * utfjr__xgk, dtype_size * bwpq__akhgp, len
        (xsi__gkpfb), xsi__gkpfb.ctypes)
    check_and_propagate_cpp_exception()


permutation_int = types.ExternalFunction('permutation_int', types.void(
    types.voidptr, types.intp))


@numba.njit
def dist_permutation_int(lhs, n):
    permutation_int(lhs.ctypes, n)


permutation_array_index = types.ExternalFunction('permutation_array_index',
    types.void(types.voidptr, types.intp, types.intp, types.voidptr, types.
    int64, types.voidptr, types.intp, types.int64))


@numba.njit
def dist_permutation_array_index(lhs, lhs_len, dtype_size, rhs, p, p_len,
    n_samples):
    wrvgb__fkv = np.ascontiguousarray(rhs)
    bqodc__wlkkf = get_tuple_prod(wrvgb__fkv.shape[1:])
    qowu__ykom = dtype_size * bqodc__wlkkf
    permutation_array_index(lhs.ctypes, lhs_len, qowu__ykom, wrvgb__fkv.
        ctypes, wrvgb__fkv.shape[0], p.ctypes, p_len, n_samples)
    check_and_propagate_cpp_exception()


from bodo.io import fsspec_reader, hdfs_reader, s3_reader
ll.add_symbol('finalize', hdist.finalize)
finalize = types.ExternalFunction('finalize', types.int32())
ll.add_symbol('finalize_s3', s3_reader.finalize_s3)
finalize_s3 = types.ExternalFunction('finalize_s3', types.int32())
ll.add_symbol('finalize_fsspec', fsspec_reader.finalize_fsspec)
finalize_fsspec = types.ExternalFunction('finalize_fsspec', types.int32())
ll.add_symbol('disconnect_hdfs', hdfs_reader.disconnect_hdfs)
disconnect_hdfs = types.ExternalFunction('disconnect_hdfs', types.int32())


def _check_for_cpp_errors():
    pass


@overload(_check_for_cpp_errors)
def overload_check_for_cpp_errors():
    return lambda : check_and_propagate_cpp_exception()


@numba.njit
def call_finalize():
    finalize()
    finalize_s3()
    finalize_fsspec()
    _check_for_cpp_errors()
    disconnect_hdfs()


def flush_stdout():
    if not sys.stdout.closed:
        sys.stdout.flush()


atexit.register(call_finalize)
atexit.register(flush_stdout)


def bcast_comm(data, comm_ranks, nranks, root=MPI_ROOT):
    rank = bodo.libs.distributed_api.get_rank()
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype, root)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return bcast_comm_impl(data, comm_ranks, nranks, root)


@overload(bcast_comm)
def bcast_comm_overload(data, comm_ranks, nranks, root=MPI_ROOT):
    return lambda data, comm_ranks, nranks, root=MPI_ROOT: bcast_comm_impl(data
        , comm_ranks, nranks, root)


@numba.generated_jit(nopython=True)
def bcast_comm_impl(data, comm_ranks, nranks, root=MPI_ROOT):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.bcast_comm()')
    if isinstance(data, (types.Integer, types.Float)):
        typ_val = numba_to_c_type(data)
        ydolg__eqihw = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        oxe__xjijn = {}
        exec(ydolg__eqihw, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, oxe__xjijn)
        fvda__tvq = oxe__xjijn['bcast_scalar_impl']
        return fvda__tvq
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        glqys__ulbd = len(data.columns)
        ohr__ktmeh = ', '.join('g_data_{}'.format(i) for i in range(
            glqys__ulbd))
        atrx__npno = ColNamesMetaType(data.columns)
        ydolg__eqihw = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(glqys__ulbd):
            ydolg__eqihw += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            ydolg__eqihw += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        ydolg__eqihw += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        ydolg__eqihw += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        ydolg__eqihw += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_bcast_comm)
"""
            .format(ohr__ktmeh))
        oxe__xjijn = {}
        exec(ydolg__eqihw, {'bodo': bodo,
            '__col_name_meta_value_bcast_comm': atrx__npno}, oxe__xjijn)
        zspa__jnvj = oxe__xjijn['impl_df']
        return zspa__jnvj
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            vwjac__vnqx = data._start
            nip__jpx = data._stop
            zhum__syif = data._step
            rjfsc__jcs = data._name
            rjfsc__jcs = bcast_scalar(rjfsc__jcs, root)
            vwjac__vnqx = bcast_scalar(vwjac__vnqx, root)
            nip__jpx = bcast_scalar(nip__jpx, root)
            zhum__syif = bcast_scalar(zhum__syif, root)
            qne__mpag = bodo.libs.array_kernels.calc_nitems(vwjac__vnqx,
                nip__jpx, zhum__syif)
            chunk_start = bodo.libs.distributed_api.get_start(qne__mpag,
                n_pes, rank)
            xaju__jmi = bodo.libs.distributed_api.get_node_portion(qne__mpag,
                n_pes, rank)
            umsox__dmwxx = vwjac__vnqx + zhum__syif * chunk_start
            aewms__pslu = vwjac__vnqx + zhum__syif * (chunk_start + xaju__jmi)
            aewms__pslu = min(aewms__pslu, nip__jpx)
            return bodo.hiframes.pd_index_ext.init_range_index(umsox__dmwxx,
                aewms__pslu, zhum__syif, rjfsc__jcs)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            hfw__ixnl = data._data
            rjfsc__jcs = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(hfw__ixnl,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, rjfsc__jcs)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            rjfsc__jcs = bodo.hiframes.pd_series_ext.get_series_name(data)
            ice__gjbl = bodo.libs.distributed_api.bcast_comm_impl(rjfsc__jcs,
                comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            lhjdb__dyqdh = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                lhjdb__dyqdh, ice__gjbl)
        return impl_series
    if isinstance(data, types.BaseTuple):
        ydolg__eqihw = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        ydolg__eqihw += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        oxe__xjijn = {}
        exec(ydolg__eqihw, {'bcast_comm_impl': bcast_comm_impl}, oxe__xjijn)
        fltj__hftwu = oxe__xjijn['impl_tuple']
        return fltj__hftwu
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    qgzbh__nlhs = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    hncg__bit = (0,) * qgzbh__nlhs

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        hfw__ixnl = np.ascontiguousarray(data)
        wmsi__onw = data.ctypes
        fgwxc__hinkf = hncg__bit
        if rank == root:
            fgwxc__hinkf = hfw__ixnl.shape
        fgwxc__hinkf = bcast_tuple(fgwxc__hinkf, root)
        gumu__ekm = get_tuple_prod(fgwxc__hinkf[1:])
        send_counts = fgwxc__hinkf[0] * gumu__ekm
        dqj__pwm = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(wmsi__onw, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(dqj__pwm.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return dqj__pwm.reshape((-1,) + fgwxc__hinkf[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        rync__kecal = MPI.COMM_WORLD
        xljwd__cowi = MPI.Get_processor_name()
        cmbp__mpp = rync__kecal.allgather(xljwd__cowi)
        node_ranks = defaultdict(list)
        for i, kvdm__qmqp in enumerate(cmbp__mpp):
            node_ranks[kvdm__qmqp].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    rync__kecal = MPI.COMM_WORLD
    sgj__veb = rync__kecal.Get_group()
    ecs__ebak = sgj__veb.Incl(comm_ranks)
    hmy__jjhex = rync__kecal.Create_group(ecs__ebak)
    return hmy__jjhex


def get_nodes_first_ranks():
    bbpjb__kbc = get_host_ranks()
    return np.array([jwfk__daky[0] for jwfk__daky in bbpjb__kbc.values()],
        dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
