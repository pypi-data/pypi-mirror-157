"""
Common IR extension functions for connectors such as CSV, Parquet and JSON readers.
"""
from collections import defaultdict
from typing import Literal, Set, Tuple
import numba
from numba.core import ir, types
from numba.core.ir_utils import replace_vars_inner, visit_vars_inner
from numba.extending import box, models, register_model
from bodo.hiframes.table import TableType
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import get_live_column_nums_block
from bodo.utils.typing import BodoError
from bodo.utils.utils import debug_prints


def connector_array_analysis(node, equiv_set, typemap, array_analysis):
    fow__wkt = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    wkcw__irqx = []
    for ztq__acgau in node.out_vars:
        typ = typemap[ztq__acgau.name]
        if typ == types.none:
            continue
        tzc__amjl = array_analysis._gen_shape_call(equiv_set, ztq__acgau,
            typ.ndim, None, fow__wkt)
        equiv_set.insert_equiv(ztq__acgau, tzc__amjl)
        wkcw__irqx.append(tzc__amjl[0])
        equiv_set.define(ztq__acgau, set())
    if len(wkcw__irqx) > 1:
        equiv_set.insert_equiv(*wkcw__irqx)
    return [], fow__wkt


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        tnl__uvrq = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        tnl__uvrq = Distribution.OneD_Var
    else:
        tnl__uvrq = Distribution.OneD
    for uly__eccsx in node.out_vars:
        if uly__eccsx.name in array_dists:
            tnl__uvrq = Distribution(min(tnl__uvrq.value, array_dists[
                uly__eccsx.name].value))
    for uly__eccsx in node.out_vars:
        array_dists[uly__eccsx.name] = tnl__uvrq


