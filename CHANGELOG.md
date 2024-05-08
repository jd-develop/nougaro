# Changelog

This file is updated nearly every commit and copied to GH release changelog.

Since 0.19.0-beta, we try using [this changelog format](https://keepachangelog.com). It consists of 6 sections, titled `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. The Nougaro changelog has another section, `Calculator`, keeping track of the changes relative to the Nougaro Calculator under the same 6-sections format.

## 0.19.0-beta

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
        If `autoraise` is True, the window is raised if possible (note that under many window managers this will occur
        regardless of the setting of this variable).

#### Metas
* Add a “meta” system
  * Using the syntax `@meta metaName` or `@meta metaName metaValue` at the beginnig of a file, you can now enable special features
  * As predicate, you can use `@`, `#@`, `%@`, `@@`, `-@` or `$@`.
* Add `legacyAbs` meta
  * No value required
  * It makes the legacy absolute value possible: `|-1|`=`1`
  * However, it makes bitwise or not accessible.
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

## 0.18.0-beta
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
* Moved config files to the right directory depending on the OS (such as `~/.config`). More infos in the docstring of the src.conffiles file.
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

## 0.17.0-beta

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

## 0.16.0-beta

### Syntax

* Add `var ... ++` and `var ... --`

### Loops

* Loops now append `None` to their result even if the node is `None`, not printable, or if the loop is broke or continued.

### Modules

#### Import and export

* Add `import ... as ...`
* You can now import nougaro files from current folder and sub-folders.
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
