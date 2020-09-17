import asyncio
import time
import json
import os

import discord
from discord.ext import commands
from discord.ext.tasks import loop              
from discord.ext.commands import when_mentioned_or

pd = os.path.dirname(__file__)

with open(pd + "\data\config.json", "r") as file: 
    data = json.loads(file.read())
    token = data["token"]   
    default_prefix = data["default_prefix"]
    
def get_prefix(bot, message): 
    if message.guild is not None: 
        with open(pd + "\data\prefixes.json", "r") as file:     
            data = json.load(file)
            server_id = str(message.guild.id)
            prefix = data.get(server_id, default_prefix)
            
        return when_mentioned_or(prefix)(bot, message)
    else : 
        pass
        
client = commands.Bot(command_prefix = get_prefix, case_insensitive = True)
    
client.remove_command("help")
extensions = ["cogs.error_handler", 
              "cogs.config_cog",
              "cogs.help_cogs",
              "cogs.music_cogs",
              
              ]    

@client.event 
async def on_ready(): 
    print(f"Logged in as {client.user}\n\n")
    
    #loading extensions 
    for extention in extensions: 
        print(f"Loading {extention}")
        client.load_extension(extention)
        
    print("Changing presence!!")
    await change_presence_loop.start()
    print("\n\nBot is ready!!")
    

@client.event 
async def on_guild_remove(guild): 
    
    with open(pd + "\data\prefixes.json", "r") as file: 
        data = json.load(file)
        try : 
            data.pop(str(guild.id))
        except : 
            pass
            
    with open(pd + "\data\prefixes.json", "w") as file: 
        json.dump(data, file)
        
@loop(seconds = 5)
async def change_presence_loop():
    """
        A background loop handler which uses commands.ext.tasks.loop couroutine.
        ------------------------------------------------------------------------
        status :
            type - Dictionary
            keys - Keys representing status type (from game, music, stream or movie)
            values - representing activity name.

        seconds :
            type - int
            Change this to change the iteration time between two sucessive status change.
    """

    servers = len(client.guilds)
    members = sum([s.member_count for s in client.guilds])
    seconds = 5

    status = {
        # "game": f"High Quality Music",
        # "music": f"@{client.user.display_name} help | v2.0",
        # "movie": f"{len(client.guilds)} servers",
        # # "stream": "Khopdi Noob"
    }

    for key, value in zip(status.keys(), status.values()):
        if key == "game":
            await client.change_presence(
                activity = discord.Game(name = value)
                )

        elif key == "music":
            await client.change_presence(
                activity = discord.Activity(type = discord.ActivityType.listening,
                    name = value)
            )

        elif key == "movie":
            await client.change_presence(
                activity = discord.Activity(type = discord.ActivityType.watching,
                    name = value)
            )

        if key == "stream":
            await client.change_presence(
                activity = discord.Streaming(name = value,
                url = "https://www.twitch.tv/fadeofficial")
                )

        else:
            pass

        await asyncio.sleep(seconds)
        
@client.command()
async def ping(cont): 
     await cont.channel.send('> **Ping**: {0} ms'.format(round(client.latency * 1000)))
        
"""
    Running our bot
"""
        
print("Logging itno the bot!!")
client.run(token)
