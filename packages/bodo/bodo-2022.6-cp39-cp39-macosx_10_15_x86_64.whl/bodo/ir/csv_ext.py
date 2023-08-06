from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from mpi4py import MPI
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import Table, TableType
from bodo.io.fs_io import get_storage_options_pyobject, storage_options_dict_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.table_column_del_pass import ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import sanitize_varname


class CsvReader(ir.Stmt):

    def __init__(self, file_name, df_out, sep, df_colnames, out_vars,
        out_types, usecols, loc, header, compression, nrows, skiprows,
        chunksize, is_skiprows_list, low_memory, escapechar,
        storage_options=None, index_column_index=None, index_column_typ=
        types.none):
        self.connector_typ = 'csv'
        self.file_name = file_name
        self.df_out = df_out
        self.sep = sep
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.usecols = usecols
        self.loc = loc
        self.skiprows = skiprows
        self.nrows = nrows
        self.header = header
        self.compression = compression
        self.chunksize = chunksize
        self.is_skiprows_list = is_skiprows_list
        self.pd_low_memory = low_memory
        self.escapechar = escapechar
        self.storage_options = storage_options
        self.index_column_index = index_column_index
        self.index_column_typ = index_column_typ
        self.out_used_cols = list(range(len(usecols)))

    def __repr__(self):
        return (
            '{} = ReadCsv(file={}, col_names={}, types={}, vars={}, nrows={}, skiprows={}, chunksize={}, is_skiprows_list={}, pd_low_memory={}, escapechar={}, storage_options={}, index_column_index={}, index_colum_typ = {}, out_used_colss={})'
            .format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars, self.nrows, self.skiprows, self.
            chunksize, self.is_skiprows_list, self.pd_low_memory, self.
            escapechar, self.storage_options, self.index_column_index, self
            .index_column_typ, self.out_used_cols))


