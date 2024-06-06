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
* [X] fix the fact that Nougaro doesn't crash with an error code when there is an error

## ✅ 0.17.0 beta (goal: no goal, this is a crash-fixing version)

### Release date: January 19th, 2024

## ✅ 0.18.0 beta (goal: February 2024)

### Release date: March 16th, 2024

* [X] add `import ... as ...` (finished 16/10/2023)
* [X] rewrite shell.py CLI args with `argparse` (finished 22/01/2024)

## ✅ 0.19.0 beta (goal: no goal)

### Release date: May 8th, 2024

* [X] add `webbrowser` (finished 24/04/2024)
* [X] add `unicodedata` (finished 9/10/2023)
* [X] move config files to `~/.config` under Linux and BSD, `~/Library/Preferences` under macOS, and `%appdata%` under Windaube. [QT documentation about where config files should be stored.](https://doc.qt.io/qt-6/qsettings.html#platform-specific-notes) (finished 10/03/2024, testing completed 11/03/2024)
* [X] rewrite parser to make it faster and easier to read (finished 30/04/2024)

## ✅ 0.20.0 beta (goal: June 8th, 2024)

### Release date: June 6th, 2024

* [X] ~~add `continue and append (value)`~~ (completed as no longer planned on 14/05/2024)
* [X] add `-i` cli arg to execute a file then run a shell within it (finished 08/05/2024)

## 1.0.0 release candidate (goal: September 2024)

* [X] if possible, implement `break (name)` and `continue (name)` where (name) is `if`, `for`, … (finished 09/05/2024)
* [X] completely switch to [semver](https://semver.org) (finished 7/11/2023)

* [ ] Add expected type in data Nougaro stores (conffiles)
* [ ] create highlight extension for VSCode
* [ ] add optional arguments in functions
  * [ ] Parser:
    * [ ] Allow optional parameters, do not allow positional parameters after them (call + def)
    * [X] Update nodes (call + def) (finished 24/02/2024)
  * [ ] Runtime:
    * [X] Update Function value and methods (finished 28/05/2024)
      * [X] Check args (finished 27/05/2024)
      * [X] Populate args (finished 28/05/2024)
    * [ ] Update Interpreter visit methods

## Future releases

* [ ] add `turtle`
* [ ] add `socket`
* [ ] add `requests`
* [ ] add `tkinter`
* [ ] add unit tests
* [ ] add complex numbers
* [ ] do all the TODOs in the code (with the pretty good PyCharm 'TODO' tab)
* [ ] add builtin classes, or find a way to have builtin-methods in Values.
* [ ] add `try catch`
* [ ] add `raise`
* [ ] add `assert ... crashes (on Error) (with message "...")`
* [X] eventually remove protected variables (finished 20/01/2024)
