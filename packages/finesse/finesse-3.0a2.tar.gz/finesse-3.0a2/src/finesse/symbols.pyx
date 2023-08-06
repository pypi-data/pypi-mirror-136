from enum import Flag
from itertools import combinations
import warnings
import abc

import numpy as np

from finesse import constants
from finesse.utilities import is_iterable
from finesse.exceptions import FinesseException

import operator
import logging


LOGGER = logging.getLogger(__name__)

MAKE_LOP = lambda name, opfn: lambda self, other: Operation(name, opfn, self, other)
MAKE_ROP = lambda name, opfn: lambda self, other: Operation(name, opfn, other, self)


# Supported operators.
OPERATORS = {
    "__add__": MAKE_LOP("+", operator.add),
    "__sub__": MAKE_LOP("-", operator.sub),
    "__mul__": MAKE_LOP("*", operator.mul),
    "__radd__": MAKE_ROP("+", operator.add),
    "__rsub__": MAKE_ROP("-", operator.sub),
    "__rmul__": MAKE_ROP("*", operator.mul),
    "__pow__": MAKE_LOP("**", operator.pow),
    "__truediv__": MAKE_LOP("/", operator.truediv),
    "__rtruediv__": MAKE_ROP("/", operator.truediv),
    "__floordiv__": MAKE_LOP("//", operator.floordiv),
    "__rfloordiv__": MAKE_ROP("//", operator.floordiv),
    "__matmul__": MAKE_LOP("@", operator.matmul),
}


# Maps function names to actual functions called,
# this is used for lambdifying symbolics as you
# can't grab the underlying function from the lambdas
# stored in FUNCTIONS below
PYFUNCTION_MAP = {
    "abs": operator.abs,
    "neg": operator.neg,
    "pos": operator.pos,
    "pow": operator.pow,
    "conj": np.conj,
    "real": np.real,
    "imag": np.imag,
    "exp": np.exp,
    "sin": np.sin,
    "arcsin": np.arcsin,
    "cos": np.cos,
    "arccos": np.arccos,
    "tan": np.tan,
    "arctan": np.arctan,
    "arctan2": np.arctan2,
    "sqrt": np.sqrt,
    "radians": np.radians,
    "degrees": np.degrees,
    "deg2rad": np.deg2rad,
    "rad2deg": np.rad2deg,
    "arange": np.arange,
    "linspace": np.linspace,
    "logspace": np.logspace,
    "geomspace": np.geomspace,
}


# Built-in symbolic functions.
FUNCTIONS = {
    "abs": lambda x: Operation("abs", operator.abs, x),
    "neg": lambda x: Operation("neg", operator.neg, x),
    "pos": lambda x: Operation("pos", operator.pos, x),
    "pow": lambda x: Operation("pow", operator.pow, x),
    "conj": lambda x: Operation("conj", np.conj, x),
    "real": lambda x: Operation("real", np.real, x),
    "imag": lambda x: Operation("imag", np.imag, x),
    "exp": lambda x: Operation("exp", np.exp, x),
    "sin": lambda x: Operation("sin", np.sin, x),
    "arcsin": lambda x: Operation("arcsin", np.arcsin, x),
    "cos": lambda x: Operation("cos", np.cos, x),
    "arccos": lambda x: Operation("arccos", np.arccos, x),
    "tan": lambda x: Operation("tan", np.tan, x),
    "arctan": lambda x: Operation("arctan", np.arctan, x),
    "arctan2": lambda y, x: Operation("arctan2", np.arctan2, y, x),
    "sqrt": lambda x: Operation("sqrt", np.sqrt, x),
    "radians": lambda x: Operation("radians", np.radians, x),
    "degrees": lambda x: Operation("degrees", np.degrees, x),
    "deg2rad": lambda x: Operation("deg2rad", np.deg2rad, x),
    "rad2deg": lambda x: Operation("rad2deg", np.rad2deg, x),
    "arange": lambda a, b, c: Operation("arange", np.arange, float(a), float(b), int(c)),
    "linspace": lambda a, b, c: Operation("linspace", np.linspace, float(a), float(b), int(c)),
    "logspace": lambda a, b, c: Operation("logspace", np.logspace, float(a), float(b), int(c)),
    "geomspace": lambda a, b, c: Operation("geomspace", np.geomspace, float(a), float(b), int(c)),
}


