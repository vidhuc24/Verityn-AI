#!/usr/bin/env python3
"""
Comprehensive Investigation of Retrieval Issues

This script investigates three key areas:
1. Query formulation - how we're constructing search queries
2. Context retrieval logic - how we're processing and ranking results  
3. Document processing - ensuring documents are properly stored and indexed

Uses real SOX documents and traces the complete flow.
"""

import asyncio
import json
import logging
import numpy as np
from pathlib import Path
import sys
from typing import Dict, List, Any, Tuple

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.app.services.vector_database import vector_db_service
from backend.app.services.document_processor import EnhancedDocumentProcessor
from backend.app.agents.specialized_agents import QuestionAnalysisAgent, ContextRetrievalAgent
from backend.app.agents.base_agent import AgentContext
from backend.app.workflows.multi_agent_workflow import MultiAgentWorkflow
from fastapi import UploadFile
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RetrievalInvestigator:
    def __init__(self):
        self.document_processor = EnhancedDocumentProcessor()
        self.question_agent = QuestionAnalysisAgent()
        self.context_agent = ContextRetrievalAgent()
        self.workflow = MultiAgentWorkflow()
        
    async def investigate_query_formulation(self):
        """Investigate how queries are being formulated and processed."""
        logger.info("🔍 Investigating Query Formulation...")
        
        # Test queries that failed in end-to-end test
        test_queries = [
            "What are the key findings from the access review?",
            "What material weaknesses were identified?",
            "What are the main compliance issues?",
            "Describe the risk assessment findings",
            "What remediation actions are recommended?"
        ]
        
        query_analysis = {}
        
        for query in test_queries:
            logger.info(f"  🔍 Analyzing query: '{query}'")
            
            try:
                # Step 1: Question Analysis Agent processing
                from backend.app.agents.base_agent import AgentType
                from datetime import datetime

                context = AgentContext(
                    inputs={"user_message": query, "conversation_history": [], "document_metadata": {}},
                    agent_type=AgentType.QUESTION_ANALYZER,
                    timestamp=datetime.now(),
                    conversation_id="investigation_test",
                    workflow_id="investigation_workflow"
                )

                try:
                    question_result = await self.question_agent.execute(context)
                    question_analysis_result = question_result
                except Exception as e:
                    question_analysis_result = {"error": str(e), "status": "failed"}
                
                # Step 2: Direct vector search (what actually gets searched)
                direct_search = await vector_db_service.semantic_search(query, limit=10, score_threshold=0.1)
                
                # Step 3: Context Retrieval Agent processing
                context_result = await self.context_agent.execute(context)
                
                query_analysis[query] = {
                    "original_query": query,
                    "question_analysis": {
                        "status": question_analysis_result.get("status", "unknown") if isinstance(question_analysis_result, dict) else "unknown",
                        "analysis": question_analysis_result.get("analysis", {}) if isinstance(question_analysis_result, dict) else {},
                        "intent": "unknown",
                        "complexity": "unknown",
                        "keywords": []
                    },
                    "direct_search": {
                        "total_results": len(direct_search),
                        "scores": [r['score'] for r in direct_search],
                        "top_3_results": [
                            {
                                "score": r['score'],
                                "content_preview": r['chunk_text'][:100] + "...",
                                "document_id": r['document_id']
                            }
                            for r in direct_search[:3]
                        ]
                    },
                    "context_retrieval": {
                        "status": context_retrieval_result.get("status", "unknown") if isinstance(context_retrieval_result, dict) else "unknown",
                        "search_results_count": len(context_retrieval_result.get("search_results", [])) if isinstance(context_retrieval_result, dict) else 0,
                        "context_count": len(context_retrieval_result.get("context", [])) if isinstance(context_retrieval_result, dict) else 0,
                        "retrieval_method": context_retrieval_result.get("retrieval_method", "unknown") if isinstance(context_retrieval_result, dict) else "unknown"
                    }
                }

                # Extract analysis details if available
                if isinstance(question_analysis_result, dict) and "analysis" in question_analysis_result:
                    analysis = question_analysis_result["analysis"]
                    query_analysis[query]["question_analysis"]["intent"] = analysis.get("intent", "unknown")
                    query_analysis[query]["question_analysis"]["complexity"] = analysis.get("complexity", "unknown")
                    query_analysis[query]["question_analysis"]["keywords"] = analysis.get("keywords", [])
                
                logger.info(f"    📊 Question intent: {query_analysis[query]['question_analysis']['intent']}")
                logger.info(f"    📊 Direct search: {len(direct_search)} results")
                logger.info(f"    📊 Context retrieval: {query_analysis[query]['context_retrieval']['context_count']} contexts")
                
            except Exception as e:
                query_analysis[query] = {"error": str(e)}
                logger.error(f"    ❌ Error: {str(e)}")
        
        return query_analysis
    
    async def investigate_context_retrieval_logic(self):
        """Investigate how context retrieval processes and ranks results."""
        logger.info("🔍 Investigating Context Retrieval Logic...")
        
        # Test with a specific query that should return results
        test_query = "What are the key findings from the access review?"
        
        try:
            # Step 1: Raw vector search
            raw_results = await vector_db_service.semantic_search(test_query, limit=20, score_threshold=0.0)
            
            # Step 2: Vector search with threshold
            threshold_results = await vector_db_service.semantic_search(test_query, limit=20, score_threshold=0.1)

            # Step 3: Context Retrieval Agent processing
            from backend.app.agents.base_agent import AgentType
            from datetime import datetime

            context = AgentContext(
                inputs={"user_message": test_query, "conversation_history": [], "document_metadata": {}},
                agent_type=AgentType.CONTEXT_RETRIEVER,
                timestamp=datetime.now(),
                conversation_id="investigation_test",
                workflow_id="investigation_workflow"
            )

            try:
                agent_results = await self.context_agent.execute(context)
                context_retrieval_result = agent_results
            except Exception as e:
                context_retrieval_result = {"error": str(e), "status": "failed"}
            
            # Step 4: Analyze the processing pipeline
            retrieval_analysis = {
                "raw_search": {
                    "total_results": len(raw_results),
                    "score_range": {
                        "min": min([r['score'] for r in raw_results]) if raw_results else 0,
                        "max": max([r['score'] for r in raw_results]) if raw_results else 0,
                        "mean": np.mean([r['score'] for r in raw_results]) if raw_results else 0
                    },
                    "sample_results": [
                        {
                            "score": r['score'],
                            "content_preview": r['chunk_text'][:100] + "...",
                            "document_type": r['metadata'].get('document_type', 'unknown'),
                            "document_id": r['document_id']
                        }
                        for r in raw_results[:5]
                    ]
                },
                "threshold_filtered": {
                    "total_results": len(threshold_results),
                    "filtered_out": len(raw_results) - len(threshold_results),
                    "score_range": {
                        "min": min([r['score'] for r in threshold_results]) if threshold_results else 0,
                        "max": max([r['score'] for r in threshold_results]) if threshold_results else 0,
                        "mean": np.mean([r['score'] for r in threshold_results]) if threshold_results else 0
                    }
                },
                "agent_processing": {
                    "status": agent_results.get("status", "unknown") if isinstance(agent_results, dict) else "unknown",
                    "search_results_count": len(agent_results.get("search_results", [])) if isinstance(agent_results, dict) else 0,
                    "context_count": len(agent_results.get("context", [])) if isinstance(agent_results, dict) else 0,
                    "retrieval_method": agent_results.get("retrieval_method", "unknown") if isinstance(agent_results, dict) else "unknown",
                    "processing_details": {
                        "hybrid_search_used": "hybrid_search" in str(agent_results) if agent_results else False,
                        "query_expansion_used": "query_expansion" in str(agent_results) if agent_results else False,
                        "metadata_filtering_used": "metadata" in str(agent_results) if agent_results else False
                    }
                }
            }
            
            logger.info(f"  📊 Raw search: {len(raw_results)} results")
            logger.info(f"  📊 Threshold filtered: {len(threshold_results)} results ({len(raw_results) - len(threshold_results)} filtered out)")
            context_count = len(agent_results.get('context', [])) if isinstance(agent_results, dict) else 0
            logger.info(f"  📊 Agent processed: {context_count} contexts")
            
            return retrieval_analysis
            
        except Exception as e:
            logger.error(f"  ❌ Error: {str(e)}")
            return {"error": str(e)}
    
    async def investigate_document_processing(self):
        """Investigate document processing, storage, and indexing."""
        logger.info("🔍 Investigating Document Processing...")
        
        try:
            # Step 1: Check what's in the vector database
            collection_info = await vector_db_service.get_collection_info()
            
            # Step 2: Get sample documents
            sample_search = await vector_db_service.semantic_search("sample", limit=20, score_threshold=0.0)
            
            # Step 3: Analyze document distribution
            document_analysis = {}
            document_types = {}
            document_sources = {}
            
            for result in sample_search:
                doc_id = result['document_id']
                metadata = result['metadata']
                
                # Track document types
                doc_type = metadata.get('document_type', 'unknown')
                document_types[doc_type] = document_types.get(doc_type, 0) + 1
                
                # Track document sources
                filename = metadata.get('filename', 'unknown')
                document_sources[filename] = document_sources.get(filename, 0) + 1
                
                # Analyze individual document
                if doc_id not in document_analysis:
                    document_analysis[doc_id] = {
                        "document_id": doc_id,
                        "filename": filename,
                        "document_type": doc_type,
                        "chunk_count": 0,
                        "metadata": metadata,
                        "sample_chunks": []
                    }
                
                document_analysis[doc_id]["chunk_count"] += 1
                if len(document_analysis[doc_id]["sample_chunks"]) < 2:
                    document_analysis[doc_id]["sample_chunks"].append({
                        "score": result['score'],
                        "content_preview": result['chunk_text'][:150] + "...",
                        "content_length": len(result['chunk_text'])
                    })
            
            # Step 4: Test processing a new document
            test_doc_path = Path("data/sox_test_documents/sox_access_review_2024.txt")
            processing_test = {}
            
            if test_doc_path.exists():
                with open(test_doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_obj = UploadFile(
                    file=BytesIO(content.encode('utf-8')),
                    filename="processing_test.txt",
                    headers={"content-type": "text/plain"}
                )
                
                process_result = await self.document_processor.process_document(
                    file=file_obj,
                    document_id="processing_investigation_test"
                )
                
                processing_test = {
                    "status": process_result.get("status", "unknown"),
                    "chunk_count": process_result.get("chunk_count", 0),
                    "classification": process_result.get("classification", {}),
                    "vector_storage": process_result.get("vector_storage", "unknown"),
                    "metadata_keys": list(process_result.get("metadata", {}).keys())
                }
            
            investigation_results = {
                "collection_info": collection_info,
                "total_chunks_found": len(sample_search),
                "document_type_distribution": document_types,
                "document_source_distribution": document_sources,
                "unique_documents": len(document_analysis),
                "document_details": list(document_analysis.values()),
                "processing_test": processing_test
            }
            
            logger.info(f"  📊 Collection status: {collection_info.get('status', 'unknown')}")
            logger.info(f"  📊 Total chunks found: {len(sample_search)}")
            logger.info(f"  📊 Unique documents: {len(document_analysis)}")
            logger.info(f"  📊 Document types: {document_types}")
            
            return investigation_results
            
        except Exception as e:
            logger.error(f"  ❌ Error: {str(e)}")
            return {"error": str(e)}
    
    async def investigate_end_to_end_flow(self):
        """Investigate the complete end-to-end flow for a failing query."""
        logger.info("🔍 Investigating End-to-End Flow...")
        
        # Use the query that failed in the end-to-end test
        failing_query = "What are the key findings from the access review?"
        
        try:
            # Step 1: Full workflow execution
            workflow_result = await self.workflow.execute(
                question=failing_query,
                conversation_id="investigation_e2e_test",
                document_id="test_document"
            )
            
            # Step 2: Trace each step
            e2e_analysis = {
                "query": failing_query,
                "workflow_result": {
                    "status": workflow_result.get("status", "unknown"),
                    "response": workflow_result.get("response", "No response"),
                    "metadata": workflow_result.get("metadata", {}),
                    "agents_executed": workflow_result.get("metadata", {}).get("agents_executed", []),
                    "agent_execution_times": workflow_result.get("metadata", {}).get("agent_execution_times", {}),
                    "total_execution_time": workflow_result.get("metadata", {}).get("total_execution_time", 0)
                },
                "step_by_step_analysis": {
                    "question_analysis": "executed" if "question_analyzer" in workflow_result.get("metadata", {}).get("agents_executed", []) else "not_executed",
                    "context_retrieval": "executed" if "context_retriever" in workflow_result.get("metadata", {}).get("agents_executed", []) else "not_executed", 
                    "response_synthesis": "executed" if "response_synthesizer" in workflow_result.get("metadata", {}).get("agents_executed", []) else "not_executed",
                    "compliance_analysis": "executed" if "compliance_analyzer" in workflow_result.get("metadata", {}).get("agents_executed", []) else "not_executed"
                }
            }
            
            logger.info(f"  📊 Workflow status: {workflow_result.get('status', 'unknown')}")
            logger.info(f"  📊 Agents executed: {workflow_result.get('metadata', {}).get('agents_executed', [])}")
            logger.info(f"  📊 Response length: {len(workflow_result.get('response', ''))}")
            
            return e2e_analysis
            
        except Exception as e:
            logger.error(f"  ❌ Error: {str(e)}")
            return {"error": str(e)}
    
    async def run_investigation(self):
        """Run the complete investigation."""
        logger.info("🚀 Starting Comprehensive Retrieval Investigation")
        
        try:
            # Investigation 1: Query Formulation
            query_formulation = await self.investigate_query_formulation()
            
            # Investigation 2: Context Retrieval Logic
            context_retrieval = await self.investigate_context_retrieval_logic()
            
            # Investigation 3: Document Processing
            document_processing = await self.investigate_document_processing()
            
            # Investigation 4: End-to-End Flow
            e2e_flow = await self.investigate_end_to_end_flow()
            
            # Compile results
            investigation_results = {
                "query_formulation_investigation": query_formulation,
                "context_retrieval_investigation": context_retrieval,
                "document_processing_investigation": document_processing,
                "end_to_end_flow_investigation": e2e_flow,
                "summary": self._generate_investigation_summary(
                    query_formulation, context_retrieval, document_processing, e2e_flow
                )
            }
            
            # Save results
            results_file = Path("scripts/testing/retrieval_investigation_results.json")
            with open(results_file, 'w') as f:
                json.dump(investigation_results, f, indent=2, default=str)
            
            logger.info(f"📊 Investigation results saved to: {results_file}")
            
            # Print summary
            self._print_investigation_summary(investigation_results)
            
            return investigation_results
            
        except Exception as e:
            logger.error(f"❌ Investigation failed: {str(e)}")
            raise
    
    def _generate_investigation_summary(self, query_form, context_ret, doc_proc, e2e) -> Dict:
        """Generate investigation summary."""
        issues_found = []
        recommendations = []
        
        # Analyze query formulation issues
        if isinstance(query_form, dict):
            for query, analysis in query_form.items():
                if "error" in analysis:
                    issues_found.append(f"Query formulation error for '{query[:30]}...': {analysis['error']}")
                elif analysis.get("context_retrieval", {}).get("context_count", 0) == 0:
                    issues_found.append(f"No context retrieved for query: '{query[:30]}...'")
        
        # Analyze context retrieval issues
        if isinstance(context_ret, dict) and "error" not in context_ret:
            agent_context_count = context_ret.get("agent_processing", {}).get("context_count", 0)
            if agent_context_count == 0:
                issues_found.append("Context Retrieval Agent returning 0 contexts")
        
        # Analyze document processing issues
        if isinstance(doc_proc, dict) and "error" not in doc_proc:
            unique_docs = doc_proc.get("unique_documents", 0)
            if unique_docs == 0:
                issues_found.append("No documents found in vector database")
        
        # Generate recommendations
        if issues_found:
            recommendations.append("Investigate context retrieval agent logic")
            recommendations.append("Check document processing and storage pipeline")
            recommendations.append("Verify query analysis and intent detection")
        
        return {
            "issues_found": issues_found,
            "recommendations": recommendations,
            "investigation_status": "issues_detected" if issues_found else "no_major_issues"
        }
    
    def _print_investigation_summary(self, results: Dict):
        """Print investigation summary."""
        print("\n" + "="*80)
        print("🔍 COMPREHENSIVE RETRIEVAL INVESTIGATION SUMMARY")
        print("="*80)
        
        summary = results.get("summary", {})
        
        print(f"\n📊 Investigation Status: {summary.get('investigation_status', 'unknown').upper()}")
        
        issues = summary.get("issues_found", [])
        if issues:
            print(f"\n❌ Issues Found ({len(issues)}):")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        
        recommendations = summary.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        # Key metrics
        doc_proc = results.get("document_processing_investigation", {})
        if "error" not in doc_proc:
            print(f"\n📄 Document Processing:")
            print(f"  Total chunks in database: {doc_proc.get('total_chunks_found', 0)}")
            print(f"  Unique documents: {doc_proc.get('unique_documents', 0)}")
            print(f"  Document types: {doc_proc.get('document_type_distribution', {})}")
        
        context_ret = results.get("context_retrieval_investigation", {})
        if "error" not in context_ret:
            print(f"\n🔍 Context Retrieval:")
            raw_count = context_ret.get("raw_search", {}).get("total_results", 0)
            threshold_count = context_ret.get("threshold_filtered", {}).get("total_results", 0)
            agent_count = context_ret.get("agent_processing", {}).get("context_count", 0)
            print(f"  Raw search results: {raw_count}")
            print(f"  After threshold filtering: {threshold_count}")
            print(f"  Agent processed contexts: {agent_count}")
        
        print("\n" + "="*80)

async def main():
    """Main investigation execution."""
    investigator = RetrievalInvestigator()
    await investigator.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())
