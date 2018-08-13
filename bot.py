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
    await bot.change_presence(activity=discord.Game("in API hell"))

@bot.event
async def on_message(message):  
    await bot.process_commands(message)

    if message.content.lower().startswith("this is so sad"):
        await message.channel.send("alexa play despacito")

    if message.content.lower().startswith("ping"):
        await message.channel.send("pong!")

    if "john" in message.content.lower():
        emoji = (bot.get_emoji(439200062795415562))
        await message.channel.send(emoji)

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
        await ctx.send("ERROR: invalid params")
    else:
        roll = 0

        for x in range(multiplier):
            roll += random.randint(1,sides)
        
        if multiplier > 1:
            await ctx.send("The dice are cast... " + "**"+str(roll)+"**!")
        else:
            await ctx.send("The die is cast..." + "**"+str(roll)+"**!") 
       

# get current scrobble
@bot.command()
async def np(ctx):
    #open users.json
    with open('users.json', 'r+') as users:
        names = json.load(users)

    sender = names[str(ctx.message.author)]
    if sender:
        # data fields 
        track_title = " "
        track_album = " "
        track_artist = " "
        album_cover = " "

        user = network.get_user(sender)
        
        track = user.get_now_playing()
        if track == None:
            track = user.get_recent_tracks(cacheable=False,limit=2)[0]
            track_title = str(track.track.title)

            try: 
                track_album = str(track.album)
                pass
            except AttributeError:
                track_album = "[unknown]"
                pass

            track_artist = str(track.track.artist)

            try: 
                album_cover = track.track.get_cover_image(size=1)
                pass
            except AttributeError:
                # todo: make filler cover
                pass 
        else:
            track_title = str(track.title)

            try: 
                track_album = str(track.get_album().get_name())
                pass
            except AttributeError:
                track_album = "[unknown]"
                pass

            track_artist = str(track.artist)

            try: 
                album_cover = track.get_album().get_cover_image(size=1)
                pass
            except AttributeError:
                # todo: make filler cover
                pass 

        # make the embed
        embed = discord.Embed(title="Now Playing",description=" ", color=0x535660)
        embed.add_field(name=track_title,value="\nfrom " + "*"+track_album+"*"+"\nby " + track_artist,inline=True)

        if album_cover:
            embed.set_thumbnail(url=album_cover)                

        await ctx.send(embed=embed)       
    else:
        await ctx.send("No valid username found. To set your username, use .npset")

# set last.fm username
@bot.command()
async def npset(ctx):
    try:
        user = network.get_user(ctx.message.content[7:])
        user.get_registered()
        pass
    except pylast.WSError:
        await ctx.send("\nInvalid username.")
        pass
    else:
        with open('users.json', 'r') as users:
            names = json.load(users)

        names[str(ctx.message.author)] = str(user)

        with open("users.json", "w") as users:
            json.dump(names, users)

        await ctx.send("Username set.")

@bot.command()
async def weekly(ctx, t: str):
    with open('users.json', 'r+') as users:
        names = json.load(users)

    sender = names[str(ctx.message.author)]

    if sender:
        user = network.get_user(sender)

        if t == "albums":
            query = user.get_top_albums(period='7day', limit=5)
        elif t == "tracks":
            query = user.get_top_tracks(period='7day', limit=5)
        elif t == "artists":
            query = user.get_top_artists(period='7day', limit=5)
        else:
            await ctx.send("Invalid parameter.")
            return

        output = "**Top 5 "+t.capitalize()+" (weekly):**"
        
        for x in range(len(query)):
                output+="\n"+str(x+1)+". "+str(query[x].item)


        await ctx.send(output)

    else:
        await ctx.send("No valid username found. To set your username, use .npset")       


# get first result from youtube query
@bot.command()
async def yt(ctx):
    query = urllib.parse.quote(ctx.message.content[4:])
    search = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
    results = re.findall(r'href=\"\/watch\?v=(.{11})', search.read().decode())
    await ctx.send("http://www.youtube.com/watch?v=" +  results[0])

bot.run(token)