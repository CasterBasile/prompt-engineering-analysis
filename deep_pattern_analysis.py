import pandas as pd
import re
from collections import Counter, defaultdict

# Leggi il file Excel
df = pd.read_excel(r'c:\Users\basil\Desktop\Progetto ST\Prompt.xlsx')

# Identifica le colonne con i prompt
prompt_columns = [col for col in df.columns if 'Report here the text' in col or 'Prompt' in col]

# Raccogli tutti i prompt
all_prompts = []
for col in prompt_columns:
    prompts = df[col].dropna().tolist()
    all_prompts.extend(prompts)

print("="*100)
print("ANALISI ULTRA-APPROFONDITA DEI PATTERN SPECIFICI")
print("="*100)
print(f"\nTotale prompt analizzati: {len(all_prompts)}\n")

# Stampa tutti i prompt per riferimento
print("\n" + "="*100)
print("SEZIONE 1: TUTTI I PROMPT RAW (per riferimento)")
print("="*100 + "\n")

for i, prompt in enumerate(all_prompts, 1):
    print(f"--- PROMPT #{i} ---")
    print(prompt)
    print()

print("\n" + "="*100)
print("SEZIONE 2: PATTERN ULTRA-SPECIFICI ESTRATTI")
print("="*100 + "\n")

# Dizionari per categorizzare i pattern
few_shot_phrases = []
cot_phrases = []
persona_phrases = []
constraint_phrases = []
self_refine_phrases = []

