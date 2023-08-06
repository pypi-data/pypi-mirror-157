from ts_t1_validator import AbstractValidator, T1Service
from ts_t1_validator.models.dto.targeting_location import TargetingLocationDTO
from ts_t1_validator.models.enums.targeting_type import TargetingTypeEnum

from ts_t1_validator.validators.rules.one_of_enum_rule import OneOfEnumRule
from ts_t1_validator.validators.rules.positive_id_list_rule import PositiveIDListRule
from ts_t1_validator.validators.rules.t1_id_duplication_in_list import IDDuplicationInListRule
from ts_t1_validator.validators.rules.t1_ids_same_check import T1CheckIds
from ts_t1_validator.validators.rules.targeting_locations_in_list_rule import TargetingLocationsInList


class TargetingLocationValidator(AbstractValidator):
    def __init__(self, t1_service: T1Service):
        """
        targeting location validation manager
        :param t1_service: T1Service
        """
        self.rules = list()
        self.errors = list()
        self.json_schema = None
        self.t1_service = t1_service

    def build_rules_set(self, *args, **kwargs):
        """
        Build rules set
        """

        # remove previous rules
        self.rules = list()

        dto = TargetingLocationDTO.fromDict(kwargs.get("dto", {}))

        self.rules.append(PositiveIDListRule(values=dto.included, field_name="Included"))
        self.rules.append(PositiveIDListRule(values=dto.excluded, field_name="Excluded"))
        self.rules.append(OneOfEnumRule(value=dto.targeting_type, expected_enum=TargetingTypeEnum,
                                        field_name="Targeting Type"))

        self.rules.append(T1CheckIds(include_value_ids=dto.included, exclude_value_ids=dto.excluded,
                                     targeting_type=dto.targeting_type))
        self.rules.append(TargetingLocationsInList(values=dto.included,
                                                   targeting_type=dto.targeting_type,
                                                   field_name="Included"))

        self.rules.append(TargetingLocationsInList(values=dto.excluded,
                                                   targeting_type=dto.targeting_type,
                                                   field_name="Excluded"))

        self.rules.append(IDDuplicationInListRule(values=dto.included,
                                                  targeting_type=dto.targeting_type,
                                                  field_name="Included"))

        self.rules.append(IDDuplicationInListRule(values=dto.excluded,
                                                  targeting_type=dto.targeting_type,
                                                  field_name="Excluded"))
