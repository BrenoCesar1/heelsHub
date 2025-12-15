"""Serviço Labs com rotação automática de múltiplas contas."""

import os
from typing import Optional, List
from dataclasses import dataclass
from pathlib import Path

from .labs_veo_service import LabsVeoService


@dataclass
class LabsAccount:
    """Representa uma conta Labs com sua API key."""
    email: str
    api_key: str
    videos_generated: int = 0
    credits_used: int = 0
    
    @property
    def credits_remaining(self) -> int:
        """Calcula créditos restantes (1000 por mês - 20 por vídeo)."""
        return 1000 - self.credits_used


class MultiAccountLabsService:
    """
    Gerencia múltiplas contas Labs com rotação automática.
    
    Features:
    - Rotação entre 4 contas Labs
    - Rastreamento de créditos por conta
    - Fallback automático quando conta atinge limite
    """
    
    CREDITS_PER_VIDEO = 20
    MAX_CREDITS_PER_ACCOUNT = 1000
    
    def __init__(self, accounts: Optional[List[LabsAccount]] = None):
        """
        Args:
            accounts: Lista de contas Labs (carrega do .env se None)
        """
        self.accounts = accounts or self._load_accounts_from_env()
        self.current_account_index = 0
        
        if not self.accounts:
            raise ValueError("Nenhuma conta Labs configurada. Configure LABS_API_KEY_1 no .env")
        
        print(f"🔧 MultiAccountLabsService inicializado com {len(self.accounts)} contas")
    
    def _load_accounts_from_env(self) -> List[LabsAccount]:
        """Carrega contas Labs do arquivo .env."""
        accounts = []
        
        # Emails identificadores das contas (para rastreamento)
        emails = [
            "account1@labs.google.com",
            "account2@labs.google.com",
            "account3@labs.google.com",
            "account4@labs.google.com",
        ]
        
        # API Keys das contas Labs
        for i in range(1, 5):
            api_key = os.getenv(f"LABS_API_KEY_{i}")
            if api_key:
                accounts.append(LabsAccount(
                    email=emails[i-1],
                    api_key=api_key
                ))
        
        return accounts
    
    def _get_current_account(self) -> LabsAccount:
        """Retorna a conta atual."""
        return self.accounts[self.current_account_index]
    
    def _rotate_account(self) -> bool:
        """
        Rotaciona para próxima conta com créditos disponíveis.
        
        Returns:
            True se encontrou conta válida, False se todas esgotaram
        """
        initial_index = self.current_account_index
        
        while True:
            self.current_account_index = (self.current_account_index + 1) % len(self.accounts)
            
            # Voltou ao início - verificou todas
            if self.current_account_index == initial_index:
                account = self.accounts[initial_index]
                if account.credits_remaining >= self.CREDITS_PER_VIDEO:
                    return True
                return False
            
            # Encontrou conta com créditos
            account = self.accounts[self.current_account_index]
            if account.credits_remaining >= self.CREDITS_PER_VIDEO:
                print(f"🔄 Rotacionando para conta: {account.email}")
                return True
    
    def generate_video(
        self,
        visual_prompt: str,
        audio_prompt: str,
        output_path: str
    ) -> Optional[str]:
        """
        Gera vídeo usando conta Labs atual.
        Rotaciona automaticamente se necessário.
        
        Args:
            visual_prompt: Prompt visual em inglês
            audio_prompt: Prompt de áudio
            output_path: Caminho de saída
            
        Returns:
            Caminho do vídeo ou None se falhar
        """
        account = self._get_current_account()
        
        # Verifica se tem créditos suficientes
        if account.credits_remaining < self.CREDITS_PER_VIDEO:
            print(f"⚠️  Conta {account.email} sem créditos suficientes")
            if not self._rotate_account():
                print("❌ Todas as contas Labs esgotaram os créditos!")
                return None
            account = self._get_current_account()
        
        print(f"🎬 Gerando vídeo com conta: {account.email}")
        print(f"   Créditos restantes: {account.credits_remaining}")
        
        try:
            # Cria serviço Labs para esta conta
            veo = LabsVeoService(api_key=account.api_key)
            
            # Gera vídeo
            video_path = veo.generate_video(
                visual_prompt=visual_prompt,
                audio_prompt=audio_prompt,
                output_path=output_path,
                aspect_ratio="9:16",
                duration_seconds=8
            )
            
            # Atualiza estatísticas
            account.videos_generated += 1
            account.credits_used += self.CREDITS_PER_VIDEO
            
            print(f"✅ Vídeo gerado! Conta {account.email} agora tem {account.credits_remaining} créditos")
            
            return video_path
            
        except Exception as e:
            print(f"❌ Erro ao gerar vídeo com {account.email}: {e}")
            
            # Tenta rotacionar e tentar novamente
            if "429" in str(e) or "quota" in str(e).lower():
                print(f"⚠️  Limite atingido, tentando próxima conta...")
                if self._rotate_account():
                    return self.generate_video(visual_prompt, audio_prompt, output_path)
            
            raise
    
    def print_stats(self):
        """Imprime estatísticas de uso das contas."""
        print("\n" + "="*60)
        print("📊 ESTATÍSTICAS DAS CONTAS LABS")
        print("="*60)
        
        total_videos = sum(acc.videos_generated for acc in self.accounts)
        total_credits_used = sum(acc.credits_used for acc in self.accounts)
        total_credits_remaining = sum(acc.credits_remaining for acc in self.accounts)
        
        print(f"Total de vídeos gerados: {total_videos}")
        print(f"Total de créditos usados: {total_credits_used}/{len(self.accounts) * self.MAX_CREDITS_PER_ACCOUNT}")
        print(f"Total de créditos restantes: {total_credits_remaining}")
        
        print(f"\n📋 Status por conta:")
        for i, acc in enumerate(self.accounts, 1):
            current = " ⭐ ATUAL" if i-1 == self.current_account_index else ""
            print(f"  {i}. {acc.email}{current}")
            print(f"     Vídeos gerados: {acc.videos_generated}")
            print(f"     Créditos usados: {acc.credits_used}/{self.MAX_CREDITS_PER_ACCOUNT}")
            print(f"     Créditos restantes: {acc.credits_remaining}")
        
        print("="*60 + "\n")
    
    def get_current_account_info(self) -> dict:
        """Retorna informações da conta atual."""
        current = self.accounts[self.current_account_index]
        return {
            'email': current.email,
            'videos_generated': current.videos_generated,
            'credits_used': current.credits_used,
            'credits_remaining': current.credits_remaining
        }


def create_multi_account_service() -> MultiAccountLabsService:
    """Helper para criar serviço multi-conta a partir do .env."""
    return MultiAccountLabsService()
