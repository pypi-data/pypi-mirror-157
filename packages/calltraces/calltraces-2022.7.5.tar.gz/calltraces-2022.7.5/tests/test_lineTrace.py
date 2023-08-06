from tests import (
    tempLogFile,
    checkLog,
    callTracesSampleLogMessage,
    calltracesTestingInfoLogPrefixRegex,
    calltracesTestingWarningLogPrefixRegex,
    calltracesTestingErrorLogPrefixRegex,
)
from calltraces.linetrace import traceError, traceInfo, traceWarning


def test_info_line_trace(tempLogFile, checkLog) -> None:

    traceInfo(callTracesSampleLogMessage)

    checkLog(
        regularExpression=calltracesTestingInfoLogPrefixRegex
        + callTracesSampleLogMessage,
        tempLogFileToCheck=tempLogFile,
    )


def test_warning_line_trace(tempLogFile, checkLog) -> None:

    traceWarning(callTracesSampleLogMessage)

    checkLog(
        regularExpression=calltracesTestingWarningLogPrefixRegex
        + callTracesSampleLogMessage,
        tempLogFileToCheck=tempLogFile,
    )


def test_error_line_trace(tempLogFile, checkLog) -> None:

    traceError(callTracesSampleLogMessage)

    checkLog(
        regularExpression=calltracesTestingErrorLogPrefixRegex
        + callTracesSampleLogMessage,
        tempLogFileToCheck=tempLogFile,
    )
