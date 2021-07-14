import os
import reddit 
import database
import time
import discord
from discord.ext import commands
from threading import Thread
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
        current_time = time.time()
        search_string = ",".join(search)
        result = database.add_to_database(connection, cursor, ctx.message.author.id, subreddit, search_string, current_time)
        if result == 1:
            await ctx.send("Now tracking the term **{}** in **r/{}**".format(search_string, subreddit))
        elif result == 0:
            await ctx.send("You have already set that term, check your terms with **!list**")


@bot.command()
async def delete(ctx):
    if not ctx.guild:
        await ctx.send('Hello!')

@bot.command()
async def list(ctx):
    if not ctx.guild:
        entries = database.get_all_entries(connection, cursor, ctx.message.author.id)
        num_entries = len(entries)
        message = "**You currently have " + str(num_entries) +" search terms:**\n"
        for subreddit, search in entries:
            message += "r/"+subreddit+"  -  "+search+"\n"

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

def search_loop():
    #change to while database is not empty
    while(1):
        #reddit.check_new_listings('mechmarket', 'keyboard')
        time.sleep(3)
        pass

if __name__ == "__main__":
    # starting scraper on seperate thread
    scrape = Thread(target=search_loop)
    scrape.start()
    # starting bot on main thread
    bot.run(TOKEN)




