import os
import yaml
import json
from ni.config.tools import logger
from jsonschema import validate, ValidationError
from copy import deepcopy
from abc import ABCMeta, abstractmethod
from cryptography.fernet import Fernet


def replace(ori_object, update_object):
    if type(ori_object) == type(update_object):
        if isinstance(ori_object, dict):
            new_object = deepcopy(ori_object)
            for key, value in update_object.items():
                if key in ori_object:
                    new_object[key] = replace(ori_object[key], value)
            return new_object
        else:
            return update_object
    else:
        raise TypeError(logger.error([4000, type(update_object), type(ori_object)]))


class Config(object):

    def __init__(self, desc):
        # 初始化
        self._name = ''
        self._value = {}
        self._desc = {}
        self._default = {}
        # 根据不同的参数进行构建实例
        if isinstance(desc, str):
            filename = desc + '.desc'
            desc_tmp = self._load(filename)
            self._name = desc_tmp['name']
            self._desc = desc_tmp['schema']
            self._default = desc_tmp['default']
        else:
            if isinstance(desc, dict):
                self._name = desc['name']
                self._desc = desc['schema']
                self._default = desc['default']
            else:
                raise TypeError(logger.error([3000]))
        self.set_default()

    def validate(self):
        try:
            validate(instance=self._value, schema=self._desc)
            return True
        except ValidationError:
            return False

    def load_config(self, config_filename):
        old_value = deepcopy(self._value)
        values = self._load(config_filename)
        for k, v in values.items():
            try:
                self[k] = v
            except ValueError:
                self._value = old_value
                raise ValueError(logger.error([3001, config_filename]))

    def _load(self, ori_filename):
        result = Config.load(ori_filename)
        if result is None:
            return {}
        else:
            return result

    @staticmethod
    def load(ori_filename):
        obj_json = None
        filename = os.path.join(os.getcwd(), ori_filename)
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                obj_json = yaml.safe_load(f)
                logger.info([3002, filename])
        else:
            logger.warning([3003, filename])
        return obj_json

    def _dump(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self._value, f, indent=4)

    def dump(self, dist_filename=None):
        if self.validate():
            config_filename = self._name + '.cfg'
            if dist_filename is None:
                pass
            else:
                config_filename = dist_filename
            filename = os.path.join(os.getcwd(), config_filename)
            self._dump(filename)
        else:
            raise AssertionError(logger.error([3004, self._name]))

    def __getitem__(self, item):
        if item in self._value:
            return self._value[item]
        else:
            raise KeyError(logger.error([3005, self._name, item]))

    def __setitem__(self, key, value):
        if key in self._value:
            t = type(self._default[key])
            if isinstance(value, t):
                old_value = deepcopy(self._value)
                self._value[key] = replace(self._value[key], value)
                if self.validate():
                    pass
                else:
                    self._value = old_value
                    raise ValueError(logger.error([3006, key]))
            else:
                raise ValueError(logger.error([3007, key, t]))
        else:
            raise KeyError(logger.error([3005, self._name, key]))

    def __repr__(self):
        return self._value.__repr__()

    def __contains__(self, item):
        return item in self._value

    def is_default(self, key=None):
        if key is None:
            return self._value == self._default
        else:
            if isinstance(key, str):
                return self._value[key] == self._default[key]
            if isinstance(key, list):
                num = len(key)
                if num > 0:
                    value = self._value[key[0]]
                    default = self._default[key[0]]
                    for i in range(1, num):
                        value = value[key[i]]
                        default = default[key[i]]
                    return value == default
                else:
                    raise ValueError(logger.error([3008]))
            raise TypeError(logger.error([3009]))

    def set_default(self):
        self._value = deepcopy(self._default)


class Codec(metaclass=ABCMeta):

    @abstractmethod
    def encode(self, content):
        pass  # pragma: no cover

    @abstractmethod
    def decode(self, content):
        pass  # pragma: no cover


class EncryptionConfig(Config):

    def __init__(self, desc: str, codec: Codec):
        self._codec = codec
        super().__init__(desc)

    def _load(self, ori_filename):
        obj_json = None
        filename = os.path.join(os.getcwd(), ori_filename)
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                content = f.read()
                obj_json = yaml.safe_load(self._codec.decode(content))
                logger.info([2000, filename])
        else:
            logger.warning([2001, str(filename)])
        if obj_json is None:
            return {}
        else:
            return obj_json

    def _dump(self, filename):
        with open(filename, 'wb') as f:
            content = json.dumps(self._value, indent=4)
            f.write(self._codec.encode(content))


class EasyCodec(Codec):

    def __init__(self, key_filename: str = None):
        super().__init__()
        self._key = Fernet.generate_key()
        self._encryption = Fernet(self._key)
        if key_filename is None:
            pass
        else:
            with open(key_filename, 'rb') as f:
                self._key = f.read()
                self._encryption = Fernet(self._key)

    def save_key(self, filename="key.dat"):
        with open(filename, 'wb') as f:
            f.write(self._key)

    def encode(self, content):
        return self._encryption.encrypt(content.encode())

    def decode(self, content):
        return self._encryption.decrypt(content).decode()
