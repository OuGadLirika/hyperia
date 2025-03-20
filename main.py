import json
import time
import re
import logging
from datetime import datetime
from typing import List, Tuple, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

print("\n████████████████████████████████████████████████████████████████████\n█▄─▄▄▀█─▄▄─█▄─▀█▀─▄██▀▄─██▄─▀█▄─▄███▄─▄▄─█▄─▄▄─█▄─▀█▄─▄█▄─▄▄─█▄─█─▄█\n██─▄─▄█─██─██─█▄█─███─▀─███─█▄▀─█████─▄████─▄█▀██─█▄▀─███─▄█▀██▄▀▄██\n▀▄▄▀▄▄▀▄▄▄▄▀▄▄▄▀▄▄▄▀▄▄▀▄▄▀▄▄▄▀▀▄▄▀▀▀▄▄▄▀▀▀▄▄▄▄▄▀▄▄▄▀▀▄▄▀▄▄▄▄▄▀▀▀▄▀▀▀")
# Настройка логгера
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class BrowserDriver:
    def __init__(self, headless: bool = True):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def fetch_page(self, url: str) -> Optional[str]:
        try:
            logging.info(f"page: {url}")
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "grid-item"))
            )
            return self.driver.page_source
        except Exception as e:
            logging.error(f"error {url}: {e}")
            return None

    def close(self):
        self.driver.quit()


class CategoryParser:
    BASE_URL = "https://www.prospektmaschine.de"

    @staticmethod
    def get_category_links(html: str) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        categories = []
        category_list = soup.select('#left-category-shops li a')

        for category in category_list:
            link = category.get('href')
            if link:
                categories.append(CategoryParser.BASE_URL + link)

        logging.info(f"find {len(categories)} categories")
        return categories


class ProspektParser:

    @staticmethod
    def parse_prospekts(html: str) -> List[dict]:
        soup = BeautifulSoup(html, 'html.parser')
        prospekts = []

        items = soup.find_all('div', class_='grid-item box blue')[:2]  # Ограничение на 2 элемента

        for item in items:
            try:
                title_element = item.select_one('p.grid-item-content strong')
                title = title_element.text.strip() if title_element else "No Title"

                thumbnail_element = item.select_one('img')
                thumbnail = thumbnail_element['src'] if thumbnail_element and 'src' in thumbnail_element.attrs else "No Thumbnail"

                shop_url = item.select_one('a')['href'] if item.select_one('a') else ""
                shop_name = shop_url.split('/')[1].capitalize() if shop_url else "Unknown Shop"

                date_element = item.select_one('small.hidden-sm') or item.select_one('small.visible-sm')
                date_text = date_element.text.strip() if date_element else "Unknown Dates"

                valid_from, valid_to = ProspektParser.parse_dates(date_text)
                parsed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                prospekt = {
                    "title": title,
                    "thumbnail": thumbnail,
                    "shop_name": shop_name,
                    "valid_from": valid_from,
                    "valid_to": valid_to,
                    "parsed_time": parsed_time
                }

                prospekts.append(prospekt)
            except Exception as e:
                logging.warning(f"warning: {e}")
                continue

        logging.info(f"find {len(prospekts)} prospekts.")
        return prospekts

    @staticmethod
    def parse_dates(date_text: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            date_text = date_text.replace("von", "").replace("bis", "").strip()

            match_full = re.match(r"(\d{2}\.\d{2}\.\d{4}) - (\d{2}\.\d{2}\.\d{4})", date_text)
            if match_full:
                valid_from = datetime.strptime(match_full.group(1), "%d.%m.%Y").strftime("%Y-%m-%d")
                valid_to = datetime.strptime(match_full.group(2), "%d.%m.%Y").strftime("%Y-%m-%d")
                return valid_from, valid_to

            match_short = re.match(r"(\d{2}\.\d{2}\.) - (\d{2}\.\d{2}\.\d{4})", date_text)
            if match_short:
                current_year = match_short.group(2).split(".")[-1]
                valid_from = datetime.strptime(match_short.group(1) + current_year, "%d.%m.%Y").strftime("%Y-%m-%d")
                valid_to = datetime.strptime(match_short.group(2), "%d.%m.%Y").strftime("%Y-%m-%d")
                return valid_from, valid_to

            logging.warning(f"warning: {date_text}")
            return None, None
        except Exception as e:
            logging.error(f"error: {e}")
            return None, None


class FileStorage:
    
    @staticmethod
    def save_to_json(data: List[dict], filename: str = "prospekts.json") -> None:
        try:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            logging.info(f"save into {filename}")
        except Exception as e:
            logging.error(f"error save JSON: {e}")


class ProspektScraper:
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.driver = BrowserDriver()

    def run(self):
        main_html = self.driver.fetch_page(self.base_url)
        if not main_html:
            logging.error("error page")
            return

        category_links = CategoryParser.get_category_links(main_html)

        all_prospekts = []
        for link in category_links:
            category_html = self.driver.fetch_page(link)
            if category_html:
                prospekts = ProspektParser.parse_prospekts(category_html)
                all_prospekts.extend(prospekts)
            time.sleep(1)

        FileStorage.save_to_json(all_prospekts)
        self.driver.close()


if __name__ == "__main__":
    scraper = ProspektScraper("https://www.prospektmaschine.de/hypermarkte/")
    scraper.run()
