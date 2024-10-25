from pyztrategic import zipper as zp
from pyztrategic import strategy as st
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


def optAdd(x, y):
    if (x == Exp.CONST(0)):
        return y
    elif (y == Exp.CONST(0)):
        return x
    elif (lambda a, b: x == Exp.CONST() and y == Exp.CONST()):
        return Exp.CONST(x.const() + y.const())
    else:
        return st.StrategicError


def optNeg(x):
    if (lambda a: x == Exp.NEG()):
        return x.neg()
    elif (lambda b: x == Exp.CONST()):
        return Exp.CONST(-x.const())
    else:
        return st.StrategicError


def expr(exp):
    x = exp.match(
        add=lambda x, y: optAdd(x, y),
        sub=lambda x, y: Exp.ADD(x, Exp.NEG(y)),
        neg=lambda x: optNeg(x),
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
    match constructor(x):
        case Constructor.CRoot:
            return dclo(x.z_dollar(1))
        case Constructor.CLet:
            return dclo(x.z_dollar(1))
        case Constructor.CNestedLet:
            return dclo(x.z_dollar(3))
        case Constructor.CAssign:
            return dclo(x.z_dollar(3))
        case Constructor.CEmpty:
            return dcli(x)


def dcli(x):
    match constructor(x):
        case Constructor.CLet:
            match constructor(x.up()):
                case Constructor.CRoot:
                    return []
                case Constructor.CNestedLet:
                    return env(x.up())
        case _:
            match constructor(x.up()):
                case Constructor.CLet:
                    return dcli(x.up())
                case Constructor.CAssign:
                    return [(lexeme_Name(x.up()), lev(x.up()), lexeme_Exp(x.up()))] + dcli(x.up())
                case Constructor.CNestedLet:
                    return [(lexeme_Name(x.up()), lev(x.up()), st.StrategicError)] + dcli(x.up())


def env(x):
    match constructor(x):
        case Constructor.CRoot:
            return dclo(x)
        case Constructor.CLet:
            return dclo(x)
        case _:
            return env(x.up())


#### for current block

def dcloBlock(x):
    match constructor(x):
        case Constructor.CRoot:
            return dcloBlock(x.z_dollar(1))
        case Constructor.CLet:
            return dcloBlock(x.z_dollar(1))
        case Constructor.CNestedLet:
            return dcloBlock(x.z_dollar(3))
        case Constructor.CAssign:
            return dcloBlock(x.z_dollar(3))
        case Constructor.CEmpty:
            return dcliBlock(x)


def dcliBlock(x):
    match constructor(x):
        case Constructor.CLet:
            match constructor(x.up()):
                case Constructor.CRoot:
                    return []
                case Constructor.CNestedLet:
                    return []
        case _:
            match constructor(x.up()):
                case Constructor.CLet:
                    return dcliBlock(x.up())
                case Constructor.CAssign:
                    return [(lexeme_Name(x.up()), lexeme_Exp(x.up()))] + dcli(x.up())
                case Constructor.CNestedLet:
                    return [(lexeme_Name(x.up()), st.StrategicError)] + dcli(x.up())


####

#### Same but only for current block, simpler, assumes we're at start of let

def dclBlock(x):
    match constructor(x):
        case Constructor.CRoot:
            return dclBlock(x.z_dollar(1))
        case Constructor.CLet:
            return dclBlock(x.z_dollar(1))
        case Constructor.CNestedLet:
            return [(lexeme_Name(x), st.StrategicError)] + dclBlock(x.z_dollar(3))
        case Constructor.CAssign:
            return [(lexeme_Name(x), lexeme_Exp(x))] + dclBlock(x.z_dollar(3))
        case Constructor.CEmpty:
            return []

####


def lev(x):
    match constructor(x):
        case Constructor.CLet:
            match constructor(x.up()):
                case Constructor.CNestedLet:
                    return lev(x.up()) + 1
                case Constructor.CRoot:
                    return 0
        case _:
            return lev(x.up())


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
        case Constructor.CNeg:
            return errs(x.z_dollar(1))
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


def semantics(p):
    return errs(zp.obj(p))

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

    #sys.setrecursionlimit(10000)

    # i = int(sys.argv[1])

    p = Let.LET(List.ASSIGN("a", Exp.ADD(Exp.VAR("b"), Exp.CONST(0)),
            List.ASSIGN("c", Exp.CONST(2),
            List.NESTEDLET("b", Let.LET(List.ASSIGN("c", Exp.CONST(3), List.EMPTY()),
                                        Exp.ADD(Exp.VAR("c"), Exp.VAR("c"))),
            List.EMPTY()))),
          Exp.SUB(Exp.ADD(Exp.VAR("a"), Exp.CONST(7)), Exp.VAR("c")))

    # print(optRC(zp.obj(generator(i))))

    print(p)
    print("\n\n")
    #print(zp.obj(p).down().down().right().node())
    print(optRC(zp.obj(Root.ROOT(p))))


if __name__ == "__main__":
    main()
