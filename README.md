# redditnotifs

### Installation
```bash
git clone https://github.com/jordcart/redditnotifs.git
cd redditnotifs
pip3 install -r requirements.txt
```

### Setup
* You are going to need a .env file, which looks something like this:
```
# fill in with your own info
# used for connecting to the discord bot
DISCORD_TOKEN=''
# used for connecting to the database
USERNAME=''
DATABASE=''
PASSWORD=''
HOST=''
PORT=''
```
* You will also need a praw.ini file in order to make requests to the Reddit API. Information on that can be found here: https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html
* Upon setting up these two files, you will be able to run the bot:
```python
python3 bot.py
```



