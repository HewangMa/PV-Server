import hashlib
import os
import re

from flask import Flask, send_from_directory, request, jsonify, abort, render_template


class Utils:
    @staticmethod
    def hash_key(key: str) -> str:
        hash_object = hashlib.sha256()
        hash_object.update(key.encode('utf-8'))
        return hash_object.hexdigest()


app = Flask(__name__)
MEDIA_DIR = os.path.expanduser(
    "/mnt/mechanical/projects/media-server/resource")
PWD_HASH = '34f681da8fa0841964a9ab7798430be9bc50be2d8e64beeaa00805e3d6c1682f'
HINT = 'the purple one'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        if Utils.hash_key(user_input) == PWD_HASH:
            return browse()
    return render_template('index.html')


@app.route("/browse/<path:req_path>")
def browse(req_path=''):
    def custom_sort(file_name):
        match = re.findall(r'(\D+)|(\d+)', file_name)
        parts = [(m[0], int(m[1])) if m[1] else (m[0], None) for m in match]
        return parts
    abs_path = os.path.join(MEDIA_DIR, req_path)
    if not os.path.exists(abs_path):
        return abort(404)
    if os.path.isfile(abs_path):
        return send_from_directory(
            os.path.dirname(abs_path), os.path.basename(abs_path)
        )
    sorted_files = sorted(os.listdir(abs_path), key=custom_sort)
    items = []
    for filename in sorted_files:
        file_path = os.path.join(req_path, filename)
        items.append(
            {
                "name": filename,
                "path": file_path,
                "is_dir": os.path.isdir(os.path.join(abs_path, filename)),
            }
        )
    return render_template("browse.html", req_path=req_path, items=items)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8017, debug=True)
