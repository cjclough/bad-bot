# -*- coding: utf-8 -*-
import asyncio
import discord
import json
import random
import re
import requests
import urllib

from discord.ext import commands
from PIL import Image
from io import BytesIO

# set config variables
with open("./config/config.json") as cfg:
    config = json.load(cfg)

token = config["token"]
api_key = config["key"]

bot = commands.Bot(command_prefix='.')

#----------FUNCTIONS----------#
def select_period(period):
    if period == 'weekly' or period == 'week' or period == 'w':
        return '7day'
    elif period == 'monthly' or period == 'month' or period == 'm':
        return '1month'
    elif period == 'yearly' or period == 'year' or period == 'y':
        return '12month'
    elif period == 'overall' or period == "all" or period == 'a':
        return 'overall'


def select_limit(size):
    l, w = size.split('x')
    return str(int(l) * int(w))


async def update_now_playing():
    await bot.wait_until_ready()
    while not bot.is_closed():
        track = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key='+api_key+'&user=networkdrift'+'&limit=1&format=json').json()
        title = track['recenttracks']['track'][0]['name']
        artist = track['recenttracks']['track'][0]['artist']['#text']
        await bot.change_presence(activity=discord.Game(artist + ' – ' + title))
        await asyncio.sleep(5)


#----------EVENTS----------#
# log in status
@bot.event
async def on_ready():
    print('logged in.')

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author == bot.user:
        return

    if "john" in message.content.lower():
        emoji = (bot.get_emoji(439200062795415562))
        await message.channel.send(emoji)


#----------COMMANDS----------#
# greet
@bot.command()
async def greet(ctx):
    await ctx.send("Hello, world.")


# roll dice
@bot.command()
async def roll(ctx, r: str):
    # split into usable params
    params = r.split('d')
    try:
        multiplier = int(params[0])
        sides = int(params[1])
    except ValueError:
        await ctx.send("the parameters you sent are invalid.")
        return

        roll = 0
        for x in range(multiplier):
            roll += random.randint(1, sides)
        
        if multiplier > 1:
            await ctx.send("the dice are cast... " + "**"+str(roll)+"**!")
        else:
            await ctx.send("the die is cast..." + "**"+str(roll)+"**!")
       

# get current scrobble
@bot.command(pass_context=True)
async def fm(ctx):
    with open('./config/users.json', 'r+') as u:
        users = json.load(u)

    try:
        sender = users[str(ctx.message.author.id)]
    except KeyError:
        await ctx.send("you have not supplied your last.fm username. to do so, use .fmset.")
        return

    track = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key='+api_key+'&user='+sender+'&limit=1&format=json').json()

    title = track['recenttracks']['track'][0]['name']
    album = track['recenttracks']['track'][0]['album']['#text']
    artist = track['recenttracks']['track'][0]['artist']['#text']
    artwork = track['recenttracks']['track'][0]['image'][2]['#text']

    # make the embed
    embed = discord.Embed(description=" ", color=0x535660)
    embed.add_field(name=title, value="\nfrom " + "*"+album+"*"+"\nby " + artist, inline=True)
    embed.set_author(name= str(ctx.message.author.display_name)+" on last.fm", url="https://www.last.fm/user/"+sender, icon_url=ctx.message.author.avatar_url)

    if artwork:
        embed.set_thumbnail(url=artwork)

    await ctx.send(embed=embed)

# generate a chart of the user's top albums
@bot.command(pass_context=True)
async def fmchart(ctx, period="weekly", size="3x3"):
    with open('./config/users.json', 'r+') as u:
        users = json.load(u)

    sender = users[str(ctx.message.author.id)]
    albums = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&api_key='+api_key+'&user='+sender+'&limit='+select_limit(size)+'&period='+select_period(period)+'&format=json').json()

    per_row = int(size[:size.find('x')])
    per_col = int(size[size.find('x')+1:])
    canvas = Image.new('RGB', (per_row*300,per_col*300))

    covers = [album['image'][3]['#text'] for album in albums['topalbums']['album']]
    offset_x = 0
    offset_y = 0
    for cover in covers:
        if offset_x == canvas.width:
            offset_x = 0
            offset_y += 300
        try:
            image = Image.open(BytesIO(requests.get(cover).content))
            canvas.paste(image, (offset_x, offset_y))
        except requests.exceptions.MissingSchema:
            pass
        offset_x += 300

        if canvas.width > 1500:
            canvas.resize((1500, 1500))

    buffer = BytesIO()
    canvas.save(buffer, format='jpeg', quality=100)
    buffer = buffer.getvalue()
    await ctx.send('', file=discord.File(fp=buffer, filename='chart.jpg'))

    # make the embed
    embed = discord.Embed(description=" ", color=0x535660)
    embed.add_field(name=ctx.message.author.display_name+'\'s last.fm chart', value=period+', '+size, inline=True)
    embed.set_author(name= str(ctx.message.author.display_name)+" on last.fm", url="https://www.last.fm/user/"+sender, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


# set last.fm username
@bot.command(pass_context=True)
async def fmset(ctx, username=None):

    if username is None:
        await ctx.send("you did not provide a username.")
        return

    user = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user='+username+'&api_key='+api_key+'&format=json').json()

    if 'error' in user:
        await ctx.send('that user doesn\'t exist on last.fm. did you make a typo?')
        return

    with open('./config/users.json', 'r') as u:
        users = json.load(u)

    users[str(ctx.message.author.id)] = str(username)

    with open("./config/users.json", "w") as u:
        json.dump(users, u, indent= 4, sort_keys=True)

    await ctx.send('set ' + ctx.message.author.name + '\'s last.fm username to ' + username + '.')


# get first result from youtube query
@bot.command()
async def yt(ctx):
    query = urllib.parse.quote(ctx.message.content[4:])
    search = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
    results = re.findall(r'href=\"\/watch\?v=(.{11})', search.read().decode())
    await ctx.send("http://www.youtube.com/watch?v=" +  results[0])


# log out
@bot.command()
# @is_owner()
async def quit(ctx):
    await bot.logout()

bot.loop.create_task(update_now_playing())

bot.run(token)
