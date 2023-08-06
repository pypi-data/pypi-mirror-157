"""
Comparable
==========

This page documents the :class:`.Comparable` checker.
"""

import operator

from .core import Checker


class _Descriptor:
    def __init__(self, comp_op, excludes=None, greater_than=None, less_than=None, long_name=None):
        self.comp_op = comp_op
        self.excludes = set() if excludes is None else excludes
        self.greater_than = set() if greater_than is None else greater_than
        self.less_than = set() if less_than is None else less_than
        self.long_name = long_name

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, owner=None):
        return obj.__dict__.get(self.name, None)

    def __set__(self, obj, value):
        if value is not None:
            if not isinstance(value, obj.other_type):
                parameters = {self.name: value}
                obj._raise_init_type_error(f'must have type {obj.other_type!r} if present', **parameters)

            for other_name in self.excludes:
                other_value = getattr(obj, other_name)

                if other_value is not None:
                    parameters = {self.name: value, other_name: other_value.other}
                    obj._raise_init_type_error('must not be both present', **parameters)

            for other_name in self.greater_than:
                other_value = getattr(obj, other_name)

                if other_value is not None and value < other_value.other:
                    parameters = {self.name: value, other_name: other_value.other}
                    obj._raise_init_value_error(f'{self.name} must be greater than {other_name}', **parameters)

            for other_name in self.less_than:
                other_value = getattr(obj, other_name)

                if other_value is not None and value > other_value.other:
                    parameters = {self.name: value, other_name: other_value.other}
                    obj._raise_init_value_error(f'{self.name} must be less than {other_name}', **parameters)

            value = _Comparer(value, self.long_name, self.comp_op)

        obj.__dict__[self.name] = value


class Comparable(Checker):
    """
    Check if `x` correctly compares to other values using any of the following binary operators:
    `<`, `<=`, `!=`, `==`, `>=` or `>`.

    Comparison need not necessarily be between numeric types, as can be seen in the first example below.

    Also, comparison shorthands can be used, as can be seen in the second example below.

    :param lt: *Optional[Any]* – Check if `x < lt`.
    :param le: *Optional[Any]* – Check if `x <= le`.
    :param ne: *Optional[Any]* – Check if `x != ne`.
    :param eq: *Optional[Any]* – Check if `x == eq`.
    :param ge: *Optional[Any]* – Check if `x >= ge`.
    :param gt: *Optional[Any]* – Check if `x > gt`.
    :param other_type: *Optional[Union[Type, Tuple[Type]]]* – If provided, restricts the types to which `x` can
       be compared, e.g. `other_type=int` with `ne=1.0` will raise a `TypeError` (because `1.0` is not an `int`).

    :Example:

    .. code-block:: python

        from argscheck import check, Comparable


        # Check if a strict subset of {'a', 'b'}
        checker = Comparable(lt={'a', 'b'})

        check(checker, set())       # Passes, an empty set is returned
        check(checker, {'a'})       # Passes, {'a'} is returned
        check(checker, {'a', 'b'})  # Fails, a ValueError is raised ({'a', 'b'} is equal to {'a', 'b'})
        check(checker, 'a')         # Fails, a TypeError is raised (< is not supported between set and str)

    :Example:

    .. code-block:: python

        from argscheck import check, Comparable


        # Check if between 3 (inclusive) and 10 (exclusive)
        checker = 3 <= (Comparable < 10)

        check(checker, 7.0)   # Passes, 7.0 is returned
        check(checker, 3)     # Passes, 3 is returned
        check(checker, 1)     # Fails, a ValueError is raised
        check(checker, 10)    # Fails, a ValueError is raised (< is not supported between set and str)

    .. warning::

       When using a **chained** comparison shorthand like in the second example, one of the comparisons must always be
       surrounded by parentheses. i.e. the following will not work: `3 <= Comparable < 10`.

       This is due to how Python's chained comparison handling is implemented.
    """

    lt = _Descriptor(operator.lt, excludes={'le', 'eq'}, greater_than={'gt', 'ge'}, long_name='less than')
    le = _Descriptor(operator.le, excludes={'lt', 'eq'}, greater_than={'gt', 'ge'}, long_name='less than or equal to')
    gt = _Descriptor(operator.gt, excludes={'ge', 'eq'}, less_than={'lt', 'le'}, long_name='greater than')
    ge = _Descriptor(operator.ge, excludes={'gt', 'eq'}, less_than={'lt', 'le'}, long_name='greater than or equal to')
    eq = _Descriptor(operator.eq, excludes={'lt', 'le', 'gt', 'ge', 'ne'}, long_name='equal to')
    ne = _Descriptor(operator.ne, excludes={'eq'}, long_name='not equal to')

    def __init__(self, *args, lt=None, le=None, ne=None, eq=None, ge=None, gt=None, other_type=object, **kwargs):
        super().__init__(*args, **kwargs)

        # `other_type` must be a type or tuple of types
        if not isinstance(other_type, tuple):
            other_type = (other_type,)
        if not all(isinstance(item, type) for item in other_type):
            self._raise_init_type_error('must be a type or tuple of types', other_type=other_type)

        self.other_type = other_type
        self.lt, self.le, self.ne, self.eq, self.ge, self.gt = lt, le, ne, eq, ge, gt

    def __lt__(self, other):
        self.lt = other

        return self

    def __gt__(self, other):
        self.gt = other

        return self

    def __le__(self, other):
        self.le = other

        return self

    def __ge__(self, other):
        self.ge = other

        return self

    def __ne__(self, other):
        self.ne = other

        return self

    def __eq__(self, other):
        self.eq = other

        return self

    def check(self, name, value, **kwargs):
        passed, value = super().check(name, value)
        if not passed:
            return False, value

        for comparator in self._comparators():
            if comparator is not None:
                try:
                    result = comparator(value)
                except TypeError:
                    return False, self._make_check_error(TypeError, name, value)

                if not result:
                    return False, self._make_check_error(ValueError, name, value)

        return True, value

    def expected(self):
        expected = [f'{comparator.long_name} {comparator.other!r}' for comparator in self._comparators()]
        expected = ', '.join(expected)

        return super().expected() + [expected]

    def _comparators(self):
        for comparator in (self.lt, self.le, self.ne, self.eq, self.ge, self.gt):
            if comparator is not None:
                yield comparator


class _Comparer:
    def __init__(self, other, long_name, comp_op):
        self.other = other
        self.long_name = long_name
        self.comp_op = comp_op

    def __call__(self, value):
        return self.comp_op(value, self.other)
