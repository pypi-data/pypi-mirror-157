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
    tmnv__aprgv = not is_overload_none(func_name)
    if tmnv__aprgv:
        func_name = get_overload_const_str(func_name)
        ngw__zobct = get_overload_const_bool(is_method)
    xlok__gybqf = out_arr_typ.instance_type if isinstance(out_arr_typ,
        types.TypeRef) else out_arr_typ
    urk__lcla = xlok__gybqf == types.none
    lmsax__auiir = len(table.arr_types)
    if urk__lcla:
        nvr__hqvd = table
    else:
        ycki__aher = tuple([xlok__gybqf] * lmsax__auiir)
        nvr__hqvd = TableType(ycki__aher)
    enlpd__elapv = {'bodo': bodo, 'lst_dtype': xlok__gybqf, 'table_typ':
        nvr__hqvd}
    yrr__tgbdi = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if urk__lcla:
        yrr__tgbdi += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        yrr__tgbdi += f'  l = len(table)\n'
    else:
        yrr__tgbdi += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({lmsax__auiir}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        yuzju__zwz = used_cols.instance_type
        xcs__dhbef = np.array(yuzju__zwz.meta, dtype=np.int64)
        enlpd__elapv['used_cols_glbl'] = xcs__dhbef
        wolx__memil = set([table.block_nums[nmi__qqwr] for nmi__qqwr in
            xcs__dhbef])
        yrr__tgbdi += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        yrr__tgbdi += f'  used_cols_set = None\n'
        xcs__dhbef = None
    yrr__tgbdi += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for vnk__jsu in table.type_to_blk.values():
        yrr__tgbdi += (
            f'  blk_{vnk__jsu} = bodo.hiframes.table.get_table_block(table, {vnk__jsu})\n'
            )
        if urk__lcla:
            yrr__tgbdi += f"""  out_list_{vnk__jsu} = bodo.hiframes.table.alloc_list_like(blk_{vnk__jsu}, len(blk_{vnk__jsu}), False)
"""
            rimjj__wrpns = f'out_list_{vnk__jsu}'
        else:
            rimjj__wrpns = 'out_list'
        if xcs__dhbef is None or vnk__jsu in wolx__memil:
            yrr__tgbdi += f'  for i in range(len(blk_{vnk__jsu})):\n'
            enlpd__elapv[f'col_indices_{vnk__jsu}'] = np.array(table.
                block_to_arr_ind[vnk__jsu], dtype=np.int64)
            yrr__tgbdi += f'    col_loc = col_indices_{vnk__jsu}[i]\n'
            if xcs__dhbef is not None:
                yrr__tgbdi += f'    if col_loc not in used_cols_set:\n'
                yrr__tgbdi += f'        continue\n'
            if urk__lcla:
                tlkw__uzwd = 'i'
            else:
                tlkw__uzwd = 'col_loc'
            if not tmnv__aprgv:
                yrr__tgbdi += (
                    f'    {rimjj__wrpns}[{tlkw__uzwd}] = blk_{vnk__jsu}[i]\n')
            elif ngw__zobct:
                yrr__tgbdi += f"""    {rimjj__wrpns}[{tlkw__uzwd}] = blk_{vnk__jsu}[i].{func_name}()
"""
            else:
                yrr__tgbdi += (
                    f'    {rimjj__wrpns}[{tlkw__uzwd}] = {func_name}(blk_{vnk__jsu}[i])\n'
                    )
        if urk__lcla:
            yrr__tgbdi += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {rimjj__wrpns}, {vnk__jsu})
"""
    if urk__lcla:
        yrr__tgbdi += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        yrr__tgbdi += '  return out_table\n'
    else:
        yrr__tgbdi += """  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)
