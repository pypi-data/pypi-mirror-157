"""
Numeric
=======

This page documents checkers for numeric arguments, as well as for sized arguments.
"""

from .core import Checker, Typed
from . import Comparable


_ints = (int,)
_floats = (float,)
_numbers = _ints + _floats


class Number(Comparable, Typed, types=_numbers):
    """
    Check if `x` is of a numeric type (`int` or `float`) and optionally, compares it to other value(s) using
    any of the following binary operators: `<`, `<=`, `!=`, `==`, `>=`, `>`.

    Comparison shorthands can be used, as can be seen in the second example below.

    :param other_type: *Optional[Union[Type, Tuple[Type]]]* – restricts the types to which `x` can be compared, e.g.
       `other_type=int` with `ne=1.0` will raise a `TypeError`. By default, `x` can only be compared to other
       `int` or `float` objects.

    :Example:

    .. code-block:: python

        from argscheck import check, Number


        # Check if a number between 0 (inclusive) and 10 (exclusive)
        checker = Number(ge=0, lt=10)

        check(checker, 0)     # Passes, 0 is returned
        check(checker, 5.0)   # Passes, 5 is returned
        check(checker, 10)    # Fails, a ValueError is raised
        check(checker, 'a')   # Fails, a TypeError is raised

    :Example:

    .. code-block:: python

        from argscheck import check, Number


        # Check if a number between 0 (inclusive) and 25 (exclusive) but not equal to 14
        checker = (0.0 <= (Number < 25)) != 14

        check(checker, 0)     # Passes, 0 is returned
        check(checker, 11.0)  # Passes, 5 is returned
        check(checker, 26)    # Fails, a ValueError is raised
        check(checker, 14)    # Fails, a ValueError is raised
    """
    def __init__(self, other_type=_numbers, **kwargs):
        super().__init__(*self.types, other_type=other_type, **kwargs)


class Int(Number, types=_ints):
    """
    Same as :class:`.Number`, plus, `x` must be an `int`.

    :meta skip-extend-docstring:
    """
    pass


class Float(Number, types=_floats):
    """
    Same as :class:`.Number`, plus, `x` must be a `float`.

    :meta skip-extend-docstring:
    """
    pass


"""
Positive
"""


class PositiveNumber(Number):
    """
    Same as :class:`.Number`, plus, `x > 0` must be `True`.

    :meta skip-extend-docstring:
    """
    def __init__(self, *args, **kwargs):
        self._assert_not_in_kwargs('gt', **kwargs)
        super().__init__(*args, gt=0, **kwargs)


class PositiveInt(Int):
    """
    Same as :class:`.Int`, plus, `x > 0` must be `True`.

    :meta skip-extend-docstring:
    """
    def __init__(self, *args, **kwargs):
        self._assert_not_in_kwargs('gt', **kwargs)
        super().__init__(*args, gt=0, **kwargs)


class PositiveFloat(Float):
    """
    Same as :class:`.Float`, plus, `x > 0` must be `True`.

    :meta skip-extend-docstring:
    """
    def __init__(self, *args, **kwargs):
        self._assert_not_in_kwargs('gt', **kwargs)
        super().__init__(*args, gt=0, **kwargs)


"""
Non Negative
"""


class NonNegativeNumber(Number):
    """
    Same as :class:`.Number`, plus, `x >= 0` must be `True`.

    :meta skip-extend-docstring:
    """
    def __init__(self, *args, **kwargs):
        self._assert_not_in_kwargs('ge', **kwargs)
        super().__init__(*args, ge=0, **kwargs)


class NonNegativeInt(Int):
    """
    Same as :class:`.Int`, plus, `x >= 0` must be `True`.

    :meta skip-extend-docstring:
    """
    def __init__(self, *args, **kwargs):
        self._assert_not_in_kwargs('ge', **kwargs)
        super().__init__(*args, ge=0, **kwargs)


class NonNegativeFloat(Float):
    """
    Same as :class:`.Float`, plus, `x >= 0` must be `True`.

    :meta skip-extend-docstring:
    """
    def __init__(self, *args, **kwargs):
        self._assert_not_in_kwargs('ge', **kwargs)
        super().__init__(*args, ge=0, **kwargs)


"""
Negative
"""


class NegativeNumber(Number):
    """
    Same as :class:`.Number`, plus, `x < 0` must be `True`.

    :meta skip-extend-docstring:
    """
    def __init__(self, *args, **kwargs):
        self._assert_not_in_kwargs('lt', **kwargs)
        super().__init__(*args, lt=0, **kwargs)


class NegativeInt(Int):
    """
    Same as :class:`.Int`, plus, `x < 0` must be `True`.

    :meta skip-extend-docstring:
    """
    def __init__(self, *args, **kwargs):
        self._assert_not_in_kwargs('lt', **kwargs)
        super().__init__(*args, lt=0, **kwargs)


