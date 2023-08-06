"""
Indexing support for pd.DataFrame type.
"""
import operator
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.utils.transform import gen_const_tup
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_list, get_overload_const_str, is_immutable_array, is_list_like_index_type, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, raise_bodo_error


@infer_global(operator.getitem)
class DataFrameGetItemTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        check_runtime_cols_unsupported(args[0], 'DataFrame getitem (df[])')
        if isinstance(args[0], DataFrameType):
            return self.typecheck_df_getitem(args)
        elif isinstance(args[0], DataFrameLocType):
            return self.typecheck_loc_getitem(args)
        else:
            return

    def typecheck_loc_getitem(self, args):
        I = args[0]
        idx = args[1]
        df = I.df_type
        if isinstance(df.columns[0], tuple):
            raise_bodo_error(
                'DataFrame.loc[] getitem (location-based indexing) with multi-indexed columns not supported yet'
                )
        if is_list_like_index_type(idx) and idx.dtype == types.bool_:
            cos__omdg = idx
            uqk__lxq = df.data
            cawlw__opypb = df.columns
            pwyik__kvhw = self.replace_range_with_numeric_idx_if_needed(df,
                cos__omdg)
            afq__nmtx = DataFrameType(uqk__lxq, pwyik__kvhw, cawlw__opypb,
                is_table_format=df.is_table_format)
            return afq__nmtx(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            vnlk__jai = idx.types[0]
            zdy__qgbx = idx.types[1]
            if isinstance(vnlk__jai, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(zdy__qgbx):
                    mao__tjie = get_overload_const_str(zdy__qgbx)
                    if mao__tjie not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, mao__tjie))
                    djm__jtaeb = df.columns.index(mao__tjie)
                    return df.data[djm__jtaeb].dtype(*args)
                if isinstance(zdy__qgbx, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(vnlk__jai
                ) and vnlk__jai.dtype == types.bool_ or isinstance(vnlk__jai,
                types.SliceType):
                pwyik__kvhw = self.replace_range_with_numeric_idx_if_needed(df,
                    vnlk__jai)
                if is_overload_constant_str(zdy__qgbx):
                    rhdab__hloj = get_overload_const_str(zdy__qgbx)
                    if rhdab__hloj not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {rhdab__hloj}'
                            )
                    djm__jtaeb = df.columns.index(rhdab__hloj)
                    jjtss__qshj = df.data[djm__jtaeb]
                    sav__uhyo = jjtss__qshj.dtype
                    pxoxg__hwz = types.literal(df.columns[djm__jtaeb])
                    afq__nmtx = bodo.SeriesType(sav__uhyo, jjtss__qshj,
                        pwyik__kvhw, pxoxg__hwz)
                    return afq__nmtx(*args)
                if isinstance(zdy__qgbx, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(zdy__qgbx):
                    pcx__dqc = get_overload_const_list(zdy__qgbx)
                    zrdm__pygwp = types.unliteral(zdy__qgbx)
                    if zrdm__pygwp.dtype == types.bool_:
                        if len(df.columns) != len(pcx__dqc):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {pcx__dqc} has {len(pcx__dqc)} values'
                                )
                        svfl__iyk = []
                        nslqd__wde = []
                        for rtso__gaubd in range(len(pcx__dqc)):
                            if pcx__dqc[rtso__gaubd]:
                                svfl__iyk.append(df.columns[rtso__gaubd])
                                nslqd__wde.append(df.data[rtso__gaubd])
                        fsqwa__yuccr = tuple()
                        sret__snvf = df.is_table_format and len(svfl__iyk
                            ) > 0 and len(svfl__iyk
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        afq__nmtx = DataFrameType(tuple(nslqd__wde),
                            pwyik__kvhw, tuple(svfl__iyk), is_table_format=
                            sret__snvf)
                        return afq__nmtx(*args)
                    elif zrdm__pygwp.dtype == bodo.string_type:
                        fsqwa__yuccr, nslqd__wde = (
                            get_df_getitem_kept_cols_and_data(df, pcx__dqc))
                        sret__snvf = df.is_table_format and len(pcx__dqc
                            ) > 0 and len(pcx__dqc
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        afq__nmtx = DataFrameType(nslqd__wde, pwyik__kvhw,
                            fsqwa__yuccr, is_table_format=sret__snvf)
                        return afq__nmtx(*args)
        raise_bodo_error(
            f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet. If you are trying to select a subset of the columns by passing a list of column names, that list must be a compile time constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def typecheck_df_getitem(self, args):
        df = args[0]
        ind = args[1]
        if is_overload_constant_str(ind) or is_overload_constant_int(ind):
            ind_val = get_overload_const_str(ind) if is_overload_constant_str(
                ind) else get_overload_const_int(ind)
            if isinstance(df.columns[0], tuple):
                svfl__iyk = []
                nslqd__wde = []
                for rtso__gaubd, liktn__txyj in enumerate(df.columns):
                    if liktn__txyj[0] != ind_val:
                        continue
                    svfl__iyk.append(liktn__txyj[1] if len(liktn__txyj) == 
                        2 else liktn__txyj[1:])
                    nslqd__wde.append(df.data[rtso__gaubd])
                jjtss__qshj = tuple(nslqd__wde)
                vns__ksg = df.index
                ohyl__lxxt = tuple(svfl__iyk)
                afq__nmtx = DataFrameType(jjtss__qshj, vns__ksg, ohyl__lxxt)
                return afq__nmtx(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                djm__jtaeb = df.columns.index(ind_val)
                jjtss__qshj = df.data[djm__jtaeb]
                sav__uhyo = jjtss__qshj.dtype
                vns__ksg = df.index
                pxoxg__hwz = types.literal(df.columns[djm__jtaeb])
                afq__nmtx = bodo.SeriesType(sav__uhyo, jjtss__qshj,
                    vns__ksg, pxoxg__hwz)
                return afq__nmtx(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            jjtss__qshj = df.data
            vns__ksg = self.replace_range_with_numeric_idx_if_needed(df, ind)
            ohyl__lxxt = df.columns
            afq__nmtx = DataFrameType(jjtss__qshj, vns__ksg, ohyl__lxxt,
                is_table_format=df.is_table_format)
            return afq__nmtx(*args)
        elif is_overload_constant_list(ind):
            ijpp__jps = get_overload_const_list(ind)
            ohyl__lxxt, jjtss__qshj = get_df_getitem_kept_cols_and_data(df,
                ijpp__jps)
            vns__ksg = df.index
            sret__snvf = df.is_table_format and len(ijpp__jps) > 0 and len(
                ijpp__jps) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            afq__nmtx = DataFrameType(jjtss__qshj, vns__ksg, ohyl__lxxt,
                is_table_format=sret__snvf)
            return afq__nmtx(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        pwyik__kvhw = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return pwyik__kvhw


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for shjsv__kog in cols_to_keep_list:
        if shjsv__kog not in df.column_index:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(shjsv__kog, df.columns))
    ohyl__lxxt = tuple(cols_to_keep_list)
    jjtss__qshj = tuple(df.data[df.column_index[kvxz__tozy]] for kvxz__tozy in
        ohyl__lxxt)
    return ohyl__lxxt, jjtss__qshj


@lower_builtin(operator.getitem, DataFrameType, types.Any)
def getitem_df_lower(context, builder, sig, args):
    impl = df_getitem_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def df_getitem_overload(df, ind):
    if not isinstance(df, DataFrameType):
        return
    if is_overload_constant_str(ind) or is_overload_constant_int(ind):
        ind_val = get_overload_const_str(ind) if is_overload_constant_str(ind
            ) else get_overload_const_int(ind)
        if isinstance(df.columns[0], tuple):
            svfl__iyk = []
            nslqd__wde = []
            for rtso__gaubd, liktn__txyj in enumerate(df.columns):
                if liktn__txyj[0] != ind_val:
                    continue
                svfl__iyk.append(liktn__txyj[1] if len(liktn__txyj) == 2 else
                    liktn__txyj[1:])
                nslqd__wde.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(rtso__gaubd))
            tfhd__gqj = 'def impl(df, ind):\n'
            nug__oguvv = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(tfhd__gqj,
                svfl__iyk, ', '.join(nslqd__wde), nug__oguvv)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        ijpp__jps = get_overload_const_list(ind)
        for shjsv__kog in ijpp__jps:
            if shjsv__kog not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(shjsv__kog, df.columns))
        lnp__hxxsa = None
        if df.is_table_format and len(ijpp__jps) > 0 and len(ijpp__jps
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            syzgp__ranx = [df.column_index[shjsv__kog] for shjsv__kog in
                ijpp__jps]
            lnp__hxxsa = {'col_nums_meta': bodo.utils.typing.MetaType(tuple
                (syzgp__ranx))}
            nslqd__wde = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, True)'
                )
        else:
            nslqd__wde = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[shjsv__kog]}).copy()'
                 for shjsv__kog in ijpp__jps)
        tfhd__gqj = 'def impl(df, ind):\n'
        nug__oguvv = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(tfhd__gqj,
            ijpp__jps, nslqd__wde, nug__oguvv, extra_globals=lnp__hxxsa)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        tfhd__gqj = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            tfhd__gqj += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        nug__oguvv = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            nslqd__wde = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            nslqd__wde = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[shjsv__kog]})[ind]'
                 for shjsv__kog in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(tfhd__gqj, df.
            columns, nslqd__wde, nug__oguvv)
    raise_bodo_error('df[] getitem using {} not supported'.format(ind))


