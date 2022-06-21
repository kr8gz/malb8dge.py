# Introduction
malb8dge (thanks bombie) is ANOTHER programming language made by kr8gz who
doesn't know how to make programming languages.

The main goal of the language is to shorten code by removing words wherever
possible, while still keeping it somewhat easy to read and understand.

# Documentation [OUTDATED]

## Running a malb8dge program
Run `py <location of malb8dge file> <location of .mlb8 file>`
in the command prompt to run a malb8dge script. Alternatively,
use `py <location of malb8dge file>`
to launch the interactive shell.

## Structure

### Blocks
Blocks are the biggest element in malb8dge. They consist of multiple statements
in braces (`{...}`) or a single statement after a colon (`:`) which is sometimes
optional. On the global level, neither the braces nor the colon are required.
Blocks always return the value of the last statement, or `null` if the block is
empty. This means that blocks (with braces) may also be used as values.

Blocks are required for:

* If-statements (colon optional)
* While loops (colon optional)
* For loops
* Functions (colon optional as the definition of a function already requires a
  colon)

Examples:
```
add = (x, y): x + y             ### block with one statement, returns x + y

multiply = (x, y): {            ### block start
    ;"Multiplying {x} by {y}!"
    x * y                       ### return x * y
}                               ### block end

3 > 2 ? ;"3 is greater than 2"  ### colon not required for if-statements
```

### Statements
A statement is basically a piece of code that does something. In malb8dge,
statements are separated by either a newline or a semicolon (`;`) and can be
one of the following:

* an expression
* a break statement - `%x` with optional expression x (only in loops)
* a continue statement - `>x` with optional expression x (only in loops)
* a return statement - `<x` with optional expression x (only in functions)
* an exit statement - `%%` (stops the program)

### Expressions
An expression is something that can be evaluated to return a value. malb8dge
expressions consist of one or more values chained together with *binary
operators*.

Examples:
```
3 + 4 + 5
3.1415926535 > 2.718281828
.._ & ?#$
x = 6 * y % 7
z /.= 10
/"Hello", "World!"
```

### If-expressions
In malb8dge, if-expressions can act as if-statements or ternary operators and
can be chained to create if-elif-else chains. The syntax for an if-expression
is:

`<expression> ? <block for true>` or
`<expression> ? <block for true> ! <block for false>`

Examples:
```
$("How old are you? ") < 18 ? {
    ;"You are younger than 18!"
} ! {
    ;"You are 18 or older!"
}

### or without braces
$("How old are you? ") < 18 ? ;"You are younger than 18!" ! ;"You are 18 or older!"

### code golfed to the maximum
;"You are {$("How old are you? ")<18?"younger than 18"!"18 or older"}!"

### chaining
input = _
input == "yes" ? ;"yay" ! input == "no" ? ;"nay" ! ;"invalid choice"
```

### Loops
Loops are created by adding `~` after an expression. By default, all loops are
for loops. To create a while loop, add a `?` after the `~`. In a for loop, you
can specify one or more target variables after the `~`. All loops must have a
block which will be run on each iteration. Because blocks always return the
last value, loops can be used to create a list with each of the return values.

Examples:
```
^10 ~ i: ;"The value of i is: " + i  ### simple for loop with a range
^^"test!" ~ (a, b): ;"{a}: {b}"      ### unpacking an enumeration
true ~ ? {}                          ### infinite loop
_ != "yes" ~ ? ;"Will you say yes?"  ### no colon needed

### Loop → List example
i = 0
list = i < 10 ~ ? {
    ;"The value of i is: " + i
    i++  ### Add i to the return values and increment it
}
;[list]  ### list now contains 0, 1, 2, ..., 10

### Using return values of a for loop to map an iterable
abc = "abcdefghijklmnopqrstuvwxyz"
;_ ~ char: abc[abc[@char] + 13 % 26]  ### ROT13 on input
```

### Functions
Functions are defined by providing a list of arguments, followed by a colon and
a block.

