#!/usr/bin/env python

from contrib.classes import Daemon
import sys
import time
from datetime import datetime
from yaml import load
import logging

logger = logging.getLogger('spam_application')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('/tmp/tasker.log')
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

    def function(self):
        pass


class Tasker(Daemon):
    def run(self):
        while True:
            try:
                inputfile = '/tmp/tasks.yaml'
                outputfile = '/tmp/tasker.out'
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
                logger.fatal(e)
                exit(e)

if __name__ == "__main__":
    daemon = Tasker('/tmp/tasker.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.status()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart|status" % sys.argv[0])
        sys.exit(2)
