"""Load page of URL, accept all cookies and take a screenshot"""

import logging
import logging.handlers
from datetime import datetime, timezone

from zoneinfo import ZoneInfo
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

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

    dst = Path("./shots")  # Directory to store resulting png images in.
    dst.mkdir(exist_ok=True)
    # url = "https://www.google.com/maps/@50.9503538,4.7123571,734m/data=!5m1!1e1"
    URL_GELDENAAKSEPOORT = (
        "https://www.google.com/maps/@50.8724828,4.7123349,17.97z/data=!5m1!1e1"
    )
    URL_TIENSEVEST = (
        "https://www.google.com/maps/@50.8747536,4.713817,17.97z/data=!5m1!1e1"
    )
    URL_TIENSESTEENWEG = (
        "https://www.google.com/maps/@50.8730661,4.7186021,18z/data=!5m1!1e1?e"
    )
    URL_TIENSESTRAAT = (
        "https://www.google.com/maps/@50.8748008,4.7106216,17z/data=!5m1!1e1?entry=ttu"
    )

    URLS = [URL_GELDENAAKSEPOORT, URL_TIENSEVEST, URL_TIENSESTEENWEG, URL_TIENSESTRAAT]
    STREETNAMES = ["geldenaaksepoort", "tiensevest", "tiensesteenweg", "tiensestraat"]

    with sync_playwright() as p:
        browser_type = p.chromium
        browser = browser_type.launch(headless=True)
        context = browser.new_context(locale="en-US")
        page = context.new_page()
        page.goto(URLS[0])
        # for i, el in enumerate(page.get_by_label("Accept all").all()):
        for i, el in enumerate(page.get_by_label("Alles accepteren").all()):
            try:
                el.click()
            except Exception as e:
                logging.debug(f"Clicked {i}th element: {str(e)}")
        page.wait_for_load_state("networkidle")
        while True:
            for url, streetname in zip(URLS, STREETNAMES):
                page.goto(url)
                page.wait_for_load_state("networkidle")
                now_utc = datetime.now(timezone.utc)
                now_local = now_utc.astimezone(ZoneInfo("Europe/Brussels"))
                timestr = now_local.strftime("%Y%m%d-%H%M%S")
                shot_file = dst / f"leuven_{streetname}_{timestr}.png"
                page.screenshot(path=shot_file.as_posix())
                logger.info(f"Took shot {shot_file.as_posix()} on {timestr}.")
            time.sleep(300)
        context.close()
        browser.close()
