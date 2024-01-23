# Changelog

This file is updated nearly every commit and copied to GH release changelog.

## 0.18.0-beta
* Remove `PROTECTED_VARS`, which means that variables can now use builtin names as identifiers.
* Add `path_exists(path)` builtin function
* Add miracle sort
* Add more tests
* Better error messages
* Rewrite argument handling in `shell.py` using `argparse` (arguments have changed, use `(nougaro) -h` to view the new arguments)
* Change repo image
* Fix a crash in `math.log`
* `list(list_value)` now returns an unlinked copy of the original list

### Calculator
* Now, the stack is kept at the end of a command. You can make computations using multiple commands, like in Unix’ `dc`.
  Note that if there is an error, the stack is left unchanged.
* Add a bunch of debugging commands (such as `printi`, `prints`, `resets`, `rsi`, …) and aliases for existing commands (such as `quit`).
* Add logarithm
* Better error messages

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
