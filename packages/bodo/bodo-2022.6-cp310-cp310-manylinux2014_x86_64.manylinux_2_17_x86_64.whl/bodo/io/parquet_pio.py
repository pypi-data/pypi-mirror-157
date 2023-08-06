import os
import warnings
from collections import defaultdict
from glob import has_magic
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow
import pyarrow.dataset as ds
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, get_definition, guard, mk_unique_var, next_label, replace_arg_nodes
from numba.extending import NativeValue, box, intrinsic, models, overload, register_model, unbox
from pyarrow import null
from pyarrow._fs import PyFileSystem
from pyarrow.fs import FSSpecHandler
import bodo
import bodo.ir.parquet_ext
import bodo.utils.tracing as tracing
from bodo.hiframes.datetime_date_ext import datetime_date_array_type, datetime_date_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import TableType
from bodo.io.fs_io import get_hdfs_fs, get_s3_fs_from_path, get_storage_options_pyobject, storage_options_dict_type
from bodo.io.helpers import is_nullable
from bodo.libs.array import cpp_table_to_py_table, delete_table, info_from_table, info_to_array, table_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.dict_arr_ext import dict_str_arr_type
from bodo.libs.distributed_api import get_end, get_start
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.transforms import distributed_pass
from bodo.utils.transform import get_const_value
from bodo.utils.typing import BodoError, BodoWarning, FileInfo, get_overload_const_str
from bodo.utils.utils import check_and_propagate_cpp_exception, numba_to_c_type, sanitize_varname
use_nullable_int_arr = True
from urllib.parse import urlparse
REMOTE_FILESYSTEMS = {'s3', 'gcs', 'gs', 'http', 'hdfs', 'abfs', 'abfss'}
READ_STR_AS_DICT_THRESHOLD = 1.0
list_of_files_error_msg = (
    '. Make sure the list/glob passed to read_parquet() only contains paths to files (no directories)'
    )


class ParquetPredicateType(types.Type):

    def __init__(self):
        super(ParquetPredicateType, self).__init__(name=
            'ParquetPredicateType()')


parquet_predicate_type = ParquetPredicateType()
types.parquet_predicate_type = parquet_predicate_type
register_model(ParquetPredicateType)(models.OpaqueModel)


@unbox(ParquetPredicateType)
def unbox_parquet_predicate_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


@box(ParquetPredicateType)
def box_parquet_predicate_type(typ, val, c):
    c.pyapi.incref(val)
    return val


class ReadParquetFilepathType(types.Opaque):

    def __init__(self):
        super(ReadParquetFilepathType, self).__init__(name=
            'ReadParquetFilepathType')


read_parquet_fpath_type = ReadParquetFilepathType()
types.read_parquet_fpath_type = read_parquet_fpath_type
register_model(ReadParquetFilepathType)(models.OpaqueModel)


@unbox(ReadParquetFilepathType)
def unbox_read_parquet_fpath_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


