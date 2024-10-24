from flask import Flask, send_from_directory, request, jsonify, abort, render_template
import os

app = Flask(__name__)
MEDIA_DIR = os.path.expanduser("/mnt/mechanical/resource")


@app.route("/")
def index():
    return """
<head>

<style>
      * {
        font-size: 50px;
      }
    </style>
</head>
    <h1>Media Server</h1>
    <ul>
        <li><a href="/browse/">Browse Files</a></li>
    </ul>
    """


@app.route("/browse/", defaults={"req_path": ""})
@app.route("/browse/<path:req_path>")
def browse(req_path):
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


@app.route("/delete/<path:file_path>", methods=["POST"])
def delete(file_path):
    abs_path = os.path.join(MEDIA_DIR, file_path)
    if not os.path.exists(abs_path):
        return jsonify(success=False, message="File not found"), 404
    try:
        os.remove(abs_path)
        return jsonify(success=True, message="File deleted")
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8017, debug=True)
