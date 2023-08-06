from enum import unique
from ts_t1_validator.models.enums.abstract_enum import AbstractEnum


@unique
class ValidatorsEnum(AbstractEnum):
    CAMPAIGN = "campaign"
    STRATEGY = "strategy"
    TARGETING_LOCATION = "targeting_location"
    UNDEFINED = None
