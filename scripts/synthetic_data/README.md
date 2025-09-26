# Synthetic Data Generation Scripts

This directory contains all scripts related to synthetic audit document generation and testing data creation for Verityn AI.

## 📋 **Scripts Overview**

### **🏗️ Core Generation Scripts**

| Script | Purpose | Key Features |
|--------|---------|--------------|
| `synthetic_data_generation.py` | Core template engine for audit document structures | Document templates, company profiles, configurable complexity |
| `content_generator.py` | AI-powered content generation using OpenAI | Realistic audit content, template-based generation |
| `document_creator.py` | PDF/CSV file generation from templates | ReportLab integration, professional document formatting |

### **📊 Specialized Generators**

| Script | Purpose | Key Features |
|--------|---------|--------------|
| `create_sox_documents.py` | SOX compliance document generator | Access reviews, risk assessments, financial controls |
| `create_test_document.py` | Simple test document creator | Quick PDF generation, basic testing |

### **🤖 Q&A Generation Scripts**

| Script | Purpose | Key Features |
|--------|---------|--------------|
| `qa_generator.py` | Question-answer pair generator | RAGAS evaluation, chat system testing |
| `enhanced_qa_generator.py` | Advanced Q&A with gap analysis | Quality-aware datasets, evaluation improvements |
| `ragas_enhanced_generator.py` | Quality-stratified document generator | High/Medium/Low/Fail scenarios, SOX control mapping |

## 🚀 **Usage Examples**

### **Generate Basic Synthetic Documents**
```bash
# From project root
python scripts/synthetic_data/synthetic_data_generation.py
python scripts/synthetic_data/content_generator.py
python scripts/synthetic_data/document_creator.py
```

### **Create SOX Test Documents**
```bash
python scripts/synthetic_data/create_sox_documents.py
```

### **Generate Q&A Datasets**
```bash
python scripts/synthetic_data/qa_generator.py
python scripts/synthetic_data/enhanced_qa_generator.py
```

## 📂 **Output Directories**

- `data/synthetic_documents/` - Generated PDF, CSV, and JSON files
- `data/qa_datasets/` - Question-answer pairs for evaluation
- `data/enhanced_qa_datasets/` - Advanced Q&A datasets
- `data/enhanced_synthetic_documents/` - Quality-stratified documents

## 🔧 **Dependencies**

All scripts require the main project dependencies:
- OpenAI API key (for content generation)
- ReportLab (for PDF generation)
- Standard Python libraries (json, csv, datetime, pathlib)

## 📝 **Notes**

- Scripts generate realistic audit scenarios for enterprise companies
- All content follows SOX compliance standards and terminology
- Generated documents are designed for RAG pipeline testing and evaluation
- Quality levels range from perfect compliance to material weaknesses
