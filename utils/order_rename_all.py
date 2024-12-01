import os

def rename_all(directory):
    folder_count = 0
    file_count = 0

    for root, dirs, files in os.walk(directory, topdown=True):
        # 重命名子文件夹
        for i, folder in enumerate(dirs):
            folder_count += 1
            new_folder_name = f"folder_{folder_count}"
            old_folder_path = os.path.join(root, folder)
            new_folder_path = os.path.join(root, new_folder_name)
            os.rename(old_folder_path, new_folder_path)
            dirs[i] = new_folder_name  # 更新目录名以确保正确递归

        # 重命名文件
        for file in files:
            file_count += 1
            file_extension = os.path.splitext(file)[1]
            new_file_name = f"file_{file_count}{file_extension}"
            old_file_path = os.path.join(root, file)
            new_file_path = os.path.join(root, new_file_name)
            os.rename(old_file_path, new_file_path)

# 使用方法
directory = "."
rename_all(directory)