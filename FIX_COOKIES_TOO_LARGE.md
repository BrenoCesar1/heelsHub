# 🔧 Solução: Cookies muito grandes para Render

## Problema

Erro: `exec /bin/bash: argument list too long`

**Causa:** O arquivo `cookies.txt` completo tem ~100+ linhas, excedendo o limite de variáveis de ambiente do Render (~32KB em algumas configurações).

## ✅ Solução: Usar apenas cookies essenciais

Em vez de colar o arquivo `cookies.txt` inteiro, use apenas os 3 cookies essenciais do Instagram.

### Passo 1: Extrair cookies essenciais

**Abra seu `cookies.txt` e encontre estas 3 linhas:**

```
.instagram.com	TRUE	/	TRUE	1234567890	sessionid	12345678%3Aabcdef...
.instagram.com	TRUE	/	TRUE	1234567890	csrftoken	abc123def456...
.instagram.com	TRUE	/	TRUE	1234567890	ds_user_id	12345678
```

**Copie apenas os VALORES (última coluna):**
- `sessionid` → valor longo (ex: `12345678%3Aabcdef...`)
- `csrftoken` → valor médio (ex: `abc123def456...`)
- `ds_user_id` → seu user ID numérico (ex: `12345678`)

### Passo 2: Configurar no Render

**Delete a variável grande:**
1. Render Dashboard → Environment
2. Encontre `YTDLP_COOKIES_CONTENT` → Delete

**Adicione os 3 cookies individuais:**
1. **Add Environment Variable** (3 vezes):
   ```
   Key: INSTAGRAM_SESSIONID
   Value: [cole o valor do sessionid aqui]
   
   Key: INSTAGRAM_CSRFTOKEN
   Value: [cole o valor do csrftoken aqui]
   
   Key: INSTAGRAM_DS_USER_ID
   Value: [cole o valor do ds_user_id aqui]
   ```

### Passo 3: Executar script de setup

O script `create_minimal_cookies.py` vai criar o arquivo cookies.txt automaticamente no startup.

**Adicione ao seu `run_api.py` ou startup:**
```python
# No início do run_api.py ou api/main.py
from create_minimal_cookies import create_minimal_instagram_cookies

# Cria cookies.txt a partir das variáveis de ambiente
create_minimal_instagram_cookies()
```

Ou execute como comando separado no Render.

### Passo 4: Deploy

1. Commit e push as alterações
2. Render faz deploy automático
3. Script cria `temp_videos/cookies.txt` no startup
4. Downloader usa automaticamente

---

## 📋 Alternativa Mais Simples: Usar INSTAGRAM_SESSIONID diretamente

Se você só precisa do cookie de sessão (geralmente suficiente):

### Método 1: Header de Cookie direto

**No Render Environment:**
```
Key: INSTAGRAM_SESSION_COOKIE
Value: sessionid=SEU_VALOR_AQUI
```

**Código atualizado (já vou implementar):**
```python
# No video_downloader_service.py
session_cookie = os.getenv('INSTAGRAM_SESSION_COOKIE')
if session_cookie and 'instagram' in url.lower():
    options['http_headers'] = {
        'Cookie': session_cookie
    }
```

### Método 2: Apenas sessionid

**No Render Environment:**
```
Key: INSTAGRAM_SESSIONID
Value: [valor do sessionid]
```

Script cria cookies.txt mínimo automaticamente.

---

## 🎯 Recomendação Rápida

**Para resolver AGORA:**

1. **Delete `YTDLP_COOKIES_CONTENT`** do Render Environment

2. **Adicione apenas:**
   ```
   INSTAGRAM_SESSIONID=[seu_sessionid_aqui]
   ```

3. **Faça deploy**

Vou atualizar o código agora para suportar isso automaticamente! ⚡
