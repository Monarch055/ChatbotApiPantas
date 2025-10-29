# Chatbot API

A RESTful API for intelligent chatbot functionality using Python, FastAPI, OpenAI GPT, and Supabase as a knowledge base with RAG (Retrieval-Augmented Generation) using vector similarity search.

## Features

- 🤖 **OpenAI Integration**: Uses GPT models for intelligent responses
- 🚀 **FastAPI Framework**: High-performance async API framework
- 📝 **Conversation History**: Maintains conversation context
- 🔧 **Configurable**: Customizable system prompts and parameters
- 📊 **Auto Documentation**: Interactive API docs with Swagger UI
- 🔒 **CORS Support**: Cross-origin resource sharing enabled
- 🏥 **Health Checks**: Built-in health monitoring endpoints
- 🗄️ **Supabase Integration**: PostgreSQL database for knowledge base and chat history
- 🔍 **RAG with Vector Search**: Smart context retrieval using embeddings and pgvector
- 📚 **Knowledge Base**: Store and retrieve documents with semantic search

## Project Structure

```
ChatbotAPI/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application factory
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py                 # Chat endpoints
│   │   ├── health.py               # Health check endpoints
│   │   └── documents.py            # Document management endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py               # Configuration settings
│   ├── db/
│   │   ├── __init__.py
│   │   └── supabase.py             # Supabase client
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py              # Pydantic models
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── chat_session_repository.py  # Chat persistence
│   │   └── faq_repository.py       # FAQ data access
│   └── services/
│       ├── __init__.py
│       ├── chat_service.py         # Chat logic with RAG
│       ├── embedding_service.py    # Vector embeddings and search
│       └── faq_service.py          # FAQ service
├── database/
│   ├── schema.sql                  # Base database schema
│   ├── vector_schema.sql           # pgvector setup and functions
│   ├── seed_data.sql               # Sample FAQ data
│   └── sample_documents.sql        # Sample knowledge base documents
├── test-website/
│   ├── index.html                  # Test chat interface
│   └── script.js                   # Frontend logic
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── run.py                          # Application entry point
├── serve_test_website.py           # Simple server for test website
├── check_documents.py              # Utility to check embeddings
├── generate_embeddings.py          # Generate embeddings for documents
└── README.md                       # This file
```

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd ChatbotAPI

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
copy .env.example .env

# Edit .env file with your credentials
```

Required environment variables in `.env`:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.7

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_or_service_role_key

# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

**Important**: Use Supabase **service_role** key (not anon key) to bypass Row Level Security for API operations.

### 3. Setup Supabase Database

#### a. Enable pgvector Extension

Go to Supabase SQL Editor and run:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

#### b. Run Database Scripts

In Supabase SQL Editor, run these files in order:
1. `database/schema.sql` - Base tables
2. `database/vector_schema.sql` - Vector search setup
3. `database/seed_data.sql` - Sample FAQ data (optional)
4. `database/sample_documents.sql` - Sample documents (optional)

#### c. Configure Row Level Security

For development, disable RLS or create permissive policies:
```sql
-- Option 1: Disable RLS (development only)
ALTER TABLE chat_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages DISABLE ROW LEVEL SECURITY;
ALTER TABLE documents DISABLE ROW LEVEL SECURITY;

-- Option 2: Create permissive policies (recommended)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable all access" ON documents FOR ALL TO authenticated, anon USING (true) WITH CHECK (true);
```

Or use the **service_role** key in your `.env` which bypasses RLS.

### 4. Generate Embeddings for Knowledge Base

After setting up the database and inserting documents:
```bash
python generate_embeddings.py
```

This generates OpenAI embeddings for all documents, enabling semantic search.

### 5. Run the API

```bash
# Run the development server
python run.py
```

The API will be available at:
- **Main API**: http://127.0.0.1:8000
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### 6. Test the Chatbot

**Option 1: Use Swagger UI**
1. Go to http://127.0.0.1:8000/docs
2. Find POST `/api/v1/chat/`
3. Click "Try it out"
4. Send a message:
```json
{
  "message": "Hello, how can you help me?"
}
```

**Option 2: Use the Test Website**
```bash
python serve_test_website.py
```
This opens a chat interface in your browser.

## API Endpoints

### Chat Endpoints

#### POST `/api/v1/chat/`
Send a message to the chatbot and receive a response.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "conversation_history": [
    {
      "role": "user",
      "content": "Previous message",
      "timestamp": "2023-01-01T12:00:00"
    }
  ],
  "system_prompt": "You are a helpful assistant",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "response": "Hello! I'm doing well, thank you for asking...",
  "conversation_id": "uuid-string",
  "timestamp": "2023-01-01T12:00:00",
  "model_used": "gpt-3.5-turbo",
  "tokens_used": 45
}
```

#### GET `/api/v1/chat/models`
Get available AI models.

### Health Endpoints

#### GET `/health`
Health check endpoint.

#### GET `/`
API information and welcome message.

