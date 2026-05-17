import sys
from pathlib import Path
from dataclasses import asdict

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.retrieval.service import MovieRetrievalService
from app.decision.engine import DecisionEngine

import streamlit as st


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
    placeholder="I want to watch __ movie (both category and name are fine) with __ / alone tomorrow night under x rupees in location.",
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

retrieval_service = MovieRetrievalService()

st.subheader("Retrieve Movie Candidates")
retrieve_clicked = st.button("Retrieve Candidates")

if retrieve_clicked:
    try:
        retrieval_result = retrieval_service.retrieve(
            st.session_state.conversation.preferences
        )

        st.subheader("Retrieval Query")
        st.json(asdict(retrieval_result.query))

        st.subheader("Source Notes")
        st.write(retrieval_result.source_notes)

        st.subheader("Retrieval Metadata")

        st.json({
            "retrieval_strategy":
                retrieval_result.metadata.retrieval_strategy,

            "candidate_count":
                retrieval_result.metadata.candidate_count,

            "selected_movie_title":
                retrieval_result.metadata.selected_movie_title,
        })

        st.subheader("Candidates")
        st.json([asdict(candidate) for candidate in retrieval_result.candidates])

    except Exception as exc:
        st.error(str(exc))

st.subheader("Selected Movie Title")
st.write(st.session_state.conversation.preferences.selected_movie_title)

decision_engine = DecisionEngine()

st.subheader("Run Decision Engine")
decision_clicked = st.button("Rank and Recommend")

if decision_clicked:
    try:
        retrieval_result = retrieval_service.retrieve(
            st.session_state.conversation.preferences
        )

        decision_result = decision_engine.evaluate(
            st.session_state.conversation.preferences,
            retrieval_result,
        )

        st.subheader("Decision Summary")
        st.write(decision_result.summary)

        st.subheader("Ranked Candidates")
        ranked_output = []

        for item in decision_result.ranked_candidates:
            ranked_output.append(
                {
                    "movie_title": item.candidate.movie_title,
                    "theater_name": item.candidate.theater_name,
                    "showtime": item.candidate.showtime,
                    "ticket_price": item.candidate.ticket_price,
                    "distance_km": item.candidate.distance_km,
                    "language": item.candidate.language,
                    "score": item.total_score,
                    "score_breakdown": item.score_breakdown,
                    "reasons": item.reasons,
                    "source_name": item.candidate.source_name,
                    "source_url": item.candidate.source_url,
                }
            )

        st.json(ranked_output)

        st.subheader("Recommended Candidate")
        if decision_result.recommended_candidate:
            best = decision_result.recommended_candidate
            st.json(
                {
                    "movie_title": best.candidate.movie_title,
                    "theater_name": best.candidate.theater_name,
                    "showtime": best.candidate.showtime,
                    "ticket_price": best.candidate.ticket_price,
                    "distance_km": best.candidate.distance_km,
                    "language": best.candidate.language,
                    "score": best.total_score,
                    "score_breakdown": best.score_breakdown,
                    "reasons": best.reasons,
                    "source_name": best.candidate.source_name,
                    "source_url": best.candidate.source_url,
                }
            )
        else:
            st.write("No candidate survived the hard filters.")

        st.subheader("Rejected Candidates")
        rejected_output = []

        for item in decision_result.rejected_candidates:
            candidate = item["candidate"]
            rejected_output.append(
                {
                    "movie_title": candidate.movie_title,
                    "theater_name": candidate.theater_name,
                    "showtime": candidate.showtime,
                    "ticket_price": candidate.ticket_price,
                    "distance_km": candidate.distance_km,
                    "reasons": item["reasons"],
                    "source_name": candidate.source_name,
                    "source_url": candidate.source_url,
                }
            )

        st.json(rejected_output)

    except Exception as exc:
        st.error(str(exc))