from io import BytesIO
from flask import Flask, send_file, request, send_from_directory
from Ves import ves as vesClass
app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>')
def base(path):
    if (len(path) == 0):
        return send_from_directory('./', 'avis.html')
    return send_from_directory('./', path)


@app.route('/render', methods=['GET', 'POST'])
def rendVes():
    vesObj = vesClass(vesStr=request.form["ves"])
    scale = 1   #   *Should* make images fit the image 'window' better
    if(vesObj.defHeight >= vesObj.defWidth):
        scale = int(request.form["height"])/vesObj.defHeight
    else:
        scale = int(request.form["width"])/vesObj.defWidth
    imgInMem = vesObj.getImage(scale = scale)
    return send_file(imgInMem, mimetype="image/png")