from tests import (
    tempLogFile,
    checkLog,
    callTracesSampleLogMessage,
    calltracesTestingInfoLogPrefixRegex,
    calltracesTestingWarningLogPrefixRegex,
    calltracesTestingErrorLogPrefixRegex,
)
from calltraces.linetrace import traceError, traceInfo, traceWarning
from calltraces.classtrace import classtrace
from calltraces import commonTraceSettings as traceSettings


@classtrace
class MyClassTraceTestClass:
    def __init__(self, a: int, b: int) -> None:
        self._a = a
        self._b = b

    def publicBaseFunction(self) -> int:

        self._privateFunction()
        self.__superPrivateFunction()

        traceInfo(callTracesSampleLogMessage)

        return self._a**2 + self._b**3

    def _privateFunction(self) -> None:
        self._a += 1

    def __superPrivateFunction(self) -> None:
        self._b += 1

    def publicWrapperFunction(self) -> None:
        return self.publicBaseFunction()


def test_class_trace(tempLogFile, checkLog) -> None:

    testObj = MyClassTraceTestClass(a=3, b=2)

    testObj.publicWrapperFunction()

    logRegularExpression = (
        calltracesTestingInfoLogPrefixRegex
        + r"tests\.test_classTrace\.MyClassTraceTestClass.publicWrapperFunction Starting Function"
        + "\n"
        + traceSettings.LOG_INDENTATION_CHAR
        + calltracesTestingInfoLogPrefixRegex
        + r"tests\.test_classTrace\.MyClassTraceTestClass.publicBaseFunction Starting Function"
        + "\n"
        + traceSettings.LOG_INDENTATION_CHAR
        + traceSettings.LOG_INDENTATION_CHAR
        + calltracesTestingInfoLogPrefixRegex
        + callTracesSampleLogMessage
        + "\n"
        + traceSettings.LOG_INDENTATION_CHAR
        + calltracesTestingInfoLogPrefixRegex
        + r"tests\.test_classTrace\.MyClassTraceTestClass.publicBaseFunction Finished Function"
        + "\n"
        + calltracesTestingInfoLogPrefixRegex
        + r"tests\.test_classTrace\.MyClassTraceTestClass.publicWrapperFunction Finished Function"
    )

    checkLog(
        regularExpression=logRegularExpression,
        tempLogFileToCheck=tempLogFile,
    )
