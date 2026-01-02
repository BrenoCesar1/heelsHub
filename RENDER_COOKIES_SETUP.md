# 🚀 Configurar Cookies do Instagram no Render

## ⚡ Guia Rápido (5 minutos)

### Passo 1: Exportar Cookies do Navegador

1. **Instale extensão:**
   - Chrome: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. **Exporte cookies:**
   - Abra Instagram no navegador
   - Faça login
   - Clique na extensão → Export
   - Salva `cookies.txt`

### Passo 2: Copiar Conteúdo

1. **Abra cookies.txt** no Bloco de Notas/TextEdit
2. **Selecione TUDO** (Ctrl+A / Cmd+A)
3. **Copie** (Ctrl+C / Cmd+C)

O conteúdo deve começar com:
```
# Netscape HTTP Cookie File
# This is a generated file! Do not edit.

.instagram.com	TRUE	/	TRUE	1234567890	...
```

### Passo 3: Configurar no Render

1. **Abra Render Dashboard**
   - Acesse seu serviço `ai-content-creator-api`

2. **Clique em "Environment"** no menu lateral esquerdo

3. **Adicione nova variável:**
   - Clique em **"Add Environment Variable"**
   - **Key:** `YTDLP_COOKIES_CONTENT`
   - **Value:** Cole TODO o conteúdo que você copiou
   - Clique **"Save Changes"**

4. **Remova variável antiga (se existir):**
   - Procure por `YTDLP_COOKIES_FILE`
   - Se existir, clique no ícone de lixeira → Delete
   - (Essa variável não funciona sem arquivo físico)

5. **Salve e faça deploy:**
   - Clique **"Save Changes"** no topo
   - Clique **"Manual Deploy"** → Deploy latest commit

### Passo 4: Testar

1. **Aguarde deploy completar** (~2-3 minutos)
2. **Abra Logs** (aba Logs no Render)
3. **Envie link do Instagram** no seu bot Telegram
4. **Deve aparecer nos logs:**
   ```
   🔐 Wrote cookies from YTDLP_COOKIES_CONTENT to: temp_videos/cookies_from_env.txt
   ✅ Download complete!
   ```

---

## 🐛 Troubleshooting

### Erro: "file not found: /opt/render/project/src/temp_videos/cookies.txt"

**Causa:** Você configurou `YTDLP_COOKIES_FILE` mas o arquivo não existe.

**Solução:**
1. Delete `YTDLP_COOKIES_FILE` do Environment
2. Use `YTDLP_COOKIES_CONTENT` (cole conteúdo) em vez disso

### Erro: "Download failed" no Telegram

**Verifique nos logs do Render:**
- Se aparecer `⚠️ Instagram download without cookies` → cookies não foram configurados
- Se aparecer `⚠️ YTDLP_COOKIES_FILE set but file not found` → use `YTDLP_COOKIES_CONTENT`
- Se aparecer `🔐 Wrote cookies from YTDLP_COOKIES_CONTENT` → cookies OK, problema pode ser outro

### Ainda não funciona após configurar cookies?

1. **Verifique se cookies estão válidos:**
   - Abra Instagram no navegador
   - Se estiver deslogado → faça login novamente
   - Exporte cookies.txt novamente
   - Atualize `YTDLP_COOKIES_CONTENT` no Render

2. **Verifique formato do cookies.txt:**
   - Primeira linha deve ser: `# Netscape HTTP Cookie File`
   - Se não tiver, a extensão está errada

3. **Teste localmente primeiro:**
   ```bash
   # No seu computador:
   export YTDLP_COOKIES_CONTENT="$(cat cookies.txt)"
   python run_api.py
   # Envie link no Telegram
   ```

---

## 📝 Checklist Render

- [ ] Exportei cookies.txt do navegador (extensão instalada)
- [ ] Copiei TODO o conteúdo do cookies.txt
- [ ] Abri Render Dashboard > meu serviço
- [ ] Cliquei em "Environment"
- [ ] Adicionei `YTDLP_COOKIES_CONTENT` com conteúdo colado
- [ ] Deletei `YTDLP_COOKIES_FILE` (se existia)
- [ ] Salvei e fiz Manual Deploy
- [ ] Aguardei deploy completar
- [ ] Testei enviando link do Instagram
- [ ] Funcionou! ✅

