#!/usr/bin/env python3
"""
Test Adaptive Response Formatting

This script tests the new adaptive response formatting in the Response Synthesis Agent.
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.app.agents.specialized_agents import ResponseSynthesisAgent, QuestionAnalysisAgent
from backend.app.agents.base_agent import AgentContext, AgentType
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_adaptive_responses():
    """Test adaptive response formatting with different question types."""

    # Initialize agents
    synthesis_agent = ResponseSynthesisAgent()
    analysis_agent = QuestionAnalysisAgent()

    # Test cases with different question types
    test_cases = [
        {
            "question": "What are the key findings from the access review?",
            "expected_complexity": "basic",
            "expected_intent": "information_retrieval"
        },
        {
            "question": "Can you elaborate on the compliance impact from your previous response?",
            "expected_complexity": "basic",
            "expected_intent": "information_retrieval",
            "is_followup": True
        },
        {
            "question": "What specific remediation actions should be taken based on the material weaknesses identified?",
            "expected_complexity": "intermediate",
            "expected_intent": "compliance_assessment"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n🧪 Test Case {i}: {test_case['question'][:50]}...")

        question = test_case["question"]
        is_followup = test_case.get("is_followup", False)

        try:
            # Step 1: Analyze the question
            context = AgentContext(
                inputs={"user_message": question, "conversation_history": [], "document_metadata": {}},
                agent_type=AgentType.QUESTION_ANALYZER,
                timestamp=datetime.now(),
                conversation_id="test_conversation",
                workflow_id="test_workflow"
            )

            analysis_result = await analysis_agent.execute(context)
            analysis = analysis_result.get("analysis", {})

            # Step 2: Test response synthesis with adaptive formatting
            synthesis_context = AgentContext(
                inputs={
                    "question": question,
                    "analysis": analysis,
                    "context": [],  # Empty context for testing
                    "classifications": [],
                    "conversation_history": [{"role": "user", "content": "Previous question"}] if is_followup else []
                },
                agent_type=AgentType.RESPONSE_SYNTHESIZER,
                timestamp=datetime.now(),
                conversation_id="test_conversation",
                workflow_id="test_workflow"
            )

            synthesis_result = await synthesis_agent.execute(synthesis_context)
            response_content = synthesis_result.get("response", "")

            # Analyze the response
            logger.info(f"  📊 Question complexity: {analysis.get('complexity', 'unknown')}")
            logger.info(f"  📊 Question intent: {analysis.get('intent', 'unknown')}")
            logger.info(f"  📊 Is followup: {is_followup}")
            logger.info(f"  📊 Response length: {len(response_content)} characters")

            # Check if response format matches expectations
            has_sections = any(section in response_content for section in ["**Key Findings:**", "**Compliance Impact:**", "**Recommended Actions:**"])
            is_concise = len(response_content) < 500

            if is_followup or (analysis.get("complexity") == "basic" and analysis.get("intent") == "information_retrieval"):
                if is_concise and not has_sections:
                    logger.info("  ✅ PASS: Concise response format as expected")
                else:
                    logger.warning("  ⚠️ UNEXPECTED: Got structured format for simple/followup question")
            else:
                if has_sections:
                    logger.info("  ✅ PASS: Structured response format as expected")
                else:
                    logger.warning("  ⚠️ UNEXPECTED: Got concise format for complex question")

        except Exception as e:
            logger.error(f"  ❌ Error: {str(e)}")

async def main():
    """Main test execution."""
    logger.info("🚀 Testing Adaptive Response Formatting")

    await test_adaptive_responses()

    logger.info("✅ Adaptive response testing completed!")

if __name__ == "__main__":
    asyncio.run(main())
