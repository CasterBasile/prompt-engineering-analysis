import pandas as pd
import re
from collections import Counter, defaultdict

# Leggi il file Excel
df = pd.read_excel(r'c:\Users\basil\Desktop\Progetto ST\Prompt.xlsx')

# Identifica le colonne con i prompt
prompt_columns = [col for col in df.columns if 'Report here the text' in col or 'Prompt' in col]
print(f"Colonne con prompt trovate: {len(prompt_columns)}")
print(f"Colonne: {prompt_columns}\n")

# Raccogli tutti i prompt
all_prompts = []
for col in prompt_columns:
    prompts = df[col].dropna().tolist()
    all_prompts.extend(prompts)

print(f"Numero totale di prompt: {len(all_prompts)}\n")

# Dizionario per memorizzare pattern e loro occorrenze
pattern_data = defaultdict(lambda: {'count': 0, 'examples': [], 'technique': None})

# Pattern specifici da cercare
patterns_to_find = {
    # Few-Shot patterns
    'example:': 'Few-Shot',
    'for example': 'Few-Shot',
    'such as': 'Few-Shot',
    'e.g.': 'Few-Shot',
    'for input': 'Few-Shot',
    'the output should': 'Few-Shot',
    'test case': 'Few-Shot',
    'test cases': 'Few-Shot',
    'scenario': 'Few-Shot',
    'scenarios': 'Few-Shot',
    'the following': 'Few-Shot',
    
    # Chain-of-Thought patterns
    'step by step': 'Chain-of-Thought',
    'think step by step': 'Chain-of-Thought',
    'passo dopo passo': 'Chain-of-Thought',
    'first': 'Chain-of-Thought',
    'then': 'Chain-of-Thought',
    'finally': 'Chain-of-Thought',
    'walk through': 'Chain-of-Thought',
    'let\'s think': 'Chain-of-Thought',
    'think carefully': 'Chain-of-Thought',
    'analyze': 'Chain-of-Thought',
    
    # Persona/Role patterns
    'act as': 'Persona',
    'you are': 'Persona',
    'agisci come': 'Persona',
    'you are a': 'Persona',
    'you are an': 'Persona',
    'as a': 'Persona',
    'expert': 'Persona',
    'senior': 'Persona',
    'specialist': 'Persona',
    'engineer': 'Persona',
    
    # Constraint-Based patterns
    'use junit': 'Constraint-Based',
    'using junit': 'Constraint-Based',
    'without mock': 'Constraint-Based',
    'no mock': 'Constraint-Based',
    'coverage': 'Constraint-Based',
    'must': 'Constraint-Based',
    'should': 'Constraint-Based',
    'ensure': 'Constraint-Based',
    'require': 'Constraint-Based',
    
    # Self-Refine patterns
    'iterate': 'Self-Refine',
    'improve': 'Self-Refine',
    'refine': 'Self-Refine',
    'feedback': 'Self-Refine',
    'enhance': 'Self-Refine',
}

# Estrai N-grammi (frasi) dai prompt
def extract_ngrams(text, n=3):
    """Estrae n-grammi di parole dal testo"""
    words = re.findall(r'\b\w+\b', text.lower())
    ngrams = []
    for i in range(len(words) - n + 1):
        ngrams.append(' '.join(words[i:i+n]))
    return ngrams

# Raccogli tutti gli n-grammi
all_bigrams = Counter()
all_trigrams = Counter()
all_4grams = Counter()
all_5grams = Counter()

for prompt in all_prompts:
    prompt_lower = prompt.lower()
    
    # Cerca pattern predefiniti
    for pattern, technique in patterns_to_find.items():
        if pattern.lower() in prompt_lower:
            pattern_data[pattern]['count'] += 1
            pattern_data[pattern]['technique'] = technique
            if len(pattern_data[pattern]['examples']) < 2:
                # Estrai il contesto intorno al pattern
                idx = prompt_lower.find(pattern.lower())
                context_start = max(0, idx - 30)
                context_end = min(len(prompt), idx + len(pattern) + 30)
                context = prompt[context_start:context_end].strip()
                pattern_data[pattern]['examples'].append(context)
    
    # Estrai n-grammi
    words = re.findall(r'\b\w+\b', prompt.lower())
    for i in range(len(words) - 1):
        all_bigrams[' '.join(words[i:i+2])] += 1
    for i in range(len(words) - 2):
        all_trigrams[' '.join(words[i:i+3])] += 1
    for i in range(len(words) - 3):
        all_4grams[' '.join(words[i:i+4])] += 1
    for i in range(len(words) - 4):
        all_5grams[' '.join(words[i:i+5])] += 1

print("="*80)
print("REPORT ANALISI PATTERN NEI PROMPT")
print("="*80)

# Stampa pattern trovati ordinati per frequenza
print("\n1. PATTERN PREDEFINITI TROVATI (ordinati per frequenza):\n")
sorted_patterns = sorted(pattern_data.items(), key=lambda x: x[1]['count'], reverse=True)

for pattern, data in sorted_patterns:
    if data['count'] > 0:
        print(f"Pattern: '{pattern}'")
        print(f"  - Tecnica: {data['technique']}")
        print(f"  - Occorrenze: {data['count']}")
        print(f"  - Esempi di contesto:")
        for ex in data['examples']:
            print(f"    * ...{ex}...")
        print()