---

## 🔐 Segurança

### É seguro colar cookies no Render?

✅ **Sim, é seguro:**
- Render trata Environment Variables como **secrets**
- Não aparecem nos logs públicos
- Ficam criptografados no servidor
- Apenas você tem acesso

⚠️ **Mas tenha cuidado:**
- Cookies dão acesso à sua conta Instagram
- Não compartilhe sua conta Render com terceiros
- Renove cookies a cada 60 dias

### Alternativas (mais seguras, porém complexas):

1. **Secret Files** (se sua conta Render tiver):
   - Settings > Secret Files > Add
   - Mais seguro que env vars

2. **Vault externo** (ex: HashiCorp Vault):
   - Para empresas/projetos grandes
   - Overkill para uso pessoal

---

## 📊 Diferenças: YTDLP_COOKIES_FILE vs YTDLP_COOKIES_CONTENT

| Aspecto | YTDLP_COOKIES_FILE | YTDLP_COOKIES_CONTENT |
|---------|-------------------|---------------------|
| **O que é** | Caminho para arquivo | Conteúdo do arquivo |
| **Exemplo** | `/path/to/cookies.txt` | `# Netscape HTTP Cookie File...` |
| **Funciona local** | ✅ Sim | ✅ Sim |
| **Funciona Render** | ⚠️ Precisa Secret Files | ✅ Sim (recomendado) |
| **Configuração** | Simples (aponta arquivo) | Cole conteúdo inteiro |
| **Segurança** | Arquivo no sistema | Variável de ambiente |
| **Renovação** | Substitui arquivo | Edita variável |

**Recomendação:** Use `YTDLP_COOKIES_CONTENT` no Render (mais fácil e funciona sempre).

---

## 🎯 Resumo Visual

```
┌─────────────────────────────────────────────────┐
│  1. EXPORTAR COOKIES DO NAVEGADOR               │
│     • Instalar extensão                         │
│     • Login no Instagram                        │
│     • Exportar cookies.txt                      │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  2. COPIAR CONTEÚDO                             │
│     • Abrir cookies.txt                         │
│     • Selecionar tudo (Ctrl+A)                  │
│     • Copiar (Ctrl+C)                           │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  3. RENDER DASHBOARD                            │
│     • Environment > Add Variable                │
│     • Key: YTDLP_COOKIES_CONTENT                │
│     • Value: [colar conteúdo]                   │
│     • Delete: YTDLP_COOKIES_FILE (se existir)   │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  4. DEPLOY E TESTAR                             │
│     • Save Changes                              │
│     • Manual Deploy                             │
│     • Aguardar (~3 min)                         │
│     • Enviar link Instagram no bot              │
│     • ✅ Funcionando!                           │
└─────────────────────────────────────────────────┘
```

---

## ❓ FAQ

**P: Preciso renovar cookies?**  
R: Sim, a cada 30-90 dias. Configure um reminder.

**P: Posso usar conta secundária do Instagram?**  
R: Sim, recomendado! Mais seguro que usar sua conta principal.

**P: E se eu esquecer de renovar?**  
R: Downloads vão começar a falhar. Basta exportar cookies novos.

**P: Cookies funcionam para TikTok/Facebook também?**  
R: Sim! Exporte cookies do site respectivo e configure.

**P: Quantas linhas tem cookies.txt?**  
R: Varia, geralmente 20-100 linhas. Cole todas!

**P: Posso ter COOKIES_FILE e COOKIES_CONTENT juntos?**  
R: Sim, CONTENT tem prioridade. Se CONTENT existir, FILE é ignorado.

---

**Precisa de ajuda?** Consulte [INSTAGRAM_COOKIES_GUIDE.md](INSTAGRAM_COOKIES_GUIDE.md) para mais detalhes.
