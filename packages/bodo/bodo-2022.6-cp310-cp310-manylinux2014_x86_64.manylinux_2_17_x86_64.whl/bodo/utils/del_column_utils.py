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
        spv__enx = typemap[call_expr.args[1].name].literal_value
        return {spv__enx}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        ajgar__sycrr = dict(call_expr.kws)
        if 'used_cols' in ajgar__sycrr:
            jpw__wuld = ajgar__sycrr['used_cols']
            que__odg = typemap[jpw__wuld.name]
            que__odg = que__odg.instance_type
            return set(que__odg.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        jpw__wuld = call_expr.args[1]
        que__odg = typemap[jpw__wuld.name]
        que__odg = que__odg.instance_type
        return set(que__odg.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        okufg__qmvl = call_expr.args[1]
        cdjt__pnt = typemap[okufg__qmvl.name]
        cdjt__pnt = cdjt__pnt.instance_type
        nqq__cqsrm = cdjt__pnt.meta
        ajgar__sycrr = dict(call_expr.kws)
        if 'used_cols' in ajgar__sycrr:
            jpw__wuld = ajgar__sycrr['used_cols']
            que__odg = typemap[jpw__wuld.name]
            que__odg = que__odg.instance_type
            hzuo__fnym = set(que__odg.meta)
            fpq__yhyyf = set()
            for funq__ipuif, wlp__zzvs in enumerate(nqq__cqsrm):
                if funq__ipuif in hzuo__fnym:
                    fpq__yhyyf.add(wlp__zzvs)
            return fpq__yhyyf
        else:
            return set(nqq__cqsrm)
    elif fdef == ('py_data_to_cpp_table', 'bodo.libs.array'):
        zcgkg__yrm = typemap[call_expr.args[2].name].instance_type.meta
        bfumf__lyn = len(typemap[call_expr.args[0].name].arr_types)
        return set(funq__ipuif for funq__ipuif in zcgkg__yrm if funq__ipuif <
            bfumf__lyn)
    return None
