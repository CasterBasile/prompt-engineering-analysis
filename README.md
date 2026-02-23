# 🔍 Prompt Engineering Analyzer - Sistema Completo di Analisi e Validazione

Sistema integrato per l'analisi automatica e validazione manuale delle tecniche di Prompt Engineering utilizzate per Unit Testing con Large Language Models (LLM).

## 📁 Struttura Progetto

```
Progetto ST/
├── 🐍 APPLICAZIONE STREAMLIT
│   ├── app.py                      # Web app principale (3 fasi)
│   ├── requirements.txt            # Dipendenze Python
│   ├── run_app.bat                 # Avvio rapido Windows
│   ├── setup.bat                   # Setup ambiente
│   ├── deploy_to_github.bat        # 🆕 Script deploy automatico
│   ├── Prompt.xlsx                 # Dataset (225 prompt)
│   ├── validations_backup.json     # Backup automatico validazioni
│   └── .streamlit/config.toml      # Configurazione
│
├── 📄 DOCUMENTO LATEX
│   └── Documento_LaTeX/
│       ├── documento_analisi.tex   # Articolo finale
│       ├── figures/                # Grafici
│       └── README.md               # Istruzioni compilazione
│
└── 📚 DOCUMENTAZIONE
    ├── README.md                   # Questo file
    └── DEPLOY.md                   # 🆕 Guida completa deploy online
```

## 📋 Descrizione

Questo progetto analizza **225 prompt** sviluppati da 75 studenti per la generazione di unit test su tre applicazioni Java:
- **TennisScoreManager**: Gestione punteggio tennis
- **SubjectParser**: Parser di stringhe soggetto-verbo-predicato
- **HSLColor**: Conversione colori HSL

## ✨ Funzionalità Principali

### 🔄 Sistema di Autosalvataggio Automatico
- **Backup automatico** dopo ogni validazione manuale
- **Recupero automatico** all'avvio dell'app
- **Salvataggio manuale** disponibile in sidebar
- **Caricamento backup** da file JSON in qualsiasi momento
- **Protezione perdita dati** anche dopo 225+ validazioni

### 📂 FASE 1: Caricamento e Analisi Automatica
- Upload intuitivo di file `.xlsx`
- Estrazione automatica dei prompt da tre sezioni
- Classificazione automatica con algoritmo semplificato
- Identificazione casi dubbi (< 70% confidenza)
- Dashboard con metriche in tempo reale

### ✏️ FASE 2: Validazione Manuale Casi Dubbi
- Focus solo sui casi dubbi identificati dall'algoritmo
- 5 opzioni di validazione:
  - ✅ **Conferma Algoritmo**: L'algoritmo ha ragione
  - ✅ **Corretta**: Lo studente aveva ragione
  - ⚠️ **Parziale**: Aggiunge tecniche a risposta studente
  - ❌ **Errata**: Correzione completa
  - 🗑️ **Scarta**: Prompt non valido
- **Motivazioni preimpostate** per ogni tecnica (40+ opzioni)
- **Note personalizzate** per ogni validazione
- **Paginazione** per navigare tra i casi
- **Autosalvataggio** dopo ogni validazione

### 📊 FASE 3: Statistiche e Risultati Finali
Dashboard completa con:
- **Distribuzione tecniche** di prompting
- **Distribuzione LLM** utilizzati
- **Confronto** Studenti vs Algoritmo
- **Tasso di errore** per applicazione
- **Match types** (esatti, parziali, errori)
- **Statistiche dettagliate** per modello LLM
- **Statistiche dettagliate** per tecnica
- **Matrice di confusione** Studente vs Corretto

### 💾 Sistema di Download ed Esportazione
1. **Report Completo Excel** (multi-foglio):
   - Risultati finali completi
   - Statistiche per modello LLM
   - Statistiche per tecnica di prompting
   - Matrice di confusione
   
2. **Statistiche CSV** (scaricabili separatamente):
   - CSV statistiche LLM
   - CSV statistiche tecniche
   - CSV matrice confusione

3. **Backup validazioni JSON** (per riprendere lavoro)

## 🚀 Avvio Rapido

### Installazione
```bash
# 1. Installa dipendenze
python -m pip install -r requirements.txt

# Oppure su Windows
setup.bat
```

### Esecuzione
```bash
# Metodo 1: Script bat (Windows)
run_app.bat

# Metodo 2: Comando diretto
streamlit run app.py
```

