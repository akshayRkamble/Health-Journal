import streamlit as st
import pandas as pd
import datetime
import json
import os
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sentiment_analyzer import SentimentAnalyzer
from response_generator import ResponseGenerator

# Load custom CSS
def load_css():
    try:
        with open("style.css", "r") as f:
            css = f.read()
        return css
    except FileNotFoundError:
        print("Warning: style.css file not found. Using default styling.")
        return ""  # Return empty string if file not found

# App title and description
st.set_page_config(
    page_title="Mental Health Journal",
    page_icon="📔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(f'<style>{load_css()}</style>', unsafe_allow_html=True)

# Initialize our analyzers and generators
sentiment_analyzer = SentimentAnalyzer()
response_generator = ResponseGenerator()

# Function to load entries
def load_entries():
    if os.path.exists("journal_entries.json"):
        with open("journal_entries.json", "r") as f:
            return json.load(f)
    return []

# Function to save entries
def save_entries(entries):
    with open("journal_entries.json", "w") as f:
        json.dump(entries, f)

# App title and description
st.title("Mental Health Journal")
st.markdown("""
This app helps you track your mental well-being through daily journaling.
Write your thoughts, and receive personalized insights and suggestions powered by AI.
""")

# Initialize session state for entries if not present
if 'entries' not in st.session_state:
    st.session_state.entries = load_entries()

# Create tabs
tab1, tab2, tab3 = st.tabs(["Journal Entry", "History & Insights", "About"])

# Journal Entry Tab
with tab1:
    st.header("New Journal Entry")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        entry_date = st.date_input("Date", datetime.date.today())
        entry_text = st.text_area("How are you feeling today?", height=250)
        
        if st.button("Save Entry", use_container_width=True):
            if entry_text:
                with st.spinner("Analyzing your entry..."):
                    # Analyze sentiment with our enhanced analyzer
                    sentiment_results = sentiment_analyzer.analyze_text(entry_text)
                    
                    # Generate supportive response
                    response = response_generator.generate_response(entry_text, sentiment_results)
                    
                    # Get coping strategy if available
                    strategy = response_generator.get_coping_strategy(sentiment_results.get("emotions", {}))
                    
                    # Create entry
                    entry = {
                        "date": entry_date.strftime("%Y-%m-%d"),
                        "text": entry_text,
                        "sentiment": sentiment_results["label"],
                        "sentiment_score": sentiment_results["score"],
                        "emotions": sentiment_results.get("emotions", {}),
                        "response": response,
                        "strategy": strategy
                    }
                    
                    # Add to entries
                    st.session_state.entries.append(entry)
                    save_entries(st.session_state.entries)
                
                # Show success message
                st.success("Entry saved successfully!")
                
                # Display sentiment analysis
                st.write(f"Sentiment analysis: **{sentiment_results['label']}** (Score: {sentiment_results['score']:.2f})")
                
                # Display emotions if available
                if "emotions" in sentiment_results and any(sentiment_results["emotions"].values()):
                    emotions = sentiment_results["emotions"]
                    st.write("Emotional breakdown:")
                    cols = st.columns(3)
                    for i, (emotion, score) in enumerate(sorted(emotions.items(), key=lambda x: x[1], reverse=True)):
                        if score > 0.1:  # Only show significant emotions
                            with cols[i % 3]:
                                st.progress(score, text=f"{emotion.capitalize()}: {score:.2f}")
                
                # Display response
                st.markdown("### Your personalized response:")
                st.markdown(f"> *{response}*")
                
                # Display coping strategy if available
                if strategy:
                    st.markdown("### Suggested strategy:")
                    st.markdown(f"💡 *{strategy}*")
            else:
                st.error("Please write something before saving.")
    
    with col2:
        st.markdown("### Journaling Tips")
        st.markdown("""
        - **Be honest** with your feelings
        - Focus on **specific events** from your day
        - Note both **challenges** and **positive moments**
        - Consider what you're **grateful** for
        - Reflect on any **patterns** in your thoughts
        - Think about what you might do **differently** tomorrow
        """)
        
        # Show sample prompts to help users get started
        st.markdown("### Journaling Prompts")
        prompts = [
            "What made you smile today?",
            "What was challenging about today?",
            "What are you grateful for right now?",
            "What's something you learned today?",
            "How did you take care of yourself today?",
            "What would make tomorrow better?"
        ]
        selected_prompt = st.selectbox("Need inspiration?", ["Select a prompt..."] + prompts)
        if selected_prompt and selected_prompt != "Select a prompt...":
            st.info(f"Prompt: {selected_prompt}")

# History & Insights Tab
with tab2:
    st.header("Your Journal History")
    
    if not st.session_state.entries:
        st.info("No entries yet. Start journaling in the 'Journal Entry' tab!")
    else:
        # Create a DataFrame for analysis
        df = pd.DataFrame(st.session_state.entries)
        df['date'] = pd.to_datetime(df['date'])
        
        # Data summary
        total_entries = len(df)
        avg_sentiment = df['sentiment_score'].mean()
        
        # Calculate sentiment trend safely
        if len(df) >= 4:  # Need at least 4 entries to compare trends
            sentiment_trend = "positive" if df['sentiment_score'].iloc[-3:].mean() > df['sentiment_score'].iloc[:-3].mean() else "negative"
        elif len(df) >= 2:  # If we have 2-3 entries, compare the latest to the first
            sentiment_trend = "positive" if df['sentiment_score'].iloc[-1] > df['sentiment_score'].iloc[0] else "negative"
        else:  # Only one entry
            sentiment_trend = "neutral"
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Entries", total_entries)
        col2.metric("Average Mood", f"{avg_sentiment:.2f}")
        col3.metric("Recent Trend", "Improving" if sentiment_trend == "positive" else "Declining")
        
        # Time filter
        time_filter = st.radio("Time Range", ["All Time", "Last Week", "Last Month"], horizontal=True)
        if time_filter == "Last Week":
            df = df[df['date'] >= (pd.Timestamp.now() - pd.Timedelta(days=7))]
        elif time_filter == "Last Month":
            df = df[df['date'] >= (pd.Timestamp.now() - pd.Timedelta(days=30))]
        
        if len(df) > 0:
            # Show sentiment trend chart
            st.subheader("Mood Trends")
            fig = px.line(df, x='date', y='sentiment_score', 
                        title='Your Mood Over Time',
                        labels={'sentiment_score': 'Mood Score', 'date': 'Date'})
            
            # Add a trend line
            if len(df) >= 3:  # Need at least 3 points for a meaningful trendline
                try:
                    x = range(len(df))
                    y = df['sentiment_score'].values
                    coefficients = np.polyfit(x, y, 1)
                    trendline = np.poly1d(coefficients)
                    fig.add_trace(go.Scatter(x=df['date'], y=trendline(x),
                                        mode='lines', name='Trend',
                                        line=dict(color='rgba(255, 0, 0, 0.5)', width=2, dash='dash')))
                except Exception as e:
                    st.warning(f"Could not generate trend line: {e}")
            
            fig.update_layout(xaxis_title="Date", yaxis_title="Mood Score")
            st.plotly_chart(fig, use_container_width=True)
            
            # Show emotion distribution if we have emotion data
            if 'emotions' in df.columns and df['emotions'].apply(lambda x: isinstance(x, dict) and len(x) > 0).any():
                st.subheader("Emotion Distribution")
                
                # Extract and aggregate emotions
                emotion_data = {}
                for entry in df.itertuples():
                    if hasattr(entry, 'emotions') and isinstance(entry.emotions, dict):
                        for emotion, score in entry.emotions.items():
                            if emotion not in emotion_data:
                                emotion_data[emotion] = []
                            if isinstance(score, (int, float)):  # Ensure score is numeric
                                emotion_data[emotion].append(score)
                
                # Calculate average scores for each emotion
                emotion_avgs = {}
                for k, v in emotion_data.items():
                    if v:  # Only calculate if we have values
                        emotion_avgs[k] = sum(v)/len(v)
                
                # Create bar chart for emotions
                if emotion_avgs:  # Only create chart if we have data
                    fig = px.bar(
                        x=list(emotion_avgs.keys()),
                        y=list(emotion_avgs.values()),
                        labels={'x': 'Emotion', 'y': 'Average Intensity'},
                        title='Distribution of Emotions in Your Journal',
                        color=list(emotion_avgs.values()),
                        color_continuous_scale=px.colors.sequential.Viridis
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough emotion data to display yet.")
            
            # Entry history
            st.subheader("Previous Entries")
            
            # Filter option
            sentiment_filter = st.multiselect("Filter by sentiment", 
                                            options=["Positive", "Neutral", "Negative"],
                                            default=["Positive", "Neutral", "Negative"])
            
            filtered_entries = [e for e in st.session_state.entries 
                                if pd.to_datetime(e['date']) in df['date'].values 
                                and e['sentiment'] in sentiment_filter]
            
            for i, entry in enumerate(sorted(filtered_entries, 
                                            key=lambda x: x['date'], 
                                            reverse=True)):
                with st.expander(f"{entry['date']} - {entry['sentiment']}"):
                    st.write(entry['text'])
                    
                    # Display emotions if available
                    if "emotions" in entry and any(entry["emotions"].values()):
                        emotions_sorted = sorted(entry["emotions"].items(), key=lambda x: x[1], reverse=True)
                        top_emotions = [f"{emotion.capitalize()}: {score:.2f}" 
                                        for emotion, score in emotions_sorted[:3] 
                                        if score > 0.1]
                        if top_emotions:
                            st.caption(f"Top emotions: {', '.join(top_emotions)}")
                    
                    st.markdown(f"**Response:** *{entry['response']}*")
                    
                    if "strategy" in entry and entry["strategy"]:
                        st.markdown(f"**Suggested strategy:** *{entry['strategy']}*")
                    
                    # Option to delete entry
                    if st.button("Delete Entry", key=f"delete_{i}"):
                        st.session_state.entries.remove(entry)
                        save_entries(st.session_state.entries)
                        st.experimental_rerun()

# About Tab
with tab3:
    st.header("About Mental Health Journal")
    
    st.markdown("""
    This app is designed to help you track your mental well-being through daily journaling.
    
    ### Features:
    - **Journal Entries**: Record your thoughts and feelings
    - **Advanced Sentiment Analysis**: AI-powered analysis of your emotional state using natural language processing
    - **Emotion Detection**: Identification of specific emotions in your writing
    - **Supportive Responses**: Receive personalized and empathetic messages generated by AI
    - **Coping Strategies**: Get suggested actions based on your emotional state
    - **Mood Tracking**: Visualize your emotional well-being over time
    
    ### How It Works:
    1. **Write your journal entry** in the Journal Entry tab
    2. Our **AI analyzes the sentiment** and emotions in your text
    3. The system **generates a supportive response** tailored to your emotional state
    4. Your entry is **securely saved** for future reference
    5. Over time, you can **track patterns** in your mood and emotional well-being
    
    ### Privacy Note:
    All your journal entries are stored locally on your device and are not shared with any third parties.
    
    *This app is not a substitute for professional mental health care. If you're experiencing severe distress, please consult with a healthcare professional.*
    """)
    
    st.markdown("---")
    
    st.subheader("Technologies Used")
    st.markdown("""
    - **Streamlit**: For the web application interface
    - **Natural Language Processing**: For sentiment and emotion analysis
    - **Machine Learning**: For generating personalized responses
    - **Data Visualization**: For tracking mood trends over time
    """)

# Sidebar
st.sidebar.header("Mental Health Journal")
st.sidebar.image("https://img.icons8.com/fluency/96/000000/journal.png", width=100)

st.sidebar.subheader("Tips for Effective Journaling")
st.sidebar.markdown("""
- Write honestly about your feelings
- Try to journal at the same time each day
- Include both challenges and positive moments
- Reflect on patterns in your thoughts and emotions
- Use this as a tool for self-awareness, not judgment
""")

# Additional resources in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Mental Health Resources")
st.sidebar.markdown("""
- National Suicide Prevention Lifeline: 988 or 1-800-273-8255
- Crisis Text Line: Text HOME to 741741
- [Mental Health America](https://www.mhanational.org/)
- [National Alliance on Mental Illness](https://www.nami.org/)
""")

# Display disclaimer at the bottom
st.sidebar.markdown("---")
st.sidebar.caption("This application is for educational purposes only and not intended as a medical device.") 