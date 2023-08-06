"""CSR Matrix data type implementation for scipy.sparse.csr_matrix
"""
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
import bodo
from bodo.utils.typing import BodoError


class CSRMatrixType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, dtype, idx_dtype):
        self.dtype = dtype
        self.idx_dtype = idx_dtype
        super(CSRMatrixType, self).__init__(name=
            f'CSRMatrixType({dtype}, {idx_dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    def copy(self):
        return CSRMatrixType(self.dtype, self.idx_dtype)


@register_model(CSRMatrixType)
class CSRMatrixModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hszdh__gbsut = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, hszdh__gbsut)


make_attribute_wrapper(CSRMatrixType, 'data', 'data')
make_attribute_wrapper(CSRMatrixType, 'indices', 'indices')
make_attribute_wrapper(CSRMatrixType, 'indptr', 'indptr')
make_attribute_wrapper(CSRMatrixType, 'shape', 'shape')


@intrinsic
def init_csr_matrix(typingctx, data_t, indices_t, indptr_t, shape_t=None):
    assert isinstance(data_t, types.Array)
    assert isinstance(indices_t, types.Array) and isinstance(indices_t.
        dtype, types.Integer)
    assert indices_t == indptr_t

    def codegen(context, builder, signature, args):
        lbta__bqqh, dup__gnom, npr__ynodv, fwtf__xdga = args
        idp__nwv = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        idp__nwv.data = lbta__bqqh
        idp__nwv.indices = dup__gnom
        idp__nwv.indptr = npr__ynodv
        idp__nwv.shape = fwtf__xdga
        context.nrt.incref(builder, signature.args[0], lbta__bqqh)
        context.nrt.incref(builder, signature.args[1], dup__gnom)
        context.nrt.incref(builder, signature.args[2], npr__ynodv)
        return idp__nwv._getvalue()
    fedx__izf = CSRMatrixType(data_t.dtype, indices_t.dtype)
    febj__kah = fedx__izf(data_t, indices_t, indptr_t, types.UniTuple(types
        .int64, 2))
    return febj__kah, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    idp__nwv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    qwh__kqet = c.pyapi.object_getattr_string(val, 'data')
    uklqt__cii = c.pyapi.object_getattr_string(val, 'indices')
    qfnq__iwuj = c.pyapi.object_getattr_string(val, 'indptr')
    jwb__unne = c.pyapi.object_getattr_string(val, 'shape')
    idp__nwv.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1, 'C'),
        qwh__kqet).value
    idp__nwv.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), uklqt__cii).value
    idp__nwv.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), qfnq__iwuj).value
    idp__nwv.shape = c.pyapi.to_native_value(types.UniTuple(types.int64, 2),
        jwb__unne).value
    c.pyapi.decref(qwh__kqet)
    c.pyapi.decref(uklqt__cii)
    c.pyapi.decref(qfnq__iwuj)
    c.pyapi.decref(jwb__unne)
    mmt__ebtkh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(idp__nwv._getvalue(), is_error=mmt__ebtkh)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    nzmu__rel = c.context.insert_const_string(c.builder.module, 'scipy.sparse')
    vml__mgd = c.pyapi.import_module_noblock(nzmu__rel)
    idp__nwv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        idp__nwv.data)
    qwh__kqet = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        idp__nwv.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        idp__nwv.indices)
    uklqt__cii = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), idp__nwv.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        idp__nwv.indptr)
    qfnq__iwuj = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), idp__nwv.indptr, c.env_manager)
    jwb__unne = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        idp__nwv.shape, c.env_manager)
    ejsd__eiua = c.pyapi.tuple_pack([qwh__kqet, uklqt__cii, qfnq__iwuj])
    zwlo__xemtr = c.pyapi.call_method(vml__mgd, 'csr_matrix', (ejsd__eiua,
        jwb__unne))
    c.pyapi.decref(ejsd__eiua)
    c.pyapi.decref(qwh__kqet)
    c.pyapi.decref(uklqt__cii)
    c.pyapi.decref(qfnq__iwuj)
    c.pyapi.decref(jwb__unne)
    c.pyapi.decref(vml__mgd)
    c.context.nrt.decref(c.builder, typ, val)
    return zwlo__xemtr


@overload(len, no_unliteral=True)
def overload_csr_matrix_len(A):
    if isinstance(A, CSRMatrixType):
        return lambda A: A.shape[0]


@overload_attribute(CSRMatrixType, 'ndim')
def overload_csr_matrix_ndim(A):
    return lambda A: 2


@overload_method(CSRMatrixType, 'copy', no_unliteral=True)
def overload_csr_matrix_copy(A):

    def copy_impl(A):
        return init_csr_matrix(A.data.copy(), A.indices.copy(), A.indptr.
            copy(), A.shape)
    return copy_impl


