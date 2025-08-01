import os
import shutil
import argparse
import sys


def make_dir(dir, folder):
    folder_path = os.path.join(dir, folder)
    images = [f for f in os.listdir(
        folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if images:
        images.sort()  # 确保按文件名排序
        first_image = images[0]
        old_image_path = os.path.join(folder_path, first_image)
        new_image_name = f"{folder}.jpg"
        new_image_path = os.path.join(dir, new_image_name)
        shutil.copy(old_image_path, new_image_path)


def rename_and_copy_first_image(directory):
    for root, dirs, files in os.walk(directory):
        for folder in dirs:
            make_dir(root, folder)



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
    rename_and_copy_first_image(target_dir)