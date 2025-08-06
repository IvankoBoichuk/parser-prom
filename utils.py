import os
import re
import requests
from slugify import slugify

from models import Competitor

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_page(url):
    """Завантажує сторінку з кешу або сайту"""
    slug = slugify(url)
    cache_file = os.path.join(CACHE_DIR, f"{slug}.html")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        response = requests.get(url)
        response.encoding = 'utf-8'
        html = response.text
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(html)
    return html

def extract_rating(text):
    match = re.search(r'(\d+(?:[\.,]\d+)?)\s*з\s*\d+', text)
    return float(match.group(1).replace(',', '.')) if match else None


def get_competitor(session, name: str):
    """Отримати конкурента за ім'ям"""
    return session.query(Competitor).filter_by(name=name).first()

def create_competitor(session, name: str, site_url: str):
    """Створити нового конкурента"""
    competitor = Competitor(name=name, site_url=site_url)
    session.add(competitor)
    session.commit()
    return competitor

def get_or_create_competitor(session, name: str, site_url: str):
    """Отримати конкурента або створити, якщо не існує"""
    competitor = get_competitor(session, name)
    if competitor:
        return competitor
    return create_competitor(session, name, site_url)