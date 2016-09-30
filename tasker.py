#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
from datetime import datetime, timedelta
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
src_dir = parser.get('tasker', 'srs_dir')

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
    filename='%s/logs/tasker.log' % src_dir
)
logger = logging.getLogger('tasker')
logger.setLevel(loglevel)

bot = telepot.Bot(token)


def getinfo(data):
    info = dict()
    info['fname'] = data.get('first_name', 'Not set')
    info['lname'] = data.get('last_name', 'Not set')
    info['nick'] = data.get('username', 'Not set')
    info['id'] = data.get('id', 'Not set')
    return info


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
    elif command == 'New task':
        text = 'Example:\n<task name>/<description>/<begin>/<end>/nn/ns'
        bot.sendMessage(chat_id, str(text), reply_markup=None)
    elif command == '/start':
        info = getinfo(msg['from'])
        cursor.execute(get_user_by_id, {'id': info['id']})
        result = cursor.fetchall()
        if not result:
            cursor.execute(add_new_user, info)
            logger.debug(
                'Added new user - nickname: %(nick)s (%(fname)s %(lname)s)' % (
                    info
                )
            )
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Active tasks'),
                    KeyboardButton(text='New task')
                ]
            ])
        bot.sendMessage(
            chat_id, 'Session has been initiated', reply_markup=markup
        )
    elif command == 'info':
        info = getinfo(msg['from'])
        info_message = u'''Немного информации -
Name: %(fname)s
Last name: %(lname)s
Nickname: %(nick)s
Telegram ID: %(id)s''' % (
            info
        )
        cursor.execute(get_user_by_id, {'id': info['id']})
        result = cursor.fetchall()
        if not result:
            cursor.execute(add_new_user, info)
            logger.debug(
                'Added new user - Nick: %(nick)s (%(fname)s %(lname)s)m ' % (
                    info
                )
            )
        bot.sendMessage(chat_id, info_message)
    else:
        mlist = msg['text'].split('/')
        task = {}
        task['name'] = mlist[0]
        try:
            task['descr'] = mlist[1] or 'Non set'
        except IndexError:
            task['descr'] = 'Non set'
        logger.debug('name - %(name)s\ndesc - %(descr)s' % task)
        task['start'] = datetime.now()
        task['stop'] = datetime.now() + timedelta(1*365/12)
        task['notify_need'] = True
        task['notify_send'] = False
        cursor.execute(insert_query, task)
        result = cursor.fetchall()
        bot.sendMessage(chat_id, '%s - task created' % task['name'])


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
