from typing import List

from ts_t1_validator.models.enums.targeting_type import TargetingTypeEnum


class TargetingLocationDTO:
    def __init__(self, targeting_type: TargetingTypeEnum, included: List[int], excluded: List[int]):
        self.targeting_type = targeting_type
        self.included = included
        self.excluded = excluded

    @staticmethod
    def fromDict(user_data: dict) -> "TargetingLocationDTO":
        """
        transform user data into inner object
        :param user_data: dict
        :return:
        """
        return TargetingLocationDTO(targeting_type=TargetingTypeEnum.set(user_data.get("targeting_type")),
                                    included=user_data.get("included"),
                                    excluded=user_data.get("excluded"))
