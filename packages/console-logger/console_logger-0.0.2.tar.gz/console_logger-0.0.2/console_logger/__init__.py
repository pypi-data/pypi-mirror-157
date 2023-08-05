import sys
from datetime import datetime

"""
Yet another logging package for Python. 
"""

__all__ = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'LEVEL_NAMES',
           'critical', 'error', 'warning', 'info', 'debug',
           'ConsoleHandler', 'FileHandler', 'Logger', 'set_default_logger']

CRITICAL = 4
ERROR = 3
WARNING = 2
INFO = 1
DEBUG = 0

LEVEL_NAMES = {
    CRITICAL: 'CRITICAL',
    ERROR: 'ERROR',
    WARNING: 'WARNING',
    INFO: 'INFO',
    DEBUG: 'DEBUG'
}

# ———————————————————————————————————————————————————————————————————————————— #
# Terminal colors

class Color:
    """
    Base class for terminal color representation.
    """
    def __init__(self, color: tuple, color_type: str):
        # noinspection PyBroadException
        try:
            self.r, self.g, self.b = color
        except:
            sys.exit('Incorrect color')
        self.color_type = color_type
        if color_type == 'fg':
            self._ansi_seq = f"\033[38;2;{self.r};{self.g};{self.b}m"
        elif color_type == 'bg':
            self._ansi_seq = f"\033[48;2;{self.r};{self.g};{self.b}m"
        else:
            raise ValueError(f"Unexpected color type '{color_type}'")

    def __repr__(self):
        return f"<Color red={self.r}, green={self.g}, blue={self.b}>"

    @property
    def colorize(self):
        return self._ansi_seq

class FgColor(Color):
    """
    Foreground color
    """
    def __init__(self, r, g, b):
        super().__init__((r, g, b), 'fg')

class BgColor(Color):
    """
    Background color
    """
    def __init__(self, r, g, b):
        super().__init__((r, g, b), 'bg')

# ———————————————————————————————————————————————————————————————————————————— #
# LogRecord

class LogRecord:
    """
    LogRecord is an instance representing logged event.
    """
    def __init__(self, msg, level, traceback, carriage_return):
        self.created = datetime.now()
        self.level = level
        self.level_name = LEVEL_NAMES[level]
        self.msg = msg
        self.traceback = traceback
        self.cr = carriage_return

    def __repr__(self):
        return f"<LogRecord: {self.level_name}, \"{self.msg}\">"

# ———————————————————————————————————————————————————————————————————————————— #
# Handlers

class Handler:
    def __init__(self):
        pass

    def emit(self, record):
        pass

    def handle(self, record):
        self.emit(record)

class ConsoleHandler(Handler):
    _fg_color = {
        'default': FgColor(255, 255, 255),
        DEBUG    : FgColor(236, 236, 236),
        INFO     : FgColor(217, 217, 255),
        WARNING  : FgColor(255, 255, 217),
        ERROR    : FgColor(255, 217, 217),
        CRITICAL : FgColor(255, 100, 100)
    }
    _bg_color = {
        'default': BgColor(0  , 0 , 0),
        DEBUG    : BgColor(19 , 19, 19),
        INFO     : BgColor(0  , 0 , 38),
        WARNING  : BgColor(38 , 38, 0),
        ERROR    : BgColor(38 , 0 , 0),
        CRITICAL : BgColor(155, 0 , 0)
    }

    def __init__(self, colors):
        Handler.__init__(self)
        self.colors = colors

    def emit(self, record):
        print(self.format(record),
              end=(lambda r: '\r' if r else '\n')(record.cr))

    def format(self, record):
        if self.colors:
            level_name = self.colored(f"{record.level_name:^8}",
                                      self._fg_color[record.level],
                                      self._bg_color[record.level])
            msg = self.colored(record.msg,
                               self._fg_color[record.level],
                               self._bg_color['default'])
            return f"{self.timestamp(record)}" \
                   f" [{level_name}] " \
                   f"\033[K" \
                   f"{msg}"
        return f"{self.timestamp(record)}"\
               f" [{record.level_name:^8}] "\
               f"\033[K"\
               f"{record.msg}"

    @classmethod
    def colored(cls, txt, fg, bg):
        return f"{fg.colorize}{bg.colorize}" \
               f"{txt}" \
               f"{cls._fg_color['default'].colorize}" \
               f"{cls._bg_color['default'].colorize}"

    def timestamp(self, record):
        time = record.created.strftime('%d.%m.%y %H:%M:%S.%f')[:-3]
        if self.colors:
            return self.colored(time[:-4],
                                self._fg_color['default'],
                                self._bg_color['default'])\
                   + self.colored(time[-4:],
                                  FgColor(180, 180, 180),
                                  self._bg_color['default'])
        return time

class FileHandler(Handler):
    def __init__(self, filename, mode='a', encoding='utf8'):
        Handler.__init__(self)
        self.filename = filename
        self.mode = mode
        self.encoding = encoding

    def emit(self, record):
        with open(self.filename, self.mode, encoding=self.encoding) as f:
            f.write(self.format(record))

    def format(self, record):
        if record.traceback:
            traceback = f"\n{record.traceback}"
        else:
            traceback = ''
        return f"{self.timestamp(record)}"\
               f" [{record.level_name:^8}] "\
               f"{record.msg}"\
               f"{traceback}"\
               f"\n"

    @staticmethod
    def timestamp(record):
        return record.created.strftime('%d.%m.%y %H:%M:%S.%f')[:-3]

# ———————————————————————————————————————————————————————————————————————————— #
# Logger

class Logger:

    def __init__(self, level=INFO, file=None,
                 console_output=True, colors=True):
        self.level = level
        self.filename = file
        self.console_output = console_output
        self.colors = colors
        if console_output:
            self.console_handler = ConsoleHandler(colors)
        if file:
            self.file_handler = FileHandler(file)

    def debug(self, msg, traceback='', cr=False):
        if self.level <= DEBUG:
            self._log(msg, DEBUG, traceback, cr)

    def info(self, msg, traceback='', cr=False):
        if self.level <= INFO:
            self._log(msg, INFO, traceback, cr)

    def warning(self, msg, traceback='', cr=False):
        if self.level <= WARNING:
            self._log(msg, WARNING, traceback, cr)

    def error(self, msg, traceback='', cr=False):
        if self.level <= ERROR:
            self._log(msg, ERROR, traceback, cr)

    def critical(self, msg, traceback='', cr=False):
        if self.level <= CRITICAL:
            self._log(msg, CRITICAL, traceback, cr)

    def _log(self, msg, level, traceback='', cr=False):
        self.handle(LogRecord(msg, level, traceback, cr))

    def handle(self, record):
        if self.console_output:
            self.console_handler.handle(record)
        if self.filename:
            self.file_handler.handle(record)

# ———————————————————————————————————————————————————————————————————————————— #
# Logger functions at module level.

def debug(msg, *args, **kwargs):
    _logger.debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    _logger.info(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    _logger.warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    _logger.error(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    _logger.critical(msg, *args, **kwargs)

# default logger instance
_logger = Logger()

def set_default_logger(logger):
    """
    Change default logger at module level.
    :param logger: New logger instance.
    :return:
    """
    global _logger
    _logger = logger
