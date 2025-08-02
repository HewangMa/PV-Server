import cv2
import os
import shutil
import send2trash
from pathlib import Path
from logger import get_logger
from PIL import Image
import random
import time
import numpy as np
import subprocess
from utils import (
    is_vertical,
    natural_sort,
    is_horizontal,
    IMAGES,
    VIDEOS,
    remove_existing_thumb,
)
from concurrent.futures import ProcessPoolExecutor

logger = get_logger("pics_thumb", level="DEBUG")


############## PICS THUMB ##########
def thumb_one_pics_dir(dir: Path):
    if not dir.is_dir():
        logger.error(f"路径不是一个目录: {dir}")
        return
    out_path = dir.parent / f"{dir.name}.jpg"
    if out_path.exists():
        send2trash.send2trash(out_path)

    out_path = dir.parent / f"{dir.name}_thumb.jpg"
    if out_path.exists():
        logger.warning(f"缩略图已存在: {out_path}")
        return

    vertical_pics = [
        p
        for p in dir.iterdir()
        if p.is_file() and not p.stem.endswith("thumb") and is_vertical(p)
    ]
    horizonal_pics = [
        p
        for p in dir.iterdir()
        if p.is_file() and not p.stem.endswith("thumb") and is_horizontal(p)
    ]
    if len(vertical_pics) > len(horizonal_pics):
        if len(vertical_pics) < 6:
            logger.warning(f"竖幅图片数量少于6张，无法生成缩略图: {dir}")
            return
        logger.info(f"使用竖幅缩略图: {dir}")
        vertical_pics.sort(key=lambda x: natural_sort(x.name))
        positions = [
            (0, 0, 2, 2),
            (2, 0, 1, 1),
            (2, 1, 1, 1),
            (0, 2, 1, 1),
            (1, 2, 1, 1),
            (2, 2, 1, 1),
        ]
        first_img = vertical_pics[0]
        other_imgs = random.sample(vertical_pics[1:], 5)
        with Image.open(first_img) as img:
            cell_width = img.width // 2  # 单元格宽度
            cell_height = img.height // 2  # 单元格高度
        grid_width = cell_width * 3
        grid_height = cell_height * 3
    else:
        if len(horizonal_pics) < 5:
            logger.warning(f"横幅图片数量少于6张，无法生成缩略图: {dir}")
            return
        logger.info(f"使用横幅缩略图: {dir}")
        horizonal_pics.sort(key=lambda x: natural_sort(x.name))
        positions = [
            (0, 0, 2, 2),
            (0, 2, 1, 1),
            (1, 2, 1, 1),
            (0, 3, 1, 1),
            (1, 3, 1, 1),
        ]
        first_img = horizonal_pics[0]
        other_imgs = random.sample(horizonal_pics[1:], 4)
        with Image.open(first_img) as img:
            cell_width = img.width // 2  # 单元格宽度
            cell_height = img.height // 2  # 单元格高度
        grid_width = cell_width * 2
        grid_height = cell_height * 4
    all_imgs = [first_img] + other_imgs
    result_img = Image.new("RGB", (grid_width, grid_height), "white")
    for img_path, pos in zip(all_imgs, positions):
        with Image.open(img_path) as img:
            target_w = cell_width * pos[2]
            target_h = cell_height * pos[3]
            img = img.resize((target_w, target_h), Image.LANCZOS)
            result_img.paste(img, (pos[0] * cell_width, pos[1] * cell_height))
    result_img.save(out_path, quality=100)
    logger.info(f"缩略图已保存: {out_path}")


# 先找到叶子目录，再对每个叶子目录执行缩略图
def thumb_pics_dir(path: Path):
    leaf_dirs = []
    for root, dirs, _ in os.walk(path):
        if len(dirs) == 0:
            leaf_dirs.append(Path(root))
    if not leaf_dirs:
        logger.warning(f"没有找到叶子目录: {path}")
        return
    with ProcessPoolExecutor(max_workers=8) as executor:
        executor.map(thumb_one_pics_dir, leaf_dirs)


############## PICS THUMB ##########


