"""
yet anotehr wrapper around the Urban Dictionary API
provides methods to get results for queried words as well as random words
"""

from typing import List
import requests

UD_DEFINE_URL = 'https://api.urbandictionary.com/v0/define?term='
UD_RANDOM_URL = 'https://api.urbandictionary.com/v0/random'

class UrbanDefinition():

    __slot__ = (
        'word',
        'definition',
        'example',
        'author',
        'thumbs_up',
        'thumbs_down',
        'id'
    )

    def __init__(self, **data) -> None:
        self.word = data.pop('word', None)
        self.definition = data.pop('definition', None)
        self.example = data.pop('example', None)
        self.author = data.pop('author', None)
        self.thumbs_up = data.pop('thumbs_up', None)
        self.thumbs_down  = data.pop('thumbs_down', None)
        self.id = data.pop('defid', None)

    def __repr__(self):
        return f"<UrbanDefinition {self.word!r} - {self.id!r}>"

    def __str__(self):
        return str(self.word)

def _get_urban_json(url: str) -> dict:
    return requests.get(url).json()

def _parse_urban_json(json_response):
    results = []
    # print(json_response)
    # [print(key, ': ', json_response['list'][0][key]) for key in json_response['list'][0].keys()]
    if json_response is None or any([e in json_response for e in ('ERROR', 'error')]):
        raise ValueError("Urb: invalid request")
    if 'list' not in json_response or len(json_response['list']) < 1:
        return results
    for definition in json_response['list']:
        results.append(UrbanDefinition(**definition))
    return results

def define(term) -> List[UrbanDefinition]:
    '''
    returns definitions for a word

    parameters:
        term: str

    e.g. urban.define('hello')
    '''
    json_response = _get_urban_json(UD_DEFINE_URL + term)
    return _parse_urban_json(json_response)

def random() -> List[UrbanDefinition]:
    '''
    returns definitions of 10 random words
    '''
    json_response = _get_urban_json(UD_RANDOM_URL)
    return _parse_urban_json(json_response)

if __name__ == '__main__':
    rando = random()
