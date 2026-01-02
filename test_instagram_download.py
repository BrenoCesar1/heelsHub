#!/usr/bin/env python3
"""
Script de teste local para verificar download do Instagram com cookies.
Testa todas as opções de cookies sem precisar do bot Telegram.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from services.downloads.video_downloader_service import VideoDownloaderService


def test_instagram_download():
    """Testa download do Instagram com diferentes configurações de cookies."""
    
    # URL de teste (use um reel público real)
    test_url = "https://www.instagram.com/reel/DS-69HKR9I/"
    
    print("="*70)
    print("🧪 TESTE DE DOWNLOAD DO INSTAGRAM")
    print("="*70)
    print(f"\n📹 URL de teste: {test_url}\n")
    
    # Verificar qual método de cookies está configurado
    print("🔍 Verificando configuração de cookies:\n")
    
    has_minimal = bool(os.getenv('INSTAGRAM_SESSIONID'))
    has_content = bool(os.getenv('YTDLP_COOKIES_CONTENT'))
    has_file = bool(os.getenv('YTDLP_COOKIES_FILE'))
    
    if has_minimal:
        print("✅ INSTAGRAM_SESSIONID configurado (método minimalista - RECOMENDADO)")
        print(f"   Sessionid: {os.getenv('INSTAGRAM_SESSIONID')[:20]}...")
        if os.getenv('INSTAGRAM_CSRFTOKEN'):
            print(f"   CSRF Token: {os.getenv('INSTAGRAM_CSRFTOKEN')[:20]}...")
        if os.getenv('INSTAGRAM_DS_USER_ID'):
            print(f"   User ID: {os.getenv('INSTAGRAM_DS_USER_ID')}")
    
    if has_content:
        content_size = len(os.getenv('YTDLP_COOKIES_CONTENT', ''))
        print(f"⚠️  YTDLP_COOKIES_CONTENT configurado ({content_size} bytes)")
        if content_size > 5000:
            print("   ⚠️  AVISO: Muito grande para Render (pode causar erro)")
    
    if has_file:
        file_path = os.getenv('YTDLP_COOKIES_FILE')
        exists = Path(file_path).exists() if file_path else False
        print(f"{'✅' if exists else '❌'} YTDLP_COOKIES_FILE: {file_path}")
        if exists:
            size = Path(file_path).stat().st_size
            print(f"   Tamanho do arquivo: {size} bytes")
    
    if not (has_minimal or has_content or has_file):
        print("❌ NENHUM COOKIE CONFIGURADO!")
        print("\n⚠️  Downloads do Instagram FALHARÃO sem cookies.")
        print("\n💡 Configure uma dessas opções:")
        print("   export INSTAGRAM_SESSIONID='seu_valor_aqui'")
        print("   export YTDLP_COOKIES_FILE='temp_videos/cookies.txt'")
        return False
    
    print("\n" + "="*70)
    print("🚀 Iniciando teste de download...\n")
    
    try:
        # Criar downloader
        downloader = VideoDownloaderService()
        
        # Verificar se URL é suportada
        if not downloader.is_supported(test_url):
            print("❌ URL não é suportada!")
            return False
        
        platform = downloader.get_platform(test_url)
        print(f"✅ Plataforma detectada: {platform}")
        
        # Tentar download
        print("\n⬇️  Iniciando download...\n")
        video_info = downloader.download(test_url)
        
        if video_info:
            print("\n" + "="*70)
            print("✅ TESTE BEM-SUCEDIDO!")
            print("="*70)
            print(f"\n📁 Arquivo: {video_info.filepath}")
            print(f"📏 Tamanho: {video_info.size_mb:.2f} MB")
            print(f"⏱️  Duração: {video_info.duration}s")
            print(f"📝 Título: {video_info.title[:50]}...")
            if video_info.description:
                print(f"📄 Descrição: {video_info.description[:100]}...")
            
            # Limpar arquivo de teste
            try:
                video_info.filepath.unlink()
                print(f"\n🧹 Arquivo de teste removido")
            except:
                pass
            
            return True
        else:
            print("\n" + "="*70)
            print("❌ TESTE FALHOU - Download retornou None")
            print("="*70)
            return False
            
    except Exception as e:
        print("\n" + "="*70)
        print("❌ ERRO NO TESTE")
        print("="*70)
        print(f"\n{type(e).__name__}: {e}")
        
        import traceback
        print("\n📋 Traceback completo:")
        print(traceback.format_exc())
        
        return False


def show_cookie_extraction_guide():
    """Mostra como extrair cookies do navegador."""
    print("\n" + "="*70)
    print("📚 GUIA: Como extrair cookies do Instagram")
    print("="*70)
    
    print("""
1. Instale extensão do navegador:
   Chrome: "Get cookies.txt LOCALLY"
   https://chrome.google.com/webstore/detail/cclelndahbckbenkjhflpdbgdldlbecc

2. Faça login no Instagram

3. Exporte cookies.txt

4. Abra o arquivo e procure esta linha:
   .instagram.com	TRUE	/	TRUE	1234567890	sessionid	SEU_VALOR_AQUI

5. Configure localmente:
   export INSTAGRAM_SESSIONID='SEU_VALOR_AQUI'
   
   OU copie o arquivo completo:
   export YTDLP_COOKIES_FILE='temp_videos/cookies.txt'

6. Execute este teste novamente:
   python test_instagram_download.py
""")


if __name__ == "__main__":
    success = test_instagram_download()
    
    if not success:
        show_cookie_extraction_guide()
        sys.exit(1)
    
    print("\n✅ Tudo funcionando! Pronto para produção.")
    sys.exit(0)
