import json
import logging
import os
import pymysql

def get_connection(connection_config):
    try:
        connection_conf = {
            "host": connection_config.get("HOST"),
            "database": connection_config.get("NAME"),
            "user": connection_config.get("USER"),
            "password": connection_config.get("PASSWORD"),
            "port": connection_config.get("PORT"),
        }
        connection = pymysql.connect(**connection_conf)
        return connection
    except Exception as e:
        logging.error(
            f'error:unable to establish connection with database for {connection_conf}, message: {str(e)},' 
                f'log_key: get_connection')
        return None


def execute_select(query, where_clause, connection_obj):
    cursor = connection_obj.cursor()
    try:
        cursor.execute(query, where_clause)
        columns = cursor.description
        result = [{columns[index][0]:column for index, column in enumerate(
            value)} for value in cursor.fetchall()]
        # connection_obj.close()
        cursor.close()
        return result
    except Exception as e:
        logging.error(
                    f'Error thrown while selecting query, message: {str(e)}, log_key: execute_select')
        return None

def execute_insert(connection_obj, table_name, parameters):
    cursor = connection_obj.cursor()
    values = ', '.join(['%s'] * len(parameters["columns"]))
    columns = ', '.join(parameters["columns"])
    query = "INSERT into %s ( %s ) VALUES ( %s )" % (table_name, columns, values)
    try:
        cursor.executemany(query, parameters["values"])
        connection_obj.commit()
        connection_obj.close()
        cursor.close()
        return cursor.rowcount
    except Exception as e:
        logging.error(
            f'Error thrown while inserting query : {json.dumps(parameters["values"])}., message: {str(e)},'
                f'log_key: update_data_by_id')
        return None

def update_data_by_id(connection_obj, table, q_data, u_data):
    cursor = connection_obj.cursor()

    set_data = ', '.join([f"{key} = %s" for key in u_data])
    where_q = ' AND '.join([f"{key} in %s" if type(q_data.get(key)) == tuple else f"{key} = %s" for key in q_data])

    query = "UPDATE %s SET %s WHERE %s" % (table, set_data, where_q)
    values = list(u_data.values()) + list(q_data.values())
    try:
        cursor.execute(query, values)
        connection_obj.commit()
        connection_obj.close()
        cursor.close()
        return {'last_row_id': cursor.lastrowid, 'row_count': cursor.rowcount}
    except Exception as e:
        logging.error(
            f'Error thrown while updating query : {json.dumps(q_data)}., message: {str(e)},'
             f'log_key: update_data_by_id')
        return None

def execute_delete(connection_obj, query, where_clause):
    cursor = connection_obj.cursor()
    try:
        cursor.execute(query, where_clause)
        connection_obj.commit()
        connection_obj.close()
        cursor.close()
        return {'last_row_id': cursor.lastrowid, 'row_count': cursor.rowcount}
    except Exception as e:
        logging.error({
            "error": e,
            "message": "error occurred while deleting data from mysql table",
            "logkey": "mysql_helper"
        })
        return {'success': False, 'exception': e}