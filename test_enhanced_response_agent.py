#!/usr/bin/env python3
"""
Test script for enhanced ResponseSynthesisAgent with Tavily integration.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.agents.specialized_agents import ResponseSynthesisAgent


async def test_enhanced_response_agent():
    """Test the enhanced ResponseSynthesisAgent with Tavily integration."""
    print("🧪 Testing Enhanced ResponseSynthesisAgent with Tavily...")
    print("=" * 60)
    
    # Initialize the agent
    agent = ResponseSynthesisAgent(verbose=True)
    
    # Test data
    test_context = {
        "inputs": {
            "question": "What are the key SOX compliance issues in this access review?",
            "context": [
                {
                    "document_id": "doc_001",
                    "document_type": "access_review",
                    "company": "TestCorp",
                    "display_name": "access_review_2024.pdf",
                    "chunk_text": "User access review findings indicate several users have excessive permissions that violate segregation of duties principles. Multiple users have both approval and execution rights for financial transactions."
                }
            ],
            "classifications": [
                {
                    "document_type": "access_review",
                    "risk_level": "high",
                    "compliance_frameworks": ["SOX"]
                }
            ]
        }
    }
    
    print("\n1️⃣ Testing enhanced response synthesis...")
    print(f"   Question: {test_context['inputs']['question']}")
    print(f"   Document Type: {test_context['inputs']['classifications'][0]['document_type']}")
    print(f"   Risk Level: {test_context['inputs']['classifications'][0]['risk_level']}")
    
    # Execute the agent
    result = await agent.execute(inputs=test_context["inputs"])
    
    if result.get("synthesis_status") == "completed":
        print("\n✅ Enhanced response synthesis successful!")
        print(f"   Regulatory Context Used: {result.get('regulatory_context_used', False)}")
        print(f"   Sources Used: {result.get('sources_used', 0)}")
        print(f"   Compliance Insights: {len(result.get('compliance_insights', {}))}")
        
        print("\n📝 Generated Response Preview:")
        response = result.get("response", "")
        # Show first 300 characters
        print(f"   {response[:300]}...")
        
        # Check if regulatory context is included
        if "Latest Regulatory Guidance" in response:
            print("\n✅ Regulatory guidance section found in response!")
        else:
            print("\n⚠️  Regulatory guidance section not found in response")
            
    else:
        print(f"\n❌ Response synthesis failed: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("🎯 Enhanced ResponseSynthesisAgent Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_enhanced_response_agent())
