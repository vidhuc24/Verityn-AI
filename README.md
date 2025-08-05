# 🔍 Verityn AI - Intelligent Document Chat
## AI-Powered Document Analysis for Audit, Risk & Compliance Professionals

Refer to all the rules files from cursor /rules folder

### 🎯 Bootcamp Final Challenge Submission

This project will address the bootcamp challenge requirements through 7 comprehensive tasks, building an end-to-end AI application for intelligent document chat with audit-specific insights, smart classification, and web-enhanced responses.

---

## 🎬 Demo Video
📹 **[5-Minute Live Demo](https://www.loom.com/share/YOUR_LOOM_LINK_HERE)**
> *Live demonstration of the Verityn AI application showing document upload, classification, smart questions, chat interface, and compliance insights*

---

## 📋 Challenge Tasks Plan

### Task 1: Problem & Audience Definition ✅
**Problem Statement:** *Audit professionals spend 60-70% of their time manually reviewing documents with inconsistent questioning approaches, missing critical insights, and lacking immediate access to current compliance guidance.*

**Target User:** Internal Audit Managers, Senior Auditors, and Risk & Compliance Analysts at mid-to-large enterprises

**Why This Matters:**
Audit professionals are overwhelmed by document analysis work. A typical compliance review requires analyzing hundreds of documents - access reviews, change logs, financial reconciliations, policy documents, risk assessments. Each document must be thoroughly questioned to extract insights, but this process is entirely manual, inconsistent across auditors, and time-intensive. Senior auditors spend their expertise on repetitive document review instead of strategic risk analysis and recommendations.

This creates a cascade of problems: different auditors ask different questions missing critical insights, knowledge gaps prevent access to current compliance guidance, constant context switching between documents and regulations reduces efficiency, and finding relevant compliance context requires extensive manual research.

### Task 2: Proposed Solution ✅
**Solution Vision:**
Verityn AI will transform document analysis from a manual, inconsistent process into an intelligent, standardized conversation. Auditors will upload any audit document and immediately receive automatic classification with tailored compliance questions. Through natural language chat, they'll extract comprehensive insights enhanced with real-time regulatory guidance, ensuring consistent, thorough analysis across all team members.

**Technology Stack:**
- **LLM**: OpenAI GPT-4 - Superior reasoning for compliance analysis and document chat
- **Embedding Model**: OpenAI text-embedding-3-small - Document similarity matching and classification
- **Orchestration**: LangChain + LangGraph - Multi-agent workflow management for document processing
- **Vector Database**: Qdrant - Fast similarity search and document retrieval
- **Web Search**: Tavily API - Real-time compliance and regulatory information integration
- **Monitoring**: LangSmith - Performance tracking and debugging of multi-agent workflows
- **Evaluation**: RAGAS - Chat response quality assessment and faithfulness measurement
- **User Interface**: Next.js + TypeScript - Modern, responsive web application with audit-focused design
- **Serving**: FastAPI + Docker - Production-ready API with containerized deployment

**Agentic Reasoning:**
- Document Processing Agent: Will extract, chunk, and embed uploaded documents for analysis
- Classification Agent: Will automatically identify document types and extract relevant metadata
- Question Analysis Agent: Will understand user intent and optimize queries for better responses
- Context Retrieval Agent: Will find relevant document sections using advanced RAG techniques
- Web Research Agent: Will gather external compliance knowledge via Tavily API
- Response Synthesis Agent: Will combine document context with web research for comprehensive answers

### Task 3: Data Strategy ✅
**Data Sources:**
1. **Document Classification Training Data**: Audit document examples across multiple types (Access Reviews, Change Logs, Financial Reconciliations, Policy Documents, Risk Assessments, System Configurations)
2. **Compliance Framework Knowledge**: SOX, SOC2, ISO27001 requirements for question suggestion templates
3. **Synthetic Test Documents**: Generated audit documents with known characteristics for testing classification and chat capabilities
4. **Tavily Search API**: Real-time regulatory guidance, best practices, and compliance updates
5. **Question Template Library**: Pre-built compliance-focused questions organized by document type

**Chunking Strategy:** Semantic chunking with 500-token overlaps optimized for document chat, preserving logical relationships within audit documents while ensuring comprehensive context retrieval for conversational analysis.

### Task 4: End-to-End Prototype 🔄
Will build complete agentic RAG application with:
- Multi-format document upload processing (PDF, DOCX, images, CSV)
- Automatic document classification with confidence scoring
- Smart question suggestions based on document type and compliance frameworks
- Multi-agent chat workflow using LangGraph for comprehensive document analysis
- Web-enhanced responses integrating real-time compliance guidance via Tavily
- Audit-focused Next.js interface with document preview and compliance insights
- Local FastAPI deployment with production-ready architecture

### Task 5: Golden Test Dataset 🔄
Will create comprehensive synthetic evaluation dataset with RAGAS framework:
- 50+ document chat scenarios across different audit document types
- Question-answer pairs covering compliance analysis, risk identification, and regulatory guidance
- Document classification test cases with ground truth labels
- Web-enhanced response evaluation scenarios combining document context with external knowledge
- Baseline performance metrics for chat quality, classification accuracy, and compliance relevance
- Automated evaluation pipeline for both document classification and chat response quality

### Task 6: Advanced Retrieval 🔄
Will implement and test multiple advanced retrieval techniques:
- Hybrid Search: Semantic + keyword matching optimized for audit terminology
- Query Expansion: Automatic compliance term expansion and synonym handling
- Multi-hop Retrieval: Cross-reference following for comprehensive document analysis
- Metadata Filtering: Document-type and compliance-framework specific filtering
- Conversational Retrieval: Context-aware responses maintaining chat history and document context
- Classification-Enhanced Retrieval: Retrieval strategies tailored to identified document types

### Task 7: Performance Assessment 🔄
Will conduct comprehensive performance comparison across all retrieval methods with quantified improvements using RAGAS metrics for chat response quality, document classification accuracy, and compliance relevance assessment.

---

## 🎯 Key Features (Planned)

### Core Functionality
- **Multi-Format Document Processing**: Support for PDF, DOCX, images, and CSV files
- **Intelligent Document Classification**: Automatic identification of audit document types with confidence scoring
- **Smart Question Suggestions**: Compliance-focused questions tailored to document type and framework
- **Natural Language Chat**: Conversational document analysis with context preservation
- **Web-Enhanced Insights**: Real-time regulatory guidance integration via Tavily API
- **Source Citations**: All responses include specific document references and confidence indicators

### Advanced AI Capabilities
- **Multi-Agent Architecture**: Specialized agents for classification, retrieval, web research, and response synthesis
- **Context-Aware Responses**: Chat maintains conversation history and document context
- **Compliance Intelligence**: Pre-trained understanding of SOX, SOC2, ISO27001 frameworks
- **Advanced Retrieval**: Hybrid search, query expansion, multi-hop retrieval
- **Real-time Processing**: Sub-5-second response times for chat interactions
- **Continuous Learning**: Model improvement from user feedback and evaluation metrics

### User Experience
- **Audit-First Design**: Interface optimized specifically for compliance workflows
- **Progressive Disclosure**: Advanced features available without overwhelming basic users
- **One-Click Questions**: Smart suggestions with interactive button selection
- **Document Preview**: Visual document display with metadata and classification results
- **Compliance Dashboard**: Risk indicators and key insights summary
- **Export Capabilities**: Conversation and insight export for audit documentation

---

## 📊 Performance Targets

### RAGAS Evaluation Goals
| Metric | Baseline Target | Target with Advanced Retrieval | Target with Multi-Agent | Target with Web Enhancement |
|--------|-------------|----------------|------------------|-------------|
| Faithfulness | 0.85 | 0.88 | 0.90 | 0.92 |
| Answer Relevancy | 0.80 | 0.83 | 0.85 | 0.88 |
| Context Precision | 0.75 | 0.82 | 0.84 | 0.86 |
| Context Recall | 0.70 | 0.76 | 0.78 | 0.82 |

### Custom Compliance Metrics
| Metric | Baseline Target | Advanced Target |
|--------|-------------|-----------------|
| Document Classification Accuracy | 0.90 | 0.95 |
| Compliance Relevance | 0.80 | 0.90 |
| Risk Identification Rate | 0.75 | 0.85 |
| Question Suggestion Adoption | 0.70 | 0.80 |

### Business Impact Goals
- **Time Savings**: 50% reduction in document analysis time
- **Consistency**: 90% standardization in audit questioning across team members
- **Coverage**: 95% of relevant compliance topics addressed through smart suggestions
- **User Engagement**: 80% of users utilize suggested questions feature
- **Accuracy**: 90% agreement with expert audit assessments

---

## 🔮 Future Roadmap

### Phase 2 Enhancements
- **Multi-Document Conversations**: Chat across multiple related documents simultaneously
- **Advanced Compliance Frameworks**: COSO, COBIT, NIST framework support
- **Audit Tool Integration**: Connect with ACL, IDEA, TeamMate, and other audit software
- **Mobile Application**: Native iOS/Android apps for field audit work
- **Team Collaboration**: Share conversations, insights, and annotations with team members
- **Advanced Analytics**: Document pattern analysis and trend identification

### Scaling Opportunities
- **Industry Specialization**: Healthcare, manufacturing, financial services customizations
- **Enterprise Deployment**: Multi-tenant SaaS platform with role-based access
- **Predictive Analytics**: AI-powered risk modeling based on document patterns
- **Integration Ecosystem**: Connect with major GRC platforms (ServiceNow, MetricStream)
- **International Expansion**: Support for global compliance frameworks and languages

---

## 🏆 Bootcamp Learning Integration

This project will demonstrate mastery of key bootcamp concepts:

- **Session 2**: RAG implementation with embeddings and vector databases for document retrieval
- **Session 4**: Production-grade LangChain/LCEL pipelines for document chat and classification
- **Session 5-6**: Multi-agent systems with LangGraph for document processing workflow
- **Session 7**: Synthetic data generation and LangSmith monitoring for performance tracking
- **Session 8**: Comprehensive evaluation with RAGAS for chat response quality assessment
- **Session 9**: Advanced retrieval techniques and optimization for audit-specific use cases

---

## 👨‍💻 Developer

**Vidhu C** - AI Engineering Bootcamp Participant
- GitHub: [@vidhuc24](https://github.com/vidhuc24)
- Project Repository: [Verityn-AI](https://github.com/vidhuc24/Verityn-AI)

---

## 📄 License

This project is part of the AI Makerspace Engineering Bootcamp certification challenge.

---

---

## 🚀 Quick Start

### Prerequisites
```bash
# Ensure you have UV installed (recommended) or Python 3.12+
uv --version  # Should show UV version
# OR
python3 --version  # Should show Python 3.12+
```

### Installation

#### Option 1: Using UV (Recommended)
```bash
# Initialize UV project and install dependencies
uv init --no-readme
uv add --requirement requirements.txt

# Set up environment variables
cp .env.example .env
# Add your OpenAI API key and Tavily API key to .env
```

#### Option 2: Using Traditional Virtual Environment
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your OpenAI API key and Tavily API key to .env
```

### 🔍 How to Verify Your Environment is Active

After installation, verify your setup is working correctly:

#### Quick Verification Commands
```bash
# Check Python location (should show your project's .venv path)
which python

# Check virtual environment variable
echo $VIRTUAL_ENV

# Test key package imports
python -c "import openai, langchain, fastapi, qdrant_client; print('✅ All packages working!')"
```

#### Expected Outputs
```bash
# Virtual environment should be active:
which python
# Expected: /path/to/your/project/.venv/bin/python

echo $VIRTUAL_ENV  
# Expected: /path/to/your/project/.venv

# Packages should import successfully:
python -c "import openai, fastapi; print('✅ Working!')"
# Expected: ✅ Working!
```

#### Troubleshooting
- **Empty parentheses `()` in prompt**: Normal with UV environments - your environment is still active
- **`pip` not found**: With UV, use `uv add package-name` instead of `pip install`
- **Package import errors**: Ensure you're in the activated environment

### Run the Application

#### Using UV (Recommended)
```bash
# Start the backend
uv run python backend/main.py

# In another terminal, start the frontend
cd frontend && npm run dev
```

#### Using Traditional Virtual Environment
```bash
# Ensure environment is activated first
source .venv/bin/activate

# Start the backend
cd backend && python main.py

# In another terminal, start the frontend
cd frontend && npm run dev
```

### Access the Application
- **Frontend**: http://localhost:3000 (Document Chat Interface)
- **API Documentation**: http://localhost:8000/docs

---

## 📁 Project Structure

```
Verityn-ai/
├── README.md                          # This file
├── PROJECT_PLAN.md                    # Detailed implementation roadmap
├── requirements.txt                   # Python dependencies
├── .env.example                      # Environment variables template
├── backend/
│   ├── main.py                       # FastAPI application
│   ├── app/
│   │   ├── document_processor.py     # Document upload and text extraction
│   │   ├── classification_engine.py  # Document type classification
│   │   ├── chat_engine.py            # Core chat functionality
│   │   ├── retrieval_engine.py       # Advanced retrieval methods
│   │   ├── vector_store.py           # Qdrant vector database management
│   │   └── tavily_client.py          # Web search integration
│   ├── agents/
│   │   ├── document_processor.py     # Document ingestion agent
│   │   ├── classifier.py             # Classification agent
│   │   ├── question_analyzer.py      # Query understanding agent
│   │   ├── web_researcher.py         # Tavily integration agent
│   │   └── response_synthesizer.py   # Response generation agent
│   ├── workflows/
│   │   └── chat_workflow.py          # LangGraph multi-agent workflow
│   └── models/
│       └── schemas.py                # Pydantic models
├── frontend/
│   ├── package.json                  # Next.js dependencies
│   ├── next.config.ts               # Next.js configuration
│   ├── tailwind.config.js           # Tailwind CSS configuration
│   └── src/                         # React components and pages
├── data/
│   ├── document_types/               # Document classification definitions
│   ├── question_templates/           # Compliance question templates
│   ├── test_documents/               # Sample documents for testing
│   └── evaluation_datasets/          # RAGAS evaluation datasets
├── scripts/
│   ├── generate_test_data.py         # Test document generation
│   ├── classification_training.py    # Document classification setup
│   ├── ragas_evaluation.py           # RAGAS evaluation pipeline
│   └── performance_analysis.py       # Performance metrics analysis
├── notebooks/
│   ├── 01_document_classification.ipynb    # Classification development
│   ├── 02_chat_pipeline.ipynb             # Chat functionality development
│   ├── 03_multi_agent_workflow.ipynb      # LangGraph implementation
│   ├── 04_ragas_evaluation.ipynb          # RAGAS evaluation
│   └── 05_advanced_retrieval.ipynb        # Advanced techniques testing
├── tests/
│   ├── test_classification.py        # Classification tests
│   ├── test_chat_engine.py           # Chat functionality tests
│   ├── test_agents.py                # Multi-agent tests
│   └── test_retrieval.py             # Retrieval tests
└── docs/
    ├── CHALLENGE_RESPONSES.md         # Detailed task responses
    ├── TECHNICAL_ARCHITECTURE.md     # System design
    ├── EVALUATION_RESULTS.md         # Performance analysis
    └── USER_GUIDE.md                 # Usage instructions
```

--- 