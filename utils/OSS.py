import alibabacloud_oss_v2 as oss
from pprint import pprint
from collections import defaultdict
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import argparse


def get_logger(
    name: str,
    level: int = logging.DEBUG,
    log_dir: str = "./logs",
    console: bool = True,
    when: str = "midnight",
    backup_count: int = 7,
) -> logging.Logger:
    """
    创建一个可复用的日志记录器
    :param name: 日志记录器名称
    :param level: 日志级别
    :param log_dir: 日志文件保存路径
    :param console: 是否输出到控制台
    :param when: 按时间滚动日志（'S', 'M', 'H', 'D', 'midnight', 'W0'-'W6'）
    :param backup_count: 日志保留份数
    :return: 配置好的 Logger 实例
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # 避免重复输出

    if not logger.handlers:  # 避免重复添加 handler
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
        )

        # 文件 Handler
        file_handler = TimedRotatingFileHandler(
            filename=f"{log_dir}/{name}.log",
            when=when,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 控制台 Handler
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    return logger


def collect_leaf_files(local_dir: Path) -> list[Path]:
    leaf_files = []

    def _traverse(path: Path):
        if path.is_file():
            leaf_files.append(path)
        else:
            for sub in path.iterdir():
                _traverse(sub)

    _traverse(local_dir)
    return leaf_files


logger = get_logger("oss_mag")

MAX_RETRIES = 3
RETRY_DELAY = 2


class MAG:
    def __init__(self):
        credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()
        cfg = oss.config.load_default()
        cfg.credentials_provider = credentials_provider
        cfg.region = "cn-shanghai"
        cfg.endpoint = "oss-cn-shanghai.aliyuncs.com"
        self.client = oss.Client(cfg)
        self.bucket = "ali-oss1"

    def all_objs(self):
        ret = []
        paginator = self.client.list_objects_v2_paginator()
        for page in paginator.iter_page(oss.ListObjectsV2Request(bucket=self.bucket)):
            ret += list(page.contents)
        return ret

    def list_leaf_dirs(self):
        dirs = defaultdict(int)
        objs = self.all_objs()
        for o in objs:
            dir = "/".join(o.key.split("/")[:-1])
            dirs[dir] += 1
        pprint(dirs)


class Uploader(MAG):
    def __init__(self):
        super().__init__()

    def upload_file(self, local_path: Path) -> None:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # 上传到以项目为开头的key，key根据提供的local_path固定
                oss_key = str(Path(*local_path.parts[4:]))
                if self.client.is_object_exist(bucket=self.bucket, key=oss_key):
                    logger.info(f"Obj key {oss_key} exists!")
                    return
                with open(local_path, "rb") as f:
                    request = oss.PutObjectRequest(
                        bucket=self.bucket, key=oss_key, body=f
                    )
                    result = self.client.put_object(request)
                logger.info(
                    f"Uploaded {local_path} ! status code: {result.status_code},"
                )
                return
            except Exception as e:
                logger.warning(
                    f"[{local_path.name}] upload failed {attempt}th times with {e}"
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"[{local_path.name}] gives up uploading")

    def upload_dir(self, local_dir: Path):
        files_to_upload = collect_leaf_files(local_dir)
        logger.info(f"Ready to Upload {len(files_to_upload)} files parallel")
        time.sleep(4)
        with ThreadPoolExecutor(max_workers=32) as executor:
            futures = [
                executor.submit(self.upload_file, file) for file in files_to_upload
            ]
            for future in as_completed(futures):
                future.result()


def get_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-p",
        "--dir_path",
        required=True,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    local_file = Path(args.dir_path).resolve()
    logger.info(local_file)
    Uploader().upload_dir(local_file)