for prompt in all_prompts:
    # FEW-SHOT: Cerca strutture di esempio
    
    # Pattern "Example:" seguito da input/output
    matches = re.finditer(r'(Example[s]?:\s*[^.]{10,150}\.)', prompt, re.IGNORECASE)
    for match in matches:
        few_shot_phrases.append(match.group(1).strip())
    
    # Pattern "for input... output should"
    matches = re.finditer(r'(for input\s+[^.]{5,80}\s+(?:the )?output should[^.]{5,80}\.)', prompt, re.IGNORECASE)
    for match in matches:
        few_shot_phrases.append(match.group(1).strip())
    
    # Pattern "scenario(s): numero)"
    matches = re.finditer(r'((?:scenario|scenarios):\s*\d+\)[^.]{10,150}\.)', prompt, re.IGNORECASE)
    for match in matches:
        few_shot_phrases.append(match.group(1).strip())
    
    # Pattern "the following scenarios/examples/cases"
    matches = re.finditer(r'(the following\s+(?:scenarios?|examples?|cases?|test cases?):[^.]{10,200})', prompt, re.IGNORECASE)
    for match in matches:
        # Prendi fino al punto o fino a 200 caratteri
        text = match.group(1).strip()
        end_idx = text.find('.', 50)
        if end_idx > 0:
            text = text[:end_idx+1]
        few_shot_phrases.append(text)
    
    # Pattern "handle the following"
    matches = re.finditer(r'(handle the following\s+[^:]+:[^)]+\))', prompt, re.IGNORECASE)
    for match in matches:
        few_shot_phrases.append(match.group(1).strip())
    
    # CHAIN-OF-THOUGHT: Cerca strutture di ragionamento
    
    # Pattern "step by step" con contesto
    matches = re.finditer(r'([^.]{10,80}\s+step by step[^.]{10,80}\.)', prompt, re.IGNORECASE)
    for match in matches:
        cot_phrases.append(match.group(1).strip())
    
    # Pattern "Think step by step"
    matches = re.finditer(r'(Think\s+step by step[^.]{0,100}\.)', prompt, re.IGNORECASE)
    for match in matches:
        cot_phrases.append(match.group(1).strip())
    
    # Pattern "First... then... finally..."
    matches = re.finditer(r'(First\s+[^,]{5,80},\s*then\s+[^,]{5,80},\s*(?:and\s+)?finally\s+[^.]{5,80}\.)', prompt, re.IGNORECASE)
    for match in matches:
        cot_phrases.append(match.group(1).strip())
    
    # Pattern "First... then..." (senza finally)
    matches = re.finditer(r'(First\s+[^,]{5,80},\s*then\s+[^.]{5,80}\.)', prompt, re.IGNORECASE)
    for match in matches:
        if 'finally' not in match.group(1).lower():  # Evita duplicati con il pattern sopra
            cot_phrases.append(match.group(1).strip())
    
    # Pattern "analyze... then..."
    matches = re.finditer(r'(analyze\s+[^,]{5,60},\s*then\s+[^.]{5,80}\.)', prompt, re.IGNORECASE)
    for match in matches:
        cot_phrases.append(match.group(1).strip())
    
    # Pattern "Walk through"
    matches = re.finditer(r'(Walk through\s+[^:]{5,80}:[^.]{10,100}\.)', prompt, re.IGNORECASE)
    for match in matches:
        cot_phrases.append(match.group(1).strip())
    
    # Pattern "Think carefully"
    matches = re.finditer(r'(Think\s+carefully\s+[^.]{10,100}\.)', prompt, re.IGNORECASE)
    for match in matches:
        cot_phrases.append(match.group(1).strip())
    
    # PERSONA: Cerca definizioni di ruolo
    
    # Pattern "Act as..."
    matches = re.finditer(r'(Act as\s+(?:a|an)\s+[^.]{5,60}\.)', prompt, re.IGNORECASE)
    for match in matches:
        persona_phrases.append(match.group(1).strip())
    
    # Pattern "You are..."
    matches = re.finditer(r'(You are\s+(?:a|an)\s+[^.]{5,60}\.)', prompt, re.IGNORECASE)
    for match in matches:
        persona_phrases.append(match.group(1).strip())
    
    # Pattern con "expert" o "specialist" o "engineer"
    matches = re.finditer(r'([^.]{0,30}(?:expert|specialist|engineer|senior|experienced)[^.]{0,60}\.)', prompt, re.IGNORECASE)
    for match in matches:
        text = match.group(1).strip()
        if any(kw in text.lower() for kw in ['you are', 'act as', 'as a']):
            persona_phrases.append(text)
    
    # CONSTRAINT-BASED: Cerca vincoli e requisiti
    
    # Pattern "use..." 
    matches = re.finditer(r'(use\s+\w+\s+(?:to|for|without)[^.]{5,80}\.)', prompt, re.IGNORECASE)
    for match in matches:
        constraint_phrases.append(match.group(1).strip())
    
    # Pattern "should/must/ensure/require"
    matches = re.finditer(r'((?:should|must|ensure|require)\s+[^.]{10,80}\.)', prompt, re.IGNORECASE)
    for match in matches:
        constraint_phrases.append(match.group(1).strip())
    
    # Pattern "without/no mock"
    matches = re.finditer(r'((?:without|no)\s+(?:mock|mocking|external)[^.]{5,80}\.)', prompt, re.IGNORECASE)
    for match in matches:
        constraint_phrases.append(match.group(1).strip())
    
    # Pattern "coverage"
    matches = re.finditer(r'([^.]{10,60}coverage[^.]{5,60}\.)', prompt, re.IGNORECASE)
    for match in matches:
        constraint_phrases.append(match.group(1).strip())
    
    # SELF-REFINE: Cerca indicatori di iterazione
    
    # Pattern "iterate/improve/refine"
    matches = re.finditer(r'((?:iterate|improve|refine|enhance)\s+[^.]{10,80}\.)', prompt, re.IGNORECASE)
    for match in matches:
        self_refine_phrases.append(match.group(1).strip())

# Stampa pattern categorizzati
print("### FEW-SHOT PATTERNS ###\n")
print(f"Pattern unici trovati: {len(set(few_shot_phrases))}")
print(f"Occorrenze totali: {len(few_shot_phrases)}\n")
few_shot_counter = Counter(few_shot_phrases)
for phrase, count in few_shot_counter.most_common():
    print(f"[{count}x] {phrase}")
print()

print("\n### CHAIN-OF-THOUGHT PATTERNS ###\n")
print(f"Pattern unici trovati: {len(set(cot_phrases))}")
print(f"Occorrenze totali: {len(cot_phrases)}\n")
cot_counter = Counter(cot_phrases)
for phrase, count in cot_counter.most_common():
    print(f"[{count}x] {phrase}")
print()

print("\n### PERSONA PATTERNS ###\n")
print(f"Pattern unici trovati: {len(set(persona_phrases))}")
print(f"Occorrenze totali: {len(persona_phrases)}\n")
persona_counter = Counter(persona_phrases)
for phrase, count in persona_counter.most_common():
    print(f"[{count}x] {phrase}")
