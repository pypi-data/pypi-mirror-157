# AUTOGENERATED FILE! PLEASE DON'T EDIT
"""This module is for creating dynamic graphs using plain old
equations. For example::

    from k1lib.imports import *
    x = graphEqn.Variable()
    y = x * 3 + 5
    z = y ** 5
    
    z(2) # returns 161051 (from (2 * 3 + 5) ** 5)

Point is, ``x`` is an unknown, ``y`` is a "function" of ``x``. ``z`` depends on
``y``, but is also a function of ``x``.

Remember that you can go pretty wild with this::

    x2 = k1lib.inverse(z)
    x2(161051) # returns 2.0

Here, ``x2`` is actually a function x(z).

For simple functions like this, it should take 200us to solve it. You can also
declare a bunch of variables early on, and then resolve them one by one like
this::

    a = Variable(); b = Variable()
    c = a + b + 2; a.value = 6
    c(5) # returns 13

    b.value = 7
    c() # returns 15
"""
from typing import Callable as _Callable, Union as _Union, Iterator as _Iterator
import k1lib as _k1lib
__all__ = ["Variable"]
F = _Callable[[float, float], float]
class Expression:
    def __init__(self, a:"Variable", b:"Variable", operation:F):
        self.a = a; self.b = b; self.operation = operation
    @property
    def resolved(self):
        """Whether this expression has been resolved (both internal variables are
resolved)."""
        return self.a.resolved and self.b.resolved
    @property
    def value(self):
        """Value of the expression."""
        return self.operation(self.a._value, self.b._value)
    def applyF(self, f:_Callable[["Variable"], None]):
        self.a._applyF(f); self.b._applyF(f)
def _op2(a, b, operation:F):
    a = a if isinstance(a, Variable) else _Constant(a)
    b = b if isinstance(b, Variable) else _Constant(b)
    answer = Variable(); answer.expr = Expression(a, b, operation)
    if answer.expr.resolved: answer._value = answer.expr.value
    return answer
class Variable:
    _idx = 0
    def __init__(self):
        self.__class__._idx += 1; self.variableName = f"V{self.__class__._idx}"
        self.expr:Expression = None
        self._value:float = None # not None, then already resolved
        self.isConstant = False # to know if the value above is resolved, or is truely a literal number
        self.trial:int = 0 # current resolve trial number
    @property
    def value(self) -> _Union[float, None]:
        """Actual float value of :class:`Variable`. When setting this, if the
new value's not None, the object would act like a constant in every future
equations. To turn it back into a :class:`Variable`, simply set this to
:data:`None`."""
        return self._value
    @value.setter
    def value(self, v):
        """Sets the value of variable. If it's an actual value, """
        if v is None: self._value = None; self.isConstant = False
        else: self._value = v; self.isConstant = True
    def _reset(self): self._value = self._value if self.isConstant else None
    @property
    def resolved(self):
        """Whether this variable has been resolved or not."""
        return self._value != None
    def _applyF(self, f:_Callable[["Variable"], None]): # apply an operation to variable and its dependencies
        f(self)
        if self.expr != None: self.expr.applyF(f)
    @property
    def _leaves(self) -> _Iterator["Variable"]:
        """Get variables that does not have an expression linked to it. Aka at
the leaf."""
        if self.resolved: return
        if self.expr == None: yield self
        else:
            yield from self.expr.a._leaves
            yield from self.expr.b._leaves
    @property
    def leaves(self): return list(set(self._leaves))
    def __call__(self, x:float=None) -> _Union[float, None]:
        """Tries to solve this variable given the independent variable ``x``.

:param x: if nothing is specified, you have to be sure that all variables already
    have a value."""
        return self._solve(x)
    def __add__(self, v): return _op2(self, v, lambda a, b: a + b)
    def __sub__(self, v): return _op2(self, v, lambda a, b: a - b)
    def __neg__(self): return _op2(_Constant(0), self, lambda a, b: a - b)
    def __mul__(self, v): return _op2(self, v, lambda a, b: a * b)
    def __truediv__(self, v): return _op2(self, v, lambda a, b: a / b)
    def __pow__(self, v): return _op2(self, v, lambda a, b: a**b)
    def __radd__(self, v): return _op2(v, self, lambda a, b: a + b)
    def __rsub__(self, v): return _op2(v, self, lambda a, b: a - b)
    def __rmul__(self, v): return _op2(v, self, lambda a, b: a * b)
    def __rtruediv__(self, v): return _op2(v, self, lambda a, b: a / b)
    def __rpow__(self, v): return _op2(v, self, lambda a, b: a**b)
    def __repr__(self): return f"{self._value}" if self.resolved else f"<Variable {self.variableName}>"
    def __int__(self): return self._value
    def __float__(self): return self._value
@_k1lib.patch(Variable)
def _resolve(self, trial:int) -> bool:
    """Attempts to resolve variable. Return true if expression tree under
this Variable changes at all.

:param trial: how many times _resolve() has been called by the originating
    :class:`Variable`? Only updates stuff if in a new trial."""
    if self.trial >= trial or self.resolved or self.expr == None: return False
    # try to resolve dependencies first
    changed = self.expr.a._resolve(trial) or self.expr.b._resolve(trial)
    self.trial = trial
    if self.expr.resolved: self._value = self.expr.value; changed = True
    return changed
@_k1lib.patch(Variable)
def _simplify(self, printStuff:bool=False):
    """Simplify system before solving"""
    self._applyF(lambda v: setattr(v, "trial", 0)); trial = 2
    while self._resolve(trial): trial += 1
    if printStuff and not self.resolved: print("Can't find a solution")
@_k1lib.patch(Variable)
def _solve(self, x:float) -> _Union[float, None]:
    """Try to solve this expression tree, given value of independent
variable."""
    self._applyF(lambda v: v._reset()); self._simplify(); leaves = self.leaves
    if len(leaves) > 1: raise Exception(f"System of equation has {len(leaves)} indenpendent variables. Please constrain system more!")
    elif len(leaves) == 1: next(iter(leaves))._value = x
    self._simplify(True); return self._value
class _Constant(Variable):
    def __init__(self, value:float):
        """Creates a constant :class:`Variable` with some specified value."""
        super().__init__(); self._value = value; self.isConstant = True