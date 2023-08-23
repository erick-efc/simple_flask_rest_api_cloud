import os
import json
import csv
from datetime import datetime
from flask import jsonify, Blueprint, request, current_app as app
from utils.functions import connect_now, insert_data_into_table, sort

globant_required_routes_bp = Blueprint('globant_required_routes_bp', __name__)

################################################
# UPLOAD PERSISTENT FILES ROUTE
################################################
@globant_required_routes_bp.route('/api/upload_hist', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file:
            filename = os.path.join(app.config['UPLOAD_HIST'], file.filename)
            file.save(filename)
        return jsonify({'message': 'File uploaded successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

################################################
# UPDATE HISTORICAL DATA FROM UPDATE_HIST FOLDER
################################################
@globant_required_routes_bp.route('/api/historical_to_db')
def historical_data_up():
    try:
        connection = connect_now()
        update_order = ["departments", "jobs", "hired_employees"] # HIRED_EMPLOYEES IS A CHILD TABLE IN THE SCHEMA
        file_list = [os.path.splitext(file)[0] for file in os.listdir(app.config['UPLOAD_HIST'])]
        for file in file_list:
            if file not in update_order:
                os.remove(os.path.join(app.config['UPLOAD_HIST'], file))
        file_list = sort(update_order, file_list)
        if not file_list:
            return jsonify({'error': 'nothing to update'}), 400
        for table in file_list:
            table_name = table
            csv_file_path = os.path.join(app.config['UPLOAD_HIST'], f'{table_name}.csv')
            insert_data_into_table(connection, table_name, csv_file_path)  
        connection.commit() 
        return jsonify({'message': 'Data updated successfully'}), 201
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        connection.close()

################################################
# UPDATE DATA FROM BATCH
################################################
@globant_required_routes_bp.route('/api/batch_insert', methods=['POST'])
def batch_insert():
    data = request.form.to_dict()
    table_name = data.get('table_name')
    rows_json = data.get('rows')
    if not table_name or not rows_json:
        return jsonify({"message": "Invalid request data"}), 400
    try:
        connection = connect_now()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        csv_file_name = f"batch_{timestamp}.csv"
        csv_file_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_file_name)
        data = json.loads(rows_json)
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        insert_data_into_table(connection, table_name, csv_file_path) 
        connection.commit() 
    except json.JSONDecodeError:
        return jsonify({"message": "Invalid JSON data in rows"}), 400
    except Exception as e:
        connection.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
    finally:
        connection.close()
    return jsonify({"message": "Batch insert successful, csv generated"}), 201
    
################################################
# QUERY 1
################################################
@globant_required_routes_bp.route('/employee-count-by-quarter', methods=['GET'])
def employee_count_by_quarter():
    query = """
    SELECT
        department_id,
        job_id,
        datetime,
        COUNT(*) AS employee_count
    FROM
        hired_employees
    WHERE
        YEAR(datetime) = 2021
    GROUP BY
        department_id, job_id, datetime
    ORDER BY
        department_id, job_id
    """
    try:
        connection = connect_now()
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        response = []
        for row in result:
            response.append(dict(zip(columns, row)))

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
