# AI Content Creator - Automated Video Generation Platform

🎬 **Plataforma completa de geração automatizada de vídeos com IA**, incluindo API REST, gerenciamento de ideias, scheduler configurável e integração com Telegram e TikTok.

---

## 🚀 Funcionalidades

### 🌐 API REST
- ✅ **Endpoints RESTful** para integração com frontend
- ✅ **Geração de vídeos** a partir de ideias do usuário
- ✅ **CRUD de ideias** para reutilização
- ✅ **Scheduler configurável** via API
- ✅ **Documentação automática** (Swagger + ReDoc)
- ✅ **CORS habilitado** para aplicações web

### 🤖 Geração de Vídeos com IA
- ✅ **Gemini 2.0 Flash**: Geração e aprimoramento de roteiros
- ✅ **Veo 3.1**: Geração profissional de vídeos
- ✅ **Multi-account**: 4 contas Veo em rotação
- ✅ **Scheduler**: Horários configuráveis para geração automática
- ✅ **Telegram**: Envio automático de vídeos gerados
- ✅ **TikTok API**: Post automático (OAuth2)

### 📥 Download de Vídeos
- ✅ **Suporte multiplataforma**: Instagram, TikTok, Facebook, YouTube, Twitter
- ✅ **Bot Telegram**: Envie link e receba o vídeo
- ✅ **Remoção de metadados**: ffmpeg para stealth mode
- ✅ **Extração de descrição**: Mantém contexto original
- ✅ **Upload automático**: Direto para TikTok após download
- ✅ **Suporte a cookies**: Bypass de rate-limits do Instagram
- ✅ **Anti-detecção**: User-agent e headers customizados

### ⚠️ Bloqueio do Instagram?
Se downloads do Instagram falharem com erro de rate-limit/login:
- 📚 **Veja guia completo**: [INSTAGRAM_COOKIES_GUIDE.md](INSTAGRAM_COOKIES_GUIDE.md)
- 🍪 **Solução rápida**: Exporte cookies do navegador e configure `YTDLP_COOKIES_FILE`

---

## 📁 Estrutura do Projeto

```
api/
├── main.py                          # FastAPI application
├── models/                          # Pydantic models
│   ├── video.py                     # Video generation models
│   ├── idea.py                      # Idea management models
│   └── scheduler.py                 # Scheduler configuration models
└── routes/                          # API endpoints
    ├── health.py                    # Health check
    ├── videos.py                    # Video generation endpoints
    ├── ideas.py                     # Idea management endpoints
    └── scheduler.py                 # Scheduler control endpoints

bots/
├── content_creator_bot.py           # Legacy standalone bot
└── link_downloader_bot.py           # Telegram video downloader

services/
├── ai/
│   ├── screenwriter.py              # AI script generation (Gemini)
│   └── marketer.py                  # Marketing content generation
├── video_generation/
│   ├── video_generation_service.py  # Core video generation service
│   ├── labs_veo_service.py          # Google Veo integration
│   ├── multi_account_labs_service.py # Multi-account rotation
│   └── video_generator.py           # Video generator orchestrator
├── integrations/
│   ├── telegram_service.py          # Telegram Bot API
│   └── tiktok_api_service.py        # TikTok Content Posting API
└── downloads/
    └── video_downloader_service.py  # Multi-platform video downloader

storage/
├── ideas_storage.py                 # JSON-based idea storage
└── scheduler_storage.py             # Scheduler configuration storage

config.py                            # Configuration settings
run_api.py                           # Start all services
requirements.txt                     # Python dependencies
```

---

## 🎮 Início Rápido

### Instalação

```bash
# 1. Clonar repositório
git clone <repo-url>
cd "Post Tiktok"

# 2. Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
nano .env  # Adicionar suas credenciais
```

### Configuração (.env)

```bash
# AI Services
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp

# Veo Accounts (4 accounts for rotation)
VEO_ACCOUNT_1_USERNAME=email1@gmail.com
VEO_ACCOUNT_1_PASSWORD=password1
VEO_ACCOUNT_2_USERNAME=email2@gmail.com
VEO_ACCOUNT_2_PASSWORD=password2
VEO_ACCOUNT_3_USERNAME=email3@gmail.com
VEO_ACCOUNT_3_PASSWORD=password3
VEO_ACCOUNT_4_USERNAME=email4@gmail.com
VEO_ACCOUNT_4_PASSWORD=password4

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# TikTok API
TIKTOK_CLIENT_KEY=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret
TIKTOK_AUTO_UPLOAD=true

# Video Downloader (opcional - para Instagram rate-limits)
YTDLP_COOKIES_FILE=temp_videos/cookies.txt
```

> **💡 Dica:** Se downloads do Instagram falharem, veja [INSTAGRAM_COOKIES_GUIDE.md](INSTAGRAM_COOKIES_GUIDE.md)

### Iniciar Sistema Completo

```bash
# Inicia API + Link Downloader Bot
python run_api.py
```

Ou iniciar serviços separadamente:

```bash
# Apenas API
python -m uvicorn api.main:app --host 0.0.0.0 --port 8070 --reload

# Apenas Link Downloader Bot
python bots/link_downloader_bot.py
```

### Acessar Documentação

- **Swagger UI**: http://localhost:8070/docs
- **ReDoc**: http://localhost:8070/redoc
- **Health Check**: http://localhost:8070/health

