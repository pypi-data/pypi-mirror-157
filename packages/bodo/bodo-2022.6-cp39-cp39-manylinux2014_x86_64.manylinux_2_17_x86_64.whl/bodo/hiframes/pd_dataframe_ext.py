"""
Implement pd.DataFrame typing and data model handling.
"""
import json
import operator
from functools import cached_property
from urllib.parse import quote
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow as pa
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.cpython.listobj import ListInstance
from numba.extending import infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_index_ext import HeterogeneousIndexType, NumericIndexType, RangeIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.series_indexing import SeriesIlocType
from bodo.hiframes.table import Table, TableType, decode_if_dict_table, get_table_data, set_table_data_codegen
from bodo.io import json_cpp
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, py_table_to_cpp_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.distributed_api import bcast_scalar
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import str_arr_from_sequence
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.conversion import fix_arr_dtype, index_to_array
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, decode_if_dict_array, dtype_to_array_type, get_index_data_arr_types, get_literal_value, get_overload_const, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_udf_error_msg, get_udf_out_arr_type, is_heterogeneous_tuple_type, is_iterable_type, is_literal_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_str_arr_type, is_tuple_like_type, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array
from bodo.utils.utils import is_null_pointer
_json_write = types.ExternalFunction('json_write', types.void(types.voidptr,
    types.voidptr, types.int64, types.int64, types.bool_, types.bool_,
    types.voidptr))
ll.add_symbol('json_write', json_cpp.json_write)


class DataFrameType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, data=None, index=None, columns=None, dist=None,
        is_table_format=False):
        from bodo.transforms.distributed_analysis import Distribution
        self.data = data
        if index is None:
            index = RangeIndexType(types.none)
        self.index = index
        self.columns = columns
        dist = Distribution.OneD_Var if dist is None else dist
        self.dist = dist
        self.is_table_format = is_table_format
        if columns is None:
            assert is_table_format, 'Determining columns at runtime is only supported for DataFrame with table format'
            self.table_type = TableType(tuple(data[:-1]), True)
        else:
            self.table_type = TableType(data) if is_table_format else None
        super(DataFrameType, self).__init__(name=
            f'dataframe({data}, {index}, {columns}, {dist}, {is_table_format}, {self.has_runtime_cols})'
            )

    def __str__(self):
        if not self.has_runtime_cols and len(self.columns) > 20:
            yigel__dnpb = f'{len(self.data)} columns of types {set(self.data)}'
            gju__vpy = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({yigel__dnpb}, {self.index}, {gju__vpy}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
                )
        return super().__str__()

    def copy(self, data=None, index=None, columns=None, dist=None,
        is_table_format=None):
        if data is None:
            data = self.data
        if columns is None:
            columns = self.columns
        if index is None:
            index = self.index
        if dist is None:
            dist = self.dist
        if is_table_format is None:
            is_table_format = self.is_table_format
        return DataFrameType(data, index, columns, dist, is_table_format)

    @property
    def has_runtime_cols(self):
        return self.columns is None

    @cached_property
    def column_index(self):
        return {ymogs__eeuca: i for i, ymogs__eeuca in enumerate(self.columns)}

    @property
    def runtime_colname_typ(self):
        return self.data[-1] if self.has_runtime_cols else None

    @property
    def runtime_data_types(self):
        return self.data[:-1] if self.has_runtime_cols else self.data

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return (self.data, self.index, self.columns, self.dist, self.
            is_table_format)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    def unify(self, typingctx, other):
        from bodo.transforms.distributed_analysis import Distribution
        if (isinstance(other, DataFrameType) and len(other.data) == len(
            self.data) and other.columns == self.columns and other.
            has_runtime_cols == self.has_runtime_cols):
            jnnn__ruf = (self.index if self.index == other.index else self.
                index.unify(typingctx, other.index))
            data = tuple(bie__wtzw.unify(typingctx, yjolu__bnt) if 
                bie__wtzw != yjolu__bnt else bie__wtzw for bie__wtzw,
                yjolu__bnt in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if jnnn__ruf is not None and None not in data:
                return DataFrameType(data, jnnn__ruf, self.columns, dist,
                    self.is_table_format)
        if isinstance(other, DataFrameType) and len(self.data
            ) == 0 and not self.has_runtime_cols:
            return other

    def can_convert_to(self, typingctx, other):
        from numba.core.typeconv import Conversion
        if (isinstance(other, DataFrameType) and self.data == other.data and
            self.index == other.index and self.columns == other.columns and
            self.dist != other.dist and self.has_runtime_cols == other.
            has_runtime_cols):
            return Conversion.safe

    def is_precise(self):
        return all(bie__wtzw.is_precise() for bie__wtzw in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        pvjtb__xmta = self.columns.index(col_name)
        uiyat__hkv = tuple(list(self.data[:pvjtb__xmta]) + [new_type] +
            list(self.data[pvjtb__xmta + 1:]))
        return DataFrameType(uiyat__hkv, self.index, self.columns, self.
            dist, self.is_table_format)


def check_runtime_cols_unsupported(df, func_name):
    if isinstance(df, DataFrameType) and df.has_runtime_cols:
        raise BodoError(
            f'{func_name} on DataFrames with columns determined at runtime is not yet supported. Please return the DataFrame to regular Python to update typing information.'
            )


class DataFramePayloadType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        super(DataFramePayloadType, self).__init__(name=
            f'DataFramePayloadType({df_type})')

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFramePayloadType)
class DataFramePayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        data_typ = types.Tuple(fe_type.df_type.data)
        if fe_type.df_type.is_table_format:
            data_typ = types.Tuple([fe_type.df_type.table_type])
        nbkjh__sxqm = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            nbkjh__sxqm.append(('columns', fe_type.df_type.runtime_colname_typ)
                )
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, nbkjh__sxqm)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        nbkjh__sxqm = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, nbkjh__sxqm)


make_attribute_wrapper(DataFrameType, 'meminfo', '_meminfo')


@infer_getattr
class DataFrameAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])

    @bound_function('df.head')
    def resolve_head(self, df, args, kws):
        func_name = 'DataFrame.head'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        ywvsr__pxs = 'n',
        iniay__paal = {'n': 5}
        ggr__wltx, nvwx__fecw = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, ywvsr__pxs, iniay__paal)
        bic__nfx = nvwx__fecw[0]
        if not is_overload_int(bic__nfx):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        iml__yxr = df.copy()
        return iml__yxr(*nvwx__fecw).replace(pysig=ggr__wltx)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        cwnp__mnmdd = (df,) + args
        ywvsr__pxs = 'df', 'method', 'min_periods'
        iniay__paal = {'method': 'pearson', 'min_periods': 1}
        ogzvd__fipzu = 'method',
        ggr__wltx, nvwx__fecw = bodo.utils.typing.fold_typing_args(func_name,
            cwnp__mnmdd, kws, ywvsr__pxs, iniay__paal, ogzvd__fipzu)
        sgaan__ihh = nvwx__fecw[2]
        if not is_overload_int(sgaan__ihh):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        ygv__mwq = []
        ols__kvk = []
        for ymogs__eeuca, ottyg__jhd in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(ottyg__jhd.dtype):
                ygv__mwq.append(ymogs__eeuca)
                ols__kvk.append(types.Array(types.float64, 1, 'A'))
        if len(ygv__mwq) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        ols__kvk = tuple(ols__kvk)
        ygv__mwq = tuple(ygv__mwq)
        index_typ = bodo.utils.typing.type_col_to_index(ygv__mwq)
        iml__yxr = DataFrameType(ols__kvk, index_typ, ygv__mwq)
        return iml__yxr(*nvwx__fecw).replace(pysig=ggr__wltx)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        xbpr__ehd = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        bxiy__ospc = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        ipnj__dcgnd = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        afow__mitty = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        ilq__rbp = dict(raw=bxiy__ospc, result_type=ipnj__dcgnd)
        sgaj__olh = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', ilq__rbp, sgaj__olh,
            package_name='pandas', module_name='DataFrame')
        tbgyf__ossu = True
        if types.unliteral(xbpr__ehd) == types.unicode_type:
            if not is_overload_constant_str(xbpr__ehd):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            tbgyf__ossu = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        waiqc__vmja = get_overload_const_int(axis)
        if tbgyf__ossu and waiqc__vmja != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif waiqc__vmja not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        srx__usvb = []
        for arr_typ in df.data:
            wger__apix = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            lxdqt__utzjo = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(wger__apix), types.int64), {}
                ).return_type
            srx__usvb.append(lxdqt__utzjo)
        ejfl__saabz = types.none
        hsflu__iwjqg = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(ymogs__eeuca) for ymogs__eeuca in df.
            columns)), None)
        smnv__hxt = types.BaseTuple.from_types(srx__usvb)
        hbf__uerrg = types.Tuple([types.bool_] * len(smnv__hxt))
        liy__mqd = bodo.NullableTupleType(smnv__hxt, hbf__uerrg)
        oai__pqz = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if oai__pqz == types.NPDatetime('ns'):
            oai__pqz = bodo.pd_timestamp_type
        if oai__pqz == types.NPTimedelta('ns'):
            oai__pqz = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(smnv__hxt):
            zqnps__ngg = HeterogeneousSeriesType(liy__mqd, hsflu__iwjqg,
                oai__pqz)
        else:
            zqnps__ngg = SeriesType(smnv__hxt.dtype, liy__mqd, hsflu__iwjqg,
                oai__pqz)
        tmoh__bhh = zqnps__ngg,
        if afow__mitty is not None:
            tmoh__bhh += tuple(afow__mitty.types)
        try:
            if not tbgyf__ossu:
                wfbr__yam = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(xbpr__ehd), self.context,
                    'DataFrame.apply', axis if waiqc__vmja == 1 else None)
            else:
                wfbr__yam = get_const_func_output_type(xbpr__ehd, tmoh__bhh,
                    kws, self.context, numba.core.registry.cpu_target.
                    target_context)
        except Exception as ouikx__fmhal:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()',
                ouikx__fmhal))
        if tbgyf__ossu:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(wfbr__yam, (SeriesType, HeterogeneousSeriesType)
                ) and wfbr__yam.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(wfbr__yam, HeterogeneousSeriesType):
                sjk__xtzu, tqp__azw = wfbr__yam.const_info
                if isinstance(wfbr__yam.data, bodo.libs.nullable_tuple_ext.
                    NullableTupleType):
                    izsnq__lquzr = wfbr__yam.data.tuple_typ.types
                elif isinstance(wfbr__yam.data, types.Tuple):
                    izsnq__lquzr = wfbr__yam.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                psv__utzg = tuple(to_nullable_type(dtype_to_array_type(
                    ovtb__udqf)) for ovtb__udqf in izsnq__lquzr)
                lcwh__kynm = DataFrameType(psv__utzg, df.index, tqp__azw)
            elif isinstance(wfbr__yam, SeriesType):
                iylgk__ispxw, tqp__azw = wfbr__yam.const_info
                psv__utzg = tuple(to_nullable_type(dtype_to_array_type(
                    wfbr__yam.dtype)) for sjk__xtzu in range(iylgk__ispxw))
                lcwh__kynm = DataFrameType(psv__utzg, df.index, tqp__azw)
            else:
                nln__kub = get_udf_out_arr_type(wfbr__yam)
                lcwh__kynm = SeriesType(nln__kub.dtype, nln__kub, df.index,
                    None)
        else:
            lcwh__kynm = wfbr__yam
        mtf__jozi = ', '.join("{} = ''".format(bie__wtzw) for bie__wtzw in
            kws.keys())
        xky__bvn = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {mtf__jozi}):
