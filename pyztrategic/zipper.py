from collections import namedtuple

from typing import Any, Callable, Dict, Tuple, Optional, Iterable


type Zipper[T] = 'Zipper[T]'

PathType = namedtuple('PathType', 'l, r, pnodes, ppath, changed')


def isa(type: type) -> Callable[[Any], bool]:
    """
    Returns is_<type>(obj) a function that returns true
    when it's argument is the istance of type
    """
    def f(obj: Any) -> bool:
        return isinstance(obj, type)

    f.__name__ = "is_{0}".format(type)
    return f

# ---------------------------------------------------------------------------


def noPrimitive(obj: Any) -> bool:
    return not isinstance(obj, (int, float, bool, str))


def tupDict[T](root: Dict[Any, T]) -> Tuple[T, ...]:
    return tuple(root.values())


def tup(root: Any) -> Tuple[Any, ...]:
    if is_list(root):
        return tuple(root)
    elif is_dict(root):
        return tupDict(root)
    else:
        t = root.__dict__
        # if tuple(t.keys())[0] == '_key':
        #     tv = tuple(t.values())
        #     if not isinstance(tv[1], tuple):
        #         tp = tuple([tv[1]])
        #     else:
        #         tp = tv[1]
        # else:
        tp = tuple(t.values())

        return tp


def mkNode[T](node: T, children: Tuple[T, ...]) -> T:
    if is_dict(node):
        #return native_dict(zip(tuple(node.keys()), children))
        return native_dict(children)
    elif is_list(node):
        return native_list(children)
    else:
        return type(node)(*children)


def obj[T](root: T) -> Zipper[T]:
    return zipper(
        root,
        noPrimitive,
        tup,
        mkNode
    )

# ---------------------------------------------------------------------------


native_list = __builtins__['list']
is_list = isa(native_list)


def list[T](root: T) -> Zipper[T]:
    return zipper(
        root,
        is_list,
        tuple,
        lambda node, children: native_list(children)
    )


native_dict = __builtins__['dict']
is_dict = isa(native_dict)


def dict[T](root: T) -> Zipper[T]:
    return zipper(
        root,
        # i is either the root object or a tuple of key value pairs
        # lambda i: i is is_dict(root) or is_dict(i[1]),
        is_dict,
        # lambda i: tuple(i.items() if i is is_dict(i) else i[1].items()),
        tupDict,
        #lambda node, children: native_dict(zip(tuple(node.keys()), children))
        lambda node, children: native_dict(children)
    )


def zipper[T](
    root: T,
    is_branch: Callable[[T], bool],
    children: Callable[[T], Tuple[T, ...]],
    make_node: Callable[[T, Tuple[T, ...]], T]
) -> Zipper[T]:
    return Zipper(root, None, is_branch, children, make_node)


