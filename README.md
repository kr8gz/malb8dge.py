# Introduction
malb8dge (thanks bombie) is ANOTHER programming language made by kr8gz who
doesn't know how to make programming languages.

The main goal of the language is to shorten code by removing words wherever
possible, while still keeping it somewhat easy to read and understand.

# Documentation

## Running a malb8dge program
Run `py <location of malb8dge file> <location of .mlb8 file>`
in the command prompt to run a malb8dge script.

## Structure

### Values
Values are the smallest elements in malb8dge. They can be one of the following:

* Literals (strings, integers, floats)
* Lists in brackets
* Parenthesized expressions
* Identifiers (variables, true/false, null)

Values may be preceded by one or more *before operators* and/or followed by one
or more of each of the following:

* a function call
* list indexing
* "brace syntax"
* "replace syntax"

More on each of them later.

Examples:
```
;"Hello World!"
^#-16777216
(2.718281828 > 3.1415926535)
`["a", 4, false]^^
?null
doStuff(x, y // 3, z)
```

### Expressions
Normally, an expression is something that can be evaluated to return a value.
This definition does not really fit malb8dge expressions very well, since some
operators act more like statements (but still return a value).

malb8dge expressions consist of one or more values chained together with
*binary operators*.

Examples:
```
3 + 4 + 5
3.1415926535 > 2.718281828
.._ & ?#$
x = 6 * y % 7
z //= 10
/"Hello", "World!"
```

### Statements
A statement is basically a piece of code that does something. In malb8dge,
a statement can be one of the following things:

* an expression
* a break statement - `%x` with optional expression x (only in loops)
* a continue statement - `>x` with optional expression x (only in loops)
* a return statement - `<x` with optional expression x (only in functions)
* an exit statement - `%%` (stops the program)

### Blocks
Blocks are the biggest element in malb8dge. They consist of multiple statements
in braces `{...}` or a single statement after a colon (`:`) which is sometimes
optional. On the global level, neither the braces nor the colon are required.

Blocks are required for:

* If-statements (colon optional)
* While loops (colon optional)
* For loops
* Functions (colon optional as the definition of a function already requires a
  colon)

Examples:
```
add = (x, y) : x + y  ############# simple block with one statement

multiply = (x, y) : {  ############ block start
    ;"Multiplying {x} by {y}!"
    x * y
}  ################################ block end

3 > 2 ? ;"3 is greater than 2"  ### colon not required for if-statements
```

### Comments
Comments are ignored by the compiler, allowing you to explain your ugly code.
In malb8dge, there are only single line comments. Comments start with `###`.

## Data Types
```
str    = "Hello World!"
int    = 16777215
float  = 3.1415926535
bool   = true
list   = "a", 4, false
null
```
Lists can be created with square brackets (`[]`) or without any brackets.
*(A list in parentheses (`()`) will be treated as a parenthesized expression.
It's pretty much the same thing though)*

## Operators
I'm just going to dive straight into this, since it's the main part of the
programming language. Basically everything you know from Python or other
languages has its own "operator" in malb8dge.

The result of trying to keep malb8dge code relatively easy to type (unlike
other esolangs, no fancy math symbols or anything similar are needed!) is that
the meaning of operators changes completely depending on their position around
a value.

### Input and output
```
;x                 ### prints x but each element is concatenated
/x                 ### prints x with spaces separating each element

_ or _(x)          ### gets input with optional prompt (x)
$ or $(x)          ### gets input as number with optional prompt (x)
#$ or #$(x)        ### splits input into a list of numbers with optional prompt (x)
```
If that sounds a little confusing, here are some examples:
```
;"Hello World!"    ### prints "Hello World!"
;1, 2, 3           ### prints "123"
/"Hello World!"    ### prints "H e l l o   W o r l d !"
/"Hello", "World!" ### prints "Hello World!"
/1, 2, 3           ### prints "1 2 3"

;_                 ### simple cat program

_("Password: ")    ### gets a string with password prompt (bad example)
#$("x, y: ")       ### gets a list of numbers (for coordinates)
```
The "get input as number" part will be explained in more detail later on.

### Numbers

### Strings

### Logic

### Miscellaneous
FAT TODO ^^^

## Function calls
These are pretty normal in malb8dge. The target function is followed by
parentheses and a list of arguments passed.

## List indexing
List indexing in malb8dge is a bit more complicated than in other languages.
There is a short form and a standard form. The short form allows for shorter
code, but reduced functionality.

Examples for short form: `list.0`, `list.x.y`, `list.1.2.3`

The standard form is what you are probably used to in other programming
languages. In malb8dge, this standard form is extended to add more
functionality to reduce the amount of operators which are needed elsewhere.

These functionalities are:
* `list[x]` normal indexing
* `list[+x]` element count
* `list[?x]` list contains element check
* `list[@x]` index of

It is also possible to mix the short form and the standard form. In some cases,
it is preferable to use the standard form over the short form to avoid unwanted
effects, like here:
```
list.0_   ### will get the second element, because the length of '0' is 1
list[0]_  ### will get the length of the first element
(list.0)_ ### this is a valid workaround, but is longer than the standard form
```

## Brace syntax
TODO `x{ASDFSDFDSF}`

## Replace syntax
TODO `x\GSKLHJHKLJL!KJHLKJHFKLH\ `