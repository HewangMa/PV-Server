import shutil
import os

cnt = 0
for root, dirs, files in os.walk("/mnt/mechanical/resource/qinqinwo/1"):
    for dir in dirs:
        path = os.path.join(root, dir)
        for file in os.listdir(path):
            old_file_path = os.path.join(path, file)
            type = file.split('.')[-1]
            new_file_path = os.path.join(root, f"{cnt}.{type}")
            cnt += 1
            shutil.copy(old_file_path, new_file_path)
