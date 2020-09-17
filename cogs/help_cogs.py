import discord
import json
import os
from discord import Embed
from discord.ext import commands
from discord.ext.commands import HelpCommand


class HelpMenu(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.embed_colour = discord.Colour.from_rgb(252, 132, 3)
        self.bot_name = bot.user.display_name
        self.bot_url = bot.user.avatar_url
        self.hidden = ["Error_Handling", "HelpMenu"]

    def _help(self, id):
        """
            Returns a embed of main help menu 
            :param id: id of the guild.
        """

        embed = Embed(title="Help Menu", colour=self.embed_colour,
                      description=f"­\n**Type `{self.get_prefix(id)}help command_name` to get help for specific command.**\n­")
        embed.set_footer(text=self.bot_name, icon_url=self.bot_url)

        for cog_name in self.bot.cogs:

            cog = self.bot.get_cog(cog_name)
            name = f"**{cog_name}**"
            value = "­"

            if cog_name not in self.hidden:

                for cmd in cog.get_commands():
                    if cog.get_commands()[-1] != cmd:
                        value += f"`{cmd.name}`, "
                    else:
                        value += f"`{cmd.name}`.­\n­"

                embed.add_field(name=name, value=value, inline=False)

        return embed

    def get_prefix(self, id):
        """
            Gets the prefix for the server
            :param id: id of the guild.
        """
        
        with open(os.path.dirname(__file__) + '\..\data\config.json', 'r') as file: 
            data = json.loads(file.read())
            default_prefix = data['default_prefix']
        
        with open(os.path.dirname(__file__) + '\..\data\prefixes.json', "r") as file:
            data = json.loads(file.read())
        
        prefix = data.get(str(id), default_prefix)
        return prefix

    def _cmd_help(self, cmd, id):
        """
            Gets more help for a specified command 
            :param cmd: command name to get more help.
            :param id: Id of the guild.
        """

        embed = Embed(title=f"{cmd.name.title()}", colour=self.embed_colour)
        embed.add_field(name="­\n**Description**",
                        value=cmd.help + "\n­", inline=False)
        embed.add_field(
            name="**Usage**", value=f"```{self.get_prefix(id)}{cmd.usage}```" , inline=False)

        if cmd.aliases:
            aliases = ""
            for i in cmd.aliases:
                if cmd.aliases[-1] != i:
                    aliases += f"`{i}`, "
                else:
                    aliases += f"`{i}`."

            embed.add_field(name="**Aliases**", value=aliases + "­\n­")

        embed.set_footer(text=self.bot_name, icon_url=self.bot_url)
        return embed
        
    @commands.command()
    async def help(self, cont, subcommand=None):
        """
            shows help menu
        """

        if subcommand is None:
            embed = self._help(str(cont.guild.id))
            await cont.channel.send(embed=embed)

        elif subcommand in [cmd.name for cmd in self.bot.commands]:
            cmd = self.bot.get_command(subcommand)
            embed = self._cmd_help(cmd, str(cont.guild.id))
            await cont.channel.send(embed=embed)

        else:
            embed = Embed(description=f"**Cannot find {subcommand} command.**",
                          colour=discord.Colour.from_rgb(255, 0, 0))
            embed.set_author(name=self.bot_name, icon_url=self.bot_url)

            await cont.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(HelpMenu(bot))
