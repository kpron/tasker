#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
from ConfigParser import SafeConfigParser
from datetime import datetime
import telepot
import psycopg2
from contrib.sqlquery import *

parser = SafeConfigParser()
parser.read('config.ini')

loglevel = parser.get('tasker_high', 'loglevel')
src_dir = parser.get('tasker_high', 'srs_dir')
token = parser.get('tasker-notifier', 'bot_token')

logging.basicConfig(
    format='%(levelname)s [%(asctime)s]:%(message)s',
    level=logging.DEBUG,
    filename='%s/logs/tasker_high.log' % src_dir
)

logger = logging.getLogger('tasker_high')
logger.setLevel(loglevel)

# database variables
dbhost = parser.get('pgsql', 'host')
dbname = parser.get('pgsql', 'db')
dbuser = parser.get('pgsql', 'user')
dbpassword = parser.get('pgsql', 'password')

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
        cursor.execute(all_high_query)
        tasks = cursor.fetchall()
        for user_id in set(tasks):
            cursor.execute(get_telid, {'user_id': user_id[0]})
            telid = cursor.fetchall()
            bot.sendMessage(
                telid[0][0],
                'У вас есть незакрытые задачи с высшим приоритетом.'
            )
        time.sleep(900)
    except Exception as e:
        logger.debug(e)
        exit(e)
