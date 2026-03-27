# Lexis AI Assistant - Quick Start Guide (5 Minutes)

## ⚡ Ultra-Fast Setup

### Prerequisites Check
- ✅ Python 3.10+ installed
- ✅ Mistral API key (get from https://console.mistral.ai/)
- ✅ Internet connection

### 1️⃣ Setup (2 minutes)

```bash
# Clone/download project
git clone <repo-url>
cd lexis-ai-assistant

# Create virtual environment
python -m venv venv

# Activate (pick one for your OS)
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate            # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Configure (1 minute)

```bash
# Create .env file
echo "MISTRAL_API_KEY=your_api_key_here" > .env
```

Or manually:
1. Create file named `.env` in project root
2. Add: `MISTRAL_API_KEY=your_actual_api_key`
3. Save

### 3️⃣ Run (instantly!)

```bash
streamlit run lexis_improved.py
```

Opens automatically at: `http://localhost:8501`

### 4️⃣ Use It (1 minute test)

1. Upload a PDF (click sidebar "Upload Documents")
2. Click "Build Knowledge Base"
3. Wait for ✅ completion message
4. Type a question in chat
5. Get answer with sources!

---

## 🚀 Common First Steps

### Test with Sample PDF
```bash
# Create simple test PDF (download one from web first)
# or use any PDF document

# Upload in sidebar
# Click "Build Knowledge Base"
# Ask: "What are the main topics covered?"
```

### Verify Installation
```python
# Run this to check everything is installed
python -c "
import streamlit
import langchain
import mistralai
print('✅ All packages installed!')
"
```

### Test API Key
```bash
# Verify your API key works
python -c "
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv('MISTRAL_API_KEY')
if key:
    print(f'✅ API key found: {key[:10]}...')
    try:
        llm = ChatMistralAI(model='mistral-small-2506')
        print('✅ API connection successful!')
    except Exception as e:
        print(f'❌ API error: {e}')
else:
    print('❌ MISTRAL_API_KEY not found')
"
```

---

## 📱 Trying Cloud Instead?

### Fastest Cloud Option: Streamlit Cloud

1. **Push to GitHub** (if not already)
   ```bash
   git push origin main
   ```

2. **Go to** https://share.streamlit.io
3. **Click** "New app"
4. **Select** your GitHub repo
5. **Add secret**: MISTRAL_API_KEY = your_key
6. **Done!** 🎉 (deploys automatically)

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run: `pip install -r requirements.txt` |
| `MISTRAL_API_KEY not found` | Create `.env` file with your key |
| `Port 8501 in use` | Run: `streamlit run lexis_improved.py --server.port 8502` |
| `ModuleNotFoundError: langchain` | Activate venv: `source venv/bin/activate` |
| Slow startup | First run takes longer, wait 30-60s |
| PDF won't upload | Check file is valid PDF, < 200MB |
| No answer to questions | 1) Check KB is built, 2) Try different question |

---

## 💡 Pro Tips

### Get Better Answers
```
❌ Bad: "tell me about the book"
✅ Good: "What are the main characters in chapter 3?"

❌ Bad: "stuff"
✅ Good: "Compare author's views on climate change"
```

### Speed Up Response
```python
# In lexis_improved.py, find CONFIG section
CONFIG = {
    "chunk_size": 1000,        # Smaller = faster
    "retriever_k": 4,          # Smaller = faster (4-8 is good)
    "retriever_fetch_k": 15,   # Smaller = faster
}
```

### Improve Accuracy
```python
# Same CONFIG section
CONFIG = {
    "chunk_size": 1800,        # Larger = better context
    "retriever_k": 10,         # Larger = more results
    "retriever_fetch_k": 35,   # Larger = better ranking
}
```

### Check What's Happening
```bash
# Enable debug output
streamlit run lexis_improved.py --logger.level=debug
```

---

## 📊 After Getting Started

### Recommended Next Steps

1. **Upload More Documents**
   - Add 3-5 PDFs to test multi-document features
   - Try diverse topics
   - Check cross-document search

2. **Explore Features**
   - Try different question types
   - Check confidence scores
   - Review source citations
   - Use document filter

3. **Optimize for Your Use**
   - Note which settings give best results
   - Adjust CONFIG for your documents
   - Test response times
   - Fine-tune chunk sizes

4. **Deploy if Satisfied**
   - Choose deployment platform
   - Follow DEPLOYMENT.md guide
   - Set up monitoring
   - Share with users

---

## 🔄 Useful Commands

```bash
# Clear everything and start fresh
rm -rf chroma_db data venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Check Python version
python --version

# Update dependencies
pip install -r requirements.txt --upgrade

# View installed packages
pip list

# Check if API key is set
echo $MISTRAL_API_KEY

# Stop Streamlit (in terminal where it's running)
Ctrl+C
```

---

## 🎯 What to Expect

### Performance
- **First load**: 5-10 seconds (first time init)
- **Build KB**: 10-30 seconds (depends on PDF size)
- **Answer**: 3-8 seconds (depends on document size)
- **Confidence**: 60-95% (depends on query clarity)

### Limitations
- Works best with text-based PDFs
- Scanned PDFs need OCR (not included)
- Long documents (~200+ pages) slower
- Quality depends on query clarity

### Capabilities
- ✅ Multi-document search
- ✅ Conversational history
- ✅ Source attribution
- ✅ Confidence scoring
- ✅ Semantic understanding
- ✅ Cross-document synthesis

---

## 📞 Getting Help

### If Something Breaks
1. Check error message in terminal
2. Try the troubleshooting table above
3. Review logs (if running on cloud)
4. Check Mistral API status
5. Restart: `Ctrl+C` then `streamlit run lexis_improved.py`

### Common Questions

**Q: How do I save my chat?**
A: Automatically saved to `data/chat_history.json`

**Q: Can I use offline?**
A: No, requires Mistral API (internet needed)

**Q: What file formats work?**
A: Currently PDF only (.pdf)

**Q: Can I delete a document from KB?**
A: Reset KB in sidebar, then rebuild with selected documents

**Q: Why is response slow?**
A: Check document size, reduce retriever_k in CONFIG

**Q: How much does it cost?**
A: Depends on Mistral API usage (pay-as-you-go model)

---

## ✅ Success Checklist

- [ ] Python 3.10+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with API key
- [ ] `streamlit run lexis_improved.py` starts without errors
- [ ] Can upload a PDF
- [ ] Can build knowledge base
- [ ] Can ask a question and get answer
- [ ] Sources are displayed
- [ ] Chat history is preserved

---

## 🎓 Next Level

Once comfortable:
1. Read [README.md](README.md) for full features
2. Check [DEPLOYMENT.md](DEPLOYMENT.md) for cloud setup
3. Modify CONFIG for your use case
4. Set up monitoring & analytics
5. Consider horizontal scaling

---

**Ready? Let's go! 🚀**

```bash
streamlit run lexis_improved.py
```

Then upload your first PDF and start asking questions!

---

**Need help?** Check the troubleshooting section above or review full README.md
