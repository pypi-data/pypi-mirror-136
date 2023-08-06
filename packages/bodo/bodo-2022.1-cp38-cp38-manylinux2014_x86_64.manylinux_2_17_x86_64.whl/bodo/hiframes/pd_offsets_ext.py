"""
Implement support for the various classes in pd.tseries.offsets.
"""
import operator
import llvmlite.binding as ll
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.pd_timestamp_ext import get_days_in_month, pd_timestamp_type
from bodo.libs import hdatetime_ext
from bodo.utils.typing import BodoError, create_unsupported_overload, is_overload_none
ll.add_symbol('box_date_offset', hdatetime_ext.box_date_offset)
ll.add_symbol('unbox_date_offset', hdatetime_ext.unbox_date_offset)


class MonthBeginType(types.Type):

    def __init__(self):
        super(MonthBeginType, self).__init__(name='MonthBeginType()')


month_begin_type = MonthBeginType()


@typeof_impl.register(pd.tseries.offsets.MonthBegin)
def typeof_month_begin(val, c):
    return month_begin_type


@register_model(MonthBeginType)
class MonthBeginModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xyasm__qjiee = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, xyasm__qjiee)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    gqan__hoeba = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    bfrb__pgn = c.pyapi.long_from_longlong(gqan__hoeba.n)
    rdxc__zrc = c.pyapi.from_native_value(types.boolean, gqan__hoeba.
        normalize, c.env_manager)
    gmr__yvod = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    jwmp__inw = c.pyapi.call_function_objargs(gmr__yvod, (bfrb__pgn, rdxc__zrc)
        )
    c.pyapi.decref(bfrb__pgn)
    c.pyapi.decref(rdxc__zrc)
    c.pyapi.decref(gmr__yvod)
    return jwmp__inw


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    bfrb__pgn = c.pyapi.object_getattr_string(val, 'n')
    rdxc__zrc = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(bfrb__pgn)
    normalize = c.pyapi.to_native_value(types.bool_, rdxc__zrc).value
    gqan__hoeba = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    gqan__hoeba.n = n
    gqan__hoeba.normalize = normalize
    c.pyapi.decref(bfrb__pgn)
    c.pyapi.decref(rdxc__zrc)
    fuidr__oxyle = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(gqan__hoeba._getvalue(), is_error=fuidr__oxyle)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        gqan__hoeba = cgutils.create_struct_proxy(typ)(context, builder)
        gqan__hoeba.n = args[0]
        gqan__hoeba.normalize = args[1]
        return gqan__hoeba._getvalue()
    return MonthBeginType()(n, normalize), codegen


make_attribute_wrapper(MonthBeginType, 'n', 'n')
make_attribute_wrapper(MonthBeginType, 'normalize', 'normalize')


@register_jitable
def calculate_month_begin_date(year, month, day, n):
    if n <= 0:
        if day > 1:
            n += 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = 1
    return year, month, day


def overload_add_operator_month_begin_offset_type(lhs, rhs):
    if lhs == month_begin_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_begin_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_begin_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_begin_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


class MonthEndType(types.Type):

    def __init__(self):
        super(MonthEndType, self).__init__(name='MonthEndType()')


month_end_type = MonthEndType()


@typeof_impl.register(pd.tseries.offsets.MonthEnd)
def typeof_month_end(val, c):
    return month_end_type


@register_model(MonthEndType)
class MonthEndModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xyasm__qjiee = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, xyasm__qjiee)