"""
        xky__bvn += '    pass\n'
        vpkt__gvz = {}
        exec(xky__bvn, {}, vpkt__gvz)
        lwnng__qys = vpkt__gvz['apply_stub']
        ggr__wltx = numba.core.utils.pysignature(lwnng__qys)
        oww__ixca = (xbpr__ehd, axis, bxiy__ospc, ipnj__dcgnd, afow__mitty
            ) + tuple(kws.values())
        return signature(lcwh__kynm, *oww__ixca).replace(pysig=ggr__wltx)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        ywvsr__pxs = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        iniay__paal = {'x': None, 'y': None, 'kind': 'line', 'figsize':
            None, 'ax': None, 'subplots': False, 'sharex': None, 'sharey': 
            False, 'layout': None, 'use_index': True, 'title': None, 'grid':
            None, 'legend': True, 'style': None, 'logx': False, 'logy': 
            False, 'loglog': False, 'xticks': None, 'yticks': None, 'xlim':
            None, 'ylim': None, 'rot': None, 'fontsize': None, 'colormap':
            None, 'table': False, 'yerr': None, 'xerr': None, 'secondary_y':
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        ogzvd__fipzu = ('subplots', 'sharex', 'sharey', 'layout',
            'use_index', 'grid', 'style', 'logx', 'logy', 'loglog', 'xlim',
            'ylim', 'rot', 'colormap', 'table', 'yerr', 'xerr',
            'sort_columns', 'secondary_y', 'colorbar', 'position',
            'stacked', 'mark_right', 'include_bool', 'backend')
        ggr__wltx, nvwx__fecw = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, ywvsr__pxs, iniay__paal, ogzvd__fipzu)
        hml__vwu = nvwx__fecw[2]
        if not is_overload_constant_str(hml__vwu):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        kniw__sxnz = nvwx__fecw[0]
        if not is_overload_none(kniw__sxnz) and not (is_overload_int(
            kniw__sxnz) or is_overload_constant_str(kniw__sxnz)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(kniw__sxnz):
            xcke__cmeh = get_overload_const_str(kniw__sxnz)
            if xcke__cmeh not in df.columns:
                raise BodoError(f'{func_name}: {xcke__cmeh} column not found.')
        elif is_overload_int(kniw__sxnz):
            bkhgd__hkhi = get_overload_const_int(kniw__sxnz)
            if bkhgd__hkhi > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {bkhgd__hkhi} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            kniw__sxnz = df.columns[kniw__sxnz]
        utul__vju = nvwx__fecw[1]
        if not is_overload_none(utul__vju) and not (is_overload_int(
            utul__vju) or is_overload_constant_str(utul__vju)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(utul__vju):
            qmvqj__dwn = get_overload_const_str(utul__vju)
            if qmvqj__dwn not in df.columns:
                raise BodoError(f'{func_name}: {qmvqj__dwn} column not found.')
        elif is_overload_int(utul__vju):
            wcma__okf = get_overload_const_int(utul__vju)
            if wcma__okf > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {wcma__okf} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            utul__vju = df.columns[utul__vju]
        aimgh__xtoyk = nvwx__fecw[3]
        if not is_overload_none(aimgh__xtoyk) and not is_tuple_like_type(
            aimgh__xtoyk):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        afvrx__qcw = nvwx__fecw[10]
        if not is_overload_none(afvrx__qcw) and not is_overload_constant_str(
            afvrx__qcw):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        cgae__bpigp = nvwx__fecw[12]
        if not is_overload_bool(cgae__bpigp):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        jcgj__ffmt = nvwx__fecw[17]
        if not is_overload_none(jcgj__ffmt) and not is_tuple_like_type(
            jcgj__ffmt):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        fnusi__zmput = nvwx__fecw[18]
        if not is_overload_none(fnusi__zmput) and not is_tuple_like_type(
            fnusi__zmput):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        ubmm__zwk = nvwx__fecw[22]
        if not is_overload_none(ubmm__zwk) and not is_overload_int(ubmm__zwk):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        uxx__czpx = nvwx__fecw[29]
        if not is_overload_none(uxx__czpx) and not is_overload_constant_str(
            uxx__czpx):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        tewl__rqb = nvwx__fecw[30]
        if not is_overload_none(tewl__rqb) and not is_overload_constant_str(
            tewl__rqb):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        rau__mqqo = types.List(types.mpl_line_2d_type)
        hml__vwu = get_overload_const_str(hml__vwu)
        if hml__vwu == 'scatter':
            if is_overload_none(kniw__sxnz) and is_overload_none(utul__vju):
                raise BodoError(
                    f'{func_name}: {hml__vwu} requires an x and y column.')
            elif is_overload_none(kniw__sxnz):
                raise BodoError(f'{func_name}: {hml__vwu} x column is missing.'
                    )
            elif is_overload_none(utul__vju):
                raise BodoError(f'{func_name}: {hml__vwu} y column is missing.'
                    )
            rau__mqqo = types.mpl_path_collection_type
        elif hml__vwu != 'line':
            raise BodoError(f'{func_name}: {hml__vwu} plot is not supported.')
        return signature(rau__mqqo, *nvwx__fecw).replace(pysig=ggr__wltx)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            piup__epp = df.columns.index(attr)
            arr_typ = df.data[piup__epp]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            nxi__mzhj = []
            uiyat__hkv = []
            ciour__tejvz = False
            for i, wwzm__mfkx in enumerate(df.columns):
                if wwzm__mfkx[0] != attr:
                    continue
                ciour__tejvz = True
                nxi__mzhj.append(wwzm__mfkx[1] if len(wwzm__mfkx) == 2 else
                    wwzm__mfkx[1:])
                uiyat__hkv.append(df.data[i])
            if ciour__tejvz:
                return DataFrameType(tuple(uiyat__hkv), df.index, tuple(
                    nxi__mzhj))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        brbk__elkq = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(brbk__elkq)
        return lambda tup, idx: tup[val_ind]


def decref_df_data(context, builder, payload, df_type):
    if df_type.is_table_format:
        context.nrt.decref(builder, df_type.table_type, builder.
            extract_value(payload.data, 0))
        context.nrt.decref(builder, df_type.index, payload.index)
        if df_type.has_runtime_cols:
            context.nrt.decref(builder, df_type.data[-1], payload.columns)
        return
    for i in range(len(df_type.data)):
        dtx__tcu = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], dtx__tcu)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    fga__mibwh = builder.module
    rhwqw__pbcz = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    tez__quxd = cgutils.get_or_insert_function(fga__mibwh, rhwqw__pbcz,
        name='.dtor.df.{}'.format(df_type))
    if not tez__quxd.is_declaration:
        return tez__quxd
    tez__quxd.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(tez__quxd.append_basic_block())
    xjc__uwceu = tez__quxd.args[0]
    egpi__opsf = context.get_value_type(payload_type).as_pointer()
    nzs__ynvqr = builder.bitcast(xjc__uwceu, egpi__opsf)
    payload = context.make_helper(builder, payload_type, ref=nzs__ynvqr)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        jdssx__cuf = context.get_python_api(builder)
        olh__qghw = jdssx__cuf.gil_ensure()
        jdssx__cuf.decref(payload.parent)
        jdssx__cuf.gil_release(olh__qghw)
    builder.ret_void()
    return tez__quxd


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    hmt__veusg = cgutils.create_struct_proxy(payload_type)(context, builder)
    hmt__veusg.data = data_tup
    hmt__veusg.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        hmt__veusg.columns = colnames
    slvpq__vqbps = context.get_value_type(payload_type)
    uhw__emvsi = context.get_abi_sizeof(slvpq__vqbps)
    mpjoo__sxt = define_df_dtor(context, builder, df_type, payload_type)
    urb__pnwp = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, uhw__emvsi), mpjoo__sxt)
    uinmh__rwd = context.nrt.meminfo_data(builder, urb__pnwp)
    qfsls__bxwn = builder.bitcast(uinmh__rwd, slvpq__vqbps.as_pointer())
    ocsdo__tvvfz = cgutils.create_struct_proxy(df_type)(context, builder)
    ocsdo__tvvfz.meminfo = urb__pnwp
    if parent is None:
        ocsdo__tvvfz.parent = cgutils.get_null_value(ocsdo__tvvfz.parent.type)
    else:
        ocsdo__tvvfz.parent = parent
        hmt__veusg.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            jdssx__cuf = context.get_python_api(builder)
            olh__qghw = jdssx__cuf.gil_ensure()
            jdssx__cuf.incref(parent)
            jdssx__cuf.gil_release(olh__qghw)
    builder.store(hmt__veusg._getvalue(), qfsls__bxwn)
    return ocsdo__tvvfz._getvalue()


@intrinsic
def init_runtime_cols_dataframe(typingctx, data_typ, index_typ,
    colnames_index_typ=None):
    assert isinstance(data_typ, types.BaseTuple) and isinstance(data_typ.
        dtype, TableType
        ) and data_typ.dtype.has_runtime_cols, 'init_runtime_cols_dataframe must be called with a table that determines columns at runtime.'
    assert bodo.hiframes.pd_index_ext.is_pd_index_type(colnames_index_typ
        ) or isinstance(colnames_index_typ, bodo.hiframes.
        pd_multi_index_ext.MultiIndexType), 'Column names must be an index'
    if isinstance(data_typ.dtype.arr_types, types.UniTuple):
        bauc__hjrow = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype
            .arr_types)
    else:
        bauc__hjrow = [ovtb__udqf for ovtb__udqf in data_typ.dtype.arr_types]
    jthwu__omdp = DataFrameType(tuple(bauc__hjrow + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        yvna__kqd = construct_dataframe(context, builder, df_type, data_tup,
            index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return yvna__kqd
    sig = signature(jthwu__omdp, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    iylgk__ispxw = len(data_tup_typ.types)
    if iylgk__ispxw == 0:
        column_names = ()
    racf__fybgg = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    assert isinstance(racf__fybgg, ColNamesMetaType) and isinstance(racf__fybgg
        .meta, tuple
        ), 'Third argument to init_dataframe must be of type ColNamesMetaType, and must contain a tuple of column names'
    column_names = racf__fybgg.meta
    if iylgk__ispxw == 1 and isinstance(data_tup_typ.types[0], TableType):
        iylgk__ispxw = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == iylgk__ispxw, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    vrxe__fve = data_tup_typ.types
    if iylgk__ispxw != 0 and isinstance(data_tup_typ.types[0], TableType):
        vrxe__fve = data_tup_typ.types[0].arr_types
        is_table_format = True
    jthwu__omdp = DataFrameType(vrxe__fve, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            ddbe__ynkek = cgutils.create_struct_proxy(jthwu__omdp.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = ddbe__ynkek.parent
        yvna__kqd = construct_dataframe(context, builder, df_type, data_tup,
            index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return yvna__kqd
    sig = signature(jthwu__omdp, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        ocsdo__tvvfz = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, ocsdo__tvvfz.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        hmt__veusg = get_dataframe_payload(context, builder, df_typ, args[0])
        eavgy__vyh = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[eavgy__vyh]
        if df_typ.is_table_format:
            ddbe__ynkek = cgutils.create_struct_proxy(df_typ.table_type)(
                context, builder, builder.extract_value(hmt__veusg.data, 0))
            qzqd__qiuaj = df_typ.table_type.type_to_blk[arr_typ]
            wft__ntm = getattr(ddbe__ynkek, f'block_{qzqd__qiuaj}')
            ljel__por = ListInstance(context, builder, types.List(arr_typ),
                wft__ntm)
            awcl__mmu = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[eavgy__vyh])
            dtx__tcu = ljel__por.getitem(awcl__mmu)
        else:
            dtx__tcu = builder.extract_value(hmt__veusg.data, eavgy__vyh)
        mnn__clroz = cgutils.alloca_once_value(builder, dtx__tcu)
        gvs__rtbez = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, mnn__clroz, gvs__rtbez)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    urb__pnwp = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, urb__pnwp)
    egpi__opsf = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, egpi__opsf)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    jthwu__omdp = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        jthwu__omdp = types.Tuple([TableType(df_typ.data)])
    sig = signature(jthwu__omdp, df_typ)

    def codegen(context, builder, signature, args):
        hmt__veusg = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            hmt__veusg.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        hmt__veusg = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, hmt__veusg
            .index)
    jthwu__omdp = df_typ.index
    sig = signature(jthwu__omdp, df_typ)
    return sig, codegen


def get_dataframe_data(df, i):
    return df[i]


@infer_global(get_dataframe_data)
class GetDataFrameDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        if not is_overload_constant_int(args[1]):
            raise_bodo_error(
                'Selecting a DataFrame column requires a constant column label'
                )
        df = args[0]
        check_runtime_cols_unsupported(df, 'get_dataframe_data')
        i = get_overload_const_int(args[1])
        iml__yxr = df.data[i]
        return iml__yxr(*args)


GetDataFrameDataInfer.prefer_literal = True


def get_dataframe_data_impl(df, i):
    if df.is_table_format:

        def _impl(df, i):
            if has_parent(df) and _column_needs_unboxing(df, i):
                bodo.hiframes.boxing.unbox_dataframe_column(df, i)
            return get_table_data(_get_dataframe_data(df)[0], i)
        return _impl

    def _impl(df, i):
        if has_parent(df) and _column_needs_unboxing(df, i):
            bodo.hiframes.boxing.unbox_dataframe_column(df, i)
        return _get_dataframe_data(df)[i]
    return _impl


@intrinsic
def get_dataframe_table(typingctx, df_typ=None):
    assert df_typ.is_table_format, 'get_dataframe_table() expects table format'

    def codegen(context, builder, signature, args):
        hmt__veusg = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(hmt__veusg.data, 0))
    return df_typ.table_type(df_typ), codegen


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        hmt__veusg = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, hmt__veusg.columns)
    return df_typ.runtime_colname_typ(df_typ), codegen


@lower_builtin(get_dataframe_data, DataFrameType, types.IntegerLiteral)
def lower_get_dataframe_data(context, builder, sig, args):
    impl = get_dataframe_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_dataframe_data',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_index',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_table',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func


def alias_ext_init_dataframe(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 3
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_dataframe',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_init_dataframe


def init_dataframe_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 3 and not kws
    data_tup = args[0]
    index = args[1]
    smnv__hxt = self.typemap[data_tup.name]
    if any(is_tuple_like_type(ovtb__udqf) for ovtb__udqf in smnv__hxt.types):
        return None
    if equiv_set.has_shape(data_tup):
        njxii__sryzr = equiv_set.get_shape(data_tup)
        if len(njxii__sryzr) > 1:
            equiv_set.insert_equiv(*njxii__sryzr)
        if len(njxii__sryzr) > 0:
            hsflu__iwjqg = self.typemap[index.name]
            if not isinstance(hsflu__iwjqg, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(njxii__sryzr[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(njxii__sryzr[0], len(
                njxii__sryzr)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    lpn__szvvp = args[0]
    data_types = self.typemap[lpn__szvvp.name].data
    if any(is_tuple_like_type(ovtb__udqf) for ovtb__udqf in data_types):
        return None
    if equiv_set.has_shape(lpn__szvvp):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            lpn__szvvp)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    lpn__szvvp = args[0]
    hsflu__iwjqg = self.typemap[lpn__szvvp.name].index
    if isinstance(hsflu__iwjqg, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(lpn__szvvp):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            lpn__szvvp)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    lpn__szvvp = args[0]
    if equiv_set.has_shape(lpn__szvvp):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            lpn__szvvp), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    lpn__szvvp = args[0]
    if equiv_set.has_shape(lpn__szvvp):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            lpn__szvvp)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    eavgy__vyh = get_overload_const_int(c_ind_typ)
    if df_typ.data[eavgy__vyh] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        emhdb__pkje, sjk__xtzu, psj__bcy = args
        hmt__veusg = get_dataframe_payload(context, builder, df_typ,
            emhdb__pkje)
        if df_typ.is_table_format:
            ddbe__ynkek = cgutils.create_struct_proxy(df_typ.table_type)(
                context, builder, builder.extract_value(hmt__veusg.data, 0))
            qzqd__qiuaj = df_typ.table_type.type_to_blk[arr_typ]
            wft__ntm = getattr(ddbe__ynkek, f'block_{qzqd__qiuaj}')
            ljel__por = ListInstance(context, builder, types.List(arr_typ),
                wft__ntm)
            awcl__mmu = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[eavgy__vyh])
            ljel__por.setitem(awcl__mmu, psj__bcy, True)
        else:
            dtx__tcu = builder.extract_value(hmt__veusg.data, eavgy__vyh)
            context.nrt.decref(builder, df_typ.data[eavgy__vyh], dtx__tcu)
            hmt__veusg.data = builder.insert_value(hmt__veusg.data,
                psj__bcy, eavgy__vyh)
            context.nrt.incref(builder, arr_typ, psj__bcy)
        ocsdo__tvvfz = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=emhdb__pkje)
        payload_type = DataFramePayloadType(df_typ)
        nzs__ynvqr = context.nrt.meminfo_data(builder, ocsdo__tvvfz.meminfo)
        egpi__opsf = context.get_value_type(payload_type).as_pointer()
        nzs__ynvqr = builder.bitcast(nzs__ynvqr, egpi__opsf)
        builder.store(hmt__veusg._getvalue(), nzs__ynvqr)
        return impl_ret_borrowed(context, builder, df_typ, emhdb__pkje)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        sxom__oepjo = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        enq__pmf = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=sxom__oepjo)
        umc__knhi = get_dataframe_payload(context, builder, df_typ, sxom__oepjo
            )
        ocsdo__tvvfz = construct_dataframe(context, builder, signature.
            return_type, umc__knhi.data, index_val, enq__pmf.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), umc__knhi.data)
        return ocsdo__tvvfz
    jthwu__omdp = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(jthwu__omdp, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    iylgk__ispxw = len(df_type.columns)
    rmgjp__jbej = iylgk__ispxw
    aajdk__unltd = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    gbpm__unx = col_name not in df_type.columns
    eavgy__vyh = iylgk__ispxw
    if gbpm__unx:
        aajdk__unltd += arr_type,
        column_names += col_name,
        rmgjp__jbej += 1
    else:
        eavgy__vyh = df_type.columns.index(col_name)
        aajdk__unltd = tuple(arr_type if i == eavgy__vyh else aajdk__unltd[
            i] for i in range(iylgk__ispxw))

    def codegen(context, builder, signature, args):
        emhdb__pkje, sjk__xtzu, psj__bcy = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, emhdb__pkje)
        pqe__vazwp = cgutils.create_struct_proxy(df_type)(context, builder,
            value=emhdb__pkje)
        if df_type.is_table_format:
            mwkz__czh = df_type.table_type
            qdm__xiteo = builder.extract_value(in_dataframe_payload.data, 0)
            yjlkx__ghme = TableType(aajdk__unltd)
            nxjlk__yli = set_table_data_codegen(context, builder, mwkz__czh,
                qdm__xiteo, yjlkx__ghme, arr_type, psj__bcy, eavgy__vyh,
                gbpm__unx)
            data_tup = context.make_tuple(builder, types.Tuple([yjlkx__ghme
                ]), [nxjlk__yli])
        else:
            vrxe__fve = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != eavgy__vyh else psj__bcy) for i in range(
                iylgk__ispxw)]
            if gbpm__unx:
                vrxe__fve.append(psj__bcy)
            for lpn__szvvp, aqqzr__bpla in zip(vrxe__fve, aajdk__unltd):
                context.nrt.incref(builder, aqqzr__bpla, lpn__szvvp)
            data_tup = context.make_tuple(builder, types.Tuple(aajdk__unltd
                ), vrxe__fve)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        dsvbq__wxydh = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, pqe__vazwp.parent, None)
        if not gbpm__unx and arr_type == df_type.data[eavgy__vyh]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            nzs__ynvqr = context.nrt.meminfo_data(builder, pqe__vazwp.meminfo)
            egpi__opsf = context.get_value_type(payload_type).as_pointer()
            nzs__ynvqr = builder.bitcast(nzs__ynvqr, egpi__opsf)
            huuqg__hqea = get_dataframe_payload(context, builder, df_type,
                dsvbq__wxydh)
            builder.store(huuqg__hqea._getvalue(), nzs__ynvqr)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, yjlkx__ghme, builder.
                    extract_value(data_tup, 0))
            else:
                for lpn__szvvp, aqqzr__bpla in zip(vrxe__fve, aajdk__unltd):
                    context.nrt.incref(builder, aqqzr__bpla, lpn__szvvp)
        has_parent = cgutils.is_not_null(builder, pqe__vazwp.parent)
        with builder.if_then(has_parent):
            jdssx__cuf = context.get_python_api(builder)
            olh__qghw = jdssx__cuf.gil_ensure()
            ragcc__hfjn = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, psj__bcy)
            ymogs__eeuca = numba.core.pythonapi._BoxContext(context,
                builder, jdssx__cuf, ragcc__hfjn)
            aox__osp = ymogs__eeuca.pyapi.from_native_value(arr_type,
                psj__bcy, ymogs__eeuca.env_manager)
            if isinstance(col_name, str):
                uudwe__orc = context.insert_const_string(builder.module,
                    col_name)
                vrnm__hpya = jdssx__cuf.string_from_string(uudwe__orc)
            else:
                assert isinstance(col_name, int)
                vrnm__hpya = jdssx__cuf.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            jdssx__cuf.object_setitem(pqe__vazwp.parent, vrnm__hpya, aox__osp)
            jdssx__cuf.decref(aox__osp)
            jdssx__cuf.decref(vrnm__hpya)
            jdssx__cuf.gil_release(olh__qghw)
        return dsvbq__wxydh
    jthwu__omdp = DataFrameType(aajdk__unltd, index_typ, column_names,
        df_type.dist, df_type.is_table_format)
    sig = signature(jthwu__omdp, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    iylgk__ispxw = len(pyval.columns)
    vrxe__fve = []
    for i in range(iylgk__ispxw):
        frvk__nlnet = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            aox__osp = frvk__nlnet.array
        else:
            aox__osp = frvk__nlnet.values
        vrxe__fve.append(aox__osp)
    vrxe__fve = tuple(vrxe__fve)
    if df_type.is_table_format:
        ddbe__ynkek = context.get_constant_generic(builder, df_type.
            table_type, Table(vrxe__fve))
        data_tup = lir.Constant.literal_struct([ddbe__ynkek])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], wwzm__mfkx) for 
            i, wwzm__mfkx in enumerate(vrxe__fve)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    rqrsv__mqk = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, rqrsv__mqk])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    mwwc__vwx = context.get_constant(types.int64, -1)
    hvid__tujg = context.get_constant_null(types.voidptr)
    urb__pnwp = lir.Constant.literal_struct([mwwc__vwx, hvid__tujg,
        hvid__tujg, payload, mwwc__vwx])
    urb__pnwp = cgutils.global_constant(builder, '.const.meminfo', urb__pnwp
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([urb__pnwp, rqrsv__mqk])


@lower_cast(DataFrameType, DataFrameType)
def cast_df_to_df(context, builder, fromty, toty, val):
    if (fromty.data == toty.data and fromty.index == toty.index and fromty.
        columns == toty.columns and fromty.is_table_format == toty.
        is_table_format and fromty.dist != toty.dist and fromty.
        has_runtime_cols == toty.has_runtime_cols):
        return val
    if not fromty.has_runtime_cols and not toty.has_runtime_cols and len(fromty
        .data) == 0 and len(toty.columns):
        return _cast_empty_df(context, builder, toty)
    if len(fromty.data) != len(toty.data) or fromty.data != toty.data and any(
        context.typing_context.unify_pairs(fromty.data[i], toty.data[i]) is
        None for i in range(len(fromty.data))
        ) or fromty.has_runtime_cols != toty.has_runtime_cols:
        raise BodoError(f'Invalid dataframe cast from {fromty} to {toty}')
    in_dataframe_payload = get_dataframe_payload(context, builder, fromty, val)
    if isinstance(fromty.index, RangeIndexType) and isinstance(toty.index,
        NumericIndexType):
        jnnn__ruf = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        jnnn__ruf = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, jnnn__ruf)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        uiyat__hkv = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                uiyat__hkv)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), uiyat__hkv)
    elif not fromty.is_table_format and toty.is_table_format:
        uiyat__hkv = _cast_df_data_to_table_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        uiyat__hkv = _cast_df_data_to_tuple_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        uiyat__hkv = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        uiyat__hkv = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, uiyat__hkv,
        jnnn__ruf, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    dco__fop = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        ahg__mvotw = get_index_data_arr_types(toty.index)[0]
        erbbb__emyce = bodo.utils.transform.get_type_alloc_counts(ahg__mvotw
            ) - 1
        lgy__xtlb = ', '.join('0' for sjk__xtzu in range(erbbb__emyce))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(lgy__xtlb, ', ' if erbbb__emyce == 1 else ''))
        dco__fop['index_arr_type'] = ahg__mvotw
    basuj__nlyi = []
    for i, arr_typ in enumerate(toty.data):
        erbbb__emyce = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        lgy__xtlb = ', '.join('0' for sjk__xtzu in range(erbbb__emyce))
        gwpel__iirv = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'
            .format(i, lgy__xtlb, ', ' if erbbb__emyce == 1 else ''))
        basuj__nlyi.append(gwpel__iirv)
        dco__fop[f'arr_type{i}'] = arr_typ
    basuj__nlyi = ', '.join(basuj__nlyi)
    xky__bvn = 'def impl():\n'
    ubt__eioy = bodo.hiframes.dataframe_impl._gen_init_df(xky__bvn, toty.
        columns, basuj__nlyi, index, dco__fop)
    df = context.compile_internal(builder, ubt__eioy, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    lpmmi__pcs = toty.table_type
    ddbe__ynkek = cgutils.create_struct_proxy(lpmmi__pcs)(context, builder)
    ddbe__ynkek.parent = in_dataframe_payload.parent
    for ovtb__udqf, qzqd__qiuaj in lpmmi__pcs.type_to_blk.items():
        ygpvw__fddvf = context.get_constant(types.int64, len(lpmmi__pcs.
            block_to_arr_ind[qzqd__qiuaj]))
        sjk__xtzu, degeu__iyxw = ListInstance.allocate_ex(context, builder,
            types.List(ovtb__udqf), ygpvw__fddvf)
        degeu__iyxw.size = ygpvw__fddvf
        setattr(ddbe__ynkek, f'block_{qzqd__qiuaj}', degeu__iyxw.value)
    for i, ovtb__udqf in enumerate(fromty.data):
        zvnv__ragxd = toty.data[i]
        if ovtb__udqf != zvnv__ragxd:
            kjhp__paa = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*kjhp__paa)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        dtx__tcu = builder.extract_value(in_dataframe_payload.data, i)
        if ovtb__udqf != zvnv__ragxd:
            crbi__npv = context.cast(builder, dtx__tcu, ovtb__udqf, zvnv__ragxd
                )
            uziyi__nas = False
        else:
            crbi__npv = dtx__tcu
            uziyi__nas = True
        qzqd__qiuaj = lpmmi__pcs.type_to_blk[ovtb__udqf]
        wft__ntm = getattr(ddbe__ynkek, f'block_{qzqd__qiuaj}')
        ljel__por = ListInstance(context, builder, types.List(ovtb__udqf),
            wft__ntm)
        awcl__mmu = context.get_constant(types.int64, lpmmi__pcs.
            block_offsets[i])
        ljel__por.setitem(awcl__mmu, crbi__npv, uziyi__nas)
    data_tup = context.make_tuple(builder, types.Tuple([lpmmi__pcs]), [
        ddbe__ynkek._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    vrxe__fve = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            kjhp__paa = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*kjhp__paa)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            dtx__tcu = builder.extract_value(in_dataframe_payload.data, i)
            crbi__npv = context.cast(builder, dtx__tcu, fromty.data[i],
                toty.data[i])
            uziyi__nas = False
        else:
            crbi__npv = builder.extract_value(in_dataframe_payload.data, i)
            uziyi__nas = True
        if uziyi__nas:
            context.nrt.incref(builder, toty.data[i], crbi__npv)
        vrxe__fve.append(crbi__npv)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), vrxe__fve)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    mwkz__czh = fromty.table_type
    qdm__xiteo = cgutils.create_struct_proxy(mwkz__czh)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    yjlkx__ghme = toty.table_type
    nxjlk__yli = cgutils.create_struct_proxy(yjlkx__ghme)(context, builder)
    nxjlk__yli.parent = in_dataframe_payload.parent
    for ovtb__udqf, qzqd__qiuaj in yjlkx__ghme.type_to_blk.items():
        ygpvw__fddvf = context.get_constant(types.int64, len(yjlkx__ghme.
            block_to_arr_ind[qzqd__qiuaj]))
        sjk__xtzu, degeu__iyxw = ListInstance.allocate_ex(context, builder,
            types.List(ovtb__udqf), ygpvw__fddvf)
        degeu__iyxw.size = ygpvw__fddvf
        setattr(nxjlk__yli, f'block_{qzqd__qiuaj}', degeu__iyxw.value)
    for i in range(len(fromty.data)):
        isx__kpal = fromty.data[i]
        zvnv__ragxd = toty.data[i]
        if isx__kpal != zvnv__ragxd:
            kjhp__paa = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*kjhp__paa)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        oamt__vukuc = mwkz__czh.type_to_blk[isx__kpal]
        tnywh__hwpvt = getattr(qdm__xiteo, f'block_{oamt__vukuc}')
        cjx__tqqu = ListInstance(context, builder, types.List(isx__kpal),
            tnywh__hwpvt)
        faq__ywxm = context.get_constant(types.int64, mwkz__czh.
            block_offsets[i])
        dtx__tcu = cjx__tqqu.getitem(faq__ywxm)
        if isx__kpal != zvnv__ragxd:
            crbi__npv = context.cast(builder, dtx__tcu, isx__kpal, zvnv__ragxd)
            uziyi__nas = False
        else:
            crbi__npv = dtx__tcu
            uziyi__nas = True
        nkt__hzt = yjlkx__ghme.type_to_blk[ovtb__udqf]
        degeu__iyxw = getattr(nxjlk__yli, f'block_{nkt__hzt}')
        gjnm__hjp = ListInstance(context, builder, types.List(zvnv__ragxd),
            degeu__iyxw)
        cqgn__atmvo = context.get_constant(types.int64, yjlkx__ghme.
            block_offsets[i])
        gjnm__hjp.setitem(cqgn__atmvo, crbi__npv, uziyi__nas)
    data_tup = context.make_tuple(builder, types.Tuple([yjlkx__ghme]), [
        nxjlk__yli._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    lpmmi__pcs = fromty.table_type
    ddbe__ynkek = cgutils.create_struct_proxy(lpmmi__pcs)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    vrxe__fve = []
    for i, ovtb__udqf in enumerate(toty.data):
        isx__kpal = fromty.data[i]
        if ovtb__udqf != isx__kpal:
            kjhp__paa = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*kjhp__paa)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        qzqd__qiuaj = lpmmi__pcs.type_to_blk[ovtb__udqf]
        wft__ntm = getattr(ddbe__ynkek, f'block_{qzqd__qiuaj}')
        ljel__por = ListInstance(context, builder, types.List(ovtb__udqf),
            wft__ntm)
        awcl__mmu = context.get_constant(types.int64, lpmmi__pcs.
            block_offsets[i])
        dtx__tcu = ljel__por.getitem(awcl__mmu)
        if ovtb__udqf != isx__kpal:
            crbi__npv = context.cast(builder, dtx__tcu, isx__kpal, ovtb__udqf)
            uziyi__nas = False
        else:
            crbi__npv = dtx__tcu
            uziyi__nas = True
        if uziyi__nas:
            context.nrt.incref(builder, ovtb__udqf, crbi__npv)
        vrxe__fve.append(crbi__npv)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), vrxe__fve)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    ozd__tfc, basuj__nlyi, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    zgf__dgtwe = ColNamesMetaType(tuple(ozd__tfc))
    xky__bvn = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    xky__bvn += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(basuj__nlyi, index_arg))
    vpkt__gvz = {}
    exec(xky__bvn, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': zgf__dgtwe}, vpkt__gvz)
    xowj__bwdmq = vpkt__gvz['_init_df']
    return xowj__bwdmq


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    jthwu__omdp = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(jthwu__omdp, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    jthwu__omdp = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(jthwu__omdp, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    mpd__keun = ''
    if not is_overload_none(dtype):
        mpd__keun = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        iylgk__ispxw = (len(data.types) - 1) // 2
        isb__mqr = [ovtb__udqf.literal_value for ovtb__udqf in data.types[1
            :iylgk__ispxw + 1]]
        data_val_types = dict(zip(isb__mqr, data.types[iylgk__ispxw + 1:]))
        vrxe__fve = ['data[{}]'.format(i) for i in range(iylgk__ispxw + 1, 
            2 * iylgk__ispxw + 1)]
        data_dict = dict(zip(isb__mqr, vrxe__fve))
        if is_overload_none(index):
            for i, ovtb__udqf in enumerate(data.types[iylgk__ispxw + 1:]):
                if isinstance(ovtb__udqf, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(iylgk__ispxw + 1 + i))
                    index_is_none = False
                    break
    elif is_overload_none(data):
        data_dict = {}
        data_val_types = {}
    else:
        if not (isinstance(data, types.Array) and data.ndim == 2):
            raise BodoError(
                'pd.DataFrame() only supports constant dictionary and array input'
                )
        if is_overload_none(columns):
            raise BodoError(
                "pd.DataFrame() 'columns' argument is required when an array is passed as data"
                )
        fyypc__mloyx = '.copy()' if copy else ''
        fcff__bwj = get_overload_const_list(columns)
        iylgk__ispxw = len(fcff__bwj)
        data_val_types = {ymogs__eeuca: data.copy(ndim=1) for ymogs__eeuca in
            fcff__bwj}
        vrxe__fve = ['data[:,{}]{}'.format(i, fyypc__mloyx) for i in range(
            iylgk__ispxw)]
        data_dict = dict(zip(fcff__bwj, vrxe__fve))
    if is_overload_none(columns):
        col_names = data_dict.keys()
    else:
        col_names = get_overload_const_list(columns)
    df_len = _get_df_len_from_info(data_dict, data_val_types, col_names,
        index_is_none, index_arg)
    _fill_null_arrays(data_dict, col_names, df_len, dtype)
    if index_is_none:
        if is_overload_none(data):
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_binary_str_index(bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0))'
                )
        else:
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, {}, 1, None)'
                .format(df_len))
    basuj__nlyi = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[ymogs__eeuca], df_len, mpd__keun) for
        ymogs__eeuca in col_names))
    if len(col_names) == 0:
        basuj__nlyi = '()'
    return col_names, basuj__nlyi, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for ymogs__eeuca in col_names:
        if ymogs__eeuca in data_dict and is_iterable_type(data_val_types[
            ymogs__eeuca]):
            df_len = 'len({})'.format(data_dict[ymogs__eeuca])
            break
    if df_len == '0':
        if not index_is_none:
            df_len = f'len({index_arg})'
        elif data_dict:
            raise BodoError(
                'Internal Error: Unable to determine length of DataFrame Index. If this is unexpected, please try passing an index value.'
                )
    return df_len


def _fill_null_arrays(data_dict, col_names, df_len, dtype):
    if all(ymogs__eeuca in data_dict for ymogs__eeuca in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    oihu__dszry = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for ymogs__eeuca in col_names:
        if ymogs__eeuca not in data_dict:
            data_dict[ymogs__eeuca] = oihu__dszry


@infer_global(len)
class LenTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        if isinstance(args[0], (DataFrameType, bodo.TableType)):
            return types.int64(*args)


@lower_builtin(len, DataFrameType)
def table_len_lower(context, builder, sig, args):
    impl = df_len_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def df_len_overload(df):
    if not isinstance(df, DataFrameType):
        return
    if df.has_runtime_cols:

        def impl(df):
            if is_null_pointer(df._meminfo):
                return 0
            ovtb__udqf = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(ovtb__udqf)
        return impl
    if len(df.columns) == 0:

        def impl(df):
            if is_null_pointer(df._meminfo):
                return 0
            return len(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
        return impl

    def impl(df):
        if is_null_pointer(df._meminfo):
            return 0
        return len(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, 0))
    return impl


@infer_global(operator.getitem)
class GetItemTuple(AbstractTemplate):
    key = operator.getitem

    def generic(self, args, kws):
        tup, idx = args
        if not isinstance(tup, types.BaseTuple) or not isinstance(idx,
            types.IntegerLiteral):
            return
        ghh__xzttz = idx.literal_value
        if isinstance(ghh__xzttz, int):
            iml__yxr = tup.types[ghh__xzttz]
        elif isinstance(ghh__xzttz, slice):
            iml__yxr = types.BaseTuple.from_types(tup.types[ghh__xzttz])
        return signature(iml__yxr, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    ghgd__ryap, idx = sig.args
    idx = idx.literal_value
    tup, sjk__xtzu = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(ghgd__ryap)
        if not 0 <= idx < len(ghgd__ryap):
            raise IndexError('cannot index at %d in %s' % (idx, ghgd__ryap))
        bjtr__jkfo = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        rsdfb__fntky = cgutils.unpack_tuple(builder, tup)[idx]
        bjtr__jkfo = context.make_tuple(builder, sig.return_type, rsdfb__fntky)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, bjtr__jkfo)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, tqx__tkdpl, suffix_x,
            suffix_y, is_join, indicator, sjk__xtzu, sjk__xtzu) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        tcmms__zpd = {ymogs__eeuca: i for i, ymogs__eeuca in enumerate(left_on)
            }
        bsuj__haf = {ymogs__eeuca: i for i, ymogs__eeuca in enumerate(right_on)
            }
        mmvs__nep = set(left_on) & set(right_on)
        lvvcg__deiwt = set(left_df.columns) & set(right_df.columns)
        ikn__dgn = lvvcg__deiwt - mmvs__nep
        jqnw__dod = '$_bodo_index_' in left_on
        jdp__wrlq = '$_bodo_index_' in right_on
        how = get_overload_const_str(tqx__tkdpl)
        lge__hzx = how in {'left', 'outer'}
        jaz__pegx = how in {'right', 'outer'}
        columns = []
        data = []
        if jqnw__dod:
            goliq__oqz = bodo.utils.typing.get_index_data_arr_types(left_df
                .index)[0]
        else:
            goliq__oqz = left_df.data[left_df.column_index[left_on[0]]]
        if jdp__wrlq:
            umu__vnwwp = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            umu__vnwwp = right_df.data[right_df.column_index[right_on[0]]]
        if jqnw__dod and not jdp__wrlq and not is_join.literal_value:
            tmt__wxri = right_on[0]
            if tmt__wxri in left_df.column_index:
                columns.append(tmt__wxri)
                if (umu__vnwwp == bodo.dict_str_arr_type and goliq__oqz ==
                    bodo.string_array_type):
                    ucy__fkzrr = bodo.string_array_type
                else:
                    ucy__fkzrr = umu__vnwwp
                data.append(ucy__fkzrr)
        if jdp__wrlq and not jqnw__dod and not is_join.literal_value:
            ppxcx__nfafg = left_on[0]
            if ppxcx__nfafg in right_df.column_index:
                columns.append(ppxcx__nfafg)
                if (goliq__oqz == bodo.dict_str_arr_type and umu__vnwwp ==
                    bodo.string_array_type):
                    ucy__fkzrr = bodo.string_array_type
                else:
                    ucy__fkzrr = goliq__oqz
                data.append(ucy__fkzrr)
        for isx__kpal, frvk__nlnet in zip(left_df.data, left_df.columns):
            columns.append(str(frvk__nlnet) + suffix_x.literal_value if 
                frvk__nlnet in ikn__dgn else frvk__nlnet)
            if frvk__nlnet in mmvs__nep:
                if isx__kpal == bodo.dict_str_arr_type:
                    isx__kpal = right_df.data[right_df.column_index[
                        frvk__nlnet]]
                data.append(isx__kpal)
            else:
                if (isx__kpal == bodo.dict_str_arr_type and frvk__nlnet in
                    tcmms__zpd):
                    if jdp__wrlq:
                        isx__kpal = umu__vnwwp
                    else:
                        arbs__gro = tcmms__zpd[frvk__nlnet]
                        vizyd__jpbue = right_on[arbs__gro]
                        isx__kpal = right_df.data[right_df.column_index[
                            vizyd__jpbue]]
                if jaz__pegx:
                    isx__kpal = to_nullable_type(isx__kpal)
                data.append(isx__kpal)
        for isx__kpal, frvk__nlnet in zip(right_df.data, right_df.columns):
            if frvk__nlnet not in mmvs__nep:
                columns.append(str(frvk__nlnet) + suffix_y.literal_value if
                    frvk__nlnet in ikn__dgn else frvk__nlnet)
                if (isx__kpal == bodo.dict_str_arr_type and frvk__nlnet in
                    bsuj__haf):
                    if jqnw__dod:
                        isx__kpal = goliq__oqz
                    else:
                        arbs__gro = bsuj__haf[frvk__nlnet]
                        ynj__lxku = left_on[arbs__gro]
                        isx__kpal = left_df.data[left_df.column_index[
                            ynj__lxku]]
                if lge__hzx:
                    isx__kpal = to_nullable_type(isx__kpal)
                data.append(isx__kpal)
        upqk__skx = get_overload_const_bool(indicator)
        if upqk__skx:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        obo__clxgn = False
        if jqnw__dod and jdp__wrlq and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            obo__clxgn = True
        elif jqnw__dod and not jdp__wrlq:
            index_typ = right_df.index
            obo__clxgn = True
        elif jdp__wrlq and not jqnw__dod:
            index_typ = left_df.index
            obo__clxgn = True
        if obo__clxgn and isinstance(index_typ, bodo.hiframes.pd_index_ext.
            RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        fnlq__dpbyq = DataFrameType(tuple(data), index_typ, tuple(columns),
            is_table_format=True)
        return signature(fnlq__dpbyq, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    ocsdo__tvvfz = cgutils.create_struct_proxy(sig.return_type)(context,
        builder)
    return ocsdo__tvvfz._getvalue()


@overload(pd.concat, inline='always', no_unliteral=True)
def concat_overload(objs, axis=0, join='outer', join_axes=None,
    ignore_index=False, keys=None, levels=None, names=None,
    verify_integrity=False, sort=None, copy=True):
    if not is_overload_constant_int(axis):
        raise BodoError("pd.concat(): 'axis' should be a constant integer")
    if not is_overload_constant_bool(ignore_index):
        raise BodoError(
            "pd.concat(): 'ignore_index' should be a constant boolean")
    axis = get_overload_const_int(axis)
    ignore_index = is_overload_true(ignore_index)
    ilq__rbp = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    iniay__paal = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', ilq__rbp, iniay__paal,
        package_name='pandas', module_name='General')
    xky__bvn = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        jsudf__jxpzs = 0
        basuj__nlyi = []
        names = []
        for i, snr__rvf in enumerate(objs.types):
            assert isinstance(snr__rvf, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(snr__rvf, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(snr__rvf,
                'pandas.concat()')
            if isinstance(snr__rvf, SeriesType):
                names.append(str(jsudf__jxpzs))
                jsudf__jxpzs += 1
                basuj__nlyi.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(snr__rvf.columns)
                for ccta__jckz in range(len(snr__rvf.data)):
                    basuj__nlyi.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, ccta__jckz))
        return bodo.hiframes.dataframe_impl._gen_init_df(xky__bvn, names,
            ', '.join(basuj__nlyi), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(ovtb__udqf, DataFrameType) for ovtb__udqf in
            objs.types)
        eqnmo__qpz = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            eqnmo__qpz.extend(df.columns)
        eqnmo__qpz = list(dict.fromkeys(eqnmo__qpz).keys())
        bauc__hjrow = {}
        for jsudf__jxpzs, ymogs__eeuca in enumerate(eqnmo__qpz):
            for i, df in enumerate(objs.types):
                if ymogs__eeuca in df.column_index:
                    bauc__hjrow[f'arr_typ{jsudf__jxpzs}'] = df.data[df.
                        column_index[ymogs__eeuca]]
                    break
        assert len(bauc__hjrow) == len(eqnmo__qpz)
        kqsd__jcb = []
        for jsudf__jxpzs, ymogs__eeuca in enumerate(eqnmo__qpz):
            args = []
            for i, df in enumerate(objs.types):
                if ymogs__eeuca in df.column_index:
                    eavgy__vyh = df.column_index[ymogs__eeuca]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, eavgy__vyh))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, jsudf__jxpzs))
            xky__bvn += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'.
                format(jsudf__jxpzs, ', '.join(args)))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(A0), 1, None)'
                )
        else:
            index = (
                """bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)) if len(objs[i].
                columns) > 0)))
        return bodo.hiframes.dataframe_impl._gen_init_df(xky__bvn,
            eqnmo__qpz, ', '.join('A{}'.format(i) for i in range(len(
            eqnmo__qpz))), index, bauc__hjrow)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(ovtb__udqf, SeriesType) for ovtb__udqf in
            objs.types)
        xky__bvn += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'.
            format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            xky__bvn += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            xky__bvn += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        xky__bvn += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        vpkt__gvz = {}
        exec(xky__bvn, {'bodo': bodo, 'np': np, 'numba': numba}, vpkt__gvz)
        return vpkt__gvz['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for jsudf__jxpzs, ymogs__eeuca in enumerate(df_type.columns):
            xky__bvn += '  arrs{} = []\n'.format(jsudf__jxpzs)
            xky__bvn += '  for i in range(len(objs)):\n'
            xky__bvn += '    df = objs[i]\n'
            xky__bvn += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(jsudf__jxpzs))
            xky__bvn += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(jsudf__jxpzs))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            xky__bvn += '  arrs_index = []\n'
            xky__bvn += '  for i in range(len(objs)):\n'
            xky__bvn += '    df = objs[i]\n'
            xky__bvn += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(xky__bvn, df_type.
            columns, ', '.join('out_arr{}'.format(i) for i in range(len(
            df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        xky__bvn += '  arrs = []\n'
        xky__bvn += '  for i in range(len(objs)):\n'
        xky__bvn += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        xky__bvn += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            xky__bvn += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            xky__bvn += '  arrs_index = []\n'
            xky__bvn += '  for i in range(len(objs)):\n'
            xky__bvn += '    S = objs[i]\n'
            xky__bvn += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            xky__bvn += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        xky__bvn += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        vpkt__gvz = {}
        exec(xky__bvn, {'bodo': bodo, 'np': np, 'numba': numba}, vpkt__gvz)
        return vpkt__gvz['impl']
    raise BodoError('pd.concat(): input type {} not supported yet'.format(objs)
        )


def sort_values_dummy(df, by, ascending, inplace, na_position):
    return df.sort_values(by, ascending=ascending, inplace=inplace,
        na_position=na_position)


@infer_global(sort_values_dummy)
class SortDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, by, ascending, inplace, na_position = args
        index = df.index
        if isinstance(index, bodo.hiframes.pd_index_ext.RangeIndexType):
            index = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64)
        jthwu__omdp = df.copy(index=index)
        return signature(jthwu__omdp, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    bpls__ytu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return bpls__ytu._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    ilq__rbp = dict(index=index, name=name)
    iniay__paal = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', ilq__rbp, iniay__paal,
        package_name='pandas', module_name='DataFrame')

    def _impl(df, index=True, name='Pandas'):
        return bodo.hiframes.pd_dataframe_ext.itertuples_dummy(df)
    return _impl


def itertuples_dummy(df):
    return df


@infer_global(itertuples_dummy)
class ItertuplesDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, = args
        assert 'Index' not in df.columns
        columns = ('Index',) + df.columns
        bauc__hjrow = (types.Array(types.int64, 1, 'C'),) + df.data
        xzpmg__mqag = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, bauc__hjrow)
        return signature(xzpmg__mqag, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    bpls__ytu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return bpls__ytu._getvalue()


def query_dummy(df, expr):
    return df.eval(expr)


@infer_global(query_dummy)
class QueryDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=RangeIndexType(types
            .none)), *args)


@lower_builtin(query_dummy, types.VarArg(types.Any))
def lower_query_dummy(context, builder, sig, args):
    bpls__ytu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return bpls__ytu._getvalue()


def val_isin_dummy(S, vals):
    return S in vals


def val_notin_dummy(S, vals):
    return S not in vals


@infer_global(val_isin_dummy)
@infer_global(val_notin_dummy)
class ValIsinTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=args[0].index), *args)


