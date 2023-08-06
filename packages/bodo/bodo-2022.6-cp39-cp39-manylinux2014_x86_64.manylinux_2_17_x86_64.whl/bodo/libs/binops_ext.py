""" Implementation of binary operators for the different types.
    Currently implemented operators:
        arith: add, sub, mul, truediv, floordiv, mod, pow
        cmp: lt, le, eq, ne, ge, gt
"""
import operator
import numba
from numba.core import types
from numba.core.imputils import lower_builtin
from numba.core.typing.builtins import machine_ints
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type, datetime_date_type, datetime_timedelta_type
from bodo.hiframes.datetime_timedelta_ext import datetime_datetime_type, datetime_timedelta_array_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import DatetimeIndexType, HeterogeneousIndexType, is_index_type
from bodo.hiframes.pd_offsets_ext import date_offset_type, month_begin_type, month_end_type, week_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.series_impl import SeriesType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_ext import string_type
from bodo.utils.typing import BodoError, is_overload_bool, is_str_arr_type, is_timedelta_type


class SeriesCmpOpTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        lhs, rhs = args
        if cmp_timeseries(lhs, rhs) or (isinstance(lhs, DataFrameType) or
            isinstance(rhs, DataFrameType)) or not (isinstance(lhs,
            SeriesType) or isinstance(rhs, SeriesType)):
            return
        iahx__vwvku = lhs.data if isinstance(lhs, SeriesType) else lhs
        iovz__rana = rhs.data if isinstance(rhs, SeriesType) else rhs
        if iahx__vwvku in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and iovz__rana.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            iahx__vwvku = iovz__rana.dtype
        elif iovz__rana in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and iahx__vwvku.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            iovz__rana = iahx__vwvku.dtype
        chn__nna = iahx__vwvku, iovz__rana
        gspo__gjkql = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            ocx__imn = self.context.resolve_function_type(self.key,
                chn__nna, {}).return_type
        except Exception as jwtz__gba:
            raise BodoError(gspo__gjkql)
        if is_overload_bool(ocx__imn):
            raise BodoError(gspo__gjkql)
        hwbsx__tmo = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        qll__nug = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        gft__kin = types.bool_
        cqly__mmc = SeriesType(gft__kin, ocx__imn, hwbsx__tmo, qll__nug)
        return cqly__mmc(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        mtbpl__bym = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if mtbpl__bym is None:
            mtbpl__bym = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, mtbpl__bym, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        iahx__vwvku = lhs.data if isinstance(lhs, SeriesType) else lhs
        iovz__rana = rhs.data if isinstance(rhs, SeriesType) else rhs
        chn__nna = iahx__vwvku, iovz__rana
        gspo__gjkql = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            ocx__imn = self.context.resolve_function_type(self.key,
                chn__nna, {}).return_type
        except Exception as vgyh__gmjf:
            raise BodoError(gspo__gjkql)
        hwbsx__tmo = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        qll__nug = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        gft__kin = ocx__imn.dtype
        cqly__mmc = SeriesType(gft__kin, ocx__imn, hwbsx__tmo, qll__nug)
        return cqly__mmc(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        mtbpl__bym = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if mtbpl__bym is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                mtbpl__bym = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, mtbpl__bym, sig, args)
    return lower_and_or_impl


def overload_add_operator_scalars(lhs, rhs):
    if lhs == week_type or rhs == week_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_week_offset_type(lhs, rhs))
    if lhs == month_begin_type or rhs == month_begin_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_begin_offset_type(lhs, rhs))
    if lhs == month_end_type or rhs == month_end_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_end_offset_type(lhs, rhs))
    if lhs == date_offset_type or rhs == date_offset_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_date_offset_type(lhs, rhs))
    if add_timestamp(lhs, rhs):
        return bodo.hiframes.pd_timestamp_ext.overload_add_operator_timestamp(
            lhs, rhs)
    if add_dt_td_and_dt_date(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_add_operator_datetime_date(lhs, rhs))
    if add_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_add_operator_datetime_timedelta(lhs, rhs))
    raise_error_if_not_numba_supported(operator.add, lhs, rhs)


def overload_sub_operator_scalars(lhs, rhs):
    if sub_offset_to_datetime_or_timestamp(lhs, rhs):
        return bodo.hiframes.pd_offsets_ext.overload_sub_operator_offsets(lhs,
            rhs)
    if lhs == pd_timestamp_type and rhs in [pd_timestamp_type,
        datetime_timedelta_type, pd_timedelta_type]:
        return bodo.hiframes.pd_timestamp_ext.overload_sub_operator_timestamp(
            lhs, rhs)
    if sub_dt_or_td(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_sub_operator_datetime_date(lhs, rhs))
    if sub_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_sub_operator_datetime_timedelta(lhs, rhs))
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
        return (bodo.hiframes.datetime_datetime_ext.
            overload_sub_operator_datetime_datetime(lhs, rhs))
    raise_error_if_not_numba_supported(operator.sub, lhs, rhs)


