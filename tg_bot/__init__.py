import logging
import os
import sys
import time
from typing import List
import spamwatch
import telegram.ext as tg
from telethon import TelegramClient
from telethon.sessions import MemorySession
from configparser import ConfigParser
from ptbcontrib.postgres_persistence import PostgresPersistence
from logging.config import fileConfig

StartTime = time.time()


flag = """
\033[37m┌─────────────────────────────────────────────┐\033[0m\n\033[37m│\033[44m\033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[0m\033[91;101m#########################\033[0m\033[37m│\n\033[37m│\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m  \033[0m\033[97;107m:::::::::::::::::::::::::\033[0m\033[37m│\n\033[37m│\033[44m\033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[0m\033[91;101m#########################\033[0m\033[37m│\n\033[37m│\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m  \033[0m\033[97;107m:::::::::::::::::::::::::\033[0m\033[37m│\n\033[37m│\033[44m\033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[0m\033[91;101m#########################\033[0m\033[37m│\n\033[37m│\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m  \033[0m\033[97;107m:::::::::::::::::::::::::\033[0m\033[37m│\n\033[37m│\033[44m\033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[97m★\033[0m\033[44m \033[0m\033[91;101m#########################\033[0m\033[37m│      \033[1mUnited we stand, Divided we fall\033[0m\n\033[37m│\033[97;107m:::::::::::::::::::::::::::::::::::::::::::::\033[0m\033[37m│ \033[1mCYBORG Project, a tribute to USS Enterprise.\033[0m\n\033[37m│\033[91;101m#############################################\033[0m\033[37m│\n\033[37m│\033[97;107m:::::::::::::::::::::::::::::::::::::::::::::\033[0m\033[37m│\n\033[37m│\033[91;101m#############################################\033[0m\033[37m│\n\033[37m│\033[97;107m:::::::::::::::::::::::::::::::::::::::::::::\033[0m\033[37m│\n\033[37m│\033[91;101m#############################################\033[0m\033[37m│\n\033[37m└─────────────────────────────────────────────┘\033[0m\n
"""

def get_user_list(key):
    # Import here to evade a circular import
    from tg_bot.modules.sql import nation_sql
    royals = nation_sql.get_royals(key)
    return [a.user_id for a in royals]

# enable logging

fileConfig('logging.ini')

#print(flag)
log = logging.getLogger('[Enterprise]')
logging.getLogger('ptbcontrib.postgres_persistence.postgrespersistence').setLevel(logging.WARNING)
log.info("[CYBORG] CYBORG is starting. | A BIONIC ROBOTS PROJECT | Licensed under GPLv3.")
log.info("[CYBORG] Not affiliated to Azur Lane or Yostar in any way whatsoever.")
log.info("[CYBORG] Project maintained by: HYPERxD")

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 7:
    log.error(
        "[CYBORG] You MUST have a python version of at least 3.7! Multiple features depend on this. Bot quitting."
    )
    quit(1)

parser = ConfigParser()
parser.read("config.ini")
kigconfig = parser["kigconfig"]

class CyborgINIT:
    def __init__(self, parser: ConfigParser):
        self.parser = parser
        self.SYS_ADMIN: int = self.parser.getint('SYS_ADMIN', 0)
        self.OWNER_ID: int = self.parser.getint('OWNER_ID')
        self.OWNER_USERNAME: str = self.parser.get('OWNER_USERNAME', None)
        self.APP_ID: str = self.parser.getint("APP_ID")
        self.API_HASH: str = self.parser.get("API_HASH")
        self.WEBHOOK: bool = self.parser.getboolean('WEBHOOK', False)
        self.URL: str = self.parser.get('URL', None)
        self.CERT_PATH: str = self.parser.get('CERT_PATH', None)
        self.PORT: int = self.parser.getint('PORT', None)
        self.INFOPIC: bool = self.parser.getboolean('INFOPIC', False)
        self.DEL_CMDS: bool = self.parser.getboolean("DEL_CMDS", False)
        self.STRICT_GBAN: bool = self.parser.getboolean("STRICT_GBAN", False)
        self.ALLOW_EXCL: bool = self.parser.getboolean("ALLOW_EXCL", False)
        self.CUSTOM_CMD: List[str] = ['/', '!']
        self.BAN_STICKER: str = self.parser.get("BAN_STICKER", None)
        self.TOKEN: str = self.parser.get("TOKEN")
        self.DB_URI: str = self.parser.get("SQLALCHEMY_DATABASE_URI")
        self.LOAD = self.parser.get("LOAD").split()
        self.LOAD: List[str] = list(map(str, self.LOAD))
        self.MESSAGE_DUMP: int = self.parser.getint('MESSAGE_DUMP', None)
        self.GBAN_LOGS: int = self.parser.getint('GBAN_LOGS', None)
        self.NO_LOAD = self.parser.get("NO_LOAD").split()
        self.NO_LOAD: List[str] = list(map(str, self.NO_LOAD))
        self.spamwatch_api: str = self.parser.get('spamwatch_api', None)
        self.CASH_API_KEY: str = self.parser.get('CASH_API_KEY', None)
        self.TIME_API_KEY: str = self.parser.get('TIME_API_KEY', None)
        self.WALL_API: str = self.parser.get('WALL_API', None)
        self.LASTFM_API_KEY: str = self.parser.get('LASTFM_API_KEY', None)
        self.CF_API_KEY: str =  self.parser.get("CF_API_KEY", None)
        self.bot_id = 0 #placeholder
        self.bot_name = "CYBORG" #placeholder
        self.bot_username = "CYBORGRobot" #placeholder
        self.DEBUG: bool = self.parser.getboolean("IS_DEBUG", False)
        self.DROP_UPDATES: bool = self.parser.getboolean("DROP_UPDATES", True)
        self.BOT_API_URL: str = self.parser.get('BOT_API_URL', "https://api.telegram.org/bot")
        self.BOT_API_FILE_URL: str = self.parser.get('BOT_API_FILE_URL', "https://api.telegram.org/file/bot")


    def init_sw(self):
        if self.spamwatch_api is None:
            log.warning("SpamWatch API key is missing! Check your config.ini")
            return None
        else:
            try:
                sw = spamwatch.Client(spamwatch_api)
                return sw
            except:
                sw = None
                log.warning("Can't connect to SpamWatch!")
                return sw


