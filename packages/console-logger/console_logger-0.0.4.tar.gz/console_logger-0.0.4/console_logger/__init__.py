import sys
from datetime import datetime

"""
Yet another logging package for Python. 
"""

__all__ = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'LEVEL_NAMES',
           'critical', 'error', 'warning', 'info', 'debug',
           'Logger', 'set_default_logger']

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
    def __init__(self, msg, level, /, *,
                 file, console_output, colors,
                 traceback='', carriage_return=False, **kwargs):
        self.created = datetime.now()
        self.msg = msg
        self.level = level
        self.level_name = LEVEL_NAMES[level]
        self.file = file
        self.console_output = console_output
        self.colors = colors
        self.traceback = traceback
        self.carriage_return = carriage_return
        self.kwargs = kwargs

    def __repr__(self):
        return f"<LogRecord: {self.level_name}, \"{self.msg}\">"

# ———————————————————————————————————————————————————————————————————————————— #
# Handlers

class Handler:
    """
    Common base interface for handlers.
    """
    def __init__(self):
        pass

    def emit(self, record):
        pass

    def format(self, record):
        pass

    def handle(self, record):
        self.emit(record)

class ConsoleHandler(Handler):
    """
    This handler process colored console output.
    """
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
              end=(lambda r: '\r' if r else '\n')(record.carriage_return))

    def format(self, record):
        if record.traceback:
            traceback = f"\n{record.traceback}"
        else:
            traceback = ''
        if self.colors:
            level_name = self.colored(f"{record.level_name:^8}",
                                      self._fg_color[record.level],
                                      self._bg_color[record.level])
            msg = self.colored(f"{record.msg}{traceback}",
                               self._fg_color[record.level],
                               self._bg_color['default'])
            return f"{self.timestamp(record)}" \
                   f" [{level_name}] " \
                   f"\033[K" \
                   f"{msg}"
        return f"{self.timestamp(record)}"\
               f" [{record.level_name:^8}] "\
               f"\033[K"\
               f"{record.msg}" \
               f"{traceback}"

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
    """
    FileHandler instance is used for writing logging records to text file.
    """
    def __init__(self, filename, /,
                 file_opening_mode='a', file_encoding='utf8',
                 **kwargs):
        Handler.__init__(self)
        self.filename = filename
        self.file_opening_mode = file_opening_mode
        self.file_encoding = file_encoding

    def emit(self, record):
        with open(self.filename,
                  self.file_opening_mode,
                  encoding=self.file_encoding) as f:
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
    """
    Main class which creates the logger instance.
    This logger receives messages and sends it to proper handlers.
    """
    def __init__(self, level=INFO, file=None,
                 console_output=True, colors=True, **kwargs):
        self.level = level
        self.file = file
        self.console_output = console_output
        self.colors = colors
        if console_output:
            self.console_handler = ConsoleHandler(colors)
        if file:
            self.file_handler = FileHandler(file, **kwargs)

    def debug(self, msg, /, **kwargs):
        if self.level <= DEBUG:
            self._log(msg, DEBUG, **kwargs)

    def info(self, msg, /, **kwargs):
        if self.level <= INFO:
            self._log(msg, INFO, **kwargs)

    def warning(self, msg, /, **kwargs):
        if self.level <= WARNING:
            self._log(msg, WARNING, **kwargs)

    def error(self, msg, /, **kwargs):
        if self.level <= ERROR:
            self._log(msg, ERROR, **kwargs)

    def critical(self, msg, /, **kwargs):
        if self.level <= CRITICAL:
            self._log(msg, CRITICAL, **kwargs)

    def _log(self, msg, level, /, **kwargs):
        self._handle(LogRecord(msg, level,
                               file=kwargs.get('file', self.file),
                               console_output=kwargs.get('console_output',
                                                         self.console_output),
                               colors=kwargs.get('colors', self.colors),
                               **kwargs))

    def _handle(self, record):
        if (record.file is not None) \
                and (record.carriage_return is False):
            try:
                self.file_handler.handle(record)
            except AttributeError:
                FileHandler(record.file, **record.kwargs).handle(record)
        if record.console_output:
            try:
                self.console_handler.handle(record)
            except AttributeError:
                ConsoleHandler(record.colors).handle(record)

# ———————————————————————————————————————————————————————————————————————————— #
# Logger functions at module level.

def debug(msg, /, **kwargs):
    _default_logger.debug(msg, **kwargs)

def info(msg, /, **kwargs):
    _default_logger.info(msg, **kwargs)

def warning(msg, /, **kwargs):
    _default_logger.warning(msg, **kwargs)

def error(msg, /, **kwargs):
    _default_logger.error(msg, **kwargs)

def critical(msg, /, **kwargs):
    _default_logger.critical(msg, **kwargs)

# default logger instance
_default_logger = Logger()

def set_default_logger(logger):
    """
    Change default logger at module level.
    :param logger: New logger instance.
    :return:
    """
    global _default_logger
    _default_logger = logger
