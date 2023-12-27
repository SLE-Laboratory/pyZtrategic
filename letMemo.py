import zipper as zp
import strategy as st
from adt import adt, Case

import sys


@adt
class Root:
    ROOT: Case["Let"]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.match(
            root=lambda l: str(l)
        )


@adt
class Let:
    LET: Case["List", "Exp"]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.match(
            let=lambda l, e: "let " + str(l) + "in " + str(e) + "\n"
        )


@adt
class List:
    NESTEDLET: Case[str, "Let", "List"]
    ASSIGN: Case[str, "Exp", "List"]
    EMPTY: Case

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.match(
            nestedlet=lambda s, l, r: s + " = " + str(l) + str(r),
            assign=lambda s, e, l: s + " = " + str(e) + "\n" + str(l),
            empty=lambda: ""
        )


@adt
class Exp:
    ADD: Case["Exp", "Exp"]
    SUB: Case["Exp", "Exp"]
    NEG: Case["Exp"]
    VAR: Case[str]
    CONST: Case[int]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.match(
            add=lambda x, y: str(x) + " + " + str(y),
            sub=lambda x, y: str(x) + " - " + str(y),
            neg=lambda x: "-" + str(x),
            var=lambda x: x,
            const=lambda x: str(x),
        )


class Constructor:
    CRoot = "CRoot"
    CLet = "CLet"
    CNestedLet = "CNestedLet"
    CAssign = "CAssign"
    CEmpty = "CEmpty"
    CAdd = "CAdd"
    CSub = "CSub"
    CNeg = "CNeg"
    CConst = "CConst"
    CVar = "CVar"


#########################################
# Memo


@adt
class LetM:
    ROOT: Case["LetM", "MemoTable"]
    LET: Case["LetM", "LetM", "MemoTable"]
    NESTEDLET: Case[str, "LetM", "LetM", "MemoTable"]
    ASSIGN: Case[str, "LetM", "LetM", "MemoTable"]
    EMPTY: Case["MemoTable"]
    ADD: Case["LetM", "LetM", "MemoTable"]
    SUB: Case["LetM", "LetM", "MemoTable"]
    NEG: Case["LetM", "MemoTable"]
    VAR: Case[str, "MemoTable"]
    CONST: Case[int, "MemoTable"]


def letMToLet(lt):
    return lt.match(
        root=lambda x, m: Root.ROOT(letMToLet(x)),
        let=lambda x, y, m: Let.LET(letMToLet(x), letMToLet(y)),
        nestedlet=lambda n, x, y, m: List.NESTEDLET(n, letMToLet(x), letMToLet(y)),
        assign=lambda n, x, y, m: List.ASSIGN(n, letMToLet(x), letMToLet(y)),
        empty=lambda m: List.EMPTY(),
        add=lambda x, y, m: Exp.ADD(letMToLet(x), letMToLet(y)),
        sub=lambda x, y, m: Exp.SUB(letMToLet(x), letMToLet(y)),
        neg=lambda x, m: Exp.NEG(letMToLet(x)),
        var=lambda x, m: Exp.VAR(x),
        const=lambda x, m: Exp.CONST(x)
    )


def buildMemoTree(m, lt):
    return lt.match(
        root=lambda x: LetM.ROOT(buildMemoTreeLet(m, x), m)
    )


def buildMemoTreeLet(m, lt):
    return lt.match(
        let=lambda x, y: LetM.LET(buildMemoTreeList(m, x), buildMemoTreeExp(m, y), m)
    )


def buildMemoTreeList(m, lt):
    return lt.match(
        nestedlet=lambda n, x, y: LetM.NESTEDLET(n, buildMemoTreeLet(m, x), buildMemoTreeList(m, y), m),
        assign=lambda n, x, y: LetM.ASSIGN(n, buildMemoTreeExp(m, x), buildMemoTreeList(m, y), m),
        empty=lambda: LetM.EMPTY(m)
    )


def buildMemoTreeExp(m, lt):
    return lt.match(
        add=lambda x, y: LetM.ADD(buildMemoTreeExp(m, x), buildMemoTreeExp(m, y), m),
        sub=lambda x, y: LetM.SUB(buildMemoTreeExp(m, x), buildMemoTreeExp(m, y), m),
        neg=lambda x: LetM.NEG(buildMemoTreeExp(m, x), m),
        var=lambda x: LetM.VAR(x, m),
        const=lambda x: LetM.CONST(x, m)
    )