# Trova i bigram più comuni (esclusi quelli troppo generici)
print("\n2. TOP 30 BIGRAM PIÙ FREQUENTI:\n")
stopwords = {'of', 'the', 'to', 'for', 'in', 'and', 'a', 'is', 'that', 'it', 'on', 'with', 'as', 'be', 'at', 'by', 'this', 'from', 'or', 'an', 'are'}
filtered_bigrams = [(bg, count) for bg, count in all_bigrams.most_common(100) 
                    if count > 1 and not all(word in stopwords for word in bg.split())]
for bigram, count in filtered_bigrams[:30]:
    print(f"  '{bigram}': {count} volte")

# Trova i trigram più comuni
print("\n3. TOP 30 TRIGRAM PIÙ FREQUENTI:\n")
filtered_trigrams = [(tg, count) for tg, count in all_trigrams.most_common(100) 
                     if count > 1]
for trigram, count in filtered_trigrams[:30]:
    print(f"  '{trigram}': {count} volte")

# Trova i 4-gram più comuni
print("\n4. TOP 20 4-GRAM PIÙ FREQUENTI:\n")
filtered_4grams = [(fg, count) for fg, count in all_4grams.most_common(50) 
                   if count > 1]
for fourgram, count in filtered_4grams[:20]:
    print(f"  '{fourgram}': {count} volte")

# Cerca frasi complete specifiche
print("\n5. FRASI COMPLETE SPECIFICHE TROVATE:\n")

specific_phrases = []
for prompt in all_prompts:
    # Cerca frasi con "act as"
    matches = re.finditer(r'(act as [a-zA-Z\s]+[.\n])', prompt, re.IGNORECASE)
    for match in matches:
        specific_phrases.append(('Persona - Act as', match.group(1).strip()))
    
    # Cerca frasi con "you are"
    matches = re.finditer(r'(you are (?:a|an) [a-zA-Z\s]+[.\n])', prompt, re.IGNORECASE)
    for match in matches:
        specific_phrases.append(('Persona - You are', match.group(1).strip()))
    
    # Cerca frasi step-by-step
    matches = re.finditer(r'([^.]*step by step[^.]*\.)', prompt, re.IGNORECASE)
    for match in matches:
        specific_phrases.append(('Chain-of-Thought - Step by step', match.group(1).strip()))
    
    # Cerca frasi con "first... then... finally"
    matches = re.finditer(r'(first [^,]+, then [^,]+, (?:and )?finally [^.]+\.)', prompt, re.IGNORECASE)
    for match in matches:
        specific_phrases.append(('Chain-of-Thought - First/Then/Finally', match.group(1).strip()))
    
    # Cerca frasi con esempi
    matches = re.finditer(r'(example[s]?:[^.]+\.)', prompt, re.IGNORECASE)
    for match in matches:
        specific_phrases.append(('Few-Shot - Example', match.group(1).strip()))
    
    # Cerca frasi con "use junit" o constraint
    matches = re.finditer(r'(use [a-zA-Z0-9]+ (?:to|for)[^.]+\.)', prompt, re.IGNORECASE)
    for match in matches:
        specific_phrases.append(('Constraint - Use X', match.group(1).strip()))

phrase_counter = Counter(specific_phrases)
for (category, phrase), count in phrase_counter.most_common(30):
    print(f"[{category}] '{phrase}' - {count} volte")

print("\n6. ANALISI PER TECNICA:\n")

technique_patterns = defaultdict(list)
for pattern, data in pattern_data.items():
    if data['count'] > 0:
        technique_patterns[data['technique']].append((pattern, data['count']))

for technique, patterns in technique_patterns.items():
    print(f"\n{technique}:")
    sorted_patterns = sorted(patterns, key=lambda x: x[1], reverse=True)
    for pattern, count in sorted_patterns:
        print(f"  - '{pattern}': {count} occorrenze")

print("\n7. PATTERN RARI MA DISTINTIVI (occorrenza = 1-2):\n")
rare_patterns = [(p, d) for p, d in pattern_data.items() if 0 < d['count'] <= 2]
for pattern, data in rare_patterns:
    print(f"  '{pattern}' ({data['technique']}): {data['count']} volta/e")
    for ex in data['examples']:
        print(f"    Context: ...{ex}...")

print("\n8. SUGGERIMENTI PER REGEX ULTRA-SPECIFICHE:\n")

print("""
Basandomi sui pattern trovati, ecco le regex suggerite:

FEW-SHOT:
- r'\\b(?:example|for example|e\\.g\\.|for instance)\\b.*?(?:input|output|should|test case)'
- r'\\b(?:scenario|scenarios|test cases?)\\s*:\\s*\\d+'
- r'\\bthe following\\s+(?:scenarios?|examples?|cases?)'

CHAIN-OF-THOUGHT:
- r'\\b(?:step by step|passo dopo passo)\\b'
- r'\\b(?:first|then|finally|next|after that)\\b.*?\\bthen\\b'
- r'\\b(?:think|analyze|walk through)\\s+(?:carefully|step by step)'

PERSONA:
- r'\\b(?:act as|you are)\\s+(?:a|an)?\\s+\\w+(?:\\s+\\w+){0,3}\\s+(?:engineer|expert|specialist|developer)'
- r'\\byou are\\s+(?:a|an)\\s+(?:senior|junior|expert|experienced)'

CONSTRAINT-BASED:
- r'\\buse\\s+\\w+\\s+(?:to|for)'
- r'\\b(?:without|no)\\s+(?:mock|mocking)'
- r'\\b\\d+%\\s+coverage\\b'
- r'\\b(?:must|should|ensure|require)\\s+\\w+'

Queste regex catturano pattern reali trovati nei prompt.
""")

print("\n" + "="*80)
print("FINE REPORT")
print("="*80)
