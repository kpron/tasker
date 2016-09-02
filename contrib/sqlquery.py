current_query = """
                SELECT *
                FROM tasks
                WHERE
                    start <= %(now)s
                    and
                    stop >= %(now)s
;"""

sent_query = """
             UPDATE tasks
             SET notify_send = %(status)s
             WHERE
                 id = %(id)s
;"""

insert_query = """
               INSERT
               INTO tasks
               (name,descr,start,stop,notify_need,notify_send)
               VALUES
               (%(name)s, %(descr)s, %(start)s, %(stop)s, %(notify_need)s, %(notify_send)s)
;"""

get_user_by_id = """
                 SELECT username
                 FROM users
                 WHERE
                     telegram_id = %(id)s
;"""

add_new_user = """
               INSERT
               INTO users
               (telegram_id, username, fname, lname)
               VALUES
               (%(id)s, %(nick)s, %(fname)s, %(lname)s)
;"""
