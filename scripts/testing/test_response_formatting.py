#!/usr/bin/env python3
"""
Test Response Formatting Logic

This script tests the response formatting logic directly without agent interface issues.
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

async def test_response_formatting():
    """Test different response formatting scenarios."""

    # Create the synthesis prompt template
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

    FOR FOLLOW-UP/CLARIFICATION QUESTIONS (is_followup = "Yes"):
    - Provide DIRECT, concise answers (1-2 sentences maximum)
    - Reference the specific aspect being clarified
    - Avoid repeating previous structure or comprehensive formatting
    - Focus only on the clarification requested

    FOR SIMPLE/FACTUAL QUESTIONS (basic complexity, information_retrieval intent):
    - Provide DIRECT answer in 1-2 sentences
    - Include brief evidence reference if needed
    - Skip formal sections unless critical information requires structure

    FOR COMPLEX/ANALYTICAL QUESTIONS (intermediate/advanced complexity):
    - Use structured format with relevant sections
    - Include Key Findings, Compliance Impact, and Recommended Actions only when substantial analysis is needed

    **Response:** [Adaptive response based on question type, complexity, and follow-up status]
    """)

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0.4)

    # Test cases
    test_cases = [
        {
            "name": "Initial Complex Question",
            "question": "What are the key findings from the access review and what remediation actions should be taken?",
            "intent": "compliance_assessment",
            "complexity": "advanced",
            "context_count": 5,
            "is_followup": "No"
        },
        {
            "name": "Follow-up Question",
            "question": "Can you elaborate on the compliance impact from your previous response?",
            "intent": "information_retrieval",
            "complexity": "basic",
            "context_count": 3,
            "is_followup": "Yes"
        },
        {
            "name": "Simple Factual Question",
            "question": "What is the document type of the access review report?",
            "intent": "information_retrieval",
            "complexity": "basic",
            "context_count": 2,
            "is_followup": "No"
        }
    ]

    for test_case in test_cases:
        logger.info(f"\n🧪 Testing: {test_case['name']}")
        logger.info(f"  Question: {test_case['question']}")

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
                    context="Sample context about SOX compliance and access reviews...",
                    classifications="Document Type: access_review, Risk Level: medium"
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
            if test_case["is_followup"] == "Yes" or (test_case["complexity"] == "basic" and test_case["intent"] == "information_retrieval"):
                if is_concise and not has_sections:
                    logger.info("  ✅ PASS: Concise format as expected for simple/followup")
                else:
                    logger.warning("  ⚠️ UNEXPECTED: Got structured format for simple/followup question")
            else:
                if has_sections:
                    logger.info("  ✅ PASS: Structured format as expected for complex question")
                else:
                    logger.warning("  ⚠️ UNEXPECTED: Got concise format for complex question")

            # Show sample of response
            logger.info(f"  📝 Response preview: {response_content[:100]}...")

        except Exception as e:
            logger.error(f"  ❌ Error: {str(e)}")

async def main():
    """Main test execution."""
    logger.info("🚀 Testing Response Formatting Logic")

    await test_response_formatting()

    logger.info("✅ Response formatting testing completed!")

if __name__ == "__main__":
    asyncio.run(main())
