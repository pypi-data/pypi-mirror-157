import logging
import os


class Formatter(logging.Formatter):
    """
    Pretty logging output, courtesy of StackOverflow:
      https://stackoverflow.com/questions/384076/
    """

    GREY = "\x1b[38;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    RED_BOLD = "\x1b[31;1m"
    RESET = "\x1b[0m"
    TEMPLATE = "%(message)s"

    FORMATS = {
        logging.DEBUG: GREY + TEMPLATE + RESET,
        logging.INFO: GREEN + TEMPLATE + RESET,
        logging.WARNING: YELLOW + TEMPLATE + RESET,
        logging.ERROR: RED + TEMPLATE + RESET,
        logging.CRITICAL: RED_BOLD + TEMPLATE + RESET,
    }

    def format(self, record):
        return logging.Formatter(self.FORMATS[record.levelno]).format(record)


class Loggable:
    """
    Use this mixin to do logging:
      self.logger.debug("My debugging message")
    """

    __logger = None
    _log_level = os.getenv("LOG_LEVEL", "WARNING")

    @property
    def logger(self) -> logging.Logger:

        if self.__logger:
            return self.__logger

        handler = logging.StreamHandler()
        handler.setFormatter(Formatter())

        logging.basicConfig(handlers=(handler,), level=self._log_level)

        self.__logger = logging.getLogger(self.__class__.__module__)

        return self.logger
