"""
Proxy Manager - Proxy Rotation Management
=========================================

Handles proxy server rotation and management.
"""

from typing import List, Optional, Dict, Any
from loguru import logger
import random
from urllib.parse import urlparse


class ProxyManager:
    """Manages proxy server rotation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', False)
        self.rotation = config.get('rotation', True)
        self.timeout = config.get('timeout', 10)
        self.proxies = self._parse_proxies(config.get('providers', []))
        self.current_index = 0
        
        if self.enabled and self.proxies:
            logger.info(f"Proxy manager initialized ({len(self.proxies)} proxies)")
        elif self.enabled and not self.proxies:
            logger.warning("Proxy enabled but no proxies configured!")
    
    def _parse_proxies(self, providers: List[str]) -> List[Dict[str, str]]:
        """Parse proxy strings to Playwright format."""
        parsed = []
        
        for proxy_url in providers:
            try:
                parsed_url = urlparse(proxy_url)
                proxy_dict = {'server': f"{parsed_url.scheme}://{parsed_url.netloc}"}
                
                if parsed_url.username:
                    proxy_dict['username'] = parsed_url.username
                if parsed_url.password:
                    proxy_dict['password'] = parsed_url.password
                
                parsed.append(proxy_dict)
            except Exception as e:
                logger.warning(f"Proxy parsing failed ({proxy_url}): {e}")
        
        return parsed
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy from rotation."""
        if not self.enabled or not self.proxies:
            return None
        
        if self.rotation:
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
        else:
            proxy = self.proxies[0]
        
        logger.debug(f"Using proxy: {proxy['server']}")
        return proxy
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get random proxy."""
        if not self.enabled or not self.proxies:
            return None
        
        proxy = random.choice(self.proxies)
        logger.debug(f"Random proxy: {proxy['server']}")
        return proxy
    
    def is_enabled(self) -> bool:
        """Check if proxy is enabled."""
        return self.enabled and len(self.proxies) > 0
