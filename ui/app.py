"""Simple Streamlit UI for Store Insights AI Chat."""

import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
import streamlit as st
from typing import Dict, Any, Optional
from config import settings

# Page configuration
st.set_page_config(page_title="Store Insights AI", page_icon="🏪", layout="centered")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Ask me about store insights."}
    ]

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "waiting_for_clarification" not in st.session_state:
    st.session_state.waiting_for_clarification = False

if "clarification_request" not in st.session_state:
    st.session_state.clarification_request = None

# Get API URL from settings or environment
if "api_url" not in st.session_state:
    st.session_state.api_url = (
        settings.store_insights_api_url or "http://localhost:8000/v1/api"
    )


def call_ask_endpoint(
    question: str,
    api_url: str,
    session_id: Optional[str] = None,
    resume_value: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Call the /chat/ask endpoint with a question or resume value."""
    try:
        payload: Dict[str, Any] = {"question": question}
        if session_id:
            payload["session_id"] = session_id
        if resume_value:
            payload["resume_value"] = resume_value

        with httpx.Client(timeout=60.0) as client:
            response = client.post(f"{api_url}/chat/ask", json=payload)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


# Header
st.title("🏪 Store Insights AI")

with st.expander(label="About Store Insights AI", expanded=True):
    """
    This chatbot is powered by LangGraph, and used to answer questions
    about store performance, inventory, and operations.

    It intelligently extracts store IDs and dates from your questions, retrieves relevant insights
    from the `Store Insights API`, and generates natural language responses powered by Azure OpenAI.
    """
st.caption("Ask questions about store performance in natural language")

# Sidebar
with st.sidebar:
    st.header("Settings")
    api_url = st.text_input("API URL", value=st.session_state.api_url)
    st.session_state.api_url = api_url

    # Test connection button
    if st.button("🔗 Test Connection", use_container_width=True):
        try:
            with httpx.Client(timeout=5.0) as client:
                api_url = st.session_state.api_url
                response = client.get(f"{str(api_url).rstrip('/chat/ask')}/health")
                if response.status_code == 200:
                    st.success("✅ Connected successfully!")
                else:
                    st.error(f"❌ Connection failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")

    st.divider()

    st.subheader("Example Queries")
    examples = [
        "What are the recommendations for store 100?",
        "Show me insights for store 50 from yesterday",
        "How did store 200 perform last week?",
    ]
    for example in examples:
        if st.button(example, key=example):
            st.session_state.example_query = example

    st.divider()

    if st.button("Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! Ask me about store insights."}
        ]
        st.session_state.thread_id = None
        st.session_state.waiting_for_clarification = False
        st.session_state.clarification_request = None
        st.rerun()

# Display chat messages
for msg in st.session_state.messages:
    role = "assistant" if msg["role"] == "assistant" else "user"
    st.chat_message(role).write(msg["content"])

    # Show metadata and sources if available
    if msg["role"] == "assistant" and "metadata" in msg:
        with st.expander("View Details"):
            st.json(msg.get("metadata", {}))
            if "sources" in msg and msg["sources"]:
                st.write(f"**Sources:** {len(msg['sources'])} insights")

# Handle example query
if "example_query" in st.session_state:
    prompt = st.session_state.example_query
    del st.session_state.example_query
else:
    prompt = st.chat_input("Ask about store insights...")


# Handle clarification input
if (
    st.session_state.waiting_for_clarification
    and st.session_state.clarification_request
):
    clarification = st.session_state.clarification_request

    with st.chat_message("assistant"):
        st.info(
            f"🤔 **Clarification needed:** {clarification.get('message', 'Please provide more information')}"
        )

        # Show current extracted values
        if "current_values" in clarification:
            with st.expander("Current extracted values"):
                st.json(clarification["current_values"])

    # Use form for clarification input
    with st.form("clarification_form", clear_on_submit=True):
        st.write("Please provide the correct information:")

        current_vals = clarification.get("current_values", {})
        store_id_input = st.text_input(
            "Store ID", value=current_vals.get("store_id", "")
        )
        date_input = st.text_input(
            "Date (YYYY-MM-DD)", value=current_vals.get("date", "")
        )

        submitted = st.form_submit_button("Submit Clarification")

        if submitted:
            # Prepare resume value
            resume_value = {
                "store_id": store_id_input if store_id_input else None,
                "date": date_input if date_input else None,
            }

            with st.spinner("Processing your clarification..."):
                response = call_ask_endpoint(
                    question="",  # Not used for resume
                    api_url=st.session_state.api_url,
                    session_id=st.session_state.thread_id,
                    resume_value=resume_value,
                )

                if response:
                    # Clear clarification state
                    st.session_state.waiting_for_clarification = False
                    st.session_state.clarification_request = None

                    # Check if another clarification is needed
                    if response.get("needs_clarification"):
                        st.session_state.waiting_for_clarification = True
                        st.session_state.clarification_request = response.get(
                            "clarification_request"
                        )
                        st.session_state.thread_id = response.get("session_id")
                    else:
                        # Got final answer
                        answer = response.get("answer", "No answer received")
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                                "metadata": response.get("metadata", {}),
                                "sources": response.get("sources", []),
                            }
                        )

                st.rerun()

# Process user input
elif prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = call_ask_endpoint(
                prompt, st.session_state.api_url, session_id=st.session_state.thread_id
            )

            if response:
                # Save session ID for continuity
                if response.get("session_id"):
                    st.session_state.thread_id = response["session_id"]

                # Check if clarification is needed
                if response.get("needs_clarification"):
                    st.session_state.waiting_for_clarification = True
                    st.session_state.clarification_request = response.get(
                        "clarification_request"
                    )
                    st.info(
                        f"🤔 {response['clarification_request'].get('message', 'Need more information')}"
                    )
                else:
                    # Normal response
                    answer = response.get("answer", "No answer received")
                    st.markdown(answer)

                    # Add to session state with full response
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "metadata": response.get("metadata", {}),
                            "sources": response.get("sources", []),
                        }
                    )

                    # Show details
                    with st.expander("View Details"):
                        st.json(response.get("metadata", {}))
                        if response.get("sources"):
                            st.write(
                                f"**Sources:** {len(response['sources'])} insights"
                            )
            else:
                error_msg = "Sorry, I encountered an error processing your request."
                st.write(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )

        st.rerun()
