# 🍪 Guia: Resolver Bloqueio do Instagram com Cookies

## Por que o Instagram bloqueia downloads?

O Instagram detecta requisições automatizadas (bots) e bloqueia com mensagens como:
- `"Requested content is not available"`
- `"Rate-limit reached"`
- `"Login required"`
- `"Main webpage is locked behind the login page"`

**Solução:** Usar cookies do seu navegador para autenticar as requisições.

---

## 🚀 Solução Rápida (3 passos)

### 1. Instalar extensão do navegador

**Chrome/Edge/Brave:**
- Instale: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)

**Firefox:**
- Instale: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

### 2. Exportar cookies do Instagram

1. **Faça login** no Instagram pelo navegador
2. **Navegue** até `https://www.instagram.com`
3. **Clique** no ícone da extensão (cookie na barra de ferramentas)
4. **Clique** em "Export" ou "Download cookies.txt"
5. **Salve** o arquivo como `cookies.txt`

### 3. Configurar no projeto

**Desenvolvimento local:**
```bash
# Copie cookies.txt para a pasta do projeto
cp ~/Downloads/cookies.txt /home/breno/Post\ Tiktok/temp_videos/

# Opção A: Configure variável de ambiente (arquivo)
export YTDLP_COOKIES_FILE=/home/breno/Post\ Tiktok/temp_videos/cookies.txt

# Opção B: Ou adicione ao .env
echo "YTDLP_COOKIES_FILE=temp_videos/cookies.txt" >> .env

# Opção C: Ou cole o conteúdo (simula Render)
export YTDLP_COOKIES_CONTENT="$(cat temp_videos/cookies.txt)"
```

**Render (produção):**
```bash
# MÉTODO RECOMENDADO: Cole o conteúdo dos cookies
# 1. Abra cookies.txt, copie TODO conteúdo
# 2. Render Dashboard > Environment > Add Variable:
#    Key: YTDLP_COOKIES_CONTENT
#    Value: [cole o conteúdo completo aqui]
# 3. Remova YTDLP_COOKIES_FILE se existir
# 4. Manual Deploy
```

---

## 📋 Passo a Passo Detalhado

### Para Desenvolvimento Local

#### 1. Exportar cookies

```bash
# Instale a extensão "Get cookies.txt LOCALLY"
# Chrome: https://chrome.google.com/webstore/detail/cclelndahbckbenkjhflpdbgdldlbecc
# Firefox: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/

# 1. Abra https://www.instagram.com no navegador
# 2. Faça login na sua conta
# 3. Clique no ícone da extensão
# 4. Clique em "Export" -> salva cookies.txt
```

#### 2. Mover arquivo para o projeto

```bash
cd /home/breno/Post\ Tiktok

# Opção A: Pasta temp_videos (recomendado)
mv ~/Downloads/cookies.txt temp_videos/cookies.txt

# Opção B: Raiz do projeto
mv ~/Downloads/cookies.txt cookies.txt
```

#### 3. Configurar variável de ambiente

**Arquivo .env:**
```bash
# Adicione esta linha ao .env
YTDLP_COOKIES_FILE=temp_videos/cookies.txt
```

**Ou via terminal:**
```bash
export YTDLP_COOKIES_FILE=temp_videos/cookies.txt
```

#### 4. Testar

```bash
# Reinicie a API
python run_api.py

# Envie um link do Instagram no Telegram
# Deve baixar sem erros agora!
```

---

### Para Render (Produção)

#### Opção 1: Colar Cookies como Variável de Ambiente (✅ RECOMENDADO)

**Use este método se não encontrar "Files" no painel do Render:**

1. **Exporte cookies.txt** do navegador (passos acima)

2. **Abra o arquivo cookies.txt** no seu computador e copie TODO o conteúdo

3. **Acesse Render Dashboard:**
   - Vá para seu serviço
   - Clique em **Environment** no menu lateral
   - Clique em **Add Environment Variable**

4. **Cole o conteúdo dos cookies:**
   ```
   Key: YTDLP_COOKIES_CONTENT
   Value: [cole TODO o conteúdo do cookies.txt aqui - várias linhas]
   ```
   
   ⚠️ **Importante:** 
   - Cole o conteúdo COMPLETO (não o caminho do arquivo)
   - Incluindo a primeira linha `# Netscape HTTP Cookie File`
   - Todas as linhas com domínios e cookies

5. **Remova YTDLP_COOKIES_FILE se existir:**
   - Se houver uma variável `YTDLP_COOKIES_FILE` → Delete
   - (Essa variável não funciona sem arquivo físico)

6. **Salve e faça Manual Deploy**

#### Opção 2: Upload via "Secret Files" (se disponível)

Se sua conta Render tiver acesso a "Secret Files":

1. **Settings** > **Secret Files**
2. **Add Secret File**
   - Filename: `temp_videos/cookies.txt`
   - Content: [cole todo conteúdo do cookies.txt]

3. **Environment** > Add Variable:
   ```
   Key: YTDLP_COOKIES_FILE
   Value: /opt/render/project/src/temp_videos/cookies.txt
   ```

