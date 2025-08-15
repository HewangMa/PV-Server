from utils import IMAGES
import requests
from pathlib import Path
from logger import get_logger
import os
from PIL import Image, ImageDraw, ImageFont
import re

logger = get_logger("classifier", level="DEBUG")
PREFIX_PATTERN = re.compile(r"^[abc]_")
PROJECT_DIR = Path(os.path.dirname(__file__)).parent
RESOURCE_DIR = PROJECT_DIR / "resource"
API_URL_SINGLE = "http://localhost:3000/classify"
API_URL_BATCH = "http://localhost:3000/classify-many"
CLASS_NAMES = ["drawing", "neutral", "sexy", "hentai", "porn"]
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # 确保字体存在
FONT_SIZE = 64


def annotate_image(image_path: Path, probs: dict, save_path: Path):
    """在图片左上角写上分类概率，并保存到 save_path"""
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except OSError:
        font = ImageFont.load_default()

    x, y, black_width = 5, 5, 1
    for label, score in probs.items():
        text = f"{label}: {score:.4f}"
        draw.text((x - black_width, y - black_width), text, font=font, fill="black")
        draw.text((x + black_width, y - black_width), text, font=font, fill="black")
        draw.text((x - black_width, y + black_width), text, font=font, fill="black")
        draw.text((x + black_width, y + black_width), text, font=font, fill="black")
        draw.text((x, y), text, font=font, fill="white")
        y += FONT_SIZE + 4

    img.save(save_path)


def classify_multi_images(images: list[Path]):
    """批量分类图片，返回每张图片的(分类结果, 概率字典)"""
    if len(images) > 10:
        raise ValueError(f"classify_multi_images with 10 images at most!")
    files = [("images", open(img, "rb")) for img in images]
    try:
        resp = requests.post(API_URL_BATCH, files=files)
        resp.raise_for_status()
        results = resp.json()
    finally:
        for _, f in files:
            f.close()

    classifications = []
    for img, probs in zip(images, results):
        category = judge(probs)
        classifications.append((img, category, probs))
    return classifications


def judge(probs: dict) -> str:
    if probs["neutral"] > 0.98:
        return "a"
    if probs["sexy"] + probs["porn"] > 0.98:
        return "b"
    return "c"


def clean_prefixes(images: list[Path]) -> list[Path]:
    """去掉文件名前的 a_ / b_ / c_ 前缀，返回清理后的文件列表"""
    cleaned_images = []
    for img in images:
        if PREFIX_PATTERN.match(img.name):
            new_name = PREFIX_PATTERN.sub("", img.name)
            new_path = img.with_name(new_name)
            if not new_path.exists():
                img.rename(new_path)
                cleaned_images.append(new_path)
            else:
                logger.warning(f"Cannot remove prefix, target exists: {new_path}")
                cleaned_images.append(img)  # 保留原路径
        else:
            cleaned_images.append(img)
    return cleaned_images


def classify_rename_images(input_dir: Path):
    """按 judge 结果给文件名前加标签前缀（自动清理旧前缀）"""
    images = [
        p
        for p in input_dir.iterdir()
        if p.is_file()
        and p.suffix.lower() in IMAGES
        and not p.name.startswith(("a_", "b_", "c_"))
    ]
    if not images:
        logger.warning(f"No images found in {input_dir}")
        return
    # images = clean_prefixes(images)

    def batcher(images, batch_size=10):
        for i in range(0, len(images), batch_size):
            yield images[i : i + batch_size]

    for batch in batcher(images):
        try:
            # 返回 (img, category, probs)
            classifications = classify_multi_images(batch)
        except Exception as e:
            logger.error(f"Failed to classify batch: {e}")
            continue

        for img, _, probs in classifications:
            label = judge(probs)
            new_name = f"{label}_{img.name}"
            new_path = img.with_name(new_name)

            if not new_path.exists():
                img.rename(new_path)
            else:
                logger.warning(f"Target file exists, skipped: {new_path}")
    logger.info(f"Classify and rename completed for {input_dir}")


def classifier_pics_dirs(path: Path):
    if test_api():
        for root, dirs, _ in os.walk(path):
            path = Path(root)
            if len(dirs) == 0 and "temp" not in path.parts:
                classify_rename_images(path)


def test_api():
    image_path = Path("/home/hewangma/projects/PV-Server/docs/c_IMG_2143.JPG")
    try:
        with open(image_path, "rb") as f:
            file = {"image": f}
        resp = requests.post(API_URL_SINGLE, files=file)
        resp.raise_for_status()
        # resp = requests.post(API_URL_BATCH, files=[file])
        # resp.raise_for_status()
        return True
    except Exception as e:
        logger.info(f"API may be not working: {e}")
        return False


if __name__ == "__main__":
    logger.info(test_api())
