#!/usr/bin/env/python 3
import os
import reddit 
import database
import time
import asyncpraw
import discord
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
cursor = connection.cursor() # get database cursor
# connect to discord
bot = commands.Bot(command_prefix='!', help_command=None, case_insensitive=True)

# connect to reddit api
rc = asyncpraw.Reddit('bot-1')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(ctx):
    channel = bot.get_channel(ctx.channel.id)
    messages = await ctx.channel.history(limit=5).flatten()

    # this means they are a new user, add to db
    if len(messages) == 1:
        database.add_new_user(connection, cursor)
    await bot.process_commands(ctx)


# help command
@bot.command(name="help", aliases=["h", "?", "commands"])
async def help(ctx):
    if not ctx.guild:
        file = open("help.txt")
        line = file.read()
        file.close()
        await ctx.send(line)

# add new listing to database
@bot.command()
async def add(ctx, sub, *search):
    if not ctx.guild:
        sub = sub.lower()
        exists = True
        sub = sub.replace('r/', '').replace('\'', '')

        if len(search) == 0:
            await ctx.send("Incorrect usage of command, make sure it is formatted like this: " +
                    "`!add (subreddit) (search term)`")
            return

        try:
            subreddit = [s async for s in rc.subreddits.search_by_name(sub, exact=True)]
        except Exception as e:
            exists = False

        if exists == True:
            current_time = int(time.time())
            if len(search) == 1:
                # if one string
                if " " in search[0]:
                    search_string = "\"" + search[0] + "\""
                else:
                    search_string = search[0]

                # case search term is empty string
                if search_string == "":
                    search_string = " "
            else:
                search_string = ""
                for x in search:
                    if " " in x:
                        search_string += (("\"" + x + "\"") + " ")
                    else:
                        search_string += (x + " ")
                search_string = search_string[:-1]

            result = database.add_to_database(connection, cursor, ctx.message.author.id, sub, search_string, current_time)
            if result == True:
                # send user a message
                if search_string == " ":
                    await ctx.send("Now tracking all new posts in **r/{}**.".format(sub))
                else:
                    await ctx.send("Now tracking the keyword **{}** in **r/{}**.".format(search_string, sub))

                # update status for bot description
                await set_status() 
                # update statistics database
                database.add_listing(connection, cursor)
            elif result == False:
                await ctx.send("You have already set that term, check your terms with **!list**.")
        if exists == False:
            await ctx.send("The subreddit **{}** doesn't exist. Please try again.".format(sub))


@bot.command()
async def delete(ctx, subreddit, *search):
    if not ctx.guild:
        # checking if command was input correctly
        if len(search) == 0:
            await ctx.send("Incorrect usage of command, make sure it is formatted like this: " +
                    "`!delete (subreddit) (search term)`")
            return

        user_id = ctx.message.author.id
        subreddit = subreddit.replace("r/", "")

        # checking if there is only one search term
        if len(search) == 1:
            # case where there are multiple search terms surrounded by quotes
            if " " in search[0]:
                search_string = "\"" + search[0] + "\""
            # case where it is actually one search term 
            else:
                search_string = search[0]

            if search_string == "":
                search_string = " "
        # case where there is more than one search term
        else:
            search_string = ""
            for x in search:
                if " " in x:
                    search_string += ("\"" + x + "\"") + " "
                else:
                    search_string += x + " "
            search_string = search_string[:-1]

        result = database.remove_from_database(connection, cursor, user_id, subreddit, search_string)
        if result == True:
            if search_string == " ":
                await ctx.send("No longer tracking all new posts in **r/{}**.".format(subreddit))
            else:
                await ctx.send("No longer tracking the keyword **{}** in **r/{}**.".format(search_string, subreddit))
            await set_status()
        elif result == False:
            await ctx.send("The term **{}** with the subreddit **r/{}** does not exist in the database.".format(search_string, subreddit))

@bot.command()
async def deleteall(ctx):
    if not ctx.guild:
        user_id = ctx.message.author.id
        result = database.delete_all_user_entries(connection, cursor, user_id)
        if result == True:
            await ctx.send("All entries have been deleted.")
            await set_status()
        elif result == False:
            await ctx.send("An error occured while while deleting your entries. Please try again.")

@bot.command()
async def list(ctx):
    if not ctx.guild:
        entries = database.get_user_entries(connection, cursor, ctx.message.author.id)
        num_entries = len(entries)
        message = "**You currently have {} search terms:**\n".format(str(num_entries))
        for subreddit, search, found in entries:
            if search == " ":
                message += "r/{} - \"\" - {} listings found.\n".format(subreddit, found)
            else:
                message += "r/{} - {} - {} listings found.\n".format(subreddit, search, found)

        await ctx.send(message)

@bot.event
async def on_command_error(ctx, error):
    if ctx.command == add:
        print(error)
        await ctx.send("Incorrect usage of command, make sure it is formatted like this: " +
                "`!add (subreddit) (search term)`")
    elif ctx.command == delete:
        print(error)
        await ctx.send("Incorrect usage of command, make sure it is formatted like this: " +
                "`!delete (subreddit) (search term)`")
    elif ctx.command == list:
        print(error)
    elif ctx.command == None:
        await ctx.send("The message sent is not a command, the available commands are: (!help, !add, !delete, !list)\n" + 
                        "If you need further help on how to use these commands type !help")

@tasks.loop(seconds=10.0)
async def search_loop():
    global connection
    global cursor
    # check for database connection
    result = database.verify_db_connection(connection, cursor)
    # if not connected, reconnect before continuing loop
    if (result == -1):
        connection = database.connect_to_database(USER, DATABASE, PASSWORD, HOST, PORT)
        cursor = connection.cursor() # get database cursor

    entries = database.get_all_entries(connection, cursor)
    # get a list containing all of the found listings
    if entries != []:
        listings = await reddit.check_listings(rc, entries)

        if listings != []:
            database.add_found_listings(connection, cursor, len(listings))

        # iterate on list and send dms to people
        max_time = 0
        for l in listings:
            user_id = l[0]; subreddit = l[1]; keyword = l[2]; url = l[3]; new_time = l[4]; title = l[5]; desc = l[6]

            # shortening description from reddit post if its too long
            if len(desc) > 200:
                desc = desc[:200] + ". . ."

            if len(title) > 200:
                title = title[:200] + ". . ."

            user = await bot.fetch_user(user_id)
            embed=discord.Embed(title=title, description=desc, color=0x45beff)

            # if keyword is empty, send different notification message 
            if keyword == " ":
                await user.send("New post in **r/{}** - {}". format(subreddit, url), embed=embed)
            # regular message
            else:
                await user.send("Found **{}** in **r/{}** - {}". format(keyword, subreddit, url), embed=embed)
            max_time = max(new_time, max_time)
            database.update_entry(connection, cursor, user_id, subreddit, keyword, max_time)

@search_loop.before_loop
async def before_search():
    print('waiting for bot to start...')
    await bot.wait_until_ready()

async def set_status():
    num_users = database.get_number_of_unique_users(connection, cursor)[0][0]
    num_entries = database.get_number_of_entries(connection, cursor)[0][0]
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="{} terms for {} users".format(num_entries, num_users)))

if __name__ == "__main__":
    # starting scraper in seperate coroutine 
    search_loop.start()
    # starting bot on main thread
    bot.run(TOKEN)
