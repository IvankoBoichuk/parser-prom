import re
import tqdm
import typer
from bs4 import BeautifulSoup
from database import init_db
from utils import fetch_page
from models import CompetitorProduct
from sqlalchemy.orm import Session

app = typer.Typer(help="Команди для запуску скрейпера")

@app.command("run")
def update_products():
    """Оновити кількість куплених товарів у БД"""
    with init_db() as session:
        products = session.query(CompetitorProduct).filter(CompetitorProduct.url.isnot(None)).all()
        if not products:
            typer.echo("⚠️ Немає жодного продукту у БД.")
            raise typer.Exit()

        typer.echo(f"📌 Оновлення куплених товарів: {len(products)} шт.")
        updated_count = 0

        for product in tqdm(products, desc="Оновлення товарів", unit="product"):
            try:
                html = fetch_page("https://prom.ua" + product.url)
                soup = BeautifulSoup(html, "html.parser")
                bought_count = get_bought_count(soup)
                category = get_category(soup)
                price = get_price(soup)
                if bought_count is not None:
                    product.bought_count = bought_count

                if category:
                    product.category = category
                
                if price:
                    product.price = price
                    
                updated_count += 1
                # typer.echo(f"✅ {product.name} (ID: {product.id}) → {bought_count}")
                
            except Exception as e:
                typer.echo(f"⚠️ Помилка з {product.id}: {e}")

        session.commit()
        typer.echo(f"✅ Оновлено {updated_count}/{len(products)} продуктів.")


def get_bought_count(soup: BeautifulSoup):
    """Отримати кількість куплених товарів з HTML-сторінки"""
    order_counter = soup.select_one("[data-qaid='order_counter']")
    if not order_counter:
        return None

    match = re.search(r'\d+', order_counter.get_text(strip=True))
    return int(match.group()) if match else 0

def get_price(soup: BeautifulSoup):
    """Отримати ціну товару з HTML-сторінки"""
    element = soup.select_one("[data-qaid='main_product_info'] [data-qaid='product_price'] span")
    if not element:
        return None

    text = element.get_text(strip=True)

    # Витягуємо тільки цифри, крапки та коми
    cleaned = re.sub(r"[^\d.,]", "", text)

    # Замінюємо кому на крапку, якщо потрібно
    cleaned = cleaned.replace(",", ".")
    
    try:
        return float(cleaned)
    except ValueError:
        return None

def get_category(soup: BeautifulSoup) -> str:
    """Отримати категорію товару з breadcrumb"""
    categories = soup.select("[data-qaid='breadcrumbs_seo_item']")
    if not categories:
        return None
    return categories[-1].get_text(strip=True)