@overload(operator.setitem, no_unliteral=True)
def df_setitem_overload(df, idx, val):
    check_runtime_cols_unsupported(df, 'DataFrame setitem (df[])')
    if not isinstance(df, DataFrameType):
        return
    raise_bodo_error('DataFrame setitem: transform necessary')


class DataFrameILocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        kvxz__tozy = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(kvxz__tozy)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        lhbl__mersd = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, lhbl__mersd)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        gyz__xzbe, = args
        vpz__ysrk = signature.return_type
        inv__eyqap = cgutils.create_struct_proxy(vpz__ysrk)(context, builder)
        inv__eyqap.obj = gyz__xzbe
        context.nrt.incref(builder, signature.args[0], gyz__xzbe)
        return inv__eyqap._getvalue()
    return DataFrameILocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iloc')
def overload_dataframe_iloc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iloc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iloc(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iloc_getitem(I, idx):
    if not isinstance(I, DataFrameILocType):
        return
    df = I.df_type
    if isinstance(idx, types.Integer):
        return _gen_iloc_getitem_row_impl(df, df.columns, 'idx')
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and not isinstance(
        idx[1], types.SliceType):
        if not (is_overload_constant_list(idx.types[1]) or
            is_overload_constant_int(idx.types[1])):
            raise_bodo_error(
                'idx2 in df.iloc[idx1, idx2] should be a constant integer or constant list of integers. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        klc__yfjk = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            sjpkc__obus = get_overload_const_int(idx.types[1])
            if sjpkc__obus < 0 or sjpkc__obus >= klc__yfjk:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            hbp__oac = [sjpkc__obus]
        else:
            is_out_series = False
            hbp__oac = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= klc__yfjk for
                ind in hbp__oac):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[hbp__oac])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                sjpkc__obus = hbp__oac[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, sjpkc__obus
                        )[idx[0]])
                return impl
            return _gen_iloc_getitem_row_impl(df, col_names, 'idx[0]')
        if is_list_like_index_type(idx.types[0]) and isinstance(idx.types[0
            ].dtype, (types.Integer, types.Boolean)) or isinstance(idx.
            types[0], types.SliceType):
            return _gen_iloc_getitem_bool_slice_impl(df, col_names, idx.
                types[0], 'idx[0]', is_out_series)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, (types.
        Integer, types.Boolean)) or isinstance(idx, types.SliceType):
        return _gen_iloc_getitem_bool_slice_impl(df, df.columns, idx, 'idx',
            False)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):
        raise_bodo_error(
            'slice2 in df.iloc[slice1,slice2] should be constant. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )
    raise_bodo_error(f'df.iloc[] getitem using {idx} not supported')


def _gen_iloc_getitem_bool_slice_impl(df, col_names, idx_typ, idx,
    is_out_series):
    tfhd__gqj = 'def impl(I, idx):\n'
    tfhd__gqj += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        tfhd__gqj += f'  idx_t = {idx}\n'
    else:
        tfhd__gqj += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    nug__oguvv = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    lnp__hxxsa = None
    if df.is_table_format and not is_out_series:
        syzgp__ranx = [df.column_index[shjsv__kog] for shjsv__kog in col_names]
        lnp__hxxsa = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            syzgp__ranx))}
        nslqd__wde = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx_t]'
            )
    else:
        nslqd__wde = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[shjsv__kog]})[idx_t]'
             for shjsv__kog in col_names)
    if is_out_series:
        phrw__gcwmp = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        tfhd__gqj += f"""  return bodo.hiframes.pd_series_ext.init_series({nslqd__wde}, {nug__oguvv}, {phrw__gcwmp})
"""
        yta__qnglm = {}
        exec(tfhd__gqj, {'bodo': bodo}, yta__qnglm)
        return yta__qnglm['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(tfhd__gqj, col_names,
        nslqd__wde, nug__oguvv, extra_globals=lnp__hxxsa)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    tfhd__gqj = 'def impl(I, idx):\n'
    tfhd__gqj += '  df = I._obj\n'
    ocpok__afhpj = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[shjsv__kog]})[{idx}]'
         for shjsv__kog in col_names)
    tfhd__gqj += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    tfhd__gqj += f"""  return bodo.hiframes.pd_series_ext.init_series(({ocpok__afhpj},), row_idx, None)
"""
    yta__qnglm = {}
    exec(tfhd__gqj, {'bodo': bodo}, yta__qnglm)
    impl = yta__qnglm['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def df_iloc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameILocType):
        return
    raise_bodo_error(
        f'DataFrame.iloc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameLocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        kvxz__tozy = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(kvxz__tozy)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        lhbl__mersd = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, lhbl__mersd)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        gyz__xzbe, = args
        zvf__ufgbv = signature.return_type
        dnk__mvx = cgutils.create_struct_proxy(zvf__ufgbv)(context, builder)
        dnk__mvx.obj = gyz__xzbe
        context.nrt.incref(builder, signature.args[0], gyz__xzbe)
        return dnk__mvx._getvalue()
    return DataFrameLocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'loc')
def overload_dataframe_loc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.loc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_loc(df)


@lower_builtin(operator.getitem, DataFrameLocType, types.Any)
def loc_getitem_lower(context, builder, sig, args):
    impl = overload_loc_getitem(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def overload_loc_getitem(I, idx):
    if not isinstance(I, DataFrameLocType):
        return
    df = I.df_type
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        tfhd__gqj = 'def impl(I, idx):\n'
        tfhd__gqj += '  df = I._obj\n'
        tfhd__gqj += '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n'
        nug__oguvv = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        if df.is_table_format:
            nslqd__wde = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[idx_t]'
                )
        else:
            nslqd__wde = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[shjsv__kog]})[idx_t]'
                 for shjsv__kog in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(tfhd__gqj, df.
            columns, nslqd__wde, nug__oguvv)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        sat__qdh = idx.types[1]
        if is_overload_constant_str(sat__qdh):
            jtyn__cxqh = get_overload_const_str(sat__qdh)
            sjpkc__obus = df.columns.index(jtyn__cxqh)

            def impl_col_name(I, idx):
                df = I._obj
                nug__oguvv = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                uir__sxb = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df
                    , sjpkc__obus)
                return bodo.hiframes.pd_series_ext.init_series(uir__sxb,
                    nug__oguvv, jtyn__cxqh).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(sat__qdh):
            col_idx_list = get_overload_const_list(sat__qdh)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(shjsv__kog in df.column_index for
                shjsv__kog in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    col_names = []
    hbp__oac = []
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        for rtso__gaubd, ddlg__jvg in enumerate(col_idx_list):
            if ddlg__jvg:
                hbp__oac.append(rtso__gaubd)
                col_names.append(df.columns[rtso__gaubd])
    else:
        col_names = col_idx_list
        hbp__oac = [df.column_index[shjsv__kog] for shjsv__kog in col_idx_list]
    lnp__hxxsa = None
    if df.is_table_format and len(col_idx_list) > 0 and len(col_idx_list
        ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
        lnp__hxxsa = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            hbp__oac))}
        nslqd__wde = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx[0]]'
            )
    else:
        nslqd__wde = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ind})[idx[0]]'
             for ind in hbp__oac)
    nug__oguvv = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    tfhd__gqj = 'def impl(I, idx):\n'
    tfhd__gqj += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(tfhd__gqj, col_names,
        nslqd__wde, nug__oguvv, extra_globals=lnp__hxxsa)


