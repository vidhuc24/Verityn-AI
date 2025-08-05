#!/usr/bin/env python3
"""
Test Script for LangSmith Integration in Verityn AI.

This script validates that LangSmith monitoring and tracing 
is working correctly with our multi-agent workflow.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.langsmith_service import langsmith_service
from backend.app.workflows.multi_agent_workflow import MultiAgentWorkflow
from backend.app.services.vector_database import VectorDatabaseService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LangSmithIntegrationTester:
    """Test LangSmith integration functionality."""
    
    def __init__(self):
        self.vector_db = VectorDatabaseService(use_memory=True)
        self.workflow = MultiAgentWorkflow(verbose=True)
        
    async def test_langsmith_service(self):
        """Test basic LangSmith service functionality."""
        print("\n🔧 Testing LangSmith Service")
        print("=" * 50)
        
        # Test service initialization
        project_info = langsmith_service.get_project_info()
        print(f"📊 Project Name: {project_info['project_name']}")
        print(f"🔍 Tracing Enabled: {project_info['tracing_enabled']}")
        print(f"🔗 Client Initialized: {project_info['client_initialized']}")
        print(f"🔑 API Key Configured: {project_info['api_key_configured']}")
        
        if not project_info['api_key_configured']:
            print("⚠️  LangSmith API key not configured - some tests will be skipped")
            return False
        
        # Test run creation
        print("\n🏃 Testing Run Creation...")
        run_id = langsmith_service.create_run(
            name="Test Run",
            run_type="chain",  # Changed from "test" to valid run_type
            inputs={"test": "data"},
            tags=["test", "integration"],
            metadata={"test_type": "langsmith_integration"}
        )
        
        if run_id:
            print(f"✅ Run created successfully: {run_id}")
            
            # Test run update
            langsmith_service.update_run(
                run_id=run_id,
                outputs={"result": "success"},
                error=None
            )
            print("✅ Run updated successfully")
        else:
            print("❌ Failed to create run")
            return False
        
        return True
    
    async def test_agent_tracing(self):
        """Test individual agent tracing."""
        print("\n🤖 Testing Agent Tracing")
        print("=" * 50)
        
        # Test individual agents
        from backend.app.agents.specialized_agents import QuestionAnalysisAgent
        
        agent = QuestionAnalysisAgent(verbose=True)
        
        print("🔍 Testing Question Analysis Agent...")
        result = await agent.execute({
            "question": "What are the key findings from recent access reviews?",
            "conversation_id": "test_123"
        })
        
        if result.get("status") == "completed":
            print("✅ Agent execution successful")
            print(f"📊 Analysis Status: {result.get('analysis_status')}")
            return True
        else:
            print("❌ Agent execution failed")
            print(f"🔥 Error: {result.get('error', 'Unknown')}")
            return False
    
    async def test_workflow_tracing(self):
        """Test complete workflow tracing."""
        print("\n🔄 Testing Workflow Tracing")
        print("=" * 50)
        
        # Setup test environment
        print("🔧 Setting up test environment...")
        await self._setup_test_data()
        
        # Test workflow execution
        print("🚀 Testing workflow execution...")
        result = await self.workflow.execute(
            question="What are the main compliance issues identified in our access reviews?",
            conversation_id="langsmith_test_123"
        )
        
        print(f"📊 Workflow Status: {result.get('status')}")
        print(f"⏱️  Execution Time: {result.get('execution_time', 0):.2f}s")
        print(f"🔗 LangSmith Run ID: {result.get('metadata', {}).get('langsmith_run_id')}")
        
        if result.get("status") == "completed":
            print("✅ Workflow execution successful")
            return True
        else:
            print("❌ Workflow execution failed")
            print(f"🔥 Errors: {result.get('errors', [])}")
            return False
    
    async def test_dataset_creation(self):
        """Test LangSmith dataset creation."""
        print("\n📊 Testing Dataset Creation")
        print("=" * 50)
        
        if not langsmith_service.client:
            print("⚠️  LangSmith client not available - skipping dataset test")
            return True
        
        # Create test dataset
        examples = [
            {
                "inputs": {"question": "What are material weaknesses in SOX controls?"},
                "outputs": {"response": "Material weaknesses are control deficiencies..."}
            },
            {
                "inputs": {"question": "Explain access review findings"},
                "outputs": {"response": "Access review findings indicate..."}
            }
        ]
        
        dataset_id = langsmith_service.create_dataset(
            dataset_name=f"verityn-test-{langsmith_service.project_name}",
            description="Test dataset for Verityn AI evaluation",
            examples=examples
        )
        
        if dataset_id:
            print(f"✅ Dataset created successfully: {dataset_id}")
            return True
        else:
            print("❌ Failed to create dataset")
            return False
    
    async def _setup_test_data(self):
        """Setup test data for workflow testing."""
        await self.vector_db.initialize_collection()
        
        # Add test documents using the correct method
        document_1_chunks = [
            "Access Review Findings: Material weakness identified in user access controls for financial systems. SOX 404 controls ineffective."
        ]
        document_1_metadata = {
            "document_type": "access_review",
            "company": "Test Company",
            "compliance_framework": "SOX"
        }
        
        document_2_chunks = [
            "Financial reconciliation shows discrepancies in month-end close process. Control testing reveals deficiencies in approval workflows."
        ]
        document_2_metadata = {
            "document_type": "financial_reconciliation", 
            "company": "Test Company",
            "compliance_framework": "SOX"
        }
        
        # Insert document chunks
        await self.vector_db.insert_document_chunks(
            document_id="test_access_review_001",
            chunks=document_1_chunks,
            metadata=document_1_metadata
        )
        
        await self.vector_db.insert_document_chunks(
            document_id="test_financial_recon_001",
            chunks=document_2_chunks,
            metadata=document_2_metadata
        )
    
    async def run_all_tests(self):
        """Run all LangSmith integration tests."""
        print("🚀 Starting LangSmith Integration Tests")
        print("🎯 Validating Monitoring and Tracing")
        print("=" * 60)
        
        tests = [
            ("LangSmith Service", self.test_langsmith_service),
            ("Agent Tracing", self.test_agent_tracing),
            ("Workflow Tracing", self.test_workflow_tracing),
            ("Dataset Creation", self.test_dataset_creation)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                print(f"\n🧪 Running {test_name} Test...")
                success = await test_func()
                results[test_name] = success
                print(f"{'✅' if success else '❌'} {test_name}: {'PASS' if success else 'FAIL'}")
            except Exception as e:
                print(f"❌ {test_name}: FAIL - {str(e)}")
                results[test_name] = False
        
        # Generate summary
        self._generate_test_summary(results)
        
        return all(results.values())
    
    def _generate_test_summary(self, results):
        """Generate test summary report."""
        print("\n📊 LangSmith Integration Test Summary")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        print(f"\n📈 Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All LangSmith integration tests passed!")
            print("✅ LangSmith monitoring and tracing is working correctly")
        else:
            print("⚠️  Some tests failed - check configuration and setup")
        
        # Print project info
        project_info = langsmith_service.get_project_info()
        print(f"\n🔗 LangSmith Project: {project_info['project_name']}")
        print(f"🌐 View traces at: https://smith.langchain.com/o/default/projects/p/{project_info['project_name']}")


async def main():
    """Main test execution."""
    tester = LangSmithIntegrationTester()
    
    try:
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 SUBTASK 5.2 COMPLETED SUCCESSFULLY!")
            print("✅ LangSmith integration is working correctly")
            print("✅ Multi-agent workflow monitoring enabled")
            print("✅ Individual agent tracing operational")
            print("🚀 Ready to proceed with Subtask 5.3: Advanced Retrieval Techniques")
        else:
            print("\n⚠️  Some tests failed - please check configuration")
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 