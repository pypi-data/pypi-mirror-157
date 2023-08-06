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
        wlgkf__solw = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, wlgkf__solw)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    ffttz__nirv = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    cfmbx__ugkb = c.pyapi.long_from_longlong(ffttz__nirv.n)
    shktg__jrybt = c.pyapi.from_native_value(types.boolean, ffttz__nirv.
        normalize, c.env_manager)
    lmfdo__ovzwr = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    jypg__opze = c.pyapi.call_function_objargs(lmfdo__ovzwr, (cfmbx__ugkb,
        shktg__jrybt))
    c.pyapi.decref(cfmbx__ugkb)
    c.pyapi.decref(shktg__jrybt)
    c.pyapi.decref(lmfdo__ovzwr)
    return jypg__opze


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    cfmbx__ugkb = c.pyapi.object_getattr_string(val, 'n')
    shktg__jrybt = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(cfmbx__ugkb)
    normalize = c.pyapi.to_native_value(types.bool_, shktg__jrybt).value
    ffttz__nirv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ffttz__nirv.n = n
    ffttz__nirv.normalize = normalize
    c.pyapi.decref(cfmbx__ugkb)
    c.pyapi.decref(shktg__jrybt)
    pbhh__dmssj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ffttz__nirv._getvalue(), is_error=pbhh__dmssj)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        ffttz__nirv = cgutils.create_struct_proxy(typ)(context, builder)
        ffttz__nirv.n = args[0]
        ffttz__nirv.normalize = args[1]
        return ffttz__nirv._getvalue()
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
        wlgkf__solw = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, wlgkf__solw)


