from hypothesis import given

from pyztrategic import strategy as st
from pyztrategic import zipper as zp
from let import *
from let_generator import genRoot



# checks if the local environment of a block is contained in the global environment
@given(genRoot())
def testPropLocInGlobal(i):
    assert all(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, localInGlobal, x), zp.obj(i)))


def localInGlobal(t, z):
    eNoLevels = [(x, z) for x, _, z in env(z)]
    return [isSubset(dclBlock(z), eNoLevels)]


def isSubset(a, b):
    return all(x in b for x in a)

# ensure that the generator is not producing invalid Let expressions
# @given(genAttRoot())
# def testPropErrors(t):
#     assert not semantics(t)


# checks if the errors of an optimized let are contained in the errors of the original let

@given(genRoot())
def testPropErrors(i):
    assert isSubset(semantics(i), semantics(optR(zp.obj(i))))



p = Let(Assign("a", Add(Var("b"), Const(0)),
             Assign("c", Const(2),
             NestedLet("b", Let(Assign("c", Const(3), Empty()),
                                         Add(Var("c"), Var("c"))),
             Empty()))),
         Sub(Add(Var("a"), Const(7)), Var("c")))

# def checkOneDead(t, z):
#     match t:
#         case Assign(x, _, _):
#             return [x] if dead(z) else []
#         case NestedLet(x, _, _):
#             return [x] if dead(z) else []
#         case _:
#             return []

def checkOneDead(t, z):
    return [dead(z)]

@given(genRoot())
def testDeadCode(i):
    assert  not any(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, checkOneDead, x), zp.obj(i)))