import logging
import os
import sys
from datetime import datetime
from io import TextIOWrapper

from colorama import Back, Fore, Style
from calltraces import commonTraceSettings


def isDebuggerAttached() -> bool:
    gettrace = getattr(sys, "gettrace", None)

    if gettrace is None:
        return False
    elif gettrace():
        return True
    else:
        return False


def getStackDepthSpace(depth: int = 0):
    if depth <= 0:
        depth = commonTraceSettings.traceStackDepth
    return commonTraceSettings.LOG_INDENTATION_CHAR.join(["" for i in range(depth)])


def formatMessageForStackDepth(msg: str, depth: int = 0):
    return msg.replace(
        "\n",
        "\n"
        + commonTraceSettings.LOG_INDENTATION_CHAR
        + getStackDepthSpace(depth=depth),
    )


def traceInfo(msg, **kwargs) -> None:
    """
    Standard print statement that can be piped to a log stream or sent to a cloud logging solution
    """

    if not commonTraceSettings.enabled:
        return

    logLevel = kwargs.pop("logLevel", logging.INFO)

    kwargs["stackDepthSpace"] = getStackDepthSpace()
    kwargs["stackDepthNum"] = f"{commonTraceSettings.traceStackDepth:02}"

    isDebug = (logLevel <= logging.DEBUG) and isDebuggerAttached()

    if isDebug:
        logLevel = logging.INFO

    for color in commonTraceSettings.all_colors:
        color_selector = color
        if isDebug:
            color_selector += ".debug"
        kwargs[color] = commonTraceSettings.color_constants.get("info", {}).get(
            color_selector, Style.RESET_ALL
        )

    commonTraceSettings.logger.log(
        level=logLevel,
        msg=formatMessageForStackDepth(msg=msg),
        # args=args,
        extra=kwargs,
    )


def traceWarning(msg, **kwargs) -> None:
    """
    Standard warning print statement that can be piped to a log stream or sent to a cloud logging solution
    """

    logLevel = kwargs.pop("logLevel", logging.WARNING)

    kwargs["stackDepthSpace"] = getStackDepthSpace()
    kwargs["stackDepthNum"] = f"{commonTraceSettings.traceStackDepth:02}"

    isDebug = (logLevel <= logging.DEBUG) and isDebuggerAttached()

    if isDebug:
        logLevel = logging.WARNING

    for color in commonTraceSettings.all_colors:
        color_selector = color
        if isDebug:
            color_selector += ".debug"
        kwargs[color] = commonTraceSettings.color_constants.get("info", {}).get(
            color_selector, Style.RESET_ALL
        )

    commonTraceSettings.logger.log(
        level=logLevel,
        msg=formatMessageForStackDepth(msg=msg),
        # args=args,
        extra=kwargs,
    )


def traceError(msg, **kwargs) -> None:
    """
    Standard error print statement that can be piped to a log stream or sent to a cloud logging solution
    """

    logLevel = kwargs.pop("logLevel", logging.ERROR)

    kwargs["stackDepthSpace"] = getStackDepthSpace()
    kwargs["stackDepthNum"] = f"{commonTraceSettings.traceStackDepth:02}"

    isDebug = (logLevel <= logging.DEBUG) and isDebuggerAttached()

    if isDebug:
        logLevel = logging.ERROR

    for color in commonTraceSettings.all_colors:
        color_selector = color
        if isDebug:
            color_selector += ".debug"
        kwargs[color] = commonTraceSettings.color_constants.get("info", {}).get(
            color_selector, Style.RESET_ALL
        )

    if type(msg) != str:
        msg = str(msg)

    sys_exc_info = sys.exc_info()

    is_exception = (
        sys_exc_info is not None
        and type(sys_exc_info) == tuple
        and sys_exc_info[0] is not None
    )

    if is_exception:

        msg += f"""\nDetailed Stack Trace: \n"""

        tb_frame = sys_exc_info[2]
        while tb_frame is not None:

            msg += f"""\n{commonTraceSettings.LOG_INDENTATION_CHAR}{str(tb_frame.tb_frame)}\n"""
            msg += f"""\n{commonTraceSettings.LOG_INDENTATION_CHAR}{commonTraceSettings.LOG_INDENTATION_CHAR}Local Variables:\n"""

            f_locals = tb_frame.tb_frame.f_locals

            for varName in f_locals.keys():
                try:
                    varValue = f_locals[varName]
                    if str(type(varValue)).lower().find("dataframe") >= 0:
                        varValue = f"DataFrame with type {type(varValue)}"
                    else:
                        varValue = str(varValue)
                    if len(varValue) > 1000:
                        varValue = varValue[:999] + "..."
                except Exception as ex:
                    varValue = f"Error getting variable {varName} value. {ex}"
                varValue = formatMessageForStackDepth(msg=varValue, depth=3)
                msg += f"""{commonTraceSettings.LOG_INDENTATION_CHAR}{commonTraceSettings.LOG_INDENTATION_CHAR}[Type {type(varValue)}] {varName} = {varValue}\n"""

            tb_frame = tb_frame.tb_next

    commonTraceSettings.logger.log(
        level=logLevel,
        msg=formatMessageForStackDepth(msg=msg),
        # args=args,
        extra=kwargs,
        exc_info=is_exception,  # Get exception information if available
    )
