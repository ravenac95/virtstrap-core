import logging

CLINT_AVAILABLE = True
try:
    from clint.textui import puts, colored
except:
    # Clint is still not stable enough yet to just import with so much
    # trust, but I really like colored output. So we'll give it a shot
    CLINT_AVAILABLE = False

class VirtstrapConsoleLogHandler(logging.Handler):
    def __init__(self, outputter):
        self._outputter = outputter
        logging.Handler.__init__(self)

    def emit(self, record):
        outputter = self._outputter 
        outputter.write(record.msg, record.levelname)

class ConsoleLogOutputter(object):
    def write(self, output, level):
        print(output)

class ColoredConsoleLogOutputter(ConsoleLogOutputter):
    level_colors = {
        "DEBUG": "green",
        "INFO": "black",
        "WARNING": "yellow",
        "CRITICAL": "purple",
        "ERROR": "red",
        "EXCEPTION": "red",
    }
    def write(self, output, level):
        color = self.level_colors.get(level, "black")
        colored_function = getattr(colored, color, lambda text: text)
        colored_output = colored_function(output)
        puts(colored_output)

logger = logging.getLogger("virtstrap")

VERBOSITY_LEVELS = {
    0: None,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
}

def setup_logger(verbosity, no_colored_output=False):
    """Sets up the logger for the program. DO NOT USE DIRECTLY IN COMMANDS"""
    verbosity_level = VERBOSITY_LEVELS.get(verbosity, logging.INFO)
    if not verbosity_level:
        return
    outputter = ConsoleLogOutputter()
    if CLINT_AVAILABLE:
        outputter = ColoredConsoleLogOutputter()
    console_handler = VirtstrapConsoleLogHandler(outputter=outputter)
    logger.setLevel(verbosity_level)
    console_handler.setLevel(verbosity_level)
    logger.addHandler(console_handler)
