import os
import json

import discord 
from discord import Embed 
from discord.ext import commands 

class Config(commands.Cog): 
    def __init__(self, bot): 
        self.bot = bot 
        self.embed_colour = discord.Color.from_rgb(252, 3, 115)
        self.bot_name = bot.user.display_name
        self.bot_url = bot.user.avatar_url
        
    def get_prefix(self, id): 
        
        with open(os.path.dirname(__file__) + '\..\data\prefixes.json', "r") as file: 
            data = json.loads(file.read())
            
        with open(os.path.dirname(__file__) + '\..\data\config.json', "r") as file: 
            data = json.loads(file.read())
            default_prefix = data["default_prefix"]
            
        prefix = data.get(str(id), default_prefix)
        return prefix
                
    def set_prefix(self, id, new_prefix): 
        with open(os.path.dirname(__file__) + '\..\data\prefixes.json', "r") as file: 
            data = json.loads(file.read())
            data[str(id)] = new_prefix
        
        with open(os.path.dirname(__file__) + '\..\data\prefixes.json', "w") as file: 
            json.dump(data, file, indent = 2)
                
    @commands.command(usage = "prefix <new_prefix>")
    @commands.has_permissions(manage_guild = True)
    @commands.guild_only()
    async def prefix(self, cont, new_prefix = None): 
        """
            This will show/replace prefix for this server.
        """
        
        if new_prefix is None: 
            
            embed = Embed(description = f"Prefix for this guild is **{self.get_prefix(cont.guild.id)}**", 
                        colour = self.embed_colour)
            embed.set_author(name = self.bot_name, icon_url = self.bot_url)
            
            await cont.channel.send(embed = embed)
        
        else : 
            
            new_prefix = new_prefix.strip()
            self.set_prefix(cont.guild.id, new_prefix)
            
            embed = Embed(colour = self.embed_colour, 
                        description = f"Success!! New prefix for this server is **{new_prefix}**")
            embed.set_author(name = self.bot_name, icon_url = self.bot_url)
            
            await cont.channel.send(embed = embed)
            
    # @commands.command(aliases = ["restrict_in", "restrict-to", "restrict-in", "restrict", "res"], usage = "restrict_to #channel")
    # @commands.has_permissions(manage_guild = True)
    # async def restrict_to(self, cont, channel : discord.TextChannel):
    #     """
    #         Restrict all music commands in a specific channel. 
    #         Note that you can still use config commands in any channel.
    #     """
    #     with open(os.path.dirname(__file__) + "\..\data\config_data.json", "r") as f: 
    #         data = json.load(f)
    #         server_data = data.get(str(cont.guild.id), None)
    # 
    #     if server_data is None:
    #         data[str(cont.guild.id)] = {
    #             "res_chan": str(channel.id)
    #         }
    # 
    #     else :
    #         server_data["res_chan"] = str(channel.id)
    #         data[str(cont.guild.id)] = server_data
    # 
    #     with open(os.path.dirname(__file__) + "\..\data\config_data.json", "w") as f: 
    #         json.dump(data, f, indent = 2)
    # 
    #     await cont.channel.send("Done")
        
    @commands.command(usage = "invite")
    async def invite(self, cont): 
        """
            Gives invite link of the bot .
        """
        
        embed = Embed(colour = self.embed_colour, title = "Invite ME!!", 
                description = "**Wanna invite me to your server? \n [Click here](https://discord.com/oauth2/authorize?client_id=730305385612967958&permissions=8&scope=bot)**")
        embed.set_footer(text=self.bot_name, icon_url=self.bot_url)
            
        await cont.channel.send(embed = embed)
            
def setup(bot): 
    bot.add_cog(Config(bot))
            