def connector_typeinfer(node, typeinferer):
    if node.connector_typ == 'csv':
        if node.chunksize is not None:
            typeinferer.lock_type(node.out_vars[0].name, node.out_types[0],
                loc=node.loc)
        else:
            typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(
                node.out_types)), loc=node.loc)
            typeinferer.lock_type(node.out_vars[1].name, node.
                index_column_typ, loc=node.loc)
        return
    if node.connector_typ in ('parquet', 'sql'):
        typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(node.
            out_types)), loc=node.loc)
        typeinferer.lock_type(node.out_vars[1].name, node.index_column_type,
            loc=node.loc)
        return
    for ztq__acgau, typ in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(ztq__acgau.name, typ, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    eyfv__ihzdc = []
    for ztq__acgau in node.out_vars:
        yqc__bzzzr = visit_vars_inner(ztq__acgau, callback, cbdata)
        eyfv__ihzdc.append(yqc__bzzzr)
    node.out_vars = eyfv__ihzdc
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for ambg__njky in node.filters:
            for cdaw__tps in range(len(ambg__njky)):
                val = ambg__njky[cdaw__tps]
                ambg__njky[cdaw__tps] = val[0], val[1], visit_vars_inner(val
                    [2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({uly__eccsx.name for uly__eccsx in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for set__ddsac in node.filters:
            for uly__eccsx in set__ddsac:
                if isinstance(uly__eccsx[2], ir.Var):
                    use_set.add(uly__eccsx[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    wgvxs__lmhg = set(uly__eccsx.name for uly__eccsx in node.out_vars)
    return set(), wgvxs__lmhg


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    eyfv__ihzdc = []
    for ztq__acgau in node.out_vars:
        yqc__bzzzr = replace_vars_inner(ztq__acgau, var_dict)
        eyfv__ihzdc.append(yqc__bzzzr)
    node.out_vars = eyfv__ihzdc
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for ambg__njky in node.filters:
            for cdaw__tps in range(len(ambg__njky)):
                val = ambg__njky[cdaw__tps]
                ambg__njky[cdaw__tps] = val[0], val[1], replace_vars_inner(val
                    [2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for ztq__acgau in node.out_vars:
        vmajz__lot = definitions[ztq__acgau.name]
        if node not in vmajz__lot:
            vmajz__lot.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        ivhg__nbd = [uly__eccsx[2] for set__ddsac in filters for uly__eccsx in
            set__ddsac]
        hljdn__ais = set()
        for gtkha__vudz in ivhg__nbd:
            if isinstance(gtkha__vudz, ir.Var):
                if gtkha__vudz.name not in hljdn__ais:
                    filter_vars.append(gtkha__vudz)
                hljdn__ais.add(gtkha__vudz.name)
        return {uly__eccsx.name: f'f{cdaw__tps}' for cdaw__tps, uly__eccsx in
            enumerate(filter_vars)}, filter_vars
    else:
        return {}, []


class StreamReaderType(types.Opaque):

    def __init__(self):
        super(StreamReaderType, self).__init__(name='StreamReaderType')


stream_reader_type = StreamReaderType()
register_model(StreamReaderType)(models.OpaqueModel)


@box(StreamReaderType)
def box_stream_reader(typ, val, c):
    c.pyapi.incref(val)
    return val


def trim_extra_used_columns(used_columns: Set, num_columns: int):
    return {cdaw__tps for cdaw__tps in used_columns if cdaw__tps < num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    iowql__jzj = {}
    for cdaw__tps, mba__puss in enumerate(df_type.data):
        if isinstance(mba__puss, bodo.IntegerArrayType):
            bcvl__srb = mba__puss.get_pandas_scalar_type_instance
            if bcvl__srb not in iowql__jzj:
                iowql__jzj[bcvl__srb] = []
            iowql__jzj[bcvl__srb].append(df.columns[cdaw__tps])
    for typ, bmjc__xoriz in iowql__jzj.items():
        df[bmjc__xoriz] = df[bmjc__xoriz].astype(typ)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    jbv__jdw = node.out_vars[0].name
    assert isinstance(typemap[jbv__jdw], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, rycg__awvb, ldqvf__phko = get_live_column_nums_block(
            column_live_map, equiv_vars, jbv__jdw)
        if not (rycg__awvb or ldqvf__phko):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    qjwv__yuq = False
    if array_dists is not None:
        fop__ieesr = node.out_vars[0].name
        qjwv__yuq = array_dists[fop__ieesr] in (Distribution.OneD,
            Distribution.OneD_Var)
        ykr__kyqvd = node.out_vars[1].name
        assert typemap[ykr__kyqvd
            ] == types.none or not qjwv__yuq or array_dists[ykr__kyqvd] in (
            Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return qjwv__yuq


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg'], output_dnf=True) ->Tuple[str, str]:
    ssr__psqeb = 'None'
    ean__ivtsp = 'None'
    if filters:
        hck__hjg = []
        skgb__kdfak = []
        mqy__gtgla = False
        orig_colname_map = {c: cdaw__tps for cdaw__tps, c in enumerate(
            col_names)}
        for ambg__njky in filters:
            jypqv__evutm = []
            ukpb__kztn = []
            for uly__eccsx in ambg__njky:
                if isinstance(uly__eccsx[2], ir.Var):
                    hmym__aahk, esw__luyh = determine_filter_cast(
                        original_out_types, typemap, uly__eccsx,
                        orig_colname_map, partition_names, source)
                    if uly__eccsx[1] == 'in':
                        oiark__gpy = (
                            f"(ds.field('{uly__eccsx[0]}').isin({filter_map[uly__eccsx[2].name]}))"
                            )
                    else:
                        oiark__gpy = (
                            f"(ds.field('{uly__eccsx[0]}'){hmym__aahk} {uly__eccsx[1]} ds.scalar({filter_map[uly__eccsx[2].name]}){esw__luyh})"
                            )
                else:
                    assert uly__eccsx[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if uly__eccsx[1] == 'is not':
                        xpiz__ibodp = '~'
                    else:
                        xpiz__ibodp = ''
                    oiark__gpy = (
                        f"({xpiz__ibodp}ds.field('{uly__eccsx[0]}').is_null())"
                        )
                ukpb__kztn.append(oiark__gpy)
                if not mqy__gtgla:
                    if uly__eccsx[0] in partition_names and isinstance(
                        uly__eccsx[2], ir.Var):
                        if output_dnf:
                            wnub__yrd = (
                                f"('{uly__eccsx[0]}', '{uly__eccsx[1]}', {filter_map[uly__eccsx[2].name]})"
                                )
                        else:
                            wnub__yrd = oiark__gpy
                        jypqv__evutm.append(wnub__yrd)
                    elif uly__eccsx[0] in partition_names and not isinstance(
                        uly__eccsx[2], ir.Var) and source == 'iceberg':
                        if output_dnf:
                            wnub__yrd = (
                                f"('{uly__eccsx[0]}', '{uly__eccsx[1]}', '{uly__eccsx[2]}')"
                                )
                        else:
                            wnub__yrd = oiark__gpy
                        jypqv__evutm.append(wnub__yrd)
            jpsgh__mttm = ''
            if jypqv__evutm:
                if output_dnf:
                    jpsgh__mttm = ', '.join(jypqv__evutm)
                else:
                    jpsgh__mttm = ' & '.join(jypqv__evutm)
            else:
                mqy__gtgla = True
            jeb__ilvll = ' & '.join(ukpb__kztn)
            if jpsgh__mttm:
                if output_dnf:
                    hck__hjg.append(f'[{jpsgh__mttm}]')
                else:
                    hck__hjg.append(f'({jpsgh__mttm})')
            skgb__kdfak.append(f'({jeb__ilvll})')
        if output_dnf:
            trske__fmf = ', '.join(hck__hjg)
        else:
            trske__fmf = ' | '.join(hck__hjg)
        uxgx__uozaz = ' | '.join(skgb__kdfak)
        if trske__fmf and not mqy__gtgla:
            if output_dnf:
                ssr__psqeb = f'[{trske__fmf}]'
            else:
                ssr__psqeb = f'({trske__fmf})'
        ean__ivtsp = f'({uxgx__uozaz})'
    return ssr__psqeb, ean__ivtsp


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    nmxe__pzxf = filter_val[0]
    awz__yhvkb = col_types[orig_colname_map[nmxe__pzxf]]
    rzs__jrpr = bodo.utils.typing.element_type(awz__yhvkb)
    if source == 'parquet' and nmxe__pzxf in partition_names:
        if rzs__jrpr == types.unicode_type:
            sxdro__xvlf = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(rzs__jrpr, types.Integer):
            sxdro__xvlf = f'.cast(pyarrow.{rzs__jrpr.name}(), safe=False)'
        else:
            sxdro__xvlf = ''
    else:
        sxdro__xvlf = ''
    twu__tmqdv = typemap[filter_val[2].name]
    if isinstance(twu__tmqdv, (types.List, types.Set)):
        dpgn__mzxt = twu__tmqdv.dtype
    else:
        dpgn__mzxt = twu__tmqdv
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rzs__jrpr,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dpgn__mzxt,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([rzs__jrpr, dpgn__mzxt]):
        if not bodo.utils.typing.is_safe_arrow_cast(rzs__jrpr, dpgn__mzxt):
            raise BodoError(
                f'Unsupported Arrow cast from {rzs__jrpr} to {dpgn__mzxt} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if rzs__jrpr == types.unicode_type:
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif rzs__jrpr in (bodo.datetime64ns, bodo.pd_timestamp_type):
            if isinstance(twu__tmqdv, (types.List, types.Set)):
                aafc__zrr = 'list' if isinstance(twu__tmqdv, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {aafc__zrr} values with isin filter pushdown.'
                    )
            return sxdro__xvlf, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return sxdro__xvlf, ''