@lower_builtin(val_isin_dummy, types.VarArg(types.Any))
@lower_builtin(val_notin_dummy, types.VarArg(types.Any))
def lower_val_isin_dummy(context, builder, sig, args):
    bpls__ytu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return bpls__ytu._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    lcukl__eof = get_overload_const_bool(check_duplicates)
    ovjp__niys = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    aox__bobc = len(value_names) > 1
    kvx__ybmux = None
    hrlm__pcwat = None
    gjh__iydfq = None
    hswyy__xsjz = None
    ccbqk__mpy = isinstance(values_tup, types.UniTuple)
    if ccbqk__mpy:
        hnj__qyy = [to_str_arr_if_dict_array(to_nullable_type(values_tup.
            dtype))]
    else:
        hnj__qyy = [to_str_arr_if_dict_array(to_nullable_type(aqqzr__bpla)) for
            aqqzr__bpla in values_tup]
    xky__bvn = 'def impl(\n'
    xky__bvn += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, _constant_pivot_values=None, parallel=False
"""
    xky__bvn += '):\n'
    xky__bvn += '    if parallel:\n'
    umg__brwk = ', '.join([f'array_to_info(index_tup[{i}])' for i in range(
        len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for i in
        range(len(columns_tup))] + [f'array_to_info(values_tup[{i}])' for i in
        range(len(values_tup))])
    xky__bvn += f'        info_list = [{umg__brwk}]\n'
    xky__bvn += '        cpp_table = arr_info_list_to_table(info_list)\n'
    xky__bvn += (
        f'        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)\n'
        )
    znyj__oqa = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
         for i in range(len(index_tup))])
    sqcr__dgd = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
         for i in range(len(columns_tup))])
    danay__xbxb = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
         for i in range(len(values_tup))])
    xky__bvn += f'        index_tup = ({znyj__oqa},)\n'
    xky__bvn += f'        columns_tup = ({sqcr__dgd},)\n'
    xky__bvn += f'        values_tup = ({danay__xbxb},)\n'
    xky__bvn += '        delete_table(cpp_table)\n'
    xky__bvn += '        delete_table(out_cpp_table)\n'
    xky__bvn += '    columns_arr = columns_tup[0]\n'
    if ccbqk__mpy:
        xky__bvn += '    values_arrs = [arr for arr in values_tup]\n'
    dqnmx__ckeon = ', '.join([
        f'bodo.utils.typing.decode_if_dict_array(index_tup[{i}])' for i in
        range(len(index_tup))])
    xky__bvn += f'    new_index_tup = ({dqnmx__ckeon},)\n'
    xky__bvn += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    xky__bvn += '        new_index_tup\n'
    xky__bvn += '    )\n'
    xky__bvn += '    n_rows = len(unique_index_arr_tup[0])\n'
    xky__bvn += '    num_values_arrays = len(values_tup)\n'
    xky__bvn += '    n_unique_pivots = len(pivot_values)\n'
    if ccbqk__mpy:
        xky__bvn += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        xky__bvn += '    n_cols = n_unique_pivots\n'
    xky__bvn += '    col_map = {}\n'
    xky__bvn += '    for i in range(n_unique_pivots):\n'
    xky__bvn += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    xky__bvn += '            raise ValueError(\n'
    xky__bvn += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    xky__bvn += '            )\n'
    xky__bvn += '        col_map[pivot_values[i]] = i\n'
    wic__lbva = False
    for i, hfpqq__jknu in enumerate(hnj__qyy):
        if is_str_arr_type(hfpqq__jknu):
            wic__lbva = True
            xky__bvn += (
                f'    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]\n'
                )
            xky__bvn += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if wic__lbva:
        if lcukl__eof:
            xky__bvn += '    nbytes = (n_rows + 7) >> 3\n'
            xky__bvn += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        xky__bvn += '    for i in range(len(columns_arr)):\n'
        xky__bvn += '        col_name = columns_arr[i]\n'
        xky__bvn += '        pivot_idx = col_map[col_name]\n'
        xky__bvn += '        row_idx = row_vector[i]\n'
        if lcukl__eof:
            xky__bvn += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            xky__bvn += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            xky__bvn += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            xky__bvn += '        else:\n'
            xky__bvn += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if ccbqk__mpy:
            xky__bvn += '        for j in range(num_values_arrays):\n'
            xky__bvn += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            xky__bvn += '            len_arr = len_arrs_0[col_idx]\n'
            xky__bvn += '            values_arr = values_arrs[j]\n'
            xky__bvn += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            xky__bvn += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            xky__bvn += '                len_arr[row_idx] = str_val_len\n'
            xky__bvn += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, hfpqq__jknu in enumerate(hnj__qyy):
                if is_str_arr_type(hfpqq__jknu):
                    xky__bvn += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    xky__bvn += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    xky__bvn += (
                        f'            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}\n'
                        )
                    xky__bvn += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    for i, hfpqq__jknu in enumerate(hnj__qyy):
        if is_str_arr_type(hfpqq__jknu):
            xky__bvn += f'    data_arrs_{i} = [\n'
            xky__bvn += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            xky__bvn += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            xky__bvn += '        )\n'
            xky__bvn += '        for i in range(n_cols)\n'
            xky__bvn += '    ]\n'
        else:
            xky__bvn += f'    data_arrs_{i} = [\n'
            xky__bvn += (
                f'        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})\n'
                )
            xky__bvn += '        for _ in range(n_cols)\n'
            xky__bvn += '    ]\n'
    if not wic__lbva and lcukl__eof:
        xky__bvn += '    nbytes = (n_rows + 7) >> 3\n'
        xky__bvn += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    xky__bvn += '    for i in range(len(columns_arr)):\n'
    xky__bvn += '        col_name = columns_arr[i]\n'
    xky__bvn += '        pivot_idx = col_map[col_name]\n'
    xky__bvn += '        row_idx = row_vector[i]\n'
    if not wic__lbva and lcukl__eof:
        xky__bvn += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        xky__bvn += (
            '        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):\n'
            )
        xky__bvn += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        xky__bvn += '        else:\n'
        xky__bvn += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if ccbqk__mpy:
        xky__bvn += '        for j in range(num_values_arrays):\n'
        xky__bvn += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        xky__bvn += '            col_arr = data_arrs_0[col_idx]\n'
        xky__bvn += '            values_arr = values_arrs[j]\n'
        xky__bvn += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        xky__bvn += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        xky__bvn += '            else:\n'
        xky__bvn += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, hfpqq__jknu in enumerate(hnj__qyy):
            xky__bvn += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            xky__bvn += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            xky__bvn += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            xky__bvn += f'        else:\n'
            xky__bvn += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        xky__bvn += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        kvx__ybmux = index_names.meta[0]
    else:
        xky__bvn += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        kvx__ybmux = tuple(index_names.meta)
    if not ovjp__niys:
        gjh__iydfq = columns_name.meta[0]
        if aox__bobc:
            xky__bvn += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            hrlm__pcwat = value_names.meta
            if all(isinstance(ymogs__eeuca, str) for ymogs__eeuca in
                hrlm__pcwat):
                hrlm__pcwat = pd.array(hrlm__pcwat, 'string')
            elif all(isinstance(ymogs__eeuca, int) for ymogs__eeuca in
                hrlm__pcwat):
                hrlm__pcwat = np.array(hrlm__pcwat, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(hrlm__pcwat.dtype, pd.StringDtype):
                xky__bvn += '    total_chars = 0\n'
                xky__bvn += f'    for i in range({len(value_names)}):\n'
                xky__bvn += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                xky__bvn += '        total_chars += value_name_str_len\n'
                xky__bvn += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                xky__bvn += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                xky__bvn += '    total_chars = 0\n'
                xky__bvn += '    for i in range(len(pivot_values)):\n'
                xky__bvn += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                xky__bvn += '        total_chars += pivot_val_str_len\n'
                xky__bvn += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                xky__bvn += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            xky__bvn += f'    for i in range({len(value_names)}):\n'
            xky__bvn += '        for j in range(len(pivot_values)):\n'
            xky__bvn += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            xky__bvn += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            xky__bvn += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            xky__bvn += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    lpmmi__pcs = None
    if ovjp__niys:
        if aox__bobc:
            cyjsc__mpw = []
            for csnd__kfm in _constant_pivot_values.meta:
                for bgvgu__axdx in value_names.meta:
                    cyjsc__mpw.append((csnd__kfm, bgvgu__axdx))
            column_names = tuple(cyjsc__mpw)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        hswyy__xsjz = ColNamesMetaType(column_names)
        trpzh__iaq = []
        for aqqzr__bpla in hnj__qyy:
            trpzh__iaq.extend([aqqzr__bpla] * len(_constant_pivot_values))
        rqni__npkkq = tuple(trpzh__iaq)
        lpmmi__pcs = TableType(rqni__npkkq)
        xky__bvn += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        xky__bvn += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, aqqzr__bpla in enumerate(hnj__qyy):
            xky__bvn += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {lpmmi__pcs.type_to_blk[aqqzr__bpla]})
"""
        xky__bvn += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        xky__bvn += '        (table,), index, columns_typ\n'
        xky__bvn += '    )\n'
    else:
        xwklb__wzkdi = ', '.join(f'data_arrs_{i}' for i in range(len(hnj__qyy))
            )
        xky__bvn += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({xwklb__wzkdi},), n_rows)