class Zipper[T](namedtuple('Zipper', 'current, path, is_branch, get_children, make_node')):
    current: T
    path: Optional[PathType]
    is_branch: Callable[[T], bool]
    get_children: Callable[[T], Tuple[T, ...]]
    make_node: Callable[[T, Tuple[T, ...]], T]


    def __repr__(self) -> str:
        return "<zipper.Zipper({}) object at {}>".format(self.current, id(self))

    # Context
    def node(self) -> T:
        return self.current

    def children(self) -> Optional[Tuple[T, ...]]:
        if self.branch():
            return self.get_children(self.current)
        else:
            return None

    def branch(self) -> bool:
        return self.is_branch(self.current)

    def root(self) -> T:
        return self.top().current

    def at_end(self) -> bool:
        return not bool(self.path)

    # Navigation
    def down(self) -> Optional[Zipper[T]]:
        children = self.children()
        if children:
            path = PathType(
                l=(),
                r=children[1:],
                pnodes=self.path.pnodes + (self.current,) if self.path else (self.current,),
                ppath=self.path,
                changed=False
            )

            return self._replace(current=children[0], path=path)

        else:
            return None


    def up(self) -> Optional[Zipper[T]]:
        if self.path:
            l, r, pnodes, ppath, changed = self.path
            if pnodes:
                pnode = pnodes[-1]
                if changed:
                    chld = l+(self.current,) + r
                    # if len(chld) == 1:
                    #     chld = chld[0]
                    # if not isinstance(chld, Iterable):
                        # chld = (chld,)
                    return self._replace(
                        current=self.make_node(pnode, chld),
                        path=ppath and ppath._replace(changed=True)
                    )
                else:
                    return self._replace(current=pnode, path=ppath)
        return None

    def top(self) -> Zipper[T]:
        Zipper = self
        while Zipper.path:
            Zipper = Zipper.up()
        return Zipper

    def ancestor(self, filter: Callable[[Zipper[T]], bool]) -> Optional[Zipper[T]]:
        """
        Return the first ancestor preceding the current Zipper that
        matches the filter(ancestor) function.

        The filter function is invoked with the Zipperation of the
        next ancestor. If the filter function returns true then
        the ancestor will be returned to the invoker of
        Zipper.ancestor(filter) method. Otherwise the search will move
        to the next ancestor until the top of the tree is reached.
        """

        u = self.up()
        while u:
            if filter(u):
                return u
            else:
                u = u.up()
        return None

    def left(self) -> Optional[Zipper[T]]:
        if self.path and self.path.l:
            ls, r = self.path[:2]
            l, current = ls[:-1], ls[-1]
            return self._replace(current=current, path=self.path._replace(
                l=l,
                r=(self.current,) + r
            ))
        else:
            return None

    def leftmost(self) -> Zipper[T]:
        """Returns the left most sibling at this Zipperation or self"""

        path = self.path
        if path:
            l, r = self.path[:2]
            t = l + (self.current,) + r
            current = t[0]

            return self._replace(current=current, path=path._replace(
                l=(),
                r=t[1:]
            ))
        else:
            return self

    def rightmost(self) ->  Zipper[T]:
        """Returns the right most sibling at this Zipperation or self"""

        path = self.path
        if path:
            l, r = self.path[:2]
            t = l + (self.current,) + r
            current = t[-1]

            return self._replace(current=current, path=path._replace(
                l=t[:-1],
                r=()
            ))
        else:
            return self

    def right(self) -> Optional[Zipper[T]]:
        if self.path and self.path.r:
            l, rs = self.path[:2]
            current, rnext = rs[0], rs[1:]
            return self._replace(current=current, path=self.path._replace(
                l=l+(self.current,),
                r=rnext
            ))
        else:
            return None

    def leftmost_descendant(self) -> Zipper[T]:
        Zipper = self
        while Zipper.branch():
            d = Zipper.down()
            if d:
                Zipper = d
            else:
                break

        return Zipper

    def rightmost_descendant(self) -> Zipper[T]:
        Zipper = self
        while Zipper.branch():
            d = Zipper.down()
            if d:
                Zipper = d.rightmost()
            else:
                break
        return Zipper

    def move_to(self, dest: Zipper[T]) -> Zipper[T]:
        """
        Move to the same 'position' in the tree as the given Zipper and return
        the Zipper that currently resides there. This method does not gurantee
        that the node from the previous Zipper will be the same node if the node
        or it's ancestory has bee modified.
        """

        moves = []
        path = dest.path

        while path:
            moves.extend(len(path.l) * ['r'])
            moves.append('d')
            path = path.ppath

        moves.reverse()

        Zipper = self.top()
        for m in moves:
            if m == 'd':
                Zipper = Zipper.down()
            else:
                Zipper = Zipper.right()

        return Zipper

    # Enumeration
    def preorder_iter(self) -> Iterable[Zipper[T]]:
        Zipper = self
        while Zipper:
            Zipper = Zipper.preorder_next()
            if Zipper:
                yield Zipper

    def preorder_next(self) -> Optional[Zipper[T]]:
        """
        Visit's nodes in depth-first pre-order.

        For eaxmple given the following tree:

                a
              /   \
             b     e
             ^     ^
            c d   f g

        preorder_next will visit the nodes in the following order
        b, c, d, e, f, g, a

        See preorder_iter for an example.
        """

        if self.path == ():
            return None

        n = self.down() or self.right()

        if n is not None:
            return n
        else:
            u = self.up()
            while u:
                r = u.right()
                if r:
                    return r
                else:
                    if u.path:
                        u = u.up()
                    else:
                        return u._replace(path=())
        return None

    def postorder_next(self) -> Optional[Zipper[T]]:
        """
        Visit's nodes in depth-first post-order.

        For eaxmple given the following tree:

                a
              /   \
             b     e
             ^     ^
            c d   f g

        postorder next will visit the nodes in the following order
        c, d, b, f, g, e a


        Note this method ends when it reaches the root node. To
        start traversal from the root call leftmost_descendant()
        first. See postorder_iter for an example.

        """

        r = self.right()
        if (r):
            return r.leftmost_descendant()
        else:
            return self.up()

    def postorder_iter(self) -> Iterable[Zipper[T]]:
        Zipper = self.leftmost_descendant()

        while Zipper:
            yield Zipper
            Zipper = Zipper.postorder_next()

    # editing
    def append(self, item: T) -> Zipper[T]:
        """
        Inserts the item as the rightmost child of the node at this Zipper,
        without moving.
        """
        return self.replace(
            self.make_node(self.node(),  self.children()+(item,))
        )

    def edit(self, f: Callable[[T, Any], T], *args: Any) -> Zipper[T]:
        "Replace the node at this Zipper with the value of f(node, *args)"
        return self.replace(f(self.current, *args))

    def insert(self, item: T) -> Zipper[T]:
        """
        Inserts the item as the leftmost child of the node at this Zipper,
        without moving.
        """
        return self.replace(
            self.make_node(self.node(), (item,) + self.children())
        )

    def insert_left(self, item: T) -> Zipper[T]:
        """Insert item as left sibling of node without moving"""
        path = self.path
        if not path:
            raise IndexError("Can't insert at top")

        new = path._replace(l=path.l + (item,), changed=True)
        return self._replace(path=new)

    def insert_right(self, item: T) -> Zipper[T]:
        """Insert item as right sibling of node without moving"""
        path = self.path
        if not path:
            raise IndexError("Can't insert at top")

        new = path._replace(r=(item,) + path.r, changed=True)
        return self._replace(path=new)

    def replace(self, value: T) -> Zipper[T]:
        if self.path:
            return self._replace(current=value, path=self.path._replace(changed=True))
        else:
            return self._replace(current=value)

    def find(self, func: Callable[[Zipper[T]], bool]) -> Optional[Zipper[T]]:
        Zipper = self.leftmost_descendant()
        while True:
            if func(Zipper):
                return Zipper
            elif Zipper.at_end():
                return None
            else:
                Zipper = Zipper.postorder_next()

    def remove(self) -> Zipper[T]:
        """
        Removes the node at the current Zipperation, returning the
        node that would have proceeded it in a depth-first walk.

        For eaxmple given the following tree:

                a
              /   \
             b     e
             ^     ^
            c d   f g
            ^
          c1 c2
        Removing c would return b, removing d would return c2.


        """
        path = self.path
        if not path:
            raise IndexError("Remove at top")

        l, r, pnodes, ppath, changed = path

        if l:
            ls, current = l[:-1], l[-1]
            return self._replace(current=current, path=path._replace(
                l=ls,
                changed=True
            )).rightmost_descendant()

        else:
            return self._replace(
                current=self.make_node(pnodes[-1], r),
                path=ppath and ppath._replace(changed=True)
            )

