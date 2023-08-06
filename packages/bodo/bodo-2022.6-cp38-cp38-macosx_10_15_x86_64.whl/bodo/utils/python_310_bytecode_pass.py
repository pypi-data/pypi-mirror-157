"""
transforms the IR to handle bytecode issues in Python 3.10. This
should be removed once https://github.com/numba/numba/pull/7866
is included in Numba 0.56
"""
import operator
import numba
from numba.core import ir
from numba.core.compiler_machinery import FunctionPass, register_pass
from numba.core.errors import UnsupportedError
from numba.core.ir_utils import dprint_func_ir, get_definition, guard


@register_pass(mutates_CFG=False, analysis_only=False)
class Bodo310ByteCodePass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        dprint_func_ir(state.func_ir,
            'starting Bodo 3.10 Bytecode optimizations pass')
        peep_hole_call_function_ex_to_call_function_kw(state.func_ir)
        peep_hole_fuse_dict_add_updates(state.func_ir)
        return True


def _call_function_ex_replace_kws_small(keyword_expr, new_body, buildmap_idx):
    uzh__dloos = keyword_expr.items.copy()
    wphki__ruu = keyword_expr.value_indexes
    for eig__wottu, myuj__tbh in wphki__ruu.items():
        uzh__dloos[myuj__tbh] = eig__wottu, uzh__dloos[myuj__tbh][1]
    new_body[buildmap_idx] = None
    return uzh__dloos


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    dff__vgj = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    uzh__dloos = []
    uuhmg__qnex = buildmap_idx + 1
    while uuhmg__qnex <= search_end:
        lwxl__sgk = body[uuhmg__qnex]
        if not (isinstance(lwxl__sgk, ir.Assign) and isinstance(lwxl__sgk.
            value, ir.Const)):
            raise UnsupportedError(dff__vgj)
        zjje__sgdzv = lwxl__sgk.target.name
        ylhg__hwcs = lwxl__sgk.value.value
        uuhmg__qnex += 1
        mpukc__jtnd = True
        while uuhmg__qnex <= search_end and mpukc__jtnd:
            wveju__dpnrm = body[uuhmg__qnex]
            if (isinstance(wveju__dpnrm, ir.Assign) and isinstance(
                wveju__dpnrm.value, ir.Expr) and wveju__dpnrm.value.op ==
                'getattr' and wveju__dpnrm.value.value.name ==
                buildmap_name and wveju__dpnrm.value.attr == '__setitem__'):
                mpukc__jtnd = False
            else:
                uuhmg__qnex += 1
        if mpukc__jtnd or uuhmg__qnex == search_end:
            raise UnsupportedError(dff__vgj)
        asjpg__hqil = body[uuhmg__qnex + 1]
        if not (isinstance(asjpg__hqil, ir.Assign) and isinstance(
            asjpg__hqil.value, ir.Expr) and asjpg__hqil.value.op == 'call' and
            asjpg__hqil.value.func.name == wveju__dpnrm.target.name and len
            (asjpg__hqil.value.args) == 2 and asjpg__hqil.value.args[0].
            name == zjje__sgdzv):
            raise UnsupportedError(dff__vgj)
        mslkw__agwb = asjpg__hqil.value.args[1]
        uzh__dloos.append((ylhg__hwcs, mslkw__agwb))
        new_body[uuhmg__qnex] = None
        new_body[uuhmg__qnex + 1] = None
        uuhmg__qnex += 2
    return uzh__dloos


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    dff__vgj = 'CALL_FUNCTION_EX with **kwargs not supported'
    uuhmg__qnex = 0
    jkmw__pftmx = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        iyxvv__mee = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        iyxvv__mee = vararg_stmt.target.name
    tbcc__ybz = True
    while search_end >= uuhmg__qnex and tbcc__ybz:
        xqjo__euyex = body[search_end]
        if (isinstance(xqjo__euyex, ir.Assign) and xqjo__euyex.target.name ==
            iyxvv__mee and isinstance(xqjo__euyex.value, ir.Expr) and 
            xqjo__euyex.value.op == 'build_tuple' and not xqjo__euyex.value
            .items):
            tbcc__ybz = False
            new_body[search_end] = None
        else:
            if search_end == uuhmg__qnex or not (isinstance(xqjo__euyex, ir
                .Assign) and xqjo__euyex.target.name == iyxvv__mee and
                isinstance(xqjo__euyex.value, ir.Expr) and xqjo__euyex.
                value.op == 'binop' and xqjo__euyex.value.fn == operator.add):
                raise UnsupportedError(dff__vgj)
            std__zqdu = xqjo__euyex.value.lhs.name
            ewa__oyq = xqjo__euyex.value.rhs.name
            hjxyz__qilx = body[search_end - 1]
            if not (isinstance(hjxyz__qilx, ir.Assign) and isinstance(
                hjxyz__qilx.value, ir.Expr) and hjxyz__qilx.value.op ==
                'build_tuple' and len(hjxyz__qilx.value.items) == 1):
                raise UnsupportedError(dff__vgj)
            if hjxyz__qilx.target.name == std__zqdu:
                iyxvv__mee = ewa__oyq
            elif hjxyz__qilx.target.name == ewa__oyq:
                iyxvv__mee = std__zqdu
            else:
                raise UnsupportedError(dff__vgj)
            jkmw__pftmx.append(hjxyz__qilx.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            jhf__wdg = True
            while search_end >= uuhmg__qnex and jhf__wdg:
                vzi__bfna = body[search_end]
                if isinstance(vzi__bfna, ir.Assign
                    ) and vzi__bfna.target.name == iyxvv__mee:
                    jhf__wdg = False
                else:
                    search_end -= 1
    if tbcc__ybz:
        raise UnsupportedError(dff__vgj)
    return jkmw__pftmx[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    dff__vgj = 'CALL_FUNCTION_EX with **kwargs not supported'
    for wpuxd__swtf in func_ir.blocks.values():
        dejh__lxcj = False
        new_body = []
        for fxui__yuv, hssc__dtauf in enumerate(wpuxd__swtf.body):
            if (isinstance(hssc__dtauf, ir.Assign) and isinstance(
                hssc__dtauf.value, ir.Expr) and hssc__dtauf.value.op ==
                'call' and hssc__dtauf.value.varkwarg is not None):
                dejh__lxcj = True
                zxv__yuyk = hssc__dtauf.value
                args = zxv__yuyk.args
                uzh__dloos = zxv__yuyk.kws
                uwjbc__jowx = zxv__yuyk.vararg
                ojxf__ywvz = zxv__yuyk.varkwarg
                qyatq__gek = fxui__yuv - 1
                ajxk__vow = qyatq__gek
                cjes__zkpvw = None
                jskia__sjsjd = True
                while ajxk__vow >= 0 and jskia__sjsjd:
                    cjes__zkpvw = wpuxd__swtf.body[ajxk__vow]
                    if isinstance(cjes__zkpvw, ir.Assign
                        ) and cjes__zkpvw.target.name == ojxf__ywvz.name:
                        jskia__sjsjd = False
                    else:
                        ajxk__vow -= 1
                if uzh__dloos or jskia__sjsjd or not (isinstance(
                    cjes__zkpvw.value, ir.Expr) and cjes__zkpvw.value.op ==
                    'build_map'):
                    raise UnsupportedError(dff__vgj)
                if cjes__zkpvw.value.items:
                    uzh__dloos = _call_function_ex_replace_kws_small(
                        cjes__zkpvw.value, new_body, ajxk__vow)
                else:
                    uzh__dloos = _call_function_ex_replace_kws_large(
                        wpuxd__swtf.body, ojxf__ywvz.name, ajxk__vow, 
                        fxui__yuv - 1, new_body)
                qyatq__gek = ajxk__vow
                if uwjbc__jowx is not None:
                    if args:
                        raise UnsupportedError(dff__vgj)
                    ann__dldzq = qyatq__gek
                    pyr__ukl = None
                    jskia__sjsjd = True
                    while ann__dldzq >= 0 and jskia__sjsjd:
                        pyr__ukl = wpuxd__swtf.body[ann__dldzq]
                        if isinstance(pyr__ukl, ir.Assign
                            ) and pyr__ukl.target.name == uwjbc__jowx.name:
                            jskia__sjsjd = False
                        else:
                            ann__dldzq -= 1
                    if jskia__sjsjd:
                        raise UnsupportedError(dff__vgj)
                    if isinstance(pyr__ukl.value, ir.Expr
                        ) and pyr__ukl.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(pyr__ukl
                            .value, new_body, ann__dldzq)
                    else:
                        args = _call_function_ex_replace_args_large(pyr__ukl,
                            wpuxd__swtf.body, new_body, ann__dldzq)
                ubly__bjeti = ir.Expr.call(zxv__yuyk.func, args, uzh__dloos,
                    zxv__yuyk.loc, target=zxv__yuyk.target)
                if hssc__dtauf.target.name in func_ir._definitions and len(
                    func_ir._definitions[hssc__dtauf.target.name]) == 1:
                    func_ir._definitions[hssc__dtauf.target.name].clear()
                func_ir._definitions[hssc__dtauf.target.name].append(
                    ubly__bjeti)
                hssc__dtauf = ir.Assign(ubly__bjeti, hssc__dtauf.target,
                    hssc__dtauf.loc)
            new_body.append(hssc__dtauf)
        if dejh__lxcj:
            wpuxd__swtf.body = [ukmfy__mcmbv for ukmfy__mcmbv in new_body if
                ukmfy__mcmbv is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for wpuxd__swtf in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        dejh__lxcj = False
        for fxui__yuv, hssc__dtauf in enumerate(wpuxd__swtf.body):
            rhhnx__faz = True
            ckqjp__awq = None
            if isinstance(hssc__dtauf, ir.Assign) and isinstance(hssc__dtauf
                .value, ir.Expr):
                if hssc__dtauf.value.op == 'build_map':
                    ckqjp__awq = hssc__dtauf.target.name
                    lit_old_idx[hssc__dtauf.target.name] = fxui__yuv
                    lit_new_idx[hssc__dtauf.target.name] = fxui__yuv
                    map_updates[hssc__dtauf.target.name
                        ] = hssc__dtauf.value.items.copy()
                    rhhnx__faz = False
                elif hssc__dtauf.value.op == 'call' and fxui__yuv > 0:
                    dtdb__dwxf = hssc__dtauf.value.func.name
                    wveju__dpnrm = wpuxd__swtf.body[fxui__yuv - 1]
                    args = hssc__dtauf.value.args
                    if (isinstance(wveju__dpnrm, ir.Assign) and 
                        wveju__dpnrm.target.name == dtdb__dwxf and
                        isinstance(wveju__dpnrm.value, ir.Expr) and 
                        wveju__dpnrm.value.op == 'getattr' and wveju__dpnrm
                        .value.value.name in lit_old_idx):
                        sudu__kqr = wveju__dpnrm.value.value.name
                        vkkjo__wrtiy = wveju__dpnrm.value.attr
                        if vkkjo__wrtiy == '__setitem__':
                            rhhnx__faz = False
                            map_updates[sudu__kqr].append(args)
                            new_body[-1] = None
                        elif vkkjo__wrtiy == 'update' and args[0
                            ].name in lit_old_idx:
                            rhhnx__faz = False
                            map_updates[sudu__kqr].extend(map_updates[args[
                                0].name])
                            new_body[-1] = None
                        if not rhhnx__faz:
                            lit_new_idx[sudu__kqr] = fxui__yuv
                            func_ir._definitions[wveju__dpnrm.target.name
                                ].remove(wveju__dpnrm.value)
            if not (isinstance(hssc__dtauf, ir.Assign) and isinstance(
                hssc__dtauf.value, ir.Expr) and hssc__dtauf.value.op ==
                'getattr' and hssc__dtauf.value.value.name in lit_old_idx and
                hssc__dtauf.value.attr in ('__setitem__', 'update')):
                for lrqr__eed in hssc__dtauf.list_vars():
                    if (lrqr__eed.name in lit_old_idx and lrqr__eed.name !=
                        ckqjp__awq):
                        _insert_build_map(func_ir, lrqr__eed.name,
                            wpuxd__swtf.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if rhhnx__faz:
                new_body.append(hssc__dtauf)
            else:
                func_ir._definitions[hssc__dtauf.target.name].remove(
                    hssc__dtauf.value)
                dejh__lxcj = True
                new_body.append(None)
        whk__zrd = list(lit_old_idx.keys())
        for sfj__xvbn in whk__zrd:
            _insert_build_map(func_ir, sfj__xvbn, wpuxd__swtf.body,
                new_body, lit_old_idx, lit_new_idx, map_updates)
        if dejh__lxcj:
            wpuxd__swtf.body = [ukmfy__mcmbv for ukmfy__mcmbv in new_body if
                ukmfy__mcmbv is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    yexgx__yff = lit_old_idx[name]
    zwjw__cbic = lit_new_idx[name]
    llm__ipz = map_updates[name]
    new_body[zwjw__cbic] = _build_new_build_map(func_ir, name, old_body,
        yexgx__yff, llm__ipz)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    sgq__jnk = old_body[old_lineno]
    loz__nwh = sgq__jnk.target
    nlrhu__tka = sgq__jnk.value
    tdb__qnl = []
    rlkv__msnzo = []
    for rvcwm__eeljh in new_items:
        xufi__kwtys, qfd__ukhn = rvcwm__eeljh
        jrlw__esa = guard(get_definition, func_ir, xufi__kwtys)
        if isinstance(jrlw__esa, (ir.Const, ir.Global, ir.FreeVar)):
            tdb__qnl.append(jrlw__esa.value)
        chu__zytqq = guard(get_definition, func_ir, qfd__ukhn)
        if isinstance(chu__zytqq, (ir.Const, ir.Global, ir.FreeVar)):
            rlkv__msnzo.append(chu__zytqq.value)
        else:
            rlkv__msnzo.append(numba.core.interpreter._UNKNOWN_VALUE(
                qfd__ukhn.name))
    wphki__ruu = {}
    if len(tdb__qnl) == len(new_items):
        skh__sercd = {ukmfy__mcmbv: kky__lrdl for ukmfy__mcmbv, kky__lrdl in
            zip(tdb__qnl, rlkv__msnzo)}
        for fxui__yuv, xufi__kwtys in enumerate(tdb__qnl):
            wphki__ruu[xufi__kwtys] = fxui__yuv
    else:
        skh__sercd = None
    ogq__kvows = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=skh__sercd, value_indexes=wphki__ruu, loc=nlrhu__tka.loc)
    func_ir._definitions[name].append(ogq__kvows)
    return ir.Assign(ogq__kvows, ir.Var(loz__nwh.scope, name, loz__nwh.loc),
        ogq__kvows.loc)
