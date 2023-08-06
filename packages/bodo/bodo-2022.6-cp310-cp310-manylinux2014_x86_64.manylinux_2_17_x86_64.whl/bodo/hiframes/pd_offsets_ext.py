"""
Implement support for the various classes in pd.tseries.offsets.
"""
import operator
import llvmlite.binding as ll
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.pd_timestamp_ext import get_days_in_month, pd_timestamp_type
from bodo.libs import hdatetime_ext
from bodo.utils.typing import BodoError, create_unsupported_overload, is_overload_none
ll.add_symbol('box_date_offset', hdatetime_ext.box_date_offset)
ll.add_symbol('unbox_date_offset', hdatetime_ext.unbox_date_offset)


class MonthBeginType(types.Type):

    def __init__(self):
        super(MonthBeginType, self).__init__(name='MonthBeginType()')


month_begin_type = MonthBeginType()


@typeof_impl.register(pd.tseries.offsets.MonthBegin)
def typeof_month_begin(val, c):
    return month_begin_type


@register_model(MonthBeginType)
class MonthBeginModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pwwh__ytt = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, pwwh__ytt)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    twh__eoap = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    bcrn__jxnxd = c.pyapi.long_from_longlong(twh__eoap.n)
    pbg__twgzi = c.pyapi.from_native_value(types.boolean, twh__eoap.
        normalize, c.env_manager)
    hzad__crjzv = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    qwwnx__ert = c.pyapi.call_function_objargs(hzad__crjzv, (bcrn__jxnxd,
        pbg__twgzi))
    c.pyapi.decref(bcrn__jxnxd)
    c.pyapi.decref(pbg__twgzi)
    c.pyapi.decref(hzad__crjzv)
    return qwwnx__ert


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    bcrn__jxnxd = c.pyapi.object_getattr_string(val, 'n')
    pbg__twgzi = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(bcrn__jxnxd)
    normalize = c.pyapi.to_native_value(types.bool_, pbg__twgzi).value
    twh__eoap = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    twh__eoap.n = n
    twh__eoap.normalize = normalize
    c.pyapi.decref(bcrn__jxnxd)
    c.pyapi.decref(pbg__twgzi)
    iot__qjfi = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(twh__eoap._getvalue(), is_error=iot__qjfi)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        twh__eoap = cgutils.create_struct_proxy(typ)(context, builder)
        twh__eoap.n = args[0]
        twh__eoap.normalize = args[1]
        return twh__eoap._getvalue()
    return MonthBeginType()(n, normalize), codegen


make_attribute_wrapper(MonthBeginType, 'n', 'n')
make_attribute_wrapper(MonthBeginType, 'normalize', 'normalize')


@register_jitable
def calculate_month_begin_date(year, month, day, n):
    if n <= 0:
        if day > 1:
            n += 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = 1
    return year, month, day


def overload_add_operator_month_begin_offset_type(lhs, rhs):
    if lhs == month_begin_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_begin_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_begin_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_begin_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


class MonthEndType(types.Type):

    def __init__(self):
        super(MonthEndType, self).__init__(name='MonthEndType()')


month_end_type = MonthEndType()


@typeof_impl.register(pd.tseries.offsets.MonthEnd)
def typeof_month_end(val, c):
    return month_end_type


@register_model(MonthEndType)
class MonthEndModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pwwh__ytt = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, pwwh__ytt)


