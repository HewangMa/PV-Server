import os
import cv2
import time
import random
import send2trash
import subprocess
import numpy as np
from pathlib import Path
from logger import get_logger
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ProcessPoolExecutor
from utils import VIDEOS, get_thumb, is_vertical, natural_sort, is_horizontal


pic_logger = get_logger("pics_thumb", level="DEBUG")


def thumb_one_pics_dir(dir: Path):
    if not dir.is_dir():
        pic_logger.error(f"路径不是一个目录: {dir}")
        return
    thumb = get_thumb(dir)
    if thumb.exists():
        pic_logger.warning(f"缩略图已存在: {thumb}")
        return

    vertical_pics = [p for p in dir.iterdir() if p.is_file() and is_vertical(p)]
    horizonal_pics = [p for p in dir.iterdir() if p.is_file() and is_horizontal(p)]
    if len(vertical_pics) > len(horizonal_pics):
        if len(vertical_pics) < 6:
            pic_logger.warning(f"数量太少，无法生成缩略图: {dir}")
            return
        vertical_pics.sort(key=lambda x: natural_sort(x.name))
        positions = [
            (0, 0, 2, 2),
            (2, 0, 1, 1),
            (2, 1, 1, 1),
            (0, 2, 1, 1),
            (1, 2, 1, 1),
            (2, 2, 1, 1),
        ]
        head_img = vertical_pics[1]
        other_imgs = random.sample(vertical_pics, 5)
        with Image.open(head_img) as img:
            cell_width = img.width // 2  # 单元格宽度
            cell_height = img.height // 2  # 单元格高度
        grid_width = cell_width * 3
        grid_height = cell_height * 3
    else:
        if len(horizonal_pics) < 5:
            pic_logger.warning(f"数量太少，无法生成缩略图: {dir}")
            return
        horizonal_pics.sort(key=lambda x: natural_sort(x.name))
        positions = [
            (0, 0, 2, 2),
            (0, 2, 1, 1),
            (1, 2, 1, 1),
            (0, 3, 1, 1),
            (1, 3, 1, 1),
        ]
        head_img = horizonal_pics[1]
        other_imgs = random.sample(horizonal_pics, 4)
        with Image.open(head_img) as img:
            cell_width = img.width // 2  # 单元格宽度
            cell_height = img.height // 2  # 单元格高度
        grid_width = cell_width * 2
        grid_height = cell_height * 4
    all_imgs = [head_img] + other_imgs
    result_img = Image.new("RGB", (grid_width, grid_height), "white")
    for img_path, pos in zip(all_imgs, positions):
        with Image.open(img_path) as img:
            target_w = cell_width * pos[2]
            target_h = cell_height * pos[3]
            img = img.resize((target_w, target_h), Image.LANCZOS)
            result_img.paste(img, (pos[0] * cell_width, pos[1] * cell_height))

    # 添加文字
    total_pics = len(vertical_pics) + len(horizonal_pics)
    text = f"{total_pics} pics"
    draw = ImageDraw.Draw(result_img)
    font_size = cell_width / 3
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    x, y = cell_height / 20, cell_height / 20
    black_width = cell_width / 100
    draw.text((x - black_width, y - black_width), text, font=font, fill="black")
    draw.text((x + black_width, y - black_width), text, font=font, fill="black")
    draw.text((x - black_width, y + black_width), text, font=font, fill="black")
    draw.text((x + black_width, y + black_width), text, font=font, fill="black")
    draw.text((x, y), text, font=font, fill="white")

    result_img.save(thumb, quality=100)
    pic_logger.info(f"缩略图已保存: {thumb}")
    time.sleep(0.5)


def thumb_pics_dirs(path: Path):
    leaf_dirs = []
    for root, dirs, _ in os.walk(path):
        if len(dirs) == 0 and "temp" not in Path(root).parts:
            leaf_dirs.append(Path(root))
    with ProcessPoolExecutor(max_workers=8) as executor:
        executor.map(thumb_one_pics_dir, leaf_dirs)


