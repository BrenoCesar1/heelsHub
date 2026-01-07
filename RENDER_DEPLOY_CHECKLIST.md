# ✅ Checklist de Deploy no Render

## 🔧 Variáveis de Ambiente Necessárias

Acesse o painel do Render → Seu serviço → Environment

### ✅ Obrigatórias para o Bot funcionar:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui
```

**E uma das duas opções abaixo:**

```bash
# Opção 1: Usuário único
TELEGRAM_CHAT_ID=seu_chat_id

# Opção 2: Múltiplos usuários (RECOMENDADO)
TELEGRAM_AUTHORIZED_CHAT_IDS=id1,id2,id3
```

### ✅ Opcionais:

```bash
# Habilitar/desabilitar o bot
ENABLE_TELEGRAM_BOT=true

# Gemini AI (para geração de vídeos)
GEMINI_API_KEY=sua_chave

# Google Veo Accounts (para geração de vídeos)
VEO_ACCOUNT_1_USERNAME=email@gmail.com
VEO_ACCOUNT_1_PASSWORD=senha

# TikTok API (para upload automático)
TIKTOK_CLIENT_KEY=sua_chave
TIKTOK_CLIENT_SECRET=seu_secret
TIKTOK_AUTO_UPLOAD=true

# Instagram Downloads (se tiver problemas)
YTDLP_COOKIES_FILE=temp_videos/cookies.txt
```

---

## 🚀 Passos para Deploy

### 1. Configure as Variáveis no Render

1. Acesse: Dashboard → Seu serviço → Environment
2. Clique em "Add Environment Variable"
3. Adicione **pelo menos**:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_AUTHORIZED_CHAT_IDS` (ou `TELEGRAM_CHAT_ID`)
4. Salve

### 2. Faça Push do Código

```bash
git add .
git commit -m "feat: multi-user support"
git push
```

### 3. Aguarde o Deploy

- Render detecta o push automaticamente
- Build leva ~2-3 minutos
- Aguarde até o status ficar "Live"

### 4. Verifique os Logs

Acesse: Dashboard → Seu serviço → Logs

**Logs esperados (sucesso):**
```
🚀 AI CONTENT CREATOR API - Starting Up
============================================================
🤖 Telegram Link Downloader Bot: ENABLED
👥 Authorized users: 1
✅ API is ready
📚 Documentation: http://...
```

**Logs de erro (problema):**
```
⚠️  Telegram Bot failed to start: ...
ℹ️  Telegram Bot: DISABLED (no tokens configured)
```

---

## 🐛 Troubleshooting

### Problema: "Bot não responde no Telegram"

#### Checklist:

- [ ] **Variáveis configuradas?**
  ```bash
  # No Render Dashboard → Environment
  TELEGRAM_BOT_TOKEN = ✅ configurado
  TELEGRAM_AUTHORIZED_CHAT_IDS = ✅ configurado
  ```

- [ ] **Chat ID está correto?**
  ```bash
  # Execute localmente:
  python discover_chat_ids.py
  # Compare com o ID no Render
  ```

- [ ] **Bot está rodando?**
  ```bash
  # Nos logs do Render, procure por:
  "🤖 Telegram Link Downloader Bot: ENABLED"
  ```

- [ ] **Seu chat_id está autorizado?**
  ```bash
  # Nos logs, ao enviar mensagem, deve aparecer:
  "📩 New message from chat XXXXXX"
  
  # Se aparecer:
  "⚠️  Unauthorized access attempt from chat_id: XXXXXX"
  # → Seu ID não está na lista autorizada!
  ```

### Solução Rápida:

