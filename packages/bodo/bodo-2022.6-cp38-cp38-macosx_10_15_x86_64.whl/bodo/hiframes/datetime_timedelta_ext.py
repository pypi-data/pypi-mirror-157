"""Numba extension support for datetime.timedelta objects and their arrays.
"""
import datetime
import operator
from collections import namedtuple
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.libs import hdatetime_ext
from bodo.utils.indexing import get_new_null_mask_bool_index, get_new_null_mask_int_index, get_new_null_mask_slice_index, setitem_slice_index_null_bits
from bodo.utils.typing import BodoError, get_overload_const_str, is_iterable_type, is_list_like_index_type, is_overload_constant_str
ll.add_symbol('box_datetime_timedelta_array', hdatetime_ext.
    box_datetime_timedelta_array)
ll.add_symbol('unbox_datetime_timedelta_array', hdatetime_ext.
    unbox_datetime_timedelta_array)


class NoInput:
    pass


_no_input = NoInput()


class NoInputType(types.Type):

    def __init__(self):
        super(NoInputType, self).__init__(name='NoInput')


register_model(NoInputType)(models.OpaqueModel)


@typeof_impl.register(NoInput)
def _typ_no_input(val, c):
    return NoInputType()


@lower_constant(NoInputType)
def constant_no_input(context, builder, ty, pyval):
    return context.get_dummy_value()


class PDTimeDeltaType(types.Type):

    def __init__(self):
        super(PDTimeDeltaType, self).__init__(name='PDTimeDeltaType()')


pd_timedelta_type = PDTimeDeltaType()
types.pd_timedelta_type = pd_timedelta_type


@typeof_impl.register(pd.Timedelta)
def typeof_pd_timedelta(val, c):
    return pd_timedelta_type


@register_model(PDTimeDeltaType)
class PDTimeDeltaModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xegp__qljz = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, xegp__qljz)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    arnl__arb = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    nppxf__flk = c.pyapi.long_from_longlong(arnl__arb.value)
    wfb__ifrws = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(wfb__ifrws, (nppxf__flk,))
    c.pyapi.decref(nppxf__flk)
    c.pyapi.decref(wfb__ifrws)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    nppxf__flk = c.pyapi.object_getattr_string(val, 'value')
    aarie__hocaw = c.pyapi.long_as_longlong(nppxf__flk)
    arnl__arb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    arnl__arb.value = aarie__hocaw
    c.pyapi.decref(nppxf__flk)
    nwcca__zcu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(arnl__arb._getvalue(), is_error=nwcca__zcu)


@lower_constant(PDTimeDeltaType)
def lower_constant_pd_timedelta(context, builder, ty, pyval):
    value = context.get_constant(types.int64, pyval.value)
    return lir.Constant.literal_struct([value])