"""
        xky__bvn += (
            '    return bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
            )
        xky__bvn += '        (table,), index, column_index\n'
        xky__bvn += '    )\n'
    vpkt__gvz = {}
    rcsv__awx = {f'data_arr_typ_{i}': hfpqq__jknu for i, hfpqq__jknu in
        enumerate(hnj__qyy)}
    uabci__wlk = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        lpmmi__pcs, 'columns_typ': hswyy__xsjz, 'index_names_lit':
        kvx__ybmux, 'value_names_lit': hrlm__pcwat, 'columns_name_lit':
        gjh__iydfq, **rcsv__awx}
    exec(xky__bvn, uabci__wlk, vpkt__gvz)
    impl = vpkt__gvz['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    pzu__sucdk = {}
    pzu__sucdk['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, zjjrz__cpgwa in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        eajpt__ldnk = None
        if isinstance(zjjrz__cpgwa, bodo.DatetimeArrayType):
            svjgp__pepp = 'datetimetz'
            fkb__jwmca = 'datetime64[ns]'
            if isinstance(zjjrz__cpgwa.tz, int):
                eeh__xsu = bodo.libs.pd_datetime_arr_ext.nanoseconds_to_offset(
                    zjjrz__cpgwa.tz)
            else:
                eeh__xsu = pd.DatetimeTZDtype(tz=zjjrz__cpgwa.tz).tz
            eajpt__ldnk = {'timezone': pa.lib.tzinfo_to_string(eeh__xsu)}
        elif isinstance(zjjrz__cpgwa, types.Array
            ) or zjjrz__cpgwa == boolean_array:
            svjgp__pepp = fkb__jwmca = zjjrz__cpgwa.dtype.name
            if fkb__jwmca.startswith('datetime'):
                svjgp__pepp = 'datetime'
        elif is_str_arr_type(zjjrz__cpgwa):
            svjgp__pepp = 'unicode'
            fkb__jwmca = 'object'
        elif zjjrz__cpgwa == binary_array_type:
            svjgp__pepp = 'bytes'
            fkb__jwmca = 'object'
        elif isinstance(zjjrz__cpgwa, DecimalArrayType):
            svjgp__pepp = fkb__jwmca = 'object'
        elif isinstance(zjjrz__cpgwa, IntegerArrayType):
            aps__swp = zjjrz__cpgwa.dtype.name
            if aps__swp.startswith('int'):
                svjgp__pepp = 'Int' + aps__swp[3:]
            elif aps__swp.startswith('uint'):
                svjgp__pepp = 'UInt' + aps__swp[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, zjjrz__cpgwa))
            fkb__jwmca = zjjrz__cpgwa.dtype.name
        elif zjjrz__cpgwa == datetime_date_array_type:
            svjgp__pepp = 'datetime'
            fkb__jwmca = 'object'
        elif isinstance(zjjrz__cpgwa, (StructArrayType, ArrayItemArrayType)):
            svjgp__pepp = 'object'
            fkb__jwmca = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, zjjrz__cpgwa))
        bvut__liee = {'name': col_name, 'field_name': col_name,
            'pandas_type': svjgp__pepp, 'numpy_type': fkb__jwmca,
            'metadata': eajpt__ldnk}
        pzu__sucdk['columns'].append(bvut__liee)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            qsojx__qelcs = '__index_level_0__'
            ubkap__qsecd = None
        else:
            qsojx__qelcs = '%s'
            ubkap__qsecd = '%s'
        pzu__sucdk['index_columns'] = [qsojx__qelcs]
        pzu__sucdk['columns'].append({'name': ubkap__qsecd, 'field_name':
            qsojx__qelcs, 'pandas_type': index.pandas_type_name,
            'numpy_type': index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        pzu__sucdk['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        pzu__sucdk['index_columns'] = []
    pzu__sucdk['pandas_version'] = pd.__version__
    return pzu__sucdk


@overload_method(DataFrameType, 'to_parquet', no_unliteral=True)
def to_parquet_overload(df, path, engine='auto', compression='snappy',
    index=None, partition_cols=None, storage_options=None, row_group_size=-
    1, _is_parallel=False):
    check_unsupported_args('DataFrame.to_parquet', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if df.has_runtime_cols and not is_overload_none(partition_cols):
        raise BodoError(
            f"DataFrame.to_parquet(): Providing 'partition_cols' on DataFrames with columns determined at runtime is not yet supported. Please return the DataFrame to regular Python to update typing information."
            )
    if not is_overload_none(engine) and get_overload_const_str(engine) not in (
        'auto', 'pyarrow'):
        raise BodoError('DataFrame.to_parquet(): only pyarrow engine supported'
            )
    if not is_overload_none(compression) and get_overload_const_str(compression
        ) not in {'snappy', 'gzip', 'brotli'}:
        raise BodoError('to_parquet(): Unsupported compression: ' + str(
            get_overload_const_str(compression)))
    if not is_overload_none(partition_cols):
        partition_cols = get_overload_const_list(partition_cols)
        ktkv__gwcrn = []
        for mpims__gnex in partition_cols:
            try:
                idx = df.columns.index(mpims__gnex)
            except ValueError as pnsg__lswsu:
                raise BodoError(
                    f'Partition column {mpims__gnex} is not in dataframe')
            ktkv__gwcrn.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    oyov__jqo = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType)
    zxcys__ocawk = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not oyov__jqo)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not oyov__jqo or is_overload_true
        (_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and oyov__jqo and not is_overload_true(_is_parallel)
    if df.has_runtime_cols:
        if isinstance(df.runtime_colname_typ, MultiIndexType):
            raise BodoError(
                'DataFrame.to_parquet(): Not supported with MultiIndex runtime column names. Please return the DataFrame to regular Python to update typing information.'
                )
        if not isinstance(df.runtime_colname_typ, bodo.hiframes.
            pd_index_ext.StringIndexType):
            raise BodoError(
                'DataFrame.to_parquet(): parquet must have string column names. Please return the DataFrame with runtime column names to regular Python to modify column names.'
                )
        zcb__dxot = df.runtime_data_types
        gdlwi__xxr = len(zcb__dxot)
        eajpt__ldnk = gen_pandas_parquet_metadata([''] * gdlwi__xxr,
            zcb__dxot, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        prf__bnh = eajpt__ldnk['columns'][:gdlwi__xxr]
        eajpt__ldnk['columns'] = eajpt__ldnk['columns'][gdlwi__xxr:]
        prf__bnh = [json.dumps(kniw__sxnz).replace('""', '{0}') for
            kniw__sxnz in prf__bnh]
        qla__hnrc = json.dumps(eajpt__ldnk)
        csd__arrj = '"columns": ['
        pzvfq__mffge = qla__hnrc.find(csd__arrj)
        if pzvfq__mffge == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        ggij__jafln = pzvfq__mffge + len(csd__arrj)
        axwvm__geni = qla__hnrc[:ggij__jafln]
        qla__hnrc = qla__hnrc[ggij__jafln:]
        cdp__dago = len(eajpt__ldnk['columns'])
    else:
        qla__hnrc = json.dumps(gen_pandas_parquet_metadata(df.columns, df.
            data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and oyov__jqo:
        qla__hnrc = qla__hnrc.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            qla__hnrc = qla__hnrc.replace('"%s"', '%s')
    if not df.is_table_format:
        basuj__nlyi = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    xky__bvn = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _is_parallel=False):
"""
    if df.is_table_format:
        xky__bvn += '    py_table = get_dataframe_table(df)\n'
        xky__bvn += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        xky__bvn += '    info_list = [{}]\n'.format(basuj__nlyi)
        xky__bvn += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        xky__bvn += '    columns_index = get_dataframe_column_names(df)\n'
        xky__bvn += '    names_arr = index_to_array(columns_index)\n'
        xky__bvn += '    col_names = array_to_info(names_arr)\n'
    else:
        xky__bvn += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and zxcys__ocawk:
        xky__bvn += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        nivqc__wfoc = True
    else:
        xky__bvn += '    index_col = array_to_info(np.empty(0))\n'
        nivqc__wfoc = False
    if df.has_runtime_cols:
        xky__bvn += '    columns_lst = []\n'
        xky__bvn += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            xky__bvn += f'    for _ in range(len(py_table.block_{i})):\n'
            xky__bvn += f"""        columns_lst.append({prf__bnh[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            xky__bvn += '        num_cols += 1\n'
        if cdp__dago:
            xky__bvn += "    columns_lst.append('')\n"
        xky__bvn += '    columns_str = ", ".join(columns_lst)\n'
        xky__bvn += ('    metadata = """' + axwvm__geni +
            '""" + columns_str + """' + qla__hnrc + '"""\n')
    else:
        xky__bvn += '    metadata = """' + qla__hnrc + '"""\n'
    xky__bvn += '    if compression is None:\n'
    xky__bvn += "        compression = 'none'\n"
    xky__bvn += '    if df.index.name is not None:\n'
    xky__bvn += '        name_ptr = df.index.name\n'
    xky__bvn += '    else:\n'
    xky__bvn += "        name_ptr = 'null'\n"
    xky__bvn += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    wdmrw__kal = None
    if partition_cols:
        wdmrw__kal = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        istzh__eih = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in ktkv__gwcrn)
        if istzh__eih:
            xky__bvn += '    cat_info_list = [{}]\n'.format(istzh__eih)
            xky__bvn += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            xky__bvn += '    cat_table = table\n'
        xky__bvn += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        xky__bvn += (
            f'    part_cols_idxs = np.array({ktkv__gwcrn}, dtype=np.int32)\n')
        xky__bvn += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        xky__bvn += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        xky__bvn += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        xky__bvn += (
            '                            unicode_to_utf8(compression),\n')
        xky__bvn += '                            _is_parallel,\n'
        xky__bvn += (
            '                            unicode_to_utf8(bucket_region),\n')
        xky__bvn += '                            row_group_size)\n'
        xky__bvn += '    delete_table_decref_arrays(table)\n'
        xky__bvn += '    delete_info_decref_array(index_col)\n'
        xky__bvn += '    delete_info_decref_array(col_names_no_partitions)\n'
        xky__bvn += '    delete_info_decref_array(col_names)\n'
        if istzh__eih:
            xky__bvn += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        xky__bvn += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        xky__bvn += (
            '                            table, col_names, index_col,\n')
        xky__bvn += '                            ' + str(nivqc__wfoc) + ',\n'
        xky__bvn += '                            unicode_to_utf8(metadata),\n'
        xky__bvn += (
            '                            unicode_to_utf8(compression),\n')
        xky__bvn += (
            '                            _is_parallel, 1, df.index.start,\n')
        xky__bvn += (
            '                            df.index.stop, df.index.step,\n')
        xky__bvn += '                            unicode_to_utf8(name_ptr),\n'
        xky__bvn += (
            '                            unicode_to_utf8(bucket_region),\n')
        xky__bvn += '                            row_group_size)\n'
        xky__bvn += '    delete_table_decref_arrays(table)\n'
        xky__bvn += '    delete_info_decref_array(index_col)\n'
        xky__bvn += '    delete_info_decref_array(col_names)\n'
    else:
        xky__bvn += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        xky__bvn += (
            '                            table, col_names, index_col,\n')
        xky__bvn += '                            ' + str(nivqc__wfoc) + ',\n'
        xky__bvn += '                            unicode_to_utf8(metadata),\n'
        xky__bvn += (
            '                            unicode_to_utf8(compression),\n')
        xky__bvn += '                            _is_parallel, 0, 0, 0, 0,\n'
        xky__bvn += '                            unicode_to_utf8(name_ptr),\n'
        xky__bvn += (
            '                            unicode_to_utf8(bucket_region),\n')
        xky__bvn += '                            row_group_size)\n'
        xky__bvn += '    delete_table_decref_arrays(table)\n'
        xky__bvn += '    delete_info_decref_array(index_col)\n'
        xky__bvn += '    delete_info_decref_array(col_names)\n'
    vpkt__gvz = {}
    if df.has_runtime_cols:
        mhkv__bfgqi = None
    else:
        for frvk__nlnet in df.columns:
            if not isinstance(frvk__nlnet, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        mhkv__bfgqi = pd.array(df.columns)
    exec(xky__bvn, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': mhkv__bfgqi,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': wdmrw__kal, 'get_dataframe_column_names':
        get_dataframe_column_names, 'fix_arr_dtype': fix_arr_dtype,
        'decode_if_dict_array': decode_if_dict_array,
        'decode_if_dict_table': decode_if_dict_table}, vpkt__gvz)
    dao__qvdo = vpkt__gvz['df_to_parquet']
    return dao__qvdo


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    xkie__nhvln = 'all_ok'
    qkfs__fxivz, wsac__rig = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        olxw__outmo = 100
        if chunksize is None:
            mxdh__qal = olxw__outmo
        else:
            mxdh__qal = min(chunksize, olxw__outmo)
        if _is_table_create:
            df = df.iloc[:mxdh__qal, :]
        else:
            df = df.iloc[mxdh__qal:, :]
            if len(df) == 0:
                return xkie__nhvln
    dfz__gzrrt = df.columns
    try:
        if qkfs__fxivz == 'snowflake':
            if wsac__rig and con.count(wsac__rig) == 1:
                con = con.replace(wsac__rig, quote(wsac__rig))
            try:
                from snowflake.connector.pandas_tools import pd_writer
                from bodo import snowflake_sqlalchemy_compat
                if method is not None and _is_table_create and bodo.get_rank(
                    ) == 0:
                    import warnings
                    from bodo.utils.typing import BodoWarning
                    warnings.warn(BodoWarning(
                        'DataFrame.to_sql(): method argument is not supported with Snowflake. Bodo always uses snowflake.connector.pandas_tools.pd_writer to write data.'
                        ))
                method = pd_writer
                df.columns = [(ymogs__eeuca.upper() if ymogs__eeuca.islower
                    () else ymogs__eeuca) for ymogs__eeuca in df.columns]
            except ImportError as pnsg__lswsu:
                xkie__nhvln = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return xkie__nhvln
        if qkfs__fxivz == 'oracle':
            import os
            import sqlalchemy as sa
            from sqlalchemy.dialects.oracle import VARCHAR2
            olfcz__aroo = os.environ.get('BODO_DISABLE_ORACLE_VARCHAR2', None)
            vovp__ogdda = bodo.typeof(df)
            bxtka__pmrmt = {}
            for ymogs__eeuca, bjsmb__ooh in zip(vovp__ogdda.columns,
                vovp__ogdda.data):
                if df[ymogs__eeuca].dtype == 'object':
                    if bjsmb__ooh == datetime_date_array_type:
                        bxtka__pmrmt[ymogs__eeuca] = sa.types.Date
                    elif bjsmb__ooh in (bodo.string_array_type, bodo.
                        dict_str_arr_type) and (not olfcz__aroo or 
                        olfcz__aroo == '0'):
                        bxtka__pmrmt[ymogs__eeuca] = VARCHAR2(4000)
            dtype = bxtka__pmrmt
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as ouikx__fmhal:
            xkie__nhvln = ouikx__fmhal.args[0]
            if qkfs__fxivz == 'oracle' and 'ORA-12899' in xkie__nhvln:
                xkie__nhvln += """
                String is larger than VARCHAR2 maximum length.
                Please set environment variable `BODO_DISABLE_ORACLE_VARCHAR2` to
                disable Bodo's optimziation use of VARCHA2.
                NOTE: Oracle `to_sql` with CLOB datatypes is known to be really slow.
                """
        return xkie__nhvln
    finally:
        df.columns = dfz__gzrrt


