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
        pqaz__qyc = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, pqaz__qyc)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    whwdo__ehbqj = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ofd__zby = c.pyapi.long_from_longlong(whwdo__ehbqj.value)
    wysgw__gkp = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(wysgw__gkp, (ofd__zby,))
    c.pyapi.decref(ofd__zby)
    c.pyapi.decref(wysgw__gkp)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    ofd__zby = c.pyapi.object_getattr_string(val, 'value')
    suz__ngga = c.pyapi.long_as_longlong(ofd__zby)
    whwdo__ehbqj = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    whwdo__ehbqj.value = suz__ngga
    c.pyapi.decref(ofd__zby)
    phyh__xikt = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(whwdo__ehbqj._getvalue(), is_error=phyh__xikt)


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
            hey__lpzi = 1000 * microseconds
            return init_pd_timedelta(hey__lpzi)
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
            hey__lpzi = 1000 * microseconds
            return init_pd_timedelta(hey__lpzi)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    zkdq__mxhqg, zhbt__mulga = pd._libs.tslibs.conversion.precision_from_unit(
        unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * zkdq__mxhqg)
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
            utr__klft = (rhs.microseconds + (rhs.seconds + rhs.days * 60 * 
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + utr__klft
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            gtgxp__kac = (lhs.microseconds + (lhs.seconds + lhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = gtgxp__kac + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            tutl__vmo = rhs.toordinal()
            fyl__jikr = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            tzz__onauv = rhs.microsecond
            kswt__wajjm = lhs.value // 1000
            gzcm__nsx = lhs.nanoseconds
            jgi__nqm = tzz__onauv + kswt__wajjm
            knxy__ncg = 1000000 * (tutl__vmo * 86400 + fyl__jikr) + jgi__nqm
            hrbr__quak = gzcm__nsx
            return compute_pd_timestamp(knxy__ncg, hrbr__quak)
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
            afy__kpkh = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            afy__kpkh = afy__kpkh + lhs
            bncv__zhhf, yfsn__igyit = divmod(afy__kpkh.seconds, 3600)
            iba__lbdhc, pzfl__wcbpm = divmod(yfsn__igyit, 60)
            if 0 < afy__kpkh.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(afy__kpkh
                    .days)
                return datetime.datetime(d.year, d.month, d.day, bncv__zhhf,
                    iba__lbdhc, pzfl__wcbpm, afy__kpkh.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            afy__kpkh = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            afy__kpkh = afy__kpkh + rhs
            bncv__zhhf, yfsn__igyit = divmod(afy__kpkh.seconds, 3600)
            iba__lbdhc, pzfl__wcbpm = divmod(yfsn__igyit, 60)
            if 0 < afy__kpkh.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(afy__kpkh
                    .days)
                return datetime.datetime(d.year, d.month, d.day, bncv__zhhf,
                    iba__lbdhc, pzfl__wcbpm, afy__kpkh.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            xpbwa__kqm = lhs.value - rhs.value
            return pd.Timedelta(xpbwa__kqm)
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
            fbdim__lxzhd = lhs
            numba.parfors.parfor.init_prange()
            n = len(fbdim__lxzhd)
            A = alloc_datetime_timedelta_array(n)
            for nmwm__ldjc in numba.parfors.parfor.internal_prange(n):
                A[nmwm__ldjc] = fbdim__lxzhd[nmwm__ldjc] - rhs
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
            vory__jhbu = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, vory__jhbu)
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
            zsvc__svwcs, vory__jhbu = divmod(lhs.value, rhs.value)
            return zsvc__svwcs, pd.Timedelta(vory__jhbu)
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
        pqaz__qyc = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, pqaz__qyc)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    whwdo__ehbqj = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    khicw__piz = c.pyapi.long_from_longlong(whwdo__ehbqj.days)
    dkae__ctcw = c.pyapi.long_from_longlong(whwdo__ehbqj.seconds)
    dvyi__fqmz = c.pyapi.long_from_longlong(whwdo__ehbqj.microseconds)
    wysgw__gkp = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(wysgw__gkp, (khicw__piz, dkae__ctcw,
        dvyi__fqmz))
    c.pyapi.decref(khicw__piz)
    c.pyapi.decref(dkae__ctcw)
    c.pyapi.decref(dvyi__fqmz)
    c.pyapi.decref(wysgw__gkp)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    khicw__piz = c.pyapi.object_getattr_string(val, 'days')
    dkae__ctcw = c.pyapi.object_getattr_string(val, 'seconds')
    dvyi__fqmz = c.pyapi.object_getattr_string(val, 'microseconds')
    kxa__zzle = c.pyapi.long_as_longlong(khicw__piz)
    icke__lyor = c.pyapi.long_as_longlong(dkae__ctcw)
    jvqjo__prnug = c.pyapi.long_as_longlong(dvyi__fqmz)
    whwdo__ehbqj = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    whwdo__ehbqj.days = kxa__zzle
    whwdo__ehbqj.seconds = icke__lyor
    whwdo__ehbqj.microseconds = jvqjo__prnug
    c.pyapi.decref(khicw__piz)
    c.pyapi.decref(dkae__ctcw)
    c.pyapi.decref(dvyi__fqmz)
    phyh__xikt = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(whwdo__ehbqj._getvalue(), is_error=phyh__xikt)


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
    zsvc__svwcs, vory__jhbu = divmod(a, b)
    vory__jhbu *= 2
    fifh__auyx = vory__jhbu > b if b > 0 else vory__jhbu < b
    if fifh__auyx or vory__jhbu == b and zsvc__svwcs % 2 == 1:
        zsvc__svwcs += 1
    return zsvc__svwcs


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
                csbab__jqnxi = _cmp(_getstate(lhs), _getstate(rhs))
                return op(csbab__jqnxi, 0)
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
            zsvc__svwcs, vory__jhbu = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return zsvc__svwcs, datetime.timedelta(0, 0, vory__jhbu)
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
    wpcbk__bnaw = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != wpcbk__bnaw
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
        pqaz__qyc = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, pqaz__qyc)


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
    axp__tmhjd = types.Array(types.intp, 1, 'C')
    irqr__yowk = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        axp__tmhjd, [n])
    aqntk__fizp = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        axp__tmhjd, [n])
    pbik__ock = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        axp__tmhjd, [n])
    ihca__ovij = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    nwuq__nxog = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [ihca__ovij])
    fprcz__cmozs = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    les__jhpjx = cgutils.get_or_insert_function(c.builder.module,
        fprcz__cmozs, name='unbox_datetime_timedelta_array')
    c.builder.call(les__jhpjx, [val, n, irqr__yowk.data, aqntk__fizp.data,
        pbik__ock.data, nwuq__nxog.data])
    irjwd__ziu = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    irjwd__ziu.days_data = irqr__yowk._getvalue()
    irjwd__ziu.seconds_data = aqntk__fizp._getvalue()
    irjwd__ziu.microseconds_data = pbik__ock._getvalue()
    irjwd__ziu.null_bitmap = nwuq__nxog._getvalue()
    phyh__xikt = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(irjwd__ziu._getvalue(), is_error=phyh__xikt)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    fbdim__lxzhd = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    irqr__yowk = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, fbdim__lxzhd.days_data)
    aqntk__fizp = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, fbdim__lxzhd.seconds_data).data
    pbik__ock = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, fbdim__lxzhd.microseconds_data).data
    vrj__rxdmb = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, fbdim__lxzhd.null_bitmap).data
    n = c.builder.extract_value(irqr__yowk.shape, 0)
    fprcz__cmozs = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    ezo__noljj = cgutils.get_or_insert_function(c.builder.module,
        fprcz__cmozs, name='box_datetime_timedelta_array')
    mkgf__faqea = c.builder.call(ezo__noljj, [n, irqr__yowk.data,
        aqntk__fizp, pbik__ock, vrj__rxdmb])
    c.context.nrt.decref(c.builder, typ, val)
    return mkgf__faqea


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        uxo__lbpaz, kvt__nvcq, icxx__flkgy, udpl__wbz = args
        swrai__wqbb = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        swrai__wqbb.days_data = uxo__lbpaz
        swrai__wqbb.seconds_data = kvt__nvcq
        swrai__wqbb.microseconds_data = icxx__flkgy
        swrai__wqbb.null_bitmap = udpl__wbz
        context.nrt.incref(builder, signature.args[0], uxo__lbpaz)
        context.nrt.incref(builder, signature.args[1], kvt__nvcq)
        context.nrt.incref(builder, signature.args[2], icxx__flkgy)
        context.nrt.incref(builder, signature.args[3], udpl__wbz)
        return swrai__wqbb._getvalue()
    opwri__airfv = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return opwri__airfv, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    irqr__yowk = np.empty(n, np.int64)
    aqntk__fizp = np.empty(n, np.int64)
    pbik__ock = np.empty(n, np.int64)
    pvc__azred = np.empty(n + 7 >> 3, np.uint8)
    for nmwm__ldjc, s in enumerate(pyval):
        dhqhd__ifgj = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(pvc__azred, nmwm__ldjc, int(
            not dhqhd__ifgj))
        if not dhqhd__ifgj:
            irqr__yowk[nmwm__ldjc] = s.days
            aqntk__fizp[nmwm__ldjc] = s.seconds
            pbik__ock[nmwm__ldjc] = s.microseconds
    dpck__jctc = context.get_constant_generic(builder, days_data_type,
        irqr__yowk)
    vsalx__offcd = context.get_constant_generic(builder, seconds_data_type,
        aqntk__fizp)
    ltcby__oyju = context.get_constant_generic(builder,
        microseconds_data_type, pbik__ock)
    kzbu__tcqs = context.get_constant_generic(builder, nulls_type, pvc__azred)
    return lir.Constant.literal_struct([dpck__jctc, vsalx__offcd,
        ltcby__oyju, kzbu__tcqs])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    irqr__yowk = np.empty(n, dtype=np.int64)
    aqntk__fizp = np.empty(n, dtype=np.int64)
    pbik__ock = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(irqr__yowk, aqntk__fizp, pbik__ock,
        nulls)


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
            trvz__nxw = bodo.utils.conversion.coerce_to_ndarray(ind)
            qil__dcgcv = A._null_bitmap
            iup__bzev = A._days_data[trvz__nxw]
            hgqma__csb = A._seconds_data[trvz__nxw]
            uavp__lnbm = A._microseconds_data[trvz__nxw]
            n = len(iup__bzev)
            ghzz__hyzj = get_new_null_mask_bool_index(qil__dcgcv, ind, n)
            return init_datetime_timedelta_array(iup__bzev, hgqma__csb,
                uavp__lnbm, ghzz__hyzj)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            trvz__nxw = bodo.utils.conversion.coerce_to_ndarray(ind)
            qil__dcgcv = A._null_bitmap
            iup__bzev = A._days_data[trvz__nxw]
            hgqma__csb = A._seconds_data[trvz__nxw]
            uavp__lnbm = A._microseconds_data[trvz__nxw]
            n = len(iup__bzev)
            ghzz__hyzj = get_new_null_mask_int_index(qil__dcgcv, trvz__nxw, n)
            return init_datetime_timedelta_array(iup__bzev, hgqma__csb,
                uavp__lnbm, ghzz__hyzj)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            qil__dcgcv = A._null_bitmap
            iup__bzev = np.ascontiguousarray(A._days_data[ind])
            hgqma__csb = np.ascontiguousarray(A._seconds_data[ind])
            uavp__lnbm = np.ascontiguousarray(A._microseconds_data[ind])
            ghzz__hyzj = get_new_null_mask_slice_index(qil__dcgcv, ind, n)
            return init_datetime_timedelta_array(iup__bzev, hgqma__csb,
                uavp__lnbm, ghzz__hyzj)
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
    otp__lpiu = (
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
            raise BodoError(otp__lpiu)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(otp__lpiu)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for nmwm__ldjc in range(n):
                    A._days_data[ind[nmwm__ldjc]] = val._days
                    A._seconds_data[ind[nmwm__ldjc]] = val._seconds
                    A._microseconds_data[ind[nmwm__ldjc]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[nmwm__ldjc], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for nmwm__ldjc in range(n):
                    A._days_data[ind[nmwm__ldjc]] = val._days_data[nmwm__ldjc]
                    A._seconds_data[ind[nmwm__ldjc]] = val._seconds_data[
                        nmwm__ldjc]
                    A._microseconds_data[ind[nmwm__ldjc]
                        ] = val._microseconds_data[nmwm__ldjc]
                    goti__clt = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, nmwm__ldjc)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[nmwm__ldjc], goti__clt)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for nmwm__ldjc in range(n):
                    if not bodo.libs.array_kernels.isna(ind, nmwm__ldjc
                        ) and ind[nmwm__ldjc]:
                        A._days_data[nmwm__ldjc] = val._days
                        A._seconds_data[nmwm__ldjc] = val._seconds
                        A._microseconds_data[nmwm__ldjc] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            nmwm__ldjc, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                mfnr__qtd = 0
                for nmwm__ldjc in range(n):
                    if not bodo.libs.array_kernels.isna(ind, nmwm__ldjc
                        ) and ind[nmwm__ldjc]:
                        A._days_data[nmwm__ldjc] = val._days_data[mfnr__qtd]
                        A._seconds_data[nmwm__ldjc] = val._seconds_data[
                            mfnr__qtd]
                        A._microseconds_data[nmwm__ldjc
                            ] = val._microseconds_data[mfnr__qtd]
                        goti__clt = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, mfnr__qtd)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            nmwm__ldjc, goti__clt)
                        mfnr__qtd += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                dnk__qllh = numba.cpython.unicode._normalize_slice(ind, len(A))
                for nmwm__ldjc in range(dnk__qllh.start, dnk__qllh.stop,
                    dnk__qllh.step):
                    A._days_data[nmwm__ldjc] = val._days
                    A._seconds_data[nmwm__ldjc] = val._seconds
                    A._microseconds_data[nmwm__ldjc] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        nmwm__ldjc, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                btqu__qxrl = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, btqu__qxrl,
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
            fbdim__lxzhd = arg1
            numba.parfors.parfor.init_prange()
            n = len(fbdim__lxzhd)
            A = alloc_datetime_timedelta_array(n)
            for nmwm__ldjc in numba.parfors.parfor.internal_prange(n):
                A[nmwm__ldjc] = fbdim__lxzhd[nmwm__ldjc] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            rvvil__jpf = True
        else:
            rvvil__jpf = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                kui__adwa = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for nmwm__ldjc in numba.parfors.parfor.internal_prange(n):
                    laql__hioe = bodo.libs.array_kernels.isna(lhs, nmwm__ldjc)
                    gmko__tqbn = bodo.libs.array_kernels.isna(rhs, nmwm__ldjc)
                    if laql__hioe or gmko__tqbn:
                        qai__cve = rvvil__jpf
                    else:
                        qai__cve = op(lhs[nmwm__ldjc], rhs[nmwm__ldjc])
                    kui__adwa[nmwm__ldjc] = qai__cve
                return kui__adwa
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                kui__adwa = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for nmwm__ldjc in numba.parfors.parfor.internal_prange(n):
                    goti__clt = bodo.libs.array_kernels.isna(lhs, nmwm__ldjc)
                    if goti__clt:
                        qai__cve = rvvil__jpf
                    else:
                        qai__cve = op(lhs[nmwm__ldjc], rhs)
                    kui__adwa[nmwm__ldjc] = qai__cve
                return kui__adwa
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                kui__adwa = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for nmwm__ldjc in numba.parfors.parfor.internal_prange(n):
                    goti__clt = bodo.libs.array_kernels.isna(rhs, nmwm__ldjc)
                    if goti__clt:
                        qai__cve = rvvil__jpf
                    else:
                        qai__cve = op(lhs, rhs[nmwm__ldjc])
                    kui__adwa[nmwm__ldjc] = qai__cve
                return kui__adwa
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for stx__qitlv in timedelta_unsupported_attrs:
        wvqg__bley = 'pandas.Timedelta.' + stx__qitlv
        overload_attribute(PDTimeDeltaType, stx__qitlv)(
            create_unsupported_overload(wvqg__bley))
    for fmofr__bnocl in timedelta_unsupported_methods:
        wvqg__bley = 'pandas.Timedelta.' + fmofr__bnocl
        overload_method(PDTimeDeltaType, fmofr__bnocl)(
            create_unsupported_overload(wvqg__bley + '()'))


_intstall_pd_timedelta_unsupported()