@overload(pd.Timedelta, no_unliteral=True)
def pd_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
    microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
    if value == _no_input:

        def impl_timedelta_kw(value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
            days += weeks * 7
            hours += days * 24
            minutes += 60 * hours
            seconds += 60 * minutes
            milliseconds += 1000 * seconds
            microseconds += 1000 * milliseconds
            atk__zauo = 1000 * microseconds
            return init_pd_timedelta(atk__zauo)
        return impl_timedelta_kw
    if value == bodo.string_type or is_overload_constant_str(value):

        def impl_str(value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
            with numba.objmode(res='pd_timedelta_type'):
                res = pd.Timedelta(value)
            return res
        return impl_str
    if value == pd_timedelta_type:
        return (lambda value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0: value)
    if value == datetime_timedelta_type:

        def impl_timedelta_datetime(value=_no_input, unit='ns', days=0,
            seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0,
            weeks=0):
            days = value.days
            seconds = 60 * 60 * 24 * days + value.seconds
            microseconds = 1000 * 1000 * seconds + value.microseconds
            atk__zauo = 1000 * microseconds
            return init_pd_timedelta(atk__zauo)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    yeo__klw, wkar__abfl = pd._libs.tslibs.conversion.precision_from_unit(unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * yeo__klw)
    return impl_timedelta


@intrinsic
def init_pd_timedelta(typingctx, value):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        timedelta = cgutils.create_struct_proxy(typ)(context, builder)
        timedelta.value = args[0]
        return timedelta._getvalue()
    return PDTimeDeltaType()(value), codegen


make_attribute_wrapper(PDTimeDeltaType, 'value', '_value')


@overload_attribute(PDTimeDeltaType, 'value')
@overload_attribute(PDTimeDeltaType, 'delta')
def pd_timedelta_get_value(td):

    def impl(td):
        return td._value
    return impl


@overload_attribute(PDTimeDeltaType, 'days')
def pd_timedelta_get_days(td):

    def impl(td):
        return td._value // (1000 * 1000 * 1000 * 60 * 60 * 24)
    return impl


@overload_attribute(PDTimeDeltaType, 'seconds')
def pd_timedelta_get_seconds(td):

    def impl(td):
        return td._value // (1000 * 1000 * 1000) % (60 * 60 * 24)
    return impl


@overload_attribute(PDTimeDeltaType, 'microseconds')
def pd_timedelta_get_microseconds(td):

    def impl(td):
        return td._value // 1000 % 1000000
    return impl


@overload_attribute(PDTimeDeltaType, 'nanoseconds')
def pd_timedelta_get_nanoseconds(td):

    def impl(td):
        return td._value % 1000
    return impl


@register_jitable
def _to_hours_pd_td(td):
    return td._value // (1000 * 1000 * 1000 * 60 * 60) % 24


@register_jitable
def _to_minutes_pd_td(td):
    return td._value // (1000 * 1000 * 1000 * 60) % 60


@register_jitable
def _to_seconds_pd_td(td):
    return td._value // (1000 * 1000 * 1000) % 60


@register_jitable
def _to_milliseconds_pd_td(td):
    return td._value // (1000 * 1000) % 1000


@register_jitable
def _to_microseconds_pd_td(td):
    return td._value // 1000 % 1000


Components = namedtuple('Components', ['days', 'hours', 'minutes',
    'seconds', 'milliseconds', 'microseconds', 'nanoseconds'], defaults=[0,
    0, 0, 0, 0, 0, 0])


@overload_attribute(PDTimeDeltaType, 'components', no_unliteral=True)
def pd_timedelta_get_components(td):

    def impl(td):
        a = Components(td.days, _to_hours_pd_td(td), _to_minutes_pd_td(td),
            _to_seconds_pd_td(td), _to_milliseconds_pd_td(td),
            _to_microseconds_pd_td(td), td.nanoseconds)
        return a
    return impl


@overload_method(PDTimeDeltaType, '__hash__', no_unliteral=True)
def pd_td___hash__(td):

    def impl(td):
        return hash(td._value)
    return impl


@overload_method(PDTimeDeltaType, 'to_numpy', no_unliteral=True)
@overload_method(PDTimeDeltaType, 'to_timedelta64', no_unliteral=True)
def pd_td_to_numpy(td):
    from bodo.hiframes.pd_timestamp_ext import integer_to_timedelta64

    def impl(td):
        return integer_to_timedelta64(td.value)
    return impl


@overload_method(PDTimeDeltaType, 'to_pytimedelta', no_unliteral=True)
def pd_td_to_pytimedelta(td):

    def impl(td):
        return datetime.timedelta(microseconds=np.int64(td._value / 1000))
    return impl


@overload_method(PDTimeDeltaType, 'total_seconds', no_unliteral=True)
def pd_td_total_seconds(td):

    def impl(td):
        return td._value // 1000 / 10 ** 6
    return impl


def overload_add_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            val = lhs.value + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            tbfz__wvopt = (rhs.microseconds + (rhs.seconds + rhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + tbfz__wvopt
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            vzecj__lld = (lhs.microseconds + (lhs.seconds + lhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = vzecj__lld + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            ivof__spysn = rhs.toordinal()
            tey__btukv = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            rmo__mgbf = rhs.microsecond
            gzkz__fac = lhs.value // 1000
            grt__ttfqu = lhs.nanoseconds
            tti__uut = rmo__mgbf + gzkz__fac
            fecvh__ftmom = 1000000 * (ivof__spysn * 86400 + tey__btukv
                ) + tti__uut
            hhoo__spc = grt__ttfqu
            return compute_pd_timestamp(fecvh__ftmom, hhoo__spc)
        return impl
    if lhs == datetime_datetime_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + rhs.to_pytimedelta()
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs.days + rhs.days
            s = lhs.seconds + rhs.seconds
            us = lhs.microseconds + rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            ges__foh = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            ges__foh = ges__foh + lhs
            qsz__eiw, onv__hcuc = divmod(ges__foh.seconds, 3600)
            qtuc__jrpn, luzf__gdn = divmod(onv__hcuc, 60)
            if 0 < ges__foh.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(ges__foh
                    .days)
                return datetime.datetime(d.year, d.month, d.day, qsz__eiw,
                    qtuc__jrpn, luzf__gdn, ges__foh.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            ges__foh = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            ges__foh = ges__foh + rhs
            qsz__eiw, onv__hcuc = divmod(ges__foh.seconds, 3600)
            qtuc__jrpn, luzf__gdn = divmod(onv__hcuc, 60)
            if 0 < ges__foh.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(ges__foh
                    .days)
                return datetime.datetime(d.year, d.month, d.day, qsz__eiw,
                    qtuc__jrpn, luzf__gdn, ges__foh.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            ubxp__hff = lhs.value - rhs.value
            return pd.Timedelta(ubxp__hff)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_datetime_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs.days - rhs.days
            s = lhs.seconds - rhs.seconds
            us = lhs.microseconds - rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_array_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            uwkq__trj = lhs
            numba.parfors.parfor.init_prange()
            n = len(uwkq__trj)
            A = alloc_datetime_timedelta_array(n)
            for snd__uer in numba.parfors.parfor.internal_prange(n):
                A[snd__uer] = uwkq__trj[snd__uer] - rhs
            return A
        return impl


def overload_mul_operator_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value * rhs)
        return impl
    elif isinstance(lhs, types.Integer) and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return pd.Timedelta(rhs.value * lhs)
        return impl
    if lhs == datetime_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            d = lhs.days * rhs
            s = lhs.seconds * rhs
            us = lhs.microseconds * rhs
            return datetime.timedelta(d, s, us)
        return impl
    elif isinstance(lhs, types.Integer) and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs * rhs.days
            s = lhs * rhs.seconds
            us = lhs * rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl


def overload_floordiv_operator_pd_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs.value // rhs.value
        return impl
    elif lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value // rhs)
        return impl


def overload_truediv_operator_pd_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs.value / rhs.value
        return impl
    elif lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(int(lhs.value / rhs))
        return impl


def overload_mod_operator_timedeltas(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value % rhs.value)
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            gue__hawi = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, gue__hawi)
        return impl


def pd_create_cmp_op_overload(op):

    def overload_pd_timedelta_cmp(lhs, rhs):
        if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

            def impl(lhs, rhs):
                return op(lhs.value, rhs.value)
            return impl
        if lhs == pd_timedelta_type and rhs == bodo.timedelta64ns:
            return lambda lhs, rhs: op(bodo.hiframes.pd_timestamp_ext.
                integer_to_timedelta64(lhs.value), rhs)
        if lhs == bodo.timedelta64ns and rhs == pd_timedelta_type:
            return lambda lhs, rhs: op(lhs, bodo.hiframes.pd_timestamp_ext.
                integer_to_timedelta64(rhs.value))
    return overload_pd_timedelta_cmp


@overload(operator.neg, no_unliteral=True)
def pd_timedelta_neg(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            return pd.Timedelta(-lhs.value)
        return impl


@overload(operator.pos, no_unliteral=True)
def pd_timedelta_pos(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            return lhs
        return impl


@overload(divmod, no_unliteral=True)
def pd_timedelta_divmod(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            kvyh__xoe, gue__hawi = divmod(lhs.value, rhs.value)
            return kvyh__xoe, pd.Timedelta(gue__hawi)
        return impl


@overload(abs, no_unliteral=True)
def pd_timedelta_abs(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            if lhs.value < 0:
                return -lhs
            else:
                return lhs
        return impl


class DatetimeTimeDeltaType(types.Type):

    def __init__(self):
        super(DatetimeTimeDeltaType, self).__init__(name=
            'DatetimeTimeDeltaType()')


datetime_timedelta_type = DatetimeTimeDeltaType()


@typeof_impl.register(datetime.timedelta)
def typeof_datetime_timedelta(val, c):
    return datetime_timedelta_type


@register_model(DatetimeTimeDeltaType)
class DatetimeTimeDeltaModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xegp__qljz = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, xegp__qljz)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    arnl__arb = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    uhcm__qbop = c.pyapi.long_from_longlong(arnl__arb.days)
    aspz__ztu = c.pyapi.long_from_longlong(arnl__arb.seconds)
    nyqo__ndjos = c.pyapi.long_from_longlong(arnl__arb.microseconds)
    wfb__ifrws = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(wfb__ifrws, (uhcm__qbop, aspz__ztu,
        nyqo__ndjos))
    c.pyapi.decref(uhcm__qbop)
    c.pyapi.decref(aspz__ztu)
    c.pyapi.decref(nyqo__ndjos)
    c.pyapi.decref(wfb__ifrws)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    uhcm__qbop = c.pyapi.object_getattr_string(val, 'days')
    aspz__ztu = c.pyapi.object_getattr_string(val, 'seconds')
    nyqo__ndjos = c.pyapi.object_getattr_string(val, 'microseconds')
    qrh__melh = c.pyapi.long_as_longlong(uhcm__qbop)
    zolvl__pngrg = c.pyapi.long_as_longlong(aspz__ztu)
    hejet__vter = c.pyapi.long_as_longlong(nyqo__ndjos)
    arnl__arb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    arnl__arb.days = qrh__melh
    arnl__arb.seconds = zolvl__pngrg
    arnl__arb.microseconds = hejet__vter
    c.pyapi.decref(uhcm__qbop)
    c.pyapi.decref(aspz__ztu)
    c.pyapi.decref(nyqo__ndjos)
    nwcca__zcu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(arnl__arb._getvalue(), is_error=nwcca__zcu)


@lower_constant(DatetimeTimeDeltaType)
def lower_constant_datetime_timedelta(context, builder, ty, pyval):
    days = context.get_constant(types.int64, pyval.days)
    seconds = context.get_constant(types.int64, pyval.seconds)
    microseconds = context.get_constant(types.int64, pyval.microseconds)
    return lir.Constant.literal_struct([days, seconds, microseconds])


@overload(datetime.timedelta, no_unliteral=True)
def datetime_timedelta(days=0, seconds=0, microseconds=0, milliseconds=0,
    minutes=0, hours=0, weeks=0):

    def impl_timedelta(days=0, seconds=0, microseconds=0, milliseconds=0,
        minutes=0, hours=0, weeks=0):
        d = s = us = 0
        days += weeks * 7
        seconds += minutes * 60 + hours * 3600
        microseconds += milliseconds * 1000
        d = days
        days, seconds = divmod(seconds, 24 * 3600)
        d += days
        s += int(seconds)
        seconds, us = divmod(microseconds, 1000000)
        days, seconds = divmod(seconds, 24 * 3600)
        d += days
        s += seconds
        return init_timedelta(d, s, us)
    return impl_timedelta


@intrinsic
def init_timedelta(typingctx, d, s, us):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        timedelta = cgutils.create_struct_proxy(typ)(context, builder)
        timedelta.days = args[0]
        timedelta.seconds = args[1]
        timedelta.microseconds = args[2]
        return timedelta._getvalue()
    return DatetimeTimeDeltaType()(d, s, us), codegen


make_attribute_wrapper(DatetimeTimeDeltaType, 'days', '_days')
make_attribute_wrapper(DatetimeTimeDeltaType, 'seconds', '_seconds')
make_attribute_wrapper(DatetimeTimeDeltaType, 'microseconds', '_microseconds')


@overload_attribute(DatetimeTimeDeltaType, 'days')
def timedelta_get_days(td):

    def impl(td):
        return td._days
    return impl


@overload_attribute(DatetimeTimeDeltaType, 'seconds')
def timedelta_get_seconds(td):

    def impl(td):
        return td._seconds
    return impl


@overload_attribute(DatetimeTimeDeltaType, 'microseconds')
def timedelta_get_microseconds(td):

    def impl(td):
        return td._microseconds
    return impl


@overload_method(DatetimeTimeDeltaType, 'total_seconds', no_unliteral=True)
def total_seconds(td):

    def impl(td):
        return ((td._days * 86400 + td._seconds) * 10 ** 6 + td._microseconds
            ) / 10 ** 6
    return impl


@overload_method(DatetimeTimeDeltaType, '__hash__', no_unliteral=True)
def __hash__(td):

    def impl(td):
        return hash((td._days, td._seconds, td._microseconds))
    return impl


@register_jitable
def _to_nanoseconds(td):
    return np.int64(((td._days * 86400 + td._seconds) * 1000000 + td.
        _microseconds) * 1000)


@register_jitable
def _to_microseconds(td):
    return (td._days * (24 * 3600) + td._seconds) * 1000000 + td._microseconds


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


@register_jitable
def _getstate(td):
    return td._days, td._seconds, td._microseconds


@register_jitable
def _divide_and_round(a, b):
    kvyh__xoe, gue__hawi = divmod(a, b)
    gue__hawi *= 2
    xeihd__pvusw = gue__hawi > b if b > 0 else gue__hawi < b
    if xeihd__pvusw or gue__hawi == b and kvyh__xoe % 2 == 1:
        kvyh__xoe += 1
    return kvyh__xoe


_MAXORDINAL = 3652059


def overload_floordiv_operator_dt_timedelta(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return us // _to_microseconds(rhs)
        return impl
    elif lhs == datetime_timedelta_type and rhs == types.int64:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return datetime.timedelta(0, 0, us // rhs)
        return impl


def overload_truediv_operator_dt_timedelta(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return us / _to_microseconds(rhs)
        return impl
    elif lhs == datetime_timedelta_type and rhs == types.int64:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return datetime.timedelta(0, 0, _divide_and_round(us, rhs))
        return impl


def create_cmp_op_overload(op):

    def overload_timedelta_cmp(lhs, rhs):
        if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

            def impl(lhs, rhs):
                wwl__jtk = _cmp(_getstate(lhs), _getstate(rhs))
                return op(wwl__jtk, 0)
            return impl
    return overload_timedelta_cmp


@overload(operator.neg, no_unliteral=True)
def timedelta_neg(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            return datetime.timedelta(-lhs.days, -lhs.seconds, -lhs.
                microseconds)
        return impl


@overload(operator.pos, no_unliteral=True)
def timedelta_pos(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            return lhs
        return impl


@overload(divmod, no_unliteral=True)
def timedelta_divmod(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            kvyh__xoe, gue__hawi = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return kvyh__xoe, datetime.timedelta(0, 0, gue__hawi)
        return impl


@overload(abs, no_unliteral=True)
def timedelta_abs(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            if lhs.days < 0:
                return -lhs
            else:
                return lhs
        return impl


@intrinsic
def cast_numpy_timedelta_to_int(typingctx, val=None):
    assert val in (types.NPTimedelta('ns'), types.int64)

    def codegen(context, builder, signature, args):
        return args[0]
    return types.int64(val), codegen


@overload(bool, no_unliteral=True)
def timedelta_to_bool(timedelta):
    if timedelta != datetime_timedelta_type:
        return
    zfkxk__kux = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != zfkxk__kux
    return impl


class DatetimeTimeDeltaArrayType(types.ArrayCompatible):

    def __init__(self):
        super(DatetimeTimeDeltaArrayType, self).__init__(name=
            'DatetimeTimeDeltaArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return datetime_timedelta_type

    def copy(self):
        return DatetimeTimeDeltaArrayType()


datetime_timedelta_array_type = DatetimeTimeDeltaArrayType()
types.datetime_timedelta_array_type = datetime_timedelta_array_type
days_data_type = types.Array(types.int64, 1, 'C')
seconds_data_type = types.Array(types.int64, 1, 'C')
microseconds_data_type = types.Array(types.int64, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(DatetimeTimeDeltaArrayType)
class DatetimeTimeDeltaArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xegp__qljz = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, xegp__qljz)


make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'days_data', '_days_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'seconds_data',
    '_seconds_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'microseconds_data',
    '_microseconds_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'null_bitmap',
    '_null_bitmap')


@overload_method(DatetimeTimeDeltaArrayType, 'copy', no_unliteral=True)
def overload_datetime_timedelta_arr_copy(A):
    return (lambda A: bodo.hiframes.datetime_timedelta_ext.
        init_datetime_timedelta_array(A._days_data.copy(), A._seconds_data.
        copy(), A._microseconds_data.copy(), A._null_bitmap.copy()))


@unbox(DatetimeTimeDeltaArrayType)
def unbox_datetime_timedelta_array(typ, val, c):
    n = bodo.utils.utils.object_length(c, val)
    erf__urnxe = types.Array(types.intp, 1, 'C')
    zjg__rye = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        erf__urnxe, [n])
    ubkz__kkr = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        erf__urnxe, [n])
    plwyd__zpj = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        erf__urnxe, [n])
    rgm__tjv = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64),
        7)), lir.Constant(lir.IntType(64), 8))
    tkdl__wba = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types
        .Array(types.uint8, 1, 'C'), [rgm__tjv])
    dsr__geg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer(
        ), lir.IntType(64), lir.IntType(64).as_pointer(), lir.IntType(64).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer()])
    papqt__iue = cgutils.get_or_insert_function(c.builder.module, dsr__geg,
        name='unbox_datetime_timedelta_array')
    c.builder.call(papqt__iue, [val, n, zjg__rye.data, ubkz__kkr.data,
        plwyd__zpj.data, tkdl__wba.data])
    sgqvz__tlv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    sgqvz__tlv.days_data = zjg__rye._getvalue()
    sgqvz__tlv.seconds_data = ubkz__kkr._getvalue()
    sgqvz__tlv.microseconds_data = plwyd__zpj._getvalue()
    sgqvz__tlv.null_bitmap = tkdl__wba._getvalue()
    nwcca__zcu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(sgqvz__tlv._getvalue(), is_error=nwcca__zcu)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    uwkq__trj = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    zjg__rye = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, uwkq__trj.days_data)
    ubkz__kkr = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, uwkq__trj.seconds_data).data
    plwyd__zpj = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, uwkq__trj.microseconds_data).data
    gbncz__pxrog = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, uwkq__trj.null_bitmap).data
    n = c.builder.extract_value(zjg__rye.shape, 0)
    dsr__geg = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    fzxh__wvzlz = cgutils.get_or_insert_function(c.builder.module, dsr__geg,
        name='box_datetime_timedelta_array')
    snn__gro = c.builder.call(fzxh__wvzlz, [n, zjg__rye.data, ubkz__kkr,
        plwyd__zpj, gbncz__pxrog])
    c.context.nrt.decref(c.builder, typ, val)
    return snn__gro


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        ygp__lri, kalam__ztuiv, yqrq__pid, crti__iqv = args
        ewwev__pvcsd = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        ewwev__pvcsd.days_data = ygp__lri
        ewwev__pvcsd.seconds_data = kalam__ztuiv
        ewwev__pvcsd.microseconds_data = yqrq__pid
        ewwev__pvcsd.null_bitmap = crti__iqv
        context.nrt.incref(builder, signature.args[0], ygp__lri)
        context.nrt.incref(builder, signature.args[1], kalam__ztuiv)
        context.nrt.incref(builder, signature.args[2], yqrq__pid)
        context.nrt.incref(builder, signature.args[3], crti__iqv)
        return ewwev__pvcsd._getvalue()
    njtx__goao = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return njtx__goao, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    zjg__rye = np.empty(n, np.int64)
    ubkz__kkr = np.empty(n, np.int64)
    plwyd__zpj = np.empty(n, np.int64)
    gmumx__uthb = np.empty(n + 7 >> 3, np.uint8)
    for snd__uer, s in enumerate(pyval):
        mzoen__yesj = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(gmumx__uthb, snd__uer, int(not
            mzoen__yesj))
        if not mzoen__yesj:
            zjg__rye[snd__uer] = s.days
            ubkz__kkr[snd__uer] = s.seconds
            plwyd__zpj[snd__uer] = s.microseconds
    hkpz__bkll = context.get_constant_generic(builder, days_data_type, zjg__rye
        )
    kwt__dbfng = context.get_constant_generic(builder, seconds_data_type,
        ubkz__kkr)
    ianbq__yct = context.get_constant_generic(builder,
        microseconds_data_type, plwyd__zpj)
    bsml__otax = context.get_constant_generic(builder, nulls_type, gmumx__uthb)
    return lir.Constant.literal_struct([hkpz__bkll, kwt__dbfng, ianbq__yct,
        bsml__otax])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    zjg__rye = np.empty(n, dtype=np.int64)
    ubkz__kkr = np.empty(n, dtype=np.int64)
    plwyd__zpj = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(zjg__rye, ubkz__kkr, plwyd__zpj, nulls
        )


def alloc_datetime_timedelta_array_equiv(self, scope, equiv_set, loc, args, kws
    ):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_datetime_timedelta_ext_alloc_datetime_timedelta_array
    ) = alloc_datetime_timedelta_array_equiv


@overload(operator.getitem, no_unliteral=True)
def dt_timedelta_arr_getitem(A, ind):
    if A != datetime_timedelta_array_type:
        return
    if isinstance(ind, types.Integer):

        def impl_int(A, ind):
            return datetime.timedelta(days=A._days_data[ind], seconds=A.
                _seconds_data[ind], microseconds=A._microseconds_data[ind])
        return impl_int
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            exa__tsle = bodo.utils.conversion.coerce_to_ndarray(ind)
            ypwuw__lslbr = A._null_bitmap
            djked__rhlo = A._days_data[exa__tsle]
            awf__xmgp = A._seconds_data[exa__tsle]
            ufch__hhhon = A._microseconds_data[exa__tsle]
            n = len(djked__rhlo)
            wyiw__qduca = get_new_null_mask_bool_index(ypwuw__lslbr, ind, n)
            return init_datetime_timedelta_array(djked__rhlo, awf__xmgp,
                ufch__hhhon, wyiw__qduca)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            exa__tsle = bodo.utils.conversion.coerce_to_ndarray(ind)
            ypwuw__lslbr = A._null_bitmap
            djked__rhlo = A._days_data[exa__tsle]
            awf__xmgp = A._seconds_data[exa__tsle]
            ufch__hhhon = A._microseconds_data[exa__tsle]
            n = len(djked__rhlo)
            wyiw__qduca = get_new_null_mask_int_index(ypwuw__lslbr,
                exa__tsle, n)
            return init_datetime_timedelta_array(djked__rhlo, awf__xmgp,
                ufch__hhhon, wyiw__qduca)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            ypwuw__lslbr = A._null_bitmap
            djked__rhlo = np.ascontiguousarray(A._days_data[ind])
            awf__xmgp = np.ascontiguousarray(A._seconds_data[ind])
            ufch__hhhon = np.ascontiguousarray(A._microseconds_data[ind])
            wyiw__qduca = get_new_null_mask_slice_index(ypwuw__lslbr, ind, n)
            return init_datetime_timedelta_array(djked__rhlo, awf__xmgp,
                ufch__hhhon, wyiw__qduca)
        return impl_slice
    raise BodoError(
        f'getitem for DatetimeTimedeltaArray with indexing type {ind} not supported.'
        )


@overload(operator.setitem, no_unliteral=True)
def dt_timedelta_arr_setitem(A, ind, val):
    if A != datetime_timedelta_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    twjg__zpd = (
        f"setitem for DatetimeTimedeltaArray with indexing type {ind} received an incorrect 'value' type {val}."
        )
    if isinstance(ind, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl(A, ind, val):
                A._days_data[ind] = val._days
                A._seconds_data[ind] = val._seconds
                A._microseconds_data[ind] = val._microseconds
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, ind, 1)
            return impl
        else:
            raise BodoError(twjg__zpd)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(twjg__zpd)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for snd__uer in range(n):
                    A._days_data[ind[snd__uer]] = val._days
                    A._seconds_data[ind[snd__uer]] = val._seconds
                    A._microseconds_data[ind[snd__uer]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[snd__uer], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for snd__uer in range(n):
                    A._days_data[ind[snd__uer]] = val._days_data[snd__uer]
                    A._seconds_data[ind[snd__uer]] = val._seconds_data[snd__uer
                        ]
                    A._microseconds_data[ind[snd__uer]
                        ] = val._microseconds_data[snd__uer]
                    xrm__lbkmy = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, snd__uer)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[snd__uer], xrm__lbkmy)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for snd__uer in range(n):
                    if not bodo.libs.array_kernels.isna(ind, snd__uer) and ind[
                        snd__uer]:
                        A._days_data[snd__uer] = val._days
                        A._seconds_data[snd__uer] = val._seconds
                        A._microseconds_data[snd__uer] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            snd__uer, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                nsbpe__hlmv = 0
                for snd__uer in range(n):
                    if not bodo.libs.array_kernels.isna(ind, snd__uer) and ind[
                        snd__uer]:
                        A._days_data[snd__uer] = val._days_data[nsbpe__hlmv]
                        A._seconds_data[snd__uer] = val._seconds_data[
                            nsbpe__hlmv]
                        A._microseconds_data[snd__uer
                            ] = val._microseconds_data[nsbpe__hlmv]
                        xrm__lbkmy = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, nsbpe__hlmv)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            snd__uer, xrm__lbkmy)
                        nsbpe__hlmv += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                hmus__fmhf = numba.cpython.unicode._normalize_slice(ind, len(A)
                    )
                for snd__uer in range(hmus__fmhf.start, hmus__fmhf.stop,
                    hmus__fmhf.step):
                    A._days_data[snd__uer] = val._days
                    A._seconds_data[snd__uer] = val._seconds
                    A._microseconds_data[snd__uer] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        snd__uer, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                vnto__nxwq = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, vnto__nxwq,
                    ind, n)
            return impl_slice_mask
    raise BodoError(
        f'setitem for DatetimeTimedeltaArray with indexing type {ind} not supported.'
        )


