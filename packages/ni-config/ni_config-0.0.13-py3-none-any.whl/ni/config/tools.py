import logging


class Logger(object):
    def __init__(self, error_def: dict, logger_name='ni.config'):
        # create logger
        self._core = logging.Logger(logger_name, logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter('%(levelname)s | %(name)s | %(asctime)s | %(message)s')
        # add formatter to ch
        ch.setFormatter(formatter)
        # add ch to logger
        self._core.addHandler(ch)
        self._error_def = error_def
        self._log_msg = '[####] 临时打印信息：\n{0}'

    def debug(self, msg_args: list, *args, **kwargs):
        msg_id = str(msg_args[0])
        msg = self._error_def[msg_id].format(*msg_args)
        self._core.debug(msg, *args, **kwargs)
        return msg

    def info(self, msg_args, *args, **kwargs):
        msg_id = str(msg_args[0])
        msg = self._error_def[msg_id].format(*msg_args)
        self._core.info(msg, *args, **kwargs)
        return msg

    def warning(self, msg_args, *args, **kwargs):
        msg_id = str(msg_args[0])
        msg = self._error_def[msg_id].format(*msg_args)
        self._core.warning(msg, *args, **kwargs)
        return msg

    def error(self, msg_args, *args, **kwargs):
        msg_id = str(msg_args[0])
        msg = self._error_def[msg_id].format(*msg_args)
        self._core.error(msg, *args, **kwargs)
        return msg

    def critical(self, msg_args, *args, **kwargs):
        msg_id = str(msg_args[0])
        msg = self._error_def[msg_id].format(*msg_args)
        self._core.critical(msg, *args, **kwargs)
        return msg

    def log(self, obj, *args, **kwargs):
        msg = self._log_msg.format(*[obj])
        self._core.info(msg, *args, **kwargs)
        return msg

# 1000-1999: ParameterValidator
# 2000-2999: EncryptionConfig
# 3000-3999: Config
# 4000-4999：Others


ERROR_DEF = {
    '1000': '[{0}] 待校验参数{1}类型或其值异常，验证不通过',
    '1001': '[{0}] 待校验参数{1}属于非法参数，验证不通过',
    '1002': '[{0}] 缺少参数{1}，验证不通过',
    '2000': '[{0}] 成功读取文件"{1}"。',
    '2001': '[{0}] 找不到"{1}"。',
    '3000': '[{0}] 参数"desc"的类型应为str或dict。',
    '3001': '[{0}] 配置文件{1}内存在不符合要求的取值。',
    '3002': '[{0}] 成功读取文件"{1}"。',
    '3003': '[{0}] 找不到"{1}"。',
    '3004': '[{0}] {1}取值不符合要求。',
    '3005': '[{0}] 配置项{1}中不存在配置项{2}。',
    '3006': '[{0}] 配置项{1}的取值不符合要求。',
    '3007': '[{0}] 配置项{1}的取值的类型应为{2}。',
    '3008': '[{0}] 当参数"key"的类型为list时，列表中至少存在一个项目。',
    '3009': '[{0}] 参数"key"的类型应为str或list。',
    '4000': '[{0}] 参数update_object的类型应({1})与参数ori_object的({2})一致。'
}

logger = Logger(ERROR_DEF)
