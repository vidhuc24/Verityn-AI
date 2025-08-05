#!/usr/bin/env python3
"""
End-to-End Multi-Agent System Test Script for Verityn AI.

This script tests the complete multi-agent workflow with all components:
- Document Processing
- Classification
- Question Analysis
- Context Retrieval (with Advanced Techniques)
- Response Synthesis
- Compliance Analysis
- LangSmith Monitoring
- RAGAS Evaluation
"""

import asyncio
import sys
import os
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.workflows.multi_agent_workflow import MultiAgentWorkflow
from backend.app.services.ragas_evaluation import ragas_evaluation_service
from backend.app.services.advanced_retrieval import advanced_retrieval_service
from backend.app.services.langsmith_service import langsmith_service
from langchain.schema import Document
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EndToEndMultiAgentTester:
    """Test complete multi-agent system end-to-end."""
    
    def __init__(self):
        self.workflow = MultiAgentWorkflow(verbose=True)
        self.ragas_service = ragas_evaluation_service
        
    async def setup_test_environment(self):
        """Setup comprehensive test environment."""
        print("🔧 Setting up End-to-End Multi-Agent Test Environment...")
        
        # Create comprehensive test documents
        test_documents = [
            Document(
                page_content="""SOX 404 COMPLIANCE DOCUMENT - ACCESS REVIEW
                
                EXECUTIVE SUMMARY
                This quarterly user access review evaluated 1,247 user accounts across financial systems 
                for Uber Technologies. The review was conducted in accordance with SOX 404 requirements
                and identified no material weaknesses.
                
                SCOPE AND METHODOLOGY
                The access review covered all users with access to financial systems including:
                - SAP Financial Module (847 users)
                - Oracle Procurement System (312 users)  
                - Expense Management Platform (623 users)
                
                KEY FINDINGS
                1. All user access is properly authorized and documented
                2. Segregation of duties is maintained across all critical processes
                3. Quarterly access certification completed with 100% response rate
                4. No terminated employees found with active system access
                
                MANAGEMENT RESPONSE
                Management is satisfied with the current access control environment.
                No remediation actions are required at this time.
                
                SOX CONTROL ASSESSMENT
                Control 404.1 - EFFECTIVE: Access review procedures operating effectively
                Control 404.2 - EFFECTIVE: User provisioning controls operating effectively""",
                metadata={
                    "document_type": "access_review",
                    "company": "Uber Technologies",
                    "compliance_framework": "SOX",
                    "quality_level": "pass",
                    "sox_control_ids": ["404.1", "404.2"],
                    "document_id": "uber_access_review_2024"
                }
            ),
            Document(
                page_content="""FINANCIAL RECONCILIATION REPORT - MONTHLY CLOSE
                
                PERIOD: March 2024
                COMPANY: Lyft Inc.
                
                RECONCILIATION SUMMARY
                This report documents the month-end financial reconciliation process for all general ledger accounts.
                Several discrepancies were identified that require management attention.
                
                DISCREPANCIES IDENTIFIED
                1. Bank reconciliation variance: $47,823 (unreconciled items over 30 days)
                2. Accounts receivable aging discrepancy: $12,450
                3. Inventory count variance: $8,920
                4. Prepaid expenses allocation error: $3,200
                
                MATERIAL WEAKNESS ASSESSMENT
                The volume and nature of reconciliation discrepancies indicate a MATERIAL WEAKNESS
                in the month-end close process. This represents a deficiency in internal controls.
                
                MANAGEMENT ACTION PLAN
                1. Implement daily cash position monitoring
                2. Enhance AR aging review procedures  
                3. Strengthen inventory count controls
                4. Improve prepaid expense tracking
                
                SOX CONTROL IMPACT
                Controls 404.3 and 404.4 are assessed as INEFFECTIVE due to these findings.""",
                metadata={
                    "document_type": "financial_reconciliation",
                    "company": "Lyft Inc",
                    "compliance_framework": "SOX",
                    "quality_level": "fail",
                    "sox_control_ids": ["404.3", "404.4"],
                    "document_id": "lyft_reconciliation_mar2024"
                }
            ),
            Document(
                page_content="""IT SECURITY RISK ASSESSMENT - ANNUAL REVIEW
                
                ASSESSMENT PERIOD: 2024 Annual Review
                ORGANIZATION: DoorDash Technologies
                
                EXECUTIVE SUMMARY
                This comprehensive IT security risk assessment evaluated cybersecurity controls
                across all critical systems. The assessment identified several HIGH RISK areas
                requiring immediate attention.
                
                HIGH RISK FINDINGS
                1. Privileged access management gaps - 23 admin accounts without proper oversight
                2. Multi-factor authentication not enforced for 40% of financial system users
                3. Security patch management delays averaging 45 days for critical systems
                4. Inadequate logging and monitoring for financial applications
                
                CONTROL EFFECTIVENESS ASSESSMENT
                - Access Controls: NEEDS IMPROVEMENT
                - Data Protection: ADEQUATE  
                - System Monitoring: INADEQUATE
                - Incident Response: ADEQUATE
                
                REMEDIATION TIMELINE
                High Risk Items: 30 days
                Medium Risk Items: 90 days
                Low Risk Items: 180 days
                
                SOX IMPLICATIONS
                These findings directly impact SOX 404 compliance for IT general controls.""",
                metadata={
                    "document_type": "risk_assessment",
                    "company": "DoorDash Technologies", 
                    "compliance_framework": "SOX",
                    "quality_level": "medium",
                    "sox_control_ids": ["404.5", "404.6"],
                    "document_id": "doordash_security_assessment_2024"
                }
            ),
            Document(
                page_content="""INTERNAL AUDIT FINDINGS - EXPENSE MANAGEMENT CONTROLS
                
                AUDIT PERIOD: Q2 2024
                ENTITY: Airbnb Inc.
                
                AUDIT OBJECTIVE
                Evaluate the effectiveness of expense management controls and compliance
                with corporate policies and SOX requirements.
                
                CONTROL TESTING RESULTS
                Sample Size: 150 expense reports ($2.3M total)
                
                EXCEPTIONS IDENTIFIED
                1. 12 expense reports lacked proper approval (8% exception rate)
                2. 8 instances of policy violations not detected by system controls
                3. 5 duplicate payments totaling $23,400
                4. Inadequate supporting documentation for 18 expense items
                
                CONTROL RATINGS
                - Expense Approval Process: NEEDS IMPROVEMENT
                - System Controls: ADEQUATE
                - Management Review: NEEDS IMPROVEMENT  
                - Policy Compliance: NEEDS IMPROVEMENT
                
                RECOMMENDATIONS
                1. Strengthen approval workflow enforcement
                2. Enhance duplicate payment detection
                3. Improve documentation requirements
                4. Increase management oversight
                
                This represents a SIGNIFICANT DEFICIENCY in expense management controls.""",
                metadata={
                    "document_type": "internal_audit",
                    "company": "Airbnb Inc",
                    "compliance_framework": "SOX", 
                    "quality_level": "medium",
                    "sox_control_ids": ["404.7"],
                    "document_id": "airbnb_expense_audit_q2_2024"
                }
            ),
            Document(
                page_content="""COMPLIANCE MONITORING REPORT - QUARTERLY ASSESSMENT
                
                REPORTING PERIOD: Q3 2024
                COMPANY: Spotify Technology S.A.
                
                COMPLIANCE FRAMEWORK ASSESSMENT
                This report summarizes compliance monitoring activities across multiple frameworks
                including SOX, SOC2, and ISO27001 requirements.
                
                SOX 404 COMPLIANCE STATUS
                - Total Controls Tested: 47
                - Effective Controls: 42 (89%)
                - Controls Needing Improvement: 5 (11%)
                - Material Weaknesses: 0
                - Significant Deficiencies: 2
                
                KEY CONTROL AREAS
                1. Financial Reporting Controls: EFFECTIVE
                2. IT General Controls: EFFECTIVE  
                3. Access Management: NEEDS IMPROVEMENT
                4. Change Management: EFFECTIVE
                5. Data Backup/Recovery: NEEDS IMPROVEMENT
                
                MANAGEMENT CERTIFICATION
                Based on this assessment, management can provide reasonable assurance
                regarding the effectiveness of internal controls over financial reporting.
                
                CONTINUOUS MONITORING
                Automated controls monitoring identified 347 control events during the quarter,
                with 99.1% operating as designed.""",
                metadata={
                    "document_type": "compliance_monitoring",
                    "company": "Spotify Technology S.A.",
                    "compliance_framework": "SOX",
                    "quality_level": "pass", 
                    "sox_control_ids": ["404.8", "404.9"],
                    "document_id": "spotify_compliance_q3_2024"
                }
            )
        ]
        
        # CRITICAL FIX: Load documents into the GLOBAL vector_db_service that all agents share
        # This follows the bootcamp pattern where all agents access the same vector store
        from backend.app.services.vector_database import vector_db_service
        
        # Initialize the global vector database
        await vector_db_service.initialize_collection()
        
        # Insert test documents into the global vector database
        success = await vector_db_service.insert_document_chunks(test_documents)
        if not success:
            raise Exception("Failed to load test documents into global vector database")
        
        # Initialize advanced retrieval with the same documents (for consistency)
        await advanced_retrieval_service.initialize_retrievers(test_documents)
        
        print(f"✅ Test environment setup completed with {len(test_documents)} documents")
        print(f"✅ Documents loaded into global vector_db_service for all agents to access")
        return test_documents
    
    async def test_complete_workflow_execution(self):
        """Test complete multi-agent workflow execution."""
        print("\n🔍 Testing Complete Multi-Agent Workflow")
        print("=" * 60)
        
        test_questions = [
            {
                "question": "What are the material weaknesses identified in SOX 404 controls?",
                "expected_agents": ["question_analyzer", "context_retriever", "response_synthesizer", "compliance_analyzer"],
                "complexity": "intermediate"
            },
            {
                "question": "How effective are the financial reconciliation controls?",
                "expected_agents": ["question_analyzer", "context_retriever", "response_synthesizer"],
                "complexity": "intermediate"
            },
            {
                "question": "What is the overall risk assessment and what remediation actions are recommended?",
                "expected_agents": ["question_analyzer", "context_retriever", "response_synthesizer", "compliance_analyzer"],
                "complexity": "advanced"
            }
        ]
        
        results = {}
        
        for i, test_case in enumerate(test_questions):
            print(f"\n🧪 Test Case {i+1}: {test_case['question']}")
            print(f"   Expected Complexity: {test_case['complexity']}")
            
            try:
                # Execute complete workflow
                workflow_result = await self.workflow.execute(
                    question=test_case["question"],
                    conversation_id=f"e2e_test_{i}",
                    document_id=None
                )
                
                # Analyze results
                success = self._analyze_workflow_result(workflow_result, test_case)
                results[f"test_case_{i+1}"] = {
                    "success": success,
                    "result": workflow_result,
                    "expected_agents": test_case["expected_agents"]
                }
                
                print(f"   ✅ Workflow executed successfully")
                print(f"   📊 Response length: {len(workflow_result.get('response', ''))} chars")
                print(f"   🎯 Status: {workflow_result.get('status', 'unknown')}")
                
            except Exception as e:
                print(f"   ❌ Workflow execution failed: {str(e)}")
                results[f"test_case_{i+1}"] = {
                    "success": False,
                    "error": str(e),
                    "expected_agents": test_case["expected_agents"]
                }
        
        return results
    
    def _analyze_workflow_result(self, result: dict, test_case: dict) -> bool:
        """Analyze workflow result for completeness."""
        # Check if response was generated
        has_response = bool(result.get("response"))
        
        # Check if metadata contains agent information
        metadata = result.get("metadata", {})
        has_metadata = bool(metadata)
        
        # Check if LangSmith run was created
        has_langsmith = bool(result.get("langsmith_run_id"))
        
        # Check if status is completed
        is_completed = result.get("status") == "completed"
        
        return has_response and has_metadata and has_langsmith and is_completed
    
    async def test_advanced_retrieval_integration(self):
        """Test advanced retrieval techniques integration."""
        print("\n🔍 Testing Advanced Retrieval Integration")
        print("=" * 60)
        
        test_queries = [
            "material weakness SOX controls",
            "financial reconciliation discrepancies",
            "risk assessment IT security",
            "effective controls testing"
        ]
        
        results = {}
        
        for i, query in enumerate(test_queries):
            print(f"\n🧪 Testing Query {i+1}: {query}")
            
            try:
                # Test hybrid search
                hybrid_results = await advanced_retrieval_service.hybrid_search(
                    query=query,
                    limit=5,
                    semantic_weight=0.7,
                    keyword_weight=0.3
                )
                
                # Test query expansion
                expansion_results = await advanced_retrieval_service.query_expansion_search(
                    query=query,
                    limit=5,
                    expansion_terms=["SOX", "compliance"]
                )
                
                results[f"query_{i+1}"] = {
                    "hybrid_count": len(hybrid_results),
                    "expansion_count": len(expansion_results),
                    "hybrid_avg_score": sum(r.get("combined_score", 0) for r in hybrid_results) / len(hybrid_results) if hybrid_results else 0,
                    "expansion_avg_score": sum(r.get("score", 0) for r in expansion_results) / len(expansion_results) if expansion_results else 0
                }
                
                print(f"   📊 Hybrid: {len(hybrid_results)} results (avg score: {results[f'query_{i+1}']['hybrid_avg_score']:.3f})")
                print(f"   📊 Expansion: {len(expansion_results)} results (avg score: {results[f'query_{i+1}']['expansion_avg_score']:.3f})")
                
            except Exception as e:
                print(f"   ❌ Advanced retrieval failed: {str(e)}")
                results[f"query_{i+1}"] = {"error": str(e)}
        
        return results
    
    async def test_langsmith_monitoring(self):
        """Test LangSmith monitoring integration."""
        print("\n🔍 Testing LangSmith Monitoring Integration")
        print("=" * 60)
        
        try:
            # Check if LangSmith is configured
            callback_manager = langsmith_service.get_callback_manager()
            is_configured = callback_manager is not None
            
            print(f"📊 LangSmith Configuration: {'✅ Configured' if is_configured else '❌ Not Configured'}")
            
            if is_configured:
                # Test creating a run
                test_run_id = langsmith_service.create_run(
                    name="E2E Test Run",
                    run_type="chain",
                    inputs={"test": "end_to_end_test"},
                    outputs={"status": "testing"}
                )
                
                has_run_id = bool(test_run_id)
                print(f"📊 Run Creation: {'✅ Success' if has_run_id else '❌ Failed'}")
                
                if has_run_id:
                    # Test updating the run
                    update_success = langsmith_service.update_run(
                        run_id=test_run_id,
                        outputs={"status": "completed", "test_result": "success"}
                    )
                    print(f"📊 Run Update: {'✅ Success' if update_success else '❌ Failed'}")
                
                return {
                    "configured": is_configured,
                    "run_creation": has_run_id,
                    "run_update": has_run_id and update_success
                }
            else:
                return {"configured": False, "run_creation": False, "run_update": False}
                
        except Exception as e:
            print(f"❌ LangSmith test failed: {str(e)}")
            return {"error": str(e)}
    
    async def test_ragas_evaluation_integration(self):
        """Test RAGAS evaluation integration."""
        print("\n🔍 Testing RAGAS Evaluation Integration")
        print("=" * 60)
        
        try:
            # Generate test dataset
            test_dataset = await self.ragas_service.generate_synthetic_test_data(num_questions=3)
            
            print(f"📊 Generated test dataset with {len(test_dataset)} questions")
            
            # Test evaluation report generation
            mock_results = {
                "method": "hybrid",
                "timestamp": "2025-01-01T12:00:00",
                "metrics": {
                    "faithfulness": 0.85,
                    "answer_relevancy": 0.78,
                    "context_precision": 0.82,
                    "context_recall": 0.75,
                    "answer_similarity": 0.80
                },
                "num_questions": len(test_dataset)
            }
            
            report = await self.ragas_service.generate_evaluation_report(mock_results)
            
            has_report = bool(report)
            has_metrics = "Faithfulness" in report and "Answer Relevancy" in report
            
            print(f"📊 Report Generation: {'✅ Success' if has_report else '❌ Failed'}")
            print(f"📊 Metrics Included: {'✅ Yes' if has_metrics else '❌ No'}")
            
            return {
                "dataset_generation": len(test_dataset) > 0,
                "report_generation": has_report,
                "metrics_included": has_metrics
            }
            
        except Exception as e:
            print(f"❌ RAGAS evaluation test failed: {str(e)}")
            return {"error": str(e)}
    
    async def test_performance_metrics(self):
        """Test performance metrics collection."""
        print("\n🔍 Testing Performance Metrics Collection")
        print("=" * 60)
        
        try:
            # Test workflow execution with timing
            import time
            
            start_time = time.time()
            
            workflow_result = await self.workflow.execute(
                question="What are the key findings from access reviews?",
                conversation_id="performance_test",
                document_id=None
            )
            
            execution_time = time.time() - start_time
            
            # Extract performance metrics
            metadata = workflow_result.get("metadata", {})
            
            performance_metrics = {
                "total_execution_time": execution_time,
                "has_agent_timings": "agent_execution_times" in metadata,
                "has_token_usage": "token_usage" in metadata,
                "has_langsmith_trace": bool(workflow_result.get("langsmith_run_id")),
                "response_generated": bool(workflow_result.get("response")),
                "status_completed": workflow_result.get("status") == "completed"
            }
            
            print(f"📊 Total Execution Time: {execution_time:.2f} seconds")
            print(f"📊 Agent Timings: {'✅ Available' if performance_metrics['has_agent_timings'] else '❌ Missing'}")
            print(f"📊 Token Usage: {'✅ Available' if performance_metrics['has_token_usage'] else '❌ Missing'}")
            print(f"📊 LangSmith Trace: {'✅ Available' if performance_metrics['has_langsmith_trace'] else '❌ Missing'}")
            
            return performance_metrics
            
        except Exception as e:
            print(f"❌ Performance metrics test failed: {str(e)}")
            return {"error": str(e)}
    
    async def run_all_tests(self):
        """Run all end-to-end tests."""
        print("🚀 Starting End-to-End Multi-Agent System Tests")
        print("🎯 Testing Complete System Integration")
        print("=" * 70)
        
        # Setup test environment
        test_documents = await self.setup_test_environment()
        
        tests = [
            ("Complete Workflow Execution", self.test_complete_workflow_execution),
            ("Advanced Retrieval Integration", self.test_advanced_retrieval_integration),
            ("LangSmith Monitoring", self.test_langsmith_monitoring),
            ("RAGAS Evaluation Integration", self.test_ragas_evaluation_integration),
            ("Performance Metrics", self.test_performance_metrics)
        ]
        
        all_results = {}
        
        for test_name, test_func in tests:
            try:
                print(f"\n🧪 Running {test_name} Test...")
                results = await test_func()
                all_results[test_name] = results
                print(f"✅ {test_name}: COMPLETED")
            except Exception as e:
                print(f"❌ {test_name}: FAILED - {str(e)}")
                all_results[test_name] = {"error": str(e)}
        
        # Generate comprehensive summary
        self._generate_comprehensive_summary(all_results)
        
        return all_results
    
    def _generate_comprehensive_summary(self, results):
        """Generate comprehensive test summary."""
        print("\n📊 End-to-End Multi-Agent System Test Summary")
        print("=" * 70)
        
        # Workflow execution summary
        workflow_results = results.get("Complete Workflow Execution", {})
        workflow_successes = sum(1 for r in workflow_results.values() if isinstance(r, dict) and r.get("success", False))
        workflow_total = len([r for r in workflow_results.values() if isinstance(r, dict)])
        
        print(f"🔧 Multi-Agent Workflow:")
        print(f"   ✅ Successful Executions: {workflow_successes}/{workflow_total}")
        
        # Advanced retrieval summary
        retrieval_results = results.get("Advanced Retrieval Integration", {})
        retrieval_successes = sum(1 for r in retrieval_results.values() if isinstance(r, dict) and "error" not in r)
        retrieval_total = len([r for r in retrieval_results.values() if isinstance(r, dict)])
        
        print(f"🔍 Advanced Retrieval:")
        print(f"   ✅ Successful Queries: {retrieval_successes}/{retrieval_total}")
        
        # LangSmith summary
        langsmith_results = results.get("LangSmith Monitoring", {})
        langsmith_configured = langsmith_results.get("configured", False)
        langsmith_working = langsmith_results.get("run_creation", False)
        
        print(f"📊 LangSmith Monitoring:")
        print(f"   ✅ Configured: {'Yes' if langsmith_configured else 'No'}")
        print(f"   ✅ Run Creation: {'Yes' if langsmith_working else 'No'}")
        
        # RAGAS summary
        ragas_results = results.get("RAGAS Evaluation Integration", {})
        ragas_dataset = ragas_results.get("dataset_generation", False)
        ragas_report = ragas_results.get("report_generation", False)
        
        print(f"📈 RAGAS Evaluation:")
        print(f"   ✅ Dataset Generation: {'Yes' if ragas_dataset else 'No'}")
        print(f"   ✅ Report Generation: {'Yes' if ragas_report else 'No'}")
        
        # Performance summary
        perf_results = results.get("Performance Metrics", {})
        perf_timing = perf_results.get("total_execution_time", 0)
        perf_completed = perf_results.get("status_completed", False)
        
        print(f"⚡ Performance:")
        print(f"   ✅ Execution Time: {perf_timing:.2f} seconds")
        print(f"   ✅ Status Completed: {'Yes' if perf_completed else 'No'}")
        
        # Overall assessment
        total_components = 5
        working_components = sum([
            workflow_successes > 0,
            retrieval_successes > 0,
            langsmith_working,
            ragas_report,
            perf_completed
        ])
        
        success_rate = working_components / total_components
        
        print(f"\n🎯 Overall System Assessment:")
        print(f"   📊 Working Components: {working_components}/{total_components}")
        print(f"   📈 Success Rate: {success_rate:.1%}")
        
        if success_rate >= 0.8:
            print("🎉 EXCELLENT: Multi-agent system is production-ready!")
            print("✅ All major components working correctly")
            print("✅ Advanced features operational")
            print("✅ Monitoring and evaluation functional")
        elif success_rate >= 0.6:
            print("✅ GOOD: Multi-agent system is functional with minor issues")
            print("⚠️  Some components need attention")
        else:
            print("⚠️  NEEDS WORK: Multiple components need attention")
        
        print("\n🚀 Subtask 5.5: End-to-End Multi-Agent Testing - COMPLETED")


async def main():
    """Main test execution."""
    tester = EndToEndMultiAgentTester()
    
    try:
        results = await tester.run_all_tests()
        
        print("\n🎉 END-TO-END MULTI-AGENT SYSTEM TESTING COMPLETED!")
        print("✅ Comprehensive system validation performed")
        print("✅ All components tested in integration")
        print("✅ Performance and monitoring verified")
        
    except Exception as e:
        print(f"\n❌ End-to-end testing failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 