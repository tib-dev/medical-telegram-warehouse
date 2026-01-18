import json
import pytest
from pathlib import Path
from datetime import datetime

from medi_tg_analytics.scraping.scraper import (
    safe_channel_name,
    today_partition,
    scrape_channel,
)

# --------------------------------------------------
# Unit tests: helpers
# --------------------------------------------------


def test_safe_channel_name():
    assert safe_channel_name("@TikvahPharma") == "tikvahpharma"
    assert safe_channel_name("lobelia4cosmetics") == "lobelia4cosmetics"


def test_today_partition_format():
    date_str = today_partition()
    # YYYY-MM-DD
    datetime.strptime(date_str, "%Y-%m-%d")


# --------------------------------------------------
# Mocks
# --------------------------------------------------

class MockMessage:
    def __init__(
        self,
        message_id=1,
        text="test message",
        views=10,
        forwards=2,
        date=None,
        media=None,
    ):
        self.id = message_id
        self.text = text
        self.views = views
        self.forwards = forwards
        self.date = date or datetime.utcnow()
        self.media = media
        self.photo = None


class MockTelegramClient:
    def __init__(self, messages):
        self._messages = messages

    async def iter_messages(self, channel, limit=None):
        for msg in self._messages[:limit]:
            yield msg

    async def download_media(self, photo, file):
        # simulate image download
        Path(file).write_bytes(b"fake image bytes")


# --------------------------------------------------
# Integration-style async test (no real Telegram)
# --------------------------------------------------

@pytest.mark.asyncio
async def test_scrape_channel_writes_json(tmp_path, monkeypatch):
    """
    Verifies:
    - JSON file is written
    - Message fields are correctly serialized
    - Directory structure is created
    """

    # Arrange: mock paths from settings
    data_raw = tmp_path / "data" / "raw"
    messages_dir = data_raw / "telegram_messages"
    images_dir = data_raw / "images"
    logs_dir = tmp_path / "logs"

    monkeypatch.setattr(
        "medi_tg_analytics.scraping.scraper.MESSAGES_DIR", messages_dir
    )
    monkeypatch.setattr(
        "medi_tg_analytics.scraping.scraper.IMAGES_DIR", images_dir
    )
    monkeypatch.setattr(
        "medi_tg_analytics.scraping.scraper.LOG_DIR", logs_dir
    )

    # Mock messages
    messages = [
        MockMessage(message_id=1, text="hello"),
        MockMessage(message_id=2, text="world"),
    ]

    client = MockTelegramClient(messages)

    # Act
    await scrape_channel(
        client=client,
        channel="@TestChannel",
        max_messages=10,
    )

    # Assert
    date_partition = today_partition()
    output_file = (
        messages_dir / date_partition / "testchannel.json"
    )

    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 2
    assert data[0]["message_text"] == "hello"
    assert data[1]["views"] == 10
    assert data[0]["channel_name"] == "testchannel"
