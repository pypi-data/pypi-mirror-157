"""
Boxing and unboxing support for DataFrame, Series, etc.
"""
import datetime
import decimal
import warnings
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.ir_utils import GuardException, guard
from numba.core.typing import signature
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, intrinsic, typeof_impl, unbox
from numba.np import numpy_support
from numba.typed.typeddict import Dict
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import PDCategoricalDtype
from bodo.hiframes.pd_dataframe_ext import DataFramePayloadType, DataFrameType, check_runtime_cols_unsupported, construct_dataframe
from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, RangeIndexType, StringIndexType, TimedeltaIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType, typeof_pd_int_dtype
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType, PandasDatetimeTZDtype
from bodo.libs.str_arr_ext import string_array_type, string_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.typing import BodoError, BodoWarning, dtype_to_array_type, get_overload_const_bool, get_overload_const_int, get_overload_const_str, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array
ll.add_symbol('is_np_array', hstr_ext.is_np_array)
ll.add_symbol('array_size', hstr_ext.array_size)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
TABLE_FORMAT_THRESHOLD = 20
_use_dict_str_type = False


def _set_bodo_meta_in_pandas():
    if '_bodo_meta' not in pd.Series._metadata:
        pd.Series._metadata.append('_bodo_meta')
    if '_bodo_meta' not in pd.DataFrame._metadata:
        pd.DataFrame._metadata.append('_bodo_meta')


_set_bodo_meta_in_pandas()


@typeof_impl.register(pd.DataFrame)
def typeof_pd_dataframe(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    fypw__jejc = tuple(val.columns.to_list())
    igigv__ggjd = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        lpvyk__vysl = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        lpvyk__vysl = numba.typeof(val.index)
    efix__ojsh = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    hjh__yrn = len(igigv__ggjd) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(igigv__ggjd, lpvyk__vysl, fypw__jejc, efix__ojsh,
        is_table_format=hjh__yrn)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    efix__ojsh = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        lket__mpzza = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        lket__mpzza = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    kvsw__bzm = dtype_to_array_type(dtype)
    if _use_dict_str_type and kvsw__bzm == string_array_type:
        kvsw__bzm = bodo.dict_str_arr_type
    return SeriesType(dtype, data=kvsw__bzm, index=lket__mpzza, name_typ=
        numba.typeof(val.name), dist=efix__ojsh)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    adt__tnau = c.pyapi.object_getattr_string(val, 'index')
    rta__xsz = c.pyapi.to_native_value(typ.index, adt__tnau).value
    c.pyapi.decref(adt__tnau)
    if typ.is_table_format:
        wgzia__hkn = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        wgzia__hkn.parent = val
        for ksp__whe, vfa__srqb in typ.table_type.type_to_blk.items():
            ijleh__vguev = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[vfa__srqb]))
            heql__bue, aoj__bazx = ListInstance.allocate_ex(c.context, c.
                builder, types.List(ksp__whe), ijleh__vguev)
            aoj__bazx.size = ijleh__vguev
            setattr(wgzia__hkn, f'block_{vfa__srqb}', aoj__bazx.value)
        sdltk__jiyi = c.pyapi.call_method(val, '__len__', ())
        jxwn__hxmqp = c.pyapi.long_as_longlong(sdltk__jiyi)
        c.pyapi.decref(sdltk__jiyi)
        wgzia__hkn.len = jxwn__hxmqp
        tpghx__nylj = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [wgzia__hkn._getvalue()])
    else:
        inpm__tgi = [c.context.get_constant_null(ksp__whe) for ksp__whe in
            typ.data]
        tpghx__nylj = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            inpm__tgi)
    fgq__qono = construct_dataframe(c.context, c.builder, typ, tpghx__nylj,
        rta__xsz, val, None)
    return NativeValue(fgq__qono)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        tra__lor = df._bodo_meta['type_metadata'][1]
    else:
        tra__lor = [None] * len(df.columns)
    dabv__xjnk = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=tra__lor[i])) for i in range(len(df.columns))]
    dabv__xjnk = [(bodo.dict_str_arr_type if _use_dict_str_type and 
        ksp__whe == string_array_type else ksp__whe) for ksp__whe in dabv__xjnk
        ]
    return tuple(dabv__xjnk)


