# UtilMaster

> Local-first AI utility platform with multi-agent intelligence and GraphRAG

## ✨ Features

- 📊 **PowerPoint Tools**: Analyze presentations and automatically fix issues
- 📄 **PDF Compression**: Reduce file sizes while preserving quality  
- 📝 **Word to PDF**: Convert documents instantly
- 🔍 **GraphRAG**: Search uploaded files using natural language
- 💬 **Context-Aware Chat**: Conversational interface with memory

## 🏗️ Architecture

**Multi-Agent System:**
- **Supervisor**: Intelligent request routing
- **PPTAgent**: PowerPoint analysis & improvement
- **WordAgent**: Document conversion
- **PDFAgent**: File compression
- **ChatAgent**: Context-aware conversations with GraphRAG

**GraphRAG Integration:**
- Vector embeddings for semantic search
- Neo4j graph database for relationships
- Hybrid search combining vector + graph queries

## 🛠️ Tech Stack

**Backend:**
- Python 3.12
- LangGraph (Multi-agent orchestration)
- LangChain + Ollama (Llama 3.1 8B)
- Neo4j (Graph database)
- FastAPI

**Frontend:**
- Next.js 15
- TypeScript + React
- Tailwind CSS
- Glassmorphism UI design

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Neo4j (local instance)
- Ollama with Llama 3.1 8B

### Installation

**1. Clone repository**
```bash
git clone https://github.com/YOUR_USERNAME/UtilMaster.git
cd UtilMaster
```

**2. Backend setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Neo4j credentials

# Start server
python server.py
```

**3. Frontend setup**
```bash
cd frontend
npm install
npm run dev
```

**4. Access application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## 📖 Documentation

- [LinkedIn Article Part 1](LINK) - Architecture & Tech Stack
- [LinkedIn Article Part 2](LINK) - Development Journey (11 Phases)

## 🎯 Use Cases

- **Students**: Analyze presentations, convert documents quickly
- **Professionals**: Compress PDFs before emailing, check slides
- **Researchers**: Search through uploaded documents with AI
- **Anyone**: All common document utilities in one place

## 🔒 Privacy First

- **100% Local**: All processing happens on your machine
- **No Cloud APIs**: Uses local Ollama LLM
- **Your Data**: Files never leave your computer
- **Zero Cost**: No API fees

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 👤 Author

**Ajay Kulkarni**
- LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)
- GitHub: [@YourUsername](https://github.com/YourUsername)

---

⭐ If you find UtilMaster useful, please give it a star!

Built with ❤️ using LangGraph, Neo4j, and Next.js