CInit = CyborgINIT(parser=kigconfig)

SYS_ADMIN = CInit.SYS_ADMIN
OWNER_ID = CInit.OWNER_ID
OWNER_USERNAME = CInit.OWNER_USERNAME
APP_ID = CInit.APP_ID
API_HASH = CInit.API_HASH
WEBHOOK = CInit.WEBHOOK
URL = CInit.URL
CERT_PATH = CInit.CERT_PATH
PORT = CInit.PORT
INFOPIC = CInit.INFOPIC
DEL_CMDS = CInit.DEL_CMDS
ALLOW_EXCL = CInit.ALLOW_EXCL
CUSTOM_CMD = CInit.CUSTOM_CMD
BAN_STICKER = CInit.BAN_STICKER
TOKEN = CInit.TOKEN
DB_URI = CInit.DB_URI
LOAD = CInit.LOAD
MESSAGE_DUMP = CInit.MESSAGE_DUMP
GBAN_LOGS = CInit.GBAN_LOGS
NO_LOAD = CInit.NO_LOAD
SUDO_USERS = [OWNER_ID] + get_user_list("sudos")
DEV_USERS = [OWNER_ID] + get_user_list("devs")
SUPPORT_USERS = get_user_list("supports")
SARDEGNA_USERS = get_user_list("sardegnas")
WHITELIST_USERS = get_user_list("whitelists")
SPAMMERS = get_user_list("spammers")
spamwatch_api = CInit.spamwatch_api
CASH_API_KEY = CInit.CASH_API_KEY
TIME_API_KEY = CInit.TIME_API_KEY
WALL_API = CInit.WALL_API
LASTFM_API_KEY = CInit.LASTFM_API_KEY
CF_API_KEY = CInit.CF_API_KEY

# SpamWatch
sw = CInit.init_sw()

from tg_bot.modules.sql import SESSION

if not CInit.DROP_UPDATES:
    updater = tg.Updater(token=TOKEN, base_url=KInit.BOT_API_URL, base_file_url=KInit.BOT_API_FILE_URL, workers=min(32, os.cpu_count() + 4), request_kwargs={"read_timeout": 10, "connect_timeout": 10}, persistence=PostgresPersistence(session=SESSION))
    
else:
    updater = tg.Updater(token=TOKEN, base_url=KInit.BOT_API_URL, base_file_url=KInit.BOT_API_FILE_URL, workers=min(32, os.cpu_count() + 4), request_kwargs={"read_timeout": 10, "connect_timeout": 10})
    
telethn = TelegramClient(MemorySession(), APP_ID, API_HASH)
dispatcher = updater.dispatcher



# Load at end to ensure all prev variables have been set
from tg_bot.modules.helper_funcs.handlers import CustomCommandHandler

if CUSTOM_CMD and len(CUSTOM_CMD) >= 1:
    tg.CommandHandler = CustomCommandHandler


def spamfilters(text, user_id, chat_id):
    # print("{} | {} | {}".format(text, user_id, chat_id))
    if int(user_id) not in SPAMMERS:
        return False

    print("This user is a spammer!")
    return True
