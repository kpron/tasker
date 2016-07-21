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

cursor.execute(current_query, {'now': current_time})
tasks = cursor.fetchall()
print(tasks)

cursor.execute(sent_query, {'id': 1, 'status': False})
cursor.execute(sent_query, {'id': 2, 'status': True})

cursor.execute(current_query, {'now': current_time})
tasks = cursor.fetchall()
print(tasks)
