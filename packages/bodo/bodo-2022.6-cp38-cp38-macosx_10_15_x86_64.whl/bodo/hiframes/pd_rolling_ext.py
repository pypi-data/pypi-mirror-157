"""typing for rolling window functions
"""
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_method, register_model
import bodo
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.hiframes.pd_groupby_ext import DataFrameGroupByType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.rolling import supported_rolling_funcs, unsupported_rolling_methods
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, get_literal_value, is_const_func_type, is_literal_type, is_overload_bool, is_overload_constant_str, is_overload_int, is_overload_none, raise_bodo_error


class RollingType(types.Type):

    def __init__(self, obj_type, window_type, on, selection,
        explicit_select=False, series_select=False):
        if isinstance(obj_type, bodo.SeriesType):
            jqnmu__lsd = 'Series'
        else:
            jqnmu__lsd = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{jqnmu__lsd}.rolling()')
        self.obj_type = obj_type
        self.window_type = window_type
        self.on = on
        self.selection = selection
        self.explicit_select = explicit_select
        self.series_select = series_select
        super(RollingType, self).__init__(name=
            f'RollingType({obj_type}, {window_type}, {on}, {selection}, {explicit_select}, {series_select})'
            )

    def copy(self):
        return RollingType(self.obj_type, self.window_type, self.on, self.
            selection, self.explicit_select, self.series_select)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(RollingType)
class RollingModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cfkcn__tloqg = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, cfkcn__tloqg)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    plac__xnwps = dict(win_type=win_type, axis=axis, closed=closed)
    cgysx__ymgk = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', plac__xnwps, cgysx__ymgk,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(df, window, min_periods, center, on)

    def impl(df, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(df, window,
            min_periods, center, on)
    return impl


@overload_method(SeriesType, 'rolling', inline='always', no_unliteral=True)
def overload_series_rolling(S, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    plac__xnwps = dict(win_type=win_type, axis=axis, closed=closed)
    cgysx__ymgk = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', plac__xnwps, cgysx__ymgk,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(S, window, min_periods, center, on)

    def impl(S, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(S, window,
            min_periods, center, on)
    return impl


@intrinsic
def init_rolling(typingctx, obj_type, window_type, min_periods_type,
    center_type, on_type=None):

    def codegen(context, builder, signature, args):
        uevuf__btasz, mogu__pov, cihv__fuws, gjvo__ocbi, wcnb__wiedu = args
        ddr__cxosq = signature.return_type
        kpv__jzvlf = cgutils.create_struct_proxy(ddr__cxosq)(context, builder)
        kpv__jzvlf.obj = uevuf__btasz
        kpv__jzvlf.window = mogu__pov
        kpv__jzvlf.min_periods = cihv__fuws
        kpv__jzvlf.center = gjvo__ocbi
        context.nrt.incref(builder, signature.args[0], uevuf__btasz)
        context.nrt.incref(builder, signature.args[1], mogu__pov)
        context.nrt.incref(builder, signature.args[2], cihv__fuws)
        context.nrt.incref(builder, signature.args[3], gjvo__ocbi)
        return kpv__jzvlf._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    ddr__cxosq = RollingType(obj_type, window_type, on, selection, False)
    return ddr__cxosq(obj_type, window_type, min_periods_type, center_type,
        on_type), codegen


def _handle_default_min_periods(min_periods, window):
    return min_periods


@overload(_handle_default_min_periods)
def overload_handle_default_min_periods(min_periods, window):
    if is_overload_none(min_periods):
        if isinstance(window, types.Integer):
            return lambda min_periods, window: window
        else:
            return lambda min_periods, window: 1
    else:
        return lambda min_periods, window: min_periods


def _gen_df_rolling_out_data(rolling):
    bget__kww = not isinstance(rolling.window_type, types.Integer)
    kvgou__vsn = 'variable' if bget__kww else 'fixed'
    grsgf__nzor = 'None'
    if bget__kww:
        grsgf__nzor = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    dtjd__ndq = []
    mytp__yxd = 'on_arr, ' if bget__kww else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{kvgou__vsn}(bodo.hiframes.pd_series_ext.get_series_data(df), {mytp__yxd}index_arr, window, minp, center, func, raw)'
            , grsgf__nzor, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    pzsg__siwfw = rolling.obj_type.data
    out_cols = []
    for cnmvd__noc in rolling.selection:
        rwxyn__lbyr = rolling.obj_type.columns.index(cnmvd__noc)
        if cnmvd__noc == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            jefc__mly = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rwxyn__lbyr})'
                )
            out_cols.append(cnmvd__noc)
        else:
            if not isinstance(pzsg__siwfw[rwxyn__lbyr].dtype, (types.
                Boolean, types.Number)):
                continue
            jefc__mly = (
                f'bodo.hiframes.rolling.rolling_{kvgou__vsn}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rwxyn__lbyr}), {mytp__yxd}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(cnmvd__noc)
        dtjd__ndq.append(jefc__mly)
    return ', '.join(dtjd__ndq), grsgf__nzor, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    plac__xnwps = dict(engine=engine, engine_kwargs=engine_kwargs, args=
        args, kwargs=kwargs)
    cgysx__ymgk = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', plac__xnwps, cgysx__ymgk,
        package_name='pandas', module_name='Window')
    if not is_const_func_type(func):
        raise BodoError(
            f"Rolling.apply(): 'func' parameter must be a function, not {func} (builtin functions not supported yet)."
            )
    if not is_overload_bool(raw):
        raise BodoError(
            f"Rolling.apply(): 'raw' parameter must be bool, not {raw}.")
    return _gen_rolling_impl(rolling, 'apply')