@box(MonthEndType)
def box_month_end(typ, val, c):
    grroq__psxt = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    bfrb__pgn = c.pyapi.long_from_longlong(grroq__psxt.n)
    rdxc__zrc = c.pyapi.from_native_value(types.boolean, grroq__psxt.
        normalize, c.env_manager)
    lxdk__nzk = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    jwmp__inw = c.pyapi.call_function_objargs(lxdk__nzk, (bfrb__pgn, rdxc__zrc)
        )
    c.pyapi.decref(bfrb__pgn)
    c.pyapi.decref(rdxc__zrc)
    c.pyapi.decref(lxdk__nzk)
    return jwmp__inw


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    bfrb__pgn = c.pyapi.object_getattr_string(val, 'n')
    rdxc__zrc = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(bfrb__pgn)
    normalize = c.pyapi.to_native_value(types.bool_, rdxc__zrc).value
    grroq__psxt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    grroq__psxt.n = n
    grroq__psxt.normalize = normalize
    c.pyapi.decref(bfrb__pgn)
    c.pyapi.decref(rdxc__zrc)
    fuidr__oxyle = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(grroq__psxt._getvalue(), is_error=fuidr__oxyle)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        grroq__psxt = cgutils.create_struct_proxy(typ)(context, builder)
        grroq__psxt.n = args[0]
        grroq__psxt.normalize = args[1]
        return grroq__psxt._getvalue()
    return MonthEndType()(n, normalize), codegen


make_attribute_wrapper(MonthEndType, 'n', 'n')
make_attribute_wrapper(MonthEndType, 'normalize', 'normalize')


@lower_constant(MonthBeginType)
@lower_constant(MonthEndType)
def lower_constant_month_end(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    return lir.Constant.literal_struct([n, normalize])


@register_jitable
def calculate_month_end_date(year, month, day, n):
    if n > 0:
        grroq__psxt = get_days_in_month(year, month)
        if grroq__psxt > day:
            n -= 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = get_days_in_month(year, month)
    return year, month, day


def overload_add_operator_month_end_offset_type(lhs, rhs):
    if lhs == month_end_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_end_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_end_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_end_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_mul_date_offset_types(lhs, rhs):
    if lhs == month_begin_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthBegin(lhs.n * rhs, lhs.normalize)
    if lhs == month_end_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthEnd(lhs.n * rhs, lhs.normalize)
    if lhs == week_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.Week(lhs.n * rhs, lhs.normalize, lhs.
                weekday)
    if lhs == date_offset_type:

        def impl(lhs, rhs):
            n = lhs.n * rhs
            normalize = lhs.normalize
            nanoseconds = lhs._nanoseconds
            nanosecond = lhs._nanosecond
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize,
                    nanoseconds=nanoseconds, nanosecond=nanosecond)
    if rhs in [week_type, month_end_type, month_begin_type, date_offset_type]:

        def impl(lhs, rhs):
            return rhs * lhs
        return impl
    return impl


class DateOffsetType(types.Type):

    def __init__(self):
        super(DateOffsetType, self).__init__(name='DateOffsetType()')


date_offset_type = DateOffsetType()
date_offset_fields = ['years', 'months', 'weeks', 'days', 'hours',
    'minutes', 'seconds', 'microseconds', 'nanoseconds', 'year', 'month',
    'day', 'weekday', 'hour', 'minute', 'second', 'microsecond', 'nanosecond']


@typeof_impl.register(pd.tseries.offsets.DateOffset)
def type_of_date_offset(val, c):
    return date_offset_type


