# 🏪 Store Insights AI

A production-ready RAG (Retrieval-Augmented Generation) system that provides intelligent, natural language access to store performance data using LangGraph, LangChain, and Azure OpenAI.

## 🎯 Overview

Store Insights AI is an intelligent chatbot that answers questions about store performance, inventory, and operations using natural language. It automatically:

- **Extracts entities** (store IDs, dates) from user questions
- **Routes queries** to the appropriate handler (API lookup or conversational)
- **Retrieves relevant insights** from an external Store Insights API
- **Generates contextual answers** using Azure OpenAI/OpenAI
- **Caches responses** for 24 hours to optimize performance

## 🏗️ Architecture

```
┌─────────────────┐
│  Streamlit UI   │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP POST /v1/api/chat/ask
         ▼
┌─────────────────────────────────────────┐
│           FastAPI Backend               │
│  ┌───────────────────────────────────┐  │
│  │     LangGraph Workflow            │  │
│  │                                   │  │
│  │  1. Analyze Intent                │  │
│  │     └─> Extract store_id, date    │  │
│  │                                   │  │
│  │  2. Route Query                   │  │
│  │     ├─> insights_api              │  │
│  │     └─> general_chat              │  │
│  │                                   │  │
│  │  3. Generate Response             │  │
│  │     └─> Context-aware answer      │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │   Caching    │  │  Middleware  │   │
│  │   (TTL 24h)  │  │  - Logging   │   │
│  │              │  │  - Req ID    │   │
│  └──────────────┘  └──────────────┘   │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Store Insights API │
│  (External Service) │
└─────────────────────┘
```

### Workflow Details

1. **Intent Analysis**: Uses LLM with structured output to extract:
   - Store ID(s)
   - Date (with dynamic "today" calculation)
   - Query intent classification

2. **Query Routing**: Based on extracted entities:
   - If store_id + date present → Route to Insights API
   - Otherwise → Route to conversational handler

3. **Response Generation**:
   - **Insights Route**: Fetches data from external API, generates answer with sources
   - **Conversational Route**: Handles greetings, help, and general questions

## 📦 Installation

### Prerequisites
- Python 3.11+
- pip or poetry
- Azure OpenAI API key (or OpenAI API key)
- Access to Store Insights API

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd store_insights_ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
# Application Settings
APP_NAME=store-insights
APP_ENV=local
APP_DEBUG=false
HOST=0.0.0.0
PORT=8000

# LLM Provider (openai or azure)
LLM_PROVIDER=azure

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# Azure OpenAI Configuration (if using Azure)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4

# External Store Insights API
INSIGHTS_API_BASE_URL=https://api.example.com/v1
INSIGHTS_API_KEY=your-api-key
INSIGHTS_API_TIMEOUT_SECONDS=30

# Observability (Optional)
APPLICATION_INSIGHTS_CONNECTION_STRING=your-app-insights-connection
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider to use (`openai` or `azure`) | `azure` |
| `INSIGHTS_API_BASE_URL` | Base URL for Store Insights API | Required |
| `INSIGHTS_API_KEY` | API key for authentication | Required |
| `INSIGHTS_API_TIMEOUT_SECONDS` | API request timeout | `30` |

## 🚀 Usage

### Running the API

Start the FastAPI server:

```bash
# Development mode with auto-reload
uvicorn app.api.api:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.api.api:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Running the UI

Start the Streamlit interface:

```bash
cd ui
streamlit run app.py
```

The UI will open at http://localhost:8501

### API Endpoints

#### Health Check
```bash
GET /v1/api/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

#### Chat - Ask Question
```bash
POST /v1/api/chat/ask
```

**Request:**
```json
{
  "question": "What are the sales for store 100?"
}
```

**Response:**
```json
{
  "answer": "Store 100 had total sales of $150,000 with 1,200 transactions...",
  "metadata": {
    "store_id": 100,
    "date": "2024-10-09",
    "route": "insights_api"
  },
  "sources": [
    {
      "type": "recommendation",
      "store_id": 100,
      "title": "Sales Performance",
      "text": "Store 100 showed strong performance...",
      "metadata": {}
    }
  ]
}
```

#### Get Insights (Direct)
```bash
GET /v1/api/insights?store_id=100&date=2024-10-09&use_cache=true
```

**Response:**
```json
{
  "store_id": 100,
  "date": "2024-10-09",
  "insights": [
    {
      "type": "recommendation",
      "title": "Inventory Alert",
      "text": "Consider restocking high-demand items..."
    }
  ],
  "cached": false
}
```

#### Cache Statistics
```bash
GET /v1/api/insights/cache/stats
```

**Response:**
```json
{
  "cache_size": 42,
  "max_size": 1000,
  "ttl_seconds": 86400
}
```

#### Clear Cache
```bash
POST /v1/api/insights/cache/clear
```

## 📁 Project Structure

