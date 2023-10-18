# TODO list
<!-- check mark character: ✅ -->

## ✅ 0.15 beta (goal: october 20th, 2023)
__Release date: october 14th, 2023__
* [X] add `var id.attr = value` (finished 4/10/23)
* [X] fix bug where `this` is not defined in classes (finished 6/10/23)
* [X] fix bug where methods are of type `functions` (finished 6/10/23)
* [X] fix bug where global vars are not accessible in methods (finished 6/10/23)
* [X] add class inheritance (finished 11/10/23, fixed 14/10/23)
* [X] add an error when things like `math.(assert 1)` (finished 3/10/23)
* [X] add `time.time()` (finished 3/10/23)

## 0.16.0 beta (goal: november 2023)
* [X] add '\xXX' and '\uXXXX' support (finished 6/10/23)
* [X] add '\UXXXXXXXX' (finished 8/10/23)
* [X] add '\N{UNICODE CHARACTER NAME}' (finished 8/10/23)
* [X] add `startswith` and `endswith` (finished 10/10/23)
* [ ] add possibility to import files in current folder and sub-folders
  * [X] Syntax: (update parser)
    * `import file` if file is in current directory
    * `import dir.file` if dir is in current directory and file is in dir
  * [X] Update ImportNode
  * [ ] Runtime:
    * [ ] Get the directory of the main file which is executed or imported
    * [ ] Resolve all the imports depending on this directory
* [X] add `var++`, and `var--` (finished 17/10/23)
* [ ] add possibility to read command line arguments
* [ ] add optional arguments in functions
* [X] switch to semantic versioning (finished 16/10/23)

## 0.17.0 beta (goal: february 2024)
* [X] add `import ... as ...` (finished 16/10/23)
* [ ] rewrite parser to make it faster and easier to read
* [ ] do all the TODOs in the code (with the pretty good PyCharm 'TODO' tab)
* [ ] add builtin classes
* [ ] add `try catch`
* [ ] add `raise`
* [ ] add `assert ... crashes (on Error) (with message "...")`

## 0.18.0 beta (goal: may 2024)
* [ ] add `tkinter`
* [ ] add `turtle`
* [ ] add `socket`
* [ ] add `requests`
* [ ] add `webbrowser`
* [X] add `unicodedata` (finished 9/10/23)

## 0.19.0 beta (goal: july 2024)
* [ ] add unit tests
* [ ] add complex numbers

## 1.0.0 release candidate (goal: october 2024)
* [ ] create highlight extension for VSCode
* [ ] if possible, implement `break (name)` and `continue (name)` where (name) is `if`, `for`, …
* [ ] completely switch to semver
