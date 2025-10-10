from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseChatModel

from app.prompts.model_prompts import (
    INTENT_ANALYZER_PROMPT,
    ROUTER_PROMPT,
    GENERATOR_PROMPT,
    CONVERSATIONAL_PROMPT,
    HALLUCINATION_GRADER_PROMPT,
)


class IntentAnalyzer:
    """Analyzes user questions to extract store_id and date parameters."""

    class ExtractedIntent(BaseModel):
        """Extracted store and date information from user question."""

        store_id: Optional[str] = Field(
            default=None,
            description="Store ID mentioned in the question (e.g., '100', 'store 50'). Extract only the numeric ID.",
        )
        date: Optional[str] = Field(
            default=None,
            description="Date mentioned in the question in YYYY-MM-DD format (e.g., '2025-10-01'). Convert relative dates like 'yesterday', 'today' to actual dates.",
        )
        needs_insights: bool = Field(
            default=False,
            description="True if the question requires store insights data to answer, False for general questions.",
        )

    @staticmethod
    def get_model(llm: BaseChatModel):
        """Create intent analyzer chain with provided LLM instance."""
        structured_llm = llm.with_structured_output(IntentAnalyzer.ExtractedIntent)
        return INTENT_ANALYZER_PROMPT | structured_llm


class Router:
    """Routes user questions to appropriate handling: store insights API or general conversation."""

    class RouteQuery(BaseModel):
        """Route a user query to the most relevant datasource."""

        datasource: Literal["insights_api", "general_chat"] = Field(
            ...,
            description="Route to insights_api for store-related questions, general_chat otherwise.",
        )

    @staticmethod
    def get_model(llm: BaseChatModel):
        """Create router chain with provided LLM instance."""
        structured_llm = llm.with_structured_output(Router.RouteQuery)
        return ROUTER_PROMPT | structured_llm


class Generator:
    """Generates answers based on store insights and recommendations."""

    @staticmethod
    def get_model(llm: BaseChatModel):
        """Create generator chain with provided LLM instance."""
        return GENERATOR_PROMPT | llm | StrOutputParser()


class ConversationalGenerator:
    """Generates conversational responses for general chat (greetings, help requests, etc.)."""

    @staticmethod
    def get_model(llm: BaseChatModel):
        """Create conversational chain with provided LLM instance."""
        return CONVERSATIONAL_PROMPT | llm | StrOutputParser()


class HallucinationGrader:
    """Grades whether the generated answer is grounded in the provided facts/context."""

    class GradeHallucination(BaseModel):
        """Binary score for hallucination check."""

        is_grounded: Literal["yes", "no"] = Field(
            description="Is the answer grounded in the facts? 'yes' or 'no'"
        )
        explanation: str = Field(
            description="Brief explanation of why the answer is or isn't grounded"
        )

    @staticmethod
    def get_model(llm: BaseChatModel):
        """Create hallucination grader chain with provided LLM instance."""
        structured_llm = llm.with_structured_output(
            HallucinationGrader.GradeHallucination
        )
        return HALLUCINATION_GRADER_PROMPT | structured_llm


class HumanFeedbackRequest(BaseModel):
    """Request for human clarification or confirmation."""

    request_type: Literal["clarification", "confirmation", "selection"] = Field(
        description="Type of human input needed"
    )
    message: str = Field(
        description="Message to show the user explaining what input is needed"
    )
    options: Optional[list[str]] = Field(
        default=None, description="Optional list of choices for the user to select from"
    )
    current_values: dict = Field(
        default_factory=dict,
        description="Current extracted values that may need confirmation",
    )
