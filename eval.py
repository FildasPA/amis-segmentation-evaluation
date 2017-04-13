#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
-- Object : Evaluate a file against a reference file.
-- By : Julien Boge
-- Last modification : 13.04.17
-- Usage : eval.py evaluated_file reference_file [-c] [-m] [-u] [-v] [-w N]
"""

import sys
import os
import string
import argparse
from argparse import RawTextHelpFormatter

verbose = False
display_matching_sentences = False
display_unmatching_sentences = False
words_to_print = 10

DESCRIPTION = """
This scripts reads two files.
It compares the number of sentences and the average of words in sentences.
Then, it counts sentences whose ending word match.
"""

class Colors:
    PURPLE    = ''
    BLUE      = ''
    GREEN     = ''
    YELLOW    = ''
    RED       = ''
    RESET     = ''
    BOLD      = ''
    UNDERLINE = ''

    @staticmethod
    def activate():
        Colors.PURPLE    = '\033[95m'
        Colors.BLUE      = '\033[94m'
        Colors.GREEN     = '\033[92m'
        Colors.YELLOW    = '\033[93m'
        Colors.RED      = '\033[91m'
        Colors.RESET     = '\033[0m'
        Colors.BOLD      = '\033[1m'
        Colors.UNDERLINE = '\033[4m'

def print_num(num):
    return Colors.GREEN + str(num) + Colors.RESET

def color(msg, color):
    return color + str(msg) + Colors.RESET

def print_err(msg):
    print color("Erreur: ", Colors.RED) + str(msg)

def print_warning(msg):
    print color("Attention: ", Colors.YELLOW) + str(msg)

def count_lines(filename):
    """Renvoie le nombre de lignes d'un fichier."""
    count = 0

    with open(filename, 'r') as file:
        for line in file:
            lines += 1

    return lines

def count_words_within_phrase(phrase):
    """"""
    # punctuation is not considered as a word, remove it
    phrase = phrase.translate(None, string.punctuation)
    words = len(phrase.split())
    return words

def count_phrases_mean_size(filename):
    """Return the average size of lines within a file."""
    phrases_size = []

    with open(filename, 'r') as file:
        for line in file:
            phrases_size += [count_words_within_phrase(line)]

    phrases_mean_size = sum(phrases_size) / len(phrases_size)
    return phrases_mean_size

def print_phrases_mean_size(eval_filename, ref_filename):
    """"""
    print "Nombre de mots moyen par phrase (évalué)    = ",
    print print_num(count_phrases_mean_size(eval_filename))
    print "Nombre de mots moyen par phrase (référence) = ",
    print print_num(count_phrases_mean_size(ref_filename))

def cut_sentence(sentence, num_words):
    """Cut a sentence if it's too long."""
    range = num_words / 2
    sentence = sentence.strip()
    if (num_words == 0) or (len(sentence.split()) <= num_words):
        return sentence
    else:
        cut  = ' '.join(sentence.split()[:range])
        cut += " ... "
        cut += ' '.join(sentence.split()[-range:])
        return cut

def print_matching_sentences(eval_line, ref_line, i, j):
    print color("Phrases correspondantes:",Colors.GREEN)
    print color(str(i) + " auto:     ", Colors.YELLOW),
    print cut_sentence(eval_line, words_to_print)
    print color(str(j) + " manuelle: ", Colors.YELLOW),
    print cut_sentence(ref_line, words_to_print)

def print_unmatching_sentence(line, i, type):
    print color("Phrase ne correspondant à aucune autre:",Colors.RED)
    print color(str(type) + " " + str(i), Colors.YELLOW),
    print cut_sentence(line, words_to_print)

def format_ref_line(line):
    """Formate une ligne issue de la transcription manuelle.
    Plus on effectue de transformations, plus on est "tolérant" avec le
    transcripteur automatique.
    """
    # Supprime pX \t
    if not line:
        return ""
    line = line.split(' ',1)[1]
    # Passage aux minuscules
    line = line.lower()
    # Supprime les espaces en trop
    line = line.strip()
    # Supprime la ponctuation en trop
    line = line.replace('.','')
    line = line.replace(',','')
    line = line.replace(';','')
    line = line.replace('"','')
    line = line.replace(':','')
    line = line.replace('!','')
    line = line.replace('?','')
    # Sépare les apostropes du mot qui les suit
    line = line.replace('l\'','l\' ')
    line = line.replace('d\'','d\' ')
    line = line.replace('s\'','s\' ')
    return line

