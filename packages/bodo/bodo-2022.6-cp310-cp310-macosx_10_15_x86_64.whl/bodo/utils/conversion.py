"""
Utility functions for conversion of data such as list to array.
Need to be inlined for better optimization.
"""
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.extending import overload
import bodo
from bodo.libs.binary_arr_ext import bytes_type
from bodo.libs.bool_arr_ext import boolean_dtype
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.nullable_tuple_ext import NullableTupleType
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, dtype_to_array_type, get_overload_const_list, get_overload_const_str, is_heterogeneous_tuple_type, is_np_arr_typ, is_overload_constant_list, is_overload_constant_str, is_overload_none, is_overload_true, is_str_arr_type, to_nullable_type
NS_DTYPE = np.dtype('M8[ns]')
TD_DTYPE = np.dtype('m8[ns]')


def coerce_to_ndarray(data, error_on_nonarray=True, use_nullable_array=None,
    scalar_to_arr_len=None):
    return data


@overload(coerce_to_ndarray)
def overload_coerce_to_ndarray(data, error_on_nonarray=True,
    use_nullable_array=None, scalar_to_arr_len=None):
    from bodo.hiframes.pd_index_ext import DatetimeIndexType, NumericIndexType, RangeIndexType, TimedeltaIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    data = types.unliteral(data)
    if isinstance(data, types.Optional) and bodo.utils.typing.is_scalar_type(
        data.type):
        data = data.type
        use_nullable_array = True
    if isinstance(data, bodo.libs.int_arr_ext.IntegerArrayType
        ) and not is_overload_none(use_nullable_array):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.int_arr_ext.
            get_int_arr_data(data))
    if data == bodo.libs.bool_arr_ext.boolean_array and not is_overload_none(
        use_nullable_array):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.bool_arr_ext.
            get_bool_arr_data(data))
    if isinstance(data, types.Array):
        if not is_overload_none(use_nullable_array) and isinstance(data.
            dtype, (types.Boolean, types.Integer)):
            if data.dtype == types.bool_:
                if data.layout != 'C':
                    return (lambda data, error_on_nonarray=True,
                        use_nullable_array=None, scalar_to_arr_len=None:
                        bodo.libs.bool_arr_ext.init_bool_array(np.
                        ascontiguousarray(data), np.full(len(data) + 7 >> 3,
                        255, np.uint8)))
                else:
                    return (lambda data, error_on_nonarray=True,
                        use_nullable_array=None, scalar_to_arr_len=None:
                        bodo.libs.bool_arr_ext.init_bool_array(data, np.
                        full(len(data) + 7 >> 3, 255, np.uint8)))
            elif data.layout != 'C':
                return (lambda data, error_on_nonarray=True,
                    use_nullable_array=None, scalar_to_arr_len=None: bodo.
                    libs.int_arr_ext.init_integer_array(np.
                    ascontiguousarray(data), np.full(len(data) + 7 >> 3, 
                    255, np.uint8)))
            else:
                return (lambda data, error_on_nonarray=True,
                    use_nullable_array=None, scalar_to_arr_len=None: bodo.
                    libs.int_arr_ext.init_integer_array(data, np.full(len(
                    data) + 7 >> 3, 255, np.uint8)))
        if data.layout != 'C':
            return (lambda data, error_on_nonarray=True, use_nullable_array
                =None, scalar_to_arr_len=None: np.ascontiguousarray(data))
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: data)
    if isinstance(data, (types.List, types.UniTuple)):
        evde__odptr = data.dtype
        if isinstance(evde__odptr, types.Optional):
            evde__odptr = evde__odptr.type
            if bodo.utils.typing.is_scalar_type(evde__odptr):
                use_nullable_array = True
        if isinstance(evde__odptr, (types.Boolean, types.Integer,
            Decimal128Type)) or evde__odptr in [bodo.hiframes.
            pd_timestamp_ext.pd_timestamp_type, bodo.hiframes.
            datetime_date_ext.datetime_date_type, bodo.hiframes.
            datetime_timedelta_ext.datetime_timedelta_type]:
            zflu__zdl = dtype_to_array_type(evde__odptr)
            if not is_overload_none(use_nullable_array):
                zflu__zdl = to_nullable_type(zflu__zdl)

            def impl(data, error_on_nonarray=True, use_nullable_array=None,
                scalar_to_arr_len=None):
                kbdch__itmk = len(data)
                A = bodo.utils.utils.alloc_type(kbdch__itmk, zflu__zdl, (-1,))
                bodo.utils.utils.tuple_list_to_array(A, data, evde__odptr)
                return A
            return impl
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.asarray(data))
    if isinstance(data, SeriesType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_series_ext.
            get_series_data(data))
    if isinstance(data, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType)):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_index_ext.
            get_index_data(data))
    if isinstance(data, RangeIndexType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.arange(data._start, data._stop,
            data._step))
    if isinstance(data, types.RangeType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.arange(data.start, data.stop,
            data.step))
    if not is_overload_none(scalar_to_arr_len):
        if isinstance(data, Decimal128Type):
            vfiyw__dkjtk = data.precision
            zaze__znvjk = data.scale

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                kbdch__itmk = scalar_to_arr_len
                A = bodo.libs.decimal_arr_ext.alloc_decimal_array(kbdch__itmk,
                    vfiyw__dkjtk, zaze__znvjk)
                for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    A[dtxpf__hiutb] = data
                return A
            return impl_ts
        if data == bodo.hiframes.datetime_datetime_ext.datetime_datetime_type:
            ewr__gvhhs = np.dtype('datetime64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                kbdch__itmk = scalar_to_arr_len
                A = np.empty(kbdch__itmk, ewr__gvhhs)
                crl__aaqkf = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(data))
                kdvfd__hgd = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                    crl__aaqkf)
                for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    A[dtxpf__hiutb] = kdvfd__hgd
                return A
            return impl_ts
        if (data == bodo.hiframes.datetime_timedelta_ext.
            datetime_timedelta_type):
            abr__ycl = np.dtype('timedelta64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                kbdch__itmk = scalar_to_arr_len
                A = np.empty(kbdch__itmk, abr__ycl)
                rff__iukkp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(data))
                for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    A[dtxpf__hiutb] = rff__iukkp
                return A
            return impl_ts
        if data == bodo.hiframes.datetime_date_ext.datetime_date_type:

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                kbdch__itmk = scalar_to_arr_len
                A = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
                    kbdch__itmk)
                for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    A[dtxpf__hiutb] = data
                return A
            return impl_ts
        if data == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            ewr__gvhhs = np.dtype('datetime64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                kbdch__itmk = scalar_to_arr_len
                A = np.empty(scalar_to_arr_len, ewr__gvhhs)
                crl__aaqkf = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                    data.value)
                for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    A[dtxpf__hiutb] = crl__aaqkf
                return A
            return impl_ts
        dtype = types.unliteral(data)
        if not is_overload_none(use_nullable_array) and isinstance(dtype,
            types.Integer):

            def impl_null_integer(data, error_on_nonarray=True,
                use_nullable_array=None, scalar_to_arr_len=None):
                numba.parfors.parfor.init_prange()
                kbdch__itmk = scalar_to_arr_len
                moh__grvj = bodo.libs.int_arr_ext.alloc_int_array(kbdch__itmk,
                    dtype)
                for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    moh__grvj[dtxpf__hiutb] = data
                return moh__grvj
            return impl_null_integer
        if not is_overload_none(use_nullable_array) and dtype == types.bool_:

            def impl_null_bool(data, error_on_nonarray=True,
                use_nullable_array=None, scalar_to_arr_len=None):
                numba.parfors.parfor.init_prange()
                kbdch__itmk = scalar_to_arr_len
                moh__grvj = bodo.libs.bool_arr_ext.alloc_bool_array(kbdch__itmk
                    )
                for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    moh__grvj[dtxpf__hiutb] = data
                return moh__grvj
            return impl_null_bool

        def impl_num(data, error_on_nonarray=True, use_nullable_array=None,
            scalar_to_arr_len=None):
            numba.parfors.parfor.init_prange()
            kbdch__itmk = scalar_to_arr_len
            moh__grvj = np.empty(kbdch__itmk, dtype)
            for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                kbdch__itmk):
                moh__grvj[dtxpf__hiutb] = data
            return moh__grvj
        return impl_num
    if isinstance(data, types.BaseTuple) and all(isinstance(qqgw__kxinm, (
        types.Float, types.Integer)) for qqgw__kxinm in data.types):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.array(data))
    if bodo.utils.utils.is_array_typ(data, False):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: data)
    if is_overload_true(error_on_nonarray):
        raise BodoError(f'cannot coerce {data} to array')
    return (lambda data, error_on_nonarray=True, use_nullable_array=None,
        scalar_to_arr_len=None: data)


