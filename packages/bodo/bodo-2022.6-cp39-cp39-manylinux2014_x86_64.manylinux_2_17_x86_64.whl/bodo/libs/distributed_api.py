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
    pgl__mcsgg = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, pgl__mcsgg, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    pgl__mcsgg = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, pgl__mcsgg, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            pgl__mcsgg = get_type_enum(arr)
            return _isend(arr.ctypes, size, pgl__mcsgg, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        pgl__mcsgg = np.int32(numba_to_c_type(arr.dtype))
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            ehdz__syb = size + 7 >> 3
            vsae__fou = _isend(arr._data.ctypes, size, pgl__mcsgg, pe, tag,
                cond)
            oax__mef = _isend(arr._null_bitmap.ctypes, ehdz__syb,
                afg__dilxh, pe, tag, cond)
            return vsae__fou, oax__mef
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        bmhm__jpj = np.int32(numba_to_c_type(offset_type))
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            llx__jtg = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(llx__jtg, pe, tag - 1)
            ehdz__syb = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                bmhm__jpj, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), llx__jtg,
                afg__dilxh, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr), ehdz__syb,
                afg__dilxh, pe, tag)
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
            pgl__mcsgg = get_type_enum(arr)
            return _irecv(arr.ctypes, size, pgl__mcsgg, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        pgl__mcsgg = np.int32(numba_to_c_type(arr.dtype))
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            ehdz__syb = size + 7 >> 3
            vsae__fou = _irecv(arr._data.ctypes, size, pgl__mcsgg, pe, tag,
                cond)
            oax__mef = _irecv(arr._null_bitmap.ctypes, ehdz__syb,
                afg__dilxh, pe, tag, cond)
            return vsae__fou, oax__mef
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        bmhm__jpj = np.int32(numba_to_c_type(offset_type))
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            dezxe__izf = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            dezxe__izf = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        wizr__wabb = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {dezxe__izf}(size, n_chars)
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
        qitui__fgcjs = dict()
        exec(wizr__wabb, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            bmhm__jpj, 'char_typ_enum': afg__dilxh}, qitui__fgcjs)
        impl = qitui__fgcjs['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    pgl__mcsgg = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), pgl__mcsgg)


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
        yax__byqjj = n_pes if rank == root or allgather else 0
        xnle__agw = np.empty(yax__byqjj, dtype)
        c_gather_scalar(send.ctypes, xnle__agw.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return xnle__agw
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
        vfb__dqriq = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], vfb__dqriq)
        return builder.bitcast(vfb__dqriq, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        vfb__dqriq = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(vfb__dqriq)
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
    ioxl__uugb = types.unliteral(value)
    if isinstance(ioxl__uugb, IndexValueType):
        ioxl__uugb = ioxl__uugb.val_typ
        wzj__viwn = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            wzj__viwn.append(types.int64)
            wzj__viwn.append(bodo.datetime64ns)
            wzj__viwn.append(bodo.timedelta64ns)
            wzj__viwn.append(bodo.datetime_date_type)
        if ioxl__uugb not in wzj__viwn:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(ioxl__uugb))
    typ_enum = np.int32(numba_to_c_type(ioxl__uugb))

    def impl(value, reduce_op):
        ujf__pex = value_to_ptr(value)
        tobe__tik = value_to_ptr(value)
        _dist_reduce(ujf__pex, tobe__tik, reduce_op, typ_enum)
        return load_val_ptr(tobe__tik, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    ioxl__uugb = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(ioxl__uugb))
    lawqr__qtv = ioxl__uugb(0)

    def impl(value, reduce_op):
        ujf__pex = value_to_ptr(value)
        tobe__tik = value_to_ptr(lawqr__qtv)
        _dist_exscan(ujf__pex, tobe__tik, reduce_op, typ_enum)
        return load_val_ptr(tobe__tik, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    epjc__ewovt = 0
    wsp__oud = 0
    for i in range(len(recv_counts)):
        evrob__sqm = recv_counts[i]
        ehdz__syb = recv_counts_nulls[i]
        jehja__crtc = tmp_null_bytes[epjc__ewovt:epjc__ewovt + ehdz__syb]
        for ezzs__kiiov in range(evrob__sqm):
            set_bit_to(null_bitmap_ptr, wsp__oud, get_bit(jehja__crtc,
                ezzs__kiiov))
            wsp__oud += 1
        epjc__ewovt += ehdz__syb


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            qmmb__hwa = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                qmmb__hwa, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            dihyb__smto = data.size
            recv_counts = gather_scalar(np.int32(dihyb__smto), allgather,
                root=root)
            gywk__ubhl = recv_counts.sum()
            jhjy__mpy = empty_like_type(gywk__ubhl, data)
            cmhhj__rma = np.empty(1, np.int32)
            if rank == root or allgather:
                cmhhj__rma = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(dihyb__smto), jhjy__mpy.ctypes,
                recv_counts.ctypes, cmhhj__rma.ctypes, np.int32(typ_val),
                allgather, np.int32(root))
            return jhjy__mpy.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            jhjy__mpy = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.str_arr_ext.init_str_arr(jhjy__mpy)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            jhjy__mpy = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(jhjy__mpy)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            dihyb__smto = len(data)
            ehdz__syb = dihyb__smto + 7 >> 3
            recv_counts = gather_scalar(np.int32(dihyb__smto), allgather,
                root=root)
            gywk__ubhl = recv_counts.sum()
            jhjy__mpy = empty_like_type(gywk__ubhl, data)
            cmhhj__rma = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            uey__owmv = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                cmhhj__rma = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                uey__owmv = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(dihyb__smto),
                jhjy__mpy._days_data.ctypes, recv_counts.ctypes, cmhhj__rma
                .ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._seconds_data.ctypes, np.int32(dihyb__smto),
                jhjy__mpy._seconds_data.ctypes, recv_counts.ctypes,
                cmhhj__rma.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._microseconds_data.ctypes, np.int32(dihyb__smto),
                jhjy__mpy._microseconds_data.ctypes, recv_counts.ctypes,
                cmhhj__rma.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._null_bitmap.ctypes, np.int32(ehdz__syb),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, uey__owmv.
                ctypes, afg__dilxh, allgather, np.int32(root))
            copy_gathered_null_bytes(jhjy__mpy._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return jhjy__mpy
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            dihyb__smto = len(data)
            ehdz__syb = dihyb__smto + 7 >> 3
            recv_counts = gather_scalar(np.int32(dihyb__smto), allgather,
                root=root)
            gywk__ubhl = recv_counts.sum()
            jhjy__mpy = empty_like_type(gywk__ubhl, data)
            cmhhj__rma = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            uey__owmv = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                cmhhj__rma = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                uey__owmv = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(dihyb__smto), jhjy__mpy.
                _data.ctypes, recv_counts.ctypes, cmhhj__rma.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(ehdz__syb),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, uey__owmv.
                ctypes, afg__dilxh, allgather, np.int32(root))
            copy_gathered_null_bytes(jhjy__mpy._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return jhjy__mpy
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        iwd__xqo = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            uyv__iwehm = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                uyv__iwehm, iwd__xqo)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            mtrha__mhupy = bodo.gatherv(data._left, allgather, warn_if_rep,
                root)
            habuy__ooo = bodo.gatherv(data._right, allgather, warn_if_rep, root
                )
            return bodo.libs.interval_arr_ext.init_interval_array(mtrha__mhupy,
                habuy__ooo)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            oyvku__rqxs = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            edc__wyazo = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                edc__wyazo, oyvku__rqxs)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        mfbrd__lit = np.iinfo(np.int64).max
        lfaja__nip = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            urcnf__knir = data._start
            hqhll__tpudg = data._stop
            if len(data) == 0:
                urcnf__knir = mfbrd__lit
                hqhll__tpudg = lfaja__nip
            urcnf__knir = bodo.libs.distributed_api.dist_reduce(urcnf__knir,
                np.int32(Reduce_Type.Min.value))
            hqhll__tpudg = bodo.libs.distributed_api.dist_reduce(hqhll__tpudg,
                np.int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if urcnf__knir == mfbrd__lit and hqhll__tpudg == lfaja__nip:
                urcnf__knir = 0
                hqhll__tpudg = 0
            fdwaf__div = max(0, -(-(hqhll__tpudg - urcnf__knir) // data._step))
            if fdwaf__div < total_len:
                hqhll__tpudg = urcnf__knir + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                urcnf__knir = 0
                hqhll__tpudg = 0
            return bodo.hiframes.pd_index_ext.init_range_index(urcnf__knir,
                hqhll__tpudg, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            isfv__ckn = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, isfv__ckn)
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
            jhjy__mpy = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(jhjy__mpy,
                data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        hlirt__anke = {'bodo': bodo, 'get_table_block': bodo.hiframes.table
            .get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        wizr__wabb = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        wizr__wabb += '  T = data\n'
        wizr__wabb += '  T2 = init_table(T, True)\n'
        for lket__etqc in data.type_to_blk.values():
            hlirt__anke[f'arr_inds_{lket__etqc}'] = np.array(data.
                block_to_arr_ind[lket__etqc], dtype=np.int64)
            wizr__wabb += (
                f'  arr_list_{lket__etqc} = get_table_block(T, {lket__etqc})\n'
                )
            wizr__wabb += f"""  out_arr_list_{lket__etqc} = alloc_list_like(arr_list_{lket__etqc}, len(arr_list_{lket__etqc}), True)
"""
            wizr__wabb += f'  for i in range(len(arr_list_{lket__etqc})):\n'
            wizr__wabb += (
                f'    arr_ind_{lket__etqc} = arr_inds_{lket__etqc}[i]\n')
            wizr__wabb += f"""    ensure_column_unboxed(T, arr_list_{lket__etqc}, i, arr_ind_{lket__etqc})
"""
            wizr__wabb += f"""    out_arr_{lket__etqc} = bodo.gatherv(arr_list_{lket__etqc}[i], allgather, warn_if_rep, root)
"""
            wizr__wabb += (
                f'    out_arr_list_{lket__etqc}[i] = out_arr_{lket__etqc}\n')
            wizr__wabb += (
                f'  T2 = set_table_block(T2, out_arr_list_{lket__etqc}, {lket__etqc})\n'
                )
        wizr__wabb += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        wizr__wabb += f'  T2 = set_table_len(T2, length)\n'
        wizr__wabb += f'  return T2\n'
        qitui__fgcjs = {}
        exec(wizr__wabb, hlirt__anke, qitui__fgcjs)
        dsl__cojy = qitui__fgcjs['impl_table']
        return dsl__cojy
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        qafb__hrwgq = len(data.columns)
        if qafb__hrwgq == 0:
            kvo__ajga = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                tsoq__lpyls = bodo.gatherv(index, allgather, warn_if_rep, root)
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    tsoq__lpyls, kvo__ajga)
            return impl
        ujt__hrcl = ', '.join(f'g_data_{i}' for i in range(qafb__hrwgq))
        wizr__wabb = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            bqo__oofb = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            ujt__hrcl = 'T2'
            wizr__wabb += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            wizr__wabb += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(qafb__hrwgq):
                wizr__wabb += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                wizr__wabb += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        wizr__wabb += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        wizr__wabb += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        wizr__wabb += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(ujt__hrcl))
        qitui__fgcjs = {}
        hlirt__anke = {'bodo': bodo,
            '__col_name_meta_value_gatherv_with_cols': ColNamesMetaType(
            data.columns)}
        exec(wizr__wabb, hlirt__anke, qitui__fgcjs)
        igazq__hpfa = qitui__fgcjs['impl_df']
        return igazq__hpfa
    if isinstance(data, ArrayItemArrayType):
        znq__pcyue = np.int32(numba_to_c_type(types.int32))
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            rrjja__wvr = bodo.libs.array_item_arr_ext.get_offsets(data)
            fiuxi__kcsb = bodo.libs.array_item_arr_ext.get_data(data)
            fiuxi__kcsb = fiuxi__kcsb[:rrjja__wvr[-1]]
            urpz__rde = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            dihyb__smto = len(data)
            owdqq__kmg = np.empty(dihyb__smto, np.uint32)
            ehdz__syb = dihyb__smto + 7 >> 3
            for i in range(dihyb__smto):
                owdqq__kmg[i] = rrjja__wvr[i + 1] - rrjja__wvr[i]
            recv_counts = gather_scalar(np.int32(dihyb__smto), allgather,
                root=root)
            gywk__ubhl = recv_counts.sum()
            cmhhj__rma = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            uey__owmv = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                cmhhj__rma = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for citpu__kucq in range(len(recv_counts)):
                    recv_counts_nulls[citpu__kucq] = recv_counts[citpu__kucq
                        ] + 7 >> 3
                uey__owmv = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            vtmbi__ajxf = np.empty(gywk__ubhl + 1, np.uint32)
            cfuv__mouq = bodo.gatherv(fiuxi__kcsb, allgather, warn_if_rep, root
                )
            ieec__fzirg = np.empty(gywk__ubhl + 7 >> 3, np.uint8)
            c_gatherv(owdqq__kmg.ctypes, np.int32(dihyb__smto), vtmbi__ajxf
                .ctypes, recv_counts.ctypes, cmhhj__rma.ctypes, znq__pcyue,
                allgather, np.int32(root))
            c_gatherv(urpz__rde.ctypes, np.int32(ehdz__syb), tmp_null_bytes
                .ctypes, recv_counts_nulls.ctypes, uey__owmv.ctypes,
                afg__dilxh, allgather, np.int32(root))
            dummy_use(data)
            xfxpe__ciult = np.empty(gywk__ubhl + 1, np.uint64)
            convert_len_arr_to_offset(vtmbi__ajxf.ctypes, xfxpe__ciult.
                ctypes, gywk__ubhl)
            copy_gathered_null_bytes(ieec__fzirg.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                gywk__ubhl, cfuv__mouq, xfxpe__ciult, ieec__fzirg)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        kkhs__qlimx = data.names
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            fkv__fnpzg = bodo.libs.struct_arr_ext.get_data(data)
            pjv__zng = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            wul__lbvb = bodo.gatherv(fkv__fnpzg, allgather=allgather, root=root
                )
            rank = bodo.libs.distributed_api.get_rank()
            dihyb__smto = len(data)
            ehdz__syb = dihyb__smto + 7 >> 3
            recv_counts = gather_scalar(np.int32(dihyb__smto), allgather,
                root=root)
            gywk__ubhl = recv_counts.sum()
            paf__yoi = np.empty(gywk__ubhl + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            uey__owmv = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                uey__owmv = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(pjv__zng.ctypes, np.int32(ehdz__syb), tmp_null_bytes.
                ctypes, recv_counts_nulls.ctypes, uey__owmv.ctypes,
                afg__dilxh, allgather, np.int32(root))
            copy_gathered_null_bytes(paf__yoi.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(wul__lbvb,
                paf__yoi, kkhs__qlimx)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            jhjy__mpy = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(jhjy__mpy)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            jhjy__mpy = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(jhjy__mpy)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            jhjy__mpy = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.map_arr_ext.init_map_arr(jhjy__mpy)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            jhjy__mpy = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            xqiw__wrzpe = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            foz__msqw = bodo.gatherv(data.indptr, allgather, warn_if_rep, root)
            hpr__zqtcr = gather_scalar(data.shape[0], allgather, root=root)
            ebd__zwsc = hpr__zqtcr.sum()
            qafb__hrwgq = bodo.libs.distributed_api.dist_reduce(data.shape[
                1], np.int32(Reduce_Type.Max.value))
            loce__cfkrr = np.empty(ebd__zwsc + 1, np.int64)
            xqiw__wrzpe = xqiw__wrzpe.astype(np.int64)
            loce__cfkrr[0] = 0
            lqxd__dufx = 1
            culv__pmyji = 0
            for rbu__wzhz in hpr__zqtcr:
                for pgi__bfm in range(rbu__wzhz):
                    lqpx__dqhbh = foz__msqw[culv__pmyji + 1] - foz__msqw[
                        culv__pmyji]
                    loce__cfkrr[lqxd__dufx] = loce__cfkrr[lqxd__dufx - 1
                        ] + lqpx__dqhbh
                    lqxd__dufx += 1
                    culv__pmyji += 1
                culv__pmyji += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(jhjy__mpy,
                xqiw__wrzpe, loce__cfkrr, (ebd__zwsc, qafb__hrwgq))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        wizr__wabb = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        wizr__wabb += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        qitui__fgcjs = {}
        exec(wizr__wabb, {'bodo': bodo}, qitui__fgcjs)
        tdz__urxw = qitui__fgcjs['impl_tuple']
        return tdz__urxw
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    wizr__wabb = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    wizr__wabb += '    if random:\n'
    wizr__wabb += '        if random_seed is None:\n'
    wizr__wabb += '            random = 1\n'
    wizr__wabb += '        else:\n'
    wizr__wabb += '            random = 2\n'
    wizr__wabb += '    if random_seed is None:\n'
    wizr__wabb += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        mlgy__zfdv = data
        qafb__hrwgq = len(mlgy__zfdv.columns)
        for i in range(qafb__hrwgq):
            wizr__wabb += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        wizr__wabb += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        ujt__hrcl = ', '.join(f'data_{i}' for i in range(qafb__hrwgq))
        wizr__wabb += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(hgf__fxehf) for
            hgf__fxehf in range(qafb__hrwgq))))
        wizr__wabb += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        wizr__wabb += '    if dests is None:\n'
        wizr__wabb += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        wizr__wabb += '    else:\n'
        wizr__wabb += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for ijnb__gpsfm in range(qafb__hrwgq):
            wizr__wabb += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(ijnb__gpsfm))
        wizr__wabb += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(qafb__hrwgq))
        wizr__wabb += '    delete_table(out_table)\n'
        wizr__wabb += '    if parallel:\n'
        wizr__wabb += '        delete_table(table_total)\n'
        ujt__hrcl = ', '.join('out_arr_{}'.format(i) for i in range(
            qafb__hrwgq))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        wizr__wabb += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(ujt__hrcl, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        wizr__wabb += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        wizr__wabb += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        wizr__wabb += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        wizr__wabb += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        wizr__wabb += '    if dests is None:\n'
        wizr__wabb += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        wizr__wabb += '    else:\n'
        wizr__wabb += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        wizr__wabb += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        wizr__wabb += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        wizr__wabb += '    delete_table(out_table)\n'
        wizr__wabb += '    if parallel:\n'
        wizr__wabb += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        wizr__wabb += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        wizr__wabb += '    if not parallel:\n'
        wizr__wabb += '        return data\n'
        wizr__wabb += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        wizr__wabb += '    if dests is None:\n'
        wizr__wabb += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        wizr__wabb += '    elif bodo.get_rank() not in dests:\n'
        wizr__wabb += '        dim0_local_size = 0\n'
        wizr__wabb += '    else:\n'
        wizr__wabb += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        wizr__wabb += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        wizr__wabb += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        wizr__wabb += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        wizr__wabb += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        wizr__wabb += '    if dests is None:\n'
        wizr__wabb += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        wizr__wabb += '    else:\n'
        wizr__wabb += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        wizr__wabb += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        wizr__wabb += '    delete_table(out_table)\n'
        wizr__wabb += '    if parallel:\n'
        wizr__wabb += '        delete_table(table_total)\n'
        wizr__wabb += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    qitui__fgcjs = {}
    hlirt__anke = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.array
        .array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        hlirt__anke.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(mlgy__zfdv.columns)})
    exec(wizr__wabb, hlirt__anke, qitui__fgcjs)
    impl = qitui__fgcjs['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    wizr__wabb = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        wizr__wabb += '    if seed is None:\n'
        wizr__wabb += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        wizr__wabb += '    np.random.seed(seed)\n'
        wizr__wabb += '    if not parallel:\n'
        wizr__wabb += '        data = data.copy()\n'
        wizr__wabb += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            wizr__wabb += '        data = data[:n_samples]\n'
        wizr__wabb += '        return data\n'
        wizr__wabb += '    else:\n'
        wizr__wabb += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        wizr__wabb += '        permutation = np.arange(dim0_global_size)\n'
        wizr__wabb += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            wizr__wabb += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            wizr__wabb += '        n_samples = dim0_global_size\n'
        wizr__wabb += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        wizr__wabb += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        wizr__wabb += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        wizr__wabb += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        wizr__wabb += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        wizr__wabb += '        return output\n'
    else:
        wizr__wabb += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            wizr__wabb += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            wizr__wabb += '    output = output[:local_n_samples]\n'
        wizr__wabb += '    return output\n'
    qitui__fgcjs = {}
    exec(wizr__wabb, {'np': np, 'bodo': bodo}, qitui__fgcjs)
    impl = qitui__fgcjs['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    mfq__hgman = np.empty(sendcounts_nulls.sum(), np.uint8)
    epjc__ewovt = 0
    wsp__oud = 0
    for eat__pzr in range(len(sendcounts)):
        evrob__sqm = sendcounts[eat__pzr]
        ehdz__syb = sendcounts_nulls[eat__pzr]
        jehja__crtc = mfq__hgman[epjc__ewovt:epjc__ewovt + ehdz__syb]
        for ezzs__kiiov in range(evrob__sqm):
            set_bit_to_arr(jehja__crtc, ezzs__kiiov, get_bit_bitmap(
                null_bitmap_ptr, wsp__oud))
            wsp__oud += 1
        epjc__ewovt += ehdz__syb
    return mfq__hgman


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    pmjn__fxww = MPI.COMM_WORLD
    data = pmjn__fxww.bcast(data, root)
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
    gmlz__rbd = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    iuur__zxbz = (0,) * gmlz__rbd

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        bmxo__bkt = np.ascontiguousarray(data)
        yljkj__ytqct = data.ctypes
        jct__lodb = iuur__zxbz
        if rank == MPI_ROOT:
            jct__lodb = bmxo__bkt.shape
        jct__lodb = bcast_tuple(jct__lodb)
        gly__ctsj = get_tuple_prod(jct__lodb[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            jct__lodb[0])
        send_counts *= gly__ctsj
        dihyb__smto = send_counts[rank]
        hfm__kvsnx = np.empty(dihyb__smto, dtype)
        cmhhj__rma = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(yljkj__ytqct, send_counts.ctypes, cmhhj__rma.ctypes,
            hfm__kvsnx.ctypes, np.int32(dihyb__smto), np.int32(typ_val))
        return hfm__kvsnx.reshape((-1,) + jct__lodb[1:])
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
        bpux__hyj = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], bpux__hyj)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        oyvku__rqxs = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=oyvku__rqxs)
        rizn__ehdso = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(rizn__ehdso)
        return pd.Index(arr, name=oyvku__rqxs)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        oyvku__rqxs = _get_name_value_for_type(dtype.name_typ)
        kkhs__qlimx = tuple(_get_name_value_for_type(t) for t in dtype.
            names_typ)
        ycg__jky = tuple(get_value_for_type(t) for t in dtype.array_types)
        ycg__jky = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in ycg__jky)
        val = pd.MultiIndex.from_arrays(ycg__jky, names=kkhs__qlimx)
        val.name = oyvku__rqxs
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        oyvku__rqxs = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=oyvku__rqxs)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ycg__jky = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({oyvku__rqxs: arr for oyvku__rqxs, arr in zip(
            dtype.columns, ycg__jky)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        rizn__ehdso = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(rizn__ehdso[0],
            rizn__ehdso[0])])
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
        znq__pcyue = np.int32(numba_to_c_type(types.int32))
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            dezxe__izf = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            dezxe__izf = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        wizr__wabb = f"""def impl(
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
            recv_arr = {dezxe__izf}(n_loc, n_loc_char)

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
        qitui__fgcjs = dict()
        exec(wizr__wabb, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            znq__pcyue, 'char_typ_enum': afg__dilxh, 'decode_if_dict_array':
            decode_if_dict_array}, qitui__fgcjs)
        impl = qitui__fgcjs['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        znq__pcyue = np.int32(numba_to_c_type(types.int32))
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            vcd__qbwi = bodo.libs.array_item_arr_ext.get_offsets(data)
            jifzz__znl = bodo.libs.array_item_arr_ext.get_data(data)
            jifzz__znl = jifzz__znl[:vcd__qbwi[-1]]
            rtdu__ynls = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            hyraw__jpktr = bcast_scalar(len(data))
            kjnw__nit = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                kjnw__nit[i] = vcd__qbwi[i + 1] - vcd__qbwi[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                hyraw__jpktr)
            cmhhj__rma = bodo.ir.join.calc_disp(send_counts)
            ezbku__ssvg = np.empty(n_pes, np.int32)
            if rank == 0:
                hkxn__zsh = 0
                for i in range(n_pes):
                    eyn__hfom = 0
                    for pgi__bfm in range(send_counts[i]):
                        eyn__hfom += kjnw__nit[hkxn__zsh]
                        hkxn__zsh += 1
                    ezbku__ssvg[i] = eyn__hfom
            bcast(ezbku__ssvg)
            ysd__nofy = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                ysd__nofy[i] = send_counts[i] + 7 >> 3
            uey__owmv = bodo.ir.join.calc_disp(ysd__nofy)
            dihyb__smto = send_counts[rank]
            jba__jalh = np.empty(dihyb__smto + 1, np_offset_type)
            srya__wbkis = bodo.libs.distributed_api.scatterv_impl(jifzz__znl,
                ezbku__ssvg)
            utut__wang = dihyb__smto + 7 >> 3
            cxdve__miyn = np.empty(utut__wang, np.uint8)
            rthha__idx = np.empty(dihyb__smto, np.uint32)
            c_scatterv(kjnw__nit.ctypes, send_counts.ctypes, cmhhj__rma.
                ctypes, rthha__idx.ctypes, np.int32(dihyb__smto), znq__pcyue)
            convert_len_arr_to_offset(rthha__idx.ctypes, jba__jalh.ctypes,
                dihyb__smto)
            mxy__kvh = get_scatter_null_bytes_buff(rtdu__ynls.ctypes,
                send_counts, ysd__nofy)
            c_scatterv(mxy__kvh.ctypes, ysd__nofy.ctypes, uey__owmv.ctypes,
                cxdve__miyn.ctypes, np.int32(utut__wang), afg__dilxh)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                dihyb__smto, srya__wbkis, jba__jalh, cxdve__miyn)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            akxex__xhmnk = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            akxex__xhmnk = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            akxex__xhmnk = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            akxex__xhmnk = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            bmxo__bkt = data._data
            pjv__zng = data._null_bitmap
            nlh__sbez = len(bmxo__bkt)
            psei__broel = _scatterv_np(bmxo__bkt, send_counts)
            hyraw__jpktr = bcast_scalar(nlh__sbez)
            cxwzb__nloz = len(psei__broel) + 7 >> 3
            wtkdi__nnug = np.empty(cxwzb__nloz, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                hyraw__jpktr)
            ysd__nofy = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                ysd__nofy[i] = send_counts[i] + 7 >> 3
            uey__owmv = bodo.ir.join.calc_disp(ysd__nofy)
            mxy__kvh = get_scatter_null_bytes_buff(pjv__zng.ctypes,
                send_counts, ysd__nofy)
            c_scatterv(mxy__kvh.ctypes, ysd__nofy.ctypes, uey__owmv.ctypes,
                wtkdi__nnug.ctypes, np.int32(cxwzb__nloz), afg__dilxh)
            return akxex__xhmnk(psei__broel, wtkdi__nnug)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            ehs__kcuzc = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            iewc__wqa = bodo.libs.distributed_api.scatterv_impl(data._right,
                send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(ehs__kcuzc,
                iewc__wqa)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            urcnf__knir = data._start
            hqhll__tpudg = data._stop
            cjf__ldc = data._step
            oyvku__rqxs = data._name
            oyvku__rqxs = bcast_scalar(oyvku__rqxs)
            urcnf__knir = bcast_scalar(urcnf__knir)
            hqhll__tpudg = bcast_scalar(hqhll__tpudg)
            cjf__ldc = bcast_scalar(cjf__ldc)
            ljgil__butb = bodo.libs.array_kernels.calc_nitems(urcnf__knir,
                hqhll__tpudg, cjf__ldc)
            chunk_start = bodo.libs.distributed_api.get_start(ljgil__butb,
                n_pes, rank)
            jkje__bauys = bodo.libs.distributed_api.get_node_portion(
                ljgil__butb, n_pes, rank)
            xnb__lbq = urcnf__knir + cjf__ldc * chunk_start
            bap__kypw = urcnf__knir + cjf__ldc * (chunk_start + jkje__bauys)
            bap__kypw = min(bap__kypw, hqhll__tpudg)
            return bodo.hiframes.pd_index_ext.init_range_index(xnb__lbq,
                bap__kypw, cjf__ldc, oyvku__rqxs)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        isfv__ckn = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            bmxo__bkt = data._data
            oyvku__rqxs = data._name
            oyvku__rqxs = bcast_scalar(oyvku__rqxs)
            arr = bodo.libs.distributed_api.scatterv_impl(bmxo__bkt,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                oyvku__rqxs, isfv__ckn)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            bmxo__bkt = data._data
            oyvku__rqxs = data._name
            oyvku__rqxs = bcast_scalar(oyvku__rqxs)
            arr = bodo.libs.distributed_api.scatterv_impl(bmxo__bkt,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, oyvku__rqxs)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            jhjy__mpy = bodo.libs.distributed_api.scatterv_impl(data._data,
                send_counts)
            oyvku__rqxs = bcast_scalar(data._name)
            kkhs__qlimx = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(jhjy__mpy,
                kkhs__qlimx, oyvku__rqxs)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            oyvku__rqxs = bodo.hiframes.pd_series_ext.get_series_name(data)
            mswz__egu = bcast_scalar(oyvku__rqxs)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            edc__wyazo = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                edc__wyazo, mswz__egu)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        qafb__hrwgq = len(data.columns)
        ujt__hrcl = ', '.join('g_data_{}'.format(i) for i in range(qafb__hrwgq)
            )
        vshf__tbx = ColNamesMetaType(data.columns)
        wizr__wabb = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        for i in range(qafb__hrwgq):
            wizr__wabb += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            wizr__wabb += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        wizr__wabb += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        wizr__wabb += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        wizr__wabb += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({ujt__hrcl},), g_index, __col_name_meta_scaterv_impl)
"""
        qitui__fgcjs = {}
        exec(wizr__wabb, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            vshf__tbx}, qitui__fgcjs)
        igazq__hpfa = qitui__fgcjs['impl_df']
        return igazq__hpfa
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            qmmb__hwa = bodo.libs.distributed_api.scatterv_impl(data.codes,
                send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                qmmb__hwa, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        wizr__wabb = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        wizr__wabb += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        qitui__fgcjs = {}
        exec(wizr__wabb, {'bodo': bodo}, qitui__fgcjs)
        tdz__urxw = qitui__fgcjs['impl_tuple']
        return tdz__urxw
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
        bmhm__jpj = np.int32(numba_to_c_type(offset_type))
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            dihyb__smto = len(data)
            jsukq__qhxmk = num_total_chars(data)
            assert dihyb__smto < INT_MAX
            assert jsukq__qhxmk < INT_MAX
            efpo__biipn = get_offset_ptr(data)
            yljkj__ytqct = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            ehdz__syb = dihyb__smto + 7 >> 3
            c_bcast(efpo__biipn, np.int32(dihyb__smto + 1), bmhm__jpj, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(yljkj__ytqct, np.int32(jsukq__qhxmk), afg__dilxh, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(ehdz__syb), afg__dilxh, np.
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
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                wdr__syrzj = 0
                aggv__abz = np.empty(0, np.uint8).ctypes
            else:
                aggv__abz, wdr__syrzj = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            wdr__syrzj = bodo.libs.distributed_api.bcast_scalar(wdr__syrzj,
                root)
            if rank != root:
                uat__gyms = np.empty(wdr__syrzj + 1, np.uint8)
                uat__gyms[wdr__syrzj] = 0
                aggv__abz = uat__gyms.ctypes
            c_bcast(aggv__abz, np.int32(wdr__syrzj), afg__dilxh, np.array([
                -1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(aggv__abz, wdr__syrzj)
        return impl_str
    typ_val = numba_to_c_type(val)
    wizr__wabb = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    qitui__fgcjs = {}
    exec(wizr__wabb, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, qitui__fgcjs)
    jxw__pfxmp = qitui__fgcjs['bcast_scalar_impl']
    return jxw__pfxmp


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    kiocn__oqa = len(val)
    wizr__wabb = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    wizr__wabb += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(kiocn__oqa)),
        ',' if kiocn__oqa else '')
    qitui__fgcjs = {}
    exec(wizr__wabb, {'bcast_scalar': bcast_scalar}, qitui__fgcjs)
    axw__des = qitui__fgcjs['bcast_tuple_impl']
    return axw__des


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            dihyb__smto = bcast_scalar(len(arr), root)
            tmj__qbmk = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(dihyb__smto, tmj__qbmk)
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
            xnb__lbq = max(arr_start, slice_index.start) - arr_start
            bap__kypw = max(slice_index.stop - arr_start, 0)
            return slice(xnb__lbq, bap__kypw)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            urcnf__knir = slice_index.start
            cjf__ldc = slice_index.step
            qjot__baf = 0 if cjf__ldc == 1 or urcnf__knir > arr_start else abs(
                cjf__ldc - arr_start % cjf__ldc) % cjf__ldc
            xnb__lbq = max(arr_start, slice_index.start
                ) - arr_start + qjot__baf
            bap__kypw = max(slice_index.stop - arr_start, 0)
            return slice(xnb__lbq, bap__kypw, cjf__ldc)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        oxcmv__hgmj = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[oxcmv__hgmj])
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
        gauu__hxbwd = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        afg__dilxh = np.int32(numba_to_c_type(types.uint8))
        ipj__gvs = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            rour__kbkto = np.int32(10)
            tag = np.int32(11)
            djy__qmnu = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                fiuxi__kcsb = arr._data
                tlj__mjnog = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    fiuxi__kcsb, ind)
                xxm__axw = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    fiuxi__kcsb, ind + 1)
                length = xxm__axw - tlj__mjnog
                vfb__dqriq = fiuxi__kcsb[ind]
                djy__qmnu[0] = length
                isend(djy__qmnu, np.int32(1), root, rour__kbkto, True)
                isend(vfb__dqriq, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(ipj__gvs,
                gauu__hxbwd, 0, 1)
            fdwaf__div = 0
            if rank == root:
                fdwaf__div = recv(np.int64, ANY_SOURCE, rour__kbkto)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    ipj__gvs, gauu__hxbwd, fdwaf__div, 1)
                yljkj__ytqct = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(yljkj__ytqct, np.int32(fdwaf__div), afg__dilxh,
                    ANY_SOURCE, tag)
            dummy_use(djy__qmnu)
            fdwaf__div = bcast_scalar(fdwaf__div)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    ipj__gvs, gauu__hxbwd, fdwaf__div, 1)
            yljkj__ytqct = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(yljkj__ytqct, np.int32(fdwaf__div), afg__dilxh, np.
                array([-1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, fdwaf__div)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        yex__pmi = bodo.hiframes.pd_categorical_ext.get_categories_int_type(arr
            .dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, yex__pmi)
            if arr_start <= ind < arr_start + len(arr):
                qmmb__hwa = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = qmmb__hwa[ind - arr_start]
                send_arr = np.full(1, data, yex__pmi)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = yex__pmi(-1)
            if rank == root:
                val = recv(yex__pmi, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            whcrv__vqfjw = arr.dtype.categories[max(val, 0)]
            return whcrv__vqfjw
        return cat_getitem_impl
    asern__jygp = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, asern__jygp)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, asern__jygp)[0]
        if rank == root:
            val = recv(asern__jygp, ANY_SOURCE, tag)
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
    mmd__wqa = get_type_enum(out_data)
    assert typ_enum == mmd__wqa
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
    wizr__wabb = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        wizr__wabb += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    wizr__wabb += '  return\n'
    qitui__fgcjs = {}
    exec(wizr__wabb, {'alltoallv': alltoallv}, qitui__fgcjs)
    tdme__odbgk = qitui__fgcjs['f']
    return tdme__odbgk


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    urcnf__knir = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return urcnf__knir, count


@numba.njit
def get_start(total_size, pes, rank):
    xnle__agw = total_size % pes
    sss__exhz = (total_size - xnle__agw) // pes
    return rank * sss__exhz + min(rank, xnle__agw)


@numba.njit
def get_end(total_size, pes, rank):
    xnle__agw = total_size % pes
    sss__exhz = (total_size - xnle__agw) // pes
    return (rank + 1) * sss__exhz + min(rank + 1, xnle__agw)


@numba.njit
def get_node_portion(total_size, pes, rank):
    xnle__agw = total_size % pes
    sss__exhz = (total_size - xnle__agw) // pes
    if rank < xnle__agw:
        return sss__exhz + 1
    else:
        return sss__exhz


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    lawqr__qtv = in_arr.dtype(0)
    hilce__lhsv = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        eyn__hfom = lawqr__qtv
        for ncb__nasfs in np.nditer(in_arr):
            eyn__hfom += ncb__nasfs.item()
        uwwzu__xzy = dist_exscan(eyn__hfom, hilce__lhsv)
        for i in range(in_arr.size):
            uwwzu__xzy += in_arr[i]
            out_arr[i] = uwwzu__xzy
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    bnd__khfir = in_arr.dtype(1)
    hilce__lhsv = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        eyn__hfom = bnd__khfir
        for ncb__nasfs in np.nditer(in_arr):
            eyn__hfom *= ncb__nasfs.item()
        uwwzu__xzy = dist_exscan(eyn__hfom, hilce__lhsv)
        if get_rank() == 0:
            uwwzu__xzy = bnd__khfir
        for i in range(in_arr.size):
            uwwzu__xzy *= in_arr[i]
            out_arr[i] = uwwzu__xzy
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        bnd__khfir = np.finfo(in_arr.dtype(1).dtype).max
    else:
        bnd__khfir = np.iinfo(in_arr.dtype(1).dtype).max
    hilce__lhsv = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        eyn__hfom = bnd__khfir
        for ncb__nasfs in np.nditer(in_arr):
            eyn__hfom = min(eyn__hfom, ncb__nasfs.item())
        uwwzu__xzy = dist_exscan(eyn__hfom, hilce__lhsv)
        if get_rank() == 0:
            uwwzu__xzy = bnd__khfir
        for i in range(in_arr.size):
            uwwzu__xzy = min(uwwzu__xzy, in_arr[i])
            out_arr[i] = uwwzu__xzy
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        bnd__khfir = np.finfo(in_arr.dtype(1).dtype).min
    else:
        bnd__khfir = np.iinfo(in_arr.dtype(1).dtype).min
    bnd__khfir = in_arr.dtype(1)
    hilce__lhsv = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        eyn__hfom = bnd__khfir
        for ncb__nasfs in np.nditer(in_arr):
            eyn__hfom = max(eyn__hfom, ncb__nasfs.item())
        uwwzu__xzy = dist_exscan(eyn__hfom, hilce__lhsv)
        if get_rank() == 0:
            uwwzu__xzy = bnd__khfir
        for i in range(in_arr.size):
            uwwzu__xzy = max(uwwzu__xzy, in_arr[i])
            out_arr[i] = uwwzu__xzy
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    pgl__mcsgg = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), pgl__mcsgg)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    ryg__fwqoy = args[0]
    if equiv_set.has_shape(ryg__fwqoy):
        return ArrayAnalysis.AnalyzeResult(shape=ryg__fwqoy, pre=[])
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
    djud__pqfir = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for
        i, ejjp__oiqc in enumerate(args) if is_array_typ(ejjp__oiqc) or
        isinstance(ejjp__oiqc, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    wizr__wabb = f"""def impl(*args):
    if {djud__pqfir} or bodo.get_rank() == 0:
        print(*args)"""
    qitui__fgcjs = {}
    exec(wizr__wabb, globals(), qitui__fgcjs)
    impl = qitui__fgcjs['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        dvuxq__wbn = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        wizr__wabb = 'def f(req, cond=True):\n'
        wizr__wabb += f'  return {dvuxq__wbn}\n'
        qitui__fgcjs = {}
        exec(wizr__wabb, {'_wait': _wait}, qitui__fgcjs)
        impl = qitui__fgcjs['f']
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
        xnle__agw = 1
        for a in t:
            xnle__agw *= a
        return xnle__agw
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    jlxx__kimy = np.ascontiguousarray(in_arr)
    hea__uwkm = get_tuple_prod(jlxx__kimy.shape[1:])
    vilj__hvn = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        yju__cirej = np.array(dest_ranks, dtype=np.int32)
    else:
        yju__cirej = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, jlxx__kimy.ctypes, new_dim0_global_len,
        len(in_arr), dtype_size * vilj__hvn, dtype_size * hea__uwkm, len(
        yju__cirej), yju__cirej.ctypes)
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
    cyk__uxfm = np.ascontiguousarray(rhs)
    uke__yqme = get_tuple_prod(cyk__uxfm.shape[1:])
    zig__wnss = dtype_size * uke__yqme
    permutation_array_index(lhs.ctypes, lhs_len, zig__wnss, cyk__uxfm.
        ctypes, cyk__uxfm.shape[0], p.ctypes, p_len, n_samples)
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
        wizr__wabb = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        qitui__fgcjs = {}
        exec(wizr__wabb, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, qitui__fgcjs)
        jxw__pfxmp = qitui__fgcjs['bcast_scalar_impl']
        return jxw__pfxmp
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        qafb__hrwgq = len(data.columns)
        ujt__hrcl = ', '.join('g_data_{}'.format(i) for i in range(qafb__hrwgq)
            )
        aye__ghpac = ColNamesMetaType(data.columns)
        wizr__wabb = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(qafb__hrwgq):
            wizr__wabb += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            wizr__wabb += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        wizr__wabb += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        wizr__wabb += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        wizr__wabb += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_bcast_comm)