def create_overload_arith_op(op):

    def overload_arith_operator(lhs, rhs):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
            f'{op} operator')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
            f'{op} operator')
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if time_series_operation(lhs, rhs) and op in [operator.add,
            operator.sub]:
            return bodo.hiframes.series_dt_impl.create_bin_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return bodo.hiframes.series_impl.create_binary_op_overload(op)(lhs,
                rhs)
        if sub_dt_index_and_timestamp(lhs, rhs) and op == operator.sub:
            return (bodo.hiframes.pd_index_ext.
                overload_sub_operator_datetime_index(lhs, rhs))
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if args_td_and_int_array(lhs, rhs):
            return bodo.libs.int_arr_ext.get_int_array_op_pd_td(op)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if op == operator.add and (is_str_arr_type(lhs) or types.unliteral(
            lhs) == string_type):
            return bodo.libs.str_arr_ext.overload_add_operator_string_array(lhs
                , rhs)
        if op == operator.add:
            return overload_add_operator_scalars(lhs, rhs)
        if op == operator.sub:
            return overload_sub_operator_scalars(lhs, rhs)
        if op == operator.mul:
            if mul_timedelta_and_int(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mul_operator_timedelta(lhs, rhs))
            if mul_string_arr_and_int(lhs, rhs):
                return bodo.libs.str_arr_ext.overload_mul_operator_str_arr(lhs,
                    rhs)
            if mul_date_offset_and_int(lhs, rhs):
                return (bodo.hiframes.pd_offsets_ext.
                    overload_mul_date_offset_types(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op in [operator.truediv, operator.floordiv]:
            if div_timedelta_and_int(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_pd_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_pd_timedelta(lhs, rhs))
            if div_datetime_timedelta(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_dt_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_dt_timedelta(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.mod:
            if mod_timedeltas(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mod_operator_timedeltas(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.pow:
            raise_error_if_not_numba_supported(op, lhs, rhs)
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_arith_operator


def create_overload_cmp_operator(op):

    def overload_cmp_operator(lhs, rhs):
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
                f'{op} operator')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
                f'{op} operator')
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if cmp_timeseries(lhs, rhs):
            return bodo.hiframes.series_dt_impl.create_cmp_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
            f'{op} operator')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
            f'{op} operator')
        if lhs == datetime_date_array_type or rhs == datetime_date_array_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload_arr(
                op)(lhs, rhs)
        if (lhs == datetime_timedelta_array_type or rhs ==
            datetime_timedelta_array_type):
            mtbpl__bym = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return mtbpl__bym(lhs, rhs)
        if is_str_arr_type(lhs) or is_str_arr_type(rhs):
            return bodo.libs.str_arr_ext.create_binary_op_overload(op)(lhs, rhs
                )
        if isinstance(lhs, Decimal128Type) and isinstance(rhs, Decimal128Type):
            return bodo.libs.decimal_arr_ext.decimal_create_cmp_op_overload(op
                )(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if binary_array_cmp(lhs, rhs):
            return bodo.libs.binary_arr_ext.create_binary_cmp_op_overload(op)(
                lhs, rhs)
        if cmp_dt_index_to_string(lhs, rhs):
            return bodo.hiframes.pd_index_ext.overload_binop_dti_str(op)(lhs,
                rhs)
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if lhs == datetime_date_type and rhs == datetime_date_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload(op)(
                lhs, rhs)
        if can_cmp_date_datetime(lhs, rhs, op):
            return (bodo.hiframes.datetime_date_ext.
                create_datetime_date_cmp_op_overload(op)(lhs, rhs))
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
            return bodo.hiframes.datetime_datetime_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:
            return bodo.hiframes.datetime_timedelta_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if cmp_timedeltas(lhs, rhs):
            mtbpl__bym = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return mtbpl__bym(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    pjpk__fjgks = lhs == datetime_timedelta_type and rhs == datetime_date_type
    aqu__jnjh = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return pjpk__fjgks or aqu__jnjh


def add_timestamp(lhs, rhs):
    pgd__qxmht = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    kfzyb__tsuin = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return pgd__qxmht or kfzyb__tsuin


def add_datetime_and_timedeltas(lhs, rhs):
    hms__pwuoz = [datetime_timedelta_type, pd_timedelta_type]
    mpp__fdlfw = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    rnb__zzlv = lhs in hms__pwuoz and rhs in hms__pwuoz
    wnkv__qhvw = (lhs == datetime_datetime_type and rhs in hms__pwuoz or 
        rhs == datetime_datetime_type and lhs in hms__pwuoz)
    return rnb__zzlv or wnkv__qhvw


def mul_string_arr_and_int(lhs, rhs):
    iovz__rana = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    iahx__vwvku = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return iovz__rana or iahx__vwvku


def mul_timedelta_and_int(lhs, rhs):
    pjpk__fjgks = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    aqu__jnjh = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return pjpk__fjgks or aqu__jnjh


def mul_date_offset_and_int(lhs, rhs):
    amqct__lphe = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    dak__crk = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return amqct__lphe or dak__crk


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    lit__syq = [datetime_datetime_type, pd_timestamp_type, datetime_date_type]
    exd__xmr = [date_offset_type, month_begin_type, month_end_type, week_type]
    return rhs in exd__xmr and lhs in lit__syq


def sub_dt_index_and_timestamp(lhs, rhs):
    twhky__myrp = isinstance(lhs, DatetimeIndexType
        ) and rhs == pd_timestamp_type
    rhex__rui = isinstance(rhs, DatetimeIndexType) and lhs == pd_timestamp_type
    return twhky__myrp or rhex__rui


def sub_dt_or_td(lhs, rhs):
    nplnx__lhkp = lhs == datetime_date_type and rhs == datetime_timedelta_type
    nzwm__kok = lhs == datetime_date_type and rhs == datetime_date_type
    fkpcg__lnioe = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return nplnx__lhkp or nzwm__kok or fkpcg__lnioe


def sub_datetime_and_timedeltas(lhs, rhs):
    bulyh__ylqys = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    rrz__jeex = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return bulyh__ylqys or rrz__jeex


def div_timedelta_and_int(lhs, rhs):
    rnb__zzlv = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    kfcc__nfve = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return rnb__zzlv or kfcc__nfve


def div_datetime_timedelta(lhs, rhs):
    rnb__zzlv = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    kfcc__nfve = lhs == datetime_timedelta_type and rhs == types.int64
    return rnb__zzlv or kfcc__nfve


def mod_timedeltas(lhs, rhs):
    ppbht__ghkhm = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    scx__fte = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return ppbht__ghkhm or scx__fte


def cmp_dt_index_to_string(lhs, rhs):
    twhky__myrp = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    rhex__rui = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return twhky__myrp or rhex__rui


def cmp_timestamp_or_date(lhs, rhs):
    tbqm__zjf = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    ejcek__imhlq = (lhs == bodo.hiframes.datetime_date_ext.
        datetime_date_type and rhs == pd_timestamp_type)
    nneaz__qvsg = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    gqh__gnmqt = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    rtify__tuot = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return (tbqm__zjf or ejcek__imhlq or nneaz__qvsg or gqh__gnmqt or
        rtify__tuot)


def cmp_timeseries(lhs, rhs):
    ejal__kmpzw = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    uej__xdbx = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    wbitw__szic = ejal__kmpzw or uej__xdbx
    wpgh__cuv = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    epubm__serjo = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    ptclt__msl = wpgh__cuv or epubm__serjo
    return wbitw__szic or ptclt__msl


def cmp_timedeltas(lhs, rhs):
    rnb__zzlv = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in rnb__zzlv and rhs in rnb__zzlv


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    hvk__elmt = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return hvk__elmt


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    pwj__kme = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    pyepz__rwtn = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    edhvq__yvfr = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    mvue__ypo = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return pwj__kme or pyepz__rwtn or edhvq__yvfr or mvue__ypo


def args_td_and_int_array(lhs, rhs):
    bwpvg__iwrl = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    bnmg__ylcj = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return bwpvg__iwrl and bnmg__ylcj


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        aqu__jnjh = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        pjpk__fjgks = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        pti__itht = aqu__jnjh or pjpk__fjgks
        wkpr__fvysh = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        jtjb__dyjtz = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        pnxgr__wkp = wkpr__fvysh or jtjb__dyjtz
        zjep__hlor = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        pvlj__zhlix = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        qaoz__ibca = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        idtqf__mbl = zjep__hlor or pvlj__zhlix or qaoz__ibca
        ifzo__syfh = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        ugtqd__dlqf = isinstance(lhs, tys) or isinstance(rhs, tys)
        bie__cuhf = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (pti__itht or pnxgr__wkp or idtqf__mbl or ifzo__syfh or
            ugtqd__dlqf or bie__cuhf)
    if op == operator.pow:
        pavh__fsm = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        jhejd__yjqhk = isinstance(lhs, types.Float) and isinstance(rhs, (
            types.IntegerLiteral, types.Float, types.Integer) or rhs in
            types.unsigned_domain or rhs in types.signed_domain)
        qaoz__ibca = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        bie__cuhf = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return pavh__fsm or jhejd__yjqhk or qaoz__ibca or bie__cuhf
    if op == operator.floordiv:
        pvlj__zhlix = lhs in types.real_domain and rhs in types.real_domain
        zjep__hlor = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        urwfd__tiv = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        rnb__zzlv = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        bie__cuhf = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (pvlj__zhlix or zjep__hlor or urwfd__tiv or rnb__zzlv or
            bie__cuhf)
    if op == operator.truediv:
        tazl__lzilf = lhs in machine_ints and rhs in machine_ints
        pvlj__zhlix = lhs in types.real_domain and rhs in types.real_domain
        qaoz__ibca = (lhs in types.complex_domain and rhs in types.
            complex_domain)
        zjep__hlor = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        urwfd__tiv = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        srl__bkigj = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        rnb__zzlv = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        bie__cuhf = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (tazl__lzilf or pvlj__zhlix or qaoz__ibca or zjep__hlor or
            urwfd__tiv or srl__bkigj or rnb__zzlv or bie__cuhf)
    if op == operator.mod:
        tazl__lzilf = lhs in machine_ints and rhs in machine_ints
        pvlj__zhlix = lhs in types.real_domain and rhs in types.real_domain
        zjep__hlor = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        urwfd__tiv = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        bie__cuhf = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (tazl__lzilf or pvlj__zhlix or zjep__hlor or urwfd__tiv or
            bie__cuhf)
    if op == operator.add or op == operator.sub:
        pti__itht = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        ixc__zzilq = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        qelfy__rkr = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        uml__wol = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        zjep__hlor = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        pvlj__zhlix = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        qaoz__ibca = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        idtqf__mbl = zjep__hlor or pvlj__zhlix or qaoz__ibca
        bie__cuhf = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        lnm__aio = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        ifzo__syfh = isinstance(lhs, types.List) and isinstance(rhs, types.List
            )
        hifu__bwcm = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        meeiz__igpu = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        mdo__mur = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        gdij__fudx = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        iwghx__whus = hifu__bwcm or meeiz__igpu or mdo__mur or gdij__fudx
        pnxgr__wkp = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        ymeb__jatds = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        wyu__ixjb = pnxgr__wkp or ymeb__jatds
        gvy__kje = lhs == types.NPTimedelta and rhs == types.NPDatetime
        nea__qxwnd = (lnm__aio or ifzo__syfh or iwghx__whus or wyu__ixjb or
            gvy__kje)
        qxeyq__dss = op == operator.add and nea__qxwnd
        return (pti__itht or ixc__zzilq or qelfy__rkr or uml__wol or
            idtqf__mbl or bie__cuhf or qxeyq__dss)


def cmp_op_supported_by_numba(lhs, rhs):
    bie__cuhf = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    ifzo__syfh = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    pti__itht = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    nhmfi__xodlq = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
        types.NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    pnxgr__wkp = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    lnm__aio = isinstance(lhs, types.BaseTuple) and isinstance(rhs, types.
        BaseTuple)
    uml__wol = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    idtqf__mbl = isinstance(lhs, types.Number) and isinstance(rhs, types.Number
        )
    kmjo__wng = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    vheh__soi = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    kdl__olwfv = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    kqowb__elatb = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    iigxz__budv = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (ifzo__syfh or pti__itht or nhmfi__xodlq or pnxgr__wkp or
        lnm__aio or uml__wol or idtqf__mbl or kmjo__wng or vheh__soi or
        kdl__olwfv or bie__cuhf or kqowb__elatb or iigxz__budv)


def raise_error_if_not_numba_supported(op, lhs, rhs):
    if arith_op_supported_by_numba(op, lhs, rhs):
        return
    raise BodoError(
        f'{op} operator not supported for data types {lhs} and {rhs}.')


def _install_series_and_or():
    for op in (operator.or_, operator.and_):
        infer_global(op)(SeriesAndOrTyper)
        lower_impl = lower_series_and_or(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)


_install_series_and_or()


def _install_cmp_ops():
    for op in (operator.lt, operator.eq, operator.ne, operator.ge, operator
        .gt, operator.le):
        infer_global(op)(SeriesCmpOpTemplate)
        lower_impl = series_cmp_op_lower(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)
        roe__mfr = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(roe__mfr)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        roe__mfr = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(roe__mfr)


install_arith_ops()
