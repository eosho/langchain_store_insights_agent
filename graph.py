from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from typing import List, Optional, Literal, cast
from datetime import date as Date, datetime
from typing_extensions import TypedDict

from schemas import Insight
from models import Router, Generator, ConversationalGenerator, IntentAnalyzer
from app.api.insights_client import ExternalInsightsClient
from app.llm.base import get_llm
from config import settings
from app.api.routes.insights import get_insights


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("azure").setLevel(logging.WARNING)


class GraphState(TypedDict):
    """Represents the state of our store insights RAG graph.
    
    Note: insights_client is NOT in state (not serializable).
    It must be passed via config: {"configurable": {"insights_client": client}}
    """

    question: str
    generation: str
    insights: List[Insight]
    store_id: Optional[str]
    date: Optional[Date]
    route: str
    iteration_count: int
    insights_retrieved: bool


class GraphNodes:
    """Node implementations for the Store Insights LangGraph workflow.

    Now includes intent analysis to extract store_id/date and retrieve insights within the graph.
    """

    def __init__(self):
        """Initialize nodes with models from models.py."""

        # Create shared LLM instances
        llm = get_llm(settings.llm_provider.value, temperature=0)

        # Initialize all model chains with shared LLM instances
        self.intent_analyzer = IntentAnalyzer.get_model(llm)
        self.question_router = Router.get_model(llm)
        self.rag_chain = Generator.get_model(llm)
        self.conversation_chain = ConversationalGenerator.get_model(llm)

    async def analyze_intent(self, state: GraphState, config: RunnableConfig) -> GraphState:
        """
        Analyze the question to extract store_id and date, then retrieve insights.

        Args:
            state (GraphState): The current graph state with question
            config (RunnableConfig): Config containing insights_client in configurable

        Returns:
            state (GraphState): Updated state with extracted parameters and retrieved insights
        """
        logger.debug("---ANALYZE INTENT---")

        question = state["question"]
        # Get insights_client from config instead of state (not serializable)
        insights_client = config.get("configurable", {}).get("insights_client")
        
        if not insights_client:
            logger.error("insights_client not found in config!")
            raise ValueError("insights_client must be passed via config")

        # Use LLM to extract intent (store_id, date, needs_insights)
        intent_result = await self.intent_analyzer.ainvoke({"question": question})
        intent = cast(IntentAnalyzer.ExtractedIntent, intent_result)

        logger.debug(
            f"---EXTRACTED INTENT: store_id={intent.store_id}, date={intent.date}, needs_insights={intent.needs_insights}---"
        )

        # Retrieve insights if needed
        insights = []
        date_obj = None

        # Convert date string to Date object if provided
        if intent.date:
            try:
                date_obj = datetime.strptime(intent.date, "%Y-%m-%d").date()
            except ValueError:
                logger.debug(f"---INVALID DATE FORMAT: {intent.date}---")

        if intent.needs_insights:
            try:
                # Call get_insights to retrieve data
                insights_response = await get_insights(
                    store_id=intent.store_id,
                    date=date_obj,
                    client=insights_client,
                )

                # Extract insights from response
                insights = insights_response.get("items", [])

                logger.debug(f"---RETRIEVED {len(insights)} INSIGHTS---")

            except Exception as e:
                logger.debug(f"---ERROR RETRIEVING INSIGHTS: {str(e)}---")
                # Continue with empty insights - generator will handle appropriately

        return {
            "question": question,
            "generation": state.get("generation", ""),
            "insights": insights,
            "store_id": intent.store_id,
            "date": date_obj,
            "route": state.get("route", ""),
            "iteration_count": state.get("iteration_count", 0) + 1,
            "insights_retrieved": True,
        }

    async def generate_answer(self, state: GraphState) -> GraphState:
        """
        Generate answer based on insights passed from chat.py.

        Args:
            state (GraphState): The current graph state with insights already populated

        Returns:
            state (GraphState): Updated state with generation
        """
        logger.debug("---GENERATE ANSWER---")

        question = state["question"]
        insights = state.get("insights", [])

        # Generate answer using the RAG chain
        generation = await self.rag_chain.ainvoke(
            {
                "context": insights,
                "question": question,
            }
        )

        logger.debug(f"---GENERATION: {generation[:100]}...---")

        return {
            "insights": insights,
            "question": question,
            "generation": generation,
            "store_id": state.get("store_id"),
            "date": state.get("date"),
            "route": "insights_api",
            "iteration_count": state.get("iteration_count", 0) + 1,
            "insights_retrieved": state.get("insights_retrieved", False),
        }

    async def generate_conversational(self, state: GraphState) -> GraphState:
        """
        Generate conversational response for general chat.

        Args:
            state (GraphState): The current graph state

        Returns:
            state (GraphState): New key added to state, generation, that contains conversational response
        """
        logger.debug("---GENERATE CONVERSATIONAL---")

        question = state["question"]

        # Generate conversational response
        generation = await self.conversation_chain.ainvoke({"question": question})

        logger.debug(f"---CONVERSATION: {generation[:100]}...---")

        return {
            "insights": [],  # No insights for general chat
            "question": question,
            "generation": generation,
            "store_id": state.get("store_id"),
            "date": state.get("date"),
            "route": "general_chat",
            "iteration_count": state.get("iteration_count", 0) + 1,
            "insights_retrieved": state.get("insights_retrieved", False),
        }

    # Edge/Routing Functions

    def route_question(
        self, state: GraphState
    ) -> Literal["general_chat", "insights_api"]:
        """
        Route question to general chat or insights API.

        Args:
            state (GraphState): The current graph state

        Returns:
            str: Next node to call ("general_chat" or "insights_api")
        """
        logger.debug("---ROUTE QUESTION---")

        question = state["question"]

        # Use router model to classify
        source_result = self.question_router.invoke({"question": question})
        source = cast(Router.RouteQuery, source_result)

        if source.datasource == "general_chat":
            logger.debug("---ROUTE QUESTION TO GENERAL CHAT---")
            return "general_chat"
        elif source.datasource == "insights_api":
            logger.debug("---ROUTE QUESTION TO INSIGHTS API---")
            return "insights_api"

        # Default to insights_api if unclear
        return "insights_api"