## Usage Examples

### Simple Chat Request

```python
import requests

response = requests.post("http://127.0.0.1:8000/api/v1/chat/", json={
    "message": "What is the capital of France?"
})

print(response.json())
```

### Chat with History

```python
import requests

response = requests.post("http://127.0.0.1:8000/api/v1/chat/", json={
    "message": "What about Germany?",
    "conversation_history": [
        {
            "role": "user",
            "content": "What is the capital of France?"
        },
        {
            "role": "assistant", 
            "content": "The capital of France is Paris."
        }
    ]
})

print(response.json())
```

### Custom System Prompt

```python
import requests

response = requests.post("http://127.0.0.1:8000/api/v1/chat/", json={
    "message": "Tell me about the weather",
    "system_prompt": "You are a weather expert. Provide detailed meteorological information.",
    "temperature": 0.3,
    "max_tokens": 500
})

print(response.json())
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `MODEL_NAME` | OpenAI model to use | `gpt-3.5-turbo` |
| `MAX_TOKENS` | Maximum response length | `1000` |
| `TEMPERATURE` | Response creativity (0-2) | `0.7` |
| `SUPABASE_URL` | Your Supabase project URL | Required |
| `SUPABASE_ANON_KEY` | Supabase anon or service_role key | Required |
| `API_HOST` | API host address | `127.0.0.1` |
| `API_PORT` | API port number | `8000` |
| `DEBUG` | Enable debug mode | `True` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000,http://localhost:8080` |
| `WHATSAPP_NUMBER` | WhatsApp support number | Optional |

## Integrating with Your Website

### JavaScript/Frontend Example

```javascript
async function sendMessage(message, history = []) {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_history: history
            })
        });
        
        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error('Error calling chatbot API:', error);
        return 'Sorry, there was an error processing your request.';
    }
}

// Usage
sendMessage("Hello!")
    .then(response => console.log(response));
```

## Error Handling

The API returns structured error responses:

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "timestamp": "2023-01-01T12:00:00"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (API key issues)
- `429`: Rate limit exceeded
- `500`: Internal server error

## How It Works: RAG (Retrieval-Augmented Generation)

This chatbot uses RAG to provide accurate, context-aware responses based on your knowledge base:

1. **User sends a message** → API receives the chat request
2. **Generate query embedding** → OpenAI creates a vector representation of the user's question
3. **Search similar documents** → Supabase's pgvector finds relevant documents using cosine similarity
4. **Retrieve context** → Top matching documents are retrieved from the knowledge base
5. **Construct prompt** → System prompt is enhanced with retrieved context
6. **Generate response** → OpenAI generates a response based on the context and user question
7. **Return answer** → API returns the contextual response to the user

## Utility Scripts

### Check Documents and Embeddings
```bash
python check_documents.py
```
Displays all documents in your knowledge base and whether they have embeddings.

### Generate Embeddings
```bash
python generate_embeddings.py
```
Generates OpenAI embeddings for all documents that don't have them. Required for semantic search.

### Test Website
```bash
python serve_test_website.py
```
Launches a simple web interface to test your chatbot.

## Troubleshooting

### "No documents found" or Generic Responses
- **Issue**: Chatbot gives generic answers instead of using your knowledge base
- **Solution**: 
  1. Check if documents exist: `python check_documents.py`
  2. Generate embeddings: `python generate_embeddings.py`
  3. Verify pgvector extension is enabled in Supabase

### "type 'vector' does not exist"
- **Issue**: pgvector extension not enabled
- **Solution**: Run `CREATE EXTENSION IF NOT EXISTS vector;` in Supabase SQL Editor

### "Row Level Security Policy Violation"
- **Issue**: RLS blocking database operations
- **Solution**: Use service_role key or disable RLS for development tables

### "OpenAI Quota Exceeded" (429 Error)
- **Issue**: No credits or rate limit reached
- **Solution**: Add credits at https://platform.openai.com/account/billing

### "Invalid role value 'string'" (400 Error)
- **Issue**: Incorrect role in conversation_history
- **Solution**: Use only: `"user"`, `"assistant"`, or `"system"` (not `"string"`, `"users"`, etc.)

## Development

### Adding New Endpoints

1. Create new router in `app/api/`
2. Add models in `app/models/schemas.py`
3. Add business logic in `app/services/`
4. Include router in `app/main.py`

### Adding Documents to Knowledge Base

Insert documents directly in Supabase or via SQL:
```sql
INSERT INTO documents (title, content, document_type, tags)
VALUES (
    'Your Document Title',
    'Your document content here...',
    'sop',
    ARRAY['tag1', 'tag2']
);
```

Then generate embeddings:
```bash
python generate_embeddings.py
```

## Deployment

### Using Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "run.py"]
```

### Production Considerations

- Use environment variables for configuration
- Set up proper logging
- Use a production ASGI server like Gunicorn
- Implement rate limiting
- Add authentication if needed
- Set up monitoring and health checks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.