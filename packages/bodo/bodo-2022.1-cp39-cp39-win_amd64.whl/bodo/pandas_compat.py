import hashlib
import inspect
import pandas as pd
_check_pandas_change = False


def _set_noconvert_columns(self):
    assert self.orig_names is not None
    baus__zxxr = {krbv__pxpk: gqkvb__osxxb for gqkvb__osxxb, krbv__pxpk in
        enumerate(self.orig_names)}
    bsz__liixf = [baus__zxxr[krbv__pxpk] for krbv__pxpk in self.names]
    btptx__lqgwf = self._set_noconvert_dtype_columns(bsz__liixf, self.names)
    for fuhm__psz in btptx__lqgwf:
        self._reader.set_noconvert(fuhm__psz)


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