@box(MonthEndType)
def box_month_end(typ, val, c):
    pohc__hbljj = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    cfmbx__ugkb = c.pyapi.long_from_longlong(pohc__hbljj.n)
    shktg__jrybt = c.pyapi.from_native_value(types.boolean, pohc__hbljj.
        normalize, c.env_manager)
    qwqih__bsg = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    jypg__opze = c.pyapi.call_function_objargs(qwqih__bsg, (cfmbx__ugkb,
        shktg__jrybt))
    c.pyapi.decref(cfmbx__ugkb)
    c.pyapi.decref(shktg__jrybt)
    c.pyapi.decref(qwqih__bsg)
    return jypg__opze


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    cfmbx__ugkb = c.pyapi.object_getattr_string(val, 'n')
    shktg__jrybt = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(cfmbx__ugkb)
    normalize = c.pyapi.to_native_value(types.bool_, shktg__jrybt).value
    pohc__hbljj = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    pohc__hbljj.n = n
    pohc__hbljj.normalize = normalize
    c.pyapi.decref(cfmbx__ugkb)
    c.pyapi.decref(shktg__jrybt)
    pbhh__dmssj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(pohc__hbljj._getvalue(), is_error=pbhh__dmssj)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        pohc__hbljj = cgutils.create_struct_proxy(typ)(context, builder)
        pohc__hbljj.n = args[0]
        pohc__hbljj.normalize = args[1]
        return pohc__hbljj._getvalue()
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
        pohc__hbljj = get_days_in_month(year, month)
        if pohc__hbljj > day:
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
        wlgkf__solw = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, wlgkf__solw)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    wtd__fli = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    mcngd__iyaj = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for jxnru__lyz, yqov__jjn in enumerate(date_offset_fields):
        c.builder.store(getattr(wtd__fli, yqov__jjn), c.builder.inttoptr(c.
            builder.add(c.builder.ptrtoint(mcngd__iyaj, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * jxnru__lyz)), lir.IntType(64)
            .as_pointer()))
    zmjz__gkeh = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    json__kqmzt = cgutils.get_or_insert_function(c.builder.module,
        zmjz__gkeh, name='box_date_offset')
    evqx__rwf = c.builder.call(json__kqmzt, [wtd__fli.n, wtd__fli.normalize,
        mcngd__iyaj, wtd__fli.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return evqx__rwf


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    cfmbx__ugkb = c.pyapi.object_getattr_string(val, 'n')
    shktg__jrybt = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(cfmbx__ugkb)
    normalize = c.pyapi.to_native_value(types.bool_, shktg__jrybt).value
    mcngd__iyaj = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    zmjz__gkeh = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer()])
    cozn__ria = cgutils.get_or_insert_function(c.builder.module, zmjz__gkeh,
        name='unbox_date_offset')
    has_kws = c.builder.call(cozn__ria, [val, mcngd__iyaj])
    wtd__fli = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wtd__fli.n = n
    wtd__fli.normalize = normalize
    for jxnru__lyz, yqov__jjn in enumerate(date_offset_fields):
        setattr(wtd__fli, yqov__jjn, c.builder.load(c.builder.inttoptr(c.
            builder.add(c.builder.ptrtoint(mcngd__iyaj, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * jxnru__lyz)), lir.IntType(64)
            .as_pointer())))
    wtd__fli.has_kws = has_kws
    c.pyapi.decref(cfmbx__ugkb)
    c.pyapi.decref(shktg__jrybt)
    pbhh__dmssj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(wtd__fli._getvalue(), is_error=pbhh__dmssj)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    zjwzp__erige = [n, normalize]
    has_kws = False
    gisfr__aia = [0] * 9 + [-1] * 9
    for jxnru__lyz, yqov__jjn in enumerate(date_offset_fields):
        if hasattr(pyval, yqov__jjn):
            qfkft__zax = context.get_constant(types.int64, getattr(pyval,
                yqov__jjn))
            has_kws = True
        else:
            qfkft__zax = context.get_constant(types.int64, gisfr__aia[
                jxnru__lyz])
        zjwzp__erige.append(qfkft__zax)
    has_kws = context.get_constant(types.boolean, has_kws)
    zjwzp__erige.append(has_kws)
    return lir.Constant.literal_struct(zjwzp__erige)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    xhgh__cjgp = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for lqpc__ozadd in xhgh__cjgp:
        if not is_overload_none(lqpc__ozadd):
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
        wtd__fli = cgutils.create_struct_proxy(typ)(context, builder)
        wtd__fli.n = args[0]
        wtd__fli.normalize = args[1]
        wtd__fli.years = args[2]
        wtd__fli.months = args[3]
        wtd__fli.weeks = args[4]
        wtd__fli.days = args[5]
        wtd__fli.hours = args[6]
        wtd__fli.minutes = args[7]
        wtd__fli.seconds = args[8]
        wtd__fli.microseconds = args[9]
        wtd__fli.nanoseconds = args[10]
        wtd__fli.year = args[11]
        wtd__fli.month = args[12]
        wtd__fli.day = args[13]
        wtd__fli.weekday = args[14]
        wtd__fli.hour = args[15]
        wtd__fli.minute = args[16]
        wtd__fli.second = args[17]
        wtd__fli.microsecond = args[18]
        wtd__fli.nanosecond = args[19]
        wtd__fli.has_kws = args[20]
        return wtd__fli._getvalue()
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
        usrtp__tuuys = -1 if dateoffset.n < 0 else 1
        for gdx__vwr in range(np.abs(dateoffset.n)):
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
            year += usrtp__tuuys * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += usrtp__tuuys * dateoffset._months
            year, month, gdo__bmtu = calculate_month_end_date(year, month,
                day, 0)
            if day > gdo__bmtu:
                day = gdo__bmtu
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
            iqid__mypit = pd.Timedelta(days=dateoffset._days + 7 *
                dateoffset._weeks, hours=dateoffset._hours, minutes=
                dateoffset._minutes, seconds=dateoffset._seconds,
                microseconds=dateoffset._microseconds)
            iqid__mypit = iqid__mypit + pd.Timedelta(dateoffset.
                _nanoseconds, unit='ns')
            if usrtp__tuuys == -1:
                iqid__mypit = -iqid__mypit
            ts = ts + iqid__mypit
            if dateoffset._weekday != -1:
                qqta__hyjdw = ts.weekday()
                biaz__iozpb = (dateoffset._weekday - qqta__hyjdw) % 7
                ts = ts + pd.Timedelta(days=biaz__iozpb)
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
        wlgkf__solw = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, wlgkf__solw)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        aiium__ftda = -1 if weekday is None else weekday
        return init_week(n, normalize, aiium__ftda)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        kab__pkyz = cgutils.create_struct_proxy(typ)(context, builder)
        kab__pkyz.n = args[0]
        kab__pkyz.normalize = args[1]
        kab__pkyz.weekday = args[2]
        return kab__pkyz._getvalue()
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
    kab__pkyz = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    cfmbx__ugkb = c.pyapi.long_from_longlong(kab__pkyz.n)
    shktg__jrybt = c.pyapi.from_native_value(types.boolean, kab__pkyz.
        normalize, c.env_manager)
    qtpsi__pscc = c.pyapi.long_from_longlong(kab__pkyz.weekday)
    yedyr__qaic = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    odpzt__ckg = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64), 
        -1), kab__pkyz.weekday)
    with c.builder.if_else(odpzt__ckg) as (bhaur__hwklu, zko__woan):
        with bhaur__hwklu:
            vtt__mkcz = c.pyapi.call_function_objargs(yedyr__qaic, (
                cfmbx__ugkb, shktg__jrybt, qtpsi__pscc))
            rzaw__php = c.builder.block
        with zko__woan:
            mdy__kxyg = c.pyapi.call_function_objargs(yedyr__qaic, (
                cfmbx__ugkb, shktg__jrybt))
            kifi__ljqps = c.builder.block
    jypg__opze = c.builder.phi(vtt__mkcz.type)
    jypg__opze.add_incoming(vtt__mkcz, rzaw__php)
    jypg__opze.add_incoming(mdy__kxyg, kifi__ljqps)
    c.pyapi.decref(qtpsi__pscc)
    c.pyapi.decref(cfmbx__ugkb)
    c.pyapi.decref(shktg__jrybt)
    c.pyapi.decref(yedyr__qaic)
    return jypg__opze


