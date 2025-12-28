"""
TikTok OAuth2 Authorization Server
Simple HTTP server to receive OAuth callback from TikTok.
"""

import os
import sys
import webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from services.integrations.tiktok_api_service import TikTokAPIService

load_dotenv()


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""
    
    auth_code = None
    
    def do_GET(self):
        """Handle GET request from TikTok redirect."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/callback':
            # Extract authorization code from query params
            query_params = parse_qs(parsed_path.query)
            code = query_params.get('code', [None])[0]
            
            if code:
                OAuthCallbackHandler.auth_code = code
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>TikTok Authorization</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }
                        .container {
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                            text-align: center;
                            max-width: 500px;
                        }
                        h1 { color: #333; margin-bottom: 20px; }
                        p { color: #666; font-size: 16px; line-height: 1.6; }
                        .success { color: #00c853; font-size: 60px; margin-bottom: 20px; }
                        .code {
                            background: #f5f5f5;
                            padding: 10px;
                            border-radius: 5px;
                            font-family: monospace;
                            word-break: break-all;
                            margin: 20px 0;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success">✅</div>
                        <h1>Autorização Bem-Sucedida!</h1>
                        <p>Seu app foi autorizado com sucesso no TikTok.</p>
                        <p><strong>Código recebido:</strong></p>
                        <div class="code">{code}</div>
                        <p>Você pode fechar esta página e voltar ao terminal.</p>
                        <p style="margin-top: 30px; color: #999; font-size: 14px;">
                            O bot está processando o token de acesso...
                        </p>
                    </div>
                </body>
                </html>
                """.format(code=code[:20] + '...')
                
                self.wfile.write(html.encode('utf-8'))
                
            else:
                # No code received
                self.send_response(400)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>TikTok Authorization - Error</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        }
                        .container {
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                            text-align: center;
                            max-width: 500px;
                        }
                        h1 { color: #333; margin-bottom: 20px; }
                        p { color: #666; font-size: 16px; line-height: 1.6; }
                        .error { color: #ff1744; font-size: 60px; margin-bottom: 20px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="error">❌</div>
                        <h1>Erro na Autorização</h1>
                        <p>Não foi possível obter o código de autorização.</p>
                        <p>Por favor, tente novamente.</p>
                    </div>
                </body>
                </html>
                """
                
                self.wfile.write(html.encode('utf-8'))
        else:
            # Unknown path
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def run_oauth_flow(redirect_uri: str):
    """
    Run complete OAuth flow with HTTP server.
    
    Args:
        redirect_uri: Redirect URI (ngrok URL + /callback)
    """
    print("\n🔐 TIKTOK API AUTHORIZATION")
    print("=" * 70)
    
    # Initialize service
    service = TikTokAPIService()
    
    # Generate authorization URL
    auth_url = service.get_authorization_url(redirect_uri)
    
    print(f"\n📱 Step 1: Opening TikTok authorization in browser...")
    print(f"   URL: {auth_url[:80]}...")
    
    # Start HTTP server
    port = int(urlparse(redirect_uri).port or 8070)
    server = HTTPServer(('0.0.0.0', port), OAuthCallbackHandler)
    
    print(f"\n🌐 Step 2: HTTP server started on port {port}")
    print(f"   Waiting for TikTok callback...")
    print(f"\n💡 If browser doesn't open automatically, copy this URL:")
    print(f"   {auth_url}")
    
    # Open browser
    try:
        webbrowser.open(auth_url)
    except:
        print(f"\n⚠️  Could not open browser automatically")
    
    # Wait for callback
    print(f"\n⏳ Listening for authorization callback...")
    print(f"   Press Ctrl+C to cancel\n")
    
    try:
        # Handle one request (the callback)
        server.handle_request()
        
        # Check if we got the code
        if OAuthCallbackHandler.auth_code:
            code = OAuthCallbackHandler.auth_code
            
            print(f"\n✅ Authorization code received!")
            print(f"   Code: {code[:20]}...")
            
            # Exchange code for token
            print(f"\n🔄 Step 3: Exchanging code for access token...")
            
            if service.exchange_code_for_token(code, redirect_uri):
                print(f"\n" + "=" * 70)
                print(f"🎉 AUTHORIZATION COMPLETE!")
                print(f"=" * 70)
                print(f"\n✅ Access token saved to .tiktok_token")
                print(f"\n📝 Next steps:")
                print(f"   1. Edit .env: TIKTOK_AUTO_UPLOAD=true")
                print(f"   2. Restart bot: pkill -f link_downloader_bot.py && \\")
                print(f"                   nohup .venv/bin/python -u bots/link_downloader_bot.py > link_downloader.log 2>&1 &")
                print(f"   3. Test by sending a video link to the bot!")
                print(f"\n🚀 Ready to upload to TikTok automatically!")
                print(f"=" * 70 + "\n")
                return True
            else:
                print(f"\n❌ Failed to exchange code for token")
                return False
        else:
            print(f"\n❌ No authorization code received")
            return False
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Authorization cancelled by user")
        return False
    finally:
        server.server_close()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  TIKTOK OAUTH2 AUTHORIZATION SETUP")
    print("=" * 70)
    
    # Check if ngrok URL is provided via environment variable
    ngrok_url = os.getenv('NGROK_URL', '').strip()
    
    if not ngrok_url:
        # Get ngrok URL from user
        print(f"\n📋 Enter your ngrok URL (from TikTok Developer Portal):")
        print(f"   Example: https://abc123.ngrok.io")
        print(f"   Or just press Enter to use localhost (if configured)")
        
        ngrok_url = input(f"\n🌐 Ngrok URL: ").strip()
    else:
        print(f"\n✅ Using ngrok URL from environment: {ngrok_url}")
    
    if ngrok_url:
        redirect_uri = f"{ngrok_url}/callback"
    else:
        redirect_uri = "http://localhost:8070/callback"
    
    print(f"\n✅ Using redirect URI: {redirect_uri}")
    print(f"\n⚠️  IMPORTANT: Make sure this URL is configured in TikTok Developer Portal!")
    print(f"   Go to: Products > Login Kit > Redirect URI")
    print(f"   Add: {redirect_uri}")
    
    input(f"\n   Press Enter when ready to continue...")
    
    # Run OAuth flow
    success = run_oauth_flow(redirect_uri)
    
    sys.exit(0 if success else 1)
