import os
import time
import send2trash
import subprocess
from pathlib import Path
from logger import get_logger
from utils import VIDEOS

logger = get_logger("convert_vid", level="DEBUG")


def convert_dir(path: Path):
    target_vids = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith(VIDEOS) and "temp" not in Path(root).parts:
                target_vids.append(Path(root) / file)
    # ffmpeg自身是多线程的
    for file in target_vids:
        convert_vid(file)


def convert_vid(file: Path) -> Path:
    file = file.resolve()
    if not file.is_file() or not file.name.lower().endswith(VIDEOS):
        logger.error(f"文件不是视频格式: {file}")
        return
    ext = file.suffix.strip(".").lower()
    output_path = file.parent / (file.stem + f"_cf_{ext}.mp4")

    logger.info(f"正在转换 {file} 到 MP4 格式")
    result = subprocess.run(
        [
            "ffmpeg",
            "-fflags",
            "+genpts+discardcorrupt",
            "-err_detect",
            "ignore_err",
            "-y",
            "-i",
            str(file),
            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            str(output_path),
            "-map_metadata",
            "0",
            "-loglevel",
            "warning",
        ]
    )

    if result.returncode == 0:
        logger.info(f"转换成功: {file} -> {output_path},已经删除原文件")
        send2trash.send2trash(file)
    else:
        logger.error(f"转换失败: {file}")
    time.sleep(0.5)