class SeriesDtypeEnum(Enum):
    Int8 = 0
    UInt8 = 1
    Int32 = 2
    UInt32 = 3
    Int64 = 4
    UInt64 = 7
    Float32 = 5
    Float64 = 6
    Int16 = 8
    UInt16 = 9
    STRING = 10
    Bool = 11
    Decimal = 12
    Datime_Date = 13
    NP_Datetime64ns = 14
    NP_Timedelta64ns = 15
    Int128 = 16
    LIST = 18
    STRUCT = 19
    BINARY = 21
    ARRAY = 22
    PD_nullable_Int8 = 23
    PD_nullable_UInt8 = 24
    PD_nullable_Int16 = 25
    PD_nullable_UInt16 = 26
    PD_nullable_Int32 = 27
    PD_nullable_UInt32 = 28
    PD_nullable_Int64 = 29
    PD_nullable_UInt64 = 30
    PD_nullable_bool = 31
    CategoricalType = 32
    NoneType = 33
    Literal = 34
    IntegerArray = 35
    RangeIndexType = 36
    DatetimeIndexType = 37
    NumericIndexType = 38
    PeriodIndexType = 39
    IntervalIndexType = 40
    CategoricalIndexType = 41
    StringIndexType = 42
    BinaryIndexType = 43
    TimedeltaIndexType = 44
    LiteralType = 45


_one_to_one_type_to_enum_map = {types.int8: SeriesDtypeEnum.Int8.value,
    types.uint8: SeriesDtypeEnum.UInt8.value, types.int32: SeriesDtypeEnum.
    Int32.value, types.uint32: SeriesDtypeEnum.UInt32.value, types.int64:
    SeriesDtypeEnum.Int64.value, types.uint64: SeriesDtypeEnum.UInt64.value,
    types.float32: SeriesDtypeEnum.Float32.value, types.float64:
    SeriesDtypeEnum.Float64.value, types.NPDatetime('ns'): SeriesDtypeEnum.
    NP_Datetime64ns.value, types.NPTimedelta('ns'): SeriesDtypeEnum.
    NP_Timedelta64ns.value, types.bool_: SeriesDtypeEnum.Bool.value, types.
    int16: SeriesDtypeEnum.Int16.value, types.uint16: SeriesDtypeEnum.
    UInt16.value, types.Integer('int128', 128): SeriesDtypeEnum.Int128.
    value, bodo.hiframes.datetime_date_ext.datetime_date_type:
    SeriesDtypeEnum.Datime_Date.value, IntDtype(types.int8):
    SeriesDtypeEnum.PD_nullable_Int8.value, IntDtype(types.uint8):
    SeriesDtypeEnum.PD_nullable_UInt8.value, IntDtype(types.int16):
    SeriesDtypeEnum.PD_nullable_Int16.value, IntDtype(types.uint16):
    SeriesDtypeEnum.PD_nullable_UInt16.value, IntDtype(types.int32):
    SeriesDtypeEnum.PD_nullable_Int32.value, IntDtype(types.uint32):
    SeriesDtypeEnum.PD_nullable_UInt32.value, IntDtype(types.int64):
    SeriesDtypeEnum.PD_nullable_Int64.value, IntDtype(types.uint64):
    SeriesDtypeEnum.PD_nullable_UInt64.value, bytes_type: SeriesDtypeEnum.
    BINARY.value, string_type: SeriesDtypeEnum.STRING.value, bodo.bool_:
    SeriesDtypeEnum.Bool.value, types.none: SeriesDtypeEnum.NoneType.value}
_one_to_one_enum_to_type_map = {SeriesDtypeEnum.Int8.value: types.int8,
    SeriesDtypeEnum.UInt8.value: types.uint8, SeriesDtypeEnum.Int32.value:
    types.int32, SeriesDtypeEnum.UInt32.value: types.uint32,
    SeriesDtypeEnum.Int64.value: types.int64, SeriesDtypeEnum.UInt64.value:
    types.uint64, SeriesDtypeEnum.Float32.value: types.float32,
    SeriesDtypeEnum.Float64.value: types.float64, SeriesDtypeEnum.
    NP_Datetime64ns.value: types.NPDatetime('ns'), SeriesDtypeEnum.
    NP_Timedelta64ns.value: types.NPTimedelta('ns'), SeriesDtypeEnum.Int16.
    value: types.int16, SeriesDtypeEnum.UInt16.value: types.uint16,
    SeriesDtypeEnum.Int128.value: types.Integer('int128', 128),
    SeriesDtypeEnum.Datime_Date.value: bodo.hiframes.datetime_date_ext.
    datetime_date_type, SeriesDtypeEnum.PD_nullable_Int8.value: IntDtype(
    types.int8), SeriesDtypeEnum.PD_nullable_UInt8.value: IntDtype(types.
    uint8), SeriesDtypeEnum.PD_nullable_Int16.value: IntDtype(types.int16),
    SeriesDtypeEnum.PD_nullable_UInt16.value: IntDtype(types.uint16),
    SeriesDtypeEnum.PD_nullable_Int32.value: IntDtype(types.int32),
    SeriesDtypeEnum.PD_nullable_UInt32.value: IntDtype(types.uint32),
    SeriesDtypeEnum.PD_nullable_Int64.value: IntDtype(types.int64),
    SeriesDtypeEnum.PD_nullable_UInt64.value: IntDtype(types.uint64),
    SeriesDtypeEnum.BINARY.value: bytes_type, SeriesDtypeEnum.STRING.value:
    string_type, SeriesDtypeEnum.Bool.value: bodo.bool_, SeriesDtypeEnum.
    NoneType.value: types.none}


