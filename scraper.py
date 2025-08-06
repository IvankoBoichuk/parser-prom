import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session
from tqdm import tqdm

from models import Competitor, CompetitorProduct, CompetitorReview
from utils import extract_rating, fetch_page

def parse_product_page(product_url):
    """ Заглушка для майбутнього парсингу сторінки товару """
    pass

def get_prefix(soup: BeautifulSoup):
    prefixes = [".b", ".cs"]
    for prefix in prefixes:
        if soup.select(f"{prefix}-comments__list"):
            return prefix
        
    return None

def process_page(url, competitor_id, session: Session):
    html = fetch_page(url)
    soup = BeautifulSoup(html, "html.parser")
    prefix = get_prefix(soup)
    
    # .cs-comments__list .cs-comments__item
    reviews = soup.select(f"{prefix}-comments__list {prefix}-comments__item")
    if not reviews:
        return

    products_to_add = {}
    reviews_to_add = []
    parsed_products = set()

    for review in reviews:
        data = review.select_one("[data-reviews-products]")
        if not data:
            continue

        try:
            data = json.loads(data["data-reviews-products"])
        except Exception:
            continue

        # .cs-rating__bar
        rating = extract_rating(review.select_one(f"{prefix}-rating__bar")["title"]) if review.select_one(f"{prefix}-rating__bar") else None
        review_text = review.select_one(f"{prefix}-comments__text").get_text(strip=True) if review.select_one(f"{prefix}-comments__text") else ""
        author = review.select_one(f"{prefix}-comments__author-name").get_text(strip=True) if review.select_one(f"{prefix}-comments__author-name") else ""
        date_raw = review.select_one(f"{prefix}-comments__date")["datetime"] if review.select_one(f"{prefix}-comments__date") else ""
        date = datetime.strptime(date_raw, "%Y-%m-%dT%H:%M:%S") if date_raw else None
        tags = ", ".join([tag["data-tag-title"] for tag in review.select(f"{prefix}-comments-tags__item")]) if review.select(f"{prefix}-comments-tags__item") else ""

        for item in data:
            product_id = item.get("id")
            product_url = item.get("url", "")
            product_name = item.get("name", "")

            # ✅ Уникнути повторного запиту до БД
            if product_id not in products_to_add and not session.query(CompetitorProduct.id).filter_by(id=product_id).scalar():
                products_to_add[product_id] = CompetitorProduct(
                    id=product_id,
                    competitor_id=competitor_id,
                    name=product_name,
                    url=product_url
                )

            # ✅ Уникнути повторного парсингу тієї ж сторінки
            if product_url and product_id not in parsed_products:
                parse_product_page(product_url)
                parsed_products.add(product_id)

            # ✅ Підготувати відгук для пакетного збереження
            reviews_to_add.append(CompetitorReview(
                product_id=product_id,
                review_average=rating,
                review_text=review_text,
                author=author,
                date=date,
                tags=tags,
                competitor_id=competitor_id
            ))

    # ✅ Додати продукти одним запитом
    if products_to_add:
        session.bulk_save_objects(products_to_add.values())

    # ✅ Додати відгуки одним запитом
    if reviews_to_add:
        session.bulk_save_objects(reviews_to_add)

    session.commit()

def get_total_pages(competitor:Competitor):
    response = requests.get(competitor.site_url + "/ua/testimonials")
    soup = BeautifulSoup(response.text, "html.parser")
    paginator = soup.select_one('[data-bazooka="Paginator"]')
    return int(paginator["data-pagination-pages-count"]) if paginator and paginator.has_attr("data-pagination-pages-count") else 1

def run_scraper(session, competitor:Competitor):
    total_pages = get_total_pages(competitor)
    print(f"Знайдено сторінок: {total_pages}")
    for page in tqdm(range(1, total_pages + 1), desc="📄 Обробка сторінок", unit="page"):
        url = f"{competitor.site_url}/ua/testimonials/page_{page}"
        process_page(url, competitor.id, session)
