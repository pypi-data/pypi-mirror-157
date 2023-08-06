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
            qlew__igy = 'Series'
        else:
            qlew__igy = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{qlew__igy}.rolling()')
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
        wzh__thf = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, wzh__thf)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    hiws__pbj = dict(win_type=win_type, axis=axis, closed=closed)
    mnk__ijh = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', hiws__pbj, mnk__ijh,
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
    hiws__pbj = dict(win_type=win_type, axis=axis, closed=closed)
    mnk__ijh = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', hiws__pbj, mnk__ijh,
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
        uwkx__hjs, zci__rldek, wgri__exstp, rxw__jme, tgmu__hrkp = args
        ian__ntyg = signature.return_type
        ncd__rtaf = cgutils.create_struct_proxy(ian__ntyg)(context, builder)
        ncd__rtaf.obj = uwkx__hjs
        ncd__rtaf.window = zci__rldek
        ncd__rtaf.min_periods = wgri__exstp
        ncd__rtaf.center = rxw__jme
        context.nrt.incref(builder, signature.args[0], uwkx__hjs)
        context.nrt.incref(builder, signature.args[1], zci__rldek)
        context.nrt.incref(builder, signature.args[2], wgri__exstp)
        context.nrt.incref(builder, signature.args[3], rxw__jme)
        return ncd__rtaf._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    ian__ntyg = RollingType(obj_type, window_type, on, selection, False)
    return ian__ntyg(obj_type, window_type, min_periods_type, center_type,
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
    jfxvm__lcwjx = not isinstance(rolling.window_type, types.Integer)
    oxbzh__rrtf = 'variable' if jfxvm__lcwjx else 'fixed'
    xsq__tbte = 'None'
    if jfxvm__lcwjx:
        xsq__tbte = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    kab__asftn = []
    fatp__uqo = 'on_arr, ' if jfxvm__lcwjx else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{oxbzh__rrtf}(bodo.hiframes.pd_series_ext.get_series_data(df), {fatp__uqo}index_arr, window, minp, center, func, raw)'
            , xsq__tbte, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    vizv__vwy = rolling.obj_type.data
    out_cols = []
    for yjdw__icso in rolling.selection:
        ross__fsv = rolling.obj_type.columns.index(yjdw__icso)
        if yjdw__icso == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            byoyg__kaoy = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ross__fsv})'
                )
            out_cols.append(yjdw__icso)
        else:
            if not isinstance(vizv__vwy[ross__fsv].dtype, (types.Boolean,
                types.Number)):
                continue
            byoyg__kaoy = (
                f'bodo.hiframes.rolling.rolling_{oxbzh__rrtf}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ross__fsv}), {fatp__uqo}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(yjdw__icso)
        kab__asftn.append(byoyg__kaoy)
    return ', '.join(kab__asftn), xsq__tbte, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    hiws__pbj = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    mnk__ijh = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', hiws__pbj, mnk__ijh,
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
    hiws__pbj = dict(win_type=win_type, axis=axis, closed=closed, method=method
        )
    mnk__ijh = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', hiws__pbj, mnk__ijh,
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
        fgihr__cfsiv = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        abpva__pmch = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{tcb__yehdq}'" if
                isinstance(tcb__yehdq, str) else f'{tcb__yehdq}' for
                tcb__yehdq in rolling.selection if tcb__yehdq != rolling.on))
        gwzzb__jjnae = wjo__zmzjv = ''
        if fname == 'apply':
            gwzzb__jjnae = 'func, raw, args, kwargs'
            wjo__zmzjv = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            gwzzb__jjnae = wjo__zmzjv = 'other, pairwise'
        if fname == 'cov':
            gwzzb__jjnae = wjo__zmzjv = 'other, pairwise, ddof'
        fkv__zgx = (
            f'lambda df, window, minp, center, {gwzzb__jjnae}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {abpva__pmch}){selection}.{fname}({wjo__zmzjv})'
            )
        fgihr__cfsiv += f"""  return rolling.obj.apply({fkv__zgx}, rolling.window, rolling.min_periods, rolling.center, {gwzzb__jjnae})
"""
        dekgx__dbbj = {}
        exec(fgihr__cfsiv, {'bodo': bodo}, dekgx__dbbj)
        impl = dekgx__dbbj['impl']
        return impl
    yqfn__jkgyh = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if yqfn__jkgyh else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if yqfn__jkgyh else rolling.obj_type.columns
        other_cols = None if yqfn__jkgyh else other.columns
        kab__asftn, xsq__tbte = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        kab__asftn, xsq__tbte, out_cols = _gen_df_rolling_out_data(rolling)
    kchv__dxdd = yqfn__jkgyh or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    kdqwy__jjv = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    kdqwy__jjv += '  df = rolling.obj\n'
    kdqwy__jjv += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if yqfn__jkgyh else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    qlew__igy = 'None'
    if yqfn__jkgyh:
        qlew__igy = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif kchv__dxdd:
        yjdw__icso = (set(out_cols) - set([rolling.on])).pop()
        qlew__igy = f"'{yjdw__icso}'" if isinstance(yjdw__icso, str) else str(
            yjdw__icso)
    kdqwy__jjv += f'  name = {qlew__igy}\n'
    kdqwy__jjv += '  window = rolling.window\n'
    kdqwy__jjv += '  center = rolling.center\n'
    kdqwy__jjv += '  minp = rolling.min_periods\n'
    kdqwy__jjv += f'  on_arr = {xsq__tbte}\n'
    if fname == 'apply':
        kdqwy__jjv += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        kdqwy__jjv += f"  func = '{fname}'\n"
        kdqwy__jjv += f'  index_arr = None\n'
        kdqwy__jjv += f'  raw = False\n'
    if kchv__dxdd:
        kdqwy__jjv += (
            f'  return bodo.hiframes.pd_series_ext.init_series({kab__asftn}, index, name)'
            )
        dekgx__dbbj = {}
        wpkh__poe = {'bodo': bodo}
        exec(kdqwy__jjv, wpkh__poe, dekgx__dbbj)
        impl = dekgx__dbbj['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(kdqwy__jjv, out_cols,
        kab__asftn)


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
        ayt__wvy = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(ayt__wvy)


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
    ckwq__bkc = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(ckwq__bkc) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    jfxvm__lcwjx = not isinstance(window_type, types.Integer)
    xsq__tbte = 'None'
    if jfxvm__lcwjx:
        xsq__tbte = 'bodo.utils.conversion.index_to_array(index)'
    fatp__uqo = 'on_arr, ' if jfxvm__lcwjx else ''
    kab__asftn = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {fatp__uqo}window, minp, center)'
            , xsq__tbte)
    for yjdw__icso in out_cols:
        if yjdw__icso in df_cols and yjdw__icso in other_cols:
            bgls__bnvel = df_cols.index(yjdw__icso)
            hbo__odc = other_cols.index(yjdw__icso)
            byoyg__kaoy = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {bgls__bnvel}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {hbo__odc}), {fatp__uqo}window, minp, center)'
                )
        else:
            byoyg__kaoy = 'np.full(len(df), np.nan)'
        kab__asftn.append(byoyg__kaoy)
    return ', '.join(kab__asftn), xsq__tbte


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    kjmn__mhc = {'pairwise': pairwise, 'ddof': ddof}
    djg__vxup = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        kjmn__mhc, djg__vxup, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    kjmn__mhc = {'ddof': ddof, 'pairwise': pairwise}
    djg__vxup = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        kjmn__mhc, djg__vxup, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, cyu__tkv = args
        if isinstance(rolling, RollingType):
            ckwq__bkc = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(cyu__tkv, (tuple, list)):
                if len(set(cyu__tkv).difference(set(ckwq__bkc))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(cyu__tkv).difference(set(ckwq__bkc))))
                selection = list(cyu__tkv)
            else:
                if cyu__tkv not in ckwq__bkc:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(cyu__tkv))
                selection = [cyu__tkv]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            pofbm__uwlix = RollingType(rolling.obj_type, rolling.
                window_type, rolling.on, tuple(selection), True, series_select)
            return signature(pofbm__uwlix, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        ckwq__bkc = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            ckwq__bkc = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            ckwq__bkc = rolling.obj_type.columns
        if attr in ckwq__bkc:
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
    mgrl__xxuwq = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    vizv__vwy = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in mgrl__xxuwq):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        odwpq__cjm = vizv__vwy[mgrl__xxuwq.index(get_literal_value(on))]
        if not isinstance(odwpq__cjm, types.Array
            ) or odwpq__cjm.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(vkwl__ini.dtype, (types.Boolean, types.Number)) for
        vkwl__ini in vizv__vwy):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
