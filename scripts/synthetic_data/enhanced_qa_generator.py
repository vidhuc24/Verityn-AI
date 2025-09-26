"""
Advanced Q&A Generator for Verityn AI

Addresses RAGAS evaluation gaps and generates quality-aware test datasets
for comprehensive chat system evaluation and performance assessment.
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from .ragas_enhanced_generator import QualityLevel, SOXControlID
from .synthetic_data_generation import DocumentTemplateEngine, CompanyProfile, DocumentType

class EnhancedQAGenerator:
    """Generates comprehensive Q&A pairs addressing RAGAS gap analysis findings"""
    
    def __init__(self, output_dir: str = "data/enhanced_qa_datasets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load gap analysis to inform question generation
        self.gap_analysis = self._load_gap_analysis()
        
    def _load_gap_analysis(self) -> Dict[str, Any]:
        """Load RAGAS gap analysis results"""
        gap_file = Path("data/enhanced_synthetic_documents/ragas_gap_analysis.json")
        if gap_file.exists():
            with open(gap_file, 'r') as f:
                return json.load(f)
        return {"missing_evidence_types": [], "recommendations": []}
    
    def generate_exception_handling_questions(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate questions focusing on exception handling (identified gap)"""
        template = document_data["template_structure"]
        quality = document_data["metadata"]["quality_level"]
        company = template["company_context"]["name"]
        doc_type = document_data["metadata"]["document_type"]
        
        questions = []
        
        if doc_type == "access_review":
            questions.extend([
                {
                    "question": f"How does {company} handle exceptions when terminated employees are found with active system access?",
                    "answer": self._get_exception_answer(quality, "Terminated employee access exceptions are escalated to the SOX Compliance Team for immediate investigation. Standard procedure requires access revocation within 24 hours and documentation of the remediation steps taken."),
                    "complexity": "intermediate",
                    "evidence_type": "exception_handling",
                    "quality_sensitive": True
                },
                {
                    "question": "What is the escalation procedure when segregation of duties violations are identified?",
                    "answer": self._get_exception_answer(quality, "Segregation of duties violations trigger immediate management notification and require approval from the CFO for any temporary exceptions. All violations must be remediated within 30 days with documented approval for any extended timelines."),
                    "complexity": "advanced",
                    "evidence_type": "exception_handling",
                    "quality_sensitive": True
                }
            ])
        
        elif doc_type == "financial_reconciliation":
            questions.extend([
                {
                    "question": f"How are reconciliation variances exceeding the materiality threshold handled at {company}?",
                    "answer": self._get_exception_answer(quality, "Variances exceeding $10,000 require immediate investigation by the Accounting Manager with documented root cause analysis. All material variances must be approved by the Assistant Controller before month-end close."),
                    "complexity": "intermediate",
                    "evidence_type": "exception_handling",
                    "quality_sensitive": True
                }
            ])
        
        elif doc_type == "risk_assessment":
            questions.extend([
                {
                    "question": "What happens when high-risk findings cannot be remediated within the standard timeline?",
                    "answer": self._get_exception_answer(quality, "High-risk findings requiring extended remediation timelines must be escalated to the Risk Committee with documented justification and interim compensating controls. Monthly progress reporting is required until full remediation."),
                    "complexity": "advanced",
                    "evidence_type": "exception_handling",
                    "quality_sensitive": True
                }
            ])
        
        return questions
    
    def generate_role_segregation_questions(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate questions focusing on role segregation (identified gap)"""
        template = document_data["template_structure"]
        quality = document_data["metadata"]["quality_level"]
        company = template["company_context"]["name"]
        doc_type = document_data["metadata"]["document_type"]
        
        questions = []
        
        if doc_type == "access_review":
            questions.extend([
                {
                    "question": f"How does {company} ensure segregation of duties between payment initiation and approval roles?",
                    "answer": self._get_segregation_answer(quality, "Role-based access controls prevent the same individual from both initiating and approving payments. The system enforces a minimum of two-person authorization for all payments exceeding $5,000, with automated segregation validation."),
                    "complexity": "intermediate",
                    "evidence_type": "role_segregation",
                    "quality_sensitive": True
                },
                {
                    "question": "What controls prevent users from having conflicting access across financial systems?",
                    "answer": self._get_segregation_answer(quality, "Automated segregation of duties matrix validates user access across all financial systems. Quarterly access reviews specifically test for conflicting access combinations, with immediate remediation required for any violations identified."),
                    "complexity": "advanced",
                    "evidence_type": "role_segregation",
                    "quality_sensitive": True
                }
            ])
        
        return questions
    
    def generate_sox_control_specific_questions(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate questions addressing specific SOX control IDs (identified gap)"""
        template = document_data["template_structure"]
        quality = document_data["metadata"]["quality_level"]
        sox_controls = document_data["metadata"]["sox_control_ids"]
        company = template["company_context"]["name"]
        
        questions = []
        
        for control_id in sox_controls:
            if control_id == "404.1":
                questions.append({
                    "question": f"How does {company} demonstrate compliance with SOX 404.1 internal control over financial reporting requirements?",
                    "answer": self._get_control_answer(quality, control_id, "SOX 404.1 compliance is demonstrated through comprehensive documentation of internal controls, quarterly management assessments, and annual effectiveness testing. All key financial processes have documented control procedures with defined testing frequencies."),
                    "complexity": "advanced",
                    "sox_control_id": control_id,
                    "quality_sensitive": True
                })
            
            elif control_id == "302.1":
                questions.append({
                    "question": f"What procedures does {company} follow for SOX 302.1 management assessment of disclosure controls?",
                    "answer": self._get_control_answer(quality, control_id, "SOX 302.1 procedures include quarterly assessment of disclosure controls effectiveness, documented management review of financial reporting processes, and certification of internal control adequacy by senior management."),
                    "complexity": "intermediate",
                    "sox_control_id": control_id,
                    "quality_sensitive": True
                })
        
        return questions
    
    def generate_quality_aware_questions(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate questions that test the RAG system's ability to detect quality levels"""
        quality = document_data["metadata"]["quality_level"]
        company = document_data["metadata"]["company"]
        doc_type = document_data["metadata"]["document_type"]
        
        questions = []
        
        # Quality detection questions
        if quality == "fail":
            questions.append({
                "question": f"Are there any material weaknesses or significant deficiencies identified in this {doc_type.replace('_', ' ')}?",
                "answer": "Yes, this document identifies material weaknesses and significant deficiencies that require immediate management attention and remediation.",
                "complexity": "basic",
                "evidence_type": "quality_detection",
                "expected_quality": "fail"
            })
        
        elif quality == "low":
            questions.append({
                "question": f"What gaps or deficiencies are noted in this {doc_type.replace('_', ' ')} documentation?",
                "answer": "The documentation shows some gaps in procedures and limited detail in certain areas that need improvement to meet full compliance standards.",
                "complexity": "intermediate",
                "evidence_type": "quality_detection",
                "expected_quality": "low"
            })
        
        elif quality == "high":
            questions.append({
                "question": f"How comprehensive is the control documentation and testing in this {doc_type.replace('_', ' ')}?",
                "answer": "The documentation is comprehensive with detailed procedures, thorough testing, and robust management oversight that exceeds standard compliance requirements.",
                "complexity": "intermediate",
                "evidence_type": "quality_detection",
                "expected_quality": "high"
            })
        
        return questions
    
    def _get_exception_answer(self, quality: str, base_answer: str) -> str:
        """Modify answer based on document quality for exception handling"""
        if quality == "high":
            return base_answer + " All exception handling procedures are fully documented with comprehensive audit trails and management oversight."
        elif quality == "medium":
            return base_answer
        elif quality == "low":
            return base_answer + " However, some exception handling procedures lack complete documentation."
        elif quality == "fail":
            return "Exception handling procedures are inadequate and fail to meet SOX compliance requirements. Significant remediation is required."
        return base_answer
    
    def _get_segregation_answer(self, quality: str, base_answer: str) -> str:
        """Modify answer based on document quality for role segregation"""
        if quality == "high":
            return base_answer + " Advanced automated controls provide real-time segregation monitoring with comprehensive reporting."
        elif quality == "medium":
            return base_answer
        elif quality == "low":
            return base_answer + " Some segregation controls rely on manual procedures that need enhancement."
        elif quality == "fail":
            return "Segregation of duties controls are inadequate with multiple violations identified. This represents a material weakness in internal controls."
        return base_answer
    
    def _get_control_answer(self, quality: str, control_id: str, base_answer: str) -> str:
        """Modify answer based on document quality for SOX controls"""
        if quality == "high":
            return base_answer + f" {control_id} implementation exceeds regulatory requirements with comprehensive documentation and testing."
        elif quality == "medium":
            return base_answer
        elif quality == "low":
            return base_answer + f" {control_id} procedures need improvement in documentation and testing frequency."
        elif quality == "fail":
            return f"SOX {control_id} compliance is inadequate and represents a material weakness requiring immediate remediation."
        return base_answer
    
    def generate_enhanced_qa_dataset(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive Q&A dataset addressing all identified gaps"""
        all_questions = []
        
        # Generate gap-addressing questions
        all_questions.extend(self.generate_exception_handling_questions(document_data))
        all_questions.extend(self.generate_role_segregation_questions(document_data))
        all_questions.extend(self.generate_sox_control_specific_questions(document_data))
        all_questions.extend(self.generate_quality_aware_questions(document_data))
        
        # Add metadata to all questions
        for i, question in enumerate(all_questions):
            question.update({
                "question_id": f"ENH_{document_data['metadata']['document_type'].upper()}_{i+1:03d}",
                "document_type": document_data["metadata"]["document_type"],
                "company": document_data["metadata"]["company"],
                "quality_level": document_data["metadata"]["quality_level"],
                "sox_control_ids": document_data["metadata"]["sox_control_ids"],
                "generated_at": datetime.now().isoformat()
            })
        
        return all_questions
    
    def generate_all_enhanced_qa_datasets(self) -> Dict[str, Any]:
        """Generate Q&A datasets for all enhanced synthetic documents"""
        
        # Load enhanced document data
        enhanced_docs_dir = Path("data/enhanced_synthetic_documents")
        
        all_qa_data = {
            "generation_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_documents": 0,
                "total_questions": 0,
                "questions_by_quality": {quality.value: 0 for quality in QualityLevel},
                "questions_by_evidence_type": {},
                "gap_analysis_addressed": self.gap_analysis
            },
            "enhanced_qa_datasets": {}
        }
        
        # Process enhanced documents from summary file
        summary_file = enhanced_docs_dir / "enhanced_generation_summary.json"
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                enhanced_summary = json.load(f)
            
            for doc_key, doc_data in enhanced_summary["documents"].items():
                try:
                    # Generate enhanced Q&A pairs
                    qa_pairs = self.generate_enhanced_qa_dataset(doc_data)
                    
                    if qa_pairs:
                        all_qa_data["enhanced_qa_datasets"][doc_key] = {
                            "document_metadata": doc_data["metadata"],
                            "questions": qa_pairs
                        }
                        
                        # Update counters
                        all_qa_data["generation_summary"]["total_documents"] += 1
                        all_qa_data["generation_summary"]["total_questions"] += len(qa_pairs)
                        
                        quality = doc_data["metadata"]["quality_level"]
                        all_qa_data["generation_summary"]["questions_by_quality"][quality] += len(qa_pairs)
                        
                        # Count evidence types
                        for question in qa_pairs:
                            evidence_type = question.get("evidence_type", "standard")
                            if evidence_type not in all_qa_data["generation_summary"]["questions_by_evidence_type"]:
                                all_qa_data["generation_summary"]["questions_by_evidence_type"][evidence_type] = 0
                            all_qa_data["generation_summary"]["questions_by_evidence_type"][evidence_type] += 1
                            
                except Exception as e:
                    print(f"Error processing {doc_key}: {str(e)}")
        
        # Save complete enhanced Q&A dataset
        qa_file = self.output_dir / "enhanced_qa_dataset.json"
        with open(qa_file, 'w', encoding='utf-8') as f:
            json.dump(all_qa_data, f, indent=2, default=str)
        
        return all_qa_data

def main():
    """Test enhanced Q&A generation"""
    print("🔍 Starting Enhanced Q&A Generation")
    print("=" * 60)
    
    # Initialize enhanced Q&A generator
    qa_generator = EnhancedQAGenerator()
    
    print(f"\n📁 Output directory: {qa_generator.output_dir}")
    
    # Show gap analysis being addressed
    if qa_generator.gap_analysis:
        print(f"\n📋 Addressing RAGAS Gap Analysis:")
        print(f"   Missing Evidence Types: {qa_generator.gap_analysis.get('missing_evidence_types', [])}")
        print(f"   Control Coverage Gaps: {qa_generator.gap_analysis.get('control_coverage_gaps', [])}")
    
    # Generate enhanced Q&A datasets
    print(f"\n🚀 Generating Enhanced Q&A Datasets...")
    
    try:
        results = qa_generator.generate_all_enhanced_qa_datasets()
        
        summary = results["generation_summary"]
        print(f"\n📊 Enhanced Q&A Generation Complete!")
        print(f"   Documents Processed: {summary['total_documents']}")
        print(f"   Total Questions: {summary['total_questions']}")
        print(f"   Questions by Quality Level:")
        for quality, count in summary['questions_by_quality'].items():
            print(f"     - {quality.title()}: {count} questions")
        print(f"   Questions by Evidence Type:")
        for evidence_type, count in summary['questions_by_evidence_type'].items():
            print(f"     - {evidence_type}: {count} questions")
        
        print(f"\n🎯 Enhanced Q&A generation completed successfully!")
        print(f"⚡ Gap-addressing questions ready for robust RAG evaluation")
        print(f"📂 Dataset saved to: {qa_generator.output_dir}/enhanced_qa_dataset.json")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during enhanced Q&A generation: {str(e)}")
        return None

if __name__ == "__main__":
    results = main() 