# ts_t1_validator
Python library for pre-validation of models used for terminalOne API based on jsonschema validation and combination of rules.
Implemented validators and rules include different type, length and business logic validations.

### Pre-requirement. Install Python 3

**MacOS (using `brew`)**

```
brew install python3
```

Installation
============

Installation is simple with pip in a virtual environment:

``` {.bash}
$ pip install ts-t1-validator
```

Execution
============================
### General usage
To use some specific validator for particular terminalOne object call T1Validator and provide dictionary of the object you'd like to validate and name of object as validator_type.
`t1_creds` are used for validations that are performed with the help of T1 api, so it requires valid oauth access token and host that is used in api code from which this validators were called.

#### Campaign:
``` {.python}
from ts_t1_validator import T1Validator

t1_creds = {"token": "token",
            "host": "https://<host>"}
                         
validator = T1Validator(t1_creds=t1_creds, validator_type="campaign")
errors = validator.validate(dto=campaign_dict)
```

`.validate()` method expects dictionary of t1 entity object. For example for campaign validator it should be campaign model as dictionary, that corresponds t1 entity requirements to pass all validations, or you can use jsonchema files (`*.json`) in ts-t1-validator.validators.entity_name.schema folders:
```
{'advertiser_id': 106713, 'campaign_name': 'Phillip Harrell', 'is_programmatic_guaranteed': False, 'status': False, 'spend_cap_automatic': False, 'spend_cap_type': 'even', 'spend_cap_amount': 1608198.58, 'zone_name': 'Asia/Riyadh', 'start_date': '2022-02-23T15:00', 'end_date': '2022-02-24T15:00', 'currency_code': 'BBD', 'budget': 6465878.24, 'goal_type': 'ctr', 'goal_value': 42, 'frequency_optimization': False, 'frequency_type': 'asap', 'frequency_interval': 'month', 'frequency_amount': 4297351, 'restrict_targeting_to_same_device_id': True}
```

#### Strategy:
``` {.python}
from ts_t1_validator import T1Validator

t1_creds = {"token": "token",
            "host": "https://<host>"}
                         
validator = T1Validator(t1_creds=t1_creds, validator_type="strategy")
errors = validator.validate(dto=startegy_dict, campaign_dto=campaign_dict)
```


### Custom validator
To create custom validator use inheritance from `AbstractValidator` and init pack of validation rules (`self.rules`) from `ts_t1_validator.validators.rules`:
``` {.python}
import os
from typing import Dict

from ts_t1_validator import AbstractValidator, T1Service
from ts_t1_validator.validators.rules.t1_advertiser import T1AdvertiserRule


class CustomValidator(AbstractValidator):
    def __init__(self, t1_service: T1Service):
        self.rules = list()
        self.errors = list()
        self.json_schema = os.path.dirname(os.path.abspath(__file__)) + "/path_to_file/file.json"
        self.t1_service = t1_service
        
    def build_rules_set(self, dto: Dict): 
        # init object parameters
        advertiser_id = dto.get('param_name')

        self.rules.append(T1AdvertiserRule(
            advertiser_id=advertiser_id,
            t1_service=self.t1_service))
```

`AbstractValidator.validate(dto)` uses jsonschema validation for json from `self.json_schema` that can be created according to [JSONSchema](https://json-schema.org/learn/getting-started-step-by-step.html#starting) standard.
Or you can use the following example with general jsonschema validations:

```json
{
  "title": "exampleJsonSchema",
  "description": "description about this schema",
  "properties": {
    "advertiser_id": {
      "type": "integer",
      "minimum": 1
    },
    "campaign_name": {
      "type": "string",
      "maxLength": 256,
      "minLength": 2,
      "example": "Campaign 1"
    },
    "status": {
      "type": "boolean"
    },
    "some_enum": {
      "type": "string",
      "enum": [
        "val1",
        "val2"
      ]
    }
  },
  "required": ["advertiser_id",
    "campaign_name",
    "status"
  ]
}
```

Package maintenance
============================
### Increase package version and update changelog
After making any package changes, make sure you have increase package version in setup.py file (`version="0.1.0"`) according to importance of your changes, shortly:
* Patch release (0.1.0 -> 0.1.1): patch releases are typically used for bug fixes, which are backward compatible. Backward compatibility refers to the compatibility of your package with previous versions of itself. For example, if a user was using v0.1.0 of your package, they should be able to upgrade to v0.1.1 and have any code they previously wrote still work. It’s fine to have so many patch releases that you need to use two digits (e.g., 0.1.27).

* Minor release (0.1.0 -> 0.2.0): a minor release typically includes larger bug fixes or new features that are backward compatible, for example, the addition of a new function. It’s fine to have so many minor releases that you need to use two digits (e.g., 0.13.0).

* Major release (0.1.0 -> 1.0.0): release 1.0.0 is typically used for the first stable release of your package. After that, major releases are made for changes that are not backward compatible and may affect many users. Changes that are not backward compatible are called “breaking changes”. For example, changing the name of one of the modules in your package would be a breaking change; if users upgraded to your new package, any code they’d written using the old module name would no longer work, and they would have to change it.

Also ensure you have added description of changes made in [ CHANGELOG.md](https://gist.github.com/juampynr/4c18214a8eb554084e21d6e288a18a2c) file (please do not forgot that some changes can be listed in Unreleased section).

### Package deployment
Package deployment is available only for authorized in [PyPI](https://pypi.org/) users, that are maintainers of [ts-t1-validator](https://pypi.org/project/ts-t1-validator/) package
Now that you are registered, you can use twine to upload the distribution packages. You’ll need to install Twine is you have not it installed:
```{.bash}
python3 -m pip install --upgrade twine
```
Make a wheel of prepared package from the root of project:
```
python setup.py sdist bdist_wheel 
```
That will create dist/ folder is if not exist and create a wheel with new version
After that you can run Twine to upload all of the archives under dist:
```{.bash}
twine upload --skip-existing dist/*
```
You will be prompted for a username and password. For the credentials use [PyPI](https://pypi.org/) username and password. After the command completes, you should see output similar to this:
```
Uploading distributions to https://upload.pypi.org/legacy/
Enter your username: [your_username]
Enter your password: 
Uploading ts_t1_validator-[new_version]-py3-none-any.whl
100%|██████████████████████k/52.1k [00:02<00:00, 22.7kB/s]
Uploading ts-t1-validator-[new_version].tar.gz
100%|█████████████████████.0k/30.0k [00:01<00:00, 16.4kB/s]

uVz%/9niYRKk4Z9
View at:
https://pypi.org/project/ts-t1-validator/[new_version]/
```
Once uploaded your package should be viewable on TestPyPI.
