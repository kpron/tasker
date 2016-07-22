import psycopg2
from datetime import datetime
from ConfigParser import SafeConfigParser
from contrib.sqlquery import *

parser = SafeConfigParser()
parser.read('config.ini')

dbhost = parser.get('pgsql', 'host')
dbname = parser.get('pgsql', 'db')
dbuser = parser.get('pgsql', 'user')
dbpassword = parser.get('pgsql', 'password')

connstring = "dbname=%s user=%s host=%s password=%s" % (
    dbname, dbuser, dbhost, dbpassword
)

try:
    conn = psycopg2.connect(connstring)
    conn.autocommit = True
except:
    print("I am unable to connect to the database")

current_time = datetime.now()

cursor = conn.cursor()

name = 'Back to work'
descr = 'A lot of information in this field. Really big string.'
start = '2016-07-22 10:30:00'
stop = '2016-07-22 11:00:00'
notify_need = 'True'
notify_send = 'False'
cursor.execute(insert_query, {
    'name': name,
    'descr': descr,
    'start': start,
    'stop': stop,
    'notify_need': notify_need,
    'notify_send': notify_send
})