@numba.njit
def to_sql_exception_guard_encaps(df, name, con, schema=None, if_exists=
    'fail', index=True, index_label=None, chunksize=None, dtype=None,
    method=None, _is_table_create=False, _is_parallel=False):
    with numba.objmode(out='unicode_type'):
        out = to_sql_exception_guard(df, name, con, schema, if_exists,
            index, index_label, chunksize, dtype, method, _is_table_create,
            _is_parallel)
    return out


@overload_method(DataFrameType, 'to_sql')
def to_sql_overload(df, name, con, schema=None, if_exists='fail', index=
    True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_parallel=False):
    check_runtime_cols_unsupported(df, 'DataFrame.to_sql()')
    if is_overload_none(schema):
        if bodo.get_rank() == 0:
            import warnings
            warnings.warn(BodoWarning(
                f'DataFrame.to_sql(): schema argument is recommended to avoid permission issues when writing the table.'
                ))
    if not (is_overload_none(chunksize) or isinstance(chunksize, types.Integer)
        ):
        raise BodoError(
            "DataFrame.to_sql(): 'chunksize' argument must be an integer if provided."
            )

    def _impl(df, name, con, schema=None, if_exists='fail', index=True,
        index_label=None, chunksize=None, dtype=None, method=None,
        _is_parallel=False):
        tjfh__uislj = bodo.libs.distributed_api.get_rank()
        xkie__nhvln = 'unset'
        if tjfh__uislj != 0:
            xkie__nhvln = bcast_scalar(xkie__nhvln)
        elif tjfh__uislj == 0:
            xkie__nhvln = to_sql_exception_guard_encaps(df, name, con,
                schema, if_exists, index, index_label, chunksize, dtype,
                method, True, _is_parallel)
            xkie__nhvln = bcast_scalar(xkie__nhvln)
        if_exists = 'append'
        if _is_parallel and xkie__nhvln == 'all_ok':
            xkie__nhvln = to_sql_exception_guard_encaps(df, name, con,
                schema, if_exists, index, index_label, chunksize, dtype,
                method, False, _is_parallel)
        if xkie__nhvln != 'all_ok':
            print('err_msg=', xkie__nhvln)
            raise ValueError('error in to_sql() operation')
    return _impl


