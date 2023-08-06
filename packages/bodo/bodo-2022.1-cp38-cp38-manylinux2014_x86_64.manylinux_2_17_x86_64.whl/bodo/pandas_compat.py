import hashlib
import inspect
import pandas as pd
_check_pandas_change = False


def _set_noconvert_columns(self):
    assert self.orig_names is not None
    cxd__vpsnl = {aps__iqj: kofq__ibd for kofq__ibd, aps__iqj in enumerate(
        self.orig_names)}
    uwfb__wrg = [cxd__vpsnl[aps__iqj] for aps__iqj in self.names]
    mih__kxfih = self._set_noconvert_dtype_columns(uwfb__wrg, self.names)
    for rdg__wpnn in mih__kxfih:
        self._reader.set_noconvert(rdg__wpnn)


if _check_pandas_change:
    lines = inspect.getsource(pd.io.parsers.c_parser_wrapper.CParserWrapper
        ._set_noconvert_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'afc2d738f194e3976cf05d61cb16dc4224b0139451f08a1cf49c578af6f975d3':
        warnings.warn(
            'pd.io.parsers.c_parser_wrapper.CParserWrapper._set_noconvert_columns has changed'
            )
pd.io.parsers.c_parser_wrapper.CParserWrapper._set_noconvert_columns = (
    _set_noconvert_columns)
