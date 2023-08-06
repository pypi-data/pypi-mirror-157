"""File containing utility functions for supporting DataFrame operations with Table Format."""
from collections import defaultdict
from typing import Dict, Set
import numba
import numpy as np
from numba.core import types
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.table import TableType
from bodo.utils.typing import get_overload_const_bool, get_overload_const_str, is_overload_constant_bool, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, raise_bodo_error


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_mappable_table_func(table, func_name, out_arr_typ, is_method,
    used_cols=None):
    if not is_overload_constant_str(func_name) and not is_overload_none(
        func_name):
        raise_bodo_error(
            'generate_mappable_table_func(): func_name must be a constant string'
            )
    if not is_overload_constant_bool(is_method):
        raise_bodo_error(
            'generate_mappable_table_func(): is_method must be a constant boolean'
            )
    hqs__mhd = not is_overload_none(func_name)
    if hqs__mhd:
        func_name = get_overload_const_str(func_name)
        bgl__lgawi = get_overload_const_bool(is_method)
    aryla__xitq = out_arr_typ.instance_type if isinstance(out_arr_typ,
        types.TypeRef) else out_arr_typ
    pneaw__ytpff = aryla__xitq == types.none
    ykwd__pwd = len(table.arr_types)
    if pneaw__ytpff:
        ttrmy__rkda = table
    else:
        uxehz__lclb = tuple([aryla__xitq] * ykwd__pwd)
        ttrmy__rkda = TableType(uxehz__lclb)
    mxs__smt = {'bodo': bodo, 'lst_dtype': aryla__xitq, 'table_typ':
        ttrmy__rkda}
    gvjyq__jfof = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if pneaw__ytpff:
        gvjyq__jfof += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        gvjyq__jfof += f'  l = len(table)\n'
    else:
        gvjyq__jfof += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({ykwd__pwd}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        tse__wryoa = used_cols.instance_type
        vfgy__ncz = np.array(tse__wryoa.meta, dtype=np.int64)
        mxs__smt['used_cols_glbl'] = vfgy__ncz
        obu__akzr = set([table.block_nums[gzew__hcqc] for gzew__hcqc in
            vfgy__ncz])
        gvjyq__jfof += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        gvjyq__jfof += f'  used_cols_set = None\n'
        vfgy__ncz = None
    gvjyq__jfof += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for eaxh__ttan in table.type_to_blk.values():
        gvjyq__jfof += f"""  blk_{eaxh__ttan} = bodo.hiframes.table.get_table_block(table, {eaxh__ttan})
"""
        if pneaw__ytpff:
            gvjyq__jfof += f"""  out_list_{eaxh__ttan} = bodo.hiframes.table.alloc_list_like(blk_{eaxh__ttan}, len(blk_{eaxh__ttan}), False)
"""
            texa__fqwu = f'out_list_{eaxh__ttan}'
        else:
            texa__fqwu = 'out_list'
        if vfgy__ncz is None or eaxh__ttan in obu__akzr:
            gvjyq__jfof += f'  for i in range(len(blk_{eaxh__ttan})):\n'
            mxs__smt[f'col_indices_{eaxh__ttan}'] = np.array(table.
                block_to_arr_ind[eaxh__ttan], dtype=np.int64)
            gvjyq__jfof += f'    col_loc = col_indices_{eaxh__ttan}[i]\n'
            if vfgy__ncz is not None:
                gvjyq__jfof += f'    if col_loc not in used_cols_set:\n'
                gvjyq__jfof += f'        continue\n'
            if pneaw__ytpff:
                vss__zng = 'i'
            else:
                vss__zng = 'col_loc'
            if not hqs__mhd:
                gvjyq__jfof += (
                    f'    {texa__fqwu}[{vss__zng}] = blk_{eaxh__ttan}[i]\n')
            elif bgl__lgawi:
                gvjyq__jfof += (
                    f'    {texa__fqwu}[{vss__zng}] = blk_{eaxh__ttan}[i].{func_name}()\n'
                    )
            else:
                gvjyq__jfof += (
                    f'    {texa__fqwu}[{vss__zng}] = {func_name}(blk_{eaxh__ttan}[i])\n'
                    )
        if pneaw__ytpff:
            gvjyq__jfof += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {texa__fqwu}, {eaxh__ttan})
"""
    if pneaw__ytpff:
        gvjyq__jfof += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        gvjyq__jfof += '  return out_table\n'
    else:
        gvjyq__jfof += """  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)
