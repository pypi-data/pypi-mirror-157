from enum import unique

from ts_t1_validator.models.enums.abstract_enum import AbstractEnum


@unique
class LocationTypeEnum(AbstractEnum):
    DMAX = "DMAX"
    REGION = "REGN"
    UNDEFINED = None
