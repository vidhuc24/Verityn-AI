"""
Performance Tracking Service for Verityn AI.

This module provides comprehensive performance tracking for the RAG pipeline
following strict testing standards:
- Uses real query patterns and document data
- No hardcoded test scenarios or fabricated data
- Measures actual system performance with real workloads
- Provides detailed timing and resource usage analysis
"""

import asyncio
import time
import uuid
import psutil
import logging
import json
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from pathlib import Path
from datetime import datetime
import threading

from backend.app.config import settings

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Comprehensive performance tracking service for RAG pipeline analysis.

    Follows Verityn AI testing standards:
    - Uses real data from sox_test_documents/
    - No fabricated test scenarios
    - Measures actual performance with real API calls
    - Provides actionable optimization insights
    """

    def __init__(self):
        """Initialize the performance tracker."""
        self.performance_logs: List[Dict[str, Any]] = []
        self.active_queries: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

        # Performance thresholds (based on real-world audit software expectations)
        self.thresholds = {
            'total_response_time': 10.0,  # seconds - reasonable for enterprise users
            'document_retrieval': 2.0,    # seconds - vector search should be fast
            'llm_generation': 5.0,        # seconds - GPT-4 calls can take time
            'context_processing': 1.0,    # seconds - formatting should be quick
            'memory_usage_mb': 500        # MB - reasonable for document processing
        }

        # Create logs directory if it doesn't exist
        self.log_dir = Path("performance_logs")
        self.log_dir.mkdir(exist_ok=True)

    def start_query(self, query_id: Optional[str] = None, query_text: str = "") -> str:
        """
        Start tracking a new query.

        Args:
            query_id: Optional custom query ID
            query_text: The user's query text

        Returns:
            Query ID for this tracking session
        """
        if query_id is None:
            query_id = str(uuid.uuid4())

        query_info = {
            'query_id': query_id,
            'query_text': query_text[:100],  # First 100 chars for identification
            'start_time': time.time(),
            'start_memory': self._get_memory_usage(),
            'steps': {},
            'status': 'active'
        }

        with self.lock:
            self.active_queries[query_id] = query_info

        logger.info(f"🚀 Started tracking query {query_id[:8]}: {query_text[:50]}...")
        return query_id

    def track_step(
        self,
        query_id: str,
        step_name: str,
        step_func: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Callable:
        """
        Decorator/context manager to track performance of pipeline steps.

        Args:
            query_id: The query ID to track
            step_name: Name of the step (e.g., 'document_retrieval', 'llm_generation')
            step_func: Optional function to wrap
            metadata: Additional metadata to store

        Returns:
            Wrapped function or context manager
        """
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._track_async_step(query_id, step_name, func, args, kwargs, metadata)

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self._track_sync_step(query_id, step_name, func, args, kwargs, metadata)

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    async def _track_async_step(
        self,
        query_id: str,
        step_name: str,
        func: Callable,
        args: tuple,
        kwargs: dict,
        metadata: Optional[Dict[str, Any]]
    ) -> Any:
        """Track an async function step."""
        step_start = time.time()
        step_start_memory = self._get_memory_usage()

        try:
            result = await func(*args, **kwargs)

            step_duration = time.time() - step_start
            step_end_memory = self._get_memory_usage()

            # Store step performance data
            step_data = {
                'step_name': step_name,
                'duration_ms': step_duration * 1000,
                'start_memory_mb': step_start_memory,
                'end_memory_mb': step_end_memory,
                'memory_delta_mb': step_end_memory - step_start_memory,
                'success': True,
                'metadata': metadata or {}
            }

            with self.lock:
                if query_id in self.active_queries:
                    self.active_queries[query_id]['steps'][step_name] = step_data

            logger.debug(f"✅ {step_name} completed in {step_duration*1000:.1f}ms")
            return result

        except Exception as e:
            step_duration = time.time() - step_start

            # Log error but don't fail the step
            step_data = {
                'step_name': step_name,
                'duration_ms': step_duration * 1000,
                'start_memory_mb': step_start_memory,
                'error': str(e),
                'success': False,
                'metadata': metadata or {}
            }

            with self.lock:
                if query_id in self.active_queries:
                    self.active_queries[query_id]['steps'][step_name] = step_data

            logger.error(f"❌ {step_name} failed after {step_duration*1000:.1f}ms: {str(e)}")
            raise

    def _track_sync_step(
        self,
        query_id: str,
        step_name: str,
        func: Callable,
        args: tuple,
        kwargs: dict,
        metadata: Optional[Dict[str, Any]]
    ) -> Any:
        """Track a sync function step."""
        step_start = time.time()
        step_start_memory = self._get_memory_usage()

        try:
            result = func(*args, **kwargs)

            step_duration = time.time() - step_start
            step_end_memory = self._get_memory_usage()

            step_data = {
                'step_name': step_name,
                'duration_ms': step_duration * 1000,
                'start_memory_mb': step_start_memory,
                'end_memory_mb': step_end_memory,
                'memory_delta_mb': step_end_memory - step_start_memory,
                'success': True,
                'metadata': metadata or {}
            }

            with self.lock:
                if query_id in self.active_queries:
                    self.active_queries[query_id]['steps'][step_name] = step_data

            logger.debug(f"✅ {step_name} completed in {step_duration*1000:.1f}ms")
            return result

        except Exception as e:
            step_duration = time.time() - step_start

            step_data = {
                'step_name': step_name,
                'duration_ms': step_duration * 1000,
                'start_memory_mb': step_start_memory,
                'error': str(e),
                'success': False,
                'metadata': metadata or {}
            }

            with self.lock:
                if query_id in self.active_queries:
                    self.active_queries[query_id]['steps'][step_name] = step_data

            logger.error(f"❌ {step_name} failed after {step_duration*1000:.1f}ms: {str(e)}")
            raise

    def end_query(self, query_id: str) -> Dict[str, Any]:
        """
        Complete tracking for a query and return performance summary.

        Args:
            query_id: The query ID to complete

        Returns:
            Complete performance data for the query
        """
        with self.lock:
            if query_id not in self.active_queries:
                logger.warning(f"Query {query_id} not found in active queries")
                return {}

            query_info = self.active_queries[query_id]
            end_time = time.time()
            end_memory = self._get_memory_usage()

            # Calculate total metrics
            total_duration = end_time - query_info['start_time']
            total_memory_delta = end_memory - query_info['start_memory']

            # Complete the query data
            query_info.update({
                'end_time': end_time,
                'total_duration_ms': total_duration * 1000,
                'end_memory_mb': end_memory,
                'total_memory_delta_mb': total_memory_delta,
                'status': 'completed'
            })

            # Move from active to logs
            completed_query = self.active_queries.pop(query_id)
            self.performance_logs.append(completed_query)

            # Keep only last 1000 queries to prevent memory bloat
            if len(self.performance_logs) > 1000:
                self.performance_logs = self.performance_logs[-1000:]

            logger.info(f"✅ Completed query {query_id[:8]} in {total_duration*1000:.1f}ms")
            return completed_query

    def analyze_performance(self, recent_only: bool = True) -> Dict[str, Any]:
        """
        Analyze collected performance data for optimization insights.

        Args:
            recent_only: If True, analyze only last 100 queries

        Returns:
            Performance analysis report
        """
        logs_to_analyze = self.performance_logs[-100:] if recent_only else self.performance_logs

        if not logs_to_analyze:
            return {"error": "No performance data available"}

        # Calculate statistics
        total_times = [q['total_duration_ms'] for q in logs_to_analyze]
        retrieval_times = []
        generation_times = []
        memory_usages = []

        for query in logs_to_analyze:
            # Extract step timings
            for step_name, step_data in query.get('steps', {}).items():
                if step_data.get('success', False):
                    if 'retrieval' in step_name.lower():
                        retrieval_times.append(step_data['duration_ms'])
                    elif 'generation' in step_name.lower() or 'llm' in step_name.lower():
                        generation_times.append(step_data['duration_ms'])

            # Memory usage
            memory_usages.append(query.get('total_memory_delta_mb', 0))

        analysis = {
            'summary': {
                'total_queries': len(logs_to_analyze),
                'avg_total_time_ms': sum(total_times) / len(total_times) if total_times else 0,
                'median_total_time_ms': sorted(total_times)[len(total_times)//2] if total_times else 0,
                'slow_queries_count': len([t for t in total_times if t > self.thresholds['total_response_time'] * 1000])
            },
            'step_performance': {
                'retrieval': {
                    'avg_ms': sum(retrieval_times) / len(retrieval_times) if retrieval_times else 0,
                    'count': len(retrieval_times)
                },
                'generation': {
                    'avg_ms': sum(generation_times) / len(generation_times) if generation_times else 0,
                    'count': len(generation_times)
                }
            },
            'memory_usage': {
                'avg_delta_mb': sum(memory_usages) / len(memory_usages) if memory_usages else 0,
                'max_delta_mb': max(memory_usages) if memory_usages else 0
            },
            'recommendations': self._generate_recommendations(logs_to_analyze)
        }

        return analysis

    def _generate_recommendations(self, logs: List[Dict[str, Any]]) -> List[str]:
        """Generate optimization recommendations based on performance data."""
        recommendations = []

        # Analyze bottlenecks
        retrieval_times = []
        generation_times = []
        total_times = []

        for query in logs:
            total_times.append(query['total_duration_ms'])

            for step_name, step_data in query.get('steps', {}).items():
                if step_data.get('success', False):
                    if 'retrieval' in step_name.lower():
                        retrieval_times.append(step_data['duration_ms'])
                    elif 'generation' in step_name.lower():
                        generation_times.append(step_data['duration_ms'])

        # Performance recommendations
        if retrieval_times:
            avg_retrieval = sum(retrieval_times) / len(retrieval_times)
            if avg_retrieval > self.thresholds['document_retrieval'] * 1000:
                recommendations.append(f"🚨 Document retrieval slow ({avg_retrieval:.1f}ms avg) - optimize vector search")

        if generation_times:
            avg_generation = sum(generation_times) / len(generation_times)
            if avg_generation > self.thresholds['llm_generation'] * 1000:
                recommendations.append(f"🚨 LLM generation slow ({avg_generation:.1f}ms avg) - consider prompt optimization")

        if total_times:
            slow_queries = len([t for t in total_times if t > self.thresholds['total_response_time'] * 1000])
            if slow_queries > len(total_times) * 0.1:  # More than 10% slow
                recommendations.append(f"⚠️ {slow_queries} slow queries detected - investigate bottlenecks")

        if not recommendations:
            recommendations.append("✅ Performance looks good - no immediate optimization needed")

        return recommendations

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert bytes to MB
        except Exception:
            return 0.0

    def save_performance_report(self, filename: Optional[str] = None) -> str:
        """
        Save performance analysis report to JSON file.

        Args:
            filename: Optional custom filename

        Returns:
            Path to saved report file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"

        report_path = self.log_dir / filename

        analysis = self.analyze_performance()

        # Add raw logs for detailed analysis
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'sample_logs': self.performance_logs[-10:] if self.performance_logs else []
        }

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        logger.info(f"📊 Performance report saved to: {report_path}")
        return str(report_path)

    def get_query_performance(self, query_id: str) -> Optional[Dict[str, Any]]:
        """
        Get performance data for a specific query.

        Args:
            query_id: The query ID to look up

        Returns:
            Performance data or None if not found
        """
        # Check active queries first
        if query_id in self.active_queries:
            return self.active_queries[query_id]

        # Check completed logs
        for query in self.performance_logs:
            if query['query_id'] == query_id:
                return query

        return None


# Global performance tracker instance
performance_tracker = PerformanceTracker()
