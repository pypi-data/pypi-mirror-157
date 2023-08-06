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
        wamcc__peiau = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, wamcc__peiau)


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
        qhmh__acbx, sygl__rnbu, kryd__oaeez, stdh__rdzc = args
        jeisv__luh = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        jeisv__luh.data = qhmh__acbx
        jeisv__luh.indices = sygl__rnbu
        jeisv__luh.indptr = kryd__oaeez
        jeisv__luh.shape = stdh__rdzc
        context.nrt.incref(builder, signature.args[0], qhmh__acbx)
        context.nrt.incref(builder, signature.args[1], sygl__rnbu)
        context.nrt.incref(builder, signature.args[2], kryd__oaeez)
        return jeisv__luh._getvalue()
    kqdc__hkb = CSRMatrixType(data_t.dtype, indices_t.dtype)
    clic__wcxcd = kqdc__hkb(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return clic__wcxcd, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    jeisv__luh = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    bnd__xmftp = c.pyapi.object_getattr_string(val, 'data')
    wvyrj__bozir = c.pyapi.object_getattr_string(val, 'indices')
    xjgcl__njth = c.pyapi.object_getattr_string(val, 'indptr')
    kzr__mazk = c.pyapi.object_getattr_string(val, 'shape')
    jeisv__luh.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1, 'C'
        ), bnd__xmftp).value
    jeisv__luh.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype,
        1, 'C'), wvyrj__bozir).value
    jeisv__luh.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 
        1, 'C'), xjgcl__njth).value
    jeisv__luh.shape = c.pyapi.to_native_value(types.UniTuple(types.int64, 
        2), kzr__mazk).value
    c.pyapi.decref(bnd__xmftp)
    c.pyapi.decref(wvyrj__bozir)
    c.pyapi.decref(xjgcl__njth)
    c.pyapi.decref(kzr__mazk)
    mjfwo__fbdi = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jeisv__luh._getvalue(), is_error=mjfwo__fbdi)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    onjfs__hpwlf = c.context.insert_const_string(c.builder.module,
        'scipy.sparse')
    xcxls__neot = c.pyapi.import_module_noblock(onjfs__hpwlf)
    jeisv__luh = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        jeisv__luh.data)
    bnd__xmftp = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        jeisv__luh.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        jeisv__luh.indices)
    wvyrj__bozir = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), jeisv__luh.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        jeisv__luh.indptr)
    xjgcl__njth = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), jeisv__luh.indptr, c.env_manager)
    kzr__mazk = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        jeisv__luh.shape, c.env_manager)
    hpxta__mvgzu = c.pyapi.tuple_pack([bnd__xmftp, wvyrj__bozir, xjgcl__njth])
    dxkda__ojnhm = c.pyapi.call_method(xcxls__neot, 'csr_matrix', (
        hpxta__mvgzu, kzr__mazk))
    c.pyapi.decref(hpxta__mvgzu)
    c.pyapi.decref(bnd__xmftp)
    c.pyapi.decref(wvyrj__bozir)
    c.pyapi.decref(xjgcl__njth)
    c.pyapi.decref(kzr__mazk)
    c.pyapi.decref(xcxls__neot)
    c.context.nrt.decref(c.builder, typ, val)
    return dxkda__ojnhm


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
    xgy__ixm = A.dtype
    cvknh__lwwgn = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            jinm__tyjv, umfcc__xlblg = A.shape
            wip__fpot = numba.cpython.unicode._normalize_slice(idx[0],
                jinm__tyjv)
            bidc__lyn = numba.cpython.unicode._normalize_slice(idx[1],
                umfcc__xlblg)
            if wip__fpot.step != 1 or bidc__lyn.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            qghg__nsx = wip__fpot.start
            zoeyg__qge = wip__fpot.stop
            ltwud__tdx = bidc__lyn.start
            kdkw__puc = bidc__lyn.stop
            rrffr__hftk = A.indptr
            roed__rab = A.indices
            slpfs__fut = A.data
            cge__xemir = zoeyg__qge - qghg__nsx
            rlj__vesjn = kdkw__puc - ltwud__tdx
            yle__cjj = 0
            fxi__ioi = 0
            for dvai__yaes in range(cge__xemir):
                wcmha__intwo = rrffr__hftk[qghg__nsx + dvai__yaes]
                vrazo__ecpm = rrffr__hftk[qghg__nsx + dvai__yaes + 1]
                for mpwk__orub in range(wcmha__intwo, vrazo__ecpm):
                    if roed__rab[mpwk__orub] >= ltwud__tdx and roed__rab[
                        mpwk__orub] < kdkw__puc:
                        yle__cjj += 1
            qoo__pnyet = np.empty(cge__xemir + 1, cvknh__lwwgn)
            jwux__omp = np.empty(yle__cjj, cvknh__lwwgn)
            cdi__zktzl = np.empty(yle__cjj, xgy__ixm)
            qoo__pnyet[0] = 0
            for dvai__yaes in range(cge__xemir):
                wcmha__intwo = rrffr__hftk[qghg__nsx + dvai__yaes]
                vrazo__ecpm = rrffr__hftk[qghg__nsx + dvai__yaes + 1]
                for mpwk__orub in range(wcmha__intwo, vrazo__ecpm):
                    if roed__rab[mpwk__orub] >= ltwud__tdx and roed__rab[
                        mpwk__orub] < kdkw__puc:
                        jwux__omp[fxi__ioi] = roed__rab[mpwk__orub
                            ] - ltwud__tdx
                        cdi__zktzl[fxi__ioi] = slpfs__fut[mpwk__orub]
                        fxi__ioi += 1
                qoo__pnyet[dvai__yaes + 1] = fxi__ioi
            return init_csr_matrix(cdi__zktzl, jwux__omp, qoo__pnyet, (
                cge__xemir, rlj__vesjn))
        return impl
    elif isinstance(idx, types.Array
        ) and idx.ndim == 1 and idx.dtype == cvknh__lwwgn:

        def impl(A, idx):
            jinm__tyjv, umfcc__xlblg = A.shape
            rrffr__hftk = A.indptr
            roed__rab = A.indices
            slpfs__fut = A.data
            cge__xemir = len(idx)
            yle__cjj = 0
            fxi__ioi = 0
            for dvai__yaes in range(cge__xemir):
                drfpk__drhzf = idx[dvai__yaes]
                wcmha__intwo = rrffr__hftk[drfpk__drhzf]
                vrazo__ecpm = rrffr__hftk[drfpk__drhzf + 1]
                yle__cjj += vrazo__ecpm - wcmha__intwo
            qoo__pnyet = np.empty(cge__xemir + 1, cvknh__lwwgn)
            jwux__omp = np.empty(yle__cjj, cvknh__lwwgn)
            cdi__zktzl = np.empty(yle__cjj, xgy__ixm)
            qoo__pnyet[0] = 0
            for dvai__yaes in range(cge__xemir):
                drfpk__drhzf = idx[dvai__yaes]
                wcmha__intwo = rrffr__hftk[drfpk__drhzf]
                vrazo__ecpm = rrffr__hftk[drfpk__drhzf + 1]
                jwux__omp[fxi__ioi:fxi__ioi + vrazo__ecpm - wcmha__intwo
                    ] = roed__rab[wcmha__intwo:vrazo__ecpm]
                cdi__zktzl[fxi__ioi:fxi__ioi + vrazo__ecpm - wcmha__intwo
                    ] = slpfs__fut[wcmha__intwo:vrazo__ecpm]
                fxi__ioi += vrazo__ecpm - wcmha__intwo
                qoo__pnyet[dvai__yaes + 1] = fxi__ioi
            pjcj__uwam = init_csr_matrix(cdi__zktzl, jwux__omp, qoo__pnyet,
                (cge__xemir, umfcc__xlblg))
            return pjcj__uwam
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
