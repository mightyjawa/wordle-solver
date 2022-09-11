# Wordle Solver

**Wordle Solver** was created to test an algorithm for solving Wordle style word puzzles. 
In its current form, the user must supply both the word to solve for and the set of possible "guess" words.
However, it could be extended to interactively solve for an unknown word when used with a Wordle style game
(but where is the fun in that).

**Wordle Solver** can be used as a stand-alone script or imported into another script.

## Generate a Word File
**Wordle Solver** needs a set of words that it uses as the source of "guesses" as it tries to solve the puzzle.
When using the script in a stand-alone mode, a predetermined list of words can be provided via a text file.
This file can be generated with the *gen-word-list* subcommand.

    python wordle-solver.py gen-word-list filename

## Solve for a Given Word
**Wordle Solver** can iteratively solve a Wordle style puzzle when provided the target word. It will use its
algorithm to try and solve for the given word using the fewest number of "guesses" possible. 

    python wordle-solver.py solve --target TARGET_WORD

The default implementation will first generate a list of valid 5-letter words to use as guesses. Since this process
can take some time, the user can specify a pre-built word list using the *--word-list* option.

    python wordle-solver.py solve --word-list WORD_LIST_FILE --target TARGET_WORD

## Analyze a Set of Words
**Wordle Solver** can be try to solve every word in a given word list. This can be used evaluate the effectiveness
of the algorithm.

    python wordle-solver.py analyze --word-list WORD_LIST_FILE
