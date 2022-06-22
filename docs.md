# Documentation
...

# Planned features and changes
## Fix scope issues
```
x = 2
f = : {
    y = 3
    g = : ;x * y  ### UndefinedError: variable 'y' is not defined
    g
}
f
```
Inner functions can already access global variables and any other variables in the outer scopes which are not inside functions.
Changing this would allow inner functions to access outer functions' variables too.

## Simpler function syntax
```
add = (a, b): a + b

sub = a, b: a - b  ### UndefinedError: variable 'a' is not defined
```
Removing the need for parentheses will make function definitions more consistent, as parentheses are already redundant for functions with only one argument.
This will also remove at least 2 characters per function when compacting malb8dge code.
Unfortunately, this means that initializing a list with a variable and a function definition will require 2 more characters, but this is a trade-off I am willing to make.

## Loop variable
```
10 ~ i: ;i
10 ~: ;~
```
*(This is already valid syntax, but the value of the loop variable itself is always `null`)*

Loop variables would reduce the amount of characters in a compacted program by a tiny amount.
But there is more good news for programmers - you will have to come up with fewer variable names as they will all be called `~`!

## Brace syntax overhaul
This one is complicated to explain.
"String loops" and later "sum loops" showed that the current brace syntax and special advanced array functions are just a complete mess in general.
Merging loops, brace syntax and special array functions while also keeping a simplified version of the current brace syntax will make everything more consistent and versatile.
Combined with the addition of loop variables (see above), this will guarantee that at least 3 characters can be removed for every use of the current brace syntax.

## Improve block parsing
This shouldn't change any syntax or anything else, but blocks and block parsing are so convoluted that at this point I do not even know what is considered a block anymore.

## .0 after math operations
If an operation yields an integer result, the result type should be an integer and not a float. This is mainly for getting rid of the extra character from the `/.` operator when it is not needed, but also for prettier printing results.

## Macros
```
\D == "?" ? ;"don't know 
a, b = _, _
a Da"
b Db"
```
This syntax will replace repetitions in the code that cannot be efficiently abstracted into a function.
