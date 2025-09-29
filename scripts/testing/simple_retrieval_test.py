#!/usr/bin/env python3
"""
Simple Retrieval Test

This script performs a focused test of the Context Retrieval Agent
without the complex investigation framework that has AgentContext issues.
"""

import asyncio
import json
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.app.services.vector_database import vector_db_service
from backend.app.agents.specialized_agents import ContextRetrievalAgent
from backend.app.agents.base_agent import AgentContext, AgentType
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_context_retrieval_agent():
    """Test the Context Retrieval Agent directly."""
    logger.info("🔍 Testing Context Retrieval Agent...")

    # Test queries
    test_queries = [
        "What are the key findings from the access review?",
        "What material weaknesses were identified?",
        "What are the main compliance issues?"
    ]

    context_agent = ContextRetrievalAgent()

    for query in test_queries:
        logger.info(f"  🧪 Testing query: '{query}'")

        try:
            # Create proper AgentContext
            context = AgentContext(
                inputs={"user_message": query, "conversation_history": [], "document_metadata": {}},
                agent_type=AgentType.CONTEXT_RETRIEVER,
                timestamp=datetime.now(),
                conversation_id="test_conversation",
                workflow_id="test_workflow"
            )

            # Execute the agent
            result = await context_agent.execute(context)

            # Check results
            if isinstance(result, dict):
                context_count = len(result.get("context", []))
                retrieval_method = result.get("retrieval_method", "unknown")
                search_query = result.get("search_query_used", query)

                logger.info(f"    ✅ Status: {result.get('status', 'unknown')}")
                logger.info(f"    📊 Context count: {context_count}")
                logger.info(f"    🔍 Retrieval method: {retrieval_method}")
                logger.info(f"    📝 Search query: '{search_query}'")

                if context_count > 0:
                    logger.info(f"    🎉 SUCCESS: Found {context_count} contexts!")

                    # Show sample context
                    sample_context = result.get("context", [])[0] if result.get("context") else None
                    if sample_context and isinstance(sample_context, dict):
                        content_preview = sample_context.get("chunk_text", "")[:100] + "..." if sample_context.get("chunk_text") else "No content"
                        score = sample_context.get("score", 0)
                        logger.info(f"    📄 Sample: Score {score:.3f}, Content: {content_preview}")
                else:
                    logger.warning(f"    ⚠️ No contexts found")

            else:
                logger.error(f"    ❌ Invalid result type: {type(result)}")

        except Exception as e:
            logger.error(f"    ❌ Error: {str(e)}")

    return True

async def test_direct_vector_search():
    """Test direct vector search to compare with agent results."""
    logger.info("🔍 Testing Direct Vector Search...")

    test_queries = [
        "What are the key findings from the access review?",
        "SOX compliance requirements",
        "material weaknesses"
    ]

    for query in test_queries:
        logger.info(f"  🧪 Direct search: '{query}'")

        try:
            # Direct search
            results = await vector_db_service.semantic_search(query, limit=5, score_threshold=0.1)

            logger.info(f"    📊 Found {len(results)} results")

            if results:
                for i, result in enumerate(results[:3], 1):
                    score = result.get("score", 0)
                    content = result.get("chunk_text", "")[:80] + "..." if result.get("chunk_text") else "No content"
                    logger.info(f"    {i}. Score: {score:.3f}, Content: {content}")

        except Exception as e:
            logger.error(f"    ❌ Error: {str(e)}")

async def main():
    """Main test execution."""
    logger.info("🚀 Starting Simple Retrieval Test")

    try:
        # Test Context Retrieval Agent
        await test_context_retrieval_agent()

        logger.info("")

        # Test direct vector search for comparison
        await test_direct_vector_search()

        logger.info("✅ Simple retrieval test completed successfully!")

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
