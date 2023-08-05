'''
this module contains printing functions for definitions form various sources
each source (like google and urban dictionary) needs to have it's own printing format
due to the vriations in the information
'''

import os
from collections import namedtuple

import pyfiglet
import typer

from .wrappers import google, urban

CONSOLE_WIDTH = os.get_terminal_size().columns


def print_urb(definition: urban.UrbanDefinition):
    '''
    the printing function for Urban Dictionary definitions
    prameter is a UrbanDefinition object returned from the API wrapper
    '''
    print(pyfiglet.figlet_format(definition.word, font='cybermedium'))

    def format_def(_def):
        if any([str(i) in _def.strip()[:3] for i in range(10)]):
            _def = '• ' + _def.strip()[3:]
        return _def

    def format_eg(_eg):
        _eg = _eg.strip()
        truth = [str(i) in _eg.strip()[:3] for i in range(10)]
        if any(truth):
            truth_index = _eg.index(str(truth.index(True)))
            while _eg[truth_index] != ' ':
                truth_index += 1
            _eg = _eg[truth_index:].strip()
        return _eg

    print(
        '\n'.join(
            list(
                map(format_def, definition.definition.split('\n'))
            )
        )
    )
    # print(f"{definition.definition}")

    lines = definition.example.split('\n')
    if 'example' in lines[0].lower():
        definition.example = '\n'.join(lines[1:])
    print('\nexample ─\n')
    print(
        '\n'.join(
            map(format_eg, lines)
        )
    )
    # print(f"\nexample - \n\n{definition.example}")

    try:
        print(
            f"\nauthor - {definition.author} | 👍 {definition.thumbs_up} | 👎 {definition.thumbs_down} :)")
    except AttributeError:
        print(f"\nauthor - {definition.author} :)")


def print_goog(definition: google.GoogleDefinition, index: int = 0):
    '''
    the printing formatter for definitions from the google dictionary api
    parameter is a GoogleDefinition object returned fromt the API wrapper
    '''
    print(pyfiglet.figlet_format(definition.word, font='cybermedium').strip(), '\n')

    if definition.phonetic is not None:
        print(definition.phonetic, '\n')
    else:
        print('\n')

    if definition.origin is not None:
        print(f"origin - \n{definition.origin}\n")

    if index > len(definition.meanings):
        index = 0
    if index != 0:
        index += 1
        definition.meanings = [definition.meanings[:index - 1][-1]]
    for meaning in definition.meanings:
        print(meaning.part_of_speech)
        print((len(meaning.definition) +
              int((os.get_terminal_size().columns - len(meaning.definition)) / 2)) * "─")
        print(meaning.definition)
        if meaning.example is not None:
            print(meaning.example, "\n")


def print_wotd(wotd: namedtuple):
    print(pyfiglet.figlet_format(wotd.word, font='cybermedium').strip())

    if wotd.type != 'not available':
        print('\n', wotd.type)
    print(((len(wotd.meaning) % os.get_terminal_size().columns) + ((os.get_terminal_size().columns - (len(wotd.meaning) % os.get_terminal_size().columns)) // 2)) * "─")
    print(wotd.meaning, '\n')
    print(f'word of the day on {wotd.date} :)')


def print_quote(quote: namedtuple):
    quote_length = len(quote.quote)
    print('\n')
    print(quote.quote.strip())
    print(((quote_length % CONSOLE_WIDTH) + ((CONSOLE_WIDTH - (quote_length % CONSOLE_WIDTH)) // 2)) * "-")
    print('\n')
    print(f'By {quote.author}')