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
            vywkp__osqb = idx
            lfsn__rybty = df.data
            jlpi__nqud = df.columns
            gctlz__aoqpc = self.replace_range_with_numeric_idx_if_needed(df,
                vywkp__osqb)
            yerjh__rjy = DataFrameType(lfsn__rybty, gctlz__aoqpc,
                jlpi__nqud, is_table_format=df.is_table_format)
            return yerjh__rjy(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            powv__nwzdx = idx.types[0]
            ojyp__eoahp = idx.types[1]
            if isinstance(powv__nwzdx, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(ojyp__eoahp):
                    pptb__tyug = get_overload_const_str(ojyp__eoahp)
                    if pptb__tyug not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, pptb__tyug))
                    fweyn__gtw = df.columns.index(pptb__tyug)
                    return df.data[fweyn__gtw].dtype(*args)
                if isinstance(ojyp__eoahp, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(powv__nwzdx
                ) and powv__nwzdx.dtype == types.bool_ or isinstance(
                powv__nwzdx, types.SliceType):
                gctlz__aoqpc = self.replace_range_with_numeric_idx_if_needed(df
                    , powv__nwzdx)
                if is_overload_constant_str(ojyp__eoahp):
                    feq__hwfdd = get_overload_const_str(ojyp__eoahp)
                    if feq__hwfdd not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {feq__hwfdd}'
                            )
                    fweyn__gtw = df.columns.index(feq__hwfdd)
                    dxp__gxp = df.data[fweyn__gtw]
                    qnzxu__jxwp = dxp__gxp.dtype
                    yry__ldn = types.literal(df.columns[fweyn__gtw])
                    yerjh__rjy = bodo.SeriesType(qnzxu__jxwp, dxp__gxp,
                        gctlz__aoqpc, yry__ldn)
                    return yerjh__rjy(*args)
                if isinstance(ojyp__eoahp, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(ojyp__eoahp):
                    niulg__whid = get_overload_const_list(ojyp__eoahp)
                    zjl__uini = types.unliteral(ojyp__eoahp)
                    if zjl__uini.dtype == types.bool_:
                        if len(df.columns) != len(niulg__whid):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {niulg__whid} has {len(niulg__whid)} values'
                                )
                        mqcr__iia = []
                        koj__vztl = []
                        for pmru__vni in range(len(niulg__whid)):
                            if niulg__whid[pmru__vni]:
                                mqcr__iia.append(df.columns[pmru__vni])
                                koj__vztl.append(df.data[pmru__vni])
                        vkd__xeu = tuple()
                        pkcn__omvhk = df.is_table_format and len(mqcr__iia
                            ) > 0 and len(mqcr__iia
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        yerjh__rjy = DataFrameType(tuple(koj__vztl),
                            gctlz__aoqpc, tuple(mqcr__iia), is_table_format
                            =pkcn__omvhk)
                        return yerjh__rjy(*args)
                    elif zjl__uini.dtype == bodo.string_type:
                        vkd__xeu, koj__vztl = (
                            get_df_getitem_kept_cols_and_data(df, niulg__whid))
                        pkcn__omvhk = df.is_table_format and len(niulg__whid
                            ) > 0 and len(niulg__whid
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        yerjh__rjy = DataFrameType(koj__vztl, gctlz__aoqpc,
                            vkd__xeu, is_table_format=pkcn__omvhk)
                        return yerjh__rjy(*args)
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
                mqcr__iia = []
                koj__vztl = []
                for pmru__vni, syglb__hsxj in enumerate(df.columns):
                    if syglb__hsxj[0] != ind_val:
                        continue
                    mqcr__iia.append(syglb__hsxj[1] if len(syglb__hsxj) == 
                        2 else syglb__hsxj[1:])
                    koj__vztl.append(df.data[pmru__vni])
                dxp__gxp = tuple(koj__vztl)
                boe__pdwj = df.index
                pmlt__dcegc = tuple(mqcr__iia)
                yerjh__rjy = DataFrameType(dxp__gxp, boe__pdwj, pmlt__dcegc)
                return yerjh__rjy(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                fweyn__gtw = df.columns.index(ind_val)
                dxp__gxp = df.data[fweyn__gtw]
                qnzxu__jxwp = dxp__gxp.dtype
                boe__pdwj = df.index
                yry__ldn = types.literal(df.columns[fweyn__gtw])
                yerjh__rjy = bodo.SeriesType(qnzxu__jxwp, dxp__gxp,
                    boe__pdwj, yry__ldn)
                return yerjh__rjy(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            dxp__gxp = df.data
            boe__pdwj = self.replace_range_with_numeric_idx_if_needed(df, ind)
            pmlt__dcegc = df.columns
            yerjh__rjy = DataFrameType(dxp__gxp, boe__pdwj, pmlt__dcegc,
                is_table_format=df.is_table_format)
            return yerjh__rjy(*args)
        elif is_overload_constant_list(ind):
            ogw__stgrc = get_overload_const_list(ind)
            pmlt__dcegc, dxp__gxp = get_df_getitem_kept_cols_and_data(df,
                ogw__stgrc)
            boe__pdwj = df.index
            pkcn__omvhk = df.is_table_format and len(ogw__stgrc) > 0 and len(
                ogw__stgrc) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            yerjh__rjy = DataFrameType(dxp__gxp, boe__pdwj, pmlt__dcegc,
                is_table_format=pkcn__omvhk)
            return yerjh__rjy(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        gctlz__aoqpc = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return gctlz__aoqpc


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for nlim__jnx in cols_to_keep_list:
        if nlim__jnx not in df.column_index:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(nlim__jnx, df.columns))
    pmlt__dcegc = tuple(cols_to_keep_list)
    dxp__gxp = tuple(df.data[df.column_index[jzi__ijcr]] for jzi__ijcr in
        pmlt__dcegc)
    return pmlt__dcegc, dxp__gxp


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
            mqcr__iia = []
            koj__vztl = []
            for pmru__vni, syglb__hsxj in enumerate(df.columns):
                if syglb__hsxj[0] != ind_val:
                    continue
                mqcr__iia.append(syglb__hsxj[1] if len(syglb__hsxj) == 2 else
                    syglb__hsxj[1:])
                koj__vztl.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(pmru__vni))
            kcoc__gkey = 'def impl(df, ind):\n'
            ibv__sbczo = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(kcoc__gkey,
                mqcr__iia, ', '.join(koj__vztl), ibv__sbczo)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        ogw__stgrc = get_overload_const_list(ind)
        for nlim__jnx in ogw__stgrc:
            if nlim__jnx not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(nlim__jnx, df.columns))
        oab__ynxh = None
        if df.is_table_format and len(ogw__stgrc) > 0 and len(ogw__stgrc
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            kloa__bvf = [df.column_index[nlim__jnx] for nlim__jnx in ogw__stgrc
                ]
            oab__ynxh = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
                kloa__bvf))}
            koj__vztl = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, True)'
                )
        else:
            koj__vztl = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[nlim__jnx]}).copy()'
                 for nlim__jnx in ogw__stgrc)
        kcoc__gkey = 'def impl(df, ind):\n'
        ibv__sbczo = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(kcoc__gkey,
            ogw__stgrc, koj__vztl, ibv__sbczo, extra_globals=oab__ynxh)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        kcoc__gkey = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            kcoc__gkey += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        ibv__sbczo = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            koj__vztl = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            koj__vztl = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[nlim__jnx]})[ind]'
                 for nlim__jnx in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(kcoc__gkey, df.
            columns, koj__vztl, ibv__sbczo)
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
        jzi__ijcr = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(jzi__ijcr)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hlh__piy = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, hlh__piy)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        lavee__myv, = args
        nxhai__ntgox = signature.return_type
        cap__pfb = cgutils.create_struct_proxy(nxhai__ntgox)(context, builder)
        cap__pfb.obj = lavee__myv
        context.nrt.incref(builder, signature.args[0], lavee__myv)
        return cap__pfb._getvalue()
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
        twpd__sho = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            zbw__fstyo = get_overload_const_int(idx.types[1])
            if zbw__fstyo < 0 or zbw__fstyo >= twpd__sho:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            nemi__sepn = [zbw__fstyo]
        else:
            is_out_series = False
            nemi__sepn = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= twpd__sho for
                ind in nemi__sepn):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[nemi__sepn])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                zbw__fstyo = nemi__sepn[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, zbw__fstyo)
                        [idx[0]])
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
    kcoc__gkey = 'def impl(I, idx):\n'
    kcoc__gkey += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        kcoc__gkey += f'  idx_t = {idx}\n'
    else:
        kcoc__gkey += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    ibv__sbczo = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    oab__ynxh = None
    if df.is_table_format and not is_out_series:
        kloa__bvf = [df.column_index[nlim__jnx] for nlim__jnx in col_names]
        oab__ynxh = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            kloa__bvf))}
        koj__vztl = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx_t]'
            )
    else:
        koj__vztl = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[nlim__jnx]})[idx_t]'
             for nlim__jnx in col_names)
    if is_out_series:
        vjna__rhwno = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        kcoc__gkey += f"""  return bodo.hiframes.pd_series_ext.init_series({koj__vztl}, {ibv__sbczo}, {vjna__rhwno})
"""
        kqsoc__ovby = {}
        exec(kcoc__gkey, {'bodo': bodo}, kqsoc__ovby)
        return kqsoc__ovby['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(kcoc__gkey, col_names,
        koj__vztl, ibv__sbczo, extra_globals=oab__ynxh)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    kcoc__gkey = 'def impl(I, idx):\n'
    kcoc__gkey += '  df = I._obj\n'
    krmy__rqvg = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[nlim__jnx]})[{idx}]'
         for nlim__jnx in col_names)
    kcoc__gkey += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    kcoc__gkey += f"""  return bodo.hiframes.pd_series_ext.init_series(({krmy__rqvg},), row_idx, None)
"""
    kqsoc__ovby = {}
    exec(kcoc__gkey, {'bodo': bodo}, kqsoc__ovby)
    impl = kqsoc__ovby['impl']
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
        jzi__ijcr = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(jzi__ijcr)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hlh__piy = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, hlh__piy)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        lavee__myv, = args
        gah__mlacq = signature.return_type
        uln__lqhuo = cgutils.create_struct_proxy(gah__mlacq)(context, builder)
        uln__lqhuo.obj = lavee__myv
        context.nrt.incref(builder, signature.args[0], lavee__myv)
        return uln__lqhuo._getvalue()
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
        kcoc__gkey = 'def impl(I, idx):\n'
        kcoc__gkey += '  df = I._obj\n'
        kcoc__gkey += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        ibv__sbczo = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        if df.is_table_format:
            koj__vztl = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[idx_t]'
                )
        else:
            koj__vztl = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[nlim__jnx]})[idx_t]'
                 for nlim__jnx in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(kcoc__gkey, df.
            columns, koj__vztl, ibv__sbczo)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        agy__zdpqe = idx.types[1]
        if is_overload_constant_str(agy__zdpqe):
            outsy__yqev = get_overload_const_str(agy__zdpqe)
            zbw__fstyo = df.columns.index(outsy__yqev)

            def impl_col_name(I, idx):
                df = I._obj
                ibv__sbczo = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                xzo__hhn = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df
                    , zbw__fstyo)
                return bodo.hiframes.pd_series_ext.init_series(xzo__hhn,
                    ibv__sbczo, outsy__yqev).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(agy__zdpqe):
            col_idx_list = get_overload_const_list(agy__zdpqe)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(nlim__jnx in df.column_index for
                nlim__jnx in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    col_names = []
    nemi__sepn = []
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        for pmru__vni, zqvkk__qkm in enumerate(col_idx_list):
            if zqvkk__qkm:
                nemi__sepn.append(pmru__vni)
                col_names.append(df.columns[pmru__vni])
    else:
        col_names = col_idx_list
        nemi__sepn = [df.column_index[nlim__jnx] for nlim__jnx in col_idx_list]
    oab__ynxh = None
    if df.is_table_format and len(col_idx_list) > 0 and len(col_idx_list
        ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
        oab__ynxh = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            nemi__sepn))}
        koj__vztl = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx[0]]'
            )
    else:
        koj__vztl = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ind})[idx[0]]'
             for ind in nemi__sepn)
    ibv__sbczo = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    kcoc__gkey = 'def impl(I, idx):\n'
    kcoc__gkey += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(kcoc__gkey, col_names,
        koj__vztl, ibv__sbczo, extra_globals=oab__ynxh)


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
        jzi__ijcr = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(jzi__ijcr)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hlh__piy = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, hlh__piy)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        lavee__myv, = args
        qgd__zbfez = signature.return_type
        shhx__jubnk = cgutils.create_struct_proxy(qgd__zbfez)(context, builder)
        shhx__jubnk.obj = lavee__myv
        context.nrt.incref(builder, signature.args[0], lavee__myv)
        return shhx__jubnk._getvalue()
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
        zbw__fstyo = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            xzo__hhn = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                zbw__fstyo)
            return bodo.utils.conversion.box_if_dt64(xzo__hhn[idx[0]])
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
        zbw__fstyo = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[zbw__fstyo]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            xzo__hhn = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                zbw__fstyo)
            xzo__hhn[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    shhx__jubnk = cgutils.create_struct_proxy(fromty)(context, builder, val)
    shl__rtbv = context.cast(builder, shhx__jubnk.obj, fromty.df_type, toty
        .df_type)
    fcpa__egag = cgutils.create_struct_proxy(toty)(context, builder)
    fcpa__egag.obj = shl__rtbv
    return fcpa__egag._getvalue()
