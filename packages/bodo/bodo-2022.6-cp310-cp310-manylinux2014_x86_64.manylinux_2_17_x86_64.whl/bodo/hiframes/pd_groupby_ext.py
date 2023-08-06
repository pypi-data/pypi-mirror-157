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
        cfcxb__tkoze = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, cfcxb__tkoze)


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
        vyx__ohh = args[0]
        berpd__ins = signature.return_type
        qdxgj__lyrqe = cgutils.create_struct_proxy(berpd__ins)(context, builder
            )
        qdxgj__lyrqe.obj = vyx__ohh
        context.nrt.incref(builder, signature.args[0], vyx__ohh)
        return qdxgj__lyrqe._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for lmgfw__xcl in keys:
        selection.remove(lmgfw__xcl)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    berpd__ins = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False)
    return berpd__ins(obj_type, by_type, as_index_type, dropna_type), codegen


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
        grpby, jyrr__lhr = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(jyrr__lhr, (tuple, list)):
                if len(set(jyrr__lhr).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(jyrr__lhr).difference(set(grpby.df_type
                        .columns))))
                selection = jyrr__lhr
            else:
                if jyrr__lhr not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(jyrr__lhr))
                selection = jyrr__lhr,
                series_select = True
            dqsxg__ofx = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True, series_select)
            return signature(dqsxg__ofx, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, jyrr__lhr = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            jyrr__lhr):
            dqsxg__ofx = StaticGetItemDataFrameGroupBy.generic(self, (grpby,
                get_literal_value(jyrr__lhr)), {}).return_type
            return signature(dqsxg__ofx, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    arr_type = to_str_arr_if_dict_array(arr_type)
    oqwg__cas = arr_type == ArrayItemArrayType(string_array_type)
    dgcis__yrgbt = arr_type.dtype
    if isinstance(dgcis__yrgbt, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {dgcis__yrgbt} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(dgcis__yrgbt, (
        Decimal128Type, types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {dgcis__yrgbt} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(
        dgcis__yrgbt, (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(dgcis__yrgbt, (types.Integer, types.Float, types.Boolean)
        ):
        if oqwg__cas or dgcis__yrgbt == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(dgcis__yrgbt, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not dgcis__yrgbt.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {dgcis__yrgbt} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(dgcis__yrgbt, types.Boolean) and func_name in {'cumsum',
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
    dgcis__yrgbt = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(dgcis__yrgbt, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(dgcis__yrgbt, types.Integer):
            return IntDtype(dgcis__yrgbt)
        return dgcis__yrgbt
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        uvw__sexd = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{uvw__sexd}'."
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
    for lmgfw__xcl in grp.keys:
        if multi_level_names:
            fbvis__axzoj = lmgfw__xcl, ''
        else:
            fbvis__axzoj = lmgfw__xcl
        fzrh__muti = grp.df_type.columns.index(lmgfw__xcl)
        data = grp.df_type.data[fzrh__muti]
        out_columns.append(fbvis__axzoj)
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
        qac__agpwi = tuple(grp.df_type.column_index[grp.keys[tuhhv__rjtu]] for
            tuhhv__rjtu in range(len(grp.keys)))
        lefl__zmjqw = tuple(grp.df_type.data[fzrh__muti] for fzrh__muti in
            qac__agpwi)
        index = MultiIndexType(lefl__zmjqw, tuple(types.StringLiteral(
            lmgfw__xcl) for lmgfw__xcl in grp.keys))
    else:
        fzrh__muti = grp.df_type.column_index[grp.keys[0]]
        cfis__cbm = grp.df_type.data[fzrh__muti]
        index = bodo.hiframes.pd_index_ext.array_type_to_index(cfis__cbm,
            types.StringLiteral(grp.keys[0]))
    zkbpq__hmhl = {}
    bqdi__twcb = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        zkbpq__hmhl[None, 'size'] = 'size'
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for kzawi__fql in columns:
            fzrh__muti = grp.df_type.column_index[kzawi__fql]
            data = grp.df_type.data[fzrh__muti]
            data = to_str_arr_if_dict_array(data)
            iein__zfwe = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                iein__zfwe = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    zcs__kiu = SeriesType(data.dtype, data, None, string_type)
                    kwa__zeije = get_const_func_output_type(func, (zcs__kiu
                        ,), {}, typing_context, target_context)
                    if kwa__zeije != ArrayItemArrayType(string_array_type):
                        kwa__zeije = dtype_to_array_type(kwa__zeije)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=kzawi__fql, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    iwgz__uujva = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    uzk__whdi = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    uskqe__ocpgu = dict(numeric_only=iwgz__uujva, min_count
                        =uzk__whdi)
                    sakf__bsc = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        uskqe__ocpgu, sakf__bsc, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    iwgz__uujva = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    uzk__whdi = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    uskqe__ocpgu = dict(numeric_only=iwgz__uujva, min_count
                        =uzk__whdi)
                    sakf__bsc = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        uskqe__ocpgu, sakf__bsc, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    iwgz__uujva = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    uskqe__ocpgu = dict(numeric_only=iwgz__uujva)
                    sakf__bsc = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        uskqe__ocpgu, sakf__bsc, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    anx__vfo = args[0] if len(args) > 0 else kws.pop('axis', 0)
                    nvakf__meqsr = args[1] if len(args) > 1 else kws.pop(
                        'skipna', True)
                    uskqe__ocpgu = dict(axis=anx__vfo, skipna=nvakf__meqsr)
                    sakf__bsc = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        uskqe__ocpgu, sakf__bsc, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    akpw__ukh = args[0] if len(args) > 0 else kws.pop('ddof', 1
                        )
                    uskqe__ocpgu = dict(ddof=akpw__ukh)
                    sakf__bsc = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        uskqe__ocpgu, sakf__bsc, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                kwa__zeije, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                tdqx__mruy = to_str_arr_if_dict_array(kwa__zeije)
                out_data.append(tdqx__mruy)
                out_columns.append(kzawi__fql)
                if func_name == 'agg':
                    zxrs__vmpwz = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    zkbpq__hmhl[kzawi__fql, zxrs__vmpwz] = kzawi__fql
                else:
                    zkbpq__hmhl[kzawi__fql, func_name] = kzawi__fql
                out_column_type.append(iein__zfwe)
            else:
                bqdi__twcb.append(err_msg)
    if func_name == 'sum':
        gmyui__jnpig = any([(tie__qzyuq == ColumnType.NumericalColumn.value
            ) for tie__qzyuq in out_column_type])
        if gmyui__jnpig:
            out_data = [tie__qzyuq for tie__qzyuq, zav__gkqe in zip(
                out_data, out_column_type) if zav__gkqe != ColumnType.
                NonNumericalColumn.value]
            out_columns = [tie__qzyuq for tie__qzyuq, zav__gkqe in zip(
                out_columns, out_column_type) if zav__gkqe != ColumnType.
                NonNumericalColumn.value]
            zkbpq__hmhl = {}
            for kzawi__fql in out_columns:
                if grp.as_index is False and kzawi__fql in grp.keys:
                    continue
                zkbpq__hmhl[kzawi__fql, func_name] = kzawi__fql
    muntt__yzl = len(bqdi__twcb)
    if len(out_data) == 0:
        if muntt__yzl == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(muntt__yzl, ' was' if muntt__yzl == 1 else 's were',
                ','.join(bqdi__twcb)))
    uyys__vmd = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index):
        if isinstance(out_data[0], IntegerArrayType):
            mbw__rktzp = IntDtype(out_data[0].dtype)
        else:
            mbw__rktzp = out_data[0].dtype
        cpkfr__cqmcd = (types.none if func_name == 'size' else types.
            StringLiteral(grp.selection[0]))
        uyys__vmd = SeriesType(mbw__rktzp, index=index, name_typ=cpkfr__cqmcd)
    return signature(uyys__vmd, *args), zkbpq__hmhl


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    omr__bdvv = True
    if isinstance(f_val, str):
        omr__bdvv = False
        cybrf__dhom = f_val
    elif is_overload_constant_str(f_val):
        omr__bdvv = False
        cybrf__dhom = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        omr__bdvv = False
        cybrf__dhom = bodo.utils.typing.get_builtin_function_name(f_val)
    if not omr__bdvv:
        if cybrf__dhom not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {cybrf__dhom}')
        dqsxg__ofx = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(dqsxg__ofx, (), cybrf__dhom, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            hwic__tmmg = types.functions.MakeFunctionLiteral(f_val)
        else:
            hwic__tmmg = f_val
        validate_udf('agg', hwic__tmmg)
        func = get_overload_const_func(hwic__tmmg, None)
        rku__bwvj = func.code if hasattr(func, 'code') else func.__code__
        cybrf__dhom = rku__bwvj.co_name
        dqsxg__ofx = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(dqsxg__ofx, (), 'agg', typing_context,
            target_context, hwic__tmmg)[0].return_type
    return cybrf__dhom, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    ocayt__mvcnu = kws and all(isinstance(gvos__vduqe, types.Tuple) and len
        (gvos__vduqe) == 2 for gvos__vduqe in kws.values())
    if is_overload_none(func) and not ocayt__mvcnu:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not ocayt__mvcnu:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    axqg__uwtfd = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if ocayt__mvcnu or is_overload_constant_dict(func):
        if ocayt__mvcnu:
            sbzke__vxak = [get_literal_value(bgdyf__pia) for bgdyf__pia,
                zgz__doc in kws.values()]
            eec__yxbfj = [get_literal_value(anic__rrir) for zgz__doc,
                anic__rrir in kws.values()]
        else:
            zzdte__puy = get_overload_constant_dict(func)
            sbzke__vxak = tuple(zzdte__puy.keys())
            eec__yxbfj = tuple(zzdte__puy.values())
        if 'head' in eec__yxbfj:
            raise BodoError(
                'Groupby.agg()/aggregate(): head cannot be mixed with other groupby operations.'
                )
        if any(kzawi__fql not in grp.selection and kzawi__fql not in grp.
            keys for kzawi__fql in sbzke__vxak):
            raise_bodo_error(
                f'Selected column names {sbzke__vxak} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            eec__yxbfj)
        if ocayt__mvcnu and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        zkbpq__hmhl = {}
        out_columns = []
        out_data = []
        out_column_type = []
        lxe__ftvg = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for igjw__hgb, f_val in zip(sbzke__vxak, eec__yxbfj):
            if isinstance(f_val, (tuple, list)):
                rmho__emuk = 0
                for hwic__tmmg in f_val:
                    cybrf__dhom, out_tp = get_agg_funcname_and_outtyp(grp,
                        igjw__hgb, hwic__tmmg, typing_context, target_context)
                    axqg__uwtfd = cybrf__dhom in list_cumulative
                    if cybrf__dhom == '<lambda>' and len(f_val) > 1:
                        cybrf__dhom = '<lambda_' + str(rmho__emuk) + '>'
                        rmho__emuk += 1
                    out_columns.append((igjw__hgb, cybrf__dhom))
                    zkbpq__hmhl[igjw__hgb, cybrf__dhom
                        ] = igjw__hgb, cybrf__dhom
                    _append_out_type(grp, out_data, out_tp)
            else:
                cybrf__dhom, out_tp = get_agg_funcname_and_outtyp(grp,
                    igjw__hgb, f_val, typing_context, target_context)
                axqg__uwtfd = cybrf__dhom in list_cumulative
                if multi_level_names:
                    out_columns.append((igjw__hgb, cybrf__dhom))
                    zkbpq__hmhl[igjw__hgb, cybrf__dhom
                        ] = igjw__hgb, cybrf__dhom
                elif not ocayt__mvcnu:
                    out_columns.append(igjw__hgb)
                    zkbpq__hmhl[igjw__hgb, cybrf__dhom] = igjw__hgb
                elif ocayt__mvcnu:
                    lxe__ftvg.append(cybrf__dhom)
                _append_out_type(grp, out_data, out_tp)
        if ocayt__mvcnu:
            for tuhhv__rjtu, dfkd__ylnl in enumerate(kws.keys()):
                out_columns.append(dfkd__ylnl)
                zkbpq__hmhl[sbzke__vxak[tuhhv__rjtu], lxe__ftvg[tuhhv__rjtu]
                    ] = dfkd__ylnl
        if axqg__uwtfd:
            index = grp.df_type.index
        else:
            index = out_tp.index
        uyys__vmd = DataFrameType(tuple(out_data), index, tuple(out_columns))
        return signature(uyys__vmd, *args), zkbpq__hmhl
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            nbyud__mfwb = get_overload_const_list(func)
        else:
            nbyud__mfwb = func.types
        if len(nbyud__mfwb) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        rmho__emuk = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        zkbpq__hmhl = {}
        depcb__cyr = grp.selection[0]
        for f_val in nbyud__mfwb:
            cybrf__dhom, out_tp = get_agg_funcname_and_outtyp(grp,
                depcb__cyr, f_val, typing_context, target_context)
            axqg__uwtfd = cybrf__dhom in list_cumulative
            if cybrf__dhom == '<lambda>' and len(nbyud__mfwb) > 1:
                cybrf__dhom = '<lambda_' + str(rmho__emuk) + '>'
                rmho__emuk += 1
            out_columns.append(cybrf__dhom)
            zkbpq__hmhl[depcb__cyr, cybrf__dhom] = cybrf__dhom
            _append_out_type(grp, out_data, out_tp)
        if axqg__uwtfd:
            index = grp.df_type.index
        else:
            index = out_tp.index
        uyys__vmd = DataFrameType(tuple(out_data), index, tuple(out_columns))
        return signature(uyys__vmd, *args), zkbpq__hmhl
    cybrf__dhom = ''
    if types.unliteral(func) == types.unicode_type:
        cybrf__dhom = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        cybrf__dhom = bodo.utils.typing.get_builtin_function_name(func)
    if cybrf__dhom:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, cybrf__dhom, typing_context, kws)
    validate_udf('agg', func)
    return get_agg_typ(grp, args, 'agg', typing_context, target_context, func)


def resolve_transformative(grp, args, kws, msg, name_operation):
    index = grp.df_type.index
    out_columns = []
    out_data = []
    if name_operation in list_cumulative:
        kws = dict(kws) if kws else {}
        anx__vfo = args[0] if len(args) > 0 else kws.pop('axis', 0)
        iwgz__uujva = args[1] if len(args) > 1 else kws.pop('numeric_only',
            False)
        nvakf__meqsr = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        uskqe__ocpgu = dict(axis=anx__vfo, numeric_only=iwgz__uujva)
        sakf__bsc = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', uskqe__ocpgu,
            sakf__bsc, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        ojm__ibmyb = args[0] if len(args) > 0 else kws.pop('periods', 1)
        lev__yhkzz = args[1] if len(args) > 1 else kws.pop('freq', None)
        anx__vfo = args[2] if len(args) > 2 else kws.pop('axis', 0)
        ihkgb__yfknd = args[3] if len(args) > 3 else kws.pop('fill_value', None
            )
        uskqe__ocpgu = dict(freq=lev__yhkzz, axis=anx__vfo, fill_value=
            ihkgb__yfknd)
        sakf__bsc = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', uskqe__ocpgu,
            sakf__bsc, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        uufm__ulf = args[0] if len(args) > 0 else kws.pop('func', None)
        wjwy__fui = kws.pop('engine', None)
        bti__mqey = kws.pop('engine_kwargs', None)
        uskqe__ocpgu = dict(engine=wjwy__fui, engine_kwargs=bti__mqey)
        sakf__bsc = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', uskqe__ocpgu,
            sakf__bsc, package_name='pandas', module_name='GroupBy')
    zkbpq__hmhl = {}
    for kzawi__fql in grp.selection:
        out_columns.append(kzawi__fql)
        zkbpq__hmhl[kzawi__fql, name_operation] = kzawi__fql
        fzrh__muti = grp.df_type.columns.index(kzawi__fql)
        data = grp.df_type.data[fzrh__muti]
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
            kwa__zeije, err_msg = get_groupby_output_dtype(data,
                get_literal_value(uufm__ulf), grp.df_type.index)
            if err_msg == 'ok':
                data = kwa__zeije
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    uyys__vmd = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        uyys__vmd = SeriesType(out_data[0].dtype, data=out_data[0], index=
            index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(uyys__vmd, *args), zkbpq__hmhl


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
        yxmeu__pdel = _get_groupby_apply_udf_out_type(func, grp, f_args,
            kws, self.context, numba.core.registry.cpu_target.target_context)
        mrrq__aqn = isinstance(yxmeu__pdel, (SeriesType,
            HeterogeneousSeriesType)
            ) and yxmeu__pdel.const_info is not None or not isinstance(
            yxmeu__pdel, (SeriesType, DataFrameType))
        if mrrq__aqn:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                rpe__oefeg = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                qac__agpwi = tuple(grp.df_type.columns.index(grp.keys[
                    tuhhv__rjtu]) for tuhhv__rjtu in range(len(grp.keys)))
                lefl__zmjqw = tuple(grp.df_type.data[fzrh__muti] for
                    fzrh__muti in qac__agpwi)
                rpe__oefeg = MultiIndexType(lefl__zmjqw, tuple(types.
                    literal(lmgfw__xcl) for lmgfw__xcl in grp.keys))
            else:
                fzrh__muti = grp.df_type.columns.index(grp.keys[0])
                cfis__cbm = grp.df_type.data[fzrh__muti]
                rpe__oefeg = bodo.hiframes.pd_index_ext.array_type_to_index(
                    cfis__cbm, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            nee__azz = tuple(grp.df_type.data[grp.df_type.columns.index(
                kzawi__fql)] for kzawi__fql in grp.keys)
            qwpgk__bndoc = tuple(types.literal(gvos__vduqe) for gvos__vduqe in
                grp.keys) + get_index_name_types(yxmeu__pdel.index)
            if not grp.as_index:
                nee__azz = types.Array(types.int64, 1, 'C'),
                qwpgk__bndoc = (types.none,) + get_index_name_types(yxmeu__pdel
                    .index)
            rpe__oefeg = MultiIndexType(nee__azz + get_index_data_arr_types
                (yxmeu__pdel.index), qwpgk__bndoc)
        if mrrq__aqn:
            if isinstance(yxmeu__pdel, HeterogeneousSeriesType):
                zgz__doc, owhh__ceue = yxmeu__pdel.const_info
                if isinstance(yxmeu__pdel.data, bodo.libs.
                    nullable_tuple_ext.NullableTupleType):
                    ggbpc__qqloo = yxmeu__pdel.data.tuple_typ.types
                elif isinstance(yxmeu__pdel.data, types.Tuple):
                    ggbpc__qqloo = yxmeu__pdel.data.types
                fynd__whfk = tuple(to_nullable_type(dtype_to_array_type(
                    fqc__imlnu)) for fqc__imlnu in ggbpc__qqloo)
                irg__nymaq = DataFrameType(out_data + fynd__whfk,
                    rpe__oefeg, out_columns + owhh__ceue)
            elif isinstance(yxmeu__pdel, SeriesType):
                zam__qwaur, owhh__ceue = yxmeu__pdel.const_info
                fynd__whfk = tuple(to_nullable_type(dtype_to_array_type(
                    yxmeu__pdel.dtype)) for zgz__doc in range(zam__qwaur))
                irg__nymaq = DataFrameType(out_data + fynd__whfk,
                    rpe__oefeg, out_columns + owhh__ceue)
            else:
                yytxc__urcn = get_udf_out_arr_type(yxmeu__pdel)
                if not grp.as_index:
                    irg__nymaq = DataFrameType(out_data + (yytxc__urcn,),
                        rpe__oefeg, out_columns + ('',))
                else:
                    irg__nymaq = SeriesType(yytxc__urcn.dtype, yytxc__urcn,
                        rpe__oefeg, None)
        elif isinstance(yxmeu__pdel, SeriesType):
            irg__nymaq = SeriesType(yxmeu__pdel.dtype, yxmeu__pdel.data,
                rpe__oefeg, yxmeu__pdel.name_typ)
        else:
            irg__nymaq = DataFrameType(yxmeu__pdel.data, rpe__oefeg,
                yxmeu__pdel.columns)
        tsaee__dwxb = gen_apply_pysig(len(f_args), kws.keys())
        wexi__ftago = (func, *f_args) + tuple(kws.values())
        return signature(irg__nymaq, *wexi__ftago).replace(pysig=tsaee__dwxb)

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
    aqi__hafpp = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            igjw__hgb = grp.selection[0]
            yytxc__urcn = aqi__hafpp.data[aqi__hafpp.columns.index(igjw__hgb)]
            yytxc__urcn = to_str_arr_if_dict_array(yytxc__urcn)
            qmnt__psmfc = SeriesType(yytxc__urcn.dtype, yytxc__urcn,
                aqi__hafpp.index, types.literal(igjw__hgb))
        else:
            ggil__uiwv = tuple(aqi__hafpp.data[aqi__hafpp.columns.index(
                kzawi__fql)] for kzawi__fql in grp.selection)
            ggil__uiwv = tuple(to_str_arr_if_dict_array(fqc__imlnu) for
                fqc__imlnu in ggil__uiwv)
            qmnt__psmfc = DataFrameType(ggil__uiwv, aqi__hafpp.index, tuple
                (grp.selection))
    else:
        qmnt__psmfc = aqi__hafpp
    slxso__kggsk = qmnt__psmfc,
    slxso__kggsk += tuple(f_args)
    try:
        yxmeu__pdel = get_const_func_output_type(func, slxso__kggsk, kws,
            typing_context, target_context)
    except Exception as lnog__xka:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', lnog__xka),
            getattr(lnog__xka, 'loc', None))
    return yxmeu__pdel


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    slxso__kggsk = (grp,) + f_args
    try:
        yxmeu__pdel = get_const_func_output_type(func, slxso__kggsk, kws,
            self.context, numba.core.registry.cpu_target.target_context, False)
    except Exception as lnog__xka:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', lnog__xka),
            getattr(lnog__xka, 'loc', None))
    tsaee__dwxb = gen_apply_pysig(len(f_args), kws.keys())
    wexi__ftago = (func, *f_args) + tuple(kws.values())
    return signature(yxmeu__pdel, *wexi__ftago).replace(pysig=tsaee__dwxb)


def gen_apply_pysig(n_args, kws):
    led__ocayu = ', '.join(f'arg{tuhhv__rjtu}' for tuhhv__rjtu in range(n_args)
        )
    led__ocayu = led__ocayu + ', ' if led__ocayu else ''
    dbbp__ami = ', '.join(f"{bjhm__tptx} = ''" for bjhm__tptx in kws)
    byc__qoloo = f'def apply_stub(func, {led__ocayu}{dbbp__ami}):\n'
    byc__qoloo += '    pass\n'
    zflar__gbq = {}
    exec(byc__qoloo, {}, zflar__gbq)
    odiib__bvh = zflar__gbq['apply_stub']
    return numba.core.utils.pysignature(odiib__bvh)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        bwjc__mfh = types.Array(types.int64, 1, 'C')
        kbnqu__qdnc = _pivot_values.meta
        piwgw__itwo = len(kbnqu__qdnc)
        oasrr__cyqq = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        dtxkj__fib = DataFrameType((bwjc__mfh,) * piwgw__itwo, oasrr__cyqq,
            tuple(kbnqu__qdnc))
        return signature(dtxkj__fib, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    byc__qoloo = 'def impl(keys, dropna, _is_parallel):\n'
    byc__qoloo += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    byc__qoloo += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{tuhhv__rjtu}])' for tuhhv__rjtu in range(len(
        keys.types))))
    byc__qoloo += '    table = arr_info_list_to_table(info_list)\n'
    byc__qoloo += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    byc__qoloo += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    byc__qoloo += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    byc__qoloo += '    delete_table_decref_arrays(table)\n'
    byc__qoloo += '    ev.finalize()\n'
    byc__qoloo += '    return sort_idx, group_labels, ngroups\n'
    zflar__gbq = {}
    exec(byc__qoloo, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, zflar__gbq)
    hmj__xdkxh = zflar__gbq['impl']
    return hmj__xdkxh


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    vzytt__jcf = len(labels)
    jgu__dwqne = np.zeros(ngroups, dtype=np.int64)
    yyu__bmw = np.zeros(ngroups, dtype=np.int64)
    swnjh__ztm = 0
    jffb__vmy = 0
    for tuhhv__rjtu in range(vzytt__jcf):
        yjoir__ykeqj = labels[tuhhv__rjtu]
        if yjoir__ykeqj < 0:
            swnjh__ztm += 1
        else:
            jffb__vmy += 1
            if tuhhv__rjtu == vzytt__jcf - 1 or yjoir__ykeqj != labels[
                tuhhv__rjtu + 1]:
                jgu__dwqne[yjoir__ykeqj] = swnjh__ztm
                yyu__bmw[yjoir__ykeqj] = swnjh__ztm + jffb__vmy
                swnjh__ztm += jffb__vmy
                jffb__vmy = 0
    return jgu__dwqne, yyu__bmw


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    hmj__xdkxh, zgz__doc = gen_shuffle_dataframe(df, keys, _is_parallel)
    return hmj__xdkxh


def gen_shuffle_dataframe(df, keys, _is_parallel):
    zam__qwaur = len(df.columns)
    cad__oiko = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    byc__qoloo = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        byc__qoloo += '  return df, keys, get_null_shuffle_info()\n'
        zflar__gbq = {}
        exec(byc__qoloo, {'get_null_shuffle_info': get_null_shuffle_info},
            zflar__gbq)
        hmj__xdkxh = zflar__gbq['impl']
        return hmj__xdkxh
    for tuhhv__rjtu in range(zam__qwaur):
        byc__qoloo += f"""  in_arr{tuhhv__rjtu} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {tuhhv__rjtu})
"""
    byc__qoloo += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    byc__qoloo += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{tuhhv__rjtu}])' for tuhhv__rjtu in range(
        cad__oiko)), ', '.join(f'array_to_info(in_arr{tuhhv__rjtu})' for
        tuhhv__rjtu in range(zam__qwaur)), 'array_to_info(in_index_arr)')
    byc__qoloo += '  table = arr_info_list_to_table(info_list)\n'
    byc__qoloo += (
        f'  out_table = shuffle_table(table, {cad__oiko}, _is_parallel, 1)\n')
    for tuhhv__rjtu in range(cad__oiko):
        byc__qoloo += f"""  out_key{tuhhv__rjtu} = info_to_array(info_from_table(out_table, {tuhhv__rjtu}), keys{tuhhv__rjtu}_typ)
"""
    for tuhhv__rjtu in range(zam__qwaur):
        byc__qoloo += f"""  out_arr{tuhhv__rjtu} = info_to_array(info_from_table(out_table, {tuhhv__rjtu + cad__oiko}), in_arr{tuhhv__rjtu}_typ)
"""
    byc__qoloo += f"""  out_arr_index = info_to_array(info_from_table(out_table, {cad__oiko + zam__qwaur}), ind_arr_typ)
"""
    byc__qoloo += '  shuffle_info = get_shuffle_info(out_table)\n'
    byc__qoloo += '  delete_table(out_table)\n'
    byc__qoloo += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{tuhhv__rjtu}' for tuhhv__rjtu in range(
        zam__qwaur))
    byc__qoloo += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    byc__qoloo += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    byc__qoloo += '  return out_df, ({},), shuffle_info\n'.format(', '.join
        (f'out_key{tuhhv__rjtu}' for tuhhv__rjtu in range(cad__oiko)))
    fcecx__bird = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    fcecx__bird.update({f'keys{tuhhv__rjtu}_typ': keys.types[tuhhv__rjtu] for
        tuhhv__rjtu in range(cad__oiko)})
    fcecx__bird.update({f'in_arr{tuhhv__rjtu}_typ': df.data[tuhhv__rjtu] for
        tuhhv__rjtu in range(zam__qwaur)})
    zflar__gbq = {}
    exec(byc__qoloo, fcecx__bird, zflar__gbq)
    hmj__xdkxh = zflar__gbq['impl']
    return hmj__xdkxh, fcecx__bird


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        vnpxs__jxy = len(data.array_types)
        byc__qoloo = 'def impl(data, shuffle_info):\n'
        byc__qoloo += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{tuhhv__rjtu}])' for tuhhv__rjtu in
            range(vnpxs__jxy)))
        byc__qoloo += '  table = arr_info_list_to_table(info_list)\n'
        byc__qoloo += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for tuhhv__rjtu in range(vnpxs__jxy):
            byc__qoloo += f"""  out_arr{tuhhv__rjtu} = info_to_array(info_from_table(out_table, {tuhhv__rjtu}), data._data[{tuhhv__rjtu}])
"""
        byc__qoloo += '  delete_table(out_table)\n'
        byc__qoloo += '  delete_table(table)\n'
        byc__qoloo += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{tuhhv__rjtu}' for tuhhv__rjtu in
            range(vnpxs__jxy))))
        zflar__gbq = {}
        exec(byc__qoloo, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, zflar__gbq)
        hmj__xdkxh = zflar__gbq['impl']
        return hmj__xdkxh
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            jdneq__gen = bodo.utils.conversion.index_to_array(data)
            tdqx__mruy = reverse_shuffle(jdneq__gen, shuffle_info)
            return bodo.utils.conversion.index_from_array(tdqx__mruy)
        return impl_index

    def impl_arr(data, shuffle_info):
        xbn__apibm = [array_to_info(data)]
        qkbsy__ukr = arr_info_list_to_table(xbn__apibm)
        mtwgg__okom = reverse_shuffle_table(qkbsy__ukr, shuffle_info)
        tdqx__mruy = info_to_array(info_from_table(mtwgg__okom, 0), data)
        delete_table(mtwgg__okom)
        delete_table(qkbsy__ukr)
        return tdqx__mruy
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    uskqe__ocpgu = dict(normalize=normalize, sort=sort, bins=bins, dropna=
        dropna)
    sakf__bsc = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', uskqe__ocpgu, sakf__bsc,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    tlha__cqou = get_overload_const_bool(ascending)
    aievu__nxpr = grp.selection[0]
    byc__qoloo = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    spt__bpm = (
        f"lambda S: S.value_counts(ascending={tlha__cqou}, _index_name='{aievu__nxpr}')"
        )
    byc__qoloo += f'    return grp.apply({spt__bpm})\n'
    zflar__gbq = {}
    exec(byc__qoloo, {'bodo': bodo}, zflar__gbq)
    hmj__xdkxh = zflar__gbq['impl']
    return hmj__xdkxh


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
    for fuadq__iyb in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, fuadq__iyb, no_unliteral=True
            )(create_unsupported_overload(f'DataFrameGroupBy.{fuadq__iyb}'))
    for fuadq__iyb in groupby_unsupported:
        overload_method(DataFrameGroupByType, fuadq__iyb, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{fuadq__iyb}'))
    for fuadq__iyb in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, fuadq__iyb, no_unliteral=True
            )(create_unsupported_overload(f'SeriesGroupBy.{fuadq__iyb}'))
    for fuadq__iyb in series_only_unsupported:
        overload_method(DataFrameGroupByType, fuadq__iyb, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{fuadq__iyb}'))
    for fuadq__iyb in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, fuadq__iyb, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{fuadq__iyb}'))


_install_groupby_unsupported()
