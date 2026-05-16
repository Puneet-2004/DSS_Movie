import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.conversation.manager import ConversationManager
from app.conversation.state import ConversationState
from app.llm.extractor import PreferenceExtractor

st.set_page_config(page_title="Movie Decision Support System", layout="centered")

st.title("Movie Decision Support System")
st.write("Describe the movie experience you want, and I will extract the details.")

if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationState()

extractor = PreferenceExtractor()
manager = ConversationManager()

user_input = st.text_area(
    "Your input",
    placeholder="I want to watch an action movie with friends tomorrow night under 1000 rupees in Bangalore.",
    height=120,
)

col1, col2 = st.columns(2)

with col1:
    analyze_clicked = st.button("Analyze", type="primary")

with col2:
    reset_clicked = st.button("Reset conversation")

if reset_clicked:
    st.session_state.conversation = ConversationState()
    st.rerun()

if analyze_clicked:
    if not user_input.strip():
        st.warning("Please enter some text first.")
    else:
        new_preferences = extractor.extract(user_input)

        st.session_state.conversation.preferences = manager.merge_preferences(
            st.session_state.conversation.preferences,
            new_preferences,
        )

        st.session_state.conversation.history.append(
            {
                "user_input": user_input,
                "extracted": new_preferences.model_dump(),
                "merged": st.session_state.conversation.preferences.model_dump(),
            }
        )

st.subheader("Current Session Preferences")
st.json(st.session_state.conversation.preferences.model_dump())

missing_fields = manager.get_missing_required_fields(
    st.session_state.conversation.preferences
)

st.subheader("Missing Required Fields")
st.write(missing_fields)

next_question = manager.get_next_question(
    st.session_state.conversation.preferences
)

st.subheader("Next Question")
st.write(next_question)

st.subheader("Conversation History")
st.json(st.session_state.conversation.history)