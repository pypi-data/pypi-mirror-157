"""IR node for the data sorting"""
from collections import defaultdict
from typing import List, Set, Tuple, Union
import numba
import numpy as np
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes, replace_vars_inner, visit_vars_inner
import bodo
from bodo.libs.array import arr_info_list_to_table, array_to_info, cpp_table_to_py_data, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, py_data_to_cpp_table, sort_values_table
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import _compute_table_column_uses, _find_used_columns, ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import MetaType, type_has_unknown_cats
from bodo.utils.utils import gen_getitem


class Sort(ir.Stmt):

    def __init__(self, df_in: str, df_out: str, in_vars: List[ir.Var],
        out_vars: List[ir.Var], key_inds: Tuple[int], inplace: bool, loc:
        ir.Loc, ascending_list: Union[List[bool], bool]=True, na_position:
        Union[List[str], str]='last', is_table_format: bool=False,
        num_table_arrays: int=0):
        self.df_in = df_in
        self.df_out = df_out
        self.in_vars = in_vars
        self.out_vars = out_vars
        self.key_inds = key_inds
        self.inplace = inplace
        self.is_table_format = is_table_format
        self.num_table_arrays = num_table_arrays
        self.dead_var_inds: Set[int] = set()
        self.dead_key_var_inds: Set[int] = set()
        if isinstance(na_position, str):
            if na_position == 'last':
                self.na_position_b = (True,) * len(key_inds)
            else:
                self.na_position_b = (False,) * len(key_inds)
        else:
            self.na_position_b = tuple([(True if ilasc__awks == 'last' else
                False) for ilasc__awks in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def get_live_in_vars(self):
        return [oelvx__kzjd for oelvx__kzjd in self.in_vars if oelvx__kzjd
             is not None]

    def get_live_out_vars(self):
        return [oelvx__kzjd for oelvx__kzjd in self.out_vars if oelvx__kzjd
             is not None]

    def __repr__(self):
        dqzz__spono = ', '.join(oelvx__kzjd.name for oelvx__kzjd in self.
            get_live_in_vars())
        zjd__stxx = f'{self.df_in}{{{dqzz__spono}}}'
        coiw__abfyv = ', '.join(oelvx__kzjd.name for oelvx__kzjd in self.
            get_live_out_vars())
        hwhuf__anlny = f'{self.df_out}{{{coiw__abfyv}}}'
        return f'Sort (keys: {self.key_inds}): {zjd__stxx} {hwhuf__anlny}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    kry__eoypi = []
    for ijku__axllr in sort_node.get_live_in_vars():
        bkqn__brmjs = equiv_set.get_shape(ijku__axllr)
        if bkqn__brmjs is not None:
            kry__eoypi.append(bkqn__brmjs[0])
    if len(kry__eoypi) > 1:
        equiv_set.insert_equiv(*kry__eoypi)
    whv__gkpx = []
    kry__eoypi = []
    for ijku__axllr in sort_node.get_live_out_vars():
        sxc__inz = typemap[ijku__axllr.name]
        wok__pxm = array_analysis._gen_shape_call(equiv_set, ijku__axllr,
            sxc__inz.ndim, None, whv__gkpx)
        equiv_set.insert_equiv(ijku__axllr, wok__pxm)
        kry__eoypi.append(wok__pxm[0])
        equiv_set.define(ijku__axllr, set())
    if len(kry__eoypi) > 1:
        equiv_set.insert_equiv(*kry__eoypi)
    return [], whv__gkpx


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    lgx__fgvqm = sort_node.get_live_in_vars()
    pqa__cfw = sort_node.get_live_out_vars()
    xzxd__erp = Distribution.OneD
    for ijku__axllr in lgx__fgvqm:
        xzxd__erp = Distribution(min(xzxd__erp.value, array_dists[
            ijku__axllr.name].value))
    eqaxe__gxc = Distribution(min(xzxd__erp.value, Distribution.OneD_Var.value)
        )
    for ijku__axllr in pqa__cfw:
        if ijku__axllr.name in array_dists:
            eqaxe__gxc = Distribution(min(eqaxe__gxc.value, array_dists[
                ijku__axllr.name].value))
    if eqaxe__gxc != Distribution.OneD_Var:
        xzxd__erp = eqaxe__gxc
    for ijku__axllr in lgx__fgvqm:
        array_dists[ijku__axllr.name] = xzxd__erp
    for ijku__axllr in pqa__cfw:
        array_dists[ijku__axllr.name] = eqaxe__gxc


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for vnc__xaibj, hdxpk__yywni in enumerate(sort_node.out_vars):
        crtb__deo = sort_node.in_vars[vnc__xaibj]
        if crtb__deo is not None and hdxpk__yywni is not None:
            typeinferer.constraints.append(typeinfer.Propagate(dst=
                hdxpk__yywni.name, src=crtb__deo.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for ijku__axllr in sort_node.get_live_out_vars():
            definitions[ijku__axllr.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for vnc__xaibj in range(len(sort_node.in_vars)):
        if sort_node.in_vars[vnc__xaibj] is not None:
            sort_node.in_vars[vnc__xaibj] = visit_vars_inner(sort_node.
                in_vars[vnc__xaibj], callback, cbdata)
        if sort_node.out_vars[vnc__xaibj] is not None:
            sort_node.out_vars[vnc__xaibj] = visit_vars_inner(sort_node.
                out_vars[vnc__xaibj], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if sort_node.is_table_format:
        izvfk__xxev = sort_node.out_vars[0]
        if izvfk__xxev is not None and izvfk__xxev.name not in lives:
            sort_node.out_vars[0] = None
            dead_cols = set(range(sort_node.num_table_arrays))
            pto__pjoho = set(sort_node.key_inds)
            sort_node.dead_key_var_inds.update(dead_cols & pto__pjoho)
            sort_node.dead_var_inds.update(dead_cols - pto__pjoho)
            if len(pto__pjoho & dead_cols) == 0:
                sort_node.in_vars[0] = None
        for vnc__xaibj in range(1, len(sort_node.out_vars)):
            oelvx__kzjd = sort_node.out_vars[vnc__xaibj]
            if oelvx__kzjd is not None and oelvx__kzjd.name not in lives:
                sort_node.out_vars[vnc__xaibj] = None
                ffv__dnmaz = sort_node.num_table_arrays + vnc__xaibj - 1
                if ffv__dnmaz in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(ffv__dnmaz)
                else:
                    sort_node.dead_var_inds.add(ffv__dnmaz)
                    sort_node.in_vars[vnc__xaibj] = None
    else:
        for vnc__xaibj in range(len(sort_node.out_vars)):
            oelvx__kzjd = sort_node.out_vars[vnc__xaibj]
            if oelvx__kzjd is not None and oelvx__kzjd.name not in lives:
                sort_node.out_vars[vnc__xaibj] = None
                if vnc__xaibj in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(vnc__xaibj)
                else:
                    sort_node.dead_var_inds.add(vnc__xaibj)
                    sort_node.in_vars[vnc__xaibj] = None
    if all(oelvx__kzjd is None for oelvx__kzjd in sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({oelvx__kzjd.name for oelvx__kzjd in sort_node.
        get_live_in_vars()})
    if not sort_node.inplace:
        def_set.update({oelvx__kzjd.name for oelvx__kzjd in sort_node.
            get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    ngpex__pgawz = set()
    if not sort_node.inplace:
        ngpex__pgawz.update({oelvx__kzjd.name for oelvx__kzjd in sort_node.
            get_live_out_vars()})
    return set(), ngpex__pgawz


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for vnc__xaibj in range(len(sort_node.in_vars)):
        if sort_node.in_vars[vnc__xaibj] is not None:
            sort_node.in_vars[vnc__xaibj] = replace_vars_inner(sort_node.
                in_vars[vnc__xaibj], var_dict)
        if sort_node.out_vars[vnc__xaibj] is not None:
            sort_node.out_vars[vnc__xaibj] = replace_vars_inner(sort_node.
                out_vars[vnc__xaibj], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = sort_node.get_live_in_vars()
    out_vars = sort_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for oelvx__kzjd in (in_vars + out_vars):
            if array_dists[oelvx__kzjd.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                oelvx__kzjd.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nodes = []
    if not sort_node.inplace:
        yot__skt = []
        for oelvx__kzjd in in_vars:
            fizg__bdyc = _copy_array_nodes(oelvx__kzjd, nodes, typingctx,
                targetctx, typemap, calltypes, sort_node.dead_var_inds)
            yot__skt.append(fizg__bdyc)
        in_vars = yot__skt
    out_types = [(typemap[oelvx__kzjd.name] if oelvx__kzjd is not None else
        types.none) for oelvx__kzjd in sort_node.out_vars]
    uvbb__fhbg, hrxt__yaxp = get_sort_cpp_section(sort_node, out_types,
        parallel)
    jlfnd__eicdv = {}
    exec(uvbb__fhbg, {}, jlfnd__eicdv)
    sjpi__emd = jlfnd__eicdv['f']
    hrxt__yaxp.update({'bodo': bodo, 'np': np, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'sort_values_table': sort_values_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'array_to_info': array_to_info,
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    hrxt__yaxp.update({f'out_type{vnc__xaibj}': out_types[vnc__xaibj] for
        vnc__xaibj in range(len(out_types))})
    wtmz__bqit = compile_to_numba_ir(sjpi__emd, hrxt__yaxp, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[oelvx__kzjd.
        name] for oelvx__kzjd in in_vars), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(wtmz__bqit, in_vars)
    pys__mlxj = wtmz__bqit.body[-2].value.value
    nodes += wtmz__bqit.body[:-2]
    for vnc__xaibj, oelvx__kzjd in enumerate(out_vars):
        gen_getitem(oelvx__kzjd, pys__mlxj, vnc__xaibj, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes,
    dead_cols):
    from bodo.hiframes.table import TableType
    whneq__lqyq = lambda arr: arr.copy()
    pfgz__erjq = None
    if isinstance(typemap[var.name], TableType):
        vkd__xgz = len(typemap[var.name].arr_types)
        pfgz__erjq = set(range(vkd__xgz)) - dead_cols
        pfgz__erjq = MetaType(tuple(sorted(pfgz__erjq)))
        whneq__lqyq = (lambda T: bodo.utils.table_utils.
            generate_mappable_table_func(T, 'copy', types.none, True,
            used_cols=_used_columns))
    wtmz__bqit = compile_to_numba_ir(whneq__lqyq, {'bodo': bodo, 'types':
        types, '_used_columns': pfgz__erjq}, typingctx=typingctx, targetctx
        =targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(wtmz__bqit, [var])
    nodes += wtmz__bqit.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(sort_node, out_types, parallel):
    rajbc__awl = len(sort_node.key_inds)
    adqdi__nlyx = len(sort_node.in_vars)
    kxi__oawo = len(sort_node.out_vars)
    n_cols = (sort_node.num_table_arrays + adqdi__nlyx - 1 if sort_node.
        is_table_format else adqdi__nlyx)
    phts__iges, weeg__axqyz, caz__iyk = _get_cpp_col_ind_mappings(sort_node
        .key_inds, sort_node.dead_var_inds, sort_node.dead_key_var_inds, n_cols
        )
    roe__qcuvr = []
    if sort_node.is_table_format:
        roe__qcuvr.append('arg0')
        for vnc__xaibj in range(1, adqdi__nlyx):
            ffv__dnmaz = sort_node.num_table_arrays + vnc__xaibj - 1
            if ffv__dnmaz not in sort_node.dead_var_inds:
                roe__qcuvr.append(f'arg{ffv__dnmaz}')
    else:
        for vnc__xaibj in range(n_cols):
            if vnc__xaibj not in sort_node.dead_var_inds:
                roe__qcuvr.append(f'arg{vnc__xaibj}')
    uvbb__fhbg = f"def f({', '.join(roe__qcuvr)}):\n"
    if sort_node.is_table_format:
        yubm__vgdrv = ',' if adqdi__nlyx - 1 == 1 else ''
        qkj__pyck = []
        for vnc__xaibj in range(sort_node.num_table_arrays, n_cols):
            if vnc__xaibj in sort_node.dead_var_inds:
                qkj__pyck.append('None')
            else:
                qkj__pyck.append(f'arg{vnc__xaibj}')
        uvbb__fhbg += f"""  in_cpp_table = py_data_to_cpp_table(arg0, ({', '.join(qkj__pyck)}{yubm__vgdrv}), in_col_inds, {sort_node.num_table_arrays})
"""
    else:
        hmxpp__recm = {vqdik__giowb: vnc__xaibj for vnc__xaibj,
            vqdik__giowb in enumerate(phts__iges)}
        mav__uumgp = [None] * len(phts__iges)
        for vnc__xaibj in range(n_cols):
            pfn__dlj = hmxpp__recm.get(vnc__xaibj, -1)
            if pfn__dlj != -1:
                mav__uumgp[pfn__dlj] = f'array_to_info(arg{vnc__xaibj})'
        uvbb__fhbg += '  info_list_total = [{}]\n'.format(','.join(mav__uumgp))
        uvbb__fhbg += (
            '  in_cpp_table = arr_info_list_to_table(info_list_total)\n')
    uvbb__fhbg += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if hktc__mbj else '0' for hktc__mbj in sort_node.
        ascending_list))
    uvbb__fhbg += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if hktc__mbj else '0' for hktc__mbj in sort_node.
        na_position_b))
    uvbb__fhbg += '  dead_keys = np.array([{}], np.int64)\n'.format(','.
        join('1' if vnc__xaibj in caz__iyk else '0' for vnc__xaibj in range
        (rajbc__awl)))
    uvbb__fhbg += f'  total_rows_np = np.array([0], dtype=np.int64)\n'
    uvbb__fhbg += f"""  out_cpp_table = sort_values_table(in_cpp_table, {rajbc__awl}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, total_rows_np.ctypes, {parallel})
"""
    if sort_node.is_table_format:
        yubm__vgdrv = ',' if kxi__oawo == 1 else ''
        out_types = (
            f"({', '.join(f'out_type{vnc__xaibj}' if not type_has_unknown_cats(out_types[vnc__xaibj]) else f'arg{vnc__xaibj}' for vnc__xaibj in range(kxi__oawo))}{yubm__vgdrv})"
            )
        uvbb__fhbg += f"""  out_data = cpp_table_to_py_data(out_cpp_table, out_col_inds, {out_types}, total_rows_np[0], {sort_node.num_table_arrays})
"""
    else:
        hmxpp__recm = {vqdik__giowb: vnc__xaibj for vnc__xaibj,
            vqdik__giowb in enumerate(weeg__axqyz)}
        mav__uumgp = []
        for vnc__xaibj in range(n_cols):
            pfn__dlj = hmxpp__recm.get(vnc__xaibj, -1)
            if pfn__dlj != -1:
                vycii__lkyua = (f'out_type{vnc__xaibj}' if not
                    type_has_unknown_cats(out_types[vnc__xaibj]) else
                    f'arg{vnc__xaibj}')
                uvbb__fhbg += f"""  out{vnc__xaibj} = info_to_array(info_from_table(out_cpp_table, {pfn__dlj}), {vycii__lkyua})
"""
                mav__uumgp.append(f'out{vnc__xaibj}')
        yubm__vgdrv = ',' if len(mav__uumgp) == 1 else ''
        lfw__imwb = f"({', '.join(mav__uumgp)}{yubm__vgdrv})"
        uvbb__fhbg += f'  out_data = {lfw__imwb}\n'
    uvbb__fhbg += '  delete_table(out_cpp_table)\n'
    uvbb__fhbg += '  delete_table(in_cpp_table)\n'
    uvbb__fhbg += f'  return out_data\n'
    return uvbb__fhbg, {'in_col_inds': MetaType(tuple(phts__iges)),
        'out_col_inds': MetaType(tuple(weeg__axqyz))}


def _get_cpp_col_ind_mappings(key_inds, dead_var_inds, dead_key_var_inds,
    n_cols):
    phts__iges = []
    weeg__axqyz = []
    caz__iyk = []
    for vqdik__giowb, vnc__xaibj in enumerate(key_inds):
        phts__iges.append(vnc__xaibj)
        if vnc__xaibj in dead_key_var_inds:
            caz__iyk.append(vqdik__giowb)
        else:
            weeg__axqyz.append(vnc__xaibj)
    for vnc__xaibj in range(n_cols):
        if vnc__xaibj in dead_var_inds or vnc__xaibj in key_inds:
            continue
        phts__iges.append(vnc__xaibj)
        weeg__axqyz.append(vnc__xaibj)
    return phts__iges, weeg__axqyz, caz__iyk


def sort_table_column_use(sort_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not sort_node.is_table_format or sort_node.in_vars[0
        ] is None or sort_node.out_vars[0] is None:
        return
    qoik__oioqa = sort_node.in_vars[0].name
    cggn__ctw = sort_node.out_vars[0].name
    rdq__fvu, uqqr__otaai, hvdm__ubc = block_use_map[qoik__oioqa]
    if uqqr__otaai or hvdm__ubc:
        return
    ilajc__qrtrb, tju__nkn, zooe__cmrk = _compute_table_column_uses(cggn__ctw,
        table_col_use_map, equiv_vars)
    qfaj__ppxnp = set(vnc__xaibj for vnc__xaibj in sort_node.key_inds if 
        vnc__xaibj < sort_node.num_table_arrays)
    block_use_map[qoik__oioqa
        ] = rdq__fvu | ilajc__qrtrb | qfaj__ppxnp, tju__nkn or zooe__cmrk, False


ir_extension_table_column_use[Sort] = sort_table_column_use


def sort_remove_dead_column(sort_node, column_live_map, equiv_vars, typemap):
    if not sort_node.is_table_format or sort_node.out_vars[0] is None:
        return False
    vkd__xgz = sort_node.num_table_arrays
    cggn__ctw = sort_node.out_vars[0].name
    pfgz__erjq = _find_used_columns(cggn__ctw, vkd__xgz, column_live_map,
        equiv_vars)
    if pfgz__erjq is None:
        return False
    wta__rip = set(range(vkd__xgz)) - pfgz__erjq
    qfaj__ppxnp = set(vnc__xaibj for vnc__xaibj in sort_node.key_inds if 
        vnc__xaibj < vkd__xgz)
    dwl__ahun = sort_node.dead_key_var_inds | wta__rip & qfaj__ppxnp
    hygp__ebr = sort_node.dead_var_inds | wta__rip - qfaj__ppxnp
    nerdp__xpzhx = (dwl__ahun != sort_node.dead_key_var_inds) | (hygp__ebr !=
        sort_node.dead_var_inds)
    sort_node.dead_key_var_inds = dwl__ahun
    sort_node.dead_var_inds = hygp__ebr
    return nerdp__xpzhx


remove_dead_column_extensions[Sort] = sort_remove_dead_column
