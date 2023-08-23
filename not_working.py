
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
                    row_values = [int(value) if value.isdigit() else value for value in row]
                    cursor.execute(query, row_values)
        return jsonify({'message': 'Data inserted successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# EMPTY TO NULL TREATMENT
def to_null (data):
    for row_idx, row in enumerate(data):
        for value_idx, value in enumerate(row):
            if value == '':
                data[row_idx][value_idx] = None
    return data

# TO SORT BASED ON HIERARCHY OF OUR GB
def sort(update_order, target_list):
    position_map = {element: position for position, element in enumerate(update_order)}
    sorted_target_list = sorted(target_list, key=lambda x: position_map.get(x, float('inf')))
    return sorted_target_list

@extra_routes_bp.route('/api/historical_data_bkup_feed')
def historical_data_up():
    try:
        connection = connect_now()
        update_order = ["departments", "jobs", "hired_employees"] # HIRED_EMPLOYEES IS A CHILD TABLE IN THE SCHEMA
        for table in update_order:
            table_name = table
            csv_file_path = os.path.join(HISTORICAL_DATA_FOLDER, f'{table_name}.csv')
            insert_data_into_table(connection, table_name, csv_file_path)  
        connection.commit() 
        return jsonify({'message': 'Data retrieved successfully'}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        connection.close()

        def connect_now():
    connection = pymysql.connect(
        host='localhost',
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
    )
    return connection