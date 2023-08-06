# -*- coding: utf-8 -*-

import os
import logging
import coloredlogs
import datetime

DEFAULT_LEVEL_STYLES = dict(
    spam=dict(color='green', faint=True),
    debug=dict(color='white'),
    verbose=dict(color='blue'),
    info=dict(color='blue'),
    notice=dict(color='magenta'),
    warning=dict(color='yellow'),
    success=dict(color='green'),
    error=dict(color='red'),
    critical=dict(color='red'))

_DEFAULT_LOG_LEVEL = logging.DEBUG
_DEFAULT_OUTPUT_FMT = '[%(asctime)s] [pid:%(process)4d] %(filename)30s line:%(lineno)4d [%(levelname)s] %(message)s'

_DEFAULT_FILE_FMT = _DEFAULT_OUTPUT_FMT
_DEFAULT_FILE_OP_MODE = 'a'


BASE_DIR = os.getcwd().split("testcase")[0]
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
TEST_RESULT_DIR = os.path.join(BASE_DIR, 'testresult').replace('\\', '/', -1)
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)
if not os.path.exists(TEST_RESULT_DIR):
    os.mkdir(TEST_RESULT_DIR)
os.environ['SINGLE_TEST_RESULT_DIR'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
LOGS_DIR = os.path.join(TEST_RESULT_DIR, str(os.environ.get('SINGLE_TEST_RESULT_DIR')))
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

class Logger(object):
    LOG_TYPE_CONSOLE = 0
    LOG_TYPE_FILE = 1
    LOG_TYPE_ALL = 2
    logger = None

    @staticmethod
    def set_log_level(log_level):
        if isinstance(log_level, str):
            log_level = getattr(logging, log_level.upper(), logging.WARNING)
        Logger.logger.setLevel(log_level)

    @staticmethod
    def create_console_handler(log_level):
        if isinstance(log_level, str):
            level = getattr(logging, log_level.upper(), _DEFAULT_LOG_LEVEL)
        else:
            level = log_level

        # Create handler for console output.
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        # Define the handler formatter.
        formatter = coloredlogs.ColoredFormatter(level_styles=DEFAULT_LEVEL_STYLES, fmt=_DEFAULT_OUTPUT_FMT)
        console_handler.setFormatter(formatter)
        return console_handler

    @staticmethod
    def create_file_handler(file_name, log_level):
        if isinstance(log_level, str):
            level = getattr(logging, log_level.upper(), _DEFAULT_LOG_LEVEL)
        else:
            level = log_level
        # Create handler for log file.
        f_handler = logging.FileHandler(file_name, _DEFAULT_FILE_OP_MODE, encoding='utf-8', delay=True)
        f_handler.setLevel(level)
        formatter = logging.Formatter(fmt=_DEFAULT_FILE_FMT)
        f_handler.setFormatter(formatter)
        return f_handler

    @staticmethod
    def get_logger(name=None, log_file_name='{}.log'.format(os.environ.get('SINGLE_TEST_RESULT_DIR')),
                   console_level='DEBUG', file_level='DEBUG', log_type=LOG_TYPE_ALL):
        """
        :param name: the log name for distinguish logger instances. Default is root.
        :param log_file_name: specify the log file name, can use default.
        :param console_level: console log level. type: string
        :param file_level: file log level. type: string
        :param log_type: 0: console, 1: log file, other value: both. Default: console.
        """
        if Logger.logger is None:
            Logger.logger = logging.getLogger(name)
            Logger.logger.setLevel(_DEFAULT_LOG_LEVEL)
            console_handler = Logger.create_console_handler(console_level)
            f_handler = Logger.create_file_handler(os.path.join(LOGS_DIR, log_file_name), file_level)

            # Add the handlers to logger.
            if log_type == Logger.LOG_TYPE_CONSOLE:
                Logger.logger.addHandler(console_handler)
            elif log_type == Logger.LOG_TYPE_FILE:
                Logger.logger.addHandler(f_handler)
            else:
                Logger.logger.addHandler(console_handler)
                Logger.logger.addHandler(f_handler)
        return Logger.logger


# logger = Logger.get_logger(name=__name__)
logger = Logger.get_logger()


class TextFileLoggerHandler(logging.Handler):
    """
    Archived, to adapt the history script
    """
    def __init__(self, file_path=None):
        logging.Handler.__init__(self)
        self.file_path = os.path.join(LOGS_DIR, file_path)

    def emit(self, record):
        msg = self.format(record)
        _dir = os.path.dirname(self.file_path)
        try:
            if os.path.exists(_dir) is False:
                os.makedirs(_dir)
        except Exception as e:
            print('cannot make dirs:{}, error msg:{}'.format(_dir, e))
        with open(self.file_path, 'a') as _fobj:
            _fobj.write(msg + '\n')
            _fobj.flush()


def create_text_file_logger_handler(file_name):
    """
    Archived, to adapt the history script
    """
    tfh = TextFileLoggerHandler(file_name)
    tfh.setLevel(logging.DEBUG)
    fmt = logging.Formatter(fmt='[%(asctime)s] %(filename)30s line:%(lineno)4d [%(levelname)s] %(message)s')
    tfh.setFormatter(fmt)
    return tfh


if __name__ == '__main__':
    logger.setLevel('INFO')
    logger.debug("This is a debug msg.")
    logger.info("This is a info msg.")
    logger.warning("This is a warning msg.")
    logger.error("This is a error msg.")
    logger.critical("This is a critical msg.")
