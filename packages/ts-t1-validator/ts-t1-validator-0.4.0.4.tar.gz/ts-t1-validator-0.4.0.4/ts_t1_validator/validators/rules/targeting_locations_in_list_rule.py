import json
import os
from typing import List

from ts_t1_validator.models.enums.targeting_type import TargetingTypeEnum
from ts_t1_validator.validators.exceptions import ValidationException
from ts_t1_validator.validators.rules.abstract_rule import ValidationRule


class TargetingLocationsInList(ValidationRule):
    REGION_PATH = "targeting_location/fixtures/regions.json"
    DMAX_PATH = "targeting_location/fixtures/dmas.json"

    def __init__(self, values: List[int], targeting_type: TargetingTypeEnum, field_name: str):
        self.values = values
        self.targeting_type = targeting_type
        self.field_name = field_name
        self.file_path = self.__setFilePath(self.targeting_type)

    def __setFilePath(self, targeting_type: TargetingTypeEnum) -> str:
        """
        set file path based on location_type
        :param targeting_type:
        :return: str
        """

        dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = self.REGION_PATH if targeting_type is TargetingTypeEnum.REGION else self.DMAX_PATH
        return f"{dir_name}/{json_path}"

    def execute(self):
        """
        based on location_type value should be in one of lists
        """
        errors = []
        with open(self.file_path) as json_file:
            id_list = json.load(json_file)
            for value in self.values:
                if value not in id_list:
                    errors.append(value)

        if errors:
            raise ValidationException(f"IDs - {errors} does not exist for {self.field_name} section in {self.targeting_type.value}")
