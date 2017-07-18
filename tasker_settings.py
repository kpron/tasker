import os
import urlparse

class Settings():
    # Database
    urlparse.uses_netloc.append("postgres")
    dburl = urlparse.urlparse(os.environ["DATABASE_URL"])
    dbstring = "dbname=%s user=%s password=%s host=%s port=%s" % (dburl.path[1:], dburl.username, dburl.password, dburl.hostname, dburl.port)
    # Tasker variables
    loglevel = os.environ.get('LOG_LEVEL', 'ERROR')
    mode = os.environ.get('MODE', 'master')
    super_port = os.environ.get('SUPER_PORT', '9001')
    # Notifier variables
    admin_id = os.environ.get('ADMIN_TELEGRAM_ID', 'tobeornottobe')
    bot_token = os.environ.get('BOT_TOKEN', 'ololotokenololo')
    http_host = os.environ.get('HTTP_HOST', 'example.com')