def updMemoTable(f, lt):
    return lt.match(
        root=lambda x, m: LetM.ROOT(x, f(m)),
        let=lambda x, y, m: LetM.LET(x, y, f(m)),
        nestedlet=lambda n, x, y, m: LetM.NESTEDLET(n, x, y, f(m)),
        assign=lambda n, x, y, m: LetM.ASSIGN(n, x, y, f(m)),
        empty=lambda m: LetM.EMPTY(f(m)),
        add=lambda x, y, m: LetM.ADD(x, y, f(m)),
        sub=lambda x, y, m: LetM.SUB(x, y, f(m)),
        neg=lambda x, m: LetM.NEG(x, f(m)),
        var=lambda x, m: LetM.VAR(x, f(m)),
        const=lambda x, m: LetM.CONST(x, f(m))
    )


def getMemoTable(lt):
    return lt.match(
        root=lambda x, m: m,
        let=lambda x, y, m: m,
        nestedlet=lambda n, x, y, m: m,
        assign=lambda n, x, y, m: m,
        empty=lambda m: m,
        add=lambda x, y, m: m,
        sub=lambda x, y, m: m,
        neg=lambda x, m: m,
        var=lambda x, m: m,
        const=lambda x, m: m
    )


def cleanMemoTable(lt):
    def aux(m):
        return updMemoTable(MemoTable(), m)
    return st.full_tdTP(lambda x: st.adhocTP(st.failTP, aux, x), lt).node()


def constructorM(ag):
    return ag.node().match(
        root=lambda x, m: Constructor.CRoot,
        let=lambda x, y, m: Constructor.CLet,
        nestedlet=lambda x, y, z, m: Constructor.CNestedLet,
        assign=lambda x, y, z, m: Constructor.CAssign,
        empty=lambda m: Constructor.CEmpty,
        add=lambda x, y, m: Constructor.CAdd,
        sub=lambda x, y, m: Constructor.CSub,
        neg=lambda x, m: Constructor.CNeg,
        var=lambda x, m: Constructor.CVar,
        const=lambda x, m: Constructor.CConst
    )


def lexemeM_Name(ag):
    return ag.node().match(
        root=lambda x, m: None,
        let=lambda x, y, m: None,
        nestedlet=lambda x, y, z, m: x,
        assign=lambda x, y, z, m: x,
        empty=lambda m: None,
        var=lambda x, m: x,
        add=lambda x, y, m: None,
        sub=lambda x, y, m: None,
        neg=lambda x, m: None,
        const=lambda x, m: None
        )


def lexemeM_Exp(ag):
    return ag.node().match(
        root=lambda x, m: None,
        let=lambda x, y, m: None,
        assign=lambda x, y, z, m: letMToLet(y),
        nestedlet=lambda x, y, z, m: None,
        empty=lambda m: None,
        var=lambda x, m: None,
        add=lambda x, y, m: None,
        sub=lambda x, y, m: None,
        neg=lambda x, m: None,
        const=lambda x, m: None
    )


class Att_DCLI:
    pass


class Att_DCLO:
    pass


class Att_Lev:
    pass


class Att_Env:
    pass


class Att_Errs:
    pass


class MemoTable:
    def __init__(self):
        self.Att_DCLI = None
        self.Att_DCLO = None
        self.Att_Lev = None
        self.Att_Env = None
        self.Att_Errs = None


def mlookup(att, m):
    if m is None:
        return None
    else:
        match(att):
            case Att_DCLI():
                return m.Att_DCLI
            case Att_DCLO():
                return m.Att_DCLO
            case Att_Env():
                return m.Att_Env
            case Att_Lev():
                return m.Att_Lev
            case Att_Errs():
                return m.Att_Errs


def massign(att, v, m):
    if m is None:
        m = MemoTable()
    match(att):
        case Att_DCLI():
            m.Att_DCLI = v
        case Att_DCLO():
            m.Att_DCLO = v
        case Att_Env():
            m.Att_Env = v
        case Att_Lev():
            m.Att_LEV = v
        case Att_Errs():
            m.Att_Errs = v


