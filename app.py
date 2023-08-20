from flask import Flask, request, jsonify
import os
import csv
import pymysql
import json

app = Flask(__name__)

# MYSQL CONFIGURATION
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'api_user'
app.config['MYSQL_PASSWORD'] = 'globant123' #nerver hardcode sensitive information, this is just for demonstration purpose
app.config['MYSQL_DB'] = 'globant_test'
app.config['MYSQL_CURSORCLASS'] = 'pymysql.cursors.DictCursor'

# SPECIFY HERE THE HISTORICAL DATA


# ROUTES

# Test route to retrieve data from the database
# @app.route('/test', methods=['GET'])
# def test_database():
#     connection = pymysql.connect(
#         host=app.config['MYSQL_HOST'],
#         user=app.config['MYSQL_USER'],
#         password=app.config['MYSQL_PASSWORD'],
#         db=app.config['MYSQL_DB'],
#     )
#     cursor = connection.cursor()
#     cursor.execute('SELECT * FROM departments')
#     data = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return jsonify(data)

# ROUTE TO UPLOAD TABLES WITH HISTORICAL LOCAL CSV DATA
@app.route('/api/historical_data_up')
def historical_data_up():
    connection = pymysql.connect( # CALLING CONNECT FROM PYMSQL
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
    )
    HISTORICAL_DATA_FOLDER = './files'
    with open('historical_tables_config.json', 'r') as config_file:
        table_config = json.load(config_file)
    for table_info in table_config['tables']:
        table_name = table_info['name']
        csv_file_path = os.path.join(HISTORICAL_DATA_FOLDER, f'{table_name}.csv') # RETRIEVING PATH FOR EACH FILE

                # BUILDING THE QUERY
        data = []
        with connection.cursor() as cursor: # THIS RETRIEVES THE COLUMNS NAMES SINCE THE PROVIDED CSVs DOESN'T HAVE HEADERS
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = cursor.fetchall()
            keys = ', '.join([column[0] for column in columns])  # Extract the first element of each tuple
        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                data.append(row)
        
        for row_idx, row in enumerate(data):
            for value_idx, value in enumerate(row):
                if value == '':
                    data[row_idx][value_idx] = None

        # Insert data into the corresponding table
        with connection.cursor() as cursor:
            for row in data:
                values_placeholder = ', '.join(['%s'] * len(row))
                query = f"INSERT INTO {table_name} ({keys}) VALUES ({values_placeholder})"
                cursor.execute(query, row)
    connection.commit()  # Commit the changes to the database
    connection.close()  # Close the connection

    return "Data uploaded successfully."

