"""Utility helpers for logging and small helpers."""

import logging

logger = logging.getLogger('data_watchdog')
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def log(msg: str):
    logger.info(msg)