def isTerminal(z):
    return not isinstance(z, (MemoTable, int, str))


def at(eval, t):
    v, t_ = eval(t)
    return (v, t_)


def atParent(eval, t):
    n = t.arity()
    v, tp = eval(t.up())
    return (v, tp.z_dollar(n))


def atRight(eval, t):
    v, tp = eval(t.right())
    return (v, tp.left())


def atLeft(eval, t):
    v, tp = eval(t.left())
    return (v, tp.right())


def memo(attr, eval, z):
    v = mlookup(attr, memoTable(z))
    if v is not None:
        return (v, z)
    else:
        v, z_ = eval(z)
        return (v, transTree(attr, v, z_))


def memoTable(z):
    return getMemoTable(z.node())


def upd(attr, v, z):
    return updMemoTable(lambda m: (massign(attr, v, m)), z.node())


def transTree(attr, v, z):
    return z.replace(upd(attr, v, z))

#########################################


def expr(exp):
    x = exp.match(
        add=lambda x, y: y if (x == exp.CONST(0)) else x if (y == exp.CONST(0)) else Exp.CONST(x.const() + y.const()) if (lambda a, b: x == exp.CONST() and y == exp.CONST()) else st.StrategicError,
        sub=lambda x, y: Exp.ADD(x, Exp.NEG(y)),
        neg=lambda x: x.neg() if (lambda a: x == Exp.NEG()) else exp.CONST(-x.neg()) if (lambda b: x == Exp.CONST()) else st.StrategicError,
        var=lambda x: st.StrategicError,
        const=lambda x: st.StrategicError
    )
    if x is st.StrategicError:
        raise x
    else:
        return x


def expC(exp, z):
    x = exp.match(
        add=lambda x, y: st.StrategicError,
        sub=lambda x, y: st.StrategicError,
        neg=lambda x: st.StrategicError,
        var=lambda x: expand((x, lev(z)), env(z)),
        const=lambda x: st.StrategicError
    )
    if x is st.StrategicError:
        raise x
    else:
        return x


def test(exp):
    x = exp.match(
        add=lambda x, y: [x],
        sub=lambda x, y: st.StrategicError(),
        neg=lambda x: st.StrategicError(),
        var=lambda x: st.StrategicError(),
        const=lambda x: st.StrategicError()
    )
    if x is st.StrategicError:
        raise x
    else:
        return x


def constructor(ag):
    if isinstance(ag.node(), Root):
        return ag.node().match(
            root=lambda x: Constructor.CRoot
        )
    elif isinstance(ag.node(), Let):
        return ag.node().match(
            let=lambda x, y: Constructor.CLet
        )
    elif isinstance(ag.node(), List):
        return ag.node().match(
            nestedlet=lambda x, y, z: Constructor.CNestedLet,
            assign=lambda x, y, z: Constructor.CAssign,
            empty=lambda: Constructor.CEmpty
        )
    else:
        return ag.node().match(
            add=lambda x, y: Constructor.CAdd,
            sub=lambda x, y: Constructor.CSub,
            neg=lambda x: Constructor.CNeg,
            var=lambda x: Constructor.CVar,
            const=lambda x: Constructor.CConst
        )


def lexeme_Name(ag):
    if isinstance(ag.node(), List):
        return ag.node().match(
            nestedlet=lambda x, y, z: x,
            assign=lambda x, y, z: x,
            empty=lambda: None
        )
    else:
        return ag.node().match(
            var=lambda x: x,
            add=lambda x, y: None,
            sub=lambda x, y: None,
            neg=lambda x: None,
            const=lambda x: None
        )


def lexeme_Exp(ag):
    return ag.node().match(
        assign=lambda x, y, z: y,
        nestedlet=lambda x, y, z: None,
        empty=lambda: None
    )


def dclo(x):
    return memo(Att_DCLO(), dcloAux, x)


