#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import os
from datetime import datetime
import telepot
import psycopg2
from contrib.sqlquery import *

loglevel = os.environ.get('LOG_LEVEL', 'ERROR')
token = os.environ.get('BOT_TOKEN')

logging.basicConfig(
    format='%(levelname)s [%(asctime)s]:%(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger('tasker_high')
logger.setLevel(loglevel)

# database variables
dbhost = os.environ.get('DB_HOST')
dbname = os.environ.get('DB_NAME')
dbuser = os.environ.get('DB_USER')
dbpassword = os.environ.get('DB_PASS')

connstring = "dbname=%s user=%s host=%s password=%s" % (
    dbname, dbuser, dbhost, dbpassword
)

bot = telepot.Bot(token)

try:
    conn = psycopg2.connect(connstring)
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
        time.sleep(900)
    except Exception as e:
        logger.debug(e)
        exit(e)