@overload(operator.getitem, no_unliteral=True)
def csr_matrix_getitem(A, idx):
    if not isinstance(A, CSRMatrixType):
        return
    livl__cidtd = A.dtype
    xwqcp__txr = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            dmbdm__ovz, geju__guoe = A.shape
            grra__sze = numba.cpython.unicode._normalize_slice(idx[0],
                dmbdm__ovz)
            vlpsz__vkst = numba.cpython.unicode._normalize_slice(idx[1],
                geju__guoe)
            if grra__sze.step != 1 or vlpsz__vkst.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            jcyr__pyjl = grra__sze.start
            ghj__kxrmy = grra__sze.stop
            qiq__pbs = vlpsz__vkst.start
            vmage__rele = vlpsz__vkst.stop
            flzs__akdga = A.indptr
            okj__jtisi = A.indices
            fqhip__zrjq = A.data
            ock__whye = ghj__kxrmy - jcyr__pyjl
            tjs__iowl = vmage__rele - qiq__pbs
            nfrn__ayad = 0
            hbfn__bmjva = 0
            for zot__sybw in range(ock__whye):
                sqlw__tjtry = flzs__akdga[jcyr__pyjl + zot__sybw]
                urq__rdfuk = flzs__akdga[jcyr__pyjl + zot__sybw + 1]
                for ugeb__fqwth in range(sqlw__tjtry, urq__rdfuk):
                    if okj__jtisi[ugeb__fqwth] >= qiq__pbs and okj__jtisi[
                        ugeb__fqwth] < vmage__rele:
                        nfrn__ayad += 1
            opi__eww = np.empty(ock__whye + 1, xwqcp__txr)
            vqtc__rrxbb = np.empty(nfrn__ayad, xwqcp__txr)
            awc__runf = np.empty(nfrn__ayad, livl__cidtd)
            opi__eww[0] = 0
            for zot__sybw in range(ock__whye):
                sqlw__tjtry = flzs__akdga[jcyr__pyjl + zot__sybw]
                urq__rdfuk = flzs__akdga[jcyr__pyjl + zot__sybw + 1]
                for ugeb__fqwth in range(sqlw__tjtry, urq__rdfuk):
                    if okj__jtisi[ugeb__fqwth] >= qiq__pbs and okj__jtisi[
                        ugeb__fqwth] < vmage__rele:
                        vqtc__rrxbb[hbfn__bmjva] = okj__jtisi[ugeb__fqwth
                            ] - qiq__pbs
                        awc__runf[hbfn__bmjva] = fqhip__zrjq[ugeb__fqwth]
                        hbfn__bmjva += 1
                opi__eww[zot__sybw + 1] = hbfn__bmjva
            return init_csr_matrix(awc__runf, vqtc__rrxbb, opi__eww, (
                ock__whye, tjs__iowl))
        return impl
    elif isinstance(idx, types.Array
        ) and idx.ndim == 1 and idx.dtype == xwqcp__txr:

        def impl(A, idx):
            dmbdm__ovz, geju__guoe = A.shape
            flzs__akdga = A.indptr
            okj__jtisi = A.indices
            fqhip__zrjq = A.data
            ock__whye = len(idx)
            nfrn__ayad = 0
            hbfn__bmjva = 0
            for zot__sybw in range(ock__whye):
                henqq__kbqp = idx[zot__sybw]
                sqlw__tjtry = flzs__akdga[henqq__kbqp]
                urq__rdfuk = flzs__akdga[henqq__kbqp + 1]
                nfrn__ayad += urq__rdfuk - sqlw__tjtry
            opi__eww = np.empty(ock__whye + 1, xwqcp__txr)
            vqtc__rrxbb = np.empty(nfrn__ayad, xwqcp__txr)
            awc__runf = np.empty(nfrn__ayad, livl__cidtd)
            opi__eww[0] = 0
            for zot__sybw in range(ock__whye):
                henqq__kbqp = idx[zot__sybw]
                sqlw__tjtry = flzs__akdga[henqq__kbqp]
                urq__rdfuk = flzs__akdga[henqq__kbqp + 1]
                vqtc__rrxbb[hbfn__bmjva:hbfn__bmjva + urq__rdfuk - sqlw__tjtry
                    ] = okj__jtisi[sqlw__tjtry:urq__rdfuk]
                awc__runf[hbfn__bmjva:hbfn__bmjva + urq__rdfuk - sqlw__tjtry
                    ] = fqhip__zrjq[sqlw__tjtry:urq__rdfuk]
                hbfn__bmjva += urq__rdfuk - sqlw__tjtry
                opi__eww[zot__sybw + 1] = hbfn__bmjva
            yccpy__wkv = init_csr_matrix(awc__runf, vqtc__rrxbb, opi__eww,
                (ock__whye, geju__guoe))
            return yccpy__wkv
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
