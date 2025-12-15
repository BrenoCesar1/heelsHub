"""
TikTok Uploader Service (Via Automação/Cookies).
Utiliza a biblioteca tiktok-uploader para simular um navegador real.
"""

from __future__ import annotations
import os
from typing import List, Optional
from tiktok_uploader.upload import upload_video

class TikTokUploader:
    def __init__(self):
        # Agora buscamos o SESSION_ID, não o Access Token
        self.session_id = os.getenv("TIKTOK_SESSION_ID")
        
        # Validação de segurança
        if not self.session_id:
            print("⚠️ AVISO: TIKTOK_SESSION_ID não encontrado no .env. O upload falhará.")

    def upload_video(self, file_path: str, title: str, hashtags: List[str]) -> bool:
        """
        Realiza o upload usando o cookie de sessão para autenticar.
        """
        
        if not self.session_id:
            raise ValueError("❌ Erro: Falta o TIKTOK_SESSION_ID no arquivo .env")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ Erro: Vídeo não encontrado no caminho: {file_path}")

        # Monta a legenda (Título + Hashtags)
        # O TikTok gosta de espaço entre o texto e as tags
        full_description = f"{title}\n\n{' '.join(hashtags)}"
        
        print(f"🚀 Iniciando upload automátizado para o TikTok...")
        print(f"📂 Arquivo: {file_path}")
        print(f"📝 Legenda: {title}")

        try:
            # Cria lista de cookies no formato esperado pela biblioteca
            cookies_list = [
                {
                    'name': 'sessionid',
                    'value': self.session_id,
                    'domain': '.tiktok.com',
                    'path': '/',
                    'secure': True,
                    'httpOnly': True
                }
            ]
            
            # O parâmetro 'headless=True' roda o navegador escondido.
            # Mude para 'headless=False' se quiser VER o robô abrindo o Chrome e clicando.
            failed_uploads = upload_video(
                filename=file_path,
                description=full_description,
                cookies_list=cookies_list,  # USA cookies_list ao invés de sessionid
                headless=True
            )

            # A biblioteca retorna uma lista de falhas. Se a lista for vazia, sucesso.
            if not failed_uploads:
                print("✅ Upload realizado com SUCESSO! O vídeo deve aparecer em instantes.")
                return True
            else:
                print("❌ O upload falhou. Verifique se o Cookie expirou.")
                return False

        except Exception as e:
            print(f"❌ Erro crítico durante a automação: {e}")
            return False