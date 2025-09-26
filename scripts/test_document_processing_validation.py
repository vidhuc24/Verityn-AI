#!/usr/bin/env python3
"""
Document Processing Pipeline Validation Test for Verityn AI

PURPOSE: Validates the core document processing pipeline from file input to vector-ready chunks
SCOPE: Tests all supported formats using real SOX documents from data/sox_test_documents/
FOLLOWS: Established testing rules

SUCCESS CRITERIA:
- All SOX document types process without errors
- Text extraction is accurate and complete  
- Chunks are properly sized (300 chars, 75 overlap)
- Metadata includes document classification
- Processing times are reasonable (<30 seconds per document)
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.document_processor import EnhancedDocumentProcessor
from backend.app.services.classification_engine import ClassificationEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentProcessingValidator:
    """Validates document processing pipeline with real SOX documents."""
    
    def __init__(self):
        self.processor = EnhancedDocumentProcessor()
        self.test_results = {}
        
        # Real SOX test documents (following testing rules)
        self.test_documents = {
            "access_review": {
                "path": "data/sox_test_documents/sox_access_review_2024.txt",
                "expected_type": "access_review",
                "expected_framework": "SOX"
            },
            "financial_controls": {
                "path": "data/sox_test_documents/sox_financial_controls_2024.txt", 
                "expected_type": "financial_controls",
                "expected_framework": "SOX"
            },
            "internal_controls": {
                "path": "data/sox_test_documents/sox_internal_controls_2024.txt",
                "expected_type": "internal_controls", 
                "expected_framework": "SOX"
            },
            "risk_assessment": {
                "path": "data/sox_test_documents/sox_risk_assessment_2024.txt",
                "expected_type": "risk_assessment",
                "expected_framework": "SOX"
            }
        }
    
    async def validate_text_extraction(self, doc_name: str, doc_info: Dict) -> Dict[str, Any]:
        """Test text extraction accuracy and completeness."""
        logger.info(f"🔍 Testing text extraction for {doc_name}")
        
        try:
            file_path = Path(doc_info["path"])
            if not file_path.exists():
                return {"success": False, "error": f"Test document not found: {file_path}"}
            
            # Read original file for comparison
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Create mock UploadFile for testing
            from fastapi import UploadFile
            import io
            
            file_content = original_content.encode('utf-8')
            mock_file = UploadFile(
                filename=file_path.name,
                file=io.BytesIO(file_content)
            )
            
            # Test extraction
            start_time = time.time()
            extracted_text = await self.processor._extract_text(mock_file)
            extraction_time = time.time() - start_time
            
            # Validate extraction quality
            extraction_ratio = len(extracted_text) / len(original_content) if original_content else 0
            
            return {
                "success": True,
                "original_length": len(original_content),
                "extracted_length": len(extracted_text),
                "extraction_ratio": extraction_ratio,
                "extraction_time": extraction_time,
                "quality_check": extraction_ratio > 0.95  # Should extract 95%+ of content
            }
            
        except Exception as e:
            logger.error(f"❌ Text extraction failed for {doc_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def validate_chunking_strategy(self, doc_name: str, doc_info: Dict) -> Dict[str, Any]:
        """Test chunking strategy and parameters."""
        logger.info(f"📄 Testing chunking strategy for {doc_name}")
        
        try:
            file_path = Path(doc_info["path"])
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Test chunking
            chunks = self.processor.text_splitter.split_text(content)
            
            # Analyze chunk characteristics
            chunk_sizes = [len(chunk) for chunk in chunks]
            avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes) if chunks else 0
            
            # Check overlap (approximate)
            overlaps = []
            for i in range(len(chunks) - 1):
                current_chunk = chunks[i]
                next_chunk = chunks[i + 1]
                # Find overlap by checking suffix of current with prefix of next
                max_overlap = min(len(current_chunk), len(next_chunk), 150)  # Max reasonable overlap
                overlap_found = 0
                for j in range(1, max_overlap):
                    if current_chunk[-j:] in next_chunk[:j*2]:  # Allow some flexibility
                        overlap_found = j
                overlaps.append(overlap_found)
            
            avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0
            
            return {
                "success": True,
                "total_chunks": len(chunks),
                "avg_chunk_size": avg_chunk_size,
                "min_chunk_size": min(chunk_sizes) if chunk_sizes else 0,
                "max_chunk_size": max(chunk_sizes) if chunk_sizes else 0,
                "avg_overlap": avg_overlap,
                "size_within_target": 200 <= avg_chunk_size <= 400,  # Target: 300 ± 100
                "overlap_reasonable": 50 <= avg_overlap <= 100  # Target: 75 ± 25
            }
            
        except Exception as e:
            logger.error(f"❌ Chunking validation failed for {doc_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def validate_classification(self, doc_name: str, doc_info: Dict) -> Dict[str, Any]:
        """Test document classification accuracy."""
        logger.info(f"🏷️ Testing classification for {doc_name}")
        
        try:
            file_path = Path(doc_info["path"])
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Initialize classification engine
            classifier = ClassificationEngine()
            
            # Test classification
            start_time = time.time()
            classification_result = await classifier.classify_document(content)
            classification_time = time.time() - start_time
            
            # Validate classification accuracy
            predicted_type = classification_result.get("document_type", "").lower()
            expected_type = doc_info["expected_type"].lower()
            
            predicted_framework = classification_result.get("compliance_framework", "").upper()
            expected_framework = doc_info["expected_framework"].upper()
            
            return {
                "success": True,
                "predicted_type": predicted_type,
                "expected_type": expected_type,
                "type_correct": expected_type in predicted_type or predicted_type in expected_type,
                "predicted_framework": predicted_framework,
                "expected_framework": expected_framework,
                "framework_correct": expected_framework in predicted_framework,
                "confidence": classification_result.get("confidence", 0.0),
                "classification_time": classification_time,
                "metadata": classification_result.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"❌ Classification failed for {doc_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def validate_full_pipeline(self, doc_name: str, doc_info: Dict) -> Dict[str, Any]:
        """Test complete document processing pipeline."""
        logger.info(f"🔄 Testing full pipeline for {doc_name}")
        
        try:
            file_path = Path(doc_info["path"])
            
            # Create mock UploadFile
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            from fastapi import UploadFile
            import io
            
            mock_file = UploadFile(
                filename=file_path.name,
                file=io.BytesIO(file_content)
            )
            
            # Test full pipeline
            start_time = time.time()
            document_id = f"test_{doc_name}_{int(time.time())}"
            
            result = await self.processor.process_document(
                file=mock_file,
                document_id=document_id,
                description=f"Test processing of {doc_name}"
            )
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "document_id": result.get("document_id"),
                "chunk_count": result.get("chunk_count", 0),
                "processing_time": processing_time,
                "status": result.get("status"),
                "vector_storage": result.get("vector_storage"),
                "classification": result.get("classification", {}),
                "metadata": result.get("metadata", {}),
                "performance_acceptable": processing_time < 30  # Should process within 30 seconds
            }
            
        except Exception as e:
            logger.error(f"❌ Full pipeline failed for {doc_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all validation tests on all SOX documents."""
        logger.info("🚀 Starting comprehensive document processing validation")
        
        overall_results = {
            "test_summary": {
                "total_documents": len(self.test_documents),
                "start_time": time.time()
            },
            "document_results": {}
        }
        
        for doc_name, doc_info in self.test_documents.items():
            logger.info(f"\n📋 Testing document: {doc_name}")
            
            doc_results = {
                "document_info": doc_info,
                "tests": {}
            }
            
            # Test 1: Text Extraction
            doc_results["tests"]["text_extraction"] = await self.validate_text_extraction(doc_name, doc_info)
            
            # Test 2: Chunking Strategy
            doc_results["tests"]["chunking"] = await self.validate_chunking_strategy(doc_name, doc_info)
            
            # Test 3: Classification
            doc_results["tests"]["classification"] = await self.validate_classification(doc_name, doc_info)
            
            # Test 4: Full Pipeline
            doc_results["tests"]["full_pipeline"] = await self.validate_full_pipeline(doc_name, doc_info)
            
            # Calculate document success rate
            successful_tests = sum(1 for test in doc_results["tests"].values() if test.get("success", False))
            doc_results["success_rate"] = successful_tests / len(doc_results["tests"])
            
            overall_results["document_results"][doc_name] = doc_results
            
            logger.info(f"✅ {doc_name} completed: {successful_tests}/4 tests passed")
        
        # Calculate overall metrics
        overall_results["test_summary"]["end_time"] = time.time()
        overall_results["test_summary"]["total_time"] = overall_results["test_summary"]["end_time"] - overall_results["test_summary"]["start_time"]
        
        successful_documents = sum(1 for result in overall_results["document_results"].values() if result["success_rate"] == 1.0)
        overall_results["test_summary"]["success_rate"] = successful_documents / len(self.test_documents)
        overall_results["test_summary"]["successful_documents"] = successful_documents
        
        return overall_results
    
    def print_results_summary(self, results: Dict[str, Any]):
        """Print a comprehensive test results summary."""
        print("\n" + "="*80)
        print("📊 DOCUMENT PROCESSING VALIDATION RESULTS")
        print("="*80)
        
        summary = results["test_summary"]
        print(f"📋 Total Documents Tested: {summary['total_documents']}")
        print(f"✅ Successful Documents: {summary['successful_documents']}/{summary['total_documents']}")
        print(f"📈 Overall Success Rate: {summary['success_rate']:.1%}")
        print(f"⏱️ Total Test Time: {summary['total_time']:.2f} seconds")
        
        print(f"\n📄 DETAILED RESULTS BY DOCUMENT:")
        print("-"*80)
        
        for doc_name, doc_result in results["document_results"].items():
            print(f"\n🔍 {doc_name.upper()}")
            print(f"   Success Rate: {doc_result['success_rate']:.1%}")
            
            for test_name, test_result in doc_result["tests"].items():
                status = "✅" if test_result.get("success", False) else "❌"
                print(f"   {status} {test_name.replace('_', ' ').title()}")
                
                if test_name == "text_extraction" and test_result.get("success"):
                    print(f"      - Extraction Ratio: {test_result.get('extraction_ratio', 0):.1%}")
                    print(f"      - Extraction Time: {test_result.get('extraction_time', 0):.2f}s")
                
                elif test_name == "chunking" and test_result.get("success"):
                    print(f"      - Total Chunks: {test_result.get('total_chunks', 0)}")
                    print(f"      - Avg Chunk Size: {test_result.get('avg_chunk_size', 0):.0f} chars")
                    print(f"      - Size Within Target: {test_result.get('size_within_target', False)}")
                
                elif test_name == "classification" and test_result.get("success"):
                    print(f"      - Type Correct: {test_result.get('type_correct', False)}")
                    print(f"      - Framework Correct: {test_result.get('framework_correct', False)}")
                    print(f"      - Confidence: {test_result.get('confidence', 0):.1%}")
                
                elif test_name == "full_pipeline" and test_result.get("success"):
                    print(f"      - Processing Time: {test_result.get('processing_time', 0):.2f}s")
                    print(f"      - Chunks Created: {test_result.get('chunk_count', 0)}")
                    print(f"      - Vector Storage: {test_result.get('vector_storage', 'unknown')}")
                
                if not test_result.get("success") and "error" in test_result:
                    print(f"      - Error: {test_result['error']}")
        
        print("\n" + "="*80)
        
        # Overall assessment
        if summary['success_rate'] >= 1.0:
            print("🎉 EXCELLENT: All document processing tests passed!")
        elif summary['success_rate'] >= 0.75:
            print("✅ GOOD: Most document processing tests passed - minor issues to address")
        elif summary['success_rate'] >= 0.5:
            print("⚠️ NEEDS WORK: Significant issues found in document processing pipeline")
        else:
            print("🚨 CRITICAL: Major failures in document processing - requires immediate attention")


async def main():
    """Run the document processing validation tests."""
    validator = DocumentProcessingValidator()
    
    try:
        results = await validator.run_comprehensive_validation()
        validator.print_results_summary(results)
        
        # Return appropriate exit code
        success_rate = results["test_summary"]["success_rate"]
        if success_rate >= 0.75:
            print(f"\n✅ Test completed successfully (Success rate: {success_rate:.1%})")
            sys.exit(0)
        else:
            print(f"\n❌ Test completed with issues (Success rate: {success_rate:.1%})")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"🚨 Critical test failure: {str(e)}")
        print(f"\n🚨 Critical test failure: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
