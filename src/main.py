import argparse
from pathlib import Path
from logger import get_logger

logger = get_logger("main", level="DEBUG")


def main():
    # 这部分需要重新设计 argparse 的结构
    parser = argparse.ArgumentParser(description="批量文件工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ===== unrar  =====
    sub_parser = subparsers.add_parser("unrar", help="批量解压缩 rar 文件")
    sub_parser.add_argument("-p", "--path", type=str, required=True, help="目标路径")
    sub_parser.add_argument("-pwd", "--password", type=str, help="解压密码")

    # ===== server  =====
    sub_parser = subparsers.add_parser("server", help="启动浏览服务器")

    # ===== cat  =====
    sub_parser = subparsers.add_parser("cat", help="连接一个目录下的视频文件")
    sub_parser.add_argument("-p", "--path", type=str, required=True, help="目标路径")

    # ===== flat  =====
    sub_parser = subparsers.add_parser("flat", help="将一个目录拍平")
    sub_parser.add_argument("-p", "--path", type=str, required=True, help="目标路径")

    # ===== thumb  =====
    sub_parser = subparsers.add_parser("thumb", help="生成图片缩略图")
    sub_parser.add_argument("-p", "--path", type=str, required=True, help="目标路径")
    sub_parser.add_argument("-vid", action="store_true", help="生成视频缩略图")
    sub_parser.add_argument("-pic", action="store_true", help="生成图片缩略图")
    sub_parser.add_argument(
        "-remove", action="store_true", help="移除已有图片和视频缩略图"
    )

    # ===== convert =====
    sub_parser = subparsers.add_parser("convert", help="转换视频格式为 mp4")
    sub_parser.add_argument("-p", "--path", type=str, required=True, help="目标路径")

    # ===== backup  =====
    parser_backup = subparsers.add_parser("backup", help="备份文件夹")
    parser_backup.add_argument("-p", "--path", type=str, required=True, help="目标路径")

    # ===== classify  =====
    sub_parser = subparsers.add_parser("classify", help="分类图片文件夹")
    sub_parser.add_argument("-p", "--path", type=str, required=True, help="目标路径")
    sub_parser.add_argument("-remove", action="store_true", help="删除已存在的分类")

    # ===== deduplicate  =====
    sub_parser = subparsers.add_parser("deduplicate", help="去重图片文件夹")
    sub_parser.add_argument("-p", "--path", type=str, required=True, help="目标路径")

    args = parser.parse_args()

    # === 命令分发 ===
    if args.command == "unrar":
        from extract import batch_extract

        password = args.password  # 可以是空，默认值在 extract.py 中
        batch_extract(Path(args.path).resolve(), password)

    elif args.command == "server":
        from server import start_server

        start_server()

    elif args.command == "cat":
        from cat_vids import cat_dirs

        cat_dirs(Path(args.path).resolve())

    elif args.command == "flat":
        from utils import flat_dir

        flat_dir(Path(args.path).resolve())

    elif args.command == "thumb":
        from thumb import thumb_vid_dir, thumb_pics_dirs
        from utils import remove_existing_pics_thumb, remove_existing_vids_thumb

        path = Path(args.path).resolve()
        if args.remove:
            remove_existing_vids_thumb(path)
            remove_existing_pics_thumb(path)
        if args.vid:
            thumb_vid_dir(path)
        if args.pic:
            thumb_pics_dirs(path)
        if not (args.remove or args.pic or args.vid):
            remove_existing_vids_thumb(path)
            remove_existing_pics_thumb(path)
            thumb_vid_dir(path)
            thumb_pics_dirs(path)

    elif args.command == "convert":
        from convert import convert_dir

        convert_dir(Path(args.path).resolve())

    elif args.command == "backup":
        from OSS import backup_dir

        backup_dir(Path(args.path).resolve())

    elif args.command == "classify":
        from classifier import Classifier

        Classifier().classifier_pics_dirs(Path(args.path).resolve(), args.remove)

    elif args.command == "deduplicate":
        from deduplicate import find_similar_images

        find_similar_images(Path(args.path).resolve())


if __name__ == "__main__":
    main()
