import random as _random

import requests
import typer

from . import prints
from .wrappers import quote as _quote
from .wrappers import wotd as _wotd
from .wrappers import google as _google
from .wrappers import spell_check, urban


# TODO - minimal output
# TODO - trans

urb = typer.Typer(help="the dankest CLI dictionary", add_completion=False)


@urb.command()
def define(
    word: str = typer.Argument(..., metavar='word'),
    google: bool = typer.Option(False, '--google', '-g', help='get definitions from google  '),
    index: int = typer.Option(0, '--index', '-i', metavar='', help="the nth result to display of multiple")
):
    '''
    search up definition a word
    '''
    try:
        if google:
            definition = _google.define(word)
            prints.print_goog(definition[0], index)
        else:
            definition = urban.define(word)
            prints.print_urb(definition[:index + 1][-1])
    except requests.exceptions.ConnectionError:
        print('\nplease connect to the internet :)')
    except IndexError:
        print(f'no definitions found for {word} :(')
        correction = spell_check.correct(word)
        if correction is not None:
            correction_flag = input(
                f"btw, did you mean  \033[92m{correction}\033[0m? (y/n) ")
            if correction_flag == 'y':
                if google:
                    definition = _google.define(correction)
                    prints.print_goog(definition[0], index)
                else:
                    definition = urban.define(correction)
                    prints.print_urb(definition[:index + 1][-1])
            else:
                print("\nok, see ya later ^_^")


@urb.command()
def random():
    '''
    define a random word
    '''
    try:
        definitions = urban.random()
        prints.print_urb(definitions[_random.randint(0, 9)])
    except requests.exceptions.ConnectionError:
        print('\nplease connect to the internet :3')


@urb.command()
def spell(word: str = typer.Argument(..., metavar='word')):
    '''
    check the spelling of a word

    displays the corrected spelling if wrong
    '''
    try:
        correction = spell_check.correct(word)
        if correction is not None:
            print('\nthe correct spelling is' +
                  f' \033[92m{correction}\033[0m ' + ':3')
        else:
            print("\nthe spelling is correct >_<")
    except requests.exceptions.ConnectionError:
        print('\nplease connect to the internet :3')


@urb.command()
def wotd(index: int = typer.Option(0, '--index', '-i', metavar='', help='the nth result to display of multiple')):
    '''
    check out the word of the day
    '''
    try:
        wotd = _wotd.get_wotd()[:index+1][-1]
        prints.print_wotd(wotd)
    except requests.exceptions.ConnectionError:
        print('\nplease connect to the internet :3')


@urb.command()
def quote():
    '''
    one quote a day keeps the therapist aways :)
    '''
    try:
        quote = _quote.get_rand_quote()
        prints.print_quote(quote)
    except requests.exceptions.ConnectionError:
        print('\nplease connect to the internet :3')


def main():
    urb()