1. **Descubra seu chat_id:**
   - Envie mensagem para [@userinfobot](https://t.me/userinfobot)
   - Copie o ID

2. **Configure no Render:**
   - Dashboard → Environment
   - Adicione/edite: `TELEGRAM_AUTHORIZED_CHAT_IDS=seu_id_aqui`
   - Salve (Render vai redeployar automaticamente)

3. **Aguarde 2-3 minutos** para o redeploy

4. **Teste novamente** enviando um link

---

## 📊 Como Verificar se Está Funcionando

### 1. Health Check

Acesse a URL do seu app + `/health`:
```
https://seu-app.onrender.com/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "version": "1.0.0"
}
```

### 2. Documentação da API

Acesse: `https://seu-app.onrender.com/docs`

Você verá a interface Swagger com todos os endpoints.

### 3. Logs do Bot

Nos logs do Render, quando você enviar uma mensagem:

**✅ Sucesso:**
```
📩 [Bot] New message from chat 123456789: https://tiktok.com/...
⬇️ Downloading from TikTok...
✅ Video sent successfully to chat 123456789
```

**❌ Não autorizado:**
```
⚠️  Unauthorized access attempt from chat_id: 999999999 (@username)
```

**❌ Bot não rodando:**
```
ℹ️  Telegram Bot: DISABLED (no tokens configured)
   Missing: TELEGRAM_AUTHORIZED_CHAT_IDS
```

---

## 🔐 Segurança

### Nunca commite credenciais!

❌ **ERRADO:**
```bash
# .env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...  # commitado no git
```

✅ **CORRETO:**
```bash
# Configure apenas no Render Dashboard
# O .env é apenas local e está no .gitignore
```

### Teste antes de fazer deploy:

```bash
# Local
python test_multi_user.py

# Deve mostrar:
✅ Service initialized successfully
✅ Authorization system: Working
✅ Total authorized users: X
```

---

## 📱 Testando Multi-Usuário

### Cenário: 3 pessoas na equipe

1. **Cada pessoa obtém seu chat_id:**
   - Via [@userinfobot](https://t.me/userinfobot)
   - Exemplo: João = `111`, Maria = `222`, Pedro = `333`

2. **Configure no Render:**
   ```bash
   TELEGRAM_AUTHORIZED_CHAT_IDS=111,222,333
   ```

3. **Cada pessoa testa:**
   - João envia: `https://tiktok.com/video1`
   - Maria envia: `https://instagram.com/video2`
   - Pedro envia: `https://youtube.com/video3`

4. **Resultado esperado:**
   - João recebe apenas video1
   - Maria recebe apenas video2
   - Pedro recebe apenas video3
   - ✅ Histórico isolado!

---

## 🆘 Ainda não funciona?

### 1. Verifique os logs completos

```bash
# No Render Dashboard → Logs
# Procure por erros em vermelho
# Copie a mensagem de erro completa
```

### 2. Teste local primeiro

```bash
# Configure o .env localmente
cp .env.example .env
# Edite o .env com suas credenciais

# Teste
python test_multi_user.py
python run_api.py

# Envie uma mensagem ao bot
# Funciona local? → Problema é no Render
# Não funciona local? → Problema na configuração
```

### 3. Variáveis comuns que faltam

```bash
# Certifique-se de ter NO MÍNIMO:
TELEGRAM_BOT_TOKEN=...
TELEGRAM_AUTHORIZED_CHAT_IDS=...

# Ou no modo antigo:
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### 4. Restart forçado

No Render Dashboard:
- Clique em "Manual Deploy" → "Clear build cache & deploy"
- Aguarde o build completo

---

## 📚 Links Úteis

- [Render Dashboard](https://dashboard.render.com/)
- [Telegram BotFather](https://t.me/BotFather)
- [Get Chat ID Bot](https://t.me/userinfobot)
- [Documentação Render](https://render.com/docs)

---

## ✅ Checklist Final

Antes de fazer deploy:

- [ ] Variáveis configuradas no Render
- [ ] Chat ID correto (testado com @userinfobot)
- [ ] `.env` local funciona (teste com `python test_multi_user.py`)
- [ ] Código commitado e pushed
- [ ] Aguardou build completar (2-3 min)
- [ ] Verificou logs do Render (deve mostrar "Bot: ENABLED")
- [ ] Testou enviando link ao bot
- [ ] Bot respondeu no chat correto

---

**Data:** 07/01/2026  
**Versão:** 2.0 - Multi-User Support
