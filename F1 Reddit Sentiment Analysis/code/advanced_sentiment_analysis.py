import spacy
import pandas as pd
import numpy as np
from spacytextblob.spacytextblob import SpacyTextBlob
from spacy.tokens import Doc, Span
from spacy.language import Language
from collections import defaultdict

class AdvancedSentimentAnalyzer:
    def __init__(self):
        """Initialize the spaCy model with the SpacyTextBlob component"""
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_md")
        
        # Add the SpacyTextBlob component for more comprehensive sentiment analysis
        self.nlp.add_pipe('spacytextblob')
    
    def basic_sentiment_analysis(self, text):
        """
        Performs basic sentiment analysis using SpacyTextBlob
        Returns polarity (-1 to 1) and subjectivity (0 to 1)
        """
        doc = self.nlp(text)
        polarity = doc._.blob.polarity
        subjectivity = doc._.blob.subjectivity
        
        # Define sentiment category
        if polarity > 0.1:
            sentiment = "Positive"
        elif polarity < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        return {
            "text": text,
            "polarity": polarity,
            "subjectivity": subjectivity,
            "sentiment": sentiment
        }
    
    def aspect_based_sentiment_analysis(self, text, aspects):
        """
        Performs aspect-based sentiment analysis
        For each provided aspect, determines the sentiment when mentioned
        
        Args:
            text (str): Input text to analyze
            aspects (list): List of aspects to look for (strings)
        
        Returns:
            dict: Dictionary of aspects and their associated sentiments
        """
        doc = self.nlp(text)
        results = {}
        
        # Create a span range window to detect sentiments near aspects
        for aspect in aspects:
            aspect_sentiments = []
            aspect_doc = self.nlp(aspect.lower())
            
            # Find aspect mentions
            for token in doc:
                if token.text.lower() == aspect.lower() or any(
                    token.has_vector and a.has_vector and token.similarity(a) > 0.8
                    for a in aspect_doc
                ):
                    # Get surrounding context (5 tokens on each side)
                    start = max(0, token.i - 5)
                    end = min(len(doc), token.i + 6)
                    
                    # Create context span and get its sentiment
                    context = doc[start:end]
                    aspect_text = context.text
                    aspect_polarity = context._.blob.polarity
                    
                    aspect_sentiments.append({
                        "mention": aspect_text,
                        "polarity": aspect_polarity
                    })
            
            if aspect_sentiments:
                avg_sentiment = sum(item["polarity"] for item in aspect_sentiments) / len(aspect_sentiments)
                results[aspect] = {
                    "mentions": aspect_sentiments,
                    "average_polarity": avg_sentiment,
                    "overall_sentiment": "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral"
                }
            else:
                results[aspect] = {"mentions": [], "average_polarity": 0, "overall_sentiment": "Not mentioned"}
        
        return results
    
    def sentence_level_sentiment_analysis(self, text):
        """
        Analyzes sentiment at the sentence level to detect mixed opinions
        """
        doc = self.nlp(text)
        sentences = list(doc.sents)
        
        results = []
        for sent in sentences:
            sent_doc = self.nlp(sent.text)
            results.append({
                "sentence": sent.text,
                "polarity": sent_doc._.blob.polarity,
                "subjectivity": sent_doc._.blob.subjectivity,
                "sentiment": "Positive" if sent_doc._.blob.polarity > 0.1 else 
                            "Negative" if sent_doc._.blob.polarity < -0.1 else "Neutral"
            })
        
        return results
    
    def extract_sentiment_phrases(self, text):
        """
        Extracts phrases that contribute to sentiment
        Focuses on adjective-noun pairs and verb phrases
        """
        doc = self.nlp(text)
        sentiment_phrases = []
        
        # Look for adjective-noun pairs
        for token in doc:
            if token.pos_ == "ADJ":
                # Look for the noun this adjective modifies
                if token.head.pos_ in ["NOUN", "PROPN"]:
                    phrase = f"{token.text} {token.head.text}"
                    phrase_doc = self.nlp(phrase)
                    sentiment_phrases.append({
                        "phrase": phrase,
                        "polarity": phrase_doc._.blob.polarity,
                        "type": "adjective-noun"
                    })
        
        # Look for verb phrases with sentiment
        for token in doc:
            if token.pos_ == "VERB":
                # Get verb with its direct object if available
                verb_phrase = token.text
                for child in token.children:
                    if child.dep_ in ["dobj", "obj"]:
                        verb_phrase = f"{token.text} {child.text}"
                        break
                
                # Only add if not just a single verb
                if verb_phrase != token.text or token._.blob.polarity != 0:
                    phrase_doc = self.nlp(verb_phrase)
                    sentiment_phrases.append({
                        "phrase": verb_phrase,
                        "polarity": phrase_doc._.blob.polarity,
                        "type": "verb-phrase"
                    })
        
        return sentiment_phrases

# Sample usage demo
if __name__ == "__main__":
    analyzer = AdvancedSentimentAnalyzer()
    
    sample_text = """The new iPhone has an excellent camera and stunning display, 
                    but the battery life is disappointing. The price is too high 
                    for what you get, though the design is sleek and modern."""
    
    # sample_text = """After reading about Bleecker Street Pizza would it live up to the hype? 
    # Absolutely in fact the best pizza I have ever tasted. I went for the Nonna Maria and it was
    #  absolutely delicious whilst Jnr Jock went for the cheese slice and loved that too. 
    #  After tasting my Nonna Maria she decided to get one too. We sat outside on a gorgeous day
    # in November with the perfect pizza, cold beer for me and a cold white wine for Jnr and 
    # just watched the world go by. Will definitely return this time with Mrs Jock next year."""
    
    print("Basic Sentiment Analysis:")
    print(analyzer.basic_sentiment_analysis(sample_text))
    print("\nAspect-Based Sentiment Analysis:")
    aspects = ["camera", "battery", "price", "design"]
    print(analyzer.aspect_based_sentiment_analysis(sample_text, aspects))
    print("\nSentence Level Sentiment Analysis:")
    sentence_results = analyzer.sentence_level_sentiment_analysis(sample_text)
    for result in sentence_results:
        print(f"- {result['sentence']} -> {result['sentiment']} ({result['polarity']:.2f})")
    print("\nSentiment Phrases:")
    phrases = analyzer.extract_sentiment_phrases(sample_text)
    for phrase in phrases:
        print(f"- {phrase['phrase']} -> {phrase['polarity']:.2f} [{phrase['type']}]")