@register_model(DateOffsetType)
class DateOffsetModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xyasm__qjiee = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, xyasm__qjiee)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    owp__iba = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    lnx__bpfze = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for yainn__bnvb, olaj__mibt in enumerate(date_offset_fields):
        c.builder.store(getattr(owp__iba, olaj__mibt), c.builder.inttoptr(c
            .builder.add(c.builder.ptrtoint(lnx__bpfze, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * yainn__bnvb)), lir.IntType(64
            ).as_pointer()))
    qdfy__qmzg = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    qoyx__cmq = cgutils.get_or_insert_function(c.builder.module, qdfy__qmzg,
        name='box_date_offset')
    pgs__wmvmq = c.builder.call(qoyx__cmq, [owp__iba.n, owp__iba.normalize,
        lnx__bpfze, owp__iba.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return pgs__wmvmq


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    bfrb__pgn = c.pyapi.object_getattr_string(val, 'n')
    rdxc__zrc = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(bfrb__pgn)
    normalize = c.pyapi.to_native_value(types.bool_, rdxc__zrc).value
    lnx__bpfze = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    qdfy__qmzg = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer()])
    jhabu__geun = cgutils.get_or_insert_function(c.builder.module,
        qdfy__qmzg, name='unbox_date_offset')
    has_kws = c.builder.call(jhabu__geun, [val, lnx__bpfze])
    owp__iba = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    owp__iba.n = n
    owp__iba.normalize = normalize
    for yainn__bnvb, olaj__mibt in enumerate(date_offset_fields):
        setattr(owp__iba, olaj__mibt, c.builder.load(c.builder.inttoptr(c.
            builder.add(c.builder.ptrtoint(lnx__bpfze, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * yainn__bnvb)), lir.IntType(64
            ).as_pointer())))
    owp__iba.has_kws = has_kws
    c.pyapi.decref(bfrb__pgn)
    c.pyapi.decref(rdxc__zrc)
    fuidr__oxyle = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(owp__iba._getvalue(), is_error=fuidr__oxyle)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    aykg__ezh = [n, normalize]
    has_kws = False
    nedcc__uofo = [0] * 9 + [-1] * 9
    for yainn__bnvb, olaj__mibt in enumerate(date_offset_fields):
        if hasattr(pyval, olaj__mibt):
            jpkni__udn = context.get_constant(types.int64, getattr(pyval,
                olaj__mibt))
            if olaj__mibt != 'nanoseconds' and olaj__mibt != 'nanosecond':
                has_kws = True
        else:
            jpkni__udn = context.get_constant(types.int64, nedcc__uofo[
                yainn__bnvb])
        aykg__ezh.append(jpkni__udn)
    has_kws = context.get_constant(types.boolean, has_kws)
    aykg__ezh.append(has_kws)
    return lir.Constant.literal_struct(aykg__ezh)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    fzak__wzmac = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for sag__tqt in fzak__wzmac:
        if not is_overload_none(sag__tqt):
            has_kws = True
            break

    def impl(n=1, normalize=False, years=None, months=None, weeks=None,
        days=None, hours=None, minutes=None, seconds=None, microseconds=
        None, nanoseconds=None, year=None, month=None, day=None, weekday=
        None, hour=None, minute=None, second=None, microsecond=None,
        nanosecond=None):
        years = 0 if years is None else years
        months = 0 if months is None else months
        weeks = 0 if weeks is None else weeks
        days = 0 if days is None else days
        hours = 0 if hours is None else hours
        minutes = 0 if minutes is None else minutes
        seconds = 0 if seconds is None else seconds
        microseconds = 0 if microseconds is None else microseconds
        nanoseconds = 0 if nanoseconds is None else nanoseconds
        year = -1 if year is None else year
        month = -1 if month is None else month
        weekday = -1 if weekday is None else weekday
        day = -1 if day is None else day
        hour = -1 if hour is None else hour
        minute = -1 if minute is None else minute
        second = -1 if second is None else second
        microsecond = -1 if microsecond is None else microsecond
        nanosecond = -1 if nanosecond is None else nanosecond
        return init_date_offset(n, normalize, years, months, weeks, days,
            hours, minutes, seconds, microseconds, nanoseconds, year, month,
            day, weekday, hour, minute, second, microsecond, nanosecond,
            has_kws)
    return impl