@overload_method(DataFrameGroupByType, 'rolling', inline='always',
    no_unliteral=True)
def groupby_rolling_overload(grp, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None, method='single'):
    plac__xnwps = dict(win_type=win_type, axis=axis, closed=closed, method=
        method)
    cgysx__ymgk = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', plac__xnwps, cgysx__ymgk,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(grp, window, min_periods, center, on)

    def _impl(grp, window, min_periods=None, center=False, win_type=None,
        on=None, axis=0, closed=None, method='single'):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(grp, window,
            min_periods, center, on)
    return _impl


def _gen_rolling_impl(rolling, fname, other=None):
    if isinstance(rolling.obj_type, DataFrameGroupByType):
        kati__vmw = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        xydd__spw = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{ynxnm__qhgw}'" if
                isinstance(ynxnm__qhgw, str) else f'{ynxnm__qhgw}' for
                ynxnm__qhgw in rolling.selection if ynxnm__qhgw != rolling.on))
        pwhin__deij = vtpvk__vmzr = ''
        if fname == 'apply':
            pwhin__deij = 'func, raw, args, kwargs'
            vtpvk__vmzr = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            pwhin__deij = vtpvk__vmzr = 'other, pairwise'
        if fname == 'cov':
            pwhin__deij = vtpvk__vmzr = 'other, pairwise, ddof'
        hzav__pxl = (
            f'lambda df, window, minp, center, {pwhin__deij}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {xydd__spw}){selection}.{fname}({vtpvk__vmzr})'
            )
        kati__vmw += f"""  return rolling.obj.apply({hzav__pxl}, rolling.window, rolling.min_periods, rolling.center, {pwhin__deij})
"""
        mvgk__aoo = {}
        exec(kati__vmw, {'bodo': bodo}, mvgk__aoo)
        impl = mvgk__aoo['impl']
        return impl
    pyouf__ercf = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if pyouf__ercf else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if pyouf__ercf else rolling.obj_type.columns
        other_cols = None if pyouf__ercf else other.columns
        dtjd__ndq, grsgf__nzor = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        dtjd__ndq, grsgf__nzor, out_cols = _gen_df_rolling_out_data(rolling)
    vtfv__lvlur = pyouf__ercf or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    nmaol__bhdu = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    nmaol__bhdu += '  df = rolling.obj\n'
    nmaol__bhdu += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if pyouf__ercf else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    jqnmu__lsd = 'None'
    if pyouf__ercf:
        jqnmu__lsd = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif vtfv__lvlur:
        cnmvd__noc = (set(out_cols) - set([rolling.on])).pop()
        jqnmu__lsd = f"'{cnmvd__noc}'" if isinstance(cnmvd__noc, str) else str(
            cnmvd__noc)
    nmaol__bhdu += f'  name = {jqnmu__lsd}\n'
    nmaol__bhdu += '  window = rolling.window\n'
    nmaol__bhdu += '  center = rolling.center\n'
    nmaol__bhdu += '  minp = rolling.min_periods\n'
    nmaol__bhdu += f'  on_arr = {grsgf__nzor}\n'
    if fname == 'apply':
        nmaol__bhdu += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        nmaol__bhdu += f"  func = '{fname}'\n"
        nmaol__bhdu += f'  index_arr = None\n'
        nmaol__bhdu += f'  raw = False\n'
    if vtfv__lvlur:
        nmaol__bhdu += (
            f'  return bodo.hiframes.pd_series_ext.init_series({dtjd__ndq}, index, name)'
            )
        mvgk__aoo = {}
        lzc__xdeer = {'bodo': bodo}
        exec(nmaol__bhdu, lzc__xdeer, mvgk__aoo)
        impl = mvgk__aoo['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(nmaol__bhdu, out_cols,
        dtjd__ndq)


