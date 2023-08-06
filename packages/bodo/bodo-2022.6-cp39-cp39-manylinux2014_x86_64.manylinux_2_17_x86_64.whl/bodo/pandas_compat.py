import hashlib
import inspect
import warnings
import pandas as pd
pandas_version = tuple(map(int, pd.__version__.split('.')[:2]))
_check_pandas_change = False
if pandas_version < (1, 4):

    def _set_noconvert_columns(self):
        assert self.orig_names is not None
        vbuv__zmk = {igdpa__czhx: yvn__kpf for yvn__kpf, igdpa__czhx in
            enumerate(self.orig_names)}
        dyzy__nbwam = [vbuv__zmk[igdpa__czhx] for igdpa__czhx in self.names]
        ykga__fmbt = self._set_noconvert_dtype_columns(dyzy__nbwam, self.names)
        for jse__txxj in ykga__fmbt:
            self._reader.set_noconvert(jse__txxj)
    if _check_pandas_change:
        lines = inspect.getsource(pd.io.parsers.c_parser_wrapper.
            CParserWrapper._set_noconvert_columns)
        if (hashlib.sha256(lines.encode()).hexdigest() !=
            'afc2d738f194e3976cf05d61cb16dc4224b0139451f08a1cf49c578af6f975d3'
            ):
            warnings.warn(
                'pd.io.parsers.c_parser_wrapper.CParserWrapper._set_noconvert_columns has changed'
                )
    (pd.io.parsers.c_parser_wrapper.CParserWrapper._set_noconvert_columns
        ) = _set_noconvert_columns
