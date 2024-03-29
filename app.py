from flask import Flask, request, jsonify
from  utils.functions import connect_now, insert_data_into_table
from routes.extra_routes import extra_routes_bp
from routes.required_routes import required_routes_bp

app = Flask(__name__)

# APP CONFIG
app.config['MYSQL_HOST'] = 'your_aws_endpoint'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'api_user'
app.config['MYSQL_PASSWORD'] = 'your_password' # NEVER HARDCODE SENSITIVE INFORMATION, THIS IS JUST FOR DEMONSTRATION PURPOSE
app.config['MYSQL_DB'] = 'api_db'
app.config['MYSQL_CURSORCLASS'] = 'pymysql.cursors.DictCursor'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  
app.config['UPLOAD_FOLDER'] = '/var/www/html/flask-app/uploads'
app.config['UPLOAD_HIST'] = '/var/www/html/flask-app/historical_upload' 

# BLUEPRINT REGISTER
app.register_blueprint(extra_routes_bp)
app.register_blueprint(required_routes_bp)
