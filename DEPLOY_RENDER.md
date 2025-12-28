# 🚀 Deploy no Render (Plano Free)

Este guia explica como fazer deploy da API **com o bot de download integrado** no [Render](https://render.com) usando o plano gratuito.

## ✅ O que funciona no Plano Free

| Recurso | Status |
|---------|--------|
| API REST | ✅ Funciona |
| Bot de Download (Telegram) | ✅ Funciona (integrado na API) |
| Scheduler | ✅ Funciona (enquanto ativo) |
| TikTok Auto-Upload | ✅ Funciona |

> 💡 **Novidade:** O bot de download agora roda **dentro da API** como uma task async, então funciona no plano free!

## 📋 Pré-requisitos

1. Conta no [Render](https://render.com) (cadastro gratuito)
2. Repositório no GitHub/GitLab com este projeto
3. Bot do Telegram criado (via @BotFather)

## 🎯 Limitações do Plano Free

| Recurso | Limite |
|---------|--------|
| RAM | 512 MB |
| CPU | Compartilhada |
| Sleep após inatividade | 15 minutos |
| Requests após sleep | ~30s para "acordar" |
| Disco efêmero | Sim (dados não persistem) |

> ⚠️ **Importante:** O plano free entra em sleep após 15 min sem requests. O bot só funciona enquanto o serviço está ativo!

## 🛠️ Passo a Passo

### 1. Conectar Repositório

1. Acesse [dashboard.render.com](https://dashboard.render.com)
2. Clique em **New +** → **Web Service**
3. Conecte seu GitHub/GitLab
4. Selecione o repositório `Post Tiktok`

### 2. Configurar o Serviço

| Campo | Valor |
|-------|-------|
| **Name** | `ai-content-creator-api` |
| **Region** | Oregon (US West) ou mais próximo |
| **Branch** | `main` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

### 3. Configurar Variáveis de Ambiente

Na aba **Environment**, adicione:

| Variável | Obrigatório | Descrição |
|----------|-------------|-----------|
| `TELEGRAM_BOT_TOKEN` | ✅ Sim | Token do bot (do @BotFather) |
| `TELEGRAM_CHAT_ID` | ✅ Sim | ID do seu chat/grupo |
| `GEMINI_API_KEY` | ⚡ Para geração | API key do Google AI Studio |
| `TIKTOK_CLIENT_KEY` | 🎵 Para TikTok | Client Key do TikTok |
| `TIKTOK_CLIENT_SECRET` | 🎵 Para TikTok | Client Secret do TikTok |
| `TIKTOK_AUTO_UPLOAD` | Opcional | `true` ou `false` (default: false) |
| `ENABLE_TELEGRAM_BOT` | Opcional | `true` ou `false` (default: true) |

### 4. Deploy

1. Clique em **Create Web Service**
2. Aguarde o build (~2-5 minutos)
3. Acesse a URL fornecida (ex: `https://ai-content-creator-api.onrender.com`)

## ✅ Verificar Deploy

```bash
# Health check
curl https://SEU-APP.onrender.com/health

# Documentação (navegador)
https://SEU-APP.onrender.com/docs
```

## 🔧 Deploy via render.yaml (Alternativo)

O projeto já inclui um `render.yaml` configurado. Para usar:

1. No Dashboard, clique em **New +** → **Blueprint**
2. Conecte o repositório
3. O Render detectará automaticamente o `render.yaml`
4. Adicione as variáveis de ambiente no Dashboard
5. Confirme o deploy

## ⚡ Manter o Serviço Ativo (Evitar Sleep)

Para evitar que o serviço entre em sleep, use um serviço de ping externo:

### Opção 1: UptimeRobot (Gratuito)
1. Crie conta em [uptimerobot.com](https://uptimerobot.com)
2. Adicione monitor HTTP(s)
3. URL: `https://SEU-APP.onrender.com/health`
4. Intervalo: 5 minutos

### Opção 2: Cron-job.org (Gratuito)
1. Crie conta em [cron-job.org](https://cron-job.org)
2. Crie um cron job para chamar `/health` a cada 5 minutos

## 📁 Arquivos Criados para Deploy

```
render.yaml     # Blueprint do Render
Procfile        # Comando de start (alternativo)
runtime.txt     # Versão do Python
```

## ⚠️ Considerações

### Persistência de Dados
O plano free usa disco efêmero. Dados em `temp_videos/` serão perdidos ao reiniciar.

**Soluções:**
- Use um banco de dados externo (ex: Supabase, PlanetScale)
- Use armazenamento externo (ex: AWS S3, Cloudinary)

### Bot do Telegram
O bot de download **agora funciona** no plano free porque foi integrado à API!

**Como funciona:**
- O bot roda como uma task async dentro do FastAPI
- Usa long-polling assíncrono (não bloqueia a API)
- Compartilha o mesmo processo/memória que a API

**Limitações:**
- O bot para se o serviço entrar em sleep (15min inatividade)
- Use serviço de ping para manter ativo (ver abaixo)

### Scheduler
O scheduler funciona enquanto a API está ativa, mas:
- Para se o serviço entrar em sleep
- Use serviço de ping para manter ativo

## 🔗 Links Úteis

- [Render Docs - Python](https://render.com/docs/deploy-fastapi)
- [Render Docs - Environment Variables](https://render.com/docs/environment-variables)
- [Render Docs - Free Plan](https://render.com/docs/free)
