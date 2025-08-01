from flask import Flask, render_template, request, redirect, url_for, session
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.urandom(24)
PROJECT_DIR = Path(os.path.dirname(__file__)).parent
RESOURCE_DIR = PROJECT_DIR / "resource"

# 密码
PASSWORD = "zisemianju"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        password = request.form["password"]
        if password == PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("browse"))
        else:
            return render_template("index.html", error="密码错误，请重新输入。")
    return render_template("index.html")


@app.route("/browse")
def browse():
    if "authenticated" in session:
        req_path = request.args.get("path", "")  # 获取当前路径
        target_path = Path(RESOURCE_DIR) / req_path

        # 确保目标路径存在
        if not target_path.exists() or not target_path.is_dir():
            return "目录不存在", 404

        # 获取目录下的文件列表
        items = []
        for item in target_path.iterdir():
            if item.is_dir():
                items.append(
                    {
                        "name": item.name,
                        "path": str(item.relative_to(RESOURCE_DIR)),
                        "is_dir": True,
                    }
                )
            else:
                items.append(
                    {
                        "name": item.name,
                        "path": str(item.relative_to(RESOURCE_DIR)),
                        "is_dir": False,
                    }
                )

        return render_template("browse.html", req_path=req_path, items=items)
    else:
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.pop("authenticated", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
