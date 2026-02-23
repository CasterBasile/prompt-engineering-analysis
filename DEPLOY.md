# 🚀 Guida al Deploy - Streamlit Community Cloud

## ✅ Soluzione Consigliata: **Streamlit Community Cloud** (GRATUITO)

Il modo **più semplice ed economico** per deployare questa app Streamlit è utilizzare **Streamlit Community Cloud**, che è:
- ✅ **Completamente GRATUITO** (nessun costo)
- ✅ **Ottimizzato per Streamlit** (configurazione zero)
- ✅ **Deploy in 5 minuti** (solo 4 passaggi)
- ✅ **Auto-deploy da GitHub** (aggiornamenti automatici)
- ✅ **HTTPS gratuito** (certificato SSL incluso)

---

## 📋 Prerequisiti

1. **Account GitHub** ([crea qui](https://github.com/signup) se non ce l'hai)
2. **Account Streamlit Community Cloud** ([registrati qui](https://share.streamlit.io/signup))
3. **Git installato** sul tuo computer

---

## 🔧 Preparazione (Eseguire una volta sola)

### Passo 1: Inizializza Repository Git Locale

Apri il terminale nella cartella del progetto ed esegui:

```bash
# Inizializza repository git (se non esiste già)
git init

# Aggiungi tutti i file
git add .

# Crea il primo commit
git commit -m "Initial commit: Prompt Engineering Analysis App"
```

### Passo 2: Crea Repository su GitHub

1. Vai su [GitHub](https://github.com) e accedi
2. Clicca su **"New repository"** (pulsante verde in alto a destra)
3. Compila i campi:
   - **Repository name**: `prompt-engineering-analysis` (o nome a tua scelta)
   - **Description**: "Analisi sistematica di tecniche di Prompt Engineering"
   - **Visibility**: `Public` (richiesto per piano gratuito) o `Private` (se hai piano Pro)
   - ❌ **NON** selezionare "Add README" (lo hai già)
4. Clicca su **"Create repository"**

### Passo 3: Collega e Carica su GitHub

GitHub ti mostrerà dei comandi. Esegui questi nel terminale:

```bash
# Collega il repository locale a GitHub (sostituisci TUO-USERNAME e NOME-REPO)
git remote add origin https://github.com/TUO-USERNAME/NOME-REPO.git

# Rinomina branch principale in "main"
git branch -M main

# Carica il codice su GitHub
git push -u origin main
```

**Esempio concreto:**
```bash
git remote add origin https://github.com/basil/prompt-engineering-analysis.git
git branch -M main
git push -u origin main
```

---

## 🚀 Deploy su Streamlit Community Cloud

### Passo 4: Deploy dell'App

1. **Vai su [Streamlit Community Cloud](https://share.streamlit.io/)**
2. **Accedi** con il tuo account GitHub
3. Clicca su **"New app"**
4. Compila il form:
   - **Repository**: Seleziona `TUO-USERNAME/NOME-REPO`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (opzionale): scegli un nome personalizzato (es. `prompts-analysis`)
5. Clicca su **"Deploy!"**

🎉 **Fatto!** L'app sarà online in 2-3 minuti su un URL tipo:
```
https://prompts-analysis.streamlit.app
```

---

## 🔄 Aggiornare l'App Dopo Modifiche

Ogni volta che modifichi il codice e vuoi aggiornare l'app online:

```bash
# Aggiungi le modifiche
git add .

# Crea un commit con descrizione delle modifiche
git commit -m "Descrizione delle modifiche"

# Carica su GitHub
git push
```

✨ **Streamlit rileverà automaticamente le modifiche** e aggiornerà l'app in 1-2 minuti!

---

## 📊 Gestione File Dati

⚠️ **IMPORTANTE**: Il file `Prompt.xlsx` NON deve essere incluso nel repository (contiene dati sensibili).

Gli utenti dovranno **caricare il proprio file Excel** tramite l'interfaccia web dell'app.

Se vuoi un file di esempio pubblico:
1. Crea `Prompt_esempio.xlsx` con dati fittizi (2-3 righe)
2. Modifica l'app per mostrare un link di download al file esempio

---

## 🔒 Gestione Segreti (Se Necessario)

Se in futuro aggiungi API keys o password:

1. Nel dashboard Streamlit Cloud, vai su **"Settings"** → **"Secrets"**
2. Aggiungi i segreti in formato TOML:
   ```toml
   [passwords]
   admin_password = "tua_password_segreta"
   
   [api_keys]
   openai_api_key = "sk-..."
   ```
3. Nel codice Python, accedi con:
   ```python
   import streamlit as st
   password = st.secrets["passwords"]["admin_password"]
   ```

---

## 🆓 Limiti del Piano Gratuito

Streamlit Community Cloud offre GRATUITAMENTE:
- ✅ **Apps illimitate** (nessun limite al numero di app)
- ✅ **1 GB RAM** per app (sufficiente per questa applicazione)
- ✅ **1 CPU core** per app
- ✅ **Utenti illimitati** (nessun limite a chi può usare l'app)
- ✅ **Banda illimitata** (nessun costo per traffico)
- ✅ **Repository pubblici** (o privati con account GitHub Pro)

⚠️ L'app va in "sleep" dopo **7 giorni di inattività**, ma si riattiva automaticamente al primo accesso (15-20 secondi).

---

## 🔧 Alternative (Se Streamlit Cloud Non Va Bene)

### 1. **Render** (Piano Gratuito)
- Pro: Supporto Docker, database inclusi
- Contro: Più complesso da configurare, app va in sleep dopo 15 min
- [Guida Deploy Render](https://docs.render.com/deploy-streamlit)

### 2. **Railway** (Piano Gratuito con Limiti)
- Pro: Deploy da GitHub facile
- Contro: $5 credito mensile gratuito (si esaurisce velocemente)
- [Guida Railway](https://railway.app/template/streamlit)

### 3. **PythonAnywhere** (Piano Gratuito Limitato)
- Pro: Shell Python completo
- Contro: Solo 1 app web, configurazione manuale
- [Guida PythonAnywhere](https://help.pythonanywhere.com/pages/Streamlit/)

### 4. **Hugging Face Spaces** (GRATUITO)
- Pro: Gratuito, comunità AI
- Contro: Richiede file di configurazione aggiuntivi
- [Guida Hugging Face](https://huggingface.co/docs/hub/spaces-sdks-streamlit)

**Raccomandazione**: Per semplicità e zero costi, resta su **Streamlit Community Cloud**.

---

## 📞 Supporto

- **Documentazione Streamlit Cloud**: https://docs.streamlit.io/streamlit-community-cloud
- **Forum Streamlit**: https://discuss.streamlit.io/
- **Troubleshooting**: https://docs.streamlit.io/knowledge-base/deploy

---

## ✅ Checklist Pre-Deploy

- [x] `requirements.txt` creato ✅
- [x] `.streamlit/config.toml` configurato ✅
- [x] `.gitignore` corretto ✅
- [ ] Repository GitHub creato
- [ ] Codice caricato su GitHub
- [ ] App deployata su Streamlit Cloud

---

## 🎯 Prossimi Passi

1. **Ora**: Segui i 4 passaggi sopra per il deploy
2. **Dopo il deploy**: Condividi l'URL con gli utenti
3. **Futuro**: Considera di aggiungere autenticazione se necessario

**Buon deploy! 🚀**
