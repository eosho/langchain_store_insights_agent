"""Simple Streamlit UI for Store Insights AI Chat."""

import os
import sys
import httpx
import streamlit as st

from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config.app_config import settings

# Page configuration
st.set_page_config(page_title="Store Insights AI", page_icon="🏪", layout="centered")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Ask me about store insights."}
    ]

# Get API URL from settings or environment
if "api_url" not in st.session_state:
    st.session_state.api_url = (
        settings.STORE_INSIGHTS_API_URL or "http://localhost:8000/v1/api"
    )


def call_ask_endpoint(
    question: str,
    api_url: str,
) -> Optional[Dict[str, Any]]:
    """Call the /chat/ask endpoint with a question."""
    try:
        payload: Dict[str, Any] = {"question": question}

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



# Process user input
if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = call_ask_endpoint(prompt, st.session_state.api_url)

            if response:
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
