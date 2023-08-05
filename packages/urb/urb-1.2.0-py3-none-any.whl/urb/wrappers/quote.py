from collections import namedtuple

import requests


url = 'https://zenquotes.io/api/random'

Quote = namedtuple('Quote', ['quote', 'author'])

def get_rand_quote():
    response = requests.get(url).json()[0]

    quote = Quote(response['q'], response['a'])

    return quote