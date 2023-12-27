class StrategicError(Exception):
    pass

#############################################


def idTP(f):
    return f


def failTP(f):
    raise StrategicError


def adhocTP(f, g, z):
    try:
        return z.trans(g)
    except (StrategicError, ValueError, AttributeError):
        return f(z)


def adhocTPZ(f, g, z):
    try:
        return z.transZ(g)
    except (StrategicError, ValueError, AttributeError):
        return f(z)


def seqTP(f, g, z):
    return g(f(z))


def choiceTP(f, g, z):
    try:
        return f(z)
    except StrategicError:
        return g(z)


def tryTP(f, z):
    return choiceTP(f, idTP, z)


def repeatTP(f, z):
    return tryTP(lambda x: seqTP(f, lambda y: repeatTP(f, y), x), z)


def allTPright(f, z):
    try:
        return f(z.right()).left()
    except (StrategicError, AttributeError):
        return z


def allTPdown(f, z):
    try:
        return f(z.down()).up()
    except (StrategicError, AttributeError):
        return z


def oneTPright(f, z):
    try:
        return f(z.right()).left()
    except (StrategicError, AttributeError) as e:
        raise e


def oneTPdown(f, z):
    try:
        return f(z.down()).up()
    except (StrategicError, AttributeError) as e:
        raise e


def full_tdTP(f, z):
    def down(x): return allTPdown(lambda y: full_tdTP(f, y), x)
    def right(w): return allTPright(lambda k: full_tdTP(f, k), w)
    def downRight(i): return seqTP(down, right, i)
    return seqTP(f, downRight,  z)


# def full_tdTP(f, z):
#     return seqTP(f, lambda i: seqTP(lambda x: allTPdown(lambda y: full_tdTP(f, y), x), lambda w: allTPright(lambda k: full_tdTP(f, k), w), i), z)


def full_buTP(f, z):
    def down(x): return allTPdown(lambda y: full_buTP(f, y), x)
    def right(w): return allTPright(lambda k: full_buTP(f, k), w)
    def downF(i): return seqTP(down, f, i)
    return seqTP(right, downF, z)


def once_tdTP(f, z):
    def down(x): return oneTPdown(lambda y: once_tdTP(f, y), x)
    def right(w): return oneTPright(lambda k: once_tdTP(f, k), w)
    def downRight(i): return choiceTP(down, right, i)
    return choiceTP(f, downRight, z)


def once_buTP(f, z):
    def down(x): return oneTPdown(lambda y: once_buTP(f, y), x)
    def right(w): return oneTPright(lambda k: once_buTP(f, k), w)
    def downF(i): return choiceTP(down, f, i)
    return choiceTP(right, downF, z)


def innermost(f, z):
    def down(x): return allTPdown(lambda y: innermost(f, y), x)
    def right(w): return allTPright(lambda k: innermost(f, k), w)
    def t(j): return seqTP(f, lambda n: innermost(f, n), j)
    def tryT(i): return tryTP(t, i)
    def downT(m): return seqTP(down, tryT, m)
    return seqTP(right, downT, z)


# def innermost(f, z):
#     return seqTP(lambda w: allTPright(lambda k: innermost(f, k), w), lambda m: seqTP(lambda x: allTPdown(lambda y: innermost(f, y), x), lambda i: tryTP(lambda j: seqTP(f, lambda n: innermost(f, n), j), i), m), z)


# broken
def innermostt(f, z):
    return repeatTP(lambda x: once_buTP(f, x), z)


def outermost(f, z):
    def down(x): return allTPdown(lambda y: outermost(f, y), x)
    def right(w): return allTPright(lambda k: outermost(f, k), w)
    def t(j): return seqTP(f, lambda n: outermost(f, n), j)
    def tryT(i): return tryTP(t, i)
    def downRight(m): return seqTP(down, right, m)
    return seqTP(tryT, downRight, z)


# broken
def outermostt(f, z):
    return repeatTP(lambda x: once_tdTP(f, x), z)


##########
####
# TU
####
##########


def idTU(f):
    return [f.node()]


def failTU(f):
    return []


def constTU(f):
    return f


def adhocTU(f, g, z):
    try:
        return g(z.node())
    except (StrategicError, AttributeError):
        return f(z)


def adhocTUZ(f, g, z):
    try:
        return g(z.node(), z)
    except (StrategicError, AttributeError):
        return f(z)


def seqTU(f, g, z):
    return f(z) + g(z)


def choiceTU(f, g, z):
    try:
        return f(z)
    except (StrategicError, AttributeError):
        return g(z)


def allTUright(f, z):
    try:
        return f(z.right())
    except (StrategicError, AttributeError):
        return []


def allTUdown(f, z):
    try:
        return f(z.down())
    except (StrategicError, AttributeError):
        return []


def full_tdTU(f, z):
    def down(x): return allTUdown(lambda y: full_tdTU(f, y), x)
    def right(w): return allTUright(lambda k: full_tdTU(f, k), w)
    def downRight(i): return seqTU(down, right, i)
    return seqTU(f, downRight,  z)


def full_buTU(f, z):
    def down(x): return allTUdown(lambda y: full_buTU(f, y), x)
    def right(w): return allTUright(lambda k: full_buTU(f, k), w)
    def downF(i): return seqTU(down, f, i)
    return seqTU(right, downF, z)
