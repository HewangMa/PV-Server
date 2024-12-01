import hashlib

from flask import Flask, send_from_directory, request, jsonify, abort, render_template
import os


class Utils:
    @staticmethod
    def hash_key(key: str) -> str:
        hash_object = hashlib.sha256()
        hash_object.update(key.encode('utf-8'))
        return hash_object.hexdigest()


app = Flask(__name__)
MEDIA_DIR = os.path.expanduser("/mnt/mechanical/resource")
# MEDIA_DIR = os.path.expanduser("C:\Users\mhw\Pictures\Feedback\{3A2395B0-8345-465E-B4D5-9E89807E0C51}")
# MEDIA_DIR = "D:/"
PWD_HASH = '34f681da8fa0841964a9ab7798430be9bc50be2d8e64beeaa00805e3d6c1682f'
HINT = 'the purple one'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        if Utils.hash_key(user_input) == PWD_HASH:
            return browse()
    return render_template('index.html')


# @app.route("/browse/", defaults={"req_path": ""})
@app.route("/browse/<path:req_path>")
def browse(req_path=''):
    abs_path = os.path.join(MEDIA_DIR, req_path)
    if not os.path.exists(abs_path):
        return abort(404)
    if os.path.isfile(abs_path):
        return send_from_directory(
            os.path.dirname(abs_path), os.path.basename(abs_path)
        )
    sorted_files = sorted(os.listdir(abs_path))
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