def check_node_typing(node, typemap):
    pzm__vpya = typemap[node.file_name.name]
    if types.unliteral(pzm__vpya) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {pzm__vpya}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        xkrui__nan = typemap[node.skiprows.name]
        if isinstance(xkrui__nan, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(xkrui__nan, types.Integer) and not (isinstance(
            xkrui__nan, (types.List, types.Tuple)) and isinstance(
            xkrui__nan.dtype, types.Integer)) and not isinstance(xkrui__nan,
            (types.LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {xkrui__nan}."
                , loc=node.skiprows.loc)
        elif isinstance(xkrui__nan, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        biwbt__wew = typemap[node.nrows.name]
        if not isinstance(biwbt__wew, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {biwbt__wew}."
                , loc=node.nrows.loc)


import llvmlite.binding as ll
from bodo.io import csv_cpp
ll.add_symbol('csv_file_chunk_reader', csv_cpp.csv_file_chunk_reader)
csv_file_chunk_reader = types.ExternalFunction('csv_file_chunk_reader',
    bodo.ir.connector.stream_reader_type(types.voidptr, types.bool_, types.
    voidptr, types.int64, types.bool_, types.voidptr, types.voidptr,
    storage_options_dict_type, types.int64, types.bool_, types.int64, types
    .bool_))


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        zled__ddocc = csv_node.out_vars[0]
        if zled__ddocc.name not in lives:
            return None
    else:
        wjs__rcr = csv_node.out_vars[0]
        buw__wji = csv_node.out_vars[1]
        if wjs__rcr.name not in lives and buw__wji.name not in lives:
            return None
        elif buw__wji.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif wjs__rcr.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    xkrui__nan = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            ihq__lls = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            mrja__avlh = csv_node.loc.strformat()
            rpej__tuwn = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', ihq__lls,
                mrja__avlh, rpej__tuwn)
            guxmi__vgz = csv_node.out_types[0].yield_type.data
            esq__vyyj = [ebr__zvatx for ihk__hrxjc, ebr__zvatx in enumerate
                (csv_node.df_colnames) if isinstance(guxmi__vgz[ihk__hrxjc],
                bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if esq__vyyj:
                jipkt__chi = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    jipkt__chi, mrja__avlh, esq__vyyj)
        if array_dists is not None:
            sewsi__xtlvp = csv_node.out_vars[0].name
            parallel = array_dists[sewsi__xtlvp] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        vku__iraa = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        vku__iraa += f'    reader = _csv_reader_init(fname, nrows, skiprows)\n'
        vku__iraa += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        uee__yor = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(vku__iraa, {}, uee__yor)
        tiq__ubllz = uee__yor['csv_iterator_impl']
        hosrd__zfq = 'def csv_reader_init(fname, nrows, skiprows):\n'
        hosrd__zfq += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        hosrd__zfq += '  return f_reader\n'
        exec(hosrd__zfq, globals(), uee__yor)
        pkp__vaaqv = uee__yor['csv_reader_init']
        ybzvs__wjltx = numba.njit(pkp__vaaqv)
        compiled_funcs.append(ybzvs__wjltx)
        uzlnc__akleb = compile_to_numba_ir(tiq__ubllz, {'_csv_reader_init':
            ybzvs__wjltx, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, xkrui__nan), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(uzlnc__akleb, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        akptu__fky = uzlnc__akleb.body[:-3]
        akptu__fky[-1].target = csv_node.out_vars[0]
        return akptu__fky
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    vku__iraa = 'def csv_impl(fname, nrows, skiprows):\n'
    vku__iraa += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    uee__yor = {}
    exec(vku__iraa, {}, uee__yor)
    jpk__zcovt = uee__yor['csv_impl']
    neyvl__fnhg = csv_node.usecols
    if neyvl__fnhg:
        neyvl__fnhg = [csv_node.usecols[ihk__hrxjc] for ihk__hrxjc in
            csv_node.out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        ihq__lls = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        mrja__avlh = csv_node.loc.strformat()
        rpej__tuwn = []
        esq__vyyj = []
        if neyvl__fnhg:
            for ihk__hrxjc in csv_node.out_used_cols:
                asr__qqpib = csv_node.df_colnames[ihk__hrxjc]
                rpej__tuwn.append(asr__qqpib)
                if isinstance(csv_node.out_types[ihk__hrxjc], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    esq__vyyj.append(asr__qqpib)
        bodo.user_logging.log_message('Column Pruning', ihq__lls,
            mrja__avlh, rpej__tuwn)
        if esq__vyyj:
            jipkt__chi = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', jipkt__chi,
                mrja__avlh, esq__vyyj)
    gioly__yza = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, neyvl__fnhg, csv_node.out_used_cols, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, csv_node.escapechar,
        csv_node.storage_options, idx_col_index=csv_node.index_column_index,
        idx_col_typ=csv_node.index_column_typ)
    uzlnc__akleb = compile_to_numba_ir(jpk__zcovt, {'_csv_reader_py':
        gioly__yza}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, xkrui__nan), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(uzlnc__akleb, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    akptu__fky = uzlnc__akleb.body[:-3]
    akptu__fky[-1].target = csv_node.out_vars[1]
    akptu__fky[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not neyvl__fnhg
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        akptu__fky.pop(-1)
    elif not neyvl__fnhg:
        akptu__fky.pop(-2)
    return akptu__fky


def csv_remove_dead_column(csv_node, column_live_map, equiv_vars, typemap):
    if csv_node.chunksize is not None:
        return False
    return bodo.ir.connector.base_connector_remove_dead_columns(csv_node,
        column_live_map, equiv_vars, typemap, 'CSVReader', csv_node.usecols)


numba.parfors.array_analysis.array_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[CsvReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[CsvReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[CsvReader] = remove_dead_csv
numba.core.analysis.ir_extension_usedefs[CsvReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[CsvReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[CsvReader] = csv_distributed_run
remove_dead_column_extensions[CsvReader] = csv_remove_dead_column
ir_extension_table_column_use[CsvReader
    ] = bodo.ir.connector.connector_table_column_use


def _get_dtype_str(t):
    cswsh__tjb = t.dtype
    if isinstance(cswsh__tjb, PDCategoricalDtype):
        kmte__juvqz = CategoricalArrayType(cswsh__tjb)
        rgc__phn = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, rgc__phn, kmte__juvqz)
        return rgc__phn
    if cswsh__tjb == types.NPDatetime('ns'):
        cswsh__tjb = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        dtccf__yldka = 'int_arr_{}'.format(cswsh__tjb)
        setattr(types, dtccf__yldka, t)
        return dtccf__yldka
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if cswsh__tjb == types.bool_:
        cswsh__tjb = 'bool_'
    if cswsh__tjb == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(cswsh__tjb, (
        StringArrayType, ArrayItemArrayType)):
        yjsc__lhoi = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, yjsc__lhoi, t)
        return yjsc__lhoi
    return '{}[::1]'.format(cswsh__tjb)


def _get_pd_dtype_str(t):
    cswsh__tjb = t.dtype
    if isinstance(cswsh__tjb, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(cswsh__tjb.categories)
    if cswsh__tjb == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if cswsh__tjb.signed else 'U',
            cswsh__tjb.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(cswsh__tjb, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(cswsh__tjb)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    vac__jhktv = ''
    from collections import defaultdict
    pjuhp__uxwtd = defaultdict(list)
    for qxo__bgnm, tacs__qpyww in typemap.items():
        pjuhp__uxwtd[tacs__qpyww].append(qxo__bgnm)
    dhbhp__lquf = df.columns.to_list()
    lwsus__hicsf = []
    for tacs__qpyww, mvw__pno in pjuhp__uxwtd.items():
        try:
            lwsus__hicsf.append(df.loc[:, mvw__pno].astype(tacs__qpyww,
                copy=False))
            df = df.drop(mvw__pno, axis=1)
        except (ValueError, TypeError) as opkm__uum:
            vac__jhktv = (
                f"Caught the runtime error '{opkm__uum}' on columns {mvw__pno}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    cwth__dprx = bool(vac__jhktv)
    if parallel:
        yxnlz__kfjvh = MPI.COMM_WORLD
        cwth__dprx = yxnlz__kfjvh.allreduce(cwth__dprx, op=MPI.LOR)
    if cwth__dprx:
        fht__kmp = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if vac__jhktv:
            raise TypeError(f'{fht__kmp}\n{vac__jhktv}')
        else:
            raise TypeError(
                f'{fht__kmp}\nPlease refer to errors on other ranks.')
    df = pd.concat(lwsus__hicsf + [df], axis=1)
    zpub__gjh = df.loc[:, dhbhp__lquf]
    return zpub__gjh


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    vnf__ioz = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        vku__iraa = '  skiprows = sorted(set(skiprows))\n'
    else:
        vku__iraa = '  skiprows = [skiprows]\n'
    vku__iraa += '  skiprows_list_len = len(skiprows)\n'
    vku__iraa += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    vku__iraa += '  check_java_installation(fname)\n'
    vku__iraa += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    vku__iraa += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    vku__iraa += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    vku__iraa += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, vnf__ioz, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    vku__iraa += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    vku__iraa += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    vku__iraa += "      raise FileNotFoundError('File does not exist')\n"
    return vku__iraa


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    cvf__dlxk = [str(ihk__hrxjc) for ihk__hrxjc, xypgw__eti in enumerate(
        usecols) if col_typs[out_used_cols[ihk__hrxjc]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        cvf__dlxk.append(str(idx_col_index))
    qybeq__fmw = ', '.join(cvf__dlxk)
    gvux__xixqh = _gen_parallel_flag_name(sanitized_cnames)
    gixb__pqflm = f"{gvux__xixqh}='bool_'" if check_parallel_runtime else ''
    yfp__myjfe = [_get_pd_dtype_str(col_typs[out_used_cols[ihk__hrxjc]]) for
        ihk__hrxjc in range(len(usecols))]
    whh__pqr = None if idx_col_index is None else _get_pd_dtype_str(idx_col_typ
        )
    yodd__gggy = [xypgw__eti for ihk__hrxjc, xypgw__eti in enumerate(
        usecols) if yfp__myjfe[ihk__hrxjc] == 'str']
    if idx_col_index is not None and whh__pqr == 'str':
        yodd__gggy.append(idx_col_index)
    atd__nyle = np.array(yodd__gggy, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = atd__nyle
    vku__iraa = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    lyqjx__fei = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = lyqjx__fei
    vku__iraa += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    iybe__afvjh = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = iybe__afvjh
        vku__iraa += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    oyl__szcrc = defaultdict(list)
    for ihk__hrxjc, xypgw__eti in enumerate(usecols):
        if yfp__myjfe[ihk__hrxjc] == 'str':
            continue
        oyl__szcrc[yfp__myjfe[ihk__hrxjc]].append(xypgw__eti)
    if idx_col_index is not None and whh__pqr != 'str':
        oyl__szcrc[whh__pqr].append(idx_col_index)
    for ihk__hrxjc, ggvxc__djmk in enumerate(oyl__szcrc.values()):
        glbs[f't_arr_{ihk__hrxjc}_{call_id}'] = np.asarray(ggvxc__djmk)
        vku__iraa += (
            f'  t_arr_{ihk__hrxjc}_{call_id}_2 = t_arr_{ihk__hrxjc}_{call_id}\n'
            )
    if idx_col_index != None:
        vku__iraa += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {gixb__pqflm}):
"""
    else:
        vku__iraa += (
            f'  with objmode(T=table_type_{call_id}, {gixb__pqflm}):\n')
    vku__iraa += f'    typemap = {{}}\n'
    for ihk__hrxjc, qsyan__yfk in enumerate(oyl__szcrc.keys()):
        vku__iraa += f"""    typemap.update({{i:{qsyan__yfk} for i in t_arr_{ihk__hrxjc}_{call_id}_2}})
"""
    vku__iraa += '    if f_reader.get_chunk_size() == 0:\n'
    vku__iraa += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    vku__iraa += '    else:\n'
    vku__iraa += '      df = pd.read_csv(f_reader,\n'
    vku__iraa += '        header=None,\n'
    vku__iraa += '        parse_dates=[{}],\n'.format(qybeq__fmw)
    vku__iraa += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    vku__iraa += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        vku__iraa += f'    {gvux__xixqh} = f_reader.is_parallel()\n'
    else:
        vku__iraa += f'    {gvux__xixqh} = {parallel}\n'
    vku__iraa += f'    df = astype(df, typemap, {gvux__xixqh})\n'
    if idx_col_index != None:
        mpt__nirgm = sorted(lyqjx__fei).index(idx_col_index)
        vku__iraa += f'    idx_arr = df.iloc[:, {mpt__nirgm}].values\n'
        vku__iraa += (
            f'    df.drop(columns=df.columns[{mpt__nirgm}], inplace=True)\n')
    if len(usecols) == 0:
        vku__iraa += f'    T = None\n'
    else:
        vku__iraa += f'    arrs = []\n'
        vku__iraa += f'    for i in range(df.shape[1]):\n'
        vku__iraa += f'      arrs.append(df.iloc[:, i].values)\n'
        vku__iraa += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return vku__iraa


def _gen_parallel_flag_name(sanitized_cnames):
    gvux__xixqh = '_parallel_value'
    while gvux__xixqh in sanitized_cnames:
        gvux__xixqh = '_' + gvux__xixqh
    return gvux__xixqh


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(ebr__zvatx) for ebr__zvatx in
        col_names]
    vku__iraa = 'def csv_reader_py(fname, nrows, skiprows):\n'
    vku__iraa += _gen_csv_file_reader_init(parallel, header, compression, -
        1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    ytd__jlnfh = globals()
    if idx_col_typ != types.none:
        ytd__jlnfh[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        ytd__jlnfh[f'table_type_{call_id}'] = types.none
    else:
        ytd__jlnfh[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    vku__iraa += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, ytd__jlnfh, parallel=parallel, check_parallel_runtime=
        False, idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        vku__iraa += '  return (T, idx_arr)\n'
    else:
        vku__iraa += '  return (T, None)\n'
    uee__yor = {}
    ytd__jlnfh['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(vku__iraa, ytd__jlnfh, uee__yor)
    gioly__yza = uee__yor['csv_reader_py']
    ybzvs__wjltx = numba.njit(gioly__yza)
    compiled_funcs.append(ybzvs__wjltx)
    return ybzvs__wjltx
