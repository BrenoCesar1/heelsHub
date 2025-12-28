# AI Content Creator API

## 📖 Visão Geral

API REST para geração automatizada de vídeos com IA. Permite que o frontend envie ideias de vídeos, gerencie conceitos salvos e configure agendamentos automáticos.

## 🚀 Início Rápido

### Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais
```

### Iniciar Servidor

```bash
# Método 1: Script completo (API + Telegram Bot)
python run_api.py

# Método 2: Apenas API
python -m uvicorn api.main:app --host 0.0.0.0 --port 8070 --reload
```

### Acessar Documentação

- **Swagger UI**: http://localhost:8070/docs
- **ReDoc**: http://localhost:8070/redoc
- **Health Check**: http://localhost:8070/health

## 📚 Endpoints

### Health Check

#### `GET /health`
Verifica status da API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-26T10:30:00",
  "service": "AI Content Creator API",
  "version": "1.0.0"
}
```

---

### Geração de Vídeos

#### `POST /api/videos/generate`
Gera um vídeo a partir de uma ideia do usuário ou ideia salva.

**Request Body:**
```json
{
  "user_idea": "Um macaco da quebrada que é influencer e mostra seu dia dia na selva",
  "send_to_telegram": true,
  "post_to_tiktok": true,
  "idea_id": null
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Video generation started. Use task_id to check progress."
}
```

#### `GET /api/videos/status/{task_id}`
Verifica o status de uma geração de vídeo.

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "message": "Video generation completed successfully",
  "video_path": "/path/to/video.mp4"
}
```

**Status possíveis:**
- `pending` - Na fila
- `generating_script` - Gerando script com IA
- `generating_video` - Gerando vídeo com Veo
- `uploading` - Enviando para Telegram/TikTok
- `completed` - Concluído
- `failed` - Falhou

#### `GET /api/videos/tasks`
Lista todas as tarefas de geração de vídeo.

#### `DELETE /api/videos/tasks/{task_id}`
Remove uma tarefa do histórico.

---

### Gerenciamento de Ideias

#### `POST /api/ideas`
Salva uma nova ideia de vídeo.

**Request Body:**
```json
{
  "title": "Macaco Influencer da Selva",
  "description": "Um macaco da quebrada que é influencer digital e mostra seu dia a dia na selva de forma cômica",
  "tags": ["comédia", "animais", "selva"]
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Macaco Influencer da Selva",
  "description": "Um macaco da quebrada que é influencer digital...",
  "tags": ["comédia", "animais", "selva"],
  "created_at": "2025-12-26T10:30:00",
  "updated_at": "2025-12-26T10:30:00",
  "videos_generated": 0
}
```

#### `GET /api/ideas`
Lista todas as ideias salvas (ordenadas por data de criação).

#### `GET /api/ideas/{idea_id}`
Obtém uma ideia específica.

#### `PATCH /api/ideas/{idea_id}`
Atualiza uma ideia existente.

**Request Body:**
```json
{
  "title": "Novo título",
  "description": "Nova descrição",
  "tags": ["nova", "tags"]
}
```

#### `DELETE /api/ideas/{idea_id}`
Remove uma ideia.

#### `GET /api/ideas/random/pick`
Retorna uma ideia aleatória (útil para scheduler).

---

### Scheduler

#### `POST /api/scheduler/configure`
Configura horários e comportamento do scheduler.

**Request Body:**
```json
{
  "enabled": true,
  "schedule_times": [
    {"hour": 12, "minute": 0},
    {"hour": 19, "minute": 0}
  ],
  "use_saved_ideas": true,
  "idea_id": null
}
```

**Campos:**
- `enabled`: Ativa/desativa scheduler
- `schedule_times`: Lista de horários (formato 24h)
- `use_saved_ideas`: Se `true`, usa ideias salvas
- `idea_id`: ID de ideia específica (opcional, senão escolhe aleatória)

#### `GET /api/scheduler/status`
Retorna status atual do scheduler.

**Response:**
```json
{
  "enabled": true,
  "running": true,
  "schedule_times": ["12:00", "19:00"],
  "next_run": "2025-12-26T12:00:00",
  "last_run": "2025-12-25T19:00:00",
  "total_videos_generated": 42,
  "use_saved_ideas": true,
  "current_idea_id": null
}
```

#### `POST /api/scheduler/start`
Inicia o scheduler com configuração salva.

#### `POST /api/scheduler/stop`
Para o scheduler (cancela agendamentos).

#### `POST /api/scheduler/run-now`
Executa geração de vídeo imediatamente (teste).

---

## 🔄 Fluxo de Trabalho

### 1. Geração Manual de Vídeo

```bash
# Criar ideia
curl -X POST http://localhost:8070/api/ideas \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Macaco Fazendo Churrasco",
    "description": "Macaco preparando churrasco na laje da selva",
    "tags": ["comédia", "comida"]
  }'