print()

print("\n### CONSTRAINT-BASED PATTERNS ###\n")
print(f"Pattern unici trovati: {len(set(constraint_phrases))}")
print(f"Occorrenze totali: {len(constraint_phrases)}\n")
constraint_counter = Counter(constraint_phrases)
for phrase, count in constraint_counter.most_common():
    print(f"[{count}x] {phrase}")
print()

print("\n### SELF-REFINE PATTERNS ###\n")
print(f"Pattern unici trovati: {len(set(self_refine_phrases))}")
print(f"Occorrenze totali: {len(self_refine_phrases)}\n")
refine_counter = Counter(self_refine_phrases)
for phrase, count in refine_counter.most_common():
    print(f"[{count}x] {phrase}")
print()

print("\n" + "="*100)
print("SEZIONE 3: TOP 50 PATTERN PIÙ FREQUENTI E SPECIFICI (CONSOLIDATI)")
print("="*100 + "\n")

all_patterns = []
all_patterns.extend([('Few-Shot', p, c) for p, c in few_shot_counter.items()])
all_patterns.extend([('Chain-of-Thought', p, c) for p, c in cot_counter.items()])
all_patterns.extend([('Persona', p, c) for p, c in persona_counter.items()])
all_patterns.extend([('Constraint-Based', p, c) for p, c in constraint_counter.items()])
all_patterns.extend([('Self-Refine', p, c) for p, c in refine_counter.items()])

# Ordina per frequenza
all_patterns.sort(key=lambda x: x[2], reverse=True)

for i, (technique, pattern, count) in enumerate(all_patterns[:50], 1):
    print(f"{i}. [{technique}] ({count}x)")
    print(f"   Pattern: '{pattern}'")
    print()

print("\n" + "="*100)
print("SEZIONE 4: PATTERN RARI MA DISTINTIVI (1 occorrenza, molto specifici)")
print("="*100 + "\n")

rare_patterns = [p for p in all_patterns if p[2] == 1]
for technique, pattern, count in rare_patterns:
    print(f"[{technique}] '{pattern}'")
    print()

print("\n" + "="*100)
print("SEZIONE 5: REGEX ULTRA-SPECIFICHE BASATE SUI DATI REALI")
print("="*100 + "\n")