# ---------------------------------------------------------------------------

    def trans(self, func: Callable[[T], T]) -> Zipper[T]:
        return self.replace(func(self.node()))

    def transZ(self, func: Callable[[T, Zipper[T]], T]) -> Zipper[T]:
        return self.replace(func(self.node(), self))

# ---------------------------------------------------------------------------

    def z_dollar(self, n: int) -> Optional[Zipper[T]]:
        current = self.down()
        for _ in range(n - 1):
            right_result = current.right()
            if right_result is None:
                return None
            current = right_result
        return current

    def z_pipe(self, n: int) -> bool:
        left_z = self.left()
        if n == 1:
            return left_z is not None
        elif left_z is None:
            return False
        else:
            return left_z.z_pipe(n-1)

    def z_dollar_r(self, n: int) -> Optional[Zipper[T]]:
        current = self.arity()
        up_result = self.up()
        if up_result:
            return up_result.z_dollar(current + n)
        else:
            return None

    def z_dollar_l(self, n: int) -> Optional[Zipper[T]]:
        current = self.arity()
        up_result = self.up()
        if up_result:
            return up_result.z_dollar(current - n)
        else:
            return None

    def arity(self) -> int:
        return self._arity(1)

    def _arity(self, n: int) -> int:
        left_m = self.left()
        if left_m is None:
            return n
        else:
            return left_m._arity(n+1)
