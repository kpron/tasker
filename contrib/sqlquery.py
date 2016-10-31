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
                    and
                    state = 1
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
               (name,descr,start,stop,notify_need,notify_send,user_id,state)
               VALUES
               (%(name)s, %(descr)s, %(start)s, %(stop)s, %(notify_need)s, %(notify_send)s, %(user_id)s, %(state)s)
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

all_veryhigh_query = """
               SELECT users.telegram_id
               FROM tasks, users
               WHERE
                  tasks.pr = 4
                  and
                  tasks.done = False
                  and
                  users.user_id = tasks.user_id
;"""

get_same_query = """
               SELECT *
               FROM tasks
               WHERE
                  user_id = %(userid)s
                  and
                  name = %(tname)s
                  and
                  done = False
;"""

update_descr_query = """
             UPDATE tasks
             SET descr = %(descr)s
             WHERE
                 id = %(id)s
;"""

get_subs_query = """
               SELECT cid
               FROM subtasks
               WHERE
                  pid = %(pid)s
;"""

multyget_task_query = """
                SELECT *
                FROM tasks
                WHERE
                    id in %(ids)s
;"""

multyget_task_query_opened = """
                SELECT *
                FROM tasks
                WHERE
                    id in %(ids)s
                    and
                    done = False
;"""

get_parent_query = """
                 SELECT pid
                 FROM subtasks
                 WHERE
                    cid = %(cid)s
;"""

get_taskid_by_name = """
                SELECT id
                FROM tasks
                WHERE
                    name = %(name)s
                    and
                    done = False
;"""

link_query = """
                INSERT INTO subtasks
                VALUES (
                    %(pid)s,
                    %(cid)s
                    )
;"""

set_state = """
             UPDATE tasks
             SET state = %(state)s
             WHERE
                 id = %(tid)s
;"""

loop_check_query = """
                SELECT *
                FROM subtasks
                WHERE
                    cid = %(pid)s
                    and
                    pid = %(cid)s
;"""

add_repeat = """
            INSERT INTO repeat_tasks
            VALUES (
                %(tid)s,
                0
                )
;"""

update_repeat = """
             UPDATE repeat_tasks
             SET state = 1
             WHERE
                 id = %(tid)s
;"""

get_repeat = """
                SELECT *
                FROM repeat_tasks
                WHERE
                    id = %(tid)s
;"""
