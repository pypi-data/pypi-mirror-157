from typing import Any

from ts_t1_validator.utils import is_int
from ts_t1_validator.validators.exceptions import ValidationException
from ts_t1_validator.validators.rules.abstract_rule import ValidationRule


class PositiveIDRule(ValidationRule):
    def __init__(self, value: Any, field_name: str):
        self.value = value
        self.field_name = field_name

    def execute(self):
        """
        Provided value must be a positive integer
        """

        if not is_int(self.value) or self.value < 1:
            raise ValidationException(f"{self.field_name} must be a valid id")
