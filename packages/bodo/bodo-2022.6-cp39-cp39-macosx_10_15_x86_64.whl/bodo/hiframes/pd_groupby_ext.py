"""Support for Pandas Groupby operations
"""
import operator
from enum import Enum
import numba
import numpy as np
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import NumericIndexType, RangeIndexType
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_table, delete_table_decref_arrays, get_groupby_labels, get_null_shuffle_info, get_shuffle_info, info_from_table, info_to_array, reverse_shuffle_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import get_call_expr_arg, get_const_func_output_type
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_index_data_arr_types, get_index_name_types, get_literal_value, get_overload_const_bool, get_overload_const_func, get_overload_const_list, get_overload_const_str, get_overload_constant_dict, get_udf_error_msg, get_udf_out_arr_type, is_dtype_nullable, is_literal_type, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_list, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, list_cumulative, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array
from bodo.utils.utils import dt_err, is_expr


class DataFrameGroupByType(types.Type):

    def __init__(self, df_type, keys, selection, as_index, dropna=True,
        explicit_select=False, series_select=False):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df_type,
            'pandas.groupby()')
        self.df_type = df_type
        self.keys = keys
        self.selection = selection
        self.as_index = as_index
        self.dropna = dropna
        self.explicit_select = explicit_select
        self.series_select = series_select
        super(DataFrameGroupByType, self).__init__(name=
            f'DataFrameGroupBy({df_type}, {keys}, {selection}, {as_index}, {dropna}, {explicit_select}, {series_select})'
            )

    def copy(self):
        return DataFrameGroupByType(self.df_type, self.keys, self.selection,
            self.as_index, self.dropna, self.explicit_select, self.
            series_select)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFrameGroupByType)
class GroupbyModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pvc__tshki = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, pvc__tshki)


make_attribute_wrapper(DataFrameGroupByType, 'obj', 'obj')


def validate_udf(func_name, func):
    if not isinstance(func, (types.functions.MakeFunctionLiteral, bodo.
        utils.typing.FunctionLiteral, types.Dispatcher, CPUDispatcher)):
        raise_bodo_error(
            f"Groupby.{func_name}: 'func' must be user defined function")


@intrinsic
def init_groupby(typingctx, obj_type, by_type, as_index_type=None,
    dropna_type=None):

    def codegen(context, builder, signature, args):
        rfrs__ewh = args[0]
        wdzf__udg = signature.return_type
        dioqx__glt = cgutils.create_struct_proxy(wdzf__udg)(context, builder)
        dioqx__glt.obj = rfrs__ewh
        context.nrt.incref(builder, signature.args[0], rfrs__ewh)
        return dioqx__glt._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for dow__lrk in keys:
        selection.remove(dow__lrk)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    wdzf__udg = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False)
    return wdzf__udg(obj_type, by_type, as_index_type, dropna_type), codegen


@lower_builtin('groupby.count', types.VarArg(types.Any))
@lower_builtin('groupby.size', types.VarArg(types.Any))
@lower_builtin('groupby.apply', types.VarArg(types.Any))
@lower_builtin('groupby.agg', types.VarArg(types.Any))
def lower_groupby_count_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


