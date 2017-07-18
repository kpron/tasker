#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
import sys
from datetime import datetime, timedelta
import logging
import telepot
from telepot.namedtuple import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton)
import psycopg2
from contrib.sqlquery import *
from contrib.pr import PR, PRA
from contrib.tags import TAGS
from contrib.dateparser import dateparse
from contrib.dev.devbutton import devbutton
from tasker_settings import Settings

reload(sys)
sys.setdefaultencoding('utf8')

exec_dir = os.getcwd() + '/'

loglevel = Settings.loglevel
MODE = Settings.mode
SUPER_PORT = Settings.super_port
id = Settings.admin_id
token = Settings.bot_token
HTTP_HOST = Settings.http_host

logging.basicConfig(
    format='%(levelname)s [%(asctime)s]:%(message)s',
    level=logging.DEBUG
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
        tasks = [
            [task[0], task[1], task[2], task[9], isrepeadly(task[0])]
            for task in result
        ]
    logger.debug('TASKS :\n%s' % tasks)
    return tasks


def isrepeadly(tid):
    cursor.execute(get_repeat, {'tid': tid})
    result = cursor.fetchall()
    if result:
        return '\xF0\x9F\x94\x84'
    else:
        return ''


def getsubs(taskid):
    logger.debug('start GETSUBS')
    cursor.execute(get_subs_query, {
        'pid': taskid
    }
    )
    cids_array = cursor.fetchall()
    cids = tuple(map(lambda x: x[0], cids_array))
    logger.debug(cids)
    cursor.execute(multyget_task_query, {
        'ids': cids
    }
    )
    result = cursor.fetchall()
    if not result:
        tasks = []
    else:
        tasks = [
            [
                task[0],
                task[1],
                task[2],
                task[9] if not task[8] else 0,
                isrepeadly(task[0])
            ] for task in result
        ]
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
                text='%s %s %s' % (TASK[1], PR[TASK[3]]['icon'], TASK[4]),
                callback_data='desc %s' % TASK[0]
            )
        ] for TASK in sorted(tasks, key=lambda x: x[3], reverse=True)
    ])
    return {'tasks': tasks, 'kb': keyboard}


def gendone(tid):
    cursor.execute(get_subs_query, {
        'pid': tid
    }
    )
    cids_array = cursor.fetchall()
    if cids_array:
        cids = tuple(map(lambda x: x[0], cids_array))
        cursor.execute(multyget_task_query_opened, {
            'ids': cids
        }
        )
        result = cursor.fetchall()
    else:
        result = []
    if result:
        button = []
    else:
        pid = get_parent(tid)
        if pid:
            qdata = "subdone %s_%s" % (tid, pid)
            logger.debug('QDATA - %s' % qdata)
        else:
            qdata = "done %s" % tid
        button = [
            InlineKeyboardButton(
                text="done \xE2\x98\x91",
                callback_data=qdata
            )
        ]
    return button


def genback(tid):
    pid = get_parent(tid)
    if pid:
        btext = u"Subtasks \u25C0\uFE0F"
        qdata = "subback %s_%s" % (tid, pid)
        logger.debug('QDATA - %s' % qdata)
    else:
        btext = u"back \u25C0\uFE0F"
        qdata = "back %s" % tid
    button = [
        InlineKeyboardButton(
            text=btext,
            callback_data=qdata
        )
    ]
    return button


def pertaskeyboard(msg, tid, prior):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        gensub(tid),
        gendone(tid) + genprbt('top', prior, tid),
        genback(tid) + genprbt('down', prior, tid)
    ])
    return {'kb': keyboard}


def get_parent(tid):
    cursor.execute(get_parent_query, {'cid': tid})
    pid = cursor.fetchall()
    logger.debug(pid)
    if pid:
        return pid[0][0]
    else:
        return pid


def gensub(tid):
    cursor.execute(get_subs_query, {
        'pid': tid
    }
    )
    conn.commit()
    result = cursor.fetchall()
    if result:
        button = [InlineKeyboardButton(
            text="Subtasks",
            callback_data="sub %s" % tid
        )]
    else:
        button = []
    return button


def subinfo(taskid, msg, ormsg):
    cursor.execute(get_subs_query, {'pid': taskid})
    subs = cursor.fetchall()
    logger.debug(subs)
    keyboard = subboard(msg, taskid)['kb']
    try:
        bot.editMessageText(ormsg, text='Подзадачи:\n',
                            parse_mode='markdown',
                            reply_markup=keyboard
                            )
    except Exception as e:
        logger.debug('Exception: %s' % e)
        pass


def subboard(msg, tid):
    tasks = getsubs(tid)
    logger.debug('START generate SUBBOARD %s' % tid)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='%s %s %s' % (TASK[1], PR[TASK[3]]['icon'], TASK[4]),
                callback_data="desc %s" % (
                    TASK[0]
                )
            )
        ] for TASK in tasks
    ] + [
        [
            InlineKeyboardButton(
                text=u'Back \u25C0\uFE0F',
                callback_data="desc %s" % tid
            )
        ]
    ]
    )
    logger.debug(keyboard)
    return {'kb': keyboard}


