import os 
import json 
import requests
import discord 

from discord.ext import commands 

class VoiceCreator(commands.Cog): 
    
    CHANNELS = {}
    
    def __init__(self, bot): 
        self.bot = bot 
        self.embed_colour = discord.Colour.from_rgb(52, 235, 216)
        
    @staticmethod
    def put_data(data: dict, key = None): 
        if key is None: 
            with open(os.path.dirname(__file__) + "\..\data\data.json", "w") as file: 
                json.dump(data, file, indent = 2)
        else : 
            with open(os.path.dirname(__file__) + "\..\data\data.json", "r") as file: 
                json_data = json.loads(file.read())
                json_data[key] = data 
            with open(os.path.dirname(__file__) + "\..\data\data.json", "w") as file: 
                json.dump(json_data, file, indent = 2)
        
    @staticmethod
    def get_data(key = None): 
        with open(os.path.dirname(__file__) + "\..\data\data.json", "r") as file: 
            data = json.loads(file.read())
        if key is None : 
            return data
        else : 
            return data.get(key)
            
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after): 
        server_data = VoiceCreator.get_data(str(member.guild.id))
        
        if server_data is not None and after.channel is not None and server_data['main_vc'] == str(after.channel.id): 
            category = discord.utils.get(member.guild.categories, id = int(server_data["category"]))
            new_vc = await member.guild.create_voice_channel(name = f"{member.name}'s Vc", category = category)
            await member.move_to(new_vc)
            VoiceCreator.CHANNELS[member.id] = new_vc.id
            
        elif server_data is not None and before.channel is not None and before.channel.id == VoiceCreator.CHANNELS.get(member.id): 
            await before.channel.delete()
            
        else : 
            pass 
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload): 
        data = VoiceCreator.get_data(str(payload.guild_id))
        guild = discord.utils.get(self.bot.guilds, id = payload.guild_id)
        channel = discord.utils.get(guild.channels, id = payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if data is not None: 
            reaction_msg_id = payload.message_id
            if str(reaction_msg_id) == str(data["cmds"]["message"]): 
                if payload.emoji in "🔒 🔑 ❌ 🔍 📖".split(): 
                    print("sahi khel gaya *")
                else : 
                    await message.remove_reaction(member = payload.emoji)
        else : 
            pass 

    @commands.command()
    async def setup(self, cont): 
        #   Automatically sets up the bot 
        embed = discord.Embed(title = "Setting up the bot...", colour = self.embed_colour, 
                description = "Till then you can check out the full list of commands from here.")
        await cont.channel.send(embed = embed)
        
        permissions = cont.me.guild_permissions 
        if not permissions.manage_channels: 
            embed = discord.Embed(title = "Error", colour = discord.Colour.from_rgb(255, 0, 0), 
                    description = "**I am missing `Manage Channels` permission.**")
            await cont.channel.send(embed = embed)
            return 
        else : 
            category = await cont.guild.create_category(name = "Byte Voice Channels")
            info_channel = await cont.guild.create_text_channel(name = "how_to_use", category = category)
            cmd_channel = await cont.guild.create_text_channel(name = "byte_cmds", category = category)
            waiting_vc = await cont.guild.create_voice_channel(name = "Waiting Lobby", category = category)
            main_vc = await cont.guild.create_voice_channel(name = "Join to Create", category = category)
            
            text = """
            **QUICK REACTION COMMANDS** :-

            > `🔒` - **Locks your voice channel**
            > `🔑` - **Unlocks your voice channel**
            > `❌` - **ForceFully Deletes your voice channel**
            > `🔍` - **Hides your voice channel**
            > `📖` - **Unhides your voice channel**

            **MORE COMMANDS** :-

            > `>allow @member` - **Allows the member to join your voice channel.**
            > `>limi number`      - **Set a specific limit to a voice channel**
            > `>reject @member`  - **Removes the member's permission to join your voice channel.**
            > `>name new_name` - **Changes the name of your voice channel.**

            **ADMIN COMMANDS** :-

            > `>remove_all` - **Removes all the voice channel.**
            > `>ignore @member` - **The user will no longer be able to create his voice channel.**
            > `>allow @member` - **Removes the member from ignored list.**
            """
            embed = discord.Embed(colour = self.embed_colour, 
                    description = text)
            embed.set_image(url = "https://cdn.discordapp.com/attachments/727478781681336391/753222963641319424/Untitled_design.png")
            await cmd_channel.send(embed = embed)
                
            server_data = {
                "cmds": {
                    "channel": f"{cmd_channel.id}", 
                    "message": "message_id"
                }, 
                "main_vc": f"{main_vc.id}", 
                "category": f"{category.id}"
            }
            
            VoiceCreator.put_data(server_data, str(cont.guild.id))
        
def setup(bot): 
    bot.add_cog(VoiceCreator(bot))
        