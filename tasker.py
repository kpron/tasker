#!/usr/bin/env python

import time
import os
import sys
from datetime import datetime
from yaml import load
import logging
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('config.ini')

exec_dir = os.getcwd() + '/'

inputfile = exec_dir + parser.get('tasker', 'tasksfile')
outputfile = exec_dir + parser.get('tasker', 'outfile')

logger = logging.getLogger('tasker')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(str(sys.stderr))
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


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

while True:
    try:
        with open(inputfile, "r") as f:
            data = load(f)
        active_tasks = []
        for task in data:
            t = Task(task)
            if t.date_in():
                active_tasks.append(t.get_name())
        open(outputfile, 'w').write("%s" % active_tasks)
        f.close()
        time.sleep(1)
    except Exception as e:
        logger.debug(e)
        exit(e)
