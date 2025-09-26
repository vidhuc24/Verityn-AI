# Scripts Directory

This directory contains utility scripts for the Verityn AI project, organized by functionality.

## 📂 **Directory Structure**

### **🏗️ Synthetic Data Generation** (`synthetic_data/`)
Complete suite of scripts for generating realistic audit documents and test data.

**Key Scripts:**
- `synthetic_data_generation.py` - Core template engine for audit document structures
- `content_generator.py` - AI-powered content generation using OpenAI
- `document_creator.py` - PDF/CSV file generation from templates
- `create_sox_documents.py` - Specialized SOX compliance document generator
- `qa_generator.py` - Question-answer pair generator for RAGAS evaluation

[📖 **View Synthetic Data Documentation →**](synthetic_data/README.md)

### **📊 Evaluation & Metrics** (Root Level)
Scripts for system evaluation and performance assessment.

**Available Scripts:**
- `get_accurate_ragas_metrics.py` - RAGAS performance metrics provider

### **🔧 Debugging & Development** (Root Level)
Development and debugging utilities.

**Available Scripts:**
- `debug_upload_flow.py` - Upload flow debugging (located at project root)

## 🚀 **Quick Start**

### **Generate Synthetic Documents**
```bash
# Create basic synthetic audit documents
python scripts/synthetic_data/synthetic_data_generation.py
python scripts/synthetic_data/content_generator.py
python scripts/synthetic_data/document_creator.py

# Generate SOX-specific test documents
python scripts/synthetic_data/create_sox_documents.py
```

### **Create Q&A Datasets**
```bash
# Generate question-answer pairs for evaluation
python scripts/synthetic_data/qa_generator.py
python scripts/synthetic_data/enhanced_qa_generator.py
```

### **Get Performance Metrics**
```bash
# Get current RAGAS evaluation metrics
python scripts/get_accurate_ragas_metrics.py
```

## 📝 **Usage Guidelines**

### **Running Scripts**
Always run scripts from the **project root directory**:

```bash
# Correct way to run scripts
cd /path/to/Verityn-AI
python scripts/synthetic_data/script_name.py
python scripts/get_accurate_ragas_metrics.py
```

### **Environment Setup**
Ensure your environment is properly configured:

```bash
# Install dependencies using UV (our package manager)
uv sync

# Run scripts using UV
uv run python scripts/script_name.py

# Add new dependencies (if needed)
uv add package_name
```

### **API Keys**
Some scripts require API keys:
- **OpenAI API Key** - Required for content generation scripts
- **Tavily API Key** - Required for web search functionality

## 🎯 **Future Additions**

Planned script categories for future development:

- **`evaluation/`** - Advanced evaluation and testing scripts
- **`debugging/`** - Comprehensive debugging and diagnostic tools  
- **`utilities/`** - General-purpose utility scripts
- **`deployment/`** - Deployment and infrastructure scripts

## 📚 **Related Documentation**

- [📖 Synthetic Data Scripts](synthetic_data/README.md) - Detailed documentation for data generation
- [📋 Codebase Analysis](../CODEBASE_ANALYSIS.md) - Complete project analysis and architecture
- [🚀 Main README](../README.md) - Project overview and setup instructions 