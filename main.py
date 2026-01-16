"""
API Scraper Pro - Main CLI Entry Point
======================================

Professional-grade API crawler and scraper.
"""

import asyncio
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
import yaml
from loguru import logger
import sys

from core.browser import StealthBrowser
from core.crawler import SmartCrawler
from core.interceptor import NetworkInterceptor
from core.database import DatabaseManager
from utils.helpers import load_yaml_config, ensure_directory

app = typer.Typer(help="🕷️ API Scraper Pro - Automated API Discovery & Scraping")
console = Console()


def setup_logging(config: dict) -> None:
    """Setup logging configuration."""
    log_config = config.get('logging', {})
    log_level = log_config.get('level', 'INFO')
    log_file = log_config.get('file', 'logs/scraper.log')
    
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    logger.remove()
    
    if log_config.get('colorize', True):
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            colorize=True
        )
    
    logger.add(
        log_file,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        rotation=f"{log_config.get('max_size', 10)} MB",
        retention=log_config.get('backup_count', 5)
    )


@app.command()
def scrape(
    url: str = typer.Argument(..., help="Start URL"),
    config: str = typer.Option("config/default.yaml", help="Config file"),
    depth: int = typer.Option(None, help="Max crawl depth"),
    headless: bool = typer.Option(True, help="Headless mode"),
    output: str = typer.Option(None, help="Output file (JSON)"),
):
    """Start API scraping."""
    cfg = load_yaml_config(config)
    setup_logging(cfg)
    
    if depth is not None:
        cfg.setdefault('scraping', {})['max_depth'] = depth
    if headless is not None:
        cfg.setdefault('scraping', {})['headless'] = headless
    
    console.print(Panel.fit(
        "[bold cyan]🕷️  API Scraper Pro[/bold cyan]\n"
        "[dim]Automated API Discovery & Scraping[/dim]",
        border_style="cyan"
    ))
    
    asyncio.run(run_scraper(url, cfg, output))


async def run_scraper(url: str, config: dict, output: str = None):
    """Main async scraper logic."""
    logger.info(f"Starting scrape: {url}")
    
    browser_config = config.get('scraping', {})
    browser_config.update(config.get('stealth', {}))
    
    async with (
        StealthBrowser(browser_config) as browser,
        DatabaseManager(config.get('database', {})) as db
    ):
        crawler = SmartCrawler(config.get('scraping', {}))
        interceptor = NetworkInterceptor(config)
        
        async def save_api_callback(api_data):
            await db.save_api_call(api_data)
        
        interceptor.add_callback(save_api_callback)
        crawler.add_url(url, depth=0, priority=10)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Crawling...", total=None)
            crawled_count = 0
            
            while True:
                next_url = crawler.get_next_url()
                if not next_url:
                    break
                
                depth, page_url = next_url
                progress.update(task, description=f"[cyan]Crawling (depth {depth}): {page_url[:60]}...")
                
                page = await browser.new_page()
                await interceptor.attach(page)
                links = await crawler.crawl_page(page, page_url)
                
                for link in links:
                    crawler.add_url(link, depth=depth + 1)
                
                await page.close()
                crawled_count += 1
                progress.update(task, advance=1)
        
        console.print("\n")
        console.print(Panel.fit("[bold green]✅ Scraping complete![/bold green]", border_style="green"))
        
        crawler_stats = crawler.get_stats()
        interceptor_stats = interceptor.get_stats()
        db_stats = await db.get_stats()
        
        table = Table(title="📊 Statistics", show_header=True, header_style="bold magenta")
        table.add_column("Category", style="cyan")
        table.add_column("Value", justify="right", style="green")
        
        table.add_row("Pages crawled", str(crawler_stats['visited_urls']))
        table.add_row("APIs found", str(interceptor_stats['total_apis']))
        table.add_row("Unique endpoints", str(interceptor_stats['unique_endpoints']))
        table.add_row("Database size", f"{db_stats['database_size_mb']} MB")
        
        console.print(table)
        
        if output:
            await export_data(db, output, 'json')
            console.print(f"\n[green]✅ Data exported: {output}[/green]")
        
        logger.success("Scraping completed successfully!")
        
        # Keep window open to show results
        console.print("\n" + "="*60)
        console.print("[bold cyan]Press ENTER to close this window...[/bold cyan]")
        console.print("="*60)
        input()  # Wait for user input before closing


@app.command()
def stats(config: str = typer.Option("config/default.yaml", help="Config file")):
    """Show database statistics."""
    cfg = load_yaml_config(config)
    asyncio.run(show_stats(cfg))


async def show_stats(config: dict):
    """Display statistics."""
    async with DatabaseManager(config.get('database', {})) as db:
        stats = await db.get_stats()
        endpoints = await db.get_all_endpoints()
        
        console.print(Panel.fit("[bold cyan]📊 API Scraper Statistics[/bold cyan]", border_style="cyan"))
        
        table = Table(title="Overview", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="green")
        
        table.add_row("Total endpoints", str(stats['total_endpoints']))
        table.add_row("Total API calls", str(stats['total_calls']))
        table.add_row("Database size", f"{stats['database_size_mb']} MB")
        
        console.print(table)
        console.print()
        
        if endpoints:
            top_table = Table(title="🔥 Top 10 Endpoints", show_header=True, header_style="bold yellow")
            top_table.add_column("#", style="dim", width=4)
            top_table.add_column("Method", style="cyan", width=8)
            top_table.add_column("URL", style="blue")
            top_table.add_column("Calls", justify="right", style="green", width=10)
            
            for i, ep in enumerate(endpoints[:10], 1):
                top_table.add_row(str(i), ep['method'], ep['url'][:80], str(ep['call_count']))
            
            console.print(top_table)


@app.command("export")
def export_cmd(
    format: str = typer.Option("json", help="Export format (json/csv)"),
    output: str = typer.Option("export.json", help="Output file"),
    config: str = typer.Option("config/default.yaml", help="Config file"),
):
    """Export database to file."""
    cfg = load_yaml_config(config)
    asyncio.run(export_data_cmd(cfg, output, format))


async def export_data_cmd(config: dict, output: str, format: str):
    """Export data."""
    async with DatabaseManager(config.get('database', {})) as db:
        await export_data(db, output, format)
        console.print(f"[green]✅ Data exported: {output}[/green]")


async def export_data(db: DatabaseManager, output: str, format: str):
    """Export data to file."""
    import json
    endpoints = await db.get_all_endpoints()
    
    if format == 'json':
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(endpoints, f, indent=2, ensure_ascii=False)
    elif format == 'csv':
        import csv
        with open(output, 'w', encoding='utf-8', newline='') as f:
            if not endpoints:
                return
            fieldnames = endpoints[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(endpoints)


@app.command()
def dashboard(config: str = typer.Option("config/default.yaml", help="Config file")):
    """Launch interactive dashboard (Streamlit)."""
    console.print("[cyan]🚀 Launching dashboard...[/cyan]")
    console.print("[dim]Dashboard will open in browser...[/dim]")
    
    import subprocess
    subprocess.run(["streamlit", "run", "dashboard/app.py", "--", "--config", config])


if __name__ == "__main__":
    app()
