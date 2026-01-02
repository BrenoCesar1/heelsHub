# 🐛 Debug: Duplicação de Mensagens no Telegram

## Problema
Mensagens sendo enviadas/recebidas duas vezes no Telegram.

## Causas Possíveis

### 1. ✅ Múltiplas instâncias do bot (VERIFICADO - OK)
**Status:** ✅ Resolvido
- `run_api.py` já foi corrigido anteriormente
- Código atual não inicia bot separado
- Bot roda APENAS embutido na API
- `ps aux | grep python` local confirmou nenhum processo duplicado

### 2. ⚠️ Webhook + Polling Simultâneos (SUSPEITA PRINCIPAL)
**Status:** 🔍 Investigar

**O que é:**
- Telegram pode enviar atualizações via Webhook (HTTP POST)
- OU via Long Polling (getUpdates)
- Se ambos estiverem ativos = mensagens duplicadas

**Como verificar:**
```bash
# Obter informações do webhook configurado
curl -X GET "https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo"

# Se retornar URL configurada:
{
  "url": "https://algo.render.com/webhook",
  "has_custom_certificate": false,
  "pending_update_count": 0
}
# = WEBHOOK ATIVO! (conflito com polling)
```

**Solução:**
```bash
# Remover webhook para usar somente polling:
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook"

# Confirmar remoção:
curl -X GET "https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo"
# Deve retornar: "url": ""
```

### 3. ⚠️ Update ID não incrementando corretamente
**Status:** ✅ Código correto
- Linha 254: `offset = update['update_id'] + 1`
- Garante que mesma atualização não é processada duas vezes

### 4. ⚠️ Render rodando múltiplos workers
**Status:** 🔍 Investigar

**O que é:**
- Render pode estar rodando 2+ instâncias da aplicação
- Cada uma com seu bot
- Ambas processam mesmas mensagens

**Como verificar no Render:**
```bash
# Nos logs, contar quantas vezes aparece na inicialização:
"🤖 Telegram Link Downloader Bot: ENABLED"
# Se aparecer 2x = 2 workers rodando
```

**Solução:**
1. Verificar `render.yaml` ou Dashboard do Render
2. Garantir que `instances: 1` (ou numInstances: 1)
3. Free tier do Render normalmente já é 1 instância

### 5. ⚠️ Callback sendo chamado múltiplas vezes
**Status:** ✅ Código correto
- Linha 271-275: Chama callback uma vez por mensagem
- Lambda garante isolamento de variáveis

### 6. ⚠️ Mensagens antigas na fila
**Status:** 🔍 Possível

**O que é:**
- Se bot ficou offline, mensagens se acumulam
- Quando volta, processa todas de uma vez
- Pode parecer duplicação

**Solução:**
```python
# Adicionar ao início do lifespan (api/main.py):
# Limpar mensagens pendentes antes de iniciar
import requests
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
offset = -1  # Pega última atualização
requests.get(f"https://api.telegram.org/bot{telegram_token}/getUpdates?offset={offset}")
```

---

## 🎯 Plano de Ação

### Passo 1: Verificar Webhook (MAIS PROVÁVEL)
```bash
# Substituir <TOKEN> pelo seu token real
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

**Se tiver URL configurada:**
```bash
# Deletar webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

### Passo 2: Verificar Workers no Render
1. Acesse Render Dashboard → Seu serviço
2. Vá em "Settings"
3. Procure por "Scaling" ou "Instances"
4. Confirme que está `1`

### Passo 3: Verificar logs no Render
```bash
# Contar quantos bots iniciaram:
grep "Telegram Link Downloader Bot: ENABLED" 

# Se aparecer 1 vez = OK
# Se aparecer 2+ vezes = múltiplos workers
```

### Passo 4: Limpar fila de mensagens
Adicione ao início do `lifespan` em [api/main.py](api/main.py#L128-L130):

```python
# Após criar o bot, antes de listen
if telegram_token:
    import requests
    # Limpa mensagens antigas
    resp = requests.get(
        f"https://api.telegram.org/bot{telegram_token}/getUpdates",
        params={"offset": -1}
    )
    print("🧹 Cleared pending Telegram messages")
```

---

## 📊 Coleta de Dados para Debug

**Execute localmente:**
```bash
cd /home/breno/Post\ Tiktok

# 1. Verificar se há webhooks
python -c "
import os, requests
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
resp = requests.get(f'https://api.telegram.org/bot{token}/getWebhookInfo')
print('🌐 Webhook Info:', resp.json())
"

# 2. Testar bot localmente com 1 mensagem
python run_api.py
# Envie UMA mensagem no Telegram
# Conte quantas respostas você recebe
```

**No Render (logs):**
```bash
# Procure por padrões:
"👂 [Async] Listening for Telegram messages..."  # Quantas vezes?
"📩 [Bot] New message:"  # Se aparecer 2x para mesma mensagem = duplicação confirmada
```

---

## ✅ Teste Final

Após aplicar correções:

1. **Local:** Enviar 1 link → Receber 1 resposta
2. **Render:** Enviar 1 link → Receber 1 resposta
3. **Logs:** Verificar se mensagem processada apenas 1 vez

**Checklist:**
- [ ] Webhook deletado (ou nunca existiu)
- [ ] Render configurado com 1 instância
- [ ] Logs mostram bot iniciando 1 vez apenas
- [ ] Mensagem de teste retorna resposta única
- [ ] Nenhum erro nos logs

---

## 🚨 Se nada funcionar

**Última opção: Restart completo**
```bash
# 1. Parar tudo no Render
# 2. Deletar webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook"

# 3. Localmente, testar isoladamente:
python test_instagram_download.py  # Sem bot

# 4. Depois testar bot sozinho:
# Remova temporariamente ENABLE_TELEGRAM_BOT=false
# Rode apenas: python bots/link_downloader_bot.py

# 5. Se funcionar isolado mas não na API:
# = Problema na integração entre FastAPI e bot
```
