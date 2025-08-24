import os
import re
import requests
from tqdm import tqdm
from utils import IMAGES
from pathlib import Path
from logger import get_logger
from PIL import Image, ImageDraw, ImageFont

logger = get_logger("classifier", level="DEBUG")

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
    """批量分类图片，单张跳过"""
    if len(images) > 10:
        raise ValueError(f"classify_multi_images with 10 images at most!")

    valid_files = []
    for img in images:
        try:
            f = open(img, "rb")
            valid_files.append(("images", f))
        except Exception as e:
            logger.warning(f"Jump {img}: {e}")

    if not valid_files:
        logger.warning("No valid images to classify in this batch.")
        return []

    try:
        resp = requests.post(API_URL_BATCH, files=valid_files)
        resp.raise_for_status()
        results = resp.json()
    finally:
        for _, f in valid_files:
            f.close()

    classifications = []
    for img, probs in zip([Path(f[1].name) for f in valid_files], results):
        category = judge(probs)
        classifications.append((img, category, probs))
    return classifications


def judge(probs: dict) -> str:
    if probs["neutral"] > 0.99:
        return "a"
    if probs["sexy"] + probs["porn"] > 0.97:
        return "b"
    return "c"


def clean_prefixes(images: list[Path]) -> list[Path]:
    cleaned_images = []
    for img in images:
        new_name = re.sub(r"^(?:[abc]_)+", "", img.name)
        if new_name != img.name:  # 确认有修改
            new_path = img.with_name(new_name)
            if not new_path.exists():
                img.rename(new_path)
                cleaned_images.append(new_path)
            else:
                raise ValueError(f"Could this file exists? {new_path}")
        else:
            cleaned_images.append(img)

    return cleaned_images


def classify_rename_images(input_dir: Path, re_classify: bool = False):
    """按 judge 结果给文件名前加标签前缀"""
    images = [
        p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGES
    ]
    if re_classify:
        images = clean_prefixes(images)
    images = [p for p in images if not p.name.startswith(("a_", "b_", "c_"))]

    if not images:
        logger.warning(f"No images found in {input_dir}")
        return

    def batcher(images, batch_size=10):
        for i in range(0, len(images), batch_size):
            yield images[i : i + batch_size]

    with tqdm(
        total=len(images),
        desc=f"Classifying {input_dir.relative_to(RESOURCE_DIR)}",
        unit="img",
    ) as pbar:
        for batch in batcher(images):
            pbar.update(len(batch))
            try:
                classifications = classify_multi_images(batch)
            except requests.exceptions.ConnectionError as e:
                logger.critical(
                    "NSFW API service is not reachable. Stopping all classification."
                )
                exit()
            except Exception as e:
                logger.error(f"Other error, skipped batch: {e}")
                continue

            for img, _, probs in classifications:
                label = judge(probs)
                new_name = f"{label}_{img.name}"
                new_path = img.with_name(new_name)

                if not new_path.exists():
                    img.rename(new_path)
                else:
                    logger.warning(f"Target file exists, skipped: {new_path}")


def classifier_pics_dirs(path: Path, re_classify: bool = False):
    if test_api():
        for root, dirs, _ in os.walk(path):
            path = Path(root)
            if len(dirs) == 0 and "temp" not in path.parts:
                classify_rename_images(path, re_classify)


def test_api():
    one = Path("/home/hewangma/projects/PV-Server/docs/1.png")
    two = Path("/home/hewangma/projects/PV-Server/docs/22.png")
    try:
        with open(one, "rb") as f:
            file = {"image": f}
            resp = requests.post(API_URL_SINGLE, files=file)
            resp.raise_for_status()
            logger.info(f"Single OK")

    except Exception as e:
        logger.info(f"API may be not working: {e}")
        return False

    try:
        _ = classify_multi_images([one, two])
        logger.info(f"Multi OK")
    except Exception as e:
        logger.info(f"API may be not working: {e}")
        return False
    return True