def _dtype_from_type_enum_list(typ_enum_list):
    znqy__qzj, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(znqy__qzj) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {znqy__qzj}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        wydcm__hyo, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return wydcm__hyo, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        wydcm__hyo, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return wydcm__hyo, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        bjsx__syjvs = typ_enum_list[1]
        wrw__ibdeb = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(bjsx__syjvs, wrw__ibdeb)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        kzp__yjq = typ_enum_list[1]
        wfcid__qzid = tuple(typ_enum_list[2:2 + kzp__yjq])
        tqrx__xxs = typ_enum_list[2 + kzp__yjq:]
        pdtc__eufz = []
        for i in range(kzp__yjq):
            tqrx__xxs, ilcrh__dcod = _dtype_from_type_enum_list_recursor(
                tqrx__xxs)
            pdtc__eufz.append(ilcrh__dcod)
        return tqrx__xxs, StructType(tuple(pdtc__eufz), wfcid__qzid)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        zhh__toucs = typ_enum_list[1]
        tqrx__xxs = typ_enum_list[2:]
        return tqrx__xxs, zhh__toucs
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        zhh__toucs = typ_enum_list[1]
        tqrx__xxs = typ_enum_list[2:]
        return tqrx__xxs, numba.types.literal(zhh__toucs)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        tqrx__xxs, jpvcz__ticjn = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        tqrx__xxs, wamd__ipuaf = _dtype_from_type_enum_list_recursor(tqrx__xxs)
        tqrx__xxs, luxz__ohe = _dtype_from_type_enum_list_recursor(tqrx__xxs)
        tqrx__xxs, rdfaq__sxq = _dtype_from_type_enum_list_recursor(tqrx__xxs)
        tqrx__xxs, vusw__stjyt = _dtype_from_type_enum_list_recursor(tqrx__xxs)
        return tqrx__xxs, PDCategoricalDtype(jpvcz__ticjn, wamd__ipuaf,
            luxz__ohe, rdfaq__sxq, vusw__stjyt)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        tqrx__xxs, pzw__urz = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return tqrx__xxs, DatetimeIndexType(pzw__urz)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        tqrx__xxs, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        tqrx__xxs, pzw__urz = _dtype_from_type_enum_list_recursor(tqrx__xxs)
        tqrx__xxs, rdfaq__sxq = _dtype_from_type_enum_list_recursor(tqrx__xxs)
        return tqrx__xxs, NumericIndexType(dtype, pzw__urz, rdfaq__sxq)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        tqrx__xxs, rtp__ipn = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        tqrx__xxs, pzw__urz = _dtype_from_type_enum_list_recursor(tqrx__xxs)
        return tqrx__xxs, PeriodIndexType(rtp__ipn, pzw__urz)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        tqrx__xxs, rdfaq__sxq = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        tqrx__xxs, pzw__urz = _dtype_from_type_enum_list_recursor(tqrx__xxs)
        return tqrx__xxs, CategoricalIndexType(rdfaq__sxq, pzw__urz)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        tqrx__xxs, pzw__urz = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return tqrx__xxs, RangeIndexType(pzw__urz)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        tqrx__xxs, pzw__urz = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return tqrx__xxs, StringIndexType(pzw__urz)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        tqrx__xxs, pzw__urz = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return tqrx__xxs, BinaryIndexType(pzw__urz)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        tqrx__xxs, pzw__urz = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return tqrx__xxs, TimedeltaIndexType(pzw__urz)
    else:
        raise_bodo_error(
            f'Unexpected Internal Error while converting typing metadata: unable to infer dtype for type enum {typ_enum_list[0]}. Please file the error here: https://github.com/Bodo-inc/Feedback'
            )


def _dtype_to_type_enum_list(typ):
    return guard(_dtype_to_type_enum_list_recursor, typ)