class StoreInsightsGraph:
    """LangGraph workflow for store insights generation.

    New flow: analyze_intent → route → generate
    The graph now handles intent analysis and insights retrieval internally.
    """

    @staticmethod
    def create(nodes: GraphNodes):
        """
        Create workflow: analyze_intent → route → generate.

        The graph now:
        1. Analyzes the question to extract store_id and date
        2. Retrieves insights from the external API
        3. Routes the question (general chat vs insights-based)
        4. Generates appropriate response

        Args:
            nodes: Nodes instance with intent analysis, routing and generation methods

        Returns:
            Compiled LangGraph StateGraph
        """
        workflow = StateGraph(GraphState)

        # Define nodes
        workflow.add_node("analyze_intent", nodes.analyze_intent)
        workflow.add_node("generate_answer", nodes.generate_answer)
        workflow.add_node("generate_conversational", nodes.generate_conversational)

        # Start with intent analysis
        workflow.set_entry_point("analyze_intent")

        # After intent analysis, route based on question type
        workflow.add_conditional_edges(
            "analyze_intent",
            nodes.route_question,
            {
                "general_chat": "generate_conversational",
                "insights_api": "generate_answer",
            },
        )

        # Simple linear flow - both routes lead to END
        workflow.add_edge("generate_conversational", END)
        workflow.add_edge("generate_answer", END)

        checkpointer = InMemorySaver()
        return workflow.compile(checkpointer=checkpointer)


def create_graph():
    """
    Factory function to create and initialize the Store Insights graph.

    This is the recommended way to initialize the graph from chat.py.
    The graph now handles intent analysis and insights retrieval internally.

    Returns:
        Compiled LangGraph workflow ready to execute
    """
    nodes = GraphNodes()
    return StoreInsightsGraph.create(nodes)
