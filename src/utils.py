import os
import re
import shutil
import socket
import hashlib
import send2trash
import subprocess
from PIL import Image
from logger import get_logger
from pathlib import Path
from PIL.ExifTags import TAGS
from datetime import datetime

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

ZIPS = (".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz")


def port_occupied(port=8017):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def get_thumb(path: Path):
    name = path.name if path.is_dir() else path.stem
    while name.startswith(("a_", "b_", "c_")):
        name = name[2:]
    return path.parent / f"{name}_thumb.jpg"


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
            return img.height >= img.width
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


def remove_existing_vids_thumb(dir: Path):
    for root, dirs, files in os.walk(dir):
        for file in files:
            path = Path(root) / file
            if path.name.lower().endswith(VIDEOS):
                thumb = get_thumb(path)
                if thumb.exists():
                    logger.info(f"Removing existing thumbnail: {thumb}")
                    send2trash.send2trash(thumb)


def remove_existing_pics_thumb(dir: Path):
    for root, dirs, files in os.walk(dir):
        for file in files:
            path = Path(root) / file
            if path.name.lower().endswith(IMAGES):
                dir = Path(root)
                thumb = get_thumb(dir)
                if thumb.exists():
                    logger.info(f"Removing existing thumbnail: {thumb}")
                    send2trash.send2trash(thumb)
                break  # 每个目录只处理一次


def get_file_time(file: Path):
    def re_parse_date(file: Path):
        if file.name.endswith(VIDEOS):
            pattern = re.compile(r"VID_(\d{8})_\w+\.mp4$", re.IGNORECASE)
            match = pattern.match(file.name)
            if match:
                return match.group(1)
        elif file.name.endswith(IMAGES):
            pattern = re.compile(r".?(20\d{6})\d?", re.IGNORECASE)
            match = pattern.search(file.name)
            if match:
                return match.group(1)
        return None

    def exif_parse_date(file: Path):
        if not file.name.endswith(IMAGES):
            return None
        try:
            img = Image.open(file)
            exif = img._getexif()
            if not exif:
                return None
            for tag, value in exif.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == "DateTimeOriginal":
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S").strftime(
                        "%Y%m%d"
                    )
        except Exception as e:
            return None
        return None

    def ffprobe_parse_date(file: Path):
        if not file.name.endswith(VIDEOS):
            return None
        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "format_tags=creation_time",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(file),
            ]
            output = (
                subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
            )
            if output:
                try:
                    dt = datetime.fromisoformat(output.replace("Z", "+00:00"))
                    return dt.strftime("%Y%m%d")
                except Exception:
                    logger.info(f"err {e} for {file}")
                    return output[:10].replace("-", "")
        except Exception as e:
            logger.info(f"err {e} for {file}")
            return None
        return None

    return re_parse_date(file) or exif_parse_date(file) or ffprobe_parse_date(file)


def move_to_subdir(src_dir: Path):
    dst_dir = src_dir
    for file in src_dir.iterdir():
        if file.is_file():
            date_str = get_file_time(file)
            if date_str:
                target_dir = dst_dir / date_str
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file), target_dir / file.name)
                logger.info(f"Moved {file.name} -> {target_dir}/")


if __name__ == "__main__":
    move_to_subdir(Path("/home/hewangma/projects/PV-Server/resource/fj/vids"))
