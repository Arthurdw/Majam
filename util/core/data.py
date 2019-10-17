import sqlite3
import configparser
import datetime
import json
from discord.ext import commands

commandConfig = configparser.ConfigParser()
commandConfig.read('config.cfg')

#################
# CUSTOM PREFIX #
#################


def get(bot, message, default):
    connect = sqlite3.connect(commandConfig["DATABASE"]["utilityDB"])
    cursor = connect.cursor()
    try:
        cursor.execute("SELECT * FROM prefixes")
    except sqlite3.OperationalError:
        cursor.execute("CREATE TABLE prefixes (server_id int, prefix text)")
    db_output = cursor.execute(f"SELECT prefix FROM prefixes WHERE server_id = {message.guild.id}")
    if len(db_output.fetchall()) == 0:
        output = default
    else:
        output = ['<@634141001769943090> ',
                  '<@!634141001769943090> ',
                  '<@634141001769943090>',
                  '<@!634141001769943090>']
        output += db_output.fetchall()
    connect.commit()
    connect.close()
    return output


def get_prefix(bot, message):
    output = str(commandConfig.get("UTILITY", "defaultPrefixes")).split(",") + ['<@634141001769943090> ',
                                                                                '<@!634141001769943090> ',
                                                                                '<@634141001769943090>',
                                                                                '<@!634141001769943090>']
    if not message.guild:
        return commands.when_mentioned_or(*output)(bot, message)
    return commands.when_mentioned_or(*get(bot, message, output))(bot, message)


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
    command_info = cursor.execute("INSERT INTO servers (?, ?, ?, ?, ?)", parameters)
    connect.commit()
    connect.close()
    return command_info.fetchall()


def edit_command(name: str, response: str):
    pass


def remove_command(name: str):
    pass