def coerce_to_array(data, error_on_nonarray=True, use_nullable_array=None,
    scalar_to_arr_len=None):
    return data


@overload(coerce_to_array, no_unliteral=True)
def overload_coerce_to_array(data, error_on_nonarray=True,
    use_nullable_array=None, scalar_to_arr_len=None):
    from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, StringIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    data = types.unliteral(data)
    if isinstance(data, types.Optional) and bodo.utils.typing.is_scalar_type(
        data.type):
        data = data.type
        use_nullable_array = True
    if isinstance(data, SeriesType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_series_ext.
            get_series_data(data))
    if isinstance(data, (StringIndexType, BinaryIndexType,
        CategoricalIndexType)):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_index_ext.
            get_index_data(data))
    if isinstance(data, types.List) and data.dtype in (bodo.string_type,
        bodo.bytes_type):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.str_arr_ext.
            str_arr_from_sequence(data))
    if isinstance(data, types.BaseTuple) and data.count == 0:
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.str_arr_ext.
            empty_str_arr(data))
    if isinstance(data, types.UniTuple) and isinstance(data.dtype, (types.
        UnicodeType, types.StringLiteral)) or isinstance(data, types.BaseTuple
        ) and all(isinstance(qqgw__kxinm, types.StringLiteral) for
        qqgw__kxinm in data.types):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.str_arr_ext.
            str_arr_from_sequence(data))
    if data in (bodo.string_array_type, bodo.dict_str_arr_type, bodo.
        binary_array_type, bodo.libs.bool_arr_ext.boolean_array, bodo.
        hiframes.datetime_date_ext.datetime_date_array_type, bodo.hiframes.
        datetime_timedelta_ext.datetime_timedelta_array_type, bodo.hiframes
        .split_impl.string_array_split_view_type) or isinstance(data, (bodo
        .libs.int_arr_ext.IntegerArrayType, DecimalArrayType, bodo.libs.
        interval_arr_ext.IntervalArrayType, bodo.libs.tuple_arr_ext.
        TupleArrayType, bodo.libs.struct_arr_ext.StructArrayType, bodo.
        hiframes.pd_categorical_ext.CategoricalArrayType, bodo.libs.
        csr_matrix_ext.CSRMatrixType, bodo.DatetimeArrayType)):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: data)
    if isinstance(data, (types.List, types.UniTuple)) and isinstance(data.
        dtype, types.BaseTuple):
        ngvnp__qjw = tuple(dtype_to_array_type(qqgw__kxinm) for qqgw__kxinm in
            data.dtype.types)

        def impl_tuple_list(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            kbdch__itmk = len(data)
            arr = bodo.libs.tuple_arr_ext.pre_alloc_tuple_array(kbdch__itmk,
                (-1,), ngvnp__qjw)
            for dtxpf__hiutb in range(kbdch__itmk):
                arr[dtxpf__hiutb] = data[dtxpf__hiutb]
            return arr
        return impl_tuple_list
    if isinstance(data, types.List) and (bodo.utils.utils.is_array_typ(data
        .dtype, False) or isinstance(data.dtype, types.List)):
        jav__vysss = dtype_to_array_type(data.dtype.dtype)

        def impl_array_item_arr(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            kbdch__itmk = len(data)
            nkor__meetd = init_nested_counts(jav__vysss)
            for dtxpf__hiutb in range(kbdch__itmk):
                qmf__pkyr = bodo.utils.conversion.coerce_to_array(data[
                    dtxpf__hiutb], use_nullable_array=True)
                nkor__meetd = add_nested_counts(nkor__meetd, qmf__pkyr)
            moh__grvj = (bodo.libs.array_item_arr_ext.
                pre_alloc_array_item_array(kbdch__itmk, nkor__meetd,
                jav__vysss))
            vpqc__vfgq = bodo.libs.array_item_arr_ext.get_null_bitmap(moh__grvj
                )
            for fnj__vqr in range(kbdch__itmk):
                qmf__pkyr = bodo.utils.conversion.coerce_to_array(data[
                    fnj__vqr], use_nullable_array=True)
                moh__grvj[fnj__vqr] = qmf__pkyr
                bodo.libs.int_arr_ext.set_bit_to_arr(vpqc__vfgq, fnj__vqr, 1)
            return moh__grvj
        return impl_array_item_arr
    if not is_overload_none(scalar_to_arr_len) and isinstance(data, (types.
        UnicodeType, types.StringLiteral)):

        def impl_str(data, error_on_nonarray=True, use_nullable_array=None,
            scalar_to_arr_len=None):
            kbdch__itmk = scalar_to_arr_len
            A = bodo.libs.str_arr_ext.pre_alloc_string_array(kbdch__itmk, -1)
            for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                kbdch__itmk):
                A[dtxpf__hiutb] = data
            return A
        return impl_str
    if isinstance(data, types.List) and isinstance(data.dtype, bodo.
        hiframes.pd_timestamp_ext.PandasTimestampType):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
            'coerce_to_array()')

        def impl_list_timestamp(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            kbdch__itmk = len(data)
            A = np.empty(kbdch__itmk, np.dtype('datetime64[ns]'))
            for dtxpf__hiutb in range(kbdch__itmk):
                A[dtxpf__hiutb
                    ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(data
                    [dtxpf__hiutb].value)
            return A
        return impl_list_timestamp
    if isinstance(data, types.List) and data.dtype == bodo.pd_timedelta_type:

        def impl_list_timedelta(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            kbdch__itmk = len(data)
            A = np.empty(kbdch__itmk, np.dtype('timedelta64[ns]'))
            for dtxpf__hiutb in range(kbdch__itmk):
                A[dtxpf__hiutb
                    ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    data[dtxpf__hiutb].value)
            return A
        return impl_list_timedelta
    if isinstance(data, bodo.hiframes.pd_timestamp_ext.PandasTimestampType):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
            'coerce_to_array()')
    if not is_overload_none(scalar_to_arr_len) and data in [bodo.
        pd_timestamp_type, bodo.pd_timedelta_type]:
        hro__dit = ('datetime64[ns]' if data == bodo.pd_timestamp_type else
            'timedelta64[ns]')

        def impl_timestamp(data, error_on_nonarray=True, use_nullable_array
            =None, scalar_to_arr_len=None):
            kbdch__itmk = scalar_to_arr_len
            A = np.empty(kbdch__itmk, hro__dit)
            data = bodo.utils.conversion.unbox_if_timestamp(data)
            for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                kbdch__itmk):
                A[dtxpf__hiutb] = data
            return A
        return impl_timestamp
    return (lambda data, error_on_nonarray=True, use_nullable_array=None,
        scalar_to_arr_len=None: bodo.utils.conversion.coerce_to_ndarray(
        data, error_on_nonarray, use_nullable_array, scalar_to_arr_len))


def _is_str_dtype(dtype):
    return isinstance(dtype, bodo.libs.str_arr_ext.StringDtype) or isinstance(
        dtype, types.Function) and dtype.key[0
        ] == str or is_overload_constant_str(dtype) and get_overload_const_str(
        dtype) == 'str' or isinstance(dtype, types.TypeRef
        ) and dtype.instance_type == types.unicode_type


def fix_arr_dtype(data, new_dtype, copy=None, nan_to_str=True, from_series=
    False):
    return data


@overload(fix_arr_dtype, no_unliteral=True)
def overload_fix_arr_dtype(data, new_dtype, copy=None, nan_to_str=True,
    from_series=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'fix_arr_dtype()')
    cyh__xfxld = is_overload_true(copy)
    yhyk__bwpvb = is_overload_constant_str(new_dtype
        ) and get_overload_const_str(new_dtype) == 'object'
    if is_overload_none(new_dtype) or yhyk__bwpvb:
        if cyh__xfxld:
            return (lambda data, new_dtype, copy=None, nan_to_str=True,
                from_series=False: data.copy())
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data)
    if isinstance(data, NullableTupleType):
        nb_dtype = bodo.utils.typing.parse_dtype(new_dtype)
        if isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype):
            nb_dtype = nb_dtype.dtype
        hnnqj__fgjw = {types.unicode_type: '', boolean_dtype: False, types.
            bool_: False, types.int8: np.int8(0), types.int16: np.int16(0),
            types.int32: np.int32(0), types.int64: np.int64(0), types.uint8:
            np.uint8(0), types.uint16: np.uint16(0), types.uint32: np.
            uint32(0), types.uint64: np.uint64(0), types.float32: np.
            float32(0), types.float64: np.float64(0), bodo.datetime64ns: pd
            .Timestamp(0), bodo.timedelta64ns: pd.Timedelta(0)}
        chw__ovqge = {types.unicode_type: str, types.bool_: bool,
            boolean_dtype: bool, types.int8: np.int8, types.int16: np.int16,
            types.int32: np.int32, types.int64: np.int64, types.uint8: np.
            uint8, types.uint16: np.uint16, types.uint32: np.uint32, types.
            uint64: np.uint64, types.float32: np.float32, types.float64: np
            .float64, bodo.datetime64ns: pd.to_datetime, bodo.timedelta64ns:
            pd.to_timedelta}
        raqf__coj = hnnqj__fgjw.keys()
        ppv__pqsd = list(data._tuple_typ.types)
        if nb_dtype not in raqf__coj:
            raise BodoError(f'type conversion to {nb_dtype} types unsupported.'
                )
        for oqynt__jdzg in ppv__pqsd:
            if oqynt__jdzg == bodo.datetime64ns:
                if nb_dtype not in (types.unicode_type, types.int64, types.
                    uint64, bodo.datetime64ns):
                    raise BodoError(
                        f'invalid type conversion from {oqynt__jdzg} to {nb_dtype}.'
                        )
            elif oqynt__jdzg == bodo.timedelta64ns:
                if nb_dtype not in (types.unicode_type, types.int64, types.
                    uint64, bodo.timedelta64ns):
                    raise BodoError(
                        f'invalid type conversion from {oqynt__jdzg} to {nb_dtype}.'
                        )
        ngci__gtd = (
            'def impl(data, new_dtype, copy=None, nan_to_str=True, from_series=False):\n'
            )
        ngci__gtd += '  data_tup = data._data\n'
        ngci__gtd += '  null_tup = data._null_values\n'
        for dtxpf__hiutb in range(len(ppv__pqsd)):
            ngci__gtd += (
                f'  val_{dtxpf__hiutb} = convert_func(default_value)\n')
            ngci__gtd += f'  if not null_tup[{dtxpf__hiutb}]:\n'
            ngci__gtd += (
                f'    val_{dtxpf__hiutb} = convert_func(data_tup[{dtxpf__hiutb}])\n'
                )
        ceu__fvxxi = ', '.join(f'val_{dtxpf__hiutb}' for dtxpf__hiutb in
            range(len(ppv__pqsd)))
        ngci__gtd += f'  vals_tup = ({ceu__fvxxi},)\n'
        ngci__gtd += """  res_tup = bodo.libs.nullable_tuple_ext.build_nullable_tuple(vals_tup, null_tup)
"""
        ngci__gtd += '  return res_tup\n'
        xqymu__ykv = {}
        pnlqx__xfb = chw__ovqge[nb_dtype]
        irsha__cpqcg = hnnqj__fgjw[nb_dtype]
        exec(ngci__gtd, {'bodo': bodo, 'np': np, 'pd': pd, 'default_value':
            irsha__cpqcg, 'convert_func': pnlqx__xfb}, xqymu__ykv)
        impl = xqymu__ykv['impl']
        return impl
    if _is_str_dtype(new_dtype):
        if isinstance(data.dtype, types.Integer):

            def impl_int_str(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                kbdch__itmk = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(kbdch__itmk,
                    -1)
                for hhgdj__ozjqm in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    if bodo.libs.array_kernels.isna(data, hhgdj__ozjqm):
                        if nan_to_str:
                            bodo.libs.str_arr_ext.str_arr_setitem_NA_str(A,
                                hhgdj__ozjqm)
                        else:
                            bodo.libs.array_kernels.setna(A, hhgdj__ozjqm)
                    else:
                        bodo.libs.str_arr_ext.str_arr_setitem_int_to_str(A,
                            hhgdj__ozjqm, data[hhgdj__ozjqm])
                return A
            return impl_int_str
        if data.dtype == bytes_type:

            def impl_binary(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                kbdch__itmk = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(kbdch__itmk,
                    -1)
                for hhgdj__ozjqm in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    if bodo.libs.array_kernels.isna(data, hhgdj__ozjqm):
                        bodo.libs.array_kernels.setna(A, hhgdj__ozjqm)
                    else:
                        A[hhgdj__ozjqm] = ''.join([chr(xsc__zzf) for
                            xsc__zzf in data[hhgdj__ozjqm]])
                return A
            return impl_binary
        if is_overload_true(from_series) and data.dtype in (bodo.
            datetime64ns, bodo.timedelta64ns):

            def impl_str_dt_series(data, new_dtype, copy=None, nan_to_str=
                True, from_series=False):
                numba.parfors.parfor.init_prange()
                kbdch__itmk = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(kbdch__itmk,
                    -1)
                for hhgdj__ozjqm in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    if bodo.libs.array_kernels.isna(data, hhgdj__ozjqm):
                        if nan_to_str:
                            A[hhgdj__ozjqm] = 'NaT'
                        else:
                            bodo.libs.array_kernels.setna(A, hhgdj__ozjqm)
                        continue
                    A[hhgdj__ozjqm] = str(box_if_dt64(data[hhgdj__ozjqm]))
                return A
            return impl_str_dt_series
        else:

            def impl_str_array(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                kbdch__itmk = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(kbdch__itmk,
                    -1)
                for hhgdj__ozjqm in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    if bodo.libs.array_kernels.isna(data, hhgdj__ozjqm):
                        if nan_to_str:
                            A[hhgdj__ozjqm] = 'nan'
                        else:
                            bodo.libs.array_kernels.setna(A, hhgdj__ozjqm)
                        continue
                    A[hhgdj__ozjqm] = str(data[hhgdj__ozjqm])
                return A
            return impl_str_array
    if isinstance(new_dtype, bodo.hiframes.pd_categorical_ext.
        PDCategoricalDtype):

        def impl_cat_dtype(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            kbdch__itmk = len(data)
            numba.parfors.parfor.init_prange()
            zrpk__hsjli = (bodo.hiframes.pd_categorical_ext.
                get_label_dict_from_categories(new_dtype.categories.values))
            A = bodo.hiframes.pd_categorical_ext.alloc_categorical_array(
                kbdch__itmk, new_dtype)
            zvrk__fwmj = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A))
            for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                kbdch__itmk):
                if bodo.libs.array_kernels.isna(data, dtxpf__hiutb):
                    bodo.libs.array_kernels.setna(A, dtxpf__hiutb)
                    continue
                val = data[dtxpf__hiutb]
                if val not in zrpk__hsjli:
                    bodo.libs.array_kernels.setna(A, dtxpf__hiutb)
                    continue
                zvrk__fwmj[dtxpf__hiutb] = zrpk__hsjli[val]
            return A
        return impl_cat_dtype
    if is_overload_constant_str(new_dtype) and get_overload_const_str(new_dtype
        ) == 'category':

        def impl_category(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            gyo__nxn = bodo.libs.array_kernels.unique(data, dropna=True)
            gyo__nxn = pd.Series(gyo__nxn).sort_values().values
            gyo__nxn = bodo.allgatherv(gyo__nxn, False)
            lhb__cqvfc = bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo
                .utils.conversion.index_from_array(gyo__nxn, None), False,
                None, None)
            kbdch__itmk = len(data)
            numba.parfors.parfor.init_prange()
            zrpk__hsjli = (bodo.hiframes.pd_categorical_ext.
                get_label_dict_from_categories_no_duplicates(gyo__nxn))
            A = bodo.hiframes.pd_categorical_ext.alloc_categorical_array(
                kbdch__itmk, lhb__cqvfc)
            zvrk__fwmj = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A))
            for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                kbdch__itmk):
                if bodo.libs.array_kernels.isna(data, dtxpf__hiutb):
                    bodo.libs.array_kernels.setna(A, dtxpf__hiutb)
                    continue
                val = data[dtxpf__hiutb]
                zvrk__fwmj[dtxpf__hiutb] = zrpk__hsjli[val]
            return A
        return impl_category
    nb_dtype = bodo.utils.typing.parse_dtype(new_dtype)
    if isinstance(data, bodo.libs.int_arr_ext.IntegerArrayType):
        lwseh__jcir = isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype
            ) and data.dtype == nb_dtype.dtype
    else:
        lwseh__jcir = data.dtype == nb_dtype
    if cyh__xfxld and lwseh__jcir:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data.copy())
    if lwseh__jcir:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data)
    if isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype):
        if isinstance(nb_dtype, types.Integer):
            hro__dit = nb_dtype
        else:
            hro__dit = nb_dtype.dtype
        if isinstance(data.dtype, types.Float):

            def impl_float(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                kbdch__itmk = len(data)
                numba.parfors.parfor.init_prange()
                mwfl__pqsb = bodo.libs.int_arr_ext.alloc_int_array(kbdch__itmk,
                    hro__dit)
                for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    if bodo.libs.array_kernels.isna(data, dtxpf__hiutb):
                        bodo.libs.array_kernels.setna(mwfl__pqsb, dtxpf__hiutb)
                    else:
                        mwfl__pqsb[dtxpf__hiutb] = int(data[dtxpf__hiutb])
                return mwfl__pqsb
            return impl_float
        else:
            if data == bodo.dict_str_arr_type:

                def impl_dict(data, new_dtype, copy=None, nan_to_str=True,
                    from_series=False):
                    return bodo.libs.dict_arr_ext.convert_dict_arr_to_int(data,
                        hro__dit)
                return impl_dict

            def impl(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                kbdch__itmk = len(data)
                numba.parfors.parfor.init_prange()
                mwfl__pqsb = bodo.libs.int_arr_ext.alloc_int_array(kbdch__itmk,
                    hro__dit)
                for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    if bodo.libs.array_kernels.isna(data, dtxpf__hiutb):
                        bodo.libs.array_kernels.setna(mwfl__pqsb, dtxpf__hiutb)
                    else:
                        mwfl__pqsb[dtxpf__hiutb] = np.int64(data[dtxpf__hiutb])
                return mwfl__pqsb
            return impl
    if isinstance(nb_dtype, types.Integer) and isinstance(data.dtype, types
        .Integer):

        def impl(data, new_dtype, copy=None, nan_to_str=True, from_series=False
            ):
            return data.astype(nb_dtype)
        return impl
    if nb_dtype == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            kbdch__itmk = len(data)
            numba.parfors.parfor.init_prange()
            mwfl__pqsb = bodo.libs.bool_arr_ext.alloc_bool_array(kbdch__itmk)
            for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                kbdch__itmk):
                if bodo.libs.array_kernels.isna(data, dtxpf__hiutb):
                    bodo.libs.array_kernels.setna(mwfl__pqsb, dtxpf__hiutb)
                else:
                    mwfl__pqsb[dtxpf__hiutb] = bool(data[dtxpf__hiutb])
            return mwfl__pqsb
        return impl_bool
    if nb_dtype == bodo.datetime_date_type:
        if data.dtype == bodo.datetime64ns:

            def impl_date(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                kbdch__itmk = len(data)
                moh__grvj = (bodo.hiframes.datetime_date_ext.
                    alloc_datetime_date_array(kbdch__itmk))
                for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    if bodo.libs.array_kernels.isna(data, dtxpf__hiutb):
                        bodo.libs.array_kernels.setna(moh__grvj, dtxpf__hiutb)
                    else:
                        moh__grvj[dtxpf__hiutb
                            ] = bodo.utils.conversion.box_if_dt64(data[
                            dtxpf__hiutb]).date()
                return moh__grvj
            return impl_date
    if nb_dtype == bodo.datetime64ns:
        if data.dtype == bodo.string_type:

            def impl_str(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                return bodo.hiframes.pd_timestamp_ext.series_str_dt64_astype(
                    data)
            return impl_str
        if data == bodo.datetime_date_array_type:

            def impl_date(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                return (bodo.hiframes.pd_timestamp_ext.
                    datetime_date_arr_to_dt64_arr(data))
            return impl_date
        if isinstance(data.dtype, types.Number) or data.dtype in [bodo.
            timedelta64ns, types.bool_]:

            def impl_numeric(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                kbdch__itmk = len(data)
                numba.parfors.parfor.init_prange()
                moh__grvj = np.empty(kbdch__itmk, dtype=np.dtype(
                    'datetime64[ns]'))
                for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                    kbdch__itmk):
                    if bodo.libs.array_kernels.isna(data, dtxpf__hiutb):
                        bodo.libs.array_kernels.setna(moh__grvj, dtxpf__hiutb)
                    else:
                        moh__grvj[dtxpf__hiutb
                            ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                            np.int64(data[dtxpf__hiutb]))
                return moh__grvj
            return impl_numeric
    if nb_dtype == bodo.timedelta64ns:
        if data.dtype == bodo.string_type:

            def impl_str(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                return bodo.hiframes.pd_timestamp_ext.series_str_td64_astype(
                    data)
            return impl_str
        if isinstance(data.dtype, types.Number) or data.dtype in [bodo.
            datetime64ns, types.bool_]:
            if cyh__xfxld:

                def impl_numeric(data, new_dtype, copy=None, nan_to_str=
                    True, from_series=False):
                    kbdch__itmk = len(data)
                    numba.parfors.parfor.init_prange()
                    moh__grvj = np.empty(kbdch__itmk, dtype=np.dtype(
                        'timedelta64[ns]'))
                    for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                        kbdch__itmk):
                        if bodo.libs.array_kernels.isna(data, dtxpf__hiutb):
                            bodo.libs.array_kernels.setna(moh__grvj,
                                dtxpf__hiutb)
                        else:
                            moh__grvj[dtxpf__hiutb] = (bodo.hiframes.
                                pd_timestamp_ext.integer_to_timedelta64(np.
                                int64(data[dtxpf__hiutb])))
                    return moh__grvj
                return impl_numeric
            else:
                return (lambda data, new_dtype, copy=None, nan_to_str=True,
                    from_series=False: data.view('int64'))
    if nb_dtype == types.int64 and data.dtype in [bodo.datetime64ns, bodo.
        timedelta64ns]:

        def impl_datelike_to_integer(data, new_dtype, copy=None, nan_to_str
            =True, from_series=False):
            kbdch__itmk = len(data)
            numba.parfors.parfor.init_prange()
            A = np.empty(kbdch__itmk, types.int64)
            for dtxpf__hiutb in numba.parfors.parfor.internal_prange(
                kbdch__itmk):
                if bodo.libs.array_kernels.isna(data, dtxpf__hiutb):
                    bodo.libs.array_kernels.setna(A, dtxpf__hiutb)
                else:
                    A[dtxpf__hiutb] = np.int64(data[dtxpf__hiutb])
            return A
        return impl_datelike_to_integer
    if data.dtype != nb_dtype:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data.astype(nb_dtype))
    raise BodoError(f'Conversion from {data} to {new_dtype} not supported yet')


def array_type_from_dtype(dtype):
    return dtype_to_array_type(bodo.utils.typing.parse_dtype(dtype))


@overload(array_type_from_dtype)
def overload_array_type_from_dtype(dtype):
    arr_type = dtype_to_array_type(bodo.utils.typing.parse_dtype(dtype))
    return lambda dtype: arr_type


@numba.jit
def flatten_array(A):
    vxjhn__wulmc = []
    kbdch__itmk = len(A)
    for dtxpf__hiutb in range(kbdch__itmk):
        gxwk__kovw = A[dtxpf__hiutb]
        for adl__ecvg in gxwk__kovw:
            vxjhn__wulmc.append(adl__ecvg)
    return bodo.utils.conversion.coerce_to_array(vxjhn__wulmc)


def parse_datetimes_from_strings(data):
    return data


@overload(parse_datetimes_from_strings, no_unliteral=True)
def overload_parse_datetimes_from_strings(data):
    assert is_str_arr_type(data
        ), 'parse_datetimes_from_strings: string array expected'

    def parse_impl(data):
        numba.parfors.parfor.init_prange()
        kbdch__itmk = len(data)
        ehgao__gsrhs = np.empty(kbdch__itmk, bodo.utils.conversion.NS_DTYPE)
        for dtxpf__hiutb in numba.parfors.parfor.internal_prange(kbdch__itmk):
            ehgao__gsrhs[dtxpf__hiutb
                ] = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(data[
                dtxpf__hiutb])
        return ehgao__gsrhs
    return parse_impl


def convert_to_dt64ns(data):
    return data


@overload(convert_to_dt64ns, no_unliteral=True)
def overload_convert_to_dt64ns(data):
    if data == bodo.hiframes.datetime_date_ext.datetime_date_array_type:
        return (lambda data: bodo.hiframes.pd_timestamp_ext.
            datetime_date_arr_to_dt64_arr(data))
    if is_np_arr_typ(data, types.int64):
        return lambda data: data.view(bodo.utils.conversion.NS_DTYPE)
    if is_np_arr_typ(data, types.NPDatetime('ns')):
        return lambda data: data
    if is_str_arr_type(data):
        return lambda data: bodo.utils.conversion.parse_datetimes_from_strings(
            data)
    raise BodoError(f'invalid data type {data} for dt64 conversion')


def convert_to_td64ns(data):
    return data


@overload(convert_to_td64ns, no_unliteral=True)
def overload_convert_to_td64ns(data):
    if is_np_arr_typ(data, types.int64):
        return lambda data: data.view(bodo.utils.conversion.TD_DTYPE)
    if is_np_arr_typ(data, types.NPTimedelta('ns')):
        return lambda data: data
    if is_str_arr_type(data):
        raise BodoError('conversion to timedelta from string not supported yet'
            )
    raise BodoError(f'invalid data type {data} for timedelta64 conversion')


def convert_to_index(data, name=None):
    return data


@overload(convert_to_index, no_unliteral=True)
def overload_convert_to_index(data, name=None):
    from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, RangeIndexType, StringIndexType, TimedeltaIndexType
    if isinstance(data, (RangeIndexType, NumericIndexType,
        DatetimeIndexType, TimedeltaIndexType, StringIndexType,
        BinaryIndexType, CategoricalIndexType, PeriodIndexType, types.NoneType)
        ):
        return lambda data, name=None: data

    def impl(data, name=None):
        izh__ypv = bodo.utils.conversion.coerce_to_array(data)
        return bodo.utils.conversion.index_from_array(izh__ypv, name)
    return impl


def force_convert_index(I1, I2):
    return I2


@overload(force_convert_index, no_unliteral=True)
def overload_force_convert_index(I1, I2):
    from bodo.hiframes.pd_index_ext import RangeIndexType
    if isinstance(I2, RangeIndexType):
        return lambda I1, I2: pd.RangeIndex(len(I1._data))
    return lambda I1, I2: I1


def index_from_array(data, name=None):
    return data


@overload(index_from_array, no_unliteral=True)
def overload_index_from_array(data, name=None):
    if data in [bodo.string_array_type, bodo.binary_array_type, bodo.
        dict_str_arr_type]:
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_binary_str_index(data, name))
    if (data == bodo.hiframes.datetime_date_ext.datetime_date_array_type or
        data.dtype == types.NPDatetime('ns')):
        return lambda data, name=None: pd.DatetimeIndex(data, name=name)
    if data.dtype == types.NPTimedelta('ns'):
        return lambda data, name=None: pd.TimedeltaIndex(data, name=name)
    if isinstance(data.dtype, (types.Integer, types.Float, types.Boolean)):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_numeric_index(data, name))
    if isinstance(data, bodo.libs.interval_arr_ext.IntervalArrayType):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_interval_index(data, name))
    if isinstance(data, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_categorical_index(data, name))
    if isinstance(data, bodo.libs.pd_datetime_arr_ext.DatetimeArrayType):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_datetime_index(data, name))
    raise BodoError(f'cannot convert {data} to Index')


