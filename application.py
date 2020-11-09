import zipfile
import requests
import asyncio
import os
import tempfile
import json

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import geopandas as gpd

# template_folder points to current directory. Flask will look for '/static/'
application = Flask(__name__, template_folder='./static/')
# The rest of your file here

CORS(application)
application.config['CORS_HEADERS'] = 'Content-Type'

API_KEY = '68313a59-f117-4b4e-926c-e4b9499559d9'
UPLOAD_FOLDER = './data'
ALLOWED_EXTENSIONS = {'zip'}

application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@application.route('/')
@cross_origin()
def index():
    """ Serving static files """
    try:
        return render_template('index.html')
    except requests.exceptions.RequestException as e:
        print(e) # TODO: change this to logging
        return jsonify({"status": "failed"})


@application.route('/v1/shp2map', methods=["POST"])
@cross_origin()
def fullocr():
    try:
        if not request.form.get('api_key', '') == API_KEY:
            return "Not Authorized"
        file = request.files['file']  
        filename = secure_filename(file.filename)
        file_like_object = file.stream._file  
        zipfile_ob = zipfile.ZipFile(file_like_object)
        file_names = zipfile_ob.namelist()
        # Filter names to only include the filetype that you want:
        convert_shps = [file_name for file_name in file_names if file_name.endswith(".shp")]

        files = [(zipfile_ob.open(name).read(),name) for name in file_names]
        with tempfile.TemporaryDirectory() as tmpdirname:
            for data, f in files:
                print(f)
                _, extension = os.path.splitext(f)
                tmp_file = os.path.join(tmpdirname, f)
                full_dir = os.path.dirname(tmp_file)
                if not os.path.isdir(full_dir):
                    os.makedirs(full_dir)
                if extension in ['.shp', '.shx', '.prj', '.dbf']:
                    with open(tmp_file, 'wb') as uz_file:
                        uz_file.write(data)

            return convert_shps
        
    except requests.exceptions.RequestException as e:
        print(e) # TODO: change this to logging
        return jsonify({"status": "failed"})

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