@box(MonthEndType)
def box_month_end(typ, val, c):
    iapzg__csgdd = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    bcrn__jxnxd = c.pyapi.long_from_longlong(iapzg__csgdd.n)
    pbg__twgzi = c.pyapi.from_native_value(types.boolean, iapzg__csgdd.
        normalize, c.env_manager)
    krpj__fju = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    qwwnx__ert = c.pyapi.call_function_objargs(krpj__fju, (bcrn__jxnxd,
        pbg__twgzi))
    c.pyapi.decref(bcrn__jxnxd)
    c.pyapi.decref(pbg__twgzi)
    c.pyapi.decref(krpj__fju)
    return qwwnx__ert


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    bcrn__jxnxd = c.pyapi.object_getattr_string(val, 'n')
    pbg__twgzi = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(bcrn__jxnxd)
    normalize = c.pyapi.to_native_value(types.bool_, pbg__twgzi).value
    iapzg__csgdd = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    iapzg__csgdd.n = n
    iapzg__csgdd.normalize = normalize
    c.pyapi.decref(bcrn__jxnxd)
    c.pyapi.decref(pbg__twgzi)
    iot__qjfi = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(iapzg__csgdd._getvalue(), is_error=iot__qjfi)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        iapzg__csgdd = cgutils.create_struct_proxy(typ)(context, builder)
        iapzg__csgdd.n = args[0]
        iapzg__csgdd.normalize = args[1]
        return iapzg__csgdd._getvalue()
    return MonthEndType()(n, normalize), codegen


make_attribute_wrapper(MonthEndType, 'n', 'n')
make_attribute_wrapper(MonthEndType, 'normalize', 'normalize')


@lower_constant(MonthBeginType)
@lower_constant(MonthEndType)
def lower_constant_month_end(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    return lir.Constant.literal_struct([n, normalize])


@register_jitable
def calculate_month_end_date(year, month, day, n):
    if n > 0:
        iapzg__csgdd = get_days_in_month(year, month)
        if iapzg__csgdd > day:
            n -= 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = get_days_in_month(year, month)
    return year, month, day


def overload_add_operator_month_end_offset_type(lhs, rhs):
    if lhs == month_end_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_end_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_end_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_end_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_mul_date_offset_types(lhs, rhs):
    if lhs == month_begin_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthBegin(lhs.n * rhs, lhs.normalize)
    if lhs == month_end_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthEnd(lhs.n * rhs, lhs.normalize)
    if lhs == week_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.Week(lhs.n * rhs, lhs.normalize, lhs.
                weekday)
    if lhs == date_offset_type:

        def impl(lhs, rhs):
            n = lhs.n * rhs
            normalize = lhs.normalize
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                nanoseconds = lhs._nanoseconds
                nanosecond = lhs._nanosecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize)
    if rhs in [week_type, month_end_type, month_begin_type, date_offset_type]:

        def impl(lhs, rhs):
            return rhs * lhs
        return impl
    return impl


class DateOffsetType(types.Type):

    def __init__(self):
        super(DateOffsetType, self).__init__(name='DateOffsetType()')


date_offset_type = DateOffsetType()
date_offset_fields = ['years', 'months', 'weeks', 'days', 'hours',
    'minutes', 'seconds', 'microseconds', 'nanoseconds', 'year', 'month',
    'day', 'weekday', 'hour', 'minute', 'second', 'microsecond', 'nanosecond']


@typeof_impl.register(pd.tseries.offsets.DateOffset)
def type_of_date_offset(val, c):
    return date_offset_type


