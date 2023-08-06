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
        ywpo__kvn = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, ywpo__kvn)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    oyjuu__ppw = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    wcbih__ktbbc = c.pyapi.long_from_longlong(oyjuu__ppw.value)
    vqc__soc = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(vqc__soc, (wcbih__ktbbc,))
    c.pyapi.decref(wcbih__ktbbc)
    c.pyapi.decref(vqc__soc)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    wcbih__ktbbc = c.pyapi.object_getattr_string(val, 'value')
    ctzbp__hkdeh = c.pyapi.long_as_longlong(wcbih__ktbbc)
    oyjuu__ppw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    oyjuu__ppw.value = ctzbp__hkdeh
    c.pyapi.decref(wcbih__ktbbc)
    aipp__xitay = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(oyjuu__ppw._getvalue(), is_error=aipp__xitay)


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
            ipjqv__aoqaw = 1000 * microseconds
            return init_pd_timedelta(ipjqv__aoqaw)
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
            ipjqv__aoqaw = 1000 * microseconds
            return init_pd_timedelta(ipjqv__aoqaw)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    ijbe__ctte, uyber__xifog = pd._libs.tslibs.conversion.precision_from_unit(
        unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * ijbe__ctte)
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
            ogh__qeufh = (rhs.microseconds + (rhs.seconds + rhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + ogh__qeufh
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            lwe__pao = (lhs.microseconds + (lhs.seconds + lhs.days * 60 * 
                60 * 24) * 1000 * 1000) * 1000
            val = lwe__pao + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            stzyr__zoikw = rhs.toordinal()
            eqh__kll = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            enzu__vdj = rhs.microsecond
            voi__jvw = lhs.value // 1000
            hoq__gsqy = lhs.nanoseconds
            uryig__wibas = enzu__vdj + voi__jvw
            uyp__vfhxq = 1000000 * (stzyr__zoikw * 86400 + eqh__kll
                ) + uryig__wibas
            wkir__dmpl = hoq__gsqy
            return compute_pd_timestamp(uyp__vfhxq, wkir__dmpl)
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
            hcp__jckd = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            hcp__jckd = hcp__jckd + lhs
            vei__kvjm, kvmv__xqhlg = divmod(hcp__jckd.seconds, 3600)
            ycrt__jjgj, zmrte__qhuz = divmod(kvmv__xqhlg, 60)
            if 0 < hcp__jckd.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(hcp__jckd
                    .days)
                return datetime.datetime(d.year, d.month, d.day, vei__kvjm,
                    ycrt__jjgj, zmrte__qhuz, hcp__jckd.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            hcp__jckd = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            hcp__jckd = hcp__jckd + rhs
            vei__kvjm, kvmv__xqhlg = divmod(hcp__jckd.seconds, 3600)
            ycrt__jjgj, zmrte__qhuz = divmod(kvmv__xqhlg, 60)
            if 0 < hcp__jckd.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(hcp__jckd
                    .days)
                return datetime.datetime(d.year, d.month, d.day, vei__kvjm,
                    ycrt__jjgj, zmrte__qhuz, hcp__jckd.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            qvlv__oja = lhs.value - rhs.value
            return pd.Timedelta(qvlv__oja)
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
            xgh__npoww = lhs
            numba.parfors.parfor.init_prange()
            n = len(xgh__npoww)
            A = alloc_datetime_timedelta_array(n)
            for ydt__kvc in numba.parfors.parfor.internal_prange(n):
                A[ydt__kvc] = xgh__npoww[ydt__kvc] - rhs
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
            dkjg__ajom = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, dkjg__ajom)
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
            vrqxc__tbrll, dkjg__ajom = divmod(lhs.value, rhs.value)
            return vrqxc__tbrll, pd.Timedelta(dkjg__ajom)
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
        ywpo__kvn = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, ywpo__kvn)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    oyjuu__ppw = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    yibif__pxiuu = c.pyapi.long_from_longlong(oyjuu__ppw.days)
    ptyul__typ = c.pyapi.long_from_longlong(oyjuu__ppw.seconds)
    kylr__onwm = c.pyapi.long_from_longlong(oyjuu__ppw.microseconds)
    vqc__soc = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.timedelta)
        )
    res = c.pyapi.call_function_objargs(vqc__soc, (yibif__pxiuu, ptyul__typ,
        kylr__onwm))
    c.pyapi.decref(yibif__pxiuu)
    c.pyapi.decref(ptyul__typ)
    c.pyapi.decref(kylr__onwm)
    c.pyapi.decref(vqc__soc)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    yibif__pxiuu = c.pyapi.object_getattr_string(val, 'days')
    ptyul__typ = c.pyapi.object_getattr_string(val, 'seconds')
    kylr__onwm = c.pyapi.object_getattr_string(val, 'microseconds')
    cmtd__xdsh = c.pyapi.long_as_longlong(yibif__pxiuu)
    sirs__qoanv = c.pyapi.long_as_longlong(ptyul__typ)
    uik__sggf = c.pyapi.long_as_longlong(kylr__onwm)
    oyjuu__ppw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    oyjuu__ppw.days = cmtd__xdsh
    oyjuu__ppw.seconds = sirs__qoanv
    oyjuu__ppw.microseconds = uik__sggf
    c.pyapi.decref(yibif__pxiuu)
    c.pyapi.decref(ptyul__typ)
    c.pyapi.decref(kylr__onwm)
    aipp__xitay = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(oyjuu__ppw._getvalue(), is_error=aipp__xitay)


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
    vrqxc__tbrll, dkjg__ajom = divmod(a, b)
    dkjg__ajom *= 2
    mxlr__kwep = dkjg__ajom > b if b > 0 else dkjg__ajom < b
    if mxlr__kwep or dkjg__ajom == b and vrqxc__tbrll % 2 == 1:
        vrqxc__tbrll += 1
    return vrqxc__tbrll


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
                tfb__jsizb = _cmp(_getstate(lhs), _getstate(rhs))
                return op(tfb__jsizb, 0)
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
            vrqxc__tbrll, dkjg__ajom = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return vrqxc__tbrll, datetime.timedelta(0, 0, dkjg__ajom)
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
    vigge__xmxs = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != vigge__xmxs
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
        ywpo__kvn = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, ywpo__kvn)


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
    vpw__bzg = types.Array(types.intp, 1, 'C')
    kwmsc__cbb = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        vpw__bzg, [n])
    mcv__vumqg = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        vpw__bzg, [n])
    mhrh__svdr = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        vpw__bzg, [n])
    gpv__htgwc = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    uuacq__xbkg = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [gpv__htgwc])
    kfj__yhvk = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(64), lir.IntType(64).as_pointer(), lir.IntType(64).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer()])
    aaa__kitq = cgutils.get_or_insert_function(c.builder.module, kfj__yhvk,
        name='unbox_datetime_timedelta_array')
    c.builder.call(aaa__kitq, [val, n, kwmsc__cbb.data, mcv__vumqg.data,
        mhrh__svdr.data, uuacq__xbkg.data])
    veip__avlk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    veip__avlk.days_data = kwmsc__cbb._getvalue()
    veip__avlk.seconds_data = mcv__vumqg._getvalue()
    veip__avlk.microseconds_data = mhrh__svdr._getvalue()
    veip__avlk.null_bitmap = uuacq__xbkg._getvalue()
    aipp__xitay = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(veip__avlk._getvalue(), is_error=aipp__xitay)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    xgh__npoww = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    kwmsc__cbb = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, xgh__npoww.days_data)
    mcv__vumqg = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, xgh__npoww.seconds_data).data
    mhrh__svdr = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, xgh__npoww.microseconds_data).data
    cybpr__dba = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, xgh__npoww.null_bitmap).data
    n = c.builder.extract_value(kwmsc__cbb.shape, 0)
    kfj__yhvk = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    phaz__msia = cgutils.get_or_insert_function(c.builder.module, kfj__yhvk,
        name='box_datetime_timedelta_array')
    xjasw__djutm = c.builder.call(phaz__msia, [n, kwmsc__cbb.data,
        mcv__vumqg, mhrh__svdr, cybpr__dba])
    c.context.nrt.decref(c.builder, typ, val)
    return xjasw__djutm


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        hltmm__ftp, lqmhw__fyg, lnxf__mizq, ddo__usqt = args
        qryzd__pfg = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        qryzd__pfg.days_data = hltmm__ftp
        qryzd__pfg.seconds_data = lqmhw__fyg
        qryzd__pfg.microseconds_data = lnxf__mizq
        qryzd__pfg.null_bitmap = ddo__usqt
        context.nrt.incref(builder, signature.args[0], hltmm__ftp)
        context.nrt.incref(builder, signature.args[1], lqmhw__fyg)
        context.nrt.incref(builder, signature.args[2], lnxf__mizq)
        context.nrt.incref(builder, signature.args[3], ddo__usqt)
        return qryzd__pfg._getvalue()
    hyuxc__xpw = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return hyuxc__xpw, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    kwmsc__cbb = np.empty(n, np.int64)
    mcv__vumqg = np.empty(n, np.int64)
    mhrh__svdr = np.empty(n, np.int64)
    fofg__yhea = np.empty(n + 7 >> 3, np.uint8)
    for ydt__kvc, s in enumerate(pyval):
        ftrc__nlmq = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(fofg__yhea, ydt__kvc, int(not
            ftrc__nlmq))
        if not ftrc__nlmq:
            kwmsc__cbb[ydt__kvc] = s.days
            mcv__vumqg[ydt__kvc] = s.seconds
            mhrh__svdr[ydt__kvc] = s.microseconds
    xtlxt__ogcb = context.get_constant_generic(builder, days_data_type,
        kwmsc__cbb)
    gcr__bdo = context.get_constant_generic(builder, seconds_data_type,
        mcv__vumqg)
    hxd__pxrq = context.get_constant_generic(builder,
        microseconds_data_type, mhrh__svdr)
    zgq__kavcv = context.get_constant_generic(builder, nulls_type, fofg__yhea)
    return lir.Constant.literal_struct([xtlxt__ogcb, gcr__bdo, hxd__pxrq,
        zgq__kavcv])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    kwmsc__cbb = np.empty(n, dtype=np.int64)
    mcv__vumqg = np.empty(n, dtype=np.int64)
    mhrh__svdr = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(kwmsc__cbb, mcv__vumqg, mhrh__svdr,
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
            dwhhu__bpdrt = bodo.utils.conversion.coerce_to_ndarray(ind)
            dar__dnlop = A._null_bitmap
            isv__rhek = A._days_data[dwhhu__bpdrt]
            umto__bwnfa = A._seconds_data[dwhhu__bpdrt]
            oqjsh__mxbot = A._microseconds_data[dwhhu__bpdrt]
            n = len(isv__rhek)
            mjt__rwcnv = get_new_null_mask_bool_index(dar__dnlop, ind, n)
            return init_datetime_timedelta_array(isv__rhek, umto__bwnfa,
                oqjsh__mxbot, mjt__rwcnv)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            dwhhu__bpdrt = bodo.utils.conversion.coerce_to_ndarray(ind)
            dar__dnlop = A._null_bitmap
            isv__rhek = A._days_data[dwhhu__bpdrt]
            umto__bwnfa = A._seconds_data[dwhhu__bpdrt]
            oqjsh__mxbot = A._microseconds_data[dwhhu__bpdrt]
            n = len(isv__rhek)
            mjt__rwcnv = get_new_null_mask_int_index(dar__dnlop,
                dwhhu__bpdrt, n)
            return init_datetime_timedelta_array(isv__rhek, umto__bwnfa,
                oqjsh__mxbot, mjt__rwcnv)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            dar__dnlop = A._null_bitmap
            isv__rhek = np.ascontiguousarray(A._days_data[ind])
            umto__bwnfa = np.ascontiguousarray(A._seconds_data[ind])
            oqjsh__mxbot = np.ascontiguousarray(A._microseconds_data[ind])
            mjt__rwcnv = get_new_null_mask_slice_index(dar__dnlop, ind, n)
            return init_datetime_timedelta_array(isv__rhek, umto__bwnfa,
                oqjsh__mxbot, mjt__rwcnv)
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
    dfu__ddm = (
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
            raise BodoError(dfu__ddm)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(dfu__ddm)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for ydt__kvc in range(n):
                    A._days_data[ind[ydt__kvc]] = val._days
                    A._seconds_data[ind[ydt__kvc]] = val._seconds
                    A._microseconds_data[ind[ydt__kvc]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[ydt__kvc], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for ydt__kvc in range(n):
                    A._days_data[ind[ydt__kvc]] = val._days_data[ydt__kvc]
                    A._seconds_data[ind[ydt__kvc]] = val._seconds_data[ydt__kvc
                        ]
                    A._microseconds_data[ind[ydt__kvc]
                        ] = val._microseconds_data[ydt__kvc]
                    jgwoy__sqvts = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, ydt__kvc)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[ydt__kvc], jgwoy__sqvts)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for ydt__kvc in range(n):
                    if not bodo.libs.array_kernels.isna(ind, ydt__kvc) and ind[
                        ydt__kvc]:
                        A._days_data[ydt__kvc] = val._days
                        A._seconds_data[ydt__kvc] = val._seconds
                        A._microseconds_data[ydt__kvc] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            ydt__kvc, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                exk__imqry = 0
                for ydt__kvc in range(n):
                    if not bodo.libs.array_kernels.isna(ind, ydt__kvc) and ind[
                        ydt__kvc]:
                        A._days_data[ydt__kvc] = val._days_data[exk__imqry]
                        A._seconds_data[ydt__kvc] = val._seconds_data[
                            exk__imqry]
                        A._microseconds_data[ydt__kvc
                            ] = val._microseconds_data[exk__imqry]
                        jgwoy__sqvts = (bodo.libs.int_arr_ext.
                            get_bit_bitmap_arr(val._null_bitmap, exk__imqry))
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            ydt__kvc, jgwoy__sqvts)
                        exk__imqry += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                dtvi__cqxvq = numba.cpython.unicode._normalize_slice(ind,
                    len(A))
                for ydt__kvc in range(dtvi__cqxvq.start, dtvi__cqxvq.stop,
                    dtvi__cqxvq.step):
                    A._days_data[ydt__kvc] = val._days
                    A._seconds_data[ydt__kvc] = val._seconds
                    A._microseconds_data[ydt__kvc] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ydt__kvc, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                srrw__fsrf = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, srrw__fsrf,
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
            xgh__npoww = arg1
            numba.parfors.parfor.init_prange()
            n = len(xgh__npoww)
            A = alloc_datetime_timedelta_array(n)
            for ydt__kvc in numba.parfors.parfor.internal_prange(n):
                A[ydt__kvc] = xgh__npoww[ydt__kvc] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            blurh__fik = True
        else:
            blurh__fik = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                eqozf__dkl = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ydt__kvc in numba.parfors.parfor.internal_prange(n):
                    nbd__rlxh = bodo.libs.array_kernels.isna(lhs, ydt__kvc)
                    fsdfk__avsna = bodo.libs.array_kernels.isna(rhs, ydt__kvc)
                    if nbd__rlxh or fsdfk__avsna:
                        wim__uxzh = blurh__fik
                    else:
                        wim__uxzh = op(lhs[ydt__kvc], rhs[ydt__kvc])
                    eqozf__dkl[ydt__kvc] = wim__uxzh
                return eqozf__dkl
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                eqozf__dkl = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ydt__kvc in numba.parfors.parfor.internal_prange(n):
                    jgwoy__sqvts = bodo.libs.array_kernels.isna(lhs, ydt__kvc)
                    if jgwoy__sqvts:
                        wim__uxzh = blurh__fik
                    else:
                        wim__uxzh = op(lhs[ydt__kvc], rhs)
                    eqozf__dkl[ydt__kvc] = wim__uxzh
                return eqozf__dkl
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                eqozf__dkl = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ydt__kvc in numba.parfors.parfor.internal_prange(n):
                    jgwoy__sqvts = bodo.libs.array_kernels.isna(rhs, ydt__kvc)
                    if jgwoy__sqvts:
                        wim__uxzh = blurh__fik
                    else:
                        wim__uxzh = op(lhs, rhs[ydt__kvc])
                    eqozf__dkl[ydt__kvc] = wim__uxzh
                return eqozf__dkl
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for ldlba__xhbyl in timedelta_unsupported_attrs:
        yqkmy__ujvg = 'pandas.Timedelta.' + ldlba__xhbyl
        overload_attribute(PDTimeDeltaType, ldlba__xhbyl)(
            create_unsupported_overload(yqkmy__ujvg))
    for quyb__ethbp in timedelta_unsupported_methods:
        yqkmy__ujvg = 'pandas.Timedelta.' + quyb__ethbp
        overload_method(PDTimeDeltaType, quyb__ethbp)(
            create_unsupported_overload(yqkmy__ujvg + '()'))


_intstall_pd_timedelta_unsupported()
