#!/usr/bin/env python3
"""
Test script for Tavily service integration.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.tavily_service import tavily_service


async def test_tavily_service():
    """Test the Tavily service functionality."""
    print("🧪 Testing Tavily Service Integration...")
    print("=" * 50)
    
    # Test 1: Basic compliance search
    print("\n1️⃣ Testing basic compliance search...")
    result = await tavily_service.search_compliance_guidance(
        query="SOX internal controls",
        document_type="access_review",
        compliance_framework="SOX"
    )
    
    if result["success"]:
        print("✅ Basic search successful!")
        print(f"   Query: {result['query']}")
        print(f"   Results found: {len(result['results'])}")
        print(f"   Insights found: {len(result['compliance_insights'])}")
        
        # Show first insight
        if result['compliance_insights']:
            first_insight = result['compliance_insights'][0]
            print(f"   Top insight: {first_insight['compliance_focus']}")
            print(f"   Title: {first_insight['title']}")
    else:
        print(f"❌ Basic search failed: {result['error']}")
    
    # Test 2: Compliance update
    print("\n2️⃣ Testing compliance update...")
    update_result = await tavily_service.get_compliance_update(
        framework="SOX",
        document_type="access_review"
    )
    
    if update_result["success"]:
        print("✅ Compliance update successful!")
        print(f"   Framework: SOX")
        print(f"   Document type: access_review")
        print(f"   Insights: {len(update_result['compliance_insights'])}")
    else:
        print(f"❌ Compliance update failed: {update_result['error']}")
    
    print("\n" + "=" * 50)
    print("🎯 Tavily Service Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_tavily_service())
