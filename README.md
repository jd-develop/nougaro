# Nougaro

[Français](README.fr.md)

![Nougaro. A programming Language.](repo-image/repo-image.png)

This is Nougaro version `1.1.0`.

Nougaro is a programming language interpreted in Python.

It is a multi-paradigm programming language that supports imperative, functional and object-oriented programming.

Nougaro is weakly typed. Its syntax is inspired from Python and Basic.

## Example
```nougaro
def fizzbuzz(n)
    for i = 0 to n then
        if i%15 == 0 then print("FizzBuzz") \
        elif i%3 == 0 then print("Fizz") \
        elif i%5 == 0 then print("Buzz") \
        else print(i)
    end
end
```

## Run

 Execute the shell with `python3 shell.py`. Open files with `python3 shell.py filename.extension`.
 Generally, we use `.noug` as extension for Nougaro files.

 The code is compiled for Windows and GNU/Linux. Check it out in the [releases](https://github.com/jd-develop/nougaro/releases/) tab!

 Supports Python 3.11 and 3.12. Has not been tested under python 3.13.

### Third-party modules (optional)

 Python builtins that are not always builtin:

* `colorama` (`pip install colorama`)

 Under GNU/Linux, to allow browsing command history with the arrow keys, and to
 save the command history across sessions:

* `readline` (`pip install readline`)

## Documentation

 The documentation is available [here](https://nougaro.github.io/documentation).

## About syntax highlighting

 The notepad++ file was no longer updated, so I deleted it from the repo. Here is [its last version](https://github.com/jd-develop/nougaro/blob/973303409d2f7a91d1b45e44f57ebdb517abde53/highlight%20theme%20for%20NPP.xml).

 I’m planning to create a [VSCode extension](https://github.com/jd-develop/nougaro-highlight-theme) – if you know something about that, contact me!

## How it works?

 Everything is explained [here](how_it_works.md) :)

## Language goals

 The main goal of this language is, for me, to learn how interpreted languages work. It is not intended
 to be blazing fast, memory safe and bleeding edge, but to be easily understandable.

> [!Important]
> I do *not* recommend to use Nougaro in real projects.

## Acknowledgements

 Thanks to [Mistera](https://github.com/mistera91) who episodically contributes.

 Thanks to [3fxcf9](https://github.com/3fxcf9) for the [repository banner](repo-image/repo-image.png).
