"""
summarizer.py — Generate concise article summaries and key takeaways.
"""

import re
import logging

logger = logging.getLogger(__name__)

try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer
    from sumy.nlp.stemmers import Stemmer
    from sumy.utils import get_stop_words
    SUMY_AVAILABLE = True
except ImportError:
    SUMY_AVAILABLE = False
    logger.warning("sumy not installed — using built-in TF summariser.")


def _summarise_sumy(text: str, sentence_count: int = 3) -> str:
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    stemmer = Stemmer("english")
    summariser = LsaSummarizer(stemmer)
    summariser.stop_words = get_stop_words("english")
    sentences = summariser(parser.document, sentence_count)
    return " ".join(str(s) for s in sentences)


def _sentence_score(sentence: str, word_freq: dict) -> float:
    words = re.findall(r"\b\w+\b", sentence.lower())
    if not words:
        return 0.0
    return sum(word_freq.get(w, 0) for w in words) / len(words)


def _summarise_tfidf(text: str, sentence_count: int = 3) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if len(sentences) <= sentence_count:
        return text
    words = re.findall(r"\b\w+\b", text.lower())
    stopwords = {
        "the","a","an","is","are","was","were","to","of","in","and","or",
        "it","that","this","for","on","at","by","with","as","be","has",
        "have","had","from","not","its","but",
    }
    freq = {}
    for w in words:
        if w not in stopwords and len(w) > 2:
            freq[w] = freq.get(w, 0) + 1
    scored = [(s, _sentence_score(s, freq)) for s in sentences if len(s) > 20]
    scored.sort(key=lambda x: x[1], reverse=True)
    top = {s for s, _ in scored[:sentence_count]}
    ordered = [s for s in sentences if s in top]
    return " ".join(ordered)


def summarise(text: str, sentence_count: int = 3) -> str:
    if not text or len(text.split()) < 30:
        return text.strip()
    if SUMY_AVAILABLE:
        try:
            return _summarise_sumy(text, sentence_count)
        except Exception as exc:
            logger.debug("sumy failed, using fallback: %s", exc)
    return _summarise_tfidf(text, sentence_count)


_TAKEAWAY_PATTERNS = [
    r"(?:announced?|said|stated?|reported?|confirmed?|revealed?)[^.]{10,80}\.",
    r"(?:will|plans? to|expects? to|aims? to)[^.]{10,80}\.",
    r"(?:increased?|decreased?|rose|fell|surged?|dropped?)[^.]{5,60}\.",
]


def extract_takeaway(text: str, title: str = "") -> str:
    if not text:
        return title or "No summary available."
    for pattern in _TAKEAWAY_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            sentence = match.group(0).strip()
            if 20 < len(sentence) < 200:
                return sentence
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    for s in sentences:
        if len(s) > 40:
            return s[:200].strip()
    return title or "No key takeaway identified."


def summarise_articles(articles: list) -> list:
    for art in articles:
        body = getattr(art, "body", "")
        art.summary = summarise(body)
        art.takeaway = extract_takeaway(body, art.title)
        logger.debug("Summarised: %s", art.title[:60])
    return articles
