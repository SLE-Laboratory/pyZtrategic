from pyztrategic.zipper import Zipper

from typing import Optional
from dataclasses import dataclass

from enum import StrEnum, auto


type Lets = Root | Let | List | Exp

type List = NestedLet | Assign | Empty

type Exp = Add | Sub | Neg | Var | Const

type Env = list[tuple[str, int, Optional[Exp]]]

type EnvBlock = list[tuple[str, Optional[Exp]]]

@dataclass
class Let:
    lst: List
    exp: Exp

    def __repr__(self):
        return f"Let({repr(self.lst)}, {repr(self.exp)})"
    
    def __str__(self):
        lst_str = str(self.lst).rstrip()
        lines = lst_str.splitlines()

        if lines:
            indented = [lines[0]] + ["    " + line for line in lines[1:]]
            formatted = "\n".join(indented)
        else:
            formatted = ""

        return f"let {formatted}\nin {self.exp}"
    
@dataclass
class Root:
    let: Let

    def __repr__(self):
        return f"Root({repr(self.let)})"

    def __str__(self):
        return str(self.let)

@dataclass
class NestedLet:
    name: str
    let: Let
    lst: List

    def __repr__(self):
        return f"NestedLet({repr(self.name)}, {repr(self.let)}, {repr(self.lst)})"

    def __str__(self):
        l_str = str(self.let).rstrip()
        lines = l_str.splitlines()
        if lines:
            indent = " " * (3 + len(self.name))
            indented = [lines[0]] + [indent + line for line in lines[1:]]
            formatted_let = "\n".join(indented)
        else:
            formatted_let = ""

        lst_str = str(self.lst)
        if lst_str:
            return f"{self.name} = {formatted_let}\n{lst_str}"
        else:
            return f"{self.name} = {formatted_let}"
        
@dataclass
class Assign:
    name: str
    exp: Exp
    lst: List

    def __repr__(self):
        return f"Assign({repr(self.name)}, {repr(self.exp)}, {repr(self.lst)})"

    def __str__(self):
        lst_str = str(self.lst)
        if lst_str:
            return f"{self.name} = {self.exp}\n{self.lst}"
        else: 
            return f"{self.name} = {self.exp}"
        
@dataclass
class Empty:
    pass

    def __repr__(self):
        return "Empty()"

    def __str__(self):
        return ""

@dataclass
class Add:
    x: Exp
    y: Exp

    def __repr__(self):
        return f"Add({repr(self.x)}, {repr(self.y)})"

    def __str__(self):
        return f"({self.x} + {self.y})"

@dataclass
class Sub:
    x: Exp
    y: Exp

    def __repr__(self):
        return f"Sub({repr(self.x)}, {repr(self.y)})"

    def __str__(self):
        return f"({self.x} - {self.y})"

@dataclass
class Neg:
    x: Exp

    def __repr__(self):
        return f"Neg({repr(self.x)})"

    def __str__(self):
        return f"-{self.x}"

@dataclass
class Var:
    name: str

    def __repr__(self):
        return f"Var({repr(self.name)})"

    def __str__(self):
        return self.name

@dataclass
class Const:
    value: int

    def __repr__(self):
        return f"Const({self.value})"

    def __str__(self):
        return str(self.value)


class Constructor(StrEnum):
    CRoot = auto()
    CLet = auto()
    CNestedLet = auto()
    CAssign = auto()
    CEmpty = auto()
    CAdd = auto()
    CSub = auto()
    CNeg = auto()
    CConst = auto()
    CVar = auto()


def constructor(ag: Zipper[Lets]) -> Constructor:
    match ag.node():
        case Root():
            return Constructor.CRoot
        case Let():
            return Constructor.CLet
        case NestedLet():
            return Constructor.CNestedLet
        case Assign():
            return Constructor.CAssign
        case Empty():
            return Constructor.CEmpty
        case Add():
            return Constructor.CAdd
        case Sub():
            return Constructor.CSub
        case Neg():
            return Constructor.CNeg
        case Var():
            return Constructor.CVar
        case Const():
            return Constructor.CConst


def lexeme_Name(ag: Zipper[Lets]) -> str:
    match ag.node():
        case NestedLet(x,_,_):
            return x
        case Assign(x,_,_):
            return x
        case Var(x):
            return x


def lexeme_Exp(ag: Zipper[Lets]) -> Exp:
    match ag.node():
        case Assign(_,y,_):
            return y