class NegativeFloat(Float):
    """
    Same as :class:`.Float`, plus, `x < 0` must be `True`.

    :meta skip-extend-docstring:
    """
    def __init__(self, *args, **kwargs):
        self._assert_not_in_kwargs('lt', **kwargs)
        super().__init__(*args, lt=0, **kwargs)


"""
Non Positive
"""


class NonPositiveNumber(Number):
    """
    Same as :class:`.Number`, plus, `x <= 0` must be `True`.

    :meta skip-extend-docstring:
    """
    def __init__(self, *args, **kwargs):
        self._assert_not_in_kwargs('le', **kwargs)
        super().__init__(*args, le=0, **kwargs)


class NonPositiveInt(Int):
    """
    Same as :class:`.Int`, plus, `x <= 0` must be `True`.

    :meta skip-extend-docstring:
    """
    def __init__(self, *args, **kwargs):
        self._assert_not_in_kwargs('le', **kwargs)
        super().__init__(*args, le=0, **kwargs)


class NonPositiveFloat(Float):
    """
    Same as :class:`.Float`, plus, `x <= 0` must be `True`.

    :meta skip-extend-docstring:
    """
    def __init__(self, *args, **kwargs):
        self._assert_not_in_kwargs('le', **kwargs)
        super().__init__(*args, le=0, **kwargs)


class Sized(Checker):
    """
    Check the length of `x`, as returned by `len(x)`.

    :param len_lt: *Optional[int]* – Check if `len(x) < len_lt`.
    :param len_le: *Optional[int]* – Check if `len(x) <= len_le`.
    :param len_ne: *Optional[int]* – Check if `len(x) != len_ne`.
    :param len_eq: *Optional[int]* – Check if `len(x) == len_eq`.
    :param len_ge: *Optional[int]* – Check if `len(x) >= len_ge`.
    :param len_gt: *Optional[int]* – Check if `len(x) > len_gt`.

    :Example:

    .. code-block:: python

        from argscheck import check, Sized


        # Check if length is equal to 3
        check(Sized(len_eq=3), ['a', 'b', 'c'])  # Passes, returns ['a', 'b', 'c']
        check(Sized(len_eq=3), 'abc')            # Passes, returns 'abc'
        check(Sized(len_eq=3), {'a', 'b'})       # Fails, raises ValueError (length is 2 instead of 3)
        check(Sized(len_eq=3), 123)              # Fails, raises TypeError (int does not have a length)

    """
    def __init__(self, *args, len_lt=None, len_le=None, len_ne=None, len_eq=None, len_ge=None, len_gt=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Length must be an int and must only be compared to an int
        self.len_checker = Int(lt=len_lt, le=len_le, ne=len_ne, eq=len_eq, ge=len_ge, gt=len_gt, other_type=_ints)

        # Check that no negative values were provided
        self._validate_lengths(len_lt=len_lt, len_le=len_le, len_ne=len_ne, len_eq=len_eq, len_ge=len_ge, len_gt=len_gt)

    def check(self, name, value, **kwargs):
        passed, value = super().check(name, value)
        if not passed:
            return False, value

        # Get value's length, if it fails, return the caught exception
        try:
            length = len(value)
        except TypeError:
            return False, self._make_check_error(TypeError, name, value)

        # Check length
        passed, e = self.len_checker.check(name, length)
        if not passed:
            return False, self._make_check_error(ValueError, name, value)

        return True, value

    def expected(self):
        s = self.len_checker.expected()
        s = 'has length ' + ', '.join(s[1:])  # [1:] to discard "an instance of <class 'int'>" that comes from Int

        return super().expected() + [s]

    def _validate_lengths(self, **kwargs):
        # At this point, values are None or int
        for name, value in kwargs.items():
            if value is not None and value < 0:
                self._raise_init_value_error('must be non-negative if present', **{name: value})


class NonEmpty(Sized):
    """
    Check if the length of `x` is greater than zero.

    :Example:

    .. code-block:: python

        from argscheck import check, NonEmpty


        # Check if non empty
        check(NonEmpty, ['a', 'b', 'c'])  # Passes, returns ['a', 'b', 'c']
        check(NonEmpty, 'abc')            # Passes, returns 'abc'
        check(NonEmpty, '')               # Fails, raises ValueError (empty string)
        check(NonEmpty, [])               # Fails, raises ValueError (empty list)

    :meta skip-extend-docstring:
    """
    def __init__(self, *args, **kwargs):
        self._assert_not_in_kwargs('len_lt', 'len_le', 'len_ne', 'len_eq', 'len_ge', 'len_gt', **kwargs)
        super().__init__(*args, len_gt=0, **kwargs)
