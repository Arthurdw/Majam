import sqlite3
import configparser
import datetime

commandConfig = configparser.ConfigParser()
commandConfig.read('config.cfg')

# TODO:
#     Optimize DB executes

#######################
# GENERAL DB COMMANDS #
#######################


def fetch_all(database: str):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    command = cursor.execute("SELECT * FROM servers")
    fetch = command.fetchall()
    connect.commit()
    connect.close()
    return fetch

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
    cursor.execute(f"DELETE FROM servers WHERE server_id = {server_id}")
    cursor.execute("INSERT INTO servers VALUES (?, ?, ?, ?)", parameters)
    connect.commit()
    connect.close()


###################
# CUSTOM COMMANDS #
###################

def get_command(server_id: int, command_name: str):
    """Gets a command from the database!"""
    connect = sqlite3.connect(commandConfig["DATABASE"]["commandsDB"])
    cursor = connect.cursor()
    try:
        cursor.execute("SELECT * FROM servers")
    except sqlite3.OperationalError as e:
        cursor.execute("CREATE TABLE servers (date blob, server_id int, creator_id int, name text, response text)")
    try:
        db_output = cursor.execute(f"SELECT * FROM servers WHERE server_id = {server_id} AND name = '{command_name}'")
        fetch = db_output.fetchall()
    except sqlite3.OperationalError as e:
        print(e)
        connect.commit()
        connect.close()
        return None
    connect.commit()
    connect.close()
    return fetch


def commands(server_id: int):
    """Gets all command names from a server!"""
    connect = sqlite3.connect(commandConfig["DATABASE"]["commandsDB"])
    cursor = connect.cursor()
    command = cursor.execute(f"SELECT name FROM servers WHERE server_id = {server_id}")
    fetch = command.fetchall()
    connect.commit()
    connect.close()
    return fetch


def get_response(server_id: int, command_name: str):
    """Gets a command response from the database!"""
    connect = sqlite3.connect(commandConfig["DATABASE"]["commandsDB"])
    cursor = connect.cursor()
    try:
        cursor.execute("SELECT * FROM servers")
    except sqlite3.OperationalError as e:
        cursor.execute("CREATE TABLE servers (date blob, server_id int, creator_id int, name text, response text)")
    db_output = cursor.execute(f"SELECT response FROM servers WHERE server_id = {server_id} "
                               f"AND name = '{command_name}'")
    out = db_output.fetchall()
    connect.commit()
    connect.close()
    output = 'Hmm, this text is here?\nHow did this happen?\nIDK, something failed internally.\n ╮ (. ❛ ᴗ ❛.) ╭'
    for item in out:
        output = item[0]
    return output


def add_command(server_id: int, author, name: str, response: str):
    """Add a custom command in the database."""
    connect = sqlite3.connect(commandConfig["DATABASE"]["commandsDB"])
    cursor = connect.cursor()
    try:
        cursor.execute("SELECT * FROM servers")
    except sqlite3.OperationalError as e:
        cursor.execute("CREATE TABLE servers (date blob, server_id int, creator_id int, name text, response text)")
    parameters = (datetime.datetime.now(), server_id, author, name.strip().lower(), response.strip())
    command_information = cursor.execute("INSERT INTO servers VALUES (?, ?, ?, ?, ?)", parameters)
    output = command_information.fetchall()
    connect.commit()
    connect.close()
    return output


def edit_command(server_id: int, name: str, new_name: str, response: str):
    """Edits a custom command!"""
    connect = sqlite3.connect(commandConfig["DATABASE"]["commandsDB"])
    cursor = connect.cursor()
    try:
        cursor.execute("SELECT * FROM servers")
    except sqlite3.OperationalError as e:
        cursor.execute("CREATE TABLE servers (date blob, server_id int, creator_id int, prefix text)")
    cursor.execute(f"UPDATE servers SET name = '{new_name}', response = '{response}' WHERE server_id = {server_id} AND "
                   f"name = '{name}'")
    connect.commit()
    connect.close()


def remove_command(server_id: int, name: str):
    """Removes a custom command!"""
    connect = sqlite3.connect(commandConfig["DATABASE"]["commandsDB"])
    cursor = connect.cursor()
    try:
        cursor.execute("SELECT * FROM servers")
    except sqlite3.OperationalError as e:
        cursor.execute("CREATE TABLE servers (date blob, server_id int, creator_id int, prefix text)")
    cursor.execute(f"DELETE FROM servers WHERE server_id = {server_id} AND name = '{name}'")
    connect.commit()
    connect.close()


def command_info(server_id: int, name: str):
    connect = sqlite3.connect(commandConfig["DATABASE"]["commandsDB"])
    cursor = connect.cursor()
    command = cursor.execute(f"SELECT * FROM servers WHERE server_id = {server_id} AND name = '{name}'")
    fetch = command.fetchall()
    connect.commit()
    connect.close()
    return fetch
