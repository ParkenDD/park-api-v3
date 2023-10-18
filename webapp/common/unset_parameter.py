"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

__all__ = ['UnsetParameter', 'UnsetParameterType']


class UnsetParameterType:
    """
    The `UnsetParameter` sentinel object can be used as a default value for optional function parameters to distinguish it from None.
    """

    def __call__(self):
        return self

    def __repr__(self):
        return 'UnsetParameter'

    def __str__(self):
        return '<UnsetParameter>'

    def __bool__(self):
        return False


# Create sentinel object UnsetParameter
UnsetParameter = UnsetParameterType()
UnsetParameterType.__new__ = lambda cls: UnsetParameter
