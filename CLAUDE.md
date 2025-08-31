# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the yak-hole project.

## Project Overview

yak-hole is a personal RAG (Retrieval Augmented Generation) system that allows users to query their personal notes (markdown and PDF format) using Ollama through a React Native chat interface. The system is designed to run on private machines while keeping the codebase open for others to train their own yak-hole instances.

## Architecture

### Frontend (React Native)
- **Technology**: React Native with TypeScript
- **Purpose**: Chat interface for querying notes
- **Key Features**:
  - Chat-based interaction
  - Note search and discovery
  - Idea combination and synthesis
  - Style-aware responses

### Backend (Python/FastAPI)
- **Technology**: Python with FastAPI
- **Purpose**: RAG system integration with Ollama
- **Key Features**:
  - Document ingestion (markdown, PDF)
  - Vector embeddings for semantic search
  - Ollama integration for LLM responses
  - API endpoints for chat interface

### Document Processing
- **Input Formats**: Markdown (.md), PDF (.pdf)
- **Processing**: Text extraction, chunking, embedding generation
- **Storage**: Local vector database for privacy

## Development Commands

### React Native App
```bash
# Install dependencies
npm install

# Start Metro bundler
npm start

# Run on Android
npm run android

# Run on iOS
npm run ios

# Run tests
npm test

# Lint code
npm run lint
```

### Backend Services
```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
python -m uvicorn main:app --reload

# Or use npm script from root
npm run backend
```

### Document Ingestion
```bash
# Process notes directory
python backend/ingest_notes.py --notes-dir /path/to/your/notes

# Update embeddings
python backend/update_embeddings.py
```

## Project Structure

```
yak-hole/
├── README.md                 # Project documentation
├── package.json             # React Native dependencies
├── CLAUDE.md               # This file
├── .gitignore              # Git ignore patterns
├── app/                    # React Native app
│   ├── components/         # Reusable components
│   ├── screens/           # App screens
│   ├── services/          # API communication
│   └── utils/             # Utility functions
├── backend/               # Python backend
│   ├── main.py           # FastAPI application
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   ├── routers/          # API routes
│   └── requirements.txt  # Python dependencies
└── docs/                 # Documentation
```

## Key Features

### Privacy-First Design
- All processing happens locally
- No data leaves the user's machine
- Notes remain private and secure

### Semantic Search
- Vector embeddings for note content
- Contextual understanding of queries
- Similarity-based retrieval

### Style Preservation
- Learns from user's writing style
- Maintains voice and tone in responses
- Adapts to personal preferences

### Cross-Platform
- React Native for mobile and desktop
- Works on iOS, Android, and web
- Consistent experience across devices

## Development Guidelines

### Code Style
- Use TypeScript for React Native components
- Follow React Native best practices
- Use Python type hints in backend code
- Implement proper error handling

### Testing
- Unit tests for utility functions
- Integration tests for API endpoints
- Component tests for React Native UI

### Documentation
- Document API endpoints with FastAPI auto-docs
- Comment complex algorithms
- Update README for setup instructions

## Deployment

### Local Development
1. Set up Ollama on local machine
2. Install React Native development environment
3. Set up Python backend environment
4. Configure note directories

### Production
- Docker containers for easy deployment
- Environment-based configuration
- Backup strategies for embeddings

## Security Considerations

- No external API calls for note content
- Local-only processing pipeline
- Secure file access permissions
- Input validation for all endpoints

When working on yak-hole, prioritize privacy, local processing, and user experience. The system should feel like a natural extension of the user's note-taking workflow while providing powerful AI-assisted search and synthesis capabilities.