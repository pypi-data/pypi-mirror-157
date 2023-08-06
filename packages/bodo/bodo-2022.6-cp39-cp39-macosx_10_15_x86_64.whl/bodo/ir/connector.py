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
    jmln__zqmex = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    kqnj__wvg = []
    for itkwy__yio in node.out_vars:
        typ = typemap[itkwy__yio.name]
        if typ == types.none:
            continue
        sqde__joqg = array_analysis._gen_shape_call(equiv_set, itkwy__yio,
            typ.ndim, None, jmln__zqmex)
        equiv_set.insert_equiv(itkwy__yio, sqde__joqg)
        kqnj__wvg.append(sqde__joqg[0])
        equiv_set.define(itkwy__yio, set())
    if len(kqnj__wvg) > 1:
        equiv_set.insert_equiv(*kqnj__wvg)
    return [], jmln__zqmex


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        iub__rht = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        iub__rht = Distribution.OneD_Var
    else:
        iub__rht = Distribution.OneD
    for tbzql__nbsk in node.out_vars:
        if tbzql__nbsk.name in array_dists:
            iub__rht = Distribution(min(iub__rht.value, array_dists[
                tbzql__nbsk.name].value))
    for tbzql__nbsk in node.out_vars:
        array_dists[tbzql__nbsk.name] = iub__rht


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
    for itkwy__yio, typ in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(itkwy__yio.name, typ, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    aenhb__xrhl = []
    for itkwy__yio in node.out_vars:
        apye__jqvfy = visit_vars_inner(itkwy__yio, callback, cbdata)
        aenhb__xrhl.append(apye__jqvfy)
    node.out_vars = aenhb__xrhl
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for ffspu__gvtrd in node.filters:
            for wzn__fmgh in range(len(ffspu__gvtrd)):
                val = ffspu__gvtrd[wzn__fmgh]
                ffspu__gvtrd[wzn__fmgh] = val[0], val[1], visit_vars_inner(val
                    [2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({tbzql__nbsk.name for tbzql__nbsk in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for dwynu__pnyao in node.filters:
            for tbzql__nbsk in dwynu__pnyao:
                if isinstance(tbzql__nbsk[2], ir.Var):
                    use_set.add(tbzql__nbsk[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    yrya__dfxid = set(tbzql__nbsk.name for tbzql__nbsk in node.out_vars)
    return set(), yrya__dfxid


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    aenhb__xrhl = []
    for itkwy__yio in node.out_vars:
        apye__jqvfy = replace_vars_inner(itkwy__yio, var_dict)
        aenhb__xrhl.append(apye__jqvfy)
    node.out_vars = aenhb__xrhl
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for ffspu__gvtrd in node.filters:
            for wzn__fmgh in range(len(ffspu__gvtrd)):
                val = ffspu__gvtrd[wzn__fmgh]
                ffspu__gvtrd[wzn__fmgh] = val[0], val[1], replace_vars_inner(
                    val[2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for itkwy__yio in node.out_vars:
        yuc__vdwjp = definitions[itkwy__yio.name]
        if node not in yuc__vdwjp:
            yuc__vdwjp.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        gxn__gouip = [tbzql__nbsk[2] for dwynu__pnyao in filters for
            tbzql__nbsk in dwynu__pnyao]
        yum__llxg = set()
        for swpgz__jxh in gxn__gouip:
            if isinstance(swpgz__jxh, ir.Var):
                if swpgz__jxh.name not in yum__llxg:
                    filter_vars.append(swpgz__jxh)
                yum__llxg.add(swpgz__jxh.name)
        return {tbzql__nbsk.name: f'f{wzn__fmgh}' for wzn__fmgh,
            tbzql__nbsk in enumerate(filter_vars)}, filter_vars
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
    return {wzn__fmgh for wzn__fmgh in used_columns if wzn__fmgh < num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    rsxhp__hvx = {}
    for wzn__fmgh, tyixk__groza in enumerate(df_type.data):
        if isinstance(tyixk__groza, bodo.IntegerArrayType):
            jteg__hhv = tyixk__groza.get_pandas_scalar_type_instance
            if jteg__hhv not in rsxhp__hvx:
                rsxhp__hvx[jteg__hhv] = []
            rsxhp__hvx[jteg__hhv].append(df.columns[wzn__fmgh])
    for typ, sze__fqlt in rsxhp__hvx.items():
        df[sze__fqlt] = df[sze__fqlt].astype(typ)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    btn__zyrti = node.out_vars[0].name
    assert isinstance(typemap[btn__zyrti], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, ougf__jyb, zhjg__vao = get_live_column_nums_block(
            column_live_map, equiv_vars, btn__zyrti)
        if not (ougf__jyb or zhjg__vao):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    kjre__fiitu = False
    if array_dists is not None:
        kyf__mwec = node.out_vars[0].name
        kjre__fiitu = array_dists[kyf__mwec] in (Distribution.OneD,
            Distribution.OneD_Var)
        nmwmq__tlp = node.out_vars[1].name
        assert typemap[nmwmq__tlp
            ] == types.none or not kjre__fiitu or array_dists[nmwmq__tlp] in (
            Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return kjre__fiitu


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg'], output_dnf=True) ->Tuple[str, str]:
    vdaos__pkzha = 'None'
    iyqo__bqxi = 'None'
    if filters:
        arxit__ngzoq = []
        aachs__nydn = []
        szkj__rgo = False
        orig_colname_map = {c: wzn__fmgh for wzn__fmgh, c in enumerate(
            col_names)}
        for ffspu__gvtrd in filters:
            djy__owg = []
            onpwd__lpf = []
            for tbzql__nbsk in ffspu__gvtrd:
                if isinstance(tbzql__nbsk[2], ir.Var):
                    ocxu__srrcw, zrzjb__ols = determine_filter_cast(
                        original_out_types, typemap, tbzql__nbsk,
                        orig_colname_map, partition_names, source)
                    if tbzql__nbsk[1] == 'in':
                        pkqzr__wer = (
                            f"(ds.field('{tbzql__nbsk[0]}').isin({filter_map[tbzql__nbsk[2].name]}))"
                            )
                    else:
                        pkqzr__wer = (
                            f"(ds.field('{tbzql__nbsk[0]}'){ocxu__srrcw} {tbzql__nbsk[1]} ds.scalar({filter_map[tbzql__nbsk[2].name]}){zrzjb__ols})"
                            )
                else:
                    assert tbzql__nbsk[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if tbzql__nbsk[1] == 'is not':
                        todkj__kfsc = '~'
                    else:
                        todkj__kfsc = ''
                    pkqzr__wer = (
                        f"({todkj__kfsc}ds.field('{tbzql__nbsk[0]}').is_null())"
                        )
                onpwd__lpf.append(pkqzr__wer)
                if not szkj__rgo:
                    if tbzql__nbsk[0] in partition_names and isinstance(
                        tbzql__nbsk[2], ir.Var):
                        if output_dnf:
                            kcbjz__wdejo = (
                                f"('{tbzql__nbsk[0]}', '{tbzql__nbsk[1]}', {filter_map[tbzql__nbsk[2].name]})"
                                )
                        else:
                            kcbjz__wdejo = pkqzr__wer
                        djy__owg.append(kcbjz__wdejo)
                    elif tbzql__nbsk[0] in partition_names and not isinstance(
                        tbzql__nbsk[2], ir.Var) and source == 'iceberg':
                        if output_dnf:
                            kcbjz__wdejo = (
                                f"('{tbzql__nbsk[0]}', '{tbzql__nbsk[1]}', '{tbzql__nbsk[2]}')"
                                )
                        else:
                            kcbjz__wdejo = pkqzr__wer
                        djy__owg.append(kcbjz__wdejo)
            wnb__cfmt = ''
            if djy__owg:
                if output_dnf:
                    wnb__cfmt = ', '.join(djy__owg)
                else:
                    wnb__cfmt = ' & '.join(djy__owg)
            else:
                szkj__rgo = True
            kxfa__vnqi = ' & '.join(onpwd__lpf)
            if wnb__cfmt:
                if output_dnf:
                    arxit__ngzoq.append(f'[{wnb__cfmt}]')
                else:
                    arxit__ngzoq.append(f'({wnb__cfmt})')
            aachs__nydn.append(f'({kxfa__vnqi})')
        if output_dnf:
            gyv__ahqyc = ', '.join(arxit__ngzoq)
        else:
            gyv__ahqyc = ' | '.join(arxit__ngzoq)
        rbun__wbdg = ' | '.join(aachs__nydn)
        if gyv__ahqyc and not szkj__rgo:
            if output_dnf:
                vdaos__pkzha = f'[{gyv__ahqyc}]'
            else:
                vdaos__pkzha = f'({gyv__ahqyc})'
        iyqo__bqxi = f'({rbun__wbdg})'
    return vdaos__pkzha, iyqo__bqxi


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    lck__zun = filter_val[0]
    jidl__ntj = col_types[orig_colname_map[lck__zun]]
    wnew__hsxnh = bodo.utils.typing.element_type(jidl__ntj)
    if source == 'parquet' and lck__zun in partition_names:
        if wnew__hsxnh == types.unicode_type:
            tuqv__wjqeg = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(wnew__hsxnh, types.Integer):
            tuqv__wjqeg = f'.cast(pyarrow.{wnew__hsxnh.name}(), safe=False)'
        else:
            tuqv__wjqeg = ''
    else:
        tuqv__wjqeg = ''
    hcm__ypu = typemap[filter_val[2].name]
    if isinstance(hcm__ypu, (types.List, types.Set)):
        iqki__jqb = hcm__ypu.dtype
    else:
        iqki__jqb = hcm__ypu
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(wnew__hsxnh,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(iqki__jqb,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([wnew__hsxnh, iqki__jqb]):
        if not bodo.utils.typing.is_safe_arrow_cast(wnew__hsxnh, iqki__jqb):
            raise BodoError(
                f'Unsupported Arrow cast from {wnew__hsxnh} to {iqki__jqb} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if wnew__hsxnh == types.unicode_type:
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif wnew__hsxnh in (bodo.datetime64ns, bodo.pd_timestamp_type):
            if isinstance(hcm__ypu, (types.List, types.Set)):
                mftw__ckpqj = 'list' if isinstance(hcm__ypu, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {mftw__ckpqj} values with isin filter pushdown.'
                    )
            return tuqv__wjqeg, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return tuqv__wjqeg, ''
