# Introduction
malb8dge is an esolang that aims to shorten code by removing words and reducing repetitions wherever possible, while still keeping it somewhat easy to understand.

# Getting started
## Hello, world!
malb8dge is written in pure Python. This means that you will only need Python and nothing else to run the malb8dge interpreter.

To get started, run `py setup.py install` in the directory where you downloaded this repository.
Then create a file called *hello.mlb8* with the following contents:
```
;"Hello, world!"
```

To run this program, simply type `malb8dge hello` in your favorite terminal.
If `Hello, world!` was printed to your console, then congratulations! You have written your first malb8dge program!

Now let's break down this program to understand what exactly is happening.

* `;` is an operator that prints everything that comes after it to the console.
* `"Hello, world!"` is a string, which you probably already know from other programming languages.
(If you have no programming experience, I strongly recommend immediately finding another activity to waste your precious time on.)

Great! It will almost certainly only go downhill from here on.

## Running malb8dge programs
As you might have already noticed, malb8dge files are run using the `malb8dge` command, followed by the location of the .mlb8 file you want to run.

An interactive shell also exists, which can be launched by just running `malb8dge` with no additional arguments.

Alternatively, you can use [@Unzor](https://github.com/Unzor)'s [malb8rowser website](https://malb8dge.seven7four4.repl.co) to test your code online. (It has yet to become good though.)

# Basic ideas
...

# first program thingy
...

# more advanced things
...

# final project thing
...

# Documentation
...

# Planned features and changes
## Fixing scope issues
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

# Thanks
* Thanks to [@itsmebombie](https://github.com/itsmebombie) for coming up with the name
* Thanks to [@DexterHill0](https://github.com/DexterHill0) for helping me with `setuptools`
* Thanks to [@zTags](https://github.com/zTags) for helping with the layout of the README