@register_model(DateOffsetType)
class DateOffsetModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pwwh__ytt = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, pwwh__ytt)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    yef__fpocl = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    vviij__bzhti = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for ssidr__yhfgr, gdsh__vfn in enumerate(date_offset_fields):
        c.builder.store(getattr(yef__fpocl, gdsh__vfn), c.builder.inttoptr(
            c.builder.add(c.builder.ptrtoint(vviij__bzhti, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * ssidr__yhfgr)), lir.IntType(
            64).as_pointer()))
    ppbn__ahya = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    gxva__ezhty = cgutils.get_or_insert_function(c.builder.module,
        ppbn__ahya, name='box_date_offset')
    djpf__bfyco = c.builder.call(gxva__ezhty, [yef__fpocl.n, yef__fpocl.
        normalize, vviij__bzhti, yef__fpocl.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return djpf__bfyco


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    bcrn__jxnxd = c.pyapi.object_getattr_string(val, 'n')
    pbg__twgzi = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(bcrn__jxnxd)
    normalize = c.pyapi.to_native_value(types.bool_, pbg__twgzi).value
    vviij__bzhti = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    ppbn__ahya = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer()])
    mwz__capy = cgutils.get_or_insert_function(c.builder.module, ppbn__ahya,
        name='unbox_date_offset')
    has_kws = c.builder.call(mwz__capy, [val, vviij__bzhti])
    yef__fpocl = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    yef__fpocl.n = n
    yef__fpocl.normalize = normalize
    for ssidr__yhfgr, gdsh__vfn in enumerate(date_offset_fields):
        setattr(yef__fpocl, gdsh__vfn, c.builder.load(c.builder.inttoptr(c.
            builder.add(c.builder.ptrtoint(vviij__bzhti, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * ssidr__yhfgr)), lir.IntType(
            64).as_pointer())))
    yef__fpocl.has_kws = has_kws
    c.pyapi.decref(bcrn__jxnxd)
    c.pyapi.decref(pbg__twgzi)
    iot__qjfi = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(yef__fpocl._getvalue(), is_error=iot__qjfi)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    gvrsc__ebf = [n, normalize]
    has_kws = False
    torq__bcpui = [0] * 9 + [-1] * 9
    for ssidr__yhfgr, gdsh__vfn in enumerate(date_offset_fields):
        if hasattr(pyval, gdsh__vfn):
            vcw__kwwjy = context.get_constant(types.int64, getattr(pyval,
                gdsh__vfn))
            has_kws = True
        else:
            vcw__kwwjy = context.get_constant(types.int64, torq__bcpui[
                ssidr__yhfgr])
        gvrsc__ebf.append(vcw__kwwjy)
    has_kws = context.get_constant(types.boolean, has_kws)
    gvrsc__ebf.append(has_kws)
    return lir.Constant.literal_struct(gvrsc__ebf)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    ixz__yzih = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for grxc__bfmi in ixz__yzih:
        if not is_overload_none(grxc__bfmi):
            has_kws = True
            break

    def impl(n=1, normalize=False, years=None, months=None, weeks=None,
        days=None, hours=None, minutes=None, seconds=None, microseconds=
        None, nanoseconds=None, year=None, month=None, day=None, weekday=
        None, hour=None, minute=None, second=None, microsecond=None,
        nanosecond=None):
        years = 0 if years is None else years
        months = 0 if months is None else months
        weeks = 0 if weeks is None else weeks
        days = 0 if days is None else days
        hours = 0 if hours is None else hours
        minutes = 0 if minutes is None else minutes
        seconds = 0 if seconds is None else seconds
        microseconds = 0 if microseconds is None else microseconds
        nanoseconds = 0 if nanoseconds is None else nanoseconds
        year = -1 if year is None else year
        month = -1 if month is None else month
        weekday = -1 if weekday is None else weekday
        day = -1 if day is None else day
        hour = -1 if hour is None else hour
        minute = -1 if minute is None else minute
        second = -1 if second is None else second
        microsecond = -1 if microsecond is None else microsecond
        nanosecond = -1 if nanosecond is None else nanosecond
        return init_date_offset(n, normalize, years, months, weeks, days,
            hours, minutes, seconds, microseconds, nanoseconds, year, month,
            day, weekday, hour, minute, second, microsecond, nanosecond,
            has_kws)
    return impl


