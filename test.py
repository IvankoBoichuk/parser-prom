import re
from bs4 import BeautifulSoup
from utils import fetch_page

html = fetch_page("https://prom.ua/ua/p1642315322-menazhnitsya-oval.html")
soup = BeautifulSoup(html, "html.parser")

order_counter = soup.select_one("[data-qaid='order_counter']")
if order_counter:
    text = order_counter.get_text(strip=True)
    match = re.search(r'\d+', text)
    number = int(match.group()) if match else None
    print(number)
else:
    print("Не знайдено")