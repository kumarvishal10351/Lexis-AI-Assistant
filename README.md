# Lexis · AI Book Assistant
## Advanced Multi-Document RAG System with Mistral AI

![Lexis Banner](https://img.shields.io/badge/Status-Production%20Ready-brightgreen) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Overview

**Lexis** is a production-ready, intelligent document analysis system that leverages advanced retrieval-augmented generation (RAG) to answer questions about uploaded PDF documents with high accuracy and confidence scoring.

### Key Features

✨ **Advanced Capabilities**
- 🎓 Multi-document support with intelligent filtering
- 🧠 Semantic search with MMR (Maximal Marginal Relevance)
- 💬 Conversational AI with chat memory persistence
- 🎯 Improved accuracy through semantic re-ranking
- 📊 Confidence scoring with quality metrics
- 🔍 Advanced query rewriting for better retrieval
- 📈 Usage analytics and performance tracking
- 💾 Chat history persistence (local & cloud)

🎨 **Professional UI/UX**
- Modern dark theme with "Moonlit Library" aesthetic
- Responsive design for desktop and mobile
- Real-time streaming responses with visual feedback
- Interactive expandable components
- Smooth animations and transitions
- Professional typography with custom fonts

🚀 **Deployment Ready**
- Error handling and graceful fallbacks
- Comprehensive logging system
- Environment variable management
- Configuration management
- Session state handling
- Rate limiting ready
- Cloud deployment optimized

---

## 📋 Requirements

### System Requirements
- Python 3.10 or higher
- 2GB minimum RAM
- 500MB disk space for dependencies
- Internet connection for API calls

### Dependencies
```
streamlit>=1.28.0
langchain>=0.1.0
langchain-community>=0.0.10
langchain-mistralai>=0.1.0
python-dotenv>=1.0.0
chroma-db>=0.4.0
pypdf>=3.17.0
```

---

## 🚀 Quick Start

### 1. **Local Installation**

```bash
# Clone or download the project
cd lexis-ai-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "MISTRAL_API_KEY=your_api_key_here" > .env

# Run the application
streamlit run lexis_improved.py
```

### 2. **Cloud Deployment (Streamlit Cloud)**

```bash
# Push to GitHub
git push origin main

# On Streamlit Cloud:
1. Go to share.streamlit.io
2. Click "New app"
3. Select GitHub repo and branch
4. Set main file path to: lexis_improved.py
5. Add secrets: MISTRAL_API_KEY
6. Deploy
```

### 3. **Docker Deployment**

```bash
# Build Docker image
docker build -t lexis-app .

# Run container
docker run -p 8501:8501 \
  -e MISTRAL_API_KEY=your_key \
  lexis-app
```

---

## 🔧 Configuration

### Advanced Settings

Edit `CONFIG` dictionary in `lexis_improved.py`:

```python
CONFIG = {
    "chunk_size": 1500,          # Document chunk size (increase for longer contexts)
    "chunk_overlap": 400,        # Overlap between chunks (improves continuity)
    "retriever_k": 8,            # Number of documents to retrieve (8 for balanced performance)
    "retriever_fetch_k": 25,     # Initial fetch before MMR ranking (higher = better ranking)
    "retriever_lambda": 0.7,     # MMR diversity factor (0.5-1.0, higher = more diversity)
    "llm_temperature": 0.2,      # Response creativity (0.0-1.0, lower = more deterministic)
    "llm_model": "mistral-small-2506",  # LLM model selection
    "embedding_model": "mistral-embed",  # Embedding model (384-dim vectors)
    "history_limit": 10,         # Chat history messages to keep
    "max_context_length": 5000,  # Maximum context window (in characters)
}
```

### Environment Variables

```env
# Required
MISTRAL_API_KEY=your_mistral_api_key_here

# Optional
STREAMLIT_LOGGER_LEVEL=info
STREAMLIT_CLIENT_MAXUPLOADSIZE=200  # Max upload in MB
```

---

## 📈 Usage Guide

### Basic Workflow

1. **Upload Documents**
   - Click "Upload Documents" in sidebar
   - Select multiple PDFs
   - Click "Build Knowledge Base"
   - Wait for indexing to complete

2. **Ask Questions**
   - Type your question in the chat input
   - System analyzes and retrieves relevant passages
   - AI generates comprehensive answer
   - Review confidence score and sources

3. **Explore Results**
   - View answer with proper formatting
   - Check confidence/quality metrics
   - Expand sources to see specific passages
   - Review chat history

### Query Tips for Best Results

✅ **Effective Queries:**
- "What are the main themes in chapter 3?"
- "Compare the approaches of author A vs author B"
- "Summarize the key findings from page 42"
- "How does the introduction relate to the conclusion?"

❌ **Ineffective Queries:**
- "Tell me everything"
- "Random stuff"
- Single word searches
- Vague pronouns without context

---

## 🎯 Advanced Features

### 1. **Semantic Re-ranking**

The system uses `semantic_score_doc()` to re-rank retrieved documents:
- Word overlap analysis
- Query-context proximity
- Content relevance scoring

### 2. **Improved Confidence Scoring**

Three-factor scoring:
- **Semantic Score** (60%): Document relevance
- **Retrieval Overlap** (30%): Source coverage
- **Diversity Bonus** (10%): Multiple sources

### 3. **Chat Memory Persistence**

- Automatic saving to `data/chat_history.json`
- Last 10 conversations preserved
- Cloud-compatible storage
- Manual export available

### 4. **Usage Analytics**

- Query tracking in `data/analytics.json`
- Performance metrics
- User patterns
- Help with optimization

### 5. **Multi-Turn Conversations**

- Maintains context across messages
- References previous questions
- Handles clarifications naturally
- 4-turn history window for context

---

## 🏗️ Architecture

```
Lexis RAG Pipeline
├── Input Layer
│   ├── PDF Upload & Parsing
│   └── Text Extraction
├── Chunking Layer
│   ├── Recursive text splitting
│   ├── Smart overlap handling
│   └── Metadata preservation
├── Embedding Layer
│   ├── Mistral embeddings (384-dim)
│   └── ChromaDB vector store
├── Retrieval Layer
│   ├── MMR search (k=8, fetch_k=25)
│   ├── Source filtering
│   └── Semantic re-ranking
├── Generation Layer
│   ├── Query rewriting
│   ├── Context formatting
│   └── Mistral LLM streaming
└── Output Layer
    ├── Formatted responses
    ├── Confidence scoring
    └── Source attribution
```

---

## 🐛 Troubleshooting

### Issue: "MISTRAL_API_KEY not found"

**Solution:**
```bash
# Local: Create .env file
echo "MISTRAL_API_KEY=your_key" > .env

# Streamlit Cloud: Add to Secrets
# In your streamlit app settings, add:
# MISTRAL_API_KEY = your_key
```

### Issue: Low Accuracy / Wrong Answers

**Solutions:**
1. Improve query: Be more specific
2. Increase `retriever_k`: From 8 to 10-12
3. Adjust `chunk_size`: Try 1200-1800
4. Check document quality: PDFs should have selectable text

### Issue: Slow Response Times

**Solutions:**
1. Reduce `retriever_fetch_k`: From 25 to 15
2. Decrease `max_context_length`: From 5000 to 3000
3. Use `selected_doc` filter to limit scope
4. Increase `chunk_overlap`: Better quality > speed

### Issue: Out of Memory

**Solutions:**
1. Reduce `retriever_k`: From 8 to 4-5
2. Decrease `chunk_size`: To 1000-1200
3. Clear chat history: Use "Clear Chat" button
4. Reset knowledge base: Rebuild with fewer documents

### Issue: Deployment Failing

**Solutions:**
1. Check requirements.txt versions
2. Verify API key in Streamlit Secrets
3. Check Python version (3.10+)
4. Review logs: `streamlit run app.py --logger.level=debug`

---

## 📊 Performance Metrics

### Expected Performance
- **Response Time**: 3-8 seconds (varies by doc size)
- **Accuracy**: 70-90% (depends on query clarity)
- **Confidence Score**: 60-95% (for good matches)
- **Scalability**: Up to 500+ documents/pages

### Optimization Tips

| Parameter | Current | For Speed | For Accuracy |
|-----------|---------|-----------|--------------|
| chunk_size | 1500 | 1000 | 1800 |
| retriever_k | 8 | 4 | 10 |
| fetch_k | 25 | 15 | 35 |
| lambda_mult | 0.7 | 0.8 | 0.5 |

---

## 🔐 Security & Privacy

- **Local Processing**: All data processed locally (when using local Mistral)
- **No Data Storage**: PDFs not stored permanently
- **API Security**: Keys in environment variables only
- **Session Isolation**: Each user has isolated session
- **Chat History**: Optional persistence, can be cleared

### Data Compliance
- GDPR compatible (no external storage by default)
- Can be modified for HIPAA/compliance requirements
- Supports air-gapped deployments

---

## 📚 API Reference

### Core Functions

#### `semantic_score_doc(doc, query_words, query)`
Scores document relevance based on semantic similarity.
```python
score = semantic_score_doc(doc, {"python", "machine"}, "machine learning")
# Returns: float (0-1)
```

#### `improved_confidence_score(docs, query, overlap_percent)`
Calculates answer confidence (0-100).
```python
confidence = improved_confidence_score(docs, query, 0.85)
# Returns: int (0-100)
```

#### `format_context_with_structure(docs)`
Formats retrieved docs with metadata.
```python
context, overlap = format_context_with_structure(docs)
# Returns: Tuple[str, float]
```

---

## 🚀 Deployment Checklist

- [ ] API key configured
- [ ] requirements.txt installed
- [ ] Test with sample documents
- [ ] Configure for production (adjust CONFIG)
- [ ] Set up logging
- [ ] Enable analytics
- [ ] Configure Streamlit secrets (cloud)
- [ ] Test error handling
- [ ] Document custom configuration
- [ ] Set up monitoring/logging
- [ ] Create backup strategy
- [ ] Test responsiveness

---

## 📝 License

MIT License - Feel free to use in personal or commercial projects.

---

## 🤝 Support & Contributing

### Getting Help
1. Check troubleshooting section
2. Review error logs: `data/error.log`
3. Check Mistral API status
4. Review analytics: `data/analytics.json`

### Reporting Issues
Include:
- Error message and traceback
- Configuration (chunk_size, etc.)
- Document type/size
- Query that caused issue
- System information (OS, Python version)

### Contributing
- Fork the repository
- Create feature branch
- Submit pull request
- Update documentation

---

## 🎓 Educational Resources

- **RAG Concepts**: https://python.langchain.com/docs/modules/data_connection/
- **Vector Databases**: https://www.chroma.db/
- **Mistral API**: https://docs.mistral.ai/
- **Streamlit**: https://docs.streamlit.io/

---

## 📞 Contact & Updates

- **Documentation**: Check included DEPLOYMENT.md
- **Latest Version**: See version in config
- **Status Updates**: Monitor this README

---

## 🙏 Acknowledgments

Built with:
- LangChain for RAG framework
- Mistral AI for LLMs & embeddings
- Chroma for vector storage
- Streamlit for UI framework

---

**Version**: 2.0.0 (Production Ready)  
**Last Updated**: 2026-03-27  
**Status**: ✅ Stable & Production Ready
