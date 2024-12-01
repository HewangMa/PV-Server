import os
# from moviepy.editor import VideoFileClip, concatenate_videoclips

# def merge_videos(directory, output_file):
#     videos = sorted([os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))])
#     if not videos:
#         print("没有找到视频文件！")
#         return
#     clips = [VideoFileClip(video) for video in videos]
#     final_clip = concatenate_videoclips(clips)
#     final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
#     print(f"视频已保存为：{output_file}")

if __name__ == '__main__':
    dir = os.path.dirname(__file__)
    print(dir)
    # output_file = "output_video.mp4"
    # merge_videos(directory, output_file)