"""
    awx__vmyo = {}
    exec(yrr__tgbdi, enlpd__elapv, awx__vmyo)
    return awx__vmyo['impl']


def generate_mappable_table_func_equiv(self, scope, equiv_set, loc, args, kws):
    mot__dugcb = args[0]
    if equiv_set.has_shape(mot__dugcb):
        return ArrayAnalysis.AnalyzeResult(shape=mot__dugcb, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_utils_table_utils_generate_mappable_table_func
    ) = generate_mappable_table_func_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    enlpd__elapv = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.
        distributed_api.Reduce_Type.Sum.value)}
    yrr__tgbdi = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    yrr__tgbdi += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for vnk__jsu in table.type_to_blk.values():
        yrr__tgbdi += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {vnk__jsu})\n'
            )
        enlpd__elapv[f'col_indices_{vnk__jsu}'] = np.array(table.
            block_to_arr_ind[vnk__jsu], dtype=np.int64)
        yrr__tgbdi += '  for i in range(len(blk)):\n'
        yrr__tgbdi += f'    col_loc = col_indices_{vnk__jsu}[i]\n'
        yrr__tgbdi += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    yrr__tgbdi += '  if parallel:\n'
    yrr__tgbdi += '    for i in range(start_offset, len(out_arr)):\n'
    yrr__tgbdi += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    awx__vmyo = {}
    exec(yrr__tgbdi, enlpd__elapv, awx__vmyo)
    return awx__vmyo['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    mrr__xcrj = table.type_to_blk[arr_type]
    enlpd__elapv = {'bodo': bodo}
    enlpd__elapv['col_indices'] = np.array(table.block_to_arr_ind[mrr__xcrj
        ], dtype=np.int64)
    laa__xfk = col_nums_meta.instance_type
    enlpd__elapv['col_nums'] = np.array(laa__xfk.meta, np.int64)
    yrr__tgbdi = 'def impl(table, col_nums_meta, arr_type):\n'
    yrr__tgbdi += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {mrr__xcrj})\n')
    yrr__tgbdi += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    yrr__tgbdi += '  n = len(table)\n'
    vocib__kfrz = bodo.utils.typing.is_str_arr_type(arr_type)
    if vocib__kfrz:
        yrr__tgbdi += '  total_chars = 0\n'
        yrr__tgbdi += '  for c in col_nums:\n'
        yrr__tgbdi += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        yrr__tgbdi += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        yrr__tgbdi += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        yrr__tgbdi += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        yrr__tgbdi += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    yrr__tgbdi += '  for i in range(len(col_nums)):\n'
    yrr__tgbdi += '    c = col_nums[i]\n'
    if not vocib__kfrz:
        yrr__tgbdi += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    yrr__tgbdi += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    yrr__tgbdi += '    off = i * n\n'
    yrr__tgbdi += '    for j in range(len(arr)):\n'
    yrr__tgbdi += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    yrr__tgbdi += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    yrr__tgbdi += '      else:\n'
    yrr__tgbdi += '        out_arr[off+j] = arr[j]\n'
    yrr__tgbdi += '  return out_arr\n'
    nxf__ukvb = {}
    exec(yrr__tgbdi, enlpd__elapv, nxf__ukvb)
    kluxx__bdpsb = nxf__ukvb['impl']
    return kluxx__bdpsb


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    nstcd__cdnvq = not is_overload_false(copy)
    ewnta__xljfr = is_overload_true(copy)
    enlpd__elapv = {'bodo': bodo}
    evhu__osa = table.arr_types
    kusu__fbael = new_table_typ.arr_types
    oacc__lciso: Set[int] = set()
    fcb__gfd: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    gca__jxwa: Set[types.Type] = set()
    for nmi__qqwr, jxbw__jikl in enumerate(evhu__osa):
        zoygq__sde = kusu__fbael[nmi__qqwr]
        if jxbw__jikl == zoygq__sde:
            gca__jxwa.add(jxbw__jikl)
        else:
            oacc__lciso.add(nmi__qqwr)
            fcb__gfd[zoygq__sde].add(jxbw__jikl)
    yrr__tgbdi = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    yrr__tgbdi += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    yrr__tgbdi += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    uxy__oks = set(range(len(evhu__osa)))
    boez__twn = uxy__oks - oacc__lciso
    if not is_overload_none(used_cols):
        yuzju__zwz = used_cols.instance_type
        iswil__xcx = set(yuzju__zwz.meta)
        oacc__lciso = oacc__lciso & iswil__xcx
        boez__twn = boez__twn & iswil__xcx
        wolx__memil = set([table.block_nums[nmi__qqwr] for nmi__qqwr in
            iswil__xcx])
    else:
        iswil__xcx = None
    enlpd__elapv['cast_cols'] = np.array(list(oacc__lciso), dtype=np.int64)
    enlpd__elapv['copied_cols'] = np.array(list(boez__twn), dtype=np.int64)
    yrr__tgbdi += f'  copied_cols_set = set(copied_cols)\n'
    yrr__tgbdi += f'  cast_cols_set = set(cast_cols)\n'
    for diiu__dksmm, vnk__jsu in new_table_typ.type_to_blk.items():
        enlpd__elapv[f'typ_list_{vnk__jsu}'] = types.List(diiu__dksmm)
        yrr__tgbdi += f"""  out_arr_list_{vnk__jsu} = bodo.hiframes.table.alloc_list_like(typ_list_{vnk__jsu}, {len(new_table_typ.block_to_arr_ind[vnk__jsu])}, False)
"""
        if diiu__dksmm in gca__jxwa:
            lwnyp__enp = table.type_to_blk[diiu__dksmm]
            if iswil__xcx is None or lwnyp__enp in wolx__memil:
                tkn__ijq = table.block_to_arr_ind[lwnyp__enp]
                teby__dpsw = [new_table_typ.block_offsets[qwwbv__iji] for
                    qwwbv__iji in tkn__ijq]
                enlpd__elapv[f'new_idx_{lwnyp__enp}'] = np.array(teby__dpsw,
                    np.int64)
                enlpd__elapv[f'orig_arr_inds_{lwnyp__enp}'] = np.array(tkn__ijq
                    , np.int64)
                yrr__tgbdi += f"""  arr_list_{lwnyp__enp} = bodo.hiframes.table.get_table_block(table, {lwnyp__enp})