@intrinsic
def init_date_offset(typingctx, n, normalize, years, months, weeks, days,
    hours, minutes, seconds, microseconds, nanoseconds, year, month, day,
    weekday, hour, minute, second, microsecond, nanosecond, has_kws):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        yef__fpocl = cgutils.create_struct_proxy(typ)(context, builder)
        yef__fpocl.n = args[0]
        yef__fpocl.normalize = args[1]
        yef__fpocl.years = args[2]
        yef__fpocl.months = args[3]
        yef__fpocl.weeks = args[4]
        yef__fpocl.days = args[5]
        yef__fpocl.hours = args[6]
        yef__fpocl.minutes = args[7]
        yef__fpocl.seconds = args[8]
        yef__fpocl.microseconds = args[9]
        yef__fpocl.nanoseconds = args[10]
        yef__fpocl.year = args[11]
        yef__fpocl.month = args[12]
        yef__fpocl.day = args[13]
        yef__fpocl.weekday = args[14]
        yef__fpocl.hour = args[15]
        yef__fpocl.minute = args[16]
        yef__fpocl.second = args[17]
        yef__fpocl.microsecond = args[18]
        yef__fpocl.nanosecond = args[19]
        yef__fpocl.has_kws = args[20]
        return yef__fpocl._getvalue()
    return DateOffsetType()(n, normalize, years, months, weeks, days, hours,
        minutes, seconds, microseconds, nanoseconds, year, month, day,
        weekday, hour, minute, second, microsecond, nanosecond, has_kws
        ), codegen


make_attribute_wrapper(DateOffsetType, 'n', 'n')
make_attribute_wrapper(DateOffsetType, 'normalize', 'normalize')
make_attribute_wrapper(DateOffsetType, 'years', '_years')
make_attribute_wrapper(DateOffsetType, 'months', '_months')
make_attribute_wrapper(DateOffsetType, 'weeks', '_weeks')
make_attribute_wrapper(DateOffsetType, 'days', '_days')
make_attribute_wrapper(DateOffsetType, 'hours', '_hours')
make_attribute_wrapper(DateOffsetType, 'minutes', '_minutes')
make_attribute_wrapper(DateOffsetType, 'seconds', '_seconds')
make_attribute_wrapper(DateOffsetType, 'microseconds', '_microseconds')
make_attribute_wrapper(DateOffsetType, 'nanoseconds', '_nanoseconds')
make_attribute_wrapper(DateOffsetType, 'year', '_year')
make_attribute_wrapper(DateOffsetType, 'month', '_month')
make_attribute_wrapper(DateOffsetType, 'weekday', '_weekday')
make_attribute_wrapper(DateOffsetType, 'day', '_day')
make_attribute_wrapper(DateOffsetType, 'hour', '_hour')
make_attribute_wrapper(DateOffsetType, 'minute', '_minute')
make_attribute_wrapper(DateOffsetType, 'second', '_second')
make_attribute_wrapper(DateOffsetType, 'microsecond', '_microsecond')
make_attribute_wrapper(DateOffsetType, 'nanosecond', '_nanosecond')
make_attribute_wrapper(DateOffsetType, 'has_kws', '_has_kws')


@register_jitable
def relative_delta_addition(dateoffset, ts):
    if dateoffset._has_kws:
        uqma__aatpa = -1 if dateoffset.n < 0 else 1
        for qylg__gwzj in range(np.abs(dateoffset.n)):
            year = ts.year
            month = ts.month
            day = ts.day
            hour = ts.hour
            minute = ts.minute
            second = ts.second
            microsecond = ts.microsecond
            nanosecond = ts.nanosecond
            if dateoffset._year != -1:
                year = dateoffset._year
            year += uqma__aatpa * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += uqma__aatpa * dateoffset._months
            year, month, kfga__gjlj = calculate_month_end_date(year, month,
                day, 0)
            if day > kfga__gjlj:
                day = kfga__gjlj
            if dateoffset._day != -1:
                day = dateoffset._day
            if dateoffset._hour != -1:
                hour = dateoffset._hour
            if dateoffset._minute != -1:
                minute = dateoffset._minute
            if dateoffset._second != -1:
                second = dateoffset._second
            if dateoffset._microsecond != -1:
                microsecond = dateoffset._microsecond
            if dateoffset._nanosecond != -1:
                nanosecond = dateoffset._nanosecond
            ts = pd.Timestamp(year=year, month=month, day=day, hour=hour,
                minute=minute, second=second, microsecond=microsecond,
                nanosecond=nanosecond)
            zavmm__mrixz = pd.Timedelta(days=dateoffset._days + 7 *
                dateoffset._weeks, hours=dateoffset._hours, minutes=
                dateoffset._minutes, seconds=dateoffset._seconds,
                microseconds=dateoffset._microseconds)
            zavmm__mrixz = zavmm__mrixz + pd.Timedelta(dateoffset.
                _nanoseconds, unit='ns')
            if uqma__aatpa == -1:
                zavmm__mrixz = -zavmm__mrixz
            ts = ts + zavmm__mrixz
            if dateoffset._weekday != -1:
                nnqrp__knpvh = ts.weekday()
                kib__fwhdw = (dateoffset._weekday - nnqrp__knpvh) % 7
                ts = ts + pd.Timedelta(days=kib__fwhdw)
        return ts
    else:
        return pd.Timedelta(days=dateoffset.n) + ts