############## VIDS THUMB ##########
def convert_to_mp4(file: Path) -> Path:
    file = file.resolve()
    if not file.is_file() or not file.name.lower().endswith(VIDEOS):
        logger.error(f"文件不是视频格式: {file}")
        return
    if file.name.lower().endswith(".mp4"):
        logger.info(f"文件已是MP4格式: {file}")
        return
    ext = file.suffix.strip(".").lower()
    output_path = file.parent / (file.stem + f"_convert_from_{ext}.mp4")

    logger.info(f"正在转换 {file} 到 MP4 格式")
    result = subprocess.run(
        [
            "ffmpeg",
            "-threads",
            "1",  # 限制 ffmpeg 单线程, 让python进程并行
            "-y",
            "-i",
            str(file),
            "-vcodec",
            "libx264",
            "-acodec",
            "aac",
            str(output_path),
        ],
        stdout=None,  # 继承父进程
        stderr=None,  # 继承父进程
    )

    if result.returncode == 0:
        logger.info(f"转换成功: {file} -> {output_path},已经删除原文件")
        send2trash.send2trash(file)
    else:
        logger.error(f"转换失败: {file}, 错误信息: {result.stderr.decode()}")


def thumb_one_vid(file: Path):
    cv2.setNumThreads(1)  # 限制 OpenCV 单线程, 让python进程并行
    VID_FRAMES = 9
    SKIP_SECONDS = 6

    file = file.resolve()
    if not file.name.lower().endswith(VIDEOS):
        return
    thumb_path = file.parent / (file.stem + "_thumb.jpg")
    if thumb_path.exists():
        logger.warning(f"缩略图已存在: {thumb_path}")
        return

    def capture_frames(vid_path: Path):
        cap = cv2.VideoCapture(str(vid_path))

        if not cap.isOpened():
            logger.error(f"请检查视频文件格式是否正确 {vid_path}")
            return [], 0, 0

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        skip_frames = int(SKIP_SECONDS * fps)
        if skip_frames >= total_frames:
            logger.error(f"视频时长不足 {SKIP_SECONDS} 秒，无法跳过片头: {vid_path}")
            return [], width, height

        usable_frames = total_frames - skip_frames
        interval = usable_frames / float(VID_FRAMES)

        frames = []
        for i in range(VID_FRAMES):
            target_frame = int(skip_frames + i * interval)
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"{i}th 视频帧获取失败: {vid_path}")
                continue
            frames.append(frame)

        cap.release()
        return frames, width, height

    def create_thumb(frames, cell_width, cell_height):
        positons = [
            [0, 0, 3, 3],
            [3, 0, 1, 1],
            [3, 1, 1, 1],
            [2, 2, 1, 1],
            [3, 2, 1, 1],
            [0, 3, 1, 1],
            [1, 3, 1, 1],
            [2, 3, 1, 1],
            [3, 3, 1, 1],
        ]
        thumbnail_height = 4 * cell_height
        thumbnail_width = 4 * cell_width
        thumbnail = np.zeros((thumbnail_height, thumbnail_width, 3), dtype=np.uint8)
        for frame, pos in zip(frames, positons):
            target_w = pos[2] * cell_width
            target_h = pos[3] * cell_height
            if frame is None:
                resized_frame = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            else:
                resized_frame = cv2.resize(frame, (target_w, target_h))
            x_start = pos[0] * cell_width
            y_start = pos[1] * cell_height
            x_end = x_start + pos[2] * cell_width
            y_end = y_start + pos[3] * cell_height
            thumbnail[y_start:y_end, x_start:x_end] = resized_frame
        return thumbnail

    frames, width, height = capture_frames(file)
    if frames:
        thumbnail = create_thumb(frames, width // 2, height // 2)
        cv2.imwrite(thumb_path, thumbnail)
        logger.info(f"缩略图已保存: {thumb_path}")
    else:
        logger.error(f"未能从视频中捕获帧: {file}")


def thumb_vids_dir(path: Path):
    target_vids = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith(VIDEOS):
                target_vids.append(Path(root) / file)
    with ProcessPoolExecutor(max_workers=8) as executor:
        executor.map(convert_to_mp4, target_vids)
    # 确保转换完成，再读取一次target_vids

    target_vids = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith(VIDEOS):
                target_vids.append(Path(root) / file)
    with ProcessPoolExecutor(max_workers=8) as executor:
        executor.map(thumb_one_vid, target_vids)


############## VIDS THUMB ##########


if __name__ == "__main__":
    eb_vids = "/home/hewangma/projects/PV-Server/resource/eb/Vids"
    # remove_existing_thumb(Path(eb_vids))
    thumb_vids_dir(Path(eb_vids))
