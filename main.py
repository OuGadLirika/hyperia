import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

class ProspektScraper:
    BASE_URL = "https://www.prospektmaschine.de"
    TARGET_URL = "https://www.prospektmaschine.de/hypermarkte/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        
    def fetch_page(self):
        try:
            response = self.session.get(self.TARGET_URL)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None
        
    def parse_prospekts(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        prospekts = []
        
        items = soup.find_all('div', class_='grid-item box blue')
        
        for item in items:
            try:
                title = item.find('p', class_='grid-item-content').text.strip()
                thumbnail = item.find('img').get('src')
                shop_name = item.find('div', class_='grid-logo').find('img').get('alt').replace('Logo ', '').strip()
                
                date_element = item.find('small', class_='hidden-sm')
                if not date_element:
                    date_element = item.find('small', class_='visible-sm')
                date_text = date_element.text.strip() if date_element else ""
                
                valid_from, valid_to = self.parse_dates(date_text)
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
            except AttributeError as e:
                print(f"Skipping an entry due to missing data: {e}")
                continue
        
        return prospekts
    
    @staticmethod
    def parse_dates(date_text):
        try:
            print(f"Parsing date: {date_text}")  # Отладочный вывод
            date_text = date_text.replace("von", "").replace("bis", "").strip()
            
            # Полный формат даты
            match_full = re.match(r"(\d{2}\.\d{2}\.\d{4}) - (\d{2}\.\d{2}\.\d{4})", date_text)
            if match_full:
                valid_from = datetime.strptime(match_full.group(1), "%d.%m.%Y").strftime("%Y-%m-%d")
                valid_to = datetime.strptime(match_full.group(2), "%d.%m.%Y").strftime("%Y-%m-%d")
                return valid_from, valid_to
            
            # Сокращённый формат даты (DD.MM. - DD.MM.YYYY)
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
        print("Fetching page...")
        html = self.fetch_page()
        if html:
            print("Parsing data...")
            prospekts = self.parse_prospekts(html)
            print(f"Found {len(prospekts)} prospekts.")
            self.save_to_json(prospekts)
        else:
            print("Failed to retrieve and parse data.")

if __name__ == "__main__":
    scraper = ProspektScraper()
    scraper.run()
