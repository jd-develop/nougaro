# Contribute

Hello! If you're here, I assume you want to contribute to the Nougaro programming language. If you do, thank you ^^

## Table of contents

* [Table of contents](#table-of-contents)
* [Code of conduct](#code-of-conduct)
* [What should I know before I get started?](#what-should-i-know-before-i-get-started)
* [How can I contribute?](#how-can-i-contribute)
  * [Bug report / feature request](#bug-report--feature-request)
  * [Pull requests](#pull-requests)
* [Styleguides](#styleguides)
  * [Code](#code)
  * [Git Commit Messages](#git-commit-messages)
* [Thank you + questions](#thank-you)

## Code of conduct

The project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code.
Please report unacceptable behavior by [mail](mailto:jd-develop@laposte.net).

## What should I know before I get started?

Nougaro is a high-level object-oriented programming language interpreted in Python.
To understand my code, you can first read [this file](how_it_works.md), then read the comments of the code files.

### Repository structure

```
File or directory               Brief explaination
/                               Repository root
|- .github/                     Files related to GitHub (issues, actions…)
|- examples/                    Examples (.noug files)
|- lib_/                        Libraries (importable using import (...),
|  |                              which imports either (...).noug or (...)_.py)
|  |- lib_to_make_libs.py       This file is the "base file" to make libs in
|  |                              Python
|- src/                         Directory containing every other source code
|  |                              file (except for shell.py)
|  |- errors/                           
|  |  |- errors.py              Source code for nougaro errors
|  |  |- strings_with_arrows.py
|  |  |                         This file generates the '^^^^^' under the
|  |  |                           problematic line in error msgs, using
|  |  |                           position start and position end
|  |- lexer/                    Every file related to the Lexer
|  |  |- lexer.py               Source code for the Lexer
|  |  |- position.py            Class that stores the position in a file
|  |  |                           (index, line number, column)
|  |  |- token_types.py         File containing different constants such as TT
|  |  |                           (Token Types)
|  |  |- token.py               The Token class
|  |- parser/                   Every file related to the Parser
|  |  |- grammar.txt            Explicitation of the syntax — not actually a
|  |  |                           file that Nougaro uses, more a "documenta-
|  |  |                           tion" file
|  |  |- nodes.py               Every node (the parent Node class and every
|  |  |                           other nodes)
|  |  |- parse_result.py        Result of parsing (notably contains the error
|  |  |                           and position)
|  |  |- parser.py              Source code for the Parser
|  |- runtime/                    Every file related to the Interpreter (and
|  |  |                           runtime)
|  |  |- values/                Source code for Values
|  |  |  |- basevalues/         Source code for Values except functions
|  |  |  |  |- basevalues.py    Base values (except functions and the parent
|  |  |  |  |                     Value class)
|  |  |  |  |- value.py         Parent Value class for all values
|  |  |  |- functions/          Source code for Functions
|  |  |  |  |- base_builtin_func.py
|  |  |  |  |                   Parent class of all built-in functions. The
|  |  |  |  |                     actual built-in functions are stored in
|  |  |  |  |                     builtin_function.py.
|  |  |  |  |- base_function.py
|  |  |  |  |                   Parent class of all functions.
|  |  |  |  |- builtin_function.py
|  |  |  |  |                   Behaviour of built-in functions (such as print,
|  |  |  |  |                     input, etc.)
|  |  |  |  |- function.py      The Function class a user can instantiate using
|  |  |  |  |                   def.
|  |  |  |- tools/
|  |  |  |  |- is_type.py       To check if a Value is of a certain type
|  |  |  |  |- py2noug.py       Converts Nougaro values to Python values and
|  |  |  |  |                     vice-versa.
|  |  |  |- number_constants.py
|  |  |  |                      The definition of True, False and null
|  |  |- context.py             The Context class, that stores the current
|  |  |                           scope’s name, symbol table, and so on.
|  |  |- interpreter.py         Source code for the Interpreter
|  |  |- runtime_result.py      The Runtime Result class, that stores the
|  |  |                           current error, or if the function should
|  |  |                           return or the loop break, etc.
|  |  |- set_symbol_table.py    Sets the symbol table to its default value
|  |  |                           (with all the built-in functions and names)
|  |  |- symbol_table.py        Source code for the Symbol Table (kind of a
|  |  |                           dictionnary with all the variables)
|  |- constants.py              Some constants, such as DIGITS ("0123456789"),
|  |                              or valid characters for an identifier.
|  |- misc.py                   Miscellaneous stuff
|  |- nougaro.py                Described in how_it_works.md
|- tests/                       Directory containing files to test Nougaro
|  |- lib_tests/, lib_test.noug, test_import_in_current_dir.noug
|  |                            Files used to test to import nougaro libs that
|  |                              are inside the current directory
|  |- test_file.noug            File used to test nougaro. It is written in
|  |                              nougaro
|  |- *.py                      Unit tests
|- build.bat                    Compiles the project to .exe
|- build.sh                     Compiles the project to GNU/Linux binary
|- changelog.md                 Changelog
|- example.noug                 Run with example()
|- how_it_works.md              This file explains how Nougaro works
|- noug_version.json            Stores the Nougaro version
|- run_tests.sh                 This file runs tests
|- shell.py                     Base file of the project
|- todo.md                      A todo-list
```

## How can I contribute?

### Bug report / feature request

In order to report bugs or to request features, please open an [issue](https://jd-develop.github.io/nougaro/bugreport.html).
Please follow the template of the issue.

### Pull requests

If you change directly the code, you can commit it in a fork of the Nougaro language then open a [Pull request](https://github.com/jd-develop/nougaro/pulls).
Please follow the [styleguides](#code)

## Styleguides

### Code

The Python code follows the [PEP8](https://pep8.org/) convention.
Summary of the PEP8:

* 4 spaces and not tabs
* mixedCase for global variables and lowercase_underscore for local variables, CamelCase for classes.
* comments: `code  # comment` or `# comment` and not `code#commment` (erk) nor `code # comment` (ouch) nor `#comment` (ugly)
* no spaces before and after `()` `[]` `{}`
* add ALWAYS a space after a comma, except before a closing parenthesis, and after a semicolon and a colon (except for the slice operator). Example : `def foo(): return bar` OK, but `def foo():return bar` is bad. However, `list[2:3]` is OK.
* only ONE SPACE before and after `=` in an ASSIGNMENT (but no space for a default param value EXCEPT when you specify the type of the value) (but NO SPACE between the ARG name and the ARG value)
* ALWAYS add ONE (single) NEW LINE at the end of your file
* Never use the characters `l` (lowercase letter el), `O` (uppercase letter oh), or `I` (uppercase letter eye) as single character variable names.
* `not ... is ...` -> `... is not ...`
* `not ... == ...` -> `... != ...`
* `except ...` and `except BaseException` -> `except Exception`
* `return` -> `return None`
* `if ... == True` -> `if ...`
* etc.

I recommend reading the full PEP8, however you can just read the examples.
<!-- If you're not sure, you can use the tool of the PyCharm IDE that checks your code while you're typing it. -->

The Nougaro code should be great to read: you can follow the PEP8 here too, as the Nougaro syntax is not too different to the Python one.

### Git Commit Messages

* Write your messages in English.
* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 50 characters or fewer.
* If you number your commits, DO NOT use the <&nbsp;#&nbsp;> character, as it is used in GitHub.

Remember that your commit message should always fit in the sentence “This commit will ‘…’.”

## Thank you!

I’m glad you’ve read until here, and I hope you will help us to build the Nougaro programming language!
If you have any question, please consider asking the community in the [GitHub discussions](https://github.com/jd-develop/nougaro/discussions), we will be happy to help you!