### Utilizzo
1. **Carica file** `Prompt.xlsx` dalla sidebar
2. **Visualizza analisi** automatica nella Fase 1
3. **Procedi a Fase 2** per validare i casi dubbi
4. **Valida prompt** uno per uno (con autosalvataggio)
5. **Procedi a Fase 3** per statistiche finali
6. **Scarica report** Excel completo

### ⚠️ Recupero da Backup
Se l'app si chiude durante la validazione:
1. Riapri l'app: il backup viene **caricato automaticamente**
2. Oppure: usa **"📥 Carica Backup Validazioni"** in sidebar
3. Riprendi esattamente da dove avevi lasciato

## 🎯 Tecniche di Prompting Supportate

### 1. Tecniche Fondamentali
- **Structured CoT (SCoT)**: Guida attraverso strutture di programmazione (loop, branch, condizioni)
- **Persona/Role Prompting**: Assegnazione di ruoli specifici (es. "Agisci come un QA Engineer")
- **Combinazioni**: Riconoscimento di tecniche multiple (es. "Persona + Few-Shot")

### 3. **🎯 Matching Intelligente delle Classificazioni (v1.2.0+)**

**Nuovo Sistema di Validazione Automatica**

L'algoritmo ora distingue tra **tre tipi di match** quando confronta la classificazione dello studente con quella rilevata:

#### ✅ **Match Esatto** (Exact Match)
Lo studente ha classificato **esattamente** la tecnica principale identificata dall'algoritmo.

**Esempio:**
```
Algoritmo rileva: "Few-Shot"
Studente scrive: "Few-Shot"
→ Match Esatto ✅
```

#### ⚠️ **Match Parziale** (Partial Match)
Lo studente ha menzionato **una delle tecniche rilevate**, ma:
- Non ha nominato la tecnica principale, OPPURE
- Ha dato una classificazione incompleta (es. ha scritto solo "Few-Shot" quando il prompt conteneva anche "Persona")

**Importante**: I match parziali **NON sono errori**! Indicano che lo studente ha **capito il prompt** ma non ha fornito la classificazione più completa.

**Esempio:**
```
Prompt: "You are a QA engineer. Example 1: test_add()... Example 2: test_subtract()..."
Algoritmo rileva: ["Persona/Role Prompting", "Few-Shot"]
Classificazione principale: "Persona + Few-Shot"
Studente scrive: "Few-Shot"
→ Match Parziale ⚠️ (lo studente ha menzionato una tecnica valida)
```

#### ❌ **Errore** (True Error)
La classificazione dello studente **non corrisponde a NESSUNA** delle tecniche rilevate dall'algoritmo. Questo è un **vero errore** di classificazione.

**Esempio:**
```
Algoritmo rileva: "Few-Shot"
Studente scrive: "Chain-of-Thought"
→ Errore Vero ❌
```

#### 📊 **Calcolo Tasso di Errore Migliorato**
```
Tasso Errore = (Solo Errori Veri / Totale Prompt) × 100
```

**Solo gli errori veri vengono contati**. Match esatti e parziali sono considerati classificazioni corrette (o incomplete ma non sbagliate).

**Impatto:**
- ✅ **Riduzione falsi positivi**: Studenti con classificazioni parziali non più penalizzati
- ✅ **Maggiore accuratezza**: Tasso di errore riflette meglio le reali difficoltà degli studenti
- ✅ **Analisi più sfumata**: Possibilità di distinguere between "ha sbagliato" vs "non ha approfondito"

**Nuove Metriche Visualizzate:**
- 🟢 **Match Esatti**: Classificazioni perfette
- 🟡 **Match Parziali**: Classificazioni incomplete ma valide
- 🔴 **Errori Veri**: Classificazioni sbagliate

**Tracciamento Tecniche Multiple:**
L'algoritmo ora traccia **tutte** le tecniche rilevate in un prompt, non solo la principale, permettendo confronti più intelligenti con le classificazioni degli studenti.

---

### 4. **Dashboard Statistica Interattiva (Plotly)**

#### 📊 Varietà delle Tecniche
- Frequency Bar Chart delle tecniche identificate
- Visualizzazione colorata con conteggi

#### 📊 Distribuzione LLM
- Pie Chart dei modelli utilizzati dagli studenti
- Percentuali e labels interattive

