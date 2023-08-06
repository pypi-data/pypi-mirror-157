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
        except OSError as srgxm__dsc:
            if 'non-file path' in str(srgxm__dsc):
                raise FileNotFoundError(str(srgxm__dsc))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        zjrz__vcml = lhs.scope
        izdic__vsifx = lhs.loc
        kkess__xnjas = None
        if lhs.name in self.locals:
            kkess__xnjas = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        bpj__kfzg = {}
        if lhs.name + ':convert' in self.locals:
            bpj__kfzg = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if kkess__xnjas is None:
            ymoi__jqvbq = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            jspoo__bqg = get_const_value(file_name, self.func_ir,
                ymoi__jqvbq, arg_types=self.args, file_info=ParquetFileInfo
                (columns, storage_options=storage_options,
                input_file_name_col=input_file_name_col, read_as_dict_cols=
                read_as_dict_cols))
            sbce__jkzfe = False
            pdy__cabd = guard(get_definition, self.func_ir, file_name)
            if isinstance(pdy__cabd, ir.Arg):
                typ = self.args[pdy__cabd.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, ftq__aabts, cguvx__dhi, col_indices,
                        partition_names, brey__bshm, hte__gaw) = typ.schema
                    sbce__jkzfe = True
            if not sbce__jkzfe:
                (col_names, ftq__aabts, cguvx__dhi, col_indices,
                    partition_names, brey__bshm, hte__gaw) = (
                    parquet_file_schema(jspoo__bqg, columns,
                    storage_options=storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            nql__pwjq = list(kkess__xnjas.keys())
            dmuv__usctt = {c: ykyx__omcl for ykyx__omcl, c in enumerate(
                nql__pwjq)}
            rpe__xdwj = [vjuyp__blqiy for vjuyp__blqiy in kkess__xnjas.values()
                ]
            cguvx__dhi = 'index' if 'index' in dmuv__usctt else None
            if columns is None:
                selected_columns = nql__pwjq
            else:
                selected_columns = columns
            col_indices = [dmuv__usctt[c] for c in selected_columns]
            ftq__aabts = [rpe__xdwj[dmuv__usctt[c]] for c in selected_columns]
            col_names = selected_columns
            cguvx__dhi = cguvx__dhi if cguvx__dhi in col_names else None
            partition_names = []
            brey__bshm = []
            hte__gaw = []
        zuw__yst = None if isinstance(cguvx__dhi, dict
            ) or cguvx__dhi is None else cguvx__dhi
        index_column_index = None
        index_column_type = types.none
        if zuw__yst:
            hczwz__ievu = col_names.index(zuw__yst)
            index_column_index = col_indices.pop(hczwz__ievu)
            index_column_type = ftq__aabts.pop(hczwz__ievu)
            col_names.pop(hczwz__ievu)
        for ykyx__omcl, c in enumerate(col_names):
            if c in bpj__kfzg:
                ftq__aabts[ykyx__omcl] = bpj__kfzg[c]
        zies__vzfyu = [ir.Var(zjrz__vcml, mk_unique_var('pq_table'),
            izdic__vsifx), ir.Var(zjrz__vcml, mk_unique_var('pq_index'),
            izdic__vsifx)]
        iuf__kkygi = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.name,
            col_names, col_indices, ftq__aabts, zies__vzfyu, izdic__vsifx,
            partition_names, storage_options, index_column_index,
            index_column_type, input_file_name_col, brey__bshm, hte__gaw)]
        return (col_names, zies__vzfyu, cguvx__dhi, iuf__kkygi, ftq__aabts,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    iqqhz__mrhu = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    dcobd__xvxh, epywg__uoak = bodo.ir.connector.generate_filter_map(pq_node
        .filters)
    extra_args = ', '.join(dcobd__xvxh.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, dcobd__xvxh, epywg__uoak, pq_node.
        original_df_colnames, pq_node.partition_names, pq_node.
        original_out_types, typemap, 'parquet', output_dnf=False)
    ldyc__mzuih = ', '.join(f'out{ykyx__omcl}' for ykyx__omcl in range(
        iqqhz__mrhu))
    derer__sgz = f'def pq_impl(fname, {extra_args}):\n'
    derer__sgz += (
        f'    (total_rows, {ldyc__mzuih},) = _pq_reader_py(fname, {extra_args})\n'
        )
    ciul__ivx = {}
    exec(derer__sgz, {}, ciul__ivx)
    ttp__judub = ciul__ivx['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        tjj__hbh = pq_node.loc.strformat()
        knece__ftlh = []
        dem__abwas = []
        for ykyx__omcl in pq_node.out_used_cols:
            edef__mici = pq_node.df_colnames[ykyx__omcl]
            knece__ftlh.append(edef__mici)
            if isinstance(pq_node.out_types[ykyx__omcl], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                dem__abwas.append(edef__mici)
        eem__ntqr = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', eem__ntqr, tjj__hbh,
            knece__ftlh)
        if dem__abwas:
            jnwjt__trw = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', jnwjt__trw,
                tjj__hbh, dem__abwas)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        tna__gvupj = set(pq_node.out_used_cols)
        pcy__dybxw = set(pq_node.unsupported_columns)
        vns__zgy = tna__gvupj & pcy__dybxw
        if vns__zgy:
            wcop__low = sorted(vns__zgy)
            ruhr__muss = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            ymkhq__efql = 0
            for xiy__lzkw in wcop__low:
                while pq_node.unsupported_columns[ymkhq__efql] != xiy__lzkw:
                    ymkhq__efql += 1
                ruhr__muss.append(
                    f"Column '{pq_node.df_colnames[xiy__lzkw]}' with unsupported arrow type {pq_node.unsupported_arrow_types[ymkhq__efql]}"
                    )
                ymkhq__efql += 1
            qdbuo__celhc = '\n'.join(ruhr__muss)
            raise BodoError(qdbuo__celhc, loc=pq_node.loc)
    xgte__axtzb = _gen_pq_reader_py(pq_node.df_colnames, pq_node.
        col_indices, pq_node.out_used_cols, pq_node.out_types, pq_node.
        storage_options, pq_node.partition_names, dnf_filter_str,
        expr_filter_str, extra_args, parallel, meta_head_only_info, pq_node
        .index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col)
    rqq__huk = typemap[pq_node.file_name.name]
    umdl__odg = (rqq__huk,) + tuple(typemap[qjd__yhfnf.name] for qjd__yhfnf in
        epywg__uoak)
    xhbvp__pmt = compile_to_numba_ir(ttp__judub, {'_pq_reader_py':
        xgte__axtzb}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        umdl__odg, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(xhbvp__pmt, [pq_node.file_name] + epywg__uoak)
    iuf__kkygi = xhbvp__pmt.body[:-3]
    if meta_head_only_info:
        iuf__kkygi[-3].target = meta_head_only_info[1]
    iuf__kkygi[-2].target = pq_node.out_vars[0]
    iuf__kkygi[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        iuf__kkygi.pop(-1)
    elif not pq_node.out_used_cols:
        iuf__kkygi.pop(-2)
    return iuf__kkygi


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    bgbg__xyj = get_overload_const_str(dnf_filter_str)
    ilsz__loi = get_overload_const_str(expr_filter_str)
    aolpk__lkd = ', '.join(f'f{ykyx__omcl}' for ykyx__omcl in range(len(
        var_tup)))
    derer__sgz = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        derer__sgz += f'  {aolpk__lkd}, = var_tup\n'
    derer__sgz += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    derer__sgz += f'    dnf_filters_py = {bgbg__xyj}\n'
    derer__sgz += f'    expr_filters_py = {ilsz__loi}\n'
    derer__sgz += '  return (dnf_filters_py, expr_filters_py)\n'
    ciul__ivx = {}
    exec(derer__sgz, globals(), ciul__ivx)
    return ciul__ivx['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col):
    xzwj__zanl = next_label()
    tsn__pfj = ',' if extra_args else ''
    derer__sgz = f'def pq_reader_py(fname,{extra_args}):\n'
    derer__sgz += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    derer__sgz += f"    ev.add_attribute('g_fname', fname)\n"
    derer__sgz += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{tsn__pfj}))
"""
    derer__sgz += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    derer__sgz += (
        f'    storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    soq__wtd = not out_used_cols
    hks__erqj = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    kfhp__bvfp = {c: ykyx__omcl for ykyx__omcl, c in enumerate(col_indices)}
    skxjl__ovdry = {c: ykyx__omcl for ykyx__omcl, c in enumerate(hks__erqj)}
    stgw__afcx = []
    gztbe__gvf = set()
    opyis__awo = partition_names + [input_file_name_col]
    for ykyx__omcl in out_used_cols:
        if hks__erqj[ykyx__omcl] not in opyis__awo:
            stgw__afcx.append(col_indices[ykyx__omcl])
        elif not input_file_name_col or hks__erqj[ykyx__omcl
            ] != input_file_name_col:
            gztbe__gvf.add(col_indices[ykyx__omcl])
    if index_column_index is not None:
        stgw__afcx.append(index_column_index)
    stgw__afcx = sorted(stgw__afcx)
    keq__ccjo = {c: ykyx__omcl for ykyx__omcl, c in enumerate(stgw__afcx)}
    bafrb__asnnf = [(int(is_nullable(out_types[kfhp__bvfp[xrb__ajzro]])) if
        xrb__ajzro != index_column_index else int(is_nullable(
        index_column_type))) for xrb__ajzro in stgw__afcx]
    str_as_dict_cols = []
    for xrb__ajzro in stgw__afcx:
        if xrb__ajzro == index_column_index:
            vjuyp__blqiy = index_column_type
        else:
            vjuyp__blqiy = out_types[kfhp__bvfp[xrb__ajzro]]
        if vjuyp__blqiy == dict_str_arr_type:
            str_as_dict_cols.append(xrb__ajzro)
    gfl__owubc = []
    snby__hahog = {}
    mljv__jepi = []
    opi__wwp = []
    for ykyx__omcl, gtjgc__hruz in enumerate(partition_names):
        try:
            giiwr__kmefs = skxjl__ovdry[gtjgc__hruz]
            if col_indices[giiwr__kmefs] not in gztbe__gvf:
                continue
        except (KeyError, ValueError) as ybgd__izt:
            continue
        snby__hahog[gtjgc__hruz] = len(gfl__owubc)
        gfl__owubc.append(gtjgc__hruz)
        mljv__jepi.append(ykyx__omcl)
        kllwp__fedc = out_types[giiwr__kmefs].dtype
        und__gpx = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            kllwp__fedc)
        opi__wwp.append(numba_to_c_type(und__gpx))
    derer__sgz += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    derer__sgz += f'    out_table = pq_read(\n'
    derer__sgz += f'        fname_py, {is_parallel},\n'
    derer__sgz += f'        dnf_filters, expr_filters,\n'
    derer__sgz += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{xzwj__zanl}.ctypes,
"""
    derer__sgz += f'        {len(stgw__afcx)},\n'
    derer__sgz += f'        nullable_cols_arr_{xzwj__zanl}.ctypes,\n'
    if len(mljv__jepi) > 0:
        derer__sgz += (
            f'        np.array({mljv__jepi}, dtype=np.int32).ctypes,\n')
        derer__sgz += f'        np.array({opi__wwp}, dtype=np.int32).ctypes,\n'
        derer__sgz += f'        {len(mljv__jepi)},\n'
    else:
        derer__sgz += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        derer__sgz += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        derer__sgz += f'        0, 0,\n'
    derer__sgz += f'        total_rows_np.ctypes,\n'
    derer__sgz += f'        {input_file_name_col is not None},\n'
    derer__sgz += f'    )\n'
    derer__sgz += f'    check_and_propagate_cpp_exception()\n'
    lljx__iall = 'None'
    zjihx__krscl = index_column_type
    uklqe__xge = TableType(tuple(out_types))
    if soq__wtd:
        uklqe__xge = types.none
    if index_column_index is not None:
        afv__ribjw = keq__ccjo[index_column_index]
        lljx__iall = (
            f'info_to_array(info_from_table(out_table, {afv__ribjw}), index_arr_type)'
            )
    derer__sgz += f'    index_arr = {lljx__iall}\n'
    if soq__wtd:
        wyv__kkwro = None
    else:
        wyv__kkwro = []
        rgt__wjv = 0
        yuep__fss = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for ykyx__omcl, xiy__lzkw in enumerate(col_indices):
            if rgt__wjv < len(out_used_cols) and ykyx__omcl == out_used_cols[
                rgt__wjv]:
                pzg__hklh = col_indices[ykyx__omcl]
                if yuep__fss and pzg__hklh == yuep__fss:
                    wyv__kkwro.append(len(stgw__afcx) + len(gfl__owubc))
                elif pzg__hklh in gztbe__gvf:
                    uvwal__wpi = hks__erqj[ykyx__omcl]
                    wyv__kkwro.append(len(stgw__afcx) + snby__hahog[uvwal__wpi]
                        )
                else:
                    wyv__kkwro.append(keq__ccjo[xiy__lzkw])
                rgt__wjv += 1
            else:
                wyv__kkwro.append(-1)
        wyv__kkwro = np.array(wyv__kkwro, dtype=np.int64)
    if soq__wtd:
        derer__sgz += '    T = None\n'
    else:
        derer__sgz += f"""    T = cpp_table_to_py_table(out_table, table_idx_{xzwj__zanl}, py_table_type_{xzwj__zanl})
"""
    derer__sgz += f'    delete_table(out_table)\n'
    derer__sgz += f'    total_rows = total_rows_np[0]\n'
    derer__sgz += f'    ev.finalize()\n'
    derer__sgz += f'    return (total_rows, T, index_arr)\n'
    ciul__ivx = {}
    bepum__dxol = {f'py_table_type_{xzwj__zanl}': uklqe__xge,
        f'table_idx_{xzwj__zanl}': wyv__kkwro,
        f'selected_cols_arr_{xzwj__zanl}': np.array(stgw__afcx, np.int32),
        f'nullable_cols_arr_{xzwj__zanl}': np.array(bafrb__asnnf, np.int32),
        'index_arr_type': zjihx__krscl, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(derer__sgz, bepum__dxol, ciul__ivx)
    xgte__axtzb = ciul__ivx['pq_reader_py']
    cbgtg__dsit = numba.njit(xgte__axtzb, no_cpython_wrapper=True)
    return cbgtg__dsit


import pyarrow as pa
_pa_numba_typ_map = {pa.bool_(): types.bool_, pa.int8(): types.int8, pa.
    int16(): types.int16, pa.int32(): types.int32, pa.int64(): types.int64,
    pa.uint8(): types.uint8, pa.uint16(): types.uint16, pa.uint32(): types.
    uint32, pa.uint64(): types.uint64, pa.float32(): types.float32, pa.
    float64(): types.float64, pa.string(): string_type, pa.binary():
    bytes_type, pa.date32(): datetime_date_type, pa.date64(): types.
    NPDatetime('ns'), null(): string_type}


def get_arrow_timestamp_type(pa_ts_typ):
    ougy__fftbm = 'ns', 'us', 'ms', 's'
    if pa_ts_typ.unit not in ougy__fftbm:
        return types.Array(bodo.datetime64ns, 1, 'C'), False
    elif pa_ts_typ.tz is not None:
        olpyk__zmu = pa_ts_typ.to_pandas_dtype().tz
        jpkn__hzos = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(
            olpyk__zmu)
        return bodo.DatetimeArrayType(jpkn__hzos), True
    else:
        return types.Array(bodo.datetime64ns, 1, 'C'), True


def _get_numba_typ_from_pa_typ(pa_typ, is_index, nullable_from_metadata,
    category_info, str_as_dict=False):
    if isinstance(pa_typ.type, pa.ListType):
        kcv__hcgqe, lljdv__pvr = _get_numba_typ_from_pa_typ(pa_typ.type.
            value_field, is_index, nullable_from_metadata, category_info)
        return ArrayItemArrayType(kcv__hcgqe), lljdv__pvr
    if isinstance(pa_typ.type, pa.StructType):
        bym__bdgtk = []
        piz__qrpu = []
        lljdv__pvr = True
        for crl__bep in pa_typ.flatten():
            piz__qrpu.append(crl__bep.name.split('.')[-1])
            tph__hzpew, otydt__cblw = _get_numba_typ_from_pa_typ(crl__bep,
                is_index, nullable_from_metadata, category_info)
            bym__bdgtk.append(tph__hzpew)
            lljdv__pvr = lljdv__pvr and otydt__cblw
        return StructArrayType(tuple(bym__bdgtk), tuple(piz__qrpu)), lljdv__pvr
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
        ujxfl__kvtt = _pa_numba_typ_map[pa_typ.type.index_type]
        pipjy__lsc = PDCategoricalDtype(category_info[pa_typ.name], bodo.
            string_type, pa_typ.type.ordered, int_type=ujxfl__kvtt)
        return CategoricalArrayType(pipjy__lsc), True
    if isinstance(pa_typ.type, pa.lib.TimestampType):
        return get_arrow_timestamp_type(pa_typ.type)
    elif pa_typ.type in _pa_numba_typ_map:
        tjis__bvi = _pa_numba_typ_map[pa_typ.type]
        lljdv__pvr = True
    else:
        raise BodoError('Arrow data type {} not supported yet'.format(
            pa_typ.type))
    if tjis__bvi == datetime_date_type:
        return datetime_date_array_type, lljdv__pvr
    if tjis__bvi == bytes_type:
        return binary_array_type, lljdv__pvr
    kcv__hcgqe = (string_array_type if tjis__bvi == string_type else types.
        Array(tjis__bvi, 1, 'C'))
    if tjis__bvi == types.bool_:
        kcv__hcgqe = boolean_array
    if nullable_from_metadata is not None:
        qiqao__bbhh = nullable_from_metadata
    else:
        qiqao__bbhh = use_nullable_int_arr
    if qiqao__bbhh and not is_index and isinstance(tjis__bvi, types.Integer
        ) and pa_typ.nullable:
        kcv__hcgqe = IntegerArrayType(tjis__bvi)
    return kcv__hcgqe, lljdv__pvr


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
        for mrbib__dpd in self.partition_names:
            self.schema = self.schema.remove(self.schema.get_field_index(
                mrbib__dpd))
        self.pieces = [ParquetPiece(frag, pa_pq_dataset.partitioning, self.
            partition_names) for frag in pa_pq_dataset._dataset.
            get_fragments(filter=pa_pq_dataset._filter_expression)]

    def set_fs(self, fs):
        self.filesystem = fs
        for mphic__nee in self.pieces:
            mphic__nee.filesystem = fs


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
            self.partition_keys = [(gtjgc__hruz, partitioning.dictionaries[
                ykyx__omcl].index(self.partition_keys[gtjgc__hruz]).as_py()
                ) for ykyx__omcl, gtjgc__hruz in enumerate(partition_names)]

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
        dji__jhz = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    xmxji__ztub = MPI.COMM_WORLD
    if isinstance(fpath, list):
        mtk__eouv = urlparse(fpath[0])
        protocol = mtk__eouv.scheme
        ehi__dbcgc = mtk__eouv.netloc
        for ykyx__omcl in range(len(fpath)):
            axr__afvs = fpath[ykyx__omcl]
            qsljw__hic = urlparse(axr__afvs)
            if qsljw__hic.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if qsljw__hic.netloc != ehi__dbcgc:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[ykyx__omcl] = axr__afvs.rstrip('/')
    else:
        mtk__eouv = urlparse(fpath)
        protocol = mtk__eouv.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as ybgd__izt:
            dlurt__hgyt = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(dlurt__hgyt)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as ybgd__izt:
            dlurt__hgyt = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
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
            qqwam__aga = gcsfs.GCSFileSystem(token=None)
            fs.append(PyFileSystem(FSSpecHandler(qqwam__aga)))
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
            tnthi__uuex = fs.glob(path)
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(tnthi__uuex) == 0:
            raise BodoError('No files found matching glob pattern')
        return tnthi__uuex
    jmqoq__bwh = False
    if get_row_counts:
        ztnjk__vgsri = getfs(parallel=True)
        jmqoq__bwh = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        aym__zdn = 1
        jnyu__iwd = os.cpu_count()
        if jnyu__iwd is not None and jnyu__iwd > 1:
            aym__zdn = jnyu__iwd // 2
        try:
            if get_row_counts:
                dbhrz__fpgly = tracing.Event('pq.ParquetDataset',
                    is_parallel=False)
                if tracing.is_tracing():
                    dbhrz__fpgly.add_attribute('g_dnf_filter', str(dnf_filters)
                        )
            ytudk__ulau = pa.io_thread_count()
            pa.set_io_thread_count(aym__zdn)
            prefix = ''
            if protocol == 's3':
                prefix = 's3://'
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{mtk__eouv.netloc}'
            if prefix:
                if isinstance(fpath, list):
                    dqv__etes = [axr__afvs[len(prefix):] for axr__afvs in fpath
                        ]
                else:
                    dqv__etes = fpath[len(prefix):]
            else:
                dqv__etes = fpath
            if isinstance(dqv__etes, list):
                pohrd__ajga = []
                for mphic__nee in dqv__etes:
                    if has_magic(mphic__nee):
                        pohrd__ajga += glob(protocol, getfs(), mphic__nee)
                    else:
                        pohrd__ajga.append(mphic__nee)
                dqv__etes = pohrd__ajga
            elif has_magic(dqv__etes):
                dqv__etes = glob(protocol, getfs(), dqv__etes)
            kokft__yzycj = pq.ParquetDataset(dqv__etes, filesystem=getfs(),
                filters=None, use_legacy_dataset=False, partitioning=
                partitioning)
            if dnf_filters is not None:
                kokft__yzycj._filters = dnf_filters
                kokft__yzycj._filter_expression = pq._filters_to_expression(
                    dnf_filters)
            wsi__feerr = len(kokft__yzycj.files)
            kokft__yzycj = ParquetDataset(kokft__yzycj, prefix)
            pa.set_io_thread_count(ytudk__ulau)
            if typing_pa_schema:
                kokft__yzycj.schema = typing_pa_schema
            if get_row_counts:
                if dnf_filters is not None:
                    dbhrz__fpgly.add_attribute('num_pieces_before_filter',
                        wsi__feerr)
                    dbhrz__fpgly.add_attribute('num_pieces_after_filter',
                        len(kokft__yzycj.pieces))
                dbhrz__fpgly.finalize()
        except Exception as srgxm__dsc:
            if isinstance(srgxm__dsc, IsADirectoryError):
                srgxm__dsc = BodoError(list_of_files_error_msg)
            elif isinstance(fpath, list) and isinstance(srgxm__dsc, (
                OSError, FileNotFoundError)):
                srgxm__dsc = BodoError(str(srgxm__dsc) +
                    list_of_files_error_msg)
            else:
                srgxm__dsc = BodoError(
                    f"""error from pyarrow: {type(srgxm__dsc).__name__}: {str(srgxm__dsc)}
"""
                    )
            xmxji__ztub.bcast(srgxm__dsc)
            raise srgxm__dsc
        if get_row_counts:
            urdyb__bqmh = tracing.Event('bcast dataset')
        xmxji__ztub.bcast(kokft__yzycj)
    else:
        if get_row_counts:
            urdyb__bqmh = tracing.Event('bcast dataset')
        kokft__yzycj = xmxji__ztub.bcast(None)
        if isinstance(kokft__yzycj, Exception):
            hhvnu__jkeoc = kokft__yzycj
            raise hhvnu__jkeoc
    kokft__yzycj.set_fs(getfs())
    if get_row_counts:
        urdyb__bqmh.finalize()
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = jmqoq__bwh = False
    if get_row_counts or jmqoq__bwh:
        if get_row_counts and tracing.is_tracing():
            vchb__zau = tracing.Event('get_row_counts')
            vchb__zau.add_attribute('g_num_pieces', len(kokft__yzycj.pieces))
            vchb__zau.add_attribute('g_expr_filters', str(expr_filters))
        ddt__jms = 0.0
        num_pieces = len(kokft__yzycj.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        qipkg__zit = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        tdiui__nxfh = 0
        msuut__kejx = 0
        bemzn__nptcc = 0
        poyzu__bfe = True
        if expr_filters is not None:
            import random
            random.seed(37)
            bnjr__afqy = random.sample(kokft__yzycj.pieces, k=len(
                kokft__yzycj.pieces))
        else:
            bnjr__afqy = kokft__yzycj.pieces
        fpaths = [mphic__nee.path for mphic__nee in bnjr__afqy[start:
            qipkg__zit]]
        aym__zdn = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(aym__zdn)
        pa.set_cpu_count(aym__zdn)
        hhvnu__jkeoc = None
        try:
            koge__guubk = ds.dataset(fpaths, filesystem=kokft__yzycj.
                filesystem, partitioning=ds.partitioning(flavor='hive') if
                kokft__yzycj.partition_names else None)
            for xnksb__irvo, frag in zip(bnjr__afqy[start:qipkg__zit],
                koge__guubk.get_fragments()):
                if jmqoq__bwh:
                    jeo__uixg = frag.metadata.schema.to_arrow_schema()
                    juhtx__zwvje = set(jeo__uixg.names)
                    vvpv__oesy = set(kokft__yzycj.schema.names)
                    if vvpv__oesy != juhtx__zwvje:
                        zbn__mgf = juhtx__zwvje - vvpv__oesy
                        kunej__rvbv = vvpv__oesy - juhtx__zwvje
                        ymoi__jqvbq = (
                            f'Schema in {xnksb__irvo} was different.\n')
                        if zbn__mgf:
                            ymoi__jqvbq += f"""File contains column(s) {zbn__mgf} not found in other files in the dataset.
"""
                        if kunej__rvbv:
                            ymoi__jqvbq += f"""File missing column(s) {kunej__rvbv} found in other files in the dataset.
"""
                        raise BodoError(ymoi__jqvbq)
                    try:
                        kokft__yzycj.schema = pa.unify_schemas([
                            kokft__yzycj.schema, jeo__uixg])
                    except Exception as srgxm__dsc:
                        ymoi__jqvbq = (
                            f'Schema in {xnksb__irvo} was different.\n' +
                            str(srgxm__dsc))
                        raise BodoError(ymoi__jqvbq)
                drk__cmf = time.time()
                stzdk__astlk = frag.scanner(schema=koge__guubk.schema,
                    filter=expr_filters, use_threads=True).count_rows()
                ddt__jms += time.time() - drk__cmf
                xnksb__irvo._bodo_num_rows = stzdk__astlk
                tdiui__nxfh += stzdk__astlk
                msuut__kejx += frag.num_row_groups
                bemzn__nptcc += sum(ejwsb__lyk.total_byte_size for
                    ejwsb__lyk in frag.row_groups)
        except Exception as srgxm__dsc:
            hhvnu__jkeoc = srgxm__dsc
        if xmxji__ztub.allreduce(hhvnu__jkeoc is not None, op=MPI.LOR):
            for hhvnu__jkeoc in xmxji__ztub.allgather(hhvnu__jkeoc):
                if hhvnu__jkeoc:
                    if isinstance(fpath, list) and isinstance(hhvnu__jkeoc,
                        (OSError, FileNotFoundError)):
                        raise BodoError(str(hhvnu__jkeoc) +
                            list_of_files_error_msg)
                    raise hhvnu__jkeoc
        if jmqoq__bwh:
            poyzu__bfe = xmxji__ztub.allreduce(poyzu__bfe, op=MPI.LAND)
            if not poyzu__bfe:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            kokft__yzycj._bodo_total_rows = xmxji__ztub.allreduce(tdiui__nxfh,
                op=MPI.SUM)
            bsxm__bfsgy = xmxji__ztub.allreduce(msuut__kejx, op=MPI.SUM)
            glor__vvj = xmxji__ztub.allreduce(bemzn__nptcc, op=MPI.SUM)
            whv__hyeun = np.array([mphic__nee._bodo_num_rows for mphic__nee in
                kokft__yzycj.pieces])
            whv__hyeun = xmxji__ztub.allreduce(whv__hyeun, op=MPI.SUM)
            for mphic__nee, gkeww__jbq in zip(kokft__yzycj.pieces, whv__hyeun):
                mphic__nee._bodo_num_rows = gkeww__jbq
            if is_parallel and bodo.get_rank(
                ) == 0 and bsxm__bfsgy < bodo.get_size() and bsxm__bfsgy != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({bsxm__bfsgy}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if bsxm__bfsgy == 0:
                wxo__ccm = 0
            else:
                wxo__ccm = glor__vvj // bsxm__bfsgy
            if (bodo.get_rank() == 0 and glor__vvj >= 20 * 1048576 and 
                wxo__ccm < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({wxo__ccm} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                vchb__zau.add_attribute('g_total_num_row_groups', bsxm__bfsgy)
                vchb__zau.add_attribute('total_scan_time', ddt__jms)
                lbbo__sqvy = np.array([mphic__nee._bodo_num_rows for
                    mphic__nee in kokft__yzycj.pieces])
                vxw__dbcfz = np.percentile(lbbo__sqvy, [25, 50, 75])
                vchb__zau.add_attribute('g_row_counts_min', lbbo__sqvy.min())
                vchb__zau.add_attribute('g_row_counts_Q1', vxw__dbcfz[0])
                vchb__zau.add_attribute('g_row_counts_median', vxw__dbcfz[1])
                vchb__zau.add_attribute('g_row_counts_Q3', vxw__dbcfz[2])
                vchb__zau.add_attribute('g_row_counts_max', lbbo__sqvy.max())
                vchb__zau.add_attribute('g_row_counts_mean', lbbo__sqvy.mean())
                vchb__zau.add_attribute('g_row_counts_std', lbbo__sqvy.std())
                vchb__zau.add_attribute('g_row_counts_sum', lbbo__sqvy.sum())
                vchb__zau.finalize()
    if read_categories:
        _add_categories_to_pq_dataset(kokft__yzycj)
    if get_row_counts:
        dji__jhz.finalize()
    if jmqoq__bwh and is_parallel:
        if tracing.is_tracing():
            vvjp__yfln = tracing.Event('unify_schemas_across_ranks')
        hhvnu__jkeoc = None
        try:
            kokft__yzycj.schema = xmxji__ztub.allreduce(kokft__yzycj.schema,
                bodo.io.helpers.pa_schema_unify_mpi_op)
        except Exception as srgxm__dsc:
            hhvnu__jkeoc = srgxm__dsc
        if tracing.is_tracing():
            vvjp__yfln.finalize()
        if xmxji__ztub.allreduce(hhvnu__jkeoc is not None, op=MPI.LOR):
            for hhvnu__jkeoc in xmxji__ztub.allgather(hhvnu__jkeoc):
                if hhvnu__jkeoc:
                    ymoi__jqvbq = (
                        f'Schema in some files were different.\n' + str(
                        hhvnu__jkeoc))
                    raise BodoError(ymoi__jqvbq)
    return kokft__yzycj


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, filesystem, str_as_dict_cols, start_offset,
    rows_to_read, has_partitions, schema):
    import pyarrow as pa
    jnyu__iwd = os.cpu_count()
    if jnyu__iwd is None or jnyu__iwd == 0:
        jnyu__iwd = 2
    iwi__imhuy = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), jnyu__iwd)
    fxznq__wpaad = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)),
        jnyu__iwd)
    if is_parallel and len(fpaths) > fxznq__wpaad and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(fxznq__wpaad)
        pa.set_cpu_count(fxznq__wpaad)
    else:
        pa.set_io_thread_count(iwi__imhuy)
        pa.set_cpu_count(iwi__imhuy)
    qiwr__ltgjz = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    kokft__yzycj = ds.dataset(fpaths, filesystem=filesystem, partitioning=
        ds.partitioning(flavor='hive') if has_partitions else None, format=
        qiwr__ltgjz)
    guq__pzpl = set(str_as_dict_cols)
    oab__uedbt = schema.names
    for ykyx__omcl, name in enumerate(oab__uedbt):
        if name in guq__pzpl:
            gjaa__uwkqd = schema.field(ykyx__omcl)
            yjwy__srqnh = pa.field(name, pa.dictionary(pa.int32(),
                gjaa__uwkqd.type), gjaa__uwkqd.nullable)
            schema = schema.remove(ykyx__omcl).insert(ykyx__omcl, yjwy__srqnh)
    kokft__yzycj = kokft__yzycj.replace_schema(pa.unify_schemas([
        kokft__yzycj.schema, schema]))
    col_names = kokft__yzycj.schema.names
    ulem__iqlf = [col_names[nfvqw__jptts] for nfvqw__jptts in selected_fields]
    bka__dflzy = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if bka__dflzy and expr_filters is None:
        sltte__eifa = []
        tzgy__bolwl = 0
        xfa__vcgg = 0
        for frag in kokft__yzycj.get_fragments():
            pmgiy__vfuk = []
            for ejwsb__lyk in frag.row_groups:
                qkj__ackvn = ejwsb__lyk.num_rows
                if start_offset < tzgy__bolwl + qkj__ackvn:
                    if xfa__vcgg == 0:
                        lktb__hpb = start_offset - tzgy__bolwl
                        wblo__uycdn = min(qkj__ackvn - lktb__hpb, rows_to_read)
                    else:
                        wblo__uycdn = min(qkj__ackvn, rows_to_read - xfa__vcgg)
                    xfa__vcgg += wblo__uycdn
                    pmgiy__vfuk.append(ejwsb__lyk.id)
                tzgy__bolwl += qkj__ackvn
                if xfa__vcgg == rows_to_read:
                    break
            sltte__eifa.append(frag.subset(row_group_ids=pmgiy__vfuk))
            if xfa__vcgg == rows_to_read:
                break
        kokft__yzycj = ds.FileSystemDataset(sltte__eifa, kokft__yzycj.
            schema, qiwr__ltgjz, filesystem=kokft__yzycj.filesystem)
        start_offset = lktb__hpb
    yejlu__wskil = kokft__yzycj.scanner(columns=ulem__iqlf, filter=
        expr_filters, use_threads=True).to_reader()
    return kokft__yzycj, yejlu__wskil, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema
    sbblj__wdo = [c for c in pa_schema.names if isinstance(pa_schema.field(
        c).type, pa.DictionaryType) and c not in pq_dataset.partition_names]
    if len(sbblj__wdo) == 0:
        pq_dataset._category_info = {}
        return
    xmxji__ztub = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            yex__wua = pq_dataset.pieces[0].frag.head(100, columns=sbblj__wdo)
            category_info = {c: tuple(yex__wua.column(c).chunk(0).
                dictionary.to_pylist()) for c in sbblj__wdo}
            del yex__wua
        except Exception as srgxm__dsc:
            xmxji__ztub.bcast(srgxm__dsc)
            raise srgxm__dsc
        xmxji__ztub.bcast(category_info)
    else:
        category_info = xmxji__ztub.bcast(None)
        if isinstance(category_info, Exception):
            hhvnu__jkeoc = category_info
            raise hhvnu__jkeoc
    pq_dataset._category_info = category_info


def get_pandas_metadata(schema, num_pieces):
    cguvx__dhi = None
    nullable_from_metadata = defaultdict(lambda : None)
    tmq__nik = b'pandas'
    if schema.metadata is not None and tmq__nik in schema.metadata:
        import json
        qvfw__cuuvr = json.loads(schema.metadata[tmq__nik].decode('utf8'))
        nyv__ymldp = len(qvfw__cuuvr['index_columns'])
        if nyv__ymldp > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        cguvx__dhi = qvfw__cuuvr['index_columns'][0] if nyv__ymldp else None
        if not isinstance(cguvx__dhi, str) and not isinstance(cguvx__dhi, dict
            ):
            cguvx__dhi = None
        for ngh__drttr in qvfw__cuuvr['columns']:
            tpn__ehq = ngh__drttr['name']
            if ngh__drttr['pandas_type'].startswith('int'
                ) and tpn__ehq is not None:
                if ngh__drttr['numpy_type'].startswith('Int'):
                    nullable_from_metadata[tpn__ehq] = True
                else:
                    nullable_from_metadata[tpn__ehq] = False
    return cguvx__dhi, nullable_from_metadata


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for tpn__ehq in pa_schema.names:
        crl__bep = pa_schema.field(tpn__ehq)
        if crl__bep.type == pa.string():
            str_columns.append(tpn__ehq)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    xmxji__ztub = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        bnjr__afqy = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        bnjr__afqy = pq_dataset.pieces
    kzq__qdo = np.zeros(len(str_columns), dtype=np.int64)
    oez__akik = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(bnjr__afqy):
        xnksb__irvo = bnjr__afqy[bodo.get_rank()]
        try:
            metadata = xnksb__irvo.metadata
            for ykyx__omcl in range(xnksb__irvo.num_row_groups):
                for rgt__wjv, tpn__ehq in enumerate(str_columns):
                    ymkhq__efql = pa_schema.get_field_index(tpn__ehq)
                    kzq__qdo[rgt__wjv] += metadata.row_group(ykyx__omcl
                        ).column(ymkhq__efql).total_uncompressed_size
            fimt__vuqc = metadata.num_rows
        except Exception as srgxm__dsc:
            if isinstance(srgxm__dsc, (OSError, FileNotFoundError)):
                fimt__vuqc = 0
            else:
                raise
    else:
        fimt__vuqc = 0
    arhro__kjfza = xmxji__ztub.allreduce(fimt__vuqc, op=MPI.SUM)
    if arhro__kjfza == 0:
        return set()
    xmxji__ztub.Allreduce(kzq__qdo, oez__akik, op=MPI.SUM)
    ixfd__uubx = oez__akik / arhro__kjfza
    str_as_dict = set()
    for ykyx__omcl, reiww__kxe in enumerate(ixfd__uubx):
        if reiww__kxe < READ_STR_AS_DICT_THRESHOLD:
            tpn__ehq = str_columns[ykyx__omcl][0]
            str_as_dict.add(tpn__ehq)
    return str_as_dict


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    ftq__aabts = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = pq_dataset.partition_names
    pa_schema = pq_dataset.schema
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    ikd__xacmz = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    jokza__sqkws = read_as_dict_cols - ikd__xacmz
    if len(jokza__sqkws) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {jokza__sqkws}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(ikd__xacmz)
    ikd__xacmz = ikd__xacmz - read_as_dict_cols
    str_columns = [hzff__bwq for hzff__bwq in str_columns if hzff__bwq in
        ikd__xacmz]
    str_as_dict: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    str_as_dict.update(read_as_dict_cols)
    col_names = pa_schema.names
    cguvx__dhi, nullable_from_metadata = get_pandas_metadata(pa_schema,
        num_pieces)
    rpe__xdwj = []
    wuum__nof = []
    nreu__euo = []
    for ykyx__omcl, c in enumerate(col_names):
        if c in partition_names:
            continue
        crl__bep = pa_schema.field(c)
        tjis__bvi, lljdv__pvr = _get_numba_typ_from_pa_typ(crl__bep, c ==
            cguvx__dhi, nullable_from_metadata[c], pq_dataset.
            _category_info, str_as_dict=c in str_as_dict)
        rpe__xdwj.append(tjis__bvi)
        wuum__nof.append(lljdv__pvr)
        nreu__euo.append(crl__bep.type)
    if partition_names:
        col_names += partition_names
        rpe__xdwj += [_get_partition_cat_dtype(pq_dataset.
            partitioning_dictionaries[ykyx__omcl]) for ykyx__omcl in range(
            len(partition_names))]
        wuum__nof.extend([True] * len(partition_names))
        nreu__euo.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        rpe__xdwj += [dict_str_arr_type]
        wuum__nof.append(True)
        nreu__euo.append(None)
    raxqy__tduqs = {c: ykyx__omcl for ykyx__omcl, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in raxqy__tduqs:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if cguvx__dhi and not isinstance(cguvx__dhi, dict
        ) and cguvx__dhi not in selected_columns:
        selected_columns.append(cguvx__dhi)
    col_names = selected_columns
    col_indices = []
    ftq__aabts = []
    brey__bshm = []
    hte__gaw = []
    for ykyx__omcl, c in enumerate(col_names):
        pzg__hklh = raxqy__tduqs[c]
        col_indices.append(pzg__hklh)
        ftq__aabts.append(rpe__xdwj[pzg__hklh])
        if not wuum__nof[pzg__hklh]:
            brey__bshm.append(ykyx__omcl)
            hte__gaw.append(nreu__euo[pzg__hklh])
    return (col_names, ftq__aabts, cguvx__dhi, col_indices, partition_names,
        brey__bshm, hte__gaw)


def _get_partition_cat_dtype(dictionary):
    assert dictionary is not None
    xpi__hzb = dictionary.to_pandas()
    dphu__icae = bodo.typeof(xpi__hzb).dtype
    if isinstance(dphu__icae, types.Integer):
        pipjy__lsc = PDCategoricalDtype(tuple(xpi__hzb), dphu__icae, False,
            int_type=dphu__icae)
    else:
        pipjy__lsc = PDCategoricalDtype(tuple(xpi__hzb), dphu__icae, False)
    return CategoricalArrayType(pipjy__lsc)


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
        ukjp__nmygl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        die__zrdd = cgutils.get_or_insert_function(builder.module,
            ukjp__nmygl, name='pq_write')
        builder.call(die__zrdd, args)
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
        ukjp__nmygl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        die__zrdd = cgutils.get_or_insert_function(builder.module,
            ukjp__nmygl, name='pq_write_partitioned')
        builder.call(die__zrdd, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64), codegen
