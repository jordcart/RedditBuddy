# search the json for the keyword
async def check_listings(connection, entries):
    # getting data out of json
    s = {x[1] for x in entries}
    s = "+".join(s)
    subreddits = await connection.subreddit(s)

    listings = []

    print("starting loop")
    async for post in subreddits.new(limit=100):
        for entry in entries:
            subreddit = entry[1]
            if post.subreddit == subreddit:
                keywords = entry[2].split(',')
                # if all words from the database are in the reddit post
                if all(x in post.title or x in post.selftext for x in keywords):
                    # checking if we have not seen the post before
                    if float(post.created_utc) > float(entry[3]):
                        url = "https://redd.it/{}".format(post.id)
                        tup = (entry[0], entry[1], entry[2], url, post.created_utc)
                        listings.append(tup)
    print("finished loop")

    return listings 
