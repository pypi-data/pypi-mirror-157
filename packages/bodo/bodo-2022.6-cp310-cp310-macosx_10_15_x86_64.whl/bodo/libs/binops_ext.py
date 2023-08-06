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
        jtvy__vqmy = lhs.data if isinstance(lhs, SeriesType) else lhs
        msavc__wlkjd = rhs.data if isinstance(rhs, SeriesType) else rhs
        if jtvy__vqmy in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and msavc__wlkjd.dtype in (bodo.datetime64ns, bodo.timedelta64ns
            ):
            jtvy__vqmy = msavc__wlkjd.dtype
        elif msavc__wlkjd in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and jtvy__vqmy.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            msavc__wlkjd = jtvy__vqmy.dtype
        whrzu__gco = jtvy__vqmy, msavc__wlkjd
        afisw__rkr = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            kasv__wrs = self.context.resolve_function_type(self.key,
                whrzu__gco, {}).return_type
        except Exception as uzra__cxcl:
            raise BodoError(afisw__rkr)
        if is_overload_bool(kasv__wrs):
            raise BodoError(afisw__rkr)
        llbwo__dak = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        dqj__rgtah = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        fjx__ecb = types.bool_
        heusx__qud = SeriesType(fjx__ecb, kasv__wrs, llbwo__dak, dqj__rgtah)
        return heusx__qud(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        lbvr__gxudp = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if lbvr__gxudp is None:
            lbvr__gxudp = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, lbvr__gxudp, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        jtvy__vqmy = lhs.data if isinstance(lhs, SeriesType) else lhs
        msavc__wlkjd = rhs.data if isinstance(rhs, SeriesType) else rhs
        whrzu__gco = jtvy__vqmy, msavc__wlkjd
        afisw__rkr = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            kasv__wrs = self.context.resolve_function_type(self.key,
                whrzu__gco, {}).return_type
        except Exception as ggd__jejz:
            raise BodoError(afisw__rkr)
        llbwo__dak = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        dqj__rgtah = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        fjx__ecb = kasv__wrs.dtype
        heusx__qud = SeriesType(fjx__ecb, kasv__wrs, llbwo__dak, dqj__rgtah)
        return heusx__qud(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        lbvr__gxudp = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if lbvr__gxudp is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                lbvr__gxudp = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, lbvr__gxudp, sig, args)
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
            lbvr__gxudp = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return lbvr__gxudp(lhs, rhs)
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
            lbvr__gxudp = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return lbvr__gxudp(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    vvlbh__qgw = lhs == datetime_timedelta_type and rhs == datetime_date_type
    xhzqr__lvr = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return vvlbh__qgw or xhzqr__lvr


def add_timestamp(lhs, rhs):
    whhm__ezo = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    jpjvg__bxd = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return whhm__ezo or jpjvg__bxd


def add_datetime_and_timedeltas(lhs, rhs):
    tmxzi__cwh = [datetime_timedelta_type, pd_timedelta_type]
    iovbg__nkeiz = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    srmks__zlc = lhs in tmxzi__cwh and rhs in tmxzi__cwh
    wpq__jadl = (lhs == datetime_datetime_type and rhs in tmxzi__cwh or rhs ==
        datetime_datetime_type and lhs in tmxzi__cwh)
    return srmks__zlc or wpq__jadl


def mul_string_arr_and_int(lhs, rhs):
    msavc__wlkjd = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    jtvy__vqmy = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return msavc__wlkjd or jtvy__vqmy


def mul_timedelta_and_int(lhs, rhs):
    vvlbh__qgw = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    xhzqr__lvr = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return vvlbh__qgw or xhzqr__lvr


def mul_date_offset_and_int(lhs, rhs):
    xnveo__xvc = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    wym__vnde = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return xnveo__xvc or wym__vnde


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    hboi__etqk = [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ]
    hvsfp__kom = [date_offset_type, month_begin_type, month_end_type, week_type
        ]
    return rhs in hvsfp__kom and lhs in hboi__etqk


def sub_dt_index_and_timestamp(lhs, rhs):
    vja__cdt = isinstance(lhs, DatetimeIndexType) and rhs == pd_timestamp_type
    pixz__peld = isinstance(rhs, DatetimeIndexType
        ) and lhs == pd_timestamp_type
    return vja__cdt or pixz__peld


def sub_dt_or_td(lhs, rhs):
    zzq__ylvjm = lhs == datetime_date_type and rhs == datetime_timedelta_type
    ptgy__kmx = lhs == datetime_date_type and rhs == datetime_date_type
    bruvp__zigp = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return zzq__ylvjm or ptgy__kmx or bruvp__zigp


def sub_datetime_and_timedeltas(lhs, rhs):
    yqp__qlxiv = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    hcrb__zito = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return yqp__qlxiv or hcrb__zito


def div_timedelta_and_int(lhs, rhs):
    srmks__zlc = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    hvcd__quoxe = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return srmks__zlc or hvcd__quoxe


def div_datetime_timedelta(lhs, rhs):
    srmks__zlc = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    hvcd__quoxe = lhs == datetime_timedelta_type and rhs == types.int64
    return srmks__zlc or hvcd__quoxe


def mod_timedeltas(lhs, rhs):
    ktbh__kpmw = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    fbx__gbqlj = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return ktbh__kpmw or fbx__gbqlj


def cmp_dt_index_to_string(lhs, rhs):
    vja__cdt = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    pixz__peld = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return vja__cdt or pixz__peld


def cmp_timestamp_or_date(lhs, rhs):
    alo__zxyfc = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    jbea__fcaip = (lhs == bodo.hiframes.datetime_date_ext.
        datetime_date_type and rhs == pd_timestamp_type)
    vmcn__tttca = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    xnsjg__ronn = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    gey__kvhv = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return alo__zxyfc or jbea__fcaip or vmcn__tttca or xnsjg__ronn or gey__kvhv


def cmp_timeseries(lhs, rhs):
    stx__qticn = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    ljuh__shi = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    qoz__fgud = stx__qticn or ljuh__shi
    ccszn__ozk = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    uafvb__jzpq = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    edzh__xzg = ccszn__ozk or uafvb__jzpq
    return qoz__fgud or edzh__xzg


def cmp_timedeltas(lhs, rhs):
    srmks__zlc = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in srmks__zlc and rhs in srmks__zlc


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    zgm__rldi = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return zgm__rldi


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    hvtuy__vnz = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    mxavt__dylxt = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    fdb__liuy = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    ljc__aeryh = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return hvtuy__vnz or mxavt__dylxt or fdb__liuy or ljc__aeryh


def args_td_and_int_array(lhs, rhs):
    dgwd__qbimb = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    fqt__mnv = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return dgwd__qbimb and fqt__mnv


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        xhzqr__lvr = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        vvlbh__qgw = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        eac__tvt = xhzqr__lvr or vvlbh__qgw
        fdoos__dtx = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        pypmy__xwvf = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        zjbxx__nfkhw = fdoos__dtx or pypmy__xwvf
        vqu__chv = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        ttvc__xcfiw = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        ilfk__uoqcw = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        mua__emk = vqu__chv or ttvc__xcfiw or ilfk__uoqcw
        aeobf__slo = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        clhr__jspa = isinstance(lhs, tys) or isinstance(rhs, tys)
        hkkj__lnbhh = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (eac__tvt or zjbxx__nfkhw or mua__emk or aeobf__slo or
            clhr__jspa or hkkj__lnbhh)
    if op == operator.pow:
        nwa__pjm = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        zlfz__ykwfk = isinstance(lhs, types.Float) and isinstance(rhs, (
            types.IntegerLiteral, types.Float, types.Integer) or rhs in
            types.unsigned_domain or rhs in types.signed_domain)
        ilfk__uoqcw = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        hkkj__lnbhh = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return nwa__pjm or zlfz__ykwfk or ilfk__uoqcw or hkkj__lnbhh
    if op == operator.floordiv:
        ttvc__xcfiw = lhs in types.real_domain and rhs in types.real_domain
        vqu__chv = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        lxdf__uvvxa = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        srmks__zlc = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        hkkj__lnbhh = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (ttvc__xcfiw or vqu__chv or lxdf__uvvxa or srmks__zlc or
            hkkj__lnbhh)
    if op == operator.truediv:
        ijk__fus = lhs in machine_ints and rhs in machine_ints
        ttvc__xcfiw = lhs in types.real_domain and rhs in types.real_domain
        ilfk__uoqcw = (lhs in types.complex_domain and rhs in types.
            complex_domain)
        vqu__chv = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        lxdf__uvvxa = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        dzgj__jetac = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        srmks__zlc = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        hkkj__lnbhh = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (ijk__fus or ttvc__xcfiw or ilfk__uoqcw or vqu__chv or
            lxdf__uvvxa or dzgj__jetac or srmks__zlc or hkkj__lnbhh)
    if op == operator.mod:
        ijk__fus = lhs in machine_ints and rhs in machine_ints
        ttvc__xcfiw = lhs in types.real_domain and rhs in types.real_domain
        vqu__chv = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        lxdf__uvvxa = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        hkkj__lnbhh = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (ijk__fus or ttvc__xcfiw or vqu__chv or lxdf__uvvxa or
            hkkj__lnbhh)
    if op == operator.add or op == operator.sub:
        eac__tvt = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        tbor__vjxt = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        oiytm__qut = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        ygd__psqgz = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        vqu__chv = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        ttvc__xcfiw = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        ilfk__uoqcw = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        mua__emk = vqu__chv or ttvc__xcfiw or ilfk__uoqcw
        hkkj__lnbhh = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        laaq__blvg = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        aeobf__slo = isinstance(lhs, types.List) and isinstance(rhs, types.List
            )
        ccw__watdp = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        lmkqv__kjykr = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs
            , types.UnicodeType)
        cubme__cwyzy = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs
            , types.UnicodeCharSeq)
        lorlc__diw = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        txlfk__dzjx = ccw__watdp or lmkqv__kjykr or cubme__cwyzy or lorlc__diw
        zjbxx__nfkhw = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        lvr__udqaq = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        ivrpo__djqzc = zjbxx__nfkhw or lvr__udqaq
        yda__ztj = lhs == types.NPTimedelta and rhs == types.NPDatetime
        lqoq__fcko = (laaq__blvg or aeobf__slo or txlfk__dzjx or
            ivrpo__djqzc or yda__ztj)
        dvnvy__bwboy = op == operator.add and lqoq__fcko
        return (eac__tvt or tbor__vjxt or oiytm__qut or ygd__psqgz or
            mua__emk or hkkj__lnbhh or dvnvy__bwboy)


