"""Load page of URL, accept all cookies and take a screenshot"""

import logging
import logging.handlers
import os
from datetime import datetime, timezone
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
    dst.mkdir(exist_ok=True)
    url = "https://www.google.com/maps/@50.9503538,4.7123571,734m/data=!5m1!1e1"
    with sync_playwright() as p:
        browser_type = p.chromium
        browser = browser_type.launch()
        page = browser.new_page()
        page.goto(url)
        for i, el in enumerate(page.get_by_label("Accept all").all()):
            try:
                el.click()
            except Exception as e:
                logging.debug(f"Clicked {i}th element: {str(e)}")
        page.wait_for_load_state("networkidle")
        now_utc = datetime.now(timezone.utc)
        timestr = now_utc.strftime("%Y%m%d-%H%M%S")
        shot_file = dst / f"rotselaar_{timestr}.png"
        page.screenshot(path=shot_file.as_posix())
        logger.info(f"Took shot {shot_file.as_posix()} on {timestr}.")
        browser.close()
