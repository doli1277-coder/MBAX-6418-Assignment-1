import streamlit as st
import pandas as pd
import json
import plotly.express as px

# --- Configure Page ---
st.set_page_config(page_title="Review Sentiment Dashboard", layout="wide")
st.title("Amazon Gift Cards: Sentiment & Emotion Analysis")

# --- Load Data ---
@st.cache_data
def load_data():
    with open("/Users/rockyli/Desktop/AssignmentOne/final_reviews.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # Determine if prediction was correct
    df['is_correct'] = df['true_class'] == df['predicted_sentiment']
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Could not find final_reviews.json. Please ensure it is in the AssignmentOne folder.")
    st.stop()

# --- Headline Metrics ---
total_reviews = len(df)
accuracy = df['is_correct'].mean() * 100

col1, col2, col3 = st.columns(3)
col1.metric("Total Reviews (Balanced)", total_reviews)
col2.metric("Overall Accuracy", f"{accuracy:.1f}%")

# --- Visualizations ---
st.header("Model Performance & Diagnostics")

colA, colB = st.columns(2)

with colA:
    st.subheader("Confusion Matrix: True vs. Predicted")
    # Group by true and predicted classes
    confusion_df = df.groupby(['true_class', 'predicted_sentiment']).size().reset_index(name='count')
    fig_conf = px.bar(confusion_df, x='true_class', y='count', color='predicted_sentiment', 
                      barmode='group', labels={'true_class': 'Actual Rating Class', 'count': 'Number of Reviews'},
                      color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_conf, use_container_width=True)

with colB:
    st.subheader("Emotion Comparison: LLM vs. NRC Lexicon")
    # Compare the top emotions detected by both methods
    emotion_melt = df.melt(value_vars=['llm_emotion', 'nrc_emotion'], var_name='Method', value_name='Emotion')
    fig_emo = px.histogram(emotion_melt, x='Emotion', color='Method', barmode='group',
                           color_discrete_sequence=['#636EFA', '#EF553B'])
    st.plotly_chart(fig_emo, use_container_width=True)

# --- Interactive Review Filtering (Step 4) ---
st.header("Interactive Review Explorer")

filter_choice = st.radio("Filter Reviews:", ["All", "Correct Predictions", "Mismatched Predictions"], horizontal=True)

if filter_choice == "Correct Predictions":
    filtered_df = df[df['is_correct'] == True]
elif filter_choice == "Mismatched Predictions":
    filtered_df = df[df['is_correct'] == False]
else:
    filtered_df = df

st.write(f"Showing **{len(filtered_df)}** reviews based on filter.")
st.dataframe(filtered_df[['title', 'text', 'rating', 'true_class', 'predicted_sentiment', 'llm_emotion', 'nrc_emotion']], use_container_width=True)