# Gerar vídeo da ideia
curl -X POST http://localhost:8070/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_idea": "Macaco preparando churrasco na laje da selva",
    "send_to_telegram": true,
    "post_to_tiktok": true
  }'

# Verificar status
curl http://localhost:8070/api/videos/status/{task_id}
```

### 2. Configurar Geração Automática

```bash
# Configurar scheduler para usar ideias salvas
curl -X POST http://localhost:8070/api/scheduler/configure \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "schedule_times": [
      {"hour": 12, "minute": 0},
      {"hour": 18, "minute": 30}
    ],
    "use_saved_ideas": true
  }'

# Verificar status
curl http://localhost:8070/api/scheduler/status
```

### 3. Download de Vídeos por Link

O bot do Telegram continua funcionando independentemente:

1. Envie link de vídeo para @Tratormax_bot
2. Bot baixa, remove metadados
3. Envia no Telegram
4. Posta no TikTok (se configurado)

---

## 🏗️ Arquitetura

```
┌─────────────────┐
│   Frontend      │
│   (React/Vue)   │
└────────┬────────┘
         │
         │ HTTP REST
         ▼
┌─────────────────┐
│   FastAPI       │
│   (API Layer)   │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┐
    │         │              │
    ▼         ▼              ▼
┌────────┐ ┌──────┐  ┌────────────┐
│ Video  │ │Ideas │  │ Scheduler  │
│Service │ │Store │  │  Storage   │
└───┬────┘ └──────┘  └────────────┘
    │
    ├──► Screenwriter (Gemini AI)
    ├──► VideoGenerator (Veo 3.1)
    ├──► TelegramService
    └──► TikTokAPIService
```

---

## 📦 Storage

### Ideias
Salvas em: `temp_videos/ideas.json`

Estrutura:
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "tags": ["array"],
  "created_at": "datetime",
  "updated_at": "datetime",
  "videos_generated": 0
}
```

### Configuração do Scheduler
Salva em: `temp_videos/scheduler_config.json`

Estrutura:
```json
{
  "enabled": true,
  "schedule_times": ["12:00", "19:00"],
  "use_saved_ideas": false,
  "idea_id": null,
  "total_videos_generated": 0,
  "last_run": "datetime"
}
```

---

## 🔒 Segurança

### CORS
Atualmente configurado para aceitar todas as origens (`*`). 

**Produção:** Configure origins específicas em `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting
Considere adicionar rate limiting para produção:

```bash
pip install slowapi
```

---

## 🚀 Deploy

### Docker (Recomendado)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

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

## 📊 Monitoramento

### Logs

```bash
# Ver logs da API
tail -f logs/api.log

# Ver logs do Telegram Bot
tail -f logs/telegram_bot.log
```

### Métricas

Endpoints úteis para monitoramento:

- `GET /health` - Health check
- `GET /api/scheduler/status` - Status do scheduler
- `GET /api/videos/tasks` - Tarefas em execução

---

## 🐛 Troubleshooting

### API não inicia

```bash
# Verificar porta em uso
lsof -i :8070

# Verificar variáveis de ambiente
cat .env
```

### Scheduler não executa

```bash
# Verificar status
curl http://localhost:8070/api/scheduler/status

# Testar execução manual
curl -X POST http://localhost:8070/api/scheduler/run-now
```

### Geração de vídeo falha

```bash
# Verificar status da tarefa
curl http://localhost:8070/api/videos/status/{task_id}

# Verificar credenciais
# - Gemini API Key
# - TikTok Client Key/Secret
# - Telegram Bot Token
```

---

## 📝 Notas

- **Sandbox TikTok**: Atualmente usando credenciais sandbox (apenas contas privadas)
- **Storage**: JSON-based (considerar PostgreSQL para produção)
- **Task Queue**: In-memory (considerar Celery + Redis para produção)
- **Veo Multi-Account**: 4 contas rotativas para evitar rate limits

---

## 🔗 Links Úteis

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Gemini API](https://ai.google.dev/)
- [TikTok Content Posting API](https://developers.tiktok.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
