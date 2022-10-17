# How Nougaro works internally ?
 Wow, what a question. We are going to explain you. Keep calm and read ;)
 
# The simple explanation
## Lexer, parser, interpreter
 When you enter something in the shell, or that you run a nougaro file, the code always pass into these three steps: [lexer](#Lexer), [parser](#Parser), [interpreter](#Interpreter).

### Lexer
 Firsts things first, the [lexer](src/lexer.py) converts your plain text code into [tokens](src/token_types.py). Tokens (in French: "lexèmes") are like lexical units, such as a '+', a keyword like 'import' or an identifier.

 For example, the line `while a != 10 then var a += 1` is translated by the lexer to this list of tokens :

    keyword:while, identifier:a, !=, int:10, keyword:then, keyword:var, identifier:a, +=, int:1, end of file

 The list of the token types in this example is:

    KEYWORD, IDENTIFIER, NE, INT, KEYWORD, KEYWORD, IDENTIFIER, PLUSEQ, INT, EOF

 The lexer uses the [position class](src/position.py) to do not lose itself in the raw code.

### Parser
 After the lexer, the [parser](src/parser.py) converts the tokens into [nodes](src/nodes.py), following some [grammar rules](grammar.txt). Nodes are bigger parts of the code, such as function definitions or binary operators.

 The lexer return a [parse result](src/parse_result.py) where the main node of the file is stored, along with errors that may have occurred.

 Let's take the tokens from the previous example and put them into the parser. We get this:

    list:([(bin_op_comp:(while:(bin_op_comp:(var_access:([identifier:a]), !=, num:int:10) then:var_assign:([identifier:a] += [bin_op_comp:(num:int:1)]))), False)])

 Ouch... Let's organise this mess to explain it easier.

    list:(
      [(
         bin_op_comp:(
            while:(
               bin_op_comp:(
                  var_access:([identifier:a]),
                  !=,
                  num:int:10
               ) 
            then:
               var_assign:(
                  [identifier:a] += [bin_op_comp:(num:int:1)]
               )
            )
         ), False
      )]
    )

 First, we have a `ListNode`. It contains only one other node, but if the code to execute had more lines, there would be more nodes.

 Then, we have some `BinOpCompNode`s. Please don't mind them.
 
 The node inside the `ListNode` is a `WhileNode` that is split into two parts: the `while` part including the condition, and the `then` part containing the body.

 The condition is a `BinOpNode`: `var_access:([identifier:a]), !=, num:int:10`: first we have a `VarAccessNode`, with the identifier `a`. It means that user wants to access to the value of the variable `a`. Then, there is a NE (not equal) token, and, finally, a `NumberNode` with an INT (int) token, with a value of 10. So we have our `a != 10` condition from the line!

 After the `then`, we have the "body node". Here, the body node is just a `VarAssignNode`, that contains the identifier (`a`), the PLUSEQ (+=) token, and then a NumberNode with an INT (int) token. So here again we have our `var a += 1` from the example line!

### Interpreter

 The [interpreter](src/interpreter.py) (AKA runtime) take the nodes as entry and return a [run-time result](src/runtime_result.py). In our case, the `WhileNode` will be 'visited', and will return (if a=1) `[2, 3, 4, 5, 6, 7, 8, 9, 10]`. The variable `a` will be updated to 10.

#### Context
 The [context](src/context.py) contain a lot of useful thing for the interpreter, such as the `display_name` (name of the function), or the [**Symbol Table**](src/symbol_table.py).

##### Variables and symbol tables
 The interpreter store all the variables in the Symbol Table. This is a table, with the name of the variables on one side and the values on the other side. This looks like that:
   
    {
       "parent": None,
       "symbols": {
          "a": 10,
          "builtin_function": <built-in function "built-in function">,
       }
    }


# More details about some steps/files
## [`shell.py`](shell.py) and [`src/nougaro.py`](src/nougaro.py)
 When you execute some code in the shell or from a file, the code starts to travel into all the other files from `shell.py` (below: "The shell").

 The shell have some main and important roles: check if the file exist, send the code to `src/nougaro.py` and print errors in red if there are some.

 `src/nougaro.py` have also important roles: it sets the symbol table by calling the function in [src/set_symbol_table.py](src/set_symbol_table.py), it sends the code to the lexer, the parser and then the interpreter, by checking at every step if there is any error to return to The shell.

# You don't find what you're looking for?
 Open an [issue](https://github.com/jd-develop/nougaro/issues/new/choose)
 If you can not open an issue, consider [emailing me](mailto://jd-dev@laposte.net), so I can update this file :) (You can also send me a Discord message, if you have my discord)
