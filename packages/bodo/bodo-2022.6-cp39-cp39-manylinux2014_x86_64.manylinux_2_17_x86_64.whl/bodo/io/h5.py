"""
Analysis and transformation for HDF5 support.
"""
import types as pytypes
import numba
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, find_callname, find_const, get_definition, guard, replace_arg_nodes, require
import bodo
import bodo.io
from bodo.utils.transform import get_const_value_inner


class H5_IO:

    def __init__(self, func_ir, _locals, flags, arg_types):
        self.func_ir = func_ir
        self.locals = _locals
        self.flags = flags
        self.arg_types = arg_types

    def handle_possible_h5_read(self, assign, lhs, rhs):
        djdq__fxtrh = self._get_h5_type(lhs, rhs)
        if djdq__fxtrh is not None:
            mkh__fbzj = str(djdq__fxtrh.dtype)
            zah__bhn = 'def _h5_read_impl(dset, index):\n'
            zah__bhn += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(djdq__fxtrh.ndim, mkh__fbzj))
            syxsn__mstky = {}
            exec(zah__bhn, {}, syxsn__mstky)
            piia__rhvf = syxsn__mstky['_h5_read_impl']
            qat__mxib = compile_to_numba_ir(piia__rhvf, {'bodo': bodo}
                ).blocks.popitem()[1]
            idm__ayhn = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(qat__mxib, [rhs.value, idm__ayhn])
            lrkq__vczc = qat__mxib.body[:-3]
            lrkq__vczc[-1].target = assign.target
            return lrkq__vczc
        return None

    def _get_h5_type(self, lhs, rhs):
        djdq__fxtrh = self._get_h5_type_locals(lhs)
        if djdq__fxtrh is not None:
            return djdq__fxtrh
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        idm__ayhn = rhs.index if rhs.op == 'getitem' else rhs.index_var
        frige__hkac = guard(find_const, self.func_ir, idm__ayhn)
        require(not isinstance(frige__hkac, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            mhynw__wok = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            vol__sid = get_const_value_inner(self.func_ir, mhynw__wok,
                arg_types=self.arg_types)
            obj_name_list.append(vol__sid)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        whiro__iuiix = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        rvd__ymbl = h5py.File(whiro__iuiix, 'r')
        zpygm__gnbb = rvd__ymbl
        for vol__sid in obj_name_list:
            zpygm__gnbb = zpygm__gnbb[vol__sid]
        require(isinstance(zpygm__gnbb, h5py.Dataset))
        icq__ubowm = len(zpygm__gnbb.shape)
        domz__vlx = numba.np.numpy_support.from_dtype(zpygm__gnbb.dtype)
        rvd__ymbl.close()
        return types.Array(domz__vlx, icq__ubowm, 'C')

    def _get_h5_type_locals(self, varname):
        yvd__cnocp = self.locals.pop(varname, None)
        if yvd__cnocp is None and varname is not None:
            yvd__cnocp = self.flags.h5_types.get(varname, None)
        return yvd__cnocp
