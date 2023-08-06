from django.db import connection


def show_readonly_state():
    with connection.cursor() as c:
        c.execute("show global VARIABLES like 'read_only'")
        result = c.fetchone()
        if result[1].lower() == 'on':
            return True
        else:
            return False


def show_select_num():
    with connection.cursor() as c:
        c.execute("show global status like 'com_select';")
        result = c.fetchone()
        return result[1]


def show_insert_num():
    with connection.cursor() as c:
        c.execute("show global status like 'com_insert';")
        result = c.fetchone()
        return result[1]


def show_update_num():
    with connection.cursor() as c:
        c.execute("show global status like 'com_update';")
        result = c.fetchone()
        return result[1]


def show_thread_connected_num():
    with connection.cursor() as c:
        c.execute("show status like 'threads_connected';")
        result = c.fetchone()
        return result[1]


def show_connection_num():
    with connection.cursor() as c:
        c.execute("show status like 'connections';")
        result = c.fetchone()
        return result[1]