def right_cut(eval_line, ref_line):
    """Tell if ending lines match."""
    eval_line = eval_line.replace(' .','')

    if not eval_line.split() or not ref_line.split():
        return False

    return eval_line.split()[-1] == ref_line.split()[-1]

def count_right_cuts(eval_filename, ref_filename):
    """Count the number of matching ending lines within two files."""

    eval_file = open(eval_filename, 'r')

    ref_lines = []
    ref_file = open(ref_filename, 'r')

    # Lis les premières lignes du fichier de référence
    for i in range(0, 10):
        ref_line = format_ref_line(ref_file.readline().strip())
        ref_lines += [ref_line]

    coupe_ok = 0
    num_ref_line = 0
    unmatching_evaluated_lines = []
    unmatching_reference_lines = []
    found = False

    if display_matching_sentences:
        print color("Coupes correspondantes:", Colors.PURPLE)

    for i, eval_line in enumerate(eval_file):
        for j, ref_line in enumerate(ref_lines):
            if right_cut(eval_line, ref_line):
                coupe_ok += 1
                unmatching_reference_lines += ref_lines[:j]
                ref_lines = ref_lines[j+1:]
                if display_matching_sentences:
                    print_matching_sentences(eval_line, ref_line, i, num_ref_line)

                num_ref_line += j + 1
                found = True
                break

        if not found:
            if display_unmatching_sentences:
                unmatching_evaluated_lines += [eval_line]
            num_ref_line += 1

        found = False
        ref_line = format_ref_line(ref_file.readline().strip())
        ref_lines += [ref_line]

    if display_unmatching_sentences:
        print color("Unmatching sentences within evaluated file:", Colors.RED)
        for line in unmatching_evaluated_lines:
            print cut_sentence(line, words_to_print)
        print "===================="
        print color("Unmatching sentences within reference file:", Colors.RED)
        for line in unmatching_reference_lines:
            print cut_sentence(line, words_to_print)

    return coupe_ok

def calc(right_cuts, num_cuts):
    """Calcule la précision et le rappel"""
    return float(right_cuts) / num_cuts

def calc2(precision, rappel):
    """Calcul f-1"""
    if(precision + rappel == 0):
        return 0
    return 2 * (float(precision * rappel) / (precision + rappel))

def main(eval_filename, ref_filename):

    num_lines = sum(1 for line in open(eval_filename))
    if not num_lines:
        print_err(eval_filename + " est vide")
        exit(1)
    num_ref_lines = sum(1 for line in open(ref_filename))
    if not num_ref_lines:
        print_err(ref_filename + " est vide")
        exit(1)

    right_cut = count_right_cuts(eval_filename,
                                 ref_filename)

    if not verbose and (display_matching_sentences or display_unmatching_sentences):
        exit(0)

    print_phrases_mean_size(eval_filename, ref_filename)

    print ""
    print "Nombre de lignes (évalué)    = " + print_num(num_lines)
    print "Nombre de lignes (référence) = " + print_num(num_ref_lines)
    print "Nombre de coupes correctes   = " + print_num(right_cut)
    print ""


    precision = calc(right_cut, num_lines)
    rappel    = calc(right_cut, num_ref_lines)
    f         = calc2(precision, rappel)

    print "précision = " + print_num(precision)
    print "rappel    = " + print_num(rappel)
    print "f-1       = " + print_num(f)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('evaluated_file',
                        help="Specify the file to evaluate")
    parser.add_argument('reference_file',
                        help="Specify the reference file")
    parser.add_argument('-c', '--color', action="store_true", default=False,
                        help="Print colors")
    parser.add_argument('-m', '--matching-cuts', action="store_true", default=False,
                        help="Only prints phrases with matching cut")
    parser.add_argument('-u', '--unmatched', action="store_true", default=False,
                        help="Prints phrases with unmatched cuts (from both files)")
    parser.add_argument('-v', '--verbose', action="store_true", default=False,
                        help="Display statistics and phrases with matching cut")
    parser.add_argument('-w', '--words', type=int,
                        help="Define the number of words to print; 0 will print full sentences")

    args = vars(parser.parse_args())

    if args['verbose']:
        verbose = True

    if args['verbose'] or args['matching_cuts']:
        display_matching_sentences = True

    if args['verbose'] or args['unmatched']:
        display_unmatching_sentences = True

    if args['color']:
        Colors.activate()

    if args['words'] or args['words'] == 0:
        if not display_matching_sentences:
            print_warning("--words needs --matching-cuts or --verbose options")
        words_to_print = args['words']

    evaluated_filename = args['evaluated_file']
    reference_filename = args['reference_file']

    main(evaluated_filename, reference_filename)
