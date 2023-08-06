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
    spsmh__xerej = context.get_python_api(builder)
    return spsmh__xerej.unserialize(spsmh__xerej.serialize_object(pyval))


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
        sukl__eoisg = ', '.join('e{}'.format(uhq__ogyb) for uhq__ogyb in
            range(len(args)))
        if sukl__eoisg:
            sukl__eoisg += ', '
        jvd__mza = ', '.join("{} = ''".format(qgjy__tzb) for qgjy__tzb in
            kws.keys())
        ssqky__mwnhh = f'def format_stub(string, {sukl__eoisg} {jvd__mza}):\n'
        ssqky__mwnhh += '    pass\n'
        phls__qdb = {}
        exec(ssqky__mwnhh, {}, phls__qdb)
        bqt__kypjn = phls__qdb['format_stub']
        gqbp__edqh = numba.core.utils.pysignature(bqt__kypjn)
        guzwn__knua = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, guzwn__knua).replace(pysig=gqbp__edqh)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for eiew__rdg in ('logging.Logger', 'logging.RootLogger'):
        for vkho__fee in func_names:
            baxo__frvt = f'@bound_function("{eiew__rdg}.{vkho__fee}")\n'
            baxo__frvt += (
                f'def resolve_{vkho__fee}(self, logger_typ, args, kws):\n')
            baxo__frvt += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(baxo__frvt)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for zlp__ftxzh in logging_logger_unsupported_attrs:
        vhszb__rgwdj = 'logging.Logger.' + zlp__ftxzh
        overload_attribute(LoggingLoggerType, zlp__ftxzh)(
            create_unsupported_overload(vhszb__rgwdj))
    for kfs__ocp in logging_logger_unsupported_methods:
        vhszb__rgwdj = 'logging.Logger.' + kfs__ocp
        overload_method(LoggingLoggerType, kfs__ocp)(
            create_unsupported_overload(vhszb__rgwdj))


_install_logging_logger_unsupported_objects()
