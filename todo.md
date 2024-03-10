# TODO list
<!-- check mark character: ✅ -->

## ✅ 0.15 beta (goal: October 20th, 2023)

### Release date: October 14th, 2023

* [X] add `var id.attr = value` (finished 4/10/23)
* [X] fix bug where `this` is not defined in classes (finished 6/10/23)
* [X] fix bug where methods are of type `functions` (finished 6/10/23)
* [X] fix bug where global vars are not accessible in methods (finished 6/10/23)
* [X] add class inheritance (finished 11/10/23, fixed 14/10/23)
* [X] add an error when things like `math.(assert 1)` (finished 3/10/23)
* [X] add `time.time()` (finished 3/10/23)

## ✅ 0.16.0 beta (goal: November 26th, 2023)

### Release date: November 27th, 2023

* [X] add '\xXX' and '\uXXXX' support (finished 6/10/23)
* [X] add '\UXXXXXXXX' (finished 8/10/23)
* [X] add '\N{UNICODE CHARACTER NAME}' (finished 8/10/23)
* [X] add `startswith` and `endswith` (finished 10/10/23)
* [X] add possibility to import files in current folder and sub-folders (finished 8/11/2023)
  * [X] Syntax: (update parser) (finished 18/10/2023)
    * `import file` if file is in current directory
    * `import dir.file` if dir is in current directory and file is in dir
  * [X] Update ImportNode (finished 18/10/2023)
  * [X] Runtime:
    * [X] Get the directory of the main file which is executed or imported (finished 7/11/2023)
    * [X] Resolve all the imports depending on this directory (finished 8/11/2023)
* [X] add `var++`, and `var--` (finished 17/10/23)
* [X] Change `export` to `export (any node) as identifier` or `export identifier` (finished 2/11/2023)
* [X] add possibility to read command line arguments (finished 26/10/2023)
* [X] switch to semantic versioning (finished 16/10/23)
* [X] return None in loops, even when there is a continue of a break (finished 24/11/2023)
* [X] fix the fact that nougaro doesn't crash with an error code when there is an error

## ✅ 0.17.0 beta (goal: no goal, this is a crash-fixing version)

### Release date: January 19th, 2024

## 0.18.0 beta (goal: February 2024)

* [X] add `import ... as ...` (finished 16/10/2023)
* [X] rewrite shell.py CLI args with `argparse` (finished 22/01/2024)
* [ ] add optional arguments in functions
  * [ ] Parser:
    * [ ] Allow optional parameters, do not allow positional parameters after them (call + def)
    * [X] Update nodes (call + def) (finished 24/02/2024)
  * [ ] Runtime:
    * [ ] Update Function value and methods
    * [ ] Update Interpreter visit methods
* [ ] rewrite parser to make it faster and easier to read
* [ ] do all the TODOs in the code (with the pretty good PyCharm 'TODO' tab)
* [ ] add builtin classes, or find a way to have builtin-methods in Values.
* [ ] add `try catch`
* [ ] add `raise`
* [ ] add `assert ... crashes (on Error) (with message "...")`

## 0.19.0 beta (goal: May 2024)

* [ ] add `tkinter`
* [ ] add `webbrowser`
* [X] add `unicodedata` (finished 9/10/23)
* [X] move config files to `~/.config` under Linux and BSD, `~/Library/Preferences` under macOS, and `%appdata%` under Windaube. [QT documentation about where config files should be stored.](https://doc.qt.io/qt-6/qsettings.html#platform-specific-notes) (finished 10/03/2024, still to test under Windows)

## 0.20.0 beta (goal: July 2024)

* [ ] add unit tests
* [ ] add complex numbers
* [ ] add `-i` cli arg to execute a file then run a shell within it.

## 1.0.0 release candidate (goal: October 2024)

* [ ] create highlight extension for VSCode
* [ ] if possible, implement `break (name)` and `continue (name)` where (name) is `if`, `for`, …
* [X] completely switch to [semver](https://semver.org) (finished 7/11/2023)

## Future releases

* [ ] add `turtle`
* [ ] add `socket`
* [ ] add `requests`
* [X] eventually remove protected variables (finished 20/01/2024)
