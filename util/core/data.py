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


def db_get(db, table, table_values, exe):
    connect = sqlite3.connect(db)
    cursor = connect.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table}")
    except sqlite3.OperationalError as e:
        cursor.execute(f"CREATE TABLE {table} {table_values}")
    fetched = cursor.execute(exe)
    fetch = fetched.fetchall()
    connect.commit()
    connect.close()
    return fetch


def db_update(db, table, table_values, parameters=None, exe=None, instant_insert=False, instant_action="INSERT INTO"):
    connect = sqlite3.connect(db)
    cursor = connect.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table}")
    except sqlite3.OperationalError as e:
        cursor.execute(f"CREATE TABLE {table} {table_values}")
    try:
        if instant_insert:
            cursor.execute(f"{instant_action} {table} {exe}")
        else:
            cursor.execute(f"UPDATE {table} {exe}")
    except IndexError:
        cursor.execute(f"{instant_action} {table} VALUES (?, ?, ?)", parameters)
    connect.commit()
    connect.close()


def db_add(db, table, table_values, parameters, questions):
    connect = sqlite3.connect(db)
    cursor = connect.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table}")
    except sqlite3.OperationalError as e:
        cursor.execute(f"CREATE TABLE {table} {table_values}")
    cursor.execute(f"INSERT INTO {table} VALUES {questions}", parameters)
    connect.commit()
    connect.close()


##################
#   STATISTICS   #
##################


def add_global_command_count():
    pass


def add_guild_command_count(guild_id: int):
    pass


def add_global_message_count():
    pass


def add_guild_message_count(guild_id: int):
    pass


def get_global_message_count():
    pass


def get_guild_message_count(guild_id: int):
    pass

##################
#    CURRENCY    #
##################


def get_base(user_id: int, balance: int, add=True):
    bal = get_global_bal(user_id=user_id)
    if not bal:
        bal = [(0, 0,)]
    cash = bal[0][1]
    final = cash - balance
    if add:
        final = cash + balance
    return final


def get_global_bal(user_id: int):
    """Gets the cash and bank from a user!"""
    return db_get(db=commandConfig["DATABASE"]["currencyDB"],
                  table="global_balance",
                  table_values="(user_id int, bank int, cash int)",
                  exe=f"SELECT cash, bank FROM global_balance WHERE user_id = {user_id}")


def add_global_bal(user_id: int, balance: int):
    """Gives a user global cash!"""
    added = get_base(user_id, balance)
    db_update(db=commandConfig["DATABASE"]["currencyDB"],
              table="global_balance",
              table_values="(user_id int, bank int, cash int)",
              parameters=(user_id, 0, balance),
              exe=f"SET cash = {added} WHERE user_id = {user_id}")


def remove_global_bal(user_id: int, balance: int):
    """Takes a user their global cash!"""
    removed = get_base(user_id, balance)
    db_update(db=commandConfig["DATABASE"]["currencyDB"],
              table="global_balance",
              table_values="(user_id int, bank int, cash int)",
              parameters=(user_id, 0, balance),
              exe=f"SET cash = {removed} WHERE user_id = {user_id}")

################
#  AUTO ROLES  #
################


def get_auto_role(server_id: int):
    """Gets all auto roles from a server!"""
    return db_get(db=commandConfig["DATABASE"]["autoRoleDB"],
                  table="servers",
                  table_values="(server_id int, role_id int)",
                  exe=f"SELECT role_id from servers WHERE server_id = {server_id}")


def add_auto_role(server_id: int, role_id: int):
    """Adds a role to the auto-role system!"""
    db_add(db=commandConfig["DATABASE"]["autoRoleDB"],
           table="servers",
           table_values="(server_id int, role_id int)",
           parameters=(server_id, role_id),
           questions="(?, ?)")


def remove_auto_role(server_id: int, role_id: int):
    """Removes a auto role!"""
    db_update(db=commandConfig["DATABASE"]["autoRoleDB"],
              table="servers",
              table_values="(server_id int, role_id int)",
              parameters=(server_id, role_id),
              instant_insert=True,
              instant_action="DELETE FROM",
              exe=f"WHERE server_id = {server_id} AND role_id = {role_id}")

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


def reset_prefix(server_id: int):
    """Resets a server their prefix"""
    db_update(db=commandConfig["DATABASE"]["utilityDB"],
              table="servers",
              table_values="(date blob, server_id int, creator_id int, prefix text)",
              exe=f"WHERE server_id = {server_id}",
              instant_insert=True,
              instant_action="DELETE FROM")


###################
# CUSTOM COMMANDS #
###################


def command_info(server_id: int, name: str):
    """Gets a command from the database!"""
    return db_get(db=commandConfig["DATABASE"]["commandsDB"],
                  table="servers",
                  table_values="(date blob, server_id int, creator_id int, name text, response text)",
                  exe=f"SELECT * FROM servers WHERE server_id = {server_id} AND name = '{name}'")


def commands(server_id: int):
    """Gets all command names from a server!"""
    return db_get(db=commandConfig["DATABASE"]["commandsDB"],
                  table="servers",
                  table_values="(date blob, server_id int, creator_id int, name text, response text)",
                  exe=f"SELECT name FROM servers WHERE server_id = {server_id}")


def get_response(server_id: int, command_name: str):
    """Gets a command response from the database!"""
    out = db_get(db=commandConfig["DATABASE"]["commandsDB"],
                 table="servers",
                 table_values="(date blob, server_id int, creator_id int, name text, response text)",
                 exe=f"SELECT response FROM servers WHERE server_id = {server_id} AND name = '{command_name}'")
    output = 'Hmm, this text is here?\nHow did this happen?\nIDK, something failed internally.\n ╮ (. ❛ ᴗ ❛.) ╭'
    for item in out:
        output = item[0]
    return output


def add_command(server_id: int, author, name: str, response: str):
    """Add a custom command in the database."""
    db_add(db=commandConfig["DATABASE"]["commandsDB"],
           table="servers",
           table_values="(date blob, server_id int, creator_id int, name text, response text)",
           parameters=(datetime.datetime.now(), server_id, author, name.strip().lower(), response.strip()),
           questions="(?, ?, ?, ?, ?)")


def edit_command(server_id: int, name: str, new_name: str, response: str):
    """Edits a custom command!"""
    db_update(db=commandConfig["DATABASE"]["commandsDB"],
              table="servers",
              table_values="(date blob, server_id int, creator_id int, name text, response text)",
              exe=f"SET name = '{new_name}', response = '{response}' WHERE server_id = {server_id} AND name = '{name}'")


def remove_command(server_id: int, name: str):
    """Removes a custom command!"""
    db_update(db=commandConfig["DATABASE"]["commandsDB"],
              table="servers",
              table_values="(date blob, server_id int, creator_id int, name text, response text)",
              exe=f"WHERE server_id = {server_id} AND name = '{name}'",
              instant_insert=True,
              instant_action="DELETE FROM")
