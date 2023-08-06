from typing import Any, List

from ts_t1_validator.validators.exceptions import ValidationException
from ts_t1_validator.validators.rules.abstract_rule import ValidationRule
from ts_t1_validator.validators.rules.positive_id_rule import PositiveIDRule


class PositiveIDListRule(ValidationRule):
    def __init__(self, values: List[Any], field_name: str):
        self.values = values
        self.field_name = field_name

    def execute(self):
        """
        Provided value must be a positive integer
        """

        errors = []
        for value in self.values:
            try:
                PositiveIDRule(value=value, field_name=self.field_name).execute()
            except ValidationException:
                errors.append(value)

        if errors:
            raise ValidationException(f"{self.field_name} must be a list of valid values, found {errors}")