############## PICS THUMB ##############
############## PICS THUMB ##############
############## PICS THUMB ##############


############## VIDS THUMB ##############
############## VIDS THUMB ##############
############## VIDS THUMB ##############
vid_logger = get_logger("vids_thumb", level="DEBUG")


def convert_vid(file: Path) -> Path:
    file = file.resolve()
    if not file.is_file() or not file.name.lower().endswith(VIDEOS):
        vid_logger.error(f"文件不是视频格式: {file}")
        return
    ext = file.suffix.strip(".").lower()
    output_path = file.parent / (file.stem + f"_convert_from_{ext}.mp4")

    vid_logger.info(f"正在转换 {file} 到 MP4 格式")
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
        ]
    )

    if result.returncode == 0:
        vid_logger.info(f"转换成功: {file} -> {output_path},已经删除原文件")
        send2trash.send2trash(file)
    else:
        vid_logger.error(f"转换失败: {file}")
    time.sleep(0.5)


def thumb_vid(file: Path):
    VID_FRAMES = 9

    file = file.resolve()
    if not file.name.lower().endswith(VIDEOS):
        return
    thumb_path = get_thumb(file)
    if thumb_path.exists():
        vid_logger.warning(f"缩略图已存在: {thumb_path}")
        return

    def format_time(seconds):
        """格式化秒为 mm:ss"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"duration {minutes:02}:{secs:02}"

    def capture_frames(vid_path: Path):
        cap = cv2.VideoCapture(str(vid_path))

        if not cap.isOpened():
            vid_logger.error(f"请检查视频文件格式是否正确 {vid_path}")
            return [], 0, 0, 0.0

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        duration_seconds = total_frames / fps  # 视频总时长
        skip_frames = 2 * total_frames // (VID_FRAMES)
        usable_frames = total_frames - skip_frames
        interval = usable_frames // VID_FRAMES

        frames = []
        for i in range(VID_FRAMES):
            target_frame = int(skip_frames + i * interval)
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            ret, frame = cap.read()
            if not ret:
                vid_logger.warning(f"{i}th 视频帧获取失败: {vid_path}")
                frame = None
            frames.append(frame)

        cap.release()
        return frames, width, height, duration_seconds

    def create_thumb(frames, cell_width, cell_height, duration_text=None):
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

        if duration_text:
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = max(2, cell_width // 180)
            thickness = max(2, cell_width // 60)
            x, y = cell_width // 6, cell_height // 2

            cv2.putText(
                thumbnail,
                duration_text,
                (x, y),
                font,
                font_scale,
                (0, 0, 0),
                max(int(thickness * 1.3), thickness + 2),
                lineType=cv2.LINE_AA,
            )
            cv2.putText(
                thumbnail,
                duration_text,
                (x, y),
                font,
                font_scale,
                (255, 255, 255),
                thickness,
                lineType=cv2.LINE_AA,
            )

        return thumbnail

    frames, width, height, duration_seconds = capture_frames(file)
    if frames:
        duration_text = format_time(duration_seconds)
        thumbnail = create_thumb(frames, width // 2, height // 2, duration_text)
        cv2.imwrite(str(thumb_path), thumbnail)
        vid_logger.info(f"缩略图已保存: {thumb_path}（总时长: {duration_text}）")
    else:
        vid_logger.error(f"未能从视频中捕获帧: {file}")


def convert_dir(path: Path):
    target_vids = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith(VIDEOS) and "temp" not in Path(root).parts:
                target_vids.append(Path(root) / file)
    # ffmpeg自身是多线程的
    for file in target_vids:
        convert_vid(file)


def thumb_dir(path: Path):
    target_vids = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith(VIDEOS) and "temp" not in Path(root).parts:
                target_vids.append(Path(root) / file)
    # ffmpeg自身是多线程的
    for file in target_vids:
        thumb_vid(file)
