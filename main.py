from io import BytesIO
from flask import Flask, send_file, request, send_from_directory
from ves import render_ves
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


def serve_pil_image(img):
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>')
def base(path):
    if (len(path) == 0):
        return send_from_directory('./', 'avis.html')
    return send_from_directory('./', path)


@app.route('/render', methods=['GET', 'POST'])
def rendVes():
  ves = request.form.get('ves')
  width = request.form.get('width')
  print(ves)
  img = render_ves()
  return serve_pil_image(img)
