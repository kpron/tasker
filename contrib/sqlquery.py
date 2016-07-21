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