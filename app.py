from flask import Flask, request, jsonify
import os
import csv
import pymysql

app = Flask(__name__)

# DECLARING CONSTANTS
UPLOAD_FOLDER = './uploads'  
HISTORICAL_DATA_FOLDER = './historical_data'

# MYSQL CONFIGURATION
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'api_user'
app.config['MYSQL_PASSWORD'] = 'globant123' # NEVER HARDCODE SENSITIVE INFORMATION, THIS IS JUST FOR DEMONSTRATION PURPOSE
app.config['MYSQL_DB'] = 'globant_test'
app.config['MYSQL_CURSORCLASS'] = 'pymysql.cursors.DictCursor'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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


################################################
# ROUTE TO RETRIEVE TABLES WITH HISTORICAL DATA
################################################
@app.route('/api/historical_data_up')
def historical_data_up():
    try:
        connection = connect_now()
        uptade_order = ["departments", "jobs", "hired_employees"] # HIRED_EMPLOYEES IS A CHILD TABLE IN THE SCHEMA
        for table in uptade_order:
            table_name = table
            csv_file_path = os.path.join(HISTORICAL_DATA_FOLDER, f'{table_name}.csv')
            insert_data_into_table(connection, table_name, csv_file_path)  
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
        connection = connect_now()
        if 'file' not in request.files: # ENSURING A FILE WAS PASSED IN THE REQUEST
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file:
            csv_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(csv_file_path)
        table_name = request.form.get('table')
        if not table_name:
            table_name = os.path.splitext(file.filename)[0] # RETRIEVING TABLE NAME BASED ON FILE
        insert_data_into_table(connection, table_name, csv_file_path)
        connection.commit()
        os.remove(csv_file_path)
        return jsonify({'message': 'Data uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        connection.close()        
