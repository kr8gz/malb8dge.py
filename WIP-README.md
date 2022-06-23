# Introduction
malb8dge is an esolang that aims to shorten code by removing words and reducing repetitions wherever possible, while still keeping it somewhat easy to understand.

# Getting started
## Installing malb8dge
malb8dge is written in pure Python. This means that you will only need Python and nothing else to run the malb8dge interpreter.

To get started, download the repository. (Technically, only the *malb8dge* folder and the *setup.py* file are needed.)
From your terminal, run
```
py setup.py install
```
in the directory where you downloaded this repository.

## Hello, world!
Create a file called *hello.mlb8* with the following contents:
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

Alternatively, you can use [@Unzor](https://github.com/Unzor)'s [malb8rowser website](https://malb8dge.seven7four4.repl.co) to test your code online.
(It has yet to become good though.)

## Updating malb8dge
There is no fancy version manager or installer for malb8dge.
If you feel like updating to the latest malb8dge version, check if the repository has been updated and follow the installation steps again.

# Making a guessing game
Now let's create something more advanced. A classic beginner project is a simple guessing game.
Here is a list of instructions we want it to execute:

* A secret random number between 1 and 100 is generated.
* The program will repeatedly ask for the player's guess.
* A message will be printed that states whether the guess was too high or too low.
* If the guess is equal to the secret number, a message appears telling the player that they won and the program will stop.

Let's start with the secret number.
We can use the `a ?? b` operator, which will generate a random number between `a` and `b`, and assign the result to a variable called `number` like this:
```
number = 1 ?? 100
```

We will then create a loop for the other instructions.
In this case we want an infinite loop that will only end when the player guesses the correct number.
You might know this as a `while true` loop from other programming languages, but malb8dge has a shortcut for that:
```
number = 1 ?? 100

? {
    
}
```
`?` signifies an infinite loop, which will execute all the statements between the braces `{ }` on every iteration.

Next, we will ask the player to input something.
We will add this inside the loop, because we want the player to be able to guess infinitely many times.
```
...

? {
    guess = _
}
```
A `_` will wait for the user to input something and return the input as text.
The text will then be assigned to the `guess` variable.

We can also add an input prompt like this:
```
...

? {
    guess = _("Your guess: ")
}
```
This will print `Your guess:` before waiting for user input.

Now we want to compare `guess` with the secret `number` and output a message depending on the outcome of the comparison.
We can do this using if-statements.
In malb8dge, if-statements work as follows:
```
condition1 ? {      ### if condition1

} ! condition2 ? {  ### else if condition2

} ! condition3 ! {  ### else if not condition3

} ! {               ### else

}
```

We will create 2 branches checking whether the guess is greater than or lesser than the secret number, and a final else part for when it is neither (i.e. equal).
```
    ...
    
    guess < number ? {
        ### less than
    } ! guess > number ? {
        ### greater than
    } ! {
        ### equal
    }
    
    ...
```

But because `guess` has a text value, we need to convert it to a number first before we can compare it to our secret number.
This can be achieved by using the `x$` operator:
```
...

? {
    guess = _("Your guess: ")$
    
    guess < number ? {
    ...
```

This causes a few more problems though.
Not every text input can be converted to a number.
The program will not be able to do anything with inputs such as `"hello"` or `"!@#$%^&*()"`, and this will cause it to stop with an error.
Instead of immediately converting the input to a number, we can check first if the input only contains digits using the `x$$` operator.
If that is not the case, we can print a message that the input was invalid using the `;x` operator from the *Hello, world!* example.
Finally, we also want to skip the rest of the loop with the checking part for this iteration if the input is invalid.
You might know this as the `continue` keyword from other languages, and its malb8dge equivalent is `>`.
After that, we can safely convert `guess` to a number.

Here is how the code should look like now:
```
number = 1 ?? 100

? {
    guess = _("Your guess: ")

    guess$$ ! {            ### if there are not only digits
        ;"Invalid guess!"  ### print a message
        >                  ### continue loop
    }
    
    ### it is now safe to convert it to a number
    guess = guess$

    guess < number ? {
        ### less than
    } ! guess > number ? {
        ### greater than
    } ! {
        ### equal
    }
}
```

If the player's guess is the same as the secret number, we want the program to stop.
This can be done by simply stopping the loop with a `break` statement. Its malb8dge equivalent is `%`.
```
    ...
  
    guess < number ? {
        ### less than
    } ! guess > number ? {
        ### greater than
    } ! {
        %  ### stop the loop
    }
    
    ...
```

After adding a few more print statements, our first little project is finished!
```
;"Guess the number!"

number = 1 ?? 100

? {
    guess = _("Your guess: ")

    guess$$ ! {
        ;"Invalid guess!"
        >
    }

    guess = guess$

    guess < number ? {
        ;"Too low!"
    } ! guess > number ? {
        ;"Too high!"
    } ! {
        ;"You guessed the number!"
        %
    }
}

```

Awesome! You have now learnt about if-statements and how to work with loops, and also got to know some operators!
In the next section, we will ggrgrgrrgrgrg

# Compacting code
tuos was the original intention of malb8dge so wer'ee gonna do that now

# Creating Tic-tac-toe in malb8dge
...

# Pushing malb8dge to its limits
...

# Documentation
The malb8dge documentation can be found [here](https://github.com/kr8gz/malb8dge/blob/master/docs.md).

# Thanks
* Thanks to [@itsmebombie](https://github.com/itsmebombie) for coming up with the name
* Thanks to [@DexterHill0](https://github.com/DexterHill0) for helping me with `setuptools`
* Thanks to [@zTags](https://github.com/zTags) for helping with the layout of the README