@intrinsic
def init_date_offset(typingctx, n, normalize, years, months, weeks, days,
    hours, minutes, seconds, microseconds, nanoseconds, year, month, day,
    weekday, hour, minute, second, microsecond, nanosecond, has_kws):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        owp__iba = cgutils.create_struct_proxy(typ)(context, builder)
        owp__iba.n = args[0]
        owp__iba.normalize = args[1]
        owp__iba.years = args[2]
        owp__iba.months = args[3]
        owp__iba.weeks = args[4]
        owp__iba.days = args[5]
        owp__iba.hours = args[6]
        owp__iba.minutes = args[7]
        owp__iba.seconds = args[8]
        owp__iba.microseconds = args[9]
        owp__iba.nanoseconds = args[10]
        owp__iba.year = args[11]
        owp__iba.month = args[12]
        owp__iba.day = args[13]
        owp__iba.weekday = args[14]
        owp__iba.hour = args[15]
        owp__iba.minute = args[16]
        owp__iba.second = args[17]
        owp__iba.microsecond = args[18]
        owp__iba.nanosecond = args[19]
        owp__iba.has_kws = args[20]
        return owp__iba._getvalue()
    return DateOffsetType()(n, normalize, years, months, weeks, days, hours,
        minutes, seconds, microseconds, nanoseconds, year, month, day,
        weekday, hour, minute, second, microsecond, nanosecond, has_kws
        ), codegen


make_attribute_wrapper(DateOffsetType, 'n', 'n')
make_attribute_wrapper(DateOffsetType, 'normalize', 'normalize')
make_attribute_wrapper(DateOffsetType, 'years', '_years')
make_attribute_wrapper(DateOffsetType, 'months', '_months')
make_attribute_wrapper(DateOffsetType, 'weeks', '_weeks')
make_attribute_wrapper(DateOffsetType, 'days', '_days')
make_attribute_wrapper(DateOffsetType, 'hours', '_hours')
make_attribute_wrapper(DateOffsetType, 'minutes', '_minutes')
make_attribute_wrapper(DateOffsetType, 'seconds', '_seconds')
make_attribute_wrapper(DateOffsetType, 'microseconds', '_microseconds')
make_attribute_wrapper(DateOffsetType, 'nanoseconds', '_nanoseconds')
make_attribute_wrapper(DateOffsetType, 'year', '_year')
make_attribute_wrapper(DateOffsetType, 'month', '_month')
make_attribute_wrapper(DateOffsetType, 'weekday', '_weekday')
make_attribute_wrapper(DateOffsetType, 'day', '_day')
make_attribute_wrapper(DateOffsetType, 'hour', '_hour')
make_attribute_wrapper(DateOffsetType, 'minute', '_minute')
make_attribute_wrapper(DateOffsetType, 'second', '_second')
make_attribute_wrapper(DateOffsetType, 'microsecond', '_microsecond')
make_attribute_wrapper(DateOffsetType, 'nanosecond', '_nanosecond')
make_attribute_wrapper(DateOffsetType, 'has_kws', '_has_kws')


@register_jitable
def relative_delta_addition(dateoffset, ts):
    if dateoffset._has_kws:
        lkzwc__zelyv = -1 if dateoffset.n < 0 else 1
        for hrvpi__kpmzs in range(np.abs(dateoffset.n)):
            year = ts.year
            month = ts.month
            day = ts.day
            hour = ts.hour
            minute = ts.minute
            second = ts.second
            microsecond = ts.microsecond
            nanosecond = ts.nanosecond
            if dateoffset._year != -1:
                year = dateoffset._year
            year += lkzwc__zelyv * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += lkzwc__zelyv * dateoffset._months
            year, month, ipsz__ziygh = calculate_month_end_date(year, month,
                day, 0)
            if day > ipsz__ziygh:
                day = ipsz__ziygh
            if dateoffset._day != -1:
                day = dateoffset._day
            if dateoffset._hour != -1:
                hour = dateoffset._hour
            if dateoffset._minute != -1:
                minute = dateoffset._minute
            if dateoffset._second != -1:
                second = dateoffset._second
            if dateoffset._microsecond != -1:
                microsecond = dateoffset._microsecond
            ts = pd.Timestamp(year=year, month=month, day=day, hour=hour,
                minute=minute, second=second, microsecond=microsecond,
                nanosecond=nanosecond)
            gfsg__zeig = pd.Timedelta(days=dateoffset._days + 7 *
                dateoffset._weeks, hours=dateoffset._hours, minutes=
                dateoffset._minutes, seconds=dateoffset._seconds,
                microseconds=dateoffset._microseconds)
            if lkzwc__zelyv == -1:
                gfsg__zeig = -gfsg__zeig
            ts = ts + gfsg__zeig
            if dateoffset._weekday != -1:
                edvl__zsuy = ts.weekday()
                gety__jfhc = (dateoffset._weekday - edvl__zsuy) % 7
                ts = ts + pd.Timedelta(days=gety__jfhc)
        return ts
    else:
        return pd.Timedelta(days=dateoffset.n) + ts