"""
            .format(ujt__hrcl))
        qitui__fgcjs = {}
        exec(wizr__wabb, {'bodo': bodo, '__col_name_meta_value_bcast_comm':
            aye__ghpac}, qitui__fgcjs)
        igazq__hpfa = qitui__fgcjs['impl_df']
        return igazq__hpfa
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            urcnf__knir = data._start
            hqhll__tpudg = data._stop
            cjf__ldc = data._step
            oyvku__rqxs = data._name
            oyvku__rqxs = bcast_scalar(oyvku__rqxs, root)
            urcnf__knir = bcast_scalar(urcnf__knir, root)
            hqhll__tpudg = bcast_scalar(hqhll__tpudg, root)
            cjf__ldc = bcast_scalar(cjf__ldc, root)
            ljgil__butb = bodo.libs.array_kernels.calc_nitems(urcnf__knir,
                hqhll__tpudg, cjf__ldc)
            chunk_start = bodo.libs.distributed_api.get_start(ljgil__butb,
                n_pes, rank)
            jkje__bauys = bodo.libs.distributed_api.get_node_portion(
                ljgil__butb, n_pes, rank)
            xnb__lbq = urcnf__knir + cjf__ldc * chunk_start
            bap__kypw = urcnf__knir + cjf__ldc * (chunk_start + jkje__bauys)
            bap__kypw = min(bap__kypw, hqhll__tpudg)
            return bodo.hiframes.pd_index_ext.init_range_index(xnb__lbq,
                bap__kypw, cjf__ldc, oyvku__rqxs)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            bmxo__bkt = data._data
            oyvku__rqxs = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(bmxo__bkt,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, oyvku__rqxs)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            oyvku__rqxs = bodo.hiframes.pd_series_ext.get_series_name(data)
            mswz__egu = bodo.libs.distributed_api.bcast_comm_impl(oyvku__rqxs,
                comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            edc__wyazo = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                edc__wyazo, mswz__egu)
        return impl_series
    if isinstance(data, types.BaseTuple):
        wizr__wabb = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        wizr__wabb += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        qitui__fgcjs = {}
        exec(wizr__wabb, {'bcast_comm_impl': bcast_comm_impl}, qitui__fgcjs)
        tdz__urxw = qitui__fgcjs['impl_tuple']
        return tdz__urxw
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    gmlz__rbd = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    iuur__zxbz = (0,) * gmlz__rbd

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        bmxo__bkt = np.ascontiguousarray(data)
        yljkj__ytqct = data.ctypes
        jct__lodb = iuur__zxbz
        if rank == root:
            jct__lodb = bmxo__bkt.shape
        jct__lodb = bcast_tuple(jct__lodb, root)
        gly__ctsj = get_tuple_prod(jct__lodb[1:])
        send_counts = jct__lodb[0] * gly__ctsj
        hfm__kvsnx = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(yljkj__ytqct, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(hfm__kvsnx.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return hfm__kvsnx.reshape((-1,) + jct__lodb[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        pmjn__fxww = MPI.COMM_WORLD
        gtsw__sicly = MPI.Get_processor_name()
        jve__phhfq = pmjn__fxww.allgather(gtsw__sicly)
        node_ranks = defaultdict(list)
        for i, hheg__anjk in enumerate(jve__phhfq):
            node_ranks[hheg__anjk].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    pmjn__fxww = MPI.COMM_WORLD
    jnxff__fmp = pmjn__fxww.Get_group()
    libw__kgywx = jnxff__fmp.Incl(comm_ranks)
    seei__bzicy = pmjn__fxww.Create_group(libw__kgywx)
    return seei__bzicy


def get_nodes_first_ranks():
    gwf__nytom = get_host_ranks()
    return np.array([cuu__sda[0] for cuu__sda in gwf__nytom.values()],
        dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
