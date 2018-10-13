#!/bin/bash
import os
import sys


def clear_screen():
    os.system("clear")


POTENTIAL_MATCHES = {
    "rz": "rzż",
    "ż": "rzż",
    "u": "uó",
    "ó": "uó",
    "ch": "hch",
    "h": "hch",
}

WORD_BOUNDARY = (" ", ",", ".")


class Letter:
    pass


class NormalLetter(Letter):
    def __init__(self, letter):
        self.letter = letter

    def __repr__(self):
        return self.letter


class DyktandizableLetter(Letter):
    def __init__(self, letter):
        self.expected = letter
        self.letter = "_"

    def __repr__(self):
        return self.letter


def word_start_index(tokens, token_idx):
    word_start = last_match(lambda t: t.letter in WORD_BOUNDARY, tokens[:token_idx])
    if word_start:
        return tokens.index(word_start)
    return 0


def word_end_index(tokens, token_idx):
    word_end = first_match(lambda t: t.letter in (" ", ",", "."), tokens[token_idx:])
    if word_end:
        return tokens.index(word_end)
    return len(tokens)


def add_mistakenly_written_word(tokens, mistake_idx):
    word_start = word_start_index(tokens, mistake_idx)
    word_end = word_end_index(tokens, mistake_idx)
    return tokens[word_start:word_end]


def tokenize(text):
    letter_index = 0
    output_text = []
    while letter_index < len(text):
        matched_letter = match_dyktandizable_letter(text[letter_index:])
        if matched_letter:
            output_text.append(DyktandizableLetter(matched_letter))
            letter_index += len(matched_letter)
        else:
            output_text.append(NormalLetter(text[letter_index]))
            letter_index += 1

    return output_text


def match_dyktandizable_letter(text):
    for match in POTENTIAL_MATCHES:
        if text.startswith(match):
            return match
    return None


def first_match(fun, seq):
    return next((t for t in seq if fun(t)), None)


def last_match(fun, seq):
    return first_match(fun, reversed(seq))


file_name = sys.argv[1]

with open(file_name) as file:
    input_text = file.read()


class Colors:
    RED = '\033[91m'
    NORMAL = '\033[0m'


tokens = tokenize(input_text)
idx = 0
dictation_finished = False
errors = []


def render_dictation_text(tokens, idx):
    output_text = []
    for token in tokens[:idx]:
        output_text.append(token.letter)
    if idx < len(tokens):
        output_text.append(Colors.RED + "?[" + POTENTIAL_MATCHES[tokens[idx].expected] + "]" + Colors.NORMAL)
    for token in tokens[idx + 1:]:
        output_text.append(str(token))
    return "".join(output_text)


while not dictation_finished:
    clear_screen()
    next_dyktandizable = first_match(lambda t: isinstance(t, DyktandizableLetter), tokens[idx:])
    if next_dyktandizable:
        idx += tokens[idx:].index(next_dyktandizable)

        print(render_dictation_text(tokens, idx))
        letter = input("\nWhat letter?")
        if letter != tokens[idx].expected:
            errors += [add_mistakenly_written_word(tokens, idx)]
        tokens[idx] = NormalLetter(letter)
    else:
        dictation_finished = True

print(render_dictation_text(tokens, len(tokens)))

print("")
print("You have made {} error(s):".format(len(errors)))
with open("mistakes.txt", "w") as mistakes:
    for error in errors:
        bad_word = "".join([str(e) for e in error])
        print(" -", bad_word)
        mistakes.write(bad_word.strip() + "\n")
