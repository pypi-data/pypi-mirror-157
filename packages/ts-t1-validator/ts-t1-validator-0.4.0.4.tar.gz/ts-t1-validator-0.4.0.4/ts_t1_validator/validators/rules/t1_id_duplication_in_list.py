from typing import Optional
import collections
from .abstract_rule import ValidationRule
from ..exceptions import ValidationException
from ...models.enums.targeting_type import TargetingTypeEnum


class IDDuplicationInListRule(ValidationRule):
    def __init__(self, values: Optional[list], targeting_type: TargetingTypeEnum, field_name: str):

        self.values = values
        self.targeting_type = targeting_type
        self.field_name = field_name

    def execute(self):
        if self.values is None:
            return

        duplicates = [item for item, count in collections.Counter(self.values).items() if count > 1]
        if len(duplicates) > 0:
            raise ValidationException(f"You can not assign the same targeting_segment to the same strategy more than once. targeting_segment id: {duplicates} for {self.field_name} section in {self.targeting_type.value}")
