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
        ndh__btb = self._get_h5_type(lhs, rhs)
        if ndh__btb is not None:
            mow__jdw = str(ndh__btb.dtype)
            act__ofjc = 'def _h5_read_impl(dset, index):\n'
            act__ofjc += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(ndh__btb.ndim, mow__jdw))
            tva__mhhc = {}
            exec(act__ofjc, {}, tva__mhhc)
            myrx__skac = tva__mhhc['_h5_read_impl']
            yytkw__koyn = compile_to_numba_ir(myrx__skac, {'bodo': bodo}
                ).blocks.popitem()[1]
            ikzjf__mmsc = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(yytkw__koyn, [rhs.value, ikzjf__mmsc])
            hxcv__fcgpw = yytkw__koyn.body[:-3]
            hxcv__fcgpw[-1].target = assign.target
            return hxcv__fcgpw
        return None

    def _get_h5_type(self, lhs, rhs):
        ndh__btb = self._get_h5_type_locals(lhs)
        if ndh__btb is not None:
            return ndh__btb
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        ikzjf__mmsc = rhs.index if rhs.op == 'getitem' else rhs.index_var
        iat__umwmr = guard(find_const, self.func_ir, ikzjf__mmsc)
        require(not isinstance(iat__umwmr, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            xfv__xyj = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            jegyv__dqq = get_const_value_inner(self.func_ir, xfv__xyj,
                arg_types=self.arg_types)
            obj_name_list.append(jegyv__dqq)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        ibs__xwz = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        wigua__sqxfm = h5py.File(ibs__xwz, 'r')
        iwwd__cfk = wigua__sqxfm
        for jegyv__dqq in obj_name_list:
            iwwd__cfk = iwwd__cfk[jegyv__dqq]
        require(isinstance(iwwd__cfk, h5py.Dataset))
        wgscm__upwj = len(iwwd__cfk.shape)
        ngf__jcb = numba.np.numpy_support.from_dtype(iwwd__cfk.dtype)
        wigua__sqxfm.close()
        return types.Array(ngf__jcb, wgscm__upwj, 'C')

    def _get_h5_type_locals(self, varname):
        bucuz__zsffh = self.locals.pop(varname, None)
        if bucuz__zsffh is None and varname is not None:
            bucuz__zsffh = self.flags.h5_types.get(varname, None)
        return bucuz__zsffh
