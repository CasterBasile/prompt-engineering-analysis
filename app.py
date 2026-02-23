"""
Web App Streamlit per l'Analisi Sistematica di Prompt Engineering
Sviluppata come supporto per l'esercitazione universitaria su LLM e Unit Testing
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import re
import json
from datetime import datetime
import os

# Configurazione pagina
st.set_page_config(
    page_title="Prompt Engineering Analyzer",
    page_icon="🔍",
    layout="wide"
)

# ===== MOTIVAZIONI PREIMPOSTATE PER TECNICHE =====
MOTIVAZIONI_PREIMPOSTATE = {
    "Few-Shot": [
        "Contiene esempi concreti di input/output",
        "Fornisce scenari di test specifici",
        "Include casi d'uso dettagliati con dati",
        "Presenta test case numerati o strutturati",
        "Mostra esempi di codice o assert statement",
        "Usa pattern 'Given-When-Then' o simili"
    ],
    "Chain-of-Thought": [
        "Richiede ragionamento passo-passo esplicito",
        "Usa espressioni sequenziali (first...then...finally)",
        "Chiede analisi step-by-step del problema",
        "Richiede processo di pensiero iterativo",
        "Usa frasi come 'think through', 'walk through'",
        "Descrive un flusso logico di operazioni"
    ],
    "Persona": [
        "Definisce un ruolo specifico (es. QA engineer, tester)",
        "Usa costrutti 'act as' o 'you are'",
        "Assegna expertise o competenze specifiche",
        "Richiede prospettiva professionale particolare",
        "Definisce il livello di esperienza (senior, expert, etc.)"
    ],
    "Constraint": [
        "Specifica vincoli tecnici espliciti",
        "Definisce requisiti obbligatori di output",
        "Limita lo scope o formato della risposta",
        "Impone restrizioni su tecnologie/linguaggi",
        "Richiede conformità a standard specifici"
    ],
    "Self-Refine": [
        "Richiede iterazioni o miglioramenti progressivi",
        "Chiede revisione o ottimizzazione del codice",
        "Usa termini come 'refine', 'improve', 'enhance'",
        "Richiede validazione e correzione iterativa",
        "Chiede di verificare e migliorare la soluzione"
    ],
    "Zero-Shot": [
        "Nessuna tecnica di prompting evidente",
        "Richiesta diretta senza esempi o struttura",
        "Prompt generico senza guida metodologica",
        "Manca contesto o esempi di supporto"
    ]
}

# Motivazioni per combinazioni comuni di tecniche
MOTIVAZIONI_COMBINAZIONI = {
    "Few-Shot + Chain-of-Thought": [
        "Combina esempi concreti con ragionamento sequenziale",
        "Esempi presentati in passi logici",
        "Mostra il processo di pensiero attraverso esempi"
    ],
    "Persona + Chain-of-Thought": [
        "Ruolo definito che applica approccio step-by-step",
        "Expertise specifica applicata metodicamente",
        "Prospettiva professionale con analisi strutturata"
    ],
    "Few-Shot + Constraint": [
        "Esempi che rispettano vincoli specifici",
        "Casi d'uso con limitazioni definite",
        "Scenari vincolati a requisiti particolari"
    ],
    "Persona + Few-Shot": [
        "Ruolo specifico che fornisce esempi dal proprio dominio",
        "Expertise dimostrata attraverso casi concreti",
        "Esempi filtrati dalla prospettiva del ruolo"
    ]
}

# ===== FUNZIONI DI SALVATAGGIO/CARICAMENTO =====
def save_validations_to_file(validations, filename='validations_backup.json'):
    """Salva le validazioni manuali in un file JSON"""
    try:
        backup_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_validations': len(validations),
            'validations': {str(k): v for k, v in validations.items()}  # Converti chiavi in stringhe per JSON
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        return True, filename
    except Exception as e:
        return False, str(e)

def load_validations_from_file(filename='validations_backup.json'):
    """Carica le validazioni manuali da un file JSON"""
    try:
        if not os.path.exists(filename):
            return None, "File non trovato"
        
        with open(filename, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Converti chiavi da stringhe a interi
        validations = {int(k): v for k, v in backup_data['validations'].items()}
        return validations, backup_data.get('timestamp', 'N/A')
    except Exception as e:
        return None, str(e)

def auto_save_validations():
    """Auto-salva le validazioni dopo ogni modifica"""
    if st.session_state.manual_validations:
        save_validations_to_file(
            st.session_state.manual_validations,
            st.session_state.backup_file
        )

# Inizializza session state per gestione fasi
if 'current_phase' not in st.session_state:
    st.session_state.current_phase = 1  # Fase 1: Caricamento & Analisi

if 'analyzed_data' not in st.session_state:
    st.session_state.analyzed_data = None

if 'backup_choice_made' not in st.session_state:
    st.session_state.backup_choice_made = False

if 'filter_validated' not in st.session_state:
    st.session_state.filter_validated = False  # Se True, mostra solo non validate

if 'manual_validations' not in st.session_state:
    st.session_state.manual_validations = {}  # {idx: {'is_correct': bool, 'corrected_technique': str or list}}
    
    # Tentativo di recupero automatico dal backup
    if os.path.exists('validations_backup.json'):
        loaded_vals, timestamp = load_validations_from_file('validations_backup.json')
        if loaded_vals is not None:
            st.session_state.manual_validations = loaded_vals
            st.session_state.backup_recovered = True
            st.session_state.backup_timestamp = timestamp
            st.session_state.backup_count = len(loaded_vals)

if 'validation_page' not in st.session_state:
    st.session_state.validation_page = 0

if 'backup_file' not in st.session_state:
    st.session_state.backup_file = 'validations_backup.json'

# Progress Bar per le fasi
st.markdown("""
<style>
.phase-container {
    display: flex;
    justify-content: space-between;
    margin: 20px 0;
    padding: 15px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
}
.phase-step {
    flex: 1;
    text-align: center;
    padding: 10px;
    margin: 0 5px;
    border-radius: 8px;
    color: white;
    font-weight: bold;
    transition: all 0.3s;
}
.phase-active {
    background: rgba(255, 255, 255, 0.3);
    border: 2px solid white;
    transform: scale(1.05);
}
.phase-completed {
    background: rgba(40, 167, 69, 0.6);
}
.phase-pending {
    background: rgba(255, 255, 255, 0.1);
    opacity: 0.7;
}
</style>
""", unsafe_allow_html=True)

# Titolo principale
st.title("🔍 Analisi Sistematica di Prompt Engineering - Multi-Fase")
st.markdown("""
Applicazione per l'analisi automatica e validazione manuale delle tecniche di prompting  
secondo la tassonomia del paper *'A Systematic Survey of Prompt Engineering in Large Language Models'*  
e del corso di **Software Testing** tenuto dal **Prof. Porfirio Tramontana**  
Università degli Studi di Napoli Federico II