---

## 📚 Endpoints da API

### Health Check

```bash
GET /health
```

### Vídeos

```bash
# Gerar vídeo a partir de ideia
POST /api/videos/generate
{
  "user_idea": "Um macaco da quebrada que é influencer",
  "send_to_telegram": true,
  "post_to_tiktok": true
}

# Verificar status de geração
GET /api/videos/status/{task_id}

# Listar todas as tarefas
GET /api/videos/tasks

# Remover tarefa do histórico
DELETE /api/videos/tasks/{task_id}
```

### Ideias

```bash
# Criar ideia
POST /api/ideas
{
  "title": "Macaco Influencer",
  "description": "Um macaco da quebrada que mostra seu dia a dia",
  "tags": ["comédia", "animais"]
}

# Listar ideias
GET /api/ideas

# Obter ideia específica
GET /api/ideas/{idea_id}

# Atualizar ideia
PATCH /api/ideas/{idea_id}

# Deletar ideia
DELETE /api/ideas/{idea_id}

# Obter ideia aleatória
GET /api/ideas/random/pick
```

### Scheduler

```bash
# Configurar scheduler
POST /api/scheduler/configure
{
  "enabled": true,
  "schedule_times": [
    {"hour": 12, "minute": 0},
    {"hour": 19, "minute": 0}
  ],
  "use_saved_ideas": true,
  "idea_id": null
}

# Ver status do scheduler
GET /api/scheduler/status

# Iniciar scheduler
POST /api/scheduler/start

# Parar scheduler
POST /api/scheduler/stop

# Executar agora (teste)
POST /api/scheduler/run-now
```

---

## 🔄 Fluxos de Trabalho

### 1. Geração Manual via API

```bash
# 1. Criar ideia
curl -X POST http://localhost:8070/api/ideas \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Macaco no Churrasco",
    "description": "Macaco preparando churrasco na laje da selva",
    "tags": ["comédia", "comida"]
  }'

# 2. Gerar vídeo
curl -X POST http://localhost:8070/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_idea": "Macaco preparando churrasco na laje",
    "send_to_telegram": true,
    "post_to_tiktok": true
  }'

# 3. Verificar status
curl http://localhost:8070/api/videos/status/{task_id}
```

### 2. Scheduler Automático

```bash
# 1. Salvar várias ideias
# (usar POST /api/ideas)

# 2. Configurar scheduler
curl -X POST http://localhost:8070/api/scheduler/configure \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "schedule_times": [{"hour": 12, "minute": 0}],
    "use_saved_ideas": true
  }'

# Scheduler vai:
# - Pegar ideia aleatória
# - Gerar vídeo
# - Enviar no Telegram
# - Postar no TikTok
# - Incrementar contador da ideia
```

### 3. Download via Telegram

1. Enviar link para @Tratormax_bot
2. Bot baixa o vídeo
3. Remove metadados
4. Envia no Telegram
5. Posta no TikTok (opcional)

---

## 🛠️ Tecnologias

- **FastAPI**: Framework web moderno e rápido
- **Pydantic**: Validação de dados com type hints
- **Uvicorn**: Servidor ASGI de alta performance
- **Google Gemini AI**: Geração de roteiros
- **Google Veo 3.1**: Geração de vídeos
- **yt-dlp**: Download de vídeos multiplataforma
- **ffmpeg**: Processamento e remoção de metadados
- **python-telegram-bot**: Integração Telegram
- **Schedule**: Agendamento de tarefas

---

## 📊 Monitoramento

```bash
# Health check
curl http://localhost:8070/health

# Status do scheduler
curl http://localhost:8070/api/scheduler/status

# Tarefas em execução
curl http://localhost:8070/api/videos/tasks
```

---

## 🐛 Troubleshooting

### API não inicia

```bash
# Verificar porta
lsof -i :8070

# Verificar .env
cat .env
```

### Scheduler não executa

```bash
# Ver status
curl http://localhost:8070/api/scheduler/status

# Testar execução manual
curl -X POST http://localhost:8070/api/scheduler/run-now
```

### Vídeo não gera

1. Verificar credenciais Gemini e Veo
2. Verificar rate limits
3. Ver status da tarefa via API
4. Checar logs do servidor

---

## 📖 Documentação Adicional

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Documentação completa da API
- [SETUP_TIKTOK_NGROK.md](SETUP_TIKTOK_NGROK.md) - Setup OAuth TikTok
- [GUIA_TIKTOK_UPLOAD.md](GUIA_TIKTOK_UPLOAD.md) - Guia de upload TikTok

---

## 🚀 Deploy

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8070

CMD ["python", "run_api.py"]
```

```bash
docker build -t ai-content-creator .
docker run -p 8070:8070 --env-file .env ai-content-creator
```

### Systemd Service

```ini
[Unit]
Description=AI Content Creator API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ai-content-creator
ExecStart=/opt/ai-content-creator/.venv/bin/python run_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 📝 Limitações Atuais

- **TikTok Sandbox**: Credenciais sandbox (apenas contas privadas)
- **Storage**: JSON-based (considerar PostgreSQL para produção)
- **Task Queue**: In-memory (considerar Celery + Redis para produção)

---

## 🤝 Contribuindo

Pull requests são bem-vindos! Para mudanças importantes, abra uma issue primeiro.

---

## 📄 Licença

MIT