def dcloAux(x):
    match constructorM(x):
        case Constructor.CRoot:
            return at(dclo, x.z_dollar(1))
        case Constructor.CLet:
            return at(dclo, x.z_dollar(1))
        case Constructor.CNestedLet:
            return at(dclo, x.z_dollar(3))
        case Constructor.CAssign:
            return at(dclo, x.z_dollar(3))
        case Constructor.CEmpty:
            return dcli(x)


def dcli(x):
    return memo(Att_DCLI(), dcliAux, x)


def dcliAux(x):
    match constructorM(x):
        case Constructor.CLet:
            match constructorM(x.up()):
                case Constructor.CRoot:
                    return ([], x)
                case Constructor.CNestedLet:
                    return atParent(env, x)
        case _:
            match constructorM(x.up()):
                case Constructor.CLet:
                    return atParent(dcli, x)
                case Constructor.CAssign:
                    levP, y = atParent(lev, x)
                    dcliP, k = atParent(dcli, y)
                    return ([(lexemeM_Name(k.up()), levP, lexemeM_Exp(k.up()))] + dcliP, k)
                case Constructor.CNestedLet:
                    levP, y = atParent(lev, x)
                    dcliP, k = atParent(dcli, y)
                    return ([(lexemeM_Name(k.up()), levP, st.StrategicError)] + dcliP, k)


def env(x):
    return memo(Att_Env(), envAux, x)


def envAux(x):
    match constructorM(x):
        case Constructor.CRoot:
            return dclo(x)
        case Constructor.CLet:
            return dclo(x)
        case _:
            return atParent(env, x)


def lev(x):
    return memo(Att_Lev(), levAux, x)


def levAux(x):
    match constructorM(x):
        case Constructor.CLet:
            match constructorM(x.up()):
                case Constructor.CNestedLet:
                    r, y = atParent(lev, x)
                    return (r+1, y)
                case Constructor.CRoot:
                    return (0, x)
        case _:
            return atParent(lev, x)


def mBIn(name, env):
    if not env:
        return [name]
    elif env[0][0] == name:
        return []
    else:
        return mBIn(name, env[1:])


def mNBIn(t, env):
    if not env:
        return []
    elif t[0] == env[0][0] and t[1] == env[0][1]:
        return [t[0]]
    else:
        return mNBIn(t, env[1:])


def errs(x):
    match constructor(x):
        case Constructor.CRoot:
            return errs(x.z_dollar(1))
        case Constructor.CLet:
            return errs(x.z_dollar(1)) + errs(x.z_dollar(2))
        case Constructor.CAdd:
            return errs(x.z_dollar(1)) + errs(x.z_dollar(2))
        case Constructor.CSub:
            return errs(x.z_dollar(1)) + errs(x.z_dollar(2))
        case Constructor.CEmpty:
            return []
        case Constructor.CConst:
            return []
        case Constructor.CVar:
            return mBIn(lexeme_Name(x), env(x))
        case Constructor.CAssign:
            return mNBIn((lexeme_Name(x), lev(x)), dcli(x)) + errs(x.z_dollar(2)) + errs(x.z_dollar(3))
        case Constructor.CNestedLet:
            return mNBIn((lexeme_Name(x), lev(x)), dcli(x)) + errs(x.z_dollar(2)) + errs(x.z_dollar(3))


def expand(t, e):
    results = sorted(filter(lambda x: x[0] == t[0] and x[1] <= t[1], e), key=lambda x: x[1], reverse=True)
    if results:
        return results[0][2]
    else:
        raise st.StrategicError


#########################################

def exprM(exp):
    x = exp.match(
        root=lambda x, m: st.StrategicError,
        let=lambda x, y, m: st.StrategicError,
        nestedlet=lambda n, x, y, m: st.StrategicError,
        assign=lambda n, x, y, m: st.StrategicError,
        empty=lambda m: st.StrategicError,
        add=lambda x, y, m: y if (x == LetM.CONST(0, getMemoTable(x))) else x if (y == LetM.CONST(0, getMemoTable(y))) else LetM.CONST(x.const()[0] + y.const()[0], m) if (lambda a, b: x == LetM.CONST() and y == LetM.CONST()) else st.StrategicError,
        sub=lambda x, y, m: LetM.ADD(x, LetM.NEG(y, MemoTable()), MemoTable()),
        neg=lambda x, m: x.neg()[0] if (lambda a: x == LetM.NEG()) else LetM.CONST(-x.neg()[0], m) if (lambda b, g: x == LetM.CONST()) else st.StrategicError,
        var=lambda x, m: st.StrategicError,
        const=lambda x, m: st.StrategicError
    )
    if x is st.StrategicError:
        raise x
    else:
        return x


