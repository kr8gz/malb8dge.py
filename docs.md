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
...

## Improve block parsing
...

## .0 after math operations
...

## Macros
...
