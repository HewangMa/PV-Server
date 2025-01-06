import os
from moviepy import VideoFileClip
from moviepy import concatenate_videoclips


def merge_videos(directory, output_file):
    videos = sorted([os.path.join(directory, f) for f in os.listdir(
        directory) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.mpg'))])
    if not videos:
        print("没有找到视频文件！")
        return
    clips = [VideoFileClip(video) for video in videos]
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
    print(f"视频已保存为：{output_file}")


if __name__ == '__main__':
    base_dir = '/mnt/mechanical/resource/ls-short-videos-todo/'
    for dir in os.listdir(base_dir):
        dir_path = os.path.join(base_dir, dir)
        print(dir_path)
        if os.path.isdir(dir_path) and '.' not in dir:
            target = base_dir+dir.split(' ')[0]+".mp4"
            print(target)
            merge_videos(dir_path, target)
