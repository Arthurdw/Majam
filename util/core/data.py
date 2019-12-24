import sqlite3
import configparser
import datetime

commandConfig = configparser.ConfigParser()
commandConfig.read('config.cfg')


#######################
# GENERAL DB COMMANDS #
#######################

def fetch_all(database: str, table="servers"):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    command = cursor.execute(f"SELECT * FROM {table}")
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
    except sqlite3.OperationalError:
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
#     LEVELS     #
##################

def get_lvl_exp(_id: int, _type: str):
    """Retrieves the current level & exp from the DB"""
    return db_get(commandConfig["DATABASE"]["levelDB"],
                  table="global",
                  table_values="(id int, exp int, lvl int)",
                  exe=f"SELECT exp, lvl FROM {_type} WHERE id = {_id}")


def add_lvl_exp(_id: int, amount: int, _type: str, sub_type: str):
    """Adds a level or exp to the db!
    (tables: servers, users)"""
    connect = sqlite3.connect(commandConfig["DATABASE"]["levelDB"])
    cursor = connect.cursor()
    try:
        cursor.execute(f"SELECT * FROM {_type} WHERE id = {_id}")
    except sqlite3.OperationalError as e:
        cursor.execute(f"CREATE TABLE {_type} (id int, exp int, lvl int)")
    if not get_lvl_exp(_id, _type):
        db_add(db=commandConfig["DATABASE"]["levelDB"],
               table=_type,
               table_values="(id int, exp int, lvl int)",
               parameters=(_id, amount, 0),
               questions="(?, ?, ?)")
    elif sub_type == "exp":
        exp = get_lvl_exp(_id, _type)[0][0] + amount
        db_update(db=commandConfig["DATABASE"]["stats"],
                  table=_type,
                  table_values="(id int, exp int, lvl int)",
                  parameters=exp,
                  exe=f"SET exp = {exp} WHERE id = {_id}")
    elif sub_type == "lvl":
        level = get_lvl_exp(_id, _type)[0][1] + amount
        db_update(db=commandConfig["DATABASE"]["stats"],
                  table=_type,
                  table_values="(id int, exp int, lvl int)",
                  parameters=level,
                  exe=f"SET lvl = {level} WHERE id = {_id}")
    connect.commit()
    connect.close()
    print('donefro')

##############
#   VOTING   #
##############

# can only concatenate tuple (not "int") to tuple


def add_vote(user_id: int):
    """"Updates the vote-list."""
    count = db_get(db=commandConfig["DATABASE"]["voteDB"],
                   table="list",
                   table_values="(user_id int, date blob, count int)",
                   exe=f"SELECT count FROM list WHERE user_id = {user_id}")
    if not count:
        db_add(db=commandConfig["DATABASE"]["voteDB"],
               table="list",
               table_values="(user_id int, date blob, count int)",
               parameters=(user_id, datetime.datetime.now(), 1),
               questions="(?, ?, ?)")
    else:
        connect = sqlite3.connect(commandConfig["DATABASE"]["voteDB"])
        cursor = connect.cursor()
        cursor.execute(f"SELECT * FROM list")
        cursor.execute(f"UPDATE list SET date = {datetime.datetime.now()}, count = {count[0][0] + 1} "
                       f"WHERE user_id = {user_id}")
        connect.commit()
        connect.close()


##################
#   STATISTICS   #
#################


def get_stats(stats):
    """Gets something from the stats DB!"""
    return db_get(db=commandConfig["DATABASE"]["stats"],
                  table="global",
                  table_values="(type string, amount int)",
                  exe=f"SELECT amount FROM global WHERE type = '{stats}'")


def add_stats(stats):
    """Add stats to the stats DB!"""
    _commands = get_stats(stats)[0][0] + 1
    db_update(db=commandConfig["DATABASE"]["stats"],
              table="global",
              table_values="(type string, amount int)",
              parameters=_commands,
              exe=f"SET amount = {_commands} WHERE type = '{stats}'")


##################
#    CURRENCY    #
##################


def get_base(user_id: int, balance: int, add=True):
    bal = get_global_bal(user_id=user_id)
    if not bal:
        bal = [(0, 0,)]
    cash = bal[0][0]
    if add:
        final = cash + balance
    else:
        final = cash - balance
    return final


def withdraw_global_bal(user_id: int, amount: int):
    add_global_bal(user_id, amount)
    db_update(db=commandConfig["DATABASE"]["currencyDB"],
              table="global_balance",
              table_values="(user_id int, bank int, cash int)",
              parameters=(user_id, 0, 0),
              exe=f"SET bank = {get_global_bal(user_id)[0][1] - amount} WHERE user_id = {user_id}")


def deposit_global_bal(user_id: int, amount: int):
    remove_global_bal(user_id, amount)
    db_update(db=commandConfig["DATABASE"]["currencyDB"],
              table="global_balance",
              table_values="(user_id int, bank int, cash int)",
              parameters=(user_id, 0, 0),
              exe=f"SET bank = {get_global_bal(user_id)[0][1] + amount} WHERE user_id = {user_id}")


def get_global_bal(user_id: int):
    """Gets the cash and bank from a user!"""
    global_bal = db_get(db=commandConfig["DATABASE"]["currencyDB"],
                        table="global_balance",
                        table_values="(user_id int, bank int, cash int)",
                        exe=f"SELECT cash, bank FROM global_balance WHERE user_id = {user_id}")
    if global_bal:
        return global_bal
    else:
        add_global_user(user_id)
        return [(0, 0)]


def add_global_user(user_id: int):
    """"Adds a user to the bank system!"""
    db_add(db=commandConfig["DATABASE"]["currencyDB"],
           table="global_balance",
           table_values="(user_id int, bank int, cash int)",
           parameters=(user_id, 0, 0),
           questions="(?, ?, ?)")


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
    removed = get_base(user_id, balance, False)
    db_update(db=commandConfig["DATABASE"]["currencyDB"],
              table="global_balance",
              table_values="(user_id int, bank int, cash int)",
              parameters=(user_id, 0, balance),
              exe=f"SET cash = {removed} WHERE user_id = {user_id}")


def get_global_max_bank(user_id: int):
    """Gets the max bank capacity from a user"""
    global_bal_max_bank = db_get(db=commandConfig["DATABASE"]["currencyDB"],
                                 table="global_balance_max_bank",
                                 table_values="(user_id int, max_bank int)",
                                 exe=f"SELECT max_bank FROM global_balance_max_bank WHERE user_id = {user_id}")
    if global_bal_max_bank:
        return global_bal_max_bank
    else:
        add_max_bank_user(user_id)
        return [(500, )]


def add_max_bank_user(user_id: int):
    """"Adds a user to the bank system!"""
    db_add(db=commandConfig["DATABASE"]["currencyDB"],
           table="global_balance_max_bank",
           table_values="(user_id int, max_bank int)",
           parameters=(user_id, 500),
           questions="(?, ?)")


def add_max_bank_bal(user_id: int, amount: int):
    """Gives a user more global bank storage!"""
    db_update(db=commandConfig["DATABASE"]["currencyDB"],
              table="global_balance_max_bank",
              table_values="(user_id int, max_bank int)",
              parameters=(user_id, 500),
              exe=f"SET max_bank = {get_global_max_bank(user_id)[0][0] + amount} WHERE user_id = {user_id}")


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