def index_to_array(data):
    return data


@overload(index_to_array, no_unliteral=True)
def overload_index_to_array(I):
    from bodo.hiframes.pd_index_ext import RangeIndexType
    if isinstance(I, RangeIndexType):
        return lambda I: np.arange(I._start, I._stop, I._step)
    return lambda I: bodo.hiframes.pd_index_ext.get_index_data(I)


def false_if_none(val):
    return False if val is None else val


@overload(false_if_none, no_unliteral=True)
def overload_false_if_none(val):
    if is_overload_none(val):
        return lambda val: False
    return lambda val: val


def extract_name_if_none(data, name):
    return name


@overload(extract_name_if_none, no_unliteral=True)
def overload_extract_name_if_none(data, name):
    from bodo.hiframes.pd_index_ext import CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, TimedeltaIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    if not is_overload_none(name):
        return lambda data, name: name
    if isinstance(data, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType, PeriodIndexType, CategoricalIndexType)):
        return lambda data, name: bodo.hiframes.pd_index_ext.get_index_name(
            data)
    if isinstance(data, SeriesType):
        return lambda data, name: bodo.hiframes.pd_series_ext.get_series_name(
            data)
    return lambda data, name: name


def extract_index_if_none(data, index):
    return index


@overload(extract_index_if_none, no_unliteral=True)
def overload_extract_index_if_none(data, index):
    from bodo.hiframes.pd_series_ext import SeriesType
    if not is_overload_none(index):
        return lambda data, index: index
    if isinstance(data, SeriesType):
        return (lambda data, index: bodo.hiframes.pd_series_ext.
            get_series_index(data))
    return lambda data, index: bodo.hiframes.pd_index_ext.init_range_index(
        0, len(data), 1, None)


