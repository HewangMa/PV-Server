import os,shutil

dir = "/mnt/mechanical/resource/qinqinwo/1-4/pics"
for file in os.listdir(dir):
    name, type = file.split('.')
    name_num = int(name)
    old_path = os.path.join(dir, file)
    if name_num < 125:
        new_path = os.path.join(
            "/mnt/mechanical/resource/qinqinwo/1-4/pics1", file)
        shutil.move(old_path, new_path)
    elif name_num < 350:
        new_path = os.path.join(
            "/mnt/mechanical/resource/qinqinwo/1-4/pics2", file)
        shutil.move(old_path, new_path)
    else:
        new_path = os.path.join(
            "/mnt/mechanical/resource/qinqinwo/1-4/pics3", file)
        shutil.move(old_path, new_path)