**A cura di:** Castrese Basile
""")

# Mostra info se backup trovato (ma non bloccare)
if 'backup_recovered' in st.session_state and st.session_state.backup_recovered and not st.session_state.backup_choice_made:
    st.info(f"🔄 **Backup trovato**: {st.session_state.backup_count} validazioni del {st.session_state.get('backup_timestamp', 'N/A')}. Carica il file per continuare.")


# Dizionario descrizioni tecniche di prompting
TECHNIQUE_DESCRIPTIONS = {
    # 1. Tecniche Fondamentali (Basic)
    "Zero-Shot": "Fornire solo la descrizione del task senza esempi.",
    "Few-Shot": "Includere alcuni esempi di input-output nel prompt.",
    
    # 2. Ragionamento e Logica
    "Chain-of-Thought": "Richiedere un ragionamento passo-passo.",
    "Auto-CoT": "Generazione automatica di catene di ragionamento.",
    "LogiCoT": "Quadro neurosimbolico basato sulla logica simbolica per verificare i passaggi.",
    "LCoT": "Framework specifico per il testing basato su analisi funzionale e percorsi di esecuzione.",
    "Tree-of-Thoughts": "Esplorazione di più percorsi di ragionamento a struttura ramificata.",
    "Graph-of-Thought": "Modellazione del ragionamento come un grafico non lineare.",
    "Self-Consistency": "Generazione di più catene di ragionamento per selezionare la risposta più coerente.",
    "System-2-Attention": "Rigenerazione del contesto per concentrarsi solo sulle parti rilevanti.",
    
    # 3. Generazione di Codice ed Esecuzione
    "Structured CoT": "Incorpora strutture di programmazione (loop, branch) nei passaggi di pensiero.",
    "Program-of-Thoughts": "Utilizzo di codice eseguibile per gestire passaggi di calcolo o logica complessa.",
    "Chain-of-Code": "Scrittura di pseudocodice simulato da un 'LMulator' per compiti semantici e logici.",
    "Scratchpad": "Generazione di token intermedi prima della risposta finale per calcoli algoritmici.",
    
    # 4. Metacognizione e Autocorrezione
    "Self-Refine": "Iterazione basata su feedback autogenerato (critica e raffinamento).",
    "Take-a-Step-Back": "Estrazione di concetti di alto livello prima di risolvere il problema specifico.",
    "Fix-Prompt": "Utilizzo dei log di errore per correggere test non compilabili o falliti.",
    
    # 5. Altre tecniche
    "Persona/Role Prompting": "Assegnazione di un ruolo o persona specifica all'LLM.",
    
    # Combinazioni
    "Persona + Few-Shot": "Combinazione di assegnazione ruolo con esempi.",
    "Persona + Chain-of-Thought": "Combinazione di assegnazione ruolo con ragionamento passo-passo.",
    "Persona + Structured CoT": "Combinazione di assegnazione ruolo con strutture di programmazione.",
    "Few-Shot CoT": "Combinazione di esempi con ragionamento passo-passo.",
    "Unknown": "Tecnica non riconosciuta o testo non valido.",
}


def normalize_llm_name(llm_text):
    """
    Normalizza i nomi degli LLM per raggruppare varianti simili.
    
    Gestisce:
    - Case insensitive (gemini = Gemini = GEMINI)
    - Varianti con versioni/numeri (gemini 3, gpt-4, gpt4, gpt 4.0)
    - Descrizioni aggiuntive (gemini con ragionamento, chatgpt plus)
    - Nomi commerciali vs tecnici (ChatGPT = GPT)
    
    Returns:
        str: Nome normalizzato dell'LLM
    """
    if pd.isna(llm_text) or not isinstance(llm_text, str):
        return "Unknown"
    
    # Converti in minuscolo e rimuovi spazi extra
    llm_lower = str(llm_text).lower().strip()
    
    # Rimuovi caratteri speciali comuni
    llm_lower = re.sub(r'[_\-\.]', ' ', llm_lower)
    llm_lower = re.sub(r'\s+', ' ', llm_lower)
    
    # Dizionario di pattern per riconoscere LLM comuni
    llm_patterns = {
        'ChatGPT': [
            r'\bchat\s*gpt\b',
            r'\bgpt\s*[34]',
            r'\bgpt\s*4o\b',
            r'\bopenai\b',
            r'\bchatbot\s*gpt\b'
        ],
        'Gemini': [
            r'\bgemini\b',
            r'\bgemin\b',  # typo comune
            r'\bgoogle\s*gemini\b',
            r'\bbard\b',  # nome precedente di Gemini
            r'\bgemini\s*pro\b',
            r'\bgemini\s*[0-9]',
            r'\bgemini\s*ultra\b',
            r'\bgemini\s*advanced\b'
        ],
        'Claude': [
            r'\bclaude\b',
            r'\banthropic\b',
            r'\bclaude\s*[0-9]',
            r'\bclaude\s*opus\b',
            r'\bclaude\s*sonnet\b'
        ],
        'LLaMA': [
            r'\bllama\b',
            r'\bll?ama\s*[0-9]',
            r'\bmeta\s*llama\b',
            r'\ballama\b'
        ],
        'Copilot': [
            r'\bcopilot\b',
            r'\bgithub\s*copilot\b',
            r'\bbing\s*chat\b',
            r'\bbing\s*ai\b'
        ],
        'Mistral': [
            r'\bmistral\b',
            r'\bmistral\s*[0-9]',
            r'\bmixtral\b'
        ],
        'GPT-3.5': [
            r'\bgpt\s*3\.5\b',
            r'\bgpt\s*35\b',
            r'\bgpt\s*3\s*5\b'
        ],
        'GPT-4': [
            r'\bgpt\s*4\b',
            r'\bgpt4\b',
            r'\bgpt\s*4\.0\b'
        ]
    }
    
    # Verifica i pattern
    for standard_name, patterns in llm_patterns.items():
        for pattern in patterns:
            if re.search(pattern, llm_lower):
                return standard_name
    
    # Riconosci domande/placeholder comuni che indicano "non specificato"
    placeholder_patterns = [
        r'\bwhich\b',
        r'\bhave\s+you\s+used\b',
        r'\?\s*$',  # termina con punto interrogativo
        r'\bselect\b',
        r'\bchoose\b',
        r'\benter\b',
        r'\binsert\b',
        r'\bspecify\b'
    ]
    
    for placeholder in placeholder_patterns:
        if re.search(placeholder, llm_lower):
            return "Non Specificato"
    
    # Se non matcha nessun pattern conosciuto, capitalizza la prima parola significativa
    # (per LLM come "Lumo", "DeepSeek", etc.)
    words = llm_lower.split()
    if words:
        first_word = words[0]
        # Rimuovi numeri e caratteri speciali dalla prima parola
        clean_word = re.sub(r'[^a-z]', '', first_word)
        if clean_word:
            return clean_word.capitalize()
    
    # Solo se completamente vuoto o non riconoscibile
    return "Non Specificato"


def classify_prompt_technique(prompt_text):
    """
    Classificazione semplificata: assegna Zero-Shot di default.
    L'algoritmo è stato semplificato per favorire la validazione manuale.
    
    Restituisce una tupla: (tecnica_principale, [lista_tecniche])
    """
    if pd.isna(prompt_text) or not isinstance(prompt_text, str):
        return "Unknown", ["Unknown"]
    
    # Classificazione base: tutto viene classificato come Zero-Shot
    # con confidence bassa per andare in validazione manuale
    return ("Zero-Shot", ["Zero-Shot"])


def classify_with_confidence(prompt_text):
    """
    Classificazione semplificata con confidenza bassa per favorire validazione manuale.
    Ritorna: (classificazione_principale, confidenza, is_doubtful, note, lista_tecniche_rilevate)
    """
    if pd.isna(prompt_text) or not isinstance(prompt_text, str):
        return "Unknown", 0, True, "Testo vuoto o non valido", ["Unknown"]
    
    # Classificazione semplificata: tutto Zero-Shot con confidence bassa (40%)
    # Questo forza tutti i prompt in validazione manuale
    main_technique = "Zero-Shot"
    confidence = 40  # Confidence bassa per andare in validazione manuale
    is_doubtful = True  # Tutti i prompt richiedono validazione
    note = "Validazione manuale richiesta"
    all_detected = ["Zero-Shot"]
    
    return main_technique, confidence, is_doubtful, note, all_detected


def extract_prompts_from_excel(df):
    """
    Estrae e consolida i prompt dalle tre sezioni dell'Excel.
    Supporta due formati:
    1. Colonne con nomi descrittivi (es. "TennisScoreManager - Report here...")
    2. Export Google Forms (colonna app + colonne successive unnamed)
    """
    applications = ['TennisScoreManager', 'SubjectParser', 'HSLColor']
    
    all_prompts = []
    extraction_log = []  # Per debug
    
    for app in applications:
        prompt_col = None
        llm_col = None
        classification_col = None
        
        # METODO 1: Cerca colonne con nomi descrittivi completi
        app_columns = [col for col in df.columns if app.lower() in str(col).lower()]
        
        if app_columns:
            # Cerca la colonna del prompt
            for col in app_columns:
                col_lower = str(col).lower()
                if 'report here' in col_lower:
                    prompt_col = col
                    break
                elif 'prompt' in col_lower and 'type' not in col_lower:
                    prompt_col = col
            
            # Cerca la colonna LLM
            for col in app_columns:
                if 'llm' in str(col).lower():
                    llm_col = col
                    break
            
            # Cerca la colonna di classificazione
            for col in app_columns:
                col_lower = str(col).lower()
                if 'which type' in col_lower or ('type' in col_lower and 'prompt' in col_lower):
                    classification_col = col
                    break
        
        # METODO 2: Se non trova con METODO 1, prova formato Google Forms
        # Cerca colonna con nome esatto dell'app
        if not (prompt_col and llm_col and classification_col):
            for i, col in enumerate(df.columns):
                if str(col).strip() == app:
                    # Trovata la colonna dell'app, le 2 successive dovrebbero essere LLM e Type
                    prompt_col = col
                    
                    # La colonna successiva (unnamed) contiene l'LLM
                    if i + 1 < len(df.columns):
                        llm_col = df.columns[i + 1]
                    
                    # La colonna dopo ancora contiene il tipo
                    if i + 2 < len(df.columns):
                        classification_col = df.columns[i + 2]
                    
                    break
        
        # Log per debug
        extraction_log.append(f"{app}: prompt_col={prompt_col}, llm_col={llm_col}, class_col={classification_col}")
        
        # Estrai i dati se le colonne sono state trovate
        if prompt_col and llm_col and classification_col:
            count = 0
            for idx, row in df.iterrows():
                prompt_text = row[prompt_col]
                llm_used = row[llm_col]
                student_class = row[classification_col]
                
                # Salta valori nulli o vuoti
                if pd.notna(prompt_text) and str(prompt_text).strip():
                    llm_original = str(llm_used) if pd.notna(llm_used) else 'Unknown'
                    all_prompts.append({
                        'Application': app,
                        'Prompt_Text': str(prompt_text).strip(),
                        'LLM_Used': normalize_llm_name(llm_used),
                        'LLM_Original': llm_original,
                        'Student_Classification': str(student_class) if pd.notna(student_class) else 'Unknown',
                        'Row_Index': idx
                    })
                    count += 1
            extraction_log.append(f"  -> {count} prompt validi estratti")
        else:
            extraction_log.append(f"  -> NESSUNA COLONNA TROVATA!")
    
    result_df = pd.DataFrame(all_prompts)
    # Stampa log in console per debug
    print("\n=== EXTRACTION LOG ===")
    for log in extraction_log:
        print(log)
    print(f"TOTALE PROMPT ESTRATTI: {len(result_df)}")
    print("======================\n")
    
    return result_df


def analyze_and_rectify(prompts_df):
    """
    Analizza i prompt e rettifica le classificazioni.
    Aggiunge informazioni su confidenza e casi dubbi.
    Implementa matching intelligente: exact/partial/error.
    """
    if prompts_df.empty:
        return prompts_df
    
    # Applica la classificazione automatica con confidenza
    classification_results = prompts_df['Prompt_Text'].apply(classify_with_confidence)
    
    prompts_df['Corrected_Classification'] = classification_results.apply(lambda x: x[0])
    prompts_df['Confidence'] = classification_results.apply(lambda x: x[1])
    prompts_df['Is_Doubtful'] = classification_results.apply(lambda x: x[2])
    prompts_df['Notes'] = classification_results.apply(lambda x: x[3])
    prompts_df['All_Detected_Techniques'] = classification_results.apply(lambda x: ', '.join(x[4]))
    
    # Aggiungi descrizione della tecnica
    prompts_df['Technique_Description'] = prompts_df['Corrected_Classification'].apply(
        lambda x: TECHNIQUE_DESCRIPTIONS.get(x, "Descrizione non disponibile")
    )
    
    # Implementa matching intelligente: exact/partial/error
    def determine_match_type(row):
        student_class = str(row['Student_Classification']).lower().strip()
        algorithm_class = str(row['Corrected_Classification']).lower().strip()
        all_detected = [t.lower().strip() for t in str(row['All_Detected_Techniques']).split(', ')]
        
        # Match esatto: studente ha scritto esattamente la tecnica principale
        if student_class == algorithm_class:
            return 'exact', False
        
        # Match parziale: studente ha menzionato una delle tecniche rilevate
        # Controllo bidirezionale: student IN detected OR detected IN student
        for detected_tech in all_detected:
            if student_class in detected_tech or detected_tech in student_class:
                return 'partial', False
        
        # Controllo anche con le tecniche combinate (es. "Few-Shot" in "Persona + Few-Shot")
        if any(student_class in tech for tech in [algorithm_class] + all_detected):
            return 'partial', False
        
        # Nessun match: errore
        return 'error', True
    
    match_results = prompts_df.apply(determine_match_type, axis=1)
    prompts_df['Match_Type'] = match_results.apply(lambda x: x[0])
    prompts_df['Needs_Correction'] = match_results.apply(lambda x: x[1])
    
    return prompts_df


def extract_prompts_from_excel(df):
    """
    Estrae e consolida i prompt dalle tre sezioni dell'Excel.
    Supporta due formati:
    1. Colonne con nomi descrittivi (es. "TennisScoreManager - Report here...")
    2. Export Google Forms (colonna app + colonne successive unnamed)
    """
    applications = ['TennisScoreManager', 'SubjectParser', 'HSLColor']
    
    all_prompts = []
    extraction_log = []  # Per debug
    
    for app in applications:
        prompt_col = None
        llm_col = None
        classification_col = None
        
        # METODO 1: Cerca colonne con nomi descrittivi completi
        app_columns = [col for col in df.columns if app.lower() in str(col).lower()]
        
        if app_columns:
            # Cerca la colonna del prompt
            for col in app_columns:
                col_lower = str(col).lower()
                if 'report here' in col_lower:
                    prompt_col = col
                    break
                elif 'prompt' in col_lower and 'type' not in col_lower:
                    prompt_col = col
            
            # Cerca la colonna LLM
            for col in app_columns:
                if 'llm' in str(col).lower():
                    llm_col = col
                    break
            
            # Cerca la colonna di classificazione
            for col in app_columns:
                col_lower = str(col).lower()
                if 'which type' in col_lower or ('type' in col_lower and 'prompt' in col_lower):
                    classification_col = col
                    break
        
        # METODO 2: Se non trova con METODO 1, prova formato Google Forms
        # Cerca colonna con nome esatto dell'app
        if not (prompt_col and llm_col and classification_col):
            for i, col in enumerate(df.columns):
                if str(col).strip() == app:
                    # Trovata la colonna dell'app, le 2 successive dovrebbero essere LLM e Type
                    prompt_col = col
                    
                    # La colonna successiva (unnamed) contiene l'LLM
                    if i + 1 < len(df.columns):
                        llm_col = df.columns[i + 1]
                    
                    # La colonna dopo ancora contiene il tipo
                    if i + 2 < len(df.columns):
                        classification_col = df.columns[i + 2]
                    
                    break
        
        # Log per debug
        extraction_log.append(f"{app}: prompt_col={prompt_col}, llm_col={llm_col}, class_col={classification_col}")
        
        # Estrai i dati se le colonne sono state trovate
        if prompt_col and llm_col and classification_col:
            count = 0
            for idx, row in df.iterrows():
                prompt_text = row[prompt_col]
                llm_used = row[llm_col]
                student_class = row[classification_col]
                
                # Salta valori nulli o vuoti
                if pd.notna(prompt_text) and str(prompt_text).strip():
                    llm_original = str(llm_used) if pd.notna(llm_used) else 'Unknown'
                    all_prompts.append({
                        'Application': app,
                        'Prompt_Text': str(prompt_text).strip(),
                        'LLM_Used': normalize_llm_name(llm_used),
                        'LLM_Original': llm_original,
                        'Student_Classification': str(student_class) if pd.notna(student_class) else 'Unknown',
                        'Row_Index': idx
                    })
                    count += 1
            extraction_log.append(f"  -> {count} prompt validi estratti")
        else:
            extraction_log.append(f"  -> NESSUNA COLONNA TROVATA!")
    
    result_df = pd.DataFrame(all_prompts)
    # Stampa log in console per debug
    print("\n=== EXTRACTION LOG ===")
    for log in extraction_log:
        print(log)
    print(f"TOTALE PROMPT ESTRATTI: {len(result_df)}")
    print("======================\n")
    
    return result_df


def analyze_and_rectify(prompts_df):
    """
    Analizza i prompt e rettifica le classificazioni.
    Aggiunge informazioni su confidenza e casi dubbi.
    Implementa matching intelligente: exact/partial/error.
    """
    if prompts_df.empty:
        return prompts_df
    
    # Applica la classificazione automatica con confidenza
    classification_results = prompts_df['Prompt_Text'].apply(classify_with_confidence)
    
    prompts_df['Corrected_Classification'] = classification_results.apply(lambda x: x[0])
    prompts_df['Confidence'] = classification_results.apply(lambda x: x[1])
    prompts_df['Is_Doubtful'] = classification_results.apply(lambda x: x[2])
    prompts_df['Notes'] = classification_results.apply(lambda x: x[3])
    prompts_df['All_Detected_Techniques'] = classification_results.apply(lambda x: ', '.join(x[4]))
    
    # Aggiungi descrizione della tecnica
    prompts_df['Technique_Description'] = prompts_df['Corrected_Classification'].apply(
        lambda x: TECHNIQUE_DESCRIPTIONS.get(x, "Descrizione non disponibile")
    )
    
    # Implementa matching intelligente: exact/partial/error
    def determine_match_type(row):
        student_class = str(row['Student_Classification']).lower().strip()
        algorithm_class = str(row['Corrected_Classification']).lower().strip()
        all_detected = [t.lower().strip() for t in str(row['All_Detected_Techniques']).split(', ')]
        
        # Match esatto: studente ha scritto esattamente la tecnica principale
        if student_class == algorithm_class:
            return 'exact', False
        
        # Match parziale: studente ha menzionato una delle tecniche rilevate
        # Controllo bidirezionale: student IN detected OR detected IN student
        for detected_tech in all_detected:
            if student_class in detected_tech or detected_tech in student_class:
                return 'partial', False
        
        # Controllo anche con le tecniche combinate (es. "Few-Shot" in "Persona + Few-Shot")
        if any(student_class in tech for tech in [algorithm_class] + all_detected):
            return 'partial', False
        
        # Nessun match: errore
        return 'error', True
    
    match_results = prompts_df.apply(determine_match_type, axis=1)
    prompts_df['Match_Type'] = match_results.apply(lambda x: x[0])
    prompts_df['Needs_Correction'] = match_results.apply(lambda x: x[1])
    
    return prompts_df


def create_visualizations(analyzed_df, manual_validations=None):
    """
    Crea le visualizzazioni con Plotly.
    
    Args:
        analyzed_df: DataFrame con i prompt analizzati
        manual_validations: Dict con validazioni manuali {idx: {'is_correct': bool, 'partially_correct': bool, ...}}
    """
    visualizations = {}
    
    if analyzed_df.empty:
        return visualizations
    
    # Determina quale colonna usare per le classificazioni
    # Se esiste 'Final_Classification', usala (Fase 3 con validazioni)
    # Altrimenti usa 'Corrected_Classification' (Fase 1)
    classification_col = 'Final_Classification' if 'Final_Classification' in analyzed_df.columns else 'Corrected_Classification'
    
    # 1. Varietà delle tecniche (Frequency Bar Chart)
    technique_counts = analyzed_df[classification_col].value_counts().reset_index()
    technique_counts.columns = ['Technique', 'Count']
    
    title_suffix = "Finale" if classification_col == 'Final_Classification' else "Corretta"
    
    fig1 = px.bar(
        technique_counts,
        x='Technique',
        y='Count',
        title=f'📊 Varietà delle Tecniche di Prompting (Classificazione {title_suffix})',
        labels={'Technique': 'Tecnica', 'Count': 'Frequenza'},
        color='Count',
        color_continuous_scale='Viridis',
        text='Count'
    )
    fig1.update_traces(textposition='outside')
    fig1.update_layout(height=500, showlegend=False)
    visualizations['techniques'] = fig1
    
    # 2. Distribuzione LLM (Pie Chart)
    llm_counts = analyzed_df['LLM_Used'].value_counts().reset_index()
    llm_counts.columns = ['LLM', 'Count']
    
    # Crea il grafico a torta con configurazione esplicita
    fig2 = go.Figure(data=[go.Pie(
        labels=llm_counts['LLM'].tolist(),
        values=llm_counts['Count'].tolist(),
        hole=0.3,
        textposition='inside',
        textinfo='percent+label'
    )])
    
    fig2.update_layout(
        title='🤖 Distribuzione dei Modelli LLM Utilizzati',
        height=500,
        showlegend=True
    )
    
    visualizations['llms'] = fig2
    
    # 3. Tasso di Errore (Confronto Student vs Corrected)
    comparison_data = []
    
    for technique in analyzed_df[classification_col].unique():
        student_count = len(analyzed_df[
            analyzed_df['Student_Classification'].str.contains(technique, case=False, na=False)
        ])
        corrected_count = len(analyzed_df[
            analyzed_df[classification_col] == technique
        ])
        
        comparison_data.append({
            'Technique': technique,
            'Student Classification': student_count,
            f'{title_suffix} Classification': corrected_count
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        name='Classificazione Studente',
        x=comparison_df['Technique'],
        y=comparison_df['Student Classification'],
        marker_color='lightblue'
    ))
    fig3.add_trace(go.Bar(
        name=f'Classificazione {title_suffix}',
        x=comparison_df['Technique'],
        y=comparison_df[f'{title_suffix} Classification'],
        marker_color='darkblue'
    ))
    
    fig3.update_layout(
        title=f'📈 Confronto: Classificazione Studente vs Classificazione {title_suffix}',
        xaxis_title='Tecnica',
        yaxis_title='Numero di Prompt',
        barmode='group',
        height=500
    )
    visualizations['comparison'] = fig3
    
    # 4. Tasso di errore generale
    # Calcola la percentuale di errori commessi dagli studenti
    # (prompt dove Student_Classification ≠ Corrected_Classification)
    # NOTA: Gli errori sono già stati corretti dall'algoritmo!
    total_prompts = len(analyzed_df)
    
    # Se ci sono validazioni manuali, usa quelle per calcolare il tasso di errore reale
    if manual_validations and len(manual_validations) > 0:
        # Conta errori reali basati sulle validazioni manuali
        # Errore = quando NON è completamente corretto (is_correct=False o is_correct=None per skipped)
        real_errors = sum(1 for val in manual_validations.values() 
                         if not val.get('is_correct', False) and not val.get('skipped', False))
        
        # Errori rimanenti non ancora validati (assumiamo corretti come algoritmo originale)
        remaining_errors = analyzed_df.loc[
            ~analyzed_df.index.isin(manual_validations.keys()),
            'Needs_Correction'
        ].sum()
        
        total_errors = real_errors + remaining_errors
        error_rate = (total_errors / total_prompts * 100) if total_prompts > 0 else 0
        
        gauge_title = f"Tasso di Errore (Validato: {len(manual_validations)}/{total_prompts})"
    else:
        # Usa calcolo originale
        errors = analyzed_df['Needs_Correction'].sum()
        error_rate = (errors / total_prompts * 100) if total_prompts > 0 else 0
        gauge_title = "Tasso di Errore (%)"
    
    fig4 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=error_rate,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': gauge_title, 'font': {'size': 20}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkred"},
            'steps': [
                {'range': [0, 25], 'color': "lightgreen"},
                {'range': [25, 50], 'color': "yellow"},
                {'range': [50, 75], 'color': "orange"},
                {'range': [75, 100], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig4.update_layout(height=400)
    visualizations['error_rate'] = fig4
    
    # 5. Distribuzione Match Types (Exact/Partial/Error)
    if 'Match_Type' in analyzed_df.columns:
        match_counts = analyzed_df['Match_Type'].value_counts().reset_index()
        match_counts.columns = ['Match_Type', 'Count']
        
        # Mappa nomi più leggibili e colori
        match_type_labels = {
            'exact': '✅ Match Esatto',
            'partial': '⚠️ Match Parziale',
            'error': '❌ Errore'
        }
        match_type_colors = {
            '✅ Match Esatto': '#28a745',  # verde
            '⚠️ Match Parziale': '#ffc107',  # giallo/arancione
            '❌ Errore': '#dc3545'  # rosso
        }
        
        match_counts['Label'] = match_counts['Match_Type'].map(match_type_labels)
        match_counts['Color'] = match_counts['Label'].map(match_type_colors)
        
        fig5 = go.Figure(data=[go.Pie(
            labels=match_counts['Label'].tolist(),
            values=match_counts['Count'].tolist(),
            hole=0.4,
            marker=dict(colors=match_counts['Color'].tolist()),
            textposition='inside',
            textinfo='percent+label+value',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig5.update_layout(
            title='🎯 Qualità delle Classificazioni Studenti',
            height=500,
            showlegend=True,
            annotations=[dict(
                text=f'{len(analyzed_df)} Totale',
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False
            )]
        )
        
        visualizations['match_types'] = fig5
    
    return visualizations


def export_to_excel(analyzed_df, original_df=None, validation_data=None):
    """
    Esporta il DataFrame analizzato in un file Excel completo.
    Include: risultati analisi, statistiche, campione validazione, file integrato
    
    Args:
        analyzed_df: DataFrame con tutti i prompt analizzati
        original_df: DataFrame originale (opzionale)
        validation_data: DataFrame con validazioni manuali se già fatte (opzionale)
    """
    output = BytesIO()
    
    # Crea un writer Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Analisi completa con colonne per validazione manuale
        export_df = analyzed_df.copy()
        export_df['Manual_Validation'] = ''  # Colonna vuota per validazione
        export_df['Manual_Notes'] = ''  # Colonna per note
        export_df.to_excel(writer, sheet_name='All_Prompts_Analysis', index=False)
        
        # Sheet 2: Campione per validazione manuale (40 prompt strategici)
        # Usa validation_data se disponibile, altrimenti genera nuovo campione
        if validation_data is not None and len(validation_data) > 0:
            # Usa i dati della validazione interattiva
            validation_sample = validation_data.copy()
        else:
            # Genera nuovo campione
            # Selezione strategica:
            # - 10 casi dubbi (Is_Doubtful=True)
            # - 15 con correzioni (Needs_Correction=True) 
            # - 15 senza correzioni (Needs_Correction=False)
            
            doubtful = analyzed_df[analyzed_df['Is_Doubtful'] == True].sample(
                n=min(10, len(analyzed_df[analyzed_df['Is_Doubtful'] == True])),
                random_state=42
            )
            
            with_corrections = analyzed_df[
                (analyzed_df['Needs_Correction'] == True) & 
                (analyzed_df['Is_Doubtful'] == False)
            ].sample(
                n=min(15, len(analyzed_df[(analyzed_df['Needs_Correction'] == True) & (analyzed_df['Is_Doubtful'] == False)])),
                random_state=42
            )
            
            without_corrections = analyzed_df[
                (analyzed_df['Needs_Correction'] == False) & 
                (analyzed_df['Is_Doubtful'] == False)
            ].sample(
                n=min(15, len(analyzed_df[(analyzed_df['Needs_Correction'] == False) & (analyzed_df['Is_Doubtful'] == False)])),
                random_state=42
            )
            
            validation_sample = pd.concat([doubtful, with_corrections, without_corrections])
            validation_sample['Manual_Validation'] = ''
            validation_sample['Agreement'] = ''  # Studente/Algoritmo/Altro
            validation_sample['Manual_Notes'] = ''
        
        # Riordina colonne per leggibilità
        sample_cols = [
            'Application', 'Prompt_Text', 'LLM_Used',
            'Student_Classification', 'Corrected_Classification',
            'Confidence', 'Is_Doubtful', 'Needs_Correction',
            'Manual_Validation', 'Agreement', 'Manual_Notes'
        ]
        validation_sample[sample_cols].to_excel(
            writer, 
            sheet_name='Validation_Sample_40', 
            index=False
        )
        
        # Sheet 3: Solo casi dubbi (per revisione prioritaria)
        doubtful_cases = analyzed_df[analyzed_df['Is_Doubtful'] == True].copy()
        doubtful_cases['Manual_Validation'] = ''
        doubtful_cases['Manual_Notes'] = ''
        doubtful_cases.to_excel(writer, sheet_name='Doubtful_Cases', index=False)
        
        # Sheet 4: Statistiche riassuntive (estese con Match Types)
        stats_rows = [
            ('Total Prompts Analyzed', len(analyzed_df)),
            ('Prompts Requiring Correction (Errors Only)', analyzed_df['Needs_Correction'].sum()),
            ('Error Rate (%)', f"{(analyzed_df['Needs_Correction'].sum() / len(analyzed_df) * 100):.2f}" if len(analyzed_df) > 0 else "0"),
            ('Doubtful Cases', analyzed_df['Is_Doubtful'].sum()),
            ('Doubtful Rate (%)', f"{(analyzed_df['Is_Doubtful'].sum() / len(analyzed_df) * 100):.2f}" if len(analyzed_df) > 0 else "0"),
            ('Average Confidence', f"{analyzed_df['Confidence'].mean():.1f}"),
            ('Unique Techniques Identified', analyzed_df['Corrected_Classification'].nunique()),
            ('Unique LLMs Used', analyzed_df['LLM_Used'].nunique()),
            ('Most Common Technique', analyzed_df['Corrected_Classification'].value_counts().index[0] if len(analyzed_df) > 0 else "N/A"),
            ('Validation Sample Size', len(validation_sample))
        ]
        
        # Aggiungi statistiche Match Types se la colonna esiste
        if 'Match_Type' in analyzed_df.columns:
            exact_count = (analyzed_df['Match_Type'] == 'exact').sum()
            partial_count = (analyzed_df['Match_Type'] == 'partial').sum()
            error_count = (analyzed_df['Match_Type'] == 'error').sum()
            
            stats_rows.extend([
                ('--- MATCH QUALITY METRICS ---', ''),
                ('Exact Matches', exact_count),
                ('Exact Match Rate (%)', f"{(exact_count / len(analyzed_df) * 100):.2f}" if len(analyzed_df) > 0 else "0"),
                ('Partial Matches', partial_count),
                ('Partial Match Rate (%)', f"{(partial_count / len(analyzed_df) * 100):.2f}" if len(analyzed_df) > 0 else "0"),
                ('True Errors', error_count),
                ('True Error Rate (%)', f"{(error_count / len(analyzed_df) * 100):.2f}" if len(analyzed_df) > 0 else "0")
            ])
        
        stats_data = {
            'Metric': [row[0] for row in stats_rows],
            'Value': [row[1] for row in stats_rows]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        # Sheet 5: Distribuzione tecniche
        technique_dist = analyzed_df['Corrected_Classification'].value_counts().reset_index()
        technique_dist.columns = ['Technique', 'Count']
        technique_dist['Percentage'] = (technique_dist['Count'] / len(analyzed_df) * 100).round(2)
        technique_dist.to_excel(writer, sheet_name='Technique_Distribution', index=False)
        
        # Sheet 6: Confronto Studente vs Algoritmo
        comparison_data = []
        for tech in analyzed_df['Corrected_Classification'].unique():
            student_count = len(analyzed_df[
                analyzed_df['Student_Classification'].str.contains(tech, case=False, na=False)
            ])
            algo_count = len(analyzed_df[
                analyzed_df['Corrected_Classification'] == tech
            ])
            comparison_data.append({
                'Technique': tech,
                'Student_Count': student_count,
                'Algorithm_Count': algo_count,
                'Difference': algo_count - student_count
            })
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_excel(writer, sheet_name='Student_vs_Algorithm', index=False)
        
        # Sheet 7: Distribuzione LLM
        llm_dist = analyzed_df['LLM_Used'].value_counts().reset_index()
        llm_dist.columns = ['LLM', 'Count']
        llm_dist['Percentage'] = (llm_dist['Count'] / len(analyzed_df) * 100).round(2)
        llm_dist.to_excel(writer, sheet_name='LLM_Distribution', index=False)
    
    output.seek(0)
    return output


# ===== INTERFACCIA STREAMLIT =====

# Sidebar per upload
st.sidebar.header("📂 Upload Dati")
uploaded_file = st.sidebar.file_uploader(
    "Carica il file Prompt.xlsx",
    type=['xlsx', 'xls'],
    help="Carica il file Excel contenente i dati dell'esercitazione"
)

st.sidebar.markdown("---")

# Gestione Backup Validazioni
st.sidebar.header("💾 Gestione Backup")

if st.session_state.manual_validations:
    st.sidebar.success(f"✅ {len(st.session_state.manual_validations)} validazioni in memoria")
    if st.sidebar.button("💾 Salva Backup Manualmente", use_container_width=True):
        success, info = save_validations_to_file(
            st.session_state.manual_validations,
            'validations_backup.json'
        )
        if success:
            st.sidebar.success(f"✅ Backup salvato: {info}")
        else:
            st.sidebar.error(f"❌ Errore: {info}")
else:
    st.sidebar.info("Nessuna validazione in memoria")

# Upload backup manuale
backup_file = st.sidebar.file_uploader(
    "📥 Carica Backup Validazioni",
    type=['json'],
    help="Carica un file di backup precedentemente salvato per riprendere le validazioni"
)

if backup_file is not None:
    try:
        backup_data = json.load(backup_file)
        loaded_validations = {int(k): v for k, v in backup_data['validations'].items()}
        st.session_state.manual_validations = loaded_validations
        st.sidebar.success(f"✅ Caricati {len(loaded_validations)} validazioni dal backup ({backup_data.get('timestamp', 'N/A')})")
        st.sidebar.info("🔄 Premi 'R' per aggiornare l'app")
    except Exception as e:
        st.sidebar.error(f"❌ Errore nel caricamento: {str(e)}")

st.sidebar.markdown("---")

# Expander con tutte le tecniche e descrizioni
with st.sidebar.expander("📖 Guida alle Tecniche di Prompting (clicca per aprire)", expanded=False):
    st.markdown("### 1️⃣ Tecniche Fondamentali")
    st.markdown("**Zero-Shot**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Zero-Shot"])
    st.markdown("**Few-Shot**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Few-Shot"])
    
    st.markdown("---")
    st.markdown("### 2️⃣ Ragionamento e Logica")
    st.markdown("**Chain-of-Thought (CoT)**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Chain-of-Thought"])
    st.markdown("**Auto-CoT**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Auto-CoT"])
    st.markdown("**LogiCoT**")
    st.caption(TECHNIQUE_DESCRIPTIONS["LogiCoT"])
    st.markdown("**LCoT**")
    st.caption(TECHNIQUE_DESCRIPTIONS["LCoT"])
    st.markdown("**Tree-of-Thoughts (ToT)**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Tree-of-Thoughts"])
    st.markdown("**Graph-of-Thought (GoT)**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Graph-of-Thought"])
    st.markdown("**Self-Consistency**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Self-Consistency"])
    st.markdown("**System-2-Attention (S2A)**")
    st.caption(TECHNIQUE_DESCRIPTIONS["System-2-Attention"])
    
    st.markdown("---")
    st.markdown("### 3️⃣ Generazione di Codice")
    st.markdown("**Structured CoT (SCoT)**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Structured CoT"])
    st.markdown("**Program-of-Thoughts (PoT)**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Program-of-Thoughts"])
    st.markdown("**Chain-of-Code (CoC)**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Chain-of-Code"])
    st.markdown("**Scratchpad**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Scratchpad"])
    
    st.markdown("---")
    st.markdown("### 4️⃣ Metacognizione e Autocorrezione")
    st.markdown("**Self-Refine**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Self-Refine"])
    st.markdown("**Take-a-Step-Back**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Take-a-Step-Back"])
    st.markdown("**Fix-Prompt / Hierarchical Repair**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Fix-Prompt"])
    
    st.markdown("---")
    st.markdown("### 5️⃣ Altre Tecniche")
    st.markdown("**Persona/Role Prompting**")
    st.caption(TECHNIQUE_DESCRIPTIONS["Persona/Role Prompting"])
    
    st.markdown("---")
    st.info("💡 **Nota**: Le tecniche possono essere combinate (es. Persona + Few-Shot per +4 punti)")

# Barra di Navigazione Fasi (sempre visibile se file caricato)
if uploaded_file is not None:
    current_phase = st.session_state.current_phase
    
    # Progress bar HTML
    phase1_class = "phase-active" if current_phase == 1 else ("phase-completed" if current_phase > 1 else "phase-pending")
    phase2_class = "phase-active" if current_phase == 2 else ("phase-completed" if current_phase > 2 else "phase-pending")
    phase3_class = "phase-active" if current_phase == 3 else "phase-pending"
    
    st.markdown(f"""
    <div class="phase-container">
        <div class="phase-step {phase1_class}">
            <div style="font-size: 24px;">📂</div>
            <div>FASE 1</div>
            <div style="font-size: 12px; opacity: 0.9;">Caricamento & Analisi Automatica</div>
        </div>
        <div class="phase-step {phase2_class}">
            <div style="font-size: 24px;">✏️</div>
            <div>FASE 2</div>
            <div style="font-size: 12px; opacity: 0.9;">Validazione Manuale Casi Dubbi</div>
        </div>
        <div class="phase-step {phase3_class}">
            <div style="font-size: 24px;">📊</div>
            <div>FASE 3</div>
            <div style="font-size: 12px; opacity: 0.9;">Statistiche & Risultati Finali</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

