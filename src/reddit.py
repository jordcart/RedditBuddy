# search the json for the keyword
async def check_listings(connection, entries):
    # getting data out of json
    s = {x[1] for x in entries}
    s = "+".join(s)
    subreddits = await connection.subreddit(s)

    listings = []

    async for post in subreddits.new(limit=100):
        for entry in entries:
            subreddit = entry[1]
            if post.subreddit == subreddit:
                keywords = entry[2].split(',')
                # if all words from the database are in the reddit post
                if all(x in post.title or x in post.selftext for x in keywords):
                    # checking if we have not seen the post before
                    last_time = float(entry[3])
                    post_time = float(post.created_utc)
                    if post.created_utc > last_time:
                        url = "https://redd.it/{}".format(post.id)
                        tup = (entry[0], entry[1], entry[2], url, post.created_utc)
                        listings.append(tup)
    return listings 

#def check_listings(keyword, json):
    #found = []
    #keyword = keyword.lower()
    #listings = json["data"]["children"]
    #for obj in listings:
    #    title = obj["data"]["title"].lower()
    #    desc = obj["data"]["selftext"].lower()
    #    if keyword in desc or keyword in title:
    #        user_id = obj["data"]["id"]
    #        time_created = obj["data"]["created_utc"]
    #        ret = (user_id, time_created)
    #        found.append(ret)
    #return found

#def check_new_listings(subreddit, keyword):
#    url = 'https://reddit.com/r/' + subreddit + '/new.json'
#    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'}
#    r = requests.get(url, headers=headers)
#    json_object = r.json()
#    found = search_keyword(keyword, json_object)
#    return found