def box_if_dt64(val):
    return val


@overload(box_if_dt64, no_unliteral=True)
def overload_box_if_dt64(val):
    if val == types.NPDatetime('ns'):
        return (lambda val: bodo.hiframes.pd_timestamp_ext.
            convert_datetime64_to_timestamp(val))
    if val == types.NPTimedelta('ns'):
        return (lambda val: bodo.hiframes.pd_timestamp_ext.
            convert_numpy_timedelta64_to_pd_timedelta(val))
    return lambda val: val


def unbox_if_timestamp(val):
    return val


@overload(unbox_if_timestamp, no_unliteral=True)
def overload_unbox_if_timestamp(val):
    if val == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        return lambda val: bodo.hiframes.pd_timestamp_ext.integer_to_dt64(val
            .value)
    if val == bodo.hiframes.datetime_datetime_ext.datetime_datetime_type:
        return lambda val: bodo.hiframes.pd_timestamp_ext.integer_to_dt64(pd
            .Timestamp(val).value)
    if val == bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type:
        return (lambda val: bodo.hiframes.pd_timestamp_ext.
            integer_to_timedelta64(val.value))
    if val == types.Optional(bodo.hiframes.pd_timestamp_ext.pd_timestamp_type):

        def impl_optional(val):
            if val is None:
                fzb__hapl = None
            else:
                fzb__hapl = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(bodo
                    .utils.indexing.unoptional(val).value)
            return fzb__hapl
        return impl_optional
    if val == types.Optional(bodo.hiframes.datetime_timedelta_ext.
        pd_timedelta_type):

        def impl_optional_td(val):
            if val is None:
                fzb__hapl = None
            else:
                fzb__hapl = (bodo.hiframes.pd_timestamp_ext.
                    integer_to_timedelta64(bodo.utils.indexing.unoptional(
                    val).value))
            return fzb__hapl
        return impl_optional_td
    return lambda val: val


