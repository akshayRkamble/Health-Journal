import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import numpy as np

# Ensure NLTK data is downloaded
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

class SentimentAnalyzer:
    def __init__(self):
        # Initialize VADER sentiment analyzer
        self.sia = SentimentIntensityAnalyzer()
        # We'll use only VADER for simplicity
        self.has_transformer = False
    
    def analyze_text(self, text):
        """
        Analyze text sentiment using VADER
        Returns sentiment label, score, and emotional categories
        """
        # Basic sentiment scores from VADER
        vader_scores = self.sia.polarity_scores(text)
        compound_score = vader_scores['compound']
        
        # Default sentiment categorization with VADER
        if compound_score >= 0.05:
            sentiment_label = "Positive"
        elif compound_score <= -0.05:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"
        
        # Use only VADER score
        final_score = compound_score
        
        # Extract emotional categories (rough approximation)
        emotions = self._extract_emotions(text, vader_scores)
        
        return {
            "label": sentiment_label,
            "score": final_score,
            "emotions": emotions,
            "raw_vader": vader_scores
        }
    
    def _extract_emotions(self, text, vader_scores):
        """
        Extract specific emotional categories based on lexical analysis
        This is a simple implementation - could be improved with a dedicated emotion classifier
        """
        emotions = {}
        
        # Emotion keywords (simple implementation)
        emotion_keywords = {
            "joy": ["happy", "joy", "delighted", "pleasure", "excited", "glad", "smile"],
            "sadness": ["sad", "unhappy", "depressed", "down", "miserable", "gloomy", "tearful"],
            "anger": ["angry", "mad", "furious", "outraged", "annoyed", "irritated", "frustrated"],
            "fear": ["afraid", "scared", "terrified", "anxious", "worried", "nervous", "panic"],
            "surprise": ["surprised", "amazed", "astonished", "shocked", "unexpected"],
            "disgust": ["disgusted", "revolted", "nauseated", "appalled", "repulsed"]
        }
        
        # Count occurrences of emotion words
        text_lower = text.lower()
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            emotions[emotion] = min(count / 2, 1.0)  # Normalize to max of 1.0
        
        # Influence emotion scores based on VADER
        if vader_scores['pos'] > 0.2:
            emotions["joy"] = max(emotions["joy"], vader_scores['pos'])
        if vader_scores['neg'] > 0.2:
            emotions["sadness"] = max(emotions["sadness"], vader_scores['neg'] * 0.7)
            emotions["anger"] = max(emotions["anger"], vader_scores['neg'] * 0.5)
        
        return emotions 