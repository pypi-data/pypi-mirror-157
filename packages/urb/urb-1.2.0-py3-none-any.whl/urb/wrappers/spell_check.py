import requests

def correct(word):
    url = "https://jspell-checker.p.rapidapi.com/check"

    payload = {
        "language": "enUS",
        "fieldvalues": word,
        "config": {
            "forceUpperCase": False,
            "ignoreIrregularCaps": True,
            "ignoreFirstCaps": True,
            "ignoreNumbers": True,
            "ignoreUpper": False,
            "ignoreDouble": False,
            "ignoreWordsWithNumbers": True
        }
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Host": "jspell-checker.p.rapidapi.com",
        "X-RapidAPI-Key": "d63c21870amsh4cd61ac76f10dbep1aa6f0jsn23601ffb40d0"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    response = response.json()
    # print(response)
    if response['spellingErrorCount'] > 0:
        return response['elements'][0]['errors'][0]['suggestions'][0]
    else:
        return None