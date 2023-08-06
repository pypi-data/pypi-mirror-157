import datetime
import numba
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
"""
Implementation is based on
https://github.com/python/cpython/blob/39a5c889d30d03a88102e56f03ee0c95db198fb3/Lib/datetime.py
"""


class DatetimeDatetimeType(types.Type):

    def __init__(self):
        super(DatetimeDatetimeType, self).__init__(name=
            'DatetimeDatetimeType()')


datetime_datetime_type = DatetimeDatetimeType()
types.datetime_datetime_type = datetime_datetime_type


@typeof_impl.register(datetime.datetime)
def typeof_datetime_datetime(val, c):
    return datetime_datetime_type


@register_model(DatetimeDatetimeType)
class DatetimeDateTimeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rdsud__fdbyx = [('year', types.int64), ('month', types.int64), (
            'day', types.int64), ('hour', types.int64), ('minute', types.
            int64), ('second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, rdsud__fdbyx)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    eurg__npti = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    oefsb__ybm = c.pyapi.long_from_longlong(eurg__npti.year)
    ofbb__cleyw = c.pyapi.long_from_longlong(eurg__npti.month)
    ykgk__ojfjo = c.pyapi.long_from_longlong(eurg__npti.day)
    xhpe__gngb = c.pyapi.long_from_longlong(eurg__npti.hour)
    rfyko__mezw = c.pyapi.long_from_longlong(eurg__npti.minute)
    gjz__natul = c.pyapi.long_from_longlong(eurg__npti.second)
    rlpy__aovda = c.pyapi.long_from_longlong(eurg__npti.microsecond)
    kvbl__tfz = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.datetime)
        )
    agro__snl = c.pyapi.call_function_objargs(kvbl__tfz, (oefsb__ybm,
        ofbb__cleyw, ykgk__ojfjo, xhpe__gngb, rfyko__mezw, gjz__natul,
        rlpy__aovda))
    c.pyapi.decref(oefsb__ybm)
    c.pyapi.decref(ofbb__cleyw)
    c.pyapi.decref(ykgk__ojfjo)
    c.pyapi.decref(xhpe__gngb)
    c.pyapi.decref(rfyko__mezw)
    c.pyapi.decref(gjz__natul)
    c.pyapi.decref(rlpy__aovda)
    c.pyapi.decref(kvbl__tfz)
    return agro__snl


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    oefsb__ybm = c.pyapi.object_getattr_string(val, 'year')
    ofbb__cleyw = c.pyapi.object_getattr_string(val, 'month')
    ykgk__ojfjo = c.pyapi.object_getattr_string(val, 'day')
    xhpe__gngb = c.pyapi.object_getattr_string(val, 'hour')
    rfyko__mezw = c.pyapi.object_getattr_string(val, 'minute')
    gjz__natul = c.pyapi.object_getattr_string(val, 'second')
    rlpy__aovda = c.pyapi.object_getattr_string(val, 'microsecond')
    eurg__npti = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    eurg__npti.year = c.pyapi.long_as_longlong(oefsb__ybm)
    eurg__npti.month = c.pyapi.long_as_longlong(ofbb__cleyw)
    eurg__npti.day = c.pyapi.long_as_longlong(ykgk__ojfjo)
    eurg__npti.hour = c.pyapi.long_as_longlong(xhpe__gngb)
    eurg__npti.minute = c.pyapi.long_as_longlong(rfyko__mezw)
    eurg__npti.second = c.pyapi.long_as_longlong(gjz__natul)
    eurg__npti.microsecond = c.pyapi.long_as_longlong(rlpy__aovda)
    c.pyapi.decref(oefsb__ybm)
    c.pyapi.decref(ofbb__cleyw)
    c.pyapi.decref(ykgk__ojfjo)
    c.pyapi.decref(xhpe__gngb)
    c.pyapi.decref(rfyko__mezw)
    c.pyapi.decref(gjz__natul)
    c.pyapi.decref(rlpy__aovda)
    wrxer__hizg = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(eurg__npti._getvalue(), is_error=wrxer__hizg)