def overload_add_operator_date_offset_type(lhs, rhs):
    if lhs == date_offset_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, rhs)
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs == date_offset_type and rhs in [datetime_date_type,
        datetime_datetime_type]:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, pd.Timestamp(rhs))
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == date_offset_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_sub_operator_offsets(lhs, rhs):
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs in [date_offset_type, month_begin_type, month_end_type,
        week_type]:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl


@overload(operator.neg, no_unliteral=True)
def overload_neg(lhs):
    if lhs == month_begin_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthBegin(-lhs.n, lhs.normalize)
    if lhs == month_end_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthEnd(-lhs.n, lhs.normalize)
    if lhs == week_type:

        def impl(lhs):
            return pd.tseries.offsets.Week(-lhs.n, lhs.normalize, lhs.weekday)
    if lhs == date_offset_type:

        def impl(lhs):
            n = -lhs.n
            normalize = lhs.normalize
            nanoseconds = lhs._nanoseconds
            nanosecond = lhs._nanosecond
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize,
                    nanoseconds=nanoseconds, nanosecond=nanosecond)
    return impl


def is_offsets_type(val):
    return val in [date_offset_type, month_begin_type, month_end_type,
        week_type]


class WeekType(types.Type):

    def __init__(self):
        super(WeekType, self).__init__(name='WeekType()')


week_type = WeekType()


@typeof_impl.register(pd.tseries.offsets.Week)
def typeof_week(val, c):
    return week_type


@register_model(WeekType)
class WeekModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xyasm__qjiee = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, xyasm__qjiee)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        hweh__xnyab = -1 if weekday is None else weekday
        return init_week(n, normalize, hweh__xnyab)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        jme__dpltb = cgutils.create_struct_proxy(typ)(context, builder)
        jme__dpltb.n = args[0]
        jme__dpltb.normalize = args[1]
        jme__dpltb.weekday = args[2]
        return jme__dpltb._getvalue()
    return WeekType()(n, normalize, weekday), codegen


@lower_constant(WeekType)
def lower_constant_week(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    if pyval.weekday is not None:
        weekday = context.get_constant(types.int64, pyval.weekday)
    else:
        weekday = context.get_constant(types.int64, -1)
    return lir.Constant.literal_struct([n, normalize, weekday])


@box(WeekType)
def box_week(typ, val, c):
    jme__dpltb = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    bfrb__pgn = c.pyapi.long_from_longlong(jme__dpltb.n)
    rdxc__zrc = c.pyapi.from_native_value(types.boolean, jme__dpltb.
        normalize, c.env_manager)
    mngyk__ejxre = c.pyapi.long_from_longlong(jme__dpltb.weekday)
    uwqws__qrmi = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    gnlu__dogkx = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64),
        -1), jme__dpltb.weekday)
    with c.builder.if_else(gnlu__dogkx) as (weekday_defined, weekday_undefined
        ):
        with weekday_defined:
            auch__vts = c.pyapi.call_function_objargs(uwqws__qrmi, (
                bfrb__pgn, rdxc__zrc, mngyk__ejxre))
            ihlu__ggu = c.builder.block
        with weekday_undefined:
            dmlva__urhx = c.pyapi.call_function_objargs(uwqws__qrmi, (
                bfrb__pgn, rdxc__zrc))
            xho__iyg = c.builder.block
    jwmp__inw = c.builder.phi(auch__vts.type)
    jwmp__inw.add_incoming(auch__vts, ihlu__ggu)
    jwmp__inw.add_incoming(dmlva__urhx, xho__iyg)
    c.pyapi.decref(mngyk__ejxre)
    c.pyapi.decref(bfrb__pgn)
    c.pyapi.decref(rdxc__zrc)
    c.pyapi.decref(uwqws__qrmi)
    return jwmp__inw


