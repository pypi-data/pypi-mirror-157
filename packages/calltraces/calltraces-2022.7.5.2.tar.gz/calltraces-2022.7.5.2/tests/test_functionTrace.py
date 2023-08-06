from tests import (
    tempLogFile,
    checkLog,
    callTracesSampleLogMessage,
    calltracesTestingInfoLogPrefixRegex,
    calltracesTestingWarningLogPrefixRegex,
    calltracesTestingErrorLogPrefixRegex,
)
from calltraces.linetrace import traceError, traceInfo, traceWarning
from calltraces.functiontrace import functiontrace
from calltraces import commonTraceSettings as traceSettings


@functiontrace
def myBaseFunctionToTrace(a: int, b: int) -> int:
    traceInfo(callTracesSampleLogMessage)
    return a**2 + b**3


@functiontrace
def myWrapperFunctionToTrace(a: int, b: int) -> int:
    return myBaseFunctionToTrace(a=a, b=b)


def test_function_trace(tempLogFile, checkLog) -> None:

    myBaseFunctionToTrace(a=3, b=2)

    logRegularExpression = (
        calltracesTestingInfoLogPrefixRegex
        + r"tests\.test_functionTrace\.myBaseFunctionToTrace Starting Function"
        + "\n"
        + traceSettings.LOG_INDENTATION_CHAR
        + calltracesTestingInfoLogPrefixRegex
        + callTracesSampleLogMessage
        + "\n"
        + calltracesTestingInfoLogPrefixRegex
        + r"tests\.test_functionTrace\.myBaseFunctionToTrace Finished Function"
    )

    checkLog(
        regularExpression=logRegularExpression,
        tempLogFileToCheck=tempLogFile,
    )


def test_wrapper_function_trace(tempLogFile, checkLog) -> None:

    myWrapperFunctionToTrace(a=3, b=2)

    logRegularExpression = (
        calltracesTestingInfoLogPrefixRegex
        + r"tests\.test_functionTrace\.myWrapperFunctionToTrace Starting Function"
        + "\n"
        + traceSettings.LOG_INDENTATION_CHAR
        + calltracesTestingInfoLogPrefixRegex
        + r"tests\.test_functionTrace\.myBaseFunctionToTrace Starting Function"
        + "\n"
        + traceSettings.LOG_INDENTATION_CHAR
        + traceSettings.LOG_INDENTATION_CHAR
        + calltracesTestingInfoLogPrefixRegex
        + callTracesSampleLogMessage
        + "\n"
        + traceSettings.LOG_INDENTATION_CHAR
        + calltracesTestingInfoLogPrefixRegex
        + r"tests\.test_functionTrace\.myBaseFunctionToTrace Finished Function"
        + "\n"
        + calltracesTestingInfoLogPrefixRegex
        + r"tests\.test_functionTrace\.myWrapperFunctionToTrace Finished Function"
    )

    checkLog(
        regularExpression=logRegularExpression,
        tempLogFileToCheck=tempLogFile,
    )
