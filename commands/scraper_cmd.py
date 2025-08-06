import typer
from database import init_db
from models import Competitor
from scraper import run_scraper

app = typer.Typer(help="Команди для запуску скрейпера")

@app.command("run")
def scrape(
    competitor_id: int = typer.Option(
        None,
        "--competitor-id",
        help="ID конкурента (якщо не задано, буде показано список)"
    )
):
    """Запустити процес збору відгуків для вибраного конкурента"""
    session = init_db()

    # Якщо ID не передали, пропонуємо вибрати
    if competitor_id is None:
        competitors = session.query(Competitor).all()
        if not competitors:
            typer.echo("⚠️ Немає жодного конкурента у БД. Спочатку додайте його командою:")
            typer.echo("   python main.py competitor create --name 'Назва' --site_url 'URL'")
            raise typer.Exit()

        typer.echo("📌 Виберіть конкурента:")
        for c in competitors:
            typer.echo(f"{c.id}. {c.name} ({c.site_url})")

        competitor_id = typer.prompt("Введіть ID конкурента", type=int)

    selected = session.query(Competitor).filter_by(id=competitor_id).first()
    if not selected:
        typer.echo("❌ Конкурента з таким ID не знайдено")
        raise typer.Exit()

    typer.echo(f"🚀 Запуск скрейпера для: {selected.name} ({selected.site_url})")
    run_scraper(session, competitor=selected)
    typer.echo("✅ Скрейпінг завершено!")
