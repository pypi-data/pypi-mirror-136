# bifrost-common

A library of commonly used functions to interact with BIFROST. Useful for module developers.

## Installation

```
pip install bifrost-common-py
```

## Components

### Log

A module to print nice logging information to the console and, optionally, to files.

```
from bifrost_common_py.Log import Log

log = Log('myComponent', 'myApplication', options={'maxLogFileSize':1e4, 'enableLogFiles':True})

log.write(`Abandon ship`, Log.WARNING)
log.write(`Run like hell`, Log.INFO)
```

Log levels are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `FAILURE`

Allowed `options` are:
- `enableLogFiles` (default: `false`): log to files as well as the console
- `logDir` (default: `log`): the log file directory (will be created as necessary)
- `maxLogFileSize` (default: `0`): maximum byte size of the log files, after which a new file will be started, default =`0` never rollover
- `maxArchiveSize`(default: 5): maximum number of log files to keep

### time

Some useful operations involving time, mostly for formatting `Log` output.

### idOfRef

Resolve the ID contained in an object. If no 'id' field is found in the
object pointed to with `ref`, the last part of the reference is returned instead.

```
from bifrost_common_py.idOfRef import idOfRef

print(idOfRef({ 'A': { 'id': '1' }}, '/A')) // '1'

```

### tokens

An object collecting string tokens commonly used in the BIFROST state.

```
import bifrost_common_py.tokens as tokens

print(tokens.tkId) // "id"
```

### select

Selectors returning fully-qualified JSON paths into the BIFROST state.

```
import bifrost_common_py.pathSelectors as select

print(select.meta())                      # "/meta"
print(select.dynamicId('DYNAMIC-1'))      # "/dynamics/byId/DYNAMIC-1"
print(select.eventParentRef('EVENT-1'))   # "/events/byId/EVENT-1/parentRef"
```

### safepointer

A wrapper that allows to specify default values if paths can not be resolved. This is best used in conjunction with `select` and a copy of the BIFROST state.

#### API

```
import bifrost_common_py.safepointer
```

##### .has(obj, path)

Determine whether the fully-qualified JSON pointer `path` points to something in `obj`.

```
safepointer.has({ 'A': { 'B': 1} }, '/A/B') # true
safepointer.has({ 'A': { 'B': 1} }, '/A/C') # false
```

##### .get(obj, path, def = null)

Resolve `path` against `obj`. If the path does not exist, `def` is returned instead.

```
safepointer.get({ 'A': { 'B': 1} }, '/A/B', 0)  # 1
safepointer.get({ 'A': { 'B': 1} }, '/A/C', 0)  # 0

import bifrost_common_py.pathSelectors as select

safepointer.get(state, select.meta(), {}) // { id: ... }
```

### SelectFrom

A declarative state selection library. Use this to select elements from the BIFROST state or from module subscription data.

```
    from bifrost_common_py.SelectFrom import SelectFrom

    SelectFrom(state).allDynamics().ofType('VOLTAGE-3P').asValueMap()

    SelectFrom(subs).allEntries().ofType('CLIMATE-MODEL').asValueList()

    SelectFrom(subs, state).allEntries().withParentOfType('WEATHER').asValueMap()
```