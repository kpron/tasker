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
                 id = %(id)s;
;"""

insert_query = """
               INSERT
               INTO tasks
               (name,descr,start,stop,notify_need,notify_send)
               VALUES
               (%(name)s, %(descr)s, %(start)s, %(stop)s, %(notify_need)s, %(notify_send)s)
;"""