@unbox(WeekType)
def unbox_week(typ, val, c):
    bfrb__pgn = c.pyapi.object_getattr_string(val, 'n')
    rdxc__zrc = c.pyapi.object_getattr_string(val, 'normalize')
    mngyk__ejxre = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(bfrb__pgn)
    normalize = c.pyapi.to_native_value(types.bool_, rdxc__zrc).value
    smqcu__apc = c.pyapi.make_none()
    vbxo__wkc = c.builder.icmp_unsigned('==', mngyk__ejxre, smqcu__apc)
    with c.builder.if_else(vbxo__wkc) as (weekday_undefined, weekday_defined):
        with weekday_defined:
            auch__vts = c.pyapi.long_as_longlong(mngyk__ejxre)
            ihlu__ggu = c.builder.block
        with weekday_undefined:
            dmlva__urhx = lir.Constant(lir.IntType(64), -1)
            xho__iyg = c.builder.block
    jwmp__inw = c.builder.phi(auch__vts.type)
    jwmp__inw.add_incoming(auch__vts, ihlu__ggu)
    jwmp__inw.add_incoming(dmlva__urhx, xho__iyg)
    jme__dpltb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jme__dpltb.n = n
    jme__dpltb.normalize = normalize
    jme__dpltb.weekday = jwmp__inw
    c.pyapi.decref(bfrb__pgn)
    c.pyapi.decref(rdxc__zrc)
    c.pyapi.decref(mngyk__ejxre)
    fuidr__oxyle = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jme__dpltb._getvalue(), is_error=fuidr__oxyle)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            qqguw__ycya = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            if lhs.normalize:
                qex__usml = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                qex__usml = rhs
            return qex__usml + qqguw__ycya
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            qqguw__ycya = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            if lhs.normalize:
                qex__usml = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                qex__usml = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return qex__usml + qqguw__ycya
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            qqguw__ycya = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            return rhs + qqguw__ycya
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == week_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


@register_jitable
def calculate_week_date(n, weekday, other_weekday):
    if weekday == -1:
        return pd.Timedelta(weeks=n)
    if weekday != other_weekday:
        isis__iwm = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=isis__iwm)


date_offset_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
date_offset_unsupported = {'__call__', 'rollback', 'rollforward',
    'is_month_start', 'is_month_end', 'apply', 'apply_index', 'copy',
    'isAnchored', 'onOffset', 'is_anchored', 'is_on_offset',
    'is_quarter_start', 'is_quarter_end', 'is_year_start', 'is_year_end'}
