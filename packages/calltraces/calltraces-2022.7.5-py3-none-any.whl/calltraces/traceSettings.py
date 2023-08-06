import logging
import os
import pathlib
import sys
from io import TextIOWrapper
from colorama import Fore, Style
from colorama.ansi import AnsiFore


class PipelineLogFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "stackDepthSpace"):
            record.stackDepthSpace = ""
        if not hasattr(record, "stackDepthNum"):
            record.stackDepthNum = ""
        if not hasattr(record, "color1"):
            record.color1 = ""
        if not hasattr(record, "color2"):
            record.color2 = ""
        if not hasattr(record, "color3"):
            record.color3 = ""
        return True


class traceSettings(object):
    """
    Common settings for tracing the program.

    Example:
    ```
        from calltraces.functiontrace import functiontrace

        @functiontrace
        def myFunc(myParam):
            ...
    ```
    """

    enabled = True
    """
    Global flag for enabling tracing
    """

    LOG_INDENTATION_CHAR = "\t"
    """
    Indentation character to use when showing nested traces
    """

    printArguments = False
    """
    Print the function argument values
    """

    printOutputs = False
    """
    Print the function argument values
    """

    traceStackDepth = 1
    """
    How much to indent a function call. Helpful to measure call-stack depth
    """

    all_colors = ["color1", "color2", "color3"]

    FORMAT_CONSOLE = (
        f"%(stackDepthSpace)s"
        + f"%(color1)s"
        # + f"[%(process)d:%(levelname)s:%(stackDepthNum)s] %(asctime)s"
        + f"[%(levelname)s:%(stackDepthNum)s] %(asctime)s"
        + f"%(color2)s "
        + f"%(message)s"
        + f"%(color3)s"
    )

    FORMAT_FILE = (
        f"%(stackDepthSpace)s"
        # + f"[%(process)d:%(levelname)s:%(stackDepthNum)s] %(asctime)s "
        + f"[%(levelname)s:%(stackDepthNum)s] %(asctime)s "
        + f"%(message)s"
    )

    ignoreSymbols = []

    color_constants = {
        "info": {
            "color1": Fore.GREEN,
            "color2": Style.RESET_ALL,
            "color3": "",
            "color1.debug": Fore.CYAN,
            "color2.debug": " DEBUG:",
            "color3.debug": Style.RESET_ALL,
        },
        "warning": {
            "color1": Fore.YELLOW,
            "color2": "",
            "color3": Style.RESET_ALL,
            "color1.debug": Fore.YELLOW,
            "color2.debug": Fore.CYAN + " DEBUG:",
            "color3.debug": Style.RESET_ALL,
        },
        "error": {
            "color1": Fore.RED,
            "color2": "",
            "color3": Style.RESET_ALL,
        },
    }

    def addOutputFileStream(self, outputFileStream: any) -> None:
        outputFullPathUpper = (
            str(pathlib.Path(outputFileStream).absolute()).strip().upper()
        )

        if outputFullPathUpper in self.outputs:
            return  # Skip adding an existing file to the output stream

        os.makedirs(name=os.path.dirname(outputFileStream), exist_ok=True)

        # create console handler and set level to debug
        fh = logging.FileHandler(filename=outputFileStream, encoding="utf-8")
        fh.setLevel(logging.INFO)

        # create formatter
        formatter = logging.Formatter(
            fmt=self.FORMAT_FILE,
        )

        # add formatter to fh
        fh.setFormatter(formatter)

        # add fh to logger
        self.logger.addHandler(fh)

        self.outputs.append(outputFullPathUpper)

    def __init__(self, *outputStreams):
        """
        Any trace setting initializations
        """
        self.traceStackDepth = 1

        # create console handler and set level to debug
        self.logger = logging.getLogger(name="calltraces")
        self.logger.setLevel(logging.INFO)

        # add logging filter
        self.logger.addFilter(filter=PipelineLogFilter())

        # ch = self.logger.handlers[0]
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # create formatter
        formatter = logging.Formatter(
            fmt=self.FORMAT_CONSOLE,
        )

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        self.logger.addHandler(ch)

        self.outputs = []

        for s in outputStreams:
            self.addOutputFileStream(s)
