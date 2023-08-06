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
        woyrz__ywh = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, woyrz__ywh)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    sgf__rxsnd = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    kqnp__mysxy = c.pyapi.long_from_longlong(sgf__rxsnd.n)
    kyhj__erwe = c.pyapi.from_native_value(types.boolean, sgf__rxsnd.
        normalize, c.env_manager)
    wubo__buaj = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    shs__vitx = c.pyapi.call_function_objargs(wubo__buaj, (kqnp__mysxy,
        kyhj__erwe))
    c.pyapi.decref(kqnp__mysxy)
    c.pyapi.decref(kyhj__erwe)
    c.pyapi.decref(wubo__buaj)
    return shs__vitx


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    kqnp__mysxy = c.pyapi.object_getattr_string(val, 'n')
    kyhj__erwe = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(kqnp__mysxy)
    normalize = c.pyapi.to_native_value(types.bool_, kyhj__erwe).value
    sgf__rxsnd = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    sgf__rxsnd.n = n
    sgf__rxsnd.normalize = normalize
    c.pyapi.decref(kqnp__mysxy)
    c.pyapi.decref(kyhj__erwe)
    wxzk__xhdnk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(sgf__rxsnd._getvalue(), is_error=wxzk__xhdnk)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        sgf__rxsnd = cgutils.create_struct_proxy(typ)(context, builder)
        sgf__rxsnd.n = args[0]
        sgf__rxsnd.normalize = args[1]
        return sgf__rxsnd._getvalue()
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
        woyrz__ywh = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, woyrz__ywh)


