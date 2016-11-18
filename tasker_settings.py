import os


class Settings():
    # Database
    dbhost = os.environ.get('DB_HOST', '127.0.0.1')
    dbname = os.environ.get('DB_NAME', 'tasker')
    dbuser = os.environ.get('DB_USER', 'tasker')
    dbpassword = os.environ.get('DB_PASS', 'tasker')
    # Tasker variables
    loglevel = os.environ.get('LOG_LEVEL', 'ERROR')
    mode = os.environ.get('MODE', 'master')
    super_port = os.environ.get('SUPER_PORT', '9001')
    # Notifier variables
    admin_id = os.environ.get('ADMIN_TELEGRAM_ID', 'tobeornottobe')
    bot_token = os.environ.get('BOT_TOKEN', 'ololotokenololo')
    http_host = os.environ.get('HTTP_HOST', 'example.com')