def overload_add_operator_date_offset_type(lhs, rhs):
    if lhs == date_offset_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, rhs)
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs == date_offset_type and rhs in [datetime_date_type,
        datetime_datetime_type]:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, pd.Timestamp(rhs))
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == date_offset_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_sub_operator_offsets(lhs, rhs):
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs in [date_offset_type, month_begin_type, month_end_type,
        week_type]:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl


@overload(operator.neg, no_unliteral=True)
def overload_neg(lhs):
    if lhs == month_begin_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthBegin(-lhs.n, lhs.normalize)
    elif lhs == month_end_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthEnd(-lhs.n, lhs.normalize)
    elif lhs == week_type:

        def impl(lhs):
            return pd.tseries.offsets.Week(-lhs.n, lhs.normalize, lhs.weekday)
    elif lhs == date_offset_type:

        def impl(lhs):
            n = -lhs.n
            normalize = lhs.normalize
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                nanoseconds = lhs._nanoseconds
                nanosecond = lhs._nanosecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize)
    else:
        return
    return impl


def is_offsets_type(val):
    return val in [date_offset_type, month_begin_type, month_end_type,
        week_type]


class WeekType(types.Type):

    def __init__(self):
        super(WeekType, self).__init__(name='WeekType()')


week_type = WeekType()


@typeof_impl.register(pd.tseries.offsets.Week)
def typeof_week(val, c):
    return week_type


@register_model(WeekType)
class WeekModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pwwh__ytt = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, pwwh__ytt)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        ytu__lxm = -1 if weekday is None else weekday
        return init_week(n, normalize, ytu__lxm)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        klhq__rqy = cgutils.create_struct_proxy(typ)(context, builder)
        klhq__rqy.n = args[0]
        klhq__rqy.normalize = args[1]
        klhq__rqy.weekday = args[2]
        return klhq__rqy._getvalue()
    return WeekType()(n, normalize, weekday), codegen


@lower_constant(WeekType)
def lower_constant_week(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    if pyval.weekday is not None:
        weekday = context.get_constant(types.int64, pyval.weekday)
    else:
        weekday = context.get_constant(types.int64, -1)
    return lir.Constant.literal_struct([n, normalize, weekday])


@box(WeekType)
def box_week(typ, val, c):
    klhq__rqy = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    bcrn__jxnxd = c.pyapi.long_from_longlong(klhq__rqy.n)
    pbg__twgzi = c.pyapi.from_native_value(types.boolean, klhq__rqy.
        normalize, c.env_manager)
    zoylp__nyj = c.pyapi.long_from_longlong(klhq__rqy.weekday)
    ume__eto = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    vycvr__lam = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64), 
        -1), klhq__rqy.weekday)
    with c.builder.if_else(vycvr__lam) as (kpat__gcxgj, mhag__mhg):
        with kpat__gcxgj:
            dep__wrwsf = c.pyapi.call_function_objargs(ume__eto, (
                bcrn__jxnxd, pbg__twgzi, zoylp__nyj))
            mof__pcq = c.builder.block
        with mhag__mhg:
            lddz__wcakr = c.pyapi.call_function_objargs(ume__eto, (
                bcrn__jxnxd, pbg__twgzi))
            fwfka__mli = c.builder.block
    qwwnx__ert = c.builder.phi(dep__wrwsf.type)
    qwwnx__ert.add_incoming(dep__wrwsf, mof__pcq)
    qwwnx__ert.add_incoming(lddz__wcakr, fwfka__mli)
    c.pyapi.decref(zoylp__nyj)
    c.pyapi.decref(bcrn__jxnxd)
    c.pyapi.decref(pbg__twgzi)
    c.pyapi.decref(ume__eto)
    return qwwnx__ert