def genprbt(level, pr, tid):
    if pr >= 2 and level == 'down':
        button = [InlineKeyboardButton(
            text=PRA['decrease'],
            callback_data="down %s" % tid
        )]
        return button
    elif pr <= 3 and level == 'top':
        button = [InlineKeyboardButton(
            text=PRA['raise'],
            callback_data="up %s" % tid
        )]
        return button
    else:
        return []


def mainboard(msg, ormsg):
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
    except Exception as e:
        logger.debug('Exception: %s' % e)
        pass


def basekeyboard(chat_id, keyboard, tasks):
    if tasks:
        message_text = "Список задач:"
    else:
        message_text = "Нет активных задач."
    bot.sendMessage(chat_id, message_text, reply_markup=keyboard)


def descboard(taskid, msg, ormsg):
    logger.debug('DROW descboard')
    cursor.execute(get_task_by_id, {'id': taskid})
    task_data = cursor.fetchall()
    prior = task_data[0][9]
    keyboard = pertaskeyboard(msg, taskid, prior)['kb']
    HEAD = 'Задача:\n\n<b>%s</b>\n<i>%s</i>\n\n<code>%s</code>'
    try:
        bot.editMessageText(ormsg, text=HEAD % (
            task_data[0][1],
            task_data[0][2],
            'Приоритет: %s' % PR[prior]['text']
        ),
            parse_mode='html',
            reply_markup=keyboard
        )
    except Exception as e:
        logger.debug('Exception: %s' % e)
        pass


def prshift(direct, tid):
    logger.debug('CHANGE PR')
    cursor.execute(get_task_by_id, {'id': tid})
    task_data = cursor.fetchall()
    prior = task_data[0][9]
    if direct == 'up':
        if (prior + 1) > 4:
            logger.debug('pizda break PR>4')
            return 'PR fail'
        QUERY = pr_up_query
    elif direct == 'down':
        if (prior - 1) < 1:
            logger.debug('pizda break PR<1')
            return 'PR fail'
        QUERY = pr_down_query
    cursor.execute(QUERY, {"id": tid})
    conn.commit()
    logger.debug('PR CHANGED for - %s' % tid)


def getsametask(userid, tname):
    cursor.execute(get_same_query, {'userid': userid, 'tname': tname})
    result = cursor.fetchall()
    if result:
        return {'id': result[0][0], 'descr': result[0][2]}
    else:
        return False


def getsubtask(line):
    parsed = {}
    cline = line.split('>', 1)
    logger.debug(cline)
    parsed['name'] = cline[0].strip()
    try:
        parsed['sub'] = cline[1].strip()
    except IndexError:
        parsed['sub'] = ''
    logger.debug(parsed)
    return parsed


def loop_check(pid, cid):
    logger.debug('%s %s' % (pid, cid))
    data = {'pid': str(pid), 'cid': str(cid)}
    logger.debug(data)
    cursor.execute(loop_check_query, data)
    result = cursor.fetchall()
    logger.debug(result)
    if result:
        logger.debug('Loop linking - block')
        return True
    else:
        return False


def linksubtask(parsedtitle):
    if parsedtitle['sub']:
        subtask = parsedtitle['name']
        cursor.execute(get_taskid_by_name, {'name': subtask})
        subtaskid = cursor.fetchall()[0][0]
        maintask = parsedtitle['sub']
        cursor.execute(get_taskid_by_name, {'name': maintask})
        try:
            maintaskid = cursor.fetchall()[0][0]
        except:
            logger.debug('Parent task not found - %s' % maintask)
            maintaskid = ''
        if maintaskid:
            logger.debug('maintaskid - %s' % maintaskid)
            logger.debug('subtaskid - %s' % subtaskid)
            if not loop_check(maintaskid, subtaskid):
                cursor.execute(link_query, {
                    'pid': maintaskid,
                    'cid': subtaskid
                })
                cursor.execute(set_state, {
                    'state': 2,
                    'tid': subtaskid
                })
                conn.commit()
    else:
        pass


def gettags(title):
    tags = []
    words = title.split(' ')
    for tag in TAGS.keys():
        if tag in words:
            tags.append(tag)
    return tags


def striptags(title, tags):
    for tag in tags:
        title = title.replace(tag, '')
    return title


def repeating(tid):
    logger.debug('ID OF REPEAT TASK - %s' % tid)
    cursor.execute(get_repeat, {'tid': tid})
    try:
        state = cursor.fetchall()[0][1]
        logger.debug('Current state - %s' % state)
        cursor.execute(update_repeat, {'tid': tid})
        conn.commit()
    except IndexError:
        cursor.execute(add_repeat, {'tid': tid})
        conn.commit()


