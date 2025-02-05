import cv2
import argparse
import numpy as np
import os
import time
import sys
import subprocess


def rename_all(dir):
    for i, file in enumerate(os.listdir(dir)):
        print(file)
        new_name = str(i) + file[-4:]
        os.rename(dir + file, dir + new_name)
        print(f"Renamed {file} to {new_name}")


def vid_gen_thumb(vid_path):
    '''
    给一个vid路径，在该路径下生成同名的thumb
    '''

    def capture_frames(vid_path, num_frames):
        cap = cv2.VideoCapture(vid_path)

        if not cap.isOpened():
            print("Error: Could not open video.")
            return [], 0, 0

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        interval = int(0.95 * total_frames) // num_frames

        frames = []
        for i in range(num_frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i * interval + 4)
            ret, frame = cap.read()
            if not ret:
                print(f"Error: Could not read frame {i * interval}.")
                break
            frames.append(frame)
        cap.release()
        return frames, width, height

    def create_thumbnail(frames, thumb_width=100, thumb_height=100, columns=5):
        print(thumb_width, thumb_height)
        resized_frames = [
            cv2.resize(frame, (thumb_width, thumb_height)) for frame in frames
        ]
        rows = (len(resized_frames) + columns - 1) // columns
        thumbnail_height = rows * thumb_height
        thumbnail_width = columns * thumb_width
        thumbnail = np.zeros(
            (thumbnail_height, thumbnail_width, 3), dtype=np.uint8)
        for i, frame in enumerate(resized_frames):
            row = i // columns
            col = i % columns
            y_start = row * thumb_height
            y_end = y_start + thumb_height
            x_start = col * thumb_width
            x_end = x_start + thumb_width
            thumbnail[y_start:y_end, x_start:x_end] = frame

        return thumbnail

    filename_list = vid_path.split('.')
    thumb_path = f"{filename_list[0]}.jpg"
    num_frames = 20
    frames, width, height = capture_frames(vid_path, num_frames)
    if frames:
        thumbnail = create_thumbnail(frames, width, height, columns=5)
        cv2.imwrite(thumb_path, thumbnail)
        print(f"Thumbnail saved to {thumb_path}")
    else:
        print("No frames were captured.")


vid_forms = [
    'avi',
    'AVI',
    'mp4',
    'MP4',
    'mov',
    'MOV',
    'wmv',
    'WMV',
    'mkv',
    'MKV',
    'flv',
    'FLV',
    'webm',
    'WEBM',
    'mpeg',
    'MPEG',
    'mpg',
    'MPG',
    'm4v',
    'M4V',
    '3gp',
    '3GP',
    'asf',
    'ASF',
    'vob',
    'VOB',
    'ts',
    'TS',
    'm2ts',
    'M2TS',
    'divx',
    'DIVX',
    'rm',
    'RM',
    'rmvb',
    'RMVB',
    'ogv',
    'OGV',
    'mxf',
    'MXF',
    'mpv',
    'MPV',
    'hevc',
    'HEVC',
]


def gen_thumbs_and_unify_to_mp4(dir):
    '''
    将所有视频转换为mp4；
    并生成预览图
    '''
    for root, _, files in os.walk(dir):
        for file in files:

            filepath = os.path.join(root, file)
            if any(filepath.endswith(f'.{form}.jpg') for form in vid_forms):
                os.remove(filepath)
                continue
            filename_list = filepath.split('.')
            prefix, ext = '_'.join(
                filename_list[:-1]).replace(' ', "_"), filename_list[-1]
            # 图片不处理
            if ext == 'jpg':
                print(f"jump {filepath}")
                continue

            _filepath = f"{prefix}.{ext}"
            os.rename(filepath, _filepath)

            # 把不是mp4的文件转换成mp4，这一步之后不要执行concat
            mp4_filepath = f"{prefix}.mp4"
            if ext.lower() != 'mp4' and not os.path.exists(mp4_filepath):
                print(f'Changing {_filepath} to mp4')
                result = subprocess.run(
                    ['ffmpeg', '-i', _filepath, '-vcodec',
                        'libx264', '-acodec', 'aac', mp4_filepath],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                if result.returncode == 0:
                    print(f"Successfully converted {_filepath} to MP4.")
                else:
                    print(f"Error converting {_filepath}: {
                          result.stderr.decode()}")
                os.remove(_filepath)
                _filepath = mp4_filepath

            thumb_filepath = f"{prefix}.jpg"
            if not os.path.exists(thumb_filepath):
                vid_gen_thumb(_filepath)


def concat_dir(target_dir):
    '''
    将dir下的所有视频文件按照文件名的顺序拼接为最低720p的mp4文件
    '''
    video_files = [f for f in os.listdir(
        target_dir) if f.lower().endswith(tuple(vid_forms))]
    if not video_files:
        print("没有找到任何视频文件")
        return

    video_files.sort()
    name = video_files[0].split(".")[0]
    output_filename = f"{video_files[0]}.mp4"
    output_path = os.path.join(os.path.dirname(target_dir), output_filename)
    
    list_file_path = os.path.join(target_dir, "file_list.txt")
    with open(list_file_path, 'w') as list_file:
        for video in video_files:
            video_path = os.path.join(target_dir, video)
            list_file.write(f"file '{video_path}'\n")

    command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',  # 允许绝对路径
        '-i', list_file_path,
        '-c', 'copy',  # 直接复制流，不重新编码
        '-y',  # 如果输出文件已存在则覆盖
        output_path
    ]

    try:
        print(f"尝试拼接 {target_dir} 目录中的视频")
        subprocess.run(command, check=True)
        print(f"视频拼接成功，输出文件: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"视频拼接失败: {e}")
    finally:
        if os.path.exists(list_file_path):
            os.remove(list_file_path)


if __name__ == "__main__":
    # 读取目录
    parser = argparse.ArgumentParser(
        description="跨平台目录处理工具",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'path',
        type=str,
        help="要处理的目录路径（Windows/Linux均支持）"
    )
    args = parser.parse_args()
    target_dir = os.path.abspath(os.path.normpath(args.path))
    if not os.path.isdir(target_dir):
        print(f"错误：路径不存在或不是目录 -> {target_dir}")
        sys.exit(1)
    # 执行处理
    gen_thumbs_and_unify_to_mp4(target_dir)