op_repr = {
    operator.add: "({}+{})",
    operator.sub: "({}-{})",
    operator.mul: "{}*{}",
    operator.pow: "{}**{}",
    operator.truediv: "{}/{}",
    operator.floordiv: "{}//{}",
    operator.mod: "({}%{})",
    operator.matmul: "({}@{})",
    operator.neg: "-{}",
    operator.pos: "+{}",
    operator.abs: "abs({})",
    np.conj: "conj({})",
    np.sqrt: "sqrt({})",
}


def finesse2sympy(expr, iter_num=0):
    """
    Notes
    -----
    It might be common for this this function to throw a NotImplementedError.
    This function maps, by hand, various operator and numpy functions to sympy.
    If you come across this error, you'll need to update the if-statement to
    include the missing operations. Over time this should get fixed for most
    use cases.
    """
    import sympy
    from finesse.parameter import ParameterRef
    iter_num += 1
    if isinstance(expr, Constant):
        return expr.value
    elif isinstance(expr, ParameterRef):
        return sympy.Symbol(expr.name)
    elif isinstance(expr, Operation):
        sympy_args = [finesse2sympy(arg,iter_num) for arg in expr.args]
        if expr.op == operator.mul:
            op = sympy.Mul
        elif expr.op == operator.add:
            op = sympy.Add
        elif expr.op == operator.truediv:
            op = lambda a, b: sympy.Mul(a, sympy.Pow(b, -1))
        elif expr.op == operator.pow:
            op = sympy.Pow
        elif expr.op == operator.sub:
            op = lambda x,y: sympy.Add(x,-y)
        elif expr.op == np.conj:
            op = sympy.conjugate
        elif expr.op == np.radians:
            op = sympy.rad
        elif expr.op == np.exp:
            op = sympy.exp
        elif expr.op == np.cos:
            op = sympy.cos
        elif expr.op == np.sin:
            op = sympy.sin
        elif expr.op == np.tan:
            op = sympy.tan
        elif expr.op == np.sqrt:
            op = sympy.sqrt
        elif expr.op == operator.abs:
            op = sympy.Abs
        elif expr.op == operator.neg:
            op = lambda x: sympy.Mul(-1, x)
        elif expr.op == np.imag:
            op = sympy.im
        elif expr.op == np.real:
            op = sympy.re
        else:
            try:
                op = getattr(sympy, expr.op.__name__)
            except AttributeError:
                raise NotImplementedError(f"undefined Operation {expr.op} in {expr}. {finesse2sympy} needs to be updated.")
        return op(*sympy_args)
    else:
        raise NotImplementedError(f'{expr} undefined. {finesse2sympy} needs to be updated.')

def sympy2finesse(expr, symbol_dict={}, iter_num=0):
    import sympy
    iter_num += 1
    if isinstance(expr,sympy.Mul):
        return np.product([sympy2finesse(arg, symbol_dict, iter_num=iter_num) for arg in expr.args])
    elif isinstance(expr,sympy.Add):
        return np.sum([sympy2finesse(arg, symbol_dict, iter_num=iter_num) for arg in expr.args])
    elif isinstance(expr,sympy.conjugate):
        return np.conj(sympy2finesse(*expr.args, symbol_dict))
    elif isinstance(expr,sympy.exp):
        return np.exp(sympy2finesse(*expr.args, symbol_dict))
    elif isinstance(expr,sympy.Pow):
        return np.power(sympy2finesse(expr.args[0], symbol_dict), sympy2finesse(expr.args[1], symbol_dict))
    elif expr.is_NumberSymbol: # sympy class for named symbols (eg Pi, golden ratio, ...)
        if str(expr) == 'pi':
            return CONSTANTS['pi']
        else:
            return complex(expr)
    elif expr.is_number:
        if expr.is_integer:
            return int(expr)
        elif expr.is_real:
            return float(expr)
        else:
            return complex(expr)
    elif expr.is_symbol:
        return symbol_dict[str(expr)]
    else:
        raise Exception(f'{expr} undefined')