@unbox(WeekType)
def unbox_week(typ, val, c):
    bcrn__jxnxd = c.pyapi.object_getattr_string(val, 'n')
    pbg__twgzi = c.pyapi.object_getattr_string(val, 'normalize')
    zoylp__nyj = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(bcrn__jxnxd)
    normalize = c.pyapi.to_native_value(types.bool_, pbg__twgzi).value
    ompaa__gka = c.pyapi.make_none()
    ppzxz__fdj = c.builder.icmp_unsigned('==', zoylp__nyj, ompaa__gka)
    with c.builder.if_else(ppzxz__fdj) as (mhag__mhg, kpat__gcxgj):
        with kpat__gcxgj:
            dep__wrwsf = c.pyapi.long_as_longlong(zoylp__nyj)
            mof__pcq = c.builder.block
        with mhag__mhg:
            lddz__wcakr = lir.Constant(lir.IntType(64), -1)
            fwfka__mli = c.builder.block
    qwwnx__ert = c.builder.phi(dep__wrwsf.type)
    qwwnx__ert.add_incoming(dep__wrwsf, mof__pcq)
    qwwnx__ert.add_incoming(lddz__wcakr, fwfka__mli)
    klhq__rqy = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    klhq__rqy.n = n
    klhq__rqy.normalize = normalize
    klhq__rqy.weekday = qwwnx__ert
    c.pyapi.decref(bcrn__jxnxd)
    c.pyapi.decref(pbg__twgzi)
    c.pyapi.decref(zoylp__nyj)
    iot__qjfi = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(klhq__rqy._getvalue(), is_error=iot__qjfi)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            tes__lurwm = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                rbiy__xlw = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                rbiy__xlw = rhs
            return rbiy__xlw + tes__lurwm
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            tes__lurwm = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                rbiy__xlw = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                rbiy__xlw = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return rbiy__xlw + tes__lurwm
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            tes__lurwm = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            return rhs + tes__lurwm
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == week_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


@register_jitable
def calculate_week_date(n, weekday, other_weekday):
    if weekday == -1:
        return pd.Timedelta(weeks=n)
    if weekday != other_weekday:
        khsuw__cgm = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=khsuw__cgm)


date_offset_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
date_offset_unsupported = {'__call__', 'rollback', 'rollforward',
    'is_month_start', 'is_month_end', 'apply', 'apply_index', 'copy',
    'isAnchored', 'onOffset', 'is_anchored', 'is_on_offset',
    'is_quarter_start', 'is_quarter_end', 'is_year_start', 'is_year_end'}
