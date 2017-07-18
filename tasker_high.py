#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
from datetime import datetime
import telepot
import psycopg2
from contrib.sqlquery import *
from tasker_settings import Settings

loglevel = Settings.loglevel
token = Settings.bot_token
HTTP_HOST = Settings.http_host

logging.basicConfig(
    format='%(levelname)s [%(asctime)s]:%(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger('tasker_high')
logger.setLevel(loglevel)

bot = telepot.Bot(token)

try:
    conn = psycopg2.connect(Settings.dbstring)
    conn.autocommit = True
except:
    print("I am unable to connect to the database (connect1)")
cursor = conn.cursor()

while True:
    try:
        current_time = datetime.now()
        cursor.execute(all_veryhigh_query)
        users = cursor.fetchall()
        for telid in set(users):
            bot.sendMessage(
                telid[0],
                'У вас есть незакрытые задачи с высшим приоритетом.'
            )
        time.sleep(300)
    except Exception as e:
        logger.debug(e)
        exit(e)
