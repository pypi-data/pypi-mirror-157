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
    jrqve__jte = keyword_expr.items.copy()
    thck__ymb = keyword_expr.value_indexes
    for wmmas__khd, dizh__iihdf in thck__ymb.items():
        jrqve__jte[dizh__iihdf] = wmmas__khd, jrqve__jte[dizh__iihdf][1]
    new_body[buildmap_idx] = None
    return jrqve__jte


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    lgvm__ars = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    jrqve__jte = []
    edbz__urlji = buildmap_idx + 1
    while edbz__urlji <= search_end:
        zoyk__kkkbw = body[edbz__urlji]
        if not (isinstance(zoyk__kkkbw, ir.Assign) and isinstance(
            zoyk__kkkbw.value, ir.Const)):
            raise UnsupportedError(lgvm__ars)
        rttq__vppy = zoyk__kkkbw.target.name
        yzqx__emtfj = zoyk__kkkbw.value.value
        edbz__urlji += 1
        ojlid__tcpl = True
        while edbz__urlji <= search_end and ojlid__tcpl:
            qnece__ornqf = body[edbz__urlji]
            if (isinstance(qnece__ornqf, ir.Assign) and isinstance(
                qnece__ornqf.value, ir.Expr) and qnece__ornqf.value.op ==
                'getattr' and qnece__ornqf.value.value.name ==
                buildmap_name and qnece__ornqf.value.attr == '__setitem__'):
                ojlid__tcpl = False
            else:
                edbz__urlji += 1
        if ojlid__tcpl or edbz__urlji == search_end:
            raise UnsupportedError(lgvm__ars)
        rhbx__miec = body[edbz__urlji + 1]
        if not (isinstance(rhbx__miec, ir.Assign) and isinstance(rhbx__miec
            .value, ir.Expr) and rhbx__miec.value.op == 'call' and 
            rhbx__miec.value.func.name == qnece__ornqf.target.name and len(
            rhbx__miec.value.args) == 2 and rhbx__miec.value.args[0].name ==
            rttq__vppy):
            raise UnsupportedError(lgvm__ars)
        bpny__qouyw = rhbx__miec.value.args[1]
        jrqve__jte.append((yzqx__emtfj, bpny__qouyw))
        new_body[edbz__urlji] = None
        new_body[edbz__urlji + 1] = None
        edbz__urlji += 2
    return jrqve__jte


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    lgvm__ars = 'CALL_FUNCTION_EX with **kwargs not supported'
    edbz__urlji = 0
    xda__jyrnz = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        vhxus__wxks = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        vhxus__wxks = vararg_stmt.target.name
    nzj__maxqi = True
    while search_end >= edbz__urlji and nzj__maxqi:
        mffa__ead = body[search_end]
        if (isinstance(mffa__ead, ir.Assign) and mffa__ead.target.name ==
            vhxus__wxks and isinstance(mffa__ead.value, ir.Expr) and 
            mffa__ead.value.op == 'build_tuple' and not mffa__ead.value.items):
            nzj__maxqi = False
            new_body[search_end] = None
        else:
            if search_end == edbz__urlji or not (isinstance(mffa__ead, ir.
                Assign) and mffa__ead.target.name == vhxus__wxks and
                isinstance(mffa__ead.value, ir.Expr) and mffa__ead.value.op ==
                'binop' and mffa__ead.value.fn == operator.add):
                raise UnsupportedError(lgvm__ars)
            wwg__xaf = mffa__ead.value.lhs.name
            frqa__fvjav = mffa__ead.value.rhs.name
            nszar__cnsx = body[search_end - 1]
            if not (isinstance(nszar__cnsx, ir.Assign) and isinstance(
                nszar__cnsx.value, ir.Expr) and nszar__cnsx.value.op ==
                'build_tuple' and len(nszar__cnsx.value.items) == 1):
                raise UnsupportedError(lgvm__ars)
            if nszar__cnsx.target.name == wwg__xaf:
                vhxus__wxks = frqa__fvjav
            elif nszar__cnsx.target.name == frqa__fvjav:
                vhxus__wxks = wwg__xaf
            else:
                raise UnsupportedError(lgvm__ars)
            xda__jyrnz.append(nszar__cnsx.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            xfijg__jig = True
            while search_end >= edbz__urlji and xfijg__jig:
                ofp__qgpd = body[search_end]
                if isinstance(ofp__qgpd, ir.Assign
                    ) and ofp__qgpd.target.name == vhxus__wxks:
                    xfijg__jig = False
                else:
                    search_end -= 1
    if nzj__maxqi:
        raise UnsupportedError(lgvm__ars)
    return xda__jyrnz[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    lgvm__ars = 'CALL_FUNCTION_EX with **kwargs not supported'
    for grlg__biiz in func_ir.blocks.values():
        rqnt__uoe = False
        new_body = []
        for pwo__tbs, phwhz__res in enumerate(grlg__biiz.body):
            if (isinstance(phwhz__res, ir.Assign) and isinstance(phwhz__res
                .value, ir.Expr) and phwhz__res.value.op == 'call' and 
                phwhz__res.value.varkwarg is not None):
                rqnt__uoe = True
                smte__ztwun = phwhz__res.value
                args = smte__ztwun.args
                jrqve__jte = smte__ztwun.kws
                ebva__jpezb = smte__ztwun.vararg
                xyrn__upzo = smte__ztwun.varkwarg
                ncr__bvn = pwo__tbs - 1
                jcd__obrgt = ncr__bvn
                pwqb__gyga = None
                lnza__dky = True
                while jcd__obrgt >= 0 and lnza__dky:
                    pwqb__gyga = grlg__biiz.body[jcd__obrgt]
                    if isinstance(pwqb__gyga, ir.Assign
                        ) and pwqb__gyga.target.name == xyrn__upzo.name:
                        lnza__dky = False
                    else:
                        jcd__obrgt -= 1
                if jrqve__jte or lnza__dky or not (isinstance(pwqb__gyga.
                    value, ir.Expr) and pwqb__gyga.value.op == 'build_map'):
                    raise UnsupportedError(lgvm__ars)
                if pwqb__gyga.value.items:
                    jrqve__jte = _call_function_ex_replace_kws_small(pwqb__gyga
                        .value, new_body, jcd__obrgt)
                else:
                    jrqve__jte = _call_function_ex_replace_kws_large(grlg__biiz
                        .body, xyrn__upzo.name, jcd__obrgt, pwo__tbs - 1,
                        new_body)
                ncr__bvn = jcd__obrgt
                if ebva__jpezb is not None:
                    if args:
                        raise UnsupportedError(lgvm__ars)
                    xkqa__gbgqr = ncr__bvn
                    voyl__rjxp = None
                    lnza__dky = True
                    while xkqa__gbgqr >= 0 and lnza__dky:
                        voyl__rjxp = grlg__biiz.body[xkqa__gbgqr]
                        if isinstance(voyl__rjxp, ir.Assign
                            ) and voyl__rjxp.target.name == ebva__jpezb.name:
                            lnza__dky = False
                        else:
                            xkqa__gbgqr -= 1
                    if lnza__dky:
                        raise UnsupportedError(lgvm__ars)
                    if isinstance(voyl__rjxp.value, ir.Expr
                        ) and voyl__rjxp.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(voyl__rjxp
                            .value, new_body, xkqa__gbgqr)
                    else:
                        args = _call_function_ex_replace_args_large(voyl__rjxp,
                            grlg__biiz.body, new_body, xkqa__gbgqr)
                afbjv__uennc = ir.Expr.call(smte__ztwun.func, args,
                    jrqve__jte, smte__ztwun.loc, target=smte__ztwun.target)
                if phwhz__res.target.name in func_ir._definitions and len(
                    func_ir._definitions[phwhz__res.target.name]) == 1:
                    func_ir._definitions[phwhz__res.target.name].clear()
                func_ir._definitions[phwhz__res.target.name].append(
                    afbjv__uennc)
                phwhz__res = ir.Assign(afbjv__uennc, phwhz__res.target,
                    phwhz__res.loc)
            new_body.append(phwhz__res)
        if rqnt__uoe:
            grlg__biiz.body = [vmsev__bisxn for vmsev__bisxn in new_body if
                vmsev__bisxn is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for grlg__biiz in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        rqnt__uoe = False
        for pwo__tbs, phwhz__res in enumerate(grlg__biiz.body):
            uryzk__jytpf = True
            obqjo__xlrvr = None
            if isinstance(phwhz__res, ir.Assign) and isinstance(phwhz__res.
                value, ir.Expr):
                if phwhz__res.value.op == 'build_map':
                    obqjo__xlrvr = phwhz__res.target.name
                    lit_old_idx[phwhz__res.target.name] = pwo__tbs
                    lit_new_idx[phwhz__res.target.name] = pwo__tbs
                    map_updates[phwhz__res.target.name
                        ] = phwhz__res.value.items.copy()
                    uryzk__jytpf = False
                elif phwhz__res.value.op == 'call' and pwo__tbs > 0:
                    bsib__dgd = phwhz__res.value.func.name
                    qnece__ornqf = grlg__biiz.body[pwo__tbs - 1]
                    args = phwhz__res.value.args
                    if (isinstance(qnece__ornqf, ir.Assign) and 
                        qnece__ornqf.target.name == bsib__dgd and
                        isinstance(qnece__ornqf.value, ir.Expr) and 
                        qnece__ornqf.value.op == 'getattr' and qnece__ornqf
                        .value.value.name in lit_old_idx):
                        dmp__prvg = qnece__ornqf.value.value.name
                        fgy__irnl = qnece__ornqf.value.attr
                        if fgy__irnl == '__setitem__':
                            uryzk__jytpf = False
                            map_updates[dmp__prvg].append(args)
                            new_body[-1] = None
                        elif fgy__irnl == 'update' and args[0
                            ].name in lit_old_idx:
                            uryzk__jytpf = False
                            map_updates[dmp__prvg].extend(map_updates[args[
                                0].name])
                            new_body[-1] = None
                        if not uryzk__jytpf:
                            lit_new_idx[dmp__prvg] = pwo__tbs
                            func_ir._definitions[qnece__ornqf.target.name
                                ].remove(qnece__ornqf.value)
            if not (isinstance(phwhz__res, ir.Assign) and isinstance(
                phwhz__res.value, ir.Expr) and phwhz__res.value.op ==
                'getattr' and phwhz__res.value.value.name in lit_old_idx and
                phwhz__res.value.attr in ('__setitem__', 'update')):
                for dzfek__amzs in phwhz__res.list_vars():
                    if (dzfek__amzs.name in lit_old_idx and dzfek__amzs.
                        name != obqjo__xlrvr):
                        _insert_build_map(func_ir, dzfek__amzs.name,
                            grlg__biiz.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if uryzk__jytpf:
                new_body.append(phwhz__res)
            else:
                func_ir._definitions[phwhz__res.target.name].remove(phwhz__res
                    .value)
                rqnt__uoe = True
                new_body.append(None)
        icci__chew = list(lit_old_idx.keys())
        for cuw__hhy in icci__chew:
            _insert_build_map(func_ir, cuw__hhy, grlg__biiz.body, new_body,
                lit_old_idx, lit_new_idx, map_updates)
        if rqnt__uoe:
            grlg__biiz.body = [vmsev__bisxn for vmsev__bisxn in new_body if
                vmsev__bisxn is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    cojzd__khbl = lit_old_idx[name]
    sjet__wpafr = lit_new_idx[name]
    edr__vfqc = map_updates[name]
    new_body[sjet__wpafr] = _build_new_build_map(func_ir, name, old_body,
        cojzd__khbl, edr__vfqc)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    zgixt__tvys = old_body[old_lineno]
    lbw__yct = zgixt__tvys.target
    uwj__fncal = zgixt__tvys.value
    bocqx__wim = []
    kaz__yda = []
    for rnise__qvrb in new_items:
        iajlu__xspt, iqs__jsfl = rnise__qvrb
        jpy__tzqe = guard(get_definition, func_ir, iajlu__xspt)
        if isinstance(jpy__tzqe, (ir.Const, ir.Global, ir.FreeVar)):
            bocqx__wim.append(jpy__tzqe.value)
        pzm__cvzd = guard(get_definition, func_ir, iqs__jsfl)
        if isinstance(pzm__cvzd, (ir.Const, ir.Global, ir.FreeVar)):
            kaz__yda.append(pzm__cvzd.value)
        else:
            kaz__yda.append(numba.core.interpreter._UNKNOWN_VALUE(iqs__jsfl
                .name))
    thck__ymb = {}
    if len(bocqx__wim) == len(new_items):
        ayy__gyko = {vmsev__bisxn: xaaf__mfnjq for vmsev__bisxn,
            xaaf__mfnjq in zip(bocqx__wim, kaz__yda)}
        for pwo__tbs, iajlu__xspt in enumerate(bocqx__wim):
            thck__ymb[iajlu__xspt] = pwo__tbs
    else:
        ayy__gyko = None
    hojo__ynzz = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=ayy__gyko, value_indexes=thck__ymb, loc=uwj__fncal.loc)
    func_ir._definitions[name].append(hojo__ynzz)
    return ir.Assign(hojo__ynzz, ir.Var(lbw__yct.scope, name, lbw__yct.loc),
        hojo__ynzz.loc)
