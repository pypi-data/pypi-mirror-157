from jsonschema import validate, ValidationError
from ni.config.tools import logger


class ParameterValidator(object):

    def __init__(self, parameter_schema: dict):
        self._parameter_schema = parameter_schema

    def validates(self, parameters: dict, strict: bool = False):
        res = True
        if strict:
            for parameter_name, parameter_value in self._parameter_schema.items():
                if parameter_name in parameters:
                    try:
                        validate(instance=parameters[parameter_name], schema=parameter_value)
                    except ValidationError:
                        logger.warning([1000, parameter_name])
                        res = False
                        break
                else:
                    logger.warning([1002, parameter_name])
                    res = False
                    break
        else:
            for parameter_name, parameter_value in parameters.items():
                if parameter_name in self._parameter_schema:
                    try:
                        validate(instance=parameter_value, schema=self._parameter_schema[parameter_name])
                    except ValidationError:
                        logger.warning([1000, parameter_name])
                        res = False
                        break
                else:
                    logger.warning([1001, parameter_name])
                    res = False
                    break
        return res

    def validate(self, parameter_name: str, parameter_value):
        res = True
        if parameter_name in self._parameter_schema:
            try:
                validate(instance=parameter_value, schema=self._parameter_schema[parameter_name])
            except ValidationError:
                logger.warning([1000, parameter_name])
                res = False
        else:
            logger.warning([1001, parameter_name])
            res = False
        return res
