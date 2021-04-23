from pprint import pprint

import requests


def search_in_wiki(search_page):
    result = {
        "completed": False,
        "title": '',
        'body': '',
        'url': ''
    }
    URL = "https://ru.wikipedia.org/w/api.php"

    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srlimit": 2,
        "srsearch": search_page
    }

    response = requests.get(url=URL, params=PARAMS).json()
    pprint(response)
    if response["query"]["searchinfo"]["totalhits"] == 0:
        return result

    result["completed"] = True
    page = response["query"]["search"][0]
    result["title"] = page["title"]
    # result["body"] = page["snippet"] # can see the code..
    pageid = page["pageid"]

    URL = "https://ru.wikipedia.org/w/api.php"

    PARAMS = {
        "action": "query",
        "format": "json",
        "pageids": pageid,
        "prop": "info",
        "inprop": "url"
    }

    response = requests.get(URL, params=PARAMS).json()
    pages = response["query"]["pages"]
    pprint(pages)

    for k, v in pages.items():
        result['url'] = v['canonicalurl']

    URL = "https://ru.wikipedia.org/w/api.php?"

    PARAMS = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "redirects": 1,
        "titles": result['title'],
        "exsectionformat": "plain"
    }
    response = requests.get(url=URL, params=PARAMS).json()
    pages = response["query"]["pages"]
    for k, v in pages.items():
        result['body'] = v['extract']

    # url change later
    return result
