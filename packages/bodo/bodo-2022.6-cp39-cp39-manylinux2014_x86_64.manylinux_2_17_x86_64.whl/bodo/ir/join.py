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
        elldg__ntei = func.signature
        undhd__rgxcs = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        xqxz__fcdh = cgutils.get_or_insert_function(builder.module,
            undhd__rgxcs, sym._literal_value)
        builder.call(xqxz__fcdh, [context.get_constant_null(elldg__ntei.
            args[0]), context.get_constant_null(elldg__ntei.args[1]),
            context.get_constant_null(elldg__ntei.args[2]), context.
            get_constant_null(elldg__ntei.args[3]), context.
            get_constant_null(elldg__ntei.args[4]), context.
            get_constant_null(elldg__ntei.args[5]), context.get_constant(
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
        vgvhz__jvlyr = left_df_type.columns
        furs__rrr = right_df_type.columns
        self.left_col_names = vgvhz__jvlyr
        self.right_col_names = furs__rrr
        self.is_left_table = left_df_type.is_table_format
        self.is_right_table = right_df_type.is_table_format
        self.n_left_table_cols = len(vgvhz__jvlyr) if self.is_left_table else 0
        self.n_right_table_cols = len(furs__rrr) if self.is_right_table else 0
        pxym__eant = self.n_left_table_cols if self.is_left_table else len(
            left_vars) - 1
        eml__anqq = self.n_right_table_cols if self.is_right_table else len(
            right_vars) - 1
        self.left_dead_var_inds = set()
        self.right_dead_var_inds = set()
        if self.left_vars[-1] is None:
            self.left_dead_var_inds.add(pxym__eant)
        if self.right_vars[-1] is None:
            self.right_dead_var_inds.add(eml__anqq)
        self.left_var_map = {dwd__rpa: xqxfi__luly for xqxfi__luly,
            dwd__rpa in enumerate(vgvhz__jvlyr)}
        self.right_var_map = {dwd__rpa: xqxfi__luly for xqxfi__luly,
            dwd__rpa in enumerate(furs__rrr)}
        if self.left_vars[-1] is not None:
            self.left_var_map[INDEX_SENTINEL] = pxym__eant
        if self.right_vars[-1] is not None:
            self.right_var_map[INDEX_SENTINEL] = eml__anqq
        self.left_key_set = set(self.left_var_map[dwd__rpa] for dwd__rpa in
            left_keys)
        self.right_key_set = set(self.right_var_map[dwd__rpa] for dwd__rpa in
            right_keys)
        if gen_cond_expr:
            self.left_cond_cols = set(self.left_var_map[dwd__rpa] for
                dwd__rpa in vgvhz__jvlyr if f'(left.{dwd__rpa})' in
                gen_cond_expr)
            self.right_cond_cols = set(self.right_var_map[dwd__rpa] for
                dwd__rpa in furs__rrr if f'(right.{dwd__rpa})' in gen_cond_expr
                )
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        ktosu__umvbm: int = -1
        qiibi__rpxem = set(left_keys) & set(right_keys)
        fqqo__mgwl = set(vgvhz__jvlyr) & set(furs__rrr)
        rosi__gqohm = fqqo__mgwl - qiibi__rpxem
        ggig__ajo: Dict[int, (Literal['left', 'right'], int)] = {}
        votq__ufhz: Dict[int, int] = {}
        sswpv__zwv: Dict[int, int] = {}
        for xqxfi__luly, dwd__rpa in enumerate(vgvhz__jvlyr):
            if dwd__rpa in rosi__gqohm:
                bkea__lkmqr = str(dwd__rpa) + suffix_left
                njeh__efodr = out_df_type.column_index[bkea__lkmqr]
                if (right_index and not left_index and xqxfi__luly in self.
                    left_key_set):
                    ktosu__umvbm = out_df_type.column_index[dwd__rpa]
                    ggig__ajo[ktosu__umvbm] = 'left', xqxfi__luly
            else:
                njeh__efodr = out_df_type.column_index[dwd__rpa]
            ggig__ajo[njeh__efodr] = 'left', xqxfi__luly
            votq__ufhz[xqxfi__luly] = njeh__efodr
        for xqxfi__luly, dwd__rpa in enumerate(furs__rrr):
            if dwd__rpa not in qiibi__rpxem:
                if dwd__rpa in rosi__gqohm:
                    eft__thv = str(dwd__rpa) + suffix_right
                    njeh__efodr = out_df_type.column_index[eft__thv]
                    if (left_index and not right_index and xqxfi__luly in
                        self.right_key_set):
                        ktosu__umvbm = out_df_type.column_index[dwd__rpa]
                        ggig__ajo[ktosu__umvbm] = 'right', xqxfi__luly
                else:
                    njeh__efodr = out_df_type.column_index[dwd__rpa]
                ggig__ajo[njeh__efodr] = 'right', xqxfi__luly
                sswpv__zwv[xqxfi__luly] = njeh__efodr
        if self.left_vars[-1] is not None:
            votq__ufhz[pxym__eant] = self.n_out_table_cols
        if self.right_vars[-1] is not None:
            sswpv__zwv[eml__anqq] = self.n_out_table_cols
        self.out_to_input_col_map = ggig__ajo
        self.left_to_output_map = votq__ufhz
        self.right_to_output_map = sswpv__zwv
        self.extra_data_col_num = ktosu__umvbm
        if len(out_data_vars) > 1:
            smkst__cim = 'left' if right_index else 'right'
            if smkst__cim == 'left':
                hul__uzoum = pxym__eant
            elif smkst__cim == 'right':
                hul__uzoum = eml__anqq
        else:
            smkst__cim = None
            hul__uzoum = -1
        self.index_source = smkst__cim
        self.index_col_num = hul__uzoum
        kmisf__you = []
        wwhl__enjo = len(left_keys)
        for uqesq__tjx in range(wwhl__enjo):
            oplym__wwnh = left_keys[uqesq__tjx]
            yedfh__rtipt = right_keys[uqesq__tjx]
            kmisf__you.append(oplym__wwnh == yedfh__rtipt)
        self.vect_same_key = kmisf__you

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
        for qbq__yid in self.left_vars:
            if qbq__yid is not None:
                vars.append(qbq__yid)
        return vars

    def get_live_right_vars(self):
        vars = []
        for qbq__yid in self.right_vars:
            if qbq__yid is not None:
                vars.append(qbq__yid)
        return vars

    def get_live_out_vars(self):
        vars = []
        for qbq__yid in self.out_data_vars:
            if qbq__yid is not None:
                vars.append(qbq__yid)
        return vars

    def set_live_left_vars(self, live_data_vars):
        left_vars = []
        skd__tyyxm = 0
        start = 0
        if self.is_left_table:
            if self.has_live_left_table_var:
                left_vars.append(live_data_vars[skd__tyyxm])
                skd__tyyxm += 1
            else:
                left_vars.append(None)
            start = 1
        lff__llqt = max(self.n_left_table_cols - 1, 0)
        for xqxfi__luly in range(start, len(self.left_vars)):
            if xqxfi__luly + lff__llqt in self.left_dead_var_inds:
                left_vars.append(None)
            else:
                left_vars.append(live_data_vars[skd__tyyxm])
                skd__tyyxm += 1
        self.left_vars = left_vars

    def set_live_right_vars(self, live_data_vars):
        right_vars = []
        skd__tyyxm = 0
        start = 0
        if self.is_right_table:
            if self.has_live_right_table_var:
                right_vars.append(live_data_vars[skd__tyyxm])
                skd__tyyxm += 1
            else:
                right_vars.append(None)
            start = 1
        lff__llqt = max(self.n_right_table_cols - 1, 0)
        for xqxfi__luly in range(start, len(self.right_vars)):
            if xqxfi__luly + lff__llqt in self.right_dead_var_inds:
                right_vars.append(None)
            else:
                right_vars.append(live_data_vars[skd__tyyxm])
                skd__tyyxm += 1
        self.right_vars = right_vars

    def set_live_out_data_vars(self, live_data_vars):
        out_data_vars = []
        befl__ltwdm = [self.has_live_out_table_var, self.has_live_out_index_var
            ]
        skd__tyyxm = 0
        for xqxfi__luly in range(len(self.out_data_vars)):
            if not befl__ltwdm[xqxfi__luly]:
                out_data_vars.append(None)
            else:
                out_data_vars.append(live_data_vars[skd__tyyxm])
                skd__tyyxm += 1
        self.out_data_vars = out_data_vars

    def get_out_table_used_cols(self):
        return {xqxfi__luly for xqxfi__luly in self.out_used_cols if 
            xqxfi__luly < self.n_out_table_cols}

    def __repr__(self):
        evm__uzasi = ', '.join([f'{dwd__rpa}' for dwd__rpa in self.
            left_col_names])
        cydv__jml = f'left={{{evm__uzasi}}}'
        evm__uzasi = ', '.join([f'{dwd__rpa}' for dwd__rpa in self.
            right_col_names])
        agrp__rjj = f'right={{{evm__uzasi}}}'
        return 'join [{}={}]: {}, {}'.format(self.left_keys, self.
            right_keys, cydv__jml, agrp__rjj)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    zbe__hnlad = []
    assert len(join_node.get_live_out_vars()
        ) > 0, 'empty join in array analysis'
    hbtvo__pder = []
    cwda__jpe = join_node.get_live_left_vars()
    for byghl__zosj in cwda__jpe:
        lkx__kvsw = typemap[byghl__zosj.name]
        klc__ses = equiv_set.get_shape(byghl__zosj)
        if klc__ses:
            hbtvo__pder.append(klc__ses[0])
    if len(hbtvo__pder) > 1:
        equiv_set.insert_equiv(*hbtvo__pder)
    hbtvo__pder = []
    cwda__jpe = list(join_node.get_live_right_vars())
    for byghl__zosj in cwda__jpe:
        lkx__kvsw = typemap[byghl__zosj.name]
        klc__ses = equiv_set.get_shape(byghl__zosj)
        if klc__ses:
            hbtvo__pder.append(klc__ses[0])
    if len(hbtvo__pder) > 1:
        equiv_set.insert_equiv(*hbtvo__pder)
    hbtvo__pder = []
    for mpv__htopp in join_node.get_live_out_vars():
        lkx__kvsw = typemap[mpv__htopp.name]
        krvmf__npqm = array_analysis._gen_shape_call(equiv_set, mpv__htopp,
            lkx__kvsw.ndim, None, zbe__hnlad)
        equiv_set.insert_equiv(mpv__htopp, krvmf__npqm)
        hbtvo__pder.append(krvmf__npqm[0])
        equiv_set.define(mpv__htopp, set())
    if len(hbtvo__pder) > 1:
        equiv_set.insert_equiv(*hbtvo__pder)
    return [], zbe__hnlad


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    rkl__fgk = Distribution.OneD
    jhh__nglw = Distribution.OneD
    for byghl__zosj in join_node.get_live_left_vars():
        rkl__fgk = Distribution(min(rkl__fgk.value, array_dists[byghl__zosj
            .name].value))
    for byghl__zosj in join_node.get_live_right_vars():
        jhh__nglw = Distribution(min(jhh__nglw.value, array_dists[
            byghl__zosj.name].value))
    fbqhe__knyc = Distribution.OneD_Var
    for mpv__htopp in join_node.get_live_out_vars():
        if mpv__htopp.name in array_dists:
            fbqhe__knyc = Distribution(min(fbqhe__knyc.value, array_dists[
                mpv__htopp.name].value))
    jyoh__vwuk = Distribution(min(fbqhe__knyc.value, rkl__fgk.value))
    xnbkp__gmrv = Distribution(min(fbqhe__knyc.value, jhh__nglw.value))
    fbqhe__knyc = Distribution(max(jyoh__vwuk.value, xnbkp__gmrv.value))
    for mpv__htopp in join_node.get_live_out_vars():
        array_dists[mpv__htopp.name] = fbqhe__knyc
    if fbqhe__knyc != Distribution.OneD_Var:
        rkl__fgk = fbqhe__knyc
        jhh__nglw = fbqhe__knyc
    for byghl__zosj in join_node.get_live_left_vars():
        array_dists[byghl__zosj.name] = rkl__fgk
    for byghl__zosj in join_node.get_live_right_vars():
        array_dists[byghl__zosj.name] = jhh__nglw
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def visit_vars_join(join_node, callback, cbdata):
    join_node.set_live_left_vars([visit_vars_inner(qbq__yid, callback,
        cbdata) for qbq__yid in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([visit_vars_inner(qbq__yid, callback,
        cbdata) for qbq__yid in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([visit_vars_inner(qbq__yid, callback,
        cbdata) for qbq__yid in join_node.get_live_out_vars()])


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if join_node.has_live_out_table_var:
        lxsa__fzau = []
        yilm__vqprx = join_node.get_out_table_var()
        if yilm__vqprx.name not in lives:
            join_node.out_data_vars[0] = None
            join_node.out_used_cols.difference_update(join_node.
                get_out_table_used_cols())
        for rkue__kpbr in join_node.out_to_input_col_map.keys():
            if rkue__kpbr in join_node.out_used_cols:
                continue
            lxsa__fzau.append(rkue__kpbr)
            if join_node.indicator_col_num == rkue__kpbr:
                join_node.indicator_col_num = -1
                continue
            if rkue__kpbr == join_node.extra_data_col_num:
                join_node.extra_data_col_num = -1
                continue
            dvqe__uvvxv, rkue__kpbr = join_node.out_to_input_col_map[rkue__kpbr
                ]
            if dvqe__uvvxv == 'left':
                if (rkue__kpbr not in join_node.left_key_set and rkue__kpbr
                     not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(rkue__kpbr)
                    if not join_node.is_left_table:
                        join_node.left_vars[rkue__kpbr] = None
            elif dvqe__uvvxv == 'right':
                if (rkue__kpbr not in join_node.right_key_set and 
                    rkue__kpbr not in join_node.right_cond_cols):
                    join_node.right_dead_var_inds.add(rkue__kpbr)
                    if not join_node.is_right_table:
                        join_node.right_vars[rkue__kpbr] = None
        for xqxfi__luly in lxsa__fzau:
            del join_node.out_to_input_col_map[xqxfi__luly]
        if join_node.is_left_table:
            ndlp__wyjl = set(range(join_node.n_left_table_cols))
            mzv__xocu = not bool(ndlp__wyjl - join_node.left_dead_var_inds)
            if mzv__xocu:
                join_node.left_vars[0] = None
        if join_node.is_right_table:
            ndlp__wyjl = set(range(join_node.n_right_table_cols))
            mzv__xocu = not bool(ndlp__wyjl - join_node.right_dead_var_inds)
            if mzv__xocu:
                join_node.right_vars[0] = None
    if join_node.has_live_out_index_var:
        uhpon__iso = join_node.get_out_index_var()
        if uhpon__iso.name not in lives:
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
    olpx__lcsjm = False
    if join_node.has_live_out_table_var:
        hgah__yhow = join_node.get_out_table_var().name
        tgx__neh, rwx__fxg, ptqd__ptgv = get_live_column_nums_block(
            column_live_map, equiv_vars, hgah__yhow)
        if not (rwx__fxg or ptqd__ptgv):
            tgx__neh = trim_extra_used_columns(tgx__neh, join_node.
                n_out_table_cols)
            niwau__xgvf = join_node.get_out_table_used_cols()
            if len(tgx__neh) != len(niwau__xgvf):
                olpx__lcsjm = not (join_node.is_left_table and join_node.
                    is_right_table)
                kgfs__wet = niwau__xgvf - tgx__neh
                join_node.out_used_cols = join_node.out_used_cols - kgfs__wet
    return olpx__lcsjm


remove_dead_column_extensions[Join] = join_remove_dead_column


def join_table_column_use(join_node: Join, block_use_map: Dict[str, Tuple[
    Set[int], bool, bool]], equiv_vars: Dict[str, Set[str]], typemap: Dict[
    str, types.Type], table_col_use_map: Dict[int, Dict[str, Tuple[Set[int],
    bool, bool]]]):
    if not (join_node.is_left_table or join_node.is_right_table):
        return
    if join_node.has_live_out_table_var:
        jdykm__zia = join_node.get_out_table_var()
        ghj__cpri, rwx__fxg, ptqd__ptgv = _compute_table_column_uses(jdykm__zia
            .name, table_col_use_map, equiv_vars)
    else:
        ghj__cpri, rwx__fxg, ptqd__ptgv = set(), False, False
    if join_node.has_live_left_table_var:
        ebyeb__enxr = join_node.left_vars[0].name
        zomg__cbe, mjsjf__lwfm, akemj__xknh = block_use_map[ebyeb__enxr]
        if not (mjsjf__lwfm or akemj__xknh):
            glttw__xfehw = set([join_node.out_to_input_col_map[xqxfi__luly]
                [1] for xqxfi__luly in ghj__cpri if join_node.
                out_to_input_col_map[xqxfi__luly][0] == 'left'])
            akq__ovx = set(xqxfi__luly for xqxfi__luly in join_node.
                left_key_set | join_node.left_cond_cols if xqxfi__luly <
                join_node.n_left_table_cols)
            if not (rwx__fxg or ptqd__ptgv):
                join_node.left_dead_var_inds |= set(range(join_node.
                    n_left_table_cols)) - (glttw__xfehw | akq__ovx)
            block_use_map[ebyeb__enxr] = (zomg__cbe | glttw__xfehw |
                akq__ovx, rwx__fxg or ptqd__ptgv, False)
    if join_node.has_live_right_table_var:
        odg__kumh = join_node.right_vars[0].name
        zomg__cbe, mjsjf__lwfm, akemj__xknh = block_use_map[odg__kumh]
        if not (mjsjf__lwfm or akemj__xknh):
            hfu__bbe = set([join_node.out_to_input_col_map[xqxfi__luly][1] for
                xqxfi__luly in ghj__cpri if join_node.out_to_input_col_map[
                xqxfi__luly][0] == 'right'])
            kuw__wlmf = set(xqxfi__luly for xqxfi__luly in join_node.
                right_key_set | join_node.right_cond_cols if xqxfi__luly <
                join_node.n_right_table_cols)
            if not (rwx__fxg or ptqd__ptgv):
                join_node.right_dead_var_inds |= set(range(join_node.
                    n_right_table_cols)) - (hfu__bbe | kuw__wlmf)
            block_use_map[odg__kumh
                ] = zomg__cbe | hfu__bbe | kuw__wlmf, rwx__fxg or ptqd__ptgv, False


ir_extension_table_column_use[Join] = join_table_column_use


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({gux__gwn.name for gux__gwn in join_node.
        get_live_left_vars()})
    use_set.update({gux__gwn.name for gux__gwn in join_node.
        get_live_right_vars()})
    def_set.update({gux__gwn.name for gux__gwn in join_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    atrd__lyl = set(gux__gwn.name for gux__gwn in join_node.get_live_out_vars()
        )
    return set(), atrd__lyl


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    join_node.set_live_left_vars([replace_vars_inner(qbq__yid, var_dict) for
        qbq__yid in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([replace_vars_inner(qbq__yid, var_dict) for
        qbq__yid in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([replace_vars_inner(qbq__yid, var_dict
        ) for qbq__yid in join_node.get_live_out_vars()])


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for byghl__zosj in join_node.get_live_out_vars():
        definitions[byghl__zosj.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 2:
        ruye__dtfy = join_node.loc.strformat()
        ksygw__bbhxq = [join_node.left_col_names[xqxfi__luly] for
            xqxfi__luly in sorted(set(range(len(join_node.left_col_names))) -
            join_node.left_dead_var_inds)]
        qcjz__wux = """Finished column elimination on join's left input:
%s
Left input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', qcjz__wux,
            ruye__dtfy, ksygw__bbhxq)
        smz__mas = [join_node.right_col_names[xqxfi__luly] for xqxfi__luly in
            sorted(set(range(len(join_node.right_col_names))) - join_node.
            right_dead_var_inds)]
        qcjz__wux = """Finished column elimination on join's right input:
%s
Right input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', qcjz__wux,
            ruye__dtfy, smz__mas)
        rvqlj__kejef = [join_node.out_col_names[xqxfi__luly] for
            xqxfi__luly in sorted(join_node.get_out_table_used_cols())]
        qcjz__wux = (
            'Finished column pruning on join node:\n%s\nOutput columns: %s\n')
        bodo.user_logging.log_message('Column Pruning', qcjz__wux,
            ruye__dtfy, rvqlj__kejef)
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    wwhl__enjo = len(join_node.left_keys)
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
    ltplr__jssvk = 0
    pgrwo__eykz = 0
    kkfq__xdg = []
    for dwd__rpa in join_node.left_keys:
        ovw__dzfo = join_node.left_var_map[dwd__rpa]
        if not join_node.is_left_table:
            kkfq__xdg.append(join_node.left_vars[ovw__dzfo])
        befl__ltwdm = 1
        njeh__efodr = join_node.left_to_output_map[ovw__dzfo]
        if dwd__rpa == INDEX_SENTINEL:
            if (join_node.has_live_out_index_var and join_node.index_source ==
                'left' and join_node.index_col_num == ovw__dzfo):
                out_physical_to_logical_list.append(njeh__efodr)
                left_used_key_nums.add(ovw__dzfo)
            else:
                befl__ltwdm = 0
        elif njeh__efodr not in join_node.out_used_cols:
            befl__ltwdm = 0
        elif ovw__dzfo in left_used_key_nums:
            befl__ltwdm = 0
        else:
            left_used_key_nums.add(ovw__dzfo)
            out_physical_to_logical_list.append(njeh__efodr)
        left_physical_to_logical_list.append(ovw__dzfo)
        left_logical_physical_map[ovw__dzfo] = ltplr__jssvk
        ltplr__jssvk += 1
        left_key_in_output.append(befl__ltwdm)
    kkfq__xdg = tuple(kkfq__xdg)
    gby__kxv = []
    for xqxfi__luly in range(len(join_node.left_col_names)):
        if (xqxfi__luly not in join_node.left_dead_var_inds and xqxfi__luly
             not in join_node.left_key_set):
            if not join_node.is_left_table:
                gux__gwn = join_node.left_vars[xqxfi__luly]
                gby__kxv.append(gux__gwn)
            mvm__cjjuk = 1
            sqe__uis = 1
            njeh__efodr = join_node.left_to_output_map[xqxfi__luly]
            if xqxfi__luly in join_node.left_cond_cols:
                if njeh__efodr not in join_node.out_used_cols:
                    mvm__cjjuk = 0
                left_key_in_output.append(mvm__cjjuk)
            elif xqxfi__luly in join_node.left_dead_var_inds:
                mvm__cjjuk = 0
                sqe__uis = 0
            if mvm__cjjuk:
                out_physical_to_logical_list.append(njeh__efodr)
            if sqe__uis:
                left_physical_to_logical_list.append(xqxfi__luly)
                left_logical_physical_map[xqxfi__luly] = ltplr__jssvk
                ltplr__jssvk += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'left' and join_node.index_col_num not in join_node.left_key_set):
        if not join_node.is_left_table:
            gby__kxv.append(join_node.left_vars[join_node.index_col_num])
        njeh__efodr = join_node.left_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(njeh__efodr)
        left_physical_to_logical_list.append(join_node.index_col_num)
    gby__kxv = tuple(gby__kxv)
    if join_node.is_left_table:
        gby__kxv = tuple(join_node.get_live_left_vars())
    kpg__rqn = []
    for xqxfi__luly, dwd__rpa in enumerate(join_node.right_keys):
        ovw__dzfo = join_node.right_var_map[dwd__rpa]
        if not join_node.is_right_table:
            kpg__rqn.append(join_node.right_vars[ovw__dzfo])
        if not join_node.vect_same_key[xqxfi__luly] and not join_node.is_join:
            befl__ltwdm = 1
            if ovw__dzfo not in join_node.right_to_output_map:
                befl__ltwdm = 0
            else:
                njeh__efodr = join_node.right_to_output_map[ovw__dzfo]
                if dwd__rpa == INDEX_SENTINEL:
                    if (join_node.has_live_out_index_var and join_node.
                        index_source == 'right' and join_node.index_col_num ==
                        ovw__dzfo):
                        out_physical_to_logical_list.append(njeh__efodr)
                        right_used_key_nums.add(ovw__dzfo)
                    else:
                        befl__ltwdm = 0
                elif njeh__efodr not in join_node.out_used_cols:
                    befl__ltwdm = 0
                elif ovw__dzfo in right_used_key_nums:
                    befl__ltwdm = 0
                else:
                    right_used_key_nums.add(ovw__dzfo)
                    out_physical_to_logical_list.append(njeh__efodr)
            right_key_in_output.append(befl__ltwdm)
        right_physical_to_logical_list.append(ovw__dzfo)
        right_logical_physical_map[ovw__dzfo] = pgrwo__eykz
        pgrwo__eykz += 1
    kpg__rqn = tuple(kpg__rqn)
    ftccc__auze = []
    for xqxfi__luly in range(len(join_node.right_col_names)):
        if (xqxfi__luly not in join_node.right_dead_var_inds and 
            xqxfi__luly not in join_node.right_key_set):
            if not join_node.is_right_table:
                ftccc__auze.append(join_node.right_vars[xqxfi__luly])
            mvm__cjjuk = 1
            sqe__uis = 1
            njeh__efodr = join_node.right_to_output_map[xqxfi__luly]
            if xqxfi__luly in join_node.right_cond_cols:
                if njeh__efodr not in join_node.out_used_cols:
                    mvm__cjjuk = 0
                right_key_in_output.append(mvm__cjjuk)
            elif xqxfi__luly in join_node.right_dead_var_inds:
                mvm__cjjuk = 0
                sqe__uis = 0
            if mvm__cjjuk:
                out_physical_to_logical_list.append(njeh__efodr)
            if sqe__uis:
                right_physical_to_logical_list.append(xqxfi__luly)
                right_logical_physical_map[xqxfi__luly] = pgrwo__eykz
                pgrwo__eykz += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'right' and join_node.index_col_num not in join_node.right_key_set):
        if not join_node.is_right_table:
            ftccc__auze.append(join_node.right_vars[join_node.index_col_num])
        njeh__efodr = join_node.right_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(njeh__efodr)
        right_physical_to_logical_list.append(join_node.index_col_num)
    ftccc__auze = tuple(ftccc__auze)
    if join_node.is_right_table:
        ftccc__auze = tuple(join_node.get_live_right_vars())
    if join_node.indicator_col_num != -1:
        out_physical_to_logical_list.append(join_node.indicator_col_num)
    zqvo__dubwd = kkfq__xdg + kpg__rqn + gby__kxv + ftccc__auze
    efvc__tzttb = tuple(typemap[gux__gwn.name] for gux__gwn in zqvo__dubwd)
    left_other_names = tuple('t1_c' + str(xqxfi__luly) for xqxfi__luly in
        range(len(gby__kxv)))
    right_other_names = tuple('t2_c' + str(xqxfi__luly) for xqxfi__luly in
        range(len(ftccc__auze)))
    if join_node.is_left_table:
        tbnp__pgiz = ()
    else:
        tbnp__pgiz = tuple('t1_key' + str(xqxfi__luly) for xqxfi__luly in
            range(wwhl__enjo))
    if join_node.is_right_table:
        ohk__rjcw = ()
    else:
        ohk__rjcw = tuple('t2_key' + str(xqxfi__luly) for xqxfi__luly in
            range(wwhl__enjo))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}):\n'.format(','.join(tbnp__pgiz + ohk__rjcw +
        left_other_names + right_other_names))
    if join_node.is_left_table:
        left_key_types = []
        left_other_types = []
        if join_node.has_live_left_table_var:
            ogrw__hzndu = typemap[join_node.left_vars[0].name]
        else:
            ogrw__hzndu = types.none
        for epmi__jywq in left_physical_to_logical_list:
            if epmi__jywq < join_node.n_left_table_cols:
                assert join_node.has_live_left_table_var, 'No logical columns should refer to a dead table'
                lkx__kvsw = ogrw__hzndu.arr_types[epmi__jywq]
            else:
                lkx__kvsw = typemap[join_node.left_vars[-1].name]
            if epmi__jywq in join_node.left_key_set:
                left_key_types.append(lkx__kvsw)
            else:
                left_other_types.append(lkx__kvsw)
        left_key_types = tuple(left_key_types)
        left_other_types = tuple(left_other_types)
    else:
        left_key_types = tuple(typemap[gux__gwn.name] for gux__gwn in kkfq__xdg
            )
        left_other_types = tuple([typemap[dwd__rpa.name] for dwd__rpa in
            gby__kxv])
    if join_node.is_right_table:
        right_key_types = []
        right_other_types = []
        if join_node.has_live_right_table_var:
            ogrw__hzndu = typemap[join_node.right_vars[0].name]
        else:
            ogrw__hzndu = types.none
        for epmi__jywq in right_physical_to_logical_list:
            if epmi__jywq < join_node.n_right_table_cols:
                assert join_node.has_live_right_table_var, 'No logical columns should refer to a dead table'
                lkx__kvsw = ogrw__hzndu.arr_types[epmi__jywq]
            else:
                lkx__kvsw = typemap[join_node.right_vars[-1].name]
            if epmi__jywq in join_node.right_key_set:
                right_key_types.append(lkx__kvsw)
            else:
                right_other_types.append(lkx__kvsw)
        right_key_types = tuple(right_key_types)
        right_other_types = tuple(right_other_types)
    else:
        right_key_types = tuple(typemap[gux__gwn.name] for gux__gwn in kpg__rqn
            )
        right_other_types = tuple([typemap[dwd__rpa.name] for dwd__rpa in
            ftccc__auze])
    matched_key_types = []
    for xqxfi__luly in range(wwhl__enjo):
        gsag__dyak = _match_join_key_types(left_key_types[xqxfi__luly],
            right_key_types[xqxfi__luly], loc)
        glbs[f'key_type_{xqxfi__luly}'] = gsag__dyak
        matched_key_types.append(gsag__dyak)
    if join_node.is_left_table:
        xnn__owtao = determine_table_cast_map(matched_key_types,
            left_key_types, None, None, True, loc)
        if xnn__owtao:
            dfe__lylgv = False
            gnmy__pujkr = False
            jwco__szfv = None
            if join_node.has_live_left_table_var:
                wsbj__dmtm = list(typemap[join_node.left_vars[0].name].
                    arr_types)
            else:
                wsbj__dmtm = None
            for rkue__kpbr, lkx__kvsw in xnn__owtao.items():
                if rkue__kpbr < join_node.n_left_table_cols:
                    assert join_node.has_live_left_table_var, 'Casting columns for a dead table should not occur'
                    wsbj__dmtm[rkue__kpbr] = lkx__kvsw
                    dfe__lylgv = True
                else:
                    jwco__szfv = lkx__kvsw
                    gnmy__pujkr = True
            if dfe__lylgv:
                func_text += f"""    {left_other_names[0]} = bodo.utils.table_utils.table_astype({left_other_names[0]}, left_cast_table_type, False, _bodo_nan_to_str=False, used_cols=left_used_cols)
"""
                glbs['left_cast_table_type'] = TableType(tuple(wsbj__dmtm))
                glbs['left_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_left_table_cols)) - join_node.
                    left_dead_var_inds)))
            if gnmy__pujkr:
                func_text += f"""    {left_other_names[1]} = bodo.utils.utils.astype({left_other_names[1]}, left_cast_index_type)
"""
                glbs['left_cast_index_type'] = jwco__szfv
    else:
        func_text += '    t1_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({tbnp__pgiz[xqxfi__luly]}, key_type_{xqxfi__luly})'
             if left_key_types[xqxfi__luly] != matched_key_types[
            xqxfi__luly] else f'{tbnp__pgiz[xqxfi__luly]}' for xqxfi__luly in
            range(wwhl__enjo)))
        func_text += '    data_left = ({}{})\n'.format(','.join(
            left_other_names), ',' if len(left_other_names) != 0 else '')
    if join_node.is_right_table:
        xnn__owtao = determine_table_cast_map(matched_key_types,
            right_key_types, None, None, True, loc)
        if xnn__owtao:
            dfe__lylgv = False
            gnmy__pujkr = False
            jwco__szfv = None
            if join_node.has_live_right_table_var:
                wsbj__dmtm = list(typemap[join_node.right_vars[0].name].
                    arr_types)
            else:
                wsbj__dmtm = None
            for rkue__kpbr, lkx__kvsw in xnn__owtao.items():
                if rkue__kpbr < join_node.n_right_table_cols:
                    assert join_node.has_live_right_table_var, 'Casting columns for a dead table should not occur'
                    wsbj__dmtm[rkue__kpbr] = lkx__kvsw
                    dfe__lylgv = True
                else:
                    jwco__szfv = lkx__kvsw
                    gnmy__pujkr = True
            if dfe__lylgv:
                func_text += f"""    {right_other_names[0]} = bodo.utils.table_utils.table_astype({right_other_names[0]}, right_cast_table_type, False, _bodo_nan_to_str=False, used_cols=right_used_cols)
"""
                glbs['right_cast_table_type'] = TableType(tuple(wsbj__dmtm))
                glbs['right_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_right_table_cols)) - join_node.
                    right_dead_var_inds)))
            if gnmy__pujkr:
                func_text += f"""    {right_other_names[1]} = bodo.utils.utils.astype({right_other_names[1]}, left_cast_index_type)
"""
                glbs['right_cast_index_type'] = jwco__szfv
    else:
        func_text += '    t2_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({ohk__rjcw[xqxfi__luly]}, key_type_{xqxfi__luly})'
             if right_key_types[xqxfi__luly] != matched_key_types[
            xqxfi__luly] else f'{ohk__rjcw[xqxfi__luly]}' for xqxfi__luly in
            range(wwhl__enjo)))
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
        for xqxfi__luly in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(xqxfi__luly
                , xqxfi__luly)
        for xqxfi__luly in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(
                xqxfi__luly, xqxfi__luly)
        for xqxfi__luly in range(wwhl__enjo):
            func_text += (
                f'    t1_keys_{xqxfi__luly} = out_t1_keys[{xqxfi__luly}]\n')
        for xqxfi__luly in range(wwhl__enjo):
            func_text += (
                f'    t2_keys_{xqxfi__luly} = out_t2_keys[{xqxfi__luly}]\n')
    atbdf__dhj = {}
    exec(func_text, {}, atbdf__dhj)
    htus__ofh = atbdf__dhj['f']
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
    asol__iebhf = compile_to_numba_ir(htus__ofh, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=efvc__tzttb, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(asol__iebhf, zqvo__dubwd)
    kdgom__uiqgd = asol__iebhf.body[:-3]
    if join_node.has_live_out_index_var:
        kdgom__uiqgd[-1].target = join_node.out_data_vars[1]
    if join_node.has_live_out_table_var:
        kdgom__uiqgd[-2].target = join_node.out_data_vars[0]
    assert join_node.has_live_out_index_var or join_node.has_live_out_table_var, 'At most one of table and index should be dead if the Join IR node is live'
    if not join_node.has_live_out_index_var:
        kdgom__uiqgd.pop(-1)
    elif not join_node.has_live_out_table_var:
        kdgom__uiqgd.pop(-2)
    return kdgom__uiqgd


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap, left_logical_physical_map,
    right_logical_physical_map):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    vrzo__lou = next_label()
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{vrzo__lou}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
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
    atbdf__dhj = {}
    exec(func_text, table_getitem_funcs, atbdf__dhj)
    xqfm__lkdx = atbdf__dhj[f'bodo_join_gen_cond{vrzo__lou}']
    jzmu__ysr = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    nltgn__xceb = numba.cfunc(jzmu__ysr, nopython=True)(xqfm__lkdx)
    join_gen_cond_cfunc[nltgn__xceb.native_name] = nltgn__xceb
    join_gen_cond_cfunc_addr[nltgn__xceb.native_name] = nltgn__xceb.address
    return nltgn__xceb, left_col_nums, right_col_nums


