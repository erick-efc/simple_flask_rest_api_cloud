# CSV TO TABLE FUNCTION
def insert_data_into_table(connection, table_name, keys, csv_file_path):
    data = []
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            data.append(row)
    data = to_null (data)
    with connection.cursor() as cursor:
        for row in data:
            id_to_insert = row[0]
            check_query = f"SELECT COUNT(*) FROM {table_name} WHERE id = %s"
            cursor.execute(check_query, (id_to_insert,))
            exists = cursor.fetchone()[0]
            if not exists:
                values_placeholder = ', '.join(['%s'] * len(row))
                query = f"INSERT INTO {table_name} ({keys}) VALUES ({values_placeholder})"
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
        return jsonify({'message': 'Data uploaded successfully'})
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)})
    finally:
        connection.close()