def applytags(parsedtitle, tags):
    for tag in tags:
        if TAGS[tag]['name'] == 'Repeat':
            cursor.execute(get_taskid_by_name, {'name': parsedtitle['name']})
            try:
                tid = cursor.fetchall()[0][0]
                repeating(tid)
            except Exception as e:
                logger.error(e)


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
            ] + devbutton(MODE),
            resize_keyboard=True)
        bot.sendMessage(
            chat_id, 'Session has been initiated', reply_markup=markup
        )
    elif command == 'Active tasks':
        tasks = keyboardtasks(msg)['tasks']
        keyboard = keyboardtasks(msg)['kb']
        basekeyboard(chat_id, keyboard, tasks)
    elif command == 'Develop' and MODE == 'develop':
        message_text = 'Develop keyboard'
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Supervisor http',
                    url='http://%s:%s' % (HTTP_HOST, SUPER_PORT)
                )
            ]
        ])
        bot.sendMessage(chat_id, message_text, reply_markup=keyboard)
    else:
        mlist = msg['text'].split('\n')
        task = {}
        firstline = mlist[0].strip()
        tags = gettags(firstline)
        logger.debug(tags)
        strippedfline = striptags(firstline, tags)
        logger.debug('Stripped - %s' % strippedfline)
        parsedtitle = getsubtask(strippedfline)
        logger.debug('Parsed title - %s' % parsedtitle)
        task['name'] = parsedtitle['name']
        task['notify_need'] = False
        task['notify_send'] = False
        try:
            task['descr'] = mlist[1].strip()
        except IndexError:
            task['descr'] = ''
        try:
            start = dateparse(mlist[2].strip())
            if start:
                starttime = datetime.now() + timedelta(minutes=start)
                task['notify_need'] = True
            else:
                starttime = datetime.now() - timedelta(seconds=5)
        except IndexError:
            starttime = datetime.now() - timedelta(seconds=5)
        task['start'] = starttime
        task['stop'] = datetime.now() + timedelta(days=365)
        task['user_id'] = getuserid(getinfo(msg['from']))
        task['state'] = 1
        sameid = getsametask(task['user_id'], task['name'])
        if sameid:
            updated = '%s\n%s' % (
                sameid['descr'],
                task['descr']
            )
            cursor.execute(update_descr_query, {
                'descr': updated,
                'id': sameid['id']
            })
            conn.commit()
            logger.debug('%s task updated' % task['name'])
        else:
            cursor.execute(insert_query, task)
            conn.commit()
            logger.debug('%s task created' % task['name'])
        linksubtask(parsedtitle)
        applytags(parsedtitle, tags)
        tasks = keyboardtasks(msg)['tasks']
        keyboard = keyboardtasks(msg)['kb']
        basekeyboard(chat_id, keyboard, tasks)


def on_callback_query(msg):
    logger.debug('GET CALLBACK - %s' % msg)
    query_id, from_id, query_data = telepot.glance(
        msg, flavor='callback_query'
    )
    ormsg = telepot.origin_identifier(msg)
    job, taskid = query_data.split(" ")
    if job == "done":
        markasdone(taskid)
        mainboard(msg, ormsg)
    elif job == "subdone":
        logger.debug('SUBDONE - %s' % taskid)
        tid, pid = taskid.split("_")
        markasdone(tid)
        subinfo(pid, msg, ormsg)
    elif job == "desc":
        descboard(taskid, msg, ormsg)
    elif job == "subback":
        logger.debug('SUBBACK - %s' % taskid)
        tid, pid = taskid.split("_")
        subinfo(pid, msg, ormsg)
    elif job == "back":
        mainboard(msg, ormsg)
    elif job == "up":
        prshift('up', taskid)
        descboard(taskid, msg, ormsg)
    elif job == "down":
        prshift('down', taskid)
        descboard(taskid, msg, ormsg)
    elif job == "sub":
        subinfo(taskid, msg, ormsg)


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
    conn = psycopg2.connect(Settings.dbstring)
    conn.autocommit = True
except:
    print("I am unable to connect to the database (connect1)")
try:
    conn2 = psycopg2.connect(Settings.dbstring)
    conn2.autocommit = True
except:
    print("I am unable to connect to the database (connect2)")


cursor = conn.cursor()
cursor2 = conn2.cursor()

bot.message_loop({
    'chat': handle,
    'callback_query': on_callback_query
})
bot.sendMessage(id, 'tasker started - %s' % datetime.now())
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
                        "Task stared:\n<b>%s</b>\n<i>%s</i>" % (
                            task.name, task.descr
                        ),
                        parse_mode='html'
                    )
                except Exception as sent:
                    logger.error(sent)
                finally:
                    task.mark_sent()
        time.sleep(1)
    except Exception as e:
        logger.debug(e)
        exit(e)
