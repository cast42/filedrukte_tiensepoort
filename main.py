"""Load page of URL, accept all cookies and take a screenshot"""

import logging
import logging.handlers
from datetime import datetime, timezone

from zoneinfo import ZoneInfo
from pathlib import Path
from playwright.sync_api import sync_playwright
import time
from traffic_analysis import (
    load_config,
)

RUN_LOCAL = False  # Set to True when run locally
CONFIG_FILE = "config.toml"
assert Path(CONFIG_FILE).exists()

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

    config = load_config(CONFIG_FILE)

    dst = Path("./shots")  # Directory to store resulting png images in.
    dst.mkdir(exist_ok=True)

    urls = []
    for location_i in config.keys():
        for street_i in config[location_i].keys():
            urls.append(config[location_i][street_i]["url"])
    streetnames = []
    for location_i in config.keys():
        for street_i in config[location_i].keys():
            streetnames.append(street_i)

    with sync_playwright() as p:
        browser_type = p.chromium
        browser = browser_type.launch(headless=True)
        context = browser.new_context(locale="en-US")
        page = context.new_page()
        page.goto(urls[0])
        # for i, el in enumerate(page.get_by_label("Accept all").all()):
        for i, el in enumerate(page.get_by_label("Alles accepteren").all()):
            try:
                el.click()
            except Exception as e:
                logging.debug(f"Clicked {i}th element: {str(e)}")
        page.wait_for_load_state("networkidle")
        if RUN_LOCAL:
            while True:
                for url, streetname in zip(urls, streetnames):
                    page.goto(url)
                    page.wait_for_load_state("networkidle")
                    now_utc = datetime.now(timezone.utc)
                    now_local = now_utc.astimezone(ZoneInfo("Europe/Brussels"))
                    timestr = now_local.strftime("%Y%m%d-%H%M%S")
                    shot_file = dst / f"leuven_{streetname}_{timestr}.png"
                    page.screenshot(path=shot_file.as_posix())
                    logger.info(f"Took shot {shot_file.as_posix()} on {timestr}.")
                time.sleep(300)
        else:
            for url, streetname in zip(urls, streetnames):
                page.goto(url)
                page.wait_for_load_state("networkidle")
                now_utc = datetime.now(timezone.utc)
                now_local = now_utc.astimezone(ZoneInfo("Europe/Brussels"))
                timestr = now_local.strftime("%Y%m%d-%H%M%S")
                shot_file = dst / f"leuven_{streetname}_{timestr}.png"
                page.screenshot(path=shot_file.as_posix())
                logger.info(f"Took shot {shot_file.as_posix()} on {timestr}.")
        context.close()
        browser.close()