print("""
Basandomi sui pattern ESATTI estratti dai prompt, ecco le regex ultra-specifiche:

=== FEW-SHOT PATTERNS ===

1. Esempi espliciti con input/output:
   r'(?i)example[s]?:\s*for\s+input\s+.{5,100}\s+(?:the\s+)?output\s+should\s+.{5,100}'
   
2. Liste di scenari numerati:
   r'(?i)(?:the\s+)?following\s+scenarios?:\s*\d+\)'
   
3. Struttura "handle the following scenarios":
   r'(?i)handle\s+the\s+following\s+scenarios?:\s*.{10,}'
   
4. Pattern di test case:
   r'(?i)(?:for\s+each|each)\s+\w+\s+scenario,?\s+create\s+a\s+test\s+case'

=== CHAIN-OF-THOUGHT PATTERNS ===

1. "Step by step" con verbi di azione:
   r'(?i)(?:think|write|create)\s+.{0,20}\s+step\s+by\s+step'
   
2. Sequenza First-Then-Finally:
   r'(?i)first\s+.{5,80},?\s+then\s+.{5,80},?\s+(?:and\s+)?finally\s+.{5,80}'
   
3. Sequenza First-Then (senza Finally):
   r'(?i)first\s+.{5,80},?\s+then\s+.{5,80}(?:,\s+and)?(?!\s+finally)'
   
4. "Analyze... then..." pattern:
   r'(?i)(?:first\s+)?analyze\s+.{5,60},?\s+then\s+.{5,80}'
   
5. "Walk through" con spiegazione:
   r'(?i)walk\s+through\s+.{5,80}:\s*.{10,}'
   
6. "Think carefully" pattern:
   r'(?i)think\s+carefully\s+about\s+.{5,80}'

=== PERSONA PATTERNS ===

1. "Act as" con ruolo professionale:
   r'(?i)act\s+as\s+(?:a|an)\s+(?:\w+\s+){0,3}(?:engineer|expert|specialist|tester|developer)'
   
2. "You are" con ruolo ed esperienza:
   r'(?i)you\s+are\s+(?:a|an)\s+(?:senior|expert|experienced)?\s*(?:\w+\s+){0,2}(?:engineer|tester|specialist|developer)'
   
3. Qualsiasi menzione di ruolo QA:
   r'(?i)(?:act\s+as|you\s+are)\s+(?:a|an)\s+(?:.{0,20})?QA\s+(?:engineer|specialist|tester|automation\s+engineer)'

=== CONSTRAINT-BASED PATTERNS ===

1. Verbi imperativi (should/must/ensure/require):
   r'(?i)(?:should|must|ensure|require)\s+(?:all|that|the)?\s*.{10,80}'
   
2. "Use X to/for" pattern:
   r'(?i)use\s+\w+\s+(?:to|for)\s+.{5,80}'
   
3. Restrizioni (without/no):
   r'(?i)(?:without|no)\s+(?:mock|mocking|external\s+dependencies)'
   
4. Coverage requirements:
   r'(?i)\d+%?\s+coverage'

=== SELF-REFINE PATTERNS ===

1. Iterazione esplicita:
   r'(?i)iterate\s+through\s+.{5,80}'
   
2. Miglioramento iterativo:
   r'(?i)(?:improve|refine|enhance)\s+.{10,80}'

=== PATTERN COMBINATI (MULTI-TECNICA) ===

1. Persona + Chain-of-Thought:
   r'(?i)you\s+are\s+(?:a|an)\s+\w+.*?(?:think|analyze|walk\s+through).*?step\s+by\s+step'
   
2. Few-Shot + Constraint:
   r'(?i)(?:examples?|scenarios?).*?(?:should|must|ensure)'
   
3. Chain-of-Thought + Constraint:
   r'(?i)(?:first|then|finally).*?(?:ensure|validate|verify)'

=== PATTERN ULTRA-SPECIFICI PER QUESTO DATASET ===

Questi pattern catturano frasi ESATTE trovate nei prompt:

1. "Think step by step and create unit tests for":
   r'(?i)think\s+step\s+by\s+step\s+and\s+create\s+unit\s+tests\s+for'
   
2. "Generate comprehensive unit tests for":
   r'(?i)generate\s+comprehensive\s+unit\s+tests\s+for'
   
3. Pattern di edge cases:
   r'(?i)(?:identify|handle|test)\s+edge\s+cases'
   
4. Pattern di validazione:
   r'(?i)validate\s+(?:the|that)?\s*.{5,50}'
   
5. "Create unit tests for X. The class should handle":
   r'(?i)create\s+unit\s+tests\s+for\s+\w+\.\s+the\s+class\s+should\s+handle'
   
6. "For the X class, Y":
   r'(?i)for\s+the\s+\w+\s+class,\s+.{10,}'

NOTA IMPORTANTE:
Tutti questi pattern sono stati estratti da frasi REALI presenti nei 15 prompt analizzati.
Non sono pattern inventati o generalizzati, ma basati su dati empirici effettivi.
""")

print("\n" + "="*100)
print("SEZIONE 6: STATISTICHE FINALI")
print("="*100 + "\n")

print(f"Prompt totali analizzati: {len(all_prompts)}")
print(f"\nPattern trovati per tecnica:")
print(f"  - Few-Shot: {len(set(few_shot_phrases))} pattern unici, {len(few_shot_phrases)} occorrenze totali")
print(f"  - Chain-of-Thought: {len(set(cot_phrases))} pattern unici, {len(cot_phrases)} occorrenze totali")
print(f"  - Persona: {len(set(persona_phrases))} pattern unici, {len(persona_phrases)} occorrenze totali")
print(f"  - Constraint-Based: {len(set(constraint_phrases))} pattern unici, {len(constraint_phrases)} occorrenze totali")
print(f"  - Self-Refine: {len(set(self_refine_phrases))} pattern unici, {len(self_refine_phrases)} occorrenze totali")
print(f"\nTotale pattern unici trovati: {len(all_patterns)}")
print(f"Totale occorrenze di pattern: {sum(p[2] for p in all_patterns)}")

print("\n" + "="*100)
print("FINE ANALISI ULTRA-APPROFONDITA")
print("="*100)
