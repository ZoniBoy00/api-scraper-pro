"""
Stealth Browser - Bot Detection Evasion
========================================

Playwright-based browser with advanced stealth capabilities.
"""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Dict, Any, List
import asyncio
import random
from loguru import logger

# Try to import playwright_stealth (optional)
try:
    from playwright_stealth import stealth_async
    STEALTH_AVAILABLE = True
except ImportError:
    logger.warning("playwright_stealth not available, using basic stealth only")
    STEALTH_AVAILABLE = False
    async def stealth_async(page):
        pass  # No-op if stealth not available


class StealthBrowser:
    """Browser with built-in bot detection evasion."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self._pages: List[Page] = []
        
    async def initialize(self) -> None:
        """Initialize Playwright browser with stealth settings."""
        logger.info("Initializing stealth browser...")
        
        self.playwright = await async_playwright().start()
        
        # Optimized launch args for stealth
        launch_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
        ]
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.config.get('headless', True),
            args=launch_args
        )
        
        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self._get_random_user_agent(),
            locale='en-US',
            timezone_id='America/New_York',
            color_scheme='dark',
        )
        
        logger.success("Browser initialized successfully")
        
    async def new_page(self) -> Page:
        """Create new page with stealth features."""
        if not self.context:
            await self.initialize()
            
        page = await self.context.new_page()
        await stealth_async(page)
        await self._inject_stealth_scripts(page)
        
        if self.config.get('mouse_movements', True):
            await self._setup_mouse_movements(page)
            
        self._pages.append(page)
        logger.debug(f"New page created (total: {len(self._pages)})")
        
        return page
    
    async def _inject_stealth_scripts(self, page: Page) -> None:
        """Inject custom stealth scripts."""
        stealth_script = """
        () => {
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {name: 'Chrome PDF Plugin', description: 'Portable Document Format'},
                    {name: 'Chrome PDF Viewer', description: ''}
                ]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';
                if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                return getParameter.apply(this, [parameter]);
            };
        }
        """
        await page.add_init_script(stealth_script)
        
    async def _setup_mouse_movements(self, page: Page) -> None:
        """Setup realistic mouse movements."""
        movement_script = """
        async () => {
            const moveRandomly = () => {
                const x = Math.random() * window.innerWidth;
                const y = Math.random() * window.innerHeight;
                const event = new MouseEvent('mousemove', {
                    view: window, bubbles: true, cancelable: true,
                    clientX: x, clientY: y
                });
                document.dispatchEvent(event);
            };
            setInterval(moveRandomly, 3000 + Math.random() * 2000);
        }
        """
        await page.evaluate(movement_script)
        
    def _get_random_user_agent(self) -> str:
        """Get random realistic user agent."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        ]
        return random.choice(user_agents) if self.config.get('rotate_user_agent', True) else user_agents[0]
    
    async def close(self) -> None:
        """Close browser and release resources."""
        logger.info("Closing browser...")
        
        for page in self._pages:
            try:
                await page.close()
            except Exception as e:
                logger.warning(f"Failed to close page: {e}")
        
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
        logger.success("Browser closed")
        
    async def __aenter__(self):
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