def _replace_column_accesses(expr, logical_to_physical_ind, name_to_var_map,
    typemap, col_vars, table_getitem_funcs, func_text, table_name, key_set,
    na_check_name, is_table_var):
    key__hlttb = []
    for dwd__rpa, mwysy__qtjqy in name_to_var_map.items():
        lzgf__mwg = f'({table_name}.{dwd__rpa})'
        if lzgf__mwg not in expr:
            continue
        bjae__bipp = f'getitem_{table_name}_val_{mwysy__qtjqy}'
        gzgs__djyoy = f'_bodo_{table_name}_val_{mwysy__qtjqy}'
        if is_table_var:
            mjmz__whpu = typemap[col_vars[0].name].arr_types[mwysy__qtjqy]
        else:
            mjmz__whpu = typemap[col_vars[mwysy__qtjqy].name]
        if is_str_arr_type(mjmz__whpu):
            func_text += f"""  {gzgs__djyoy}, {gzgs__djyoy}_size = {bjae__bipp}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {gzgs__djyoy} = bodo.libs.str_arr_ext.decode_utf8({gzgs__djyoy}, {gzgs__djyoy}_size)
"""
        else:
            func_text += (
                f'  {gzgs__djyoy} = {bjae__bipp}({table_name}_data1, {table_name}_ind)\n'
                )
        hjuru__kntz = logical_to_physical_ind[mwysy__qtjqy]
        table_getitem_funcs[bjae__bipp
            ] = bodo.libs.array._gen_row_access_intrinsic(mjmz__whpu,
            hjuru__kntz)
        expr = expr.replace(lzgf__mwg, gzgs__djyoy)
        hqpos__avbec = f'({na_check_name}.{table_name}.{dwd__rpa})'
        if hqpos__avbec in expr:
            upnfr__mdqh = f'nacheck_{table_name}_val_{mwysy__qtjqy}'
            uth__drmwe = f'_bodo_isna_{table_name}_val_{mwysy__qtjqy}'
            if (isinstance(mjmz__whpu, bodo.libs.int_arr_ext.
                IntegerArrayType) or mjmz__whpu == bodo.libs.bool_arr_ext.
                boolean_array or is_str_arr_type(mjmz__whpu)):
                func_text += f"""  {uth__drmwe} = {upnfr__mdqh}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += f"""  {uth__drmwe} = {upnfr__mdqh}({table_name}_data1, {table_name}_ind)
