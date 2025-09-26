# Testing Scripts for Verityn AI

This directory contains validation and testing scripts for system components.

## 📋 **Available Tests**

### **Component Validation Scripts**

| Script | Purpose | Usage |
|--------|---------|-------|
| `test_document_processing_validation.py` | Validates document processing pipeline | Tests text extraction, chunking, classification |
| `test_chunk_coverage_analysis.py` | Analyzes chunk coverage and quality | Validates content preservation and boundaries |
| `test_chunking_strategy_comparison.py` | Compares different chunking approaches | Evaluates RecursiveCharacter vs Document-Aware |

## 🚀 **Running Tests**

All tests follow the established testing rules and use real SOX documents only.

```bash
# Run from project root using UV
uv run python scripts/testing/test_document_processing_validation.py
uv run python scripts/testing/test_chunk_coverage_analysis.py
uv run python scripts/testing/test_chunking_strategy_comparison.py
```

## 📊 **Test Data Sources**

Following `.cursor/rules/testing-rules.mdc`:
1. **Primary**: `data/sox_test_documents/` - High-quality realistic SOX documents
2. **Secondary**: `data/synthetic_documents/` - Template-based functional documents
3. **Avoid**: Any hardcoded or fabricated test data

## ✅ **Testing Philosophy**

- Use real-world audit document scenarios
- No predetermined perfect outcomes
- Dynamic evaluation criteria based on document characteristics
- Comprehensive error handling and edge case testing
