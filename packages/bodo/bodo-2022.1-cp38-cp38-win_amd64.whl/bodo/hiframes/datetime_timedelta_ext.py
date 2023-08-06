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
        kawq__zmgz = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, kawq__zmgz)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    tawf__zjma = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ser__dln = c.pyapi.long_from_longlong(tawf__zjma.value)
    tyx__hsw = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(tyx__hsw, (ser__dln,))
    c.pyapi.decref(ser__dln)
    c.pyapi.decref(tyx__hsw)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    ser__dln = c.pyapi.object_getattr_string(val, 'value')
    lfspy__imw = c.pyapi.long_as_longlong(ser__dln)
    tawf__zjma = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tawf__zjma.value = lfspy__imw
    c.pyapi.decref(ser__dln)
    gjmao__vce = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tawf__zjma._getvalue(), is_error=gjmao__vce)


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
            bcr__wjpsh = 1000 * microseconds
            return init_pd_timedelta(bcr__wjpsh)
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
            bcr__wjpsh = 1000 * microseconds
            return init_pd_timedelta(bcr__wjpsh)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    krzjb__myf, xnxmg__xpe = pd._libs.tslibs.conversion.precision_from_unit(
        unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * krzjb__myf)
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
            lsbt__vbbks = (rhs.microseconds + (rhs.seconds + rhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + lsbt__vbbks
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            hsy__zlvz = (lhs.microseconds + (lhs.seconds + lhs.days * 60 * 
                60 * 24) * 1000 * 1000) * 1000
            val = hsy__zlvz + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            btwis__cqh = rhs.toordinal()
            tzssk__ykk = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            etvm__vfn = rhs.microsecond
            mci__cvmd = lhs.value // 1000
            dwssw__woz = lhs.nanoseconds
            yzhr__qod = etvm__vfn + mci__cvmd
            wqev__esd = 1000000 * (btwis__cqh * 86400 + tzssk__ykk) + yzhr__qod
            zsp__gzsid = dwssw__woz
            return compute_pd_timestamp(wqev__esd, zsp__gzsid)
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
            hxt__ihlb = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            hxt__ihlb = hxt__ihlb + lhs
            eijzi__stva, juvj__lzfmr = divmod(hxt__ihlb.seconds, 3600)
            ebk__iya, ilt__aqq = divmod(juvj__lzfmr, 60)
            if 0 < hxt__ihlb.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(hxt__ihlb
                    .days)
                return datetime.datetime(d.year, d.month, d.day,
                    eijzi__stva, ebk__iya, ilt__aqq, hxt__ihlb.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            hxt__ihlb = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            hxt__ihlb = hxt__ihlb + rhs
            eijzi__stva, juvj__lzfmr = divmod(hxt__ihlb.seconds, 3600)
            ebk__iya, ilt__aqq = divmod(juvj__lzfmr, 60)
            if 0 < hxt__ihlb.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(hxt__ihlb
                    .days)
                return datetime.datetime(d.year, d.month, d.day,
                    eijzi__stva, ebk__iya, ilt__aqq, hxt__ihlb.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            ypxv__nlcrz = lhs.value - rhs.value
            return pd.Timedelta(ypxv__nlcrz)
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
            erox__aiy = lhs
            numba.parfors.parfor.init_prange()
            n = len(erox__aiy)
            A = alloc_datetime_timedelta_array(n)
            for ponh__czl in numba.parfors.parfor.internal_prange(n):
                A[ponh__czl] = erox__aiy[ponh__czl] - rhs
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
            duc__klmu = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, duc__klmu)
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
            nvan__fmkx, duc__klmu = divmod(lhs.value, rhs.value)
            return nvan__fmkx, pd.Timedelta(duc__klmu)
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
        kawq__zmgz = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, kawq__zmgz)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    tawf__zjma = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    mog__hxib = c.pyapi.long_from_longlong(tawf__zjma.days)
    ahd__vsi = c.pyapi.long_from_longlong(tawf__zjma.seconds)
    zwioz__aorn = c.pyapi.long_from_longlong(tawf__zjma.microseconds)
    tyx__hsw = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.timedelta)
        )
    res = c.pyapi.call_function_objargs(tyx__hsw, (mog__hxib, ahd__vsi,
        zwioz__aorn))
    c.pyapi.decref(mog__hxib)
    c.pyapi.decref(ahd__vsi)
    c.pyapi.decref(zwioz__aorn)
    c.pyapi.decref(tyx__hsw)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    mog__hxib = c.pyapi.object_getattr_string(val, 'days')
    ahd__vsi = c.pyapi.object_getattr_string(val, 'seconds')
    zwioz__aorn = c.pyapi.object_getattr_string(val, 'microseconds')
    cqswd__xjv = c.pyapi.long_as_longlong(mog__hxib)
    cub__hgqhf = c.pyapi.long_as_longlong(ahd__vsi)
    zuy__ayqa = c.pyapi.long_as_longlong(zwioz__aorn)
    tawf__zjma = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tawf__zjma.days = cqswd__xjv
    tawf__zjma.seconds = cub__hgqhf
    tawf__zjma.microseconds = zuy__ayqa
    c.pyapi.decref(mog__hxib)
    c.pyapi.decref(ahd__vsi)
    c.pyapi.decref(zwioz__aorn)
    gjmao__vce = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tawf__zjma._getvalue(), is_error=gjmao__vce)


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
    nvan__fmkx, duc__klmu = divmod(a, b)
    duc__klmu *= 2
    uqcdr__svubl = duc__klmu > b if b > 0 else duc__klmu < b
    if uqcdr__svubl or duc__klmu == b and nvan__fmkx % 2 == 1:
        nvan__fmkx += 1
    return nvan__fmkx


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
                pydy__upllj = _cmp(_getstate(lhs), _getstate(rhs))
                return op(pydy__upllj, 0)
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
            nvan__fmkx, duc__klmu = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return nvan__fmkx, datetime.timedelta(0, 0, duc__klmu)
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
    eivh__fmr = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != eivh__fmr
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
        kawq__zmgz = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, kawq__zmgz)


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
    nao__mij = types.Array(types.intp, 1, 'C')
    wdz__hhzcy = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        nao__mij, [n])
    frx__cfpq = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        nao__mij, [n])
    bdcxp__ikl = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        nao__mij, [n])
    uxvd__bvgej = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    ejbz__mrwn = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [uxvd__bvgej])
    utqrv__xcug = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    cfip__kwxpv = cgutils.get_or_insert_function(c.builder.module,
        utqrv__xcug, name='unbox_datetime_timedelta_array')
    c.builder.call(cfip__kwxpv, [val, n, wdz__hhzcy.data, frx__cfpq.data,
        bdcxp__ikl.data, ejbz__mrwn.data])
    xbdzu__lik = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xbdzu__lik.days_data = wdz__hhzcy._getvalue()
    xbdzu__lik.seconds_data = frx__cfpq._getvalue()
    xbdzu__lik.microseconds_data = bdcxp__ikl._getvalue()
    xbdzu__lik.null_bitmap = ejbz__mrwn._getvalue()
    gjmao__vce = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xbdzu__lik._getvalue(), is_error=gjmao__vce)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    erox__aiy = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    wdz__hhzcy = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, erox__aiy.days_data)
    frx__cfpq = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, erox__aiy.seconds_data).data
    bdcxp__ikl = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, erox__aiy.microseconds_data).data
    kfwnv__cnd = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, erox__aiy.null_bitmap).data
    n = c.builder.extract_value(wdz__hhzcy.shape, 0)
    utqrv__xcug = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    rrrgg__kuds = cgutils.get_or_insert_function(c.builder.module,
        utqrv__xcug, name='box_datetime_timedelta_array')
    pyc__yvlx = c.builder.call(rrrgg__kuds, [n, wdz__hhzcy.data, frx__cfpq,
        bdcxp__ikl, kfwnv__cnd])
    c.context.nrt.decref(c.builder, typ, val)
    return pyc__yvlx


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        thn__qasth, lvp__auk, kyze__gcpd, eup__pzmdl = args
        fhf__hnotf = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        fhf__hnotf.days_data = thn__qasth
        fhf__hnotf.seconds_data = lvp__auk
        fhf__hnotf.microseconds_data = kyze__gcpd
        fhf__hnotf.null_bitmap = eup__pzmdl
        context.nrt.incref(builder, signature.args[0], thn__qasth)
        context.nrt.incref(builder, signature.args[1], lvp__auk)
        context.nrt.incref(builder, signature.args[2], kyze__gcpd)
        context.nrt.incref(builder, signature.args[3], eup__pzmdl)
        return fhf__hnotf._getvalue()
    htih__khkg = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return htih__khkg, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    wdz__hhzcy = np.empty(n, np.int64)
    frx__cfpq = np.empty(n, np.int64)
    bdcxp__ikl = np.empty(n, np.int64)
    cywo__dfqq = np.empty(n + 7 >> 3, np.uint8)
    for ponh__czl, s in enumerate(pyval):
        zjyay__uopy = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(cywo__dfqq, ponh__czl, int(not
            zjyay__uopy))
        if not zjyay__uopy:
            wdz__hhzcy[ponh__czl] = s.days
            frx__cfpq[ponh__czl] = s.seconds
            bdcxp__ikl[ponh__czl] = s.microseconds
    nzch__iyb = context.get_constant_generic(builder, days_data_type,
        wdz__hhzcy)
    ihdw__rfzb = context.get_constant_generic(builder, seconds_data_type,
        frx__cfpq)
    aql__hmall = context.get_constant_generic(builder,
        microseconds_data_type, bdcxp__ikl)
    lghh__cvsph = context.get_constant_generic(builder, nulls_type, cywo__dfqq)
    return lir.Constant.literal_struct([nzch__iyb, ihdw__rfzb, aql__hmall,
        lghh__cvsph])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    wdz__hhzcy = np.empty(n, dtype=np.int64)
    frx__cfpq = np.empty(n, dtype=np.int64)
    bdcxp__ikl = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(wdz__hhzcy, frx__cfpq, bdcxp__ikl,
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
            sfer__eqj = bodo.utils.conversion.coerce_to_ndarray(ind)
            xth__eqhu = A._null_bitmap
            deiy__czwqs = A._days_data[sfer__eqj]
            sba__cwm = A._seconds_data[sfer__eqj]
            fum__vfj = A._microseconds_data[sfer__eqj]
            n = len(deiy__czwqs)
            qfb__mfj = get_new_null_mask_bool_index(xth__eqhu, ind, n)
            return init_datetime_timedelta_array(deiy__czwqs, sba__cwm,
                fum__vfj, qfb__mfj)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            sfer__eqj = bodo.utils.conversion.coerce_to_ndarray(ind)
            xth__eqhu = A._null_bitmap
            deiy__czwqs = A._days_data[sfer__eqj]
            sba__cwm = A._seconds_data[sfer__eqj]
            fum__vfj = A._microseconds_data[sfer__eqj]
            n = len(deiy__czwqs)
            qfb__mfj = get_new_null_mask_int_index(xth__eqhu, sfer__eqj, n)
            return init_datetime_timedelta_array(deiy__czwqs, sba__cwm,
                fum__vfj, qfb__mfj)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            xth__eqhu = A._null_bitmap
            deiy__czwqs = np.ascontiguousarray(A._days_data[ind])
            sba__cwm = np.ascontiguousarray(A._seconds_data[ind])
            fum__vfj = np.ascontiguousarray(A._microseconds_data[ind])
            qfb__mfj = get_new_null_mask_slice_index(xth__eqhu, ind, n)
            return init_datetime_timedelta_array(deiy__czwqs, sba__cwm,
                fum__vfj, qfb__mfj)
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
    jai__rvt = (
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
            raise BodoError(jai__rvt)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(jai__rvt)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for ponh__czl in range(n):
                    A._days_data[ind[ponh__czl]] = val._days
                    A._seconds_data[ind[ponh__czl]] = val._seconds
                    A._microseconds_data[ind[ponh__czl]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[ponh__czl], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for ponh__czl in range(n):
                    A._days_data[ind[ponh__czl]] = val._days_data[ponh__czl]
                    A._seconds_data[ind[ponh__czl]] = val._seconds_data[
                        ponh__czl]
                    A._microseconds_data[ind[ponh__czl]
                        ] = val._microseconds_data[ponh__czl]
                    dzh__btk = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, ponh__czl)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[ponh__czl], dzh__btk)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for ponh__czl in range(n):
                    if not bodo.libs.array_kernels.isna(ind, ponh__czl
                        ) and ind[ponh__czl]:
                        A._days_data[ponh__czl] = val._days
                        A._seconds_data[ponh__czl] = val._seconds
                        A._microseconds_data[ponh__czl] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            ponh__czl, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                oap__zfnuu = 0
                for ponh__czl in range(n):
                    if not bodo.libs.array_kernels.isna(ind, ponh__czl
                        ) and ind[ponh__czl]:
                        A._days_data[ponh__czl] = val._days_data[oap__zfnuu]
                        A._seconds_data[ponh__czl] = val._seconds_data[
                            oap__zfnuu]
                        A._microseconds_data[ponh__czl
                            ] = val._microseconds_data[oap__zfnuu]
                        dzh__btk = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                            ._null_bitmap, oap__zfnuu)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            ponh__czl, dzh__btk)
                        oap__zfnuu += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                alauj__beroa = numba.cpython.unicode._normalize_slice(ind,
                    len(A))
                for ponh__czl in range(alauj__beroa.start, alauj__beroa.
                    stop, alauj__beroa.step):
                    A._days_data[ponh__czl] = val._days
                    A._seconds_data[ponh__czl] = val._seconds
                    A._microseconds_data[ponh__czl] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ponh__czl, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                yqbp__rhcy = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, yqbp__rhcy,
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
            erox__aiy = arg1
            numba.parfors.parfor.init_prange()
            n = len(erox__aiy)
            A = alloc_datetime_timedelta_array(n)
            for ponh__czl in numba.parfors.parfor.internal_prange(n):
                A[ponh__czl] = erox__aiy[ponh__czl] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            duq__ohod = True
        else:
            duq__ohod = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                odkb__orch = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ponh__czl in numba.parfors.parfor.internal_prange(n):
                    sqwi__emmy = bodo.libs.array_kernels.isna(lhs, ponh__czl)
                    woio__svj = bodo.libs.array_kernels.isna(rhs, ponh__czl)
                    if sqwi__emmy or woio__svj:
                        yvo__crbr = duq__ohod
                    else:
                        yvo__crbr = op(lhs[ponh__czl], rhs[ponh__czl])
                    odkb__orch[ponh__czl] = yvo__crbr
                return odkb__orch
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                odkb__orch = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ponh__czl in numba.parfors.parfor.internal_prange(n):
                    dzh__btk = bodo.libs.array_kernels.isna(lhs, ponh__czl)
                    if dzh__btk:
                        yvo__crbr = duq__ohod
                    else:
                        yvo__crbr = op(lhs[ponh__czl], rhs)
                    odkb__orch[ponh__czl] = yvo__crbr
                return odkb__orch
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                odkb__orch = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ponh__czl in numba.parfors.parfor.internal_prange(n):
                    dzh__btk = bodo.libs.array_kernels.isna(rhs, ponh__czl)
                    if dzh__btk:
                        yvo__crbr = duq__ohod
                    else:
                        yvo__crbr = op(lhs, rhs[ponh__czl])
                    odkb__orch[ponh__czl] = yvo__crbr
                return odkb__orch
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for ulad__kmsfa in timedelta_unsupported_attrs:
        cmhp__kxyhh = 'pandas.Timedelta.' + ulad__kmsfa
        overload_attribute(PDTimeDeltaType, ulad__kmsfa)(
            create_unsupported_overload(cmhp__kxyhh))
    for ssa__idp in timedelta_unsupported_methods:
        cmhp__kxyhh = 'pandas.Timedelta.' + ssa__idp
        overload_method(PDTimeDeltaType, ssa__idp)(create_unsupported_overload
            (cmhp__kxyhh + '()'))


_intstall_pd_timedelta_unsupported()
