import sqlite3


def init_connection(path_to_database):
    connection = sqlite3.connect(path_to_database)
    cursor = connection.cursor()
    return connection, cursor


def query_exist(connection, name, table_name):
    """
    query whether a scientist exists in a particular table
    :param connection: to the database
    :param name: the scientist's name
    :param table_name: the name of the table
    :return: False if no, otherwise, yes
    """
    result = connection.execute("SELECT * from {} where name is (?)".format(table_name), (name, ))
    # result = connection.execute("SELECT name from physical_sci where name is 'Jules_Aarons'")
    result = result.fetchall()
    if len(result) == 0:
        return False
    else:
        return True


def get_inner_product(connection):
    """
    Get scientists who are both titled as mathematician and physical scientists directly from the inner product
    :param connection: to the database
    :return: inner product result
    """
    result = connection.execute(\
        'SELECT \
            mathematicians.name \
        FROM \
            mathematicians \
        INNER JOIN \
            physical_sci \
        ON mathematicians.name = physical_sci.name\
        ')

    return result


