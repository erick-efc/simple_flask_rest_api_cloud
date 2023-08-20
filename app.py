from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'api_user'
app.config['MYSQL_PASSWORD'] = 'globant123'
app.config['MYSQL_DB'] = 'globant_test'
app.config['MYSQL_CURSORCLASS'] = 'pymysql.cursors.DictCursor'

# Test route to retrieve data from the database
@app.route('/test', methods=['GET'])
def test_database():
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
    )
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM departments')
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(data)