#### 🎯 Qualità delle Classificazioni Studenti (NUOVO v1.2.0!)
**Pie Chart dei Match Types:**
- 🟢 **Match Esatti** (verde): Classificazioni perfette
- 🟡 **Match Parziali** (giallo): Classificazioni incomplete ma valide
- 🔴 **Errori Veri** (rosso): Classificazioni errate

Visualizzazione immediata della **distribuzione qualitativa** delle classificazioni degli studenti.

#### 🎯 Tasso di Errore degli Studenti
**Cosa rappresenta:** Percentuale di **errori veri** commessi dagli studenti (ora escludendo i match parziali)

**Calcolo:** `(N° errori veri / Totale prompt) × 100`

**⚠️ IMPORTANTE:** Gli errori sono **già stati corretti automaticamente** dall'algoritmo. Questo valore mostra solo quanti **veri errori** hanno fatto gli studenti.

**Visualizzazioni:**
- **Gauge Indicator**: Con range colorati per valutare la performance degli studenti
  - 🟢 Verde (0-25%): Ottimo - Studenti molto accurati
  - 🟡 Giallo (25-50%): Discreto - Alcuni errori
  - 🟠 Arancione (50-75%): Critico - Molti errori
  - 🔴 Rosso (75-100%): Problematico - Maggioranza delle classificazioni errata
- **Bar Chart Comparativo**: Confronto classificazione studente vs algoritmo per ogni tecnica

#### 📊 Metriche in Tempo Reale
Dashboard con **8 metriche** (2 righe):

**Prima riga:**
- Total Prompts
- Errori Studenti (solo errori veri)
- Casi Dubbi
- Confidenza Media
- Tecniche Uniche

**Seconda riga (NUOVA v1.2.0!):**
- ✅ **Match Esatti**: Conteggio e percentuale
- ⚠️ **Match Parziali**: Conteggio e percentuale
- ❌ **Errori Veri**: Conteggio e percentuale

---

### 5. **🔍 Validazione Completa Manuale**

**Interfaccia interattiva per validare TUTTI i prompt uno per uno**

**Caratteristiche:**
- ✅ **Revisione Manuale**: Verifica se l'algoritmo ha classificato correttamente ogni prompt
- 📊 **Confronto Visuale**: Vedi "Studente ha detto X, Algoritmo ha detto Y, tu cosa pensi?"
- 📝 **Motivazioni**: Aggiungi note per spiegare perché l'algoritmo ha ragione/sbagliato
- ⛔ **Esclusione Prompt**: Escludi dalla classificazione prompt non rilevanti, ambigui o corrotti
- ⚡ **Tasso di Errore Dinamico**: Si aggiorna in tempo reale in base alle tue validazioni
- 🧭 **Paginazione**: Naviga tra i prompt con controlli intuitivi (5/10/20/50 per pagina)
- 💾 **Download Progressivo**: Scarica validazioni parziali o complete in Excel

**Come Funziona:**
1. Per ogni prompt vedi: Testo, Classificazione Studente, Classificazione Algoritmo
2. Seleziona dal **menu a tendina** la tecnica corretta (18 tecniche disponibili)
3. Decidi: "L'algoritmo ha ragione?" → Sì/No + Motivazione
4. Salva → Il gauge del tasso di errore si aggiorna automaticamente
5. Continua con i prossimi prompt o scarica i progressi

**🎯 Menu a Tendina Intelligente:**
- Parte con la classificazione dell'algoritmo già selezionata
- Liste tutte le 18 tecniche disponibili
- Facile e veloce: nessun errore di battitura!

**📖 Guida Completa**: Vedi [GUIDA_VALIDAZIONE_COMPLETA.md](GUIDA_VALIDAZIONE_COMPLETA.md)

**🎯 Indicatori Match Types nella Validazione (NUOVO v1.2.0!):**
Nella sezione di validazione completa, ogni prompt mostra il tipo di match:
- 🟢 **Box verde**: Match esatto ✅
- 🟡 **Box giallo**: Match parziale ⚠️ (studente incompleto)
- 🔴 **Box rosso**: Errore vero ❌
- **Tecniche rilevate**: Mostra tutte le tecniche identificate dall'algoritmo

---

### 6. **Esportazione Dati**
Download di file Excel con **7 fogli** (alcuni nuovi in v1.2.0):
- **All_Prompts_Analysis**: Tutti i prompt con classificazioni corrette
  - **NUOVE COLONNE**: `Match_Type`, `All_Detected_Techniques` 
