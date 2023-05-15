"""Load page of URL, accept all cookies and take a screenshot"""

import logging
import logging.handlers
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger_file_handler = logging.handlers.RotatingFileHandler(
        "status.log",
        maxBytes=1024 * 1024,
        backupCount=1,
        encoding="utf8",
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger_file_handler.setFormatter(formatter)
    logger.addHandler(logger_file_handler)

    dst = Path("./shots")  # Directory to store resulting png in.
    url = "https://www.google.com/maps/@50.9503538,4.7123571,734m/data=!3m1!1e3!5m1!1e1"
    with sync_playwright() as p:
        browser_type = p.chromium
        browser = browser_type.launch()
        page = browser.new_page()
        page.goto(url)
        page.get_by_label("Alles accepteren").all()[0].click()
        page.wait_for_load_state("networkidle")
        timestr = time.strftime("%Y%m%d-%H%M%S")
        shot_file = dst / f"rotselaar_{timestr}.png"
        page.screenshot(path=shot_file.as_posix())
        logger.info(f"Took shot {shot_file.as_posix()} on {timestr}.")
        browser.close()
