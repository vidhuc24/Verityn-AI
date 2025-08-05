"""
RAGAS Evaluation Service for Verityn AI.

This module implements RAGAS evaluation framework following bootcamp Session 8
patterns to assess RAG performance with faithfulness, relevance, precision, and recall.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
import pandas as pd
from pathlib import Path

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    answer_correctness,
    context_precision,
    context_recall,
    answer_similarity
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from datasets import Dataset

from backend.app.config import settings
from backend.app.services.advanced_retrieval import advanced_retrieval_service
from backend.app.workflows.multi_agent_workflow import MultiAgentWorkflow

logger = logging.getLogger(__name__)


class RAGASEvaluationService:
    """RAGAS evaluation service for comprehensive RAG assessment."""
    
    def __init__(self):
        """Initialize RAGAS evaluation service."""
        self.evaluator_llm = LangchainLLMWrapper(
            ChatOpenAI(
                model="gpt-4",
                temperature=0.1,
                openai_api_key=settings.OPENAI_API_KEY,
                request_timeout=120,  # Increased timeout
                max_retries=3  # Add retries
            )
        )
        self.evaluator_embeddings = LangchainEmbeddingsWrapper(
            OpenAIEmbeddings(
                model=settings.OPENAI_EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                request_timeout=120,  # Increased timeout
                max_retries=3  # Add retries
            )
        )
        
        # Initialize workflow for testing
        self.workflow = MultiAgentWorkflow(verbose=True)
        
        # Evaluation metrics
        self.metrics = [
            faithfulness,
            answer_relevancy,
            answer_correctness,
            context_precision,
            context_recall,
            answer_similarity
        ]
        
        # Rate limiting configuration
        self.rate_limit_delay = 2.0  # Seconds between API calls
        self.batch_size = 3  # Process questions in smaller batches
        
        # Audit-specific test questions
        self.audit_test_questions = [
            {
                "question": "What are the material weaknesses identified in SOX 404 controls?",
                "ground_truth": "Material weaknesses in SOX 404 controls include ineffective user access controls for financial systems, excessive permissions that violate segregation of duties, and significant deficiencies in IT access controls.",
                "contexts": [
                    "Access Review Findings: Material weakness identified in user access controls for financial systems. SOX 404 controls ineffective.",
                    "Material Weakness Disclosure: Significant deficiency in IT access controls identified. Users have inappropriate access to financial systems."
                ]
            },
            {
                "question": "What are the key findings from financial reconciliation processes?",
                "ground_truth": "Financial reconciliation processes show discrepancies in account reconciliations, deficiencies in approval workflows for journal entries, and control testing reveals inadequate month-end close procedures.",
                "contexts": [
                    "Financial Reconciliation Report: Month-end close process shows discrepancies in account reconciliations. Control testing reveals deficiencies in approval workflows for journal entries."
                ]
            },
            {
                "question": "What is the overall risk assessment for IT security controls?",
                "ground_truth": "Overall risk level is medium with key risks including IT security vulnerabilities, inadequate internal controls, and material weaknesses identified in IT general controls.",
                "contexts": [
                    "Risk Assessment Summary: Overall risk level is medium. Key risks include IT security vulnerabilities and inadequate internal controls. Material weaknesses identified in IT general controls."
                ]
            },
            {
                "question": "Are there any effective SOX 404 controls identified?",
                "ground_truth": "Yes, some SOX 404 controls are effective. Internal controls over financial reporting are effective in some areas with no material weaknesses identified and all key controls tested passed with satisfactory results.",
                "contexts": [
                    "SOX 404 Testing Results: Internal controls over financial reporting are effective. No material weaknesses identified. All key controls tested passed with satisfactory results."
                ]
            }
        ]
    
    async def _rate_limited_delay(self):
        """Add rate limiting delay between API calls."""
        await asyncio.sleep(self.rate_limit_delay)
    
    async def _process_batch_with_rate_limiting(self, batch_items: List[Dict], retrieval_method: str) -> List[Dict]:
        """Process a batch of items with rate limiting."""
        results = []
        for i, item in enumerate(batch_items):
            try:
                logger.info(f"Processing item {i+1}/{len(batch_items)}")
                
                # Get system response
                system_response = await self._get_system_response(item["question"], retrieval_method)
                
                results.append({
                    "question": item["question"],
                    "answer": system_response["answer"],
                    "contexts": system_response["contexts"],
                    "ground_truth": item["ground_truth"]
                })
                
                # Add rate limiting delay between items
                if i < len(batch_items) - 1:  # Don't delay after the last item
                    await self._rate_limited_delay()
                    
            except Exception as e:
                logger.error(f"Error processing item {i+1}: {str(e)}")
                # Add fallback response
                results.append({
                    "question": item["question"],
                    "answer": "Unable to generate response due to system error.",
                    "contexts": [],
                    "ground_truth": item["ground_truth"]
                })
                
        return results
    
    async def generate_synthetic_test_data(self, num_questions: int = 10) -> Dataset:
        """
        Generate synthetic test data for evaluation using audit documents.
        
        Args:
            num_questions: Number of synthetic questions to generate
            
        Returns:
            Dataset with questions, contexts, and ground truth answers
        """
        try:
            logger.info(f"Generating {num_questions} synthetic test questions")
            
            # For now, use our predefined audit questions and expand them
            test_data = {
                "question": [],
                "ground_truth": [],
                "contexts": []
            }
            
            # Use predefined questions as base
            base_questions = self.audit_test_questions[:min(num_questions, len(self.audit_test_questions))]
            
            for item in base_questions:
                test_data["question"].append(item["question"])
                test_data["ground_truth"].append(item["ground_truth"])
                test_data["contexts"].append(item["contexts"])
            
            # Generate additional variations if needed
            if num_questions > len(base_questions):
                additional_needed = num_questions - len(base_questions)
                variations = await self._generate_question_variations(base_questions, additional_needed)
                
                for variation in variations:
                    test_data["question"].append(variation["question"])
                    test_data["ground_truth"].append(variation["ground_truth"])
                    test_data["contexts"].append(variation["contexts"])
            
            dataset = Dataset.from_dict(test_data)
            logger.info(f"Generated synthetic dataset with {len(dataset)} questions")
            
            return dataset
            
        except Exception as e:
            logger.error(f"Failed to generate synthetic test data: {str(e)}")
            raise
    
    async def _generate_question_variations(self, base_questions: List[Dict], num_variations: int) -> List[Dict]:
        """Generate variations of base questions."""
        variations = []
        
        variation_prompts = [
            "What compliance issues were found in the audit?",
            "Which controls are working effectively?",
            "What remediation actions are recommended?",
            "How severe are the identified risks?",
            "What are the regulatory implications?"
        ]
        
        # Create simple variations by cycling through prompts
        for i in range(num_variations):
            base_idx = i % len(base_questions)
            base_item = base_questions[base_idx]
            
            variation = {
                "question": variation_prompts[i % len(variation_prompts)],
                "ground_truth": f"Based on audit findings, {base_item['ground_truth'].lower()}",
                "contexts": base_item["contexts"]
            }
            variations.append(variation)
        
        return variations
    
    async def evaluate_retrieval_system(
        self,
        test_dataset: Dataset,
        retrieval_method: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        Evaluate retrieval system using RAGAS metrics with rate limiting.
        
        Args:
            test_dataset: Dataset with test questions and ground truth
            retrieval_method: Which retrieval method to test
            
        Returns:
            Evaluation results with RAGAS metrics
        """
        try:
            logger.info(f"Evaluating retrieval system with {retrieval_method} method")
            
            # Convert dataset to list for batch processing
            dataset_list = list(test_dataset)
            
            # Process in batches with rate limiting
            evaluation_data = {
                "question": [],
                "answer": [],
                "contexts": [],
                "ground_truth": []
            }
            
            # Process in smaller batches to avoid rate limits
            for i in range(0, len(dataset_list), self.batch_size):
                batch = dataset_list[i:i + self.batch_size]
                logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(dataset_list) + self.batch_size - 1)//self.batch_size}")
                
                batch_results = await self._process_batch_with_rate_limiting(batch, retrieval_method)
                
                # Add batch results to evaluation data
                for result in batch_results:
                    evaluation_data["question"].append(result["question"])
                    evaluation_data["answer"].append(result["answer"])
                    evaluation_data["contexts"].append(result["contexts"])
                    evaluation_data["ground_truth"].append(result["ground_truth"])
                
                # Add delay between batches
                if i + self.batch_size < len(dataset_list):
                    logger.info("Adding delay between batches...")
                    await asyncio.sleep(5.0)  # 5 second delay between batches
            
            # Create evaluation dataset
            eval_dataset = Dataset.from_dict(evaluation_data)
            
            logger.info("Running RAGAS evaluation...")
            
            # Run RAGAS evaluation with additional delay
            await asyncio.sleep(3.0)  # Delay before RAGAS evaluation
            
            result = evaluate(
                dataset=eval_dataset,
                metrics=self.metrics,
                llm=self.evaluator_llm,
                embeddings=self.evaluator_embeddings
            )
            
            # Process results
            evaluation_results = {
                "method": retrieval_method,
                "timestamp": datetime.now().isoformat(),
                "metrics": dict(result),
                "num_questions": len(test_dataset),
                "detailed_results": evaluation_data
            }
            
            logger.info(f"Evaluation completed for {retrieval_method}")
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            raise
    
    async def _get_system_response(self, question: str, retrieval_method: str) -> Dict[str, Any]:
        """Get response from our RAG system."""
        try:
            if retrieval_method == "hybrid":
                # Use advanced retrieval hybrid search
                search_results = await advanced_retrieval_service.hybrid_search(
                    query=question,
                    limit=5
                )
                contexts = [result.get("chunk_text", "") for result in search_results]
                
            elif retrieval_method == "multi_agent":
                # Use full multi-agent workflow
                workflow_result = await self.workflow.execute(
                    question=question,
                    conversation_id="eval_test",
                    document_id=None
                )
                contexts = [
                    result.get("chunk_text", "")
                    for result in workflow_result.get("metadata", {}).get("context_retrieval", {}).get("search_results", [])
                ]
                return {
                    "answer": workflow_result.get("response", ""),
                    "contexts": contexts
                }
                
            else:
                # Basic semantic search
                search_results = await advanced_retrieval_service.vector_db.semantic_search(
                    query_text=question,
                    limit=5
                )
                contexts = [result.get("chunk_text", "") for result in search_results]
            
            # Generate simple answer from contexts
            answer = self._generate_simple_answer(question, contexts)
            
            return {
                "answer": answer,
                "contexts": contexts
            }
            
        except Exception as e:
            logger.error(f"Failed to get system response: {str(e)}")
            return {
                "answer": "Unable to generate response due to system error.",
                "contexts": []
            }
    
    def _generate_simple_answer(self, question: str, contexts: List[str]) -> str:
        """Generate a simple answer from contexts."""
        if not contexts:
            return "No relevant information found to answer this question."
        
        # Simple answer generation based on question type
        question_lower = question.lower()
        
        if "material weakness" in question_lower:
            relevant_contexts = [ctx for ctx in contexts if "material weakness" in ctx.lower()]
            if relevant_contexts:
                return f"Based on the audit findings: {relevant_contexts[0][:200]}..."
        
        elif "risk" in question_lower:
            relevant_contexts = [ctx for ctx in contexts if "risk" in ctx.lower()]
            if relevant_contexts:
                return f"Risk assessment shows: {relevant_contexts[0][:200]}..."
        
        elif "effective" in question_lower or "controls" in question_lower:
            relevant_contexts = [ctx for ctx in contexts if "effective" in ctx.lower() or "controls" in ctx.lower()]
            if relevant_contexts:
                return f"Control effectiveness analysis: {relevant_contexts[0][:200]}..."
        
        # Default response
        return f"Based on available information: {contexts[0][:200]}..."
    
    async def compare_retrieval_methods(
        self,
        test_dataset: Dataset,
        methods: List[str] = ["semantic", "hybrid", "query_expansion"]
    ) -> Dict[str, Any]:
        """
        Compare different retrieval methods using RAGAS evaluation with rate limiting.
        
        Args:
            test_dataset: Test dataset for evaluation
            methods: List of retrieval methods to compare
            
        Returns:
            Comparison results across methods
        """
        try:
            logger.info(f"Comparing retrieval methods: {methods}")
            
            comparison_results = {
                "timestamp": datetime.now().isoformat(),
                "methods": {},
                "summary": {}
            }
            
            # Evaluate each method with delays between them
            for i, method in enumerate(methods):
                logger.info(f"Evaluating method {i+1}/{len(methods)}: {method}")
                
                try:
                    method_results = await self.evaluate_retrieval_system(test_dataset, method)
                    comparison_results["methods"][method] = method_results
                    
                    logger.info(f"Completed evaluation for {method}")
                    
                    # Add delay between method evaluations
                    if i < len(methods) - 1:  # Don't delay after the last method
                        logger.info("Adding delay between method evaluations...")
                        await asyncio.sleep(10.0)  # 10 second delay between methods
                        
                except Exception as e:
                    logger.error(f"Failed to evaluate method {method}: {str(e)}")
                    comparison_results["methods"][method] = {
                        "error": str(e),
                        "method": method,
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Generate comparison summary
            comparison_results["summary"] = self._generate_comparison_summary(comparison_results["methods"])
            
            logger.info("Method comparison completed")
            return comparison_results
            
        except Exception as e:
            logger.error(f"Method comparison failed: {str(e)}")
            raise
    
    def _generate_comparison_summary(self, method_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparison summary across methods."""
        summary = {
            "best_method": {},
            "metric_comparison": {},
            "recommendations": []
        }
        
        # Compare key metrics
        key_metrics = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        
        for metric in key_metrics:
            metric_scores = {}
            for method, results in method_results.items():
                score = results.get("metrics", {}).get(metric, 0)
                metric_scores[method] = score
            
            # Find best method for this metric
            best_method = max(metric_scores.items(), key=lambda x: x[1])
            summary["best_method"][metric] = {
                "method": best_method[0],
                "score": best_method[1]
            }
            summary["metric_comparison"][metric] = metric_scores
        
        # Generate recommendations
        overall_scores = {}
        for method, results in method_results.items():
            metrics = results.get("metrics", {})
            avg_score = sum(metrics.get(m, 0) for m in key_metrics) / len(key_metrics)
            overall_scores[method] = avg_score
        
        best_overall = max(overall_scores.items(), key=lambda x: x[1])
        
        summary["recommendations"] = [
            f"Best overall method: {best_overall[0]} (avg score: {best_overall[1]:.3f})",
            f"Best for faithfulness: {summary['best_method']['faithfulness']['method']}",
            f"Best for relevancy: {summary['best_method']['answer_relevancy']['method']}",
            f"Best for precision: {summary['best_method']['context_precision']['method']}"
        ]
        
        return summary
    
    async def generate_evaluation_report(
        self,
        evaluation_results: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate comprehensive evaluation report.
        
        Args:
            evaluation_results: Results from RAGAS evaluation
            output_path: Optional path to save report
            
        Returns:
            Report content as string
        """
        try:
            report_lines = [
                "# RAGAS Evaluation Report for Verityn AI",
                f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "## Executive Summary",
                ""
            ]
            
            if "methods" in evaluation_results:
                # Multi-method comparison report
                report_lines.extend([
                    "### Method Comparison Results",
                    ""
                ])
                
                for method, results in evaluation_results["methods"].items():
                    metrics = results.get("metrics", {})
                    report_lines.extend([
                        f"#### {method.upper()} Method",
                        f"- **Faithfulness**: {metrics.get('faithfulness', 0):.3f}",
                        f"- **Answer Relevancy**: {metrics.get('answer_relevancy', 0):.3f}",
                        f"- **Context Precision**: {metrics.get('context_precision', 0):.3f}",
                        f"- **Context Recall**: {metrics.get('context_recall', 0):.3f}",
                        ""
                    ])
                
                # Add recommendations
                summary = evaluation_results.get("summary", {})
                if "recommendations" in summary:
                    report_lines.extend([
                        "### Recommendations",
                        ""
                    ])
                    for rec in summary["recommendations"]:
                        report_lines.append(f"- {rec}")
                    report_lines.append("")
            
            else:
                # Single method report
                metrics = evaluation_results.get("metrics", {})
                method = evaluation_results.get("method", "Unknown")
                
                report_lines.extend([
                    f"### {method.upper()} Method Results",
                    f"- **Faithfulness**: {metrics.get('faithfulness', 0):.3f}",
                    f"- **Answer Relevancy**: {metrics.get('answer_relevancy', 0):.3f}",
                    f"- **Context Precision**: {metrics.get('context_precision', 0):.3f}",
                    f"- **Context Recall**: {metrics.get('context_recall', 0):.3f}",
                    f"- **Answer Similarity**: {metrics.get('answer_similarity', 0):.3f}",
                    ""
                ])
            
            # Add technical details
            report_lines.extend([
                "## Technical Details",
                f"- **Evaluation Framework**: RAGAS",
                f"- **LLM Model**: GPT-4",
                f"- **Embedding Model**: {settings.OPENAI_EMBEDDING_MODEL}",
                f"- **Test Questions**: {evaluation_results.get('num_questions', 'N/A')}",
                "",
                "## Next Steps",
                "1. Implement recommendations for best-performing methods",
                "2. Continue monitoring with additional test cases",
                "3. Optimize underperforming components",
                "4. Schedule regular evaluation cycles"
            ])
            
            report_content = "\n".join(report_lines)
            
            # Save report if path provided
            if output_path:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write(report_content)
                logger.info(f"Report saved to {output_path}")
            
            return report_content
            
        except Exception as e:
            logger.error(f"Failed to generate evaluation report: {str(e)}")
            raise


# Global RAGAS evaluation service instance
ragas_evaluation_service = RAGASEvaluationService() 