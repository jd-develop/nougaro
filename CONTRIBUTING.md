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

I recommend you reading the full PEP8, however you can just read the examples.
If you're not sure, you can use the tool of the PyCharm IDE that checks your code while you're typing it.

The nougaro code should be great to read: you can follow the PEP8 here too, as the Nougaro syntax is not too different to the Python one.

### Git Commit Messages
* Write your messages in english.
* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 50 characters or fewer.
* If you number your commits, DO NOT use the <&nbsp;#&nbsp;> character, as it is used in GitHub.


## Thank you!
I'm glad you read until here, and I hope you will help us to build the Nougaro programming language!
If you have any question, please consider asking the community in the [GitHub discussions](https://github.com/jd-develop/nougaro/discussions), we will be happy to help you!
