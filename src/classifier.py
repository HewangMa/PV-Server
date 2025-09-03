import os
import re
import requests
from tqdm import tqdm
from utils import IMAGES
from pathlib import Path
from logger import get_logger
from PIL import Image, ImageDraw, ImageFont
from enum import Enum

logger = get_logger("classifier", level="DEBUG")

PROJECT_DIR = Path(os.path.dirname(__file__)).parent
RESOURCE_DIR = PROJECT_DIR / "resource"

API_URL_SINGLE = "http://localhost:3000/classify"
API_URL_BATCH = "http://localhost:3000/classify-many"

CLASS_NAMES = ["drawing", "neutral", "sexy", "hentai", "porn"]

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # 确保字体存在
FONT_SIZE = 64


class Tag(Enum):
    FIRST = "a"
    SECOND = "b"
    THIRD = "c"


class Classifier:
    pattern = rf"^(?:{'|'.join(re.escape(tag.value+'_') for tag in Tag)})+"

    def classify_multi_images(self, images: list[Path]):
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

        probs = []
        for img, prob in zip([Path(f[1].name) for f in valid_files], results):
            probs.append((img, prob))
        return probs

    def classify_img_path(self, input_dir: Path, re_classify: bool = False):
        """按 judge 结果给文件名前加标签前缀"""
        if re_classify:
            for f in input_dir.iterdir():
                if f.is_file() and f.suffix.lower() in IMAGES:
                    self.untag_img(f)
        images = [
            p
            for p in images
            if not re.match(self.pattern, p.name) and p.suffix.lower() in IMAGES
        ]

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
                    probs = self.classify_multi_images(batch)
                except requests.exceptions.ConnectionError as e:
                    logger.critical(
                        "NSFW API service is not reachable. Stopping all classification."
                    )
                    exit()
                except Exception as e:
                    logger.error(f"Other error, skipped batch: {e}")
                    continue

                for img, prob in probs:
                    self.tag_img(img, self.judge(prob))

    def classifier_pics_dirs(self, path: Path, re_classify: bool = False):
        if self.classify_api_ok():
            for root, dirs, _ in os.walk(path):
                path = Path(root)
                if len(dirs) == 0 and "temp" not in path.parts:
                    self.classify_img_path(path, re_classify)

    def tag_img(self, img, tag):
        if not img.exists() or not img.is_file() or not img.suffix.lower() in IMAGES:
            logger.warning(f"Invalid image to tag: {img}")
            return
        new_path = img.with_name(f"{tag}_{img.name}")
        if not new_path.exists():
            img.rename(new_path)
        else:
            logger.warning(f"Target file exists, skipped: {new_path}")

    def untag_img(self, img: Path) -> Path:
        if not img.exists() or not img.is_file() or not img.suffix.lower() in IMAGES:
            logger.warning(f"Invalid image to untag: {img}")
            return img
        new_name = re.sub(self.pattern, "", img.name)
        if new_name != img.name:
            new_path = img.with_name(new_name)
            if not new_path.exists():
                img.rename(new_path)
                return new_path
            else:
                logger.warning(f"Two file same-named exists? {new_path} and {img}")
        return img

    def judge(self, probs: dict) -> Tag:
        if probs["neutral"] > 0.99:
            return Tag.FIRST
        if probs["sexy"] + probs["porn"] > 0.97:
            return Tag.SECOND
        return Tag.THIRD

    def classify_api_ok(self):
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

    def annotate_image(self, image_path: Path, probs: dict, save_path: Path):
        if save_path == image_path:
            raise ValueError(
                "save_path should be different from image_path to avoid overwrite"
            )
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
