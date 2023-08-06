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
        pkj__fgq = [('year', types.int64), ('month', types.int64), ('day',
            types.int64), ('hour', types.int64), ('minute', types.int64), (
            'second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, pkj__fgq)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    tlgk__bxuro = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    iyolb__qjwsf = c.pyapi.long_from_longlong(tlgk__bxuro.year)
    yop__bihz = c.pyapi.long_from_longlong(tlgk__bxuro.month)
    ayux__lmgb = c.pyapi.long_from_longlong(tlgk__bxuro.day)
    tcyrg__rjxl = c.pyapi.long_from_longlong(tlgk__bxuro.hour)
    poxl__alicv = c.pyapi.long_from_longlong(tlgk__bxuro.minute)
    fyyki__bvgn = c.pyapi.long_from_longlong(tlgk__bxuro.second)
    mfer__vmo = c.pyapi.long_from_longlong(tlgk__bxuro.microsecond)
    rygh__eov = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.datetime)
        )
    ibazm__lmz = c.pyapi.call_function_objargs(rygh__eov, (iyolb__qjwsf,
        yop__bihz, ayux__lmgb, tcyrg__rjxl, poxl__alicv, fyyki__bvgn,
        mfer__vmo))
    c.pyapi.decref(iyolb__qjwsf)
    c.pyapi.decref(yop__bihz)
    c.pyapi.decref(ayux__lmgb)
    c.pyapi.decref(tcyrg__rjxl)
    c.pyapi.decref(poxl__alicv)
    c.pyapi.decref(fyyki__bvgn)
    c.pyapi.decref(mfer__vmo)
    c.pyapi.decref(rygh__eov)
    return ibazm__lmz


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    iyolb__qjwsf = c.pyapi.object_getattr_string(val, 'year')
    yop__bihz = c.pyapi.object_getattr_string(val, 'month')
    ayux__lmgb = c.pyapi.object_getattr_string(val, 'day')
    tcyrg__rjxl = c.pyapi.object_getattr_string(val, 'hour')
    poxl__alicv = c.pyapi.object_getattr_string(val, 'minute')
    fyyki__bvgn = c.pyapi.object_getattr_string(val, 'second')
    mfer__vmo = c.pyapi.object_getattr_string(val, 'microsecond')
    tlgk__bxuro = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tlgk__bxuro.year = c.pyapi.long_as_longlong(iyolb__qjwsf)
    tlgk__bxuro.month = c.pyapi.long_as_longlong(yop__bihz)
    tlgk__bxuro.day = c.pyapi.long_as_longlong(ayux__lmgb)
    tlgk__bxuro.hour = c.pyapi.long_as_longlong(tcyrg__rjxl)
    tlgk__bxuro.minute = c.pyapi.long_as_longlong(poxl__alicv)
    tlgk__bxuro.second = c.pyapi.long_as_longlong(fyyki__bvgn)
    tlgk__bxuro.microsecond = c.pyapi.long_as_longlong(mfer__vmo)
    c.pyapi.decref(iyolb__qjwsf)
    c.pyapi.decref(yop__bihz)
    c.pyapi.decref(ayux__lmgb)
    c.pyapi.decref(tcyrg__rjxl)
    c.pyapi.decref(poxl__alicv)
    c.pyapi.decref(fyyki__bvgn)
    c.pyapi.decref(mfer__vmo)
    ofiq__lzm = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tlgk__bxuro._getvalue(), is_error=ofiq__lzm)


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
        tlgk__bxuro = cgutils.create_struct_proxy(typ)(context, builder)
        tlgk__bxuro.year = args[0]
        tlgk__bxuro.month = args[1]
        tlgk__bxuro.day = args[2]
        tlgk__bxuro.hour = args[3]
        tlgk__bxuro.minute = args[4]
        tlgk__bxuro.second = args[5]
        tlgk__bxuro.microsecond = args[6]
        return tlgk__bxuro._getvalue()
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
                y, tdhg__rvoa = lhs.year, rhs.year
                jyd__wmomk, pajsz__oilev = lhs.month, rhs.month
                d, zxo__dqaa = lhs.day, rhs.day
                oyss__ijd, tyfdj__xdo = lhs.hour, rhs.hour
                vnn__cdtf, sfl__kxtw = lhs.minute, rhs.minute
                rmsmf__yvbg, iyb__drakp = lhs.second, rhs.second
                iiw__cntc, zmso__upz = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, jyd__wmomk, d, oyss__ijd, vnn__cdtf,
                    rmsmf__yvbg, iiw__cntc), (tdhg__rvoa, pajsz__oilev,
                    zxo__dqaa, tyfdj__xdo, sfl__kxtw, iyb__drakp, zmso__upz
                    )), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            vrkl__kwof = lhs.toordinal()
            ddhg__wkwv = rhs.toordinal()
            ojip__auuub = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            dcueq__xonby = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            hrj__haxo = datetime.timedelta(vrkl__kwof - ddhg__wkwv, 
                ojip__auuub - dcueq__xonby, lhs.microsecond - rhs.microsecond)
            return hrj__haxo
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    myb__wwws = context.make_helper(builder, fromty, value=val)
    tkq__idu = cgutils.as_bool_bit(builder, myb__wwws.valid)
    with builder.if_else(tkq__idu) as (then, orelse):
        with then:
            uen__nlt = context.cast(builder, myb__wwws.data, fromty.type, toty)
            bli__iwgq = builder.block
        with orelse:
            mmt__dds = numba.np.npdatetime.NAT
            jcbz__nmlb = builder.block
    ibazm__lmz = builder.phi(uen__nlt.type)
    ibazm__lmz.add_incoming(uen__nlt, bli__iwgq)
    ibazm__lmz.add_incoming(mmt__dds, jcbz__nmlb)
    return ibazm__lmz