@lower_constant(DatetimeDatetimeType)
def constant_datetime(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    hour = context.get_constant(types.int64, pyval.hour)
    minute = context.get_constant(types.int64, pyval.minute)
    second = context.get_constant(types.int64, pyval.second)
    microsecond = context.get_constant(types.int64, pyval.microsecond)
    return lir.Constant.literal_struct([year, month, day, hour, minute,
        second, microsecond])


@overload(datetime.datetime, no_unliteral=True)
def datetime_datetime(year, month, day, hour=0, minute=0, second=0,
    microsecond=0):

    def impl_datetime(year, month, day, hour=0, minute=0, second=0,
        microsecond=0):
        return init_datetime(year, month, day, hour, minute, second,
            microsecond)
    return impl_datetime


@intrinsic
def init_datetime(typingctx, year, month, day, hour, minute, second,
    microsecond):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        eurg__npti = cgutils.create_struct_proxy(typ)(context, builder)
        eurg__npti.year = args[0]
        eurg__npti.month = args[1]
        eurg__npti.day = args[2]
        eurg__npti.hour = args[3]
        eurg__npti.minute = args[4]
        eurg__npti.second = args[5]
        eurg__npti.microsecond = args[6]
        return eurg__npti._getvalue()
    return DatetimeDatetimeType()(year, month, day, hour, minute, second,
        microsecond), codegen


make_attribute_wrapper(DatetimeDatetimeType, 'year', '_year')
make_attribute_wrapper(DatetimeDatetimeType, 'month', '_month')
make_attribute_wrapper(DatetimeDatetimeType, 'day', '_day')
make_attribute_wrapper(DatetimeDatetimeType, 'hour', '_hour')
make_attribute_wrapper(DatetimeDatetimeType, 'minute', '_minute')
make_attribute_wrapper(DatetimeDatetimeType, 'second', '_second')
make_attribute_wrapper(DatetimeDatetimeType, 'microsecond', '_microsecond')


@overload_attribute(DatetimeDatetimeType, 'year')
def datetime_get_year(dt):

    def impl(dt):
        return dt._year
    return impl


@overload_attribute(DatetimeDatetimeType, 'month')
def datetime_get_month(dt):

    def impl(dt):
        return dt._month
    return impl


@overload_attribute(DatetimeDatetimeType, 'day')
def datetime_get_day(dt):

    def impl(dt):
        return dt._day
    return impl


@overload_attribute(DatetimeDatetimeType, 'hour')
def datetime_get_hour(dt):

    def impl(dt):
        return dt._hour
    return impl


@overload_attribute(DatetimeDatetimeType, 'minute')
def datetime_get_minute(dt):

    def impl(dt):
        return dt._minute
    return impl


@overload_attribute(DatetimeDatetimeType, 'second')
def datetime_get_second(dt):

    def impl(dt):
        return dt._second
    return impl


@overload_attribute(DatetimeDatetimeType, 'microsecond')
def datetime_get_microsecond(dt):

    def impl(dt):
        return dt._microsecond
    return impl


@overload_method(DatetimeDatetimeType, 'date', no_unliteral=True)
def date(dt):

    def impl(dt):
        return datetime.date(dt.year, dt.month, dt.day)
    return impl


@register_jitable
def now_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.now()
    return d


@register_jitable
def today_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.today()
    return d


@register_jitable
def strptime_impl(date_string, dtformat):
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.strptime(date_string, dtformat)
    return d


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


def create_cmp_op_overload(op):

    def overload_datetime_cmp(lhs, rhs):
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

            def impl(lhs, rhs):
                y, lmd__xks = lhs.year, rhs.year
                qtn__pfpsa, ltdok__gfiu = lhs.month, rhs.month
                d, xftt__eeoms = lhs.day, rhs.day
                poizb__pmgqd, yspqn__uhkag = lhs.hour, rhs.hour
                lul__zxvx, ymhr__rlehr = lhs.minute, rhs.minute
                lztac__ebpeu, vffjn__kqeef = lhs.second, rhs.second
                inzi__qki, ior__ycrgi = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, qtn__pfpsa, d, poizb__pmgqd, lul__zxvx,
                    lztac__ebpeu, inzi__qki), (lmd__xks, ltdok__gfiu,
                    xftt__eeoms, yspqn__uhkag, ymhr__rlehr, vffjn__kqeef,
                    ior__ycrgi)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            ubqt__ijlkz = lhs.toordinal()
            qxl__apu = rhs.toordinal()
            txda__oqk = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            sls__rpq = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            omyza__tox = datetime.timedelta(ubqt__ijlkz - qxl__apu, 
                txda__oqk - sls__rpq, lhs.microsecond - rhs.microsecond)
            return omyza__tox
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    ixbtz__fqa = context.make_helper(builder, fromty, value=val)
    abwq__oer = cgutils.as_bool_bit(builder, ixbtz__fqa.valid)
    with builder.if_else(abwq__oer) as (xqvjo__ixv, iczmn__pca):
        with xqvjo__ixv:
            hujy__bap = context.cast(builder, ixbtz__fqa.data, fromty.type,
                toty)
            uxq__ygyiq = builder.block
        with iczmn__pca:
            tanv__qadj = numba.np.npdatetime.NAT
            vwq__twh = builder.block
    agro__snl = builder.phi(hujy__bap.type)
    agro__snl.add_incoming(hujy__bap, uxq__ygyiq)
    agro__snl.add_incoming(tanv__qadj, vwq__twh)
    return agro__snl
