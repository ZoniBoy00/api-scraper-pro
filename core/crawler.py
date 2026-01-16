"""
Smart Crawler - Intelligent Website Crawling
============================================

Dynamic website mapping with priority queue.
"""

from playwright.async_api import Page
from typing import Dict, Any, List, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse
from loguru import logger
import asyncio
from collections import deque
import re


class SmartCrawler:
    """Intelligent crawler with dynamic website mapping."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_depth = config.get('max_depth', 3)
        self.page_delay = config.get('page_delay', 2000) / 1000
        self.timeout = config.get('timeout', 30000)
        
        self.visited_urls: Set[str] = set()
        self.queue: deque = deque()
        self.url_depths: Dict[str, int] = {}
        
        self.priority_patterns = [
            (r'/api/', 10), (r'/graphql', 10), (r'/rest/', 9),
            (r'/v\d+/', 8), (r'/products', 7), (r'/search', 7),
            (r'/data', 7), (r'/users', 6), (r'/posts', 6),
        ]
        
    def add_url(self, url: str, depth: int = 0, priority: int = 5) -> None:
        """Add URL to crawl queue."""
        normalized = self._normalize_url(url)
        
        if normalized in self.visited_urls or depth > self.max_depth:
            return
        
        if not self._is_same_domain(normalized):
            return
        
        calculated_priority = self._calculate_priority(normalized, priority)
        self.queue.append((calculated_priority, depth, normalized))
        self.url_depths[normalized] = depth
        self.queue = deque(sorted(self.queue, key=lambda x: x[0], reverse=True))
        
        logger.debug(f"URL queued: {normalized} (depth: {depth}, priority: {calculated_priority})")
    
    def get_next_url(self) -> Optional[Tuple[int, str]]:
        """Get next URL to crawl."""
        while self.queue:
            priority, depth, url = self.queue.popleft()
            if url not in self.visited_urls:
                self.visited_urls.add(url)
                return (depth, url)
        return None
    
    async def crawl_page(self, page: Page, url: str) -> List[str]:
        """Crawl single page and return found links."""
        try:
            logger.info(f"Crawling: {url}")
            
            response = await page.goto(url, wait_until='networkidle', timeout=self.timeout)
            
            if not response or response.status >= 400:
                logger.warning(f"HTTP {response.status if response else 'N/A'}: {url}")
                return []
            
            await asyncio.sleep(self.page_delay)
            await self._scroll_page(page)
            links = await self._extract_links(page, url)
            
            logger.success(f"Crawled: {url} ({len(links)} links found)")
            return links
            
        except Exception as e:
            logger.error(f"Crawl failed ({url}): {e}")
            return []
    
    async def _scroll_page(self, page: Page) -> None:
        """Scroll page to trigger lazy loading."""
        try:
            await page.evaluate("""
                async () => {
                    const distance = 100;
                    const delay = 100;
                    while (window.scrollY + window.innerHeight < document.body.scrollHeight) {
                        window.scrollBy(0, distance);
                        await new Promise(resolve => setTimeout(resolve, delay));
                    }
                }
            """)
        except Exception as e:
            logger.debug(f"Scroll failed: {e}")
    
    async def _extract_links(self, page: Page, base_url: str) -> List[str]:
        """Extract all links from page."""
        try:
            links = await page.evaluate("""
                () => {
                    const anchors = Array.from(document.querySelectorAll('a[href]'));
                    return anchors.map(a => a.href).filter(href => href);
                }
            """)
            
            normalized_links = []
            for link in links:
                try:
                    absolute_url = urljoin(base_url, link)
                    normalized = self._normalize_url(absolute_url)
                    
                    if normalized in self.visited_urls or not self._is_same_domain(normalized):
                        continue
                    
                    normalized_links.append(normalized)
                except Exception:
                    continue
            
            return list(set(normalized_links))
            
        except Exception as e:
            logger.debug(f"Link extraction failed: {e}")
            return []
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL (remove fragment, sort params)."""
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        if parsed.query:
            normalized += f"?{parsed.query}"
        
        if normalized.endswith('/') and len(normalized) > 10:
            normalized = normalized[:-1]
        
        return normalized
    
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL is from same domain."""
        if not hasattr(self, '_base_domain'):
            parsed = urlparse(url)
            self._base_domain = parsed.netloc
            return True
        
        parsed = urlparse(url)
        return parsed.netloc == self._base_domain
    
    def _calculate_priority(self, url: str, base_priority: int) -> int:
        """Calculate URL priority based on patterns."""
        priority = base_priority
        for pattern, boost in self.priority_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                priority += boost
                logger.debug(f"Priority boost +{boost} for {url} (pattern: {pattern})")
        return priority
    
    def get_stats(self) -> Dict[str, Any]:
        """Get crawling statistics."""
        return {
            'visited_urls': len(self.visited_urls),
            'queue_size': len(self.queue),
            'max_depth': self.max_depth,
            'urls_by_depth': self._count_by_depth(),
        }
    
    def _count_by_depth(self) -> Dict[int, int]:
        """Count URLs by depth."""
        counts = {}
        for depth in self.url_depths.values():
            counts[depth] = counts.get(depth, 0) + 1
        return counts
    
    def clear(self) -> None:
        """Clear crawler state."""
        self.visited_urls.clear()
        self.queue.clear()
        self.url_depths.clear()
        logger.debug("Crawler state cleared")
