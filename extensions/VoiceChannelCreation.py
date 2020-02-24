import configparser
import discord
from discord.ext import commands

config = configparser.ConfigParser()
config.read("config.cfg")


class VoiceChannelCreation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id == 634141277788831795:
            async def check_leave():
                if before.channel is not None:
                    if str(before.channel.category).lower() == config["VOICE"]["join_to_create_category"]:
                        if str(before.channel) == config["VOICE"]["join_to_create_name"] or \
                                before.channel.id == 638377701950095391:
                            pass
                        else:
                            if len(before.channel.members) == 0:
                                await before.channel.delete(reason="All users left!")
            if after.channel is not None:
                await check_leave()
                if after.channel.name == config["VOICE"]["join_to_create_name"]:
                    overwrite = discord.PermissionOverwrite()
                    overwrite.create_instant_invite = overwrite.manage_channels = True
                    overwrite.connect = overwrite.speak = overwrite.manage_roles = True
                    overwrite.move_members = overwrite.priority_speaker = overwrite.stream = True
                    channel = await member.guild.create_voice_channel(name=f'{member.name}\'s voice channel!',
                                                                      overwrites=None,
                                                                      category=after.channel.category,
                                                                      reason=f"Join To Create channel for {member}",
                                                                      position=1,
                                                                      topic=f"{member.name}'s crazy channel!",
                                                                      )
                    await channel.set_permissions(member, overwrite=overwrite)
                    await member.move_to(channel, reason=f"Custom VC, moving for {member}")
            else:
                await check_leave()


def setup(bot):
    bot.add_cog(VoiceChannelCreation(bot))