def as_symbol(x):
    return x if isinstance(x, Symbol) else Constant(x)


def display(a):
    """
    For a given Symbol this method will return a human readable string
    representing the various operations it contains.

    Parameters
    ----------
    a : :class:`.Symbol`
        Symbol to print

    Returns
    -------
    String form of Symbol
    """
    if hasattr(a, "op"):
        # Check if operation has a predefined string format
        if a.op in op_repr:
            sop = op_repr[a.op]
        else:  # if not just treat it as a function
            sop = a.op.__name__ + "(" + ("{}," * len(a.args)).rstrip(",") + ")"

        sargs = (display(_) for _ in a.args)

        return sop.format(*sargs)
    elif hasattr(a, "name"):  # Anything with a name attribute just display that
        return a.name
    elif type(a) is Symbol:
        return f"<Symbol @ {hex(id(a))}>"
    else:
        return str(a)


def evaluate(x):
    """Evaluates a symbol or N-dimensional array of symbols.

    Parameters
    ----------
    x : :class:`.Symbol` or array-like
        A symbolic expression or an array of symbolic expressions.

    Returns
    -------
    out : float, complex, :class:`numpy.ndarray`
        A single value for the evaluated expression if `x` is not
        array-like, otherwise an array of the evaluated expressions.
    """
    if is_iterable(x):
        y = np.array(x, dtype=np.complex128)
        if not np.any(y.imag): # purely real symbols in array
            with warnings.catch_warnings():
                # suppress 'casting to float discards imag part' warning
                # as we know that all imag parts are zero here anyway
                warnings.simplefilter("ignore", category=np.ComplexWarning)
                y = np.array(y, dtype=np.float64)

        return y

    if isinstance(x, Symbol):
        return x.eval()

    # If not a symbol then just return x directly
    return x


