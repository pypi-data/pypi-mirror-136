# NagiosCheckHelper

This library helps with the boilerplate nagios check formating, status information, and basic evaluations when writing a Python nagios/icinga check

## Installation
It's on pypi, so it's as easy as installing via pip
```
pip3 install NagiosCheckHelper
```

## NagErrors Object

An object to hold the Errors that have occured.

Generally you can call it with obj.addCritical(error text) or obj.addWarning(error text) to accumulate your errors

Then call obj.printStatus() to print the formatted Errors

Then call obj.doExit() to exit your program with the proper result code.

### Usage
#### Object Creation
No parameters, so just do a:
```
from NagiosCheckHelper import NagErrors
nerr = NagErrors()
```

#### Logging Errors
There are 4 functions for logging errors:
- addRecord(eType,etext)
- addCritical(etext)
- addWarning(etext)
- addUnknown(etext)

- eType would be the type of error. One of: critical, warning, or unknown\
- etext is the Error message (without any Error or Warning prefix, that's automatically added)

example:
```
from NagiosCheckHelper import NagErrors
nerr = NagErrors()
nerr.addRecord("critical", "The printer is on fire.")
nerr.addWarning("The printer is out of paper.")
nerr.addUnknown("The printer grew legs and walked out the door.")
```

#### Outputting status
There are 2 main functions for outputting status:
- printStatus() - print out the formatted status lines
- doExit() - Exit the program with the proper status code.


### NagErrors "full" example:
A quick example that sets a couple messages and exits
```
from NagiosCheckHelper import NagErrors
nerr = NagErrors()
nerr.addCritical("This is a Critical Event")
nerr.addWarning("This is a Warning Event")
nerr.printStatus()
nerr.doExit()
```

## NagEval Object

An object with common subroutines to evaluate data and cause error events based on the comparisons.

Be sure to initite it with an NagErrors Object.

### Usage
#### Object Creation
Takes a NagErrors object to track errors, so just do a:
```
from NagiosCheckHelper import NagErrors, NagEval
nerr = NagErrors()
neval = NagEval(nerr)
```

#### Evaluate value against Enumerated Values
Evaluate a value based on lists of enumerated values
```
evalEnum(value, defaultStatus="UNKNOWN", okValues=[], warningValues=[], criticalValues=[], unknownValues=[], prefixText="", postfixText= "")
```

#### Evaluate List of values against Enumerated Values
Evaluate a list of values based on lists of enumerated values
```
values = ['value1', 'value2', 'value3']
evalListEnum(values, emptyStatus="UNKNOWN", unknownValueStatus="UNKNOWN", okValues=[], warningValues=[], criticalValues=[], unknownValues=[], prefixText="", postfixText= "")
```

#### Evaluate Numbers
There are 2 evaluators that will handle number ranges (asending and decending):
```
evalNumberAsc(value, warningAbove=None, criticalAbove=None, prefixText="", postfixText="", numberUnits="")
evalNumberDesc(value, warningBelow=None, criticalBelow=None, prefixText="", postfixText= "", numberUnits="")
```

#### Evaluate List of Numbers
There are 2 evaluators that will handle lists of numbers based on number ranges (asending and decending):
```
values = [5, 90, 55, 200001]
evalListNumberAsc(values, emptyStatus="UNKNOWN", warningAbove=None, criticalAbove=None, prefixText="", postfixText="", numberUnits="")
evalListNumberDesc(values, emptyStatus="UNKNOWN", warningBelow=None, criticalBelow=None, prefixText="", postfixText= "", numberUnits="")
```


### NagEval "full" example:
A quick example that tests a value, outputs the results and exits with the proper code
```
from NagiosCheckHelper import NagErrors, NagEval
nerr = NagErrors()
neval = NagEval(nerr)
neval.evalNumberAsc(95, warningAbove=80, criticalAbove=90, numberUnits="%")
nerr.printStatus()
nerr.doExit()
```

## Full Examples
These are full examples/checks that use this library and click to handle most of the boilerplate and script is mostly just defining the options and running the actual check.
- [check_puppet_agent](https://github.com/paradxum/check_puppet_agent)
- [check_truenas](https://github.com/paradxum/check_truenas)

