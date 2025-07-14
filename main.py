import requests
import json
import time
from bs4 import BeautifulSoup

# Configuración del bot
TELEGRAM_TOKEN = "8095048569:AAHrhxm0PgaFxf5LvWaViA4hAB4b9cst06k"
CHAT_ID = "1935816973"
URLS = [
    "https://www.pararius.com/apartments/arnhem/0-1200/radius-10",
    "https://www.pararius.com/apartments/wageningen/0-1200/radius-10",
    "https://www.pararius.com/apartments/utrecht/0-1200/radius-25",
    "https://www.funda.nl/zoeken/huur?selected_area=[%22wageningen,15km%22]&price=%220-1500%22&object_type=[%22apartment%22]&sort=%22date_down%22",
    "https://www.huurwoningen.nl/en/in/wageningen/?radius=10",
    "https://www.huurwoningen.nl/en/in/arnhem/",
    "https://www.huurwoningen.nl/en/in/nijmegen/",
    "https://kamernet.nl/en/for-rent/properties-arnhem?pageNo=1&radius=4&minSize=0&maxRent=0&searchCategories=2%2C1%2C4%2C17%2C19%2C18&searchView=1&sort=1&hasInternet=false&isBathroomPrivate=false&isKitchenPrivate=false&isToiletPrivate=false&suitableForNumberOfPersons=0&isSmokingInsideAllowed=false&isPetsInsideAllowed=false&nwlat=54.216270703936516&nwlng=-3.267085312500001&selat=50.130263513834905&selng=12.5532271875&mapZoom=7&mapMarkerLat=0&mapMarkerLng=0",
    "https://kamernet.nl/en/for-rent/room-wageningen?pageNo=1&radius=5&minSize=0&maxRent=0&searchView=1&sort=1&hasInternet=false&isBathroomPrivate=false&isKitchenPrivate=false&isToiletPrivate=false&suitableForNumberOfPersons=0&isSmokingInsideAllowed=false&isPetsInsideAllowed=false&nwlat=54.216270703936516&nwlng=-3.267085312500001&selat=50.130263513834905&selng=12.5532271875&mapZoom=7&mapMarkerLat=0&mapMarkerLng=0",
    "https://kamernet.nl/en/for-rent/properties-utrecht?pageNo=1&radius=4&minSize=0&maxRent=0&searchCategories=2%2C1%2C4%2C17%2C19%2C18&searchView=1&sort=1&hasInternet=false&isBathroomPrivate=false&isKitchenPrivate=false&isToiletPrivate=false&suitableForNumberOfPersons=0&isSmokingInsideAllowed=false&isPetsInsideAllowed=false&nwlat=54.216270703936516&nwlng=-3.267085312500001&selat=50.130263513834905&selng=12.5532271875&mapZoom=7&mapMarkerLat=0&mapMarkerLng=0",
    "https://kamernet.nl/en/for-rent/properties-nijmegen?pageNo=1&radius=4&minSize=0&maxRent=0&searchCategories=2%2C1%2C4%2C17%2C19%2C18&searchView=1&sort=1&hasInternet=false&isBathroomPrivate=false&isKitchenPrivate=false&isToiletPrivate=false&suitableForNumberOfPersons=0&isSmokingInsideAllowed=false&isPetsInsideAllowed=false&nwlat=54.216270703936516&nwlng=-3.267085312500001&selat=50.130263513834905&selng=12.5532271875&mapZoom=7&mapMarkerLat=0&mapMarkerLng=0"
]
DATA_FILE = "data.json"

# Función para enviar mensajes a Telegram
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "disable_web_page_preview": True}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Error enviando mensaje a Telegram:", e)

# Cargar datos vistos previamente
def load_seen():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Guardar datos vistos
def save_seen(seen):
    with open(DATA_FILE, "w") as f:
        json.dump(seen, f)

# Función principal de scraping
def scrape():
    seen = load_seen()
    for url in URLS:
        print("Revisando:", url)
        try:
            res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a", href=True)
            new_items = []
            for link in links:
                href = link["href"]
                if href not in seen.get(url, []):
                    seen.setdefault(url, []).append(href)
                    full_link = href if href.startswith("http") else f"{url}{href}"
                    new_items.append(full_link)
            if new_items:
                for item in new_items:
                    send_telegram(f"🆕 Nuevo anuncio:\n{item}")
        except Exception as e:
            print("Error en scraping:", e)
    save_seen(seen)


if __name__ == "__main__":
    scrape()
