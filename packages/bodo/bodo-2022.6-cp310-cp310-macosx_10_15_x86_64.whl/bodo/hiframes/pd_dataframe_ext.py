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
            jxdn__oyl = f'{len(self.data)} columns of types {set(self.data)}'
            cwh__skaag = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({jxdn__oyl}, {self.index}, {cwh__skaag}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
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
        return {hdfrz__dmqbx: i for i, hdfrz__dmqbx in enumerate(self.columns)}

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
            glbsc__otgj = (self.index if self.index == other.index else
                self.index.unify(typingctx, other.index))
            data = tuple(jrwzn__zlyeb.unify(typingctx, zivf__kgi) if 
                jrwzn__zlyeb != zivf__kgi else jrwzn__zlyeb for 
                jrwzn__zlyeb, zivf__kgi in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if glbsc__otgj is not None and None not in data:
                return DataFrameType(data, glbsc__otgj, self.columns, dist,
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
        return all(jrwzn__zlyeb.is_precise() for jrwzn__zlyeb in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        hkf__ounc = self.columns.index(col_name)
        adjco__ylxgv = tuple(list(self.data[:hkf__ounc]) + [new_type] +
            list(self.data[hkf__ounc + 1:]))
        return DataFrameType(adjco__ylxgv, self.index, self.columns, self.
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
        romu__kpqs = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            romu__kpqs.append(('columns', fe_type.df_type.runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, romu__kpqs)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        romu__kpqs = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, romu__kpqs)


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
        vds__tajr = 'n',
        ibh__rotp = {'n': 5}
        kbqqs__lero, xfm__vpks = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, vds__tajr, ibh__rotp)
        flv__rqa = xfm__vpks[0]
        if not is_overload_int(flv__rqa):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        sdtd__xwmpd = df.copy()
        return sdtd__xwmpd(*xfm__vpks).replace(pysig=kbqqs__lero)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        xtev__zfx = (df,) + args
        vds__tajr = 'df', 'method', 'min_periods'
        ibh__rotp = {'method': 'pearson', 'min_periods': 1}
        tkh__gdi = 'method',
        kbqqs__lero, xfm__vpks = bodo.utils.typing.fold_typing_args(func_name,
            xtev__zfx, kws, vds__tajr, ibh__rotp, tkh__gdi)
        nfpe__bpeym = xfm__vpks[2]
        if not is_overload_int(nfpe__bpeym):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        zwpkg__fbhtg = []
        dehmb__epfn = []
        for hdfrz__dmqbx, hqok__zuo in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(hqok__zuo.dtype):
                zwpkg__fbhtg.append(hdfrz__dmqbx)
                dehmb__epfn.append(types.Array(types.float64, 1, 'A'))
        if len(zwpkg__fbhtg) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        dehmb__epfn = tuple(dehmb__epfn)
        zwpkg__fbhtg = tuple(zwpkg__fbhtg)
        index_typ = bodo.utils.typing.type_col_to_index(zwpkg__fbhtg)
        sdtd__xwmpd = DataFrameType(dehmb__epfn, index_typ, zwpkg__fbhtg)
        return sdtd__xwmpd(*xfm__vpks).replace(pysig=kbqqs__lero)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        sgaj__ghhv = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        tlkrg__ogx = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        rlx__qmr = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        ubow__bqxgg = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        wvx__xao = dict(raw=tlkrg__ogx, result_type=rlx__qmr)
        rhm__cot = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', wvx__xao, rhm__cot,
            package_name='pandas', module_name='DataFrame')
        xkpas__wogq = True
        if types.unliteral(sgaj__ghhv) == types.unicode_type:
            if not is_overload_constant_str(sgaj__ghhv):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            xkpas__wogq = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        ewvav__ozo = get_overload_const_int(axis)
        if xkpas__wogq and ewvav__ozo != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif ewvav__ozo not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        scn__sex = []
        for arr_typ in df.data:
            kqaoj__ynhvj = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            avu__euet = self.context.resolve_function_type(operator.getitem,
                (SeriesIlocType(kqaoj__ynhvj), types.int64), {}).return_type
            scn__sex.append(avu__euet)
        ewhq__pmm = types.none
        srvko__ztw = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(hdfrz__dmqbx) for hdfrz__dmqbx in df.
            columns)), None)
        amicd__unr = types.BaseTuple.from_types(scn__sex)
        ttp__ggnol = types.Tuple([types.bool_] * len(amicd__unr))
        eydpm__nqabc = bodo.NullableTupleType(amicd__unr, ttp__ggnol)
        jff__dzna = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if jff__dzna == types.NPDatetime('ns'):
            jff__dzna = bodo.pd_timestamp_type
        if jff__dzna == types.NPTimedelta('ns'):
            jff__dzna = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(amicd__unr):
            qktxe__zksfh = HeterogeneousSeriesType(eydpm__nqabc, srvko__ztw,
                jff__dzna)
        else:
            qktxe__zksfh = SeriesType(amicd__unr.dtype, eydpm__nqabc,
                srvko__ztw, jff__dzna)
        dnatk__eayev = qktxe__zksfh,
        if ubow__bqxgg is not None:
            dnatk__eayev += tuple(ubow__bqxgg.types)
        try:
            if not xkpas__wogq:
                tcrj__xza = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(sgaj__ghhv), self.context,
                    'DataFrame.apply', axis if ewvav__ozo == 1 else None)
            else:
                tcrj__xza = get_const_func_output_type(sgaj__ghhv,
                    dnatk__eayev, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as hklye__mlgvh:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()',
                hklye__mlgvh))
        if xkpas__wogq:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(tcrj__xza, (SeriesType, HeterogeneousSeriesType)
                ) and tcrj__xza.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(tcrj__xza, HeterogeneousSeriesType):
                wdbw__pvnox, eiqaf__ieowy = tcrj__xza.const_info
                if isinstance(tcrj__xza.data, bodo.libs.nullable_tuple_ext.
                    NullableTupleType):
                    nfsh__wdkyl = tcrj__xza.data.tuple_typ.types
                elif isinstance(tcrj__xza.data, types.Tuple):
                    nfsh__wdkyl = tcrj__xza.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                kax__ttfl = tuple(to_nullable_type(dtype_to_array_type(
                    jlwu__jnia)) for jlwu__jnia in nfsh__wdkyl)
                zji__njudx = DataFrameType(kax__ttfl, df.index, eiqaf__ieowy)
            elif isinstance(tcrj__xza, SeriesType):
                yykso__spvte, eiqaf__ieowy = tcrj__xza.const_info
                kax__ttfl = tuple(to_nullable_type(dtype_to_array_type(
                    tcrj__xza.dtype)) for wdbw__pvnox in range(yykso__spvte))
                zji__njudx = DataFrameType(kax__ttfl, df.index, eiqaf__ieowy)
            else:
                bls__cyreg = get_udf_out_arr_type(tcrj__xza)
                zji__njudx = SeriesType(bls__cyreg.dtype, bls__cyreg, df.
                    index, None)
        else:
            zji__njudx = tcrj__xza
        fpq__achx = ', '.join("{} = ''".format(jrwzn__zlyeb) for
            jrwzn__zlyeb in kws.keys())
        btc__gcgy = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {fpq__achx}):
