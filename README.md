# OneLab MVP 

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


## System Architecture
                    ┌──────────────┐
                    │     User     │
                    └──────┬───────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │  Tutor Chat API   │
                 │    /api/chat      │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │   SharedAIService │
                 └─────────┬─────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
 ┌───────────────┐                    ┌─────────────────┐
 │   ChromaDB    │                    │       LLM       │
 │ retrieve()    │                    │ ask_llm()       │
 └───────┬───────┘                    └────────┬────────┘
         │                                     │
         └───────────────┬─────────────────────┘
                         ▼
               ┌────────────────────┐
               │ Response + Mastery │
               │     Adjustment     │
               └─────────┬──────────┘
                         │
                         ▼
            ┌───────────────────────────┐
            │ Learner Knowledge Graph   │
            │      (ConceptNode)        │
            └───────────────────────────┘

## Research Paper Processing Pipeline
           ┌─────────────────────┐
           │   Paper Upload API  │
           │      /research      │
           └─────────┬───────────┘
                     │
                     ▼
             ┌───────────────┐
             │    PyMuPDF    │
             │Text Extraction│
             └──────┬────────┘
                    │
                    ▼
             ┌───────────────┐
             │   Chunking    │
             └──────┬────────┘
                    │
                    ▼
             ┌───────────────┐
             │   Embedding   │
             │ Generation    │
             └──────┬────────┘
                    │
                    ▼
             ┌───────────────┐
             │   ChromaDB    │
             │embed_and_store│
             └──────┬────────┘
                    │
                    ▼
             ┌───────────────┐
             │ Paper Summary │
             │   Generation  │
             └───────────────┘