- **Validation_Sample**: 40 prompt campione per validazione manuale
- **Doubtful_Cases**: Casi dubbi da verificare
- **Statistics**: Metriche riassuntive
  - **NUOVE METRICHE**: Exact/Partial/Error counts e percentuali
- **Technique_Distribution**: Distribuzione delle tecniche
- **Student_vs_Algorithm**: Confronto classificazioni
- **LLM_Distribution**: Distribuzione modelli utilizzati

## 🚀 Quick Start

### 🐍 PARTE 1: Analisi con Streamlit

**Passo 1 - Installa Dipendenze**
```bash
pip install -r requirements.txt
```

**Passo 2 - Avvia App**
```bash
streamlit run app.py
# Oppure su Windows:
run_app.bat
```

**Passo 3 - Usa l'Interfaccia**
1. Carica `Prompt.xlsx`
2. Visualizza metriche e grafici
3. Valida campione 40 prompt
4. Scarica Excel completo con risultati

### 📄 PARTE 2: Documento LaTeX

**Passo 1 - Completa Analisi**
- Completa validazione manuale nell'app
- Esporta grafici come PNG in `Documento_LaTeX/figures/`

**Passo 2 - Compila Documento**
```bash
cd Documento_LaTeX
# Su Overleaf: carica documento_analisi.tex
# Locale: pdflatex documento_analisi.tex
```

**Passo 3 - Popola Dati**
- Sostituisci placeholder `[VALORE]` con dati reali
- Decommenta figure dopo aver aggiunto PNG

Vedi `Documento_LaTeX/README.md` per dettagli.

## 🔄 Workflow Completo Progetto

```
1. ⬆️  Carica Prompt.xlsx nell'app Streamlit
2. 📊 Visualizza dashboard con statistiche automatiche
3. ✅ Valida manualmente 40 prompt campione
4. 💾 Esporta Excel completo (7 fogli)
5. 📸 Salva grafici come PNG in Documento_LaTeX/figures/
6. ✏️  Compila placeholders in documento_analisi.tex
7. 🔨 Compila PDF finale con LaTeX
8. 🎉 Consegna progetto completo!
```

## 🚀 Installazione e Utilizzo

### Prerequisiti
- Python 3.8 o superiore
- pip

### Installazione

1. **Clone o scarica questo progetto**

2. **Installa le dipendenze:**
```bash
pip install -r requirements.txt
```

### Avvio dell'Applicazione

#### 🏠 Esecuzione Locale

```bash
streamlit run app.py
```

L'app si aprirà automaticamente nel browser all'indirizzo `http://localhost:8501`

#### 🌐 Deploy Online (GRATIS)

Per rendere l'app accessibile online **gratuitamente**, usa **Streamlit Community Cloud**:

