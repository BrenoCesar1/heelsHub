# Fix: Render Deployment Error

## Problema Identificado

O deploy no Render estava falhando com o seguinte erro:

```
ValueError: Nenhuma conta Labs configurada. Configure LABS_API_KEY_1 no .env
```

### Causa Raiz

O erro ocorria porque os serviços `VideoGenerationService` e `MultiAccountLabsService` eram **inicializados durante a importação do módulo** (nível global), antes mesmo da API começar a rodar:

```python
# ❌ ANTES - Inicialização no nível do módulo
_video_service = VideoGenerationService()  # Executado durante import
```

Quando o Uvicorn tentava carregar a aplicação FastAPI, ele importava todos os módulos, e o `MultiAccountLabsService` verificava se as chaves Labs existiam. Como no Render você não tem essas chaves configuradas (porque não está usando geração de vídeo), a aplicação falhava **antes mesmo de iniciar**.

## Solução Implementada

### 1. Lazy Initialization (Inicialização Preguiçosa)

Mudamos para criar os serviços **apenas quando forem realmente usados**:

**Arquivo: `api/routes/videos.py`**
```python
# ✅ DEPOIS - Inicialização lazy
_video_service: VideoGenerationService = None
_ideas_storage: IdeasStorage = None

def _get_video_service() -> VideoGenerationService:
    """Get or create video service instance (lazy initialization)."""
    global _video_service
    if _video_service is None:
        _video_service = VideoGenerationService()
    return _video_service

def _get_ideas_storage() -> IdeasStorage:
    """Get or create ideas storage instance (lazy initialization)."""
    global _ideas_storage
    if _ideas_storage is None:
        _ideas_storage = IdeasStorage()
    return _ideas_storage
```

Agora, em vez de usar `_video_service.method()`, usamos `_get_video_service().method()`.

### 2. Tolerância no MultiAccountLabsService

**Arquivo: `services/video_generation/multi_account_labs_service.py`**

**ANTES:**
```python
def __init__(self, accounts: Optional[List[LabsAccount]] = None):
    self.accounts = accounts or self._load_accounts_from_env()
    
    if not self.accounts:
        raise ValueError("Nenhuma conta Labs configurada...")  # ❌ Erro na inicialização
```

**DEPOIS:**
```python
def __init__(self, accounts: Optional[List[LabsAccount]] = None):
    self.accounts = accounts or self._load_accounts_from_env()
    
    if not self.accounts:
        # ✅ Apenas aviso - não bloqueia a inicialização
        print("⚠️  MultiAccountLabsService: Nenhuma conta Labs configurada")
        print("   Configure LABS_API_KEY_1 no .env para usar geração de vídeo")
    else:
        print(f"🔧 MultiAccountLabsService inicializado com {len(self.accounts)} contas")

def generate_video(...):
    # ✅ Validação só acontece quando tentar gerar vídeo
    if not self.accounts:
        raise ValueError(
            "Nenhuma conta Labs configurada. "
            "Configure LABS_API_KEY_1 no .env para usar geração de vídeo"
        )
    # ... resto do código
```

## Benefícios

### ✅ API Inicia Mesmo Sem LABS_API_KEY

Agora a API pode iniciar no Render **sem** as chaves Labs configuradas:
- Endpoints de **health check** funcionam ✅
- Endpoints de **ideas** funcionam ✅  
- Endpoints de **scheduler** funcionam ✅
- Apenas o endpoint de **geração de vídeo** retornará erro se tentar usar sem as chaves

### ✅ Melhor Performance

Os serviços pesados só são inicializados quando realmente necessários, reduzindo o tempo de startup da aplicação.

### ✅ Melhor Tratamento de Erros

Erros são mais específicos e acontecem no momento certo:
- **Antes**: Erro genérico durante o startup
- **Agora**: Erro específico quando tentar gerar vídeo sem credenciais

## Como Testar no Render

1. **Deploy deve funcionar agora** ✅
   ```bash
   # O Render conseguirá iniciar a API sem LABS_API_KEY
   ```

2. **Health Check deve responder** ✅
   ```bash
   curl https://seu-app.onrender.com/health
   # Retorna: {"status": "healthy", ...}
   ```

3. **Documentação deve abrir** ✅
   ```
   https://seu-app.onrender.com/docs
   ```

4. **Endpoints de Ideas devem funcionar** ✅
   ```bash
   curl https://seu-app.onrender.com/api/ideas
   ```

5. **Endpoint de geração de vídeo retornará erro apropriado** ✅
   ```bash
   # Se tentar gerar vídeo sem LABS_API_KEY
   # Retorna: 500 com mensagem clara sobre falta de configuração
   ```

## Para Usar Geração de Vídeo no Render

Se futuramente quiser usar a geração de vídeo no Render, basta:

1. Ir em **Dashboard > Environment**
2. Adicionar variáveis:
   ```
   LABS_API_KEY_1=sua_chave_aqui
   LABS_EMAIL_1=seu_email_aqui
   ```
3. Fazer redeploy

## Commit

```bash
git add .
git commit -m "fix: implement lazy initialization for video services

- Changed VideoGenerationService and IdeasStorage to use lazy initialization
- MultiAccountLabsService now warns instead of raising error on init
- Validation moved to generate_video() method when actually needed
- Fixes Render deployment error about missing LABS_API_KEY
- Allows API to start even without LABS_API_KEY (other endpoints work)"

git push
```

## Status

✅ **Problema Resolvido**
- API pode iniciar sem LABS_API_KEY
- Deploy no Render deve funcionar
- Outros endpoints funcionam normalmente
- Geração de vídeo só falha quando realmente tentar usar
