import re
import heapq
import nltk
from collections import defaultdict
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
nltk.download('punkt_tab')  # Explicitly download 'punkt_tab'




# Download necessary resources
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("averaged_perceptron_tagger")


def preprocess_text(text):
    """Cleans and tokenizes text for processing."""
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces/newlines
    sentences = sent_tokenize(text)  # Split into sentences
    return sentences


def build_word_frequencies(sentences):
    """Creates a frequency table of words (ignoring stopwords)."""
    stop_words = set(stopwords.words("english"))
    word_frequencies = defaultdict(int)


    for sentence in sentences:
        words = word_tokenize(sentence.lower())  # Tokenize and convert to lowercase
        for word in words:
            if word not in stop_words and word.isalnum():  # Ignore stopwords and symbols
                word_frequencies[word] += 1


    # Normalize frequencies by dividing by max frequency
    max_freq = max(word_frequencies.values(), default=1)
    for word in word_frequencies:
        word_frequencies[word] /= max_freq


    return word_frequencies


def rank_sentences(sentences, word_frequencies):
    """Scores each sentence based on word frequency and ranks them."""
    sentence_scores = {}


    for sentence in sentences:
        words = word_tokenize(sentence.lower())
        score = sum(word_frequencies.get(word, 0) for word in words)
        sentence_scores[sentence] = score


    return sentence_scores


def extract_summary(sentences, sentence_scores, num_sentences=3):
    """Extracts the top-ranked sentences as the summary."""
    top_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    return " ".join(top_sentences)


def summarize_text_simple(text, summary_length=3):
    """Generates a summary using an extractive method."""
    sentences = preprocess_text(text)


    if len(sentences) <= summary_length:  
        return text  # If too short, return original text


    word_frequencies = build_word_frequencies(sentences)
    sentence_scores = rank_sentences(sentences, word_frequencies)


    summary = extract_summary(sentences, sentence_scores, num_sentences=summary_length)
    return summary


if __name__ == "__main__":
    print("Enter the text you want to summarize (press Enter twice when done):")
   
    # Capture multi-line input
    user_text = []
    blank_line_count = 0  


    while True:
        try:
            line = input()
            if line.strip() == "":
                blank_line_count += 1
                if blank_line_count == 2:
                    break
                user_text.append("")
            else:
                blank_line_count = 0
                user_text.append(line)
        except EOFError:
            break


    user_text = "\n".join(user_text)


    if not user_text.strip():
        print("⚠️ Error: You must enter some text to summarize!")
    else:
        summary = summarize_text_simple(user_text)
        print("\n🔹 Extractive Summary:\n", summary)



