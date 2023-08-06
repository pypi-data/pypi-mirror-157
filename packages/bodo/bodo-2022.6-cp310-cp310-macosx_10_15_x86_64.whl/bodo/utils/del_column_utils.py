"""Helper information to keep table column deletion
pass organized. This contains information about all
table operations for optimizations.
"""
from typing import Dict, Tuple
from numba.core import ir, types
from bodo.hiframes.table import TableType
table_usecol_funcs = {('get_table_data', 'bodo.hiframes.table'), (
    'table_filter', 'bodo.hiframes.table'), ('table_subset',
    'bodo.hiframes.table'), ('set_table_data', 'bodo.hiframes.table'), (
    'set_table_data_null', 'bodo.hiframes.table'), (
    'generate_mappable_table_func', 'bodo.utils.table_utils'), (
    'table_astype', 'bodo.utils.table_utils'), ('generate_table_nbytes',
    'bodo.utils.table_utils'), ('table_concat', 'bodo.utils.table_utils'),
    ('py_data_to_cpp_table', 'bodo.libs.array')}


def is_table_use_column_ops(fdef: Tuple[str, str], args, typemap):
    return fdef in table_usecol_funcs and len(args) > 0 and isinstance(typemap
        [args[0].name], TableType)


def get_table_used_columns(fdef: Tuple[str, str], call_expr: ir.Expr,
    typemap: Dict[str, types.Type]):
    if fdef == ('get_table_data', 'bodo.hiframes.table'):
        gmdm__yntyd = typemap[call_expr.args[1].name].literal_value
        return {gmdm__yntyd}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        uxkp__wgye = dict(call_expr.kws)
        if 'used_cols' in uxkp__wgye:
            afxln__rhn = uxkp__wgye['used_cols']
            gresu__veeiu = typemap[afxln__rhn.name]
            gresu__veeiu = gresu__veeiu.instance_type
            return set(gresu__veeiu.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        afxln__rhn = call_expr.args[1]
        gresu__veeiu = typemap[afxln__rhn.name]
        gresu__veeiu = gresu__veeiu.instance_type
        return set(gresu__veeiu.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        vlys__ujaq = call_expr.args[1]
        onavm__kafyt = typemap[vlys__ujaq.name]
        onavm__kafyt = onavm__kafyt.instance_type
        los__zlv = onavm__kafyt.meta
        uxkp__wgye = dict(call_expr.kws)
        if 'used_cols' in uxkp__wgye:
            afxln__rhn = uxkp__wgye['used_cols']
            gresu__veeiu = typemap[afxln__rhn.name]
            gresu__veeiu = gresu__veeiu.instance_type
            iox__hgw = set(gresu__veeiu.meta)
            sykan__yxk = set()
            for nwp__lcm, bzns__dimsh in enumerate(los__zlv):
                if nwp__lcm in iox__hgw:
                    sykan__yxk.add(bzns__dimsh)
            return sykan__yxk
        else:
            return set(los__zlv)
    elif fdef == ('py_data_to_cpp_table', 'bodo.libs.array'):
        oih__rfxh = typemap[call_expr.args[2].name].instance_type.meta
        zdzum__lcc = len(typemap[call_expr.args[0].name].arr_types)
        return set(nwp__lcm for nwp__lcm in oih__rfxh if nwp__lcm < zdzum__lcc)
    return None