@infer
class StaticGetItemDataFrameGroupBy(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        grpby, oxuoj__srw = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(oxuoj__srw, (tuple, list)):
                if len(set(oxuoj__srw).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(oxuoj__srw).difference(set(grpby.
                        df_type.columns))))
                selection = oxuoj__srw
            else:
                if oxuoj__srw not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(oxuoj__srw))
                selection = oxuoj__srw,
                series_select = True
            jewts__mjfo = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True, series_select)
            return signature(jewts__mjfo, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, oxuoj__srw = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            oxuoj__srw):
            jewts__mjfo = StaticGetItemDataFrameGroupBy.generic(self, (
                grpby, get_literal_value(oxuoj__srw)), {}).return_type
            return signature(jewts__mjfo, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    arr_type = to_str_arr_if_dict_array(arr_type)
    rma__mcnng = arr_type == ArrayItemArrayType(string_array_type)
    etw__suiv = arr_type.dtype
    if isinstance(etw__suiv, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {etw__suiv} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(etw__suiv, (Decimal128Type,
        types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {etw__suiv} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(etw__suiv,
        (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(etw__suiv, (types.Integer, types.Float, types.Boolean)):
        if rma__mcnng or etw__suiv == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(etw__suiv, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not etw__suiv.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {etw__suiv} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(etw__suiv, types.Boolean) and func_name in {'cumsum',
        'sum', 'mean', 'std', 'var'}:
        return (None,
            f'groupby built-in functions {func_name} does not support boolean column'
            )
    if func_name in {'idxmin', 'idxmax'}:
        return dtype_to_array_type(get_index_data_arr_types(index_type)[0].
            dtype), 'ok'
    if func_name in {'count', 'nunique'}:
        return dtype_to_array_type(types.int64), 'ok'
    else:
        return arr_type, 'ok'


def get_pivot_output_dtype(arr_type, func_name, index_type=None):
    etw__suiv = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(etw__suiv, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(etw__suiv, types.Integer):
            return IntDtype(etw__suiv)
        return etw__suiv
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        fusse__qmrog = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{fusse__qmrog}'."
            )
    elif len(args) > len_args:
        raise BodoError(
            f'Groupby.{func_name}() takes {len_args + 1} positional argument but {len(args)} were given.'
            )


class ColumnType(Enum):
    KeyColumn = 0
    NumericalColumn = 1
    NonNumericalColumn = 2


def get_keys_not_as_index(grp, out_columns, out_data, out_column_type,
    multi_level_names=False):
    for dow__lrk in grp.keys:
        if multi_level_names:
            bptcb__hzbwo = dow__lrk, ''
        else:
            bptcb__hzbwo = dow__lrk
        uyf__swgs = grp.df_type.columns.index(dow__lrk)
        data = grp.df_type.data[uyf__swgs]
        out_columns.append(bptcb__hzbwo)
        out_data.append(data)
        out_column_type.append(ColumnType.KeyColumn.value)


def get_agg_typ(grp, args, func_name, typing_context, target_context, func=
    None, kws=None):
    index = RangeIndexType(types.none)
    out_data = []
    out_columns = []
    out_column_type = []
    if func_name == 'head':
        grp.as_index = True
    if not grp.as_index:
        get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
    elif func_name == 'head':
        if grp.df_type.index == index:
            index = NumericIndexType(types.int64, types.none)
        else:
            index = grp.df_type.index
    elif len(grp.keys) > 1:
        jav__kgb = tuple(grp.df_type.column_index[grp.keys[nibz__ssea]] for
            nibz__ssea in range(len(grp.keys)))
        luzx__yqy = tuple(grp.df_type.data[uyf__swgs] for uyf__swgs in jav__kgb
            )
        index = MultiIndexType(luzx__yqy, tuple(types.StringLiteral(
            dow__lrk) for dow__lrk in grp.keys))
    else:
        uyf__swgs = grp.df_type.column_index[grp.keys[0]]
        nxxm__estfv = grp.df_type.data[uyf__swgs]
        index = bodo.hiframes.pd_index_ext.array_type_to_index(nxxm__estfv,
            types.StringLiteral(grp.keys[0]))
    tit__nhogh = {}
    huz__dawcw = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        tit__nhogh[None, 'size'] = 'size'
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for jbgg__qsoi in columns:
            uyf__swgs = grp.df_type.column_index[jbgg__qsoi]
            data = grp.df_type.data[uyf__swgs]
            data = to_str_arr_if_dict_array(data)
            ybxa__utzdu = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                ybxa__utzdu = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    lntr__wvdmd = SeriesType(data.dtype, data, None,
                        string_type)
                    ncfh__fmt = get_const_func_output_type(func, (
                        lntr__wvdmd,), {}, typing_context, target_context)
                    if ncfh__fmt != ArrayItemArrayType(string_array_type):
                        ncfh__fmt = dtype_to_array_type(ncfh__fmt)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=jbgg__qsoi, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    vsm__lsy = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    xsahb__wqlag = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    nax__wbbz = dict(numeric_only=vsm__lsy, min_count=
                        xsahb__wqlag)
                    kbt__mocg = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        nax__wbbz, kbt__mocg, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    vsm__lsy = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    xsahb__wqlag = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    nax__wbbz = dict(numeric_only=vsm__lsy, min_count=
                        xsahb__wqlag)
                    kbt__mocg = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        nax__wbbz, kbt__mocg, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    vsm__lsy = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    nax__wbbz = dict(numeric_only=vsm__lsy)
                    kbt__mocg = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        nax__wbbz, kbt__mocg, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    ijln__lvosc = args[0] if len(args) > 0 else kws.pop('axis',
                        0)
                    mfdjr__kaz = args[1] if len(args) > 1 else kws.pop('skipna'
                        , True)
                    nax__wbbz = dict(axis=ijln__lvosc, skipna=mfdjr__kaz)
                    kbt__mocg = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        nax__wbbz, kbt__mocg, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    gvx__mzz = args[0] if len(args) > 0 else kws.pop('ddof', 1)
                    nax__wbbz = dict(ddof=gvx__mzz)
                    kbt__mocg = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        nax__wbbz, kbt__mocg, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                ncfh__fmt, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                hncni__ncd = to_str_arr_if_dict_array(ncfh__fmt)
                out_data.append(hncni__ncd)
                out_columns.append(jbgg__qsoi)
                if func_name == 'agg':
                    joda__fvan = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    tit__nhogh[jbgg__qsoi, joda__fvan] = jbgg__qsoi
                else:
                    tit__nhogh[jbgg__qsoi, func_name] = jbgg__qsoi
                out_column_type.append(ybxa__utzdu)
            else:
                huz__dawcw.append(err_msg)
    if func_name == 'sum':
        lhs__yhxyv = any([(kjmad__wpqzg == ColumnType.NumericalColumn.value
            ) for kjmad__wpqzg in out_column_type])
        if lhs__yhxyv:
            out_data = [kjmad__wpqzg for kjmad__wpqzg, eaz__jzvj in zip(
                out_data, out_column_type) if eaz__jzvj != ColumnType.
                NonNumericalColumn.value]
            out_columns = [kjmad__wpqzg for kjmad__wpqzg, eaz__jzvj in zip(
                out_columns, out_column_type) if eaz__jzvj != ColumnType.
                NonNumericalColumn.value]
            tit__nhogh = {}
            for jbgg__qsoi in out_columns:
                if grp.as_index is False and jbgg__qsoi in grp.keys:
                    continue
                tit__nhogh[jbgg__qsoi, func_name] = jbgg__qsoi
    wuky__plsk = len(huz__dawcw)
    if len(out_data) == 0:
        if wuky__plsk == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(wuky__plsk, ' was' if wuky__plsk == 1 else 's were',
                ','.join(huz__dawcw)))
    xujri__catmk = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index):
        if isinstance(out_data[0], IntegerArrayType):
            rfw__xqx = IntDtype(out_data[0].dtype)
        else:
            rfw__xqx = out_data[0].dtype
        zcrrj__ajfl = (types.none if func_name == 'size' else types.
            StringLiteral(grp.selection[0]))
        xujri__catmk = SeriesType(rfw__xqx, index=index, name_typ=zcrrj__ajfl)
    return signature(xujri__catmk, *args), tit__nhogh


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    mnxy__jjoc = True
    if isinstance(f_val, str):
        mnxy__jjoc = False
        qsgh__grp = f_val
    elif is_overload_constant_str(f_val):
        mnxy__jjoc = False
        qsgh__grp = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        mnxy__jjoc = False
        qsgh__grp = bodo.utils.typing.get_builtin_function_name(f_val)
    if not mnxy__jjoc:
        if qsgh__grp not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {qsgh__grp}')
        jewts__mjfo = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(jewts__mjfo, (), qsgh__grp, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            qqthc__koyi = types.functions.MakeFunctionLiteral(f_val)
        else:
            qqthc__koyi = f_val
        validate_udf('agg', qqthc__koyi)
        func = get_overload_const_func(qqthc__koyi, None)
        lwwzy__bko = func.code if hasattr(func, 'code') else func.__code__
        qsgh__grp = lwwzy__bko.co_name
        jewts__mjfo = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(jewts__mjfo, (), 'agg', typing_context,
            target_context, qqthc__koyi)[0].return_type
    return qsgh__grp, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    olqc__sxfw = kws and all(isinstance(vtlue__gzwsy, types.Tuple) and len(
        vtlue__gzwsy) == 2 for vtlue__gzwsy in kws.values())
    if is_overload_none(func) and not olqc__sxfw:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not olqc__sxfw:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    mrfg__gxt = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if olqc__sxfw or is_overload_constant_dict(func):
        if olqc__sxfw:
            ypy__hhkn = [get_literal_value(nhiy__fyvqu) for nhiy__fyvqu,
                botv__vqh in kws.values()]
            xfojx__cqdum = [get_literal_value(ryca__lrzy) for botv__vqh,
                ryca__lrzy in kws.values()]
        else:
            kyfx__jhf = get_overload_constant_dict(func)
            ypy__hhkn = tuple(kyfx__jhf.keys())
            xfojx__cqdum = tuple(kyfx__jhf.values())
        if 'head' in xfojx__cqdum:
            raise BodoError(
                'Groupby.agg()/aggregate(): head cannot be mixed with other groupby operations.'
                )
        if any(jbgg__qsoi not in grp.selection and jbgg__qsoi not in grp.
            keys for jbgg__qsoi in ypy__hhkn):
            raise_bodo_error(
                f'Selected column names {ypy__hhkn} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            xfojx__cqdum)
        if olqc__sxfw and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        tit__nhogh = {}
        out_columns = []
        out_data = []
        out_column_type = []
        libji__ivtkn = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for jpwa__msq, f_val in zip(ypy__hhkn, xfojx__cqdum):
            if isinstance(f_val, (tuple, list)):
                tyig__daxtc = 0
                for qqthc__koyi in f_val:
                    qsgh__grp, out_tp = get_agg_funcname_and_outtyp(grp,
                        jpwa__msq, qqthc__koyi, typing_context, target_context)
                    mrfg__gxt = qsgh__grp in list_cumulative
                    if qsgh__grp == '<lambda>' and len(f_val) > 1:
                        qsgh__grp = '<lambda_' + str(tyig__daxtc) + '>'
                        tyig__daxtc += 1
                    out_columns.append((jpwa__msq, qsgh__grp))
                    tit__nhogh[jpwa__msq, qsgh__grp] = jpwa__msq, qsgh__grp
                    _append_out_type(grp, out_data, out_tp)
            else:
                qsgh__grp, out_tp = get_agg_funcname_and_outtyp(grp,
                    jpwa__msq, f_val, typing_context, target_context)
                mrfg__gxt = qsgh__grp in list_cumulative
                if multi_level_names:
                    out_columns.append((jpwa__msq, qsgh__grp))
                    tit__nhogh[jpwa__msq, qsgh__grp] = jpwa__msq, qsgh__grp
                elif not olqc__sxfw:
                    out_columns.append(jpwa__msq)
                    tit__nhogh[jpwa__msq, qsgh__grp] = jpwa__msq
                elif olqc__sxfw:
                    libji__ivtkn.append(qsgh__grp)
                _append_out_type(grp, out_data, out_tp)
        if olqc__sxfw:
            for nibz__ssea, hemvg__zcsou in enumerate(kws.keys()):
                out_columns.append(hemvg__zcsou)
                tit__nhogh[ypy__hhkn[nibz__ssea], libji__ivtkn[nibz__ssea]
                    ] = hemvg__zcsou
        if mrfg__gxt:
            index = grp.df_type.index
        else:
            index = out_tp.index
        xujri__catmk = DataFrameType(tuple(out_data), index, tuple(out_columns)
            )
        return signature(xujri__catmk, *args), tit__nhogh
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            uuqqb__pkvpr = get_overload_const_list(func)
        else:
            uuqqb__pkvpr = func.types
        if len(uuqqb__pkvpr) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        tyig__daxtc = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        tit__nhogh = {}
        evg__asfjc = grp.selection[0]
        for f_val in uuqqb__pkvpr:
            qsgh__grp, out_tp = get_agg_funcname_and_outtyp(grp, evg__asfjc,
                f_val, typing_context, target_context)
            mrfg__gxt = qsgh__grp in list_cumulative
            if qsgh__grp == '<lambda>' and len(uuqqb__pkvpr) > 1:
                qsgh__grp = '<lambda_' + str(tyig__daxtc) + '>'
                tyig__daxtc += 1
            out_columns.append(qsgh__grp)
            tit__nhogh[evg__asfjc, qsgh__grp] = qsgh__grp
            _append_out_type(grp, out_data, out_tp)
        if mrfg__gxt:
            index = grp.df_type.index
        else:
            index = out_tp.index
        xujri__catmk = DataFrameType(tuple(out_data), index, tuple(out_columns)
            )
        return signature(xujri__catmk, *args), tit__nhogh
    qsgh__grp = ''
    if types.unliteral(func) == types.unicode_type:
        qsgh__grp = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        qsgh__grp = bodo.utils.typing.get_builtin_function_name(func)
    if qsgh__grp:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, qsgh__grp, typing_context, kws)
    validate_udf('agg', func)
    return get_agg_typ(grp, args, 'agg', typing_context, target_context, func)


def resolve_transformative(grp, args, kws, msg, name_operation):
    index = grp.df_type.index
    out_columns = []
    out_data = []
    if name_operation in list_cumulative:
        kws = dict(kws) if kws else {}
        ijln__lvosc = args[0] if len(args) > 0 else kws.pop('axis', 0)
        vsm__lsy = args[1] if len(args) > 1 else kws.pop('numeric_only', False)
        mfdjr__kaz = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        nax__wbbz = dict(axis=ijln__lvosc, numeric_only=vsm__lsy)
        kbt__mocg = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', nax__wbbz,
            kbt__mocg, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        ckf__evfs = args[0] if len(args) > 0 else kws.pop('periods', 1)
        sbog__nacc = args[1] if len(args) > 1 else kws.pop('freq', None)
        ijln__lvosc = args[2] if len(args) > 2 else kws.pop('axis', 0)
        zpv__zptnm = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        nax__wbbz = dict(freq=sbog__nacc, axis=ijln__lvosc, fill_value=
            zpv__zptnm)
        kbt__mocg = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', nax__wbbz,
            kbt__mocg, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        luja__zjp = args[0] if len(args) > 0 else kws.pop('func', None)
        gmmq__vaw = kws.pop('engine', None)
        lgvn__wtd = kws.pop('engine_kwargs', None)
        nax__wbbz = dict(engine=gmmq__vaw, engine_kwargs=lgvn__wtd)
        kbt__mocg = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', nax__wbbz, kbt__mocg,
            package_name='pandas', module_name='GroupBy')
    tit__nhogh = {}
    for jbgg__qsoi in grp.selection:
        out_columns.append(jbgg__qsoi)
        tit__nhogh[jbgg__qsoi, name_operation] = jbgg__qsoi
        uyf__swgs = grp.df_type.columns.index(jbgg__qsoi)
        data = grp.df_type.data[uyf__swgs]
        data = to_str_arr_if_dict_array(data)
        if name_operation == 'cumprod':
            if not isinstance(data.dtype, (types.Integer, types.Float)):
                raise BodoError(msg)
        if name_operation == 'cumsum':
            if data.dtype != types.unicode_type and data != ArrayItemArrayType(
                string_array_type) and not isinstance(data.dtype, (types.
                Integer, types.Float)):
                raise BodoError(msg)
        if name_operation in ('cummin', 'cummax'):
            if not isinstance(data.dtype, types.Integer
                ) and not is_dtype_nullable(data.dtype):
                raise BodoError(msg)
        if name_operation == 'shift':
            if isinstance(data, (TupleArrayType, ArrayItemArrayType)):
                raise BodoError(msg)
            if isinstance(data.dtype, bodo.hiframes.datetime_timedelta_ext.
                DatetimeTimeDeltaType):
                raise BodoError(
                    f"""column type of {data.dtype} is not supported in groupby built-in function shift.
{dt_err}"""
                    )
        if name_operation == 'transform':
            ncfh__fmt, err_msg = get_groupby_output_dtype(data,
                get_literal_value(luja__zjp), grp.df_type.index)
            if err_msg == 'ok':
                data = ncfh__fmt
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    xujri__catmk = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        xujri__catmk = SeriesType(out_data[0].dtype, data=out_data[0],
            index=index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(xujri__catmk, *args), tit__nhogh


def resolve_gb(grp, args, kws, func_name, typing_context, target_context,
    err_msg=''):
    if func_name in set(list_cumulative) | {'shift', 'transform'}:
        return resolve_transformative(grp, args, kws, err_msg, func_name)
    elif func_name in {'agg', 'aggregate'}:
        return resolve_agg(grp, args, kws, typing_context, target_context)
    else:
        return get_agg_typ(grp, args, func_name, typing_context,
            target_context, kws=kws)


@infer_getattr
class DataframeGroupByAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameGroupByType
    _attr_set = None

    @bound_function('groupby.agg', no_unliteral=True)
    def resolve_agg(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.aggregate', no_unliteral=True)
    def resolve_aggregate(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.sum', no_unliteral=True)
    def resolve_sum(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'sum', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.count', no_unliteral=True)
    def resolve_count(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'count', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.nunique', no_unliteral=True)
    def resolve_nunique(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'nunique', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.median', no_unliteral=True)
    def resolve_median(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'median', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.mean', no_unliteral=True)
    def resolve_mean(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'mean', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.min', no_unliteral=True)
    def resolve_min(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'min', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.max', no_unliteral=True)
    def resolve_max(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'max', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.prod', no_unliteral=True)
    def resolve_prod(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'prod', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.var', no_unliteral=True)
    def resolve_var(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'var', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.std', no_unliteral=True)
    def resolve_std(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'std', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.first', no_unliteral=True)
    def resolve_first(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'first', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.last', no_unliteral=True)
    def resolve_last(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'last', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmin', no_unliteral=True)
    def resolve_idxmin(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmin', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmax', no_unliteral=True)
    def resolve_idxmax(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmax', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.size', no_unliteral=True)
    def resolve_size(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'size', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.cumsum', no_unliteral=True)
    def resolve_cumsum(self, grp, args, kws):
        msg = (
            'Groupby.cumsum() only supports columns of types integer, float, string or liststring'
            )
        return resolve_gb(grp, args, kws, 'cumsum', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cumprod', no_unliteral=True)
    def resolve_cumprod(self, grp, args, kws):
        msg = (
            'Groupby.cumprod() only supports columns of types integer and float'
            )
        return resolve_gb(grp, args, kws, 'cumprod', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummin', no_unliteral=True)
    def resolve_cummin(self, grp, args, kws):
        msg = (
            'Groupby.cummin() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummin', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummax', no_unliteral=True)
    def resolve_cummax(self, grp, args, kws):
        msg = (
            'Groupby.cummax() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummax', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.shift', no_unliteral=True)
    def resolve_shift(self, grp, args, kws):
        msg = (
            'Column type of list/tuple is not supported in groupby built-in function shift'
            )
        return resolve_gb(grp, args, kws, 'shift', self.context, numba.core
            .registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.pipe', no_unliteral=True)
    def resolve_pipe(self, grp, args, kws):
        return resolve_obj_pipe(self, grp, args, kws, 'GroupBy')

    @bound_function('groupby.transform', no_unliteral=True)
    def resolve_transform(self, grp, args, kws):
        msg = (
            'Groupby.transform() only supports sum, count, min, max, mean, and std operations'
            )
        return resolve_gb(grp, args, kws, 'transform', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.head', no_unliteral=True)
    def resolve_head(self, grp, args, kws):
        msg = 'Unsupported Gropupby head operation.\n'
        return resolve_gb(grp, args, kws, 'head', self.context, numba.core.
            registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.apply', no_unliteral=True)
    def resolve_apply(self, grp, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws.pop('func', None)
        f_args = tuple(args[1:]) if len(args) > 0 else ()
        ycn__cnvna = _get_groupby_apply_udf_out_type(func, grp, f_args, kws,
            self.context, numba.core.registry.cpu_target.target_context)
        uvwg__yovfu = isinstance(ycn__cnvna, (SeriesType,
            HeterogeneousSeriesType)
            ) and ycn__cnvna.const_info is not None or not isinstance(
            ycn__cnvna, (SeriesType, DataFrameType))
        if uvwg__yovfu:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                yuora__gms = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                jav__kgb = tuple(grp.df_type.columns.index(grp.keys[
                    nibz__ssea]) for nibz__ssea in range(len(grp.keys)))
                luzx__yqy = tuple(grp.df_type.data[uyf__swgs] for uyf__swgs in
                    jav__kgb)
                yuora__gms = MultiIndexType(luzx__yqy, tuple(types.literal(
                    dow__lrk) for dow__lrk in grp.keys))
            else:
                uyf__swgs = grp.df_type.columns.index(grp.keys[0])
                nxxm__estfv = grp.df_type.data[uyf__swgs]
                yuora__gms = bodo.hiframes.pd_index_ext.array_type_to_index(
                    nxxm__estfv, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            zxj__yesf = tuple(grp.df_type.data[grp.df_type.columns.index(
                jbgg__qsoi)] for jbgg__qsoi in grp.keys)
            xjdgq__gpcbw = tuple(types.literal(vtlue__gzwsy) for
                vtlue__gzwsy in grp.keys) + get_index_name_types(ycn__cnvna
                .index)
            if not grp.as_index:
                zxj__yesf = types.Array(types.int64, 1, 'C'),
                xjdgq__gpcbw = (types.none,) + get_index_name_types(ycn__cnvna
                    .index)
            yuora__gms = MultiIndexType(zxj__yesf +
                get_index_data_arr_types(ycn__cnvna.index), xjdgq__gpcbw)
        if uvwg__yovfu:
            if isinstance(ycn__cnvna, HeterogeneousSeriesType):
                botv__vqh, zua__yfzje = ycn__cnvna.const_info
                if isinstance(ycn__cnvna.data, bodo.libs.nullable_tuple_ext
                    .NullableTupleType):
                    inov__yppd = ycn__cnvna.data.tuple_typ.types
                elif isinstance(ycn__cnvna.data, types.Tuple):
                    inov__yppd = ycn__cnvna.data.types
                fzeh__wagup = tuple(to_nullable_type(dtype_to_array_type(
                    aiwc__rcx)) for aiwc__rcx in inov__yppd)
                bwp__qdwts = DataFrameType(out_data + fzeh__wagup,
                    yuora__gms, out_columns + zua__yfzje)
            elif isinstance(ycn__cnvna, SeriesType):
                doosg__xyg, zua__yfzje = ycn__cnvna.const_info
                fzeh__wagup = tuple(to_nullable_type(dtype_to_array_type(
                    ycn__cnvna.dtype)) for botv__vqh in range(doosg__xyg))
                bwp__qdwts = DataFrameType(out_data + fzeh__wagup,
                    yuora__gms, out_columns + zua__yfzje)
            else:
                nnc__uivr = get_udf_out_arr_type(ycn__cnvna)
                if not grp.as_index:
                    bwp__qdwts = DataFrameType(out_data + (nnc__uivr,),
                        yuora__gms, out_columns + ('',))
                else:
                    bwp__qdwts = SeriesType(nnc__uivr.dtype, nnc__uivr,
                        yuora__gms, None)
        elif isinstance(ycn__cnvna, SeriesType):
            bwp__qdwts = SeriesType(ycn__cnvna.dtype, ycn__cnvna.data,
                yuora__gms, ycn__cnvna.name_typ)
        else:
            bwp__qdwts = DataFrameType(ycn__cnvna.data, yuora__gms,
                ycn__cnvna.columns)
        fnl__csgc = gen_apply_pysig(len(f_args), kws.keys())
        bfyf__oicc = (func, *f_args) + tuple(kws.values())
        return signature(bwp__qdwts, *bfyf__oicc).replace(pysig=fnl__csgc)

    def generic_resolve(self, grpby, attr):
        if self._is_existing_attr(attr):
            return
        if attr not in grpby.df_type.columns:
            raise_bodo_error(
                f'groupby: invalid attribute {attr} (column not found in dataframe or unsupported function)'
                )
        return DataFrameGroupByType(grpby.df_type, grpby.keys, (attr,),
            grpby.as_index, grpby.dropna, True, True)


def _get_groupby_apply_udf_out_type(func, grp, f_args, kws, typing_context,
    target_context):
    capuc__mmv = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            jpwa__msq = grp.selection[0]
            nnc__uivr = capuc__mmv.data[capuc__mmv.columns.index(jpwa__msq)]
            nnc__uivr = to_str_arr_if_dict_array(nnc__uivr)
            bwbw__uqmwx = SeriesType(nnc__uivr.dtype, nnc__uivr, capuc__mmv
                .index, types.literal(jpwa__msq))
        else:
            dlo__qse = tuple(capuc__mmv.data[capuc__mmv.columns.index(
                jbgg__qsoi)] for jbgg__qsoi in grp.selection)
            dlo__qse = tuple(to_str_arr_if_dict_array(aiwc__rcx) for
                aiwc__rcx in dlo__qse)
            bwbw__uqmwx = DataFrameType(dlo__qse, capuc__mmv.index, tuple(
                grp.selection))
    else:
        bwbw__uqmwx = capuc__mmv
    toa__xugy = bwbw__uqmwx,
    toa__xugy += tuple(f_args)
    try:
        ycn__cnvna = get_const_func_output_type(func, toa__xugy, kws,
            typing_context, target_context)
    except Exception as xeep__xwgi:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', xeep__xwgi),
            getattr(xeep__xwgi, 'loc', None))
    return ycn__cnvna


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    toa__xugy = (grp,) + f_args
    try:
        ycn__cnvna = get_const_func_output_type(func, toa__xugy, kws, self.
            context, numba.core.registry.cpu_target.target_context, False)
    except Exception as xeep__xwgi:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', xeep__xwgi
            ), getattr(xeep__xwgi, 'loc', None))
    fnl__csgc = gen_apply_pysig(len(f_args), kws.keys())
    bfyf__oicc = (func, *f_args) + tuple(kws.values())
    return signature(ycn__cnvna, *bfyf__oicc).replace(pysig=fnl__csgc)


def gen_apply_pysig(n_args, kws):
    year__elk = ', '.join(f'arg{nibz__ssea}' for nibz__ssea in range(n_args))
    year__elk = year__elk + ', ' if year__elk else ''
    nyyko__eryl = ', '.join(f"{ffyr__umie} = ''" for ffyr__umie in kws)
    qdolm__bevmx = f'def apply_stub(func, {year__elk}{nyyko__eryl}):\n'
    qdolm__bevmx += '    pass\n'
    cqlp__nxkgb = {}
    exec(qdolm__bevmx, {}, cqlp__nxkgb)
    ejo__abtfd = cqlp__nxkgb['apply_stub']
    return numba.core.utils.pysignature(ejo__abtfd)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        omn__isgg = types.Array(types.int64, 1, 'C')
        tspjo__dpp = _pivot_values.meta
        rbqgu__upr = len(tspjo__dpp)
        vusd__rbb = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        hdrdx__ebl = DataFrameType((omn__isgg,) * rbqgu__upr, vusd__rbb,
            tuple(tspjo__dpp))
        return signature(hdrdx__ebl, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    qdolm__bevmx = 'def impl(keys, dropna, _is_parallel):\n'
    qdolm__bevmx += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    qdolm__bevmx += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{nibz__ssea}])' for nibz__ssea in range(len(
        keys.types))))
    qdolm__bevmx += '    table = arr_info_list_to_table(info_list)\n'
    qdolm__bevmx += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    qdolm__bevmx += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    qdolm__bevmx += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    qdolm__bevmx += '    delete_table_decref_arrays(table)\n'
    qdolm__bevmx += '    ev.finalize()\n'
    qdolm__bevmx += '    return sort_idx, group_labels, ngroups\n'
    cqlp__nxkgb = {}
    exec(qdolm__bevmx, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, cqlp__nxkgb)
    nxlu__rhxlm = cqlp__nxkgb['impl']
    return nxlu__rhxlm


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    iaq__zeln = len(labels)
    ndhra__emqn = np.zeros(ngroups, dtype=np.int64)
    ycegk__wuxpf = np.zeros(ngroups, dtype=np.int64)
    eodr__taahd = 0
    dua__dxpez = 0
    for nibz__ssea in range(iaq__zeln):
        okvo__wvxn = labels[nibz__ssea]
        if okvo__wvxn < 0:
            eodr__taahd += 1
        else:
            dua__dxpez += 1
            if nibz__ssea == iaq__zeln - 1 or okvo__wvxn != labels[
                nibz__ssea + 1]:
                ndhra__emqn[okvo__wvxn] = eodr__taahd
                ycegk__wuxpf[okvo__wvxn] = eodr__taahd + dua__dxpez
                eodr__taahd += dua__dxpez
                dua__dxpez = 0
    return ndhra__emqn, ycegk__wuxpf


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    nxlu__rhxlm, botv__vqh = gen_shuffle_dataframe(df, keys, _is_parallel)
    return nxlu__rhxlm


def gen_shuffle_dataframe(df, keys, _is_parallel):
    doosg__xyg = len(df.columns)
    tmqo__anmpx = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    qdolm__bevmx = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        qdolm__bevmx += '  return df, keys, get_null_shuffle_info()\n'
        cqlp__nxkgb = {}
        exec(qdolm__bevmx, {'get_null_shuffle_info': get_null_shuffle_info},
            cqlp__nxkgb)
        nxlu__rhxlm = cqlp__nxkgb['impl']
        return nxlu__rhxlm
    for nibz__ssea in range(doosg__xyg):
        qdolm__bevmx += f"""  in_arr{nibz__ssea} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {nibz__ssea})
"""
    qdolm__bevmx += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    qdolm__bevmx += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{nibz__ssea}])' for nibz__ssea in range(
        tmqo__anmpx)), ', '.join(f'array_to_info(in_arr{nibz__ssea})' for
        nibz__ssea in range(doosg__xyg)), 'array_to_info(in_index_arr)')
    qdolm__bevmx += '  table = arr_info_list_to_table(info_list)\n'
    qdolm__bevmx += (
        f'  out_table = shuffle_table(table, {tmqo__anmpx}, _is_parallel, 1)\n'
        )
    for nibz__ssea in range(tmqo__anmpx):
        qdolm__bevmx += f"""  out_key{nibz__ssea} = info_to_array(info_from_table(out_table, {nibz__ssea}), keys{nibz__ssea}_typ)
"""
    for nibz__ssea in range(doosg__xyg):
        qdolm__bevmx += f"""  out_arr{nibz__ssea} = info_to_array(info_from_table(out_table, {nibz__ssea + tmqo__anmpx}), in_arr{nibz__ssea}_typ)
"""
    qdolm__bevmx += f"""  out_arr_index = info_to_array(info_from_table(out_table, {tmqo__anmpx + doosg__xyg}), ind_arr_typ)
"""
    qdolm__bevmx += '  shuffle_info = get_shuffle_info(out_table)\n'
    qdolm__bevmx += '  delete_table(out_table)\n'
    qdolm__bevmx += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{nibz__ssea}' for nibz__ssea in range(
        doosg__xyg))
    qdolm__bevmx += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    qdolm__bevmx += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    qdolm__bevmx += '  return out_df, ({},), shuffle_info\n'.format(', '.
        join(f'out_key{nibz__ssea}' for nibz__ssea in range(tmqo__anmpx)))
    duczu__gise = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    duczu__gise.update({f'keys{nibz__ssea}_typ': keys.types[nibz__ssea] for
        nibz__ssea in range(tmqo__anmpx)})
    duczu__gise.update({f'in_arr{nibz__ssea}_typ': df.data[nibz__ssea] for
        nibz__ssea in range(doosg__xyg)})
    cqlp__nxkgb = {}
    exec(qdolm__bevmx, duczu__gise, cqlp__nxkgb)
    nxlu__rhxlm = cqlp__nxkgb['impl']
    return nxlu__rhxlm, duczu__gise


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        qrv__uwv = len(data.array_types)
        qdolm__bevmx = 'def impl(data, shuffle_info):\n'
        qdolm__bevmx += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{nibz__ssea}])' for nibz__ssea in
            range(qrv__uwv)))
        qdolm__bevmx += '  table = arr_info_list_to_table(info_list)\n'
        qdolm__bevmx += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for nibz__ssea in range(qrv__uwv):
            qdolm__bevmx += f"""  out_arr{nibz__ssea} = info_to_array(info_from_table(out_table, {nibz__ssea}), data._data[{nibz__ssea}])
"""
        qdolm__bevmx += '  delete_table(out_table)\n'
        qdolm__bevmx += '  delete_table(table)\n'
        qdolm__bevmx += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{nibz__ssea}' for nibz__ssea in range
            (qrv__uwv))))
        cqlp__nxkgb = {}
        exec(qdolm__bevmx, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, cqlp__nxkgb)
        nxlu__rhxlm = cqlp__nxkgb['impl']
        return nxlu__rhxlm
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            gnhjt__ius = bodo.utils.conversion.index_to_array(data)
            hncni__ncd = reverse_shuffle(gnhjt__ius, shuffle_info)
            return bodo.utils.conversion.index_from_array(hncni__ncd)
        return impl_index

    def impl_arr(data, shuffle_info):
        gupbg__ftpy = [array_to_info(data)]
        vqb__mnd = arr_info_list_to_table(gupbg__ftpy)
        qjytj__ssqtv = reverse_shuffle_table(vqb__mnd, shuffle_info)
        hncni__ncd = info_to_array(info_from_table(qjytj__ssqtv, 0), data)
        delete_table(qjytj__ssqtv)
        delete_table(vqb__mnd)
        return hncni__ncd
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    nax__wbbz = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna)
    kbt__mocg = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', nax__wbbz, kbt__mocg,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    tqtjc__lysq = get_overload_const_bool(ascending)
    pfto__tgkpu = grp.selection[0]
    qdolm__bevmx = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    lpyz__jcd = (
        f"lambda S: S.value_counts(ascending={tqtjc__lysq}, _index_name='{pfto__tgkpu}')"
        )
    qdolm__bevmx += f'    return grp.apply({lpyz__jcd})\n'
    cqlp__nxkgb = {}
    exec(qdolm__bevmx, {'bodo': bodo}, cqlp__nxkgb)
    nxlu__rhxlm = cqlp__nxkgb['impl']
    return nxlu__rhxlm


groupby_unsupported_attr = {'groups', 'indices'}
groupby_unsupported = {'__iter__', 'get_group', 'all', 'any', 'bfill',
    'backfill', 'cumcount', 'cummax', 'cummin', 'cumprod', 'ffill',
    'ngroup', 'nth', 'ohlc', 'pad', 'rank', 'pct_change', 'sem', 'tail',
    'corr', 'cov', 'describe', 'diff', 'fillna', 'filter', 'hist', 'mad',
    'plot', 'quantile', 'resample', 'sample', 'skew', 'take', 'tshift'}
series_only_unsupported_attrs = {'is_monotonic_increasing',
    'is_monotonic_decreasing'}
series_only_unsupported = {'nlargest', 'nsmallest', 'unique'}
dataframe_only_unsupported = {'corrwith', 'boxplot'}


def _install_groupby_unsupported():
    for dsf__kjlp in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, dsf__kjlp, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{dsf__kjlp}'))
    for dsf__kjlp in groupby_unsupported:
        overload_method(DataFrameGroupByType, dsf__kjlp, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{dsf__kjlp}'))
    for dsf__kjlp in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, dsf__kjlp, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{dsf__kjlp}'))
    for dsf__kjlp in series_only_unsupported:
        overload_method(DataFrameGroupByType, dsf__kjlp, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{dsf__kjlp}'))
    for dsf__kjlp in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, dsf__kjlp, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{dsf__kjlp}'))


_install_groupby_unsupported()
