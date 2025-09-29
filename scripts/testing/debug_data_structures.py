#!/usr/bin/env python3
"""
Debug Data Structures Script

This script examines the actual return types and data structures from:
1. vector_db_service.semantic_search()
2. document_processor.process_document()
3. OpenAI API calls

Uses real SOX documents to understand what we're actually working with.
"""

import asyncio
import json
import logging
from pathlib import Path
import sys
from typing import Any, Dict

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.app.services.vector_database import vector_db_service
from backend.app.services.document_processor import EnhancedDocumentProcessor
from fastapi import UploadFile
from io import BytesIO
import openai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataStructureDebugger:
    def __init__(self):
        self.document_processor = EnhancedDocumentProcessor()
        
    async def debug_vector_search(self):
        """Debug the vector search service return types."""
        logger.info("🔍 Debugging vector search service...")
        
        try:
            # Test with a simple query
            test_query = "SOX compliance"
            logger.info(f"  Testing query: '{test_query}'")
            
            # Call semantic search
            results = await vector_db_service.semantic_search(test_query, limit=3, score_threshold=0.0)
            
            logger.info(f"  📊 Results type: {type(results)}")
            logger.info(f"  📊 Results length: {len(results) if results else 'None'}")
            
            if results:
                logger.info(f"  📊 First result type: {type(results[0])}")
                logger.info(f"  📊 First result attributes: {dir(results[0])}")
                
                # Try to access common attributes
                first_result = results[0]
                debug_info = {
                    "result_type": str(type(first_result)),
                    "result_attributes": dir(first_result),
                    "has_score": hasattr(first_result, 'score'),
                    "has_page_content": hasattr(first_result, 'page_content'),
                    "has_metadata": hasattr(first_result, 'metadata'),
                }
                
                # Try to get values
                try:
                    debug_info["score_value"] = first_result.score if hasattr(first_result, 'score') else "No score attribute"
                except Exception as e:
                    debug_info["score_error"] = str(e)
                
                try:
                    debug_info["page_content_value"] = first_result.page_content[:100] + "..." if hasattr(first_result, 'page_content') and first_result.page_content else "No page_content"
                except Exception as e:
                    debug_info["page_content_error"] = str(e)
                
                try:
                    debug_info["metadata_value"] = first_result.metadata if hasattr(first_result, 'metadata') else "No metadata"
                except Exception as e:
                    debug_info["metadata_error"] = str(e)
                
                logger.info(f"  📊 Debug info: {json.dumps(debug_info, indent=2, default=str)}")
                
                return debug_info
            else:
                logger.warning("  ⚠️ No results returned")
                return {"error": "No results returned"}
                
        except Exception as e:
            logger.error(f"  ❌ Error: {str(e)}")
            return {"error": str(e)}
    
    async def debug_document_processing(self):
        """Debug the document processor return types."""
        logger.info("🔍 Debugging document processor...")
        
        try:
            # Load a real SOX document
            sox_docs_path = Path("data/sox_test_documents/sox_access_review_2024.txt")
            if not sox_docs_path.exists():
                logger.error("  ❌ Test document not found")
                return {"error": "Test document not found"}
            
            with open(sox_docs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"  📄 Document content length: {len(content)} chars")
            
            # Create UploadFile
            file_obj = UploadFile(
                file=BytesIO(content.encode('utf-8')),
                filename="debug_test.txt",
                headers={"content-type": "text/plain"}
            )
            
            # Process document
            result = await self.document_processor.process_document(
                file=file_obj,
                document_id="debug_test_document"
            )
            
            logger.info(f"  📊 Process result type: {type(result)}")
            logger.info(f"  📊 Process result: {result}")
            
            if result:
                debug_info = {
                    "result_type": str(type(result)),
                    "result_keys": list(result.keys()) if isinstance(result, dict) else "Not a dict",
                    "result_attributes": dir(result) if hasattr(result, '__dict__') else "No attributes",
                }
                
                # Check for chunks
                if isinstance(result, dict) and 'chunks' in result:
                    chunks = result['chunks']
                    logger.info(f"  📊 Chunks type: {type(chunks)}")
                    logger.info(f"  📊 Chunks length: {len(chunks) if chunks else 'None'}")
                    
                    if chunks and len(chunks) > 0:
                        first_chunk = chunks[0]
                        logger.info(f"  📊 First chunk type: {type(first_chunk)}")
                        logger.info(f"  📊 First chunk attributes: {dir(first_chunk)}")
                        
                        chunk_debug = {
                            "chunk_type": str(type(first_chunk)),
                            "chunk_attributes": dir(first_chunk),
                            "has_page_content": hasattr(first_chunk, 'page_content'),
                            "has_metadata": hasattr(first_chunk, 'metadata'),
                        }
                        
                        try:
                            chunk_debug["page_content_value"] = first_chunk.page_content[:100] + "..." if hasattr(first_chunk, 'page_content') and first_chunk.page_content else "No page_content"
                        except Exception as e:
                            chunk_debug["page_content_error"] = str(e)
                        
                        try:
                            chunk_debug["metadata_value"] = first_chunk.metadata if hasattr(first_chunk, 'metadata') else "No metadata"
                        except Exception as e:
                            chunk_debug["metadata_error"] = str(e)
                        
                        debug_info["chunk_debug"] = chunk_debug
                
                logger.info(f"  📊 Debug info: {json.dumps(debug_info, indent=2, default=str)}")
                return debug_info
            else:
                logger.warning("  ⚠️ No result returned")
                return {"error": "No result returned"}
                
        except Exception as e:
            logger.error(f"  ❌ Error: {str(e)}")
            return {"error": str(e)}
    
    async def debug_openai_api(self):
        """Debug the OpenAI API usage."""
        logger.info("🔍 Debugging OpenAI API...")
        
        try:
            # Test with a simple query
            test_query = "SOX compliance requirements"
            logger.info(f"  Testing query: '{test_query}'")
            
            # Try the new OpenAI client syntax
            client = openai.OpenAI()
            
            # Test embedding
            response = client.embeddings.create(
                input=test_query,
                model="text-embedding-3-small"
            )
            
            logger.info(f"  📊 Embedding response type: {type(response)}")
            logger.info(f"  📊 Embedding response attributes: {dir(response)}")
            
            debug_info = {
                "response_type": str(type(response)),
                "response_attributes": dir(response),
                "has_data": hasattr(response, 'data'),
                "data_type": str(type(response.data)) if hasattr(response, 'data') else "No data",
            }
            
            if hasattr(response, 'data') and response.data:
                first_embedding = response.data[0]
                debug_info["first_embedding_type"] = str(type(first_embedding))
                debug_info["first_embedding_attributes"] = dir(first_embedding)
                debug_info["has_embedding"] = hasattr(first_embedding, 'embedding')
                
                if hasattr(first_embedding, 'embedding'):
                    debug_info["embedding_length"] = len(first_embedding.embedding)
                    debug_info["embedding_sample"] = first_embedding.embedding[:5]  # First 5 values
            
            logger.info(f"  📊 Debug info: {json.dumps(debug_info, indent=2, default=str)}")
            return debug_info
            
        except Exception as e:
            logger.error(f"  ❌ Error: {str(e)}")
            return {"error": str(e)}
    
    async def debug_collection_info(self):
        """Debug the collection info from Qdrant."""
        logger.info("🔍 Debugging Qdrant collection info...")
        
        try:
            collection_info = await vector_db_service.get_collection_info()
            
            logger.info(f"  📊 Collection info type: {type(collection_info)}")
            logger.info(f"  📊 Collection info: {collection_info}")
            
            debug_info = {
                "info_type": str(type(collection_info)),
                "info_content": collection_info,
                "is_dict": isinstance(collection_info, dict),
            }
            
            if isinstance(collection_info, dict):
                debug_info["keys"] = list(collection_info.keys())
                debug_info["vectors_count"] = collection_info.get("vectors_count", "Not found")
                debug_info["points_count"] = collection_info.get("points_count", "Not found")
            
            logger.info(f"  📊 Debug info: {json.dumps(debug_info, indent=2, default=str)}")
            return debug_info
            
        except Exception as e:
            logger.error(f"  ❌ Error: {str(e)}")
            return {"error": str(e)}
    
    async def run_debug_analysis(self):
        """Run complete debug analysis."""
        logger.info("🚀 Starting Data Structure Debug Analysis")
        
        try:
            # Debug each service
            vector_debug = await self.debug_vector_search()
            document_debug = await self.debug_document_processing()
            openai_debug = await self.debug_openai_api()
            collection_debug = await self.debug_collection_info()
            
            # Compile results
            debug_results = {
                "vector_search_debug": vector_debug,
                "document_processing_debug": document_debug,
                "openai_api_debug": openai_debug,
                "collection_info_debug": collection_debug,
                "summary": {
                    "vector_search_working": "error" not in vector_debug,
                    "document_processing_working": "error" not in document_debug,
                    "openai_api_working": "error" not in openai_debug,
                    "collection_info_working": "error" not in collection_debug,
                }
            }
            
            # Save results
            results_file = Path("scripts/testing/debug_data_structures_results.json")
            with open(results_file, 'w') as f:
                json.dump(debug_results, f, indent=2, default=str)
            
            logger.info(f"📊 Debug results saved to: {results_file}")
            
            # Print summary
            print("\n" + "="*80)
            print("🔍 DATA STRUCTURE DEBUG SUMMARY")
            print("="*80)
            
            print(f"\n📊 Vector Search: {'✅ Working' if debug_results['summary']['vector_search_working'] else '❌ Issues'}")
            print(f"📊 Document Processing: {'✅ Working' if debug_results['summary']['document_processing_working'] else '❌ Issues'}")
            print(f"📊 OpenAI API: {'✅ Working' if debug_results['summary']['openai_api_working'] else '❌ Issues'}")
            print(f"📊 Collection Info: {'✅ Working' if debug_results['summary']['collection_info_working'] else '❌ Issues'}")
            
            print("\n" + "="*80)
            
            return debug_results
            
        except Exception as e:
            logger.error(f"❌ Debug analysis failed: {str(e)}")
            raise

async def main():
    """Main debug execution."""
    debugger = DataStructureDebugger()
    await debugger.run_debug_analysis()

if __name__ == "__main__":
    asyncio.run(main())
