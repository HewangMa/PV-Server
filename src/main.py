import argparse
from pathlib import Path
from logger import get_logger
from extract import batch_extract
from server import start_server
from cat_vids import cat_dirs
from thumb import thumb_pics_dirs, thumb_dir, convert_dir
from utils import remove_existing_vids_thumb, remove_existing_pics_thumb
from OSS import backup_dir

logger = get_logger("main", level="DEBUG")


def main():
    parser = argparse.ArgumentParser(description="批量文件工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ===== unrar 子命令 =====
    parser_unrar = subparsers.add_parser("unrar", help="批量解压缩 rar 文件")
    parser_unrar.add_argument("-p", "--path", type=str, required=True, help="目标路径")
    parser_unrar.add_argument("-pwd", "--password", type=str, help="解压密码")

    # ===== server 子命令 =====
    parser_server = subparsers.add_parser("server", help="启动浏览服务器")

    # ===== cat 子命令 =====
    parser_cat = subparsers.add_parser("cat", help="连接一个目录下的视频文件")
    parser_cat.add_argument("-p", "--path", type=str, required=True, help="目标路径")

    # ===== p-thumb 子命令 =====
    parser_thumb = subparsers.add_parser("p-thumb", help="生成图片/视频缩略图")
    parser_thumb.add_argument("-p", "--path", type=str, required=True, help="目标路径")
    parser_thumb.add_argument(
        "-remove", action="store_true", help="是否删除已存在的缩略图"
    )

    # ===== v-thumb 子命令 =====
    parser_thumb = subparsers.add_parser("v-thumb", help="生成图片/视频缩略图")
    parser_thumb.add_argument("-p", "--path", type=str, required=True, help="目标路径")
    parser_thumb.add_argument("-convert", action="store_true", help="是否转换视频格式")
    parser_thumb.add_argument(
        "-remove", action="store_true", help="是否删除已存在的缩略图"
    )

    # ===== backup 子命令 =====
    parser_backup = subparsers.add_parser("backup", help="备份文件夹")
    parser_backup.add_argument("-p", "--path", type=str, required=True, help="目标路径")

    # ===== clean 子命令 =====
    parser_clean = subparsers.add_parser("clean", help="清理图片文件夹")
    parser_clean.add_argument("-p", "--path", type=str, required=True, help="目标路径")

    args = parser.parse_args()

    # === 命令分发 ===
    if args.command == "unrar":
        password = args.password  # 可以是空，默认值在 extract.py 中
        batch_extract(Path(args.path).resolve(), password)

    elif args.command == "server":
        start_server()

    elif args.command == "cat":
        cat_dirs(Path(args.path).resolve())

    elif args.command == "p-thumb":
        if args.remove:
            remove_existing_pics_thumb(Path(args.path).resolve())
        thumb_pics_dirs(Path(args.path).resolve())

    elif args.command == "v-thumb":
        if args.remove:
            remove_existing_vids_thumb(Path(args.path).resolve())
        if args.convert:
            convert_dir(Path(args.path).resolve())
        thumb_dir(Path(args.path).resolve())

    elif args.command == "backup":
        backup_dir(Path(args.path).resolve())

    elif args.command == "clean":
        pass


if __name__ == "__main__":
    main()
