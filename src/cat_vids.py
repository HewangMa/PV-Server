import os
import subprocess
from logger import get_logger
from utils import VIDEOS, natural_sort
from thumb import convert_vid

logger = get_logger("cat_vids", level="DEBUG")

from pathlib import Path


def cat_dir_by_ffmpeg(dir: Path):
    videos = [
        f
        for f in dir.iterdir()
        if f.is_file() and f.suffix.lower() in VIDEOS and not f.stem.endswith("cated")
    ]
    if not videos:
        logger.warning(f"没有找到任何视频文件: {dir}")
        return

    videos.sort(key=lambda x: natural_sort(x.name))
    output_path = dir.parent / f"{dir.name}_cated.mp4"
    if output_path.exists():
        logger.warning(f"输出文件已存在，请检查: {output_path}")
        return
    list_file_path = dir / "file_list.txt"
    with open(list_file_path, "w") as list_file:
        for video in videos:
            list_file.write(f"file '{str(video)}'\n")

    command = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file_path),
        "-c",
        "copy",  # 流拷贝，不重编码
        "-y",
        str(output_path),
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logger.info(f"视频拼接失败: {e}")
    finally:
        logger.info(f"完成(请检查是否成功): {output_path}")


def cat_dirs(dir_path: Path):
    leaf_dirs = []
    for root, dirs, files in os.walk(dir_path):
        if not dirs:
            leaf_dirs.append(Path(root))
    for leaf_dir in leaf_dirs:
        # 转换之后再连接
        convert_vid(leaf_dir)
        cat_dir_by_ffmpeg(leaf_dir)