def exprZM(exp, z):
    x = exp.match(
        root=lambda x, m: st.StrategicError,
        let=lambda x, y, m: st.StrategicError,
        nestedlet=lambda n, x, y, m: st.StrategicError,
        assign=lambda n, x, y, m: st.StrategicError,
        empty=lambda m: st.StrategicError,
        add=lambda x, y, m: st.StrategicError,
        sub=lambda x, y, m: st.StrategicError,
        neg=lambda x, m: st.StrategicError,
        var=lambda x, m: expandZ(x, z),
        const=lambda x, m: st.StrategicError
    )
    if x is st.StrategicError:
        raise x
    else:
        return x


def expandZ(t, z):
    e, zz = env(z)
    l, zzz = lev(zz)
    expr = expand((t, l), e)
    k = buildMemoTreeExp(MemoTable(), expr)
    return k


# def opt(z):
#     zz = zp.obj(buildMemoTree(MemoTable(), z))
#     stt = st.innermost(lambda x: st.adhocTP(st.failTP, exprM, x), zz).node()
#     return letMToLet(stt)


def opt(z):
    def exp1(y):
        return st.adhocTPZ(st.failTP, exprZM, y)

    def exp2(x):
        return st.adhocTP(exp1, exprM, x)

    zz = zp.obj(buildMemoTree(MemoTable(), z))
    stt = st.innermost(exp2, zz).node()
    return letMToLet(stt)


#########################################
# generator


def generator(n):
    return Root.ROOT(Let.LET(genLetTree(n), Exp.VAR("n_" + str(n))))


def genLetTree(n):
    return addList(genNestedLets(n))


def addList(t):
    return t.match(
        nestedlet=lambda s, l, ll: List.NESTEDLET(s, l, addList(ll)),
        empty=lambda: List.ASSIGN("va", Exp.CONST(10), List.ASSIGN("vb", Exp.CONST(20), List.EMPTY())),
        assign=lambda s, a, ll: List.ASSIGN(s, a, addList(ll))
    )


def genNestedLets(n):
    if n == 0:
        return List.EMPTY()
    elif n == 1:
        return List.NESTEDLET("n_1", Let.LET(oneList(n), Exp.ADD(Exp.VAR("z_10"), Exp.VAR("z_9"))), genListAssign(n*10))
    elif n > 1:
        return List.NESTEDLET("n_" + str(n), Let.LET(oneList(n), Exp.ADD(Exp.VAR("n_" + str(n-1)), Exp.VAR("z_" + str(n*10-1)))), genListAssign(n*10))


def oneList(n):
    return List.ASSIGN("zz_" + str(n), Exp.CONST(10), List.ASSIGN("zz_" + str(n-1), Exp.VAR("va"), genNestedLets(n-1)))


def genListAssign(n):
    if n == 0:
        return List.ASSIGN("z_0", Exp.CONST(10), List.EMPTY())
    elif n % 9 == 0:
        return List.ASSIGN("z_" + str(n), Exp.VAR("va"), genListAssign(n-1))
    else:
        return List.ASSIGN("z_" + str(n), Exp.ADD(Exp.VAR("z_" + str(n-1)), Exp.CONST(1)), genListAssign(n-1))


##########################################

def optR(z):
    return st.innermost(lambda x: st.adhocTP(st.failTP, expr, x), z).node()


def optRC(z):
    def exp1(y):
        return st.adhocTPZ(st.failTP, expC, y)

    def exp2(x):
        return st.adhocTP(exp1, expr, x)

    return st.innermost(exp2, z).node()


def main():

    sys.setrecursionlimit(10000)

    i = int(sys.argv[1])

    zp.noPrimitive = isTerminal

    print(opt(generator(i)))

    #print(dclo(zp.obj(buildMemoTree(MemoTable(), generator(1)))))


if __name__ == "__main__":
    main()
