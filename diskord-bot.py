import discord
import requests
from bs4 import BeautifulSoup
import asyncio

# --- Konfiguracja ---
DISCORD_TOKEN = ''  # Wklej tutaj token swojego bota
CHANNEL_ID = '1421853540665786530'  # Wklej ID kanału, na który mają być wysyłane powiadomienia
OLX_URL = 'https://www.olx.pl/elektronika/telefony/q-iphone/?search%5Bfilter_float_price:to%5D=2000&search%5Bfilter_enum_state%5D%5B0%5D=used&search%5Bfilter_enum_state%5D%5B1%5D=new&search%5Bfilter_enum_phonemodel%5D%5B0%5D=iphone-air&search%5Bfilter_enum_phonemodel%5D%5B1%5D=iphone-13-pro-max&search%5Bfilter_enum_phonemodel%5D%5B2%5D=iphone-17&search%5Bfilter_enum_phonemodel%5D%5B3%5D=iphone-12&search%5Bfilter_enum_phonemodel%5D%5B4%5D=iphone-12-mini&search%5Bfilter_enum_phonemodel%5D%5B5%5D=iphone-12-pro&search%5Bfilter_enum_phonemodel%5D%5B6%5D=iphone-12-pro-max&search%5Bfilter_enum_phonemodel%5D%5B7%5D=iphone-11-pro&search%5Bfilter_enum_phonemodel%5D%5B8%5D=iphone-11-pro-max&search%5Bfilter_enum_phonemodel%5D%5B9%5D=iphone-17-pro&search%5Bfilter_enum_phonemodel%5D%5B10%5D=iphone-17-pro-max&search%5Bfilter_enum_phonemodel%5D%5B11%5D=iphone-15-pro&search%5Bfilter_enum_phonemodel%5D%5B12%5D=iphone-16&search%5Bfilter_enum_phonemodel%5D%5B13%5D=iphone-16-plus&search%5Bfilter_enum_phonemodel%5D%5B14%5D=iphone-16pro&search%5Bfilter_enum_phonemodel%5D%5B15%5D=iphone-16-pro-max&search%5Bfilter_enum_phonemodel%5D%5B16%5D=iphone-15&search%5Bfilter_enum_phonemodel%5D%5B17%5D=iphone-15-plus&search%5Bfilter_enum_phonemodel%5D%5B18%5D=iphone-15-pro-max&search%5Bfilter_enum_phonemodel%5D%5B19%5D=iphone-14&search%5Bfilter_enum_phonemodel%5D%5B20%5D=iphone-14-plus&search%5Bfilter_enum_phonemodel%5D%5B21%5D=iphone-14-pro&search%5Bfilter_enum_phonemodel%5D%5B22%5D=iphone-14-pro-max&search%5Bfilter_enum_phonemodel%5D%5B23%5D=iphone-13&search%5Bfilter_enum_phonemodel%5D%5B24%5D=iphone-13-mini&search%5Bfilter_enum_phonemodel%5D%5B25%5D=iphone-13-pro'# Przykładowy link do wyszukiwania
CHECK_INTERVAL = 1  # Czas w sekundach, co ile bot ma sprawdzać nowe ogłoszenia (np. 300 = 5 minut)

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

# Lista do przechowywania linków już wysłanych ogłoszeń
sent_ads = set()

async def check_olx():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(OLX_URL, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Znajdź wszystkie kontenery z ogłoszeniami (selektor może się zmienić, sprawdź go w narzędziach deweloperskich przeglądarki)
            ads = soup.find_all('div', {'data-cy': 'l-card'})

            for ad in ads:
                # Wyciąganie linku
                link_tag = ad.find('a', href=True)
                link = 'https://www.olx.pl' + link_tag['href'] if link_tag and not link_tag['href'].startswith('http') else link_tag['href'] if link_tag else 'Brak linku'

                if link not in sent_ads:
                    # Wyciąganie tytułu
                    title_tag = ad.find('h6')
                    title = title_tag.text.strip() if title_tag else 'Brak tytułu'

                    # Wyciąganie ceny
                    price_tag = ad.find('p', {'data-testid': 'ad-price'})
                    price = price_tag.text.strip() if price_tag else 'Brak ceny'

                    # Wyciąganie lokalizacji
                    location_tag = ad.find('p', {'data-testid': 'location-date'})
                    location = location_tag.text.strip() if location_tag else 'Brak lokalizacji'
                    
                    # Sprawdzenie możliwości wysyłki (informacja o przesyłce OLX)
                    shipping_tag = ad.find('div', {'data-testid': 'delivery-badge'})
                    shipping = "Tak" if shipping_tag else "Nie"

                    # Formatowanie wiadomości
                    message = (
                        
                        f"**📌 Tytuł:** {title}\n"
                        f"**💰 Cena:** {price}\n"
                        f"**📍 Lokalizacja:** {location}\n"
                        f"**📦 Dostawa:** {shipping}\n\n"
                        f"**🔗 Link:** [Link do ogłoszenia]({link})""
                    )

                    await channel.send(message)
                    sent_ads.add(link)
                    
        except Exception as e:
            print(f"Wystąpił błąd: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

@client.event
async def on_ready():
    print(f'Zalogowano jako {client.user}')
    client.loop.create_task(check_olx())

client.run(DISCORD_TOKEN)