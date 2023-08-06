from threading import Thread
import ast
import hashlib, uuid
import os
import sys
import time
import codefast as cf
import requests
from flask import Flask, flash, redirect, request
from hashids import Hashids
from waitress import serve
from werkzeug.utils import secure_filename
from authc import authc

from dofast.config import CHANNEL_MESSALERT
from dofast.flask.config import AUTH_KEY
from dofast.flask.model import lock_device, unlock_device, open_url_on_linux
from dofast.flask.utils import authenticate_flask
from dofast.network import Twitter
from dofast.pipe import author
from dofast.toolkits.telegram import Channel
from authc import get_redis

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'log', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1000 * 1000  # Maximum size 1GB
authenticate_flask(app)


@app.errorhandler(Exception)
def handle_invalid_usage(error):
    cf.error(error)
    raise error


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/open_url_on_linux', methods=['GET', 'POST'])
def _open_url_on_linux():
    data = request.args.get('url').replace(' ', '+')
    open_url_on_linux.delay(data)
    return {'status': 'OK', 'data': cf.b64decode(data)}


@app.route('/device_control', methods=['GET', 'POST'])
def device_control():
    accs = authc()
    if request.headers.get('User-Agent') != accs['whitelist_agent']:
        return 'UNRECOGNIZED device'
    action = request.args.get('action', 'lock')
    task = unlock_device.delay() if action == 'unlock' else lock_device.delay()
    TIMEOUT = 10
    while TIMEOUT > 0:
        if task.status == 'SUCCESS':
            return redirect('https://www.google.com')
        time.sleep(1)
        TIMEOUT -= 1
    return redirect('https://www.baidu.com')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            folder = request.form.get('upload_folder')
            if folder:
                app.config['UPLOAD_FOLDER'] = folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('download_file', name=filename))
            return "SUCCESS"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/tweet', methods=['GET', 'POST'])
def tweet():
    text = request.args.get('text', '')
    cf.info('input text: ' + text)
    files = request.files.getlist('images')
    cf.info('input files: ' + str(files))
    media = ['/tmp/{}'.format(f.filename) for f in files]
    for m, f in zip(media, files):
        f.save(m)
    keys = ast.literal_eval(author.get('slp'))
    twitter_api = Twitter(keys['consumer_key'], keys['consumer_secret'],
                          keys['access_token'], keys['access_token_secret'])
    twitter_api.post([text] + media)
    return {'text': text, 'images': [f.filename for f in files]}


@app.route('/download', methods=['GET', 'POST'])
def download():
    js = request.get_json()
    filename = js['filename']
    return cf.io.reads(filename)


@app.route('/messalert', methods=['GET', 'POST'])
def msg():
    js = request.get_json()
    Channel(CHANNEL_MESSALERT).post(js['text'])
    return 'SUCCESS'


@app.route('/hello')
def hello_world():
    return 'SUCCESS!'


@app.route('/s', methods=['GET', 'POST'])
def shorten() -> str:
    """Url shortener"""
    data = request.get_json(force=True)
    cf.info('input data: ' + str(data))
    if not data:
        return {}
    url = data.get('url', '')
    md5 = hashlib.md5(url.encode()).hexdigest()
    hid = Hashids(salt=md5, min_length=6)
    uniq_id = hid.encode(42)

    def persist(key, url):
        return get_redis().set(key, url, ex=60 * 60 * 24 * 365)

    Thread(target=persist, args=('shorten_' + uniq_id, url)).start()
    return {
        'code': 200,
        'status': 'SUCCESS',
        'url': request.host_url + 's/' + uniq_id
    }


@app.route('/<path:path>')
def all_other(path):
    path_str = str(path)
    cf.info('request path: ' + path_str)
    if not path_str.startswith('s/'):
        return ''
    r = get_redis()
    key = 'shorten_' + path_str.replace('s/', '')
    out_url = r.get(key).decode() if r.exists(
        key) else 'https://www.google.com'
    cf.info('out_url: ' + out_url)
    return redirect(out_url)


@app.route('/hanlp', methods=['POST', 'GET'])
def hanlp_route():
    texts = request.json.get('texts', [])
    cf.info('hanlp input texts:', texts)
    resp = requests.post('http://localhost:55555/hanlp', json={'texts': texts})
    return resp.json()


def run():
    port = int(sys.argv[1]) if len(sys.argv) >= 2 else 6363
    serve(app, host="0.0.0.0", port=port)


if __name__ == '__main__':
    app.run(host="0.0.0.0",
            port=443,
            ssl_context=('/etc/letsencrypt/live/140716.xyz/fullchain.pem',
                         '/etc/letsencrypt/live/140716.xyz/privkey.pem'),
            threaded=True)