def to_tuple(val):
    return val


@overload(to_tuple, no_unliteral=True)
def overload_to_tuple(val):
    if not isinstance(val, types.BaseTuple) and is_overload_constant_list(val):
        hdfmk__imb = len(val.types if isinstance(val, types.LiteralList) else
            get_overload_const_list(val))
        ngci__gtd = 'def f(val):\n'
        ohk__mmd = ','.join(f'val[{dtxpf__hiutb}]' for dtxpf__hiutb in
            range(hdfmk__imb))
        ngci__gtd += f'  return ({ohk__mmd},)\n'
        xqymu__ykv = {}
        exec(ngci__gtd, {}, xqymu__ykv)
        impl = xqymu__ykv['f']
        return impl
    assert isinstance(val, types.BaseTuple), 'tuple type expected'
    return lambda val: val


def get_array_if_series_or_index(data):
    return data


@overload(get_array_if_series_or_index)
def overload_get_array_if_series_or_index(data):
    from bodo.hiframes.pd_series_ext import SeriesType
    if isinstance(data, SeriesType):
        return lambda data: bodo.hiframes.pd_series_ext.get_series_data(data)
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        return lambda data: bodo.utils.conversion.coerce_to_array(data)
    if isinstance(data, bodo.hiframes.pd_index_ext.HeterogeneousIndexType):
        if not is_heterogeneous_tuple_type(data.data):

            def impl(data):
                ceiyr__jsdx = bodo.hiframes.pd_index_ext.get_index_data(data)
                return bodo.utils.conversion.coerce_to_array(ceiyr__jsdx)
            return impl

        def impl(data):
            return bodo.hiframes.pd_index_ext.get_index_data(data)
        return impl
    return lambda data: data