@overload(operator.setitem, no_unliteral=True)
def df_loc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameLocType):
        return
    raise_bodo_error(
        f'DataFrame.loc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameIatType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        kvxz__tozy = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(kvxz__tozy)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        lhbl__mersd = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, lhbl__mersd)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        gyz__xzbe, = args
        hhgaa__echi = signature.return_type
        wrzj__tja = cgutils.create_struct_proxy(hhgaa__echi)(context, builder)
        wrzj__tja.obj = gyz__xzbe
        context.nrt.incref(builder, signature.args[0], gyz__xzbe)
        return wrzj__tja._getvalue()
    return DataFrameIatType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iat')
def overload_dataframe_iat(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iat')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iat(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iat_getitem(I, idx):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat getitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        sjpkc__obus = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            uir__sxb = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                sjpkc__obus)
            return bodo.utils.conversion.box_if_dt64(uir__sxb[idx[0]])
        return impl_col_ind
    raise BodoError('df.iat[] getitem using {} not supported'.format(idx))


@overload(operator.setitem, no_unliteral=True)
def overload_iat_setitem(I, idx, val):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat setitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        sjpkc__obus = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[sjpkc__obus]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            uir__sxb = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                sjpkc__obus)
            uir__sxb[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    wrzj__tja = cgutils.create_struct_proxy(fromty)(context, builder, val)
    llm__lco = context.cast(builder, wrzj__tja.obj, fromty.df_type, toty.
        df_type)
    vuneb__djpvs = cgutils.create_struct_proxy(toty)(context, builder)
    vuneb__djpvs.obj = llm__lco
    return vuneb__djpvs._getvalue()
