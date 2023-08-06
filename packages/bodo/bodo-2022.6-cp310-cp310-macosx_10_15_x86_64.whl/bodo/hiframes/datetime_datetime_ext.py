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
        sxxin__szkb = [('year', types.int64), ('month', types.int64), (
            'day', types.int64), ('hour', types.int64), ('minute', types.
            int64), ('second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, sxxin__szkb)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    owelo__mlk = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    wilh__itcbr = c.pyapi.long_from_longlong(owelo__mlk.year)
    qeb__ifi = c.pyapi.long_from_longlong(owelo__mlk.month)
    lqi__huy = c.pyapi.long_from_longlong(owelo__mlk.day)
    mlr__edibr = c.pyapi.long_from_longlong(owelo__mlk.hour)
    fux__fpsv = c.pyapi.long_from_longlong(owelo__mlk.minute)
    beb__tugh = c.pyapi.long_from_longlong(owelo__mlk.second)
    ecs__ckiv = c.pyapi.long_from_longlong(owelo__mlk.microsecond)
    wtc__rfa = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.datetime))
    hljhh__eqli = c.pyapi.call_function_objargs(wtc__rfa, (wilh__itcbr,
        qeb__ifi, lqi__huy, mlr__edibr, fux__fpsv, beb__tugh, ecs__ckiv))
    c.pyapi.decref(wilh__itcbr)
    c.pyapi.decref(qeb__ifi)
    c.pyapi.decref(lqi__huy)
    c.pyapi.decref(mlr__edibr)
    c.pyapi.decref(fux__fpsv)
    c.pyapi.decref(beb__tugh)
    c.pyapi.decref(ecs__ckiv)
    c.pyapi.decref(wtc__rfa)
    return hljhh__eqli


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    wilh__itcbr = c.pyapi.object_getattr_string(val, 'year')
    qeb__ifi = c.pyapi.object_getattr_string(val, 'month')
    lqi__huy = c.pyapi.object_getattr_string(val, 'day')
    mlr__edibr = c.pyapi.object_getattr_string(val, 'hour')
    fux__fpsv = c.pyapi.object_getattr_string(val, 'minute')
    beb__tugh = c.pyapi.object_getattr_string(val, 'second')
    ecs__ckiv = c.pyapi.object_getattr_string(val, 'microsecond')
    owelo__mlk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    owelo__mlk.year = c.pyapi.long_as_longlong(wilh__itcbr)
    owelo__mlk.month = c.pyapi.long_as_longlong(qeb__ifi)
    owelo__mlk.day = c.pyapi.long_as_longlong(lqi__huy)
    owelo__mlk.hour = c.pyapi.long_as_longlong(mlr__edibr)
    owelo__mlk.minute = c.pyapi.long_as_longlong(fux__fpsv)
    owelo__mlk.second = c.pyapi.long_as_longlong(beb__tugh)
    owelo__mlk.microsecond = c.pyapi.long_as_longlong(ecs__ckiv)
    c.pyapi.decref(wilh__itcbr)
    c.pyapi.decref(qeb__ifi)
    c.pyapi.decref(lqi__huy)
    c.pyapi.decref(mlr__edibr)
    c.pyapi.decref(fux__fpsv)
    c.pyapi.decref(beb__tugh)
    c.pyapi.decref(ecs__ckiv)
    ebm__eik = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(owelo__mlk._getvalue(), is_error=ebm__eik)


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
        owelo__mlk = cgutils.create_struct_proxy(typ)(context, builder)
        owelo__mlk.year = args[0]
        owelo__mlk.month = args[1]
        owelo__mlk.day = args[2]
        owelo__mlk.hour = args[3]
        owelo__mlk.minute = args[4]
        owelo__mlk.second = args[5]
        owelo__mlk.microsecond = args[6]
        return owelo__mlk._getvalue()
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
                y, nwz__dtuv = lhs.year, rhs.year
                mxhnk__rkjbl, yxs__eogie = lhs.month, rhs.month
                d, ahf__kctz = lhs.day, rhs.day
                scwxj__ksqn, skpv__rbx = lhs.hour, rhs.hour
                fpzh__azdii, seosl__llld = lhs.minute, rhs.minute
                hre__rje, cwvo__laupl = lhs.second, rhs.second
                idhu__pvat, olcj__xyuw = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, mxhnk__rkjbl, d, scwxj__ksqn,
                    fpzh__azdii, hre__rje, idhu__pvat), (nwz__dtuv,
                    yxs__eogie, ahf__kctz, skpv__rbx, seosl__llld,
                    cwvo__laupl, olcj__xyuw)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            kwd__bnjd = lhs.toordinal()
            qneig__huz = rhs.toordinal()
            ohvs__ixder = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            fvl__hsi = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            vmv__bnkj = datetime.timedelta(kwd__bnjd - qneig__huz, 
                ohvs__ixder - fvl__hsi, lhs.microsecond - rhs.microsecond)
            return vmv__bnkj
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    ghec__ocnr = context.make_helper(builder, fromty, value=val)
    jczz__truv = cgutils.as_bool_bit(builder, ghec__ocnr.valid)
    with builder.if_else(jczz__truv) as (ymc__mnpx, uxyrv__hqf):
        with ymc__mnpx:
            oqdz__mddxt = context.cast(builder, ghec__ocnr.data, fromty.
                type, toty)
            lvw__rmlfc = builder.block
        with uxyrv__hqf:
            avc__tfev = numba.np.npdatetime.NAT
            ffjhb__oaiju = builder.block
    hljhh__eqli = builder.phi(oqdz__mddxt.type)
    hljhh__eqli.add_incoming(oqdz__mddxt, lvw__rmlfc)
    hljhh__eqli.add_incoming(avc__tfev, ffjhb__oaiju)
    return hljhh__eqli