class ParquetFileInfo(FileInfo):

    def __init__(self, columns, storage_options=None, input_file_name_col=
        None, read_as_dict_cols=None):
        self.columns = columns
        self.storage_options = storage_options
        self.input_file_name_col = input_file_name_col
        self.read_as_dict_cols = read_as_dict_cols
        super().__init__()

    def _get_schema(self, fname):
        try:
            return parquet_file_schema(fname, selected_columns=self.columns,
                storage_options=self.storage_options, input_file_name_col=
                self.input_file_name_col, read_as_dict_cols=self.
                read_as_dict_cols)
        except OSError as ylvn__ojoa:
            if 'non-file path' in str(ylvn__ojoa):
                raise FileNotFoundError(str(ylvn__ojoa))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        rcc__fqd = lhs.scope
        rmpgv__phd = lhs.loc
        zplme__nrn = None
        if lhs.name in self.locals:
            zplme__nrn = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        xkunc__egmb = {}
        if lhs.name + ':convert' in self.locals:
            xkunc__egmb = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if zplme__nrn is None:
            pmu__rytjc = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            tqdzj__zpx = get_const_value(file_name, self.func_ir,
                pmu__rytjc, arg_types=self.args, file_info=ParquetFileInfo(
                columns, storage_options=storage_options,
                input_file_name_col=input_file_name_col, read_as_dict_cols=
                read_as_dict_cols))
            lbdi__qtnw = False
            dwmo__xgz = guard(get_definition, self.func_ir, file_name)
            if isinstance(dwmo__xgz, ir.Arg):
                typ = self.args[dwmo__xgz.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, elbpe__ausw, ixpmi__xan, col_indices,
                        partition_names, qegde__ojy, urx__cmzpl) = typ.schema
                    lbdi__qtnw = True
            if not lbdi__qtnw:
                (col_names, elbpe__ausw, ixpmi__xan, col_indices,
                    partition_names, qegde__ojy, urx__cmzpl) = (
                    parquet_file_schema(tqdzj__zpx, columns,
                    storage_options=storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            frnah__sbw = list(zplme__nrn.keys())
            els__zqtna = {c: jfbza__lidq for jfbza__lidq, c in enumerate(
                frnah__sbw)}
            ihqo__qlxu = [ivnkn__dsf for ivnkn__dsf in zplme__nrn.values()]
            ixpmi__xan = 'index' if 'index' in els__zqtna else None
            if columns is None:
                selected_columns = frnah__sbw
            else:
                selected_columns = columns
            col_indices = [els__zqtna[c] for c in selected_columns]
            elbpe__ausw = [ihqo__qlxu[els__zqtna[c]] for c in selected_columns]
            col_names = selected_columns
            ixpmi__xan = ixpmi__xan if ixpmi__xan in col_names else None
            partition_names = []
            qegde__ojy = []
            urx__cmzpl = []
        hala__vuqoc = None if isinstance(ixpmi__xan, dict
            ) or ixpmi__xan is None else ixpmi__xan
        index_column_index = None
        index_column_type = types.none
        if hala__vuqoc:
            mvsx__rgbf = col_names.index(hala__vuqoc)
            index_column_index = col_indices.pop(mvsx__rgbf)
            index_column_type = elbpe__ausw.pop(mvsx__rgbf)
            col_names.pop(mvsx__rgbf)
        for jfbza__lidq, c in enumerate(col_names):
            if c in xkunc__egmb:
                elbpe__ausw[jfbza__lidq] = xkunc__egmb[c]
        zwoj__ctt = [ir.Var(rcc__fqd, mk_unique_var('pq_table'), rmpgv__phd
            ), ir.Var(rcc__fqd, mk_unique_var('pq_index'), rmpgv__phd)]
        yjrjf__qup = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.name,
            col_names, col_indices, elbpe__ausw, zwoj__ctt, rmpgv__phd,
            partition_names, storage_options, index_column_index,
            index_column_type, input_file_name_col, qegde__ojy, urx__cmzpl)]
        return (col_names, zwoj__ctt, ixpmi__xan, yjrjf__qup, elbpe__ausw,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    xrh__yqez = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    bswbo__nkphm, stc__opa = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    extra_args = ', '.join(bswbo__nkphm.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, bswbo__nkphm, stc__opa, pq_node.
        original_df_colnames, pq_node.partition_names, pq_node.
        original_out_types, typemap, 'parquet', output_dnf=False)
    ofa__zimbm = ', '.join(f'out{jfbza__lidq}' for jfbza__lidq in range(
        xrh__yqez))
    aqeg__nogvq = f'def pq_impl(fname, {extra_args}):\n'
    aqeg__nogvq += (
        f'    (total_rows, {ofa__zimbm},) = _pq_reader_py(fname, {extra_args})\n'
        )
    ayhd__ocjmu = {}
    exec(aqeg__nogvq, {}, ayhd__ocjmu)
    nyrft__qzj = ayhd__ocjmu['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        wzfeb__xmz = pq_node.loc.strformat()
        ieeg__diaw = []
        zaxa__qdol = []
        for jfbza__lidq in pq_node.out_used_cols:
            dnmjg__kzels = pq_node.df_colnames[jfbza__lidq]
            ieeg__diaw.append(dnmjg__kzels)
            if isinstance(pq_node.out_types[jfbza__lidq], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                zaxa__qdol.append(dnmjg__kzels)
        fbx__hkd = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', fbx__hkd,
            wzfeb__xmz, ieeg__diaw)
        if zaxa__qdol:
            awwt__psdm = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', awwt__psdm,
                wzfeb__xmz, zaxa__qdol)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        ejkg__eoo = set(pq_node.out_used_cols)
        wvd__bwic = set(pq_node.unsupported_columns)
        tyyu__vwil = ejkg__eoo & wvd__bwic
        if tyyu__vwil:
            dmaty__vbh = sorted(tyyu__vwil)
            bvhi__urbca = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            fnuz__fghyl = 0
            for vfp__cjnd in dmaty__vbh:
                while pq_node.unsupported_columns[fnuz__fghyl] != vfp__cjnd:
                    fnuz__fghyl += 1
                bvhi__urbca.append(
                    f"Column '{pq_node.df_colnames[vfp__cjnd]}' with unsupported arrow type {pq_node.unsupported_arrow_types[fnuz__fghyl]}"
                    )
                fnuz__fghyl += 1
            cwyft__nhgc = '\n'.join(bvhi__urbca)
            raise BodoError(cwyft__nhgc, loc=pq_node.loc)
    vxbi__gwvrq = _gen_pq_reader_py(pq_node.df_colnames, pq_node.
        col_indices, pq_node.out_used_cols, pq_node.out_types, pq_node.
        storage_options, pq_node.partition_names, dnf_filter_str,
        expr_filter_str, extra_args, parallel, meta_head_only_info, pq_node
        .index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col)
    qdih__wbvx = typemap[pq_node.file_name.name]
    jcgq__mib = (qdih__wbvx,) + tuple(typemap[afr__pyfc.name] for afr__pyfc in
        stc__opa)
    uoym__fgf = compile_to_numba_ir(nyrft__qzj, {'_pq_reader_py':
        vxbi__gwvrq}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        jcgq__mib, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(uoym__fgf, [pq_node.file_name] + stc__opa)
    yjrjf__qup = uoym__fgf.body[:-3]
    if meta_head_only_info:
        yjrjf__qup[-3].target = meta_head_only_info[1]
    yjrjf__qup[-2].target = pq_node.out_vars[0]
    yjrjf__qup[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        yjrjf__qup.pop(-1)
    elif not pq_node.out_used_cols:
        yjrjf__qup.pop(-2)
    return yjrjf__qup


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    tab__jrowg = get_overload_const_str(dnf_filter_str)
    yby__lico = get_overload_const_str(expr_filter_str)
    ywery__vph = ', '.join(f'f{jfbza__lidq}' for jfbza__lidq in range(len(
        var_tup)))
    aqeg__nogvq = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        aqeg__nogvq += f'  {ywery__vph}, = var_tup\n'
    aqeg__nogvq += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    aqeg__nogvq += f'    dnf_filters_py = {tab__jrowg}\n'
    aqeg__nogvq += f'    expr_filters_py = {yby__lico}\n'
    aqeg__nogvq += '  return (dnf_filters_py, expr_filters_py)\n'
    ayhd__ocjmu = {}
    exec(aqeg__nogvq, globals(), ayhd__ocjmu)
    return ayhd__ocjmu['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col):
    hwwp__jjv = next_label()
    kdmq__ucis = ',' if extra_args else ''
    aqeg__nogvq = f'def pq_reader_py(fname,{extra_args}):\n'
    aqeg__nogvq += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    aqeg__nogvq += f"    ev.add_attribute('g_fname', fname)\n"
    aqeg__nogvq += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{kdmq__ucis}))
"""
    aqeg__nogvq += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    aqeg__nogvq += f"""    storage_options_py = get_storage_options_pyobject({str(storage_options)})
"""
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    pawwz__sxwpb = not out_used_cols
    wudy__stmbm = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    fbk__bgl = {c: jfbza__lidq for jfbza__lidq, c in enumerate(col_indices)}
    edip__cxwv = {c: jfbza__lidq for jfbza__lidq, c in enumerate(wudy__stmbm)}
    rdcu__zrarb = []
    gicpz__xwdeo = set()
    roe__skry = partition_names + [input_file_name_col]
    for jfbza__lidq in out_used_cols:
        if wudy__stmbm[jfbza__lidq] not in roe__skry:
            rdcu__zrarb.append(col_indices[jfbza__lidq])
        elif not input_file_name_col or wudy__stmbm[jfbza__lidq
            ] != input_file_name_col:
            gicpz__xwdeo.add(col_indices[jfbza__lidq])
    if index_column_index is not None:
        rdcu__zrarb.append(index_column_index)
    rdcu__zrarb = sorted(rdcu__zrarb)
    sbu__ohta = {c: jfbza__lidq for jfbza__lidq, c in enumerate(rdcu__zrarb)}
    ech__tpq = [(int(is_nullable(out_types[fbk__bgl[awh__fpf]])) if 
        awh__fpf != index_column_index else int(is_nullable(
        index_column_type))) for awh__fpf in rdcu__zrarb]
    str_as_dict_cols = []
    for awh__fpf in rdcu__zrarb:
        if awh__fpf == index_column_index:
            ivnkn__dsf = index_column_type
        else:
            ivnkn__dsf = out_types[fbk__bgl[awh__fpf]]
        if ivnkn__dsf == dict_str_arr_type:
            str_as_dict_cols.append(awh__fpf)
    vkci__fnkpp = []
    pfpyo__paw = {}
    lcyy__bzvd = []
    tury__ykdj = []
    for jfbza__lidq, zmdr__dewr in enumerate(partition_names):
        try:
            gdyr__rwk = edip__cxwv[zmdr__dewr]
            if col_indices[gdyr__rwk] not in gicpz__xwdeo:
                continue
        except (KeyError, ValueError) as oqqi__budwh:
            continue
        pfpyo__paw[zmdr__dewr] = len(vkci__fnkpp)
        vkci__fnkpp.append(zmdr__dewr)
        lcyy__bzvd.append(jfbza__lidq)
        gvp__itrzz = out_types[gdyr__rwk].dtype
        jhe__pefo = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            gvp__itrzz)
        tury__ykdj.append(numba_to_c_type(jhe__pefo))
    aqeg__nogvq += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    aqeg__nogvq += f'    out_table = pq_read(\n'
    aqeg__nogvq += f'        fname_py, {is_parallel},\n'
    aqeg__nogvq += f'        dnf_filters, expr_filters,\n'
    aqeg__nogvq += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{hwwp__jjv}.ctypes,
"""
    aqeg__nogvq += f'        {len(rdcu__zrarb)},\n'
    aqeg__nogvq += f'        nullable_cols_arr_{hwwp__jjv}.ctypes,\n'
    if len(lcyy__bzvd) > 0:
        aqeg__nogvq += (
            f'        np.array({lcyy__bzvd}, dtype=np.int32).ctypes,\n')
        aqeg__nogvq += (
            f'        np.array({tury__ykdj}, dtype=np.int32).ctypes,\n')
        aqeg__nogvq += f'        {len(lcyy__bzvd)},\n'
    else:
        aqeg__nogvq += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        aqeg__nogvq += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        aqeg__nogvq += f'        0, 0,\n'
    aqeg__nogvq += f'        total_rows_np.ctypes,\n'
    aqeg__nogvq += f'        {input_file_name_col is not None},\n'
    aqeg__nogvq += f'    )\n'
    aqeg__nogvq += f'    check_and_propagate_cpp_exception()\n'
    ishmf__ofrxp = 'None'
    qga__qpriy = index_column_type
    rdha__ivmjf = TableType(tuple(out_types))
    if pawwz__sxwpb:
        rdha__ivmjf = types.none
    if index_column_index is not None:
        lhlq__whks = sbu__ohta[index_column_index]
        ishmf__ofrxp = (
            f'info_to_array(info_from_table(out_table, {lhlq__whks}), index_arr_type)'
            )
    aqeg__nogvq += f'    index_arr = {ishmf__ofrxp}\n'
    if pawwz__sxwpb:
        pqv__unh = None
    else:
        pqv__unh = []
        gay__xaw = 0
        bsm__zdh = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for jfbza__lidq, vfp__cjnd in enumerate(col_indices):
            if gay__xaw < len(out_used_cols) and jfbza__lidq == out_used_cols[
                gay__xaw]:
                zara__henjl = col_indices[jfbza__lidq]
                if bsm__zdh and zara__henjl == bsm__zdh:
                    pqv__unh.append(len(rdcu__zrarb) + len(vkci__fnkpp))
                elif zara__henjl in gicpz__xwdeo:
                    rqe__qcifq = wudy__stmbm[jfbza__lidq]
                    pqv__unh.append(len(rdcu__zrarb) + pfpyo__paw[rqe__qcifq])
                else:
                    pqv__unh.append(sbu__ohta[vfp__cjnd])
                gay__xaw += 1
            else:
                pqv__unh.append(-1)
        pqv__unh = np.array(pqv__unh, dtype=np.int64)
    if pawwz__sxwpb:
        aqeg__nogvq += '    T = None\n'
    else:
        aqeg__nogvq += f"""    T = cpp_table_to_py_table(out_table, table_idx_{hwwp__jjv}, py_table_type_{hwwp__jjv})
"""
    aqeg__nogvq += f'    delete_table(out_table)\n'
    aqeg__nogvq += f'    total_rows = total_rows_np[0]\n'
    aqeg__nogvq += f'    ev.finalize()\n'
    aqeg__nogvq += f'    return (total_rows, T, index_arr)\n'
    ayhd__ocjmu = {}
    eftw__gpkpz = {f'py_table_type_{hwwp__jjv}': rdha__ivmjf,
        f'table_idx_{hwwp__jjv}': pqv__unh,
        f'selected_cols_arr_{hwwp__jjv}': np.array(rdcu__zrarb, np.int32),
        f'nullable_cols_arr_{hwwp__jjv}': np.array(ech__tpq, np.int32),
        'index_arr_type': qga__qpriy, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(aqeg__nogvq, eftw__gpkpz, ayhd__ocjmu)
    vxbi__gwvrq = ayhd__ocjmu['pq_reader_py']
    jiwuh__sqfo = numba.njit(vxbi__gwvrq, no_cpython_wrapper=True)
    return jiwuh__sqfo


import pyarrow as pa
_pa_numba_typ_map = {pa.bool_(): types.bool_, pa.int8(): types.int8, pa.
    int16(): types.int16, pa.int32(): types.int32, pa.int64(): types.int64,
    pa.uint8(): types.uint8, pa.uint16(): types.uint16, pa.uint32(): types.
    uint32, pa.uint64(): types.uint64, pa.float32(): types.float32, pa.
    float64(): types.float64, pa.string(): string_type, pa.binary():
    bytes_type, pa.date32(): datetime_date_type, pa.date64(): types.
    NPDatetime('ns'), null(): string_type}


def get_arrow_timestamp_type(pa_ts_typ):
    jwyc__ohov = 'ns', 'us', 'ms', 's'
    if pa_ts_typ.unit not in jwyc__ohov:
        return types.Array(bodo.datetime64ns, 1, 'C'), False
    elif pa_ts_typ.tz is not None:
        uke__lssbl = pa_ts_typ.to_pandas_dtype().tz
        hnbb__kqsl = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(
            uke__lssbl)
        return bodo.DatetimeArrayType(hnbb__kqsl), True
    else:
        return types.Array(bodo.datetime64ns, 1, 'C'), True


def _get_numba_typ_from_pa_typ(pa_typ, is_index, nullable_from_metadata,
    category_info, str_as_dict=False):
    if isinstance(pa_typ.type, pa.ListType):
        jwcew__uldwi, tbjfs__utex = _get_numba_typ_from_pa_typ(pa_typ.type.
            value_field, is_index, nullable_from_metadata, category_info)
        return ArrayItemArrayType(jwcew__uldwi), tbjfs__utex
    if isinstance(pa_typ.type, pa.StructType):
        sflgd__dfq = []
        ufgc__itfay = []
        tbjfs__utex = True
        for vxge__nqcc in pa_typ.flatten():
            ufgc__itfay.append(vxge__nqcc.name.split('.')[-1])
            aviwq__grwgn, lqgfg__tei = _get_numba_typ_from_pa_typ(vxge__nqcc,
                is_index, nullable_from_metadata, category_info)
            sflgd__dfq.append(aviwq__grwgn)
            tbjfs__utex = tbjfs__utex and lqgfg__tei
        return StructArrayType(tuple(sflgd__dfq), tuple(ufgc__itfay)
            ), tbjfs__utex
    if isinstance(pa_typ.type, pa.Decimal128Type):
        return DecimalArrayType(pa_typ.type.precision, pa_typ.type.scale), True
    if str_as_dict:
        if pa_typ.type != pa.string():
            raise BodoError(
                f'Read as dictionary used for non-string column {pa_typ}')
        return dict_str_arr_type, True
    if isinstance(pa_typ.type, pa.DictionaryType):
        if pa_typ.type.value_type != pa.string():
            raise BodoError(
                f'Parquet Categorical data type should be string, not {pa_typ.type.value_type}'
                )
        zkqm__fma = _pa_numba_typ_map[pa_typ.type.index_type]
        hesz__mtk = PDCategoricalDtype(category_info[pa_typ.name], bodo.
            string_type, pa_typ.type.ordered, int_type=zkqm__fma)
        return CategoricalArrayType(hesz__mtk), True
    if isinstance(pa_typ.type, pa.lib.TimestampType):
        return get_arrow_timestamp_type(pa_typ.type)
    elif pa_typ.type in _pa_numba_typ_map:
        zhrj__xvo = _pa_numba_typ_map[pa_typ.type]
        tbjfs__utex = True
    else:
        raise BodoError('Arrow data type {} not supported yet'.format(
            pa_typ.type))
    if zhrj__xvo == datetime_date_type:
        return datetime_date_array_type, tbjfs__utex
    if zhrj__xvo == bytes_type:
        return binary_array_type, tbjfs__utex
    jwcew__uldwi = (string_array_type if zhrj__xvo == string_type else
        types.Array(zhrj__xvo, 1, 'C'))
    if zhrj__xvo == types.bool_:
        jwcew__uldwi = boolean_array
    if nullable_from_metadata is not None:
        ldchl__coltt = nullable_from_metadata
    else:
        ldchl__coltt = use_nullable_int_arr
    if ldchl__coltt and not is_index and isinstance(zhrj__xvo, types.Integer
        ) and pa_typ.nullable:
        jwcew__uldwi = IntegerArrayType(zhrj__xvo)
    return jwcew__uldwi, tbjfs__utex


class ParquetDataset(object):

    def __init__(self, pa_pq_dataset, prefix=''):
        self.schema = pa_pq_dataset.schema
        self.filesystem = None
        self._bodo_total_rows = 0
        self._prefix = prefix
        self.partition_names = ([] if pa_pq_dataset.partitioning is None or
            pa_pq_dataset.partitioning.schema == pa_pq_dataset.schema else
            list(pa_pq_dataset.partitioning.schema.names))
        if self.partition_names:
            self.partitioning_dictionaries = (pa_pq_dataset.partitioning.
                dictionaries)
        else:
            self.partitioning_dictionaries = {}
        for ywo__xkix in self.partition_names:
            self.schema = self.schema.remove(self.schema.get_field_index(
                ywo__xkix))
        self.pieces = [ParquetPiece(frag, pa_pq_dataset.partitioning, self.
            partition_names) for frag in pa_pq_dataset._dataset.
            get_fragments(filter=pa_pq_dataset._filter_expression)]

    def set_fs(self, fs):
        self.filesystem = fs
        for stkp__asvfp in self.pieces:
            stkp__asvfp.filesystem = fs


class ParquetPiece(object):

    def __init__(self, frag, partitioning, partition_names):
        self._frag = None
        self.format = frag.format
        self.path = frag.path
        self._bodo_num_rows = 0
        self.partition_keys = []
        if partitioning is not None:
            self.partition_keys = ds._get_partition_keys(frag.
                partition_expression)
            self.partition_keys = [(zmdr__dewr, partitioning.dictionaries[
                jfbza__lidq].index(self.partition_keys[zmdr__dewr]).as_py()
                ) for jfbza__lidq, zmdr__dewr in enumerate(partition_names)]

    @property
    def frag(self):
        if self._frag is None:
            self._frag = self.format.make_fragment(self.path, self.filesystem)
            del self.format
        return self._frag

    @property
    def metadata(self):
        return self.frag.metadata

    @property
    def num_row_groups(self):
        return self.frag.num_row_groups


def get_parquet_dataset(fpath, get_row_counts=True, dnf_filters=None,
    expr_filters=None, storage_options=None, read_categories=False,
    is_parallel=False, tot_rows_to_read=None, typing_pa_schema=None,
    partitioning='hive'):
    if get_row_counts:
        njqys__qfoj = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    ekng__gpwyu = MPI.COMM_WORLD
    if isinstance(fpath, list):
        lai__krper = urlparse(fpath[0])
        protocol = lai__krper.scheme
        rqxy__fqib = lai__krper.netloc
        for jfbza__lidq in range(len(fpath)):
            rhj__zjrep = fpath[jfbza__lidq]
            fub__rtsu = urlparse(rhj__zjrep)
            if fub__rtsu.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if fub__rtsu.netloc != rqxy__fqib:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[jfbza__lidq] = rhj__zjrep.rstrip('/')
    else:
        lai__krper = urlparse(fpath)
        protocol = lai__krper.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as oqqi__budwh:
            tiae__tsheg = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(tiae__tsheg)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as oqqi__budwh:
            tiae__tsheg = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
"""
    fs = []

    def getfs(parallel=False):
        if len(fs) == 1:
            return fs[0]
        if protocol == 's3':
            fs.append(get_s3_fs_from_path(fpath, parallel=parallel,
                storage_options=storage_options) if not isinstance(fpath,
                list) else get_s3_fs_from_path(fpath[0], parallel=parallel,
                storage_options=storage_options))
        elif protocol in {'gcs', 'gs'}:
            sqyu__kzu = gcsfs.GCSFileSystem(token=None)
            fs.append(PyFileSystem(FSSpecHandler(sqyu__kzu)))
        elif protocol == 'http':
            fs.append(PyFileSystem(FSSpecHandler(fsspec.filesystem('http'))))
        elif protocol in {'hdfs', 'abfs', 'abfss'}:
            fs.append(get_hdfs_fs(fpath) if not isinstance(fpath, list) else
                get_hdfs_fs(fpath[0]))
        else:
            fs.append(pyarrow.fs.LocalFileSystem())
        return fs[0]

    def glob(protocol, fs, path):
        if not protocol and fs is None:
            from fsspec.implementations.local import LocalFileSystem
            fs = LocalFileSystem()
        if isinstance(fs, pyarrow.fs.FileSystem):
            from fsspec.implementations.arrow import ArrowFSWrapper
            fs = ArrowFSWrapper(fs)
        try:
            tenm__bpyt = fs.glob(path)
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(tenm__bpyt) == 0:
            raise BodoError('No files found matching glob pattern')
        return tenm__bpyt
    dejo__ukjmj = False
    if get_row_counts:
        hfu__zln = getfs(parallel=True)
        dejo__ukjmj = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        qbxcz__ftvmk = 1
        qwxu__qau = os.cpu_count()
        if qwxu__qau is not None and qwxu__qau > 1:
            qbxcz__ftvmk = qwxu__qau // 2
        try:
            if get_row_counts:
                rvo__cecii = tracing.Event('pq.ParquetDataset', is_parallel
                    =False)
                if tracing.is_tracing():
                    rvo__cecii.add_attribute('g_dnf_filter', str(dnf_filters))
            iju__fybol = pa.io_thread_count()
            pa.set_io_thread_count(qbxcz__ftvmk)
            prefix = ''
            if protocol == 's3':
                prefix = 's3://'
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{lai__krper.netloc}'
            if prefix:
                if isinstance(fpath, list):
                    fok__xhzl = [rhj__zjrep[len(prefix):] for rhj__zjrep in
                        fpath]
                else:
                    fok__xhzl = fpath[len(prefix):]
            else:
                fok__xhzl = fpath
            if isinstance(fok__xhzl, list):
                elkn__baaxt = []
                for stkp__asvfp in fok__xhzl:
                    if has_magic(stkp__asvfp):
                        elkn__baaxt += glob(protocol, getfs(), stkp__asvfp)
                    else:
                        elkn__baaxt.append(stkp__asvfp)
                fok__xhzl = elkn__baaxt
            elif has_magic(fok__xhzl):
                fok__xhzl = glob(protocol, getfs(), fok__xhzl)
            wzuz__facis = pq.ParquetDataset(fok__xhzl, filesystem=getfs(),
                filters=None, use_legacy_dataset=False, partitioning=
                partitioning)
            if dnf_filters is not None:
                wzuz__facis._filters = dnf_filters
                wzuz__facis._filter_expression = pq._filters_to_expression(
                    dnf_filters)
            hfx__qxxl = len(wzuz__facis.files)
            wzuz__facis = ParquetDataset(wzuz__facis, prefix)
            pa.set_io_thread_count(iju__fybol)
            if typing_pa_schema:
                wzuz__facis.schema = typing_pa_schema
            if get_row_counts:
                if dnf_filters is not None:
                    rvo__cecii.add_attribute('num_pieces_before_filter',
                        hfx__qxxl)
                    rvo__cecii.add_attribute('num_pieces_after_filter', len
                        (wzuz__facis.pieces))
                rvo__cecii.finalize()
        except Exception as ylvn__ojoa:
            if isinstance(ylvn__ojoa, IsADirectoryError):
                ylvn__ojoa = BodoError(list_of_files_error_msg)
            elif isinstance(fpath, list) and isinstance(ylvn__ojoa, (
                OSError, FileNotFoundError)):
                ylvn__ojoa = BodoError(str(ylvn__ojoa) +
                    list_of_files_error_msg)
            else:
                ylvn__ojoa = BodoError(
                    f"""error from pyarrow: {type(ylvn__ojoa).__name__}: {str(ylvn__ojoa)}
"""
                    )
            ekng__gpwyu.bcast(ylvn__ojoa)
            raise ylvn__ojoa
        if get_row_counts:
            xyq__cod = tracing.Event('bcast dataset')
        ekng__gpwyu.bcast(wzuz__facis)
    else:
        if get_row_counts:
            xyq__cod = tracing.Event('bcast dataset')
        wzuz__facis = ekng__gpwyu.bcast(None)
        if isinstance(wzuz__facis, Exception):
            ijxy__spret = wzuz__facis
            raise ijxy__spret
    wzuz__facis.set_fs(getfs())
    if get_row_counts:
        xyq__cod.finalize()
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = dejo__ukjmj = False
    if get_row_counts or dejo__ukjmj:
        if get_row_counts and tracing.is_tracing():
            ypf__prl = tracing.Event('get_row_counts')
            ypf__prl.add_attribute('g_num_pieces', len(wzuz__facis.pieces))
            ypf__prl.add_attribute('g_expr_filters', str(expr_filters))
        rcg__nmv = 0.0
        num_pieces = len(wzuz__facis.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        gjkmf__imfzr = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        muv__atku = 0
        eku__onjnu = 0
        sssg__gaddb = 0
        ehfi__ckk = True
        if expr_filters is not None:
            import random
            random.seed(37)
            sqnyq__sczo = random.sample(wzuz__facis.pieces, k=len(
                wzuz__facis.pieces))
        else:
            sqnyq__sczo = wzuz__facis.pieces
        fpaths = [stkp__asvfp.path for stkp__asvfp in sqnyq__sczo[start:
            gjkmf__imfzr]]
        qbxcz__ftvmk = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(qbxcz__ftvmk)
        pa.set_cpu_count(qbxcz__ftvmk)
        ijxy__spret = None
        try:
            ivng__zmiwj = ds.dataset(fpaths, filesystem=wzuz__facis.
                filesystem, partitioning=ds.partitioning(flavor='hive') if
                wzuz__facis.partition_names else None)
            for iouop__jwe, frag in zip(sqnyq__sczo[start:gjkmf__imfzr],
                ivng__zmiwj.get_fragments()):
                if dejo__ukjmj:
                    cyz__tppvv = frag.metadata.schema.to_arrow_schema()
                    ncsfj__kyjwd = set(cyz__tppvv.names)
                    dsn__jekhc = set(wzuz__facis.schema.names)
                    if dsn__jekhc != ncsfj__kyjwd:
                        yrxry__rtmvt = ncsfj__kyjwd - dsn__jekhc
                        alw__kosx = dsn__jekhc - ncsfj__kyjwd
                        pmu__rytjc = f'Schema in {iouop__jwe} was different.\n'
                        if yrxry__rtmvt:
                            pmu__rytjc += f"""File contains column(s) {yrxry__rtmvt} not found in other files in the dataset.
"""
                        if alw__kosx:
                            pmu__rytjc += f"""File missing column(s) {alw__kosx} found in other files in the dataset.
"""
                        raise BodoError(pmu__rytjc)
                    try:
                        wzuz__facis.schema = pa.unify_schemas([wzuz__facis.
                            schema, cyz__tppvv])
                    except Exception as ylvn__ojoa:
                        pmu__rytjc = (
                            f'Schema in {iouop__jwe} was different.\n' +
                            str(ylvn__ojoa))
                        raise BodoError(pmu__rytjc)
                gvtz__flw = time.time()
                vantb__ibykw = frag.scanner(schema=ivng__zmiwj.schema,
                    filter=expr_filters, use_threads=True).count_rows()
                rcg__nmv += time.time() - gvtz__flw
                iouop__jwe._bodo_num_rows = vantb__ibykw
                muv__atku += vantb__ibykw
                eku__onjnu += frag.num_row_groups
                sssg__gaddb += sum(baoq__ytbi.total_byte_size for
                    baoq__ytbi in frag.row_groups)
        except Exception as ylvn__ojoa:
            ijxy__spret = ylvn__ojoa
        if ekng__gpwyu.allreduce(ijxy__spret is not None, op=MPI.LOR):
            for ijxy__spret in ekng__gpwyu.allgather(ijxy__spret):
                if ijxy__spret:
                    if isinstance(fpath, list) and isinstance(ijxy__spret,
                        (OSError, FileNotFoundError)):
                        raise BodoError(str(ijxy__spret) +
                            list_of_files_error_msg)
                    raise ijxy__spret
        if dejo__ukjmj:
            ehfi__ckk = ekng__gpwyu.allreduce(ehfi__ckk, op=MPI.LAND)
            if not ehfi__ckk:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            wzuz__facis._bodo_total_rows = ekng__gpwyu.allreduce(muv__atku,
                op=MPI.SUM)
            qat__fdtrv = ekng__gpwyu.allreduce(eku__onjnu, op=MPI.SUM)
            rlkqt__fykz = ekng__gpwyu.allreduce(sssg__gaddb, op=MPI.SUM)
            gei__addc = np.array([stkp__asvfp._bodo_num_rows for
                stkp__asvfp in wzuz__facis.pieces])
            gei__addc = ekng__gpwyu.allreduce(gei__addc, op=MPI.SUM)
            for stkp__asvfp, xrh__lusgv in zip(wzuz__facis.pieces, gei__addc):
                stkp__asvfp._bodo_num_rows = xrh__lusgv
            if is_parallel and bodo.get_rank(
                ) == 0 and qat__fdtrv < bodo.get_size() and qat__fdtrv != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({qat__fdtrv}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if qat__fdtrv == 0:
                zvqsc__ipwd = 0
            else:
                zvqsc__ipwd = rlkqt__fykz // qat__fdtrv
            if (bodo.get_rank() == 0 and rlkqt__fykz >= 20 * 1048576 and 
                zvqsc__ipwd < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({zvqsc__ipwd} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                ypf__prl.add_attribute('g_total_num_row_groups', qat__fdtrv)
                ypf__prl.add_attribute('total_scan_time', rcg__nmv)
                jcuam__idvc = np.array([stkp__asvfp._bodo_num_rows for
                    stkp__asvfp in wzuz__facis.pieces])
                zmvtx__etu = np.percentile(jcuam__idvc, [25, 50, 75])
                ypf__prl.add_attribute('g_row_counts_min', jcuam__idvc.min())
                ypf__prl.add_attribute('g_row_counts_Q1', zmvtx__etu[0])
                ypf__prl.add_attribute('g_row_counts_median', zmvtx__etu[1])
                ypf__prl.add_attribute('g_row_counts_Q3', zmvtx__etu[2])
                ypf__prl.add_attribute('g_row_counts_max', jcuam__idvc.max())
                ypf__prl.add_attribute('g_row_counts_mean', jcuam__idvc.mean())
                ypf__prl.add_attribute('g_row_counts_std', jcuam__idvc.std())
                ypf__prl.add_attribute('g_row_counts_sum', jcuam__idvc.sum())
                ypf__prl.finalize()
    if read_categories:
        _add_categories_to_pq_dataset(wzuz__facis)
    if get_row_counts:
        njqys__qfoj.finalize()
    if dejo__ukjmj and is_parallel:
        if tracing.is_tracing():
            tcczx__gnli = tracing.Event('unify_schemas_across_ranks')
        ijxy__spret = None
        try:
            wzuz__facis.schema = ekng__gpwyu.allreduce(wzuz__facis.schema,
                bodo.io.helpers.pa_schema_unify_mpi_op)
        except Exception as ylvn__ojoa:
            ijxy__spret = ylvn__ojoa
        if tracing.is_tracing():
            tcczx__gnli.finalize()
        if ekng__gpwyu.allreduce(ijxy__spret is not None, op=MPI.LOR):
            for ijxy__spret in ekng__gpwyu.allgather(ijxy__spret):
                if ijxy__spret:
                    pmu__rytjc = (f'Schema in some files were different.\n' +
                        str(ijxy__spret))
                    raise BodoError(pmu__rytjc)
    return wzuz__facis


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, filesystem, str_as_dict_cols, start_offset,
    rows_to_read, has_partitions, schema):
    import pyarrow as pa
    qwxu__qau = os.cpu_count()
    if qwxu__qau is None or qwxu__qau == 0:
        qwxu__qau = 2
    vkcrw__srfqf = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), qwxu__qau
        )
    vioog__vtjuq = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)),
        qwxu__qau)
    if is_parallel and len(fpaths) > vioog__vtjuq and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(vioog__vtjuq)
        pa.set_cpu_count(vioog__vtjuq)
    else:
        pa.set_io_thread_count(vkcrw__srfqf)
        pa.set_cpu_count(vkcrw__srfqf)
    yfkp__jgqy = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    wzuz__facis = ds.dataset(fpaths, filesystem=filesystem, partitioning=ds
        .partitioning(flavor='hive') if has_partitions else None, format=
        yfkp__jgqy)
    ruyk__atpl = set(str_as_dict_cols)
    qacn__kvxqz = schema.names
    for jfbza__lidq, name in enumerate(qacn__kvxqz):
        if name in ruyk__atpl:
            kkgv__wecu = schema.field(jfbza__lidq)
            hrmn__hixo = pa.field(name, pa.dictionary(pa.int32(),
                kkgv__wecu.type), kkgv__wecu.nullable)
            schema = schema.remove(jfbza__lidq).insert(jfbza__lidq, hrmn__hixo)
    wzuz__facis = wzuz__facis.replace_schema(pa.unify_schemas([wzuz__facis.
        schema, schema]))
    col_names = wzuz__facis.schema.names
    rzwhy__wbmc = [col_names[njic__slgbq] for njic__slgbq in selected_fields]
    vng__gwz = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if vng__gwz and expr_filters is None:
        xiv__ipyen = []
        utl__txn = 0
        fjzfg__yaic = 0
        for frag in wzuz__facis.get_fragments():
            tutri__sie = []
            for baoq__ytbi in frag.row_groups:
                ujxn__sltuh = baoq__ytbi.num_rows
                if start_offset < utl__txn + ujxn__sltuh:
                    if fjzfg__yaic == 0:
                        cpwqz__asg = start_offset - utl__txn
                        fqgie__lqya = min(ujxn__sltuh - cpwqz__asg,
                            rows_to_read)
                    else:
                        fqgie__lqya = min(ujxn__sltuh, rows_to_read -
                            fjzfg__yaic)
                    fjzfg__yaic += fqgie__lqya
                    tutri__sie.append(baoq__ytbi.id)
                utl__txn += ujxn__sltuh
                if fjzfg__yaic == rows_to_read:
                    break
            xiv__ipyen.append(frag.subset(row_group_ids=tutri__sie))
            if fjzfg__yaic == rows_to_read:
                break
        wzuz__facis = ds.FileSystemDataset(xiv__ipyen, wzuz__facis.schema,
            yfkp__jgqy, filesystem=wzuz__facis.filesystem)
        start_offset = cpwqz__asg
    klvdo__piom = wzuz__facis.scanner(columns=rzwhy__wbmc, filter=
        expr_filters, use_threads=True).to_reader()
    return wzuz__facis, klvdo__piom, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema
    kkzhc__soo = [c for c in pa_schema.names if isinstance(pa_schema.field(
        c).type, pa.DictionaryType) and c not in pq_dataset.partition_names]
    if len(kkzhc__soo) == 0:
        pq_dataset._category_info = {}
        return
    ekng__gpwyu = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            pprt__omcj = pq_dataset.pieces[0].frag.head(100, columns=kkzhc__soo
                )
            category_info = {c: tuple(pprt__omcj.column(c).chunk(0).
                dictionary.to_pylist()) for c in kkzhc__soo}
            del pprt__omcj
        except Exception as ylvn__ojoa:
            ekng__gpwyu.bcast(ylvn__ojoa)
            raise ylvn__ojoa
        ekng__gpwyu.bcast(category_info)
    else:
        category_info = ekng__gpwyu.bcast(None)
        if isinstance(category_info, Exception):
            ijxy__spret = category_info
            raise ijxy__spret
    pq_dataset._category_info = category_info


def get_pandas_metadata(schema, num_pieces):
    ixpmi__xan = None
    nullable_from_metadata = defaultdict(lambda : None)
    cqlvq__twd = b'pandas'
    if schema.metadata is not None and cqlvq__twd in schema.metadata:
        import json
        qhg__bhr = json.loads(schema.metadata[cqlvq__twd].decode('utf8'))
        ixsyb__bqnn = len(qhg__bhr['index_columns'])
        if ixsyb__bqnn > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        ixpmi__xan = qhg__bhr['index_columns'][0] if ixsyb__bqnn else None
        if not isinstance(ixpmi__xan, str) and not isinstance(ixpmi__xan, dict
            ):
            ixpmi__xan = None
        for yueog__gbgda in qhg__bhr['columns']:
            vso__suth = yueog__gbgda['name']
            if yueog__gbgda['pandas_type'].startswith('int'
                ) and vso__suth is not None:
                if yueog__gbgda['numpy_type'].startswith('Int'):
                    nullable_from_metadata[vso__suth] = True
                else:
                    nullable_from_metadata[vso__suth] = False
    return ixpmi__xan, nullable_from_metadata


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for vso__suth in pa_schema.names:
        vxge__nqcc = pa_schema.field(vso__suth)
        if vxge__nqcc.type == pa.string():
            str_columns.append(vso__suth)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    ekng__gpwyu = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        sqnyq__sczo = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        sqnyq__sczo = pq_dataset.pieces
    ozusz__amc = np.zeros(len(str_columns), dtype=np.int64)
    eore__qffy = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(sqnyq__sczo):
        iouop__jwe = sqnyq__sczo[bodo.get_rank()]
        try:
            metadata = iouop__jwe.metadata
            for jfbza__lidq in range(iouop__jwe.num_row_groups):
                for gay__xaw, vso__suth in enumerate(str_columns):
                    fnuz__fghyl = pa_schema.get_field_index(vso__suth)
                    ozusz__amc[gay__xaw] += metadata.row_group(jfbza__lidq
                        ).column(fnuz__fghyl).total_uncompressed_size
            xajc__gunlp = metadata.num_rows
        except Exception as ylvn__ojoa:
            if isinstance(ylvn__ojoa, (OSError, FileNotFoundError)):
                xajc__gunlp = 0
            else:
                raise
    else:
        xajc__gunlp = 0
    ttcd__nyvi = ekng__gpwyu.allreduce(xajc__gunlp, op=MPI.SUM)
    if ttcd__nyvi == 0:
        return set()
    ekng__gpwyu.Allreduce(ozusz__amc, eore__qffy, op=MPI.SUM)
    csde__qygbo = eore__qffy / ttcd__nyvi
    str_as_dict = set()
    for jfbza__lidq, xjkkk__pwht in enumerate(csde__qygbo):
        if xjkkk__pwht < READ_STR_AS_DICT_THRESHOLD:
            vso__suth = str_columns[jfbza__lidq][0]
            str_as_dict.add(vso__suth)
    return str_as_dict


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    elbpe__ausw = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = pq_dataset.partition_names
    pa_schema = pq_dataset.schema
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    dik__zvif = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    xsb__mqlq = read_as_dict_cols - dik__zvif
    if len(xsb__mqlq) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {xsb__mqlq}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(dik__zvif)
    dik__zvif = dik__zvif - read_as_dict_cols
    str_columns = [ctp__tnouc for ctp__tnouc in str_columns if ctp__tnouc in
        dik__zvif]
    str_as_dict: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    str_as_dict.update(read_as_dict_cols)
    col_names = pa_schema.names
    ixpmi__xan, nullable_from_metadata = get_pandas_metadata(pa_schema,
        num_pieces)
    ihqo__qlxu = []
    eimqr__dlwyt = []
    verqr__xljop = []
    for jfbza__lidq, c in enumerate(col_names):
        if c in partition_names:
            continue
        vxge__nqcc = pa_schema.field(c)
        zhrj__xvo, tbjfs__utex = _get_numba_typ_from_pa_typ(vxge__nqcc, c ==
            ixpmi__xan, nullable_from_metadata[c], pq_dataset.
            _category_info, str_as_dict=c in str_as_dict)
        ihqo__qlxu.append(zhrj__xvo)
        eimqr__dlwyt.append(tbjfs__utex)
        verqr__xljop.append(vxge__nqcc.type)
    if partition_names:
        col_names += partition_names
        ihqo__qlxu += [_get_partition_cat_dtype(pq_dataset.
            partitioning_dictionaries[jfbza__lidq]) for jfbza__lidq in
            range(len(partition_names))]
        eimqr__dlwyt.extend([True] * len(partition_names))
        verqr__xljop.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        ihqo__qlxu += [dict_str_arr_type]
        eimqr__dlwyt.append(True)
        verqr__xljop.append(None)
    dbwjt__hlz = {c: jfbza__lidq for jfbza__lidq, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in dbwjt__hlz:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if ixpmi__xan and not isinstance(ixpmi__xan, dict
        ) and ixpmi__xan not in selected_columns:
        selected_columns.append(ixpmi__xan)
    col_names = selected_columns
    col_indices = []
    elbpe__ausw = []
    qegde__ojy = []
    urx__cmzpl = []
    for jfbza__lidq, c in enumerate(col_names):
        zara__henjl = dbwjt__hlz[c]
        col_indices.append(zara__henjl)
        elbpe__ausw.append(ihqo__qlxu[zara__henjl])
        if not eimqr__dlwyt[zara__henjl]:
            qegde__ojy.append(jfbza__lidq)
            urx__cmzpl.append(verqr__xljop[zara__henjl])
    return (col_names, elbpe__ausw, ixpmi__xan, col_indices,
        partition_names, qegde__ojy, urx__cmzpl)


def _get_partition_cat_dtype(dictionary):
    assert dictionary is not None
    xszy__vqzpz = dictionary.to_pandas()
    lwoeq__wlyxc = bodo.typeof(xszy__vqzpz).dtype
    if isinstance(lwoeq__wlyxc, types.Integer):
        hesz__mtk = PDCategoricalDtype(tuple(xszy__vqzpz), lwoeq__wlyxc, 
            False, int_type=lwoeq__wlyxc)
    else:
        hesz__mtk = PDCategoricalDtype(tuple(xszy__vqzpz), lwoeq__wlyxc, False)
    return CategoricalArrayType(hesz__mtk)


_pq_read = types.ExternalFunction('pq_read', table_type(
    read_parquet_fpath_type, types.boolean, parquet_predicate_type,
    parquet_predicate_type, storage_options_dict_type, types.int64, types.
    voidptr, types.int32, types.voidptr, types.voidptr, types.voidptr,
    types.int32, types.voidptr, types.int32, types.voidptr, types.boolean))
from llvmlite import ir as lir
from numba.core import cgutils
if bodo.utils.utils.has_pyarrow():
    from bodo.io import arrow_cpp
    ll.add_symbol('pq_read', arrow_cpp.pq_read)
    ll.add_symbol('pq_write', arrow_cpp.pq_write)
    ll.add_symbol('pq_write_partitioned', arrow_cpp.pq_write_partitioned)


@intrinsic
def parquet_write_table_cpp(typingctx, filename_t, table_t, col_names_t,
    index_t, write_index, metadata_t, compression_t, is_parallel_t,
    write_range_index, start, stop, step, name, bucket_region, row_group_size):

    def codegen(context, builder, sig, args):
        rvee__iyfn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        jetmt__neg = cgutils.get_or_insert_function(builder.module,
            rvee__iyfn, name='pq_write')
        builder.call(jetmt__neg, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, table_t, col_names_t, index_t, types.
        boolean, types.voidptr, types.voidptr, types.boolean, types.boolean,
        types.int32, types.int32, types.int32, types.voidptr, types.voidptr,
        types.int64), codegen


@intrinsic
def parquet_write_table_partitioned_cpp(typingctx, filename_t, data_table_t,
    col_names_t, col_names_no_partitions_t, cat_table_t, part_col_idxs_t,
    num_part_col_t, compression_t, is_parallel_t, bucket_region, row_group_size
    ):

    def codegen(context, builder, sig, args):
        rvee__iyfn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        jetmt__neg = cgutils.get_or_insert_function(builder.module,
            rvee__iyfn, name='pq_write_partitioned')
        builder.call(jetmt__neg, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64), codegen