@overload(len, no_unliteral=True)
def overload_len_datetime_timedelta_arr(A):
    if A == datetime_timedelta_array_type:
        return lambda A: len(A._days_data)


@overload_attribute(DatetimeTimeDeltaArrayType, 'shape')
def overload_datetime_timedelta_arr_shape(A):
    return lambda A: (len(A._days_data),)


@overload_attribute(DatetimeTimeDeltaArrayType, 'nbytes')
def timedelta_arr_nbytes_overload(A):
    return (lambda A: A._days_data.nbytes + A._seconds_data.nbytes + A.
        _microseconds_data.nbytes + A._null_bitmap.nbytes)


def overload_datetime_timedelta_arr_sub(arg1, arg2):
    if (arg1 == datetime_timedelta_array_type and arg2 ==
        datetime_timedelta_type):

        def impl(arg1, arg2):
            uwkq__trj = arg1
            numba.parfors.parfor.init_prange()
            n = len(uwkq__trj)
            A = alloc_datetime_timedelta_array(n)
            for snd__uer in numba.parfors.parfor.internal_prange(n):
                A[snd__uer] = uwkq__trj[snd__uer] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            yen__xpz = True
        else:
            yen__xpz = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                kzchv__zmvkc = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for snd__uer in numba.parfors.parfor.internal_prange(n):
                    rguje__tlp = bodo.libs.array_kernels.isna(lhs, snd__uer)
                    uoqf__weh = bodo.libs.array_kernels.isna(rhs, snd__uer)
                    if rguje__tlp or uoqf__weh:
                        bhw__kiabm = yen__xpz
                    else:
                        bhw__kiabm = op(lhs[snd__uer], rhs[snd__uer])
                    kzchv__zmvkc[snd__uer] = bhw__kiabm
                return kzchv__zmvkc
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                kzchv__zmvkc = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for snd__uer in numba.parfors.parfor.internal_prange(n):
                    xrm__lbkmy = bodo.libs.array_kernels.isna(lhs, snd__uer)
                    if xrm__lbkmy:
                        bhw__kiabm = yen__xpz
                    else:
                        bhw__kiabm = op(lhs[snd__uer], rhs)
                    kzchv__zmvkc[snd__uer] = bhw__kiabm
                return kzchv__zmvkc
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                kzchv__zmvkc = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for snd__uer in numba.parfors.parfor.internal_prange(n):
                    xrm__lbkmy = bodo.libs.array_kernels.isna(rhs, snd__uer)
                    if xrm__lbkmy:
                        bhw__kiabm = yen__xpz
                    else:
                        bhw__kiabm = op(lhs, rhs[snd__uer])
                    kzchv__zmvkc[snd__uer] = bhw__kiabm
                return kzchv__zmvkc
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for qhw__gaqfi in timedelta_unsupported_attrs:
        thf__flnb = 'pandas.Timedelta.' + qhw__gaqfi
        overload_attribute(PDTimeDeltaType, qhw__gaqfi)(
            create_unsupported_overload(thf__flnb))
    for qwfj__lsf in timedelta_unsupported_methods:
        thf__flnb = 'pandas.Timedelta.' + qwfj__lsf
        overload_method(PDTimeDeltaType, qwfj__lsf)(create_unsupported_overload
            (thf__flnb + '()'))


_intstall_pd_timedelta_unsupported()
