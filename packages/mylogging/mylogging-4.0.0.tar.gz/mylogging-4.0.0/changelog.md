# List of what have been done in new versions

## 3.x - 2021
- level option addeed (DEBUG, WARNING, ERROR). In traceback set as parameter.
- set_warnings removed. Warnings displayed only once handled inside based on new config value filter - "once", "always", "ignore", "error" (now also working on traceback and in logging to file).
- For filtering list of defined warning messages now warnings__filter function is defined. There is also possibility to reset user original filters with reset__filter_warnings.
- filter_warnings to be able to filter repeated warnings (if default warnings `once` filter not working)

## 2.x - 2021
- Api changed to more conventional usage - mylogging - warn, info