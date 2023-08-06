from typing import Type

from ts_t1_validator.models.enums.abstract_enum import AbstractEnum
from ts_t1_validator.validators.exceptions import ValidationException
from ts_t1_validator.validators.rules.abstract_rule import ValidationRule


class OneOfEnumRule(ValidationRule):
    def __init__(self, value, expected_enum: Type[AbstractEnum], field_name: str):
        self.value = value
        self.expected_enum = expected_enum
        self.field_name = field_name

    def execute(self):
        """
        Value must not to be undefined
        """

        if not isinstance(self.value, AbstractEnum):
            raise ValidationException(f"{self.field_name} should have valid value")

        if self.value is self.value.UNDEFINED:
            raise ValidationException(f"{self.field_name} should be one of {str(self.expected_enum.asList())}")
