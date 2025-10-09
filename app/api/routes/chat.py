from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Body, Request
from langchain_core.runnables import RunnableConfig

from schemas import ChatRequest, ChatResponse
from ..insights_client import ExternalInsightsClient
from graph import create_graph, GraphState


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("azure").setLevel(logging.WARNING)


router = APIRouter(prefix="/chat", tags=["chat"])


def get_insights_client(request: Request) -> ExternalInsightsClient:
    """Retrieve the shared ExternalInsightsClient from app state."""
    return request.app.state.insights_client


@router.post("/ask", response_model=ChatResponse)
async def ask(
    request: ChatRequest = Body(...),
    client: ExternalInsightsClient = Depends(get_insights_client),
):
    """Non-streaming chat endpoint that answers questions based on store insights.

    The graph now uses an intent analysis node to extract store_id and date from
    the question, then retrieves insights automatically.

    Args:
        request: ChatRequest containing question (e.g., "What are sales for store 100 yesterday?")
        client: Injected insights client

    Returns:
        ChatResponse with the answer, sources, and metadata (including extracted store_id/date)

    Raises:
        HTTPException: On LLM errors or missing configuration
    """
    try:
        # Create and invoke graph - it handles intent analysis and insights retrieval
        config = RunnableConfig(
            {"configurable": {"thread_id": 1, "insights_client": client}}
        )

        graph = create_graph()
        initial_state: GraphState = {
            "question": request.question,
            "generation": "",
            "insights": [],
            "store_id": None,
            "date": None,
            "route": "",
            "iteration_count": 0,
            "insights_retrieved": False,
        }

        final_state = await graph.ainvoke(initial_state, config)
        answer = final_state.get("generation", "")
        insights_used = final_state.get("insights", [])

        # Format date for response
        date_value = final_state.get("date")
        if date_value:
            # Convert date object to string if needed
            date_str = (
                date_value.isoformat()
                if hasattr(date_value, "isoformat")
                else str(date_value)
            )
        else:
            date_str = None

        return ChatResponse(
            answer=answer,
            sources=[
                item.dict() if hasattr(item, "dict") else dict(item)
                for item in insights_used
            ],
            metadata={
                "store_id": final_state.get("store_id"),
                "date": date_str,
                "route": final_state.get("route"),
            },
        )

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions from get_insights with logging
        logger.warning(f"HTTP exception: {http_exc.status_code} - {http_exc.detail}")
        raise
    except Exception as e:
        # Log full exception details with traceback
        logger.exception(f"Error generating response: {type(e).__name__}: {str(e)}\n")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {type(e).__name__}: {str(e)}",
        ) from e
