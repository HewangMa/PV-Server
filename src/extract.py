import os
import argparse
import rarfile
from pathlib import Path
import time

import subprocess
import argparse
from pathlib import Path
import time
import sys

def extract_rar(rar_path: Path, password: str):
    extract_dir = rar_path.parent
    extract_dir.mkdir(exist_ok=True)

    try:
        cmd = [
            "7z", "x",
            f"-p{password}",
            str(rar_path),
            f"-o{extract_dir}",
            "-y"  # 自动全部 yes
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        print(f"解压完成：{rar_path.name}")

        if any(extract_dir.iterdir()):
            print("✅ 所有文件成功解压\n")
        else:
            print(f"⚠️ 解压目录为空：{extract_dir}\n")
            print(result.stdout)
            print(result.stderr)
    except Exception as e:
        print(f"❌ 解压失败：{rar_path.name}")
        print(e)

def batch_extract(dir_path: Path, password: str):
    if not dir_path.is_dir():
        print(f"目录不存在：{dir_path}")
        sys.exit(1)

    rar_files = list(dir_path.rglob("*.rar"))
    if not rar_files:
        print("❌ 未找到任何 .rar 文件")
        return

    print(f"共找到 {len(rar_files)} 个 .rar 文件，开始解压...\n")
    for rar_file in rar_files:
        extract_rar(rar_file, password)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量解压 RAR 文件")
    parser.add_argument("-d", "--dir", required=True, help="RAR 文件所在目录")
    parser.add_argument("-p", "--password", required=True, help="解压密码")
    args = parser.parse_args()

    batch_extract(Path(args.dir).resolve(), args.password)

