#!/bin/bash

# TikTok OAuth2 Setup - Quick Start Script
# Este script facilita todo o processo de configuração

set -e

echo ""
echo "=========================================="
echo "  TIKTOK OAUTH2 - QUICK SETUP"
echo "=========================================="
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ Ngrok não está instalado!"
    echo ""
    echo "Instale com:"
    echo "  - Linux: curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo \"deb https://ngrok-agent.s3.amazonaws.com buster main\" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok"
    echo "  - macOS: brew install ngrok"
    echo ""
    exit 1
fi

echo "✅ Ngrok encontrado!"
echo ""

# Check if ngrok is already running
if pgrep -x "ngrok" > /dev/null; then
    echo "⚠️  Ngrok já está rodando!"
    echo ""
    echo "Para ver a URL atual, acesse: http://localhost:4040"
    echo ""
    read -p "Deseja parar o ngrok atual e iniciar um novo? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill ngrok
        echo "✅ Ngrok anterior parado"
        echo ""
    else
        echo "ℹ️  Continuando com ngrok existente..."
        echo ""
    fi
fi

# Start ngrok if not running
if ! pgrep -x "ngrok" > /dev/null; then
    echo "🚀 Iniciando ngrok na porta 8070..."
    echo ""
    
    # Start ngrok in background
    ngrok http 8070 > /dev/null 2>&1 &
    
    # Wait for ngrok to start
    sleep 3
    
    echo "✅ Ngrok iniciado!"
    echo ""
fi

# Get ngrok URL from API
echo "🔍 Obtendo URL do ngrok..."
echo ""

# Wait a bit more for ngrok to be fully ready
sleep 2

NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -n 1)

if [ -z "$NGROK_URL" ]; then
    echo "⚠️  Não foi possível obter a URL automaticamente"
    echo ""
    echo "📋 Por favor, acesse http://localhost:4040 no navegador"
    echo "   e copie a URL HTTPS manualmente"
    echo ""
    echo "   Exemplo: https://abc123xyz.ngrok.io"
    echo ""
    read -p "🌐 Cole a URL HTTPS do ngrok aqui: " NGROK_URL
    echo ""
    
    if [ -z "$NGROK_URL" ]; then
        echo "❌ URL não fornecida. Saindo..."
        exit 1
    fi
fi

echo "✅ URL do Ngrok:"
echo "   $NGROK_URL"
echo ""

# Show redirect URI
REDIRECT_URI="${NGROK_URL}/callback"
echo "📋 Redirect URI para TikTok Developer Portal:"
echo "   $REDIRECT_URI"
echo ""

# Copy to clipboard if possible
if command -v xclip &> /dev/null; then
    echo "$REDIRECT_URI" | xclip -selection clipboard
    echo "✅ Redirect URI copiada para área de transferência!"
    echo ""
elif command -v pbcopy &> /dev/null; then
    echo "$REDIRECT_URI" | pbcopy
    echo "✅ Redirect URI copiada para área de transferência!"
    echo ""
fi

echo "=========================================="
echo "  PRÓXIMOS PASSOS:"
echo "=========================================="
echo ""
echo "1. Acesse TikTok Developer Portal:"
echo "   https://developers.tiktok.com/"
echo ""
echo "2. Vá em: My Apps → Post Tiktok → Products → Login Kit"
echo ""
echo "3. Role até 'Redirect URI' e adicione:"
echo "   $REDIRECT_URI"
echo ""
echo "4. Clique em 'Apply changes' (botão vermelho)"
echo ""
echo "5. Aguarde a confirmação"
echo ""
echo "=========================================="
echo ""

read -p "Pressione Enter quando tiver configurado o Redirect URI no Developer Portal..."
echo ""

# Run OAuth setup
echo "🔐 Iniciando processo de autorização..."
echo ""

# Export ngrok URL for the Python script
export NGROK_URL="$NGROK_URL"

# Run Python OAuth script
.venv/bin/python setup_tiktok_oauth_server.py

# Check if token was created
if [ -f ".tiktok_token" ]; then
    echo ""
    echo "=========================================="
    echo "  ✅ AUTORIZAÇÃO COMPLETA!"
    echo "=========================================="
    echo ""
    echo "Token salvo em: .tiktok_token"
    echo ""
    echo "📝 Próximos passos:"
    echo ""
    echo "1. Ativar upload automático:"
    echo "   Edite .env e mude: TIKTOK_AUTO_UPLOAD=true"
    echo ""
    echo "2. Reiniciar o bot:"
    echo "   pkill -f link_downloader_bot.py"
    echo "   nohup .venv/bin/python -u bots/link_downloader_bot.py > link_downloader.log 2>&1 &"
    echo ""
    echo "3. Testar enviando um link no Telegram!"
    echo ""
    echo "=========================================="
    echo ""
else
    echo ""
    echo "❌ Token não foi criado. Algo deu errado."
    echo ""
    echo "Verifique os logs acima para mais detalhes."
    echo ""
fi
