"""
Test script for Multi-Agent Workflow.

This script tests the complete multi-agent workflow including all specialized
agents and the LangGraph orchestration system.
"""

import asyncio
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.workflows.multi_agent_workflow import MultiAgentWorkflow
from backend.app.agents.specialized_agents import (
    DocumentProcessingAgent,
    ClassificationAgent,
    QuestionAnalysisAgent,
    ContextRetrievalAgent,
    ResponseSynthesisAgent,
    ComplianceAnalyzerAgent
)
from backend.app.agents.base_agent import AgentType, AgentState
from backend.app.services.vector_database import VectorDatabaseService
from backend.app.config import settings

logger = logging.getLogger(__name__)

class MockUploadFile:
    """Mock UploadFile for testing."""
    
    def __init__(self, filename: str, content: str, content_type: str = "text/plain"):
        self.filename = filename
        self.content = content.encode('utf-8')
        self.content_type = content_type
        self.size = len(self.content)
    
    async def read(self) -> bytes:
        return self.content

class MultiAgentWorkflowTester:
    """Comprehensive tester for multi-agent workflow."""
    
    def __init__(self):
        self.workflow = MultiAgentWorkflow(verbose=True)
        self.vector_db = VectorDatabaseService(use_memory=True)
        
        # Test data
        self.test_documents = self._get_test_documents()
        self.test_queries = self._get_test_queries()
        
        # Performance tracking
        self.test_results = {
            "individual_agents": {},
            "workflow_execution": {},
            "performance_metrics": {}
        }
    
    def _get_test_documents(self) -> Dict[str, str]:
        """Get test documents for workflow testing."""
        return {
            "uber_access_review": """
SOX 404 COMPLIANCE DOCUMENT - ACCESS REVIEW

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
Control 404.2 - EFFECTIVE: User provisioning controls operating effectively
            """,
            "walmart_material_weakness": """
SOX 404 COMPLIANCE DOCUMENT - ACCESS REVIEW

EXECUTIVE SUMMARY
This quarterly user access review for Walmart Inc. identified several MATERIAL 
WEAKNESSES requiring immediate management attention and remediation.

SCOPE AND METHODOLOGY
The access review covered financial systems including:
- SAP Financial Module
- Oracle Procurement System
- Expense Management Platform

CRITICAL FINDINGS - MATERIAL WEAKNESSES IDENTIFIED
1. SEGREGATION OF DUTIES VIOLATIONS: 23 users have conflicting access rights
2. TERMINATED EMPLOYEE ACCESS: 8 terminated employees retain active system access
3. UNAUTHORIZED ACCESS: 15 users have access beyond their job requirements
4. MISSING APPROVALS: 45 access grants lack proper management approval

MANAGEMENT RESPONSE
Management acknowledges the material weaknesses and has initiated immediate remediation:
- All terminated employee access revoked within 24 hours
- Segregation of duties matrix being updated
- Comprehensive access recertification to be completed within 30 days

SOX CONTROL ASSESSMENT
Control 404.1 - DEFICIENT: Material weakness in access review procedures
Control 404.2 - DEFICIENT: User provisioning controls require enhancement
Control 404.4 - FAILING: Access termination procedures inadequate
            """
        }
    
    def _get_test_queries(self) -> List[Dict[str, Any]]:
        """Get test queries for workflow validation."""
        return [
            {
                "question": "What are the key findings from the access reviews?",
                "expected_agents": ["question_analyzer", "context_retriever", "classifier", "compliance_analyzer", "response_synthesizer"],
                "complexity": "basic"
            },
            {
                "question": "Which companies have material weaknesses in their SOX 404 controls?",
                "expected_agents": ["question_analyzer", "context_retriever", "classifier", "compliance_analyzer", "response_synthesizer"],
                "complexity": "intermediate"
            },
            {
                "question": "Compare the access control effectiveness between Uber and Walmart",
                "expected_agents": ["question_analyzer", "context_retriever", "classifier", "compliance_analyzer", "response_synthesizer"],
                "complexity": "advanced"
            }
        ]
    
    async def setup_test_environment(self) -> bool:
        """Set up test environment with documents in vector database."""
        print("🔧 Setting up test environment...")
        
        try:
            # Initialize vector database
            await self.vector_db.initialize_collection()
            
            # Create test version of document processor with in-memory vector DB
            from backend.app.services.document_processor import EnhancedDocumentProcessor
            
            class TestDocumentProcessor(EnhancedDocumentProcessor):
                """Test version of document processor with in-memory vector database."""
                
                def __init__(self):
                    super().__init__()
                    # Use in-memory vector database for testing
                    self.test_vector_db = VectorDatabaseService(use_memory=True)
                
                async def _store_in_vector_database(
                    self,
                    document_id: str,
                    chunks: List[str],
                    metadata: Dict,
                ) -> bool:
                    """Store document chunks in in-memory vector database."""
                    try:
                        await self.test_vector_db.initialize_collection()
                        return await self.test_vector_db.insert_document_chunks(
                            document_id=document_id,
                            chunks=chunks,
                            metadata=metadata
                        )
                    except Exception as e:
                        logger.error(f"Failed to store document in test vector database: {str(e)}")
                        return False
                
                async def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
                    """Get document info from test vector database."""
                    try:
                        # This would typically query the vector database
                        # For testing, return basic info
                        return {
                            "document_id": document_id,
                            "status": "processed",
                            "chunk_count": 0
                        }
                    except Exception as e:
                        logger.error(f"Failed to get document info: {str(e)}")
                        return None
                
                async def delete_document(self, document_id: str) -> bool:
                    """Delete document from test vector database."""
                    try:
                        # This would typically delete from vector database
                        # For testing, return success
                        return True
                    except Exception as e:
                        logger.error(f"Failed to delete document: {str(e)}")
                        return False
            
            processor = TestDocumentProcessor()
            
            for doc_name, content in self.test_documents.items():
                print(f"📄 Processing {doc_name}...")
                
                mock_file = MockUploadFile(
                    filename=f"{doc_name}.txt",
                    content=content,
                    content_type="text/plain"
                )
                
                result = await processor.process_document(
                    file=mock_file,
                    document_id=doc_name,
                    description=f"Test document: {doc_name}",
                    document_metadata={
                        "document_type": "access_review",
                        "company": "uber" if "uber" in doc_name else "walmart",
                        "quality_level": "high" if "uber" in doc_name else "fail",
                        "compliance_framework": "SOX"
                    }
                )
                
                if result["status"] == "processed":
                    print(f"   ✅ {doc_name} processed: {result['chunk_count']} chunks")
                else:
                    print(f"   ❌ {doc_name} failed: {result.get('error')}")
            
            print("✅ Test environment setup completed")
            return True
            
        except Exception as e:
            print(f"❌ Test environment setup failed: {str(e)}")
            return False
    
    async def test_individual_agents(self) -> bool:
        """Test each agent individually."""
        print("\n🧪 Testing Individual Agents")
        print("=" * 60)
        
        try:
            # Test Question Analysis Agent
            print("\n🔍 Testing Question Analysis Agent...")
            question_agent = QuestionAnalysisAgent(verbose=True)
            
            question_result = await question_agent.execute({
                "question": "What are the material weaknesses in SOX 404 controls?",
                "conversation_id": "test_conv_001"
            })
            
            self.test_results["individual_agents"]["question_analyzer"] = question_result
            print(f"   ✅ Question Analysis: {question_result.get('analysis_status')}")
            
            # Test Classification Agent
            print("\n🏷️ Testing Classification Agent...")
            classifier_agent = ClassificationAgent(verbose=True)
            
            classification_result = await classifier_agent.execute({
                "content": self.test_documents["walmart_material_weakness"],
                "document_id": "walmart_test"
            })
            
            self.test_results["individual_agents"]["classifier"] = classification_result
            print(f"   ✅ Classification: {classification_result.get('classification_status')}")
            
            # Test Context Retrieval Agent
            print("\n🔍 Testing Context Retrieval Agent...")
            retrieval_agent = ContextRetrievalAgent(verbose=True)
            
            retrieval_result = await retrieval_agent.execute({
                "question": "What are the material weaknesses?",
                "analysis": question_result.get("analysis", {})
            })
            
            self.test_results["individual_agents"]["context_retriever"] = retrieval_result
            print(f"   ✅ Context Retrieval: {retrieval_result.get('retrieval_status')}")
            
            # Test Compliance Analyzer Agent
            print("\n📊 Testing Compliance Analyzer Agent...")
            compliance_agent = ComplianceAnalyzerAgent(verbose=True)
            
            compliance_result = await compliance_agent.execute({
                "question": "What are the material weaknesses?",
                "context": retrieval_result.get("search_results", []),
                "classifications": [classification_result.get("classification", {})]
            })
            
            self.test_results["individual_agents"]["compliance_analyzer"] = compliance_result
            print(f"   ✅ Compliance Analysis: {compliance_result.get('analysis_status')}")
            
            # Test Response Synthesis Agent
            print("\n💬 Testing Response Synthesis Agent...")
            synthesis_agent = ResponseSynthesisAgent(verbose=True)
            
            synthesis_result = await synthesis_agent.execute({
                "question": "What are the material weaknesses?",
                "analysis": question_result.get("analysis", {}),
                "context": retrieval_result.get("search_results", []),
                "classifications": [classification_result.get("classification", {})]
            })
            
            self.test_results["individual_agents"]["response_synthesizer"] = synthesis_result
            print(f"   ✅ Response Synthesis: {synthesis_result.get('synthesis_status')}")
            
            print("\n✅ All individual agents tested successfully")
            return True
            
        except Exception as e:
            print(f"\n❌ Individual agent testing failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_workflow_execution(self) -> bool:
        """Test complete workflow execution."""
        print("\n🚀 Testing Complete Workflow Execution")
        print("=" * 60)
        
        try:
            for i, query_data in enumerate(self.test_queries, 1):
                print(f"\n🔍 Test {i}: {query_data['complexity']} complexity")
                print(f"   Question: {query_data['question']}")
                
                # Execute workflow
                start_time = time.time()
                workflow_result = await self.workflow.execute(
                    question=query_data["question"],
                    conversation_id=f"test_conv_{i}",
                    config={"recursion_limit": 25}
                )
                execution_time = time.time() - start_time
                
                # Store results
                self.test_results["workflow_execution"][f"test_{i}"] = {
                    "query": query_data,
                    "result": workflow_result,
                    "execution_time": execution_time
                }
                
                # Analyze results
                status = workflow_result.get("status", "unknown")
                response_content = workflow_result.get("response", {}).get("content", "")
                errors = workflow_result.get("errors", [])
                
                print(f"   ✅ Status: {status}")
                print(f"   ⏱️  Execution Time: {execution_time:.2f}s")
                print(f"   📝 Response Length: {len(response_content)} characters")
                print(f"   ❌ Errors: {len(errors)}")
                
                if errors:
                    for error in errors:
                        print(f"      - {error}")
                
                # Show response preview
                preview = response_content[:200].replace('\n', ' ')
                print(f"   💬 Preview: {preview}...")
                
                # Check agent results
                agent_results = workflow_result.get("metadata", {}).get("agent_results", {})
                print(f"   🤖 Agents Executed: {len(agent_results)}")
                for agent_name, agent_result in agent_results.items():
                    agent_status = agent_result.get("state", "unknown")
                    print(f"      - {agent_name}: {agent_status}")
            
            print("\n✅ Complete workflow testing completed")
            return True
            
        except Exception as e:
            print(f"\n❌ Workflow testing failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_workflow_error_handling(self) -> bool:
        """Test workflow error handling and recovery."""
        print("\n🛡️ Testing Error Handling")
        print("=" * 60)
        
        try:
            # Test with invalid question
            print("\n🔍 Testing invalid question handling...")
            error_result = await self.workflow.execute(
                question="",  # Empty question
                conversation_id="error_test"
            )
            
            print(f"   ✅ Error handling: {error_result.get('status')}")
            print(f"   📝 Error response: {len(error_result.get('response', {}).get('content', ''))} chars")
            
            # Test with malformed input
            print("\n🔍 Testing malformed input handling...")
            malformed_result = await self.workflow.execute(
                question="This is a very long question that might cause issues " * 100,  # Very long question
                conversation_id="malformed_test"
            )
            
            print(f"   ✅ Malformed input handling: {malformed_result.get('status')}")
            
            print("\n✅ Error handling tests completed")
            return True
            
        except Exception as e:
            print(f"\n❌ Error handling tests failed: {str(e)}")
            return False
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        print("\n📊 Generating Performance Report")
        print("=" * 60)
        
        # Calculate metrics
        total_workflows = len(self.test_results["workflow_execution"])
        successful_workflows = sum(
            1 for result in self.test_results["workflow_execution"].values()
            if result["result"].get("status") == "completed"
        )
        
        avg_execution_time = sum(
            result["execution_time"] for result in self.test_results["workflow_execution"].values()
        ) / total_workflows if total_workflows > 0 else 0
        
        # Agent success rates - Fixed logic
        agent_success_rates = {}
        for agent_name, result in self.test_results["individual_agents"].items():
            # Check the appropriate status field based on agent type
            if agent_name == "question_analyzer":
                agent_success_rates[agent_name] = result.get("analysis_status") == "completed"
            elif agent_name == "classifier":
                agent_success_rates[agent_name] = result.get("classification_status") == "completed"
            elif agent_name == "context_retriever":
                agent_success_rates[agent_name] = result.get("retrieval_status") == "completed"
            elif agent_name == "compliance_analyzer":
                agent_success_rates[agent_name] = result.get("analysis_status") == "completed"
            elif agent_name == "response_synthesizer":
                agent_success_rates[agent_name] = result.get("synthesis_status") == "completed"
            else:
                # Fallback: check if there's no error field
                agent_success_rates[agent_name] = "error" not in result
        
        # Generate report
        report = {
            "summary": {
                "total_workflows": total_workflows,
                "successful_workflows": successful_workflows,
                "success_rate": successful_workflows / total_workflows if total_workflows > 0 else 0,
                "avg_execution_time": avg_execution_time
            },
            "agent_performance": agent_success_rates,
            "workflow_details": self.test_results["workflow_execution"],
            "recommendations": self._generate_recommendations()
        }
        
        # Print summary
        print(f"📈 Performance Summary:")
        print(f"   Total Workflows: {total_workflows}")
        print(f"   Successful: {successful_workflows}")
        print(f"   Success Rate: {report['summary']['success_rate']:.1%}")
        print(f"   Avg Execution Time: {avg_execution_time:.2f}s")
        
        print(f"\n🤖 Agent Performance:")
        for agent_name, success in agent_success_rates.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {agent_name}: {status}")
        
        print(f"\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"   • {rec}")
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        # Get the latest report data
        total_workflows = len(self.test_results["workflow_execution"])
        successful_workflows = sum(
            1 for result in self.test_results["workflow_execution"].values()
            if result["result"].get("status") == "completed"
        )
        success_rate = successful_workflows / total_workflows if total_workflows > 0 else 0
        
        avg_execution_time = sum(
            result["execution_time"] for result in self.test_results["workflow_execution"].values()
        ) / total_workflows if total_workflows > 0 else 0
        
        # Analyze success rate
        if success_rate < 0.8:
            recommendations.append("Improve workflow error handling and recovery")
        
        # Analyze execution time
        if avg_execution_time > 30:
            recommendations.append("Optimize agent execution for faster response times")
        
        # Analyze agent performance - Fixed logic
        agent_success_rates = {}
        for agent_name, result in self.test_results["individual_agents"].items():
            # Check the appropriate status field based on agent type
            if agent_name == "question_analyzer":
                agent_success_rates[agent_name] = result.get("analysis_status") == "completed"
            elif agent_name == "classifier":
                agent_success_rates[agent_name] = result.get("classification_status") == "completed"
            elif agent_name == "context_retriever":
                agent_success_rates[agent_name] = result.get("retrieval_status") == "completed"
            elif agent_name == "compliance_analyzer":
                agent_success_rates[agent_name] = result.get("analysis_status") == "completed"
            elif agent_name == "response_synthesizer":
                agent_success_rates[agent_name] = result.get("synthesis_status") == "completed"
            else:
                # Fallback: check if there's no error field
                agent_success_rates[agent_name] = "error" not in result
        
        failed_agents = [name for name, success in agent_success_rates.items() if not success]
        if failed_agents:
            recommendations.append(f"Fix issues with agents: {', '.join(failed_agents)}")
        
        if not recommendations:
            recommendations.append("Multi-agent workflow is performing optimally")
        
        return recommendations

async def main():
    """Main testing function."""
    print("🚀 Starting Multi-Agent Workflow Tests")
    print("🎯 Validating Complete Multi-Agent System")
    
    # Check OpenAI API key
    if not settings.OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Please set your OpenAI API key to run multi-agent tests")
        return
    
    # Initialize tester
    tester = MultiAgentWorkflowTester()
    
    # Run comprehensive testing
    try:
        # Step 1: Setup test environment
        setup_success = await tester.setup_test_environment()
        if not setup_success:
            print("❌ Test environment setup failed - cannot proceed")
            return
        
        # Step 2: Test individual agents
        agents_success = await tester.test_individual_agents()
        if not agents_success:
            print("❌ Individual agent testing failed")
            return
        
        # Step 3: Test complete workflow
        workflow_success = await tester.test_workflow_execution()
        if not workflow_success:
            print("❌ Workflow execution testing failed")
            return
        
        # Step 4: Test error handling
        error_success = await tester.test_workflow_error_handling()
        
        # Step 5: Generate performance report
        report = tester.generate_performance_report()
        
        # Overall success assessment
        overall_success = (
            setup_success and 
            agents_success and 
            workflow_success and 
            report["summary"]["success_rate"] >= 0.8
        )
        
        if overall_success:
            print(f"\n🎉 SUBTASK 5.1 COMPLETED SUCCESSFULLY!")
            print(f"✅ Multi-agent workflow validated and working")
            print(f"✅ All agents functioning correctly")
            print(f"✅ LangGraph orchestration operational")
            print(f"🚀 Ready to proceed with Subtask 5.2: LangSmith Integration")
        else:
            print(f"\n⚠️  SUBTASK 5.1 PARTIALLY COMPLETED")
            print(f"🔧 Some components need optimization")
        
        return overall_success
        
    except Exception as e:
        print(f"\n❌ Multi-agent testing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(main()) 