@unbox(WeekType)
def unbox_week(typ, val, c):
    cfmbx__ugkb = c.pyapi.object_getattr_string(val, 'n')
    shktg__jrybt = c.pyapi.object_getattr_string(val, 'normalize')
    qtpsi__pscc = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(cfmbx__ugkb)
    normalize = c.pyapi.to_native_value(types.bool_, shktg__jrybt).value
    ufup__gcst = c.pyapi.make_none()
    hkk__nwkk = c.builder.icmp_unsigned('==', qtpsi__pscc, ufup__gcst)
    with c.builder.if_else(hkk__nwkk) as (zko__woan, bhaur__hwklu):
        with bhaur__hwklu:
            vtt__mkcz = c.pyapi.long_as_longlong(qtpsi__pscc)
            rzaw__php = c.builder.block
        with zko__woan:
            mdy__kxyg = lir.Constant(lir.IntType(64), -1)
            kifi__ljqps = c.builder.block
    jypg__opze = c.builder.phi(vtt__mkcz.type)
    jypg__opze.add_incoming(vtt__mkcz, rzaw__php)
    jypg__opze.add_incoming(mdy__kxyg, kifi__ljqps)
    kab__pkyz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kab__pkyz.n = n
    kab__pkyz.normalize = normalize
    kab__pkyz.weekday = jypg__opze
    c.pyapi.decref(cfmbx__ugkb)
    c.pyapi.decref(shktg__jrybt)
    c.pyapi.decref(qtpsi__pscc)
    pbhh__dmssj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(kab__pkyz._getvalue(), is_error=pbhh__dmssj)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            nws__lnpzb = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                nbel__urro = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                nbel__urro = rhs
            return nbel__urro + nws__lnpzb
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            nws__lnpzb = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                nbel__urro = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                nbel__urro = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return nbel__urro + nws__lnpzb
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            nws__lnpzb = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            return rhs + nws__lnpzb
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
        pea__wjr = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=pea__wjr)


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
    for acq__ifgev in date_offset_unsupported_attrs:
        sxq__unvmt = 'pandas.tseries.offsets.DateOffset.' + acq__ifgev
        overload_attribute(DateOffsetType, acq__ifgev)(
            create_unsupported_overload(sxq__unvmt))
    for acq__ifgev in date_offset_unsupported:
        sxq__unvmt = 'pandas.tseries.offsets.DateOffset.' + acq__ifgev
        overload_method(DateOffsetType, acq__ifgev)(create_unsupported_overload
            (sxq__unvmt))


def _install_month_begin_unsupported():
    for acq__ifgev in month_begin_unsupported_attrs:
        sxq__unvmt = 'pandas.tseries.offsets.MonthBegin.' + acq__ifgev
        overload_attribute(MonthBeginType, acq__ifgev)(
            create_unsupported_overload(sxq__unvmt))
    for acq__ifgev in month_begin_unsupported:
        sxq__unvmt = 'pandas.tseries.offsets.MonthBegin.' + acq__ifgev
        overload_method(MonthBeginType, acq__ifgev)(create_unsupported_overload
            (sxq__unvmt))


def _install_month_end_unsupported():
    for acq__ifgev in date_offset_unsupported_attrs:
        sxq__unvmt = 'pandas.tseries.offsets.MonthEnd.' + acq__ifgev
        overload_attribute(MonthEndType, acq__ifgev)(
            create_unsupported_overload(sxq__unvmt))
    for acq__ifgev in date_offset_unsupported:
        sxq__unvmt = 'pandas.tseries.offsets.MonthEnd.' + acq__ifgev
        overload_method(MonthEndType, acq__ifgev)(create_unsupported_overload
            (sxq__unvmt))


def _install_week_unsupported():
    for acq__ifgev in week_unsupported_attrs:
        sxq__unvmt = 'pandas.tseries.offsets.Week.' + acq__ifgev
        overload_attribute(WeekType, acq__ifgev)(create_unsupported_overload
            (sxq__unvmt))
    for acq__ifgev in week_unsupported:
        sxq__unvmt = 'pandas.tseries.offsets.Week.' + acq__ifgev
        overload_method(WeekType, acq__ifgev)(create_unsupported_overload(
            sxq__unvmt))


def _install_offsets_unsupported():
    for qfkft__zax in offsets_unsupported:
        sxq__unvmt = 'pandas.tseries.offsets.' + qfkft__zax.__name__
        overload(qfkft__zax)(create_unsupported_overload(sxq__unvmt))


def _install_frequencies_unsupported():
    for qfkft__zax in frequencies_unsupported:
        sxq__unvmt = 'pandas.tseries.frequencies.' + qfkft__zax.__name__
        overload(qfkft__zax)(create_unsupported_overload(sxq__unvmt))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