def cmp_op_supported_by_numba(lhs, rhs):
    hkkj__lnbhh = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    aeobf__slo = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    eac__tvt = isinstance(lhs, types.NPTimedelta) and isinstance(rhs, types
        .NPTimedelta)
    zlzn__tqn = isinstance(lhs, types.NPDatetime) and isinstance(rhs, types
        .NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    zjbxx__nfkhw = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    laaq__blvg = isinstance(lhs, types.BaseTuple) and isinstance(rhs, types
        .BaseTuple)
    ygd__psqgz = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    mua__emk = isinstance(lhs, types.Number) and isinstance(rhs, types.Number)
    btlos__spypi = isinstance(lhs, types.Boolean) and isinstance(rhs, types
        .Boolean)
    stgaa__pdr = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    tcfm__sea = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    orkxo__mnw = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    piu__djo = isinstance(lhs, types.Literal) and isinstance(rhs, types.Literal
        )
    return (aeobf__slo or eac__tvt or zlzn__tqn or zjbxx__nfkhw or
        laaq__blvg or ygd__psqgz or mua__emk or btlos__spypi or stgaa__pdr or
        tcfm__sea or hkkj__lnbhh or orkxo__mnw or piu__djo)


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
        pxxgc__ngooh = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(pxxgc__ngooh)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        pxxgc__ngooh = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(pxxgc__ngooh)


install_arith_ops()