@overload_method(DataFrameType, 'to_csv', no_unliteral=True)
def to_csv_overload(df, path_or_buf=None, sep=',', na_rep='', float_format=
    None, columns=None, header=True, index=True, index_label=None, mode='w',
    encoding=None, compression=None, quoting=None, quotechar='"',
    line_terminator=None, chunksize=None, date_format=None, doublequote=
    True, escapechar=None, decimal='.', errors='strict', storage_options=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_csv()')
    check_unsupported_args('DataFrame.to_csv', {'encoding': encoding,
        'mode': mode, 'errors': errors, 'storage_options': storage_options},
        {'encoding': None, 'mode': 'w', 'errors': 'strict',
        'storage_options': None}, package_name='pandas', module_name='IO')
    if not (is_overload_none(path_or_buf) or is_overload_constant_str(
        path_or_buf) or path_or_buf == string_type):
        raise BodoError(
            "DataFrame.to_csv(): 'path_or_buf' argument should be None or string"
            )
    if not is_overload_none(compression):
        raise BodoError(
            "DataFrame.to_csv(): 'compression' argument supports only None, which is the default in JIT code."
            )
    if is_overload_constant_str(path_or_buf):
        jlu__krscw = get_overload_const_str(path_or_buf)
        if jlu__krscw.endswith(('.gz', '.bz2', '.zip', '.xz')):
            import warnings
            from bodo.utils.typing import BodoWarning
            warnings.warn(BodoWarning(
                "DataFrame.to_csv(): 'compression' argument defaults to None in JIT code, which is the only supported value."
                ))
    if not (is_overload_none(columns) or isinstance(columns, (types.List,
        types.Tuple))):
        raise BodoError(
            "DataFrame.to_csv(): 'columns' argument must be list a or tuple type."
            )
    if is_overload_none(path_or_buf):

        def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=
            None, columns=None, header=True, index=True, index_label=None,
            mode='w', encoding=None, compression=None, quoting=None,
            quotechar='"', line_terminator=None, chunksize=None,
            date_format=None, doublequote=True, escapechar=None, decimal=
            '.', errors='strict', storage_options=None):
            with numba.objmode(D='unicode_type'):
                D = df.to_csv(path_or_buf, sep, na_rep, float_format,
                    columns, header, index, index_label, mode, encoding,
                    compression, quoting, quotechar, line_terminator,
                    chunksize, date_format, doublequote, escapechar,
                    decimal, errors, storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=None,
        columns=None, header=True, index=True, index_label=None, mode='w',
        encoding=None, compression=None, quoting=None, quotechar='"',
        line_terminator=None, chunksize=None, date_format=None, doublequote
        =True, escapechar=None, decimal='.', errors='strict',
        storage_options=None):
        with numba.objmode(D='unicode_type'):
            D = df.to_csv(None, sep, na_rep, float_format, columns, header,
                index, index_label, mode, encoding, compression, quoting,
                quotechar, line_terminator, chunksize, date_format,
                doublequote, escapechar, decimal, errors, storage_options)
        bodo.io.fs_io.csv_write(path_or_buf, D)
    return _impl