@box(MonthEndType)
def box_month_end(typ, val, c):
    wmjmu__wfw = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    kqnp__mysxy = c.pyapi.long_from_longlong(wmjmu__wfw.n)
    kyhj__erwe = c.pyapi.from_native_value(types.boolean, wmjmu__wfw.
        normalize, c.env_manager)
    rxw__dsaw = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    shs__vitx = c.pyapi.call_function_objargs(rxw__dsaw, (kqnp__mysxy,
        kyhj__erwe))
    c.pyapi.decref(kqnp__mysxy)
    c.pyapi.decref(kyhj__erwe)
    c.pyapi.decref(rxw__dsaw)
    return shs__vitx


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    kqnp__mysxy = c.pyapi.object_getattr_string(val, 'n')
    kyhj__erwe = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(kqnp__mysxy)
    normalize = c.pyapi.to_native_value(types.bool_, kyhj__erwe).value
    wmjmu__wfw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wmjmu__wfw.n = n
    wmjmu__wfw.normalize = normalize
    c.pyapi.decref(kqnp__mysxy)
    c.pyapi.decref(kyhj__erwe)
    wxzk__xhdnk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(wmjmu__wfw._getvalue(), is_error=wxzk__xhdnk)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        wmjmu__wfw = cgutils.create_struct_proxy(typ)(context, builder)
        wmjmu__wfw.n = args[0]
        wmjmu__wfw.normalize = args[1]
        return wmjmu__wfw._getvalue()
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
        wmjmu__wfw = get_days_in_month(year, month)
        if wmjmu__wfw > day:
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
        woyrz__ywh = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, woyrz__ywh)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    bszt__xjh = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    hcr__sjjqe = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for tsjlu__lmt, bwbxs__zxkg in enumerate(date_offset_fields):
        c.builder.store(getattr(bszt__xjh, bwbxs__zxkg), c.builder.inttoptr
            (c.builder.add(c.builder.ptrtoint(hcr__sjjqe, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * tsjlu__lmt)), lir.IntType(64)
            .as_pointer()))
    tcf__ycn = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    mtvs__aykb = cgutils.get_or_insert_function(c.builder.module, tcf__ycn,
        name='box_date_offset')
    ljd__nzuk = c.builder.call(mtvs__aykb, [bszt__xjh.n, bszt__xjh.
        normalize, hcr__sjjqe, bszt__xjh.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return ljd__nzuk


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    kqnp__mysxy = c.pyapi.object_getattr_string(val, 'n')
    kyhj__erwe = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(kqnp__mysxy)
    normalize = c.pyapi.to_native_value(types.bool_, kyhj__erwe).value
    hcr__sjjqe = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    tcf__ycn = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer(
        ), lir.IntType(64).as_pointer()])
    obwkd__ssy = cgutils.get_or_insert_function(c.builder.module, tcf__ycn,
        name='unbox_date_offset')
    has_kws = c.builder.call(obwkd__ssy, [val, hcr__sjjqe])
    bszt__xjh = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    bszt__xjh.n = n
    bszt__xjh.normalize = normalize
    for tsjlu__lmt, bwbxs__zxkg in enumerate(date_offset_fields):
        setattr(bszt__xjh, bwbxs__zxkg, c.builder.load(c.builder.inttoptr(c
            .builder.add(c.builder.ptrtoint(hcr__sjjqe, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * tsjlu__lmt)), lir.IntType(64)
            .as_pointer())))
    bszt__xjh.has_kws = has_kws
    c.pyapi.decref(kqnp__mysxy)
    c.pyapi.decref(kyhj__erwe)
    wxzk__xhdnk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(bszt__xjh._getvalue(), is_error=wxzk__xhdnk)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    est__hka = [n, normalize]
    has_kws = False
    vqsrh__ooly = [0] * 9 + [-1] * 9
    for tsjlu__lmt, bwbxs__zxkg in enumerate(date_offset_fields):
        if hasattr(pyval, bwbxs__zxkg):
            rmcv__pnvf = context.get_constant(types.int64, getattr(pyval,
                bwbxs__zxkg))
            if bwbxs__zxkg != 'nanoseconds' and bwbxs__zxkg != 'nanosecond':
                has_kws = True
        else:
            rmcv__pnvf = context.get_constant(types.int64, vqsrh__ooly[
                tsjlu__lmt])
        est__hka.append(rmcv__pnvf)
    has_kws = context.get_constant(types.boolean, has_kws)
    est__hka.append(has_kws)
    return lir.Constant.literal_struct(est__hka)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    bsdz__lpu = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for zvtar__gpeg in bsdz__lpu:
        if not is_overload_none(zvtar__gpeg):
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
        bszt__xjh = cgutils.create_struct_proxy(typ)(context, builder)
        bszt__xjh.n = args[0]
        bszt__xjh.normalize = args[1]
        bszt__xjh.years = args[2]
        bszt__xjh.months = args[3]
        bszt__xjh.weeks = args[4]
        bszt__xjh.days = args[5]
        bszt__xjh.hours = args[6]
        bszt__xjh.minutes = args[7]
        bszt__xjh.seconds = args[8]
        bszt__xjh.microseconds = args[9]
        bszt__xjh.nanoseconds = args[10]
        bszt__xjh.year = args[11]
        bszt__xjh.month = args[12]
        bszt__xjh.day = args[13]
        bszt__xjh.weekday = args[14]
        bszt__xjh.hour = args[15]
        bszt__xjh.minute = args[16]
        bszt__xjh.second = args[17]
        bszt__xjh.microsecond = args[18]
        bszt__xjh.nanosecond = args[19]
        bszt__xjh.has_kws = args[20]
        return bszt__xjh._getvalue()
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
        uxr__wlmkq = -1 if dateoffset.n < 0 else 1
        for vvab__rzxf in range(np.abs(dateoffset.n)):
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
            year += uxr__wlmkq * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += uxr__wlmkq * dateoffset._months
            year, month, qja__uxjzh = calculate_month_end_date(year, month,
                day, 0)
            if day > qja__uxjzh:
                day = qja__uxjzh
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
            tyawg__tvs = pd.Timedelta(days=dateoffset._days + 7 *
                dateoffset._weeks, hours=dateoffset._hours, minutes=
                dateoffset._minutes, seconds=dateoffset._seconds,
                microseconds=dateoffset._microseconds)
            if uxr__wlmkq == -1:
                tyawg__tvs = -tyawg__tvs
            ts = ts + tyawg__tvs
            if dateoffset._weekday != -1:
                bns__vdcw = ts.weekday()
                zybn__eby = (dateoffset._weekday - bns__vdcw) % 7
                ts = ts + pd.Timedelta(days=zybn__eby)
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
        woyrz__ywh = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, woyrz__ywh)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        qejb__ndh = -1 if weekday is None else weekday
        return init_week(n, normalize, qejb__ndh)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        lqh__yoafb = cgutils.create_struct_proxy(typ)(context, builder)
        lqh__yoafb.n = args[0]
        lqh__yoafb.normalize = args[1]
        lqh__yoafb.weekday = args[2]
        return lqh__yoafb._getvalue()
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
    lqh__yoafb = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    kqnp__mysxy = c.pyapi.long_from_longlong(lqh__yoafb.n)
    kyhj__erwe = c.pyapi.from_native_value(types.boolean, lqh__yoafb.
        normalize, c.env_manager)
    lmlly__bqlt = c.pyapi.long_from_longlong(lqh__yoafb.weekday)
    mzn__oyla = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    ere__ckk = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64), -1
        ), lqh__yoafb.weekday)
    with c.builder.if_else(ere__ckk) as (weekday_defined, weekday_undefined):
        with weekday_defined:
            qmei__icfcf = c.pyapi.call_function_objargs(mzn__oyla, (
                kqnp__mysxy, kyhj__erwe, lmlly__bqlt))
            bjic__ycl = c.builder.block
        with weekday_undefined:
            wsmn__itrrc = c.pyapi.call_function_objargs(mzn__oyla, (
                kqnp__mysxy, kyhj__erwe))
            yszw__wudba = c.builder.block
    shs__vitx = c.builder.phi(qmei__icfcf.type)
    shs__vitx.add_incoming(qmei__icfcf, bjic__ycl)
    shs__vitx.add_incoming(wsmn__itrrc, yszw__wudba)
    c.pyapi.decref(lmlly__bqlt)
    c.pyapi.decref(kqnp__mysxy)
    c.pyapi.decref(kyhj__erwe)
    c.pyapi.decref(mzn__oyla)
    return shs__vitx


