import requests
from bs4 import BeautifulSoup
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URL = "https://www.pararius.com/apartments/arnhem/0-1200/radius-110"
BASE_URL = "https://www.pararius.com"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "disable_web_page_preview": True}
    try:
        r = requests.post(url, data=payload)
        print("Enviado a Telegram:", msg)
        print("Respuesta Telegram:", r.text)
    except Exception as e:
        print("Error enviando mensaje a Telegram:", e)

def scrape():
    print(f"Revisando: {URL}")
    try:
        res = requests.get(URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        found = False
        for label in soup.find_all("span", class_="listing-label listing-label--new"):
            print("Etiqueta NEW encontrada:", label)
            a_tag = label.find_parent("div", class_="listing-search-item__label")
            if a_tag:
                main_item = a_tag.find_parent("div")
                if main_item:
                    link_tag = main_item.find("a", class_="listing-search-item__link")
                    if link_tag and link_tag.get("href"):
                        full_link = BASE_URL + link_tag["href"] if link_tag["href"].startswith("/") else link_tag["href"]
                        print("Link detectado:", full_link)
                        send_telegram(f"🆕 Nuevo piso (TEST):\n{full_link}")
                        found = True
        if not found:
            print("No se detectaron anuncios nuevos con etiqueta 'New'.")
    except Exception as e:
        print("Error en scraping:", e)

if __name__ == "__main__":
    scrape()

