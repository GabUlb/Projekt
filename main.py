from io import BytesIO
from flask import Flask, send_file, request, send_from_directory
from Ves import ves as vesClass
from copy import deepcopy
app = Flask(__name__)
cache = {}

@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>')
def base(path):
    if (len(path) == 0):
        return send_from_directory('./', 'avis.html')
    return send_from_directory('./', path)


@app.route('/render', methods=['GET', 'POST'])
def rendVes():
    if(request.form["requestNum"] not in cache.keys()):
        print("Rendering new")
        vesObj = vesClass(vesStr=request.form["ves"])
        scale = 1   #   *Should* make images fit the image 'window' better
        if(vesObj.defHeight >= vesObj.defWidth):
            scale = int(request.form["height"])/vesObj.defHeight
        else:
            scale = int(request.form["width"])/vesObj.defWidth
        imgInMem = vesObj.getImage(scale = scale)
        cache[request.form["requestNum"]] = deepcopy(vesObj)
        return send_file(imgInMem, mimetype="image/png")
    else:
        print("Rendering already rendered")
        vesObj = vesClass(initial=["1.0", 0, 0])
        vesObj.prerendered(cache[request.form["requestNum"]])
        scale = 1   #   *Should* make images fit the image 'window' better
        if(vesObj.defHeight >= vesObj.defWidth):
            scale = int(request.form["height"])/vesObj.defHeight
        else:
            scale = int(request.form["width"])/vesObj.defWidth
        toAddOrig = request.form["toAdd"]
        toAdd = toAddOrig
        # for line in toAddOrig.split("\n"):
        #     splitLine = line.split()
        #     toAdd += splitLine[0] + " "
        #     for word in splitLine[1: -1]:
        #         toAdd += str(int(int(word)*(1/scale))) + " "
        #     toAdd += splitLine[-1] + "\n"
        vesObj.fromStr(toAdd)
        imgInMem = vesObj.getImage(scale = scale)
        return send_file(imgInMem, mimetype="image/png")
