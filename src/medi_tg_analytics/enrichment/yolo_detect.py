import csv
import logging
from pathlib import Path
from typing import List, Dict

from ultralytics import YOLO

from medi_tg_analytics.core.settings import settings

# --------------------------------------------------
# Paths
# --------------------------------------------------

IMAGES_DIR = settings.paths.DATA["raw_dir"] / "images"
OUTPUT_DIR = settings.paths.DATA["interim_dir"]
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = OUTPUT_DIR / "yolo_image_detections.csv"

LOG_DIR = settings.paths.LOGS["enrichment_logs_dir"]
LOG_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    filename=LOG_DIR / "yolo_detect.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# YOLO setup
# --------------------------------------------------

MODEL_NAME = "yolov8n.pt"
model = YOLO(MODEL_NAME)

PERSON_CLASSES = {"person"}
PRODUCT_CLASSES = {"bottle", "cup", "bowl", "jar"}

# --------------------------------------------------
# Helpers
# --------------------------------------------------


def classify_image(detected_classes: List[str]) -> str:
    has_person = any(cls in PERSON_CLASSES for cls in detected_classes)
    has_product = any(cls in PRODUCT_CLASSES for cls in detected_classes)

    if has_person and has_product:
        return "promotional"
    if has_product and not has_person:
        return "product_display"
    if has_person and not has_product:
        return "lifestyle"
    return "other"


def scan_images() -> List[Path]:
    return list(IMAGES_DIR.rglob("*.jpg"))


# --------------------------------------------------
# Core enrichment
# --------------------------------------------------

def run_yolo_enrichment():
    logger.info("Starting YOLO image enrichment")

    rows: List[Dict] = []

    images = scan_images()
    logger.info("Found %d images", len(images))

    for image_path in images:
        try:
            results = model(image_path, verbose=False)[0]

            detected = []
            confidences = []

            for box in results.boxes:
                cls_id = int(box.cls[0])
                cls_name = model.names[cls_id]
                conf = float(box.conf[0])

                detected.append(cls_name)
                confidences.append(conf)

            image_category = classify_image(detected)

            message_id = image_path.stem
            channel_name = image_path.parent.name

            for cls, conf in zip(detected, confidences):
                rows.append(
                    {
                        "message_id": message_id,
                        "channel_name": channel_name,
                        "detected_class": cls,
                        "confidence_score": round(conf, 4),
                        "image_category": image_category,
                    }
                )

        except Exception as exc:
            logger.warning("Failed processing %s: %s", image_path, exc)

    write_csv(rows)
    logger.info("YOLO enrichment completed | rows: %d", len(rows))


def write_csv(rows: List[Dict]):
    if not rows:
        logger.warning("No detection results to write")
        return

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "message_id",
                "channel_name",
                "detected_class",
                "confidence_score",
                "image_category",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Saved YOLO results to %s", OUTPUT_CSV)


# --------------------------------------------------
# Entrypoint
# --------------------------------------------------

if __name__ == "__main__":
    run_yolo_enrichment()
