# 📄 Documento LaTeX - Analisi Prompt Engineering

Questo documento presenta l'analisi delle tecniche di prompt engineering utilizzate dagli studenti per la generazione di unit test con LLM.

## 📁 Struttura Cartella

```
Documento_LaTeX/
├── documento_analisi.tex    # Documento principale
├── figures/                  # [Da creare] Grafici e immagini
│   ├── technique_distribution.png
│   ├── llm_distribution.png
│   └── student_vs_algorithm.png
└── README.md                 # Questo file
```

## 🚀 Come Compilare

### Opzione 1: Overleaf (Consigliato)

1. Vai su [Overleaf](https://www.overleaf.com)
2. Crea nuovo progetto → "Upload Project"
3. Carica `documento_analisi.tex`
4. Compila automaticamente!

### Opzione 2: Locale (Windows con MiKTeX/TeX Live)

```cmd
cd "c:\Users\basil\Desktop\Progetto ST\Documento_LaTeX"
pdflatex documento_analisi.tex
pdflatex documento_analisi.tex
```

(Compilare due volte per aggiornare riferimenti e indice)

### Opzione 3: Visual Studio Code

1. Installa estensione "LaTeX Workshop"
2. Apri `documento_analisi.tex`
3. Clicca sull'icona "Build LaTeX project" oppure premi `Ctrl+Alt+B`

## 📊 Come Aggiungere i Grafici

### 1. Esporta Grafici dalla Dashboard Streamlit

Esegui l'app Streamlit e salva i grafici:
- Dashboard → Grafici → Salva come PNG

### 2. Crea Cartella Figures

```cmd
mkdir figures
```

### 3. Salva i File

Salva nella cartella `figures/`:
- `technique_distribution.png` - Distribuzione tecniche
- `llm_distribution.png` - Distribuzione LLM
- `student_vs_algorithm.png` - Confronto classificazioni

### 4. Decommenta nel .tex

Nel file `documento_analisi.tex`, trova le righe commentate:

```latex
%\begin{figure}[htbp]
%\centering
%\includegraphics[width=\linewidth]{figures/technique_distribution}
%\caption{Distribuzione tecniche di prompting}
%\label{fig:techniques}
%\end{figure}
```

Rimuovi i `%` per attivarle:

```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/technique_distribution}
\caption{Distribuzione tecniche di prompting}
\label{fig:techniques}
\end{figure}
```

## ✏️ Placeholders da Compilare

Dopo aver completato l'analisi con l'app Streamlit, sostituisci i placeholders:

- `[VALORE]` - Con i valori numerici effettivi
- `[X]` - Con le percentuali
- `[N]` - Con i conteggi
- `[NOME]` - Con nomi delle tecniche

Cerca nel documento: `\textit{[Da compilare` per trovare tutte le sezioni.

## 🎨 Personalizzazione Colori

Nel file `.tex`, modifica le definizioni colore (righe 22-25):

```latex
\definecolor{primarycolor}{RGB}{0,51,102}      % Blu navy
\definecolor{secondarycolor}{RGB}{0,102,204}   % Blu chiaro
\definecolor{accentcolor}{RGB}{220,50,47}      % Rosso
```

Cambia i valori RGB per personalizzare:
- `primarycolor`: Titoli sezioni
- `secondarycolor`: Sottotitoli e link
- `accentcolor`: Accenti (non usato molto)

## 📋 Checklist Pre-Compilazione

- [ ] Analisi completata con app Streamlit
- [ ] Excel esportato con tutti i fogli
- [ ] Grafici salvati in `figures/`
- [ ] Placeholders `[VALORE]` sostituiti
- [ ] Sezioni `[Da compilare]` completate
- [ ] Bibliografia verificata
- [ ] Figure decommentate

## 🐛 Problemi Comuni

### Errore: "File not found: figures/..."

**Soluzione**: Crea la cartella `figures/` o commenta le righe `\includegraphics`

### Errore: "Missing $ inserted"

**Soluzione**: Caratteri speciali (`%`, `_`, `&`) devono essere escaped: `\%`, `\_`, `\&`

### Errore: "Undefined control sequence"

**Soluzione**: Assicurati di avere tutti i pacchetti installati. Su MiKTeX installa al volo, su Linux:
```bash
sudo apt-get install texlive-full
```

## 📮 Output

Dopo compilazione, troverai:
- `documento_analisi.pdf` - Documento finale
- `documento_analisi.aux`, `.log`, `.out` - File temporanei (ignorabili)

## 🎯 Prossimi Passi

1. **Completa l'analisi** con l'app Streamlit
2. **Valida il campione** di 40 prompt
3. **Esporta i dati** in Excel
4. **Compila il documento** sostituendo placeholders
5. **Aggiungi i grafici**
6. **Compila PDF finale**
7. **Consegna!** 🎉

---

**Autore**: Castrese Basile  
**Corso**: Software Testing  
**Docente**: Prof. Porfirio Tramontana  
**Università**: Università degli Studi di Napoli Federico II  
**Anno**: A.A. 2025/2026
