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
    mbji__irr = tuple(val.columns.to_list())
    hmanz__bqvfg = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        qhmsl__onk = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        qhmsl__onk = numba.typeof(val.index)
    eyf__sax = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    yiw__neuoc = len(hmanz__bqvfg) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(hmanz__bqvfg, qhmsl__onk, mbji__irr, eyf__sax,
        is_table_format=yiw__neuoc)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    eyf__sax = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        tqdqb__huqjn = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        tqdqb__huqjn = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    jksdc__sciu = dtype_to_array_type(dtype)
    if _use_dict_str_type and jksdc__sciu == string_array_type:
        jksdc__sciu = bodo.dict_str_arr_type
    return SeriesType(dtype, data=jksdc__sciu, index=tqdqb__huqjn, name_typ
        =numba.typeof(val.name), dist=eyf__sax)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    uof__vos = c.pyapi.object_getattr_string(val, 'index')
    yzozg__bhr = c.pyapi.to_native_value(typ.index, uof__vos).value
    c.pyapi.decref(uof__vos)
    if typ.is_table_format:
        afq__ghfn = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        afq__ghfn.parent = val
        for kpjlo__twg, ycojx__fdckl in typ.table_type.type_to_blk.items():
            bofoh__uum = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[ycojx__fdckl]))
            vsslh__wnkz, waq__hof = ListInstance.allocate_ex(c.context, c.
                builder, types.List(kpjlo__twg), bofoh__uum)
            waq__hof.size = bofoh__uum
            setattr(afq__ghfn, f'block_{ycojx__fdckl}', waq__hof.value)
        kse__cmrh = c.pyapi.call_method(val, '__len__', ())
        vznj__lkyk = c.pyapi.long_as_longlong(kse__cmrh)
        c.pyapi.decref(kse__cmrh)
        afq__ghfn.len = vznj__lkyk
        ixhq__vvd = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [afq__ghfn._getvalue()])
    else:
        vwsi__oku = [c.context.get_constant_null(kpjlo__twg) for kpjlo__twg in
            typ.data]
        ixhq__vvd = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            vwsi__oku)
    nidu__ktpjm = construct_dataframe(c.context, c.builder, typ, ixhq__vvd,
        yzozg__bhr, val, None)
    return NativeValue(nidu__ktpjm)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        etn__qefom = df._bodo_meta['type_metadata'][1]
    else:
        etn__qefom = [None] * len(df.columns)
    mese__javv = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=etn__qefom[i])) for i in range(len(df.columns))]
    mese__javv = [(bodo.dict_str_arr_type if _use_dict_str_type and 
        kpjlo__twg == string_array_type else kpjlo__twg) for kpjlo__twg in
        mese__javv]
    return tuple(mese__javv)


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
    mtnkm__lqvkv, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(mtnkm__lqvkv) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {mtnkm__lqvkv}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        svcmq__rlho, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return svcmq__rlho, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        svcmq__rlho, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return svcmq__rlho, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        spy__gpwc = typ_enum_list[1]
        yrbcl__eejjt = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(spy__gpwc, yrbcl__eejjt)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        vzxd__zfjyl = typ_enum_list[1]
        qqt__ojia = tuple(typ_enum_list[2:2 + vzxd__zfjyl])
        qwm__tydpw = typ_enum_list[2 + vzxd__zfjyl:]
        kxurt__sqsr = []
        for i in range(vzxd__zfjyl):
            qwm__tydpw, sud__mll = _dtype_from_type_enum_list_recursor(
                qwm__tydpw)
            kxurt__sqsr.append(sud__mll)
        return qwm__tydpw, StructType(tuple(kxurt__sqsr), qqt__ojia)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        yflzs__wfnm = typ_enum_list[1]
        qwm__tydpw = typ_enum_list[2:]
        return qwm__tydpw, yflzs__wfnm
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        yflzs__wfnm = typ_enum_list[1]
        qwm__tydpw = typ_enum_list[2:]
        return qwm__tydpw, numba.types.literal(yflzs__wfnm)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        qwm__tydpw, hhw__tys = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        qwm__tydpw, txvrl__gwaqu = _dtype_from_type_enum_list_recursor(
            qwm__tydpw)
        qwm__tydpw, dcxjn__zvilg = _dtype_from_type_enum_list_recursor(
            qwm__tydpw)
        qwm__tydpw, fpayy__onp = _dtype_from_type_enum_list_recursor(qwm__tydpw
            )
        qwm__tydpw, osf__fjb = _dtype_from_type_enum_list_recursor(qwm__tydpw)
        return qwm__tydpw, PDCategoricalDtype(hhw__tys, txvrl__gwaqu,
            dcxjn__zvilg, fpayy__onp, osf__fjb)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        qwm__tydpw, efio__jleal = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return qwm__tydpw, DatetimeIndexType(efio__jleal)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        qwm__tydpw, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        qwm__tydpw, efio__jleal = _dtype_from_type_enum_list_recursor(
            qwm__tydpw)
        qwm__tydpw, fpayy__onp = _dtype_from_type_enum_list_recursor(qwm__tydpw
            )
        return qwm__tydpw, NumericIndexType(dtype, efio__jleal, fpayy__onp)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        qwm__tydpw, srq__tld = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        qwm__tydpw, efio__jleal = _dtype_from_type_enum_list_recursor(
            qwm__tydpw)
        return qwm__tydpw, PeriodIndexType(srq__tld, efio__jleal)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        qwm__tydpw, fpayy__onp = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        qwm__tydpw, efio__jleal = _dtype_from_type_enum_list_recursor(
            qwm__tydpw)
        return qwm__tydpw, CategoricalIndexType(fpayy__onp, efio__jleal)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        qwm__tydpw, efio__jleal = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return qwm__tydpw, RangeIndexType(efio__jleal)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        qwm__tydpw, efio__jleal = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return qwm__tydpw, StringIndexType(efio__jleal)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        qwm__tydpw, efio__jleal = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return qwm__tydpw, BinaryIndexType(efio__jleal)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        qwm__tydpw, efio__jleal = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return qwm__tydpw, TimedeltaIndexType(efio__jleal)
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
        ruwgb__puv = get_overload_const_int(typ)
        if numba.types.maybe_literal(ruwgb__puv) == typ:
            return [SeriesDtypeEnum.LiteralType.value, ruwgb__puv]
    elif is_overload_constant_str(typ):
        ruwgb__puv = get_overload_const_str(typ)
        if numba.types.maybe_literal(ruwgb__puv) == typ:
            return [SeriesDtypeEnum.LiteralType.value, ruwgb__puv]
    elif is_overload_constant_bool(typ):
        ruwgb__puv = get_overload_const_bool(typ)
        if numba.types.maybe_literal(ruwgb__puv) == typ:
            return [SeriesDtypeEnum.LiteralType.value, ruwgb__puv]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        gdqo__euwtx = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for fyibi__yap in typ.names:
            gdqo__euwtx.append(fyibi__yap)
        for ppjll__qcif in typ.data:
            gdqo__euwtx += _dtype_to_type_enum_list_recursor(ppjll__qcif)
        return gdqo__euwtx
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        wec__pwwt = _dtype_to_type_enum_list_recursor(typ.categories)
        qrq__yrz = _dtype_to_type_enum_list_recursor(typ.elem_type)
        tsf__bdrv = _dtype_to_type_enum_list_recursor(typ.ordered)
        sqku__qmejo = _dtype_to_type_enum_list_recursor(typ.data)
        tzmlz__xap = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + wec__pwwt + qrq__yrz + tsf__bdrv + sqku__qmejo + tzmlz__xap
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                xeta__cgon = types.float64
                pjq__ytfg = types.Array(xeta__cgon, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                xeta__cgon = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    pjq__ytfg = IntegerArrayType(xeta__cgon)
                else:
                    pjq__ytfg = types.Array(xeta__cgon, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                xeta__cgon = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    pjq__ytfg = IntegerArrayType(xeta__cgon)
                else:
                    pjq__ytfg = types.Array(xeta__cgon, 1, 'C')
            elif typ.dtype == types.bool_:
                xeta__cgon = typ.dtype
                pjq__ytfg = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(xeta__cgon
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(pjq__ytfg)
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
                gwc__jafx = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(gwc__jafx)
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
        oofgk__gkidp = S.dtype.unit
        if oofgk__gkidp != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        ctciz__rpnnq = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.
            dtype.tz)
        return PandasDatetimeTZDtype(ctciz__rpnnq)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    tpzn__mzy = cgutils.is_not_null(builder, parent_obj)
    giqxo__qjvgh = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(tpzn__mzy):
        cza__pmw = pyapi.object_getattr_string(parent_obj, 'columns')
        kse__cmrh = pyapi.call_method(cza__pmw, '__len__', ())
        builder.store(pyapi.long_as_longlong(kse__cmrh), giqxo__qjvgh)
        pyapi.decref(kse__cmrh)
        pyapi.decref(cza__pmw)
    use_parent_obj = builder.and_(tpzn__mzy, builder.icmp_unsigned('==',
        builder.load(giqxo__qjvgh), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        oleqj__gau = df_typ.runtime_colname_typ
        context.nrt.incref(builder, oleqj__gau, dataframe_payload.columns)
        return pyapi.from_native_value(oleqj__gau, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        ytp__sdloz = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        ytp__sdloz = np.array(df_typ.columns, 'int64')
    else:
        ytp__sdloz = df_typ.columns
    bohg__qsr = numba.typeof(ytp__sdloz)
    apuma__lyz = context.get_constant_generic(builder, bohg__qsr, ytp__sdloz)
    ztf__chli = pyapi.from_native_value(bohg__qsr, apuma__lyz, c.env_manager)
    return ztf__chli


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (lghd__kttz, wph__skf):
        with lghd__kttz:
            pyapi.incref(obj)
            zfhho__zzexo = context.insert_const_string(c.builder.module,
                'numpy')
            fsv__oqcq = pyapi.import_module_noblock(zfhho__zzexo)
            if df_typ.has_runtime_cols:
                hmor__pkau = 0
            else:
                hmor__pkau = len(df_typ.columns)
            mbeqz__jwyho = pyapi.long_from_longlong(lir.Constant(lir.
                IntType(64), hmor__pkau))
            wsian__gznd = pyapi.call_method(fsv__oqcq, 'arange', (
                mbeqz__jwyho,))
            pyapi.object_setattr_string(obj, 'columns', wsian__gznd)
            pyapi.decref(fsv__oqcq)
            pyapi.decref(wsian__gznd)
            pyapi.decref(mbeqz__jwyho)
        with wph__skf:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            avql__nzq = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            zfhho__zzexo = context.insert_const_string(c.builder.module,
                'pandas')
            fsv__oqcq = pyapi.import_module_noblock(zfhho__zzexo)
            df_obj = pyapi.call_method(fsv__oqcq, 'DataFrame', (pyapi.
                borrow_none(), avql__nzq))
            pyapi.decref(fsv__oqcq)
            pyapi.decref(avql__nzq)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    roq__mybl = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = roq__mybl.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        vthkx__hvt = typ.table_type
        afq__ghfn = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, vthkx__hvt, afq__ghfn)
        tuaou__zdtog = box_table(vthkx__hvt, afq__ghfn, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (rso__atj, bzsy__humbl):
            with rso__atj:
                iwdma__nixe = pyapi.object_getattr_string(tuaou__zdtog,
                    'arrays')
                byr__zlugk = c.pyapi.make_none()
                if n_cols is None:
                    kse__cmrh = pyapi.call_method(iwdma__nixe, '__len__', ())
                    bofoh__uum = pyapi.long_as_longlong(kse__cmrh)
                    pyapi.decref(kse__cmrh)
                else:
                    bofoh__uum = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, bofoh__uum) as upsxj__ojm:
                    i = upsxj__ojm.index
                    aje__bfko = pyapi.list_getitem(iwdma__nixe, i)
                    pyki__kzbgj = c.builder.icmp_unsigned('!=', aje__bfko,
                        byr__zlugk)
                    with builder.if_then(pyki__kzbgj):
                        wsub__aylbm = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, wsub__aylbm, aje__bfko)
                        pyapi.decref(wsub__aylbm)
                pyapi.decref(iwdma__nixe)
                pyapi.decref(byr__zlugk)
            with bzsy__humbl:
                df_obj = builder.load(res)
                avql__nzq = pyapi.object_getattr_string(df_obj, 'index')
                wgl__gxk = c.pyapi.call_method(tuaou__zdtog, 'to_pandas', (
                    avql__nzq,))
                builder.store(wgl__gxk, res)
                pyapi.decref(df_obj)
                pyapi.decref(avql__nzq)
        pyapi.decref(tuaou__zdtog)
    else:
        pzjyw__zfhkn = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        bscr__zrou = typ.data
        for i, ybdbl__kkvna, jksdc__sciu in zip(range(n_cols), pzjyw__zfhkn,
            bscr__zrou):
            omym__jujta = cgutils.alloca_once_value(builder, ybdbl__kkvna)
            sosi__izin = cgutils.alloca_once_value(builder, context.
                get_constant_null(jksdc__sciu))
            pyki__kzbgj = builder.not_(is_ll_eq(builder, omym__jujta,
                sosi__izin))
            ttx__kcyra = builder.or_(builder.not_(use_parent_obj), builder.
                and_(use_parent_obj, pyki__kzbgj))
            with builder.if_then(ttx__kcyra):
                wsub__aylbm = pyapi.long_from_longlong(context.get_constant
                    (types.int64, i))
                context.nrt.incref(builder, jksdc__sciu, ybdbl__kkvna)
                arr_obj = pyapi.from_native_value(jksdc__sciu, ybdbl__kkvna,
                    c.env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, wsub__aylbm, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(wsub__aylbm)
    df_obj = builder.load(res)
    ztf__chli = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', ztf__chli)
    pyapi.decref(ztf__chli)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    byr__zlugk = pyapi.borrow_none()
    ngz__oue = pyapi.unserialize(pyapi.serialize_object(slice))
    xyl__pvw = pyapi.call_function_objargs(ngz__oue, [byr__zlugk])
    dftno__psdj = pyapi.long_from_longlong(col_ind)
    spapq__wtuey = pyapi.tuple_pack([xyl__pvw, dftno__psdj])
    qxdt__jyqgb = pyapi.object_getattr_string(df_obj, 'iloc')
    xxml__buz = pyapi.object_getitem(qxdt__jyqgb, spapq__wtuey)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        uqp__othvz = pyapi.object_getattr_string(xxml__buz, 'array')
    else:
        uqp__othvz = pyapi.object_getattr_string(xxml__buz, 'values')
    if isinstance(data_typ, types.Array):
        apw__rac = context.insert_const_string(builder.module, 'numpy')
        eyma__pfoyn = pyapi.import_module_noblock(apw__rac)
        arr_obj = pyapi.call_method(eyma__pfoyn, 'ascontiguousarray', (
            uqp__othvz,))
        pyapi.decref(uqp__othvz)
        pyapi.decref(eyma__pfoyn)
    else:
        arr_obj = uqp__othvz
    pyapi.decref(ngz__oue)
    pyapi.decref(xyl__pvw)
    pyapi.decref(dftno__psdj)
    pyapi.decref(spapq__wtuey)
    pyapi.decref(qxdt__jyqgb)
    pyapi.decref(xxml__buz)
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
        roq__mybl = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            roq__mybl.parent, args[1], data_typ)
        dfsp__usi = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            afq__ghfn = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            ycojx__fdckl = df_typ.table_type.type_to_blk[data_typ]
            kfxke__fgg = getattr(afq__ghfn, f'block_{ycojx__fdckl}')
            qudug__gte = ListInstance(c.context, c.builder, types.List(
                data_typ), kfxke__fgg)
            szcaw__xvmvc = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[col_ind])
            qudug__gte.inititem(szcaw__xvmvc, dfsp__usi.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, dfsp__usi.value, col_ind)
        jhwt__oac = DataFramePayloadType(df_typ)
        jrc__bqgq = context.nrt.meminfo_data(builder, roq__mybl.meminfo)
        hadv__iymt = context.get_value_type(jhwt__oac).as_pointer()
        jrc__bqgq = builder.bitcast(jrc__bqgq, hadv__iymt)
        builder.store(dataframe_payload._getvalue(), jrc__bqgq)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        uqp__othvz = c.pyapi.object_getattr_string(val, 'array')
    else:
        uqp__othvz = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        apw__rac = c.context.insert_const_string(c.builder.module, 'numpy')
        eyma__pfoyn = c.pyapi.import_module_noblock(apw__rac)
        arr_obj = c.pyapi.call_method(eyma__pfoyn, 'ascontiguousarray', (
            uqp__othvz,))
        c.pyapi.decref(uqp__othvz)
        c.pyapi.decref(eyma__pfoyn)
    else:
        arr_obj = uqp__othvz
    nxdvu__suas = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    avql__nzq = c.pyapi.object_getattr_string(val, 'index')
    yzozg__bhr = c.pyapi.to_native_value(typ.index, avql__nzq).value
    ihce__uhcyv = c.pyapi.object_getattr_string(val, 'name')
    dabyy__dqx = c.pyapi.to_native_value(typ.name_typ, ihce__uhcyv).value
    qve__ndsbs = bodo.hiframes.pd_series_ext.construct_series(c.context, c.
        builder, typ, nxdvu__suas, yzozg__bhr, dabyy__dqx)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(avql__nzq)
    c.pyapi.decref(ihce__uhcyv)
    return NativeValue(qve__ndsbs)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        wgjy__ynnb = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(wgjy__ynnb._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    zfhho__zzexo = c.context.insert_const_string(c.builder.module, 'pandas')
    saza__kfpjj = c.pyapi.import_module_noblock(zfhho__zzexo)
    tug__jtn = bodo.hiframes.pd_series_ext.get_series_payload(c.context, c.
        builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, tug__jtn.data)
    c.context.nrt.incref(c.builder, typ.index, tug__jtn.index)
    c.context.nrt.incref(c.builder, typ.name_typ, tug__jtn.name)
    arr_obj = c.pyapi.from_native_value(typ.data, tug__jtn.data, c.env_manager)
    avql__nzq = c.pyapi.from_native_value(typ.index, tug__jtn.index, c.
        env_manager)
    ihce__uhcyv = c.pyapi.from_native_value(typ.name_typ, tug__jtn.name, c.
        env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(saza__kfpjj, 'Series', (arr_obj, avql__nzq,
        dtype, ihce__uhcyv))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(avql__nzq)
    c.pyapi.decref(ihce__uhcyv)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(saza__kfpjj)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    qjfdi__ksmgq = []
    for mbme__spdv in typ_list:
        if isinstance(mbme__spdv, int) and not isinstance(mbme__spdv, bool):
            glb__ppvo = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), mbme__spdv))
        else:
            aal__cdmhr = numba.typeof(mbme__spdv)
            iomr__ssvzg = context.get_constant_generic(builder, aal__cdmhr,
                mbme__spdv)
            glb__ppvo = pyapi.from_native_value(aal__cdmhr, iomr__ssvzg,
                env_manager)
        qjfdi__ksmgq.append(glb__ppvo)
    cypdu__chilx = pyapi.list_pack(qjfdi__ksmgq)
    for val in qjfdi__ksmgq:
        pyapi.decref(val)
    return cypdu__chilx


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    gedxx__frcc = not typ.has_runtime_cols and (not typ.is_table_format or 
        len(typ.columns) < TABLE_FORMAT_THRESHOLD)
    bkzt__ucm = 2 if gedxx__frcc else 1
    hkjd__lssp = pyapi.dict_new(bkzt__ucm)
    wryh__xkyr = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ
        .dist.value))
    pyapi.dict_setitem_string(hkjd__lssp, 'dist', wryh__xkyr)
    pyapi.decref(wryh__xkyr)
    if gedxx__frcc:
        upxkp__uzuy = _dtype_to_type_enum_list(typ.index)
        if upxkp__uzuy != None:
            pjfo__wxv = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, upxkp__uzuy)
        else:
            pjfo__wxv = pyapi.make_none()
        ispol__cai = []
        for dtype in typ.data:
            typ_list = _dtype_to_type_enum_list(dtype)
            if typ_list != None:
                cypdu__chilx = type_enum_list_to_py_list_obj(pyapi, context,
                    builder, c.env_manager, typ_list)
            else:
                cypdu__chilx = pyapi.make_none()
            ispol__cai.append(cypdu__chilx)
        fyv__whmyn = pyapi.list_pack(ispol__cai)
        lydm__fwgys = pyapi.list_pack([pjfo__wxv, fyv__whmyn])
        for val in ispol__cai:
            pyapi.decref(val)
        pyapi.dict_setitem_string(hkjd__lssp, 'type_metadata', lydm__fwgys)
    pyapi.object_setattr_string(obj, '_bodo_meta', hkjd__lssp)
    pyapi.decref(hkjd__lssp)


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
    hkjd__lssp = pyapi.dict_new(2)
    wryh__xkyr = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ
        .dist.value))
    upxkp__uzuy = _dtype_to_type_enum_list(typ.index)
    if upxkp__uzuy != None:
        pjfo__wxv = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, upxkp__uzuy)
    else:
        pjfo__wxv = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            isrrn__sege = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            isrrn__sege = pyapi.make_none()
    else:
        isrrn__sege = pyapi.make_none()
    svjz__oppz = pyapi.list_pack([pjfo__wxv, isrrn__sege])
    pyapi.dict_setitem_string(hkjd__lssp, 'type_metadata', svjz__oppz)
    pyapi.decref(svjz__oppz)
    pyapi.dict_setitem_string(hkjd__lssp, 'dist', wryh__xkyr)
    pyapi.object_setattr_string(obj, '_bodo_meta', hkjd__lssp)
    pyapi.decref(hkjd__lssp)
    pyapi.decref(wryh__xkyr)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as dvgk__plnae:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    yhvxr__zocga = numba.np.numpy_support.map_layout(val)
    jpsn__rybc = not val.flags.writeable
    return types.Array(dtype, val.ndim, yhvxr__zocga, readonly=jpsn__rybc)


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
    sngc__lwct = val[i]
    if isinstance(sngc__lwct, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(sngc__lwct, bytes):
        return binary_array_type
    elif isinstance(sngc__lwct, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(sngc__lwct, (int, np.int8, np.int16, np.int32, np.int64,
        np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(sngc__lwct))
    elif isinstance(sngc__lwct, (dict, Dict)) and all(isinstance(
        tqyrn__fcyy, str) for tqyrn__fcyy in sngc__lwct.keys()):
        qqt__ojia = tuple(sngc__lwct.keys())
        vfyg__ydq = tuple(_get_struct_value_arr_type(v) for v in sngc__lwct
            .values())
        return StructArrayType(vfyg__ydq, qqt__ojia)
    elif isinstance(sngc__lwct, (dict, Dict)):
        xpzw__uazs = numba.typeof(_value_to_array(list(sngc__lwct.keys())))
        rudlp__qpfmd = numba.typeof(_value_to_array(list(sngc__lwct.values())))
        xpzw__uazs = to_str_arr_if_dict_array(xpzw__uazs)
        rudlp__qpfmd = to_str_arr_if_dict_array(rudlp__qpfmd)
        return MapArrayType(xpzw__uazs, rudlp__qpfmd)
    elif isinstance(sngc__lwct, tuple):
        vfyg__ydq = tuple(_get_struct_value_arr_type(v) for v in sngc__lwct)
        return TupleArrayType(vfyg__ydq)
    if isinstance(sngc__lwct, (list, np.ndarray, pd.arrays.BooleanArray, pd
        .arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(sngc__lwct, list):
            sngc__lwct = _value_to_array(sngc__lwct)
        hor__usm = numba.typeof(sngc__lwct)
        hor__usm = to_str_arr_if_dict_array(hor__usm)
        return ArrayItemArrayType(hor__usm)
    if isinstance(sngc__lwct, datetime.date):
        return datetime_date_array_type
    if isinstance(sngc__lwct, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(sngc__lwct, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(sngc__lwct, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(f'Unsupported object array with first value: {sngc__lwct}')


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    tzou__mnugl = val.copy()
    tzou__mnugl.append(None)
    ybdbl__kkvna = np.array(tzou__mnugl, np.object_)
    if len(val) and isinstance(val[0], float):
        ybdbl__kkvna = np.array(val, np.float64)
    return ybdbl__kkvna


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
    jksdc__sciu = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        jksdc__sciu = to_nullable_type(jksdc__sciu)
    return jksdc__sciu
