import os
import sys
import random
from pathlib import Path
from logger import get_logger
from utils import (
    IMAGES,
    VIDEOS,
    lan_ip,
    hash_pwd,
    get_thumb,
    natural_sort,
    port_occupied,
    is_mounted,
)
from flask import (
    Flask,
    request,
    session,
    url_for,
    redirect,
    render_template,
    send_from_directory,
)

logger = get_logger("app", level="DEBUG")
app = Flask(__name__)
app.secret_key = os.urandom(24)
PROJECT_DIR = Path(os.path.dirname(__file__)).parent

RESOURCE_BASES = [
    PROJECT_DIR / "resource",
    Path("/mnt/hewangma1/resource"),  # 待更改到/media目录下
    Path("/mnt/hewangma2/resource"),
]


MENU_ITEMS = [
    {
        "type": "dir",
        "name": path.stem,
        "path": path,
        "preview": None,
    }
    for path in RESOURCE_BASES
    if is_mounted(str(path))
]


BG_DIR = PROJECT_DIR / "resource" / "background"
BG_LIST = [
    str(f) for f in BG_DIR.iterdir() if f.is_file() and f.name.lower().endswith(IMAGES)
]

# 密码
PWD_HASH = "34f681da8fa0841964a9ab7798430be9bc50be2d8e64beeaa00805e3d6c1682f"
HINT = "the purple"


@app.route("/resource/<path:filepath>")
def resource(filepath):
    return send_from_directory("/", filepath)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        password = request.form["password"]
        if hash_pwd(password.lower()) == PWD_HASH:
            session["authenticated"] = True
            return redirect(url_for("browse"))
        else:
            return render_template(
                "index.html",
                error="密码错误，请重新输入。",
                bg_list=None,
                bg_img=None,
            )
    return render_template("index.html", bg_list=None, bg_img=None)


def path_is_save(path: Path):
    if not path.exists():
        return False
    for base in RESOURCE_BASES:
        if path.is_relative_to(base):
            return True
    return False


def gather_images(path: Path):
    images = {}
    for _path in path.iterdir():
        if _path.is_file() and _path.name.lower().endswith(IMAGES):
            images[_path.stem] = _path
    return images


def gather_items(path: Path, images: dict = None):
    items = []
    for _path in path.iterdir():
        name = _path.name
        thumb = get_thumb(_path)
        preview = images.get(thumb.stem)
        if _path.is_dir():
            items.append(
                {
                    "type": "dir",
                    "name": name,
                    "path": _path,
                    "preview": preview,
                }
            )
        elif name.lower().endswith(VIDEOS):
            items.append(
                {
                    "type": "video",
                    "name": name,
                    "path": _path,
                    "preview": preview,
                }
            )
    return items


@app.route("/browse")
def browse():
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    req_path = request.args.get("path", "")
    target_path = Path(req_path).resolve()
    bg_img = random.choice(BG_LIST)
    if not req_path:
        # 进入目录页
        return render_template(
            "browse.html",
            req_path=None,
            items=MENU_ITEMS,
            bg_list=BG_LIST,
            bg_img=bg_img,
        )
    elif path_is_save(target_path):
        # 进入该路径下的内容
        images = gather_images(target_path)
        items = gather_items(target_path, images)
        if not items:
            # 该目录下没有视频和子目录，则展示图片页
            return redirect(url_for("images", path=target_path))
        items.sort(
            key=lambda x: (
                0 if x["type"] == "video" else 1,
                natural_sort(x["name"]),
            )
        )
        return render_template(
            "browse.html",
            req_path=target_path,
            items=items,
            bg_list=BG_LIST,
            bg_img=bg_img,
        )
    else:
        return "目录不存在", 404


@app.route("/images")
def images():
    if not session.get("authenticated"):
        return redirect(url_for("index"))

    req_path = request.args.get("path", "")
    target_path = Path(req_path).resolve()
    if not path_is_save(target_path):
        return "目录不存在", 404

    groups = {
        "a_": [],
        "b_": [],
        "c_": [],
        "other": [],
    }

    for image_file in target_path.iterdir():
        if image_file.is_file() and image_file.name.lower().endswith(IMAGES):
            img = {
                "type": "image",
                "name": image_file.name,
                "path": image_file,
            }
            prefix = img["name"][:2]
            if prefix in groups:
                groups[prefix].append(img)
            else:
                groups["other"].append(img)
    for _, items in groups.items():
        items.sort(key=lambda x: natural_sort(x["name"]))
    group_classes = {
        "a_": "group-a",
        "b_": "group-b",
        "c_": "group-c",
        "other": "group-other",
    }

    bg_img = random.choice(BG_LIST)
    return render_template(
        "images.html",
        req_path=req_path,
        groups=groups,
        group_classes=group_classes,
        bg_list=BG_LIST,
        bg_img=bg_img,
    )


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