def extract_index_array(A):
    return np.arange(len(A))


@overload(extract_index_array, no_unliteral=True)
def overload_extract_index_array(A):
    from bodo.hiframes.pd_series_ext import SeriesType
    if isinstance(A, SeriesType):

        def impl(A):
            index = bodo.hiframes.pd_series_ext.get_series_index(A)
            wag__dys = bodo.utils.conversion.coerce_to_array(index)
            return wag__dys
        return impl
    return lambda A: np.arange(len(A))


def ensure_contig_if_np(arr):
    return np.ascontiguousarray(arr)


@overload(ensure_contig_if_np, no_unliteral=True)
def overload_ensure_contig_if_np(arr):
    if isinstance(arr, types.Array):
        return lambda arr: np.ascontiguousarray(arr)
    return lambda arr: arr


def struct_if_heter_dict(values, names):
    return {afjhr__fyk: crl__aaqkf for afjhr__fyk, crl__aaqkf in zip(names,
        values)}


@overload(struct_if_heter_dict, no_unliteral=True)
def overload_struct_if_heter_dict(values, names):
    if not types.is_homogeneous(*values.types):
        return lambda values, names: bodo.libs.struct_arr_ext.init_struct(
            values, names)
    ayigi__epbwd = len(values.types)
    ngci__gtd = 'def f(values, names):\n'
    ohk__mmd = ','.join("'{}': values[{}]".format(get_overload_const_str(
        names.types[dtxpf__hiutb]), dtxpf__hiutb) for dtxpf__hiutb in range
        (ayigi__epbwd))
    ngci__gtd += '  return {{{}}}\n'.format(ohk__mmd)
    xqymu__ykv = {}
    exec(ngci__gtd, {}, xqymu__ykv)
    impl = xqymu__ykv['f']
    return impl
