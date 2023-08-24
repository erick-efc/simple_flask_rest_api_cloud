import csv
import pymysql
from flask import jsonify, current_app as app

# CONNECTION HANDLER
def connect_now():
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        port=app.config['MYSQL_PORT']
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
            sanitized_row = []
            for value in row:
                if value == "":
                    sanitized_row.append(None)
                elif value.isdigit():
                    sanitized_row.append(int(value))
                else:
                    sanitized_row.append(value)
            data.append(sanitized_row)
    if all(isinstance(value, str) for value in data[0]):
        del data[0]
    try:
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
        return jsonify({'message': 'Data inserted successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# TO SORT BASED ON HIERARCHY OF OUR GB
def sort(update_order, target_list):
    position_map = {element: position for position, element in enumerate(update_order)}
    sorted_target_list = sorted(target_list, key=lambda x: position_map.get(x, float('inf')))
    return sorted_target_list

# RUN QUERY
def execute_query(query):
    try:
        connection = connect_now()
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        response = [dict(zip(columns, row)) for row in result]
        return response
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
