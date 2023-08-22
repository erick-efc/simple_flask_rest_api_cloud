from flask import Flask, request, jsonify
import os
import csv
import pymysql

app = Flask(__name__)

# MYSQL CONFIGURATION
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'api_user'
app.config['MYSQL_PASSWORD'] = 'globant123' #nerver hardcode sensitive information, this is just for demonstration purpose
app.config['MYSQL_DB'] = 'globant_test'
app.config['MYSQL_CURSORCLASS'] = 'pymysql.cursors.DictCursor'
    
# CSV TO TABLE FUNCTION
def insert_data_into_table(connection, table_name, headers, csv_file_path):
    data = []
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            data.append(row)
    if all(value.isalpha() for value in data[0]):
        del data[0]
    data = to_null (data)
    with connection.cursor() as cursor:
        for row in data:
            id_to_insert = row[0]
            check_query = f"SELECT COUNT(*) FROM {table_name} WHERE id = %s"
            cursor.execute(check_query, (id_to_insert,))
            exists = cursor.fetchone()[0]
            if not exists:
                values_placeholder = ', '.join(['%s'] * len(row))
                query = f"INSERT INTO {table_name} ({headers}) VALUES ({values_placeholder})"
                cursor.execute(query, row)
    return data

# EMPTY TO NULL
def to_null (data):
    for row_idx, row in enumerate(data):
        for value_idx, value in enumerate(row):
            if value == '':
                data[row_idx][value_idx] = None
    return data


################################################
# ROUTE TO RETRIEVE TABLES WITH HISTORICAL DATA
################################################
@app.route('/api/historical_data_up')
def historical_data_up():
    try:
        HISTORICAL_DATA_FOLDER = './historical_data'
        connection = pymysql.connect(
        host='localhost',
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        )
        uptade_order = ["departments", "jobs", "hired_employees"] # HIRED_EMPLOYEES IS A CHILD TABLE IN THE SCHEMA
        for table in uptade_order:
            table_name = table
            csv_file_path = os.path.join(HISTORICAL_DATA_FOLDER, f'{table_name}.csv')
            with connection.cursor() as cursor: # THIS RETRIEVES THE COLUMNS NAMES SINCE THE PROVIDED CSVs DOESN'T HAVE HEADERS
                cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                columns = cursor.fetchall()
                keys = ', '.join([column[0] for column in columns]) 
            insert_data_into_table(connection, table_name, keys, csv_file_path)  
        connection.commit() 
        return jsonify({'message': 'Data uploaded successfully'}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        connection.close()

################################################
# UPLOAD FILES ROUTE
################################################
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        UPLOAD_FOLDER = './uploads'  
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
        return jsonify({'message': 'File uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
################################################
# UPDATE DB WITH A CSV
################################################
@app.route('/update_db_csv', methods=['POST'])
def update_db_csv():
    try:
        UPLOAD_FOLDER = './uploads'  
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
        connection = pymysql.connect(
            host='localhost',
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            db=app.config['MYSQL_DB'],
        ) 
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file:
            csv_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(csv_file_path)
        table_name = request.form.get('table')
        if not table_name:
            table_name = os.path.splitext(file.filename)[0]
        with connection.cursor() as cursor: # THIS RETRIEVES THE COLUMNS NAMES SINCE THE PROVIDED CSVs DOESN'T HAVE HEADERS
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = cursor.fetchall()
            headers = ', '.join([column[0] for column in columns])
            insert_data_into_table(connection, table_name, headers, csv_file_path)
        connection.commit() 
        return jsonify({'message': 'Data uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        connection.close()        