@overload_method(DataFrameType, 'to_json', no_unliteral=True)
def to_json_overload(df, path_or_buf=None, orient='records', date_format=
    None, double_precision=10, force_ascii=True, date_unit='ms',
    default_handler=None, lines=True, compression='infer', index=True,
    indent=None, storage_options=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_json()')
    check_unsupported_args('DataFrame.to_json', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if path_or_buf is None or path_or_buf == types.none:

        def _impl(df, path_or_buf=None, orient='records', date_format=None,
            double_precision=10, force_ascii=True, date_unit='ms',
            default_handler=None, lines=True, compression='infer', index=
            True, indent=None, storage_options=None):
            with numba.objmode(D='unicode_type'):
                D = df.to_json(path_or_buf, orient, date_format,
                    double_precision, force_ascii, date_unit,
                    default_handler, lines, compression, index, indent,
                    storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, orient='records', date_format=None,
        double_precision=10, force_ascii=True, date_unit='ms',
        default_handler=None, lines=True, compression='infer', index=True,
        indent=None, storage_options=None):
        with numba.objmode(D='unicode_type'):
            D = df.to_json(None, orient, date_format, double_precision,
                force_ascii, date_unit, default_handler, lines, compression,
                index, indent, storage_options)
        dru__tgb = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(dru__tgb))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(dru__tgb))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    kmuc__chfj = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    bag__ycm = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', kmuc__chfj, bag__ycm,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    xky__bvn = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        geq__ygucv = data.data.dtype.categories
        xky__bvn += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        geq__ygucv = data.dtype.categories
        xky__bvn += '  data_values = data\n'
    iylgk__ispxw = len(geq__ygucv)
    xky__bvn += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    xky__bvn += '  numba.parfors.parfor.init_prange()\n'
    xky__bvn += '  n = len(data_values)\n'
    for i in range(iylgk__ispxw):
        xky__bvn += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    xky__bvn += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    xky__bvn += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for ccta__jckz in range(iylgk__ispxw):
        xky__bvn += '          data_arr_{}[i] = 0\n'.format(ccta__jckz)
    xky__bvn += '      else:\n'
    for aarsb__ghpx in range(iylgk__ispxw):
        xky__bvn += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            aarsb__ghpx)
    basuj__nlyi = ', '.join(f'data_arr_{i}' for i in range(iylgk__ispxw))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(geq__ygucv[0], np.datetime64):
        geq__ygucv = tuple(pd.Timestamp(ymogs__eeuca) for ymogs__eeuca in
            geq__ygucv)
    elif isinstance(geq__ygucv[0], np.timedelta64):
        geq__ygucv = tuple(pd.Timedelta(ymogs__eeuca) for ymogs__eeuca in
            geq__ygucv)
    return bodo.hiframes.dataframe_impl._gen_init_df(xky__bvn, geq__ygucv,
        basuj__nlyi, index)


