import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # checking if there is no message guild, in other words private dm
    if not message.guild:
        if message.content.startswith('hi'):
            await message.channel.send('Hello!')

client.run(TOKEN)

