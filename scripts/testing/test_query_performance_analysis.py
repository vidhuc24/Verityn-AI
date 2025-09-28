#!/usr/bin/env python3
"""
Query Performance Analysis Test for Verityn AI

This test analyzes query performance to identify:
1. Slow/problematic queries that exceed performance thresholds
2. Performance bottlenecks in the RAG pipeline
3. Query patterns that perform well vs poorly
4. Memory usage patterns during query processing

Follows Verityn AI testing standards:
- Uses real data from sox_test_documents/
- No hardcoded test scenarios
- Measures actual performance with real API calls
- Provides actionable optimization insights
"""

import asyncio
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import logging
import statistics

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.chat_engine import RAGChatEngine
from backend.app.services.performance_tracker import performance_tracker
from backend.app.services.vector_database import vector_db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QueryPerformanceAnalyzer:
    """
    Comprehensive query performance analysis following Verityn AI standards.

    Tests real query scenarios with actual document data to identify
    performance bottlenecks and optimization opportunities.
    """

    def __init__(self):
        """Initialize the performance analyzer."""
        self.chat_engine = RAGChatEngine()

        # Query categories for comprehensive testing
        self.query_categories = {
            'simple_audit': [
                "What are the key findings?",
                "What controls were tested?",
                "What compliance issues were found?",
                "What risks were identified?",
                "What recommendations were made?"
            ],
            'complex_audit': [
                "What SOX 404 controls were tested for the revenue recognition process?",
                "How many user access reviews were completed in Q4 2024?",
                "What material weaknesses were identified in the financial reporting controls?",
                "Which control deficiencies require remediation by year-end?",
                "What percentage of IT general controls were found to be effective?"
            ],
            'vague_queries': [
                "controls",
                "findings",
                "assessment",
                "compliance",
                "audit"
            ],
            'specific_queries': [
                "What was the exact date of the last access review completion?",
                "Which user had the most privileged access violations?",
                "What is the control ID for automated three-way match validation?",
                "How many segregation of duties conflicts were identified?",
                "What was the sample size used for testing revenue recognition controls?"
            ]
        }

        # Performance thresholds (realistic for enterprise audit software)
        self.performance_thresholds = {
            'total_response_time_ms': 10000,  # 10 seconds max
            'document_retrieval_ms': 2000,    # 2 seconds max for search
            'llm_generation_ms': 5000,        # 5 seconds max for GPT-4
            'memory_usage_mb': 500            # 500MB max per query
        }

    async def run_performance_analysis(self) -> Dict[str, Any]:
        """
        Run comprehensive performance analysis across all query categories.

        Returns:
            Detailed performance analysis report
        """
        logger.info("🚀 Starting Query Performance Analysis")
        logger.info("📊 Testing real audit query scenarios with actual document data")

        # Clear previous performance data
        performance_tracker.performance_logs.clear()

        results = {
            'analysis_timestamp': time.time(),
            'test_summary': {},
            'performance_by_category': {},
            'slow_queries': [],
            'bottleneck_analysis': {},
            'optimization_recommendations': [],
            'detailed_results': []
        }

        # Test each query category
        for category, queries in self.query_categories.items():
            logger.info(f"\n📋 Testing category: {category}")
            category_results = await self._test_query_category(category, queries)
            results['performance_by_category'][category] = category_results
            results['detailed_results'].extend(category_results['query_details'])

            # Update summary stats
            results['test_summary'][category] = {
                'queries_tested': len(queries),
                'avg_response_time_ms': category_results['avg_total_time_ms'],
                'slow_queries_count': category_results['slow_queries_count'],
                'memory_usage_avg_mb': category_results['avg_memory_usage_mb']
            }

        # Analyze bottlenecks and generate recommendations
        results['bottleneck_analysis'] = self._analyze_bottlenecks(results['detailed_results'])
        results['slow_queries'] = self._identify_slow_queries(results['detailed_results'])
        results['optimization_recommendations'] = self._generate_optimization_recommendations(results)

        # Print summary
        self._print_performance_summary(results)

        return results

    async def _test_query_category(self, category: str, queries: List[str]) -> Dict[str, Any]:
        """Test performance for a specific query category."""
        category_results = {
            'category': category,
            'total_queries': len(queries),
            'successful_queries': 0,
            'failed_queries': 0,
            'avg_total_time_ms': 0,
            'avg_retrieval_time_ms': 0,
            'avg_generation_time_ms': 0,
            'avg_memory_usage_mb': 0,
            'slow_queries_count': 0,
            'query_details': []
        }

        total_times = []
        retrieval_times = []
        generation_times = []
        memory_usages = []

        for i, query in enumerate(queries, 1):
            logger.info(f"  🔍 Testing query {i}/{len(queries)}: '{query[:60]}...'")

            try:
                # Process query with performance tracking
                start_time = time.time()
                response = await self.chat_engine.process_message(query)
                end_time = time.time()

                # Extract performance data from response
                performance_data = response.get('performance', {})
                if performance_data:
                    query_detail = {
                        'query': query,
                        'category': category,
                        'success': True,
                        'total_time_ms': performance_data.get('total_time_ms', 0),
                        'retrieval_time_ms': self._get_step_time(performance_data, 'document_retrieval'),
                        'generation_time_ms': self._get_step_time(performance_data, 'llm_generation'),
                        'memory_usage_mb': performance_data.get('memory_usage_mb', 0),
                        'chunks_retrieved': response.get('context_metadata', {}).get('chunks_retrieved', 0),
                        'response_length': len(response.get('message', {}).get('content', ''))
                    }

                    # Update category statistics
                    total_times.append(query_detail['total_time_ms'])
                    retrieval_times.append(query_detail['retrieval_time_ms'])
                    generation_times.append(query_detail['generation_time_ms'])
                    memory_usages.append(query_detail['memory_usage_mb'])

                    if query_detail['total_time_ms'] > self.performance_thresholds['total_response_time_ms']:
                        category_results['slow_queries_count'] += 1

                    category_results['successful_queries'] += 1
                else:
                    # No performance data available
                    query_detail = {
                        'query': query,
                        'category': category,
                        'success': False,
                        'error': 'No performance data recorded'
                    }
                    category_results['failed_queries'] += 1

                category_results['query_details'].append(query_detail)

            except Exception as e:
                logger.error(f"❌ Query failed: {str(e)}")
                query_detail = {
                    'query': query,
                    'category': category,
                    'success': False,
                    'error': str(e)
                }
                category_results['failed_queries'] += 1
                category_results['query_details'].append(query_detail)

        # Calculate category averages
        if total_times:
            category_results['avg_total_time_ms'] = statistics.mean(total_times)
            category_results['avg_retrieval_time_ms'] = statistics.mean(retrieval_times) if retrieval_times else 0
            category_results['avg_generation_time_ms'] = statistics.mean(generation_times) if generation_times else 0
            category_results['avg_memory_usage_mb'] = statistics.mean(memory_usages) if memory_usages else 0

        return category_results

    def _get_step_time(self, performance_data: Dict[str, Any], step_name: str) -> float:
        """Extract timing for a specific pipeline step."""
        step_breakdown = performance_data.get('step_breakdown', {})
        step_data = step_breakdown.get(step_name, {})
        return step_data.get('duration_ms', 0)

    def _analyze_bottlenecks(self, query_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance bottlenecks across all queries."""
        bottlenecks = {
            'slowest_step_overall': None,
            'most_problematic_step': None,
            'performance_distribution': {},
            'memory_issues': []
        }

        # Analyze step performance
        step_times = {
            'document_retrieval': [],
            'llm_generation': []
        }

        for query in query_results:
            if query.get('success', False):
                # Collect step timings
                for step_name in step_times.keys():
                    step_time = query.get(f'{step_name.split("_")[1]}_time_ms', 0)
                    if step_time > 0:
                        step_times[step_name].append(step_time)

        # Find slowest step
        if step_times['document_retrieval'] and step_times['llm_generation']:
            avg_retrieval = statistics.mean(step_times['document_retrieval'])
            avg_generation = statistics.mean(step_times['llm_generation'])

            if avg_retrieval > avg_generation:
                bottlenecks['slowest_step_overall'] = 'document_retrieval'
                bottlenecks['most_problematic_step'] = 'document_retrieval'
            else:
                bottlenecks['slowest_step_overall'] = 'llm_generation'
                bottlenecks['most_problematic_step'] = 'llm_generation'

        # Memory usage analysis
        memory_usages = [q.get('memory_usage_mb', 0) for q in query_results if q.get('success', False)]
        if memory_usages:
            high_memory_queries = [q for q in query_results if q.get('memory_usage_mb', 0) > self.performance_thresholds['memory_usage_mb']]
            bottlenecks['memory_issues'] = len(high_memory_queries)

        return bottlenecks

    def _identify_slow_queries(self, query_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify queries that exceed performance thresholds."""
        slow_queries = []

        for query in query_results:
            if query.get('success', False):
                total_time = query.get('total_time_ms', 0)
                if total_time > self.performance_thresholds['total_response_time_ms']:
                    slow_queries.append({
                        'query': query['query'],
                        'category': query['category'],
                        'total_time_ms': total_time,
                        'chunks_retrieved': query.get('chunks_retrieved', 0),
                        'memory_usage_mb': query.get('memory_usage_mb', 0)
                    })

        # Sort by total time (slowest first)
        slow_queries.sort(key=lambda x: x['total_time_ms'], reverse=True)
        return slow_queries

    def _generate_optimization_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable optimization recommendations."""
        recommendations = []

        # Analyze bottlenecks
        bottlenecks = results['bottleneck_analysis']
        if bottlenecks['slowest_step_overall'] == 'document_retrieval':
            recommendations.append("🚨 Document retrieval is the slowest step - optimize vector search parameters")
            recommendations.append("💡 Consider reducing search limit or adding query preprocessing")

        if bottlenecks['slowest_step_overall'] == 'llm_generation':
            recommendations.append("🚨 LLM generation is the bottleneck - optimize prompt size and context")
            recommendations.append("💡 Reduce context chunks or implement context filtering")

        # Memory recommendations
        memory_issues_count = len(bottlenecks['memory_issues']) if bottlenecks['memory_issues'] else 0
        if memory_issues_count > 0:
            recommendations.append(f"⚠️ {memory_issues_count} queries exceeded memory threshold - investigate memory leaks")

        # Query pattern recommendations
        category_performance = results['performance_by_category']
        for category, data in category_performance.items():
            if data['slow_queries_count'] > data['total_queries'] * 0.3:  # More than 30% slow
                recommendations.append(f"🔍 {category} queries are consistently slow - analyze query patterns")

        # General recommendations
        if not recommendations:
            recommendations.append("✅ Performance looks good across all query categories")
            recommendations.append("💡 Consider monitoring for performance regressions in production")

        return recommendations

    async def _load_test_documents(self) -> Dict[str, Dict[str, Any]]:
        """Load test documents for performance analysis."""
        test_docs = {}

        # Load 2 TXT files from sox_test_documents
        txt_files = [
            "data/sox_test_documents/sox_access_review_2024.txt",
            "data/sox_test_documents/sox_internal_controls_2024.txt"
        ]

        # Load 2 PDF files from synthetic_documents
        pdf_files = [
            "data/synthetic_documents/pdf/SOX_Access_Review_2024.pdf",
            "data/synthetic_documents/pdf/uber_access_review_20250804.pdf"
        ]

        all_files = txt_files + pdf_files

        for file_path in all_files:
            try:
                doc_name = Path(file_path).stem
                doc_type = "access_review" if "access" in doc_name.lower() else "internal_controls"

                if file_path.endswith('.pdf'):
                    # Handle PDF files using pypdf
                    try:
                        from pypdf import PdfReader
                        with open(file_path, 'rb') as f:
                            pdf_reader = PdfReader(f)
                            content = ""
                            for page in pdf_reader.pages:
                                content += page.extract_text() + "\n"
                    except Exception as pdf_error:
                        logger.error(f"❌ PDF processing failed for {file_path}: {str(pdf_error)}")
                        continue
                else:
                    # Handle text files
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                if content and content.strip():
                    test_docs[doc_name] = {
                        'path': file_path,
                        'type': 'pdf' if file_path.endswith('.pdf') else 'txt',
                        'content': content,
                        'expected_type': doc_type
                    }
                    logger.info(f"✅ Loaded {doc_name} ({len(content)} chars)")
                else:
                    logger.warning(f"⚠️ Empty or no content in: {file_path}")

            except Exception as e:
                logger.error(f"❌ Failed to load {file_path}: {str(e)}")

        return test_docs

    async def _process_test_documents(self, test_documents: Dict[str, Dict[str, Any]]) -> None:
        """Process test documents into vector database for realistic performance testing."""
        from backend.app.services.document_processor import EnhancedDocumentProcessor
        from fastapi import UploadFile
        from io import BytesIO

        processor = EnhancedDocumentProcessor()
        processed_count = 0

        for doc_name, doc_info in test_documents.items():
            try:
                logger.info(f"🔄 Processing {doc_name} into vector database...")

                # Read file content
                with open(doc_info['path'], 'rb') as f:
                    file_content = f.read()

                # Create a mock UploadFile object
                mock_file = UploadFile(
                    file=BytesIO(file_content),
                    filename=Path(doc_info['path']).name
                )

                # Process the document
                result = await processor.process_document(
                    file=mock_file,
                    document_id=doc_name,
                    description=f"Test document: {doc_name}"
                )

                # Extract chunks and metadata from result
                chunks = result.get('chunks', [])
                metadata = result.get('metadata', {})

                if chunks:
                    # Store in vector database
                    success = await vector_db_service.insert_document_chunks(
                        document_id=doc_name,
                        chunks=chunks,
                        metadata=metadata
                    )

                    if success:
                        processed_count += 1
                        logger.info(f"✅ Processed {doc_name}: {len(chunks)} chunks stored")
                    else:
                        logger.error(f"❌ Failed to store {doc_name} in vector database")
                else:
                    logger.warning(f"⚠️ No chunks generated for {doc_name}")

            except Exception as e:
                logger.error(f"❌ Failed to process {doc_name}: {str(e)}")

        logger.info(f"📊 Document processing complete: {processed_count}/{len(test_documents)} documents processed")

    def _print_performance_summary(self, results: Dict[str, Any]) -> None:
        """Print comprehensive performance analysis summary."""
        print("\n" + "="*120)
        print("📊 QUERY PERFORMANCE ANALYSIS RESULTS")
        print("="*120)

        # Overall statistics
        total_queries = sum(cat['total_queries'] for cat in results['performance_by_category'].values())
        total_successful = sum(cat['successful_queries'] for cat in results['performance_by_category'].values())

        print(f"📋 Overall Status: {'✅ EXCELLENT' if total_successful/total_queries > 0.9 else '🟡 GOOD' if total_successful/total_queries > 0.7 else '❌ NEEDS IMPROVEMENT'}")
        print(f"📄 Total Queries Tested: {total_queries}")
        print(f"✅ Successful Queries: {total_successful} ({total_successful/total_queries:.1%})")

        # Category breakdown
        print("\n📊 PERFORMANCE BY CATEGORY:")
        print("-" * 120)

        for category, data in results['performance_by_category'].items():
            status = "✅" if data['slow_queries_count'] == 0 else "🟡" if data['slow_queries_count'] <= 2 else "❌"
            print(f"\n{status} {category.upper().replace('_', ' ')}")
            print(f"   📄 Queries: {data['total_queries']} ({data['successful_queries']}/{data['failed_queries']} success/fail)")
            print(f"   ⏱️ Avg Response Time: {data['avg_total_time_ms']:.1f}ms")
            print(f"   🔍 Avg Retrieval Time: {data['avg_retrieval_time_ms']:.1f}ms")
            print(f"   🤖 Avg Generation Time: {data['avg_generation_time_ms']:.1f}ms")
            print(f"   💾 Avg Memory Usage: {data['avg_memory_usage_mb']:.1f}MB")
            print(f"   🐌 Slow Queries: {data['slow_queries_count']}")

        # Bottleneck analysis
        bottlenecks = results['bottleneck_analysis']
        print("\n🎯 BOTTLENECK ANALYSIS:")
        print(f"   🚨 Slowest Step: {bottlenecks['slowest_step_overall'] or 'N/A'}")
        print(f"   🔍 Most Problematic: {bottlenecks['most_problematic_step'] or 'N/A'}")
        print(f"   💾 Memory Issues: {bottlenecks['memory_issues']} queries")

        # Slow queries
        slow_queries = results['slow_queries']
        if slow_queries:
            print("\n🐌 SLOWEST QUERIES:")
            print(f"   📊 Top {min(5, len(slow_queries))} slowest queries:")
            for i, query in enumerate(slow_queries[:5], 1):
                print(f"   {i}. \"{query['query'][:60]}...\" - {query['total_time_ms']:.1f}ms")

        # Recommendations
        recommendations = results['optimization_recommendations']
        print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

        print("\n" + "="*120)
        print("✅ QUERY PERFORMANCE ANALYSIS COMPLETED")
        print("="*120)

async def main():
    """Run the query performance analysis."""
    analyzer = QueryPerformanceAnalyzer()

    # Initialize vector database (required for testing)
    try:
        await vector_db_service.initialize_collection()
        logger.info("✅ Vector database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Vector database initialization failed: {str(e)}")
        logger.info("💡 Continuing with analysis - some queries may fail without documents")
        # Don't exit - we can still analyze the system structure

    # Load test documents for performance analysis
    test_documents = await analyzer._load_test_documents()
    logger.info(f"📄 Loaded {len(test_documents)} test documents for performance analysis")

    # Process documents into vector database for realistic testing
    if test_documents:
        await analyzer._process_test_documents(test_documents)
        logger.info("✅ Test documents processed into vector database")
    else:
        logger.warning("⚠️ No test documents loaded - performance analysis will be limited")

    # Run comprehensive performance analysis
    results = await analyzer.run_performance_analysis()

    # Save detailed results
    output_file = Path(__file__).parent / "query_performance_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    logger.info(f"📊 Detailed results saved to: {output_file}")

    # Generate performance report using the tracker
    report_path = performance_tracker.save_performance_report("query_performance_analysis")
    logger.info(f"📈 Performance report saved to: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
