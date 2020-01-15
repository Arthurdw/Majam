import configparser
import glob
import os
import sys
from util.core import data, formatter
from discord.ext import commands
from util.core import GitHub

em = formatter.embed_message
config = configparser.ConfigParser()
token = configparser.ConfigParser()
config.read("config.cfg")
token.read("token.cfg")
os.system("cls")


class Majam(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=data.get_prefix,
                         description=config["UTILITY"]["description"],
                         case_insensitive=True,
                         help_attrs=dict(hidden=True))
        self.remove_command('help')
        print("\\/\\/\\/\\/\\/ EXTENSIONS \\/\\/\\/\\/\\/")
        for extension in glob.glob("extensions/*.py"):
            print(extension.replace("extensions\\", "")[:-3] + ": Starting", end='')
            sys.stdout.flush()
            self.load_extension(extension.replace("\\", ".")[:-3])
            print("\r", extension.replace("extensions\\", "")[:-3] + ": Ready      ")
            sys.stdout.flush()
        print("/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\")

    async def on_ready(self):
        print('\n*-* *-* *-* *-*  *-* *-* *-* *-*')
        print('*-* Logged in as:            *-*')
        print(f'*-* Name: {self.user.name}#{self.user.discriminator}         *-*')
        print(f'*-* ID: {self.user.id}   *-*')
        print(f'*-* Version: {GitHub.version()}        *-*')
        print('*-* *-* *-* *-*  *-* *-* *-* *-*\n')

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    def run(self):
        super().run(token["SECRET"]["token"], reconnect=True)


if __name__ == '__main__':
    Majam().run()
