from pyztrategic.zipper import Zipper, obj
from pyztrategic import strategy as st

import sys

from typing import Optional

from let_data import *


def optAdd(x: Exp, y: Exp) -> Exp:
    match(x, y):
        case Const(0), _:
            return y
        case _, Const(0):
            return x
        case Const(xx), Const(yy):
            return Const(xx + yy)
        case _:
            raise st.StrategicError


def optNeg(x: Exp) -> Exp:
    match x:
        case Neg(y):
            return y
        case Const(i):
            return Const(-i)
        case _:
            raise st.StrategicError


def expr(exp: Exp) -> Exp:
    match exp:
        case Add(x, y):
            return optAdd(x, y)
        case Sub(x, y):
            return Add(x, Neg(y))
        case Neg(x):
            return optNeg(x)
        case _:
            raise st.StrategicError


def expC(exp: Exp, z: Zipper[Lets]) -> Exp:
    match exp:
        case Var(x):
            return expand((x, lev(z)), env(z))
        case _:
            raise st.StrategicError



def dclo(x: Zipper[Lets]) -> Env:
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


def dcli(x: Zipper[Lets]) -> Env:
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
                    return [(lexeme_Name(x.up()), lev(x.up()), None)] + dcli(x.up())


def env(x: Zipper[Lets]) -> Env:
    match constructor(x):
        case Constructor.CRoot:
            return dclo(x)
        case Constructor.CLet:
            return dclo(x)
        case _:
            return env(x.up())


#### for current block

def dcloBlock(x: Zipper[Lets]) -> EnvBlock:
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


def dcliBlock(x: Zipper[Lets]) -> EnvBlock:
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
                    return [(lexeme_Name(x.up()), lexeme_Exp(x.up()))] + dcliBlock(x.up())
                case Constructor.CNestedLet:
                    return [(lexeme_Name(x.up()), None)] + dcliBlock(x.up())


def envBlock(x: Zipper[Lets]) -> EnvBlock:
    match constructor(x):
        case Constructor.CRoot:
            return dcloBlock(x)
        case Constructor.CLet:
            return dcloBlock(x)
        case _:
            return envBlock(x.up())

####

#### Same but only for current block, simpler, assumes we're at start of let

def dclBlock(x: Zipper[Lets]) -> EnvBlock:
    match constructor(x):
        case Constructor.CRoot:
            return dclBlock(x.z_dollar(1))
        case Constructor.CLet:
            return dclBlock(x.z_dollar(1))
        case Constructor.CNestedLet:
            return [(lexeme_Name(x), None)] + dclBlock(x.z_dollar(3))
        case Constructor.CAssign:
            return [(lexeme_Name(x), lexeme_Exp(x))] + dclBlock(x.z_dollar(3))
        case Constructor.CEmpty:
            return []

####


def lev(x: Zipper[Lets]) -> int:
    match constructor(x):
        case Constructor.CLet:
            match constructor(x.up()):
                case Constructor.CNestedLet:
                    return lev(x.up()) + 1
                case Constructor.CRoot:
                    return 0
        case _:
            return lev(x.up())


def mBIn(name: str, env: Env) -> list[str]:
    if not env:
        return [name]
    elif env[0][0] == name:
        return []
    else:
        return mBIn(name, env[1:])


def mNBIn(t: tuple[str, int], env: Env) -> list[str]:
    if not env:
        return []
    elif t[0] == env[0][0] and t[1] == env[0][1]:
        return [t[0]]
    else:
        return mNBIn(t, env[1:])


def errs(x: Zipper[Lets]) -> list[str]:
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

def expand(t: tuple[str, int], e: Env) -> Exp:
    results = sorted(filter(lambda x: x[0] == t[0] and x[1] <= t[1], e), key=lambda x: x[1], reverse=True)
    if results:
        res = results[0][2]
        if res:
            return res
        else:
            raise st.StrategicError
    else:
        raise st.StrategicError


def semantics(p: Lets) -> list[str]:
    return errs(obj(p))

def optR(z: Zipper[Lets]) -> Lets:
    return st.innermost(lambda x: st.adhocTP(st.failTP, expr, x), z).node()

def optRC(z: Zipper[Lets]) -> Lets:
    def exp1(y):
        return st.adhocTPZ(st.failTP, expC, y)

    def exp2(x):
        return st.adhocTP(exp1, expr, x)

    return st.innermost(exp2, z).node()


######################################################



def dead(t: Zipper[Lets]) -> bool:
    match constructor(t):
        case Constructor.CAssign:
            return deadsFromBlock(lexeme_Name(t), t)
        case Constructor.CNestedLet:
            return deadsFromBlock(lexeme_Name(t), t)
        case _:
            raise st.StrategicError

def deadsFromBlock(s: str, t: Zipper[Lets]) -> bool:
    match constructor(t):
        case Constructor.CLet:
            return deads(s, t.z_dollar(1)) and deads(s, t.z_dollar(2))
        case Constructor.CRoot:
            return deads(s, t.z_dollar(1))
        case _:
            return deadsFromBlock(s, t.up())

def deads(s: str, t: Zipper[Lets]) -> bool:
    match constructor(t):
        case Constructor.CEmpty:
            return True
        case Constructor.CAssign:
            return deads(s, t.z_dollar(2)) and deads(s, t.z_dollar(3))
        case Constructor.CVar:
            return s != lexeme_Name(t)
        case Constructor.CLet:
            return any([name for (name, _) in envBlock(t) if name == s]) or deadsFromBlock(s, t)
        case Constructor.CRoot:
            return any([name for (name, _) in envBlock(t) if name == s]) or deadsFromBlock(s, t)
        case Constructor.CNestedLet:
            return deads(s, t.z_dollar(2)) and deads(s, t.z_dollar(3))
        case Constructor.CAdd:
            return deads(s, t.z_dollar(1)) and deads(s, t.z_dollar(2))
        case Constructor.CSub:
            return deads(s, t.z_dollar(1)) and deads(s, t.z_dollar(2))
        case Constructor.CNeg:
            return deads(s, t.z_dollar(1))
        case Constructor.CConst:
            return True
     
######################################################


def main():

    sys.setrecursionlimit(10000)

    # i = int(sys.argv[1])

    p = Let(Assign("a", Add(Var("b"), Const(0)),
            Assign("c", Const(2),
            NestedLet("b", Let(Assign("c", Const(3), Empty()),
                                        Add(Var("c"), Var("c"))),
            Empty()))),
        Sub(Add(Var("a"), Const(7)), Var("c")))

    # print(optRC(zp.obj(generator(i))))

    print(p)
    print("\n\n")
    #print(zp.obj(p).down().down().right().node())
    print(optRC(obj(Root(p))))


if __name__ == "__main__":
    main()
