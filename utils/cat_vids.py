import os
from moviepy import VideoFileClip
from moviepy import concatenate_videoclips
import subprocess
import argparse
import sys

from pathlib import Path


def concat_dir(target_dir):
    """
    将dir下的所有视频文件按照文件名的顺序拼接为最低720p的mp4文件
    """
    video_files = [
        f for f in os.listdir(target_dir) if f.lower().endswith(tuple(vid_forms))
    ]
    if not video_files:
        print("没有找到任何视频文件")
        return

    video_files.sort()
    name = video_files[0].split(".")[0]
    output_filename = f"{video_files[0]}.mp4"
    output_path = os.path.join(os.path.dirname(target_dir), output_filename)

    list_file_path = os.path.join(target_dir, "file_list.txt")
    with open(list_file_path, "w") as list_file:
        for video in video_files:
            video_path = os.path.join(target_dir, video)
            list_file.write(f"file '{video_path}'\n")

    command = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",  # 允许绝对路径
        "-i",
        list_file_path,
        "-c",
        "copy",  # 直接复制流，不重新编码
        "-y",  # 如果输出文件已存在则覆盖
        output_path,
    ]

    try:
        print(f"尝试拼接 {target_dir} 目录中的视频")
        subprocess.run(command, check=True)
        print(f"视频拼接成功，输出文件: {output_path}")
        # if os.path.exists(list_file_path):
        #     os.remove(list_file_path)
    except subprocess.CalledProcessError as e:
        print(f"视频拼接失败: {e}")


vid_forms = [
    "avi",
    "AVI",
    "mp4",
    "MP4",
    "mov",
    "MOV",
    "wmv",
    "WMV",
    "mkv",
    "MKV",
    "flv",
    "FLV",
    "webm",
    "WEBM",
    "mpeg",
    "MPEG",
    "mpg",
    "MPG",
    "m4v",
    "M4V",
    "3gp",
    "3GP",
    "asf",
    "ASF",
    "vob",
    "VOB",
    "ts",
    "TS",
    "m2ts",
    "M2TS",
    "divx",
    "DIVX",
    "rm",
    "RM",
    "rmvb",
    "RMVB",
    "ogv",
    "OGV",
    "mxf",
    "MXF",
    "mpv",
    "MPV",
    "hevc",
    "HEVC",
]


def merge_videos(end_dir_path):
    path = Path(end_dir_path)
    file_name = path.name
    output_file = os.path.join(os.path.dirname(end_dir_path), f"{file_name}.mp4")
    videos = sorted(
        [
            os.path.join(end_dir_path, f)
            for f in os.listdir(end_dir_path)
            if f.lower().endswith(tuple(vid_forms))
        ]
    )
    if not videos:
        print("没有找到视频文件！")
        return
    clips = [VideoFileClip(video) for video in videos]
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
    print(f"视频已保存为：{output_file}")


def is_end_dir(dir_path):
    if not os.path.isdir(dir_path):
        return False
    subdirs = []
    with os.scandir(dir_path) as entries:
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):  # 不追踪符号链接
                subdirs.append(entry.path)
    return len(subdirs) == 0


def merge_folder(dir_path):
    if is_end_dir(dir_path):
        merge_videos(dir_path)
    else:
        if os.path.isdir(dir_path):
            for sub in os.listdir(dir_path):
                sub_path = os.path.join(dir_path, sub)
                merge_folder(sub_path)


if __name__ == "__main__":
    # 读取目录
    parser = argparse.ArgumentParser(
        description="跨平台目录处理工具",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "path", type=str, help="要处理的目录路径（Windows/Linux均支持）"
    )
    args = parser.parse_args()
    target_dir = os.path.abspath(os.path.normpath(args.path))
    if not os.path.isdir(target_dir):
        print(f"错误：路径不存在或不是目录 -> {target_dir}")
        sys.exit(1)
    # 执行处理
    merge_folder(target_dir)
