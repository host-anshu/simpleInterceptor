## Change Log

All notable changes to this project will be documented in this file.


### [0.1] - 2016-05-04

#### Added
- Don't intercept magic methods except __init__.
- Example to minimally lint ansible playbook for undefined variable.

#### Changed
- Pass method and its return value to advices.

#### Fixed
- Exact method name using `\b` wasn't working.
- Exception from the method was being suppressed.

#### Removed
- `@classmethod` won't be intercepted now(temporarily).


### [0.1.dev1] - 2016-04-18
First Release
