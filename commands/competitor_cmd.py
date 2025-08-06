import typer
from database import init_db
from models import Competitor

app = typer.Typer(help="Команди для роботи з конкурентами")

@app.command("create")
def create_competitor(
    name: str = typer.Option(..., help="Назва конкурента"),
    site_url: str = typer.Option(..., help="Сайт конкурента")
):
    """Створити запис у таблиці competitors"""
    session = init_db()
    existing = session.query(Competitor).filter_by(name=name).first()
    if existing:
        typer.echo(f"⚠️ Конкурент '{name}' вже існує (id={existing.id})")
        return
    new_competitor = Competitor(name=name, site_url=site_url)
    session.add(new_competitor)
    session.commit()
    typer.echo(f"✅ Конкурент '{name}' успішно доданий (id={new_competitor.id})")
