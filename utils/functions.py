import csv
import pymysql
from flask import current_app as app

# CONNECTION HANDLER
def connect_now():
    connection = pymysql.connect(
        host='localhost',
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
    )
    return connection

# CSV TO TABLE FUNCTION
def insert_data_into_table(connection, table_name, csv_file_path):
    data = []
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            data.append(row)
    if all(value.isalpha() for value in data[0]):
        del data[0]
    data = to_null (data)
    with connection.cursor() as cursor:
        cursor.execute(f"SHOW COLUMNS FROM {table_name}") # THIS RETRIEVES THE COLUMNS NAMES SINCE THE PROVIDED CSVs DOESN'T HAVE HEADERS
        columns = cursor.fetchall()
        headers = ', '.join([column[0] for column in columns]) 
        for row in data:
            id_to_insert = row[0]
            check_query = f"SELECT COUNT(*) FROM {table_name} WHERE id = %s"
            cursor.execute(check_query, (id_to_insert,))
            exists = cursor.fetchone()[0]
            if not exists: # ONLY PROCEEDS WITH PREVIOUS ID CHECK IS FALSE
                values_placeholder = ', '.join(['%s'] * len(row))
                query = f"INSERT INTO {table_name} ({headers}) VALUES ({values_placeholder})"
                cursor.execute(query, row)
    return data

# EMPTY TO NULL TREATMENT
def to_null (data):
    for row_idx, row in enumerate(data):
        for value_idx, value in enumerate(row):
            if value == '':
                data[row_idx][value_idx] = None
    return data

