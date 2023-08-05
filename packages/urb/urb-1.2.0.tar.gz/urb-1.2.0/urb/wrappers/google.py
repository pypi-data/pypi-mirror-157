"""
just a sneazy wrapper around the Free Dictionary API from https://dictionaryapi.dev/
allows defining searching for a definition for a word
"""

from typing import List
import requests

FD_ENTRIES_URL = 'https://api.dictionaryapi.dev/api/v2/entries/en/'

class DefinitionMeaning():

    __slots__ = (
        'part_of_speech',
        'definition',
        'example',
        'synonyms',
        'antonyms'
    )

    def __init__(self, **data) -> None:
        self.part_of_speech = data.get('partOfSpeech', None)
        self.definition = data.get('definitions')[0]['definition']
        self.example = data.get('definitions')[0].get('example', None)
        self.synonyms = data.get('definitions')[0]['synonyms']
        self.antonyms = data.get('definitions')[0]['antonyms']


class GoogleDefinition():

    __slots__ = (
        'word',
        'phonetic',
        'origin',
        'meanings'
    )

    def __init__(self, **data) -> None:
        self.word = data.pop('word', None)
        self.phonetic = data.pop('phonetic', None)
        self.origin = data.pop('origin', None)
        self.meanings = [DefinitionMeaning(**meaning) for meaning in data.pop('meanings', [])]

    def __repr__(self):
        return f"<GoogleDefinition {self.word!r}>"
    def __str__(self):
        return str(self.word)

def _get_google_json(url: str) -> dict:
    try:
        data = requests.get(url).json()
    except Exception as exception:
        print()
        data = []
    return data

def _parse_google_json(data):
    results = []
    if len(data) <= 0 or 'resolution' in data:
        data = []
        return data
    for _definition in data:
        results.append(GoogleDefinition(**_definition))
    return results

def define(term) -> List[GoogleDefinition]:
    '''
    returns definition for a word

    parameters:
        term: str

    e.g. urban.define('hello')
    '''
    data = _get_google_json(FD_ENTRIES_URL + term)
    return _parse_google_json(data)

if __name__ == '__main__':
    definition = define('lmao')
