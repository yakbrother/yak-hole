# 🕳️ yak-hole

A privacy-first RAG (Retrieval Augmented Generation) system for querying your personal notes using Ollama with a React Native chat interface. Transform your markdown and PDF notes into an intelligent, searchable knowledge base that understands your writing style and helps you discover connections between your ideas.

## ✨ Features

- **Privacy-First**: All processing happens locally on your machine
- **Multi-Format Support**: Works with Markdown (.md) and PDF (.pdf) files
- **Semantic Search**: Uses vector embeddings for contextual note retrieval
- **Style-Aware**: Learns and maintains your writing voice and tone
- **Cross-Platform**: React Native app works on iOS, Android, and web
- **Local LLM**: Powered by Ollama for complete offline functionality
- **Idea Synthesis**: Combines related notes to generate new insights

## 🚀 Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) (v16 or later)
- [Python](https://python.org/) (3.8 or later)
- [Ollama](https://ollama.ai/) installed and running
- React Native development environment ([setup guide](https://reactnative.dev/docs/environment-setup))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd yak-hole
   ```

2. **Install dependencies**
   ```bash
   # Frontend dependencies
   npm install
   
   # Backend dependencies
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. **Set up Ollama**
   ```bash
   # Install and start Ollama
   ollama pull llama2  # or your preferred model
   ollama serve
   ```

4. **Configure your notes directory**
   ```bash
   # Copy example config and edit
   cp backend/config.example.py backend/config.py
   # Edit backend/config.py to point to your notes directory
   ```

5. **Process your notes**
   ```bash
   python backend/ingest_notes.py --notes-dir /path/to/your/notes
   ```

6. **Start the application**
   ```bash
   # Terminal 1: Start backend
   npm run backend
   
   # Terminal 2: Start React Native
   npm start
   
   # Terminal 3: Run on your platform
   npm run ios     # for iOS
   npm run android # for Android
   ```

## 📱 Usage

1. **Chat Interface**: Ask questions about your notes in natural language
2. **Semantic Search**: Find related concepts even if exact keywords don't match
3. **Note Synthesis**: Ask to combine ideas from multiple notes
4. **Style Queries**: Request responses in your personal writing style

### Example Queries

- "What did I write about machine learning last month?"
- "Combine my thoughts on productivity with my notes on time management"
- "Find connections between my project ideas and market research"
- "Summarize my meeting notes from this week in my writing style"

### Chat History & Data Management

**Chat Storage:**
- Conversations automatically saved locally
- Search previous chats: "Show my conversation about productivity"
- Export chats to markdown or JSON
- Chat backup/restore functionality

**Adding New Notes:**
- Drop new files in your notes directory
- Run: `python backend/ingest_notes.py --incremental`
- Or enable auto-processing: `python backend/ingest_notes.py --watch`
- New embeddings added in ~5-30 seconds per note

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  React Native   │    │   FastAPI        │    │     Ollama      │
│  Chat Interface │◄──►│   Backend        │◄──►│   Local LLM     │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Vector Database │
                       │  (Your Notes)   │
                       └─────────────────┘
```

### Components

- **Frontend**: React Native app with chat interface
- **Backend**: FastAPI server for RAG processing and Ollama integration
- **Vector DB**: Local embeddings of your notes for semantic search
- **Ollama**: Local LLM for generating contextual responses

## 🔧 Configuration

### Backend Configuration (`backend/config.py`)

```python
# Notes directory
NOTES_DIR = "/path/to/your/notes"

# Supported file types
SUPPORTED_EXTENSIONS = [".md", ".pdf", ".txt"]

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama2"

# Vector database settings
VECTOR_DB_PATH = "./data/vector_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chat storage settings
CHAT_HISTORY_PATH = "./data/chat_history"
ENABLE_CHAT_STORAGE = True
MAX_CHAT_HISTORY = 1000  # Number of conversations to keep
```

### React Native Configuration

The app automatically connects to the backend at `http://localhost:8000`. For mobile devices, update the API endpoint in `app/services/api.ts`.

## 📁 Project Structure

```
yak-hole/
├── README.md                 # This file
├── package.json             # React Native dependencies
├── CLAUDE.md               # Development guidelines
├── app/                    # React Native application
│   ├── components/         # Reusable UI components
│   ├── screens/           # App screens (Chat, Settings)
│   ├── services/          # API communication layer
│   └── utils/             # Utility functions
├── backend/               # Python RAG backend
│   ├── main.py           # FastAPI application entry
│   ├── models/           # Data models and schemas
│   ├── services/         # RAG processing logic
│   ├── routers/          # API route handlers
│   ├── ingest_notes.py   # Note processing script
│   └── requirements.txt  # Python dependencies
└── docs/                 # Additional documentation
```

## 🛠️ Development

### Adding New File Types

1. Update `SUPPORTED_EXTENSIONS` in `backend/config.py`
2. Add processor in `backend/services/document_processor.py`
3. Test with sample files

### Customizing the Chat Interface

- Modify components in `app/components/`
- Update chat logic in `app/screens/ChatScreen.tsx`
- Customize styling in component files

### Improving RAG Performance

- Experiment with different embedding models
- Adjust chunk sizes in document processing
- Fine-tune retrieval parameters

## ⚡ Performance & Optimization

### Embedding Processing Times

**MacBook Air M1/M2:**
- 500 notes: ~5-10 minutes
- 1000 notes: ~15-25 minutes  
- 2000+ notes: ~30-60 minutes

**MacBook Pro/iMac:**
- 500 notes: ~3-7 minutes
- 1000 notes: ~10-18 minutes
- 2000+ notes: ~20-45 minutes

**Factors affecting speed:**
- Total text volume (not just file count)
- PDF complexity (scanned images vs searchable text)
- Available RAM (8GB minimum, 16GB+ recommended)
- Background processes consuming CPU

### Optimization Strategies

**For Large Note Collections (1000+ files):**
```python
# In backend/config.py
CHUNK_SIZE = 500          # Smaller chunks for better retrieval
BATCH_SIZE = 32          # Process more files simultaneously
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fastest model
```

**Hardware Optimizations:**
- Close other applications during initial processing
- Use SSD storage for faster I/O
- Ensure adequate cooling (MacBook Air may throttle)
- Process during off-peak hours

**Incremental Processing:**
- Only new/modified files are re-processed
- Use `--incremental` flag: `python ingest_notes.py --incremental`
- Track processing with: `python ingest_notes.py --verbose`
- Watch mode: `python ingest_notes.py --watch` (auto-processes new files)

### Cloud & Server Deployment

**Option 1: Backend on Server, App Local**
```bash
# Deploy backend to cloud server
# Update app/services/api.ts with server URL
const API_BASE_URL = 'https://your-server.com:8000'
```

**Option 2: Full Cloud Deployment**
```yaml
# docker-compose.yml for cloud deployment
services:
  backend:
    build: ./backend
    environment:
      - NOTES_DIR=/app/notes
    volumes:
      - ./your-notes:/app/notes:ro
  
  app:
    build: ./app
    ports:
      - "3000:3000"
```

**Privacy Considerations for Cloud:**
- ⚠️ **Notes data leaves your machine**
- Consider encrypting notes before upload
- Use private cloud/VPN for sensitive content
- Self-hosted options maintain more privacy

**Hybrid Approach:**
- Keep sensitive notes local
- Put general knowledge/reference notes on server
- Configure multiple note directories with different privacy levels

## 📚 Data Management

### Adding New Notes

**Real-time Processing:**
```bash
# Watch mode - automatically processes new files
python backend/ingest_notes.py --watch
```

**Manual Updates:**
```bash
# Process only new/modified files (fast)
python backend/ingest_notes.py --incremental

# Force reprocess specific directory
python backend/ingest_notes.py --path /specific/folder --force

# Check what needs updating
python backend/ingest_notes.py --dry-run
```

**Performance:**
- New single note: ~5-30 seconds to embed
- Batch of 10 notes: ~1-3 minutes
- Modified existing note: ~10-15 seconds to re-embed

### Chat History Management

**Automatic Storage:**
- All conversations saved in `./data/chat_history/`
- Indexed by date and topic keywords
- Searchable through chat interface

**Chat Commands:**
```bash
# In chat interface
"/history" - Show recent conversations
"/search productivity" - Find chats about productivity
"/export today" - Export today's chats to markdown
"/clear old" - Remove chats older than 30 days
```

**Manual Management:**
```bash
# Export all chats
python backend/export_chats.py --format markdown --output ./exports/

# Backup chat database
python backend/backup_chats.py --destination ./backups/

# Import chats from backup
python backend/restore_chats.py --source ./backups/chat_backup.json
```

### Database Maintenance

**Regular Cleanup:**
```bash
# Remove orphaned embeddings (notes no longer exist)
python backend/cleanup_db.py --remove-orphaned

# Optimize vector database
python backend/optimize_db.py --compact

# Check database health
python backend/check_db.py --verify
```

**Storage Management:**
- Vector DB grows ~1-5MB per 100 notes
- Chat history ~10KB per conversation
- Automatic cleanup of old temporary files
- Configurable retention policies

## 💾 Disk Space Requirements

### Base Installation
```
Application files:          ~50-100MB
Python dependencies:       ~200-500MB
Node.js dependencies:      ~100-300MB
Ollama models:             1-7GB (varies by model)
Total base install:        ~1.5-8GB
```

### Data Storage Estimates

**Vector Database (Embeddings):**
```
Small collection (500 notes):      5-25MB
Medium collection (2,000 notes):   20-100MB
Large collection (10,000 notes):   100-500MB
Massive collection (50,000 notes): 500MB-2.5GB
```

**Chat History:**
```
Light usage (100 chats):          1MB
Regular usage (1,000 chats):      10MB
Heavy usage (10,000 chats):       100MB
Power user (100,000 chats):       1GB
```

**Original Notes (your files):**
```
Typical markdown notes:           50KB-500KB each
PDF documents:                    1-50MB each
Academic papers:                  2-10MB each
Scanned documents:                5-100MB each
```

### Real-World Examples

**Academic Researcher:**
- 5,000 papers (PDFs): ~25GB
- Vector embeddings: ~250MB
- 2 years of chats: ~50MB
- **Total: ~25.3GB**

**Professional Note-Taker:**
- 2,000 markdown notes: ~100MB
- Vector embeddings: ~100MB
- 1 year of chats: ~20MB
- **Total: ~220MB**

**Personal Knowledge Base:**
- 500 mixed files: ~500MB
- Vector embeddings: ~25MB
- 6 months of chats: ~5MB
- **Total: ~530MB**

### Growth Patterns

**Monthly Growth (active use):**
- New notes: 10-500MB (depends on note types)
- New embeddings: 1-25MB
- Chat history: 2-10MB
- **Typical monthly growth: 15-535MB**

**Storage Optimization:**
- Compress old chats: Save ~50% space
- Archive old embeddings: Move unused notes
- PDF optimization: Reduce scanned document sizes
- Cleanup tools: Remove duplicate embeddings

### Disk Space Planning

**Minimum System:**
- 2GB free space (small collection)
- SSD recommended for performance

**Recommended System:**
- 10-50GB free space (medium-large collection)
- Fast SSD for embedding generation
- Regular backups to external storage

**Power User System:**
- 100GB+ free space
- NVMe SSD for optimal performance  
- Dedicated partition for yak-hole data
- Automated backup to NAS/cloud storage

## 🐛 Troubleshooting

### Performance Issues

**Slow embedding generation:**
```bash
# Check system resources
htop  # or Activity Monitor on macOS

# Use faster embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Instead of all-mpnet-base-v2

# Reduce batch size if running out of memory
BATCH_SIZE = 16  # Instead of 32
```

**MacBook Air overheating/throttling:**
- Process in smaller batches
- Enable "Low Power Mode" in System Preferences
- Use external cooling or process overnight

### Common Issues

**Ollama not responding**
```bash
# Check if Ollama is running
ollama list
# Restart if needed
ollama serve
```

**Notes not found**
- Verify `NOTES_DIR` path in `backend/config.py`
- Check file permissions
- Re-run `ingest_notes.py`

**Out of memory during processing**
- Reduce `BATCH_SIZE` in config
- Close other applications
- Process in smaller chunks

**React Native build issues**
- Clear Metro cache: `npx react-native start --reset-cache`
- Clean build: `cd ios && xcodebuild clean` (iOS) or `cd android && ./gradlew clean` (Android)

## 🤝 Contributing

yak-hole is designed to be personal and customizable. Feel free to:

1. Fork the repository
2. Create your feature branch
3. Test with your own notes
4. Submit a pull request

### Ideas for Contributions

- Support for more file formats (DOCX, EPUB, etc.)
- Advanced query types (date ranges, tags, etc.)
- Export functionality for chat conversations
- Integration with note-taking apps

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM capabilities
- [React Native](https://reactnative.dev/) for cross-platform development
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Sentence Transformers](https://www.sbert.net/) for embeddings

---

**Note**: Your notes never leave your machine. yak-hole is built with privacy as the core principle - all processing, storage, and AI inference happens locally.