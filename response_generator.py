import random

class ResponseGenerator:
    def __init__(self):
        # We'll use pre-defined responses only
        self.has_model = False
        print("Using pre-defined responses.")
        
        # Pre-defined responses
        self.positive_responses = [
            "It's wonderful to hear you're feeling good! Keep nurturing those positive emotions and remember what contributed to them.",
            "I'm so glad you're experiencing these positive feelings. You deserve these moments of joy!",
            "That's fantastic news! Acknowledging these positive emotions helps reinforce them.",
            "Your positive outlook is inspiring. Consider how you might carry this energy forward into tomorrow.",
            "Wonderful! Take a moment to really savor these positive feelings and what brought them about."
        ]
        
        self.negative_responses = [
            "I hear that you're going through a difficult time. Remember that it's okay to feel this way, and these feelings won't last forever.",
            "I'm sorry you're feeling down. Be gentle with yourself today and remember that even small acts of self-care can help.",
            "It sounds like today has been challenging. Try to focus on small things within your control and remember that you have overcome difficult times before.",
            "When we face tough emotions, sometimes just acknowledging them can help. You're showing strength by expressing your feelings.",
            "During difficult moments, try to treat yourself with the same kindness you would offer a good friend. You deserve compassion."
        ]
        
        self.neutral_responses = [
            "Thank you for sharing your thoughts today. Regular reflection like this is a powerful practice for self-awareness.",
            "Even in neutral moments, you're developing important insight through your journaling practice.",
            "Every day doesn't need to be extraordinary. There's value in these moments of calm reflection too.",
            "Your commitment to checking in with yourself shows dedication to your well-being.",
            "Sometimes a neutral day provides good space for reflection on your broader goals and values."
        ]
    
    def generate_response(self, text, sentiment_info):
        """
        Generate an empathetic response based on the sentiment of the input text
        Uses pre-defined responses
        """
        sentiment = sentiment_info["label"]
        emotions = sentiment_info.get("emotions", {})
        
        # Select appropriate response set based on sentiment
        if sentiment == "Positive":
            responses = self.positive_responses
        elif sentiment == "Negative":
            responses = self.negative_responses
        else:
            responses = self.neutral_responses
        
        # Determine if any emotion is particularly strong
        strongest_emotion = None
        strongest_score = 0.5  # Threshold
        
        for emotion, score in emotions.items():
            if score > strongest_score:
                strongest_emotion = emotion
                strongest_score = score
        
        # Select a random response from the appropriate set
        return random.choice(responses)
            
    def get_coping_strategy(self, emotions):
        """
        Suggest a specific coping strategy based on detected emotions
        """
        strategies = {
            "sadness": [
                "Consider talking to someone you trust about how you're feeling",
                "Gentle exercise like walking can help lift your mood",
                "Be kind to yourself today and engage in a small self-care activity"
            ],
            "anger": [
                "Deep breathing exercises can help manage feelings of anger",
                "Physical activity can be a healthy outlet for frustration",
                "Writing out your thoughts might help process these emotions"
            ],
            "fear": [
                "Grounding exercises can help with anxiety - try naming 5 things you can see, 4 things you can touch, etc.",
                "Limiting news and social media might help reduce feelings of anxiety",
                "Progressive muscle relaxation can help release tension from anxiety"
            ],
            "joy": [
                "Savor this positive feeling by writing down what contributed to it",
                "Share your positive experience with someone close to you",
                "Consider how you might create similar positive experiences in the future"
            ]
        }
        
        # Find the strongest emotion
        if not emotions:
            return None
            
        strongest_emotion = max(emotions.items(), key=lambda x: x[1])
        
        # Only suggest a strategy if the emotion is significant
        if strongest_emotion[1] > 0.3 and strongest_emotion[0] in strategies:
            return random.choice(strategies[strongest_emotion[0]])
            
        return None 