from flask import Flask, request, jsonify
from  utils.functions import connect_now, insert_data_into_table
from routes.extra_routes import extra_routes_bp
from routes.globant_required_routes import globant_required_routes_bp

app = Flask(__name__)

# APP CONFIG
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'api_user'
app.config['MYSQL_PASSWORD'] = 'globant123' # NEVER HARDCODE SENSITIVE INFORMATION, THIS IS JUST FOR DEMONSTRATION PURPOSE
app.config['MYSQL_DB'] = 'globant_test'
app.config['MYSQL_CURSORCLASS'] = 'pymysql.cursors.DictCursor'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  
app.config['UPLOAD_FOLDER'] = './uploads' 

# BLUEPRINT REGISTER
app.register_blueprint(extra_routes_bp)
app.register_blueprint(globant_required_routes_bp)
