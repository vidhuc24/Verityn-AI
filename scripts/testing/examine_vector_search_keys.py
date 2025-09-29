#!/usr/bin/env python3
"""
Examine Vector Search Result Keys

This script examines the actual keys in vector search results to understand
the data structure we're working with.
"""

import asyncio
import json
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.app.services.vector_database import vector_db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def examine_vector_search_keys():
    """Examine the actual keys in vector search results."""
    logger.info("🔍 Examining vector search result keys...")
    
    try:
        # Test with a simple query
        test_query = "SOX compliance"
        logger.info(f"  Testing query: '{test_query}'")
        
        # Call semantic search
        results = await vector_db_service.semantic_search(test_query, limit=3, score_threshold=0.0)
        
        if results:
            logger.info(f"  📊 Found {len(results)} results")
            
            # Examine the first result
            first_result = results[0]
            logger.info(f"  📊 First result type: {type(first_result)}")
            
            if isinstance(first_result, dict):
                logger.info(f"  📊 First result keys: {list(first_result.keys())}")
                
                # Print each key-value pair
                for key, value in first_result.items():
                    if isinstance(value, str) and len(value) > 100:
                        logger.info(f"    {key}: {value[:100]}...")
                    else:
                        logger.info(f"    {key}: {value}")
                
                return {
                    "result_type": "dict",
                    "keys": list(first_result.keys()),
                    "sample_result": first_result
                }
            else:
                logger.info(f"  📊 First result: {first_result}")
                return {
                    "result_type": str(type(first_result)),
                    "result": first_result
                }
        else:
            logger.warning("  ⚠️ No results returned")
            return {"error": "No results returned"}
            
    except Exception as e:
        logger.error(f"  ❌ Error: {str(e)}")
        return {"error": str(e)}

async def main():
    """Main examination function."""
    logger.info("🚀 Starting Vector Search Keys Examination")
    
    try:
        result = await examine_vector_search_keys()
        
        # Save results
        results_file = Path("scripts/testing/vector_search_keys_results.json")
        with open(results_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        logger.info(f"📊 Results saved to: {results_file}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Examination failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
