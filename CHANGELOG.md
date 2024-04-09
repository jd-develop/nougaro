# Changelog

This file is updated nearly every commit and copied to GH release changelog.

Since 0.19.0-beta, we try using [this changelog format](https://keepachangelog.com). It consists of 6 sections, titled `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. The Nougaro changelog has another section, `Calculator`, keeping track of the changes relative to the Nougaro Calculator under the same 6-sections format.

## 0.19.0-beta (Unreleased)

### Added

* Add a “meta” system
  * Using the syntax `@meta metaName` or `@meta metaName metaValue` at the beginnig of a file, you can now enable special features
* Add `legacyAbs` meta
  * No value required
  * It makes the legacy absolute value possible: `|-1|`=`1`
  * However, it makes bitwise or not accessible.
* Add `nbspBetweenFrenchGuillemets` meta
  * No value required
  * Experience the true french pain! (and I don’t talk about baguettes…) If you want to use the french string quotes (`«»`), you will have to put a no-break space (or a narrow no-break space) after the `«` and before the other `»`. Those (N)NBSP will not be counted in the string.
* Data version and version id can now be known using `__data_version__` and `__version_id__`.
* Data version is now stored in `./noug_version.json`
* `(Internal API)` Noug version can now be retrieved using `src.noug_version` library. It consists of 8 constants: `MAJOR`, `MINOR`, `PATCH`, `PHASE`, `PHASE_MINOR`, `VERSION` (`str`), `VERSION_ID`, `DATA_VERSION`.
* `(Build scripts)` It is now possible to use a custom python command in `build.sh` by passing the command as parameter. Note that I forgot to mention that this is possible with `run_tests.sh` since 0.18.0-beta.

### Changed

* Moved `./config/noug_version.json` to `./noug_version.json`
* Data version has been increased to 5

### Fixed

* Fix typos
* Fix a bug where files were referred as `<stdin>` in the shell (and therefore in error messages, etc.)

### Calculator
#### Removed
* Remove the possibility to print i with `pi` (it is now possible to get the value of π outside of an operation)

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
