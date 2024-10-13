# How does Nougaro work internally ?

## The simple explanation

### Lexer, parser, interpreter

 When you enter something in the shell, or that you run a nougaro file, the code always pass into these three steps: [lexer](#lexer), [parser](#parser), [interpreter](#interpreter).

#### Lexer

 Firsts things first, the [lexer](src/lexer/lexer.py) converts your plain text code into [tokens](src/lexer/token.py). Tokens (in French: «&nbsp;lexèmes&nbsp;») are like lexical units, such as a '+', a keyword like 'import' or an identifier.

 For example, the line `while a != 10 then var a += 1` is translated by the lexer to this list of tokens :

    keyword:while, identifier:a, !=, int:10, keyword:then, keyword:var, identifier:a, +=, int:1, end of file

 The list of the [token types](src/lexer/token_types.py) in this example is:

    KEYWORD, IDENTIFIER, NE, INT, KEYWORD, KEYWORD, IDENTIFIER, PLUSEQ, INT, EOF

 The lexer uses the [position class](src/lexer/position.py) to not lose itself in the raw code. Each token has a start and an end position.

#### Parser

 After the lexer, the [parser](src/parser/parser.py) converts the tokens into an abstract syntax tree composed of [nodes](src/parser/nodes.py), following some [grammar rules](src/parser/grammar.txt). Nodes are bigger parts of the code, such as function definitions or binary operators.

 The lexer return a [parse result](src/parser/parse_result.py) where the main node of the file is stored, along with errors that may have occurred.

 Let's take the tokens from the previous example and put them into the parser. We get this:

    list:[(while:(bin_op_comp:([var_access:[identifier:"a"]], !=, [num:int:10]) then:var_assign:([[identifier:"a"]] += [num:int:1])), False)]

 Ouch… Let's organize this mess to explain it easier.

    list:[
       (
          while:(
             bin_op_comp:(
                [var_access:[identifier:"a"]],
                !=,
                [num:int:10]
             )
          then:
             var_assign:(
                [[identifier:"a"]] += [num:int:1]
             )
          ), False
       )
    ]

 First, we have a `ListNode`. It contains only one other node, but if the code to execute had more lines, there would be more nodes. Every pased file or line of input is inside a `ListNode`.

 The node inside the `ListNode` is a `WhileNode` that is split into two parts: the `while` part including the condition, and the `then` part containing the body.

 The condition is a `BinOpCompNode`: `var_access:[identifier:"a"], !=, num:int:10`. It is a `BinOpCOMPNode` because it is a comparison. First, we have a `VarAccessNode`, with the identifier `a`: it means that the user wants to access to the value of the variable `a`. Then, there is a NE (not equal) token, and, finally, a `NumberNode` with an INT (int) token, with a value of 10. So we have our `a != 10` condition from the line!

 After the `then`, we have the “body node”. Here, the body node is just a `VarAssignNode`, that contains the identifier (`a`), the PLUSEQ (+=) token, and then a NumberNode with an INT (int) token. So here again we have our `var a += 1` from the example line!

#### Interpreter

 The [interpreter](src/runtime/interpreter.py) (AKA runtime) take the nodes as entry and return a [run-time result](src/runtime/runtime_result.py). In our case, the `WhileNode` will be 'visited', and will return (if a=1) `[2, 3, 4, 5, 6, 7, 8, 9, 10]`. The variable `a` will be updated to 10. It uses a contex to store useful information.

##### Context

 The [context](src/runtime/context.py) contain a lot of useful thing for the interpreter, such as the `display_name` (name of the function), booleans to store whether or not it should break or continue the loop, or which value to return in the function… It also stores the [**Symbol Table**](src/runtime/symbol_table.py).

###### Variables and symbol tables

 The interpreter stores all the variables in the Symbol Table. This is a dictionnary, with the name of the variables as the keys and the values as the, well, values. It looks like that:

    {
       "parent": None,
       "symbols": {
          "a": 10,
          "some_builtin_function": <built-in function "some_builtin_function">,
          "another_variable": value
       }
    }

When the Interpreter wants to create a variable, it creates an entry in the symbol table of the current Context. If it
wants to access a variable, it checks in the symbol table of the current Context, but also in its parent, and its
parent’s parent, etc.

>[!Note]
> The only case where it doesn’t look into the parent symbol table is in built-in functions,
> because otherwise if an optional parameter is not given but the user already have a variable with the same name, the
> interpreter will look to this variable (see issue [#10](https://github.com/jd-develop/nougaro/issues/10)). By the way,
> this is why it is recommended in [this doc page](https://nougaro.github.io/documentation/1.0/Expanding/Write-libs/#get-arguments)
> to use the `getf` method of symbol table in built-in functions (see the difference in the code between `get` and `getf`).

The symbol table is set to its default value at the beginning of the execution of a program, using [this file](src/runtime/set_symbol_table.py)

## More details about some steps/files

### [`shell.py`](shell.py) and [`src/nougaro.py`](src/nougaro.py)

 When you execute some code in the shell or from a file, the code starts to travel into all the other files from `shell.py` (below: “The shell”).

 The shell have some main and important roles: check if the file exist, send the code to `src/nougaro.py` and print errors in red if there are some.

 `src/nougaro.py` have also important roles: it sets the symbol table by calling the function in [src/set_symbol_table.py](src/runtime/set_symbol_table.py), it sends the code to the lexer, the parser and then the interpreter, by checking at every step if there is any error to return to The shell.

## You don't find what you're looking for?

 Open an [issue](https://github.com/jd-develop/nougaro/issues/new/choose).

 If you can not open an issue, consider [emailing me](mailto://jd-dev@laposte.net), so I can update this file :) (You can also send me a Discord message, if you have my discord)