class Symbol(abc.ABC):
    __add__ = OPERATORS["__add__"]
    __sub__ = OPERATORS["__sub__"]
    __mul__ = OPERATORS["__mul__"]
    __radd__ = OPERATORS["__radd__"]
    __rsub__ = OPERATORS["__rsub__"]
    __rmul__ = OPERATORS["__rmul__"]
    __pow__ = OPERATORS["__pow__"]
    __truediv__ = OPERATORS["__truediv__"]
    __rtruediv__ = OPERATORS["__rtruediv__"]
    __floordiv__ = OPERATORS["__floordiv__"]
    __rfloordiv__ = OPERATORS["__rfloordiv__"]
    __matmul__ = OPERATORS["__matmul__"]

    __abs__ = FUNCTIONS["abs"]
    __neg__ = FUNCTIONS["neg"]
    __pos__ = FUNCTIONS["pos"]
    conjugate = FUNCTIONS["conj"]
    conj = FUNCTIONS["conj"]
    exp = FUNCTIONS["exp"]
    sin = FUNCTIONS["sin"]
    arcsin = FUNCTIONS["arcsin"]
    cos = FUNCTIONS["cos"]
    arccos = FUNCTIONS["arccos"]
    tan = FUNCTIONS["tan"]
    arctan = FUNCTIONS["arctan"]
    arctan2 = FUNCTIONS["arctan2"]
    sqrt = FUNCTIONS["sqrt"]
    radians = FUNCTIONS["radians"]
    degrees = FUNCTIONS["degrees"]
    deg2rad = FUNCTIONS["deg2rad"]
    rad2deg = FUNCTIONS["rad2deg"]

    @property
    def real(self):
        return FUNCTIONS["real"](self)

    @property
    def imag(self):
        return FUNCTIONS["imag"](self)

    def __float__(self):
        v = self.eval()
        if np.isscalar(v):
            return float(v)
        else:
            raise TypeError(f"Can't cast {type(v)} into a single float value")

    def __complex__(self):
        v = self.eval()
        if np.isscalar(v):
            return complex(v)
        else:
            raise TypeError(f"Can't cast {type(v)} into a single complex value")

    def __int__(self):
        v = self.eval()
        if np.isscalar(v):
            return int(v)
        else:
            raise TypeError(f"Can't cast {type(v)} into a single int value")

    @property
    def value(self):
        return self.eval()

    def __str__(self):
        return display(self)

    def __repr__(self):
        return f"<Symbolic='{display(self)}' @ {hex(id(self))}>"

    @property
    def is_changing(self):
        """
        Returns True if one of the arguements of this symbolic object
        is varying whilst a :class:`` is running.
        """
        res = False

        if hasattr(self, "op"):
            res = any([_.is_changing for _ in self.args])
        elif hasattr(self, "parameter"):
            res = self.parameter.is_tunable or self.parameter.is_changing

        return res

    def parameters(self, memo=None):
        """
        Returns all the parameters that are present in this symbolic statement
        """
        if memo is None:
            memo = set()

        if hasattr(self, "op"):
            for _ in self.args:
                _.parameters(memo)
        elif hasattr(self, "parameter"):
            memo.add(self)

        return list(memo)

    def changing_parameters(self):
        p = np.array(self.parameters())
        return list(p[list(map(lambda x: x.is_changing, p))])

    def to_sympy(self):
        """Converts a Finesse symbolic expression into a Sympy expression.
        Warning: for large functions this can be quite slow.
        """
        return finesse2sympy(self)

    def sympy_simplify(self):
        """Converts this expression into a Sympy symbol
        """
        refs = {_.name: _ for _ in self.parameters()} # get a list of symbols we're using
        sympy = finesse2sympy(self)
        return sympy2finesse(sympy.simplify(), refs)

    def expand_symbols(self):
        """A method that expands any symbolic parameter references that are themselves
        symbolic. This can be used to get an expression that only depends on references
        that are numeric.

        Examples
        --------
        >>> import finesse
        >>> model = finesse.Model()
        >>> model.parse(
        ...     '''
        ...     var d 300
        ...     var c 6000
        ...     var b &c+&d
        ...     var a &b+1
        ...     '''
        ... )
        >>> model.a.value.value.expand_symbols()
        <Symbolic='((c.value+d.value)+1)' @ 0x7faa4d351c10>

        Parameters
        ----------
        sym : Symbolic
            Symbolic equation to expand
        """
        def process(p):
            if p.parameter.is_symbolic:
                return p.parameter.value
            else:
                return p

        def _expand(sym):
            if not all(p.parameter.is_symbolic for p in  sym.parameters()):
                return None
            else:
                return sym.eval(subs={p: process(p) for p in sym.parameters()})

        sym = self
        while True:
            res = _expand(sym)
            if res is None:
                return sym
            else:
                sym = res

class Constant(Symbol):
    """Defines a constant symbol that can be used in symbolic math.

    Parameters
    ----------
    value : float, int
        Value of constant

    name : str, optional
        Name of the constant to use when printing
    """

    def __init__(self, value, name=None):
        self.__value = value
        self.__name = name

    def __str__(self):
        return self.__name or str(self.__value)

    def __repr__(self):
        return str(self.__name or self.__value)

    def __eq__(self, obj):
        if isinstance(obj, Constant):
            return obj.value == self.value
        else:
            return False

    def __hash__(self):
        """Constant hash.

        This is used by the tokenizer. Constants are by definition immutable.
        """
        # Add the class to reduce chance of hash collisions.
        return hash((type(self), self.value))

    def eval(self, **kwargs):
        return self.__value


# Constants.
# NOTE: The keys here are used by the parser to recognise constants in kat script.
CONSTANTS = {
    "pi": Constant(constants.PI, name="π"),
    "c0": Constant(constants.C_LIGHT, name="c"),
}


class Resolving(Symbol):
    """A special symbol that represents a symbol that is not yet resolved.

    This is used in the parser to support self-referencing parameters.

    An error is thrown if the value is attempted to be read.
    """
    def eval(self, **kwargs):
        raise RuntimeError(
            "an attempt has been made to read the value of a resolving symbol (hint: "
            "symbols should not be evaluated until parsing has fully finished)"
        )

    @property
    def name(self):
        return "RESOLVING"