"""
            table_getitem_funcs[upnfr__mdqh
                ] = bodo.libs.array._gen_row_na_check_intrinsic(mjmz__whpu,
                hjuru__kntz)
            expr = expr.replace(hqpos__avbec, uth__drmwe)
        if mwysy__qtjqy not in key_set:
            key__hlttb.append(hjuru__kntz)
    return expr, func_text, key__hlttb


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as ctag__xzlo:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    shxt__hghbz = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[gux__gwn.name] in shxt__hghbz for
        gux__gwn in join_node.get_live_left_vars())
    right_parallel = all(array_dists[gux__gwn.name] in shxt__hghbz for
        gux__gwn in join_node.get_live_right_vars())
    if not left_parallel:
        assert not any(array_dists[gux__gwn.name] in shxt__hghbz for
            gux__gwn in join_node.get_live_left_vars())
    if not right_parallel:
        assert not any(array_dists[gux__gwn.name] in shxt__hghbz for
            gux__gwn in join_node.get_live_right_vars())
    if left_parallel or right_parallel:
        assert all(array_dists[gux__gwn.name] in shxt__hghbz for gux__gwn in
            join_node.get_live_out_vars())
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
    nzhrd__oywfy = set(left_col_nums)
    qjji__kjh = set(right_col_nums)
    kmisf__you = join_node.vect_same_key
    vnss__bsszo = []
    for xqxfi__luly in range(len(left_key_types)):
        if left_key_in_output[xqxfi__luly]:
            vnss__bsszo.append(needs_typechange(matched_key_types[
                xqxfi__luly], join_node.is_right, kmisf__you[xqxfi__luly]))
    ugdjh__zlhym = len(left_key_types)
    zlrvn__abl = 0
    mlp__jqj = left_physical_to_logical_list[len(left_key_types):]
    for xqxfi__luly, epmi__jywq in enumerate(mlp__jqj):
        ltpeg__fpu = True
        if epmi__jywq in nzhrd__oywfy:
            ltpeg__fpu = left_key_in_output[ugdjh__zlhym]
            ugdjh__zlhym += 1
        if ltpeg__fpu:
            vnss__bsszo.append(needs_typechange(left_other_types[
                xqxfi__luly], join_node.is_right, False))
    for xqxfi__luly in range(len(right_key_types)):
        if not kmisf__you[xqxfi__luly] and not join_node.is_join:
            if right_key_in_output[zlrvn__abl]:
                vnss__bsszo.append(needs_typechange(matched_key_types[
                    xqxfi__luly], join_node.is_left, False))
            zlrvn__abl += 1
    djo__dnil = right_physical_to_logical_list[len(right_key_types):]
    for xqxfi__luly, epmi__jywq in enumerate(djo__dnil):
        ltpeg__fpu = True
        if epmi__jywq in qjji__kjh:
            ltpeg__fpu = right_key_in_output[zlrvn__abl]
            zlrvn__abl += 1
        if ltpeg__fpu:
            vnss__bsszo.append(needs_typechange(right_other_types[
                xqxfi__luly], join_node.is_left, False))
    wwhl__enjo = len(left_key_types)
    func_text = '    # beginning of _gen_local_hash_join\n'
    if join_node.is_left_table:
        if join_node.has_live_left_table_var:
            mryzi__xyt = left_other_names[1:]
            yilm__vqprx = left_other_names[0]
        else:
            mryzi__xyt = left_other_names
            yilm__vqprx = None
        arbm__deggv = '()' if len(mryzi__xyt) == 0 else f'({mryzi__xyt[0]},)'
        func_text += f"""    table_left = py_data_to_cpp_table({yilm__vqprx}, {arbm__deggv}, left_in_cols, {join_node.n_left_table_cols})
