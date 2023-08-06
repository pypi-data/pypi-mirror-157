import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.io.fs_io import get_storage_options_pyobject, storage_options_dict_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.utils.utils import check_java_installation, sanitize_varname


class JsonReader(ir.Stmt):

    def __init__(self, df_out, loc, out_vars, out_types, file_name,
        df_colnames, orient, convert_dates, precise_float, lines,
        compression, storage_options):
        self.connector_typ = 'json'
        self.df_out = df_out
        self.loc = loc
        self.out_vars = out_vars
        self.out_types = out_types
        self.file_name = file_name
        self.df_colnames = df_colnames
        self.orient = orient
        self.convert_dates = convert_dates
        self.precise_float = precise_float
        self.lines = lines
        self.compression = compression
        self.storage_options = storage_options

    def __repr__(self):
        return ('{} = ReadJson(file={}, col_names={}, types={}, vars={})'.
            format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars))


import llvmlite.binding as ll
from bodo.io import json_cpp
ll.add_symbol('json_file_chunk_reader', json_cpp.json_file_chunk_reader)
json_file_chunk_reader = types.ExternalFunction('json_file_chunk_reader',
    bodo.ir.connector.stream_reader_type(types.voidptr, types.bool_, types.
    bool_, types.int64, types.voidptr, types.voidptr,
    storage_options_dict_type))


def remove_dead_json(json_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    hgdya__dww = []
    tfh__prvri = []
    arn__wyh = []
    for pkuiy__uzzg, olrf__hkly in enumerate(json_node.out_vars):
        if olrf__hkly.name in lives:
            hgdya__dww.append(json_node.df_colnames[pkuiy__uzzg])
            tfh__prvri.append(json_node.out_vars[pkuiy__uzzg])
            arn__wyh.append(json_node.out_types[pkuiy__uzzg])
    json_node.df_colnames = hgdya__dww
    json_node.out_vars = tfh__prvri
    json_node.out_types = arn__wyh
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        etkiq__udwh = (
            'Finish column pruning on read_json node:\n%s\nColumns loaded %s\n'
            )
        xsci__ewo = json_node.loc.strformat()
        zfzyo__uhv = json_node.df_colnames
        bodo.user_logging.log_message('Column Pruning', etkiq__udwh,
            xsci__ewo, zfzyo__uhv)
        pmxl__fbgta = [zmtuw__fii for pkuiy__uzzg, zmtuw__fii in enumerate(
            json_node.df_colnames) if isinstance(json_node.out_types[
            pkuiy__uzzg], bodo.libs.dict_arr_ext.DictionaryArrayType)]
        if pmxl__fbgta:
            oobmc__arlqp = """Finished optimized encoding on read_json node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                oobmc__arlqp, xsci__ewo, pmxl__fbgta)
    parallel = False
    if array_dists is not None:
        parallel = True
        for mamv__oor in json_node.out_vars:
            if array_dists[mamv__oor.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                mamv__oor.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    yanc__kdu = len(json_node.out_vars)
    mapod__daq = ', '.join('arr' + str(pkuiy__uzzg) for pkuiy__uzzg in
        range(yanc__kdu))
    ldnw__nakl = 'def json_impl(fname):\n'
    ldnw__nakl += '    ({},) = _json_reader_py(fname)\n'.format(mapod__daq)
    ugw__fsygh = {}
    exec(ldnw__nakl, {}, ugw__fsygh)
    thfxl__gjh = ugw__fsygh['json_impl']
    okjeh__snlf = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression, json_node.storage_options)
    auxy__dczya = compile_to_numba_ir(thfxl__gjh, {'_json_reader_py':
        okjeh__snlf}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(auxy__dczya, [json_node.file_name])
    xmy__bbw = auxy__dczya.body[:-3]
    for pkuiy__uzzg in range(len(json_node.out_vars)):
        xmy__bbw[-len(json_node.out_vars) + pkuiy__uzzg
            ].target = json_node.out_vars[pkuiy__uzzg]
    return xmy__bbw


numba.parfors.array_analysis.array_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[JsonReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[JsonReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[JsonReader] = remove_dead_json
numba.core.analysis.ir_extension_usedefs[JsonReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[JsonReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[JsonReader] = json_distributed_run
compiled_funcs = []


def _gen_json_reader_py(col_names, col_typs, typingctx, targetctx, parallel,
    orient, convert_dates, precise_float, lines, compression, storage_options):
    tla__hip = [sanitize_varname(zmtuw__fii) for zmtuw__fii in col_names]
    xhkv__qdq = ', '.join(str(pkuiy__uzzg) for pkuiy__uzzg, tffpg__ici in
        enumerate(col_typs) if tffpg__ici.dtype == types.NPDatetime('ns'))
    bcv__yku = ', '.join(["{}='{}'".format(nxol__gjruv, bodo.ir.csv_ext.
        _get_dtype_str(tffpg__ici)) for nxol__gjruv, tffpg__ici in zip(
        tla__hip, col_typs)])
    qnos__ysn = ', '.join(["'{}':{}".format(ppnhn__zux, bodo.ir.csv_ext.
        _get_pd_dtype_str(tffpg__ici)) for ppnhn__zux, tffpg__ici in zip(
        col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    ldnw__nakl = 'def json_reader_py(fname):\n'
    ldnw__nakl += '  df_typeref_2 = df_typeref\n'
    ldnw__nakl += '  check_java_installation(fname)\n'
    ldnw__nakl += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    ldnw__nakl += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    ldnw__nakl += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    ldnw__nakl += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py )
"""
        .format(lines, parallel, compression))
    ldnw__nakl += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    ldnw__nakl += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    ldnw__nakl += "      raise FileNotFoundError('File does not exist')\n"
    ldnw__nakl += f'  with objmode({bcv__yku}):\n'
    ldnw__nakl += f"    df = pd.read_json(f_reader, orient='{orient}',\n"
    ldnw__nakl += f'       convert_dates = {convert_dates}, \n'
    ldnw__nakl += f'       precise_float={precise_float}, \n'
    ldnw__nakl += f'       lines={lines}, \n'
    ldnw__nakl += '       dtype={{{}}},\n'.format(qnos__ysn)
    ldnw__nakl += '       )\n'
    ldnw__nakl += (
        '    bodo.ir.connector.cast_float_to_nullable(df, df_typeref_2)\n')
    for nxol__gjruv, ppnhn__zux in zip(tla__hip, col_names):
        ldnw__nakl += '    if len(df) > 0:\n'
        ldnw__nakl += "        {} = df['{}'].values\n".format(nxol__gjruv,
            ppnhn__zux)
        ldnw__nakl += '    else:\n'
        ldnw__nakl += '        {} = np.array([])\n'.format(nxol__gjruv)
    ldnw__nakl += '  return ({},)\n'.format(', '.join(vxszl__drdl for
        vxszl__drdl in tla__hip))
    kxncg__btt = globals()
    kxncg__btt.update({'bodo': bodo, 'pd': pd, 'np': np, 'objmode': objmode,
        'check_java_installation': check_java_installation, 'df_typeref':
        bodo.DataFrameType(tuple(col_typs), bodo.RangeIndexType(None),
        tuple(col_names)), 'get_storage_options_pyobject':
        get_storage_options_pyobject})
    ugw__fsygh = {}
    exec(ldnw__nakl, kxncg__btt, ugw__fsygh)
    okjeh__snlf = ugw__fsygh['json_reader_py']
    tydrk__awj = numba.njit(okjeh__snlf)
    compiled_funcs.append(tydrk__awj)
    return tydrk__awj
