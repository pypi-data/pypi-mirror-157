import os
import re
import tempfile

import pytest
from calltraces import commonTraceSettings as traceSettings


@pytest.fixture
def tempLogFile() -> tempfile.NamedTemporaryFile:
    with tempfile.NamedTemporaryFile(
        suffix=".log", prefix=os.path.basename(__file__)
    ) as tf:
        tf_directory = os.path.dirname(tf.name)
        traceSettings.addOutputFileStream(tf.name)
        yield tf


@pytest.fixture
def checkLog():
    def checkLogFunction(
        regularExpression: str, tempLogFileToCheck: tempfile.NamedTemporaryFile
    ) -> None:
        tempLogFileToCheck.seek(0)

        logOutput = tempLogFileToCheck.read().decode(encoding="utf-8").strip()

        logRegex = re.compile(regularExpression)

        assert logRegex.match(logOutput)

    yield checkLogFunction


callTracesSampleLogMessage = "A sample log message to test calltraces..."
calltracesTestingTimeRegex = r"\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d "
calltracesTestingInfoLogPrefixRegex = r"\[INFO:\d\d\] " + calltracesTestingTimeRegex
calltracesTestingWarningLogPrefixRegex = (
    r"\[WARNING:\d\d\] " + calltracesTestingTimeRegex
)
calltracesTestingErrorLogPrefixRegex = r"\[ERROR:\d\d\] " + calltracesTestingTimeRegex
