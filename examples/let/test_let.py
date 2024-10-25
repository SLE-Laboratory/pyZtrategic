from hypothesis import given
from hypothesis.strategies import integers, from_regex, composite, one_of, sampled_from, builds, deferred

from pyztrategic import strategy as st
from pyztrategic import zipper as zp
from let import Root, Let, List, Exp, dclBlock, env, semantics, errs


# -- --------
# -- --
# -- - Generator for Let expressions
# -- --
# -- --------



@composite
def genExp(draw, names):
    add = builds(Exp.ADD, deferred(lambda: exp), deferred(lambda: exp))
    sub = builds(Exp.SUB, deferred(lambda: exp), deferred(lambda: exp))
    neg = builds(Exp.NEG, deferred(lambda: exp))
    const = builds(Exp.CONST, integers(min_value=1))
    if not names:
        exp = deferred(lambda: one_of(const, neg, add, sub))
        return draw(exp)
    else:
        var = builds(Exp.VAR, sampled_from(names))
        exp = deferred(lambda: one_of(const, var, neg, add, sub))
        return draw(exp)

@composite
def genAssign(draw, names, n):
    name = draw(genName())
    while name in names:
        name = draw(genName())
    nExp = draw(genExp(names))
    newNames, lst = draw(genList([name] + names, n-1))
    return newNames, List.ASSIGN(name, nExp, lst)


@composite
def genNestedLet(draw, names, n):
    name = draw(genName())
    nLet = draw(genLet(names, n))
    newNames, lst = draw(genList([name] + names, n-1))
    return newNames, List.NESTEDLET(name, nLet, lst)


@composite
def genList(draw, names, n):
    if n == 0:
        return names, List.EMPTY()
    else:
        return draw(one_of([genNestedLet(names, n), genAssign(names, n)]))


@composite
def genLet(draw, names, n):
    listSize = draw(integers(min_value=1, max_value=n+1))
    (newNames, lst) = draw(genList(names, listSize))
    expr = draw(genExp(newNames))
    return Let.LET(lst, expr)


@composite
def genName(draw):
    return draw(from_regex(r'^[a-z]$', fullmatch=True))


@composite
def genRoot(draw):
    return Root.ROOT(draw(genLet([], draw(integers(min_value=1, max_value=2)))))

###########

## Using Attributes


@composite
def genAttExp(draw):
    add = builds(Exp.ADD, deferred(lambda: exp), deferred(lambda: exp))
    sub = builds(Exp.SUB, deferred(lambda: exp), deferred(lambda: exp))
    neg = builds(Exp.NEG, deferred(lambda: exp))
    const = builds(Exp.CONST, integers(min_value=1))
    var = builds(Exp.VAR, sampled_from(draw(genName())))
    exp = deferred(lambda: one_of(const, var, neg, add, sub))
    return draw(exp)

@composite
def genSafeExp(draw):
    add = builds(Exp.ADD, deferred(lambda: exp), deferred(lambda: exp))
    sub = builds(Exp.SUB, deferred(lambda: exp), deferred(lambda: exp))
    neg = builds(Exp.NEG, deferred(lambda: exp))
    const = builds(Exp.CONST, integers(min_value=1))
    exp = deferred(lambda: one_of(const, neg, add, sub))
    return draw(exp)

@composite
def genAttAssign(draw, n):
    name = draw(genName())
    nExp = draw(genAttExp())
    lst = draw(genAttList(n-1))
    return List.ASSIGN(name, nExp, lst)


@composite
def genAttNestedLet(draw, n):
    name = draw(genName())
    nLet = draw(genAttLet())
    lst = draw(genAttList(n-1))
    return List.NESTEDLET(name, nLet, lst)


@composite
def genAttList(draw, n):
    if n == 0:
        return List.EMPTY()
    else:
        return draw(one_of([genAttNestedLet(n), genAttAssign(n)]))


@composite
def addVars(draw, errs, l):
    for i in errs:
        nExp = draw(genSafeExp())
        l = List.ASSIGN(i, nExp, l)
    return l


@composite
def genAttLet(draw):
    l = draw(genAttList(5))
    newExp = draw(genAttExp())
    e = errs(zp.obj(Root.ROOT(Let.LET(l, newExp))))
    return Let.LET(draw(addVars(e, l)), newExp)


@composite
def genAttRoot(draw):
    return Root.ROOT(draw(genAttLet()))


###########



# checks if the local environment of a block is contained in the global environment
@given(genRoot())
def testPropLocInGlobal(i):
    assert all(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, localInGlobal, x), zp.obj(i)))



def localInGlobal(t, z):
    return [containedIn(dclBlock(z), env(z))]


def containedIn(b, e):
    eNoLevels = [(x, z) for x, y, z in e]
    set1 = set(b)
    set2 = set(eNoLevels)
    intersection = set1.intersection(set2)
    return intersection == set1


# ensure that the generator is not producing invalid Let expressions
# @given(genAttRoot())
# def testPropErrors(t):
#     assert not semantics(t)