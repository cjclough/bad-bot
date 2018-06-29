import discord
import json
import random
import re
import urllib

from discord.ext import commands


# set config variables
with open("config.json") as cfg:
    config = json.load(cfg)
	
token = config["token"]
	
bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print('Logged in as') 
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def greet(ctx):
    await ctx.send("Hello, world.")

# get first result from youtube query
@bot.command()
async def yt(ctx):
    query = urllib.parse.quote(ctx.message.content[4:])
    search = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
    results = re.findall(r'href=\"\/watch\?v=(.{11})', search.read().decode())
    await ctx.send("http://www.youtube.com/watch?v=" +  results[0])

# task list
@bot.command()
async def todo(ctx):
    embed = discord.Embed(title="TODO", description="Tasks:", color=0xeee657)
    embed.add_field(name=".np username", value="--> scrape last scrobble from username", inline=False)    
    await ctx.send(embed=embed)

bot.run(token)