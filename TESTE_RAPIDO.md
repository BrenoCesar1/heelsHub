# Guia de Teste Rápido - API

Este guia mostra como testar a API após a instalação.

## 1. Iniciar API

```bash
# Terminal 1: Iniciar sistema completo
python run_api.py

# OU iniciar apenas a API
python -m uvicorn api.main:app --reload
```

Aguarde a mensagem: `✅ API is ready`

## 2. Testar Health Check

```bash
curl http://localhost:8070/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-26T...",
  "service": "AI Content Creator API",
  "version": "1.0.0"
}
```

## 3. Acessar Documentação

Abra no navegador:
- **Swagger UI**: http://localhost:8070/docs
- **ReDoc**: http://localhost:8070/redoc

## 4. Criar uma Ideia

```bash
curl -X POST http://localhost:8070/api/ideas \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Teste - Macaco no Skate",
    "description": "Um macaco da quebrada andando de skate pela selva",
    "tags": ["teste", "comédia"]
  }'
```

**Resposta esperada:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Teste - Macaco no Skate",
  "description": "Um macaco da quebrada andando de skate pela selva",
  "tags": ["teste", "comédia"],
  "created_at": "2025-12-26T...",
  "updated_at": "2025-12-26T...",
  "videos_generated": 0
}
```

Salve o `id` retornado!

## 5. Listar Ideias

```bash
curl http://localhost:8070/api/ideas
```

## 6. Configurar Scheduler

```bash
curl -X POST http://localhost:8070/api/scheduler/configure \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false,
    "schedule_times": [
      {"hour": 12, "minute": 0}
    ],
    "use_saved_ideas": true,
    "idea_id": null
  }'
```

> **Nota:** `enabled: false` para não executar automaticamente durante testes

## 7. Ver Status do Scheduler

```bash
curl http://localhost:8070/api/scheduler/status
```

**Resposta esperada:**
```json
{
  "enabled": false,
  "running": false,
  "schedule_times": ["12:00"],
  "next_run": null,
  "last_run": null,
  "total_videos_generated": 0,
  "use_saved_ideas": true,
  "current_idea_id": null
}
```

## 8. Gerar Vídeo (OPCIONAL - Requer Credenciais)

⚠️ **Atenção:** Este teste irá:
- Consumir créditos da API Gemini
- Usar uma conta Veo
- Enviar para Telegram (se configurado)
- Postar no TikTok (se configurado)

```bash
curl -X POST http://localhost:8070/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_idea": "Macaco da quebrada fazendo teste",
    "send_to_telegram": false,
    "post_to_tiktok": false
  }'
```

**Resposta esperada:**
```json
{
  "task_id": "abc123...",
  "status": "pending",
  "message": "Video generation started. Use task_id to check progress."
}
```

Verificar progresso:
```bash
curl http://localhost:8070/api/videos/status/{task_id}
```

## 9. Teste via Swagger UI

1. Acesse http://localhost:8070/docs
2. Expanda qualquer endpoint
3. Clique em "Try it out"
4. Preencha os parâmetros
5. Clique em "Execute"
6. Veja a resposta

### Endpoints Recomendados para Teste:

1. **GET /health** - Sem parâmetros
2. **POST /api/ideas** - Criar ideia de teste
3. **GET /api/ideas** - Listar ideias
4. **GET /api/scheduler/status** - Ver status

## 10. Teste do Link Downloader Bot

Se iniciado via `run_api.py`, o Link Downloader Bot estará rodando.

**Teste:**
1. Abra Telegram
2. Envie mensagem para @Tratormax_bot
3. Envie um link de vídeo (Instagram, TikTok, etc)
4. Bot baixará e enviará o vídeo

## Troubleshooting

### API não inicia

```bash
# Verificar se porta 8070 está em uso
lsof -i :8070

# Matar processo na porta
kill -9 <PID>
```

### Erro de importação

```bash
# Reinstalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list | grep -E "(fastapi|uvicorn|pydantic)"
```

### Erro de permissão

```bash
# Dar permissão de execução ao run_api.py
chmod +x run_api.py
```

### Storage não cria arquivos

```bash
# Verificar permissões da pasta temp_videos
ls -la temp_videos/

# Criar se não existir
mkdir -p temp_videos
```

## Verificação Completa

Execute todos os comandos em sequência:

```bash
# 1. Health check
curl -s http://localhost:8070/health | jq

# 2. Criar ideia
IDEA_RESPONSE=$(curl -s -X POST http://localhost:8070/api/ideas \
  -H "Content-Type: application/json" \
  -d '{"title":"Teste API","description":"Teste de funcionamento","tags":["teste"]}')

echo $IDEA_RESPONSE | jq

# 3. Extrair ID
IDEA_ID=$(echo $IDEA_RESPONSE | jq -r '.id')
echo "Idea ID: $IDEA_ID"

# 4. Buscar ideia
curl -s http://localhost:8070/api/ideas/$IDEA_ID | jq

# 5. Listar ideias
curl -s http://localhost:8070/api/ideas | jq

# 6. Status do scheduler
curl -s http://localhost:8070/api/scheduler/status | jq

# 7. Deletar ideia de teste
curl -X DELETE http://localhost:8070/api/ideas/$IDEA_ID

echo "✅ Teste completo!"
```

Se todos os comandos executarem sem erros, sua API está funcionando perfeitamente! 🎉
