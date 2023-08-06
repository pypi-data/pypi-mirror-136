import datetime
import numba
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
"""
Implementation is based on
https://github.com/python/cpython/blob/39a5c889d30d03a88102e56f03ee0c95db198fb3/Lib/datetime.py
"""


class DatetimeDatetimeType(types.Type):

    def __init__(self):
        super(DatetimeDatetimeType, self).__init__(name=
            'DatetimeDatetimeType()')


datetime_datetime_type = DatetimeDatetimeType()
types.datetime_datetime_type = datetime_datetime_type


@typeof_impl.register(datetime.datetime)
def typeof_datetime_datetime(val, c):
    return datetime_datetime_type


@register_model(DatetimeDatetimeType)
class DatetimeDateTimeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        udr__nxw = [('year', types.int64), ('month', types.int64), ('day',
            types.int64), ('hour', types.int64), ('minute', types.int64), (
            'second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, udr__nxw)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    sjdd__nzowa = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    hjul__phif = c.pyapi.long_from_longlong(sjdd__nzowa.year)
    audh__kgh = c.pyapi.long_from_longlong(sjdd__nzowa.month)
    oyf__dcdt = c.pyapi.long_from_longlong(sjdd__nzowa.day)
    tot__oaij = c.pyapi.long_from_longlong(sjdd__nzowa.hour)
    vyts__lpflu = c.pyapi.long_from_longlong(sjdd__nzowa.minute)
    plse__arp = c.pyapi.long_from_longlong(sjdd__nzowa.second)
    hbsno__dqusy = c.pyapi.long_from_longlong(sjdd__nzowa.microsecond)
    arr__fbd = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.datetime))
    qvxvy__zka = c.pyapi.call_function_objargs(arr__fbd, (hjul__phif,
        audh__kgh, oyf__dcdt, tot__oaij, vyts__lpflu, plse__arp, hbsno__dqusy))
    c.pyapi.decref(hjul__phif)
    c.pyapi.decref(audh__kgh)
    c.pyapi.decref(oyf__dcdt)
    c.pyapi.decref(tot__oaij)
    c.pyapi.decref(vyts__lpflu)
    c.pyapi.decref(plse__arp)
    c.pyapi.decref(hbsno__dqusy)
    c.pyapi.decref(arr__fbd)
    return qvxvy__zka


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    hjul__phif = c.pyapi.object_getattr_string(val, 'year')
    audh__kgh = c.pyapi.object_getattr_string(val, 'month')
    oyf__dcdt = c.pyapi.object_getattr_string(val, 'day')
    tot__oaij = c.pyapi.object_getattr_string(val, 'hour')
    vyts__lpflu = c.pyapi.object_getattr_string(val, 'minute')
    plse__arp = c.pyapi.object_getattr_string(val, 'second')
    hbsno__dqusy = c.pyapi.object_getattr_string(val, 'microsecond')
    sjdd__nzowa = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    sjdd__nzowa.year = c.pyapi.long_as_longlong(hjul__phif)
    sjdd__nzowa.month = c.pyapi.long_as_longlong(audh__kgh)
    sjdd__nzowa.day = c.pyapi.long_as_longlong(oyf__dcdt)
    sjdd__nzowa.hour = c.pyapi.long_as_longlong(tot__oaij)
    sjdd__nzowa.minute = c.pyapi.long_as_longlong(vyts__lpflu)
    sjdd__nzowa.second = c.pyapi.long_as_longlong(plse__arp)
    sjdd__nzowa.microsecond = c.pyapi.long_as_longlong(hbsno__dqusy)
    c.pyapi.decref(hjul__phif)
    c.pyapi.decref(audh__kgh)
    c.pyapi.decref(oyf__dcdt)
    c.pyapi.decref(tot__oaij)
    c.pyapi.decref(vyts__lpflu)
    c.pyapi.decref(plse__arp)
    c.pyapi.decref(hbsno__dqusy)
    ovc__eysh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(sjdd__nzowa._getvalue(), is_error=ovc__eysh)


