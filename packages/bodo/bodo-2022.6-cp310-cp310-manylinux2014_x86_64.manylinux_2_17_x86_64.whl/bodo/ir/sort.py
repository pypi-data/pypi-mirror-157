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
            self.na_position_b = tuple([(True if sag__oob == 'last' else 
                False) for sag__oob in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def get_live_in_vars(self):
        return [vhu__ppc for vhu__ppc in self.in_vars if vhu__ppc is not None]

    def get_live_out_vars(self):
        return [vhu__ppc for vhu__ppc in self.out_vars if vhu__ppc is not None]

    def __repr__(self):
        befi__zlo = ', '.join(vhu__ppc.name for vhu__ppc in self.
            get_live_in_vars())
        slzan__vkk = f'{self.df_in}{{{befi__zlo}}}'
        jaa__tzke = ', '.join(vhu__ppc.name for vhu__ppc in self.
            get_live_out_vars())
        yuosp__oqt = f'{self.df_out}{{{jaa__tzke}}}'
        return f'Sort (keys: {self.key_inds}): {slzan__vkk} {yuosp__oqt}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    ihurn__leirh = []
    for lhujv__qatw in sort_node.get_live_in_vars():
        iqa__qfs = equiv_set.get_shape(lhujv__qatw)
        if iqa__qfs is not None:
            ihurn__leirh.append(iqa__qfs[0])
    if len(ihurn__leirh) > 1:
        equiv_set.insert_equiv(*ihurn__leirh)
    wpd__wyztm = []
    ihurn__leirh = []
    for lhujv__qatw in sort_node.get_live_out_vars():
        fslk__rsrj = typemap[lhujv__qatw.name]
        sccno__qfqt = array_analysis._gen_shape_call(equiv_set, lhujv__qatw,
            fslk__rsrj.ndim, None, wpd__wyztm)
        equiv_set.insert_equiv(lhujv__qatw, sccno__qfqt)
        ihurn__leirh.append(sccno__qfqt[0])
        equiv_set.define(lhujv__qatw, set())
    if len(ihurn__leirh) > 1:
        equiv_set.insert_equiv(*ihurn__leirh)
    return [], wpd__wyztm


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    vwz__prllm = sort_node.get_live_in_vars()
    lsdgk__haou = sort_node.get_live_out_vars()
    yvig__ije = Distribution.OneD
    for lhujv__qatw in vwz__prllm:
        yvig__ije = Distribution(min(yvig__ije.value, array_dists[
            lhujv__qatw.name].value))
    ohx__pwhp = Distribution(min(yvig__ije.value, Distribution.OneD_Var.value))
    for lhujv__qatw in lsdgk__haou:
        if lhujv__qatw.name in array_dists:
            ohx__pwhp = Distribution(min(ohx__pwhp.value, array_dists[
                lhujv__qatw.name].value))
    if ohx__pwhp != Distribution.OneD_Var:
        yvig__ije = ohx__pwhp
    for lhujv__qatw in vwz__prllm:
        array_dists[lhujv__qatw.name] = yvig__ije
    for lhujv__qatw in lsdgk__haou:
        array_dists[lhujv__qatw.name] = ohx__pwhp


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for pkuu__lbbg, dkvsg__kvqb in enumerate(sort_node.out_vars):
        yls__goo = sort_node.in_vars[pkuu__lbbg]
        if yls__goo is not None and dkvsg__kvqb is not None:
            typeinferer.constraints.append(typeinfer.Propagate(dst=
                dkvsg__kvqb.name, src=yls__goo.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for lhujv__qatw in sort_node.get_live_out_vars():
            definitions[lhujv__qatw.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for pkuu__lbbg in range(len(sort_node.in_vars)):
        if sort_node.in_vars[pkuu__lbbg] is not None:
            sort_node.in_vars[pkuu__lbbg] = visit_vars_inner(sort_node.
                in_vars[pkuu__lbbg], callback, cbdata)
        if sort_node.out_vars[pkuu__lbbg] is not None:
            sort_node.out_vars[pkuu__lbbg] = visit_vars_inner(sort_node.
                out_vars[pkuu__lbbg], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if sort_node.is_table_format:
        xaggq__ebx = sort_node.out_vars[0]
        if xaggq__ebx is not None and xaggq__ebx.name not in lives:
            sort_node.out_vars[0] = None
            dead_cols = set(range(sort_node.num_table_arrays))
            imm__xzgw = set(sort_node.key_inds)
            sort_node.dead_key_var_inds.update(dead_cols & imm__xzgw)
            sort_node.dead_var_inds.update(dead_cols - imm__xzgw)
            if len(imm__xzgw & dead_cols) == 0:
                sort_node.in_vars[0] = None
        for pkuu__lbbg in range(1, len(sort_node.out_vars)):
            vhu__ppc = sort_node.out_vars[pkuu__lbbg]
            if vhu__ppc is not None and vhu__ppc.name not in lives:
                sort_node.out_vars[pkuu__lbbg] = None
                uyzn__wovqi = sort_node.num_table_arrays + pkuu__lbbg - 1
                if uyzn__wovqi in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(uyzn__wovqi)
                else:
                    sort_node.dead_var_inds.add(uyzn__wovqi)
                    sort_node.in_vars[pkuu__lbbg] = None
    else:
        for pkuu__lbbg in range(len(sort_node.out_vars)):
            vhu__ppc = sort_node.out_vars[pkuu__lbbg]
            if vhu__ppc is not None and vhu__ppc.name not in lives:
                sort_node.out_vars[pkuu__lbbg] = None
                if pkuu__lbbg in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(pkuu__lbbg)
                else:
                    sort_node.dead_var_inds.add(pkuu__lbbg)
                    sort_node.in_vars[pkuu__lbbg] = None
    if all(vhu__ppc is None for vhu__ppc in sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({vhu__ppc.name for vhu__ppc in sort_node.get_live_in_vars()}
        )
    if not sort_node.inplace:
        def_set.update({vhu__ppc.name for vhu__ppc in sort_node.
            get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    yuk__grn = set()
    if not sort_node.inplace:
        yuk__grn.update({vhu__ppc.name for vhu__ppc in sort_node.
            get_live_out_vars()})
    return set(), yuk__grn


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for pkuu__lbbg in range(len(sort_node.in_vars)):
        if sort_node.in_vars[pkuu__lbbg] is not None:
            sort_node.in_vars[pkuu__lbbg] = replace_vars_inner(sort_node.
                in_vars[pkuu__lbbg], var_dict)
        if sort_node.out_vars[pkuu__lbbg] is not None:
            sort_node.out_vars[pkuu__lbbg] = replace_vars_inner(sort_node.
                out_vars[pkuu__lbbg], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = sort_node.get_live_in_vars()
    out_vars = sort_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for vhu__ppc in (in_vars + out_vars):
            if array_dists[vhu__ppc.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                vhu__ppc.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nodes = []
    if not sort_node.inplace:
        kzy__lsg = []
        for vhu__ppc in in_vars:
            qoc__gxdlg = _copy_array_nodes(vhu__ppc, nodes, typingctx,
                targetctx, typemap, calltypes, sort_node.dead_var_inds)
            kzy__lsg.append(qoc__gxdlg)
        in_vars = kzy__lsg
    out_types = [(typemap[vhu__ppc.name] if vhu__ppc is not None else types
        .none) for vhu__ppc in sort_node.out_vars]
    bqsvd__dgz, lycmg__uyx = get_sort_cpp_section(sort_node, out_types,
        parallel)
    imegq__wrdrf = {}
    exec(bqsvd__dgz, {}, imegq__wrdrf)
    mcyo__bccuk = imegq__wrdrf['f']
    lycmg__uyx.update({'bodo': bodo, 'np': np, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'sort_values_table': sort_values_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'array_to_info': array_to_info,
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    lycmg__uyx.update({f'out_type{pkuu__lbbg}': out_types[pkuu__lbbg] for
        pkuu__lbbg in range(len(out_types))})
    tui__qfc = compile_to_numba_ir(mcyo__bccuk, lycmg__uyx, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[vhu__ppc.
        name] for vhu__ppc in in_vars), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(tui__qfc, in_vars)
    gta__mjuor = tui__qfc.body[-2].value.value
    nodes += tui__qfc.body[:-2]
    for pkuu__lbbg, vhu__ppc in enumerate(out_vars):
        gen_getitem(vhu__ppc, gta__mjuor, pkuu__lbbg, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes,
    dead_cols):
    from bodo.hiframes.table import TableType
    xgoml__dvv = lambda arr: arr.copy()
    vvyb__fnkzy = None
    if isinstance(typemap[var.name], TableType):
        kraqb__epla = len(typemap[var.name].arr_types)
        vvyb__fnkzy = set(range(kraqb__epla)) - dead_cols
        vvyb__fnkzy = MetaType(tuple(sorted(vvyb__fnkzy)))
        xgoml__dvv = (lambda T: bodo.utils.table_utils.
            generate_mappable_table_func(T, 'copy', types.none, True,
            used_cols=_used_columns))
    tui__qfc = compile_to_numba_ir(xgoml__dvv, {'bodo': bodo, 'types':
        types, '_used_columns': vvyb__fnkzy}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(tui__qfc, [var])
    nodes += tui__qfc.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(sort_node, out_types, parallel):
    uoom__vvl = len(sort_node.key_inds)
    plsdg__pnx = len(sort_node.in_vars)
    sepp__akxuq = len(sort_node.out_vars)
    n_cols = (sort_node.num_table_arrays + plsdg__pnx - 1 if sort_node.
        is_table_format else plsdg__pnx)
    lzwhu__vbztk, jdnki__shdrx, eepfv__szdqn = _get_cpp_col_ind_mappings(
        sort_node.key_inds, sort_node.dead_var_inds, sort_node.
        dead_key_var_inds, n_cols)
    jrn__qaj = []
    if sort_node.is_table_format:
        jrn__qaj.append('arg0')
        for pkuu__lbbg in range(1, plsdg__pnx):
            uyzn__wovqi = sort_node.num_table_arrays + pkuu__lbbg - 1
            if uyzn__wovqi not in sort_node.dead_var_inds:
                jrn__qaj.append(f'arg{uyzn__wovqi}')
    else:
        for pkuu__lbbg in range(n_cols):
            if pkuu__lbbg not in sort_node.dead_var_inds:
                jrn__qaj.append(f'arg{pkuu__lbbg}')
    bqsvd__dgz = f"def f({', '.join(jrn__qaj)}):\n"
    if sort_node.is_table_format:
        wemj__khhx = ',' if plsdg__pnx - 1 == 1 else ''
        xoc__wms = []
        for pkuu__lbbg in range(sort_node.num_table_arrays, n_cols):
            if pkuu__lbbg in sort_node.dead_var_inds:
                xoc__wms.append('None')
            else:
                xoc__wms.append(f'arg{pkuu__lbbg}')
        bqsvd__dgz += f"""  in_cpp_table = py_data_to_cpp_table(arg0, ({', '.join(xoc__wms)}{wemj__khhx}), in_col_inds, {sort_node.num_table_arrays})
"""
    else:
        yionr__pdt = {dhxff__yxjn: pkuu__lbbg for pkuu__lbbg, dhxff__yxjn in
            enumerate(lzwhu__vbztk)}
        aes__esc = [None] * len(lzwhu__vbztk)
        for pkuu__lbbg in range(n_cols):
            hfh__jyn = yionr__pdt.get(pkuu__lbbg, -1)
            if hfh__jyn != -1:
                aes__esc[hfh__jyn] = f'array_to_info(arg{pkuu__lbbg})'
        bqsvd__dgz += '  info_list_total = [{}]\n'.format(','.join(aes__esc))
        bqsvd__dgz += (
            '  in_cpp_table = arr_info_list_to_table(info_list_total)\n')
    bqsvd__dgz += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if sdwuj__slwfi else '0' for sdwuj__slwfi in sort_node.
        ascending_list))
    bqsvd__dgz += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if sdwuj__slwfi else '0' for sdwuj__slwfi in sort_node.
        na_position_b))
    bqsvd__dgz += '  dead_keys = np.array([{}], np.int64)\n'.format(','.
        join('1' if pkuu__lbbg in eepfv__szdqn else '0' for pkuu__lbbg in
        range(uoom__vvl)))
    bqsvd__dgz += f'  total_rows_np = np.array([0], dtype=np.int64)\n'
    bqsvd__dgz += f"""  out_cpp_table = sort_values_table(in_cpp_table, {uoom__vvl}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, total_rows_np.ctypes, {parallel})
"""
    if sort_node.is_table_format:
        wemj__khhx = ',' if sepp__akxuq == 1 else ''
        out_types = (
            f"({', '.join(f'out_type{pkuu__lbbg}' if not type_has_unknown_cats(out_types[pkuu__lbbg]) else f'arg{pkuu__lbbg}' for pkuu__lbbg in range(sepp__akxuq))}{wemj__khhx})"
            )
        bqsvd__dgz += f"""  out_data = cpp_table_to_py_data(out_cpp_table, out_col_inds, {out_types}, total_rows_np[0], {sort_node.num_table_arrays})
"""
    else:
        yionr__pdt = {dhxff__yxjn: pkuu__lbbg for pkuu__lbbg, dhxff__yxjn in
            enumerate(jdnki__shdrx)}
        aes__esc = []
        for pkuu__lbbg in range(n_cols):
            hfh__jyn = yionr__pdt.get(pkuu__lbbg, -1)
            if hfh__jyn != -1:
                sst__xvkf = (f'out_type{pkuu__lbbg}' if not
                    type_has_unknown_cats(out_types[pkuu__lbbg]) else
                    f'arg{pkuu__lbbg}')
                bqsvd__dgz += f"""  out{pkuu__lbbg} = info_to_array(info_from_table(out_cpp_table, {hfh__jyn}), {sst__xvkf})
"""
                aes__esc.append(f'out{pkuu__lbbg}')
        wemj__khhx = ',' if len(aes__esc) == 1 else ''
        mnso__rorb = f"({', '.join(aes__esc)}{wemj__khhx})"
        bqsvd__dgz += f'  out_data = {mnso__rorb}\n'
    bqsvd__dgz += '  delete_table(out_cpp_table)\n'
    bqsvd__dgz += '  delete_table(in_cpp_table)\n'
    bqsvd__dgz += f'  return out_data\n'
    return bqsvd__dgz, {'in_col_inds': MetaType(tuple(lzwhu__vbztk)),
        'out_col_inds': MetaType(tuple(jdnki__shdrx))}


def _get_cpp_col_ind_mappings(key_inds, dead_var_inds, dead_key_var_inds,
    n_cols):
    lzwhu__vbztk = []
    jdnki__shdrx = []
    eepfv__szdqn = []
    for dhxff__yxjn, pkuu__lbbg in enumerate(key_inds):
        lzwhu__vbztk.append(pkuu__lbbg)
        if pkuu__lbbg in dead_key_var_inds:
            eepfv__szdqn.append(dhxff__yxjn)
        else:
            jdnki__shdrx.append(pkuu__lbbg)
    for pkuu__lbbg in range(n_cols):
        if pkuu__lbbg in dead_var_inds or pkuu__lbbg in key_inds:
            continue
        lzwhu__vbztk.append(pkuu__lbbg)
        jdnki__shdrx.append(pkuu__lbbg)
    return lzwhu__vbztk, jdnki__shdrx, eepfv__szdqn


def sort_table_column_use(sort_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not sort_node.is_table_format or sort_node.in_vars[0
        ] is None or sort_node.out_vars[0] is None:
        return
    htfj__zzc = sort_node.in_vars[0].name
    cupls__yxist = sort_node.out_vars[0].name
    rhjfi__jrfr, ugfb__udju, euy__qxs = block_use_map[htfj__zzc]
    if ugfb__udju or euy__qxs:
        return
    mre__dmtm, cww__lyzk, elpk__svjw = _compute_table_column_uses(cupls__yxist,
        table_col_use_map, equiv_vars)
    ior__hhxu = set(pkuu__lbbg for pkuu__lbbg in sort_node.key_inds if 
        pkuu__lbbg < sort_node.num_table_arrays)
    block_use_map[htfj__zzc
        ] = rhjfi__jrfr | mre__dmtm | ior__hhxu, cww__lyzk or elpk__svjw, False


ir_extension_table_column_use[Sort] = sort_table_column_use


def sort_remove_dead_column(sort_node, column_live_map, equiv_vars, typemap):
    if not sort_node.is_table_format or sort_node.out_vars[0] is None:
        return False
    kraqb__epla = sort_node.num_table_arrays
    cupls__yxist = sort_node.out_vars[0].name
    vvyb__fnkzy = _find_used_columns(cupls__yxist, kraqb__epla,
        column_live_map, equiv_vars)
    if vvyb__fnkzy is None:
        return False
    rju__hbzn = set(range(kraqb__epla)) - vvyb__fnkzy
    ior__hhxu = set(pkuu__lbbg for pkuu__lbbg in sort_node.key_inds if 
        pkuu__lbbg < kraqb__epla)
    hnc__adr = sort_node.dead_key_var_inds | rju__hbzn & ior__hhxu
    ygjtk__vxcmp = sort_node.dead_var_inds | rju__hbzn - ior__hhxu
    xehye__itg = (hnc__adr != sort_node.dead_key_var_inds) | (ygjtk__vxcmp !=
        sort_node.dead_var_inds)
    sort_node.dead_key_var_inds = hnc__adr
    sort_node.dead_var_inds = ygjtk__vxcmp
    return xehye__itg


remove_dead_column_extensions[Sort] = sort_remove_dead_column