"""
        glbs['left_in_cols'] = MetaType(tuple(left_physical_to_logical_list))
    else:
        mcxw__lpr = []
        for xqxfi__luly in range(wwhl__enjo):
            mcxw__lpr.append('t1_keys[{}]'.format(xqxfi__luly))
        for xqxfi__luly in range(len(left_other_names)):
            mcxw__lpr.append('data_left[{}]'.format(xqxfi__luly))
        func_text += '    info_list_total_l = [{}]\n'.format(','.join(
            'array_to_info({})'.format(wqfj__ssru) for wqfj__ssru in mcxw__lpr)
            )
        func_text += (
            '    table_left = arr_info_list_to_table(info_list_total_l)\n')
    if join_node.is_right_table:
        if join_node.has_live_right_table_var:
            nei__cwezm = right_other_names[1:]
            yilm__vqprx = right_other_names[0]
        else:
            nei__cwezm = right_other_names
            yilm__vqprx = None
        arbm__deggv = '()' if len(nei__cwezm) == 0 else f'({nei__cwezm[0]},)'
        func_text += f"""    table_right = py_data_to_cpp_table({yilm__vqprx}, {arbm__deggv}, right_in_cols, {join_node.n_right_table_cols})
"""
        glbs['right_in_cols'] = MetaType(tuple(right_physical_to_logical_list))
    else:
        vewu__mmtu = []
        for xqxfi__luly in range(wwhl__enjo):
            vewu__mmtu.append('t2_keys[{}]'.format(xqxfi__luly))
        for xqxfi__luly in range(len(right_other_names)):
            vewu__mmtu.append('data_right[{}]'.format(xqxfi__luly))
        func_text += '    info_list_total_r = [{}]\n'.format(','.join(
            'array_to_info({})'.format(wqfj__ssru) for wqfj__ssru in
            vewu__mmtu))
        func_text += (
            '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    glbs['vect_same_key'] = np.array(kmisf__you, dtype=np.int64)
    glbs['vect_need_typechange'] = np.array(vnss__bsszo, dtype=np.int64)
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
        .format(left_parallel, right_parallel, wwhl__enjo, len(mlp__jqj),
        len(djo__dnil), join_node.is_left, join_node.is_right, join_node.
        is_join, join_node.extra_data_col_num != -1, join_node.
        indicator_col_num != -1, join_node.is_na_equal, len(left_col_nums),
        len(right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    xxbkt__eyyd = '(py_table_type, index_col_type)'
    func_text += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {xxbkt__eyyd}, total_rows_np[0], {join_node.n_out_table_cols})
"""
    if join_node.has_live_out_table_var:
        func_text += f'    T = out_data[0]\n'
    else:
        func_text += f'    T = None\n'
    if join_node.has_live_out_index_var:
        skd__tyyxm = 1 if join_node.has_live_out_table_var else 0
        func_text += f'    index_var = out_data[{skd__tyyxm}]\n'
    else:
        func_text += f'    index_var = None\n'
    glbs['py_table_type'] = out_table_type
    glbs['index_col_type'] = index_col_type
    glbs['out_col_inds'] = MetaType(tuple(out_physical_to_logical_list))
    if bool(join_node.out_used_cols) or index_col_type != types.none:
        func_text += '    delete_table(out_table)\n'
    if out_table_type != types.none:
        xnn__owtao = determine_table_cast_map(matched_key_types,
            left_key_types, left_used_key_nums, join_node.
            left_to_output_map, False, join_node.loc)
        xnn__owtao.update(determine_table_cast_map(matched_key_types,
            right_key_types, right_used_key_nums, join_node.
            right_to_output_map, False, join_node.loc))
        dfe__lylgv = False
        gnmy__pujkr = False
        if join_node.has_live_out_table_var:
            wsbj__dmtm = list(out_table_type.arr_types)
        else:
            wsbj__dmtm = None
        for rkue__kpbr, lkx__kvsw in xnn__owtao.items():
            if rkue__kpbr < join_node.n_out_table_cols:
                assert join_node.has_live_out_table_var, 'Casting columns for a dead table should not occur'
                wsbj__dmtm[rkue__kpbr] = lkx__kvsw
                dfe__lylgv = True
            else:
                jwco__szfv = lkx__kvsw
                gnmy__pujkr = True
        if dfe__lylgv:
            func_text += f"""    T = bodo.utils.table_utils.table_astype(T, cast_table_type, False, _bodo_nan_to_str=False, used_cols=used_cols)
"""
            ohmwm__feo = bodo.TableType(tuple(wsbj__dmtm))
            glbs['py_table_type'] = ohmwm__feo
            glbs['cast_table_type'] = out_table_type
            glbs['used_cols'] = MetaType(tuple(out_table_used_cols))
        if gnmy__pujkr:
            glbs['index_col_type'] = jwco__szfv
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
    xnn__owtao: Dict[int, types.Type] = {}
    wwhl__enjo = len(matched_key_types)
    for xqxfi__luly in range(wwhl__enjo):
        if used_key_nums is None or xqxfi__luly in used_key_nums:
            if matched_key_types[xqxfi__luly] != key_types[xqxfi__luly] and (
                convert_dict_col or key_types[xqxfi__luly] != bodo.
                dict_str_arr_type):
                if output_map:
                    skd__tyyxm = output_map[xqxfi__luly]
                else:
                    skd__tyyxm = xqxfi__luly
                xnn__owtao[skd__tyyxm] = matched_key_types[xqxfi__luly]
    return xnn__owtao


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    pkizp__abtfi = bodo.libs.distributed_api.get_size()
    olt__wro = np.empty(pkizp__abtfi, left_key_arrs[0].dtype)
    fazdg__xnfoc = np.empty(pkizp__abtfi, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(olt__wro, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(fazdg__xnfoc, left_key_arrs[0][-1])
    hupp__ggv = np.zeros(pkizp__abtfi, np.int32)
    qxtb__sxk = np.zeros(pkizp__abtfi, np.int32)
    nxzad__gvhg = np.zeros(pkizp__abtfi, np.int32)
    ipvn__wyelb = right_key_arrs[0][0]
    kbzc__qrhus = right_key_arrs[0][-1]
    lff__llqt = -1
    xqxfi__luly = 0
    while xqxfi__luly < pkizp__abtfi - 1 and fazdg__xnfoc[xqxfi__luly
        ] < ipvn__wyelb:
        xqxfi__luly += 1
    while xqxfi__luly < pkizp__abtfi and olt__wro[xqxfi__luly] <= kbzc__qrhus:
        lff__llqt, xsv__izanr = _count_overlap(right_key_arrs[0], olt__wro[
            xqxfi__luly], fazdg__xnfoc[xqxfi__luly])
        if lff__llqt != 0:
            lff__llqt -= 1
            xsv__izanr += 1
        hupp__ggv[xqxfi__luly] = xsv__izanr
        qxtb__sxk[xqxfi__luly] = lff__llqt
        xqxfi__luly += 1
    while xqxfi__luly < pkizp__abtfi:
        hupp__ggv[xqxfi__luly] = 1
        qxtb__sxk[xqxfi__luly] = len(right_key_arrs[0]) - 1
        xqxfi__luly += 1
    bodo.libs.distributed_api.alltoall(hupp__ggv, nxzad__gvhg, 1)
    qwy__hbz = nxzad__gvhg.sum()
    acvrz__bfi = np.empty(qwy__hbz, right_key_arrs[0].dtype)
    svbtk__gqnil = alloc_arr_tup(qwy__hbz, right_data)
    qvmdx__czlx = bodo.ir.join.calc_disp(nxzad__gvhg)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], acvrz__bfi,
        hupp__ggv, nxzad__gvhg, qxtb__sxk, qvmdx__czlx)
    bodo.libs.distributed_api.alltoallv_tup(right_data, svbtk__gqnil,
        hupp__ggv, nxzad__gvhg, qxtb__sxk, qvmdx__czlx)
    return (acvrz__bfi,), svbtk__gqnil


