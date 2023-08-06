"""IR node for the join and merge"""
from collections import defaultdict
from typing import Dict, List, Literal, Optional, Set, Tuple, Union
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir, ir_utils, types
from numba.core.ir_utils import compile_to_numba_ir, next_label, replace_arg_nodes, replace_vars_inner, visit_vars_inner
from numba.extending import intrinsic
import bodo
from bodo.hiframes.table import TableType
from bodo.ir.connector import trim_extra_used_columns
from bodo.libs.array import arr_info_list_to_table, array_to_info, cpp_table_to_py_data, delete_table, hash_join_table, py_data_to_cpp_table
from bodo.libs.timsort import getitem_arr_tup, setitem_arr_tup
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import _compute_table_column_uses, get_live_column_nums_block, ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import INDEX_SENTINEL, BodoError, MetaType, dtype_to_array_type, find_common_np_dtype, is_dtype_nullable, is_nullable_type, is_str_arr_type, to_nullable_type
from bodo.utils.utils import alloc_arr_tup, is_null_pointer
join_gen_cond_cfunc = {}
join_gen_cond_cfunc_addr = {}


@intrinsic
def add_join_gen_cond_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        odze__fsllr = func.signature
        ajz__bynm = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        nnjke__ymewj = cgutils.get_or_insert_function(builder.module,
            ajz__bynm, sym._literal_value)
        builder.call(nnjke__ymewj, [context.get_constant_null(odze__fsllr.
            args[0]), context.get_constant_null(odze__fsllr.args[1]),
            context.get_constant_null(odze__fsllr.args[2]), context.
            get_constant_null(odze__fsllr.args[3]), context.
            get_constant_null(odze__fsllr.args[4]), context.
            get_constant_null(odze__fsllr.args[5]), context.get_constant(
            types.int64, 0), context.get_constant(types.int64, 0)])
        context.add_linking_libs([join_gen_cond_cfunc[sym._literal_value].
            _library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_join_cond_addr(name):
    with numba.objmode(addr='int64'):
        addr = join_gen_cond_cfunc_addr[name]
    return addr


HOW_OPTIONS = Literal['inner', 'left', 'right', 'outer', 'asof']


class Join(ir.Stmt):

    def __init__(self, left_keys: Union[List[str], str], right_keys: Union[
        List[str], str], out_data_vars: List[ir.Var], out_df_type: bodo.
        DataFrameType, left_vars: List[ir.Var], left_df_type: bodo.
        DataFrameType, right_vars: List[ir.Var], right_df_type: bodo.
        DataFrameType, how: HOW_OPTIONS, suffix_left: str, suffix_right:
        str, loc: ir.Loc, is_left: bool, is_right: bool, is_join: bool,
        left_index: bool, right_index: bool, indicator_col_num: int,
        is_na_equal: bool, gen_cond_expr: str):
        self.left_keys = left_keys
        self.right_keys = right_keys
        self.out_data_vars = out_data_vars
        self.out_col_names = out_df_type.columns
        self.left_vars = left_vars
        self.right_vars = right_vars
        self.how = how
        self.loc = loc
        self.is_left = is_left
        self.is_right = is_right
        self.is_join = is_join
        self.left_index = left_index
        self.right_index = right_index
        self.indicator_col_num = indicator_col_num
        self.is_na_equal = is_na_equal
        self.gen_cond_expr = gen_cond_expr
        self.n_out_table_cols = len(self.out_col_names)
        self.out_used_cols = set(range(self.n_out_table_cols))
        if self.out_data_vars[1] is not None:
            self.out_used_cols.add(self.n_out_table_cols)
        ggy__lgorl = left_df_type.columns
        ndxm__ouear = right_df_type.columns
        self.left_col_names = ggy__lgorl
        self.right_col_names = ndxm__ouear
        self.is_left_table = left_df_type.is_table_format
        self.is_right_table = right_df_type.is_table_format
        self.n_left_table_cols = len(ggy__lgorl) if self.is_left_table else 0
        self.n_right_table_cols = len(ndxm__ouear
            ) if self.is_right_table else 0
        byk__dhh = self.n_left_table_cols if self.is_left_table else len(
            left_vars) - 1
        syqrs__dca = self.n_right_table_cols if self.is_right_table else len(
            right_vars) - 1
        self.left_dead_var_inds = set()
        self.right_dead_var_inds = set()
        if self.left_vars[-1] is None:
            self.left_dead_var_inds.add(byk__dhh)
        if self.right_vars[-1] is None:
            self.right_dead_var_inds.add(syqrs__dca)
        self.left_var_map = {khndh__pssza: burlk__vfkk for burlk__vfkk,
            khndh__pssza in enumerate(ggy__lgorl)}
        self.right_var_map = {khndh__pssza: burlk__vfkk for burlk__vfkk,
            khndh__pssza in enumerate(ndxm__ouear)}
        if self.left_vars[-1] is not None:
            self.left_var_map[INDEX_SENTINEL] = byk__dhh
        if self.right_vars[-1] is not None:
            self.right_var_map[INDEX_SENTINEL] = syqrs__dca
        self.left_key_set = set(self.left_var_map[khndh__pssza] for
            khndh__pssza in left_keys)
        self.right_key_set = set(self.right_var_map[khndh__pssza] for
            khndh__pssza in right_keys)
        if gen_cond_expr:
            self.left_cond_cols = set(self.left_var_map[khndh__pssza] for
                khndh__pssza in ggy__lgorl if f'(left.{khndh__pssza})' in
                gen_cond_expr)
            self.right_cond_cols = set(self.right_var_map[khndh__pssza] for
                khndh__pssza in ndxm__ouear if f'(right.{khndh__pssza})' in
                gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        qycay__unf: int = -1
        gcm__suovi = set(left_keys) & set(right_keys)
        vnhqm__zcsfr = set(ggy__lgorl) & set(ndxm__ouear)
        dbx__ifiku = vnhqm__zcsfr - gcm__suovi
        xbhbn__vcv: Dict[int, (Literal['left', 'right'], int)] = {}
        kcv__zgimk: Dict[int, int] = {}
        ktnw__njlg: Dict[int, int] = {}
        for burlk__vfkk, khndh__pssza in enumerate(ggy__lgorl):
            if khndh__pssza in dbx__ifiku:
                bfr__bvh = str(khndh__pssza) + suffix_left
                cykz__auhi = out_df_type.column_index[bfr__bvh]
                if (right_index and not left_index and burlk__vfkk in self.
                    left_key_set):
                    qycay__unf = out_df_type.column_index[khndh__pssza]
                    xbhbn__vcv[qycay__unf] = 'left', burlk__vfkk
            else:
                cykz__auhi = out_df_type.column_index[khndh__pssza]
            xbhbn__vcv[cykz__auhi] = 'left', burlk__vfkk
            kcv__zgimk[burlk__vfkk] = cykz__auhi
        for burlk__vfkk, khndh__pssza in enumerate(ndxm__ouear):
            if khndh__pssza not in gcm__suovi:
                if khndh__pssza in dbx__ifiku:
                    rxbgy__qgawg = str(khndh__pssza) + suffix_right
                    cykz__auhi = out_df_type.column_index[rxbgy__qgawg]
                    if (left_index and not right_index and burlk__vfkk in
                        self.right_key_set):
                        qycay__unf = out_df_type.column_index[khndh__pssza]
                        xbhbn__vcv[qycay__unf] = 'right', burlk__vfkk
                else:
                    cykz__auhi = out_df_type.column_index[khndh__pssza]
                xbhbn__vcv[cykz__auhi] = 'right', burlk__vfkk
                ktnw__njlg[burlk__vfkk] = cykz__auhi
        if self.left_vars[-1] is not None:
            kcv__zgimk[byk__dhh] = self.n_out_table_cols
        if self.right_vars[-1] is not None:
            ktnw__njlg[syqrs__dca] = self.n_out_table_cols
        self.out_to_input_col_map = xbhbn__vcv
        self.left_to_output_map = kcv__zgimk
        self.right_to_output_map = ktnw__njlg
        self.extra_data_col_num = qycay__unf
        if len(out_data_vars) > 1:
            tkhh__sglz = 'left' if right_index else 'right'
            if tkhh__sglz == 'left':
                dzt__itxz = byk__dhh
            elif tkhh__sglz == 'right':
                dzt__itxz = syqrs__dca
        else:
            tkhh__sglz = None
            dzt__itxz = -1
        self.index_source = tkhh__sglz
        self.index_col_num = dzt__itxz
        xrl__dsvu = []
        rjs__voquz = len(left_keys)
        for vmad__qnsje in range(rjs__voquz):
            typ__zpav = left_keys[vmad__qnsje]
            vby__jlzq = right_keys[vmad__qnsje]
            xrl__dsvu.append(typ__zpav == vby__jlzq)
        self.vect_same_key = xrl__dsvu

    @property
    def has_live_left_table_var(self):
        return self.is_left_table and self.left_vars[0] is not None

    @property
    def has_live_right_table_var(self):
        return self.is_right_table and self.right_vars[0] is not None

    @property
    def has_live_out_table_var(self):
        return self.out_data_vars[0] is not None

    @property
    def has_live_out_index_var(self):
        return self.out_data_vars[1] is not None

    def get_out_table_var(self):
        return self.out_data_vars[0]

    def get_out_index_var(self):
        return self.out_data_vars[1]

    def get_live_left_vars(self):
        vars = []
        for vwxip__tonp in self.left_vars:
            if vwxip__tonp is not None:
                vars.append(vwxip__tonp)
        return vars

    def get_live_right_vars(self):
        vars = []
        for vwxip__tonp in self.right_vars:
            if vwxip__tonp is not None:
                vars.append(vwxip__tonp)
        return vars

    def get_live_out_vars(self):
        vars = []
        for vwxip__tonp in self.out_data_vars:
            if vwxip__tonp is not None:
                vars.append(vwxip__tonp)
        return vars

    def set_live_left_vars(self, live_data_vars):
        left_vars = []
        ecw__oyd = 0
        start = 0
        if self.is_left_table:
            if self.has_live_left_table_var:
                left_vars.append(live_data_vars[ecw__oyd])
                ecw__oyd += 1
            else:
                left_vars.append(None)
            start = 1
        hvcbi__uorz = max(self.n_left_table_cols - 1, 0)
        for burlk__vfkk in range(start, len(self.left_vars)):
            if burlk__vfkk + hvcbi__uorz in self.left_dead_var_inds:
                left_vars.append(None)
            else:
                left_vars.append(live_data_vars[ecw__oyd])
                ecw__oyd += 1
        self.left_vars = left_vars

    def set_live_right_vars(self, live_data_vars):
        right_vars = []
        ecw__oyd = 0
        start = 0
        if self.is_right_table:
            if self.has_live_right_table_var:
                right_vars.append(live_data_vars[ecw__oyd])
                ecw__oyd += 1
            else:
                right_vars.append(None)
            start = 1
        hvcbi__uorz = max(self.n_right_table_cols - 1, 0)
        for burlk__vfkk in range(start, len(self.right_vars)):
            if burlk__vfkk + hvcbi__uorz in self.right_dead_var_inds:
                right_vars.append(None)
            else:
                right_vars.append(live_data_vars[ecw__oyd])
                ecw__oyd += 1
        self.right_vars = right_vars

    def set_live_out_data_vars(self, live_data_vars):
        out_data_vars = []
        ojm__qog = [self.has_live_out_table_var, self.has_live_out_index_var]
        ecw__oyd = 0
        for burlk__vfkk in range(len(self.out_data_vars)):
            if not ojm__qog[burlk__vfkk]:
                out_data_vars.append(None)
            else:
                out_data_vars.append(live_data_vars[ecw__oyd])
                ecw__oyd += 1
        self.out_data_vars = out_data_vars

    def get_out_table_used_cols(self):
        return {burlk__vfkk for burlk__vfkk in self.out_used_cols if 
            burlk__vfkk < self.n_out_table_cols}

    def __repr__(self):
        sdkk__rtowl = ', '.join([f'{khndh__pssza}' for khndh__pssza in self
            .left_col_names])
        cxvsl__slxp = f'left={{{sdkk__rtowl}}}'
        sdkk__rtowl = ', '.join([f'{khndh__pssza}' for khndh__pssza in self
            .right_col_names])
        iqflw__yaznm = f'right={{{sdkk__rtowl}}}'
        return 'join [{}={}]: {}, {}'.format(self.left_keys, self.
            right_keys, cxvsl__slxp, iqflw__yaznm)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    fwo__uhs = []
    assert len(join_node.get_live_out_vars()
        ) > 0, 'empty join in array analysis'
    rud__xhauw = []
    fvl__fdet = join_node.get_live_left_vars()
    for vqbzj__qwwve in fvl__fdet:
        nin__ykuf = typemap[vqbzj__qwwve.name]
        drhq__worz = equiv_set.get_shape(vqbzj__qwwve)
        if drhq__worz:
            rud__xhauw.append(drhq__worz[0])
    if len(rud__xhauw) > 1:
        equiv_set.insert_equiv(*rud__xhauw)
    rud__xhauw = []
    fvl__fdet = list(join_node.get_live_right_vars())
    for vqbzj__qwwve in fvl__fdet:
        nin__ykuf = typemap[vqbzj__qwwve.name]
        drhq__worz = equiv_set.get_shape(vqbzj__qwwve)
        if drhq__worz:
            rud__xhauw.append(drhq__worz[0])
    if len(rud__xhauw) > 1:
        equiv_set.insert_equiv(*rud__xhauw)
    rud__xhauw = []
    for gwv__nyoz in join_node.get_live_out_vars():
        nin__ykuf = typemap[gwv__nyoz.name]
        msc__zowo = array_analysis._gen_shape_call(equiv_set, gwv__nyoz,
            nin__ykuf.ndim, None, fwo__uhs)
        equiv_set.insert_equiv(gwv__nyoz, msc__zowo)
        rud__xhauw.append(msc__zowo[0])
        equiv_set.define(gwv__nyoz, set())
    if len(rud__xhauw) > 1:
        equiv_set.insert_equiv(*rud__xhauw)
    return [], fwo__uhs


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    bzbm__nittx = Distribution.OneD
    fxs__ghtll = Distribution.OneD
    for vqbzj__qwwve in join_node.get_live_left_vars():
        bzbm__nittx = Distribution(min(bzbm__nittx.value, array_dists[
            vqbzj__qwwve.name].value))
    for vqbzj__qwwve in join_node.get_live_right_vars():
        fxs__ghtll = Distribution(min(fxs__ghtll.value, array_dists[
            vqbzj__qwwve.name].value))
    dvwnl__tqh = Distribution.OneD_Var
    for gwv__nyoz in join_node.get_live_out_vars():
        if gwv__nyoz.name in array_dists:
            dvwnl__tqh = Distribution(min(dvwnl__tqh.value, array_dists[
                gwv__nyoz.name].value))
    wrqa__xqho = Distribution(min(dvwnl__tqh.value, bzbm__nittx.value))
    epq__ppkc = Distribution(min(dvwnl__tqh.value, fxs__ghtll.value))
    dvwnl__tqh = Distribution(max(wrqa__xqho.value, epq__ppkc.value))
    for gwv__nyoz in join_node.get_live_out_vars():
        array_dists[gwv__nyoz.name] = dvwnl__tqh
    if dvwnl__tqh != Distribution.OneD_Var:
        bzbm__nittx = dvwnl__tqh
        fxs__ghtll = dvwnl__tqh
    for vqbzj__qwwve in join_node.get_live_left_vars():
        array_dists[vqbzj__qwwve.name] = bzbm__nittx
    for vqbzj__qwwve in join_node.get_live_right_vars():
        array_dists[vqbzj__qwwve.name] = fxs__ghtll
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def visit_vars_join(join_node, callback, cbdata):
    join_node.set_live_left_vars([visit_vars_inner(vwxip__tonp, callback,
        cbdata) for vwxip__tonp in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([visit_vars_inner(vwxip__tonp, callback,
        cbdata) for vwxip__tonp in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([visit_vars_inner(vwxip__tonp,
        callback, cbdata) for vwxip__tonp in join_node.get_live_out_vars()])


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if join_node.has_live_out_table_var:
        eqnuk__opmx = []
        gzsr__axjcl = join_node.get_out_table_var()
        if gzsr__axjcl.name not in lives:
            join_node.out_data_vars[0] = None
            join_node.out_used_cols.difference_update(join_node.
                get_out_table_used_cols())
        for ntxbi__voyyw in join_node.out_to_input_col_map.keys():
            if ntxbi__voyyw in join_node.out_used_cols:
                continue
            eqnuk__opmx.append(ntxbi__voyyw)
            if join_node.indicator_col_num == ntxbi__voyyw:
                join_node.indicator_col_num = -1
                continue
            if ntxbi__voyyw == join_node.extra_data_col_num:
                join_node.extra_data_col_num = -1
                continue
            fvbru__git, ntxbi__voyyw = join_node.out_to_input_col_map[
                ntxbi__voyyw]
            if fvbru__git == 'left':
                if (ntxbi__voyyw not in join_node.left_key_set and 
                    ntxbi__voyyw not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(ntxbi__voyyw)
                    if not join_node.is_left_table:
                        join_node.left_vars[ntxbi__voyyw] = None
            elif fvbru__git == 'right':
                if (ntxbi__voyyw not in join_node.right_key_set and 
                    ntxbi__voyyw not in join_node.right_cond_cols):
                    join_node.right_dead_var_inds.add(ntxbi__voyyw)
                    if not join_node.is_right_table:
                        join_node.right_vars[ntxbi__voyyw] = None
        for burlk__vfkk in eqnuk__opmx:
            del join_node.out_to_input_col_map[burlk__vfkk]
        if join_node.is_left_table:
            kvgku__hvgx = set(range(join_node.n_left_table_cols))
            uhv__lezh = not bool(kvgku__hvgx - join_node.left_dead_var_inds)
            if uhv__lezh:
                join_node.left_vars[0] = None
        if join_node.is_right_table:
            kvgku__hvgx = set(range(join_node.n_right_table_cols))
            uhv__lezh = not bool(kvgku__hvgx - join_node.right_dead_var_inds)
            if uhv__lezh:
                join_node.right_vars[0] = None
    if join_node.has_live_out_index_var:
        mfijp__aqlmz = join_node.get_out_index_var()
        if mfijp__aqlmz.name not in lives:
            join_node.out_data_vars[1] = None
            join_node.out_used_cols.remove(join_node.n_out_table_cols)
            if join_node.index_source == 'left':
                if (join_node.index_col_num not in join_node.left_key_set and
                    join_node.index_col_num not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(join_node.index_col_num)
                    join_node.left_vars[-1] = None
            elif join_node.index_col_num not in join_node.right_key_set and join_node.index_col_num not in join_node.right_cond_cols:
                join_node.right_dead_var_inds.add(join_node.index_col_num)
                join_node.right_vars[-1] = None
    if not (join_node.has_live_out_table_var or join_node.
        has_live_out_index_var):
        return None
    return join_node


ir_utils.remove_dead_extensions[Join] = remove_dead_join


def join_remove_dead_column(join_node, column_live_map, equiv_vars, typemap):
    xer__fydva = False
    if join_node.has_live_out_table_var:
        djce__dmn = join_node.get_out_table_var().name
        yedg__mtb, wxq__meinm, yyz__pwvyz = get_live_column_nums_block(
            column_live_map, equiv_vars, djce__dmn)
        if not (wxq__meinm or yyz__pwvyz):
            yedg__mtb = trim_extra_used_columns(yedg__mtb, join_node.
                n_out_table_cols)
            khsdk__jccpk = join_node.get_out_table_used_cols()
            if len(yedg__mtb) != len(khsdk__jccpk):
                xer__fydva = not (join_node.is_left_table and join_node.
                    is_right_table)
                yeacx__okjux = khsdk__jccpk - yedg__mtb
                join_node.out_used_cols = (join_node.out_used_cols -
                    yeacx__okjux)
    return xer__fydva


remove_dead_column_extensions[Join] = join_remove_dead_column


def join_table_column_use(join_node: Join, block_use_map: Dict[str, Tuple[
    Set[int], bool, bool]], equiv_vars: Dict[str, Set[str]], typemap: Dict[
    str, types.Type], table_col_use_map: Dict[int, Dict[str, Tuple[Set[int],
    bool, bool]]]):
    if not (join_node.is_left_table or join_node.is_right_table):
        return
    if join_node.has_live_out_table_var:
        zsvu__zigp = join_node.get_out_table_var()
        qvcm__sgjs, wxq__meinm, yyz__pwvyz = _compute_table_column_uses(
            zsvu__zigp.name, table_col_use_map, equiv_vars)
    else:
        qvcm__sgjs, wxq__meinm, yyz__pwvyz = set(), False, False
    if join_node.has_live_left_table_var:
        hrts__sbf = join_node.left_vars[0].name
        jql__ppx, rhgun__tkh, vud__fvhju = block_use_map[hrts__sbf]
        if not (rhgun__tkh or vud__fvhju):
            tey__gcde = set([join_node.out_to_input_col_map[burlk__vfkk][1] for
                burlk__vfkk in qvcm__sgjs if join_node.out_to_input_col_map
                [burlk__vfkk][0] == 'left'])
            ubqyg__uep = set(burlk__vfkk for burlk__vfkk in join_node.
                left_key_set | join_node.left_cond_cols if burlk__vfkk <
                join_node.n_left_table_cols)
            if not (wxq__meinm or yyz__pwvyz):
                join_node.left_dead_var_inds |= set(range(join_node.
                    n_left_table_cols)) - (tey__gcde | ubqyg__uep)
            block_use_map[hrts__sbf] = (jql__ppx | tey__gcde | ubqyg__uep, 
                wxq__meinm or yyz__pwvyz, False)
    if join_node.has_live_right_table_var:
        zkjp__bmog = join_node.right_vars[0].name
        jql__ppx, rhgun__tkh, vud__fvhju = block_use_map[zkjp__bmog]
        if not (rhgun__tkh or vud__fvhju):
            ctgch__lfqx = set([join_node.out_to_input_col_map[burlk__vfkk][
                1] for burlk__vfkk in qvcm__sgjs if join_node.
                out_to_input_col_map[burlk__vfkk][0] == 'right'])
            mgfte__jgret = set(burlk__vfkk for burlk__vfkk in join_node.
                right_key_set | join_node.right_cond_cols if burlk__vfkk <
                join_node.n_right_table_cols)
            if not (wxq__meinm or yyz__pwvyz):
                join_node.right_dead_var_inds |= set(range(join_node.
                    n_right_table_cols)) - (ctgch__lfqx | mgfte__jgret)
            block_use_map[zkjp__bmog] = (jql__ppx | ctgch__lfqx |
                mgfte__jgret, wxq__meinm or yyz__pwvyz, False)


ir_extension_table_column_use[Join] = join_table_column_use


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({jppm__ylggm.name for jppm__ylggm in join_node.
        get_live_left_vars()})
    use_set.update({jppm__ylggm.name for jppm__ylggm in join_node.
        get_live_right_vars()})
    def_set.update({jppm__ylggm.name for jppm__ylggm in join_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    egnii__povqo = set(jppm__ylggm.name for jppm__ylggm in join_node.
        get_live_out_vars())
    return set(), egnii__povqo


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    join_node.set_live_left_vars([replace_vars_inner(vwxip__tonp, var_dict) for
        vwxip__tonp in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([replace_vars_inner(vwxip__tonp, var_dict
        ) for vwxip__tonp in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([replace_vars_inner(vwxip__tonp,
        var_dict) for vwxip__tonp in join_node.get_live_out_vars()])


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for vqbzj__qwwve in join_node.get_live_out_vars():
        definitions[vqbzj__qwwve.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 2:
        vkwi__pnoyk = join_node.loc.strformat()
        gmq__gpljj = [join_node.left_col_names[burlk__vfkk] for burlk__vfkk in
            sorted(set(range(len(join_node.left_col_names))) - join_node.
            left_dead_var_inds)]
        fno__qycfo = """Finished column elimination on join's left input:
%s
Left input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', fno__qycfo,
            vkwi__pnoyk, gmq__gpljj)
        vnris__golwj = [join_node.right_col_names[burlk__vfkk] for
            burlk__vfkk in sorted(set(range(len(join_node.right_col_names))
            ) - join_node.right_dead_var_inds)]
        fno__qycfo = """Finished column elimination on join's right input:
%s
Right input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', fno__qycfo,
            vkwi__pnoyk, vnris__golwj)
        emnrq__vuv = [join_node.out_col_names[burlk__vfkk] for burlk__vfkk in
            sorted(join_node.get_out_table_used_cols())]
        fno__qycfo = (
            'Finished column pruning on join node:\n%s\nOutput columns: %s\n')
        bodo.user_logging.log_message('Column Pruning', fno__qycfo,
            vkwi__pnoyk, emnrq__vuv)
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    rjs__voquz = len(join_node.left_keys)
    out_physical_to_logical_list = []
    if join_node.has_live_out_table_var:
        out_table_type = typemap[join_node.get_out_table_var().name]
    else:
        out_table_type = types.none
    if join_node.has_live_out_index_var:
        index_col_type = typemap[join_node.get_out_index_var().name]
    else:
        index_col_type = types.none
    if join_node.extra_data_col_num != -1:
        out_physical_to_logical_list.append(join_node.extra_data_col_num)
    left_key_in_output = []
    right_key_in_output = []
    left_used_key_nums = set()
    right_used_key_nums = set()
    left_logical_physical_map = {}
    right_logical_physical_map = {}
    left_physical_to_logical_list = []
    right_physical_to_logical_list = []
    bzv__uio = 0
    xcup__zgkf = 0
    dft__ufzu = []
    for khndh__pssza in join_node.left_keys:
        tcg__gpuyl = join_node.left_var_map[khndh__pssza]
        if not join_node.is_left_table:
            dft__ufzu.append(join_node.left_vars[tcg__gpuyl])
        ojm__qog = 1
        cykz__auhi = join_node.left_to_output_map[tcg__gpuyl]
        if khndh__pssza == INDEX_SENTINEL:
            if (join_node.has_live_out_index_var and join_node.index_source ==
                'left' and join_node.index_col_num == tcg__gpuyl):
                out_physical_to_logical_list.append(cykz__auhi)
                left_used_key_nums.add(tcg__gpuyl)
            else:
                ojm__qog = 0
        elif cykz__auhi not in join_node.out_used_cols:
            ojm__qog = 0
        elif tcg__gpuyl in left_used_key_nums:
            ojm__qog = 0
        else:
            left_used_key_nums.add(tcg__gpuyl)
            out_physical_to_logical_list.append(cykz__auhi)
        left_physical_to_logical_list.append(tcg__gpuyl)
        left_logical_physical_map[tcg__gpuyl] = bzv__uio
        bzv__uio += 1
        left_key_in_output.append(ojm__qog)
    dft__ufzu = tuple(dft__ufzu)
    ureex__lxz = []
    for burlk__vfkk in range(len(join_node.left_col_names)):
        if (burlk__vfkk not in join_node.left_dead_var_inds and burlk__vfkk
             not in join_node.left_key_set):
            if not join_node.is_left_table:
                jppm__ylggm = join_node.left_vars[burlk__vfkk]
                ureex__lxz.append(jppm__ylggm)
            tnv__inxtf = 1
            nbcs__htl = 1
            cykz__auhi = join_node.left_to_output_map[burlk__vfkk]
            if burlk__vfkk in join_node.left_cond_cols:
                if cykz__auhi not in join_node.out_used_cols:
                    tnv__inxtf = 0
                left_key_in_output.append(tnv__inxtf)
            elif burlk__vfkk in join_node.left_dead_var_inds:
                tnv__inxtf = 0
                nbcs__htl = 0
            if tnv__inxtf:
                out_physical_to_logical_list.append(cykz__auhi)
            if nbcs__htl:
                left_physical_to_logical_list.append(burlk__vfkk)
                left_logical_physical_map[burlk__vfkk] = bzv__uio
                bzv__uio += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'left' and join_node.index_col_num not in join_node.left_key_set):
        if not join_node.is_left_table:
            ureex__lxz.append(join_node.left_vars[join_node.index_col_num])
        cykz__auhi = join_node.left_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(cykz__auhi)
        left_physical_to_logical_list.append(join_node.index_col_num)
    ureex__lxz = tuple(ureex__lxz)
    if join_node.is_left_table:
        ureex__lxz = tuple(join_node.get_live_left_vars())
    tbd__mqk = []
    for burlk__vfkk, khndh__pssza in enumerate(join_node.right_keys):
        tcg__gpuyl = join_node.right_var_map[khndh__pssza]
        if not join_node.is_right_table:
            tbd__mqk.append(join_node.right_vars[tcg__gpuyl])
        if not join_node.vect_same_key[burlk__vfkk] and not join_node.is_join:
            ojm__qog = 1
            if tcg__gpuyl not in join_node.right_to_output_map:
                ojm__qog = 0
            else:
                cykz__auhi = join_node.right_to_output_map[tcg__gpuyl]
                if khndh__pssza == INDEX_SENTINEL:
                    if (join_node.has_live_out_index_var and join_node.
                        index_source == 'right' and join_node.index_col_num ==
                        tcg__gpuyl):
                        out_physical_to_logical_list.append(cykz__auhi)
                        right_used_key_nums.add(tcg__gpuyl)
                    else:
                        ojm__qog = 0
                elif cykz__auhi not in join_node.out_used_cols:
                    ojm__qog = 0
                elif tcg__gpuyl in right_used_key_nums:
                    ojm__qog = 0
                else:
                    right_used_key_nums.add(tcg__gpuyl)
                    out_physical_to_logical_list.append(cykz__auhi)
            right_key_in_output.append(ojm__qog)
        right_physical_to_logical_list.append(tcg__gpuyl)
        right_logical_physical_map[tcg__gpuyl] = xcup__zgkf
        xcup__zgkf += 1
    tbd__mqk = tuple(tbd__mqk)
    mhd__tujt = []
    for burlk__vfkk in range(len(join_node.right_col_names)):
        if (burlk__vfkk not in join_node.right_dead_var_inds and 
            burlk__vfkk not in join_node.right_key_set):
            if not join_node.is_right_table:
                mhd__tujt.append(join_node.right_vars[burlk__vfkk])
            tnv__inxtf = 1
            nbcs__htl = 1
            cykz__auhi = join_node.right_to_output_map[burlk__vfkk]
            if burlk__vfkk in join_node.right_cond_cols:
                if cykz__auhi not in join_node.out_used_cols:
                    tnv__inxtf = 0
                right_key_in_output.append(tnv__inxtf)
            elif burlk__vfkk in join_node.right_dead_var_inds:
                tnv__inxtf = 0
                nbcs__htl = 0
            if tnv__inxtf:
                out_physical_to_logical_list.append(cykz__auhi)
            if nbcs__htl:
                right_physical_to_logical_list.append(burlk__vfkk)
                right_logical_physical_map[burlk__vfkk] = xcup__zgkf
                xcup__zgkf += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'right' and join_node.index_col_num not in join_node.right_key_set):
        if not join_node.is_right_table:
            mhd__tujt.append(join_node.right_vars[join_node.index_col_num])
        cykz__auhi = join_node.right_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(cykz__auhi)
        right_physical_to_logical_list.append(join_node.index_col_num)
    mhd__tujt = tuple(mhd__tujt)
    if join_node.is_right_table:
        mhd__tujt = tuple(join_node.get_live_right_vars())
    if join_node.indicator_col_num != -1:
        out_physical_to_logical_list.append(join_node.indicator_col_num)
    vzguy__oypd = dft__ufzu + tbd__mqk + ureex__lxz + mhd__tujt
    telmf__egivz = tuple(typemap[jppm__ylggm.name] for jppm__ylggm in
        vzguy__oypd)
    left_other_names = tuple('t1_c' + str(burlk__vfkk) for burlk__vfkk in
        range(len(ureex__lxz)))
    right_other_names = tuple('t2_c' + str(burlk__vfkk) for burlk__vfkk in
        range(len(mhd__tujt)))
    if join_node.is_left_table:
        mkzjf__wdb = ()
    else:
        mkzjf__wdb = tuple('t1_key' + str(burlk__vfkk) for burlk__vfkk in
            range(rjs__voquz))
    if join_node.is_right_table:
        jpf__scknd = ()
    else:
        jpf__scknd = tuple('t2_key' + str(burlk__vfkk) for burlk__vfkk in
            range(rjs__voquz))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}):\n'.format(','.join(mkzjf__wdb + jpf__scknd +
        left_other_names + right_other_names))
    if join_node.is_left_table:
        left_key_types = []
        left_other_types = []
        if join_node.has_live_left_table_var:
            gtej__ghg = typemap[join_node.left_vars[0].name]
        else:
            gtej__ghg = types.none
        for tmw__mjr in left_physical_to_logical_list:
            if tmw__mjr < join_node.n_left_table_cols:
                assert join_node.has_live_left_table_var, 'No logical columns should refer to a dead table'
                nin__ykuf = gtej__ghg.arr_types[tmw__mjr]
            else:
                nin__ykuf = typemap[join_node.left_vars[-1].name]
            if tmw__mjr in join_node.left_key_set:
                left_key_types.append(nin__ykuf)
            else:
                left_other_types.append(nin__ykuf)
        left_key_types = tuple(left_key_types)
        left_other_types = tuple(left_other_types)
    else:
        left_key_types = tuple(typemap[jppm__ylggm.name] for jppm__ylggm in
            dft__ufzu)
        left_other_types = tuple([typemap[khndh__pssza.name] for
            khndh__pssza in ureex__lxz])
    if join_node.is_right_table:
        right_key_types = []
        right_other_types = []
        if join_node.has_live_right_table_var:
            gtej__ghg = typemap[join_node.right_vars[0].name]
        else:
            gtej__ghg = types.none
        for tmw__mjr in right_physical_to_logical_list:
            if tmw__mjr < join_node.n_right_table_cols:
                assert join_node.has_live_right_table_var, 'No logical columns should refer to a dead table'
                nin__ykuf = gtej__ghg.arr_types[tmw__mjr]
            else:
                nin__ykuf = typemap[join_node.right_vars[-1].name]
            if tmw__mjr in join_node.right_key_set:
                right_key_types.append(nin__ykuf)
            else:
                right_other_types.append(nin__ykuf)
        right_key_types = tuple(right_key_types)
        right_other_types = tuple(right_other_types)
    else:
        right_key_types = tuple(typemap[jppm__ylggm.name] for jppm__ylggm in
            tbd__mqk)
        right_other_types = tuple([typemap[khndh__pssza.name] for
            khndh__pssza in mhd__tujt])
    matched_key_types = []
    for burlk__vfkk in range(rjs__voquz):
        mvx__otvnq = _match_join_key_types(left_key_types[burlk__vfkk],
            right_key_types[burlk__vfkk], loc)
        glbs[f'key_type_{burlk__vfkk}'] = mvx__otvnq
        matched_key_types.append(mvx__otvnq)
    if join_node.is_left_table:
        wzygq__bigb = determine_table_cast_map(matched_key_types,
            left_key_types, None, None, True, loc)
        if wzygq__bigb:
            wkwj__rhmfd = False
            cyoew__gzjxe = False
            vfa__nkj = None
            if join_node.has_live_left_table_var:
                bokwb__pmz = list(typemap[join_node.left_vars[0].name].
                    arr_types)
            else:
                bokwb__pmz = None
            for ntxbi__voyyw, nin__ykuf in wzygq__bigb.items():
                if ntxbi__voyyw < join_node.n_left_table_cols:
                    assert join_node.has_live_left_table_var, 'Casting columns for a dead table should not occur'
                    bokwb__pmz[ntxbi__voyyw] = nin__ykuf
                    wkwj__rhmfd = True
                else:
                    vfa__nkj = nin__ykuf
                    cyoew__gzjxe = True
            if wkwj__rhmfd:
                func_text += f"""    {left_other_names[0]} = bodo.utils.table_utils.table_astype({left_other_names[0]}, left_cast_table_type, False, _bodo_nan_to_str=False, used_cols=left_used_cols)
"""
                glbs['left_cast_table_type'] = TableType(tuple(bokwb__pmz))
                glbs['left_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_left_table_cols)) - join_node.
                    left_dead_var_inds)))
            if cyoew__gzjxe:
                func_text += f"""    {left_other_names[1]} = bodo.utils.utils.astype({left_other_names[1]}, left_cast_index_type)
"""
                glbs['left_cast_index_type'] = vfa__nkj
    else:
        func_text += '    t1_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({mkzjf__wdb[burlk__vfkk]}, key_type_{burlk__vfkk})'
             if left_key_types[burlk__vfkk] != matched_key_types[
            burlk__vfkk] else f'{mkzjf__wdb[burlk__vfkk]}' for burlk__vfkk in
            range(rjs__voquz)))
        func_text += '    data_left = ({}{})\n'.format(','.join(
            left_other_names), ',' if len(left_other_names) != 0 else '')
    if join_node.is_right_table:
        wzygq__bigb = determine_table_cast_map(matched_key_types,
            right_key_types, None, None, True, loc)
        if wzygq__bigb:
            wkwj__rhmfd = False
            cyoew__gzjxe = False
            vfa__nkj = None
            if join_node.has_live_right_table_var:
                bokwb__pmz = list(typemap[join_node.right_vars[0].name].
                    arr_types)
            else:
                bokwb__pmz = None
            for ntxbi__voyyw, nin__ykuf in wzygq__bigb.items():
                if ntxbi__voyyw < join_node.n_right_table_cols:
                    assert join_node.has_live_right_table_var, 'Casting columns for a dead table should not occur'
                    bokwb__pmz[ntxbi__voyyw] = nin__ykuf
                    wkwj__rhmfd = True
                else:
                    vfa__nkj = nin__ykuf
                    cyoew__gzjxe = True
            if wkwj__rhmfd:
                func_text += f"""    {right_other_names[0]} = bodo.utils.table_utils.table_astype({right_other_names[0]}, right_cast_table_type, False, _bodo_nan_to_str=False, used_cols=right_used_cols)
"""
                glbs['right_cast_table_type'] = TableType(tuple(bokwb__pmz))
                glbs['right_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_right_table_cols)) - join_node.
                    right_dead_var_inds)))
            if cyoew__gzjxe:
                func_text += f"""    {right_other_names[1]} = bodo.utils.utils.astype({right_other_names[1]}, left_cast_index_type)
"""
                glbs['right_cast_index_type'] = vfa__nkj
    else:
        func_text += '    t2_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({jpf__scknd[burlk__vfkk]}, key_type_{burlk__vfkk})'
             if right_key_types[burlk__vfkk] != matched_key_types[
            burlk__vfkk] else f'{jpf__scknd[burlk__vfkk]}' for burlk__vfkk in
            range(rjs__voquz)))
        func_text += '    data_right = ({}{})\n'.format(','.join(
            right_other_names), ',' if len(right_other_names) != 0 else '')
    general_cond_cfunc, left_col_nums, right_col_nums = (
        _gen_general_cond_cfunc(join_node, typemap,
        left_logical_physical_map, right_logical_physical_map))
    if join_node.how == 'asof':
        if left_parallel or right_parallel:
            assert left_parallel and right_parallel, 'pd.merge_asof requires both left and right to be replicated or distributed'
            func_text += """    t2_keys, data_right = parallel_asof_comm(t1_keys, t2_keys, data_right)
"""
        func_text += """    out_t1_keys, out_t2_keys, out_data_left, out_data_right = bodo.ir.join.local_merge_asof(t1_keys, t2_keys, data_left, data_right)
"""
    else:
        func_text += _gen_local_hash_join(join_node, left_key_types,
            right_key_types, matched_key_types, left_other_names,
            right_other_names, left_other_types, right_other_types,
            left_key_in_output, right_key_in_output, left_parallel,
            right_parallel, glbs, out_physical_to_logical_list,
            out_table_type, index_col_type, join_node.
            get_out_table_used_cols(), left_used_key_nums,
            right_used_key_nums, general_cond_cfunc, left_col_nums,
            right_col_nums, left_physical_to_logical_list,
            right_physical_to_logical_list)
    if join_node.how == 'asof':
        for burlk__vfkk in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(burlk__vfkk
                , burlk__vfkk)
        for burlk__vfkk in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(
                burlk__vfkk, burlk__vfkk)
        for burlk__vfkk in range(rjs__voquz):
            func_text += (
                f'    t1_keys_{burlk__vfkk} = out_t1_keys[{burlk__vfkk}]\n')
        for burlk__vfkk in range(rjs__voquz):
            func_text += (
                f'    t2_keys_{burlk__vfkk} = out_t2_keys[{burlk__vfkk}]\n')
    gmzlv__cnzb = {}
    exec(func_text, {}, gmzlv__cnzb)
    ogll__reswa = gmzlv__cnzb['f']
    glbs.update({'bodo': bodo, 'np': np, 'pd': pd, 'parallel_asof_comm':
        parallel_asof_comm, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'hash_join_table':
        hash_join_table, 'delete_table': delete_table,
        'add_join_gen_cond_cfunc_sym': add_join_gen_cond_cfunc_sym,
        'get_join_cond_addr': get_join_cond_addr, 'key_in_output': np.array
        (left_key_in_output + right_key_in_output, dtype=np.bool_),
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    if general_cond_cfunc:
        glbs.update({'general_cond_cfunc': general_cond_cfunc})
    wbkz__looyw = compile_to_numba_ir(ogll__reswa, glbs, typingctx=
        typingctx, targetctx=targetctx, arg_typs=telmf__egivz, typemap=
        typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(wbkz__looyw, vzguy__oypd)
    impy__rzy = wbkz__looyw.body[:-3]
    if join_node.has_live_out_index_var:
        impy__rzy[-1].target = join_node.out_data_vars[1]
    if join_node.has_live_out_table_var:
        impy__rzy[-2].target = join_node.out_data_vars[0]
    assert join_node.has_live_out_index_var or join_node.has_live_out_table_var, 'At most one of table and index should be dead if the Join IR node is live'
    if not join_node.has_live_out_index_var:
        impy__rzy.pop(-1)
    elif not join_node.has_live_out_table_var:
        impy__rzy.pop(-2)
    return impy__rzy


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap, left_logical_physical_map,
    right_logical_physical_map):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    hkt__xtryp = next_label()
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{hkt__xtryp}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
"""
    func_text += '  if is_null_pointer(left_table):\n'
    func_text += '    return False\n'
    expr, func_text, left_col_nums = _replace_column_accesses(expr,
        left_logical_physical_map, join_node.left_var_map, typemap,
        join_node.left_vars, table_getitem_funcs, func_text, 'left',
        join_node.left_key_set, na_check_name, join_node.is_left_table)
    expr, func_text, right_col_nums = _replace_column_accesses(expr,
        right_logical_physical_map, join_node.right_var_map, typemap,
        join_node.right_vars, table_getitem_funcs, func_text, 'right',
        join_node.right_key_set, na_check_name, join_node.is_right_table)
    func_text += f'  return {expr}'
    gmzlv__cnzb = {}
    exec(func_text, table_getitem_funcs, gmzlv__cnzb)
    pjw__fda = gmzlv__cnzb[f'bodo_join_gen_cond{hkt__xtryp}']
    ukj__fmbps = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    kopi__ctzj = numba.cfunc(ukj__fmbps, nopython=True)(pjw__fda)
    join_gen_cond_cfunc[kopi__ctzj.native_name] = kopi__ctzj
    join_gen_cond_cfunc_addr[kopi__ctzj.native_name] = kopi__ctzj.address
    return kopi__ctzj, left_col_nums, right_col_nums


def _replace_column_accesses(expr, logical_to_physical_ind, name_to_var_map,
    typemap, col_vars, table_getitem_funcs, func_text, table_name, key_set,
    na_check_name, is_table_var):
    bskg__pytum = []
    for khndh__pssza, aiqt__rzs in name_to_var_map.items():
        pxz__bvm = f'({table_name}.{khndh__pssza})'
        if pxz__bvm not in expr:
            continue
        ibj__ppj = f'getitem_{table_name}_val_{aiqt__rzs}'
        smah__dwk = f'_bodo_{table_name}_val_{aiqt__rzs}'
        if is_table_var:
            oej__non = typemap[col_vars[0].name].arr_types[aiqt__rzs]
        else:
            oej__non = typemap[col_vars[aiqt__rzs].name]
        if is_str_arr_type(oej__non):
            func_text += f"""  {smah__dwk}, {smah__dwk}_size = {ibj__ppj}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {smah__dwk} = bodo.libs.str_arr_ext.decode_utf8({smah__dwk}, {smah__dwk}_size)
"""
        else:
            func_text += (
                f'  {smah__dwk} = {ibj__ppj}({table_name}_data1, {table_name}_ind)\n'
                )
        xbyp__ogj = logical_to_physical_ind[aiqt__rzs]
        table_getitem_funcs[ibj__ppj
            ] = bodo.libs.array._gen_row_access_intrinsic(oej__non, xbyp__ogj)
        expr = expr.replace(pxz__bvm, smah__dwk)
        ivh__hrd = f'({na_check_name}.{table_name}.{khndh__pssza})'
        if ivh__hrd in expr:
            cbg__zlfq = f'nacheck_{table_name}_val_{aiqt__rzs}'
            moqno__iuyo = f'_bodo_isna_{table_name}_val_{aiqt__rzs}'
            if (isinstance(oej__non, bodo.libs.int_arr_ext.IntegerArrayType
                ) or oej__non == bodo.libs.bool_arr_ext.boolean_array or
                is_str_arr_type(oej__non)):
                func_text += f"""  {moqno__iuyo} = {cbg__zlfq}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += f"""  {moqno__iuyo} = {cbg__zlfq}({table_name}_data1, {table_name}_ind)
"""
            table_getitem_funcs[cbg__zlfq
                ] = bodo.libs.array._gen_row_na_check_intrinsic(oej__non,
                xbyp__ogj)
            expr = expr.replace(ivh__hrd, moqno__iuyo)
        if aiqt__rzs not in key_set:
            bskg__pytum.append(xbyp__ogj)
    return expr, func_text, bskg__pytum


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as wlxqq__ikcuu:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    hufr__cpmh = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[jppm__ylggm.name] in hufr__cpmh for
        jppm__ylggm in join_node.get_live_left_vars())
    right_parallel = all(array_dists[jppm__ylggm.name] in hufr__cpmh for
        jppm__ylggm in join_node.get_live_right_vars())
    if not left_parallel:
        assert not any(array_dists[jppm__ylggm.name] in hufr__cpmh for
            jppm__ylggm in join_node.get_live_left_vars())
    if not right_parallel:
        assert not any(array_dists[jppm__ylggm.name] in hufr__cpmh for
            jppm__ylggm in join_node.get_live_right_vars())
    if left_parallel or right_parallel:
        assert all(array_dists[jppm__ylggm.name] in hufr__cpmh for
            jppm__ylggm in join_node.get_live_out_vars())
    return left_parallel, right_parallel


def _gen_local_hash_join(join_node, left_key_types, right_key_types,
    matched_key_types, left_other_names, right_other_names,
    left_other_types, right_other_types, left_key_in_output,
    right_key_in_output, left_parallel, right_parallel, glbs,
    out_physical_to_logical_list, out_table_type, index_col_type,
    out_table_used_cols, left_used_key_nums, right_used_key_nums,
    general_cond_cfunc, left_col_nums, right_col_nums,
    left_physical_to_logical_list, right_physical_to_logical_list):

    def needs_typechange(in_type, need_nullable, is_same_key):
        return isinstance(in_type, types.Array) and not is_dtype_nullable(
            in_type.dtype) and need_nullable and not is_same_key
    bsg__cmok = set(left_col_nums)
    aygg__wri = set(right_col_nums)
    xrl__dsvu = join_node.vect_same_key
    xznk__qtbk = []
    for burlk__vfkk in range(len(left_key_types)):
        if left_key_in_output[burlk__vfkk]:
            xznk__qtbk.append(needs_typechange(matched_key_types[
                burlk__vfkk], join_node.is_right, xrl__dsvu[burlk__vfkk]))
    grsr__ogjqu = len(left_key_types)
    nixyd__toeos = 0
    vedh__fuuzf = left_physical_to_logical_list[len(left_key_types):]
    for burlk__vfkk, tmw__mjr in enumerate(vedh__fuuzf):
        hfdkb__keqpc = True
        if tmw__mjr in bsg__cmok:
            hfdkb__keqpc = left_key_in_output[grsr__ogjqu]
            grsr__ogjqu += 1
        if hfdkb__keqpc:
            xznk__qtbk.append(needs_typechange(left_other_types[burlk__vfkk
                ], join_node.is_right, False))
    for burlk__vfkk in range(len(right_key_types)):
        if not xrl__dsvu[burlk__vfkk] and not join_node.is_join:
            if right_key_in_output[nixyd__toeos]:
                xznk__qtbk.append(needs_typechange(matched_key_types[
                    burlk__vfkk], join_node.is_left, False))
            nixyd__toeos += 1
    mauv__vgz = right_physical_to_logical_list[len(right_key_types):]
    for burlk__vfkk, tmw__mjr in enumerate(mauv__vgz):
        hfdkb__keqpc = True
        if tmw__mjr in aygg__wri:
            hfdkb__keqpc = right_key_in_output[nixyd__toeos]
            nixyd__toeos += 1
        if hfdkb__keqpc:
            xznk__qtbk.append(needs_typechange(right_other_types[
                burlk__vfkk], join_node.is_left, False))
    rjs__voquz = len(left_key_types)
    func_text = '    # beginning of _gen_local_hash_join\n'
    if join_node.is_left_table:
        if join_node.has_live_left_table_var:
            dxoxm__oimro = left_other_names[1:]
            gzsr__axjcl = left_other_names[0]
        else:
            dxoxm__oimro = left_other_names
            gzsr__axjcl = None
        ffxo__tvh = '()' if len(dxoxm__oimro) == 0 else f'({dxoxm__oimro[0]},)'
        func_text += f"""    table_left = py_data_to_cpp_table({gzsr__axjcl}, {ffxo__tvh}, left_in_cols, {join_node.n_left_table_cols})
"""
        glbs['left_in_cols'] = MetaType(tuple(left_physical_to_logical_list))
    else:
        jxs__xzm = []
        for burlk__vfkk in range(rjs__voquz):
            jxs__xzm.append('t1_keys[{}]'.format(burlk__vfkk))
        for burlk__vfkk in range(len(left_other_names)):
            jxs__xzm.append('data_left[{}]'.format(burlk__vfkk))
        func_text += '    info_list_total_l = [{}]\n'.format(','.join(
            'array_to_info({})'.format(fox__tjnzd) for fox__tjnzd in jxs__xzm))
        func_text += (
            '    table_left = arr_info_list_to_table(info_list_total_l)\n')
    if join_node.is_right_table:
        if join_node.has_live_right_table_var:
            kqlw__mllug = right_other_names[1:]
            gzsr__axjcl = right_other_names[0]
        else:
            kqlw__mllug = right_other_names
            gzsr__axjcl = None
        ffxo__tvh = '()' if len(kqlw__mllug) == 0 else f'({kqlw__mllug[0]},)'
        func_text += f"""    table_right = py_data_to_cpp_table({gzsr__axjcl}, {ffxo__tvh}, right_in_cols, {join_node.n_right_table_cols})
"""
        glbs['right_in_cols'] = MetaType(tuple(right_physical_to_logical_list))
    else:
        rxr__dqp = []
        for burlk__vfkk in range(rjs__voquz):
            rxr__dqp.append('t2_keys[{}]'.format(burlk__vfkk))
        for burlk__vfkk in range(len(right_other_names)):
            rxr__dqp.append('data_right[{}]'.format(burlk__vfkk))
        func_text += '    info_list_total_r = [{}]\n'.format(','.join(
            'array_to_info({})'.format(fox__tjnzd) for fox__tjnzd in rxr__dqp))
        func_text += (
            '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    glbs['vect_same_key'] = np.array(xrl__dsvu, dtype=np.int64)
    glbs['vect_need_typechange'] = np.array(xznk__qtbk, dtype=np.int64)
    glbs['left_table_cond_columns'] = np.array(left_col_nums if len(
        left_col_nums) > 0 else [-1], dtype=np.int64)
    glbs['right_table_cond_columns'] = np.array(right_col_nums if len(
        right_col_nums) > 0 else [-1], dtype=np.int64)
    if general_cond_cfunc:
        func_text += f"""    cfunc_cond = add_join_gen_cond_cfunc_sym(general_cond_cfunc, '{general_cond_cfunc.native_name}')
"""
        func_text += (
            f"    cfunc_cond = get_join_cond_addr('{general_cond_cfunc.native_name}')\n"
            )
    else:
        func_text += '    cfunc_cond = 0\n'
    func_text += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    func_text += (
        """    out_table = hash_join_table(table_left, table_right, {}, {}, {}, {}, {}, vect_same_key.ctypes, key_in_output.ctypes, vect_need_typechange.ctypes, {}, {}, {}, {}, {}, {}, cfunc_cond, left_table_cond_columns.ctypes, {}, right_table_cond_columns.ctypes, {}, total_rows_np.ctypes)
"""
        .format(left_parallel, right_parallel, rjs__voquz, len(vedh__fuuzf),
        len(mauv__vgz), join_node.is_left, join_node.is_right, join_node.
        is_join, join_node.extra_data_col_num != -1, join_node.
        indicator_col_num != -1, join_node.is_na_equal, len(left_col_nums),
        len(right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    zzqm__epll = '(py_table_type, index_col_type)'
    func_text += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {zzqm__epll}, total_rows_np[0], {join_node.n_out_table_cols})
"""
    if join_node.has_live_out_table_var:
        func_text += f'    T = out_data[0]\n'
    else:
        func_text += f'    T = None\n'
    if join_node.has_live_out_index_var:
        ecw__oyd = 1 if join_node.has_live_out_table_var else 0
        func_text += f'    index_var = out_data[{ecw__oyd}]\n'
    else:
        func_text += f'    index_var = None\n'
    glbs['py_table_type'] = out_table_type
    glbs['index_col_type'] = index_col_type
    glbs['out_col_inds'] = MetaType(tuple(out_physical_to_logical_list))
    if bool(join_node.out_used_cols) or index_col_type != types.none:
        func_text += '    delete_table(out_table)\n'
    if out_table_type != types.none:
        wzygq__bigb = determine_table_cast_map(matched_key_types,
            left_key_types, left_used_key_nums, join_node.
            left_to_output_map, False, join_node.loc)
        wzygq__bigb.update(determine_table_cast_map(matched_key_types,
            right_key_types, right_used_key_nums, join_node.
            right_to_output_map, False, join_node.loc))
        wkwj__rhmfd = False
        cyoew__gzjxe = False
        if join_node.has_live_out_table_var:
            bokwb__pmz = list(out_table_type.arr_types)
        else:
            bokwb__pmz = None
        for ntxbi__voyyw, nin__ykuf in wzygq__bigb.items():
            if ntxbi__voyyw < join_node.n_out_table_cols:
                assert join_node.has_live_out_table_var, 'Casting columns for a dead table should not occur'
                bokwb__pmz[ntxbi__voyyw] = nin__ykuf
                wkwj__rhmfd = True
            else:
                vfa__nkj = nin__ykuf
                cyoew__gzjxe = True
        if wkwj__rhmfd:
            func_text += f"""    T = bodo.utils.table_utils.table_astype(T, cast_table_type, False, _bodo_nan_to_str=False, used_cols=used_cols)
"""
            yjqk__nerb = bodo.TableType(tuple(bokwb__pmz))
            glbs['py_table_type'] = yjqk__nerb
            glbs['cast_table_type'] = out_table_type
            glbs['used_cols'] = MetaType(tuple(out_table_used_cols))
        if cyoew__gzjxe:
            glbs['index_col_type'] = vfa__nkj
            glbs['index_cast_type'] = index_col_type
            func_text += (
                f'    index_var = bodo.utils.utils.astype(index_var, index_cast_type)\n'
                )
    func_text += f'    out_table = T\n'
    func_text += f'    out_index = index_var\n'
    return func_text


def determine_table_cast_map(matched_key_types: List[types.Type], key_types:
    List[types.Type], used_key_nums: Optional[Set[int]], output_map:
    Optional[Dict[int, int]], convert_dict_col: bool, loc: ir.Loc):
    wzygq__bigb: Dict[int, types.Type] = {}
    rjs__voquz = len(matched_key_types)
    for burlk__vfkk in range(rjs__voquz):
        if used_key_nums is None or burlk__vfkk in used_key_nums:
            if matched_key_types[burlk__vfkk] != key_types[burlk__vfkk] and (
                convert_dict_col or key_types[burlk__vfkk] != bodo.
                dict_str_arr_type):
                if output_map:
                    ecw__oyd = output_map[burlk__vfkk]
                else:
                    ecw__oyd = burlk__vfkk
                wzygq__bigb[ecw__oyd] = matched_key_types[burlk__vfkk]
    return wzygq__bigb


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    ikecu__zmnh = bodo.libs.distributed_api.get_size()
    rgjg__cgben = np.empty(ikecu__zmnh, left_key_arrs[0].dtype)
    zxvx__hrxpn = np.empty(ikecu__zmnh, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(rgjg__cgben, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(zxvx__hrxpn, left_key_arrs[0][-1])
    oqkq__ywfj = np.zeros(ikecu__zmnh, np.int32)
    xve__fqs = np.zeros(ikecu__zmnh, np.int32)
    exq__hyww = np.zeros(ikecu__zmnh, np.int32)
    xtfij__vpih = right_key_arrs[0][0]
    bfzq__xaz = right_key_arrs[0][-1]
    hvcbi__uorz = -1
    burlk__vfkk = 0
    while burlk__vfkk < ikecu__zmnh - 1 and zxvx__hrxpn[burlk__vfkk
        ] < xtfij__vpih:
        burlk__vfkk += 1
    while burlk__vfkk < ikecu__zmnh and rgjg__cgben[burlk__vfkk] <= bfzq__xaz:
        hvcbi__uorz, njl__rjd = _count_overlap(right_key_arrs[0],
            rgjg__cgben[burlk__vfkk], zxvx__hrxpn[burlk__vfkk])
        if hvcbi__uorz != 0:
            hvcbi__uorz -= 1
            njl__rjd += 1
        oqkq__ywfj[burlk__vfkk] = njl__rjd
        xve__fqs[burlk__vfkk] = hvcbi__uorz
        burlk__vfkk += 1
    while burlk__vfkk < ikecu__zmnh:
        oqkq__ywfj[burlk__vfkk] = 1
        xve__fqs[burlk__vfkk] = len(right_key_arrs[0]) - 1
        burlk__vfkk += 1
    bodo.libs.distributed_api.alltoall(oqkq__ywfj, exq__hyww, 1)
    wvnr__cnea = exq__hyww.sum()
    idkxr__aacpv = np.empty(wvnr__cnea, right_key_arrs[0].dtype)
    zmbr__crla = alloc_arr_tup(wvnr__cnea, right_data)
    bhp__lksg = bodo.ir.join.calc_disp(exq__hyww)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], idkxr__aacpv,
        oqkq__ywfj, exq__hyww, xve__fqs, bhp__lksg)
    bodo.libs.distributed_api.alltoallv_tup(right_data, zmbr__crla,
        oqkq__ywfj, exq__hyww, xve__fqs, bhp__lksg)
    return (idkxr__aacpv,), zmbr__crla


@numba.njit
def _count_overlap(r_key_arr, start, end):
    njl__rjd = 0
    hvcbi__uorz = 0
    bex__dwqdu = 0
    while bex__dwqdu < len(r_key_arr) and r_key_arr[bex__dwqdu] < start:
        hvcbi__uorz += 1
        bex__dwqdu += 1
    while bex__dwqdu < len(r_key_arr) and start <= r_key_arr[bex__dwqdu
        ] <= end:
        bex__dwqdu += 1
        njl__rjd += 1
    return hvcbi__uorz, njl__rjd


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    govzo__hsu = np.empty_like(arr)
    govzo__hsu[0] = 0
    for burlk__vfkk in range(1, len(arr)):
        govzo__hsu[burlk__vfkk] = govzo__hsu[burlk__vfkk - 1] + arr[
            burlk__vfkk - 1]
    return govzo__hsu


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    vob__fei = len(left_keys[0])
    vke__ohjba = len(right_keys[0])
    grzl__hcl = alloc_arr_tup(vob__fei, left_keys)
    lbjmx__ocf = alloc_arr_tup(vob__fei, right_keys)
    mtd__hiyze = alloc_arr_tup(vob__fei, data_left)
    haum__pvwre = alloc_arr_tup(vob__fei, data_right)
    iluh__hvgio = 0
    abhw__xud = 0
    for iluh__hvgio in range(vob__fei):
        if abhw__xud < 0:
            abhw__xud = 0
        while abhw__xud < vke__ohjba and getitem_arr_tup(right_keys, abhw__xud
            ) <= getitem_arr_tup(left_keys, iluh__hvgio):
            abhw__xud += 1
        abhw__xud -= 1
        setitem_arr_tup(grzl__hcl, iluh__hvgio, getitem_arr_tup(left_keys,
            iluh__hvgio))
        setitem_arr_tup(mtd__hiyze, iluh__hvgio, getitem_arr_tup(data_left,
            iluh__hvgio))
        if abhw__xud >= 0:
            setitem_arr_tup(lbjmx__ocf, iluh__hvgio, getitem_arr_tup(
                right_keys, abhw__xud))
            setitem_arr_tup(haum__pvwre, iluh__hvgio, getitem_arr_tup(
                data_right, abhw__xud))
        else:
            bodo.libs.array_kernels.setna_tup(lbjmx__ocf, iluh__hvgio)
            bodo.libs.array_kernels.setna_tup(haum__pvwre, iluh__hvgio)
    return grzl__hcl, lbjmx__ocf, mtd__hiyze, haum__pvwre