"""
        btc__gcgy += '    pass\n'
        ijk__jua = {}
        exec(btc__gcgy, {}, ijk__jua)
        aln__pts = ijk__jua['apply_stub']
        kbqqs__lero = numba.core.utils.pysignature(aln__pts)
        cdkz__vznl = (sgaj__ghhv, axis, tlkrg__ogx, rlx__qmr, ubow__bqxgg
            ) + tuple(kws.values())
        return signature(zji__njudx, *cdkz__vznl).replace(pysig=kbqqs__lero)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        vds__tajr = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        ibh__rotp = {'x': None, 'y': None, 'kind': 'line', 'figsize': None,
            'ax': None, 'subplots': False, 'sharex': None, 'sharey': False,
            'layout': None, 'use_index': True, 'title': None, 'grid': None,
            'legend': True, 'style': None, 'logx': False, 'logy': False,
            'loglog': False, 'xticks': None, 'yticks': None, 'xlim': None,
            'ylim': None, 'rot': None, 'fontsize': None, 'colormap': None,
            'table': False, 'yerr': None, 'xerr': None, 'secondary_y': 
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        tkh__gdi = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        kbqqs__lero, xfm__vpks = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, vds__tajr, ibh__rotp, tkh__gdi)
        kqnv__bxm = xfm__vpks[2]
        if not is_overload_constant_str(kqnv__bxm):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        hpnk__hobi = xfm__vpks[0]
        if not is_overload_none(hpnk__hobi) and not (is_overload_int(
            hpnk__hobi) or is_overload_constant_str(hpnk__hobi)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(hpnk__hobi):
            rvmbw__war = get_overload_const_str(hpnk__hobi)
            if rvmbw__war not in df.columns:
                raise BodoError(f'{func_name}: {rvmbw__war} column not found.')
        elif is_overload_int(hpnk__hobi):
            jytyy__mzxnu = get_overload_const_int(hpnk__hobi)
            if jytyy__mzxnu > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {jytyy__mzxnu} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            hpnk__hobi = df.columns[hpnk__hobi]
        cnxyq__daf = xfm__vpks[1]
        if not is_overload_none(cnxyq__daf) and not (is_overload_int(
            cnxyq__daf) or is_overload_constant_str(cnxyq__daf)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(cnxyq__daf):
            zqxez__mhy = get_overload_const_str(cnxyq__daf)
            if zqxez__mhy not in df.columns:
                raise BodoError(f'{func_name}: {zqxez__mhy} column not found.')
        elif is_overload_int(cnxyq__daf):
            lji__dxkvo = get_overload_const_int(cnxyq__daf)
            if lji__dxkvo > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {lji__dxkvo} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            cnxyq__daf = df.columns[cnxyq__daf]
        odb__unga = xfm__vpks[3]
        if not is_overload_none(odb__unga) and not is_tuple_like_type(odb__unga
            ):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        ufu__xlm = xfm__vpks[10]
        if not is_overload_none(ufu__xlm) and not is_overload_constant_str(
            ufu__xlm):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        xovpr__wrb = xfm__vpks[12]
        if not is_overload_bool(xovpr__wrb):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        nrrlz__vzuvh = xfm__vpks[17]
        if not is_overload_none(nrrlz__vzuvh) and not is_tuple_like_type(
            nrrlz__vzuvh):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        rkcs__auer = xfm__vpks[18]
        if not is_overload_none(rkcs__auer) and not is_tuple_like_type(
            rkcs__auer):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        ajtg__vql = xfm__vpks[22]
        if not is_overload_none(ajtg__vql) and not is_overload_int(ajtg__vql):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        oebh__wcupi = xfm__vpks[29]
        if not is_overload_none(oebh__wcupi) and not is_overload_constant_str(
            oebh__wcupi):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        iizs__wtz = xfm__vpks[30]
        if not is_overload_none(iizs__wtz) and not is_overload_constant_str(
            iizs__wtz):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        nbqm__xymp = types.List(types.mpl_line_2d_type)
        kqnv__bxm = get_overload_const_str(kqnv__bxm)
        if kqnv__bxm == 'scatter':
            if is_overload_none(hpnk__hobi) and is_overload_none(cnxyq__daf):
                raise BodoError(
                    f'{func_name}: {kqnv__bxm} requires an x and y column.')
            elif is_overload_none(hpnk__hobi):
                raise BodoError(
                    f'{func_name}: {kqnv__bxm} x column is missing.')
            elif is_overload_none(cnxyq__daf):
                raise BodoError(
                    f'{func_name}: {kqnv__bxm} y column is missing.')
            nbqm__xymp = types.mpl_path_collection_type
        elif kqnv__bxm != 'line':
            raise BodoError(f'{func_name}: {kqnv__bxm} plot is not supported.')
        return signature(nbqm__xymp, *xfm__vpks).replace(pysig=kbqqs__lero)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            wfel__nrujm = df.columns.index(attr)
            arr_typ = df.data[wfel__nrujm]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            agnx__codsa = []
            adjco__ylxgv = []
            dvamu__cwfif = False
            for i, uag__ogfml in enumerate(df.columns):
                if uag__ogfml[0] != attr:
                    continue
                dvamu__cwfif = True
                agnx__codsa.append(uag__ogfml[1] if len(uag__ogfml) == 2 else
                    uag__ogfml[1:])
                adjco__ylxgv.append(df.data[i])
            if dvamu__cwfif:
                return DataFrameType(tuple(adjco__ylxgv), df.index, tuple(
                    agnx__codsa))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        ujcj__pyfyk = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(ujcj__pyfyk)
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
        pzcxo__hduw = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], pzcxo__hduw)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    dcv__hqvj = builder.module
    twk__tpuo = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    bggcs__krt = cgutils.get_or_insert_function(dcv__hqvj, twk__tpuo, name=
        '.dtor.df.{}'.format(df_type))
    if not bggcs__krt.is_declaration:
        return bggcs__krt
    bggcs__krt.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(bggcs__krt.append_basic_block())
    ugtu__qizx = bggcs__krt.args[0]
    oxw__oqbiq = context.get_value_type(payload_type).as_pointer()
    tmyz__ploe = builder.bitcast(ugtu__qizx, oxw__oqbiq)
    payload = context.make_helper(builder, payload_type, ref=tmyz__ploe)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        byln__rjpj = context.get_python_api(builder)
        xmlt__vjz = byln__rjpj.gil_ensure()
        byln__rjpj.decref(payload.parent)
        byln__rjpj.gil_release(xmlt__vjz)
    builder.ret_void()
    return bggcs__krt


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    sni__rqe = cgutils.create_struct_proxy(payload_type)(context, builder)
    sni__rqe.data = data_tup
    sni__rqe.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        sni__rqe.columns = colnames
    ebrsj__kvvf = context.get_value_type(payload_type)
    fvm__ygzj = context.get_abi_sizeof(ebrsj__kvvf)
    vzkkc__yttdk = define_df_dtor(context, builder, df_type, payload_type)
    jhr__fqdem = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, fvm__ygzj), vzkkc__yttdk)
    mno__xndqe = context.nrt.meminfo_data(builder, jhr__fqdem)
    rjdco__qrhj = builder.bitcast(mno__xndqe, ebrsj__kvvf.as_pointer())
    tez__xgqq = cgutils.create_struct_proxy(df_type)(context, builder)
    tez__xgqq.meminfo = jhr__fqdem
    if parent is None:
        tez__xgqq.parent = cgutils.get_null_value(tez__xgqq.parent.type)
    else:
        tez__xgqq.parent = parent
        sni__rqe.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            byln__rjpj = context.get_python_api(builder)
            xmlt__vjz = byln__rjpj.gil_ensure()
            byln__rjpj.incref(parent)
            byln__rjpj.gil_release(xmlt__vjz)
    builder.store(sni__rqe._getvalue(), rjdco__qrhj)
    return tez__xgqq._getvalue()


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
        kcefb__pfp = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype.
            arr_types)
    else:
        kcefb__pfp = [jlwu__jnia for jlwu__jnia in data_typ.dtype.arr_types]
    xhgya__tpf = DataFrameType(tuple(kcefb__pfp + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        ysek__dcq = construct_dataframe(context, builder, df_type, data_tup,
            index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return ysek__dcq
    sig = signature(xhgya__tpf, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    yykso__spvte = len(data_tup_typ.types)
    if yykso__spvte == 0:
        column_names = ()
    urxwv__zvg = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    assert isinstance(urxwv__zvg, ColNamesMetaType) and isinstance(urxwv__zvg
        .meta, tuple
        ), 'Third argument to init_dataframe must be of type ColNamesMetaType, and must contain a tuple of column names'
    column_names = urxwv__zvg.meta
    if yykso__spvte == 1 and isinstance(data_tup_typ.types[0], TableType):
        yykso__spvte = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == yykso__spvte, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    gbh__ynis = data_tup_typ.types
    if yykso__spvte != 0 and isinstance(data_tup_typ.types[0], TableType):
        gbh__ynis = data_tup_typ.types[0].arr_types
        is_table_format = True
    xhgya__tpf = DataFrameType(gbh__ynis, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            tfwpv__mcwu = cgutils.create_struct_proxy(xhgya__tpf.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = tfwpv__mcwu.parent
        ysek__dcq = construct_dataframe(context, builder, df_type, data_tup,
            index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return ysek__dcq
    sig = signature(xhgya__tpf, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        tez__xgqq = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, tez__xgqq.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        sni__rqe = get_dataframe_payload(context, builder, df_typ, args[0])
        uyn__zgqga = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[uyn__zgqga]
        if df_typ.is_table_format:
            tfwpv__mcwu = cgutils.create_struct_proxy(df_typ.table_type)(
                context, builder, builder.extract_value(sni__rqe.data, 0))
            evwx__raij = df_typ.table_type.type_to_blk[arr_typ]
            qwvpt__upmbd = getattr(tfwpv__mcwu, f'block_{evwx__raij}')
            ttpop__vofx = ListInstance(context, builder, types.List(arr_typ
                ), qwvpt__upmbd)
            xxbgl__vxyu = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[uyn__zgqga])
            pzcxo__hduw = ttpop__vofx.getitem(xxbgl__vxyu)
        else:
            pzcxo__hduw = builder.extract_value(sni__rqe.data, uyn__zgqga)
        ccz__uus = cgutils.alloca_once_value(builder, pzcxo__hduw)
        bpw__xzdoy = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, ccz__uus, bpw__xzdoy)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    jhr__fqdem = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, jhr__fqdem)
    oxw__oqbiq = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, oxw__oqbiq)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    xhgya__tpf = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        xhgya__tpf = types.Tuple([TableType(df_typ.data)])
    sig = signature(xhgya__tpf, df_typ)

    def codegen(context, builder, signature, args):
        sni__rqe = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            sni__rqe.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        sni__rqe = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, sni__rqe.index
            )
    xhgya__tpf = df_typ.index
    sig = signature(xhgya__tpf, df_typ)
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
        sdtd__xwmpd = df.data[i]
        return sdtd__xwmpd(*args)


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
        sni__rqe = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(sni__rqe.data, 0))
    return df_typ.table_type(df_typ), codegen


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        sni__rqe = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, sni__rqe.columns)
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
    amicd__unr = self.typemap[data_tup.name]
    if any(is_tuple_like_type(jlwu__jnia) for jlwu__jnia in amicd__unr.types):
        return None
    if equiv_set.has_shape(data_tup):
        awg__fqitr = equiv_set.get_shape(data_tup)
        if len(awg__fqitr) > 1:
            equiv_set.insert_equiv(*awg__fqitr)
        if len(awg__fqitr) > 0:
            srvko__ztw = self.typemap[index.name]
            if not isinstance(srvko__ztw, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(awg__fqitr[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(awg__fqitr[0], len(
                awg__fqitr)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    brpyv__jvr = args[0]
    data_types = self.typemap[brpyv__jvr.name].data
    if any(is_tuple_like_type(jlwu__jnia) for jlwu__jnia in data_types):
        return None
    if equiv_set.has_shape(brpyv__jvr):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            brpyv__jvr)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    brpyv__jvr = args[0]
    srvko__ztw = self.typemap[brpyv__jvr.name].index
    if isinstance(srvko__ztw, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(brpyv__jvr):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            brpyv__jvr)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    brpyv__jvr = args[0]
    if equiv_set.has_shape(brpyv__jvr):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            brpyv__jvr), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    brpyv__jvr = args[0]
    if equiv_set.has_shape(brpyv__jvr):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            brpyv__jvr)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    uyn__zgqga = get_overload_const_int(c_ind_typ)
    if df_typ.data[uyn__zgqga] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        aanbg__eyh, wdbw__pvnox, vrbjk__updp = args
        sni__rqe = get_dataframe_payload(context, builder, df_typ, aanbg__eyh)
        if df_typ.is_table_format:
            tfwpv__mcwu = cgutils.create_struct_proxy(df_typ.table_type)(
                context, builder, builder.extract_value(sni__rqe.data, 0))
            evwx__raij = df_typ.table_type.type_to_blk[arr_typ]
            qwvpt__upmbd = getattr(tfwpv__mcwu, f'block_{evwx__raij}')
            ttpop__vofx = ListInstance(context, builder, types.List(arr_typ
                ), qwvpt__upmbd)
            xxbgl__vxyu = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[uyn__zgqga])
            ttpop__vofx.setitem(xxbgl__vxyu, vrbjk__updp, True)
        else:
            pzcxo__hduw = builder.extract_value(sni__rqe.data, uyn__zgqga)
            context.nrt.decref(builder, df_typ.data[uyn__zgqga], pzcxo__hduw)
            sni__rqe.data = builder.insert_value(sni__rqe.data, vrbjk__updp,
                uyn__zgqga)
            context.nrt.incref(builder, arr_typ, vrbjk__updp)
        tez__xgqq = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=aanbg__eyh)
        payload_type = DataFramePayloadType(df_typ)
        tmyz__ploe = context.nrt.meminfo_data(builder, tez__xgqq.meminfo)
        oxw__oqbiq = context.get_value_type(payload_type).as_pointer()
        tmyz__ploe = builder.bitcast(tmyz__ploe, oxw__oqbiq)
        builder.store(sni__rqe._getvalue(), tmyz__ploe)
        return impl_ret_borrowed(context, builder, df_typ, aanbg__eyh)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        gxfo__oya = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        traqn__eck = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=gxfo__oya)
        ubqt__hzrq = get_dataframe_payload(context, builder, df_typ, gxfo__oya)
        tez__xgqq = construct_dataframe(context, builder, signature.
            return_type, ubqt__hzrq.data, index_val, traqn__eck.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), ubqt__hzrq.data)
        return tez__xgqq
    xhgya__tpf = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(xhgya__tpf, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    yykso__spvte = len(df_type.columns)
    ida__labv = yykso__spvte
    znkvp__upzc = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    mvee__izhw = col_name not in df_type.columns
    uyn__zgqga = yykso__spvte
    if mvee__izhw:
        znkvp__upzc += arr_type,
        column_names += col_name,
        ida__labv += 1
    else:
        uyn__zgqga = df_type.columns.index(col_name)
        znkvp__upzc = tuple(arr_type if i == uyn__zgqga else znkvp__upzc[i] for
            i in range(yykso__spvte))

    def codegen(context, builder, signature, args):
        aanbg__eyh, wdbw__pvnox, vrbjk__updp = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, aanbg__eyh)
        jdv__tqkrs = cgutils.create_struct_proxy(df_type)(context, builder,
            value=aanbg__eyh)
        if df_type.is_table_format:
            aip__glp = df_type.table_type
            cztq__jzyvm = builder.extract_value(in_dataframe_payload.data, 0)
            euc__awypk = TableType(znkvp__upzc)
            poxl__ebyy = set_table_data_codegen(context, builder, aip__glp,
                cztq__jzyvm, euc__awypk, arr_type, vrbjk__updp, uyn__zgqga,
                mvee__izhw)
            data_tup = context.make_tuple(builder, types.Tuple([euc__awypk]
                ), [poxl__ebyy])
        else:
            gbh__ynis = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != uyn__zgqga else vrbjk__updp) for i in range(
                yykso__spvte)]
            if mvee__izhw:
                gbh__ynis.append(vrbjk__updp)
            for brpyv__jvr, aegl__ihem in zip(gbh__ynis, znkvp__upzc):
                context.nrt.incref(builder, aegl__ihem, brpyv__jvr)
            data_tup = context.make_tuple(builder, types.Tuple(znkvp__upzc),
                gbh__ynis)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        yahx__zdjm = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, jdv__tqkrs.parent, None)
        if not mvee__izhw and arr_type == df_type.data[uyn__zgqga]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            tmyz__ploe = context.nrt.meminfo_data(builder, jdv__tqkrs.meminfo)
            oxw__oqbiq = context.get_value_type(payload_type).as_pointer()
            tmyz__ploe = builder.bitcast(tmyz__ploe, oxw__oqbiq)
            jmzt__wife = get_dataframe_payload(context, builder, df_type,
                yahx__zdjm)
            builder.store(jmzt__wife._getvalue(), tmyz__ploe)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, euc__awypk, builder.
                    extract_value(data_tup, 0))
            else:
                for brpyv__jvr, aegl__ihem in zip(gbh__ynis, znkvp__upzc):
                    context.nrt.incref(builder, aegl__ihem, brpyv__jvr)
        has_parent = cgutils.is_not_null(builder, jdv__tqkrs.parent)
        with builder.if_then(has_parent):
            byln__rjpj = context.get_python_api(builder)
            xmlt__vjz = byln__rjpj.gil_ensure()
            nel__dpfd = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, vrbjk__updp)
            hdfrz__dmqbx = numba.core.pythonapi._BoxContext(context,
                builder, byln__rjpj, nel__dpfd)
            eqy__xel = hdfrz__dmqbx.pyapi.from_native_value(arr_type,
                vrbjk__updp, hdfrz__dmqbx.env_manager)
            if isinstance(col_name, str):
                scg__jtq = context.insert_const_string(builder.module, col_name
                    )
                pxfp__ech = byln__rjpj.string_from_string(scg__jtq)
            else:
                assert isinstance(col_name, int)
                pxfp__ech = byln__rjpj.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            byln__rjpj.object_setitem(jdv__tqkrs.parent, pxfp__ech, eqy__xel)
            byln__rjpj.decref(eqy__xel)
            byln__rjpj.decref(pxfp__ech)
            byln__rjpj.gil_release(xmlt__vjz)
        return yahx__zdjm
    xhgya__tpf = DataFrameType(znkvp__upzc, index_typ, column_names,
        df_type.dist, df_type.is_table_format)
    sig = signature(xhgya__tpf, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    yykso__spvte = len(pyval.columns)
    gbh__ynis = []
    for i in range(yykso__spvte):
        jxbj__pkaeh = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            eqy__xel = jxbj__pkaeh.array
        else:
            eqy__xel = jxbj__pkaeh.values
        gbh__ynis.append(eqy__xel)
    gbh__ynis = tuple(gbh__ynis)
    if df_type.is_table_format:
        tfwpv__mcwu = context.get_constant_generic(builder, df_type.
            table_type, Table(gbh__ynis))
        data_tup = lir.Constant.literal_struct([tfwpv__mcwu])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], uag__ogfml) for 
            i, uag__ogfml in enumerate(gbh__ynis)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    mwijv__alnv = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, mwijv__alnv])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    ssqbn__mfh = context.get_constant(types.int64, -1)
    bliwe__ewj = context.get_constant_null(types.voidptr)
    jhr__fqdem = lir.Constant.literal_struct([ssqbn__mfh, bliwe__ewj,
        bliwe__ewj, payload, ssqbn__mfh])
    jhr__fqdem = cgutils.global_constant(builder, '.const.meminfo', jhr__fqdem
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([jhr__fqdem, mwijv__alnv])


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
        glbsc__otgj = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        glbsc__otgj = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, glbsc__otgj)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        adjco__ylxgv = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                adjco__ylxgv)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), adjco__ylxgv)
    elif not fromty.is_table_format and toty.is_table_format:
        adjco__ylxgv = _cast_df_data_to_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        adjco__ylxgv = _cast_df_data_to_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        adjco__ylxgv = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        adjco__ylxgv = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, adjco__ylxgv,
        glbsc__otgj, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    fscgy__afu = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        cjk__lwjb = get_index_data_arr_types(toty.index)[0]
        bvnfg__xylw = bodo.utils.transform.get_type_alloc_counts(cjk__lwjb) - 1
        gpoie__hyou = ', '.join('0' for wdbw__pvnox in range(bvnfg__xylw))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(gpoie__hyou, ', ' if bvnfg__xylw == 1 else ''))
        fscgy__afu['index_arr_type'] = cjk__lwjb
    qyew__lwc = []
    for i, arr_typ in enumerate(toty.data):
        bvnfg__xylw = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        gpoie__hyou = ', '.join('0' for wdbw__pvnox in range(bvnfg__xylw))
        nujdi__xha = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'.
            format(i, gpoie__hyou, ', ' if bvnfg__xylw == 1 else ''))
        qyew__lwc.append(nujdi__xha)
        fscgy__afu[f'arr_type{i}'] = arr_typ
    qyew__lwc = ', '.join(qyew__lwc)
    btc__gcgy = 'def impl():\n'
    keyje__qsv = bodo.hiframes.dataframe_impl._gen_init_df(btc__gcgy, toty.
        columns, qyew__lwc, index, fscgy__afu)
    df = context.compile_internal(builder, keyje__qsv, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    tlh__yyrb = toty.table_type
    tfwpv__mcwu = cgutils.create_struct_proxy(tlh__yyrb)(context, builder)
    tfwpv__mcwu.parent = in_dataframe_payload.parent
    for jlwu__jnia, evwx__raij in tlh__yyrb.type_to_blk.items():
        fzwg__gfwn = context.get_constant(types.int64, len(tlh__yyrb.
            block_to_arr_ind[evwx__raij]))
        wdbw__pvnox, lmae__ijwki = ListInstance.allocate_ex(context,
            builder, types.List(jlwu__jnia), fzwg__gfwn)
        lmae__ijwki.size = fzwg__gfwn
        setattr(tfwpv__mcwu, f'block_{evwx__raij}', lmae__ijwki.value)
    for i, jlwu__jnia in enumerate(fromty.data):
        qzgbw__kisi = toty.data[i]
        if jlwu__jnia != qzgbw__kisi:
            ratty__rtjxm = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ratty__rtjxm)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        pzcxo__hduw = builder.extract_value(in_dataframe_payload.data, i)
        if jlwu__jnia != qzgbw__kisi:
            ixzax__monu = context.cast(builder, pzcxo__hduw, jlwu__jnia,
                qzgbw__kisi)
            ftjn__june = False
        else:
            ixzax__monu = pzcxo__hduw
            ftjn__june = True
        evwx__raij = tlh__yyrb.type_to_blk[jlwu__jnia]
        qwvpt__upmbd = getattr(tfwpv__mcwu, f'block_{evwx__raij}')
        ttpop__vofx = ListInstance(context, builder, types.List(jlwu__jnia),
            qwvpt__upmbd)
        xxbgl__vxyu = context.get_constant(types.int64, tlh__yyrb.
            block_offsets[i])
        ttpop__vofx.setitem(xxbgl__vxyu, ixzax__monu, ftjn__june)
    data_tup = context.make_tuple(builder, types.Tuple([tlh__yyrb]), [
        tfwpv__mcwu._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    gbh__ynis = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            ratty__rtjxm = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ratty__rtjxm)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            pzcxo__hduw = builder.extract_value(in_dataframe_payload.data, i)
            ixzax__monu = context.cast(builder, pzcxo__hduw, fromty.data[i],
                toty.data[i])
            ftjn__june = False
        else:
            ixzax__monu = builder.extract_value(in_dataframe_payload.data, i)
            ftjn__june = True
        if ftjn__june:
            context.nrt.incref(builder, toty.data[i], ixzax__monu)
        gbh__ynis.append(ixzax__monu)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), gbh__ynis)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    aip__glp = fromty.table_type
    cztq__jzyvm = cgutils.create_struct_proxy(aip__glp)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    euc__awypk = toty.table_type
    poxl__ebyy = cgutils.create_struct_proxy(euc__awypk)(context, builder)
    poxl__ebyy.parent = in_dataframe_payload.parent
    for jlwu__jnia, evwx__raij in euc__awypk.type_to_blk.items():
        fzwg__gfwn = context.get_constant(types.int64, len(euc__awypk.
            block_to_arr_ind[evwx__raij]))
        wdbw__pvnox, lmae__ijwki = ListInstance.allocate_ex(context,
            builder, types.List(jlwu__jnia), fzwg__gfwn)
        lmae__ijwki.size = fzwg__gfwn
        setattr(poxl__ebyy, f'block_{evwx__raij}', lmae__ijwki.value)
    for i in range(len(fromty.data)):
        logm__uxn = fromty.data[i]
        qzgbw__kisi = toty.data[i]
        if logm__uxn != qzgbw__kisi:
            ratty__rtjxm = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ratty__rtjxm)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        shhv__kxhw = aip__glp.type_to_blk[logm__uxn]
        unavl__jtk = getattr(cztq__jzyvm, f'block_{shhv__kxhw}')
        rvyaz__daphd = ListInstance(context, builder, types.List(logm__uxn),
            unavl__jtk)
        ejlbw__chhh = context.get_constant(types.int64, aip__glp.
            block_offsets[i])
        pzcxo__hduw = rvyaz__daphd.getitem(ejlbw__chhh)
        if logm__uxn != qzgbw__kisi:
            ixzax__monu = context.cast(builder, pzcxo__hduw, logm__uxn,
                qzgbw__kisi)
            ftjn__june = False
        else:
            ixzax__monu = pzcxo__hduw
            ftjn__june = True
        mdd__cbow = euc__awypk.type_to_blk[jlwu__jnia]
        lmae__ijwki = getattr(poxl__ebyy, f'block_{mdd__cbow}')
        lks__aoa = ListInstance(context, builder, types.List(qzgbw__kisi),
            lmae__ijwki)
        dvgag__qxrw = context.get_constant(types.int64, euc__awypk.
            block_offsets[i])
        lks__aoa.setitem(dvgag__qxrw, ixzax__monu, ftjn__june)
    data_tup = context.make_tuple(builder, types.Tuple([euc__awypk]), [
        poxl__ebyy._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    tlh__yyrb = fromty.table_type
    tfwpv__mcwu = cgutils.create_struct_proxy(tlh__yyrb)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    gbh__ynis = []
    for i, jlwu__jnia in enumerate(toty.data):
        logm__uxn = fromty.data[i]
        if jlwu__jnia != logm__uxn:
            ratty__rtjxm = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ratty__rtjxm)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        evwx__raij = tlh__yyrb.type_to_blk[jlwu__jnia]
        qwvpt__upmbd = getattr(tfwpv__mcwu, f'block_{evwx__raij}')
        ttpop__vofx = ListInstance(context, builder, types.List(jlwu__jnia),
            qwvpt__upmbd)
        xxbgl__vxyu = context.get_constant(types.int64, tlh__yyrb.
            block_offsets[i])
        pzcxo__hduw = ttpop__vofx.getitem(xxbgl__vxyu)
        if jlwu__jnia != logm__uxn:
            ixzax__monu = context.cast(builder, pzcxo__hduw, logm__uxn,
                jlwu__jnia)
            ftjn__june = False
        else:
            ixzax__monu = pzcxo__hduw
            ftjn__june = True
        if ftjn__june:
            context.nrt.incref(builder, jlwu__jnia, ixzax__monu)
        gbh__ynis.append(ixzax__monu)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), gbh__ynis)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    qfm__sovtt, qyew__lwc, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    jybx__evgv = ColNamesMetaType(tuple(qfm__sovtt))
    btc__gcgy = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    btc__gcgy += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(qyew__lwc, index_arg))
    ijk__jua = {}
    exec(btc__gcgy, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': jybx__evgv}, ijk__jua)
    gkhwp__xmqxj = ijk__jua['_init_df']
    return gkhwp__xmqxj


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    xhgya__tpf = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(xhgya__tpf, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    xhgya__tpf = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(xhgya__tpf, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    ali__kaado = ''
    if not is_overload_none(dtype):
        ali__kaado = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        yykso__spvte = (len(data.types) - 1) // 2
        uchc__rubli = [jlwu__jnia.literal_value for jlwu__jnia in data.
            types[1:yykso__spvte + 1]]
        data_val_types = dict(zip(uchc__rubli, data.types[yykso__spvte + 1:]))
        gbh__ynis = ['data[{}]'.format(i) for i in range(yykso__spvte + 1, 
            2 * yykso__spvte + 1)]
        data_dict = dict(zip(uchc__rubli, gbh__ynis))
        if is_overload_none(index):
            for i, jlwu__jnia in enumerate(data.types[yykso__spvte + 1:]):
                if isinstance(jlwu__jnia, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(yykso__spvte + 1 + i))
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
        vhp__vip = '.copy()' if copy else ''
        nkjj__glgph = get_overload_const_list(columns)
        yykso__spvte = len(nkjj__glgph)
        data_val_types = {hdfrz__dmqbx: data.copy(ndim=1) for hdfrz__dmqbx in
            nkjj__glgph}
        gbh__ynis = ['data[:,{}]{}'.format(i, vhp__vip) for i in range(
            yykso__spvte)]
        data_dict = dict(zip(nkjj__glgph, gbh__ynis))
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
    qyew__lwc = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[hdfrz__dmqbx], df_len, ali__kaado) for
        hdfrz__dmqbx in col_names))
    if len(col_names) == 0:
        qyew__lwc = '()'
    return col_names, qyew__lwc, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for hdfrz__dmqbx in col_names:
        if hdfrz__dmqbx in data_dict and is_iterable_type(data_val_types[
            hdfrz__dmqbx]):
            df_len = 'len({})'.format(data_dict[hdfrz__dmqbx])
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
    if all(hdfrz__dmqbx in data_dict for hdfrz__dmqbx in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    voy__jfp = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for hdfrz__dmqbx in col_names:
        if hdfrz__dmqbx not in data_dict:
            data_dict[hdfrz__dmqbx] = voy__jfp


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
            jlwu__jnia = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(jlwu__jnia)
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
        emgqs__lrrez = idx.literal_value
        if isinstance(emgqs__lrrez, int):
            sdtd__xwmpd = tup.types[emgqs__lrrez]
        elif isinstance(emgqs__lrrez, slice):
            sdtd__xwmpd = types.BaseTuple.from_types(tup.types[emgqs__lrrez])
        return signature(sdtd__xwmpd, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    wpvuz__iaet, idx = sig.args
    idx = idx.literal_value
    tup, wdbw__pvnox = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(wpvuz__iaet)
        if not 0 <= idx < len(wpvuz__iaet):
            raise IndexError('cannot index at %d in %s' % (idx, wpvuz__iaet))
        rlja__cudo = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        ptyil__ufx = cgutils.unpack_tuple(builder, tup)[idx]
        rlja__cudo = context.make_tuple(builder, sig.return_type, ptyil__ufx)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, rlja__cudo)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, oldni__rbhmp, suffix_x,
            suffix_y, is_join, indicator, wdbw__pvnox, wdbw__pvnox) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        ijl__lbru = {hdfrz__dmqbx: i for i, hdfrz__dmqbx in enumerate(left_on)}
        irwlt__xxz = {hdfrz__dmqbx: i for i, hdfrz__dmqbx in enumerate(
            right_on)}
        npw__xjm = set(left_on) & set(right_on)
        vjvgu__mwon = set(left_df.columns) & set(right_df.columns)
        rbrx__npfd = vjvgu__mwon - npw__xjm
        jnw__rzakt = '$_bodo_index_' in left_on
        qoam__kpg = '$_bodo_index_' in right_on
        how = get_overload_const_str(oldni__rbhmp)
        imp__yfgj = how in {'left', 'outer'}
        wxweu__yzax = how in {'right', 'outer'}
        columns = []
        data = []
        if jnw__rzakt:
            tzl__kili = bodo.utils.typing.get_index_data_arr_types(left_df.
                index)[0]
        else:
            tzl__kili = left_df.data[left_df.column_index[left_on[0]]]
        if qoam__kpg:
            veigb__jpma = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            veigb__jpma = right_df.data[right_df.column_index[right_on[0]]]
        if jnw__rzakt and not qoam__kpg and not is_join.literal_value:
            rhmij__nbm = right_on[0]
            if rhmij__nbm in left_df.column_index:
                columns.append(rhmij__nbm)
                if (veigb__jpma == bodo.dict_str_arr_type and tzl__kili ==
                    bodo.string_array_type):
                    pqgf__bho = bodo.string_array_type
                else:
                    pqgf__bho = veigb__jpma
                data.append(pqgf__bho)
        if qoam__kpg and not jnw__rzakt and not is_join.literal_value:
            ekg__qag = left_on[0]
            if ekg__qag in right_df.column_index:
                columns.append(ekg__qag)
                if (tzl__kili == bodo.dict_str_arr_type and veigb__jpma ==
                    bodo.string_array_type):
                    pqgf__bho = bodo.string_array_type
                else:
                    pqgf__bho = tzl__kili
                data.append(pqgf__bho)
        for logm__uxn, jxbj__pkaeh in zip(left_df.data, left_df.columns):
            columns.append(str(jxbj__pkaeh) + suffix_x.literal_value if 
                jxbj__pkaeh in rbrx__npfd else jxbj__pkaeh)
            if jxbj__pkaeh in npw__xjm:
                if logm__uxn == bodo.dict_str_arr_type:
                    logm__uxn = right_df.data[right_df.column_index[
                        jxbj__pkaeh]]
                data.append(logm__uxn)
            else:
                if (logm__uxn == bodo.dict_str_arr_type and jxbj__pkaeh in
                    ijl__lbru):
                    if qoam__kpg:
                        logm__uxn = veigb__jpma
                    else:
                        mgp__qqxid = ijl__lbru[jxbj__pkaeh]
                        soxal__clled = right_on[mgp__qqxid]
                        logm__uxn = right_df.data[right_df.column_index[
                            soxal__clled]]
                if wxweu__yzax:
                    logm__uxn = to_nullable_type(logm__uxn)
                data.append(logm__uxn)
        for logm__uxn, jxbj__pkaeh in zip(right_df.data, right_df.columns):
            if jxbj__pkaeh not in npw__xjm:
                columns.append(str(jxbj__pkaeh) + suffix_y.literal_value if
                    jxbj__pkaeh in rbrx__npfd else jxbj__pkaeh)
                if (logm__uxn == bodo.dict_str_arr_type and jxbj__pkaeh in
                    irwlt__xxz):
                    if jnw__rzakt:
                        logm__uxn = tzl__kili
                    else:
                        mgp__qqxid = irwlt__xxz[jxbj__pkaeh]
                        hoa__qel = left_on[mgp__qqxid]
                        logm__uxn = left_df.data[left_df.column_index[hoa__qel]
                            ]
                if imp__yfgj:
                    logm__uxn = to_nullable_type(logm__uxn)
                data.append(logm__uxn)
        ucyk__dxsu = get_overload_const_bool(indicator)
        if ucyk__dxsu:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        eqxyz__cgkv = False
        if jnw__rzakt and qoam__kpg and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            eqxyz__cgkv = True
        elif jnw__rzakt and not qoam__kpg:
            index_typ = right_df.index
            eqxyz__cgkv = True
        elif qoam__kpg and not jnw__rzakt:
            index_typ = left_df.index
            eqxyz__cgkv = True
        if eqxyz__cgkv and isinstance(index_typ, bodo.hiframes.pd_index_ext
            .RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        gpcnu__hida = DataFrameType(tuple(data), index_typ, tuple(columns),
            is_table_format=True)
        return signature(gpcnu__hida, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    tez__xgqq = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return tez__xgqq._getvalue()


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
    wvx__xao = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    ibh__rotp = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', wvx__xao, ibh__rotp,
        package_name='pandas', module_name='General')
    btc__gcgy = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        cqxj__fphgs = 0
        qyew__lwc = []
        names = []
        for i, iojx__ghnpz in enumerate(objs.types):
            assert isinstance(iojx__ghnpz, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(iojx__ghnpz, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                iojx__ghnpz, 'pandas.concat()')
            if isinstance(iojx__ghnpz, SeriesType):
                names.append(str(cqxj__fphgs))
                cqxj__fphgs += 1
                qyew__lwc.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(iojx__ghnpz.columns)
                for hlr__lkmnd in range(len(iojx__ghnpz.data)):
                    qyew__lwc.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, hlr__lkmnd))
        return bodo.hiframes.dataframe_impl._gen_init_df(btc__gcgy, names,
            ', '.join(qyew__lwc), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(jlwu__jnia, DataFrameType) for jlwu__jnia in
            objs.types)
        zaiw__rhbh = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            zaiw__rhbh.extend(df.columns)
        zaiw__rhbh = list(dict.fromkeys(zaiw__rhbh).keys())
        kcefb__pfp = {}
        for cqxj__fphgs, hdfrz__dmqbx in enumerate(zaiw__rhbh):
            for i, df in enumerate(objs.types):
                if hdfrz__dmqbx in df.column_index:
                    kcefb__pfp[f'arr_typ{cqxj__fphgs}'] = df.data[df.
                        column_index[hdfrz__dmqbx]]
                    break
        assert len(kcefb__pfp) == len(zaiw__rhbh)
        vfx__yge = []
        for cqxj__fphgs, hdfrz__dmqbx in enumerate(zaiw__rhbh):
            args = []
            for i, df in enumerate(objs.types):
                if hdfrz__dmqbx in df.column_index:
                    uyn__zgqga = df.column_index[hdfrz__dmqbx]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, uyn__zgqga))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, cqxj__fphgs))
            btc__gcgy += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(cqxj__fphgs, ', '.join(args)))
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
        return bodo.hiframes.dataframe_impl._gen_init_df(btc__gcgy,
            zaiw__rhbh, ', '.join('A{}'.format(i) for i in range(len(
            zaiw__rhbh))), index, kcefb__pfp)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(jlwu__jnia, SeriesType) for jlwu__jnia in
            objs.types)
        btc__gcgy += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            btc__gcgy += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            btc__gcgy += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        btc__gcgy += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        ijk__jua = {}
        exec(btc__gcgy, {'bodo': bodo, 'np': np, 'numba': numba}, ijk__jua)
        return ijk__jua['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for cqxj__fphgs, hdfrz__dmqbx in enumerate(df_type.columns):
            btc__gcgy += '  arrs{} = []\n'.format(cqxj__fphgs)
            btc__gcgy += '  for i in range(len(objs)):\n'
            btc__gcgy += '    df = objs[i]\n'
            btc__gcgy += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(cqxj__fphgs))
            btc__gcgy += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(cqxj__fphgs))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            btc__gcgy += '  arrs_index = []\n'
            btc__gcgy += '  for i in range(len(objs)):\n'
            btc__gcgy += '    df = objs[i]\n'
            btc__gcgy += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(btc__gcgy, df_type
            .columns, ', '.join('out_arr{}'.format(i) for i in range(len(
            df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        btc__gcgy += '  arrs = []\n'
        btc__gcgy += '  for i in range(len(objs)):\n'
        btc__gcgy += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        btc__gcgy += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            btc__gcgy += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            btc__gcgy += '  arrs_index = []\n'
            btc__gcgy += '  for i in range(len(objs)):\n'
            btc__gcgy += '    S = objs[i]\n'
            btc__gcgy += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            btc__gcgy += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        btc__gcgy += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        ijk__jua = {}
        exec(btc__gcgy, {'bodo': bodo, 'np': np, 'numba': numba}, ijk__jua)
        return ijk__jua['impl']
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
        xhgya__tpf = df.copy(index=index)
        return signature(xhgya__tpf, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    cveqp__ptjmr = cgutils.create_struct_proxy(sig.return_type)(context,
        builder)
    return cveqp__ptjmr._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    wvx__xao = dict(index=index, name=name)
    ibh__rotp = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', wvx__xao, ibh__rotp,
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
        kcefb__pfp = (types.Array(types.int64, 1, 'C'),) + df.data
        kelq__orbi = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, kcefb__pfp)
        return signature(kelq__orbi, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    cveqp__ptjmr = cgutils.create_struct_proxy(sig.return_type)(context,
        builder)
    return cveqp__ptjmr._getvalue()


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
    cveqp__ptjmr = cgutils.create_struct_proxy(sig.return_type)(context,
        builder)
    return cveqp__ptjmr._getvalue()


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
    cveqp__ptjmr = cgutils.create_struct_proxy(sig.return_type)(context,
        builder)
    return cveqp__ptjmr._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    mqd__jziv = get_overload_const_bool(check_duplicates)
    ircbh__hyv = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    mhb__irbr = len(value_names) > 1
    zom__jpkk = None
    cbmc__ygls = None
    uil__samw = None
    malpb__vlw = None
    utqgu__ioisu = isinstance(values_tup, types.UniTuple)
    if utqgu__ioisu:
        lpl__qpz = [to_str_arr_if_dict_array(to_nullable_type(values_tup.
            dtype))]
    else:
        lpl__qpz = [to_str_arr_if_dict_array(to_nullable_type(aegl__ihem)) for
            aegl__ihem in values_tup]
    btc__gcgy = 'def impl(\n'
    btc__gcgy += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, _constant_pivot_values=None, parallel=False
"""
    btc__gcgy += '):\n'
    btc__gcgy += '    if parallel:\n'
    kewh__yvpqn = ', '.join([f'array_to_info(index_tup[{i}])' for i in
        range(len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for i in
        range(len(columns_tup))] + [f'array_to_info(values_tup[{i}])' for i in
        range(len(values_tup))])
    btc__gcgy += f'        info_list = [{kewh__yvpqn}]\n'
    btc__gcgy += '        cpp_table = arr_info_list_to_table(info_list)\n'
    btc__gcgy += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
    mvlc__sof = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
         for i in range(len(index_tup))])
    euc__dtigx = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
         for i in range(len(columns_tup))])
    bqn__gvz = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
         for i in range(len(values_tup))])
    btc__gcgy += f'        index_tup = ({mvlc__sof},)\n'
    btc__gcgy += f'        columns_tup = ({euc__dtigx},)\n'
    btc__gcgy += f'        values_tup = ({bqn__gvz},)\n'
    btc__gcgy += '        delete_table(cpp_table)\n'
    btc__gcgy += '        delete_table(out_cpp_table)\n'
    btc__gcgy += '    columns_arr = columns_tup[0]\n'
    if utqgu__ioisu:
        btc__gcgy += '    values_arrs = [arr for arr in values_tup]\n'
    yrgt__xlak = ', '.join([
        f'bodo.utils.typing.decode_if_dict_array(index_tup[{i}])' for i in
        range(len(index_tup))])
    btc__gcgy += f'    new_index_tup = ({yrgt__xlak},)\n'
    btc__gcgy += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    btc__gcgy += '        new_index_tup\n'
    btc__gcgy += '    )\n'
    btc__gcgy += '    n_rows = len(unique_index_arr_tup[0])\n'
    btc__gcgy += '    num_values_arrays = len(values_tup)\n'
    btc__gcgy += '    n_unique_pivots = len(pivot_values)\n'
    if utqgu__ioisu:
        btc__gcgy += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        btc__gcgy += '    n_cols = n_unique_pivots\n'
    btc__gcgy += '    col_map = {}\n'
    btc__gcgy += '    for i in range(n_unique_pivots):\n'
    btc__gcgy += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    btc__gcgy += '            raise ValueError(\n'
    btc__gcgy += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    btc__gcgy += '            )\n'
    btc__gcgy += '        col_map[pivot_values[i]] = i\n'
    avmt__dpi = False
    for i, tojm__afpj in enumerate(lpl__qpz):
        if is_str_arr_type(tojm__afpj):
            avmt__dpi = True
            btc__gcgy += (
                f'    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]\n'
                )
            btc__gcgy += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if avmt__dpi:
        if mqd__jziv:
            btc__gcgy += '    nbytes = (n_rows + 7) >> 3\n'
            btc__gcgy += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        btc__gcgy += '    for i in range(len(columns_arr)):\n'
        btc__gcgy += '        col_name = columns_arr[i]\n'
        btc__gcgy += '        pivot_idx = col_map[col_name]\n'
        btc__gcgy += '        row_idx = row_vector[i]\n'
        if mqd__jziv:
            btc__gcgy += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            btc__gcgy += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            btc__gcgy += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            btc__gcgy += '        else:\n'
            btc__gcgy += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if utqgu__ioisu:
            btc__gcgy += '        for j in range(num_values_arrays):\n'
            btc__gcgy += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            btc__gcgy += '            len_arr = len_arrs_0[col_idx]\n'
            btc__gcgy += '            values_arr = values_arrs[j]\n'
            btc__gcgy += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            btc__gcgy += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            btc__gcgy += '                len_arr[row_idx] = str_val_len\n'
            btc__gcgy += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, tojm__afpj in enumerate(lpl__qpz):
                if is_str_arr_type(tojm__afpj):
                    btc__gcgy += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    btc__gcgy += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    btc__gcgy += (
                        f'            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}\n'
                        )
                    btc__gcgy += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    for i, tojm__afpj in enumerate(lpl__qpz):
        if is_str_arr_type(tojm__afpj):
            btc__gcgy += f'    data_arrs_{i} = [\n'
            btc__gcgy += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            btc__gcgy += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            btc__gcgy += '        )\n'
            btc__gcgy += '        for i in range(n_cols)\n'
            btc__gcgy += '    ]\n'
        else:
            btc__gcgy += f'    data_arrs_{i} = [\n'
            btc__gcgy += (
                f'        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})\n'
                )
            btc__gcgy += '        for _ in range(n_cols)\n'
            btc__gcgy += '    ]\n'
    if not avmt__dpi and mqd__jziv:
        btc__gcgy += '    nbytes = (n_rows + 7) >> 3\n'
        btc__gcgy += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    btc__gcgy += '    for i in range(len(columns_arr)):\n'
    btc__gcgy += '        col_name = columns_arr[i]\n'
    btc__gcgy += '        pivot_idx = col_map[col_name]\n'
    btc__gcgy += '        row_idx = row_vector[i]\n'
    if not avmt__dpi and mqd__jziv:
        btc__gcgy += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        btc__gcgy += (
            '        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):\n'
            )
        btc__gcgy += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        btc__gcgy += '        else:\n'
        btc__gcgy += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if utqgu__ioisu:
        btc__gcgy += '        for j in range(num_values_arrays):\n'
        btc__gcgy += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        btc__gcgy += '            col_arr = data_arrs_0[col_idx]\n'
        btc__gcgy += '            values_arr = values_arrs[j]\n'
        btc__gcgy += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        btc__gcgy += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        btc__gcgy += '            else:\n'
        btc__gcgy += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, tojm__afpj in enumerate(lpl__qpz):
            btc__gcgy += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            btc__gcgy += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            btc__gcgy += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            btc__gcgy += f'        else:\n'
            btc__gcgy += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        btc__gcgy += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        zom__jpkk = index_names.meta[0]
    else:
        btc__gcgy += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        zom__jpkk = tuple(index_names.meta)
    if not ircbh__hyv:
        uil__samw = columns_name.meta[0]
        if mhb__irbr:
            btc__gcgy += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            cbmc__ygls = value_names.meta
            if all(isinstance(hdfrz__dmqbx, str) for hdfrz__dmqbx in cbmc__ygls
                ):
                cbmc__ygls = pd.array(cbmc__ygls, 'string')
            elif all(isinstance(hdfrz__dmqbx, int) for hdfrz__dmqbx in
                cbmc__ygls):
                cbmc__ygls = np.array(cbmc__ygls, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(cbmc__ygls.dtype, pd.StringDtype):
                btc__gcgy += '    total_chars = 0\n'
                btc__gcgy += f'    for i in range({len(value_names)}):\n'
                btc__gcgy += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                btc__gcgy += '        total_chars += value_name_str_len\n'
                btc__gcgy += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                btc__gcgy += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                btc__gcgy += '    total_chars = 0\n'
                btc__gcgy += '    for i in range(len(pivot_values)):\n'
                btc__gcgy += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                btc__gcgy += '        total_chars += pivot_val_str_len\n'
                btc__gcgy += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                btc__gcgy += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            btc__gcgy += f'    for i in range({len(value_names)}):\n'
            btc__gcgy += '        for j in range(len(pivot_values)):\n'
            btc__gcgy += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            btc__gcgy += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            btc__gcgy += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            btc__gcgy += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    tlh__yyrb = None
    if ircbh__hyv:
        if mhb__irbr:
            pkpis__uuom = []
            for ykbhf__hhacf in _constant_pivot_values.meta:
                for hltm__lyml in value_names.meta:
                    pkpis__uuom.append((ykbhf__hhacf, hltm__lyml))
            column_names = tuple(pkpis__uuom)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        malpb__vlw = ColNamesMetaType(column_names)
        tvo__rqwwp = []
        for aegl__ihem in lpl__qpz:
            tvo__rqwwp.extend([aegl__ihem] * len(_constant_pivot_values))
        cny__qsxuv = tuple(tvo__rqwwp)
        tlh__yyrb = TableType(cny__qsxuv)
        btc__gcgy += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        btc__gcgy += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, aegl__ihem in enumerate(lpl__qpz):
            btc__gcgy += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {tlh__yyrb.type_to_blk[aegl__ihem]})