```
store_insights_ai/
├── app/
│   ├── api/
│   │   ├── api.py              # FastAPI application setup
│   │   ├── cache.py            # Caching implementation
│   │   ├── insights_client.py  # External API client
│   │   ├── middleware.py       # Logging & request ID middleware
│   │   └── routes/
│   │       ├── chat.py         # Chat endpoints
│   │       ├── health.py       # Health check
│   │       └── insights.py     # Insights endpoints
│   └── llm/
│       ├── __init__.py         # LLM module initialization
│       ├── base.py             # Base LLM interfaces
│       └── provider.py         # LLM provider factory
├── ui/
│   ├── app.py                  # Streamlit chat interface
│   ├── requirements.txt        # UI-specific dependencies
│   ├── README.md              # UI documentation
│   └── .streamlit/
│       └── config.toml        # Streamlit configuration
├── data/
│   └── stage.json             # Sample data
├── config.py                  # Centralized configuration
├── graph.py                   # LangGraph workflow definition
├── models.py                  # LLM chains and prompts
├── schemas.py                 # Pydantic schemas
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create from .env.example)
├── .env.example              # Environment template
└── README.md                 # This file
```

## 🔧 Development

### Code Organization

- **`models.py`**: LLM chain definitions (IntentAnalyzer, Router, Generator, ConversationalGenerator)
- **`graph.py`**: LangGraph state machine and workflow nodes
- **`config.py`**: Centralized settings using Pydantic
- **`app/api/`**: FastAPI application and routes
- **`app/llm/`**: LLM provider abstraction and factory

### Key Design Patterns

1. **Shared LLM Instances**: Only 2 LLM instances created for the entire application
   - Temperature 0.0 for structured output (intent, routing)
   - Temperature 0.7 for generation (answers)

2. **Provider Pattern**: LLMFactory dynamically registers only the configured provider
   ```python
   # Only registers OpenAI OR Azure, not both
   llm = get_llm(settings.llm_provider.value, temperature=0)
   ```

3. **Middleware Pipeline**:
   - `RequestIDMiddleware`: Adds unique X-Request-ID to all requests
   - `LoggingMiddleware`: Logs request/response with timing

4. **TTL Caching**: 24-hour cache for expensive API calls
   ```python
   cache = TTLCache(maxsize=1000, ttl=86400)  # 24 hours
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_graph.py
```

## 💾 Caching Strategy

### Overview
The system implements a 24-hour TTL (Time To Live) cache for Store Insights API responses.

### Cache Configuration
- **Max Size**: 1000 entries
- **TTL**: 86400 seconds (24 hours)
- **Implementation**: In-memory using `cachetools.TTLCache`

### Cache Key Format
```python
f"{store_id}:{date}"  # Example: "100:2024-10-09"
```

### Cache Behavior
- **On Hit**: Returns cached data, sets `cached=true` in response
- **On Miss**: Fetches from API, stores in cache, sets `cached=false`
- **Expiration**: Automatic after 24 hours
- **Manual Clear**: Available via API endpoint

### Cache Statistics
Monitor cache performance:
```bash
GET /v1/api/insights/cache/stats
```

### Clearing Cache
```bash
POST /v1/api/insights/cache/clear
```

## 📊 Logging & Monitoring

### Request Logging
Every request is logged with:
- Request ID (X-Request-ID header)
- HTTP method and path
- Response status code
- Request duration

**Log Format:**
```
→ POST /v1/api/chat/ask
← POST /v1/api/chat/ask 200 (1.234s)
```

### Request ID Tracking
Each request gets a unique UUID:
- Automatically generated if not provided
- Available in response headers
- Useful for distributed tracing

### LLM Provider Logging
```
INFO:root:Registering provider: azure
INFO:root:Created Azure LLM client successfully.
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Provider Not Registered Error
```
ValueError: Provider not registered: azure
```

**Solution**: Ensure `app/llm/__init__.py` imports the provider module:
```python
from . import provider  # Triggers provider registration
```

#### 2. Connection Refused
```
Error: Connection error: [Errno 111] Connection refused
```

**Solution**: 
- Ensure the FastAPI server is running
- Check that the API URL in the UI matches the backend (default: `http://localhost:8000/v1/api`)
- Test connection using the "🔗 Test Connection" button in the UI

#### 3. Missing API Key
```
Error: Missing required environment variable: AZURE_OPENAI_API_KEY
```

**Solution**: Add the required environment variables to your `.env` file

#### 4. Timeout Error
```
Error: Request timeout after 60s
```

**Solution**: 
- Check external API availability
- Increase timeout in config: `INSIGHTS_API_TIMEOUT_SECONDS=60`
- Review network connectivity

### Debug Mode

Enable debug logging:
```env
APP_DEBUG=true
```

This will:
- Show detailed error traces
- Log all LLM calls and responses
- Display cache hits/misses

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the development team

---

Built with ❤️ using LangChain, LangGraph, FastAPI, and Streamlit
