"""
JIT support for Python's logging module
"""
import logging
import numba
from numba.core import types
from numba.core.imputils import lower_constant
from numba.core.typing.templates import bound_function
from numba.core.typing.templates import AttributeTemplate, infer_getattr, signature
from numba.extending import NativeValue, box, models, overload_attribute, overload_method, register_model, typeof_impl, unbox
from bodo.utils.typing import create_unsupported_overload, gen_objmode_attr_overload


class LoggingLoggerType(types.Type):

    def __init__(self, is_root=False):
        self.is_root = is_root
        super(LoggingLoggerType, self).__init__(name=
            f'LoggingLoggerType(is_root={is_root})')


@typeof_impl.register(logging.RootLogger)
@typeof_impl.register(logging.Logger)
def typeof_logging(val, c):
    if isinstance(val, logging.RootLogger):
        return LoggingLoggerType(is_root=True)
    else:
        return LoggingLoggerType(is_root=False)


register_model(LoggingLoggerType)(models.OpaqueModel)


@box(LoggingLoggerType)
def box_logging_logger(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(LoggingLoggerType)
def unbox_logging_logger(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@lower_constant(LoggingLoggerType)
def lower_constant_logger(context, builder, ty, pyval):
    drbm__ztio = context.get_python_api(builder)
    return drbm__ztio.unserialize(drbm__ztio.serialize_object(pyval))


gen_objmode_attr_overload(LoggingLoggerType, 'level', None, types.int64)
gen_objmode_attr_overload(LoggingLoggerType, 'name', None, 'unicode_type')
gen_objmode_attr_overload(LoggingLoggerType, 'propagate', None, types.boolean)
gen_objmode_attr_overload(LoggingLoggerType, 'disabled', None, types.boolean)
gen_objmode_attr_overload(LoggingLoggerType, 'parent', None,
    LoggingLoggerType())
gen_objmode_attr_overload(LoggingLoggerType, 'root', None,
    LoggingLoggerType(is_root=True))


@infer_getattr
class LoggingLoggerAttribute(AttributeTemplate):
    key = LoggingLoggerType

    def _resolve_helper(self, logger_typ, args, kws):
        kws = dict(kws)
        ajall__gznmd = ', '.join('e{}'.format(iwh__xfk) for iwh__xfk in
            range(len(args)))
        if ajall__gznmd:
            ajall__gznmd += ', '
        mrj__amafa = ', '.join("{} = ''".format(ycej__ixr) for ycej__ixr in
            kws.keys())
        vzck__vqzen = (
            f'def format_stub(string, {ajall__gznmd} {mrj__amafa}):\n')
        vzck__vqzen += '    pass\n'
        rxz__ixv = {}
        exec(vzck__vqzen, {}, rxz__ixv)
        damh__qbra = rxz__ixv['format_stub']
        tbryk__trcp = numba.core.utils.pysignature(damh__qbra)
        vui__mosjk = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, vui__mosjk).replace(pysig=tbryk__trcp)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for acv__ityy in ('logging.Logger', 'logging.RootLogger'):
        for kxk__ofmj in func_names:
            rge__ble = f'@bound_function("{acv__ityy}.{kxk__ofmj}")\n'
            rge__ble += (
                f'def resolve_{kxk__ofmj}(self, logger_typ, args, kws):\n')
            rge__ble += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(rge__ble)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for cbymh__aerfq in logging_logger_unsupported_attrs:
        jpb__frwr = 'logging.Logger.' + cbymh__aerfq
        overload_attribute(LoggingLoggerType, cbymh__aerfq)(
            create_unsupported_overload(jpb__frwr))
    for snh__hgj in logging_logger_unsupported_methods:
        jpb__frwr = 'logging.Logger.' + snh__hgj
        overload_method(LoggingLoggerType, snh__hgj)(
            create_unsupported_overload(jpb__frwr))


_install_logging_logger_unsupported_objects()
