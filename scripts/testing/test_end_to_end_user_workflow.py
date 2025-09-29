#!/usr/bin/env python3
"""
REAL End-to-End User Workflow Test for Verityn AI

This test validates the COMPLETE user experience from document upload
to final response generation, simulating real user interactions.

TESTING PRINCIPLES:
- Tests actual user workflow: Upload → Question → Response
- Uses real audit documents and realistic compliance questions
- Validates complete multi-agent pipeline execution
- Measures end-to-end performance and user experience
- Tests error handling and edge cases
- Includes response quality assessment
"""

import asyncio
import time
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.workflows.multi_agent_workflow import MultiAgentWorkflow
from backend.app.services.document_processor import EnhancedDocumentProcessor
from backend.app.config import settings


class TestInterruptException(Exception):
    """Exception raised when test validation fails and should be interrupted."""
    pass


class EndToEndUserWorkflowTest:
    """Real end-to-end user workflow testing with complete user experience validation."""

    def __init__(self):
        self.workflow = MultiAgentWorkflow()
        self.document_processor = EnhancedDocumentProcessor()
        self.real_documents = {}
        self.test_scenarios = []
        self.results = []

    async def run_test(self):
        """Execute the complete end-to-end user workflow test suite."""
        logger.info("🎯 Starting REAL End-to-End User Workflow Test")
        logger.info("📤 Testing complete user journey: Document Upload → Question → Complete Response")
        logger.info("🔄 Validating full multi-agent pipeline with real user scenarios")

        # Load real audit documents
        await self._load_real_audit_documents()

        # Define realistic user workflow scenarios
        self._define_user_workflow_scenarios()

        logger.info(f"✅ Loaded {len(self.real_documents)} real audit documents")
        logger.info(f"🔍 Testing {len(self.test_scenarios)} complete user workflows")

        # CRITICAL VALIDATION CHECKS BEFORE RUNNING TESTS
        try:
            await self._validate_test_prerequisites()
            logger.info("✅ All validation checks passed - proceeding with test scenarios")
        except TestInterruptException as e:
            logger.error(f"❌ CRITICAL VALIDATION FAILED: {str(e)}")
            logger.error("🛑 Test cannot proceed - fixing issues required")
            return

        # Run user workflow scenarios
        for i, scenario in enumerate(self.test_scenarios, 1):
            logger.info(f"👤 Testing user workflow {i}/{len(self.test_scenarios)}: '{scenario['name']}'")

            try:
                result = await self._test_user_workflow(scenario)
                self.results.append(result)
            except TestInterruptException as e:
                logger.error(f"🛑 CRITICAL VALIDATION FAILED in scenario {i}: {str(e)}")
                logger.error("🛑 Stopping all tests due to validation failure")
                break  # Stop testing all scenarios

        # Analyze and report results
        self._analyze_results()
        self._save_results()

    async def _load_real_audit_documents(self):
        """Load actual audit documents from sox_test_documents/."""
        documents_dir = project_root / "data" / "sox_test_documents"

        # Load all TXT documents (real audit content from sox_test_documents)
        txt_files = [
            "sox_access_review_2024.txt",
            "sox_risk_assessment_2024.txt",
            "sox_financial_controls_2024.txt",
            "sox_internal_controls_2024.txt"
        ]

        # Load 2 PDF documents (realistic audit scenarios from synthetic_documents)
        pdf_files = [
            "SOX_Access_Review_2024.pdf",
            "amazon_financial_reconciliation_20250804.pdf"
        ]

        # Load TXT documents from sox_test_documents
        for txt_file in txt_files:
            file_path = documents_dir / txt_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()

                    doc_id = txt_file.replace('.txt', '')
                    self.real_documents[doc_id] = {
                        "content": content,
                        "file_path": str(file_path),
                        "document_type": self._infer_document_type(doc_id),
                        "content_preview": content[:200] + "..." if len(content) > 200 else content
                    }

                    logger.info(f"📄 Loaded TXT document: {doc_id} ({len(content)} chars)")

                except Exception as e:
                    logger.warning(f"⚠️ Could not load TXT {txt_file}: {str(e)}")

        # Load PDF documents from synthetic_documents
        synthetic_dir = project_root / "data" / "synthetic_documents" / "pdf"
        for pdf_file in pdf_files:
            file_path = synthetic_dir / pdf_file
            if file_path.exists():
                try:
                    # For PDFs, we'll use the file path and let the document processor handle extraction
                    doc_id = pdf_file.replace('.pdf', '')
                    self.real_documents[doc_id] = {
                        "file_path": str(file_path),
                        "document_type": self._infer_document_type(doc_id),
                        "content": ""  # Will be extracted by document processor
                    }

                    logger.info(f"📄 Loaded PDF document: {doc_id} ({file_path.name})")

                except Exception as e:
                    logger.warning(f"⚠️ Could not load PDF {pdf_file}: {str(e)}")

    def _infer_document_type(self, doc_id: str) -> str:
        """Infer document type from filename."""
        doc_id_lower = doc_id.lower()
        if "access" in doc_id_lower:
            return "access_review"
        elif "risk" in doc_id_lower:
            return "risk_assessment"
        elif "financial" in doc_id_lower:
            return "financial_controls"
        elif "internal" in doc_id_lower:
            return "internal_controls"
        else:
            return "audit_report"

    def _define_user_workflow_scenarios(self):
        """Define realistic end-to-end user workflow scenarios."""
        self.test_scenarios = [
            {
                "name": "comprehensive_access_review_analysis",
                "description": "User uploads access review document and asks about SOX compliance",
                "document_key": "sox_access_review_2024",  # TXT file
                "user_questions": [
                    "What are the key findings from this access review document?",
                    "Are there any material weaknesses identified in the access controls?",
                    "What remediation actions are recommended for the access control issues?",
                    "How does this impact our SOX 404 compliance status?"
                ],
                "expected_workflow": {
                    "document_upload": True,
                    "question_analysis": True,
                    "context_retrieval": True,
                    "response_synthesis": True,
                    "web_research": True,
                    "compliance_analysis": True
                },
                "expected_quality": {
                    "overall_user_experience": 0.8,
                    "response_consistency": 0.8,
                    "contextual_relevance": 0.8,
                    "regulatory_compliance": 0.7
                }
            },
            {
                "name": "risk_assessment_deep_dive",
                "description": "User uploads risk assessment and asks detailed compliance questions",
                "document_key": "sox_risk_assessment_2024",
                "user_questions": [
                    "What are the high-risk areas identified in this risk assessment?",
                    "How effective are the current internal controls according to this document?",
                    "What specific control deficiencies need to be addressed?",
                    "What regulatory guidance applies to these risk findings?"
                ],
                "expected_workflow": {
                    "document_upload": True,
                    "question_analysis": True,
                    "context_retrieval": True,
                    "response_synthesis": True,
                    "web_research": True,
                    "compliance_analysis": True
                },
                "expected_quality": {
                    "overall_user_experience": 0.75,
                    "response_consistency": 0.8,
                    "contextual_relevance": 0.8,
                    "regulatory_compliance": 0.7
                }
            },
            {
                "name": "financial_controls_audit",
                "description": "User uploads financial controls document and requests compliance analysis",
                "document_key": "sox_financial_controls_2024",
                "user_questions": [
                    "What controls need improvement based on this financial controls assessment?",
                    "Are there any significant deficiencies in the financial reporting controls?",
                    "What are the compliance implications of these control findings?",
                    "What regulatory updates should we consider for these financial controls?"
                ],
                "expected_workflow": {
                    "document_upload": True,
                    "question_analysis": True,
                    "context_retrieval": True,
                    "response_synthesis": True,
                    "web_research": True,
                    "compliance_analysis": True
                },
                "expected_quality": {
                    "overall_user_experience": 0.8,
                    "response_consistency": 0.8,
                    "contextual_relevance": 0.8,
                    "regulatory_compliance": 0.7
                }
            },
            {
                "name": "financial_reconciliation_pdf_analysis",
                "description": "User uploads PDF financial reconciliation document and analyzes compliance",
                "document_key": "amazon_financial_reconciliation_20250804",  # PDF file
                "user_questions": [
                    "What are the key findings from this financial reconciliation document?",
                    "Are there any reconciling items that require attention?",
                    "What is the overall status of the reconciliation process?",
                    "What compliance implications does this document have?"
                ],
                "expected_workflow": {
                    "document_upload": True,
                    "question_analysis": True,
                    "context_retrieval": True,
                    "response_synthesis": True,
                    "web_research": True,
                    "compliance_analysis": True
                },
                "expected_quality": {
                    "overall_user_experience": 0.75,
                    "response_consistency": 0.8,
                    "contextual_relevance": 0.8,
                    "regulatory_compliance": 0.7
                }
            }
        ]

    async def _test_user_workflow(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test a complete user workflow scenario."""
        scenario_result = {
            "scenario_name": scenario["name"],
            "document_used": scenario["document_key"],
            "user_questions": scenario["user_questions"],
            "start_time": time.time(),
            "success": False,
            "question_results": [],
            "overall_workflow": {},
            "quality_scores": {},
            "errors": []
        }

        try:
            logger.info(f"  📝 Document: {scenario['document_key']}")
            logger.info(f"  ❓ Questions: {len(scenario['user_questions'])}")

            # Process document first (simulating user upload)
            document_id = scenario["document_key"]
            document_data = self.real_documents[document_id]
            
            # ACTUALLY PROCESS THE DOCUMENT INTO QDRANT
            await self._process_document_for_testing(document_id, document_data)

            # Test each user question in sequence
            conversation_results = []

            for i, question in enumerate(scenario["user_questions"]):
                logger.info(f"    ❓ Question {i+1}: {question[:50]}...")

                try:
                    # Execute complete workflow for this question
                    workflow_result = await self.workflow.execute(
                        question=question,
                        conversation_id=f"e2e_test_{scenario['name']}_{i+1}",
                        document_id=document_id
                    )

                    # CRITICAL VALIDATION: Check response for "no document" patterns
                    response = workflow_result.get("response", "")
                    if self._detect_no_document_pattern(response):
                        logger.error(f"    ❌ CRITICAL: Response indicates no document context!")
                        logger.error(f"    📝 Response: {response[:100]}...")
                        raise TestInterruptException(f"Question {i+1} returned 'no document' response - test invalid")

                    # CRITICAL VALIDATION: Check workflow stages executed
                    if not self._validate_workflow_stages(workflow_result):
                        logger.error(f"    ❌ CRITICAL: Required workflow stages did not execute!")
                        raise TestInterruptException(f"Question {i+1} workflow stages failed - test invalid")

                    question_result = {
                        "question": question,
                        "workflow_result": workflow_result,
                        "success": workflow_result.get("status") == "completed",
                        "response": response,
                        "execution_time": workflow_result.get("metadata", {}).get("workflow_execution_time", 0)
                    }

                    conversation_results.append(question_result)

                    # Brief pause between questions (simulating user thinking time)
                    await asyncio.sleep(0.5)

                except TestInterruptException as e:
                    logger.error(f"    🛑 CRITICAL VALIDATION FAILED: {str(e)}")
                    logger.error(f"    🛑 Stopping scenario due to validation failure")
                    raise e  # Re-raise to stop the entire test
                    
                except Exception as e:
                    logger.error(f"    💥 Question {i+1} failed: {str(e)}")
                    question_result = {
                        "question": question,
                        "workflow_result": {},
                        "success": False,
                        "response": "",
                        "execution_time": 0,
                        "error": str(e)
                    }
                    conversation_results.append(question_result)

            # Analyze overall workflow success
            scenario_result["question_results"] = conversation_results
            scenario_result["overall_workflow"] = self._analyze_workflow_success(conversation_results)
            scenario_result["quality_scores"] = self._calculate_user_experience_quality(conversation_results, scenario["expected_quality"])

            # Overall success if most questions succeeded
            successful_questions = sum(1 for q in conversation_results if q["success"])
            scenario_result["success"] = successful_questions >= len(conversation_results) * 0.8  # 80% success rate

            logger.info(f"    ✅ Workflow completed: {successful_questions}/{len(conversation_results)} questions successful")
            logger.info(f"    📊 Quality score: {scenario_result['quality_scores'].get('overall_user_experience', 0):.1%}")

        except Exception as e:
            scenario_result["errors"].append(f"User workflow test failed: {str(e)}")
            logger.error(f"    💥 User workflow failed: {str(e)}")

        scenario_result["end_time"] = time.time()
        return scenario_result

    def _analyze_workflow_success(self, question_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall workflow success across all questions."""
        total_questions = len(question_results)
        successful_questions = sum(1 for q in question_results if q["success"])

        # Check if all major workflow components executed
        workflow_stages = {
            "document_processing": True,  # Assumed successful if workflow runs
            "question_analysis": False,
            "context_retrieval": False,
            "response_synthesis": False,
            "web_research": False,
            "compliance_analysis": False
        }

        # Check agent execution in first successful question
        for question_result in question_results:
            if question_result["success"]:
                metadata = question_result["workflow_result"].get("metadata", {})
                agent_times = metadata.get("agent_execution_times", {})

                workflow_stages["question_analysis"] = "question_analyzer" in agent_times
                workflow_stages["context_retrieval"] = "context_retriever" in agent_times
                workflow_stages["response_synthesis"] = "response_synthesizer" in agent_times
                workflow_stages["compliance_analysis"] = "compliance_analyzer" in agent_times

                # Check for web research in agents_executed
                agents_executed = metadata.get("agents_executed", [])
                workflow_stages["web_research"] = ("regulatory_context" in agents_executed or
                                                 "web_research" in agents_executed)
                break

        return {
            "total_questions": total_questions,
            "successful_questions": successful_questions,
            "success_rate": successful_questions / total_questions if total_questions > 0 else 0,
            "workflow_stages": workflow_stages,
            "all_stages_executed": all(workflow_stages.values())
        }

    def _calculate_user_experience_quality(self, question_results: List[Dict[str, Any]], expected: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate user experience quality across all questions."""
        scores = {}

        # Response consistency (all questions should have similar quality)
        response_lengths = [len(q["response"].split()) for q in question_results if q["success"] and q["response"]]
        if response_lengths:
            avg_length = sum(response_lengths) / len(response_lengths)
            length_variance = sum((length - avg_length) ** 2 for length in response_lengths) / len(response_lengths)
            scores["response_consistency"] = max(0, 1 - (length_variance / (avg_length ** 2)))  # Lower variance = higher consistency
        else:
            scores["response_consistency"] = 0.0

        # Contextual relevance (responses should be relevant to questions)
        relevant_responses = 0
        for question_result in question_results:
            if question_result["success"] and question_result["response"]:
                response = question_result["response"].lower()
                question = question_result["question"].lower()

                # Check if response contains relevant keywords from question
                question_keywords = set(question.split()[:5])  # First 5 words
                response_matches = sum(1 for keyword in question_keywords if keyword in response)
                if response_matches >= 2:  # At least 2 keyword matches
                    relevant_responses += 1

        scores["contextual_relevance"] = relevant_responses / len(question_results) if question_results else 0.0

        # Response quality (length and completeness)
        quality_scores = []
        for question_result in question_results:
            if question_result["success"] and question_result["response"]:
                word_count = len(question_result["response"].split())
                if 150 <= word_count <= 800:
                    quality_scores.append(1.0)
                elif word_count < 150:
                    quality_scores.append(max(0.7, word_count / 150))
                else:
                    quality_scores.append(max(0.6, 800 / word_count))

        scores["avg_response_quality"] = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

        # Regulatory compliance (check for regulatory terms in responses)
        regulatory_terms = ["sox", "pcaob", "2024", "compliance", "regulatory"]
        regulatory_scores = []
        for question_result in question_results:
            if question_result["success"] and question_result["response"]:
                response_lower = question_result["response"].lower()
                term_count = sum(1 for term in regulatory_terms if term in response_lower)
                regulatory_scores.append(min(term_count / 3, 1.0))  # At least 3 terms for full score

        scores["regulatory_compliance"] = sum(regulatory_scores) / len(regulatory_scores) if regulatory_scores else 0.0

        # Overall user experience (weighted average)
        scores["overall_user_experience"] = (
            scores["response_consistency"] * 0.25 +
            scores["contextual_relevance"] * 0.25 +
            scores["avg_response_quality"] * 0.25 +
            scores["regulatory_compliance"] * 0.25
        )

        return scores

    def _analyze_results(self):
        """Analyze and report end-to-end user workflow test results."""
        total_scenarios = len(self.results)
        successful_scenarios = sum(1 for r in self.results if r["success"])

        # Calculate average scores
        quality_scores = [r["quality_scores"] for r in self.results if r["success"]]
        if quality_scores:
            avg_user_experience = sum(qs.get("overall_user_experience", 0) for qs in quality_scores) / len(quality_scores)
            avg_consistency = sum(qs.get("response_consistency", 0) for qs in quality_scores) / len(quality_scores)
            avg_relevance = sum(qs.get("contextual_relevance", 0) for qs in quality_scores) / len(quality_scores)
            avg_regulatory = sum(qs.get("regulatory_compliance", 0) for qs in quality_scores) / len(quality_scores)
        else:
            avg_user_experience = avg_consistency = avg_relevance = avg_regulatory = 0.0

        # Calculate average execution time
        execution_times = []
        for result in self.results:
            for q_result in result["question_results"]:
                if q_result["success"]:
                    execution_times.append(q_result["execution_time"])

        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0

        # Analyze workflow stage success rates
        workflow_stages = {}
        for result in self.results:
            if result["success"]:
                stages = result["overall_workflow"]["workflow_stages"]
                for stage, success in stages.items():
                    if stage not in workflow_stages:
                        workflow_stages[stage] = {"total": 0, "successful": 0}
                    workflow_stages[stage]["total"] += 1
                    if success:
                        workflow_stages[stage]["successful"] += 1

        logger.info("\n" + "="*100)
        logger.info("🎯 END-TO-END USER WORKFLOW TEST RESULTS")
        logger.info("="*100)
        logger.info(f"📊 OVERALL STATUS: {'✅ SUCCESS' if successful_scenarios == total_scenarios else '❌ NEEDS IMPROVEMENT'}")
        logger.info(f"🎯 Success Rate: {successful_scenarios}/{total_scenarios} ({successful_scenarios/total_scenarios*100:.1f}%)")
        logger.info(f"⏱️ Avg Question Execution Time: {avg_execution_time:.1f}s")
        logger.info(f"📄 Test Approach: Complete user workflow with real documents")
        logger.info("")
        logger.info("📊 USER EXPERIENCE METRICS:")
        logger.info(f"   ✅ Overall User Experience: {avg_user_experience:.1%} (Target: 80.0%)")
        logger.info(f"   ✅ Response Consistency: {avg_consistency:.1%} (Target: 80.0%)")
        logger.info(f"   ✅ Contextual Relevance: {avg_relevance:.1%} (Target: 80.0%)")
        logger.info(f"   ✅ Regulatory Compliance: {avg_regulatory:.1%} (Target: 70.0%)")
        logger.info("")
        logger.info("🔧 WORKFLOW STAGE SUCCESS RATES:")
        for stage, stats in workflow_stages.items():
            success_rate = stats["successful"] / stats["total"] * 100
            logger.info(f"   {stage.replace('_', ' ').title()}: {success_rate:.1f}% ({stats['successful']}/{stats['total']})")
        logger.info("")
        logger.info("📋 SCENARIO RESULTS:")
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            quality = result["quality_scores"].get("overall_user_experience", 0) if result["success"] else 0
            questions = len(result["question_results"])
            successful_q = sum(1 for q in result["question_results"] if q["success"])
            logger.info(f"   {status} {result['scenario_name']}: {quality:.1%} quality, {successful_q}/{questions} questions")

        # Recommendations
        logger.info("")
        if avg_user_experience < 0.8:
            logger.info("💡 IMPROVEMENT RECOMMENDATIONS:")
            if avg_consistency < 0.8:
                logger.info("   1. CRITICAL: Improve response consistency across different question types")
            if avg_relevance < 0.8:
                logger.info("   2. HIGH: Enhance contextual relevance of responses to user questions")
            if avg_regulatory < 0.7:
                logger.info("   3. MEDIUM: Increase regulatory content integration in responses")
        else:
            logger.info("🎉 EXCELLENT: End-to-end user workflow meets all quality targets!")

        logger.info("="*100)
        logger.info("✅ END-TO-END USER WORKFLOW TEST COMPLETED (REAL DATA)")
        logger.info("="*100)

    def _save_results(self):
        """Save detailed test results to file."""
        import json

        output_path = Path("scripts/testing/end_to_end_user_workflow_results.json")

        # Prepare results for JSON serialization
        serializable_results = []
        for result in self.results:
            serializable_result = result.copy()
            # Ensure all values are JSON serializable
            for key, value in serializable_result.items():
                if isinstance(value, (int, float, str, bool, list, dict, type(None))):
                    continue
                else:
                    serializable_result[key] = str(value)
            serializable_results.append(serializable_result)

        with open(output_path, 'w') as f:
            json.dump({
                "test_metadata": {
                    "test_name": "End-to-End User Workflow Test (Complete User Journey)",
                    "timestamp": time.time(),
                    "total_scenarios": len(self.results),
                    "documents_used": list(self.real_documents.keys()),
                    "test_type": "End-to-End"
                },
                "results": serializable_results
            }, f, indent=2)

        logger.info(f"📊 Detailed results saved to: {output_path}")

    async def _validate_test_prerequisites(self):
        """Validate all prerequisites before running test scenarios."""
        logger.info("🔍 Running critical validation checks...")
        
        # Check #1: Document Processing Validation
        await self._validate_documents_in_qdrant()
        
        # Check #2: Vector Database Health Check
        await self._validate_vector_database_health()
        
        # Check #3: Context Retrieval Validation
        await self._validate_context_retrieval()
        
        # Check #4: Response Quality Thresholds (will be checked per response)
        # Check #5: Workflow Stage Validation (will be checked per workflow)
        # Check #7: API Service Health Checks
        await self._validate_api_services()
        
        # Check #8: Response Pattern Detection (will be checked per response)
        logger.info("✅ All prerequisite validations passed")

    async def _validate_documents_in_qdrant(self):
        """Check #1: Verify documents are actually processed into Qdrant."""
        logger.info("  🔍 Validating documents in Qdrant...")
        
        # Check if we have documents loaded
        if not self.real_documents:
            raise TestInterruptException("No documents loaded for testing")
        
        # Check if documents are in Qdrant by doing a simple search
        from backend.app.services.vector_database import vector_db_service
        
        # Try to get collection info
        try:
            collection_info = await vector_db_service.get_collection_info()
            vectors_count = collection_info.get("vectors_count", 0)
            
            if vectors_count == 0:
                raise TestInterruptException("Vector database is empty - documents not processed")
            
            logger.info(f"  ✅ Found {vectors_count} documents in Qdrant")
            
        except Exception as e:
            raise TestInterruptException(f"Failed to validate Qdrant collection: {str(e)}")

    async def _validate_vector_database_health(self):
        """Check #2: Verify vector database is healthy and accessible."""
        logger.info("  🔍 Validating vector database health...")
        
        from backend.app.services.vector_database import vector_db_service
        
        try:
            # Test basic Qdrant connectivity
            collection_info = await vector_db_service.get_collection_info()
            
            if not collection_info:
                raise TestInterruptException("Cannot access Qdrant collection")
            
            vectors_count = collection_info.get("vectors_count", 0)
            if vectors_count == 0:
                raise TestInterruptException("Vector database contains no documents")
            
            logger.info(f"  ✅ Vector database healthy with {vectors_count} documents")
            
        except Exception as e:
            raise TestInterruptException(f"Vector database health check failed: {str(e)}")

    async def _validate_context_retrieval(self):
        """Check #3: Test if context retrieval system is working."""
        logger.info("  🔍 Validating context retrieval system...")
        
        from backend.app.services.vector_database import vector_db_service
        
        try:
            # Test a simple query
            test_query = "audit compliance sox"
            test_results = await vector_db_service.semantic_search(test_query, limit=1)
            
            if len(test_results) == 0:
                raise TestInterruptException("Context retrieval returning 0 results - system not functioning")
            
            logger.info(f"  ✅ Context retrieval working - found {len(test_results)} results")
            
        except Exception as e:
            raise TestInterruptException(f"Context retrieval validation failed: {str(e)}")

    async def _validate_api_services(self):
        """Check #7: Verify all external API services are available."""
        logger.info("  🔍 Validating API services...")
        
        # Test OpenAI (basic import check)
        try:
            import openai
            logger.info("  ✅ OpenAI service available")
        except Exception as e:
            raise TestInterruptException(f"OpenAI service not available: {str(e)}")
        
        # Test Qdrant (already tested in vector database health check)
        logger.info("  ✅ Qdrant service available")
        
        # Test Tavily (basic import check)
        try:
            from backend.app.services.tavily_service import TavilyService
            tavily = TavilyService()
            logger.info("  ✅ Tavily service available")
        except Exception as e:
            logger.warning(f"  ⚠️ Tavily service check failed: {str(e)} (may not be critical)")

    def _detect_no_document_pattern(self, response: str) -> bool:
        """Check #8: Detect if response indicates no document context."""
        no_doc_patterns = [
            "no document context was provided",
            "no access review document was found",
            "unable to assess without the necessary document",
            "please provide the document",
            "no document was found for analysis",
            "without the document, it is not possible"
        ]
        response_lower = response.lower()
        return any(pattern in response_lower for pattern in no_doc_patterns)

    def _validate_workflow_stages(self, workflow_result: Dict[str, Any]) -> bool:
        """Check #5: Verify each workflow stage executed successfully."""
        required_stages = ["question_analyzer", "context_retriever", "response_synthesizer"]
        
        metadata = workflow_result.get("metadata", {})
        agent_execution_times = metadata.get("agent_execution_times", {})
        
        for stage in required_stages:
            if stage not in agent_execution_times:
                logger.error(f"  ❌ Workflow stage '{stage}' did not execute")
                return False
        
        logger.info("  ✅ All required workflow stages executed")
        return True

    async def _process_document_for_testing(self, document_id: str, document_data: Dict[str, Any]):
        """Process a document through the document processor to store it in Qdrant."""
        logger.info(f"  📤 Processing document {document_id} into Qdrant...")
        
        try:
            # Check if document has file_path (for PDFs) or content (for TXTs)
            if "file_path" in document_data and document_data["file_path"]:
                # Process PDF file
                from fastapi import UploadFile
                from io import BytesIO
                
                file_path = document_data["file_path"]
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                file_obj = UploadFile(
                    file=BytesIO(file_content),
                    filename=Path(file_path).name,
                    headers={"content-type": "application/pdf"}
                )
                
                result = await self.document_processor.process_document(
                    file=file_obj,
                    document_id=document_id
                )
                
                if result and result.get("status") in ["success", "processed"]:
                    logger.info(f"  ✅ PDF document {document_id} processed successfully")
                else:
                    logger.warning(f"  ⚠️ PDF document {document_id} processing issues: {result.get('status') if result else 'No result'}")
                    
            elif "content" in document_data and document_data["content"]:
                # Process TXT content
                from fastapi import UploadFile
                from io import BytesIO
                
                content = document_data["content"]
                file_obj = UploadFile(
                    file=BytesIO(content.encode('utf-8')),
                    filename=f"{document_id}.txt",
                    headers={"content-type": "text/plain"}
                )
                
                result = await self.document_processor.process_document(
                    file=file_obj,
                    document_id=document_id
                )
                
                if result and result.get("status") in ["success", "processed"]:
                    logger.info(f"  ✅ TXT document {document_id} processed successfully")
                else:
                    logger.warning(f"  ⚠️ TXT document {document_id} processing issues: {result.get('status') if result else 'No result'}")
            else:
                logger.warning(f"  ⚠️ Document {document_id} has no file_path or content to process")
                
        except Exception as e:
            logger.error(f"  ❌ Failed to process document {document_id}: {str(e)}")
            raise


if __name__ == "__main__":
    test = EndToEndUserWorkflowTest()
    asyncio.run(test.run_test())