def _dtype_to_type_enum_list_recursor(typ, upcast_numeric_index=True):
    if typ.__hash__ and typ in _one_to_one_type_to_enum_map:
        return [_one_to_one_type_to_enum_map[typ]]
    if isinstance(typ, (dict, int, list, tuple, str, bool, bytes, float)):
        return [SeriesDtypeEnum.Literal.value, typ]
    elif typ is None:
        return [SeriesDtypeEnum.Literal.value, typ]
    elif is_overload_constant_int(typ):
        flz__myl = get_overload_const_int(typ)
        if numba.types.maybe_literal(flz__myl) == typ:
            return [SeriesDtypeEnum.LiteralType.value, flz__myl]
    elif is_overload_constant_str(typ):
        flz__myl = get_overload_const_str(typ)
        if numba.types.maybe_literal(flz__myl) == typ:
            return [SeriesDtypeEnum.LiteralType.value, flz__myl]
    elif is_overload_constant_bool(typ):
        flz__myl = get_overload_const_bool(typ)
        if numba.types.maybe_literal(flz__myl) == typ:
            return [SeriesDtypeEnum.LiteralType.value, flz__myl]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        dqter__lcvi = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for imztq__cqvn in typ.names:
            dqter__lcvi.append(imztq__cqvn)
        for vqo__ilfx in typ.data:
            dqter__lcvi += _dtype_to_type_enum_list_recursor(vqo__ilfx)
        return dqter__lcvi
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        hfma__zcqca = _dtype_to_type_enum_list_recursor(typ.categories)
        qlhct__pxf = _dtype_to_type_enum_list_recursor(typ.elem_type)
        lmudq__hbxi = _dtype_to_type_enum_list_recursor(typ.ordered)
        qem__lwux = _dtype_to_type_enum_list_recursor(typ.data)
        oeqdt__abtxp = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + hfma__zcqca + qlhct__pxf + lmudq__hbxi + qem__lwux + oeqdt__abtxp
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                ipy__ofkn = types.float64
                qpvk__wpofl = types.Array(ipy__ofkn, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                ipy__ofkn = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    qpvk__wpofl = IntegerArrayType(ipy__ofkn)
                else:
                    qpvk__wpofl = types.Array(ipy__ofkn, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                ipy__ofkn = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    qpvk__wpofl = IntegerArrayType(ipy__ofkn)
                else:
                    qpvk__wpofl = types.Array(ipy__ofkn, 1, 'C')
            elif typ.dtype == types.bool_:
                ipy__ofkn = typ.dtype
                qpvk__wpofl = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(ipy__ofkn
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(qpvk__wpofl)
        else:
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(typ.dtype
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(typ.data)
    elif isinstance(typ, PeriodIndexType):
        return [SeriesDtypeEnum.PeriodIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.freq
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, CategoricalIndexType):
        return [SeriesDtypeEnum.CategoricalIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.data
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, RangeIndexType):
        return [SeriesDtypeEnum.RangeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, StringIndexType):
        return [SeriesDtypeEnum.StringIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, BinaryIndexType):
        return [SeriesDtypeEnum.BinaryIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, TimedeltaIndexType):
        return [SeriesDtypeEnum.TimedeltaIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    else:
        raise GuardException('Unable to convert type')


def _infer_series_dtype(S, array_metadata=None):
    if S.dtype == np.dtype('O'):
        if len(S.values) == 0:
            if array_metadata != None:
                return _dtype_from_type_enum_list(array_metadata).dtype
            elif hasattr(S, '_bodo_meta'
                ) and S._bodo_meta is not None and 'type_metadata' in S._bodo_meta and S._bodo_meta[
                'type_metadata'][1] is not None:
                uwef__rqsmt = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(uwef__rqsmt)
        return numba.typeof(S.values).dtype
    if isinstance(S.dtype, pd.core.arrays.integer._IntegerDtype):
        return typeof_pd_int_dtype(S.dtype, None)
    elif isinstance(S.dtype, pd.CategoricalDtype):
        return bodo.typeof(S.dtype)
    elif isinstance(S.dtype, pd.StringDtype):
        return string_type
    elif isinstance(S.dtype, pd.BooleanDtype):
        return types.bool_
    if isinstance(S.dtype, pd.DatetimeTZDtype):
        hilnf__guyc = S.dtype.unit
        if hilnf__guyc != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        slis__odx = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.dtype.tz
            )
        return PandasDatetimeTZDtype(slis__odx)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    qjpwn__wefwu = cgutils.is_not_null(builder, parent_obj)
    yroy__somyt = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(qjpwn__wefwu):
        mtiqw__msfb = pyapi.object_getattr_string(parent_obj, 'columns')
        sdltk__jiyi = pyapi.call_method(mtiqw__msfb, '__len__', ())
        builder.store(pyapi.long_as_longlong(sdltk__jiyi), yroy__somyt)
        pyapi.decref(sdltk__jiyi)
        pyapi.decref(mtiqw__msfb)
    use_parent_obj = builder.and_(qjpwn__wefwu, builder.icmp_unsigned('==',
        builder.load(yroy__somyt), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        hyw__ptctu = df_typ.runtime_colname_typ
        context.nrt.incref(builder, hyw__ptctu, dataframe_payload.columns)
        return pyapi.from_native_value(hyw__ptctu, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        ride__dfu = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        ride__dfu = np.array(df_typ.columns, 'int64')
    else:
        ride__dfu = df_typ.columns
    dihb__bpsdw = numba.typeof(ride__dfu)
    zqa__czpy = context.get_constant_generic(builder, dihb__bpsdw, ride__dfu)
    cww__azwe = pyapi.from_native_value(dihb__bpsdw, zqa__czpy, c.env_manager)
    return cww__azwe


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (seaeo__qsnqc, gmi__spodm):
        with seaeo__qsnqc:
            pyapi.incref(obj)
            dcytd__kew = context.insert_const_string(c.builder.module, 'numpy')
            obcl__xpq = pyapi.import_module_noblock(dcytd__kew)
            if df_typ.has_runtime_cols:
                foms__fhu = 0
            else:
                foms__fhu = len(df_typ.columns)
            jzvi__ijda = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), foms__fhu))
            pmyig__plh = pyapi.call_method(obcl__xpq, 'arange', (jzvi__ijda,))
            pyapi.object_setattr_string(obj, 'columns', pmyig__plh)
            pyapi.decref(obcl__xpq)
            pyapi.decref(pmyig__plh)
            pyapi.decref(jzvi__ijda)
        with gmi__spodm:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            slf__qgx = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            dcytd__kew = context.insert_const_string(c.builder.module, 'pandas'
                )
            obcl__xpq = pyapi.import_module_noblock(dcytd__kew)
            df_obj = pyapi.call_method(obcl__xpq, 'DataFrame', (pyapi.
                borrow_none(), slf__qgx))
            pyapi.decref(obcl__xpq)
            pyapi.decref(slf__qgx)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    nczpq__emzmj = cgutils.create_struct_proxy(typ)(context, builder, value=val
        )
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = nczpq__emzmj.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        bftib__evzm = typ.table_type
        wgzia__hkn = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, bftib__evzm, wgzia__hkn)
        rvrnm__qax = box_table(bftib__evzm, wgzia__hkn, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (mwybt__ixzbc, rfq__zpt):
            with mwybt__ixzbc:
                jwu__pfxwk = pyapi.object_getattr_string(rvrnm__qax, 'arrays')
                hpkyw__qto = c.pyapi.make_none()
                if n_cols is None:
                    sdltk__jiyi = pyapi.call_method(jwu__pfxwk, '__len__', ())
                    ijleh__vguev = pyapi.long_as_longlong(sdltk__jiyi)
                    pyapi.decref(sdltk__jiyi)
                else:
                    ijleh__vguev = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, ijleh__vguev) as aehlo__dyl:
                    i = aehlo__dyl.index
                    xvf__obf = pyapi.list_getitem(jwu__pfxwk, i)
                    tsjs__ona = c.builder.icmp_unsigned('!=', xvf__obf,
                        hpkyw__qto)
                    with builder.if_then(tsjs__ona):
                        gvxy__avw = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, gvxy__avw, xvf__obf)
                        pyapi.decref(gvxy__avw)
                pyapi.decref(jwu__pfxwk)
                pyapi.decref(hpkyw__qto)
            with rfq__zpt:
                df_obj = builder.load(res)
                slf__qgx = pyapi.object_getattr_string(df_obj, 'index')
                ebhhd__anm = c.pyapi.call_method(rvrnm__qax, 'to_pandas', (
                    slf__qgx,))
                builder.store(ebhhd__anm, res)
                pyapi.decref(df_obj)
                pyapi.decref(slf__qgx)
        pyapi.decref(rvrnm__qax)
    else:
        dyqgm__ogu = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        tlav__ilim = typ.data
        for i, nylgj__ojz, kvsw__bzm in zip(range(n_cols), dyqgm__ogu,
            tlav__ilim):
            ycb__agdp = cgutils.alloca_once_value(builder, nylgj__ojz)
            ofdi__gftjz = cgutils.alloca_once_value(builder, context.
                get_constant_null(kvsw__bzm))
            tsjs__ona = builder.not_(is_ll_eq(builder, ycb__agdp, ofdi__gftjz))
            rnq__ktkwe = builder.or_(builder.not_(use_parent_obj), builder.
                and_(use_parent_obj, tsjs__ona))
            with builder.if_then(rnq__ktkwe):
                gvxy__avw = pyapi.long_from_longlong(context.get_constant(
                    types.int64, i))
                context.nrt.incref(builder, kvsw__bzm, nylgj__ojz)
                arr_obj = pyapi.from_native_value(kvsw__bzm, nylgj__ojz, c.
                    env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, gvxy__avw, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(gvxy__avw)
    df_obj = builder.load(res)
    cww__azwe = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', cww__azwe)
    pyapi.decref(cww__azwe)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    hpkyw__qto = pyapi.borrow_none()
    axzx__nsl = pyapi.unserialize(pyapi.serialize_object(slice))
    uze__bfybp = pyapi.call_function_objargs(axzx__nsl, [hpkyw__qto])
    wcmgh__txvuo = pyapi.long_from_longlong(col_ind)
    gjaa__tqpoo = pyapi.tuple_pack([uze__bfybp, wcmgh__txvuo])
    qhz__lnyun = pyapi.object_getattr_string(df_obj, 'iloc')
    lavg__jdmcb = pyapi.object_getitem(qhz__lnyun, gjaa__tqpoo)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        rpsa__hjnh = pyapi.object_getattr_string(lavg__jdmcb, 'array')
    else:
        rpsa__hjnh = pyapi.object_getattr_string(lavg__jdmcb, 'values')
    if isinstance(data_typ, types.Array):
        chtt__wwich = context.insert_const_string(builder.module, 'numpy')
        wgdk__etxvt = pyapi.import_module_noblock(chtt__wwich)
        arr_obj = pyapi.call_method(wgdk__etxvt, 'ascontiguousarray', (
            rpsa__hjnh,))
        pyapi.decref(rpsa__hjnh)
        pyapi.decref(wgdk__etxvt)
    else:
        arr_obj = rpsa__hjnh
    pyapi.decref(axzx__nsl)
    pyapi.decref(uze__bfybp)
    pyapi.decref(wcmgh__txvuo)
    pyapi.decref(gjaa__tqpoo)
    pyapi.decref(qhz__lnyun)
    pyapi.decref(lavg__jdmcb)
    return arr_obj


@intrinsic
def unbox_dataframe_column(typingctx, df, i=None):
    assert isinstance(df, DataFrameType) and is_overload_constant_int(i)

    def codegen(context, builder, sig, args):
        pyapi = context.get_python_api(builder)
        c = numba.core.pythonapi._UnboxContext(context, builder, pyapi)
        df_typ = sig.args[0]
        col_ind = get_overload_const_int(sig.args[1])
        data_typ = df_typ.data[col_ind]
        nczpq__emzmj = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            nczpq__emzmj.parent, args[1], data_typ)
        pdpe__stiqw = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            wgzia__hkn = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            vfa__srqb = df_typ.table_type.type_to_blk[data_typ]
            fxek__ywbi = getattr(wgzia__hkn, f'block_{vfa__srqb}')
            qxo__coh = ListInstance(c.context, c.builder, types.List(
                data_typ), fxek__ywbi)
            kdrqp__zpjov = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[col_ind])
            qxo__coh.inititem(kdrqp__zpjov, pdpe__stiqw.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, pdpe__stiqw.value, col_ind)
        zqo__xwv = DataFramePayloadType(df_typ)
        wpu__znu = context.nrt.meminfo_data(builder, nczpq__emzmj.meminfo)
        mflu__bzm = context.get_value_type(zqo__xwv).as_pointer()
        wpu__znu = builder.bitcast(wpu__znu, mflu__bzm)
        builder.store(dataframe_payload._getvalue(), wpu__znu)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        rpsa__hjnh = c.pyapi.object_getattr_string(val, 'array')
    else:
        rpsa__hjnh = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        chtt__wwich = c.context.insert_const_string(c.builder.module, 'numpy')
        wgdk__etxvt = c.pyapi.import_module_noblock(chtt__wwich)
        arr_obj = c.pyapi.call_method(wgdk__etxvt, 'ascontiguousarray', (
            rpsa__hjnh,))
        c.pyapi.decref(rpsa__hjnh)
        c.pyapi.decref(wgdk__etxvt)
    else:
        arr_obj = rpsa__hjnh
    gkp__yxyb = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    slf__qgx = c.pyapi.object_getattr_string(val, 'index')
    rta__xsz = c.pyapi.to_native_value(typ.index, slf__qgx).value
    rsj__rlq = c.pyapi.object_getattr_string(val, 'name')
    ialrj__rhqdv = c.pyapi.to_native_value(typ.name_typ, rsj__rlq).value
    nyof__sehw = bodo.hiframes.pd_series_ext.construct_series(c.context, c.
        builder, typ, gkp__yxyb, rta__xsz, ialrj__rhqdv)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(slf__qgx)
    c.pyapi.decref(rsj__rlq)
    return NativeValue(nyof__sehw)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        qetg__abei = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(qetg__abei._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    dcytd__kew = c.context.insert_const_string(c.builder.module, 'pandas')
    uibmf__ceoc = c.pyapi.import_module_noblock(dcytd__kew)
    ypa__ynpoc = bodo.hiframes.pd_series_ext.get_series_payload(c.context,
        c.builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, ypa__ynpoc.data)
    c.context.nrt.incref(c.builder, typ.index, ypa__ynpoc.index)
    c.context.nrt.incref(c.builder, typ.name_typ, ypa__ynpoc.name)
    arr_obj = c.pyapi.from_native_value(typ.data, ypa__ynpoc.data, c.
        env_manager)
    slf__qgx = c.pyapi.from_native_value(typ.index, ypa__ynpoc.index, c.
        env_manager)
    rsj__rlq = c.pyapi.from_native_value(typ.name_typ, ypa__ynpoc.name, c.
        env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(uibmf__ceoc, 'Series', (arr_obj, slf__qgx,
        dtype, rsj__rlq))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(slf__qgx)
    c.pyapi.decref(rsj__rlq)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(uibmf__ceoc)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    ksivh__jtht = []
    for svlt__zlqlj in typ_list:
        if isinstance(svlt__zlqlj, int) and not isinstance(svlt__zlqlj, bool):
            gypnt__jygpc = pyapi.long_from_longlong(lir.Constant(lir.
                IntType(64), svlt__zlqlj))
        else:
            oskgs__bhp = numba.typeof(svlt__zlqlj)
            unotw__yxij = context.get_constant_generic(builder, oskgs__bhp,
                svlt__zlqlj)
            gypnt__jygpc = pyapi.from_native_value(oskgs__bhp, unotw__yxij,
                env_manager)
        ksivh__jtht.append(gypnt__jygpc)
    gbyv__lykfn = pyapi.list_pack(ksivh__jtht)
    for val in ksivh__jtht:
        pyapi.decref(val)
    return gbyv__lykfn


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    ftyr__pnd = not typ.has_runtime_cols and (not typ.is_table_format or 
        len(typ.columns) < TABLE_FORMAT_THRESHOLD)
    isa__ajmn = 2 if ftyr__pnd else 1
    kex__mcz = pyapi.dict_new(isa__ajmn)
    rbcio__rpvo = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    pyapi.dict_setitem_string(kex__mcz, 'dist', rbcio__rpvo)
    pyapi.decref(rbcio__rpvo)
    if ftyr__pnd:
        omil__uhvx = _dtype_to_type_enum_list(typ.index)
        if omil__uhvx != None:
            uqa__doj = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, omil__uhvx)
        else:
            uqa__doj = pyapi.make_none()
        zqxlb__nmepm = []
        for dtype in typ.data:
            typ_list = _dtype_to_type_enum_list(dtype)
            if typ_list != None:
                gbyv__lykfn = type_enum_list_to_py_list_obj(pyapi, context,
                    builder, c.env_manager, typ_list)
            else:
                gbyv__lykfn = pyapi.make_none()
            zqxlb__nmepm.append(gbyv__lykfn)
        qeuub__fyb = pyapi.list_pack(zqxlb__nmepm)
        zdgrs__dztrl = pyapi.list_pack([uqa__doj, qeuub__fyb])
        for val in zqxlb__nmepm:
            pyapi.decref(val)
        pyapi.dict_setitem_string(kex__mcz, 'type_metadata', zdgrs__dztrl)
    pyapi.object_setattr_string(obj, '_bodo_meta', kex__mcz)
    pyapi.decref(kex__mcz)


def get_series_dtype_handle_null_int_and_hetrogenous(series_typ):
    if isinstance(series_typ, HeterogeneousSeriesType):
        return None
    if isinstance(series_typ.dtype, types.Number) and isinstance(series_typ
        .data, IntegerArrayType):
        return IntDtype(series_typ.dtype)
    return series_typ.dtype


def _set_bodo_meta_series(obj, c, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    kex__mcz = pyapi.dict_new(2)
    rbcio__rpvo = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    omil__uhvx = _dtype_to_type_enum_list(typ.index)
    if omil__uhvx != None:
        uqa__doj = type_enum_list_to_py_list_obj(pyapi, context, builder, c
            .env_manager, omil__uhvx)
    else:
        uqa__doj = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            vmr__bcbca = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            vmr__bcbca = pyapi.make_none()
    else:
        vmr__bcbca = pyapi.make_none()
    miyj__ppdf = pyapi.list_pack([uqa__doj, vmr__bcbca])
    pyapi.dict_setitem_string(kex__mcz, 'type_metadata', miyj__ppdf)
    pyapi.decref(miyj__ppdf)
    pyapi.dict_setitem_string(kex__mcz, 'dist', rbcio__rpvo)
    pyapi.object_setattr_string(obj, '_bodo_meta', kex__mcz)
    pyapi.decref(kex__mcz)
    pyapi.decref(rbcio__rpvo)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as fyyu__ccah:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    nbxpm__cqmui = numba.np.numpy_support.map_layout(val)
    ibr__nni = not val.flags.writeable
    return types.Array(dtype, val.ndim, nbxpm__cqmui, readonly=ibr__nni)


def _infer_ndarray_obj_dtype(val):
    if not val.dtype == np.dtype('O'):
        raise BodoError('Unsupported array dtype: {}'.format(val.dtype))
    i = 0
    while i < len(val) and (pd.api.types.is_scalar(val[i]) and pd.isna(val[
        i]) or not pd.api.types.is_scalar(val[i]) and len(val[i]) == 0):
        i += 1
    if i == len(val):
        warnings.warn(BodoWarning(
            'Empty object array passed to Bodo, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    omyjy__bufc = val[i]
    if isinstance(omyjy__bufc, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(omyjy__bufc, bytes):
        return binary_array_type
    elif isinstance(omyjy__bufc, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(omyjy__bufc, (int, np.int8, np.int16, np.int32, np.
        int64, np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(omyjy__bufc)
            )
    elif isinstance(omyjy__bufc, (dict, Dict)) and all(isinstance(
        xvdes__dfx, str) for xvdes__dfx in omyjy__bufc.keys()):
        wfcid__qzid = tuple(omyjy__bufc.keys())
        qkd__iav = tuple(_get_struct_value_arr_type(v) for v in omyjy__bufc
            .values())
        return StructArrayType(qkd__iav, wfcid__qzid)
    elif isinstance(omyjy__bufc, (dict, Dict)):
        vxy__lka = numba.typeof(_value_to_array(list(omyjy__bufc.keys())))
        ffiu__ltge = numba.typeof(_value_to_array(list(omyjy__bufc.values())))
        vxy__lka = to_str_arr_if_dict_array(vxy__lka)
        ffiu__ltge = to_str_arr_if_dict_array(ffiu__ltge)
        return MapArrayType(vxy__lka, ffiu__ltge)
    elif isinstance(omyjy__bufc, tuple):
        qkd__iav = tuple(_get_struct_value_arr_type(v) for v in omyjy__bufc)
        return TupleArrayType(qkd__iav)
    if isinstance(omyjy__bufc, (list, np.ndarray, pd.arrays.BooleanArray,
        pd.arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(omyjy__bufc, list):
            omyjy__bufc = _value_to_array(omyjy__bufc)
        qqvqx__aywwr = numba.typeof(omyjy__bufc)
        qqvqx__aywwr = to_str_arr_if_dict_array(qqvqx__aywwr)
        return ArrayItemArrayType(qqvqx__aywwr)
    if isinstance(omyjy__bufc, datetime.date):
        return datetime_date_array_type
    if isinstance(omyjy__bufc, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(omyjy__bufc, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(omyjy__bufc, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(f'Unsupported object array with first value: {omyjy__bufc}'
        )


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    iza__tohsz = val.copy()
    iza__tohsz.append(None)
    nylgj__ojz = np.array(iza__tohsz, np.object_)
    if len(val) and isinstance(val[0], float):
        nylgj__ojz = np.array(val, np.float64)
    return nylgj__ojz


def _get_struct_value_arr_type(v):
    if isinstance(v, (dict, Dict)):
        return numba.typeof(_value_to_array(v))
    if isinstance(v, list):
        return dtype_to_array_type(numba.typeof(_value_to_array(v)))
    if pd.api.types.is_scalar(v) and pd.isna(v):
        warnings.warn(BodoWarning(
            'Field value in struct array is NA, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return string_array_type
    kvsw__bzm = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        kvsw__bzm = to_nullable_type(kvsw__bzm)
    return kvsw__bzm
