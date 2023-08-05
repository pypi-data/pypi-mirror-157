# urb

urb is a dank cli dictionary to quickly search up definitions from Urban Dictionary and Google

It is primarily supposed to be used from the terminal, and can also be used as a python module to use the Urban Dictionary and Google dictionay APIs and much more

The CLI offers a lot of fun amusing commands to fulfill your vocabulary needs from the convinience of the terminal.

# Installation

    pip install urb

# commands

## define

Pulls up the definition for a word. the word to be searched is given as an argument to this command. Urb searches words on urban dicitonary by default

    urb define hello

- fetch search results from Google dictionary instead \

        urb define -g hello
        
        urb define --google hello

- Specify the result to display out of multiple definitions fetched from the resources. There can be multiple definitions for a single word, use this option to choose which definition gets displayed. This option takes a number as an argument.

        urb define -i 3 hello

        urb define --index 3 hello

## random

Get's the definition of a random word. This commands takes no arguments and has no options.

    urb random

## spell

use this commands to verify if a spelling is correct. urb offers corrections is a spelling is wrong. This commands takes a word as an argument and has no options.

    urb spell convinience

## wotd

Get a word of the day.

    urb wotd

- Specify the result to display out of multiple definitions fetched from the resource. There can be multiple multiple words of the day, use this option to choose which definition gets displayed. This option takes a number as an argument.

        urb wotd -i 3

        urb wotd --index 3

## quote

fetch a random quote

    urb quote
