from typing import Dict

from ts_t1_validator.models.enums.validators import ValidatorsEnum
from ts_t1_validator.services.t1 import T1Service
from ts_t1_validator.validators.abstract_validator import AbstractValidator
from ts_t1_validator.validators.campaign_post_validator import CampaignPostValidator
from ts_t1_validator.validators.strategy_post_validator import StrategyPostValidator
from ts_t1_validator.validators.targeting_location_validator import TargetingLocationValidator


class T1Validator:
    def __init__(self, t1_creds: Dict, validator_type="campaign"):
        self.validator = None
        t1_service = T1Service(t1_creds=t1_creds)
        validator_enum = ValidatorsEnum.set(validator_type)
        if validator_enum is ValidatorsEnum.CAMPAIGN:
            self.validator = CampaignPostValidator(t1_service=t1_service)
        elif validator_enum is ValidatorsEnum.STRATEGY:
            self.validator = StrategyPostValidator(t1_service=t1_service)
        elif validator_enum is ValidatorsEnum.TARGETING_LOCATION:
            self.validator = TargetingLocationValidator(t1_service=t1_service)
        else:
            raise NotImplemented()

    def validate(self, *args, **kwargs):
        """
        Proxy validate method to proper class
        :return:
        """
        return self.validator.validate(*args, **kwargs)
