current_query = """
                SELECT *
                FROM tasks
                WHERE
                    start <= %(now)s
                    and
                    stop >= %(now)s
                    and
                    user_id = %(user_id)s
                    and
                    done = False
;"""

allcurrent_query = """
                   SELECT *
                   FROM tasks
                   WHERE
                      start <= %(now)s
                      and
                      stop >= %(now)s
;"""

done_query = """
             UPDATE tasks
             SET done = true
             WHERE
                 id = %(id)s
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
               (name,descr,start,stop,notify_need,notify_send,user_id)
               VALUES
               (%(name)s, %(descr)s, %(start)s, %(stop)s, %(notify_need)s, %(notify_send)s, %(user_id)s)
;"""

get_user_by_id = """
                 SELECT username, user_id
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

get_telid = """
               SELECT telegram_id
               FROM users
               WHERE
                   user_id = %(user_id)s
;"""

get_task_by_id = """
               SELECT *
               FROM tasks
               WHERE
                  id = %(id)s
;"""

pr_down_query = """
             UPDATE tasks
             SET pr = pr - 1
             WHERE
                 id = %(id)s
;"""

pr_up_query = """
             UPDATE tasks
             SET pr = pr + 1
             WHERE
                 id = %(id)s
;"""