4. **Redeploy** o serviço

#### Opção 2: Via Git (NÃO recomendado para cookies)

⚠️ **Cuidado:** Não commite cookies no Git público!

```bash
# .gitignore já deve ter:
cookies.txt
temp_videos/cookies.txt
```

Se for repositório privado:
```bash
cp cookies.txt temp_videos/
git add temp_videos/cookies.txt
git commit -m "Add Instagram cookies"
git push
```

#### Opção 3: Usar Render Secrets (Mais seguro)

```bash
# 1. No Render Dashboard > Environment
# 2. Add environment variable do tipo "Secret File"
YTDLP_COOKIES_FILE=/etc/secrets/cookies.txt

# 3. Cole o conteúdo do cookies.txt
```

---

## 🔐 Segurança

### ⚠️ Importante

- **Cookies expiram:** Você precisará renovar (exportar novamente) a cada 30-90 dias
- **Não compartilhe:** Cookies dão acesso à sua conta
- **Use .gitignore:** Nunca commite cookies em repositórios públicos

### .gitignore recomendado

```gitignore
# Cookies
cookies.txt
**/cookies.txt
temp_videos/cookies.txt

# Senhas
.netrc
```

### Renovação automática

Configure um reminder para renovar cookies:
```bash
# Renovar a cada 60 dias
# 1. Faça login no Instagram
# 2. Exporte cookies novamente
# 3. Atualize no Render (Settings > Files)
```

---

## 🧪 Testando Localmente

```bash
# 1. Certifique-se que cookies.txt existe
ls -lh temp_videos/cookies.txt

# 2. Configure variável de ambiente
export YTDLP_COOKIES_FILE=temp_videos/cookies.txt

# 3. Inicie API
python run_api.py

# 4. Teste via curl (se tiver endpoint direto)
curl -X POST http://localhost:8070/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/reel/..."}'

# 5. Ou envie link no Telegram
# Deve mostrar:
# 🔐 Using cookies file: temp_videos/cookies.txt
```

---

## 🐛 Troubleshooting

### Erro: "cookies.txt not found"

```bash
# Verifique caminho
ls -lh temp_videos/cookies.txt

# Verifique variável
echo $YTDLP_COOKIES_FILE

# Use caminho absoluto se necessário
export YTDLP_COOKIES_FILE=/home/breno/Post\ Tiktok/temp_videos/cookies.txt
```

### Ainda recebe "rate-limit" mesmo com cookies

```bash
# Cookies podem estar expirados - exporte novamente
# 1. Abra Instagram no navegador
# 2. Faça logout e login novamente
# 3. Exporte cookies.txt novo
# 4. Substitua o arquivo antigo
```

### "Invalid cookies format"

```bash
# Certifique-se de usar extensão correta
# Formato deve ser Netscape cookies.txt

# Primeira linha deve ser:
# # Netscape HTTP Cookie File

# Verifique conteúdo:
head -5 temp_videos/cookies.txt
```

### No Render: "Permission denied"

```bash
# Certifique-se que o caminho existe
# No Render, use:
YTDLP_COOKIES_FILE=/opt/render/project/src/temp_videos/cookies.txt

# Ou Secret File (Render gerencia permissões):
YTDLP_COOKIES_FILE=/etc/secrets/cookies.txt
```

---

## 📚 Referências

- [yt-dlp Cookies Documentation](https://github.com/yt-dlp/yt-dlp#cookies)
- [Get cookies.txt LOCALLY (Chrome)](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
- [cookies.txt (Firefox)](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
- [Render Secret Files](https://docs.render.com/configure-environment-variables#secret-files)

---

## ✅ Checklist

- [ ] Instalei extensão de cookies no navegador
- [ ] Fiz login no Instagram
- [ ] Exportei cookies.txt
- [ ] Copiei para `temp_videos/cookies.txt`
- [ ] Configurei `YTDLP_COOKIES_FILE` no .env
- [ ] Testei localmente - funcionou!
- [ ] Configurei no Render (Secret File ou Environment)
- [ ] Fiz redeploy no Render
- [ ] Testei em produção - funcionou!
- [ ] Adicionei reminder para renovar cookies em 60 dias

---

## 🎯 Resumo

```bash
# 1. Instale extensão "Get cookies.txt LOCALLY"
# 2. Abra Instagram, faça login
# 3. Exporte cookies.txt
# 4. Mova para temp_videos/cookies.txt
# 5. Configure variável:
echo "YTDLP_COOKIES_FILE=temp_videos/cookies.txt" >> .env

# 6. Reinicie:
python run_api.py

# 7. Para Render:
# Dashboard > Environment > Add Variable
# YTDLP_COOKIES_FILE=/opt/render/project/src/temp_videos/cookies.txt
# Dashboard > Settings > Files > Add Secret File
# Filename: temp_videos/cookies.txt
# Content: [cole cookies]
```

**Pronto!** Agora o Instagram não bloqueará mais seus downloads. 🎉
