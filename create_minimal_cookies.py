#!/usr/bin/env python3
"""
Script para criar cookies.txt minificado apenas com cookies essenciais do Instagram.
Reduz de ~100 linhas para ~10 linhas (apenas cookies necessários).
"""

import os
import sys
from pathlib import Path

def create_minimal_instagram_cookies():
    """
    Cria arquivo cookies.txt minificado com apenas cookies essenciais.
    
    Use quando YTDLP_COOKIES_CONTENT for muito grande para variável de ambiente.
    """
    # Cookies essenciais do Instagram (configure esses valores)
    essential_cookies = {
        'sessionid': os.getenv('INSTAGRAM_SESSIONID', ''),
        'csrftoken': os.getenv('INSTAGRAM_CSRFTOKEN', ''),
        'ds_user_id': os.getenv('INSTAGRAM_DS_USER_ID', ''),
    }
    
    # Verifica se algum cookie essencial foi configurado
    if not any(essential_cookies.values()):
        print("⚠️  No Instagram cookies configured via environment variables")
        print("   Set: INSTAGRAM_SESSIONID, INSTAGRAM_CSRFTOKEN, INSTAGRAM_DS_USER_ID")
        return None
    
    # Formato Netscape cookies.txt
    output_dir = Path(__file__).parent / "temp_videos"
    output_dir.mkdir(exist_ok=True)
    
    cookies_file = output_dir / "cookies.txt"
    
    with open(cookies_file, 'w') as f:
        # Header obrigatório
        f.write("# Netscape HTTP Cookie File\n")
        f.write("# This is a generated file! Do not edit.\n\n")
        
        # Escreve apenas cookies essenciais
        # Formato: domain, flag, path, secure, expiration, name, value
        for name, value in essential_cookies.items():
            if value:  # Só escreve se tiver valor
                f.write(f".instagram.com\tTRUE\t/\tTRUE\t1999999999\t{name}\t{value}\n")
    
    print(f"✅ Created minimal cookies file: {cookies_file}")
    print(f"   Cookies configured: {', '.join(k for k, v in essential_cookies.items() if v)}")
    
    return str(cookies_file)


if __name__ == "__main__":
    create_minimal_instagram_cookies()
