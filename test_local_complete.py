#!/usr/bin/env python3
"""
Test local completo para verificar duplicação e downloads.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

print("="*70)
print("🧪 TESTE LOCAL COMPLETO - Bot + Downloads")
print("="*70)

# ============================================
# Teste 1: Configuração de Cookies
# ============================================
print("\n📋 TESTE 1: Verificação de Cookies")
print("-"*70)

has_cookies = False
cookie_method = None

# Método 1: Variáveis individuais (prioridade)
sessionid = os.getenv("INSTAGRAM_SESSIONID")
csrftoken = os.getenv("INSTAGRAM_CSRFTOKEN")
ds_user_id = os.getenv("INSTAGRAM_DS_USER_ID")

if sessionid and csrftoken and ds_user_id:
    has_cookies = True
    cookie_method = "Variáveis de ambiente (INSTAGRAM_*)"
    print(f"✅ {cookie_method}")
    print(f"   sessionid: {sessionid[:20]}..." if len(sessionid) > 20 else f"   sessionid: {sessionid}")
    print(f"   csrftoken: {csrftoken[:20]}..." if len(csrftoken) > 20 else f"   csrftoken: {csrftoken}")
    print(f"   ds_user_id: {ds_user_id}")
else:
    # Método 2: Arquivo
    cookies_file = os.getenv("YTDLP_COOKIES_FILE", "temp_videos/cookies.txt")
    if Path(cookies_file).exists():
        has_cookies = True
        cookie_method = f"Arquivo: {cookies_file}"
        print(f"✅ {cookie_method}")
        size = Path(cookies_file).stat().st_size
        print(f"   Tamanho: {size} bytes")
    else:
        print(f"❌ Nenhum método de cookies configurado")
        print(f"\n💡 Configure cookies primeiro:")
        print(f"   export INSTAGRAM_SESSIONID='seu_sessionid'")
        print(f"   export INSTAGRAM_CSRFTOKEN='seu_csrftoken'")
        print(f"   export INSTAGRAM_DS_USER_ID='seu_ds_user_id'")
        print(f"\nOu crie: {cookies_file}")

# ============================================
# Teste 2: Download de Vídeo
# ============================================
if has_cookies:
    print(f"\n📹 TESTE 2: Download de Vídeo do Instagram")
    print("-"*70)
    
    from services.downloads.video_downloader_service import VideoDownloaderService
    
    test_url = "https://www.instagram.com/reel/DS-69HKR9I/"
    print(f"🔗 URL de teste: {test_url}")
    
    downloader = VideoDownloaderService()
    
    print(f"⬇️  Baixando...")
    video_info = downloader.download(test_url)
    
    if video_info:
        print(f"\n✅ DOWNLOAD BEM-SUCEDIDO!")
        print(f"   📁 Arquivo: {video_info.filepath}")
        print(f"   📏 Tamanho: {video_info.size_mb:.2f} MB")
        print(f"   ⏱️  Duração: {video_info.duration}s")
        print(f"   🏷️  Título: {video_info.title[:50]}...")
        
        # Cleanup
        if video_info.filepath.exists():
            video_info.filepath.unlink()
            print(f"   🧹 Arquivo removido após teste")
    else:
        print(f"\n❌ DOWNLOAD FALHOU")
        print(f"   Verifique logs acima para detalhes do erro")
        sys.exit(1)

# ============================================
# Teste 3: Bot do Telegram (Duplicação)
# ============================================
print(f"\n🤖 TESTE 3: Bot do Telegram (Verificar Duplicação)")
print("-"*70)

telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
telegram_chat = os.getenv("TELEGRAM_CHAT_ID")

if not telegram_token or not telegram_chat:
    print("⚠️  TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurados")
    print("   Pulando teste do bot")
else:
    print("✅ Tokens do Telegram configurados")
    print(f"   Chat ID: {telegram_chat}")
    
    print(f"\n📝 INSTRUÇÕES PARA TESTE MANUAL:")
    print(f"   1. Execute: python run_api.py")
    print(f"   2. Aguarde mensagem: '🤖 Telegram Link Downloader Bot: ENABLED'")
    print(f"   3. Envie NO TELEGRAM esta mensagem:")
    print(f"      'Teste {test_url if has_cookies else 'https://www.tiktok.com/@username/video/123'}'")
    print(f"   4. CONTE quantas respostas você recebe:")
    print(f"      - ✅ 1 resposta = OK")
    print(f"      - ❌ 2+ respostas = DUPLICAÇÃO CONFIRMADA")
    print(f"\n   5. Verifique nos logs:")
    print(f"      grep '📩 \\[Bot\\] New message' | wc -l")
    print(f"      Deve aparecer 1 vez para cada mensagem enviada")

# ============================================
# Teste 4: Verificar processos duplicados
# ============================================
print(f"\n🔍 TESTE 4: Processos Python em Execução")
print("-"*70)

import subprocess
result = subprocess.run(
    ["ps", "aux"],
    capture_output=True,
    text=True
)

python_procs = [
    line for line in result.stdout.split('\n')
    if 'python' in line.lower()
    and 'run_api' in line or 'link_downloader' in line or 'main.py' in line
]

if not python_procs:
    print("✅ Nenhum processo da API ou bot rodando no momento")
else:
    print(f"⚠️  Processos encontrados:")
    for proc in python_procs:
        # Extrair info relevante
        parts = proc.split()
        if len(parts) > 10:
            pid = parts[1]
            cmd = ' '.join(parts[10:])
            print(f"   PID {pid}: {cmd}")

# ============================================
# Resumo
# ============================================
print(f"\n" + "="*70)
print("📊 RESUMO DOS TESTES")
print("="*70)

print(f"\n✅ Testes Automáticos Completados:")
print(f"   1. Cookies: {'✅ Configurados (' + cookie_method + ')' if has_cookies else '❌ Não configurados'}")
if has_cookies:
    print(f"   2. Download: {'✅ Funcionando' if video_info else '❌ Falhou'}")
print(f"   3. Telegram: {'✅ Configurado' if telegram_token and telegram_chat else '❌ Não configurado'}")

print(f"\n⏭️  PRÓXIMOS PASSOS:")

if not has_cookies:
    print(f"   1. Configure cookies do Instagram (veja instruções acima)")
    print(f"   2. Execute novamente: python test_local_complete.py")
elif telegram_token and telegram_chat:
    print(f"   1. Inicie a API: python run_api.py")
    print(f"   2. Envie 1 mensagem no Telegram")
    print(f"   3. Verifique se recebe apenas 1 resposta (não duplicada)")
    print(f"   4. Se duplicar, consulte: TELEGRAM_DUPLICATION_DEBUG.md")
else:
    print(f"   1. Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env")
    print(f"   2. Execute novamente: python test_local_complete.py")

print(f"\n📖 Documentação:")
print(f"   - CHECKLIST_PRE_PRODUCTION.md")
print(f"   - TELEGRAM_DUPLICATION_DEBUG.md")
print(f"   - INSTAGRAM_COOKIES_GUIDE.md")

print(f"\n" + "="*70)
