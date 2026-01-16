"""
Network Interceptor - API Call Capture
======================================

Captures and analyzes network traffic to identify API calls.
"""

from playwright.async_api import Page, Response, Request
from typing import Dict, Any, List, Callable, Optional
from loguru import logger
import json
import re
from datetime import datetime
from urllib.parse import urlparse


class NetworkInterceptor:
    """Captures and analyzes network traffic for API calls."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.captured_apis: List[Dict[str, Any]] = []
        self.api_detection = config.get('api_detection', {})
        self.ignore_patterns = self.api_detection.get('ignore_patterns', [])
        self.content_types = self.api_detection.get('content_types', [])
        self._callbacks: List[Callable] = []
        
    async def attach(self, page: Page) -> None:
        """Attach interceptor to page."""
        logger.debug("Attaching network interceptor...")
        page.on('response', self._handle_response)
        page.on('request', self._handle_request)
        logger.debug("Network interceptor attached")
        
    async def _handle_response(self, response: Response) -> None:
        """Handle response and identify API calls."""
        try:
            url = response.url
            if self._should_ignore(url) or not await self._is_api_response(response):
                return
            
            api_data = await self._extract_api_data(response)
            if api_data:
                self.captured_apis.append(api_data)
                logger.info(f"API found: {url} [{response.status}]")
                await self._trigger_callbacks(api_data)
                
        except Exception as e:
            logger.debug(f"Response handling failed: {e}")
    
    async def _handle_request(self, request: Request) -> None:
        """Handle request to extract auth headers."""
        try:
            headers = request.headers
            if 'authorization' in [h.lower() for h in headers.keys()]:
                logger.debug(f"Authorization header found: {request.url}")
        except Exception as e:
            logger.debug(f"Request handling failed: {e}")
    
    def _should_ignore(self, url: str) -> bool:
        """Check if URL should be ignored."""
        return any(re.match(pattern, url) for pattern in self.ignore_patterns)
    
    async def _is_api_response(self, response: Response) -> bool:
        """Identify if response is an API call."""
        try:
            content_type = response.headers.get('content-type', '').lower()
            if any(ct in content_type for ct in self.content_types):
                return True
            
            url = response.url.lower()
            api_patterns = ['/api/', '/v1/', '/v2/', '/v3/', '/graphql', '/rest/']
            return any(pattern in url for pattern in api_patterns)
            
        except Exception:
            return False
    
    async def _extract_api_data(self, response: Response) -> Optional[Dict[str, Any]]:
        """Extract API data from response."""
        try:
            body = await response.body()
            min_size = self.api_detection.get('min_json_size', 50)
            if len(body) < min_size:
                return None
            
            try:
                json_data = json.loads(body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'url': response.url,
                'method': response.request.method,
                'status': response.status,
                'headers': dict(response.headers),
                'request_headers': dict(response.request.headers),
                'response_body': json_data,
                'response_size': len(body),
                'content_type': response.headers.get('content-type', ''),
                'schema': self._infer_schema(json_data)
            }
            
        except Exception as e:
            logger.debug(f"API data extraction failed: {e}")
            return None
    
    def _infer_schema(self, data: Any, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        """Infer JSON data schema."""
        if current_depth >= max_depth:
            return {'type': 'truncated'}
        
        if isinstance(data, dict):
            return {
                'type': 'object',
                'properties': {
                    key: self._infer_schema(value, max_depth, current_depth + 1)
                    for key, value in data.items()
                }
            }
        elif isinstance(data, list):
            if not data:
                return {'type': 'array', 'items': {'type': 'unknown'}}
            return {
                'type': 'array',
                'items': self._infer_schema(data[0], max_depth, current_depth + 1),
                'length': len(data)
            }
        elif isinstance(data, str):
            return {'type': 'string'}
        elif isinstance(data, int):
            return {'type': 'integer'}
        elif isinstance(data, float):
            return {'type': 'number'}
        elif isinstance(data, bool):
            return {'type': 'boolean'}
        elif data is None:
            return {'type': 'null'}
        else:
            return {'type': 'unknown'}
    
    def add_callback(self, callback: Callable) -> None:
        """Add callback for API discovery."""
        self._callbacks.append(callback)
        logger.debug(f"Callback added (total: {len(self._callbacks)})")
    
    async def _trigger_callbacks(self, api_data: Dict[str, Any]) -> None:
        """Trigger all registered callbacks."""
        for callback in self._callbacks:
            try:
                await callback(api_data)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def get_captured_apis(self) -> List[Dict[str, Any]]:
        """Get all captured API calls."""
        return self.captured_apis
    
    def get_unique_endpoints(self) -> List[str]:
        """Get unique API endpoint URLs."""
        endpoints = set()
        for api in self.captured_apis:
            parsed = urlparse(api['url'])
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            endpoints.add(base_url)
        return sorted(list(endpoints))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get capture statistics."""
        total = len(self.captured_apis)
        unique_endpoints = len(self.get_unique_endpoints())
        
        methods = {}
        status_codes = {}
        
        for api in self.captured_apis:
            method = api['method']
            methods[method] = methods.get(method, 0) + 1
            status = api['status']
            status_codes[status] = status_codes.get(status, 0) + 1
        
        return {
            'total_apis': total,
            'unique_endpoints': unique_endpoints,
            'methods': methods,
            'status_codes': status_codes,
        }
    
    def clear(self) -> None:
        """Clear captured APIs."""
        self.captured_apis.clear()
        logger.debug("Captured APIs cleared")
