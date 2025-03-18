from hypothesis import given

from pyztrategic import strategy as st
from pyztrategic.zipper import Zipper, obj
from let import *
from let_generator import genRoot



# checks if the local environment of a block is contained in the global environment
@given(genRoot())
def testPropLocInGlobal(i):
    assert all(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, localInGlobal, x), obj(i)))


def localInGlobal(t : Lets, z: Zipper[Lets]) -> list[bool]:
    eNoLevels = [(x, z) for x, _, z in env(z)]
    return [isSubset(dclBlock(z), eNoLevels)]


def isSubset[T](a : list[T], b: list[T]) -> bool:
    return all(x in b for x in a)

# ensure that the generator is not producing invalid Let expressions
# @given(genAttRoot())
# def testPropErrors(t):
#     assert not semantics(t)


# checks if the errors of an optimized let are contained in the errors of the original let

@given(genRoot())
def testPropErrors(i):
    assert isSubset(semantics(i), semantics(optR(obj(i))))



p = Let(Assign("a", Add(Var("b"), Const(0)),
             Assign("c", Const(2),
             NestedLet("b", Let(Assign("c", Const(3), Empty()),
                                         Add(Var("c"), Var("c"))),
             Empty()))),
         Sub(Add(Var("a"), Const(7)), Var("c")))


# check no deads

# def checkOneDead(t, z):
#     match t:
#         case Assign(x, _, _):
#             return [x] if dead(z) else []
#         case NestedLet(x, _, _):
#             return [x] if dead(z) else []
#         case _:
#             return []

def checkOneDead(t: Lets, z: Zipper[Lets]) -> list[bool]:
    return [dead(z)]

@given(genRoot())
def testDeadCode(i):
    assert not any(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, checkOneDead, x), obj(i)))



# every declared name needs to be in the environment

def mBInB(name: str, env: Env) -> bool:
    return any(e[0] == name for e in env)

def checkOneDeclared(t: Lets, z: Zipper[Lets]) -> list[bool]:
    match t:
        case Assign(x, _, _) | NestedLet(x, _, _):
            return [mBInB(x, env(z))]
        case _:
            return []


@given(genRoot())
def testDeclaredNames(i):
    assert all(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, checkOneDeclared, x), obj(i)))



# every declared name must not be in the accumulated environment


def mNBInB(t: tuple[str, int], env: Env) -> bool:
    return all(t[0] != e[0] or t[1] != e[1] for e in env)


def checkOneDeclaredDcli(t: Lets, z: Zipper[Lets]) -> list[bool]:
    match t:
        case Assign(x, _, _) | NestedLet(x, _, _):
            return [mNBInB((x, lev(z)), dcli(z))]
        case _:
            return []


@given(genRoot())
def testDeclaredNamesDcli(i):
    assert all(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, checkOneDeclaredDcli, x), obj(i)))




# initial list of declarations of a nestedLet is a subset of the total environment of its outer one


def checkNested(t: Lets, z: Zipper[Lets]) -> list[bool]:
    match t:
        case NestedLet(_, _, _):
            return [isSubset(dcli(z.z_dollar(2)), env(z.z_dollar(2)))]
        case _:
            return []


@given(genRoot())
def testNested(i):
    assert all(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, checkNested, x), obj(i)))