# Prompt Engineering Analysis Tool

## Descrizione del Tool

Questo strumento web è stato sviluppato per supportare la validazione manuale sistematica delle tecniche di prompt engineering utilizzate dagli studenti in un contesto di testing del software con Large Language Models (LLM).

## Scopo e Motivazione

L'obiettivo principale del tool è permettere la **validazione manuale accurata e veloce** di un elevato numero di prompt (centinaia di istanze), fornendo un'interfaccia intuitiva che:

1. **Carica e visualizza** i prompt raccolti dagli studenti
2. **Presenta** ogni prompt in modo strutturato con informazioni contestuali (applicazione, LLM utilizzato, classificazione dello studente)
3. **Facilita la validazione** tramite un'interfaccia a scelta multipla che permette di confermare o correggere rapidamente la classificazione
4. **Salva automaticamente** i progressi per evitare perdite di dati
5. **Esporta i risultati** in formato Excel per ulteriori analisi

Il tool è stato progettato per essere utilizzato da un valutatore umano che deve processare manualmente centinaia di prompt, riducendo i tempi necessari mantenendo l'accuratezza della validazione.

## Algoritmo di Classificazione Automatica

Durante lo sviluppo, è stato implementato un **algoritmo sperimentale basato su euristiche** per tentare la classificazione automatica delle tecniche di prompting. L'algoritmo utilizza:

- Pattern matching su parole chiave specifiche
- Analisi della struttura del prompt
- Riconoscimento di pattern comuni (es. "act as", esempi numerati, ragionamento step-by-step)

Tuttavia, l'accuratezza dell'algoritmo si è rivelata limitata, evidenziando la complessità della classificazione automatica delle tecniche di prompting. Questo ha rafforzato la necessità della validazione manuale.

### Sviluppi Futuri

Il sistema potrebbe essere migliorato con:
- Algoritmi di machine learning allenati su dataset annotati manualmente
- Modelli di linguaggio fine-tuned specificamente per la classificazione di tecniche di prompting
- Approcci ibridi che combinano euristiche e modelli statistici

## Tecnologie Utilizzate

Il tool è stato sviluppato interamente in **Python** utilizzando:

- **Streamlit**: Framework per la creazione dell'interfaccia web interattiva
- **Pandas**: Gestione e manipolazione dei dati in formato tabellare
- **Plotly**: Creazione di visualizzazioni grafiche interattive
- **OpenPyXL**: Lettura e scrittura di file Excel

## Architettura

L'applicazione segue un'architettura multi-fase:

1. **Fase 1**: Caricamento dati e analisi automatica preliminare
2. **Fase 2**: Validazione manuale dei casi dubbi
3. **Fase 2.2**: Esportazione delle risposte validate come corrette
4. **Fase 3**: Visualizzazione statistiche e metriche finali

## Accesso al Tool

L'applicazione è accessibile pubblicamente all'indirizzo:
**https://mptsanalysis.streamlit.app/**

Il deployment è gestito tramite Streamlit Cloud, che permette l'hosting gratuito di applicazioni Streamlit.

## Utilizzo nel Contesto della Ricerca

Questo tool è stato utilizzato per:
- Validare le classificazioni degli studenti delle tecniche di prompting
- Identificare pattern comuni e errori di classificazione
- Raccogliere metriche quantitative sull'accuratezza delle classificazioni studentesche
- Analizzare la distribuzione delle tecniche utilizzate

I dati validati tramite questo strumento sono stati utilizzati per l'analisi presentata nel paper.

---

*Sviluppato da: Castrese Basile*  
*Corso: Software Testing - Prof. Porfirio Tramontana*  
*Università degli Studi di Napoli Federico II*
