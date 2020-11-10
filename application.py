import zipfile
import requests
import asyncio
import os
import tempfile
import json
import uuid
import glob
import copy

from flask import Flask, render_template_string, request, jsonify, Response
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import geopandas as gpd

# template_folder points to current directory. Flask will look for '/static/'
application = Flask(__name__, template_folder='./static/')
# The rest of your file here

CORS(application)
application.config['CORS_HEADERS'] = 'Content-Type'

API_KEY = 'super-secret-api-key'
UPLOAD_FOLDER = './data'
ALLOWED_EXTENSIONS = {'zip'}

application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


SOURCES = """
    map.addSource('dummy', {
        'type': 'geojson',
        'data': data_placeholder});"""

LINE_LAYER = """
    map.addLayer({
        'id': 'dummy',
        'type': 'line',
        'source': 'dummy',
        'layout': {
            'line-join': 'round',
            'line-cap': 'round'
        },
        'paint': {
            'line-color': '#086623',
            'line-width': 2
        }
    });"""

POINT_LAYER = """
    map.addLayer({
        'id': 'dummy',
        'type': 'circle',
        'source': 'dummy',
        'paint': {
            'circle-color': '#C7EA46',
            'circle-radius': 2
        }
    });"""

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
    transaction_dir = ""
    try:
        if not request.form.get('api_key', '') == API_KEY:
            return "Not Authorized"
        transaction = uuid.uuid4()
        file = request.files['file']  
        filename = secure_filename(file.filename)
        file_like_object = file.stream._file  
        zipfile_ob = zipfile.ZipFile(file_like_object)
        file_names = zipfile_ob.namelist()
        convert_shps = []
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
                    if extension == '.shp':
                        convert_shps.append(tmp_file)

            for i, c in enumerate(convert_shps):
                gdf = gpd.read_file(c)
                gdf = gdf.to_crs("EPSG:4326")
                transaction_dir = os.path.join(os.getcwd(), "data", str(transaction))
                if not os.path.isdir(transaction_dir):
                    os.makedirs(transaction_dir)

                gdf.to_file(os.path.join(transaction_dir, f"{i}.geojson"), driver="GeoJSON")

        json_files = glob.glob(os.path.join(transaction_dir, "*.geojson"))


        sources = ""
        layers = ""

        for i, j in enumerate(json_files):
            s = copy.copy(SOURCES)
            with open(j, "r") as layer_f:
                layer = json.load(layer_f)
                s = s.replace("dummy", str(i))
                s = s.replace("data_placeholder", str(layer))
                sources += s
                sources += "\n"

                l = copy.copy(POINT_LAYER)
                l = l.replace("dummy", str(i))
                layers += l
                layers += "\n"

        template = "\n".join(open("./template/template.html").readlines())
        template = template.replace("{{ sources }}", str(sources))
        template = template.replace("{{ layers }}", str(layers))
        template = template.replace("{{ center }}", str([-95.7129, 37.0902]))
        template = template.replace('None', "''")

        return Response(template)
        
    except requests.exceptions.RequestException as e:
        print(e) # TODO: change this to logging
        return jsonify({"status": "failed"})

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
