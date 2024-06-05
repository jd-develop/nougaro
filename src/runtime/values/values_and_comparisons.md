# Comparisons between values

The goal of this file is to precisely determine the behaviour of **comparisons**, such as equals, less than or equal, etc.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL
NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and
"OPTIONAL" in this document are to be interpreted as described in
[RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

## Definitions

The following comparisons are defined:
* **equals** (`==`)
* **not equals** (`!=`)
* **less than** (`<`), and its respective equals comparison: **less than or equals** (`<=`)
* **greather than** (`>`), and its respective equals comparison: **greater than or equals** (`>=`)

## Basics

The **equals** comparison MUST NOT throw an error, except if the value involved is the Base Value, it which case it MUST throw an error. Either a value is equal to an other, either it is not, but it MUST NOT be neither of both, except if the value involved is the Base Value, in which case it MUST throw an error.

The **not equals** comparison MUST return false if **equals** returns true, and MUST return true if **equals** returns false. It MUST NOT throw an error, except if the value involved is the Base Value.

The **less than** and **greather than** MAY cause an error: those comparisons MAY be unsupported between certain types of values.

The **less than or equal** (respectively **greater than or equal**) MUST fail if **less than** (respectively **greather than**) fails. It MUST NOT depend on the failure of **equals**. It MUST NOT fail if its respective non-equal comparison does not fail, in that case it MUST return the result of the ‘or’ operation between the respective non-equal comparison and the equal comparison.

## Behaviours
### Number
A number is equal to another if they have the same value. A float SHOULD equals an integer if its decimal part equals 0 and that they have the same integer part. The Python comparison MAY be used to determine wether or not two numbers are equal.

A number is less than or greater than another nuber in the mathematical sense. A float, if SHOULD be less than or greater than a int if they are in the mathematical sense. The Python comparison MAY be used to determine wether or not a number is greater or less than another.

A number SHOULD NOT be equal to, less or greather than any other value than Number.

## String
String comparisons SHOULD be the same as in Python. Strings SHOULD NOT be equal to any other value and the GT, GTE, LT, LTE comparisons SHOULD fail between a string and any other value.

## List
Two lists SHOULD be equal if and only if they have the same length and that every element of each list are equal two by two. GT, GTE, LT, LTE comparisons SHOULD fail.

## Modules
Two modules SHOULD be equal if they have the same name. GT, GTE, LT, LTE comparisons SHOULD fail.

## Constructors
Two constructors SHOULD be equal if they have the same name, the same parent, the same attributes and the same symbol table. GT, GTE, LT, LTE comparisons SHOULD fail.

## Objects
Two objects SHOULD be equal if they have the same attributes, constructors, and types. GT, GTE, LT, LTE comparisons SHOULD fail.

## NoneValue
Two NoneValues SHOULD be equal. GT, GTE, LT, LTE comparisons SHOULD fail.

## Functions (user-written) and methods
Two Functions SHOULD be equal when their body node is equal and their parameters are equal. A one-line (arrowed) function SHOULD NOT be equal to a multi-line function. GT, GTE, LT, LTE comparisons SHOULD fail. The fact that two methods are not defined in the same object SHOULD NOT affect their equality.

## BuiltinFunctions and ModuleFunctions
Two Builtin/Module functions SHOULD be equal when their name and their type is equal. Their type is defined as their module name or `BuiltinFunction` if not in a module. GT, GTE, LT, LTE comparisons SHOULD fail.
