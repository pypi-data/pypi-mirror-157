"""
Implements array kernels that are specific to BodoSQL
"""
import numba
import numpy as np
from numba.core import types
from numba.extending import overload
import bodo
from bodo.utils.typing import raise_bodo_error


def gen_vectorized(arg_names, arg_types, propogate_null, scalar_text,
    constructor_text, arg_string=None):
    ouuz__kmgsa = [bodo.utils.utils.is_array_typ(boz__kjt, True) for
        boz__kjt in arg_types]
    mkgd__ztymf = not any(ouuz__kmgsa)
    cnys__akcgn = any([propogate_null[i] for i in range(len(arg_types)) if 
        arg_types[i] == bodo.none])
    ktltt__snr = scalar_text.splitlines()[0]
    qhsze__zek = len(ktltt__snr) - len(ktltt__snr.lstrip())
    if arg_string == None:
        arg_string = ', '.join(arg_names)
    gdh__gwo = f'def impl({arg_string}):\n'
    if mkgd__ztymf:
        if cnys__akcgn:
            gdh__gwo += '   return None'
        else:
            for i in range(len(arg_names)):
                gdh__gwo += f'   arg{i} = {arg_names[i]}\n'
            for ehahg__beu in scalar_text.splitlines():
                gdh__gwo += ' ' * 3 + ehahg__beu[qhsze__zek:].replace(
                    'res[i] =', 'answer =') + '\n'
            gdh__gwo += '   return answer'
    else:
        nwo__uwrv = False
        for i in range(len(arg_names)):
            if ouuz__kmgsa[i]:
                if not nwo__uwrv:
                    ehq__mmozc = f'len({arg_names[i]})'
                    nwo__uwrv = True
                if not bodo.utils.utils.is_array_typ(arg_types[i], False):
                    gdh__gwo += f"""   {arg_names[i]} = bodo.hiframes.pd_series_ext.get_series_data({arg_names[i]})
"""
        gdh__gwo += f'   n = {ehq__mmozc}\n'
        gdh__gwo += f'   res = {constructor_text}\n'
        gdh__gwo += '   for i in range(n):\n'
        if cnys__akcgn:
            gdh__gwo += f'      bodo.libs.array_kernels.setna(res, i)\n'
        else:
            for i in range(len(arg_names)):
                if ouuz__kmgsa[i]:
                    if propogate_null[i]:
                        gdh__gwo += (
                            f'      if bodo.libs.array_kernels.isna({arg_names[i]}, i):\n'
                            )
                        gdh__gwo += (
                            '         bodo.libs.array_kernels.setna(res, i)\n')
                        gdh__gwo += '         continue\n'
            for i in range(len(arg_names)):
                if ouuz__kmgsa[i]:
                    gdh__gwo += f'      arg{i} = {arg_names[i]}[i]\n'
                else:
                    gdh__gwo += f'      arg{i} = {arg_names[i]}\n'
            for ehahg__beu in scalar_text.splitlines():
                gdh__gwo += ' ' * 6 + ehahg__beu[qhsze__zek:] + '\n'
        gdh__gwo += (
            '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, n, 1), None)'
            )
    imxs__fenx = {}
    exec(gdh__gwo, {'bodo': bodo, 'numba': numba, 'np': np}, imxs__fenx)
    impl = imxs__fenx['impl']
    return impl


def unopt_argument(func_name, arg_names, i):
    exvxg__gth = [(arg_names[vvgy__nhrs] if vvgy__nhrs != i else 'None') for
        vvgy__nhrs in range(len(arg_names))]
    ufk__gsuj = [(arg_names[vvgy__nhrs] if vvgy__nhrs != i else
        f'bodo.utils.indexing.unoptional({arg_names[vvgy__nhrs]})') for
        vvgy__nhrs in range(len(arg_names))]
    gdh__gwo = f"def impl({', '.join(arg_names)}):\n"
    gdh__gwo += f'   if {arg_names[i]} is None:\n'
    gdh__gwo += f"      return {func_name}({', '.join(exvxg__gth)})\n"
    gdh__gwo += f'   else:\n'
    gdh__gwo += f"      return {func_name}({', '.join(ufk__gsuj)})"
    imxs__fenx = {}
    exec(gdh__gwo, {'bodo': bodo, 'numba': numba}, imxs__fenx)
    impl = imxs__fenx['impl']
    return impl


def lpad(arr, length, padstr):
    return


def rpad(arr, length, padstr):
    return


def lpad_util(arr, length, padstr):
    return


def rpad_util(arr, length, padstr):
    return


@overload(lpad)
def overload_lpad(arr, length, padstr):
    args = [arr, length, padstr]
    for i in range(3):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.lpad', [
                'arr', 'length', 'padstr'], i)

    def impl(arr, length, padstr):
        return lpad_util(arr, length, padstr)
    return impl


@overload(rpad)
def overload_rpad(arr, length, padstr):
    args = [arr, length, padstr]
    for i in range(3):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.rpad', [
                'arr', 'length', 'padstr'], i)

    def impl(arr, length, padstr):
        return rpad_util(arr, length, padstr)
    return impl


def create_lpad_rpad_util_overload(func_name):

    def overload_lpad_rpad_util(arr, length, pad_string):
        if arr not in (types.none, types.unicode_type) and not (bodo.utils.
            utils.is_array_typ(arr, True) and arr.dtype == types.unicode_type):
            raise_bodo_error(
                f'{func_name} can only be applied to strings, string columns, or null'
                )
        if length not in (types.none, *types.integer_domain) and not (bodo.
            utils.utils.is_array_typ(length, True) and length.dtype in
            types.integer_domain):
            raise_bodo_error(
                f'{func_name} length argument must be an integer, integer column, or null'
                )
        if pad_string not in (types.none, types.unicode_type) and not (bodo
            .utils.utils.is_array_typ(pad_string, True) and pad_string.
            dtype == types.unicode_type):
            raise_bodo_error(
                f'{func_name} {func_name.lower()}_string argument must be a string, string column, or null'
                )
        if func_name == 'LPAD':
            pfoiv__jkouj = f'(arg2 * quotient) + arg2[:remainder] + arg0'
        elif func_name == 'RPAD':
            pfoiv__jkouj = f'arg0 + (arg2 * quotient) + arg2[:remainder]'
        arg_names = ['arr', 'length', 'pad_string']
        arg_types = [arr, length, pad_string]
        propogate_null = [True] * 3
        scalar_text = f"""            if arg1 <= 0:
                res[i] =  ''
            elif len(arg2) == 0:
                res[i] = arg0
            elif len(arg0) >= arg1:
                res[i] = arg0[:arg1]
            else:
                quotient = (arg1 - len(arg0)) // len(arg2)
                remainder = (arg1 - len(arg0)) % len(arg2)
                res[i] = {pfoiv__jkouj}"""
        constructor_text = (
            'bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)')
        return gen_vectorized(arg_names, arg_types, propogate_null,
            scalar_text, constructor_text)
    return overload_lpad_rpad_util


def _install_lpad_rpad_overload():
    for tcae__bjtet, func_name in zip((lpad_util, rpad_util), ('LPAD', 'RPAD')
        ):
        gjnp__ufeyy = create_lpad_rpad_util_overload(func_name)
        overload(tcae__bjtet)(gjnp__ufeyy)


_install_lpad_rpad_overload()