class Variable(Symbol):
    """
    Makes a variable symbol that can be used in symbolic math. Values must be substituted
    in when evaluating an expression.

    Examples
    --------
    Using some variables to make an expression and evaluating it:

    >>> import numpy as np
    >>> x = Variable('x')
    >>> y = Variable('y')
    >>> z = 4*x**2 - np.cos(y)
    >>> print(f"{z} = {z.eval(subs={x:2, y:3})} : x={2}, y={3}")
    (4*x**2-y) = 13 : x=2, y=3

    Parameters
    ----------
    value : float, int
        Value of constant

    name : str, optional
        Name of the constant to use when printing
    """

    def __init__(self, name):
        if name is None:
            raise ValueError("Name must be provided")
        self.__name = str(name)

    @property
    def name(self):
        return self.__name

    def eval(self, subs=None, keep=None, **kwargs):
        """Blah
        """
        if keep:
            if self.name == keep:
                return self
            elif is_iterable(keep):
                if self.name in keep or self in keep:
                    return self
        if subs:
            if self.name in subs:
                return subs[self.name]
            if self in subs:
                return subs[self]


        return self


class Operation(Symbol):
    """
    This is a symbol to represent a mathematical operation. This could be
    a simple addition, or a more complicated multi-argument function.

    It supports creating new mathematical operations::

        import math
        import cmath

        cos   = lambda x: finesse.symbols.Operation("cos", math.cos, x)
        sin   = lambda x: finesse.symbols.Operation("sin", math.sin, x)
        atan2 = lambda y, x: finesse.symbols.Operation("atan2", math.atan2, y, x)

    Complex math can also be used::

        import numpy as np
        angle = lambda x: finesse.symbols.Operation("angle", np.angle, x)
        print(f"{angle(1+1j)} = {angle(1+1j).eval()}")

    The equality operator is overridden to provide a very basic
    symbolic equality test. It only tests whether two symbolic
    statements are *exactly* the same, e.g.:

        >>> y+x == y+x # True
        >>> y+x == x+y # False

    This could be fixed by making operators more

    Parameters
    ----------
    name : str
        The operation name. This is used for dumping operations to kat script.

    operation : callable
        The function to pass the arguments of this operation to.

    Other Parameters
    ----------------
    *args
        The arguments to pass to `operation` during a call.
    """

    def __init__(self, name, operation, *args):
        self.name = str(name)
        self.args = tuple(as_symbol(_) for _ in args)
        self.op = operation

    def eval(self, **kwargs):
        """Evaluates the operation.

        Parameters
        ----------
        subs : dict, optional
            Parameter substitutions can be given via an optional
            ``subs`` dict (mapping parameters to substituted values).

        Returns
        -------
        result : number or array-like
            The single-valued result of evaluation of the operation (if no
            substitutions given, or all substitutions are scalar-valued). Otherwise,
            if any parameter substitution was a :class:`numpy.ndarray`, then a corresponding array
            of results.
        """
        try:
            args = tuple(_.eval(**kwargs) for _ in self.args)
            return self.op(*args)
        except TypeError as ex:
            msg = f"Whilst evaluating {self.op}{self.args} this error was raised:\n`    {ex}`"
            for _ in self.args:
                if _.value is None:
                    msg += f"\nHint: {_} is `None` make sure it is defined before being used."
                    if _.parameter.full_name == "fsig.f":
                        msg += f" if using KatScript use `fsig(f)` before this line."
            raise FinesseException(msg)

    @property
    def contains_unresolved_symbol(self):
        """Whether the operation contains any unresolved symbols.

        :getter: Returns true if any symbol in the operation is an instance
                 of :class:`.Resolving`, false otherwise. Read-only.
        """
        for arg in self.args:
            if isinstance(arg, Resolving):
                return True

            if isinstance(arg, Operation):
                return arg.contains_unresolved_symbol

        return False


    def __eq__(self, obj):
        if isinstance(obj, Operation):
            if self.op == obj.op:
                return all([a == b for a, b in zip(self.args, obj.args)])
            else:
                return False
        else:
            return False
