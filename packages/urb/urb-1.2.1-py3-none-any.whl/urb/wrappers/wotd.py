from collections import namedtuple

import requests

BASE_URL = "https://word-of-the-day2.p.rapidapi.com/word/today"

headers = {
	"X-RapidAPI-Host": "word-of-the-day2.p.rapidapi.com",
	"X-RapidAPI-Key": "1df31ffe41mshf0e37a0bcbfb997p1c41bbjsn1a66024d579c"
}

Word = namedtuple('Word', ['date', 'word', 'meaning', 'type'])
words = []
def get_wotd():
    response = requests.request("GET", BASE_URL, headers=headers)

    response = response.json()[1:]

    for word in response:
        word = Word(word['date'], word['word'], word['mean'], word['type'])
        words.append(word)

    return words


if __name__ == '__main__':
    words = get_wotd()
    print(words)