1. Carica il progetto su **GitHub** (repository pubblico o privato)
2. Vai su [share.streamlit.io](https://share.streamlit.io/) e accedi con GitHub
3. Clicca **"New app"** e seleziona il tuo repository
4. L'app sarà online in pochi minuti con URL tipo `https://tua-app.streamlit.app`

**📖 Guida Completa**: Vedi [DEPLOY.md](DEPLOY.md) per istruzioni dettagliate passo-passo.

**🚀 Script Automatico**: Esegui `deploy_to_github.bat` per preparare il repository in automatico.

**✨ Vantaggi**:
- ✅ Completamente gratis
- ✅ HTTPS incluso
- ✅ Aggiornamenti automatici da GitHub
- ✅ Nessun limite di utenti

## 📁 Struttura del File Excel Input

Il file `Prompt.xlsx` deve contenere colonne con pattern simili a:

```
[Application] - Report here the text of the Prompt...
[Application] - Which LLM have you used?
[Application] - Which type of prompt have you used?
```

Dove `[Application]` può essere:
- TennisScoreManager
- SubjectParser
- HSLColor

### Esempio di Struttura

| TennisScoreManager - Report here the text of the Prompt... | TennisScoreManager - Which LLM have you used? | TennisScoreManager - Which type of prompt have you used? | SubjectParser - Report here the text... | ... |
|-------------------------------------------------------------|-----------------------------------------------|----------------------------------------------------------|----------------------------------------|-----|
| "Act as a QA engineer. Generate unit tests for..."         | ChatGPT-4                                     | Few-Shot                                                 | "Create tests step by step..."         | ... |

## 🔬 Algoritmo di Classificazione

### Euristiche Implementate

L'algoritmo usa pattern regex per identificare:

1. **Persona/Role Prompting** (priorità alta):
   - Pattern: `act as`, `agisci come`, `you are a`, `expert`, `QA engineer`

2. **Structured CoT**:
   - Pattern: `for each`, `if...then...else`, `loop through`, `iterate`, `branch`

3. **Chain-of-Thought**:
   - Pattern: `step by step`, `passo dopo passo`, `think through`, `ragiona`

4. **Few-Shot**:
   - Blocchi di codice: ` ``` `
   - Esempi: `example:`, `for instance`, `ad esempio`
   - Codice: `public class`, `def`, `function`
   - Conta almeno 2 indicatori per ridurre falsi positivi

5. **Zero-Shot** (default):
   - Assegnato quando non ci sono indicatori delle altre tecniche

### Classificazione Gerarchica

Le tecniche sono identificate con priorità:
1. Structured CoT (più specifico)
2. Chain-of-Thought
3. Few-Shot
4. Persona/Role
5. Zero-Shot (default)

Le combinazioni sono supportate (es. "Persona + Few-Shot CoT").

## 📊 Dashboard e Visualizzazioni

### Metriche Principali
- Total Prompts analizzati
- Correzioni Necessarie (con percentuale)
- Tecniche Uniche identificate
- LLM Utilizzati

### Grafici Interattivi
1. **Bar Chart**: Frequenza delle tecniche
2. **Pie Chart**: Distribuzione LLM
3. **Grouped Bar Chart**: Confronto classificazioni
4. **Gauge Chart**: Tasso di errore generale

### Filtri Interattivi
- Filtra per Applicazione
- Filtra per LLM
- Mostra solo correzioni necessarie

## 💾 Output e Export

Il file Excel esportato contiene:

### Sheet 1: Analyzed_Prompts
- Application
## 📥 Output e Download

L'applicazione genera i seguenti file:

### 1. Excel Report Completo (4 fogli)
**File**: `Report_Completo_Analisi_Prompting.xlsx`

#### Foglio 1: Risultati_Finali
- Tutti i prompt con classificazione finale
- Validazioni manuali applicate
- Note e motivazioni
- Confidenza e match type

#### Foglio 2: Statistiche_LLM
- Tot. Prompts per modello
- % Errori studenti
- Tecnica più usata
- Validazioni manuali

#### Foglio 3: Statistiche_Tecniche
- Tot. Prompts per tecnica
- % sul totale
- Match esatti ed errori
- LLM predominante
- Confidenza media

#### Foglio 4: Matrice_Confusione
- Classificazione Studente vs Finale
- Conteggio occorrenze
- Match type

### 2. File CSV Individuali
- `statistiche_per_LLM.csv`
- `statistiche_per_tecnica.csv`
- `matrice_confusione.csv`

### 3. Backup Validazioni
- `validations_backup.json` (autosalvato automaticamente)

## 🛠️ Tecnologie Utilizzate

- **Streamlit 1.32+**: Framework per web app interattive
- **Pandas**: Manipolazione e analisi dati
- **Plotly**: Visualizzazioni grafiche interattive
- **OpenPyXL**: Lettura e scrittura file Excel multi-foglio
- **Python 3.8+**: Regex, JSON, datetime

## 💡 Best Practices

### Durante la Validazione
1. ✅ **Salva spesso**: L'autosalvataggio funziona dopo ogni validazione, ma puoi salvare manualmente dalla sidebar
2. 📝 **Usa le motivazioni**: Seleziona motivazioni preimpostate per velocizzare il lavoro
3. 📋 **Aggiungi note**: Per casi complessi, aggiungi note personalizzate
4. ⏸️ **Prenditi pause**: Usa la paginazione per fare pause senza perdere progressi
5. 💾 **Backup multipli**: Scarica il backup JSON periodicamente come sicurezza extra

### Interpretazione Statistiche
- **% Errori < 25%**: Performance eccellente studenti
- **% Errori 25-50%**: Performance buona
- **% Errori > 50%**: Necessaria revisione didattica
- **Confidenza < 70%**: Caso dubbio (validazione manuale)
- **Match Parziale**: Studente ha capito parzialmente

### Esportazione Dati
1. Usa **Report Completo Excel** per analisi approfondite
2. Usa **CSV** per importare in altri strumenti (R, SPSS, Excel avanzato)
3. Conserva **backup JSON** per riprendere validazioni

## 🔄 Workflow Completo

### Preparazione
1. Assicurati di avere `Prompt.xlsx` nella cartella
2. Installa dipendenze con `setup.bat` (solo prima volta)
3. Avvia app con `run_app.bat`

### Fase 1: Analisi Automatica (2-5 minuti)
1. Carica file dalla sidebar
2. Attendi analisi automatica
3. Esamina dashboard metriche
4. Procedi a Fase 2

### Fase 2: Validazione Manuale (30-60 minuti per 225 prompt)
1. Valida solo i casi dubbi (automaticamente filtrati)
2. Usa motivazioni preimpostate quando possibile
3. Salva periodicamente (già automatico)
4. Procedi a Fase 3 quando completato

### Fase 3: Analisi Risultati (5-10 minuti)
1. Esplora grafici interattivi
2. Esamina statistiche dettagliate
3. Scarica Report Completo Excel
4. Scarica CSV per analisi esterne

## ⚠️ Troubleshooting

### ❌ "App si chiude durante validazione"
**Soluzione**: Il backup è automatico! Riapri l'app e il progresso viene recuperato automaticamente.

### ❌ "Non vedo il backup caricato"
**Soluzione**: 
1. Vai in sidebar → "📥 Carica Backup Validazioni"
2. Seleziona `validations_backup.json`
3. Premi 'R' per ricaricare

### ❌ "Excel non si apre / errore download"
**Soluzione**: 
1. Verifica di avere Excel/LibreOffice installato
2. Controlla che il browser non blocchi il download
3. Prova a scaricare CSV invece di Excel

### ❌ "Nessun prompt trovato nel file"
**Soluzione**:
- Verifica che il file si chiami esattamente `Prompt.xlsx`
- Controlla che ci siano colonne con i pattern attesi
- Assicurati che ci siano dati nelle colonne rilevanti

## 📚 Riferimenti

Basato sulla tassonomia del paper:
*"A Systematic Survey of Prompt Engineering in Large Language Models: Techniques and Applications"*

Tecniche implementate:
- Zero-Shot, Few-Shot
- Chain-of-Thought (CoT) e varianti
- Persona/Role Prompting
- Constraint-Based Prompting
- Self-Refine, Fix-Prompt
- E molte altre (40+ tecniche totali)

## 🎓 Scopo Educativo

Sviluppato come supporto per esercitazioni universitarie di **Software Testing** con focus su:
- 🤖 Large Language Models (LLM) per testing
- ✅ Unit Testing automatizzato
- 📝 Prompt Engineering sistematico
- 📊 Analisi qualitativa e quantitativa dei dati

## 📊 Dati di Esempio

Il dataset include:
- **225 prompt** totali
- **75 studenti** (3 prompt ciascuno)
- **3 applicazioni** Java (TennisScoreManager, SubjectParser, HSLColor)
- **10+ modelli LLM** utilizzati (GPT-4, Gemini, Claude, ecc.)
- **15+ tecniche** di prompting rilevate

## 🔐 Privacy e Sicurezza

- ✅ Tutti i dati rimangono **locali** (nessun upload a server esterni)
- ✅ Backup JSON salvati solo sul tuo computer
- ✅ Download Excel/CSV gestiti dal browser
- ✅ Nessuna telemetria o tracking

## 📝 Note Tecniche

- Supporta file Excel `.xlsx` e `.xls`
- Gestisce prompt in **italiano** e **inglese**
- Classificazione **case-insensitive**
- Normalizzazione automatica nomi LLM
- Gestione automatica valori null/vuoti

## 🚀 Aggiornamenti Futuri

Possibili miglioramenti:
- [ ] Export PDF dei report
- [ ] Grafici personalizzabili
- [ ] Filtri avanzati per ricerca
- [ ] Integrazione con API LLM per validazione automatica
- [ ] Dashboard comparativa multi-dataset

---

**Versione**: 2.0 - Sistema Completo con Autosalvataggio  
**Data**: Febbraio 2026  
**Licenza**: Academic Use  
**Python**: 3.8+  
**Streamlit**: 1.32+

💡 **Tip**: Per supporto o domande, consulta la guida nell'app (sidebar → 📖 Guida Tecniche)