@lower_constant(DatetimeDatetimeType)
def constant_datetime(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    hour = context.get_constant(types.int64, pyval.hour)
    minute = context.get_constant(types.int64, pyval.minute)
    second = context.get_constant(types.int64, pyval.second)
    microsecond = context.get_constant(types.int64, pyval.microsecond)
    return lir.Constant.literal_struct([year, month, day, hour, minute,
        second, microsecond])


@overload(datetime.datetime, no_unliteral=True)
def datetime_datetime(year, month, day, hour=0, minute=0, second=0,
    microsecond=0):

    def impl_datetime(year, month, day, hour=0, minute=0, second=0,
        microsecond=0):
        return init_datetime(year, month, day, hour, minute, second,
            microsecond)
    return impl_datetime


@intrinsic
def init_datetime(typingctx, year, month, day, hour, minute, second,
    microsecond):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        sjdd__nzowa = cgutils.create_struct_proxy(typ)(context, builder)
        sjdd__nzowa.year = args[0]
        sjdd__nzowa.month = args[1]
        sjdd__nzowa.day = args[2]
        sjdd__nzowa.hour = args[3]
        sjdd__nzowa.minute = args[4]
        sjdd__nzowa.second = args[5]
        sjdd__nzowa.microsecond = args[6]
        return sjdd__nzowa._getvalue()
    return DatetimeDatetimeType()(year, month, day, hour, minute, second,
        microsecond), codegen


make_attribute_wrapper(DatetimeDatetimeType, 'year', '_year')
make_attribute_wrapper(DatetimeDatetimeType, 'month', '_month')
make_attribute_wrapper(DatetimeDatetimeType, 'day', '_day')
make_attribute_wrapper(DatetimeDatetimeType, 'hour', '_hour')
make_attribute_wrapper(DatetimeDatetimeType, 'minute', '_minute')
make_attribute_wrapper(DatetimeDatetimeType, 'second', '_second')
make_attribute_wrapper(DatetimeDatetimeType, 'microsecond', '_microsecond')


@overload_attribute(DatetimeDatetimeType, 'year')
def datetime_get_year(dt):

    def impl(dt):
        return dt._year
    return impl


@overload_attribute(DatetimeDatetimeType, 'month')
def datetime_get_month(dt):

    def impl(dt):
        return dt._month
    return impl


@overload_attribute(DatetimeDatetimeType, 'day')
def datetime_get_day(dt):

    def impl(dt):
        return dt._day
    return impl


@overload_attribute(DatetimeDatetimeType, 'hour')
def datetime_get_hour(dt):

    def impl(dt):
        return dt._hour
    return impl


@overload_attribute(DatetimeDatetimeType, 'minute')
def datetime_get_minute(dt):

    def impl(dt):
        return dt._minute
    return impl


@overload_attribute(DatetimeDatetimeType, 'second')
def datetime_get_second(dt):

    def impl(dt):
        return dt._second
    return impl


@overload_attribute(DatetimeDatetimeType, 'microsecond')
def datetime_get_microsecond(dt):

    def impl(dt):
        return dt._microsecond
    return impl


@overload_method(DatetimeDatetimeType, 'date', no_unliteral=True)
def date(dt):

    def impl(dt):
        return datetime.date(dt.year, dt.month, dt.day)
    return impl


@register_jitable
def now_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.now()
    return d


@register_jitable
def today_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.today()
    return d


@register_jitable
def strptime_impl(date_string, dtformat):
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.strptime(date_string, dtformat)
    return d


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


def create_cmp_op_overload(op):

    def overload_datetime_cmp(lhs, rhs):
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

            def impl(lhs, rhs):
                y, axip__xwy = lhs.year, rhs.year
                hmu__amxb, ajrmi__ebd = lhs.month, rhs.month
                d, fseh__fbesj = lhs.day, rhs.day
                hmxx__gupzw, setj__tqkw = lhs.hour, rhs.hour
                ulo__srz, fsj__dwj = lhs.minute, rhs.minute
                xqylh__fyrai, thm__zxh = lhs.second, rhs.second
                rgyt__sllp, wskat__lild = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, hmu__amxb, d, hmxx__gupzw, ulo__srz,
                    xqylh__fyrai, rgyt__sllp), (axip__xwy, ajrmi__ebd,
                    fseh__fbesj, setj__tqkw, fsj__dwj, thm__zxh,
                    wskat__lild)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            opul__dkl = lhs.toordinal()
            nql__udf = rhs.toordinal()
            ctu__wut = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            gphm__naw = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            xib__foy = datetime.timedelta(opul__dkl - nql__udf, ctu__wut -
                gphm__naw, lhs.microsecond - rhs.microsecond)
            return xib__foy
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    dsrkv__kyu = context.make_helper(builder, fromty, value=val)
    ezs__waxg = cgutils.as_bool_bit(builder, dsrkv__kyu.valid)
    with builder.if_else(ezs__waxg) as (then, orelse):
        with then:
            stc__ormt = context.cast(builder, dsrkv__kyu.data, fromty.type,
                toty)
            sbgz__patyz = builder.block
        with orelse:
            fzo__noq = numba.np.npdatetime.NAT
            ducg__wvd = builder.block
    qvxvy__zka = builder.phi(stc__ormt.type)
    qvxvy__zka.add_incoming(stc__ormt, sbgz__patyz)
    qvxvy__zka.add_incoming(fzo__noq, ducg__wvd)
    return qvxvy__zka
