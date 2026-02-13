# 🧠 Long_Memory_AI

**Persistent Real-Time Cognitive Architecture**

> Bridging the gap between transient context and permanent memory.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.2.0-61dafb.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

- [The Problem: The "Goldfish" Effect](#-the-problem-the-goldfish-effect)
- [The Solution: Cognitive Bridge](#-the-solution-cognitive-bridge)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Installation](#-installation)
- [Deployment](#-deployment)
- [Use Cases](#-use-cases)
- [Future Roadmap](#-future-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🐠 The Problem: The "Goldfish" Effect

### When AI Forgets

Modern LLMs suffer from **context amnesia** across long conversations:

```
Turn 1: "My preferred language is Kannada."
        ↓
Turn 937: "Can you call me tomorrow?"
          ❌ System: [Context Lost] What language should I use?
```

### The Core Issues:

1. **The Constraint:** LLMs have limited context windows (1,000+ turns = amnesia)
2. **The Cost:** Replaying full history is slow, expensive, and increases latency
3. **The Need:** Persistent memory of preferences, facts, and commitments without re-reading entire conversations

---

## ✨ The Solution: Cognitive Bridge

Long_Memory_AI is a **full-stack system** that extracts, stores, ranks, and injects memory in real-time.

### The Four Pillars:

```
    EXTRACT → PERSIST
       ↓         ↓
    INJECT ← RETRIEVE
```

**It doesn't just save chat logs; it remembers.**

---

## 🏗 Architecture

### System Overview

```
┌─────────────┐
│    User     │
│   Message   │
└──────┬──────┘
       │
       ↓
┌──────────────────┐     ┌─────────────────────────────────┐
│   FastAPI        │────→│      FAST PATH                  │
│   Backend        │     │  • Semantic Search              │
│  (Stateless)     │     │  • Context Injection            │
└──────┬───────────┘     │  • Response Generation (Groq)   │
       │                 └─────────────────────────────────┘
       │
       ↓ Async
┌──────────────────────────────────────────────────────────┐
│              BACKGROUND PATH                             │
│  • LLM Extraction (Groq Llama-3.1)                      │
│  • Validation & Duplicate Check                          │
│  • TinyDB Storage + HuggingFace Embeddings              │
└──────────────────────────────────────────────────────────┘
```

### Asynchronous Pipeline

1. **Fast Path** (200ms): Retrieve → Rank → Inject → Generate
2. **Background Path** (Async): Extract → Validate → Store

**Result:** Instant responses with memory processing in the background.

---

## 🎯 Features

### 1. Intelligent Extraction

The system extracts **5 memory types** from user messages:

```python
Memory Types:
1. Preference    → "I prefer tea over coffee"
2. Fact          → "I live in Mumbai"
3. Constraint    → "Don't call before 9 AM"
4. Commitment    → "Remind me to exercise daily"
5. Instruction   → "Always respond in Hindi"
```

**Signal vs. Noise:** The system ignores trivia and stores only actionable user facts.

**Example Extraction:**
```json
{
  "type": "preference",
  "key": "call_time",
  "value": "after 11 AM",
  "confidence": 0.94
}
```

---

### 2. Semantic Retrieval & Intelligent Ranking

#### Vector Search (HuggingFace API)
```
User Query: "What should I eat?"
              ↓
         [Embedding]
              ↓
    ┌────────────────────┐
    │  Vector Database   │
    │    (TinyDB +       │
    │   HF Embeddings)   │
    └────────────────────┘
              ↓
    Semantic matches (not just keywords)
```

#### Hybrid Ranking Algorithm

```
Final Score = (Relevance × 70%) + Confidence + Recency Bias
```

- **Relevance (70%):** Semantic similarity to current query
- **Confidence Score:** How certain the extraction was
- **Recency Bias:** Recent memories weighted higher

---

### 3. The Reflection Engine

**From raw data to insight.**

```
Turn 1: "I ordered salad"
Turn 3: "I don't eat steak"
         ↓
  [Every 5 turns]
         ↓
   REFLECTION EVENT
         ↓
 "User is likely vegetarian and health-conscious"
         ↓
   Meta-Memory Insight (stored as reflection type)
```

**Trigger:** Activates every 5 conversational turns to infer personality traits and behavioral patterns.

---

### 4. Real-Time Context Injection

```python
# Retrieved memories are formatted and injected into LLM context
context = """
User Profile:
- Preferred language: Kannada
- Call time: After 11 AM
- Dietary: Vegetarian
- Insight: Health-conscious
"""

# LLM generates response with full context awareness
response = generate_reply(user_message, context)
```

---

## 🛠️ Tech Stack

### Backend & API
- **FastAPI (v0.110.0)** - Async Python web framework
- **Groq API** - LLM inference (Llama-3.1-8b-instant)
- **Python 3.11** - Core logic

### Data & AI
- **TinyDB** - Lightweight JSON database (replaces ChromaDB)
- **HuggingFace Inference API** - Embeddings (all-MiniLM-L6-v2)
- **Sentence Transformers** - Semantic search
- **NumPy** - Vector operations

### Frontend
- **React (v19.2.0)** - UI framework
- **Vite (v7.3.1)** - Build tool
- **Google OAuth** - Authentication
- **Axios** - API client

### Deployment
- **Render** - Backend hosting (Python)
- **Vercel** - Frontend hosting (React)

---

## 🚀 Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- Groq API Key ([Get one here](https://console.groq.com))
- HuggingFace Token ([Get one here](https://huggingface.co/settings/tokens))
- Google OAuth Credentials ([Setup guide](https://console.cloud.google.com))

---

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/long-memory-ai.git
cd long-memory-ai/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here
EOF

# 5. Run the server
python main.py
```

**Backend will run on:** `https://long-memory-ai-1.onrender.com`

---

### Frontend Setup

```bash
# 1. Navigate to frontend
cd ../memory-chat-ui

# 2. Install dependencies
npm install

# 3. Create .env file
cat > .env << EOF
VITE_API_URL=https://long-memory-ai-1.onrender.com
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
EOF

# 4. Run dev server
npm run dev
```

**Frontend will run on:** `https://memory-chat-ui.vercel.app`

---

## 🌐 Deployment

### Backend Deployment (Render)

1. **Push backend to GitHub**
2. **Create Web Service on Render:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
   - Add environment variables:
     ```
     GROQ_API_KEY=your_key
     HF_TOKEN=your_token
     PORT=10000
     ```

3. **Get backend URL:** `https://long-memory-ai-1.onrender.com`

---

### Frontend Deployment (Vercel)

1. **Push frontend to GitHub**
2. **Import project on Vercel**
3. **Configure:**
   - Framework Preset: **Vite**
   - Root Directory: `./memory-chat-ui`
   - Add environment variables:
     ```
     VITE_API_URL=https://long-memory-ai-1.onrender.com
     VITE_GOOGLE_CLIENT_ID=your_google_client_id
     ```

4. **Deploy!**

5. **Update Google OAuth:**
   - Add Vercel URL to authorized origins
   - Add Vercel URL to redirect URIs

---

## 💡 Use Cases & Real-World Impact

### 1. Personal Assistant
> "Manages dietary restrictions and schedules. 'Remind me to call after 11 AM'."

### 2. Customer Support
> "Eliminates repetition. Resolves tickets faster by retaining history across sessions."

### 3. Mental Health
> "Tracks behavioural patterns and emotional states over weeks, not just minutes."

### 4. Education
> "Adapts to learning styles and remembers student progress across a full term."

---

## 🗺 Future Roadmap

```
Timeline of Enhancements:

├─ Voice Biometrics (Security)
├─ Emotional Memory (Sentiment Tracking)
├─ Knowledge Graphs (Entity Relationships)
└─ [Future] Moving from stateless Chatbots to persistent Life Companions
```

**Status:** ✅ Production Ready

---

## 📊 Memory Types & Examples

| Type | Description | Example |
|------|-------------|---------|
| **Preference** | User likes/dislikes | "I prefer dark mode" |
| **Fact** | Personal information | "I live in Bangalore" |
| **Constraint** | Time/resource limits | "Budget is ₹50,000" |
| **Commitment** | Future actions | "Remind me to exercise" |
| **Instruction** | How to behave | "Always use formal tone" |

---

## 🔐 Security & Privacy

- **User Isolation:** Each Google account = separate memory database
- **Session ID:** Tied to Google OAuth `sub` claim
- **No Password Storage:** OAuth handles authentication
- **Local Storage:** User data stored in TinyDB JSON file
- **API Keys:** Never exposed to frontend

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Commit changes:** `git commit -m 'Add amazing feature'`
4. **Push to branch:** `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React
- Write clear commit messages
- Add tests for new features
- Update documentation

---

## 🙏 Acknowledgments

- **Groq** for fast LLM inference
- **HuggingFace** for embedding models
- **FastAPI** for excellent async framework
- **React Team** for amazing UI library
- **Hackathon 2026** for the opportunity

---

## 📞 Contact & Support

- **Team:** TEAM LONG_MEMORY
- **GitHub:** [yourusername/long-memory-ai](https://github.com/yourusername/long-memory-ai)
- **Issues:** [Report bugs here](https://github.com/yourusername/long-memory-ai/issues)
- **Discussions:** [Join the conversation](https://github.com/yourusername/long-memory-ai/discussions)

---

## 🎯 Project Stats

```
📦 Backend:   FastAPI + Python + TinyDB
🎨 Frontend:  React + Vite + Google OAuth
🧠 AI:        Groq (Llama-3.1) + HuggingFace Embeddings
📊 Database:  TinyDB with JSON storage
🚀 Deployed:  Render + Vercel
⚡ Speed:     <200ms response time
💾 Memory:    ~50-80MB RAM usage
```

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

<div align="center">

**Moving from stateless Chatbots to persistent Life Companions.**


[Documentation](https://github.com/yourusername/long-memory-ai/wiki) • [Demo](https://your-app.vercel.app) • [Report Bug](https://github.com/yourusername/long-memory-ai/issues)

</div>
