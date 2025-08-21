#!/usr/bin/env python3
"""
Test script for enhanced multi-agent workflow with regulatory search.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.workflows.multi_agent_workflow import MultiAgentWorkflow


async def test_enhanced_workflow():
    """Test the enhanced multi-agent workflow with regulatory search."""
    print("🧪 Testing Enhanced Multi-Agent Workflow with Regulatory Search...")
    print("=" * 70)
    
    # Initialize the workflow
    workflow = MultiAgentWorkflow(verbose=True)
    
    # Test data
    test_state = {
        "question": "What are the key SOX compliance issues in this access review?",
        "conversation_id": "test_conv_001",
        "document_id": "test_doc_001",
        "question_analysis": None,
        "context_retrieval": None,
        "document_classifications": None,
        "compliance_analysis": None,
        "regulatory_context": None,
        "final_response": None,
        "workflow_id": "",
        "start_time": "",
        "current_step": "",
        "agent_results": {},
        "errors": [],
        "status": ""
    }
    
    print("\n1️⃣ Testing workflow initialization...")
    print(f"   Question: {test_state['question']}")
    print(f"   Conversation ID: {test_state['conversation_id']}")
    
    # Test the workflow step by step
    try:
        # Initialize workflow
        state = await workflow._initialize_workflow(test_state)
        print(f"   ✅ Workflow initialized: {state['workflow_id']}")
        
        # Analyze question
        state = await workflow._analyze_question(state)
        print(f"   ✅ Question analyzed: {state.get('question_analysis', {}).get('analysis_status', 'unknown')}")
        
        # Retrieve context (mock data for testing)
        state["context_retrieval"] = {
            "search_results": [
                {
                    "document_id": "doc_001",
                    "document_type": "access_review",
                    "company": "TestCorp",
                    "display_name": "access_review_2024.pdf",
                    "chunk_text": "User access review findings indicate several users have excessive permissions that violate segregation of duties principles."
                }
            ],
            "retrieval_status": "completed"
        }
        print("   ✅ Context retrieval (mock data added)")
        
        # Classify documents
        state["document_classifications"] = [
            {
                "document_type": "access_review",
                "risk_level": "high",
                "compliance_frameworks": ["SOX"]
            }
        ]
        print("   ✅ Document classifications (mock data added)")
        
        # Analyze compliance
        state["compliance_analysis"] = {
            "analysis_status": "completed",
            "risk_assessment": {"overall_risk": "high"}
        }
        print("   ✅ Compliance analysis (mock data added)")
        
        # Test regulatory search
        print("\n2️⃣ Testing regulatory search step...")
        state = await workflow._regulatory_search(state)
        
        if state.get("regulatory_context"):
            regulatory_result = state["regulatory_context"]
            if regulatory_result.get("success"):
                print("   ✅ Regulatory search successful!")
                print(f"      Insights found: {len(regulatory_result.get('compliance_insights', []))}")
                if regulatory_result.get("compliance_insights"):
                    first_insight = regulatory_result["compliance_insights"][0]
                    print(f"      Top insight: {first_insight.get('compliance_focus', 'Unknown')}")
            else:
                print("   ✅ Regulatory search completed with fallback")
                print(f"      Fallback message: {regulatory_result.get('fallback_message', 'None')}")
        else:
            print("   ❌ Regulatory search failed")
        
        # Test response synthesis
        print("\n3️⃣ Testing response synthesis with regulatory context...")
        state = await workflow._synthesize_response(state)
        
        if state.get("final_response"):
            response = state["final_response"]
            if response.get("synthesis_status") == "completed":
                print("   ✅ Response synthesis successful!")
                print(f"      Regulatory context used: {response.get('regulatory_context_used', False)}")
                print(f"      Sources used: {response.get('sources_used', 0)}")
                
                # Check if regulatory guidance is in the response
                response_content = response.get("response", "")
                if "Latest Regulatory Guidance" in response_content:
                    print("   ✅ Regulatory guidance section found in response!")
                else:
                    print("   ⚠️  Regulatory guidance section not found in response")
            else:
                print(f"   ❌ Response synthesis failed: {response.get('error', 'Unknown error')}")
        else:
            print("   ❌ Response synthesis failed")
        
        # Complete workflow
        state = await workflow._complete_workflow(state)
        print(f"\n4️⃣ Workflow completed with status: {state['status']}")
        
        if state.get("total_duration"):
            print(f"   Total duration: {state['total_duration']:.2f} seconds")
        
    except Exception as e:
        print(f"\n❌ Workflow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎯 Enhanced Multi-Agent Workflow Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_enhanced_workflow())
