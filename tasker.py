#!/usr/bin/env python

import time
import os
from datetime import datetime
from yaml import load, dump
import logging
from ConfigParser import SafeConfigParser
import telepot

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

logging.basicConfig(
    format='%(levelname)s [%(asctime)s]:%(message)s',
    level=logging.DEBUG,
    filename='/home/kpron/kpronProjects/tasker/logs/tasker.log'
)
logger = logging.getLogger('tasker')
logger.setLevel(loglevel)

bot = telepot.Bot(token)


class Task(object):
    """Simple task class. Has few methods."""

    def __init__(self, data):
        super(Task, self).__init__()
        self.data = data
        self.name = ''.join(self.data.keys())
        self.info = self.data[self.name]
        self.start = self.info["start"]
        self.end = self.info["end"]
        self.nows = time.strftime("%H:%M")
        self.nowd = datetime.strptime(self.nows, "%H:%M")
        self.notify = self.info["notify"]

    def get_time(self):
        """Return task time interval as string "start - end" """
        return("%s - %s" % (self.start, self.end))

    def get_name(self):
        """Return task name as a string"""
        return(self.name)

    def get_data(self):
        """Return task data (all of this)"""
        return(self.data)

    def get_info(self):
        """Return task info (all of this, except name)"""
        return(self.info)

    def date_in(self):
        """Return bool value. True if task is active and False if not."""
        self.startd = datetime.strptime(self.start, "%H:%M")
        self.endd = datetime.strptime(self.end, "%H:%M")
        if self.nowd >= self.startd and self.nowd <= self.endd:
            return True
        else:
            return False

    def notify_need(self):
        if self.notify:
            if not self.notify["sent"]:
                return(True)
            else:
                return(False)
        else:
            return(False)

    def mark_sent(self):
        if self.notify:
            if not self.notify["sent"]:
                changed = self.data
                changed[self.name]["notify"]["sent"] = True
                return(changed)

while True:
    try:
        with open(inputfile, "r") as f:
            data = load(f)
            logger.debug(data)
        active_tasks = [time.strftime("%H:%M:%S")]
        for task in data:
            t = Task(task)
            if t.date_in():
                if t.notify_need():
                    logger.info("Need notify for - %s" % t.get_name())
                    if bot.sendMessage(id, t.get_name()):
                        logger.info("Notify sent.")
                        data.remove(task)
                        data.append(t.mark_sent())
                    else:
                        logger.info("Error while sending notify")
                else:
                    active_tasks.append([t.get_name()])
        # logger.debug(dump(data, default_flow_style=False))
        with open(inputfile, "w") as w:
            w.write(dump(data, default_flow_style=False))
            w.close()
        f.close()
        time.sleep(10)
    except Exception as e:
        logger.debug(e)
        exit(e)