# Main content
if uploaded_file is not None:
    try:
        # ===== CARICAMENTO DATI (sempre, indipendentemente dalla fase) =====
        if st.session_state.analyzed_data is None:
            with st.spinner("📥 Caricamento dati in corso..."):
                df_original = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File caricato con successo! ({len(df_original)} righe)")
            
            # Mostra anteprima dati originali
            with st.expander("👁️ Visualizza Dati Originali", expanded=False):
                st.dataframe(df_original.head(10))
            
            # Estrai e consolida i prompt
            with st.spinner("🔍 Estrazione e consolidamento prompt..."):
                prompts_df = extract_prompts_from_excel(df_original)
            
            if prompts_df.empty:
                st.error("""
                ⚠️ Nessun prompt trovato nel file. Verifica che il file contenga le colonne corrette:
                - Colonne con 'Prompt' o 'Report here the text'
                - Colonne con 'LLM'
                - Colonne con 'type' o 'Which type'
                """)
                st.stop()
            
            # Mostra normalizzazione LLM
            with st.expander("🤖 Normalizzazione LLM Applicata", expanded=False):
                st.markdown("""
                **I nomi degli LLM sono stati normalizzati automaticamente** per raggruppare varianti simili:
                - **Case insensitive**: `gemini` = `Gemini` = `GEMINI`
                - **Versioni/numeri**: `gemini 3`, `gemini pro`, `gemini con ragionamento` → `Gemini`
                - **Varianti GPT**: `gpt-4`, `gpt4`, `chatgpt`, `chat gpt` → `ChatGPT`
                """)
                
                llm_counts = prompts_df['LLM_Used'].value_counts()
                st.write(f"**{len(llm_counts)} LLM unici trovati dopo normalizzazione:**")
                for llm, count in llm_counts.items():
                    st.write(f"  • **{llm}**: {count} prompt ({count/len(prompts_df)*100:.1f}%)")
            
            # Analizza e rettifica
            with st.spinner("🧠 Analisi automatica delle tecniche di prompting in corso..."):
                analyzed_df = analyze_and_rectify(prompts_df)
            
            # Salva in session state
            st.session_state.analyzed_data = analyzed_df
            st.success(f"✅ Analisi automatica completata! {len(analyzed_df)} prompt analizzati")
        else:
            # Dati già caricati
            analyzed_df = st.session_state.analyzed_data
        
        # ===== DIALOG SCELTA BACKUP (dopo analisi) =====
        if 'backup_recovered' in st.session_state and st.session_state.backup_recovered and not st.session_state.backup_choice_made:
            st.markdown("---")
            st.warning(f"🔄 **Backup Trovato!** Ho recuperato {st.session_state.backup_count} validazioni salvate il {st.session_state.get('backup_timestamp', 'N/A')}")
            
            with st.container():
                st.markdown("### ⚙️ Come vuoi procedere?")
                st.markdown("""
                Ho trovato un backup con validazioni precedenti. Scegli come vuoi continuare:
                
                - **📝 Riprendi Validazioni**: Continua da dove avevi lasciato, validando solo le istanze che NON hai ancora validato
                - **🔄 Ricomincia da Capo**: Cancella il backup e ricomincia la validazione di tutte le istanze
                """)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📝 Riprendi Validazioni (solo non validate)", use_container_width=True, type="primary", key="btn_resume"):
                        st.session_state.filter_validated = True
                        st.session_state.backup_choice_made = True
                        st.session_state.backup_recovered = False
                        st.success(f"✅ OK! In Fase 2 vedrai solo le istanze non ancora validate.")
                        st.rerun()
                
                with col2:
                    if st.button("🔄 Ricomincia da Capo (tutte le istanze)", use_container_width=True, key="btn_restart"):
                        st.session_state.manual_validations = {}
                        st.session_state.filter_validated = False
                        st.session_state.backup_choice_made = True
                        st.session_state.backup_recovered = False
                        # Elimina il file backup
                        if os.path.exists('validations_backup.json'):
                            os.remove('validations_backup.json')
                        st.success("✅ Backup cancellato! Ricomincerai la validazione da capo.")
                        st.rerun()
            
            st.markdown("---")
            st.info("👆 **Scegli un'opzione sopra per continuare**")
            # Stop qui - non mostrare il resto finché l'utente non sceglie
            st.stop()
        
        # ===== FASE 1: CARICAMENTO & ANALISI AUTOMATICA =====
        if st.session_state.current_phase == 1:
                st.header("📂 FASE 1: Caricamento & Analisi Automatica")
                st.markdown("L'algoritmo ha analizzato **automaticamente** tutti i prompt e rilevato le tecniche utilizzate.")
                
                # Metriche principali - Fase 1
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Total Prompts", len(analyzed_df))
                
                with col2:
                    corrections_needed = analyzed_df['Needs_Correction'].sum()
                    st.metric(
                        "Errori Rilevati",
                        corrections_needed,
                        delta=f"{(corrections_needed/len(analyzed_df)*100):.1f}%",
                        help="Prompt classificati erroneamente dagli studenti (solo errori veri, NON match parziali)"
                    )
                
                with col3:
                    doubtful_cases = analyzed_df['Is_Doubtful'].sum()
                    st.metric(
                        "⚠️ Casi Dubbi",
                        doubtful_cases,
                        delta=f"{(doubtful_cases/len(analyzed_df)*100):.1f}%",
                        help="Prompt con bassa confidenza che richiedono validazione manuale"
                    )
                
                with col4:
                    avg_confidence = analyzed_df['Confidence'].mean()
                    st.metric(
                        "Confidenza Media",
                        f"{avg_confidence:.1f}%",
                        help="Confidenza media delle classificazioni automatiche"
                    )
                
                with col5:
                    st.metric(
                        "Tecniche Rilevate",
                        analyzed_df['Corrected_Classification'].nunique()
                    )
                
                # === STATISTICHE AGGIUNTIVE: LLM E TECNICHE ===
                st.markdown("#### 📊 Statistiche Distribuzioni")
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                
                with col_stat1:
                    # LLM più usato
                    most_common_llm = analyzed_df['LLM_Used'].mode()[0] if len(analyzed_df) > 0 else 'N/A'
                    llm_count = (analyzed_df['LLM_Used'] == most_common_llm).sum()
                    llm_pct = (llm_count / len(analyzed_df) * 100) if len(analyzed_df) > 0 else 0
                    st.metric(
                        "🤖 LLM Più Usato",
                        most_common_llm,
                        delta=f"{llm_count} prompt ({llm_pct:.1f}%)",
                        help="Modello LLM utilizzato più frequentemente dagli studenti"
                    )
                
                with col_stat2:
                    # Tecnica più usata (rilevata dall'algoritmo)
                    most_common_technique = analyzed_df['Corrected_Classification'].mode()[0] if len(analyzed_df) > 0 else 'N/A'
                    tech_count = (analyzed_df['Corrected_Classification'] == most_common_technique).sum()
                    tech_pct = (tech_count / len(analyzed_df) * 100) if len(analyzed_df) > 0 else 0
                    st.metric(
                        "🎯 Tecnica Più Rilevata",
                        most_common_technique,
                        delta=f"{tech_count} prompt ({tech_pct:.1f}%)",
                        help="Tecnica di prompting rilevata più frequentemente dall'algoritmo"
                    )
                
                with col_stat3:
                    # Applicazione più rappresentata
                    if 'Application' in analyzed_df.columns:
                        most_common_app = analyzed_df['Application'].mode()[0] if len(analyzed_df) > 0 else 'N/A'
                        app_count = (analyzed_df['Application'] == most_common_app).sum()
                        app_pct = (app_count / len(analyzed_df) * 100) if len(analyzed_df) > 0 else 0
                        st.metric(
                            "📱 Applicazione Principale",
                            most_common_app,
                            delta=f"{app_count} prompt ({app_pct:.1f}%)",
                            help="Applicazione con più prompt nel dataset"
                        )
                
                # Match Types summary
                if 'Match_Type' in analyzed_df.columns:
                    st.markdown("#### 🎯 Riepilogo Correzioni Automatiche")
                    col1, col2, col3 = st.columns(3)
                    
                    exact_matches = (analyzed_df['Match_Type'] == 'exact').sum()
                    partial_matches = (analyzed_df['Match_Type'] == 'partial').sum()
                    errors = (analyzed_df['Match_Type'] == 'error').sum()
                    
                    with col1:
                        st.metric(
                            "✅ Match Esatti",
                            exact_matches,
                            delta=f"{(exact_matches/len(analyzed_df)*100):.1f}%"
                        )
                    
                    with col2:
                        st.metric(
                            "⚠️ Incompleti",
                            partial_matches,
                            delta=f"{(partial_matches/len(analyzed_df)*100):.1f}%"
                        )
                    
                    with col3:
                        st.metric(
                            "❌ Errori",
                            errors,
                            delta=f"{(errors/len(analyzed_df)*100):.1f}%",
                            delta_color="inverse"
                        )
                
                st.markdown("---")
                
                # Tabella risultati analisi automatica
                with st.expander("📋 Visualizza Tabella Completa Analisi Automatica", expanded=False):
                    st.dataframe(analyzed_df, use_container_width=True)
                
                # Pulsante per passare a Fase 2
                st.markdown("### ➡️ Prossimo Passo")
                if doubtful_cases > 0:
                    st.warning(f"""
                    ⚠️ **{doubtful_cases} casi dubbi** rilevati che richiedono validazione manuale nella Fase 2.
                    
                    Questi sono prompt con **bassa confidenza** (<70%) dove l'algoritmo non è sicuro della classificazione dello studente.
                    """)
                    
                    # Esporta SOLO i casi dubbi in Excel
                    st.markdown("#### 📥 Export Casi Dubbi")
                    st.info("💡 Scarica un Excel con **solo i casi dubbi** da validare (ideale per condivisione/revisione offline)")
                    
                    doubtful_df = analyzed_df[analyzed_df['Is_Doubtful'] == True].copy()
                    
                    output_doubtful = BytesIO()
                    with pd.ExcelWriter(output_doubtful, engine='openpyxl') as writer:
                        doubtful_df.to_excel(writer, sheet_name='Casi_Dubbi', index=False)
                    output_doubtful.seek(0)
                    
                    st.download_button(
                        label=f"📥 Scarica {len(doubtful_df)} Casi Dubbi (Excel)",
                        data=output_doubtful,
                        file_name=f"Casi_Dubbi_da_Validare_{len(doubtful_df)}_prompts.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="secondary"
                    )
                    
                    st.markdown("---")
                else:
                    st.success("✅ Nessun caso dubbio rilevato! Tutti i prompt hanno alta confidenza.")
                
                if st.button("▶️ Procedi a Fase 2: Validazione Manuale", type="primary", use_container_width=True):
                    st.session_state.current_phase = 2
                    st.rerun()
        
        # ===== FASE 2: VALIDAZIONE MANUALE CASI DUBBI =====
        elif st.session_state.current_phase == 2:
            analyzed_df = st.session_state.analyzed_data
            
            st.header("✏️ FASE 2: Validazione Manuale Casi Dubbi")
            st.markdown("""
            In questa fase validi **manualmente** solo i prompt dubbi (confidenza <70%).
            
            **Validazione Rapida** - Per ogni prompt:
            1. 🔘 Scegli l'opzione (Corretta, Parziale, Errata, Scarta)
            2. 📋 Se Parziale/Errata: seleziona tecniche
            3. 💾 Click su Salva
            
            *📝 Prompt e Risposta: clicca icona copia per copiare il testo*
            """)
            
            # Filtra solo i casi dubbi
            doubtful_df = analyzed_df[analyzed_df['Is_Doubtful'] == True].copy()
            
            # Se riprendi validazioni, filtra solo quelle NON ancora validate
            if st.session_state.filter_validated and st.session_state.manual_validations:
                validated_indices = set(st.session_state.manual_validations.keys())
                doubtful_df = doubtful_df[~doubtful_df.index.isin(validated_indices)]
                
                if len(st.session_state.manual_validations) > 0:
                    st.info(f"📝 **Modalità Ripresa Attiva**: Mostro solo le istanze NON ancora validate. ({len(st.session_state.manual_validations)} già validate escluse)")
            
            if len(doubtful_df) == 0:
                st.success("🎉 Nessun caso dubbio da validare! Procedi direttamente alla Fase 3.")
                if st.button("▶️ Procedi a Fase 3: Statistiche Finali", type="primary"):
                    st.session_state.current_phase = 3
                    st.rerun()
            else:
                # Metriche validazione
                validated_count = sum(1 for v in st.session_state.manual_validations.values() if not v.get('skipped', False))
                skipped_count = sum(1 for v in st.session_state.manual_validations.values() if v.get('skipped', False))
                partial_count = sum(1 for v in st.session_state.manual_validations.values() if v.get('partially_correct', False))
                total_processed = len(st.session_state.manual_validations)
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Casi Dubbi Totali", len(doubtful_df))
                
                with col2:
                    st.metric(
                        "Validati",
                        validated_count,
                        delta=f"{(validated_count/len(doubtful_df)*100):.0f}%"
                    )
                
                with col3:
                    st.metric(
                        "Parziali",
                        partial_count,
                        delta_color="normal"
                    )
                
                with col4:
                    st.metric(
                        "Scartati",
                        skipped_count,
                        delta_color="off"
                    )
                
                with col5:
                    remaining = len(doubtful_df) - total_processed
                    st.metric(
                        "Rimanenti",
                        remaining,
                        delta_color="inverse"
                    )
                
                st.info("⚡ **Validazione Ultra-Rapida**: Le modifiche vengono salvate senza ricaricamento. Al cambio pagina tutti i dati vengono aggiornati.")
                
                # === BACKUP E RIPRISTINO ===
                st.markdown("### 💾 Backup e Ripristino")
                
                col_backup1, col_backup2, col_backup3 = st.columns([2, 2, 1])
                
                with col_backup1:
                    st.success(f"🔄 **Auto-salvataggio attivo**: {len(st.session_state.manual_validations)} validazioni salvate automaticamente")
                
                with col_backup2:
                    # Pulsante per download manuale del backup
                    if st.session_state.manual_validations:
                        backup_data = {
                            'timestamp': datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
                            'total_validations': len(st.session_state.manual_validations),
                            'validations': {str(k): v for k, v in st.session_state.manual_validations.items()}
                        }
                        backup_json = json.dumps(backup_data, indent=2, ensure_ascii=False)
                        
                        st.download_button(
                            label="📥 Scarica Backup JSON",
                            data=backup_json,
                            file_name=f"validazioni_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True,
                            help="Scarica un file JSON con tutte le tue validazioni"
                        )
                
                with col_backup3:
                    # Pulsante per caricare backup
                    uploaded_backup = st.file_uploader(
                        "📤 Carica Backup",
                        type=['json'],
                        key="backup_uploader",
                        help="Carica un file di backup precedente"
                    )
                    
                    if uploaded_backup is not None:
                        try:
                            backup_data = json.load(uploaded_backup)
                            loaded_validations = {int(k): v for k, v in backup_data['validations'].items()}
                            st.session_state.manual_validations = loaded_validations
                            st.success(f"✅ Caricati {len(loaded_validations)} validazioni dal backup del {backup_data.get('timestamp', 'N/A')}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Errore nel caricamento: {str(e)}")
                
                st.markdown("---")
                
                # Paginazione
                items_per_page = 5
                total_pages = (len(doubtful_df) + items_per_page - 1) // items_per_page
                current_page = st.session_state.validation_page
                
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    if st.button("⬅️ Precedente", disabled=current_page == 0):
                        st.session_state.validation_page -= 1
                        st.rerun()
                
                with col2:
                    st.markdown(f"<h4 style='text-align: center;'>Pagina {current_page + 1} di {total_pages}</h4>", unsafe_allow_html=True)
                
                with col3:
                    if st.button("➡️ Successiva", disabled=current_page >= total_pages - 1):
                        st.session_state.validation_page += 1
                        st.rerun()
                
                st.markdown("---")
                
                # Mostra prompts della pagina corrente
                start_idx = current_page * items_per_page
                end_idx = min(start_idx + items_per_page, len(doubtful_df))
                page_data = doubtful_df.iloc[start_idx:end_idx]
                
                # Lista di tutte le tecniche per multi-select
                all_techniques = [
                    "Zero-Shot", "Few-Shot", "Chain-of-Thought", "Auto-CoT", "LogiCoT", "LCoT",
                    "Tree-of-Thoughts", "Graph-of-Thought", "Self-Consistency", "System-2-Attention",
                    "Structured CoT", "Program-of-Thoughts", "Chain-of-Code", "Scratchpad",
                    "Self-Refine", "Take-a-Step-Back", "Fix-Prompt", "Persona/Role Prompting"
                ]
                
                for position, (idx, row) in enumerate(page_data.iterrows(), 1):
                    # Verifica se già validato
                    validation = st.session_state.manual_validations.get(idx, {})
                    is_validated = idx in st.session_state.manual_validations
                    is_skipped = validation.get('skipped', False) if is_validated else False
                    is_partially_correct = validation.get('partially_correct', False) if is_validated else False
                    is_correct = validation.get('is_correct', False) if is_validated else False
                    
                    # Box colorato
                    if is_validated:
                        if is_skipped:
                            box_color = "#e9ecef"
                            border_color = "#6c757d"
                            status = "⏭️ SCARTATO - Non Validato"
                        elif is_correct:
                            box_color = "#d4edda"
                            border_color = "#28a745"
                            status = "✅ VALIDATO - Risposta Studente Corretta"
                        elif is_partially_correct:
                            box_color = "#d1ecf1"
                            border_color = "#17a2b8"
                            status = "⚠️ VALIDATO - Parzialmente Corretta (Tecniche Aggiunte)"
                        else:
                            box_color = "#f8d7da"
                            border_color = "#dc3545"
                            status = "❌ VALIDATO - Completamente Errata"
                    else:
                        box_color = "#fff3cd"
                        border_color = "#ffc107"
                        status = "⏳ DA VALIDARE"
                    
                    st.markdown(f"""
                    <div style='background-color: {box_color}; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid {border_color}'>
                        <h4 style='margin: 0 0 10px 0;'>🔍 Prompt Dubbio #{position} (ID: {idx}) - {status}</h4>
                        <p style='margin: 5px 0;'><strong>App:</strong> {row['Application']} | <strong>LLM:</strong> {row['LLM_Used']} | <strong>Confidence:</strong> {row['Confidence']:.0f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Layout informazioni prompt
                    col_left, col_right = st.columns([2, 1])
                    
                    with col_left:
                        st.markdown("**📝 Prompt:**")
                        st.code(row['Prompt_Text'], language=None, line_numbers=False)
                    
                    with col_right:
                        st.markdown("**🎓 Risposta Studente:**")
                        st.code(row['Student_Classification'], language=None, line_numbers=False)
                        
                        st.markdown("**🤖 Algoritmo:**")
                        st.caption(f"📌 {row['Corrected_Classification']}")
                        if 'All_Detected_Techniques' in row and pd.notna(row['All_Detected_Techniques']):
                            st.caption(f"🔍 Tutte: {row['All_Detected_Techniques']}")
                    
                    st.markdown("---")
                    st.markdown("### ⚡ Validazione Rapida")
                    
                    # Determina default per radio button
                    if is_validated:
                        if is_skipped:
                            default_option = "Scarta"
                        elif is_correct:
                            default_option = "Corretta"
                        elif is_partially_correct:
                            default_option = "Parziale"
                        else:
                            default_option = "Errata"
                    else:
                        default_option = None
                    
                    # Radio button per scelta rapida
                    validation_choice = st.radio(
                        "Scegli l'azione:",
                        options=["Conferma Algoritmo", "Corretta", "Parziale", "Errata", "Scarta"],
                        index=["Conferma Algoritmo", "Corretta", "Parziale", "Errata", "Scarta"].index(default_option) if default_option else 0,
                        key=f"choice_{idx}",
                        horizontal=True,
                        help="🤖 Conferma Algoritmo | ✅ Corretta | ⚠️ Parziale (aggiungi) | ❌ Errata (sostituisci) | ⏭️ Scarta"
                    )
                    
                    # Multiselect condizionale
                    selected_techniques = []
                    selected_motivation = None
                    if validation_choice in ["Parziale", "Errata", "Conferma Algoritmo"]:
                        # Default: recupera tecniche se già validato
                        default_tech = []
                        if is_validated:
                            corrected = validation.get('corrected_technique')
                            if isinstance(corrected, list):
                                default_tech = corrected
                            elif isinstance(corrected, str) and corrected:
                                default_tech = [corrected]
                        
                        # Se "Conferma Algoritmo", usa la classificazione dell'algoritmo
                        if validation_choice == "Conferma Algoritmo":
                            algo_class = row['Corrected_Classification']
                            if isinstance(algo_class, str):
                                default_tech = [t.strip() for t in algo_class.split('+')]
                        
                        label = "Tecniche da **aggiungere**:" if validation_choice == "Parziale" else "Tecniche **selezionate**:"
                        if validation_choice == "Conferma Algoritmo":
                            label = "Tecniche identificate dall'algoritmo:"
                        
                        selected_techniques = st.multiselect(
                            label,
                            options=all_techniques,
                            default=default_tech,
                            key=f"techniques_{idx}",
                            help="Parziale: aggiungi le mancanti | Errata/Conferma: tecniche corrette",
                            disabled=(validation_choice == "Conferma Algoritmo")  # Disabilita se conferma algoritmo
                        )
                        
                        # DROPDOWN MOTIVAZIONI PREIMPOSTATE
                        if selected_techniques:
                            st.markdown("#### 💡 Motivazione (opzionale)")
                            
                            # Determina quali motivazioni mostrare
                            motivations_to_show = []
                            
                            # Se è una combinazione comune, mostra quelle
                            if len(selected_techniques) > 1:
                                combo_key = " + ".join(sorted(selected_techniques))
                                if combo_key in MOTIVAZIONI_COMBINAZIONI:
                                    motivations_to_show = MOTIVAZIONI_COMBINAZIONI[combo_key]
                                    st.caption(f"🔗 Motivazioni per la combinazione: **{combo_key}**")
                            
                            # Altrimenti usa le motivazioni della singola tecnica
                            if not motivations_to_show and len(selected_techniques) == 1:
                                tech = selected_techniques[0]
                                if tech in MOTIVAZIONI_PREIMPOSTATE:
                                    motivations_to_show = MOTIVAZIONI_PREIMPOSTATE[tech]
                                    st.caption(f"Motivazioni per: **{tech}**")
                            
                            # Se nessuna motivazione specifica, mostra un messaggio
                            if not motivations_to_show:
                                motivations_to_show = [
                                    "Combinazione custom - specifica nelle note",
                                    "Motivazione non standard"
                                ]
                                st.caption("⚠️ Combinazione non standard - usa le note per dettagli")
                            
                            # Dropdown motivazioni
                            selected_motivation = st.selectbox(
                                "Seleziona motivazione",
                                options=["Nessuna"] + motivations_to_show,
                                key=f"motivation_{idx}",
                                label_visibility="collapsed",
                                help="Seleziona una motivazione preimpostata o lascia 'Nessuna' e specifica nelle note"
                            )
                    
                    # Note opzionali compatte
                    with st.expander("📝 Aggiungi note (opzionale)", expanded=False):
                        default_notes = validation.get('notes', '') if is_validated else ''
                        notes = st.text_area(
                            "Note",
                            value=default_notes,
                            key=f"validation_notes_{idx}",
                            placeholder="Es: 'Ambiguo', 'Click sbagliato', 'Manca contesto'...",
                            height=60,
                            label_visibility="collapsed"
                        )
                    
                    # Pulsante Salva unico
                    col_save, col_modify = st.columns([3, 1])
                    
                    with col_save:
                        # Determina se disabilitare
                        save_disabled = (validation_choice in ["Parziale", "Errata"] and len(selected_techniques) == 0)
                        
                        # Determina testo e icona
                        if validation_choice == "Conferma Algoritmo":
                            btn_text = "🤖 Conferma Classificazione Algoritmo"
                            btn_type = "primary"
                        elif validation_choice == "Corretta":
                            btn_text = "✅ Salva - Completamente Corretta"
                            btn_type = "primary"
                        elif validation_choice == "Parziale":
                            btn_text = "⚠️ Salva - Parzialmente Corretta"
                            btn_type = "secondary"
                        elif validation_choice == "Errata":
                            btn_text = "❌ Salva - Completamente Errata"
                            btn_type = "secondary"
                        else:  # Scarta
                            btn_text = "⏭️ Scarta dalla Validazione"
                            btn_type = "secondary"
                        
                        if st.button(btn_text, key=f"save_{idx}", disabled=save_disabled, use_container_width=True, type=btn_type):
                            if validation_choice == "Conferma Algoritmo":
                                st.session_state.manual_validations[idx] = {
                                    'is_correct': True,
                                    'partially_correct': False,
                                    'corrected_technique': row['Corrected_Classification'],
                                    'notes': st.session_state.get(f'validation_notes_{idx}', ''),
                                    'motivation': selected_motivation if selected_motivation and selected_motivation != "Nessuna" else '',
                                    'confirmed_algorithm': True
                                }
                                auto_save_validations()  # SALVATAGGIO AUTOMATICO
                                st.toast(f"🤖 Prompt #{idx}: Classificazione algoritmo confermata ({row['Corrected_Classification']})!", icon="🤖")
                            elif validation_choice == "Corretta":
                                st.session_state.manual_validations[idx] = {
                                    'is_correct': True,
                                    'partially_correct': False,
                                    'corrected_technique': None,
                                    'notes': st.session_state.get(f'validation_notes_{idx}', '')
                                }
                                auto_save_validations()  # SALVATAGGIO AUTOMATICO
                                st.toast(f"✅ Prompt #{idx}: Confermata corretta!", icon="✅")
                            elif validation_choice == "Parziale":
                                st.session_state.manual_validations[idx] = {
                                    'is_correct': False,
                                    'partially_correct': True,
                                    'corrected_technique': selected_techniques if len(selected_techniques) > 1 else selected_techniques[0],
                                    'notes': st.session_state.get(f'validation_notes_{idx}', ''),
                                    'motivation': selected_motivation if selected_motivation and selected_motivation != "Nessuna" else ''
                                }
                                auto_save_validations()  # SALVATAGGIO AUTOMATICO
                                st.toast(f"⚠️ Prompt #{idx}: Parziale (+{', '.join(selected_techniques)})!", icon="⚠️")
                            elif validation_choice == "Errata":
                                st.session_state.manual_validations[idx] = {
                                    'is_correct': False,
                                    'partially_correct': False,
                                    'corrected_technique': selected_techniques if len(selected_techniques) > 1 else selected_techniques[0],
                                    'notes': st.session_state.get(f'validation_notes_{idx}', ''),
                                    'motivation': selected_motivation if selected_motivation and selected_motivation != "Nessuna" else ''
                                }
                                auto_save_validations()  # SALVATAGGIO AUTOMATICO
                                st.toast(f"❌ Prompt #{idx}: Errata → {', '.join(selected_techniques)}!", icon="❌")
                            else:  # Scarta
                                st.session_state.manual_validations[idx] = {
                                    'is_correct': None,
                                    'skipped': True,
                                    'corrected_technique': None,
                                    'notes': st.session_state.get(f'validation_notes_{idx}', '')
                                }
                                auto_save_validations()  # SALVATAGGIO AUTOMATICO
                                st.toast(f"⏭️ Prompt #{idx}: Scartato!", icon="⏭️")
                    
                    with col_modify:
                        if is_validated:
                            if st.button("🔄 Reset", key=f"modify_{idx}", use_container_width=True):
                                del st.session_state.manual_validations[idx]
                                auto_save_validations()  # SALVATAGGIO AUTOMATICO
                                st.toast(f"♻️ Prompt #{idx}: Reset", icon="♻️")
                    
                    st.markdown("---")
                
                # Navigazione in fondo
                st.markdown("### 📄 Navigazione")
                colnav1, colnav2, colnav3 = st.columns([1, 2, 1])
                
                with colnav1:
                    if st.button("⬅️ Pagina Precedente", disabled=current_page == 0, key="nav_prev_bottom"):
                        st.session_state.validation_page -= 1
                        st.rerun()
                
                with colnav2:
                    st.markdown(f"<p style='text-align: center;'>Pagina {current_page + 1} di {total_pages}</p>", unsafe_allow_html=True)
                
                with colnav3:
                    if st.button("Pagina Successiva ➡️", disabled=current_page >= total_pages - 1, key="nav_next_bottom"):
                        st.session_state.validation_page += 1
                        st.rerun()
                
                st.markdown("---")
                
                # Pulsante per procedere a Fase 3
                st.markdown("### ➡️ Prossimo Passo")
                
                if validated_count >= len(doubtful_df):
                    st.success(f"🎉 Hai validato tutti i {len(doubtful_df)} casi dubbi! Procedi alla Fase 3 per vedere le statistiche finali.")
                    proceed_button_type = "primary"
                else:
                    st.warning(f"⚠️ Hai validato {validated_count}/{len(doubtful_df)} casi dubbi. Puoi procedere comunque o completare la validazione.")
                    proceed_button_type = "secondary"
                
                if st.button("▶️ Procedi a Fase 3: Statistiche Finali", type=proceed_button_type, use_container_width=True):
                    st.session_state.current_phase = 3
                    st.rerun()
        
        # ===== FASE 3: STATISTICHE & RISULTATI FINALI =====
        elif st.session_state.current_phase == 3:
            analyzed_df = st.session_state.analyzed_data.copy()
            
            st.header("📊 FASE 3: Statistiche & Risultati Finali")
            st.markdown("""
            Risultati finali combinando **correzioni automatiche** dell'algoritmo e **validazioni manuali** della Fase 2.
            """)
            
            # Applica validazioni manuali ai dati
            final_df = analyzed_df.copy()
            manual_validations = st.session_state.manual_validations
            
            if len(manual_validations) > 0:
                st.success(f"✅ {len(manual_validations)} validazioni manuali applicate ai risultati finali")
                
                # Applica le correzioni manuali
                for idx, validation in manual_validations.items():
                    if idx in final_df.index:
                        if validation.get('skipped', False):
                            # Prompt scartato - usa classificazione algoritmo
                            final_df.at[idx, 'Final_Classification'] = final_df.at[idx, 'Corrected_Classification']
                            final_df.at[idx, 'Manually_Validated'] = 'Skipped'
                        elif validation.get('is_correct', False):
                            # Studente era corretto - usa classificazione studente come finale
                            final_df.at[idx, 'Final_Classification'] = final_df.at[idx, 'Student_Classification']
                            final_df.at[idx, 'Manually_Validated'] = 'Confirmed_Student'
                        elif validation.get('partially_correct', False):
                            # Parzialmente corretto - combina risposta studente + tecniche aggiuntive
                            student_answer = final_df.at[idx, 'Student_Classification']
                            additional = validation['corrected_technique']
                            if isinstance(additional, list):
                                additional_str = ' + '.join(additional)
                            else:
                                additional_str = additional
                            final_df.at[idx, 'Final_Classification'] = f"{student_answer} + {additional_str}"
                            final_df.at[idx, 'Manually_Validated'] = 'Partially_Correct'
                        else:
                            # Completamente errato - usa correzione manuale
                            corrected = validation['corrected_technique']
                            if isinstance(corrected, list):
                                final_classification = ' + '.join(corrected)
                            else:
                                final_classification = corrected
                            final_df.at[idx, 'Final_Classification'] = final_classification
                            final_df.at[idx, 'Manually_Validated'] = 'Manually_Corrected'
                        
                        # Aggiungi note di validazione
                        final_df.at[idx, 'Validation_Notes'] = validation.get('notes', '')
            
            # Per tutti gli altri, usa la classificazione algoritmo
            if 'Final_Classification' not in final_df.columns:
                final_df['Final_Classification'] = final_df['Corrected_Classification']
                final_df['Manually_Validated'] = 'Algorithm_Only'
                final_df['Validation_Notes'] = ''
            else:
                final_df['Final_Classification'].fillna(final_df['Corrected_Classification'], inplace=True)
                final_df['Manually_Validated'].fillna('Algorithm_Only', inplace=True)
                if 'Validation_Notes' not in final_df.columns:
                    final_df['Validation_Notes'] = ''
                final_df['Validation_Notes'].fillna('', inplace=True)
            
            # Metriche principali Fase 3
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Prompts Analizzati", len(final_df))
            
            with col2:
                manual_count = len(manual_validations)
                st.metric(
                    "Validazioni Manuali",
                    manual_count,
                    delta=f"{(manual_count/len(final_df)*100):.1f}%"
                )
            
            with col3:
                confirmed_student = (final_df['Manually_Validated'] == 'Confirmed_Student').sum()
                st.metric(
                    "Studenti Confermati Corretti",
                    confirmed_student,
                    help="Casi dubbi dove la risposta studente è stata validata come corretta"
                )
            
            with col4:
                manually_corrected = (final_df['Manually_Validated'] == 'Manually_Corrected').sum()
                st.metric(
                    "Correzioni Manuali",
                    manually_corrected,
                    help="Casi dubbi dove è stata inserita una correzione manuale"
                )
            
            st.markdown("---")
            
            # ===== GRAFICI E VISUALIZZAZIONI (in expander) =====
            st.markdown("### 📈 Dashboard Statistica Interattiva")
            st.info("👇 **Clicca sulle sezioni** per mostrare/nascondere i grafici e analisi dettagliate")
            
            # Crea visualizzazioni
            visualizations = create_visualizations(final_df, manual_validations)
            
            # Grafico 1: Distribuzione Tecniche
            with st.expander("📊 Distribuzione Tecniche di Prompting", expanded=True):
                if 'techniques' in visualizations:
                    st.plotly_chart(visualizations['techniques'], use_container_width=True)
                    
                    # Tabella dettagliata
                    technique_counts = final_df['Final_Classification'].value_counts()
                    st.markdown("#### 📋 Tabella Dettagliata")
                    technique_df = pd.DataFrame({
                        'Tecnica': technique_counts.index,
                        'Conteggio': technique_counts.values,
                        'Percentuale': (technique_counts.values / len(final_df) * 100).round(2)
                    })
                    st.dataframe(technique_df, use_container_width=True)
            
            # Grafico 2: Distribuzione LLM
            with st.expander("🤖 Distribuzione LLM Utilizzati", expanded=False):
                if 'llms' in visualizations:
                    import hashlib
                    fig_data = visualizations['llms'].data[0]
                    data_hash = hashlib.md5(str(fig_data.values).encode()).hexdigest()
                    st.plotly_chart(
                        visualizations['llms'], 
                        use_container_width=True,
                        key=f"llm_chart_phase3_{data_hash}"
                    )
                    
                    # Dettagli varianti LLM
                    with st.expander("🔍 Dettaglio Varianti LLM (clicca per aprire)", expanded=False):
                        llm_variants = {}
                        for _, row in final_df.iterrows():
                            llm_norm = row['LLM_Used']
                            llm_orig = row.get('LLM_Original', llm_norm)
                            
                            if llm_norm not in llm_variants:
                                llm_variants[llm_norm] = {}
                            
                            if llm_orig not in llm_variants[llm_norm]:
                                llm_variants[llm_norm][llm_orig] = 0
                            llm_variants[llm_norm][llm_orig] += 1
                        
                        for llm_norm in sorted(llm_variants.keys()):
                            total_prompts = sum(llm_variants[llm_norm].values())
                            st.markdown(f"#### 🤖 **{llm_norm}** ({total_prompts} prompt)")
                            sorted_variants = sorted(llm_variants[llm_norm].items(), key=lambda x: x[1], reverse=True)
                            for variant, count in sorted_variants:
                                percentage = (count / total_prompts) * 100
                                st.write(f"  • `{variant}`: {count} ({percentage:.1f}%)")
                            st.markdown("---")
            
            # Grafico 3: Confronto Studenti vs Algoritmo
            with st.expander("📊 Confronto Classificazioni: Studenti vs Algoritmo", expanded=False):
                if 'comparison' in visualizations:
                    st.plotly_chart(visualizations['comparison'], use_container_width=True)
            
            # Grafico 4: Tasso di Errore
            with st.expander("🎯 Tasso di Errore degli Studenti", expanded=False):
                st.markdown("""
                **📊 Cos'è il Tasso di Errore?**
                
                Percentuale di prompt dove gli studenti hanno classificato erroneamente rispetto al totale.
                
                **Interpretazione:**
                - 🟢 **0-25%**: Ottimo! Gli studenti hanno capito bene
                - 🟡 **25-50%**: Discreto - Alcuni errori
                - 🟠 **50-75%**: Criticità - Molti errori
                - 🔴 **75-100%**: Problematico - Difficoltà diffuse
                """)
                
                if 'error_rate' in visualizations:
                    st.plotly_chart(visualizations['error_rate'], use_container_width=True)
            
            # Grafico 5: Match Types
            with st.expander("🎯 Qualità Classificazioni: Match Types", expanded=False):
                st.markdown("""
                **📊 Tipologie di Match:**
                
                - **✅ Match Esatto**: Studente ha classificato esattamente giusto
                - **⚠️ Match Parziale**: Studente ha menzionato UNA tecnica corretta ma incompletamente
                - **❌ Errore**: Classificazione errata (non corrisponde a nulla di rilevato)
                """)
                
                if 'match_types' in visualizations:
                    st.plotly_chart(visualizations['match_types'], use_container_width=True)
            
            st.markdown("---")
            
            # ===== STATISTICHE DETTAGLIATE =====
            st.markdown("### 📊 Statistiche Dettagliate")
            
            # Statistica 1: Analisi per Modello LLM
            with st.expander("🤖 Analisi Dettagliata per Modello LLM", expanded=False):
                st.markdown("#### 📈 Prestazioni per Modello LLM")
                st.caption("Analisi della distribuzione delle tecniche e degli errori per ciascun modello LLM utilizzato")
                
                # Raggruppa per LLM
                llm_stats = []
                for llm in final_df['LLM_Used'].unique():
                    llm_df = final_df[final_df['LLM_Used'] == llm]
                    total_prompts = len(llm_df)
                    
                    # Calcola errori (match_type = 'error')
                    errors = (llm_df['Match_Type'] == 'error').sum()
                    error_rate = (errors / total_prompts * 100) if total_prompts > 0 else 0
                    
                    # Tecnica più usata
                    most_common_technique = llm_df['Final_Classification'].mode()[0] if len(llm_df) > 0 else 'N/A'
                    
                    # Validazioni manuali
                    manual_vals = llm_df[llm_df['Manually_Validated'] != 'Algorithm_Only']
                    manual_count = len(manual_vals)
                    manual_pct = (manual_count / total_prompts * 100) if total_prompts > 0 else 0
                    
                    llm_stats.append({
                        'Modello LLM': llm,
                        'Tot. Prompts': total_prompts,
                        'Errori Studenti': errors,
                        '% Errori': f"{error_rate:.1f}%",
                        'Tecnica Più Usata': most_common_technique,
                        'Validazioni Manuali': manual_count,
                        '% Validazioni': f"{manual_pct:.1f}%"
                    })
                
                llm_stats_df = pd.DataFrame(llm_stats).sort_values('Tot. Prompts', ascending=False)
                st.dataframe(llm_stats_df, use_container_width=True, hide_index=True)
                
                # Download CSV statistiche LLM
                csv_llm = llm_stats_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Scarica Statistiche LLM (CSV)",
                    data=csv_llm,
                    file_name="statistiche_per_LLM.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Statistica 2: Analisi per Tecnica di Prompting
            with st.expander("🎯 Analisi Dettagliata per Tecnica di Prompting", expanded=False):
                st.markdown("#### 📊 Prestazioni per Tecnica di Prompting")
                st.caption("Analisi della distribuzione e degli errori per ciascuna tecnica di prompting rilevata")
                
                # Raggruppa per tecnica
                technique_stats = []
                for technique in final_df['Final_Classification'].unique():
                    tech_df = final_df[final_df['Final_Classification'] == technique]
                    total_prompts = len(tech_df)
                    
                    # Calcola errori
                    errors = (tech_df['Match_Type'] == 'error').sum()
                    error_rate = (errors / total_prompts * 100) if total_prompts > 0 else 0
                    
                    # Match esatti
                    exact_matches = (tech_df['Match_Type'] == 'exact').sum()
                    exact_pct = (exact_matches / total_prompts * 100) if total_prompts > 0 else 0
                    
                    # LLM più usato per questa tecnica
                    most_common_llm = tech_df['LLM_Used'].mode()[0] if len(tech_df) > 0 else 'N/A'
                    
                    # Confidenza media
                    avg_confidence = tech_df['Confidence'].mean() if 'Confidence' in tech_df.columns else 0
                    
                    technique_stats.append({
                        'Tecnica': technique,
                        'Tot. Prompts': total_prompts,
                        '% sul Totale': f"{(total_prompts/len(final_df)*100):.1f}%",
                        'Match Esatti': exact_matches,
                        '% Match Esatti': f"{exact_pct:.1f}%",
                        'Errori': errors,
                        '% Errori': f"{error_rate:.1f}%",
                        'LLM Predominante': most_common_llm,
                        'Confidenza Media': f"{avg_confidence:.1f}%"
                    })
                
                technique_stats_df = pd.DataFrame(technique_stats).sort_values('Tot. Prompts', ascending=False)
                st.dataframe(technique_stats_df, use_container_width=True, hide_index=True)
                
                # Download CSV statistiche tecniche
                csv_tech = technique_stats_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Scarica Statistiche Tecniche (CSV)",
                    data=csv_tech,
                    file_name="statistiche_per_tecnica.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Statistica 3: Matrice Confusione (Studente vs Corretto)
            with st.expander("🔀 Matrice di Confusione: Studente vs Corretto", expanded=False):
                st.markdown("#### 📊 Confronto Classificazioni Studente vs Finale")
                st.caption("Mostra le corrispondenze tra ciò che hanno classificato gli studenti e la classificazione finale corretta")
                
                # Crea matrice confusione
                confusion_data = []
                for idx, row in final_df.iterrows():
                    student_class = row['Student_Classification']
                    final_class = row['Final_Classification']
                    
                    confusion_data.append({
                        'Classificazione Studente': student_class,
                        'Classificazione Finale': final_class,
                        'Match Type': row['Match_Type']
                    })
                
                confusion_df = pd.DataFrame(confusion_data)
                
                # Conta occorrenze
                confusion_matrix = confusion_df.groupby(['Classificazione Studente', 'Classificazione Finale']).size().reset_index(name='Conteggio')
                confusion_matrix = confusion_matrix.sort_values('Conteggio', ascending=False)
                
                st.dataframe(confusion_matrix.head(30), use_container_width=True, hide_index=True)
                st.caption("Mostrate le prime 30 combinazioni più frequenti")
                
                # Download matrice confusione completa
                csv_confusion = confusion_matrix.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Scarica Matrice Confusione Completa (CSV)",
                    data=csv_confusion,
                    file_name="matrice_confusione.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            st.markdown("---")
            
            # Tabella Finale Completa
            with st.expander("📋 Visualizza Tabella Completa Risultati Finali", expanded=False):
                display_cols = [
                    'Application', 'LLM_Used', 'Prompt_Text', 
                    'Student_Classification', 'Final_Classification',
                    'Confidence', 'Match_Type', 'Manually_Validated', 'Validation_Notes'
                ]
                available_cols = [col for col in display_cols if col in final_df.columns]
                st.dataframe(final_df[available_cols], use_container_width=True, height=400)
            
            # Riepilogo Note di Validazione
            if len(manual_validations) > 0:
                notes_with_text = {idx: val for idx, val in manual_validations.items() if val.get('notes', '').strip() != ''}
                
                if len(notes_with_text) > 0:
                    with st.expander(f"📝 Note Validazioni Manuali ({len(notes_with_text)} con motivazione)", expanded=False):
                        st.markdown("""
                        **Motivazioni inserite durante la validazione manuale:**
                        
                        Queste note possono essere utili per discutere casi particolari o spiegare decisioni di validazione.
                        """)
                        
                        for idx, val in notes_with_text.items():
                            row = final_df.loc[idx]
                            st.markdown(f"**Prompt #{idx}** - {row['Application']}")
                            st.markdown(f"- **Studente**: {row['Student_Classification']}")
                            if val['is_correct']:
                                st.success(f"✅ Confermato corretto")
                            else:
                                corrected = val['corrected_technique']
                                if isinstance(corrected, list):
                                    corrected_str = ' + '.join(corrected)
                                else:
                                    corrected_str = corrected
                                st.warning(f"✏️ Corretto in: {corrected_str}")
                            st.info(f"💬 **Motivazione**: {val['notes']}")
                            st.markdown("---")
            
            # Download Risultati Finali
            st.markdown("---")
            st.markdown("### 💾 Download Risultati Finali")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download Excel con solo risultati finali
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    final_df.to_excel(writer, sheet_name='Final_Results', index=False)
                output.seek(0)
                
                st.download_button(
                    label="📥 Scarica Risultati Finali (Excel)",
                    data=output,
                    file_name="Final_Prompt_Analysis_Results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary"
                )
            
            with col2:
                # Download Excel completo con tutte le statistiche
                output_complete = BytesIO()
                
                # Prepara i dati delle statistiche
                # Statistiche LLM
                llm_stats = []
                for llm in final_df['LLM_Used'].unique():
                    llm_df = final_df[final_df['LLM_Used'] == llm]
                    total_prompts = len(llm_df)
                    errors = (llm_df['Match_Type'] == 'error').sum()
                    error_rate = (errors / total_prompts * 100) if total_prompts > 0 else 0
                    most_common_technique = llm_df['Final_Classification'].mode()[0] if len(llm_df) > 0 else 'N/A'
                    manual_vals = llm_df[llm_df['Manually_Validated'] != 'Algorithm_Only']
                    manual_count = len(manual_vals)
                    manual_pct = (manual_count / total_prompts * 100) if total_prompts > 0 else 0
                    
                    llm_stats.append({
                        'Modello LLM': llm,
                        'Tot. Prompts': total_prompts,
                        'Errori Studenti': errors,
                        '% Errori': error_rate,
                        'Tecnica Più Usata': most_common_technique,
                        'Validazioni Manuali': manual_count,
                        '% Validazioni': manual_pct
                    })
                llm_stats_df = pd.DataFrame(llm_stats).sort_values('Tot. Prompts', ascending=False)
                
                # Statistiche Tecniche
                technique_stats = []
                for technique in final_df['Final_Classification'].unique():
                    tech_df = final_df[final_df['Final_Classification'] == technique]
                    total_prompts = len(tech_df)
                    errors = (tech_df['Match_Type'] == 'error').sum()
                    error_rate = (errors / total_prompts * 100) if total_prompts > 0 else 0
                    exact_matches = (tech_df['Match_Type'] == 'exact').sum()
                    exact_pct = (exact_matches / total_prompts * 100) if total_prompts > 0 else 0
                    most_common_llm = tech_df['LLM_Used'].mode()[0] if len(tech_df) > 0 else 'N/A'
                    avg_confidence = tech_df['Confidence'].mean() if 'Confidence' in tech_df.columns else 0
                    
                    technique_stats.append({
                        'Tecnica': technique,
                        'Tot. Prompts': total_prompts,
                        '% sul Totale': (total_prompts/len(final_df)*100),
                        'Match Esatti': exact_matches,
                        '% Match Esatti': exact_pct,
                        'Errori': errors,
                        '% Errori': error_rate,
                        'LLM Predominante': most_common_llm,
                        'Confidenza Media': avg_confidence
                    })
                technique_stats_df = pd.DataFrame(technique_stats).sort_values('Tot. Prompts', ascending=False)
                
                # Matrice Confusione
                confusion_data = []
                for idx, row in final_df.iterrows():
                    confusion_data.append({
                        'Classificazione Studente': row['Student_Classification'],
                        'Classificazione Finale': row['Final_Classification'],
                        'Match Type': row['Match_Type']
                    })
                confusion_df = pd.DataFrame(confusion_data)
                confusion_matrix = confusion_df.groupby(['Classificazione Studente', 'Classificazione Finale']).size().reset_index(name='Conteggio')
                confusion_matrix = confusion_matrix.sort_values('Conteggio', ascending=False)
                
                # Crea Excel multi-foglio
                with pd.ExcelWriter(output_complete, engine='openpyxl') as writer:
                    final_df.to_excel(writer, sheet_name='Risultati_Finali', index=False)
                    llm_stats_df.to_excel(writer, sheet_name='Statistiche_LLM', index=False)
                    technique_stats_df.to_excel(writer, sheet_name='Statistiche_Tecniche', index=False)
                    confusion_matrix.to_excel(writer, sheet_name='Matrice_Confusione', index=False)
                output_complete.seek(0)
                
                st.download_button(
                    label="📊 Scarica Report Completo con Statistiche (Excel)",
                    data=output_complete,
                    file_name="Report_Completo_Analisi_Prompting.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="secondary"
                )
            
            st.markdown("---")
            
            # Pulsanti navigazione
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("⬅️ Torna a Fase 1 (Rianalizza)", use_container_width=True):
                    st.session_state.current_phase = 1
                    st.rerun()
            
            with col2:
                if st.button("⬅️ Torna a Fase 2 (Modifica Validazioni)", use_container_width=True):
                    st.session_state.current_phase = 2
                    st.rerun()
    
    except Exception as e:
        st.error(f"❌ Errore durante l'elaborazione: {str(e)}")
        st.exception(e)
else:
    st.info("👈 Carica il file **Prompt.xlsx** dalla sidebar per iniziare l'analisi")
    
    st.markdown("---")
    st.markdown("### 📖 Come Funziona")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 📂 FASE 1
        **Caricamento & Analisi Automatica**
        
        1. Carica file Excel
        2. Algoritmo analizza tutti i prompt
        3. Rileva tecniche automaticamente
        4. Identifica casi dubbi (<70% confidenza)
        """)
    
    with col2:
        st.markdown("""
        #### ✏️ FASE 2
        **Validazione Manuale**
        
        1. Valida solo i casi dubbi
        2. ✅ Conferma risposta studente
        3. ✏️ oppure correggi manualmente
        4. Multi-selezione tecniche possibile
        """)
    
    with col3:
        st.markdown("""
        #### 📊 FASE 3
        **Statistiche Finali**
        
        1. Risultati completi
        2. Grafici interattivi (espandibili)
        3. Dashboard statistica
        4. Download Excel risultati
        """)
    
    st.markdown("---")
    st.success("🚀 **Carica il file per iniziare!**")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p style='margin-bottom: 5px;'><strong>Applicazione per l'analisi sistematica di Prompt Engineering</strong></p>
    <p style='margin-bottom: 5px;'>Basato su "A Systematic Survey of Prompt Engineering in Large Language Models"</p>
    <p style='margin-bottom: 5px;'>Corso di Software Testing - Prof. Porfirio Tramontana</p>
    <p style='margin-bottom: 5px;'>Università degli Studi di Napoli Federico II</p>
    <p style='margin-top: 15px; font-style: italic;'>A cura di Castrese Basile - 2026</p>
</div>
""", unsafe_allow_html=True)
