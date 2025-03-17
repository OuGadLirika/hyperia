import json
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


service = Service("/usr/local/bin/chromedriver")
class ProspektScraper:
    BASE_URL = "https://www.prospektmaschine.de"
    TARGET_URL = "https://www.prospektmaschine.de/hypermarkte/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    def __init__(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Запуск без интерфейса
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Используем WebDriver Manager для автоматической установки драйвера
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def fetch_page(self, url):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "grid-item"))
            )  # Ждём появления элементов
            return self.driver.page_source
        except Exception as e:
            print(f"Error fetching page {url}: {e}")
            return None
    
    def get_category_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        categories = []
        category_list = soup.select('#left-category-shops li a')
        
        for category in category_list:
            link = category.get('href')
            if link:
                categories.append(self.BASE_URL + link)
        
        return categories
    
    def parse_prospekts(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        prospekts = []
        
        items = soup.find_all('div', class_='grid-item box blue')[:2]  # Берем только первые 2 элемента
        
        for item in items:
            try:
                # Название проспекта
                title_element = item.select_one('p.grid-item-content strong')
                title = title_element.text.strip() if title_element else "No Title"

                # Миниатюра
                thumbnail_element = item.select_one('img')
                thumbnail = thumbnail_element['src'] if thumbnail_element and 'src' in thumbnail_element.attrs else "No Thumbnail"

                # Название магазина (извлекаем из URL)
                shop_url = item.select_one('a')['href'] if item.select_one('a') else ""
                shop_name = shop_url.split('/')[1].capitalize() if shop_url else "Unknown Shop"

                # Дата действия проспекта
                date_element = item.select_one('small.hidden-sm') or item.select_one('small.visible-sm')
                date_text = date_element.text.strip() if date_element else "Unknown Dates"

                valid_from, valid_to = self.parse_dates(date_text)
                parsed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Создание объекта проспекта
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
                print(f"Skipping an entry due to error: {e}")
                continue

        return prospekts
    
    def parse_dates(self, date_text):
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
            
            print(f"Warning: Unrecognized date format: {date_text}")
            return None, None
        except Exception as e:
            print(f"Error parsing dates: {e}")
            return None, None
    
    def save_to_json(self, data, filename="prospekts.json"):
        try:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            print(f"Data successfully saved to {filename}")
        except Exception as e:
            print(f"Error saving JSON: {e}")
    
    def run(self):
        print("Fetching main category page...")
        main_html = self.fetch_page(self.TARGET_URL)
        if not main_html:
            print("Failed to retrieve main page.")
            return
        
        category_links = self.get_category_links(main_html)
        print(f"Found {len(category_links)} categories to scrape.")
        
        all_prospekts = []
        for link in category_links:
            print(f"Fetching category page: {link}")
            category_html = self.fetch_page(link)
            if category_html:
                prospekts = self.parse_prospekts(category_html)
                all_prospekts.extend(prospekts)
            time.sleep(1)  # Avoid too many requests in a short time
        
        print(f"Found total {len(all_prospekts)} prospekts.")
        self.save_to_json(all_prospekts)
        self.driver.quit()  # Закрытие Selenium WebDriver

if __name__ == "__main__":
    scraper = ProspektScraper()
    scraper.run()
