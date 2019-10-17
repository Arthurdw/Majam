import sqlite3
import configparser
import datetime
from discord.ext import commands

commandConfig = configparser.ConfigParser()
commandConfig.read('config.cfg')

#################
# CUSTOM PREFIX #
#################


def get_prefix(bot, message):
    connect = sqlite3.connect(commandConfig["DATABASE"]["utilityDB"])
    cursor = connect.cursor()
    try:
        cursor.execute("SELECT * FROM prefixes")
    except sqlite3.OperationalError:
        cursor.execute("CREATE TABLE prefixes (server_id int, prefix text)")
    try:
        output = cursor.execute(f"SELECT prefix FROM prefixes WHERE server_id = {message.guild.id}")
    except sqlite3.OperationalError:
        output = "!"
    connect.commit()
    connect.close()
    return output


###################
# CUSTOM COMMANDS #
###################


def add_command(server_id: int, author, name: str, response: str):
    """Add a custom command in the database."""
    connect = sqlite3.connect(commandConfig["DATABASE"]["commandsDB"])
    cursor = connect.cursor()
    try:
        cursor.execute("SELECT * FROM servers")
    except sqlite3.OperationalError as e:
        cursor.execute("CREATE TABLE servers (date blob, server_id int, creator blob, name text, response text)")
    parameters = (datetime.datetime.now(), server_id, author, name, response)
    cursor.execute("INSERT INTO servers (?, ?, ?, ?, ?)", parameters)
    connect.commit()
    connect.close()


def edit_command(name: str, response: str):
    pass


def remove_command(name: str):
    pass

