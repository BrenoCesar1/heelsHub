# 👥 Configuração Multi-Usuário - Bot Telegram

Este guia explica como configurar o bot para suportar múltiplos usuários, cada um com seu próprio histórico isolado.

## 🎯 Como Funciona

- Cada usuário (chat_id) tem seu próprio histórico de mensagens isolado
- Apenas usuários autorizados podem usar o bot
- As respostas são enviadas automaticamente para o chat correto
- Sem interferência entre usuários diferentes

## 📝 Configuração Passo a Passo

### 1. Obter IDs dos Usuários

Para obter o `chat_id` de cada usuário:

#### Método 1: Usando o @userinfobot
1. Cada usuário deve adicionar [@userinfobot](https://t.me/userinfobot) no Telegram
2. Enviar qualquer mensagem para o bot
3. O bot responderá com o `chat_id`

#### Método 2: Temporariamente comentar a verificação
1. Temporariamente comente a verificação de autorização no código
2. Peça para cada usuário enviar uma mensagem ao bot
3. Os IDs aparecerão nos logs do servidor
4. Anote os IDs e restaure a verificação

### 2. Configurar Variáveis de Ambiente

Edite seu arquivo `.env` e adicione/modifique:

```bash
# Bot Token (igual para todos)
TELEGRAM_BOT_TOKEN=seu_bot_token_aqui

# Opção 1: Usuário Único (compatibilidade retroativa)
TELEGRAM_CHAT_ID=123456789

# Opção 2: Múltiplos Usuários (RECOMENDADO)
TELEGRAM_AUTHORIZED_CHAT_IDS=123456789,987654321,555666777

# Nota: Use vírgulas para separar múltiplos IDs
# Espaços ao redor das vírgulas são automaticamente removidos
```

### 3. Exemplos de Configuração

#### Configuração para 1 usuário:
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

#### Configuração para 3 usuários:
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_AUTHORIZED_CHAT_IDS=123456789,987654321,555666777
```

#### Configuração para equipe (5+ usuários):
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_AUTHORIZED_CHAT_IDS=123456789,987654321,555666777,444333222,111000999
```

## 🔒 Segurança

### O que acontece com usuários não autorizados?

Quando um usuário não autorizado tenta usar o bot:

1. ✅ A mensagem é detectada
2. ⚠️ Um alerta é registrado no log do servidor:
   ```
   ⚠️  Unauthorized access attempt from chat_id: 999888777 (@hacker)
   ```
3. ❌ O usuário recebe a mensagem:
   ```
   ❌ Acesso não autorizado. Entre em contato com o administrador.
   ```
4. 🚫 A mensagem não é processada

### Logs de Segurança

O servidor mantém logs de todas as tentativas de acesso:
- ✅ Acessos autorizados: `📩 New message from chat 123456789: ...`
- ⚠️ Tentativas bloqueadas: `⚠️  Unauthorized access attempt from chat_id: ...`

## 🔧 Como Adicionar/Remover Usuários

### Adicionar Novo Usuário

1. Obtenha o `chat_id` do novo usuário (veja seção 1)
2. Adicione o ID à variável `TELEGRAM_AUTHORIZED_CHAT_IDS`:
   ```bash
   # Antes
   TELEGRAM_AUTHORIZED_CHAT_IDS=123456789,987654321
   
   # Depois (adicionar 555666777)
   TELEGRAM_AUTHORIZED_CHAT_IDS=123456789,987654321,555666777
   ```
3. Reinicie o bot/servidor

### Remover Usuário

1. Remova o ID da variável `TELEGRAM_AUTHORIZED_CHAT_IDS`:
   ```bash
   # Antes
   TELEGRAM_AUTHORIZED_CHAT_IDS=123456789,987654321,555666777
   
   # Depois (remover 987654321)
   TELEGRAM_AUTHORIZED_CHAT_IDS=123456789,555666777
   ```
2. Reinicie o bot/servidor

## 💬 Isolamento de Histórico

### Como Funciona o Isolamento?

Cada `chat_id` é tratado independentemente:

**Usuário A (chat_id: 123456789):**
```
Usuário A: https://tiktok.com/video1
Bot → [processa e envia para 123456789]

Usuário A: https://instagram.com/video2
Bot → [processa e envia para 123456789]
```

**Usuário B (chat_id: 987654321):**
```
Usuário B: https://youtube.com/video3
Bot → [processa e envia para 987654321]

Usuário B: https://tiktok.com/video4
Bot → [processa e envia para 987654321]
```

**Resultado:**
- Usuário A vê apenas seus vídeos (video1 e video2)
- Usuário B vê apenas seus vídeos (video3 e video4)
- Nenhuma interferência entre eles

### Storage Isolado

Se você usar recursos de storage (como `IdeasStorage`), pode criar instâncias separadas por usuário:

```python
# Exemplo de uso isolado
from storage.ideas_storage import IdeasStorage

# Cada usuário tem seu próprio arquivo de ideias
storage_user_a = IdeasStorage(Path(f"temp_videos/ideas_{chat_id_a}.json"))
storage_user_b = IdeasStorage(Path(f"temp_videos/ideas_{chat_id_b}.json"))
```

## 🧪 Testando Multi-Usuário

### Teste Local

1. Configure 2 chat_ids na variável `TELEGRAM_AUTHORIZED_CHAT_IDS`
2. Inicie o bot: `python bots/link_downloader_bot.py`
3. Envie mensagens de ambos os chats simultaneamente
4. Verifique que cada usuário recebe apenas suas próprias respostas

### Checklist de Teste

- [ ] Usuário autorizado consegue enviar links
- [ ] Usuário autorizado recebe vídeos no chat correto
- [ ] Usuário não autorizado recebe mensagem de erro
- [ ] Múltiplos usuários podem usar simultaneamente
- [ ] Logs mostram tentativas não autorizadas
- [ ] Respostas vão para o chat correto

## ⚙️ Integração com API

Se você usar a API FastAPI, o bot pode rodar em paralelo:

```python
# api/main.py
import asyncio
from services.integrations.telegram_service import TelegramService
from bots.link_downloader_bot import LinkDownloaderBot

@app.on_event("startup")
async def startup_event():
    bot = LinkDownloaderBot()
    # Inicia polling em background
    asyncio.create_task(
        bot.telegram.listen_for_messages_async(bot.handle_message)
    )
```

## 🚀 Deploy em Produção

### Render.com / Heroku

As variáveis de ambiente são configuradas no painel:

1. Acesse as configurações do app
2. Adicione `TELEGRAM_AUTHORIZED_CHAT_IDS`
3. Cole os IDs separados por vírgula
4. Deploy automático

### Docker

```dockerfile
# .env para Docker
TELEGRAM_BOT_TOKEN=seu_token
TELEGRAM_AUTHORIZED_CHAT_IDS=123,456,789
```

```bash
docker run -e TELEGRAM_AUTHORIZED_CHAT_IDS="123,456,789" seu-app
```

## 📊 Monitoramento

### Verificar Usuários Ativos

Adicione logging para rastrear uso:

```python
# No handle_message
print(f"📊 Stats: User {chat_id} processed {count} videos today")
```

### Auditoria

Os logs do servidor contêm todas as interações:
```
[2026-01-07 10:30:15] 📩 New message from chat 123456789: https://...
[2026-01-07 10:30:18] ✅ Video sent successfully to chat 123456789
[2026-01-07 10:35:22] ⚠️  Unauthorized access from chat 999888777
```

## 🆘 Troubleshooting

### "No chat IDs configured"
**Problema:** Nenhum ID foi configurado
**Solução:** Adicione `TELEGRAM_AUTHORIZED_CHAT_IDS` ou `TELEGRAM_CHAT_ID`

### Usuário autorizado não recebe resposta
**Problema:** ID pode estar incorreto
**Solução:** 
1. Verifique o ID no log: `📩 New message from chat XXXXXX`
2. Compare com a variável de ambiente
3. IDs devem ser strings de números sem espaços

### Bot responde para o chat errado
**Problema:** Implementação antiga do callback
**Solução:** Use sempre `chat_id=chat_id` nos métodos:
```python
self.telegram.send_message("Texto", chat_id=chat_id)
self.telegram.send_video(path, caption, chat_id=chat_id)
```

### Performance com muitos usuários
**Problema:** Bot lento com 10+ usuários
**Solução:** 
- Use versão async: `listen_for_messages_async()`
- Considere usar webhook ao invés de polling
- Implemente rate limiting se necessário

## 📚 Referências

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Long Polling vs Webhooks](https://core.telegram.org/bots/api#getting-updates)
- Código: [telegram_service.py](services/integrations/telegram_service.py)
- Código: [link_downloader_bot.py](bots/link_downloader_bot.py)

## 💡 Próximos Passos

- [ ] Implementar rate limiting por usuário
- [ ] Adicionar comandos administrativos (/adduser, /removeuser)
- [ ] Dashboard de analytics por usuário
- [ ] Sistema de quotas/limites por usuário
- [ ] Notificações em grupo para equipes

---

**Última atualização:** 07/01/2026
**Versão:** 2.0 - Multi-User Support
