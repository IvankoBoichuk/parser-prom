import typer
from commands import competitor_cmd, scraper_cmd, update_products_cmd

app = typer.Typer(help="🛠 Scraper CLI")

# Підкоманди
app.add_typer(competitor_cmd.app, name="competitor")
app.add_typer(scraper_cmd.app, name="scraper")
app.add_typer(update_products_cmd.app, name="updator")

if __name__ == "__main__":
    app()
