import psycopg2 as pg
import os
import sys
import hashlib


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

sys.path.append(os.path.join(ROOT_DIR, '..'))

from settings import postgres

BATCH_SIZE = 10000

def get_connection_string(
        host_address=None, port=None, database_name=None, user=None, password=None, **irrelevant_settings):
    string_parts = ["host={host} dbname={dbname}".format(
        **{'host': host_address, 'dbname': database_name})]

    if port:
        string_parts.append("port=" + str(port))

    if user:
        string_parts.append("user=" + user)

    if password:
        string_parts.append("password=" + password)

    return ' '.join(string_parts)


def compute_hashes(log_batch):
    output = []

    for log in log_batch:
        hasher = hashlib.sha512()
        hasher.update((''.join([str(value) for value in log[1:]])).encode('utf8'))
        row_hash = hasher.hexdigest()
        output.append({'id': log[0], 'row_hash': row_hash})

    return output


connection_string = get_connection_string(**postgres)

with pg.connect(connection_string) as connection:
    cursor = connection.cursor()
    cursor.execute("ALTER TABLE {0} ADD COLUMN row_hash text".format(postgres['table_name']))

with pg.connect(connection_string) as connection:
    with connection.cursor(name="select_all") as select_all_cursor, connection.cursor() as update_cursor:
        select_all_cursor.itersize = BATCH_SIZE
        query = "SELECT * FROM {0};".format(postgres['table_name'])
        select_all_cursor.execute(query)

        batch = []

        for row in select_all_cursor:
            batch.append(row)

            if len(batch) == BATCH_SIZE:
                ids_and_hashes = compute_hashes(batch)
                update_cursor.executemany('UPDATE {0} SET row_hash = %(row_hash)s WHERE id = %(id)s;'.format(postgres['table_name']), ids_and_hashes)
                batch = []

        if batch:
            ids_and_hashes = compute_hashes(batch)
            update_cursor.executemany('UPDATE {0} SET row_hash = %(row_hash)s WHERE id = %(id)s;'.format(postgres['table_name']), ids_and_hashes)