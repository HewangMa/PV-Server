from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_from_directory,
)
import os
from pathlib import Path
import random
import sys
from logger import get_logger
from utils import natural_sort, hash_pwd, port_occupied, lan_ip, IMAGES, VIDEOS

logger = get_logger("app", level="DEBUG")
app = Flask(__name__)
app.secret_key = os.urandom(24)
PROJECT_DIR = Path(os.path.dirname(__file__)).parent
RESOURCE_DIR = PROJECT_DIR / "resource"
BACKGROUND_DIR = RESOURCE_DIR / "background"


# 密码
PWD_HASH = "34f681da8fa0841964a9ab7798430be9bc50be2d8e64beeaa00805e3d6c1682f"
HINT = "the purple"


@app.route("/resource/<path:filename>")
def resource(filename):
    return send_from_directory(RESOURCE_DIR, filename)


@app.route("/", methods=["GET", "POST"])
def index():
    bg_images = [
        f
        for f in BACKGROUND_DIR.iterdir()
        if f.is_file() and f.name.lower().endswith(IMAGES)
    ]
    bg_list = [str(f.relative_to(RESOURCE_DIR)) for f in bg_images]

    if request.method == "POST":
        password = request.form["password"]
        if hash_pwd(password.lower()) == PWD_HASH:
            session["authenticated"] = True
            return redirect(url_for("browse"))
        else:
            # 随机选一张图片作为初始背景
            bg_img = random.choice(bg_list) if bg_list else None
            return render_template(
                "index.html",
                error="密码错误，请重新输入。",
                bg_list=bg_list,
                bg_img=bg_img,
            )
    # GET 请求
    bg_img = random.choice(bg_list) if bg_list else None
    return render_template("index.html", bg_list=bg_list, bg_img=bg_img)


@app.route("/browse")
def browse():
    if session.get("authenticated"):
        req_path = request.args.get("path", "")
        target_path = Path(RESOURCE_DIR) / req_path
        if not target_path.exists() or not target_path.is_dir():
            return "目录不存在", 404

        # 收集所有图片
        images = {}
        for _path in target_path.iterdir():
            if _path.is_file() and _path.name.lower().endswith(IMAGES):
                images[_path.stem] = str(_path.relative_to(RESOURCE_DIR))

        items = []
        for _path in target_path.iterdir():
            name = _path.name
            rel_path = str(_path.relative_to(RESOURCE_DIR))
            if _path.is_dir():
                preview = images.get(_path.name) or images.get(_path.name + "_thumb")
                items.append(
                    {
                        "type": "dir",
                        "name": name,
                        "path": rel_path,
                        "preview": preview,
                    }
                )
            elif name.lower().endswith(VIDEOS):
                preview = images.get(_path.stem) or images.get(_path.stem + "_thumb")
                items.append(
                    {
                        "type": "video",
                        "name": name,
                        "path": rel_path,
                        "preview": preview,
                    }
                )

        if not items:
            return redirect(url_for("images", path=req_path))

        items.sort(
            key=lambda x: (
                0 if x["type"] == "video" else 1,
                natural_sort(x["name"]),
            )
        )

        # 背景图片逻辑
        bg_dir = BACKGROUND_DIR
        bg_images = [
            f
            for f in bg_dir.iterdir()
            if f.is_file() and f.name.lower().endswith(IMAGES)
        ]
        bg_list = [str(f.relative_to(RESOURCE_DIR)) for f in bg_images]
        bg_img = random.choice(bg_list) if bg_list else None
        return render_template(
            "browse.html",
            req_path=req_path,
            items=items,
            bg_list=bg_list,
            bg_img=bg_img,
        )
    else:
        return redirect(url_for("index"))


@app.route("/images")
def images():
    if session.get("authenticated"):
        req_path = request.args.get("path", "")
        target_path = Path(RESOURCE_DIR) / req_path
        if not target_path.exists() or not target_path.is_dir():
            return "目录不存在", 404

        image_items = []
        for item in target_path.iterdir():
            if item.is_file() and item.name.lower().endswith(IMAGES):
                image_items.append(
                    {
                        "type": "image",
                        "name": item.name,
                        "path": str(item.relative_to(RESOURCE_DIR)),
                    }
                )

        image_items.sort(key=lambda x: natural_sort(x["name"]))
        return render_template("images.html", req_path=req_path, items=image_items)
    else:
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.pop("authenticated", None)
    return redirect(url_for("index"))


def start_server():
    if not port_occupied():
        logger.info(f"Starting PV-Server on ip of {lan_ip()} and port of 8017")
        app.run(host="0.0.0.0", port=8017)
    else:
        logger.error("PV-Server is already running on port 8017.")
        sys.exit(1)
