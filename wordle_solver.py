"""Solve Wordle style word problems."""

import datetime
import string
from argparse import ArgumentParser
from collections import Counter
from itertools import combinations_with_replacement, permutations
from typing import Counter as CounterType, List


def generate_word_list_file(filename: str, words: List[str]) -> None:
    """Create a file from the list of words.

    The file will contain one word per line.

    :param filename: Name of the output file
    :param words: List of words
    :return: None
    """
    with open(filename, "w") as word_file:
        for word in words:
            word_file.write(word + "\n")


def generate_word_list(word_size: int) -> List[str]:
    """Generated a list of words.
    
    Each word will be all lower case.
    
    :param word_size: Number of characters in each word
    :return: Sorted list of words
    """
    import enchant
    d = enchant.Dict("en_US")

    char_set = string.ascii_lowercase

    # Can't just use 'permutations' to generate the list because it
    # won't include words with multiple instances of the same letter.
    # So we have to use 'combinations_with_replacements' first to get
    # every possible 'group' of letters. Then find all the permutations
    # of each group. This will result in multiple instances of each word
    # that has duplicate letters, so we'll use a 'set' to remove the
    # duplicates.
    words = set()
    for c in combinations_with_replacement(char_set, word_size):
        for p in permutations(c, word_size):
            # Create a word from the group of letters
            word = "".join(p)
            # See if it is in the dictionary
            if d.check(word):
                # Exclude simple plurals by seeing if the same
                # combination minus the final 's' is a word
                if word.endswith("s"):
                    if d.check(word[0:4]):
                        continue
                # This is a valid word, add it to the list
                words.add(word)
    return sorted(words)


def solve(target_word: str, word_list: List[str], show_work: bool = False) -> int:
    """Solve the puzzle using the `word_list`.

    Use the following algorithm to try and solve the puzzle.
    1) Find out which letters are used the most in the word list.
    2) Calculate a score for each word in the list based on the frequency of the letters it contains.
    3) Make a guess using the word with the highest score.
    4) Reduce the word list based on the results of the guess.
    5) Repeat until the guess matches the `target_word`.

    :param target_word: The word we are trying to guess
    :param word_list: List of possible words
    :param show_work: Print status messages
    :return: Number of guesses needed to solve the puzzle
    """
    # Make a copy, so we can reduce the list in place
    words = word_list.copy()

    if show_work:
        print(f"Target word = {target_word}")

    # Loop until we find the answer (starting at 1 since the guess count will be '1' based
    max_loop_count = 100
    for i in range(1, max_loop_count):
        # Which letters are most used in the remaining word list
        counts = calculate_letter_distribution(words)
        if show_work:
            print(counts)

        # Find the word in the list that consumes the highest "letter distribution"
        word_scores = {}
        for word in words:
            score = 0
            for letter in set(word):
                score += counts[letter]
            word_scores[word] = score

        # Sort the dictionary
        sorted_list = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
        if show_work:
            print(sorted_list)

        guess = sorted_list[0][0]
        # Check the word; returns letters that were an exact match or were present somewhere else in the word
        exact_match, other_letters = evaluation_guess(guess, target_word)

        # Get letters that were in the guess but didn't match anywhere
        # Words with these letters will be removed from the word list
        letters_to_remove = "".join(set(guess) - (set(exact_match) | set(other_letters)))
        if show_work:
            print(i, guess, exact_match, other_letters, letters_to_remove)

        if guess == exact_match:
            if show_work:
                print("Done")
            return i

        # Remove the guess since it obviously wasn't the answer
        words.remove(guess)

        # Remove all other words that don't match the returned pattern
        # Loop over a copy of the list, so we can modify the original list in the loop
        for word in words.copy():
            if not fits_pattern(word, exact_match, other_letters, letters_to_remove):
                words.remove(word)

    # If we got here, we couldn't find a solution
    if show_work:
        print("Unable to find a solution")

    return max_loop_count


def fits_pattern(word: str, exact_match: str, others: str, exclude: str) -> bool:
    """Evaluate the `word` and see if it matches the input patterns.

    :param word: Word to evaluate
    :param exact_match: Letters that match the exact position
    :param others: Letters that are present somewhere in the word
    :param exclude: Letters that must not be in the word
    :return: True if the word satisfies the input patterns

    >>> fits_pattern("abcde", "abc**", "*****", "")
    True
    >>> fits_pattern("abdde", "abc**", "*****", "")
    False
    >>> fits_pattern("abcde", "abc**", "***e*", "")
    True
    >>> fits_pattern("abcde", "abc**", "*****", "d")
    False
    """
    # Check for the presence of the excluded letters
    if any([x in word for x in exclude]):
        return False

    remaining_letters = list(word)
    for i, letter in enumerate(word):
        if exact_match[i] != "*":
            if letter != exact_match[i]:
                return False
            else:
                # If the letter matches, remove it from the remaining_letters list
                # so the others list won't find it in the next loop
                remaining_letters.remove(letter)
        if others[i] == word[i]:
            # Letters in the "other" list can't be present in their current location,
            # otherwise, they would have been in the exact_match list
            return False

    for i, letter in enumerate(others):
        if letter != "*":
            if letter not in remaining_letters:
                return False
            else:
                remaining_letters.remove(letter)

    return True