def categorical_can_construct_dataframe(val):
    if isinstance(val, CategoricalArrayType):
        return val.dtype.categories is not None
    elif isinstance(val, SeriesType) and isinstance(val.data,
        CategoricalArrayType):
        return val.data.dtype.categories is not None
    return False


def handle_inplace_df_type_change(inplace, _bodo_transformed, func_name):
    if is_overload_false(_bodo_transformed
        ) and bodo.transforms.typing_pass.in_partial_typing and (
        is_overload_true(inplace) or not is_overload_constant_bool(inplace)):
        bodo.transforms.typing_pass.typing_transform_required = True
        raise Exception('DataFrame.{}(): transform necessary for inplace'.
            format(func_name))


pd_unsupported = (pd.read_pickle, pd.read_table, pd.read_fwf, pd.
    read_clipboard, pd.ExcelFile, pd.read_html, pd.read_xml, pd.read_hdf,
    pd.read_feather, pd.read_orc, pd.read_sas, pd.read_spss, pd.
    read_sql_query, pd.read_gbq, pd.read_stata, pd.ExcelWriter, pd.
    json_normalize, pd.merge_ordered, pd.factorize, pd.wide_to_long, pd.
    bdate_range, pd.period_range, pd.infer_freq, pd.interval_range, pd.eval,
    pd.test, pd.Grouper)
pd_util_unsupported = pd.util.hash_array, pd.util.hash_pandas_object
dataframe_unsupported = ['set_flags', 'convert_dtypes', 'bool', '__iter__',
    'items', 'iteritems', 'keys', 'iterrows', 'lookup', 'pop', 'xs', 'get',
    'add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'pow', 'dot',
    'radd', 'rsub', 'rmul', 'rdiv', 'rtruediv', 'rfloordiv', 'rmod', 'rpow',
    'lt', 'gt', 'le', 'ge', 'ne', 'eq', 'combine', 'combine_first',
    'subtract', 'divide', 'multiply', 'applymap', 'agg', 'aggregate',
    'transform', 'expanding', 'ewm', 'all', 'any', 'clip', 'corrwith',
    'cummax', 'cummin', 'eval', 'kurt', 'kurtosis', 'mad', 'mode', 'rank',
    'round', 'sem', 'skew', 'value_counts', 'add_prefix', 'add_suffix',
    'align', 'at_time', 'between_time', 'equals', 'reindex', 'reindex_like',
    'rename_axis', 'set_axis', 'truncate', 'backfill', 'bfill', 'ffill',
    'interpolate', 'pad', 'droplevel', 'reorder_levels', 'nlargest',
    'nsmallest', 'swaplevel', 'stack', 'unstack', 'swapaxes', 'squeeze',
    'to_xarray', 'T', 'transpose', 'compare', 'update', 'asfreq', 'asof',
    'slice_shift', 'tshift', 'first_valid_index', 'last_valid_index',
    'resample', 'to_period', 'to_timestamp', 'tz_convert', 'tz_localize',
    'boxplot', 'hist', 'from_dict', 'from_records', 'to_pickle', 'to_hdf',
    'to_dict', 'to_excel', 'to_html', 'to_feather', 'to_latex', 'to_stata',
    'to_gbq', 'to_records', 'to_clipboard', 'to_markdown', 'to_xml']
dataframe_unsupported_attrs = ['at', 'attrs', 'axes', 'flags', 'style',
    'sparse']


def _install_pd_unsupported(mod_name, pd_unsupported):
    for lhhms__bpir in pd_unsupported:
        nddfk__ecpp = mod_name + '.' + lhhms__bpir.__name__
        overload(lhhms__bpir, no_unliteral=True)(create_unsupported_overload
            (nddfk__ecpp))


def _install_dataframe_unsupported():
    for mgnrg__ycc in dataframe_unsupported_attrs:
        gpz__foozj = 'DataFrame.' + mgnrg__ycc
        overload_attribute(DataFrameType, mgnrg__ycc)(
            create_unsupported_overload(gpz__foozj))
    for nddfk__ecpp in dataframe_unsupported:
        gpz__foozj = 'DataFrame.' + nddfk__ecpp + '()'
        overload_method(DataFrameType, nddfk__ecpp)(create_unsupported_overload
            (gpz__foozj))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
