# hyperia

![Picture](https://github.com/OuGadLirika/hyperia/blob/main/pic.png)


# Prospekt Scraper

## English

### 📌 Description
**Prospekt Scraper** is a Python-based web scraper that extracts promotional flyers from [prospektmaschine.de](https://www.prospektmaschine.de). It uses **Selenium** and **BeautifulSoup** to dynamically load and parse data, saving the results in JSON format.

### ⚙️ Features
- Scrapes **only the first two promotional flyers** from each supermarket category.
- Uses **Selenium WebDriver** to wait for page load and handle dynamic content.
- Saves extracted data in a structured **JSON format**.
- Runs in **headless mode** for efficiency.

### 📦 Requirements
- Python 3.7+
- Google Chrome
- ChromeDriver
- Required libraries: `selenium`, `webdriver-manager`, `beautifulsoup4`, `requests`

### 🔧 Installation
```bash
pip install -r requirements.txt
```

### 🚀 Usage
```bash
python main.py
```

### 📝 Output
The script will save the scraped data to `prospekts.json`.

---

### 📌 Popis
**Prospekt Scraper** je Python web scraper, ktorý extrahuje reklamné letáky zo stránky [prospektmaschine.de](https://www.prospektmaschine.de). Používa **Selenium** a **BeautifulSoup** na dynamické načítanie a analýzu dát, pričom výsledky sa ukladajú vo formáte JSON.

### ⚙️ Funkcie
- Stiahne **iba prvé dva letáky** z každej kategórie supermarketov.
- Používa **Selenium WebDriver** na čakanie na načítanie stránky a spracovanie dynamického obsahu.
- Uloží extrahované údaje vo **formáte JSON**.
- Beží v **headless režime** pre efektivitu.

### 📦 Požiadavky
- Python 3.7+
- Google Chrome
- ChromeDriver
- Potrebné knižnice: `selenium`, `webdriver-manager`, `beautifulsoup4`, `requests`

### 🔧 Inštalácia
```bash
pip install -r requirements.txt
```

### 🚀 Použitie
```bash
python main.py
```

### 📝 Výstup
Skript uloží získané dáta do súboru `prospekts.json`.