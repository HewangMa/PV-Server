from pathlib import Path
from logger import get_logger
from PIL import Image
import send2trash
import re
import os
import random
import hashlib
import socket
import sys

logger = get_logger("utils", level="DEBUG")

# 视频扩展名
VIDEOS = (
    ".mp4",
    ".avi",
    ".mkv",
    ".mov",
    ".flv",
    ".wmv",
    ".webm",
    ".mpeg",
    ".mpg",
    ".3gp",
    ".m4v",
    ".ts",
    ".m3u8",
    ".vob",
    ".ogv",
    ".rmvb",
    ".m2ts",
    ".mts",
    ".mpg",
    ".mpeg",
    ".mpeg2",
    ".mpeg4",
    ".mpe",
    ".mpv",
    ".m2v",
    ".m4p",
    ".m4b",
    ".m4r",
)

IMAGES = (
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".webp",
    ".tiff",
    ".svg",
    ".ico",
    ".heic",
)


def port_occupied(port=8017):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"  # 失败时返回本地回环


def is_vertical(img_path: Path):
    try:
        with Image.open(img_path) as img:
            return img.height > img.width
    except:
        return False


def is_horizontal(img_path: Path):
    try:
        with Image.open(img_path) as img:
            return img.height < img.width
    except:
        return False


def natural_sort(name: str):
    """将字符串分成数字和非数字部分，自然排序"""
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r"(\d+)", name)
    ]


def hash_pwd(key: str) -> str:
    hash_object = hashlib.sha256()
    hash_object.update(key.encode("utf-8"))
    return hash_object.hexdigest()


def remove_existing_thumb(dir: Path):
    for root, dirs, files in os.walk(dir):
        for file in files:
            path = Path(root) / file
            if path.name.lower().endswith(VIDEOS):
                thumb = Path(root) / (path.stem + "_thumb.jpg")
                if thumb.exists():
                    logger.info(f"Removing existing thumbnail: {thumb}")
                    send2trash.send2trash(thumb)
                thumb = Path(root) / (path.stem + ".jpg")
                if thumb.exists():
                    logger.info(f"Removing existing thumbnail: {thumb}")
                    send2trash.send2trash(thumb)
