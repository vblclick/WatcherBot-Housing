import requests
import json
import os
from bs4 import BeautifulSoup

# Configuración del bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URLS = [
    "https://www.pararius.com/apartments/arnhem/0-1200/radius-10",
    "https://www.pararius.com/apartments/wageningen/0-1200/radius-10",
    "https://www.pararius.com/apartments/utrecht/0-1200/radius-25",
    "https://www.huurwoningen.nl/en/in/wageningen/?radius=10",
    "https://www.huurwoningen.nl/en/in/arnhem/",
    "https://www.huurwoningen.nl/en/in/nijmegen/",
    "https://kamernet.nl/en/for-rent/properties-arnhem?pageNo=1&radius=4",
    "https://kamernet.nl/en/for-rent/properties-utrecht?pageNo=1&radius=4",
    "https://kamernet.nl/en/for-rent/properties-nijmegen?pageNo=1&radius=4"
]
BASE_URLS = {
    "pararius.com": "https://www.pararius.com",
    "huurwoningen.nl": "https://www.huurwoningen.nl",
    "kamernet.nl": "https://kamernet.nl"
}
DATA_FILE = "data.json"


def send_telegram(msg):
    """Enviar mensaje a Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "disable_web_page_preview": True}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Error enviando mensaje a Telegram:", e)


def load_seen():
    """Cargar propiedades vistas"""
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_seen(seen):
    """Guardar propiedades vistas"""
    with open(DATA_FILE, "w") as f:
        json.dump(seen, f)


def find_new_properties_pararius(soup):
    new_links = []
    for label in soup.find_all("span", class_="listing-label listing-label--new"):
        link_tag = label.find_parent("div", class_="listing-search-item__label").find_parent("div").find("a", class_="listing-search-item__link")
        if link_tag and link_tag.get("href"):
            new_links.append(BASE_URLS["pararius.com"] + link_tag["href"])
    return new_links


def find_new_properties_huurwoningen(soup):
    new_links = []
    for label in soup.find_all("span", class_="listing-label listing-label--new"):
        link_tag = label.find_parent("a", class_="listing-search-item__link")
        if link_tag and link_tag.get("href"):
            new_links.append(link_tag["href"])
    return new_links


def find_new_properties_kamernet(soup):
    new_links = []
    for label in soup.find_all("span", class_="MuiChip-label MuiChip-labelMedium mui-style-9iedg7"):
        link_tag = label.find_parent("a")
        if link_tag and link_tag.get("href"):
            new_links.append(BASE_URLS["kamernet.nl"] + link_tag["href"])
    return new_links


def scrape():
    seen = load_seen()
    for url in URLS:
        print("Revisando:", url)
        try:
            res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")
            domain = next((k for k in BASE_URLS if k in url), None)

            if domain == "pararius.com":
                new_items = find_new_properties_pararius(soup)
            elif domain == "huurwoningen.nl":
                new_items = find_new_properties_huurwoningen(soup)
            elif domain == "kamernet.nl":
                new_items = find_new_properties_kamernet(soup)
            else:
                new_items = []

            for item in new_items:
                if item not in seen.get(url, []):
                    send_telegram(f"🆕 Nuevo piso:\n{item}")
                    seen.setdefault(url, []).append(item)

        except Exception as e:
            print("Error en scraping:", e)

    save_seen(seen)


if __name__ == "__main__":
    scrape()