"""
                yrr__tgbdi += (
                    f'  for i in range(len(arr_list_{lwnyp__enp})):\n')
                yrr__tgbdi += (
                    f'    arr_ind_{lwnyp__enp} = orig_arr_inds_{lwnyp__enp}[i]\n'
                    )
                yrr__tgbdi += (
                    f'    if arr_ind_{lwnyp__enp} not in copied_cols_set:\n')
                yrr__tgbdi += f'      continue\n'
                yrr__tgbdi += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{lwnyp__enp}, i, arr_ind_{lwnyp__enp})
"""
                yrr__tgbdi += (
                    f'    out_idx_{vnk__jsu}_{lwnyp__enp} = new_idx_{lwnyp__enp}[i]\n'
                    )
                yrr__tgbdi += (
                    f'    arr_val_{lwnyp__enp} = arr_list_{lwnyp__enp}[i]\n')
                if ewnta__xljfr:
                    yrr__tgbdi += (
                        f'    arr_val_{lwnyp__enp} = arr_val_{lwnyp__enp}.copy()\n'
                        )
                elif nstcd__cdnvq:
                    yrr__tgbdi += f"""    arr_val_{lwnyp__enp} = arr_val_{lwnyp__enp}.copy() if copy else arr_val_{vnk__jsu}
"""
                yrr__tgbdi += f"""    out_arr_list_{vnk__jsu}[out_idx_{vnk__jsu}_{lwnyp__enp}] = arr_val_{lwnyp__enp}
"""
    fwpv__kyp = set()
    for diiu__dksmm, vnk__jsu in new_table_typ.type_to_blk.items():
        if diiu__dksmm in fcb__gfd:
            if isinstance(diiu__dksmm, bodo.IntegerArrayType):
                wgr__eujh = diiu__dksmm.get_pandas_scalar_type_instance.name
            else:
                wgr__eujh = diiu__dksmm.dtype
            enlpd__elapv[f'typ_{vnk__jsu}'] = wgr__eujh
            dxzvi__isb = fcb__gfd[diiu__dksmm]
            for omcij__xmj in dxzvi__isb:
                lwnyp__enp = table.type_to_blk[omcij__xmj]
                if iswil__xcx is None or lwnyp__enp in wolx__memil:
                    if (omcij__xmj not in gca__jxwa and omcij__xmj not in
                        fwpv__kyp):
                        tkn__ijq = table.block_to_arr_ind[lwnyp__enp]
                        teby__dpsw = [new_table_typ.block_offsets[
                            qwwbv__iji] for qwwbv__iji in tkn__ijq]
                        enlpd__elapv[f'new_idx_{lwnyp__enp}'] = np.array(
                            teby__dpsw, np.int64)
                        enlpd__elapv[f'orig_arr_inds_{lwnyp__enp}'] = np.array(
                            tkn__ijq, np.int64)
                        yrr__tgbdi += f"""  arr_list_{lwnyp__enp} = bodo.hiframes.table.get_table_block(table, {lwnyp__enp})
"""
                    fwpv__kyp.add(omcij__xmj)
                    yrr__tgbdi += (
                        f'  for i in range(len(arr_list_{lwnyp__enp})):\n')
                    yrr__tgbdi += (
                        f'    arr_ind_{lwnyp__enp} = orig_arr_inds_{lwnyp__enp}[i]\n'
                        )
                    yrr__tgbdi += (
                        f'    if arr_ind_{lwnyp__enp} not in cast_cols_set:\n')
                    yrr__tgbdi += f'      continue\n'
                    yrr__tgbdi += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{lwnyp__enp}, i, arr_ind_{lwnyp__enp})
"""
                    yrr__tgbdi += (
                        f'    out_idx_{vnk__jsu}_{lwnyp__enp} = new_idx_{lwnyp__enp}[i]\n'
                        )
                    yrr__tgbdi += f"""    arr_val_{vnk__jsu} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{lwnyp__enp}[i], typ_{vnk__jsu}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    yrr__tgbdi += f"""    out_arr_list_{vnk__jsu}[out_idx_{vnk__jsu}_{lwnyp__enp}] = arr_val_{vnk__jsu}
"""
        yrr__tgbdi += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{vnk__jsu}, {vnk__jsu})
"""
    yrr__tgbdi += '  return out_table\n'
    awx__vmyo = {}
    exec(yrr__tgbdi, enlpd__elapv, awx__vmyo)
    return awx__vmyo['impl']


def table_astype_equiv(self, scope, equiv_set, loc, args, kws):
    mot__dugcb = args[0]
    if equiv_set.has_shape(mot__dugcb):
        return ArrayAnalysis.AnalyzeResult(shape=mot__dugcb, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_utils_table_utils_table_astype = (
    table_astype_equiv)
