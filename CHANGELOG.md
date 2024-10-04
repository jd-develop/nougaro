# Changelog

Since 0.16.0-beta, Nougaro follows [Semantic Versioning](https://semver.org).

This file is updated nearly every commit and copied to GH release changelog.

Since 0.19.0-beta, we use [this changelog format](https://keepachangelog.com). It consists of 6 sections, titled `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. The Nougaro changelog has another section, `Calculator`, keeping track of the changes relative to the Nougaro Calculator under the same 6-sections format.

## upcoming

### Added
* Added `math.gcd`, that takes exactly two integer arguments and return their
gcd.

### Changed
* Any value can now be passed as `assert` error message (and will be converted
to str)
* `$` and the following identifier can now be spaced (`$ id` is now valid)

### Fixed
* Fixed a crash in `math.log` on base=1
* Updated error messages when method in not defined in python-written modules
(does not change anything to public API)
* Optimised asserts a little bit
* Fixed bug where identifiers after `$` could start with digits
* Better error messages

#### Build scripts
* Build scripts now copy `CHANGELOG.md`.
* `build.bat` is now more verbose.

### Calculator
#### Fixed
* Fixed a crash with `log` on base=1

## 1.1.0 (2024-08-13)

### Added
* Added the `loop` loop, which is an infinite loop.
* Add support for newlines after `(` and `[`, before `)` and `]`, as well as inside lists, calls, and function defs, and after commas.
  For instance, this is now legal:
  ```nougaro
  def a(
     b,
     c
  )(
     d = 4,
     e = 5
  )
      stuff
  end
  ```

### Changed
* Version id has been increased to `10`

### Calculator
#### Added
* Added the `sto` instruction, that stores the last value in the stack into the memory.
* Added the `gsto` variable, which is the value contained in the memory.

#### Changed
* The `p` instruction can be used in any command (e.g. things like `1 2 + p` are now possible)

## 1.0.0 (2024-07-08)
*As this change does not affect public API, this is released as 1.0.0*

### Fixed
* `(Build scripts)` (Windows) The build script now properly removes `__pycache__`.

## 1.0.0-rc.2 (2024-07-02)

### Fixed
* Maybe fixed some encoding bugs (for instance with imports) under Windows

## 1.0.0-rc.1 (2024-06-28)

*Note: rc stands for release candidate.*

### Changed
* Version id has been increased to `9`.

### Fixed
* Fixed attribute error messages (previously, `(1).b` was giving the message `AttributeError: attribute of 1 has no attribute 'b'.`, which was erroneous)

## 0.23.0-beta (2024-06-26) [YANKED]

### Added
* Added `noug_version.clean_version_for_nuitka_under_windows()` function, that returns a nice output of the Nougaro version that can be passed into the `--windows-product-version` Nuitka argument. Takes 2 optional parameters: `print_value` (default=False), which, if true, makes the function prints the result; and `return_value` (default=True), which, if true, makes the function returns the result.
* Added two new optional parameters to the `noug_version.clean_version_for_gh()` function: `print_value` (default=False), which, if true, makes the function prints the result; and `return_value` (default=True), which, if true, makes the function returns the result.

### Changed
* Version ID has been increased to `8`.

### Fixed
* `(Build scripts)` (Windows) Fix Nuitka crashing when called

## 0.22.0-beta (2024-06-26)

This version comes with a new huge functionality – optional parameters –, rather big bug fixes, as well as smaller tweaks and fixes.

### Added
* Added optional parameters to function definitions. Use `def identifier(mendatory1, mendatory2)(optional1=default_value, optional2=default_value)` to define optional parameters. When you call the function, you can omit the optional arguments. If you want to leave `optional1` to its default value but to change `optional2`, you can use `identifier(mendatory1, mendatory2, <default>, new_value)`.
* Added the `<default>` token, and the `<default>` value.
* Added a new type of comments (NOUGAROIGNORE). They are opened and closed by `..NOUGAROIGNORE` or `.. NOUGAROIGNORE` where `.` is any character among `#@/%!$;`. There should not be anything else on lines where there are NOUGAROIGNORE opening or closing statements.

### Changed
* Version ID has been increased to `7`.
* Lib version has been increased to `4`.
* Key `"run_noug_dir_work_dir"` in BuiltinFunction dictionaries (and in libs too) was renamed to `"run_noug_dir"`.
* Type of functions is now `func`, regardless of if they are functions or built-in functions. However, type of methods is still `method`.
* Modules and functions are now True in boolean context (i.e. in a condition)
* `round` built-in function now returns `int` if `n_digits` ⩽ 0, not only for `n_digits` = 0.
* `__how_many_lines_of_code__` now accepts any value as argument (it checks if the value is true).
* `(Internal API)` `dived_by` and `floor_dived_by` methods in Values are now renamed to `divided_by` and `floor_divided_by`.
* `(Build scripts)` (Windows) The Nougaro version is now automatically fetched.

### Removed
* `(Internal API)` `to_str_`, `to_int_`, `to_float_`, `to_list_` methods in Values are now removed. Please use `to_str`, `to_int`, `to_float` and `to_list` instead.

### Fixed
* Fixed position start and end of duplicate arguments error messages.
* `__test__` and `example` builtin functions now work from every location in the file system.
* Fixed functions returning `None` if their return value was interpreted as `False` (empty string, empty list, …)
* Fix a potential crash with errors (when an error occurs in an empty line…)

## 0.21.0-beta (2024-06-11) [YANKED]

This version is small but contains a rather big crash fix, as well as a deprecation.

### Changed
* Data version has been increased to `7`.
* Lib version has been increased to `3`.
* Version ID has been increased to `6`.
* Data in the config files can now be typed, meaning that only a certain type of data can be written.
* Under GNU/Linux and Unix, panicsort (`sort(list, "panic")`) now crashes with `illegal hardware instruction` instead of `segmentation fault` when the list is not sorted (funnier). Thanks [@Mistera91](https://github.com/Mistera91)!
* `(Internal API)` Changed `to_str_`, `to_int_`, `to_float_`, `to_list_` methods to `to_str`, `to_int`, `to_float` and `to_list` in Values. The old name are now deprecated and will be removed in 0.22.0 (or will be removed in 1.0.0-rc.1 if it releases before 0.22.0)

### Deprecated
* `(Internal API)` `to_str_`, `to_int_`, `to_float_`, `to_list_` methods in Values are now deprecated and will be removed in 0.22.0. Please use `to_str`, `to_int`, `to_float` and `to_list` instead.

### Removed
* `(Internal API/Writing libs)` Removed `TRUE`, `FALSE` and `NULL` values, please use `Number(True)`, `Number(False)` and `Number(0)` instead.

### Fixed
* Fixed a crash when giving too many arguments to a function having the property `should_respect_args_number` set to `False`.
* Fixed a bug with `position_end` of call nodes (it was just before the closing parenthesis)

## 0.20.0-beta (2024-06-06)

This version may in some cases improve performance.

### Added

#### Syntax
* Allow the `+` sign in a e-infix expression (such as `10e+3`)

#### Flow control
* Add the `break and return (value)` syntax, which allows to return a certain value when breaking a loop.
* Add loop labels:
  * Using the syntax `for:label`, `while:label` or `do:label`, you can label your loops.
  * Using the syntax `break:label` and `continue:label`, you can break or continue an outer loop.

#### Builtins
* Add the `is_object` builtin function
* Add the `is_constructor` builtin function

#### Metas
* Add the `appendNoneOnContinue` meta
  * Takes no argument
  * If enabled, loops will append `None` to  their result if there is a `continue` (see the Changed section)
* Add the `appendNoneOnBreak` meta
  * Takes no argument
  * If enabled, loops will append `None` to  their result if there is a `break` (see the Changed section)

#### Command line interface
* Add the `-i` (or `--interactive`) CLI argument. Allows to run an interactive shell after executing
  a file, within the context of that file (i.e. with all the variables)

#### Technical and debug
* Add the `print_time` debug option: add `debug.should_print_time` (0 or 1), `debug.print_time()`, `debug.stop_print_time()`. This option prints the total time different parts of Nougaro took to complete.
* `[Internal API]` Add `RecursionError`, accessible in libs using `RTRecursionError`.
* `[Internal API]` Add Library Version, accessible through `src.noug_version.LIB_VERSION`. It is stored in the key `"lib-version"` in `noug_version.json`. It is currently `2`.

### Changed
#### Syntax
* Numbers can no longer have trailing underscore at the beginning or at the end.

#### Runtime
* Loops no longer append `None` to their result if there is a `continue` or `break`. Use `appendNoneOnContinue` and `appendNoneOnBreak` metas if you still want to do that.
* Rework completely equality and other comparisons to be more consistent
  * Functions, built-in functions, methods and module functions can now be equal (if they’re the same)
  * Same for objects and constructors
  * Strings can now be less than or equal to others, according to the alphabetical order.
    For instance, `"foo" > "bar"`, and `"hello" < "world"`.
  * `<`, `<=`, `>`, `>=` comparisons now crash when used on lists, modules, constructors, objects, any function, None.
  * `and`, `or` and `xor` now works properly with functions, methods, built-in functions
* Functions can now be converted to strings using `str()`.
* Representation of the `exit` builtin function is now `"Use exit(), CTRL+C (i.e. interrupt) or CTRL+D (i.e. EOF) to exit."` instead of `"<built-in function exit>"`.

#### Technical and debug
* `debug.enable_all()` and `debug.disable_all()` now also enable or disable the `print_time` debug option.
* Data version has been increased to `6`.
* Version ID has been increased to `5`.
* `[Internal API]` It is now possible to compare Nodes and Tokens. Use `node1 == node2` or `node1 != node2`. Does not check `pos_start` and `pos_end`, so it is better than `hash(node1) == hash(node2)`.
* `[Build scripts]` (Linux) The Nougaro version is now automatically fetched.

#### Writing libraries
* Modules written in Python now need to have a library version (`__LIBRARY_VERSION__`). If a module doesn’t have the same
  library version as the current Nougaro version, an error is thrown. Library version is currently `2`.
* Libraries now need the `is_eq` method as described in documentation.

### Removed
* Removed `noug_version.phase_minor`. Use `noug_version.release_serial` instead.

### Fixed
* Fix position start of constructors in error messages.
* `10eanystringofcharacters-10` is no longer parsed to `10e-10`, and throws an error instead.
* Fix a crash on maximum recursion depth exceeded.
* Fix a bug where you could have two parameters with the same name in a function definition.
* Start and end positions of `xor` are now correct.
* Accessing a variable no longer return a copy of the value, but directly the value instead. It allows things such as `def return(object)->object; var return(a).b = 4` (this previously left `a.b` unchanged, it now properly updates it to 4)
* `input_num` now returns an integer if the entered value is an integer, otherwise it returns a float.
* Fix a crash when trying to print surrogates Unicode characters (within a pair or not)

## 0.19.0-beta (2024-05-08)

This version comes with a lot of new features, and one single deprecation (see “How to update” to know how to update your code). This version improves a little bit performances in some cases.

### Added

#### Libs
* Add the `noug_version.clean_version_for_gh` function that generates a beautiful str for the GH issues or PRs.
* Add `noug_version.release_serial` which is the same as `noug_version.phase_minor`, as it is now deprecated.
* Add `math.factorial`, which computes factorial.
* Add `webbrowser` lib, which contains one function:
  * `webbrowser.open(url, new=0, autoraise=True)`: display `url` using the default browser.
        If `new` is 0, the `url` is opened in the same browser window if possible.
        If `new` is 1, a new browser window is opened if possible.
        If `new` is 2, a new tab is opened if possible.
        If `autoraise` is True, the window is raised if possible (note that under many window managers this will occur regardless of the setting of this variable).

#### Metas
* Add a “meta” system
  * Using the syntax `@meta metaName` or `@meta metaName metaValue` at the beginning of a file, you can now enable special features
  * As predicate, you can use `@`, `#@`, `%@`, `@@`, `-@` or `$@`.
* Add `legacyAbs` meta
  * No value required
  * It makes the legacy absolute value possible: `|-1|`=`1`
  * However, it makes bit-wise or not accessible.
* Add `nbspBetweenFrenchGuillemets` meta
  * No value required
  * Experience the true french pain! (and I don’t talk about baguettes…) If you want to use the french string quotes (`«»`), you will have to put a no-break space (or a narrow no-break space) after the `«` and before the other `»`. Those (N)NBSP will not be counted in the string.
* Add `setTheTestValueTo` meta
  * Sets `__the_test_value__` to the str value given in the meta value
  * If no value is given, it sets it to `None`.

#### Technical
* Data version and version ID can now be known using `__data_version__` and `__version_id__`.
* Data version is now stored in `./noug_version.json`
* `(lib to make libs)` Add `default_pos` function, which returns a tuple (Position, Position)
* `(Internal API)` Noug version can now be retrieved using `src.noug_version` library. It consists of 8 constants: `MAJOR`, `MINOR`, `PATCH`, `PHASE`, `RELEASE_SERIAL`, `VERSION` (`str`), `VERSION_ID`, `DATA_VERSION`. It does not contains “phase minor”, as it is now called “release serial”.
* `(Build scripts)` It is now possible to use a custom python command in `build.sh` by passing the command as parameter. Note that I forgot to mention that this is possible with `run_tests.sh` since 0.18.0-beta.

### Changed
* Renamed “phase minor” to “release serial”. In `noug_version.json`, the key is renamed from `phase-minor` to `release-serial`. The different “phase minor” references are now deprecated (see the Deprecated section), and will be removed in 0.20.0

#### Technical
* Moved `./config/noug_version.json` to `./noug_version.json`
* Data version has been increased to 5
* Version ID has been increased to 4
* Argument handling has been rewritten back without `argparse`, it was causing more issues than it simplified things
* Renamed the `--command_dont_verbose` CLI option to `--command-dont-verbose`.
* Each value now takes `pos_start` and `pos_end` arguments, so watch out if you’re making libs! These changes will be available in the documentation (along with everything else)

### Deprecated

* `noug_version.phase_minor` is deprecated and will be deleted in 0.20.0.

### Fixed

* Fix typos
* Fix a bug where files were referred as `<stdin>` in the shell (and therefore in error messages, etc.)
* Fix some crashes with imports (where values didn’t have any context)
* Fix an internal bug where the first optional argument of functions whose `should_respect_args_number` was `False` was not populated. Never happen in real life because no such function take optional arguments, but you know, just in case.
* Unit tests now work properly when debug mode is enabled
* Fix the fact that Nougaro exited with exit code 0 even when there was an error using `-c`, `-d`, etc.
* Sometimes, tracebacks in error messages indicated file `(unknown)` and line `(unknown)`: this has been fixed

### Calculator
#### Added
* Add the possibility to print the current value (last value in stack) using `p`.
* Add the possibility to exit with `exit()` (yes, it was frustrating)
* Add a “DC mode”, accessible using `-d` or `--dc-mode` option, which is a minimal, teletype-friendly mode.
* Add the possibility to print the help message using `-h` CLI option.
* Add the possibility to print the last error message with `h`.
* Add factorial with `number !`.

#### Removed
* Remove the possibility to print i with `pi` (it is now possible to get the value of π outside of an operation)
* Remove the possibility to print the help with `h`

#### Fixed
* Adding more dots into a float no longer does the same thing as adding multiple floats (for instance, `1.9.12` was previously parsed to `2.02`, which is the same as `1 0.9 + 0.12 +`)

### How to update
> [!Important]
> If you were using `noug_version.phase_minor`, simply replace it with `noug_version.release_serial`, as `phase_minor` is now deprecated.

## 0.18.0-beta (2024-03-16)
### Syntax
* `«` and `»` are now valid string delimiters
* Allow to nest multi-line comments
* Allow the use of NBSP and NNBSP as spaces

### Changes
* `list(list_value)` now returns an unlinked copy of the original list
* Remove `PROTECTED_VARS`, which means that variables can now use builtin names as identifiers.
* Change repo image
* Under GNU/Linux and Unix, add an interactive history using `readline`. May not work with non-GNU/Linux systems.

### Built-in functions
* Add `path_exists(path)` builtin function
* Add `print_in_green(value)` and `print_in_green_ret(value)` builtins functions
* Add miracle sort and panic sort

### Fixes
* Better error messages
* Fix crashes in `math.log`
* Fix several overflow crashes
* Fix other crashes
* Fix some bugs, such as #18
* Fix a bug where values other than String and Number weren’t printed in `input`

### Libs
* Add `noug_version.version_list`
* Add `math.tau` and `math.sqrt_tau`.

### Technical
* Add more tests
* Rewrite argument handling in `shell.py` using `argparse` (arguments have changed, use `(nougaro) -h` to view the new arguments)
* (internal API) py2noug can now properly convert lists and tuples containing python values
* (internal API) py2noug can now properly convert dicts, under a list of [key, value] lists
* (internal API) add an alias `is_noug_num` to `is_n_num` function
* (internal API) add an alias `is_tok_type` to `does_tok_type_exist` function
* Moved config files to the right directory depending on the OS (such as `~/.config`). More infos in the docstring of the `src.conffiles` file.
* Add a `version_id`. Incremented at least each new version. The current `version_id` is 3.

### Calculator
* Now, the stack is kept at the end of a command. You can make computations using multiple commands, like in Unix’ `dc`.
  Note that if there is an error, the stack is left unchanged.
* Add logarithm
* Add a bunch of debugging commands (such as `printi`, `prints`, `resets`, `rsi`, …) and aliases for existing commands (such as `quit`).
* Add `tau`
* Better error messages
* Move the RPN examples from the greeter to the help, and add an example
* If debug is enabled (through `debug.enable()` in Nougaro), it now prints tokens

## 0.17.0-beta (2024-01-19)

### Technical
* Fix a lot of crashes and a lot of bugs
* Rewrite and type hint the source code
* Better error messages
* Add some edge-case tests
* Now works with pipe operator in (...)sh
* Change lib API

### Calculator
* Add `e` in calculator
* Fix bugs in calculator

## 0.16.0-beta (2023-11-27)

### Syntax

* Add `var ... ++` and `var ... --`

### Loops

* Loops now append `None` to their result even if the node is `None`, not printable, or if the loop is broke or continued.

### Modules

#### Import and export

* Add `import ... as ...`
* You can now import Nougaro files from current folder and sub-folders.
* Add `export (node) as ...`
* `export` now returns the value to export

#### Builtin libs

* Add `noug_version` lib
* Fixed an old bug in the `debug` lib:
  * When you activate the debug mode from the shell, you no longer need to restart it for errors to print their origin file.

### Builtin functions

* Add `__python__` builtin func
* Update `reverse` builtin function (fix error message + can now take strings as argument)
* Improve `__gpl__` builtin func on BSD:
  * now can take any command as text editor

### Misc

* Better error messages
* Switch to semantic versioning
* Add `__args__` to have access to CLI args (except in Nebraska)
* Better retro-compatibility with python 3.10 in tests
* Add a reference to this changelog file in the intro text
* Add back lines to the intro text to be more pleasant to read
* Add python version to intro text in debug mode

## 0.15-beta (2023-10-14)
### Object-oriented
* Nougaro is now object-oriented!
  * Add `class` keyword
  * Add `constructor`, `object` and `method` types

### Builtin functions
* Add `__py_type__` builtin function
* Add `sort` builtin function
   * 3 algorithms: `timsort` (default), `stalin` and `sleep` (sleep sort was implemented by @Mistera91, thank you :smile:)
* Add `startswith` and `endswith` builtin functions
* Add `reverse` builtin function
* Add `print_in_red` and `print_in_red_ret` builtin functions

### Syntax
* Add possibility to make a new line inside a str, like in `"a";"b"`, which is equivalent to `"ab"`
* Add `var variable.attribute = value`
* Add multi-line comments (with `/* */` syntax)
* Add dollar-print
   * syntax: `$identifier`
   * prints and returns the content of variable `identifier`
   * if not defined, prints and returns the string `"$identifier"`
   * if no identifier is given, prints and returns the string `"$"`
* Add `"\x00"`, `"\u0000"` and `"\U00000000"` escape characters in strings, as well as `"\N{UNICODE_CHAR_NAME}"`

### Modules
* Add `unicodedata` module
* Add `debug.disable()` and `debug.enable()` aliases (same as `debug.debug_mode_disable()` and `debug.debug_mode_enable()`)
* Add `random.shuffle()` and `random.seed()`
* Add `time.time()` and `time.epoch()`
* Add `math.isqrt()` and `math.iroot()`

### Examples
* Various changes in `calculator` example
   * `done`
   * `cls`, `clear`
   * `//`
   * `help`
   * `i`

### Misc
* Add `-V` (`--version`) CLI option
* Fix various bugs, crashes, typos, error messages, …
* Rewrite some files
* Add best match in error messages (`... is not defined, did you mean ...?`)
* Delete highlight theme for notepad++ (I’m currently working on a VSCode one)

## 0.14-beta (2023-08-20)

* Add `-c` option to run a line, and `-cd` to do that silently
* Add `--help` option
* Add Tic Tac Toe example
* Make `colorama` optional to run Nougaro.
* Results of loops no longer contain `None`
* Better error messages
* Better intro text
* A lot of bug fixes, including #10 and interpreter crashes
* Fix typos

### Calculator
* Better error messages
* Fix crashes
* Add `sqrt`, `pi`, `mod`
* Add `clear` command

### Meta
* Improve build scripts

## 0.13.1-beta (2023-02-15)
This release fixes a little bug, updates the repo structure and makes Nougaro mostly work under FreeBSD and OpenBSD.

## 0.13-beta (2023-02-07)
* ADD  `lorem` LIB
* ADD `export` statement
* Add `calculator` example
* Add `is_module` builin func
* Str is now iterable (`str(3)`)
* Fix keyword `and` (`False and stuff` will now ignore completely `stuff`)
* Fix variable edit permissions (`__noug_dir__`)
* Make things return their values instead of None (if, for, while, do while)
* Fix (finally) #6
* Fix a critical bug (interpreter crash)
* Fix a bug where the shell tries to execute itself (python code) when renamed
* Now, for Nougaro modules too you need to write `module.value` instead of `module_value`
* Better error messages
* Fix some typo
* Reorganise the repo

## 0.12-beta (2023-01-18)
* Update way to call module functions/constants (only with python-written ones)
  * Now, if you want to access to function `asin` of module `math`, **you have to type `math.asin`** instead of `math_asin`.
* `shell.py` or built `shell.exe` or `shell` is now launchable from everywhere in the system, without any error
* You can now, if you are under Linux and that you install the `readline` module, browse in the command history using arrow keys in the shell
* Several bug fixes
* [TECHNICAL] Added attributes to values

## 0.11-alpha (2023-01-06)
* Add `round` builtin func
* Fix lot of bugs
* Finish `test_file.noug` and `__test__` builtin func
* Add [`CONTRIBUTING.md`](CONTRIBUTING.md)

> [!Important]
> Nougaro now requires PYTHON 3.10 (or 3.11)! Consider download it from your favourite package manager or from [the official Python website](https://python.org/downloads)

## 0.10-alpha (2022-11-28)
### Syntax
* add `var foo, bar = a, b` (and also `var foo, bar = bar, foo`)
* add `id ? id ? expr`
* add `for e in "str"`
* add `NUMeNUM` and `NUMe-NUM`
* `12_345` is now interpreted as `12345` (cool thing ^^)
* add `0b`, `0o` and `0x`
* add `*any_expr` in lists and function calls if `any_expr` is a list
* `write "foo" >> "<newfile>"` will now create the file

### Libs and debug
* add a new lib system (see Wiki if you want to write one ^^)
* add `hello` lib
* add `debug` lib
* add config folder and debug mode:

### Builtins
* add `ord` and `chr` builtin functions

### Misc
* better error messages
* fix a lot of bugs

## 0.9-alpha (2022-10-05)

* All code is now commented
* A few bugs fixed
* Some features added
  * `int("null")` now returns 0
  * add `__python_version__`
  * `len` now calculates the length of a string
  * add `__is_keyword__` builtin function
  * add `__is_valid_token_type__` builtin function
  * add `math_log` and `math_log2` functions in `math` module
  * `pop(list)` now pops the last element of the list
  * add `__test__` builtin function
  * .5 is now parsed as 0.5

## 0.8.1-alpha (2022-05-24)

* add `assert`
* add `example` builtin function
* add `ppap` example
* increase speed of `max` and `min` builtin functions
* fix bugs (like #5)

## 0.8-alpha (2022-05-17)

* add 'time' module
* add 'statistics' module
* better error messages
* renamed `noug_version`, `os_name`, `os_release`, `os_version` to `__noug_version__`, `__os_name__`, `__os_release__`, `__os_version__`
* add `__symbol_table__` and `__base_value__`
* (change in python source code) add py2noug
* (change in python source code) add draft for attributes
* (source code downloads only) add build.bat

## 0.7-alpha (2022-05-11)

* add `read` and `write` keywords
* add the "do while" loop (`do ... then loop while ...`)
* add `replace` builtin function
* add `===`, `<==`, `<<=`, `>==`, `>>=`
* add `TypeError` that replace some `RunTimeError`s
* add `KeyboardInterrupt` instead of the python traceback when KeyboardInterrupt
* Single-line `for` statement now accepts `break` and `continue`

## 0.6-alpha (2022-05-02)

### Builtin functions
* Add `insert` builtin function
* Add `split` builtin function

### Technical
* Add `is_int` and `is_float` methods in `src.values.basevalues.Number`
* Better import system
* add `__actual_context__` and `__exec_from__`.

## 0.5-alpha (2022-04-09)
Better error messages, usage of `_` as identifier now legal, new `input_num` builtin func.

## 0.4-alpha (2022-04-05)

* Add modules
  * Add `math` module with builtin math functions and constants
  * Add `random` module with some awesome random functions like `randint`, `random`, or `choice` !!
* Better error message
* Huge bug fixes
* Random tweaks and fixes

## 0.3-alpha (2022-03-31)

* Update README and highlight theme
* Add `os_name`, `os_release` and `os_version` constants (read the Wiki for more info)
* `extend` builtin function can now delete duplicates (read the Wiki for more info)
* first argument of `print` and `print_ret` builtin functions is no longer required (e.g. `print()` is like `print('')`)
* Add special `*[...]` syntax. More infos in the Wiki, in [functions](https://github.com/jd-develop/nougaro/wiki/Functions) and [lists](https://github.com/jd-develop/nougaro/wiki/Lists).
* Better error messages
* Bug fixes

## 0.2-alpha (2022-03-23)

Bug fixes, better error messages, new `id ? id` syntax, `upper` and `lower` builtin functions and system calls (`system_call` builtin function).

## 0.1-alpha (2022-03-21)

Bug fixes.

## prototype-2 (2022-03-19)

New operators and some fixes.

## prototype-1 (2022-03-17)

The first version of the Nougaro programming language.
