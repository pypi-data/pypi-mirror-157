import logging

import colorama


class TermLog(logging.Formatter):
    grey = "\x1b[38m"
    blue = "\x1b[34m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    red_on_white = "\x1b[37;41m"
    reset = "\x1b[0m"
    # format_1 = "{color}[%(levelname)-8s]{reset}:%(asctime)s:%(name)s: %(message)s (%(filename)s:%(lineno)d)"
    # format_2 = "{color}[%(levelname).3s]{reset}:%(asctime)s:%(name)s: %(message)s (%(filename)s:%(lineno)d)"
    format = "{color}[{level}]{reset}:%(asctime)s:%(name)s: %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: format.format(color=blue, reset=reset, level="DBG"),
        logging.INFO: format.format(color=green, reset=reset, level="INF"),
        logging.WARNING: format.format(color=yellow, reset=reset, level="WRN"),
        logging.ERROR: format.format(color=red, reset=reset, level="ERR"),
        logging.CRITICAL: format.format(color=red_on_white, reset=reset, level="CRT"),
    }
    _handler = None

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

    def format_root_logger(self):
        if not self._handler:
            colorama.init()
            root = logging.getLogger()
            self._handler = logging.StreamHandler()
            self._handler.setFormatter(self)
            root.addHandler(self._handler)

    def get_logger(self, name, level=logging.INFO):
        self.format_root_logger()
        logger = logging.getLogger(name)
        logger.setLevel(level)
        # logger.addHandler(self._handler) # Not required if same handler is set on the root logger
        return logger


def main():
    log = TermLog().get_logger(__name__, logging.DEBUG)
    log.debug("This is a debug")
    log.info("This is a info")
    log.warning("This is a warning")
    log.error("This is a error")
    log.critical("This is a critical")
    return 0


if __name__ == "__main__":
    exit((main()))
