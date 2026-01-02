# 🔧 Checklist: Antes de Testar em Produção

## ✅ Pré-requisitos Locais

### 1. Exportar cookies do Instagram

```bash
# Usando extensão do navegador "Get cookies.txt LOCALLY":
# 1. Faça login no Instagram
# 2. Exporte cookies.txt
# 3. Salve em temp_videos/cookies.txt
```

### 2. Configurar localmente (escolha UMA opção):

**Opção A: Arquivo completo (desenvolvimento)**
```bash
export YTDLP_COOKIES_FILE=temp_videos/cookies.txt
```

**Opção B: Cookies minimalistas (simula Render)**
```bash
# Abra temp_videos/cookies.txt e extraia os valores:
export INSTAGRAM_SESSIONID='valor_do_sessionid_aqui'
export INSTAGRAM_CSRFTOKEN='valor_do_csrftoken_aqui'
export INSTAGRAM_DS_USER_ID='valor_do_ds_user_id_aqui'
```

### 3. Testar localmente

```bash
cd /home/breno/Post\ Tiktok

# Teste 1: Script de teste
python test_instagram_download.py

# Deve mostrar:
# ✅ TESTE BEM-SUCEDIDO!
# 📁 Arquivo: temp_videos/XXX.mp4
# 📏 Tamanho: X.XX MB
```

### 4. Testar bot completo localmente (opcional)

```bash
# Inicie a API localmente
python run_api.py

# Em outro terminal ou no Telegram:
# Envie um link do Instagram para o bot

# Verifique nos logs:
# - Deve mostrar: 🔐 Created minimal Instagram cookies
# - NÃO deve ter: ⚠️ Instagram download without cookies
# - NÃO deve duplicar mensagens
```

---

## 🐛 Problemas Conhecidos e Soluções

### Problema 1: Mensagens Duplicadas no Telegram

**Causa Possível:** Bot pode estar rodando em dois lugares:
1. Como processo separado
2. Embutido na API

**Verificação no Render:**
```bash
# Nos logs do Render, procure por:
"Link Downloader Bot started" 
# Se aparecer 2 vezes = problema!
```

**Solução:**
- Certifique-se que apenas a API está rodando
- `run_api.py` já foi corrigido para NÃO iniciar bot separado
- Bot roda apenas dentro da API (embedded)

### Problema 2: Download Failed

**Causas:**
1. Cookies não configurados
2. Cookies expirados
3. Formato errado de cookies

**Verificação:**
```bash
# Nos logs deve aparecer UMA dessas linhas:
🔐 Created minimal Instagram cookies from env vars
🔐 Using cookies file: temp_videos/cookies.txt
🔐 Wrote cookies from YTDLP_COOKIES_CONTENT

# Se aparecer:
⚠️ Instagram download without cookies
# = Cookies NÃO estão sendo lidos
```

### Problema 3: "exec /bin/bash: argument list too long"

**Causa:** `YTDLP_COOKIES_CONTENT` muito grande (>32KB)

**Solução:** Use cookies minimalistas (3 variáveis pequenas)

---

## 📋 Checklist Completo

### Local (antes de produção):
- [ ] Exportei cookies.txt do navegador
- [ ] Configurei variáveis de ambiente localmente
- [ ] `python test_instagram_download.py` → ✅ SUCESSO
- [ ] `python run_api.py` → Inicia sem erros
- [ ] Enviei link teste no Telegram → Baixou e enviou vídeo
- [ ] NÃO recebo mensagens duplicadas
- [ ] Logs mostram cookies sendo usados

### Produção (Render):
- [ ] Decidi qual método usar (minimalista recomendado)
- [ ] Removi variáveis antigas conflitantes
- [ ] Configurei novas variáveis corretamente
- [ ] Aguardei deploy completar (~3 min)
- [ ] Testei com 1 link do Instagram
- [ ] Funcionou sem duplicação
- [ ] Logs confirmam cookies carregados

---

## 🎯 Próximos Passos

**SOMENTE depois que tudo funcionar 100% localmente:**

1. Documente exatamente quais variáveis estão funcionando
2. Anote os valores (sem compartilhar publicamente!)
3. Configure no Render com os mesmos valores
4. Monitore logs durante primeiro teste em produção

**NÃO envie para produção se:**
- ❌ Teste local falhou
- ❌ Recebe mensagens duplicadas localmente
- ❌ Não tem cookies válidos
- ❌ Download falha localmente

---

## 📞 Suporte

Se tudo funcionar localmente mas falhar no Render:
1. Compare variáveis de ambiente (local vs Render)
2. Verifique logs do Render linha por linha
3. Confirme que apenas 1 processo está rodando
4. Teste com link diferente (pode ser problema de conteúdo específico)
