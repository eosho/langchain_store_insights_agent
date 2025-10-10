from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from typing import List, Optional, Literal, cast
from datetime import date as Date, datetime
from typing_extensions import TypedDict

from schemas import Insight
from models import (
    Router,
    Generator,
    ConversationalGenerator,
    IntentAnalyzer,
    HallucinationGrader,
)
from app.llm.base import get_llm, PROVIDER_TYPE
from app.config.app_config import settings
from app.api.routes.insights import get_insights
from app.api.insights_client import FreshAgentAPIClient


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("azure").setLevel(logging.WARNING)


class GraphState(TypedDict):
    """Represents the state of our store insights RAG graph."""

    question: str
    generation: str
    insights: List[Insight]
    store_id: Optional[str]
    date: Optional[Date]
    route: str
    iteration_count: int
    insights_retrieved: bool
    is_grounded: Optional[str]


class GraphNodes:
    """Node implementations for the Store Insights LangGraph workflow.

    Now includes intent analysis to extract store_id/date and retrieve insights within the graph.
    """

    def __init__(self):
        """Initialize nodes with models from models.py."""

        # Create shared LLM instances
        llm = get_llm(cast(PROVIDER_TYPE, settings.LLM_PROVIDER), temperature=0)
        grader_llm = get_llm(
            cast(PROVIDER_TYPE, settings.LLM_PROVIDER), temperature=0.7
        )

        # Initialize all model chains with shared LLM instances
        self.intent_analyzer = IntentAnalyzer.get_model(llm)
        self.question_router = Router.get_model(llm)
        self.rag_chain = Generator.get_model(llm)
        self.conversation_chain = ConversationalGenerator.get_model(llm)
        self.hallucination_grader = HallucinationGrader.get_model(grader_llm)

    async def analyze_intent(
        self, state: GraphState, config: RunnableConfig
    ) -> GraphState:
        """
        Analyze the question to extract store_id and date, then retrieve insights.

        Args:
            state (GraphState): The current graph state with question
            config (RunnableConfig): Config containing insights_client in configurable

        Returns:
            state (GraphState): Updated state with extracted parameters and retrieved insights
        """
        logger.debug("---ANALYZE INTENT---")

        question = state.get("question")
        # Get insights_client from config instead of state (not serializable)
        insights_client = config.get("configurable", {}).get("insights_client")

        if not insights_client:
            logger.warning(
                "insights_client not found in config! Initializing a new instance."
            )

            insights_client = FreshAgentAPIClient(
                base_url=settings.FRESH_AGENT_API_BASE_URL,
                api_key=settings.FRESH_AGENT_API_KEY,
            )

        # Use LLM to extract intent (store_id, date, needs_insights)
        result = await self.intent_analyzer.ainvoke({"question": question})
        intent = cast(IntentAnalyzer.ExtractedIntent, result)

        logger.debug(
            f"---EXTRACTED INTENT: store_id={intent.store_id}, needs_insights={intent.needs_insights}---"
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
            **state,
            "question": question,
            "insights": insights,
            "store_id": intent.store_id,
            "date": date_obj,
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

        question = state.get("question")
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
            **state,
            "generation": generation,
            "route": "insights_api",
            "iteration_count": state.get("iteration_count", 0) + 1,
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

        question = state.get("question")

        # Generate conversational response
        generation = await self.conversation_chain.ainvoke({"question": question})

        logger.debug(f"---CONVERSATION: {generation[:100]}...---")

        return {
            **state,
            "generation": generation,
            "route": "general_chat",
            "insights": [],  # No insights for general chat
            "iteration_count": state.get("iteration_count", 0) + 1,
        }

    async def grade_hallucination(self, state: GraphState) -> GraphState:
        """
        Grade whether the generated answer is grounded in the provided insights.

        Args:
            state (GraphState): Current state with generation and insights

        Returns:
            state (GraphState): Updated state with is_grounded field
        """
        logger.debug("---GRADE HALLUCINATION---")

        generation = state.get("generation")
        insights = state.get("insights", [])

        # Grade the answer
        grade_result = await self.hallucination_grader.ainvoke(
            {"context": insights, "generation": generation}
        )
        grade = cast(HallucinationGrader.GradeHallucination, grade_result)

        logger.info(f"Hallucination grade: {grade.is_grounded} - {grade.explanation}")

        return {
            **state,
            "is_grounded": grade.is_grounded,
            "iteration_count": state.get("iteration_count", 0) + 1,
        }

    def decide_after_grading(
        self, state: GraphState
    ) -> Literal["generate_answer", "END"]:
        """
        Decide whether to regenerate or end based on grading.

        Args:
            state (GraphState): Current state with is_grounded

        Returns:
            str: Next node - retry generation or end
        """
        logger.debug("---DECIDE AFTER GRADING---")

        is_grounded = state.get("is_grounded")
        iteration_count = state.get("iteration_count", 0)
        max_retries = 2  # Maximum retry attempts

        if is_grounded == "yes":
            logger.info("Answer is grounded - proceeding to END")
            return "END"

        if iteration_count >= max_retries:
            logger.warning(
                f"Max retries ({max_retries}) reached - accepting answer despite hallucination"
            )
            return "END"

        logger.info(
            f"Answer not grounded - regenerating (attempt {iteration_count + 1}/{max_retries})"
        )
        return "generate_answer"

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

        question = state.get("question")

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
        """Create workflow: analyze_intent → route → generate.

        Args:
            nodes: Nodes instance with intent analysis, routing, generation, and grading methods

        Returns:
            Compiled LangGraph StateGraph
        """
        workflow = StateGraph(GraphState)

        # Define nodes
        workflow.add_node("analyze_intent", nodes.analyze_intent)
        workflow.add_node("generate_answer", nodes.generate_answer)
        workflow.add_node("generate_conversational", nodes.generate_conversational)
        workflow.add_node("grade_hallucination", nodes.grade_hallucination)

        workflow.set_entry_point("analyze_intent")

        workflow.add_conditional_edges(
            "analyze_intent",
            nodes.route_question,
            {
                "general_chat": "generate_conversational",
                "insights_api": "generate_answer",
            },
        )
        workflow.add_edge("generate_answer", "grade_hallucination")

        workflow.add_conditional_edges(
            "grade_hallucination",
            nodes.decide_after_grading,
            {
                "generate_answer": "generate_answer",  # Retry generation
                "END": END,
            },
        )

        workflow.add_edge("generate_conversational", END)

        checkpointer = InMemorySaver()
        return workflow.compile(checkpointer=checkpointer)


def initialize_graph_state():
    """Initialize a new graph state with default values."""

    return GraphState(
        question="",
        generation="",
        insights=[],
        store_id=None,
        date=None,
        route="",
        iteration_count=0,
        insights_retrieved=False,
        is_grounded=None,
    )


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
