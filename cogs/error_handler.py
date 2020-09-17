import os
import json

import discord 
from discord import Embed
from colorama import Fore
from discord.ext import commands 

class Error_Handling(commands.Cog): 
        
    def __init__(self, bot): 
        """Initilializing our class"""
        
        self.bot = bot
        self.embed_colour = discord.Color.from_rgb(255, 0, 0)
        
    def get_prefix(self, id): 
        
        with open(os.path.dirname(__file__) + "\..\data\prefixes.json", "r") as file: 
            data = json.loads(file.read())
            
        prefix = data.get(str(id))
        return prefix
        
    @commands.Cog.listener()
    async def on_command_error(self, cont, error): 
        """Event to handle errors in **Commands**"""
        
        prefix = self.get_prefix(cont.guild.id)
        
        if isinstance(error, commands.CommandNotFound): 
            pass
            
        elif isinstance(error, commands.CheckFailure): 
            embed = Embed(title = "Error", colour = self.embed_colour, 
                            description = "You are not allowed to do that!!")
            await cont.channel.send(embed = embed)
                            
        elif isinstance(error, commands.MissingRequiredArgument): 
            embed = Embed(title = "Error", colour = self.embed_colour, 
                            description = f"Invalid command format: Missing some arguments. Please type `{prefix}help` to check correct syntax.")
            await cont.channel.send(embed = embed)
            
        elif isinstance(error, commands.CommandOnCooldown):
            if cont.author.id == 723230901622014017: 
                await cont.channel.send("This command is on cooldown! But hey!! You are my owner :) **Reset cooldown**")
                cont.command.reset_cooldown(cont)
                await self.bot.process_commands(cont.message)
            else :
                embed = Embed(title = "Error", colour = self.embed_colour, 
                                description = "You can use this command again in **{round(error.retry_after//60)}m {round(error.retry_after%60)}s**")
                await cont.channel.send(embed = embed)
                
        elif isinstance(error, commands.BadArgument): 
            embed = Embed(title = "Error", colour = self.embed_colour, 
                            description = f"Invalid arguments passed. Please type `{prefix}help` to check correct way.")
            await cont.channel.send(embed = embed)
        
        elif isinstance(error, commands.BotMissingPermissions): 
            embed = Embed(title = "Error", colour = self.embed_colour, 
                            description = f"I am missing some permissions to do this task!")
            await cont.channel.send(embed = embed)
        
        else : 
            error_str = str(error)
            error = getattr(error, 'original', error)
            print(f"{Fore.RED}Error:: {Fore.YELLOW}{error_str}"+Fore.RESET)
            
def setup(bot): 
    bot.add_cog(Error_Handling(bot))
