#!/usr/bin/env python

import time
import os
from datetime import datetime
import logging
from ConfigParser import SafeConfigParser
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import psycopg2
from contrib.sqlquery import *

parser = SafeConfigParser()
parser.read('config.ini')

exec_dir = os.getcwd() + '/'

# Tasker variables
inputfile = exec_dir + parser.get('tasker', 'tasksfile')
outputfile = exec_dir + parser.get('tasker', 'outfile')
loglevel = parser.get('tasker', 'loglevel')

# Notifier variables
id = parser.get('tasker-notifier', 'telegram_id')
token = parser.get('tasker-notifier', 'bot_token')

# database variables
dbhost = parser.get('pgsql', 'host')
dbname = parser.get('pgsql', 'db')
dbuser = parser.get('pgsql', 'user')
dbpassword = parser.get('pgsql', 'password')

connstring = "dbname=%s user=%s host=%s password=%s" % (
    dbname, dbuser, dbhost, dbpassword
)

logging.basicConfig(
    format='%(levelname)s [%(asctime)s]:%(message)s',
    level=logging.DEBUG,
    filename='/home/kpron/kpronProjects/tasker/logs/tasker.log'
)
logger = logging.getLogger('tasker')
logger.setLevel(loglevel)

bot = telepot.Bot(token)


def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    logger.debug('Got command: %s' % command)

    if command == 'Active tasks':
        cursor.execute(current_query, {'now': current_time})
        result = cursor.fetchall()
        tasks = [[task[1], task[2]] for task in result]
        text = 'Active tasks for now (%s)\n' % (
            current_time.strftime("%Y-%m-%d %H:%M")
        )
        for task in tasks:
            text += '%s - %s\n' % (task[0], task[1])
        bot.sendMessage(chat_id, str(text))
    elif command == 'tasks':
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Active tasks')]
            ])
        bot.sendMessage(chat_id, 'Custom keyboard', reply_markup=markup)


class Task(object):
    """Simple task class. Has few methods."""

    def __init__(self, data):
        super(Task, self).__init__()
        self.data = data
        self.id = self.data[0]
        self.name = self.data[1]
        self.descr = self.data[2]
        self.notify = self.data[5]
        self.sent = self.data[6]

    def notify_need(self):
        if self.notify:
            if not self.sent:
                return(True)
            else:
                return(False)
        else:
            return(False)

    def mark_sent(self):
        if self.notify:
            if not self.sent:
                cursor.execute(sent_query, {'id': self.id, 'status': True})

try:
    conn = psycopg2.connect(connstring)
    conn.autocommit = True
except:
    print("I am unable to connect to the database")
cursor = conn.cursor()

bot.message_loop(handle)
logger.info('kpronbot listening ...')

while True:
    try:
        current_time = datetime.now()
        cursor.execute(current_query, {'now': current_time})
        tasks = cursor.fetchall()
        for item in tasks:
            task = Task(item)
            if task.notify_need():
                try:
                    bot.sendMessage(
                        id,
                        "%s\n%s" % (
                            task.name, task.descr
                        )
                    )
                except Exception as sent:
                    logger.error(sent)
                finally:
                    task.mark_sent()
        time.sleep(1)
    except Exception as e:
        logger.debug(e)
        exit(e)