def evaluation_guess(guess: str, target_word: str) -> (str, str):
    """Compare the guess against the target word and return the matching patterns.

    For the return strings, an "*" means no match for that character. For the exact match string,
    a non-* character means that character matched at the exact location. For the other string,
    a non-* character means that letter matched somewhere else in the target word, but NOT at that
    location.

    :param guess: Word to compare against the target word
    :param target_word: The word we are solving for
    :return: (Exact match, other matches)

    >>> evaluation_guess("abcde", "abxcy")
    ('ab***', '**c**')
    >>> evaluation_guess("abcdd", "ffdff")
    ('*****', '***d*')
    >>> evaluation_guess("abcdd", "dfdff")
    ('*****', '***dd')
    """
    # Look for letters that match exactly
    exact_match = [a if a == b else "*" for a, b in zip(guess, target_word)]
    # Make a list of all letters that didn't match exactly
    remaining_letters = [b if a != b else "" for a, b in zip(guess, target_word)]

    # Now see if any of those remaining letters are present somewhere else in the target word
    others = []
    for i, letter in enumerate(exact_match):
        if letter != "*":
            # This position was an exact match, so don't include it in the "others" list
            others.append("*")
        else:
            # This position wasn't an exact match, so see if the letter in the guess is in
            # the list of remaining letters
            if guess[i] in remaining_letters:
                # The letter is in the target word somewhere, so add it to the "other" list and
                # remove it from the remaining letters list
                others.append(guess[i])
                remaining_letters.remove(guess[i])
            else:
                others.append("*")

    return "".join(exact_match), "".join(others)


def calculate_letter_distribution(words: List[str]) -> CounterType:
    """Count the number of occurrences of each letter in the word list.

    :param words: List of words to evaluate
    :return: A counter object that contains an entry for each letter
    """
    c = Counter()
    for word in words:
        c.update(word)
    return c


def analyze(word_list: List[str]) -> None:
    """Solve for every entry in the word list and summarize the results.
    
    :param word_list: List of words to solve for
    :return: None
    """
    print(f"Solving for {len(word_list)} words")
    # The results will be stored in a list of lists; each list will contain all the
    # words it took the same number of guesses to solve.
    distribution = []
    for i in range(100):
        distribution.append([])

    # Process all the words and save the results
    most_guesses = 0
    for word in word_list:
        guesses = solve(word, word_list)
        if guesses > most_guesses:
            most_guesses = guesses
        distribution[guesses].append(word)

    # Display the results
    for i in range(1, most_guesses):
        count = len(distribution[i])
        percent = (count / len(word_list)) * 100
        print(f"{i} - {count} ({percent:.2f}%) - {distribution[i]}")


def get_word_list_from_file(filename: str) -> List:
    """Read words from a text file and return as a list.

    The text file should include one word per line.

    :param filename: Name of the file containing the words
    :return: List of words
    """
    words = []
    with open(filename, "r") as word_list_file:
        for line in word_list_file.readlines():
            words.append(line.strip())
    return words


# noinspection PyShadowingNames
def gen_word_list_sub_command(args):
    """Process the 'gen-word-list' subcommand."""
    print("Generating word list . . .")

    start_time = datetime.datetime.now()
    word_list = generate_word_list(5)
    generate_word_list_file(args.file, word_list)
    elapsed_time = datetime.datetime.now() - start_time

    print(f"Generated {len(word_list)} words in {elapsed_time.seconds} seconds.")


# noinspection PyShadowingNames
def solve_sub_command(args):
    """Process the 'solve' subcommand."""
    solve(args.target_word, get_word_list_from_file(args.word_list_file), show_work=True)


# noinspection PyShadowingNames
def analyze_sub_command(args):
    """Process the 'analyze' subcommand."""
    analyze(get_word_list_from_file(args.word_list_file))


if __name__ == "__main__":
    parser = ArgumentParser(description="Wordle style puzzle solver.")
    subparsers = parser.add_subparsers(required=True)

    gen_parser = subparsers.add_parser("gen-word-list", help="Generate a word list file")
    gen_parser.add_argument("file", help="File that will hold the word list")
    gen_parser.set_defaults(func=gen_word_list_sub_command)

    solve_parser = subparsers.add_parser("solve", help="Solve for the given word")
    solve_parser.add_argument("--word-list", dest="word_list_file", default=None,
                              help="Use the specified list of words")
    solve_parser.add_argument("--target", dest="target_word", default=None, help="Target word")
    solve_parser.set_defaults(func=solve_sub_command)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze solutions for all words")
    analyze_parser.add_argument("--word-list", dest="word_list_file", default=None,
                                help="Use the specified list of words")
    analyze_parser.set_defaults(func=analyze_sub_command)

    args = parser.parse_args()
    args.func(args)
