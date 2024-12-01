import os
import shutil

def make_dir(dir,folder):
    folder_path = os.path.join(dir,folder)
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
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
            make_dir(root,folder)

# 使用方法
directory = "."
rename_and_copy_first_image(directory)
