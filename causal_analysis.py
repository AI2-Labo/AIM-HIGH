import os
import spacy
import openai

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Retrieve the OpenAI API Key from environment variable
openai.api_key = os.getenv('API_KEY')

# Check if the API key is successfully loaded
if openai.api_key is None:
    print("Error: API Key not found. Please check your environment variables.")
    exit()

# Common causal phrases
CAUSE_EFFECT_PHRASES = [
    "because", "due to", "as a result", "therefore", "since", "so", "because of", "consequently"
]

def preprocess_text(text):
    """Preprocess text and filter sentences with causal phrases."""
    doc = nlp(text)
    causal_sentences = [sent.text for sent in doc.sents if any(phrase in sent.text.lower() for phrase in CAUSE_EFFECT_PHRASES)]
    return causal_sentences

def extract_causal_pairs_rule_based(sentence):
    """Rule-based extraction of cause-effect pairs."""
    causal_pairs = []
    doc = nlp(sentence)
    for token in doc:
        if token.text.lower() in CAUSE_EFFECT_PHRASES:
            # Extract cause and effect based on dependency parsing
            cause = ""
            effect = ""
            for child in token.children:
                if child.dep_ in ["nsubj", "dobj", "attr"]:
                    if token.text.lower() in ["because", "since", "due to"]:
                        cause = child.text
                    else:
                        effect = child.text
            if cause and effect:
                causal_pairs.append((cause, effect))
    return causal_pairs

def extract_causal_pairs_gpt(text):
    """Use OpenAI GPT to extract cause-effect pairs from a paragraph."""
    prompt = f"Extract cause-effect relationships from the following text. Return in the format: Cause -> Effect.\nText: {text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI that extracts causal relationships from text."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.5
    )
    return response.choices[0].message['content'].strip()

def parse_gpt_output(gpt_output):
    """Parse GPT output into cause-effect pairs."""
    pairs = []
    for line in gpt_output.split("\n"):
        if "->" in line:
            cause, effect = line.split("->", 1)
            pairs.append((cause.strip(), effect.strip()))
    return pairs

def display_and_modify_results(causal_pairs):
    """Display results and allow user modification."""
    print("\nDetected Cause-Effect Pairs:")
    for idx, (cause, effect) in enumerate(causal_pairs, 1):
        print(f"{idx}. Cause: {cause}\n   Effect: {effect}")

    while True:
        modify_idx = input("\nEnter the number of the pair you'd like to modify, or 'done' to finish: ")
        if modify_idx.lower() == 'done':
            break
        try:
            modify_idx = int(modify_idx) - 1
            if modify_idx < 0 or modify_idx >= len(causal_pairs):
                print("Invalid index. Try again.")
                continue
            new_cause = input(f"Enter new cause (current: {causal_pairs[modify_idx][0]}): ")
            new_effect = input(f"Enter new effect (current: {causal_pairs[modify_idx][1]}): ")
            causal_pairs[modify_idx] = (new_cause, new_effect)
            print("Pair updated.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    print("\nFinal Cause-Effect Pairs:")
    for idx, (cause, effect) in enumerate(causal_pairs, 1):
        print(f"{idx}. Cause: {cause}\n   Effect: {effect}")

# Main function
def analyze_causal_relations():
    """Ask user for input and analyze causal relations."""
    text = input("Please enter the text for analysis: ")
    causal_sentences = preprocess_text(text)
    causal_pairs = []

    # Rule-based extraction for individual sentences
    for sentence in causal_sentences:
        rule_based_pairs = extract_causal_pairs_rule_based(sentence)
        if rule_based_pairs:
            causal_pairs.extend(rule_based_pairs)

    # GPT-based extraction for the entire paragraph
    gpt_output = extract_causal_pairs_gpt(text)
    gpt_pairs = parse_gpt_output(gpt_output)
    causal_pairs.extend(gpt_pairs)

    # Display and allow user modification
    display_and_modify_results(causal_pairs)

# Example usage
analyze_causal_relations()