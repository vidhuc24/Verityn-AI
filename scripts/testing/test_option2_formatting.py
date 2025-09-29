#!/usr/bin/env python3
"""
Test Option 2: Question Type-Based Formatting

This script tests the adaptive response formatting based on question complexity and intent.
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_option2_formatting():
    """Test the Option 2 formatting approach."""

    # Create the synthesis prompt template (same as implemented)
    synthesis_prompt = ChatPromptTemplate.from_template("""
    You are a Senior Audit Professional providing expert analysis on compliance and audit matters.

    RESPONSE ADAPTATION REQUIREMENTS:
    - ADAPT response format based on question complexity and context availability
    - For SIMPLE/FACTUAL questions: Provide direct, concise answers without heavy formatting
    - For COMPLEX/ANALYTICAL questions: Use structured format with sections
    - For FOLLOW-UP questions: Keep responses focused and avoid repeating previous structure
    - Always prioritize CLARITY and RELEVANCE over comprehensiveness

    Question: {question}
    Question Intent: {intent}
    Question Complexity: {complexity}
    Context Count: {context_count}
    Is Follow-up: {is_followup}

    Retrieved Context:
    {context}

    **ADAPTIVE RESPONSE FORMATS**:

    FOR SIMPLE/FACTUAL QUESTIONS (basic complexity, information_retrieval intent):
    - Provide DIRECT answer in 1-2 sentences
    - Include brief evidence reference if needed
    - Skip formal sections unless critical information requires structure

    FOR COMPLEX/ANALYTICAL QUESTIONS (intermediate/advanced complexity):
    - Use structured format with relevant sections
    - Include Key Findings, Compliance Impact, and Recommended Actions only when substantial analysis is needed

    **Response:** [Adaptive response based on question type and complexity]
    """)

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0.4)

    # Test cases for Option 2
    test_cases = [
        {
            "name": "Simple Factual Question",
            "question": "What is the document type of the access review report?",
            "intent": "information_retrieval",
            "complexity": "basic",
            "context_count": 2,
            "is_followup": "No",
            "expected_format": "concise"
        },
        {
            "name": "Complex Analytical Question",
            "question": "What are the key findings from the access review and what remediation actions should be taken?",
            "intent": "compliance_assessment",
            "complexity": "advanced",
            "context_count": 5,
            "is_followup": "No",
            "expected_format": "structured"
        },
        {
            "name": "Follow-up Question",
            "question": "Can you elaborate on the compliance impact from your previous response?",
            "intent": "information_retrieval",
            "complexity": "basic",
            "context_count": 3,
            "is_followup": "Yes",
            "expected_format": "concise"
        }
    ]

    for test_case in test_cases:
        logger.info(f"\n🧪 Testing: {test_case['name']}")
        logger.info(f"  Question: {test_case['question']}")
        logger.info(f"  Expected format: {test_case['expected_format']}")

        try:
            # Format the prompt
            messages = [
                SystemMessage(content="You are a senior audit professional with expertise in SOX compliance. Adapt your response format based on question complexity and context availability."),
                HumanMessage(content=synthesis_prompt.format(
                    question=test_case["question"],
                    intent=test_case["intent"],
                    complexity=test_case["complexity"],
                    context_count=test_case["context_count"],
                    is_followup=test_case["is_followup"],
                    context="Sample context about SOX compliance and access reviews with relevant document information...",
                    classifications="Document Type: access_review, Risk Level: medium",
                    regulatory_context="Latest SOX 404 requirements and compliance guidelines."
                ))
            ]

            # Get response
            response = await llm.ainvoke(messages)
            response_content = response.content

            # Analyze response characteristics
            has_sections = any(section in response_content for section in ["**Key Findings:**", "**Compliance Impact:**", "**Recommended Actions:**"])
            is_concise = len(response_content) < 500

            logger.info(f"  📊 Response length: {len(response_content)} characters")
            logger.info(f"  📊 Has sections: {has_sections}")
            logger.info(f"  📊 Is concise: {is_concise}")

            # Check if format matches expectations
            if test_case["expected_format"] == "concise":
                if is_concise and not has_sections:
                    logger.info("  ✅ PASS: Concise format as expected")
                else:
                    logger.warning("  ⚠️ FAIL: Expected concise format but got structured")
            else:  # structured
                if has_sections:
                    logger.info("  ✅ PASS: Structured format as expected")
                else:
                    logger.warning("  ⚠️ FAIL: Expected structured format but got concise")

            # Show response preview
            logger.info(f"  📝 Response: {response_content[:150]}...")

        except Exception as e:
            logger.error(f"  ❌ Error: {str(e)}")

async def main():
    """Main test execution."""
    logger.info("🚀 Testing Option 2: Question Type-Based Formatting")

    await test_option2_formatting()

    logger.info("✅ Option 2 formatting test completed!")

if __name__ == "__main__":
    asyncio.run(main())
