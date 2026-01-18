import os
import json
import asyncio
import logging
from datetime import datetime

from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from dotenv import load_dotenv

from medi_tg_analytics.core.settings import settings

# ------------------------------------------------------------------
# Environment & Paths
# ------------------------------------------------------------------
load_dotenv()

DATA_RAW = settings.paths.DATA["raw_dir"]
MESSAGES_DIR = DATA_RAW / "telegram_messages"
IMAGES_DIR = DATA_RAW / "images"
LOG_DIR = settings.paths.LOGS["scraping_logs_dir"]
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
logging.basicConfig(
    filename=LOG_DIR / "scraper.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def today_partition() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")


def safe_channel_name(name: str) -> str:
    return name.replace("@", "").lower()


# ------------------------------------------------------------------
# Core scraper
# ------------------------------------------------------------------
async def scrape_channel(client: TelegramClient, channel: str, max_messages=None):
    channel_name = safe_channel_name(channel)
    date_partition = today_partition()

    messages_path = MESSAGES_DIR / date_partition
    images_path = IMAGES_DIR / channel_name
    messages_path.mkdir(parents=True, exist_ok=True)
    images_path.mkdir(parents=True, exist_ok=True)

    output_file = messages_path / f"{channel_name}.json"
    temp_file = output_file.with_suffix(".tmp")

    results = []
    processed = 0

    logger.info(f"Starting scrape for channel: {channel_name}")

    try:
        async for message in client.iter_messages(channel, limit=max_messages):
            if not message.text and not message.media:
                continue

            record = {
                "message_id": message.id,
                "channel_name": channel_name,
                "message_date": message.date.isoformat() if message.date else None,
                "message_text": message.text,
                "views": message.views or 0,
                "forwards": message.forwards or 0,
                "has_media": bool(message.media),
                "image_path": None,
            }

            if isinstance(message.media, MessageMediaPhoto):
                image_file = images_path / f"{message.id}.jpg"
                try:
                    await client.download_media(message.photo, image_file)
                    record["image_path"] = str(image_file)
                except Exception as e:
                    logger.warning(f"Failed to download image {message.id}: {e}")

            results.append(record)
            processed += 1

    except Exception as exc:
        logger.exception(f"Failed scraping {channel_name}: {exc}")
        return

    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        temp_file.replace(output_file)
        logger.info(f"Completed channel {channel_name} | messages saved: {processed}")
    except Exception as exc:
        logger.exception(f"Failed writing JSON for {channel_name}: {exc}")


# ------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------
async def main():
    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH")

    if not api_id or not api_hash:
        logger.error("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env")
        return

    # Load channels and limits from YAML via settings.get(...)
    telegram_cfg = settings.get("telegram", {})
    channels = telegram_cfg.get("channels", [])
    limits = settings.get("limits", {})
    max_messages = limits.get("max_messages_per_channel")

    async with TelegramClient("telegram_session", api_id, api_hash) as client:
        for channel in channels:
            await scrape_channel(client, channel, max_messages)
            await asyncio.sleep(1)  # rate-limit friendly


if __name__ == "__main__":
    asyncio.run(main())
