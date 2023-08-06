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
    ifie__jyw = context.get_python_api(builder)
    return ifie__jyw.unserialize(ifie__jyw.serialize_object(pyval))


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
        xwus__rif = ', '.join('e{}'.format(upej__tpie) for upej__tpie in
            range(len(args)))
        if xwus__rif:
            xwus__rif += ', '
        xit__zfd = ', '.join("{} = ''".format(qeb__wvy) for qeb__wvy in kws
            .keys())
        nwa__mfwsw = f'def format_stub(string, {xwus__rif} {xit__zfd}):\n'
        nwa__mfwsw += '    pass\n'
        pxi__cqxod = {}
        exec(nwa__mfwsw, {}, pxi__cqxod)
        thgv__tnw = pxi__cqxod['format_stub']
        vfsqn__pzzig = numba.core.utils.pysignature(thgv__tnw)
        bht__ifhgw = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, bht__ifhgw).replace(pysig=vfsqn__pzzig)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for humjq__xkb in ('logging.Logger', 'logging.RootLogger'):
        for ilxwc__tooi in func_names:
            daxgk__kond = f'@bound_function("{humjq__xkb}.{ilxwc__tooi}")\n'
            daxgk__kond += (
                f'def resolve_{ilxwc__tooi}(self, logger_typ, args, kws):\n')
            daxgk__kond += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(daxgk__kond)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for vuh__hnqk in logging_logger_unsupported_attrs:
        bjicd__xur = 'logging.Logger.' + vuh__hnqk
        overload_attribute(LoggingLoggerType, vuh__hnqk)(
            create_unsupported_overload(bjicd__xur))
    for ewimp__ghvr in logging_logger_unsupported_methods:
        bjicd__xur = 'logging.Logger.' + ewimp__ghvr
        overload_method(LoggingLoggerType, ewimp__ghvr)(
            create_unsupported_overload(bjicd__xur))


_install_logging_logger_unsupported_objects()
