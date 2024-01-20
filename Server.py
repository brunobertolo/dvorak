import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/credentials', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    zip_file = request.files['file']

    if zip_file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Specify the folder where you want to store the uploaded ZIP file
    upload_folder = 'Credentials'

    # Save the ZIP file
    zip_filename = secure_filename(zip_file.filename)
    zip_file.save(os.path.join(upload_folder, zip_filename))

    return jsonify({'message': 'ZIP file uploaded successfully'})

if __name__ == '__main__':
    app.run(debug=True)