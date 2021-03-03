# -*- coding: utf-8 -*-

# bot.py
import os
import random
import pprint
import itertools
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import investmentManager as im
import priceFetcher as pf

from beratQuotes import quotes
from treasury import TREASURE

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


def split_dict(x, chunks):      
    i = itertools.cycle(range(chunks))       
    split = [dict() for _ in range(chunks)]
    for k, v in x.items():
        split[next(i)][k] = v
    return split

'''
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("**Invalid command.** Try using **`help`** to figure out commands!")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in **all** required arguments.')
    else:
        await ctx.send('There is a problem, please check the terminal logs!')
'''

@bot.event
async def on_ready():
    check_prices.start()
    print(f'{bot.user.name} has connected to Discord!')
    

@bot.command(name='sayın_bakanım', help='Sayın bakanım size bir söz söyler.')
async def portfolio_talks(ctx):
    randomQuotes = quotes['random']

    response = random.choice(randomQuotes)
    await ctx.send(response)

@bot.command(name='sell', help='Sell an instrument (Remove or decrease the amount)')
async def sell(ctx, amount:float, instrumentName:str, instrumentType:str):
    issuedBy = str(ctx.message.author)
    instrumentName = instrumentName.lower()
    instrumentType = instrumentType.lower()
    if instrumentType not in ["fx", "gold", "fund", "coin"]:
        message = "Invalid instrument type, please choose fx, coin or gold for instrument type."
        await ctx.send(message)
    try:
        test = TREASURE[issuedBy]
    except:
        TREASURE[issuedBy] = {"fx":{}, "gold":{}, "fund": {}, "coin":{}}
    try:
        oldAmount = TREASURE[issuedBy][instrumentType][instrumentName]
        TREASURE[issuedBy][instrumentType][instrumentName] -= amount
        if TREASURE[issuedBy][instrumentType][instrumentName] < 0:
            message = "There might be a typo! Your current {0} balance is {1}, you cannot sell {2} {0} - **Not updated.**".format(instrumentName, oldAmount, amount)
            TREASURE[issuedBy][instrumentType][instrumentName] = oldAmount
            await ctx.send(message)
        message = "({0}) {1} balance goes from {2} to {3}".format(issuedBy, instrumentName, oldAmount, str(TREASURE[issuedBy][instrumentName]))
        im.update_treasury()
        await ctx.send(message)
    except:
        message = "Could not sell something that you do not own!"
        await ctx.send(message)

@bot.command(name='buy', help='Buy an instrument (Add or increase the amount)')
async def buy(ctx, amount:float, instrumentName:str, instrumentType:str):
    oldAmount = 0
    issuedBy = str(ctx.message.author)
    instrumentName = instrumentName.lower()
    instrumentType = instrumentType.lower()

    if instrumentType not in ["fx", "gold", "fund", "coin"]:
        message = "Invalid instrument type, please choose fx, coin or gold for instrument type."
        await ctx.send(message)
    try:
        test = TREASURE[issuedBy]
    except:
        TREASURE[issuedBy] = {"fx":{}, "coin":{}, "gold":{}}
    try:
        oldAmount = TREASURE[issuedBy][instrumentType][instrumentName]
        TREASURE[issuedBy][instrumentType][instrumentName] += amount
    except:
        TREASURE[issuedBy][instrumentType][instrumentName] = amount

    message = "({0}) {1} balance goes from {2} to {3}".format(issuedBy, instrumentName, oldAmount, str(TREASURE[issuedBy][instrumentName]))
    im.update_treasury()
    await ctx.send(message)

@bot.command(name='export_portfolio', help='Export current status of the portfolio.')
async def export_portfolio(ctx, *, checkALL="all"):
    if checkALL == "all":
        fName = im.export_portfolio("all")
        await ctx.send(file=discord.File(fName))
        message = "Total portfolio is exported"
    else:
        issuedBy = str(ctx.message.author)
        fName = im.export_portfolio(issuedBy)
        await ctx.send(file=discord.File(fName))
        message = issuedBy + "'s portfolio is exported."
    await ctx.send(message)

@bot.command(name='report_portfolio', help='Report and print the current status of the treasury.')
async def report_portfolio(ctx, *, checkALL="all"):
    message = "The Mighty Treasure:"
    await ctx.send(message)
    message = pprint.pformat(im.report_portfolio(checkALL), sort_dicts=False)
    await ctx.send(message)
    await ctx.send("Reporting completed!")

@bot.command(name='report_coin_wallet', help='Reports the current status of the binance wallet.')
async def report_coin_wallet(ctx, *, currency="USDT"):
    issuedBy = str(ctx.message.author)
    walletStatus = im.report_coin_wallet(issuedBy, currency)
    message = issuedBy + "'s wallet status:"
    await ctx.send(message)
    splittedFormat = split_dict(walletStatus, 5)
    for s in splittedFormat:
        message = pprint.pformat(s)
        await ctx.send(message)
    await ctx.send("Reporting completed!")

@bot.command(name='report_coin_profit', help='Reports the current status of the binance wallet.')
async def report_coin_profit(ctx, *, currency="USDT"):
    issuedBy = str(ctx.message.author)
    profits = im.report_coin_profits(issuedBy, currency)
    message = "Profit History:\n"
    await ctx.send(message)
    splittedFormat = split_dict(profits, 5)
    for s in splittedFormat:
        if s != {}:
            message = pprint.pformat(s)
            await ctx.send(message)
    await ctx.send("Reporting completed!")

@tasks.loop(seconds=1800)
async def check_prices():
    pf.update_prices("isbank")

bot.run(TOKEN)