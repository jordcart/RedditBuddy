import requests
import json
import time

# search the json for the keyword
def search_keyword(keyword, json):
    # getting data out of json
    found = []
    listings = json["data"]["children"]
    for obj in listings:
        title = obj["data"]["title"]
        desc = obj["data"]["selftext"]
        if keyword in desc or keyword in title:
            found.append(obj["data"]["url"])
    return found

def check_new_listings(subreddit, keyword):
    url = 'https://reddit.com/r/' + subreddit + '/new.json'
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'}
    r = requests.get(url, headers=headers)
    json_object = r.json()
    found = search_keyword(keyword, json_object)
    print(time.time())