Examples:
```
add = (x, y): x + y           ### function with 2 arguments
double = x: x * 2             ### function with 1 argument - no parentheses needed
doStuff = : ;"doing stuff"    ### function with no arguments

longerStuff = : {             ### the colon is needed to be able to tell it
    ;"doing stuff"            ### apart from a normal block
    ;"doing more stuff"
}

### Additional info
add = x, y: x + y             ### will be grouped as (add = x), (y: x + y)
add = [x, y]: x + y           ### possible, but parentheses are preferred
double = (x): x * 2           ### add parentheses when they improve readability
doStuff = (): ;"doing stuff"  ### if you REALLY don't like the : being alone
```

### Values
Values are the smallest elements in malb8dge. They can be one of the following:

* Literals (strings, integers, floats)
* Lists in brackets
* Parenthesized expressions
* Identifiers (variables, true/false, null)
* Blocks

Values may be preceded by one or more *before operators* and/or followed by one
or more of each of the following:

* after operators
* function calls
* list indexing
* "brace syntax"
* "replace syntax"

They will be explained in more detail later.

Examples:
```
;"Hello World!"
^#-16777216
(2.718281828 > 3.1415926535)
`["a", 4, false]^^
null
doStuff(x, y /. 3, z){^}[0]\the\\_
```

### Comments
Comments are ignored by the compiler, allowing you to explain your (ugly) code.
In malb8dge, there are only single line comments. Comments start with `###`.

## Data types
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
Operators are the most important part of malb8dge. Basically everything you know
from Python or other languages has its own "operator" in malb8dge.

The result of trying to keep malb8dge code relatively easy to type (unlike
other esolangs, no fancy math symbols or anything similar are needed!) is that
the meaning of operators changes completely depending on their position around
a value.

### Input and output
```
;x                 ### prints x but each element is concatenated
/x                 ### prints x with spaces separating each element

_(x)               ### gets input with optional prompt (x)
$(x)               ### gets input as number with optional prompt (x)
#$(x)              ### splits input into a list of numbers with optional prompt (x)
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
Note: The print operators also return the string that was printed.

The "get input as number" part will be explained in the Numbers section.

### Numbers
```
x$       ### If x is a list:
         ###   Convert every element in x to a number
         ###
         ### How converting to a number works:
         ###   - Try converting x to float
         ###   - If x cannot be converted to float, then error
         ###   - If x ends in .0, then return x converted to int
         ###   - Else return x converted to float
         
x'       ### Round x to the nearest integer
-x       ### Negate x
#x       ### Return the absolute value of x
x++, x-- ### Return value then increment / decrement
++x, --x ### Increment / decrement then return value

a @ b    ### If a is a string: Convert base b number in string to an int
         ### If a is an int:   Return the base b representation of a

a ^* b   ### Return the larger value
a .* b   ### Return the smaller value
a ** b   ### Raise a to the power of b
a /% b   ### Returns [a /. b, a % b]
a +- b   ### Returns [a + b, a - b]
a /. b   ### Floor division
a / b    ### Division
a * b    ### Multiplication
a - b    ### Subtraction
a + b    ### Addition
a % b    ### Modulo
```

### Strings
```
x`       ### Convert x to string / convert every element in a list to string
x^^      ### Join list with empty string
x##      ### Split string with space as delimiter
x#$      ### Split string into a list of digits converted to int
x_       ### Get length of x
x``      ### Check if string is alphabetic
x$$      ### Check if string is numeric
x@@      ### Check if string is alphanumeric
.x       ### Convert x to lowercase string
..x      ### Check if string is lowercase
`x       ### Convert x to uppercase string
``x      ### Check if string is uppercase
'x       ### Convert character to int and vice versa

a *# b   ### Split string a on first occurrence of b
a #* b   ### Split string a on last occurrence of b
a # b    ### Split string a with string b as delimiter
a ^ b    ### Join list a with string b
```

### Logic
```
?x       ### Convert x to bool
!x       ### Convert x to bool and inverts value

a > b    ### Check if a is greater than b
a < b    ### Check if a is less than b
a >> b   ### Check if a is greater than or equal to b
a << b   ### Check if a is less than or equal to b
a == b   ### Check if a is equal to b
a != b   ### Check if a is not equal to b
a & b    ### Return a if ?a is false, else return b
a | b    ### Return a if ?a is true, else return b
a && b   ### Return ?(a & b)
a || b   ### Return ?(a | b)
```

### Miscellaneous
```
@x       ### Reverse x
^^x      ### Enumerate x

