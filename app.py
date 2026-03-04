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

# Configurazioni rimosse per semplificazione

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

if 'categorized_labels' not in st.session_state:
    st.session_state.categorized_labels = {}  # {idx: 'Label pulita'} per risposte corrette

if 'label_counts' not in st.session_state:
    st.session_state.label_counts = {}  # {'Zero-Shot': 15, 'Few-Shot': 23, ...} registrazione manuale etichette

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
st.title("Analisi di Prompt Engineering")
st.markdown("""
Analisi e validazione delle tecniche di prompting secondo la tassonomia del paper  
*'A Systematic Survey of Prompt Engineering in Large Language Models'*.  
Progetto per il corso di Software Testing - Prof. Porfirio Tramontana  
Università degli Studi di Napoli Federico II - A cura di Castrese Basile
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
            analyzed_df['Student_Classification'].str.contains(technique, case=False, na=False, regex=False)
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
                analyzed_df['Student_Classification'].str.contains(tech, case=False, na=False, regex=False)
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
st.sidebar.header("Gestione Backup")

if st.session_state.manual_validations:
    st.sidebar.success(f"✅ {len(st.session_state.manual_validations)} validazioni in memoria")
    if st.sidebar.button("Salva Backup Manualmente", use_container_width=True):
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
    phase22_class = "phase-active" if current_phase == 2.2 else ("phase-completed" if current_phase > 2.2 else "phase-pending")
    phase3_class = "phase-active" if current_phase == 3 else "phase-pending"
    
    st.markdown(f"""
    <div class="phase-container">
        <div class="phase-step {phase1_class}">
            <div style="font-size: 20px;">📂</div>
            <div>FASE 1</div>
            <div style="font-size: 10px; opacity: 0.9;">Analisi Auto</div>
        </div>
        <div class="phase-step {phase2_class}">
            <div style="font-size: 20px;">✏️</div>
            <div>FASE 2</div>
            <div style="font-size: 10px; opacity: 0.9;">Validazione</div>
        </div>
        <div class="phase-step {phase22_class}">
            <div style="font-size: 20px;">🏷️</div>
            <div>FASE 2.2</div>
            <div style="font-size: 10px; opacity: 0.9;">Categorizzazione</div>
        </div>
        <div class="phase-step {phase3_class}">
            <div style="font-size: 20px;">📊</div>
            <div>FASE 3</div>
            <div style="font-size: 10px; opacity: 0.9;">Statistiche</div>
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
            total_doubtful = len(doubtful_df)  # Salva il totale prima del filtro
            
            # Toggle per filtrare i prompt già validati (se ci sono validazioni)
            if st.session_state.manual_validations:
                col_toggle1, col_toggle2 = st.columns([3, 1])
                with col_toggle1:
                    previous_filter = st.session_state.filter_validated
                    show_only_unvalidated = st.checkbox(
                        "🎯 Mostra solo prompt NON ancora validati", 
                        value=st.session_state.filter_validated,
                        help="Se attivo, nasconde i prompt che hai già validato",
                        key="toggle_filter_validated"
                    )
                    # Reset pagina se il filtro è cambiato
                    if previous_filter != show_only_unvalidated:
                        st.session_state.validation_page = 0
                    # Aggiorna il session state
                    st.session_state.filter_validated = show_only_unvalidated
                with col_toggle2:
                    pass  # Spacer
            
            # Se riprendi validazioni, filtra solo quelle NON ancora validate
            if st.session_state.filter_validated and st.session_state.manual_validations:
                validated_indices = set(st.session_state.manual_validations.keys())
                doubtful_df = doubtful_df[~doubtful_df.index.isin(validated_indices)]
                
                if len(st.session_state.manual_validations) > 0:
                    st.info(f"📝 **Filtro attivo**: Mostro solo {len(doubtful_df)} istanze NON ancora validate. ({len(st.session_state.manual_validations)} già validate nascoste)")
            
            if len(doubtful_df) == 0:
                st.success("🎉 Nessun caso dubbio da validare!")
                
                col_phase_nav1, col_phase_nav2 = st.columns(2)
                
                with col_phase_nav1:
                    if st.button("▶️ Procedi a Fase 2.2: Categorizzazione Risposte", type="primary", use_container_width=True):
                        st.session_state.current_phase = 2.2
                        st.rerun()
                
                with col_phase_nav2:
                    if st.button("⏭️ Salta a Fase 3: Statistiche Finali", type="secondary", use_container_width=True):
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
                    st.metric("Casi Dubbi Totali", total_doubtful)
                
                with col2:
                    st.metric(
                        "Validati",
                        validated_count,
                        delta=f"{(validated_count/total_doubtful*100):.0f}%" if total_doubtful > 0 else "0%"
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
                    remaining = total_doubtful - total_processed
                    st.metric(
                        "Rimanenti",
                        max(0, remaining),  # Non mostrare valori negativi
                        delta_color="inverse"
                    )
                
                # Progress Bar
                progress_pct = (validated_count / total_doubtful * 100) if total_doubtful > 0 else 0
                st.progress(progress_pct / 100, text=f"Progresso: {validated_count}/{total_doubtful} validati ({progress_pct:.1f}%)")
                
                st.info("Le modifiche vengono salvate automaticamente. Al cambio pagina i dati vengono aggiornati.")
                
                # === BACKUP E RIPRISTINO ===
                st.markdown("### Backup e Ripristino")
                
                col_backup1, col_backup2, col_backup3 = st.columns([2, 2, 1])
                
                with col_backup1:
                    st.success(f"Auto-salvataggio attivo: {len(st.session_state.manual_validations)} validazioni salvate")
                
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
                            label="Scarica Backup JSON",
                            data=backup_json,
                            file_name=f"validazioni_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True,
                            help="Scarica un file JSON con tutte le tue validazioni"
                        )
                
                with col_backup3:
                    # Pulsante per caricare backup
                    uploaded_backup = st.file_uploader(
                        "Carica Backup",
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
                total_pages = max(1, (len(doubtful_df) + items_per_page - 1) // items_per_page)
                # Assicura che current_page sia valida
                current_page = min(st.session_state.validation_page, total_pages - 1)
                st.session_state.validation_page = max(0, current_page)
                
                col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
                
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
                
                with col4:
                    # Pulsante per saltare al primo non validato
                    if not st.session_state.filter_validated and st.button("🎯 Vai a non validati", help="Attiva filtro e vai all'inizio"):
                        st.session_state.filter_validated = True
                        st.session_state.validation_page = 0
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
                    
                    # Note opzionali compatte
                    with st.expander("Aggiungi note (opzionale)", expanded=False):
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
                                    'confirmed_algorithm': True
                                }
                                auto_save_validations()
                                st.toast(f"Prompt #{idx}: Classificazione algoritmo confermata ({row['Corrected_Classification']})")
                            elif validation_choice == "Corretta":
                                st.session_state.manual_validations[idx] = {
                                    'is_correct': True,
                                    'partially_correct': False,
                                    'corrected_technique': None,
                                    'notes': st.session_state.get(f'validation_notes_{idx}', '')
                                }
                                auto_save_validations()
                                st.toast(f"Prompt #{idx}: Confermata corretta")
                            elif validation_choice == "Parziale":
                                st.session_state.manual_validations[idx] = {
                                    'is_correct': False,
                                    'partially_correct': True,
                                    'corrected_technique': selected_techniques if len(selected_techniques) > 1 else selected_techniques[0],
                                    'notes': st.session_state.get(f'validation_notes_{idx}', '')
                                }
                                auto_save_validations()
                                st.toast(f"Prompt #{idx}: Parziale (+{', '.join(selected_techniques)})")
                            elif validation_choice == "Errata":
                                st.session_state.manual_validations[idx] = {
                                    'is_correct': False,
                                    'partially_correct': False,
                                    'corrected_technique': selected_techniques if len(selected_techniques) > 1 else selected_techniques[0],
                                    'notes': st.session_state.get(f'validation_notes_{idx}', '')
                                }
                                auto_save_validations()
                                st.toast(f"Prompt #{idx}: Errata -> {', '.join(selected_techniques)}")
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
                
                # Pulsante per procedere a Fase 2.2
                st.markdown("### ➡️ Prossimo Passo")
                
                if validated_count >= total_doubtful:
                    st.success(f"🎉 Hai validato tutti i {total_doubtful} casi dubbi! Procedi alla Fase 2.2 per categorizzare le risposte corrette.")
                    proceed_button_type = "primary"
                else:
                    st.warning(f"⚠️ Hai validato {validated_count}/{total_doubtful} casi dubbi. Puoi procedere comunque o completare la validazione.")
                    proceed_button_type = "secondary"
                
                if st.button("▶️ Procedi a Fase 2.2: Categorizzazione Risposte", type=proceed_button_type, use_container_width=True):
                    st.session_state.current_phase = 2.2
                    st.rerun()
        
        # ===== FASE 2.2: ESPORTA RISPOSTE CORRETTE =====
        elif st.session_state.current_phase == 2.2:
            st.header("📥 FASE 2.2: Esporta Risposte Validate come Corrette")
            st.markdown("""
            In questa fase puoi **esportare** solo le risposte dove hai cliccato **"✅ Corretta"** nella Fase 2.
            
            **Contenuto:** SOLO le risposte dove hai confermato che lo studente aveva ragione.
            
            **Escluso:** 
            - Risposte "Parziali" (dove hai aggiunto tecniche)
            - Risposte "Errate" (anche se le hai corrette)
            - Risposte dove hai confermato l'algoritmo
            - Match esatti non validati manualmente
            """)
            
            analyzed_df = st.session_state.analyzed_data
            manual_validations = st.session_state.manual_validations
            
            # Filtra SOLO le risposte dove hai cliccato "Corretta"
            correct_indices = [idx for idx, val in manual_validations.items() 
                             if val.get('is_correct', False) 
                             and not val.get('partially_correct', False)
                             and not val.get('skipped', False)
                             and not val.get('confirmed_algorithm', False)]
            
            if len(correct_indices) == 0:
                st.info("ℹ️ Nessuna risposta validata manualmente come \"Corretta\" nella Fase 2. Procedi alla Fase 3.")
                if st.button("▶️ Salta a Fase 3: Statistiche Finali", type="primary"):
                    st.session_state.current_phase = 3
                    st.rerun()
            else:
                st.success(f"✅ {len(correct_indices)} risposte validate manualmente come **Corretta** pronte per l'esportazione")
                
                # Crea DataFrame con le risposte corrette
                correct_df = analyzed_df.loc[correct_indices].copy()
                
                # Seleziona SOLO colonne degli studenti (senza algoritmo)
                possible_columns = [
                    'Application', 'LLM_Used', 'Prompt_Text', 
                    'Student_Classification'
                ]
                export_columns = [col for col in possible_columns if col in correct_df.columns]
                export_df = correct_df[export_columns]
                
                # Preview dei dati
                st.markdown("### 👀 Anteprima Dati da Esportare")
                st.dataframe(export_df.head(10), use_container_width=True)
                
                if len(correct_indices) > 10:
                    st.caption(f"Mostrate prime 10 righe di {len(correct_indices)} totali")
                
                st.markdown("---")
                
                # Pulsante per esportare
                st.markdown("### 💾 Esporta in Excel")
                
                import io
                from datetime import datetime
                
                # Crea file Excel in memoria
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    export_df.to_excel(writer, sheet_name='Validate_Corrette', index=True)
                output.seek(0)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"validate_corrette_{timestamp}.xlsx"
                
                st.download_button(
                    label=f"📥 Scarica Excel - {len(correct_indices)} Risposte Validate come Corrette",
                    data=output,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True,
                    help="Include SOLO le risposte dove hai cliccato il pulsante '✅ Corretta' nella Fase 2"
                )
                
                st.markdown("---")
                
                # Sezione per registrare etichette e conteggi manualmente
                st.markdown("### Registra Risultati per Etichetta (Opzionale)")
                st.markdown("""
                Inserisci manualmente quante istanze validate come corrette appartengono a ciascuna tecnica/etichetta.
                Questo è opzionale e serve per documentazione aggiuntiva.
                """)
                
                # Lista tecniche standard
                standard_labels = [
                    "Zero-Shot", "Few-Shot", "Chain-of-Thought", "Auto-CoT", "LogiCoT", "LCoT",
                    "Tree-of-Thoughts", "Graph-of-Thought", "Self-Consistency", "System-2-Attention",
                    "Structured CoT", "Program-of-Thoughts", "Chain-of-Code", "Scratchpad",
                    "Self-Refine", "Take-a-Step-Back", "Fix-Prompt", "Persona/Role Prompting",
                    "Few-Shot + Chain-of-Thought", "Persona + Few-Shot", "Persona + Chain-of-Thought"
                ]
                
                # Scegli tra etichetta predefinita o personalizzata
                label_type = st.radio(
                    "Tipo di etichetta:",
                    options=["Predefinita", "Personalizzata"],
                    horizontal=True,
                    key="label_type_radio"
                )
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    if label_type == "Predefinita":
                        selected_label = st.selectbox(
                            "Seleziona Etichetta",
                            options=standard_labels,
                            key="label_selector"
                        )
                    else:
                        selected_label = st.text_input(
                            "Inserisci Etichetta Personalizzata",
                            placeholder="Es: Zero-Shot + LCoT",
                            key="custom_label_input"
                        )
                
                with col2:
                    count_value = st.number_input(
                        "Numero Istanze",
                        min_value=0,
                        max_value=len(correct_indices),
                        value=1,
                        step=1,
                        key="count_input"
                    )
                
                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                    # Disabilita il pulsante se l'etichetta personalizzata è vuota
                    is_disabled = (label_type == "Personalizzata" and not selected_label)
                    if st.button("Aggiungi", type="secondary", use_container_width=True, disabled=is_disabled):
                        st.session_state.label_counts[selected_label] = count_value
                        st.success(f"Aggiunto: {selected_label} = {count_value}")
                        st.rerun()
                
                # Mostra etichette registrate
                if len(st.session_state.label_counts) > 0:
                    st.markdown("#### Etichette Registrate")
                    
                    # Crea tabella con le etichette
                    labels_data = []
                    for label, count in st.session_state.label_counts.items():
                        labels_data.append({
                            'Etichetta': label,
                            'Numero Istanze': count
                        })
                    
                    labels_df = pd.DataFrame(labels_data)
                    
                    # Mostra con opzione di rimozione
                    for idx, row in labels_df.iterrows():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.text(f"🏷️ {row['Etichetta']}")
                        with col2:
                            st.text(f"📊 {row['Numero Istanze']}")
                        with col3:
                            if st.button("🗑️", key=f"remove_{idx}", help="Rimuovi questa etichetta"):
                                del st.session_state.label_counts[row['Etichetta']]
                                st.rerun()
                    
                    # Totale
                    total_counted = sum(st.session_state.label_counts.values())
                    st.metric("Totale Istanze Registrate", total_counted)
                    
                    # Esporta anche le etichette in Excel
                    st.markdown("---")
                    output_labels = io.BytesIO()
                    with pd.ExcelWriter(output_labels, engine='openpyxl') as writer:
                        labels_df.to_excel(writer, sheet_name='Etichette_Conteggi', index=False)
                    output_labels.seek(0)
                    
                    timestamp_labels = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename_labels = f"etichette_conteggi_{timestamp_labels}.xlsx"
                    
                    st.download_button(
                        label="📊 Scarica Excel con Etichette e Conteggi",
                        data=output_labels,
                        file_name=filename_labels,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="secondary",
                        use_container_width=True
                    )
                else:
                    st.info("ℹ️ Nessuna etichetta registrata ancora. Aggiungi la prima etichetta sopra.")
                
                st.markdown("---")
                
                # Pulsante per procedere a Fase 3
                st.markdown("### ➡️ Prossimo Passo")
                st.info("Puoi scaricare i file Excel e poi procedere alle statistiche finali")
                
                if st.button("▶️ Procedi a Fase 3: Statistiche Finali", type="primary", use_container_width=True):
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
                            # Studente era corretto - marcatore per etichetta manuale (Fase 2.2)
                            final_df.at[idx, 'Final_Classification'] = '[ETICHETTA_MANUALE]'
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
            
            # RICALCOLA Match_Type basandosi su Final_Classification (post-validazione)
            def recalculate_match_type(row):
                final_class = str(row['Final_Classification']).lower().strip()
                
                # Caso speciale: etichetta manuale dalla Fase 2.2 (studente confermato corretto)
                if final_class == '[etichetta_manuale]':
                    return 'exact'
                
                student_class = str(row['Student_Classification']).lower().strip()
                
                # Match esatto: studente ha scritto esattamente la tecnica finale (case-insensitive)
                if student_class == final_class:
                    return 'exact'
                
                # Match parziale: uno contiene l'altro
                if student_class in final_class or final_class in student_class:
                    return 'partial'
                
                # Controllo per tecniche combinate (es. "Few-Shot" in "Persona + Few-Shot")
                final_parts = [p.strip().lower() for p in final_class.split('+')]
                if student_class in final_parts or any(student_class in part for part in final_parts):
                    return 'partial'
                
                # Nessun match: errore
                return 'error'
            
            final_df['Match_Type'] = final_df.apply(recalculate_match_type, axis=1)
            
            # Metriche principali Fase 3
            col1, col2, col3 = st.columns(3)
            
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
            
            st.markdown("---")
            
            # ===== GRAFICI E VISUALIZZAZIONI (in expander) =====
            st.markdown("### 📈 Dashboard Statistica Interattiva")
            st.info("👇 **Clicca sulle sezioni** per mostrare/nascondere i grafici e analisi dettagliate")
            
            # Crea visualizzazioni
            visualizations = create_visualizations(final_df, manual_validations)
            
            # Grafico 1: Distribuzione Tecniche
            with st.expander("📊 Distribuzione Tecniche di Prompting", expanded=True):
                # Combina etichette manuali (Fase 2.2) con classificazioni automatiche/corrette
                label_counts_manual = st.session_state.label_counts
                
                # Conta tecniche da final_df (escludendo le etichette manuali)
                technique_counts_auto = final_df[final_df['Final_Classification'] != '[ETICHETTA_MANUALE]']['Final_Classification'].value_counts()
                
                # Combina i due dizionari
                combined_counts = {}
                
                # Aggiungi conteggi automatici
                for tech, count in technique_counts_auto.items():
                    combined_counts[tech] = count
                
                # Aggiungi/somma conteggi manuali dalla Fase 2.2
                for label, count in label_counts_manual.items():
                    if label in combined_counts:
                        combined_counts[label] += count
                    else:
                        combined_counts[label] = count
                
                if len(combined_counts) > 0:
                    # Crea DataFrame ordinato
                    sorted_counts = sorted(combined_counts.items(), key=lambda x: x[1], reverse=True)
                    technique_df = pd.DataFrame({
                        'Tecnica': [t[0] for t in sorted_counts],
                        'Conteggio': [t[1] for t in sorted_counts],
                        'Percentuale': [(t[1] / len(final_df) * 100) for t in sorted_counts]
                    })
                    technique_df['Percentuale'] = technique_df['Percentuale'].round(2)
                    
                    # Crea grafico
                    import plotly.express as px
                    fig = px.bar(
                        technique_df,
                        x='Tecnica',
                        y='Conteggio',
                        title='Distribuzione Tecniche di Prompting (Finali)',
                        text='Conteggio'
                    )
                    fig.update_traces(textposition='outside')
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tabella dettagliata
                    st.markdown("#### 📋 Tabella Dettagliata")
                    if len(label_counts_manual) > 0:
                        st.info(f"✅ Include {sum(label_counts_manual.values())} istanze corrette registrate manualmente nella Fase 2.2")
                    st.dataframe(technique_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("Nessuna tecnica da visualizzare")
            
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
                    
                    # Dettagli varianti LLM (senza expander annidato)
                    st.markdown("---")
                    st.markdown("#### 🔍 Dettaglio Varianti LLM")
                    
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
                        st.markdown(f"**{llm_norm}** ({total_prompts} prompt)")
                        sorted_variants = sorted(llm_variants[llm_norm].items(), key=lambda x: x[1], reverse=True)
                        for variant, count in sorted_variants:
                            percentage = (count / total_prompts) * 100
                            st.write(f"  • `{variant}`: {count} ({percentage:.1f}%)")
                        st.markdown("---")
            
            # Grafico 3: Tasso di Errore
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
            
            # Impatto Validazioni Manuali
            with st.expander("✏️ Impatto delle Validazioni Manuali", expanded=False):
                st.markdown("#### 📊 Come le validazioni manuali hanno modificato i risultati")
                
                if len(manual_validations) > 0:
                    # Conta le diverse categorie
                    confirmed = (final_df['Manually_Validated'] == 'Confirmed_Student').sum()
                    corrected = (final_df['Manually_Validated'] == 'Manually_Corrected').sum()
                    partial = (final_df['Manually_Validated'] == 'Partially_Correct').sum()
                    algo_only = (final_df['Manually_Validated'] == 'Algorithm_Only').sum()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("✅ Studente Confermato", confirmed, help="Casi dubbi dove lo studente aveva ragione")
                    with col2:
                        st.metric("❌ Totalmente Errato", corrected, help="Casi dubbi corretti completamente")
                    with col3:
                        st.metric("⚠️ Parzialmente Corretto", partial, help="Studente parzialmente corretto")
                    with col4:
                        st.metric("🤖 Solo Algoritmo", algo_only, help="Non validati manualmente")
                    
                    # Distribuzione
                    validation_dist = pd.DataFrame({
                        'Tipo Validazione': ['Studente Confermato', 'Completamente Errato', 'Parziale', 'Solo Algoritmo'],
                        'Conteggio': [confirmed, corrected, partial, algo_only],
                        'Percentuale': [
                            f"{confirmed/len(final_df)*100:.1f}%",
                            f"{corrected/len(final_df)*100:.1f}%",
                            f"{partial/len(final_df)*100:.1f}%",
                            f"{algo_only/len(final_df)*100:.1f}%"
                        ]
                    })
                    st.dataframe(validation_dist, use_container_width=True, hide_index=True)
                else:
                    st.info("🤖 Nessuna validazione manuale effettuata. Tutti i risultati sono stati determinati dall'algoritmo.")
            
            # Statistica 1: Analisi per Modello LLM
            with st.expander("🤖 Analisi Dettagliata per Modello LLM", expanded=False):
                st.markdown("#### 📈 Prestazioni per Modello LLM")
                st.caption("Quali LLM hanno prodotto le classificazioni più corrette (basato sui risultati finali)")
                
                # Raggruppa per LLM
                llm_stats = []
                for llm in final_df['LLM_Used'].unique():
                    llm_df = final_df[final_df['LLM_Used'] == llm]
                    total_prompts = len(llm_df)
                    
                    # Calcola errori (match_type = 'error')
                    errors = (llm_df['Match_Type'] == 'error').sum()
                    error_rate = (errors / total_prompts * 100) if total_prompts > 0 else 0
                    
                    # Tecnica più usata (escludi etichette manuali segnaposto)
                    llm_df_filtered = llm_df[llm_df['Final_Classification'] != '[ETICHETTA_MANUALE]']
                    most_common_technique = llm_df_filtered['Final_Classification'].mode()[0] if len(llm_df_filtered) > 0 else 'N/A'
                    
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
            
            # Statistica 2: Analisi per Tecnica di Prompting (risultati corretti)
            with st.expander("🎯 Tecniche di Prompting Utilizzate (Risultati Corretti)", expanded=False):
                st.markdown("#### 📊 Quali Tecniche Sono State Realmente Utilizzate")
                st.caption("Basato sulle classificazioni finali corrette (post-validazione)")
                
                # Raggruppa per tecnica FINALE (corretta)
                technique_stats = []
                for technique in final_df['Final_Classification'].unique():
                    tech_df = final_df[final_df['Final_Classification'] == technique]
                    total_prompts = len(tech_df)
                    
                    # Studenti che l'hanno indovinata
                    correctly_guessed = (tech_df['Match_Type'] == 'exact').sum()
                    guess_rate = (correctly_guessed / total_prompts * 100) if total_prompts > 0 else 0
                    
                    # LLM più usato per questa tecnica
                    most_common_llm = tech_df['LLM_Used'].mode()[0] if len(tech_df) > 0 else 'N/A'
                    
                    # App più comune
                    most_common_app = tech_df['Application'].mode()[0] if len(tech_df) > 0 else 'N/A'
                    
                    technique_stats.append({
                        'Tecnica (Corretta)': technique,
                        'Utilizzi Totali': total_prompts,
                        '% sul Totale': f"{(total_prompts/len(final_df)*100):.1f}%",
                        "Studenti che l'hanno Indovinata": correctly_guessed,
                        '% Indovinata': f"{guess_rate:.1f}%",
                        'LLM Principale': most_common_llm,
                        'App Principale': most_common_app
                    })
                
                technique_stats_df = pd.DataFrame(technique_stats).sort_values('Utilizzi Totali', ascending=False)
                st.dataframe(technique_stats_df, use_container_width=True, hide_index=True)
                
                # Grafico tecniche più usate
                fig_tech = px.bar(
                    technique_stats_df.head(10),
                    x='Tecnica (Corretta)',
                    y='Utilizzi Totali',
                    title='TOP 10 Tecniche Più Utilizzate (Risultati Corretti)',
                    color='% Indovinata',
                    color_continuous_scale='RdYlGn',
                    text='Utilizzi Totali'
                )
                fig_tech.update_traces(textposition='outside')
                fig_tech.update_layout(height=500, xaxis_tickangle=-45)
                st.plotly_chart(fig_tech, use_container_width=True)
                
                # Download CSV statistiche tecniche
                csv_tech = technique_stats_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Scarica Statistiche Tecniche (CSV)",
                    data=csv_tech,
                    file_name="statistiche_tecniche_corrette.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Statistica 3: Confusioni Più Comuni
            with st.expander("🔀 Confusioni Più Comuni degli Studenti", expanded=False):
                st.markdown("#### 🎭 Quali tecniche vengono confuse tra loro?")
                st.caption("Analisi delle confusioni più frequenti: cosa hanno scritto gli studenti quando era sbagliato")
                
                # Filtra solo errori
                errors_only = final_df[final_df['Match_Type'] == 'error'].copy()
                
                if len(errors_only) > 0:
                    # Conta le confusioni
                    confusion_counts = errors_only.groupby(['Student_Classification', 'Final_Classification']).size().reset_index(name='Frequenza')
                    confusion_counts.columns = ['Hanno Scritto (ERRORE)', 'Era In Realtà', 'Volte Confuse']
                    confusion_counts = confusion_counts.sort_values('Volte Confuse', ascending=False)
                    
                    st.markdown("##### 🔝 TOP 15 Confusioni Più Frequenti")
                    st.dataframe(confusion_counts.head(15), use_container_width=True, hide_index=True)
                    
                    # Heatmap delle confusioni più comuni
                    top_wrong = errors_only['Student_Classification'].value_counts().head(5).index.tolist()
                    top_correct = errors_only['Final_Classification'].value_counts().head(5).index.tolist()
                    
                    # Crea matrice per heatmap
                    heatmap_data = []
                    for wrong in top_wrong:
                        row_data = []
                        for correct in top_correct:
                            count = len(errors_only[(errors_only['Student_Classification'] == wrong) & 
                                                    (errors_only['Final_Classification'] == correct)])
                            row_data.append(count)
                        heatmap_data.append(row_data)
                    
                    fig_heat = go.Figure(data=go.Heatmap(
                        z=heatmap_data,
                        x=[f"Era:<br>{t[:20]}" for t in top_correct],
                        y=[f"Scritto:<br>{t[:20]}" for t in top_wrong],
                        colorscale='Reds',
                        text=heatmap_data,
                        texttemplate='%{text}',
                        textfont={"size":12}
                    ))
                    fig_heat.update_layout(
                        title='Heatmap delle Confusioni (TOP 5x5)',
                        xaxis_title='Classificazione Corretta',
                        yaxis_title='Classificazione Errata (Studente)',
                        height=500
                    )
                    st.plotly_chart(fig_heat, use_container_width=True)
                    
                    # Download confusioni
                    csv_confusion = confusion_counts.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Scarica Analisi Completa Confusioni (CSV)",
                        data=csv_confusion,
                        file_name="confusioni_studenti.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.success("🎉 Nessuna confusione rilevata! Gli studenti hanno classificato tutto correttamente.")
            
            st.markdown("---")
            
            # Analisi Errori Studenti
            with st.expander("❌ TOP Errori degli Studenti", expanded=True):
                st.markdown("#### 🔍 Quali tecniche hanno sbagliato di più?")
                st.caption("Analisi degli errori più comuni commessi dagli studenti nelle classificazioni")
                
                # Filtra solo gli errori
                errors_df = final_df[final_df['Match_Type'] == 'error'].copy()
                
                if len(errors_df) > 0:
                    # TOP errori: cosa hanno scritto vs cosa era corretto
                    error_analysis = []
                    for idx, row in errors_df.iterrows():
                        error_analysis.append({
                            'Applicazione': row['Application'],
                            'LLM Usato': row['LLM_Used'],
                            'Classificazione Errata (Studente)': row['Student_Classification'],
                            '→ Classificazione Corretta': row['Final_Classification'],
                            'Confidenza Algoritmo': f"{row['Confidence']:.0f}%"
                        })
                    
                    error_df = pd.DataFrame(error_analysis)
                    
                    # Mostra statistiche errori
                    st.metric("Totale Errori Rilevati", len(errors_df), delta=f"{len(errors_df)/len(final_df)*100:.1f}% del totale")
                    
                    # TOP 10 errori più comuni
                    st.markdown("##### 🎯 TOP 10 Errori Più Comuni")
                    error_counts = error_df.groupby(['Classificazione Errata (Studente)', '→ Classificazione Corretta']).size().reset_index(name='Frequenza')
                    error_counts = error_counts.sort_values('Frequenza', ascending=False).head(10)
                    st.dataframe(error_counts, use_container_width=True, hide_index=True)
                    
                    # Tecnica più sbagliata
                    st.markdown("##### ⚠️ Tecniche Più Sbagliate dagli Studenti")
                    wrong_tech_counts = errors_df['Student_Classification'].value_counts().head(5)
                    wrong_tech_df = pd.DataFrame({
                        'Tecnica Sbagliata': wrong_tech_counts.index,
                        'Volte Sbagliata': wrong_tech_counts.values,
                        '% sugli Errori': (wrong_tech_counts.values / len(errors_df) * 100).round(1)
                    })
                    st.dataframe(wrong_tech_df, use_container_width=True, hide_index=True)
                    
                    # Download errori
                    csv_errors = error_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Scarica Lista Completa Errori (CSV)",
                        data=csv_errors,
                        file_name="analisi_errori_studenti.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.success("🎉 Nessun errore rilevato! Tutti gli studenti hanno classificato correttamente.")
            
            # Analisi per Applicazione
            with st.expander("📱 Prestazioni per Applicazione", expanded=False):
                st.markdown("#### 📊 Confronto tra le 3 Applicazioni")
                st.caption("Come si sono comportati gli studenti su ciascuna classe da testare")
                
                app_stats = []
                for app in final_df['Application'].unique():
                    app_df = final_df[final_df['Application'] == app]
                    total = len(app_df)
                    errors = (app_df['Match_Type'] == 'error').sum()
                    exact = (app_df['Match_Type'] == 'exact').sum()
                    
                    # Tecnica più usata (escludi etichette manuali segnaposto)
                    app_df_filtered = app_df[app_df['Final_Classification'] != '[ETICHETTA_MANUALE]']
                    top_tech = app_df_filtered['Final_Classification'].mode()[0] if len(app_df_filtered) > 0 else 'N/A'
                    
                    # LLM più usato
                    top_llm = app_df['LLM_Used'].mode()[0] if len(app_df) > 0 else 'N/A'
                    
                    app_stats.append({
                        'Applicazione': app,
                        'Tot. Prompt': total,
                        'Match Esatti': exact,
                        '% Corrette': f"{(exact/total*100):.1f}%",
                        'Errori': errors,
                        '% Errori': f"{(errors/total*100):.1f}%",
                        'Tecnica Prevalente': top_tech,
                        'LLM Prevalente': top_llm
                    })
                
                app_stats_df = pd.DataFrame(app_stats)
                st.dataframe(app_stats_df, use_container_width=True, hide_index=True)
                
                # Grafico prestazioni per app
                fig_app = go.Figure()
                fig_app.add_trace(go.Bar(
                    name='Match Esatti',
                    x=app_stats_df['Applicazione'],
                    y=[float(x.replace('%', '')) for x in app_stats_df['% Corrette']],
                    marker_color='green'
                ))
                fig_app.add_trace(go.Bar(
                    name='Errori',
                    x=app_stats_df['Applicazione'],
                    y=[float(x.replace('%', '')) for x in app_stats_df['% Errori']],
                    marker_color='red'
                ))
                fig_app.update_layout(
                    title='Percentuale Match Esatti vs Errori per Applicazione',
                    yaxis_title='Percentuale (%)',
                    barmode='group',
                    height=400
                )
                st.plotly_chart(fig_app, use_container_width=True)
            
            # Tabella Finale Completa (SENZA testo prompt)
            with st.expander("📋 Visualizza Tabella Completa Risultati Finali", expanded=False):
                st.warning("⚠️ Nota: I testi dei prompt sono stati rimossi da questa visualizzazione per privacy e leggibilità")
                display_cols = [
                    'Application', 'LLM_Used',
                    'Student_Classification', 'Final_Classification',
                    'Confidence', 'Match_Type', 'Manually_Validated'
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
                    llm_df_filtered = llm_df[llm_df['Final_Classification'] != '[ETICHETTA_MANUALE]']
                    most_common_technique = llm_df_filtered['Final_Classification'].mode()[0] if len(llm_df_filtered) > 0 else 'N/A'
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