month_end_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_end_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
month_begin_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_begin_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
week_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos', 'rule_code'}
week_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
offsets_unsupported = {pd.tseries.offsets.BusinessDay, pd.tseries.offsets.
    BDay, pd.tseries.offsets.BusinessHour, pd.tseries.offsets.
    CustomBusinessDay, pd.tseries.offsets.CDay, pd.tseries.offsets.
    CustomBusinessHour, pd.tseries.offsets.BusinessMonthEnd, pd.tseries.
    offsets.BMonthEnd, pd.tseries.offsets.BusinessMonthBegin, pd.tseries.
    offsets.BMonthBegin, pd.tseries.offsets.CustomBusinessMonthEnd, pd.
    tseries.offsets.CBMonthEnd, pd.tseries.offsets.CustomBusinessMonthBegin,
    pd.tseries.offsets.CBMonthBegin, pd.tseries.offsets.SemiMonthEnd, pd.
    tseries.offsets.SemiMonthBegin, pd.tseries.offsets.WeekOfMonth, pd.
    tseries.offsets.LastWeekOfMonth, pd.tseries.offsets.BQuarterEnd, pd.
    tseries.offsets.BQuarterBegin, pd.tseries.offsets.QuarterEnd, pd.
    tseries.offsets.QuarterBegin, pd.tseries.offsets.BYearEnd, pd.tseries.
    offsets.BYearBegin, pd.tseries.offsets.YearEnd, pd.tseries.offsets.
    YearBegin, pd.tseries.offsets.FY5253, pd.tseries.offsets.FY5253Quarter,
    pd.tseries.offsets.Easter, pd.tseries.offsets.Tick, pd.tseries.offsets.
    Day, pd.tseries.offsets.Hour, pd.tseries.offsets.Minute, pd.tseries.
    offsets.Second, pd.tseries.offsets.Milli, pd.tseries.offsets.Micro, pd.
    tseries.offsets.Nano}
frequencies_unsupported = {pd.tseries.frequencies.to_offset}


def _install_date_offsets_unsupported():
    for ksl__wrr in date_offset_unsupported_attrs:
        mdohd__hki = 'pandas.tseries.offsets.DateOffset.' + ksl__wrr
        overload_attribute(DateOffsetType, ksl__wrr)(
            create_unsupported_overload(mdohd__hki))
    for ksl__wrr in date_offset_unsupported:
        mdohd__hki = 'pandas.tseries.offsets.DateOffset.' + ksl__wrr
        overload_method(DateOffsetType, ksl__wrr)(create_unsupported_overload
            (mdohd__hki))


def _install_month_begin_unsupported():
    for ksl__wrr in month_begin_unsupported_attrs:
        mdohd__hki = 'pandas.tseries.offsets.MonthBegin.' + ksl__wrr
        overload_attribute(MonthBeginType, ksl__wrr)(
            create_unsupported_overload(mdohd__hki))
    for ksl__wrr in month_begin_unsupported:
        mdohd__hki = 'pandas.tseries.offsets.MonthBegin.' + ksl__wrr
        overload_method(MonthBeginType, ksl__wrr)(create_unsupported_overload
            (mdohd__hki))


def _install_month_end_unsupported():
    for ksl__wrr in date_offset_unsupported_attrs:
        mdohd__hki = 'pandas.tseries.offsets.MonthEnd.' + ksl__wrr
        overload_attribute(MonthEndType, ksl__wrr)(create_unsupported_overload
            (mdohd__hki))
    for ksl__wrr in date_offset_unsupported:
        mdohd__hki = 'pandas.tseries.offsets.MonthEnd.' + ksl__wrr
        overload_method(MonthEndType, ksl__wrr)(create_unsupported_overload
            (mdohd__hki))


def _install_week_unsupported():
    for ksl__wrr in week_unsupported_attrs:
        mdohd__hki = 'pandas.tseries.offsets.Week.' + ksl__wrr
        overload_attribute(WeekType, ksl__wrr)(create_unsupported_overload(
            mdohd__hki))
    for ksl__wrr in week_unsupported:
        mdohd__hki = 'pandas.tseries.offsets.Week.' + ksl__wrr
        overload_method(WeekType, ksl__wrr)(create_unsupported_overload(
            mdohd__hki))


def _install_offsets_unsupported():
    for vcw__kwwjy in offsets_unsupported:
        mdohd__hki = 'pandas.tseries.offsets.' + vcw__kwwjy.__name__
        overload(vcw__kwwjy)(create_unsupported_overload(mdohd__hki))


def _install_frequencies_unsupported():
    for vcw__kwwjy in frequencies_unsupported:
        mdohd__hki = 'pandas.tseries.frequencies.' + vcw__kwwjy.__name__
        overload(vcw__kwwjy)(create_unsupported_overload(mdohd__hki))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
