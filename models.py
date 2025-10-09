from typing import Literal, Optional
from datetime import date
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseChatModel


class QuestionRephraser:
    """Rephrases user questions for better clarity and entity extraction."""

    class RephrasedQuestion(BaseModel):
        """Rephrased question with confidence score."""

        rephrased_question: str = Field(
            description="The rephrased question with improved clarity"
        )
        needs_rephrasing: bool = Field(
            description="True if the question was actually rephrased, False if original was clear"
        )
        confidence: Literal["high", "medium", "low"] = Field(
            description="Confidence that the rephrased question captures user intent"
        )

    system = """You are an expert at rephrasing retail store questions for maximum clarity.

    Your task:
    1. Identify vague or ambiguous questions and rephrase them to be more specific
    2. Preserve the user's intent and all mentioned entities (store IDs, dates, etc.)
    3. Add context if the question is too brief (e.g., "sales" → "What are the sales for this store?")
    4. Fix grammar or spelling issues
    5. If the question is already clear, return it unchanged with needs_rephrasing=False

    Examples:
    - "sales for 100" → "What are the sales for store 100?"
    - "yesterday?" → "What happened yesterday?" (low confidence - needs more context)
    - "why low" → "Why are metrics low?" (medium confidence)
    - "Show me insights for store 50 from yesterday" → (unchanged, already clear)
    - "What are the sales trends for store 100?" → (unchanged, already clear)

    Mark confidence as:
    - high: Question is specific with clear entities
    - medium: Question is clear but could use more context
    - low: Question is very vague and may need human clarification
    """

    rephraser_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Original question: {question}"),
        ]
    )

    @staticmethod
    def get_model(llm: BaseChatModel):
        """Create question rephraser chain with provided LLM instance."""
        structured_llm = llm.with_structured_output(QuestionRephraser.RephrasedQuestion)
        return QuestionRephraser.rephraser_prompt | structured_llm


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

    # Get today's date for prompt context
    current_date = date.today().isoformat()

    # Prompt template with dynamic current_date
    system = f"""You are an expert at analyzing retail store questions and extracting key parameters.

    Today's date is: {current_date}

    Your task is to extract:
    1. **store_id** - The numeric store identifier if mentioned (e.g., "store 100" → "100", "site 50" → "50")
    2. **date** - The date in YYYY-MM-DD format if mentioned
       - For relative dates like "yesterday", calculate based on today's date ({current_date})
       - For "today" use {current_date}
       - For "yesterday" subtract 1 day from {current_date}
       - For specific dates like "October 1st 2025" use 2025-10-01
    3. **needs_insights** - True if answering requires store data, False for greetings/general questions

    Examples (assuming today is {current_date}):
    - "What are the sales for store 100?" → store_id="100", date=None, needs_insights=True
    - "Show me insights for store 50 from yesterday" → store_id="50", date=<yesterday's date>, needs_insights=True
    - "How did store 200 perform on October 1st 2025?" → store_id="200", date="2025-10-01", needs_insights=True
    - "What stores have low inventory?" → store_id=None, date=None, needs_insights=True
    - "Hello, how are you?" → store_id=None, date=None, needs_insights=False
    - "What can you do?" → store_id=None, date=None, needs_insights=False

    Be precise with extraction - only extract what's explicitly mentioned or clearly implied.
    """

    intent_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )

    @staticmethod
    def get_model(llm: BaseChatModel):
        """Create intent analyzer chain with provided LLM instance."""
        structured_llm = llm.with_structured_output(IntentAnalyzer.ExtractedIntent)
        return IntentAnalyzer.intent_prompt | structured_llm


class Router:
    """Routes user questions to appropriate handling: store insights API or general conversation."""

    class RouteQuery(BaseModel):
        """Route a user query to the most relevant datasource."""

        datasource: Literal["insights_api", "general_chat"] = Field(
            ...,
            description="Route to insights_api for store-related questions, general_chat otherwise.",
        )

    # Prompt
    system = """You are an expert at routing user questions about retail store operations and insights.
    Your task is to determine if a question should be answered using:
    1. **insights_api** - Store insights and recommendations data (sales, inventory, operations, performance metrics)
    2. **general_chat** - General conversation not requiring store data

    Route to **insights_api** if the question involves:
    - Store performance, sales, revenue, or KPIs
    - Inventory levels, stock issues, or product availability
    - Customer behavior, traffic, or conversion rates
    - Store operations, staffing, or efficiency
    - Recommendations or actions for specific stores
    - Trends, patterns, or comparisons across stores or time periods
    - Any question asking "what", "why", or "how" about store metrics

    Route to **general_chat** if the question is:
    - A greeting or casual conversation
    - Asking about your capabilities
    - A completely unrelated topic (weather, sports, etc.)
    - Small talk that doesn't need store data

    Examples:
    - "What are the sales trends for store 100?" → insights_api
    - "Show me recommendations for underperforming stores" → insights_api
    - "Why did store 50 have low conversion yesterday?" → insights_api
    - "Hello, how are you?" → general_chat
    - "What can you help me with?" → general_chat
    - "Tell me about the weather" → general_chat
    """
    route_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )

    @staticmethod
    def get_model(llm: BaseChatModel):
        """Create router chain with provided LLM instance."""
        structured_llm = llm.with_structured_output(Router.RouteQuery)
        return Router.route_prompt | structured_llm


class Generator:
    """Generates answers based on store insights and recommendations."""

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a specialized retail analytics assistant helping store managers and executives understand their store performance.

                  Your role:
                  - Analyze store insights, recommendations, and performance data
                  - Provide clear, actionable answers based on the provided context
                  - Reference specific insights by their store ID when relevant
                  - Be concise but thorough in your analysis
                  - If trends or patterns exist across multiple stores, highlight them
                  - Always ground your answers in the provided data

                  Important rules:
                  - ONLY use information from the provided context (insights and recommendations)
                  - If the answer isn't in the context, clearly state "I don't have that information in the current insights"
                  - Never make up data or statistics
                  - For store-specific questions, focus on that store's data
                  - Keep responses professional and focused on retail operations
                """,
            ),
            (
                "human",
                """Based on the following store insights and recommendations, please answer the question.

                  Context (Store Insights & Recommendations):
                  {context}

                  Question: {question}

                  Provide a clear, data-driven answer based only on the context above:
                """,
            ),
        ]
    )

    @staticmethod
    def get_model(llm: BaseChatModel):
        """Create generator chain with provided LLM instance."""
        return Generator.prompt | llm | StrOutputParser()


class ConversationalGenerator:
    """Generates conversational responses for general chat (greetings, help requests, etc.)."""

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a friendly retail analytics assistant for a store insights system.

                  When users greet you or ask general questions (not about specific store data):
                  - Be warm and professional
                  - Explain your capabilities: analyzing store insights, recommendations, performance data
                  - Offer examples of questions you can answer
                  - Keep responses concise

                  Example capabilities to mention:
                  - Analyze store performance metrics and trends
                  - Review insights and recommendations for specific stores
                  - Compare performance across stores or time periods
                  - Identify patterns in sales, inventory, or operations
                  - Answer questions about specific stores or dates

                  Do NOT provide actual store data in general conversation - only explain what you can do.
                """,
            ),
            (
                "human",
                "{question}",
            ),
        ]
    )

    @staticmethod
    def get_model(llm: BaseChatModel):
        """Create conversational chain with provided LLM instance."""
        return ConversationalGenerator.prompt | llm | StrOutputParser()


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
