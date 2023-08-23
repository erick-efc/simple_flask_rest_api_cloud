from flask import jsonify, Blueprint,request, current_app as app
import os
from utils.functions import insert_data_into_table, connect_now

extra_routes_bp = Blueprint('extra_routes_bp', __name__)

HISTORICAL_DATA_FOLDER = './historical_data_bkup'

################################################
# ROUTE TO RETRIEVE TABLES WITH HISTORICAL DATA
################################################
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

################################################
# UPLOAD PERSISTENT FILES ROUTE
################################################
@extra_routes_bp.route('/api/upload', methods=['POST'])
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
        return jsonify({'message': 'File uploaded successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

################################################
# UPDATE DB WITH A NON PERSISTENT CSV
################################################
@extra_routes_bp.route('/update_db_csv', methods=['POST'])
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
        return jsonify({'message': 'Data uploaded successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        connection.close()        
