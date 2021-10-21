import re

# search the json for the keyword
async def check_listings(connection, entries):
    # getting data out of json
    s = {x[1] for x in entries}
    s = "+".join(s)
    subreddits = await connection.subreddit(s)

    listings = []

    try:
        async for post in subreddits.new(limit=100):
            for entry in entries:
                subreddit = entry[1]
                if post.subreddit == subreddit:
                    # splits text depending if substring has text encased in quotes
                    keywords = re.split(r'\"([^\"]+)\"|(\b[^\s]+\b)', entry[2])

                    # turning subreddit text into lowercase to make searching case insensitive
                    lc_title = post.title.lower()
                    lc_body = post.selftext.lower()

                    # if all words from the database are in the reddit post
                    # the string is split containing None, "", and spaced chars, if those are found return True since they
                    # do not affect the ability to find the string in the reddit post
                    if all((x == None or x == "" or x.isspace()) or (x.lower() in lc_title or x.lower() in lc_body) for x in keywords):
                        # checking if we have not seen the post before
                        if float(post.created_utc) > float(entry[3]):
                            url = "https://redd.it/{}".format(post.id)
                            tup = (entry[0], entry[1], entry[2], url, post.created_utc, post.title, post.selftext)
                            listings.append(tup)
    except:
        return [] 

    return listings 
