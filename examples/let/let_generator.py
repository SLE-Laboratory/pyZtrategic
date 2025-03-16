from hypothesis.strategies import integers, from_regex, composite, one_of, sampled_from, builds, deferred


from let_data import *

#########################################
# Hypothesis generator

@composite
def genExp(draw, names):
    if names:
        exp = deferred(lambda: one_of(const, var, neg, add, sub))
        var = builds(Var, sampled_from(names))
    else:
        exp = deferred(lambda: one_of(const, neg, add, sub))

    add = builds(Add, exp, exp)
    sub = builds(Sub, exp, exp)
    neg = builds(Neg, exp)
    const = builds(Const, integers(min_value=1))
    return draw(exp)

@composite
def genAssign(draw, names, n):
    name = draw(genName().filter(lambda x: x not in names))
    nExp = draw(genExp(names))
    newNames, lst = draw(genList([name] + names, n-1))
    return newNames, Assign(name, nExp, lst)


@composite
def genNestedLet(draw, names, n):
    name = draw(genName().filter(lambda x: x not in names))
    nLet = draw(genLet(names, n))
    newNames, lst = draw(genList([name] + names, n-1))
    return newNames, NestedLet(name, nLet, lst)


@composite
def genList(draw, names, n):
    if n == 0:
        return names, Empty()
    else:
        return draw(one_of(genNestedLet(names, n), genAssign(names, n)))


@composite
def genLet(draw, names, n):
    listSize = draw(integers(min_value=1, max_value=n+1))
    (newNames, lst) = draw(genList(names, listSize))
    expr = draw(genExp(newNames))
    return Let(lst, expr)


@composite
def genName(draw):
    return draw(from_regex(r'^[a-z]$', fullmatch=True))


@composite
def genRoot(draw):
    return Root(draw(genLet([], draw(integers(min_value=1, max_value=2)))))

#########################################
# Using Attributes

# Bad


# @composite
# def genAttExp(draw):
#     add = builds(Add, deferred(lambda: exp), deferred(lambda: exp))
#     sub = builds(Sub, deferred(lambda: exp), deferred(lambda: exp))
#     neg = builds(Neg, deferred(lambda: exp))
#     const = builds(Const, integers(min_value=1))
#     var = builds(Var, sampled_from(draw(genName())))
#     exp = deferred(lambda: one_of(const, var, neg, add, sub))
#     return draw(exp)


@composite
def genAttExp(draw):
    exp = deferred(lambda: one_of(const, var, neg, add, sub))
    add = builds(Add, exp, exp)
    sub = builds(Sub, exp, exp)
    neg = builds(Neg, exp)
    const = builds(Const, integers(min_value=1))
    var = builds(Var, sampled_from(draw(genName())))
    return draw(exp)


# @composite
# def genSafeExp(draw):
#     add = builds(Add, deferred(lambda: exp), deferred(lambda: exp))
#     sub = builds(Sub, deferred(lambda: exp), deferred(lambda: exp))
#     neg = builds(Neg, deferred(lambda: exp))
#     const = builds(Const, integers(min_value=1))
#     exp = deferred(lambda: one_of(const, neg, add, sub))
#     return draw(exp)


@composite
def genSafeExp(draw):
    exp = deferred(lambda: one_of(const, neg, add, sub))
    add = builds(Add, exp, exp)
    sub = builds(Sub, exp, exp)
    neg = builds(Neg, exp)
    const = builds(Const, integers(min_value=1))
    return draw(exp)

@composite
def genAttAssign(draw, n):
    name = draw(genName())
    nExp = draw(genAttExp())
    lst = draw(genAttList(n-1))
    return Assign(name, nExp, lst)


@composite
def genAttNestedLet(draw, n):
    name = draw(genName())
    nLet = draw(genAttLet())
    lst = draw(genAttList(n-1))
    return NestedLet(name, nLet, lst)


@composite
def genAttList(draw, n):
    if n == 0:
        return Empty()
    else:
        return draw(one_of(genAttNestedLet(n), genAttAssign(n)))


@composite
def addVars(draw, errs, l):
    for i in errs:
        nExp = draw(genSafeExp())
        l = Assign(i, nExp, l)
    return l


@composite
def genAttLet(draw):
    l = draw(genAttList(5))
    newExp = draw(genAttExp())
    e = errs(zp.obj(Root(Let(l, newExp))))
    return Let(draw(addVars(e, l)), newExp)


@composite
def genAttRoot(draw):
    return Root(draw(genAttLet()))


#########################################
# Normal generator


def generator(n: int) -> Root:
    return Root(Let(genLetTree(n), Var("n_" + str(n))))


def genLetTree(n: int) -> List:
    return addList(genNestedLets(n))


def addList(t):
    match(t):
        case NestedLet(s, l, ll):
            return NestedLet(s, l, addList(ll))
        case Empty():
            return Assign("va", Const(10), Assign("vb", Const(20), Empty()))
        case Assign(s, a, ll):
            return Assign(s, a, addList(ll))


def genNestedLets(n: int) -> List:
    if n == 0:
        return Empty()
    elif n == 1:
        return NestedLet("n_1", Let(oneList(n), Add(Var("z_10"), Var("z_9"))), genListAssign(n*10))
    elif n > 1:
        return NestedLet("n_" + str(n), Let(oneList(n), Add(Var("n_" + str(n-1)), Var("z_" + str(n*10-1)))), genListAssign(n*10))


def oneList(n: int) -> Assign:
    return Assign("zz_" + str(n), Const(10), Assign("zz_" + str(n-1), Var("va"), genNestedLets(n-1)))


def genListAssign(n: int) -> Assign:
    if n == 0:
        return Assign("z_0", Const(10), Empty())
    elif n % 9 == 0:
        return Assign("z_" + str(n), Var("va"), genListAssign(n-1))
    else:
        return Assign("z_" + str(n), Add(Var("z_" + str(n-1)), Const(1)), genListAssign(n-1))


##########################################