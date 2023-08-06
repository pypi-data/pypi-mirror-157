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
    adl__cpj = typemap[node.file_name.name]
    if types.unliteral(adl__cpj) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {adl__cpj}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        vxglo__sxrte = typemap[node.skiprows.name]
        if isinstance(vxglo__sxrte, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(vxglo__sxrte, types.Integer) and not (isinstance
            (vxglo__sxrte, (types.List, types.Tuple)) and isinstance(
            vxglo__sxrte.dtype, types.Integer)) and not isinstance(vxglo__sxrte
            , (types.LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {vxglo__sxrte}."
                , loc=node.skiprows.loc)
        elif isinstance(vxglo__sxrte, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        bhw__whg = typemap[node.nrows.name]
        if not isinstance(bhw__whg, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {bhw__whg}."
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
        oag__lfj = csv_node.out_vars[0]
        if oag__lfj.name not in lives:
            return None
    else:
        lvu__fgyb = csv_node.out_vars[0]
        ayh__soyo = csv_node.out_vars[1]
        if lvu__fgyb.name not in lives and ayh__soyo.name not in lives:
            return None
        elif ayh__soyo.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif lvu__fgyb.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    vxglo__sxrte = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            vqk__pzlrb = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            dhng__csgzt = csv_node.loc.strformat()
            rxixu__bby = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', vqk__pzlrb,
                dhng__csgzt, rxixu__bby)
            xnrjn__hydbe = csv_node.out_types[0].yield_type.data
            mxbmm__zitm = [erd__pslx for aqa__anu, erd__pslx in enumerate(
                csv_node.df_colnames) if isinstance(xnrjn__hydbe[aqa__anu],
                bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if mxbmm__zitm:
                muj__dzgcx = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    muj__dzgcx, dhng__csgzt, mxbmm__zitm)
        if array_dists is not None:
            btmg__hwqw = csv_node.out_vars[0].name
            parallel = array_dists[btmg__hwqw] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        twtw__mcvi = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        twtw__mcvi += (
            f'    reader = _csv_reader_init(fname, nrows, skiprows)\n')
        twtw__mcvi += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        fvk__hzpm = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(twtw__mcvi, {}, fvk__hzpm)
        lnyy__btg = fvk__hzpm['csv_iterator_impl']
        oxu__fnc = 'def csv_reader_init(fname, nrows, skiprows):\n'
        oxu__fnc += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        oxu__fnc += '  return f_reader\n'
        exec(oxu__fnc, globals(), fvk__hzpm)
        eor__btskw = fvk__hzpm['csv_reader_init']
        evaro__gdj = numba.njit(eor__btskw)
        compiled_funcs.append(evaro__gdj)
        roesd__frwl = compile_to_numba_ir(lnyy__btg, {'_csv_reader_init':
            evaro__gdj, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, vxglo__sxrte), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(roesd__frwl, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        tkv__jkil = roesd__frwl.body[:-3]
        tkv__jkil[-1].target = csv_node.out_vars[0]
        return tkv__jkil
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    twtw__mcvi = 'def csv_impl(fname, nrows, skiprows):\n'
    twtw__mcvi += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    fvk__hzpm = {}
    exec(twtw__mcvi, {}, fvk__hzpm)
    omce__rdls = fvk__hzpm['csv_impl']
    sxada__biif = csv_node.usecols
    if sxada__biif:
        sxada__biif = [csv_node.usecols[aqa__anu] for aqa__anu in csv_node.
            out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        vqk__pzlrb = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        dhng__csgzt = csv_node.loc.strformat()
        rxixu__bby = []
        mxbmm__zitm = []
        if sxada__biif:
            for aqa__anu in csv_node.out_used_cols:
                tuass__ugk = csv_node.df_colnames[aqa__anu]
                rxixu__bby.append(tuass__ugk)
                if isinstance(csv_node.out_types[aqa__anu], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    mxbmm__zitm.append(tuass__ugk)
        bodo.user_logging.log_message('Column Pruning', vqk__pzlrb,
            dhng__csgzt, rxixu__bby)
        if mxbmm__zitm:
            muj__dzgcx = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', muj__dzgcx,
                dhng__csgzt, mxbmm__zitm)
    zvciv__cdvq = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, sxada__biif, csv_node.out_used_cols, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, csv_node.escapechar,
        csv_node.storage_options, idx_col_index=csv_node.index_column_index,
        idx_col_typ=csv_node.index_column_typ)
    roesd__frwl = compile_to_numba_ir(omce__rdls, {'_csv_reader_py':
        zvciv__cdvq}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, vxglo__sxrte), typemap=typemap, calltypes
        =calltypes).blocks.popitem()[1]
    replace_arg_nodes(roesd__frwl, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    tkv__jkil = roesd__frwl.body[:-3]
    tkv__jkil[-1].target = csv_node.out_vars[1]
    tkv__jkil[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not sxada__biif
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        tkv__jkil.pop(-1)
    elif not sxada__biif:
        tkv__jkil.pop(-2)
    return tkv__jkil


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
    ivf__axsi = t.dtype
    if isinstance(ivf__axsi, PDCategoricalDtype):
        rcxu__pbg = CategoricalArrayType(ivf__axsi)
        banxs__qrnpc = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, banxs__qrnpc, rcxu__pbg)
        return banxs__qrnpc
    if ivf__axsi == types.NPDatetime('ns'):
        ivf__axsi = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        cack__jij = 'int_arr_{}'.format(ivf__axsi)
        setattr(types, cack__jij, t)
        return cack__jij
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if ivf__axsi == types.bool_:
        ivf__axsi = 'bool_'
    if ivf__axsi == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(ivf__axsi, (
        StringArrayType, ArrayItemArrayType)):
        enohe__xen = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, enohe__xen, t)
        return enohe__xen
    return '{}[::1]'.format(ivf__axsi)


def _get_pd_dtype_str(t):
    ivf__axsi = t.dtype
    if isinstance(ivf__axsi, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(ivf__axsi.categories)
    if ivf__axsi == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if ivf__axsi.signed else 'U',
            ivf__axsi.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(ivf__axsi, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(ivf__axsi)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    jdnqa__etjcd = ''
    from collections import defaultdict
    cipmd__eplca = defaultdict(list)
    for dyfqy__elijz, jypqj__hsmg in typemap.items():
        cipmd__eplca[jypqj__hsmg].append(dyfqy__elijz)
    iuz__eblt = df.columns.to_list()
    yiwx__ijzif = []
    for jypqj__hsmg, mbslc__ndtb in cipmd__eplca.items():
        try:
            yiwx__ijzif.append(df.loc[:, mbslc__ndtb].astype(jypqj__hsmg,
                copy=False))
            df = df.drop(mbslc__ndtb, axis=1)
        except (ValueError, TypeError) as rkbg__plmep:
            jdnqa__etjcd = (
                f"Caught the runtime error '{rkbg__plmep}' on columns {mbslc__ndtb}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    hiwp__nvk = bool(jdnqa__etjcd)
    if parallel:
        wmq__eat = MPI.COMM_WORLD
        hiwp__nvk = wmq__eat.allreduce(hiwp__nvk, op=MPI.LOR)
    if hiwp__nvk:
        lghk__ztv = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if jdnqa__etjcd:
            raise TypeError(f'{lghk__ztv}\n{jdnqa__etjcd}')
        else:
            raise TypeError(
                f'{lghk__ztv}\nPlease refer to errors on other ranks.')
    df = pd.concat(yiwx__ijzif + [df], axis=1)
    qsuie__hjl = df.loc[:, iuz__eblt]
    return qsuie__hjl


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    cij__gjkgo = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        twtw__mcvi = '  skiprows = sorted(set(skiprows))\n'
    else:
        twtw__mcvi = '  skiprows = [skiprows]\n'
    twtw__mcvi += '  skiprows_list_len = len(skiprows)\n'
    twtw__mcvi += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    twtw__mcvi += '  check_java_installation(fname)\n'
    twtw__mcvi += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    twtw__mcvi += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    twtw__mcvi += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    twtw__mcvi += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, cij__gjkgo, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    twtw__mcvi += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    twtw__mcvi += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    twtw__mcvi += "      raise FileNotFoundError('File does not exist')\n"
    return twtw__mcvi


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    lra__hyv = [str(aqa__anu) for aqa__anu, bnxxd__szxi in enumerate(
        usecols) if col_typs[out_used_cols[aqa__anu]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        lra__hyv.append(str(idx_col_index))
    awm__dzi = ', '.join(lra__hyv)
    mueq__wfx = _gen_parallel_flag_name(sanitized_cnames)
    wnzti__pzcu = f"{mueq__wfx}='bool_'" if check_parallel_runtime else ''
    qusya__dvr = [_get_pd_dtype_str(col_typs[out_used_cols[aqa__anu]]) for
        aqa__anu in range(len(usecols))]
    dymmk__rvkwm = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    grwye__qfnrp = [bnxxd__szxi for aqa__anu, bnxxd__szxi in enumerate(
        usecols) if qusya__dvr[aqa__anu] == 'str']
    if idx_col_index is not None and dymmk__rvkwm == 'str':
        grwye__qfnrp.append(idx_col_index)
    fnc__ipwip = np.array(grwye__qfnrp, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = fnc__ipwip
    twtw__mcvi = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    vpmn__tmt = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = vpmn__tmt
    twtw__mcvi += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    sbill__wykey = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = sbill__wykey
        twtw__mcvi += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    jfxs__atksx = defaultdict(list)
    for aqa__anu, bnxxd__szxi in enumerate(usecols):
        if qusya__dvr[aqa__anu] == 'str':
            continue
        jfxs__atksx[qusya__dvr[aqa__anu]].append(bnxxd__szxi)
    if idx_col_index is not None and dymmk__rvkwm != 'str':
        jfxs__atksx[dymmk__rvkwm].append(idx_col_index)
    for aqa__anu, wdcqn__gpb in enumerate(jfxs__atksx.values()):
        glbs[f't_arr_{aqa__anu}_{call_id}'] = np.asarray(wdcqn__gpb)
        twtw__mcvi += (
            f'  t_arr_{aqa__anu}_{call_id}_2 = t_arr_{aqa__anu}_{call_id}\n')
    if idx_col_index != None:
        twtw__mcvi += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {wnzti__pzcu}):
"""
    else:
        twtw__mcvi += (
            f'  with objmode(T=table_type_{call_id}, {wnzti__pzcu}):\n')
    twtw__mcvi += f'    typemap = {{}}\n'
    for aqa__anu, iykqz__cwbt in enumerate(jfxs__atksx.keys()):
        twtw__mcvi += f"""    typemap.update({{i:{iykqz__cwbt} for i in t_arr_{aqa__anu}_{call_id}_2}})
"""
    twtw__mcvi += '    if f_reader.get_chunk_size() == 0:\n'
    twtw__mcvi += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    twtw__mcvi += '    else:\n'
    twtw__mcvi += '      df = pd.read_csv(f_reader,\n'
    twtw__mcvi += '        header=None,\n'
    twtw__mcvi += '        parse_dates=[{}],\n'.format(awm__dzi)
    twtw__mcvi += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    twtw__mcvi += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        twtw__mcvi += f'    {mueq__wfx} = f_reader.is_parallel()\n'
    else:
        twtw__mcvi += f'    {mueq__wfx} = {parallel}\n'
    twtw__mcvi += f'    df = astype(df, typemap, {mueq__wfx})\n'
    if idx_col_index != None:
        epxos__ounca = sorted(vpmn__tmt).index(idx_col_index)
        twtw__mcvi += f'    idx_arr = df.iloc[:, {epxos__ounca}].values\n'
        twtw__mcvi += (
            f'    df.drop(columns=df.columns[{epxos__ounca}], inplace=True)\n')
    if len(usecols) == 0:
        twtw__mcvi += f'    T = None\n'
    else:
        twtw__mcvi += f'    arrs = []\n'
        twtw__mcvi += f'    for i in range(df.shape[1]):\n'
        twtw__mcvi += f'      arrs.append(df.iloc[:, i].values)\n'
        twtw__mcvi += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return twtw__mcvi


def _gen_parallel_flag_name(sanitized_cnames):
    mueq__wfx = '_parallel_value'
    while mueq__wfx in sanitized_cnames:
        mueq__wfx = '_' + mueq__wfx
    return mueq__wfx


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(erd__pslx) for erd__pslx in col_names]
    twtw__mcvi = 'def csv_reader_py(fname, nrows, skiprows):\n'
    twtw__mcvi += _gen_csv_file_reader_init(parallel, header, compression, 
        -1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    bub__cmkfl = globals()
    if idx_col_typ != types.none:
        bub__cmkfl[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        bub__cmkfl[f'table_type_{call_id}'] = types.none
    else:
        bub__cmkfl[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    twtw__mcvi += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, bub__cmkfl, parallel=parallel, check_parallel_runtime=
        False, idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        twtw__mcvi += '  return (T, idx_arr)\n'
    else:
        twtw__mcvi += '  return (T, None)\n'
    fvk__hzpm = {}
    bub__cmkfl['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(twtw__mcvi, bub__cmkfl, fvk__hzpm)
    zvciv__cdvq = fvk__hzpm['csv_reader_py']
    evaro__gdj = numba.njit(zvciv__cdvq)
    compiled_funcs.append(evaro__gdj)
    return evaro__gdj
