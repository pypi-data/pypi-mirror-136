"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from decimal import Decimal
import pytest

from validataclass.exceptions import ValidationError
from validataclass.validators import Noneable, DecimalValidator, IntegerValidator


class NoneableTest:
    @staticmethod
    def test_valid_none():
        """ Test that Noneable allows None as value and returns None in that case by default. """
        validator = Noneable(DecimalValidator())
        assert validator.validate(None) is None

    @staticmethod
    def test_valid_with_default():
        """ Test that Noneable allows None as value and returns a specified default value. """
        validator = Noneable(DecimalValidator(), default=Decimal('3.1415'))
        assert validator.validate(None) == Decimal('3.1415')

    @staticmethod
    def test_valid_not_none_value():
        """ Test that Noneable correctly wraps a specified validator in case of non-None values. """
        validator = Noneable(DecimalValidator())
        assert validator.validate('12.34') == Decimal('12.34')

    @staticmethod
    def test_invalid_not_none_value():
        """ Test that Noneable correctly wraps a specified validator and leaves (most) exceptions unmodified. """
        validator = Noneable(DecimalValidator())
        with pytest.raises(ValidationError) as exception_info:
            validator.validate('foobar')
        assert exception_info.value.to_dict() == {'code': 'invalid_decimal'}

    @staticmethod
    def test_invalid_type_contains_none():
        """ Test that Noneable adds 'none' to the expected_types parameter if the wrapped validator raises an InvalidTypeError. """
        validator = Noneable(DecimalValidator())
        with pytest.raises(ValidationError) as exception_info:
            validator.validate(123)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_types': ['none', 'str'],
        }

    @staticmethod
    def test_default_value_is_deepcopied():
        """
        Test that given default values are deepcopied. Otherwise using for example `default=[]` would always return a
        reference to the *same* list, and modifying this list would result in unexpected behaviour.
        """
        # Note: An empty list as default value for an IntegerValidator doesn't make a lot of sense, but simplifies the test.
        validator = Noneable(IntegerValidator(), default=[])
        first_list = validator.validate(None)
        second_list = validator.validate(None)
        assert first_list == []
        assert second_list == []
        # The lists are equal (both are empty lists), but they must not be the *same* object, otherwise bad stuff will happen.
        assert first_list is not second_list