"""
    kuf__yiee = {}
    exec(gvjyq__jfof, mxs__smt, kuf__yiee)
    return kuf__yiee['impl']


def generate_mappable_table_func_equiv(self, scope, equiv_set, loc, args, kws):
    qlww__byvg = args[0]
    if equiv_set.has_shape(qlww__byvg):
        return ArrayAnalysis.AnalyzeResult(shape=qlww__byvg, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_utils_table_utils_generate_mappable_table_func
    ) = generate_mappable_table_func_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    mxs__smt = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.distributed_api.
        Reduce_Type.Sum.value)}
    gvjyq__jfof = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    gvjyq__jfof += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for eaxh__ttan in table.type_to_blk.values():
        gvjyq__jfof += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {eaxh__ttan})\n'
            )
        mxs__smt[f'col_indices_{eaxh__ttan}'] = np.array(table.
            block_to_arr_ind[eaxh__ttan], dtype=np.int64)
        gvjyq__jfof += '  for i in range(len(blk)):\n'
        gvjyq__jfof += f'    col_loc = col_indices_{eaxh__ttan}[i]\n'
        gvjyq__jfof += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    gvjyq__jfof += '  if parallel:\n'
    gvjyq__jfof += '    for i in range(start_offset, len(out_arr)):\n'
    gvjyq__jfof += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    kuf__yiee = {}
    exec(gvjyq__jfof, mxs__smt, kuf__yiee)
    return kuf__yiee['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    mqpod__kjd = table.type_to_blk[arr_type]
    mxs__smt = {'bodo': bodo}
    mxs__smt['col_indices'] = np.array(table.block_to_arr_ind[mqpod__kjd],
        dtype=np.int64)
    giocn__guyjo = col_nums_meta.instance_type
    mxs__smt['col_nums'] = np.array(giocn__guyjo.meta, np.int64)
    gvjyq__jfof = 'def impl(table, col_nums_meta, arr_type):\n'
    gvjyq__jfof += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {mqpod__kjd})\n')
    gvjyq__jfof += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    gvjyq__jfof += '  n = len(table)\n'
    fuwu__lsv = bodo.utils.typing.is_str_arr_type(arr_type)
    if fuwu__lsv:
        gvjyq__jfof += '  total_chars = 0\n'
        gvjyq__jfof += '  for c in col_nums:\n'
        gvjyq__jfof += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        gvjyq__jfof += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        gvjyq__jfof += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        gvjyq__jfof += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        gvjyq__jfof += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    gvjyq__jfof += '  for i in range(len(col_nums)):\n'
    gvjyq__jfof += '    c = col_nums[i]\n'
    if not fuwu__lsv:
        gvjyq__jfof += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    gvjyq__jfof += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    gvjyq__jfof += '    off = i * n\n'
    gvjyq__jfof += '    for j in range(len(arr)):\n'
    gvjyq__jfof += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    gvjyq__jfof += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    gvjyq__jfof += '      else:\n'
    gvjyq__jfof += '        out_arr[off+j] = arr[j]\n'
    gvjyq__jfof += '  return out_arr\n'
    vcm__nsq = {}
    exec(gvjyq__jfof, mxs__smt, vcm__nsq)
    joxu__kdyx = vcm__nsq['impl']
    return joxu__kdyx


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    pftur__ymlh = not is_overload_false(copy)
    wpqtz__iagc = is_overload_true(copy)
    mxs__smt = {'bodo': bodo}
    izq__hag = table.arr_types
    bsfej__oolhh = new_table_typ.arr_types
    zyjf__zjg: Set[int] = set()
    xkq__wrzqn: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    fvoeo__uxdc: Set[types.Type] = set()
    for gzew__hcqc, sap__pxy in enumerate(izq__hag):
        vbpd__wsaxg = bsfej__oolhh[gzew__hcqc]
        if sap__pxy == vbpd__wsaxg:
            fvoeo__uxdc.add(sap__pxy)
        else:
            zyjf__zjg.add(gzew__hcqc)
            xkq__wrzqn[vbpd__wsaxg].add(sap__pxy)
    gvjyq__jfof = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    gvjyq__jfof += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    gvjyq__jfof += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    akig__uno = set(range(len(izq__hag)))
    ncqlt__sta = akig__uno - zyjf__zjg
    if not is_overload_none(used_cols):
        tse__wryoa = used_cols.instance_type
        dmt__axgs = set(tse__wryoa.meta)
        zyjf__zjg = zyjf__zjg & dmt__axgs
        ncqlt__sta = ncqlt__sta & dmt__axgs
        obu__akzr = set([table.block_nums[gzew__hcqc] for gzew__hcqc in
            dmt__axgs])
    else:
        dmt__axgs = None
    mxs__smt['cast_cols'] = np.array(list(zyjf__zjg), dtype=np.int64)
    mxs__smt['copied_cols'] = np.array(list(ncqlt__sta), dtype=np.int64)
    gvjyq__jfof += f'  copied_cols_set = set(copied_cols)\n'
    gvjyq__jfof += f'  cast_cols_set = set(cast_cols)\n'
    for adm__xyku, eaxh__ttan in new_table_typ.type_to_blk.items():
        mxs__smt[f'typ_list_{eaxh__ttan}'] = types.List(adm__xyku)
        gvjyq__jfof += f"""  out_arr_list_{eaxh__ttan} = bodo.hiframes.table.alloc_list_like(typ_list_{eaxh__ttan}, {len(new_table_typ.block_to_arr_ind[eaxh__ttan])}, False)
