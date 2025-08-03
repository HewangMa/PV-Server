import alibabacloud_oss_v2 as oss
from pprint import pprint
from collections import defaultdict
import logging
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from utils import VIDEOS, IMAGES
from logger import get_logger

logger = get_logger(name="OSS", level=logging.DEBUG)


def collect_to_backup(local_dir: Path) -> list[Path]:
    leaf_files = []

    def _traverse(path: Path):
        if path.is_file():
            if "temp" not in path.parts and path.name.lower().endswith(IMAGES + VIDEOS):
                leaf_files.append(path)
        else:
            for sub in path.iterdir():
                _traverse(sub)

    _traverse(local_dir)
    return leaf_files


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
        files_to_upload = collect_to_backup(local_dir)
        with ThreadPoolExecutor(max_workers=32) as executor:
            futures = [
                executor.submit(self.upload_file, file) for file in files_to_upload
            ]
            for future in as_completed(futures):
                future.result()
        logger.info(f"Finished uploading {len(files_to_upload)} files")


def backup_dir(path: Path):
    path = path.resolve()
    if not path.exists() or not path.is_dir():
        logger.error(f"Path {path} does not exist or is not a directory.")
        sys.exit(1)

    uploader = Uploader()
    uploader.upload_dir(path)
    logger.info(f"Backup of {path} completed.")
