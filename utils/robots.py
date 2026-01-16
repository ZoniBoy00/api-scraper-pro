"""
Robots.txt Parser - Respect Website Crawling Rules
==================================================

Reads and respects robots.txt directives.
"""

from urllib.parse import urljoin, urlparse
from typing import Set, Optional
from loguru import logger
import httpx


class RobotsParser:
    """Parses and respects robots.txt rules."""
    
    def __init__(self, respect_robots: bool = True):
        self.respect_robots = respect_robots
        self.disallowed_paths: Set[str] = set()
        self.crawl_delay: Optional[float] = None
        self._loaded = False
    
    async def load(self, base_url: str) -> None:
        """Load robots.txt from URL."""
        if not self.respect_robots:
            logger.info("Robots.txt ignored (respect_robots=False)")
            return
        
        try:
            parsed = urlparse(base_url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            logger.info(f"Loading robots.txt: {robots_url}")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(robots_url)
                
                if response.status_code == 200:
                    self._parse(response.text)
                    self._loaded = True
                    logger.success(f"Robots.txt loaded ({len(self.disallowed_paths)} disallow rules)")
                else:
                    logger.warning(f"Robots.txt not found (HTTP {response.status_code})")
        
        except Exception as e:
            logger.warning(f"Robots.txt load failed: {e}")
    
    def _parse(self, content: str) -> None:
        """Parse robots.txt content."""
        user_agent_match = False
        
        for line in content.split('\n'):
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            if ':' in line:
                directive, value = line.split(':', 1)
                directive = directive.strip().lower()
                value = value.strip()
                
                if directive == 'user-agent':
                    user_agent_match = (value == '*')
                
                elif directive == 'disallow' and user_agent_match:
                    if value:
                        self.disallowed_paths.add(value)
                
                elif directive == 'crawl-delay' and user_agent_match:
                    try:
                        self.crawl_delay = float(value)
                        logger.info(f"Crawl delay set: {self.crawl_delay}s")
                    except ValueError:
                        pass
    
    def is_allowed(self, url: str) -> bool:
        """Check if URL crawling is allowed."""
        if not self.respect_robots or not self._loaded:
            return True
        
        parsed = urlparse(url)
        path = parsed.path
        
        for disallowed in self.disallowed_paths:
            if path.startswith(disallowed):
                logger.debug(f"Robots.txt blocks: {url}")
                return False
        
        return True
    
    def get_crawl_delay(self) -> Optional[float]:
        """Get recommended crawl delay."""
        return self.crawl_delay
