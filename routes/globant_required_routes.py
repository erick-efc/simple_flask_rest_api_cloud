import os
from flask import jsonify, Blueprint, request, current_app as app

globant_required_routes_bp = Blueprint('globant_required_routes_bp', __name__)

################################################
# UPLOAD FILES ROUTE
################################################
@globant_required_routes_bp.route('/upload', methods=['POST'])
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