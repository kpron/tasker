#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
from datetime import datetime, timedelta
import logging
from ConfigParser import SafeConfigParser
import telepot
from telepot.namedtuple import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton)
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
    logger.debug('start GETINFO')
    info = dict()
    info['fname'] = data.get('first_name', 'Not set')
    info['lname'] = data.get('last_name', 'Not set')
    info['nick'] = data.get('username', 'Not set')
    info['id'] = data.get('id', 'Not set')
    return info


def getuserid(info):
    logger.debug('start GETUSERID')
    cursor.execute(get_user_by_id, {'id': info['id']})
    conn.commit()
    result = cursor.fetchall()
    if not result:
        reguser(info)
        cursor.execute(get_user_by_id, {'id': info['id']})
        result = cursor.fetchall()
        return result[0][1]
    else:
        return result[0][1]


def reguser(info):
    logger.debug('start REGUSER')
    cursor.execute(add_new_user, info)
    conn.commit()
    bot.sendMessage(id, '%s - user created' % info)
    logger.debug(
        'Added new user - Nick: %(nick)s (%(fname)s %(lname)s)' % (
            info
        )
    )


def getasks(msg):
    logger.debug('start GETTASKS')
    info = getinfo(msg['from'])
    user_id = getuserid(info)
    cursor.execute(current_query, {
        'now': datetime.now(),
        'user_id': user_id
    }
    )
    conn.commit()
    result = cursor.fetchall()
    if not result:
        tasks = []
    else:
        tasks = [[task[0], task[1], task[2]] for task in result]
    return tasks


def markasdone(taskid):
    logger.debug('start MARKASDONE')
    cursor.execute(done_query, {"id": taskid})
    conn.commit()
    logger.debug('marks as done - %s' % taskid)


def keyboardtasks(msg):
    tasks = getasks(msg)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=TASK[1],
                callback_data="desc %s" % TASK[0]
            ),
            InlineKeyboardButton(
                text="done \xE2\x98\x91",
                callback_data="done %s" % (
                    TASK[0]
                )
            )
        ] for TASK in tasks
    ])
    return {'tasks': tasks, 'kb': keyboard}


def basekeyboard(chat_id, keyboard, tasks):
    if tasks:
        message_text = "Список задач:"
    else:
        message_text = "Нет активных задач."
    bot.sendMessage(chat_id, message_text, reply_markup=keyboard)


def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    logger.debug('Got command: %s' % command)

    if command == 'Inline tasks':
        tasks = getasks(msg)
        text = 'Active tasks for now (%s)\n' % (
            current_time.strftime("%Y-%m-%d %H:%M")
        )
        for task in tasks:
            text += '*%s* - _%s_\n' % (task[1], task[2])
        bot.sendMessage(chat_id, str(text), parse_mode='markdown')
    elif command == 'New task':
        text = 'Example:\n<task name>\n<description>\n<begin>\n<end>'
        bot.sendMessage(chat_id, str(text), reply_markup=None)
    elif command == '/start':
        info = getinfo(msg['from'])
        getuserid(info)
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Active tasks')
                ]
            ])
        bot.sendMessage(
            chat_id, 'Session has been initiated', reply_markup=markup
        )
    elif command == 'Active tasks':
        tasks = keyboardtasks(msg)['tasks']
        keyboard = keyboardtasks(msg)['kb']
        basekeyboard(chat_id, keyboard, tasks)
    else:
        mlist = msg['text'].split('\n')
        task = {}
        task['name'] = mlist[0].strip()
        try:
            task['descr'] = mlist[1].strip()
        except IndexError:
            task['descr'] = 'No description'
        try:
            start = mlist[2].strip()
            if start == '1':
                starttime = datetime.now() + timedelta(hours=1)
            else:
                starttime = datetime.now() - timedelta(seconds=5)
        except IndexError:
            starttime = datetime.now() - timedelta(seconds=5)
        task['start'] = starttime
        task['stop'] = datetime.now() + timedelta(hours=24)
        task['notify_need'] = True
        task['notify_send'] = False
        task['user_id'] = getuserid(getinfo(msg['from']))
        cursor.execute(insert_query, task)
        conn.commit()
        logger.debug('%s task created' % task['name'])
        tasks = keyboardtasks(msg)['tasks']
        keyboard = keyboardtasks(msg)['kb']
        basekeyboard(chat_id, keyboard, tasks)


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(
        msg, flavor='callback_query'
    )
    ormsg = telepot.origin_identifier(msg)
    job, taskid = query_data.split(" ")
    if job == "done":
        logger.debug('Callback Query: %s %s %s' % (
            query_id, from_id, query_data))
        markasdone(taskid)
        keyboard = keyboardtasks(msg)['kb']
        if keyboardtasks(msg)['tasks']:
            message_text = "Список задач:"
        else:
            message_text = "Нет активных задач."
        try:
            bot.editMessageText(ormsg, text=message_text,
                                parse_mode='markdown',
                                reply_markup=keyboard
                                )
        except:
            pass
    elif job == "desc":
        logger.debug(query_data)
        cursor.execute(get_task_by_id, {'id': taskid})
        task_data = cursor.fetchall()
        keyboard = keyboardtasks(msg)['kb']
        try:
            bot.editMessageText(ormsg, text='*%s*\n_%s_' % (
                task_data[0][1],
                task_data[0][2],
            ),
                parse_mode='markdown',
                reply_markup=keyboard
            )
        except:
            pass


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
        self.userid = self.data[7]

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
                cursor2.execute(sent_query, {'id': self.id, 'status': True})
                conn2.commit()

    def get_telid(self):
        cursor2.execute(get_telid, {'user_id': self.userid})
        telid = cursor2.fetchall()
        return telid[0][0]


try:
    conn = psycopg2.connect(connstring)
    conn.autocommit = True
except:
    print("I am unable to connect to the database (connect1)")
try:
    conn2 = psycopg2.connect(connstring)
    conn2.autocommit = True
except:
    print("I am unable to connect to the database (connect2)")
cursor = conn.cursor()
cursor2 = conn2.cursor()

bot.message_loop({
    'chat': handle,
    'callback_query': on_callback_query
})
logger.info('kpronbot listening ...')

while True:
    try:
        current_time = datetime.now()
        cursor2.execute(allcurrent_query, {'now': current_time})
        tasks = cursor2.fetchall()
        for item in tasks:
            task = Task(item)
            if task.notify_need():
                try:
                    bot.sendMessage(
                        task.get_telid(),
                        "Task stared:\n*%s*\n_%s_" % (
                            task.name, task.descr
                        ),
                        parse_mode='markdown'
                    )
                except Exception as sent:
                    logger.error(sent)
                finally:
                    task.mark_sent()
        time.sleep(1)
    except Exception as e:
        logger.debug(e)
        exit(e)