^x       ### If x is an int: create a list of ints from 0 to x - 1
         ### If x is a list of ints:
         ###   Create a range based on the following parameters:
         ###            [stop]
         ###     [start, stop]
         ###     [start, stop, step]
```

## Other syntax

### Interpolated strings
Strings can have expressions inside them when surrounded by braces (`{...}`).
No special marker at the start of the string is required for it to be an
interpolated string. `null` will be treated as an empty string. Interpolated
strings can also be nested.

Examples:
```
"x + y is {x + y}!"
"test{$ != 1 ? "s"}"  ### no else part → null → empty string
"There {apples == 1 ? "is 1 apple" ! "are {apples} apples"}!"  ### nesting
```

### Function calls
These are pretty normal in malb8dge. The target function is followed by
parentheses and a list of arguments passed.

Examples:
```
add(3, 4)
something()
otherThing(s)
doStuff(x, y /. 3, true)
```

### List indexing
List indexing in malb8dge is a bit more complicated than in other languages.
There is a short form and a standard form. The short form allows for shorter
code, but reduced functionality. The syntax for the short form is the target,
followed by a dot and a value (the index). This value may be a variable or be
preceded or followed by operators.

Examples for short form: `list.0`, `list.x.y`, `list.1.2.3`, `list.-1`

The standard form is what you are probably used to in other programming
languages. In malb8dge, this standard form is extended to add more
functionality to reduce the amount of operators which are needed elsewhere.

These functionalities are:
* `list[x]` - normal indexing
* `list[+x]` - count occurrences of x
* `list[?x]` - check if list contains x
* `list[@x]` - index of x in list
* `list[start:stop:step]` - slicing (works like in python)

It is also possible to mix the short form and the standard form. In some cases,
it is preferable to use the standard form over the short form to avoid unwanted
effects, like here:
```
list.0_   ### will get the second element, because the length of '0' is 1
list[0]_  ### will get the length of the first element
(list.0)_ ### this is a valid workaround, but is longer than the standard form
```

### Brace syntax
You can think of brace syntax as a kind of "reduce function". There are 15
different modes to pick from. The syntax is as follows:
```
x{mf}
```
where `x` is an iterable, `m` is a character specifying one of the predefined
modes, and `f` is an optional key function.

The different modes are:
* normal reduce with any of the following 9 operators:
  `+`, `-`, `*`, `/`, `/.`, `&`, `|`, `&&`, `||`
* `=` / `!` - check if all values are equal / different
* `<` / `>` - sort ascending / descending
* `.` / `^` - get minimum / maximum value

Examples:
```
${*}       ### digit product
!list{!}   ### check if list has any duplicate values
_{+x: 'x}  ### sum of all char values of all characters
```

### Replace syntax
Replace can only be used on strings. Replacing works in *pairs* which are
defined in the *patterns*. There are 2 *patterns*: the "find pattern" on the
left, and the "replace pattern" on the right, which are separated by the mode
specifier.

There are 4 different replace modes:
* `\​` - replace all
* `!` - replace first
* `@` - replace last
* `|` - swap

The replacement action will be performed on each pair.

With *single character mode* (double backslash at the beginning), only single
characters from both patterns form a *pair*. If not, each value in the pattern
must be separated by a comma. If there are more find values than replace values,
any remaining find value will be paired with an empty string. There must not be
more replace values than find values.

Similarly to strings, replace patterns can be interpolated by using braces
(`{...}`) too. (Note: only without single character mode)

To escape characters with special meanings (like braces or backslashes), use
`` ` ``.

Examples:
```
s\123\456\   ### replace "123" with "456"
s\\123\456\  ### replace "1" with "4", "2" with "5" and "3" with "6"
s\`\\\       ### remove all backslashes
s\x|o\       ### swap all "x" and "o"
s\_!{_}\     ### replace first "_" with user input
```

**Please tell me if something is unclear or if I can make anything easier to
understand!**
