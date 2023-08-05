"""Prep utils and data."""
# pylint: disable=invalid-name
from pathlib import Path

from logzero import logger

data_dir = Path(__file__).with_name("data")
try:
    text1 = Path(data_dir, "test-en.txt").read_text(encoding="utf8")
except Exception as exc:
    logger.error("rea text1 error: %s, setting to ''", exc)
    text1 = ""
try:
    text2 = Path(data_dir, "test-zh.txt").read_text(encoding="utf8")
except Exception as exc:
    logger.error("read text2 error: %s, setting to ''", exc)
    text2 = ""
