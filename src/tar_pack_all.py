import os
import tarfile


def compress_files_to_tar(source_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for item in os.listdir(source_dir):
        print(f"packing {item}")
        item_path = os.path.join(source_dir, item)
        tar_file_path = os.path.join(output_dir, f"{item}.tar")
        with tarfile.open(tar_file_path, "w") as tar:
            tar.add(item_path, arcname=item)
            print(f"Compressed: {item_path} -> {tar_file_path}")


if __name__ == "__main__":
    source_directory = "/mnt/mechanical/resource/docs"
    output_directory = "/mnt/mechanical/resource/tars"
    compress_files_to_tar(source_directory, output_directory)