month_end_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_end_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
month_begin_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_begin_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
week_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos', 'rule_code'}
week_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
offsets_unsupported = {pd.tseries.offsets.BusinessDay, pd.tseries.offsets.
    BDay, pd.tseries.offsets.BusinessHour, pd.tseries.offsets.
    CustomBusinessDay, pd.tseries.offsets.CDay, pd.tseries.offsets.
    CustomBusinessHour, pd.tseries.offsets.BusinessMonthEnd, pd.tseries.
    offsets.BMonthEnd, pd.tseries.offsets.BusinessMonthBegin, pd.tseries.
    offsets.BMonthBegin, pd.tseries.offsets.CustomBusinessMonthEnd, pd.
    tseries.offsets.CBMonthEnd, pd.tseries.offsets.CustomBusinessMonthBegin,
    pd.tseries.offsets.CBMonthBegin, pd.tseries.offsets.SemiMonthEnd, pd.
    tseries.offsets.SemiMonthBegin, pd.tseries.offsets.WeekOfMonth, pd.
    tseries.offsets.LastWeekOfMonth, pd.tseries.offsets.BQuarterEnd, pd.
    tseries.offsets.BQuarterBegin, pd.tseries.offsets.QuarterEnd, pd.
    tseries.offsets.QuarterBegin, pd.tseries.offsets.BYearEnd, pd.tseries.
    offsets.BYearBegin, pd.tseries.offsets.YearEnd, pd.tseries.offsets.
    YearBegin, pd.tseries.offsets.FY5253, pd.tseries.offsets.FY5253Quarter,
    pd.tseries.offsets.Easter, pd.tseries.offsets.Tick, pd.tseries.offsets.
    Day, pd.tseries.offsets.Hour, pd.tseries.offsets.Minute, pd.tseries.
    offsets.Second, pd.tseries.offsets.Milli, pd.tseries.offsets.Micro, pd.
    tseries.offsets.Nano}
frequencies_unsupported = {pd.tseries.frequencies.to_offset}


def _install_date_offsets_unsupported():
    for shf__upre in date_offset_unsupported_attrs:
        kse__vsk = 'pandas.tseries.offsets.DateOffset.' + shf__upre
        overload_attribute(DateOffsetType, shf__upre)(
            create_unsupported_overload(kse__vsk))
    for shf__upre in date_offset_unsupported:
        kse__vsk = 'pandas.tseries.offsets.DateOffset.' + shf__upre
        overload_method(DateOffsetType, shf__upre)(create_unsupported_overload
            (kse__vsk))


def _install_month_begin_unsupported():
    for shf__upre in month_begin_unsupported_attrs:
        kse__vsk = 'pandas.tseries.offsets.MonthBegin.' + shf__upre
        overload_attribute(MonthBeginType, shf__upre)(
            create_unsupported_overload(kse__vsk))
    for shf__upre in month_begin_unsupported:
        kse__vsk = 'pandas.tseries.offsets.MonthBegin.' + shf__upre
        overload_method(MonthBeginType, shf__upre)(create_unsupported_overload
            (kse__vsk))


def _install_month_end_unsupported():
    for shf__upre in date_offset_unsupported_attrs:
        kse__vsk = 'pandas.tseries.offsets.MonthEnd.' + shf__upre
        overload_attribute(MonthEndType, shf__upre)(create_unsupported_overload
            (kse__vsk))
    for shf__upre in date_offset_unsupported:
        kse__vsk = 'pandas.tseries.offsets.MonthEnd.' + shf__upre
        overload_method(MonthEndType, shf__upre)(create_unsupported_overload
            (kse__vsk))


def _install_week_unsupported():
    for shf__upre in week_unsupported_attrs:
        kse__vsk = 'pandas.tseries.offsets.Week.' + shf__upre
        overload_attribute(WeekType, shf__upre)(create_unsupported_overload
            (kse__vsk))
    for shf__upre in week_unsupported:
        kse__vsk = 'pandas.tseries.offsets.Week.' + shf__upre
        overload_method(WeekType, shf__upre)(create_unsupported_overload(
            kse__vsk))


def _install_offsets_unsupported():
    for jpkni__udn in offsets_unsupported:
        kse__vsk = 'pandas.tseries.offsets.' + jpkni__udn.__name__
        overload(jpkni__udn)(create_unsupported_overload(kse__vsk))


def _install_frequencies_unsupported():
    for jpkni__udn in frequencies_unsupported:
        kse__vsk = 'pandas.tseries.frequencies.' + jpkni__udn.__name__
        overload(jpkni__udn)(create_unsupported_overload(kse__vsk))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
