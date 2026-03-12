# OneLab MVP - GSoC 2026 proof of concept

OneLab demonstrates a minimal but production-minded architecture for an AI-powered personalized learning + research assistant.

## Setup

1. Create and activate a virtual environment
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy environment template:
   - `.env.example` -> `.env`
4. Run migrations:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
5. Seed concepts:
   - `python manage.py seed_concepts`
6. Start server:
   - `python manage.py runserver`


## Architecture (ASCII)

User -> Tutor Chat -> SharedAIService -> ChromaDB + LLM -> ConceptNode update

Detailed flow:

User
  |
  v
Tutor Chat API (/api/chat)
  |
  v
SharedAIService
  |---- retrieve(query) from ChromaDB (user_<id>)
  |---- ask_llm(messages, context)
  v
Response + mastery adjustment
  |
  v
ConceptNode (Learner Knowledge Graph)

Paper Upload API (/research)
  |
  v
PyMuPDF text extraction -> chunking -> embed_and_store() -> summary generation
