"""Google Labs Veo integration - usa créditos mensais do Labs."""

import os
import time
import base64
import requests
from pathlib import Path
from typing import Optional


class LabsVeoService:
    """
    Integração com Google Labs para geração de vídeos usando Veo.
    Usa os créditos mensais da sua conta Labs.
    """
    
    # Endpoints do Google Labs
    LABS_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: API key do Google AI Studio (mesma usada para Gemini)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY necessária (mesma key do Labs)")
    
    def generate_video(
        self, 
        visual_prompt: str, 
        audio_prompt: str,
        output_path: str,
        aspect_ratio: str = "9:16",
        duration_seconds: int = 8
    ) -> str:
        """
        Gera vídeo usando Veo via Google Labs API.
        
        Args:
            visual_prompt: Descrição visual em inglês
            audio_prompt: Descrição de áudio em português
            output_path: Caminho para salvar o vídeo
            aspect_ratio: Formato do vídeo (9:16 para vertical)
            duration_seconds: Duração do vídeo
            
        Returns:
            Caminho do arquivo de vídeo gerado
        """
        print(f"   > Gerando vídeo com Google Labs Veo 3.1...")
        
        # Combina prompts
        full_prompt = f"{visual_prompt}\n\nAudio description: {audio_prompt}"
        
        # Payload para Veo 3.1 Fast (SEM parâmetros de áudio - API ainda não suporta)
        payload = {
            "instances": [{
                "prompt": full_prompt
            }],
            "parameters": {
                "aspectRatio": aspect_ratio,
                "durationSeconds": duration_seconds,
                "personGeneration": "allow_all"
            }
        }
        
        # Usa Veo 3.1 Fast
        model = "veo-3.1-fast-generate-preview"
        url = f"{self.LABS_API_BASE}/models/{model}:predictLongRunning?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        print(f"   > Enviando requisição ao Labs ({model})...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code >= 400:
            print(f"   > Erro {response.status_code}: {response.text[:200]}")
        
        response.raise_for_status()
        data = response.json()
        
        # predictLongRunning retorna uma operação
        if "name" in data:
            operation_name = data["name"]
            print(f"   > Operação LRO iniciada: {operation_name}")
            return self._wait_for_operation(operation_name, output_path)
        
        raise RuntimeError(f"Resposta inesperada (sem 'name'): {list(data.keys())}")
    
    def _wait_for_operation(self, operation_name: str, output_path: str) -> str:
        """Aguarda operação assíncrona completar (polling)."""
        url = f"{self.LABS_API_BASE}/{operation_name}?key={self.api_key}"
        
        max_attempts = 60  # 5 minutos (5s * 60)
        
        for attempt in range(max_attempts):
            time.sleep(5)
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("done"):
                print(f"   > Vídeo gerado!")
                
                # Extrai vídeo da resposta
                if "response" in data:
                    resp = data["response"]
                    
                    # Formato 1: generateVideoResponse (novo formato Veo 3.1)
                    if "generateVideoResponse" in resp:
                        gen_resp = resp["generateVideoResponse"]
                        if "generatedSamples" in gen_resp and len(gen_resp["generatedSamples"]) > 0:
                            sample = gen_resp["generatedSamples"][0]
                            if "video" in sample and "uri" in sample["video"]:
                                download_url = sample["video"]["uri"]
                                print(f"   > Baixando vídeo...")
                                return self._download_video(download_url, output_path)
                    
                    # Formato 2: generatedSamples direto
                    if "generatedSamples" in resp and len(resp["generatedSamples"]) > 0:
                        sample = resp["generatedSamples"][0]
                        if "video" in sample and "uri" in sample["video"]:
                            download_url = sample["video"]["uri"]
                            print(f"   > Baixando vídeo...")
                            return self._download_video(download_url, output_path)
                    
                    # Formato 3: campo 'video' direto (base64)
                    if "video" in resp:
                        return self._save_video(resp["video"], output_path)
                    
                    # Formato 4: candidates
                    if "candidates" in resp:
                        video_data = resp["candidates"][0].get("content", {}).get("parts", [{}])[0]
                        if "videoData" in video_data:
                            return self._save_video(video_data["videoData"], output_path)
                
                # Erro na operação
                if "error" in data:
                    raise RuntimeError(f"Erro do Labs: {data['error']}")
                
                raise RuntimeError(f"Operação completa mas sem vídeo: {data}")
            
            print(f"   > Aguardando geração... ({attempt + 1}/{max_attempts})")
        
        raise TimeoutError("Timeout aguardando geração do vídeo no Labs")
    
    def _download_video(self, url: str, output_path: str) -> str:
        """Faz download do vídeo a partir de uma URL."""
        print(f"   > Baixando vídeo...")
        
        # A URL já tem :download?alt=media, só precisamos adicionar a key
        if "key=" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}key={self.api_key}"
        
        response = requests.get(url, timeout=120)
        
        if response.status_code != 200:
            print(f"   > Erro {response.status_code}: {response.text[:200]}")
        
        response.raise_for_status()
        
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(response.content)
        
        file_size = len(response.content) / 1024 / 1024
        print(f"   > ✓ Vídeo baixado: {output} ({file_size:.2f} MB)")
        
        return str(output)
    
    def _save_video(self, video_data: str, output_path: str) -> str:
        """Decodifica base64 e salva vídeo."""
        print(f"   > Decodificando vídeo...")
        
        # Remove prefixo data URL se presente
        if video_data.startswith("data:"):
            video_data = video_data.split(",", 1)[1]
        
        binary = base64.b64decode(video_data)
        
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(binary)
        
        file_size = len(binary) / 1024 / 1024
        print(f"   > ✓ Vídeo salvo: {output} ({file_size:.2f} MB)")
        
        return str(output)