"""
        btc__gcgy += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        btc__gcgy += '        (table,), index, columns_typ\n'
        btc__gcgy += '    )\n'
    else:
        jsklc__tio = ', '.join(f'data_arrs_{i}' for i in range(len(lpl__qpz)))
        btc__gcgy += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({jsklc__tio},), n_rows)
"""
        btc__gcgy += (
            '    return bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
            )
        btc__gcgy += '        (table,), index, column_index\n'
        btc__gcgy += '    )\n'
    ijk__jua = {}
    smcll__musve = {f'data_arr_typ_{i}': tojm__afpj for i, tojm__afpj in
        enumerate(lpl__qpz)}
    oeeo__meouu = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        tlh__yyrb, 'columns_typ': malpb__vlw, 'index_names_lit': zom__jpkk,
        'value_names_lit': cbmc__ygls, 'columns_name_lit': uil__samw, **
        smcll__musve}
    exec(btc__gcgy, oeeo__meouu, ijk__jua)
    impl = ijk__jua['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    vgl__kla = {}
    vgl__kla['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, xfd__ebrp in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        saw__sihxl = None
        if isinstance(xfd__ebrp, bodo.DatetimeArrayType):
            nmhj__srydp = 'datetimetz'
            xzgz__qoz = 'datetime64[ns]'
            if isinstance(xfd__ebrp.tz, int):
                ikem__auwdc = (bodo.libs.pd_datetime_arr_ext.
                    nanoseconds_to_offset(xfd__ebrp.tz))
            else:
                ikem__auwdc = pd.DatetimeTZDtype(tz=xfd__ebrp.tz).tz
            saw__sihxl = {'timezone': pa.lib.tzinfo_to_string(ikem__auwdc)}
        elif isinstance(xfd__ebrp, types.Array) or xfd__ebrp == boolean_array:
            nmhj__srydp = xzgz__qoz = xfd__ebrp.dtype.name
            if xzgz__qoz.startswith('datetime'):
                nmhj__srydp = 'datetime'
        elif is_str_arr_type(xfd__ebrp):
            nmhj__srydp = 'unicode'
            xzgz__qoz = 'object'
        elif xfd__ebrp == binary_array_type:
            nmhj__srydp = 'bytes'
            xzgz__qoz = 'object'
        elif isinstance(xfd__ebrp, DecimalArrayType):
            nmhj__srydp = xzgz__qoz = 'object'
        elif isinstance(xfd__ebrp, IntegerArrayType):
            mwgxl__fqt = xfd__ebrp.dtype.name
            if mwgxl__fqt.startswith('int'):
                nmhj__srydp = 'Int' + mwgxl__fqt[3:]
            elif mwgxl__fqt.startswith('uint'):
                nmhj__srydp = 'UInt' + mwgxl__fqt[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, xfd__ebrp))
            xzgz__qoz = xfd__ebrp.dtype.name
        elif xfd__ebrp == datetime_date_array_type:
            nmhj__srydp = 'datetime'
            xzgz__qoz = 'object'
        elif isinstance(xfd__ebrp, (StructArrayType, ArrayItemArrayType)):
            nmhj__srydp = 'object'
            xzgz__qoz = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, xfd__ebrp))
        ckkc__gbd = {'name': col_name, 'field_name': col_name,
            'pandas_type': nmhj__srydp, 'numpy_type': xzgz__qoz, 'metadata':
            saw__sihxl}
        vgl__kla['columns'].append(ckkc__gbd)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            llfem__yui = '__index_level_0__'
            bgrk__zutq = None
        else:
            llfem__yui = '%s'
            bgrk__zutq = '%s'
        vgl__kla['index_columns'] = [llfem__yui]
        vgl__kla['columns'].append({'name': bgrk__zutq, 'field_name':
            llfem__yui, 'pandas_type': index.pandas_type_name, 'numpy_type':
            index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        vgl__kla['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        vgl__kla['index_columns'] = []
    vgl__kla['pandas_version'] = pd.__version__
    return vgl__kla


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
        jpne__cagmu = []
        for pvego__qjiaw in partition_cols:
            try:
                idx = df.columns.index(pvego__qjiaw)
            except ValueError as zxhu__lurf:
                raise BodoError(
                    f'Partition column {pvego__qjiaw} is not in dataframe')
            jpne__cagmu.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    kiur__mbz = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType)
    obhf__msl = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not kiur__mbz)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not kiur__mbz or is_overload_true
        (_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and kiur__mbz and not is_overload_true(_is_parallel)
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
        cfc__luczj = df.runtime_data_types
        arg__uphwn = len(cfc__luczj)
        saw__sihxl = gen_pandas_parquet_metadata([''] * arg__uphwn,
            cfc__luczj, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        iqpwl__kibkr = saw__sihxl['columns'][:arg__uphwn]
        saw__sihxl['columns'] = saw__sihxl['columns'][arg__uphwn:]
        iqpwl__kibkr = [json.dumps(hpnk__hobi).replace('""', '{0}') for
            hpnk__hobi in iqpwl__kibkr]
        cixj__ppq = json.dumps(saw__sihxl)
        uop__pll = '"columns": ['
        boo__yjrz = cixj__ppq.find(uop__pll)
        if boo__yjrz == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        zoml__use = boo__yjrz + len(uop__pll)
        dqb__jcln = cixj__ppq[:zoml__use]
        cixj__ppq = cixj__ppq[zoml__use:]
        hrq__eyet = len(saw__sihxl['columns'])
    else:
        cixj__ppq = json.dumps(gen_pandas_parquet_metadata(df.columns, df.
            data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and kiur__mbz:
        cixj__ppq = cixj__ppq.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            cixj__ppq = cixj__ppq.replace('"%s"', '%s')
    if not df.is_table_format:
        qyew__lwc = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    btc__gcgy = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _is_parallel=False):
"""
    if df.is_table_format:
        btc__gcgy += '    py_table = get_dataframe_table(df)\n'
        btc__gcgy += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        btc__gcgy += '    info_list = [{}]\n'.format(qyew__lwc)
        btc__gcgy += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        btc__gcgy += '    columns_index = get_dataframe_column_names(df)\n'
        btc__gcgy += '    names_arr = index_to_array(columns_index)\n'
        btc__gcgy += '    col_names = array_to_info(names_arr)\n'
    else:
        btc__gcgy += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and obhf__msl:
        btc__gcgy += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        mgfok__xvamz = True
    else:
        btc__gcgy += '    index_col = array_to_info(np.empty(0))\n'
        mgfok__xvamz = False
    if df.has_runtime_cols:
        btc__gcgy += '    columns_lst = []\n'
        btc__gcgy += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            btc__gcgy += f'    for _ in range(len(py_table.block_{i})):\n'
            btc__gcgy += f"""        columns_lst.append({iqpwl__kibkr[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            btc__gcgy += '        num_cols += 1\n'
        if hrq__eyet:
            btc__gcgy += "    columns_lst.append('')\n"
        btc__gcgy += '    columns_str = ", ".join(columns_lst)\n'
        btc__gcgy += ('    metadata = """' + dqb__jcln +
            '""" + columns_str + """' + cixj__ppq + '"""\n')
    else:
        btc__gcgy += '    metadata = """' + cixj__ppq + '"""\n'
    btc__gcgy += '    if compression is None:\n'
    btc__gcgy += "        compression = 'none'\n"
    btc__gcgy += '    if df.index.name is not None:\n'
    btc__gcgy += '        name_ptr = df.index.name\n'
    btc__gcgy += '    else:\n'
    btc__gcgy += "        name_ptr = 'null'\n"
    btc__gcgy += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    yufv__ruff = None
    if partition_cols:
        yufv__ruff = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        zfgj__imbjm = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in jpne__cagmu)
        if zfgj__imbjm:
            btc__gcgy += '    cat_info_list = [{}]\n'.format(zfgj__imbjm)
            btc__gcgy += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            btc__gcgy += '    cat_table = table\n'
        btc__gcgy += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        btc__gcgy += (
            f'    part_cols_idxs = np.array({jpne__cagmu}, dtype=np.int32)\n')
        btc__gcgy += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        btc__gcgy += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        btc__gcgy += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        btc__gcgy += (
            '                            unicode_to_utf8(compression),\n')
        btc__gcgy += '                            _is_parallel,\n'
        btc__gcgy += (
            '                            unicode_to_utf8(bucket_region),\n')
        btc__gcgy += '                            row_group_size)\n'
        btc__gcgy += '    delete_table_decref_arrays(table)\n'
        btc__gcgy += '    delete_info_decref_array(index_col)\n'
        btc__gcgy += '    delete_info_decref_array(col_names_no_partitions)\n'
        btc__gcgy += '    delete_info_decref_array(col_names)\n'
        if zfgj__imbjm:
            btc__gcgy += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        btc__gcgy += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        btc__gcgy += (
            '                            table, col_names, index_col,\n')
        btc__gcgy += '                            ' + str(mgfok__xvamz) + ',\n'
        btc__gcgy += '                            unicode_to_utf8(metadata),\n'
        btc__gcgy += (
            '                            unicode_to_utf8(compression),\n')
        btc__gcgy += (
            '                            _is_parallel, 1, df.index.start,\n')
        btc__gcgy += (
            '                            df.index.stop, df.index.step,\n')
        btc__gcgy += '                            unicode_to_utf8(name_ptr),\n'
        btc__gcgy += (
            '                            unicode_to_utf8(bucket_region),\n')
        btc__gcgy += '                            row_group_size)\n'
        btc__gcgy += '    delete_table_decref_arrays(table)\n'
        btc__gcgy += '    delete_info_decref_array(index_col)\n'
        btc__gcgy += '    delete_info_decref_array(col_names)\n'
    else:
        btc__gcgy += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        btc__gcgy += (
            '                            table, col_names, index_col,\n')
        btc__gcgy += '                            ' + str(mgfok__xvamz) + ',\n'
        btc__gcgy += '                            unicode_to_utf8(metadata),\n'
        btc__gcgy += (
            '                            unicode_to_utf8(compression),\n')
        btc__gcgy += '                            _is_parallel, 0, 0, 0, 0,\n'
        btc__gcgy += '                            unicode_to_utf8(name_ptr),\n'
        btc__gcgy += (
            '                            unicode_to_utf8(bucket_region),\n')
        btc__gcgy += '                            row_group_size)\n'
        btc__gcgy += '    delete_table_decref_arrays(table)\n'
        btc__gcgy += '    delete_info_decref_array(index_col)\n'
        btc__gcgy += '    delete_info_decref_array(col_names)\n'
    ijk__jua = {}
    if df.has_runtime_cols:
        hjp__kxxad = None
    else:
        for jxbj__pkaeh in df.columns:
            if not isinstance(jxbj__pkaeh, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        hjp__kxxad = pd.array(df.columns)
    exec(btc__gcgy, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': hjp__kxxad,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': yufv__ruff, 'get_dataframe_column_names':
        get_dataframe_column_names, 'fix_arr_dtype': fix_arr_dtype,
        'decode_if_dict_array': decode_if_dict_array,
        'decode_if_dict_table': decode_if_dict_table}, ijk__jua)
    rvn__skrbi = ijk__jua['df_to_parquet']
    return rvn__skrbi


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    wzgwq__stjym = 'all_ok'
    lroh__ubr, lprxx__zdwow = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        xzq__ipmhi = 100
        if chunksize is None:
            zzhtb__ibl = xzq__ipmhi
        else:
            zzhtb__ibl = min(chunksize, xzq__ipmhi)
        if _is_table_create:
            df = df.iloc[:zzhtb__ibl, :]
        else:
            df = df.iloc[zzhtb__ibl:, :]
            if len(df) == 0:
                return wzgwq__stjym
    kczj__plkzc = df.columns
    try:
        if lroh__ubr == 'snowflake':
            if lprxx__zdwow and con.count(lprxx__zdwow) == 1:
                con = con.replace(lprxx__zdwow, quote(lprxx__zdwow))
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
                df.columns = [(hdfrz__dmqbx.upper() if hdfrz__dmqbx.islower
                    () else hdfrz__dmqbx) for hdfrz__dmqbx in df.columns]
            except ImportError as zxhu__lurf:
                wzgwq__stjym = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return wzgwq__stjym
        if lroh__ubr == 'oracle':
            import os
            import sqlalchemy as sa
            from sqlalchemy.dialects.oracle import VARCHAR2
            zsfd__sxbp = os.environ.get('BODO_DISABLE_ORACLE_VARCHAR2', None)
            izh__htoe = bodo.typeof(df)
            cca__eiev = {}
            for hdfrz__dmqbx, hmtqd__hwqo in zip(izh__htoe.columns,
                izh__htoe.data):
                if df[hdfrz__dmqbx].dtype == 'object':
                    if hmtqd__hwqo == datetime_date_array_type:
                        cca__eiev[hdfrz__dmqbx] = sa.types.Date
                    elif hmtqd__hwqo in (bodo.string_array_type, bodo.
                        dict_str_arr_type) and (not zsfd__sxbp or 
                        zsfd__sxbp == '0'):
                        cca__eiev[hdfrz__dmqbx] = VARCHAR2(4000)
            dtype = cca__eiev
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as hklye__mlgvh:
            wzgwq__stjym = hklye__mlgvh.args[0]
            if lroh__ubr == 'oracle' and 'ORA-12899' in wzgwq__stjym:
                wzgwq__stjym += """
                String is larger than VARCHAR2 maximum length.
                Please set environment variable `BODO_DISABLE_ORACLE_VARCHAR2` to
                disable Bodo's optimziation use of VARCHA2.
                NOTE: Oracle `to_sql` with CLOB datatypes is known to be really slow.
                """
        return wzgwq__stjym
    finally:
        df.columns = kczj__plkzc


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
        hgznx__wqhf = bodo.libs.distributed_api.get_rank()
        wzgwq__stjym = 'unset'
        if hgznx__wqhf != 0:
            wzgwq__stjym = bcast_scalar(wzgwq__stjym)
        elif hgznx__wqhf == 0:
            wzgwq__stjym = to_sql_exception_guard_encaps(df, name, con,
                schema, if_exists, index, index_label, chunksize, dtype,
                method, True, _is_parallel)
            wzgwq__stjym = bcast_scalar(wzgwq__stjym)
        if_exists = 'append'
        if _is_parallel and wzgwq__stjym == 'all_ok':
            wzgwq__stjym = to_sql_exception_guard_encaps(df, name, con,
                schema, if_exists, index, index_label, chunksize, dtype,
                method, False, _is_parallel)
        if wzgwq__stjym != 'all_ok':
            print('err_msg=', wzgwq__stjym)
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
        icc__barvz = get_overload_const_str(path_or_buf)
        if icc__barvz.endswith(('.gz', '.bz2', '.zip', '.xz')):
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
        hyb__fstbg = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(hyb__fstbg))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(hyb__fstbg))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    iymnd__graxd = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    dil__mbq = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', iymnd__graxd, dil__mbq,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    btc__gcgy = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        was__cagda = data.data.dtype.categories
        btc__gcgy += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        was__cagda = data.dtype.categories
        btc__gcgy += '  data_values = data\n'
    yykso__spvte = len(was__cagda)
    btc__gcgy += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    btc__gcgy += '  numba.parfors.parfor.init_prange()\n'
    btc__gcgy += '  n = len(data_values)\n'
    for i in range(yykso__spvte):
        btc__gcgy += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    btc__gcgy += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    btc__gcgy += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for hlr__lkmnd in range(yykso__spvte):
        btc__gcgy += '          data_arr_{}[i] = 0\n'.format(hlr__lkmnd)
    btc__gcgy += '      else:\n'
    for sprq__czelf in range(yykso__spvte):
        btc__gcgy += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            sprq__czelf)
    qyew__lwc = ', '.join(f'data_arr_{i}' for i in range(yykso__spvte))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(was__cagda[0], np.datetime64):
        was__cagda = tuple(pd.Timestamp(hdfrz__dmqbx) for hdfrz__dmqbx in
            was__cagda)
    elif isinstance(was__cagda[0], np.timedelta64):
        was__cagda = tuple(pd.Timedelta(hdfrz__dmqbx) for hdfrz__dmqbx in
            was__cagda)
    return bodo.hiframes.dataframe_impl._gen_init_df(btc__gcgy, was__cagda,
        qyew__lwc, index)


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
    for qrezg__rvw in pd_unsupported:
        zugv__exih = mod_name + '.' + qrezg__rvw.__name__
        overload(qrezg__rvw, no_unliteral=True)(create_unsupported_overload
            (zugv__exih))


def _install_dataframe_unsupported():
    for nenea__amc in dataframe_unsupported_attrs:
        iqto__mrbx = 'DataFrame.' + nenea__amc
        overload_attribute(DataFrameType, nenea__amc)(
            create_unsupported_overload(iqto__mrbx))
    for zugv__exih in dataframe_unsupported:
        iqto__mrbx = 'DataFrame.' + zugv__exih + '()'
        overload_method(DataFrameType, zugv__exih)(create_unsupported_overload
            (iqto__mrbx))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
