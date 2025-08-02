"""
python main.py -unrar -p <path> # 批量解压缩rar文件
python main.py -server # 启动服务器
python main.py -cat -p <path> # 连接一个目录下的视频文件
python main.py -thumb -p <path> # 对图片文件夹和视频文件夹生成缩略图
python main.py -backup -p <path> # 备份文件夹
python main.py -clean -p <path> # 清理图片文件夹
"""

import argparse
import sys
from pathlib import Path
from logger import get_logger

logger = get_logger("main", level="DEBUG")


def main():
    parser = argparse.ArgumentParser(description="PV Server SDK - 统一入口")

    # 主命令（互斥）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-unrar", action="store_true", help="批量解压缩 rar 文件")
    group.add_argument("-server", action="store_true", help="启动浏览服务器")
    group.add_argument("-cat", action="store_true", help="连接一个目录下的视频文件")
    group.add_argument("-thumb", action="store_true", help="生成图片/视频缩略图")
    group.add_argument("-backup", action="store_true", help="备份文件夹")
    group.add_argument("-clean", action="store_true", help="清理图片文件夹")

    # 通用参数
    parser.add_argument("-p", "--path", type=str, help="目标路径")
    parser.add_argument("-pwd", "--password", type=str, help="解压密码（unrar 用）")

    args = parser.parse_args()

    # === 命令分发 ===
    if args.unrar:
        if not args.path:
            logger.error("❌ 批量解压必须指定路径：-p <path>")
            sys.exit(1)

    elif args.server:
        from server import start_server

        start_server()

    elif args.cat:
        if not args.path:
            logger.error("连接视频必须指定路径：-p <path>")
            sys.exit(1)

    elif args.thumb:
        if not args.path:
            logger.error("生成缩略图必须指定路径：-p <path>")
            sys.exit(1)
        from thumb import thumb_pics_dir, thumb_vids_dir

        thumb_pics_dir(Path(args.path).resolve())
        thumb_vids_dir(Path(args.path).resolve())

    elif args.backup:
        if not args.path:
            logger.error("批量备份必须指定路径：-p <path>")
            sys.exit(1)
        from OSS import backup_dir

        backup_dir(Path(args.path).resolve())

    elif args.clean:
        if not args.path:
            logger.error("清理图片文件夹必须指定路径：-p <path>")
            sys.exit(1)


if __name__ == "__main__":
    main()