def _get_rolling_func_args(fname):
    if fname == 'apply':
        return (
            'func, raw=False, engine=None, engine_kwargs=None, args=None, kwargs=None\n'
            )
    elif fname == 'corr':
        return 'other=None, pairwise=None, ddof=1\n'
    elif fname == 'cov':
        return 'other=None, pairwise=None, ddof=1\n'
    return ''


def create_rolling_overload(fname):

    def overload_rolling_func(rolling):
        return _gen_rolling_impl(rolling, fname)
    return overload_rolling_func


def _install_rolling_methods():
    for fname in supported_rolling_funcs:
        if fname in ('apply', 'corr', 'cov'):
            continue
        rxdn__xavsj = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(rxdn__xavsj)


def _install_rolling_unsupported_methods():
    for fname in unsupported_rolling_methods:
        overload_method(RollingType, fname, no_unliteral=True)(
            create_unsupported_overload(
            f'pandas.core.window.rolling.Rolling.{fname}()'))


_install_rolling_methods()
_install_rolling_unsupported_methods()


def _get_corr_cov_out_cols(rolling, other, func_name):
    if not isinstance(other, DataFrameType):
        raise_bodo_error(
            f"DataFrame.rolling.{func_name}(): requires providing a DataFrame for 'other'"
            )
    fas__xfr = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(fas__xfr) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    bget__kww = not isinstance(window_type, types.Integer)
    grsgf__nzor = 'None'
    if bget__kww:
        grsgf__nzor = 'bodo.utils.conversion.index_to_array(index)'
    mytp__yxd = 'on_arr, ' if bget__kww else ''
    dtjd__ndq = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {mytp__yxd}window, minp, center)'
            , grsgf__nzor)
    for cnmvd__noc in out_cols:
        if cnmvd__noc in df_cols and cnmvd__noc in other_cols:
            egye__vtid = df_cols.index(cnmvd__noc)
            kibnb__ycx = other_cols.index(cnmvd__noc)
            jefc__mly = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {egye__vtid}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {kibnb__ycx}), {mytp__yxd}window, minp, center)'
                )
        else:
            jefc__mly = 'np.full(len(df), np.nan)'
        dtjd__ndq.append(jefc__mly)
    return ', '.join(dtjd__ndq), grsgf__nzor


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    pkcv__pgwxp = {'pairwise': pairwise, 'ddof': ddof}
    ymjzj__hni = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        pkcv__pgwxp, ymjzj__hni, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    pkcv__pgwxp = {'ddof': ddof, 'pairwise': pairwise}
    ymjzj__hni = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        pkcv__pgwxp, ymjzj__hni, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, copw__nyty = args
        if isinstance(rolling, RollingType):
            fas__xfr = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(copw__nyty, (tuple, list)):
                if len(set(copw__nyty).difference(set(fas__xfr))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(copw__nyty).difference(set(fas__xfr))))
                selection = list(copw__nyty)
            else:
                if copw__nyty not in fas__xfr:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(copw__nyty))
                selection = [copw__nyty]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            msir__rqib = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(msir__rqib, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        fas__xfr = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            fas__xfr = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            fas__xfr = rolling.obj_type.columns
        if attr in fas__xfr:
            return RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, (attr,) if rolling.on is None else (attr,
                rolling.on), True, True)


def _validate_rolling_args(obj, window, min_periods, center, on):
    assert isinstance(obj, (SeriesType, DataFrameType, DataFrameGroupByType)
        ), 'invalid rolling obj'
    func_name = 'Series' if isinstance(obj, SeriesType
        ) else 'DataFrame' if isinstance(obj, DataFrameType
        ) else 'DataFrameGroupBy'
    if not (is_overload_int(window) or is_overload_constant_str(window) or 
        window == bodo.string_type or window in (pd_timedelta_type,
        datetime_timedelta_type)):
        raise BodoError(
            f"{func_name}.rolling(): 'window' should be int or time offset (str, pd.Timedelta, datetime.timedelta), not {window}"
            )
    if not is_overload_bool(center):
        raise BodoError(
            f'{func_name}.rolling(): center must be a boolean, not {center}')
    if not (is_overload_none(min_periods) or isinstance(min_periods, types.
        Integer)):
        raise BodoError(
            f'{func_name}.rolling(): min_periods must be an integer, not {min_periods}'
            )
    if isinstance(obj, SeriesType) and not is_overload_none(on):
        raise BodoError(
            f"{func_name}.rolling(): 'on' not supported for Series yet (can use a DataFrame instead)."
            )
    icwu__gvy = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    pzsg__siwfw = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in icwu__gvy):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        jpv__tnn = pzsg__siwfw[icwu__gvy.index(get_literal_value(on))]
        if not isinstance(jpv__tnn, types.Array
            ) or jpv__tnn.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(wgbv__tkjcg.dtype, (types.Boolean, types.Number)) for
        wgbv__tkjcg in pzsg__siwfw):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
