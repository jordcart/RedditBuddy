#!/usr/bin/env/python 3
import os
import reddit 
import database
import time
import asyncpraw
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
USER = os.getenv('USERNAME')
DATABASE = os.getenv('DATABASE')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

connection = database.connect_to_database(USER, DATABASE, PASSWORD, HOST, PORT)
cursor = connection.cursor()
bot = commands.Bot(command_prefix='!', help_command=None)

reddit_connection = asyncpraw.Reddit('bot-1')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def help(ctx):
    if not ctx.guild:
        await ctx.send('Hello!')

@bot.command()
async def add(ctx, subreddit, *search):
    if not ctx.guild:
        current_time = int(time.time())
        search_string = ",".join(search)
        result = database.add_to_database(connection, cursor, ctx.message.author.id, subreddit, search_string, current_time)
        if result == True:
            await ctx.send("Now tracking the **\"{}\"** in **r/{}**".format(search_string, subreddit))
        elif result == False:
            await ctx.send("You have already set that term, check your terms with **!list**")


@bot.command()
async def delete(ctx, subreddit, search):
    if not ctx.guild:
        user_id = ctx.message.author.id
        result = database.remove_from_database(connection, cursor, user_id, subreddit, search)
        if result == True:
            await ctx.send("No longer tracking **\"{}\"** in **r/{}**.".format(search, subreddit))
        elif result == False:
            await ctx.send("The term **\"{}\"** doesnt exist in the database.".format(search))

@bot.command()
async def list(ctx):
    if not ctx.guild:
        entries = database.get_user_entries(connection, cursor, ctx.message.author.id)
        num_entries = len(entries)
        message = "**You currently have {} search terms:**\n".format(str(num_entries))
        for subreddit, search, found in entries:
            message += "r/{} - \"{}\" - {} listings found.\n".format(subreddit, search, found)

        await ctx.send(message)

@bot.event
async def on_command_error(ctx, error):
    if ctx.command == add:
        print(error)
        await ctx.send("Incorrect usage of command, make sure it is formatted like this: " +
                "`!add (subreddit) (search term)`")
    elif ctx.command == delete:
        print(error)
    elif ctx.command == list:
        print(error)
    elif ctx.command == None:
        await ctx.send("The message sent is not a command, the available commands are: (!help, !add, !delete, !list)\n" + 
                        "If you need further help on how to use these commands type !help")

@tasks.loop(seconds=10.0)
async def search_loop():
    entries = database.get_all_entries(connection, cursor)
    # get a list containing all of the found listings
    listings = await reddit.check_listings(reddit_connection, entries)
    print(listings)
    
    # iterate on list and send dms to people
    max_time = 0
    for l in listings:
        user_id = l[0]; subreddit = l[1]; keyword = l[2]; url = l[3]; new_time = l[4]
        user = await bot.fetch_user(user_id)
        await user.send("Found **\"{}\"** in **r/{}** - {}". format(keyword, subreddit, url))
        max_time = max(new_time, max_time)
        database.update_entry(connection, cursor, user_id, subreddit, keyword, max_time)

@search_loop.before_loop
async def before_search():
    print('waiting for bot to start...')
    await bot.wait_until_ready()

if __name__ == "__main__":
    # starting scraper in seperate coroutine 
    search_loop.start()
    # starting bot on main thread
    bot.run(TOKEN)
