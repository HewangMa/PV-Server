import subprocess
from pathlib import Path
import sys
from logger import get_logger
from utils import ZIPS
import os

logger = get_logger("extractor", level="INFO")


def extract_rar(rar_path: Path, password: str):
    extract_dir = rar_path.parent
    extract_dir.mkdir(exist_ok=True)

    try:
        cmd = [
            "7z",
            "x",
            f"-p{password}",
            str(rar_path),
            f"-o{extract_dir}",
            "-y",  # 自动全部 yes
        ]
        _ = subprocess.run(cmd, stdout=None, stderr=None, text=True)
    except Exception as e:
        logger.error(f"❌ 解压失败：{rar_path.name}")
        logger.info(e)
    finally:
        logger.info(f"完成：{rar_path.name} -> {extract_dir}")


def batch_extract(dir_path: Path, password: str):
    if password is None:
        password = "@-LS-Models-Collection-@"
    if not dir_path.is_dir():
        logger.warning(f"目录不存在：{dir_path}")
        sys.exit(1)

    rar_files = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            path = Path(root) / file
            if path.suffix.lower() in ZIPS and "temp" not in path.parts:
                rar_files.append(path)

    logger.info(f"共找到 {len(rar_files)} 个 .rar 文件，开始解压...\n")
    for rar_file in rar_files:
        extract_rar(rar_file, password)
