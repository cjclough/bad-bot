import discord
import json
import pylast
import random
import re
import urllib

from discord.ext import commands


# set config variables
with open("config.json") as cfg:
    config = json.load(cfg)

token = config["token"]
api_key = config["key"]
api_secret = config["secret"]

# get pylast network object
network = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)

bot = commands.Bot(command_prefix='.')

# log in status
@bot.event
async def on_ready():
    print('Logged in as') 
    print(bot.user.name)
    print(bot.user.id)
    print('------')

# greet
@bot.command()
async def greet(ctx):
    await ctx.send("Hello, world.")

# get current scrobble or last scrobble
@bot.command()
async def np(ctx):
    if len(ctx.message.content) < 5:
        with open('users.json', 'r+') as users:
            names = json.load(users)
            sender = names[str(ctx.message.author)]
            if sender:
                user = network.get_user(sender)
                track = user.get_now_playing()
                if track:
                    embed = discord.Embed(title=":notes: Now playing :notes:", description=str(track.artist) + " - " + str(track.title), color=0x535660)
                    await ctx.send(embed=embed)
                else:
                    track = user.get_recent_tracks(limit=1)[0]
                    embed = discord.Embed(title=":notes: Last played :notes:", description=str(track.track.artist) + " - " + str(track.track.title), color=0x535660)
                    await ctx.send(embed=embed)
            else:
                await ctx.send("No valid username found. To set your username, use .npset")
    else:
        user = network.get_user(ctx.message.content[4:])
        track = user.get_now_playing()
        if track:
            embed = discord.Embed(title=":notes: Now playing :notes:", description=str(track.artist) + " - " + str(track.title), color=0x535660)
            await ctx.send(embed=embed)
        else:
            track = user.get_recent_tracks(limit=1)[0]
            embed = discord.Embed(title=":notes: Last played :notes:", description=str(track.track.artist) + " - " + str(track.track.title), color=0x535660)
            await ctx.send(embed=embed)

# set last.fm username
@bot.command()
async def npset(ctx):
    try:
        user = network.get_user(ctx.message.content[7:])
        user.get_registered()
        pass
    except pylast.WSError:
        await ctx.send("\nInvalid username. Try again.")
        pass
    else:
        with open('users.json', 'r') as users:
            names = json.load(users)

        names[str(ctx.message.author)] = str(user)

        with open("users.json", "w") as users:
            json.dump(names, users)

        await ctx.send("Username set.")

# get first result from youtube query
@bot.command()
async def yt(ctx):
    query = urllib.parse.quote(ctx.message.content[4:])
    search = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
    results = re.findall(r'href=\"\/watch\?v=(.{11})', search.read().decode())
    await ctx.send("http://www.youtube.com/watch?v=" +  results[0])

bot.run(token)