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
    pbp__uwnwg = context.get_python_api(builder)
    return pbp__uwnwg.unserialize(pbp__uwnwg.serialize_object(pyval))


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
        egsxq__zzft = ', '.join('e{}'.format(divp__cjh) for divp__cjh in
            range(len(args)))
        if egsxq__zzft:
            egsxq__zzft += ', '
        zpwg__hunz = ', '.join("{} = ''".format(jzv__wqh) for jzv__wqh in
            kws.keys())
        mlcnh__bmd = f'def format_stub(string, {egsxq__zzft} {zpwg__hunz}):\n'
        mlcnh__bmd += '    pass\n'
        btihn__vtnci = {}
        exec(mlcnh__bmd, {}, btihn__vtnci)
        okvqg__bdw = btihn__vtnci['format_stub']
        ccgz__vkbs = numba.core.utils.pysignature(okvqg__bdw)
        xexs__wthb = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, xexs__wthb).replace(pysig=ccgz__vkbs)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for aanqr__hwi in ('logging.Logger', 'logging.RootLogger'):
        for uiq__qsjxt in func_names:
            klm__tslm = f'@bound_function("{aanqr__hwi}.{uiq__qsjxt}")\n'
            klm__tslm += (
                f'def resolve_{uiq__qsjxt}(self, logger_typ, args, kws):\n')
            klm__tslm += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(klm__tslm)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for ojgaa__fpwms in logging_logger_unsupported_attrs:
        unj__turz = 'logging.Logger.' + ojgaa__fpwms
        overload_attribute(LoggingLoggerType, ojgaa__fpwms)(
            create_unsupported_overload(unj__turz))
    for rvw__cnht in logging_logger_unsupported_methods:
        unj__turz = 'logging.Logger.' + rvw__cnht
        overload_method(LoggingLoggerType, rvw__cnht)(
            create_unsupported_overload(unj__turz))


_install_logging_logger_unsupported_objects()
