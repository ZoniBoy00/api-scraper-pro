"""
Basic API Scraping Example
==========================

Demonstrates core functionality of API Scraper Pro.
"""

import asyncio
import yaml
from core.browser import StealthBrowser
from core.crawler import SmartCrawler
from core.interceptor import NetworkInterceptor
from core.database import DatabaseManager
from utils.robots import RobotsParser
from utils.normalization import DataNormalizer


async def main():
    """Main function."""
    
    # Load config
    with open('config/default.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Target URL
    target_url = "https://jsonplaceholder.typicode.com"
    
    print("🕷️  API Scraper Pro - Example")
    print(f"🎯 Target: {target_url}\n")
    
    # Check robots.txt
    robots = RobotsParser(respect_robots=config.get('compliance', {}).get('respect_robots_txt', True))
    await robots.load(target_url)
    
    if not robots.is_allowed(target_url):
        print("❌ Blocked by robots.txt!")
        return
    
    # Initialize data normalizer
    normalizer = DataNormalizer(config)
    
    # Start scraping
    async with (
        StealthBrowser(config.get('scraping', {})) as browser,
        DatabaseManager(config.get('database', {})) as db
    ):
        crawler = SmartCrawler(config.get('scraping', {}))
        interceptor = NetworkInterceptor(config)
        
        # Callback to save and anonymize API calls
        async def save_and_anonymize(api_data):
            # Anonymize PII
            api_data['response_body'] = normalizer.anonymize(api_data['response_body'])
            
            # Detect PII (for logging)
            pii_found = normalizer.detect_pii(api_data['response_body'])
            if pii_found:
                print(f"🔒 PII detected and anonymized: {pii_found}")
            
            # Save to database
            await db.save_api_call(api_data)
            print(f"💾 API saved: {api_data['method']} {api_data['url']}")
        
        interceptor.add_callback(save_and_anonymize)
        
        # Add starting URL
        crawler.add_url(target_url, depth=0, priority=10)
        
        # Crawl loop
        crawled = 0
        max_pages = 5  # Limit for example
        
        while crawled < max_pages:
            next_url = crawler.get_next_url()
            if not next_url:
                break
            
            depth, page_url = next_url
            
            # Check robots.txt
            if not robots.is_allowed(page_url):
                print(f"🚫 Blocked by robots.txt: {page_url}")
                continue
            
            print(f"\n🔍 Crawling (depth {depth}): {page_url}")
            
            # Create page
            page = await browser.new_page()
            await interceptor.attach(page)
            
            # Crawl page
            links = await crawler.crawl_page(page, page_url)
            
            # Add new links
            for link in links[:5]:  # Limit links for example
                crawler.add_url(link, depth=depth + 1)
            
            await page.close()
            crawled += 1
            
            # Respect crawl delay
            crawl_delay = robots.get_crawl_delay() or config.get('scraping', {}).get('page_delay', 2000) / 1000
            await asyncio.sleep(crawl_delay)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 Summary")
        print("="*60)
        
        crawler_stats = crawler.get_stats()
        interceptor_stats = interceptor.get_stats()
        db_stats = await db.get_stats()
        
        print(f"✅ Pages crawled: {crawler_stats['visited_urls']}")
        print(f"🎯 APIs found: {interceptor_stats['total_apis']}")
        print(f"📍 Unique endpoints: {interceptor_stats['unique_endpoints']}")
        print(f"💾 Database size: {db_stats['database_size_mb']} MB")
        
        # Print endpoints
        print("\n🔥 Discovered endpoints:")
        for i, endpoint in enumerate(interceptor.get_unique_endpoints()[:10], 1):
            print(f"  {i}. {endpoint}")
        
        # Create backup
        backup_path = await db.backup()
        if backup_path:
            print(f"\n💾 Backup created: {backup_path}")
        
        print("\n✨ Done!")


if __name__ == "__main__":
    asyncio.run(main())
