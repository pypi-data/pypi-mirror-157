# Call Traces

[![Build Status](https://dev.azure.com/righteous-ai/Python-Repos/_apis/build/status/calltraces?branchName=azure-pipelines)](https://dev.azure.com/righteous-ai/Python-Repos/_build/latest?definitionId=6&branchName=azure-pipelines)
![Azure DevOps coverage](https://img.shields.io/azure-devops/coverage/righteous-ai/Python-Repos/6)
![PyPI](https://img.shields.io/pypi/v/calltraces)
![Azure DevOps tests](https://img.shields.io/azure-devops/tests/righteous-ai/Python-Repos/6?compact_message)
![PyPI - Downloads](https://img.shields.io/pypi/dd/calltraces)
![PyPI - Format](https://img.shields.io/pypi/format/calltraces)
![PyPI - Status](https://img.shields.io/pypi/status/calltraces)
![GitHub](https://img.shields.io/github/license/righteouslabs/calltraces)
![GitHub language count](https://img.shields.io/github/languages/count/righteouslabs/calltraces)
![GitHub top language](https://img.shields.io/github/languages/top/righteouslabs/calltraces)
![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/righteouslabs/calltraces)
![Snyk Vulnerabilities for GitHub Repo](https://img.shields.io/snyk/vulnerabilities/github/righteouslabs/calltraces)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/righteouslabs/calltraces/colorama)
![Libraries.io dependency status for GitHub repo](https://img.shields.io/librariesio/github/righteouslabs/calltraces)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/righteouslabs/calltraces)
![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/righteouslabs/calltraces)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/calltraces)

A small package for tracing function calls

## Installing ⏬

```bash
pip install calltraces
```

## Usage 📝

Python code:

```python
from calltraces.linetrace import traceInfo
from calltraces.functiontrace import functiontrace

# ...

@functiontrace # Add a function decorator
def myFunction():
    traceInfo("some log message...")

# ...

# Whenever the function is called:
myFunction()
```

This will produce the output:

```bash
[INFO:01] 2022-06-26 18:00:32,234 __main__.myFunction Starting Function
	[INFO:02] 2022-06-26 18:00:32,235 some log message...
[INFO:01] 2022-06-26 18:00:32,235 __main__.myFunction Finished Function
```

## Advanced Usage 🪆

Python code:

```python
from calltraces.linetrace import traceInfo
from calltraces.functiontrace import functiontrace

# ...

@functiontrace
def myFunction1():
    traceInfo("some log message...")

@functiontrace
def myFunction2():
    myFunction1()

@functiontrace
def myFunction3():
    # Calling a function twice
    myFunction2()
    myFunction2()

# ...

# Whenever the function is called:
myFunction3()
```

This will produce the output:

```bash
[INFO:01] 2022-06-26 18:06:38,625 __main__.myFunction3 Starting Function
	[INFO:02] 2022-06-26 18:06:38,626 __main__.myFunction2 Starting Function
		[INFO:03] 2022-06-26 18:06:38,634 __main__.myFunction1 Starting Function
			[INFO:04] 2022-06-26 18:06:38,634 some log message...
		[INFO:03] 2022-06-26 18:06:38,634 __main__.myFunction1 Finished Function
	[INFO:02] 2022-06-26 18:06:38,634 __main__.myFunction2 Finished Function
	[INFO:02] 2022-06-26 18:06:38,634 __main__.myFunction2 Starting Function
		[INFO:03] 2022-06-26 18:06:38,635 __main__.myFunction1 Starting Function
			[INFO:04] 2022-06-26 18:06:38,635 some log message...
		[INFO:03] 2022-06-26 18:06:38,635 __main__.myFunction1 Finished Function
	[INFO:02] 2022-06-26 18:06:38,635 __main__.myFunction2 Finished Function
[INFO:01] 2022-06-26 18:06:38,635 __main__.myFunction3 Finished Function
```

## Usage with classes 📦

Adding the python decorator on a class will automatically add trace wrappers to public functions.

> ⚠️ Private functions will stay unaffected.

Python code:

```python
from calltraces.linetrace import traceInfo
from calltraces.classtrace import classtrace

# ...

@classtrace # Add a class decorator
class MyObject:
    def __init__(self, input) -> None:
        self._x = input

    def _privateFunction(self):
        self._x = self._x * 2

    def __superPrivateFunction(self):
        self._x = self._x * 3

    def publicBaseFunction(self):
        self._privateFunction()
        self.__superPrivateFunction()
        traceInfo("some log message...")

    def publicWrapperFunction(self) -> None:
        return self.publicBaseFunction()

# ...

# Whenever the object functions are called
myObj = MyObject(input=12345)
myObj.publicWrapperFunction()
```

This will produce the output:

```bash
[INFO:01] 2022-06-26 18:17:15,456 __main__.MyObject.publicWrapperFunction Starting Function
	[INFO:02] 2022-06-26 18:17:15,456 __main__.MyObject.publicBaseFunction Starting Function
		[INFO:03] 2022-06-26 18:17:15,456 some log message...
	[INFO:02] 2022-06-26 18:17:15,456 __main__.MyObject.publicBaseFunction Finished Function
[INFO:01] 2022-06-26 18:17:15,456 __main__.MyObject.publicWrapperFunction Finished Function
```
