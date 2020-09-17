import os 
import json
import lavalink

import discord 
from discord import Embed
from discord.ext import commands 

class Music(commands.Cog): 
    
    def __init__(self, bot): 
        self.bot = bot 
        self.embed_colour = discord.Colour.from_rgb(212, 0, 255)
        self.error_colour = discord.Colour.from_rgb(255, 0, 0)
        self.bot_name = bot.user.display_name
        self.bot_url = bot.user.avatar_url
        self.queue = {}
        
        if not hasattr(bot, 'lavalink'): 
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node('localhost', 2333, 'youshallnotpass', 'eu', 'default-node')
            bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')
            
        lavalink.add_event_hook(self.event_hook)
        
    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)
        
    async def event_hook(self, event): 
        if isinstance(event, lavalink.events.QueueEndEvent): 
            #Disconnects bot from vc 
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
            try : 
                self.np.pop(guild_id)
                self.queue.pop(guild_id)
            except : 
                pass
            
        if isinstance(event, lavalink.events.TrackEndEvent): 
            guild_id = int(event.player.guild_id)
            queue = self.queue.get(guild_id)
            if queue is not None : 
                try : 
                    queue.pop(0) 
                    self.queue[guild_id] = queue
                except: 
                    pass
            else : 
                pass
            
        if isinstance(event, lavalink.events.TrackStartEvent): 
            pass
            
    async def cog_before_invoke(self, cont): 
        if cont.guild is not None: 
            await self.pre_check(cont)
                
    async def pre_check(self, cont): 
        player = self.bot.lavalink.player_manager.create(cont.guild.id,
                    endpoint = str(cont.guild.region))
                    
        ignore_cmds = ["now_playing", "queue"]
        
        if not cont.command.name in ignore_cmds: 
        
            if cont.author.voice is None: 
                raise commands.CommandInvokeError("You must be connected to a voice channel!")
            
            if not player.is_connected: 
                if not cont.command.name == "play":  
                    raise commands.CommandInvokeError("I am not connected to any voice channel!")
                    
                else : 
                    permission = cont.author.voice.channel.permissions_for(cont.me)
        
                    if not permission.view_channel: 
                        raise commands.CommandInvokeError("I am not allowed to **view** your channel.")
                    if not permission.connect: 
                        raise commands.CommandInvokeError("I need permissions to connect to your voice channel.")
                    if not permission.speak: 
                        raise commands.CommandInvokeError("I need **Speak** permissions to play song!")
                        
                    await self.connect_to(cont.guild.id, str(cont.author.voice.channel.id))
            
            else : 
                if int(player.channel_id) != cont.author.voice.channel.id: 
                    raise commands.CommandInvokeError("You must be in same voice channel to use that command.")
                    
    @commands.Cog.listener()
    async def on_voice_update(self, before, after): 
        if before is not None and after is None: 
            guild_id = before.guild.id
            player = self.bot.lavalink.player_manager.get(guild_id)
            
            try : 
                self.np.pop(guild_id)
                self.queue.pop(guild_id)
            except : 
                pass
            
            await player.queue.clear()
            await player.stop()
            await self.connect_to(guild_id, None)
                
    @commands.command(aliases=["p"], usage="play <song_name")
    async def play(self, cont, *, query):
        """
            Command to play song in a voice channel
        """ 
        
        embed = Embed(
            title=f"**Searching `{query}`**", colour=self.embed_colour)
        search_msg = await cont.channel.send(embed=embed)
        
        player = self.bot.lavalink.player_manager.get(cont.guild.id)
        query = f"ytsearch: {query}"
        result = await player.node.get_tracks(query)
        
        if result['loadType'] == 'PLAYLIST_LOADED':
            tracks = result['tracks']
            # 
            # for track in tracks:
            # 
            #     # Add all of the tracks from the playlist to the queue.
            #     player.add(requester=cont.author.id, track=track)
            # 
            # await cont.channel.send("Added all songs from queue to the playlist. Use `queue` command to see all.")
            await cont.channel.send("Playlist are not supported yet!!")
        
        else:
            track = result['tracks'][0]
            song_data = track['info']
            
            track = lavalink.models.AudioTrack(track, cont.author.id, recommended=True)
            player.add(requester=cont.author.id, track=track)
            
            queue = self.queue.get(cont.guild.id)
            if queue is None: 
                self.queue[cont.guild.id] = [song_data]
            else : 
                self.queue[cont.guild.id].append(song_data)
                
        if not player.is_playing:
            
            embed = Embed(colour=self.embed_colour,
                          description=f'**Now Playing :- [{song_data["title"]}]({song_data["uri"]})**\n\n\
                                        **Total time :- `{lavalink.format_time(song_data["length"])}`**')
            embed.set_author(
                name=self.bot_name, icon_url=self.bot_url)

            await search_msg.edit(embed=embed)
            await player.play() 
        
        else : 
            embed = Embed(colour=self.embed_colour,
                          description=f'**Added to queue :- [{song_data["title"]}]({song_data["uri"]})**\n\n\
                                        **Total time :- `{lavalink.format_time(song_data["length"])}`**')
            embed.set_author(
                name=self.bot_name, icon_url=self.bot_url)

            await search_msg.edit(embed=embed)
                
    @commands.command(aliases=["n"], usage="next")
    async def next(self, cont):
        """
            Skips the current playing song
        """
        player = self.bot.lavalink.player_manager.get(cont.guild.id)
        await player.skip()
        
        queue = self.queue.get(cont.guild.id)
        if len(queue) >= 1: 
            await cont.message.add_reaction("👍")
        else : 
            embed = Embed(title = "Error", colour = discord.Colour.from_rgb(255, 0, 0), 
                    description = "**Queue has ended**")
            await cont.channel.send(embed = embed)
        
    @commands.command(aliases=["np", "playing"], usage="now_playing")
    async def now_playing(self, cont):
        """
            Displays the currently playing song
        """ 
        queue = self.queue.get(cont.guild.id)
        
        if len(queue) >= 1: 
            song_data = queue[0]
            embed = Embed(colour=self.embed_colour,
                          description=f'**Now playing :- [{song_data["title"]}]({song_data["uri"]})**\n\n\
                                        **Total time :- `{lavalink.format_time(song_data["length"])}`**')
            embed.set_author(
                name=self.bot_name, icon_url=self.bot_url)
                
            await cont.channel.send(embed = embed)
        
        else : 
            embed = Embed(title = "Error", colour = discord.Colour.from_rgb(255, 0, 0), 
                    description = "**No song is playing in this server.**")
            await cont.channel.send(embed = embed)
            
    @commands.command(aliases=["q"], usage="queue")
    async def queue(self, cont):
        """
            Displays the list of song in queue
        """ 
        song_list = self.queue.get(cont.guild.id)

        if song_list is None:
            embed = Embed(title="Error", colour=self.error_colour,
                          description=f"**Nothing is playing in this server.**")
            await cont.channel.send(embed=embed)
            return
        else:
            text = ""
            try: 
                text += f"Currently playing :- **{song_list[0]['title']}**\n\n"
            except IndexError: 
                embed = Embed(title="Error", colour=self.error_colour,
                              description=f"**Nothing is playing in this server.**")
                await cont.channel.send(embed=embed)
                return

            count = 1
            if len(song_list) > 1: 
                text += "Songs in queue :- \n"
                for song_data in song_list:
                    if not song_list.index(song_data) == 0:
                        title = song_data["title"]
                        text += f"{count}) **{title}**\n"
                        count += 1

            embed = Embed(colour=self.embed_colour, description=text)
            embed.set_author(name=self.bot_name, icon_url=self.bot_url)
            await cont.channel.send(embed=embed)
            return
            
    @commands.command(aliases=["s", "stop"], usage="pause")
    async def pause(self, cont):
        """
            Pauses the playing voice client
        """
        player = self.bot.lavalink.player_manager.get(cont.guild.id)
        if not player.paused: 
            await player.set_pause(True)
            await cont.message.add_reaction("👍")
        else : 
            embed = Embed(title="Error", colour=self.error_colour,
                          description=f"**Player is already paused**")
            await cont.channel.send(embed=embed)
            
    @commands.command(aliases=["r", "restart"], usage="resume")
    async def resume(self, cont):
        """
            Resumes the paused voice client
        """
        player = self.bot.lavalink.player_manager.get(cont.guild.id)
        if player.paused: 
            await player.set_pause(False)
            await cont.message.add_reaction("👍")
        else : 
            embed = Embed(title="Error", colour=self.error_colour,
                          description=f"**Player is not paused**")
            await cont.channel.send(embed=embed)
            
    @commands.command(aliases=["dc", "leave"], usage="disconnect")
    async def disconnect(self, cont):
        """
            Disconnects from voice player
        """
        player = self.bot.lavalink.player_manager.get(cont.guild.id)
        guild_id = cont.guild.id
        
        try : 
            self.np.pop(int(guild_id))
            self.queue.pop(int(guild_id))
        except : 
            pass
        
        player.queue.clear()
        await player.stop()
        await self.connect_to(cont.guild.id, None)
        
        await cont.message.add_reaction("👋")
    
    @commands.command(aliases=["l"], usage="loop")
    async def loop(self, cont):
        """
            Loops the current song
        """ 
        player = self.bot.lavalink.player_manager.get(cont.guild.id)
        if player.repeat: 
            player.repeat = False 
            loop = 'Disabled'
        else : 
            player.repeat = True
            loop = "Enabled"
            
        embed = discord.Embed(colour = self.embed_colour, description=f"**Loop {loop}**")
        embed.set_author(name=self.bot_name, icon_url=self.bot_url)
        await cont.channel.send(embed = embed)
        
    @commands.command(aliases=["rem"], usage="remove position")
    async def remove(self, cont, index):
        """
            Removes the specified song
        """ 
        try : 
            index = int(index)
            if index > len(self.queue.get(cont.guild.id)) - 1: 
                raise ValueError
        except : 
            embed = Embed(title="Error", colour=self.error_colour,
                          description=f"**No songs at index {index}**")
            return await cont.channel.send(embed=embed)
        else : 
            player = self.bot.lavalink.player_manager.get(cont.guild.id)
            print(player.queue)
            player.queue.pop(index - 1)
            local_queue = self.queue.get(cont.guild.id)
            song_data = local_queue.pop(index)
            embed = Embed(colour=self.embed_colour,
                          description=f'**Removed :- [{song_data["title"]}]({song_data["uri"]})**\n\n\
                                        **Requester :- `{cont.author.name}`**')
            embed.set_author(
                name=self.bot_name, icon_url=self.bot_url)
                
            await cont.channel.send(embed = embed)
            
    @commands.command(usage="seek mm:ss")
    async def seek(self, cont, timing):
        """
            Seeks player to the specified time.
            -------
            Format : mm:ss
        """ 
        try : 
            minutes, seconds = timing.split(":")
            minutes = int(minutes.strip())
            seconds = int(seconds.strip())
        except : 
            embed = Embed(title="Error", colour=self.error_colour,
                          description=f"**Wrong format provided (`mm:ss`)**")
            return await cont.channel.send(embed=embed)
        else : 
            milliseconds = minutes*60000 + seconds*1000
            song_list = self.queue.get(cont.guild.id)
            
            if song_list is None or len(song_list) == 0: 
                embed = Embed(title="Error", colour=self.error_colour,
                              description=f"**Nothing is playing which can be seeked.**")
                return await cont.channel.send(embed=embed)
                
            elif milliseconds < 0 or milliseconds > song_list[0]['length']: 
                embed = Embed(title="Error", colour=self.error_colour,
                              description=f"**You can't exceed the song's length.**")
                return await cont.channel.send(embed=embed)
                
            else : 
                player = self.bot.lavalink.player_manager.get(cont.guild.id)
                await player.seek(milliseconds)
                await cont.message.add_reaction("👍")
            
            
def setup(bot): 
    bot.add_cog(Music(bot))
