# Publiscord
[![Library-discord.py](https://img.shields.io/badge/Python-3.7-3778ae?logo=Python&logoColor=ffffff)](https://python.org)
[![Main Library-discord.py](https://img.shields.io/badge/Main%20Library-discord.py-fecc34?logo=pypi&logoColor=ffffff)](https://github.com/Rapptz/discord.py)

# Overview
Automatically publish news. Library for discord.py extension.    

# Install
Python 3 or higher is required.    
```cmd
# Linux/OS X
$ python -m pip install -U publiscord

# Windows
> py -3 -m pip install -U publiscord
```    

# Example
Automatically publish news.    
```py
import discord
from discord.ext import commands

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)


bot.load_extension('publiscord')


bot.run("token")
```