"""
        if adm__xyku in fvoeo__uxdc:
            qdp__boeag = table.type_to_blk[adm__xyku]
            if dmt__axgs is None or qdp__boeag in obu__akzr:
                poa__exybp = table.block_to_arr_ind[qdp__boeag]
                csx__eemyq = [new_table_typ.block_offsets[hzu__thit] for
                    hzu__thit in poa__exybp]
                mxs__smt[f'new_idx_{qdp__boeag}'] = np.array(csx__eemyq, np
                    .int64)
                mxs__smt[f'orig_arr_inds_{qdp__boeag}'] = np.array(poa__exybp,
                    np.int64)
                gvjyq__jfof += f"""  arr_list_{qdp__boeag} = bodo.hiframes.table.get_table_block(table, {qdp__boeag})
"""
                gvjyq__jfof += (
                    f'  for i in range(len(arr_list_{qdp__boeag})):\n')
                gvjyq__jfof += (
                    f'    arr_ind_{qdp__boeag} = orig_arr_inds_{qdp__boeag}[i]\n'
                    )
                gvjyq__jfof += (
                    f'    if arr_ind_{qdp__boeag} not in copied_cols_set:\n')
                gvjyq__jfof += f'      continue\n'
                gvjyq__jfof += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{qdp__boeag}, i, arr_ind_{qdp__boeag})
"""
                gvjyq__jfof += (
                    f'    out_idx_{eaxh__ttan}_{qdp__boeag} = new_idx_{qdp__boeag}[i]\n'
                    )
                gvjyq__jfof += (
                    f'    arr_val_{qdp__boeag} = arr_list_{qdp__boeag}[i]\n')
                if wpqtz__iagc:
                    gvjyq__jfof += (
                        f'    arr_val_{qdp__boeag} = arr_val_{qdp__boeag}.copy()\n'
                        )
                elif pftur__ymlh:
                    gvjyq__jfof += f"""    arr_val_{qdp__boeag} = arr_val_{qdp__boeag}.copy() if copy else arr_val_{eaxh__ttan}
"""
                gvjyq__jfof += f"""    out_arr_list_{eaxh__ttan}[out_idx_{eaxh__ttan}_{qdp__boeag}] = arr_val_{qdp__boeag}
"""
    kte__ikjfz = set()
    for adm__xyku, eaxh__ttan in new_table_typ.type_to_blk.items():
        if adm__xyku in xkq__wrzqn:
            if isinstance(adm__xyku, bodo.IntegerArrayType):
                scgpe__fvazi = adm__xyku.get_pandas_scalar_type_instance.name
            else:
                scgpe__fvazi = adm__xyku.dtype
            mxs__smt[f'typ_{eaxh__ttan}'] = scgpe__fvazi
            foq__krlz = xkq__wrzqn[adm__xyku]
            for rtcup__txcd in foq__krlz:
                qdp__boeag = table.type_to_blk[rtcup__txcd]
                if dmt__axgs is None or qdp__boeag in obu__akzr:
                    if (rtcup__txcd not in fvoeo__uxdc and rtcup__txcd not in
                        kte__ikjfz):
                        poa__exybp = table.block_to_arr_ind[qdp__boeag]
                        csx__eemyq = [new_table_typ.block_offsets[hzu__thit
                            ] for hzu__thit in poa__exybp]
                        mxs__smt[f'new_idx_{qdp__boeag}'] = np.array(csx__eemyq
                            , np.int64)
                        mxs__smt[f'orig_arr_inds_{qdp__boeag}'] = np.array(
                            poa__exybp, np.int64)
                        gvjyq__jfof += f"""  arr_list_{qdp__boeag} = bodo.hiframes.table.get_table_block(table, {qdp__boeag})
"""
                    kte__ikjfz.add(rtcup__txcd)
                    gvjyq__jfof += (
                        f'  for i in range(len(arr_list_{qdp__boeag})):\n')
                    gvjyq__jfof += (
                        f'    arr_ind_{qdp__boeag} = orig_arr_inds_{qdp__boeag}[i]\n'
                        )
                    gvjyq__jfof += (
                        f'    if arr_ind_{qdp__boeag} not in cast_cols_set:\n')
                    gvjyq__jfof += f'      continue\n'
                    gvjyq__jfof += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{qdp__boeag}, i, arr_ind_{qdp__boeag})
"""
                    gvjyq__jfof += f"""    out_idx_{eaxh__ttan}_{qdp__boeag} = new_idx_{qdp__boeag}[i]
"""
                    gvjyq__jfof += f"""    arr_val_{eaxh__ttan} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{qdp__boeag}[i], typ_{eaxh__ttan}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    gvjyq__jfof += f"""    out_arr_list_{eaxh__ttan}[out_idx_{eaxh__ttan}_{qdp__boeag}] = arr_val_{eaxh__ttan}
"""
        gvjyq__jfof += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{eaxh__ttan}, {eaxh__ttan})
"""
    gvjyq__jfof += '  return out_table\n'
    kuf__yiee = {}
    exec(gvjyq__jfof, mxs__smt, kuf__yiee)
    return kuf__yiee['impl']


def table_astype_equiv(self, scope, equiv_set, loc, args, kws):
    qlww__byvg = args[0]
    if equiv_set.has_shape(qlww__byvg):
        return ArrayAnalysis.AnalyzeResult(shape=qlww__byvg, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_utils_table_utils_table_astype = (
    table_astype_equiv)