@numba.njit
def _count_overlap(r_key_arr, start, end):
    xsv__izanr = 0
    lff__llqt = 0
    nxzb__pdq = 0
    while nxzb__pdq < len(r_key_arr) and r_key_arr[nxzb__pdq] < start:
        lff__llqt += 1
        nxzb__pdq += 1
    while nxzb__pdq < len(r_key_arr) and start <= r_key_arr[nxzb__pdq] <= end:
        nxzb__pdq += 1
        xsv__izanr += 1
    return lff__llqt, xsv__izanr


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    psso__asc = np.empty_like(arr)
    psso__asc[0] = 0
    for xqxfi__luly in range(1, len(arr)):
        psso__asc[xqxfi__luly] = psso__asc[xqxfi__luly - 1] + arr[
            xqxfi__luly - 1]
    return psso__asc


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    xlx__cufj = len(left_keys[0])
    uuak__jdmjy = len(right_keys[0])
    vismm__dsoj = alloc_arr_tup(xlx__cufj, left_keys)
    lpcxp__tootx = alloc_arr_tup(xlx__cufj, right_keys)
    ktlwh__iko = alloc_arr_tup(xlx__cufj, data_left)
    eocpz__jjbkb = alloc_arr_tup(xlx__cufj, data_right)
    ubttb__snko = 0
    unw__uajq = 0
    for ubttb__snko in range(xlx__cufj):
        if unw__uajq < 0:
            unw__uajq = 0
        while unw__uajq < uuak__jdmjy and getitem_arr_tup(right_keys, unw__uajq
            ) <= getitem_arr_tup(left_keys, ubttb__snko):
            unw__uajq += 1
        unw__uajq -= 1
        setitem_arr_tup(vismm__dsoj, ubttb__snko, getitem_arr_tup(left_keys,
            ubttb__snko))
        setitem_arr_tup(ktlwh__iko, ubttb__snko, getitem_arr_tup(data_left,
            ubttb__snko))
        if unw__uajq >= 0:
            setitem_arr_tup(lpcxp__tootx, ubttb__snko, getitem_arr_tup(
                right_keys, unw__uajq))
            setitem_arr_tup(eocpz__jjbkb, ubttb__snko, getitem_arr_tup(
                data_right, unw__uajq))
        else:
            bodo.libs.array_kernels.setna_tup(lpcxp__tootx, ubttb__snko)
            bodo.libs.array_kernels.setna_tup(eocpz__jjbkb, ubttb__snko)
    return vismm__dsoj, lpcxp__tootx, ktlwh__iko, eocpz__jjbkb
