import discord
import json
import random

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
	
@bot.command()
async def rand(ctx):
	await ctx.send(random.randint(0,100))

@bot.command()
async def todo(ctx):
    embed = discord.Embed(title="TODO", description="Tasks:", color=0xeee657)
    embed.add_field(name=".np username", value="--> scrape last scrobble from username", inline=False)    
    await ctx.send(embed=embed)

bot.run(token)
