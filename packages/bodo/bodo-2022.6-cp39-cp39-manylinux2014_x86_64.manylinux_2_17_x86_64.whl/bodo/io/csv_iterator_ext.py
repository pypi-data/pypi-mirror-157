"""
Class information for DataFrame iterators returned by pd.read_csv. This is used
to handle situations in which pd.read_csv is used to return chunks with separate
read calls instead of just a single read.
"""
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir_utils, types
from numba.core.imputils import RefType, impl_ret_borrowed, iternext_impl
from numba.core.typing.templates import signature
from numba.extending import intrinsic, lower_builtin, models, register_model
import bodo
import bodo.ir.connector
import bodo.ir.csv_ext
from bodo import objmode
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.table import Table, TableType
from bodo.io import csv_cpp
from bodo.ir.csv_ext import _gen_read_csv_objmode, astype
from bodo.utils.typing import ColNamesMetaType
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import sanitize_varname
ll.add_symbol('update_csv_reader', csv_cpp.update_csv_reader)
ll.add_symbol('initialize_csv_reader', csv_cpp.initialize_csv_reader)


class CSVIteratorType(types.SimpleIteratorType):

    def __init__(self, df_type, out_colnames, out_types, usecols, sep,
        index_ind, index_arr_typ, index_name, escapechar, storage_options):
        assert isinstance(df_type, DataFrameType
            ), 'CSVIterator must return a DataFrame'
        vxi__wzrp = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(vxi__wzrp)
        self._yield_type = df_type
        self._out_colnames = out_colnames
        self._out_types = out_types
        self._usecols = usecols
        self._sep = sep
        self._index_ind = index_ind
        self._index_arr_typ = index_arr_typ
        self._index_name = index_name
        self._escapechar = escapechar
        self._storage_options = storage_options

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(CSVIteratorType)
class CSVIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vwp__cqghr = [('csv_reader', bodo.ir.connector.stream_reader_type),
            ('index', types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, vwp__cqghr)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    ptq__rbhji = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    uzcie__jbhe = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer()])
    xnkq__saxax = cgutils.get_or_insert_function(builder.module,
        uzcie__jbhe, name='initialize_csv_reader')
    builder.call(xnkq__saxax, [ptq__rbhji.csv_reader])
    builder.store(context.get_constant(types.uint64, 0), ptq__rbhji.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [jwn__ibn] = sig.args
    [lbhxf__jwd] = args
    ptq__rbhji = cgutils.create_struct_proxy(jwn__ibn)(context, builder,
        value=lbhxf__jwd)
    uzcie__jbhe = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer()])
    xnkq__saxax = cgutils.get_or_insert_function(builder.module,
        uzcie__jbhe, name='update_csv_reader')
    tqj__kphn = builder.call(xnkq__saxax, [ptq__rbhji.csv_reader])
    result.set_valid(tqj__kphn)
    with builder.if_then(tqj__kphn):
        yiedu__xbf = builder.load(ptq__rbhji.index)
        ucro__say = types.Tuple([sig.return_type.first_type, types.int64])
        tvxt__cjwxp = gen_read_csv_objmode(sig.args[0])
        yth__rrvbv = signature(ucro__say, bodo.ir.connector.
            stream_reader_type, types.int64)
        cyj__oujui = context.compile_internal(builder, tvxt__cjwxp,
            yth__rrvbv, [ptq__rbhji.csv_reader, yiedu__xbf])
        qxntc__ybtm, lent__aoh = cgutils.unpack_tuple(builder, cyj__oujui)
        qvnu__zci = builder.add(yiedu__xbf, lent__aoh, flags=['nsw'])
        builder.store(qvnu__zci, ptq__rbhji.index)
        result.yield_(qxntc__ybtm)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        sruku__sfs = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        sruku__sfs.csv_reader = args[0]
        wcj__usnq = context.get_constant(types.uintp, 0)
        sruku__sfs.index = cgutils.alloca_once_value(builder, wcj__usnq)
        return sruku__sfs._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    qnfxe__cbdkk = csv_iterator_typeref.instance_type
    sig = signature(qnfxe__cbdkk, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    mbg__nkqyf = 'def read_csv_objmode(f_reader):\n'
    hbg__uhgd = [sanitize_varname(far__ysr) for far__ysr in
        csv_iterator_type._out_colnames]
    spl__mrtvc = ir_utils.next_label()
    tau__kec = globals()
    out_types = csv_iterator_type._out_types
    tau__kec[f'table_type_{spl__mrtvc}'] = TableType(tuple(out_types))
    tau__kec[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    zqro__hnm = list(range(len(csv_iterator_type._usecols)))
    mbg__nkqyf += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        hbg__uhgd, out_types, csv_iterator_type._usecols, zqro__hnm,
        csv_iterator_type._sep, csv_iterator_type._escapechar,
        csv_iterator_type._storage_options, spl__mrtvc, tau__kec, parallel=
        False, check_parallel_runtime=True, idx_col_index=csv_iterator_type
        ._index_ind, idx_col_typ=csv_iterator_type._index_arr_typ)
    fjiwl__oeptc = bodo.ir.csv_ext._gen_parallel_flag_name(hbg__uhgd)
    ehh__vnrou = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [fjiwl__oeptc]
    mbg__nkqyf += f"  return {', '.join(ehh__vnrou)}"
    tau__kec = globals()
    kaxaw__hfyq = {}
    exec(mbg__nkqyf, tau__kec, kaxaw__hfyq)
    otgwn__vic = kaxaw__hfyq['read_csv_objmode']
    tei__fnjs = numba.njit(otgwn__vic)
    bodo.ir.csv_ext.compiled_funcs.append(tei__fnjs)
    bne__wzpln = 'def read_func(reader, local_start):\n'
    bne__wzpln += f"  {', '.join(ehh__vnrou)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        bne__wzpln += f'  local_len = len(T)\n'
        bne__wzpln += '  total_size = local_len\n'
        bne__wzpln += f'  if ({fjiwl__oeptc}):\n'
        bne__wzpln += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        bne__wzpln += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        smr__eumkg = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        bne__wzpln += '  total_size = 0\n'
        smr__eumkg = (
            f'bodo.utils.conversion.convert_to_index({ehh__vnrou[1]}, {csv_iterator_type._index_name!r})'
            )
    bne__wzpln += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({ehh__vnrou[0]},), {smr__eumkg}, __col_name_meta_value_read_csv_objmode), total_size)
"""
    exec(bne__wzpln, {'bodo': bodo, 'objmode_func': tei__fnjs, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        '__col_name_meta_value_read_csv_objmode': ColNamesMetaType(
        csv_iterator_type.yield_type.columns)}, kaxaw__hfyq)
    return kaxaw__hfyq['read_func']
