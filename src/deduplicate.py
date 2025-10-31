from tqdm import tqdm
from pathlib import Path
import os
from PIL import Image
import imagehash
from send2trash import send2trash
from itertools import combinations
from logger import get_logger

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
HASH_FUNC = imagehash.phash  # 可选 ahash, dhash, whash, phash
SIMILARITY_THRESHOLD = 10  # 汉明距离阈值，小于等于此值即认为相似
logger = get_logger("cat_vids", level="DEBUG")


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        if self.parent.get(x, x) != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent.get(x, x)

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def find_images(root: Path):
    for dirpath, _, files in os.walk(root):
        for f in files:
            if os.path.splitext(f)[1].lower() in IMG_EXT:
                yield os.path.join(dirpath, f)


def find_duplicates_all_same(root: Path):
    hash_map = {}
    for path in tqdm(list(find_images(root))):
        try:
            h = imagehash.phash(Image.open(path))
            hash_map.setdefault(str(h), []).append(path)
        except Exception:
            pass

    for h, files in hash_map.items():
        if len(files) > 1:
            logger.info(f"\nPotential duplicates (hash={h}):")
            for f in files:
                logger.info("  ", f)


def get_size(path):
    try:
        return os.path.getsize(path)
    except:
        return 0


def find_similar_images(root: Path):
    logger.info(f"Scanning directory: {root}")
    hash_map = {}

    for path in tqdm(list(find_images(root))):
        try:
            with Image.open(path) as img:
                img_hash = HASH_FUNC(img)
            hash_map[path] = img_hash
        except Exception as e:
            logger.info(f"Error processing {path}: {e}")

    logger.info("\nComparing images for similarity...")
    paths = list(hash_map.keys())

    # ==== 2️⃣ 并查集合并 ====
    logger.info("\nClustering similar images...")
    uf = UnionFind()

    for a, b in tqdm(list(combinations(paths, 2))):
        try:
            dist = hash_map[a] - hash_map[b]
            if dist <= SIMILARITY_THRESHOLD:
                uf.union(a, b)
        except Exception:
            continue

    clusters = {}
    for path in paths:
        root = uf.find(path)
        clusters.setdefault(root, []).append(path)

    logger.info("\n📸 Visual duplicate clusters:\n")
    for i, (root, group) in enumerate(clusters.items(), 1):
        if len(group) == 1:
            continue
        group.sort(key=get_size, reverse=True)
        master = group[0]
        logger.info(f"== Group {i} ==")
        logger.info(f"  📂 Source: {master}  ({get_size(master)/1024:.1f} KB)")
        for dup in group[1:]:
            dist = hash_map[master] - hash_map[dup]
            logger.info(
                f"   ↳ {dup}  [Δ={dist}]  ({get_size(dup)/1024:.1f} KB), moving to trash..."
            )
            send2trash(dup)
        logger.info()

    logger.info("✅ Done.")