@unbox(WeekType)
def unbox_week(typ, val, c):
    kqnp__mysxy = c.pyapi.object_getattr_string(val, 'n')
    kyhj__erwe = c.pyapi.object_getattr_string(val, 'normalize')
    lmlly__bqlt = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(kqnp__mysxy)
    normalize = c.pyapi.to_native_value(types.bool_, kyhj__erwe).value
    ocba__hkfs = c.pyapi.make_none()
    wcxn__tatl = c.builder.icmp_unsigned('==', lmlly__bqlt, ocba__hkfs)
    with c.builder.if_else(wcxn__tatl) as (weekday_undefined, weekday_defined):
        with weekday_defined:
            qmei__icfcf = c.pyapi.long_as_longlong(lmlly__bqlt)
            bjic__ycl = c.builder.block
        with weekday_undefined:
            wsmn__itrrc = lir.Constant(lir.IntType(64), -1)
            yszw__wudba = c.builder.block
    shs__vitx = c.builder.phi(qmei__icfcf.type)
    shs__vitx.add_incoming(qmei__icfcf, bjic__ycl)
    shs__vitx.add_incoming(wsmn__itrrc, yszw__wudba)
    lqh__yoafb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    lqh__yoafb.n = n
    lqh__yoafb.normalize = normalize
    lqh__yoafb.weekday = shs__vitx
    c.pyapi.decref(kqnp__mysxy)
    c.pyapi.decref(kyhj__erwe)
    c.pyapi.decref(lmlly__bqlt)
    wxzk__xhdnk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(lqh__yoafb._getvalue(), is_error=wxzk__xhdnk)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            ltr__mewi = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                wuinh__gbgi = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                wuinh__gbgi = rhs
            return wuinh__gbgi + ltr__mewi
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            ltr__mewi = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                wuinh__gbgi = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                wuinh__gbgi = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return wuinh__gbgi + ltr__mewi
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            ltr__mewi = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            return rhs + ltr__mewi
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
        ryyg__jov = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=ryyg__jov)


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
    for lzutl__hdx in date_offset_unsupported_attrs:
        yjr__kitqc = 'pandas.tseries.offsets.DateOffset.' + lzutl__hdx
        overload_attribute(DateOffsetType, lzutl__hdx)(
            create_unsupported_overload(yjr__kitqc))
    for lzutl__hdx in date_offset_unsupported:
        yjr__kitqc = 'pandas.tseries.offsets.DateOffset.' + lzutl__hdx
        overload_method(DateOffsetType, lzutl__hdx)(create_unsupported_overload
            (yjr__kitqc))


def _install_month_begin_unsupported():
    for lzutl__hdx in month_begin_unsupported_attrs:
        yjr__kitqc = 'pandas.tseries.offsets.MonthBegin.' + lzutl__hdx
        overload_attribute(MonthBeginType, lzutl__hdx)(
            create_unsupported_overload(yjr__kitqc))
    for lzutl__hdx in month_begin_unsupported:
        yjr__kitqc = 'pandas.tseries.offsets.MonthBegin.' + lzutl__hdx
        overload_method(MonthBeginType, lzutl__hdx)(create_unsupported_overload
            (yjr__kitqc))


def _install_month_end_unsupported():
    for lzutl__hdx in date_offset_unsupported_attrs:
        yjr__kitqc = 'pandas.tseries.offsets.MonthEnd.' + lzutl__hdx
        overload_attribute(MonthEndType, lzutl__hdx)(
            create_unsupported_overload(yjr__kitqc))
    for lzutl__hdx in date_offset_unsupported:
        yjr__kitqc = 'pandas.tseries.offsets.MonthEnd.' + lzutl__hdx
        overload_method(MonthEndType, lzutl__hdx)(create_unsupported_overload
            (yjr__kitqc))


def _install_week_unsupported():
    for lzutl__hdx in week_unsupported_attrs:
        yjr__kitqc = 'pandas.tseries.offsets.Week.' + lzutl__hdx
        overload_attribute(WeekType, lzutl__hdx)(create_unsupported_overload
            (yjr__kitqc))
    for lzutl__hdx in week_unsupported:
        yjr__kitqc = 'pandas.tseries.offsets.Week.' + lzutl__hdx
        overload_method(WeekType, lzutl__hdx)(create_unsupported_overload(
            yjr__kitqc))


def _install_offsets_unsupported():
    for rmcv__pnvf in offsets_unsupported:
        yjr__kitqc = 'pandas.tseries.offsets.' + rmcv__pnvf.__name__
        overload(rmcv__pnvf)(create_unsupported_overload(yjr__kitqc))


def _install_frequencies_unsupported():
    for rmcv__pnvf in frequencies_unsupported:
        yjr__kitqc = 'pandas.tseries.frequencies.' + rmcv__pnvf.__name__
        overload(rmcv__pnvf)(create_unsupported_overload(yjr__kitqc))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
