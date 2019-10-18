import sqlite3
import configparser
import datetime

commandConfig = configparser.ConfigParser()
commandConfig.read('config.cfg')

#################
# CUSTOM PREFIX #
#################


def get_prefix(bot, message, db_only=False):
    """Gets the current bot prefix for the server."""
    output = str(commandConfig.get("UTILITY", "defaultPrefixes")).split(",") + ['<@634141001769943090> ',
                                                                                '<@!634141001769943090> ',
                                                                                '<@634141001769943090>',
                                                                                '<@!634141001769943090>']
    if not message.guild:
        if db_only is True:
            return "!"
        else:
            return output
    connect = sqlite3.connect(commandConfig["DATABASE"]["utilityDB"])
    cursor = connect.cursor()
    try:
        cursor.execute("SELECT * FROM servers")
    except sqlite3.OperationalError:
        cursor.execute("CREATE TABLE servers (server_id int, prefix text)")
    db_output = cursor.execute(f"SELECT prefix FROM servers WHERE server_id = {message.guild.id}")
    prefix = '!'
    for item in db_output.fetchall():
        prefix = item[0]
    if db_only is True:
        return prefix
    else:
        output = ['<@634141001769943090> ', '<@!634141001769943090> ',
                  '<@634141001769943090>', '<@!634141001769943090>']
        output += prefix
    connect.commit()
    connect.close()
    return output


def set_prefix(server_id, author, prefix):
    """Sets a server prefix"""
    connect = sqlite3.connect(commandConfig["DATABASE"]["utilityDB"])
    cursor = connect.cursor()
    try:
        cursor.execute("SELECT * FROM servers")
    except sqlite3.OperationalError as e:
        cursor.execute("CREATE TABLE servers (date blob, server_id int, creator_id int, prefix text)")
    parameters = (datetime.datetime.now(), server_id, author, prefix)
    cursor.execute("INSERT INTO servers VALUES (?, ?, ?, ?)", parameters)
    connect.commit()
    connect.close()


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
        cursor.execute("CREATE TABLE servers (date blob, server_id int, creator_id int, name text, response text)")
    parameters = (datetime.datetime.now(), server_id, author, name, response)
    command_info = cursor.execute("INSERT INTO servers VALUES (?, ?, ?, ?, ?)", parameters)
    connect.commit()
    connect.close()
    return command_info.fetchall()


def edit_command(name: str, response: str):
    pass


def remove_command(name: str):
    pass

